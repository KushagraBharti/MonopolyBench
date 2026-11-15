"""Executed routes, values and end cash for the sixteen necessity episodes. Read-only arithmetic."""
import json
from lib import *
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
nec = [e for e in eps if e["u0"] < e["debt"] <= e["ustar"]]
out = []
for e in nec:
    st, rs = load(e["game"])
    you = st[e["first"]]["prompt_payload"]["game_state"]["you"]
    built = {h["space_key"]: (h["houses"], h["hotel"]) for h in you["holdings"]["owned"] if h["houses"] or h["hotel"]}
    groups = {SPACES[k]["group"] for k in built}
    released = [h["space_key"] for h in you["holdings"]["owned"] if not h["mortgaged"] and SPACES[h["space_key"]].get("group") in groups]
    rel_val = {k: SPACES[k]["price"] // 2 for k in released}
    seq = []; raised_s = raised_m = 0
    for d in e["ds"]:
        fa = rs[d]["final_action"]
        if fa["action"] == "mortgage_property":
            k = fa["args"]["space_key"]; v = SPACES[k]["price"] // 2; raised_m += v
            seq.append(f"M {k} {v}{' (released)' if k in released else ''}")
        elif fa["action"] == "sell_houses_or_hotel":
            v = sum(HOUSE_COST[SPACES[i["space_key"]]["group"]] // 2 * i["count"] for i in fa["args"]["sell_plan"]); raised_s += v
            seq.append("S " + ", ".join(f"{i['space_key']}x{i['count']}{i['kind'][0]}" for i in fa["args"]["sell_plan"]) + f" {v}")
        else:
            seq.append("DECLARE")
    nxt = e["ds"][-1] + 1
    pid = st[e["first"]]["player_id"]
    end_cash = None
    while nxt in st:
        if st[nxt]["player_id"] == pid:
            end_cash = st[nxt]["prompt_payload"]["game_state"]["you"]["cash"]; break
        nxt += 1
    row = dict(game=e["game"], first=e["first"], model=e["model"], debt=e["debt"], cash=e["cash"], salvage=e["salvage"], m0=e["m0"],
               listed=e["listed_mortgages"], released_values=rel_val, released_sum=sum(rel_val.values()), u0=e["u0"], ustar=e["ustar"],
               built=built, bank_houses=e["bank_houses"], route=seq, raised_sales=raised_s, raised_mortgages=raised_m,
               after_pay=(e["cash"] + raised_s + raised_m - e["debt"]) if not e["declared"] else None, next_cash=end_cash, n_actions=len(e["ds"]),
               conditions=[rs[d]["attempts"][-1].get("response_condition") for d in e["ds"]])
    out.append(row)
    print(f"G{e['game']} d{e['first']} {e['model']} D {e['debt']} C {e['cash']} S {e['salvage']} M0 {e['m0']} released {rel_val} U0 {e['u0']} U* {e['ustar']} bank {e['bank_houses']}")
    print("    built", built)
    for s in seq: print("    ", s)
    print(f"    raised sales {raised_s} mortgages {raised_m} -> after pay {row['after_pay']} (next own cash {end_cash}); unused U* slack {e['ustar'] - e['debt']}")
(HERE.parent / "data" / "sixteen_routes.json").write_text(json.dumps(out, indent=1) + "\n")
