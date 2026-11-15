"""Bargaining tabulations: prices, responses by cash, blocking dyads and fates.

Everything here is fresh arithmetic on the rebuilt offer ledger
(``a2_offer_ledger.json``), the rebuilt group episodes and the debt episodes.
Definitions are written out next to each block.  Offers are dependent within
threads, dyads and games, so the script reports counts, medians, per-block
sign counts and leave-one-seed-block-out ranges, and no offer-level tests.
"""
from __future__ import annotations

import collections
import json
import re
import statistics as S

from corpus import MODELS, OUT, board, load_all, write_json

B = board()
ROWS = [r for r in json.loads((OUT / "a2_offer_ledger.json").read_text())]
LEGAL = [r for r in ROWS if r["accept_available"]]
EPS = json.loads((OUT / "a3_group_episodes.json").read_text())
DEBT = json.loads((OUT / "a4_debt_episodes.json").read_text())
STRATA = ["<100", "100-299", "300-599", "600+"]


def strat(c: int) -> str:
    return "<100" if c < 100 else ("100-299" if c < 300 else ("300-599" if c < 600 else "600+"))


def med(xs, nd=3):
    xs = list(xs)
    return {"median": round(S.median(xs), nd) if xs else None, "n": len(xs)}


def acr(xs) -> dict:
    c = collections.Counter(r["response"] for r in xs)
    n = len(xs)
    return {
        "n": n,
        "accept": c["accept_trade"],
        "counter": c["counter_trade"],
        "reject": c["reject_trade"],
        "reject_share": round(c["reject_trade"] / n, 4) if n else None,
        "accept_share": round(c["accept_trade"] / n, 4) if n else None,
    }


# ---------------------------------------------------------------------------
# 1. Pure cash-for-deed offers
# ---------------------------------------------------------------------------
def pure_offers() -> list[dict]:
    out = []
    for r in LEGAL:
        ag, rg = r["author_gives"], r["recipient_gives"]
        if ag["get_out_of_jail_cards"] or rg["get_out_of_jail_cards"]:
            continue
        if ag["properties"] and not rg["properties"] and rg["cash"] > 0 and ag["cash"] == 0:
            kind, deeds, cash, mort = "ask", ag["properties"], rg["cash"], r["author_gives_mortgaged"]
            seller, buyer = "author", "recipient"
        elif rg["properties"] and not ag["properties"] and ag["cash"] > 0 and rg["cash"] == 0:
            kind, deeds, cash, mort = "bid", rg["properties"], ag["cash"], r["recipient_gives_mortgaged"]
            seller, buyer = "recipient", "author"
        else:
            continue
        lst = sum(B["by_key"][d]["price"] for d in deeds)
        p = {
            "game": r["game"],
            "block": r["block"],
            "decision": r["decision"],
            "turn": r["turn"],
            "thread_id": r["thread_id"],
            "kind": kind,
            "opening": r["opening"],
            "deeds": deeds,
            "cash": cash,
            "list": lst,
            "ratio": cash / lst,
            "mstat": "unmortgaged" if not mort else ("mortgaged" if len(mort) == len(deeds) else "mixed"),
            "seller": r[seller],
            "buyer": r[buyer],
            "seller_model": r[seller + "_model"],
            "buyer_model": r[buyer + "_model"],
            "seller_cash": r[seller + "_cash_before"],
            "buyer_cash": r[buyer + "_cash_before"],
            "buyer_completes": bool(r[buyer + "_new_groups"]),
            "response": r["response"],
        }
        if len(deeds) == 1:
            d = deeds[0]
            grp = B["by_key"][d]["group"]
            ks = B["groups"][grp]
            bh = sum(1 for k in ks if k in r[buyer + "_holdings_before"])
            p.update({"group": grp, "group_size": len(ks), "buyer_has": bh, "missing_after": len(ks) - bh - 1,
                      "color": grp not in ("RAILROAD", "UTILITY")})
        out.append(p)
    return out


def price_tables(P: list[dict]) -> dict:
    asks = [p for p in P if p["kind"] == "ask"]
    bids = [p for p in P if p["kind"] == "bid"]
    out: dict = {"n_pure": len(P), "n_asks": len(asks), "n_bids": len(bids)}
    out["pooled"] = {
        "ask_completes": med(p["ratio"] for p in asks if p["buyer_completes"]),
        "ask_other": med(p["ratio"] for p in asks if not p["buyer_completes"]),
        "bid_completes": med(p["ratio"] for p in bids if p["buyer_completes"]),
        "bid_other": med(p["ratio"] for p in bids if not p["buyer_completes"]),
    }
    cells = {}
    for kind, xs, who in (("ask", asks, "seller_model"), ("bid", bids, "buyer_model")):
        for m in MODELS:
            for ms in ("unmortgaged", "mortgaged"):
                a = [p["ratio"] for p in xs if p[who] == m and p["mstat"] == ms and p["buyer_completes"]]
                b = [p["ratio"] for p in xs if p[who] == m and p["mstat"] == ms and not p["buyer_completes"]]
                cells[f"{kind}|{m}|{ms}"] = {"completes": med(a), "other": med(b)}
    out["by_author_and_mortgage"] = cells
    comp = {"ask": {"higher": 0, "lower": 0, "equal": 0, "cells": []}, "bid": {"higher": 0, "lower": 0, "equal": 0, "cells": []}}
    for k, v in cells.items():
        kind = k.split("|")[0]
        a, b = v["completes"], v["other"]
        if a["n"] >= 3 and b["n"] >= 3:
            sign = "higher" if a["median"] > b["median"] else ("lower" if a["median"] < b["median"] else "equal")
            comp[kind][sign] += 1
            comp[kind]["cells"].append(k)
    out["cells_with_at_least_3_each"] = comp
    out["by_stage_and_mortgage"] = {
        f"{kind}|{'opening' if st else 'later'}|{ms}": {
            "completes": med(p["ratio"] for p in xs if p["opening"] == st and p["mstat"] == ms and p["buyer_completes"]),
            "other": med(p["ratio"] for p in xs if p["opening"] == st and p["mstat"] == ms and not p["buyer_completes"]),
        }
        for kind, xs in (("ask", asks), ("bid", bids))
        for st in (True, False)
        for ms in ("unmortgaged", "mortgaged")
    }
    out["ask_by_seller_cash_and_mortgage"] = {
        f"{ms}|{s}": {
            "completes": med(p["ratio"] for p in asks if p["mstat"] == ms and strat(p["seller_cash"]) == s and p["buyer_completes"]),
            "other": med(p["ratio"] for p in asks if p["mstat"] == ms and strat(p["seller_cash"]) == s and not p["buyer_completes"]),
        }
        for ms in ("unmortgaged", "mortgaged")
        for s in STRATA
    }
    # distance to a monopoly after the trade (single colour deed)
    grad = {}
    for kind, xs in (("ask", asks), ("bid", bids)):
        for ms in ("unmortgaged", "mortgaged"):
            for miss in (2, 1, 0):
                sel = [p for p in xs if p.get("color") and p["mstat"] == ms and p["missing_after"] == miss]
                grad[f"{kind}|{ms}|missing_after={miss}"] = med(p["ratio"] for p in sel)
        for m in MODELS:
            who = "seller_model" if kind == "ask" else "buyer_model"
            for miss in (2, 1, 0):
                sel = [p for p in xs if p.get("color") and p["mstat"] == "unmortgaged" and p["missing_after"] == miss and p[who] == m]
                grad[f"{kind}|unmortgaged|{m}|missing_after={miss}"] = med(p["ratio"] for p in sel)
    out["gradient_single_color_deed"] = grad
    # leave-one-seed-block-out for the unmortgaged ask contrast
    lobo = {}
    for b in range(1, 6):
        a = [p["ratio"] for p in asks if p["block"] != b and p["mstat"] == "unmortgaged" and p["buyer_completes"]]
        c = [p["ratio"] for p in asks if p["block"] != b and p["mstat"] == "unmortgaged" and not p["buyer_completes"]]
        lobo[b] = [round(S.median(a), 3), round(S.median(c), 3)]
    out["ask_unmortgaged_leave_one_block_out"] = lobo
    per_block = {}
    for b in range(1, 6):
        a = [p["ratio"] for p in asks if p["block"] == b and p["mstat"] == "unmortgaged" and p["buyer_completes"]]
        c = [p["ratio"] for p in asks if p["block"] == b and p["mstat"] == "unmortgaged" and not p["buyer_completes"]]
        per_block[b] = {"completes": med(a), "other": med(c)}
    out["ask_unmortgaged_per_block"] = per_block
    # same game / seller / deed
    grp = collections.defaultdict(list)
    for p in asks:
        if len(p["deeds"]) == 1:
            grp[(p["game"], p["seller"], p["deeds"][0])].append(p)
    pairs = []
    for (game, seller, deed), v in sorted(grp.items()):
        c = [p for p in v if p["buyer_completes"]]
        nc = [p for p in v if not p["buyer_completes"]]
        if not c or not nc:
            continue
        mc, mn = S.median(p["cash"] for p in c), S.median(p["cash"] for p in nc)
        pairs.append(
            {
                "game": game,
                "seller_model": v[0]["seller_model"],
                "deed": deed,
                "completing_asks": [[p["decision"], p["turn"], p["cash"], p["mstat"], p["seller_cash"], p["buyer_model"]] for p in sorted(c, key=lambda p: p["decision"])],
                "other_asks": [[p["decision"], p["turn"], p["cash"], p["mstat"], p["seller_cash"], p["buyer_model"]] for p in sorted(nc, key=lambda p: p["decision"])],
                "median_completing": mc,
                "median_other": mn,
                "first_completing": min(c, key=lambda p: p["decision"])["cash"],
                "direction_by_median": "higher" if mc > mn else ("lower" if mc < mn else "equal"),
            }
        )
    out["same_game_seller_deed_pairs"] = pairs
    out["same_game_seller_deed_direction"] = dict(collections.Counter(p["direction_by_median"] for p in pairs))
    # deed-matched cells across the cohort (deed key x mortgage status)
    dm = collections.defaultdict(lambda: {"c": [], "n": []})
    for p in asks:
        if len(p["deeds"]) == 1 and p["mstat"] in ("unmortgaged", "mortgaged"):
            dm[(p["deeds"][0], p["mstat"])]["c" if p["buyer_completes"] else "n"].append(p["ratio"])
    signs = collections.Counter()
    for k, v in dm.items():
        if v["c"] and v["n"]:
            a, b = S.median(v["c"]), S.median(v["n"])
            signs["higher" if a > b else ("lower" if a < b else "equal")] += 1
    out["deed_and_mortgage_matched_cells"] = dict(signs)
    return out


# ---------------------------------------------------------------------------
# 2. Counter repricing (re-derived)
# ---------------------------------------------------------------------------
def counters() -> dict:
    by_thread = collections.defaultdict(list)
    for r in ROWS:
        by_thread[r["thread_id"]].append(r)
    res = {}
    for cellname, pred in (
        ("author_only", lambda r: r["completion_cell"] == "author_only"),
        ("neither_with_deed_request", lambda r: r["completion_cell"] == "neither" and r["recipient_gives"]["properties"]),
    ):
        n = keep = same_more = 0
        for tid, xs in by_thread.items():
            xs.sort(key=lambda r: r["exchange_index"])
            for a, b in zip(xs, xs[1:]):
                if a["response"] != "counter_trade" or not a["accept_available"] or not pred(a):
                    continue
                assert b["author"] == a["recipient"] and b["exchange_index"] == a["exchange_index"] + 1
                n += 1
                # original author's requested deeds = a.recipient_gives; in b the counterer is the author
                kept = set(a["recipient_gives"]["properties"]) <= set(b["author_gives"]["properties"])
                keep += kept
                same_noncash = (
                    sorted(a["recipient_gives"]["properties"]) == sorted(b["author_gives"]["properties"])
                    and sorted(a["author_gives"]["properties"]) == sorted(b["recipient_gives"]["properties"])
                    and a["recipient_gives"]["get_out_of_jail_cards"] == b["author_gives"]["get_out_of_jail_cards"]
                    and a["author_gives"]["get_out_of_jail_cards"] == b["recipient_gives"]["get_out_of_jail_cards"]
                )
                # net cash to the counterer: before = a.net author->recipient ; after = -(b.net author->recipient)
                more = (-b["net_cash_author_to_recipient"]) > a["net_cash_author_to_recipient"]
                same_more += same_noncash and more
        res[cellname] = {"counters": n, "all_requested_deeds_retained": keep, "same_noncash_bundle_more_cash_to_counterer": same_more}
    return res


# ---------------------------------------------------------------------------
# 3. Responses of deed holders by cash
# ---------------------------------------------------------------------------
def holder_cash() -> dict:
    ao = [r for r in LEGAL if r["completion_cell"] == "author_only"]
    ne = [r for r in LEGAL if r["completion_cell"] == "neither" and r["recipient_gives"]["properties"]]
    out = {
        "definition": "author_only: acceptance-legal offers under which only the author would complete a colour group; the recipient holds the completing deed(s). "
        "Cash is the recipient's cash in the delivered state before responding.",
        "author_only_by_holder_cash": {s: acr([r for r in ao if strat(r["recipient_cash_before"]) == s]) for s in STRATA},
        "other_deed_requests_by_holder_cash": {s: acr([r for r in ne if strat(r["recipient_cash_before"]) == s]) for s in STRATA},
        "author_only_by_recipient_and_cash": {
            f"{m}|{s}": acr([r for r in ao if r["recipient_model"] == m and f(r["recipient_cash_before"])])
            for m in MODELS
            for s, f in (("<100", lambda c: c < 100), ("100-299", lambda c: 100 <= c < 300), ("300+", lambda c: c >= 300))
        },
    }

    def gap(sample):
        lo = [r for r in sample if r["recipient_cash_before"] < 100]
        hi = [r for r in sample if r["recipient_cash_before"] >= 300]
        if not lo or not hi:
            return None
        return {
            "low": [sum(r["response"] == "reject_trade" for r in lo), len(lo)],
            "high": [sum(r["response"] == "reject_trade" for r in hi), len(hi)],
            "gap_points": round(100 * (sum(r["response"] == "reject_trade" for r in hi) / len(hi) - sum(r["response"] == "reject_trade" for r in lo) / len(lo)), 1),
        }

    out["reject_gap_under100_vs_300plus"] = {
        "all": gap(ao),
        "per_block": {b: gap([r for r in ao if r["block"] == b]) for b in range(1, 6)},
        "leave_one_block_out": {b: gap([r for r in ao if r["block"] != b]) for b in range(1, 6)},
        "excluding_opus_recipients": gap([r for r in ao if r["recipient_model"] != "Opus"]),
        "excluding_opus_either_side": gap([r for r in ao if r["recipient_model"] != "Opus" and r["author_model"] != "Opus"]),
        "opening_only": gap([r for r in ao if r["opening"]]),
        "later_only": gap([r for r in ao if not r["opening"]]),
        "other_deed_requests": gap(ne),
    }
    games_with_both = 0
    games_lower = 0
    for gnum in range(1, 21):
        gp = gap([r for r in ao if r["game"] == gnum])
        if gp:
            games_with_both += 1
            games_lower += gp["gap_points"] > 0
    out["reject_gap_games_with_both_strata"] = [games_lower, games_with_both]
    # who is asked: share of deed requests aimed at holders under $100
    req = [r for r in LEGAL if r["recipient_gives"]["properties"]]
    out["requests_aimed_at_holders_under_100"] = {
        cell: [sum(1 for r in req if r["completion_cell"] == cell and r["recipient_cash_before"] < 100), sum(1 for r in req if r["completion_cell"] == cell)]
        for cell in ("author_only", "neither", "both", "recipient_only")
    }
    out["opening_requests_aimed_at_holders_under_100"] = {
        cell: [sum(1 for r in req if r["opening"] and r["completion_cell"] == cell and r["recipient_cash_before"] < 100), sum(1 for r in req if r["opening"] and r["completion_cell"] == cell)]
        for cell in ("author_only", "neither")
    }
    return out


# ---------------------------------------------------------------------------
# 4. Blocking dyads
# ---------------------------------------------------------------------------
def dyads() -> tuple[list[dict], dict]:
    games = load_all()
    dy: dict = collections.OrderedDict()
    for r in LEGAL:
        for role, other in (("author", "recipient"), ("recipient", "author")):
            for grp in r[role + "_new_groups"]:
                k = (r["game"], r[role], r[other], grp)
                d = dy.setdefault(
                    k,
                    {"game": r["game"], "block": r["block"], "completer": r[role], "holder": r[other], "group": grp,
                     "completer_model": r[role + "_model"], "holder_model": r[other + "_model"], "requests": []},
                )
                net_to_holder = r["net_cash_author_to_recipient"] if role == "author" else -r["net_cash_author_to_recipient"]
                d["requests"].append(
                    {"decision": r["decision"], "turn": r["turn"], "thread_id": r["thread_id"], "completer_role": role, "response": r["response"],
                     "written_by": "completer" if role == "author" else "holder",
                     "cell": r["completion_cell"], "holder_cash": r[other + "_cash_before"], "completer_cash": r[role + "_cash_before"],
                     "net_cash_to_holder": net_to_holder}
                )
    ep_by = collections.defaultdict(list)
    for e in EPS:
        ep_by[(e["game"], e["group"])].append(e)
    elim = {(d["game"], d["player"]): d for d in DEBT if d["outcome"] == "eliminated"}
    rows = []
    for k, d in dy.items():
        rq = d["requests"]
        acc = [x for x in rq if x["response"] == "accept_trade"]
        d["n_requests"] = len(rq)
        d["n_threads"] = len({x["thread_id"] for x in rq})
        d["settled"] = bool(acc)
        d["first_turn"], d["first_holder_cash"] = rq[0]["turn"], rq[0]["holder_cash"]
        d["last_turn"], d["last_holder_cash"] = rq[-1]["turn"], rq[-1]["holder_cash"]
        d["min_holder_cash"] = min(x["holder_cash"] for x in rq)
        if acc:
            a = acc[0]
            d["settle_turn"], d["settle_holder_cash"], d["settle_completer_cash"] = a["turn"], a["holder_cash"], a["completer_cash"]
            d["settle_cell"] = a["cell"]
            d["settle_decision"] = a["decision"]
            d["settle_net_cash_to_holder"] = a["net_cash_to_holder"]
            d["one_sided"] = a["cell"] != "both"
            d["settled_on_later_turn"] = a["turn"] > rq[0]["turn"]
            earlier = [x for x in rq if x["turn"] < a["turn"]]
            # the holder declined a request written by the completer (rejected or countered it)
            hd = [x for x in earlier if x["written_by"] == "completer" and x["response"] != "accept_trade"]
            # the completer declined terms written by the holder
            cd = [x for x in earlier if x["written_by"] == "holder" and x["response"] != "accept_trade"]
            d["holder_declined_on_earlier_turn"] = bool(hd)
            d["completer_declined_on_earlier_turn"] = bool(cd)
            if hd:
                d["first_holder_decline_turn"] = hd[0]["turn"]
                d["first_holder_decline_cash"] = hd[0]["holder_cash"]
        else:
            later = [e for e in ep_by[(d["game"], d["group"])] if e["start_turn"] >= d["first_turn"]]
            later.sort(key=lambda e: e["start_seq"])
            if not later:
                d["fate"] = "group never completed"
            else:
                e = later[0]
                who = "same would-be completer" if e["player"] == d["completer"] else "another player"
                d["fate"] = f"{who} via {e['route_detail']}"
                d["fate_route"] = e["route_detail"]
                d["fate_same_completer"] = e["player"] == d["completer"]
        # what happened to the holder
        he = elim.get((d["game"], d["holder"]))
        d["holder_eliminated_turn"] = he["turn"] if he else None
        d["holder_eliminated_by_completer"] = bool(he and he["creditor"] == d["completer"])
        rows.append(d)
    settled = [d for d in rows if d["settled"]]
    one = [d for d in settled if d["one_sided"]]
    mut = [d for d in settled if not d["one_sided"]]
    uns = [d for d in rows if not d["settled"]]
    later_one = [d for d in one if d["settled_on_later_turn"]]
    later_mut = [d for d in mut if d["settled_on_later_turn"]]

    def change(xs):
        ch = [d["settle_holder_cash"] - d["first_holder_cash"] for d in xs]
        return {
            "n": len(xs),
            "lower": sum(c < 0 for c in ch),
            "higher": sum(c > 0 for c in ch),
            "equal": sum(c == 0 for c in ch),
            "median_first": S.median(d["first_holder_cash"] for d in xs) if xs else None,
            "median_settle": S.median(d["settle_holder_cash"] for d in xs) if xs else None,
            "by_holder_model": dict(collections.Counter(d["holder_model"] for d in xs)),
            "lower_by_holder_model": dict(collections.Counter(d["holder_model"] for d in xs if d["settle_holder_cash"] < d["first_holder_cash"])),
        }

    uns_multi = [d for d in uns if d["last_turn"] > d["first_turn"]]
    # seller fate after one-sided sale: rent paid on the sold group to the buyer; elimination on it
    idx_group = {r["index"]: r["group"] for r in B["by_index"].values()}
    pos_group = {}
    for g in games.values():
        pass
    seller_fate = []
    for d in one:
        g = games[d["game"]]
        rent_paid = 0
        for e in g.events:
            if e["turn_index"] < d["settle_turn"]:
                continue
            if e["type"] == "RENT_PAID":
                p = e["payload"]
                if p["from_player_id"] == d["holder"] and p["to_player_id"] == d["completer"] and idx_group.get(p["space_index"]) == d["group"]:
                    rent_paid += p["amount"]
        he = elim.get((d["game"], d["holder"]))
        lethal = False
        if he and he["creditor"] == d["completer"] and he["reason"] == "RENT":
            pos = g.started[he["first_decision"]]["prompt_payload"]["game_state"]["you"]["position"]
            lethal = B["by_key"].get(pos, {}).get("group") == d["group"]
        seller_fate.append(
            {"game": d["game"], "group": d["group"], "holder_model": d["holder_model"], "completer_model": d["completer_model"],
             "settle_turn": d["settle_turn"], "holder_cash_at_sale": d["settle_holder_cash"], "rent_later_paid_on_group_to_buyer": rent_paid,
             "holder_eliminated_turn": he["turn"] if he else None, "eliminated_by_buyer": bool(he and he["creditor"] == d["completer"]),
             "eliminated_on_sold_group": lethal, "holder_won": g.winner_pid == d["holder"], "completer_won": g.winner_pid == d["completer"]}
        )
    summary = {
        "definition": "A blocking dyad is (game, would-be completer, holder, colour group) with at least one acceptance-legal offer under which the completer "
        "would newly hold the whole group using deed(s) from the holder. An offer completing a group for each party contributes two dyads.",
        "dyads": len(rows),
        "request_instances": sum(d["n_requests"] for d in rows),
        "settled": len(settled),
        "settled_one_sided": len(one),
        "settled_mutual": len(mut),
        "unsettled": len(uns),
        "settled_by_holder_model": {m: [sum(d["settled"] for d in rows if d["holder_model"] == m), sum(1 for d in rows if d["holder_model"] == m)] for m in MODELS},
        "settled_by_completer_model": {m: [sum(d["settled"] for d in rows if d["completer_model"] == m), sum(1 for d in rows if d["completer_model"] == m)] for m in MODELS},
        "settled_by_block": {b: [sum(d["settled"] for d in rows if d["block"] == b), sum(1 for d in rows if d["block"] == b)] for b in range(1, 6)},
        "settled_same_turn_as_first_request": sum(1 for d in settled if not d["settled_on_later_turn"]),
        "settled_later_turn": sum(1 for d in settled if d["settled_on_later_turn"]),
        "median_turns_to_settle_when_later": S.median(d["settle_turn"] - d["first_turn"] for d in settled if d["settled_on_later_turn"]),
        "one_sided_holder_cash_at_settlement": {s: sum(1 for d in one if strat(d["settle_holder_cash"]) == s) for s in STRATA},
        "one_sided_holder_cash_median": S.median(d["settle_holder_cash"] for d in one),
        "one_sided_under_100_by_holder_model": dict(collections.Counter(d["holder_model"] for d in one if d["settle_holder_cash"] < 100)),
        "one_sided_by_holder_model": dict(collections.Counter(d["holder_model"] for d in one)),
        "mutual_holder_cash_at_settlement": {s: sum(1 for d in mut if strat(d["settle_holder_cash"]) == s) for s in STRATA},
        "mutual_holder_cash_median": S.median(d["settle_holder_cash"] for d in mut),
        "within_dyad_one_sided_later_turn": change(later_one),
        "within_dyad_one_sided_later_turn_excluding_opus_holders": change([d for d in later_one if d["holder_model"] != "Opus"]),
        "within_dyad_mutual_later_turn": change(later_mut),
        "later_one_sided_holder_declined_earlier": sum(1 for d in later_one if d["holder_declined_on_earlier_turn"]),
        "later_one_sided_only_completer_declined_earlier": sum(1 for d in later_one if not d["holder_declined_on_earlier_turn"] and d["completer_declined_on_earlier_turn"]),
        "from_first_holder_decline": (lambda xs: {
            "n": len(xs),
            "lower": sum(d["settle_holder_cash"] < d["first_holder_decline_cash"] for d in xs),
            "higher": sum(d["settle_holder_cash"] > d["first_holder_decline_cash"] for d in xs),
            "equal": sum(d["settle_holder_cash"] == d["first_holder_decline_cash"] for d in xs),
            "median_at_decline": S.median(d["first_holder_decline_cash"] for d in xs),
            "median_at_settlement": S.median(d["settle_holder_cash"] for d in xs),
            "by_holder_model": dict(collections.Counter(d["holder_model"] for d in xs)),
            "lower_excluding_opus_holders": [sum(d["settle_holder_cash"] < d["first_holder_decline_cash"] for d in xs if d["holder_model"] != "Opus"), sum(1 for d in xs if d["holder_model"] != "Opus")],
        })([d for d in later_one if d["holder_declined_on_earlier_turn"]]),
        "unsettled_multi_turn": {
            "n": len(uns_multi),
            "holder_cash_lower_at_last": sum(d["last_holder_cash"] < d["first_holder_cash"] for d in uns_multi),
            "higher": sum(d["last_holder_cash"] > d["first_holder_cash"] for d in uns_multi),
            "median_first": S.median(d["first_holder_cash"] for d in uns_multi),
            "median_last": S.median(d["last_holder_cash"] for d in uns_multi),
        },
        "unsettled_min_holder_cash_under_100": [sum(d["min_holder_cash"] < 100 for d in uns), len(uns)],
        "unsettled_fates": dict(collections.Counter(d["fate"] for d in uns)),
        "unsettled_resolved_by_estate": sum(1 for d in uns if "estate" in d.get("fate", "")),
        "unsettled_resolved_by_nonterminal_estate": sum(1 for d in uns if d.get("fate_route") == "nonterminal_estate"),
        "unsettled_same_completer_via_estate": sum(1 for d in uns if d.get("fate_same_completer") and "estate" in d.get("fate_route", "")),
        "unsettled_same_completer_via_nonterminal_estate": sum(1 for d in uns if d.get("fate_same_completer") and d.get("fate_route") == "nonterminal_estate"),
        "seller_fate_one_sided": {
            "n": len(seller_fate),
            "seller_later_paid_rent_on_sold_group": sum(1 for s in seller_fate if s["rent_later_paid_on_group_to_buyer"] > 0),
            "rent_total": sum(s["rent_later_paid_on_group_to_buyer"] for s in seller_fate),
            "seller_eliminated": sum(1 for s in seller_fate if s["holder_eliminated_turn"] is not None),
            "seller_eliminated_by_buyer": sum(1 for s in seller_fate if s["eliminated_by_buyer"]),
            "seller_eliminated_on_sold_group": sum(1 for s in seller_fate if s["eliminated_on_sold_group"]),
            "seller_won": sum(1 for s in seller_fate if s["holder_won"]),
            "buyer_won": sum(1 for s in seller_fate if s["completer_won"]),
            "under_100_sellers": sum(1 for s in seller_fate if s["holder_cash_at_sale"] < 100),
            "under_100_seller_eliminated": sum(1 for s in seller_fate if s["holder_cash_at_sale"] < 100 and s["holder_eliminated_turn"] is not None),
            "under_100_seller_median_turns_to_elimination": S.median(
                s["holder_eliminated_turn"] - s["settle_turn"] for s in seller_fate if s["holder_cash_at_sale"] < 100 and s["holder_eliminated_turn"] is not None
            ),
            "other_seller_median_turns_to_elimination": S.median(
                s["holder_eliminated_turn"] - s["settle_turn"] for s in seller_fate if s["holder_cash_at_sale"] >= 100 and s["holder_eliminated_turn"] is not None
            ),
            "under_100_seller_won": sum(1 for s in seller_fate if s["holder_cash_at_sale"] < 100 and s["holder_won"]),
        },
    }
    # one-sided pure-cash settlement prices
    by_key = {(r["game"], r["decision"]): r for r in ROWS}
    price_rows = []
    for d in one:
        r = by_key[(d["game"], d["settle_decision"])]
        ag, rg = r["author_gives"], r["recipient_gives"]
        if ag["get_out_of_jail_cards"] or rg["get_out_of_jail_cards"]:
            continue
        # which side is the holder
        if r["author"] == d["holder"]:
            deeds, cash, other_deeds, other_cash, mort = ag["properties"], rg["cash"], rg["properties"], ag["cash"], r["author_gives_mortgaged"]
        else:
            deeds, cash, other_deeds, other_cash, mort = rg["properties"], ag["cash"], ag["properties"], rg["cash"], r["recipient_gives_mortgaged"]
        if other_deeds or other_cash or cash <= 0:
            continue
        price_rows.append(
            {"game": d["game"], "decision": d["settle_decision"], "holder_model": d["holder_model"], "holder_cash": d["settle_holder_cash"],
             "ratio": round(cash / sum(B["by_key"][x]["price"] for x in deeds), 3), "cash": cash,
             "mstat": "unmortgaged" if not mort else ("mortgaged" if len(mort) == len(deeds) else "mixed")}
        )
    summary["one_sided_pure_cash_settlements"] = {
        "n": len(price_rows),
        "under_100_opus": med((p["ratio"] for p in price_rows if p["holder_cash"] < 100 and p["holder_model"] == "Opus"), 2),
        "under_100_other": med((p["ratio"] for p in price_rows if p["holder_cash"] < 100 and p["holder_model"] != "Opus"), 2),
        "100_plus_opus": med((p["ratio"] for p in price_rows if p["holder_cash"] >= 100 and p["holder_model"] == "Opus"), 2),
        "100_plus_other": med((p["ratio"] for p in price_rows if p["holder_cash"] >= 100 and p["holder_model"] != "Opus"), 2),
        "rows": price_rows,
    }
    summary["seller_fate_rows"] = seller_fate
    return rows, summary


# ---------------------------------------------------------------------------
# 5. Grok content/call conflicts (fresh parse) and sensitivity
# ---------------------------------------------------------------------------
NAME_RE = re.compile(r'"name"\s*:\s*"([a-z_]+)"')


def grok_conflicts() -> dict:
    games = load_all()
    conflicts = set()
    named = 0
    for g in games.values():
        pid = g.pid_of["Grok"]
        for k in range(g.n_decisions):
            r = g.resolved[k]
            if r["player_id"] != pid:
                continue
            # the selected attempt is the last valid one
            sel = None
            for a in r["attempts"]:
                if a.get("outcome") == "valid":
                    sel = a
            if sel is None:
                continue
            content = sel.get("assistant_content")
            if not content:
                continue
            m = NAME_RE.search(content)
            if not m:
                continue
            named += 1
            if m.group(1) != (sel.get("parsed_tool_call") or {}).get("name"):
                conflicts.add((g.number, k))
    return {"named": named, "conflicts": conflicts}


def sensitivity(conf: set) -> dict:
    by_thread = collections.defaultdict(list)
    for r in ROWS:
        by_thread[r["thread_id"]].append(r)
    games = load_all()
    # threads opened by a conflicting Grok proposal: the proposing decision precedes the first response
    opened_conf = set()
    for tid, xs in by_thread.items():
        xs.sort(key=lambda r: r["exchange_index"])
        first = xs[0]
        g = games[first["game"]]
        # find the propose decision: the latest decision before first['decision'] by the author that is propose_trade
        k = first["decision"] - 1
        while k >= 0 and not (g.resolved[k]["player_id"] == first["author"] and g.resolved[k]["final_action"]["action"] == "propose_trade"):
            k -= 1
        if (first["game"], k) in conf:
            opened_conf.add(tid)
    resp_conf = {(r["game"], r["decision"]) for r in ROWS if (r["game"], r["decision"]) in conf}
    counter_author_conf = set()
    # counters authored by Grok with a conflict: the row whose response is the conflicting counter produces the next offer
    for tid, xs in by_thread.items():
        for a, b in zip(xs, xs[1:]):
            if (a["game"], a["decision"]) in conf and a["response"] == "counter_trade":
                counter_author_conf.add((b["game"], b["decision"]))
    clean = [r for r in LEGAL if r["thread_id"] not in opened_conf and (r["game"], r["decision"]) not in resp_conf and (r["game"], r["decision"]) not in counter_author_conf]
    ao = [r for r in clean if r["completion_cell"] == "author_only"]
    lo = [r for r in ao if r["recipient_cash_before"] < 100]
    hi = [r for r in ao if r["recipient_cash_before"] >= 300]
    cells = {c: acr([r for r in clean if r["completion_cell"] == c]) for c in ("author_only", "recipient_only", "both", "neither")}
    return {
        "threads_opened_by_conflicting_grok_call": len(opened_conf),
        "of_grok_threads": sum(1 for tid, xs in by_thread.items() if xs[0]["author_model"] == "Grok"),
        "conflict_opened_threads_settled": sum(1 for tid in opened_conf if any(r["response"] == "accept_trade" for r in by_thread[tid])),
        "responses_with_conflict": len(resp_conf),
        "responses_with_conflict_by_action": dict(collections.Counter(r["response"] for r in ROWS if (r["game"], r["decision"]) in resp_conf)),
        "legal_offers_after_exclusion": len(clean),
        "cells_after_exclusion": cells,
        "reject_under100_vs_300plus_after_exclusion": {
            "low": [sum(r["response"] == "reject_trade" for r in lo), len(lo)],
            "high": [sum(r["response"] == "reject_trade" for r in hi), len(hi)],
        },
    }


# ---------------------------------------------------------------------------
# 6. Census tables
# ---------------------------------------------------------------------------
def census() -> dict:
    out = {
        "responses_all": acr(ROWS),
        "legal": len(LEGAL),
        "cells": {c: acr([r for r in LEGAL if r["completion_cell"] == c]) for c in ("author_only", "recipient_only", "both", "neither")},
        "cells_by_stage": {
            f"{c}|{'opening' if st else 'later'}": acr([r for r in LEGAL if r["completion_cell"] == c and r["opening"] == st])
            for c in ("author_only", "recipient_only", "both", "neither")
            for st in (True, False)
        },
        "by_recipient": {m: acr([r for r in ROWS if r["recipient_model"] == m]) for m in MODELS},
        "joint_recipient_stage_cell": {
            f"{m}|{'opening' if st else 'later'}|{c}": acr([r for r in LEGAL if r["recipient_model"] == m and r["opening"] == st and r["completion_cell"] == c])
            for m in MODELS
            for st in (True, False)
            for c in ("author_only", "recipient_only", "both", "neither")
        },
        "threads": len({r["thread_id"] for r in ROWS}),
        "threads_by_initiator": dict(collections.Counter(r["author_model"] for r in ROWS if r["opening"])),
        "threads_settled": len({r["thread_id"] for r in ROWS if r["response"] == "accept_trade"}),
        "settled_on_opening_offer": sum(1 for r in ROWS if r["response"] == "accept_trade" and r["opening"]),
    }
    # repeated openings: same initiator, same counterparty, same deed bundle on both sides earlier in the game
    seen = collections.defaultdict(set)
    rep = collections.Counter()
    rep_cash = collections.Counter()
    for r in sorted(ROWS, key=lambda r: (r["game"], r["decision"])):
        if not r["opening"]:
            continue
        k = (r["game"], r["author"], r["recipient"])
        bundle = (tuple(sorted(r["author_gives"]["properties"])), tuple(sorted(r["recipient_gives"]["properties"])))
        full = bundle + (r["author_gives"]["cash"], r["recipient_gives"]["cash"])
        if bundle in {b[:2] for b in seen[k]}:
            rep[r["author_model"]] += 1
            if full in seen[k]:
                rep_cash[r["author_model"]] += 1
        seen[k].add(full)
    out["repeated_opening_bundles"] = dict(rep)
    out["repeated_opening_bundles_same_cash"] = dict(rep_cash)
    return out


def main() -> None:
    P = pure_offers()
    prices = price_tables(P)
    ctr = counters()
    hc = holder_cash()
    dy_rows, dy_summary = dyads()
    gc = grok_conflicts()
    sens = sensitivity(gc["conflicts"])
    sens["grok_selected_content_names"] = gc["named"]
    sens["grok_selected_conflicts"] = len(gc["conflicts"])
    cen = census()
    write_json("a6_pure_offers.json", P)
    write_json("a6_dyads.json", dy_rows)
    out = {"census": cen, "prices": prices, "counters": ctr, "holder_cash": hc, "dyads": dy_summary, "grok_sensitivity": sens}
    write_json("a6_bargaining.json", out)
    brief = json.loads(json.dumps(out))
    brief["dyads"].pop("seller_fate_rows", None)
    brief["dyads"]["one_sided_pure_cash_settlements"].pop("rows", None)
    brief["prices"].pop("same_game_seller_deed_pairs", None)
    brief["census"].pop("joint_recipient_stage_cell", None)
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
