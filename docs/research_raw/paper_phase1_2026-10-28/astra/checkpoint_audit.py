"""Independent accounting audit against every saved decision observation.

This reconstructs economic state from canonical events without importing either
the engine or the other researchers' reducers. It checks observation consistency,
not optimal strategy, latent intentions, or legality of the underlying rules.
"""
from __future__ import annotations

import collections
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def space_key(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


class Ledger:
    def __init__(self, player_ids, board, starting_cash=1500):
        self.cash = {pid: starting_cash for pid in player_ids}
        self.assets = {s["index"]: {"owner": None, "houses": 0, "hotel": False,
                       "mortgaged": False} for s in board if s.get("price") is not None}
        self.keys = {s["index"]: space_key(s["name"]) for s in board if s.get("price") is not None}
        self.bank_houses, self.bank_hotels = 32, 12

    def apply(self, event):
        kind, p = event["type"], event["payload"]
        if kind == "CASH_CHANGED":
            self.cash[p["player_id"]] += p["delta"]
            if p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
                for asset in self.assets.values():
                    if asset["owner"] == p["player_id"]:
                        self.bank_houses += asset["houses"]
                        self.bank_hotels += int(asset["hotel"])
                        asset.update(owner=None, houses=0, hotel=False, mortgaged=False)
        elif kind == "PROPERTY_PURCHASED":
            # Creditor inheritance preserves improvements and mortgage status.
            self.assets[p["space_index"]]["owner"] = p["player_id"]
        elif kind == "PROPERTY_TRANSFERRED":
            asset = self.assets[p["space_index"]]
            if asset["owner"] != p["from_player_id"]:
                raise ValueError("Recorded transfer does not match prior owner")
            asset["owner"] = p["to_player_id"]
            if asset["mortgaged"] != p["mortgaged"]:
                raise ValueError("Recorded transfer mortgage flag differs from prior state")
        elif kind in {"PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"}:
            self.assets[p["space_index"]]["mortgaged"] = kind == "PROPERTY_MORTGAGED"
        elif kind in {"HOUSE_BUILT", "HOUSE_SOLD"}:
            delta = p["count"] * (1 if kind == "HOUSE_BUILT" else -1)
            self.assets[p["space_index"]]["houses"] += delta
            self.bank_houses -= delta
        elif kind == "HOTEL_BUILT":
            asset = self.assets[p["space_index"]]
            self.bank_houses += asset["houses"]
            self.bank_hotels -= p["count"]
            asset.update(houses=0, hotel=True)
        elif kind == "HOTEL_SOLD":
            asset = self.assets[p["space_index"]]
            self.bank_houses -= 4
            self.bank_hotels += p["count"]
            asset.update(houses=4, hotel=False)

    def compare(self, observed):
        differences = []
        players = [observed["you"], *observed["others"]]
        observed_assets = {}
        def check(field, expected, actual):
            if expected != actual:
                differences.append({"field": field, "event_reconstruction": expected,
                                    "saved_observation": actual})
        for player in players:
            pid = player["player_id"]
            check(f"cash.{pid}", self.cash[pid], player["cash"])
            for holding in player["holdings"]["owned"]:
                key = holding["space_key"]
                if key in observed_assets:
                    raise ValueError("Duplicate asset in observed player holdings")
                observed_assets[key] = {"owner": pid, "houses": holding["houses"],
                                        "hotel": holding["hotel"], "mortgaged": holding["mortgaged"]}
            check(f"mortgage_list.{pid}",
                  sorted(self.keys[i] for i, a in self.assets.items()
                         if a["owner"] == pid and a["mortgaged"]),
                  sorted(item["space_key"] for item in player["holdings"]["mortgaged"]))
        for index, asset in self.assets.items():
            key = self.keys[index]
            actual = observed_assets.get(key, {"owner": None, "houses": 0, "hotel": False, "mortgaged": False})
            check("asset." + key, asset, actual)
        check("bank.houses_remaining", self.bank_houses, observed["bank"]["houses_remaining"])
        check("bank.hotels_remaining", self.bank_hotels, observed["bank"]["hotels_remaining"])
        check("bank.unowned_space_keys", sorted(self.keys[i] for i,a in self.assets.items() if a["owner"] is None),
              sorted(observed["bank"]["unowned_space_keys"]))
        return differences


def main():
    board = json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"]
    games, mismatches = [], []
    decision_count = 0
    for name in ("railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26"):
        collection = ROOT / "saved_games" / name
        with (collection / "game-index.csv").open() as stream:
            indexes = list(csv.DictReader(stream))
        for index in indexes:
            run = collection / index["package"] / "run"
            config = json.loads((run / "run_config.json").read_text())
            starts = {}
            with (run / "decisions.jsonl").open() as stream:
                for number, line in enumerate(stream, 1):
                    d = json.loads(line)
                    if d["phase"] == "decision_started":
                        starts[d["decision_id"]] = (number, d["prompt_payload"]["game_state"])
            ledger = Ledger([p["player_id"] for p in config["players"]], board)
            checked = set()
            group_counts = collections.Counter()
            with (run / "events.jsonl").open() as stream:
                for line in stream:
                    event = json.loads(line)
                    ledger.apply(event)
                    if event["type"] == "LLM_DECISION_REQUESTED":
                        did = event["payload"]["decision_id"]
                        source_line, observed = starts[did]
                        differences = ledger.compare(observed)
                        for difference in differences:
                            mismatches.append({"game": int(index["collection_game"]), "decision_id": did,
                                               "request_event": event["event_id"], "decision_line": source_line,
                                               **difference})
                        checked.add(did)
                        group_counts["checkpoints"] += 1
                        group_counts["mismatching_checkpoints"] += bool(differences)
            assert checked == set(starts), "Some decision observations were not checked"
            decision_count += len(checked)
            games.append({"game": int(index["collection_game"]), "run_id": config["run_id"],
                          **group_counts})
    report = {"method": "independent_event_accounting_vs_all_started_decision_observations",
              "games": games, "decisions_checked": decision_count,
              "mismatching_fields": len(mismatches), "mismatches": mismatches,
              "checked_fields": ["all_player_cash", "all_deed_owners", "houses", "hotels",
                                 "mortgages", "bank_building_inventory", "unowned_deeds"],
              "not_established": ["rule_correctness", "strategy_quality", "semantic_behavior_labels",
                                  "latent_intent", "causal_effects"]}
    (OUT / "checkpoint_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k:report[k] for k in ("decisions_checked", "mismatching_fields")}, indent=2))
    if mismatches:
        print(json.dumps(mismatches[:5], indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
