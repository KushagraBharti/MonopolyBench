"""Attach canonical evidence and observed follow-up to three feasibility checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FOUNDATION = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def observed_success(ledger):
    """A targeted observed counterexample, not an experimental control group."""
    units = [next(u for u in ledger.values() if u["game"] == 17
                  and u["decision_id"].endswith(f"{i:06d}")) for i in range(253, 257)]
    packets = [rows(ROOT / u["packet"])[u["packet_line"] - 1] for u in units]
    actions = [p["applied_action_record"]["action"] for p in packets]
    assert [a["action"] for a in actions] == ["mortgage_property", "sell_houses_or_hotel",
                                              "sell_houses_or_hotel", "mortgage_property"]
    assert actions[0]["args"] == {"space_key": "MARVIN_GARDENS"}
    assert actions[3]["args"] == {"space_key": "INDIANA_AVENUE"}
    cash = [p["initial_prompt"]["payload"]["game_state"]["you"]["cash"] for p in packets]
    assert cash == [38, 128, 278, 503]
    events = [e for p in packets for e in p["canonical_event_segment"]]
    payments = [e for e in events if e["type"] == "RENT_PAID"]
    assert len(payments) == 1
    assert payments[0]["payload"] == {"amount": 550, "from_player_id": "p1",
                                      "space_index": 18, "to_player_id": "p2"}
    changes = [e for e in events if e["type"] == "CASH_CHANGED"
               and e["payload"]["player_id"] == "p1"]
    assert [e["payload"]["delta"] for e in changes] == [140, -50, 150, 225, 110, -550]
    return {"case_id": "astra_g17_d000253_000256_successful_liquidation",
            "status": "targeted_astra_review_pending_independent_core_adjudication",
            "selection": "Observed follow-up in game 17, chosen as a counterexample to premature insolvency calculations.",
            "game": 17, "model": "Opus", "source_units": units,
            "source_packets": packets, "cash_before_each_decision": cash,
            "cash_after_payment": cash[0] + sum(e["payload"]["delta"] for e in changes),
            "payment_event": payments[0],
            "interpretation": "The applied sequence sells the red houses, then uses the newly available mortgage to pay. This is observed payment success, not optimality or a general model comparison.",
            "scope": "Ends at the recorded $550 payment at event 1690. Does not claim later victory."}


def main():
    proof = json.loads((HERE / "feasible_liquidation.json").read_text())
    ledger = {row["decision_id"]: row for row in rows(FOUNDATION / "review_unit_ledger.jsonl")}
    results = []
    for case in proof["cases"]:
        screen = case["case"]
        unit = ledger[screen["decision_id"]]
        packet = rows(ROOT / unit["packet"])[unit["packet_line"] - 1]
        run = ROOT / packet["source_run"]
        events = rows(run / "events.jsonl")
        decisions = rows(run / "decisions.jsonl")
        start = next(i for i, d in enumerate(decisions)
                     if d.get("phase") == "decision_started" and d["decision_id"] == screen["decision_id"])
        public = packet["applied_action_record"]["action"].get("public_message")
        exposures = []
        for record in decisions[start + 1:]:
            if record.get("phase") != "decision_started" or record["player_id"] == case["actor"]:
                continue
            timeline = record["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]
            matches = [entry for entry in timeline if entry.get("message") == public
                       and entry.get("player_id") == case["actor"]]
            if matches:
                exposures.append({"decision_id": record["decision_id"], "recipient": record["player_id"],
                                  "turn": record["turn_index"], "entries": matches})
        occurrences = [e for e in events if e["type"] == "LLM_PUBLIC_MESSAGE"
                       and e["payload"].get("player_id") == case["actor"]
                       and e["payload"].get("message") == public]
        assert len(occurrences) == 1, "Repeated utterance needs occurrence-level attribution"
        focal = next(e for e in packet["canonical_event_segment"] if e["type"] == "LLM_DECISION_RESPONSE")
        creditor = screen["owed_to"]
        board = case["initial_snapshot"]["board"]
        inherited = [s for s in board if s.get("owner_id") == case["actor"]]
        spaces = {s["index"] for s in inherited}
        transfers = [e for e in packet["canonical_event_segment"]
                     if e["type"] == "PROPERTY_PURCHASED" and e["payload"]["player_id"] == creditor]
        assert {e["payload"]["space_index"] for e in transfers} == spaces
        assert all(e["payload"]["price"] == 0 for e in transfers)
        followup = [e for e in events if e["seq"] > focal["seq"] and e["type"] == "RENT_PAID"
                    and e["payload"]["to_player_id"] == creditor and e["payload"]["space_index"] in spaces]
        end = next(e for e in reversed(events) if e["type"] == "GAME_ENDED")
        notes = []
        for attempt in packet["attempts"]:
            raw = attempt.get("raw_response") or {}
            messages = [c.get("message", {}) for c in raw.get("choices", [])]
            notes.append({"index": attempt["attempt_index_zero_based"], "outcome": attempt["outcome"],
                          "response_condition": attempt["response_condition"],
                          "assistant_content": attempt["assistant_content"],
                          "parsed_tool_call": attempt["parsed_tool_call"],
                          "messages": messages})
        final_actor = next(p for p in case["final_snapshot"]["players"] if p["player_id"] == case["actor"])
        results.append({
            "case_id": f"astra_g{screen['game']:02d}_d{screen['decision_id'].rsplit('-', 1)[1]}_liquidation",
            "status": "targeted_astra_review_pending_independent_core_adjudication",
            "game": screen["game"], "model": screen["model"], "decision_id": screen["decision_id"],
            "source_packet": unit["packet"], "source_packet_line": unit["packet_line"],
            "source_run": packet["source_run"], "source_lines": packet["source_lines"],
            "physical_responses": packet["physical_responses"],
            "timeline_exposure": {"exact_same_speaker_text_later_opponent_prompts": exposures,
                                  "unique_canonical_utterance": True,
                                  "scope": "Recorded initial public timeline prompts only; not semantic exposure through every possible field, belief or influence."},
            "prompt_observation": packet["initial_prompt"]["payload"],
            "applied_action": packet["applied_action_record"], "attempts": notes,
            "original_event_segment": packet["canonical_event_segment"],
            "creditor": creditor, "cash_before": screen["cash"], "debt": screen["owed"],
            "inherited_deeds": inherited,
            "observed_followup": {"endpoint": end, "inherited_deed_rent_events": followup,
                                  "rent_paid_to_original_creditor": sum(e["payload"]["amount"] for e in followup),
                                  "interpretation": "Observed receipts on these deeds. Not incremental profit or a causal effect of bankruptcy; subsequent development and transfers may occur."},
            "verified_alternative": {"prefix_matches": case["recorded_prefix_equal"],
                                     "actions": case["feasible_liquidation_actions"],
                                     "payment_event": case["payment_event"],
                                     "cash_after_payment": final_actor["cash"],
                                     "bankrupt_after_payment": final_actor["bankrupt"],
                                     "followup": "Ends once this debt is paid; no later counterfactual outcome."},
            "sources": case["canonical_sources"],
        })
    success = observed_success(ledger)
    assert success["cash_after_payment"] == 63
    output = {"version": "liquidation_case_evidence_v2", "cases": results,
              "observed_successful_liquidation": success,
              "selection": proof["selection"], "coverage": "Three targeted bankruptcy cases and one observed repayment episode. Not exhaustive semantic corpus review.",
              "proof_sha256": hashlib.sha256((HERE / "feasible_liquidation.json").read_bytes()).hexdigest()}
    (HERE / "liquidation_case_evidence.json").write_text(json.dumps(output, indent=2) + "\n")
    for case in results:
        print(json.dumps({"case_id": case["case_id"], "inherited_deeds": len(case["inherited_deeds"]),
                          "inherited_houses": sum(s["houses"] for s in case["inherited_deeds"]),
                          "followup_rents": case["observed_followup"]["rent_paid_to_original_creditor"],
                          "rent_events": len(case["observed_followup"]["inherited_deed_rent_events"])}))


if __name__ == "__main__":
    main()
