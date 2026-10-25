from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .run_files import RunFiles, evidence_paths


USAGE_ACCOUNTING_VERSION = "usage_accounting_v3"
# Why a configured fallback model served an attempt. Response conditions come from the
# arena's versioned refusal-recovery policy; accounting only describes them.
FALLBACK_TRIGGERS = {"fallback_without_private_thought": "explicit_provider_refusal_after_same_model_retry"}


def build_usage_report(run_files: RunFiles, *, byok_aware: bool = False) -> dict[str, Any]:
    decisions = _read_jsonl(run_files.decisions_path)
    attempt_rows = _all_attempt_usage_rows(run_files, decisions)
    decision_rows = _decision_usage_rows(attempt_rows)
    report = _aggregate_usage(run_files.run_id, attempt_rows, decision_rows)
    if byok_aware:
        # Usage v2 already adds BYOK upstream inference cost and keeps unknown cost null.
        report["source"] = "openrouter_and_byok_actuals"
    return report


def write_usage_artifacts(run_files: RunFiles) -> dict[str, Any]:
    decisions = _read_jsonl(run_files.decisions_path)
    attempt_rows = _all_attempt_usage_rows(run_files, decisions)
    decision_rows = _decision_usage_rows(attempt_rows)
    report = _aggregate_usage(run_files.run_id, attempt_rows, decision_rows)
    _write_jsonl(run_files.usage_attempts_path, attempt_rows)
    _write_jsonl(run_files.usage_decisions_path, decision_rows)
    run_files.write_json_artifact(run_files.usage_path, report)
    run_files.write_json_artifact(run_files.cost_report_path, _cost_report(report))
    return report


def _all_attempt_usage_rows(run_files: RunFiles, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _attempt_usage_rows(decisions)
    participants = {row.get("decision_id"): row for row in decisions if row.get("decision_id")}
    accounted_calls = {row["call_id"] for row in rows if row.get("call_id")}
    legacy_accounted = {(row["decision_id"], row["attempt_index"]) for row in rows if not row.get("call_id")}
    for path in evidence_paths(run_files.run_dir / "calls"):
        call = json.loads(path.read_text(encoding="utf-8"))
        if call["call_id"] in accounted_calls or (call["decision_id"], call["attempt_index"]) in legacy_accounted:
            continue
        result = _dict(call.get("result"))
        raw = _dict(result.get("response_json"))
        normalized = _normalize_usage(_dict(raw.get("usage")), raw)
        decision = _dict(participants.get(call["decision_id"]))
        requested = call["request"].get("model")
        participant = decision.get("openrouter_model_id") or requested
        rows.append({**normalized, "run_id": run_files.run_id, "decision_id": call["decision_id"],
                     "attempt_index": call["attempt_index"], "player_id": call.get("player_id"),
                     "turn_index": call.get("turn_index"), "decision_type": call.get("decision_type"),
                     "openrouter_model_id": raw.get("model") or requested, "call_id": call["call_id"],
                     "participant_model_id": participant,
                     "participant_model_display_name": decision.get("model_display_name") or participant,
                     "requested_model_id": requested, "response_condition": call.get("response_condition") or "standard",
                     "fallback_model_used": bool(requested and participant and requested != participant),
                     "call_status": call["status"], "input_tokens": normalized["prompt_tokens"],
                     "output_tokens": normalized["completion_tokens"],
                     "accounting_status": "actual_openrouter_usage" if normalized["usage_seen"] else "missing_openrouter_usage",
                     "error_type": result.get("error_type"), "applied": False})
    return rows


def _attempt_usage_rows(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        if decision.get("phase") != "decision_resolved":
            continue
        attempts = _list(decision.get("attempts"))
        for index, attempt_value in enumerate(attempts):
            attempt = _dict(attempt_value)
            raw = _dict(attempt.get("raw_response"))
            usage = _dict(raw.get("usage"))
            normalized = _normalize_usage(usage, raw)
            participant = decision.get("openrouter_model_id")
            requested = attempt.get("requested_model") or participant
            rows.append(
                {
                    "schema_version": "v1",
                    "usage_accounting_version": USAGE_ACCOUNTING_VERSION,
                    "run_id": decision.get("run_id"),
                    "decision_id": decision.get("decision_id"),
                    "attempt_index": index,
                    "turn_index": decision.get("turn_index"),
                    "decision_type": decision.get("decision_type"),
                    "player_id": decision.get("player_id"),
                    # openrouter_model_id is the model that served this attempt; the
                    # participant is the seat's configured model, which owns the decision.
                    "openrouter_model_id": raw.get("model") or requested,
                    "model_display_name": raw.get("model") or requested or decision.get("model_display_name"),
                    "participant_model_id": participant,
                    "participant_model_display_name": decision.get("model_display_name") or participant,
                    "requested_model_id": requested,
                    "response_condition": attempt.get("response_condition") or "standard",
                    "fallback_model_used": bool(requested and participant and requested != participant),
                    "openrouter_request_id": attempt.get("openrouter_request_id"),
                    "call_id": attempt.get("call_id"),
                    "openrouter_status_code": attempt.get("openrouter_status_code"),
                    "generation_id": raw.get("id"),
                    "finish_reason": _finish_reason(raw),
                    "accounting_status": "actual_openrouter_usage" if normalized["usage_seen"] else "missing_openrouter_usage",
                    "accounting_source": normalized["accounting_source"],
                    "prompt_tokens": normalized["prompt_tokens"],
                    "input_tokens": normalized["prompt_tokens"],
                    "completion_tokens": normalized["completion_tokens"],
                    "output_tokens": normalized["completion_tokens"],
                    "total_tokens": normalized["total_tokens"],
                    "native_prompt_tokens": normalized["native_prompt_tokens"],
                    "native_completion_tokens": normalized["native_completion_tokens"],
                    "native_total_tokens": normalized["native_total_tokens"],
                    "reasoning_tokens": normalized["reasoning_tokens"],
                    "cached_tokens": normalized["cached_tokens"],
                    "cache_read_tokens": normalized["cache_read_tokens"],
                    "cache_write_tokens": normalized["cache_write_tokens"],
                    "cost": normalized["cost"],
                    "gateway_charge": normalized["gateway_charge"],
                    "upstream_inference_cost": normalized["upstream_inference_cost"],
                    "cost_status": normalized["cost_status"],
                    "raw_usage": usage,
                    "latency_ms": attempt.get("latency_ms"),
                    "retry_used": bool(decision.get("retry_used")),
                    "fallback_used": bool(decision.get("fallback_used")),
                    "fallback_reason": decision.get("fallback_reason"),
                    "error_type": attempt.get("error_type"),
                }
            )
    return rows


def _decision_usage_rows(attempt_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in attempt_rows:
        decision_id = str(row.get("decision_id") or "")
        grouped.setdefault(decision_id, []).append(row)
    rows: list[dict[str, Any]] = []
    for decision_id, attempts in sorted(grouped.items()):
        first = attempts[0]
        rows.append(
            {
                "schema_version": "v1",
                "usage_accounting_version": USAGE_ACCOUNTING_VERSION,
                "run_id": first.get("run_id"),
                "decision_id": decision_id,
                "turn_index": first.get("turn_index"),
                "decision_type": first.get("decision_type"),
                "player_id": first.get("player_id"),
                "openrouter_model_id": _participant(first),
                "model_display_name": first.get("participant_model_display_name") or first.get("model_display_name"),
                "attempt_count": len(attempts),
                "fallback_attempt_count": sum(1 for row in attempts if row.get("fallback_model_used")),
                "fallback_models_used": sorted({str(row.get("requested_model_id")) for row in attempts
                                                if row.get("fallback_model_used")}),
                "accounting_status": _combined_status(attempts),
                "prompt_tokens": _sum_optional(attempts, "prompt_tokens"),
                "input_tokens": _sum_optional(attempts, "input_tokens"),
                "completion_tokens": _sum_optional(attempts, "completion_tokens"),
                "output_tokens": _sum_optional(attempts, "output_tokens"),
                "total_tokens": _sum_optional(attempts, "total_tokens"),
                "native_prompt_tokens": _sum_optional(attempts, "native_prompt_tokens"),
                "native_completion_tokens": _sum_optional(attempts, "native_completion_tokens"),
                "native_total_tokens": _sum_optional(attempts, "native_total_tokens"),
                "reasoning_tokens": _sum_optional(attempts, "reasoning_tokens"),
                "cached_tokens": _sum_optional(attempts, "cached_tokens"),
                "cache_read_tokens": _sum_optional(attempts, "cache_read_tokens"),
                "cache_write_tokens": _sum_optional(attempts, "cache_write_tokens"),
                "cost": _sum_optional_float(attempts, "cost"),
                "latency_ms": _sum_optional(attempts, "latency_ms"),
                "retry_used": any(row.get("retry_used") for row in attempts),
                "fallback_used": any(row.get("fallback_used") for row in attempts),
                "fallback_reason": next((row.get("fallback_reason") for row in attempts if row.get("fallback_reason")), None),
            }
        )
    return rows


def _aggregate_usage(
    run_id: str,
    attempt_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    by_player: dict[str, dict[str, Any]] = {}
    for row in decision_rows:
        model_id = str(row.get("openrouter_model_id") or "unknown")
        player_id = str(row.get("player_id") or "unknown")
        _accumulate_group(by_model, model_id, row)
        _accumulate_group(by_player, player_id, row)
    # Known spend per group comes from attempts: a decision with one unknown call has no cost.
    # Groups are participants, so fallback-model attempts stay under the seat that used them.
    for target, key_of in ((by_model, _participant), (by_player, lambda row: str(row.get("player_id") or "unknown"))):
        attempts_by_key: dict[str, list[dict[str, Any]]] = {}
        for row in attempt_rows:
            attempts_by_key.setdefault(key_of(row), []).append(row)
        for key, rows in attempts_by_key.items():
            group = target.setdefault(key, {"decision_count": 0, **_zero_totals()})
            group["known_cost_subtotal"] = _known_subtotal(rows)
            group["own_model"] = _attempt_breakdown([row for row in rows if not row.get("fallback_model_used")])
            group["fallback_models"] = _fallback_breakdown(rows)
        for group in target.values():
            group.setdefault("known_cost_subtotal", 0.0)
            group.setdefault("own_model", _attempt_breakdown([]))
            group.setdefault("fallback_models", {})
    totals = _totals(decision_rows)
    if not attempt_rows:
        totals["cost"] = 0.0  # No provider calls is known zero spending, not missing usage.
    return {
        "schema_version": "v1",
        "usage_accounting_version": USAGE_ACCOUNTING_VERSION,
        "run_id": run_id,
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "attempt_count": len(attempt_rows),
        "decision_count": len(decision_rows),
        "missing_usage_attempt_count": sum(1 for row in attempt_rows if row["accounting_status"] == "missing_openrouter_usage"),
        "missing_cost_attempt_count": sum(row.get("cost") is None for row in attempt_rows),
        "cost_coverage": "complete" if all(row.get("cost") is not None for row in attempt_rows) else "partial_or_missing",
        "known_cost_subtotal": round(sum(float(row["cost"]) for row in attempt_rows if row.get("cost") is not None), 10),
        "fallback_attempt_count": sum(1 for row in attempt_rows if row.get("fallback_model_used")),
        "totals": totals,
        "by_model": by_model,
        "by_player": by_player,
    }


def _participant(row: dict[str, Any]) -> str:
    return str(row.get("participant_model_id") or row.get("openrouter_model_id") or "unknown")


def _known_subtotal(rows: list[dict[str, Any]]) -> float:
    return round(sum(float(row["cost"]) for row in rows if isinstance(row.get("cost"), (int, float))), 10)


def _attempt_breakdown(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "attempt_count": len(rows),
        "prompt_tokens": _sum_optional(rows, "prompt_tokens"),
        "completion_tokens": _sum_optional(rows, "completion_tokens"),
        "total_tokens": _sum_optional(rows, "total_tokens"),
        "reasoning_tokens": _sum_optional(rows, "reasoning_tokens"),
        # Unknown stays unknown: one missing call cost leaves this cost null.
        "cost": _sum_optional_float(rows, "cost") if rows else 0.0,
        "known_cost_subtotal": _known_subtotal(rows),
        "missing_cost_attempt_count": sum(1 for row in rows if row.get("cost") is None),
    }


def _fallback_breakdown(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Fallback models nest under the participant that used them, with why and where."""
    by_fallback: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("fallback_model_used"):
            by_fallback.setdefault(str(row.get("requested_model_id")), []).append(row)
    breakdown: dict[str, dict[str, Any]] = {}
    for model_id, fallback_rows in sorted(by_fallback.items()):
        conditions = sorted({str(row.get("response_condition") or "standard") for row in fallback_rows})
        decision_ids = sorted({str(row.get("decision_id")) for row in fallback_rows})
        breakdown[model_id] = {
            **_attempt_breakdown(fallback_rows),
            "served_model_ids": sorted({str(row.get("openrouter_model_id")) for row in fallback_rows}),
            "decision_count": len(decision_ids),
            "decision_ids": decision_ids,
            "response_conditions": conditions,
            "triggers": sorted({FALLBACK_TRIGGERS.get(condition, f"unrecognized_condition:{condition}")
                                for condition in conditions}),
        }
    return breakdown


def _cost_report(usage_report: dict[str, Any]) -> dict[str, Any]:
    totals = _dict(usage_report.get("totals"))
    return {
        "schema_version": "v1",
        "usage_accounting_version": USAGE_ACCOUNTING_VERSION,
        "run_id": usage_report.get("run_id"),
        "source": usage_report.get("source"),
        "local_tokenizer_estimates_used": False,
        "total_actual_cost": totals.get("cost"),
        "known_cost_subtotal": usage_report.get("known_cost_subtotal"),
        "cost_coverage": usage_report.get("cost_coverage"),
        "attempt_count": usage_report.get("attempt_count"),
        "missing_cost_attempt_count": usage_report.get("missing_cost_attempt_count"),
        "total_estimated_cost": None,
        "missing_usage_attempt_count": usage_report.get("missing_usage_attempt_count"),
        "by_model": _dict(usage_report.get("by_model")),
        "by_player": _dict(usage_report.get("by_player")),
    }


def _normalize_usage(usage: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    generation_data = _generation_data(raw)
    native = _dict(usage.get("native_tokens"))
    prompt_details = _dict(usage.get("prompt_tokens_details"))
    completion_details = _dict(usage.get("completion_tokens_details"))
    cost = usage.get("cost")
    if not isinstance(cost, (int, float)):
        cost = raw.get("cost") if isinstance(raw.get("cost"), (int, float)) else raw.get("total_cost")
    if not isinstance(cost, (int, float)) and isinstance(generation_data.get("total_cost"), (int, float)):
        cost = generation_data["total_cost"]
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    if not isinstance(prompt_tokens, (int, float)):
        prompt_tokens = generation_data.get("tokens_prompt")
    if not isinstance(completion_tokens, (int, float)):
        completion_tokens = generation_data.get("tokens_completion")
    if not isinstance(total_tokens, (int, float)):
        total_tokens = generation_data.get("total_tokens")
    if (
        not isinstance(total_tokens, (int, float))
        and isinstance(prompt_tokens, (int, float))
        and isinstance(completion_tokens, (int, float))
    ):
        total_tokens = int(prompt_tokens) + int(completion_tokens)
    accounting_source = "missing"
    gateway_charge = float(cost) if isinstance(cost, (int, float)) else None
    details = _dict(usage.get("cost_details"))
    # An explicit null is missing evidence, so later sources may still supply the value.
    upstream = next((value for value in (details.get("upstream_inference_cost"), generation_data.get("upstream_inference_cost"))
                     if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)), None)
    byok = next((value for value in (usage.get("is_byok"), raw.get("is_byok"), generation_data.get("is_byok"))
                 if isinstance(value, bool)), None)
    # Upstream cost is already included for credit-billed calls. It is additive
    # only with explicit BYOK evidence, or a zero gateway charge.
    if isinstance(upstream, (int, float)) and (byok is True or gateway_charge == 0):
        cost = gateway_charge + float(upstream) if gateway_charge is not None else None
    elif byok is True:
        cost = None  # A known gateway fee does not reveal the missing upstream bill.
    if usage and generation_data:
        accounting_source = "chat_completion_usage_with_generation_backfill"
    elif usage:
        accounting_source = "chat_completion_usage"
    elif generation_data:
        accounting_source = "generation_endpoint"
    return {
        "usage_seen": bool(usage) or bool(generation_data),
        "accounting_source": accounting_source,
        "prompt_tokens": _optional_int(prompt_tokens),
        "completion_tokens": _optional_int(completion_tokens),
        "total_tokens": _optional_int(total_tokens),
        "native_prompt_tokens": _optional_int(
            native.get("prompt_tokens") or usage.get("native_prompt_tokens") or generation_data.get("native_tokens_prompt")
        ),
        "native_completion_tokens": _optional_int(
            native.get("completion_tokens")
            or usage.get("native_completion_tokens")
            or generation_data.get("native_tokens_completion")
        ),
        "native_total_tokens": _optional_int(
            native.get("total_tokens") or usage.get("native_total_tokens") or _generation_native_total(generation_data)
        ),
        "reasoning_tokens": _optional_int(
            completion_details.get("reasoning_tokens")
            or completion_details.get("reasoning")
            or usage.get("reasoning_tokens")
            or generation_data.get("native_tokens_reasoning")
        ),
        "cached_tokens": _optional_int(
            prompt_details.get("cached_tokens")
            or prompt_details.get("cache_read_tokens")
            or usage.get("cached_tokens")
            or generation_data.get("native_tokens_cached")
        ),
        "cache_read_tokens": _optional_int(prompt_details.get("cache_read_tokens") or usage.get("cache_read_tokens")),
        "cache_write_tokens": _optional_int(prompt_details.get("cache_write_tokens") or usage.get("cache_write_tokens")),
        "cost": float(cost) if isinstance(cost, (int, float)) else None,
        "gateway_charge": gateway_charge,
        "upstream_inference_cost": upstream,
        "cost_status": "known" if isinstance(cost, (int, float)) else "unknown",
    }


def _finish_reason(raw: dict[str, Any]) -> str | None:
    choices = raw.get("choices") if isinstance(raw.get("choices"), list) else []
    if not choices:
        return None
    first = choices[0] if isinstance(choices[0], dict) else {}
    value = first.get("finish_reason")
    return value if isinstance(value, str) else None


def _generation_data(raw: dict[str, Any]) -> dict[str, Any]:
    metadata = raw.get("openrouter_generation")
    if not isinstance(metadata, dict) or metadata.get("status") != "ok":
        return {}
    data = metadata.get("data")
    return data if isinstance(data, dict) else {}


def _generation_native_total(generation_data: dict[str, Any]) -> int | None:
    prompt = generation_data.get("native_tokens_prompt")
    completion = generation_data.get("native_tokens_completion")
    if isinstance(prompt, (int, float)) and isinstance(completion, (int, float)):
        return int(prompt) + int(completion)
    return None


def _accumulate_group(target: dict[str, dict[str, Any]], key: str, row: dict[str, Any]) -> None:
    current = target.setdefault(key, {"decision_count": 0, **_zero_totals()})
    current["decision_count"] += 1
    for field in _numeric_fields():
        value = row.get(field)
        if field == "cost":
            if not isinstance(value, (int, float)) or (current["decision_count"] > 1 and current[field] is None):
                current[field] = None
            else:
                current[field] = (current[field] or 0) + value
            continue
        if isinstance(value, (int, float)):
            current[field] = (current[field] or 0) + value


def _totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = _zero_totals()
    for row in rows:
        for field in _numeric_fields():
            value = row.get(field)
            if isinstance(value, (int, float)):
                totals[field] = (totals[field] or 0) + value
    totals["cost"] = _sum_optional_float(rows, "cost")
    return totals


def _zero_totals() -> dict[str, Any]:
    return {field: None for field in _numeric_fields()}


def _numeric_fields() -> tuple[str, ...]:
    return (
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


def _combined_status(rows: list[dict[str, Any]]) -> str:
    statuses = {row.get("accounting_status") for row in rows}
    if statuses == {"actual_openrouter_usage"}:
        return "actual_openrouter_usage"
    if "actual_openrouter_usage" in statuses:
        return "partial_openrouter_usage"
    return "missing_openrouter_usage"


def _sum_optional(rows: list[dict[str, Any]], field: str) -> int | None:
    values: list[int] = []
    for row in rows:
        value = row.get(field)
        if isinstance(value, int):
            values.append(value)
    return sum(values) if values else None


def _sum_optional_float(rows: list[dict[str, Any]], field: str) -> float | None:
    values: list[float] = []
    for row in rows:
        value = row.get(field)
        if isinstance(value, (int, float)):
            values.append(float(value))
        else:
            return None
    return round(sum(values), 10) if values else None


def _optional_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")
