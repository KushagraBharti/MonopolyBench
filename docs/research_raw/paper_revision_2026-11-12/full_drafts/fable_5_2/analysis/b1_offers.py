"""Offer census: rebuild, reconcile, and tabulate every negotiation response.

Reads canonical ``decisions.jsonl`` through ``corpus.py``.  One row per
trade-response decision (an offer awaiting a response).  Terms, cash and
holdings come from the state delivered to the recipient.  Imports no engine
code, runs no game and makes no model call.

Outputs
-------
data/b1_offer_ledger.json     one row per offer (920)
data/b1_offers.json           every tabulation cited in the manuscript
"""
from __future__ import annotations

import collections
import itertools
import json
import re
import statistics as S

import numpy as np

from corpus import MODELS, REPO, board, block_of, complete_groups, load_all, sha256_file, write_json

RETAINED = REPO / "docs/research_raw/paper_revision_2026-11-11/integrated/data/offers.json"
CODES = REPO / "docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/rejection_reason_coding.json"
CODES2 = REPO / "docs/research_raw/paper_agenda_revision_2026-10-29/reviews/negotiation/reason_comparison.json"
NAME_RE = re.compile(r'"name"\s*:\s*"([a-z_]+)"')
CELLS = ["author_only", "recipient_only", "both", "neither"]
FORMS = ["swap", "cash_bid", "sale_offer", "other"]
RESP = ["accept_trade", "counter_trade", "reject_trade"]
BOOT_SEED = 20261112
BOOT_DRAWS = 20000


# ---------------------------------------------------------------------------
# ledger
# ---------------------------------------------------------------------------
def cell(a_new, r_new) -> str:
    if a_new and r_new:
        return "both"
    if a_new:
        return "author_only"
    if r_new:
        return "recipient_only"
    return "neither"


def form(author_gives: dict, recipient_gives: dict) -> str:
    """Offer form.  ``swap`` and ``cash_bid`` equal the earlier integration's definitions."""
    a, b = author_gives, recipient_gives
    cards = a["get_out_of_jail_cards"] or b["get_out_of_jail_cards"]
    if a["properties"] and b["properties"]:
        return "swap"
    if b["properties"] and not a["properties"] and a["cash"] > 0 and b["cash"] == 0 and not cards:
        return "cash_bid"
    if a["properties"] and not b["properties"] and b["cash"] > 0 and a["cash"] == 0 and not cards:
        return "sale_offer"
    return "other"


def selected_attempt(r: dict):
    sel = None
    for a in r["attempts"]:
        if a.get("outcome") == "valid":
            sel = a
    return sel


def channel_conflict(r: dict) -> bool:
    """Assistant content names an action other than the received tool call."""
    sel = selected_attempt(r)
    if sel is None:
        return False
    content = sel.get("assistant_content")
    if not content:
        return False
    m = NAME_RE.search(content)
    return bool(m and m.group(1) != (sel.get("parsed_tool_call") or {}).get("name"))


def build() -> list[dict]:
    B = board()
    rows = []
    for g in load_all().values():
        thread_no = 0
        thread_id = None
        for k in range(g.n_decisions):
            st, rs = g.started[k], g.resolved[k]
            if st["decision_type"] != "TRADE_RESPONSE_DECISION":
                continue
            sc = st["prompt_payload"]["action_state"]["scenario"]
            cur = sc["current_offer"]
            recipient = st["player_id"]
            author = cur["from_player_id"]
            ex = sc["exchange_index"]
            if ex == 0:
                thread_no += 1
                thread_id = f"G{g.number:02d}-T{thread_no:03d}"
            give = cur["if_you_accept"]["you_give"]      # recipient -> author
            recv = cur["if_you_accept"]["you_receive"]   # author -> recipient
            state = g.state_before(k)["players"]
            a_own, r_own = state[author]["owned"], state[recipient]["owned"]
            a_keys, r_keys = set(a_own), set(r_own)
            assert set(recv["properties"]) <= a_keys and set(give["properties"]) <= r_keys
            a_after = (a_keys - set(recv["properties"])) | set(give["properties"])
            r_after = (r_keys - set(give["properties"])) | set(recv["properties"])
            a_new = sorted(complete_groups(a_after) - complete_groups(a_keys))
            r_new = sorted(complete_groups(r_after) - complete_groups(r_keys))

            def interest(keys, owned):
                return sum(-(-B["by_key"][x]["mortgage"] // 10) for x in keys if owned[x]["mortgaged"])

            # the decision in which the author wrote these terms
            want = "propose_trade" if ex == 0 else "counter_trade"
            j = k - 1
            while j >= 0 and not (g.resolved[j]["player_id"] == author and g.resolved[j]["final_action"]["action"] == want):
                j -= 1
            assert j >= 0
            list_value = lambda t: t["cash"] + sum(B["by_key"][x]["price"] for x in t["properties"])
            net = recv["cash"] - give["cash"]
            a_int = interest(give["properties"], r_own)
            a_cash_after = state[author]["cash"] - net - a_int
            cap = None
            if a_new:
                cap = max(a_cash_after // B["by_key"][B["color_groups"][grp][0]]["house_cost"] for grp in a_new)
            rows.append({
                "game": g.number, "block": g.block, "decision": k, "turn": st["turn_index"],
                "thread_id": thread_id, "exchange_index": ex, "opening": ex == 0,
                "author": author, "recipient": recipient,
                "author_model": g.model[author], "recipient_model": g.model[recipient],
                "response": rs["final_action"]["action"],
                "accept_available": "accept_trade" in st["prompt_payload"]["action_state"]["available_actions"],
                "author_gives": recv, "recipient_gives": give,
                "form": form(recv, give),
                "author_new_groups": a_new, "recipient_new_groups": r_new,
                "completion_cell": cell(a_new, r_new),
                "author_cash_before": state[author]["cash"], "recipient_cash_before": state[recipient]["cash"],
                "net_cash_author_to_recipient": net,
                "author_interest_if_accepted": a_int,
                "recipient_interest_if_accepted": interest(recv["properties"], a_own),
                "author_cash_if_accepted": a_cash_after,
                "author_house_capacity_if_accepted": cap,
                "net_list_value_to_recipient": list_value(recv) - list_value(give),
                "offer_decision": j,
                "author_channel_conflict": channel_conflict(g.resolved[j]),
                "recipient_channel_conflict": channel_conflict(rs),
                "response_condition": rs["sequence_meta"].get("response_condition"),
                "fallback_used": rs["fallback_used"],
                "public_message": rs["final_action"].get("public_message"),
                "private_note": rs["final_action"].get("private_thought"),
                "source_line": g.decision_line[k],
            })
    return rows


def reconcile(rows: list[dict]) -> dict:
    old = json.loads(RETAINED.read_text())
    ob = {(r["game"], r["decision"]): r for r in old}
    nb = {(r["game"], r["decision"]): r for r in rows}
    assert set(ob) == set(nb)
    pairs = [("response", "response"), ("author_model", "author_model"), ("recipient_model", "recipient_model"),
             ("exchange_index", "exchange_index"), ("completion_cell", "completion_cell"),
             ("accept_available", "accept_available"), ("recipient_cash_before", "recipient_cash_before"),
             ("author_cash_before", "author_cash_before"), ("thread_id", "thread_id"),
             ("offer_decision", "offer_decision"), ("author_gives", "offer"), ("recipient_gives", "request")]
    mism = {new: sum(nb[k][new] != ob[k][oldf] for k in nb) for new, oldf in pairs}
    assert not any(mism.values()), mism
    return {"retained_ledger": str(RETAINED.relative_to(REPO)), "retained_sha256": sha256_file(RETAINED),
            "rows": len(rows), "fields_compared": [p[0] for p in pairs], "mismatches": mism}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def acr(rs) -> dict:
    c = collections.Counter(r["response"] for r in rs)
    return {"n": len(rs), "accept": c["accept_trade"], "counter": c["counter_trade"], "reject": c["reject_trade"]}


def rej(rs) -> list[int]:
    return [sum(r["response"] == "reject_trade" for r in rs), len(rs)]


def units(rs) -> dict:
    return {"games": len({r["game"] for r in rs}), "threads": len({r["thread_id"] for r in rs}),
            "author_recipient_pairs": len({(r["game"], r["author"], r["recipient"]) for r in rs})}


def rate_diff(a, b, key="reject_trade"):
    """Difference in the share of ``key`` responses, cell a minus cell b.  None if a cell is empty."""
    if not a or not b:
        return None
    return sum(r["response"] == key for r in a) / len(a) - sum(r["response"] == key for r in b) / len(b)


def sensitivity(a: list[dict], b: list[dict], key="reject_trade") -> dict:
    """Sensitivity of one cohort contrast to which seed blocks and games it contains.

    Target: the difference in response share between two fixed sets of offers in
    this cohort.  The three summaries below vary the set of games; none of them
    is an interval for new games, new opponents or new models.
      * leave-one-block-out: recompute after removing each seed block (5 values)
      * seed-block resampling: all 5^5 ordered resamples of the five blocks, exact
      * game resampling: 20,000 resamples of the twenty games (optimistic, since
        the four games in a block share a seed and all share one roster)
    """
    point = rate_diff(a, b, key)

    def per(unit_of, n_units):
        t = np.zeros((n_units, 4))
        for r in a:
            u = unit_of(r)
            t[u, 0] += r["response"] == key
            t[u, 1] += 1
        for r in b:
            u = unit_of(r)
            t[u, 2] += r["response"] == key
            t[u, 3] += 1
        return t

    tb = per(lambda r: r["block"] - 1, 5)
    tg = per(lambda r: r["game"] - 1, 20)

    def stat(t):
        s = t.sum(axis=0)
        return None if s[1] == 0 or s[3] == 0 else s[0] / s[1] - s[2] / s[3]

    lobo = [stat(np.delete(tb, i, axis=0)) for i in range(5)]
    per_block = [None if tb[i, 1] == 0 or tb[i, 3] == 0 else tb[i, 0] / tb[i, 1] - tb[i, 2] / tb[i, 3] for i in range(5)]
    exact = [stat(tb[list(ix)]) for ix in itertools.product(range(5), repeat=5)]
    exact_ok = sorted(x for x in exact if x is not None)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.integers(0, 20, size=(BOOT_DRAWS, 20))
    sums = tg[draws].sum(axis=1)
    ok = (sums[:, 1] > 0) & (sums[:, 3] > 0)
    gs = np.sort(sums[ok, 0] / sums[ok, 1] - sums[ok, 2] / sums[ok, 3])
    q = lambda xs, p: float(np.quantile(np.asarray(xs), p)) if len(xs) else None
    pp = lambda x: None if x is None else round(100 * x, 1)
    return {
        "cells": {"a": [sum(r["response"] == key for r in a), len(a)], "b": [sum(r["response"] == key for r in b), len(b)]},
        "point_pp": pp(point),
        "per_block_pp": [pp(x) for x in per_block],
        "per_block_counts": [[int(v) for v in row] for row in tb],
        "blocks_same_sign_as_point": sum(1 for x in per_block if x is not None and point is not None and x * point > 0),
        "leave_one_block_out_pp": [pp(x) for x in lobo],
        "leave_one_block_out_range_pp": [pp(min(x for x in lobo if x is not None)), pp(max(x for x in lobo if x is not None))],
        "block_resampling": {"resamples": len(exact), "undefined": len(exact) - len(exact_ok),
                             "p2_5_pp": pp(q(exact_ok, 0.025)), "p97_5_pp": pp(q(exact_ok, 0.975)),
                             "min_pp": pp(exact_ok[0]), "max_pp": pp(exact_ok[-1]),
                             "share_positive": round(sum(x > 0 for x in exact_ok) / len(exact_ok), 4)},
        "game_resampling": {"draws": BOOT_DRAWS, "seed": BOOT_SEED, "undefined": int((~ok).sum()),
                            "p2_5_pp": pp(q(gs, 0.025)), "p97_5_pp": pp(q(gs, 0.975)),
                            "share_positive": round(float((gs > 0).mean()), 4)},
    }


def standardized(a, b, weights: dict) -> float:
    """Proposer-standardized rejection difference with the given proposer weights."""
    tot = sum(weights.values())
    out = 0.0
    for m, w in weights.items():
        am = [r for r in a if r["author_model"] == m]
        bm = [r for r in b if r["author_model"] == m]
        if not am or not bm:
            return None
        out += w / tot * (rej(am)[0] / len(am) - rej(bm)[0] / len(bm))
    return round(100 * out, 1)


COMPLETION_RE = re.compile(r"monopol|complet|\bsets?\b|finish|\bthird\b|\bblock", re.I)
BUILD_RE = re.compile(r"\bhous|hotel|\bbuild|develop", re.I)


def text_of(r) -> str:
    return (r["public_message"] or "") + "\n" + (r["private_note"] or "")


def main() -> None:
    rows = build()
    rec = reconcile(rows)
    write_json("b1_offer_ledger.json", rows)
    out: dict = {"reconciliation": rec}
    legal = [r for r in rows if r["accept_available"]]
    opening = [r for r in legal if r["opening"]]
    later = [r for r in legal if not r["opening"]]
    assert len(rows) == 920 and len(legal) == 918

    # ---- census -------------------------------------------------------------
    out["census"] = {
        "responses": acr(rows), "threads": len({r["thread_id"] for r in rows}), "acceptance_legal": len(legal),
        "by_recipient": {m: acr([r for r in rows if r["recipient_model"] == m]) for m in MODELS},
        "by_author": {m: acr([r for r in rows if r["author_model"] == m]) for m in MODELS},
        "opening": len(opening), "later": len(later),
        "opus_recipient_action_only": sum(1 for r in rows if r["recipient_model"] == "Opus" and r["response_condition"] != "standard"),
        "grok_recipient_conflicts": dict(collections.Counter(r["response"] for r in rows if r["recipient_model"] == "Grok" and r["recipient_channel_conflict"])),
        "grok_openings": sum(1 for r in rows if r["opening"] and r["author_model"] == "Grok"),
        "grok_openings_conflict": sum(1 for r in rows if r["opening"] and r["author_model"] == "Grok" and r["author_channel_conflict"]),
        "grok_acceptances": sum(1 for r in rows if r["recipient_model"] == "Grok" and r["response"] == "accept_trade"),
    }

    G = load_all()
    grok_all = [r for g in G.values() for r in g.resolved.values() if g.model[r["player_id"]] == "Grok"]
    out["census"]["grok_decisions"] = len(grok_all)
    out["census"]["grok_content_names_action"] = sum(1 for r in grok_all if (selected_attempt(r) or {}).get("assistant_content") and NAME_RE.search(selected_attempt(r)["assistant_content"]))
    out["census"]["grok_conflicts_all"] = sum(channel_conflict(r) for r in grok_all)
    out["census"]["other_systems_conflicts"] = sum(channel_conflict(r) for g in G.values() for r in g.resolved.values() if g.model[r["player_id"]] != "Grok")

    # ---- full form x completion x stage table ------------------------------
    full = {}
    for stage, rs in (("opening", opening), ("later", later), ("all", legal)):
        full[stage] = {f: {c: acr([r for r in rs if r["form"] == f and r["completion_cell"] == c]) for c in CELLS} for f in FORMS}
        full[stage]["all_forms"] = {c: acr([r for r in rs if r["completion_cell"] == c]) for c in CELLS}
        full[stage]["form_totals"] = {f: acr([r for r in rs if r["form"] == f]) for f in FORMS}
    out["full_table"] = full
    out["form_definitions"] = {
        "swap": "deeds in both directions; cash and jail cards may accompany",
        "cash_bid": "proposer gives only cash (>0); recipient gives only deeds",
        "sale_offer": "proposer gives only deeds; recipient gives only cash (>0)",
        "other": "every remaining offer (cash both ways, jail cards without a swap, gifts, cash-only)",
    }

    def cells_of(rs, f):
        return ([r for r in rs if r["form"] == f and r["completion_cell"] == "author_only"],
                [r for r in rs if r["form"] == f and r["completion_cell"] == "neither"])

    sw_po, sw_n = cells_of(opening, "swap")
    cb_po, cb_n = cells_of(opening, "cash_bid")
    sw_both = [r for r in opening if r["form"] == "swap" and r["completion_cell"] == "both"]
    assert rej(sw_po) == [95, 116] and rej(sw_n) == [37, 72] and rej(cb_po) == [42, 70] and rej(cb_n) == [67, 103]
    assert rej(sw_both) == [34, 48]
    out["headline_cells"] = {"swap_proposer_only": acr(sw_po), "swap_neither": acr(sw_n),
                             "cash_bid_proposer_only": acr(cb_po), "cash_bid_neither": acr(cb_n),
                             "swap_both": acr(sw_both)}
    out["headline_units"] = {"swap_proposer_only": units(sw_po), "swap_neither": units(sw_n),
                             "cash_bid_proposer_only": units(cb_po), "cash_bid_neither": units(cb_n)}

    # ---- strata -------------------------------------------------------------
    def strata(key):
        return {m: {"swap_proposer_only": acr([r for r in sw_po if r[key] == m]), "swap_neither": acr([r for r in sw_n if r[key] == m]),
                    "cash_bid_proposer_only": acr([r for r in cb_po if r[key] == m]), "cash_bid_neither": acr([r for r in cb_n if r[key] == m])}
                for m in MODELS}

    out["by_proposer"] = strata("author_model")
    out["by_recipient"] = strata("recipient_model")
    out["by_block"] = {b: {"swap_proposer_only": acr([r for r in sw_po if r["block"] == b]), "swap_neither": acr([r for r in sw_n if r["block"] == b]),
                           "cash_bid_proposer_only": acr([r for r in cb_po if r["block"] == b]), "cash_bid_neither": acr([r for r in cb_n if r["block"] == b])}
                       for b in range(1, 6)}
    pairs = {}
    for a in MODELS:
        for b in MODELS:
            if a == b:
                continue
            x = [r for r in sw_po if r["author_model"] == a and r["recipient_model"] == b]
            y = [r for r in sw_n if r["author_model"] == a and r["recipient_model"] == b]
            pairs[f"{a}->{b}"] = {"proposer_only": rej(x), "neither": rej(y)}
    both_obs = {k: v for k, v in pairs.items() if v["proposer_only"][1] and v["neither"][1]}
    out["swap_by_pair"] = pairs
    out["swap_pairs_summary"] = {
        "pairs_with_both_cells": len(both_obs),
        "pairs_positive": sum(1 for v in both_obs.values() if v["proposer_only"][0] / v["proposer_only"][1] > v["neither"][0] / v["neither"][1]),
        "pairs_negative": sum(1 for v in both_obs.values() if v["proposer_only"][0] / v["proposer_only"][1] < v["neither"][0] / v["neither"][1]),
        "pairs_equal": sum(1 for v in both_obs.values() if v["proposer_only"][0] / v["proposer_only"][1] == v["neither"][0] / v["neither"][1]),
    }

    # ---- composition ---------------------------------------------------------
    no_grok = lambda rs: [r for r in rs if r["author_model"] != "Grok"]
    no_conf = lambda rs: [r for r in rs if not r["author_channel_conflict"]]
    acc_n = [r for r in sw_n if r["response"] == "accept_trade"]
    out["composition"] = {
        "swap_neither_by_grok": len([r for r in sw_n if r["author_model"] == "Grok"]),
        "swap_neither_accepted": len(acc_n),
        "swap_neither_accepted_by_grok": len([r for r in acc_n if r["author_model"] == "Grok"]),
        "swap_neither_accepted_conflict_openings": len([r for r in acc_n if r["author_channel_conflict"]]),
        "swap_neither_grok_conflict_openings": len([r for r in sw_n if r["author_model"] == "Grok" and r["author_channel_conflict"]]),
        "cash_bids_in_headline_cells_by_opus": len([r for r in cb_po + cb_n if r["author_model"] == "Opus"]),
        "cash_bids_in_headline_cells": len(cb_po) + len(cb_n),
        "without_grok_authors": {"swap_proposer_only": rej(no_grok(sw_po)), "swap_neither": rej(no_grok(sw_n)),
                                 "cash_bid_proposer_only": rej(no_grok(cb_po)), "cash_bid_neither": rej(no_grok(cb_n))},
        "without_conflict_openings": {"swap_proposer_only": rej(no_conf(sw_po)), "swap_neither": rej(no_conf(sw_n)),
                                      "cash_bid_proposer_only": rej(no_conf(cb_po)), "cash_bid_neither": rej(no_conf(cb_n))},
        "conflict_opened_threads": len({r["thread_id"] for r in opening if r["author_channel_conflict"]}),
        "standardized_swap_gap_pp": {
            "weights_proposer_only_cell": standardized(sw_po, sw_n, collections.Counter(r["author_model"] for r in sw_po)),
            "weights_neither_cell": standardized(sw_po, sw_n, collections.Counter(r["author_model"] for r in sw_n)),
            "weights_pooled": standardized(sw_po, sw_n, collections.Counter(r["author_model"] for r in sw_po + sw_n)),
        },
        "accepted_openings_net_list_value_to_recipient": {
            "grok_authored": [sum(r["net_list_value_to_recipient"] for r in opening if r["response"] == "accept_trade" and r["author_model"] == "Grok"),
                              sum(1 for r in opening if r["response"] == "accept_trade" and r["author_model"] == "Grok")],
            "other_authors": [sum(r["net_list_value_to_recipient"] for r in opening if r["response"] == "accept_trade" and r["author_model"] != "Grok"),
                              sum(1 for r in opening if r["response"] == "accept_trade" and r["author_model"] != "Grok")],
        },
    }
    assert out["composition"]["without_grok_authors"]["swap_proposer_only"] == [90, 108]
    assert out["composition"]["without_grok_authors"]["swap_neither"] == [24, 36]
    assert out["composition"]["without_conflict_openings"]["swap_proposer_only"] == [93, 112]
    assert out["composition"]["without_conflict_openings"]["swap_neither"] == [26, 43]

    # ---- sensitivity of the selected contrasts -------------------------------
    out["sensitivity"] = {
        "swap_gap": sensitivity(sw_po, sw_n),
        "cash_bid_gap": sensitivity(cb_po, cb_n),
        "swap_gap_without_grok_authors": sensitivity(no_grok(sw_po), no_grok(sw_n)),
        "swap_gap_without_conflict_openings": sensitivity(no_conf(sw_po), no_conf(sw_n)),
        "swap_both_vs_neither": sensitivity(sw_both, sw_n),
        "counter_share_cash_bid_vs_swap_proposer_only": sensitivity(cb_po, sw_po, key="counter_trade"),
    }
    # difference in differences (form by completion), block and game sensitivity
    def did(rs):
        a, b = cells_of(rs, "swap")
        c, d = cells_of(rs, "cash_bid")
        x, y = rate_diff(a, b), rate_diff(c, d)
        return None if x is None or y is None else x - y

    did_point = did(opening)
    lobo = [did([r for r in opening if r["block"] != b]) for b in range(1, 6)]
    byb = {b: [r for r in opening if r["block"] == b] for b in range(1, 6)}
    exact = [did([r for b in ix for r in byb[b]]) for ix in itertools.product(range(1, 6), repeat=5)]
    exact_ok = sorted(x for x in exact if x is not None)
    out["sensitivity"]["form_by_completion_difference"] = {
        "point_pp": round(100 * did_point, 1),
        "leave_one_block_out_pp": [round(100 * x, 1) for x in lobo],
        "block_resampling": {"resamples": len(exact), "undefined": len(exact) - len(exact_ok),
                             "p2_5_pp": round(100 * float(np.quantile(exact_ok, 0.025)), 1),
                             "p97_5_pp": round(100 * float(np.quantile(exact_ok, 0.975)), 1),
                             "share_positive": round(sum(x > 0 for x in exact_ok) / len(exact_ok), 4)},
    }

    # ---- what recipients do instead of rejecting -----------------------------
    by_thread = collections.defaultdict(dict)
    for r in rows:
        by_thread[r["thread_id"]][r["exchange_index"]] = r

    def counter_kind(r):
        nxt = by_thread[r["thread_id"]].get(r["exchange_index"] + 1)
        if nxt is None:
            return "no_recorded_response"
        same = (sorted(nxt["author_gives"]["properties"]) == sorted(r["recipient_gives"]["properties"])
                and sorted(nxt["recipient_gives"]["properties"]) == sorted(r["author_gives"]["properties"])
                and nxt["author_gives"]["get_out_of_jail_cards"] == r["recipient_gives"]["get_out_of_jail_cards"]
                and nxt["recipient_gives"]["get_out_of_jail_cards"] == r["author_gives"]["get_out_of_jail_cards"])
        better = -nxt["net_cash_author_to_recipient"] > r["net_cash_author_to_recipient"]
        if same and better:
            return "same_bundle_more_cash"
        return "same_bundle_other" if same else "changed_bundle"

    def counters(rs):
        cs = [r for r in rs if r["response"] == "counter_trade"]
        return {"counters": len(cs), **dict(collections.Counter(counter_kind(r) for r in cs))}

    out["counters"] = {
        "opening_swap_proposer_only": counters(sw_po), "opening_cash_bid_proposer_only": counters(cb_po),
        "opening_swap_neither": counters(sw_n), "opening_cash_bid_neither": counters(cb_n),
        "all_author_only": counters([r for r in legal if r["completion_cell"] == "author_only"]),
        "all_neither_deed_requests": counters([r for r in legal if r["completion_cell"] == "neither" and r["recipient_gives"]["properties"]]),
    }
    # where proposer-only openings end: any acceptance later in the same thread
    def thread_settles(r):
        return any(x["response"] == "accept_trade" for x in by_thread[r["thread_id"]].values())

    out["thread_outcomes"] = {
        "swap_proposer_only": {"threads": len(sw_po), "settled": sum(thread_settles(r) for r in sw_po)},
        "cash_bid_proposer_only": {"threads": len(cb_po), "settled": sum(thread_settles(r) for r in cb_po)},
        "swap_neither": {"threads": len(sw_n), "settled": sum(thread_settles(r) for r in sw_n)},
        "cash_bid_neither": {"threads": len(cb_n), "settled": sum(thread_settles(r) for r in cb_n)},
    }

    # ---- regex screen on stated text (not semantic coding) -------------------
    def screen(rs, resp):
        xs = [r for r in rs if r["response"] == resp]
        return {"n": len(xs), "completion_terms": sum(bool(COMPLETION_RE.search(text_of(r))) for r in xs),
                "building_terms": sum(bool(BUILD_RE.search(text_of(r))) for r in xs)}

    out["keyword_screen"] = {
        "definition": {"completion_terms": COMPLETION_RE.pattern, "building_terms": BUILD_RE.pattern,
                       "fields": "recipient public message plus applied private note; a regular-expression count, not semantic coding"},
        "rejections": {"swap_proposer_only": screen(sw_po, "reject_trade"), "swap_neither": screen(sw_n, "reject_trade"),
                       "cash_bid_proposer_only": screen(cb_po, "reject_trade"), "cash_bid_neither": screen(cb_n, "reject_trade")},
        "counters": {"swap_proposer_only": screen(sw_po, "counter_trade"), "cash_bid_proposer_only": screen(cb_po, "counter_trade")},
    }

    # how each recipient words a refusal of a proposer-completing opening (regex screen)
    RECIP_RE = re.compile(r"in return|monopoly-for-monopoly|for me as well|on my side|completes? a (color )?(set|group|monopoly) for me", re.I)
    NEVER_RE = re.compile(r"\bnever\b|not for sale|do not counter|no counter", re.I)
    po_rej = [r for r in sw_po + cb_po if r["response"] == "reject_trade"]
    out["refusal_wording"] = {
        "definition": {"reciprocity_terms": RECIP_RE.pattern, "commitment_terms": NEVER_RE.pattern,
                       "fields": "recipient public message plus applied private note; regular-expression count"},
        "by_recipient": {m: {"rejections": sum(r["recipient_model"] == m for r in po_rej),
                             "reciprocity_terms": sum(1 for r in po_rej if r["recipient_model"] == m and RECIP_RE.search(text_of(r))),
                             "commitment_terms": sum(1 for r in po_rej if r["recipient_model"] == m and NEVER_RE.search(text_of(r))),
                             "building_terms": sum(1 for r in po_rej if r["recipient_model"] == m and BUILD_RE.search(text_of(r)))}
                         for m in MODELS},
        "responses_by_recipient_proposer_only_openings": {m: acr([r for r in sw_po + cb_po if r["recipient_model"] == m]) for m in MODELS},
    }

    # ---- does rejection follow the size of the rival's opportunity? ----------
    def capacity_bins(rs):
        bins = collections.OrderedDict((k, []) for k in ("0", "1-2", "3-5", "6+"))
        for r in rs:
            c = r["author_house_capacity_if_accepted"]
            bins["0" if c <= 0 else "1-2" if c <= 2 else "3-5" if c <= 5 else "6+"].append(r)
        return {k: acr(v) for k, v in bins.items()}

    out["rival_capacity"] = {
        "definition": "houses the proposer could buy on the completed group with its cash after the proposed trade and transfer interest; mortgages it could still raise are ignored",
        "swap_proposer_only": capacity_bins(sw_po), "cash_bid_proposer_only": capacity_bins(cb_po),
        "median_capacity": {"swap_proposer_only": S.median(r["author_house_capacity_if_accepted"] for r in sw_po),
                            "cash_bid_proposer_only": S.median(r["author_house_capacity_if_accepted"] for r in cb_po)},
    }

    # ---- crude list-value check ----------------------------------------------
    def lv(rs):
        fav = [r for r in rs if r["net_list_value_to_recipient"] > 0]
        return {"median_net_list_value_to_recipient": S.median(r["net_list_value_to_recipient"] for r in rs),
                "favourable_to_recipient": rej(fav), "nonnegative": sum(r["net_list_value_to_recipient"] >= 0 for r in rs)}

    out["list_value"] = {
        "definition": "cash plus board purchase price of deeds the recipient would receive, minus the same for what it would give; ignores mortgages, group value and blocking value",
        "swap_proposer_only": lv(sw_po), "swap_neither": lv(sw_n), "cash_bid_proposer_only": lv(cb_po), "cash_bid_neither": lv(cb_n),
        "swap_without_grok_authors": {"proposer_only": lv(no_grok(sw_po)), "neither": lv(no_grok(sw_n))},
    }

    # ---- holder cash ----------------------------------------------------------
    ao = [r for r in legal if r["completion_cell"] == "author_only"]
    band = lambda rs, lo, hi: [r for r in rs if lo <= r["recipient_cash_before"] < hi]
    out["holder_cash"] = {
        "all_author_only": {"under_100": acr(band(ao, -10**9, 100)), "100_299": acr(band(ao, 100, 300)), "300_plus": acr(band(ao, 300, 10**9))},
        "by_recipient": {m: {"under_100": acr(band([r for r in ao if r["recipient_model"] == m], -10**9, 100)),
                             "300_plus": acr(band([r for r in ao if r["recipient_model"] == m], 300, 10**9))} for m in MODELS},
        "under_100_later_offers": sum(1 for r in band(ao, -10**9, 100) if not r["opening"]),
        "under_100_to_opus": sum(1 for r in band(ao, -10**9, 100) if r["recipient_model"] == "Opus"),
    }

    # ---- the inherited semantic codes sit in a disjoint population -------------
    codes = json.loads(CODES.read_text())
    cmp_ = json.loads(CODES2.read_text())
    lb = {(r["game"], r["decision"]): r for r in rows}
    coded = [lb[(r["game"], r["decision"])] for r in codes["rows_data"]]
    common = set(cmp_["categories"]["D"]["common_positive_keys"])
    key_of = lambda r: f"G{r['game']:02d}d{r['decision']}"
    out["semantic_codes"] = {
        "source": str(CODES.relative_to(REPO)), "source_sha256": sha256_file(CODES),
        "comparison_source": str(CODES2.relative_to(REPO)), "comparison_sha256": sha256_file(CODES2),
        "coded_rows": len(coded),
        "coded_by_cell": dict(collections.Counter(r["completion_cell"] for r in coded)),
        "coded_opening": sum(r["opening"] for r in coded),
        "coded_rows_in_headline_cells": sum(1 for r in coded if r["completion_cell"] in ("author_only", "neither")),
        "agreed_rival_consequence": len(common),
        "agreed_by_cell": dict(collections.Counter(r["completion_cell"] for r in coded if key_of(r) in common)),
        "agreed_by_recipient": dict(collections.Counter(r["recipient_model"] for r in coded if key_of(r) in common)),
        "agreed_in_g1_g15": sum(1 for r in coded if key_of(r) in common and r["game"] in (1, 15)),
        "population_is_all_rejected_recipient_completing": len(coded) == sum(
            1 for r in legal if r["completion_cell"] in ("recipient_only", "both") and r["response"] == "reject_trade"),
    }
    assert out["semantic_codes"]["coded_rows_in_headline_cells"] == 0

    # ---- later offers -----------------------------------------------------------
    lsw_po, lsw_n = cells_of(later, "swap")
    lcb_po, lcb_n = cells_of(later, "cash_bid")
    out["later_cells"] = {"swap_proposer_only": acr(lsw_po), "swap_neither": acr(lsw_n),
                          "cash_bid_proposer_only": acr(lcb_po), "cash_bid_neither": acr(lcb_n)}

    out["sources"] = {n: g.source_hashes() for n, g in load_all().items()}
    write_json("b1_offers.json", out)
    brief = {k: v for k, v in out.items() if k not in ("sources", "swap_by_pair", "full_table")}
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
