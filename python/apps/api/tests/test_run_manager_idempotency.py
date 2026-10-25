from __future__ import annotations

import asyncio
from dataclasses import replace

import pytest

from monopoly_engine import create_initial_state
from monopoly_telemetry import init_run_files
from monopoly_telemetry.commit import write_commit

from monopoly_api.player_config import DEFAULT_SYSTEM_PROMPT, PlayerConfig, derive_model_display_name
from monopoly_api.run_manager import RunManager
from monopoly_arena.treatment import treatment_fingerprint


class FakeRunner:
    def __init__(
        self,
        *,
        seed: int,
        players: list[PlayerConfig],
        run_id: str,
        openrouter: object | None = None,
        run_files: object | None = None,
        **_: object,
    ) -> None:
        self.run_id = run_id
        self.players = players
        self.extra_kwargs = _
        self.run_calls = 0
        self.pause_calls = 0
        self.resume_calls = 0
        self._stop_event = asyncio.Event()
        self._snapshot = create_initial_state(
            run_id,
            seed,
            [{"player_id": player.player_id, "name": player.name} for player in players],
        ).to_snapshot()

    def request_stop(self, reason: str = "STOPPED") -> None:
        self._stop_event.set()

    def pause(self) -> None:
        self.pause_calls += 1

    def resume(self) -> None:
        self.resume_calls += 1

    def get_snapshot(self) -> dict[str, object]:
        return self._snapshot

    async def run(self, *_: object, **__: object) -> None:
        self.run_calls += 1
        await self._stop_event.wait()


def _make_players() -> list[PlayerConfig]:
    model_id = "openai/gpt-oss-120b"
    return [
        PlayerConfig(
            player_id="p1",
            name="P1",
            openrouter_model_id=model_id,
            model_display_name=derive_model_display_name(model_id),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            reasoning=None,
        ),
        PlayerConfig(
            player_id="p2",
            name="P2",
            openrouter_model_id=model_id,
            model_display_name=derive_model_display_name(model_id),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            reasoning=None,
        ),
        PlayerConfig(
            player_id="p3",
            name="P3",
            openrouter_model_id=model_id,
            model_display_name=derive_model_display_name(model_id),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            reasoning=None,
        ),
        PlayerConfig(
            player_id="p4",
            name="P4",
            openrouter_model_id=model_id,
            model_display_name=derive_model_display_name(model_id),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            reasoning=None,
        ),
    ]


def test_start_run_idempotent_when_running(tmp_path) -> None:
    async def run_test() -> None:
        runners: list[FakeRunner] = []

        def runner_factory(**kwargs: object) -> FakeRunner:
            runner = FakeRunner(**kwargs)
            runners.append(runner)
            return runner

        manager = RunManager(
            tmp_path,
            runner_factory=runner_factory,
            openrouter_factory=lambda: object(),
        )
        players = _make_players()
        run_id = await manager.start_run(seed=101, players=players)
        await asyncio.sleep(0)
        first_task = manager._runner_task
        first_runner = manager._runner

        second_run_id = await manager.start_run(seed=101, players=players)
        await asyncio.sleep(0)

        assert second_run_id == run_id
        assert manager._runner_task is first_task
        assert manager._runner is first_runner
        assert len(runners) == 1
        assert runners[0].run_calls == 1

        await manager.stop_run()

    asyncio.run(run_test())


def test_resume_is_idempotent(tmp_path) -> None:
    async def run_test() -> None:
        runners: list[FakeRunner] = []

        def runner_factory(**kwargs: object) -> FakeRunner:
            runner = FakeRunner(**kwargs)
            runners.append(runner)
            return runner

        manager = RunManager(
            tmp_path,
            runner_factory=runner_factory,
            openrouter_factory=lambda: object(),
        )
        players = _make_players()
        await manager.start_run(seed=202, players=players)
        await asyncio.sleep(0)

        await manager.resume()
        assert runners[0].resume_calls == 0

        await manager.pause()
        assert runners[0].pause_calls == 1

        await manager.resume()
        assert runners[0].resume_calls == 1

        await manager.resume()
        assert runners[0].resume_calls == 1

        await manager.stop_run()

    asyncio.run(run_test())


def test_recover_run_restores_logged_configuration(tmp_path) -> None:
    async def run_test() -> None:
        runners: list[FakeRunner] = []

        def runner_factory(**kwargs: object) -> FakeRunner:
            runner = FakeRunner(**kwargs)
            runners.append(runner)
            return runner

        manager = RunManager(
            tmp_path,
            runner_factory=runner_factory,
            openrouter_factory=lambda: object(),
        )
        players = _make_players()
        run_id = "interrupted-run"
        run_files = init_run_files(tmp_path, run_id)
        run_files.write_run_config(
            {
                "run_id": run_id,
                "seed": 303,
                "max_turns": 25,
                "players": [player.to_status() for player in players],
                "baseline_strategies": {},
                "treatment_fingerprint": treatment_fingerprint(),
            }
        )
        run_files.write_event({"seq": 0, "turn_index": 0, "type": "LLM_DECISION_REQUESTED"})
        for index, player in enumerate(players):
            run_files.write_decision(
                {
                    "phase": "decision_started",
                    "decision_id": f"{run_id}-dec-{index:06d}",
                    "player_id": player.player_id,
                    "prompt_messages": [{"role": "system", "content": player.system_prompt}],
                }
            )

        recovered_id = await manager.recover_run(run_id)
        await asyncio.sleep(0)

        assert recovered_id == run_id
        assert manager.get_status()["running"] is True
        assert runners[0].extra_kwargs["resume_events"] == [
            {"seq": 0, "turn_index": 0, "type": "LLM_DECISION_REQUESTED"}
        ]
        assert [player.system_prompt for player in runners[0].players] == [
            player.system_prompt for player in players
        ]

        await manager.stop_run()

    asyncio.run(run_test())


@pytest.mark.parametrize("mismatch", ["identity", "treatment"])
def test_rejected_recovery_does_not_repair_journals(tmp_path, mismatch):
    files = init_run_files(tmp_path, "rejected")
    files.write_run_config({"run_id": "wrong" if mismatch == "identity" else "rejected",
                            "treatment_fingerprint": "old-treatment" if mismatch == "treatment" else None})
    write_commit(files, {"decision_id": "d1"}, {"decision_id": "d1", "phase": "decision_resolved"},
                 [{"seq": 1, "type": "EXPECTED"}])
    paths = [files.actions_path, files.decisions_path, files.events_path]
    before = {path: path.read_bytes() if path.exists() else None for path in paths}
    manager = RunManager(tmp_path, runner_factory=FakeRunner, openrouter_factory=lambda: object())
    with pytest.raises(ValueError):
        asyncio.run(manager.recover_run("rejected"))
    assert {path: path.read_bytes() if path.exists() else None for path in paths} == before


def test_repeated_start_after_stop_preserves_saved_run(tmp_path):
    async def run_test():
        manager = RunManager(tmp_path, runner_factory=FakeRunner, openrouter_factory=lambda: object())
        players = _make_players()
        run_id = await manager.start_run(seed=5, players=players)
        files = init_run_files(tmp_path, run_id)
        files.write_event({"seq": 1, "type": "ORIGINAL"})
        before = files.events_path.read_bytes()
        await manager.stop_run()
        with pytest.raises(ValueError, match="already exists"):
            await manager.start_run(seed=5, players=players)
        assert files.events_path.read_bytes() == before
        assert not manager.get_status()["running"]
    asyncio.run(run_test())


@pytest.mark.parametrize("changed", ["provider", "reasoning", "treatment"])
def test_api_run_identity_includes_full_treatment(monkeypatch, changed):
    players = _make_players()
    kwargs = {"seed": 5, "players": players, "max_turns": 5, "max_trade_exchanges": 20, "max_auction_actions": 200}
    original = RunManager._generate_run_id(**kwargs)
    if changed == "treatment":
        monkeypatch.setattr("monopoly_api.run_manager.treatment_fingerprint", lambda: "different-source")
    else:
        players[0] = replace(players[0], **{changed: {"only": ["openai"]} if changed == "provider" else {"effort": "high"}})
    assert RunManager._generate_run_id(**kwargs) != original


@pytest.mark.parametrize("legacy_shape", ["completed_without_marker", "interrupted"])
def test_recovery_refuses_historical_runs_without_rewriting_them(tmp_path, legacy_shape) -> None:
    manager = RunManager(tmp_path, runner_factory=FakeRunner, openrouter_factory=lambda: object())
    players = _make_players()
    run_id = "historical-run"
    run_files = init_run_files(tmp_path, run_id)
    run_files.write_run_config({"run_id": run_id, "seed": 303, "max_turns": 5,
                                "players": [player.to_status() for player in players], "baseline_strategies": {}})
    run_files.write_event({"seq": 0, "turn_index": 0, "type": "LLM_DECISION_REQUESTED"})
    if legacy_shape == "completed_without_marker":
        run_files.write_summary({"run_id": run_id, "reason": "TURN_LIMIT"})
        run_files.write_json_artifact(run_files.usage_path, {"run_id": run_id, "usage_accounting_version": "usage_accounting_v1"})
    before = {path: path.read_bytes() for path in run_files.run_dir.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="different executable treatment"):
        asyncio.run(manager.recover_run(run_id))
    after = {path: path.read_bytes() for path in run_files.run_dir.rglob("*") if path.is_file()}
    assert after == before


@pytest.mark.parametrize("second_cost", [0.25, None])
def test_model_detail_keeps_unknown_cost_unknown(tmp_path, second_cost) -> None:
    import json
    manager = RunManager(tmp_path, runner_factory=FakeRunner, openrouter_factory=lambda: object())
    for run_id, cost in (("run-a", 0.5), ("run-b", second_cost)):
        run_files = init_run_files(tmp_path, run_id)
        run_files.scorecard_path.write_text(json.dumps({"players": [{"openrouter_model_id": "test/model", "winner": False}]}))
        # A partially accounted run keeps its known spend in known_cost_subtotal.
        row = {"total_tokens": 10, "cost": cost, "known_cost_subtotal": 0.1 if cost is None else cost}
        run_files.usage_path.write_text(json.dumps({"by_model": {"test/model": row}}))
    detail = manager.get_model("test__model")
    assert detail is not None and detail["game_count"] == 2
    assert detail["known_cost_subtotal"] == pytest.approx(0.5 + (0.1 if second_cost is None else second_cost))
    assert detail["total_cost"] == (None if second_cost is None else 0.75)
