"""G19 original claim checks: holdings, price framing, retries and solvency."""

from collections import Counter
import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 19]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    assert {h["space_key"] for h in state(38)["you"]["holdings"]["owned"]} == {"KENTUCKY_AVENUE", "ILLINOIS_AVENUE"}
    assert "INDIANA_AVENUE" in {h["space_key"] for h in state(38)["others"][0]["holdings"]["owned"]}
    assert "TENNESSEE_AVENUE" in state(38)["bank"]["unowned_space_keys"]
    assert "$670 in cash and prime Green property value" in action(52)["public_message"]
    assert state(52)["others"][-1]["cash"] + action(52)["args"]["offer"]["cash"] == 1337
    assert "Force p3 to pay" in action(87)["private_thought"]
    assert "For me it finishes the set" in action(90)["public_message"]
    assert action(105)["args"]["request"]["cash"] == 220
    assert "Abort this trade. Do not send it." in action(135)["private_thought"]
    assert "States is pink, not orange" in action(136)["public_message"]
    received = state(136)["memory"]["public_timeline_last_20"]
    assert any(r.get("message") == action(135)["public_message"] for r in received)
    cash_round_trip = Counter()
    transfers = []
    for n in (136, 142):
        for e in packets[n]["canonical_event_segment"]:
            p = e["payload"]
            if e["type"] == "CASH_CHANGED" and p.get("reason") == "TRADE_CASH":
                cash_round_trip[p["player_id"]] += p["delta"]
            elif e["type"] == "PROPERTY_TRANSFERRED":
                transfers.append(e)
    assert dict(cash_round_trip) == {"p2": 0, "p4": 0}

    attempt_plans = {}
    for n in (55, 160, 231, 234, 307):
        attempt_plans[n] = [{"outcome": a["outcome"], "validation_errors": a["validation_errors"],
                             "tool": a["parsed_tool_call"]} for a in packets[n]["attempts"]]
    first55 = json.loads(attempt_plans[55][0]["tool"]["arguments"])["build_plan"]
    last55 = action(55)["args"]["build_plan"]
    assert sum(i["count"] for i in first55) == 12 and all(i["kind"] == "HOUSE" for i in first55)
    assert sum(i["kind"] == "HOTEL" for i in last55) == 3
    assert action(231)["private_thought"] == "fallback"
    assert all(h["houses"] == 0 for h in state(232)["others"][0]["holdings"]["owned"])

    # A payment witness is not a maximum. Here the recorded path preserves a house.
    engine, decision = restore(run, packets[310]["decision_id"])
    actor = next(p for p in engine.state.players if p.player_id == "p4")
    owned = [s for s in engine.state.board if s.owner_id == "p4"]
    assert not any(s.hotel for s in owned)
    full_upper = actor.cash + sum(s.houses * 50 for s in owned) + sum(s.price // 2 for s in owned if not s.mortgaged)
    assert full_upper == 1712
    actual_path = []
    for n in (310, 311, 312, 313):
        a = action(n)
        decision, result = apply(engine, decision, a["action"], a["args"])
        actual_path.append(result)
    assert actor.cash == 42 and not actor.bankrupt
    assert [engine.state.board[i].houses for i in (11, 13, 14)] == [0, 0, 1]
    assert any(e["type"] == "RENT_PAID" and e["payload"]["amount"] == 1400 for e in result["events"])

    # The queued card debt exposes the currently serviced recipient, not all of them.
    scenario = packets[263]["initial_prompt"]["payload"]["action_state"]["scenario"]
    assert scenario["owed_amount"] == 50 and scenario["owed_to_player_id"] == "p1"
    chairman = [e for e in packets[263]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"
                and e["payload"].get("reason") == "ELECTED_CHAIRMAN_PAY_EACH_PLAYER_50"]
    assert sum(-e["payload"]["delta"] for e in chairman if e["payload"]["player_id"] == "p3") == 100
    assert state(264)["you"]["cash"] == 77

    # Use this author's separately implemented whole-corpus fold with matching event hash.
    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    event_hash = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == event_hash
    profiles = [u for u in aggregation["units"] if u["game"] == 19]
    game = next(g for g in aggregation["games"] if g["game"] == 19)
    assert game["event_minimum_bank_houses"] == 6
    assert sum(u["spend"] for u in profiles if u["player"] == "p1") == 5300
    assert next(u for u in profiles if u["player"] == "p3")["developed_rent_whole_game"] == 175
    selected = {22, 23, 38, 52, 54, 55, 69, 70, 85, 87, 90, 91, 98, 100, 105, 135, 136,
                142, 155, 160, 173, 174, 175, 176, 180, 224, 225, 229, 230, 231, 232,
                234, 245, 246, 255, 256, 258, 259, 260, 263, 264, 278, 284, 290, 293,
                301, 303, 307, 308, 310, 311, 312, 313, 315, 316, 320, 322}
    report = {"source_scope": "Complete extraction narrative and catalog; selected original fields and attempts; original event fold reused with hash match; exact local replay only.",
              "originals": {n: {"action": action(n), "payload": packets[n]["initial_prompt"]["payload"],
                                  "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
              "zero_cash_round_trip": {"cash": dict(cash_round_trip), "deed_transfers": transfers},
              "retry_plans": attempt_plans,
              "survival310": {"actual_raised_plus_starting_cash": 1442, "full_liquidation_upper_bound": full_upper,
                              "recorded_path_replay": actual_path, "remaining_cash": 42,
                              "limits": "1442 is the funding used, not a maximum;1712 is a house-only arithmetic upper bound. No alternative winner simulated."},
              "chairman": {"delivered_scenario": scenario, "actual_payments": chairman},
              "profiles_from_independent_event_fold": profiles, "bank_stock_summary": game,
              "liquidation_ceilings": [check(19, 225, 502), check(19, 284, 409), check(19, 322, 512)],
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "canonical_event_sha256": event_hash,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g19_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"cash_round_trip": dict(cash_round_trip), "survival_cash": 42,
                      "full_upper": full_upper, "bank_minimum": 6, "terminal_ceilings": [502, 409, 512]}))


if __name__ == "__main__":
    main()
