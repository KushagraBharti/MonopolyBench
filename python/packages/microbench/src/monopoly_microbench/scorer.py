from __future__ import annotations

from typing import Any


def score_action(
    scenario: dict[str, Any],
    action: dict[str, Any],
    *,
    fallback_used: bool = False,
) -> dict[str, Any]:
    if fallback_used:
        return {
            "total": 0.0,
            "label": "invalid",
            "breakdown": [
                {
                    "criterion_id": "fallback",
                    "points": 0.0,
                    "max_points": 1.0,
                    "passed": False,
                    "message": "Fallback outcomes score invalid for benchmark ranking.",
                }
            ],
        }
    breakdown: list[dict[str, Any]] = []
    total = 0.0
    possible = 0.0
    for criterion in scenario["evaluation"]["rubric"]:
        max_points = float(criterion["max_points"])
        possible += max_points
        passed = _criterion_passes(scenario, action, criterion)
        points = max_points if passed else 0.0
        total += points
        breakdown.append(
            {
                "criterion_id": criterion["criterion_id"],
                "points": round(points, 6),
                "max_points": max_points,
                "passed": passed,
                "message": criterion["description"] if passed else f"Did not satisfy: {criterion['description']}",
            }
        )
    normalized = 0.0 if possible <= 0 else round(total / possible, 6)
    label = "preferred" if normalized >= 0.8 else "acceptable" if normalized >= 0.5 else "bad"
    return {"total": normalized, "label": label, "breakdown": breakdown}


def _criterion_passes(scenario: dict[str, Any], action: dict[str, Any], criterion: dict[str, Any]) -> bool:
    kind = criterion["type"]
    params = criterion.get("params", {})
    args = action.get("args", {})
    if kind == "action_name_is":
        return action.get("action") == params.get("action")
    if kind == "action_name_in":
        return action.get("action") in set(params.get("actions", []))
    if kind == "arg_equals":
        return args.get(params.get("key")) == params.get("value")
    if kind == "arg_in_range":
        value = args.get(params.get("key"))
        return isinstance(value, (int, float)) and float(params.get("min", value)) <= value <= float(params.get("max", value))
    if kind in {"bid_at_least", "bid_at_most", "bid_between"}:
        bid = args.get("bid_amount")
        if not isinstance(bid, int):
            return False
        if kind == "bid_at_least":
            return bid >= int(params["min"])
        if kind == "bid_at_most":
            return bid <= int(params["max"])
        return int(params["min"]) <= bid <= int(params["max"])
    if kind == "trade_target_is":
        return args.get("to_player_id") == params.get("player_id")
    if kind == "trade_offer_contains_property":
        return params.get("space_key") in _trade_bundle(args, "offer").get("properties", [])
    if kind == "trade_request_contains_property":
        return params.get("space_key") in _trade_bundle(args, "request").get("properties", [])
    if kind == "trade_offer_cash_between":
        cash = _trade_bundle(args, "offer").get("cash")
        return isinstance(cash, int) and int(params["min"]) <= cash <= int(params["max"])
    if kind == "trade_request_cash_between":
        cash = _trade_bundle(args, "request").get("cash")
        return isinstance(cash, int) and int(params["min"]) <= cash <= int(params["max"])
    if kind == "trade_completes_focal_monopoly":
        return bool(params.get("space_key")) and params["space_key"] in _trade_bundle(args, "request").get("properties", [])
    if kind == "builds_on_group":
        keys = set(params.get("space_keys", []))
        return any(entry.get("space_key") in keys for entry in args.get("build_plan", []))
    if kind == "build_count_between":
        count = sum(int(entry.get("count", 0)) for entry in args.get("build_plan", []))
        return int(params["min"]) <= count <= int(params["max"])
    if kind == "mortgages_space":
        return args.get("space_key") == params.get("space_key")
    if kind == "uses_jail_card":
        return action.get("action") == "use_get_out_of_jail_card"
    if kind == "keeps_cash_above":
        return _cash_after_action(scenario, action) >= int(params["min_cash"])
    if kind == "private_thought_mentions":
        thought = str(action.get("private_thought", "")).lower()
        return any(str(term).lower() in thought for term in params.get("terms", []))
    if kind == "public_message_nonempty":
        return bool(str(action.get("public_message", "")).strip())
    return False


def _trade_bundle(args: dict[str, Any], key: str) -> dict[str, Any]:
    bundle = args.get(key)
    return bundle if isinstance(bundle, dict) else {}


def _cash_after_action(scenario: dict[str, Any], action: dict[str, Any]) -> int:
    state = scenario["decision_point"]["state"]
    player_id = scenario["focal_player_id"]
    cash = next(int(player["cash"]) for player in state["players"] if player["player_id"] == player_id)
    if action["action"] == "buy_property":
        actor = next(player for player in state["players"] if player["player_id"] == player_id)
        index = int(actor.get("position", 0))
        if index is not None:
            cash -= int(state["board"][index].get("price") or 0)
    if action["action"] == "bid_auction":
        cash -= int(action.get("args", {}).get("bid_amount", 0))
    if action["action"] == "pay_jail_fine":
        cash -= 50
    return cash
