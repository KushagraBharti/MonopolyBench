"""Exact G20 conditional trade finance and actual hotel liquidation.

All branches use original prefixes. Trade acceptances are explicitly diagnostic.
"""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix
from check_g16_sample_financing import cash, houses, key, perform

HERE = Path(__file__).resolve().parent
ORANGE = ("ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE")
SIDE = ("ORIENTAL_AVENUE", "B_O_RAILROAD", "ATLANTIC_AVENUE", "PARK_PLACE")
BROWN = ("MEDITERRANEAN_AVENUE", "BALTIC_AVENUE")


def prior_management_bound(suffix, actor, expected):
    engine, decision, packet, provenance = prefix(20, suffix)
    focal = units(20)[200][0]["initial_prompt"]["payload"]["game_state"]
    focal_player = next(p for p in focal["others"] if p["player_id"] == actor)
    own = packet["initial_prompt"]["payload"]["game_state"]["you"]
    assert own["cash"] == focal_player["cash"]
    assert own["holdings"] == focal_player["holdings"]
    previous_bank = packet["initial_prompt"]["payload"]["game_state"]["bank"]
    assert all(previous_bank[field] == focal["bank"][field]
               for field in ("houses_remaining", "hotels_remaining"))
    assert decision["player_id"] == actor
    steps = []
    held = [s for s in engine.state.board if s.owner_id == actor and s.houses]
    assert all(not s.hotel and s.houses == held[0].houses for s in held)
    sale_keys = tuple(key(s) for s in held) * held[0].houses
    decision, result = perform(engine, decision, *houses("sell_houses_or_hotel", sale_keys))
    steps.append(result)
    for space in engine.state.board:
        if space.owner_id == actor and not space.mortgaged and space.price:
            decision, result = perform(engine, decision, "mortgage_property", {"space_key": key(space)})
            steps.append(result)
    assert cash(engine, actor) == expected
    return {**provenance, "same_cash_holdings_and_building_stock_as200": True,
            "steps": steps, "cash_after": expected,
            "scope": "Legal own management sequence at preceding actual opportunity with focal200 cash, holdings and building stock unchanged. B&O leaves bank ownership during the intervening auction, so unowned inventory is NOT asserted equal. No synthetic debt, transferred control, future draw or alternate outcome."}


def conditional(suffix, count, sell_browns=False):
    engine, decision, _, provenance = prefix(20, suffix)
    steps = []
    decision, accepted = perform(engine, decision, "accept_trade", {})
    steps.append(accepted)
    assert decision["player_id"] == "p3", decision
    after_accept = cash(engine, "p3")
    for deed in (*SIDE, *(("MARVIN_GARDENS",) if suffix == 257 else ())):
        decision, result = perform(engine, decision, "mortgage_property", {"space_key": deed})
        steps.append(result)
    decision, redeemed = perform(engine, decision, "unmortgage_property", {"space_key": "NEW_YORK_AVENUE"})
    steps.append(redeemed)
    if sell_browns:
        for deed in BROWN:
            decision, result = perform(engine, decision, "sell_houses_or_hotel", {
                "sell_plan": [{"space_key": deed, "kind": "HOTEL", "count": 1}]})
            steps.append(result)
        decision, result = perform(engine, decision, *houses("sell_houses_or_hotel", BROWN * 4))
        steps.append(result)
    before_build = cash(engine, "p3")
    keys = (ORANGE * 3)[:count]
    decision, result = perform(engine, decision, *houses("build_houses_or_hotel", keys))
    steps.append(result)
    return {**provenance, "artificial_conditional_acceptance": True,
            "cash_after_acceptance_and_interest": after_accept,
            "cash_before_build": before_build, "cash_after": cash(engine, "p3"),
            "steps": steps, "after": engine.get_snapshot()}


def main():
    grok_bound = prior_management_bound(192, "p1", 566)
    gemini_bound = prior_management_bound(191, "p4", 1383)
    four = conditional(235, 4)
    assert (four["cash_after_acceptance_and_interest"], four["cash_before_build"], four["cash_after"]) == (97, 441, 41)
    six = conditional(235, 6, sell_browns=True)
    assert six["cash_after"] == 91
    later_six = conditional(257, 6)
    assert later_six["cash_after"] == 64

    game = units(20)
    engine, decision, _, provenance = prefix(20, 327)
    steps = []
    for suffix in range(327, 337):
        action = game[suffix][0]["applied_action_record"]["action"]
        assert decision["decision_id"] == action["decision_id"]
        decision, result = perform(engine, decision, action["action"], action["args"])
        result["source"] = game[suffix][1]
        result["recorded_action"] = action
        steps.append(result)
    assert cash(engine, "p3") == 14
    events = [e for step in steps for e in step["events"]]
    salvage = sum(e["payload"]["delta"] for e in events
                  if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "SELL_BUILDING")
    mortgages = sum(e["payload"]["delta"] for e in events
                    if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "MORTGAGE")
    paid = [e for e in events if e["type"] == "RENT_PAID"]
    assert (salvage, mortgages, [e["payload"]["amount"] for e in paid]) == (700, 665, [1400])
    report = {
        "d200_rival_financing_at_matching_actual_management": {
            "grok192": grok_bound, "gemini191": gemini_bound},
        "400_accept_four_orange_houses_preserving_brown_hotels": four,
        "400_accept_six_orange_houses_after_brown_liquidation": six,
        "later250_accept_six_preserving_brown_hotels": later_six,
        "actual327_through336": {**provenance, "steps": steps, "salvage": salvage,
                                 "mortgages": mortgages, "rent_paid": paid, "cash_after": 14},
        "findings": "235literal zero reachable development is false: actual400acceptance permits four houses and41while preserving brown hotels. Its earlier six-house target is not affordable from side mortgages alone, but legal brown liquidation also funds six with91. Thus even the six-house limitation needs a preserve-brown-income condition. At257later actual250offer acceptance permits six with64and brown hotels intact.325correct1414total contains offsetting25component errors, and its returned provider falsely adds the200cost to413while applied private correctly leaves213. Actual327–336legally realizes700salvage plus665mortgages from49, pays1400and retains14.",
        "semantic_limit": "No acceptance or liquidation preference is inferred from feasibility.235may use cannot develop as a larger-target budget shorthand, and brown liquidation sacrifices an existing income engine. No recorded explicit deceptive intent, recipient belief uptake, optimal trade, improved future survival or alternate winner. The five-red-houses-for250public claim is separately numerically false at150per new red house.",
        "reading_scope": "All twelve G20common bundles and full98-line historical notes read. Complete nonsample235and325original bundles read after peer nomination.191/192/257and327–336applied notes, menus, actions and original events checked for these branches; their full provider bundles not represented as read.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g20_sample_financing_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"400_four": 41, "400_six_after_brown_liquidation": 91,
                      "250_later_six": 64, "actual_salvage": salvage,
                      "actual_mortgages": mortgages, "actual_final_cash": 14}))
    for step in steps:
        print(json.dumps({"source": step["source"], "recorded_action": step["recorded_action"]}))


if __name__ == "__main__":
    main()
