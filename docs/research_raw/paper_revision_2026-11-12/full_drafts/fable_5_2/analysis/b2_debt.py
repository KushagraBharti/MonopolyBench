"""Debt census: every liquidation episode, partitioned by what the first menu could raise.

A debt episode is a maximal run of consecutive LIQUIDATION_DECISION prompts to
one player for one debt.  It ends in payment or elimination.  All arithmetic
uses the state and menu delivered at the first decision plus applied actions.
No engine import, no game, no model call.

Tiers at the first menu (C cash, M0 mortgage value of deeds the menu lists,
S salvage of every building at half cost, M1 mortgage value of unmortgaged
deeds the menu does not list):
  listed      C + M0            >= debt   payable without selling a building
  sales       C + M0 + S        >= debt   needs building sales, no unlisted deed
  unlisted    C + M0 + S + M1   >= debt   cannot be paid without mortgages that
                                          appear only after buildings are sold
  above       C + M0 + S + M1   <  debt   exceeds every own asset
The sums are upper bounds on what each resource class can raise.  A sufficient
sum does not show that a legal payment sequence exists; that comes from the
observed payment or from earlier engine-executed witnesses (inherited).

Outputs: data/b2_debt_episodes.json, data/b2_debt.json, data/b2_first_texts.json
"""
from __future__ import annotations

import collections
import json
import statistics as S

from corpus import MODELS, REPO, board, load_all, sha256_file, write_json

WITNESS = REPO / "docs/research_raw/paper_rewrite_2026-11-10/data/t06_eliminations.json"
RETAINED = REPO / "docs/research_raw/paper_revision_2026-11-11/integrated/data/liquidation_episodes.json"


def first_menu(B, st) -> dict:
    you = st["prompt_payload"]["game_state"]["you"]
    sc = st["prompt_payload"]["action_state"]["scenario"]
    listed = set(sc["options"]["mortgageable_space_keys"])
    owned = you["holdings"]["owned"]
    built_groups = {B["by_key"][h["space_key"]]["group"] for h in owned if h["houses"] or h["hotel"]}
    salv = sum((5 if h["hotel"] else h["houses"]) * B["by_key"][h["space_key"]]["house_cost"] // 2 for h in owned if h["houses"] or h["hotel"])
    unlisted = [h["space_key"] for h in owned if not h["mortgaged"] and h["space_key"] not in listed]
    # every unmortgaged deed missing from the mortgage menu sits in a group that still has buildings
    assert all(B["by_key"][x]["group"] in built_groups for x in unlisted), unlisted
    assert all(not next(h for h in owned if h["space_key"] == x)["mortgaged"] for x in listed)
    return {
        "cash": you["cash"],
        "listed_keys": sorted(listed), "listed_mortgage": sum(B["by_key"][x]["mortgage"] for x in listed),
        "salvage": salv,
        "unlisted_keys": sorted(unlisted), "unlisted_mortgage": sum(B["by_key"][x]["mortgage"] for x in unlisted),
        "menu_has_sale": bool(sc["options"]["sellable_building_space_keys"]),
        "building_levels": sum((5 if h["hotel"] else h["houses"]) for h in owned),
        "deeds": len(owned),
    }


def tier(m: dict, debt: int) -> str:
    c = m["cash"]
    if c + m["listed_mortgage"] >= debt:
        return "listed"
    if c + m["listed_mortgage"] + m["salvage"] >= debt:
        return "sales"
    if c + m["listed_mortgage"] + m["salvage"] + m["unlisted_mortgage"] >= debt:
        return "unlisted"
    return "above"


def build() -> list[dict]:
    B = board()
    eps = []
    for g in load_all().values():
        resp_pos = {}
        for i, e in enumerate(g.events):
            if e["type"] == "LLM_DECISION_RESPONSE":
                resp_pos[g.dec_index(e["payload"]["decision_id"])] = i
        cur = None
        mine = []
        for k in range(g.n_decisions):
            st = g.started[k]
            if st["decision_type"] != "LIQUIDATION_DECISION":
                continue
            sc = st["prompt_payload"]["action_state"]["scenario"]
            key = (st["player_id"], st["turn_index"], sc["owed_amount"], sc.get("reason"), sc.get("owed_to_player_id"))
            if cur and cur["_key"] == key and cur["decisions"][-1] == k - 1:
                cur["decisions"].append(k)
                continue
            m = first_menu(B, st)
            cur = {"_key": key, "game": g.number, "block": g.block, "player": st["player_id"], "model": g.model[st["player_id"]],
                   "turn": st["turn_index"], "first_decision": k, "decisions": [k], "debt": sc["owed_amount"],
                   "reason": sc.get("reason"), "creditor": sc.get("owed_to_player_id"),
                   "creditor_model": g.model.get(sc.get("owed_to_player_id")),
                   "players_remaining": sum(1 for p in [st["prompt_payload"]["game_state"]["you"]] + st["prompt_payload"]["game_state"]["others"] if not p["bankrupt"]),
                   "winner_is_creditor": sc.get("owed_to_player_id") == g.winner_pid,
                   **m, "bound": m["cash"] + m["listed_mortgage"] + m["salvage"] + m["unlisted_mortgage"],
                   "tier": tier(m, sc["owed_amount"])}
            mine.append(cur)
        for ep in mine:
            acts = []
            for k in ep["decisions"]:
                fa = g.resolved[k]["final_action"]
                acts.append({"decision": k, "action": fa["action"], "args": fa.get("args") or {},
                             "response_condition": g.resolved[k]["sequence_meta"].get("response_condition"),
                             "fallback": g.resolved[k]["fallback_used"]})
            ep["actions"] = [a["action"] for a in acts]
            ep["action_rows"] = acts
            ep["n_actions"] = len(acts)
            ep["first_action"] = acts[0]["action"]
            ep["fallback_any"] = any(a["fallback"] for a in acts)
            i = resp_pos[ep["decisions"][-1]] + 1
            bankrupt = False
            while i < len(g.events) and g.events[i]["type"] != "LLM_DECISION_REQUESTED":
                e = g.events[i]
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY" and e["payload"]["player_id"] == ep["player"]:
                    bankrupt = True
                i += 1
            ep["outcome"] = "eliminated" if bankrupt else "paid"
            ep["termination"] = ("declared" if ep["actions"][-1] == "declare_bankruptcy" else "automatic") if bankrupt else None
            # mortgages on deeds that the first menu did not list
            used, sales_so_far = [], 0
            for a in acts:
                if a["action"] == "sell_houses_or_hotel":
                    sales_so_far += 1
                if a["action"] == "mortgage_property" and a["args"]["space_key"] in ep["unlisted_keys"]:
                    assert sales_so_far > 0
                    menu_now = g.started[a["decision"]]["prompt_payload"]["action_state"]["scenario"]["options"]["mortgageable_space_keys"]
                    assert a["args"]["space_key"] in menu_now
                    used.append(a["args"]["space_key"])
            ep["unlisted_mortgages_used"] = used
            ep["n_sales"] = ep["actions"].count("sell_houses_or_hotel")
            ep["n_mortgages"] = ep["actions"].count("mortgage_property")
            if not bankrupt:
                nxt = ep["decisions"][-1] + 1
                ep["cash_after_payment"] = g.state_before(nxt)["players"][ep["player"]]["cash"] if nxt < g.n_decisions else None
            ep.pop("_key")
        eps.extend(mine)
    return eps


def first_texts(eps: list[dict]) -> list[dict]:
    """Stored text at the first decision of each necessary-collateral episode."""
    G = load_all()
    out = []
    for ep in eps:
        if ep["tier"] != "unlisted":
            continue
        g = G[ep["game"]]
        k = ep["first_decision"]
        r = g.resolved[k]
        sel = None
        for i, a in enumerate(r["attempts"]):
            if a.get("outcome") == "valid":
                sel = i
        att = r["attempts"][sel]
        msg = ((att.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {})
        out.append({
            "game": ep["game"], "decision": k, "model": ep["model"], "outcome": ep["outcome"], "debt": ep["debt"],
            "cash": ep["cash"], "listed_mortgage": ep["listed_mortgage"], "salvage": ep["salvage"],
            "unlisted_mortgage": ep["unlisted_mortgage"], "unlisted_keys": ep["unlisted_keys"], "listed_keys": ep["listed_keys"],
            "response_condition": r["sequence_meta"].get("response_condition"), "selected_attempt": sel,
            "applied_action": r["final_action"]["action"], "applied_args": r["final_action"].get("args"),
            "private_note": r["final_action"].get("private_thought"),
            "public_message": r["final_action"].get("public_message"),
            "provider_reasoning": msg.get("reasoning"),
            "assistant_content": att.get("assistant_content"),
            "actions": ep["actions"], "cash_after_payment": ep.get("cash_after_payment"),
            "source_line": g.decision_line[k],
        })
    return out


def main() -> None:
    eps = build()
    assert len(eps) == 188
    paid = [e for e in eps if e["outcome"] == "paid"]
    elim = [e for e in eps if e["outcome"] == "eliminated"]
    assert len(paid) == 128 and len(elim) == 60

    # inherited feasibility witnesses for the eliminations (engine-executed earlier, not here)
    wit = {(r["game"], int(r["decision"].split("-")[1])): r for r in json.loads(WITNESS.read_text())}
    for e in elim:
        o = wit[(e["game"], e["decisions"][-1])]
        assert o["owed"] == e["debt"]
        e["inherited_class"] = "payable_witness" if o["avoidable"] else ("above_bound" if o["full"] < o["owed"] else "menu_restricted")
        e["inherited_witness_steps"] = o.get("steps") if o["avoidable"] else None
    for e in paid:
        e["inherited_class"] = None

    def klass(e):
        if e["outcome"] == "paid":
            return "paid"
        return {"payable_witness": "payable_declared", "above_bound": "above_bound", "menu_restricted": "menu_restricted"}[e["inherited_class"]]

    for e in eps:
        e["class"] = klass(e)
    # the fresh first-menu bound agrees with the inherited classification
    assert all((e["tier"] == "above") == (e["class"] == "above_bound") for e in eps)
    cls = collections.Counter(e["class"] for e in eps)
    assert cls == {"paid": 128, "above_bound": 56, "menu_restricted": 1, "payable_declared": 3}, cls

    # reconcile episode identities with the integrated copy
    old = json.loads(RETAINED.read_text())
    assert len(old) == 188
    assert {(o["game"], o["first_decision"]) for o in old} == {(e["game"], e["first_decision"]) for e in eps}
    ob = {(o["game"], o["first_decision"]): o for o in old}
    assert all((ob[(e["game"], e["first_decision"])]["outcome"] == "paid") == (e["outcome"] == "paid") for e in eps)
    assert all(ob[(e["game"], e["first_decision"])]["debt"] == e["debt"] and ob[(e["game"], e["first_decision"])]["actions"] == e["actions"] for e in eps)
    bound_equal = sum(1 for e in eps if ob[(e["game"], e["first_decision"])].get("upper_bound") == e["bound"])

    payable = [e for e in eps if e["class"] in ("paid", "payable_declared")]
    assert len(payable) == 131
    tiers = {}
    for t in ("listed", "sales", "unlisted"):
        xs = [e for e in payable if e["tier"] == t]
        tiers[t] = {"episodes": len(xs), "paid": sum(e["outcome"] == "paid" for e in xs),
                    "declared": sum(e["outcome"] == "eliminated" for e in xs),
                    "single_action_payments": sum(1 for e in xs if e["outcome"] == "paid" and e["n_actions"] == 1),
                    "median_actions_when_paid": S.median([e["n_actions"] for e in xs if e["outcome"] == "paid"]),
                    "max_actions_when_paid": max(e["n_actions"] for e in xs if e["outcome"] == "paid"),
                    "median_debt": S.median(e["debt"] for e in xs),
                    "by_model": {m: [sum(1 for e in xs if e["model"] == m and e["outcome"] == "paid"), sum(1 for e in xs if e["model"] == m)] for m in MODELS},
                    "by_block": {b: [sum(1 for e in xs if e["block"] == b and e["outcome"] == "paid"), sum(1 for e in xs if e["block"] == b)] for b in range(1, 6)},
                    "games": len({e["game"] for e in xs})}
    assert [tiers[t]["episodes"] for t in ("listed", "sales", "unlisted")] == [62, 53, 16]
    assert [tiers[t]["paid"] for t in ("listed", "sales", "unlisted")] == [62, 52, 14]

    used = [e for e in paid if e["unlisted_mortgages_used"]]
    assert len(used) == 19 and sum(len(e["unlisted_mortgages_used"]) for e in used) == 33
    nec = [e for e in eps if e["tier"] == "unlisted" and e["class"] in ("paid", "payable_declared")]
    assert all(e["unlisted_mortgages_used"] for e in nec if e["outcome"] == "paid")
    optional = [e for e in used if e["tier"] != "unlisted"]

    # the decision at the first menu: quit or continue
    first = collections.Counter((("payable" if e["class"] in ("paid", "payable_declared") else e["class"]),
                                 "declare" if e["first_action"] == "declare_bankruptcy" else "continue") for e in eps)
    above = [e for e in eps if e["class"] == "above_bound"]

    nec_rows = []
    for e in sorted(nec, key=lambda e: (e["game"], e["first_decision"])):
        short_without = e["debt"] - (e["cash"] + e["listed_mortgage"] + e["salvage"])
        nec_rows.append({
            "game": e["game"], "decision": e["first_decision"], "model": e["model"], "block": e["block"], "turn": e["turn"],
            "debt": e["debt"], "cash": e["cash"], "listed_mortgage": e["listed_mortgage"], "salvage": e["salvage"],
            "unlisted_mortgage": e["unlisted_mortgage"], "shortfall_without_unlisted": short_without,
            "margin_with_unlisted": e["bound"] - e["debt"],
            "outcome": e["outcome"], "first_action": e["first_action"], "n_actions": e["n_actions"],
            "n_sales": e["n_sales"], "n_mortgages": e["n_mortgages"], "unlisted_used": len(e["unlisted_mortgages_used"]),
            "cash_after_payment": e.get("cash_after_payment"),
            "response_condition_first": e["action_rows"][0]["response_condition"],
            "creditor_model": e["creditor_model"], "reason": e["reason"],
        })

    summary = {
        "episodes": len(eps), "liquidation_decisions": sum(e["n_actions"] for e in eps),
        "classes": dict(cls), "payable": len(payable),
        "tiers_among_payable": tiers,
        "paid_actions": {"mortgages": sum(e["n_mortgages"] for e in paid), "sales": sum(e["n_sales"] for e in paid),
                         "single_action": sum(1 for e in paid if e["n_actions"] == 1),
                         "multi_action": sum(1 for e in paid if e["n_actions"] > 1),
                         "max_actions": max(e["n_actions"] for e in paid),
                         "debt_total": sum(e["debt"] for e in paid),
                         "fallback_in_paid": sum(e["fallback_any"] for e in paid),
                         "median_debt_over_bound": round(S.median(e["debt"] / e["bound"] for e in paid), 3)},
        "by_model": {m: {"episodes": sum(e["model"] == m for e in eps), "paid": sum(e["model"] == m for e in paid),
                         "multi_action": sum(1 for e in paid if e["model"] == m and e["n_actions"] > 1),
                         "used_unlisted": sum(e["model"] == m for e in used),
                         "necessary": sum(e["model"] == m for e in nec),
                         "necessary_paid": sum(1 for e in nec if e["model"] == m and e["outcome"] == "paid")} for m in MODELS},
        "unlisted_use": {"episodes": len(used), "mortgages": sum(len(e["unlisted_mortgages_used"]) for e in used),
                         "necessary": len([e for e in used if e["tier"] == "unlisted"]), "optional": len(optional),
                         "optional_rows": [[e["game"], e["first_decision"], e["model"], e["tier"]] for e in optional],
                         "by_model": dict(collections.Counter(e["model"] for e in used))},
        "necessary": {"episodes": len(nec), "paid": sum(e["outcome"] == "paid" for e in nec),
                      "games": len({e["game"] for e in nec}), "blocks_with_cases": len({e["block"] for e in nec}),
                      "leave_one_block_out": [[sum(1 for e in nec if e["block"] != b and e["outcome"] == "paid"), sum(1 for e in nec if e["block"] != b)] for b in range(1, 6)],
                      "first_action": dict(collections.Counter(e["first_action"] for e in nec)),
                      "first_action_paid": dict(collections.Counter(e["first_action"] for e in nec if e["outcome"] == "paid")),
                      "median_actions_paid": S.median(e["n_actions"] for e in nec if e["outcome"] == "paid"),
                      "median_shortfall_without_unlisted": S.median(r["shortfall_without_unlisted"] for r in nec_rows),
                      "median_cash_after_payment": S.median(r["cash_after_payment"] for r in nec_rows if r["outcome"] == "paid"),
                      "rows": nec_rows},
        "first_menu_decision": {f"{a}|{b}": n for (a, b), n in sorted(first.items())},
        "above_bound": {"episodes": len(above), "declared_at_first_menu": sum(e["first_action"] == "declare_bankruptcy" for e in above),
                        "liquidated_before_elimination": sum(1 for e in above if e["n_actions"] > 1),
                        "termination": dict(collections.Counter(e["termination"] for e in above))},
        "payable_declared_rows": [[e["game"], e["first_decision"], e["model"], e["tier"], e["debt"], e["first_action"]] for e in eps if e["class"] == "payable_declared"],
        "menu_restricted_rows": [[e["game"], e["first_decision"], e["model"], e["debt"], e["bound"], e["menu_has_sale"]] for e in eps if e["class"] == "menu_restricted"],
        "eliminations": {"total": len(elim), "nonterminal": sum(1 for e in elim if e["players_remaining"] > 2),
                         "to_player_creditor": sum(1 for e in elim if e["creditor"]),
                         "nonterminal_to_eventual_winner": sum(1 for e in elim if e["players_remaining"] > 2 and e["winner_is_creditor"])},
        "reconciliation": {"retained": str(RETAINED.relative_to(REPO)), "retained_sha256": sha256_file(RETAINED),
                           "episode_identities_equal": True, "outcomes_equal": True, "bounds_equal": bound_equal,
                           "witness_ledger": str(WITNESS.relative_to(REPO)), "witness_sha256": sha256_file(WITNESS)},
    }
    write_json("b2_debt_episodes.json", eps)
    write_json("b2_debt.json", summary)
    write_json("b2_first_texts.json", first_texts(eps))
    brief = dict(summary)
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
