from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from fastapi import WebSocket

from monopoly_telemetry import (
    RunFiles,
    append_jsonl,
    append_review_label,
    build_review_summary,
    build_run_files,
    init_run_files,
    read_review_labels,
)

from monopoly_api.mock_runner import build_idle_snapshot
from monopoly_arena import LlmRunner, OpenRouterClient, PlayerConfig
from monopoly_arena.player_config import DEFAULT_SYSTEM_PROMPT, EXPECTED_PLAYER_COUNT, derive_model_display_name
from monopoly_api.ws_protocol import make_event, make_hello, make_snapshot
from monopoly_api.decision_index import DecisionIndex


class RunManager:
    def __init__(
        self,
        runs_dir: Path,
        *,
        runner_factory: Callable[..., LlmRunner] | None = None,
        openrouter_factory: Callable[[], OpenRouterClient] | None = None,
    ) -> None:
        self._runs_dir = runs_dir
        self._clients: set[WebSocket] = set()
        self._runner: LlmRunner | None = None
        self._runner_task: asyncio.Task[None] | None = None
        self._run_id: str | None = None
        self._snapshot: dict[str, Any] | None = None
        self._seq: int | None = None
        self._turn_index: int | None = None
        self._telemetry: RunFiles | None = None
        self._players: list[PlayerConfig] = []
        self._decision_index: DecisionIndex | None = None
        self._paused = False
        self._lock = asyncio.Lock()
        self._runner_factory = runner_factory or LlmRunner
        self._openrouter_factory = openrouter_factory or OpenRouterClient

    async def start_run(
        self,
        seed: int,
        players: list[PlayerConfig],
        *,
        max_turns: int = 200,
        max_trade_exchanges: int = 20,
        max_auction_actions: int = 200,
    ) -> str:
        async with self._lock:
            if len(players) != EXPECTED_PLAYER_COUNT:
                raise ValueError(f"Exactly {EXPECTED_PLAYER_COUNT} players are required for LLM runs.")
            run_id = self._generate_run_id(
                seed,
                players,
                max_turns=max_turns,
                max_trade_exchanges=max_trade_exchanges,
                max_auction_actions=max_auction_actions,
            )
            if self._is_running() and self._run_id == run_id:
                return run_id
            if self._runner_task is not None and self._runner_task.done():
                self._runner_task = None
            if self._is_running():
                await self._stop_run_locked()
            self._run_id = run_id
            self._telemetry = init_run_files(self._runs_dir, run_id)
            self._decision_index = DecisionIndex(self._telemetry)
            self._players = players
            self._runner = self._runner_factory(
                seed=seed,
                players=players,
                run_id=run_id,
                openrouter=self._openrouter_factory(),
                run_files=self._telemetry,
                max_turns=max_turns,
                max_trade_exchanges=max_trade_exchanges,
                max_auction_actions=max_auction_actions,
            )
            self._paused = False
            self._snapshot = self._runner.get_snapshot()
            self._turn_index = self._snapshot["turn_index"]
            self._seq = None
            await self.broadcast_snapshot(self._snapshot)
            self._runner_task = asyncio.create_task(self._run_loop(run_id))
            return run_id

    async def stop_run(self) -> None:
        async with self._lock:
            await self._stop_run_locked()

    async def recover_run(self, run_id: str) -> str:
        async with self._lock:
            if self._is_running():
                if self._run_id == run_id:
                    return run_id
                raise ValueError("Another run is currently active.")
            run_files = self._resolve_run_files(run_id)
            if run_files is None:
                raise FileNotFoundError(f"Run '{run_id}' was not found.")
            if run_files.summary_path.exists():
                raise ValueError("Completed runs cannot be recovered as interrupted runs.")

            run_config = _read_json(run_files.run_config_path)
            if run_config.get("run_id") != run_id:
                raise ValueError("Run configuration does not match the requested run id.")
            events = _read_jsonl(run_files.events_path)
            actions = _read_jsonl(run_files.actions_path)
            decisions = _read_jsonl(run_files.decisions_path)
            if not events:
                raise ValueError("Interrupted run has no recorded events.")
            players = _recovery_player_configs(run_config, decisions)

            self._run_id = run_id
            self._telemetry = init_run_files(self._runs_dir, run_id)
            self._decision_index = DecisionIndex(self._telemetry)
            self._players = players
            self._runner = self._runner_factory(
                seed=int(run_config["seed"]),
                players=players,
                run_id=run_id,
                openrouter=self._openrouter_factory(),
                run_files=self._telemetry,
                max_turns=int(run_config.get("max_turns", 200)),
                start_ts_ms=int(run_config.get("start_ts_ms", 0)),
                ts_step_ms=int(run_config.get("ts_step_ms", 250)),
                max_trade_exchanges=int(run_config.get("max_trade_exchanges", 20)),
                max_auction_actions=int(run_config.get("max_auction_actions", 200)),
                baseline_strategies=_dict(run_config.get("baseline_strategies")),
                resume_actions=actions,
                resume_events=events,
            )
            self._paused = False
            self._snapshot = self._runner.get_snapshot()
            self._turn_index = self._snapshot.get("turn_index")
            self._seq = events[-1].get("seq")
            await self.broadcast_snapshot(self._snapshot)
            self._runner_task = asyncio.create_task(self._run_loop(run_id))
            return run_id

    def get_status(self) -> dict[str, Any]:
        running = self._is_running()
        return {
            "running": running,
            "paused": self._paused,
            "run_id": self._run_id,
            "turn_index": self._turn_index,
            "connected_clients": len(self._clients),
            "players": [player.to_status() for player in self._players],
        }

    def get_snapshot(self) -> dict[str, Any]:
        if self._snapshot is None:
            return build_idle_snapshot()
        return copy.deepcopy(self._snapshot)

    async def subscribe(self, websocket: WebSocket) -> None:
        self._clients.add(websocket)
        try:
            await websocket.send_json(make_hello(self._run_id))
            await websocket.send_json(make_snapshot(self.get_snapshot()))
        except Exception:
            self._clients.discard(websocket)

    async def unsubscribe(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast_event(self, event: dict[str, Any]) -> None:
        self._seq = event.get("seq")
        self._turn_index = event.get("turn_index")
        if self._telemetry is not None:
            self._telemetry.write_event(event)
        await self._broadcast(make_event(event))

    async def broadcast_snapshot(self, snapshot: dict[str, Any]) -> None:
        self._snapshot = snapshot
        self._turn_index = snapshot.get("turn_index")
        if self._telemetry is not None:
            self._telemetry.write_snapshot(snapshot)
        await self._broadcast(make_snapshot(snapshot))

    async def _run_loop(self, run_id: str) -> None:
        runner = self._runner
        if runner is None or self._run_id != run_id:
            return
        await runner.run(
            on_event=self.broadcast_event,
            on_snapshot=self.broadcast_snapshot,
            on_summary=self._write_summary,
            on_decision=self._record_decision,
        )

    async def _write_summary(self, summary: dict[str, Any]) -> None:
        if self._telemetry is not None:
            self._telemetry.write_summary(summary)

    async def _broadcast(self, message: dict[str, Any]) -> None:
        if not self._clients:
            return
        clients = list(self._clients)
        results = await asyncio.gather(
            *(self._safe_send(client, message) for client in clients),
            return_exceptions=True,
        )
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                self._clients.discard(client)

    async def _safe_send(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        await websocket.send_json(message)

    async def _stop_run_locked(self) -> None:
        if self._runner_task is None:
            return
        if self._runner is not None:
            self._runner.request_stop("STOPPED")
            self._runner.resume()
        task = self._runner_task
        if task is not None and not task.done():
            task.cancel()
        if task is not None:
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._runner_task = None
        self._runner = None
        self._paused = False

    @staticmethod
    def _generate_run_id(
        seed: int,
        players: list[PlayerConfig],
        *,
        max_turns: int,
        max_trade_exchanges: int,
        max_auction_actions: int,
    ) -> str:
        players_blob = [
            {
                "player_id": player.player_id,
                "name": player.name,
                "openrouter_model_id": player.openrouter_model_id,
                "system_prompt": player.system_prompt,
            }
            for player in players
        ]
        seed_blob = json.dumps(
            {
                "seed": seed,
                "players": players_blob,
                "max_turns": max_turns,
                "max_trade_exchanges": max_trade_exchanges,
                "max_auction_actions": max_auction_actions,
            },
            sort_keys=True,
        )
        digest = hashlib.sha1(seed_blob.encode("utf-8")).hexdigest()[:8]
        return f"mock-{seed}-{digest}"

    async def _record_decision(self, entry: dict[str, Any]) -> None:
        if self._telemetry is not None:
            self._telemetry.write_decision(entry)
        if self._decision_index is not None:
            self._decision_index.record_entry(entry)

    async def pause(self) -> None:
        async with self._lock:
            if self._runner is None or not self._is_running() or self._paused:
                return
            self._paused = True
            self._runner.pause()

    async def resume(self) -> None:
        async with self._lock:
            if self._runner is None or not self._is_running():
                self._paused = False
                return
            if not self._paused:
                return
            self._paused = False
            self._runner.resume()

    def get_recent_decisions(self, limit: int) -> list[dict[str, Any]]:
        if self._decision_index is None:
            return []
        return self._decision_index.recent(limit=limit)

    def get_decision_bundle(self, decision_id: str) -> dict[str, Any] | None:
        if self._decision_index is None:
            return None
        return self._decision_index.get_bundle(decision_id)

    def get_decisions_for_run(self, run_id: str, limit: int | None = None) -> list[dict[str, Any]] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        index = self._resolve_decision_index(run_id, run_files)
        return index.ordered(limit=limit)

    def get_decision_bundle_for_run(self, run_id: str, decision_id: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        index = self._resolve_decision_index(run_id, run_files)
        return index.get_bundle(decision_id)

    def list_run_artifacts(self, run_id: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        artifacts = []
        for name, path in _run_artifact_paths(run_files).items():
            artifacts.append(
                {
                    "name": name,
                    "path": str(path),
                    "exists": path.exists(),
                    "kind": "jsonl" if path.suffix == ".jsonl" else "json",
                }
            )
        return {"run_id": run_id, "artifacts": artifacts}

    def get_run_artifact(self, run_id: str, artifact_name: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        paths = _run_artifact_paths(run_files)
        path = paths.get(artifact_name)
        if path is None or not path.exists() or not path.is_file():
            return None
        if path.suffix == ".jsonl":
            return {
                "run_id": run_id,
                "artifact": artifact_name,
                "kind": "jsonl",
                "rows": _read_jsonl(path),
            }
        return {
            "run_id": run_id,
            "artifact": artifact_name,
            "kind": "json",
            "content": _read_json(path),
        }

    def list_run_snapshots(self, run_id: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        snapshots = []
        if run_files.snapshots_dir.exists():
            for path in sorted(run_files.snapshots_dir.glob("*.json")):
                if _is_safe_snapshot_name(path.name):
                    snapshots.append({"name": path.name, "path": str(path)})
        return {"run_id": run_id, "snapshots": snapshots}

    def get_run_snapshot(self, run_id: str, snapshot_name: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None or not _is_safe_snapshot_name(snapshot_name):
            return None
        path = run_files.snapshots_dir / snapshot_name
        if not path.exists() or not path.is_file():
            return None
        return {
            "run_id": run_id,
            "snapshot": snapshot_name,
            "content": _read_json(path),
        }

    def get_review_queue(self, run_id: str) -> dict[str, Any] | None:
        artifact = self.get_run_artifact(run_id, "review_queue")
        if artifact is None:
            return None
        return {"run_id": run_id, "queue": artifact.get("rows", [])}

    def add_review_queue_item(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        current_queue = _read_jsonl(run_files.review_queue_path)
        queue_item = {
            "schema_version": "v1",
            "review_label_version": "review_label_v1",
            "queue_item_id": str(payload.get("queue_item_id") or f"review-{len(current_queue):06d}"),
            "run_id": run_id,
            "decision_id": payload.get("decision_id"),
            "turn_index": payload.get("turn_index"),
            "player_id": payload.get("player_id"),
            "model_id": payload.get("model_id"),
            "finding_ids": payload.get("finding_ids") if isinstance(payload.get("finding_ids"), list) else [],
            "failure_ids": payload.get("failure_ids") if isinstance(payload.get("failure_ids"), list) else [],
            "severity": str(payload.get("severity") or "medium"),
            "reason_for_review": str(payload.get("reason_for_review") or "user_selected_decision"),
            "suggested_labels": (
                payload.get("suggested_labels")
                if isinstance(payload.get("suggested_labels"), list)
                else ["user_selected_decision"]
            ),
            "status": "unreviewed",
            "reviewer_id": str(payload.get("reviewer_id") or "local_reviewer"),
            "review_mode": "human_only",
            "artifact_paths": {
                "events": "events.jsonl",
                "decisions": "decisions.jsonl",
                "replay": "replay.jsonl",
                "trace_findings": "trace_findings.jsonl",
                "failure_findings": "failure_findings.jsonl",
            },
        }
        append_jsonl(run_files.review_queue_path, queue_item)
        return {"run_id": run_id, "queue_item": queue_item}

    def get_review_labels(self, run_id: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        return {"run_id": run_id, "labels": read_review_labels(run_files)}

    def add_review_label(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        label = append_review_label(run_files, payload)
        return {"run_id": run_id, "label": label, "summary": build_review_summary(run_files)}

    def get_review_summary(self, run_id: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        summary = build_review_summary(run_files)
        if not run_files.review_summary_path.exists():
            run_files.write_json_artifact(run_files.review_summary_path, summary)
        return summary

    def list_runs(self) -> dict[str, Any]:
        runs = []
        if self._runs_dir.exists():
            for path in sorted(self._runs_dir.iterdir()):
                if not path.is_dir() or path.name in {"batches", "micro", "micro_batches"} or not _is_safe_run_id(path.name):
                    continue
                summary = _read_json(path / "summary.json")
                run_config = _read_json(path / "run_config.json")
                scorecard = _read_json(path / "scorecard.json")
                runs.append(
                    {
                        "run_id": path.name,
                        "run_dir": str(path),
                        "mode": run_config.get("mode"),
                        "seed": run_config.get("seed"),
                        "winner_player_id": summary.get("winner_player_id"),
                        "turn_count": summary.get("turn_count"),
                        "reason": summary.get("reason"),
                        "summary_exists": bool(summary),
                        "scorecard_exists": bool(scorecard),
                        "replay_report_exists": (path / "replay_report.json").exists(),
                        "state_replay_report_exists": (path / "state_replay_report.json").exists(),
                        "artifact_replay_report_exists": (path / "artifact_replay_report.json").exists(),
                    }
                )
        return {"runs": runs}

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        run_files = self._resolve_run_files(run_id)
        if run_files is None:
            return None
        return {
            "run_id": run_id,
            "run_dir": str(run_files.run_dir),
            "summary": _read_json(run_files.summary_path),
            "run_config": _read_json(run_files.run_config_path),
            "players": _read_json(run_files.players_path),
            "seat_assignment": _read_json(run_files.seat_assignment_path),
            "scorecard": _read_json(run_files.scorecard_path),
            "usage": _read_json(run_files.usage_path),
            "replay_report": _read_json(run_files.replay_report_path),
            "state_replay_report": _read_json(run_files.state_replay_report_path),
            "artifact_replay_report": _read_json(run_files.artifact_replay_report_path),
            "trace_summary": _read_json(run_files.trace_summary_path),
            "failure_summary": _read_json(run_files.failure_summary_path),
        }

    def get_model(self, model_id: str) -> dict[str, Any] | None:
        if "/" in model_id:
            target_model_id = model_id
        else:
            target_model_id = model_id.replace("__", "/")
        runs: list[dict[str, Any]] = []
        total_games = 0
        wins = 0
        final_net_worth_values: list[float] = []
        total_cost = 0.0
        total_tokens = 0
        for run in self.list_runs()["runs"]:
            run_id = str(run.get("run_id") or "")
            run_files = self._resolve_run_files(run_id)
            if run_files is None:
                continue
            scorecard = _read_json(run_files.scorecard_path)
            usage = _read_json(run_files.usage_path)
            matched_players = [
                player
                for player in _list(scorecard.get("players"))
                if isinstance(player, dict) and str(player.get("openrouter_model_id") or "") == target_model_id
            ]
            if not matched_players:
                continue
            for player in matched_players:
                total_games += 1
                wins += 1 if player.get("winner") else 0
                if isinstance(player.get("final_net_worth_estimate"), (int, float)):
                    final_net_worth_values.append(float(player["final_net_worth_estimate"]))
            by_model = _dict(usage.get("by_model"))
            usage_row = _dict(by_model.get(target_model_id))
            if isinstance(usage_row.get("cost"), (int, float)):
                total_cost += float(usage_row["cost"])
            if isinstance(usage_row.get("total_tokens"), (int, float)):
                total_tokens += int(usage_row["total_tokens"])
            runs.append({"run_id": run_id, "players": matched_players})
        if not runs:
            return None
        return {
            "model_id": target_model_id,
            "game_count": total_games,
            "win_count": wins,
            "win_rate": wins / total_games if total_games else None,
            "average_final_net_worth": (
                sum(final_net_worth_values) / len(final_net_worth_values)
                if final_net_worth_values
                else None
            ),
            "total_cost": round(total_cost, 10),
            "total_tokens": total_tokens,
            "runs": runs,
        }

    def list_batches(self) -> dict[str, Any]:
        batch_root = self._runs_dir / "batches"
        batches = []
        if batch_root.exists():
            for path in sorted(batch_root.iterdir()):
                if not path.is_dir() or not _is_safe_run_id(path.name):
                    continue
                manifest = _read_json(path / "batch_manifest.json") if (path / "batch_manifest.json").exists() else {}
                batches.append(
                    {
                        "batch_id": path.name,
                        "batch_dir": str(path),
                        "run_count": manifest.get("run_count"),
                        "manifest_exists": bool(manifest),
                    }
                )
        return {"batches": batches}

    def get_batch(self, batch_id: str) -> dict[str, Any] | None:
        batch_dir = self._resolve_batch_dir(batch_id)
        if batch_dir is None:
            return None
        return {
            "batch_id": batch_id,
            "batch_dir": str(batch_dir),
            "manifest": _read_json(batch_dir / "batch_manifest.json"),
            "config": _read_json(batch_dir / "batch_config.json"),
            "leaderboard": _read_json(batch_dir / "leaderboard.json"),
        }

    def list_batch_artifacts(self, batch_id: str) -> dict[str, Any] | None:
        batch_dir = self._resolve_batch_dir(batch_id)
        if batch_dir is None:
            return None
        artifacts = []
        for name, path in _batch_artifact_paths(batch_dir).items():
            artifacts.append(
                {
                    "name": name,
                    "path": str(path),
                    "exists": path.exists(),
                    "kind": "jsonl" if path.suffix == ".jsonl" else "json",
                }
            )
        model_cards_dir = batch_dir / "model_cards"
        model_cards = []
        if model_cards_dir.exists():
            for path in sorted(model_cards_dir.glob("*.json")):
                model_cards.append({"card_id": path.stem, "json_path": str(path), "markdown_path": str(path.with_suffix(".md"))})
        return {"batch_id": batch_id, "artifacts": artifacts, "model_cards": model_cards}

    def get_batch_artifact(self, batch_id: str, artifact_name: str) -> dict[str, Any] | None:
        batch_dir = self._resolve_batch_dir(batch_id)
        if batch_dir is None:
            return None
        path = _batch_artifact_paths(batch_dir).get(artifact_name)
        if path is None or not path.exists() or not path.is_file():
            return None
        if path.suffix == ".jsonl":
            return {"batch_id": batch_id, "artifact": artifact_name, "kind": "jsonl", "rows": _read_jsonl(path)}
        return {"batch_id": batch_id, "artifact": artifact_name, "kind": "json", "content": _read_json(path)}

    def get_batch_model_card(self, batch_id: str, card_id: str) -> dict[str, Any] | None:
        batch_dir = self._resolve_batch_dir(batch_id)
        if batch_dir is None or not _is_safe_run_id(card_id):
            return None
        json_path = batch_dir / "model_cards" / f"{card_id}.json"
        markdown_path = batch_dir / "model_cards" / f"{card_id}.md"
        if not json_path.exists() or not json_path.is_file():
            return None
        return {
            "batch_id": batch_id,
            "card_id": card_id,
            "json": _read_json(json_path),
            "markdown": markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else None,
        }

    def list_campaigns(self) -> dict[str, Any]:
        root = self._runs_dir / "campaigns"
        campaigns = []
        if root.exists():
            for path in sorted(root.iterdir()):
                if not path.is_dir() or not _is_safe_run_id(path.name):
                    continue
                manifest = _read_json(path / "campaign_manifest.json")
                campaigns.append(
                    {
                        "campaign_id": path.name,
                        "campaign_dir": str(path),
                        "run_count": manifest.get("run_count"),
                        "completed_run_count": manifest.get("completed_run_count"),
                        "execution_status": manifest.get("execution_status"),
                        "manifest_exists": bool(manifest),
                    }
                )
        return {"campaigns": campaigns}

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        campaign_dir = self._resolve_campaign_dir(campaign_id)
        if campaign_dir is None:
            return None
        return {
            "campaign_id": campaign_id,
            "campaign_dir": str(campaign_dir),
            "manifest": _read_json(campaign_dir / "campaign_manifest.json"),
            "config": _read_json(campaign_dir / "campaign_config.json"),
            "leaderboard": _read_json(campaign_dir / "leaderboard.json"),
            "statistics": _read_json(campaign_dir / "statistics.json"),
            "baseline_comparison": _read_json(campaign_dir / "baseline_comparison.json"),
        }

    def list_campaign_artifacts(self, campaign_id: str) -> dict[str, Any] | None:
        campaign_dir = self._resolve_campaign_dir(campaign_id)
        if campaign_dir is None:
            return None
        return {
            "campaign_id": campaign_id,
            "artifacts": _artifact_index(_campaign_artifact_paths(campaign_dir)),
        }

    def get_campaign_artifact(self, campaign_id: str, artifact_name: str) -> dict[str, Any] | None:
        campaign_dir = self._resolve_campaign_dir(campaign_id)
        if campaign_dir is None:
            return None
        path = _campaign_artifact_paths(campaign_dir).get(artifact_name)
        return _artifact_payload("campaign_id", campaign_id, artifact_name, path)

    def list_micro_research_reports(self) -> dict[str, Any]:
        root = self._runs_dir / "micro_batches"
        reports = []
        if root.exists():
            for path in sorted(root.iterdir()):
                if not path.is_dir() or not _is_safe_run_id(path.name) or not (path / "micro_report.json").exists():
                    continue
                report = _read_json(path / "micro_report.json")
                reports.append(
                    {
                        "report_id": path.name,
                        "report_dir": str(path),
                        "suite_id": report.get("suite_id"),
                        "suite_family": report.get("suite_family"),
                        "scenario_count": report.get("scenario_count"),
                        "joined_result_count": report.get("joined_result_count"),
                        "human_label_count": report.get("human_label_count"),
                    }
                )
        return {"reports": reports}

    def get_micro_research_report(self, report_id: str) -> dict[str, Any] | None:
        report_dir = self._resolve_micro_research_dir(report_id)
        if report_dir is None:
            return None
        return {
            "report_id": report_id,
            "report_dir": str(report_dir),
            "micro_report": _read_json(report_dir / "micro_report.json"),
            "category_breakdown": _read_json(report_dir / "category_breakdown.json"),
            "counterfactual_report": _read_json(report_dir / "counterfactual_report.json"),
            "safety_report": _read_json(report_dir / "safety_report.json"),
            "campaign_report": _read_json(report_dir / "campaign_report.json"),
            "result_join": _read_json(report_dir / "result_join.json"),
            "label_summary": _read_json(report_dir / "label_summary.json"),
        }

    def list_micro_research_artifacts(self, report_id: str) -> dict[str, Any] | None:
        report_dir = self._resolve_micro_research_dir(report_id)
        if report_dir is None:
            return None
        return {
            "report_id": report_id,
            "artifacts": _artifact_index(_micro_research_artifact_paths(report_dir)),
        }

    def get_micro_research_artifact(self, report_id: str, artifact_name: str) -> dict[str, Any] | None:
        report_dir = self._resolve_micro_research_dir(report_id)
        if report_dir is None:
            return None
        path = _micro_research_artifact_paths(report_dir).get(artifact_name)
        return _artifact_payload("report_id", report_id, artifact_name, path)

    def _is_running(self) -> bool:
        return self._runner_task is not None and not self._runner_task.done()

    def _resolve_run_files(self, run_id: str) -> RunFiles | None:
        if self._telemetry is not None and self._run_id == run_id:
            return self._telemetry
        if not _is_safe_run_id(run_id):
            return None
        run_dir = self._runs_dir / run_id
        if not run_dir.exists() or not run_dir.is_dir():
            return None
        return build_run_files(self._runs_dir, run_id)

    def _resolve_decision_index(self, run_id: str, run_files: RunFiles) -> DecisionIndex:
        if self._decision_index is not None and self._run_id == run_id:
            return self._decision_index
        return DecisionIndex(run_files)

    def _resolve_batch_dir(self, batch_id: str) -> Path | None:
        if not _is_safe_run_id(batch_id):
            return None
        batch_dir = self._runs_dir / "batches" / batch_id
        if not batch_dir.exists() or not batch_dir.is_dir():
            return None
        return batch_dir

    def _resolve_campaign_dir(self, campaign_id: str) -> Path | None:
        if not _is_safe_run_id(campaign_id):
            return None
        campaign_dir = self._runs_dir / "campaigns" / campaign_id
        if not campaign_dir.exists() or not campaign_dir.is_dir():
            return None
        return campaign_dir

    def _resolve_micro_research_dir(self, report_id: str) -> Path | None:
        if not _is_safe_run_id(report_id):
            return None
        report_dir = self._runs_dir / "micro_batches" / report_id
        if not report_dir.exists() or not report_dir.is_dir() or not (report_dir / "micro_report.json").exists():
            return None
        return report_dir


def _is_safe_run_id(run_id: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", run_id))


def _is_safe_snapshot_name(name: str) -> bool:
    return bool(re.fullmatch(r"turn_[0-9]{4}(?:_[A-Za-z0-9_-]+_[0-9]{4})?\.json", name))


def _run_artifact_paths(run_files: RunFiles) -> dict[str, Path]:
    return {
        "summary": run_files.summary_path,
        "run_config": run_files.run_config_path,
        "players": run_files.players_path,
        "seat_assignment": run_files.seat_assignment_path,
        "artifact_manifest": run_files.artifact_manifest_path,
        "pricing_snapshot": run_files.pricing_snapshot_path,
        "scorecard": run_files.scorecard_path,
        "scorecard_players": run_files.scorecard_players_path,
        "scorecard_decisions": run_files.scorecard_decisions_path,
        "scorecard_events": run_files.scorecard_events_path,
        "usage": run_files.usage_path,
        "usage_decisions": run_files.usage_decisions_path,
        "usage_attempts": run_files.usage_attempts_path,
        "cost_report": run_files.cost_report_path,
        "replay_report": run_files.replay_report_path,
        "state_replay_report": run_files.state_replay_report_path,
        "artifact_replay_report": run_files.artifact_replay_report_path,
        "replay_diff": run_files.replay_diff_path,
        "event_hashes": run_files.event_hashes_path,
        "replay_steps": run_files.replay_steps_path,
        "replay_flags": run_files.replay_flags_path,
        "replay_navigation": run_files.replay_navigation_path,
        "timeline": run_files.timeline_path,
        "decision_index": run_files.decision_index_path,
        "turn_index": run_files.turn_index_path,
        "player_timelines": run_files.player_timelines_path,
        "negotiation_threads": run_files.negotiation_threads_path,
        "auction_threads": run_files.auction_threads_path,
        "asset_flow": run_files.asset_flow_path,
        "cash_flow": run_files.cash_flow_path,
        "behavioral_flags": run_files.behavioral_flags_path,
        "trace_findings": run_files.trace_findings_path,
        "trace_summary": run_files.trace_summary_path,
        "failure_findings": run_files.failure_findings_path,
        "failure_summary": run_files.failure_summary_path,
        "review_queue": run_files.review_queue_path,
        "review_labels": run_files.review_labels_path,
        "review_summary": run_files.review_summary_path,
    }


def _batch_artifact_paths(batch_dir: Path) -> dict[str, Path]:
    return {
        "batch_config": batch_dir / "batch_config.json",
        "batch_manifest": batch_dir / "batch_manifest.json",
        "model_config": batch_dir / "model_config.json",
        "model_pricing_snapshot": batch_dir / "model_pricing_snapshot.json",
        "seed_manifest": batch_dir / "seed_manifest.json",
        "seat_manifest": batch_dir / "seat_manifest.json",
        "run_index": batch_dir / "run_index.json",
        "run_index_jsonl": batch_dir / "run_index.jsonl",
        "results": batch_dir / "results.jsonl",
        "leaderboard": batch_dir / "leaderboard.json",
        "scorecard_summary": batch_dir / "scorecard_summary.json",
        "category_breakdown": batch_dir / "category_breakdown.json",
        "statistical_summary": batch_dir / "statistical_summary.json",
        "replay_report": batch_dir / "replay_report.json",
        "trace_summary": batch_dir / "trace_summary.json",
        "failure_summary": batch_dir / "failure_summary.json",
        "cost_report": batch_dir / "cost_report.json",
        "token_report": batch_dir / "token_report.json",
        "usage_summary": batch_dir / "usage_summary.json",
        "budget_report": batch_dir / "budget_report.json",
        "model_failure_breakdown": batch_dir / "model_failure_breakdown.json",
        "failure_leaderboard": batch_dir / "failure_leaderboard.json",
        "top_findings": batch_dir / "top_findings.jsonl",
        "model_trace_breakdown": batch_dir / "model_trace_breakdown.json",
        "failure_trace_breakdown": batch_dir / "failure_trace_breakdown.json",
        "review_queue": batch_dir / "review_queue.jsonl",
        "artifact_manifest": batch_dir / "artifact_manifest.json",
    }


def _campaign_artifact_paths(campaign_dir: Path) -> dict[str, Path]:
    return {
        "campaign_config": campaign_dir / "campaign_config.json",
        "campaign_manifest": campaign_dir / "campaign_manifest.json",
        "seed_manifest": campaign_dir / "seed_manifest.json",
        "model_roster": campaign_dir / "model_roster.json",
        "baseline_roster": campaign_dir / "baseline_roster.json",
        "run_matrix": campaign_dir / "run_matrix.json",
        "run_matrix_jsonl": campaign_dir / "run_matrix.jsonl",
        "results": campaign_dir / "results.jsonl",
        "results_csv": campaign_dir / "results.csv",
        "run_results": campaign_dir / "run_results.json",
        "leaderboard": campaign_dir / "leaderboard.json",
        "leaderboard_csv": campaign_dir / "leaderboard.csv",
        "statistics": campaign_dir / "statistics.json",
        "baseline_comparison": campaign_dir / "baseline_comparison.json",
        "paper_report": campaign_dir / "paper_report.md",
        "execution_result": campaign_dir / "execution_result.json",
        "batch_runner_compatibility": campaign_dir / "batch_runner_compatibility.json",
        "artifact_manifest": campaign_dir / "artifact_manifest.json",
    }


def _micro_research_artifact_paths(report_dir: Path) -> dict[str, Path]:
    return {
        "micro_report": report_dir / "micro_report.json",
        "micro_report_csv": report_dir / "micro_report.csv",
        "category_breakdown": report_dir / "category_breakdown.json",
        "category_breakdown_csv": report_dir / "category_breakdown.csv",
        "counterfactual_report": report_dir / "counterfactual_report.json",
        "safety_report": report_dir / "safety_report.json",
        "campaign_report": report_dir / "campaign_report.json",
        "result_join": report_dir / "result_join.json",
        "result_join_csv": report_dir / "result_join.csv",
        "human_review_queue": report_dir / "human_review_queue.jsonl",
        "expert_labels": report_dir / "expert_labels.jsonl",
        "label_summary": report_dir / "label_summary.json",
        "paper_summary": report_dir / "paper_summary.md",
        "artifact_manifest": report_dir / "artifact_manifest.json",
    }


def _artifact_index(paths: dict[str, Path]) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "path": str(path),
            "exists": path.exists(),
            "kind": _artifact_kind(path),
        }
        for name, path in paths.items()
    ]


def _artifact_payload(
    owner_key: str,
    owner_id: str,
    artifact_name: str,
    path: Path | None,
) -> dict[str, Any] | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    kind = _artifact_kind(path)
    payload: dict[str, Any] = {
        owner_key: owner_id,
        "artifact": artifact_name,
        "kind": kind,
    }
    if kind == "jsonl":
        payload["rows"] = _read_jsonl(path)
    elif kind == "json":
        payload["content"] = _read_json(path)
    else:
        payload["text"] = path.read_text(encoding="utf-8")
    return payload


def _artifact_kind(path: Path) -> str:
    if path.suffix == ".jsonl":
        return "jsonl"
    if path.suffix == ".json":
        return "json"
    if path.suffix == ".csv":
        return "csv"
    if path.suffix == ".md":
        return "markdown"
    return "text"


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return rows
    for line in lines:
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def _recovery_player_configs(
    run_config: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> list[PlayerConfig]:
    entries = [entry for entry in _list(run_config.get("players")) if isinstance(entry, dict)]
    if len(entries) != EXPECTED_PLAYER_COUNT:
        raise ValueError(f"Interrupted run must contain exactly {EXPECTED_PLAYER_COUNT} player configurations.")

    prompts_by_player: dict[str, set[str]] = {}
    for decision in decisions:
        player_id = decision.get("player_id")
        if not isinstance(player_id, str):
            continue
        for message in _list(decision.get("prompt_messages")):
            if not isinstance(message, dict) or message.get("role") != "system":
                continue
            content = message.get("content")
            if isinstance(content, str) and content:
                prompts_by_player.setdefault(player_id, set()).add(content)

    baseline_players = set(_dict(run_config.get("baseline_strategies")))
    players: list[PlayerConfig] = []
    for entry in entries:
        player_id = entry.get("player_id")
        model_id = entry.get("openrouter_model_id")
        if not isinstance(player_id, str) or not player_id:
            raise ValueError("Interrupted run contains a player without a valid player_id.")
        if not isinstance(model_id, str) or not model_id:
            raise ValueError(f"Interrupted run player '{player_id}' has no model id.")
        observed_prompts = prompts_by_player.get(player_id, set())
        if len(observed_prompts) > 1:
            raise ValueError(f"Interrupted run player '{player_id}' used multiple system prompts.")
        if observed_prompts:
            system_prompt = next(iter(observed_prompts))
        elif player_id in baseline_players:
            system_prompt = DEFAULT_SYSTEM_PROMPT
        else:
            raise ValueError(f"Interrupted run player '{player_id}' has no recoverable system prompt.")
        players.append(
            PlayerConfig(
                player_id=player_id,
                name=str(entry.get("name") or player_id),
                openrouter_model_id=model_id,
                model_display_name=str(entry.get("model_display_name") or derive_model_display_name(model_id)),
                system_prompt=system_prompt,
                reasoning=entry.get("reasoning") if isinstance(entry.get("reasoning"), dict) else None,
                provider=entry.get("provider") if isinstance(entry.get("provider"), dict) else None,
            )
        )
    return players
