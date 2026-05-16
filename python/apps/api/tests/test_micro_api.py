from __future__ import annotations

import json

from fastapi.testclient import TestClient

from monopoly_api import main as api_main
from monopoly_api import micro as api_micro
from monopoly_api.settings import Settings
from monopoly_arena import OpenRouterResult


class ScriptedOpenRouter:
    queued_results: list[OpenRouterResult] = []

    def __init__(self, *_: object, **__: object) -> None:
        self.calls: list[dict[str, object]] = []

    async def create_chat_completion(self, **kwargs: object) -> OpenRouterResult:
        self.calls.append(kwargs)
        if not self.queued_results:
            raise AssertionError("No scripted OpenRouter results queued.")
        return self.queued_results.pop(0)

    async def aclose(self) -> None:
        return None


class StreamingOpenRouter:
    def __init__(self, *_: object, stream_callback: object | None = None, **__: object) -> None:
        self._stream_callback = stream_callback

    async def create_chat_completion(self, **_: object) -> OpenRouterResult:
        if callable(self._stream_callback):
            await self._stream_callback({"type": "reasoning_delta", "text": "reason"})
            await self._stream_callback({"type": "tool_arguments_delta", "text": '{"action":"buy_property"}'})
        return _tool_call_result("buy_property", {"private_thought": "reason"})

    async def aclose(self) -> None:
        return None


def _tool_call_result(name: str, args: dict[str, object]) -> OpenRouterResult:
    payload_args = {
        **args,
        "public_message": args.get("public_message", ""),
        "private_thought": args.get("private_thought", "test"),
    }
    response_json = {
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
                                "name": name,
                                "arguments": json.dumps(payload_args, separators=(",", ":"), ensure_ascii=True),
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
        response_json=response_json,
        error=None,
        error_type=None,
        request_id="req-1",
        request_payload_raw=None,
        response_text=json.dumps(response_json, separators=(",", ":"), ensure_ascii=True),
    )


def test_micro_scenarios_endpoints() -> None:
    client = TestClient(api_main.app)

    response = client.get("/micro/scenarios")
    assert response.status_code == 200
    payload = response.json()
    scenario_ids = {item["scenario_id"] for item in payload["scenarios"]}
    assert "buy-or-auction-vermont-light-blue-tempo-01" in scenario_ids
    assert "jail-cash-poor-danger-roll-15" in scenario_ids

    detail = client.get("/micro/scenarios/trade-propose-water-works-for-new-york-01")
    assert detail.status_code == 200
    scenario = detail.json()
    assert scenario["category"] == "TRADE_PROPOSE"
    assert scenario["decision_point"]["decision_type"] == "TRADE_PROPOSE_DECISION"


def test_micro_run_endpoint_writes_isolated_artifacts(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        api_main,
        "settings",
        Settings(
            runs_dir=tmp_path / "runs",
            api_host="127.0.0.1",
            api_port=8000,
            players_config_path=tmp_path / "players.json",
        ),
    )
    monkeypatch.setattr(api_main, "OpenRouterClient", StreamingOpenRouter)
    client = TestClient(api_main.app)
    run_response = client.post(
        "/micro/run",
        json={
            "scenario_id": "buy-or-auction-vermont-light-blue-tempo-01",
            "openrouter_model_id": "openai/gpt-oss-120b",
            "name": "Alpha",
            "reasoning": {"effort": "medium"},
            "prompt_condition": "live_game",
        },
    )
    assert run_response.status_code == 200
    run_id = run_response.json()["run_id"]

    detail_response = client.get(f"/micro/runs/{run_id}")
    assert detail_response.status_code == 200
    payload = detail_response.json()

    assert payload["summary"]["mode"] == "micro"
    assert payload["summary"]["scenario_id"] == "buy-or-auction-vermont-light-blue-tempo-01"
    assert payload["summary"]["prompt_condition"] == "live_game"
    assert payload["decision_bundle"]["final_action"]["action"] == "buy_property"
    assert payload["result"]["score"]["label"] in {"preferred", "acceptable", "bad", "invalid"}
    assert payload["artifact_paths"]["result"].endswith("result.json")
    assert (tmp_path / "runs" / "micro" / run_id / "scenario.json").exists()
    assert not (tmp_path / "runs" / run_id).exists()
    assert (tmp_path / "quality_check" / "micro" / run_id).exists()


def test_micro_suites_and_model_batch(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        api_main,
        "settings",
        Settings(
            runs_dir=tmp_path / "runs",
            api_host="127.0.0.1",
            api_port=8000,
            players_config_path=tmp_path / "players.json",
        ),
    )
    monkeypatch.setattr(api_main, "OpenRouterClient", StreamingOpenRouter)
    client = TestClient(api_main.app)
    suites = client.get("/micro/suites")
    assert suites.status_code == 200
    assert suites.json()["suites"][0]["suite_id"] == "micro-v1"

    batch = client.post(
        "/micro/batches",
        json={
            "suite_id": "micro-v1",
            "openrouter_model_ids": ["openai/gpt-oss-120b"],
            "prompt_condition": "live_game",
            "scenario_ids": [
                "buy-or-auction-vermont-light-blue-tempo-01",
            ],
        },
    )
    assert batch.status_code == 200
    batch_id = batch.json()["batch_id"]
    leaderboard = client.get(f"/micro/batches/{batch_id}/leaderboard")
    assert leaderboard.status_code == 200
    assert leaderboard.json()["rows"]


def test_micro_stream_endpoint_emits_llm_deltas_and_result(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        api_main,
        "settings",
        Settings(
            runs_dir=tmp_path / "runs",
            api_host="127.0.0.1",
            api_port=8000,
            players_config_path=tmp_path / "players.json",
        ),
    )
    monkeypatch.setattr(api_micro, "OpenRouterClient", StreamingOpenRouter)
    client = TestClient(api_main.app)
    with client.stream(
        "POST",
        "/micro/run/stream",
        json={
            "scenario_id": "buy-or-auction-vermont-light-blue-tempo-01",
            "openrouter_model_id": "openai/gpt-oss-120b",
            "name": "Alpha",
        },
    ) as response:
        assert response.status_code == 200
        text = "".join(response.iter_text())
    assert "event: status" in text
    assert "reasoning_delta" in text
    assert "tool_arguments_delta" in text
    assert "event: result" in text


def test_micro_batch_stream_runs_in_limited_waves(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        api_main,
        "settings",
        Settings(
            runs_dir=tmp_path / "runs",
            api_host="127.0.0.1",
            api_port=8000,
            players_config_path=tmp_path / "players.json",
        ),
    )
    monkeypatch.setattr(api_micro, "MICRO_BATCH_PARALLEL_LIMIT", 1)
    client = TestClient(api_main.app)
    with client.stream(
        "POST",
        "/micro/batches/stream",
        json={
            "suite_id": "micro-v1",
            "openrouter_model_ids": ["openai/gpt-oss-120b"],
            "prompt_condition": "live_game",
            "scenario_ids": [
                "buy-or-auction-vermont-light-blue-tempo-01",
            ],
        },
    ) as response:
        assert response.status_code == 200
        text = "".join(response.iter_text())
    assert '"parallel_limit":1' in text
    assert '"wave_scenario_ids":["buy-or-auction-vermont-light-blue-tempo-01"]' in text
    assert text.count('"state":"wave_started"') == 1
    assert text.count("event: scenario_result") == 1
    assert "event: batch_result" in text


def test_micro_batch_stream_emits_per_scenario_llm_deltas(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        api_main,
        "settings",
        Settings(
            runs_dir=tmp_path / "runs",
            api_host="127.0.0.1",
            api_port=8000,
            players_config_path=tmp_path / "players.json",
        ),
    )
    monkeypatch.setattr(api_micro, "OpenRouterClient", StreamingOpenRouter)
    client = TestClient(api_main.app)
    with client.stream(
        "POST",
        "/micro/batches/stream",
        json={
            "suite_id": "micro-v1",
            "openrouter_model_ids": ["openai/gpt-oss-120b"],
            "prompt_condition": "live_game",
            "scenario_ids": ["buy-or-auction-vermont-light-blue-tempo-01"],
        },
    ) as response:
        assert response.status_code == 200
        text = "".join(response.iter_text())
    assert "event: scenario_started" in text
    assert "event: llm_delta" in text
    assert '"scenario_id":"buy-or-auction-vermont-light-blue-tempo-01"' in text
    assert "reasoning_delta" in text
    assert text.index("event: llm_delta") < text.index("event: scenario_result")


def test_micro_run_returns_not_found_for_unknown_scenario() -> None:
    client = TestClient(api_main.app)
    response = client.post(
        "/micro/run",
        json={
            "scenario_id": "does-not-exist",
            "openrouter_model_id": "openai/gpt-oss-120b",
        },
    )
    assert response.status_code == 404
