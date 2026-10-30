"""Mechanical candidate screen only; no semantic denial or motive labels."""

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from monopoly_engine.engine import HOUSE_COST_BY_GROUP

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEDGER = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"


def main():
    board = json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"]
    groups = defaultdict(set)
    for space in board:
        if space.get("group") in HOUSE_COST_BY_GROUP:
            groups[space["group"]].add(re.sub(r"[^A-Z0-9]+", "_", space["name"].upper()).strip("_"))
    cache, hits, hashes = {}, [], {}
    for line in LEDGER.read_text().splitlines():
        unit = json.loads(line)
        path = ROOT / unit["packet"]
        if path not in cache:
            data = path.read_bytes()
            hashes[unit["packet"]] = hashlib.sha256(data).hexdigest()
            cache = {path: [json.loads(x) for x in data.splitlines()]}
        packet = cache[path][unit["packet_line"] - 1]
        if packet["applied_action_record"]["decision_type"] != "POST_TURN_ACTION_DECISION":
            continue
        state = packet["initial_prompt"]["payload"]["game_state"]
        player = state["you"]
        if state["bank"]["houses_remaining"] != 0:
            continue
        owned = {r["space_key"]: r for r in player["holdings"]["owned"]}
        for group, keys in groups.items():
            if not keys.issubset(owned):
                continue
            values = [owned[k] for k in keys]
            if (any(v["mortgaged"] for v in values)
                    or min(5 if v["hotel"] else v["houses"] for v in values) >= 4
                    or player["cash"] < HOUSE_COST_BY_GROUP[group]):
                continue
            hits.append({"game": unit["game"], "decision_id": unit["decision_id"],
                         "turn": packet["turn_index"], "player": player["player_id"],
                         "model": packet["model"], "group": group, "cash": player["cash"],
                         "bank": 0, "source_unit": unit,
                         "levels": [[k, owned[k]["houses"], owned[k]["hotel"]] for k in sorted(keys)]})
    report = {
        "scope": "Mechanical public-state group/decision candidates, not semantic denial episodes. Includes constraints created by the actor's own holdings.",
        "hits": hits, "packet_sha256": hashes,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
    }
    (HERE / "supply_screen.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"{len(hits)} mechanical group/decision candidates; no semantic labels assigned")


if __name__ == "__main__":
    main()
