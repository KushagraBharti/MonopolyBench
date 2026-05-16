from __future__ import annotations

import json

from monopoly_arena.llm_runner import DecisionAttempt, LlmRunner
from monopoly_arena.player_config import PlayerConfig
from monopoly_arena.prompting import build_trade_propose_decision_focus


class _DummyOpenRouter:
    async def aclose(self) -> None:
        return None


def _players() -> list[PlayerConfig]:
    return [
        PlayerConfig(
            player_id=f"P{i}",
            name=f"Player {i}",
            openrouter_model_id="openai/gpt-oss-120b",
            model_display_name="gpt-oss-120b",
            system_prompt="test",
            reasoning=None,
        )
        for i in range(1, 5)
    ]


def _runner() -> LlmRunner:
    return LlmRunner(
        seed=123,
        players=_players(),
        run_id="run_test",
        openrouter=_DummyOpenRouter(),
    )


def test_post_turn_single_action_without_end_turn_is_valid() -> None:
    runner = _runner()
    decision = {
        "decision_id": "decision_post_turn",
        "decision_type": "POST_TURN_ACTION_DECISION",
        "legal_actions": [
            {"action": "mortgage_property"},
            {"action": "end_turn"},
        ],
    }
    attempt = DecisionAttempt(
        prompt_messages=[],
        prompt_payload=None,
        prompt_payload_raw=None,
        raw_response=None,
        assistant_content=None,
        parsed_tool_call=None,
        parsed_tool_calls=[
            {
                "name": "mortgage_property",
                "arguments": json.dumps(
                    {
                        "space_key": "READING_RAILROAD",
                        "public_message": "",
                        "private_thought": "test",
                    }
                ),
            }
        ],
        validation_errors=[],
        openrouter_request_id=None,
        openrouter_status_code=None,
        error_type=None,
        error_message=None,
        request_start_ms=None,
        response_end_ms=None,
        latency_ms=None,
    )

    action, errors, error_reason, sequence_meta = runner._build_action_from_attempt(  # noqa: SLF001
        decision,
        attempt,
    )

    assert errors == []
    assert error_reason is None
    assert action is not None
    assert action["action"] == "mortgage_property"
    assert sequence_meta == {"parsed_tool_calls_count": 1}


def test_post_turn_multi_call_is_rejected() -> None:
    runner = _runner()
    decision = {
        "decision_id": "decision_post_turn",
        "decision_type": "POST_TURN_ACTION_DECISION",
        "legal_actions": [
            {"action": "mortgage_property"},
            {"action": "unmortgage_property"},
            {"action": "end_turn"},
        ],
    }
    attempt = DecisionAttempt(
        prompt_messages=[],
        prompt_payload=None,
        prompt_payload_raw=None,
        raw_response=None,
        assistant_content=None,
        parsed_tool_call=None,
        parsed_tool_calls=[
            {
                "name": "mortgage_property",
                "arguments": json.dumps(
                    {
                        "space_key": "READING_RAILROAD",
                        "public_message": "",
                        "private_thought": "test",
                    }
                ),
            },
            {
                "name": "unmortgage_property",
                "arguments": json.dumps(
                    {
                        "space_key": "PENNSYLVANIA_RAILROAD",
                        "public_message": "",
                        "private_thought": "test",
                    }
                ),
            },
        ],
        validation_errors=[],
        openrouter_request_id=None,
        openrouter_status_code=None,
        error_type=None,
        error_message=None,
        request_start_ms=None,
        response_end_ms=None,
        latency_ms=None,
    )

    action, errors, error_reason, sequence_meta = runner._build_action_from_attempt(  # noqa: SLF001
        decision,
        attempt,
    )

    assert action is None
    assert sequence_meta is None
    assert error_reason == "malformed"
    assert attempt.outcome == "malformed"
    assert attempt.reason == "multiple_tool_calls"
    assert errors == ["Expected exactly one tool call, got 2"]


def test_trade_propose_focus_handles_non_dict_post_turn_and_options() -> None:
    decision = {
        "decision_id": "decision_trade",
        "decision_type": "TRADE_PROPOSE_DECISION",
        "player_id": "P1",
        "state": {
            "players": [
                {"player_id": "P1", "bankrupt": False},
                {"player_id": "P2", "bankrupt": False},
                {"player_id": "P3", "bankrupt": True},
                {"player_id": "P4", "bankrupt": False},
            ]
        },
        "post_turn": ["unexpected"],
        "legal_actions": [{"action": "propose_trade"}],
    }

    focus = build_trade_propose_decision_focus(decision)

    assert focus["scenario"]["max_exchanges"] is None
    assert focus["scenario"]["eligible_counterparties_player_ids"] == ["P2", "P4"]
