"""Per game x model: post-turn decisions with propose_trade legal, applied proposals, accepted trades by
original thread initiator. Read-only. Output JSON to argv[1]."""
import json, sys, collections
from common import game_dirs, decisions, action_state, ALIAS
out = {}
for g, run in game_dirs().items():
    st, rs = decisions(run)
    el = collections.Counter(); pr = collections.Counter(); acc = collections.Counter(); seat = {}
    for d, s in sorted(st.items()):
        m = ALIAS[s["openrouter_model_id"]]; seat[s["player_id"]] = m
        a, _ = action_state(s)
        fa = (rs[d]["final_action"] or {}).get("action")
        if s["decision_type"] == "POST_TURN_ACTION_DECISION" and "propose_trade" in a["available_actions"]:
            el[m] += 1; pr[m] += fa == "propose_trade"
        if fa == "accept_trade":
            acc[m] += 1
    out[g] = {m: dict(eligible=el[m], proposals=pr[m], accepts_as_responder=acc[m]) for m in sorted(set(seat.values()))}
json.dump(out, open(sys.argv[1], "w"), indent=1)
tot = collections.defaultdict(collections.Counter)
for g, d in out.items():
    print(g, {m: f'{v["proposals"]}/{v["eligible"]} acc{v["accepts_as_responder"]}' for m, v in d.items()})
    for m, v in d.items():
        for k, x in v.items(): tot[m][k] += x
print("TOTAL", {m: dict(v) for m, v in tot.items()})
