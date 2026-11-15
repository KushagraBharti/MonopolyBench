"""Record-reading checks behind individual findings in review.md.

Every check reads retained ledgers or canonical saved-game records. Nothing
is executed against the engine and no model is called.

  A. Who acted at G2 d243 (Opus draft: "Sol's seven-house target").
  B. Grok content/tool conflicts joined to offers and threads, and every
     conflict that involves a bankruptcy declaration in either channel.
  C. Grok's cash path in G13 from the insurance sale to its elimination.
  D. Delivered liquidation menus and applied notes at the four eliminations
     whose own-asset bound is not below the debt.
  E. The 74 coded rejections split by completion cell and by recipient.
  F. Arithmetic inside newly quoted notes (quotes stay verbatim; the paper
     must say where they are wrong).
  G. Chronology facts used by the G2, G15, G1, G11 and G18 incident texts.
"""
from __future__ import annotations

import collections
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import MODEL, board, decisions, dump, ledger  # noqa: E402

B, SP = board()
out: dict = {}
offers = ledger("agenda_offers.json")
flows = ledger("agenda_flows.json")
elims = ledger("t06_eliminations.json")
rc = ledger("resolution_conditions.json")
units = ledger("t05_spending_units.json")


def res(g, i):
    return decisions(g)[i]["resolved"]


def started(g, i):
    return decisions(g)[i]["started"]


# --- A -------------------------------------------------------------------
out["A_g2_actors"] = {
    f"d{i}": {
        "model": MODEL[res(2, i)["openrouter_model_id"]],
        "player": res(2, i)["player_id"],
        "type": res(2, i)["decision_type"],
        "applied": res(2, i)["final_action"]["action"],
        "turn": res(2, i)["turn_index"],
        "attempts": len(res(2, i)["attempts"]),
        "retry_used": res(2, i)["retry_used"],
    }
    for i in (239, 243, 244)
}

# --- B -------------------------------------------------------------------
conf = rc["selected_grok_conflicts"]
pairs = collections.Counter((c["content_name"], c["received_tool_name"]) for c in conf)
conf_idx = {(c["game"], int(c["decision_id"].rsplit("-", 1)[1])) for c in conf}
threads = collections.defaultdict(list)
for o in offers:
    threads[o["thread_id"]].append(o)
for t in threads.values():
    t.sort(key=lambda r: r["exchange_index"])
opened = [t for t in threads.values() if (t[0]["game"], t[0]["offer_decision"]) in conf_idx]
resp = [o for o in offers if (o["game"], o["decision"]) in conf_idx]
elim_key = {(e["game"], int(e["decision"].split("-")[1])): e for e in elims}
last_elim_by_player = {}
for e in elims:
    last_elim_by_player[(e["game"], e["player"])] = e
bank_conf = []
for c in conf:
    if "declare_bankruptcy" not in (c["content_name"], c["received_tool_name"]):
        continue
    g, i = c["game"], int(c["decision_id"].rsplit("-", 1)[1])
    st = started(g, i)
    sc = st["prompt_payload"]["action_state"]["scenario"]
    e = last_elim_by_player.get((g, st["player_id"]))
    bank_conf.append(
        {
            "game": g,
            "decision": i,
            "content": c["content_name"],
            "received": c["received_tool_name"],
            "owed": sc.get("owed_amount"),
            "cash": st["prompt_payload"]["game_state"]["you"]["cash"],
            "this_players_elimination": None
            if not e
            else {"decision": e["decision"], "owed": e["owed"], "full_bound": e["full"], "avoidable": e["avoidable"], "kind": e["elimination"]},
        }
    )
out["B_conflicts"] = {
    "selected": len(conf),
    "pairs": {f"{a} -> {b}": n for (a, b), n in pairs.most_common()},
    "threads_opened_by_conflict": len(opened),
    "of_which_settled": sum(t[-1]["response"] == "accept_trade" for t in opened),
    "grok_threads": sum(t[0]["author_model"] == "Grok" for t in threads.values()),
    "conflicting_trade_responses": len(resp),
    "conflicting_acceptances": sum(o["response"] == "accept_trade" for o in resp),
    "conflicting_acceptances_author_only_cell": [
        {"game": o["game"], "decision": o["decision"], "author": o["author_model"], "groups": o["author_new_groups"]}
        for o in resp
        if o["response"] == "accept_trade" and o["completion_cell"] == "author_only"
    ],
    "bankruptcy_related": bank_conf,
    "content_declares_but_call_liquidates": sum(c["content"] == "declare_bankruptcy" for c in bank_conf),
    "of_those_with_debt_above_bound_at_elimination": sum(
        c["content"] == "declare_bankruptcy"
        and c["this_players_elimination"]
        and c["this_players_elimination"]["full_bound"] < c["this_players_elimination"]["owed"]
        for c in bank_conf
    ),
}

# --- C -------------------------------------------------------------------
path, last = [], None
for i in range(250, 312):
    st = started(13, i)
    gs = st["prompt_payload"]["game_state"]
    grok = [p for p in [gs["you"]] + gs["others"] if "grok" in p["name"]][0]
    if grok["cash"] != last:
        path.append({"decision": i, "turn": st["turn_index"], "cash": grok["cash"], "position": grok["position"]})
        last = grok["cash"]
out["C_g13_grok_cash_path"] = {
    "changes": path,
    "min_cash_between_sale_and_turn_146": min(p["cash"] for p in path if 254 <= p["decision"] < 307),
    "note": "Observed cash as shown in delivered prompts. Not a counterfactual path without the sale.",
}

# --- D -------------------------------------------------------------------
menus = {}
for g, i in ((12, 190), (12, 249), (17, 234), (7, 339)):
    st = started(g, i)
    a = st["prompt_payload"]["action_state"]
    you = st["prompt_payload"]["game_state"]["you"]
    fa = res(g, i)["final_action"]
    built_groups = {SP[h["space_key"]].get("group") for h in you["holdings"]["owned"] if h["houses"] or h["hotel"]}
    unlocked = sum(
        SP[h["space_key"]]["price"] // 2
        for h in you["holdings"]["owned"]
        if not h["mortgaged"] and SP[h["space_key"]].get("group") in built_groups
    )
    menus[f"G{g} d{i}"] = {
        "model": MODEL[st["openrouter_model_id"]],
        "cash": you["cash"],
        "owed": a["scenario"]["owed_amount"],
        "menu": a["available_actions"],
        "sale_action_on_menu": "sell_houses_or_hotel" in a["available_actions"],
        "mortgageable_listed": a["scenario"]["options"]["mortgageable_space_keys"],
        "sellable_listed": a["scenario"]["options"]["sellable_building_space_keys"],
        "bank_houses": st["prompt_payload"]["game_state"]["bank"]["houses_remaining"],
        "mortgage_value_locked_behind_buildings": unlocked,
        "applied": fa["action"],
        "note_head": (fa.get("private_thought") or "")[:420],
    }
out["D_liquidation_menus"] = menus

# --- E -------------------------------------------------------------------
rr = ledger("agenda_rejection_reasons.json")["rows_data"]
out["E_rejection_reasons"] = {
    "n": len(rr),
    "by_cell": dict(collections.Counter(r["completion_cell"] for r in rr)),
    "by_recipient": dict(collections.Counter(r["recipient_model"] for r in rr)),
    "first_reader_D_by_cell": {
        cell: {
            "D": sum("D" in r["codes"] for r in rr if r["completion_cell"] == cell),
            "n": sum(r["completion_cell"] == cell for r in rr),
        }
        for cell in ("both", "recipient_only")
    },
    "first_reader_D_by_recipient": {
        m: {"D": sum("D" in r["codes"] for r in rr if r["recipient_model"] == m), "n": sum(r["recipient_model"] == m for r in rr)}
        for m in ("Sol", "Gemini", "Opus", "Grok")
    },
    "top_games": collections.Counter(r["game"] for r in rr).most_common(3),
    "note": "First reader only; the 61 agreed codes are not itemized in the retained file.",
}

# --- F -------------------------------------------------------------------
yellow = B["house_cost_by_group"]["YELLOW"]
green = B["house_cost_by_group"]["GREEN"]
bw_m = SP["BOARDWALK"]["price"] // 2
out["F_quote_arithmetic"] = {
    "g2_d124_note": {
        "quote": "At $325 p4 retains $520, enough for nine yellow houses immediately.",
        "residual_cash_845_minus_325": 845 - 325,
        "yellow_house_cost": yellow,
        "houses_520_buys": 520 // yellow,
        "cost_of_nine": 9 * yellow,
        "verdict": "Residual cash is right. The capacity claim is wrong from cash alone: $520 buys three yellow houses; nine cost $1,350.",
    },
    "g2_d124_note_second": {
        "quote": "$650 gives me acquisition/building capital while leaving p4 only $195 before mortgages.",
        "845_minus_650": 845 - 650,
        "verdict": "Correct.",
    },
    "g15_d169_note": {
        "quote": "~$830 plus mortgage capacity to drop 5+ yellow houses ($150) ... only ~$233 - can't even even-build one house each ($600)",
        "sol_cash_if_accepted": 830,
        "houses_830_buys": 830 // yellow,
        "grok_cash_if_accepted": 233,
        "one_green_house": green,
        "one_each_on_three_greens": 3 * green,
        "verdict": "Cash figures match the ledger; 830 buys five yellow houses. $233 covers one green house but not one on each ($600), which is what the note says.",
    },
    "g15_d174_public": {"quote": "$583 versus my $480", "333_plus_250": 333 + 250, "730_minus_250": 730 - 250, "verdict": "Correct."},
    "g1_d309_note": {
        "quote": "Cash $239 ... Cannot unmortgage ($220)",
        "cash_after_price": 339 - 100,
        "cash_after_price_and_transfer_interest": 339 - 100 - 20,
        "standard_redemption": bw_m * 11 // 10,
        "engine_redemption_with_documented_overcharge": bw_m * 11 // 10 + 1,
        "verdict": "The note omits the $20 transfer interest (cash after settlement is $219) and uses the standard $220; this engine charges $221.",
    },
    "g13_d250_public": {"quote": "5/36 is Short Line", "atlantic_to_short_line_squares": 35 - 26, "ways_to_roll_9": 4, "verdict": "Wrong; 4/36."},
}

# --- G -------------------------------------------------------------------
def elim_rows(g):
    rows = []
    for e in elims:
        if e["game"] == g:
            i = int(e["decision"].split("-")[1])
            cred = sorted({f["to_model"] for f in flows if f["game"] == g and f["kind"].startswith("estate") and f["from_model"] == e["model"]})
            rows.append({"debtor": e["model"], "decision": i, "turn": res(g, i)["turn_index"], "owed": e["owed"], "bound": e["full"], "creditor": cred})
    return rows


def offer_row(g, d):
    o = [x for x in offers if x["game"] == g and x["decision"] == d][0]
    return {
        k: o[k]
        for k in (
            "turn", "author_model", "recipient_model", "response", "completion_cell", "offer", "request",
            "author_cash_before", "recipient_cash_before", "author_cash_if_accepted", "recipient_cash_if_accepted",
            "recipient_interest_if_accepted", "response_condition",
        )
    }


out["G_chronology"] = {
    "eliminations": {f"G{g}": elim_rows(g) for g in (1, 2, 11, 13, 15, 18)},
    "g2_offers": {f"d{d}": offer_row(2, d) for d in (124, 128, 197, 198)},
    "g2_yellow_spending_units": [u for u in units if u["game"] == 2 and u["group"] == "YELLOW"],
    "g15_offers": {f"d{d}": offer_row(15, d) for d in (169, 173, 175)},
    "g15_grok_estate_deeds": sorted(f["space_key"] for f in flows if f["game"] == 15 and f["kind"] == "estate_deed" and f["from_model"] == "Grok"),
    "g1_d309": offer_row(1, 309),
}

dump("record_checks.json", out)
print(json.dumps({k: v for k, v in out.items() if k not in ("G_chronology",)}, indent=1)[:9000])
