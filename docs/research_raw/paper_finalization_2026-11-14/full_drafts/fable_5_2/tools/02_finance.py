"""Arithmetic over the rebuilt episodes: census, payable partition, first actions,
premises of the continued-financing argument, the middle category and route composition.

Read-only. Does not advance any state. Writes data/finance_summary.json.
"""
import collections
import statistics

from lib import *

C = collections.Counter
eps = read_json("episodes.json")
# Three declarations on debts for which a legal payment sequence was executed in the
# engine audit that predates this paper (retained, not rerun here).
WITNESSED = {(12, 190), (17, 234), (12, 249)}
# One episode whose nominal bound covers the debt but whose menu could not reach it
# (retained restricted search, not rerun).
MENU_UNPAYABLE = {(7, 338)}


def k(e):
    return (e["game"], e["first"])


def cat(e):
    if e["cash"] + e["m0"] >= e["debt"]:
        return "A"
    if e["u0"] >= e["debt"]:
        return "B"
    return "C"


def coverage(e):
    """First sufficient condition, in a fixed order, under which no continuing sequence
    of valid cash-raising actions can reach an unpaid state with nothing offered."""
    if e["hotels"] == 0:
        return "no_hotel"
    if e["cash"] + e["m0"] >= e["debt"]:
        return "listed_mortgages_suffice"
    if e["bank_houses"] >= 4 * e["hotels"]:
        return "stock_covers_every_downgrade"
    one_each = all(n <= 1 for n in e["hotels_by_group"].values())
    if one_each and e["bank_houses"] + e["houses_in_hotel_free_groups"] >= 4:
        return "one_hotel_per_group_recyclable_stock"
    return "uncovered"


S = {}
paid = [e for e in eps if e["outcome"] == "paid"]
bank = [e for e in eps if e["outcome"] == "bankrupt"]
S["episodes"] = len(eps)
S["paid"] = len(paid)
S["eliminated"] = len(bank)
S["liquidation_decisions"] = sum(len(e["decisions"]) for e in eps)
S["paid_debt_total"] = sum(e["debt"] for e in paid)
S["paid_mortgage_actions"] = sum(1 for e in paid for a in e["actions"] if a == "mortgage_property")
S["paid_sale_actions"] = sum(1 for e in paid for a in e["actions"] if a == "sell_houses_or_hotel")
S["paid_one_action"] = sum(1 for e in paid if len(e["actions"]) == 1)
S["paid_multi_action"] = sum(1 for e in paid if len(e["actions"]) > 1)
S["paid_max_actions"] = max(len(e["actions"]) for e in paid)
S["paid_with_fallback"] = sum(1 for e in paid if any(e["fallbacks"]))
S["first_action_fallbacks"] = sum(1 for e in eps if e["fallbacks"][0])
S["episodes_by_model"] = dict(C(e["model"] for e in eps))
S["paid_by_model"] = dict(C(e["model"] for e in paid))
S["multi_action_paid_by_model"] = dict(C(e["model"] for e in paid if len(e["actions"]) > 1))

within = [e for e in eps if e["ustar"] >= e["debt"]]
above = [e for e in eps if e["ustar"] < e["debt"]]
S["bound_covers"] = len(within)
S["bound_short"] = len(above)
S["declare_first_when_covers"] = sum(1 for e in within if e["first_action"] == "declare_bankruptcy")
S["declare_first_when_short"] = sum(1 for e in above if e["first_action"] == "declare_bankruptcy")
S["short_menus_bankruptcy_only"] = sum(1 for e in above if e["menu"] == ["declare_bankruptcy"])
S["covers_menus_bankruptcy_only"] = sum(1 for e in within if e["menu"] == ["declare_bankruptcy"])
S["short_start_financing"] = [f"G{e['game']} d{e['first']} {e['model']}" for e in above if e["first_action"] != "declare_bankruptcy"]
S["covers_declare_first"] = [f"G{e['game']} d{e['first']} {e['model']}" for e in within if e["first_action"] == "declare_bankruptcy"]
S["bankrupt_without_declaration"] = [f"G{e['game']} d{e['first']} {e['model']} U*{'>=' if e['ustar'] >= e['debt'] else '<'}D actions {e['actions']}" for e in bank if not e["declared"]]

payable = [e for e in eps if e["outcome"] == "paid" or k(e) in WITNESSED]
S["payable"] = len(payable)
assert all(e["ustar"] >= e["debt"] for e in payable)
S["covers_but_not_payable"] = [f"G{e['game']} d{e['first']} {e['model']}" for e in within if e not in payable]
part = C(cat(e) for e in payable)
part_paid = C(cat(e) for e in payable if e["outcome"] == "paid")
S["partition"] = {c: {"episodes": part[c], "paid": part_paid[c]} for c in "ABC"}
S["partition_by_model"] = {c: dict(C(e["model"] for e in payable if cat(e) == c)) for c in "ABC"}
S["necessity_by_model"] = {m: [sum(1 for e in payable if cat(e) == "C" and e["model"] == m and e["outcome"] == "paid"),
                               sum(1 for e in payable if cat(e) == "C" and e["model"] == m)] for m in ("Sol", "Gemini", "Opus", "Grok")}
S["necessity_games"] = dict(C(e["game"] for e in payable if cat(e) == "C"))
S["necessity_decisions"] = sum(len(e["decisions"]) for e in payable if cat(e) == "C")

# middle category support
B = [e for e in payable if cat(e) == "B"]
S["middle_paid_without_released"] = sum(1 for e in B if e["outcome"] == "paid" and not e["released_mortgages_used"])
S["middle_paid_with_released"] = [f"G{e['game']} d{e['first']} {e['model']}" for e in B if e["outcome"] == "paid" and e["released_mortgages_used"]]
S["middle_declared"] = [f"G{e['game']} d{e['first']} {e['model']}" for e in B if e["outcome"] != "paid"]
S["middle_constructive"] = [
    dict(entry=f"G{e['game']} d{e['first']}", model=e["model"], cash=e["cash"], debt=e["debt"], m0=e["m0"], salvage=e["salvage"],
         u0=e["u0"], hotels=e["hotels"], bank_houses=e["bank_houses"], built=e["built"], hotels_by_group=e["hotels_by_group"])
    for e in B if e["outcome"] == "paid" and e["released_mortgages_used"]]

# uses of released mortgages
used = [e for e in paid if e["released_mortgages_used"]]
S["payments_using_released"] = len(used)
S["released_mortgages_used"] = sum(len(e["released_mortgages_used"]) for e in used)
S["payments_using_released_by_category"] = dict(C(cat(e) for e in used))

# continued-financing premises
S["premise_complete_ownership"] = sum(1 for e in payable if e["developed_groups_complete"])
S["premise_even"] = sum(1 for e in payable if e["developed_groups_even"])
cov = C(coverage(e) for e in payable)
S["coverage"] = dict(cov)
S["coverage_necessity"] = dict(C(coverage(e) for e in payable if cat(e) == "C"))
S["coverage_last_class"] = [
    dict(entry=f"G{e['game']} d{e['first']}", model=e["model"], bank_houses=e["bank_houses"],
         houses_in_hotel_free_groups=e["houses_in_hotel_free_groups"], hotels_by_group=e["hotels_by_group"], built=e["built"],
         debt=e["debt"], ustar=e["ustar"], outcome=e["outcome"])
    for e in payable if coverage(e) == "one_hotel_per_group_recyclable_stock"]
S["hotel_states_payable"] = sum(1 for e in payable if e["hotels"])
S["hotel_states_all"] = sum(1 for e in eps if e["hotels"])

# selective financing, described without any search
A = [e for e in paid if cat(e) == "A"]
S["A_paid"] = len(A)
S["A_holding_buildings"] = sum(1 for e in A if e["salvage"] > 0)
S["A_sold_buildings"] = [f"G{e['game']} d{e['first']} {e['model']} sold {e['sale_total']}" for e in A if e["sale_total"] > 0]
S["A_mortgage_only_despite_buildings"] = sum(1 for e in A if e["salvage"] > 0 and e["sale_total"] == 0)
Bp = [e for e in paid if cat(e) == "B"]
S["B_paid_sold_everything"] = sum(1 for e in Bp if e["sale_total"] == e["salvage"])
S["B_paid_kept_some_buildings"] = sum(1 for e in Bp if e["sale_total"] < e["salvage"])
S["paid_cash_after_median"] = statistics.median(e["cash_after"] for e in paid)
S["paid_left_unmortgaged"] = sum(1 for e in paid if e["mortgage_total"] < e["mstar"])
S["paid_all_mortgaged_all_sold"] = sum(1 for e in paid if e["mortgage_total"] == e["mstar"] and e["sale_total"] == e["salvage"])
nec_paid = [e for e in paid if cat(e) == "C"]
S["necessity_paid_slack"] = {f"G{e['game']} d{e['first']}": dict(model=e["model"], slack=e["ustar"] - e["debt"], cash_after=e["cash_after"],
                                                               unused=e["ustar"] - e["debt"] - e["cash_after"], n_actions=len(e["actions"]))
                             for e in nec_paid}
S["necessity_paid_stopped_before_exhausting"] = sum(1 for e in nec_paid if e["ustar"] - e["debt"] - e["cash_after"] > 0)

# share arithmetic
S["shares"] = {"16/188": round(100 * 16 / 188, 1), "16/131": round(100 * 16 / 131, 1)}
write_json("finance_summary.json", S)
for key_, v in S.items():
    print(key_, "=", v)
