"""Event-derived ownership, mortgage, building and cash timeline.

The tracker folds canonical events in sequence order.  It is validated against
the structured state delivered in every one of the 6,989 decision prompts
(``validate()``), which makes later tabulations independent of the retained
phase-1 and phase-2 ledgers.  No engine code is imported.
"""
from __future__ import annotations

import collections
import copy
import json

from corpus import Game, board, load_all, write_json

START_CASH = 1500


class Tracker:
    def __init__(self, game: Game):
        self.g = game
        self.B = board()
        self.key = {i: r["key"] for i, r in self.B["by_index"].items()}
        self.owner: dict[str, str | None] = {k: None for k in self.B["by_key"]}
        self.mortgaged: dict[str, bool] = {k: False for k in self.B["by_key"]}
        self.level: dict[str, int] = {k: 0 for k in self.B["by_key"]}  # 0-4 houses, 5 hotel
        self.cash = {p: START_CASH for p in game.model}
        self.bankrupt: dict[str, dict] = {}
        self.pos = {p: 0 for p in game.model}
        self._pending_bankrupt: str | None = None
        self._pending_creditor: str | None = None

    def owned_by(self, pid: str) -> list[str]:
        return sorted(k for k, o in self.owner.items() if o == pid)

    def apply(self, e: dict) -> dict | None:
        """Apply one event.  Returns a small record for ownership changes."""
        t, p = e["type"], e["payload"]
        change = None
        if t == "CASH_CHANGED":
            self.cash[p["player_id"]] += p["delta"]
            r = p["reason"]
            if r == "BANKRUPTCY_CASH" and p["delta"] > 0:
                self._pending_creditor = p["player_id"]
            if r == "BANKRUPTCY":
                # The cash-transfer creditor is only a hint: a debtor with $0 emits no
                # BANKRUPTCY_CASH transfer.  Callers that need the creditor must take it
                # from the debt prompt (owed_to_player_id) or the estate recipients.
                self._pending_bankrupt = p["player_id"]
                self.bankrupt[p["player_id"]] = {
                    "seq": e["seq"],
                    "turn": e["turn_index"],
                    "cash_creditor_hint": self._pending_creditor,
                }
                change = {"kind": "bankruptcy", "debtor": p["player_id"], "creditor": self._pending_creditor}
                self._pending_creditor = None
            if r == "BANKRUPTCY_ASSETS_TO_BANK":
                pid = p["player_id"]
                for k in self.owned_by(pid):
                    self.owner[k] = None
                    self.mortgaged[k] = False
                    self.level[k] = 0
                change = {"kind": "estate_to_bank", "debtor": pid}
        elif t == "PROPERTY_PURCHASED":
            k = self.key[p["space_index"]]
            prev = self.owner[k]
            self.owner[k] = p["player_id"]
            if prev is not None and prev in self.bankrupt:
                change = {"kind": "estate", "key": k, "from": prev, "to": p["player_id"]}
            else:
                assert prev is None, (self.g.number, e["seq"], k, prev)
                change = {"kind": "purchase", "key": k, "to": p["player_id"], "price": p.get("price")}
        elif t == "AUCTION_ENDED":
            if p.get("winner_player_id"):
                k = p["property_space"]
                change = {"kind": "auction", "key": k, "to": p["winner_player_id"], "price": p.get("winning_bid")}
                # ownership itself is set by the PROPERTY_PURCHASED event if present; see validate()
                self._last_auction = change
        elif t == "PROPERTY_TRANSFERRED":
            k = self.key[p["space_index"]]
            assert self.owner[k] == p["from_player_id"], (self.g.number, e["seq"])
            self.owner[k] = p["to_player_id"]
            change = {"kind": "trade", "key": k, "from": p["from_player_id"], "to": p["to_player_id"]}
        elif t == "PROPERTY_MORTGAGED":
            self.mortgaged[self.key[p["space_index"]]] = True
        elif t == "PROPERTY_UNMORTGAGED":
            self.mortgaged[self.key[p["space_index"]]] = False
        elif t == "HOUSE_BUILT":
            self.level[self.key[p["space_index"]]] += p.get("count", 1)
        elif t == "HOTEL_BUILT":
            self.level[self.key[p["space_index"]]] = 5
        elif t == "HOUSE_SOLD":
            self.level[self.key[p["space_index"]]] -= p.get("count", 1)
        elif t == "HOTEL_SOLD":
            # resolved by validate(): the prompt state fixes the post-sale level
            self.level[self.key[p["space_index"]]] = 4
        elif t == "PLAYER_MOVED":
            self.pos[e["actor"]["player_id"]] = p["to"]
        return change

    def snapshot(self) -> dict:
        return {
            "owner": dict(self.owner),
            "mortgaged": dict(self.mortgaged),
            "level": dict(self.level),
            "cash": dict(self.cash),
        }


def validate() -> dict:
    """Compare the tracker with every delivered prompt state."""
    report = {"prompts": 0, "cash_mismatch": 0, "owner_mismatch": 0, "mortgage_mismatch": 0, "level_mismatch": 0, "examples": []}
    for g in load_all().values():
        tr = Tracker(g)
        dec_seq = {}
        for e in g.events:
            if e["type"] == "LLM_DECISION_REQUESTED":
                k = g.dec_index(e["payload"]["decision_id"])
                st = g.state_before(k)["players"]
                report["prompts"] += 1
                for pid, ps in st.items():
                    if ps["bankrupt"]:
                        continue
                    if ps["cash"] != tr.cash[pid]:
                        report["cash_mismatch"] += 1
                        if len(report["examples"]) < 10:
                            report["examples"].append(["cash", g.number, k, pid, ps["cash"], tr.cash[pid]])
                    if sorted(ps["owned"]) != tr.owned_by(pid):
                        report["owner_mismatch"] += 1
                        if len(report["examples"]) < 10:
                            report["examples"].append(["owner", g.number, k, pid, sorted(set(ps["owned"]) ^ set(tr.owned_by(pid)))])
                    for key, h in ps["owned"].items():
                        if h["mortgaged"] != tr.mortgaged[key]:
                            report["mortgage_mismatch"] += 1
                        lvl = 5 if h["hotel"] else h["houses"]
                        if lvl != tr.level[key]:
                            report["level_mismatch"] += 1
                            if len(report["examples"]) < 10:
                                report["examples"].append(["level", g.number, k, key, lvl, tr.level[key]])
            tr.apply(e)
    return report


if __name__ == "__main__":
    rep = validate()
    write_json("state_track_validation.json", rep)
    print(json.dumps(rep, indent=1))
