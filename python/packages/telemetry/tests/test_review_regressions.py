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


@pytest.mark.parametrize("second_cost", [0.3, None])
def test_summary_total_cost_is_unknown_when_any_call_cost_is_missing(second_cost):
    from monopoly_telemetry.summary import _build_decision_stats
    usage = [{"cost": 0.2, "prompt_tokens": 5, "completion_tokens": 1},
             {"prompt_tokens": 5, "completion_tokens": 1} if second_cost is None else
             {"cost": second_cost, "prompt_tokens": 5, "completion_tokens": 1}]
    decisions = [{"phase": "decision_resolved", "attempts": [{"raw_response": {"usage": row}}]} for row in usage]
    _, token_usage = _build_decision_stats(decisions)
    assert token_usage is not None
    assert token_usage["known_cost_subtotal"] == 0.2 + (second_cost or 0)
    assert token_usage["total_cost"] == (None if second_cost is None else round(0.2 + second_cost, 6))


def test_manifest_ignores_hidden_interrupted_write_and_lock_files(tmp_path):
    from monopoly_telemetry.run_files import build_artifact_manifest
    files = init_run_files(tmp_path, "hidden")
    files.write_event({"seq": 1, "type": "EXPECTED"})
    (files.run_dir / ".writer.lock").write_text("")
    (files.snapshots_dir / ".write-interrupted").write_text("partial")
    listed = {entry["relative_path"] for entry in build_artifact_manifest(files)["artifacts"]}
    assert "events.jsonl" in listed
    assert not any(name.rsplit("/", 1)[-1].startswith(".") for name in listed)


def test_hidden_files_are_not_cost_or_commit_evidence(tmp_path):
    from monopoly_telemetry.usage import build_usage_report
    files = init_run_files(tmp_path, "hidden-evidence")
    (files.run_dir / "calls").mkdir()
    (files.run_dir / "calls" / ".extra.json").write_text(json.dumps({
        "call_id": "injected", "decision_id": "d", "attempt_index": 0, "status": "received",
        "request": {"model": "test"}, "result": {"response_json": {"usage": {"cost": 123}}}}))
    (files.run_dir / "commits").mkdir()
    (files.run_dir / "commits" / ".write-partial.json").write_text("{not json")
    assert build_usage_report(files)["attempt_count"] == 0
    repair_committed_tails(files)  # The interrupted temporary is ignored, not parsed as a commit.
    assert not files.events_path.exists()
