"""For every fallback decision: the rejected build plan's total houses/hotels and cost vs. cash at the decision,
bank house/hotel stock, and whether the same multiset of builds in round-robin order respects even-building
and the 4-house/hotel cap given current development. Also report the cheapest legal single build (one house
on a buildable deed) as a lower bound on feasible development. Read-only; uses the observation in the prompt."""
import json, re, collections
from common import game_dirs, decisions, action_state, ALIAS, ROOT
board = json.load(open(f"{ROOT}/contracts/data/board.json"))
HC = board["house_cost_by_group"]
key = lambda n: re.sub(r"[^A-Z0-9]+", "_", n.upper()).strip("_")
G = {key(s["name"]): s["group"] for s in board["spaces"] if s.get("kind") == "PROPERTY"}
members = collections.defaultdict(list)
for k, g in G.items(): members[g].append(k)
out = []
for g, run in game_dirs().items():
    st, rs = decisions(run)
    for d, r in rs.items():
        if not r.get("fallback_used"):
            continue
        s = st[d]; a, gs = action_state(s)
        cash = gs["you"]["cash"]
        bank = gs.get("bank") or {}
        dev = {h["space_key"]: (5 if h.get("hotel") else h.get("houses", 0)) for h in gs["you"]["holdings"]["owned"]}
        plan = None
        for at in r["attempts"]:
            tc = at.get("parsed_tool_call") or {}
            if tc.get("name") == "build_houses_or_hotel":
                try:
                    plan = json.loads(tc["arguments"]).get("build_plan") if isinstance(tc["arguments"], str) else tc["arguments"].get("build_plan")
                except Exception:
                    plan = None
        if not plan:
            out.append(dict(game=g, dec=d[-6:], model=ALIAS[s["openrouter_model_id"]], plan=None)); continue
        tgt = dict(dev); cost = 0; nh = 0
        for p in plan:
            sk = p.get("space_key"); c = int(p.get("count", 1))
            if sk not in G: continue
            tgt[sk] = tgt.get(sk, 0) + c; cost += HC[G[sk]] * c; nh += c
        groups = {G[p["space_key"]] for p in plan if p.get("space_key") in G}
        even_ok = all(max(tgt.get(k, 0) for k in members[gr]) - min(tgt.get(k, 0) for k in members[gr]) <= 1 for gr in groups)
        cap_ok = all(v <= 5 for v in tgt.values())
        bk = a["scenario"]["options"].get("buildable_space_keys") or []
        cheapest = min((HC[G[k]] for k in bk if k in G), default=None)
        out.append(dict(game=g, dec=d[-6:], model=ALIAS[s["openrouter_model_id"]], cash=cash, plan_houses=nh, plan_cost=cost,
                        affordable=cost <= cash, final_even=even_ok, cap_ok=cap_ok, bank=bank, cheapest_single=cheapest,
                        single_affordable=(cheapest is not None and cheapest <= cash)))
json.dump(out, open("../h1_plan_feasibility.json", "w"), indent=0)
c = collections.Counter((o["model"], o.get("affordable"), o.get("final_even"), o.get("single_affordable")) for o in out)
for k, v in sorted(c.items(), key=str): print(k, v)
for o in out:
    if o["model"] != "Opus" or not o.get("affordable") or not o.get("final_even"):
        print(o)
