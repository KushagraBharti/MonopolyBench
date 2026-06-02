import json

from monopoly_telemetry import (
    init_run_files,
    write_scorecard_artifacts,
    write_trace_failure_artifacts,
    write_usage_artifacts,
)


def test_write_snapshot_does_not_overwrite_turn_file(tmp_path) -> None:
    run_files = init_run_files(tmp_path, "run-snapshots")

    start_turn = {"schema_version": "v1", "run_id": "run-snapshots", "turn_index": 1, "phase": "START_TURN"}
    decision = {"schema_version": "v1", "run_id": "run-snapshots", "turn_index": 1, "phase": "AWAITING_DECISION"}

    canonical_path = run_files.write_snapshot(start_turn)
    assert canonical_path.name == "turn_0001.json"
    assert json.loads(canonical_path.read_text(encoding="utf-8"))["phase"] == "START_TURN"

    variant_path = run_files.write_snapshot(decision)
    assert variant_path.name.startswith("turn_0001_decision_")
    assert variant_path.name.endswith(".json")
    assert json.loads(canonical_path.read_text(encoding="utf-8"))["phase"] == "START_TURN"
    assert json.loads(variant_path.read_text(encoding="utf-8"))["phase"] == "AWAITING_DECISION"


def test_run_files_exposes_research_artifact_paths_and_manifest(tmp_path) -> None:
    run_files = init_run_files(tmp_path, "run-artifacts")

    run_files.write_run_config({"schema_version": "v1", "run_id": "run-artifacts"})
    run_files.write_players({"schema_version": "v1", "players": []})
    run_files.write_seat_assignment({"schema_version": "v1", "assignments": []})
    run_files.write_summary({"schema_version": "v1", "run_id": "run-artifacts"})
    run_files.write_artifact_manifest()

    manifest = json.loads(run_files.artifact_manifest_path.read_text(encoding="utf-8"))
    by_label = {entry["label"]: entry for entry in manifest["artifacts"]}

    assert manifest["schema_version"] == "v1"
    assert manifest["run_id"] == "run-artifacts"
    assert by_label["run_config"]["exists"] is True
    assert by_label["players"]["exists"] is True
    assert by_label["seat_assignment"]["exists"] is True
    assert by_label["summary"]["exists"] is True
    assert by_label["scorecard"]["exists"] is False
    assert by_label["run_config"]["relative_path"] == "run_config.json"
    assert len(by_label["run_config"]["sha256"]) == 64


def test_write_scorecard_artifacts_from_logs(tmp_path) -> None:
    run_files = init_run_files(tmp_path, "run-scorecard")
    run_files.write_players(
        {
            "schema_version": "v1",
            "players": [
                {
                    "player_id": "p1",
                    "name": "Alpha",
                    "openrouter_model_id": "model/a",
                    "model_display_name": "a",
                },
                {
                    "player_id": "p2",
                    "name": "Beta",
                    "openrouter_model_id": "model/b",
                    "model_display_name": "b",
                },
            ],
        }
    )
    run_files.write_seat_assignment(
        {
            "schema_version": "v1",
            "assignments": [
                {"player_id": "p1", "seat_index": 0, "turn_order": 0},
                {"player_id": "p2", "seat_index": 1, "turn_order": 1},
            ],
        }
    )
    run_files.write_event(
        {
            "schema_version": "v1",
            "run_id": "run-scorecard",
            "event_id": "evt-1",
            "seq": 1,
            "turn_index": 0,
            "ts_ms": 0,
            "actor": {"kind": "ENGINE", "player_id": None},
            "type": "PROPERTY_PURCHASED",
            "payload": {"player_id": "p1", "space_index": 1, "price": 60},
        }
    )
    run_files.write_event(
        {
            "schema_version": "v1",
            "run_id": "run-scorecard",
            "event_id": "evt-2",
            "seq": 2,
            "turn_index": 1,
            "ts_ms": 1,
            "actor": {"kind": "ENGINE", "player_id": None},
            "type": "RENT_PAID",
            "payload": {"from_player_id": "p2", "to_player_id": "p1", "amount": 12, "space_index": 1},
        }
    )
    run_files.write_event(
        {
            "schema_version": "v1",
            "run_id": "run-scorecard",
            "event_id": "evt-3",
            "seq": 3,
            "turn_index": 1,
            "ts_ms": 2,
            "actor": {"kind": "ENGINE", "player_id": None},
            "type": "HOUSE_BUILT",
            "payload": {"player_id": "p1", "space_index": 1, "count": 1},
        }
    )
    run_files.write_decision(
        {
            "phase": "decision_resolved",
            "run_id": "run-scorecard",
            "turn_index": 0,
            "decision_id": "dec-1",
            "decision_type": "BUY_OR_AUCTION_DECISION",
            "player_id": "p1",
            "openrouter_model_id": "model/a",
            "model_display_name": "a",
            "retry_used": True,
            "fallback_used": False,
            "fallback_reason": None,
            "final_action": {"action": "buy_property"},
            "attempts": [{"validation_errors": ["bad"]}, {"validation_errors": []}],
            "latency_ms": 123,
        }
    )
    run_files.write_action(
        {
            "decision_id": "dec-1",
            "actor_player_id": "p1",
            "decision_type": "BUY_OR_AUCTION_DECISION",
            "turn_index": 0,
            "action": {"action": "buy_property"},
        }
    )
    run_files.write_summary(
        {
            "run_id": "run-scorecard",
            "winner_player_id": "p1",
            "turn_count": 2,
            "reason": "BANKRUPTCY",
            "players": {
                "p1": {"name": "Alpha", "cash": 1520, "net_worth_estimate": 1580, "bankrupt": False, "turns_played": 2},
                "p2": {"name": "Beta", "cash": 1488, "net_worth_estimate": 1488, "bankrupt": True, "turns_played": 2},
            },
        }
    )

    scorecard = write_scorecard_artifacts(run_files)
    players = {entry["player_id"]: entry for entry in scorecard["players"]}

    assert run_files.scorecard_path.exists()
    assert run_files.scorecard_players_path.exists()
    assert run_files.scorecard_decisions_path.exists()
    assert run_files.scorecard_events_path.exists()
    assert scorecard["run"]["total_rent_paid"] == 12
    assert scorecard["run"]["total_houses_built"] == 1
    assert scorecard["run"]["decision_stats"]["invalid_attempts"] == 1
    assert players["p1"]["winner"] is True
    assert players["p1"]["primary_score"] == 1580
    assert players["p1"]["rent_collected"] == 12
    assert players["p2"]["rent_paid"] == 12
    assert players["p1"]["retries_used"] == 1


def test_write_usage_artifacts_from_openrouter_actuals(tmp_path) -> None:
    run_files = init_run_files(tmp_path, "run-usage")
    run_files.write_decision(
        {
            "phase": "decision_resolved",
            "run_id": "run-usage",
            "turn_index": 0,
            "decision_id": "dec-usage",
            "decision_type": "BUY_OR_AUCTION_DECISION",
            "player_id": "p1",
            "openrouter_model_id": "model/a",
            "model_display_name": "a",
            "retry_used": True,
            "fallback_used": False,
            "fallback_reason": None,
            "attempts": [
                {
                    "raw_response": {
                        "id": "gen-1",
                        "choices": [{"finish_reason": "tool_calls"}],
                        "usage": {
                            "prompt_tokens": 10,
                            "completion_tokens": 5,
                            "total_tokens": 15,
                            "native_tokens": {
                                "prompt_tokens": 11,
                                "completion_tokens": 6,
                                "total_tokens": 17,
                            },
                            "completion_tokens_details": {"reasoning_tokens": 2},
                            "prompt_tokens_details": {"cached_tokens": 3},
                            "cost": 0.0123,
                        },
                    },
                    "openrouter_request_id": "req-1",
                    "openrouter_status_code": 200,
                    "latency_ms": 100,
                },
                {
                    "raw_response": {"id": "gen-2", "choices": [{"finish_reason": "tool_calls"}]},
                    "openrouter_request_id": "req-2",
                    "openrouter_status_code": 200,
                    "latency_ms": 200,
                },
            ],
        }
    )

    usage = write_usage_artifacts(run_files)
    attempts = [
        json.loads(line)
        for line in run_files.usage_attempts_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    decisions = [
        json.loads(line)
        for line in run_files.usage_decisions_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    cost_report = json.loads(run_files.cost_report_path.read_text(encoding="utf-8"))

    assert usage["source"] == "openrouter_actuals_only"
    assert usage["local_tokenizer_estimates_used"] is False
    assert usage["missing_usage_attempt_count"] == 1
    assert usage["totals"]["prompt_tokens"] == 10
    assert usage["totals"]["native_total_tokens"] == 17
    assert usage["totals"]["reasoning_tokens"] == 2
    assert usage["totals"]["cached_tokens"] == 3
    assert usage["totals"]["cost"] == 0.0123
    assert attempts[0]["accounting_status"] == "actual_openrouter_usage"
    assert attempts[1]["accounting_status"] == "missing_openrouter_usage"
    assert decisions[0]["accounting_status"] == "partial_openrouter_usage"
    assert cost_report["total_actual_cost"] == 0.0123
    assert cost_report["total_estimated_cost"] is None


def test_write_trace_failure_artifacts_from_logs(tmp_path) -> None:
    run_files = init_run_files(tmp_path, "run-analysis")
    run_files.write_event(
        {
            "schema_version": "v1",
            "run_id": "run-analysis",
            "event_id": "evt-rent",
            "seq": 1,
            "turn_index": 3,
            "ts_ms": 0,
            "actor": {"kind": "ENGINE", "player_id": None},
            "type": "RENT_PAID",
            "payload": {"from_player_id": "p2", "to_player_id": "p1", "amount": 150, "space_index": 19},
        }
    )
    run_files.write_decision(
        {
            "phase": "decision_resolved",
            "run_id": "run-analysis",
            "turn_index": 4,
            "decision_id": "dec-fallback",
            "decision_type": "BUY_OR_AUCTION_DECISION",
            "player_id": "p2",
            "openrouter_model_id": "model/b",
            "fallback_used": True,
            "fallback_reason": "malformed_after_retry",
            "retry_used": True,
            "attempts": [{"validation_errors": ["No tool call found"]}],
            "emitted_event_ids": ["evt-x"],
            "emitted_event_seq_start": 2,
            "emitted_event_seq_end": 2,
        }
    )

    result = write_trace_failure_artifacts(run_files)
    trace_findings = [
        json.loads(line)
        for line in run_files.trace_findings_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    failure_findings = [
        json.loads(line)
        for line in run_files.failure_findings_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    failure_summary = json.loads(run_files.failure_summary_path.read_text(encoding="utf-8"))
    review_queue = [
        json.loads(line)
        for line in run_files.review_queue_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert result["trace_summary"]["total_findings"] >= 2
    assert any(finding["finding_type"] == "large_rent_payment" for finding in trace_findings)
    assert any(finding["finding_type"] == "fallback_used" for finding in failure_findings)
    assert any(finding["finding_type"] == "missing_tool_call" for finding in failure_findings)
    assert failure_summary["by_type"]["fallback_used"] >= 1
    assert review_queue
    assert any(item["reason_for_review"] == "fallback_used" for item in review_queue)
    assert run_files.timeline_path.exists()
    assert run_files.decision_index_path.exists()
    assert run_files.cash_flow_path.exists()

