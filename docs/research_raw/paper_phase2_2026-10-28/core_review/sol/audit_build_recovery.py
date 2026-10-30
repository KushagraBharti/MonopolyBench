"""Replay all actual games and test received failed build plans locally.

No game continuation changes. Semantic source reading is tracked separately.
"""

import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from monopoly_engine import Engine
from monopoly_engine.replay import canonical_event_lines

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def parse_plan(attempt):
    call = attempt.get("parsed_tool_call")
    if not call or call.get("name") != "build_houses_or_hotel":
        return None
    try:
        args = call["arguments"]
        args = json.loads(args) if isinstance(args, str) else args
        plan = args["build_plan"]
        assert plan and all(set(("space_key", "kind", "count")) <= set(row)
                            and isinstance(row["count"], int) and row["count"] > 0 for row in plan)
        return plan
    except (ValueError, TypeError, KeyError, AssertionError):
        return None


def allocation(plan):
    counts = Counter()
    for row in plan:
        counts[(row["space_key"], row["kind"])] += row["count"]
    return sorted([deed, kind, count] for (deed, kind), count in counts.items())


def test_interleaved(engine, decision, plan):
    levels = {}
    groups = {}
    for space in engine.state.board:
        key = re.sub(r"[^A-Z0-9]+", "_", space.name.upper()).strip("_")
        levels[key] = 5 if space.hotel else space.houses
        groups[key] = space.group
    queued_groups = {}
    for row in plan:
        deed = row["space_key"]
        if deed not in levels or row["kind"] not in {"HOUSE", "HOTEL"}:
            return {"tested": False, "reason": "unknown deed or operation"}
        group = queued_groups.setdefault(groups[deed], defaultdict(list))
        group[deed].extend([row["kind"]] * row["count"])
    ordered = []
    # Finish each original color group before the next, allowing a group's
    # hotel conversions to return physical houses before later groups build.
    for queue in queued_groups.values():
        while queue:
            deed = min(queue, key=lambda name: (levels[name], name))
            kind = queue[deed].pop(0)
            ordered.append({"space_key": deed, "kind": kind, "count": 1})
            levels[deed] = 5 if kind == "HOTEL" else levels[deed] + 1
            if not queue[deed]:
                del queue[deed]
    assert allocation(ordered) == allocation(plan)
    branch = copy.deepcopy(engine)
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": "build_houses_or_hotel", "args": {"build_plan": ordered}}
    before = next(p.cash for p in branch.state.players if p.player_id == decision["player_id"])
    try:
        _, events, _, _ = branch.apply_action(action)
    except ValueError as exc:
        return {"tested": True, "legal": False, "before_cash": before,
                "interleaved_plan": ordered, "validation_error": str(exc)}
    rejected = [e for e in events if e["type"] == "ACTION_REJECTED"]
    after = next(p.cash for p in branch.state.players if p.player_id == decision["player_id"])
    return {"tested": True, "legal": not rejected, "before_cash": before, "after_cash": after,
            "interleaved_plan": ordered, "events": events}


def main():
    defaults = []
    uneven_rows = []
    fallback_counts = Counter()
    uneven_counts = Counter()
    repaired = Counter()
    preserving = Counter()
    changed = Counter()
    replay = []
    for game in range(1, 21):
        source = units(game)
        run = ROOT / next(iter(source.values()))[0]["source_run"]
        config = json.loads((run / "run_config.json").read_text())
        engine = Engine(**{k: config[k] for k in
                           ("seed", "players", "run_id", "max_turns", "max_trade_exchanges", "max_auction_actions")})
        actions = [json.loads(line) for line in (run / "actions.jsonl").read_text().splitlines()]
        actual = []
        for recorded in actions:
            _, events, decision, _ = engine.advance_until_decision(max_steps=100000)
            actual.extend(events)
            assert decision["decision_id"] == recorded["decision_id"]
            suffix = int(decision["decision_id"][-6:])
            unit, ref = source[suffix]
            name = unit["model"]
            is_default = unit["resolution"].get("fallback_used", False)
            uneven_attempts = [a for a in unit["attempts"] if
                               "Uneven intermediate" in json.dumps(a.get("validation_errors", []))]
            if uneven_attempts:
                uneven_counts[name] += 1
                final = recorded["action"]
                outcome = {"game": game, "decision_id": decision["decision_id"], "source": ref,
                           "model": name, "applied_action": final["action"], "fallback_used": is_default}
                if final["action"] == "build_houses_or_hotel":
                    repaired[name] += 1
                    original = parse_plan(uneven_attempts[0])
                    same = original is not None and allocation(original) == allocation(final["args"]["build_plan"])
                    outcome["allocation_preserved_within_decision"] = same
                    (preserving if same else changed)[name] += 1
                uneven_rows.append(outcome)
            if is_default:
                fallback_counts[name] += 1
                trials = []
                for index, attempt in enumerate(unit["attempts"]):
                    plan = parse_plan(attempt)
                    if plan is not None:
                        trials.append({"attempt_index": index, "received_plan": plan,
                                       "test": test_interleaved(engine, decision, plan)})
                options = unit["initial_prompt"]["payload"]["action_state"]["scenario"]["options"]
                smaller = []
                for deed in options.get("buildable_space_keys", []):
                    result = test_interleaved(engine, decision, [{"space_key": deed, "kind": "HOUSE", "count": 1}])
                    if result.get("legal"):
                        smaller.append(deed)
                defaults.append({"game": game, "decision_id": decision["decision_id"], "source": ref,
                                 "model": name, "fallback_action": recorded["action"],
                                 "attempt_chain": [{"outcome": a["outcome"], "response_condition": a.get("response_condition"),
                                                    "errors": a.get("validation_errors")} for a in unit["attempts"]],
                                 "plan_tests": trials, "legal_single_house_deeds": smaller})
            _, events, _, _ = engine.apply_action(recorded["action"], decision_meta=recorded.get("decision_meta"))
            actual.extend(events)
        canonical = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
        assert canonical_event_lines(actual) == canonical_event_lines(canonical), game
        replay.append({"game": game, "events_equal": True, "event_count": len(actual),
                       "actions": len(actions), "event_sha256": hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()})
    opus = [r for r in defaults if r["model"] == "anthropic/claude-opus-5.5"]
    assert len(defaults) == 66 and all(r["fallback_action"]["action"] == "end_turn"
                                      and r["legal_single_house_deeds"] for r in defaults)
    pending = [r for r in opus if len(r["plan_tests"]) != 1 or not r["plan_tests"][0]["test"].get("legal")]
    if pending:
        print(json.dumps({"pending_plan_tests": pending}))
    assert len(opus) == 61 and not pending
    sol = [r for r in defaults if r["model"] == "openai/gpt-6.1-sol"]
    sol_tests = [p for r in sol for p in r["plan_tests"]]
    assert len(sol) == 4 and len(sol_tests) == 8 and sum(t["test"].get("legal", False) for t in sol_tests) == 1
    assert all(r["legal_single_house_deeds"] for r in sol)
    summary = {"fallbacks": dict(fallback_counts), "uneven_rejection_decisions": dict(uneven_counts),
               "resolved_to_applied_build": dict(repaired),
               "allocation_preserving_within_decision": dict(preserving),
               "allocation_changing_within_decision": dict(changed),
               "opus_all61_same_allocation_legal_after_interleaving": True,
               "sol_failed_plan_tests": len(sol_tests), "sol_legal_interleaved_attempts": 1,
               "all20_actual_event_streams_replayed": True}
    report = {"summary": summary, "defaults": defaults, "uneven_rows": uneven_rows,
              "canonical_replays": replay,
              "provenance": "Peer numerical targets known. Implementation independently replays all actual engine events and applies local copies for plan diagnostics. No model calls or changed trajectories saved.",
              "limits": "All attempt fields are mechanically screened; this is not a claim of complete semantic reading of all8679attempts. Received plans do not identify latent intended action. Resolving to some applied build, preserving a within-decision allocation and eventually attaining the same-turn target differ. Valid chosen ENDs remain separate, and repair rates describe this response policy and selected errors rather than intrinsic provider capabilities.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "build_recovery_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
