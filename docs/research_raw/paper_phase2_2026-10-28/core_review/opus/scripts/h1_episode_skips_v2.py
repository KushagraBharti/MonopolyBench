"""v2 of h1_episode_skips (Astra's qualification): per skipped group-turn, record whether a fallback occurred on
that turn AND whether the failed build plan included a deed of the focal group; also report distinct own turns.
Read-only."""
import json, os, re, collections
from common import game_dirs, decisions, action_state, ROOT
EP = os.path.join(ROOT, "docs/research_raw/paper_phase1_2026-10-28/opus/opus_group_episodes.jsonl")
board = json.load(open(f"{ROOT}/contracts/data/board.json"))
key = lambda n: re.sub(r"[^A-Z0-9]+", "_", n.upper()).strip("_")
grp = collections.defaultdict(set)
for s in board["spaces"]:
    if s.get("kind") == "PROPERTY": grp[s["group"]].add(key(s["name"]))
def plan_keys(r):
    ks = set()
    for at in r.get("attempts") or []:
        tc = at.get("parsed_tool_call") or {}
        if tc.get("name") == "build_houses_or_hotel":
            a = tc["arguments"]; a = json.loads(a) if isinstance(a, str) else a
            ks |= {p.get("space_key") for p in a.get("build_plan", [])}
    return ks
dirs = game_dirs(); cache = {}
gt = collections.Counter(); turns_by_model = collections.defaultdict(set); rows = []
for e in map(json.loads, open(EP)):
    if not e.get("legal_turns_skipped_before_first_build"): continue
    g = e["game"]; cache.setdefault(g, decisions(dirs[g])); st, rs = cache[g]
    end = e["first_build_turn"] if e["first_build_turn"] is not None else (e["end_turn"] if e["end_turn"] is not None else 10**9)
    T = collections.defaultdict(lambda: [False, False])
    for d, s in st.items():
        if s["player_id"] != e["player_id"] or s["decision_type"] != "POST_TURN_ACTION_DECISION": continue
        t = s["turn_index"]
        if not (e["start_turn"] <= t < end): continue
        a, _ = action_state(s)
        if not (set(a["scenario"]["options"].get("buildable_space_keys") or []) & grp[e["group"]]): continue
        T[t]
        r = rs[d]
        if r.get("fallback_used"):
            T[t][0] = True
            if plan_keys(r) & grp[e["group"]]: T[t][1] = True
    m = e["model"]
    for t, (fb, focal) in T.items():
        gt[(m, "group_turns")] += 1; gt[(m, "group_turns_fallback")] += fb; gt[(m, "group_turns_fallback_focal")] += focal
        turns_by_model[(m, "all")].add((g, e["player_id"], t))
        if fb: turns_by_model[(m, "fb")].add((g, e["player_id"], t))
        if focal: turns_by_model[(m, "fb_focal")].add((g, e["player_id"], t))
    rows.append(dict(game=g, model=m, group=e["group"], route=e["completion_route"], group_turns=len(T),
                     fb=sum(v[0] for v in T.values()), fb_focal=sum(v[1] for v in T.values())))
for r in rows:
    if r["fb"]: print(r)
print({f"{a}:{b}": v for (a, b), v in sorted(gt.items())})
print({f"{a}:{b}": len(v) for (a, b), v in sorted(turns_by_model.items())})
