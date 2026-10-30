"""G01 original chronology, set conditions, income and terminal financing."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 1]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    def turn(n):
        return packets[n]["canonical_event_segment"][0]["turn_index"]

    assert [turn(n) for n in (118, 128, 129)] == [40, 43, 43]
    assert action(181)["args"]["bid_amount"] == 180
    assert action(184)["args"]["bid_amount"] == 220
    assert "$25 to you" in action(185)["public_message"]
    assert action(186)["action"] == "drop_out"
    assert "$220 cap" in action(186)["private_thought"]
    assert "cap near $220" in action(181)["private_thought"]
    assert action(293)["args"]["offer"]["properties"] == ["ST_CHARLES_PLACE", "VIRGINIA_AVENUE", "PACIFIC_AVENUE"]
    assert "STATES_AVENUE" in {h["space_key"] for h in state(294)["you"]["holdings"]["owned"]}
    assert action(294)["action"] == "reject_trade"
    assert "right in front of me" in action(294)["private_thought"]
    paid = [e for e in events if e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == "p1"
            and e["payload"]["to_player_id"] == "p3"]
    assert [e["payload"]["amount"] for e in paid] == [28, 20, 600, 550, 550]
    assert sum(e["payload"]["amount"] for e in paid) == 1748
    appeals = {n: [r for r in state(n)["memory"]["public_timeline_last_20"]
                   if r.get("message") == action(315)["public_message"]] for n in (316, 318)}
    assert appeals == {316: [], 318: []}
    assert next(h for h in state(485)["you"]["holdings"]["owned"] if h["space_key"] == "MARVIN_GARDENS")["mortgaged"] is False
    late_rents = [e for e in events if e["type"] == "RENT_PAID" and e["seq"] >= 3300
                  and e["payload"]["from_player_id"] == "p4"]
    assert any(e["payload"]["space_index"] == 31 and e["payload"]["amount"] == 1100 for e in late_rents)
    assert any(e["payload"]["space_index"] == 8 and e["payload"]["amount"] == 550 for e in late_rents)

    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [u for u in aggregation["units"] if u["game"] == 1]
    eligible = [n for n, p in packets.items() if p["initial_prompt"]["payload"]["game_state"]["you"]["player_id"] == "p3"
                and "propose_trade" in p["initial_prompt"]["payload"]["action_state"]["available_actions"]]
    assert len(eligible) == 66
    assert not any(action(n)["action"] == "propose_trade" for n in eligible)
    selected = {54, 76, 108, 109, 111, 112, 118, 119, 128, 129, 154, 181, 184,
                185, 186, 263, 268, 269, 278, 284, 289, 293, 294, 309, 315,
                316, 318, 342, 350, 366, 370, 371, 373, 375, 379, 380, 383,
                387, 400, 421, 422, 426, 448, 449, 450, 451, 452, 454, 466,
                468, 471, 473, 478, 485}
    report = {"scope": "Complete extracted narrative and 28 public entries; selected original actions and prompts; independent event arithmetic and terminal replay. Full original semantic reread not claimed.",
              "trade_and_build_turns": [turn(n) for n in (118, 128, 129)],
              "opus_paid_rent_to_winner": paid,
              "terminal_appeal_exact_text_in_two_recipient_timelines": appeals,
              "winner_proposal_eligible_decisions": len(eligible),
              "winner_initiated_proposals": 0,
              "late_rents": late_rents,
              "profiles": profiles,
              "terminal_ceilings": [check(1, 315, 318), check(1, 454, 121), check(1, 485, 170)],
              "originals": {n: {"action": action(n), "payload": packets[n]["initial_prompt"]["payload"],
                                  "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "canonical_event_sha256": digest,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g01_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"rent": 1748, "terminal_ceilings": [318, 121, 170], "winner_proposals": 0,
                      "eligible_decisions": len(eligible), "profiles": profiles}))


if __name__ == "__main__":
    main()
