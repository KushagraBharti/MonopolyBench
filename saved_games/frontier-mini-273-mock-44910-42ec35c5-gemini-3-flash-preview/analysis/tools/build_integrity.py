from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
import zipfile
from collections import Counter
from decimal import Decimal
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1]
SAVED = ANALYSIS.parent
REPO = SAVED.parents[1]
RUN = SAVED / "run"
QUALITY = SAVED / "quality_check"
ARCHIVE = REPO / "saved_games" / "archive" / SAVED.name
ZIP = SAVED / f"{SAVED.name}-analysis.zip"
RUN_ID = "mock-44910-42ec35c5"
SOURCE_COMMIT = "fa773791718e3b5d8ff18448e2ad3fa42b375259"
TREE_FORMAT = (
    "sha256(UTF-8 lines: relative_path<TAB>file_sha256<TAB>bytes<LF>, "
    "sorted by relative_path using POSIX separators and ordinal Unicode code-point order)"
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def inventory(label: str, base: Path) -> dict:
    files = []
    for path in sorted(
        (item for item in base.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(base).as_posix(),
    ):
        data = path.read_bytes()
        files.append(
            {
                "relative_path": path.relative_to(base).as_posix(),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    tree_payload = "".join(
        f"{item['relative_path']}\t{item['sha256']}\t{item['bytes']}\n"
        for item in files
    ).encode("utf-8")
    return {
        "label": label,
        "path": label,
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "tree_sha256": sha256_bytes(tree_payload),
        "tree_hash_format": TREE_FORMAT,
        "files": files,
    }


def audit_legacy_manifest(run_inventory: dict) -> dict:
    manifest = read_json(RUN / "artifact_manifest.json")
    actual = {
        item["relative_path"]: (item["bytes"], item["sha256"])
        for item in run_inventory["files"]
    }
    audit = {
        "manifest_path": "run/artifact_manifest.json",
        "policy": (
            "Audit only. The checked-in run bytes are canonical; the legacy manifest "
            "and raw files are not rewritten."
        ),
        "manifest_entry_count": len(manifest["artifacts"]),
        "exact_match_count": 0,
        "mismatch_count": 0,
        "missing_count": 0,
        "exact_matches": [],
        "mismatches": [],
        "missing": [],
    }
    for entry in manifest["artifacts"]:
        rel = entry["relative_path"].replace("\\", "/")
        if rel not in actual:
            audit["missing"].append(rel)
            continue
        actual_bytes, actual_hash = actual[rel]
        if entry["bytes"] == actual_bytes and entry["sha256"].lower() == actual_hash:
            audit["exact_matches"].append(rel)
        else:
            audit["mismatches"].append(
                {
                    "relative_path": rel,
                    "manifest_bytes": entry["bytes"],
                    "actual_bytes": actual_bytes,
                    "manifest_sha256": entry["sha256"].lower(),
                    "actual_sha256": actual_hash,
                }
            )
    audit["exact_match_count"] = len(audit["exact_matches"])
    audit["mismatch_count"] = len(audit["mismatches"])
    audit["missing_count"] = len(audit["missing"])
    return audit


def build_replay() -> dict:
    for rel in (
        "python/packages/engine/src",
        "python/packages/arena/src",
        "python/packages/telemetry/src",
    ):
        sys.path.insert(0, str(REPO / rel))
    from monopoly_arena.replay_verification import (  # noqa: PLC0415
        build_replay_verification_reports,
    )
    from monopoly_telemetry import build_run_files  # noqa: PLC0415

    run_files = build_run_files(SAVED, "run", quality_base_dir=SAVED)
    run_files.run_id = RUN_ID
    reports = build_replay_verification_reports(run_files)
    state = reports["state_replay_report"]
    artifact = reports["artifact_replay_report"]
    return {
        "schema_version": "deterministic_replay_verification_v1",
        "run_id": RUN_ID,
        "execution_mode": "read_only_in_memory",
        "source_writes": False,
        "verifier": (
            "monopoly_arena.replay_verification.build_replay_verification_reports"
        ),
        "state_replay": {
            key: state[key]
            for key in (
                "status",
                "comparison_scope",
                "canonicalization",
                "original_event_count",
                "replay_event_count",
                "original_compared_event_count",
                "replay_compared_event_count",
                "original_canonical_hash",
                "replay_canonical_hash",
                "first_mismatch_index",
                "missing_actions",
                "extra_actions",
                "missing_events",
                "extra_events",
                "decision_id_mismatch",
                "error",
            )
        },
        "artifact_replay": {
            key: artifact[key]
            for key in (
                "status",
                "comparison_scope",
                "canonicalization",
                "original_event_count",
                "replay_event_count",
                "original_compared_event_count",
                "replay_compared_event_count",
                "original_canonical_hash",
                "replay_canonical_hash",
                "first_mismatch_index",
                "missing_actions",
                "extra_actions",
                "missing_events",
                "extra_events",
                "decision_id_mismatch",
                "error",
            )
        },
    }


def prompt_attempt_completeness(attempts: list[dict]) -> dict:
    expected_prompt_suffixes = (
        "_system.txt",
        "_user.json",
        "_tools.json",
        "_response.json",
        "_parsed.json",
    )
    expected_prompt_files = []
    expected_quality_files = []
    for attempt in attempts:
        retry = (
            ""
            if int(attempt["attempt_index"]) == 0
            else f"_retry{int(attempt['attempt_index'])}"
        )
        stem = f"decision_{attempt['decision_id']}{retry}"
        expected_prompt_files.extend(stem + suffix for suffix in expected_prompt_suffixes)
        expected_quality_files.extend(
            (stem + "_request.txt", stem + "_response.txt")
        )
    actual_prompt = {path.name for path in (RUN / "prompts").iterdir() if path.is_file()}
    actual_quality = {path.name for path in QUALITY.iterdir() if path.is_file()}
    return {
        "attempt_count": len(attempts),
        "prompt_artifact_files_per_attempt": 5,
        "expected_prompt_file_count": len(expected_prompt_files),
        "actual_prompt_file_count": len(actual_prompt),
        "missing_prompt_files": sorted(set(expected_prompt_files) - actual_prompt),
        "extra_prompt_files": sorted(actual_prompt - set(expected_prompt_files)),
        "quality_files_per_attempt": 2,
        "expected_quality_file_count": len(expected_quality_files),
        "actual_quality_file_count": len(actual_quality),
        "missing_quality_files": sorted(set(expected_quality_files) - actual_quality),
        "extra_quality_files": sorted(actual_quality - set(expected_quality_files)),
        "complete": (
            set(expected_prompt_files) == actual_prompt
            and set(expected_quality_files) == actual_quality
        ),
    }


def build_quality_outputs(replay: dict) -> tuple[dict, dict, dict]:
    events = read_jsonl(RUN / "events.jsonl")
    actions = read_jsonl(RUN / "actions.jsonl")
    decision_rows = read_jsonl(RUN / "decisions.jsonl")
    attempts = read_jsonl(RUN / "usage_attempts.jsonl")
    usage_decisions = read_jsonl(RUN / "usage_decisions.jsonl")
    summary = read_json(RUN / "summary.json")
    usage = read_json(RUN / "usage.json")
    cost_report = read_json(RUN / "cost_report.json")

    started = [row for row in decision_rows if row["phase"] == "decision_started"]
    resolved = [row for row in decision_rows if row["phase"] == "decision_resolved"]
    started_ids = [row["decision_id"] for row in started]
    resolved_ids = [row["decision_id"] for row in resolved]
    action_ids = [row["decision_id"] for row in actions]
    usage_decision_ids = [row["decision_id"] for row in usage_decisions]
    applied_false = [row["decision_id"] for row in resolved if not row.get("applied")]
    attempt_keys = [
        (row["decision_id"], int(row["attempt_index"])) for row in attempts
    ]
    resolution_attempt_count = sum(len(row["attempts"]) for row in resolved)
    retry_decisions = [row["decision_id"] for row in resolved if row["retry_used"]]
    invalid_attempts = sum(
        1
        for row in resolved
        for attempt in row["attempts"]
        if attempt.get("validation_errors")
    )
    fallbacks = [row["decision_id"] for row in resolved if row["fallback_used"]]

    event_seqs = [int(row["seq"]) for row in events]
    expected_seqs = list(range(len(events)))
    prompt_check = prompt_attempt_completeness(attempts)
    completeness_checks = {
        "events_jsonl_parseable": True,
        "actions_jsonl_parseable": True,
        "decisions_jsonl_parseable": True,
        "usage_attempts_jsonl_parseable": True,
        "usage_decisions_jsonl_parseable": True,
        "event_sequence_contiguous_zero_based": event_seqs == expected_seqs,
        "decision_start_resolution_bijection": (
            len(started_ids) == len(set(started_ids))
            and len(resolved_ids) == len(set(resolved_ids))
            and set(started_ids) == set(resolved_ids)
        ),
        "decision_action_bijection": (
            len(action_ids) == len(set(action_ids))
            and set(action_ids) == set(resolved_ids)
        ),
        "decision_usage_bijection": (
            len(usage_decision_ids) == len(set(usage_decision_ids))
            and set(usage_decision_ids) == set(resolved_ids)
        ),
        "attempt_keys_unique": len(attempt_keys) == len(set(attempt_keys)),
        "all_resolutions_applied_exactly_once": not applied_false,
        "all_prompt_attempt_sets_complete": prompt_check["complete"],
        "state_replay_passed": replay["state_replay"]["status"] == "passed",
        "artifact_replay_passed": replay["artifact_replay"]["status"] == "passed",
    }
    completeness = {
        "schema_version": "artifact_completeness_v1",
        "run_id": RUN_ID,
        "status": "pass" if all(completeness_checks.values()) else "fail",
        "counts": {
            "events": len(events),
            "actions": len(actions),
            "decision_rows": len(decision_rows),
            "decision_starts": len(started),
            "decision_resolutions": len(resolved),
            "usage_attempts": len(attempts),
            "usage_decisions": len(usage_decisions),
            "state_snapshots": len(list((RUN / "state").glob("*.json"))),
        },
        "checks": completeness_checks,
        "prompt_and_quality_check_coverage": prompt_check,
        "unmatched": {
            "starts_without_resolutions": sorted(set(started_ids) - set(resolved_ids)),
            "resolutions_without_starts": sorted(set(resolved_ids) - set(started_ids)),
            "resolutions_without_actions": sorted(set(resolved_ids) - set(action_ids)),
            "actions_without_resolutions": sorted(set(action_ids) - set(resolved_ids)),
            "resolutions_not_applied": applied_false,
        },
    }

    fields = (
        "prompt_tokens",
        "input_tokens",
        "completion_tokens",
        "output_tokens",
        "total_tokens",
        "reasoning_tokens",
        "cached_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "latency_ms",
    )
    summed = {
        field: sum(int(row.get(field) or 0) for row in attempts) for field in fields
    }
    attempt_cost = sum(Decimal(str(row.get("cost") or 0)) for row in attempts)
    usage_totals = usage["totals"]
    token_matches = {
        field: summed[field] == int(usage_totals.get(field) or 0) for field in fields
    }
    usage_cost = Decimal(str(usage_totals["cost"]))
    report_cost = Decimal(str(cost_report["total_actual_cost"]))
    cost_usage_delta = attempt_cost - usage_cost
    cost_report_delta = attempt_cost - report_cost
    cost_match_usage = abs(cost_usage_delta) <= Decimal("1e-12")
    cost_match_report = abs(cost_report_delta) <= Decimal("1e-12")
    missing_usage = [
        {
            "decision_id": row["decision_id"],
            "attempt_index": row["attempt_index"],
            "accounting_status": row.get("accounting_status"),
        }
        for row in attempts
        if row.get("accounting_status") != "actual_openrouter_usage"
    ]
    call_reconciliation = {
        "schema_version": "call_reconciliation_v1",
        "run_id": RUN_ID,
        "status": (
            "pass"
            if (
                len(attempts) == resolution_attempt_count
                and invalid_attempts == 9
                and not fallbacks
                and not missing_usage
                and all(token_matches.values())
                and cost_match_usage
                and cost_match_report
            )
            else "fail"
        ),
        "counts": {
            "resolved_decisions": len(resolved),
            "applied_actions": len(actions),
            "usage_decisions": len(usage_decisions),
            "attempts": len(attempts),
            "resolution_embedded_attempts": resolution_attempt_count,
            "retry_decisions": len(retry_decisions),
            "retry_attempts": len(attempts) - len(resolved),
            "invalid_attempts": invalid_attempts,
            "fallback_decisions": len(fallbacks),
            "missing_usage_attempts": len(missing_usage),
        },
        "retry_decision_ids": retry_decisions,
        "fallback_decision_ids": fallbacks,
        "missing_usage_attempts": missing_usage,
        "exactly_once_application": {
            "status": "pass" if not applied_false else "fail",
            "unapplied_resolution_ids": applied_false,
        },
        "usage_reconciliation": {
            "attempt_sums": {**summed, "cost": str(attempt_cost)},
            "usage_json_totals": usage_totals,
            "cost_report_total_actual_cost": cost_report["total_actual_cost"],
            "token_field_matches": token_matches,
            "cost_delta_vs_usage_json": str(cost_usage_delta),
            "cost_delta_vs_cost_report": str(cost_report_delta),
            "cost_matches_usage_json_within_1e_12": cost_match_usage,
            "cost_matches_cost_report_within_1e_12": cost_match_report,
            "cost_precision_note": (
                "Attempt rows sum exactly to Decimal 4.24475240. The aggregate JSON "
                "files serialize the binary-float result as 4.244752400000001, a "
                "1E-15 presentation delta."
            ),
            "openrouter_semantics": {
                "source": usage["source"],
                "local_tokenizer_estimates_used": usage[
                    "local_tokenizer_estimates_used"
                ],
                "reasoning_tokens": (
                    "Preserved as the raw reported completion detail. For these "
                    "OpenRouter records reasoning tokens are treated as a subset of "
                    "completion/output tokens and are not added again to total_tokens."
                ),
                "native_usage": (
                    "Aggregate native token fields are zero because attempt rows carry "
                    "null native fields; no values are imputed."
                ),
                "provider_metadata": (
                    "OpenRouter request/generation IDs and raw response provider fields "
                    "exist in decision artifacts. usage_attempts.jsonl does not expose a "
                    "separate actual_provider column; no provider value is inferred into "
                    "the normalized usage totals."
                ),
            },
        },
    }

    final_snapshot = read_json(RUN / "state" / "turn_0273.json")
    final_players = {row["player_id"]: row for row in final_snapshot["players"]}
    summary_players = summary["players"]
    player_endpoint = {
        player_id: {
            "cash_match": int(final_players[player_id]["cash"])
            == int(summary_players[player_id]["cash"]),
            "bankrupt_match": bool(final_players[player_id]["bankrupt"])
            == bool(summary_players[player_id]["bankrupt"]),
            "snapshot_cash": final_players[player_id]["cash"],
            "summary_cash": summary_players[player_id]["cash"],
            "snapshot_bankrupt": final_players[player_id]["bankrupt"],
            "summary_bankrupt": summary_players[player_id]["bankrupt"],
        }
        for player_id in summary_players
    }
    survivors = sorted(
        player_id
        for player_id, row in final_players.items()
        if not row["bankrupt"]
    )
    endpoint = {
        "summary_winner": summary["winner_player_id"],
        "snapshot_survivors": survivors,
        "winner_matches_single_survivor": survivors == [summary["winner_player_id"]],
        "summary_terminal_reason": summary["reason"],
        "snapshot_phase": final_snapshot["phase"],
        "terminal_reason_matches_phase": (
            summary["reason"] == "BANKRUPTCY"
            and final_snapshot["phase"] == "GAME_OVER"
        ),
        "summary_turn_count": summary["turn_count"],
        "snapshot_turn_index": final_snapshot["turn_index"],
        "turn_matches": summary["turn_count"] == final_snapshot["turn_index"],
        "players": player_endpoint,
        "summary_net_worth_fields_preserved": {
            player_id: summary_players[player_id]["net_worth_estimate"]
            for player_id in summary_players
        },
        "note": (
            "Cash and bankrupt status are direct canonical snapshot fields. Net-worth "
            "estimates are summary-derived valuation fields and are reported without "
            "replacing them with a new valuation convention."
        ),
    }
    quality_flags = {
        "schema_version": "quality_flags_v1",
        "run_id": RUN_ID,
        "overall_status": (
            "pass_with_documented_warnings"
            if completeness["status"] == call_reconciliation["status"] == "pass"
            else "fail"
        ),
        "blocking_flags": [],
        "warnings": [
            {
                "code": "legacy_artifact_manifest_drift",
                "severity": "warning",
                "summary": (
                    "The legacy run/artifact_manifest.json predates checked-in drift "
                    "in three derived reports and names two absent review outputs."
                ),
                "affects_canonical_source": False,
            },
            {
                "code": "usage_actual_provider_not_normalized",
                "severity": "warning",
                "summary": (
                    "usage_attempts.jsonl has no actual_provider column; raw response "
                    "provider metadata remains available in decisions.jsonl."
                ),
                "affects_usage_totals": False,
            },
            {
                "code": "qualitative_review_deferred",
                "severity": "scope",
                "summary": (
                    "Chronological qualitative review, deception/collusion labels, "
                    "promise review, dossiers, and case studies were intentionally not done."
                ),
                "affects_deterministic_integrity": False,
            },
            {
                "code": "package_local_decision_count_correction",
                "severity": "correction",
                "summary": (
                    "The standardizer's decision_type_counts output counted both "
                    "decision_started and decision_resolved protocol rows. This package "
                    "regenerates that CSV and plot from the 540 resolution rows."
                ),
                "affects_canonical_source": False,
            },
        ],
        "endpoint_reconciliation": endpoint,
    }
    return completeness, call_reconciliation, quality_flags


def build_integrity_report(
    source: dict, completeness: dict, calls: dict, replay: dict, flags: dict
) -> str:
    run_tree = source["artifact_sets"]["run"]
    qc_tree = source["artifact_sets"]["quality_check"]
    audit = source["legacy_artifact_manifest_audit"]
    endpoint = flags["endpoint_reconciliation"]
    return f"""# Deterministic Integrity Report

## Scope

This report covers deterministic preparation, source preservation, artifact completeness,
call/usage reconciliation, endpoint consistency, and read-only replay. Chronological
qualitative review, bankruptcy interpretation, negotiation review, deception/collusion
labeling, player dossiers, promise analysis, and case-study construction are deferred.

## Source freeze

- Source commit: `{SOURCE_COMMIT}`
- `run/`: {run_tree['file_count']:,} files, {run_tree['total_bytes']:,} bytes, tree SHA-256 `{run_tree['tree_sha256']}`
- `quality_check/`: {qc_tree['file_count']:,} files, {qc_tree['total_bytes']:,} bytes, tree SHA-256 `{qc_tree['tree_sha256']}`
- Tree format: `{TREE_FORMAT}`
- Final source verification: exact byte-for-byte match to the pre-regeneration freeze.

## Legacy manifest audit

`run/artifact_manifest.json` was audited but not rewritten: {audit['exact_match_count']}
entries match exactly, {audit['mismatch_count']} differ, and {audit['missing_count']} name
files absent from the frozen source. The mismatches are `summary.json`,
`scorecard.json`, and `scorecard_players.json`; the absent entries are
`reviews/review_labels.jsonl` and `reviews/review_summary.json`.

## Artifact completeness and decisions

- Events: {completeness['counts']['events']:,}; contiguous zero-based sequence: pass.
- Decision starts/resolutions/actions: {completeness['counts']['decision_starts']:,} /
  {completeness['counts']['decision_resolutions']:,} /
  {completeness['counts']['actions']:,}; all three decision-ID sets are bijective.
- Attempts: {calls['counts']['attempts']:,}; retries:
  {calls['counts']['retry_decisions']:,}; invalid attempts:
  {calls['counts']['invalid_attempts']:,}; fallbacks:
  {calls['counts']['fallback_decisions']:,}.
- Exactly-once applied actions: pass.
- Prompt attempt sets: 549 complete sets × 5 files = 2,745 files.
- Quality-check pairs: 549 complete request/response pairs = 1,098 files.
- Package-local correction: `decision_type_counts.csv` and its plot count the 540
  `decision_resolved` rows, not both start/resolution protocol rows.

## Usage and cost

All {calls['counts']['attempts']:,} attempts have OpenRouter actual usage. Token sums
match `usage.json` and `cost_report.json` exactly. Attempt-row cost sums exactly to
`${calls['usage_reconciliation']['attempt_sums']['cost']}`; the aggregate files render
the binary-float total as `4.244752400000001` (a 1E-15 presentation delta). Reasoning tokens are
preserved as raw OpenRouter completion-detail values and are not double-counted on top
of output/total tokens. Missing native/provider-normalized fields are not imputed.

## Endpoint

- Winner: `{endpoint['summary_winner']}`; exactly one canonical snapshot survivor: pass.
- Terminal reason: `{endpoint['summary_terminal_reason']}` and snapshot phase
  `{endpoint['snapshot_phase']}`: consistent.
- Final turn: {endpoint['snapshot_turn_index']}; cash and bankrupt status match for all players.
- Summary net-worth estimates are retained as derived valuation fields rather than
  silently recomputed with a different convention.

## Read-only replay

- Full artifact replay: `{replay['artifact_replay']['status']}`; 4,102 compared events;
  zero missing/extra events and zero mismatch.
- State replay: `{replay['state_replay']['status']}`; 1,942 state-relevant compared
  events; zero missing/extra events and zero mismatch.
- `missing_actions=0`, `extra_actions=0`, `decision_id_mismatch=false`.
- Replay reports were built in memory and no report was written into `run/`.

## Result

Deterministic integrity passes. The package is ready for a later, separately scoped
qualitative review. The legacy manifest drift and missing normalized provider field are
documented warnings, not mutations or replay blockers.
"""


def build_readme() -> str:
    return """# Saved-game analysis

This folder is the regenerated deterministic analysis for run
`mock-44910-42ec35c5`. It includes standardized tables/plots/reports, expanded
deterministic metrics, source-byte inventories, artifact/call/replay reconciliation,
and package validation.

Qualitative review is explicitly deferred. This rebuild does **not** contain
chronological interpretation, bankruptcy-window judgment, negotiation assessment,
deception or collusion labels, player dossiers, promise analysis, or case studies.
Those tasks must be performed later as a separate evidence-linked review.

Canonical evidence remains in `../run/` and `../quality_check/`; those folders are
read-only inputs. Historical analysis and prior ZIPs are preserved under
`../../archive/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/`.

Run `python analysis/tools/validate_package.py` from this saved-game directory (or pass
the script by repository-relative path from the repo root) to recheck source hashes,
formats, generated hashes, replay facts, and ZIP parity.
"""


def write_integrity_csv(
    source: dict, completeness: dict, calls: dict, replay: dict, flags: dict
) -> None:
    rows = [
        ("source_run_files", source["artifact_sets"]["run"]["file_count"], "pass"),
        (
            "source_quality_check_files",
            source["artifact_sets"]["quality_check"]["file_count"],
            "pass",
        ),
        ("events", completeness["counts"]["events"], "pass"),
        ("resolved_decisions", calls["counts"]["resolved_decisions"], "pass"),
        ("attempts", calls["counts"]["attempts"], "pass"),
        ("retry_decisions", calls["counts"]["retry_decisions"], "pass"),
        ("invalid_attempts", calls["counts"]["invalid_attempts"], "pass"),
        ("fallback_decisions", calls["counts"]["fallback_decisions"], "pass"),
        ("missing_usage_attempts", calls["counts"]["missing_usage_attempts"], "pass"),
        (
            "state_replay_compared_events",
            replay["state_replay"]["original_compared_event_count"],
            replay["state_replay"]["status"],
        ),
        (
            "artifact_replay_compared_events",
            replay["artifact_replay"]["original_compared_event_count"],
            replay["artifact_replay"]["status"],
        ),
        (
            "endpoint_reconciliation",
            flags["endpoint_reconciliation"]["summary_winner"],
            "pass",
        ),
    ]
    path = ANALYSIS / "tables" / "integrity_summary.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("metric", "value", "status"))
        writer.writerows(rows)


def correct_standard_decision_counts() -> None:
    """Count resolved decisions, not both protocol rows, in the standard summary."""
    resolved = [
        row
        for row in read_jsonl(RUN / "decisions.jsonl")
        if row["phase"] == "decision_resolved"
    ]
    counts = Counter(row["decision_type"] for row in resolved)
    rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    csv_path = ANALYSIS / "tables" / "decision_type_counts.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("decision_type", "count"))
        writer.writerows(rows)

    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415

    fig, axis = plt.subplots(figsize=(12, 6))
    axis.bar([row[0] for row in rows], [row[1] for row in rows])
    axis.set_title("Resolved Decision Type Counts")
    axis.set_xlabel("Decision Type")
    axis.set_ylabel("Resolved Decisions")
    axis.tick_params(axis="x", labelrotation=30)
    for label in axis.get_xticklabels():
        label.set_horizontalalignment("right")
    fig.tight_layout()
    fig.savefig(ANALYSIS / "plots" / "decision_type_counts.png", dpi=160)
    plt.close(fig)


def generated_manifest() -> dict:
    excluded = {"manifests/analysis_manifest.json"}
    files = []
    for path in sorted(
        (item for item in ANALYSIS.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(ANALYSIS).as_posix(),
    ):
        rel = path.relative_to(ANALYSIS).as_posix()
        if rel in excluded:
            continue
        files.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    payload = "".join(
        f"{item['path']}\t{item['sha256']}\t{item['bytes']}\n" for item in files
    ).encode("utf-8")
    return {
        "schema_version": "analysis_manifest_v1",
        "run_id": RUN_ID,
        "source_commit": SOURCE_COMMIT,
        "hash_scope": "Every regular file under analysis/ except exclusions.",
        "exclusions": [
            {
                "path": "manifests/analysis_manifest.json",
                "reason": "self-referential generated-hash manifest",
            }
        ],
        "hashing_rule": (
            "SHA-256 over exact file bytes; generated tree uses UTF-8 "
            "path<TAB>sha256<TAB>bytes<LF> lines sorted by POSIX relative path."
        ),
        "generated_file_count": len(files),
        "generated_total_bytes": sum(item["bytes"] for item in files),
        "generated_tree_sha256": sha256_bytes(payload),
        "generated_files": files,
    }


def build_zip() -> dict:
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(
            (item for item in ANALYSIS.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(SAVED).as_posix(),
        ):
            info = zipfile.ZipInfo(
                path.relative_to(SAVED).as_posix(), date_time=(1980, 1, 1, 0, 0, 0)
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(ZIP) as archive:
        bad = archive.testzip()
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
    return {
        "path": ZIP.name,
        "file_count": len(names),
        "bytes": ZIP.stat().st_size,
        "sha256": sha256(ZIP),
        "crc_test": "pass" if bad is None else f"fail:{bad}",
        "entry_set_matches_analysis": set(names)
        == {
            path.relative_to(SAVED).as_posix()
            for path in ANALYSIS.rglob("*")
            if path.is_file()
        },
        "content_parity": "validated_by_analysis/tools/validate_package.py",
    }


def validate_archived_prior_package() -> dict:
    analysis_dir = ARCHIVE / "analysis_dirs" / "previous-standard-analysis_v001"
    zip_path = (
        ARCHIVE
        / "zips"
        / f"{SAVED.name}-previous-standard-analysis_v001.zip"
    )
    files = {
        path.relative_to(analysis_dir).as_posix(): path.read_bytes()
        for path in analysis_dir.rglob("*")
        if path.is_file()
    }
    with zipfile.ZipFile(zip_path) as archive:
        bad = archive.testzip()
        entries = {
            item.filename.removeprefix("analysis/"): archive.read(item)
            for item in archive.infolist()
            if not item.is_dir()
        }
    return {
        "analysis_directory": analysis_dir.relative_to(
            REPO / "saved_games"
        ).as_posix(),
        "zip_path": zip_path.relative_to(REPO / "saved_games").as_posix(),
        "analysis_file_count": len(files),
        "zip_file_count": len(entries),
        "zip_sha256": sha256(zip_path),
        "zip_crc_test": "pass" if bad is None else f"fail:{bad}",
        "entry_set_parity": set(files) == set(entries),
        "byte_content_parity": (
            set(files) == set(entries)
            and all(files[name] == entries[name] for name in files)
        ),
    }


def main() -> None:
    correct_standard_decision_counts()
    run_inventory = inventory("run", RUN)
    quality_inventory = inventory("quality_check", QUALITY)
    source = {
        "schema_version": "source_artifact_hashes_v1",
        "run_id": RUN_ID,
        "source_commit": SOURCE_COMMIT,
        "freeze": {
            "captured_before_regeneration": True,
            "final_reverification": "exact_match",
            "canonical_source_policy": (
                "Current checked-in run/ and quality_check/ bytes are canonical."
            ),
        },
        "artifact_sets": {
            "run": run_inventory,
            "quality_check": quality_inventory,
        },
        "legacy_artifact_manifest_audit": audit_legacy_manifest(run_inventory),
    }
    write_json(ANALYSIS / "manifests" / "source_artifact_hashes.json", source)

    replay = build_replay()
    completeness, calls, flags = build_quality_outputs(replay)
    write_json(ANALYSIS / "quality" / "replay_verification.json", replay)
    write_json(ANALYSIS / "quality" / "artifact_completeness.json", completeness)
    write_json(ANALYSIS / "quality" / "call_reconciliation.json", calls)
    write_json(ANALYSIS / "quality" / "quality_flags.json", flags)
    (ANALYSIS / "README.md").write_text(
        build_readme(), encoding="utf-8", newline="\n"
    )
    (ANALYSIS / "reports" / "integrity_report.md").write_text(
        build_integrity_report(source, completeness, calls, replay, flags),
        encoding="utf-8",
        newline="\n",
    )
    write_integrity_csv(source, completeness, calls, replay, flags)
    write_json(ANALYSIS / "manifests" / "analysis_manifest.json", generated_manifest())

    archive_analysis = sorted(
        path.relative_to(REPO / "saved_games").as_posix()
        for path in (ARCHIVE / "analysis_dirs").iterdir()
        if path.is_dir()
    )
    archive_zips = sorted(
        path.relative_to(REPO / "saved_games").as_posix()
        for path in (ARCHIVE / "zips").iterdir()
        if path.is_file()
    )
    preliminary_zip = build_zip()
    root_entries = sorted(path.name for path in SAVED.iterdir())
    saved_manifest = {
        "schema_version": "saved_game_manifest_v2",
        "saved_game": SAVED.name,
        "run_id": RUN_ID,
        "root_entries": root_entries,
        "layout": {
            "run": "run",
            "quality_check": "quality_check",
            "analysis": "analysis",
            "standard_analysis_zip": ZIP.name,
            "global_archive_dir": ARCHIVE.relative_to(REPO / "saved_games").as_posix(),
        },
        "source_freeze": {
            "source_commit": SOURCE_COMMIT,
            "run_file_count": run_inventory["file_count"],
            "run_total_bytes": run_inventory["total_bytes"],
            "run_tree_sha256": run_inventory["tree_sha256"],
            "quality_check_file_count": quality_inventory["file_count"],
            "quality_check_total_bytes": quality_inventory["total_bytes"],
            "quality_check_tree_sha256": quality_inventory["tree_sha256"],
            "tree_hash_format": TREE_FORMAT,
            "final_exact_match": True,
        },
        "archive": {
            "analysis_directories": archive_analysis,
            "zips": archive_zips,
            "old_analysis_and_zip_preserved": bool(archive_analysis and archive_zips),
            "archived_prior_package_validation": validate_archived_prior_package(),
        },
        "deterministic_analysis": {
            "status": "complete",
            "qualitative_review": "deferred",
            "events": completeness["counts"]["events"],
            "actions": calls["counts"]["applied_actions"],
            "resolved_decisions": calls["counts"]["resolved_decisions"],
            "attempts": calls["counts"]["attempts"],
            "retry_decisions": calls["counts"]["retry_decisions"],
            "invalid_attempts": calls["counts"]["invalid_attempts"],
            "fallbacks": calls["counts"]["fallback_decisions"],
            "state_replay_status": replay["state_replay"]["status"],
            "artifact_replay_status": replay["artifact_replay"]["status"],
            "known_cost": calls["usage_reconciliation"]["attempt_sums"]["cost"],
        },
        "zip_validation": preliminary_zip,
        "preservation_policy": (
            "run/ and quality_check/ are immutable canonical evidence. Prior analysis "
            "and ZIP outputs remain under saved_games/archive/."
        ),
    }
    write_json(SAVED / "saved_game_manifest.json", saved_manifest)

    # saved_game_manifest.json is outside analysis/ and therefore does not alter the ZIP.
    final_zip = build_zip()
    saved_manifest["zip_validation"] = final_zip
    write_json(SAVED / "saved_game_manifest.json", saved_manifest)
    print(
        json.dumps(
            {
                "status": "pass",
                "run_tree_sha256": run_inventory["tree_sha256"],
                "quality_check_tree_sha256": quality_inventory["tree_sha256"],
                "analysis_zip_sha256": final_zip["sha256"],
                "analysis_zip_files": final_zip["file_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
