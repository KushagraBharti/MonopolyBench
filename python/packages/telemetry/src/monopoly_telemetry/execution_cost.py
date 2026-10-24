from __future__ import annotations

from typing import Any
import json
from pathlib import Path


def call_cost(usage: dict[str, Any] | None, *, unknown: bool = False) -> dict[str, Any]:
    usage = usage or {}
    charge: Any = usage.get("cost")
    upstream: Any = (usage.get("cost_details") or {}).get("upstream_inference_cost")
    byok = usage.get("is_byok")
    known = isinstance(charge, (int, float)) and (byok is not True or isinstance(upstream, (int, float)))
    return {"is_byok": byok, "usage_cost": charge, "upstream_cost": upstream,
            "total_cost": charge + upstream if known and byok else charge if known else None,
            "cost_status": "unknown" if unknown else "known" if known else "missing"}


def execution_cost(calls: list[dict[str, Any]]) -> dict[str, Any]:
    return {"version": "execution_cost_v1", "calls": len(calls),
            "known_total": sum(c["total_cost"] for c in calls if c.get("total_cost") is not None),
            "openrouter_charge": sum(c.get("usage_cost") or 0 for c in calls),
            "provider_charge": sum((c.get("upstream_cost") or 0) for c in calls if c.get("is_byok")),
            "missing_calls": sum(c.get("cost_status") == "missing" for c in calls),
            "unknown_calls": sum(c.get("cost_status") == "unknown" for c in calls)}


def execution_cost_report(directory: Path, calls: list[dict[str, Any]]) -> dict[str, Any]:
    """Separate token-price estimates from actual charges, including unknown calls."""
    pricing_file = directory / "pricing_start.json"
    pricing = json.loads(pricing_file.read_text()) if pricing_file.exists() else {}
    catalog = (pricing.get("response_json") or {}).get("data", [])
    prices = {entry["id"]: entry.get("pricing", {}) for entry in catalog if "id" in entry}
    rows = []
    for call in calls:
        intent_path = directory / "calls" / f"{call['call_id']}.intent.json"
        response_path = directory / "calls" / f"{call['call_id']}.response.json"
        intent = json.loads(intent_path.read_text()) if intent_path.exists() else {}
        response = json.loads(response_path.read_text()) if response_path.exists() else {}
        payload = intent.get("payload", {})
        usage = (response.get("response_json") or {}).get("usage") or {}
        price = prices.get(payload.get("model"), {})
        estimated = None
        estimated_tokens = None
        source = None
        if call.get("cost_status") != "known" and price.get("prompt") is not None:
            # Character heuristic is deliberately labeled, never used as actual cost.
            estimated_tokens = usage.get("prompt_tokens") or (len(intent.get("payload_raw", ""))+3)//4
            output = usage.get("completion_tokens", 0)
            estimated = estimated_tokens * float(price["prompt"]) + output * float(price.get("completion", 0))
            source = "reported_tokens_start_catalog" if usage.get("prompt_tokens") else "characters_div_four_input_only_start_catalog"
        rows.append({**call, "estimated_cost": estimated, "estimated_input_tokens": estimated_tokens, "estimate_source": source})
    return {**execution_cost(calls), "call_details": rows,
            "estimated_unaccounted_cost": sum(row["estimated_cost"] for row in rows if row["estimated_cost"] is not None)}
