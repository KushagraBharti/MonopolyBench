"""Exact local checks nominated by full G13 common-sample readings."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def branch(suffix, steps, actor, expected_cash):
    engine, decision, packet, provenance = prefix(13, suffix)
    before = engine.get_snapshot()
    applied = []
    for name, args in steps:
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        applied.append({"action": action, "events": events})
    actual_cash = next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
    assert actual_cash == expected_cash, (actual_cash, expected_cash)
    return engine, {**provenance, "source": units(13)[suffix][1], "before": before,
                    "actual_recorded_action": packet["applied_action_record"], "steps": applied,
                    "after": engine.get_snapshot()}


def mortgage(key):
    return "mortgage_property", {"space_key": key}


def house(*keys):
    return "build_houses_or_hotel", {"build_plan": [
        {"space_key": key, "kind": "HOUSE", "count": 1} for key in keys]}


def main():
    game = units(13)
    build = game[160][0]
    note = build["applied_action_record"]["action"]
    assert note["action"] == "end_turn" and "Two houses placed" in note["private_thought"]
    assert json.loads(build["attempts"][0]["assistant_content"])["name"] == "build_houses_or_hotel"
    assert not build["resolution"]["fallback_used"]
    assert not any(e["type"] in {"HOUSE_BUILT", "ACTION_REJECTED"} for e in build["canonical_event_segment"])
    _, build_route = branch(160, [house("VENTNOR_AVENUE", "MARVIN_GARDENS")], "p4", 57)
    mortgage_unit = game[272][0]
    assert mortgage_unit["initial_prompt"]["payload"]["game_state"]["you"]["cash"] == 179
    assert "Cash $309" in mortgage_unit["applied_action_record"]["action"]["private_thought"]
    assert json.loads(mortgage_unit["attempts"][0]["assistant_content"])["name"] == "mortgage_property"
    assert mortgage_unit["attempts"][0]["parsed_tool_call"]["name"] == "end_turn"
    assert not mortgage_unit["resolution"]["fallback_used"]
    _, mortgage_route = branch(272, [mortgage("VENTNOR_AVENUE")], "p4", 309)
    _, high_price = branch(172, [
        ("accept_trade", {}), ("unmortgage_property", {"space_key": "PARK_PLACE"}),
        mortgage("ELECTRIC_COMPANY"), mortgage("KENTUCKY_AVENUE"), house("BOARDWALK"),
    ], "p3", 28)
    _, low_price = branch(171, [
        ("accept_trade", {}), ("unmortgage_property", {"space_key": "PARK_PLACE"}),
        mortgage("ELECTRIC_COMPANY"), house("PARK_PLACE", "BOARDWALK"),
    ], "p3", 68)
    for route in (high_price, low_price):
        transfer_interest = [e["payload"]["delta"] for step in route["steps"] for e in step["events"]
                             if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE_INTEREST"]
        assert transfer_interest == [-18], transfer_interest
    report = {
        "sources": {i: game[i][1] for i in (160, 171, 272)},
        "reading_scope": "Complete common bundles160and171 and nonsample272 manually read, all distinct delivered histories/channels/attempts/events. Long160and171returned explanations repaired in contiguous0:15000/15000:endsegments.172completeproviderbundle unread; only menu, applied record and chronology inspected before its explicitly conditional branch.",
        "phantom_build160": build_route,
        "phantom_mortgage272": mortgage_route,
        "conditional_500_acceptance172": high_price,
        "conditional_150_acceptance171": low_price,
        "findings": "160and272are valid receivedENDs, not validator defaults. Content requests a legal build or mortgage; applied private describes its unexecuted result. Later171provider corrects prior phantom house history against zero-house state.272provider starts from correct179andclearVentnor, then elects mortgage; receivedEND does not apply it. Internal state/intent and upstream emission cause remain unidentified.",
        "financing_boundary": "500plusPacific acceptance is artificial, not historical agreement.754minus500minus18transferinterestminus193redemptionleaves43;75Electricand110Kentuckymortgages allowone200houseand28reserve. Thus zero-house conclusion is cash-only, not full legal financing impossibility.150acceptance plus18interest/193redemptionleaves393, not411; Electric75permits twohousesand68reserve. Rival funding concern remains viable despite incorrect exact11reserve.",
        "limits": "No actual construction300or mortgage130 counted in historical160/272. Their legal local alternatives do not prove restraint inferior, changed later rents or an alternate winner. Mortgage-on-demand could still cover an eventual debt; no fatal omission attributed to272END. Recorded slightly-deceptive reservation framing at171does not identify induced recipient reliance or violate the benchmark's allowed competitive-deception norm.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g13_sample_channel_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"160_legal_build_cash": 57, "272_legal_mortgage_cash": 309,
                      "conditional500_one_house_cash": 28, "conditional150_two_house_cash": 68}))


if __name__ == "__main__":
    main()
