from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .run_files import RunFiles
from .writer_jsonl import append_jsonl


EXPERIMENT_MANIFEST_VERSION = "experiment_manifest_v1"
REVIEW_COST_AGGREGATE_VERSION = "review_cost_aggregate_v1"
OPENROUTER_REASONING_POLICY_VERSION = "openrouter_reasoning_effort_only_v1"

USAGE_FIELDS = (
    "prompt_tokens",
    "input_tokens",
    "completion_tokens",
    "output_tokens",
    "total_tokens",
    "native_prompt_tokens",
    "native_completion_tokens",
    "native_total_tokens",
    "reasoning_tokens",
    "cached_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "cost",
    "latency_ms",
)

PROVIDER_REASONING_SEMANTICS = {
    "openai": {
        "native_control": "reasoning effort",
        "openrouter_low_mapping": "OpenRouter routes effort=low to the provider's low reasoning-effort control when supported.",
        "token_budget_policy": "No max_tokens or reasoning token budget is set by MonopolyBench.",
    },
    "anthropic": {
        "native_control": "extended thinking budget semantics",
        "openrouter_low_mapping": "OpenRouter abstracts Claude thinking controls behind effort=low when supported.",
        "token_budget_policy": "No explicit thinking budget is set by MonopolyBench.",
    },
    "google": {
        "native_control": "Gemini thinking level/budget semantics",
        "openrouter_low_mapping": "OpenRouter maps effort=low to the lowest supported Gemini thinking control for the route.",
        "token_budget_policy": "No thinkingBudget, maxOutputTokens, or max_tokens setting is set by MonopolyBench.",
    },
    "x-ai": {
        "native_control": "reasoning_effort",
        "openrouter_low_mapping": "OpenRouter routes effort=low to xAI's low reasoning-effort control when supported.",
        "token_budget_policy": "No max_tokens or reasoning token budget is set by MonopolyBench.",
    },
    "unknown": {
        "native_control": "provider-specific reasoning control, if supported",
        "openrouter_low_mapping": "OpenRouter receives effort=low; provider-native semantics should be checked for this model route.",
        "token_budget_policy": "No max_tokens or reasoning token budget is set by MonopolyBench.",
    },
}


def build_experiment_manifest(
    *,
    experiment_id: str,
    benchmark_tracks: list[str],
    models: list[dict[str, Any]] | list[str],
    reasoning_policy: dict[str, Any] | None,
    batch_type: str | None = None,
    run_count: int | None = None,
) -> dict[str, Any]:
    model_rows = [_model_manifest_row(model, reasoning_policy) for model in models]
    return {
        "schema_version": "v1",
        "experiment_manifest_version": EXPERIMENT_MANIFEST_VERSION,
        "experiment_id": experiment_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "gateway": "openrouter",
        "gateway_policy": {
            "status": "openrouter_only",
            "direct_provider_apis_used": False,
        },
        "batch_type": batch_type,
        "benchmark_tracks": benchmark_tracks,
        "run_count": run_count,
        "exact_model_ids": [row["openrouter_model_id"] for row in model_rows],
        "models": model_rows,
        "reasoning_policy": _reasoning_policy(reasoning_policy),
        "max_token_policy": {
            "max_tokens_set": False,
            "reasoning_max_tokens_set": False,
            "note": "MonopolyBench does not set max_tokens, max_completion_tokens, reasoning.max_tokens, thinkingBudget, or provider token-budget controls.",
        },
        "usage_accounting": {
            "source": "openrouter_actuals_only",
            "local_tokenizer_estimates_used": False,
            "per_call_artifacts": ["usage_attempts.jsonl"],
            "per_decision_artifacts": ["usage_decisions.jsonl"],
            "aggregate_artifacts": ["usage.json", "cost_report.json", "token_report.json", "review_cost_aggregate.json"],
            "fields": list(USAGE_FIELDS),
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Experiment manifests and accounting artifacts are post-hoc/control metadata and are not injected into prompts.",
        },
    }


def build_review_cost_aggregate(
    *,
    batch_id: str,
    batch_type: str,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    calls = _collect_usage_rows(entries, "usage_attempts.jsonl")
    decisions = _collect_usage_rows(entries, "usage_decisions.jsonl")
    return {
        "schema_version": "v1",
        "review_cost_aggregate_version": REVIEW_COST_AGGREGATE_VERSION,
        "batch_id": batch_id,
        "batch_type": batch_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "run_count": len(entries),
        "call_count": len(calls),
        "decision_count": len(decisions),
        "totals": _totals(calls),
        "by_model": _group(calls, "openrouter_model_id"),
        "by_run": _group(calls, "run_id"),
        "by_decision_type": _group(calls, "decision_type"),
        "by_player": _group(calls, "player_id"),
        "by_turn": _group_by_turn(calls),
        "per_call": calls,
        "per_decision": decisions,
        "manual_review_queue": _manual_review_queue(entries, calls, decisions),
    }


def usage_calls_jsonl(aggregate: dict[str, Any]) -> list[dict[str, Any]]:
    calls = aggregate.get("per_call")
    return [row for row in calls if isinstance(row, dict)] if isinstance(calls, list) else []


def write_experiment_review_artifacts(
    run_files: RunFiles,
    *,
    benchmark_tracks: list[str],
    models: list[dict[str, Any]] | list[str],
    reasoning_policy: dict[str, Any] | None,
    batch_type: str,
) -> dict[str, Any]:
    manifest = build_experiment_manifest(
        experiment_id=run_files.run_id,
        benchmark_tracks=benchmark_tracks,
        models=models,
        reasoning_policy=reasoning_policy,
        batch_type=batch_type,
        run_count=1,
    )
    aggregate = build_review_cost_aggregate(
        batch_id=run_files.run_id,
        batch_type=batch_type,
        entries=[
            {
                "run_id": run_files.run_id,
                "run_index": 0,
                "run_dir": str(run_files.run_dir),
                "status": "completed",
            }
        ],
    )
    run_files.write_json_artifact(run_files.experiment_manifest_path, manifest)
    run_files.write_json_artifact(run_files.review_cost_aggregate_path, aggregate)
    if run_files.review_cost_calls_path.exists():
        run_files.review_cost_calls_path.unlink()
    for row in usage_calls_jsonl(aggregate):
        append_jsonl(run_files.review_cost_calls_path, row)
    return aggregate


def _model_manifest_row(model: dict[str, Any] | str, reasoning_policy: dict[str, Any] | None) -> dict[str, Any]:
    if isinstance(model, dict):
        model_id = str(model.get("openrouter_model_id") or model.get("model_id") or model.get("id") or "unknown")
        display_name = model.get("model_display_name") or model.get("display_name")
        reasoning = model.get("reasoning") if isinstance(model.get("reasoning"), dict) else reasoning_policy
    else:
        model_id = str(model)
        display_name = None
        reasoning = reasoning_policy
    provider = _provider_from_model_id(model_id)
    return {
        "openrouter_model_id": model_id,
        "model_display_name": display_name,
        "provider": provider,
        "openrouter_provider_routing": model.get("provider") if isinstance(model, dict) else None,
        "reasoning": _reasoning_policy(reasoning)["request_payload"],
        "provider_native_reasoning_semantics": PROVIDER_REASONING_SEMANTICS.get(
            provider,
            PROVIDER_REASONING_SEMANTICS["unknown"],
        ),
    }


def _reasoning_policy(reasoning_policy: dict[str, Any] | None) -> dict[str, Any]:
    if reasoning_policy is None:
        return {
            "policy_id": "none",
            "policy_version": OPENROUTER_REASONING_POLICY_VERSION,
            "request_payload": None,
            "effort": None,
        }
    effort = reasoning_policy.get("effort") if isinstance(reasoning_policy, dict) else None
    return {
        "policy_id": f"effort_{effort}_v1" if effort else "custom_effort_v1",
        "policy_version": OPENROUTER_REASONING_POLICY_VERSION,
        "request_payload": {"effort": effort} if effort else dict(reasoning_policy),
        "effort": effort,
    }


def _provider_from_model_id(model_id: str) -> str:
    return model_id.split("/", 1)[0] if "/" in model_id else "unknown"


def _collect_usage_rows(entries: list[dict[str, Any]], filename: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        run_dir = Path(str(entry.get("run_dir") or ""))
        run_id = str(entry.get("run_id") or "")
        for row in _read_jsonl(run_dir / filename):
            item = _with_usage_aliases(dict(row))
            item["batch_run_id"] = run_id
            item["batch_run_index"] = entry.get("run_index")
            item["batch_status"] = entry.get("status")
            item["run_dir"] = str(run_dir)
            rows.append(item)
    return rows


def _with_usage_aliases(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("input_tokens") is None:
        row["input_tokens"] = row.get("prompt_tokens")
    if row.get("output_tokens") is None:
        row["output_tokens"] = row.get("completion_tokens")
    return row


def _totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {field: 0.0 if field in {"cost"} else 0 for field in USAGE_FIELDS}
    retry_count = 0
    fallback_count = 0
    missing_usage_count = 0
    for row in rows:
        for field in USAGE_FIELDS:
            value = row.get(field)
            if isinstance(value, (int, float)):
                totals[field] += float(value) if field == "cost" else int(value)
        if row.get("retry_used"):
            retry_count += 1
        if row.get("fallback_used"):
            fallback_count += 1
        if row.get("accounting_status") == "missing_openrouter_usage":
            missing_usage_count += 1
    totals["cost"] = round(float(totals["cost"]), 10)
    totals["retry_call_count"] = retry_count
    totals["fallback_call_count"] = fallback_count
    totals["missing_usage_call_count"] = missing_usage_count
    return totals


def _group(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        group_key = str(row.get(key) or "unknown")
        current = grouped.setdefault(group_key, {"count": 0, **{field: 0 for field in USAGE_FIELDS}})
        current["count"] += 1
        for field in USAGE_FIELDS:
            value = row.get(field)
            if isinstance(value, (int, float)):
                current[field] += float(value) if field == "cost" else int(value)
    for value in grouped.values():
        value["cost"] = round(float(value["cost"]), 10)
    return grouped


def _group_by_turn(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], dict[str, Any]] = {}
    for row in rows:
        turn_index = row.get("turn_index")
        if not isinstance(turn_index, int):
            continue
        key = (str(row.get("run_id") or "unknown"), turn_index)
        current = grouped.setdefault(
            key,
            {
                "run_id": key[0],
                "turn_index": key[1],
                "call_count": 0,
                **{field: 0 for field in USAGE_FIELDS},
            },
        )
        current["call_count"] += 1
        for field in USAGE_FIELDS:
            value = row.get(field)
            if isinstance(value, (int, float)):
                current[field] += float(value) if field == "cost" else int(value)
    rows_out = list(grouped.values())
    for row in rows_out:
        row["cost"] = round(float(row["cost"]), 10)
    rows_out.sort(key=lambda row: (str(row["run_id"]), int(row["turn_index"])))
    return rows_out


def _manual_review_queue(
    entries: list[dict[str, Any]],
    calls: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    queue.extend(_outlier_rows(calls, "cost", "high_cost_call"))
    queue.extend(_outlier_rows(calls, "reasoning_tokens", "high_reasoning_tokens_call"))
    for row in calls:
        if row.get("fallback_used") or row.get("retry_used") or row.get("accounting_status") == "missing_openrouter_usage":
            queue.append(_queue_item(row, "reliability_review"))
    for entry in entries:
        if entry.get("status") != "completed":
            queue.append(
                {
                    "queue_item_type": "failed_run",
                    "run_id": entry.get("run_id"),
                    "run_dir": entry.get("run_dir"),
                    "status": entry.get("status"),
                    "error": entry.get("error"),
                    "suggested_labels": ["tool_reliability_issue"],
                }
            )
    decision_scores = {
        str(row.get("decision_id")): row
        for row in decisions
        if row.get("decision_id") is not None
    }
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in queue:
        marker = json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        if marker in seen:
            continue
        seen.add(marker)
        decision_id = item.get("decision_id")
        if decision_id is not None and str(decision_id) in decision_scores:
            item["decision_usage"] = decision_scores[str(decision_id)]
        unique.append(item)
    return unique[:500]


def _outlier_rows(rows: list[dict[str, Any]], field: str, item_type: str) -> list[dict[str, Any]]:
    numeric = [row for row in rows if isinstance(row.get(field), (int, float)) and float(row[field]) > 0]
    numeric.sort(key=lambda row: float(row.get(field) or 0), reverse=True)
    return [_queue_item(row, item_type) for row in numeric[:25]]


def _queue_item(row: dict[str, Any], item_type: str) -> dict[str, Any]:
    return {
        "queue_item_type": item_type,
        "run_id": row.get("run_id"),
        "run_dir": row.get("run_dir"),
        "decision_id": row.get("decision_id"),
        "attempt_index": row.get("attempt_index"),
        "turn_index": row.get("turn_index"),
        "decision_type": row.get("decision_type"),
        "player_id": row.get("player_id"),
        "openrouter_model_id": row.get("openrouter_model_id"),
        "cost": row.get("cost"),
        "input_tokens": row.get("input_tokens"),
        "output_tokens": row.get("output_tokens"),
        "reasoning_tokens": row.get("reasoning_tokens"),
        "total_tokens": row.get("total_tokens"),
        "latency_ms": row.get("latency_ms"),
        "retry_used": row.get("retry_used"),
        "fallback_used": row.get("fallback_used"),
        "suggested_labels": _suggested_labels(row, item_type),
    }


def _suggested_labels(row: dict[str, Any], item_type: str) -> list[str]:
    labels: list[str] = []
    decision_type = str(row.get("decision_type") or "")
    if "TRADE" in decision_type:
        labels.append("bad_trade")
    if "LIQUIDATION" in decision_type or "BUILD" in decision_type or "MORTGAGE" in decision_type:
        labels.append("cash_buffer_error")
    if "AUCTION" in decision_type:
        labels.append("auction_overpay")
    if "JAIL" in decision_type:
        labels.append("jail_policy_error")
    if row.get("fallback_used") or item_type == "reliability_review":
        labels.append("tool_reliability_issue")
    if item_type == "high_cost_call":
        labels.append("cost_outlier")
    if item_type == "high_reasoning_tokens_call":
        labels.append("reasoning_token_outlier")
    return labels or ["manual_review"]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows
