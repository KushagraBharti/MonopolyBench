import json

import pytest

from monopoly_telemetry import init_run_files
from monopoly_telemetry.commit import repair_committed_tails, write_commit
from monopoly_telemetry.scorecard import _rank_players
from monopoly_telemetry.usage import _decision_usage_rows, _aggregate_usage, _cost_report


def test_net_worth_ranks_tie_independently_of_winner_and_cash():
    rows = {
        "a": {"player_id": "a", "final_net_worth_estimate": 1500, "winner": True, "final_cash": 1000, "primary_score": 1500},
        "b": {"player_id": "b", "final_net_worth_estimate": 1500, "winner": False, "final_cash": 700, "primary_score": 1500},
        "c": {"player_id": "c", "final_net_worth_estimate": 1000, "winner": False, "final_cash": 1000, "primary_score": 1000},
    }
    _rank_players(rows, {})
    assert [rows[key]["final_rank"] for key in rows] == [1, 1, 3]


def test_conflicting_later_commit_leaves_all_journals_unchanged(tmp_path):
    files = init_run_files(tmp_path, "conflict")
    for index in (1, 2):
        write_commit(files, {"decision_id": f"d{index}"},
                     {"decision_id": f"d{index}", "phase": "decision_resolved"},
                     [{"seq": index, "type": "EXPECTED"}])
    files.write_event({"seq": 1, "type": "EXPECTED"})
    files.write_event({"seq": 2, "type": "CORRUPTED"})
    paths = [files.actions_path, files.decisions_path, files.events_path]
    before = {path: path.read_bytes() if path.exists() else None for path in paths}
    with pytest.raises(ValueError, match="Conflicting"):
        repair_committed_tails(files)
    assert {path: path.read_bytes() if path.exists() else None for path in paths} == before


@pytest.mark.parametrize("journal", ["actions", "decisions"])
def test_missing_interior_commit_record_is_not_appended_out_of_order(tmp_path, journal):
    files = init_run_files(tmp_path, "interior")
    for index in (1, 2):
        action = {"decision_id": f"d{index}"}
        decision = {"decision_id": f"d{index}", "phase": "decision_resolved"}
        events = [{"seq": index, "type": "EXPECTED"}]
        write_commit(files, action, decision, events)
        files.write_action(action)
        files.write_decision(decision)
        files.write_event(events[0])
    path = getattr(files, f"{journal}_path")
    remaining = json.loads(path.read_text().splitlines()[1])
    path.write_text(json.dumps(remaining) + "\n")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="append tail"):
        repair_committed_tails(files)
    assert path.read_bytes() == before


@pytest.mark.parametrize("costs", [[2.0, None], [None, 2.0], [0.0, 2.0]])
@pytest.mark.parametrize("same_decision", [False, True])
def test_unknown_cost_propagates_through_decision_player_model_and_run(costs, same_decision):
    attempts = [{"decision_id": "d" if same_decision else f"d{i}", "player_id": "p", "openrouter_model_id": "m",
                 "cost": cost, "accounting_status": "actual_openrouter_usage"} for i, cost in enumerate(costs)]
    decisions = _decision_usage_rows(attempts)
    report = _aggregate_usage("cost", attempts, decisions)
    expected = None if None in costs else sum(costs)
    assert report["totals"]["cost"] == expected
    assert report["by_player"]["p"]["cost"] == expected
    assert report["by_model"]["m"]["cost"] == expected
    assert report["known_cost_subtotal"] == sum(cost for cost in costs if cost is not None)
    cost_report = _cost_report(report)
    assert cost_report["total_actual_cost"] == expected
    assert cost_report["known_cost_subtotal"] == report["known_cost_subtotal"]
    assert cost_report["missing_cost_attempt_count"] == costs.count(None)
    if same_decision:
        assert decisions[0]["cost"] == expected


@pytest.mark.parametrize("journal", ["actions", "decisions"])
def test_unknown_record_rejects_repair_before_any_bytes_change(tmp_path, journal):
    files = init_run_files(tmp_path, "unknown")
    for index in (1, 2):
        write_commit(files, {"decision_id": f"d{index}"},
                     {"decision_id": f"d{index}", "phase": "decision_resolved"},
                     [{"seq": index, "type": "EXPECTED"}])
    files.write_action({"decision_id": "d1"})
    files.write_decision({"decision_id": "d1", "phase": "decision_resolved"})
    files.write_event({"seq": 1, "type": "EXPECTED"})
    if journal == "actions":
        files.write_action({"decision_id": "unknown"})
    else:
        files.write_decision({"decision_id": "unknown", "phase": "decision_resolved"})
    paths = [files.actions_path, files.decisions_path, files.events_path]
    before = {path: path.read_bytes() for path in paths}
    with pytest.raises(ValueError, match="Unknown"):
        repair_committed_tails(files)
    assert {path: path.read_bytes() for path in paths} == before
