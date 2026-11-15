"""All debt episodes, including the ones that were paid.

A debt episode is a maximal run of consecutive LIQUIDATION_DECISION prompts to
one player for one debt (same turn, amount, reason and creditor).  It ends in
payment (play continues) or in elimination (a BANKRUPTCY cash event before the
next decision request).  The generous own-asset bound U at the first menu is
fresh arithmetic on the delivered prompt state.  Feasibility for eliminations
is *inherited* from the retained certificate ledger (payment witnesses and the
G7 restricted search were engine-executed in earlier work, not here).
"""
from __future__ import annotations

import collections
import json
import statistics as S

from corpus import MODELS, REPO, board, load_all, sha256_file, write_json

RETAINED = REPO / "docs/research_raw/paper_rewrite_2026-11-10/data/t06_eliminations.json"


def bound(B, you: dict) -> dict:
    cash = you["cash"]
    salv = 0
    mort = 0
    for h in you["holdings"]["owned"]:
        row = B["by_key"][h["space_key"]]
        lvl = 5 if h["hotel"] else h["houses"]
        if lvl:
            salv += lvl * row["house_cost"] // 2
        if not h["mortgaged"]:
            mort += row["mortgage"]
    return {"cash": cash, "salvage": salv, "mortgage": mort, "U": cash + salv + mort}


def build() -> list[dict]:
    B = board()
    eps = []
    for g in load_all().values():
        # index of event position for each decision response
        resp_pos = {}
        for i, e in enumerate(g.events):
            if e["type"] == "LLM_DECISION_RESPONSE":
                resp_pos[g.dec_index(e["payload"]["decision_id"])] = i
        cur = None
        for k in range(g.n_decisions):
            st = g.started[k]
            if st["decision_type"] != "LIQUIDATION_DECISION":
                continue
            sc = st["prompt_payload"]["action_state"]["scenario"]
            key = (st["player_id"], st["turn_index"], sc["owed_amount"], sc.get("reason"), sc.get("owed_to_player_id"))
            if cur and cur["_key"] == key and cur["decisions"][-1] == k - 1:
                cur["decisions"].append(k)
            else:
                you = st["prompt_payload"]["game_state"]["you"]
                b = bound(B, you)
                cur = {
                    "_key": key,
                    "game": g.number,
                    "block": g.block,
                    "player": st["player_id"],
                    "model": g.model[st["player_id"]],
                    "turn": st["turn_index"],
                    "first_decision": k,
                    "decisions": [k],
                    "debt": sc["owed_amount"],
                    "reason": sc.get("reason"),
                    "creditor": sc.get("owed_to_player_id"),
                    "shortfall_first": sc["shortfall"],
                    "cash_first": b["cash"],
                    "salvage_first": b["salvage"],
                    "mortgage_first": b["mortgage"],
                    "bound_U": b["U"],
                    "menu_mortgage_first": sum(B["by_key"][x]["mortgage"] for x in sc["options"]["mortgageable_space_keys"]),
                    "menu_has_sale_first": bool(sc["options"]["sellable_building_space_keys"]),
                    "winner": st["player_id"] == g.winner_pid,
                }
                eps.append(cur)
        for ep in [e for e in eps if e["game"] == g.number]:
            acts = [g.resolved[k]["final_action"]["action"] for k in ep["decisions"]]
            ep["actions"] = acts
            ep["n_mortgages"] = acts.count("mortgage_property")
            ep["n_sales"] = acts.count("sell_houses_or_hotel")
            ep["fallback_any"] = any(g.resolved[k]["fallback_used"] for k in ep["decisions"])
            last = ep["decisions"][-1]
            i = resp_pos[last] + 1
            bankrupt = False
            while i < len(g.events) and g.events[i]["type"] != "LLM_DECISION_REQUESTED":
                e = g.events[i]
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY" and e["payload"]["player_id"] == ep["player"]:
                    bankrupt = True
                i += 1
            ep["outcome"] = "eliminated" if bankrupt else "paid"
            ep["termination"] = None
            if bankrupt:
                ep["termination"] = "declared" if acts[-1] == "declare_bankruptcy" else "automatic"
            if not bankrupt:
                # cash after the episode: next prompt state for anyone
                nxt = last + 1
                cash_after = None
                if nxt < g.n_decisions:
                    cash_after = g.state_before(nxt)["players"][ep["player"]]["cash"]
                ep["cash_after_payment"] = cash_after
            ep.pop("_key", None)
    return eps


def main() -> None:
    eps = build()
    old = json.loads(RETAINED.read_text())
    old_by = {(r["game"], int(r["decision"].split("-")[1])): r for r in old}
    elim = [e for e in eps if e["outcome"] == "eliminated"]
    paid = [e for e in eps if e["outcome"] == "paid"]
    assert len(elim) == 60, len(elim)
    # reconcile eliminations with the retained ledger on last decision, debt, cash and bound
    mism = []
    for e in elim:
        o = old_by.get((e["game"], e["decisions"][-1]))
        if o is None:
            mism.append(["missing", e["game"], e["decisions"]])
            continue
        e["inherited_class"] = (
            "payable_witness" if o["avoidable"] else ("below_bound" if o["full"] < o["owed"] else "menu_blocked")
        )
        e["retained_bound_at_last_decision"] = o["full"]
        e["retained_cash_at_last_decision"] = o["cash"]
        if o["owed"] != e["debt"]:
            mism.append(["debt", e["game"], e["decisions"][-1], o["owed"], e["debt"]])
        if o["elimination"] != e["termination"]:
            mism.append(["termination", e["game"], e["decisions"][-1], o["elimination"], e["termination"]])
        # the generous bound is invariant to mortgages and loses nothing to sales except rounding,
        # so the first-menu bound must be >= the last-menu bound
        if e["bound_U"] < o["full"]:
            mism.append(["bound_order", e["game"], e["decisions"][-1], e["bound_U"], o["full"]])
    for e in paid:
        e["inherited_class"] = "paid"
    cls = collections.Counter(e["inherited_class"] for e in eps)
    by_model = {}
    for m in MODELS:
        xs = [e for e in eps if e["model"] == m]
        by_model[m] = {
            "episodes": len(xs),
            "paid": sum(e["outcome"] == "paid" for e in xs),
            "eliminated": sum(e["outcome"] == "eliminated" for e in xs),
            "payable_but_eliminated": sum(e["inherited_class"] == "payable_witness" for e in xs),
        }
    feasible = cls["paid"] + cls["payable_witness"]
    # fresh arithmetic check of the bound for eliminations at first menu
    fresh_below = sum(1 for e in elim if e["bound_U"] < e["debt"])
    paid_margin = [e["bound_U"] - e["debt"] for e in paid]
    summary = {
        "retained_sha256": sha256_file(RETAINED),
        "episodes": len(eps),
        "liquidation_decisions": sum(len(e["decisions"]) for e in eps),
        "paid": len(paid),
        "eliminated": len(elim),
        "classes": dict(cls),
        "feasible_episodes": feasible,
        "payable_but_eliminated_share_of_feasible": round(cls["payable_witness"] / feasible, 4),
        "by_model": by_model,
        "reconciliation_mismatches": mism,
        "eliminations_first_menu_bound_below_debt_fresh": fresh_below,
        "paid_bound_minus_debt": {
            "min": min(paid_margin),
            "median": S.median(paid_margin),
            "under_100": sum(1 for x in paid_margin if x < 100),
            "under_250": sum(1 for x in paid_margin if x < 250),
        },
        "paid_composition": {
            "mortgage_only": sum(1 for e in paid if e["n_mortgages"] and not e["n_sales"]),
            "sales_only": sum(1 for e in paid if e["n_sales"] and not e["n_mortgages"]),
            "both": sum(1 for e in paid if e["n_sales"] and e["n_mortgages"]),
        },
        "paid_sale_when_menu_mortgages_cover_shortfall": sum(
            1 for e in paid if e["n_sales"] and e["menu_mortgage_first"] >= e["shortfall_first"]
        ),
        "paid_with_sale": sum(1 for e in paid if e["n_sales"]),
        "eliminated_after_some_liquidation": sum(1 for e in elim if len(e["decisions"]) > 1),
        "eliminated_after_building_sale": sum(1 for e in elim if e["n_sales"]),
        "reasons": dict(collections.Counter(e["reason"] for e in eps)),
        "reason_by_outcome": {f"{a}|{b}": n for (a, b), n in collections.Counter((e["reason"], e["outcome"]) for e in eps).items()},
        "per_game": {
            n: [sum(1 for e in eps if e["game"] == n and e["outcome"] == "paid"), sum(1 for e in eps if e["game"] == n)]
            for n in range(1, 21)
        },
        "per_block_paid_of_feasible": {
            b: [
                sum(1 for e in eps if e["block"] == b and e["inherited_class"] == "paid"),
                sum(1 for e in eps if e["block"] == b and e["inherited_class"] in ("paid", "payable_witness")),
            ]
            for b in range(1, 6)
        },
    }
    write_json("a4_debt_episodes.json", eps)
    write_json("a4_debt_summary.json", summary)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
