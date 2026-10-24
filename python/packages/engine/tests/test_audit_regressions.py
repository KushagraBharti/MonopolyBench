from __future__ import annotations

import pytest
from monopoly_engine import Engine, replay_actions
from monopoly_engine.board import SPACE_KEY_BY_INDEX
from monopoly_engine.models import TradeBundle, TradeExchange, TradeThread


def engine():
    return Engine(seed=7, run_id="audit", max_turns=5,
                  players=[{"player_id": f"p{i}", "name": f"P{i}"} for i in range(4)])


def action(decision, name, **args):
    return {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}


def test_third_jail_roll_finances_fine_and_moves_once():
    game = engine()
    player = game.state.players[0]
    player.cash, player.position, player.in_jail, player.jail_turns = 0, 10, True, 2
    game.state.board[5].owner_id = player.player_id
    rolls = iter([(1, 2)])
    game._rng.roll_dice = lambda: next(rolls)
    _, _, decision, _ = game.advance_until_decision()
    _, _, debt, _ = game.apply_action(action(decision, "roll_for_doubles"))
    assert debt["decision_type"] == "LIQUIDATION_DECISION"
    assert not player.bankrupt
    _, events, next_decision, _ = game.apply_action(action(debt, "mortgage_property", space_key=SPACE_KEY_BY_INDEX[5]))
    assert player.cash == 50 and player.position == 13 and not player.in_jail
    assert not any(e["type"] == "DICE_ROLLED" for e in events)
    assert next_decision["decision_type"] == "BUY_OR_AUCTION_DECISION"


def test_birthday_finances_other_player_and_resumes_turn_owner():
    game = engine()
    recipient, debtor = game.state.players[:2]
    debtor.cash = 5
    game.state.board[5].owner_id = debtor.player_id
    events = []
    decision, _ = game._apply_card_effect(
        "COMMUNITY_CHEST", "BIRTHDAY_COLLECT_10_FROM_EACH_PLAYER", recipient, events, turn_index=0, rolled_double=False)
    assert decision["player_id"] == debtor.player_id
    game._activate_debt_decision(decision, events)
    _, _, decision, _ = game.apply_action(action(decision, "mortgage_property", space_key=SPACE_KEY_BY_INDEX[5]))
    assert debtor.cash == 95 and not debtor.bankrupt
    assert recipient.cash == 1530
    assert decision["player_id"] == recipient.player_id
    assert game.state.turn_index == 0


def test_mixed_house_hotel_plan_cannot_borrow_future_bank_inventory():
    game = engine()
    player = game.state.players[0]
    for i in (1, 3):
        game.state.board[i].owner_id = player.player_id
    game.state.bank.houses_remaining = 1
    plan = [{"space_index": i, "kind": kind, "count": count}
            for kind, count in [("HOUSE", 4), ("HOTEL", 1)] for i in (1, 3)]
    with pytest.raises(ValueError, match="Bank houses"):
        game._validate_build_plan(player, plan)
    assert game.state.board[1].houses == 0


def test_bare_property_in_developed_group_cannot_be_traded():
    game = engine()
    owner = game.state.players[0]
    for i in (1, 3):
        game.state.board[i].owner_id = owner.player_id
    game.state.board[1].houses = 1
    with pytest.raises(ValueError, match="developed group"):
        game._validate_trade_bundle(TradeBundle(0, [SPACE_KEY_BY_INDEX[3]], 0), owner, allow_cash_overdraft=False)


def test_mortgaged_sibling_does_not_disable_double_rent():
    game = engine()
    owner = game.state.players[0]
    for i in (1, 3):
        game.state.board[i].owner_id = owner.player_id
    game.state.board[3].mortgaged = True
    assert game._calculate_rent(game.state.board[1], owner, 0) == 4


@pytest.mark.parametrize("author", ["p0", "p1"])
def test_trade_snapshot_identifies_current_author(author):
    offer = TradeExchange(author, TradeBundle(30, [], 0), TradeBundle(40, [], 0))
    trade = TradeThread("p0", "p1", 20, 2, [offer], offer, "p0", False)
    assert trade.to_snapshot()["current_offer"]["from_player_id"] == author


def test_terminal_replay_rejects_extra_actions():
    with pytest.raises(ValueError, match="Extra action"):
        replay_actions(seed=1, players=[{"player_id": "p0", "name": "P0"}], run_id="audit",
                       max_turns=0, actions=[{"decision_id": "impossible"}])


def test_last_birthday_debtor_bankruptcy_emits_no_unanswered_decision():
    game = engine()
    recipient, debtor = game.state.players[:2]
    for player in game.state.players[2:]:
        player.bankrupt = True
    debtor.cash = 0
    events = []
    decision, _ = game._apply_card_effect(
        "COMMUNITY_CHEST", "BIRTHDAY_COLLECT_10_FROM_EACH_PLAYER", recipient, events,
        turn_index=0, rolled_double=False,
    )
    game._activate_debt_decision(decision, events)
    _, terminal_events, next_decision, snapshot = game.apply_action(action(decision, "declare_bankruptcy"))
    assert snapshot["phase"] == "GAME_OVER"
    assert next_decision is None
    assert game.advance_until_decision()[2] is None
    assert not any(event["type"] == "LLM_DECISION_REQUESTED" for event in terminal_events)
    assert terminal_events[-1]["type"] == "GAME_ENDED"
