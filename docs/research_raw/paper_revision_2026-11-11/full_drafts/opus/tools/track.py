"""Event-sourced board tracker with estate transfers, validated on snapshots.

State is rebuilt from events only. On a player's BANKRUPTCY cash event,
the debtor's deeds (with buildings and mortgage flags) move to the creditor
named in the debtor's liquidation menu for that turn, or return to the
bank (unowned, unmortgaged, no buildings) when the creditor is the bank.
`validate()` compares cash, owner, mortgage and building counts with every
turn-start snapshot in state/ and reports mismatches.
"""
from __future__ import annotations

import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import corpus

COLOR = ["BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED", "YELLOW", "GREEN", "DARK_BLUE"]


class Board:
    def __init__(self, game, spaces, groups, by_index):
        self.s, self.g, self.bi = spaces, groups, by_index
        self.game = game
        players = sorted(game["pmodel"])
        self.cash = {p: 1500 for p in players}
        self.owner, self.mort, self.houses = {}, set(), defaultdict(int)
        self.alive = set(players)
        self.creditor = {}
        for idx, d in game["decisions"].items():
            if d["type"] == "LIQUIDATION_DECISION":
                sc = d["payload"]["action_state"]["scenario"]
                self.creditor[(d["player"], d["turn"])] = sc.get("owed_to_player_id")

    def key(self, x):
        if isinstance(x, int):
            return self.bi[x]
        return x if x in self.s else corpus.normalize_key(x)

    def apply(self, e):
        t, p = e["type"], e["payload"]
        changed = None
        if t == "CASH_CHANGED":
            self.cash[p["player_id"]] += p["delta"]
            if p.get("reason") in ("BANKRUPTCY", "BANKRUPTCY_ASSETS_TO_BANK") and p["player_id"] in self.alive:
                debtor = p["player_id"]
                cred = self.creditor.get((debtor, e["turn_index"]))
                deeds = [k for k, o in self.owner.items() if o == debtor]
                for k in deeds:
                    if cred:
                        self.owner[k] = cred
                    else:
                        del self.owner[k]
                        self.mort.discard(k)
                        self.houses[k] = 0
                self.alive.discard(debtor)
                changed = ("estate", debtor, cred, deeds)
        elif t == "PROPERTY_PURCHASED":
            self.owner[self.bi[p["space_index"]]] = p["player_id"]
            changed = ("acquire", p["player_id"], [self.bi[p["space_index"]]], "purchase")
        elif t == "AUCTION_ENDED" and p.get("winner_player_id"):
            k = self.key(p["property_space"])
            self.owner[k] = p["winner_player_id"]
            changed = ("acquire", p["winner_player_id"], [k], "auction")
        elif t == "PROPERTY_TRANSFERRED":
            k = self.bi[p["space_index"]]
            self.owner[k] = p["to_player_id"]
            changed = ("acquire", p["to_player_id"], [k], "trade")
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
        return changed

    def complete(self, pid):
        return [c for c in COLOR if all(self.owner.get(k) == pid for k in self.g[c])]


def validate(game, spaces, groups, by_index):
    snaps = {}
    for f in glob.glob(str(corpus.REPO / game["run"] / "state" / "turn_*.json")):
        m = re.search(r"turn_(\d+)\.json$", f)
        if m:
            snaps[int(m.group(1))] = f
    b = Board(game, spaces, groups, by_index)
    mism = defaultdict(int)
    checked = 0
    evs = game["events"]
    for i, e in enumerate(evs):
        if e["type"] == "TURN_STARTED" and e["turn_index"] in snaps:
            snap = json.loads(Path(snaps[e["turn_index"]]).read_text())
            checked += 1
            for pl in snap["players"]:
                if pl["cash"] != b.cash[pl["player_id"]]:
                    mism["cash"] += 1
            for sp in snap["board"]:
                if sp["kind"] not in ("PROPERTY", "RAILROAD", "UTILITY"):
                    continue
                k = by_index[sp["index"]]
                if sp["owner_id"] != b.owner.get(k):
                    mism["owner"] += 1
                if bool(sp["mortgaged"]) != (k in b.mort):
                    mism["mortgaged"] += 1
                h = 5 if sp["hotel"] else sp["houses"]
                if h != b.houses[k]:
                    mism["buildings"] += 1
        b.apply(e)
    return checked, dict(mism)


if __name__ == "__main__":
    D = corpus.build_cache()
    spaces, groups, by_index = corpus.board()
    tot = 0
    allm = defaultdict(int)
    for g, game in D["games"].items():
        c, m = validate(game, spaces, groups, by_index)
        tot += c
        for k, v in m.items():
            allm[k] += v
        print(g, c, m)
    print("snapshots checked", tot, dict(allm))
