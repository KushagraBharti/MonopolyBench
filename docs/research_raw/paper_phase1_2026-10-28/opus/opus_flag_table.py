"""Episode-level table: trade-completed groups x response flags. Version opus_phase1_v1.

For each trade-completed group episode, list management decisions (owner, episode
window, up to and including the first build turn) whose saved menu made the group
buildable, the applied action, and any content/tool action-name mismatch. Original
denominators are kept; no outcome is repaired or removed. Requires opus_corpus.py
and opus_responses.py outputs.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opus_reduce import HERE, game_dirs, load_board, load_jsonl  # noqa: E402


def main():
    board = load_board()
    mm = {json.loads(line)["decision_id"]: json.loads(line) for line in open(HERE / "opus_response_mismatches.jsonl")}
    eps = [json.loads(line) for line in open(HERE / "opus_group_episodes.jsonl")]
    runs = {g: run for g, run, _ in game_dirs()}
    cache = {}
    rows = []
    for ep in eps:
        if ep["completion_route"] != "trade":
            continue
        g = ep["game"]
        if g not in cache:
            rs = load_jsonl(runs[g] / "decisions.jsonl")
            cache[g] = ({r["decision_id"]: r for r in rs if r["phase"] == "decision_started"},
                        {r["decision_id"]: r for r in rs if r["phase"] == "decision_resolved"})
        started, resolved = cache[g]
        keys = {board["key"][i] for i in board["groups"][ep["group"]]}
        hi = ep["first_build_turn"] if ep["first_build_turn"] is not None else (
            ep["end_turn"] if ep["end_turn"] is not None else 10 ** 9)
        legal = []
        for did, s in started.items():
            if s["player_id"] != ep["player_id"] or s["decision_type"] != "POST_TURN_ACTION_DECISION":
                continue
            if not (ep["start_turn"] <= s["turn_index"] <= hi):
                continue
            opts = s["prompt_payload"]["action_state"]["scenario"]["options"]
            if keys & set(opts.get("buildable_space_keys") or []):
                legal.append((s["turn_index"], did))
        legal.sort()
        flagged = [(t, mm[d]["content_name"], mm[d]["tool_name"]) for t, d in legal if d in mm]
        rows.append({
            "game": g, "model": ep["model"], "group": ep["group"], "start_turn": ep["start_turn"],
            "first_mgmt_turn": ep.get("first_mgmt_turn"), "entry_buildable": ep.get("entry_buildable"),
            "built_in_first_mgmt_turn": ep.get("built_in_first_mgmt_turn"),
            "first_build_turn": ep.get("first_build_turn"),
            "legal_turns_skipped_before_first_build": ep.get("legal_turns_skipped_before_first_build"),
            "legal_build_decisions": len(legal),
            "applied_on_legal_build_decisions": ";".join(resolved[d]["final_action"]["action"] for _, d in legal),
            "flagged_legal_build_decisions": len(flagged),
            "flagged_on_first_mgmt_turn": sum(t == ep.get("first_mgmt_turn") for t, _, _ in flagged),
            "flag_pairs": ";".join(f"t{t}:{a}->{b}" for t, a, b in flagged),
            "end_reason": ep["end_reason"], "owner_won_game": ep["winner"],
        })
    rows.sort(key=lambda r: (r["model"], r["game"], r["start_turn"]))
    with open(HERE / "opus_trade_group_flags.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    by = {}
    for r in rows:
        b = by.setdefault(r["model"], {"groups": 0, "groups_with_flag": 0, "groups_flag_first_turn": 0,
                                       "built_first_turn": 0, "built_first_turn_among_unflagged_first_turn": 0,
                                       "unflagged_first_turn": 0})
        b["groups"] += 1
        b["groups_with_flag"] += r["flagged_legal_build_decisions"] > 0
        b["groups_flag_first_turn"] += r["flagged_on_first_mgmt_turn"] > 0
        b["built_first_turn"] += bool(r["built_in_first_mgmt_turn"])
        if not r["flagged_on_first_mgmt_turn"]:
            b["unflagged_first_turn"] += 1
            b["built_first_turn_among_unflagged_first_turn"] += bool(r["built_in_first_mgmt_turn"])
    print(json.dumps(by, indent=1))
    (HERE / "opus_trade_group_flags_summary.json").write_text(json.dumps(
        {"version": "opus_phase1_v1",
         "note": "Selected-subset description; not a sensitivity range or counterfactual.",
         "by_model": by}, indent=2) + "\n")


if __name__ == "__main__":
    main()
