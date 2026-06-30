import asyncio
import json
from pathlib import Path
from typing import Any

from monopoly_arena import OpenRouterResult
from monopoly_arena.batch_artifacts import budget_preflight_estimate, should_stop_for_budget
from monopoly_arena.batch_run import run_batch
from monopoly_arena.paths import default_players_config_path


def _extract_payload(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    for message in messages:
        if message.get("role") != "user":
            continue
        try:
            payload = json.loads(message.get("content", "{}"))
        except json.JSONDecodeError:
            continue
        if "action_state" in payload and "game_state" in payload:
            action_state = payload.get("action_state", {})
            legal_actions = [
                {"action": tool.get("function", {}).get("name")}
                for tool in tools or []
                if tool.get("function", {}).get("name")
            ]
            normalized = dict(payload)
            normalized["decision"] = {
                "decision_type": action_state.get("decision_type"),
                "player_id": action_state.get("actor_player_id"),
                "legal_actions": legal_actions,
            }
            normalized["decision_focus"] = action_state
            normalized["full_state"] = payload.get("game_state")
            return normalized
        if "decision" in payload and "full_state" in payload:
            return payload
    return None


class DeterministicOpenRouter:
    async def create_chat_completion(self, *, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, **_: Any):
        payload = _extract_payload(messages, tools)
        decision = payload["decision"] if payload else {}
        legal = {entry.get("action") for entry in decision.get("legal_actions", [])}
        if "buy_property" in legal:
            action_name, args = "buy_property", {}
        elif "start_auction" in legal:
            action_name, args = "start_auction", {}
        elif "end_turn" in legal:
            action_name, args = "end_turn", {}
        elif "reject_trade" in legal:
            action_name, args = "reject_trade", {}
        else:
            action_name, args = next(iter(legal)), {}
        args = {
            **args,
            "public_message": "",
            "private_thought": "test",
        }
        payload = {
            "id": "resp-1",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "type": "function",
                                "function": {
                                    "name": action_name,
                                    "arguments": json.dumps(args),
                                },
                            }
                        ],
                    }
                }
            ],
        }
        return OpenRouterResult(
            ok=True,
            status_code=200,
            response_json=payload,
            error=None,
            error_type=None,
            request_id="req-1",
        )


class CountingOpenRouter(DeterministicOpenRouter):
    create_calls = 0

    async def create_chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ):
        type(self).create_calls += 1
        return await super().create_chat_completion(messages=messages, tools=tools, **kwargs)


class FailingOpenRouter:
    async def create_chat_completion(self, **_: Any):
        raise RuntimeError("scripted batch failure")


def test_batch_runner_writes_index_and_summaries(tmp_path: Path) -> None:
    config_path = tmp_path / "batch.json"
    config = {
        "batch_id": "batch-test",
        "seeds": [11, 12],
        "matches": 2,
        "players": str(default_players_config_path()),
        "seat_permutation": "latin_square",
        "batch_seed": 99,
        "max_turns": 8,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    index_path = asyncio.run(
        run_batch(
            json.loads(config_path.read_text(encoding="utf-8")),
            runs_dir=tmp_path,
            openrouter_factory=DeterministicOpenRouter,
        )
    )

    assert index_path.exists()
    batch_dir = tmp_path / "batches" / "batch-test"
    assert index_path == batch_dir / "run_index.jsonl"
    for artifact_name in [
        "batch_config.json",
        "batch_manifest.json",
        "model_config.json",
        "model_pricing_snapshot.json",
        "seed_manifest.json",
        "seat_manifest.json",
        "run_index.json",
        "results.jsonl",
        "leaderboard.json",
        "scorecard_summary.json",
        "statistical_summary.json",
        "replay_report.json",
        "trace_summary.json",
        "failure_summary.json",
        "cost_report.json",
        "token_report.json",
        "experiment_manifest.json",
        "review_cost_aggregate.json",
        "review_cost_calls.jsonl",
        "budget_report.json",
        "review_queue.jsonl",
        "artifact_manifest.json",
    ]:
        assert (batch_dir / artifact_name).exists()
    model_cards_dir = batch_dir / "model_cards"
    assert model_cards_dir.exists()

    lines = [line for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 2
    seat_manifest = json.loads((batch_dir / "seat_manifest.json").read_text(encoding="utf-8"))
    assert seat_manifest["permutation_mode"] == "latin_square"
    first_seats = seat_manifest["assignments"][0]["players"]
    second_seats = seat_manifest["assignments"][1]["players"]
    assert first_seats[0]["player_id"] != second_seats[0]["player_id"]
    assert first_seats[0]["player_id"] == second_seats[-1]["player_id"]

    pricing_snapshot = json.loads((batch_dir / "model_pricing_snapshot.json").read_text(encoding="utf-8"))
    assert pricing_snapshot["status"] == "unavailable"
    assert pricing_snapshot["reason"] == "client_has_no_get_models"
    experiment_manifest = json.loads((batch_dir / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert experiment_manifest["gateway"] == "openrouter"
    assert experiment_manifest["max_token_policy"]["max_tokens_set"] is False
    review_cost_aggregate = json.loads((batch_dir / "review_cost_aggregate.json").read_text(encoding="utf-8"))
    assert review_cost_aggregate["batch_id"] == "batch-test"
    assert "by_model" in review_cost_aggregate

    for line in lines:
        entry = json.loads(line)
        run_dir = Path(entry["run_dir"])
        summary_path = run_dir / "summary.json"
        assert summary_path.exists()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert "players" in summary
        assert "decision_stats" in summary
        assert "property_acquisition_timeline" in summary
        seat_assignment = json.loads((run_dir / "seat_assignment.json").read_text(encoding="utf-8"))
        assert seat_assignment["batch_id"] == "batch-test"
        assert seat_assignment["permutation_mode"] == "latin_square"
        assert (run_dir / "scorecard.json").exists()
        assert (run_dir / "usage.json").exists()
        assert (run_dir / "replay_report.json").exists()
        assert (run_dir / "state_replay_report.json").exists()
        assert (run_dir / "artifact_replay_report.json").exists()
        assert (run_dir / "trace_summary.json").exists()
        assert (run_dir / "failure_summary.json").exists()

    batch_replay_report = json.loads((batch_dir / "replay_report.json").read_text(encoding="utf-8"))
    assert "state_status_counts" in batch_replay_report
    assert "artifact_status_counts" in batch_replay_report

    leaderboard = json.loads((batch_dir / "leaderboard.json").read_text(encoding="utf-8"))
    assert leaderboard["ranking_modes"]["primary"] == "winner_then_average_final_net_worth"
    assert leaderboard["rankings"]
    model_card_paths = sorted(model_cards_dir.glob("*.json"))
    assert model_card_paths
    model_card = json.loads(model_card_paths[0].read_text(encoding="utf-8"))
    assert model_card["model_card_version"] == "model_card_v1"
    assert model_card["prompt_pipeline"]["status"] == "unchanged"
    markdown_card = model_card_paths[0].with_suffix(".md")
    assert markdown_card.exists()
    markdown_text = markdown_card.read_text(encoding="utf-8")
    assert "Private thoughts: linked via replay/review artifacts, not quoted here" in markdown_text
    assert '"private_thought":"test"' not in markdown_text


def test_batch_runner_continues_after_failures_when_configured(tmp_path: Path) -> None:
    config = {
        "batch_id": "batch-failure-test",
        "seeds": [21, 22],
        "matches": 2,
        "players": str(default_players_config_path()),
        "continue_on_failure": True,
        "max_turns": 8,
    }

    index_path = asyncio.run(
        run_batch(
            config,
            runs_dir=tmp_path,
            openrouter_factory=FailingOpenRouter,
        )
    )

    rows = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2
    assert {row["status"] for row in rows} == {"failed"}
    assert all("scripted batch failure" in row["error"] for row in rows)
    batch_dir = tmp_path / "batches" / "batch-failure-test"
    manifest = json.loads((batch_dir / "batch_manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_count"] == 2
    assert [run["status"] for run in manifest["runs"]] == ["failed", "failed"]
    results = [json.loads(line) for line in (batch_dir / "results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [row["status"] for row in results] == ["failed", "failed"]
    assert (batch_dir / "budget_report.json").exists()
    assert (batch_dir / "artifact_manifest.json").exists()


def test_batch_runner_resume_skips_existing_completed_runs(tmp_path: Path) -> None:
    config = {
        "batch_id": "batch-resume-test",
        "seeds": [31],
        "matches": 1,
        "players": str(default_players_config_path()),
        "resume": True,
        "max_turns": 8,
    }
    CountingOpenRouter.create_calls = 0
    asyncio.run(run_batch(config, runs_dir=tmp_path, openrouter_factory=CountingOpenRouter))
    first_call_count = CountingOpenRouter.create_calls
    assert first_call_count > 0

    index_path = asyncio.run(run_batch(config, runs_dir=tmp_path, openrouter_factory=CountingOpenRouter))

    assert CountingOpenRouter.create_calls == first_call_count
    rows = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1
    assert rows[0]["status"] == "completed"
    batch_config = json.loads((tmp_path / "batches" / "batch-resume-test" / "batch_config.json").read_text(encoding="utf-8"))
    assert batch_config["max_turns"] == 8


def test_batch_budget_preflight_uses_historical_actual_costs() -> None:
    config = {"cost_budget": 1.6, "budget_policy": "stop_immediately"}
    entries = [
        {"cost_report": {"total_actual_cost": 0.6}},
        {"cost_report": {"total_actual_cost": 0.5}},
    ]

    preflight = budget_preflight_estimate(config, entries)

    assert preflight["source"] == "historical_max_actual_run_cost"
    assert preflight["estimated_next_run_cost"] == 0.6
    assert preflight["remaining_budget"] == 0.5
    assert preflight["would_exceed_remaining_budget"] is True
    assert should_stop_for_budget(config, entries) == "remaining_budget_0.5_less_than_historical_max_run_cost_0.6"
