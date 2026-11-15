"""Completion episodes: timing, development and rent exposure.

An episode begins when a player newly owns every deed of a colour group
(mortgaged deeds count) and ends when it no longer does, is eliminated, or
the game ends. Route = the acquisition that completed the group (trade,
purchase, auction, estate). Using the snapshot-validated event tracker:

  owner_turns_to_build  number of the owner's own turns started after
                        completion before its first HOUSE_BUILT on the group
                        (0 = built in the turn of completion)
  opp_landings          PLAYER_MOVED arrivals of other players on the group
  landings_developed    arrivals while the group carries >= 1 building
  rent                  RENT_PAID to the owner on the group's deeds
  rent_eliminations     eliminations whose debt was rent owed to this owner
                        on this group (debtor's liquidation menu, reason RENT,
                        debtor position on the group)

Exposure (landings) is an observed count, not an expectation.
"""
from __future__ import annotations

import json
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

import corpus
from track import Board, COLOR

OUT = Path(__file__).resolve().parents[1] / "data"


def main():
    D = corpus.build_cache()
    spaces, groups, by_index = corpus.board()
    idx_group = {spaces[k]["index"]: spaces[k]["group"] for k in spaces}
    eps = []
    for g, game in D["games"].items():
        b = Board(game, spaces, groups, by_index)
        active = {}  # (pid, color) -> episode dict
        pos = {}
        turn_player = {}
        last_turn = 0
        # active player per turn from first PLAYER actor
        for e in game["events"]:
            if e["actor"]["kind"] == "PLAYER" and e["turn_index"] not in turn_player and e["type"] in ("DICE_ROLLED", "LLM_DECISION_REQUESTED", "PLAYER_MOVED"):
                turn_player[e["turn_index"]] = e["actor"]["player_id"]
        evs = game["events"]
        pending_before = None
        pending_route = None
        for i, e in enumerate(evs):
            t, p = e["type"], e["payload"]
            last_turn = e["turn_index"]
            before = pending_before if pending_before is not None else {pid: set(b.complete(pid)) for pid in b.cash}
            ch = b.apply(e)
            if ch and ch[0] == "acquire" and ch[3] == "purchase" and i + 2 < len(evs) and any(
                    x["type"] == "AUCTION_ENDED" for x in evs[i + 1:i + 3]):
                ch = ("acquire", ch[1], ch[2], "auction")
            # a trade settlement is evaluated atomically after its last transfer/cash event
            nxt = evs[i + 1] if i + 1 < len(evs) else None
            in_settlement = t in ("PROPERTY_TRANSFERRED", "CASH_CHANGED", "TRADE_ACCEPTED") and (pending_before is not None or t == "TRADE_ACCEPTED") and nxt is not None and (
                nxt["type"] == "PROPERTY_TRANSFERRED" or (nxt["type"] == "CASH_CHANGED" and nxt["payload"].get("reason") in ("TRADE_CASH", "MORTGAGE_INTEREST")))
            if in_settlement:
                pending_before = before
                if ch and ch[0] == "acquire":
                    pending_route = ch
                continue
            if pending_before is not None and ch is None and pending_route is not None:
                ch = pending_route
            pending_before, pending_route = None, None
            after = {pid: set(b.complete(pid)) for pid in b.cash}
            # closures
            for (pid, c), ep in list(active.items()):
                if c not in after.get(pid, set()) or pid not in b.alive:
                    ep["end_turn"] = e["turn_index"]
                    ep["end_reason"] = "eliminated" if pid not in b.alive else "lost_group"
                    eps.append(ep)
                    del active[(pid, c)]
            # openings
            for pid in b.cash:
                for c in after[pid] - before[pid]:
                    route = None
                    if ch and ch[0] == "acquire":
                        route = ch[3]
                    elif ch and ch[0] == "estate":
                        route = "estate"
                    terminal = False
                    active[(pid, c)] = {"game": g, "owner": pid, "model": game["pmodel"][pid], "color": c, "route": route,
                                        "start_turn": e["turn_index"], "start_seq": e["seq"], "first_build_turn": None,
                                        "owner_turns_to_build": None, "owner_turns_seen": 0, "opp_landings": 0,
                                        "landings_developed": 0, "rent": 0, "rent_developed": 0, "build_spend": 0, "landing_log": [], "rent_log": [],
                                        "winner": game["winner"] == pid, "mortgaged_at_start": sum(k in b.mort for k in groups[c])}
            if t == "TURN_STARTED":
                for (pid, c), ep in active.items():
                    if turn_player.get(e["turn_index"]) == pid and e["turn_index"] > ep["start_turn"]:
                        ep["owner_turns_seen"] += 1
            if t in ("HOUSE_BUILT", "HOTEL_BUILT"):
                k = by_index[p["space_index"]]
                c = spaces[k]["group"]
                ep = active.get((p["player_id"], c))
                if ep is not None:
                    if ep["first_build_turn"] is None:
                        ep["first_build_turn"] = e["turn_index"]
                        ep["owner_turns_to_build"] = ep["owner_turns_seen"]
            if t == "CASH_CHANGED" and p.get("reason") == "BUILD":
                pass
            if t == "PLAYER_MOVED":
                mover = e["actor"]["player_id"]
                dest = p["to"]
                c = idx_group.get(dest)
                if c in COLOR:
                    for (pid, cc), ep in active.items():
                        if cc == c and pid != mover:
                            ep["opp_landings"] += 1
                            dev = any(b.houses[k] > 0 for k in groups[c])
                            ep["landing_log"].append([e["turn_index"], dev])
                            if dev:
                                ep["landings_developed"] += 1
            if t == "RENT_PAID":
                c = idx_group.get(p["space_index"])
                ep = active.get((p["to_player_id"], c))
                if ep is not None:
                    ep["rent"] += p["amount"]
                    ep["rent_log"].append([e["turn_index"], p["amount"]])
                    if any(b.houses[k] > 0 for k in groups[c]):
                        ep["rent_developed"] += p["amount"]
        for (pid, c), ep in active.items():
            ep["end_turn"] = last_turn
            ep["end_reason"] = "game_end"
            eps.append(ep)
    # terminal estates: completed by the final elimination (no later play)
    for ep in eps:
        ep["duration_turns"] = ep["end_turn"] - ep["start_turn"]
        ep["terminal"] = ep["route"] == "estate" and ep["end_reason"] == "game_end" and ep["duration_turns"] == 0
    # summaries
    def summarize(sel):
        built = [x for x in sel if x["first_build_turn"] is not None]
        delays = [x["owner_turns_to_build"] for x in built]
        return {"episodes": len(sel), "built_ever": len(built),
                "built_owner_turn_0or1": sum(d <= 1 for d in delays),
                "median_owner_turns_to_build": st.median(delays) if delays else None,
                "median_duration_turns": st.median([x["duration_turns"] for x in sel]) if sel else None,
                "opp_landings": sum(x["opp_landings"] for x in sel), "landings_developed": sum(x["landings_developed"] for x in sel),
                "rent": sum(x["rent"] for x in sel), "rent_developed": sum(x["rent_developed"] for x in sel),
                "winner_owned": sum(x["winner"] for x in sel)}
    S = {}
    for route in ("trade", "purchase", "auction", "estate"):
        sel = [x for x in eps if x["route"] == route and not x["terminal"]]
        S[route] = summarize(sel)
    S["estate_terminal"] = {"episodes": sum(x["terminal"] for x in eps)}
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        S[f"trade|{m}"] = summarize([x for x in eps if x["route"] == "trade" and x["model"] == m])
    tr = [x for x in eps if x["route"] == "trade"]
    # rent per opponent landing, split by development state
    S["trade_rent_per_landing"] = {
        "developed": round(sum(x["rent_developed"] for x in tr) / max(1, sum(x["landings_developed"] for x in tr)), 1),
        "undeveloped": round((sum(x["rent"] for x in tr) - sum(x["rent_developed"] for x in tr)) / max(1, sum(x["opp_landings"] - x["landings_developed"] for x in tr)), 1)}
    (OUT / "completion_episodes.json").write_text(json.dumps({"summary": S, "episodes": eps}, indent=1))
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
