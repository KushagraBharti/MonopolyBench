"""Local supply diagnostics, not alternative legal game histories or winners.

Rebuild two recorded prefixes. For each, compare the engine's build predicate
with an explicitly artificial extra bank house. In game 14 first perform the
legal redemption needed to make the completed group developable. This separates
immediate availability from availability reachable through own financing.
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


def check(game, suffix, space_key, index, redeem=None):
    units = rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
    unit = next(u for u in units if u["game"] == game and u["decision_id"].endswith(f"{suffix:06d}"))
    packet = rows(ROOT / unit["packet"])[unit["packet_line"] - 1]
    run = ROOT / packet["source_run"]
    config = json.loads((run / "run_config.json").read_text())
    engine = Engine(**{k: config[k] for k in ["seed", "players", "run_id", "max_turns",
                                            "max_trade_exchanges", "max_auction_actions"]})
    actions, recorded = rows(run / "actions.jsonl"), rows(run / "events.jsonl")
    prefix = []
    for record in actions:
        _, events, decision, _ = engine.advance_until_decision(max_steps=100_000)
        prefix.extend(events)
        assert decision["decision_id"] == record["decision_id"]
        if record["decision_id"] == unit["decision_id"]:
            break
        _, events, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
        prefix.extend(events)
    assert canonical_event_lines(prefix) == canonical_event_lines(recorded[:len(prefix)])
    actor = decision["player_id"]
    original = engine.get_snapshot()
    redemption_events = []
    if redeem:
        redemption = {"schema_version": "v1", "decision_id": decision["decision_id"],
                      "action": "unmortgage_property", "args": {"space_key": redeem}}
        assert engine.validate_action_for_decision(redemption, decision) == []
        _, redemption_events, decision, _ = engine.apply_action(redemption)
        assert decision["decision_type"] == "POST_TURN_ACTION_DECISION"
        assert decision["player_id"] == actor
    base = engine.get_snapshot()
    player = next(p for p in engine.state.players if p.player_id == actor)
    assert engine.state.bank.houses_remaining == 0
    actual_buildable = engine._buildable_space_indices(player)
    assert index not in actual_buildable
    plan = [{"space_index": index, "kind": "HOUSE", "count": 1}]
    try:
        engine._validate_build_plan(player, plan)
    except ValueError as exc:
        original_error = str(exc)
    else:
        raise AssertionError("The actual supply-constrained build unexpectedly passed")
    assert "Bank houses exhausted" in original_error
    diagnostic = copy.deepcopy(engine)
    diagnostic.state.bank.houses_remaining = 1
    diagnostic_player = next(p for p in diagnostic.state.players if p.player_id == actor)
    available = diagnostic._buildable_space_indices(diagnostic_player)
    assert index in available
    validation = diagnostic._validate_build_plan(diagnostic_player, plan)
    # No alternative action is applied after introducing an artificial house.
    return {
        "game": game, "decision_id": unit["decision_id"], "unit": unit,
        "canonical_prefix_equal": True, "original_snapshot": original,
        "original_applied_action": record["action"],
        "legal_redemption_before_diagnostic": redeem, "redemption_events": redemption_events,
        "state_after_optional_redemption": base, "target": space_key,
        "buildable_indices_at_actual_supply": actual_buildable,
        "original_build_error": original_error,
        "artificial_supply_check": {"houses_changed": [0, 1],
                                    "target_becomes_buildable": True,
                                    "validated_build_cost": validation["total_cost"]},
        "limitations": "Artificial supply relaxation is a predicate diagnostic, not a feasible historical intervention, executed rival response, optimality or winner effect.",
        "source_sha256": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                          for n in ["run_config.json", "actions.jsonl", "events.jsonl"]},
    }


def main():
    report = {"version": 1, "cases": [check(4, 252, "VIRGINIA_AVENUE", 14),
                                       check(14, 220, "PARK_PLACE", 37, "PARK_PLACE")],
              "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "supply_constraint_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    for case in report["cases"]:
        actor = case["original_applied_action"]["decision_id"]
        print(json.dumps({"decision": actor, "redemption": case["legal_redemption_before_diagnostic"],
                          "actual_error": case["original_build_error"],
                          "one_extra_house_makes_build_legal": True}))


if __name__ == "__main__":
    main()
