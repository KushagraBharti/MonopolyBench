"""Independent arithmetic over the rebuilt episodes (read-only; no engine, no policy).
Checks: census, partition, first-action table, payment totals, the 28/30
building-preservation subset, and the premises of the continued-financing argument."""
import json, collections
from lib import *
C = collections.Counter
eps = json.loads((OUT / "episodes_188.json").read_text())
res = {}
# --- outcome from arithmetic alone: paid iff not declared and cash + proceeds >= debt
for e in eps:
    e["paid"] = (not e["declared"]) and (e["cash"] + e["proceeds"] >= e["debt"])
    e["first_action"] = e["actions"][0]
paid = [e for e in eps if e["paid"]]
res["episodes"] = len(eps); res["paid"] = len(paid); res["eliminated"] = len(eps) - len(paid)
res["paid_debt_total"] = sum(e["debt"] for e in paid)
res["mortgage_actions_in_paid"] = sum(e["n_mortgages"] for e in paid)
res["sale_actions_in_paid"] = sum(e["n_sale_actions"] for e in paid)
res["one_action_payments"] = sum(1 for e in paid if len(e["ds"]) == 1)
res["multi_action_payments"] = sum(1 for e in paid if len(e["ds"]) > 1)
res["max_actions"] = max(len(e["ds"]) for e in paid)
res["fallback_in_paid"] = sum(any(e["fallbacks"]) for e in paid)
PAYABLE_DECLARED = {(12, 190), (17, 234), (12, 249)}   # inherited engine-executed witnesses (not rerun)
payable = [e for e in eps if e["paid"] or (e["game"], e["first"]) in PAYABLE_DECLARED]
def cat(e):
    if e["cash"] + e["m0"] >= e["debt"]: return "A_initial"
    if e["u0"] >= e["debt"]: return "B_sale_no_release"
    return "C_release_required"
res["payable"] = len(payable)
res["partition"] = dict(C(cat(e) for e in payable)); res["partition_paid"] = dict(C(cat(e) for e in payable if e["paid"]))
# --- first-action table
cov = [e for e in eps if e["ustar"] >= e["debt"]]; short = [e for e in eps if e["ustar"] < e["debt"]]
res["first_actions"] = {
  "bound_covers": {"n": len(cov), "declare": sum(e["first_action"] == "declare_bankruptcy" for e in cov)},
  "bound_short": {"n": len(short), "declare": sum(e["first_action"] == "declare_bankruptcy" for e in short),
                  "only_bankruptcy_offered": sum(1 for e in short if not e["listed_mortgages"] and not e["listed_sales"])}}
res["above_bound_starts"] = sorted(f"G{e['game']} d{e['first']} {e['model']} D{e['debt']} U*{e['ustar']} first={e['first_action']} actions={e['actions']}" for e in short if e["first_action"] != "declare_bankruptcy")
res["covered_not_paid"] = sorted(f"G{e['game']} d{e['first']} {e['model']} D{e['debt']} U0 {e['u0']} U*{e['ustar']} actions={e['actions']}" for e in cov if not e["paid"])
res["first_menu_declare_by_region_model"] = {}
for name, pop in (("U0>=D", [e for e in eps if e["u0"] >= e["debt"]]), ("U0<D<=U*", [e for e in eps if e["u0"] < e["debt"] <= e["ustar"]]), ("U*<D", short)):
    res["first_menu_declare_by_region_model"][name] = {m: f"{sum(e['first_action']=='declare_bankruptcy' for e in pop if e['model']==m)}/{sum(e['model']==m for e in pop)}" for m in ("Sol","Gemini","Opus","Grok")}
# --- 28/30: payable from cash + initially listed mortgages, debtor owns buildings
A = [e for e in payable if cat(e) == "A_initial"]
own = [e for e in A if e["built"]]
sold = [e for e in own if e["n_sale_actions"]]
res["development_preservation"] = {"class_A": len(A), "class_A_paid": sum(e["paid"] for e in A), "building_owners": len(own),
   "paid_without_any_sale": sum(1 for e in own if e["paid"] and not e["n_sale_actions"]),
   "sold": [f"G{e['game']} d{e['first']} {e['model']} D{e['debt']} C{e['cash']} M0 {e['m0']} built={e['built']} actions={e['actions']}" for e in sold],
   "owners_by_model": dict(C(e["model"] for e in own)),
   "members": sorted([e["game"], e["first"]] for e in own)}
# --- continuation premises
rows = []
for e in payable:
    st, rs = load(e["game"])
    you = st[e["first"]]["prompt_payload"]["game_state"]["you"]
    owned = {h["space_key"]: h for h in you["holdings"]["owned"]}
    built_groups = {SPACES[k]["group"] for k, h in owned.items() if h.get("houses") or h.get("hotel")}
    p1 = all(COLORS[g] <= set(owned) for g in built_groups)
    lv = {g: [(5 if owned[k].get("hotel") else owned[k].get("houses", 0)) for k in COLORS[g]] for g in built_groups if COLORS[g] <= set(owned)}
    p2 = all(max(v) - min(v) <= 1 for v in lv.values())
    hotels_per_group = {g: sum(1 for x in v if x == 5) for g, v in lv.items()}
    h_free = sum(sum(v) for g, v in lv.items() if hotels_per_group[g] == 0)
    cls = "hotel_free" if e["hotels"] == 0 else ("initial_mortgages" if e["cash"] + e["m0"] >= e["debt"] else ("stocked_downgrades" if e["bank_houses"] >= 4 * e["hotels"] else "recyclable_stock"))
    rows.append(dict(id=f"G{e['game']} d{e['first']}", model=e["model"], p1=p1, p2=p2, p3=e["ustar"] >= e["debt"], cls=cls,
                     hotels=e["hotels"], bank=e["bank_houses"], h_free=h_free, max_hotels_in_group=max(hotels_per_group.values(), default=0), levels=lv))
res["continuation"] = {"n": len(rows), "p1_complete_ownership": sum(r["p1"] for r in rows), "p2_even": sum(r["p2"] for r in rows), "p3_bound": sum(r["p3"] for r in rows),
                       "classes": dict(C(r["cls"] for r in rows)),
                       "recyclable": [r for r in rows if r["cls"] == "recyclable_stock"],
                       "necessity_class": dict(C(r["cls"] for r, e in zip(rows, payable) if cat(e) == "C_release_required"))}
# --- released collateral use
used = [e for e in paid if e["released_mortgages_used"]]
res["released_use"] = {"payments": len(used), "mortgages": sum(len(e["released_mortgages_used"]) for e in used), "by_class": dict(C(cat(e) for e in used)),
                       "non_necessity": sorted(f"G{e['game']} d{e['first']} {e['model']}" for e in used if cat(e) != "C_release_required")}
B = [e for e in payable if cat(e) == "B_sale_no_release"]
res["middle"] = {"n": len(B), "paid_no_release": sum(1 for e in B if e["paid"] and not e["released_mortgages_used"])}
# --- necessity sixteen: remainder after payment
res["sixteen"] = [dict(id=f"G{e['game']} d{e['first']}", model=e["model"], D=e["debt"], C=e["cash"], U0=e["u0"], Ustar=e["ustar"],
                       paid=e["paid"], left=(e["cash"] + e["proceeds"] - e["debt"]) if e["paid"] else None, actions=e["actions"],
                       hotels=e["hotels"]) for e in payable if cat(e) == "C_release_required"]
res["by_model"] = {m: {"episodes": sum(e["model"] == m for e in eps), "paid": sum(e["model"] == m for e in paid), "payable": sum(e["model"] == m for e in payable)} for m in ("Sol","Gemini","Opus","Grok")}
(OUT / "finance_checks.json").write_text(json.dumps(res, indent=1) + "\n")
for k, v in res.items():
    if k in ("sixteen",): 
        for r in v: print("  ", r)
    else: print(k, "=", json.dumps(v)[:1500])
