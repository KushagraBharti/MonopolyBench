"""Downstream event accounting and recorded-menu measurements, version sol_phase1_v1.

No engine rule simulation, model calls, or canonical writes. Group completion is
ownership, not strategic value. Trade settlement is atomic for group comparisons.
All times are global engine turn indexes. Missing access is distinct from passing.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import re


BUILD_EVENTS = {"HOUSE_BUILT", "HOTEL_BUILT"}
MANAGEMENT = "POST_TURN_ACTION_DECISION"
TRADE_REASONS = {"TRADE_CASH", "MORTGAGE_INTEREST"}


def space_key(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_").upper()


def is_trade_effect(event):
    return event["type"] == "PROPERTY_TRANSFERRED" or (
        event["type"] == "CASH_CHANGED" and event["payload"].get("reason") in TRADE_REASONS
    )


def reconstruct(events, players, board, initial_cash=1500):
    """Reconstruct ownership episodes, deed routes, cash and bilateral settlements.

    The retained engine emits creditor inheritance as PROPERTY_PURCHASED at zero
    price on a deed that still has an owner. A zero-price unowned deed has unknown
    provenance here and fails instead of silently becoming inheritance.
    """
    assert [e["seq"] for e in events] == list(range(len(events))), "Non-contiguous events"
    groups = {}
    for s in board:
        if s["kind"] == "PROPERTY":
            groups.setdefault(s["group"], []).append(s["index"])
    owners = {s["index"]: None for s in board if s.get("price") is not None}
    cash = {p: initial_cash for p in players}
    last_route, acquisitions, episodes, trades, active = {}, [], [], [], {}
    auction = False

    def holdings():
        return {(p, g) for p in players for g, indices in groups.items()
                if all(owners[i] == p for i in indices)}

    def change(e, route):
        p, typ = e["payload"], e["type"]
        if typ == "CASH_CHANGED":
            cash[p["player_id"]] += p["delta"]
            if p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
                for i in owners:
                    if owners[i] == p["player_id"]:
                        owners[i] = None
                        last_route.pop(i, None)
        elif typ in {"PROPERTY_TRANSFERRED", "PROPERTY_PURCHASED"}:
            i = p["space_index"]
            previous = owners[i]
            if typ == "PROPERTY_TRANSFERRED":
                assert previous == p["from_player_id"], (e["seq"], previous, p)
                recipient = p["to_player_id"]
                assert route == "trade", "Transfer outside accepted settlement"
            else:
                recipient = p["player_id"]
                if previous is not None:
                    assert previous != recipient and p["price"] == 0, e
                    route = "creditor_inheritance"
                elif p["price"] == 0:
                    raise ValueError("Unowned zero-price purchase needs an explicit route")
            owners[i] = recipient
            last_route[i] = route
            acquisitions.append({"seq": e["seq"], "event_id": e["event_id"],
                                 "turn": e["turn_index"], "space_index": i,
                                 "from_player_id": previous, "to_player_id": recipient,
                                 "route": route, "price": p.get("price")})

    def update_episodes(before, marker, cause, settlement_end=None):
        after = holdings()
        for key in sorted(before - after):
            episode = active.pop(key)
            episode.update(end_seq_exclusive=marker["seq"], end_reason="ownership_loss")
        for p, g in sorted(after - before):
            episode = {"player_id": p, "group": g, "route": cause,
                       "acquisition_seq": marker["seq"], "acquisition_event": marker["event_id"],
                       "acquisition_turn": marker["turn_index"],
                       "settlement_end_seq": settlement_end if settlement_end is not None else marker["seq"],
                       "constituent_last_routes": {str(i): last_route[i] for i in groups[g]}}
            episodes.append(episode)
            active[(p, g)] = episode

    i = 0
    while i < len(events):
        e = events[i]
        typ, p = e["type"], e["payload"]
        before = holdings()
        if typ == "TRADE_ACCEPTED":
            parties = [p["initiator_player_id"], p["counterparty_player_id"]]
            assert len(set(parties)) == 2
            accepting = e["actor"]["player_id"]
            assert accepting in parties
            author = next(pid for pid in parties if pid != accepting)
            cash_before = dict(cash)
            transfers, flows, interest = [], Counter(), Counter()
            j = i + 1
            while j < len(events) and is_trade_effect(events[j]):
                effect = events[j]
                ep = effect["payload"]
                if effect["type"] == "PROPERTY_TRANSFERRED":
                    assert {ep["from_player_id"], ep["to_player_id"]} == set(parties)
                    transfers.append(deepcopy(ep))
                else:
                    assert ep["player_id"] in parties
                    flows[ep["player_id"]] += ep["delta"]
                    if ep["reason"] == "MORTGAGE_INTEREST":
                        interest[ep["player_id"]] += -ep["delta"]
                change(effect, "trade")
                j += 1
            update_episodes(before, e, "trade", j - 1)
            gained = {pid: sorted(g for who, g in holdings() - before if who == pid) for pid in parties}
            trades.append({"seq": e["seq"], "event_id": e["event_id"], "turn": e["turn_index"],
                           "settlement_end_seq": j - 1, "thread_initiator": parties[0],
                           "thread_recipient": parties[1], "accepting_player": accepting,
                           "final_offer_author": author, "transfers": transfers,
                           "cash_before": {pid: cash_before[pid] for pid in parties},
                           "cash_after": {pid: cash[pid] for pid in parties},
                           "net_cash": {pid: flows[pid] for pid in parties},
                           "mortgage_interest": {pid: interest[pid] for pid in parties},
                           "new_groups": gained, "completion_sides": sum(bool(v) for v in gained.values())})
            i = j
            continue
        if typ == "AUCTION_STARTED":
            auction = True
        elif typ == "AUCTION_ENDED":
            auction = False
        route = "auction" if auction else "direct_purchase"
        change(e, route)
        # Inheritance is identified by the ownership transition, not price alone.
        if typ == "PROPERTY_PURCHASED":
            route = acquisitions[-1]["route"]
        update_episodes(before, e, route)
        i += 1
    terminal = any(e["type"] == "GAME_ENDED" for e in events)
    for episode in active.values():
        episode.update(end_seq_exclusive=len(events), end_reason="game_end" if terminal else "record_end")
    return {"owners": owners, "cash": cash, "deed_acquisitions": acquisitions,
            "group_episodes": episodes, "trades": trades}


def measure_episode(episode, events, menus, group_keys):
    """Measure an episode from recorded engine requests and saved legal menus.

    A missing menu raises. An absent management opportunity returns null build
    responsiveness. No inference of legality from cash, ownership or elapsed time.
    """
    pid = episode["player_id"]
    lower, upper = episode["settlement_end_seq"], episode["end_seq_exclusive"]
    future = [e for e in events if lower < e["seq"] < upper]
    requests = [e for e in future if e["type"] == "LLM_DECISION_REQUESTED"
                and e["payload"].get("player_id") == pid]
    management = [e for e in requests if e["payload"].get("decision_type") == MANAGEMENT]
    first = management[0] if management else None
    builds = [e for e in future if e["type"] in BUILD_EVENTS and e["payload"]["player_id"] == pid
              and e["payload"]["space_index"] in group_keys]
    build = builds[0] if builds else None
    result = {"first_management_turn": first["turn_index"] if first else None,
              "first_management_decision": first["payload"]["decision_id"] if first else None,
              "first_build_turn": build["turn_index"] if build else None,
              "first_build_event": build["event_id"] if build else None,
              "elapsed_to_management": first["turn_index"] - episode["acquisition_turn"] if first else None,
              "elapsed_to_build": build["turn_index"] - episode["acquisition_turn"] if build else None,
              "pre_management_decisions": [e["payload"] for e in requests
                                            if first is None or e["seq"] < first["seq"]],
              "rent_until_loss_or_end": sum(e["payload"]["amount"] for e in future
                  if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == pid
                  and e["payload"].get("space_index") in group_keys)}
    if first is None:
        result.update(entry_legal=None, later_legal_in_window=None, built_first_management=None,
                      access_status="lost_before_access" if episode["end_reason"] == "ownership_loss"
                      else "no_access_before_" + episode["end_reason"])
        return result
    end = next((e["seq"] for e in future if e["seq"] > first["seq"] and e["type"] == "TURN_ENDED"
                and e["turn_index"] == first["turn_index"]), upper)
    window_requests = [e for e in management if first["seq"] <= e["seq"] < end
                       and e["turn_index"] == first["turn_index"]]

    def legal(request):
        menu = menus[request["payload"]["decision_id"]]
        return ("build_houses_or_hotel" in menu["available_actions"] and
                bool(set(group_keys.values()) & set(menu.get("buildable_space_keys", []))))

    built = any(first["seq"] < e["seq"] < end and e["turn_index"] == first["turn_index"] for e in builds)
    complete = end < upper or episode["end_reason"] != "record_end"
    result.update(entry_legal=legal(first), later_legal_in_window=any(legal(r) for r in window_requests),
                  built_first_management=built if complete or built else None,
                  access_status="observed", window_complete=complete, window_end_seq_exclusive=end)
    return result
