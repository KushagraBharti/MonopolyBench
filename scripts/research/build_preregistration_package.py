from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_ROOT = "analysis/research_protocol/preregistration"
FROZEN_RELATIVE = "frozen"
PROTOCOL_INPUTS = {
    "protocol/scientific_protocol_v2.md": "docs/research_protocol/scientific_protocol_v2.md",
    "protocol/downstream_bridge_contracts.md": "docs/research_protocol/downstream_bridge_contracts.md",
    "protocol/campaign_control_audit.md": "docs/research_protocol/campaign_control_audit.md",
    "protocol/social_evidence_codebook.md": "docs/research_protocol/social_evidence_codebook.md",
    "protocol/llm_judge_social_evidence_protocol.md": (
        "docs/research_protocol/llm_judge_social_evidence_protocol.md"
    ),
    "protocol/preregistration_freeze_contract.md": (
        "docs/research_protocol/preregistration_freeze_contract.md"
    ),
}
PILOT_INPUTS = {
    "pilot/e1_validation.json": "analysis/research_protocol/pilot/e1_validation.json",
    "pilot/e1_analysis_matrix_manifest.json": (
        "analysis/research_protocol/pilot/e1_analysis_matrix/manifest.json"
    ),
    "pilot/power_simulation.json": "analysis/research_protocol/pilot/power_simulation.json",
    "pilot/design_lock.json": "analysis/research_protocol/pilot/design_lock.json",
    "pilot/budget_projection.json": "analysis/research_protocol/pilot/budget_projection.json",
    "pilot/communication_packet_manifest.json": (
        "analysis/research_protocol/pilot/communication_calibration_e0/"
        "packet_manifest.json"
    ),
    "pilot/trajectory_fixture_repetition_manifest.json": (
        "analysis/research_protocol/pilot/trajectory_fixture_repetitions_e1/manifest.json"
    ),
}
CAMPAIGN_INPUTS = {
    "campaign/primary_seed_draw.json": (
        "analysis/research_protocol/preregistration/inputs/primary_seed_draw.json"
    ),
    "campaign/campaign_config.json": (
        "analysis/research_protocol/preregistration/inputs/ecological_campaign/campaign_config.json"
    ),
    "campaign/run_matrix.json": (
        "analysis/research_protocol/preregistration/inputs/ecological_campaign/run_matrix.json"
    ),
    "campaign/execution_manifest.json": (
        "analysis/research_protocol/preregistration/inputs/ecological_campaign/execution_manifest.json"
    ),
    "campaign/model_roster.json": "contracts/research/monopoly_long_v1_model_rosters.json",
    "campaign/endpoint_window.json": (
        "analysis/research_protocol/preregistration/inputs/endpoint_window.json"
    ),
    "campaign/endpoint_preflight.json": (
        "analysis/research_protocol/preregistration/inputs/endpoint_preflight.json"
    ),
}
ANALYSIS_INPUTS = {
    "analysis/comparison_families.json": (
        "analysis/research_protocol/preregistration/draft/comparison_families.json"
    ),
    "analysis/analysis_plan.json": (
        "analysis/research_protocol/preregistration/draft/analysis_plan.json"
    ),
    "analysis/social_judge_rubric.json": (
        "analysis/research_protocol/preregistration/draft/social_judge_rubric.json"
    ),
}
REQUIRED_INPUTS = {
    **PROTOCOL_INPUTS,
    **PILOT_INPUTS,
    **CAMPAIGN_INPUTS,
    **ANALYSIS_INPUTS,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate or freeze the confirmatory preregistration package."
    )
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--freeze",
        action="store_true",
        help="Create the immutable frozen tree after every gate passes.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    output_root = (repo_root / args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    readiness = _readiness(repo_root)
    readiness_path = output_root / "readiness.json"
    _write_json(readiness_path, readiness)
    readiness_path.with_suffix(".md").write_text(_readiness_markdown(readiness), encoding="utf-8")

    if not args.freeze:
        print(
            json.dumps(
                {
                    "freeze_ready": readiness["freeze_ready"],
                    "output": _relative(repo_root, readiness_path),
                    "provider_calls": 0,
                    "status": readiness["status"],
                },
                sort_keys=True,
            )
        )
        return 0

    if readiness["freeze_ready"] is not True:
        raise ValueError("Preregistration freeze refused: readiness gates are incomplete.")
    if not _git_worktree_clean(repo_root):
        raise ValueError("Preregistration freeze requires a clean Git worktree.")
    untracked_inputs = [
        source
        for source in REQUIRED_INPUTS.values()
        if not _git_path_tracked(repo_root, source)
    ]
    if untracked_inputs:
        raise ValueError(f"Preregistration inputs are not tracked: {untracked_inputs}.")

    frozen_dir = output_root / FROZEN_RELATIVE
    if frozen_dir.exists():
        raise FileExistsError(
            f"{frozen_dir} already exists; frozen packages are never overwritten."
        )
    source_commit = _git_head(repo_root)
    if not source_commit:
        raise ValueError("Unable to resolve the source Git commit.")

    source_hashes: list[dict[str, Any]] = []
    for destination_relative, source_relative in sorted(REQUIRED_INPUTS.items()):
        source = repo_root / source_relative
        destination = frozen_dir / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        source_digest = _sha256_file(source)
        destination_digest = _sha256_file(destination)
        if source_digest != destination_digest:
            raise ValueError(f"Copy verification failed for {source_relative}.")
        source_hashes.append(
            {
                "source_path": source_relative,
                "frozen_path": destination_relative,
                "bytes": source.stat().st_size,
                "sha256": source_digest,
            }
        )

    provenance_dir = frozen_dir / "provenance"
    provenance_dir.mkdir(parents=True, exist_ok=True)
    source_hash_path = provenance_dir / "source_hashes.json"
    _write_json(
        source_hash_path,
        {
            "schema_version": "preregistration_source_hashes_v1",
            "source_commit": source_commit,
            "files": source_hashes,
        },
    )
    tree_hash = _tree_hash(frozen_dir)
    tree_hash_path = provenance_dir / "tree_hash.json"
    _write_json(
        tree_hash_path,
        {
            "schema_version": "preregistration_tree_hash_v1",
            "algorithm": "sha256(relative_path_utf8 + NUL + file_sha256_ascii + LF)",
            "source_commit": source_commit,
            "tree_sha256_before_manifest": tree_hash,
        },
    )
    design_lock = _read_json(repo_root / PILOT_INPUTS["pilot/design_lock.json"])
    manifest = {
        "schema_version": "monopolybench_preregistration_manifest_v1",
        "status": "frozen",
        "frozen_at_utc": _utc_now(),
        "source_commit": source_commit,
        "source_commit_boundary": (
            "All copied inputs and analysis code were committed and the worktree was clean "
            "before this frozen tree was created."
        ),
        "primary_seed_blocks": design_lock.get("selected_primary_seed_blocks"),
        "primary_games": design_lock.get("selected_primary_games"),
        "approved_maximum_campaign_cost": design_lock.get(
            "approved_maximum_campaign_cost"
        ),
        "input_file_count": len(source_hashes),
        "source_hashes": "provenance/source_hashes.json",
        "source_hashes_sha256": _sha256_file(source_hash_path),
        "tree_hash": "provenance/tree_hash.json",
        "tree_hash_sha256": _sha256_file(tree_hash_path),
        "tree_sha256_before_manifest": tree_hash,
        "amendment_policy": (
            "This directory is immutable. Any change creates a separately versioned "
            "amendment and retains this package."
        ),
        "checksum_semantics": (
            "The detached SHA-256 file seals canonical manifest bytes; it is not described "
            "as a personal digital signature."
        ),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "The preregistration package is downstream and makes no provider call.",
        },
        "provider_calls": 0,
    }
    manifest_path = frozen_dir / "preregistration_manifest.json"
    _write_json(manifest_path, manifest)
    digest = _sha256_file(manifest_path)
    (frozen_dir / "preregistration_manifest.sha256").write_text(
        f"{digest}  preregistration_manifest.json\n",
        encoding="ascii",
    )
    print(
        json.dumps(
            {
                "frozen_dir": _relative(repo_root, frozen_dir),
                "manifest_sha256": digest,
                "provider_calls": 0,
                "source_commit": source_commit,
                "status": "frozen",
            },
            sort_keys=True,
        )
    )
    return 0


def _readiness(repo_root: Path) -> dict[str, Any]:
    evidence = {
        destination: _file_status(repo_root, repo_root / source)
        for destination, source in sorted(REQUIRED_INPUTS.items())
    }
    blockers = [
        f"Missing required input: {value['source_path']}"
        for value in evidence.values()
        if not value["exists"]
    ]

    validation = _read_json(repo_root / PILOT_INPUTS["pilot/e1_validation.json"])
    if validation.get("empirical_gate_passed") is not True:
        blockers.append("E1 empirical validation has not passed.")

    matrix = _read_json(
        repo_root / PILOT_INPUTS["pilot/e1_analysis_matrix_manifest.json"]
    )
    if matrix.get("status") != "complete":
        blockers.append("The blinded E1 analysis matrix is incomplete.")

    power = _read_json(repo_root / PILOT_INPUTS["pilot/power_simulation.json"])
    if power.get("status") != "design_selected" or power.get("selected_seed_blocks") is None:
        blockers.append("Power simulation has not selected a budget-approved design.")

    design_lock = _read_json(repo_root / PILOT_INPUTS["pilot/design_lock.json"])
    if design_lock.get("status") != "locked_for_preregistration_build":
        blockers.append("The pilot design lock is absent or not final.")

    communication = _read_json(
        repo_root / PILOT_INPUTS["pilot/communication_packet_manifest.json"]
    )
    communication_judge = _dict(communication.get("judge_execution"))
    if (
        not 20 <= _integer(communication.get("packet_count")) <= 30
        or communication.get("model_identity_masked") is not True
        or communication.get("winner_and_rank_excluded") is not True
        or communication.get("campaign_execution_blocker") is not False
        or communication_judge.get("external_model_api_calls") is not False
        or communication_judge.get("openrouter_calls") is not False
    ):
        blockers.append(
            "The communication instrument-development packet is incomplete or not masked."
        )

    social_rubric = _read_json(
        repo_root / ANALYSIS_INPUTS["analysis/social_judge_rubric.json"]
    )
    social_coverage = _dict(social_rubric.get("coverage"))
    social_execution = _dict(social_rubric.get("execution_environment"))
    social_publication = _dict(social_rubric.get("publication_rules"))
    if (
        social_coverage.get("focal_turn_coverage_required") != 1.0
        or social_coverage.get("lexical_prefilter_may_exclude_turns") is not False
        or social_coverage.get("explicit_negative_required_per_candidate_free_window")
        is not True
        or social_publication.get("campaign_blocked_by_human_review") is not False
        or social_execution.get("mode") != "local_agentic_research_tool"
        or social_execution.get("external_model_api_calls") is not False
        or social_execution.get("openrouter_calls") is not False
    ):
        blockers.append(
            "The social-judge rubric does not enforce exhaustive coverage, explicit "
            "negatives, local agentic-tool execution without model APIs, and nonblocking "
            "downstream human validation."
        )

    fixtures = _read_json(
        repo_root / PILOT_INPUTS["pilot/trajectory_fixture_repetition_manifest.json"]
    )
    fixture_count = _integer(fixtures.get("fixture_count"))
    planned_calls = _integer(fixtures.get("planned_call_count"))
    recorded_calls = _integer(fixtures.get("recorded_call_count"))
    if not (
        fixtures.get("status") == "complete"
        and 20 <= fixture_count <= 30
        and planned_calls > 0
        and recorded_calls == planned_calls
    ):
        blockers.append("E1-derived 20–30 fixture repetition coverage is incomplete.")

    selected_blocks = _integer(design_lock.get("selected_primary_seed_blocks"))
    seed_draw = _read_json(
        repo_root / CAMPAIGN_INPUTS["campaign/primary_seed_draw.json"]
    )
    if selected_blocks < 1 or _integer(seed_draw.get("count")) != selected_blocks:
        blockers.append("Confirmatory seed draw does not match the selected block count.")
    if seed_draw and seed_draw.get("outcome_information_used") is not False:
        blockers.append("Confirmatory seed draw is not explicitly outcome-blind.")

    execution = _read_json(
        repo_root / CAMPAIGN_INPUTS["campaign/execution_manifest.json"]
    )
    ordered_runs = _list(execution.get("ordered_runs"))
    if not (
        execution.get("sequential_execution") is True
        and selected_blocks > 0
        and len(ordered_runs) == selected_blocks * 4
    ):
        blockers.append("Confirmatory execution manifest is absent or structurally incomplete.")

    campaign_config = _read_json(
        repo_root / CAMPAIGN_INPUTS["campaign/campaign_config.json"]
    )
    if campaign_config and campaign_config.get("dry_run") is not False:
        blockers.append("Confirmatory campaign config is not execution-enabled.")

    endpoint_window = _read_json(
        repo_root / CAMPAIGN_INPUTS["campaign/endpoint_window.json"]
    )
    if not _valid_endpoint_window(endpoint_window):
        blockers.append("Endpoint execution window is absent, invalid, or not frozen.")

    endpoint_preflight = _read_json(
        repo_root / CAMPAIGN_INPUTS["campaign/endpoint_preflight.json"]
    )
    if endpoint_preflight and _dict(endpoint_preflight.get("verdict")).get(
        "all_routes_ready"
    ) is not True:
        blockers.append("Frozen endpoint preflight does not show all exact routes ready.")

    comparison = _read_json(
        repo_root / ANALYSIS_INPUTS["analysis/comparison_families.json"]
    )
    if comparison.get("status") != "frozen":
        blockers.append("Comparison families remain draft.")
    analysis_plan = _read_json(
        repo_root / ANALYSIS_INPUTS["analysis/analysis_plan.json"]
    )
    if analysis_plan.get("status") != "frozen":
        blockers.append("Analysis plan remains draft.")

    return {
        "schema_version": "preregistration_readiness_v1",
        "generated_at_utc": _utc_now(),
        "status": "ready_to_freeze" if not blockers else "not_ready",
        "freeze_ready": not blockers,
        "source_commit": _git_head(repo_root),
        "provider_calls": 0,
        "required_input_count": len(REQUIRED_INPUTS),
        "inputs": evidence,
        "blockers": blockers,
        "worktree_clean": _git_worktree_clean(repo_root),
        "note": (
            "A dirty worktree does not block readiness inspection, but it blocks the "
            "actual --freeze operation."
        ),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Readiness inspection is downstream and makes no provider call.",
        },
        "provenance": {
            "script": _relative(repo_root, Path(__file__).resolve()),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
    }


def _file_status(repo_root: Path, path: Path) -> dict[str, Any]:
    return {
        "source_path": _relative(repo_root, path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
        "sha256": _sha256_file(path) if path.is_file() else None,
    }


def _valid_endpoint_window(payload: dict[str, Any]) -> bool:
    if payload.get("status") != "frozen":
        return False
    start = payload.get("earliest_start_utc")
    finish = payload.get("latest_finish_utc")
    if not isinstance(start, str) or not isinstance(finish, str):
        return False
    try:
        start_value = datetime.fromisoformat(start.replace("Z", "+00:00"))
        finish_value = datetime.fromisoformat(finish.replace("Z", "+00:00"))
    except ValueError:
        return False
    return start_value < finish_value


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = str(path.relative_to(root)).replace("\\", "/")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _git_worktree_clean(repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.returncode == 0 and not result.stdout.strip()


def _git_path_tracked(repo_root: Path, relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative_path],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.returncode == 0


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _readiness_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Preregistration Freeze Readiness",
        "",
        f"- Status: **{payload.get('status')}**",
        f"- Freeze ready: **{payload.get('freeze_ready')}**",
        f"- Required inputs: {payload.get('required_input_count')}",
        f"- Worktree clean: {payload.get('worktree_clean')}",
        "- Provider calls: 0",
        "",
    ]
    blockers = [str(value) for value in _list(payload.get("blockers"))]
    if blockers:
        lines.extend(["## Blocking gates", ""])
        lines.extend(f"- {value}" for value in blockers)
        lines.append("")
    lines.extend(
        [
            "The freeze operation additionally requires every source input to be tracked",
            "and the worktree to be clean. Existing frozen packages are never overwritten.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
