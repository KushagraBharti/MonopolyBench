"""Color-group completion episodes with timing, exposure and receipts.

Rebuilt from canonical events with the validated tracker.  An episode starts
when a player first holds every deed of a color group at a stable boundary
(after a purchase, an auction, all transfers of one accepted trade, or all
transfers of one estate) and ends when the player loses a deed of the group or
the game ends.
"""
from __future__ import annotations

import collections
import json
import statistics as S

from corpus import MODELS, board, complete_groups, load_all, write_json
from state_track import Tracker


def rent_due(B, key, level, mortgaged, group_complete):
    row = B["by_key"][key]
    if mortgaged or row["rents"] is None:
        return 0
    if level == 0:
        return row["rents"][0] * (2 if group_complete else 1)
    return row["rents"][level]


def episodes_for(g) -> tuple[list[dict], list[dict]]:
    B = board()
    idx_of = {r["key"]: r["index"] for r in B["by_key"].values()}
    tr = Tracker(g)
    eps: list[dict] = []
    open_eps: dict[tuple[str, str], dict] = {}
    held = {p: set() for p in g.model}  # complete groups currently held
    bankrupt_seqs = []
    events = g.events
    n = len(events)
    i = 0
    last_elim_seq = None
    elims = []
    pending_landing: dict = {}

    def boundary(route: str, e: dict, extra: dict | None = None):
        """Re-evaluate complete groups at a stable boundary."""
        for pid in g.model:
            if pid in tr.bankrupt:
                now = set()
            else:
                now = complete_groups(tr.owned_by(pid))
            for grp in sorted(held[pid] - now):
                ep = open_eps.pop((pid, grp))
                ep["end_seq"] = e["seq"]
                ep["end_turn"] = e["turn_index"]
                ep["end_reason"] = "bankrupt" if pid in tr.bankrupt else "traded_away"
                eps.append(ep)
            for grp in sorted(now - held[pid]):
                keys = B["color_groups"][grp]
                ep = {
                    "game": g.number,
                    "block": g.block,
                    "player": pid,
                    "model": g.model[pid],
                    "winner": pid == g.winner_pid,
                    "group": grp,
                    "route": route,
                    "start_seq": e["seq"],
                    "start_turn": e["turn_index"],
                    "mortgaged_at_start": sorted(k for k in keys if tr.mortgaged[k]),
                    "levels_at_start": {k: tr.level[k] for k in keys},
                    "cash_at_start": tr.cash[pid],
                    "rent": 0,
                    "rent_payments": 0,
                    "developed_rent": 0,
                    "landings": 0,
                    "landings_unmortgaged": 0,
                    "rent_due_at_landings": 0,
                    "houses_bought": 0,
                    "build_spend": 0,
                    "first_build_turn": None,
                    "first_build_seq": None,
                    "lethal_demands": 0,
                    "landing_events": [],  # [turns since start, rent paid, rent due at landing]
                }
                if extra:
                    ep.update(extra)
                open_eps[(pid, grp)] = ep
            held[pid] = now

    while i < n:
        e = events[i]
        t = e["type"]
        p = e["payload"]
        # --- per-event accounting on open episodes (before applying the event)
        if t == "RENT_PAID":
            key = tr.key.get(p["space_index"])
            grp = B["by_key"][key]["group"] if key else None
            ep = open_eps.get((p["to_player_id"], grp))
            if ep is not None:
                ep["rent"] += p["amount"]
                ep["rent_payments"] += 1
                if tr.level[key] > 0:
                    ep["developed_rent"] += p["amount"]
                pend = pending_landing.get(p["from_player_id"])
                if pend is not None and pend[0] is ep and pend[2] == p["space_index"]:
                    pend[1][1] += p["amount"]
        if t == "PLAYER_MOVED":
            mover = e["actor"]["player_id"]
            key = tr.key.get(p["to"])
            if key:
                grp = B["by_key"][key]["group"]
                own = tr.owner[key]
                ep = open_eps.get((own, grp)) if own and own != mover else None
                pending_landing.pop(mover, None)
                if ep is not None:
                    ep["landings"] += 1
                    if not tr.mortgaged[key]:
                        ep["landings_unmortgaged"] += 1
                    due = rent_due(B, key, tr.level[key], tr.mortgaged[key], True)
                    ep["rent_due_at_landings"] += due
                    rec = [e["turn_index"] - ep["start_turn"], 0, due]
                    ep["landing_events"].append(rec)
                    pending_landing[mover] = (ep, rec, p["to"])
        if t in ("HOUSE_BUILT", "HOTEL_BUILT"):
            key = tr.key[p["space_index"]]
            grp = B["by_key"][key]["group"]
            ep = open_eps.get((p["player_id"], grp))
            if ep is not None:
                cnt = p.get("count", 1)
                ep["houses_bought"] += cnt
                ep["build_spend"] += cnt * B["by_key"][key]["house_cost"]
                if ep["first_build_turn"] is None:
                    ep["first_build_turn"] = e["turn_index"]
                    ep["first_build_seq"] = e["seq"]
        change = tr.apply(e)
        # --- stable boundaries
        if t == "PROPERTY_PURCHASED" and change and change["kind"] == "purchase":
            # auction purchases are preceded by AUCTION_ENDED in the same turn
            # an auction sale is followed by a CASH_CHANGED 'auction_bid' and AUCTION_ENDED
            route = "auction" if any(ev["type"] == "AUCTION_ENDED" for ev in events[i + 1:i + 3]) else "purchase"
            boundary(route, e)
        elif t == "TRADE_ACCEPTED":
            j = i + 1
            while j < n and events[j]["type"] in ("CASH_CHANGED", "PROPERTY_TRANSFERRED"):
                tr_change = None
                ev = events[j]
                if ev["type"] == "CASH_CHANGED" and ev["payload"]["reason"] not in ("TRADE_CASH", "MORTGAGE_INTEREST"):
                    break
                tr.apply(ev)
                j += 1
            boundary("trade", e, {"trade_seq": e["seq"]})
            i = j
            continue
        elif change and change["kind"] == "bankruptcy":
            debtor, creditor = change["debtor"], change["creditor"]
            j = i + 1
            recipients = set()
            to_bank = False
            while j < n and (
                (events[j]["type"] == "PROPERTY_PURCHASED" and events[j]["payload"].get("price") == 0)
                or (events[j]["type"] == "CASH_CHANGED" and events[j]["payload"]["reason"] == "BANKRUPTCY_ASSETS_TO_BANK")
            ):
                if events[j]["type"] == "PROPERTY_PURCHASED":
                    recipients.add(events[j]["payload"]["player_id"])
                else:
                    to_bank = True
                tr.apply(events[j])
                j += 1
            assert len(recipients) <= 1
            if recipients:
                assert creditor in (None, next(iter(recipients)))
                creditor = next(iter(recipients))
            elif to_bank:
                assert creditor is None
            alive = [q for q in g.model if q not in tr.bankrupt]
            terminal = len(alive) == 1
            elims.append({"game": g.number, "seq": e["seq"], "turn": e["turn_index"], "debtor": debtor, "creditor": creditor, "creditor_source": "estate_recipient" if recipients else ("bank_return" if to_bank else "cash_transfer_or_none"), "terminal": terminal})
            boundary("estate", e, {"terminal_estate": terminal, "estate_from": debtor})
            i = j
            continue
        i += 1
    end = events[-1]
    for (pid, grp), ep in list(open_eps.items()):
        ep["end_seq"] = end["seq"]
        ep["end_turn"] = end["turn_index"]
        ep["end_reason"] = "game_end"
        eps.append(ep)
    for ep in eps:
        ep["duration_turns"] = ep["end_turn"] - ep["start_turn"]
    return eps, elims


def main() -> None:
    all_eps, all_elims = [], []
    for g in load_all().values():
        eps, elims = episodes_for(g)
        all_eps += eps
        all_elims += elims
    all_eps.sort(key=lambda r: (r["game"], r["start_seq"], r["player"], r["group"]))
    routes = collections.Counter()
    for ep in all_eps:
        r = ep["route"]
        if r == "estate":
            r = "terminal_estate" if ep.get("terminal_estate") else "nonterminal_estate"
        ep["route_detail"] = r
        routes[r] += 1
    summary = {
        "episodes": len(all_eps),
        "routes": dict(routes),
        "winner_by_route": {r: sum(1 for e in all_eps if e["route_detail"] == r and e["winner"]) for r in routes},
        "eliminations": len(all_elims),
        "rent_by_route": {r: sum(e["rent"] for e in all_eps if e["route_detail"] == r) for r in routes},
        "rent_earning_by_route": {r: sum(1 for e in all_eps if e["route_detail"] == r and e["rent"] > 0) for r in routes},
    }
    trade = [e for e in all_eps if e["route"] == "trade"]
    summary["trade_by_model"] = {m: sum(1 for e in trade if e["model"] == m) for m in MODELS}
    summary["trade_rent_by_model"] = {m: sum(e["rent"] for e in trade if e["model"] == m) for m in MODELS}
    write_json("a3_group_episodes.json", all_eps)
    write_json("a3_eliminations_basic.json", all_elims)
    write_json("a3_group_summary.json", summary)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
