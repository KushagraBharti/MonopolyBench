"""Arithmetic over the rebuilt 188 episodes. Read-only."""
import json, collections
from lib import *
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
paper = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
C = collections.Counter
paid = [e for e in eps if not e["declared"] and paper[(e["game"], e["first"])]["outcome"] != "bankrupt"]
print("paper outcomes", C(p["outcome"] for p in paper.values()))
print("mine declared", sum(e["declared"] for e in eps))
# outcome from paper file
for e in eps:
    e["outcome"] = paper[(e["game"], e["first"])]["outcome"]
print("outcome x declared", C((e["outcome"], e["declared"]) for e in eps))
above = [e for e in eps if e["ustar"] < e["debt"]]
within = [e for e in eps if e["ustar"] >= e["debt"]]
print("U*>=D", len(within), "U*<D", len(above))
print("first action | U*>=D", C(e["actions"][0] for e in within))
print("first action | U*<D", C(e["actions"][0] for e in above))
print("above-bound menus with bankruptcy alone", sum(1 for e in above if e["menu"] == ["declare_bankruptcy"]))
print("within-bound menus with bankruptcy alone", sum(1 for e in within if e["menu"] == ["declare_bankruptcy"]))
print()
print("== above-bound episodes whose first action is not a declaration")
for e in above:
    if e["actions"][0] != "declare_bankruptcy":
        print(f"G{e['game']} d{e['first']}-d{e['last']} {e['model']} debt {e['debt']} cash {e['cash']} S {e['salvage']} M0 {e['m0']} M* {e['mstar']} U* {e['ustar']} gap {e['debt']-e['ustar']} actions {e['actions']} outcome {e['outcome']} creditor {e['creditor']} last_events {C(e['last_event_types']).most_common(4)}")
print()
print("== necessity set and partition")
pay = [e for e in eps if e["outcome"] == "paid"]
print("paid", len(pay), "sum debt", sum(e["debt"] for e in pay))
print("actions in paid", C(a for e in pay for a in e["actions"]))
print("paid n actions", C(len(e["actions"]) for e in pay))
print("fallback in paid", sum(any(e["fallbacks"]) for e in pay))
nec = [e for e in eps if e["u0"] < e["debt"] <= e["ustar"]]
print("necessity", len(nec), C((e["model"], e["outcome"]) for e in nec))
print("necessity by game", C(e["game"] for e in nec))
print("decisions inside the 16 episodes", sum(len(e["ds"]) for e in nec), "inside all 188", sum(len(e["ds"]) for e in eps))
hotel_eps = [e for e in eps if e["hotels"]]
print("episodes with hotels at entry", len(hotel_eps), C((e["outcome"], e["ustar"] >= e["debt"]) for e in hotel_eps))
for e in hotel_eps:
    print(f"   G{e['game']} d{e['first']} {e['model']} hotels {e['hotels']} houses {e['houses']} bank_houses {e['bank_houses']} debt {e['debt']} U0 {e['u0']} U* {e['ustar']} outcome {e['outcome']} first {e['actions'][0]} n {len(e['actions'])} listed_sales {e['listed_sales']}")
