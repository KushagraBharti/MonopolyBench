"""Hand-specified accounting/window examples. Expected values precede corpus use."""
from collections import Counter

import pytest

from economics import measure_episode, reconstruct


BOARD = [
    {"index": 1, "kind": "PROPERTY", "name": "A", "price": 60, "group": "BROWN"},
    {"index": 3, "kind": "PROPERTY", "name": "B", "price": 60, "group": "BROWN"},
    {"index": 6, "kind": "PROPERTY", "name": "C", "price": 100, "group": "BLUE"},
    {"index": 8, "kind": "PROPERTY", "name": "D", "price": 100, "group": "BLUE"},
    {"index": 5, "kind": "RAILROAD", "name": "R", "price": 200, "group": "RAILROAD"},
]


def ev(kind, payload=None, turn=0, actor=None):
    return {"type": kind, "payload": payload or {}, "turn_index": turn,
            "actor": {"player_id": actor}}


def indexed(events):
    return [dict(e, seq=i, event_id=f"event-{i}") for i, e in enumerate(events)]


def purchase(pid, space, price=60, turn=0):
    return ev("PROPERTY_PURCHASED", {"player_id": pid, "space_index": space, "price": price}, turn)


def cash(pid, delta, reason="TRADE_CASH", turn=0):
    return ev("CASH_CHANGED", {"player_id": pid, "delta": delta, "reason": reason}, turn)


def accepted(actor="p2", turn=0):
    return ev("TRADE_ACCEPTED", {"initiator_player_id": "p1", "counterparty_player_id": "p2"}, turn, actor)


def transfer(a, b, space, turn=0):
    return ev("PROPERTY_TRANSFERRED", {"from_player_id": a, "to_player_id": b,
                                      "space_index": space, "mortgaged": False}, turn)


def request(did, kind="POST_TURN_ACTION_DECISION", turn=0, pid="p1"):
    return ev("LLM_DECISION_REQUESTED", {"decision_id": did, "player_id": pid, "decision_type": kind}, turn)


def build(turn=0, pid="p1", space=1):
    return ev("HOUSE_BUILT", {"player_id": pid, "space_index": space, "count": 1}, turn)


def menu(keys=(), actions=("build_houses_or_hotel",)):
    return {"available_actions": list(actions), "buildable_space_keys": list(keys)}


def reduce(events):
    return reconstruct(indexed(events), ["p1", "p2"], BOARD)


def measure(events, menus):
    events = indexed(events)
    row = reconstruct(events, ["p1", "p2"], BOARD)["group_episodes"][0]
    return measure_episode(row, events, menus, {1: "A", 3: "B"})


def test_routes_use_previous_owner_and_auction_context():
    result = reduce([purchase("p1", 1), purchase("p1", 3), ev("AUCTION_STARTED"),
                     purchase("p2", 5, 80), ev("AUCTION_ENDED"),
                     cash("p1", 0, "BANKRUPTCY"), purchase("p2", 1, 0), purchase("p2", 3, 0)])
    assert Counter(x["route"] for x in result["deed_acquisitions"]) == {
        "direct_purchase": 2, "auction": 1, "creditor_inheritance": 2}
    assert [(r["player_id"], r["route"], r["end_reason"]) for r in result["group_episodes"]] == [
        ("p1", "direct_purchase", "ownership_loss"), ("p2", "creditor_inheritance", "record_end")]
    assert len(result["group_episodes"]) == 2  # Railroads never count as color groups.


def test_unknown_zero_price_unowned_purchase_is_not_silently_inheritance():
    with pytest.raises(ValueError, match="explicit route"):
        reduce([purchase("p1", 1, 0)])


def test_counteroffer_author_is_opposite_acceptor_not_thread_initiator():
    result = reduce([purchase("p2", 1), purchase("p1", 3), accepted(actor="p1"),
                     cash("p2", -100), cash("p1", 100), transfer("p2", "p1", 1), ev("TURN_ENDED")])
    trade = result["trades"][0]
    assert trade["thread_initiator"] == "p1"
    assert trade["final_offer_author"] == "p2"
    assert trade["accepting_player"] == "p1"
    assert trade["new_groups"] == {"p1": ["BROWN"], "p2": []}
    assert trade["net_cash"] == {"p1": 100, "p2": -100}
    assert trade["transfers"][0]["to_player_id"] == "p1"


def test_cash_boundaries_include_interest_but_exclude_next_cash_event():
    result = reduce([purchase("p1", 1), accepted(), cash("p2", -200), cash("p1", 200),
                     transfer("p1", "p2", 1), cash("p2", -3, "MORTGAGE_INTEREST"),
                     cash("p1", -50, "RENT")])
    trade = result["trades"][0]
    assert trade["cash_before"] == {"p1": 1500, "p2": 1500}
    assert trade["cash_after"] == {"p1": 1700, "p2": 1297}
    assert trade["mortgage_interest"] == {"p1": 0, "p2": 3}
    assert result["cash"] == {"p1": 1650, "p2": 1297}
    assert sum(trade["net_cash"].values()) == -3


def test_loss_and_reacquisition_start_new_episode_and_stop_old_rent():
    events = indexed([purchase("p1", 1), purchase("p1", 3),
        ev("RENT_PAID", {"from_player_id": "p2", "to_player_id": "p1", "amount": 4, "space_index": 1}),
        accepted(), transfer("p1", "p2", 1), ev("TURN_ENDED"),
        accepted(), transfer("p2", "p1", 1), request("new", turn=4), build(turn=4),
        ev("RENT_PAID", {"from_player_id": "p2", "to_player_id": "p1", "amount": 10, "space_index": 1}, turn=5),
        ev("GAME_ENDED", turn=6)])
    rows = reconstruct(events, ["p1", "p2"], BOARD)["group_episodes"]
    old, new = [measure_episode(r, events, {"new": menu(["A"])}, {1: "A", 3: "B"}) for r in rows]
    assert len(rows) == 2
    assert old["rent_until_loss_or_end"] == 4
    assert old["first_build_event"] is None and old["access_status"] == "lost_before_access"
    assert new["rent_until_loss_or_end"] == 10 and new["built_first_management"] is True
    assert rows[1]["constituent_last_routes"] == {"1": "trade", "3": "direct_purchase"}


def test_bank_return_zero_delta_closes_ownership_episode():
    result = reduce([purchase("p1", 1), purchase("p1", 3),
                     cash("p1", 0, "BANKRUPTCY_ASSETS_TO_BANK"), ev("GAME_ENDED")])
    assert result["owners"][1] is None and result["owners"][3] is None
    assert result["group_episodes"][0]["end_seq_exclusive"] == 2
    assert result["group_episodes"][0]["end_reason"] == "ownership_loss"


def test_atomic_settlement_ignores_transient_group_and_duplicate_ownership():
    result = reduce([purchase("p1", 1), purchase("p1", 3), accepted(),
                     transfer("p1", "p2", 1), transfer("p2", "p1", 1), ev("TURN_ENDED")])
    assert len(result["group_episodes"]) == 1
    assert result["trades"][0]["completion_sides"] == 0


def test_partial_groups_are_not_completions():
    assert reduce([purchase("p1", 1), purchase("p2", 3)])["group_episodes"] == []


def test_first_actual_management_skips_jail_and_keeps_elapsed_delay():
    result = measure([purchase("p1", 1, turn=74), purchase("p1", 3, turn=74),
                      request("jail1", "JAIL_DECISION", 77), request("jail2", "JAIL_DECISION", 81),
                      request("manage", turn=85), build(turn=85), ev("TURN_ENDED", turn=85)],
                     {"manage": menu(["A"])})
    assert result["first_management_turn"] == 85
    assert result["elapsed_to_management"] == result["elapsed_to_build"] == 11
    assert len(result["pre_management_decisions"]) == 2
    assert result["built_first_management"] is True


def test_other_players_management_cannot_start_window():
    result = measure([purchase("p1", 1), purchase("p1", 3), request("other", pid="p2"),
                      ev("TURN_ENDED"), request("own", turn=3), build(turn=3), ev("TURN_ENDED", turn=3)],
                     {"own": menu(["A"])})
    assert result["first_management_decision"] == "own"
    assert result["elapsed_to_management"] == 3


def test_financing_later_in_window_is_distinct_from_entry_legality():
    result = measure([purchase("p1", 1), purchase("p1", 3), request("entry"),
                      cash("p1", 100, "MORTGAGE"), request("later"), build(), ev("TURN_ENDED")],
                     {"entry": menu([], ["mortgage_property", "end_turn"]), "later": menu(["A"])})
    assert result["entry_legal"] is False
    assert result["later_legal_in_window"] is True and result["built_first_management"] is True


@pytest.mark.parametrize("keys,actions,expected", [
    (["C"], ["build_houses_or_hotel"], False),
    (["A"], ["end_turn"], False),
    (["A"], ["build_houses_or_hotel"], True),
    ([], ["build_houses_or_hotel"], False),
])
def test_legality_requires_group_specific_key_and_build_action(keys, actions, expected):
    result = measure([purchase("p1", 1), purchase("p1", 3), request("m"), ev("TURN_ENDED")],
                     {"m": menu(keys, actions)})
    assert result["entry_legal"] is expected
    assert result["built_first_management"] is False


def test_no_management_before_game_end_is_not_a_declined_opportunity():
    result = measure([purchase("p1", 1), purchase("p1", 3), ev("GAME_ENDED")], {})
    assert result["entry_legal"] is result["built_first_management"] is None
    assert result["access_status"] == "no_access_before_game_end"


def test_record_end_mid_window_censors_nonbuild_but_preserves_observed_build():
    prefix = [purchase("p1", 1), purchase("p1", 3), request("m")]
    result = measure(prefix, {"m": menu(["A"])})
    assert result["window_complete"] is False and result["built_first_management"] is None
    assert measure(prefix + [build()], {"m": menu(["A"])})["built_first_management"] is True


def test_later_turn_build_is_not_first_window_build():
    result = measure([purchase("p1", 1), purchase("p1", 3), request("m"), ev("TURN_ENDED"),
                      build(turn=4), ev("GAME_ENDED", turn=5)], {"m": menu(["A"])})
    assert result["built_first_management"] is False and result["elapsed_to_build"] == 4


def test_missing_recorded_menu_fails_instead_of_inferred_legality():
    with pytest.raises(KeyError):
        measure([purchase("p1", 1), purchase("p1", 3), request("missing")], {})


def test_wrong_transfer_owner_and_event_gaps_fail():
    with pytest.raises(AssertionError):
        reduce([purchase("p1", 1), accepted(), transfer("p2", "p1", 1)])
    with pytest.raises(AssertionError, match="Non-contiguous"):
        reconstruct([dict(ev("TURN_ENDED"), seq=1)], ["p1", "p2"], BOARD)
