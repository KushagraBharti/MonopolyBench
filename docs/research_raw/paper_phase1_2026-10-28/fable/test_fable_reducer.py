"""Hand-specified expectations for the Fable reducer.

Each expected value was derived from engine.py semantics before reducing the
corpus: _apply_trade_accept ordering and interest, _handle_bankruptcy block
shape, _apply_property_purchase/_apply_auction_purchase paired cash events,
_maybe_start_post_turn_decision suppressing menus in jail, and _run_turn's
jail-bankruptcy path. Peer output files were not consulted for these numbers.
"""
import pytest

from fable_reducer import (
    Board, Tracker, access_class, actual_settlement, content_tool_mismatch, crn_horizon,
    dice_uses, group_episodes, measure_windows, mortgage_interest, predict_bankruptcy_block,
    predict_settlement, route_by_ownership, route_by_paired_cash, turn_table,
)

SPACES = [
    {"index": 1, "kind": "PROPERTY", "name": "Mediterranean Avenue", "group": "BROWN", "price": 60},
    {"index": 3, "kind": "PROPERTY", "name": "Baltic Avenue", "group": "BROWN", "price": 60},
    {"index": 5, "kind": "RAILROAD", "name": "Reading Railroad", "group": "RAILROAD", "price": 200},
    {"index": 37, "kind": "PROPERTY", "name": "Park Place", "group": "DARK_BLUE", "price": 350},
    {"index": 39, "kind": "PROPERTY", "name": "Boardwalk", "group": "DARK_BLUE", "price": 400},
    {"index": 10, "kind": "JAIL", "name": "Jail", "group": None, "price": None},
]
BOARD = Board(SPACES)
P = ["p1", "p2", "p3"]


def ev(kind, payload=None, actor=None, turn=0):
    return {"type": kind, "payload": payload or {}, "turn_index": turn,
            "actor": {"kind": "PLAYER" if actor else "ENGINE", "player_id": actor}}


def seq(events):
    return [dict(e, seq=i, event_id=f"evt-{i}") for i, e in enumerate(events)]


def buy(pid, idx, price, turn=0):
    return [ev("PROPERTY_PURCHASED", {"player_id": pid, "space_index": idx, "price": price}, pid, turn),
            ev("CASH_CHANGED", {"player_id": pid, "delta": -price, "reason": "buy_property"}, pid, turn)]


def bundle(cash=0, props=(), cards=0):
    return {"cash": cash, "properties": list(props), "get_out_of_jail_cards": cards}


def accepted(initiator, counterparty, acceptor, offer, request, turn=0):
    return ev("TRADE_ACCEPTED", {"initiator_player_id": initiator, "counterparty_player_id": counterparty,
                                 "exchange_index": 1, "max_exchanges": 20,
                                 "offer": bundle(**offer), "request": bundle(**request)}, acceptor, turn)


# ------------------------------------------------------------- interest

@pytest.mark.parametrize("price,expected", [(60, 3), (100, 5), (120, 6), (140, 7), (160, 8), (180, 9),
                                            (200, 10), (220, 11), (240, 12), (260, 13), (280, 14),
                                            (300, 15), (320, 16), (350, 18), (400, 20), (150, 8)])
def test_mortgage_interest_is_ceil_ten_percent_of_half_price(price, expected):
    # Park Place: 350 // 2 = 175, 17.5 -> 18. Utility 150: 75 -> 7.5 -> 8.
    assert mortgage_interest(price) == expected


# ------------------------------------------------------------- routes

def test_direct_auction_and_inheritance_routes_by_paired_cash_and_ownership_agree():
    events = seq(buy("p1", 1, 60) + buy("p1", 3, 60)
                 + [ev("AUCTION_STARTED", {"property_space": 5, "initiator_player_id": "p2"}),
                    ev("PROPERTY_PURCHASED", {"player_id": "p2", "space_index": 5, "price": 80}, "p2"),
                    ev("CASH_CHANGED", {"player_id": "p2", "delta": -80, "reason": "auction_bid"}, "p2"),
                    ev("AUCTION_ENDED", {"property_space": 5, "winner_player_id": "p2", "winning_bid": 80, "reason": "SOLD"}),
                    ev("CASH_CHANGED", {"player_id": "p1", "delta": -1380, "reason": "BANKRUPTCY_CASH"}, "p1"),
                    ev("CASH_CHANGED", {"player_id": "p3", "delta": 1380, "reason": "BANKRUPTCY_CASH"}, "p3"),
                    ev("CASH_CHANGED", {"player_id": "p1", "delta": 0, "reason": "BANKRUPTCY"}, "p1"),
                    ev("PROPERTY_PURCHASED", {"player_id": "p3", "space_index": 1, "price": 0}, "p3"),
                    ev("PROPERTY_PURCHASED", {"player_id": "p3", "space_index": 3, "price": 0}, "p3")])
    t = Tracker(P, BOARD)
    in_auction, got = False, []
    for i, e in enumerate(events):
        in_auction = {"AUCTION_STARTED": True, "AUCTION_ENDED": False}.get(e["type"], in_auction)
        if e["type"] == "PROPERTY_PURCHASED":
            got.append((route_by_paired_cash(events, i), route_by_ownership(t, e, in_auction)))
        t.apply(e)
    assert got == [("direct_purchase",) * 2, ("direct_purchase",) * 2, ("auction",) * 2,
                   ("creditor_inheritance",) * 2, ("creditor_inheritance",) * 2]


def test_zero_price_purchase_without_bankruptcy_marker_is_rejected():
    events = seq([ev("PROPERTY_PURCHASED", {"player_id": "p1", "space_index": 1, "price": 0}, "p1")])
    with pytest.raises(ValueError, match="Unclassifiable"):
        route_by_paired_cash(events, 0)


def test_purchase_whose_cash_event_names_another_player_is_rejected():
    events = seq([ev("PROPERTY_PURCHASED", {"player_id": "p1", "space_index": 1, "price": 60}, "p1"),
                  ev("CASH_CHANGED", {"player_id": "p2", "delta": -60, "reason": "buy_property"}, "p2")])
    with pytest.raises(ValueError):
        route_by_paired_cash(events, 0)


# ---------------------------------------------------------- settlement

def test_settlement_prediction_orders_cash_transfers_and_interest_like_engine():
    # p2 owns mortgaged Park Place; p1 authored the final offer: gives $100 + Baltic, asks Park Place.
    # p2 accepts. Engine: offer cash pair, (no request cash), offer transfer, request transfer,
    # offerer interest on request property (Park Place mortgaged -> 18 charged to p1).
    t = Tracker(P, BOARD)
    for e in seq(buy("p1", 3, 60) + buy("p2", 37, 350) + [ev("PROPERTY_MORTGAGED", {"player_id": "p2", "space_index": 37, "amount": 175}, "p2")]):
        t.apply(e)
    acc = accepted("p2", "p1", acceptor="p2", offer={"cash": 100, "props": ["BALTIC_AVENUE"]}, request={"props": ["PARK_PLACE"]})
    expected, meta = predict_settlement(acc, t)
    assert meta["offerer"] == "p1" and meta["acceptor"] == "p2"
    assert meta["thread_initiator"] == "p2"  # counter-offer reversed authorship
    assert expected == [
        ("CASH_CHANGED", {"player_id": "p1", "delta": -100, "reason": "TRADE_CASH"}),
        ("CASH_CHANGED", {"player_id": "p2", "delta": 100, "reason": "TRADE_CASH"}),
        ("PROPERTY_TRANSFERRED", {"from_player_id": "p1", "to_player_id": "p2", "space_index": 3, "mortgaged": False}),
        ("PROPERTY_TRANSFERRED", {"from_player_id": "p2", "to_player_id": "p1", "space_index": 37, "mortgaged": True}),
        ("CASH_CHANGED", {"player_id": "p1", "delta": -18, "reason": "MORTGAGE_INTEREST"}),
    ]
    assert meta["offerer_interest"] == 18 and meta["acceptor_interest"] == 0


def test_settlement_with_both_cash_sides_and_both_interests():
    t = Tracker(P, BOARD)
    for e in seq(buy("p1", 1, 60) + buy("p2", 39, 400)
                 + [ev("PROPERTY_MORTGAGED", {"player_id": "p1", "space_index": 1, "amount": 30}, "p1"),
                    ev("PROPERTY_MORTGAGED", {"player_id": "p2", "space_index": 39, "amount": 200}, "p2")]):
        t.apply(e)
    acc = accepted("p1", "p2", acceptor="p2", offer={"cash": 50, "props": ["MEDITERRANEAN_AVENUE"]},
                   request={"cash": 20, "props": ["BOARDWALK"]})
    expected, meta = predict_settlement(acc, t)
    assert [x[0] for x in expected] == ["CASH_CHANGED"] * 4 + ["PROPERTY_TRANSFERRED"] * 2 + ["CASH_CHANGED"] * 2
    assert expected[2] == ("CASH_CHANGED", {"player_id": "p2", "delta": -20, "reason": "TRADE_CASH"})
    assert expected[-2] == ("CASH_CHANGED", {"player_id": "p1", "delta": -20, "reason": "MORTGAGE_INTEREST"})  # Boardwalk 200 -> 20
    assert expected[-1] == ("CASH_CHANGED", {"player_id": "p2", "delta": -3, "reason": "MORTGAGE_INTEREST"})  # Mediterranean 30 -> 3


def test_jail_card_only_trade_predicts_no_events_but_reports_cards():
    t = Tracker(P, BOARD)
    acc = accepted("p1", "p2", acceptor="p2", offer={"cards": 1}, request={"cash": 0})
    expected, meta = predict_settlement(acc, t)
    assert expected == []
    assert meta["jail_cards_offerer_to_acceptor"] == 1


def test_actual_settlement_stops_at_first_non_settlement_event():
    events = seq([accepted("p1", "p2", "p2", {"cash": 10}, {}),
                  ev("CASH_CHANGED", {"player_id": "p1", "delta": -10, "reason": "TRADE_CASH"}, "p1"),
                  ev("CASH_CHANGED", {"player_id": "p2", "delta": 10, "reason": "TRADE_CASH"}, "p2"),
                  ev("CASH_CHANGED", {"player_id": "p1", "delta": -50, "reason": "RENT"}, "p1")])
    acts, j = actual_settlement(events, 0)
    assert len(acts) == 2 and j == 3


# ---------------------------------------------------------- bankruptcy

def test_bankruptcy_block_predicts_sweep_creditor_and_deed_set_in_board_order():
    t = Tracker(P, BOARD)
    for e in seq(buy("p1", 39, 400) + buy("p1", 1, 60)
                 + [ev("HOUSE_BUILT", {"player_id": "p1", "space_index": 1, "count": 2}, "p1"),
                    ev("PROPERTY_MORTGAGED", {"player_id": "p1", "space_index": 39, "amount": 200}, "p1")]):
        t.apply(e)
    assert t.cash["p1"] == 1500 - 460
    events = seq([ev("CASH_CHANGED", {"player_id": "p1", "delta": -1040, "reason": "BANKRUPTCY_CASH"}, "p1"),
                  ev("CASH_CHANGED", {"player_id": "p2", "delta": 1040, "reason": "BANKRUPTCY_CASH"}, "p2"),
                  ev("CASH_CHANGED", {"player_id": "p1", "delta": 0, "reason": "BANKRUPTCY"}, "p1"),
                  ev("PROPERTY_PURCHASED", {"player_id": "p2", "space_index": 1, "price": 0}, "p2"),
                  ev("PROPERTY_PURCHASED", {"player_id": "p2", "space_index": 39, "price": 0}, "p2"),
                  ev("TURN_ENDED")])
    blk = predict_bankruptcy_block(events, 2, t)
    assert blk["creditor"] == "p2" and not blk["to_bank"]
    assert blk["deeds_before"] == [1, 39] and blk["inherited_set_ok"]
    assert blk["buildings_inherited"] == 2 and blk["mortgaged_inherited"] == 1
    assert blk["cash_swept_ok"] and blk["block_end_exclusive"] == 5


def test_bank_bankruptcy_block_has_no_inheritance_and_ends_with_bank_marker():
    t = Tracker(P, BOARD)
    for e in seq(buy("p1", 1, 60)):
        t.apply(e)
    t.cash["p1"] = 0
    events = seq([ev("CASH_CHANGED", {"player_id": "p1", "delta": 0, "reason": "BANKRUPTCY"}, "p1"),
                  ev("CASH_CHANGED", {"player_id": "p1", "delta": 0, "reason": "BANKRUPTCY_ASSETS_TO_BANK"}, "p1")])
    blk = predict_bankruptcy_block(events, 0, t)
    assert blk["to_bank"] and blk["creditor"] is None and blk["inherited_set_ok"] and blk["cash_swept_ok"]
    assert blk["block_end_exclusive"] == 2


def test_bank_return_clears_mortgage_and_buildings_in_tracker():
    t = Tracker(P, BOARD)
    for e in seq(buy("p1", 1, 60) + [ev("PROPERTY_MORTGAGED", {"player_id": "p1", "space_index": 1, "amount": 30}, "p1"),
                                     ev("CASH_CHANGED", {"player_id": "p1", "delta": 0, "reason": "BANKRUPTCY_ASSETS_TO_BANK"}, "p1")]):
        t.apply(e)
    assert t.owner[1] is None and t.mortgaged[1] is False


# ------------------------------------------------------------ turn access

def turn(owner, body, turn_index):
    return [ev("TURN_STARTED", turn=turn_index)] + [dict(e, turn_index=turn_index) for e in body]


def req(pid, kind, did="d"):
    return ev("LLM_DECISION_REQUESTED", {"decision_id": did, "player_id": pid, "decision_type": kind})


def test_turn_classes_follow_engine_menu_suppression_rules():
    events = seq(
        turn("p1", [ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p1"),
                    ev("PLAYER_MOVED", {"from": 0, "to": 3, "passed_go": False}, "p1"),
                    req("p1", "POST_TURN_ACTION_DECISION", "a"), ev("TURN_ENDED")], 0)
        + turn("p2", [req("p2", "JAIL_DECISION", "b"), ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p2"),
                      ev("TURN_ENDED")], 1)
        + turn("p3", [req("p3", "JAIL_DECISION", "c"), ev("CASH_CHANGED", {"player_id": "p3", "delta": -50, "reason": "JAIL_FINE"}, "p3"),
                      ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p3"),
                      ev("PLAYER_MOVED", {"from": 10, "to": 13, "passed_go": False}, "p3"),
                      req("p3", "POST_TURN_ACTION_DECISION", "d"), ev("TURN_ENDED")], 2)
        + turn("p1", [ev("DICE_ROLLED", {"d1": 3, "d2": 3, "is_double": True}, "p1"),
                      ev("PLAYER_MOVED", {"from": 3, "to": 10, "passed_go": False}, "p1"),
                      ev("SENT_TO_JAIL", {"player_id": "p1", "reason": "GO_TO_JAIL"}, "p1"), ev("TURN_ENDED")], 3)
        + turn("p2", [ev("CASH_CHANGED", {"player_id": "p2", "delta": 0, "reason": "BANKRUPTCY"}, "p2"),
                      ev("CASH_CHANGED", {"player_id": "p2", "delta": 0, "reason": "BANKRUPTCY_ASSETS_TO_BANK"}, "p2"),
                      ev("TURN_ENDED")], 4)
        + turn("p3", [ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p3"),
                      ev("PLAYER_MOVED", {"from": 13, "to": 16, "passed_go": False}, "p3"),
                      ev("GAME_ENDED", {"winner_player_id": "p3", "reason": "BANKRUPTCY"})], 5))
    rows = turn_table(events)
    assert [r["owner"] for r in rows] == ["p1", "p2", "p3", "p1", "p2", "p3"]
    assert [access_class(r) for r in rows] == ["management", "jail_no_exit", "management", "sent_to_jail_this_turn",
                                               "bankrupted_this_turn", "game_ended_before_menu"]
    assert rows[2]["started_in_jail"] and rows[2]["jail_exit"]


def test_unexplained_missing_menu_is_flagged_not_hidden():
    events = seq(turn("p1", [ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p1"),
                             ev("PLAYER_MOVED", {"from": 0, "to": 3, "passed_go": False}, "p1"), ev("TURN_ENDED")], 0))
    assert access_class(turn_table(events)[0]) == "UNEXPLAINED_NO_MENU"


# ----------------------------------------------------------- CRN horizon

def roll(pid, d1, d2, to, turn):
    return [ev("DICE_ROLLED", {"d1": d1, "d2": d2, "is_double": d1 == d2}, pid, turn),
            ev("PLAYER_MOVED", {"from": 0, "to": to, "passed_go": False}, pid, turn)]


def test_crn_horizon_reports_first_seat_and_landing_divergence():
    seat = {"p1": 0, "p2": 1, "p3": 2}
    a = dice_uses(seq(roll("p1", 1, 2, 3, 0) + roll("p2", 3, 4, 7, 1) + roll("p3", 2, 2, 4, 2)), seat)
    # same dice, but in game b the second draw is consumed by seat 2 (seat 1 sat in jail without rolling)
    b = dice_uses(seq(roll("p1", 1, 2, 3, 0) + roll("p3", 3, 4, 7, 1) + roll("p2", 2, 2, 4, 2)), seat)
    assert crn_horizon(a, b) == {"shared_prefix_draws": 3, "first_seat_divergence": 1, "first_landing_divergence": 1}
    c = dice_uses(seq(roll("p1", 1, 2, 3, 0) + roll("p2", 3, 4, 9, 1) + roll("p3", 2, 2, 4, 2)), seat)  # card moved p2
    assert crn_horizon(a, c) == {"shared_prefix_draws": 3, "first_seat_divergence": None, "first_landing_divergence": 1}


def test_crn_horizon_rejects_differing_raw_dice():
    seat = {"p1": 0}
    with pytest.raises(AssertionError):
        crn_horizon(dice_uses(seq(roll("p1", 1, 2, 3, 0)), seat), dice_uses(seq(roll("p1", 2, 2, 4, 0)), seat))


# -------------------------------------------------------- episodes/windows

def menu(keys=(), actions=("build_houses_or_hotel", "end_turn")):
    return {"available_actions": list(actions), "buildable_space_keys": list(keys)}


def test_trade_on_other_players_turn_waits_for_own_management_and_jail_delays_it():
    # p1 completes BROWN by trade during p2's turn 5; p1's next own turn 6 is a failed jail roll
    # (no menu); first actual management is turn 9. Next-own-turn window = turn 6 (no build).
    events = seq(
        turn("p1", buy("p1", 1, 60), 0)
        + turn("p2", buy("p2", 3, 60), 1)
        + turn("p2", [req("p2", "POST_TURN_ACTION_DECISION", "m0"),
                      accepted("p2", "p1", acceptor="p1", offer={"props": ["BALTIC_AVENUE"]}, request={"cash": 100}),
                      ev("CASH_CHANGED", {"player_id": "p1", "delta": -100, "reason": "TRADE_CASH"}, "p1"),
                      ev("CASH_CHANGED", {"player_id": "p2", "delta": 100, "reason": "TRADE_CASH"}, "p2"),
                      ev("PROPERTY_TRANSFERRED", {"from_player_id": "p2", "to_player_id": "p1", "space_index": 3, "mortgaged": False}, None),
                      req("p2", "POST_TURN_ACTION_DECISION", "m1"), ev("TURN_ENDED")], 5)
        + turn("p1", [req("p1", "JAIL_DECISION", "j1"), ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p1"), ev("TURN_ENDED")], 6)
        + turn("p2", [ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p2"), req("p2", "POST_TURN_ACTION_DECISION", "m2"), ev("TURN_ENDED")], 7)
        + turn("p1", [req("p1", "JAIL_DECISION", "j2"), ev("CASH_CHANGED", {"player_id": "p1", "delta": -50, "reason": "JAIL_FINE"}, "p1"),
                      ev("DICE_ROLLED", {"d1": 1, "d2": 2, "is_double": False}, "p1"),
                      ev("PLAYER_MOVED", {"from": 10, "to": 13, "passed_go": False}, "p1"),
                      req("p1", "POST_TURN_ACTION_DECISION", "m3"),
                      ev("HOUSE_BUILT", {"player_id": "p1", "space_index": 1, "count": 1}, "p1"),
                      req("p1", "POST_TURN_ACTION_DECISION", "m4"), ev("TURN_ENDED")], 9)
        + turn("p2", [ev("GAME_ENDED", {"winner_player_id": "p1", "reason": "BANKRUPTCY"})], 10))
    routes = {e["seq"]: "direct_purchase" for e in events if e["type"] == "PROPERTY_PURCHASED"}
    eps = group_episodes(events, ["p1", "p2"], BOARD, routes)
    assert len(eps) == 1 and eps[0]["route"] == "trade" and eps[0]["acq_turn"] == 5 and not eps[0]["acquired_on_own_turn"]
    menus = {"m0": menu(), "m1": menu(), "m2": menu(), "m3": menu(["MEDITERRANEAN_AVENUE"]), "m4": menu(["BALTIC_AVENUE"])}
    w = measure_windows(eps[0], events, menus, BOARD, turn_table(events))
    assert w["first_mgmt_turn"] == 9 and w["elapsed_to_first_mgmt"] == 4
    assert w["entry_legal"] is True and w["built_first_mgmt_turn"] is True
    assert w["pre_mgmt_decision_types"] == ["JAIL_DECISION", "JAIL_DECISION"]
    assert w["next_own_turn"] == 6 and w["built_next_own_turn"] is False
    assert w["legal_turns_without_build"] == 0 and w["management_turns_in_episode"] == 1


def test_trade_on_own_turn_opens_window_immediately_and_entry_legality_is_menu_specific():
    events = seq(
        turn("p1", buy("p1", 1, 60), 0) + turn("p2", buy("p2", 3, 60), 1)
        + turn("p1", [req("p1", "POST_TURN_ACTION_DECISION", "m0"),
                      accepted("p1", "p2", acceptor="p2", offer={"cash": 100}, request={"props": ["BALTIC_AVENUE"]}),
                      ev("CASH_CHANGED", {"player_id": "p1", "delta": -100, "reason": "TRADE_CASH"}, "p1"),
                      ev("CASH_CHANGED", {"player_id": "p2", "delta": 100, "reason": "TRADE_CASH"}, "p2"),
                      ev("PROPERTY_TRANSFERRED", {"from_player_id": "p2", "to_player_id": "p1", "space_index": 3, "mortgaged": False}, None),
                      req("p1", "POST_TURN_ACTION_DECISION", "m1"),
                      ev("CASH_CHANGED", {"player_id": "p1", "delta": 100, "reason": "MORTGAGE"}, "p1"),
                      ev("PROPERTY_MORTGAGED", {"player_id": "p1", "space_index": 5, "amount": 100}, "p1"),
                      req("p1", "POST_TURN_ACTION_DECISION", "m2"), ev("TURN_ENDED")], 2)
        + turn("p2", [ev("GAME_ENDED", {"winner_player_id": "p1", "reason": "BANKRUPTCY"})], 3))
    routes = {e["seq"]: "direct_purchase" for e in events if e["type"] == "PROPERTY_PURCHASED"}
    eps = group_episodes(events, ["p1", "p2"], BOARD, routes)
    assert eps[0]["acquired_on_own_turn"] is True
    menus = {"m0": menu(), "m1": menu([], ["mortgage_property", "end_turn"]), "m2": menu(["BALTIC_AVENUE"])}
    w = measure_windows(eps[0], events, menus, BOARD, turn_table(events))
    assert w["first_mgmt_turn"] == 2 and w["elapsed_to_first_mgmt"] == 0
    assert w["entry_legal"] is False and w["legal_any_menu_that_turn"] is True
    assert w["built_first_mgmt_turn"] is False and w["next_own_turn"] == 2 and w["built_next_own_turn"] is False
    assert w["legal_turns_without_build"] == 1


def test_loss_ends_episode_and_inheritance_records_buildings_present():
    events = seq(
        turn("p1", buy("p1", 1, 60) + buy("p1", 3, 60) + [ev("HOUSE_BUILT", {"player_id": "p1", "space_index": 1, "count": 1}, "p1"),
                                                          ev("HOUSE_BUILT", {"player_id": "p1", "space_index": 3, "count": 1}, "p1")], 0)
        + turn("p1", [ev("CASH_CHANGED", {"player_id": "p1", "delta": 0, "reason": "BANKRUPTCY"}, "p1"),
                      ev("PROPERTY_PURCHASED", {"player_id": "p2", "space_index": 1, "price": 0}, "p2"),
                      ev("PROPERTY_PURCHASED", {"player_id": "p2", "space_index": 3, "price": 0}, "p2"),
                      ev("GAME_ENDED", {"winner_player_id": "p2", "reason": "BANKRUPTCY"})], 1))
    routes = {}
    for i, e in enumerate(events):
        if e["type"] == "PROPERTY_PURCHASED":
            routes[e["seq"]] = route_by_paired_cash(events, i)
    eps = group_episodes(events, ["p1", "p2"], BOARD, routes)
    assert [(e["player_id"], e["route"], e["end_reason"]) for e in eps] == [
        ("p1", "direct_purchase", "ownership_loss"), ("p2", "creditor_inheritance", "game_end")]
    assert eps[1]["buildings_at_acquisition"] == 2
    w = measure_windows(eps[1], events, {}, BOARD, turn_table(events))
    assert w["first_mgmt_turn"] is None and w["built_first_mgmt_turn"] is None and w["next_own_turn"] is None


def test_missing_menu_raises_rather_than_inferring_legality():
    events = seq(turn("p1", buy("p1", 1, 60) + buy("p1", 3, 60) + [req("p1", "POST_TURN_ACTION_DECISION", "gone"), ev("TURN_ENDED")], 0))
    routes = {e["seq"]: "direct_purchase" for e in events if e["type"] == "PROPERTY_PURCHASED"}
    eps = group_episodes(events, ["p1", "p2"], BOARD, routes)
    with pytest.raises(KeyError):
        measure_windows(eps[0], events, {}, BOARD, turn_table(events))


# --------------------------------------------------------- attempt parsing

def test_content_tool_mismatch_requires_name_difference_and_tracks_argument_identity():
    same = {"public_message": "No.", "private_thought": "Reject."}
    a = {"assistant_content": '{"name":"reject_trade","parameters":{"public_message":"No.","private_thought":"Reject."}}',
         "parsed_tool_call": {"name": "accept_trade", "arguments": '{"public_message":"No.","private_thought":"Reject."}'}}
    m = content_tool_mismatch(a)
    assert m == {"content_name": "reject_trade", "tool_name": "accept_trade", "parsed": True, "args_equal": True}
    a["parsed_tool_call"]["name"] = "reject_trade"
    assert content_tool_mismatch(a) is None
    b = {"assistant_content": "Plain prose, no JSON", "parsed_tool_call": {"name": "end_turn", "arguments": "{}"}}
    assert content_tool_mismatch(b) is None
    c = {"assistant_content": '{"name":"build_houses_or_hotel", "parameters": {"public_message":"x" BROKEN',
         "parsed_tool_call": {"name": "end_turn", "arguments": "{}"}}
    assert content_tool_mismatch(c) == {"content_name": "build_houses_or_hotel", "tool_name": "end_turn", "parsed": False, "args_equal": None}
    assert same  # silence unused warning
