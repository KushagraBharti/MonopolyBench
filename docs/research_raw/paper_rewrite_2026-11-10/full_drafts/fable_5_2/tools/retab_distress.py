#!/usr/bin/env python3
"""Exploratory re-tabulation: offers in which the cash-seeking side is cash-poor (existing ledger only).

Input : ../../data/agenda_offers.json, ../../data/agenda_flows.json, ../../data/t01_cohort.json
Output: data/distress_retabulation.json
Definition fixed before tabulating outcomes for the manuscript: an offer is a *cash ask* when net cash would flow
from recipient to offer writer, and a *cash bid* when it would flow from writer to recipient. The cash-seeking side
is "cash-poor" when its cash before the offer is below THRESHOLD (primary 100; 50/150/200 reported as sensitivity).
"""
import json, collections, pathlib, statistics as st
HERE = pathlib.Path(__file__).resolve().parent.parent
D = HERE.parent.parent / "data"
rows = [r for r in json.loads((D / "agenda_offers.json").read_text()) if r["accept_available"]]
flows = json.loads((D / "agenda_flows.json").read_text())
winner = {c["game"]: c["winner"] for c in json.loads((D / "t01_cohort.json").read_text())}
C = collections.Counter
def tab(rr):
    c = C(r["response"] for r in rr)
    return {"n": len(rr), "accept": c["accept_trade"], "counter": c["counter_trade"], "reject": c["reject_trade"]}
out = {"definition": __doc__.split("Definition")[1].strip(), "thresholds": {}}
for thr in (50, 100, 150, 200):
    ask = [r for r in rows if r["net_cash_author_to_recipient"] < 0]
    bid = [r for r in rows if r["net_cash_author_to_recipient"] > 0]
    out["thresholds"][str(thr)] = {
        "ask_by_cash_poor_writer": tab([r for r in ask if r["author_cash_before"] < thr]),
        "ask_by_other_writer": tab([r for r in ask if r["author_cash_before"] >= thr]),
        "bid_to_cash_poor_recipient": tab([r for r in bid if r["recipient_cash_before"] < thr]),
        "bid_to_other_recipient": tab([r for r in bid if r["recipient_cash_before"] >= thr])}
out["all_asks"] = tab([r for r in rows if r["net_cash_author_to_recipient"] < 0])
out["all_bids"] = tab([r for r in rows if r["net_cash_author_to_recipient"] > 0])
out["no_net_cash"] = tab([r for r in rows if r["net_cash_author_to_recipient"] == 0])
T = 100
poor_ask = [r for r in rows if r["net_cash_author_to_recipient"] < 0 and r["author_cash_before"] < T]
poor_bid = [r for r in rows if r["net_cash_author_to_recipient"] > 0 and r["recipient_cash_before"] < T]
out["primary_composition"] = {
    "ask_writer_model": dict(C(r["author_model"] for r in poor_ask)), "ask_recipient_model": dict(C(r["recipient_model"] for r in poor_ask)),
    "ask_games": len(set(r["game"] for r in poor_ask)), "ask_cells": dict(C(r["completion_cell"] for r in poor_ask)),
    "bid_writer_model": dict(C(r["author_model"] for r in poor_bid)), "bid_recipient_model": dict(C(r["recipient_model"] for r in poor_bid)),
    "bid_games": len(set(r["game"] for r in poor_bid)), "bid_cells": dict(C(r["completion_cell"] for r in poor_bid)),
    "ask_by_recipient_model": {m: tab([r for r in poor_ask if r["recipient_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]},
    "bid_by_recipient_model": {m: tab([r for r in poor_bid if r["recipient_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]},
    "other_ask_by_recipient_model": {m: tab([r for r in rows if r["net_cash_author_to_recipient"] < 0 and r["author_cash_before"] >= T and r["recipient_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]},
    "other_bid_by_recipient_model": {m: tab([r for r in rows if r["net_cash_author_to_recipient"] > 0 and r["recipient_cash_before"] >= T and r["recipient_model"] == m]) for m in ["Sol", "Gemini", "Opus", "Grok"]}}
# settlements in which the net cash receiver held under T before the trade
acc = [r for r in rows if r["response"] == "accept_trade"]
ds = []
for r in acc:
    net = r["net_cash_author_to_recipient"]
    if net == 0: continue
    seller, seller_model, seller_cash, buyer_model, buyer_groups = ((r["recipient"], r["recipient_model"], r["recipient_cash_before"], r["author_model"], r["author_new_groups"]) if net > 0
                                                                     else (r["author"], r["author_model"], r["author_cash_before"], r["recipient_model"], r["recipient_new_groups"]))
    if seller_cash < T:
        el = [x for x in flows if x["game"] == r["game"] and x["kind"] in ("estate_cash", "estate_deed") and x["from"] == seller]
        el_turn = min((x["turn"] for x in el), default=None)
        ds.append({"game": r["game"], "decision": r["decision"], "turn": r["turn"], "seller": seller_model, "buyer": buyer_model, "price": abs(net), "seller_cash_before": seller_cash,
                   "buyer_completes": buyer_groups, "seller_won": seller_model == winner[r["game"]], "seller_estate_turn": el_turn,
                   "turns_to_seller_estate": (el_turn - r["turn"]) if el_turn is not None else None})
out["distress_settlements"] = {"n": len(ds), "of_settlements_with_net_cash": sum(1 for r in acc if r["net_cash_author_to_recipient"] != 0), "of_all_settlements": len(acc),
                               "buyer_completes_group": sum(1 for d in ds if d["buyer_completes"]), "median_price": st.median(d["price"] for d in ds),
                               "seller_model": dict(C(d["seller"] for d in ds)), "buyer_model": dict(C(d["buyer"] for d in ds)), "games": len(set(d["game"] for d in ds)),
                               "seller_later_won": sum(1 for d in ds if d["seller_won"]),
                               "seller_estate_recorded": sum(1 for d in ds if d["seller_estate_turn"] is not None),
                               "median_turns_to_seller_estate": st.median(d["turns_to_seller_estate"] for d in ds if d["turns_to_seller_estate"] is not None),
                               "seller_estate_within_10_turns": sum(1 for d in ds if d["turns_to_seller_estate"] is not None and d["turns_to_seller_estate"] <= 10),
                               "seller_estate_within_20_turns": sum(1 for d in ds if d["turns_to_seller_estate"] is not None and d["turns_to_seller_estate"] <= 20)}

# threshold sensitivity for settlements, and the completing/non-completing split
def seller_side(r):
    net = r["net_cash_author_to_recipient"]
    if net > 0: return r["recipient_cash_before"], bool(r["author_new_groups"])
    if net < 0: return r["author_cash_before"], bool(r["recipient_new_groups"])
    return None, None
sens = {}
for thr in (50, 100, 150, 200):
    n = comp = 0
    for r in acc:
        cash, buyer_completes = seller_side(r)
        if cash is None or cash >= thr: continue
        n += 1; comp += bool(buyer_completes)
    sens[str(thr)] = {"cash_poor_seller_settlements": n, "of_which_buyer_completes": comp}
out["settlement_sensitivity"] = sens
completing = [r for r in acc if r["author_new_groups"] or r["recipient_new_groups"]]
out["completing_settlements"] = {"n": len(completing),
    "payer_completes": sum(1 for r in completing if seller_side(r)[1]),
    "payer_completes_and_seller_under_100": sum(1 for r in completing if seller_side(r)[1] and seller_side(r)[0] < 100),
    "median_seller_cash_when_payer_completes": st.median(seller_side(r)[0] for r in completing if seller_side(r)[1]),
    "no_net_cash": sum(1 for r in completing if r["net_cash_author_to_recipient"] == 0)}
noncomp = [r for r in acc if not (r["author_new_groups"] or r["recipient_new_groups"])]
out["noncompleting_settlements"] = {"n": len(noncomp), "with_net_cash": sum(1 for r in noncomp if r["net_cash_author_to_recipient"] != 0),
    "seller_under_100": sum(1 for r in noncomp if seller_side(r)[0] is not None and seller_side(r)[0] < 100),
    "median_seller_cash": st.median(seller_side(r)[0] for r in noncomp if seller_side(r)[0] is not None)}
out["distress_settlement_rows"] = ds
(HERE / "data" / "distress_retabulation.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "distress_settlement_rows"}, indent=1))
