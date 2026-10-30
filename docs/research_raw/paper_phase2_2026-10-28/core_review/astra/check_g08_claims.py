"""Read-only G8 accounting, source checks and exact local construction branches."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 8]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    b = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / b[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return b[n]["applied_action_record"]["action"]

    def state(n):
        return b[n]["initial_prompt"]["payload"]["game_state"]

    def person(n, player=None):
        s = state(n)
        return next(p for p in [s["you"], *s["others"]]
                    if p["player_id"] == (player or s["you"]["player_id"]))

    assert sum(action(n)["action"] == "counter_trade" for n in range(57, 64)) == 5
    assert sum(action(n)["action"] == "counter_trade" for n in range(64, 70)) == 4
    assert person(63, "p3")["cash"] == 1235 and person(64, "p3")["cash"] == 885
    assert person(69, "p2")["cash"] == 1129 and person(70, "p2")["cash"] == 1679
    assert person(70, "p3")["cash"] == 335
    marvin = [n for n in b if action(n)["action"] == "propose_trade"
              and b[n]["player_id"] == "p2" and n < 150
              and "MARVIN_GARDENS" in action(n)["args"]["request"]["properties"]]
    assert marvin == [75, 77, 90, 106, 113, 147]
    assert action(167)["args"]["request"]["properties"] == ["NORTH_CAROLINA_AVENUE"]
    assert "VIRGINIA_AVENUE" in [s["space_key"] for s in person(158, "p1")["holdings"]["owned"]]
    all_owned = {s["space_key"] for p in [state(158)["you"], *state(158)["others"]]
                 for s in p["holdings"]["owned"]}
    assert {"ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"} <= all_owned
    assert person(158)["cash"] == 444 and person(159, "p4")["cash"] == 744
    assert "second trade" in action(156)["public_message"]
    assert "Park Place" in action(158)["private_thought"]
    assert sum(e["payload"]["delta"] for n in range(159, 163)
               for e in b[n]["canonical_event_segment"]
               if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE") == 310

    branches = []
    for n, expected in [(163, 172), (164, 172), (174, 176), (177, 4)]:
        assert action(n)["action"] == "end_turn" and not b[n]["resolution"]["fallback_used"]
        content = json.loads(b[n]["attempts"][0]["assistant_content"])
        assert content["name"] == "build_houses_or_hotel"
        plan = content.get("arguments", content.get("parameters"))["build_plan"]
        ordered = [{**p, "count": 1} for i in range(max(p["count"] for p in plan))
                   for p in plan if p["count"] > i]
        engine, decision = restore(run, b[n]["decision_id"])
        _, result = apply(engine, decision, "build_houses_or_hotel", {"build_plan": ordered})
        assert next(p.cash for p in engine.state.players if p.player_id == "p1") == expected
        branches.append({"decision": n, "content_plan": plan, "legal_ordered_plan": ordered,
                         "remaining_cash": expected, "branch": result,
                         "limit": "Immediate legal construction only;177 requires interleaving. No later rent or winner counterfactual."})
    assert person(187)["cash"] == 704 and person(188)["cash"] == 104
    assert not any(e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == "p1"
                   and e["seq"] > b[187]["resolution"]["emitted_event_seq_end"] for e in events)
    assert [e["payload"]["amount"] for e in events if e["type"] == "RENT_PAID"
            and e["payload"]["to_player_id"] == "p1" and 1152 < e["seq"] < 1350] == [28, 28]
    assert action(176)["action"] == "roll_for_doubles" and action(181)["action"] == "pay_jail_fine"
    assert "post-roll" in action(176)["private_thought"] and "immediately ends" in action(181)["private_thought"]
    assert person(184)["cash"] == 508
    assert person(203)["cash"] == 104 and person(204, "p1")["cash"] == 304
    assert person(209)["cash"] == 100
    assert 100 + 575 >= 3 * 200 and 100 + 575 < 4 * 200
    assert "three houses on Dark Blue" in action(209)["public_message"]
    assert "3 houses each" in action(209)["private_thought"]
    assert "would put developed Browns" in action(249)["private_thought"]
    assert "Holding my $640" in action(215)["private_thought"]
    assert person(260)["cash"] == 13 and person(263, "p4")["cash"] == 133
    assert person(263, "p2")["cash"] == 507
    for n, value in [(207, 56), (274, 221)]:
        assert [e["payload"]["delta"] for e in b[n]["canonical_event_segment"]
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "UNMORTGAGE"] == [-value]
    assert all(b[n]["initial_prompt"]["payload"]["action_state"]["available_actions"] == ["roll_for_doubles"]
               for n in [278, 281, 285])
    assert not any(p["resolution"]["fallback_used"] for p in b.values())
    opus = [p for p in b.values() if p["player_id"] == "p2"]
    assert all([a["outcome"] for a in p["attempts"]] == ["refused", "valid"] for p in opus)
    selected = sorted({16, 25, 27, 50, 52, 54, 58, 60, 62, 63, 65, 67, 69, 72, 76, 78, 91, 97,
                       107, 120, 122, 124, 136, 143, 144, 147, 148, *range(154, 165), 166,
                       170, 171, 172, 174, 176, 177, 181, 184, 187, 188, *range(192, 197),
                       200, 201, 203, 207, 209, 210, 211, 215, 220, 239, 241, 243, 249,
                       *range(257, 265), 267, 271, 273, 274, 275, 277, 280, 282, 286, 287})
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    development = json.loads((HERE / "development_aggregation_check.json").read_text())
    assert development["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [r for r in development["units"] if r["game"] == 8]
    result = {"game": 8, "checks": "passed", "trade_counter_counts": [5, 4],
              "early_marvin_proposals": marvin, "legal_build_branches": branches,
              "post_build_grok_paid_rent": 0, "opus_refused_then_valid_decisions": len(opus),
              "terminal_ceilings": [check(8, 271, 308), check(8, 280, 666), check(8, 287, 309)],
              "profiles": profiles, "originals": {n: b[n] for n in selected},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g08_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "profiles": profiles,
                      "terminal_ceilings": [308, 666, 309], "opus_valid_recoveries": len(opus)}))


if __name__ == "__main__":
    main()
