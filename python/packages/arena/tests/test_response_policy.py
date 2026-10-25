"""Regressions for live Grok text responses and Claude partial refusals."""
import asyncio
import copy
import json

import pytest

from monopoly_arena.cloud_preflight import preflight
from monopoly_arena.decision_resolver import SharedDecisionResolver, parse_tool_calls
from monopoly_arena.job_store import JobStore
from monopoly_arena.openrouter_client import OpenRouterResult, _StreamingCompletionAccumulator
from monopoly_arena.player_config import build_single_player_config
from monopoly_arena.prompting import (
    PromptMemory, build_compact_decision, build_openrouter_tools,
    build_prompt_bundle, build_space_key_by_index,
)
from monopoly_engine import Engine
from monopoly_telemetry import init_run_files


def tool_response(name="buy_property", *, private=True):
    return {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [
        {"id": "tool-1", "type": "function", "function": {
            "name": name, "arguments": json.dumps({"public_message": "", **({"private_thought": "test"} if private else {})}),
        }},
    ]}}]}


def refused_response(with_tool=True):
    response = tool_response("start_auction")
    choice = response["choices"][0]
    choice.update(finish_reason="content_filter", native_finish_reason="refusal")
    choice["message"]["refusal"] = "Provider declined this request."
    if not with_tool:
        choice["message"].pop("tool_calls")
    return response


class ScriptedClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def create_chat_completion(self, **payload):
        self.calls.append(payload)
        response = self.responses.pop(0)
        return OpenRouterResult(True, 200, response, None, None, "test", response_text=json.dumps(response))


def resolve(tmp_path, responses, model="anthropic/claude-opus-5.5"):
    engine = Engine(seed=42, run_id="response-policy", players=[
        {"player_id": f"p{i+1}", "name": f"Player {i+1}"} for i in range(4)
    ])
    _, _, decision, _ = engine.advance_until_decision(max_steps=100)
    assert decision is not None
    client = ScriptedClient(responses)
    files = init_run_files(tmp_path, "response-policy")
    spaces = build_space_key_by_index()
    memory = PromptMemory(space_key_by_index=spaces)
    player = build_single_player_config(player_id=decision["player_id"], name="Player", openrouter_model_id=model,
                                        reasoning={"effort": "medium"})
    resolver = SharedDecisionResolver(openrouter=client, run_files=files, prompt_memory=memory,
        space_key_by_index=spaces, rules_validator=lambda d, a: engine.validate_action_for_decision(a, d))
    outcome = asyncio.run(resolver.resolve_decision(decision=decision, player_config=player, log_writer=None))
    return outcome, client, files, decision, player, memory


@pytest.mark.parametrize("signal", ["finish_reason", "native_finish_reason", "message_refusal", "stop_reason", "stop_details"])
def test_refusal_takes_precedence_over_valid_tool(signal):
    response = tool_response()
    choice = response["choices"][0]
    if signal == "finish_reason":
        choice[signal] = "content_filter"
    elif signal == "native_finish_reason":
        choice[signal] = "refusal"
    elif signal == "message_refusal":
        choice["message"]["refusal"] = "Declined."
    else:
        response[signal] = "refusal" if signal == "stop_reason" else {"type": "refusal", "category": None}
    assert parse_tool_calls(response) == (None, "Provider refused the response")


def test_normal_tool_is_not_rejected_based_on_prose():
    response = tool_response()
    response["choices"][0]["message"].update(content="I refuse their trade.", refusal=None)
    calls, error = parse_tool_calls(response)
    assert calls and calls[0]["name"] == "buy_property" and error is None


@pytest.mark.parametrize("with_tool", [False, True])
def test_refusal_retries_once_and_preserves_raw_response(tmp_path, with_tool):
    refused = refused_response(with_tool)
    original = copy.deepcopy(refused)
    outcome, client, files, *_ = resolve(tmp_path, [refused, tool_response(private=False)])
    assert len(client.calls) == 2 and outcome.retry_used and not outcome.fallback_used
    assert outcome.action["action"] == "buy_property"
    attempt = outcome.attempts[0]
    assert (attempt.outcome, attempt.reason) == ("refused", "provider_refusal")
    assert attempt.parsed_tool_calls is None and attempt.parsed_tool_call is None
    assert attempt.raw_response == original
    saved = [json.loads(p.read_text()) for p in files.prompts_dir.glob('*_parsed.json')]
    assert any(p["outcome"] == "refused" and p["reason"] == "provider_refusal" for p in saved)


@pytest.mark.parametrize("first", [refused_response(), {"choices": [{"message": {"content": "no tool"}}]}])
def test_refused_retry_uses_deterministic_fallback_not_partial_action(tmp_path, first):
    count = 3 if first.get("choices", [{}])[0].get("finish_reason") == "content_filter" else 2
    outcome, client, *_ = resolve(tmp_path, [first, *[refused_response() for _ in range(count-1)]])
    assert len(client.calls) == count and outcome.retry_used and outcome.fallback_used
    assert outcome.fallback_reason == "provider_refusal_after_retry"
    assert outcome.action["action"] == "buy_property"  # Refused proposal was start_auction.
    assert outcome.action["private_thought"] == "fallback"
    assert outcome.attempts[-1].parsed_tool_calls is None


@pytest.mark.parametrize("model,expected", [
    ("x-ai/grok-4.7", "required"), ("x-ai/grok-4.3", "auto"),
    ("anthropic/claude-opus-5.5", "auto"), ("openai/gpt-6.1-sol", "auto"),
    ("google/gemini-4-argon", "auto"),
])
def test_tool_choice_on_initial_call_and_retry_preserves_prompt(tmp_path, model, expected):
    # JSON in content remains invalid even when it describes a schema-valid move.
    text = {"choices": [{"message": {"content": json.dumps({"name": "buy_property", "arguments": {
        "public_message": "", "private_thought": "test",
    }})}}]}
    outcome, client, _, decision, player, memory = resolve(tmp_path, [text, tool_response()], model)
    assert outcome.retry_used and not outcome.fallback_used
    assert outcome.attempts[0].reason == "missing_tool_call"
    for call in client.calls:
        assert call["tool_choice"] == expected
        assert call["parallel_tool_calls"] is False
        assert call["reasoning"] == {"effort": "medium"}
        assert call["provider"] == player.provider
        assert call["tools"] == build_openrouter_tools(build_compact_decision(decision))
    for index, call in enumerate(client.calls):
        bundle = build_prompt_bundle(decision, player, memory=memory, space_key_by_index=build_space_key_by_index(),
            retry_errors=["No tool call found"] if index else None, retry_outcome="malformed" if index else None)
        assert call["messages"] == bundle.messages


@pytest.mark.parametrize("signal", ["delta_refusal", "native_finish_reason", "finish_reason", "stop_details"])
def test_streamed_refusal_cannot_be_lost_after_tool_deltas(signal):
    accumulator = _StreamingCompletionAccumulator(request_id="stream-refused")
    accumulator.apply_chunk({"choices": [{"delta": tool_response()["choices"][0]["message"]}]})
    if signal == "delta_refusal":
        chunk = {"choices": [{"delta": {"refusal": "Declined."}}]}
    elif signal == "stop_details":
        chunk = {"stop_details": {"type": "refusal", "category": "unknown"}}
    else:
        chunk = {"choices": [{signal: "refusal" if signal == "native_finish_reason" else "content_filter"}]}
    accumulator.apply_chunk(chunk)
    accumulator.apply_chunk({"choices": [{"delta": {}, "finish_reason": "stop"}]})
    response = accumulator.to_response_json()
    assert response["choices"][0]["message"]["tool_calls"]  # Kept as evidence, never accepted.
    assert parse_tool_calls(response) == (None, "Provider refused the response")


@pytest.mark.parametrize("refused", [False, True])
def test_preflight_uses_model_policy_and_rejects_refused_tools(tmp_path, monkeypatch, refused):
    calls = []
    class Client:
        def __init__(self, **kwargs):
            pass

        async def create_chat_completion(self, **payload):
            calls.append(payload)
            response = refused_response() if refused else tool_response(private="private_thought" in payload["tools"][0]["function"]["parameters"]["properties"])
            response.update(model=payload["model"], provider=payload["provider"]["only"][0])
            return OpenRouterResult(True, 200, response, None, None, "preflight-test")

        async def aclose(self):
            pass

    monkeypatch.setattr("monopoly_arena.cloud_preflight.OpenRouterClient", Client)
    report = asyncio.run(preflight(JobStore(tmp_path)))
    assert report["passed"] is not refused
    if refused:
        assert "provider refused" in report["error"]
        assert not report["routes"][0]["valid"]
        assert len(calls) == 3
    else:
        assert len(calls) == 5
        assert {p["model"]: p["tool_choice"] for p in calls} == {
            "anthropic/claude-opus-5.5": "auto", "openai/gpt-6.1-sol": "auto",
            "google/gemini-4-argon": "auto", "x-ai/grok-4.7": "required",
            "anthropic/claude-opus-4.8": "auto",
        }


@pytest.mark.parametrize("fallback", [False, True])
def test_refusal_recovery_keeps_reasoning_and_attributes_each_attempt(tmp_path, fallback):
    responses = [refused_response(), *([refused_response()] if fallback else []), tool_response(private=False)]
    outcome, client, files, decision, player, memory = resolve(tmp_path, responses)
    assert len(client.calls) == (3 if fallback else 2)
    assert not outcome.fallback_used and "private_thought" not in outcome.action
    assert outcome.sequence_meta["model_fallback_used"] is fallback
    assert [a.requested_model for a in outcome.attempts] == [c["model"] for c in client.calls]
    assert client.calls[-1]["model"] == ("anthropic/claude-opus-4.8" if fallback else player.openrouter_model_id)
    assert all(c["reasoning"] == {"effort": "medium"} for c in client.calls)
    assert all(c["provider"] == {"only": ["anthropic"], "allow_fallbacks": False} for c in client.calls)
    expected = build_prompt_bundle(decision, player, memory=memory, space_key_by_index=build_space_key_by_index())
    assert client.calls[0]["messages"] == expected.messages
    for call in client.calls[1:]:
        assert "Use it to reason honestly" not in call["messages"][0]["content"]
        for tool in call["tools"]:
            schema = tool["function"]["parameters"]
            assert "private_thought" not in schema["properties"]
            assert "private_thought" not in schema["required"]
        payload = json.loads(call["messages"][1]["content"])
        assert payload["game_state"] == expected.user_payload["game_state"]
    resolver = SharedDecisionResolver(openrouter=client, run_files=files, prompt_memory=memory,
                                     space_key_by_index=build_space_key_by_index())
    assert resolver.ensure_valid_outcome(decision=decision, outcome=outcome) is outcome
    parsed = sorted(files.prompts_dir.glob('*_parsed.json'))
    assert len(parsed) == len(client.calls)
    assert json.loads(parsed[-1].read_text())["requested_model"] == client.calls[-1]["model"]
    # Re-entering a saved decision must reuse all stages without new calls.
    recovered = asyncio.run(resolver.resolve_decision(decision=decision, player_config=player, log_writer=None))
    assert recovered.action == outcome.action and len(client.calls) == len(responses)


def test_malformed_action_only_retry_does_not_switch_models(tmp_path):
    malformed = {"choices": [{"message": {"content": "not a tool"}}]}
    outcome, client, *_ = resolve(tmp_path, [refused_response(), malformed])
    assert len(client.calls) == 2 and outcome.fallback_used
    assert outcome.fallback_reason == "malformed_after_retry"


def test_other_model_refusals_do_not_switch_models(tmp_path):
    outcome, client, *_ = resolve(tmp_path, [refused_response(), refused_response()], "openai/gpt-6.1-sol")
    assert len(client.calls) == 2 and outcome.fallback_used
    assert all(c["model"] == "openai/gpt-6.1-sol" for c in client.calls)


def test_action_only_retry_does_not_accept_a_new_private_note(tmp_path):
    outcome, client, *_ = resolve(tmp_path, [refused_response(), tool_response()])
    assert len(client.calls) == 2 and outcome.fallback_used
    assert outcome.attempts[-1].reason == "unexpected_private_thought"


@pytest.mark.parametrize("fallback_cost", [0.02, None])
def test_usage_nests_fallback_model_under_its_participant(fallback_cost):
    from monopoly_telemetry.usage import _attempt_usage_rows, _aggregate_usage, _decision_usage_rows
    chain = [("anthropic/claude-opus-5.5", "standard", 0.01),
             ("anthropic/claude-opus-5.5", "same_model_without_private_thought", 0.005),
             ("anthropic/claude-opus-4.8", "fallback_without_private_thought", fallback_cost)]
    attempts = [{"requested_model": model, "response_condition": condition, "raw_response": {"model": model, "usage": (
        {"is_byok": True, "cost": 0, "cost_details": {"upstream_inference_cost": cost}} if cost is not None else {})}}
        for model, condition, cost in chain]
    ordinary = [{"requested_model": "anthropic/claude-opus-5.5", "response_condition": "standard",
                 "raw_response": {"model": "anthropic/claude-opus-5.5", "usage": {"cost": 0.001}}}]
    decisions = [{"phase": "decision_resolved", "decision_id": decision_id, "player_id": "p1",
                  "openrouter_model_id": "anthropic/claude-opus-5.5", "attempts": decision_attempts}
                 for decision_id, decision_attempts in (("d1", attempts), ("d2", ordinary))]
    rows = _attempt_usage_rows(decisions)
    # Each attempt names the model that served it, its participant, and whether it was a fallback.
    assert [r["openrouter_model_id"] for r in rows] == [m for m, _, _ in chain] + ["anthropic/claude-opus-5.5"]
    assert {r["participant_model_id"] for r in rows} == {"anthropic/claude-opus-5.5"}
    assert [r["fallback_model_used"] for r in rows] == [False, False, True, False]
    decision_rows = _decision_usage_rows(rows)
    assert [(d["openrouter_model_id"], d["fallback_attempt_count"], d["fallback_models_used"]) for d in decision_rows] == [
        ("anthropic/claude-opus-5.5", 1, ["anthropic/claude-opus-4.8"]), ("anthropic/claude-opus-5.5", 0, [])]
    report = _aggregate_usage("test", rows, decision_rows)
    # The fallback is not a participant: it appears only under the seat that used it.
    assert set(report["by_model"]) == {"anthropic/claude-opus-5.5"}
    assert report["fallback_attempt_count"] == 1
    for umbrella in (report["by_model"]["anthropic/claude-opus-5.5"], report["by_player"]["p1"]):
        known_total = 0.01 + 0.005 + 0.001 + (fallback_cost or 0)
        assert umbrella["known_cost_subtotal"] == pytest.approx(known_total)
        assert umbrella["cost"] == (pytest.approx(known_total) if fallback_cost is not None else None)
        own = umbrella["own_model"]
        assert (own["attempt_count"], own["cost"], own["missing_cost_attempt_count"]) == (3, pytest.approx(0.016), 0)
        fallback = umbrella["fallback_models"]["anthropic/claude-opus-4.8"]
        assert fallback["attempt_count"] == 1 and fallback["decision_ids"] == ["d1"] and fallback["decision_count"] == 1
        assert fallback["cost"] == (pytest.approx(fallback_cost) if fallback_cost is not None else None)
        assert fallback["known_cost_subtotal"] == pytest.approx(fallback_cost or 0)
        assert fallback["missing_cost_attempt_count"] == (0 if fallback_cost is not None else 1)
        assert fallback["response_conditions"] == ["fallback_without_private_thought"]
        assert fallback["triggers"] == ["explicit_provider_refusal_after_same_model_retry"]
        assert fallback["served_model_ids"] == ["anthropic/claude-opus-4.8"]


@pytest.mark.parametrize("saved_condition", [True, False])
def test_unfinished_fallback_call_keeps_its_trigger(tmp_path, saved_condition):
    from monopoly_telemetry import init_run_files
    from monopoly_telemetry.usage import build_usage_report
    from monopoly_arena.decision_resolver import SharedDecisionResolver
    from monopoly_arena.prompting import PromptMemory, build_space_key_by_index

    class Client:
        async def create_chat_completion(self, **kwargs):
            return OpenRouterResult(True, 200, {"id": "gen", "model": kwargs["model"], "usage": {"cost": 0.02}},
                                    None, None, "request")

    files = init_run_files(tmp_path, "unfinished-fallback")
    # The decision started, Opus 4.8 was called, and the run stopped before decision_resolved.
    files.write_decision({"phase": "decision_started", "decision_id": "d1", "player_id": "p1",
                          "openrouter_model_id": "anthropic/claude-opus-5.5"})
    resolver = SharedDecisionResolver(openrouter=Client(), run_files=files,
                                      prompt_memory=PromptMemory(space_key_by_index=build_space_key_by_index()),
                                      space_key_by_index=build_space_key_by_index())
    decision = {"decision_id": "d1", "player_id": "p1", "turn_index": 0, "decision_type": "BUY_OR_AUCTION_DECISION"}
    asyncio.run(resolver._call_completion(decision, 2, {"model": "anthropic/claude-opus-4.8"},
                                          response_condition="fallback_without_private_thought"))
    record_path = next((files.run_dir / "calls").glob("*.json"))
    if not saved_condition:  # A durable record written before conditions were saved.
        record = json.loads(record_path.read_text())
        record.pop("response_condition")
        record_path.write_text(json.dumps(record))
    report = build_usage_report(files)
    assert set(report["by_model"]) == {"anthropic/claude-opus-5.5"}
    fallback = report["by_model"]["anthropic/claude-opus-5.5"]["fallback_models"]["anthropic/claude-opus-4.8"]
    assert fallback["cost"] == pytest.approx(0.02) and fallback["decision_ids"] == ["d1"]
    assert fallback["triggers"] == (["explicit_provider_refusal_after_same_model_retry"] if saved_condition
                                    else ["unrecognized_condition:unrecorded"])
