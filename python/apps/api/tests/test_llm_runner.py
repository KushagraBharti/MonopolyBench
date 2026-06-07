import asyncio
import json
from typing import Any, Callable

from monopoly_arena import OpenRouterResult
from monopoly_arena.prompting import (
    PromptMemory,
    build_compact_decision,
    build_openrouter_tools,
    build_prompt_bundle,
    build_space_key_by_index,
)
from monopoly_engine import Engine
from monopoly_telemetry import init_run_files

from monopoly_api.llm_runner import LlmRunner
from monopoly_api.player_config import PlayerConfig, derive_model_display_name, DEFAULT_SYSTEM_PROMPT


def _make_player(player_id: str, name: str) -> PlayerConfig:
    model_id = "openai/gpt-oss-120b"
    return PlayerConfig(
        player_id=player_id,
        name=name,
        openrouter_model_id=model_id,
        model_display_name=derive_model_display_name(model_id),
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        reasoning=None,
    )


def _make_players() -> list[PlayerConfig]:
    return [
        _make_player("p1", "P1"),
        _make_player("p2", "P2"),
        _make_player("p3", "P3"),
        _make_player("p4", "P4"),
    ]


def _event(
    event_type: str,
    payload: dict[str, Any],
    *,
    turn_index: int = 0,
    player_id: str | None = None,
) -> dict[str, Any]:
    return {
        "type": event_type,
        "turn_index": turn_index,
        "actor": {"kind": "PLAYER" if player_id else "ENGINE", "player_id": player_id},
        "payload": payload,
    }


def _tool_call_response(name: str, args: dict[str, Any]) -> OpenRouterResult:
    args = {
        **args,
        "public_message": args.get("public_message", ""),
        "private_thought": args.get("private_thought", "test"),
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
                                "name": name,
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


def _error_response(error_type: str, status_code: int | None = None) -> OpenRouterResult:
    return OpenRouterResult(
        ok=False,
        status_code=status_code,
        response_json=None,
        error="error",
        error_type=error_type,
        request_id="req-err",
    )


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
            game_state = payload.get("game_state", {})
            scenario = action_state.get("scenario", {}) if isinstance(action_state, dict) else {}
            stable_scenario = dict(scenario)
            stable_scenario.pop("notes", None)
            available_actions = (
                action_state.get("available_actions", []) if isinstance(action_state, dict) else []
            )
            tool_actions = [
                tool.get("function", {}).get("name")
                for tool in tools or []
                if tool.get("function", {}).get("name")
            ]
            legal_action_names = available_actions or tool_actions
            players = []
            if isinstance(game_state, dict):
                if isinstance(game_state.get("you"), dict):
                    players.append(game_state["you"])
                players.extend(player for player in game_state.get("others", []) if isinstance(player, dict))
            minimal_state = {
                "players": players,
                "auction": {
                    "current_high_bid": scenario.get("current_high_bid"),
                    "current_leader_player_id": scenario.get("current_leader_player_id"),
                    "active_bidders_player_ids": scenario.get("active_bidders_player_ids", []),
                    "history": scenario.get("history", []),
                },
            }
            normalized = dict(payload)
            normalized["decision"] = {
                "decision_id": json.dumps(
                    {
                        "turn_index": game_state.get("metadata", {}).get("turn_index")
                        if isinstance(game_state, dict)
                        else None,
                        "decision_type": action_state.get("decision_type") if isinstance(action_state, dict) else None,
                        "actor_player_id": action_state.get("actor_player_id") if isinstance(action_state, dict) else None,
                        "scenario": stable_scenario,
                    },
                    sort_keys=True,
                ),
                "decision_type": action_state.get("decision_type") if isinstance(action_state, dict) else None,
                "player_id": action_state.get("actor_player_id") if isinstance(action_state, dict) else None,
                "legal_actions": [{"action": action} for action in legal_action_names],
                "state": minimal_state,
            }
            normalized["decision_focus"] = action_state
            normalized["full_state"] = game_state
            return normalized
        if "decision" in payload and "full_state" in payload:
            return payload
    return None


class PolicyOpenRouter:
    def __init__(
        self,
        policy: Callable[[dict[str, Any], dict[str, Any]], tuple[str, dict[str, Any]]],
    ) -> None:
        self._policy = policy

    async def create_chat_completion(self, *, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, **_: Any) -> OpenRouterResult:
        payload = _extract_payload(messages, tools)
        if payload is None:
            return _tool_call_response("start_auction", {})
        tool_name, args = self._policy(payload["decision"], payload["decision_focus"])
        return _tool_call_response(tool_name, args)


class ErrorOpenRouter:
    def __init__(self, error_type: str, status_code: int | None = None) -> None:
        self._error_type = error_type
        self._status_code = status_code

    async def create_chat_completion(self, *_: Any, **__: Any) -> OpenRouterResult:
        return _error_response(self._error_type, self._status_code)


class ScriptedOpenRouter:
    def __init__(self) -> None:
        self._decision_index: dict[str, int] = {}
        self._decision_attempts: dict[str, int] = {}

    async def create_chat_completion(self, *, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, **_: Any) -> OpenRouterResult:
        payload = _extract_payload(messages, tools)
        if payload is None:
            return _tool_call_response("start_auction", {})
        decision = payload["decision"]
        decision_focus = payload["decision_focus"]
        decision_id = decision["decision_id"]
        if decision.get("decision_type") != "BUY_OR_AUCTION_DECISION":
            tool_name, args = _choose_buy_if_legal(decision, decision_focus)
            return _tool_call_response(tool_name, args)
        if decision_id not in self._decision_index:
            self._decision_index[decision_id] = len(self._decision_index)
            self._decision_attempts[decision_id] = 0
        attempt = self._decision_attempts[decision_id]
        self._decision_attempts[decision_id] = attempt + 1

        decision_number = self._decision_index[decision_id]
        if decision_number == 0:
            tool_name, args = _choose_buy_if_legal(decision, decision_focus)
            return _tool_call_response(tool_name, args)
        if decision_number == 1:
            if attempt == 0:
                return _tool_call_response("buy_property_invalid", {})
            tool_name, args = _choose_buy_if_legal(decision, decision_focus)
            return _tool_call_response(tool_name, args)
        if decision_number == 2:
            return _tool_call_response("buy_property_invalid", {})
        tool_name, args = _choose_buy_if_legal(decision, decision_focus)
        return _tool_call_response(tool_name, args)


class CaptureOpenRouter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create_chat_completion(self, *, model: str, messages: list[dict[str, Any]], **kwargs: Any) -> OpenRouterResult:
        self.calls.append({"model": model, "messages": messages, "kwargs": kwargs})
        payload = _extract_payload(messages, kwargs.get("tools"))
        if payload is None:
            return _tool_call_response("start_auction", {})
        tool_name, args = _choose_buy_if_legal(payload["decision"], payload["decision_focus"])
        return _tool_call_response(tool_name, args)


class GenerationBackfillOpenRouter:
    def __init__(self) -> None:
        self.generation_ids: list[str] = []

    async def create_chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **_: Any,
    ) -> OpenRouterResult:
        payload = _extract_payload(messages, tools)
        if payload is None:
            return _tool_call_response("start_auction", {})
        tool_name, args = _choose_buy_if_legal(payload["decision"], payload["decision_focus"])
        return _tool_call_response(tool_name, args)

    async def get_generation(self, generation_id: str) -> OpenRouterResult:
        self.generation_ids.append(generation_id)
        return OpenRouterResult(
            ok=True,
            status_code=200,
            response_json={
                "data": {
                    "id": generation_id,
                    "total_cost": 0.0015,
                    "tokens_prompt": 10,
                    "tokens_completion": 25,
                    "native_tokens_prompt": 11,
                    "native_tokens_completion": 26,
                    "native_tokens_reasoning": 5,
                    "native_tokens_cached": 3,
                    "finish_reason": "stop",
                    "provider_name": "TestProvider",
                }
            },
            error=None,
            error_type=None,
            request_id="generation-req-1",
        )


def _choose_buy_if_legal(
    decision: dict[str, Any],
    decision_focus: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    legal = {entry.get("action") for entry in decision.get("legal_actions", [])}
    decision_type = decision.get("decision_type")
    if decision_type == "AUCTION_BID_DECISION":
        auction = decision.get("state", {}).get("auction", {})
        current_high_bid = int(auction.get("current_high_bid", 0) or 0)
        min_next_bid = current_high_bid + 1
        player_cash = None
        for player in decision.get("state", {}).get("players", []):
            if player.get("player_id") == decision.get("player_id"):
                player_cash = int(player.get("cash", 0))
                break
        if "bid_auction" in legal and player_cash is not None and player_cash >= min_next_bid:
            return "bid_auction", {"bid_amount": min_next_bid}
        if "drop_out" in legal:
            return "drop_out", {}
    if decision_type == "TRADE_RESPONSE_DECISION":
        if "reject_trade" in legal:
            return "reject_trade", {}
        if "accept_trade" in legal:
            return "accept_trade", {}
        if "counter_trade" in legal:
            return "counter_trade", {
                "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
            }
    if decision_type == "TRADE_PROPOSE_DECISION":
        if "propose_trade" in legal:
            players = decision.get("state", {}).get("players", [])
            actor_id = decision.get("player_id")
            target_id = next(
                (
                    entry.get("player_id")
                    for entry in players
                    if entry.get("player_id") != actor_id and not entry.get("bankrupt")
                ),
                None,
            )
            if target_id:
                return "propose_trade", {
                    "to_player_id": target_id,
                    "offer": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                    "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
                }
    if decision_type == "POST_TURN_ACTION_DECISION":
        if "end_turn" in legal:
            return "end_turn", {}
    if decision_type == "LIQUIDATION_DECISION":
        if "declare_bankruptcy" in legal:
            return "declare_bankruptcy", {}
        options = decision_focus.get("scenario", {}).get("options", {})
        mortgageable = options.get("mortgageable_space_keys", [])
        if "mortgage_property" in legal and mortgageable:
            return "mortgage_property", {"space_key": mortgageable[0]}
        sellable = options.get("sellable_building_space_keys", [])
        if "sell_houses_or_hotel" in legal and sellable:
            return "sell_houses_or_hotel", {
                "sell_plan": [{"space_key": sellable[0], "kind": "HOUSE", "count": 1}]
            }
    if "buy_property" in legal:
        return "buy_property", {}
    return "start_auction", {}


def test_retry_then_valid_action(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-retry")
    call_state = {"count": 0}

    def policy(decision: dict[str, Any], decision_focus: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if decision.get("decision_type") == "BUY_OR_AUCTION_DECISION":
            call_state["count"] += 1
            if call_state["count"] == 1:
                return "buy_property_invalid", {}
        return _choose_buy_if_legal(decision, decision_focus)

    fake = PolicyOpenRouter(policy)
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-retry",
        openrouter=fake,
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )
    events: list[dict[str, Any]] = []

    async def on_event(event: dict[str, Any]) -> None:
        events.append(event)

    asyncio.run(runner.run(on_event=on_event))

    decisions_path = run_files.decisions_path
    lines = decisions_path.read_text(encoding="utf-8").strip().splitlines()
    assert lines
    entries = [json.loads(line) for line in lines if line.strip()]
    decision_id = entries[0]["decision_id"]
    decision_entries = [entry for entry in entries if entry["decision_id"] == decision_id]
    started = next(entry for entry in decision_entries if entry["phase"] == "decision_started")
    resolved = next(entry for entry in decision_entries if entry["phase"] == "decision_resolved")
    assert started["request_start_ms"] is not None
    assert resolved["retry_used"] is True
    assert resolved["fallback_used"] is False
    assert len(resolved["attempts"]) == 2
    assert resolved["request_start_ms"] is not None
    assert resolved["response_end_ms"] is not None
    assert resolved["latency_ms"] is not None
    assert resolved["applied"] is True
    assert "LLM_DECISION_RESPONSE" in resolved["emitted_event_types"]
    assert resolved["emitted_event_seq_start"] <= resolved["emitted_event_seq_end"]

    response_events = [event for event in events if event["type"] == "LLM_DECISION_RESPONSE"]
    assert response_events
    assert response_events[0]["payload"]["valid"] is True


def test_static_run_artifacts_are_written_without_system_prompt_text(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-static-artifacts")
    LlmRunner(
        seed=321,
        players=players,
        run_id="run-static-artifacts",
        openrouter=PolicyOpenRouter(_choose_buy_if_legal),
        run_files=run_files,
        event_delay_s=0,
        max_turns=7,
        start_ts_ms=0,
        ts_step_ms=5,
        max_trade_exchanges=3,
        max_auction_actions=9,
    )

    run_config = json.loads(run_files.run_config_path.read_text(encoding="utf-8"))
    players_payload = json.loads(run_files.players_path.read_text(encoding="utf-8"))
    seat_assignment = json.loads(run_files.seat_assignment_path.read_text(encoding="utf-8"))
    serialized = json.dumps(
        {"run_config": run_config, "players": players_payload, "seat_assignment": seat_assignment},
        sort_keys=True,
    )

    assert run_config["seed"] == 321
    assert run_config["max_turns"] == 7
    assert run_config["ts_step_ms"] == 5
    assert run_config["max_trade_exchanges"] == 3
    assert run_config["max_auction_actions"] == 9
    assert run_config["prompt_pipeline"]["status"] == "unchanged"
    assert players_payload["players"][0]["player_id"] == "p1"
    assert players_payload["players"][0]["system_prompt_logged"] is False
    assert seat_assignment["assignments"][0]["seat_index"] == 0
    assert seat_assignment["assignments"][0]["turn_order"] == 0
    assert "You are an autonomous player" not in serialized


def test_generation_endpoint_backfills_usage_artifacts(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-generation-backfill")
    fake = GenerationBackfillOpenRouter()
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-generation-backfill",
        openrouter=fake,
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )

    asyncio.run(runner.run())

    assert fake.generation_ids
    attempt_rows = [
        json.loads(line)
        for line in run_files.usage_attempts_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert attempt_rows
    first = attempt_rows[0]
    assert first["accounting_status"] == "actual_openrouter_usage"
    assert first["accounting_source"] == "chat_completion_usage_with_generation_backfill"
    assert first["prompt_tokens"] == 10
    assert first["completion_tokens"] == 25
    assert first["total_tokens"] == 35
    assert first["native_prompt_tokens"] == 11
    assert first["native_completion_tokens"] == 26
    assert first["native_total_tokens"] == 37
    assert first["reasoning_tokens"] == 5
    assert first["cached_tokens"] == 3
    assert first["cost"] == 0.0015
    cost_report = json.loads(run_files.cost_report_path.read_text(encoding="utf-8"))
    assert cost_report["total_actual_cost"] > 0


def test_invalid_twice_fallback(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-fallback")
    def policy(decision: dict[str, Any], decision_focus: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if decision.get("decision_type") == "BUY_OR_AUCTION_DECISION":
            return "buy_property_invalid", {}
        return _choose_buy_if_legal(decision, decision_focus)

    fake = PolicyOpenRouter(policy)
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-fallback",
        openrouter=fake,
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )
    events: list[dict[str, Any]] = []

    async def on_event(event: dict[str, Any]) -> None:
        events.append(event)

    asyncio.run(runner.run(on_event=on_event))

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    decision_id = entries[0]["decision_id"]
    resolved = next(entry for entry in entries if entry["decision_id"] == decision_id and entry["phase"] == "decision_resolved")
    assert resolved["retry_used"] is True
    assert resolved["fallback_used"] is True
    assert resolved["fallback_reason"] == "malformed_after_retry"
    assert resolved["applied"] is True
    assert resolved["attempts"][0]["outcome"] == "malformed"
    assert resolved["attempts"][1]["outcome"] == "malformed"
    assert "LLM_DECISION_RESPONSE" in resolved["emitted_event_types"]

    response_events = [event for event in events if event["type"] == "LLM_DECISION_RESPONSE"]
    assert response_events
    assert response_events[0]["payload"]["valid"] is False
    assert response_events[0]["payload"]["error"].startswith("fallback:")


def test_illogical_then_valid_action_is_retried(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-illogical-retry")
    auction_attempts = {"count": 0}

    def policy(decision: dict[str, Any], decision_focus: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        decision_type = decision.get("decision_type")
        if decision_type == "BUY_OR_AUCTION_DECISION":
            return "start_auction", {}
        if decision_type == "AUCTION_BID_DECISION":
            auction_attempts["count"] += 1
            if auction_attempts["count"] == 1:
                return "bid_auction", {"bid_amount": 0}
            return "drop_out", {}
        return _choose_buy_if_legal(decision, decision_focus)

    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-illogical-retry",
        openrouter=PolicyOpenRouter(policy),
        run_files=run_files,
        event_delay_s=0,
        max_turns=4,
    )

    async def on_event(_event: dict[str, Any]) -> None:
        return None

    asyncio.run(runner.run(on_event=on_event))

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    resolved = next(
        entry
        for entry in entries
        if entry["phase"] == "decision_resolved" and entry["decision_type"] == "AUCTION_BID_DECISION"
    )
    assert resolved["retry_used"] is True
    assert resolved["fallback_used"] is False
    assert resolved["attempts"][0]["outcome"] == "illogical"
    assert resolved["attempts"][0]["reason"] == "bid_below_minimum"
    assert resolved["attempts"][1]["outcome"] == "valid"
    retry_prompt = resolved["attempts"][1]["prompt_payload"]["action_state"]["scenario"]["notes"]
    assert any("Previous action was not legal in the current game state" in note for note in retry_prompt)


def test_prompt_payload_shape(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-prompt")
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-prompt",
        openrouter=PolicyOpenRouter(_choose_buy_if_legal),
        run_files=run_files,
        event_delay_s=0,
        max_turns=6,
    )
    asyncio.run(runner.run())

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    started = next(
        entry
        for entry in entries
        if entry["phase"] == "decision_started"
        and entry.get("decision_type") == "BUY_OR_AUCTION_DECISION"
    )
    payload = started["prompt_payload"]
    raw_payload = started["prompt_payload_raw"]
    assert payload is not None
    assert raw_payload is not None
    assert json.loads(raw_payload) == payload
    assert set(payload.keys()) <= {"game_state", "action_state", "llm"}
    assert {"game_state", "action_state"}.issubset(payload.keys())

    game_state = payload["game_state"]
    assert game_state["title"] == "game_state"
    assert "board" not in game_state
    assert "schema_version" not in game_state
    assert "run_id" not in game_state["metadata"]
    assert set(game_state["metadata"].keys()) == {"turn_index", "you_player_id"}
    assert "space_name" not in json.dumps(game_state)
    assert len(game_state["others"]) == 3
    assert isinstance(game_state["you"]["position"], str)
    assert isinstance(game_state["you"]["get_out_of_jail_cards"], int)
    assert "has_get_out_of_jail_card" not in game_state["you"]
    for player in [game_state["you"], *game_state["others"]]:
        assert isinstance(player["get_out_of_jail_cards"], int)
        assert "has_get_out_of_jail_card" not in player
        for holding in player["holdings"]["owned"]:
            assert "space_key" in holding
            assert "name" not in holding
    bank = game_state["bank"]
    assert {"houses_remaining", "hotels_remaining", "unowned_space_keys"} <= set(bank.keys())
    assert isinstance(bank["unowned_space_keys"], list)
    assert game_state["memory"].get("public_timeline_last_20") is not None

    action_state = payload["action_state"]
    assert action_state["title"] == "action_state"
    assert action_state["decision_type"] == "BUY_OR_AUCTION_DECISION"
    assert action_state["actor_player_id"] == "p1"
    assert "schema_version" not in action_state
    assert "decision" not in action_state
    assert "decision_focus" not in action_state
    assert "decision_id" not in action_state
    assert "jail_turns" not in json.dumps(action_state)
    scenario = action_state["scenario"]
    assert "landed_space" in scenario
    assert {"buy_property", "start_auction"}.intersection(action_state["available_actions"])


def test_prompt_memory_pairs_public_message_with_primary_action_only() -> None:
    memory = PromptMemory(space_key_by_index=build_space_key_by_index())
    memory.update(
        _event(
            "LLM_DECISION_RESPONSE",
            {
                "decision_id": "dec-1",
                "player_id": "p1",
                "action_name": "buy_property",
                "valid": True,
                "error": None,
            },
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "LLM_PUBLIC_MESSAGE",
            {"decision_id": "dec-1", "player_id": "p1", "message": "I want Reading Railroad."},
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "PROPERTY_PURCHASED",
            {"player_id": "p1", "space_index": 5, "price": 200},
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "CASH_CHANGED",
            {"player_id": "p1", "delta": -200, "reason": "buy_property"},
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "RENT_PAID",
            {"from_player_id": "p2", "to_player_id": "p1", "space_index": 5, "amount": 25},
            turn_index=1,
            player_id="p2",
        )
    )

    timeline = memory.snapshot_for_player("p1")["public_timeline_last_20"]
    assert timeline == [
        {
            "turn_index": 0,
            "player_id": "p1",
            "event_type": "PROPERTY_PURCHASED",
            "action": "bought READING_RAILROAD for $200",
            "message": "I want Reading Railroad.",
        },
        {
            "turn_index": 1,
            "player_id": "p2",
            "event_type": "RENT_PAID",
            "action": "paid $25 rent to p1 on READING_RAILROAD",
            "message": None,
        },
    ]


def test_prompt_memory_combines_build_plan_items_with_one_message() -> None:
    memory = PromptMemory(space_key_by_index=build_space_key_by_index())
    memory.update(
        _event(
            "LLM_DECISION_RESPONSE",
            {
                "decision_id": "dec-build",
                "player_id": "p1",
                "action_name": "build_houses_or_hotel",
                "valid": True,
                "error": None,
            },
            turn_index=5,
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "LLM_PUBLIC_MESSAGE",
            {"decision_id": "dec-build", "player_id": "p1", "message": "Brown rents are about to matter."},
            turn_index=5,
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "CASH_CHANGED",
            {"player_id": "p1", "delta": -100, "reason": "BUILD"},
            turn_index=5,
            player_id="p1",
        )
    )
    memory.update(
        _event("HOUSE_BUILT", {"player_id": "p1", "space_index": 1, "count": 1}, turn_index=5, player_id="p1")
    )
    memory.update(
        _event("HOUSE_BUILT", {"player_id": "p1", "space_index": 3, "count": 1}, turn_index=5, player_id="p1")
    )

    timeline = memory.snapshot_for_player("p1")["public_timeline_last_20"]
    assert timeline == [
        {
            "turn_index": 5,
            "player_id": "p1",
            "event_type": "BUILDINGS_BUILT",
            "action": "built 1 house on MEDITERRANEAN_AVENUE and built 1 house on BALTIC_AVENUE",
            "message": "Brown rents are about to matter.",
        }
    ]


def test_prompt_memory_keeps_substantive_end_turn_message() -> None:
    memory = PromptMemory(space_key_by_index=build_space_key_by_index())
    memory.update(
        _event(
            "LLM_DECISION_RESPONSE",
            {
                "decision_id": "dec-end",
                "player_id": "p1",
                "action_name": "end_turn",
                "valid": True,
                "error": None,
            },
            turn_index=2,
            player_id="p1",
        )
    )
    memory.update(
        _event(
            "LLM_PUBLIC_MESSAGE",
            {"decision_id": "dec-end", "player_id": "p1", "message": "Holding cash for now."},
            turn_index=2,
            player_id="p1",
        )
    )
    memory.update(_event("TURN_ENDED", {}, turn_index=2))

    assert memory.snapshot_for_player("p1")["public_timeline_last_20"] == [
        {
            "turn_index": 2,
            "player_id": "p1",
            "event_type": "TURN_ENDED",
            "action": "ended turn",
            "message": "Holding cash for now.",
        }
    ]


def test_jail_decision_focus_shape() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=9, players=players_state, run_id="run-jail-shape", max_turns=3, ts_step_ms=1)
    player = engine.state.players[0]
    engine.state.active_player_id = "p1"
    player.in_jail = True
    player.position = 10
    player.jail_turns = 0

    _, _, decision, _ = engine.advance_until_decision(max_steps=1)
    assert decision is not None
    assert decision["decision_type"] == "JAIL_DECISION"

    space_key_by_index = build_space_key_by_index()
    prompt = build_prompt_bundle(
        decision,
        _make_player("p1", "P1"),
        memory=PromptMemory(space_key_by_index=space_key_by_index),
        space_key_by_index=space_key_by_index,
    )
    focus = prompt.user_payload["action_state"]
    assert focus["decision_type"] == "JAIL_DECISION"
    assert "jail_turns" not in json.dumps(focus)
    options = focus["scenario"]["options"]
    assert isinstance(options["can_roll_for_doubles"], bool)
    assert "roll_for_doubles" in focus["available_actions"]


def test_post_turn_decision_focus_shape() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=19, players=players_state, run_id="run-post-turn", max_turns=3, ts_step_ms=1)
    player = engine.state.players[0]
    engine.state.active_player_id = "p1"
    engine.state.board[1].owner_id = "p1"
    engine.state.board[3].owner_id = "p1"
    engine.state.board[1].houses = 1
    engine.state.board[5].owner_id = "p1"
    engine.state.board[12].owner_id = "p1"
    engine.state.board[12].mortgaged = True

    decision = engine._build_post_turn_action_decision(player)
    space_key_by_index = build_space_key_by_index()
    prompt = build_prompt_bundle(
        decision,
        _make_player("p1", "P1"),
        memory=PromptMemory(space_key_by_index=space_key_by_index),
        space_key_by_index=space_key_by_index,
    )
    focus = prompt.user_payload["action_state"]

    assert focus["decision_type"] == "POST_TURN_ACTION_DECISION"
    assert "cash" not in json.dumps(focus)
    assert "position" not in json.dumps(focus)
    assert "jail_turns" not in json.dumps(focus)
    assert focus["scenario"]["note"].startswith("Choose exactly one post-turn action now.")
    options = focus["scenario"]["options"]
    assert isinstance(options["mortgageable_space_keys"], list)
    action_names = set(focus["available_actions"])
    assert "end_turn" in action_names
    assert "propose_trade" in action_names
    assert "build_houses_or_hotel" in action_names
    assert "sell_houses_or_hotel" in action_names
    assert "mortgage_property" in action_names
    assert "unmortgage_property" in action_names


def test_liquidation_decision_focus_shape() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=21, players=players_state, run_id="run-liquidation-shape", max_turns=3, ts_step_ms=1)
    player = engine.state.players[0]
    engine.state.active_player_id = "p1"
    player.cash = 90
    engine.state.board[1].owner_id = "p1"
    engine.state.board[3].owner_id = "p1"
    engine.state.board[1].houses = 1
    engine.state.board[5].owner_id = "p1"

    payment = engine._build_payment_entry(340, "p2", "RENT", kind="RENT", space_index=14)
    options = engine._compute_liquidation_options(player)
    decision = engine._build_liquidation_decision(player, payment, options=options)

    space_key_by_index = build_space_key_by_index()
    prompt = build_prompt_bundle(
        decision,
        _make_player("p1", "P1"),
        memory=PromptMemory(space_key_by_index=space_key_by_index),
        space_key_by_index=space_key_by_index,
    )
    focus = prompt.user_payload["action_state"]
    focus_without_note = json.loads(json.dumps(focus))
    focus_without_note["scenario"].pop("note", None)

    assert focus["decision_type"] == "LIQUIDATION_DECISION"
    assert "cash" not in json.dumps(focus_without_note)
    assert "position" not in json.dumps(focus_without_note)
    assert "jail_turns" not in json.dumps(focus_without_note)
    scenario = focus["scenario"]
    assert scenario["note"].startswith("Choose exactly one liquidation action now.")
    assert scenario["owed_amount"] == 340
    assert scenario["owed_to_player_id"] == "p2"
    assert scenario["shortfall"] == 250
    action_names = set(focus["available_actions"])
    assert "declare_bankruptcy" in action_names
    assert "mortgage_property" in action_names
    assert "sell_houses_or_hotel" in action_names


def test_auction_decision_focus_shape() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=11, players=players_state, run_id="run-auction-shape", max_turns=3, ts_step_ms=1)
    engine.state.players[0].position = 10
    engine.state.active_player_id = "p1"
    engine._rng.roll_dice = lambda: (1, 3)
    target_index = 14
    engine.state.board[target_index].owner_id = None

    _, _, decision, _ = engine.advance_until_decision(max_steps=1)
    assert decision is not None
    assert decision["decision_type"] == "BUY_OR_AUCTION_DECISION"

    action = {
        "schema_version": "v1",
        "decision_id": decision["decision_id"],
        "action": "start_auction",
        "args": {},
    }
    _, _, auction_decision, _ = engine.apply_action(action)
    assert auction_decision is not None
    assert auction_decision["decision_type"] == "AUCTION_BID_DECISION"

    space_key_by_index = build_space_key_by_index()
    prompt = build_prompt_bundle(
        auction_decision,
        _make_player("p2", "P2"),
        memory=PromptMemory(space_key_by_index=space_key_by_index),
        space_key_by_index=space_key_by_index,
    )
    focus = prompt.user_payload["action_state"]

    assert focus["decision_type"] == "AUCTION_BID_DECISION"
    assert "cash" not in json.dumps(focus)
    assert "position" not in json.dumps(focus)
    assert "space_index" not in json.dumps(focus)
    scenario = focus["scenario"]
    assert "property_space" in scenario
    assert "current_high_bid" in scenario
    assert "min_next_bid" in scenario
    action_names = set(focus["available_actions"])
    assert "bid_auction" in action_names
    assert "drop_out" in action_names


def test_auction_tool_schema_includes_bid_amount() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=15, players=players_state, run_id="run-auction-tools", max_turns=3, ts_step_ms=1)
    engine.state.players[0].position = 10
    engine.state.active_player_id = "p1"
    engine._rng.roll_dice = lambda: (1, 3)
    engine.state.board[14].owner_id = None

    _, _, decision, _ = engine.advance_until_decision(max_steps=1)
    assert decision is not None
    action = {
        "schema_version": "v1",
        "decision_id": decision["decision_id"],
        "action": "start_auction",
        "args": {},
    }
    _, _, auction_decision, _ = engine.apply_action(action)
    assert auction_decision is not None

    tools = build_openrouter_tools(build_compact_decision(auction_decision))

    bid_tool = next(tool for tool in tools if tool["function"]["name"] == "bid_auction")
    bid_params = bid_tool["function"]["parameters"]
    assert "bid_amount" in bid_params.get("properties", {})


def test_trade_response_decision_focus_shape() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=17, players=players_state, run_id="run-trade-shape", max_turns=3, ts_step_ms=1)
    engine.state.board[1].owner_id = "p1"
    engine.state.active_player_id = "p1"
    player = engine.state.players[0]
    decision = engine._build_post_turn_action_decision(player)
    engine.state.phase = "AWAITING_DECISION"
    engine._pending_decision = decision
    engine._pending_turn = {
        "player_id": "p1",
        "decision_type": "POST_TURN_ACTION_DECISION",
        "rolled_double": False,
    }
    action = {
        "schema_version": "v1",
        "decision_id": decision["decision_id"],
        "action": "propose_trade",
        "args": {
            "to_player_id": "p2",
            "offer": {"cash": 0, "properties": ["MEDITERRANEAN_AVENUE"], "get_out_of_jail_cards": 0},
            "request": {"cash": 0, "properties": [], "get_out_of_jail_cards": 0},
        },
    }
    _, _, trade_decision, _ = engine.apply_action(action)
    assert trade_decision is not None
    assert trade_decision["decision_type"] == "TRADE_RESPONSE_DECISION"

    space_key_by_index = build_space_key_by_index()
    prompt = build_prompt_bundle(
        trade_decision,
        _make_player("p2", "P2"),
        memory=PromptMemory(space_key_by_index=space_key_by_index),
        space_key_by_index=space_key_by_index,
    )
    focus = prompt.user_payload["action_state"]

    assert focus["decision_type"] == "TRADE_RESPONSE_DECISION"
    assert "position" not in json.dumps(focus)
    assert "jail_turns" not in json.dumps(focus)
    scenario = focus["scenario"]
    assert scenario["counterparty_player_id"] == "p1"
    assert scenario["max_exchanges"] == 20
    assert scenario["exchange_index"] == 0
    assert isinstance(scenario["history"], list)
    assert len(scenario["history"]) == 0
    assert scenario["current_offer"]["from_player_id"] == "p1"
    assert "to_player_id" not in scenario["current_offer"]
    assert scenario["current_offer"]["if_you_accept"]["you_give"] == {
        "cash": 0,
        "properties": [],
        "get_out_of_jail_cards": 0,
    }
    assert scenario["current_offer"]["if_you_accept"]["you_receive"] == {
        "cash": 0,
        "properties": ["MEDITERRANEAN_AVENUE"],
        "get_out_of_jail_cards": 0,
    }
    action_names = set(focus["available_actions"])
    assert "accept_trade" in action_names
    assert "reject_trade" in action_names
    assert "counter_trade" in action_names


def test_post_turn_tool_schema_includes_build_and_sell_plans() -> None:
    players_state = [
        {"player_id": "p1", "name": "P1"},
        {"player_id": "p2", "name": "P2"},
        {"player_id": "p3", "name": "P3"},
        {"player_id": "p4", "name": "P4"},
    ]
    engine = Engine(seed=29, players=players_state, run_id="run-post-turn-tools", max_turns=3, ts_step_ms=1)
    player = engine.state.players[0]
    engine.state.active_player_id = "p1"
    engine.state.board[1].owner_id = "p1"
    engine.state.board[3].owner_id = "p1"
    engine.state.board[1].houses = 1

    decision = engine._build_post_turn_action_decision(player)
    tools = build_openrouter_tools(build_compact_decision(decision))

    build_tool = next(tool for tool in tools if tool["function"]["name"] == "build_houses_or_hotel")
    build_params = build_tool["function"]["parameters"]
    assert "build_plan" in build_params.get("properties", {})

    sell_tool = next(tool for tool in tools if tool["function"]["name"] == "sell_houses_or_hotel")
    sell_params = sell_tool["function"]["parameters"]
    assert "sell_plan" in sell_params.get("properties", {})

def test_two_llms_deterministic_replay() -> None:
    players = _make_players()
    policy_client = PolicyOpenRouter(_choose_buy_if_legal)

    async def run_once() -> list[dict[str, Any]]:
        runner = LlmRunner(
            seed=2024,
            players=players,
            run_id="run-deterministic",
            openrouter=policy_client,
            event_delay_s=0,
            max_turns=20,
        )
        collected: list[dict[str, Any]] = []

        async def on_event(event: dict[str, Any]) -> None:
            collected.append(event)

        await runner.run(on_event=on_event)
        return collected

    events_a = asyncio.run(run_once())
    events_b = asyncio.run(run_once())
    assert events_a == events_b


def test_openrouter_http_429_fallback_reason(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-http-429")
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-http-429",
        openrouter=ErrorOpenRouter("http_429", 429),
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )
    events: list[dict[str, Any]] = []

    async def on_event(event: dict[str, Any]) -> None:
        events.append(event)

    asyncio.run(runner.run(on_event=on_event))

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    resolved = next(entry for entry in entries if entry["phase"] == "decision_resolved")
    assert resolved["fallback_reason"] == "openrouter_http_429"

    response_events = [event for event in events if event["type"] == "LLM_DECISION_RESPONSE"]
    assert response_events
    assert response_events[0]["payload"]["error"] == "fallback:openrouter_http_429"


def test_openrouter_http_5xx_fallback_reason(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-http-5xx")
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-http-5xx",
        openrouter=ErrorOpenRouter("http_5xx", 503),
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )
    asyncio.run(runner.run())

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    resolved = next(entry for entry in entries if entry["phase"] == "decision_resolved")
    assert resolved["fallback_reason"] == "openrouter_http_5xx"


def test_openrouter_http_4xx_fallback_reason(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-http-4xx")
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-http-4xx",
        openrouter=ErrorOpenRouter("http_4xx", 401),
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )
    events: list[dict[str, Any]] = []

    async def on_event(event: dict[str, Any]) -> None:
        events.append(event)

    asyncio.run(runner.run(on_event=on_event))

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    resolved = next(entry for entry in entries if entry["phase"] == "decision_resolved")
    assert resolved["fallback_used"] is True
    assert resolved["fallback_reason"] == "openrouter_http_4xx"

    response_events = [event for event in events if event["type"] == "LLM_DECISION_RESPONSE"]
    assert response_events
    assert response_events[0]["payload"]["valid"] is False
    assert response_events[0]["payload"]["error"].startswith("fallback:")


def test_openrouter_network_error_fallback_reason(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-network-error")
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-network-error",
        openrouter=ErrorOpenRouter("network_error"),
        run_files=run_files,
        event_delay_s=0,
        max_turns=8,
    )
    asyncio.run(runner.run())

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    resolved = next(entry for entry in entries if entry["phase"] == "decision_resolved")
    assert resolved["fallback_reason"] == "openrouter_network_error"


def test_reasoning_effort_and_free_model_propagate(tmp_path) -> None:
    players = _make_players()
    reasoning = {"effort": "low"}
    players[0] = PlayerConfig(
        player_id="p1",
        name="P1",
        openrouter_model_id="openai/gpt-oss-120b:free",
        model_display_name=derive_model_display_name("openai/gpt-oss-120b:free"),
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        reasoning=reasoning,
    )
    run_files = init_run_files(tmp_path, "run-reasoning")
    openrouter = CaptureOpenRouter()
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-reasoning",
        openrouter=openrouter,
        run_files=run_files,
        event_delay_s=0,
        max_turns=20,
    )
    asyncio.run(runner.run())

    assert openrouter.calls
    matched_call = None
    for call in openrouter.calls:
        payload = _extract_payload(call["messages"])
        if payload and payload.get("decision", {}).get("player_id") == "p1":
            matched_call = call
            break
    assert matched_call is not None
    assert matched_call["model"] == "openai/gpt-oss-120b:free"
    assert matched_call["kwargs"].get("reasoning") == reasoning

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    decision_entry = next(
        entry
        for entry in entries
        if entry["phase"] == "decision_started" and entry["player_id"] == "p1"
    )
    decision_id = decision_entry["decision_id"]
    resolved = next(
        entry
        for entry in entries
        if entry["phase"] == "decision_resolved" and entry["player_id"] == "p1"
    )
    assert resolved["openrouter_model_id"] == "openai/gpt-oss-120b:free"
    assert resolved["model_display_name"] == "gpt-oss-120b:free"
    assert resolved["reasoning"] == reasoning

    prompt_payload = json.loads(
        (run_files.prompts_dir / f"decision_{decision_id}_user.json").read_text(encoding="utf-8")
    )
    assert prompt_payload["llm"]["reasoning"] == reasoning

    request_payload = json.loads(
        (run_files.quality_dir / f"decision_{decision_id}_request.txt").read_text(encoding="utf-8")
    )
    assert request_payload["reasoning"] == reasoning
    assert "temperature" not in request_payload
    assert "max_tokens" not in request_payload
    assert "max_completion_tokens" not in request_payload
    assert "max_tokens" not in request_payload["reasoning"]


def test_missing_reasoning_omits_openrouter_field(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-no-reasoning")
    openrouter = CaptureOpenRouter()
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-no-reasoning",
        openrouter=openrouter,
        run_files=run_files,
        event_delay_s=0,
        max_turns=2,
    )
    asyncio.run(runner.run())

    assert openrouter.calls
    first_call = openrouter.calls[0]
    assert "reasoning" not in first_call["kwargs"]


def test_request_stop_still_emits_game_ended(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-stopped")
    runner = LlmRunner(
        seed=123,
        players=players,
        run_id="run-stopped",
        openrouter=ScriptedOpenRouter(),
        run_files=run_files,
        event_delay_s=0,
        max_turns=4,
    )
    events: list[dict[str, Any]] = []

    async def on_event(event: dict[str, Any]) -> None:
        events.append(event)

    runner.request_stop("STOPPED")
    asyncio.run(runner.run(on_event=on_event))

    game_end = next(event for event in events if event["type"] == "GAME_ENDED")
    assert game_end["payload"]["reason"] == "STOPPED"


def test_decisions_jsonl_pairs_and_applied(tmp_path) -> None:
    players = _make_players()
    run_files = init_run_files(tmp_path, "run-sample")
    runner = LlmRunner(
        seed=2024,
        players=players,
        run_id="run-sample",
        openrouter=ScriptedOpenRouter(),
        run_files=run_files,
        event_delay_s=0,
        max_turns=40,
    )
    asyncio.run(runner.run())

    entries = [
        json.loads(line)
        for line in run_files.decisions_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    decision_order: list[str] = []
    for entry in entries:
        if entry["phase"] != "decision_started":
            continue
        if entry.get("decision_type") != "BUY_OR_AUCTION_DECISION":
            continue
        decision_id = entry["decision_id"]
        if decision_id not in decision_order:
            decision_order.append(decision_id)
    assert len(decision_order) >= 3

    resolved_by_id = {
        entry["decision_id"]: entry
        for entry in entries
        if entry["phase"] == "decision_resolved"
    }
    for decision_id in decision_order[:3]:
        started = next(
            entry for entry in entries if entry["decision_id"] == decision_id and entry["phase"] == "decision_started"
        )
        resolved = resolved_by_id[decision_id]
        assert started["decision_id"] == resolved["decision_id"]
        assert resolved["applied"] is True
        assert "LLM_DECISION_RESPONSE" in resolved["emitted_event_types"]

    first_id, second_id, third_id = decision_order[:3]
    assert resolved_by_id[first_id]["retry_used"] is False
    assert resolved_by_id[first_id]["fallback_used"] is False
    assert resolved_by_id[second_id]["retry_used"] is True
    assert resolved_by_id[second_id]["fallback_used"] is False
    assert resolved_by_id[third_id]["retry_used"] is True
    assert resolved_by_id[third_id]["fallback_used"] is True

