"""Check the factual statements made around the eight incidents against canonical records.

Each check reads decision prompts, applied actions or events directly.  The
script asserts what the manuscript states and writes the observed values.
"""
from __future__ import annotations

import json

from corpus import OUT, board, load_all, write_json
from state_track import Tracker

B = board()
G = load_all()
EPS = json.loads((OUT / "a3_group_episodes.json").read_text())
DEBT = json.loads((OUT / "a4_debt_episodes.json").read_text())
DY = json.loads((OUT / "a6_dyads.json").read_text())
out = {}


def cash(g, k, pid=None):
    st = g.started[k]["prompt_payload"]["game_state"]
    if pid is None or pid == st["you"]["player_id"]:
        return st["you"]["cash"]
    return next(o["cash"] for o in st["others"] if o["player_id"] == pid)


def act(g, k):
    fa = g.resolved[k]["final_action"]
    return fa["action"], fa.get("args") or {}


def elim(gn, model):
    g = G[gn]
    return next(d for d in DEBT if d["game"] == gn and d["outcome"] == "eliminated" and d["model"] == model)


def episode(gn, model, group):
    return [e for e in EPS if e["game"] == gn and e["model"] == model and e["group"] == group]


def events(g, typ, **kw):
    res = []
    for e in g.events:
        if e["type"] != typ:
            continue
        p = e["payload"]
        if all(p.get(k) == v for k, v in kw.items()):
            res.append(e)
    return res


# ---------------- G2
g = G[2]
sol, opus, grok, gem = (g.pid_of[m] for m in ("Sol", "Opus", "Grok", "Gemini"))
c = {}
c["d119_sol_cash"] = cash(g, 119); assert c["d119_sol_cash"] == 137
assert act(g, 119)[1]["request"]["cash"] == 450 and act(g, 121)[0] == "reject_trade"
assert act(g, 124)[1]["request"]["cash"] == 650 and act(g, 126)[1]["request"]["cash"] == 600
assert act(g, 127)[1]["offer"]["cash"] == 450 and act(g, 128)[0] == "reject_trade"
assert g.started[118]["turn_index"] == 44 and g.started[124]["turn_index"] == 45 and g.started[197]["turn_index"] == 69
assert cash(g, 196) == 435 and cash(g, 197) == 17 and act(g, 198)[0] == "accept_trade"
eo = elim(2, "Opus"); es = elim(2, "Sol")
assert eo["turn"] == 72 and eo["debt"] == 1300 and eo["creditor"] == gem
assert es["turn"] == 85 and es["creditor"] == gem and g.winner == "Gemini"
ep = episode(2, "Sol", "YELLOW")[0]
c["sol_yellow"] = {k: ep[k] for k in ("start_turn", "houses_bought", "build_spend", "rent", "developed_rent", "end_turn")}
sold = [e for e in g.events if e["type"] == "HOUSE_SOLD" and e["payload"]["player_id"] == sol]
c["sol_house_sales_turns"] = sorted({e["turn_index"] for e in sold}); assert 73 in c["sol_house_sales_turns"]
assert ep["houses_bought"] == 2
out["G2"] = c

# ---------------- G15
g = G[15]
sol, grok, gem = g.pid_of["Sol"], g.pid_of["Grok"], g.pid_of["Gemini"]
assert g.started[168]["turn_index"] == 63 and cash(g, 168) == 730 and cash(g, 169) == 333
assert [act(g, k)[0] for k in (169, 173, 175)] == ["reject_trade"] * 3 and act(g, 171)[0] == "reject_trade"
eg = elim(15, "Grok"); assert eg["turn"] == 81 and eg["creditor"] == gem and g.winner == "Gemini"
first = min((d for d in DEBT if d["game"] == 15 and d["outcome"] == "eliminated"), key=lambda d: d["first_decision"]); assert first["model"] == "Grok"
assert not episode(15, "Sol", "YELLOW") and not episode(15, "Sol", "GREEN")
out["G15"] = {"turn": 63, "grok_eliminated_turn": 81, "sol_yellow_or_green_episodes": 0}

# ---------------- G1
g = G[1]
opus, grok, gem = g.pid_of["Opus"], g.pid_of["Grok"], g.pid_of["Gemini"]
assert cash(g, 306) == 18 and act(g, 306)[1]["request"]["cash"] == 150 and act(g, 307)[1]["offer"]["cash"] == 50
assert act(g, 308)[1]["request"]["cash"] == 100 and act(g, 309)[0] == "accept_trade" and g.started[306]["turn_index"] == 122
ep = episode(1, "Grok", "DARK_BLUE")[0]
assert (ep["start_turn"], ep["duration_turns"], ep["landings"], ep["rent"], ep["houses_bought"]) == (122, 94, 5, 70, 0)
eo = elim(1, "Opus"); assert eo["turn"] == 126 and eo["debt"] == 550 and eo["creditor"] == gem and g.winner == "Gemini"
d = next(d for d in DY if d["game"] == 1 and d["group"] == "DARK_BLUE" and d["holder_model"] == "Opus" and d["completer_model"] == "Grok")
assert (d["first_turn"], d["first_holder_cash"], d["settle_holder_cash"]) == (69, 453, 18)
assert B["by_key"]["BOARDWALK"]["price"] == 400
out["G1"] = {"sale_price": 100, "list": 400, "first_request_turn": 69, "first_holder_cash": 453, "sale_turn": 122, "episode": [94, 5, 70]}

# ---------------- G13
g = G[13]
opus, grok, sol = g.pid_of["Opus"], g.pid_of["Grok"], g.pid_of["Sol"]
st = g.started[250]["prompt_payload"]["game_state"]["you"]
assert st["cash"] == 35 and st["position"] == "ATLANTIC_AVENUE" and g.started[250]["turn_index"] == 107
own = {h["space_key"]: h for h in st["holdings"]["owned"]}
assert not own["VENTNOR_AVENUE"]["mortgaged"] and own["PENNSYLVANIA_AVENUE"]["mortgaged"] and B["by_key"]["VENTNOR_AVENUE"]["mortgage"] == 130
assert {"ATLANTIC_AVENUE", "VENTNOR_AVENUE", "MARVIN_GARDENS"} <= set(own)
assert act(g, 251)[1]["offer"]["cash"] == 130 and act(g, 252)[1]["request"]["cash"] == 200 and act(g, 253)[0] == "accept_trade"
interest = [e for e in g.events if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE_INTEREST" and e["turn_index"] == 107]
assert interest and interest[0]["payload"]["delta"] == -16 and interest[0]["payload"]["player_id"] == opus
auc = [e for e in g.events if e["type"] == "AUCTION_ENDED" and e["payload"]["property_space"] == "NORTH_CAROLINA_AVENUE"]
assert auc[0]["payload"]["winner_player_id"] == opus and auc[0]["payload"]["winning_bid"] == 650 and auc[0]["turn_index"] == 114
ep = episode(13, "Opus", "GREEN"); assert ep and ep[0]["start_turn"] == 114
moves = [e for e in g.events if e["type"] == "PLAYER_MOVED" and e["actor"]["player_id"] == grok and e["turn_index"] > 107]
assert B["by_key"]["SHORT_LINE"]["index"] == 35 and moves[0]["payload"]["to"] != 35
rent_bo = [e for e in g.events if e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == grok and e["payload"]["space_index"] == 25 and e["turn_index"] == 146]
assert rent_bo and rent_bo[0]["payload"]["amount"] == 200
eg = elim(13, "Grok"); assert eg["turn"] == 150 and eg["creditor"] == sol and eg["debt"] == 200
assert g.started[eg["first_decision"]]["prompt_payload"]["game_state"]["you"]["position"] == "SHORT_LINE"
# distance Atlantic (26) -> Short Line (35) = 9
assert 35 - 26 == 9 and g.winner == "Opus"
out["G13"] = {"grok_next_square": moves[0]["payload"]["to"], "opus_green_complete_turn": 114, "grok_eliminated_turn": 150}

# ---------------- G18
g = G[18]
opus, sol = g.pid_of["Opus"], g.pid_of["Sol"]
c = {"d431_turn": g.started[431]["turn_index"], "d441_turn": g.started[441]["turn_index"], "d441_sol_cash": cash(g, 441), "d442_action": act(g, 442)[0]}
a441 = act(g, 441)
c["d441"] = a441
# earlier Opus offers of $250 for Pacific
offers = []
for k in range(g.n_decisions):
    r = g.resolved[k]
    a, args = act(g, k)
    if a in ("propose_trade", "counter_trade") and r["player_id"] == opus:
        if "PACIFIC_AVENUE" in (args.get("request", {}).get("properties") or []):
            offers.append([k, g.started[k]["turn_index"], args["offer"]["cash"]])
    if a in ("propose_trade", "counter_trade") and r["player_id"] == sol:
        if "PACIFIC_AVENUE" in (args.get("offer", {}).get("properties") or []):
            offers.append([k, g.started[k]["turn_index"], -args["request"]["cash"]])
c["pacific_offers_opus_positive_sol_negative"] = offers
c["opus_unmortgages"] = [[e["turn_index"], B["by_index"][e["payload"]["space_index"]]["key"]] for e in events(g, "PROPERTY_UNMORTGAGED", player_id=opus) if e["turn_index"] >= 185]
rents = [[e["turn_index"], e["payload"]["amount"]] for e in g.events if e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == sol and e["payload"]["to_player_id"] == opus and e["turn_index"] >= 175]
c["sol_to_opus_rents"] = rents
es = elim(18, "Sol"); c["sol_elim"] = [es["turn"], g.model[es["creditor"]]]; assert es["creditor"] == opus and g.winner == "Opus"
pac_trades = [e for e in g.events if e["type"] == "PROPERTY_TRANSFERRED" and e["payload"]["space_index"] == 31]
c["pacific_ever_traded"] = len(pac_trades)
out["G18"] = c

# ---------------- G20
g = G[20]
grok, gem, opus, sol = (g.pid_of[m] for m in ("Grok", "Gemini", "Opus", "Sol"))
c = {}
ep = episode(20, "Grok", "RED")[0]; c["red_start_turn"] = ep["start_turn"]; c["grok_cash_after"] = ep["cash_at_start"]
tr_acc = [e for e in g.events if e["type"] == "TRADE_ACCEPTED" and e["turn_index"] == ep["start_turn"]]
c["red_trade"] = tr_acc[0]["payload"] if tr_acc else None
assert B["by_key"]["ILLINOIS_AVENUE"]["house_cost"] == 150
assert act(g, 98)[0] == "build_houses_or_hotel" and act(g, 100)[1]["request"]["cash"] == 150 and act(g, 101)[0] == "reject_trade"
assert act(g, 102) == ("mortgage_property", {"space_key": "VERMONT_AVENUE"})
c["attempts_d97"] = [(a.get("response_condition"), a.get("outcome")) for a in g.resolved[97]["attempts"]]
later = []
for k in range(103, g.n_decisions):
    a, args = act(g, k)
    if g.resolved[k]["player_id"] == opus and a in ("propose_trade",) and args.get("to_player_id") == grok:
        later.append([k, g.started[k]["turn_index"], args["offer"], args["request"]])
c["opus_offers_to_grok_after"] = later
c["winner"] = g.winner; assert g.winner == "Gemini"
out["G20"] = c

# ---------------- G12
g = G[12]
grok, opus = g.pid_of["Grok"], g.pid_of["Opus"]
st = g.started[249]["prompt_payload"]["game_state"]["you"]
own = {h["space_key"]: h for h in st["holdings"]["owned"]}
c = {"cash": st["cash"], "pinks": {k: own[k]["houses"] for k in ("ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE")}}
sc = g.started[249]["prompt_payload"]["action_state"]["scenario"]
assert sc["owed_amount"] == 250 and st["cash"] == 43 and sc["owed_to_player_id"] == opus and act(g, 249)[0] == "declare_bankruptcy"
c["content_names_sale"] = '"name": "sell_houses_or_hotel"' in g.resolved[249]["attempts"][0]["assistant_content"]
assert c["content_names_sale"]
c["two_house_sale_reaches"] = 43 + 2 * 50
out["G12"] = c

# ---------------- G7
g = G[7]
sol, gem, grok, opus = (g.pid_of[m] for m in ("Sol", "Gemini", "Grok", "Opus"))
c = {}
assert g.started[39]["turn_index"] == 25 and cash(g, 39) == 1150 and act(g, 39)[1]["request"]["cash"] == 650
assert act(g, 42)[1]["offer"]["cash"] == 600 and act(g, 43)[0] == "accept_trade" and B["by_key"]["NORTH_CAROLINA_AVENUE"]["price"] == 300
assert act(g, 138)[0] == "accept_trade" and g.started[138]["turn_index"] == 67 and cash(g, 139) == 684 and cash(g, 140) == 84
assert act(g, 141)[1]["offer"]["cash"] == 350 and act(g, 142)[1]["request"]["cash"] == 700 and act(g, 145)[0] == "accept_trade" and g.started[145]["turn_index"] == 68
assert B["by_key"]["NEW_YORK_AVENUE"]["price"] == 200
built_after = [e for e in g.events if e["type"] in ("HOUSE_BUILT", "HOTEL_BUILT") and e["payload"]["player_id"] == sol and 68 <= e["turn_index"] <= 76 and e["seq"] > g.resolved[145]["emitted_event_seq_end"]]
c["sol_houses_built_within_8_turns_after_sale"] = sum(e["payload"].get("count", 1) for e in built_after)
ep = episode(7, "Gemini", "ORANGE")[0]; c["gemini_orange"] = {k: ep[k] for k in ("start_turn", "rent", "houses_bought", "end_reason", "end_turn")}
gem_builds_t68 = sum(e["payload"].get("count", 1) for e in g.events if e["type"] == "HOUSE_BUILT" and e["payload"]["player_id"] == gem and e["turn_index"] == 68)
c["gemini_houses_turn_68"] = gem_builds_t68
gem_mort_t68 = len([e for e in events(g, "PROPERTY_MORTGAGED", player_id=gem) if e["turn_index"] == 68]); c["gemini_mortgages_turn_68"] = gem_mort_t68
eg = elim(7, "Grok"); c["grok_elim"] = [eg["turn"], eg["debt"], g.model[eg["creditor"]]]
ege = elim(7, "Gemini"); c["gemini_elim"] = [ege["turn"], ege["debt"], g.model[ege["creditor"]]]
assert g.winner == "Sol"
out["G7"] = c

# ---------------- G17
g = G[17]
gem, sol = g.pid_of["Gemini"], g.pid_of["Sol"]
eg = elim(17, "Gemini")
st = g.started[eg["first_decision"]]["prompt_payload"]["game_state"]["you"]
c = {"turn": eg["turn"], "debt": eg["debt"], "cash": st["cash"], "creditor": g.model[eg["creditor"]], "class": eg["inherited_class"], "bound": eg["bound_U"],
     "houses": {h["space_key"]: (5 if h["hotel"] else h["houses"]) for h in st["holdings"]["owned"] if h["houses"] or h["hotel"]}, "deeds": len(st["holdings"]["owned"])}
assert eg["debt"] == 550 and st["cash"] == 0 and eg["creditor"] == sol and eg["inherited_class"] == "payable_witness" and g.winner == "Sol"
out["G17"] = c

write_json("a9_incident_checks.json", out)
print(json.dumps(out, indent=1))
