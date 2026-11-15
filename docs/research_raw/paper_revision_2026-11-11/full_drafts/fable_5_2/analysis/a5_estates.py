"""Positions immediately before each game's first estate.

For every game, take the state delivered at the first liquidation prompt of the
debt episode that ends in the first elimination.  Describe all four players at
that moment (cash, deeds, buildings, complete and developed groups, rent
received so far and a simple asset total) and ask whether the first creditor
and the eventual winner were already ahead.
"""
from __future__ import annotations

import collections
import json

from corpus import board, complete_groups, load_all, write_json
from state_track import Tracker


def asset_total(B, tr: Tracker, pid: str) -> dict:
    deeds = tr.owned_by(pid)
    deed_value = sum(B["by_key"][k]["price"] // (2 if tr.mortgaged[k] else 1) for k in deeds)
    bld = sum(tr.level[k] * (B["by_key"][k]["house_cost"] or 0) for k in deeds)
    groups = complete_groups(deeds)
    developed = sorted(g for g in groups if any(tr.level[k] > 0 for k in B["color_groups"][g]))
    return {
        "cash": tr.cash[pid],
        "deeds": len(deeds),
        "mortgaged_deeds": sum(1 for k in deeds if tr.mortgaged[k]),
        "deed_value": deed_value,
        "building_cost": bld,
        "building_levels": sum(tr.level[k] for k in deeds),
        "complete_groups": sorted(groups),
        "developed_groups": developed,
        "assets": tr.cash[pid] + deed_value + bld,
    }


def main() -> None:
    B = board()
    debt = json.loads((__import__("corpus").OUT / "a4_debt_episodes.json").read_text())
    rows = []
    all_elims = []
    for g in load_all().values():
        elim_eps = sorted((e for e in debt if e["game"] == g.number and e["outcome"] == "eliminated"), key=lambda e: e["first_decision"])
        assert len(elim_eps) == 3
        first = elim_eps[0]
        # fold events up to the first liquidation prompt of that episode
        tr = Tracker(g)
        rent_in = collections.Counter()
        rent_out = collections.Counter()
        target = first["first_decision"]
        elim_order = []
        snap = None
        deeds_after_first = None
        for e in g.events:
            if e["type"] == "LLM_DECISION_REQUESTED" and g.dec_index(e["payload"]["decision_id"]) == target and snap is None:
                snap = {pid: asset_total(B, tr, pid) for pid in g.model}
                for pid in g.model:
                    snap[pid]["rent_received"] = rent_in[pid]
                    snap[pid]["rent_paid"] = rent_out[pid]
                snap_turn = e["turn_index"]
            if e["type"] == "RENT_PAID":
                rent_in[e["payload"]["to_player_id"]] += e["payload"]["amount"]
                rent_out[e["payload"]["from_player_id"]] += e["payload"]["amount"]
            ch = tr.apply(e)
            if ch and ch["kind"] == "bankruptcy":
                elim_order.append((ch["debtor"], ch["creditor"], e["turn_index"], e["seq"]))
        # creditor identity comes from the debt prompt (owed_to_player_id); the cash-transfer
        # hint in the tracker is empty when the debtor has no cash to hand over
        creditors = [ep["creditor"] for ep in elim_eps]
        elim_order = [(d, creditors[i], t, s) for i, (d, _c, t, s) in enumerate(elim_order)]
        debtor, creditor, turn, seq = elim_order[0]
        assert debtor == first["player"], (g.number, debtor, first["player"])
        survivors = [p for p in g.model if p != debtor]

        def rank(field, pid):
            vals = sorted((snap[p][field] if not isinstance(snap[p][field], list) else len(snap[p][field]) for p in g.model), reverse=True)
            v = snap[pid][field] if not isinstance(snap[pid][field], list) else len(snap[pid][field])
            return 1 + sum(1 for x in vals if x > v)

        def leader(field):
            def val(p):
                x = snap[p][field]
                return len(x) if isinstance(x, list) else x
            best = max(val(p) for p in g.model)
            return [p for p in g.model if val(p) == best]

        row = {
            "game": g.number,
            "block": g.block,
            "turn": turn,
            "debtor": debtor,
            "debtor_model": g.model[debtor],
            "creditor": creditor,
            "creditor_model": g.model[creditor] if creditor else "bank",
            "winner": g.winner_pid,
            "winner_model": g.winner,
            "creditor_is_winner": creditor == g.winner_pid,
            "debt": first["debt"],
            "debt_reason": first["reason"],
            "positions": {g.model[p]: snap[p] for p in g.model},
            "estate": {
                "deeds": snap[debtor]["deeds"],
                "building_levels": snap[debtor]["building_levels"],
                "complete_groups": snap[debtor]["complete_groups"],
                "cash_at_first_menu": snap[debtor]["cash"],
            },
        }
        for who, pid in (("creditor", creditor), ("winner", g.winner_pid)):
            if pid is None:
                continue
            for f in ("assets", "cash", "deeds", "building_cost", "rent_received", "developed_groups", "complete_groups"):
                row[f"{who}_rank_{f}"] = rank(f, pid)
        for f in ("assets", "rent_received", "building_cost"):
            row[f"leader_{f}"] = leader(f)
            row[f"creditor_leads_{f}"] = creditor in leader(f) if creditor else False
            row[f"winner_leads_{f}"] = g.winner_pid in leader(f)
        tot_assets = sum(snap[p]["assets"] for p in g.model)
        row["creditor_asset_share"] = round(snap[creditor]["assets"] / tot_assets, 3) if creditor else None
        row["winner_asset_share"] = round(snap[g.winner_pid]["assets"] / tot_assets, 3)
        row["creditor_rent_share"] = (
            round(snap[creditor]["rent_received"] / max(1, sum(snap[p]["rent_received"] for p in g.model)), 3) if creditor else None
        )
        row["elimination_order"] = [
            {"debtor": g.model[d], "creditor": (g.model[c] if c else "bank"), "turn": t} for d, c, t, _ in elim_order
        ]
        rows.append(row)
        for i, (d, c, t, s) in enumerate(elim_order):
            all_elims.append(
                {"game": g.number, "order": i + 1, "debtor": g.model[d], "creditor": (g.model[c] if c else "bank"), "creditor_is_winner": c == g.winner_pid, "turn": t}
            )
    n = len(rows)
    summary = {
        "games": n,
        "first_creditor_is_winner": sum(r["creditor_is_winner"] for r in rows),
        "first_creditor_leads_assets": sum(r["creditor_leads_assets"] for r in rows),
        "first_creditor_leads_rent_received": sum(r["creditor_leads_rent_received"] for r in rows),
        "first_creditor_leads_building_cost": sum(r["creditor_leads_building_cost"] for r in rows),
        "winner_leads_assets_before_first_estate": sum(r["winner_leads_assets"] for r in rows),
        "winner_leads_rent_before_first_estate": sum(r["winner_leads_rent_received"] for r in rows),
        "winner_leads_building_before_first_estate": sum(r["winner_leads_building_cost"] for r in rows),
        "creditor_rank_assets_distribution": {str(k): v for k, v in collections.Counter(r.get("creditor_rank_assets", "bank") for r in rows).items()},
        "creditor_rank_rent_distribution": {str(k): v for k, v in collections.Counter(r.get("creditor_rank_rent_received", "bank") for r in rows).items()},
        "winner_rank_assets_distribution": {str(k): v for k, v in collections.Counter(r["winner_rank_assets"] for r in rows).items()},
        "creditor_has_developed_group": sum(1 for r in rows if r["creditor"] and r["positions"][r["creditor_model"]]["developed_groups"]),
        "games_where_asset_leader_is_winner_but_not_first_creditor": [r["game"] for r in rows if r["winner_leads_assets"] and not r["creditor_is_winner"]],
        "games_where_first_creditor_wins_without_leading_assets": [r["game"] for r in rows if r["creditor_is_winner"] and not r["creditor_leads_assets"]],
        "games_first_creditor_not_winner": [r["game"] for r in rows if not r["creditor_is_winner"]],
        "first_elimination_turn_median": sorted(r["turn"] for r in rows)[n // 2],
        "all_three_estates_to_winner": sum(
            1 for g in range(1, 21) if all(e["creditor_is_winner"] for e in all_elims if e["game"] == g)
        ),
    }
    write_json("a5_pre_estate.json", rows)
    write_json("a5_pre_estate_summary.json", summary)
    print(json.dumps(summary, indent=1))
    for r in rows:
        c = r["positions"].get(r["creditor_model"], {"developed_groups": None})
        w = r["positions"][r["winner_model"]]
        print(
            r["game"], "t", r["turn"], r["debtor_model"], "->", r["creditor_model"], "| win", r["winner_model"],
            "| cred assets rank", r.get("creditor_rank_assets"), "share", r["creditor_asset_share"], "rent rank", r.get("creditor_rank_rent_received"),
            "dev", c["developed_groups"], "| winner rank", r["winner_rank_assets"], "share", r["winner_asset_share"],
            "| estate deeds", r["estate"]["deeds"], "groups", r["estate"]["complete_groups"], "lvls", r["estate"]["building_levels"],
        )


if __name__ == "__main__":
    main()
