"""Positions immediately before each game's first estate transfer.

For every game, the first BANKRUPTCY cash event identifies the first
elimination. Its creditor is read from the debtor's liquidation menu or,
if none, from the BANKRUPTCY_CASH recipient. Standing is measured from
events replayed up to (not including) the first BANKRUPTCY_CASH event:
cash, deed holdings, buildings, mortgages and cumulative rent received.
Holdings are reconstructed from purchase, auction, trade and building
events; at that point no estate has moved, so no inheritance rule is used.
The reconstruction is checked against the last turn-start snapshot.

Standing measures (all in game dollars):
  asset value = cash + list price of unmortgaged deeds + half list price of
                mortgaged deeds + building cost of houses/hotels
  developed groups = complete colour groups with at least one building
  rent received = cumulative RENT_PAID to the player
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"
COLOR = ["BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED", "YELLOW", "GREEN", "DARK_BLUE"]


class Tracker:
    def __init__(self, spaces, groups, by_index, players):
        self.s, self.g, self.bi = spaces, groups, by_index
        self.cash = {p: 1500 for p in players}
        self.owner = {}
        self.mort = set()
        self.houses = defaultdict(int)  # 5 = hotel
        self.rent_in = defaultdict(int)
        self.rent_out = defaultdict(int)
        self.alive = set(players)

    def apply(self, e):
        t, p = e["type"], e["payload"]
        if t == "CASH_CHANGED":
            self.cash[p["player_id"]] += p["delta"]
        elif t == "PROPERTY_PURCHASED":
            self.owner[self.bi[p["space_index"]]] = p["player_id"]
        elif t == "AUCTION_ENDED" and p.get("winner_player_id"):
            self.owner[corpus.normalize_key(p["property_space"]) if p["property_space"] not in self.s else p["property_space"]] = p["winner_player_id"]
        elif t == "PROPERTY_TRANSFERRED":
            self.owner[self.bi[p["space_index"]]] = p["to_player_id"]
        elif t == "PROPERTY_MORTGAGED":
            self.mort.add(self.bi[p["space_index"]])
        elif t == "PROPERTY_UNMORTGAGED":
            self.mort.discard(self.bi[p["space_index"]])
        elif t == "HOUSE_BUILT":
            self.houses[self.bi[p["space_index"]]] += p.get("count", 1)
        elif t == "HOTEL_BUILT":
            self.houses[self.bi[p["space_index"]]] = 5
        elif t == "HOUSE_SOLD":
            self.houses[self.bi[p["space_index"]]] -= p.get("count", 1)
        elif t == "HOTEL_SOLD":
            self.houses[self.bi[p["space_index"]]] = 4
        elif t == "RENT_PAID":
            self.rent_in[p["to_player_id"]] += p["amount"]
            self.rent_out[p["from_player_id"]] += p["amount"]

    def standing(self, pid):
        deeds = [k for k, o in self.owner.items() if o == pid]
        val = self.cash[pid]
        for k in deeds:
            val += self.s[k]["price"] // 2 if k in self.mort else self.s[k]["price"]
            if self.s[k]["house_cost"]:
                val += self.s[k]["house_cost"] * self.houses[k]
        complete = [c for c in COLOR if all(self.owner.get(k) == pid for k in self.g[c])]
        developed = [c for c in complete if any(self.houses[k] > 0 for k in self.g[c])]
        bldg = sum(self.houses[k] for k in deeds)
        return {"cash": self.cash[pid], "asset_value": val, "deeds": len(deeds), "complete": complete,
                "developed": developed, "buildings": bldg, "rent_in": self.rent_in[pid], "rent_out": self.rent_out[pid]}


def main():
    D = corpus.build_cache()
    spaces, groups, by_index = corpus.board()
    rows = []
    for g, game in D["games"].items():
        players = sorted(game["pmodel"])
        tr = Tracker(spaces, groups, by_index, players)
        first = None
        turn_of_first = None
        for e in game["events"]:
            if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") in ("BANKRUPTCY_CASH", "BANKRUPTCY", "BANKRUPTCY_ASSETS_TO_BANK"):
                first = e
                break
            tr.apply(e)
        debtor = first["payload"]["player_id"]
        turn_of_first = first["turn_index"]
        # creditor from the liquidation menu of the debtor in that turn, else from the paired cash event
        creditor = None
        for idx, d in sorted(game["decisions"].items()):
            if d["type"] == "LIQUIDATION_DECISION" and d["player"] == debtor and d["turn"] == turn_of_first:
                creditor = d["payload"]["action_state"]["scenario"].get("owed_to_player_id")
        # snapshot check at the last turn-start before the elimination
        snap_path = corpus.REPO / game["run"] / "state" / f"turn_{turn_of_first:04d}.json"
        snap = json.loads(snap_path.read_text())
        st = {p: tr.standing(p) for p in players}
        ranking = sorted(players, key=lambda p: -st[p]["asset_value"])
        rent_rank = sorted(players, key=lambda p: -st[p]["rent_in"])
        leader = ranking[0]
        rows.append({
            "game": g, "turn": turn_of_first, "debtor": debtor, "debtor_model": game["pmodel"][debtor],
            "creditor": creditor, "creditor_model": game["pmodel"].get(creditor) if creditor else "Bank",
            "winner": game["winner"], "winner_model": game["pmodel"][game["winner"]],
            "asset_leader": leader, "asset_leader_model": game["pmodel"][leader],
            "rent_leader": rent_rank[0],
            "creditor_rank_assets": ranking.index(creditor) + 1 if creditor else None,
            "creditor_rank_rent": rent_rank.index(creditor) + 1 if creditor else None,
            "winner_rank_assets": ranking.index(game["winner"]) + 1,
            "creditor_developed": st[creditor]["developed"] if creditor else None,
            "standing": {game["pmodel"][p] + "/" + p: st[p] for p in players},
            "snapshot_turn_start_cash": {p["player_id"]: p["cash"] for p in snap["players"]},
            "snapshot": str(snap_path.relative_to(corpus.REPO)),
            "snapshot_sha256": corpus.sha256(snap_path),
        })
    summ = {
        "games": len(rows),
        "first_creditor_is_winner": sum(r["creditor"] == r["winner"] for r in rows),
        "first_creditor_is_asset_leader": sum(r["creditor"] == r["asset_leader"] for r in rows),
        "first_creditor_is_rent_leader": sum(r["creditor"] == r["rent_leader"] for r in rows),
        "asset_leader_is_winner": sum(r["asset_leader"] == r["winner"] for r in rows),
        "creditor_has_developed_group": sum(bool(r["creditor_developed"]) for r in rows),
        "creditor_rank_assets": [r["creditor_rank_assets"] for r in rows],
        "winner_rank_assets": [r["winner_rank_assets"] for r in rows],
        "turn": [r["turn"] for r in rows],
    }
    (OUT / "first_estates.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
    print(json.dumps(summ, indent=1))
    for r in rows:
        print(r["game"], r["turn"], r["debtor_model"], "->", r["creditor_model"], "winner", r["winner_model"], "leader", r["asset_leader_model"],
              "cred_rank", r["creditor_rank_assets"], "rent_rank", r["creditor_rank_rent"], "win_rank", r["winner_rank_assets"],
              {k: (v["asset_value"], v["rent_in"], len(v["developed"])) for k, v in r["standing"].items()})


if __name__ == "__main__":
    main()
