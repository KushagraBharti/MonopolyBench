"""Read the canonical menus behind the nine 'never legal in window' groups.

Question under review: does "no observed menu in the first management window
listed construction" support "the group could not be built on" (Fable draft)
or "access was unavailable" (Sol/Astra wording)?

For each window this reads the delivered decision payloads (existing records)
and reports cash, which group deeds were mortgaged, whether redemption was on
the menu, and plain arithmetic for (redemption of the group's mortgaged deeds
+ one house). It executes nothing. Arithmetic sufficiency is NOT a legal
witness: the engine was not run, so "arithmetically covered" means only that
the observed menu fact cannot be upgraded to a financing impossibility.
"""
from __future__ import annotations

import math
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import board, decisions, dump, ledger  # noqa: E402

B, SP = board()
OVERCHARGE = {50, 90, 100, 110, 200}  # documented float-ceiling principals


def mortgage_value(key):
    return SP[key]["price"] // 2


def redemption(key):
    m = mortgage_value(key)
    exact = math.ceil(m * 11 / 10)
    return exact + (1 if m in OVERCHARGE else 0)


def group_of(key):
    return SP[key].get("group")


win = ledger("first_management_windows.json")
rows = []
for r in win["rows"]:
    if r["cause"] == "built":
        continue
    g = r["game"]
    grp = r["group"]
    members = [k for k, s in SP.items() if s.get("group") == grp]
    house = B["house_cost_by_group"][grp]
    dec_rows = []
    for d in r["decisions"]:
        idx = int(d["decision_id"].rsplit("-", 1)[1])
        rec = decisions(g)[idx]
        st = rec["started"]
        you = st["prompt_payload"]["game_state"]["you"]
        assert st["player_id"] == r["player"], (g, idx)
        opts = st["prompt_payload"]["action_state"]["scenario"].get("options", {})
        owned = {h["space_key"]: h for h in you["holdings"]["owned"]}
        if not all(m in owned for m in members):
            # decision in the same turn that precedes the completing settlement
            dec_rows.append({"decision": idx, "pre_completion": True,
                             "applied": rec["resolved"]["final_action"]["action"]})
            continue
        mort_in_group = [m for m in members if owned[m]["mortgaged"]]
        redeem_cost = sum(redemption(m) for m in mort_in_group)
        other_clear = [
            k
            for k, h in owned.items()
            if not h["mortgaged"] and k not in members and h["houses"] == 0 and not h["hotel"]
        ]
        # collateral outside the group whose own colour group carries no buildings
        def group_has_buildings(k):
            gk = group_of(k)
            if gk is None:
                return False
            return any(
                (o["houses"] or o["hotel"]) for kk, o in owned.items() if group_of(kk) == gk
            )

        other_collateral = sum(mortgage_value(k) for k in other_clear if not group_has_buildings(k))
        need = redeem_cost + house
        dec_rows.append(
            {
                "decision": idx,
                "turn": st["turn_index"],
                "cash": you["cash"],
                "menu": st["prompt_payload"]["action_state"]["available_actions"],
                "buildable_keys": opts.get("buildable_space_keys"),
                "redeemable_keys_on_menu": opts.get("unmortgageable_space_keys"),
                "group_deeds_mortgaged": mort_in_group,
                "redemption_cost_group": redeem_cost,
                "house_cost": house,
                "need_redeem_plus_one_house": need,
                "cash_covers_need": you["cash"] >= need,
                "other_clear_collateral_value": other_collateral,
                "cash_plus_other_mortgages_covers_need": you["cash"] + other_collateral >= need,
                "applied": rec["resolved"]["final_action"]["action"],
                "fallback_used": rec["resolved"]["fallback_used"],
                "private_note": (rec["resolved"]["final_action"].get("private_thought") or "")[:400],
                "public_message": (rec["resolved"]["final_action"].get("public_message") or "")[:300],
            }
        )
    rows.append(
        {
            "game": g,
            "model": r["model"],
            "player": r["player"],
            "group": grp,
            "cause": r["cause"],
            "entry_legal": r["entry_legal"],
            "legal_any_menu": r["legal_any_menu_that_turn"],
            "first_mgmt_turn": r["first_mgmt_turn"],
            "decisions": dec_rows,
        }
    )

summary = {"never_legal": []}
for r in rows:
    if r["cause"] != "never_legal_in_window":
        continue
    post = [d for d in r["decisions"] if not d.get("pre_completion")]
    first = post[0]
    summary["never_legal"].append(
        {
            "case": f"G{r['game']} {r['model']} {r['group']}",
            "window_decisions": [d["decision"] for d in post],
            "applied": [d["applied"] for d in post],
            "pre_completion_decisions_same_turn": [d["decision"] for d in r["decisions"] if d.get("pre_completion")],
            "cash_at_first_decision": first["cash"],
            "group_deeds_mortgaged": first["group_deeds_mortgaged"],
            "redemption_on_first_menu": bool(
                set(first["group_deeds_mortgaged"]) & set(first["redeemable_keys_on_menu"] or [])
            ),
            "need": first["need_redeem_plus_one_house"],
            "cash_covers_need": first["cash_covers_need"],
            "cash_plus_other_mortgages_covers_need": first["cash_plus_other_mortgages_covers_need"],
            "other_clear_collateral_value": first["other_clear_collateral_value"],
        }
    )
nl = summary["never_legal"]
summary["counts"] = {
    "never_legal_windows": len(nl),
    "with_a_mortgaged_group_deed": sum(bool(x["group_deeds_mortgaged"]) for x in nl),
    "cash_alone_covers_redemption_plus_one_house": sum(x["cash_covers_need"] for x in nl),
    "cash_plus_unrelated_mortgages_covers": sum(
        x["cash_plus_other_mortgages_covers_need"] for x in nl
    ),
    "neither": sum(not x["cash_plus_other_mortgages_covers_need"] for x in nl),
    "caveat": "Arithmetic only; no engine execution. Not a legal witness and not evidence that building was sound.",
}
dump("window_menu_checks.json", {"summary": summary, "rows": rows})

import json  # noqa: E402

print(json.dumps(summary, indent=1))
for r in rows:
    if r["cause"] == "never_legal_in_window":
        for d in [x for x in r["decisions"] if not x.get("pre_completion")]:
            print(
                f"G{r['game']} d{d['decision']} {r['model']} {r['group']} cash={d['cash']} menu={d['menu']} "
                f"redeemable={d['redeemable_keys_on_menu']} applied={d['applied']}"
            )
            print("   note:", d["private_note"][:300].replace("\n", " "))
            print("   pub :", d["public_message"][:200].replace("\n", " "))
