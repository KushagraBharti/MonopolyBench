"""Reconcile the integration's hand-typeset cells and G2 rent statement."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
REPO = BASE.parents[2]
inputs = {}


def read(path, lines=False):
    raw = path.read_bytes()
    inputs[str(path.relative_to(REPO))] = hashlib.sha256(raw).hexdigest()
    return [json.loads(s) for s in raw.splitlines()] if lines else json.loads(raw)


offers = read(BASE / "data/agenda_offers.json")
cells = defaultdict(Counter)
styles = defaultdict(Counter)
for row in offers:
    styles[row["recipient_model"]][row["response"]] += 1
    if row["accept_available"]:
        cells[row["completion_cell"]][row["response"]] += 1
expected_cells = {
    "author_only": [289, 19, 111, 159],
    "recipient_only": [140, 24, 78, 38],
    "both": [81, 10, 35, 36],
    "neither": [408, 60, 169, 179],
}
expected_styles = {
    "Sol": [235, 30, 140, 65], "Gemini": [242, 26, 36, 180],
    "Opus": [189, 29, 141, 19], "Grok": [254, 28, 77, 149],
}
types = ("accept_trade", "counter_trade", "reject_trade")
for observed, expected in ((cells, expected_cells), (styles, expected_styles)):
    for key, values in expected.items():
        assert [sum(observed[key].values())] + [observed[key][k] for k in types] == values
cohort = read(BASE / "data/t01_cohort.json")
winners = {r["game"]: r["winner"] for r in cohort}
episodes = read(BASE.parent / "paper_phase1_2026-10-28/sol/group_episodes.jsonl", True)
routes = defaultdict(lambda: [0, 0])
for row in episodes:
    route = row["route"]
    if route == "creditor_inheritance":
        route = "terminal_estate" if row["access_status"] == "no_access_before_game_end" else "nonterminal_estate"
    routes[route][0] += 1
    routes[route][1] += int(row["model"] == winners[row["game"]])
assert dict(routes) == {"trade": [63, 18], "direct_purchase": [16, 12], "auction": [9, 2],
                        "nonterminal_estate": [52, 45], "terminal_estate": [69, 69]}

g2_events_path = REPO / "saved_games/railway-research-12-games-2026-10-25/game-02-102turns-270aabe8/run/events.jsonl"
events = read(g2_events_path, True)
event = next(e for e in events if e["seq"] == 1566)
assert event["type"] == "RENT_PAID" and event["turn_index"] == 77
assert event["payload"] == {"from_player_id": "p2", "to_player_id": "p1", "amount": 44, "space_index": 26}
episode = next(r for r in episodes if r["game"] == 2 and r["model"] == "Sol" and r["group"] == "YELLOW")
assert episode["rent_until_loss_or_end"] == 44
units = read(BASE / "data/t05_spending_units.json")
unit = next(r for r in units if r["game"] == 2 and r["configuration"] == "Sol" and r["group"] == "YELLOW")
assert [unit[k] for k in ("spend", "sale_proceeds", "paid_developed_rent_whole_game")] == [300, 150, 0]

report = {"scope": "Existing-ledger re-tabulation and one original rent-event check; no engine or model execution.",
          "offer_cells": expected_cells, "recipient_styles": expected_styles, "completion_routes": dict(routes),
          "g2_rent_event": event, "g2_completion_rent": 44,
          "g2_outlay_salvage_developed_rent": [300, 150, 0], "inputs": inputs,
          "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE / "qa/retained_table_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print("Offer cells, recipient styles, completion routes and original G2 rent event agree.")
