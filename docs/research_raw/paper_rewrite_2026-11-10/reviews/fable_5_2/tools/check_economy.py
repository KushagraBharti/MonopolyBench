"""Independent re-tabulation of completion routes, estates and seed-block claims.

Inputs are retained ledgers only (phase-1 episode ledger, typed flows, cohort,
eliminations). No engine execution.
"""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import PKG, dump, ledger, median  # noqa: E402

eps = [
    json.loads(l)
    for l in open(os.path.join(PKG, "..", "paper_phase1_2026-10-28", "sol", "group_episodes.jsonl"))
]
flows = ledger("agenda_flows.json")
cohort = {c["game"]: c for c in ledger("t01_cohort.json")}
elims = ledger("t06_eliminations.json")
out: dict = {}

seat_of = {}  # (game, model) -> seat via flows/eps
for e in eps:
    seat_of[(e["game"], e["model"])] = e["player_id"]
for f in flows:
    seat_of[(f["game"], f["from_model"])] = f["from"]
    if f.get("to_model"):
        seat_of[(f["game"], f["to_model"])] = f["to"]


def is_winner(game, model):
    return cohort[game]["winner"] == model


# ---------------------------------------------------------------------------
routes = collections.Counter(e["route"] for e in eps)
inh = [e for e in eps if e["route"] == "creditor_inheritance"]
term = [e for e in inh if e["access_status"] == "no_access_before_game_end"]
live = [e for e in inh if e["access_status"] == "observed"]
out["routes"] = dict(routes)
out["inheritance"] = {
    "all": len(inh),
    "terminal_no_later_decision": len(term),
    "with_later_play": len(live),
    "with_later_play_to_eventual_winner": sum(is_winner(e["game"], e["model"]) for e in live),
    "with_later_play_built_first_management": sum(bool(e["built_first_management"]) for e in live),
    "with_later_play_entry_legal": sum(bool(e["entry_legal"]) for e in live),
    "with_later_play_collecting_any_rent": sum(e["rent_until_loss_or_end"] > 0 for e in live),
    "with_later_play_rent": sum(e["rent_until_loss_or_end"] for e in live),
    "with_later_play_by_model": dict(collections.Counter(e["model"] for e in live)),
    "with_later_play_by_game": dict(sorted(collections.Counter(e["game"] for e in live).items())),
    "games_with_any_live_inherited_completion": len({e["game"] for e in live}),
    "median_turns_from_live_completion_to_game_end": median(
        [cohort[e["game"]]["turns"] - e["acquisition_turn"] for e in live]
    ),
}
trade = [e for e in eps if e["route"] == "trade"]
out["trade_completed"] = {
    "n": len(trade),
    "to_eventual_winner": sum(is_winner(e["game"], e["model"]) for e in trade),
    "rent": sum(e["rent_until_loss_or_end"] for e in trade),
    "by_model": {
        m: {
            "groups": sum(e["model"] == m for e in trade),
            "built_first_management": sum(e["model"] == m and bool(e["built_first_management"]) for e in trade),
            "rent": sum(e["rent_until_loss_or_end"] for e in trade if e["model"] == m),
            "same_turn_management": sum(
                e["model"] == m and e["first_management_turn"] == e["acquisition_turn"] for e in trade
            ),
        }
        for m in ["Sol", "Gemini", "Opus", "Grok"]
    },
    "rent_built_first_window": sum(e["rent_until_loss_or_end"] for e in trade if e["built_first_management"]),
    "rent_not_built_first_window": sum(
        e["rent_until_loss_or_end"] for e in trade if not e["built_first_management"]
    ),
}
out["rent_by_route"] = {
    r: sum(e["rent_until_loss_or_end"] for e in eps if e["route"] == r) for r in routes
}
out["rent_total_on_complete_groups"] = sum(e["rent_until_loss_or_end"] for e in eps)
out["paid_rent_total"] = sum(f["amount"] for f in flows if f["kind"] == "paid_rent")

# ---------------------------------------------------------------------------
# Estates
elim_by_game = collections.defaultdict(list)
for e in elims:
    elim_by_game[e["game"]].append(e)
est = [f for f in flows if f["kind"] == "estate_deed"]
est_cash = [f for f in flows if f["kind"] == "estate_cash"]
out["estate_deeds"] = {
    "all": len(est),
    "terminal": sum(f["terminal_estate"] for f in est),
    "nonterminal": sum(not f["terminal_estate"] for f in est),
    "nonterminal_to_winner": sum(
        (not f["terminal_estate"]) and is_winner(f["game"], f["to_model"]) for f in est
    ),
    "all_to_winner": sum(is_winner(f["game"], f["to_model"]) for f in est),
}
out["estate_cash"] = {
    "all": sum(f["amount"] for f in est_cash),
    "nonterminal": sum(f["amount"] for f in est_cash if not f["terminal_estate"]),
    "nonterminal_to_winner": sum(
        f["amount"] for f in est_cash if not f["terminal_estate"] and is_winner(f["game"], f.get("to_model"))
    ),
    "rows_to_bank": [f for f in est_cash if f.get("to") in (None, "bank", "BANK") or f.get("to_model") in (None, "bank", "Bank")],
}
# creditor per elimination from estate rows (deed or cash)
cred = {}
for f in est + est_cash:
    cred[(f["game"], f["elimination_index"])] = (f.get("to_model"), f["terminal_estate"], f["from_model"])
out["elimination_creditors"] = {
    "eliminations_with_estate_rows": len(cred),
    "to_winner_all": sum(is_winner(g, m) for (g, i), (m, t, _) in cred.items() if m),
    "to_winner_nonterminal": sum(is_winner(g, m) for (g, i), (m, t, _) in cred.items() if m and not t),
    "nonterminal": sum(not t for (_, t, _) in cred.values()),
    "first_estate_to_winner_games": sum(
        1 for g in range(1, 21) if (g, 1) in cred and cred[(g, 1)][0] and is_winner(g, cred[(g, 1)][0])
    ),
    "single_creditor_all_three_games": sum(
        1
        for g in range(1, 21)
        if len({cred.get((g, i), (None,))[0] for i in (1, 2, 3)}) == 1
    ),
    "missing": [k for k in [(g, i) for g in range(1, 21) for i in (1, 2, 3)] if k not in cred],
}

# ---------------------------------------------------------------------------
# First completion per game and the seed-block claims in the Fable draft.
first = {}
for g in range(1, 21):
    ge = sorted([e for e in eps if e["game"] == g], key=lambda e: e["acquisition_seq"])
    f0 = ge[0]
    first[g] = {
        "owner": f0["model"],
        "seat": f0["player_id"],
        "group": f0["group"],
        "route": f0["route"],
        "turn": f0["acquisition_turn"],
        "built_first_management": f0["built_first_management"],
        "owner_won": is_winner(g, f0["model"]),
        "winner": cohort[g]["winner"],
        "winner_seat": cohort[g]["winner_seat"],
    }
out["first_completion_per_game"] = first
out["first_completion_summary"] = {
    "by_route": dict(collections.Counter(v["route"] for v in first.values())),
    "owner_won": sum(v["owner_won"] for v in first.values()),
    "owner_won_and_built_first_window": sum(
        v["owner_won"] and bool(v["built_first_management"]) for v in first.values()
    ),
}
out["block3_dark_blue"] = [
    {k: e[k] for k in ("game", "model", "player_id", "group", "route", "acquisition_turn", "first_build_turn")}
    for e in eps
    if e["game"] in (9, 10, 11, 12) and e["group"] == "DARK_BLUE" and e["route"] in ("direct_purchase", "auction")
]
out["block4_orange"] = [
    {k: e[k] for k in ("game", "model", "player_id", "group", "route", "acquisition_turn", "first_build_turn", "rent_until_loss_or_end")}
    for e in eps
    if e["game"] in (13, 14, 15, 16) and e["group"] == "ORANGE"
]
out["direct_purchase_or_auction_completions"] = [
    {
        "game": e["game"],
        "model": e["model"],
        "seat": e["player_id"],
        "group": e["group"],
        "route": e["route"],
        "turn": e["acquisition_turn"],
        "won": is_winner(e["game"], e["model"]),
        "rent": e["rent_until_loss_or_end"],
    }
    for e in sorted(eps, key=lambda e: (e["game"], e["acquisition_seq"]))
    if e["route"] in ("direct_purchase", "auction")
]
dp = out["direct_purchase_or_auction_completions"]
out["bank_route_summary"] = {
    "n": len(dp),
    "owner_won": sum(x["won"] for x in dp),
    "games": sorted({x["game"] for x in dp}),
}

# G15 Gemini orange chronology
out["g15_gemini_orange"] = [
    {k: e.get(k) for k in ("route", "acquisition_turn", "acquisition_seq", "first_build_turn", "first_build_event", "elapsed_to_build", "rent_until_loss_or_end", "first_management_turn")}
    for e in eps
    if e["game"] == 15 and e["model"] == "Gemini" and e["group"] == "ORANGE"
]

# Elimination partition
out["eliminations"] = {
    "n": len(elims),
    "declared": sum(e["elimination"] == "declared" for e in elims),
    "full_below_owed": sum(e["full"] < e["owed"] for e in elims),
    "avoidable": [
        {k: e[k] for k in ("game", "decision", "model", "owed", "cash", "menu_mortgage_only", "accessible", "full", "bank_houses")}
        for e in elims
        if e["avoidable"]
    ],
    "full_ge_owed_not_avoidable": [
        {k: e[k] for k in ("game", "decision", "model", "owed", "cash", "menu_mortgage_only", "accessible", "full", "bank_houses", "elimination")}
        for e in elims
        if e["full"] >= e["owed"] and not e["avoidable"]
    ],
    "median_shortfall_of_56": median([e["owed"] - e["full"] for e in elims if e["full"] < e["owed"]]),
    "shortfall_under_100": sum(0 < e["owed"] - e["full"] < 100 for e in elims),
    "min_shortfall": min(e["owed"] - e["full"] for e in elims if e["full"] < e["owed"]),
    "by_debtor": dict(collections.Counter(e["model"] for e in elims)),
}

dump("economy_checks.json", out)
print(json.dumps({k: v for k, v in out.items() if k not in ("first_completion_per_game", "direct_purchase_or_auction_completions")}, indent=1))
for g, v in first.items():
    print(g, v)
for x in dp:
    print(x)
