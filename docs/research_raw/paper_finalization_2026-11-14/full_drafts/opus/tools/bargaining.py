"""Descriptive bargaining census from the retained 920-response ledger.

The offer ledger and its completion classification are inherited from the
earlier packages (rebuilt from raw decisions in prior rounds). This script only
re-tabulates them. It computes no p-values and no resampling; the retained
block-resampling summaries are read from the integrated package. Read-only.
"""
from __future__ import annotations

import json
from collections import Counter

import lib

offers = json.loads(lib.OFFER_FILE.read_text())
assert len(offers) == 920
legal = [r for r in offers if r["accept_available"]]
opening = [r for r in legal if r["exchange_index"] == 0]
MODELS = ["Sol", "Gemini", "Opus", "Grok"]


def form(r):
    a, b = r["offer"], r["request"]
    if a["properties"] and b["properties"]:
        return "Swap"
    if not a["get_out_of_jail_cards"] and not b["get_out_of_jail_cards"]:
        if b["properties"] and not a["properties"] and a["cash"] > 0 and b["cash"] == 0:
            return "Cash bid"
        if a["properties"] and not b["properties"] and b["cash"] > 0 and a["cash"] == 0:
            return "Cash ask"
    return "Other"


def resp(rs):
    c = Counter(r["response"] for r in rs)
    return {"n": len(rs), "accept": c["accept_trade"], "counter": c["counter_trade"], "reject": c["reject_trade"]}


def gap(a, b):
    return 100 * (a["reject"] / a["n"] - b["reject"] / b["n"]) if a["n"] and b["n"] else None


def contrast(rs):
    a = resp([r for r in rs if r["completion_cell"] == "author_only"])
    b = resp([r for r in rs if r["completion_cell"] == "neither"])
    return {"proposer_only": a, "neither": b, "gap_pp": gap(a, b)}


def main():
    conf = {r["thread"] for r in json.loads((lib.INTEGRATED / "data/conflicting_openings.json").read_text())["conflict_openings"]}
    swaps = [r for r in opening if form(r) == "Swap"]
    bids = [r for r in opening if form(r) == "Cash bid"]
    by_recipient = {m: resp([r for r in offers if r["recipient_model"] == m]) for m in MODELS}
    summary = {
        "responses": resp(offers),
        "threads": len({(r["game"], r["thread_id"]) for r in offers}),
        "accept_available": len(legal),
        "by_recipient_model": by_recipient,
        "opening_swaps": contrast(swaps),
        "opening_swaps_both_completing": resp([r for r in swaps if r["completion_cell"] == "both"]),
        "opening_swaps_no_grok_authors": contrast([r for r in swaps if r["author_model"] != "Grok"]),
        "opening_swaps_no_conflicting_openings": contrast([r for r in swaps if r["thread_id"] not in conf]),
        "opening_swaps_by_proposer": {m: contrast([r for r in swaps if r["author_model"] == m]) for m in MODELS},
        "opening_cash_bids": contrast(bids),
        "opening_cash_bids_by_recipient": {m: contrast([r for r in bids if r["recipient_model"] == m]) for m in MODELS},
        "opening_swaps_by_recipient": {m: contrast([r for r in swaps if r["recipient_model"] == m]) for m in MODELS},
        "later_swaps": contrast([r for r in legal if r["exchange_index"] > 0 and form(r) == "Swap"]),
        "grok_neither_swaps_authored": sum(1 for r in swaps if r["completion_cell"] == "neither" and r["author_model"] == "Grok"),
        "grok_neither_swaps_accepted": sum(1 for r in swaps if r["completion_cell"] == "neither" and r["author_model"] == "Grok" and r["response"] == "accept_trade"),
        "grok_neither_swaps_accepted_from_conflicting_openings": sum(1 for r in swaps if r["completion_cell"] == "neither" and r["author_model"] == "Grok" and r["response"] == "accept_trade" and r["thread_id"] in conf),
        "inputs": {lib.rel(lib.OFFER_FILE): lib.sha256_file(lib.OFFER_FILE),
                   lib.rel(lib.INTEGRATED / "data/conflicting_openings.json"): lib.sha256_file(lib.INTEGRATED / "data/conflicting_openings.json")},
    }
    byt = {}
    for r in offers:
        byt.setdefault((r["game"], r["thread_id"]), {})[r["exchange_index"]] = r

    def keeps_exchange(r):
        nx = byt[(r["game"], r["thread_id"])].get(r["exchange_index"] + 1)
        if nx is None:
            return False
        return (sorted(nx["offer"]["properties"]) == sorted(r["request"]["properties"])
                and sorted(nx["request"]["properties"]) == sorted(r["offer"]["properties"])
                and nx["offer"]["get_out_of_jail_cards"] == r["request"]["get_out_of_jail_cards"]
                and nx["request"]["get_out_of_jail_cards"] == r["offer"]["get_out_of_jail_cards"])
    c_po = [r for r in legal if r["response"] == "counter_trade" and r["completion_cell"] == "author_only"]
    c_ne = [r for r in legal if r["response"] == "counter_trade" and r["completion_cell"] == "neither" and r["request"]["properties"]]
    summary["counters_preserving_noncash_exchange"] = {
        "proposer_only_completion": [sum(map(keeps_exchange, c_po)), len(c_po)],
        "neither_completing_deed_requests": [sum(map(keeps_exchange, c_ne)), len(c_ne)],
    }
    stab = json.loads((lib.INTEGRATED / "data/revision_analysis.json").read_text())["stability"]
    summary["retained_block_summaries"] = {k: {kk: v.get(kk) for kk in ["gap_pp", "block_gaps", "leave_one_block_out", "resampling_percentiles", "alternative_resampling"]} for k, v in stab.items()}
    lib.write_json("bargaining_census.json", summary)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
