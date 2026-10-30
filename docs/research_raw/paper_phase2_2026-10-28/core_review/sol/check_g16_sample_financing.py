"""Local financing and utility checks after complete G16 common readings.

Branches preserve exact historical prefixes. Conditional acceptances and
management liquidation sequences are diagnostics, not historical outcomes.
"""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def key(space):
    return re.sub(r"[^A-Z0-9]+", "_", space.name.upper()).strip("_")


def cash(engine, actor):
    return next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == actor)


def perform(engine, decision, name, args):
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": name, "args": args}
    _, events, following, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    return following, {"action": action, "events": events}


def operation(name, key):
    return name, {"space_key": key}


def houses(name, keys):
    plan = "build_plan" if name == "build_houses_or_hotel" else "sell_plan"
    return name, {plan: [{"space_key": key, "kind": "HOUSE", "count": 1} for key in keys]}


def run(suffix, steps, actor, expected):
    engine, decision, packet, provenance = prefix(16, suffix)
    before = engine.get_snapshot()
    results = []
    for name, args in steps:
        decision, result = perform(engine, decision, name, args)
        results.append(result)
    assert cash(engine, actor) == expected, (suffix, cash(engine, actor), expected)
    return engine, {**provenance, "before": before, "steps": results,
                    "actual_recorded_action": packet["applied_action_record"],
                    "after": engine.get_snapshot()}


def main():
    game = units(16)
    engine, _, _, evidence = prefix(16, 173)
    spare = {key(s): s.price // 2 for s in engine.state.board
             if s.owner_id == "p3" and not s.hotel and not s.houses and not s.mortgaged}
    assert sorted(spare.values()) == [75, 150, 200], spare
    assert sum(spare.values()) == 425 and cash(engine, "p3") + sum(spare.values()) == 592
    steps = [operation("mortgage_property", key) for key in spare]
    steps.append(("sell_houses_or_hotel", {"sell_plan": [
        {"space_key": "MEDITERRANEAN_AVENUE", "kind": "HOTEL", "count": 1}]}))
    _, reserve173 = run(173, steps, "p3", 617)

    side = [operation("mortgage_property", key) for key in
            ("ST_CHARLES_PLACE", "STATES_AVENUE", "WATER_WORKS", "MARVIN_GARDENS")]
    orange = ("ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE")
    preparation = [operation("unmortgage_property", "NEW_YORK_AVENUE"), *side]
    three_build = houses("build_houses_or_hotel", orange)
    _, three = run(261, [*preparation, three_build], "p1", 185)
    _, three_liquidated = run(261, [*preparation, three_build,
        houses("sell_houses_or_hotel", orange),
        *[operation("mortgage_property", key) for key in orange]], "p1", 615)
    four_keys = (*orange, "NEW_YORK_AVENUE")
    four_build = houses("build_houses_or_hotel", four_keys)
    _, four = run(261, [*preparation, four_build], "p1", 85)
    _, four_liquidated = run(261, [*preparation, four_build,
        houses("sell_houses_or_hotel", tuple(reversed(four_keys))),
        *[operation("mortgage_property", key) for key in orange]], "p1", 565)

    utility, decision, _, utility_provenance = prefix(16, 429)
    owner = next(p for p in utility.state.players if p.player_id == "p1")
    ww = next(s for s in utility.state.board if key(s) == "WATER_WORKS")
    rent_before = utility._calculate_rent(ww, owner, 7)
    _, utility_step = perform(utility, decision, "accept_trade", {})
    rent_after = utility._calculate_rent(ww, owner, 7)
    assert (rent_before, rent_after, cash(utility, "p1")) == (28, 70, 77)
    ec = next(s for s in utility.state.board if key(s) == "ELECTRIC_COMPANY")
    assert ec.owner_id == "p1" and ec.mortgaged

    seller, offer, _, seller_provenance = prefix(16, 322)
    next_decision, acceptance = perform(seller, offer, "accept_trade", {})
    assert next_decision["player_id"] == "p2"
    next_decision, redeem = perform(seller, next_decision, "unmortgage_property", {"space_key": "PARK_PLACE"})
    _, build = perform(seller, next_decision, *houses("build_houses_or_hotel", ("BOARDWALK",)))
    assert cash(seller, "p2") == 99

    report = {
        "sources": {i: game[i][1] for i in (173, 261, 322, 341, 429)},
        "reserve173": {"prefix": evidence, "spare_mortgage_values": spare,
                       "spare_only_cash": 592, "one_hotel_downgrade_route": reserve173},
        "three_house_build261": three, "three_house_liquidation261": three_liquidated,
        "four_house_build261": four, "four_house_liquidation261": four_liquidated,
        "conditional_utility_accept429": {**utility_provenance, "step": utility_step,
            "dice_total": 7, "water_rent_before": rent_before, "water_rent_after": rent_after,
            "buyer_cash_after": 77, "electric_stays_mortgaged": True},
        "conditional_rail_accept322": {**seller_provenance,
            "steps": [acceptance, redeem, build], "seller_cash_after": 99},
        "reading_scope": "Complete common originals173,261,322,341 and surrounding applied chronology read before these branches.429applied note, current trade menu, holdings, events and conditional acceptance checked; its full provider bundle remains unread.",
        "findings": "173overstates spare mortgages by10,592rather than602. One legal brown-hotel downgrade supplies25and reaches617without artificial stock.261can legally build three total orange houses and subsequently liquidate to615, or four total and liquidate to565, with all unlocked orange mortgages included. Its next550-hit fatality assertion is not a full financing bound. A target of three houses EACH remains unaffordable.429mortgaged Electric ownership raises active Water Works rent from4x to10x;77cash still cannot redeem Electric for83.322accepted350rail sale would permit seller Park redemption and one Boardwalk house at its immediately returned management decision, leaving99.",
        "limits": "No historical trade acceptance or construction substituted for received END/reject. No future hotel debt, improved expected value, recipient agreement, alternate winner or causal persuasion inferred. Construction and liquidation here occur through currently legal management actions, not a simulated future draw or changed supply.341combined donor/recipient arithmetic alone does not establish an agreed transfer.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g16_sample_financing_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"173_spare_only": 592, "173_with_downgrade": 617,
                      "261_three_house_liquidated": 615, "261_four_house_liquidated": 565,
                      "429_active_water_rent": [rent_before, rent_after],
                      "322_one_house_reserve": 99}))


if __name__ == "__main__":
    main()
