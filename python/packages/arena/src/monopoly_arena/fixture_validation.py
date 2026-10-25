"""Reconstruct public rule state for single-decision legality checks.

This validates economic actions, not future random draws or hidden deck state.
"""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from monopoly_engine import Engine
from monopoly_engine.board import SPACE_INDEX_BY_KEY, normalize_space_key
from monopoly_engine.models import AuctionState, PlayerState, TradeBundle, TradeExchange, TradeThread

from .action_validation import validate_action_payload
from .trade_offer import current_offer_author


def fixture_engine(decision: dict[str, Any]) -> Engine:
    state = decision["state"]
    engine = Engine(seed=0, players=state["players"], run_id=state["run_id"])
    engine.state.players = [PlayerState(**{f.name: p[f.name] for f in fields(PlayerState) if f.name in p})
                            for p in state["players"]]
    engine.state.turn_index = state["turn_index"]
    engine.state.active_player_id = state["active_player_id"]
    engine.state.phase = state["phase"]
    for space, payload in zip(engine.state.board, state["board"], strict=True):
        if space.index != payload["index"]:
            raise ValueError("Fixture board order is invalid")
        for key in ("owner_id", "mortgaged", "houses", "hotel"):
            setattr(space, key, payload[key])
    engine.state.bank.houses_remaining = state["bank"]["houses_remaining"]
    engine.state.bank.hotels_remaining = state["bank"]["hotels_remaining"]
    actor = next(p for p in engine.state.players if p.player_id == decision["player_id"])
    engine._pending_decision = decision
    engine._pending_turn = {"player_id": actor.player_id, "space_index": actor.position,
                            "decision_type": decision["decision_type"], "rolled_double": False}
    auction = state.get("auction")
    if auction:
        bidders = auction["active_bidders_player_ids"]
        engine.state.auction = AuctionState(
            property_space_key=auction["property_space_key"],
            property_space_index=SPACE_INDEX_BY_KEY[normalize_space_key(auction["property_space_key"])],
            current_high_bid=auction["current_high_bid"],
            current_leader_player_id=auction["current_leader_player_id"],
            active_bidders_player_ids=bidders,
            current_bidder_index=bidders.index(auction["current_bidder_player_id"]),
            initiator_player_id=auction["initiator_player_id"], turn_owner_player_id=state["active_player_id"],
            rolled_double=False,
        )
    trade = state.get("trade")
    if trade:
        offer = trade["current_offer"]
        author = current_offer_author(trade)
        if author is None:
            raise ValueError("Trade has no identifiable offer author")
        exchange = TradeExchange(author, TradeBundle(**offer["offer"]), TradeBundle(**offer["request"]))
        engine.state.trade = TradeThread(
            trade["initiator_player_id"], trade["counterparty_player_id"], trade["max_exchanges"],
            trade["exchange_index"], [], exchange, state["active_player_id"], False,
        )
    return engine


def validate_fixture_action(decision: dict[str, Any], action: dict[str, Any]) -> list[str]:
    try:
        valid, errors = validate_action_payload(action)
        if not valid:
            return errors
        return fixture_engine(decision).validate_action_for_decision(action, decision)
    except (ValueError, KeyError, TypeError, StopIteration) as exc:
        return [f"Invalid fixture/action state: {exc}"]
