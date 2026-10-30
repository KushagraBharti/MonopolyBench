"""Tie phase-1 'legal turns skipped before first build' to fallback status, per episode. Read-only.
Uses phase-1 opus_group_episodes.jsonl (my reducer) and canonical decisions."""
import json, os, collections
from common import game_dirs, decisions, action_state, ALIAS, ROOT
EP = os.path.join(ROOT, "docs/research_raw/paper_phase1_2026-10-28/opus/opus_group_episodes.jsonl")
board = json.load(open(os.path.join(ROOT, "contracts/data/board.json")))
spaces = board["spaces"] if isinstance(board, dict) and "spaces" in board else board
grp = collections.defaultdict(set)
import re
for s in spaces:
    if s.get("kind") == "PROPERTY" and s.get("group"):
        grp[s["group"].upper()].add(re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"))
eps = [json.loads(l) for l in open(EP)]
dirs = game_dirs(); cache = {}
tot = collections.Counter(); detail = []
for e in eps:
    if not e.get("legal_turns_skipped_before_first_build"):
        continue
    g = e["game"]
    if g not in cache:
        cache[g] = decisions(dirs[g])
    st, rs = cache[g]
    keys = grp[e["group"]]
    end = e["first_build_turn"] if e["first_build_turn"] is not None else (e["end_turn"] if e["end_turn"] is not None else 10**9)
    turns = collections.defaultdict(list)
    for did, s in st.items():
        if s["player_id"] != e["player_id"] or s["decision_type"] != "POST_TURN_ACTION_DECISION":
            continue
        t = s["turn_index"]
        if t < e["start_turn"] or t >= end:
            continue
        a, _ = action_state(s)
        bk = set(a["scenario"]["options"].get("buildable_space_keys") or [])
        if bk & keys:
            r = rs[did]
            turns[t].append(bool(r.get("fallback_used")))
    fbt = sum(1 for t, v in turns.items() if any(v))
    rec = dict(game=g, model=e["model"], group=e["group"], route=e["completion_route"], skipped=e["legal_turns_skipped_before_first_build"],
               legal_turns_found=len(turns), turns_with_fallback=fbt, winner=e["winner"])
    detail.append(rec)
    tot[(e["model"], "skipped")] += e["legal_turns_skipped_before_first_build"]
    tot[(e["model"], "fallback_turns")] += fbt
for d in detail: print(d)
print(dict(tot))
