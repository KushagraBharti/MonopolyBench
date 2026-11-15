"""Descriptive liquidation composition without any search or optimum. Read-only arithmetic.

Category A: cash plus initially listed mortgages cover the debt. A building sale there is a route that
raises cash at a 50% loss when a 10% route was open. This is a description under a stated cost ordering,
not a regret computed against a searched optimum.
"""
import json, collections, statistics
from lib import *
C = collections.Counter
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
paper = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
rows = []
for e in eps:
    e["outcome"] = paper[(e["game"], e["first"])]["outcome"]
    if e["outcome"] != "paid":
        continue
    st, rs = load(e["game"])
    sale = mort = 0
    for d in e["ds"]:
        fa = rs[d]["final_action"]
        if fa["action"] == "mortgage_property":
            mort += SPACES[fa["args"]["space_key"]]["price"] // 2
        elif fa["action"] == "sell_houses_or_hotel":
            sale += sum(HOUSE_COST[SPACES[i["space_key"]]["group"]] // 2 * i["count"] for i in fa["args"]["sell_plan"])
    cat = "A" if e["cash"] + e["m0"] >= e["debt"] else ("B" if e["u0"] >= e["debt"] else "C")
    rows.append(dict(game=e["game"], first=e["first"], model=e["model"], cat=cat, debt=e["debt"], cash=e["cash"], m0=e["m0"], salvage=e["salvage"],
                     sale=sale, mort=mort, over=e["cash"] + sale + mort - e["debt"], n=len(e["ds"]), has_buildings=e["salvage"] > 0))
print("paid", len(rows), C(r["cat"] for r in rows))
A = [r for r in rows if r["cat"] == "A"]
print("A: episodes with any building sale:", sum(1 for r in A if r["sale"] > 0), "of", len(A), "| A with buildings held:", sum(1 for r in A if r["has_buildings"]))
print("A sellers by model:", C(r["model"] for r in A if r["sale"] > 0), "A with buildings by model:", C(r["model"] for r in A if r["has_buildings"]))
for r in A:
    if r["sale"] > 0:
        print(f"   G{r['game']} d{r['first']} {r['model']} debt {r['debt']} cash {r['cash']} listed M0 {r['m0']} sold {r['sale']} mortgaged {r['mort']} end surplus {r['over']}")
for cat in "ABC":
    R = [r for r in rows if r["cat"] == cat]
    print(cat, "n", len(R), "median surplus after payment", statistics.median(r["over"] for r in R), "total sale", sum(r["sale"] for r in R), "total mortgage", sum(r["mort"] for r in R))
print("all paid: total sale proceeds", sum(r["sale"] for r in rows), "total mortgage proceeds", sum(r["mort"] for r in rows))
(HERE.parent / "data" / "liquidation_composition.json").write_text(json.dumps(rows, indent=1) + "\n")
