"""Recheck every defaulted construction request at its exact recorded state.

An exhaustive finite ordering search splits counts into one-piece operations,
preserves the requested purchases per deed, and validates every prefix through
the engine. A successful branch stops immediately after that single build.
No original run, prompt, policy or winner is changed.
"""

import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.engine import HOUSE_COST_BY_GROUP
from monopoly_engine.replay import canonical_event_lines

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
FOUNDATION = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def action_for(decision, plan):
    return {"schema_version": "v1", "decision_id": decision["decision_id"],
            "action": "build_houses_or_hotel", "args": {"build_plan": plan}}


def legal_order(engine, decision, plan):
    spaces = {re.sub(r"[^A-Za-z0-9]+", "_", s.name).strip("_").upper(): s
              for s in engine.state.board}
    queues = defaultdict(list)
    try:
        for item in plan:
            key, kind, count = item["space_key"], item["kind"], item["count"]
            if key not in spaces or kind not in {"HOUSE", "HOTEL"} or not isinstance(count, int) or count < 1:
                return {"status": "malformed_plan", "legal_plan": None}
            queues[key].extend([kind] * count)
    except (KeyError, TypeError):
        return {"status": "malformed_plan", "legal_plan": None}
    cost = sum(HOUSE_COST_BY_GROUP.get(spaces[k].group, 0) * len(v) for k, v in queues.items())
    player = next(p for p in engine.state.players if p.player_id == decision["player_id"])
    base = {"requested_cost": cost, "cash": player.cash,
            "cash_margin": player.cash - cost, "groups": sorted({spaces[k].group for k in queues})}
    if cost > player.cash:
        return {**base, "status": "unaffordable_same_allocation", "legal_plan": None}
    keys = sorted(queues)
    end = tuple(len(queues[k]) for k in keys)
    visited = set()
    rejection_counts = Counter()

    def search(position, prefix):
        if position == end:
            return prefix
        if position in visited:
            return None
        visited.add(position)
        for i, key in enumerate(keys):
            if position[i] == end[i]:
                continue
            item = {"space_key": key, "kind": queues[key][position[i]], "count": 1}
            proposed = prefix + [item]
            errors = engine.validate_action_for_decision(action_for(decision, proposed), decision)
            if errors:
                rejection_counts.update(errors)
                continue
            nxt = list(position)
            nxt[i] += 1
            result = search(tuple(nxt), proposed)
            if result is not None:
                return result
        return None

    ordered = search(tuple(0 for _ in keys), [])
    if ordered is None:
        return {**base, "status": "no_legal_order_for_same_allocation", "legal_plan": None,
                "visited_states": len(visited), "prefix_rejections": dict(rejection_counts)}
    requested_units = Counter((k, kind) for k, kinds in queues.items() for kind in kinds)
    assert requested_units == Counter((x["space_key"], x["kind"]) for x in ordered)
    alternate = action_for(decision, ordered)
    assert engine.validate_action_for_decision(alternate, decision) == []
    branch = copy.deepcopy(engine)
    before = branch.get_snapshot()
    _, events, _, _ = branch.apply_action(alternate)
    after = branch.get_snapshot()
    actor = decision["player_id"]
    before_cash = next(p["cash"] for p in before["players"] if p["player_id"] == actor)
    after_cash = next(p["cash"] for p in after["players"] if p["player_id"] == actor)
    assert before_cash - after_cash == cost
    final_spaces = {s["index"]: s for s in after["board"]}
    for key, kinds in queues.items():
        source = spaces[key]
        level = 5 if source.hotel else source.houses
        expected_level = level + len(kinds)
        actual = final_spaces[source.index]
        assert (5 if actual["hotel"] else actual["houses"]) == expected_level
    return {**base, "status": "same_allocation_constructed_legally", "legal_plan": ordered,
            "visited_states": len(visited), "prefix_rejections": dict(rejection_counts),
            "cash_after_build": after_cash, "branch_events": events}


def main():
    units = rows(FOUNDATION / "review_unit_ledger.jsonl")
    selected = defaultdict(dict)
    packet_cache = {}
    response_counts = Counter()
    for unit in units:
        path = ROOT / unit["packet"]
        if path not in packet_cache:
            packet_cache = {path: rows(path)}
        packet = packet_cache[path][unit["packet_line"] - 1]
        if not packet["resolution"].get("fallback_used"):
            continue
        selected[unit["game"]][unit["decision_id"]] = (unit, packet)
        response_counts[packet["model"]] += 1
    assert sum(response_counts.values()) == 66
    results, sources = [], {}
    for game, targets in sorted(selected.items()):
        packet = next(iter(targets.values()))[1]
        run = ROOT / packet["source_run"]
        config = json.loads((run / "run_config.json").read_text())
        actions, recorded = rows(run / "actions.jsonl"), rows(run / "events.jsonl")
        engine = Engine(**{k: config[k] for k in ["seed", "players", "run_id", "max_turns",
                                                "max_trade_exchanges", "max_auction_actions"]})
        prefix = []
        for record in actions:
            _, emitted, decision, _ = engine.advance_until_decision(max_steps=100_000)
            prefix.extend(emitted)
            assert decision["decision_id"] == record["decision_id"]
            if record["decision_id"] in targets:
                unit, packet = targets[record["decision_id"]]
                assert canonical_event_lines(prefix) == canonical_event_lines(recorded[:len(prefix)])
                assert decision["decision_type"] == "POST_TURN_ACTION_DECISION"
                assert "build_houses_or_hotel" in {a["action"] for a in decision["legal_actions"]}
                assert record["action"]["action"] == "end_turn"
                assert record["action"].get("private_thought") == "fallback"
                attempts = []
                for attempt in packet["attempts"]:
                    item = {k: attempt.get(k) for k in ["attempt_index_zero_based", "outcome",
                                                       "response_condition", "validation_errors"]}
                    call = attempt.get("parsed_tool_call")
                    if call:
                        item["call_name"] = call["name"]
                        arguments = json.loads(call["arguments"]) if isinstance(call["arguments"], str) else call["arguments"]
                        item["arguments"] = arguments
                        if call["name"] == "build_houses_or_hotel":
                            plan = arguments.get("build_plan")
                            item["construction_check"] = legal_order(engine, decision, plan)
                    attempts.append(item)
                assert any(a.get("call_name") == "build_houses_or_hotel" for a in attempts)
                results.append({"game": game, "decision_id": unit["decision_id"],
                                "turn_index": packet["turn_index"], "model": packet["model"],
                                "source_unit": unit, "prefix_equal": True,
                                "recorded_action": record["action"], "attempts": attempts})
            _, emitted, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
            prefix.extend(emitted)
        for name in ["run_config.json", "actions.jsonl", "events.jsonl", "decisions.jsonl"]:
            path = run / name
            sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    summaries = []
    for model in sorted(response_counts):
        group = [r for r in results if r["model"] == model]
        status = Counter(a["construction_check"]["status"] for r in group for a in r["attempts"]
                         if "construction_check" in a)
        summaries.append({"model": model, "default_decisions": len(group), "plan_checks": dict(status)})
    report = {"version": 1, "selection": "All 66 fallback decisions, selected from original resolution fields",
              "scope": "Immediate construction feasibility at recorded states, preserving exact requested purchases; no changed rollout or winner",
              "sources_sha256": sources,
              "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "summary": summaries, "cases": results}
    (HERE / "default_build_plans.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
