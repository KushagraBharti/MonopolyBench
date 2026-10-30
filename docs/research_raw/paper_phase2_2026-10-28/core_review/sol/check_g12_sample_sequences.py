"""Local legal action sequences nominated by complete G12 sample readings."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def cash(engine, actor):
    return next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == actor)


def branch(suffix, steps, expected_cash):
    engine, decision, packet, provenance = prefix(12, suffix)
    before = engine.get_snapshot()
    actor = decision["player_id"]
    records = []
    for name, args in steps:
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        records.append({"action": action, "events": events, "cash_after": cash(engine, actor),
                        "bank_houses_after": engine.state.bank.houses_remaining})
    assert cash(engine, actor) == expected_cash
    return engine, {**provenance, "before": before, "steps": records, "after": engine.get_snapshot(),
                    "recorded_action": packet["applied_action_record"], "source": units(12)[suffix][1]}


def house(key):
    return "build_houses_or_hotel", {"build_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]}


def sell(key):
    return "sell_houses_or_hotel", {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]}


def mortgage(key):
    return "mortgage_property", {"space_key": key}


def main():
    engine, hotel = branch(312, [
        sell("CONNECTICUT_AVENUE"), house("KENTUCKY_AVENUE"), mortgage("READING_RAILROAD"),
        sell("STATES_AVENUE"), house("INDIANA_AVENUE"), mortgage("PENNSYLVANIA_RAILROAD"),
        ("build_houses_or_hotel", {"build_plan": [{"space_key": "ILLINOIS_AVENUE", "kind": "HOTEL", "count": 1}]}),
    ], 26)
    assert engine.state.board[24].hotel
    assert engine.state.bank.houses_remaining == 4
    _, low_cash = branch(242, [mortgage("BALTIC_AVENUE"), house("ORIENTAL_AVENUE")], 5)
    _, rival = branch(73, [mortgage("PENNSYLVANIA_RAILROAD"), mortgage("KENTUCKY_AVENUE"), house("BOARDWALK")], 55)
    engine, _, _, count_provenance = prefix(12, 291)
    count = sum(s.houses for s in engine.state.board)
    assert count == 31 and engine.state.bank.houses_remaining == 1
    assert all(s.owner_id == "p2" for s in engine.state.board if s.houses)
    report = {"hotel_route312": hotel, "low_cash_route242": low_cash, "rival_route73": rival,
              "count291": {**count_provenance, "source": units(12)[291][1],
                           "applied": units(12)[291][0]["applied_action_record"], "actual_houses": count},
              "reading_scope": "Complete common bundles072/242/312/292 read.073and291fullproviderbundles not read; only delivered menus, applied actions/events and exact prefixes checked.",
              "limits": "312direct hotel unavailable is a true entry-menu statement, not permanent sequence impossibility. Legal reallocation and two mortgages reach an Illinois hotel with26cash/bank4; no value, denied rival project or future winner claim.242cash25alone cannot buy50house but Baltic30mortgage permits one, preserving distinction from financing preference.073rival45cash can legally fund a second Boardwalk house via210mortgages, ending55, without testing forecast likelihood.291public27versus31is numeric mismatch only, no intent inference.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g12_sample_sequence_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"312_cash_after": 26, "312_bank_after": 4, "242_cash_after": 5,
                      "73_cash_after": 55, "291_actual_houses": count}))


if __name__ == "__main__":
    main()
