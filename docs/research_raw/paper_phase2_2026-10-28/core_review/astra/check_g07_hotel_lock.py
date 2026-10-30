"""Verify the automatic hotel-locked bankruptcy and both available mortgage orders."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    ledger = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"
    packets, units = {}, {}
    for u in rows(ledger):
        n = int(u["decision_id"][-6:])
        if u["game"] == 7 and n in {309, 336, 337, 338, 339}:
            packets[n] = rows(ROOT / u["packet"])[u["packet_line"] - 1]
            units[n] = u
    run = ROOT / packets[338]["source_run"]
    prefix_engine, decision = restore(run, packets[338]["decision_id"])
    menu = packets[338]["initial_prompt"]["payload"]["action_state"]
    you = packets[338]["initial_prompt"]["payload"]["game_state"]["you"]
    assert you["cash"] == 290
    assert menu["available_actions"] == ["mortgage_property", "declare_bankruptcy"]
    assert set(menu["scenario"]["options"]["mortgageable_space_keys"]) == {"READING_RAILROAD", "ORIENTAL_AVENUE"}
    assert menu["scenario"]["options"]["sellable_building_space_keys"] == []
    assert menu["scenario"]["owed_amount"] == 750
    assert prefix_engine.get_snapshot()["bank"]["houses_remaining"] == 0
    estates = {p["space_key"]: p for p in you["holdings"]["owned"]}
    assert [estates[k]["houses"] for k in ["ST_CHARLES_PLACE", "STATES_AVENUE"]] == [4, 4]
    assert estates["VIRGINIA_AVENUE"]["hotel"]
    nominal = 290 + 100 + 50 + 13 * 50 + 70 + 70 + 80
    assert nominal == 1310
    branches = []
    for order in [("READING_RAILROAD", "ORIENTAL_AVENUE"), ("ORIENTAL_AVENUE", "READING_RAILROAD")]:
        engine, decision = restore(run, packets[338]["decision_id"])
        steps = []
        for key in order:
            decision, step = apply(engine, decision, "mortgage_property", {"space_key": key})
            steps.append(step)
        last = steps[-1]
        bankrupt_cash = [e["payload"]["delta"] for e in last["events"]
                         if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY_CASH"
                         and e["payload"]["player_id"] == "p3"]
        assert bankrupt_cash == [-440]
        assert next(p for p in last["snapshot"]["players"] if p["player_id"] == "p3")["bankrupt"]
        branches.append({"order": order, "steps": steps})
    earlier = packets[309]["initial_prompt"]["payload"]
    assert earlier["game_state"]["you"]["player_id"] == "p3"
    assert earlier["game_state"]["bank"]["houses_remaining"] < 4
    assert earlier["action_state"]["scenario"]["options"]["sellable_building_space_keys"] == []
    report = {"scope": "Exact recorded prefix, both permitted mortgage orders. Immediate liquidation only; no alternative winner inference.",
              "peer_provenance": "Fable supplied the hotel-lock estate and Sol supplied the earlier d309 access objection before this check.",
              "game": 7, "before_decision": packets[338]["decision_id"],
              "actual_automatic_elimination_decision": packets[339]["decision_id"],
              "cash": 290, "accessible_ceiling": 440, "nominal_full_access_upper_bound": nominal,
              "owed": 750, "branches": branches,
              "earlier_d309": {"bank_houses": earlier["game_state"]["bank"]["houses_remaining"],
                                "action_state": earlier["action_state"]},
              "interpretation": "The later capture of the last two bank houses did not newly create the empty sale menu; it was already empty at d309. Automatic bankruptcy is not an applied surrender action.",
              "source_units": units,
              "packet_sha256": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                 for u in units.values()},
              "source_sha256": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                                for n in ["run_config.json", "actions.jsonl", "events.jsonl"]},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g07_hotel_lock.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G7 hotel lock verified: both legal mortgage orders reach $440 then automatic bankruptcy against $750; nominal $1310 is inaccessible. Sale menu already empty at d309.")


if __name__ == "__main__":
    main()
