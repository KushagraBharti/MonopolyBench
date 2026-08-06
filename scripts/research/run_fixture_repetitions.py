from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
for package in ("engine", "arena", "telemetry"):
    package_src = REPO_ROOT / "python" / "packages" / package / "src"
    if str(package_src) not in sys.path:
        sys.path.insert(0, str(package_src))

from monopoly_arena.decision_resolver import SharedDecisionResolver  # noqa: E402
from monopoly_arena.openrouter_client import OpenRouterClient  # noqa: E402
from monopoly_arena.player_config import build_single_player_config  # noqa: E402
from monopoly_arena.prompting import (  # noqa: E402
    build_compact_decision,
    build_openrouter_tools,
    build_prompt_bundle,
    build_space_key_by_index,
)
from monopoly_telemetry import build_run_files, write_usage_artifacts  # noqa: E402


DEFAULT_PLAN = "analysis/research_protocol/architecture_proof/repetition_plan_v2"
DEFAULT_OUTPUT = "analysis/research_protocol/pilot/fixture_repetition_execution_e0_v2"
DEFAULT_PREFLIGHT = "analysis/research_protocol/control_audit/openrouter_preflight.json"
TERMINAL_STATUSES = {
    "succeeded_valid_first",
    "succeeded_after_retry",
    "fallback",
    "provider_error",
}


class FrozenPromptMemory:
    def __init__(self, snapshot: dict[str, Any]) -> None:
        self._snapshot = copy.deepcopy(snapshot)

    def snapshot_for_player(self, _player_id: str) -> dict[str, Any]:
        return copy.deepcopy(self._snapshot)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or execute an exact-history fixture repetition plan. "
            "Validation is the default and makes no provider calls."
        )
    )
    parser.add_argument("--plan", default=DEFAULT_PLAN)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT)
    parser.add_argument("--preflight", default=DEFAULT_PREFLIGHT)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Make paid provider calls after every execution gate passes.",
    )
    parser.add_argument(
        "--approved-cost-budget",
        type=float,
        help="Required with --execute and must exactly match the frozen plan budget.",
    )
    parser.add_argument(
        "--maximum-preflight-age-hours",
        type=float,
        default=6.0,
    )
    args = parser.parse_args()

    plan_dir = (REPO_ROOT / args.plan).resolve()
    output_dir = (REPO_ROOT / args.output_dir).resolve()
    preflight_path = (REPO_ROOT / args.preflight).resolve()
    plan_manifest = _read_json(plan_dir / "manifest.json")
    calls = _read_jsonl(plan_dir / str(plan_manifest.get("calls_jsonl") or "calls.jsonl"))
    preflight = _read_json(preflight_path)

    precheck = _validate_plan(
        plan_dir=plan_dir,
        plan_manifest=plan_manifest,
        calls=calls,
        preflight_path=preflight_path,
        preflight=preflight,
        maximum_preflight_age_hours=args.maximum_preflight_age_hours,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "execution_precheck.json", precheck)

    if not args.execute:
        print(
            json.dumps(
                {
                    "mode": "validate_only",
                    "planned_call_count": len(calls),
                    "provider_calls": 0,
                    "prompt_integrity_passed": precheck["prompt_integrity"]["passed"],
                    "paid_execution_authorized": precheck["paid_execution"]["authorized"],
                    "blockers": precheck["paid_execution"]["blockers"],
                    "output": str(output_dir / "execution_precheck.json"),
                },
                sort_keys=True,
            )
        )
        return 0 if precheck["prompt_integrity"]["passed"] else 1

    _require_execution_authorization(
        precheck=precheck,
        plan_manifest=plan_manifest,
        approved_cost_budget=args.approved_cost_budget,
    )
    api_key = os.getenv("OPENROUTER_API_KEY") or _read_env_value(
        REPO_ROOT / ".env",
        "OPENROUTER_API_KEY",
    )
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is unavailable; no provider call was made.")

    return asyncio.run(
        _execute_plan(
            plan_dir=plan_dir,
            output_dir=output_dir,
            plan_manifest=plan_manifest,
            calls=calls,
            precheck=precheck,
            api_key=api_key,
        )
    )


def _validate_plan(
    *,
    plan_dir: Path,
    plan_manifest: dict[str, Any],
    calls: list[dict[str, Any]],
    preflight_path: Path,
    preflight: dict[str, Any],
    maximum_preflight_age_hours: float,
) -> dict[str, Any]:
    blockers: list[str] = []
    integrity_errors: list[dict[str, Any]] = []
    calls_path = plan_dir / str(plan_manifest.get("calls_jsonl") or "calls.jsonl")
    expected_calls_hash = plan_manifest.get("calls_jsonl_sha256")
    if expected_calls_hash != _sha256_file(calls_path):
        integrity_errors.append(
            {
                "scope": "plan",
                "reason": "calls_jsonl_sha256_mismatch",
                "expected": expected_calls_hash,
                "observed": _sha256_file(calls_path),
            }
        )
    if len(calls) != int(plan_manifest.get("planned_call_count") or -1):
        integrity_errors.append(
            {
                "scope": "plan",
                "reason": "planned_call_count_mismatch",
                "expected": plan_manifest.get("planned_call_count"),
                "observed": len(calls),
            }
        )
    repetition_ids = [str(call.get("repetition_id") or "") for call in calls]
    if not repetition_ids or len(set(repetition_ids)) != len(repetition_ids):
        integrity_errors.append(
            {
                "scope": "plan",
                "reason": "missing_or_duplicate_repetition_ids",
            }
        )
    ranks = [call.get("execution_rank") for call in calls]
    if ranks != list(range(len(calls))):
        integrity_errors.append(
            {
                "scope": "plan",
                "reason": "execution_ranks_not_contiguous_in_file_order",
            }
        )

    fixture_collection_manifest_path = (
        REPO_ROOT / str(plan_manifest.get("source_fixture_manifest") or "")
    ).resolve()
    expected_fixture_manifest_hash = plan_manifest.get("source_fixture_manifest_sha256")
    if (
        not fixture_collection_manifest_path.exists()
        or _sha256_file(fixture_collection_manifest_path) != expected_fixture_manifest_hash
    ):
        integrity_errors.append(
            {
                "scope": "fixture_collection",
                "reason": "source_fixture_manifest_sha256_mismatch",
                "expected": expected_fixture_manifest_hash,
                "observed": (
                    _sha256_file(fixture_collection_manifest_path)
                    if fixture_collection_manifest_path.exists()
                    else None
                ),
            }
        )
    else:
        fixture_collection = _read_json(fixture_collection_manifest_path)
        fixture_collection_root = fixture_collection_manifest_path.parent
        expected_collection_tree = plan_manifest.get(
            "source_fixture_collection_tree_sha256"
        )
        observed_collection_tree = _tree_hash(
            fixture_collection_root,
            exclude={"manifest.json"},
        )
        if (
            fixture_collection.get("collection_tree_sha256") != expected_collection_tree
            or observed_collection_tree != expected_collection_tree
        ):
            integrity_errors.append(
                {
                    "scope": "fixture_collection",
                    "reason": "source_fixture_collection_tree_sha256_mismatch",
                    "expected": expected_collection_tree,
                    "manifest_value": fixture_collection.get("collection_tree_sha256"),
                    "observed": observed_collection_tree,
                }
            )

    validated_fixture_keys: set[tuple[str, str, str, str, str]] = set()
    prompt_hash_rows: list[dict[str, Any]] = []
    for call in calls:
        fixture_relative = str(call.get("fixture_relative_path") or "")
        key = (
            fixture_relative,
            str(call.get("system_sha256") or ""),
            str(call.get("user_sha256") or ""),
            str(call.get("tools_sha256") or ""),
            _canonical_json(call.get("reasoning")),
        )
        if key in validated_fixture_keys:
            continue
        validated_fixture_keys.add(key)
        try:
            row = _validate_call_prompt(call)
        except Exception as exc:
            integrity_errors.append(
                {
                    "scope": "fixture",
                    "repetition_id": call.get("repetition_id"),
                    "fixture_id": call.get("fixture_id"),
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                }
            )
        else:
            prompt_hash_rows.append(row)

    preflight_age_hours = _age_hours(preflight.get("observed_at_utc"))
    if preflight_age_hours is None:
        blockers.append("preflight_timestamp_missing_or_invalid")
    elif preflight_age_hours > maximum_preflight_age_hours:
        blockers.append(
            f"preflight_age_{preflight_age_hours:.3f}h_exceeds_{maximum_preflight_age_hours:.3f}h"
        )
    verdict = _dict(preflight.get("verdict"))
    if not verdict.get("all_routes_ready"):
        blockers.append("one_or_more_provider_routes_not_ready")
    if not verdict.get("paid_pilot_authorized_by_preflight"):
        blockers.append("paid_pilot_not_authorized_by_preflight")
    if preflight.get("roster_id") != plan_manifest.get("roster_id"):
        blockers.append("preflight_roster_does_not_match_plan")

    checks_by_model = {
        str(check.get("model_id")): check
        for check in _list(preflight.get("model_checks"))
        if isinstance(check, dict)
    }
    for call in calls:
        model_id = str(call.get("model_id") or "")
        check = _dict(checks_by_model.get(model_id))
        if not check or not check.get("route_ready"):
            blockers.append(f"route_not_ready:{model_id}")
            continue
        if _canonical_json(check.get("provider_route")) != _canonical_json(
            call.get("provider_constraint")
        ):
            blockers.append(f"provider_constraint_mismatch:{model_id}")

    available = _number_or_none(_dict(preflight.get("credits")).get("available_credits"))
    cost_budget = _number_or_none(plan_manifest.get("cost_budget"))
    if available is None:
        blockers.append("available_credit_balance_missing")
    elif cost_budget is None:
        blockers.append("plan_cost_budget_missing")
    elif available < cost_budget:
        blockers.append(
            f"available_credit_{available:.6f}_below_plan_budget_{cost_budget:.6f}"
        )
    if integrity_errors:
        blockers.append("prompt_or_plan_integrity_failed")

    unique_blockers = sorted(set(blockers))
    model_counts = Counter(str(call.get("model_id")) for call in calls)
    fixture_counts = Counter(str(call.get("fixture_id")) for call in calls)
    return {
        "schema_version": "fixture_repetition_execution_precheck_v1",
        "generated_at_utc": _utc_now(),
        "source_commit": _git_head(),
        "mode": "zero_cost_validation",
        "provider_calls": 0,
        "plan": {
            "path": _relative(plan_dir),
            "manifest_sha256": _sha256_file(plan_dir / "manifest.json"),
            "calls_sha256": _sha256_file(calls_path),
            "planned_call_count": len(calls),
            "cost_budget": cost_budget,
            "models": dict(sorted(model_counts.items())),
            "fixtures": dict(sorted(fixture_counts.items())),
        },
        "prompt_integrity": {
            "passed": not integrity_errors,
            "unique_fixture_prompt_variants_checked": len(validated_fixture_keys),
            "validated_prompt_rows": prompt_hash_rows,
            "errors": integrity_errors,
        },
        "preflight": {
            "path": _relative(preflight_path),
            "sha256": _sha256_file(preflight_path),
            "observed_at_utc": preflight.get("observed_at_utc"),
            "age_hours": preflight_age_hours,
            "maximum_age_hours": maximum_preflight_age_hours,
            "available_credits": available,
            "roster_id": preflight.get("roster_id"),
        },
        "paid_execution": {
            "authorized": not unique_blockers,
            "blockers": unique_blockers,
            "requires_execute_flag": True,
            "requires_exact_budget_acknowledgement": True,
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": (
                "Validation reconstructs the source first-attempt prompt and tools in memory. "
                "It does not call a provider or apply an action."
            ),
        },
    }


def _validate_call_prompt(call: dict[str, Any]) -> dict[str, Any]:
    fixture_dir = (REPO_ROOT / str(call["fixture_relative_path"])).resolve()
    fixture = _read_json(fixture_dir / "fixture.json")
    fixture_manifest = _read_json(fixture_dir / "provenance" / "manifest.json")
    if fixture.get("schema_version") != "trajectory_fixture_v2":
        raise ValueError("fixture must use trajectory_fixture_v2 ordered prompt inputs")
    if fixture.get("integrity_status") != "pass_exact_history":
        raise ValueError("fixture did not pass exact-history extraction")
    if fixture_manifest.get("status") != "pass_exact_history":
        raise ValueError("fixture provenance manifest did not pass exact-history extraction")
    _verify_fixture_provenance(fixture_dir, fixture_manifest)

    source_dir = fixture_dir / "source"
    expected = {
        "system_sha256": str(call["system_sha256"]),
        "user_sha256": str(call["user_sha256"]),
        "tools_sha256": str(call["tools_sha256"]),
    }
    observed_source = {
        "system_sha256": _sha256_file(source_dir / "original_system.txt"),
        "user_sha256": _sha256_file(source_dir / "original_user.json"),
        "tools_sha256": _sha256_file(source_dir / "original_tools.json"),
    }
    if observed_source != expected:
        raise ValueError(f"source prompt hashes differ from plan: {observed_source!r}")

    decision = _read_json(source_dir / "decision_ordered.json")
    started = _read_json(source_dir / "decision_started.json")
    memory = _read_json(fixture_dir / "reconstructed" / "prompt_memory_ordered.json")
    system_prompt = _read_text_exact(source_dir / "original_system.txt")
    player_config = build_single_player_config(
        player_id=str(started["player_id"]),
        name=str(started.get("player_name") or started["player_id"]),
        openrouter_model_id=str(call["model_id"]),
        system_prompt=system_prompt,
        reasoning=_dict_or_none(call.get("reasoning")),
        provider=_dict_or_none(call.get("provider_constraint")),
    )
    space_key_by_index = build_space_key_by_index()
    bundle = build_prompt_bundle(
        decision,
        player_config,
        memory=FrozenPromptMemory(memory),
        space_key_by_index=space_key_by_index,
    )
    tools = build_openrouter_tools(build_compact_decision(decision))
    observed_reconstruction = {
        "system_sha256": _sha256_bytes(bundle.system_prompt.encode("utf-8")),
        "user_sha256": _sha256_bytes(bundle.user_content.encode("utf-8")),
        "tools_sha256": _sha256_bytes(_compact_json_bytes(tools)),
    }
    if observed_reconstruction != expected:
        raise ValueError(
            "current prompt reconstruction differs from frozen source: "
            f"{observed_reconstruction!r}"
        )
    return {
        "fixture_id": call.get("fixture_id"),
        "model_id": call.get("model_id"),
        "reasoning": call.get("reasoning"),
        "source_hashes": observed_source,
        "reconstructed_hashes": observed_reconstruction,
        "exact": True,
    }


def _require_execution_authorization(
    *,
    precheck: dict[str, Any],
    plan_manifest: dict[str, Any],
    approved_cost_budget: float | None,
) -> None:
    if not _dict(precheck.get("prompt_integrity")).get("passed"):
        raise SystemExit("Prompt integrity failed; no provider call was made.")
    paid = _dict(precheck.get("paid_execution"))
    if not paid.get("authorized"):
        blockers = ", ".join(str(item) for item in _list(paid.get("blockers")))
        raise SystemExit(f"Paid execution is blocked ({blockers}); no provider call was made.")
    budget = _number_or_none(plan_manifest.get("cost_budget"))
    if approved_cost_budget is None or budget is None:
        raise SystemExit(
            "--execute requires --approved-cost-budget matching the frozen plan; "
            "no provider call was made."
        )
    if abs(approved_cost_budget - budget) > 1e-9:
        raise SystemExit(
            f"Approved budget {approved_cost_budget} does not match plan budget {budget}; "
            "no provider call was made."
        )


async def _execute_plan(
    *,
    plan_dir: Path,
    output_dir: Path,
    plan_manifest: dict[str, Any],
    calls: list[dict[str, Any]],
    precheck: dict[str, Any],
    api_key: str,
) -> int:
    results_path = output_dir / "results.jsonl"
    existing = _last_results(results_path)
    interrupted = [
        repetition_id
        for repetition_id, row in existing.items()
        if row.get("status") == "started"
    ]
    if interrupted:
        raise SystemExit(
            "Interrupted calls require an amended plan with new repetition IDs; refusing "
            f"to overwrite or rerun: {', '.join(sorted(interrupted))}"
        )

    client = OpenRouterClient(api_key=api_key, timeout_s=180.0, max_retries=2)
    started_at = _utc_now()
    credit_before = await _credit_snapshot(client)
    budget = float(plan_manifest["cost_budget"])
    starting_usage = _number_or_none(credit_before.get("total_usage"))
    stop_reason: str | None = None
    try:
        for call in calls:
            repetition_id = str(call["repetition_id"])
            previous = existing.get(repetition_id)
            if previous and previous.get("status") in TERMINAL_STATUSES:
                continue
            credit_now = await _credit_snapshot(client)
            observed_spend = _usage_delta(starting_usage, credit_now.get("total_usage"))
            if observed_spend is None:
                stop_reason = "credit_usage_unavailable_fail_closed"
                break
            if observed_spend >= budget:
                stop_reason = (
                    f"observed_account_usage_delta_{observed_spend:.10f}_meets_or_exceeds_"
                    f"budget_{budget:.10f}"
                )
                break

            started_row = {
                **_call_identity(call),
                "status": "started",
                "started_at_utc": _utc_now(),
                "credit_snapshot_before": credit_now,
            }
            _append_jsonl(results_path, started_row)
            result = await _execute_call(
                call=call,
                output_dir=output_dir,
                plan_manifest=plan_manifest,
                client=client,
            )
            credit_after_call = await _credit_snapshot(client)
            result["credit_snapshot_after"] = credit_after_call
            result["observed_account_usage_delta_from_start"] = _usage_delta(
                starting_usage,
                credit_after_call.get("total_usage"),
            )
            _append_jsonl(results_path, result)
            existing[repetition_id] = result
    finally:
        credit_after = await _credit_snapshot(client)
        await client.aclose()

    latest = _last_results(results_path)
    final_rows: list[dict[str, Any]] = []
    for call in calls:
        repetition_id = str(call["repetition_id"])
        result = latest.get(repetition_id)
        if result and result.get("status") != "started":
            final_rows.append(result)
        else:
            final_rows.append(
                {
                    **_call_identity(call),
                    "status": "not_executed",
                    "reason": stop_reason or "execution_incomplete",
                }
            )
    _write_jsonl(output_dir / "final_ledger.jsonl", final_rows)
    status_counts = Counter(str(row.get("status")) for row in final_rows)
    manifest = {
        "schema_version": "fixture_repetition_execution_manifest_v1",
        "status": "complete" if all(row["status"] in TERMINAL_STATUSES for row in final_rows) else "partial",
        "started_at_utc": started_at,
        "ended_at_utc": _utc_now(),
        "source_commit": _git_head(),
        "plan_path": _relative(plan_dir),
        "plan_manifest_sha256": _sha256_file(plan_dir / "manifest.json"),
        "precheck_sha256": _sha256_file(output_dir / "execution_precheck.json"),
        "planned_call_count": len(calls),
        "status_counts": dict(sorted(status_counts.items())),
        "cost_budget": budget,
        "credit_snapshot_before": credit_before,
        "credit_snapshot_after": credit_after,
        "observed_account_usage_delta": _usage_delta(
            starting_usage,
            credit_after.get("total_usage"),
        ),
        "stop_reason": stop_reason,
        "results_jsonl": "results.jsonl",
        "results_jsonl_sha256": _sha256_file(results_path) if results_path.exists() else None,
        "final_ledger_jsonl": "final_ledger.jsonl",
        "final_ledger_jsonl_sha256": _sha256_file(output_dir / "final_ledger.jsonl"),
        "precheck": {
            "prompt_integrity_passed": _dict(precheck.get("prompt_integrity")).get("passed"),
            "paid_execution_authorized": _dict(precheck.get("paid_execution")).get("authorized"),
        },
        "technical_rerun_policy": plan_manifest.get("technical_rerun_policy"),
    }
    _write_json(output_dir / "execution_manifest.json", manifest)
    print(
        json.dumps(
            {
                "mode": "execute",
                "status": manifest["status"],
                "status_counts": manifest["status_counts"],
                "observed_account_usage_delta": manifest["observed_account_usage_delta"],
                "stop_reason": stop_reason,
                "output": str(output_dir),
            },
            sort_keys=True,
        )
    )
    return 0 if manifest["status"] == "complete" else 2


async def _execute_call(
    *,
    call: dict[str, Any],
    output_dir: Path,
    plan_manifest: dict[str, Any],
    client: OpenRouterClient,
) -> dict[str, Any]:
    _validate_call_prompt(call)
    repetition_id = str(call["repetition_id"])
    fixture_dir = (REPO_ROOT / str(call["fixture_relative_path"])).resolve()
    source_dir = fixture_dir / "source"
    decision = _read_json(source_dir / "decision_ordered.json")
    started = _read_json(source_dir / "decision_started.json")
    source_action_entry = _read_json(source_dir / "target_action.json")
    memory = _read_json(fixture_dir / "reconstructed" / "prompt_memory_ordered.json")
    system_prompt = _read_text_exact(source_dir / "original_system.txt")
    player_config = build_single_player_config(
        player_id=str(started["player_id"]),
        name=str(started.get("player_name") or started["player_id"]),
        openrouter_model_id=str(call["model_id"]),
        system_prompt=system_prompt,
        reasoning=_dict_or_none(call.get("reasoning")),
        provider=_dict_or_none(call.get("provider_constraint")),
    )
    intended_run_dir = output_dir / "runs" / repetition_id
    if intended_run_dir.exists() and any(intended_run_dir.iterdir()):
        raise FileExistsError(
            f"{intended_run_dir} already contains artifacts; refusing to overwrite."
        )
    run_files = build_run_files(
        output_dir / "runs",
        repetition_id,
        quality_base_dir=output_dir / "quality_check",
    )
    run_files.write_run_config(
        {
            "schema_version": "exact_history_repetition_run_config_v1",
            **_call_identity(call),
            "source_commit": _git_head(),
            "plan_experiment_id": plan_manifest.get("experiment_id"),
            "plan_prompt_mode": call.get("prompt_mode"),
            "source_fixture_path": _relative(fixture_dir),
            "source_prompt_hashes": {
                "system_sha256": call.get("system_sha256"),
                "user_sha256": call.get("user_sha256"),
                "tools_sha256": call.get("tools_sha256"),
            },
            "model": player_config.to_status(),
            "sampling_policy": "provider_default_unseeded",
            "action_application": "not_applied_one_step_decision_probe",
        }
    )
    run_files.write_players(
        {
            "schema_version": "v1",
            "players": [player_config.to_status()],
        }
    )
    run_files.write_snapshot(_dict(decision.get("state")))
    resolver = SharedDecisionResolver(
        openrouter=client,
        run_files=run_files,
        prompt_memory=FrozenPromptMemory(memory),
        space_key_by_index=build_space_key_by_index(),
    )

    async def log_writer(entry: dict[str, Any]) -> None:
        run_files.write_decision(entry)

    outcome = await resolver.resolve_decision(
        decision=decision,
        player_config=player_config,
        log_writer=log_writer,
    )
    run_files.write_action(
        {
            "decision_id": decision["decision_id"],
            "actor_player_id": decision["player_id"],
            "decision_type": decision["decision_type"],
            "turn_index": decision["turn_index"],
            "action": outcome.action,
            "decision_meta": outcome.decision_meta,
            "applied": False,
        }
    )
    resolved = resolver.build_decision_log_entry(
        decision=decision,
        player_config=player_config,
        phase="decision_resolved",
        action=outcome.action,
        attempts=outcome.attempts,
        retry_used=outcome.retry_used,
        fallback_used=outcome.fallback_used,
        fallback_reason=outcome.fallback_reason,
        applied=False,
        sequence_meta=outcome.sequence_meta,
    )
    run_files.write_decision(resolved)
    usage = write_usage_artifacts(run_files)
    source_action = _dict(source_action_entry.get("action"))
    status = _outcome_status(outcome)
    summary = {
        "schema_version": "exact_history_repetition_summary_v1",
        **_call_identity(call),
        "status": status,
        "source_action": source_action,
        "sampled_action": outcome.action,
        "action_and_args_match_source": _action_and_args(outcome.action)
        == _action_and_args(source_action),
        "full_action_match_source": outcome.action == source_action,
        "retry_used": outcome.retry_used,
        "fallback_used": outcome.fallback_used,
        "fallback_reason": outcome.fallback_reason,
        "attempt_count": len(outcome.attempts),
        "usage": usage,
        "action_applied": False,
        "completed_at_utc": _utc_now(),
    }
    run_files.write_summary(summary)
    run_files.write_artifact_manifest()
    cost = _number_or_none(_dict(usage.get("totals")).get("cost"))
    return {
        **_call_identity(call),
        "status": status,
        "completed_at_utc": summary["completed_at_utc"],
        "run_dir": _relative(run_files.run_dir),
        "quality_check_dir": _relative(run_files.quality_dir),
        "summary_sha256": _sha256_file(run_files.summary_path),
        "artifact_manifest_sha256": _sha256_file(run_files.artifact_manifest_path),
        "attempt_count": len(outcome.attempts),
        "retry_used": outcome.retry_used,
        "fallback_used": outcome.fallback_used,
        "fallback_reason": outcome.fallback_reason,
        "action_and_args_match_source": summary["action_and_args_match_source"],
        "full_action_match_source": summary["full_action_match_source"],
        "actual_cost": cost,
        "missing_usage_attempt_count": usage.get("missing_usage_attempt_count"),
    }


def _outcome_status(outcome: Any) -> str:
    if outcome.fallback_used:
        error_types = {
            str(attempt.error_type)
            for attempt in outcome.attempts
            if attempt.error_type
        }
        if error_types:
            return "provider_error"
        return "fallback"
    if outcome.retry_used:
        return "succeeded_after_retry"
    return "succeeded_valid_first"


async def _credit_snapshot(client: OpenRouterClient) -> dict[str, Any]:
    observed_at = _utc_now()
    result = await client.get_credits()
    if not result.ok:
        return {
            "observed_at_utc": observed_at,
            "status": "error",
            "status_code": result.status_code,
            "request_id": result.request_id,
            "error_type": result.error_type,
            "error": result.error,
            "total_credits": None,
            "total_usage": None,
            "available_credits": None,
        }
    data = _dict(_dict(result.response_json).get("data"))
    total_credits = _number_or_none(data.get("total_credits"))
    total_usage = _number_or_none(data.get("total_usage"))
    available = (
        round(total_credits - total_usage, 10)
        if total_credits is not None and total_usage is not None
        else None
    )
    return {
        "observed_at_utc": observed_at,
        "status": "ok",
        "status_code": result.status_code,
        "request_id": result.request_id,
        "total_credits": total_credits,
        "total_usage": total_usage,
        "available_credits": available,
    }


def _usage_delta(starting_usage: float | None, current_usage: Any) -> float | None:
    current = _number_or_none(current_usage)
    if starting_usage is None or current is None:
        return None
    return round(max(current - starting_usage, 0.0), 10)


def _last_results(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path):
        repetition_id = str(row.get("repetition_id") or "")
        if repetition_id:
            result[repetition_id] = row
    return result


def _call_identity(call: dict[str, Any]) -> dict[str, Any]:
    return {
        "repetition_id": call.get("repetition_id"),
        "execution_rank": call.get("execution_rank"),
        "fixture_id": call.get("fixture_id"),
        "actor_id": call.get("actor_id"),
        "model_id": call.get("model_id"),
        "repetition_index": call.get("repetition_index"),
        "source_run_id": call.get("source_run_id"),
        "source_decision_id": call.get("source_decision_id"),
        "source_category": call.get("source_category"),
    }


def _action_and_args(action: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": action.get("action"),
        "args": _dict(action.get("args")),
    }


def _age_hours(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    return max((_utc_datetime() - observed.astimezone(timezone.utc)).total_seconds() / 3600, 0.0)


def _read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip("\"'")
    return None


def _read_text_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object.")
        rows.append(value)
    return rows


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
        )
        handle.flush()


def _git_head() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _verify_fixture_provenance(
    fixture_dir: Path,
    fixture_manifest: dict[str, Any],
) -> None:
    generated_path = fixture_dir / "provenance" / "generated_hashes.json"
    generated = _read_json(generated_path)
    for row in _list(generated.get("files")):
        if not isinstance(row, dict):
            raise ValueError("fixture generated-hash inventory contains a non-object row")
        relative_path = str(row.get("relative_path") or "")
        path = fixture_dir / relative_path
        if (
            not path.is_file()
            or path.stat().st_size != row.get("bytes")
            or _sha256_file(path) != row.get("sha256")
        ):
            raise ValueError(f"fixture generated hash mismatch: {relative_path}")
    expected_tree = fixture_manifest.get("fixture_tree_sha256_before_manifest")
    observed_tree = _tree_hash(
        fixture_dir,
        exclude={"provenance/manifest.json"},
    )
    if observed_tree != expected_tree:
        raise ValueError(
            "fixture tree hash mismatch: "
            f"expected {expected_tree!r}, observed {observed_tree!r}"
        )


def _tree_hash(root: Path, *, exclude: set[str] | None = None) -> str:
    excluded = exclude or set()
    stream = bytearray()
    files = sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.as_posix(),
    )
    for path in files:
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        stream.extend(relative.encode("utf-8"))
        stream.extend(b"\0")
        stream.extend(_sha256_file(path).encode("ascii"))
        stream.extend(b"\n")
    return hashlib.sha256(bytes(stream)).hexdigest()


def _compact_json_bytes(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _utc_datetime() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now() -> str:
    return _utc_datetime().isoformat().replace("+00:00", "Z")


def _number_or_none(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
