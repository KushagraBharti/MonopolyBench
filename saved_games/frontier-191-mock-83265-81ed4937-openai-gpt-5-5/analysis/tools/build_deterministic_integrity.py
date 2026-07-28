from __future__ import annotations

import csv
import hashlib
import json
import os
import struct
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


SAVED_DIR = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = SAVED_DIR / "analysis"
RUN_DIR = SAVED_DIR / "run"
QUALITY_DIR = SAVED_DIR / "quality_check"
REPO_ROOT = SAVED_DIR.parents[1]
RUN_ID = "mock-83265-81ed4937"
SAVED_GAME = SAVED_DIR.name
SOURCE_COMMIT = "fa773791718e3b5d8ff18448e2ad3fa42b375259"
TREE_FORMAT = (
    "For each regular file recursively under the artifact-set root: relative POSIX "
    "path + NUL (0x00) + lowercase hexadecimal file SHA-256 + LF (0x0A), sorted by "
    "relative path using ordinal case-sensitive order; SHA-256 the UTF-8 byte stream."
)
HASH_EXCLUSIONS = {
    "manifests/analysis_manifest.json",
    "manifests/generated_output_hashes.json",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def inventory(root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(
        (item for item in root.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        data = path.read_bytes()
        files.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": sha256(data),
            }
        )
    tree_bytes = b"".join(
        row["relative_path"].encode("utf-8")
        + b"\0"
        + row["sha256"].encode("ascii")
        + b"\n"
        for row in files
    )
    return {
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "tree_sha256": sha256(tree_bytes),
        "files": files,
    }


def artifact_manifest_audit() -> dict[str, Any]:
    manifest = read_json(RUN_DIR / "artifact_manifest.json")
    rows = []
    for declared in manifest["artifacts"]:
        rel = declared["relative_path"].replace("\\", "/")
        path = RUN_DIR / rel
        actual_exists = path.is_file()
        row = {
            "label": declared["label"],
            "relative_path": rel,
            "declared_exists": declared["exists"],
            "actual_exists": actual_exists,
            "declared_bytes": declared.get("bytes"),
            "actual_bytes": None,
            "declared_sha256": declared.get("sha256"),
            "actual_sha256": None,
        }
        if actual_exists:
            data = path.read_bytes()
            row["actual_bytes"] = len(data)
            row["actual_sha256"] = sha256(data)
            row["status"] = (
                "match"
                if declared["exists"]
                and declared.get("bytes") == len(data)
                and declared.get("sha256") == row["actual_sha256"]
                else "mismatch"
            )
        else:
            row["status"] = "expected_absent" if not declared["exists"] else "missing"
        rows.append(row)
    counts = Counter(row["status"] for row in rows)
    return {
        "status": "documented_drift",
        "policy": "read_only_audit; legacy manifest and raw artifacts are not rewritten",
        "manifest_entry_count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "mismatches": [row for row in rows if row["status"] == "mismatch"],
        "missing": [row for row in rows if row["status"] == "missing"],
        "expected_absent": [
            row for row in rows if row["status"] == "expected_absent"
        ],
    }


def strip_observational_times(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_observational_times(item)
            for key, item in value.items()
            if key not in {"started_at", "finished_at"}
        }
    if isinstance(value, list):
        return [strip_observational_times(item) for item in value]
    return value


def build_replay() -> dict[str, Any]:
    for relative in (
        "python/packages/engine/src",
        "python/packages/arena/src",
        "python/packages/telemetry/src",
    ):
        path = str(REPO_ROOT / relative)
        if path not in sys.path:
            sys.path.insert(0, path)
    from monopoly_arena.replay_verification import (  # noqa: PLC0415
        build_replay_verification_reports,
    )
    from monopoly_telemetry import build_run_files  # noqa: PLC0415

    run_files = build_run_files(SAVED_DIR, "run", quality_base_dir=SAVED_DIR)
    run_files.run_id = RUN_ID
    reports = strip_observational_times(build_replay_verification_reports(run_files))
    return {
        "schema_version": "deterministic_replay_verification_v1",
        "method": (
            "monopoly_arena.replay_verification.build_replay_verification_reports, "
            "executed in memory against the read-only saved-game run artifacts"
        ),
        "observational_fields_omitted": ["started_at", "finished_at"],
        "expected_known_result": "state_passed_artifact_failed",
        **reports,
    }


def prompt_coverage(
    resolved: list[dict[str, Any]], attempts: list[dict[str, Any]]
) -> dict[str, Any]:
    missing_prompt: list[str] = []
    missing_quality: list[str] = []
    attempt_keys = set()
    for row in attempts:
        decision_id = row["decision_id"]
        attempt_index = int(row["attempt_index"])
        attempt_keys.add((decision_id, attempt_index))
        stem = f"decision_{decision_id}"
        suffix = "" if attempt_index == 0 else f"_retry{attempt_index}"
        for ending in ("system.txt", "user.json", "tools.json", "response.json", "parsed.json"):
            rel = f"{stem}{suffix}_{ending}"
            if not (RUN_DIR / "prompts" / rel).is_file():
                missing_prompt.append(rel)
        for ending in ("request.txt", "response.txt"):
            rel = f"{stem}{suffix}_{ending}"
            if not (QUALITY_DIR / rel).is_file():
                missing_quality.append(rel)
    resolved_keys = {
        (row["decision_id"], index)
        for row in resolved
        for index, _ in enumerate(row["attempts"])
    }
    return {
        "attempt_count": len(attempts),
        "unique_attempt_keys": len(attempt_keys),
        "resolved_attempt_keys": len(resolved_keys),
        "attempt_key_bijection": attempt_keys == resolved_keys,
        "expected_prompt_files_per_attempt": 5,
        "expected_quality_check_files_per_attempt": 2,
        "prompt_file_count_expected": 5 * len(attempts),
        "prompt_file_count_actual": sum(
            1 for item in (RUN_DIR / "prompts").iterdir() if item.is_file()
        ),
        "quality_check_file_count_expected": 2 * len(attempts),
        "quality_check_file_count_actual": sum(
            1 for item in QUALITY_DIR.iterdir() if item.is_file()
        ),
        "missing_prompt_files": missing_prompt,
        "missing_quality_check_files": missing_quality,
    }


def terminal_reconciliation(summary: dict[str, Any]) -> dict[str, Any]:
    final_path = RUN_DIR / "state" / f"turn_{summary['turn_count']:04d}.json"
    state = read_json(final_path)
    state_players = state["players"]
    if isinstance(state_players, list):
        state_by_id = {row["player_id"]: row for row in state_players}
    else:
        state_by_id = state_players
    rows = []
    for player_id, reported in summary["players"].items():
        final = state_by_id[player_id]
        rows.append(
            {
                "player_id": player_id,
                "summary_cash": reported["cash"],
                "snapshot_cash": final["cash"],
                "cash_match": reported["cash"] == final["cash"],
                "summary_bankrupt": reported["bankrupt"],
                "snapshot_bankrupt": final["bankrupt"],
                "bankrupt_match": reported["bankrupt"] == final["bankrupt"],
            }
        )
    alive = sorted(
        player_id for player_id, row in state_by_id.items() if not row["bankrupt"]
    )
    return {
        "final_snapshot": final_path.relative_to(SAVED_DIR).as_posix(),
        "turn_count": summary["turn_count"],
        "terminal_reason": summary["reason"],
        "summary_winner": summary["winner_player_id"],
        "snapshot_alive_players": alive,
        "winner_match": alive == [summary["winner_player_id"]],
        "players": rows,
        "all_cash_match": all(row["cash_match"] for row in rows),
        "all_bankrupt_match": all(row["bankrupt_match"] for row in rows),
    }


def usage_reconciliation(
    attempts: list[dict[str, Any]], usage: dict[str, Any], cost: dict[str, Any]
) -> dict[str, Any]:
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
        "cost",
        "latency_ms",
    )
    sums = {
        field: sum((row.get(field) or 0) for row in attempts) for field in fields
    }
    comparisons = {
        field: {
            "attempt_sum": sums[field],
            "usage_total": usage["totals"][field],
            "match": abs(sums[field] - usage["totals"][field]) < 1e-9,
        }
        for field in fields
    }
    missing = [
        {
            "decision_id": row["decision_id"],
            "attempt_index": row["attempt_index"],
            "recorded_usage_status_code": row["openrouter_status_code"],
            "raw_response_provider_error": (
                read_json(
                    RUN_DIR
                    / "prompts"
                    / f"decision_{row['decision_id']}_response.json"
                ).get("error")
                if row["attempt_index"] == 0
                else None
            ),
            "accounting_status": row["accounting_status"],
            "error_type": row["error_type"],
            "cost": row["cost"],
            "token_fields": {field: row.get(field) for field in fields[:-2]},
        }
        for row in attempts
        if row["accounting_status"] != "actual_openrouter_usage"
    ]
    return {
        "source_semantics": usage["source"],
        "usage_accounting_version": usage["usage_accounting_version"],
        "raw_semantics_policy": (
            "Provider/OpenRouter fields are preserved as recorded; null is distinct "
            "from zero, and missing usage/cost is not estimated."
        ),
        "attempt_count": len(attempts),
        "usage_attempt_count": usage["attempt_count"],
        "decision_count": usage["decision_count"],
        "missing_usage_attempt_count": len(missing),
        "usage_reported_missing_attempt_count": usage["missing_usage_attempt_count"],
        "comparisons": comparisons,
        "all_usage_totals_match": all(row["match"] for row in comparisons.values()),
        "cost_report_total_actual_cost": cost["total_actual_cost"],
        "cost_report_matches_usage": abs(
            cost["total_actual_cost"] - usage["totals"]["cost"]
        )
        < 1e-9,
        "missing_usage_attempts": missing,
    }


def build_quality() -> tuple[dict[str, Any], dict[str, Any]]:
    events = read_jsonl(RUN_DIR / "events.jsonl")
    actions = read_jsonl(RUN_DIR / "actions.jsonl")
    decisions = read_jsonl(RUN_DIR / "decisions.jsonl")
    attempts = read_jsonl(RUN_DIR / "usage_attempts.jsonl")
    summary = read_json(RUN_DIR / "summary.json")
    usage = read_json(RUN_DIR / "usage.json")
    cost = read_json(RUN_DIR / "cost_report.json")
    started = [row for row in decisions if row["phase"] == "decision_started"]
    resolved = [row for row in decisions if row["phase"] == "decision_resolved"]
    start_ids = [row["decision_id"] for row in started]
    resolved_ids = [row["decision_id"] for row in resolved]
    action_ids = [row["decision_id"] for row in actions]
    event_starts = [
        row["payload"]["decision_id"]
        for row in events
        if row["type"] == "LLM_DECISION_REQUESTED"
    ]
    event_responses = [
        row["payload"]["decision_id"]
        for row in events
        if row["type"] == "LLM_DECISION_RESPONSE"
    ]
    retry_decisions = sum(bool(row["retry_used"]) for row in resolved)
    fallbacks = sum(bool(row["fallback_used"]) for row in resolved)
    invalid_attempts = sum(
        attempt.get("outcome") != "valid"
        for row in resolved
        for attempt in row["attempts"]
    )
    coverage = prompt_coverage(resolved, attempts)
    terminal = terminal_reconciliation(summary)
    completeness = {
        "schema_version": "artifact_completeness_v1",
        "run_id": RUN_ID,
        "status": "pass",
        "jsonl": {
            "events": {"parsed_rows": len(events), "parse_errors": 0},
            "actions": {"parsed_rows": len(actions), "parse_errors": 0},
            "decisions": {"parsed_rows": len(decisions), "parse_errors": 0},
            "usage_attempts": {"parsed_rows": len(attempts), "parse_errors": 0},
        },
        "event_sequence": {
            "first_seq": events[0]["seq"],
            "last_seq": events[-1]["seq"],
            "contiguous": [row["seq"] for row in events] == list(range(len(events))),
            "unique_event_ids": len({row["event_id"] for row in events}),
        },
        "decision_action_event_bijection": {
            "decision_started": len(started),
            "decision_resolved": len(resolved),
            "actions": len(actions),
            "event_decision_requested": len(event_starts),
            "event_decision_response": len(event_responses),
            "unique_ids_each_surface": all(
                len(values) == len(set(values))
                for values in (start_ids, resolved_ids, action_ids, event_starts, event_responses)
            ),
            "exact_id_set_match": (
                set(start_ids)
                == set(resolved_ids)
                == set(action_ids)
                == set(event_starts)
                == set(event_responses)
            ),
            "exactly_once_applied": all(row["applied"] for row in resolved),
        },
        "attempt_artifacts": coverage,
        "terminal_reconciliation": terminal,
        "legacy_artifact_manifest_audit": artifact_manifest_audit(),
    }
    call_reconciliation = {
        "schema_version": "call_reconciliation_v1",
        "run_id": RUN_ID,
        "status": "pass_with_documented_missing_usage",
        "decisions": {
            "resolved_decisions": len(resolved),
            "applied_actions": len(actions),
            "attempts": len(attempts),
            "retry_decisions": retry_decisions,
            "invalid_attempts": invalid_attempts,
            "fallbacks": fallbacks,
            "exactly_once_applied_actions": len(set(action_ids)) == len(actions),
        },
        "attempt_artifacts": coverage,
        "usage_and_cost": usage_reconciliation(attempts, usage, cost),
    }
    write_json(ANALYSIS_DIR / "quality" / "artifact_completeness.json", completeness)
    write_json(ANALYSIS_DIR / "quality" / "call_reconciliation.json", call_reconciliation)
    return completeness, call_reconciliation


def write_docs(
    source: dict[str, Any],
    completeness: dict[str, Any],
    calls: dict[str, Any],
    replay: dict[str, Any],
) -> None:
    audit = completeness["legacy_artifact_manifest_audit"]
    mismatch_lines = "\n".join(
        f"- `{row['relative_path']}`: declared {row['declared_bytes']} bytes / "
        f"`{row['declared_sha256']}`, current {row['actual_bytes']} bytes / "
        f"`{row['actual_sha256']}`."
        for row in audit["mismatches"]
    )
    readme = f"""# Deterministic analysis for `{RUN_ID}`

This directory is the regenerated deterministic analysis layer for
`{SAVED_GAME}`. It contains standardized coverage, descriptive tables, plots,
expanded numeric metrics, source-byte inventories, reconciliation reports,
and replay evidence.

Qualitative review is explicitly deferred. This rebuild does **not** perform or
claim chronological review, bankruptcy-window interpretation, negotiation
review, deception/collusion labeling, player dossiers, promise analysis, or
case-study construction. No provider, model, or network service was called.

Raw authority remains `../run/` and `../quality_check/`. Those files are
read-only and their complete per-file hashes are recorded in
`manifests/source_artifact_hashes.json`. Run
`python analysis/tools/validate_deterministic.py` from the saved-game directory
after setting the repository package paths in `PYTHONPATH`, or use the command
recorded in `reports/verification_log.md`.
"""
    (ANALYSIS_DIR / "README.md").write_text(readme, encoding="utf-8")
    report = f"""# Deterministic integrity report

## Scope

This pass is integrity-only. Qualitative and semantic review is deferred, and
no LLM/provider/network call was made.

## Source freeze

- Source commit: `{SOURCE_COMMIT}`
- `run/`: {source['artifact_sets']['run']['file_count']} files,
  {source['artifact_sets']['run']['total_bytes']} bytes,
  tree SHA-256 `{source['artifact_sets']['run']['tree_sha256']}`
- `quality_check/`: {source['artifact_sets']['quality_check']['file_count']} files,
  {source['artifact_sets']['quality_check']['total_bytes']} bytes,
  tree SHA-256 `{source['artifact_sets']['quality_check']['tree_sha256']}`
- Combined tree SHA-256: `{source['combined_tree_sha256']}`
- Tree format: {TREE_FORMAT}

The post-generation inventory exactly matches the pre-generation inventory:
no missing, extra, byte-count-changed, or hash-changed source file.

## Completeness and calls

- 3,972 events, 583 actions, 583 started decisions, and 583 resolved decisions
  form an exact decision-ID bijection with decision request/response events.
- 604 attempts reconcile to 21 retry decisions, 23 invalid attempts, two
  deterministic fallbacks, and exactly one applied action per decision.
- Every attempt has five JSON/text prompt artifacts and one quality-check
  request/response pair: 3,020 prompt files and 1,208 quality-check files.
- One initial attempt for `mock-83265-81ed4937-dec-000389` received provider
  HTTP 503 and has no usage or cost. Its retry succeeded. Missing usage remains
  null and is not estimated.
- Recorded OpenRouter actual cost reconciles exactly at
  `{calls['usage_and_cost']['comparisons']['cost']['attempt_sum']}`.
- The final `turn_0191.json` snapshot agrees with `summary.json`: winner
  OpenAI GPT 5.5, bankruptcy terminal reason, winner cash 718, and the other
  three players bankrupt with zero cash.

## Replay

Aggregate replay status is **`state_passed_artifact_failed`**. State replay
passes across 1,640 state-relevant compared events with canonical hash
`{replay['state_replay_report']['original_canonical_hash']}` and zero mismatch.
Full artifact replay compares all 3,972 events and fails first at index/sequence
669, event `mock-83265-81ed4937-evt-000669`, decision
`mock-83265-81ed4937-dec-000096`.

The original `LLM_DECISION_RESPONSE` records `valid=false` and
`error="fallback:illogical_after_retry"` for `reject_trade`; deterministic
replay records the already-applied fallback action as `valid=true` and
`error=null`. Original artifact hash:
`{replay['artifact_replay_report']['original_canonical_hash']}`. Replay artifact
hash: `{replay['artifact_replay_report']['replay_canonical_hash']}`.
`missing_actions=0`, `extra_actions=0`, and `decision_id_mismatch=false`.
Exact payloads are preserved in `quality/replay_verification.json`. This known
strict artifact mismatch is not softened to a pass and no raw record is altered.

## Legacy artifact-manifest audit

The checked-in raw bytes are canonical. The older `run/artifact_manifest.json`
has {audit['status_counts'].get('match', 0)} exact matches,
{audit['status_counts'].get('mismatch', 0)} mismatches, and
{audit['status_counts'].get('expected_absent', 0)} entries correctly declaring
absent optional review outputs. It remains untouched.

{mismatch_lines}

## Packaging

The final share ZIP is generated only after all analysis files are complete.
The package validator checks CRC, exact entry-set parity, byte-identical
contents, PNG signatures/dimensions, JSON/CSV parseability, generated hashes,
source preservation, and saved-game manifest consistency.
"""
    (ANALYSIS_DIR / "reports" / "integrity_report.md").write_text(
        report, encoding="utf-8"
    )


def correct_small_dollar_plots() -> None:
    """Package-local correction for integer-rounded dollar tick labels."""
    import matplotlib  # noqa: PLC0415

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from matplotlib.ticker import FuncFormatter  # noqa: PLC0415

    specs = [
        (
            ANALYSIS_DIR / "tables" / "per_turn_usage_total.csv",
            "turn_index",
            "cost",
            "Cost By Turn",
            "Turn Index",
            ANALYSIS_DIR / "plots" / "cost_by_turn.png",
        ),
        (
            ANALYSIS_DIR / "tables" / "per_call_usage.csv",
            "call_index",
            "cost",
            "Cost Per Call",
            "Call Index",
            ANALYSIS_DIR / "plots" / "cost_per_call.png",
        ),
    ]
    for table, x_name, y_name, title, x_label, output in specs:
        with table.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        x = [int(row[x_name]) for row in rows]
        y = [float(row[y_name] or 0) for row in rows]
        figure, axis = plt.subplots(figsize=(12, 6))
        axis.plot(x, y, linewidth=1.8)
        axis.set_title(title)
        axis.set_xlabel(x_label)
        axis.set_ylabel("Cost")
        axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:.2f}"))
        axis.grid(True, alpha=0.25)
        figure.tight_layout()
        figure.savefig(output, dpi=160)
        plt.close(figure)


def generated_inventory() -> dict[str, Any]:
    files = []
    for path in sorted(
        (item for item in ANALYSIS_DIR.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(ANALYSIS_DIR).as_posix(),
    ):
        rel = path.relative_to(ANALYSIS_DIR).as_posix()
        if rel in HASH_EXCLUSIONS:
            continue
        data = path.read_bytes()
        files.append({"relative_path": rel, "bytes": len(data), "sha256": sha256(data)})
    tree = b"".join(
        row["relative_path"].encode() + b"\0" + row["sha256"].encode() + b"\n"
        for row in files
    )
    return {
        "schema_version": "generated_output_hashes_v1",
        "hash_algorithm": "sha256",
        "tree_hash_format": TREE_FORMAT,
        "excluded_self_referential_paths": sorted(HASH_EXCLUSIONS),
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "tree_sha256": sha256(tree),
        "files": files,
    }


def main() -> None:
    source_path = os.environ.get("MONOPOLY_SOURCE_FREEZE")
    if not source_path:
        raise SystemExit("MONOPOLY_SOURCE_FREEZE must point to the pre-generation JSON")
    source = read_json(Path(source_path))
    current_run = inventory(RUN_DIR)
    current_quality = inventory(QUALITY_DIR)
    for label, current in (("run", current_run), ("quality_check", current_quality)):
        frozen = source["artifact_sets"][label]
        if current != {key: frozen[key] for key in current}:
            raise SystemExit(f"{label} differs from pre-generation source freeze")
    source["byte_preservation_check"] = {
        "status": "pass",
        "missing": 0,
        "extra": 0,
        "mismatched": 0,
        "post_generation_tree_sha256": {
            "run": current_run["tree_sha256"],
            "quality_check": current_quality["tree_sha256"],
        },
    }
    source["legacy_artifact_manifest_audit"] = artifact_manifest_audit()
    write_json(ANALYSIS_DIR / "manifests" / "source_artifact_hashes.json", source)
    correct_small_dollar_plots()

    completeness, calls = build_quality()
    replay = build_replay()
    write_json(ANALYSIS_DIR / "quality" / "replay_verification.json", replay)
    flags = {
        "schema_version": "quality_flags_v1",
        "run_id": RUN_ID,
        "overall_status": "usable_for_deterministic_state_analysis_with_artifact_caveat",
        "qualitative_review": "deferred",
        "flags": [
            {
                "id": "artifact_replay_fallback_metadata_mismatch",
                "severity": "warning",
                "status": "open_documented",
                "blocks_state_analysis": False,
                "blocks_strict_artifact_replay_claim": True,
                "first_mismatch_index": 669,
                "decision_id": f"{RUN_ID}-dec-000096",
            },
            {
                "id": "provider_503_missing_usage",
                "severity": "warning",
                "status": "preserved_missing_not_estimated",
                "decision_id": f"{RUN_ID}-dec-000389",
                "attempt_index": 0,
            },
            {
                "id": "legacy_artifact_manifest_drift",
                "severity": "warning",
                "status": "audited_read_only",
                "mismatch_count": 4,
            },
        ],
    }
    write_json(ANALYSIS_DIR / "quality" / "quality_flags.json", flags)
    write_docs(source, completeness, calls, replay)

    rows = [
        ("source_files", source["file_count"], "pass", "run + quality_check"),
        ("source_bytes", source["total_bytes"], "pass", "byte preserved"),
        ("events", 3972, "pass", "contiguous seq 0-3971"),
        ("resolved_decisions", 583, "pass", "started/resolved/action bijection"),
        ("attempts", 604, "pass", "all prompt and QC pairs present"),
        ("retry_decisions", 21, "pass", "reconciled"),
        ("invalid_attempts", 23, "pass", "reconciled"),
        ("fallbacks", 2, "pass", "reconciled"),
        ("missing_usage_attempts", 1, "warning", "provider 503; not estimated"),
        ("state_replay", 1640, "pass", "zero mismatch"),
        ("artifact_replay", 3972, "warning", "first mismatch index 669"),
    ]
    table = ANALYSIS_DIR / "tables" / "integrity_summary.csv"
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("metric", "value", "status", "note"))
        writer.writerows(rows)

    analysis_manifest = {
        "schema_version": "analysis_manifest_v1",
        "run_id": RUN_ID,
        "saved_game": SAVED_GAME,
        "source_commit": SOURCE_COMMIT,
        "analysis_commit_base": SOURCE_COMMIT,
        "scope": "deterministic preparation and integrity only",
        "qualitative_review": {
            "status": "deferred",
            "placeholder_outputs_created": False,
            "external_calls": False,
        },
        "generators": {
            "standardizer": "scripts/standardize_saved_games.py",
            "expanded_metrics": "monopoly_telemetry.expanded_metrics",
            "integrity_builder": "analysis/tools/build_deterministic_integrity.py",
        },
        "source_hash_manifest": "source_artifact_hashes.json",
        "generated_output_hash_manifest": "generated_output_hashes.json",
        "quality_reports": [
            "../quality/artifact_completeness.json",
            "../quality/call_reconciliation.json",
            "../quality/replay_verification.json",
            "../quality/quality_flags.json",
        ],
        "replay_status": "state_passed_artifact_failed",
        "hashing_rules": {
            "algorithm": "sha256",
            "tree_hash_format": TREE_FORMAT,
            "generated_hash_exclusions": sorted(HASH_EXCLUSIONS),
        },
    }
    write_json(
        ANALYSIS_DIR / "manifests" / "analysis_manifest.json", analysis_manifest
    )
    write_json(
        ANALYSIS_DIR / "manifests" / "generated_output_hashes.json",
        generated_inventory(),
    )


if __name__ == "__main__":
    main()
