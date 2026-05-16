from __future__ import annotations

import copy
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from monopoly_engine.board import (
    GROUP_INDEXES,
    HOUSE_COST_BY_GROUP,
    OWNABLE_KINDS,
    PROPERTY_RENT_TABLES,
    RAILROAD_RENTS,
    SPACE_INDEX_BY_KEY,
    SPACE_KEY_BY_INDEX,
    UTILITY_RENT_MULTIPLIER,
)

from .player_config import DEFAULT_SYSTEM_PROMPT, PlayerConfig


PROMPT_SCHEMA_VERSION = "v2"
JAIL_FINE = 50

def build_space_key_by_index() -> dict[int, str]:
    return dict(SPACE_KEY_BY_INDEX)


SPACE_KEY_BY_INDEX_LOOKUP = build_space_key_by_index()


def space_key_for_index(space_index: int, mapping: dict[int, str]) -> str:
    return mapping.get(space_index, f"SPACE_{space_index}")


@dataclass(slots=True)
class PromptBundle:
    system_prompt: str
    user_payload: dict[str, Any]
    user_content: str
    messages: list[dict[str, Any]]


class PromptMemory:
    def __init__(
        self,
        *,
        space_key_by_index: dict[int, str] | None = None,
        public_chat_limit: int = 20,
        recent_actions_limit: int = 20,
        private_thought_limit: int = 10,
    ) -> None:
        self._space_key_by_index = space_key_by_index or SPACE_KEY_BY_INDEX_LOOKUP
        self._public_timeline: deque[dict[str, Any]] = deque(maxlen=max(public_chat_limit, recent_actions_limit))
        self._pending_messages_by_decision: dict[str, dict[str, Any]] = {}
        self._pending_messages_by_player: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
        self._private_thoughts: dict[str, deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=private_thought_limit)
        )

    def update(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")
        payload = event.get("payload", {})
        turn_index = event.get("turn_index")
        if event_type == "LLM_DECISION_RESPONSE":
            decision_id = payload.get("decision_id")
            player_id = payload.get("player_id")
            action_name = payload.get("action_name")
            if isinstance(decision_id, str) and isinstance(player_id, str) and isinstance(action_name, str):
                self._pending_messages_by_decision[decision_id] = {
                    "turn_index": turn_index,
                    "player_id": player_id,
                    "action_name": action_name,
                    "message": None,
                }
            return
        if event_type == "LLM_PUBLIC_MESSAGE":
            self._track_public_message(turn_index, payload)
            return
        if event_type == "LLM_PRIVATE_THOUGHT":
            player_id = payload.get("player_id")
            if player_id:
                self._private_thoughts[player_id].append(
                    {
                        "turn_index": turn_index,
                        "thought": payload.get("thought"),
                    }
                )
            return

        pending = self._claim_pending_message(event)
        summary = _summarize_action_event(event, self._space_key_by_index, pending=pending)
        if summary is not None:
            self._append_or_merge_summary(summary)

    def snapshot_for_player(self, player_id: str) -> dict[str, Any]:
        return {
            "public_timeline_last_20": list(self._public_timeline),
            "your_private_thoughts_last_10": list(self._private_thoughts.get(player_id, [])),
        }

    def _track_public_message(self, turn_index: int | None, payload: dict[str, Any]) -> None:
        decision_id = payload.get("decision_id")
        player_id = payload.get("player_id")
        if not isinstance(player_id, str):
            return
        pending = None
        if isinstance(decision_id, str):
            pending = self._pending_messages_by_decision.pop(decision_id, None)
        if pending is None:
            pending = {
                "turn_index": turn_index,
                "player_id": player_id,
                "action_name": None,
                "message": None,
            }
        message = payload.get("message")
        pending["message"] = message if isinstance(message, str) and message.strip() else None
        self._pending_messages_by_player[player_id].append(pending)

    def _claim_pending_message(self, event: dict[str, Any]) -> dict[str, Any] | None:
        event_type = event.get("type")
        if event_type == "TURN_ENDED":
            for queue in self._pending_messages_by_player.values():
                for pending in list(queue):
                    if pending.get("action_name") == "end_turn":
                        queue.remove(pending)
                        return pending
        candidate_player_ids = _candidate_player_ids_for_event(event)
        for player_id in candidate_player_ids:
            pending_queue = self._pending_messages_by_player.get(player_id)
            if not pending_queue:
                continue
            for pending in list(pending_queue):
                action_name = pending.get("action_name")
                if _is_primary_event_for_action(action_name, event_type):
                    pending_queue.remove(pending)
                    return pending
        return None

    def _append_or_merge_summary(self, summary: dict[str, Any]) -> None:
        if self._public_timeline and _can_merge_timeline_items(self._public_timeline[-1], summary):
            previous = self._public_timeline[-1]
            previous["action"] = _merge_action_text(str(previous["action"]), str(summary["action"]))
            if previous.get("message") is None and summary.get("message") is not None:
                previous["message"] = summary["message"]
            return
        self._public_timeline.append(summary)


PRIMARY_EVENT_BY_ACTION = {
    "buy_property": {"PROPERTY_PURCHASED"},
    "start_auction": {"AUCTION_STARTED"},
    "bid_auction": {"AUCTION_BID_PLACED"},
    "drop_out": {"AUCTION_PLAYER_DROPPED"},
    "propose_trade": {"TRADE_PROPOSED"},
    "accept_trade": {"TRADE_ACCEPTED"},
    "reject_trade": {"TRADE_REJECTED"},
    "counter_trade": {"TRADE_COUNTERED"},
    "mortgage_property": {"PROPERTY_MORTGAGED"},
    "unmortgage_property": {"PROPERTY_UNMORTGAGED"},
    "build_houses_or_hotel": {"HOUSE_BUILT", "HOTEL_BUILT"},
    "sell_houses_or_hotel": {"HOUSE_SOLD", "HOTEL_SOLD"},
    "declare_bankruptcy": {"CASH_CHANGED"},
    "pay_jail_fine": {"CASH_CHANGED"},
    "use_get_out_of_jail_card": {"DICE_ROLLED"},
    "roll_for_doubles": {"DICE_ROLLED"},
    "end_turn": {"TURN_ENDED"},
}


def _is_primary_event_for_action(action_name: Any, event_type: Any) -> bool:
    if not isinstance(action_name, str) or not isinstance(event_type, str):
        return False
    return event_type in PRIMARY_EVENT_BY_ACTION.get(action_name, set())


def _candidate_player_ids_for_event(event: dict[str, Any]) -> list[str]:
    payload = event.get("payload", {})
    actor = event.get("actor", {})
    player_ids = [
        payload.get("player_id"),
        payload.get("from_player_id"),
        payload.get("bidder_player_id"),
        payload.get("initiator_player_id"),
        payload.get("counterparty_player_id"),
        actor.get("player_id") if isinstance(actor, dict) else None,
    ]
    return [player_id for player_id in player_ids if isinstance(player_id, str)]


def _format_money(amount: Any) -> str:
    if isinstance(amount, int):
        return f"${amount}"
    return "$?"


def _format_signed_money(delta: Any) -> str:
    if isinstance(delta, int):
        prefix = "+" if delta >= 0 else "-"
        return f"{prefix}${abs(delta)}"
    return "$?"


def _message_from_pending(pending: dict[str, Any] | None) -> str | None:
    if not pending:
        return None
    message = pending.get("message")
    return message if isinstance(message, str) and message.strip() else None


def _timeline_item(
    *,
    turn_index: Any,
    player_id: Any,
    event_type: str,
    action: str,
    pending: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "turn_index": turn_index,
        "player_id": player_id,
        "event_type": event_type,
        "action": action,
        "message": _message_from_pending(pending),
    }


def _space_key_from_payload(payload: dict[str, Any], space_key_by_index: dict[int, str]) -> str | None:
    space_key = payload.get("property_space")
    if isinstance(space_key, str):
        return space_key
    space_index = payload.get("space_index")
    return space_key_for_index(int(space_index), space_key_by_index) if space_index is not None else None


def _trade_bundle_text(bundle: Any) -> str:
    if not isinstance(bundle, dict):
        return "nothing"
    parts: list[str] = []
    cash = bundle.get("cash", 0)
    if isinstance(cash, int) and cash:
        parts.append(_format_money(cash))
    properties = bundle.get("properties", [])
    if isinstance(properties, list) and properties:
        parts.append(", ".join(str(item) for item in properties))
    jail_cards = bundle.get("get_out_of_jail_cards", 0)
    if isinstance(jail_cards, int) and jail_cards:
        label = "Get Out of Jail Free card" if jail_cards == 1 else "Get Out of Jail Free cards"
        parts.append(f"{jail_cards} {label}")
    return " + ".join(parts) if parts else "nothing"


def _trade_action_text(verb: str, payload: dict[str, Any]) -> str:
    initiator = payload.get("initiator_player_id")
    counterparty = payload.get("counterparty_player_id")
    offer = _trade_bundle_text(payload.get("offer"))
    request = _trade_bundle_text(payload.get("request"))
    if verb == "accepted":
        return f"accepted trade with {initiator}: {initiator} gives {offer}; {counterparty} gives {request}"
    if verb == "rejected":
        return f"rejected trade with {initiator}: {initiator} offered {offer} for {request}"
    if verb == "countered":
        return f"countered trade with {counterparty}: offer {offer}; request {request}"
    return f"proposed trade to {counterparty}: offer {offer}; request {request}"


def _building_action_fragment(event_type: str, count: Any, space_key: str | None) -> str:
    safe_count = count if isinstance(count, int) else "?"
    building = "hotel" if "HOTEL" in event_type else "house"
    if safe_count != 1:
        building += "s"
    verb = "built" if event_type in {"HOUSE_BUILT", "HOTEL_BUILT"} else "sold"
    return f"{verb} {safe_count} {building} on {space_key}"


def _can_merge_timeline_items(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    mergeable = {
        ("BUILDINGS_BUILT", "BUILDINGS_BUILT"),
        ("BUILDINGS_SOLD", "BUILDINGS_SOLD"),
    }
    return (
        (previous.get("event_type"), current.get("event_type")) in mergeable
        and previous.get("turn_index") == current.get("turn_index")
        and previous.get("player_id") == current.get("player_id")
    )


def _merge_action_text(previous: str, current: str) -> str:
    if " and " in previous:
        return f"{previous}, and {current}"
    return f"{previous} and {current}"


def _summarize_action_event(
    event: dict[str, Any],
    space_key_by_index: dict[int, str],
    *,
    pending: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    event_type = event.get("type")
    payload = event.get("payload", {})
    turn_index = event.get("turn_index")
    if event_type == "PROPERTY_PURCHASED":
        space_key = _space_key_from_payload(payload, space_key_by_index)
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="PROPERTY_PURCHASED",
            action=f"bought {space_key} for {_format_money(payload.get('price'))}",
            pending=pending,
        )
    if event_type == "RENT_PAID":
        space_key = _space_key_from_payload(payload, space_key_by_index)
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("from_player_id"),
            event_type="RENT_PAID",
            action=(
                f"paid {_format_money(payload.get('amount'))} rent to "
                f"{payload.get('to_player_id')} on {space_key}"
            ),
            pending=pending,
        )
    if event_type == "SENT_TO_JAIL":
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="SENT_TO_JAIL",
            action=f"was sent to jail ({payload.get('reason')})",
            pending=pending,
        )
    if event_type == "DICE_ROLLED":
        if pending is None:
            return None
        d1 = payload.get("d1")
        d2 = payload.get("d2")
        roll = f"{d1}+{d2}"
        suffix = " and rolled doubles" if payload.get("is_double") else ""
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id") or event.get("actor", {}).get("player_id"),
            event_type="DICE_ROLLED",
            action=f"rolled {roll}{suffix}",
            pending=pending,
        )
    if event_type == "AUCTION_STARTED":
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("initiator_player_id"),
            event_type="AUCTION_STARTED",
            action=f"started auction for {payload.get('property_space')}",
            pending=pending,
        )
    if event_type == "AUCTION_BID_PLACED":
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("bidder_player_id"),
            event_type="AUCTION_BID_PLACED",
            action=f"bid {_format_money(payload.get('bid_amount'))} on {payload.get('property_space')}",
            pending=pending,
        )
    if event_type == "AUCTION_PLAYER_DROPPED":
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="AUCTION_PLAYER_DROPPED",
            action=f"dropped out of auction for {payload.get('property_space')}",
            pending=pending,
        )
    if event_type == "AUCTION_ENDED":
        winner_id = payload.get("winner_player_id")
        if winner_id is None:
            action = f"auction for {payload.get('property_space')} ended with no winner ({payload.get('reason')})"
        else:
            action = (
                f"auction for {payload.get('property_space')} ended: "
                f"{winner_id} won for {_format_money(payload.get('winning_bid'))}"
            )
        return _timeline_item(
            turn_index=turn_index,
            player_id=winner_id,
            event_type="AUCTION_ENDED",
            action=action,
            pending=pending,
        )
    if event_type in {"TRADE_PROPOSED", "TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED"}:
        verb_by_event = {
            "TRADE_PROPOSED": "proposed",
            "TRADE_COUNTERED": "countered",
            "TRADE_ACCEPTED": "accepted",
            "TRADE_REJECTED": "rejected",
        }
        player_id = payload.get("initiator_player_id")
        if event_type in {"TRADE_ACCEPTED", "TRADE_REJECTED", "TRADE_COUNTERED"} and pending:
            player_id = pending.get("player_id")
        return _timeline_item(
            turn_index=turn_index,
            player_id=player_id,
            event_type=event_type,
            action=_trade_action_text(verb_by_event[event_type], payload),
            pending=pending,
        )
    if event_type == "TRADE_EXPIRED":
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("counterparty_player_id"),
            event_type="TRADE_EXPIRED",
            action=f"trade expired ({payload.get('reason')})",
            pending=pending,
        )
    if event_type == "PROPERTY_MORTGAGED":
        space_key = _space_key_from_payload(payload, space_key_by_index)
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="PROPERTY_MORTGAGED",
            action=f"mortgaged {space_key} for {_format_money(payload.get('amount'))}",
            pending=pending,
        )
    if event_type == "PROPERTY_UNMORTGAGED":
        space_key = _space_key_from_payload(payload, space_key_by_index)
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="PROPERTY_UNMORTGAGED",
            action=f"unmortgaged {space_key} for {_format_money(payload.get('amount'))}",
            pending=pending,
        )
    if event_type in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
        space_key = _space_key_from_payload(payload, space_key_by_index)
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="BUILDINGS_BUILT" if event_type in {"HOUSE_BUILT", "HOTEL_BUILT"} else "BUILDINGS_SOLD",
            action=_building_action_fragment(event_type, payload.get("count"), space_key),
            pending=pending,
        )
    if event_type == "TURN_ENDED":
        if pending is None or _message_from_pending(pending) is None:
            return None
        return _timeline_item(
            turn_index=turn_index,
            player_id=pending.get("player_id"),
            event_type="TURN_ENDED",
            action="ended turn",
            pending=pending,
        )
    if event_type == "CASH_CHANGED":
        reason = payload.get("reason")
        if reason == "JAIL_FINE":
            action = f"paid {_format_money(abs(payload.get('delta', JAIL_FINE)))} to leave jail"
        elif reason == "PASS_GO":
            action = f"collected {_format_money(payload.get('delta'))} for passing GO"
        elif reason == "TAX_INCOME":
            action = "paid $200 income tax"
        elif reason == "TAX_LUXURY":
            action = "paid $100 luxury tax"
        elif reason == "BANKRUPTCY":
            action = "declared bankruptcy"
        elif reason == "BANKRUPTCY_ASSETS_TO_BANK":
            action = "returned assets to the bank after bankruptcy"
        else:
            return None
        return _timeline_item(
            turn_index=turn_index,
            player_id=payload.get("player_id"),
            event_type="CASH_CHANGED",
            action=action,
            pending=pending,
        )
    return None


def build_system_prompt(player: PlayerConfig) -> str:
    if player.system_prompt:
        return player.system_prompt
    return DEFAULT_SYSTEM_PROMPT


def build_full_state(
    snapshot: dict[str, Any],
    *,
    you_player_id: str,
    memory: PromptMemory,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    players = snapshot.get("players", [])
    if len(players) != 4:
        raise ValueError("Exactly 4 players are required for LLM prompts.")
    board = snapshot.get("board", [])
    player_lookup = {player.get("player_id"): player for player in players}
    you_player = player_lookup.get(you_player_id) or player_lookup.get(snapshot.get("active_player_id"))
    if you_player is None:
        you_player = players[0]

    def build_holdings(player_id: str) -> dict[str, Any]:
        owned: list[dict[str, Any]] = []
        mortgaged: list[dict[str, Any]] = []
        for space in board:
            if space.get("owner_id") != player_id:
                continue
            space_index = int(space.get("index", 0))
            space_key = space_key_for_index(space_index, space_key_by_index)
            mortgaged_flag = bool(space.get("mortgaged"))
            owned.append(
                {
                    "space_key": space_key,
                    "houses": int(space.get("houses", 0)),
                    "hotel": bool(space.get("hotel", False)),
                    "mortgaged": mortgaged_flag,
                }
            )
            if mortgaged_flag:
                mortgaged.append({"space_key": space_key})
        return {"owned": owned, "mortgaged": mortgaged}

    def build_player_view(player: dict[str, Any]) -> dict[str, Any]:
        position_index = int(player.get("position", 0))
        return {
            "player_id": player.get("player_id"),
            "name": player.get("name"),
            "cash": player.get("cash"),
            "position": space_key_for_index(position_index, space_key_by_index),
            "in_jail": bool(player.get("in_jail")),
            "holdings": build_holdings(str(player.get("player_id"))),
            "get_out_of_jail_cards": int(player.get("get_out_of_jail_cards", 0)),
        }

    you_view = build_player_view(you_player)
    others = [
        build_player_view(player)
        for player in players
        if player.get("player_id") != you_player.get("player_id")
    ]
    if len(others) != 3:
        raise ValueError("Expected exactly 3 other players for LLM prompts.")

    unowned_space_keys = [
        space_key_for_index(int(space.get("index", 0)), space_key_by_index)
        for space in board
        if space.get("kind") in OWNABLE_KINDS and space.get("owner_id") is None
    ]

    return {
        "title": "game_state",
        "metadata": {
            "turn_index": snapshot.get("turn_index"),
            "you_player_id": you_player.get("player_id"),
        },
        "you": you_view,
        "others": others,
        "bank": {
            "houses_remaining": snapshot.get("bank", {}).get("houses_remaining"),
            "hotels_remaining": snapshot.get("bank", {}).get("hotels_remaining"),
            "unowned_space_keys": unowned_space_keys,
        },
        "memory": memory.snapshot_for_player(str(you_player.get("player_id"))),
    }


def _augment_args_schema(args_schema: dict[str, Any] | None, *, include_private_thought: bool = True) -> dict[str, Any]:
    schema = copy.deepcopy(args_schema or {"type": "object", "additionalProperties": False})
    schema.setdefault("type", "object")
    schema.setdefault("additionalProperties", False)
    properties = schema.setdefault("properties", {})
    if isinstance(properties, dict):
        properties.setdefault("public_message", {"type": "string"})
        if include_private_thought:
            properties.setdefault("private_thought", {"type": "string"})
        else:
            properties.pop("private_thought", None)
    required = schema.setdefault("required", [])
    if isinstance(required, list):
        if "public_message" not in required:
            required.append("public_message")
        if include_private_thought and "private_thought" not in required:
            required.append("private_thought")
        if not include_private_thought and "private_thought" in required:
            required.remove("private_thought")
    return schema


def build_compact_decision(decision: dict[str, Any]) -> dict[str, Any]:
    legal_actions = []
    include_private_thought = decision.get("micro_prompt_condition") != "no_private_thought"
    for entry in decision.get("legal_actions", []):
        action_name = entry.get("action")
        if not action_name:
            continue
        args_schema = _augment_args_schema(entry.get("args_schema") or {}, include_private_thought=include_private_thought)
        legal_actions.append(
            {
                "action": action_name,
                "args_schema": args_schema,
            }
        )
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "player_id": decision.get("player_id"),
        "legal_actions": legal_actions,
    }


def build_openrouter_tools(decision_payload: dict[str, Any]) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for entry in decision_payload.get("legal_actions", []):
        action_name = entry.get("action")
        if not action_name:
            continue
        args_schema = copy.deepcopy(entry.get("args_schema") or {})
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": action_name,
                    "description": _describe_action(action_name),
                    "parameters": args_schema,
                },
            }
        )
    return tools


def _describe_action(action_name: str) -> str:
    descriptions = {
        "buy_property": "Buy the property at the current space.",
        "start_auction": "Decline purchase and start an auction for the current space.",
        "bid_auction": "Place a bid in the current auction.",
        "drop_out": "Drop out of the current auction.",
        "propose_trade": "Propose a trade to another player.",
        "accept_trade": "Accept the current trade offer.",
        "reject_trade": "Reject the current trade offer.",
        "counter_trade": "Counter the current trade offer.",
        "ROLL_DICE": "Roll the dice to start your move.",
        "roll_for_doubles": "Roll for doubles to attempt to leave jail.",
        "pay_jail_fine": "Pay the jail fine to leave jail.",
        "use_get_out_of_jail_card": "Use a Get Out of Jail Free card.",
        "end_turn": "End your turn.",
        "mortgage_property": "Mortgage a property you own.",
        "unmortgage_property": "Unmortgage a property you own.",
        "build_houses_or_hotel": "Build houses or a hotel on your monopolies.",
        "sell_houses_or_hotel": "Sell houses or a hotel from your monopolies.",
        "declare_bankruptcy": "Declare bankruptcy when you cannot pay.",
        "NOOP": "Take no action.",
    }
    return descriptions.get(action_name, f"Take the {action_name} action.")


def build_action_state(
    decision: dict[str, Any],
    decision_focus: dict[str, Any],
) -> dict[str, Any]:
    action_state: dict[str, Any] = {
        "title": "action_state",
        "decision_type": decision.get("decision_type"),
        "actor_player_id": decision.get("player_id"),
    }
    scenario = decision_focus.get("scenario")
    if isinstance(scenario, dict):
        action_state["scenario"] = scenario
    else:
        for key, value in decision_focus.items():
            if key in {"schema_version", "decision_id", "decision_type", "actor_player_id", "legal_tools"}:
                continue
            action_state[key] = value
    action_state["available_actions"] = [
        entry.get("action")
        for entry in decision.get("legal_actions", [])
        if entry.get("action")
    ]
    prompt_condition = decision.get("micro_prompt_condition")
    if isinstance(prompt_condition, str) and prompt_condition != "live_game":
        action_state["prompt_condition"] = prompt_condition
    return action_state


def build_decision_focus(
    decision: dict[str, Any],
    *,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    decision_type = decision.get("decision_type")
    if decision_type == "BUY_OR_AUCTION_DECISION":
        return build_buy_or_auction_decision_focus(decision, space_key_by_index=space_key_by_index)
    # TODO: expand focus payloads when engine emits richer decision contexts.
    if decision_type == "JAIL_DECISION":
        return build_jail_decision_focus(decision, space_key_by_index=space_key_by_index)
    if decision_type == "POST_TURN_ACTION_DECISION":
        return build_post_turn_action_decision_focus(decision, space_key_by_index=space_key_by_index)
    if decision_type == "LIQUIDATION_DECISION":
        return build_liquidation_decision_focus(decision, space_key_by_index=space_key_by_index)
    if decision_type == "AUCTION_BID_DECISION":
        return build_auction_bid_decision_focus(decision, space_key_by_index=space_key_by_index)
    if decision_type == "TRADE_PROPOSE_DECISION":
        return build_trade_propose_decision_focus(decision)
    if decision_type == "TRADE_RESPONSE_DECISION":
        return build_trade_response_decision_focus(decision)
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "focus_type": "UNKNOWN_DECISION_FOCUS",
        "notes": [f"Unsupported decision_type: {decision_type}"],
    }


def _build_legal_tools(decision: dict[str, Any], *, include_args: bool) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for entry in decision.get("legal_actions", []):
        tool_name = entry.get("action")
        if not tool_name:
            continue
        tool: dict[str, Any] = {
            "tool_name": tool_name,
            "requires": ["public_message", "private_thought"],
        }
        if include_args:
            tool["args"] = {}
        tools.append(tool)
    return tools


def _rent_summary(space_kind: str | None, space_index: int) -> list[int]:
    if space_kind == "PROPERTY":
        return PROPERTY_RENT_TABLES.get(space_index, [])
    if space_kind == "RAILROAD":
        return list(RAILROAD_RENTS)
    if space_kind == "UTILITY":
        return [UTILITY_RENT_MULTIPLIER[key] for key in sorted(UTILITY_RENT_MULTIPLIER)]
    return []


def _group_progress(board: list[dict[str, Any]], player_id: str | None, group: str | None) -> dict[str, int]:
    if not group or not player_id:
        return {"you_own_in_group": 0, "total_in_group": 0}
    indices = GROUP_INDEXES.get(group, [])
    if not indices:
        return {"you_own_in_group": 0, "total_in_group": 0}
    board_by_index = {int(space.get("index", 0)): space for space in board}
    owned = sum(
        1 for index in indices if board_by_index.get(index, {}).get("owner_id") == player_id
    )
    return {"you_own_in_group": owned, "total_in_group": len(indices)}


def build_buy_or_auction_decision_focus(
    decision: dict[str, Any],
    *,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    state = decision.get("state", {})
    board = state.get("board", [])
    active_player_id = decision.get("player_id")
    active_player: dict[str, Any] = next(
        (player for player in state.get("players", []) if player.get("player_id") == active_player_id),
        {},
    )
    position_index = int(active_player.get("position", 0))
    landed_space = next((space for space in board if space.get("index") == position_index), None)
    if landed_space is None:
        landed_space = {"index": position_index}
    space_kind = landed_space.get("kind")
    raw_group = landed_space.get("group")
    group = str(raw_group) if raw_group is not None else None
    rent = _rent_summary(space_kind, position_index)
    house_cost = HOUSE_COST_BY_GROUP.get(group, 0) if space_kind == "PROPERTY" and group else 0
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": active_player_id,
        "scenario": {
            "landed_space": space_key_for_index(position_index, space_key_by_index),
            "space_kind": space_kind,
            "group": group,
            "price": landed_space.get("price"),
            "house_cost": house_cost,
            "rent": rent,
            "group_progress": _group_progress(board, active_player_id, group),
        },
        "legal_tools": _build_legal_tools(decision, include_args=True),
    }


def build_jail_decision_focus(
    decision: dict[str, Any],
    *,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    tool_names = {entry.get("action") for entry in decision.get("legal_actions", [])}
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": decision.get("player_id"),
        "scenario": {
            "jail_fine": JAIL_FINE,
            "options": {
                "can_pay_fine": "pay_jail_fine" in tool_names,
                "can_roll_for_doubles": "roll_for_doubles" in tool_names,
                "can_use_jail_card": "use_get_out_of_jail_card" in tool_names,
            },
            "notes": ["If you roll doubles, you immediately leave jail and move normally."],
        },
        "legal_tools": _build_legal_tools(decision, include_args=False),
    }


def _tool_requires(action_name: str) -> list[str]:
    if action_name == "propose_trade":
        return ["to_player_id", "offer", "request", "public_message", "private_thought"]
    if action_name == "counter_trade":
        return ["offer", "request", "public_message", "private_thought"]
    if action_name in {"accept_trade", "reject_trade"}:
        return ["public_message", "private_thought"]
    if action_name in {"mortgage_property", "unmortgage_property"}:
        return ["space_key", "public_message", "private_thought"]
    if action_name == "build_houses_or_hotel":
        return ["build_plan", "public_message", "private_thought"]
    if action_name == "sell_houses_or_hotel":
        return ["sell_plan", "public_message", "private_thought"]
    return ["public_message", "private_thought"]


def _lean_tool_entry(action_name: str, *, include_args: bool) -> dict[str, Any]:
    tool: dict[str, Any] = {
        "tool_name": action_name,
        "requires": _tool_requires(action_name),
    }
    if include_args:
        tool["args"] = {}
    return tool


def _build_post_turn_legal_tools(decision: dict[str, Any]) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for entry in decision.get("legal_actions", []):
        action_name = entry.get("action")
        if not action_name:
            continue
        include_args = action_name in {"end_turn"}
        tools.append(_lean_tool_entry(action_name, include_args=include_args))
    return tools


def _build_liquidation_legal_tools(decision: dict[str, Any]) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for entry in decision.get("legal_actions", []):
        action_name = entry.get("action")
        if not action_name:
            continue
        include_args = action_name in {"declare_bankruptcy"}
        tools.append(_lean_tool_entry(action_name, include_args=include_args))
    return tools


def _space_keys_for_indices(
    indices: list[int] | None,
    space_key_by_index: dict[int, str],
) -> list[str]:
    if not indices:
        return []
    return [space_key_for_index(int(index), space_key_by_index) for index in indices]


def build_post_turn_action_decision_focus(
    decision: dict[str, Any],
    *,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    post_turn = decision.get("post_turn", {})
    options = post_turn.get("options", {}) if isinstance(post_turn, dict) else {}
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": decision.get("player_id"),
        "scenario": {
            "note": (
                "Choose exactly one post-turn action now. The engine will apply it, update the game state, "
                "and ask you again if more post-turn actions remain legal. Choose end_turn only when you "
                "are done taking optional actions."
            ),
            "options": {
                "can_trade_with": list(options.get("can_trade_with", [])),
                "max_trade_exchanges": options.get("max_trade_exchanges"),
                "mortgageable_space_keys": _space_keys_for_indices(
                    options.get("mortgageable_space_indices"),
                    space_key_by_index,
                ),
                "unmortgageable_space_keys": _space_keys_for_indices(
                    options.get("unmortgageable_space_indices"),
                    space_key_by_index,
                ),
                "buildable_space_keys": _space_keys_for_indices(
                    options.get("buildable_space_indices"),
                    space_key_by_index,
                ),
                "sellable_building_space_keys": _space_keys_for_indices(
                    options.get("sellable_building_space_indices"),
                    space_key_by_index,
                ),
            },
        },
        "legal_tools": _build_post_turn_legal_tools(decision),
    }


def build_liquidation_decision_focus(
    decision: dict[str, Any],
    *,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    liquidation = decision.get("liquidation", {})
    options = liquidation.get("options", {}) if isinstance(liquidation, dict) else {}
    scenario: dict[str, Any] = {
        "note": (
            "Choose exactly one liquidation action now. The engine will apply it, update your cash/assets, "
            "and ask you again if you still cannot pay. Declare bankruptcy only when you cannot or should "
            "not raise enough cash."
        ),
        "owed_amount": liquidation.get("owed_amount"),
        "reason": liquidation.get("reason"),
        "shortfall": liquidation.get("shortfall"),
        "options": {
            "mortgageable_space_keys": _space_keys_for_indices(
                options.get("mortgageable_space_indices"),
                space_key_by_index,
            ),
            "sellable_building_space_keys": _space_keys_for_indices(
                options.get("sellable_building_space_indices"),
                space_key_by_index,
            ),
        },
    }
    if liquidation.get("owed_to_player_id") is not None:
        scenario["owed_to_player_id"] = liquidation.get("owed_to_player_id")
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": decision.get("player_id"),
        "scenario": scenario,
        "legal_tools": _build_liquidation_legal_tools(decision),
    }


def build_auction_bid_decision_focus(
    decision: dict[str, Any],
    *,
    space_key_by_index: dict[int, str],
) -> dict[str, Any]:
    state = decision.get("state", {})
    auction = state.get("auction", {}) if isinstance(state, dict) else {}
    property_space_key = auction.get("property_space_key")
    group = None
    if property_space_key:
        space_index = SPACE_INDEX_BY_KEY.get(property_space_key)
        if space_index is not None:
            board = state.get("board", [])
            space = next((entry for entry in board if entry.get("index") == space_index), None)
            if space:
                group = space.get("group")
    current_high_bid = int(auction.get("current_high_bid", 0) or 0)
    min_next_bid = current_high_bid + 1
    active_bidders = list(auction.get("active_bidders_player_ids", []))
    leader_id = auction.get("current_leader_player_id")
    history = list(auction.get("history", []))

    tools: list[dict[str, Any]] = []
    for entry in decision.get("legal_actions", []):
        action_name = entry.get("action")
        if action_name == "bid_auction":
            tools.append(
                {
                    "tool_name": "bid_auction",
                    "requires": ["bid_amount", "public_message", "private_thought"],
                }
            )
        elif action_name == "drop_out":
            tools.append(
                {
                    "tool_name": "drop_out",
                    "requires": ["public_message", "private_thought"],
                    "args": {},
                }
            )

    focus: dict[str, Any] = {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": decision.get("player_id"),
        "scenario": {
            "property_space": property_space_key,
            "group": group,
            "current_high_bid": current_high_bid,
            "current_leader_player_id": leader_id,
            "min_next_bid": min_next_bid,
            "active_bidders_player_ids": active_bidders,
            "action_count": auction.get("action_count"),
            "history": history,
        },
        "legal_tools": tools,
    }
    return focus


def build_trade_propose_decision_focus(decision: dict[str, Any]) -> dict[str, Any]:
    state = decision.get("state", {})
    players = state.get("players", [])
    actor_id = decision.get("player_id")
    post_turn = decision.get("post_turn")
    if not isinstance(post_turn, dict):
        post_turn = {}
    options = post_turn.get("options")
    if not isinstance(options, dict):
        options = {}
    eligible = [
        player.get("player_id")
        for player in players
        if player.get("player_id") != actor_id and not player.get("bankrupt")
    ]
    tools: list[dict[str, Any]] = []
    for entry in decision.get("legal_actions", []):
        if entry.get("action") != "propose_trade":
            continue
        tools.append(
            {
                "tool_name": "propose_trade",
                "requires": ["to_player_id", "offer", "request", "public_message", "private_thought"],
            }
        )
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": actor_id,
        "scenario": {
            "max_exchanges": options.get("max_trade_exchanges"),
            "eligible_counterparties_player_ids": eligible,
        },
        "legal_tools": tools,
    }


def build_trade_response_decision_focus(decision: dict[str, Any]) -> dict[str, Any]:
    state = decision.get("state", {})
    trade = state.get("trade", {}) if isinstance(state, dict) else {}
    actor_id = decision.get("player_id")
    initiator = trade.get("initiator_player_id")
    counterparty = trade.get("counterparty_player_id")
    counterparty_id = (
        counterparty if actor_id == initiator else initiator if initiator else counterparty
    )
    history: list[dict[str, Any]] = []
    trade_history = trade.get("history")
    if not isinstance(trade_history, list):
        trade_history = trade.get("history_last_2", [])
    for entry in trade_history:
        if not isinstance(entry, dict):
            continue
        history.append(
            {
                "from_player_id": entry.get("from_player_id"),
                "offer": entry.get("offer"),
                "request": entry.get("request"),
            }
        )
    current_offer_payload = trade.get("current_offer", {})
    current_offer_from = current_offer_payload.get("from_player_id")
    if not isinstance(current_offer_from, str):
        current_offer_from = initiator
    raw_offer = current_offer_payload.get("offer")
    raw_request = current_offer_payload.get("request")
    if actor_id == current_offer_from:
        you_give = raw_offer
        you_receive = raw_request
    else:
        you_give = raw_request
        you_receive = raw_offer
    current_offer: dict[str, Any] = {
        "from_player_id": current_offer_from,
        "if_you_accept": {
            "you_give": you_give,
            "you_receive": you_receive,
        },
    }
    tools: list[dict[str, Any]] = []
    for entry in decision.get("legal_actions", []):
        action_name = entry.get("action")
        if action_name == "accept_trade":
            tools.append(
                {
                    "tool_name": "accept_trade",
                    "requires": ["public_message", "private_thought"],
                    "args": {},
                }
            )
        elif action_name == "reject_trade":
            tools.append(
                {
                    "tool_name": "reject_trade",
                    "requires": ["public_message", "private_thought"],
                    "args": {},
                }
            )
        elif action_name == "counter_trade":
            tools.append(
                {
                    "tool_name": "counter_trade",
                    "requires": ["offer", "request", "public_message", "private_thought"],
                }
            )
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "decision_id": decision.get("decision_id"),
        "decision_type": decision.get("decision_type"),
        "actor_player_id": actor_id,
        "scenario": {
            "max_exchanges": trade.get("max_exchanges"),
            "exchange_index": trade.get("exchange_index"),
            "counterparty_player_id": counterparty_id,
            "history": history,
            "current_offer": current_offer,
        },
        "legal_tools": tools,
    }

def build_build_decision_focus(decision: dict[str, Any]) -> dict[str, Any]:
    focus: dict[str, Any] = {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "focus_type": "BUILD_DECISION_FOCUS",
    }
    build = decision.get("build", {})
    if "buildable_space_keys" in build:
        focus["buildable_space_keys"] = build.get("buildable_space_keys")
    return focus


def build_mortgage_decision_focus(decision: dict[str, Any]) -> dict[str, Any]:
    focus: dict[str, Any] = {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "focus_type": "MORTGAGE_DECISION_FOCUS",
    }
    mortgage = decision.get("mortgage", {})
    if "eligible_space_keys" in mortgage:
        focus["eligible_space_keys"] = mortgage.get("eligible_space_keys")
    return focus


def build_unmortgage_decision_focus(decision: dict[str, Any]) -> dict[str, Any]:
    focus: dict[str, Any] = {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "focus_type": "UNMORTGAGE_DECISION_FOCUS",
    }
    unmortgage = decision.get("unmortgage", {})
    if "eligible_space_keys" in unmortgage:
        focus["eligible_space_keys"] = unmortgage.get("eligible_space_keys")
    return focus


def build_end_turn_focus(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "focus_type": "END_TURN_FOCUS",
    }


def build_prompt_bundle(
    decision: dict[str, Any],
    player: PlayerConfig,
    *,
    memory: PromptMemory,
    space_key_by_index: dict[int, str],
    retry_errors: list[str] | None = None,
    retry_outcome: str | None = None,
) -> PromptBundle:
    system_prompt = build_system_prompt(player)
    state = decision.get("state", {})
    full_state = build_full_state(
        state,
        you_player_id=str(decision.get("player_id")),
        memory=memory,
        space_key_by_index=space_key_by_index,
    )
    decision_focus = build_decision_focus(decision, space_key_by_index=space_key_by_index)
    if retry_errors:
        decision_focus = _with_retry_notes(decision_focus, retry_errors, retry_outcome=retry_outcome)
    action_state = build_action_state(decision, decision_focus)
    payload: dict[str, Any] = {
        "game_state": full_state,
        "action_state": action_state,
    }
    prompt_condition = decision.get("micro_prompt_condition")
    if prompt_condition in {"minimal", "compact_state"}:
        payload["game_state"] = {
            "title": "compact_game_state",
            "metadata": full_state.get("metadata", {}),
            "you": full_state.get("you", {}),
            "bank": full_state.get("bank", {}),
        }
    elif prompt_condition == "full_state":
        payload["full_protocol_state"] = state
    elif prompt_condition == "no_private_thought":
        payload["response_instruction"] = "Tool arguments require public_message but do not require private_thought for this prompt condition."
    if player.reasoning is not None:
        payload["llm"] = {"reasoning": player.reasoning}
    user_content = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    return PromptBundle(
        system_prompt=system_prompt,
        user_payload=payload,
        user_content=user_content,
        messages=messages,
    )


def _with_retry_notes(
    decision_focus: dict[str, Any],
    errors: list[str],
    *,
    retry_outcome: str | None,
) -> dict[str, Any]:
    focus = copy.deepcopy(decision_focus)
    target = focus.get("scenario")
    if isinstance(target, dict):
        notes = target.get("notes")
        if not isinstance(notes, list):
            notes = []
            target["notes"] = notes
    else:
        notes = focus.get("notes")
        if not isinstance(notes, list):
            notes = []
            focus["notes"] = notes
    joined_errors = ", ".join(errors)
    if retry_outcome == "malformed":
        notes.append(f"Previous response was malformed: {joined_errors}.")
        notes.append("Respond with exactly one valid tool call using one of the available actions.")
    elif retry_outcome == "illogical":
        notes.append(f"Previous action was not legal in the current game state: {joined_errors}.")
        notes.append("Choose exactly one action that is legal in the current game state.")
    else:
        notes.append(f"Previous validation errors: {joined_errors}.")
        notes.append("Respond with a valid tool call only. No freeform text.")
    return focus
