"""Verify three disputed liquidation ceilings using exact recorded prefixes.

Only in-memory branches are created. These are debt-feasibility checks, not
counterfactual winner estimates. There are no hotels in the checked estates.
"""

import hashlib
import json
import re
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.engine import HOUSE_COST_BY_GROUP
from monopoly_engine.replay import canonical_event_lines

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
UNITS = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def check(game, suffix, expected):
    unit = next(r for r in rows(UNITS) if r["game"] == game
                and r["decision_id"].endswith(f"{suffix:06d}"))
    packet = rows(ROOT / unit["packet"])[unit["packet_line"] - 1]
    run = ROOT / packet["source_run"]
    config = json.loads((run / "run_config.json").read_text())
    actions, recorded = rows(run / "actions.jsonl"), rows(run / "events.jsonl")
    engine = Engine(**{key: config[key] for key in [
        "seed", "players", "run_id", "max_turns", "max_trade_exchanges", "max_auction_actions"]})
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
    initial = engine.get_snapshot()
    player = next(p for p in initial["players"] if p["player_id"] == actor)
    spaces = [s for s in engine.state.board if s.owner_id == actor]
    assert not any(s.hotel for s in spaces), "This constructive bound is limited to house-only estates"
    components = {
        "cash": player["cash"],
        "house_salvage": sum(s.houses * HOUSE_COST_BY_GROUP.get(s.group, 0) // 2 for s in spaces),
        "all_unmortgaged_deed_capacity": sum(s.price // 2 for s in spaces if not s.mortgaged),
    }
    ceiling = sum(components.values())
    assert ceiling == expected
    owed = decision["liquidation"]["owed_amount"]
    assert ceiling < owed
    keys = {s.index: re.sub(r"[^A-Za-z0-9]+", "_", s.name).strip("_").upper()
            for s in engine.state.board}
    branch, steps = [], []
    while decision and decision["decision_type"] == "LIQUIDATION_DECISION" and decision["player_id"] == actor:
        options = decision["liquidation"]["options"]
        if options["mortgageable_space_indices"]:
            index = min(options["mortgageable_space_indices"])
            name, args = "mortgage_property", {"space_key": keys[index]}
        elif options["sellable_building_space_indices"]:
            index = min(options["sellable_building_space_indices"])
            name, args = "sell_houses_or_hotel", {
                "sell_plan": [{"space_key": keys[index], "kind": "HOUSE", "count": 1}]}
        else:
            # Some recorded decisions already have no financing options. Their
            # only legal action is the explicit declaration, not another raise.
            name, args = "declare_bankruptcy", {}
        action = {"schema_version": "v1", "decision_id": decision["decision_id"],
                  "action": name, "args": args}
        before = next(p for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events)
        after = next(p for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
        steps.append({"action": action, "offered_options": options,
                      "cash_before": before["cash"], "cash_after": after["cash"],
                      "bankrupt_after": after["bankrupt"]})
        branch.extend(events)
        assert len(steps) < 50
        if after["bankrupt"]:
            break
    final = next(p for p in engine.get_snapshot()["players"] if p["player_id"] == actor)
    assert final["bankrupt"]
    cash_changes = [e["payload"] for e in branch if e["type"] == "CASH_CHANGED"
                    and e["payload"]["player_id"] == actor]
    cash = max_cash = components["cash"]
    for change in cash_changes:
        cash += change["delta"]
        max_cash = max(max_cash, cash)
    assert max_cash == ceiling, (max_cash, ceiling)
    assert not any(e["type"] == "RENT_PAID" and e["payload"].get("from_player_id") == actor for e in branch)
    return {
        "game": game, "decision_id": unit["decision_id"], "unit": unit,
        "prefix_events": len(prefix), "canonical_prefix_equal": True,
        "initial_snapshot": initial, "components": components,
        "ceiling_reached_legally": ceiling, "owed": owed, "shortfall_after_maximum": owed - ceiling,
        "steps": steps, "branch_events": branch,
        "bankruptcy_after_exhaustion": True,
        "source_sha256": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                          for n in ["run_config.json", "events.jsonl", "actions.jsonl"]},
    }


def main():
    results = [check(*case) for case in [(19, 322, 512), (20, 354, 340), (20, 310, 550)]]
    report = {
        "version": 1, "scope": "Exact legal liquidation ceilings for three house-only estates; no winner counterfactual",
        "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "cases": results,
    }
    (HERE / "final_liquidations.json").write_text(json.dumps(report, indent=2) + "\n")
    for r in results:
        print(json.dumps({k: r[k] for k in ["game", "decision_id", "components", "ceiling_reached_legally", "owed", "shortfall_after_maximum"]}))


if __name__ == "__main__":
    main()
