"""Financing census, resource partition, first actions and continuation premises.

Reads the retained 188-episode ledger (inherited episode detector), the original
decision records and board values. Recomputes every entry bound and route amount
by arithmetic. Does not execute the engine, a policy, a replay or a search.
The three payable declarations rely on the earlier engine-executed witnesses,
which are inherited and not rerun here.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from statistics import median

import lib

WITNESSED_DECLARATIONS = {(12, 190), (17, 234), (12, 249)}  # inherited executable witnesses
MENU_RESTRICTED = {(7, 338)}  # inherited restricted menu search


def applied_actions(game: int, decision_ids: list[str]) -> list[dict]:
    rows = []
    for did in decision_ids:
        idx = int(did.rsplit("-", 1)[1])
        rz = lib.decision(game, idx)["decision_resolved"]
        fa = rz["final_action"]
        act = fa["action"]
        amount = 0
        detail = None
        if act == "mortgage_property":
            key = fa["args"]["space_key"]
            amount = lib.mortgage_value(key)
            detail = key
        elif act == "sell_houses_or_hotel":
            plan = fa["args"].get("sell_plan", [])
            detail = plan
            for item in plan:
                amount += lib.unit_salvage(item["space_key"]) * int(item.get("count", 1))
        rows.append({
            "decision": idx,
            "action": act,
            "amount": amount,
            "detail": detail,
            "fallback": bool(rz.get("fallback_used")),
            "conditions": [a.get("response_condition") for a in rz.get("attempts", [])],
        })
    return rows


def main() -> None:
    eps = lib.episodes()
    assert len(eps) == 188
    out = []
    mismatches = []
    for e in eps:
        g, i = e["game"], e["first_decision"]
        x = lib.entry_state(g, i)
        if x["Ustar"] != e["upper_bound"]:
            mismatches.append((g, i, x["Ustar"], e["upper_bound"]))
        acts = applied_actions(g, e["decisions"])
        key = (g, i)
        if e["outcome"] == "paid" or key in WITNESSED_DECLARATIONS:
            category = "payable"
        elif key in MENU_RESTRICTED:
            category = "menu_restricted"
        elif x["Ustar"] < x["D"]:
            category = "above_bound"
        else:
            category = "unclassified"
        if category == "payable":
            if x["C"] + x["M0"] >= x["D"]:
                region = "A_cash_and_listed_mortgages"
            elif x["U0"] >= x["D"]:
                region = "B_sales_needed_no_release"
            else:
                region = "C_release_necessary"
        else:
            region = None
        mort_keys = [a["detail"] for a in acts if a["action"] == "mortgage_property"]
        released = [k for k in mort_keys if k not in x["listed_mortgages"]]
        sale_proceeds = sum(a["amount"] for a in acts if a["action"] == "sell_houses_or_hotel")
        mort_proceeds = sum(a["amount"] for a in acts if a["action"] == "mortgage_property")
        row = {k: v for k, v in x.items() if k != "holdings"}
        row.update({
            "outcome": e["outcome"],
            "category": category,
            "region": region,
            "first_action": acts[0]["action"],
            "first_action_fallback": acts[0]["fallback"],
            "n_decisions": len(acts),
            "actions": [{k: v for k, v in a.items() if k != "detail"} for a in acts],
            "mortgaged": mort_keys,
            "released_mortgages_used": released,
            "sale_proceeds": sale_proceeds,
            "mortgage_proceeds": mort_proceeds,
            "cash_after_payment": (x["C"] + sale_proceeds + mort_proceeds - x["D"]) if e["outcome"] == "paid" else None,
            "fallback_actions": sum(a["fallback"] for a in acts),
        })
        out.append(row)

    # Partition and outcomes
    pay = [r for r in out if r["category"] == "payable"]
    part = {}
    for reg in ["A_cash_and_listed_mortgages", "B_sales_needed_no_release", "C_release_necessary"]:
        rr = [r for r in pay if r["region"] == reg]
        part[reg] = {"episodes": len(rr), "paid": sum(r["outcome"] == "paid" for r in rr)}

    # First-menu declarations by bound region (entry-defined)
    def region_of(r):
        if r["Ustar"] < r["D"]:
            return "Ustar_below_D"
        if r["U0"] >= r["D"]:
            return "U0_at_least_D"
        return "U0_below_D_le_Ustar"

    first = defaultdict(lambda: Counter())
    first_by_model = defaultdict(lambda: defaultdict(Counter))
    for r in out:
        reg = region_of(r)
        first[reg]["n"] += 1
        first[reg][r["first_action"]] += 1
        first_by_model[reg][r["model"]]["n"] += 1
        first_by_model[reg][r["model"]][r["first_action"]] += 1
    only_declare = [
        (r["game"], r["decision"]) for r in out
        if r["Ustar"] < r["D"] and r["menu_actions"] == ["declare_bankruptcy"]
    ]

    # Episodes per model and paid counts
    by_model = defaultdict(Counter)
    for r in out:
        by_model[r["model"]]["episodes"] += 1
        by_model[r["model"]][r["outcome"]] += 1

    # Action totals for paid episodes
    paid = [r for r in out if r["outcome"] == "paid"]
    n_mort = sum(1 for r in paid for a in r["actions"] if a["action"] == "mortgage_property")
    n_sell = sum(1 for r in paid for a in r["actions"] if a["action"] == "sell_houses_or_hotel")
    paid_debt = sum(r["D"] for r in paid)
    one_action = sum(1 for r in paid if r["n_decisions"] == 1)
    paid_fallbacks = sum(r["fallback_actions"] for r in paid)

    # Released collateral use
    released_use = [r for r in paid if r["released_mortgages_used"]]

    # Mortgage-first financing (descriptive, search-free)
    regA_paid = [r for r in paid if r["region"] == "A_cash_and_listed_mortgages"]
    regA_with_buildings = [r for r in regA_paid if r["S"] > 0]
    regA_sold = [r for r in regA_with_buildings if r["sale_proceeds"] > 0]
    regB_paid = [r for r in paid if r["region"] == "B_sales_needed_no_release"]
    excess = []
    for r in regB_paid:
        need = r["D"] - r["C"] - r["M0"]
        excess.append({"game": r["game"], "decision": r["decision"], "model": r["model"],
                       "required_sale_after_listed_mortgages": need,
                       "sale_proceeds": r["sale_proceeds"],
                       "excess": r["sale_proceeds"] - need,
                       "released_used": bool(r["released_mortgages_used"])})
    ex_vals = [x["excess"] for x in excess if not x["released_used"]]

    # Continuation premises for all 131 payable entries (source argument; arithmetic only)
    prem = []
    for r in pay:
        if r["hotels"] == 0:
            support = "hotel_free"
        elif r["C"] + r["M0"] >= r["D"]:
            support = "initial_cash_and_listed_mortgages_suffice"
        elif r["bank_houses"] >= 4 * r["hotels"]:
            support = "bank_stock_covers_every_hotel_downgrade"
        elif all(v <= 1 for v in r["hotels_by_group"].values()) and r["bank_houses"] + r["houses_in_hotel_free_groups"] >= 4:
            support = "single_hotel_per_group_recyclable_stock"
        else:
            support = "not_covered"
        prem.append({"game": r["game"], "decision": r["decision"], "model": r["model"],
                     "complete": r["complete"], "even": r["even"], "Ustar_ge_D": r["Ustar"] >= r["D"],
                     "hotels_by_group": r["hotels_by_group"], "bank_houses": r["bank_houses"],
                     "houses_in_hotel_free_groups": r["houses_in_hotel_free_groups"], "support": support})
    assert all(p["complete"] and p["even"] and p["Ustar_ge_D"] for p in prem)

    summary = {
        "episodes": len(out),
        "outcomes": dict(Counter(r["outcome"] for r in out)),
        "categories": dict(Counter(r["category"] for r in out)),
        "Ustar_mismatches_vs_retained_ledger": mismatches,
        "partition": part,
        "first_menu_by_region": {k: dict(v) for k, v in first.items()},
        "first_menu_by_region_model": {k: {m: dict(c) for m, c in v.items()} for k, v in first_by_model.items()},
        "above_bound_menus_offering_only_bankruptcy": only_declare,
        "episodes_by_model": {k: dict(v) for k, v in by_model.items()},
        "paid": {"n": len(paid), "mortgage_actions": n_mort, "sale_actions": n_sell, "obligations_paid": paid_debt,
                 "one_action": one_action, "two_or_more": len(paid) - one_action,
                 "fallback_actions_in_paid_episodes": paid_fallbacks},
        "released_collateral_use": {"payments": len(released_use),
                                    "mortgages": sum(len(r["released_mortgages_used"]) for r in released_use),
                                    "necessity_payments": sum(r["region"] == "C_release_necessary" for r in released_use),
                                    "other": [(r["game"], r["decision"], r["model"], r["region"]) for r in released_use if r["region"] != "C_release_necessary"]},
        "mortgage_first": {
            "regionA_paid": len(regA_paid),
            "regionA_paid_holding_buildings": len(regA_with_buildings),
            "regionA_paid_selling_any_building": [(r["game"], r["decision"], r["model"], r["sale_proceeds"]) for r in regA_sold],
            "regionB_paid": len(regB_paid),
            "regionB_excess_median": median(ex_vals) if ex_vals else None,
            "regionB_excess_max": max(ex_vals) if ex_vals else None,
            "regionB_excess_ge_100": sum(v >= 100 for v in ex_vals),
            "regionB_paid_without_released_mortgage": len(ex_vals),
            "regionB_excess_min": min(ex_vals) if ex_vals else None,
            "regionB_paid_using_released_mortgage": [(x["game"], x["decision"], x["model"]) for x in excess if x["released_used"]],
        },
        "continuation_premises": dict(Counter(p["support"] for p in prem)),
        "inputs": {lib.rel(p): lib.sha256_file(p) for p in [lib.EPISODE_FILE, lib.BOARD_FILE, lib.GAME_MAP_FILE]},
        "method": "Arithmetic over stored records; no engine, policy, replay, search or model call.",
    }
    lib.write_json("finance_census.json", {"summary": summary, "rows": out})
    lib.write_json("continuation_premises.json", {"summary": summary["continuation_premises"], "rows": prem,
                                                  "excess_rows_regionB": excess})
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
