from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from monopoly_telemetry import RunFiles

from .action_validation import validate_action_payload
from .openrouter_client import OpenRouterResult
from .player_config import PlayerConfig
from .prompting import (
    PromptBundle,
    PromptMemory,
    build_compact_decision,
    build_openrouter_tools,
    build_prompt_bundle,
)


DecisionLogWriter = Callable[[dict[str, Any]], Awaitable[None]]
RulesValidator = Callable[[dict[str, Any], dict[str, Any]], list[str]]


@dataclass(slots=True)
class DecisionResolutionAttempt:
    prompt_messages: list[dict[str, Any]]
    prompt_payload: dict[str, Any] | None
    prompt_payload_raw: str | None
    raw_response: dict[str, Any] | None
    assistant_content: str | None
    parsed_tool_call: dict[str, Any] | None
    parsed_tool_calls: list[dict[str, Any]] | None
    validation_errors: list[str]
    openrouter_request_id: str | None
    openrouter_status_code: int | None
    error_type: str | None
    error_message: str | None
    request_start_ms: int | None
    response_end_ms: int | None
    latency_ms: int | None
    outcome: str | None = None
    reason: str | None = None


@dataclass(slots=True)
class DecisionResolutionOutcome:
    action: dict[str, Any]
    decision_meta: dict[str, Any]
    attempts: list[DecisionResolutionAttempt]
    retry_used: bool
    fallback_used: bool
    fallback_reason: str | None
    sequence_meta: dict[str, Any] | None = None
    automated: bool = False


class SharedDecisionResolver:
    def __init__(
        self,
        *,
        openrouter: Any,
        run_files: RunFiles | None,
        prompt_memory: PromptMemory,
        space_key_by_index: dict[int, str],
        rules_validator: RulesValidator | None = None,
    ) -> None:
        self._openrouter = openrouter
        self._run_files = run_files
        self._prompt_memory = prompt_memory
        self._space_key_by_index = space_key_by_index
        self._rules_validator = rules_validator

    async def resolve_decision(
        self,
        *,
        decision: dict[str, Any],
        player_config: PlayerConfig,
        log_writer: DecisionLogWriter | None,
    ) -> DecisionResolutionOutcome:
        attempts: list[DecisionResolutionAttempt] = []
        artifact_attempts: list[dict[str, Any]] = []

        async def emit(entry: dict[str, Any]) -> None:
            if log_writer is not None:
                await log_writer(entry)

        prompt_bundle = build_prompt_bundle(
            decision,
            player_config,
            memory=self._prompt_memory,
            space_key_by_index=self._space_key_by_index,
        )
        tools = build_openrouter_tools(build_compact_decision(decision))

        def response_payload(result: OpenRouterResult | None) -> dict[str, Any]:
            if result is None:
                return {
                    "ok": False,
                    "status_code": None,
                    "request_id": None,
                    "error_type": "no_request",
                    "error": "No OpenRouter request was made",
                }
            if result.response_json is not None:
                return result.response_json
            return {
                "ok": False,
                "status_code": result.status_code,
                "request_id": result.request_id,
                "error_type": result.error_type,
                "error": result.error,
            }

        def write_artifacts(outcome: DecisionResolutionOutcome) -> None:
            if self._run_files is None:
                return
            for item in artifact_attempts:
                attempt_index = int(item.get("attempt_index", 0))
                prompt_item = item.get("prompt_bundle")
                if not isinstance(prompt_item, PromptBundle):
                    continue
                attempt_item = item.get("attempt")
                tool_action = item.get("action")
                validation_errors = item.get("errors")
                if not isinstance(validation_errors, list):
                    validation_errors = []
                error_reason = item.get("error_reason")
                parsed = {
                    "schema_version": "v1",
                    "decision_id": decision["decision_id"],
                    "attempt_index": attempt_index,
                    "parsed_tool_call": attempt_item.parsed_tool_call
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "parsed_tool_calls": attempt_item.parsed_tool_calls
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "validation_errors": validation_errors,
                    "error_reason": error_reason,
                    "outcome": attempt_item.outcome
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "reason": attempt_item.reason
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "tool_action": tool_action,
                    "openrouter_request_id": attempt_item.openrouter_request_id
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "openrouter_status_code": attempt_item.openrouter_status_code
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "openrouter_error_type": attempt_item.error_type
                    if isinstance(attempt_item, DecisionResolutionAttempt)
                    else None,
                    "final_action": outcome.action,
                    "retry_used": outcome.retry_used,
                    "fallback_used": outcome.fallback_used,
                    "fallback_reason": outcome.fallback_reason,
                    "sequence_meta": outcome.sequence_meta,
                }
                self._run_files.write_prompt_artifacts(
                    decision_id=decision["decision_id"],
                    attempt_index=attempt_index,
                    system_prompt=prompt_item.system_prompt,
                    user_payload=prompt_item.user_payload,
                    tools=tools,
                    response=response_payload(item.get("result")),
                    parsed=parsed,
                )

        if not tools:
            fallback_action = self._fallback_action(decision)
            outcome = self._build_decision_outcome(
                action=fallback_action,
                attempts=attempts,
                retry_used=False,
                fallback_used=True,
                fallback_reason="unknown",
            )
            artifact_attempts.append(
                {
                    "attempt_index": 0,
                    "prompt_bundle": prompt_bundle,
                    "result": None,
                    "attempt": None,
                    "action": None,
                    "errors": ["No tools generated"],
                    "error_reason": "no_tools",
                }
            )
            write_artifacts(outcome)
            return outcome

        request_start_ms = _now_ms()
        await emit(
            self.build_decision_log_entry(
                decision=decision,
                player_config=player_config,
                phase="decision_started",
                action=None,
                attempts=[],
                retry_used=False,
                fallback_used=False,
                fallback_reason=None,
                request_start_ms=request_start_ms,
                prompt_messages=prompt_bundle.messages,
                prompt_payload=prompt_bundle.user_payload,
                prompt_payload_raw=prompt_bundle.user_content,
            )
        )
        tool_choice = "required"
        parallel_tool_calls = False
        create_kwargs: dict[str, Any] = {
            "model": player_config.openrouter_model_id,
            "messages": prompt_bundle.messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "parallel_tool_calls": parallel_tool_calls,
        }
        if player_config.reasoning is not None:
            create_kwargs["reasoning"] = player_config.reasoning
        result = await self._openrouter.create_chat_completion(**create_kwargs)
        response_end_ms = _now_ms()
        request_payload_raw = result.request_payload_raw or self._build_request_payload_raw(
            model=player_config.openrouter_model_id,
            messages=prompt_bundle.messages,
            tools=tools,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            reasoning=player_config.reasoning,
        )
        self._write_quality_artifacts(
            decision_id=decision["decision_id"],
            attempt_index=0,
            request_text=request_payload_raw,
            response_text=result.response_text,
        )
        attempt = self._attempt_from_response(
            prompt_bundle,
            result,
            request_start_ms,
            response_end_ms,
            include_prompt=False,
        )
        attempts.append(attempt)
        action, errors, error_reason, sequence_meta = self._build_action_from_attempt(decision, attempt)
        outcome_sequence_meta = sequence_meta
        artifact_attempts.append(
            {
                "attempt_index": 0,
                "prompt_bundle": prompt_bundle,
                "result": result,
                "attempt": attempt,
                "action": action,
                "errors": list(attempt.validation_errors),
                "error_reason": error_reason,
            }
        )

        if not result.ok and result.error_type != "invalid_json":
            outcome = self._build_decision_outcome(
                action=self._fallback_action(decision),
                attempts=attempts,
                retry_used=False,
                fallback_used=True,
                fallback_reason=_map_openrouter_error(result.error_type),
                sequence_meta=outcome_sequence_meta,
            )
            write_artifacts(outcome)
            return outcome

        if errors:
            retry_bundle = build_prompt_bundle(
                decision,
                player_config,
                memory=self._prompt_memory,
                space_key_by_index=self._space_key_by_index,
                retry_errors=errors,
                retry_outcome=error_reason,
            )
            retry_start_ms = _now_ms()
            retry_kwargs = {
                "model": player_config.openrouter_model_id,
                "messages": retry_bundle.messages,
                "tools": tools,
                "tool_choice": tool_choice,
                "parallel_tool_calls": parallel_tool_calls,
            }
            if player_config.reasoning is not None:
                retry_kwargs["reasoning"] = player_config.reasoning
            retry_result = await self._openrouter.create_chat_completion(**retry_kwargs)
            retry_end_ms = _now_ms()
            retry_request_payload_raw = retry_result.request_payload_raw or self._build_request_payload_raw(
                model=player_config.openrouter_model_id,
                messages=retry_bundle.messages,
                tools=tools,
                tool_choice=tool_choice,
                parallel_tool_calls=parallel_tool_calls,
                reasoning=player_config.reasoning,
            )
            self._write_quality_artifacts(
                decision_id=decision["decision_id"],
                attempt_index=1,
                request_text=retry_request_payload_raw,
                response_text=retry_result.response_text,
            )
            retry_attempt = self._attempt_from_response(
                retry_bundle,
                retry_result,
                retry_start_ms,
                retry_end_ms,
                include_prompt=True,
            )
            attempts.append(retry_attempt)
            retry_action, retry_errors, retry_error_reason, retry_sequence_meta = self._build_action_from_attempt(
                decision,
                retry_attempt,
            )
            outcome_sequence_meta = retry_sequence_meta
            artifact_attempts.append(
                {
                    "attempt_index": 1,
                    "prompt_bundle": retry_bundle,
                    "result": retry_result,
                    "attempt": retry_attempt,
                    "action": retry_action,
                    "errors": list(retry_attempt.validation_errors),
                    "error_reason": retry_error_reason,
                }
            )
            if not retry_result.ok and retry_result.error_type != "invalid_json":
                outcome = self._build_decision_outcome(
                    action=self._fallback_action(decision),
                    attempts=attempts,
                    retry_used=True,
                    fallback_used=True,
                    fallback_reason=_map_openrouter_error(retry_result.error_type),
                    sequence_meta=outcome_sequence_meta,
                )
                write_artifacts(outcome)
                return outcome
            if retry_errors:
                outcome = self._build_decision_outcome(
                    action=self._fallback_action(decision),
                    attempts=attempts,
                    retry_used=True,
                    fallback_used=True,
                    fallback_reason=_fallback_reason_after_retry(retry_error_reason),
                    sequence_meta=outcome_sequence_meta,
                )
                write_artifacts(outcome)
                return outcome
            outcome = self._build_decision_outcome(
                action=retry_action or self._fallback_action(decision),
                attempts=attempts,
                retry_used=True,
                fallback_used=False,
                fallback_reason=None,
                sequence_meta=outcome_sequence_meta,
            )
            write_artifacts(outcome)
            return outcome

        outcome = self._build_decision_outcome(
            action=action or self._fallback_action(decision),
            attempts=attempts,
            retry_used=False,
            fallback_used=False,
            fallback_reason=None,
            sequence_meta=outcome_sequence_meta,
        )
        write_artifacts(outcome)
        return outcome

    def ensure_valid_outcome(
        self,
        *,
        decision: dict[str, Any],
        outcome: DecisionResolutionOutcome,
    ) -> DecisionResolutionOutcome:
        errors = validate_decision_action(decision, outcome.action)
        if not errors and self._rules_validator is not None:
            errors = self._rules_validator(decision, outcome.action)
        if not errors:
            return outcome
        return self._build_decision_outcome(
            action=self._fallback_action(decision),
            attempts=outcome.attempts,
            retry_used=outcome.retry_used,
            fallback_used=True,
            fallback_reason="illogical_after_pause",
            sequence_meta=outcome.sequence_meta,
            automated=outcome.automated,
        )

    def build_decision_log_entry(
        self,
        *,
        decision: dict[str, Any],
        player_config: PlayerConfig,
        phase: str,
        action: dict[str, Any] | None,
        attempts: list[DecisionResolutionAttempt],
        retry_used: bool,
        fallback_used: bool,
        fallback_reason: str | None,
        request_start_ms: int | None = None,
        prompt_messages: list[dict[str, Any]] | None = None,
        prompt_payload: dict[str, Any] | None = None,
        prompt_payload_raw: str | None = None,
        action_events: list[dict[str, Any]] | None = None,
        applied: bool | None = None,
        sequence_meta: dict[str, Any] | None = None,
        automated: bool = False,
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "phase": phase,
            "run_id": decision["run_id"],
            "turn_index": decision["turn_index"],
            "decision_id": decision["decision_id"],
            "decision_type": decision["decision_type"],
            "player_id": decision["player_id"],
            "player_name": player_config.name,
            "openrouter_model_id": player_config.openrouter_model_id,
            "model_display_name": player_config.model_display_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if player_config.reasoning is not None:
            entry["reasoning"] = player_config.reasoning
        if phase == "decision_started":
            entry["request_start_ms"] = request_start_ms
            entry["prompt_messages"] = prompt_messages or []
            entry["prompt_payload"] = prompt_payload
            entry["prompt_payload_raw"] = prompt_payload_raw
            if sequence_meta is not None:
                entry["sequence_meta"] = sequence_meta
            if automated:
                entry["automated"] = True
            return entry

        entry["attempts"] = [
            {
                "prompt_messages": attempt.prompt_messages,
                "prompt_payload": attempt.prompt_payload,
                "prompt_payload_raw": attempt.prompt_payload_raw,
                "raw_response": attempt.raw_response,
                "assistant_content": attempt.assistant_content,
                "parsed_tool_call": attempt.parsed_tool_call,
                "parsed_tool_calls": attempt.parsed_tool_calls,
                "validation_errors": attempt.validation_errors,
                "outcome": attempt.outcome,
                "reason": attempt.reason,
                "openrouter_request_id": attempt.openrouter_request_id,
                "openrouter_status_code": attempt.openrouter_status_code,
                "error_type": attempt.error_type,
                "error_message": attempt.error_message,
                "request_start_ms": attempt.request_start_ms,
                "response_end_ms": attempt.response_end_ms,
                "latency_ms": attempt.latency_ms,
            }
            for attempt in attempts
        ]
        entry["retry_used"] = retry_used
        entry["fallback_used"] = fallback_used
        entry["fallback_reason"] = fallback_reason
        entry["final_action"] = action
        if sequence_meta is not None:
            entry["sequence_meta"] = sequence_meta
        if automated:
            entry["automated"] = True
        if fallback_used:
            entry["fallback_action"] = action
        if applied is not None:
            entry["applied"] = applied
        if action_events is not None:
            event_ids = [event.get("event_id") for event in action_events]
            event_types = [event.get("type") for event in action_events]
            seqs: list[int] = []
            for event in action_events:
                seq = event.get("seq")
                if isinstance(seq, int):
                    seqs.append(seq)
            entry["emitted_event_ids"] = event_ids
            entry["emitted_event_types"] = event_types
            if seqs:
                entry["emitted_event_seq_start"] = min(seqs)
                entry["emitted_event_seq_end"] = max(seqs)
        decision_start_ms = request_start_ms
        if decision_start_ms is None and attempts:
            decision_start_ms = attempts[0].request_start_ms
        decision_end_ms = attempts[-1].response_end_ms if attempts else None
        if decision_start_ms is not None:
            entry["request_start_ms"] = decision_start_ms
        if decision_end_ms is not None:
            entry["response_end_ms"] = decision_end_ms
        if decision_start_ms is not None and decision_end_ms is not None:
            entry["latency_ms"] = max(decision_end_ms - decision_start_ms, 0)
        return entry

    def _attempt_from_response(
        self,
        prompt: PromptBundle,
        result: OpenRouterResult,
        request_start_ms: int | None,
        response_end_ms: int | None,
        *,
        include_prompt: bool,
    ) -> DecisionResolutionAttempt:
        response_json = result.response_json if result.ok else None
        assistant_content = None
        tool_calls = None
        errors: list[str] = []
        if response_json is None:
            errors.append(result.error or "OpenRouter error")
        else:
            assistant_content = response_json.get("choices", [{}])[0].get("message", {}).get("content")
            tool_calls, parse_error = parse_tool_calls(response_json)
            if parse_error:
                errors.append(parse_error)
        latency_ms = None
        if request_start_ms is not None and response_end_ms is not None:
            latency_ms = max(response_end_ms - request_start_ms, 0)
        prompt_messages: list[dict[str, Any]] = []
        prompt_payload = None
        prompt_payload_raw = None
        if include_prompt:
            prompt_messages = prompt.messages
            prompt_payload = prompt.user_payload
            prompt_payload_raw = prompt.user_content
        first_tool_call = tool_calls[0] if tool_calls else None
        return DecisionResolutionAttempt(
            prompt_messages=prompt_messages,
            prompt_payload=prompt_payload,
            prompt_payload_raw=prompt_payload_raw,
            raw_response=response_json,
            assistant_content=assistant_content,
            parsed_tool_call=first_tool_call,
            parsed_tool_calls=tool_calls,
            validation_errors=errors,
            openrouter_request_id=result.request_id,
            openrouter_status_code=result.status_code,
            error_type=result.error_type,
            error_message=result.error,
            request_start_ms=request_start_ms,
            response_end_ms=response_end_ms,
            latency_ms=latency_ms,
        )

    def _build_action_from_attempt(
        self,
        decision: dict[str, Any],
        attempt: Any,
        *,
        check_rules: bool = True,
    ) -> tuple[dict[str, Any] | None, list[str], str | None, dict[str, Any] | None]:
        parsed_tool_calls = attempt.parsed_tool_calls or []
        if not parsed_tool_calls:
            errors = attempt.validation_errors or ["Missing tool call"]
            if not attempt.validation_errors:
                attempt.validation_errors.extend(errors)
            _mark_attempt(attempt, "malformed", "missing_tool_call")
            return None, errors, "malformed", None
        if len(parsed_tool_calls) != 1:
            errors = [f"Expected exactly one tool call, got {len(parsed_tool_calls)}"]
            attempt.validation_errors.extend(errors)
            _mark_attempt(attempt, "malformed", "multiple_tool_calls")
            return None, errors, "malformed", None
        action, conversion_error = tool_call_to_action(decision, parsed_tool_calls[0])
        if action is None:
            errors = [conversion_error or "Unable to map tool call to action"]
            attempt.validation_errors.extend(errors)
            _mark_attempt(attempt, "malformed", _malformed_reason_from_errors(errors))
            return None, errors, "malformed", None
        errors = validate_decision_action(decision, action)
        if errors:
            attempt.validation_errors.extend(errors)
            _mark_attempt(attempt, "malformed", _malformed_reason_from_errors(errors))
            return action, errors, "malformed", None
        if check_rules and self._rules_validator is not None:
            rule_errors = self._rules_validator(decision, action)
            if rule_errors:
                attempt.validation_errors.extend(rule_errors)
                _mark_attempt(attempt, "illogical", _illogical_reason_from_errors(rule_errors))
                return action, rule_errors, "illogical", None
        _mark_attempt(attempt, "valid", None)
        return action, [], None, {"parsed_tool_calls_count": len(parsed_tool_calls)}

    def _build_decision_outcome(
        self,
        *,
        action: dict[str, Any],
        attempts: list[DecisionResolutionAttempt],
        retry_used: bool,
        fallback_used: bool,
        fallback_reason: str | None,
        sequence_meta: dict[str, Any] | None = None,
        automated: bool = False,
    ) -> DecisionResolutionOutcome:
        decision_meta: dict[str, Any] = {"valid": True, "error": None}
        if fallback_used:
            decision_meta = {"valid": False, "error": f"fallback:{fallback_reason or 'unknown'}"}
        return DecisionResolutionOutcome(
            action=action,
            decision_meta=decision_meta,
            attempts=attempts,
            retry_used=retry_used,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            sequence_meta=sequence_meta,
            automated=automated,
        )

    def _fallback_action(self, decision: dict[str, Any]) -> dict[str, Any]:
        legal_actions = [entry["action"] for entry in decision.get("legal_actions", []) if entry.get("action")]
        decision_id = decision["decision_id"]

        def with_messages(payload: dict[str, Any]) -> dict[str, Any]:
            payload["public_message"] = payload.get("public_message") or ""
            payload["private_thought"] = payload.get("private_thought") or "fallback"
            return payload

        def first_space_key(indices: list[int] | None) -> str | None:
            if not indices:
                return None
            index = int(indices[0])
            return self._space_key_by_index.get(index, f"SPACE_{index}")

        post_turn = decision.get("post_turn", {})
        post_options = post_turn.get("options", {}) if isinstance(post_turn, dict) else {}
        liquidation = decision.get("liquidation", {})
        liq_options = liquidation.get("options", {}) if isinstance(liquidation, dict) else {}

        if decision.get("decision_type") == "AUCTION_BID_DECISION":
            auction = decision.get("state", {}).get("auction", {})
            current_high_bid = int(auction.get("current_high_bid", 0) or 0)
            min_next_bid = current_high_bid + 1
            player_cash = None
            action_name = "NOOP"
            auction_args: dict[str, Any] = {"reason": "fallback"}
            for player in decision.get("state", {}).get("players", []):
                if player.get("player_id") == decision.get("player_id"):
                    player_cash = int(player.get("cash", 0))
                    break
            if "bid_auction" in legal_actions and player_cash is not None and player_cash >= min_next_bid:
                action_name = "bid_auction"
                auction_args = {"bid_amount": min_next_bid}
            elif "drop_out" in legal_actions:
                action_name = "drop_out"
                auction_args = {}
            elif legal_actions:
                action_name = legal_actions[0]
                auction_args = {}
            return with_messages(
                {
                    "schema_version": "v1",
                    "decision_id": decision_id,
                    "action": action_name,
                    "args": auction_args,
                }
            )

        if decision.get("decision_type") == "TRADE_RESPONSE_DECISION":
            if "reject_trade" in legal_actions:
                return with_messages(
                    {
                        "schema_version": "v1",
                        "decision_id": decision_id,
                        "action": "reject_trade",
                        "args": {},
                    }
                )
            if "accept_trade" in legal_actions:
                return with_messages(
                    {
                        "schema_version": "v1",
                        "decision_id": decision_id,
                        "action": "accept_trade",
                        "args": {},
                    }
                )
            if "counter_trade" in legal_actions:
                return with_messages(
                    {
                        "schema_version": "v1",
                        "decision_id": decision_id,
                        "action": "counter_trade",
                        "args": {
                            "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                            "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                        },
                    }
                )

        if decision.get("decision_type") == "TRADE_PROPOSE_DECISION" and "propose_trade" in legal_actions:
            players = decision.get("state", {}).get("players", [])
            actor_id = decision.get("player_id")
            target_id = None
            for entry in players:
                if entry.get("player_id") != actor_id and not entry.get("bankrupt"):
                    target_id = entry.get("player_id")
                    break
            if target_id:
                return with_messages(
                    {
                        "schema_version": "v1",
                        "decision_id": decision_id,
                        "action": "propose_trade",
                        "args": {
                            "to_player_id": target_id,
                            "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                            "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                        },
                    }
                )

        def build_plan_args(indices: list[int] | None) -> dict[str, Any] | None:
            if not indices:
                return None
            space_key = first_space_key(indices)
            if space_key is None:
                return None
            board = decision.get("state", {}).get("board", [])
            matching: dict[str, Any] = next((space for space in board if space.get("index") == indices[0]), {})
            houses = int(matching.get("houses", 0))
            hotel = bool(matching.get("hotel", False))
            kind = "HOTEL" if hotel or houses >= 4 else "HOUSE"
            return {"build_plan": [{"space_key": space_key, "kind": kind, "count": 1}]}

        def sell_plan_args(indices: list[int] | None) -> dict[str, Any] | None:
            if not indices:
                return None
            space_key = first_space_key(indices)
            if space_key is None:
                return None
            board = decision.get("state", {}).get("board", [])
            matching: dict[str, Any] = next((space for space in board if space.get("index") == indices[0]), {})
            hotel = bool(matching.get("hotel", False))
            kind = "HOTEL" if hotel else "HOUSE"
            return {"sell_plan": [{"space_key": space_key, "kind": kind, "count": 1}]}

        action_name = "NOOP"
        args: dict[str, Any] = {"reason": "fallback"}
        if "buy_property" in legal_actions:
            action_name = "buy_property"
            args = {}
        elif "start_auction" in legal_actions:
            action_name = "start_auction"
            args = {}
        elif "end_turn" in legal_actions:
            action_name = "end_turn"
            args = {}
        elif "declare_bankruptcy" in legal_actions:
            action_name = "declare_bankruptcy"
            args = {}
        elif "mortgage_property" in legal_actions:
            space_key = first_space_key(
                post_options.get("mortgageable_space_indices") or liq_options.get("mortgageable_space_indices")
            )
            if space_key:
                action_name = "mortgage_property"
                args = {"space_key": space_key}
            else:
                action_name = "declare_bankruptcy"
                args = {}
        elif "unmortgage_property" in legal_actions:
            space_key = first_space_key(post_options.get("unmortgageable_space_indices"))
            if space_key:
                action_name = "unmortgage_property"
                args = {"space_key": space_key}
            else:
                action_name = "end_turn"
                args = {}
        elif "sell_houses_or_hotel" in legal_actions:
            args_payload = sell_plan_args(
                post_options.get("sellable_building_space_indices")
                or liq_options.get("sellable_building_space_indices")
            )
            if args_payload:
                action_name = "sell_houses_or_hotel"
                args = args_payload
            elif "declare_bankruptcy" in legal_actions:
                action_name = "declare_bankruptcy"
                args = {}
            else:
                action_name = "end_turn"
                args = {}
        elif "build_houses_or_hotel" in legal_actions:
            args_payload = build_plan_args(post_options.get("buildable_space_indices"))
            if args_payload:
                action_name = "build_houses_or_hotel"
                args = args_payload
            else:
                action_name = "end_turn"
                args = {}
        elif legal_actions:
            action_name = legal_actions[0]
            args = {}
        return with_messages(
            {
                "schema_version": "v1",
                "decision_id": decision_id,
                "action": action_name,
                "args": args,
            }
        )

    def _build_request_payload_raw(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        tool_choice: str | dict[str, Any] | None,
        parallel_tool_calls: bool | None,
        reasoning: dict[str, Any] | None,
    ) -> str:
        payload: dict[str, Any] = {"model": model, "messages": messages, "temperature": 0.0}
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if parallel_tool_calls is not None:
            payload["parallel_tool_calls"] = parallel_tool_calls
        if reasoning is not None:
            payload["reasoning"] = reasoning
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)

    def _write_quality_artifacts(
        self,
        *,
        decision_id: str,
        attempt_index: int,
        request_text: str | None,
        response_text: str | None,
    ) -> None:
        if self._run_files is None:
            return
        self._run_files.write_quality_artifacts(
            decision_id=decision_id,
            attempt_index=attempt_index,
            request_text=request_text,
            response_text=response_text,
        )


def _now_ms() -> int:
    return int(time.time() * 1000)


def _map_openrouter_error(error_type: str | None) -> str:
    mapping = {
        "no_api_key": "no_api_key",
        "http_429": "openrouter_http_429",
        "http_5xx": "openrouter_http_5xx",
        "http_4xx": "openrouter_http_4xx",
        "network_error": "openrouter_network_error",
        "invalid_json": "invalid_tool_call",
    }
    if error_type is None:
        return "unknown"
    return mapping.get(error_type, "unknown")


def _mark_attempt(
    attempt: Any,
    outcome: str,
    reason: str | None,
) -> None:
    attempt.outcome = outcome
    attempt.reason = reason


def _fallback_reason_after_retry(reason: str | None) -> str:
    if reason == "malformed":
        return "malformed_after_retry"
    if reason == "illogical":
        return "illogical_after_retry"
    return reason or "invalid_action_after_retry"


def _malformed_reason_from_errors(errors: list[str]) -> str:
    text = " ".join(errors).lower()
    if "exactly one tool call" in text:
        return "multiple_tool_calls"
    if "no tool call" in text or "missing tool call" in text:
        return "missing_tool_call"
    if "not legal" in text or "unknown tool" in text:
        return "unknown_tool"
    if "not valid json" in text:
        return "bad_json_arguments"
    if "missing required public_message" in text or "missing required private_thought" in text:
        return "missing_required_message"
    if "missing required" in text:
        return "missing_required_arg"
    return "protocol_invalid"


def _illogical_reason_from_errors(errors: list[str]) -> str:
    text = " ".join(errors).lower()
    if "bid below minimum" in text:
        return "bid_below_minimum"
    if "insufficient cash for bid" in text:
        return "bid_exceeds_cash"
    if "not current bidder" in text:
        return "not_current_bidder"
    if "cannot mortgage" in text or "property already mortgaged" in text:
        return "invalid_mortgage"
    if "cannot unmortgage" in text or "property not mortgaged" in text:
        return "invalid_unmortgage"
    if "cannot build" in text or "uneven building" in text or "build" in text:
        return "invalid_build"
    if "cannot sell" in text or "not enough houses" in text or "no hotel" in text or "sell" in text:
        return "invalid_sell"
    if "trade" in text:
        return "invalid_trade"
    if "jail" in text:
        return "invalid_jail_action"
    return "rules_invalid"


def parse_tool_calls(response_json: dict[str, Any]) -> tuple[list[dict[str, Any]] | None, str | None]:
    choices = response_json.get("choices", [])
    if not choices:
        return None, "No choices in response"
    message = choices[0].get("message", {})
    tool_calls = message.get("tool_calls") or []
    if tool_calls:
        parsed_calls: list[dict[str, Any]] = []
        for idx, call in enumerate(tool_calls):
            func = call.get("function", {})
            name = func.get("name")
            if not isinstance(name, str) or not name.strip():
                return None, f"Tool call #{idx} missing function.name"
            parsed_calls.append({"name": name, "arguments": func.get("arguments")})
        return parsed_calls, None
    function_call = message.get("function_call")
    if function_call:
        name = function_call.get("name")
        if not isinstance(name, str) or not name.strip():
            return None, "function_call missing name"
        return [{"name": name, "arguments": function_call.get("arguments")}], None
    return None, "No tool call found"


def tool_call_to_action(
    decision: dict[str, Any],
    tool_call: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    tool_name = tool_call.get("name")
    if not tool_name:
        return None, "Tool call missing name"
    legal_actions = [entry.get("action") for entry in decision.get("legal_actions", [])]
    action_name = _resolve_action_name(tool_name, legal_actions)
    if action_name is None:
        return None, f"Tool '{tool_name}' is not legal for this decision"

    arguments = tool_call.get("arguments")
    if isinstance(arguments, str):
        try:
            args_payload = json.loads(arguments)
        except json.JSONDecodeError:
            return None, "Tool call arguments are not valid JSON"
    elif isinstance(arguments, dict):
        args_payload = arguments
    else:
        args_payload = {}

    if not isinstance(args_payload, dict):
        return None, "Tool call arguments must be an object"

    payload_without_messages, messages, message_errors = _extract_message_fields(args_payload)
    if message_errors:
        return None, "; ".join(message_errors)

    args, arg_errors = _canonicalize_action_args(action_name, payload_without_messages)
    if arg_errors:
        return None, "; ".join(arg_errors)

    action = {
        "schema_version": "v1",
        "decision_id": decision["decision_id"],
        "action": action_name,
        "args": args,
    }
    if "public_message" in messages:
        action["public_message"] = messages.get("public_message")
    if "private_thought" in messages:
        action["private_thought"] = messages.get("private_thought")
    return action, None


def _resolve_action_name(tool_name: str, legal_actions: list[str | None]) -> str | None:
    allowed = [action for action in legal_actions if action]
    if tool_name in allowed:
        return tool_name
    normalized = _normalize_tool_name(tool_name)
    candidates = [action for action in allowed if _normalize_tool_name(action) == normalized]
    if len(candidates) == 1:
        return candidates[0]
    return None


def _normalize_tool_name(value: str) -> str:
    return value.strip().replace("-", "_").replace(" ", "_").lower()


def _normalize_kind(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    normalized = _normalize_tool_name(value)
    if normalized == "house":
        return "HOUSE"
    if normalized == "hotel":
        return "HOTEL"
    return value


def _normalize_space_key_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().replace(" ", "_").replace("-", "_").upper()
    return value


def _canonicalize_object_keys(
    args_payload: dict[str, Any],
    *,
    allowed_keys: set[str],
    context: str,
) -> tuple[dict[str, Any], list[str]]:
    by_normalized: dict[str, str] = {}
    for key in allowed_keys:
        normalized = _normalize_tool_name(key)
        existing = by_normalized.get(normalized)
        if existing is None:
            by_normalized[normalized] = key
        elif existing != key:
            return {}, [f"Non-unique key alias mapping in {context} for '{normalized}'"]

    mapped: dict[str, Any] = {}
    errors: list[str] = []
    for raw_key, value in args_payload.items():
        if not isinstance(raw_key, str):
            mapped[raw_key] = value
            continue
        canonical = by_normalized.get(_normalize_tool_name(raw_key))
        if canonical is None:
            mapped[raw_key] = value
            continue
        if canonical in mapped and mapped[canonical] != value:
            errors.append(f"Ambiguous key mapping for {context}.{canonical}")
            continue
        mapped[canonical] = value
    return mapped, errors


def _extract_message_fields(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    canonical, errors = _canonicalize_object_keys(
        payload,
        allowed_keys={"public_message", "private_thought"},
        context="args",
    )
    if errors:
        return {}, {}, errors
    action_args = dict(canonical)
    messages: dict[str, Any] = {}
    if "public_message" in action_args:
        messages["public_message"] = action_args.pop("public_message")
    if "private_thought" in action_args:
        messages["private_thought"] = action_args.pop("private_thought")
    return action_args, messages, []


def _canonicalize_trade_bundle(
    payload: Any,
    *,
    context: str,
) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    bundle, errors = _canonicalize_object_keys(
        payload,
        allowed_keys={"cash", "properties", "get_out_of_jail_cards"},
        context=context,
    )
    if errors:
        return None, errors
    properties = bundle.get("properties")
    if isinstance(properties, list):
        bundle["properties"] = [_normalize_space_key_value(item) if isinstance(item, str) else item for item in properties]
    return bundle, []


def _canonicalize_plan_entries(
    entries: Any,
    *,
    context: str,
) -> tuple[Any, list[str]]:
    if not isinstance(entries, list):
        return entries, []
    normalized_entries: list[Any] = []
    errors: list[str] = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            normalized_entries.append(item)
            continue
        normalized_item, item_errors = _canonicalize_object_keys(
            item,
            allowed_keys={"space_key", "kind", "count"},
            context=f"{context}[{index}]",
        )
        if item_errors:
            errors.extend(item_errors)
            continue
        if "space_key" in normalized_item:
            normalized_item["space_key"] = _normalize_space_key_value(normalized_item["space_key"])
        if "kind" in normalized_item:
            normalized_item["kind"] = _normalize_kind(normalized_item["kind"])
        normalized_entries.append(normalized_item)
    if errors:
        return None, errors
    return normalized_entries, []


def _canonicalize_action_args(
    action_name: str,
    args_payload: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(args_payload, dict):
        return {}, []
    if action_name in {
        "ROLL_DICE",
        "buy_property",
        "start_auction",
        "drop_out",
        "accept_trade",
        "reject_trade",
        "pay_jail_fine",
        "use_get_out_of_jail_card",
        "roll_for_doubles",
        "end_turn",
        "declare_bankruptcy",
    }:
        return {}, []
    if action_name == "bid_auction":
        return _canonicalize_object_keys(args_payload, allowed_keys={"bid_amount"}, context=action_name)
    if action_name in {"mortgage_property", "unmortgage_property"}:
        args, errors = _canonicalize_object_keys(args_payload, allowed_keys={"space_key"}, context=action_name)
        if errors:
            return {}, errors
        if "space_key" in args:
            args["space_key"] = _normalize_space_key_value(args["space_key"])
        return args, []
    if action_name in {"build_houses_or_hotel", "sell_houses_or_hotel"}:
        plan_key = "build_plan" if action_name == "build_houses_or_hotel" else "sell_plan"
        args, errors = _canonicalize_object_keys(args_payload, allowed_keys={plan_key}, context=action_name)
        if errors:
            return {}, errors
        if plan_key in args:
            normalized_entries, entry_errors = _canonicalize_plan_entries(args.get(plan_key), context=f"{action_name}.{plan_key}")
            if entry_errors:
                return {}, entry_errors
            args[plan_key] = normalized_entries
        return args, []
    if action_name in {"propose_trade", "counter_trade"}:
        top_level = {"offer", "request"}
        if action_name == "propose_trade":
            top_level.add("to_player_id")
        args, errors = _canonicalize_object_keys(args_payload, allowed_keys=top_level, context=action_name)
        if errors:
            return {}, errors
        if "offer" in args:
            offer, offer_errors = _canonicalize_trade_bundle(args.get("offer"), context=f"{action_name}.offer")
            if offer_errors:
                return {}, offer_errors
            args["offer"] = offer
        if "request" in args:
            request, request_errors = _canonicalize_trade_bundle(args.get("request"), context=f"{action_name}.request")
            if request_errors:
                return {}, request_errors
            args["request"] = request
        return args, []
    if action_name == "NOOP":
        return _canonicalize_object_keys(args_payload, allowed_keys={"reason"}, context=action_name)
    return dict(args_payload), []


def validate_decision_action(decision: dict[str, Any], action: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema_ok, schema_errors = validate_action_payload(action)
    if not schema_ok:
        errors.extend(schema_errors)
    legal_actions = decision.get("legal_actions", [])
    allowed = {entry.get("action") for entry in legal_actions}
    if action.get("action") not in allowed:
        errors.append("Action not in legal_actions")
    public_message = action.get("public_message")
    if not isinstance(public_message, str):
        errors.append("Missing required public_message")
    private_thought = action.get("private_thought")
    if not isinstance(private_thought, str):
        errors.append("Missing required private_thought")
    return errors
