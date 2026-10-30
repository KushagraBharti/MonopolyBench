"""H1: are 'skipped legal build' post-turn decisions model choices or engine defaults?

For every POST_TURN_ACTION_DECISION with a non-empty buildable list, classify the applied action and
whether it came from the deterministic fallback, and whether any attempt proposed a build.
Output: per-model counts and per-game list of fallback decisions. Read-only.
"""
import json, sys, collections
from common import game_dirs, decisions, action_state, ALIAS

rows = []
for g, run in game_dirs().items():
    st, rs = decisions(run)
    for did, s in st.items():
        if s["decision_type"] != "POST_TURN_ACTION_DECISION":
            continue
        a, _ = action_state(s)
        bk = a["scenario"]["options"].get("buildable_space_keys") or []
        r = rs[did]
        att = r.get("attempts") or []
        tried_build = any(((x.get("parsed_tool_call") or {}).get("name")) == "build_houses_or_hotel" for x in att)
        chain = [f'{x.get("response_condition")}:{x.get("outcome")}' for x in att]
        rows.append(dict(game=g, decision_id=did, model=ALIAS[s["openrouter_model_id"]], buildable=bool(bk),
                         final=(r.get("final_action") or {}).get("action"), fallback=bool(r.get("fallback_used")),
                         fallback_reason=r.get("fallback_reason"), tried_build=tried_build, chain=chain,
                         val_err=[e for x in att for e in (x.get("validation_errors") or [])][:3]))

out = collections.defaultdict(collections.Counter)
for r in rows:
    if not r["buildable"]:
        continue
    k = r["model"]
    out[k]["buildable_postturn"] += 1
    out[k][f"final={r['final']}"] += 1
    if r["final"] == "end_turn":
        out[k]["end_turn_fallback" if r["fallback"] else "end_turn_model"] += 1
        if r["fallback"] and r["tried_build"]:
            out[k]["end_turn_fallback_after_build_attempt"] += 1
for k, c in sorted(out.items()):
    print(k, dict(sorted(c.items())))
print()
fb = [r for r in rows if r["fallback"]]
print("all fallback post-turn decisions:", len(fb))
by = collections.Counter((r["game"], r["model"], r["buildable"], r["tried_build"]) for r in fb)
for k, v in sorted(by.items()):
    print(k, v)
json.dump(rows, open(sys.argv[1], "w")) if len(sys.argv) > 1 else None
