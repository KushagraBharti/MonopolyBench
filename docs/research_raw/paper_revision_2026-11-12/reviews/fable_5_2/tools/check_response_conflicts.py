#!/usr/bin/env python3
"""Channel conflicts on the response side, and secondary offer counts.

The four drafts report Grok's conflicting calls among its trade openings.
This script looks at the 920 responses: where the selected attempt's assistant
content names a tool other than the received call.  It also recomputes several
secondary counts that the drafts carry (counters that keep the bundle, holder
cash, proposer house capacity) from the offers rebuilt in ``check_offers``.

Stored records only.  No engine, replay or model query.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

import check_offers as C
from ro_corpus import MODELS, board, complete_groups, load_all, write_json

BK = board()["by_key"]
CG = board()["color_groups"]


def cnt(rs):
    c = Counter(r["response"] for r in rs)
    return [len(rs), c["accept_trade"], c["counter_trade"], c["reject_trade"]]


def gap(rs, f="swap"):
    a = [r for r in rs if r["form"] == f and r["cell"] == "author_only"]
    b = [r for r in rs if r["form"] == f and r["cell"] == "neither"]
    ra = sum(r["response"] == "reject_trade" for r in a)
    rb = sum(r["response"] == "reject_trade" for r in b)
    return [ra, len(a), rb, len(b), round(100 * (ra / len(a) - rb / len(b)), 1)]


def main():
    games = load_all()
    rows = C.build()
    for r in rows:
        g = games[r["game"]]
        r["recipient_conflict"] = bool(C.conflict(g, r["decision"]))
        if r["recipient_conflict"]:
            r["content_names"] = C.NAME_RE.search(g.selected_attempt(r["decision"])["assistant_content"]).group(1)
    legal = [r for r in rows if r["accept_available"]]
    opening = [r for r in legal if r["opening"]]
    conf = [r for r in rows if r["recipient_conflict"]]
    grok = [r for r in rows if r["recipient_model"] == "Grok"]
    out = {
        "recipient_conflicts_total": len(conf),
        "recipient_conflicts_by_model": dict(Counter(r["recipient_model"] for r in conf)),
        "applied_vs_named": {f"{a}|{b}": n for (a, b), n in Counter((r["response"], r["content_names"]) for r in conf).items()},
        "grok_acceptances": sum(r["response"] == "accept_trade" for r in grok),
        "grok_conflicted_acceptances": sum(r["response"] == "accept_trade" and r["recipient_conflict"] for r in grok),
        "gap_all": gap(opening),
        "gap_excl_recipient_conflicts": gap([r for r in opening if not r["recipient_conflict"]]),
        "gap_excl_any_conflict": gap([r for r in opening if not r["recipient_conflict"]
                                      and not (r["author_model"] == "Grok" and r["author_conflict"] is True)]),
        "cash_gap_all": gap(opening, "cash_bid"),
        "accepted_completing_openings": [
            {"game": r["game"], "decision": r["decision"], "form": r["form"], "author": r["author_model"],
             "recipient": r["recipient_model"], "recipient_conflict": r["recipient_conflict"],
             "content_names": r.get("content_names"), "recipient_cash": r["recipient_cash"]}
            for r in opening if r["cell"] == "author_only" and r["form"] in ("swap", "cash_bid")
            and r["response"] == "accept_trade"],
    }

    # all-system content/call conflicts over every decision
    named, conflict = Counter(), Counter()
    for g in games.values():
        for k in range(g.n):
            m = g.model[g.started[k]["player_id"]]
            c = C.conflict(g, k)
            if c is None:
                continue
            named[m] += 1
            conflict[m] += bool(c)
    out["content_names_an_action"] = dict(named)
    out["content_conflicts_with_call"] = dict(conflict)

    # counters that keep the non-cash bundle and raise the counterer's cash, all stages
    by_thread = defaultdict(dict)
    for r in rows:
        by_thread[r["thread"]][r["exchange_index"]] = r

    def same_more(r):
        nx = by_thread[r["thread"]].get(r["exchange_index"] + 1)
        if not nx:
            return None
        same = (sorted(nx["a_gives"]["properties"]) == sorted(r["r_gives"]["properties"])
                and sorted(nx["r_gives"]["properties"]) == sorted(r["a_gives"]["properties"])
                and nx["a_gives"]["get_out_of_jail_cards"] == r["r_gives"]["get_out_of_jail_cards"]
                and nx["r_gives"]["get_out_of_jail_cards"] == r["a_gives"]["get_out_of_jail_cards"])
        return same and (nx["r_gives"]["cash"] - nx["a_gives"]["cash"]) > (r["a_gives"]["cash"] - r["r_gives"]["cash"])

    def counters(sel):
        cs = [r for r in legal if sel(r) and r["response"] == "counter_trade"]
        return [sum(bool(same_more(r)) for r in cs), len(cs)]
    out["counters_same_bundle_more_cash"] = {
        "proposer_only_all_stages": counters(lambda r: r["cell"] == "author_only"),
        "neither_deed_requests_all_stages": counters(lambda r: r["cell"] == "neither" and bool(r["r_gives"]["properties"])),
    }

    # holder cash
    allpo = [r for r in legal if r["cell"] == "author_only"]
    out["holder_cash_all_stages_proposer_only"] = {
        "under_100": cnt([r for r in allpo if r["recipient_cash"] < 100]),
        "at_least_300": cnt([r for r in allpo if r["recipient_cash"] >= 300]),
        "by_recipient": {m: {"under_100": cnt([r for r in allpo if r["recipient_model"] == m and r["recipient_cash"] < 100]),
                             "at_least_300": cnt([r for r in allpo if r["recipient_model"] == m and r["recipient_cash"] >= 300])}
                         for m in MODELS},
    }
    non_opus = [r for r in opening if r["recipient_model"] != "Opus"]
    po = [r for r in non_opus if r["cell"] == "author_only"]
    nd = [r for r in non_opus if r["cell"] == "neither" and r["r_gives"]["properties"]]
    out["holder_cash_opening_to_sol_gemini_grok"] = {
        "proposer_only_under_100": cnt([r for r in po if r["recipient_cash"] < 100]),
        "proposer_only_at_least_300": cnt([r for r in po if r["recipient_cash"] >= 300]),
        "neither_deed_request_under_100": cnt([r for r in nd if r["recipient_cash"] < 100]),
        "neither_deed_request_at_least_300": cnt([r for r in nd if r["recipient_cash"] >= 300]),
    }

    # proposer house capacity after the trade
    def cap(r):
        h = games[r["game"]].holdings(r["decision"])
        a = set(h[r["author"]]["owned"])
        after = (a - set(r["a_gives"]["properties"])) | set(r["r_gives"]["properties"])
        new = complete_groups(after) - complete_groups(a)
        if not new:
            return None
        interest = sum(math.ceil(BK[p]["mortgage"] * 0.1) for p in r["r_gives"]["properties"]
                       if h[r["recipient"]]["owned"][p]["mortgaged"])
        cash = r["author_cash_after"] - interest
        return max(0, cash) // min(BK[CG[gp][0]]["house_cost"] for gp in new)

    def band(c):
        return "0" if c == 0 else "1-2" if c <= 2 else "3-5" if c <= 5 else "6+"
    capacity = {}
    for f in ("swap", "cash_bid"):
        t, rj = Counter(), Counter()
        for r in opening:
            if r["form"] == f and r["cell"] == "author_only":
                b = band(cap(r))
                t[b] += 1
                rj[b] += r["response"] == "reject_trade"
        capacity[f] = {b: [rj[b], t[b]] for b in ("0", "1-2", "3-5", "6+")}
    out["rejected_by_proposer_house_capacity"] = capacity

    write_json("check_recipient_conflicts.json", out)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
