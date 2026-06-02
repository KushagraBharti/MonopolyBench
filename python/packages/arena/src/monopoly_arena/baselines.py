from __future__ import annotations

import hashlib
import json
import random
from typing import Any

from monopoly_engine.board import normalize_space_key


BASELINE_RANDOM = "random_legal"
BASELINE_ALWAYS_BUY = "always_buy"
BASELINE_CASH_CONSERVATIVE = "cash_conservative"
BASELINE_NO_TRADE = "no_trade"
BASELINE_BUILDER = "builder"
BASELINE_AUCTION_AGGRESSIVE = "auction_aggressive"

BASELINE_IDS = {
    BASELINE_RANDOM,
    BASELINE_ALWAYS_BUY,
    BASELINE_CASH_CONSERVATIVE,
    BASELINE_NO_TRADE,
    BASELINE_BUILDER,
    BASELINE_AUCTION_AGGRESSIVE,
}


def choose_baseline_action(
    decision: dict[str, Any],
    baseline_id: str,
    *,
    seed_material: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if baseline_id not in BASELINE_IDS:
        raise ValueError(f"Unknown baseline_id '{baseline_id}'.")
    legal = _legal_actions(decision)
    if not legal:
        return _action(decision, "NOOP", {"reason": "no_legal_actions"}, baseline_id)
    if baseline_id == BASELINE_RANDOM:
        rng = random.Random(_deterministic_int({"decision": _decision_seed(decision), "extra": seed_material or {}}))
        action_name = rng.choice(_constructible_actions(decision, legal))
        return _construct_action(decision, action_name, baseline_id, rng=rng)
    if decision.get("decision_type") == "AUCTION_BID_DECISION":
        return _auction_action(decision, baseline_id)
    if decision.get("decision_type") == "TRADE_RESPONSE_DECISION":
        return _trade_response_action(decision, baseline_id)
    if decision.get("decision_type") == "TRADE_PROPOSE_DECISION":
        return _trade_propose_action(decision, baseline_id)
    if decision.get("decision_type") == "LIQUIDATION_DECISION":
        return _liquidation_action(decision, baseline_id)
    if decision.get("decision_type") == "JAIL_DECISION":
        return _jail_action(decision, baseline_id)
    if decision.get("decision_type") == "POST_TURN_ACTION_DECISION":
        return _post_turn_action(decision, baseline_id)
    if "buy_property" in legal and _should_buy_current_property(decision, baseline_id):
        return _action(decision, "buy_property", {}, baseline_id)
    if "start_auction" in legal:
        return _action(decision, "start_auction", {}, baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _auction_action(decision: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    legal = _legal_actions(decision)
    min_bid = _min_next_bid(decision)
    cash = _player_cash(decision)
    if "bid_auction" in legal and min_bid is not None and cash >= min_bid:
        cap = _auction_bid_cap(decision, baseline_id)
        if min_bid <= cap:
            return _action(decision, "bid_auction", {"bid_amount": min(max(min_bid, cap), cash)}, baseline_id)
    if "drop_out" in legal:
        return _action(decision, "drop_out", {}, baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _trade_response_action(decision: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    legal = _legal_actions(decision)
    if baseline_id in {BASELINE_NO_TRADE, BASELINE_CASH_CONSERVATIVE, BASELINE_RANDOM} and "reject_trade" in legal:
        return _action(decision, "reject_trade", {}, baseline_id)
    if "accept_trade" in legal and baseline_id in {BASELINE_ALWAYS_BUY, BASELINE_BUILDER}:
        return _action(decision, "accept_trade", {}, baseline_id)
    if "reject_trade" in legal:
        return _action(decision, "reject_trade", {}, baseline_id)
    if "counter_trade" in legal:
        return _action(decision, "counter_trade", _empty_trade_args(include_player=False), baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _trade_propose_action(decision: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    legal = _legal_actions(decision)
    if "end_turn" in legal and baseline_id in {BASELINE_NO_TRADE, BASELINE_CASH_CONSERVATIVE}:
        return _action(decision, "end_turn", {}, baseline_id)
    if "propose_trade" in legal and baseline_id not in {BASELINE_NO_TRADE, BASELINE_CASH_CONSERVATIVE}:
        target = _first_trade_target(decision)
        if target is not None:
            return _action(decision, "propose_trade", _empty_trade_args(to_player_id=target), baseline_id)
    if "end_turn" in legal:
        return _action(decision, "end_turn", {}, baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _liquidation_action(decision: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    legal = _legal_actions(decision)
    options = _liquidation_options(decision)
    if "mortgage_property" in legal:
        space_key = _first_space_key(decision, options.get("mortgageable_space_indices"))
        if space_key:
            return _action(decision, "mortgage_property", {"space_key": space_key}, baseline_id)
    if "sell_houses_or_hotel" in legal:
        args = _sell_plan_args(decision, options.get("sellable_building_space_indices"))
        if args:
            return _action(decision, "sell_houses_or_hotel", args, baseline_id)
    if "declare_bankruptcy" in legal:
        return _action(decision, "declare_bankruptcy", {}, baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _jail_action(decision: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    legal = _legal_actions(decision)
    player = _player(decision)
    cash = int(player.get("cash") or 0)
    jail_turns = int(player.get("jail_turns") or 0)
    if baseline_id in {BASELINE_BUILDER, BASELINE_ALWAYS_BUY}:
        if "use_get_out_of_jail_card" in legal:
            return _action(decision, "use_get_out_of_jail_card", {}, baseline_id)
        if "pay_jail_fine" in legal and cash >= 250:
            return _action(decision, "pay_jail_fine", {}, baseline_id)
    if jail_turns >= 2 and "pay_jail_fine" in legal and cash >= 50:
        return _action(decision, "pay_jail_fine", {}, baseline_id)
    if "roll_for_doubles" in legal:
        return _action(decision, "roll_for_doubles", {}, baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _post_turn_action(decision: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    legal = _legal_actions(decision)
    options = _post_turn_options(decision)
    if baseline_id == BASELINE_BUILDER and "build_houses_or_hotel" in legal:
        args = _build_plan_args(decision, options.get("buildable_space_indices"))
        if args and _cash_after_build(decision, args) >= 150:
            return _action(decision, "build_houses_or_hotel", args, baseline_id)
    if baseline_id == BASELINE_CASH_CONSERVATIVE and "unmortgage_property" in legal and _player_cash(decision) >= 800:
        space_key = _first_space_key(decision, options.get("unmortgageable_space_indices"))
        if space_key:
            return _action(decision, "unmortgage_property", {"space_key": space_key}, baseline_id)
    if baseline_id not in {BASELINE_NO_TRADE, BASELINE_CASH_CONSERVATIVE} and "propose_trade" in legal:
        target = _first_trade_target(decision)
        if target is not None and baseline_id == BASELINE_BUILDER:
            return _action(decision, "propose_trade", _empty_trade_args(to_player_id=target), baseline_id)
    if "end_turn" in legal:
        return _action(decision, "end_turn", {}, baseline_id)
    return _construct_action(decision, legal[0], baseline_id)


def _construct_action(
    decision: dict[str, Any],
    action_name: str,
    baseline_id: str,
    *,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    if action_name == "bid_auction":
        min_bid = _min_next_bid(decision) or 0
        cash = _player_cash(decision)
        bid = min(cash, min_bid + ((rng.randint(0, 25) if rng is not None and cash > min_bid else 0)))
        return _action(decision, action_name, {"bid_amount": max(min_bid, bid)}, baseline_id)
    if action_name in {"mortgage_property", "unmortgage_property"}:
        options = _liquidation_options(decision) if decision.get("decision_type") == "LIQUIDATION_DECISION" else _post_turn_options(decision)
        key_name = "mortgageable_space_indices" if action_name == "mortgage_property" else "unmortgageable_space_indices"
        space_key = _first_space_key(decision, options.get(key_name))
        return _action(decision, action_name, {"space_key": space_key or ""}, baseline_id)
    if action_name == "build_houses_or_hotel":
        return _action(decision, action_name, _build_plan_args(decision, _post_turn_options(decision).get("buildable_space_indices")) or {"build_plan": []}, baseline_id)
    if action_name == "sell_houses_or_hotel":
        options = _liquidation_options(decision) if decision.get("decision_type") == "LIQUIDATION_DECISION" else _post_turn_options(decision)
        return _action(decision, action_name, _sell_plan_args(decision, options.get("sellable_building_space_indices")) or {"sell_plan": []}, baseline_id)
    if action_name == "propose_trade":
        target = _first_trade_target(decision) or _first_other_player_id(decision)
        return _action(decision, action_name, _empty_trade_args(to_player_id=target or ""), baseline_id)
    if action_name == "counter_trade":
        return _action(decision, action_name, _empty_trade_args(include_player=False), baseline_id)
    if action_name == "NOOP":
        return _action(decision, action_name, {"reason": "baseline_noop"}, baseline_id)
    return _action(decision, action_name, {}, baseline_id)


def _constructible_actions(decision: dict[str, Any], legal: list[str]) -> list[str]:
    constructible: list[str] = []
    for action_name in legal:
        if action_name == "bid_auction" and (_min_next_bid(decision) is None or _player_cash(decision) < (_min_next_bid(decision) or 0)):
            continue
        if action_name in {"mortgage_property", "unmortgage_property"} and not _has_space_arg(decision, action_name):
            continue
        if action_name == "build_houses_or_hotel" and not _build_plan_args(decision, _post_turn_options(decision).get("buildable_space_indices")):
            continue
        if action_name == "sell_houses_or_hotel":
            options = _liquidation_options(decision) if decision.get("decision_type") == "LIQUIDATION_DECISION" else _post_turn_options(decision)
            if not _sell_plan_args(decision, options.get("sellable_building_space_indices")):
                continue
        if action_name == "propose_trade" and (_first_trade_target(decision) is None and _first_other_player_id(decision) is None):
            continue
        constructible.append(action_name)
    return constructible or legal


def _should_buy_current_property(decision: dict[str, Any], baseline_id: str) -> bool:
    cash = _player_cash(decision)
    price = int((_current_space(decision) or {}).get("price") or 0)
    if price <= 0 or cash < price:
        return False
    if baseline_id in {BASELINE_ALWAYS_BUY, BASELINE_BUILDER, BASELINE_AUCTION_AGGRESSIVE}:
        return True
    if baseline_id == BASELINE_CASH_CONSERVATIVE:
        return cash - price >= 300
    if baseline_id == BASELINE_NO_TRADE:
        return cash - price >= 150
    return True


def _auction_bid_cap(decision: dict[str, Any], baseline_id: str) -> int:
    cash = _player_cash(decision)
    price = int((_auction_space(decision) or {}).get("price") or 100)
    if baseline_id == BASELINE_AUCTION_AGGRESSIVE:
        return min(cash, int(price * 1.25))
    if baseline_id == BASELINE_ALWAYS_BUY:
        return min(cash, price)
    if baseline_id == BASELINE_BUILDER:
        return min(cash, int(price * 0.9))
    if baseline_id == BASELINE_CASH_CONSERVATIVE:
        return max(0, min(cash - 300, int(price * 0.55)))
    return max(0, min(cash - 150, int(price * 0.7)))


def _action(decision: dict[str, Any], action_name: str, args: dict[str, Any], baseline_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "decision_id": decision["decision_id"],
        "action": action_name,
        "args": args,
        "public_message": "",
        "private_thought": f"Deterministic baseline '{baseline_id}' selected {action_name}.",
    }


def _legal_actions(decision: dict[str, Any]) -> list[str]:
    return [str(entry["action"]) for entry in decision.get("legal_actions", []) if entry.get("action")]


def _player(decision: dict[str, Any]) -> dict[str, Any]:
    player_id = decision.get("player_id")
    for player in decision.get("state", {}).get("players", []):
        if isinstance(player, dict) and player.get("player_id") == player_id:
            return player
    return {}


def _player_cash(decision: dict[str, Any]) -> int:
    return int(_player(decision).get("cash") or 0)


def _current_space(decision: dict[str, Any]) -> dict[str, Any] | None:
    position = _player(decision).get("position")
    for space in decision.get("state", {}).get("board", []):
        if isinstance(space, dict) and space.get("index") == position:
            return space
    return None


def _auction_space(decision: dict[str, Any]) -> dict[str, Any] | None:
    auction = decision.get("state", {}).get("auction")
    if not isinstance(auction, dict):
        return None
    key = auction.get("property_space_key")
    for space in decision.get("state", {}).get("board", []):
        if isinstance(space, dict) and _space_key(space) == key:
            return space
    return None


def _min_next_bid(decision: dict[str, Any]) -> int | None:
    auction = decision.get("state", {}).get("auction")
    if not isinstance(auction, dict):
        return None
    return int(auction.get("current_high_bid") or 0) + 1


def _post_turn_options(decision: dict[str, Any]) -> dict[str, Any]:
    post_turn = decision.get("post_turn")
    options = post_turn.get("options") if isinstance(post_turn, dict) else None
    return options if isinstance(options, dict) else {}


def _liquidation_options(decision: dict[str, Any]) -> dict[str, Any]:
    liquidation = decision.get("liquidation")
    options = liquidation.get("options") if isinstance(liquidation, dict) else None
    return options if isinstance(options, dict) else {}


def _first_space_key(decision: dict[str, Any], indices: Any) -> str | None:
    if not isinstance(indices, list) or not indices:
        return None
    target = indices[0]
    for space in decision.get("state", {}).get("board", []):
        if isinstance(space, dict) and space.get("index") == target:
            return _space_key(space)
    return None


def _space_key(space: dict[str, Any]) -> str:
    return normalize_space_key(str(space.get("name") or ""))


def _build_plan_args(decision: dict[str, Any], indices: Any) -> dict[str, Any] | None:
    space_key = _first_space_key(decision, indices)
    if space_key is None:
        return None
    space = _space_by_key(decision, space_key)
    houses = int((space or {}).get("houses") or 0)
    kind = "HOTEL" if houses >= 4 else "HOUSE"
    return {"build_plan": [{"space_key": space_key, "kind": kind, "count": 1}]}


def _sell_plan_args(decision: dict[str, Any], indices: Any) -> dict[str, Any] | None:
    space_key = _first_space_key(decision, indices)
    if space_key is None:
        return None
    space = _space_by_key(decision, space_key)
    kind = "HOTEL" if bool((space or {}).get("hotel")) else "HOUSE"
    return {"sell_plan": [{"space_key": space_key, "kind": kind, "count": 1}]}


def _cash_after_build(decision: dict[str, Any], args: dict[str, Any]) -> int:
    cash = _player_cash(decision)
    for item in args.get("build_plan", []):
        if not isinstance(item, dict):
            continue
        space = _space_by_key(decision, str(item.get("space_key") or ""))
        if not space:
            continue
        group = space.get("group")
        cost = _house_cost(str(group)) if group else 0
        cash -= cost * int(item.get("count") or 0)
    return cash


def _house_cost(group: str) -> int:
    if group in {"BROWN", "LIGHT_BLUE"}:
        return 50
    if group in {"PINK", "ORANGE"}:
        return 100
    if group in {"RED", "YELLOW"}:
        return 150
    if group in {"GREEN", "DARK_BLUE"}:
        return 200
    return 0


def _space_by_key(decision: dict[str, Any], space_key: str) -> dict[str, Any] | None:
    for space in decision.get("state", {}).get("board", []):
        if isinstance(space, dict) and _space_key(space) == space_key:
            return space
    return None


def _has_space_arg(decision: dict[str, Any], action_name: str) -> bool:
    options = _liquidation_options(decision) if decision.get("decision_type") == "LIQUIDATION_DECISION" else _post_turn_options(decision)
    key_name = "mortgageable_space_indices" if action_name == "mortgage_property" else "unmortgageable_space_indices"
    return _first_space_key(decision, options.get(key_name)) is not None


def _first_trade_target(decision: dict[str, Any]) -> str | None:
    options = _post_turn_options(decision)
    targets = options.get("can_trade_with")
    if isinstance(targets, list) and targets:
        return str(targets[0])
    return _first_other_player_id(decision)


def _first_other_player_id(decision: dict[str, Any]) -> str | None:
    player_id = decision.get("player_id")
    for player in decision.get("state", {}).get("players", []):
        if isinstance(player, dict) and player.get("player_id") != player_id and not player.get("bankrupt"):
            return str(player.get("player_id"))
    return None


def _empty_trade_args(*, to_player_id: str | None = None, include_player: bool = True) -> dict[str, Any]:
    args: dict[str, Any] = {
        "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
        "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
    }
    if include_player:
        args["to_player_id"] = to_player_id
    return args


def _decision_seed(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": decision.get("run_id"),
        "turn_index": decision.get("turn_index"),
        "decision_id": decision.get("decision_id"),
        "player_id": decision.get("player_id"),
        "decision_type": decision.get("decision_type"),
        "legal_actions": _legal_actions(decision),
    }


def _deterministic_int(payload: dict[str, Any]) -> int:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
