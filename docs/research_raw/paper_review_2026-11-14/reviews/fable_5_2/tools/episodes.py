"""Rebuild the 188 financing episodes from raw decisions.jsonl (read-only, no engine).

Adds, for each episode: hotels held at entry, bank house stock, first-action text channels,
argument order of the first tool call, and whether any mortgage used was absent from the first menu.
Writes data/episodes_188.json.
"""
import json, collections
from lib import *

def first_fields(r):
    a = r["attempts"][-1]
    tcs = a.get("parsed_tool_calls") or []
    order = None
    if tcs:
        try:
            order = list(json.loads(tcs[0]["arguments"]).keys())
        except Exception:
            order = None
    fa = r.get("final_action") or {}
    return dict(action=fa.get("action"), args=fa.get("args"), note=fa.get("private_thought"),
                public=fa.get("public_message"), content=a.get("assistant_content"),
                provider=reasoning(r), arg_order=order, condition=a.get("response_condition"),
                attempts=len(r["attempts"]), fallback=bool(r.get("fallback_used")),
                reasoning_tokens=((a.get("raw_response") or {}).get("usage") or {}).get("completion_tokens_details", {}).get("reasoning_tokens"))

def episodes():
    out = []
    for g in range(1, 21):
        st, rs = load(g)
        cur = None
        eps = []
        for i in sorted(rs):
            r = rs[i]
            if r["decision_type"] != "LIQUIDATION_DECISION":
                continue
            sc = st[i]["prompt_payload"]["action_state"]["scenario"]
            sig = (r["player_id"], r["turn_index"], sc["owed_amount"], sc.get("owed_to_player_id"), sc.get("reason"))
            if cur is None or cur["sig"] != sig or cur["closed"]:
                cur = {"sig": sig, "game": g, "ds": [], "closed": False}
                eps.append(cur)
            cur["ds"].append(i)
            if (r.get("final_action") or {}).get("action") == "declare_bankruptcy":
                cur["closed"] = True
        for e in eps:
            i = e["ds"][0]
            pp = st[i]["prompt_payload"]
            sc = pp["action_state"]["scenario"]
            you = pp["game_state"]["you"]
            salvage = mstar = hotels = houses = 0
            for h in you["holdings"]["owned"]:
                sp = SPACES[h["space_key"]]
                n = h.get("houses", 0) + (5 if h.get("hotel") else 0)
                hotels += 1 if h.get("hotel") else 0
                houses += h.get("houses", 0)
                if n:
                    salvage += n * HOUSE_COST[sp["group"]] // 2
                if not h.get("mortgaged"):
                    mstar += sp["price"] // 2
            listed = sc["options"].get("mortgageable_space_keys", [])
            sell_listed = sc["options"].get("sellable_building_space_keys", [])
            m0 = sum(SPACES[k]["price"] // 2 for k in listed)
            acts = [(rs[j].get("final_action") or {}).get("action") for j in e["ds"]]
            used_new = [rs[j]["final_action"]["args"]["space_key"] for j in e["ds"]
                        if rs[j]["final_action"]["action"] == "mortgage_property"
                        and rs[j]["final_action"]["args"]["space_key"] not in listed]
            last = rs[e["ds"][-1]]
            ev_types = last.get("emitted_event_types") or []
            e.update(first=i, last=e["ds"][-1], model=who(rs[i]), turn=rs[i]["turn_index"], debt=sc["owed_amount"],
                     creditor=sc.get("owed_to_player_id"), reason=sc.get("reason"), cash=you["cash"],
                     salvage=salvage, m0=m0, mstar=mstar, u0=you["cash"] + salvage + m0, ustar=you["cash"] + salvage + mstar,
                     hotels=hotels, houses=houses, bank_houses=pp["game_state"]["bank"]["houses_remaining"],
                     listed_mortgages=listed, listed_sales=sell_listed,
                     menu=[a if isinstance(a, str) else a.get("action") for a in pp["action_state"]["available_actions"]],
                     actions=acts, fallbacks=[bool(rs[j].get("fallback_used")) for j in e["ds"]],
                     released_mortgages_used=used_new,
                     declared=acts[-1] == "declare_bankruptcy",
                     last_event_types=ev_types,
                     first_fields=first_fields(rs[i]))
            e["sig"] = list(e["sig"])
            del e["closed"]
            out.append(e)
    return out

if __name__ == "__main__":
    eps = episodes()
    (HERE.parent / "data" / "episodes_188.json").write_text(json.dumps(eps, indent=1, ensure_ascii=False) + "\n")
    print("episodes", len(eps))
    paper = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
    mine = {(e["game"], e["first"]): e for e in eps}
    print("paper", len(paper), "unmatched", len(set(mine) ^ set(paper)))
    print("paper keys", sorted(next(iter(paper.values())).keys()))
