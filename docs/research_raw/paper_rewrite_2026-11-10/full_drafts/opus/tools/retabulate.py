#!/usr/bin/env python3
"""Re-tabulate retained ledgers for the Opus full draft.

Inputs (read-only, shared workspace): ../../data/agenda_offers.json,
agenda_flows.json, t01_cohort.json, t06_eliminations.json.
Output: ../data/opus_retabulation.json. Every new number in the Opus
manuscript that is not inherited from an earlier audit comes from this file.
No engine execution, no model calls, no new games.
"""
import json
import pathlib
import statistics as st
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
DRAFT = HERE.parent
SHARED = DRAFT.parents[1] / "data"
CELLS = ["neither", "author_only", "recipient_only", "both"]
CONFIGS = ["Sol", "Gemini", "Opus", "Grok"]
RESP = {"accept_trade": "accept", "counter_trade": "counter", "reject_trade": "reject"}


def load(name):
    return json.loads((SHARED / name).read_text(encoding="utf-8"))


def tally(rows):
    c = Counter(RESP[r["response"]] for r in rows)
    return {"n": len(rows), "accept": c["accept"], "counter": c["counter"], "reject": c["reject"]}


def med(xs):
    return st.median(xs) if xs else None


def block(game):
    return (game - 1) // 4 + 1


def main():
    offers = load("agenda_offers.json")
    flows = load("agenda_flows.json")
    cohort = {c["game"]: c for c in load("t01_cohort.json")}
    elims = load("t06_eliminations.json")
    legal = [r for r in offers if r["accept_available"]]
    out = {"inputs": ["agenda_offers.json", "agenda_flows.json", "t01_cohort.json", "t06_eliminations.json"],
           "note": "author = writer of the current offer, not the thread initiator; recipient = responder."}

    out["responses_all_920"] = tally(offers)
    out["acceptance_legal"] = len(legal)
    out["cells_legal"] = {c: tally([r for r in legal if r["completion_cell"] == c]) for c in CELLS}
    out["cells_all_920"] = {c: tally([r for r in offers if r["completion_cell"] == c]) for c in CELLS}
    out["median_net_cash_to_recipient_by_cell"] = {
        c: med([r["net_cash_author_to_recipient"] for r in legal if r["completion_cell"] == c]) for c in CELLS}
    out["median_net_cash_to_recipient_by_cell_response"] = {
        c: {RESP[k]: med([r["net_cash_author_to_recipient"] for r in legal
                          if r["completion_cell"] == c and r["response"] == k]) for k in RESP} for c in CELLS}

    # Recipient (responder) configuration styles and cells.
    out["responder_all_920"] = {m: tally([r for r in offers if r["recipient_model"] == m]) for m in CONFIGS}
    out["responder_by_cell_legal"] = {
        m: {c: tally([r for r in legal if r["recipient_model"] == m and r["completion_cell"] == c]) for c in CELLS}
        for m in CONFIGS}
    out["opus_responder_conditions"] = dict(Counter(
        r["response_condition"] for r in offers if r["recipient_model"] == "Opus"))
    out["opus_responder_by_condition_cell_legal"] = {
        cond: {c: tally([r for r in legal if r["recipient_model"] == "Opus" and r["response_condition"] == cond
                         and r["completion_cell"] == c]) for c in ["author_only", "recipient_only"]}
        for cond in sorted(set(r["response_condition"] for r in offers if r["recipient_model"] == "Opus"))}
    out["block_by_cell_legal"] = {
        str(b): {c: tally([r for r in legal if block(r["game"]) == b and r["completion_cell"] == c]) for c in CELLS}
        for b in range(1, 6)}
    out["game_author_vs_recipient_only_legal"] = {
        str(g): {c: tally([r for r in legal if r["game"] == g and r["completion_cell"] == c])
                 for c in ["author_only", "recipient_only"]} for g in range(1, 21)}
    # Direction checks: reject share and accept share, author_only vs recipient_only.
    def shares(t):
        return (t["reject"] / t["n"] if t["n"] else None, t["accept"] / t["n"] if t["n"] else None)
    dir_blocks = {}
    for b in range(1, 6):
        a = out["block_by_cell_legal"][str(b)]["author_only"]
        rc = out["block_by_cell_legal"][str(b)]["recipient_only"]
        ra, aa = shares(a)
        rr, ar = shares(rc)
        dir_blocks[str(b)] = {"reject_share_author_gt_recipient": ra > rr, "accept_share_author_lt_recipient": aa < ar}
    out["direction_by_block"] = dir_blocks
    dir_cfg = {}
    for m in CONFIGS:
        a = out["responder_by_cell_legal"][m]["author_only"]
        rc = out["responder_by_cell_legal"][m]["recipient_only"]
        ra, aa = shares(a)
        rr, ar = shares(rc)
        dir_cfg[m] = {"reject_share_author_gt_recipient": ra > rr, "accept_share_author_lt_recipient": aa < ar}
    out["direction_by_responder"] = dir_cfg
    games_with_both = [g for g in range(1, 21)
                       if out["game_author_vs_recipient_only_legal"][str(g)]["author_only"]["n"]
                       and out["game_author_vs_recipient_only_legal"][str(g)]["recipient_only"]["n"]]
    rej_dir = sum(1 for g in games_with_both if shares(out["game_author_vs_recipient_only_legal"][str(g)]["author_only"])[0]
                  > shares(out["game_author_vs_recipient_only_legal"][str(g)]["recipient_only"])[0])
    out["games_with_both_cells"] = len(games_with_both)
    out["games_reject_share_author_gt_recipient"] = rej_dir

    # Counteroffer content: what does the counter do to each party's completion and the counterer's cash?
    by = defaultdict(dict)
    for r in offers:
        by[r["thread_id"]][r["exchange_index"]] = r
    counters = defaultdict(lambda: defaultdict(list))
    counters_author_only_by_responder = defaultdict(lambda: defaultdict(list))
    for r in offers:
        if r["response"] != "counter_trade":
            continue
        nxt = by[r["thread_id"]][r["exchange_index"] + 1]
        assert nxt["author"] == r["recipient"]
        orig_author_completes = bool(nxt["recipient_new_groups"])
        counterer_completes = bool(nxt["author_new_groups"])
        gain = (-nxt["net_cash_author_to_recipient"]) - r["net_cash_author_to_recipient"]
        key = f"orig_author_completes={orig_author_completes};counterer_completes={counterer_completes}"
        counters[r["completion_cell"]][key].append(gain)
        if r["completion_cell"] == "author_only":
            counters_author_only_by_responder[r["recipient_model"]][key].append(gain)
    out["counter_content_author_only_by_responder"] = {
        m: {k: {"n": len(v), "median_cash_gain_to_counterer": med(v),
                "gain_positive": sum(1 for x in v if x > 0)} for k, v in d.items()}
        for m, d in counters_author_only_by_responder.items()}
    out["counter_content"] = {
        cell: {k: {"n": len(v), "median_cash_gain_to_counterer": med(v),
                   "gain_positive": sum(1 for x in v if x > 0), "gain_zero": sum(1 for x in v if x == 0),
                   "gain_negative": sum(1 for x in v if x < 0)} for k, v in d.items()}
        for cell, d in counters.items()}

    # Thread-level outcomes by the opening offer's cell (author of opening offer = initiator).
    threads = defaultdict(list)
    for r in offers:
        threads[r["thread_id"]].append(r)
    th_out = defaultdict(Counter)
    init_completion = []
    for t, rs in threads.items():
        rs.sort(key=lambda r: r["exchange_index"])
        first, last = rs[0], rs[-1]
        assert first["author"] == first["initiator"]
        cell = first["completion_cell"]
        settled = last["response"] == "accept_trade"
        th_out[cell]["settled" if settled else "unsettled"] += 1
        if settled and cell == "author_only":
            ini = first["author"]
            if last["author"] == ini:
                comp = bool(last["author_new_groups"])
                paid = last["net_cash_author_to_recipient"]
            else:
                comp = bool(last["recipient_new_groups"])
                paid = -last["net_cash_author_to_recipient"]
            init_completion.append((comp, paid - first["net_cash_author_to_recipient"]))
    out["threads_total"] = len(threads)
    out["threads_by_opening_cell"] = {c: dict(th_out[c]) for c in CELLS}
    keep = [x for c, x in init_completion if c]
    out["author_only_opening_settled"] = {
        "settled": len(init_completion),
        "initiator_still_completes": len(keep),
        "median_extra_cash_paid_by_initiator_vs_opening_when_completing": med(keep),
    }

    # Cash-seeking offers by author cash on hand (descriptive threshold, not a distress measure).
    sellers = [r for r in legal if r["net_cash_author_to_recipient"] < 0]
    out["cash_seeking_legal_offers"] = len(sellers)
    out["cash_seeking_by_author_cash"] = {
        f"{lo}-{hi if hi < 10**6 else 'inf'}": tally([r for r in sellers if lo <= r["author_cash_before"] < hi])
        for lo, hi in [(0, 100), (100, 300), (300, 700), (700, 10**6)]}

    # Creditor identity versus eventual winner.
    by_game = defaultdict(list)
    for e in elims:
        by_game[e["game"]].append(e)
    cred = Counter()
    nonterm = Counter()
    for g, es in by_game.items():
        es.sort(key=lambda e: e["elimination_event_seq"])
        for i, e in enumerate(es):
            mods = {f["to_model"] for f in flows
                    if f["game"] == g and f["kind"].startswith("estate") and f["from"] == e["player"]}
            key = "winner" if mods == {cohort[g]["winner"]} else ("none" if not mods else "+".join(sorted(mods)))
            cred[key] += 1
            if i < len(es) - 1:
                nonterm[key] += 1
    out["estate_recipient_all_60"] = dict(cred)
    out["estate_recipient_nonterminal_40"] = dict(nonterm)
    est_deeds = [f for f in flows if f["kind"] == "estate_deed"]
    out["estate_deeds"] = {"total": len(est_deeds),
                           "to_winner": sum(1 for f in est_deeds if f["to_model"] == cohort[f["game"]]["winner"]),
                           "nonterminal": sum(1 for f in est_deeds if not f.get("terminal_estate")),
                           "nonterminal_to_winner": sum(1 for f in est_deeds if not f.get("terminal_estate")
                                                        and f["to_model"] == cohort[f["game"]]["winner"])}

    # Elimination financing partition, including the displayed-menu-only figure.
    out["eliminations"] = {
        "n": len(elims),
        "declared": sum(1 for e in elims if e["elimination"] == "declared"),
        "automatic": sum(1 for e in elims if e["elimination"] == "automatic"),
        "nominal_bound_below_debt": sum(1 for e in elims if e["full"] < e["owed"]),
        "payable_by_witness": sum(1 for e in elims if e["avoidable"]),
        "payable_cases_menu_mortgage_only_below_debt": sum(1 for e in elims if e["avoidable"]
                                                           and e["menu_mortgage_only"] < e["owed"]),
        "nominal_ge_debt_not_payable": [f"G{e['game']} {e['decision']}" for e in elims
                                        if e["full"] >= e["owed"] and not e["avoidable"]],
        "by_configuration": dict(Counter(e["model"] for e in elims)),
    }
    (DRAFT / "data").mkdir(exist_ok=True)
    (DRAFT / "data" / "opus_retabulation.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["cells_legal", "direction_by_responder", "direction_by_block",
                                          "games_with_both_cells", "games_reject_share_author_gt_recipient",
                                          "author_only_opening_settled", "estate_recipient_all_60",
                                          "estate_recipient_nonterminal_40", "estate_deeds", "eliminations",
                                          "opus_responder_conditions", "opus_responder_by_condition_cell_legal",
                                          "threads_by_opening_cell"]}, indent=1))


if __name__ == "__main__":
    main()
