"""Check every factual statement made around the eight incidents against saved records.

Each check reads delivered prompt states, applied actions or events.  The
script asserts what the manuscript states and writes the observed values to
``data/b5_incidents.json``.  No engine, replay or model call.
"""
from __future__ import annotations

import json
import re

from corpus import OUT, board, complete_groups, load_all, write_json

B = board()
G = load_all()
DEBT = json.loads((OUT / "b2_debt_episodes.json").read_text())
out = {}


def cash(g, k, pid=None):
    st = g.started[k]["prompt_payload"]["game_state"]
    if pid is None or pid == st["you"]["player_id"]:
        return st["you"]["cash"]
    return next(o["cash"] for o in st["others"] if o["player_id"] == pid)


def act(g, k):
    fa = g.resolved[k]["final_action"]
    return fa["action"], fa.get("args") or {}


def turn(g, k):
    return g.started[k]["turn_index"]


def elim(gn, model):
    return next(d for d in DEBT if d["game"] == gn and d["outcome"] == "eliminated" and d["model"] == model)


def owned(g, k, pid):
    return g.state_before(k)["players"][pid]["owned"]


def ever_complete(g, pid, group):
    keys = set(B["color_groups"][group])
    return any(keys <= set(g.state_before(k)["players"][pid]["owned"]) for k in range(g.n_decisions))


def delivered(g, k, text, to_pid, horizon=80):
    for j in range(k + 1, min(g.n_decisions, k + horizon)):
        st = g.started[j]
        if st["player_id"] == to_pid and text in json.dumps(st["prompt_payload"], ensure_ascii=False):
            return j
    return None


def texts(r):
    sel = [a for a in r["attempts"] if a.get("outcome") == "valid"]
    a = sel[-1] if sel else r["attempts"][-1]
    msg = ((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {})
    return {"public": r["final_action"].get("public_message") or "", "note": r["final_action"].get("private_thought") or "",
            "content": a.get("assistant_content") or "", "reasoning": msg.get("reasoning") or ""}


# ------------------------------------------------------------------ G15
g = G[15]
sol, grok, gem = g.pid_of["Sol"], g.pid_of["Grok"], g.pid_of["Gemini"]
assert turn(g, 168) == 63 and cash(g, 168) == 730 and cash(g, 169) == 333
a168 = act(g, 168)[1]
assert a168["offer"]["properties"] == ["PACIFIC_AVENUE", "NORTH_CAROLINA_AVENUE"] or set(a168["offer"]["properties"]) <= set(B["color_groups"]["GREEN"])
assert a168["request"]["properties"] == ["VENTNOR_AVENUE"] and a168["request"]["cash"] == 100
assert 730 + 100 == 830 and 333 - 100 == 233
seq = [(k, g.model[g.resolved[k]["player_id"]], *act(g, k)) for k in range(168, 177)]
offers = [(k, a["offer"], a["request"]) for k, m, name, a in seq if name == "propose_trade" and m == "Sol" and a["to_player_id"] == grok]
rejections = [k for k, m, name, a in seq if name == "reject_trade" and m == "Grok"]
assert B["by_key"]["PACIFIC_AVENUE"]["house_cost"] == 200 and B["by_key"]["VENTNOR_AVENUE"]["house_cost"] == 150
eg = elim(15, "Grok")
assert eg["turn"] == 81 and eg["creditor"] == gem and g.winner == "Gemini"
assert not ever_complete(g, sol, "YELLOW") and not ever_complete(g, sol, "GREEN")
last = act(g, 174)[1]
out["G15"] = {"turn": 63, "sol_cash": 730, "grok_cash": 333, "sol_offers": offers, "grok_rejections": rejections,
              "final_offer": last, "post_trade_cash_final": [730 - last["offer"]["cash"], 333 + last["offer"]["cash"]],
              "grok_eliminated_turn": 81, "creditor": "Gemini", "sol_ever_completes_yellow_or_green": False,
              "refusal_delivered_to_sol_at": delivered(g, 175, g.resolved[175]["final_action"]["public_message"], sol),
              "opus_appeal_d166": g.resolved[166]["final_action"]["public_message"],
              "opus_appeal_in_grok_prompt_d169": "let's not hand him the last piece of any set" in json.dumps(g.started[169]["prompt_payload"]),
              "gemini_also_refuses_sol_d171": act(g, 171)[0]}
assert len(offers) == 3 and offers[2][1]["cash"] == 250 and "KENTUCKY_AVENUE" in offers[2][1]["properties"]
assert out["G15"]["post_trade_cash_final"] == [480, 583]

# ------------------------------------------------------------------ G2
g = G[2]
sol, opus, grok, gem = (g.pid_of[m] for m in ("Sol", "Opus", "Grok", "Gemini"))
assert turn(g, 119) == 44 and act(g, 119)[1]["request"]["cash"] == 450 and act(g, 119)[1]["offer"]["properties"] == ["MARVIN_GARDENS"]
assert act(g, 118)[1]["to_player_id"] == sol and g.resolved[118]["player_id"] == grok and act(g, 118)[1]["offer"]["cash"] == 200
yellow = set(B["color_groups"]["YELLOW"])
assert len(yellow & set(owned(g, 119, grok))) == 0 and len(yellow & set(owned(g, 124, opus))) == 2
assert turn(g, 124) == 45 and act(g, 124)[1]["request"]["cash"] == 650
bid = None
for k in range(120, 125):
    name, a = act(g, k)
    if name == "propose_trade" and g.resolved[k]["player_id"] == opus:
        bid = (k, a["offer"]["cash"], a["request"]["properties"])
assert bid and bid[1] == 325 and bid[2] == ["MARVIN_GARDENS"]
opus_cash_at_bid = cash(g, bid[0])
assert opus_cash_at_bid - 325 == 520 and B["by_key"]["MARVIN_GARDENS"]["house_cost"] == 150 and 520 // 150 == 3
assert opus_cash_at_bid - 650 == 195
assert act(g, 127)[1]["offer"]["cash"] == 450 and act(g, 128)[0] == "reject_trade"
assert turn(g, 197) == 69 and cash(g, 197) == 17 and act(g, 198)[0] == "accept_trade"
a197 = act(g, 197)[1]
assert set(a197["offer"]["properties"]) < yellow and len(a197["offer"]["properties"]) == 2 and a197["request"]["cash"] == 100
assert all(B["by_key"][x]["group"] == "RAILROAD" for x in a197["request"]["properties"]) and len(a197["request"]["properties"]) == 2
eo, es = elim(2, "Opus"), elim(2, "Sol")
assert eo["turn"] == 72 and eo["creditor"] == gem and es["turn"] == 85 and es["creditor"] == gem and g.winner == "Gemini"
yi = {B["by_key"][x]["index"] for x in yellow}
rent = [e for e in g.events if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == sol and e["payload"]["space_index"] in yi and e["turn_index"] >= 69]
built = [e for e in g.events if e["type"] == "HOUSE_BUILT" and e["payload"]["player_id"] == sol and e["turn_index"] >= 69]
sold = [e for e in g.events if e["type"] == "HOUSE_SOLD" and e["payload"]["player_id"] == sol and e["turn_index"] >= 69]
out["G2"] = {"ask_to_grok": 450, "opus_bid": 325, "opus_cash_at_bid": opus_cash_at_bid, "houses_520_buys": 3, "sol_ask": 650,
             "opus_final": 450, "reversal_turn": 69, "opus_cash_at_reversal": 17,
             "sol_yellow_rent_after": [[e["turn_index"], e["payload"]["amount"]] for e in rent],
             "sol_house_built_events": len(built), "sol_house_sold_events": len(sold),
             "opus_eliminated_turn": 72, "sol_eliminated_turn": 85, "winner": "Gemini",
             "final_claim_delivered_to_sol_at": delivered(g, 127, "$450, and that's my final offer.", sol)}
assert sum(e["payload"]["amount"] for e in rent) == 44

# ------------------------------------------------------------------ G13
g = G[13]
opus, grok, sol = g.pid_of["Opus"], g.pid_of["Grok"], g.pid_of["Sol"]
st = g.started[250]["prompt_payload"]["game_state"]["you"]
assert st["cash"] == 35 and st["position"] == "ATLANTIC_AVENUE" and turn(g, 250) == 107
own = {h["space_key"]: h for h in st["holdings"]["owned"]}
assert not own["VENTNOR_AVENUE"]["mortgaged"] and own["PENNSYLVANIA_AVENUE"]["mortgaged"] and B["by_key"]["VENTNOR_AVENUE"]["mortgage"] == 130
assert yellow_ok if (yellow_ok := {"ATLANTIC_AVENUE", "VENTNOR_AVENUE", "MARVIN_GARDENS"} <= set(own)) else False
assert act(g, 250)[1]["request"]["cash"] == 200 and act(g, 251)[1]["offer"]["cash"] == 130 and act(g, 252)[1]["request"]["cash"] == 200 and act(g, 253)[0] == "accept_trade"
interest = [e for e in g.events if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE_INTEREST" and e["turn_index"] == 107]
assert interest and interest[0]["payload"]["delta"] == -16 and interest[0]["payload"]["player_id"] == opus
auc = [e for e in g.events if e["type"] == "AUCTION_ENDED" and e["payload"]["property_space"] == "NORTH_CAROLINA_AVENUE"]
assert auc[0]["payload"]["winner_player_id"] == opus and auc[0]["turn_index"] == 114
moves = [e for e in g.events if e["type"] == "PLAYER_MOVED" and e["actor"]["player_id"] == grok and e["turn_index"] > 107]
assert B["by_key"]["SHORT_LINE"]["index"] == 35 and B["by_key"]["ATLANTIC_AVENUE"]["index"] == 26 and moves[0]["payload"]["to"] != 35
eg = elim(13, "Grok")
assert eg["turn"] == 150 and eg["creditor"] == sol and eg["debt"] == 200 and g.winner == "Opus"
assert g.started[eg["first_decision"]]["prompt_payload"]["game_state"]["you"]["position"] == "SHORT_LINE"
# rent on Short Line at d250: Sol's railroad count
rr = [x for x in owned(g, 250, sol) if B["by_key"][x]["group"] == "RAILROAD"]
assert len(rr) == 4 and "SHORT_LINE" in rr
assert 35 + 130 + 130 >= 200 and 35 + 130 < 200 and 35 + 165 == 200
t253 = texts(g.resolved[253])
out["G13"] = {"turn": 107, "grok_cash": 35, "sol_railroads": len(rr), "short_line_rent": 200, "ventnor_mortgage": 130,
              "nine_probability": "4/36", "opus_interest": 16, "opus_green_complete_turn": 114, "grok_next_square": moves[0]["payload"]["to"],
              "grok_eliminated_turn": 150, "creditor": "Sol", "winner": "Opus",
              "opus_d253_condition": g.resolved[253]["sequence_meta"].get("response_condition"),
              "opus_d253_reasoning": t253["reasoning"],
              "opening_delivered_to_opus_at": delivered(g, 250, "gpt inherits the yellows in bankruptcy", opus),
              "counter_delivered_to_opus_at": delivered(g, 252, "$130 leaves me $35 short of Short Line", opus)}

# ------------------------------------------------------------------ G18
g = G[18]
opus, sol = g.pid_of["Opus"], g.pid_of["Sol"]
remaining = lambda k: sum(1 for p in g.state_before(k)["players"].values() if not p["bankrupt"])
assert remaining(421) == 2 and remaining(442) == 2
pat = re.compile(r"inherit|estate|creditor", re.I)
hits = []
for k in range(421, 462):
    r = g.resolved[k]
    if r["player_id"] != opus:
        continue
    for ch, t in texts(r).items():
        if pat.search(t):
            hits.append([k, ch])
assert hits == []
bids = []
for k in range(380, g.n_decisions):
    name, a = act(g, k)
    if name in ("propose_trade", "counter_trade") and g.resolved[k]["player_id"] == opus and "PACIFIC_AVENUE" in (a.get("request", {}).get("properties") or []):
        bids.append([k, turn(g, k), a["offer"]["cash"]])
    if name in ("propose_trade", "counter_trade") and g.resolved[k]["player_id"] == sol and "PACIFIC_AVENUE" in (a.get("offer", {}).get("properties") or []):
        bids.append([k, turn(g, k), -a["request"]["cash"]])
unm = [[e["turn_index"], B["by_index"][e["payload"]["space_index"]]["key"]] for e in g.events
       if e["type"] == "PROPERTY_UNMORTGAGED" and e["payload"]["player_id"] == opus and e["turn_index"] >= turn(g, 442)]
rents = [[e["turn_index"], e["payload"]["amount"]] for e in g.events if e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == sol and e["payload"]["to_player_id"] == opus and e["turn_index"] >= turn(g, 425)]
es = elim(18, "Sol")
assert es["creditor"] == opus and g.winner == "Opus"
assert cash(g, 441) == 49 and act(g, 442)[0] != "accept_trade"
assert own_pac if (own_pac := owned(g, 441, sol)["PACIFIC_AVENUE"]["mortgaged"]) else False
greens_opus = {x: owned(g, 442, opus)[x]["mortgaged"] for x in ("NORTH_CAROLINA_AVENUE", "PENNSYLVANIA_AVENUE")}
t431, t442 = texts(g.resolved[431]), texts(g.resolved[442])
out["G18"] = {"players_remaining_d421_d442": 2, "inheritance_terms_in_opus_text_d421_461": hits,
              "pacific_offers_opus_positive_sol_negative": bids, "opus_unmortgages_after_withdrawal": unm,
              "sol_to_opus_rents": rents, "sol_cash_d441": 49, "d441": act(g, 441), "d442_action": act(g, 442)[0],
              "turns": {"d431": turn(g, 431), "d441": turn(g, 441), "d442": turn(g, 442)},
              "opus_greens_mortgaged_at_d442": greens_opus, "sol_eliminated_turn": es["turn"],
              "d431_content": t431["content"], "d431_reasoning": t431["reasoning"], "d442_reasoning": t442["reasoning"],
              "assurance_in_sol_prompt_at_d441": "My Pacific offer still stands" in json.dumps(g.started[441]["prompt_payload"]),
              "assurance_in_opus_prompt_at_d442": "My Pacific offer still stands" in json.dumps(g.started[442]["prompt_payload"]),
              "pacific_ever_transferred_by_trade": any(e["type"] == "TRADE_ACCEPTED" and "PACIFIC_AVENUE" in json.dumps(e["payload"]) for e in g.events if e["turn_index"] >= turn(g, 421))}

# ------------------------------------------------------------------ G20 appeal
g = G[20]
grok, gem, opus, sol = (g.pid_of[m] for m in ("Grok", "Gemini", "Opus", "Sol"))
ill = [k for k in range(96) if g.started[k]["decision_type"] == "TRADE_RESPONSE_DECISION" and act(g, k)[0] == "accept_trade"
       and "ILLINOIS_AVENUE" in json.dumps(g.started[k]["prompt_payload"]["action_state"]["scenario"]["current_offer"])]
assert len(ill) == 1
cur = g.started[ill[0]]["prompt_payload"]["action_state"]["scenario"]["current_offer"]
tr = {"decision": ill[0], "turn": turn(g, ill[0]), "accepted_by": g.model[g.resolved[ill[0]]["player_id"]],
      "offer_from": g.model[cur["from_player_id"]], "if_you_accept": cur["if_you_accept"],
      "grok_cash_before": cash(g, ill[0], grok), "grok_cash_next_prompt": cash(g, ill[0] + 1, grok)}
red = set(B["color_groups"]["RED"])
assert red <= set(owned(g, 96, grok)) and cash(g, 96, grok) == 222
assert act(g, 98)[0] == "build_houses_or_hotel" and act(g, 100)[1]["request"]["cash"] == 150 and act(g, 100)[1]["offer"]["properties"] == ["VERMONT_AVENUE"]
assert act(g, 101)[0] == "reject_trade" and act(g, 102) == ("mortgage_property", {"space_key": "VERMONT_AVENUE"})
built98 = act(g, 98)[1]
later = []
for k in range(103, g.n_decisions):
    name, a = act(g, k)
    if g.resolved[k]["player_id"] == opus and name == "propose_trade" and a.get("to_player_id") == grok:
        later.append([k, turn(g, k), a["offer"]["cash"], a["request"]["properties"]])
settled = [e for e in g.events if e["type"] == "TRADE_ACCEPTED" and e["turn_index"] > turn(g, 102) and {grok, opus} == {e["payload"].get("from_player_id"), e["payload"].get("to_player_id")}]
order = [d["model"] for d in sorted((d for d in DEBT if d["game"] == 20 and d["outcome"] == "eliminated"), key=lambda d: d["first_decision"])]
assert order[0] == "Grok" and g.winner == "Gemini"
out["G20_appeal"] = {"illinois_sale": tr, "grok_turn27": [[k, act(g, k)[0], cash(g, k)] for k in range(97, 104)], "grok_cash_after": 222, "build_d98": built98, "opus_later_offers_to_grok": later,
                     "opus_grok_trades_settled_after": len(settled), "elimination_order": order, "winner": "Gemini",
                     "appeal_in_grok_prompt_d97": "let's not fund their houses" in json.dumps(g.started[97]["prompt_payload"]),
                     "d129_public": g.resolved[129]["final_action"].get("public_message") if 129 < g.n_decisions else None}
assert out["G20_appeal"]["appeal_in_grok_prompt_d97"]

# ------------------------------------------------------------------ G20 payment
acts = [act(g, k)[0] for k in range(327, 337)]
assert acts.count("sell_houses_or_hotel") == 2 and acts.count("mortgage_property") == 8 and acts[:2] == ["sell_houses_or_hotel"] * 2
cash_path = [cash(g, k) for k in range(327, 338)]
assert cash_path[0] == 49 and cash_path[-1] == 14
ev = [e for e in g.events if e["turn_index"] == 108]
sale = sum(e["payload"]["delta"] for e in ev if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "SELL_BUILDING")
mort = sum(e["payload"]["delta"] for e in ev if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "MORTGAGE")
rentp = [e for e in ev if e["type"] == "RENT_PAID"]
assert sale == 700 and mort == 665 and rentp[0]["payload"]["amount"] == 1400 and 49 + sale + mort - 1400 == 14
assert remaining_g20 if (remaining_g20 := sum(1 for p in g.state_before(325)["players"].values() if not p["bankrupt"]) == 2) else False
assert g.resolved[325]["player_id"] == gem and act(g, 325)[0] == "build_houses_or_hotel"
st327 = g.started[327]["prompt_payload"]["game_state"]["you"]["holdings"]["owned"]
lv = {h["space_key"]: (5 if h["hotel"] else h["houses"]) for h in st327 if h["hotel"] or h["houses"]}
menu_changes = [sorted(g.started[k]["prompt_payload"]["action_state"]["scenario"]["options"]["mortgageable_space_keys"]) for k in range(327, 337)]
out["G20_payment"] = {"actions": acts, "cash_at_prompts": cash_path, "sales": sale, "mortgages": mort, "rent": 1400,
                      "building_levels_at_d327": lv, "mortgage_menu_sizes": [len(m) for m in menu_changes],
                      "turns": {"d325": turn(g, 325), "d327": turn(g, 327)},
                      "gemini_components": {"stated_sales": 675, "stated_mortgages": 690, "realized_sales": sale, "realized_mortgages": mort},
                      "sol_eliminated_later": elim(20, "Sol")["turn"]}

# ------------------------------------------------------------------ G7
g = G[7]
sol, gem, grok, opus = (g.pid_of[m] for m in ("Sol", "Gemini", "Grok", "Opus"))
assert turn(g, 39) == 25 and act(g, 39)[1]["request"]["cash"] == 650
asks = [(k, act(g, k)[1].get("request", {}).get("cash"), act(g, k)[1].get("offer", {}).get("cash")) for k in range(39, 44)]
assert act(g, 42)[1]["offer"]["cash"] == 600 and act(g, 43)[0] == "accept_trade" and B["by_key"]["NORTH_CAROLINA_AVENUE"]["price"] == 300
assert act(g, 41)[1]["request"]["cash"] == 625
assert turn(g, 138) == 67 and cash(g, 140) == 84
assert act(g, 141)[1]["offer"]["cash"] == 350 and act(g, 141)[1]["request"]["properties"] == ["NEW_YORK_AVENUE"]
assert act(g, 142)[1]["request"]["cash"] == 700 and act(g, 145)[0] == "accept_trade" and turn(g, 145) == 68
orange = set(B["color_groups"]["ORANGE"])
gem_built_68 = sum(e["payload"].get("count", 1) for e in g.events if e["type"] == "HOUSE_BUILT" and e["payload"]["player_id"] == gem and e["turn_index"] == 68)
gem_mort_68 = sum(1 for e in g.events if e["type"] == "PROPERTY_MORTGAGED" and e["payload"]["player_id"] == gem and e["turn_index"] == 68)
sol_built = sum(e["payload"].get("count", 1) for e in g.events if e["type"] == "HOUSE_BUILT" and e["payload"]["player_id"] == sol and 68 <= e["turn_index"] <= 76 and e["seq"] > g.resolved[145]["emitted_event_seq_end"])
oi = {B["by_key"][x]["index"] for x in orange}
gem_orange_rent = sum(e["payload"]["amount"] for e in g.events if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == gem and e["payload"]["space_index"] in oi and e["turn_index"] >= 68)
ege = elim(7, "Gemini")
assert ege["creditor"] == sol and g.winner == "Sol"
blue_built_before = sum(e["payload"].get("count", 1) for e in g.events if e["type"] == "HOUSE_BUILT" and e["payload"]["player_id"] == sol and e["turn_index"] == 67)
out["G7"] = {"early_asks": asks, "nc_price": 300, "sale_price": 600, "private_ceiling": 625,
             "sol_cash_after_blue_build": 84, "sol_houses_built_turn_67": blue_built_before,
             "gemini_bid": 350, "sol_ask": 700, "gemini_houses_turn_68": gem_built_68, "gemini_mortgages_turn_68": gem_mort_68,
             "sol_houses_within_8_turns": sol_built, "gemini_orange_rent": gem_orange_rent,
             "gemini_eliminated": [ege["turn"], "Sol"], "winner": "Sol",
             "final_claim_delivered_to_sol_at": delivered(g, 42, "$600, final.", sol)}

# ------------------------------------------------------------------ G19
g = G[19]
grok, sol = g.pid_of["Grok"], g.pid_of["Sol"]
name, a = act(g, 135)
assert name == "propose_trade" and a["offer"]["properties"] == ["VIRGINIA_AVENUE"] and a["offer"]["cash"] == 150 and a["request"]["properties"] == ["STATES_AVENUE"]
assert B["by_key"]["STATES_AVENUE"]["group"] == B["by_key"]["VIRGINIA_AVENUE"]["group"] == "PINK"
assert act(g, 136)[0] == "accept_trade" and g.resolved[136]["player_id"] == sol
before_s, before_g = set(owned(g, 136, sol)), set(owned(g, 136, grok))
after_s = (before_s - {"STATES_AVENUE"}) | {"VIRGINIA_AVENUE"}
after_g = (before_g - {"VIRGINIA_AVENUE"}) | {"STATES_AVENUE"}
assert complete_groups(after_s) == complete_groups(before_s) and complete_groups(after_g) == complete_groups(before_g)
t135 = texts(g.resolved[135])
assert '"name": "end_turn"' in t135["content"] and "Abort this trade. Do not send it." in t135["note"]
out["G19"] = {"turn": turn(g, 135), "terms": a, "both_pink": True, "accepted": True, "completes_group": False,
              "sol_orange_holdings": sorted(set(B["color_groups"]["ORANGE"]) & before_s),
              "false_message_in_sol_prompt_d136": "States is the third orange" in json.dumps(g.started[136]["prompt_payload"]),
              "sol_note_d136": g.resolved[136]["final_action"].get("private_thought")}
assert out["G19"]["false_message_in_sol_prompt_d136"]

# ------------------------------------------------------------------ the two failed sums and G12 Grok
g = G[12]
e = next(d for d in DEBT if d["game"] == 12 and d["first_decision"] == 190)
assert (e["cash"], e["salvage"], e["listed_mortgage"], e["unlisted_mortgage"], e["debt"]) == (53, 225, 130, 340, 500)
assert 53 + 225 + 130 == 408 and 408 + 340 >= 500
g17 = next(d for d in DEBT if d["game"] == 17 and d["first_decision"] == 234)
assert (g17["cash"], g17["salvage"], g17["listed_mortgage"], g17["unlisted_mortgage"], g17["debt"]) == (0, 500, 30, 375, 550)
gg = next(d for d in DEBT if d["game"] == 12 and d["first_decision"] == 249)
assert gg["model"] == "Grok" and gg["debt"] == 250 and gg["cash"] == 43 and gg["tier"] == "sales" and gg["first_action"] == "declare_bankruptcy"
t249 = texts(G[12].resolved[249])
assert '"name": "sell_houses_or_hotel"' in t249["content"]
out["failed_sums"] = {"G12_d190": {"stated_max": 408, "omitted": 340, "debt": 500, "witness": e["inherited_witness_steps"]},
                      "G17_d234": {"stated_max": 530, "omitted": 375, "debt": 550, "witness": g17["inherited_witness_steps"]},
                      "G12_d249": {"debt": 250, "cash": 43, "salvage": gg["salvage"], "witness": gg["inherited_witness_steps"]}}

# ------------------------------------------------------------------ further assertions for amounts typed in the text
ep20 = next(d for d in DEBT if d["game"] == 20 and d["first_decision"] == 327)
assert ep20["listed_mortgage"] == 325 and ep20["unlisted_mortgage"] == 340 and len(ep20["unlisted_mortgages_used"]) == 5 and len(ep20["listed_keys"]) == 3
assert out["G20_payment"]["sol_eliminated_later"] - out["G20_payment"]["turns"]["d327"] == 7
g18 = out["G18"]
assert g18["turns"] == {"d431": 187, "d441": 188, "d442": 188} and [186, 750] in g18["sol_to_opus_rents"] and [188, 750] in g18["sol_to_opus_rents"]
assert [419, 181, 200] in g18["pacific_offers_opus_positive_sol_negative"] and [421, 181, 250] in g18["pacific_offers_opus_positive_sol_negative"]
assert [453, 194, 150] in g18["pacific_offers_opus_positive_sol_negative"] and [455, 194, 225] in g18["pacific_offers_opus_positive_sol_negative"]
assert [u[0] for u in g18["opus_unmortgages_after_withdrawal"][:2]] == [190, 192] and g18["sol_eliminated_turn"] == 197
g7 = out["G7"]
assert 84 + 700 - 3 * 200 == 184 and 745 - 700 == 45 and g7["gemini_houses_turn_68"] == 4 and g7["gemini_mortgages_turn_68"] == 5
assert g7["sol_houses_within_8_turns"] == 3 and g7["gemini_orange_rent"] == 270 and g7["gemini_eliminated"] == [125, "Sol"] and g7["sol_houses_built_turn_67"] == 3
assert G[7].started[143]["turn_index"] == 68 and act(G[7], 143)[1]["offer"]["cash"] == 520 and act(G[7], 144)[1]["request"]["cash"] == 700
assert act(G[7], 138)[0] == "accept_trade" and act(G[7], 137)[1]["request"]["cash"] == 800 and act(G[7], 137)[1]["request"]["properties"] == ["STATES_AVENUE"]
g20a = out["G20_appeal"]
assert g20a["illinois_sale"]["turn"] == 22 and g20a["illinois_sale"]["if_you_accept"]["you_give"]["cash"] == 500 and g20a["grok_cash_after"] == 222
assert turn(G[20], 96) == 25 and turn(G[20], 100) == 27 and g20a["opus_later_offers_to_grok"][0][:3] == [129, 37, 140]
assert out["G19"]["turn"] == 67 and out["G15"]["grok_rejections"] == [169, 173, 175]
assert out["G2"]["sol_house_built_events"] == 2 and out["G2"]["sol_house_sold_events"] == 2
assert out["G13"]["opening_delivered_to_opus_at"] == 251 and out["G13"]["counter_delivered_to_opus_at"] == 253
ep7 = next(d for d in DEBT if d["game"] == 7 and d["first_decision"] == 338)
assert (ep7["cash"], ep7["listed_mortgage"], ep7["debt"], ep7["menu_has_sale"]) == (290, 150, 750, False)

write_json("b5_incidents.json", out)
print(json.dumps(out, indent=1, ensure_ascii=False))
