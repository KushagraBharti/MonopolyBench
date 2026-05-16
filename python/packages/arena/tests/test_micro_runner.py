from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from monopoly_arena import OpenRouterResult, build_single_player_config
from monopoly_arena.decision_resolver import SharedDecisionResolver
from monopoly_arena.micro_runner import MicroRunner
from monopoly_arena.micro_scenarios import list_micro_scenarios, load_micro_scenario, validate_micro_scenario
from monopoly_arena.prompting import PromptMemory, build_space_key_by_index
from monopoly_telemetry import build_run_files


class ScriptedOpenRouter:
    def __init__(self, results: list[OpenRouterResult]) -> None:
        self._results = list(results)
        self.calls: list[dict[str, Any]] = []

    async def create_chat_completion(self, **kwargs: Any) -> OpenRouterResult:
        self.calls.append(kwargs)
        if not self._results:
            raise AssertionError("No scripted OpenRouter results remaining.")
        return self._results.pop(0)

    async def aclose(self) -> None:
        return None


def _tool_call_result(name: str, args: dict[str, Any], *, request_id: str = "req-1") -> OpenRouterResult:
    payload_args = {
        **args,
        "public_message": args.get("public_message", ""),
        "private_thought": args.get("private_thought", "test"),
    }
    response_json = {
        "id": request_id,
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
    response_text = json.dumps(response_json, separators=(",", ":"), ensure_ascii=True)
    return OpenRouterResult(
        ok=True,
        status_code=200,
        response_json=response_json,
        error=None,
        error_type=None,
        request_id=request_id,
        request_payload_raw=None,
        response_text=response_text,
    )


def _run_files(tmp_path: Path, run_id: str):
    return build_run_files(
        tmp_path / "runs" / "micro",
        run_id,
        quality_base_dir=tmp_path / "quality_check" / "micro",
    )


def _player_config() -> Any:
    return build_single_player_config(
        player_id="p1",
        name="Alpha",
        openrouter_model_id="openai/gpt-oss-120b",
    )


def _resolver(tmp_path: Path, run_id: str, results: list[OpenRouterResult]) -> tuple[SharedDecisionResolver, Any]:
    run_files = _run_files(tmp_path, run_id)
    space_key_by_index = build_space_key_by_index()
    router = ScriptedOpenRouter(results)
    resolver = SharedDecisionResolver(
        openrouter=router,
        run_files=run_files,
        prompt_memory=PromptMemory(space_key_by_index=space_key_by_index),
        space_key_by_index=space_key_by_index,
    )
    return resolver, router


def test_micro_scenario_seed_corpus_and_validation() -> None:
    scenario_ids = {scenario["scenario_id"] for scenario in list_micro_scenarios()}
    assert len(scenario_ids) == 130
    assert "auction-illinois-min-raise-red-completion-01" in scenario_ids
    assert "buy-or-auction-vermont-light-blue-tempo-01" in scenario_ids
    assert "trade-propose-water-works-for-new-york-01" in scenario_ids

    invalid = load_micro_scenario("buy-or-auction-vermont-light-blue-tempo-01")
    invalid["focal_player_id"] = "p2"
    try:
        validate_micro_scenario(invalid)
    except ValueError as exc:
        assert "focal_player_id" in str(exc)
    else:
        raise AssertionError("Expected invalid micro scenario to raise ValueError.")


def test_shared_decision_resolver_accepts_valid_tool_call_and_writes_artifacts(tmp_path) -> None:
    scenario = load_micro_scenario("buy-or-auction-vermont-light-blue-tempo-01")
    decision = scenario["decision_point"]
    resolver, router = _resolver(tmp_path, "micro-valid", [_tool_call_result("buy_property", {})])
    decision_logs: list[dict[str, Any]] = []

    async def log_writer(entry: dict[str, Any]) -> None:
        decision_logs.append(entry)

    outcome = asyncio.run(
        resolver.resolve_decision(
            decision=decision,
            player_config=_player_config(),
            log_writer=log_writer,
        )
    )

    run_files = _run_files(tmp_path, "micro-valid")
    prompt_prefix = run_files.prompts_dir / f"decision_{decision['decision_id']}"

    assert outcome.action["action"] == "buy_property"
    assert outcome.retry_used is False
    assert outcome.fallback_used is False
    assert len(router.calls) == 1
    assert len(decision_logs) == 1
    assert decision_logs[0]["phase"] == "decision_started"
    assert (prompt_prefix.with_name(f"{prompt_prefix.name}_user.json")).exists()
    assert (prompt_prefix.with_name(f"{prompt_prefix.name}_parsed.json")).exists()
    assert (run_files.quality_dir / f"decision_{decision['decision_id']}_request.txt").exists()


def test_shared_decision_resolver_retries_after_invalid_tool_call(tmp_path) -> None:
    scenario = load_micro_scenario("buy-or-auction-vermont-light-blue-tempo-01")
    decision = scenario["decision_point"]
    resolver, router = _resolver(
        tmp_path,
        "micro-retry",
        [
            _tool_call_result("buy_property_invalid", {}),
            _tool_call_result("buy_property", {}),
        ],
    )

    outcome = asyncio.run(
        resolver.resolve_decision(
            decision=decision,
            player_config=_player_config(),
            log_writer=None,
        )
    )

    run_files = _run_files(tmp_path, "micro-retry")
    retry_prefix = run_files.prompts_dir / f"decision_{decision['decision_id']}_retry1"

    assert outcome.action["action"] == "buy_property"
    assert outcome.retry_used is True
    assert outcome.fallback_used is False
    assert len(router.calls) == 2
    assert (retry_prefix.with_name(f"{retry_prefix.name}_parsed.json")).exists()


def test_shared_decision_resolver_uses_deterministic_fallback_after_second_failure(tmp_path) -> None:
    scenario = load_micro_scenario("auction-illinois-min-raise-red-completion-01")
    decision = scenario["decision_point"]
    resolver, router = _resolver(
        tmp_path,
        "micro-fallback",
        [
            _tool_call_result("illegal_bid", {}),
            _tool_call_result("still_illegal", {}),
        ],
    )

    outcome = asyncio.run(
        resolver.resolve_decision(
            decision=decision,
            player_config=_player_config(),
            log_writer=None,
        )
    )

    assert outcome.retry_used is True
    assert outcome.fallback_used is True
    assert outcome.fallback_reason == "malformed_after_retry"
    assert outcome.action["action"] == "bid_auction"
    current_bid = decision["state"]["auction"]["current_high_bid"]
    assert outcome.action["args"] == {"bid_amount": current_bid + 1}
    assert outcome.action["private_thought"] == "fallback"
    assert len(router.calls) == 2


def test_micro_runner_writes_isolated_artifacts(tmp_path) -> None:
    scenario = load_micro_scenario("buy-or-auction-vermont-light-blue-tempo-01")
    run_files = _run_files(tmp_path, "micro-runner")
    runner = MicroRunner(
        scenario=scenario,
        player_config=_player_config(),
        run_id="micro-runner",
        openrouter=ScriptedOpenRouter([_tool_call_result("buy_property", {})]),
        run_files=run_files,
    )

    result = asyncio.run(runner.run())
    summary = json.loads(run_files.summary_path.read_text(encoding="utf-8"))
    decisions_lines = run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
    actions_lines = run_files.actions_path.read_text(encoding="utf-8").strip().splitlines()

    assert result["summary"]["mode"] == "micro"
    assert summary["scenario_id"] == "buy-or-auction-vermont-light-blue-tempo-01"
    assert (run_files.run_dir / "scenario.json").exists()
    assert (run_files.snapshots_dir / f"turn_{scenario['decision_point']['turn_index']:04d}.json").exists()
    assert len(decisions_lines) == 2
    assert len(actions_lines) == 1
    assert run_files.run_dir.parts[-2:] == ("micro", "micro-runner")
    assert run_files.quality_dir is not None
    assert run_files.quality_dir.parts[-2:] == ("micro", "micro-runner")
