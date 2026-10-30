"""Render a compact, chronological reading copy of one game from public_review.

Usage: python3 -I render.py GAME [CHAR_BUDGET_PER_PAGE]
Writes reading/gXX/pNNN.txt.  #N is the 1-based source line in game-XX.jsonl.
This is preparation only; semantic review is done by reading the pages.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

TYPE_SHORT = {
    "POST_TURN_ACTION_DECISION": "POST",
    "TRADE_RESPONSE_DECISION": "TRESP",
    "AUCTION_BID_DECISION": "AUCT",
    "BUY_OR_AUCTION_DECISION": "BUY?",
    "LIQUIDATION_DECISION": "LIQ",
    "JAIL_DECISION": "JAIL",
}
SKIP_CASH = {"RENT", "buy_property", "MORTGAGE", "UNMORTGAGE", "auction_bid"}


def ev_str(e):
    t = e["type"]
    p = e["payload"]
    a = e["actor"].get("player_id")
    if t == "DICE_ROLLED":
        return "%s rolls %d+%d%s" % (a, p["d1"], p["d2"], " DBL" if p["is_double"] else "")
    if t == "PLAYER_MOVED":
        return "%s->%s%s" % (a, sk(IDX2KEY.get(p["to"], str(p["to"]))), " (passGO)" if p.get("passed_go") else "")
    if t == "RENT_PAID":
        return "RENT %s>%s $%d @%s" % (p["from_player_id"], p["to_player_id"], p["amount"], sk(IDX2KEY.get(p["space_index"], p["space_index"])))
    if t == "CASH_CHANGED":
        r = p["reason"]
        if r in SKIP_CASH:
            return None
        if r == "PASS_GO":
            return "GO %s+%d" % (p["player_id"], p["delta"])
        return "$%s %+d %s" % (p["player_id"], p["delta"], r)
    if t == "PROPERTY_PURCHASED":
        return "BUY %s %s $%d" % (p["player_id"], sk(IDX2KEY[p["space_index"]]), p["price"])
    if t == "PROPERTY_TRANSFERRED":
        return "XFER %s %s>%s%s" % (sk(IDX2KEY[p["space_index"]]), p["from_player_id"], p["to_player_id"], " [mortgaged]" if p.get("mortgaged") else "")
    if t == "TRADE_ACCEPTED":
        return "TRADE-ACCEPTED idx%d init=%s" % (p["exchange_index"], p["initiator_player_id"])
    if t == "CARD_DRAWN":
        return "CARD %s %s:%s" % (a, p["deck_type"][:2], p["card_id"])
    if t == "SENT_TO_JAIL":
        return "JAILED %s (%s)" % (p["player_id"], p["reason"])
    if t == "AUCTION_STARTED":
        return "AUC-START by %s on %s" % (p["initiator_player_id"], sk(p["property_space"]))
    if t == "AUCTION_ENDED":
        return "AUC-END %s %s winner=%s bid=%s" % (sk(p["property_space"]), p["reason"], p.get("winner_player_id"), p.get("winning_bid"))
    if t == "HOUSE_BUILT":
        return "HOUSE+%d %s %s" % (p["count"], p["player_id"], sk(IDX2KEY[p["space_index"]]))
    if t == "HOTEL_BUILT":
        return "HOTEL %s %s" % (p["player_id"], sk(IDX2KEY[p["space_index"]]))
    if t == "HOUSE_SOLD":
        return "HOUSE-%d %s %s" % (p["count"], p["player_id"], sk(IDX2KEY[p["space_index"]]))
    if t == "HOTEL_SOLD":
        return "HOTEL-SOLD %s %s" % (p["player_id"], sk(IDX2KEY[p["space_index"]]))
    if t == "PROPERTY_MORTGAGED":
        return "MORT %s %s +$%d" % (p["player_id"], sk(IDX2KEY[p["space_index"]]), p["amount"])
    if t == "PROPERTY_UNMORTGAGED":
        return "UNMORT %s %s -$%d" % (p["player_id"], sk(IDX2KEY[p["space_index"]]), p["amount"])
    if t == "GAME_ENDED":
        return "GAME-ENDED %s winner=%s" % (p.get("reason"), p.get("winner_player_id"))
    if t == "GAME_STARTED":
        return "GAME-START"
    return None  # LLM_*, TURN_*, trade proposal/counter/reject (shown in action line), bids, drops


def hist_str(h):
    return " ; ".join("%s:%s>%s" % (x["from_player_id"], bundle_str(x["offer"]), bundle_str(x["request"])) for x in h)


def action_str(a):
    n = a["action"]
    args = a.get("args") or {}
    if n in ("propose_trade",):
        return "propose_trade to %s: OFFER %s for REQUEST %s" % (args["to_player_id"], bundle_str(args["offer"]), bundle_str(args["request"]))
    if n == "counter_trade":
        return "counter_trade: OFFER %s for REQUEST %s" % (bundle_str(args["offer"]), bundle_str(args["request"]))
    if n == "bid_auction":
        return "bid_auction $%d" % args["bid_amount"]
    if n in ("build_houses_or_hotel", "sell_houses_or_hotel"):
        plan = args.get("build_plan") or args.get("sell_plan") or []
        agg = {}
        for x in plan:
            key = (sk(x["space_key"]), x["kind"])
            agg[key] = agg.get(key, 0) + x["count"]
        return "%s %s" % (n, " ".join("%s%s%d" % (k[0], "+" if n[0] == "b" else "-", c) + ("" if k[1] == "HOUSE" else "(%s)" % k[1]) for k, c in agg.items()))
    if n in ("mortgage_property", "unmortgage_property"):
        return "%s %s" % (n, sk(args.get("space_key", "?")))
    return n if not args else "%s %s" % (n, args)


def ctx_str(r):
    s = r["action_state"].get("scenario") or {}
    dt = r["decision_type"]
    if dt == "BUY_OR_AUCTION_DECISION":
        av = r["action_state"]["available_actions"]
        return "land %s $%s grp=%s own %s/%s rent0=%s%s" % (sk(s["landed_space"]), s.get("price"), s.get("group"), s["group_progress"]["you_own_in_group"], s["group_progress"]["total_in_group"], s["rent"][0] if s.get("rent") else "-", "" if "buy_property" in av else "  [buy NOT legal: only %s]" % "/".join(av))
    if dt == "AUCTION_BID_DECISION":
        return "AUC %s hi=$%s leader=%s min=%s active=%s n=%s" % (sk(s["property_space"]), s["current_high_bid"], s["current_leader_player_id"], s["min_next_bid"], ",".join(s["active_bidders_player_ids"]), s["action_count"])
    if dt == "TRADE_RESPONSE_DECISION":
        co = s["current_offer"]
        ia = co["if_you_accept"]
        h = s.get("history") or []
        return "TRADE from %s idx%d (max %d): you GIVE %s / you GET %s%s" % (s["counterparty_player_id"], s["exchange_index"], s["max_exchanges"], bundle_str(ia["you_give"]), bundle_str(ia["you_receive"]), (" || hist: " + hist_str(h)) if h else "")
    if dt == "JAIL_DECISION":
        o = s["options"]
        return "jail fine=%s pay=%s roll=%s card=%s" % (s["jail_fine"], o["can_pay_fine"], o["can_roll_for_doubles"], o["can_use_jail_card"])
    if dt == "LIQUIDATION_DECISION":
        o = s["options"]
        return "OWES $%s to %s (%s) shortfall=$%s mortgageable=%s sellable=%s" % (s["owed_amount"], s.get("owed_to_player_id") or "BANK", s["reason"], s["shortfall"], ",".join(sk(x) for x in o["mortgageable_space_keys"]) or "-", ",".join(sk(x) for x in o["sellable_building_space_keys"]) or "-")
    if dt == "POST_TURN_ACTION_DECISION":
        o = s["options"]
        bits = []
        if o["buildable_space_keys"]:
            bits.append("buildable=" + ",".join(sk(x) for x in o["buildable_space_keys"]))
        if o["sellable_building_space_keys"]:
            bits.append("sellable=" + ",".join(sk(x) for x in o["sellable_building_space_keys"]))
        if o["unmortgageable_space_keys"]:
            bits.append("unmortgageable=" + ",".join(sk(x) for x in o["unmortgageable_space_keys"]))
        bits.append("mortgageable#%d" % len(o["mortgageable_space_keys"]))
        bits.append("trade_with=" + ",".join(o["can_trade_with"]))
        return " ".join(bits)
    return ""


def player_line(pid, pl, model):
    return "%s/%s $%d BV%d %s%s%s | %s" % (pid, model, pl["cash"], book_value(pl), "JAIL " if pl.get("in_jail") else "", "BANKRUPT " if pl.get("bankrupt") else "", ("GOOJ%d " % pl["get_out_of_jail_cards"]) if pl.get("get_out_of_jail_cards") else "", holdings_str(pl))


def render_game(g, budget=28000):
    rows = load_game(g)
    models = {}
    for r in rows:
        models[r["player_id"]] = MODEL_SHORT.get(r["model"], r["model"])
    outdir = "%s/reading/g%02d" % (OUT, g)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    pages = []
    cur = []
    cursize = 0
    page_first = None
    last_state = -100

    def flush():
        nonlocal cur, cursize
        if cur:
            pages.append(cur)
        cur = []
        cursize = 0

    for i, r in enumerate(rows):
        ln = i + 1
        obs = r["observation"]
        pl = all_players(obs)
        pid = r["player_id"]
        a = r["applied_action"]
        lines = []
        cash = " ".join("%s:%s%d" % (p, "*" if p == pid else "", pl[p]["cash"]) for p in sorted(pl))
        lines.append("#%d t%d %s/%s %s  $[%s]%s" % (ln, r["turn_index"], pid, models[pid], TYPE_SHORT[r["decision_type"]], cash,
                                                    "  JAILED:" + ",".join(p for p in sorted(pl) if pl[p].get("in_jail")) if any(pl[p].get("in_jail") for p in pl) else ""))
        # state checkpoint
        need_state = (ln - last_state >= 30) or not cur
        cp = None
        if r["decision_type"] == "TRADE_RESPONSE_DECISION":
            cp = r["action_state"]["scenario"]["counterparty_player_id"]
        elif a["action"] == "propose_trade":
            cp = a["args"]["to_player_id"]
        if need_state:
            lines.append("  STATE: " + " ## ".join(player_line(p, pl[p], models[p]) for p in sorted(pl)))
            last_state = ln
        elif cp or r["decision_type"] == "LIQUIDATION_DECISION" or a["action"] in ("build_houses_or_hotel", "sell_houses_or_hotel"):
            who = [pid]
            if cp:
                who.append(cp)
            if r["decision_type"] == "LIQUIDATION_DECISION":
                who.append(r["action_state"]["scenario"].get("owed_to_player_id") or pid)
            seen = []
            for w in who:
                if w in pl and w not in seen:
                    seen.append(w)
            lines.append("  H: " + " ## ".join(player_line(p, pl[p], models[p]) for p in seen))
        c = ctx_str(r)
        if c:
            lines.append("  ctx: " + c)
        # events, split around the decision
        pre, post = [], []
        seen_req = False
        for e in r["events"]:
            if e["type"] == "LLM_DECISION_REQUESTED":
                seen_req = True
                continue
            s = ev_str(e)
            if s:
                (post if seen_req else pre).append(s)
        if pre:
            lines.append("  pre: " + "; ".join(pre))
        att = r["attempt_metadata"]
        attn = ""
        if not (len(att) == 1 and att[0]["outcome"] == "valid" and att[0]["response_condition"] == "standard"):
            attn = "  [ATT " + ">".join("%s(%s)" % (x["outcome"], "std" if x["response_condition"] == "standard" else "nothought") for x in att) + (" FALLBACK" if r["fallback_used"] else "") + "]"
        lines.append("  > " + action_str(a) + attn)
        msg = a.get("public_message")
        lines.append("  \"%s\"" % msg if msg else "  (no public message)")
        if post:
            lines.append("  post: " + "; ".join(post))
        block = "\n".join(lines) + "\n"
        if cursize + len(block) > budget and cur:
            flush()
            # re-render with state header for new page (force)
            last_state = -100
            lines2 = lines[:]
            if not any(x.startswith("  STATE:") for x in lines2):
                lines2.insert(1, "  STATE: " + " ## ".join(player_line(p, pl[p], models[p]) for p in sorted(pl)))
                last_state = ln
            block = "\n".join(lines2) + "\n"
        cur.append((ln, block))
        cursize += len(block)
    flush()
    for pi, pg in enumerate(pages, 1):
        with open("%s/p%03d.txt" % (outdir, pi), "w") as f:
            f.write("# game %d page %d  decisions #%d..#%d  seats: %s\n\n" % (g, pi, pg[0][0], pg[-1][0], ", ".join("%s=%s" % (k, v) for k, v in sorted(models.items()))))
            for ln, b in pg:
                f.write(b)
    return len(pages), len(rows), sum(len(b) for pg in pages for _, b in pg)


if __name__ == "__main__":
    g = int(sys.argv[1])
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 28000
    print(render_game(g, budget))
