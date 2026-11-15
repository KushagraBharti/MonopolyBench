"""Cross-review check. For every demonstrated-payable debt, test the premises of the continued-financing
argument at entry and count how many states it covers. Read-only arithmetic on recorded holdings.

Premises checked per state:
  P1  every color group that holds a building is completely owned by the debtor
  P2  building levels within each such group differ by at most one (hotel counts as five)
  P3  U* >= debt
Coverage classes (any one suffices for 'no continuing sequence of offered financing actions ends unpaid'):
  H0  no hotel at entry (every building is sellable in some order, stock only rises)
  A   cash plus initially listed mortgages >= debt (listed mortgages stay listed until used,
      so a state with nothing offered has cash >= C + M0 >= D and was already paid)
  S   bank houses >= 4 x hotels held (every downgrade is affordable in the worst order)
No policy is executed and no state is advanced.
"""
import json, collections
from lib import *
C = collections.Counter
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
paper = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
PAYABLE_DECLARED = {(12, 190), (17, 234), (12, 249)}
rows = []
for e in eps:
    key = (e["game"], e["first"])
    if not (paper[key]["outcome"] == "paid" or key in PAYABLE_DECLARED):
        continue
    st, rs = load(e["game"])
    you = st[e["first"]]["prompt_payload"]["game_state"]["you"]
    owned = {h["space_key"]: h for h in you["holdings"]["owned"]}
    built_groups = {SPACES[k]["group"] for k, h in owned.items() if h["houses"] or h["hotel"]}
    p1 = all(COLORS[g] <= set(owned) for g in built_groups)
    p2 = True
    for g in built_groups:
        lv = [(5 if owned[k]["hotel"] else owned[k]["houses"]) for k in COLORS[g] if k in owned]
        if max(lv) - min(lv) > 1:
            p2 = False
    p3 = e["ustar"] >= e["debt"]
    h0 = e["hotels"] == 0
    a = e["cash"] + e["m0"] >= e["debt"]
    s = e["bank_houses"] >= 4 * e["hotels"]
    rows.append(dict(game=e["game"], first=e["first"], model=e["model"], p1=p1, p2=p2, p3=p3, H0=h0, A=a, S=s,
                     hotels=e["hotels"], bank=e["bank_houses"], necessity=e["u0"] < e["debt"]))
print("payable", len(rows), "P1 complete ownership", sum(r["p1"] for r in rows), "P2 even", sum(r["p2"] for r in rows), "P3 U*>=D", sum(r["p3"] for r in rows))
ok = [r for r in rows if r["p1"] and r["p2"] and r["p3"]]
print("hotel-free", sum(r["H0"] for r in ok), "| hotel states", sum(not r["H0"] for r in ok))
cov = [r for r in ok if r["H0"] or r["A"] or r["S"]]
print("covered by H0 or A or S:", len(cov), "of", len(rows), "| by class (first that applies):", C("H0" if r["H0"] else ("A" if r["A"] else "S") for r in cov))
print("necessity sixteen covered:", sum(1 for r in cov if r["necessity"]), "of", sum(r["necessity"] for r in rows))
print("not covered by these three sufficient conditions:")
for r in ok:
    if not (r["H0"] or r["A"] or r["S"]):
        print(f"   G{r['game']} d{r['first']} {r['model']} hotels {r['hotels']} bank houses {r['bank']}")
