from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT = "analysis/research_protocol/readiness_audit.json"
E1_CAMPAIGN_ID = "monopoly-long-v1-e1-pilot-random-v1"
COMPLETE_RUN_STATUSES = {"completed", "resumed_completed"}
RECORDED_RUN_STATUSES = COMPLETE_RUN_STATUSES | {
    "failed",
    "not_runnable",
    "not_started_after_failure",
    "not_started_budget_stop",
    "not_started_credit_gate",
    "not_started_max_runs_limit",
    "not_started_preflight_gate",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit research-protocol readiness without making provider calls."
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--campaign-dir",
        default=f"runs/campaigns/{E1_CAMPAIGN_ID}",
        help="Executed E1 campaign directory, not the planning-only directory.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    output_path = (repo_root / args.output).resolve()
    campaign_dir = (repo_root / args.campaign_dir).resolve()

    checks = [
        _protocol_check(repo_root),
        _architecture_check(repo_root),
        _bridge_check(repo_root),
        _campaign_control_check(repo_root),
        _pilot_games_check(repo_root, campaign_dir),
        _fixture_pilot_check(repo_root),
        _communication_check(repo_root),
        _power_budget_check(repo_root),
        _preregistration_check(repo_root),
        _ecological_campaign_check(repo_root),
    ]
    blocking = [check["requirement_id"] for check in checks if check["status"] != "complete"]
    external = [
        check["requirement_id"]
        for check in checks
        if check["status"] == "blocked_external"
    ]
    payload = {
        "schema_version": "research_protocol_readiness_audit_v1",
        "generated_at_utc": _utc_now(),
        "source_commit": _git_head(repo_root),
        "goal_complete": not blocking,
        "provider_calls": 0,
        "summary": {
            "requirement_count": len(checks),
            "status_counts": dict(sorted(Counter(check["status"] for check in checks).items())),
            "blocking_requirement_ids": blocking,
            "external_blocker_ids": external,
        },
        "requirements": checks,
        "prompt_pipeline": {
            "status": "unchanged",
            "note": (
                "This audit reads downstream protocol and campaign artifacts only. "
                "It does not construct or submit a model-facing request."
            ),
        },
        "provenance": {
            "script": _relative(repo_root, Path(__file__).resolve()),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    markdown_path = output_path.with_suffix(".md")
    markdown_path.write_text(_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "goal_complete": payload["goal_complete"],
                "output": _relative(repo_root, output_path),
                "provider_calls": 0,
                "status_counts": payload["summary"]["status_counts"],
            },
            sort_keys=True,
        )
    )
    return 0


def _protocol_check(repo_root: Path) -> dict[str, Any]:
    required = {
        "docs/research_protocol/scientific_protocol_v2.md": (
            "## 4. Experimental layers",
            "## 6. Primary estimands",
            "## 8. Confirmatory hypotheses",
            "## 9. Randomness policy",
            "## 10. Inclusion and exclusion",
            "## 11. Generalization contract",
        ),
        "docs/research_protocol/social_evidence_codebook.md": (
            "## 3. Episode universe and eligible denominators",
            "## 12. Judge-first review procedure",
            "## 13. Gates",
        ),
        "docs/research_protocol/llm_judge_social_evidence_protocol.md": (
            "## 6. Complete review universe",
            "## 7. Judge passes",
            "## 12. Human-review sampling",
            "## 16. Gates",
        ),
    }
    missing: list[str] = []
    evidence: list[dict[str, Any]] = []
    for relative_path, markers in required.items():
        path = repo_root / relative_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        missing_markers = [marker for marker in markers if marker not in text]
        if not path.exists() or missing_markers:
            missing.append(relative_path)
        evidence.append(
            {
                "path": relative_path,
                "sha256": _sha256_file(path) if path.exists() else None,
                "missing_markers": missing_markers,
            }
        )
    return _check(
        "protocol",
        "Rewrite the scientific protocol",
        complete=not missing,
        evidence=evidence,
        blockers=missing,
        complete_note=(
            "Ecological layers, robustness rings, stochasticity, estimands, hypotheses, "
            "inclusion, and bounded generalization are explicitly specified."
        ),
    )


def _architecture_check(repo_root: Path) -> dict[str, Any]:
    proof_path = repo_root / "analysis/research_protocol/architecture_proof/manifest.json"
    fixtures_path = (
        repo_root / "analysis/research_protocol/architecture_proof/fixtures_v2/manifest.json"
    )
    proof = _read_json(proof_path)
    fixtures = _read_json(fixtures_path)
    conditions = {
        "decision_count_at_least_12": _number(proof.get("decision_count")) >= 12,
        "engine_replay_exact": proof.get("all_engine_replay_prompts_exact") is True,
        "recorded_event_replay_exact": proof.get("all_recorded_event_prompts_exact") is True,
        "provider_calls_zero": proof.get("provider_calls") == 0,
        "v2_fixture_count_matches": fixtures.get("fixture_count") == proof.get("decision_count"),
        "v2_all_exact_history": fixtures.get("all_exact_history") is True,
        "memory_loss_ledger_exists": (
            repo_root / "analysis/research_protocol/architecture_proof/memory_loss.jsonl"
        ).exists(),
        "v1_defect_preserved": (
            repo_root
            / "analysis/research_protocol/architecture_proof/fixture_format_migration.md"
        ).exists(),
    }
    return _check(
        "architecture_proof",
        "Run a zero-cost architecture proof",
        complete=all(conditions.values()),
        evidence=[
            _file_evidence(repo_root, proof_path),
            _file_evidence(repo_root, fixtures_path),
            {"conditions": conditions},
        ],
        blockers=[name for name, passed in conditions.items() if not passed],
        complete_note=(
            "Twelve decisions pass exact reconstruction from both in-memory replay and "
            "persisted v2 ordered inputs; memory loss is quantified and provider calls are zero."
        ),
    )


def _bridge_check(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "docs/research_protocol/downstream_bridge_contracts.md"
    markers = (
        "## 2. Trajectory fixture extraction contract",
        "## 3. Exact-history replay contract",
        "## 4. Repetition manifest contract",
        "## 5. One-step branch contract",
        "## 6. Provenance requirements",
        "## 8. Quality gates",
    )
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    missing = [marker for marker in markers if marker not in text]
    return _check(
        "downstream_bridge",
        "Specify the downstream bridge",
        complete=path.exists() and not missing,
        evidence=[_file_evidence(repo_root, path), {"missing_markers": missing}],
        blockers=missing,
        complete_note=(
            "Extraction, exact-history replay, repetition, one-step branch, provenance, "
            "failure, and quality contracts are specified without engine or prompt changes."
        ),
    )


def _campaign_control_check(repo_root: Path) -> dict[str, Any]:
    plan_dir = (
        repo_root
        / "analysis/research_protocol/pilot/planning_runs/campaigns"
        / E1_CAMPAIGN_ID
    )
    matrix_path = plan_dir / "run_matrix.json"
    execution_path = plan_dir / "execution_manifest.json"
    preflight_path = (
        repo_root / "analysis/research_protocol/control_audit/openrouter_preflight.json"
    )
    matrix = _read_json(matrix_path)
    execution = _read_json(execution_path)
    preflight = _read_json(preflight_path)
    rows = _list(matrix.get("runs"))
    actors = [actor for row in rows for actor in _list(_dict(row).get("actors"))]
    provider_pinned = all(
        _dict(actor).get("provider", {}).get("allow_fallbacks") is False
        and len(_list(_dict(actor).get("provider", {}).get("only"))) == 1
        for actor in actors
    )
    conditions = {
        "eight_planned_cells": len(rows) == 8,
        "unique_execution_ranks": sorted(
            int(_dict(row).get("execution_rank", -1)) for row in rows
        )
        == list(range(8)),
        "sequential_execution": execution.get("sequential_execution") is True,
        "provider_constraints_pinned": provider_pinned,
        "fallback_routing_disabled": provider_pinned,
        "all_routes_ready_at_preflight": _dict(preflight.get("verdict")).get(
            "all_routes_ready"
        )
        is True,
        "sampling_policy_disclosed": all(
            _dict(actor).get("top_p") is None for actor in actors
        ),
    }
    credits = _dict(preflight.get("credits"))
    external = not bool(
        _dict(preflight.get("verdict")).get("paid_pilot_authorized_by_preflight")
    )
    blockers = [name for name, passed in conditions.items() if not passed]
    evidence = [
        _file_evidence(repo_root, matrix_path),
        _file_evidence(repo_root, execution_path),
        _file_evidence(repo_root, preflight_path),
        {"conditions": conditions, "credits": credits},
    ]
    if blockers:
        return _check(
            "campaign_controls",
            "Audit campaign controls",
            complete=False,
            evidence=evidence,
            blockers=blockers,
        )
    return {
        **_check(
            "campaign_controls",
            "Audit campaign controls",
            complete=True,
            evidence=evidence,
            blockers=[],
            complete_note=(
                "Execution is sequential and randomized; provider routes are exact, "
                "fallbacks disabled, provider-default sampling disclosed, and endpoint "
                "preflight archived."
            ),
        ),
        "external_execution_gate": {
            "blocked": external,
            "reason": "available_credit_below_e1_gate" if external else None,
            "available_credits": credits.get("available_credits"),
            "minimum_available_required": credits.get("minimum_available_required"),
        },
    }


def _pilot_games_check(repo_root: Path, campaign_dir: Path) -> dict[str, Any]:
    plan_path = (
        repo_root
        / "analysis/research_protocol/pilot/planning_runs/campaigns"
        / E1_CAMPAIGN_ID
        / "run_matrix.json"
    )
    planned = [_dict(row) for row in _list(_read_json(plan_path).get("runs"))]
    results_path = campaign_dir / "run_results.json"
    if not results_path.exists():
        return _pending_check(
            "pilot_games",
            "Execute 2 seed blocks with four cyclic seat rotations",
            status="blocked_external",
            evidence=[_file_evidence(repo_root, plan_path)],
            blockers=[
                "Executed campaign run_results.json does not exist.",
                "OpenRouter credit gate has not passed.",
            ],
        )
    results = [_dict(row) for row in _list(_read_json(results_path).get("runs"))]
    planned_ids = [str(row.get("run_id")) for row in planned]
    result_ids = [str(row.get("run_id")) for row in results]
    duplicates = [run_id for run_id, count in Counter(result_ids).items() if count > 1]
    unknown = sorted(set(result_ids) - set(planned_ids))
    missing = sorted(set(planned_ids) - set(result_ids))
    invalid_status = sorted(
        {
            str(row.get("status"))
            for row in results
            if str(row.get("status")) not in RECORDED_RUN_STATUSES
        }
    )
    coverage = _seat_rotation_coverage(planned)
    complete = not duplicates and not unknown and not missing and not invalid_status
    blockers = []
    if duplicates:
        blockers.append(f"duplicate result rows: {duplicates}")
    if unknown:
        blockers.append(f"unplanned result rows: {unknown}")
    if missing:
        blockers.append(f"planned cells absent from ledger: {missing}")
    if invalid_status:
        blockers.append(f"unrecognized result statuses: {invalid_status}")
    if not coverage["complete"]:
        blockers.extend(coverage["errors"])
        complete = False
    completed_count = sum(1 for row in results if row.get("status") in COMPLETE_RUN_STATUSES)
    if completed_count < 8:
        blockers.append(
            f"Only {completed_count}/8 cells completed; failed/capped cells remain evidence "
            "but E1 nuisance estimation may be insufficient."
        )
        complete = False
    return _check(
        "pilot_games",
        "Execute 2 seed blocks with four cyclic seat rotations",
        complete=complete,
        evidence=[
            _file_evidence(repo_root, plan_path),
            _file_evidence(repo_root, results_path),
            {
                "planned_count": len(planned),
                "recorded_count": len(results),
                "completed_count": completed_count,
                "status_counts": dict(sorted(Counter(row.get("status") for row in results).items())),
                "seat_rotation_coverage": coverage,
            },
        ],
        blockers=blockers,
        complete_note=(
            "Every planned E1 cell is recorded, all eight completed, and both seed blocks "
            "contain complete cyclic seat coverage."
        ),
    )


def _fixture_pilot_check(repo_root: Path) -> dict[str, Any]:
    expected = (
        repo_root
        / "analysis/research_protocol/pilot/trajectory_fixture_repetitions_e1/manifest.json"
    )
    if not expected.exists():
        return _pending_check(
            "pilot_fixture_repetitions",
            "Repeat 20–30 exact-history decisions from E1",
            status="blocked_external",
            evidence=[
                _file_evidence(
                    repo_root,
                    repo_root
                    / "analysis/research_protocol/architecture_proof/repetition_plan_v2/manifest.json",
                )
            ],
            blockers=[
                "E1 trajectories do not exist yet.",
                "No paid E1 trajectory-fixture repetition manifest has executed.",
            ],
        )
    manifest = _read_json(expected)
    fixture_count = int(_number(manifest.get("fixture_count")))
    planned = int(_number(manifest.get("planned_call_count")))
    recorded = int(_number(manifest.get("recorded_call_count")))
    complete = (
        20 <= fixture_count <= 30
        and planned > 0
        and recorded == planned
        and manifest.get("status") == "complete"
    )
    return _check(
        "pilot_fixture_repetitions",
        "Repeat 20–30 exact-history decisions from E1",
        complete=complete,
        evidence=[_file_evidence(repo_root, expected), manifest],
        blockers=[] if complete else ["Fixture count, call coverage, or completion status failed."],
        complete_note="Twenty to thirty E1-derived decisions have complete repeated-query coverage.",
    )


def _communication_check(repo_root: Path) -> dict[str, Any]:
    packet_path = (
        repo_root
        / "analysis/research_protocol/pilot/communication_calibration_e0/packet_manifest.json"
    )
    calibration_path = (
        repo_root
        / "analysis/research_protocol/pilot/communication_calibration_e0/"
        "calibration_manifest.json"
    )
    packet_manifest = _read_json(packet_path)
    calibration_manifest = _read_json(calibration_path)
    packet_count = int(_number(packet_manifest.get("packet_count")))
    judge_protocol_path = (
        repo_root / "docs/research_protocol/llm_judge_social_evidence_protocol.md"
    )
    judge_protocol = (
        judge_protocol_path.read_text(encoding="utf-8")
        if judge_protocol_path.exists()
        else ""
    )
    rubric_path = (
        repo_root
        / "analysis/research_protocol/preregistration/draft/social_judge_rubric.json"
    )
    rubric = _read_json(rubric_path)
    rubric_coverage = _dict(rubric.get("coverage"))
    rubric_execution = _dict(rubric.get("execution_environment"))
    rubric_publication = _dict(rubric.get("publication_rules"))
    packet_judge_execution = _dict(packet_manifest.get("judge_execution"))
    packet_ready = (
        20 <= packet_count <= 30
        and packet_manifest.get("model_identity_masked") is True
        and packet_manifest.get("winner_and_rank_excluded") is True
        and packet_manifest.get("campaign_execution_blocker") is False
        and packet_judge_execution.get("external_model_api_calls") is False
        and packet_judge_execution.get("openrouter_calls") is False
    )
    judge_plan_ready = all(
        marker in judge_protocol
        for marker in (
            "## 6. Complete review universe",
            "### J1: Chronological high-recall sweep",
            "### 12.3 Negative audit",
            "### 16.1 Campaign execution gate",
        )
    ) and (
        rubric_coverage.get("focal_turn_coverage_required") == 1.0
        and rubric_coverage.get("lexical_prefilter_may_exclude_turns") is False
        and rubric_coverage.get(
            "explicit_negative_required_per_candidate_free_window"
        )
        is True
        and rubric_publication.get("campaign_blocked_by_human_review") is False
        and rubric_execution.get("mode") == "local_agentic_research_tool"
        and rubric_execution.get("external_model_api_calls") is False
        and rubric_execution.get("openrouter_calls") is False
    )
    blockers = []
    if not packet_ready:
        blockers.append("Instrument packet count or identity/outcome masking failed.")
    if not judge_plan_ready:
        blockers.append("Exhaustive judge and judge-negative audit protocol is incomplete.")
    complete = packet_ready and judge_plan_ready
    check = _pending_check(
        "communication_calibration",
        "Freeze judge-first social-evidence discovery and validation design",
        status="complete" if complete else "incomplete",
        evidence=[
            _file_evidence(repo_root, packet_path),
            packet_manifest,
            _file_evidence(repo_root, judge_protocol_path),
            _file_evidence(repo_root, rubric_path),
            rubric,
            _file_evidence(repo_root, calibration_path),
            calibration_manifest,
        ],
        blockers=blockers,
        complete_note=(
            "The instrument packet and exhaustive masked judge/human-audit workflow are "
            "frozen for preregistration; human results gate later social claims only."
        ),
    )
    check["publication_gate"] = {
        "status": (
            "complete"
            if calibration_manifest.get("calibration_passed") is True
            else "pending_downstream_human_validation"
        ),
        "campaign_execution_blocker": False,
        "human_coder_count_completed": int(
            _number(calibration_manifest.get("human_coder_count_completed"))
        ),
        "human_coder_count_required": int(
            _number(calibration_manifest.get("human_coder_count_required"))
        ),
        "adjudication_completed": calibration_manifest.get("adjudication_completed")
        is True,
        "calibration_passed": calibration_manifest.get("calibration_passed") is True,
    }
    return check


def _power_budget_check(repo_root: Path) -> dict[str, Any]:
    planning_path = repo_root / "analysis/research_protocol/pilot/budget_projection.json"
    design_lock_path = repo_root / "analysis/research_protocol/pilot/design_lock.json"
    power_path = repo_root / "analysis/research_protocol/pilot/power_simulation.json"
    planning = _read_json(planning_path)
    complete = design_lock_path.exists() and power_path.exists()
    evidence = [
        _file_evidence(repo_root, planning_path),
        _file_evidence(repo_root, design_lock_path),
        _file_evidence(repo_root, power_path),
        {
            "planning_credit_gate_passed": _dict(planning.get("gates")).get(
                "credit_gate_passed"
            )
        },
    ]
    return _pending_check(
        "power_and_budget_lock",
        "Use the pilot for power and budget simulation",
        status="complete" if complete else "pending_empirical",
        evidence=evidence,
        blockers=(
            []
            if complete
            else [
                "Empirical E1 nuisance estimates are unavailable.",
                "Final block, repeat, robustness, and fixture counts are not locked.",
            ]
        ),
        complete_note="Pilot-based power, precision, attrition, cost, and final design are locked.",
    )


def _preregistration_check(repo_root: Path) -> dict[str, Any]:
    path = (
        repo_root
        / "analysis/research_protocol/preregistration/frozen/preregistration_manifest.json"
    )
    complete = path.exists() and _read_json(path).get("status") == "frozen"
    return _pending_check(
        "freeze_and_preregister",
        "Freeze and preregister the confirmatory design",
        status="complete" if complete else "pending_empirical",
        evidence=[_file_evidence(repo_root, path)],
        blockers=(
            []
            if complete
            else [
                "Pilot-based design lock is incomplete.",
                "No frozen signed preregistration manifest exists.",
            ]
        ),
        complete_note="The complete preregistration input tree is frozen, hashed, and committed.",
    )


def _ecological_campaign_check(repo_root: Path) -> dict[str, Any]:
    path = (
        repo_root
        / "analysis/research_protocol/confirmatory/ecological_campaign/completion_audit.json"
    )
    complete = path.exists() and _read_json(path).get("goal_complete") is True
    return _pending_check(
        "ecological_campaign",
        "Run the ecological campaign and diagnostics",
        status="complete" if complete else "pending_preregistration",
        evidence=[_file_evidence(repo_root, path)],
        blockers=(
            []
            if complete
            else [
                "Confirmatory campaign cannot begin before preregistration freeze.",
                "No campaign-wide completion audit exists.",
            ]
        ),
        complete_note=(
            "Every planned confirmatory cell and diagnostic has a preserved status and "
            "validated evidence trail."
        ),
    )


def _seat_rotation_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    errors: list[str] = []
    for row in rows:
        by_seed[int(row.get("seed", -1))].append(row)
    seed_details: dict[str, Any] = {}
    for seed, seed_rows in sorted(by_seed.items()):
        actor_seats: dict[str, list[int]] = defaultdict(list)
        permutations = []
        for row in seed_rows:
            permutations.append(str(row.get("permutation_id")))
            for actor in _list(row.get("actors")):
                actor_payload = _dict(actor)
                actor_seats[str(actor_payload.get("actor_id"))].append(
                    int(actor_payload.get("seat_index", -1))
                )
        expected_permutations = [f"latin_square:{index}" for index in range(4)]
        if sorted(permutations) != expected_permutations:
            errors.append(f"Seed {seed} does not contain exactly four cyclic permutations.")
        for actor_id, seats in actor_seats.items():
            if sorted(seats) != [0, 1, 2, 3]:
                errors.append(f"Seed {seed}, actor {actor_id} lacks all four seats: {seats}.")
        seed_details[str(seed)] = {
            "run_count": len(seed_rows),
            "permutations": sorted(permutations),
            "actor_seats": {key: sorted(value) for key, value in sorted(actor_seats.items())},
        }
    if len(by_seed) not in {2, 3}:
        errors.append(f"Expected 2–3 seed blocks, found {len(by_seed)}.")
    return {"complete": not errors, "seed_count": len(by_seed), "seeds": seed_details, "errors": errors}


def _check(
    requirement_id: str,
    title: str,
    *,
    complete: bool,
    evidence: list[dict[str, Any]],
    blockers: list[str],
    complete_note: str | None = None,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "title": title,
        "status": "complete" if complete else "incomplete",
        "complete": complete,
        "evidence": evidence,
        "blockers": blockers,
        "conclusion": complete_note if complete else None,
    }


def _pending_check(
    requirement_id: str,
    title: str,
    *,
    status: str,
    evidence: list[dict[str, Any]],
    blockers: list[str],
    complete_note: str | None = None,
) -> dict[str, Any]:
    complete = status == "complete"
    return {
        "requirement_id": requirement_id,
        "title": title,
        "status": status,
        "complete": complete,
        "evidence": evidence,
        "blockers": blockers,
        "conclusion": complete_note if complete else None,
    }


def _file_evidence(repo_root: Path, path: Path) -> dict[str, Any]:
    return {
        "path": _relative(repo_root, path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": _sha256_file(path) if path.exists() and path.is_file() else None,
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _markdown(payload: dict[str, Any]) -> str:
    status_icons = {
        "complete": "PASS",
        "blocked_external": "BLOCKED",
        "pending_empirical": "PENDING",
        "pending_preregistration": "PENDING",
        "incomplete": "FAIL",
    }
    lines = [
        "# Research Protocol Readiness Audit",
        "",
        "This audit distinguishes implemented preparation from completed empirical evidence.",
        "It makes no provider calls and does not authorize manuscript drafting.",
        "",
        "| Requirement | Status | Blocking condition |",
        "|---|---|---|",
    ]
    for check in _list(payload.get("requirements")):
        item = _dict(check)
        blockers = "; ".join(str(value) for value in _list(item.get("blockers"))) or "—"
        lines.append(
            f"| {item.get('title')} | {status_icons.get(str(item.get('status')), item.get('status'))} "
            f"| {blockers} |"
        )
    lines.extend(
        [
            "",
            f"Overall goal complete: **{payload.get('goal_complete')}**.",
            "",
            "The confirmatory campaign remains downstream of empirical pilot completion,",
            "design lock, and preregistration freeze. Human verification separately gates",
            "publication-facing social claims.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
