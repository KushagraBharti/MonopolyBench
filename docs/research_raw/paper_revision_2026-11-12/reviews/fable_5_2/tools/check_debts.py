#!/usr/bin/env python3
"""Cross-review check of the debt claims, from stored records only.

Rebuilds liquidation episodes from raw ``LIQUIDATION_DECISION`` records,
recomputes first-menu resource sums, and examines the first applied action in
every episode.  It reads the inherited elimination classification for the
three payable bankruptcies and the menu-restricted case; those rest on earlier
engine-executed checks that this script does not and may not rerun.

No engine import, no replay, no model query.
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict

from ro_corpus import REVISION, board, load_all, write_json

B = board()["by_key"]


def first_menu_sums(g, k):
    st = g.started[k]
    sc = st["prompt_payload"]["action_state"]["scenario"]
    you = st["prompt_payload"]["game_state"]["you"]
    listed = list(sc["options"]["mortgageable_space_keys"])
    owned = you["holdings"]["owned"]
    m0 = sum(B[key]["mortgage"] for key in listed)
    salvage = 0
    for h in owned:
        levels = 5 if h["hotel"] else h["houses"]
        if levels:
            salvage += levels * B[h["space_key"]]["house_cost"] // 2
    unlisted = [h["space_key"] for h in owned if not h["mortgaged"] and h["space_key"] not in listed]
    m1 = sum(B[key]["mortgage"] for key in unlisted)
    return {
        "cash": you["cash"],
        "debt": sc["owed_amount"],
        "shortfall": sc["shortfall"],
        "listed_keys": listed,
        "listed_mortgage": m0,
        "sellable_keys": list(sc["options"]["sellable_building_space_keys"]),
        "salvage": salvage,
        "unlisted_keys": unlisted,
        "unlisted_mortgage": m1,
        "available_actions": list(st["prompt_payload"]["action_state"]["available_actions"]),
        "owed_to": sc.get("owed_to_player_id"),
        "reason": sc.get("reason"),
    }


def build_episodes():
    """An episode is a maximal run of consecutive liquidation decisions by one player."""
    eps = []
    for g in load_all().values():
        cur = None
        for k in range(g.n):
            st = g.started[k]
            if st["decision_type"] != "LIQUIDATION_DECISION":
                cur = None
                continue
            sc = st["prompt_payload"]["action_state"]["scenario"]
            sig = (st["player_id"], st["turn_index"], sc.get("owed_to_player_id"), sc.get("reason"))
            if cur is None or cur["sig"] != sig:
                cur = {"game": g.number, "block": g.block, "player": st["player_id"],
                       "model": g.model[st["player_id"]], "sig": sig, "decisions": []}
                eps.append(cur)
            cur["decisions"].append(k)
    for e in eps:
        g = load_all()[e["game"]]
        k0 = e["decisions"][0]
        e.update(first_menu_sums(g, k0))
        e["first_decision"] = k0
        rows = []
        for k in e["decisions"]:
            rs = g.resolved[k]
            rows.append({
                "decision": k,
                "action": rs["final_action"]["action"],
                "args": rs["final_action"].get("args"),
                "fallback_used": bool(rs.get("fallback_used")),
                "response_condition": (rs.get("sequence_meta") or {}).get("response_condition"),
            })
        e["action_rows"] = rows
        e["actions"] = [r["action"] for r in rows]
        e["first_action"] = rows[0]["action"]
        e["first_fallback"] = rows[0]["fallback_used"]
        e["first_condition"] = rows[0]["response_condition"]
        e["declared"] = "declare_bankruptcy" in e["actions"]
        # outcome from the debtor's status after the episode
        last = e["decisions"][-1]
        e["bankrupt_after"] = None
        for k in range(last + 1, g.n):
            hold = g.holdings(k)
            if e["player"] in hold:
                e["bankrupt_after"] = bool(hold[e["player"]]["bankrupt"])
                break
        if e["bankrupt_after"] is None:
            # game ended with this episode; the debtor lost if it is not the winner
            end = [ev for ev in g.events if ev["type"] == "GAME_ENDED"][0]
            e["bankrupt_after"] = end["payload"]["winner_player_id"] != e["player"]
        e["outcome"] = "eliminated" if e["bankrupt_after"] else "paid"
        e["reach_listed"] = e["cash"] + e["listed_mortgage"]
        e["reach_without_unlisted"] = e["reach_listed"] + e["salvage"]
        e["bound"] = e["reach_without_unlisted"] + e["unlisted_mortgage"]
        del e["sig"]
    return eps


def main():
    eps = build_episodes()
    out = {"episodes": len(eps)}
    key = {(e["game"], e["first_decision"]): e for e in eps}

    # --- reconcile with the two frozen ledgers (identity, debt, outcome, bound)
    ledger = json.loads((REVISION / "full_drafts/astra/data/liquidation_episodes.json").read_text())
    lkey = {(r["game"], r["first_decision"]): r for r in ledger}
    out["ledger_rows"] = len(ledger)
    out["identity_equal"] = sorted(key) == sorted(lkey)
    mism = []
    for kk, e in key.items():
        r = lkey.get(kk)
        if r is None:
            mism.append([kk, "missing in ledger"])
            continue
        led_outcome = "eliminated" if r["outcome"] == "bankrupt" else r["outcome"]
        if (r["debt"], r["cash"], r["upper_bound"], led_outcome, r["actions"]) != (
                e["debt"], e["cash"], e["bound"], e["outcome"], e["actions"]):
            mism.append([kk, (r["debt"], r["cash"], r["upper_bound"], r["outcome"]),
                         (e["debt"], e["cash"], e["bound"], e["outcome"])])
    out["ledger_mismatches"] = mism

    # --- inherited classification of the sixty eliminations
    elim = json.loads((REVISION / "full_drafts/sol/data/eliminations_inherited.json").read_text())
    out["inherited_elimination_rows"] = len(elim) if isinstance(elim, list) else "see keys"
    out["inherited_elimination_keys"] = sorted(elim[0].keys()) if isinstance(elim, list) else sorted(elim.keys())

    paid = [e for e in eps if e["outcome"] == "paid"]
    dead = [e for e in eps if e["outcome"] == "eliminated"]
    out["paid"] = len(paid)
    out["eliminated"] = len(dead)

    above = [e for e in dead if e["debt"] > e["bound"]]
    within = [e for e in dead if e["debt"] <= e["bound"]]
    out["eliminated_above_bound"] = len(above)
    out["eliminated_within_bound"] = [
        {"game": e["game"], "decision": e["first_decision"], "model": e["model"], "debt": e["debt"],
         "reach_listed": e["reach_listed"], "reach_without_unlisted": e["reach_without_unlisted"],
         "bound": e["bound"], "first_action": e["first_action"], "actions": e["actions"],
         "available_actions": e["available_actions"], "sellable_keys": e["sellable_keys"],
         "first_fallback": e["first_fallback"], "first_condition": e["first_condition"]}
        for e in within]

    # payable = paid + the three inherited payable bankruptcies (G12 d190, G12 d249, G17 d234)
    inherited_payable = {(12, 190), (12, 249), (17, 234)}
    restricted = {(7, 338)}
    out["within_bound_eliminations_match_inherited"] = (
        {(e["game"], e["first_decision"]) for e in within} == inherited_payable | restricted)
    payable = paid + [e for e in within if (e["game"], e["first_decision"]) in inherited_payable]
    out["payable"] = len(payable)

    def tier(e):
        if e["reach_listed"] >= e["debt"]:
            return "listed"
        if e["reach_without_unlisted"] >= e["debt"]:
            return "sales"
        return "unlisted"

    tiers = defaultdict(lambda: Counter())
    for e in payable:
        t = tier(e)
        tiers[t]["episodes"] += 1
        tiers[t]["paid"] += e["outcome"] == "paid"
        tiers[t]["declared_first"] += e["first_action"] == "declare_bankruptcy"
        tiers[t]["one_action_paid"] += (e["outcome"] == "paid" and len(e["actions"]) == 1)
    out["tiers_among_payable"] = {t: dict(c) for t, c in tiers.items()}

    # --- the first-action comparison (Fable draft: 50/56 against 3/131)
    fa = {}
    for name, group in (("above_bound", above), ("payable", payable)):
        c = Counter(e["first_action"] for e in group)
        fa[name] = {"n": len(group), "first_action": dict(c),
                    "declared_first": c["declare_bankruptcy"]}
    out["first_action"] = fa

    # What did the above-bound menus offer, and who chose?
    ab = []
    for e in above:
        ab.append({
            "game": e["game"], "decision": e["first_decision"], "model": e["model"],
            "debt": e["debt"], "cash": e["cash"], "bound": e["bound"],
            "ratio_bound_to_debt": round(e["bound"] / e["debt"], 3),
            "available_actions": e["available_actions"],
            "n_listed": len(e["listed_keys"]), "n_sellable": len(e["sellable_keys"]),
            "first_action": e["first_action"], "first_fallback": e["first_fallback"],
            "first_condition": e["first_condition"], "n_actions": len(e["actions"]),
        })
    out["above_bound_rows"] = ab
    only_bk = [r for r in ab if r["available_actions"] == ["declare_bankruptcy"]]
    has_alt = [r for r in ab if r["available_actions"] != ["declare_bankruptcy"]]
    out["above_bound_menu"] = {
        "only_bankruptcy_listed": len(only_bk),
        "alternative_listed": len(has_alt),
        "declared_first_when_alternative_listed": sum(r["first_action"] == "declare_bankruptcy" for r in has_alt),
        "declared_first_when_only_bankruptcy": sum(r["first_action"] == "declare_bankruptcy" for r in only_bk),
        "first_choice_by_fallback": sum(r["first_fallback"] for r in ab),
        "first_condition": dict(Counter(r["first_condition"] for r in ab)),
        "by_model_alt_listed": {
            m: {"n": sum(r["model"] == m for r in has_alt),
                "declared_first": sum(r["model"] == m and r["first_action"] == "declare_bankruptcy" for r in has_alt)}
            for m in ("Sol", "Gemini", "Opus", "Grok")},
        "continued_rows": [r for r in ab if r["first_action"] != "declare_bankruptcy"],
        "bound_to_debt_ratio_quartiles_alt_listed": (
            [round(x, 3) for x in statistics.quantiles([r["ratio_bound_to_debt"] for r in has_alt], n=4)]
            if len(has_alt) >= 4 else None),
        "alt_listed_within_10pct_of_debt": sum(r["ratio_bound_to_debt"] >= 0.9 for r in has_alt),
        "alt_listed_declared_first_within_10pct": sum(
            r["ratio_bound_to_debt"] >= 0.9 and r["first_action"] == "declare_bankruptcy" for r in has_alt),
    }
    pay_only_bk = [e for e in payable if e["available_actions"] == ["declare_bankruptcy"]]
    out["payable_menu_only_bankruptcy"] = len(pay_only_bk)

    # --- payment descriptors
    n_actions = Counter(len(e["actions"]) for e in paid)
    out["paid_action_counts"] = dict(sorted(n_actions.items()))
    out["paid_one_action"] = n_actions[1]
    out["paid_mortgage_actions"] = sum(a == "mortgage_property" for e in paid for a in e["actions"])
    out["paid_sale_actions"] = sum(a == "sell_houses_or_hotel" for e in paid for a in e["actions"])
    out["paid_other_actions"] = dict(Counter(a for e in paid for a in e["actions"]
                                             if a not in ("mortgage_property", "sell_houses_or_hotel")))
    out["paid_obligations_total"] = sum(e["debt"] for e in paid)
    out["paid_fallback_actions"] = sum(r["fallback_used"] for e in paid for r in e["action_rows"])
    out["median_debt_over_bound_paid"] = round(statistics.median(e["debt"] / e["bound"] for e in paid), 4)
    out["median_debt_over_bound_payable"] = round(statistics.median(e["debt"] / e["bound"] for e in payable), 4)

    # --- the sixteen and the nineteen
    sixteen = sorted((e for e in payable if tier(e) == "unlisted"), key=lambda e: (e["game"], e["first_decision"]))
    rows16 = []
    for e in sixteen:
        g = load_all()[e["game"]]
        used = []
        sale_seen = False
        first_released_after_sale = None
        for r in e["action_rows"]:
            if r["action"] == "sell_houses_or_hotel":
                sale_seen = True
            if r["action"] == "mortgage_property":
                sk = (r["args"] or {}).get("space_key")
                if sk in e["unlisted_keys"]:
                    used.append(sk)
                    if first_released_after_sale is None:
                        first_released_after_sale = sale_seen
        k0 = e["first_decision"]
        rs = g.resolved[k0]
        note = rs["final_action"].get("private_thought")
        rows16.append({
            "game": e["game"], "decision": k0, "model": e["model"], "block": e["block"],
            "debt": e["debt"], "cash": e["cash"], "listed_mortgage": e["listed_mortgage"],
            "salvage": e["salvage"], "unlisted_mortgage": e["unlisted_mortgage"],
            "reach_without_unlisted": e["reach_without_unlisted"], "bound": e["bound"],
            "gap_only_unlisted_can_close": e["debt"] - e["reach_without_unlisted"],
            "outcome": e["outcome"], "actions": e["actions"], "n_actions": len(e["actions"]),
            "first_action": e["first_action"], "released_mortgages_used": used,
            "sale_before_first_released_mortgage": first_released_after_sale,
            "first_condition": e["first_condition"],
            "channel": "applied private note" if note else "provider-returned text",
            "first_note": note, "first_provider_text": g.provider_reasoning(k0),
        })
    out["sixteen"] = rows16
    out["sixteen_summary"] = {
        "n": len(rows16),
        "paid": sum(r["outcome"] == "paid" for r in rows16),
        "by_model": {m: [sum(r["model"] == m and r["outcome"] == "paid" for r in rows16),
                         sum(r["model"] == m for r in rows16)] for m in ("Sol", "Gemini", "Opus", "Grok")},
        "by_block": {b: [sum(r["block"] == b and r["outcome"] == "paid" for r in rows16),
                         sum(r["block"] == b for r in rows16)] for b in range(1, 6)},
        "games": sorted({r["game"] for r in rows16}),
        "channel_paid": dict(Counter(r["channel"] for r in rows16 if r["outcome"] == "paid")),
        "channel_failed": dict(Counter(r["channel"] for r in rows16 if r["outcome"] != "paid")),
        "paid_using_released_mortgage": sum(bool(r["released_mortgages_used"]) for r in rows16 if r["outcome"] == "paid"),
        "failed_first_action": [r["first_action"] for r in rows16 if r["outcome"] != "paid"],
        "paid_first_action": dict(Counter(r["first_action"] for r in rows16 if r["outcome"] == "paid")),
        "gap_range": [min(r["gap_only_unlisted_can_close"] for r in rows16),
                      max(r["gap_only_unlisted_can_close"] for r in rows16)],
        "paid_action_range": [min(r["n_actions"] for r in rows16 if r["outcome"] == "paid"),
                              max(r["n_actions"] for r in rows16 if r["outcome"] == "paid")],
    }
    uses = []
    for e in paid:
        used = [(r["args"] or {}).get("space_key") for r in e["action_rows"]
                if r["action"] == "mortgage_property" and (r["args"] or {}).get("space_key") in e["unlisted_keys"]]
        if used:
            uses.append({"game": e["game"], "decision": e["first_decision"], "model": e["model"],
                         "tier": tier(e), "released_used": used})
    out["released_collateral_uses"] = {
        "episodes": len(uses), "mortgages": sum(len(u["released_used"]) for u in uses),
        "necessary": sum(u["tier"] == "unlisted" for u in uses),
        "optional": [u for u in uses if u["tier"] != "unlisted"],
    }

    # --- how close to the boundary were the two classes?
    def band(x):
        for lo, hi, name in ((0, 0.5, "under 0.50"), (0.5, 0.75, "0.50-0.75"), (0.75, 0.9, "0.75-0.90"), (0.9, 9, "0.90-1.00")):
            if lo <= x < hi:
                return name
    margin = {"above_bound_alternative_listed_by_bound_over_debt": {}, "payable_by_debt_over_bound": {}}
    for r in has_alt:
        c = margin["above_bound_alternative_listed_by_bound_over_debt"].setdefault(
            band(r["ratio_bound_to_debt"]), {"n": 0, "declared_first": 0})
        c["n"] += 1
        c["declared_first"] += r["first_action"] == "declare_bankruptcy"
    for e in payable:
        c = margin["payable_by_debt_over_bound"].setdefault(
            band(e["debt"] / e["bound"]), {"n": 0, "declared_first": 0, "paid": 0})
        c["n"] += 1
        c["declared_first"] += e["first_action"] == "declare_bankruptcy"
        c["paid"] += e["outcome"] == "paid"
    out["margin"] = margin
    out["payable_within_10pct_rows"] = [
        {"game": e["game"], "decision": e["first_decision"], "model": e["model"], "debt": e["debt"],
         "bound": e["bound"], "tier": tier(e), "first_action": e["first_action"], "outcome": e["outcome"]}
        for e in payable if e["debt"] / e["bound"] >= 0.9]
    out["all_rows"] = [
        {"game": e["game"], "decision": e["first_decision"], "model": e["model"], "block": e["block"],
         "debt": e["debt"], "cash": e["cash"], "listed_mortgage": e["listed_mortgage"], "salvage": e["salvage"],
         "unlisted_mortgage": e["unlisted_mortgage"], "bound": e["bound"], "outcome": e["outcome"],
         "first_action": e["first_action"], "n_actions": len(e["actions"]),
         "available_actions": e["available_actions"]}
        for e in eps]

    write_json("check_debts.json", out)
    brief = {k: v for k, v in out.items() if k not in ("above_bound_rows", "sixteen", "all_rows")}
    print(json.dumps(brief, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
