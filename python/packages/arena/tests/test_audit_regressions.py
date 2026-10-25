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


@pytest.mark.parametrize("corruption", ["missing_marker", "false_marker", "empty_manifest", "unhashed_manifest", "missing_entry"])
def test_completion_requires_final_marker_and_complete_hashed_inventory(completed_run, corruption):
    files = completed_run
    marker = files.run_dir / "completion.json"
    if corruption == "missing_marker":
        marker.unlink()
    elif corruption == "false_marker":
        value = json.loads(marker.read_text())
        value["complete"] = False
        marker.write_text(json.dumps(value))
    else:
        manifest = json.loads(files.artifact_manifest_path.read_text())
        if corruption == "empty_manifest":
            manifest["artifacts"] = []
        elif corruption == "unhashed_manifest":
            for entry in manifest["artifacts"]:
                entry.pop("sha256", None)
        else:
            manifest["artifacts"] = [entry for entry in manifest["artifacts"]
                                     if not entry["relative_path"].startswith("state/")]
        files.artifact_manifest_path.write_text(json.dumps(manifest))
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


@pytest.mark.parametrize("status,error", [(None, "no_api_key"), (401, "http_4xx"), (402, "http_4xx"), (429, "http_429")])
def test_rejected_call_can_resume_without_erasing_or_double_counting_calls(tmp_path, status, error):
    from monopoly_telemetry.usage import write_usage_artifacts
    class Client:
        calls = 0

        async def create_chat_completion(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return OpenRouterResult(False, status, None, "Known rejection", error, None)
            return OpenRouterResult(True, 200, {"id": "generation", "usage": {"cost": 0.2}}, None, None, "request")

    files = init_run_files(tmp_path, "recover-call")
    client = Client()
    resolver = SharedDecisionResolver(openrouter=client, run_files=files,
        prompt_memory=PromptMemory(space_key_by_index=build_space_key_by_index()), space_key_by_index=build_space_key_by_index())
    decision = {"decision_id": "d", "player_id": "p", "turn_index": 0, "decision_type": "BUY_OR_AUCTION_DECISION"}
    first = asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    first_path = next((files.run_dir / "calls").glob("*.json"))
    original = first_path.read_bytes()
    second = asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    third = asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    assert not first.ok and second.ok and third == second and client.calls == 2
    assert first_path.read_bytes() == original
    assert first.call_id != second.call_id
    files.write_decision({"phase": "decision_resolved", **decision, "openrouter_model_id": "test",
                          "attempts": [{"raw_response": second.response_json, "call_id": second.call_id}]})
    usage = write_usage_artifacts(files)
    assert usage["attempt_count"] == 2
    attempts = load_jsonl(files.usage_attempts_path)
    assert {row["call_id"] for row in attempts} == {first.call_id, second.call_id}
    assert [row["cost"] for row in attempts if row["cost"] is not None] == [0.2]


@pytest.mark.parametrize("status,error", [(None, "total_timeout"), (None, "network_error"), (503, "http_5xx")])
def test_unknown_call_outcome_still_blocks_resubmission(tmp_path, status, error):
    class Client:
        calls = 0
        async def create_chat_completion(self, **kwargs):
            self.calls += 1
            return OpenRouterResult(False, status, None, "Outcome not known", error, None)
    files = init_run_files(tmp_path, "unknown-call")
    client = Client()
    resolver = SharedDecisionResolver(openrouter=client, run_files=files,
        prompt_memory=PromptMemory(space_key_by_index=build_space_key_by_index()), space_key_by_index=build_space_key_by_index())
    decision = {"decision_id": "d", "player_id": "p", "turn_index": 0, "decision_type": "BUY_OR_AUCTION_DECISION"}
    asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    with pytest.raises(RuntimeError, match="unknown outcome"):
        asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    assert client.calls == 1


def test_missing_physical_call_record_blocks_recovery_without_another_request(tmp_path):
    class Client:
        calls = 0
        async def create_chat_completion(self, **kwargs):
            self.calls += 1
            return OpenRouterResult(False, 429, None, "Rejected", "http_429", None)
    files = init_run_files(tmp_path, "call-gap")
    client = Client()
    resolver = SharedDecisionResolver(openrouter=client, run_files=files,
        prompt_memory=PromptMemory(space_key_by_index=build_space_key_by_index()), space_key_by_index=build_space_key_by_index())
    decision = {"decision_id": "d", "player_id": "p", "turn_index": 0, "decision_type": "BUY_OR_AUCTION_DECISION"}
    for _ in range(3):
        asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    next((files.run_dir / "calls").glob("*-1.json")).unlink()
    with pytest.raises(RuntimeError, match="history has a gap"):
        asyncio.run(resolver._call_completion(decision, 0, {"model": "test"}))
    assert client.calls == 3


def test_human_reviews_do_not_invalidate_completed_campaign_cell(completed_run):
    from monopoly_telemetry.review import append_review_label
    from monopoly_telemetry.writer_jsonl import append_jsonl
    from monopoly_arena.long_campaign import _run_campaign_row
    files = completed_run
    original = {path: path.read_bytes() for path in (files.events_path, files.actions_path, files.decisions_path)}
    append_review_label(files, {"notes": "Reviewed the action", "selected_labels": ["legal"]})
    append_jsonl(files.review_queue_path, {"queue_item_id": "manual", "decision_id": "d"})
    assert _completed_run_exists(files.run_dir)
    def no_client():
        raise AssertionError("A completed reviewed cell must not run again")
    result = asyncio.run(_run_campaign_row({"run_id": files.run_id, "runnable_with_long_runner": True},
        runs_root=files.run_dir.parent, openrouter_factory=no_client, resume=True))
    assert result["status"] == "resumed_completed"
    assert {path: path.read_bytes() for path in original} == original
    # Annotation exclusions must not exempt execution evidence from integrity checks.
    with files.actions_path.open("a") as handle:
        handle.write('{}\n')
    assert not _completed_run_exists(files.run_dir)


def test_campaign_identity_ignores_execution_controls_but_tracks_model_treatment():
    from copy import deepcopy
    from monopoly_arena.long_campaign import _run_id
    config = {"benchmark_id": "b", "campaign_id": "c", "max_turns": 5, "max_trade_exchanges": 20,
              "max_auction_actions": 200, "cost_budget": 1, "execution_preflight_path": "old.json"}
    actors = [{"seat_index": 0, "actor_id": "a", "roster_slot_index": 0, "actor_type": "llm",
               "roster_actor_ref": "a#0", "openrouter_model_id": "model/one", "provider": {"only": ["p"]}}]
    def identity(cfg, cells):
        return (_run_id(campaign_id="c", seed=7, repetition_index=0, permutation_id="fixed", max_turns=5,
                        actors=cells, run_index=0, treatment_config=cfg), _resume_key(cfg, 7, 0, "fixed", cells))
    original = identity(config, actors)
    operational = {**config, "cost_budget": 50, "execution_preflight_path": "new.json", "dry_run": False,
                   "concurrency": 2, "maximum_preflight_age_hours": 5, "execution_order_seed": 99}
    assert identity(operational, actors) == original
    assert all(a != b for a, b in zip(identity({**config, "max_trade_exchanges": 21}, actors), original))
    for key, value in [("provider", {"only": ["new"]}), ("reasoning", {"effort": "high"}),
                       ("openrouter_model_id", "model/two"), ("display_name", "New Name")]:
        changed = deepcopy(actors)
        changed[0][key] = value
        assert all(a != b for a, b in zip(identity(config, changed), original))


class RecoveryClient:
    def __init__(self, reject_once=False):
        self.reject_once = reject_once
        self.runner = None
        self.calls = 0

    async def create_chat_completion(self, **kwargs):
        self.calls += 1
        if self.reject_once:
            self.reject_once = False
            return OpenRouterResult(False, 429, None, "Rate limited", "http_429", "rejected")
        decision = self.runner._engine._pending_decision
        selected = choose_baseline_action(decision, "always_buy")
        args = {**selected.get("args", {}), "public_message": "", "private_thought": "Legal baseline move"}
        return OpenRouterResult(True, 200, {
            "id": f"generation-{self.calls}", "usage": {"cost": 0.001},
            "choices": [{"message": {"role": "assistant", "tool_calls": [{
                "id": f"tool-{self.calls}", "type": "function", "function": {
                    "name": selected["action"], "arguments": json.dumps(args)}}]}}],
        }, None, None, f"request-{self.calls}")

    async def aclose(self):
        pass


def test_five_turn_run_recovers_after_known_rate_limit_with_full_call_accounting(tmp_path):
    files = init_run_files(tmp_path, "recovered-five-turn")
    players = [build_single_player_config(player_id=f"p{i}", name=f"P{i}", openrouter_model_id="test/model")
               for i in range(4)]
    first = RecoveryClient(reject_once=True)
    first.runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=first,
                             run_files=files, max_turns=5, event_delay_s=0)
    with pytest.raises(RuntimeError):
        asyncio.run(first.runner.run())
    assert load_jsonl(files.actions_path) == []
    original_call = next((files.run_dir / "calls").glob("*.json"))
    original_bytes = original_call.read_bytes()
    recovered = RecoveryClient()
    recovered.runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=recovered,
        run_files=files, max_turns=5, event_delay_s=0,
        resume_actions=load_jsonl(files.actions_path), resume_events=load_jsonl(files.events_path))
    asyncio.run(recovered.runner.run())
    assert recovered.runner.get_snapshot()["turn_index"] == 5
    assert _completed_run_exists(files.run_dir)
    assert original_call.read_bytes() == original_bytes
    actions = load_jsonl(files.actions_path)
    usage = json.loads(files.usage_path.read_text())
    assert usage["attempt_count"] == len(actions) + 1 == recovered.calls + 1
    assert len(list((files.run_dir / "calls").glob("*.json"))) == usage["attempt_count"]
    starts = [row["decision_id"] for row in load_jsonl(files.decisions_path) if row["phase"] == "decision_started"]
    assert len(starts) == len(set(starts)) == len(actions)


@pytest.mark.parametrize("interruption", ["before_commit", "before_action", "before_resolution", "mid_events"])
def test_five_turn_recovery_from_write_failures_never_repeats_a_successful_call(tmp_path, monkeypatch, interruption):
    files = init_run_files(tmp_path, "write-failure")
    players = [build_single_player_config(player_id=f"p{i}", name=f"P{i}", openrouter_model_id="test/model")
               for i in range(4)]
    first = RecoveryClient()
    first.runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=first,
                             run_files=files, max_turns=5, event_delay_s=0)
    def fail(*args, **kwargs):
        raise OSError("Injected interruption")
    original_decision_writer, original_event_writer = files.write_decision, files.write_event
    committed_event_count = 0
    def decision_writer(row):
        if row.get("phase") == "decision_resolved":
            fail()
        original_decision_writer(row)
    def event_writer(row):
        nonlocal committed_event_count
        if list((files.run_dir / "commits").glob("*.json")):
            committed_event_count += 1
            if committed_event_count == 2:
                fail()
        original_event_writer(row)
    with monkeypatch.context() as patch:
        if interruption == "before_commit":
            patch.setattr("monopoly_arena.llm_runner.write_commit", fail)
        elif interruption == "before_action":
            patch.setattr(files, "write_action", fail)
        elif interruption == "before_resolution":
            patch.setattr(files, "write_decision", decision_writer)
        else:
            patch.setattr(files, "write_event", event_writer)
        with pytest.raises(OSError, match="Injected"):
            asyncio.run(first.runner.run())
    first_call = next((files.run_dir / "calls").glob("*.json"))
    saved_response = first_call.read_bytes()
    repair_committed_tails(files)
    recovered = RecoveryClient()
    recovered.runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=recovered,
        run_files=files, max_turns=5, event_delay_s=0,
        resume_actions=load_jsonl(files.actions_path), resume_events=load_jsonl(files.events_path))
    asyncio.run(recovered.runner.run())
    assert _completed_run_exists(files.run_dir)
    assert first_call.read_bytes() == saved_response
    action_count = len(load_jsonl(files.actions_path))
    assert first.calls + recovered.calls == action_count
    assert json.loads(files.usage_path.read_text())["attempt_count"] == action_count


@pytest.mark.parametrize("exchange_index", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("legacy", [False, True])
def test_offer_description_matches_executed_cash_properties_and_cards(exchange_index, legacy):
    game = Engine(seed=1, run_id="orientation", players=[{"player_id": f"p{i}", "name": f"P{i}"} for i in range(4)])
    author, recipient = (game.state.players[0], game.state.players[1]) if exchange_index % 2 == 0 else (game.state.players[1], game.state.players[0])
    game.state.board[1].owner_id = author.player_id
    game.state.board[3].owner_id = recipient.player_id
    author.get_out_of_jail_cards = 1
    game._jail_card_sources[author.player_id] = ["CHANCE"]
    offer = TradeExchange(author.player_id, TradeBundle(30, [SPACE_KEY_BY_INDEX[1]], 1),
                          TradeBundle(40, [SPACE_KEY_BY_INDEX[3]], 0))
    history = [TradeExchange(f"p{i % 2}", TradeBundle(0, [], 0), TradeBundle(0, [], 0)) for i in range(exchange_index)]
    thread = TradeThread("p0", "p1", 20, exchange_index, history, offer, "p0", False)
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


def test_legacy_counter_history_keeps_prompt_normalized_and_fixture_author_consistent():
    from monopoly_arena.fixture_validation import fixture_engine
    game = Engine(seed=1, run_id="counter", players=[{"player_id": f"p{i}", "name": f"P{i}"} for i in range(4)])
    bundle = {"cash": 20, "properties": [], "get_out_of_jail_cards": 0}
    request = {**bundle, "cash": 10}
    game._start_trade(game.state.players[0], {"args": {"to_player_id": "p1", "offer": bundle, "request": request}}, [], rolled_double=False)
    for counter_index in range(1, 5):
        author = game.state.players[counter_index % 2]
        decision = game._apply_trade_counter(author, game.state.trade, {"args": {"offer": bundle, "request": request}}, [])
        trade = decision["state"]["trade"]
        del trade["current_offer"]["from_player_id"]
        trade["history"] = trade.pop("history_last_2", trade.get("history", []))
        trade["history"][-1]["unrelated_metadata"] = "must not enter prompt"
        trade["history"].append("invalid history entry")
        focus = build_trade_response_decision_focus(decision)["scenario"]
        assert focus["current_offer"]["from_player_id"] == author.player_id
        assert focus["current_offer"]["if_you_accept"]["you_give"] == request
        assert all(set(row) == {"from_player_id", "offer", "request"} for row in focus["history"])
        assert fixture_engine(decision).state.trade.current_offer.from_player_id == author.player_id


def test_campaign_cost_statistics_exclude_unknown_and_count_it():
    from monopoly_arena.long_campaign import _leaderboard_payload, _statistics_payload, _baseline_comparison_payload
    entries = [{"status": "completed", "seed": i, "summary": {"turn_count": 5},
                "players": [{"actor_id": "a", "total_cost": cost}],
                "run_metrics": {"usage_metrics": {"total_cost": cost}}}
               for i, cost in enumerate([None, 0.0, 2.0])]
    config = {"campaign_id": "cost-test"}
    row = _leaderboard_payload(config, entries)["rows"][0]
    assert row["total_cost"]["count"] == 2
    assert row["average_cost_per_game"] == 1.0
    assert row["unknown_cost_count"] == 1
    stats = _statistics_payload(config, {"run_matrix": entries}, entries)["run_level"]
    assert stats["total_cost"]["count"] == 2 and stats["total_cost"]["mean"] == 1.0
    assert stats["unknown_cost_count"] == 1
    comparison = _baseline_comparison_payload(config, entries, {"rows": [row]})["rows"][0]
    assert comparison["net_worth_per_dollar"] is None
    assert comparison["unknown_cost_count"] == 1


@pytest.mark.parametrize("budget", [1.0, 50.0])
def test_incomplete_cost_coverage_blocks_next_game_and_preserves_known_spend(budget):
    from monopoly_arena.batch_artifacts import batch_actual_cost, should_stop_for_budget
    entries = [{"status": "completed", "usage": {"attempt_count": 2},
                "cost_report": {"total_actual_cost": None, "known_cost_subtotal": 5.0,
                                "cost_coverage": "partial_or_missing", "missing_cost_attempt_count": 1}}]
    assert batch_actual_cost(entries) == 5.0
    assert should_stop_for_budget({"cost_budget": budget}, entries) is not None
    entries[0]["cost_report"] = {"total_actual_cost": 0.0, "cost_coverage": "complete"}
    assert should_stop_for_budget({"cost_budget": budget}, entries) is None


@pytest.mark.parametrize("attempt_count,should_stop", [(0, False), (1, True), (None, True)])
def test_legacy_empty_cost_requires_confirmed_zero_calls(attempt_count, should_stop):
    from monopoly_arena.batch_artifacts import should_stop_for_budget, batch_cost_coverage
    entries = [{"status": "completed", "usage": {"attempt_count": attempt_count, "cost_coverage": "complete"},
                "cost_report": {"total_actual_cost": None}}]
    assert bool(should_stop_for_budget({"cost_budget": 1.0}, entries)) is should_stop
    assert batch_cost_coverage(entries) == ("partial_or_missing" if should_stop else "complete")


def test_replay_steps_expose_timeline_contract_and_preserve_legacy_envelope():
    from monopoly_arena.replay_verification import _build_replay_steps
    event = {"seq": 7, "event_id": "e7", "turn_index": 2, "type": "LLM_DECISION_REQUESTED",
             "actor": {"kind": "player", "player_id": "p1"}, "payload": {"decision_id": "d1"}}
    step = _build_replay_steps([event])[0]
    assert step["event_type"] == step["type"] == event["type"]
    assert step["event_seq"] == step["seq"] == 7
    assert step["actor"] == event["actor"]
    assert step["payload"] == event["payload"]
    assert step["event"] == event


@pytest.mark.parametrize("second_cost", [2.0, None])
def test_batch_model_costs_are_counted_once_per_game_and_unknown_stays_unknown(second_cost):
    from monopoly_arena.batch_artifacts import _leaderboard, _model_card, _batch_usage_summary
    entries = []
    for cost in [2.0, second_cost]:
        group = {"cost": cost, "decision_count": 2}
        entries.append({"status": "completed", "scorecard": {"players": [
            {"player_id": p, "openrouter_model_id": "m", "final_net_worth_estimate": 1000} for p in ["p1", "p2"]]},
            "usage": {"by_model": {"m": group}},
            "cost_report": {"total_actual_cost": cost, "by_model": {"m": group}}})
    leaderboard = _leaderboard(entries)
    expected = 4.0 if second_cost is not None else None
    assert leaderboard["rankings"][0]["total_cost"] == expected
    card = _model_card("m", entries, leaderboard)
    assert card["usage"]["total_cost"] == expected
    summary = _batch_usage_summary(entries)
    assert summary["actual_cost"] == expected
    assert summary["cost_report"]["by_model"]["m"]["cost"] == expected
    if expected is None:
        assert leaderboard["rankings"][0]["cost_adjusted_score"] is None
        assert card["usage"]["cost_per_game"] is None
        assert summary["known_cost_subtotal"] == 2.0


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


@pytest.mark.parametrize("mode", ["deleted", "empty", "only_starts"])
def test_replay_requires_resolved_decisions_even_when_file_is_empty(completed_run, mode):
    files = completed_run
    if mode == "deleted":
        files.decisions_path.unlink()
    elif mode == "empty":
        files.decisions_path.write_text("")
    else:
        starts = [row for row in load_jsonl(files.decisions_path) if row["phase"] != "decision_resolved"]
        files.decisions_path.write_text("".join(json.dumps(row) + "\n" for row in starts))
    assert build_replay_verification_report(files)["status"] != "passed"


@pytest.mark.parametrize("boundary", ["turn_end", "pending_decision"])
def test_recovery_resumes_exact_committed_turn_boundary(completed_run, boundary):
    import shutil
    files = completed_run
    original_events = load_jsonl(files.events_path)
    cutoff = next(event["seq"] for event in original_events if event["type"] == "TURN_ENDED")
    pending_id = None
    if boundary == "pending_decision":
        pending_event = next(event for event in original_events
                             if event["seq"] > cutoff and event["type"] == "LLM_DECISION_REQUESTED")
        cutoff = pending_event["seq"]
        pending_id = pending_event["payload"]["decision_id"]
    actions = load_jsonl(files.actions_path)
    decisions = load_jsonl(files.decisions_path)
    committed_ids = {row["decision_id"] for row in decisions if row.get("phase") == "decision_resolved"
                     and row["emitted_event_seq_end"] <= cutoff}
    files.actions_path.write_text("".join(json.dumps(row) + "\n" for row in actions if row["decision_id"] in committed_ids))
    files.decisions_path.write_text("".join(json.dumps(row) + "\n" for row in decisions
        if row["decision_id"] in committed_ids or (row["decision_id"] == pending_id and row["phase"] == "decision_started")))
    files.events_path.write_text("".join(json.dumps(row) + "\n" for row in original_events if row["seq"] <= cutoff))
    for path in (files.run_dir / "commits").glob("*.json"):
        if json.loads(path.read_text())["action"]["decision_id"] not in committed_ids:
            path.unlink()
    shutil.rmtree(files.snapshots_dir)
    files.snapshots_dir.mkdir()
    config = json.loads(files.run_config_path.read_text())
    players = [build_single_player_config(player_id=p["player_id"], name=p["name"],
               openrouter_model_id=p["openrouter_model_id"]) for p in config["players"]]
    runner = LlmRunner(seed=42, run_id=files.run_id, players=players, openrouter=object(),
                       run_files=files, max_turns=5, event_delay_s=0,
                       baseline_strategies=config["baseline_strategies"],
                       resume_actions=load_jsonl(files.actions_path), resume_events=load_jsonl(files.events_path))
    asyncio.run(runner.run())
    assert load_jsonl(files.events_path) == original_events
    starts = [row["decision_id"] for row in load_jsonl(files.decisions_path) if row["phase"] == "decision_started"]
    assert len(starts) == len(set(starts))
    assert _completed_run_exists(files.run_dir)
