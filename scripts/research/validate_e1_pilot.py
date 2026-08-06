from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CAMPAIGN_ID = "monopoly-long-v1-e1-pilot-random-v1"
DEFAULT_PLAN_DIR = (
    "analysis/research_protocol/pilot/planning_runs/campaigns/"
    "monopoly-long-v1-e1-pilot-random-v1"
)
DEFAULT_CAMPAIGN_DIR = "runs/campaigns/monopoly-long-v1-e1-pilot-random-v1"
DEFAULT_OUTPUT = "analysis/research_protocol/pilot/e1_validation.json"
COMPLETE_STATUSES = {"completed", "resumed_completed"}
ALLOWED_STATUSES = COMPLETE_STATUSES | {
    "failed",
    "not_runnable",
    "not_started_after_failure",
    "not_started_budget_stop",
    "not_started_credit_gate",
    "not_started_max_runs_limit",
    "not_started_preflight_gate",
}
CORE_RUN_FILES = (
    "actions.jsonl",
    "artifact_manifest.json",
    "artifact_replay_report.json",
    "cost_report.json",
    "decisions.jsonl",
    "events.jsonl",
    "failure_summary.json",
    "players.json",
    "replay_report.json",
    "run_config.json",
    "scorecard.json",
    "scorecard_players.json",
    "seat_assignment.json",
    "state_replay_report.json",
    "summary.json",
    "trace_summary.json",
    "usage.json",
)
CORE_RUN_DIRECTORIES = ("prompts", "state")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate E1 planning and, when present, every executed pilot cell."
    )
    parser.add_argument("--plan-dir", default=DEFAULT_PLAN_DIR)
    parser.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return a failing exit code unless all eight E1 cells pass the empirical gate.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    plan_dir = (repo_root / args.plan_dir).resolve()
    campaign_dir = (repo_root / args.campaign_dir).resolve()
    output_path = (repo_root / args.output).resolve()

    plan_report = _validate_plan(repo_root, plan_dir)
    execution_report = _validate_execution(repo_root, campaign_dir, plan_report)
    complete = plan_report["passed"] and execution_report["empirical_gate_passed"]
    payload = {
        "schema_version": "e1_pilot_validation_v1",
        "generated_at_utc": _utc_now(),
        "campaign_id": CAMPAIGN_ID,
        "source_commit": _git_head(repo_root),
        "status": "complete" if complete else execution_report["status"],
        "empirical_gate_passed": complete,
        "provider_calls": 0,
        "plan_validation": plan_report,
        "execution_validation": execution_report,
        "prompt_pipeline": {
            "status": "unchanged",
            "note": (
                "Validation reads campaign and run artifacts only. It does not build or "
                "submit any model-facing request."
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
    output_path.with_suffix(".md").write_text(_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "empirical_gate_passed": complete,
                "output": _relative(repo_root, output_path),
                "provider_calls": 0,
                "status": payload["status"],
            },
            sort_keys=True,
        )
    )
    if args.require_complete and not complete:
        return 2
    return 0


def _validate_plan(repo_root: Path, plan_dir: Path) -> dict[str, Any]:
    required = (
        "artifact_manifest.json",
        "campaign_config.json",
        "campaign_manifest.json",
        "execution_manifest.json",
        "execution_manifest.jsonl",
        "model_roster.json",
        "run_matrix.json",
        "run_matrix.jsonl",
        "seed_manifest.json",
    )
    missing_files = [name for name in required if not (plan_dir / name).is_file()]
    matrix = _read_json(plan_dir / "run_matrix.json")
    execution = _read_json(plan_dir / "execution_manifest.json")
    campaign = _read_json(plan_dir / "campaign_manifest.json")
    rows = [_dict(row) for row in _list(matrix.get("runs"))]
    errors: list[str] = []
    if missing_files:
        errors.append(f"Missing planning artifacts: {missing_files}.")
    if len(rows) != 8:
        errors.append(f"Expected 8 planned cells, found {len(rows)}.")
    run_ids = [str(row.get("run_id")) for row in rows]
    if len(set(run_ids)) != len(run_ids):
        errors.append("Planned run IDs are not unique.")
    ranks = sorted(_integer(row.get("execution_rank"), default=-1) for row in rows)
    if ranks != list(range(len(rows))):
        errors.append(f"Execution ranks are not contiguous: {ranks}.")
    ordered = [_dict(row) for row in _list(execution.get("ordered_runs"))]
    ordered_ids = [str(row.get("run_id")) for row in ordered]
    expected_ordered_ids = [
        str(row.get("run_id"))
        for row in sorted(rows, key=lambda row: _integer(row.get("execution_rank"), default=-1))
    ]
    if ordered_ids != expected_ordered_ids:
        errors.append("Execution manifest order does not match run-matrix ranks.")
    if execution.get("sequential_execution") is not True:
        errors.append("Execution manifest is not explicitly sequential.")
    if campaign.get("concurrency_effective") != 1:
        errors.append("Effective concurrency is not one.")

    coverage = _seat_coverage(rows)
    errors.extend(coverage["errors"])
    route_errors = _provider_route_errors(rows)
    errors.extend(route_errors)
    source_hashes = {
        name: _sha256_file(plan_dir / name)
        for name in required
        if (plan_dir / name).is_file()
    }
    return {
        "passed": not errors,
        "plan_dir": _relative(repo_root, plan_dir),
        "planned_cell_count": len(rows),
        "planned_run_ids": run_ids,
        "source_hashes": source_hashes,
        "seat_coverage": coverage,
        "route_errors": route_errors,
        "errors": errors,
    }


def _validate_execution(
    repo_root: Path,
    campaign_dir: Path,
    plan_report: dict[str, Any],
) -> dict[str, Any]:
    results_path = campaign_dir / "run_results.json"
    if not results_path.is_file():
        return {
            "status": "planned_not_executed",
            "empirical_gate_passed": False,
            "campaign_dir": _relative(repo_root, campaign_dir),
            "results_present": False,
            "planned_cell_count": plan_report["planned_cell_count"],
            "recorded_cell_count": 0,
            "completed_cell_count": 0,
            "blockers": [
                "Executed campaign run_results.json is absent.",
                "No E1 empirical nuisance estimates may be produced.",
            ],
            "cell_reports": [],
        }

    results_payload = _read_json(results_path)
    results = [_dict(row) for row in _list(results_payload.get("runs"))]
    planned_ids = [str(value) for value in _list(plan_report.get("planned_run_ids"))]
    result_ids = [str(row.get("run_id")) for row in results]
    duplicate_ids = sorted(run_id for run_id, count in Counter(result_ids).items() if count > 1)
    unknown_ids = sorted(set(result_ids) - set(planned_ids))
    missing_ids = sorted(set(planned_ids) - set(result_ids))
    invalid_statuses = sorted(
        {
            str(row.get("status"))
            for row in results
            if str(row.get("status")) not in ALLOWED_STATUSES
        }
    )
    errors: list[str] = []
    if duplicate_ids:
        errors.append(f"Duplicate run-result IDs: {duplicate_ids}.")
    if unknown_ids:
        errors.append(f"Unplanned run-result IDs: {unknown_ids}.")
    if missing_ids:
        errors.append(f"Planned cells missing from result ledger: {missing_ids}.")
    if invalid_statuses:
        errors.append(f"Invalid result statuses: {invalid_statuses}.")

    cell_reports = [_validate_cell(repo_root, row) for row in results]
    complete_cells = [report for report in cell_reports if report["status"] in COMPLETE_STATUSES]
    failed_integrity = [report["run_id"] for report in complete_cells if not report["passed"]]
    if failed_integrity:
        errors.append(f"Completed cells failing artifact/integrity validation: {failed_integrity}.")
    if len(complete_cells) != 8:
        errors.append(f"Expected 8 completed cells for E1 estimation, found {len(complete_cells)}.")

    recorded_all = not duplicate_ids and not unknown_ids and not missing_ids and not invalid_statuses
    empirical_gate = (
        plan_report["passed"]
        and recorded_all
        and len(complete_cells) == 8
        and not failed_integrity
    )
    return {
        "status": "complete" if empirical_gate else "executed_incomplete_or_invalid",
        "empirical_gate_passed": empirical_gate,
        "campaign_dir": _relative(repo_root, campaign_dir),
        "results_present": True,
        "run_results_sha256": _sha256_file(results_path),
        "planned_cell_count": len(planned_ids),
        "recorded_cell_count": len(results),
        "completed_cell_count": len(complete_cells),
        "status_counts": dict(sorted(Counter(str(row.get("status")) for row in results).items())),
        "duplicate_run_ids": duplicate_ids,
        "unknown_run_ids": unknown_ids,
        "missing_run_ids": missing_ids,
        "errors": errors,
        "cell_reports": cell_reports,
    }


def _validate_cell(repo_root: Path, row: dict[str, Any]) -> dict[str, Any]:
    run_id = str(row.get("run_id"))
    status = str(row.get("status"))
    run_dir = _resolve_run_dir(repo_root, row.get("run_dir"), run_id)
    report: dict[str, Any] = {
        "run_id": run_id,
        "status": status,
        "run_dir": _relative(repo_root, run_dir),
        "passed": status not in COMPLETE_STATUSES,
        "errors": [],
    }
    if status not in COMPLETE_STATUSES:
        report["note"] = "Non-completed cell is preserved for reliability analysis."
        return report

    missing_files = [name for name in CORE_RUN_FILES if not (run_dir / name).is_file()]
    missing_directories = [
        name for name in CORE_RUN_DIRECTORIES if not (run_dir / name).is_dir()
    ]
    if missing_files:
        report["errors"].append(f"Missing files: {missing_files}.")
    if missing_directories:
        report["errors"].append(f"Missing directories: {missing_directories}.")

    decision_ids = _jsonl_ids(
        run_dir / "decisions.jsonl",
        id_field="decision_id",
        predicate=lambda value: value.get("phase") == "decision_started",
    )
    action_ids = _jsonl_ids(run_dir / "actions.jsonl", id_field="decision_id")
    missing_actions = sorted(set(decision_ids) - set(action_ids))
    extra_actions = sorted(set(action_ids) - set(decision_ids))
    duplicate_decisions = sorted(
        decision_id for decision_id, count in Counter(decision_ids).items() if count > 1
    )
    duplicate_actions = sorted(
        decision_id for decision_id, count in Counter(action_ids).items() if count > 1
    )
    if missing_actions or extra_actions or duplicate_decisions or duplicate_actions:
        report["errors"].append("Decision/action bijection failed.")

    state_replay = _read_json(run_dir / "state_replay_report.json")
    artifact_replay = _read_json(run_dir / "artifact_replay_report.json")
    replay = _read_json(run_dir / "replay_report.json")
    if state_replay.get("status") != "passed":
        report["errors"].append(
            f"State replay status is {state_replay.get('status')!r}, expected 'passed'."
        )
    if artifact_replay.get("status") != "passed":
        report["errors"].append(
            f"Artifact replay status is {artifact_replay.get('status')!r}, expected 'passed'."
        )
    if replay.get("state_status") != "passed" or replay.get("artifact_status") != "passed":
        report["errors"].append("Aggregate replay report does not record both layers as passed.")

    manifest = _read_json(run_dir / "artifact_manifest.json")
    manifest_status = manifest.get("status")
    if manifest_status not in {None, "complete", "passed"}:
        report["errors"].append(f"Artifact manifest status is unexpected: {manifest_status!r}.")

    report.update(
        {
            "artifact_counts": {
                "events": _jsonl_count(run_dir / "events.jsonl"),
                "decisions_started": len(decision_ids),
                "actions": len(action_ids),
                "prompts": _file_count(run_dir / "prompts"),
                "state_snapshots": _file_count(run_dir / "state"),
            },
            "decision_action_bijection": {
                "passed": not (
                    missing_actions or extra_actions or duplicate_decisions or duplicate_actions
                ),
                "missing_actions": missing_actions,
                "extra_actions": extra_actions,
                "duplicate_decisions": duplicate_decisions,
                "duplicate_actions": duplicate_actions,
            },
            "replay": {
                "state_status": state_replay.get("status"),
                "artifact_status": artifact_replay.get("status"),
                "aggregate_status": replay.get("status"),
            },
            "source_hashes": {
                name: _sha256_file(run_dir / name)
                for name in CORE_RUN_FILES
                if (run_dir / name).is_file()
            },
        }
    )
    report["passed"] = not report["errors"]
    return report


def _seat_coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_seed[_integer(row.get("seed"), default=-1)].append(row)
    details: dict[str, Any] = {}
    for seed, seed_rows in sorted(by_seed.items()):
        actor_seats: dict[str, list[int]] = defaultdict(list)
        permutations: list[str] = []
        for row in seed_rows:
            permutations.append(str(row.get("permutation_id")))
            for actor in _list(row.get("actors")):
                actor_payload = _dict(actor)
                actor_seats[str(actor_payload.get("actor_id"))].append(
                    _integer(actor_payload.get("seat_index"), default=-1)
                )
        if sorted(permutations) != [f"latin_square:{index}" for index in range(4)]:
            errors.append(f"Seed {seed} lacks the four cyclic permutations.")
        for actor_id, seats in sorted(actor_seats.items()):
            if sorted(seats) != [0, 1, 2, 3]:
                errors.append(f"Seed {seed}, actor {actor_id} seat coverage is {sorted(seats)}.")
        details[str(seed)] = {
            "run_count": len(seed_rows),
            "permutations": sorted(permutations),
            "actor_seats": {
                actor_id: sorted(seats) for actor_id, seats in sorted(actor_seats.items())
            },
        }
    if len(by_seed) not in {2, 3}:
        errors.append(f"Expected 2–3 seed blocks, found {len(by_seed)}.")
    return {"passed": not errors, "seed_count": len(by_seed), "seeds": details, "errors": errors}


def _provider_route_errors(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for row in rows:
        run_id = str(row.get("run_id"))
        for actor in _list(row.get("actors")):
            payload = _dict(actor)
            provider = _dict(payload.get("provider"))
            only = _list(provider.get("only"))
            if provider.get("allow_fallbacks") is not False or len(only) != 1:
                errors.append(
                    f"{run_id}/{payload.get('actor_id')} does not have one exact route with "
                    "fallbacks disabled."
                )
            if payload.get("top_p") is not None:
                errors.append(f"{run_id}/{payload.get('actor_id')} unexpectedly sets top_p.")
    return errors


def _resolve_run_dir(repo_root: Path, value: Any, run_id: str) -> Path:
    runs_root = (repo_root / "runs").resolve()
    candidate = Path(str(value)) if value else runs_root / run_id
    if not candidate.is_absolute():
        candidate = (repo_root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(runs_root)
    except ValueError as exc:
        raise ValueError(f"Run directory escapes the runs root: {candidate}") from exc
    return candidate


def _jsonl_ids(
    path: Path,
    *,
    id_field: str,
    predicate: Any | None = None,
) -> list[str]:
    if not path.is_file():
        return []
    ids: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object.")
            if predicate is not None and not predicate(value):
                continue
            identifier = value.get(id_field)
            if not isinstance(identifier, str) or not identifier:
                raise ValueError(f"{path}:{line_number} is missing {id_field}.")
            ids.append(identifier)
    return ids


def _jsonl_count(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _file_count(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _integer(value: Any, *, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    return default


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
    plan = _dict(payload.get("plan_validation"))
    execution = _dict(payload.get("execution_validation"))
    lines = [
        "# E1 Pilot Validation",
        "",
        f"- Status: **{payload.get('status')}**",
        f"- Empirical gate passed: **{payload.get('empirical_gate_passed')}**",
        f"- Planning validation passed: **{plan.get('passed')}**",
        f"- Planned cells: {plan.get('planned_cell_count')}",
        f"- Recorded cells: {execution.get('recorded_cell_count')}",
        f"- Completed cells: {execution.get('completed_cell_count')}",
        "- Provider calls made by this validator: 0",
        "",
    ]
    errors = [str(value) for value in _list(execution.get("errors"))]
    blockers = [str(value) for value in _list(execution.get("blockers"))]
    combined = blockers + errors
    if combined:
        lines.extend(["## Current blockers", ""])
        lines.extend(f"- {value}" for value in combined)
        lines.append("")
    lines.extend(
        [
            "This file validates evidence; it does not treat a planned cell as an observed game.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
