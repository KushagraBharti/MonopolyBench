"""Resource partition of payable debts and the 'released mortgages not necessary' category. Read-only arithmetic."""
import json, collections
from lib import *
C = collections.Counter
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
paper = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
for e in eps:
    e["outcome"] = paper[(e["game"], e["first"])]["outcome"]
PAYABLE_DECLARED = {(12, 190), (17, 234), (12, 249)}
payable = [e for e in eps if e["outcome"] == "paid" or (e["game"], e["first"]) in PAYABLE_DECLARED]
print("demonstrated payable", len(payable))
def cat(e):
    if e["cash"] + e["m0"] >= e["debt"]:
        return "A cash+listed mortgages"
    if e["u0"] >= e["debt"]:
        return "B sales also, release not necessary by bound"
    return "C release necessary"
print(C(cat(e) for e in payable))
print(C((cat(e), e["outcome"]) for e in payable))
B = [e for e in payable if cat(e).startswith("B")]
print("B: used released mortgages", C(bool(e["released_mortgages_used"]) for e in B))
print("B: hotels at entry", C(bool(e["hotels"]) for e in B), " hotels & used released", sum(1 for e in B if e["hotels"] and e["released_mortgages_used"]))
print("B: paid without any released mortgage (observed no-release witness):", sum(1 for e in B if e["outcome"] == "paid" and not e["released_mortgages_used"]))
print()
for e in B:
    if e["released_mortgages_used"] or e["outcome"] != "paid":
        st, rs = load(e["game"])
        seq = []
        for d in e["ds"]:
            fa = rs[d]["final_action"]
            if fa["action"] == "mortgage_property":
                k = fa["args"]["space_key"]; seq.append(f"M:{k}({SPACES[k]['price']//2}){'*' if k in e['released_mortgages_used'] else ''}")
            elif fa["action"] == "sell_houses_or_hotel":
                seq.append("S:" + ",".join(f"{i['space_key']}x{i['count']}{i['kind'][0]}" for i in fa["args"]["sell_plan"]))
            else:
                seq.append("DECLARE")
        print(f"G{e['game']} d{e['first']} {e['model']} D {e['debt']} C {e['cash']} S {e['salvage']} M0 {e['m0']} U0 {e['u0']} U* {e['ustar']} hotels {e['hotels']} houses {e['houses']} bank_houses {e['bank_houses']} outcome {e['outcome']}")
        print("     listed mortgages", e["listed_mortgages"], "listed sales", e["listed_sales"])
        print("     route", " | ".join(seq))
        st0 = st[e["first"]]["prompt_payload"]["game_state"]["you"]["holdings"]["owned"]
        print("     built:", [(h["space_key"], h["houses"], h["hotel"]) for h in st0 if h["houses"] or h["hotel"]])
print()
# all 19 payments that used released mortgages
used = [e for e in eps if e["released_mortgages_used"] and e["outcome"] == "paid"]
print("payments using released mortgages", len(used), "mortgages", sum(len(e["released_mortgages_used"]) for e in used), C(cat(e) for e in used))
# hotel-free payable episodes
print("payable hotel-free", sum(1 for e in payable if not e["hotels"]), "payable with hotels", sum(1 for e in payable if e["hotels"]))
print("payable with hotels by category", C(cat(e) for e in payable if e["hotels"]))
