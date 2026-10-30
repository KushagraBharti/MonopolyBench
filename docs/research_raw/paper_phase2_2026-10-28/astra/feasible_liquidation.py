"""Construct legal debt-payment sequences for three screened bankruptcy cases.

Replays the recorded prefix in memory, then uses only offered liquidation actions.
No original run is changed, no provider is called, and no future winner is inferred.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.replay import canonical_event_lines

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FOUNDATION = ROOT / "docs/research_raw/paper_phase1_2026-10-28"


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    manifest = json.loads((FOUNDATION / "astra/visibility_manifest.json").read_text())
    screened = json.loads((FOUNDATION / "fable/fable_surrender_scan.json").read_text())
    candidates = [r for r in screened["surrender_with_financing_options"] if r["shortfall_coverable_upper_bound"]]
    board = json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"]
    keys = {s["index"]: re.sub(r"[^A-Za-z0-9]+", "_", s["name"]).strip("_").upper() for s in board}
    results = []
    for candidate in candidates:
        game = next(g for g in manifest["games"] if g["game"] == candidate["game"])
        run = ROOT / game["package"] / "run"
        config = json.loads((run / "run_config.json").read_text())
        actions = read_rows(run / "actions.jsonl")
        recorded_events = read_rows(run / "events.jsonl")
        target = next(i for i, action in enumerate(actions) if action["decision_id"] == candidate["decision_id"])
        engine = Engine(seed=config["seed"], players=config["players"], run_id=config["run_id"],
                        max_turns=config["max_turns"], max_trade_exchanges=config["max_trade_exchanges"],
                        max_auction_actions=config["max_auction_actions"])
        prefix = []
        for record in actions[:target]:
            _, events, decision, _ = engine.advance_until_decision(max_steps=100_000)
            prefix.extend(events)
            assert decision["decision_id"] == record["decision_id"]
            _, events, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
            prefix.extend(events)
        _, events, decision, _ = engine.advance_until_decision(max_steps=100_000)
        prefix.extend(events)
        assert decision["decision_id"] == candidate["decision_id"]
        assert canonical_event_lines(prefix) == canonical_event_lines(recorded_events[:len(prefix)])
        actor = decision["player_id"]
        assert decision["liquidation"]["owed_amount"] == candidate["owed"]
        initial = engine.get_snapshot()
        path, branch_events = [], []
        while decision and decision["decision_type"] == "LIQUIDATION_DECISION":
            assert decision["player_id"] == actor
            options = decision["liquidation"]["options"]
            if options["mortgageable_space_indices"]:
                index = min(options["mortgageable_space_indices"])
                name, arguments = "mortgage_property", {"space_key": keys[index]}
            elif options["sellable_building_space_indices"]:
                index = min(options["sellable_building_space_indices"])
                space = engine.state.board[index]
                name = "sell_houses_or_hotel"
                arguments = {"sell_plan": [{"space_key": keys[index], "kind": "HOTEL" if space.hotel else "HOUSE", "count": 1}]}
            else:
                raise AssertionError("Constructive sequence exhausted legal financing")
            assert name in {item["action"] for item in decision["legal_actions"]}
            before = next(p for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
            action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": arguments}
            _, events, decision, _ = engine.apply_action(action)
            after = next(p for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
            assert not after["bankrupt"]
            path.append({"action": action, "cash_before": before["cash"], "cash_after": after["cash"],
                         "event_types": [e["type"] for e in events], "offered_options": options})
            branch_events.extend(events)
            assert len(path) <= 100
        payments = [e for e in branch_events if e["type"] == "RENT_PAID"
                    and e["payload"]["from_player_id"] == actor
                    and e["payload"]["to_player_id"] == candidate["owed_to"]
                    and e["payload"]["amount"] == candidate["owed"]]
        assert len(payments) == 1, "The exact recorded debt was not paid once"
        final = engine.get_snapshot()
        results.append({"case": candidate, "actor": actor, "recorded_prefix_equal": True,
                        "recorded_action": actions[target]["action"], "initial_snapshot": initial,
                        "feasible_liquidation_actions": path, "branch_events": branch_events,
                        "payment_event": payments[0], "final_snapshot": final,
                        "next_decision_type": decision["decision_type"] if decision else None,
                        "canonical_sources": [{"path": str((run / name).relative_to(ROOT)),
                                               "sha256": hashlib.sha256((run / name).read_bytes()).hexdigest()}
                                              for name in ("events.jsonl", "actions.jsonl", "run_config.json")]})
    report = {"version": "astra_liquidation_feasibility_v1", "cases": results,
              "scope": "Constructive legal debt-payment feasibility at recorded states. Not optimal liquidation, intent, later survival, or a repaired game outcome.",
              "selection": "All three positive arithmetic-bound screens in Fable's phase-1 surrender scan.",
              "engine_source_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest()}
    (HERE / "feasible_liquidation.json").write_text(json.dumps(report, indent=2) + "\n")
    for result in results:
        final_player = next(p for p in result["final_snapshot"]["players"] if p["player_id"] == result["actor"])
        print(json.dumps({"game": result["case"]["game"], "model": result["case"]["model"],
                          "actions": len(result["feasible_liquidation_actions"]), "cash_after_paying": final_player["cash"],
                          "bankrupt": final_player["bankrupt"]}))


if __name__ == "__main__":
    main()
