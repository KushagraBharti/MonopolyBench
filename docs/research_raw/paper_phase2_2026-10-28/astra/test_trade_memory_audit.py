"""Known-direction accounting examples independent of the corpus counts."""

from trade_memory_audit import correct_summary, settlement


def test_original_offer_direction():
    offer = {"cash": 200, "properties": []}
    request = {"cash": 0, "properties": ["CONNECTICUT_AVENUE"]}
    assert settlement("p4", "p1", offer, request) == ({"p4": -200, "p1": 200}, [("p1", "p4", 9)])
    assert correct_summary("p4", "p1", offer, request) == (
        "accepted trade with p4: p4 gives $200; p1 gives CONNECTICUT_AVENUE")


def test_counteroffer_direction_follows_author():
    offer = {"cash": 0, "properties": ["CONNECTICUT_AVENUE"]}
    request = {"cash": 100, "properties": ["ST_JAMES_PLACE"]}
    assert settlement("p1", "p4", offer, request) == (
        {"p1": 100, "p4": -100}, [("p1", "p4", 9), ("p4", "p1", 16)])
    assert correct_summary("p1", "p4", offer, request) == (
        "accepted trade with p1: p1 gives CONNECTICUT_AVENUE; p4 gives $100 + ST_JAMES_PLACE")


def test_both_cash_flows_and_jail_card_text():
    offer = {"cash": 1500, "get_out_of_jail_cards": 1}
    request = {"cash": 600, "get_out_of_jail_cards": 2}
    assert settlement("a", "b", offer, request) == ({"a": -900, "b": 900}, [])
    assert correct_summary("a", "b", offer, request) == (
        "accepted trade with a: a gives $1,500 + 1 Get Out of Jail Free card; "
        "b gives $600 + 2 Get Out of Jail Free cards")
