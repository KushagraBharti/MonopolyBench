"""Check five attempted light-blue builds followed by applied engine defaults.

Each alternative changes only the order/size of purchase operations, keeping the
same nine-house final allocation. It stops after the build, not at a game outcome.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.replay import canonical_event_lines

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE1 = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"
TARGETS = (75, 81, 99, 114, 129)
LIGHT_BLUES = ("ORIENTAL_AVENUE", "VERMONT_AVENUE", "CONNECTICUT_AVENUE")
INDICES = (6, 8, 9)


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    units = [u for u in rows(PHASE1 / "review_unit_ledger.jsonl")
             if u["game"] == 2 and int(u["decision_id"].rsplit("-", 1)[1]) in TARGETS]
    assert len(units) == len(TARGETS)
    packets = [rows(ROOT / u["packet"])[u["packet_line"] - 1] for u in units]
    run = ROOT / packets[0]["source_run"]
    config = json.loads((run / "run_config.json").read_text())
    actions, events = rows(run / "actions.jsonl"), rows(run / "events.jsonl")
    cases = []
    for unit, packet in zip(units, packets, strict=True):
        target = next(i for i, a in enumerate(actions) if a["decision_id"] == packet["decision_id"])
        assert target in TARGETS
        engine = Engine(seed=config["seed"], players=config["players"], run_id=config["run_id"],
                        max_turns=config["max_turns"], max_trade_exchanges=config["max_trade_exchanges"],
                        max_auction_actions=config["max_auction_actions"])
        prefix = []
        for record in actions[:target]:
            _, emitted, decision, _ = engine.advance_until_decision(max_steps=100_000)
            prefix.extend(emitted)
            assert decision["decision_id"] == record["decision_id"]
            _, emitted, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
            prefix.extend(emitted)
        _, emitted, decision, _ = engine.advance_until_decision(max_steps=100_000)
        prefix.extend(emitted)
        assert decision["decision_id"] == packet["decision_id"]
        assert canonical_event_lines(prefix) == canonical_event_lines(events[:len(prefix)])
        resolution = packet["resolution"]
        assert resolution["fallback_used"]
        assert resolution["final_action"]["action"] == "end_turn"
        assert resolution["final_action"]["public_message"] == ""
        attempts = []
        for attempt in packet["attempts"]:
            call = attempt["parsed_tool_call"]
            plan = json.loads(call["arguments"])["build_plan"] if call else None
            if call:
                assert call["name"] == "build_houses_or_hotel"
                assert plan == [{"space_key": key, "kind": "HOUSE", "count": 3} for key in LIGHT_BLUES]
                assert attempt["validation_errors"] == [
                    "Uneven intermediate building operation; interleave purchases across the group."]
            attempts.append({"index": attempt["attempt_index_zero_based"], "outcome": attempt["outcome"],
                             "response_condition": attempt["response_condition"],
                             "action_name": call["name"] if call else None,
                             "build_plan": plan, "validation_errors": attempt["validation_errors"]})
        expected = ["illogical", "refused"] if target == 129 else ["refused", "illogical"]
        assert [a["outcome"] for a in attempts] == expected
        assert sum(a["action_name"] == "build_houses_or_hotel" for a in attempts) == 1
        assert "build_houses_or_hotel" in {a["action"] for a in decision["legal_actions"]}
        actor = packet["player_id"]
        initial = engine.get_snapshot()
        before = next(p for p in initial["players"] if p["player_id"] == actor)
        assert before["cash"] == packet["initial_prompt"]["payload"]["game_state"]["you"]["cash"]
        for space in initial["board"]:
            if space["index"] in INDICES:
                assert space["owner_id"] == actor and not space["mortgaged"]
                assert space["houses"] == 0 and not space["hotel"]
        plan = [{"space_key": key, "kind": "HOUSE", "count": 1} for _ in range(3) for key in LIGHT_BLUES]
        alternate = {"schema_version": "v1", "decision_id": decision["decision_id"],
                     "action": "build_houses_or_hotel", "args": {"build_plan": plan}}
        _, branch_events, _, _ = engine.apply_action(alternate)
        final = engine.get_snapshot()
        after = next(p for p in final["players"] if p["player_id"] == actor)
        assert before["cash"] - after["cash"] == 450
        final_blues = [s for s in final["board"] if s["index"] in INDICES]
        assert len(final_blues) == 3 and all(s["houses"] == 3 and not s["hotel"] for s in final_blues)
        cases.append({"game": 2, "decision_id": packet["decision_id"], "turn_index": packet["turn_index"],
                      "source_unit": unit, "source_lines": packet["source_lines"],
                      "physical_responses": packet["physical_responses"],
                      "recorded_action": packet["applied_action_record"],
                      "recorded_events": packet["canonical_event_segment"],
                      "fallback_reason": resolution["fallback_reason"], "attempts": attempts,
                      "recorded_prefix_equal": True, "cash_before": before["cash"],
                      "legal_interleaved_action": alternate, "alternate_build_cost": 450,
                      "cash_after_alternate_build": after["cash"], "alternate_light_blues": final_blues,
                      "branch_events": branch_events})
    report = {"version": "g02_build_fallback_audit_v1", "cases": cases,
              "selection": "The five public-scope G02-C005 fallback decisions flagged by Sonnet, checked independently against canonical response chains and the engine.",
              "interpretation": "Each of the five decision chains contains a request for an affordable nine-house light-blue build using invalid intermediate purchase ordering. The applied end-turn was the deterministic fallback. The last case has invalid-first/refusal-second order, unlike the first four. Keep these in configured-agent outcomes; they do not evidence a deliberate decision to refrain from building.",
              "scope": "Immediate legal construction feasibility only. No altered historical results, later counterfactual outcomes, optimality, or latent-intent inference.",
              "sources": [{"path": str((run / name).relative_to(ROOT)),
                           "sha256": hashlib.sha256((run / name).read_bytes()).hexdigest()}
                          for name in ("run_config.json", "events.jsonl", "actions.jsonl", "decisions.jsonl")],
              "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest()}
    (HERE / "g02_build_fallback_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checked_fallbacks": len(cases), "exact_prefixes": len(cases),
                      "legal_equivalent_final_allocations": len(cases),
                      "attempt_orders": [c["attempts"][0]["outcome"] for c in cases]}))


if __name__ == "__main__":
    main()
