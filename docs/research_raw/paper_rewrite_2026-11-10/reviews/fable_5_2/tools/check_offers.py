"""Independent re-tabulation of the retained offer ledger (920 rows).

Reproduces the completion-by-response cells and then attacks the two new
bargaining readings in the drafts:

  * Opus: "the completing deed stays on the table" in counters (92/111).
  * Fable: "the completing side pays" (373/429) as evidence that completion
    itself is priced.

Both need a baseline that does not involve completion. This script supplies
one from the same ledger. Existing-log re-tabulation only.
"""
from __future__ import annotations

import collections
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import board, dump, ledger, median  # noqa: E402

offers = ledger("agenda_offers.json")
_, SPACES = board()
RESP = {"accept_trade": "A", "counter_trade": "C", "reject_trade": "R"}
CELLS = ["author_only", "recipient_only", "both", "neither"]
out: dict = {}


def acr(rows):
    c = collections.Counter(RESP[r["response"]] for r in rows)
    return {"n": len(rows), "A": c["A"], "C": c["C"], "R": c["R"]}


legal = [o for o in offers if o["accept_available"]]
out["population"] = {
    "responses": len(offers),
    "acceptance_legal": len(legal),
    "threads": len({o["thread_id"] for o in offers}),
    "all": acr(offers),
}
out["cells"] = {}
for cell in CELLS:
    rows = [o for o in legal if o["completion_cell"] == cell]
    d = acr(rows)
    d["median_cash_author_to_recipient"] = median(
        [o["net_cash_author_to_recipient"] for o in rows]
    )
    out["cells"][cell] = d

# ---------------------------------------------------------------------------
# Thread structure
threads: dict[str, list] = collections.defaultdict(list)
for o in offers:
    threads[o["thread_id"]].append(o)
for t in threads.values():
    t.sort(key=lambda r: r["exchange_index"])
    assert [r["exchange_index"] for r in t] == list(range(len(t)))

# ---------------------------------------------------------------------------
# 1. Counter content, replicated, then with a non-completion baseline.
def deeds_to_author(o):
    return set(o["request"]["properties"])


def deeds_to_recipient(o):
    return set(o["offer"]["properties"])


counter_rows = []
for t in threads.values():
    for a, b in zip(t, t[1:]):
        assert a["response"] == "counter_trade"
        assert b["author"] == a["recipient"] and b["recipient"] == a["author"]
        # counterer = a.recipient = b.author
        cash_before = -a["net_cash_author_to_recipient"] * -1  # to counterer
        cash_before = a["net_cash_author_to_recipient"]  # cash to counterer under a
        cash_after = -b["net_cash_author_to_recipient"]  # cash to counterer under b
        row = {
            "game": a["game"],
            "thread": a["thread_id"],
            "decision": a["decision"],
            "cell": a["completion_cell"],
            "legal": a["accept_available"],
            "counterer_model": a["recipient_model"],
            "orig_author_completes_before": bool(a["author_new_groups"]),
            "orig_author_completes_after": bool(b["recipient_new_groups"]),
            "counterer_completes_before": bool(a["recipient_new_groups"]),
            "counterer_completes_after": bool(b["author_new_groups"]),
            "cash_change_to_counterer": cash_after - cash_before,
            # deeds the original author asked for, and whether the counter
            # still hands every one of them over
            "asked_deeds": sorted(deeds_to_author(a)),
            "keeps_all_asked_deeds": deeds_to_author(a) <= deeds_to_recipient(b)
            and bool(deeds_to_author(a)),
            "keeps_any_asked_deed": bool(deeds_to_author(a) & deeds_to_recipient(b)),
            "same_deed_sets": deeds_to_author(a) == deeds_to_recipient(b)
            and deeds_to_recipient(a) == deeds_to_author(b),
        }
        counter_rows.append(row)
assert len(counter_rows) == 394, len(counter_rows)

cc: dict = {}
ao = [r for r in counter_rows if r["cell"] == "author_only"]
cc["author_only_counters_all"] = len(ao)
cc["author_only_counters_legal"] = sum(r["legal"] for r in ao)
keep = [r for r in ao if r["orig_author_completes_after"]]
keep_only = [r for r in keep if not r["counterer_completes_after"]]
keep_both = [r for r in keep if r["counterer_completes_after"]]
swap = [
    r for r in ao if not r["orig_author_completes_after"] and r["counterer_completes_after"]
]
none = [
    r
    for r in ao
    if not r["orig_author_completes_after"] and not r["counterer_completes_after"]
]


def cash_summary(rows):
    ch = [r["cash_change_to_counterer"] for r in rows]
    return {
        "n": len(rows),
        "cash_rises": sum(c > 0 for c in ch),
        "cash_same": sum(c == 0 for c in ch),
        "cash_falls": sum(c < 0 for c in ch),
        "median_change": median(ch),
    }


cc["author_only"] = {
    "keeps_author_completion": len(keep),
    "keeps_author_only": cash_summary(keep_only),
    "keeps_author_adds_counterer": cash_summary(keep_both),
    "swaps_to_counterer": cash_summary(swap),
    "removes_all": cash_summary(none),
}
cc["author_only_keep_only_by_counterer"] = {
    m: cash_summary([r for r in keep_only if r["counterer_model"] == m])
    for m in ["Sol", "Gemini", "Opus", "Grok"]
}

# Baseline: in every cell, how often does a counter still hand over every deed
# the original author asked for? If the answer is the same where no completion
# is involved, "the completing deed stays on the table" is how counters work
# in this corpus, not something specific to completion.
base = {}
for cell in CELLS:
    rows = [r for r in counter_rows if r["cell"] == cell and r["asked_deeds"]]
    base[cell] = {
        "counters_where_author_asked_for_a_deed": len(rows),
        "counter_keeps_all_asked_deeds": sum(r["keeps_all_asked_deeds"] for r in rows),
        "counter_keeps_any_asked_deed": sum(r["keeps_any_asked_deed"] for r in rows),
        "cash_rises": sum(r["cash_change_to_counterer"] > 0 for r in rows),
        "median_cash_change": median([r["cash_change_to_counterer"] for r in rows]),
    }
cc["baseline_asked_deed_retention_by_cell"] = base
# same, restricted to counters that keep all asked deeds: cash rise share
cc["cash_rise_among_deed_keeping_counters"] = {
    cell: cash_summary(
        [
            r
            for r in counter_rows
            if r["cell"] == cell and r["asked_deeds"] and r["keeps_all_asked_deeds"]
        ]
    )
    for cell in CELLS
}
out["counter_content"] = cc

# ---------------------------------------------------------------------------
# 2. Cash direction against deed direction.
def deed_dir(o):
    a, r = len(o["request"]["properties"]), len(o["offer"]["properties"])
    return "author_net_receives" if a > r else "recipient_net_receives" if r > a else "equal"


def cash_dir(o):
    c = o["net_cash_author_to_recipient"]
    return "author_pays" if c > 0 else "recipient_pays" if c < 0 else "none"


dd = {}
for cell in CELLS:
    rows = [o for o in legal if o["completion_cell"] == cell]
    tab = collections.Counter((deed_dir(o), cash_dir(o)) for o in rows)
    dd[cell] = {f"{k[0]}|{k[1]}": v for k, v in sorted(tab.items())}
out["deed_direction_by_cash_direction"] = dd
# "The net deed receiver pays" share, by cell.
ndr = {}
for cell in CELLS:
    rows = [o for o in legal if o["completion_cell"] == cell and deed_dir(o) != "equal"]
    pays = sum(
        (deed_dir(o) == "author_net_receives" and cash_dir(o) == "author_pays")
        or (deed_dir(o) == "recipient_net_receives" and cash_dir(o) == "recipient_pays")
        for o in rows
    )
    ndr[cell] = {"offers_with_unequal_deed_counts": len(rows), "net_deed_receiver_pays": pays}
out["net_deed_receiver_pays"] = ndr
# "completing side pays" replicated
ao_l = [o for o in legal if o["completion_cell"] == "author_only"]
ro_l = [o for o in legal if o["completion_cell"] == "recipient_only"]
out["completing_side_pays"] = {
    "author_only_author_pays": sum(cash_dir(o) == "author_pays" for o in ao_l),
    "author_only_n": len(ao_l),
    "recipient_only_recipient_pays": sum(cash_dir(o) == "recipient_pays" for o in ro_l),
    "recipient_only_n": len(ro_l),
}

# ---------------------------------------------------------------------------
# 3. Offered price relative to list price for one-deed-for-cash offers.
def one_deed_for_cash(o):
    """Return (buyer_role, deed, cash) when one side gives exactly one deed and
    nothing else and the other gives only cash; otherwise None."""
    of, rq = o["offer"], o["request"]
    if of["get_out_of_jail_cards"] or rq["get_out_of_jail_cards"]:
        return None
    if len(rq["properties"]) == 1 and not of["properties"] and of["cash"] > 0 and rq["cash"] == 0:
        return ("author", rq["properties"][0], of["cash"])
    if len(of["properties"]) == 1 and not rq["properties"] and rq["cash"] > 0 and of["cash"] == 0:
        return ("recipient", of["properties"][0], rq["cash"])
    return None


price_rows = []
for o in legal:
    hit = one_deed_for_cash(o)
    if not hit:
        continue
    buyer, deed, cash = hit
    sp = SPACES[deed]
    if sp["kind"] != "PROPERTY":
        continue  # colour deeds only; railroads and utilities cannot complete
    interest = o["author_interest_if_accepted"] if buyer == "author" else o["recipient_interest_if_accepted"]
    completes = bool(o["author_new_groups"] if buyer == "author" else o["recipient_new_groups"])
    seller_breaks = bool(o["recipient_lost_groups"] if buyer == "author" else o["author_lost_groups"])
    price_rows.append(
        {
            "game": o["game"],
            "decision": o["decision"],
            "buyer_role": buyer,
            "deed": deed,
            "list": sp["price"],
            "cash": cash,
            "ratio": cash / sp["price"],
            "mortgaged": interest > 0,
            "completes_buyer": completes,
            "response": RESP[o["response"]],
            "exchange_index": o["exchange_index"],
        }
    )


def ratio_summary(rows):
    r = [x["ratio"] for x in rows]
    return {
        "n": len(rows),
        "median_ratio_to_list": None if not r else round(median(r), 3),
        "median_cash": median([x["cash"] for x in rows]),
        "accepted": sum(x["response"] == "A" for x in rows),
    }


pr: dict = {"one_colour_deed_for_cash_offers": len(price_rows)}
for mort in (False, True):
    for buyer in ("author", "recipient"):
        for comp in (True, False):
            rows = [
                x
                for x in price_rows
                if x["mortgaged"] == mort and x["buyer_role"] == buyer and x["completes_buyer"] == comp
            ]
            key = f"{'mortgaged' if mort else 'clear'}|buyer={buyer}|{'completes' if comp else 'does_not_complete'}"
            pr[key] = ratio_summary(rows)
            pr[key + "|accepted_only"] = ratio_summary([x for x in rows if x["response"] == "A"])
out["offered_price_to_list_single_deed"] = pr

# ---------------------------------------------------------------------------
# 4. Thread position, block, game, recipient.
pos = {}
for cell in CELLS:
    first = [o for o in legal if o["completion_cell"] == cell and o["exchange_index"] == 0]
    later = [o for o in legal if o["completion_cell"] == cell and o["exchange_index"] > 0]
    pos[cell] = {"first": acr(first), "later": acr(later)}
out["by_thread_position"] = pos

byrec = {}
for m in ["Sol", "Gemini", "Opus", "Grok"]:
    byrec[m] = {"all920": acr([o for o in offers if o["recipient_model"] == m])}
    for cell in CELLS:
        byrec[m][cell] = acr(
            [o for o in legal if o["recipient_model"] == m and o["completion_cell"] == cell]
        )
    ao_m = [o for o in legal if o["recipient_model"] == m and o["completion_cell"] == "author_only"]
    ro_m = [o for o in legal if o["recipient_model"] == m and o["completion_cell"] == "recipient_only"]
    byrec[m]["action_only"] = {
        "all": sum(o["response_condition"] != "standard" for o in offers if o["recipient_model"] == m),
        "author_only": acr([o for o in ao_m if o["response_condition"] != "standard"]),
        "recipient_only": acr([o for o in ro_m if o["response_condition"] != "standard"]),
    }
out["by_recipient"] = byrec


def share(d, k):
    return d[k] / d["n"] if d["n"] else None


games = {}
rej_dir = acc_dir = both_present = 0
rej_equal = rej_lower = 0
for g in range(1, 21):
    a = acr([o for o in legal if o["game"] == g and o["completion_cell"] == "author_only"])
    r = acr([o for o in legal if o["game"] == g and o["completion_cell"] == "recipient_only"])
    games[g] = {"author_only": a, "recipient_only": r}
    if a["n"] and r["n"]:
        both_present += 1
        if share(a, "R") > share(r, "R"):
            rej_dir += 1
        elif share(a, "R") == share(r, "R"):
            rej_equal += 1
        else:
            rej_lower += 1
        acc_dir += share(a, "A") < share(r, "A")
out["by_game"] = {
    "rows": games,
    "games_with_both_cells": both_present,
    "author_only_reject_share_higher": rej_dir,
    "equal": rej_equal,
    "lower": rej_lower,
    "author_only_accept_share_lower": acc_dir,
}
blocks = {}
for b in range(5):
    gs = set(range(4 * b + 1, 4 * b + 5))
    a = acr([o for o in legal if o["game"] in gs and o["completion_cell"] == "author_only"])
    r = acr([o for o in legal if o["game"] in gs and o["completion_cell"] == "recipient_only"])
    blocks[b + 1] = {
        "author_only": a,
        "recipient_only": r,
        "reject_higher_for_author_only": share(a, "R") > share(r, "R"),
        "accept_lower_for_author_only": share(a, "A") < share(r, "A"),
    }
out["by_block"] = blocks

# concentration of the pooled contrast
out["concentration"] = {
    "author_only_by_recipient_share_of_rejections": {
        m: byrec[m]["author_only"]["R"] for m in byrec
    },
    "note": "159 author-only rejections; Gemini and Grok supply 125",
}

# ---------------------------------------------------------------------------
# 5. Thread outcomes by opening cell.
to = {}
for cell in CELLS:
    ts = [t for t in threads.values() if t[0]["completion_cell"] == cell and t[0]["accept_available"]]
    settled = [t for t in ts if t[-1]["response"] == "accept_trade"]
    to[cell] = {"threads": len(ts), "settled": len(settled)}
ts = [t for t in threads.values() if t[0]["completion_cell"] == "author_only" and t[0]["accept_available"]]
settled = [t for t in ts if t[-1]["response"] == "accept_trade"]
still = []
for t in settled:
    init = t[0]["author"]
    last = t[-1]
    init_completes = bool(last["author_new_groups"] if last["author"] == init else last["recipient_new_groups"])
    cash0 = t[0]["net_cash_author_to_recipient"]
    cashN = last["net_cash_author_to_recipient"] if last["author"] == init else -last["net_cash_author_to_recipient"]
    still.append({"thread": t[0]["thread_id"], "init_completes": init_completes, "raise": cashN - cash0})
to["author_only_opening"] = {
    "settled": len(settled),
    "initiator_still_completes": sum(s["init_completes"] for s in still),
    "median_raise_when_completes": median([s["raise"] for s in still if s["init_completes"]]),
}
out["thread_outcomes_by_opening_cell"] = to

# ---------------------------------------------------------------------------
# 6. Cash-poor tabulations (threshold sensitivity).
cp = {}
settle = [o for o in offers if o["response"] == "accept_trade"]


def seller(o):
    """Net cash receiver in a settlement: (role, cash_before, payer_completes)."""
    c = o["net_cash_author_to_recipient"]
    if c > 0:
        return ("recipient", o["recipient_cash_before"], bool(o["author_new_groups"]), o["recipient_model"])
    if c < 0:
        return ("author", o["author_cash_before"], bool(o["recipient_new_groups"]), o["author_model"])
    return None


sell = [s for s in map(seller, settle) if s]
comp = [s for s in sell if s[2]]
noncomp = [s for s in sell if not s[2]]
cp["settlements_with_net_cash"] = len(sell)
cp["paying_side_completes"] = {
    "n": len(comp),
    "seller_median_cash_before": median([s[1] for s in comp]),
    "seller_under_100": sum(s[1] < 100 for s in comp),
    "seller_under_200": sum(s[1] < 200 for s in comp),
    "seller_under_300": sum(s[1] < 300 for s in comp),
    "seller_500_or_more": sum(s[1] >= 500 for s in comp),
    "by_seller_model": dict(collections.Counter(s[3] for s in comp)),
    "under_100_by_seller_model": dict(collections.Counter(s[3] for s in comp if s[1] < 100)),
}
cp["paying_side_does_not_complete"] = {
    "n": len(noncomp),
    "seller_median_cash_before": median([s[1] for s in noncomp]),
    "seller_under_100": sum(s[1] < 100 for s in noncomp),
    "by_seller_model": dict(collections.Counter(s[3] for s in noncomp)),
}
# does the seller-cash contrast survive removing Opus sellers?
for excl in ("Opus",):
    c2 = [s for s in comp if s[3] != excl]
    n2 = [s for s in noncomp if s[3] != excl]
    cp[f"without_{excl}_sellers"] = {
        "completing": {"n": len(c2), "median": median([s[1] for s in c2]), "under_100": sum(s[1] < 100 for s in c2)},
        "non_completing": {"n": len(n2), "median": median([s[1] for s in n2]), "under_100": sum(s[1] < 100 for s in n2)},
    }
out["cash_poor_settlements"] = cp

# ---------------------------------------------------------------------------
# 7. Pure cash repricing (same noncash bundle) in every cell, and counter asks
#    normalized by the cash originally offered and by list price. This is the
#    baseline for Astra's "79 of 88 true cash-only repricings".
def same_bundle(a, b):
    return all(
        sorted(a[x]["properties"]) == sorted(b[y]["properties"])
        and a[x]["get_out_of_jail_cards"] == b[y]["get_out_of_jail_cards"]
        for x, y in (("offer", "request"), ("request", "offer"))
    )


pure: dict = {}
norm_rows = []
for cell in CELLS:
    pure[cell] = collections.Counter()
for t in threads.values():
    for a, b in zip(t, t[1:]):
        cell = a["completion_cell"]
        sb = same_bundle(a, b)
        before = a["net_cash_author_to_recipient"]
        after = -b["net_cash_author_to_recipient"]
        delta = after - before
        asked = bool(a["request"]["properties"])
        pure[cell]["counters"] += 1
        pure[cell]["same_noncash_bundle"] += sb
        pure[cell]["same_bundle_cash_up"] += sb and delta > 0
        if asked:
            pure[cell]["asked_deed"] += 1
            pure[cell]["asked_deed_same_bundle_cash_up"] += sb and delta > 0
        if sb and a["request"]["properties"] and not a["offer"]["properties"] and before > 0:
            lst = sum(SPACES[k]["price"] for k in a["request"]["properties"])
            norm_rows.append(
                {
                    "cell": cell,
                    "counterer": a["recipient_model"],
                    "first_offer": a["exchange_index"] == 0,
                    "delta": delta,
                    "ask_over_offer": after / before,
                    "offer_over_list": before / lst,
                    "ask_over_list": after / lst,
                }
            )
out["pure_cash_repricing_by_cell"] = {c: dict(v) for c, v in pure.items()}
nm: dict = {}
for cell in ("author_only", "neither"):
    rows_c = [r for r in norm_rows if r["cell"] == cell]
    nm[cell] = {
        "n": len(rows_c),
        "median_delta": median([r["delta"] for r in rows_c]),
        "median_ask_over_offer": round(median([r["ask_over_offer"] for r in rows_c]), 3),
        "median_offer_over_list": round(median([r["offer_over_list"] for r in rows_c]), 3),
        "median_ask_over_list": round(median([r["ask_over_list"] for r in rows_c]), 3),
        "by_counterer": {
            m: {
                "n": sum(r["counterer"] == m for r in rows_c),
                "median_ask_over_offer": (
                    round(median([r["ask_over_offer"] for r in rows_c if r["counterer"] == m]), 3)
                    if any(r["counterer"] == m for r in rows_c)
                    else None
                ),
                "median_ask_over_list": (
                    round(median([r["ask_over_list"] for r in rows_c if r["counterer"] == m]), 3)
                    if any(r["counterer"] == m for r in rows_c)
                    else None
                ),
            }
            for m in ["Sol", "Gemini", "Opus", "Grok"]
        },
    }
out["cash_for_deed_offers_countered_by_pure_repricing"] = nm
# median pure-repricing increase by counterer where a deed was asked
inc = {}
for t in threads.values():
    for a, b in zip(t, t[1:]):
        if same_bundle(a, b) and a["request"]["properties"]:
            inc.setdefault((a["completion_cell"], a["recipient_model"]), []).append(
                -b["net_cash_author_to_recipient"] - a["net_cash_author_to_recipient"]
            )
out["pure_repricing_increase_by_cell_and_counterer"] = {
    f"{c}|{m}": {"n": len(v), "median": median(v)} for (c, m), v in sorted(inc.items())
}

dump("offer_checks.json", out)
dump("counter_rows.json", counter_rows)
dump("single_deed_price_rows.json", price_rows)

import json  # noqa: E402

print(json.dumps({k: out[k] for k in out if k not in ("by_game",)}, indent=1))
print(json.dumps({k: v for k, v in out["by_game"].items() if k != "rows"}, indent=1))
