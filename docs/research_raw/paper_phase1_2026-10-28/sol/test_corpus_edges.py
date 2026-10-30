"""Targeted real-record regressions, independent of generated output files.

These are finite boundary checks. They do not claim exhaustive social review.
"""
import csv
import json
from pathlib import Path

import pytest

from economics import reconstruct, measure_episode, space_key


ROOT = Path(__file__).resolve().parents[4]


def load(game):
    name = "railway-research-12-games-2026-10-25" if game <= 12 else "railway-research-8-games-2026-10-26"
    collection = ROOT / "saved_games" / name
    with (collection / "game-index.csv").open() as f:
        index = next(r for r in csv.DictReader(f) if int(r["collection_game"]) == game)
    run = collection / index["package"] / "run"
    cfg = json.loads((run / "run_config.json").read_text())
    events = [json.loads(line) for line in (run / "events.jsonl").open()]
    board = json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"]
    return run, cfg, events, board


@pytest.mark.parametrize("game,group,acquired,management,decision_tail,jail_actions", [
    (6, "PINK", 74, 85, "000159", ["roll_for_doubles", "roll_for_doubles"]),
    (8, "DARK_BLUE", 77, 87, "000182", ["roll_for_doubles", "pay_jail_fine"]),
])
def test_real_jail_windows(game, group, acquired, management, decision_tail, jail_actions):
    run, cfg, events, board = load(game)
    result = reconstruct(events, [p["player_id"] for p in cfg["players"]], board)
    episode = next(r for r in result["group_episodes"] if r["player_id"] == "p4" and r["group"] == group and r["route"] == "trade")
    menus, actions = {}, {}
    for d in map(json.loads, (run / "decisions.jsonl").open()):
        if d["phase"] == "decision_started":
            state = d["prompt_payload"]["action_state"]
            menus[d["decision_id"]] = {"available_actions": state["available_actions"],
                "buildable_space_keys": state.get("scenario", {}).get("options", {}).get("buildable_space_keys", [])}
        else:
            actions[d["decision_id"]] = d["final_action"]["action"]
    keys = {s["index"]: space_key(s["name"]) for s in board if s["group"] == group}
    measured = measure_episode(episode, events, menus, keys)
    assert episode["acquisition_turn"] == acquired
    assert measured["first_management_turn"] == measured["first_build_turn"] == management
    assert measured["first_management_decision"].endswith(decision_tail)
    assert measured["entry_legal"] and measured["built_first_management"]
    assert [actions[d["decision_id"]] for d in measured["pre_management_decisions"]] == jail_actions


def test_actual_mortgaged_trade_settlement_cash_boundary():
    _, cfg, events, board = load(1)
    result = reconstruct(events, [p["player_id"] for p in cfg["players"]], board)
    trade = next(t for t in result["trades"] if t["seq"] == 1989)
    assert trade["cash_before"] == {"p1": 68, "p4": 347}
    assert trade["cash_after"] == {"p1": 168, "p4": 229}
    assert trade["mortgage_interest"] == {"p1": 0, "p4": 18}
    assert trade["settlement_end_seq"] == 1994
    assert trade["new_groups"] == {"p1": [], "p4": ["ORANGE"]}


@pytest.mark.parametrize("game,model", [(14, "openai/gpt-6.1-sol"), (15, "google/gemini-4-argon")])
def test_nontrade_winners_are_real_purchase_routes(game, model):
    run, cfg, events, board = load(game)
    pid = next(p["player_id"] for p in cfg["players"] if p["openrouter_model_id"] == model)
    assert json.loads((run / "summary.json").read_text())["winner_player_id"] == pid
    result = reconstruct(events, [p["player_id"] for p in cfg["players"]], board)
    assert not any(pid in (t["thread_initiator"], t["thread_recipient"]) for t in result["trades"])
    orange = next(r for r in result["group_episodes"] if r["player_id"] == pid and r["group"] == "ORANGE")
    assert orange["acquisition_turn"] == 47 and orange["route"] == "direct_purchase"
    assert set(orange["constituent_last_routes"].values()) == {"direct_purchase"}
