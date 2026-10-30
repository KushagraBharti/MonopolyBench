"""Local G18 checks after reading all twelve original common-sample bundles.

Peer nominations were known for 244, 253 and 284. These checks independently
implement immediate legal branches, not future outcomes or optimality tests.
"""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 18]
    selected = {244, 253, 254, 284, 396, 428, 429, 431, 441, 442}
    bundles, sources = {}, {}
    for u in units:
        n = int(u["decision_id"][-6:])
        if n in selected:
            bundles[n] = rows(ROOT / u["packet"])[u["packet_line"] - 1]
            sources[n] = u
    run = ROOT / bundles[284]["source_run"]

    def branch(n, operations, actor):
        engine, decision = restore(run, bundles[n]["decision_id"])
        steps = []
        for name, args in operations:
            assert decision["player_id"] == actor
            decision, record = apply(engine, decision, name, args)
            steps.append(record)
        cash = next(p["cash"] for p in engine.get_snapshot()["players"]
                    if p["player_id"] == actor)
        return {"steps": steps, "cash": cash}

    def sale(key):
        return ("sell_houses_or_hotel", {"sell_plan": [
            {"space_key": key, "kind": "HOUSE", "count": 1}]})

    liquid = branch(284, [sale(k) for k in [
        "BOARDWALK", "PARK_PLACE", "BOARDWALK", "PARK_PLACE", "BOARDWALK"]]
        + [("mortgage_property", {"space_key": k}) for k in ["PARK_PLACE", "BOARDWALK"]], "p3")
    assert liquid["cash"] == 876
    # This is a management-state financing diagnostic; no artificial rent is charged.
    engine, decision = restore(run, bundles[254]["decision_id"])
    assert decision["player_id"] == "p4"
    decision, accepted = apply(engine, decision, "accept_trade", {})
    assert decision["player_id"] == "p3"
    decision, financed = apply(engine, decision, "mortgage_property", {"space_key": "PACIFIC_AVENUE"})
    decision, built = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "ATLANTIC_AVENUE", "kind": "HOUSE", "count": 1}]})
    assert next(p["cash"] for p in built["snapshot"]["players"] if p["player_id"] == "p3") == 71
    sale_args = bundles[428]["applied_action_record"]["action"]["args"]
    actual_plan = branch(428, [("sell_houses_or_hotel", sale_args),
                              ("mortgage_property", {"space_key": "KENTUCKY_AVENUE"})], "p1")
    assert actual_plan["cash"] == 69
    hold = branch(396, [("build_houses_or_hotel", {"build_plan": [
        {"space_key": "ST_CHARLES_PLACE", "kind": "HOUSE", "count": 1}]})], "p4")
    assert hold["cash"] == 65
    owned = bundles[396]["initial_prompt"]["payload"]["game_state"]["you"]["holdings"]["owned"]
    assert not {"KENTUCKY_AVENUE", "INDIANA_AVENUE"}.intersection(s["space_key"] for s in owned)
    assert not bundles[396]["resolution"]["fallback_used"]
    b244 = bundles[244]["initial_prompt"]["payload"]["game_state"]
    assert b244["you"]["position"] == "TENNESSEE_AVENUE"
    assert next(p for p in b244["others"] if p["player_id"] == "p4")["position"] == "NORTH_CAROLINA_AVENUE"
    distances = [37 - 32, 39 - 32]
    ways = sum(a + b in distances for a in range(1, 7) for b in range(1, 7))
    assert distances == [5, 7] and ways == 10 and 19 - 18 == 1
    quote = bundles[431]["applied_action_record"]["action"]["public_message"]
    for n in [441, 442]:
        memory = bundles[n]["initial_prompt"]["payload"]["game_state"]["memory"]
        assert any(x.get("message") == quote and x["player_id"] == "p4"
                   for x in memory["public_timeline_last_20"])
    assert bundles[442]["applied_action_record"]["action"]["action"] == "reject_trade"
    events = rows(run / "events.jsonl")
    start = bundles[431]["canonical_event_segment"][0]["seq"]
    end = bundles[441]["canonical_event_segment"][0]["seq"]
    intervening = [e for e in events if start < e["seq"] < end
                   and e["type"] in {"HOUSE_SOLD", "HOTEL_SOLD", "RENT_PAID"}]
    assert any(e["type"] == "RENT_PAID" and e["payload"]["amount"] == 750 for e in intervening)
    report = {
        "scope": "Twelve common bundles completely read; selected adjacent fields. No future game continuation.",
        "provenance": "Sol nominated 244/253/284; immediate branches independently implemented after source reading.",
        "d284_accessible_cash": liquid,
        "d253_artificial_acceptance": {"accept": accepted, "finance": financed, "build": built,
                                       "qualification": "No actual agreement or superior trade inferred."},
        "d428_executed_financing_sequence": actual_plan,
        "d396_feasible_one_house": hold,
        "d244_direct_movement": {"north_carolina_to_blues": distances, "ways_out_of_36": ways,
                                  "tennessee_to_new_york": 1},
        "standing_offer_intervening_events": intervening,
        "source_units": sources,
        "packet_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in sources.values()},
        "canonical_hashes": {n: hashlib.sha256((run / n).read_bytes()).hexdigest()
                             for n in ["events.jsonl", "actions.jsonl", "run_config.json"]},
        "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g18_sample_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G18 sample checks pass: 876 financing, conditional yellow house with 71, actual rent payment leaves 69, feasible pink house leaves 65; direct geometry and standing-offer exposure checked.")


if __name__ == "__main__":
    main()
