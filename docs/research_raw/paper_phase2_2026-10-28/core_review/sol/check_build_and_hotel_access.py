"""Exact-prefix in-memory legality checks, not alternate winner estimates.

The G13 hypothesis came from Opus's audit, after Sol's initial trajectory note.
The implementation independently replays original actions and compares events.
"""

import copy
import hashlib
import json
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.replay import canonical_event_lines

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def prefix(game, suffix):
    ledger = rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
    unit = next(x for x in ledger if x["game"] == game and x["decision_id"].endswith(f"{suffix:06d}"))
    packet = rows(ROOT / unit["packet"])[unit["packet_line"] - 1]
    run = ROOT / packet["source_run"]
    config = json.loads((run / "run_config.json").read_text())
    engine = Engine(**{key: config[key] for key in ["seed", "players", "run_id", "max_turns", "max_trade_exchanges", "max_auction_actions"]})
    observed = []
    for record in rows(run / "actions.jsonl"):
        _, events, decision, _ = engine.advance_until_decision(max_steps=100_000)
        observed.extend(events)
        assert decision["decision_id"] == record["decision_id"]
        if decision["decision_id"] == unit["decision_id"]:
            break
        _, events, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
        observed.extend(events)
    assert canonical_event_lines(observed) == canonical_event_lines(rows(run / "events.jsonl")[:len(observed)])
    provenance = {"unit": unit, "canonical_prefix_equal": True, "prefix_events": len(observed),
                  "source_hashes": {name: hashlib.sha256((run / name).read_bytes()).hexdigest() for name in ["events.jsonl", "actions.jsonl", "run_config.json"]}}
    return engine, decision, packet, provenance


def build_check():
    engine, decision, packet, evidence = prefix(13, 93)
    rejected = packet["attempts"][1]
    assert rejected["outcome"] == "illogical"
    args = json.loads(rejected["parsed_tool_call"]["arguments"])
    original = copy.deepcopy(args["build_plan"])
    remaining = [entry["count"] for entry in original]
    interleaved = []
    while any(remaining):
        for index, entry in enumerate(original):
            if remaining[index]:
                interleaved.append({**entry, "count": 1})
                remaining[index] -= 1
    before = engine.get_snapshot()
    actor = decision["player_id"]
    cash_before = next(x["cash"] for x in before["players"] if x["player_id"] == actor)
    args["build_plan"] = interleaved
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": "build_houses_or_hotel", "args": {"build_plan": interleaved}}
    _, events, following, _ = engine.apply_action(action)
    assert not any(x["type"] == "ACTION_REJECTED" for x in events), events
    after = engine.get_snapshot()
    cash_after = next(x["cash"] for x in after["players"] if x["player_id"] == actor)
    assert cash_before - cash_after == 600
    builds = [x for x in events if x["type"] == "HOUSE_BUILT"]
    assert len(builds) == 6
    return {**evidence, "original_rejected_plan": original, "interleaved_plan": interleaved,
            "cash_before": cash_before, "cash_after": cash_after,
            "rejected_attempt": {k: rejected[k] for k in ["outcome", "validation_errors", "response_condition"]},
            "recorded_applied_action": packet["applied_action_record"],
            "counterfactual_build_events": events, "following_decision": following,
            "claim": "The same six-house plan is legal and affordable at the exact prefix when interleaved; no subsequent winner or rent counterfactual tested."}


def hotel_check():
    engine, decision, packet, evidence = prefix(7, 339)
    before = engine.get_snapshot()
    options = decision["liquidation"]["options"]
    assert not options["sellable_building_space_indices"]
    actor = decision["player_id"]
    held = [{"index": s.index, "name": s.name, "houses": s.houses, "hotel": s.hotel,
             "mortgaged": s.mortgaged, "price": s.price} for s in engine.state.board if s.owner_id == actor]
    # The sole non-declaration entry action is the historical Oriental mortgage.
    # Reapply it to verify the episode endpoint rather than equating the entry
    # menu with all possible later liquidation menus in a more general estate.
    assert options["mortgageable_space_indices"] == [6]
    _, applied_events, _, _ = engine.apply_action(packet["applied_action_record"]["action"],
                                                 decision_meta=packet["applied_action_record"].get("decision_meta"))
    estate = [e for e in applied_events if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY_CASH" and e["payload"]["delta"] > 0]
    assert len(estate) == 1 and estate[0]["payload"]["delta"] == 440
    assert next(p["bankrupt"] for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
    return {**evidence, "snapshot": before, "decision": decision, "held": held,
            "recorded_events": packet["canonical_event_segment"],
              "sole_mortgage_action_events": applied_events, "after": engine.get_snapshot(),
              "claim": "No building sale is offered. The only non-declaration liquidation move, Oriental mortgage50, raises390to440and triggers automatic bankruptcy on750. Entry alternatives and this endpoint establish440accessible here, not a generic current-menu rule. No artificial supply intervention or alternate winner."}


def main():
    report = {"build_check": build_check(), "hotel_check": hotel_check(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "build_and_hotel_access.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"build": {k: report["build_check"][k] for k in ["cash_before", "cash_after", "prefix_events", "canonical_prefix_equal", "claim"]},
                      "hotel": {"canonical_prefix_equal": report["hotel_check"]["canonical_prefix_equal"], "held": report["hotel_check"]["held"],
                                "liquidation": report["hotel_check"]["decision"]["liquidation"],
                                "legal_actions": [x["action"] for x in report["hotel_check"]["decision"]["legal_actions"]]}}, indent=2))


if __name__ == "__main__":
    main()
