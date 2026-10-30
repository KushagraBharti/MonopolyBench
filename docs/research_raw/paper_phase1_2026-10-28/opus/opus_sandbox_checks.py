"""Opus phase-1 sandbox checks, version opus_phase1_v1. No provider calls.

1. Model-facing memory reconstruction: feed canonical events into the arena's
   PromptMemory and compare to the memory in every recorded decision_started prompt.
2. Exact reset and branch: for one recorded decision per game, replay the recorded
   action prefix into a fresh Engine; check prefix events, pending decision id and
   rebuilt memory; replay the recorded action to confirm the next recorded events
   (hidden RNG/deck state preserved); then, on a second fresh engine, apply a
   DIFFERENT legal action and roll the game out to termination with a deterministic
   reference policy ("builder"). The rollout is a counterfactual continuation of the
   game engine, not of the LLM agents; it demonstrates environment support only.

Run with the repository venv from repo root:
  PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase1_2026-10-28/opus/opus_sandbox_checks.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opus_reduce import HERE, game_dirs, load_jsonl  # noqa: E402

from monopoly_arena.baselines import choose_baseline_action  # noqa: E402
from monopoly_arena.prompting import PromptMemory  # noqa: E402
from monopoly_engine import Engine  # noqa: E402
from monopoly_engine.replay import canonical_event_lines  # noqa: E402

MAX_ROLLOUT_DECISIONS = 20_000


def engine_for(cfg):
    return Engine(seed=cfg["seed"], players=cfg["players"], run_id=cfg["run_id"], max_turns=cfg["max_turns"],
                  max_trade_exchanges=cfg["max_trade_exchanges"], max_auction_actions=cfg["max_auction_actions"])


def replay_prefix(cfg, actions, k):
    eng = engine_for(cfg)
    out = []
    for a in actions[:k]:
        _, ev, d, _ = eng.advance_until_decision(max_steps=10_000)
        out += ev
        if d is None or d["decision_id"] != a["decision_id"]:
            raise AssertionError("prefix decision mismatch")
        _, ev, _, _ = eng.apply_action(a["action"], decision_meta=a.get("decision_meta"))
        out += ev
    _, ev, d, _ = eng.advance_until_decision(max_steps=10_000)
    return eng, out + ev, d


def alternative(d, recorded_name):
    for a in d["legal_actions"]:
        if a["action"] != recorded_name and a["action"] in ("end_turn", "start_auction", "buy_property",
                                                            "reject_trade", "drop_out", "roll_for_doubles",
                                                            "pay_jail_fine"):
            return {"schema_version": "v1", "decision_id": d["decision_id"], "action": a["action"], "args": {}}
    return None


def main():
    memory_rows, branch_rows = [], []
    for gno, run, _ in game_dirs():
        cfg = json.loads((run / "run_config.json").read_text())
        events = load_jsonl(run / "events.jsonl")
        actions = load_jsonl(run / "actions.jsonl")
        started = {r["decision_id"]: r for r in load_jsonl(run / "decisions.jsonl") if r["phase"] == "decision_started"}
        mem, ok, total = PromptMemory(), 0, 0
        for e in events:
            mem.update(e)
            if e["type"] == "LLM_DECISION_REQUESTED":
                total += 1
                ok += mem.snapshot_for_player(e["payload"]["player_id"]) == \
                    started[e["payload"]["decision_id"]]["prompt_payload"]["game_state"]["memory"]
        memory_rows.append({"game": gno, "decisions": total, "memory_equal": ok})
        # branch at the middle recorded decision that has a simple alternative
        k = len(actions) // 2
        while True:
            eng, pre, d = replay_prefix(cfg, actions, k)
            alt = alternative(d, actions[k]["action"]["action"])
            if alt is not None:
                break
            k += 1
        n = len(pre)
        row = {"game": gno, "k": k, "decision_id": d["decision_id"], "decision_type": d["decision_type"],
               "recorded_action": actions[k]["action"]["action"], "branch_action": alt["action"],
               "prefix_events": n,
               "prefix_identical": canonical_event_lines(pre) == canonical_event_lines(events[:n])}
        m = PromptMemory()
        for e in pre:
            m.update(e)
        row["memory_equal_at_k"] = m.snapshot_for_player(d["player_id"]) == \
            started[d["decision_id"]]["prompt_payload"]["game_state"]["memory"]
        _, same, _, _ = eng.apply_action(actions[k]["action"], decision_meta=actions[k].get("decision_meta"))
        _, more, _, _ = eng.advance_until_decision(max_steps=10_000)
        tail = same + more
        row["recorded_suffix_reproduced"] = canonical_event_lines(tail) == canonical_event_lines(events[n:n + len(tail)])
        eng2, _, d2 = replay_prefix(cfg, actions, k)
        _, ev, nd, _ = eng2.apply_action(alt)
        branch = list(ev)
        steps = 0
        while not eng2.is_game_over() and steps < MAX_ROLLOUT_DECISIONS:
            if nd is None:
                _, ev, nd, _ = eng2.advance_until_decision(max_steps=10_000)
                branch += ev
                continue
            a = choose_baseline_action(nd, "builder")
            _, ev, nd, _ = eng2.apply_action(a)
            branch += ev
            steps += 1
        row["branch_diverges"] = canonical_event_lines(branch[:len(tail)]) != canonical_event_lines(tail)
        row["rollout_decisions"] = steps
        row["rollout_terminal"] = eng2.is_game_over()
        row["rollout_end_reason"] = next((e["payload"].get("reason") for e in branch if e["type"] == "GAME_ENDED"), None)
        branch_rows.append(row)
        print(gno, row)
    out = {"version": "opus_phase1_v1",
           "memory_reconstruction": {"games": len(memory_rows),
                                     "decisions": sum(r["decisions"] for r in memory_rows),
                                     "memory_equal": sum(r["memory_equal"] for r in memory_rows),
                                     "per_game": memory_rows},
           "branch_checks": branch_rows,
           "branch_summary": {k: sum(bool(r[k]) for r in branch_rows) for k in
                              ("prefix_identical", "memory_equal_at_k", "recorded_suffix_reproduced",
                               "branch_diverges", "rollout_terminal")}}
    (HERE / "opus_sandbox_checks.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out["memory_reconstruction"]["memory_equal"]), json.dumps(out["branch_summary"]))


if __name__ == "__main__":
    main()
