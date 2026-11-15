"""Debt-episode tabulations from stored first menus and applied actions.

Read-only. Produces data/finance_analysis.json and
data/necessary_first_texts.json (verbatim first-decision fields for the
sixteen necessary-collateral episodes, for reading, not for coding claims).

Definitions, all at the first stored decision of an episode:
  cash  = debtor cash in the delivered prompt
  L0    = mortgage value of every deed listed in mortgageable_space_keys
  S     = half the house cost per building level (hotel = five levels)
  U     = mortgage value of every unmortgaged owned deed absent from L0
  bound = cash + S + L0 + U  (the generous own-asset bound)
Tiers for payable debts:
  A  cash + L0 >= debt                (no sale needed)
  B  cash + L0 < debt <= cash + L0 + S (sales needed, no unlisted mortgage)
  N  cash + L0 + S < debt <= bound    (payment needs mortgages unlisted at entry)
  X  debt > bound                     (own assets cannot pay)
A bound at or above the debt is arithmetic, not a feasible legal route;
legal-route witnesses for the three unpaid payable debts are inherited.
"""
from __future__ import annotations

from collections import Counter
from statistics import median

import common as C

EPS = C.episodes()
rows = []
for e in EPS:
    k0 = C.did_index(e["decisions"][0])
    st = C.started(e["game"], k0)
    p = st["prompt_payload"]
    you = p["game_state"]["you"]
    sc = p["action_state"]["scenario"]
    listed = list(sc["options"]["mortgageable_space_keys"])
    owned = you["holdings"]["owned"]
    L0 = sum(C.mortgage_value(k) for k in listed)
    S = sum((5 if h["hotel"] else h["houses"]) * C.house_cost(C.group_of(h["space_key"])) // 2 for h in owned)
    unl = [h["space_key"] for h in owned if not h["mortgaged"] and h["space_key"] not in listed]
    U = sum(C.mortgage_value(k) for k in unl)
    cash, debt = you["cash"], e["debt"]
    assert sc["owed_amount"] == debt and cash == e["cash"]
    bound = cash + S + L0 + U
    assert bound == e["upper_bound"], (e["game"], e["first_decision"], bound, e["upper_bound"])
    tier = "A" if cash + L0 >= debt else "B" if cash + L0 + S >= debt else "N" if bound >= debt else "X"
    # applied actions in the episode
    acts = []
    sales_seen = 0
    for did in e["decisions"]:
        k = C.did_index(did)
        fa = C.resolved(e["game"], k)["final_action"]
        a = fa["action"]
        entry = {"decision": k, "action": a}
        if a == "sell_houses_or_hotel":
            sales_seen += 1
        if a == "mortgage_property":
            key = fa["args"]["space_key"]
            entry["deed"] = key
            entry["unlisted_at_entry"] = key not in listed
            if key not in listed:
                cur = C.started(e["game"], k)["prompt_payload"]["action_state"]["scenario"]["options"]["mortgageable_space_keys"]
                assert key in cur and sales_seen > 0
        acts.append(entry)
    rows.append({
        "game": e["game"], "player": e["player"], "model": e["model"].split(" ")[0], "first_decision": e["first_decision"],
        "turn": e["turn"], "reason": e["reason"], "cash": cash, "debt": debt, "L0": L0, "S": S, "U": U, "bound": bound,
        "tier": tier, "outcome": e["outcome"], "n_actions": len(e["actions"]), "actions": acts,
        "unlisted_mortgages_used": sum(1 for a in acts if a.get("unlisted_at_entry")),
        "sales": sum(1 for a in acts if a["action"] == "sell_houses_or_hotel"),
        "fallback_actions": e["fallback_actions"],
        "response_condition": C.resolved(e["game"], k0)["attempts"][-1].get("response_condition", "standard"),
    })

MODEL = {"claude-opus-5.5": "Opus", "gpt-6.1-sol": "Sol", "gemini-4-argon": "Gemini", "grok-4.7": "Grok"}
for r in rows:
    r["model"] = MODEL[r["model"]]

paid = [r for r in rows if r["outcome"] == "paid"]
elim = [r for r in rows if r["outcome"] != "paid"]
out = {"episodes": len(rows), "paid": len(paid), "eliminated": len(elim),
       "outcome_values": dict(Counter(r["outcome"] for r in rows))}
assert len(rows) == 188 and len(paid) == 128

# inherited classification of the four within-bound eliminations
WITNESS = {(12, 190): "payable (inherited witness)", (17, 234): "payable (inherited witness)",
           (12, 249): "payable (inherited witness)"}
within = [r for r in elim if r["tier"] != "X"]
out["eliminations_within_bound"] = [{k: r[k] for k in ("game", "model", "first_decision", "tier", "cash", "debt", "L0", "S", "U", "bound")}
                                    for r in within]
out["eliminations_above_bound"] = sum(r["tier"] == "X" for r in elim)
assert out["eliminations_above_bound"] == 56 and len(within) == 4
menu_restricted = [r for r in within if (r["game"], r["first_decision"]) not in WITNESS]
assert len(menu_restricted) == 1 and menu_restricted[0]["game"] == 7 and menu_restricted[0]["model"] == "Opus"
payable_unpaid = [r for r in within if (r["game"], r["first_decision"]) in WITNESS]

# tiers among payable debts (paid + three inherited payable declarations)
payable = paid + payable_unpaid
out["payable"] = len(payable)
out["tiers"] = {t: {"episodes": sum(r["tier"] == t for r in payable), "paid": sum(r["tier"] == t and r["outcome"] == "paid" for r in payable)}
                for t in ("A", "B", "N")}
out["tiers_all_188"] = dict(Counter(r["tier"] for r in rows))
out["menu_restricted"] = {k: menu_restricted[0][k] for k in ("game", "model", "first_decision", "tier", "cash", "debt", "bound")}
out["payable_unpaid"] = [{k: r[k] for k in ("game", "model", "first_decision", "tier", "cash", "debt", "L0", "S", "U")} for r in payable_unpaid]

# difficulty descriptors
out["paid_one_action"] = sum(r["n_actions"] == 1 for r in paid)
out["paid_multi_action"] = sum(r["n_actions"] > 1 for r in paid)
out["paid_action_counts"] = dict(sorted(Counter(r["n_actions"] for r in paid).items()))
out["paid_tier_A"] = sum(r["tier"] == "A" for r in paid)
out["paid_tier_A_or_B"] = sum(r["tier"] in "AB" for r in paid)
out["median_debt_to_bound_paid"] = round(median(r["debt"] / r["bound"] for r in paid), 3)
out["paid_with_fallback_action"] = sum(r["fallback_actions"] > 0 for r in paid)
out["paid_actions_total"] = dict(Counter(a["action"] for r in paid for a in r["actions"]))
out["paid_obligations_total"] = sum(r["debt"] for r in paid)

# nineteen uses of unlocked collateral versus sixteen necessary episodes
uses = [r for r in paid if r["unlisted_mortgages_used"] > 0]
nec = [r for r in rows if r["tier"] == "N"]
out["unlocked_uses"] = {"episodes": len(uses), "mortgage_actions": sum(r["unlisted_mortgages_used"] for r in uses),
                        "by_model": dict(Counter(r["model"] for r in uses))}
assert len(uses) == 19 and out["unlocked_uses"]["mortgage_actions"] == 33
nec_paid = [r for r in nec if r["outcome"] == "paid"]
assert len(nec) == 16 and len(nec_paid) == 14
assert all(r in uses for r in nec_paid)
optional = [r for r in uses if r["tier"] != "N"]
out["necessary"] = {"episodes": len(nec), "paid": len(nec_paid),
                    "by_model": {m: {"episodes": sum(r["model"] == m for r in nec),
                                     "paid": sum(r["model"] == m and r["outcome"] == "paid" for r in nec)} for m in C.MODELS},
                    "rows": [{k: r[k] for k in ("game", "model", "first_decision", "turn", "reason", "cash", "debt", "L0", "S", "U",
                                                "bound", "outcome", "n_actions", "sales", "unlisted_mortgages_used",
                                                "response_condition")} | {"shortfall_without_unlisted": r["debt"] - (r["cash"] + r["L0"] + r["S"])}
                             for r in nec]}
out["optional_uses"] = [{k: r[k] for k in ("game", "model", "first_decision", "tier", "unlisted_mortgages_used")} for r in optional]
assert len(optional) == 5

# action structure of the necessary payments (execution length vs prerequisite layers)
struct = []
for r in nec_paid:
    seq = [a["action"] for a in r["actions"]]
    first_unlisted = next(i for i, a in enumerate(r["actions"]) if a.get("unlisted_at_entry"))
    struct.append({"game": r["game"], "model": r["model"], "first_decision": r["first_decision"], "n_actions": len(seq),
                   "sales": seq.count("sell_houses_or_hotel"), "listed_mortgages": sum(1 for a in r["actions"] if a["action"] == "mortgage_property" and not a.get("unlisted_at_entry")),
                   "unlisted_mortgages": r["unlisted_mortgages_used"],
                   "sales_before_first_unlisted": sum(1 for a in r["actions"][:first_unlisted] if a["action"] == "sell_houses_or_hotel"),
                   "sequence": seq})
out["necessary_paid_structure"] = struct

# verbatim first-decision text for reading (the 16 necessary episodes)
texts = []
for r in nec:
    rec = C.resolved(r["game"], r["first_decision"])
    att = rec["attempts"][-1]
    msg = ((att.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {}) or {}
    texts.append({"game": r["game"], "decision": r["first_decision"], "model": r["model"], "outcome": r["outcome"],
                  "cash": r["cash"], "debt": r["debt"], "L0": r["L0"], "S": r["S"], "U": r["U"],
                  "selected_attempt_index": len(rec["attempts"]) - 1, "attempt_count": len(rec["attempts"]),
                  "applied_action": rec["final_action"]["action"],
                  "applied_private_note": rec["final_action"].get("private_thought"),
                  "public_message": rec["final_action"].get("public_message"),
                  "provider_reasoning": msg.get("reasoning"),
                  "assistant_content": att.get("assistant_content")})
C.write_json("necessary_first_texts.json", texts)

out["sources"] = C.sources_snapshot()
C.write_json("finance_analysis.json", out)
C.write_json("finance_rows.json", rows)
print({k: out[k] for k in ("episodes", "paid", "payable", "tiers", "paid_one_action", "paid_multi_action", "paid_tier_A",
                           "paid_tier_A_or_B", "median_debt_to_bound_paid", "unlocked_uses", "paid_with_fallback_action")})
print(out["necessary"]["by_model"])
for r in out["necessary"]["rows"]:
    print(r)
print(out["optional_uses"])
print(out["payable_unpaid"], out["menu_restricted"])
