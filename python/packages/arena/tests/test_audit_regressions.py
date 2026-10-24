from __future__ import annotations

import json
import asyncio
import pytest

from monopoly_engine import Engine, canonical_event_lines, replay_actions
from monopoly_engine.replay import load_jsonl
from monopoly_arena.baselines import BASELINE_IDS, choose_baseline_action
from monopoly_arena.long_campaign import _completed_run_exists, _resume_key, _bootstrap_mean_ci
from monopoly_telemetry import init_run_files
from monopoly_telemetry.commit import write_commit, repair_committed_tails
from monopoly_telemetry.usage import _normalize_usage, _totals
from monopoly_arena import LlmRunner, OpenRouterResult, build_single_player_config
from monopoly_arena.replay_verification import build_replay_verification_report
from monopoly_arena.decision_resolver import SharedDecisionResolver
from monopoly_arena.prompting import PromptMemory, build_space_key_by_index
from monopoly_arena.prompting import build_trade_response_decision_focus
from monopoly_engine.models import TradeBundle, TradeExchange, TradeThread
from monopoly_engine.board import SPACE_KEY_BY_INDEX


@pytest.mark.parametrize("baseline", sorted(BASELINE_IDS))
@pytest.mark.parametrize("seed", [7, 23, 42])
def test_five_turn_baseline_smoke_with_exact_replay(baseline, seed):
    players = [{"player_id": f"p{i}", "name": f"P{i}"} for i in range(4)]
    game = Engine(seed=seed, run_id="smoke", players=players, max_turns=5)
    events, actions = [], []
    for _ in range(1000):
        _, new, decision, _ = game.advance_until_decision()
        events.extend(new)
        if decision:
            action = choose_baseline_action(decision, baseline)
            assert not game.validate_action_for_decision(action, decision)
            actions.append(action)
            _, new, _, _ = game.apply_action(action)
            events.extend(new)
        if game.is_game_over():
            break
    assert game.is_game_over() and game.state.turn_index == 5
    replay = replay_actions(seed=seed, run_id="smoke", players=players, max_turns=5, actions=actions)
    assert canonical_event_lines(events) == canonical_event_lines(replay)


def test_strict_records_and_empty_completion(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text('{"seq":1}\n{"bad":\n')
    with pytest.raises(ValueError, match="invalid JSON"):
        load_jsonl(path)
    assert not _completed_run_exists(tmp_path)
    path.write_text('[]\n')
    with pytest.raises(ValueError, match="expected an object"):
        load_jsonl(path)


def test_byok_cost_and_unknown_are_distinct():
    byok = _normalize_usage({"cost": 0, "cost_details": {"upstream_inference_cost": 3.5}}, {})
    assert byok["cost"] == 3.5 and byok["gateway_charge"] == 0
    credit = _normalize_usage({"cost": 3.5, "cost_details": {"upstream_inference_cost": 3.5}}, {})
    assert credit["cost"] == 3.5
    assert _totals([{"cost": None}])["cost"] is None
    assert _totals([{"cost": 0}])["cost"] == 0
    assert _normalize_usage({"cost": 0, "is_byok": True}, {})["cost"] is None


def test_treatment_identity_changes_and_singleton_has_no_ci():
    config = {"benchmark_id": "b", "campaign_id": "c", "max_turns": 5, "max_trade_exchanges": 20}
    first = _resume_key(config, 1, 0, "p", [])
    config["max_trade_exchanges"] = 21
    assert _resume_key(config, 1, 0, "p", []) != first
    assert _bootstrap_mean_ci([5])["lower"] is None


@pytest.mark.parametrize("boundary", [0, 1, 2, 3])
def test_commit_repairs_each_append_boundary_idempotently(tmp_path, boundary):
    files = init_run_files(tmp_path, "repair")
    action = {"decision_id": "d1", "action": {"action": "end_turn"}}
    decision = {"decision_id": "d1", "phase": "decision_resolved"}
    events = [{"seq": 1, "type": "LLM_DECISION_RESPONSE"}, {"seq": 2, "type": "TURN_ENDED"}]
    write_commit(files, action, decision, events)
    if boundary >= 1:
        files.write_action(action)
    if boundary >= 2:
        files.write_decision(decision)
    if boundary >= 3:
        files.write_event(events[0])
    repair_committed_tails(files)
    repair_committed_tails(files)
    assert load_jsonl(files.actions_path) == [action]
    assert load_jsonl(files.decisions_path) == [decision]
    assert load_jsonl(files.events_path) == events
    files.events_path.write_text(json.dumps({"seq": 1, "type": "CORRUPTED"}) + "\n")
    with pytest.raises(ValueError, match="Conflicting"):
        repair_committed_tails(files)


@pytest.fixture
def completed_run(tmp_path):
    files = init_run_files(tmp_path, "full-smoke")
    players = [build_single_player_config(player_id=f"p{i}", name=f"P{i}", openrouter_model_id="test/model")
               for i in range(4)]
    runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=object(),
                       run_files=files, max_turns=5, event_delay_s=0,
                       baseline_strategies={p.player_id: "always_buy" for p in players})
    asyncio.run(runner.run())
    assert _completed_run_exists(files.run_dir)
    return files


@pytest.mark.parametrize("corruption", ["malformed", "extra", "delete", "duplicate", "reorder", "modify"])
def test_complete_record_reconciliation_rejects_corruption(completed_run, corruption):
    files = completed_run
    if corruption == "malformed":
        with files.events_path.open("a") as handle:
            handle.write('{"broken":\n')
    else:
        rows = load_jsonl(files.actions_path)
        if corruption == "extra":
            rows.append({"decision_id": "extra", "action": {"action": "end_turn"}})
        elif corruption == "delete":
            rows.pop()
        elif corruption == "duplicate":
            rows.append(rows[-1])
        elif corruption == "reorder":
            rows[0], rows[1] = rows[1], rows[0]
        else:
            rows[0]["action"]["public_message"] = "modified"
        files.actions_path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    assert build_replay_verification_report(files)["status"] != "passed"
    assert not _completed_run_exists(files.run_dir)


def test_saved_response_is_reused_without_second_call(tmp_path):
    class Client:
        calls = 0

        async def create_chat_completion(self, **kwargs):
            self.calls += 1
            return OpenRouterResult(True, 200, {"id": "generation"}, None, None, "request")

    files = init_run_files(tmp_path, "reuse")
    client = Client()
    resolver = SharedDecisionResolver(openrouter=client, run_files=files,
                                      prompt_memory=PromptMemory(space_key_by_index=build_space_key_by_index()),
                                      space_key_by_index=build_space_key_by_index())
    decision = {"decision_id": "d", "player_id": "p", "turn_index": 0, "decision_type": "BUY_OR_AUCTION_DECISION"}
    first = asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    second = asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    assert first == second and client.calls == 1
    with pytest.raises(RuntimeError, match="differs"):
        asyncio.run(resolver._call_completion(decision, 0, {"model": "changed"}))


@pytest.mark.parametrize("exchange_index", [1, 2, 3, 4])
@pytest.mark.parametrize("legacy", [False, True])
def test_offer_description_matches_executed_cash_properties_and_cards(exchange_index, legacy):
    game = Engine(seed=1, run_id="orientation", players=[{"player_id": f"p{i}", "name": f"P{i}"} for i in range(4)])
    author, recipient = (game.state.players[0], game.state.players[1]) if exchange_index % 2 else (game.state.players[1], game.state.players[0])
    game.state.board[1].owner_id = author.player_id
    game.state.board[3].owner_id = recipient.player_id
    author.get_out_of_jail_cards = 1
    game._jail_card_sources[author.player_id] = ["CHANCE"]
    offer = TradeExchange(author.player_id, TradeBundle(30, [SPACE_KEY_BY_INDEX[1]], 1),
                          TradeBundle(40, [SPACE_KEY_BY_INDEX[3]], 0))
    thread = TradeThread("p0", "p1", 20, exchange_index, [offer], offer, "p0", False)
    snapshot = thread.to_snapshot()
    if legacy:
        del snapshot["current_offer"]["from_player_id"]
    focus = build_trade_response_decision_focus({"player_id": recipient.player_id, "state": {"trade": snapshot}})
    description = focus["scenario"]["current_offer"]["if_you_accept"]
    assert description["you_give"] == offer.request.to_snapshot()
    assert description["you_receive"] == offer.offer.to_snapshot()
    before = recipient.cash
    game._apply_trade_accept(thread, [])
    assert recipient.cash == before + description["you_receive"]["cash"] - description["you_give"]["cash"]
    assert game.state.board[1].owner_id == recipient.player_id
    assert game.state.board[3].owner_id == author.player_id
    assert recipient.get_out_of_jail_cards == 1 and author.get_out_of_jail_cards == 0


def test_terminal_run_can_repeat_finalization_without_provider_calls(completed_run):
    files = completed_run
    original_actions = files.actions_path.read_bytes()
    original_events = files.events_path.read_bytes()
    config = json.loads(files.run_config_path.read_text())
    players = [build_single_player_config(player_id=p["player_id"], name=p["name"],
                                          openrouter_model_id=p["openrouter_model_id"]) for p in config["players"]]
    runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=object(),
                       run_files=files, max_turns=5, event_delay_s=0,
                       baseline_strategies=config["baseline_strategies"],
                       resume_actions=load_jsonl(files.actions_path), resume_events=load_jsonl(files.events_path))
    asyncio.run(runner.run())
    assert _completed_run_exists(files.run_dir)
    assert files.actions_path.read_bytes() == original_actions
    assert files.events_path.read_bytes() == original_events
