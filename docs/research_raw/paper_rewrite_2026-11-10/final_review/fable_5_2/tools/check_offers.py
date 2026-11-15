"""Independent re-tabulation of the retained offer ledger (no engine, no model calls).

Usage: python3 -I check_offers.py <package_dir> <out_json>
Reads <package_dir>/data/agenda_offers.json and t01_cohort.json read-only.
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

pkg, out_path = Path(sys.argv[1]), Path(sys.argv[2])
src = {}


def load(rel):
    raw = (pkg / rel).read_bytes()
    src[rel] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


offers = load("data/agenda_offers.json")
cohort = load("data/t01_cohort.json")
out = {"sources": src}
SHORT = {"accept_trade": "A", "counter_trade": "C", "reject_trade": "R"}
MODELS = ["Sol", "Gemini", "Opus", "Grok"]
CELLS = ["author_only", "recipient_only", "both", "neither"]

# ---- populations
out["n_offers"] = len(offers)
out["responses_all"] = dict(Counter(SHORT[r["response"]] for r in offers))
legal = [r for r in offers if r["accept_available"]]
out["n_legal"] = len(legal)
out["illegal"] = [(r["game"], r["decision"], r["recipient_model"], SHORT[r["response"]], r["exchange_index"],
                   r["author_cash_if_accepted"], r["recipient_cash_if_accepted"]) for r in offers
                  if not r["accept_available"]]
out["threads"] = len({r["thread_id"] for r in offers})


def acr(rows):
    c = Counter(SHORT[r["response"]] for r in rows)
    return [len(rows), c["A"], c["C"], c["R"]]


t2 = {}
for cell in CELLS + ["all"]:
    rows = [r for r in legal if cell == "all" or r["completion_cell"] == cell]
    t2[cell] = {"all": acr(rows), "opening": acr([r for r in rows if r["exchange_index"] == 0]),
                "later": acr([r for r in rows if r["exchange_index"] > 0])}
out["table2"] = t2
out["table3"] = {m: acr([r for r in offers if r["recipient_model"] == m]) for m in MODELS}
out["table8"] = {m: {c: acr([r for r in legal if r["recipient_model"] == m and r["completion_cell"] == c])
                     for c in CELLS} for m in MODELS}
out["response_condition_by_recipient"] = {
    m: dict(Counter(r["response_condition"] for r in offers if r["recipient_model"] == m)) for m in MODELS}
out["defaults_among_responses"] = sum(bool(r["fallback_used"]) for r in offers)

# per-stage per-recipient author-only vs recipient-only (does the Opus exception survive stage?)
stage = {}
for m in MODELS:
    for st, pred in (("opening", lambda r: r["exchange_index"] == 0), ("later", lambda r: r["exchange_index"] > 0)):
        for c in ("author_only", "recipient_only", "both", "neither"):
            stage[f"{m}/{st}/{c}"] = acr([r for r in legal if r["recipient_model"] == m and pred(r)
                                           and r["completion_cell"] == c])
out["stage_by_recipient"] = stage

# ---- initiations
first = {}
for r in offers:
    if r["exchange_index"] == 0:
        first[r["thread_id"]] = r
out["initiations"] = dict(Counter(r["author_model"] for r in first.values()))
by_thread = defaultdict(list)
for r in offers:
    by_thread[r["thread_id"]].append(r)
for rows in by_thread.values():
    rows.sort(key=lambda r: r["exchange_index"])
out["max_exchanges_in_thread"] = max(len(v) for v in by_thread.values())
# earlier thread between same unordered pair in same game
seen, earlier = set(), 0
for tid in sorted(by_thread, key=lambda t: (by_thread[t][0]["game"], by_thread[t][0]["offer_seq"])):
    r = by_thread[tid][0]
    key = (r["game"], frozenset((r["author"], r["recipient"])))
    earlier += key in seen
    seen.add(key)
out["threads_with_earlier_same_pair"] = earlier
accepts = [r for r in offers if r["response"] == "accept_trade"]
out["settlements"] = len(accepts)
out["settlement_final_author_differs_from_initiator"] = sum(r["author"] != r["initiator"] for r in accepts)
out["settlements_opening_vs_later"] = [sum(r["exchange_index"] == 0 for r in accepts),
                                       sum(r["exchange_index"] > 0 for r in accepts)]

# ---- seed-block and game robustness of the pooled contrasts
seeds = []
for g in cohort:
    if g["seed"] not in seeds:
        seeds.append(g["seed"])
block = {g["game"]: seeds.index(g["seed"]) + 1 for g in cohort}
winner_model = {g["game"]: g["winner"] for g in cohort}
out["seed_blocks"] = {str(sd): [g["game"] for g in cohort if g["seed"] == sd] for sd in seeds}


def rate(rows, resp):
    return (sum(r["response"] == resp for r in rows) / len(rows)) if rows else None


def contrast(group_fn):
    res = {}
    keys = sorted({group_fn(r) for r in legal})
    for k in keys:
        ao = [r for r in legal if group_fn(r) == k and r["completion_cell"] == "author_only"]
        ro = [r for r in legal if group_fn(r) == k and r["completion_cell"] == "recipient_only"]
        res[k] = {"n_ao": len(ao), "n_ro": len(ro),
                  "rej_ao": rate(ao, "reject_trade"), "rej_ro": rate(ro, "reject_trade"),
                  "acc_ao": rate(ao, "accept_trade"), "acc_ro": rate(ro, "accept_trade")}
    return res


bl = contrast(lambda r: block[r["game"]])
gm = contrast(lambda r: r["game"])
out["blocks"] = bl
both_games = {k: v for k, v in gm.items() if v["n_ao"] and v["n_ro"]}
out["games_with_both"] = len(both_games)
out["block_rej_holds"] = sum(v["rej_ao"] > v["rej_ro"] for v in bl.values())
out["block_acc_holds"] = sum(v["acc_ao"] < v["acc_ro"] for v in bl.values())
out["game_rej_holds"] = sum(v["rej_ao"] > v["rej_ro"] for v in both_games.values())
out["game_acc_holds"] = sum(v["acc_ao"] < v["acc_ro"] for v in both_games.values())
out["game_rej_fail"] = {k: v for k, v in both_games.items() if not v["rej_ao"] > v["rej_ro"]}
out["game_acc_fail"] = {k: v for k, v in both_games.items() if not v["acc_ao"] < v["acc_ro"]}

# ---- counters: every counter joined to the next offer in its thread
pairs = []
for rows in by_thread.values():
    for a, b in zip(rows, rows[1:]):
        assert a["response"] == "counter_trade" and a["recipient"] == b["author"] and a["author"] == b["recipient"]
        pairs.append((a, b))
out["counter_pairs"] = len(pairs)


def same_noncash(a, b):
    return all(sorted(a[x]["properties"]) == sorted(b[y]["properties"])
               and a[x]["get_out_of_jail_cards"] == b[y]["get_out_of_jail_cards"]
               for x, y in (("offer", "request"), ("request", "offer")))


def counter_block(cell, need_request):
    rows = [(a, b) for a, b in pairs if a["completion_cell"] == cell
            and (a["request"]["properties"] or not need_request)]
    res = {"n": len(rows)}
    # predicate P1: every deed the original author requested is still offered to it in the counter
    p1 = [set(a["request"]["properties"]) <= set(b["offer"]["properties"]) for a, b in rows]
    # predicate P2: every group newly completed for the original author is still newly completed for it
    p2 = [set(a["author_new_groups"]) <= set(b["recipient_new_groups"]) and bool(a["author_new_groups"])
          for a, b in rows]
    # predicate P2b: at least one of those groups still completes
    p2b = [bool(set(a["author_new_groups"]) & set(b["recipient_new_groups"])) for a, b in rows]
    res["P1_all_requested_deeds_retained"] = sum(p1)
    res["P2_all_original_author_groups_still_complete"] = sum(p2)
    res["P2b_any_original_author_group_still_completes"] = sum(p2b)
    res["P1_and_P2"] = sum(x and y for x, y in zip(p1, p2))
    res["P1_not_P2"] = [(a["game"], a["decision"]) for (a, b), x, y in zip(rows, p1, p2) if x and not y]
    res["P2_not_P1"] = [(a["game"], a["decision"]) for (a, b), x, y in zip(rows, p1, p2) if y and not x]
    # only the original author completes after the counter
    only = [y and not b["author_new_groups"] for (a, b), y in zip(rows, p2)]
    res["P2_and_counterer_completes_nothing"] = sum(only)
    res["counter_cell_distribution"] = dict(Counter(b["completion_cell"] for a, b in rows))
    # cash to counterer: before = what original author pays counterer; after = what it pays under the counter
    delta = [(-b["net_cash_author_to_recipient"]) - a["net_cash_author_to_recipient"] for a, b in rows]
    res["cash_up_all"] = sum(d > 0 for d in delta)
    res["cash_same_all"] = sum(d == 0 for d in delta)
    res["cash_down_all"] = sum(d < 0 for d in delta)
    for name, mask in (("P2", p2), ("only", only), ("P1", p1)):
        sub = [d for d, m in zip(delta, mask) if m]
        res[f"cash_up_within_{name}"] = sum(d > 0 for d in sub)
        res[f"median_increase_among_up_within_{name}"] = median([d for d in sub if d > 0]) if sub else None
        res[f"median_delta_within_{name}"] = median(sub) if sub else None
    res["median_increase_among_up_all"] = median([d for d in delta if d > 0])
    res["median_delta_all"] = median(delta)
    same = [same_noncash(a, b) for a, b in rows]
    res["same_noncash"] = sum(same)
    res["same_noncash_cash_up"] = sum(s and d > 0 for s, d in zip(same, delta))
    res["same_noncash_cash_not_up"] = [(a["game"], a["decision"], d) for (a, b), s, d in zip(rows, same, delta)
                                       if s and d <= 0]
    res["same_noncash_within_only"] = sum(s and o for s, o in zip(same, only))
    res["median_increase_same_noncash_up"] = median([d for s, d in zip(same, delta) if s and d > 0])
    # interest-inclusive cash check for the 'only' subset
    net = [(b["author_cash_if_accepted"] - b["author_cash_before"]) -
           (a["recipient_cash_if_accepted"] - a["recipient_cash_before"]) for a, b in rows]
    res["net_cash_after_interest_up_all"] = sum(n > 0 for n in net)
    res["net_cash_after_interest_up_within_only"] = sum(n > 0 for n, o in zip(net, only) if o)
    res["net_cash_after_interest_up_within_P2"] = sum(n > 0 for n, y in zip(net, p2) if y)
    res["median_net_increase_within_only_up"] = median([n for n, o in zip(net, only) if o and n > 0]) \
        if any(o and n > 0 for n, o in zip(net, only)) else None
    res["negotiated_vs_net_disagree_within_only"] = sum((d > 0) != (n > 0) for d, n, o in zip(delta, net, only) if o)
    res["by_counterer"] = {m: {"n": sum(a["recipient_model"] == m for a, b in rows),
                               "P1": sum(x for (a, b), x in zip(rows, p1) if a["recipient_model"] == m),
                               "same_up": sum(s and d > 0 for (a, b), s, d in zip(rows, same, delta)
                                              if a["recipient_model"] == m)} for m in MODELS}
    return res


out["counters_author_only"] = counter_block("author_only", True)
out["counters_author_only_no_request_filter"] = counter_block("author_only", False)["n"]
out["counters_neither_requesting"] = counter_block("neither", True)
out["counters_neither_all"] = counter_block("neither", False)["n"]
out["counters_recipient_only"] = {"n": sum(a["completion_cell"] == "recipient_only" for a, b in pairs)}

# ---- nineteen accepted author-only offers
acc = [r for r in accepts if r["completion_cell"] == "author_only"]
out["accepted_author_only"] = {
    "n": len(acc), "later": sum(r["exchange_index"] > 0 for r in acc),
    "recipient_below_100": sum(r["recipient_cash_before"] < 100 for r in acc),
    "by_recipient": dict(Counter(r["recipient_model"] for r in acc)),
    "opus_conditions": dict(Counter(r["response_condition"] for r in acc if r["recipient_model"] == "Opus")),
    "opening": [(r["game"], r["decision"], r["author_model"], r["recipient_model"], r["author_new_groups"])
                for r in acc if r["exchange_index"] == 0],
    "rows": [(r["game"], r["decision"], r["author_model"], r["recipient_model"], r["exchange_index"],
              r["recipient_cash_before"], r["author_new_groups"]) for r in acc]}

# ---- rejections that would complete the recipient's group
rej = [r for r in legal if r["response"] == "reject_trade" and r["completion_cell"] in ("recipient_only", "both")]
out["reason_population"] = {"n": len(rej), "by_cell": dict(Counter(r["completion_cell"] for r in rej)),
                            "by_recipient": dict(Counter(r["recipient_model"] for r in rej)),
                            "by_game_top": Counter(r["game"] for r in rej).most_common(4),
                            "by_stage": dict(Counter("opening" if r["exchange_index"] == 0 else "later" for r in rej))}

# ---- cash at settlement
def seller_view(r):
    """Return (payer, seller, seller_cash_before, payer_new_groups, seller_model) or None if no net cash."""
    n = r["net_cash_author_to_recipient"]
    if n > 0:
        return "author", "recipient", r["recipient_cash_before"], r["author_new_groups"], r["recipient_model"], r["recipient"]
    if n < 0:
        return "recipient", "author", r["author_cash_before"], r["recipient_new_groups"], r["author_model"], r["author"]
    return None


cash_set = [(r, seller_view(r)) for r in accepts if seller_view(r)]
out["cash_settlements"] = len(cash_set)
payer_completes = [(r, v) for r, v in cash_set if v[3]]
neither_set = [(r, v) for r, v in cash_set if r["completion_cell"] == "neither"]
out["payer_completing_cash_settlements"] = {
    "n": len(payer_completes), "median_seller_cash": median(v[2] for r, v in payer_completes),
    "seller_below_100": sum(v[2] < 100 for r, v in payer_completes),
    "by_cell": dict(Counter(r["completion_cell"] for r, v in payer_completes)),
    "seller_below_100_by_model": dict(Counter(v[4] for r, v in payer_completes if v[2] < 100))}
out["neither_cash_settlements"] = {"n": len(neither_set), "median_seller_cash": median(v[2] for r, v in neither_set)}
thr = {}
for t in (50, 100, 150, 200):
    low = [(r, v) for r, v in cash_set if v[2] < t]
    thr[t] = [sum(bool(v[3]) for r, v in low), len(low)]
out["threshold_cuts"] = thr
low100 = [(r, v) for r, v in cash_set if v[2] < 100]
out["below100_seller_by_model"] = dict(Counter(v[4] for r, v in low100))
out["low_cash_completing_sellers_who_win"] = sum(
    winner_model[r["game"]] == v[4] for r, v in payer_completes if v[2] < 100)
out["low_cash_completing_sellers"] = [(r["game"], r["decision"], v[4], v[5], v[2]) for r, v in payer_completes
                                      if v[2] < 100]
# offers of cash to low-cash recipients (recipient would receive net cash)
cash_offers = [r for r in legal if r["net_cash_author_to_recipient"] > 0]
lo = [r for r in cash_offers if r["recipient_cash_before"] < 100]
hi = [r for r in cash_offers if r["recipient_cash_before"] >= 100]
out["cash_offers_to_recipient"] = {"n": len(cash_offers), "low": acr(lo), "other": acr(hi)}
cash_offers_all = [r for r in offers if r["net_cash_author_to_recipient"] > 0]
out["cash_offers_to_recipient_incl_illegal"] = {
    "low": acr([r for r in cash_offers_all if r["recipient_cash_before"] < 100]),
    "other": acr([r for r in cash_offers_all if r["recipient_cash_before"] >= 100])}

# ---- cash direction
one_sided = [r for r in legal if r["completion_cell"] in ("author_only", "recipient_only")]
def completing_side_gets_deed(r):
    return bool(r["request"]["properties"]) if r["completion_cell"] == "author_only" else bool(r["offer"]["properties"])
out["one_sided"] = {
    "n": len(one_sided), "completing_side_receives_deed": sum(completing_side_gets_deed(r) for r in one_sided),
    "author_only_author_pays": sum(r["net_cash_author_to_recipient"] > 0 for r in one_sided
                                   if r["completion_cell"] == "author_only"),
    "recipient_only_recipient_pays": sum(r["net_cash_author_to_recipient"] < 0 for r in one_sided
                                         if r["completion_cell"] == "recipient_only")}
out["median_signed_cash_to_recipient"] = {c: median(r["net_cash_author_to_recipient"] for r in legal
                                                     if r["completion_cell"] == c) for c in CELLS}
nei = [r for r in legal if r["completion_cell"] == "neither"
       and len(r["request"]["properties"]) != len(r["offer"]["properties"])]
out["neither_unequal_deeds"] = {"n": len(nei), "buyer_pays": sum(
    (len(r["request"]["properties"]) > len(r["offer"]["properties"])) == (r["net_cash_author_to_recipient"] > 0)
    and r["net_cash_author_to_recipient"] != 0 for r in nei)}

out_path.write_text(json.dumps(out, indent=1, default=str) + "\n")
print(json.dumps({k: v for k, v in out.items() if k not in ("blocks", "stage_by_recipient")}, indent=1, default=str))
