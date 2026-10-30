"""Check sampled reserve bounds over legal management sequences."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix
from check_g16_sample_financing import cash, houses, key, perform

HERE = Path(__file__).resolve().parent
LB = ("ORIENTAL_AVENUE", "VERMONT_AVENUE", "CONNECTICUT_AVENUE")


def exhaust(engine, decision, actor):
    steps = []
    while True:
        held = [s for s in engine.state.board if s.owner_id == actor]
        developed = [s for s in held if s.hotel or s.houses]
        if not developed:
            break
        space = max(developed, key=lambda s: 5 if s.hotel else s.houses)
        assert not space.hotel, "These nominated local branches contain houses only"
        decision, result = perform(engine, decision, *houses("sell_houses_or_hotel", (key(space),)))
        steps.append(result)
    for space in engine.state.board:
        if space.owner_id == actor and not space.mortgaged and space.price:
            decision, result = perform(engine, decision, "mortgage_property", {"space_key": key(space)})
            steps.append(result)
    return steps


def branch(suffix, preparation, expected):
    engine, decision, packet, provenance = prefix(17, suffix)
    before = engine.get_snapshot()
    steps = []
    for name, args in preparation:
        decision, result = perform(engine, decision, name, args)
        steps.append(result)
    before_liquidation = engine.get_snapshot()
    owner = next(p for p in engine.state.players if p.player_id == "p4")
    rents = {key(s): engine._calculate_rent(s, owner, 7)
             for s in engine.state.board if key(s) in LB}
    steps.extend(exhaust(engine, decision, "p4"))
    assert cash(engine, "p4") == expected, (suffix, cash(engine, "p4"), expected)
    return {**provenance, "source_action": packet["applied_action_record"],
            "before": before, "before_liquidation": before_liquidation,
            "pre_liquidation_light_blue_rents": rents,
            "steps": steps, "after": engine.get_snapshot()}


def main():
    game = units(17)
    current = branch(236, [], 759)
    proposed = branch(236, [("mortgage_property", {"space_key": "NORTH_CAROLINA_AVENUE"}),
                            houses("build_houses_or_hotel", LB)], 684)
    assert sorted(proposed["pre_liquidation_light_blue_rents"].values()) == [400, 400, 450]
    actual241 = game[241][0]["applied_action_record"]["action"]
    one = branch(241, [(actual241["action"], actual241["args"])], 934)
    two = branch(241, [(actual241["action"], actual241["args"]),
                       houses("build_houses_or_hotel", ("VERMONT_AVENUE",))], 909)
    report = {
        "sources": {i: game[i][1] for i in (236, 237, 240, 241)},
        "current236": current, "three_fourth_houses236": proposed,
        "actual_one_fourth241": one, "conditional_second_fourth241": two,
        "reading_scope": "Complete common236and240 original bundles and surrounding applied chronology read before checks.237and241applied notes, menus, actions and events inspected; their full provider bundles remain unread.",
        "findings": "236and237omit160light-blue collateral unlocked by selling houses: current759not599, proposed three fourth houses684not524. A literal NY600fatal-by1 claim is false on this full legal financing sequence. Fourth Oriental/Vermont rent400not350.241one-fourth-house full934not774; a second fourth house permits909not749, so750is not a mechanically fatal threshold. These are legal management build/sale/mortgage sequences at exact historical prefixes, not future dice or winner branches.",
        "limits": "No observed550/600/750debt is invented. A more conservative reserve or a preference to preserve earning buildings remains distinct from an incorrect full-liquidation bound. No improved expectation, causal action dependence on the error or optimal investment is established. No supply predicate changed.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g17_sample_bound_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"236_current": 759, "236_after_three_fourths": 684,
                      "241_one_fourth": 934, "241_two_fourths": 909,
                      "fourth_house_rents": [400, 400, 450]}))


if __name__ == "__main__":
    main()
