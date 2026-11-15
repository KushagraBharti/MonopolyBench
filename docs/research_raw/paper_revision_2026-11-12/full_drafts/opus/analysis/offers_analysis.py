"""Bargaining tabulations from the stored 920-response offer ledger.

Read-only. Produces data/offers_analysis.json. Definitions are in the
docstrings and in Appendix C of the manuscript.
"""
from __future__ import annotations

import random
import re
from collections import Counter, defaultdict
from statistics import median

import common as C

ALL = C.offers()
LEGAL = C.legal_offers()
OPEN = [r for r in LEGAL if r["exchange_index"] == 0]
HEAD = ("author_only", "neither")
out: dict = {}

# ------------------------------------------------------------ 1. full table
out["population"] = {
    "responses": len(ALL),
    "acceptance_legal": len(LEGAL),
    "not_acceptance_legal": C.acr([r for r in ALL if not r["accept_available"]]),
    "threads": len({r["thread_id"] for r in ALL}),
    "all_responses": C.acr(ALL),
    "by_recipient": {m: C.acr([r for r in ALL if r["recipient_model"] == m]) for m in C.MODELS},
}
full = {}
for st in ("opening", "later"):
    for f in C.FORMS:
        for c in C.CELLS:
            full[f"{st}|{f}|{c}"] = C.acr([r for r in LEGAL if C.stage(r) == st and C.form(r) == f
                                           and r["completion_cell"] == c])
out["full_table"] = full
assert sum(v["n"] for v in full.values()) == len(LEGAL) == 918
assert full["opening|swap|author_only"] == {"n": 116, "A": 1, "C": 20, "R": 95}
assert full["opening|swap|neither"] == {"n": 72, "A": 17, "C": 18, "R": 37}
assert full["opening|cash_bid|author_only"] == {"n": 70, "A": 2, "C": 26, "R": 42}
assert full["opening|cash_bid|neither"] == {"n": 103, "A": 4, "C": 32, "R": 67}
out["completion_totals"] = {c: {st: C.acr([r for r in LEGAL if C.stage(r) == st and r["completion_cell"] == c])
                                for st in ("opening", "later")} for c in C.CELLS}


def rate(cell):
    return cell["R"] / cell["n"] if cell["n"] else None


def gap(rows, f):
    a = [r for r in rows if C.form(r) == f and r["completion_cell"] == "author_only"]
    b = [r for r in rows if C.form(r) == f and r["completion_cell"] == "neither"]
    ca, cb = C.acr(a), C.acr(b)
    return {"proposer_only": ca, "neither": cb,
            "gap_pp": None if not ca["n"] or not cb["n"] else round(100 * (rate(ca) - rate(cb)), 2)}


# ------------------------------------------------------------ 2. Grok conflicting openings
def content_action(att: dict):
    text = att.get("assistant_content")
    if text is None:
        text = (att.get("raw_response") or {}).get("choices", [{}])[0].get("message", {}).get("content")
    m = re.search(r'"name"\s*:\s*"([a-z_]+)"', text or "")
    return m[1] if m else None


conflict_threads = []
for r in ALL:
    if r["exchange_index"] or r["author_model"] != "Grok":
        continue
    k = r["offer_decision"] if isinstance(r["offer_decision"], int) else C.did_index(r["offer_decision"])
    rec = C.resolved(r["game"], k)
    assert rec["final_action"]["action"] == "propose_trade"
    act = content_action(rec["attempts"][-1])
    if act and act != "propose_trade":
        conflict_threads.append({"thread": r["thread_id"], "game": r["game"], "decision": k, "content_action": act})
CONF = {x["thread"] for x in conflict_threads}
assert len(CONF) == 64
out["grok_conflict_openings"] = {"threads": len(CONF),
                                 "content_actions": dict(Counter(x["content_action"] for x in conflict_threads))}

# ------------------------------------------------------------ 3. composition versions
VERSIONS = {
    "all": lambda r: True,
    "without_conflicting_grok_openings": lambda r: r["thread_id"] not in CONF,
    "without_grok_authored": lambda r: r["author_model"] != "Grok",
}
comp = {}
for name, keep in VERSIONS.items():
    rows = [r for r in OPEN if keep(r)]
    comp[name] = {f: gap(rows, f) for f in ("swap", "cash_bid")}
out["composition_versions"] = comp

# composition facts about the comparator swaps
cmp_swaps = [r for r in OPEN if C.form(r) == "swap" and r["completion_cell"] == "neither"]
acc = [r for r in cmp_swaps if r["response"] == "accept_trade"]
out["comparator_swap_composition"] = {
    "n": len(cmp_swaps), "grok_authored": sum(r["author_model"] == "Grok" for r in cmp_swaps),
    "accepted": len(acc), "accepted_grok_authored": sum(r["author_model"] == "Grok" for r in acc),
    "accepted_grok_in_conflict_threads": sum(r["author_model"] == "Grok" and r["thread_id"] in CONF for r in acc),
    "grok_authored_in_conflict_threads": sum(r["author_model"] == "Grok" and r["thread_id"] in CONF for r in cmp_swaps),
    "accepted_grok_net_list_value_to_recipient": sum(C.net_list_value_to_recipient(r) for r in acc if r["author_model"] == "Grok"),
}
cash_head = [r for r in OPEN if C.form(r) == "cash_bid" and r["completion_cell"] in HEAD]
out["cash_bid_composition"] = {"n": len(cash_head), "by_author": dict(Counter(r["author_model"] for r in cash_head))}

# ------------------------------------------------------------ 4. proposer and recipient strata
strata = {}
for who in ("author_model", "recipient_model"):
    strata[who] = {}
    for m in C.MODELS:
        rows = [r for r in OPEN if r[who] == m]
        strata[who][m] = {f: gap(rows, f) for f in ("swap", "cash_bid")}
out["strata"] = strata
pairs = {}
for a in C.MODELS:
    for b in C.MODELS:
        if a == b:
            continue
        rows = [r for r in OPEN if r["author_model"] == a and r["recipient_model"] == b]
        g = gap(rows, "swap")
        if g["proposer_only"]["n"] and g["neither"]["n"]:
            pairs[f"{a}->{b}"] = g
out["author_recipient_swap_pairs"] = pairs
out["author_recipient_swap_pairs_positive"] = sum(v["gap_pp"] > 0 for v in pairs.values())

# proposer standardisation of the swap gap
g_by = {m: strata["author_model"][m]["swap"] for m in C.MODELS}
std = {}
for ref in ("proposer_only", "neither", "pooled"):
    w = {m: (g_by[m]["proposer_only"]["n"] + g_by[m]["neither"]["n"]) if ref == "pooled" else g_by[m][ref]["n"]
         for m in C.MODELS}
    num = sum(w[m] * g_by[m]["gap_pp"] for m in C.MODELS if g_by[m]["gap_pp"] is not None)
    den = sum(w[m] for m in C.MODELS if g_by[m]["gap_pp"] is not None)
    std[ref] = round(num / den, 2)
out["swap_gap_standardised_by_proposer"] = std

# ------------------------------------------------------------ 5. seed blocks
blocks = {}
for name, keep in VERSIONS.items():
    blocks[name] = {}
    for f in ("swap", "cash_bid"):
        per = {b: gap([r for r in OPEN if keep(r) and C.block_of(r["game"]) == b], f) for b in range(1, 6)}
        loo = {b: gap([r for r in OPEN if keep(r) and C.block_of(r["game"]) != b], f)["gap_pp"] for b in range(1, 6)}
        blocks[name][f] = {"per_block": per, "leave_one_block_out": loo,
                           "positive_blocks": sum(1 for v in per.values() if v["gap_pp"] is not None and v["gap_pp"] > 0)}
out["seed_blocks"] = blocks

# ------------------------------------------------------------ 6. resampling
# Target: difference in pooled rejection share (R/n, proposer-only minus
# neither) among opening offers of one form, for a cohort with this design.
# Units: (a) two-stage: draw 5 seed blocks with replacement, then 4 games
# with replacement within each drawn block; (b) seed blocks only; (c) games
# only (ignores shared seeds; shown for comparison). 20,000 draws each.
by_game = defaultdict(list)
for r in OPEN:
    by_game[r["game"]].append(r)


def cell_counts(game_list, keep, f):
    na = ra = nb = rb = 0
    for g in game_list:
        for r in by_game[g]:
            if not keep(r) or C.form(r) != f:
                continue
            if r["completion_cell"] == "author_only":
                na += 1; ra += r["response"] == "reject_trade"
            elif r["completion_cell"] == "neither":
                nb += 1; rb += r["response"] == "reject_trade"
    return na, ra, nb, rb


def pct(xs, q):
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def boot(keep, f, mode, reps=20000, seed=20261112):
    rng = random.Random(seed)
    games_in = {b: [g for g in range(1, 21) if C.block_of(g) == b] for b in range(1, 6)}
    vals = []
    for _ in range(reps):
        if mode == "two_stage":
            sample = []
            for b in (rng.choice(range(1, 6)) for _ in range(5)):
                sample += [rng.choice(games_in[b]) for _ in range(4)]
        elif mode == "blocks":
            sample = [g for b in (rng.choice(range(1, 6)) for _ in range(5)) for g in games_in[b]]
        else:
            sample = [rng.choice(range(1, 21)) for _ in range(20)]
        na, ra, nb, rb = cell_counts(sample, keep, f)
        if na and nb:
            vals.append(100 * (ra / na - rb / nb))
    return {"reps_used": len(vals), "p2.5": round(pct(vals, .025), 1), "p50": round(pct(vals, .5), 1),
            "p97.5": round(pct(vals, .975), 1), "share_positive": round(sum(v > 0 for v in vals) / len(vals), 3)}


res = {}
for name, keep in VERSIONS.items():
    res[name] = {f: {mode: boot(keep, f, mode) for mode in ("two_stage", "blocks", "games")}
                 for f in ("swap", "cash_bid")}
out["resampling"] = res
out["resampling_definition"] = (
    "Percentile intervals of the difference in pooled rejection share, proposer-only minus neither, "
    "opening offers of one form. two_stage resamples five seed blocks then four games within each; "
    "blocks resamples seed blocks intact; games resamples twenty games and ignores shared seeds. "
    "20,000 draws, random.Random(20261112). Descriptive spread for a cohort of this design; "
    "the contrast was chosen after inspecting this corpus, so no interval here confirms it.")

# ------------------------------------------------------------ 7. offer terms per headline cell
def capacity(r):
    groups = r["author_new_groups"]
    if not groups:
        return None
    cost = min(C.house_cost(g) for g in groups)
    return r["author_cash_if_accepted"] / cost if cost else None


terms = {}
for f in ("swap", "cash_bid"):
    for c in HEAD:
        rows = [r for r in OPEN if C.form(r) == f and r["completion_cell"] == c]
        nlv = [C.net_list_value_to_recipient(r) for r in rows]
        caps = [x for x in (capacity(r) for r in rows) if x is not None]
        terms[f"{f}|{c}"] = {
            "n": len(rows),
            "median_net_list_value_to_recipient": median(nlv),
            "share_net_list_value_nonnegative": round(sum(v >= 0 for v in nlv) / len(nlv), 3),
            "median_cash_to_recipient": median(r["offer"]["cash"] - r["request"]["cash"] for r in rows),
            "median_deeds_offered": median(len(r["offer"]["properties"]) for r in rows),
            "median_proposer_cash_if_accepted": median(r["author_cash_if_accepted"] for r in rows),
            "median_proposer_house_capacity": None if not caps else round(median(caps), 2),
        }
out["headline_offer_terms"] = terms
# list-value split inside proposer-only vs neither swaps
fav = {}
for name, keep in VERSIONS.items():
    rows = [r for r in OPEN if keep(r) and C.form(r) == "swap"]
    fav[name] = {c: C.acr([r for r in rows if r["completion_cell"] == c and C.net_list_value_to_recipient(r) > 0])
                 for c in HEAD}
out["swaps_with_positive_net_list_value"] = fav
# rejection by proposer's post-trade house capacity, proposer-only cells
bands = {}
for f in ("swap", "cash_bid"):
    rows = [r for r in OPEN if C.form(r) == f and r["completion_cell"] == "author_only"]
    def band(x):
        if x is None: return "unknown"
        if x < 1: return "<1"
        if x < 3: return "1-2"
        if x < 6: return "3-5"
        return "6+"
    bands[f] = {b: C.acr([r for r in rows if band(capacity(r)) == b]) for b in ("<1", "1-2", "3-5", "6+", "unknown")}
out["proposer_only_by_house_capacity"] = bands

# ------------------------------------------------------------ 8. what counters do
by_thread = defaultdict(dict)
for r in ALL:
    by_thread[r["thread_id"]][r["exchange_index"]] = r


def counter_kind(r):
    nxt = by_thread[r["thread_id"]].get(r["exchange_index"] + 1)
    if nxt is None:
        return "no_next_offer"
    # the counter is authored by the recipient of r; compare deed bundles
    same_deeds = (sorted(nxt["offer"]["properties"]) == sorted(r["request"]["properties"]) and
                  sorted(nxt["request"]["properties"]) == sorted(r["offer"]["properties"]) and
                  nxt["offer"]["get_out_of_jail_cards"] == r["request"]["get_out_of_jail_cards"] and
                  nxt["request"]["get_out_of_jail_cards"] == r["offer"]["get_out_of_jail_cards"])
    cash_to_counterer_before = r["offer"]["cash"] - r["request"]["cash"]
    cash_to_counterer_after = nxt["request"]["cash"] - nxt["offer"]["cash"]
    if same_deeds and cash_to_counterer_after > cash_to_counterer_before:
        return "same_deeds_more_cash"
    if same_deeds:
        return "same_deeds_other_cash"
    return "different_deeds"


counters = {}
for f in ("swap", "cash_bid"):
    for c in HEAD:
        rows = [r for r in OPEN if C.form(r) == f and r["completion_cell"] == c and r["response"] == "counter_trade"]
        counters[f"{f}|{c}"] = dict(Counter(counter_kind(r) for r in rows), n=len(rows))
out["opening_counters"] = counters

# ------------------------------------------------------------ 9. keyword screen (not semantic coding)
COMPLETION = re.compile(r"monopol|complet|\bsets?\b|finish|third|full (?:colou?r )?group|close[sd]?\b", re.I)
BUILD = re.compile(r"\bhouses?\b|\bhotels?\b|\bbuild|develop", re.I)
screen = {}
for f in ("swap", "cash_bid"):
    for c in HEAD:
        for resp in ("reject_trade", "counter_trade"):
            rows = [r for r in OPEN if C.form(r) == f and r["completion_cell"] == c and r["response"] == resp]
            text = lambda r: (r.get("public_message") or "") + " " + (r.get("applied_private_note") or "")
            screen[f"{f}|{c}|{resp}"] = {"n": len(rows),
                                         "completion_terms": sum(bool(COMPLETION.search(text(r))) for r in rows),
                                         "building_terms": sum(bool(BUILD.search(text(r))) for r in rows),
                                         "with_private_note": sum(bool(r.get("applied_private_note")) for r in rows)}
out["keyword_screen"] = screen
out["keyword_screen_definition"] = {"completion": COMPLETION.pattern, "building": BUILD.pattern,
                                    "fields": "recipient public message plus applied private note of the response",
                                    "status": "single-pass regular-expression screen, post hoc; not semantic coding"}

# ------------------------------------------------------------ 10. the 61/74 semantic population
neg = C.REPO / "docs/research_raw/paper_agenda_revision_2026-10-29"
c1 = C.read_json(neg / "negotiation/rejection_reason_coding.json")
c2 = C.read_json(neg / "reviews/negotiation/reason_comparison.json")
idx = {(r["game"], r["decision"]): r for r in ALL}
coded = [idx[(r["game"], r["decision"])] for r in c1["rows_data"]]
common = set(c2["categories"]["D"]["common_positive_keys"])
key = lambda r: f"G{r['game']:02d}d{r['decision']}"
out["semantic_population"] = {
    "definition": c1["population"],
    "rows": len(coded),
    "by_cell": dict(Counter(r["completion_cell"] for r in coded)),
    "by_stage": dict(Counter(C.stage(r) for r in coded)),
    "in_headline_cells": sum(r["completion_cell"] in HEAD for r in coded),
    "rival_consequence_first_pass": c2["categories"]["D"]["first_pass_positive"],
    "rival_consequence_second_reading": c2["categories"]["D"]["reviewer_positive"],
    "rival_consequence_agreed": c2["categories"]["D"]["common_positive"],
    "agreed_by_cell": dict(Counter(r["completion_cell"] for r in coded if key(r) in common)),
    "agreed_by_recipient": dict(Counter(r["recipient_model"] for r in coded if key(r) in common)),
    "agreed_in_G1_or_G15": sum(1 for r in coded if key(r) in common and r["game"] in (1, 15)),
    "status": "inherited LLM-assisted codes; membership and counts rejoined here; no human validation",
}
assert out["semantic_population"]["in_headline_cells"] == 0
assert out["semantic_population"]["rival_consequence_agreed"] == 61

# ------------------------------------------------------------ 11. cash bands (context)
def cashband(c):
    return "<100" if c < 100 else "100-299" if c < 300 else "300+"


cb = {}
for m in C.MODELS:
    rows = [r for r in LEGAL if r["completion_cell"] == "author_only" and r["recipient_model"] == m]
    cb[m] = {b: C.acr([r for r in rows if cashband(r["recipient_cash_before"]) == b]) for b in ("<100", "100-299", "300+")}
out["proposer_only_requests_by_holder_cash"] = cb

out["sources"] = C.sources_snapshot()
C.write_json("offers_analysis.json", out)

h = comp["all"]
print("swap", h["swap"]["gap_pp"], "cash", h["cash_bid"]["gap_pp"])
for n in comp:
    print(n, comp[n]["swap"], comp[n]["cash_bid"]["gap_pp"])
print("std", std)
print("resampling", {n: {f: res[n][f] for f in res[n]} for n in res})
