"""G7 original-source accounting and immediate-menu checks.

The hotel-lock endpoint is separately proved in check_g07_hotel_lock.py.
These local branches never assert an alternative future winner.
"""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 7]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def payload(n):
        return packets[n]["initial_prompt"]["payload"]

    def state(n):
        return payload(n)["game_state"]

    def person(n, player=None):
        s = state(n)
        return next(p for p in [s["you"], *s["others"]]
                    if p["player_id"] == (player or s["you"]["player_id"]))

    assert packets[34]["turn_index"] == 23 and packets[38]["turn_index"] == 25
    assert sum(action(n)["action"] == "counter_trade" for n in range(38, 44)) == 4
    assert sum(action(n)["action"] == "counter_trade" for n in range(132, 139)) == 5
    assert action(44)["action"] == "propose_trade"
    assert json.loads(packets[44]["attempts"][0]["assistant_content"])["name"] == "end_turn"
    assert action(99)["action"] == "reject_trade"
    assert "$120 over list" in action(105)["public_message"]
    assert "$450" in action(143)["private_thought"]
    assert "unable to build" in action(143)["public_message"]
    assert "overstated" in action(144)["private_thought"]
    assert action(143)["public_message"] in [r["message"] for r in state(144)["memory"]["public_timeline_last_20"]]
    mortgage_funding = [e for n in range(146, 151) for e in packets[n]["canonical_event_segment"]
                        if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE"]
    assert sum(e["payload"]["delta"] for e in mortgage_funding) == 450
    assert person(151)["cash"] == 495 and person(152, "p1")["cash"] == 95

    assert [n for n, p in packets.items() if p["resolution"]["fallback_used"]] == [183]
    engine, decision = restore(run, packets[183]["decision_id"])
    plan = json.loads(packets[183]["attempts"][-1]["parsed_tool_call"]["arguments"])["build_plan"]
    interleaved = [{**entry, "count": 1} for level in range(max(x["count"] for x in plan))
                   for entry in plan if entry["count"] > level]
    _, recovered_build = apply(engine, decision, "build_houses_or_hotel", {"build_plan": interleaved})
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 119

    # Peer-nominated attainable financing, independently replayed from the real menu.
    engine, decision = restore(run, packets[183]["decision_id"])
    funding = []
    for key in ["READING_RAILROAD", "PENNSYLVANIA_RAILROAD"]:
        decision, result = apply(engine, decision, "mortgage_property", {"space_key": key})
        funding.append(result)
    nine = [{"space_key": key, "kind": "HOUSE", "count": 1} for _ in range(3)
            for key in ["ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"]]
    _, nine_build = apply(engine, decision, "build_houses_or_hotel", {"build_plan": nine})
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 19

    assert person(168, "p4")["cash"] == 74
    estate168 = {s["space_key"]: s for s in person(168, "p4")["holdings"]["owned"]}
    assert [estate168[k]["houses"] for k in ["PARK_PLACE", "BOARDWALK"]] == [2, 3]
    assert person(200, "p4")["cash"] == 94
    assert person(237)["cash"] == 15
    assert packets[249]["turn_index"] - packets[237]["turn_index"] == 3
    assert action(236)["public_message"] in [r["message"] for r in state(237)["memory"]["public_timeline_last_20"]]
    assert action(237)["action"] == "reject_trade"
    assert action(244)["args"]["bid_amount"] == person(244, "p3")["cash"] == 171
    assert action(264)["action"] == "start_auction" and person(264)["cash"] == 463
    assert person(274)["cash"] == 371 and person(275)["cash"] == 501
    assert "mortgages for $130" in action(266)["private_thought"]
    assert action(267)["public_message"] in [r["message"] for r in state(268)["memory"]["public_timeline_last_20"]]
    assert action(286)["action"] == "mortgage_property"
    assert action(286)["private_thought"] == action(274)["private_thought"]
    assert json.loads(packets[286]["attempts"][0]["assistant_content"])["name"] == "declare_bankruptcy"
    assert payload(293)["action_state"]["available_actions"] == ["roll_for_doubles"]
    assert "send 8 houses back" in packets[309]["attempts"][-1]["assistant_content"]

    # Sol's own release option is not the only possible management-time release.
    engine, decision = restore(run, packets[329]["decision_id"])
    _, sol_release = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "ST_JAMES_PLACE", "kind": "HOTEL", "count": 1}]})
    assert engine.state.bank.houses_remaining == 6
    assert next(p.cash for p in engine.state.players if p.player_id == "p4") == 55
    # A separate fresh prefix retains historical329 END and reaches the actual330 menu.
    engine, decision = restore(run, packets[330]["decision_id"])
    assert decision["player_id"] == "p3"
    decision, opus_release = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "ST_CHARLES_PLACE", "kind": "HOTEL", "count": 1}]})
    assert engine.state.bank.houses_remaining == 6
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 430
    decision, newly_accessible_sale = apply(engine, decision, "sell_houses_or_hotel", {"sell_plan": [
        {"space_key": "VIRGINIA_AVENUE", "kind": "HOTEL", "count": 1}]})
    assert engine.state.bank.houses_remaining == 2
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 480

    # No gift of houses or altered hidden random state is used in these branches.
    for n in [313, 326]:
        assert [e["payload"]["delta"] for e in packets[n]["canonical_event_segment"]
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "UNMORTGAGE"] == [-111]
    assert sum(len(person(n)["holdings"]["owned"]) for n in [287, 304]) == 16
    assert action(339)["action"] == "mortgage_property"
    assert any(e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY"
               for e in packets[339]["canonical_event_segment"])
    assert next(e["payload"]["amount"] for e in events if e["seq"] == 2188) == 200
    assert next(e["payload"]["amount"] for e in events if e["seq"] == 1610) == 500
    assert len([n for n in range(208, 234) if packets[n]["decision_type"] == "AUCTION_BID_DECISION"]) == 25
    assert all(not p["resolution"]["fallback_used"] for n, p in packets.items() if n != 183)

    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [u for u in aggregation["units"] if u["game"] == 7]
    assert {(u["player"], u["group"]): u["developed_rent_whole_game"] for u in profiles} == {
        ("p1", "ORANGE"): 270, ("p3", "PINK"): 1305, ("p4", "DARK_BLUE"): 600,
        ("p4", "GREEN"): 780, ("p4", "ORANGE"): 0}
    selected = {r["decision_id_zero_based_suffix"] for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G07") for r in c["source_entry"]["decision_refs"]}
    selected |= {34, 99, 143, 144, 152, 168, 179, 182, 183, 192, 200, 211, 224, 235,
                 251, 265, 266, 268, 277, 286, 293, 301, 329, 330, 337}
    result = {
        "scope": "All23 public entries,19 full-channel final/historical entries and complete trajectories; selected original channels, not every provider bundle reread.",
        "peer_exposure": "Prior hotel-lock, early menu, financing and release leads were peer-nominated. All branches here independently implemented.",
        "mortgage_funding": mortgage_funding, "correctly_interleaved_default_plan": recovered_build,
        "financed_nine_house_build": {"mortgages": funding, "build": nine_build},
        "management_release": {"sol329": sol_release, "opus330": opus_release, "opus330_sale": newly_accessible_sale,
                               "limits": "Separate fresh prefixes. Immediate legal choices only. No future debt escape, improved outcome or optimality assertion. Eventual338 insolvency remains unchanged in the recorded path."},
        "terminal_ceilings": [check(7, 287, 1291), check(7, 304, 741)],
        "hotel_lock_endpoint": "g07_hotel_lock.json:440 accessible versus750 debt,1310 nominal. Both mortgage orders checked separately.",
        "profiles": profiles,
        "originals": {n: {"action": action(n), "payload": payload(n), "attempts": packets[n]["attempts"],
                           "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g07_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "terminal_ceilings": [1291, 741],
                      "management_release": "both legal; own hotel upgrade unlocks an immediate sale", "profiles": profiles}))


if __name__ == "__main__":
    main()
