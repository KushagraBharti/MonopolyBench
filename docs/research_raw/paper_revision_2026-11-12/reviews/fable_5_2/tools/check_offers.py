#!/usr/bin/env python3
"""Cross-review check of the offer claims, from stored records only.

Rebuilds every trade-response opportunity from raw ``TRADE_RESPONSE_DECISION``
records with code written for this review, compares it with the frozen offer
ledger, and recomputes the form x completion x stage table, the proposer and
recipient strata, the composition versions, proposer-standardized gaps,
per-block values and three kinds of resampling.

Resampling uses stored observations only.  No engine, replay or model query.
"""
from __future__ import annotations

import itertools
import json
import re
from collections import Counter, defaultdict

import numpy as np

from ro_corpus import MODELS, REVISION, board, complete_groups, load_all, write_json

NAME_RE = re.compile(r'"name"\s*:\s*"([a-z_]+)"')
CELLS = ["author_only", "recipient_only", "both", "neither"]
RESP = ["accept_trade", "counter_trade", "reject_trade"]
B = board()["by_key"]


def form(a, b):
    cards = a["get_out_of_jail_cards"] or b["get_out_of_jail_cards"]
    if a["properties"] and b["properties"]:
        return "swap"
    if b["properties"] and not a["properties"] and a["cash"] > 0 and b["cash"] == 0 and not cards:
        return "cash_bid"
    if a["properties"] and not b["properties"] and b["cash"] > 0 and a["cash"] == 0 and not cards:
        return "sale_offer"
    return "other"


def conflict(g, k):
    """Assistant content names a tool other than the received call (selected attempt)."""
    sel = g.selected_attempt(k)
    if sel is None:
        return None
    content = sel.get("assistant_content")
    if not content:
        return None
    m = NAME_RE.search(content)
    if not m:
        return None
    return m.group(1) != (sel.get("parsed_tool_call") or {}).get("name")


def build():
    rows = []
    for g in load_all().values():
        thread = 0
        for k in range(g.n):
            st = g.started[k]
            if st["decision_type"] != "TRADE_RESPONSE_DECISION":
                continue
            sc = st["prompt_payload"]["action_state"]["scenario"]
            cur = sc["current_offer"]
            recipient, author = st["player_id"], cur["from_player_id"]
            ex = sc["exchange_index"]
            if ex == 0:
                thread += 1
            r_gives = cur["if_you_accept"]["you_give"]
            a_gives = cur["if_you_accept"]["you_receive"]
            hold = g.holdings(k)
            a_keys, r_keys = set(hold[author]["owned"]), set(hold[recipient]["owned"])
            a_after = (a_keys - set(a_gives["properties"])) | set(r_gives["properties"])
            r_after = (r_keys - set(r_gives["properties"])) | set(a_gives["properties"])
            a_new = complete_groups(a_after) - complete_groups(a_keys)
            r_new = complete_groups(r_after) - complete_groups(r_keys)
            cell = ("both" if a_new and r_new else "author_only" if a_new
                    else "recipient_only" if r_new else "neither")
            # the decision that produced this offer: nearest earlier decision by the author
            # whose applied action is propose_trade (opening) or counter_trade (later)
            offer_dec = None
            for j in range(k - 1, -1, -1):
                if g.started[j]["player_id"] == author and g.resolved[j]["final_action"]["action"] in (
                        "propose_trade", "counter_trade"):
                    offer_dec = j
                    break
            a_cash_after = hold[author]["cash"] - a_gives["cash"] + r_gives["cash"]
            list_net = (a_gives["cash"] - r_gives["cash"]
                        + sum(B[p]["price"] for p in a_gives["properties"])
                        - sum(B[p]["price"] for p in r_gives["properties"]))
            rs = g.resolved[k]
            rows.append({
                "game": g.number, "block": g.block, "decision": k, "thread": f"G{g.number:02d}-T{thread:03d}",
                "exchange_index": ex, "opening": ex == 0,
                "author": author, "recipient": recipient,
                "author_model": g.model[author], "recipient_model": g.model[recipient],
                "response": rs["final_action"]["action"],
                "accept_available": "accept_trade" in st["prompt_payload"]["action_state"]["available_actions"],
                "form": form(a_gives, r_gives), "cell": cell,
                "offer_decision": offer_dec,
                "author_conflict": conflict(g, offer_dec) if offer_dec is not None else None,
                "recipient_cash": hold[recipient]["cash"], "author_cash_after": a_cash_after,
                "net_list_value_to_recipient": list_net,
                "a_gives": a_gives, "r_gives": r_gives,
                "response_condition": (rs.get("sequence_meta") or {}).get("response_condition"),
            })
    return rows


def cnt(rs):
    c = Counter(r["response"] for r in rs)
    return [len(rs), c["accept_trade"], c["counter_trade"], c["reject_trade"]]


def rej(rs, f, cell):
    sub = [r for r in rs if r["form"] == f and r["cell"] == cell]
    return sum(r["response"] == "reject_trade" for r in sub), len(sub)


def gap(rs, f="swap"):
    a, an = rej(rs, f, "author_only")
    b, bn = rej(rs, f, "neither")
    if not an or not bn:
        return None
    return 100 * (a / an - b / bn)


def pct(vals, q):
    return float(np.percentile(np.array(vals, dtype=float), q))


def resample(rows, f, keep):
    rows = [r for r in rows if keep(r)]
    by_game = defaultdict(list)
    for r in rows:
        if r["form"] == f and r["cell"] in ("author_only", "neither"):
            by_game[r["game"]].append(r)
    # per-game sufficient statistics: (rej_P, n_P, rej_N, n_N)
    stat = {}
    for gnum in range(1, 21):
        rs = by_game.get(gnum, [])
        stat[gnum] = np.array([
            sum(r["cell"] == "author_only" and r["response"] == "reject_trade" for r in rs),
            sum(r["cell"] == "author_only" for r in rs),
            sum(r["cell"] == "neither" and r["response"] == "reject_trade" for r in rs),
            sum(r["cell"] == "neither" for r in rs)], dtype=float)
    blocks = {b: [g for g in range(1, 21) if (g - 1) // 4 + 1 == b] for b in range(1, 6)}
    bstat = {b: sum(stat[g] for g in gs) for b, gs in blocks.items()}

    def g_of(s):
        if s[1] == 0 or s[3] == 0:
            return None
        return 100 * (s[0] / s[1] - s[2] / s[3])

    point = g_of(sum(stat.values()))
    per_block = {b: g_of(bstat[b]) for b in blocks}
    loo = [g_of(sum(bstat[b] for b in blocks if b != drop)) for drop in blocks]
    exact = [g_of(sum(bstat[b] for b in combo)) for combo in itertools.product(range(1, 6), repeat=5)]
    exact_ok = [x for x in exact if x is not None]
    rng = np.random.default_rng(20261112)
    games_only, two_stage = [], []
    for _ in range(20000):
        gs = rng.integers(1, 21, size=20)
        v = g_of(sum(stat[int(g)] for g in gs))
        if v is not None:
            games_only.append(v)
        bs = rng.integers(1, 6, size=5)
        tot = np.zeros(4)
        for b in bs:
            for g in rng.choice(blocks[int(b)], size=4, replace=True):
                tot += stat[int(g)]
        v = g_of(tot)
        if v is not None:
            two_stage.append(v)
    return {
        "point": round(point, 2) if point is not None else None,
        "per_block": {b: (round(v, 1) if v is not None else None) for b, v in per_block.items()},
        "per_block_counts": {b: [int(x) for x in bstat[b]] for b in blocks},
        "blocks_positive": int(sum(v is not None and v > 0 for v in per_block.values())),
        "leave_one_block_out": [round(min(loo), 1), round(max(loo), 1)],
        "block_exact_3125": {"undefined": len(exact) - len(exact_ok),
                             "p2.5_p97.5": [round(pct(exact_ok, 2.5), 1), round(pct(exact_ok, 97.5), 1)],
                             "min_max": [round(min(exact_ok), 1), round(max(exact_ok), 1)],
                             "share_below_zero": round(sum(x < 0 for x in exact_ok) / len(exact_ok), 4)},
        "games_only_20000": {"undefined": 20000 - len(games_only),
                             "p2.5_p97.5": [round(pct(games_only, 2.5), 1), round(pct(games_only, 97.5), 1)],
                             "share_below_zero": round(sum(x < 0 for x in games_only) / len(games_only), 4)},
        "two_stage_20000": {"undefined": 20000 - len(two_stage),
                            "p2.5_p97.5": [round(pct(two_stage, 2.5), 1), round(pct(two_stage, 97.5), 1)],
                            "share_below_zero": round(sum(x < 0 for x in two_stage) / len(two_stage), 4)},
    }


def main():
    rows = build()
    out = {"responses": len(rows), "threads": len({r["thread"] for r in rows})}
    out["responses_by_action"] = dict(Counter(r["response"] for r in rows))

    # --- reconcile with the frozen ledger (astra/data/offers.json == 11 November integrated ledger)
    led = json.loads((REVISION / "full_drafts/astra/data/offers.json").read_text())
    lk = {(r["game"], r["decision"]): r for r in led}
    mism = []
    for r in rows:
        l = lk.get((r["game"], r["decision"]))
        if l is None:
            mism.append([r["game"], r["decision"], "missing"])
            continue
        mine = (r["response"], r["cell"], r["exchange_index"], r["accept_available"],
                r["author_model"], r["recipient_model"], r["offer_decision"],
                form(r["a_gives"], r["r_gives"]) , r["author_cash_after"])
        theirs = (l["response"], l["completion_cell"], l["exchange_index"], l["accept_available"],
                  l["author_model"], l["recipient_model"], l["offer_decision"],
                  form(l["offer"], l["request"]), l["author_cash_if_accepted"] + l.get("author_interest_if_accepted", 0) * 0)
        if mine[:8] != theirs[:8]:
            mism.append([r["game"], r["decision"], mine[:8], theirs[:8]])
    out["ledger_rows"] = len(led)
    out["ledger_field_mismatches"] = mism[:20]
    out["ledger_field_mismatch_count"] = len(mism)

    legal = [r for r in rows if r["accept_available"]]
    out["acceptance_legal"] = len(legal)
    out["not_acceptance_legal"] = [[r["game"], r["decision"], r["response"], r["opening"]] for r in rows if not r["accept_available"]]
    opening = [r for r in legal if r["opening"]]
    later = [r for r in legal if not r["opening"]]
    out["opening"] = len(opening)
    out["later"] = len(later)
    out["by_recipient"] = {m: cnt([r for r in rows if r["recipient_model"] == m]) for m in MODELS}
    out["opus_recovery_trade_responses"] = sum(
        r["recipient_model"] == "Opus" and r["response_condition"] != "standard" for r in rows)

    def table(rs):
        return {f: {c: cnt([r for r in rs if r["form"] == f and r["cell"] == c]) for c in CELLS}
                for f in ("swap", "cash_bid", "sale_offer", "other")}
    out["table_opening"] = table(opening)
    out["table_later"] = table(later)

    # --- strata
    out["by_proposer"] = {m: {f: [list(rej([r for r in opening if r["author_model"] == m], f, c))
                                  for c in ("author_only", "neither")] for f in ("swap", "cash_bid")} for m in MODELS}
    out["by_recipient_strata"] = {m: {f: [list(rej([r for r in opening if r["recipient_model"] == m], f, c))
                                          for c in ("author_only", "neither")] for f in ("swap", "cash_bid")} for m in MODELS}
    pairs = {}
    for a in MODELS:
        for b in MODELS:
            if a == b:
                continue
            sub = [r for r in opening if r["author_model"] == a and r["recipient_model"] == b]
            p, pn = rej(sub, "swap", "author_only")
            q, qn = rej(sub, "swap", "neither")
            if pn and qn:
                pairs[f"{a}->{b}"] = {"proposer_only": [p, pn], "neither": [q, qn], "gap": round(100 * (p / pn - q / qn), 1)}
    out["author_recipient_swap_pairs"] = pairs
    out["author_recipient_pairs_positive"] = [sum(v["gap"] > 0 for v in pairs.values()), len(pairs)]

    # --- composition of the comparison cell
    comp = [r for r in opening if r["form"] == "swap" and r["cell"] == "neither"]
    acc = [r for r in comp if r["response"] == "accept_trade"]
    out["comparison_swaps"] = {
        "n": len(comp), "by_author": dict(Counter(r["author_model"] for r in comp)),
        "accepted": len(acc), "accepted_by_author": dict(Counter(r["author_model"] for r in acc)),
        "accepted_grok_conflict_openings": sum(r["author_model"] == "Grok" and r["author_conflict"] is True for r in acc),
        "accepted_grok_net_list_value": sum(r["net_list_value_to_recipient"] for r in acc if r["author_model"] == "Grok"),
    }
    grok_open = {(r["game"], r["thread"]) for r in rows if r["opening"] and r["author_model"] == "Grok"}
    grok_conf = {(r["game"], r["thread"]) for r in rows if r["opening"] and r["author_model"] == "Grok" and r["author_conflict"] is True}
    out["grok_openings"] = [len(grok_conf), len(grok_open)]
    conflict_threads = grok_conf

    versions = {
        "all": lambda r: True,
        "no_conflicting_grok_openings": lambda r: (r["game"], r["thread"]) not in conflict_threads,
        "no_grok_authored": lambda r: r["author_model"] != "Grok",
    }
    out["composition_versions"] = {}
    for name, keep in versions.items():
        sub = [r for r in opening if keep(r)]
        out["composition_versions"][name] = {
            f: {"proposer_only": list(rej(sub, f, "author_only")), "neither": list(rej(sub, f, "neither")),
                "gap": round(gap(sub, f), 2)} for f in ("swap", "cash_bid")}

    # --- proposer-standardized swap gap under three weightings
    gaps, wP, wN = {}, {}, {}
    for m in MODELS:
        sub = [r for r in opening if r["author_model"] == m]
        p, pn = rej(sub, "swap", "author_only")
        q, qn = rej(sub, "swap", "neither")
        gaps[m] = (p / pn - q / qn) * 100 if pn and qn else None
        wP[m], wN[m] = pn, qn
    def std(w):
        tot = sum(w[m] for m in MODELS if gaps[m] is not None)
        return round(sum(w[m] * gaps[m] for m in MODELS if gaps[m] is not None) / tot, 1)
    out["within_proposer_swap_gaps"] = {m: (round(v, 1) if v is not None else None) for m, v in gaps.items()}
    out["standardized_swap_gap"] = {
        "weights_proposer_only_cell": std(wP), "weights_neither_cell": std(wN),
        "weights_pooled": std({m: wP[m] + wN[m] for m in MODELS})}

    # --- resampling under three units
    out["resampling"] = {}
    for name, keep in versions.items():
        out["resampling"][name] = {f: resample(opening, f, keep) for f in ("swap", "cash_bid")}

    # --- counters
    def counters(f):
        sub = [r for r in opening if r["form"] == f and r["cell"] == "author_only"]
        return [sum(r["response"] == "counter_trade" for r in sub), len(sub)]
    out["counter_share_proposer_only"] = {"cash_bid": counters("cash_bid"), "swap": counters("swap")}
    # What do counters to completing cash bids change?  Compare with the next offer in the thread.
    nxt = {}
    by_thread = defaultdict(list)
    for r in rows:
        by_thread[r["thread"]].append(r)
    same_more = 0
    total = 0
    for r in opening:
        if r["form"] == "cash_bid" and r["cell"] == "author_only" and r["response"] == "counter_trade":
            total += 1
            seq = sorted(by_thread[r["thread"]], key=lambda x: x["exchange_index"])
            follow = [x for x in seq if x["exchange_index"] == r["exchange_index"] + 1]
            if not follow:
                continue
            x = follow[0]   # authored by the original recipient
            same_deeds = (sorted(x["a_gives"]["properties"]) == sorted(r["r_gives"]["properties"])
                          and sorted(x["r_gives"]["properties"]) == sorted(r["a_gives"]["properties"])
                          and x["a_gives"]["get_out_of_jail_cards"] == r["r_gives"]["get_out_of_jail_cards"]
                          and x["r_gives"]["get_out_of_jail_cards"] == r["a_gives"]["get_out_of_jail_cards"])
            more_cash = (x["r_gives"]["cash"] - x["a_gives"]["cash"]) > (r["a_gives"]["cash"] - r["r_gives"]["cash"])
            same_more += same_deeds and more_cash
    out["cash_bid_counters_same_deeds_more_cash"] = [same_more, total]

    # --- acceptance of completing openings
    po = [r for r in opening if r["cell"] == "author_only" and r["form"] in ("swap", "cash_bid")]
    nei = [r for r in opening if r["cell"] == "neither" and r["form"] in ("swap", "cash_bid")]
    out["completing_openings_swap_or_cash_bid"] = cnt(po)
    out["neither_openings_swap_or_cash_bid"] = cnt(nei)
    out["completing_openings_accepted_rows"] = [
        [r["game"], r["decision"], r["form"], r["author_model"], r["recipient_model"], r["recipient_cash"]]
        for r in po if r["response"] == "accept_trade"]

    # --- holder cash (all stages, offers completing only the proposer)
    allpo = [r for r in legal if r["cell"] == "author_only"]
    low = [r for r in allpo if r["recipient_cash"] < 100]
    high = [r for r in allpo if r["recipient_cash"] >= 300]
    out["holder_cash"] = {
        "under_100": cnt(low), "at_least_300": cnt(high),
        "under_100_later": sum(not r["opening"] for r in low),
        "under_100_to_opus": sum(r["recipient_model"] == "Opus" for r in low),
        "by_recipient": {m: {"under_100": cnt([r for r in low if r["recipient_model"] == m]),
                             "at_least_300": cnt([r for r in high if r["recipient_model"] == m])} for m in MODELS},
    }

    # --- list-value and capacity slices (crude)
    sw_po = [r for r in opening if r["form"] == "swap" and r["cell"] == "author_only"]
    sw_n = [r for r in opening if r["form"] == "swap" and r["cell"] == "neither"]
    fav = lambda rs: [sum(r["response"] == "reject_trade" for r in rs if r["net_list_value_to_recipient"] > 0),
                      sum(r["net_list_value_to_recipient"] > 0 for r in rs)]
    out["list_value"] = {
        "median_swap_proposer_only": float(np.median([r["net_list_value_to_recipient"] for r in sw_po])),
        "median_swap_neither": float(np.median([r["net_list_value_to_recipient"] for r in sw_n])),
        "favourable_rejected_proposer_only": fav(sw_po), "favourable_rejected_neither": fav(sw_n),
        "favourable_rejected_no_grok": [fav([r for r in sw_po if r["author_model"] != "Grok"]),
                                        fav([r for r in sw_n if r["author_model"] != "Grok"])],
    }

    def plain(o):
        if isinstance(o, dict):
            return {str(k): plain(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [plain(v) for v in o]
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return o
    out = plain(out)
    write_json("check_offers.json", out)
    print(json.dumps(out, indent=1)[:14000])


if __name__ == "__main__":
    main()
