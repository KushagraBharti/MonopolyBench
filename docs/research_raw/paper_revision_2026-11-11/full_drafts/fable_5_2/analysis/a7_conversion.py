"""Conversion: what completed groups and sale proceeds turned into.

(a) Timing, exposure and receipts for the 63 trade-completed groups, with the
    *inherited* first-management-window classification joined for reference.
(b) What sellers did after one-sided completion sales: construction within a
    fixed window after the sale, later elimination and game outcome.
(c) Cohort outcome tables by system and seat.
All counts are fresh arithmetic on canonical events unless marked inherited.
"""
from __future__ import annotations

import collections
import json
import statistics as S

from corpus import MODELS, OUT, REPO, board, load_all, sha256_file, write_json

B = board()
RETAINED_WINDOWS = REPO / "docs/research_raw/paper_rewrite_2026-11-10/data/first_management_windows.json"
WINDOW_TURNS = 8  # two rounds of a four-player table; reported with 4 and 12 as sensitivity


def trade_groups() -> tuple[list[dict], dict]:
    eps = [e for e in json.loads((OUT / "a3_group_episodes.json").read_text()) if e["route"] == "trade"]
    fw = {(r["game"], r["player"], r["group"]): r for r in json.loads(RETAINED_WINDOWS.read_text())["rows"]}
    rows = []
    for e in eps:
        w = fw[(e["game"], e["player"], e["group"])]
        lag = None if e["first_build_turn"] is None else e["first_build_turn"] - e["start_turn"]
        rows.append(
            {
                **{k: e[k] for k in ("game", "block", "player", "model", "winner", "group", "start_turn", "end_turn", "duration_turns", "end_reason",
                                     "cash_at_start", "rent", "developed_rent", "rent_payments", "landings", "landings_unmortgaged",
                                     "rent_due_at_landings", "houses_bought", "build_spend", "first_build_turn")},
                "mortgaged_deeds_at_completion": len(e["mortgaged_at_start"]),
                "turns_to_first_build": lag,
                "inherited_first_window_cause": w["cause"],
                "inherited_built_first_window": w["built_first_mgmt_turn"],
                "inherited_entry_legal": w["entry_legal"],
            }
        )
    by_model = {}
    for m in MODELS:
        xs = [r for r in rows if r["model"] == m]
        lags = [r["turns_to_first_build"] for r in xs if r["turns_to_first_build"] is not None]
        by_model[m] = {
            "groups": len(xs),
            "built_first_window_inherited": sum(r["inherited_built_first_window"] for r in xs),
            "ever_built": sum(r["first_build_turn"] is not None for r in xs),
            "built_within_2_turns": sum(1 for r in xs if r["turns_to_first_build"] is not None and r["turns_to_first_build"] <= 2),
            "median_turns_to_first_build_when_built": S.median(lags) if lags else None,
            "mortgaged_deed_at_completion": sum(r["mortgaged_deeds_at_completion"] > 0 for r in xs),
            "median_cash_after_completion": S.median(r["cash_at_start"] for r in xs),
            "median_start_turn": S.median(r["start_turn"] for r in xs),
            "median_duration_turns": S.median(r["duration_turns"] for r in xs),
            "group_turns_held": sum(r["duration_turns"] for r in xs),
            "opponent_landings": sum(r["landings"] for r in xs),
            "opponent_landings_unmortgaged": sum(r["landings_unmortgaged"] for r in xs),
            "rent_paid": sum(r["rent"] for r in xs),
            "rent_due_at_landings": sum(r["rent_due_at_landings"] for r in xs),
            "construction_spend": sum(r["build_spend"] for r in xs),
            "rent_per_landing": round(sum(r["rent"] for r in xs) / max(1, sum(r["landings"] for r in xs)), 1),
            "rent_due_per_landing": round(sum(r["rent_due_at_landings"] for r in xs) / max(1, sum(r["landings"] for r in xs)), 1),
            "landings_per_100_group_turns": round(100 * sum(r["landings"] for r in xs) / max(1, sum(r["duration_turns"] for r in xs)), 2),
            "groups_with_zero_landings": sum(r["landings"] == 0 for r in xs),
            "winner_groups": sum(r["winner"] for r in xs),
        }
    per_block = {}
    for b in range(1, 6):
        per_block[b] = {}
        for label, ms in (("Sol+Gemini", ("Sol", "Gemini")), ("Opus+Grok", ("Opus", "Grok"))):
            xs = [r for r in rows if r["block"] == b and r["model"] in ms]
            per_block[b][label] = {
                "groups": len(xs),
                "landings": sum(r["landings"] for r in xs),
                "rent": sum(r["rent"] for r in xs),
                "rent_per_landing": round(sum(r["rent"] for r in xs) / max(1, sum(r["landings"] for r in xs)), 1),
            }
    early = [r for r in rows if r["inherited_built_first_window"]]
    late = [r for r in rows if not r["inherited_built_first_window"]]
    summary = {
        "retained_windows_sha256": sha256_file(RETAINED_WINDOWS),
        "groups": len(rows),
        "by_model": by_model,
        "per_block_rent_per_landing": per_block,
        "inherited_first_window_causes": dict(collections.Counter(r["inherited_first_window_cause"] for r in rows)),
        "first_window_built": {
            "groups": len(early), "rent": sum(r["rent"] for r in early), "landings": sum(r["landings"] for r in early),
            "group_turns": sum(r["duration_turns"] for r in early), "median_duration": S.median(r["duration_turns"] for r in early),
        },
        "first_window_not_built": {
            "groups": len(late), "rent": sum(r["rent"] for r in late), "landings": sum(r["landings"] for r in late),
            "group_turns": sum(r["duration_turns"] for r in late), "median_duration": S.median(r["duration_turns"] for r in late),
            "later_built": sum(r["first_build_turn"] is not None for r in late),
        },
        "total_rent": sum(r["rent"] for r in rows),
        "total_landings": sum(r["landings"] for r in rows),
        "median_landings_per_group": S.median(r["landings"] for r in rows),
        "top5_groups_share_of_rent": round(sum(sorted((r["rent"] for r in rows), reverse=True)[:5]) / sum(r["rent"] for r in rows), 3),
        "groups_with_rent": sum(r["rent"] > 0 for r in rows),
        "not_built_mortgaged_at_completion": sum(1 for r in late if r["mortgaged_deeds_at_completion"] > 0),
        "built_mortgaged_at_completion": sum(1 for r in early if r["mortgaged_deeds_at_completion"] > 0),
    }
    return rows, summary


def seller_conversion() -> dict:
    games = load_all()
    dy = [d for d in json.loads((OUT / "a6_dyads.json").read_text()) if d["settled"] and d["one_sided"]]
    rows = []
    for d in dy:
        g = games[d["game"]]
        k = d["settle_decision"]
        st = g.state_before(k)["players"][d["holder"]]
        levels = sum((5 if h["hotel"] else h["houses"]) for h in st["owned"].values())
        seq = g.resolved[k]["emitted_event_seq_end"]
        built = {4: 0, 8: 0, 12: 0}
        for e in g.events:
            if e["seq"] <= seq:
                continue
            dt = e["turn_index"] - d["settle_turn"]
            if dt > 12:
                break
            if e["type"] in ("HOUSE_BUILT", "HOTEL_BUILT") and e["payload"]["player_id"] == d["holder"]:
                for w in built:
                    if dt <= w:
                        built[w] += e["payload"].get("count", 1)
        rows.append(
            {
                "game": d["game"], "block": d["block"], "seller_model": d["holder_model"], "buyer_model": d["completer_model"], "group": d["group"],
                "turn": d["settle_turn"], "seller_cash": d["settle_holder_cash"], "net_cash_to_seller": d["settle_net_cash_to_holder"],
                "seller_building_levels_at_sale": levels, "houses_built_within": built,
                "seller_eliminated_turn": d["holder_eliminated_turn"], "seller_won": g.winner_pid == d["holder"], "buyer_won": g.winner_pid == d["completer"],
            }
        )

    def tab(xs, w=WINDOW_TURNS):
        fin = [r for r in xs if r["houses_built_within"][w] > 0]
        non = [r for r in xs if r["houses_built_within"][w] == 0]

        def desc(ys):
            el = [r["seller_eliminated_turn"] - r["turn"] for r in ys if r["seller_eliminated_turn"] is not None]
            return {
                "n": len(ys), "seller_won": sum(r["seller_won"] for r in ys), "seller_eliminated": len(el),
                "distinct_seller_player_games": len({(r["game"], r["seller_model"]) for r in ys}),
                "distinct_winning_seller_player_games": len({(r["game"], r["seller_model"]) for r in ys if r["seller_won"]}),
                "median_turns_to_elimination": S.median(el) if el else None,
                "eliminated_within_30_turns": sum(1 for x in el if x <= 30),
                "by_seller_model": dict(collections.Counter(r["seller_model"] for r in ys)),
                "games": sorted({r["game"] for r in ys}),
                "median_net_cash": S.median(r["net_cash_to_seller"] for r in ys) if ys else None,
            }

        return {"built_after_sale": desc(fin), "no_construction_after_sale": desc(non)}

    low = [r for r in rows if r["seller_cash"] < 100]
    out = {
        "definition": f"One-sided completion sales (43). 'Built after sale' = the seller buys at least one house or hotel within {WINDOW_TURNS} global turns after settlement.",
        "all_one_sided": tab(rows),
        "seller_under_100": tab(low),
        "seller_100_plus": tab([r for r in rows if r["seller_cash"] >= 100]),
        "sensitivity_window_4": {"seller_under_100": tab(low, 4), "all_one_sided": tab(rows, 4)},
        "sensitivity_window_12": {"seller_under_100": tab(low, 12), "all_one_sided": tab(rows, 12)},
        "rows": rows,
    }
    return out


def cohort() -> dict:
    games = load_all()
    wins = collections.Counter(g.winner for g in games.values())
    seat = collections.Counter(g.seat[g.winner_pid] for g in games.values())
    block = {b: {g.rotation: [g.winner, g.seat[g.winner_pid]] for g in games.values() if g.block == b} for b in range(1, 6)}
    # elimination order by model
    order = collections.defaultdict(collections.Counter)
    debt = json.loads((OUT / "a4_debt_episodes.json").read_text())
    for n, g in games.items():
        el = sorted((d for d in debt if d["game"] == n and d["outcome"] == "eliminated"), key=lambda d: d["first_decision"])
        for i, d in enumerate(el):
            order[d["model"]][i + 1] += 1
    return {
        "wins_by_system": dict(wins),
        "wins_by_seat": {str(k): v for k, v in sorted(seat.items())},
        "winner_by_block_and_rotation": block,
        "elimination_position_by_system": {m: {str(k): v for k, v in sorted(order[m].items())} for m in MODELS},
        "turns": {n: g.turns for n, g in games.items()},
        "decisions_by_system": {m: sum(1 for g in games.values() for k in range(g.n_decisions) if g.model[g.started[k]["player_id"]] == m) for m in MODELS},
    }


def main() -> None:
    rows, summary = trade_groups()
    conv = seller_conversion()
    co = cohort()
    write_json("a7_trade_groups.json", rows)
    eps = [e for e in json.loads((OUT / "a3_group_episodes.json").read_text()) if e["route"] == "trade"]
    write_json("a7_landings.json", {f"{e['game']}|{e['player']}|{e['group']}": e["landing_events"] for e in eps})
    write_json("a7_conversion.json", {"trade_groups": summary, "seller_conversion": conv, "cohort": co})
    brief = {"trade_groups": summary, "seller_conversion": {k: v for k, v in conv.items() if k != "rows"}, "cohort": co}
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
