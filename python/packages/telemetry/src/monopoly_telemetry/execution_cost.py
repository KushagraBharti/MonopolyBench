from __future__ import annotations

from typing import Any
import json
import math
from pathlib import Path


def call_cost(usage: dict[str, Any] | None, *, unknown: bool = False) -> dict[str, Any]:
    usage = usage if isinstance(usage, dict) else {}
    def number(value: Any) -> int | float | None:
        return value if type(value) in {int, float} and math.isfinite(value) else None
    charge = number(usage.get("cost"))
    details = usage.get("cost_details")
    upstream = number(details.get("upstream_inference_cost")) if isinstance(details, dict) else None
    byok = usage.get("is_byok") if type(usage.get("is_byok")) is bool else None
    if charge is not None and upstream is not None and adds_upstream(charge, upstream, byok):
        total = charge + upstream
    elif charge is not None and byok is not True:
        total = charge
    else:
        total = None  # A BYOK gateway fee does not reveal the provider's bill.
    return {"is_byok": byok, "usage_cost": charge, "upstream_cost": upstream, "total_cost": total,
            "cost_status": "unknown" if unknown else "known" if total is not None else "missing"}


def adds_upstream(charge: float | None, upstream: float | None, byok: bool | None) -> bool:
    """Usage accounting v2 rule: upstream cost is already inside credit charges and is
    additive only with explicit BYOK evidence or a zero gateway charge."""
    return charge is not None and upstream is not None and (byok is True or charge == 0)


def execution_cost(calls: list[dict[str, Any]]) -> dict[str, Any]:
    return {"version": "execution_cost_v1", "calls": len(calls),
            "known_total": sum(c["total_cost"] for c in calls if c.get("total_cost") is not None),
            "openrouter_charge": sum(c.get("usage_cost") or 0 for c in calls),
            "provider_charge": sum(c["upstream_cost"] for c in calls if adds_upstream(
                c.get("usage_cost"), c.get("upstream_cost"), True if c.get("is_byok") else None)),
            "missing_calls": sum(c.get("cost_status") == "missing" for c in calls),
            "unknown_calls": sum(c.get("cost_status") == "unknown" for c in calls)}


def execution_cost_report(directory: Path, calls: list[dict[str, Any]]) -> dict[str, Any]:
    """Separate token-price estimates from actual charges, including unknown calls."""
    pricing_file = directory / "pricing_start.json"
    pricing = json.loads(pricing_file.read_text()) if pricing_file.exists() else {}
    catalog = (pricing.get("response_json") or {}).get("data", [])
    prices = {entry["id"]: entry.get("pricing") or {} for entry in (catalog if isinstance(catalog, list) else [])
              if isinstance(entry, dict) and "id" in entry}
    rows = []
    for call in calls:
        intent_path = directory / "calls" / f"{call['call_id']}.intent.json"
        response_path = directory / "calls" / f"{call['call_id']}.response.json"
        intent = json.loads(intent_path.read_text()) if intent_path.exists() else {}
        response = json.loads(response_path.read_text()) if response_path.exists() else {}
        payload = intent.get("payload", {})
        usage = (response.get("response_json") or {}).get("usage")
        usage = usage if isinstance(usage, dict) else {}
        price = prices.get(payload.get("model"), {})
        prompt_price = _price(price.get("prompt"))
        estimated = None
        estimated_tokens = None
        source = None
        if call.get("cost_status") != "known" and prompt_price is not None:
            # Character heuristic is deliberately labeled, never used as actual cost. Missing
            # or null token counts leave that part out of the estimate instead of failing export.
            reported_input = _count(usage.get("prompt_tokens"))
            estimated_tokens = reported_input if reported_input else (len(intent.get("payload_raw", ""))+3)//4
            output = _count(usage.get("completion_tokens")) or 0
            estimated = estimated_tokens * prompt_price + output * (_price(price.get("completion")) or 0.0)
            source = "reported_tokens_start_catalog" if reported_input else "characters_div_four_input_only_start_catalog"
        rows.append({**call, "estimated_cost": estimated, "estimated_input_tokens": estimated_tokens, "estimate_source": source})
    return {**execution_cost(calls), "call_details": rows,
            "estimated_unaccounted_cost": sum(row["estimated_cost"] for row in rows if row["estimated_cost"] is not None)}


def _count(value: Any) -> int | None:
    return int(value) if type(value) in {int, float} and math.isfinite(value) and value >= 0 else None


def _price(value: Any) -> float | None:
    """Catalog prices are numeric strings; anything unparseable is unavailable."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None
