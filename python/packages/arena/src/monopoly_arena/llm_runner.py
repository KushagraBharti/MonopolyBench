from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, AsyncIterable, Awaitable, Callable

from monopoly_engine import Engine
from monopoly_engine.board import normalize_space_key
from monopoly_telemetry import (
    RunFiles,
    build_summary,
    write_experiment_review_artifacts,
    write_scorecard_artifacts,
    write_trace_failure_artifacts,
    write_usage_artifacts,
)

from .openrouter_client import OpenRouterClient, OpenRouterResult

from .action_validation import validate_action_payload
from .baselines import choose_baseline_action
from .decision_resolver import DecisionResolutionAttempt, DecisionResolutionOutcome, SharedDecisionResolver
from .player_config import EXPECTED_PLAYER_COUNT, PlayerConfig
from .prompting import (
    PromptBundle,
    PromptMemory,
    build_space_key_by_index,
)
from .replay_verification import write_replay_verification_artifacts


DecisionCallback = Callable[[dict[str, Any]], Awaitable[None]]


DecisionAttempt = DecisionResolutionAttempt
DecisionOutcome = DecisionResolutionOutcome


@dataclass(slots=True)
class PendingResolution:
    decision: dict[str, Any]
    outcome: DecisionOutcome


class LlmRunner:
    def __init__(
        self,
        *,
        seed: int,
        players: list[PlayerConfig],
        run_id: str,
        openrouter: OpenRouterClient,
        run_files: RunFiles | None = None,
        max_turns: int = 200,
        event_delay_s: float = 0.25,
        start_ts_ms: int = 0,
        ts_step_ms: int = 250,
        max_trade_exchanges: int = 20,
        max_auction_actions: int = 200,
        seat_assignment_metadata: dict[str, Any] | None = None,
        baseline_strategies: dict[str, str] | None = None,
    ) -> None:
        self.run_id = run_id
        if len(players) != EXPECTED_PLAYER_COUNT:
            raise ValueError(f"Exactly {EXPECTED_PLAYER_COUNT} players are required for LLM runs.")
        self._seed = seed
        self._players = list(players)
        self._max_turns = max_turns
        self._start_ts_ms = start_ts_ms
        self._ts_step_ms = ts_step_ms
        self._player_configs = {player.player_id: player for player in players}
        self._baseline_strategies = dict(baseline_strategies or {})
        unknown_baseline_players = set(self._baseline_strategies) - set(self._player_configs)
        if unknown_baseline_players:
            raise ValueError(f"Baseline strategies reference unknown players: {sorted(unknown_baseline_players)}")
        self._openrouter = openrouter
        self._run_files = run_files
        self._engine = Engine(
            seed=seed,
            players=[{"player_id": p.player_id, "name": p.name} for p in players],
            run_id=run_id,
            max_turns=max_turns,
            start_ts_ms=start_ts_ms,
            ts_step_ms=ts_step_ms,
            max_trade_exchanges=max_trade_exchanges,
            max_auction_actions=max_auction_actions,
        )
        self._event_delay_s = event_delay_s
        self._max_trade_exchanges = max_trade_exchanges
        self._max_auction_actions = max_auction_actions
        self._seat_assignment_metadata = seat_assignment_metadata or {}
        self._space_key_by_index = build_space_key_by_index()
        self._prompt_memory = PromptMemory(space_key_by_index=self._space_key_by_index)
        self._decision_resolver = SharedDecisionResolver(
            openrouter=self._openrouter,
            run_files=self._run_files,
            prompt_memory=self._prompt_memory,
            space_key_by_index=self._space_key_by_index,
            rules_validator=self._rules_validator,
        )
        self._paused = False
        self._resume_event = asyncio.Event()
        self._resume_event.set()
        self._pending_resolution: PendingResolution | None = None
        self._advance_lock = asyncio.Lock()
        self._applied_decision_ids: set[str] = set()
        self._write_static_run_artifacts()

    def request_stop(self, reason: str = "STOPPED") -> None:
        self._engine.request_stop(reason)
        self.resume()

    def pause(self) -> None:
        self._paused = True
        self._resume_event.clear()

    def resume(self) -> None:
        self._paused = False
        self._resume_event.set()

    def is_paused(self) -> bool:
        return self._paused

    def has_pending_resolution(self) -> bool:
        return self._pending_resolution is not None

    def get_snapshot(self) -> dict[str, Any]:
        return self._engine.get_snapshot()

    async def run(
        self,
        on_event: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
        on_snapshot: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
        on_summary: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
        on_decision: DecisionCallback | None = None,
    ) -> None:
        event_handler = on_event
        snapshot_handler = on_snapshot
        summary_handler = on_summary
        if self._run_files is not None:
            run_files = self._run_files
            if event_handler is None:
                async def _write_event(event: dict[str, Any]) -> None:
                    run_files.write_event(event)

                event_handler = _write_event
            if snapshot_handler is None:
                async def _write_snapshot(snapshot: dict[str, Any]) -> None:
                    run_files.write_snapshot(snapshot)

                snapshot_handler = _write_snapshot
            if summary_handler is None:
                async def _write_summary(summary: dict[str, Any]) -> None:
                    run_files.write_summary(summary)

                summary_handler = _write_summary
        try:
            async for event in self._event_stream(on_decision=on_decision):
                if event_handler is not None:
                    await event_handler(event)
                if snapshot_handler is not None and event["type"] in {
                    "LLM_DECISION_REQUESTED",
                    "TURN_ENDED",
                    "GAME_ENDED",
                }:
                    await snapshot_handler(self.get_snapshot())
            if self._event_delay_s > 0:
                await asyncio.sleep(self._event_delay_s)
            if summary_handler is not None:
                summary: dict[str, Any]
                if self._run_files is not None:
                    summary = build_summary(self._run_files)
                else:
                    summary = self._engine.build_summary()
                summary["run_config"] = {
                    "seed": self._seed,
                    "max_turns": self._max_turns,
                    "start_ts_ms": self._start_ts_ms,
                    "ts_step_ms": self._ts_step_ms,
                    "max_trade_exchanges": self._max_trade_exchanges,
                    "max_auction_actions": self._max_auction_actions,
                }
                await summary_handler(summary)
                if self._run_files is not None:
                    write_usage_artifacts(self._run_files)
                    await self._write_pricing_snapshot_artifact()
                    write_experiment_review_artifacts(
                        self._run_files,
                        benchmark_tracks=["long_horizon_game"],
                        models=[player.to_status() for player in self._players],
                        reasoning_policy=self._common_reasoning_policy(),
                        batch_type="full_game_single",
                    )
                    write_scorecard_artifacts(self._run_files)
                    write_replay_verification_artifacts(self._run_files)
                    write_trace_failure_artifacts(self._run_files)
                    self._run_files.write_artifact_manifest()
        finally:
            await self._close_openrouter()

    def _common_reasoning_policy(self) -> dict[str, Any] | None:
        policies = [player.reasoning for player in self._players]
        if not policies:
            return None
        first = policies[0]
        return first if all(policy == first for policy in policies) else None

    async def _write_pricing_snapshot_artifact(self) -> None:
        if self._run_files is None:
            return
        method = getattr(self._openrouter, "get_models", None)
        payload: dict[str, Any]
        if method is None:
            payload = {
                "schema_version": "v1",
                "source": "openrouter_get_models",
                "status": "unavailable",
                "reason": "client_has_no_get_models",
            }
        else:
            result = await method()
            payload = {
                "schema_version": "v1",
                "source": "openrouter_get_models",
                "status": "ok" if getattr(result, "ok", False) else "error",
                "status_code": getattr(result, "status_code", None),
                "request_id": getattr(result, "request_id", None),
                "error": getattr(result, "error", None),
                "error_type": getattr(result, "error_type", None),
                "data": getattr(result, "response_json", None),
            }
        self._run_files.write_json_artifact(self._run_files.pricing_snapshot_path, payload)

    async def _event_stream(
        self,
        on_decision: DecisionCallback | None = None,
    ) -> AsyncIterable[dict[str, Any]]:
        async def write_decision(entry: dict[str, Any]) -> None:
            if on_decision is not None:
                await on_decision(entry)
            elif self._run_files is not None:
                self._run_files.write_decision(entry)

        while True:
            await self._await_resume()
            async with self._advance_lock:
                _, events, decision, _ = self._engine.advance_until_decision(max_steps=1)
            if not events and decision is None:
                break
            for event in events:
                await self._await_resume()
                self._prompt_memory.update(event)
                yield event
            if decision is not None:
                await self._await_resume()
                outcome = await self._resolve_decision(decision, write_decision)
                self._pending_resolution = PendingResolution(decision=decision, outcome=outcome)
                await self._await_resume()
                pending = self._pending_resolution
                self._pending_resolution = None
                if pending is None:
                    continue
                decision = pending.decision
                outcome = self._validate_outcome_after_pause(decision, pending.outcome)
                async with self._advance_lock:
                    decision_id = decision["decision_id"]
                    if decision_id in self._applied_decision_ids:
                        raise RuntimeError(f"Decision {decision_id} already applied.")
                    _, action_events, _, _ = self._engine.apply_action(
                        outcome.action,
                        decision_meta=outcome.decision_meta,
                    )
                    self._applied_decision_ids.add(decision_id)
                if self._run_files is not None:
                    self._run_files.write_action(
                        {
                            "decision_id": decision["decision_id"],
                            "actor_player_id": decision["player_id"],
                            "decision_type": decision["decision_type"],
                            "turn_index": decision["turn_index"],
                            "action": outcome.action,
                            "decision_meta": outcome.decision_meta,
                        }
                    )
                player_config = self._player_configs[decision["player_id"]]
                resolved_entry = self._build_decision_log_entry(
                    decision=decision,
                    player_config=player_config,
                    phase="decision_resolved",
                    action=outcome.action,
                    attempts=outcome.attempts,
                    retry_used=outcome.retry_used,
                    fallback_used=outcome.fallback_used,
                    fallback_reason=outcome.fallback_reason,
                    action_events=action_events,
                    applied=True,
                    sequence_meta=outcome.sequence_meta,
                    automated=outcome.automated,
                )
                await write_decision(resolved_entry)
                for event in action_events:
                    await self._await_resume()
                    self._prompt_memory.update(event)
                    yield event
                if self._engine.is_game_over():
                    break
                continue
            if self._engine.is_game_over():
                break

    async def _resolve_decision(
        self,
        decision: dict[str, Any],
        log_writer: DecisionCallback | None,
    ) -> DecisionOutcome:
        player_id = decision["player_id"]
        player_config = self._player_configs[player_id]
        baseline_id = self._baseline_strategies.get(player_id)
        if baseline_id is not None:
            sequence_meta = {
                "actor_type": "baseline",
                "baseline_id": baseline_id,
                "prompt_pipeline": {
                    "status": "unchanged",
                    "note": "Baseline actor selected from legal actions without prompt construction or OpenRouter.",
                },
            }
            if log_writer is not None:
                await log_writer(
                    self._build_decision_log_entry(
                        decision=decision,
                        player_config=player_config,
                        phase="decision_started",
                        action=None,
                        attempts=[],
                        retry_used=False,
                        fallback_used=False,
                        fallback_reason=None,
                        request_start_ms=None,
                        prompt_messages=[],
                        prompt_payload=None,
                        prompt_payload_raw=None,
                        sequence_meta=sequence_meta,
                        automated=True,
                    )
                )
            action = choose_baseline_action(
                decision,
                baseline_id,
                seed_material={
                    "run_id": self.run_id,
                    "seed": self._seed,
                    "turn_index": decision.get("turn_index"),
                    "player_id": player_id,
                },
            )
            return self._build_decision_outcome(
                decision=decision,
                action=action,
                attempts=[],
                retry_used=False,
                fallback_used=False,
                fallback_reason=None,
                sequence_meta=sequence_meta,
                automated=True,
            )
        return await self._decision_resolver.resolve_decision(
            decision=decision,
            player_config=player_config,
            log_writer=log_writer,
        )

    def _rules_validator(self, decision: dict[str, Any], action: dict[str, Any]) -> list[str]:
        return self._engine.validate_action_for_decision(action, decision)

    def _write_static_run_artifacts(self) -> None:
        if self._run_files is None:
            return
        players_payload = _players_payload(self._players)
        seat_assignment = _seat_assignment_payload(
            run_id=self.run_id,
            players=self._players,
            mode=str(self._seat_assignment_metadata.get("permutation_mode") or "configured_order"),
            permutation_id=self._seat_assignment_metadata.get("permutation_id"),
            permutation_seed_material=self._seat_assignment_metadata.get("permutation_seed_material"),
            batch_id=self._seat_assignment_metadata.get("batch_id"),
            batch_run_index=self._seat_assignment_metadata.get("batch_run_index"),
        )
        run_config = {
            "schema_version": "v1",
            "run_config_version": "run_config_v1",
            "run_id": self.run_id,
            "mode": "full_game",
            "seed": self._seed,
            "max_turns": self._max_turns,
            "start_ts_ms": self._start_ts_ms,
            "ts_step_ms": self._ts_step_ms,
            "max_trade_exchanges": self._max_trade_exchanges,
            "max_auction_actions": self._max_auction_actions,
            "engine": {
                "deterministic_rng_seed": self._seed,
                "event_timestamps": {
                    "start_ts_ms": self._start_ts_ms,
                    "ts_step_ms": self._ts_step_ms,
                },
            },
            "players": players_payload["players"],
            "seat_assignment": seat_assignment["assignments"],
            "baseline_strategies": self._baseline_strategies,
            "replay": {
                "enabled_by_default": True,
                "source_actions": "actions.jsonl",
                "canonical_events": "events.jsonl",
            },
            "prompt_pipeline": {
                "status": "unchanged",
                "note": "Run metadata only; no prompt-building fields are modified here.",
            },
        }
        self._run_files.write_run_config(run_config)
        self._run_files.write_players(players_payload)
        self._run_files.write_seat_assignment(seat_assignment)

    def _attempt_from_response(
        self,
        prompt: PromptBundle,
        result: OpenRouterResult,
        request_start_ms: int | None,
        response_end_ms: int | None,
        *,
        include_prompt: bool,
    ) -> DecisionAttempt:
        response_json = result.response_json if result.ok else None
        assistant_content = None
        tool_calls = None
        errors: list[str] = []
        if response_json is None:
            errors.append(result.error or "OpenRouter error")
        else:
            assistant_content = (
                response_json.get("choices", [{}])[0].get("message", {}).get("content")
            )
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
        return DecisionAttempt(
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
        attempt: DecisionAttempt,
    ) -> tuple[dict[str, Any] | None, list[str], str | None, dict[str, Any] | None]:
        return self._decision_resolver._build_action_from_attempt(  # noqa: SLF001
            decision,
            attempt,
            check_rules=False,
        )

    def _build_decision_outcome(
        self,
        *,
        decision: dict[str, Any],
        action: dict[str, Any],
        attempts: list[DecisionAttempt],
        retry_used: bool,
        fallback_used: bool,
        fallback_reason: str | None,
        sequence_meta: dict[str, Any] | None = None,
        automated: bool = False,
    ) -> DecisionOutcome:
        decision_meta: dict[str, Any] = {"valid": True, "error": None}
        if fallback_used:
            decision_meta = {
                "valid": False,
                "error": f"fallback:{fallback_reason or 'unknown'}",
            }
        return DecisionOutcome(
            action=action,
            decision_meta=decision_meta,
            attempts=attempts,
            retry_used=retry_used,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            sequence_meta=sequence_meta,
            automated=automated,
        )

    def _validate_outcome_after_pause(
        self,
        decision: dict[str, Any],
        outcome: DecisionOutcome,
    ) -> DecisionOutcome:
        return self._decision_resolver.ensure_valid_outcome(decision=decision, outcome=outcome)

    def _build_decision_log_entry(
        self,
        *,
        decision: dict[str, Any],
        player_config: PlayerConfig,
        phase: str,
        action: dict[str, Any] | None,
        attempts: list[DecisionAttempt],
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
        return self._decision_resolver.build_decision_log_entry(
            decision=decision,
            player_config=player_config,
            phase=phase,
            action=action,
            attempts=attempts,
            retry_used=retry_used,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            request_start_ms=request_start_ms,
            prompt_messages=prompt_messages,
            prompt_payload=prompt_payload,
            prompt_payload_raw=prompt_payload_raw,
            action_events=action_events,
            applied=applied,
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
            return with_messages({
                "schema_version": "v1",
                "decision_id": decision_id,
                "action": action_name,
                "args": auction_args,
            })
        if decision.get("decision_type") == "TRADE_RESPONSE_DECISION":
            if "reject_trade" in legal_actions:
                return with_messages({
                    "schema_version": "v1",
                    "decision_id": decision_id,
                    "action": "reject_trade",
                    "args": {},
                })
            if "accept_trade" in legal_actions:
                return with_messages({
                    "schema_version": "v1",
                    "decision_id": decision_id,
                    "action": "accept_trade",
                    "args": {},
                })
            if "counter_trade" in legal_actions:
                return with_messages({
                    "schema_version": "v1",
                    "decision_id": decision_id,
                    "action": "counter_trade",
                    "args": {
                        "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                        "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                    },
                })
        if decision.get("decision_type") == "TRADE_PROPOSE_DECISION":
            if "propose_trade" in legal_actions:
                players = decision.get("state", {}).get("players", [])
                actor_id = decision.get("player_id")
                target_id = None
                for entry in players:
                    if entry.get("player_id") != actor_id and not entry.get("bankrupt"):
                        target_id = entry.get("player_id")
                        break
                if target_id:
                    return with_messages({
                        "schema_version": "v1",
                        "decision_id": decision_id,
                        "action": "propose_trade",
                        "args": {
                            "to_player_id": target_id,
                            "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                            "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                        },
                    })

        def build_plan_args(indices: list[int] | None) -> dict[str, Any] | None:
            if not indices:
                return None
            space_key = first_space_key(indices)
            if space_key is None:
                return None
            board = decision.get("state", {}).get("board", [])
            matching: dict[str, Any] = next(
                (space for space in board if space.get("index") == indices[0]),
                {},
            )
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
            matching: dict[str, Any] = next(
                (space for space in board if space.get("index") == indices[0]),
                {},
            )
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
                post_options.get("mortgageable_space_indices")
                or liq_options.get("mortgageable_space_indices")
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
        return with_messages({
            "schema_version": "v1",
            "decision_id": decision_id,
            "action": action_name,
            "args": args,
        })

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
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
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

    async def _close_openrouter(self) -> None:
        close = getattr(self._openrouter, "aclose", None)
        if close is None:
            return
        result = close()
        if asyncio.iscoroutine(result):
            await result

    async def _await_resume(self) -> None:
        if self._resume_event.is_set():
            return
        await self._resume_event.wait()


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
            parsed_calls.append(
                {
                    "name": name,
                    "arguments": func.get("arguments"),
                }
            )
        return parsed_calls, None
    function_call = message.get("function_call")
    if function_call:
        name = function_call.get("name")
        if not isinstance(name, str) or not name.strip():
            return None, "function_call missing name"
        return [
            {
                "name": name,
                "arguments": function_call.get("arguments"),
            }
        ], None
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
        return normalize_space_key(value)
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
        bundle["properties"] = [
            _normalize_space_key_value(item) if isinstance(item, str) else item for item in properties
        ]
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

    # Zero-arg actions ignore extra fields after message extraction.
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
        args, errors = _canonicalize_object_keys(
            args_payload,
            allowed_keys={"bid_amount"},
            context=action_name,
        )
        return args, errors

    if action_name in {"mortgage_property", "unmortgage_property"}:
        args, errors = _canonicalize_object_keys(
            args_payload,
            allowed_keys={"space_key"},
            context=action_name,
        )
        if errors:
            return {}, errors
        if "space_key" in args:
            args["space_key"] = _normalize_space_key_value(args["space_key"])
        return args, []

    if action_name in {"build_houses_or_hotel", "sell_houses_or_hotel"}:
        plan_key = "build_plan" if action_name == "build_houses_or_hotel" else "sell_plan"
        args, errors = _canonicalize_object_keys(
            args_payload,
            allowed_keys={plan_key},
            context=action_name,
        )
        if errors:
            return {}, errors
        if plan_key in args:
            normalized_entries, entry_errors = _canonicalize_plan_entries(
                args.get(plan_key),
                context=f"{action_name}.{plan_key}",
            )
            if entry_errors:
                return {}, entry_errors
            args[plan_key] = normalized_entries
        return args, []

    if action_name in {"propose_trade", "counter_trade"}:
        top_level = {"offer", "request"}
        if action_name == "propose_trade":
            top_level.add("to_player_id")
        args, errors = _canonicalize_object_keys(
            args_payload,
            allowed_keys=top_level,
            context=action_name,
        )
        if errors:
            return {}, errors
        if "offer" in args:
            offer, offer_errors = _canonicalize_trade_bundle(args.get("offer"), context=f"{action_name}.offer")
            if offer_errors:
                return {}, offer_errors
            args["offer"] = offer
        if "request" in args:
            request, request_errors = _canonicalize_trade_bundle(
                args.get("request"),
                context=f"{action_name}.request",
            )
            if request_errors:
                return {}, request_errors
            args["request"] = request
        return args, []

    if action_name == "NOOP":
        args, errors = _canonicalize_object_keys(
            args_payload,
            allowed_keys={"reason"},
            context=action_name,
        )
        return args, errors

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


def _players_payload(players: list[PlayerConfig]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "players_version": "players_v1",
        "players": [
            {
                "player_id": player.player_id,
                "name": player.name,
                "openrouter_model_id": player.openrouter_model_id,
                "model_display_name": player.model_display_name,
                "reasoning": player.reasoning,
                "provider": player.provider,
                "system_prompt_logged": False,
            }
            for player in players
        ],
    }


def _seat_assignment_payload(
    *,
    run_id: str,
    players: list[PlayerConfig],
    mode: str,
    permutation_id: Any = None,
    permutation_seed_material: Any = None,
    batch_id: Any = None,
    batch_run_index: Any = None,
) -> dict[str, Any]:
    assignments = [
        {
            "player_id": player.player_id,
            "player_name": player.name,
            "openrouter_model_id": player.openrouter_model_id,
            "model_display_name": player.model_display_name,
            "seat_index": index,
            "turn_order": index,
        }
        for index, player in enumerate(players)
    ]
    digest_payload = {
        "assignments": assignments,
        "mode": mode,
        "permutation_id": permutation_id,
        "permutation_seed_material": permutation_seed_material,
    }
    digest_source = json.dumps(digest_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    payload: dict[str, Any] = {
        "schema_version": "v1",
        "seat_assignment_version": "seat_assignment_v1",
        "run_id": run_id,
        "permutation_mode": mode,
        "permutation_id": str(permutation_id or f"{mode}:0"),
        "permutation_seed_material": permutation_seed_material,
        "permutation_digest": hashlib.sha1(digest_source.encode("utf-8")).hexdigest(),
        "assignments": assignments,
    }
    if batch_id is not None:
        payload["batch_id"] = str(batch_id)
    if batch_run_index is not None:
        payload["batch_run_index"] = int(batch_run_index)
    return payload
