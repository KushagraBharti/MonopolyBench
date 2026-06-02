from __future__ import annotations

import asyncio
import json

from monopoly_arena.baselines import BASELINE_IDS, choose_baseline_action
from monopoly_arena.decision_resolver import validate_decision_action
from monopoly_arena.llm_runner import LlmRunner
from monopoly_arena.paths import resolve_repo_root
from monopoly_arena.player_config import build_single_player_config


def _example(name: str) -> dict:
    path = resolve_repo_root() / "contracts" / "examples" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _micro_scenario(scenario_id: str) -> dict:
    path = resolve_repo_root() / "contracts" / "micro" / "scenarios" / f"{scenario_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_baselines_return_valid_actions_for_representative_decisions() -> None:
    decisions = [
        _example("decision.auction.example.json"),
        _example("decision.post_turn.example.json"),
        _example("decision.liquidation.example.json"),
        _example("decision.jail.example.json"),
        _micro_scenario("buy-or-auction-vermont-light-blue-tempo-01")["decision_point"],
        _micro_scenario("trade-response-reject-leader-red-05")["decision_point"],
        _micro_scenario("trade-propose-water-works-for-new-york-01")["decision_point"],
    ]

    for decision in decisions:
        for baseline_id in BASELINE_IDS:
            action = choose_baseline_action(decision, baseline_id)
            assert action["public_message"] == ""
            assert baseline_id in action["private_thought"]
            assert validate_decision_action(decision, action) == []


def test_random_legal_baseline_is_deterministic_for_same_decision() -> None:
    decision = _example("decision.auction.example.json")
    first = choose_baseline_action(decision, "random_legal")
    second = choose_baseline_action(decision, "random_legal")
    assert first == second


def test_named_baselines_have_distinct_auction_behavior() -> None:
    decision = _example("decision.auction.example.json")
    conservative = choose_baseline_action(decision, "cash_conservative")
    aggressive = choose_baseline_action(decision, "auction_aggressive")

    assert conservative["action"] == "bid_auction"
    assert aggressive["action"] == "bid_auction"
    assert aggressive["args"]["bid_amount"] >= conservative["args"]["bid_amount"]


def test_no_trade_baseline_rejects_trade_response() -> None:
    decision = _micro_scenario("trade-response-reject-leader-red-05")["decision_point"]
    action = choose_baseline_action(decision, "no_trade")
    assert action["action"] == "reject_trade"
    assert validate_decision_action(decision, action) == []


def test_llm_runner_baseline_players_do_not_call_openrouter() -> None:
    class RaisingOpenRouter:
        calls = 0

        async def create_chat_completion(self, **_: object) -> object:
            self.calls += 1
            raise AssertionError("Baseline players must not call OpenRouter.")

        async def aclose(self) -> None:
            return None

    players = [
        build_single_player_config(player_id=f"p{index}", name=f"Baseline {index}", openrouter_model_id="baseline/no_trade")
        for index in range(1, 5)
    ]
    openrouter = RaisingOpenRouter()
    runner = LlmRunner(
        seed=101,
        players=players,
        run_id="baseline-runner-test",
        openrouter=openrouter,  # type: ignore[arg-type]
        run_files=None,
        max_turns=3,
        event_delay_s=0,
        baseline_strategies={player.player_id: "no_trade" for player in players},
    )
    decision_logs: list[dict] = []

    async def on_decision(entry: dict) -> None:
        decision_logs.append(entry)

    asyncio.run(runner.run(on_decision=on_decision))

    assert openrouter.calls == 0
    started = [entry for entry in decision_logs if entry["phase"] == "decision_started"]
    resolved = [entry for entry in decision_logs if entry["phase"] == "decision_resolved"]
    assert started
    assert resolved
    assert all(entry.get("automated") is True for entry in started)
    assert all(entry.get("prompt_messages") == [] for entry in started)
    assert all(entry.get("sequence_meta", {}).get("actor_type") == "baseline" for entry in resolved)
