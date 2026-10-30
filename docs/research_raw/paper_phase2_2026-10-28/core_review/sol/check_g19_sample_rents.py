"""Check G19 sampled rent propositions and the recorded red-build recovery."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix
from check_g16_sample_financing import cash, houses, key, perform

HERE = Path(__file__).resolve().parent


def rents_at(suffix, keys):
    engine, _, _, provenance = prefix(19, suffix)
    values = {}
    for space in engine.state.board:
        if key(space) in keys:
            owner = next(p for p in engine.state.players if p.player_id == space.owner_id)
            values[key(space)] = engine._calculate_rent(space, owner, 7)
    return {**provenance, "rents": values}


def main():
    pink = ("ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE")
    red = ("KENTUCKY_AVENUE", "INDIANA_AVENUE", "ILLINOIS_AVENUE")
    rail = ("READING_RAILROAD", "PENNSYLVANIA_RAILROAD", "B_O_RAILROAD")
    pink220 = rents_at(220, pink)
    red237 = rents_at(237, red)
    rail269 = rents_at(269, rail)
    assert list(pink220["rents"].values()) == [450, 450, 500]
    assert list(red237["rents"].values()) == [700, 700, 750]
    assert list(rail269["rents"].values()) == [100, 100, 100]

    engine, decision, packet, provenance = prefix(19, 234)
    decision, interleaved = perform(engine, decision, *houses("build_houses_or_hotel", red * 3))
    assert cash(engine, "p1") == 262
    assert all(s.houses == 3 for s in engine.state.board if key(s) in red)
    game = units(19)
    actual = []
    for suffix in (234, 235, 236):
        action = game[suffix][0]["applied_action_record"]["action"]
        assert action["action"] == "build_houses_or_hotel"
        assert sum(entry["count"] for entry in action["args"]["build_plan"]) == 3
        actual.append({"source": game[suffix][1], "action": action})

    report = {
        "pink220": pink220, "red237": red237, "rail269": rail269,
        "interleaved_original234": {**provenance, "recorded_action": packet["applied_action_record"],
                                     "step": interleaved, "cash_after": 262},
        "actual_three_decision_layers": actual,
        "self_corrections": [
            "Initial sample220 mistakenly endorsed States500 and Virginia550. Exact current rents are450/450/500.502covers ALL three pink rents, not merely two. The applied fatal-Virginia assertion is false.",
            "My subsequent commentary proposed correcting sample227's red700/700/750 to550/550/600. That proposed correction was itself wrong and failed this script's first assertion. The exact engine confirms the initial700/700/750, which remains unchanged. No failed script result is treated as verification.",
        ],
        "findings": "Sample269's three-owned-railroad200 proposition is false, normal active rents100each. Original234nine-house allocation is legal after interleaving and leaves262. Actual234/235/236buy three layers on the same management turn; some-build, within-decision allocation preservation and eventual same-turn target attainment are distinct.",
        "reading_scope": "All twelve G19 common bundles completely read.234both attempts read as sample216.235/236/237applied actions, current menus, history and events inspected, not all their full returned provider bundles. Historical G19 note trail read in full as secondary context, not as a substitute for originals.",
        "limits": "Local rent and legality diagnostics only. No alternate roll, improved utility, causal reliance or changed winner. Preserving existing houses does not by itself establish binding rival supply denial.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g19_sample_rent_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"pink": pink220["rents"], "red": red237["rents"],
                      "rail": rail269["rents"], "interleaved_cash": 262}))


if __name__ == "__main__":
    main()
