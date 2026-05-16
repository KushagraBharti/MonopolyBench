from __future__ import annotations

import random
from typing import Any


BASELINES = {"first_legal", "random_legal", "pro_heuristic_v1", "haliem_fixed_v1"}


def baseline_action(scenario: dict[str, Any], baseline: str) -> dict[str, Any]:
    if baseline not in BASELINES:
        raise ValueError(f"Unknown baseline '{baseline}'. Expected one of {sorted(BASELINES)}.")
    if baseline in {"pro_heuristic_v1", "haliem_fixed_v1"}:
        return _with_messages(dict(scenario["reference_policy"]["action"]), baseline)
    actions = scenario["decision_point"]["legal_actions"]
    legal = actions[0] if baseline == "first_legal" else random.Random(scenario["scenario_id"]).choice(actions)
    return _with_messages(_minimal_action(scenario["decision_point"], legal["action"]), baseline)


def _minimal_action(decision: dict[str, Any], action_name: str) -> dict[str, Any]:
    args: dict[str, Any] = {}
    if action_name == "bid_auction":
        current = int(decision.get("state", {}).get("auction", {}).get("current_high_bid", 0))
        args = {"bid_amount": current + 1}
    elif action_name in {"mortgage_property", "unmortgage_property"}:
        options = decision.get("post_turn", {}).get("options", {}) | decision.get("liquidation", {}).get("options", {})
        key = "mortgageable_space_indices" if action_name == "mortgage_property" else "unmortgageable_space_indices"
        index = (options.get(key) or [0])[0]
        args = {"space_key": _space_key(decision, index)}
    elif action_name == "build_houses_or_hotel":
        index = (decision.get("post_turn", {}).get("options", {}).get("buildable_space_indices") or [0])[0]
        args = {"build_plan": [{"space_key": _space_key(decision, index), "kind": "HOUSE", "count": 1}]}
    elif action_name == "sell_houses_or_hotel":
        index = (
            decision.get("post_turn", {}).get("options", {}).get("sellable_building_space_indices")
            or decision.get("liquidation", {}).get("options", {}).get("sellable_building_space_indices")
            or [0]
        )[0]
        args = {"sell_plan": [{"space_key": _space_key(decision, index), "kind": "HOUSE", "count": 1}]}
    elif action_name in {"propose_trade", "counter_trade"}:
        bundle = {"cash": 0, "properties": [], "get_out_of_jail_cards": 0}
        args = {"offer": dict(bundle), "request": dict(bundle)}
        if action_name == "propose_trade":
            actor = decision["player_id"]
            target = next(player["player_id"] for player in decision["state"]["players"] if player["player_id"] != actor)
            args["to_player_id"] = target
    elif action_name == "NOOP":
        args = {"reason": "baseline"}
    return {"schema_version": "v1", "decision_id": decision["decision_id"], "action": action_name, "args": args}


def _space_key(decision: dict[str, Any], index: int) -> str:
    name = decision["state"]["board"][index]["name"]
    return str(name).replace(" ", "_").replace(".", "").upper()


def _with_messages(action: dict[str, Any], baseline: str) -> dict[str, Any]:
    action.setdefault("public_message", "")
    action.setdefault("private_thought", f"{baseline} selected this deterministic action.")
    return action
