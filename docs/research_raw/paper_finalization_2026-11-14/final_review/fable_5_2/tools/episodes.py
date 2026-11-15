"""Rebuild the financing episodes from raw decisions.jsonl (read-only; no engine).
Writes checks/episodes_188.json inside this review folder only."""
import json
from lib import *

def episodes():
    out = []
    for g in range(1, 21):
        st, rs = load(g)
        cur, eps = None, []
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
            built = []
            for h in you["holdings"]["owned"]:
                sp = SPACES[h["space_key"]]
                n = h.get("houses", 0) + (5 if h.get("hotel") else 0)
                hotels += 1 if h.get("hotel") else 0
                houses += h.get("houses", 0)
                if n:
                    salvage += n * HOUSE_COST[sp["group"]] // 2
                    built.append([h["space_key"], h.get("houses", 0), bool(h.get("hotel"))])
                if not h.get("mortgaged"):
                    mstar += sp["price"] // 2
            listed = sc["options"].get("mortgageable_space_keys", [])
            sell_listed = sc["options"].get("sellable_building_space_keys", [])
            m0 = sum(SPACES[k]["price"] // 2 for k in listed)
            acts, proceeds, nsales, nmort = [], 0, 0, 0
            used_new = []
            for j in e["ds"]:
                fa = rs[j].get("final_action") or {}
                acts.append(fa.get("action"))
                if fa.get("action") == "mortgage_property":
                    k = fa["args"]["space_key"]; proceeds += SPACES[k]["price"] // 2; nmort += 1
                    if k not in listed: used_new.append(k)
                elif fa.get("action") == "sell_houses_or_hotel":
                    nsales += 1
                    for it in fa["args"]["sell_plan"]:
                        proceeds += it["count"] * HOUSE_COST[SPACES[it["space_key"]]["group"]] // 2
            e.update(first=i, last=e["ds"][-1], model=who(rs[i]), turn=rs[i]["turn_index"], debt=sc["owed_amount"],
                     creditor=sc.get("owed_to_player_id"), cash=you["cash"], salvage=salvage, m0=m0, mstar=mstar,
                     u0=you["cash"] + salvage + m0, ustar=you["cash"] + salvage + mstar,
                     hotels=hotels, houses=houses, built=built,
                     bank_houses=pp["game_state"]["bank"]["houses_remaining"],
                     listed_mortgages=listed, listed_sales=sell_listed,
                     menu=[a if isinstance(a, str) else a.get("action") for a in pp["action_state"]["available_actions"]],
                     actions=acts, n_sale_actions=nsales, n_mortgages=nmort, proceeds=proceeds,
                     fallbacks=[bool(rs[j].get("fallback_used")) for j in e["ds"]],
                     released_mortgages_used=used_new, declared=acts[-1] == "declare_bankruptcy",
                     last_event_types=rs[e["ds"][-1]].get("emitted_event_types") or [])
            e["sig"] = list(e["sig"]); del e["closed"]
            out.append(e)
    return out

if __name__ == "__main__":
    eps = episodes()
    OUT.mkdir(exist_ok=True)
    (OUT / "episodes_188.json").write_text(json.dumps(eps, indent=1, ensure_ascii=False) + "\n")
    print("episodes", len(eps))
