"""Unpaid review probes. Reads canonical artifacts; writes only --out.

From python/: uv run --frozen python ../docs/research_raw/review_2026-09-22/probes.py
Private helper probes establish implementation behavior, not full scenario coverage.
"""

import argparse
import copy
import csv
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from monopoly_arena.baselines import BASELINE_IDS, choose_baseline_action
from monopoly_arena.decision_resolver import validate_decision_action
from monopoly_arena.long_campaign import build_campaign_plan, _completed_run_exists
from monopoly_arena.replay_verification import build_replay_verification_reports
from monopoly_engine import Engine
from monopoly_engine.board import HOUSE_COST_BY_GROUP, SPACE_INDEX_BY_KEY
from monopoly_microbench.scorer import _cash_after_action, score_action
from monopoly_telemetry.scorecard import _rank_players


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("/tmp/monopolybench-review-probes.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    out = {"schema_version": "research_review_probes_v1", "provider_calls": 0}
    ledger = root / "docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv"
    replay = []
    with ledger.open() as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        if row["saved_game"] == "TOTAL":
            continue
        directory = root / "saved_games" / row["saved_game"] / "run"
        # No RunFiles factory: its constructor helper creates state directories.
        files = SimpleNamespace(
            run_id=row["run_id"], events_path=directory / "events.jsonl",
            actions_path=directory / "actions.jsonl", run_config_path=directory / "run_config.json",
        )
        actions = [json.loads(line) for line in files.actions_path.read_text().splitlines() if line.strip()]
        decisions = [json.loads(line) for line in (directory / "decisions.jsonl").read_text().splitlines() if line.strip()]
        starts = [item["decision_id"] for item in decisions if item.get("phase") == "decision_started"]
        action_ids = [item["decision_id"] for item in actions]
        reports = build_replay_verification_reports(files)
        replay.append({
            "saved_game": row["saved_game"], "actions": len(actions),
            "decision_start_rows": len(starts), "unique_decision_starts": len(set(starts)),
            "duplicate_start_ids": [key for key, count in Counter(starts).items() if count > 1],
            "decision_action_id_sets_match": set(starts) == set(action_ids),
            "unique_actions": len(action_ids) == len(set(action_ids)),
            "state": reports["state_replay_report"]["status"],
            "artifact": reports["artifact_replay_report"]["status"],
            "artifact_first_mismatch": reports["artifact_replay_report"].get("first_mismatch_index"),
        })
    out["saved_replay"] = replay
    failures, text_weights, label_changes, build_cash = [], [], [], []
    checks = 0
    for path in sorted((root / "contracts/micro/scenarios").glob("*.json")):
        scenario = json.loads(path.read_text())
        decision = scenario["decision_point"]
        for baseline in sorted(BASELINE_IDS):
            action = choose_baseline_action(decision, baseline)
            errors = validate_decision_action(decision, action)
            checks += 1
            if errors:
                failures.append({"scenario": path.stem, "baseline": baseline, "errors": errors})
        rubric = scenario["evaluation"]["rubric"]
        total = sum(item["max_points"] for item in rubric)
        text_points = sum(item["max_points"] for item in rubric if item["type"] in {"private_thought_mentions", "public_message_nonempty"})
        if text_points:
            text_weights.append(text_points / total)
        action = choose_baseline_action(decision, "builder")
        action["public_message"] = ""
        action["private_thought"] = ""
        before = score_action(scenario, action)
        action["public_message"] = "message"
        action["private_thought"] = " ".join(str(term) for item in rubric if item["type"] == "private_thought_mentions" for term in item.get("params", {}).get("terms", []))
        after = score_action(scenario, action)
        if before["label"] != after["label"]:
            label_changes.append({"scenario": path.stem, "before": before["total"], "after": after["total"], "from": before["label"], "to": after["label"]})
        if action["action"] == "build_houses_or_hotel":
            board = decision["state"]["board"]
            cash = next(player["cash"] for player in decision["state"]["players"] if player["player_id"] == decision["player_id"])
            cost = sum(HOUSE_COST_BY_GROUP[board[SPACE_INDEX_BY_KEY[item["space_key"]]]["group"]] * item["count"] for item in action["args"]["build_plan"])
            criteria = [item for item in rubric if item["type"] == "keeps_cash_above"]
            build_cash.append({"scenario": path.stem, "before_cash": cash, "build_cost": cost, "accounting_after_cash": cash - cost, "scorer_after_cash": _cash_after_action(scenario, action), "liquidity_criteria": criteria})
    out["micro"] = {"baseline_checks": checks, "baseline_failures": failures, "scenarios_with_text_scoring": len(text_weights), "text_weight_range": [min(text_weights), max(text_weights)], "text_only_label_changes": label_changes, "build_cash_probes": build_cash}
    config = json.loads((root / "campaigns/monopoly-long-v1-smoke.json").read_text())
    changed = copy.deepcopy(config)
    changed["max_trade_exchanges"] = 1
    original_plan, changed_plan = build_campaign_plan(config), build_campaign_plan(changed)
    out["campaign"] = {
        "changed_trade_cap_same_run_ids": [row["run_id"] for row in original_plan["run_matrix"]] == [row["run_id"] for row in changed_plan["run_matrix"]],
        "changed_trade_cap_same_resume_keys": [row["resume_key"] for row in original_plan["run_matrix"]] == [row["resume_key"] for row in changed_plan["run_matrix"]],
    }
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        for name in ("events.jsonl", "actions.jsonl", "decisions.jsonl", "summary.json", "scorecard.json", "scorecard_players.json", "replay_report.json", "state_replay_report.json", "artifact_replay_report.json", "trace_summary.json", "failure_summary.json"):
            (directory / name).touch()
        out["campaign"]["empty_files_pass_completed_check"] = _completed_run_exists(directory)
    engine = Engine(seed=1, players=[{"player_id": "p1", "name": "Debtor"}, {"player_id": "p2", "name": "Creditor"}], run_id="review-probe")
    debtor, creditor = engine.state.players
    debtor.cash = 5
    for index in (1, 3):
        engine.state.board[index].owner_id = "p1"
        engine.state.board[index].houses = 1
    engine.state.bank.houses_remaining = 30
    engine.state.board[5].owner_id = "p1"
    engine.state.board[5].mortgaged = True
    before = creditor.cash
    events = []
    engine._handle_bankruptcy(debtor, creditor, events, turn_index=0)
    out["bankruptcy_internal_path"] = {"creditor_cash_delta": creditor.cash - before, "houses_retained": [engine.state.board[index].houses for index in (1, 3)], "bank_houses_after": engine.state.bank.houses_remaining, "mortgaged_railroad_owner": engine.state.board[5].owner_id, "event_types": [item["type"] for item in events]}
    players = {pid: {"player_id": pid, "primary_score": 0, "final_net_worth_estimate": 0, "winner": False, "final_liquid_net_worth_estimate": 0, "final_cash": 0, "bankruptcy_turn": turn} for pid, turn in [("p1", 1), ("p2", 100), ("p3", 50)]}
    metrics = {}
    _rank_players(players, metrics)
    out["equal_wealth_rank_probe"] = metrics["rankings"]
    manifest = json.loads((root / "paper/final_build_manifest.json").read_text())
    out["paper_hash_checks"] = []
    for item in (manifest["manuscript"]["source"], manifest["manuscript"]["pdf"], manifest["anonymous_supplement"]):
        path = root / item["path"]
        out["paper_hash_checks"].append({"path": item["path"], "exists": path.exists(), "hash_matches": path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"output": str(args.out), "replayed_games": len(replay), "baseline_checks": checks, "text_only_label_changes": len(label_changes), "paper_hash_checks": out["paper_hash_checks"]}, indent=2))


if __name__ == "__main__":
    main()
