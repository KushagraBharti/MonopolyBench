from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import itertools
import json
import math
import random
import re
from io import StringIO
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

from .baselines import BASELINE_IDS
from .llm_runner import LlmRunner
from .openrouter_client import OpenRouterClient
from .paths import resolve_repo_path, resolve_repo_root
from .player_config import DEFAULT_SYSTEM_PROMPT, PlayerConfig, derive_model_display_name, normalize_reasoning
from .research_registry import (
    EXPECTED_LONG_HORIZON_PLAYERS,
    get_model_roster,
    get_seed_cohort,
    load_model_roster_registry,
    load_seed_registry,
    validate_campaign_config,
)
from monopoly_telemetry import init_run_files


LONG_CAMPAIGN_PROTOCOL_VERSION = "long_horizon_campaign_v1"
DEFAULT_RUNS_DIR = "runs"
SUPPORTED_SEAT_MODES = {"configured_order", "full", "latin_square", "seeded_random"}


def load_campaign_config(path: Path | str) -> dict[str, Any]:
    parsed = json.loads(resolve_repo_path(str(path)).read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    validate_campaign_config(parsed)
    return parsed


def build_campaign_plan(
    config: dict[str, Any],
    *,
    seed_registry: dict[str, Any] | None = None,
    roster_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_campaign_config(config)
    seed_registry = seed_registry if seed_registry is not None else load_seed_registry()
    roster_registry = roster_registry if roster_registry is not None else load_model_roster_registry()
    seed_cohort = get_seed_cohort(str(config["seed_cohort"]), seed_registry)
    roster_bundle = get_model_roster(
        str(config["model_roster"]),
        roster_registry,
        include_disabled=bool(config.get("allow_disabled_actors", False)),
    )
    actors = _actor_slots(roster_bundle["actors"])
    if len(actors) != EXPECTED_LONG_HORIZON_PLAYERS:
        raise ValueError(
            f"Long-horizon campaigns currently require exactly {EXPECTED_LONG_HORIZON_PLAYERS} actors."
        )
    seat_mode = str(config["seat_permutation"])
    if seat_mode not in SUPPORTED_SEAT_MODES:
        raise ValueError(f"Unsupported seat_permutation mode: {seat_mode}")
    rows = _build_run_matrix(config=config, seed_cohort=seed_cohort, actors=actors)
    return {
        "schema_version": "v1",
        "campaign_protocol_version": LONG_CAMPAIGN_PROTOCOL_VERSION,
        "campaign_config": _normalized_campaign_config(config),
        "seed_manifest": _seed_manifest(config, seed_cohort),
        "model_roster": _model_roster_manifest(config, roster_bundle, actors),
        "baseline_roster": _baseline_roster_manifest(config, actors),
        "run_matrix": rows,
        "batch_runner_compatibility": _batch_runner_compatibility(config, rows),
        "campaign_manifest": _campaign_manifest(config, seed_cohort, actors, rows),
    }


def write_campaign_plan(config: dict[str, Any], *, runs_dir: Path | str | None = None) -> Path:
    plan = build_campaign_plan(config)
    paths = campaign_paths(
        resolve_repo_path(str(runs_dir)) if runs_dir is not None else resolve_repo_root() / DEFAULT_RUNS_DIR,
        str(config["campaign_id"]),
    )
    paths["campaign_dir"].mkdir(parents=True, exist_ok=True)
    _write_json(paths["campaign_config"], plan["campaign_config"])
    _write_json(paths["campaign_manifest"], plan["campaign_manifest"])
    _write_json(paths["seed_manifest"], plan["seed_manifest"])
    _write_json(paths["model_roster"], plan["model_roster"])
    _write_json(paths["baseline_roster"], plan["baseline_roster"])
    _write_json(paths["run_matrix"], {"schema_version": "v1", "runs": plan["run_matrix"]})
    _write_jsonl(paths["run_matrix_jsonl"], plan["run_matrix"])
    _write_json(paths["batch_runner_compatibility"], plan["batch_runner_compatibility"])
    _write_json(paths["artifact_manifest"], _artifact_manifest(paths))
    return paths["campaign_dir"]


async def run_campaign(
    config: dict[str, Any],
    *,
    runs_dir: Path | str | None = None,
    openrouter_factory: Any = OpenRouterClient,
    max_runs: int | None = None,
    force_execute: bool = False,
) -> dict[str, Any]:
    validate_campaign_config(config)
    root = resolve_repo_path(str(runs_dir)) if runs_dir is not None else resolve_repo_root() / DEFAULT_RUNS_DIR
    plan = build_campaign_plan(config)
    paths = campaign_paths(root, str(config["campaign_id"]))
    write_campaign_plan(config, runs_dir=root)
    if bool(config.get("dry_run")) and not force_execute:
        result = {
            "schema_version": "v1",
            "campaign_id": config["campaign_id"],
            "status": "dry_run_only",
            "run_count": 0,
            "campaign_dir": str(paths["campaign_dir"]),
            "prompt_pipeline": _prompt_marker("Dry-run campaign planning does not execute prompts."),
        }
        _write_json(paths["execution_result"], result)
        _write_json(paths["artifact_manifest"], _artifact_manifest(paths))
        return result

    run_entries: list[dict[str, Any]] = []
    executed = 0
    for row in plan["run_matrix"]:
        if max_runs is not None and executed >= max_runs:
            entry = _campaign_result_entry(row, status="not_started_max_runs_limit", run_dir=root / str(row["run_id"]))
            run_entries.append(entry)
            continue
        entry = await _run_campaign_row(
            row,
            runs_root=root,
            openrouter_factory=openrouter_factory,
            resume=bool(config.get("resume", True)),
        )
        run_entries.append(entry)
        if entry["status"] not in {"resumed_completed", "not_runnable"}:
            executed += 1
        if entry["status"] == "failed" and not bool(config.get("continue_on_failure", False)):
            break

    _write_campaign_dynamic_artifacts(paths, config, plan, run_entries)
    return {
        "schema_version": "v1",
        "campaign_id": config["campaign_id"],
        "status": "executed",
        "run_count": len(run_entries),
        "completed_count": sum(1 for entry in run_entries if entry["status"] in {"completed", "resumed_completed"}),
        "failed_count": sum(1 for entry in run_entries if entry["status"] == "failed"),
        "campaign_dir": str(paths["campaign_dir"]),
        "prompt_pipeline": _prompt_marker("Campaign execution uses existing LlmRunner prompt path for LLMs only."),
    }


def campaign_paths(runs_root: Path, campaign_id: str) -> dict[str, Path]:
    campaign_dir = runs_root / "campaigns" / campaign_id
    return {
        "campaign_dir": campaign_dir,
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


def _build_run_matrix(
    *,
    config: dict[str, Any],
    seed_cohort: dict[str, Any],
    actors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    run_index = 0
    repetitions = int(config["repetitions_per_seed"])
    for seed_entry in _list(seed_cohort.get("seeds")):
        seed = int(seed_entry["seed"])
        for repetition_index in range(repetitions):
            for permutation_id, ordered_actors, seed_material in _seat_orders(
                actors=actors,
                mode=str(config["seat_permutation"]),
                campaign_id=str(config["campaign_id"]),
                seed=seed,
                repetition_index=repetition_index,
                max_turns=int(config["max_turns"]),
            ):
                row_actors = [_seat_actor(actor, seat_index) for seat_index, actor in enumerate(ordered_actors)]
                contains_baseline = any(actor["actor_type"] == "baseline" for actor in row_actors)
                baseline_strategies = _baseline_strategies(row_actors)
                run_id = _run_id(
                    campaign_id=str(config["campaign_id"]),
                    seed=seed,
                    repetition_index=repetition_index,
                    permutation_id=permutation_id,
                    max_turns=int(config["max_turns"]),
                    actors=row_actors,
                    run_index=run_index,
                )
                rows.append(
                    {
                        "schema_version": "v1",
                        "campaign_protocol_version": LONG_CAMPAIGN_PROTOCOL_VERSION,
                        "campaign_id": config["campaign_id"],
                        "benchmark_id": config["benchmark_id"],
                        "run_index": run_index,
                        "run_id": run_id,
                        "seed": seed,
                        "seed_label": seed_entry.get("label"),
                        "seed_rationale": seed_entry.get("rationale"),
                        "seed_cohort": seed_cohort["cohort_id"],
                        "repetition_index": repetition_index,
                        "seat_permutation": config["seat_permutation"],
                        "permutation_id": permutation_id,
                        "permutation_seed_material": seed_material,
                        "max_turns": int(config["max_turns"]),
                        "max_trade_exchanges": int(config.get("max_trade_exchanges") or 20),
                        "max_auction_actions": int(config.get("max_auction_actions") or 200),
                        "actors": row_actors,
                        "contains_baseline": contains_baseline,
                        "baseline_strategies": baseline_strategies,
                        "runnable_with_current_batch_runner": _runnable_with_current_batch_runner(row_actors),
                        "runnable_with_long_runner": _runnable_with_long_runner(row_actors),
                        "status": "planned",
                        "resume_key": _resume_key(config, seed, repetition_index, permutation_id, row_actors),
                        "prompt_pipeline": {
                            "status": "unchanged",
                            "note": "This planned cell only assigns seed, seat, and actor ids; it does not change prompts.",
                        },
                    }
                )
                run_index += 1
    return rows


def _seat_orders(
    *,
    actors: list[dict[str, Any]],
    mode: str,
    campaign_id: str,
    seed: int,
    repetition_index: int,
    max_turns: int,
) -> list[tuple[str, list[dict[str, Any]], dict[str, Any]]]:
    seed_material = {
        "campaign_id": campaign_id,
        "seed": seed,
        "repetition_index": repetition_index,
        "mode": mode,
        "max_turns": max_turns,
        "roster_slots": [actor["roster_actor_ref"] for actor in actors],
    }
    if mode == "configured_order":
        return [("configured_order:0", list(actors), seed_material)]
    if mode == "latin_square":
        return [
            (f"latin_square:{offset}", list(actors[offset:]) + list(actors[:offset]), seed_material)
            for offset in range(len(actors))
        ]
    if mode == "full":
        return [
            (f"full:{index}", list(order), seed_material)
            for index, order in enumerate(itertools.permutations(actors))
        ]
    if mode == "seeded_random":
        selected = list(actors)
        random.Random(_deterministic_int(seed_material)).shuffle(selected)
        return [("seeded_random:0", selected, seed_material)]
    raise ValueError(f"Unsupported seat_permutation mode: {mode}")


def _actor_slots(actors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for index, actor in enumerate(actors):
        actor_id = str(actor["actor_id"])
        slots.append(
            {
                **actor,
                "roster_slot_index": index,
                "roster_actor_ref": f"{actor_id}#{index}",
            }
        )
    return slots


def _seat_actor(actor: dict[str, Any], seat_index: int) -> dict[str, Any]:
    row = {
        "seat_index": seat_index,
        "player_id": f"p{seat_index + 1}",
        "actor_id": actor["actor_id"],
        "actor_type": actor["actor_type"],
        "display_name": actor["display_name"],
        "enabled": bool(actor["enabled"]),
        "cost_budget_group": actor["cost_budget_group"],
        "roster_slot_index": actor["roster_slot_index"],
        "roster_actor_ref": actor["roster_actor_ref"],
    }
    for key in ("openrouter_model_id", "reasoning", "top_p", "baseline_id", "notes"):
        if key in actor:
            row[key] = actor[key]
    return row


def _normalized_campaign_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        **config,
        "concurrency": int(config.get("concurrency") or 1),
        "budget_policy": str(config.get("budget_policy") or "stop_immediately"),
        "resume": bool(config.get("resume", True)),
        "continue_on_failure": bool(config.get("continue_on_failure", False)),
        "replay_after_run": bool(config.get("replay_after_run", True)),
        "build_scorecard_after_run": bool(config.get("build_scorecard_after_run", True)),
        "build_trace_after_run": bool(config.get("build_trace_after_run", True)),
        "build_failure_taxonomy_after_run": bool(config.get("build_failure_taxonomy_after_run", True)),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Campaign configuration changes only run planning and artifact generation, not model-facing prompts.",
        },
    }


def _seed_manifest(config: dict[str, Any], seed_cohort: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "seed_manifest_version": "long_horizon_seed_manifest_v1",
        "campaign_id": config["campaign_id"],
        "benchmark_id": config["benchmark_id"],
        "seed_cohort": seed_cohort["cohort_id"],
        "cohort_version": seed_cohort["version"],
        "description": seed_cohort["description"],
        "intended_use": seed_cohort["intended_use"],
        "source_cohorts": seed_cohort.get("source_cohorts", []),
        "seeds": seed_cohort["seeds"],
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Seed manifests are post-hoc/config artifacts and are never injected into prompts.",
        },
    }


def _model_roster_manifest(
    config: dict[str, Any],
    roster_bundle: dict[str, Any],
    actors: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "model_roster_manifest_version": "long_horizon_model_roster_manifest_v1",
        "campaign_id": config["campaign_id"],
        "benchmark_id": config["benchmark_id"],
        "roster_id": roster_bundle["roster_id"],
        "roster": roster_bundle["roster"],
        "actors": actors,
        "llm_actors": [actor for actor in actors if actor["actor_type"] == "llm"],
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Roster metadata selects actors and is not included in model-facing prompt content.",
        },
    }


def _baseline_roster_manifest(config: dict[str, Any], actors: list[dict[str, Any]]) -> dict[str, Any]:
    baselines = [actor for actor in actors if actor["actor_type"] == "baseline"]
    return {
        "schema_version": "v1",
        "baseline_roster_manifest_version": "long_horizon_baseline_roster_manifest_v1",
        "campaign_id": config["campaign_id"],
        "benchmark_id": config["benchmark_id"],
        "baseline_count": len(baselines),
        "baselines": baselines,
        "execution_status": "long_runner_available" if baselines else "no_baselines_in_selected_roster",
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Baselines are non-LLM comparators and must not receive or alter LLM prompts.",
        },
    }


def _campaign_manifest(
    config: dict[str, Any],
    seed_cohort: dict[str, Any],
    actors: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    baseline_count = sum(1 for actor in actors if actor["actor_type"] == "baseline")
    return {
        "schema_version": "v1",
        "campaign_manifest_version": "long_horizon_campaign_manifest_v1",
        "campaign_protocol_version": LONG_CAMPAIGN_PROTOCOL_VERSION,
        "campaign_id": config["campaign_id"],
        "benchmark_id": config["benchmark_id"],
        "dry_run": bool(config["dry_run"]),
        "planning_only": True,
        "execution_status": "planned_not_executed",
        "seed_cohort": seed_cohort["cohort_id"],
        "seed_count": len(_list(seed_cohort.get("seeds"))),
        "repetitions_per_seed": int(config["repetitions_per_seed"]),
        "seat_permutation": config["seat_permutation"],
        "actor_count": len(actors),
        "baseline_actor_count": baseline_count,
        "llm_actor_count": len(actors) - baseline_count,
        "run_count": len(rows),
        "runnable_with_current_batch_runner_count": sum(
            1 for row in rows if bool(row.get("runnable_with_current_batch_runner"))
        ),
        "runnable_with_long_runner_count": sum(1 for row in rows if bool(row.get("runnable_with_long_runner"))),
        "cost_budget": config.get("cost_budget"),
        "budget_policy": config.get("budget_policy"),
        "concurrency": config.get("concurrency"),
        "resume": config.get("resume"),
        "artifacts": [
            "campaign_config.json",
            "campaign_manifest.json",
            "seed_manifest.json",
            "model_roster.json",
            "baseline_roster.json",
            "run_matrix.json",
            "run_matrix.jsonl",
            "batch_runner_compatibility.json",
            "artifact_manifest.json",
        ],
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Campaign planning writes research artifacts only; no prompt builders are touched.",
        },
    }


def _batch_runner_compatibility(config: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    compatible_rows = [row for row in rows if row.get("runnable_with_current_batch_runner")]
    all_rows_compatible = len(compatible_rows) == len(rows)
    reasons: list[str] = []
    if not all_rows_compatible:
        reasons.append("Selected matrix contains deterministic baseline actors that require long_campaign execution.")
    if config["seat_permutation"] in {"latin_square", "full"} and len({row["seed"] for row in rows}) > 1:
        reasons.append(
            "Existing batch_run cycles seeds and seats by run index; this campaign matrix explicitly expands every seed-seat cell."
        )
    return {
        "schema_version": "v1",
        "campaign_id": config["campaign_id"],
        "compatible": all_rows_compatible and not reasons,
        "compatible_row_count": len(compatible_rows),
        "total_row_count": len(rows),
        "reasons": reasons,
        "next_step": (
            "Use long_campaign run execution once implemented."
            if reasons
            else "Rows contain only enabled LLM actors; execution adapter can map rows to PlayerConfig."
        ),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Compatibility analysis is post-hoc and does not affect model-facing content.",
        },
    }


async def _run_campaign_row(
    row: dict[str, Any],
    *,
    runs_root: Path,
    openrouter_factory: Any,
    resume: bool,
) -> dict[str, Any]:
    run_dir = runs_root / str(row["run_id"])
    if not bool(row.get("runnable_with_long_runner")):
        return _campaign_result_entry(
            row,
            status="not_runnable",
            run_dir=run_dir,
            error="Run row contains a disabled or unsupported actor.",
        )
    if resume and _completed_run_exists(run_dir):
        return _campaign_result_entry(row, status="resumed_completed", run_dir=run_dir)
    if run_dir.exists() and not _run_dir_is_empty(run_dir):
        return _campaign_result_entry(
            row,
            status="failed",
            run_dir=run_dir,
            error=(
                "Run directory exists but does not contain a completed artifact set. "
                "Delete or archive it before rerunning this deterministic cell."
            ),
        )

    try:
        players = _campaign_players(row)
        run_files = init_run_files(runs_root, str(row["run_id"]))
        openrouter = openrouter_factory() if callable(openrouter_factory) else openrouter_factory
        runner = LlmRunner(
            seed=int(row["seed"]),
            players=players,
            run_id=str(row["run_id"]),
            openrouter=openrouter,
            run_files=run_files,
            max_turns=int(row["max_turns"]),
            event_delay_s=0,
            start_ts_ms=0,
            ts_step_ms=250,
            max_trade_exchanges=int(row.get("max_trade_exchanges") or 20),
            max_auction_actions=int(row.get("max_auction_actions") or 200),
            seat_assignment_metadata={
                "permutation_mode": row.get("seat_permutation"),
                "permutation_id": row.get("permutation_id"),
                "permutation_seed_material": row.get("permutation_seed_material"),
                "batch_id": row.get("campaign_id"),
                "batch_run_index": row.get("run_index"),
            },
            baseline_strategies=_dict(row.get("baseline_strategies")),
        )
        run_files.write_snapshot(runner.get_snapshot())
        await runner.run()
    except Exception as exc:  # noqa: BLE001 - campaign artifacts should record failed cells.
        return _campaign_result_entry(row, status="failed", run_dir=run_dir, error=f"{type(exc).__name__}: {exc}")

    return _campaign_result_entry(row, status="completed", run_dir=run_dir)


def _campaign_players(row: dict[str, Any]) -> list[PlayerConfig]:
    players: list[PlayerConfig] = []
    for actor in _list(row.get("actors")):
        actor_type = str(actor.get("actor_type") or "")
        if actor_type == "baseline":
            baseline_id = str(actor.get("baseline_id") or "")
            model_id = f"baseline/{baseline_id}"
            reasoning = None
        else:
            model_id = str(actor.get("openrouter_model_id") or "")
            if not model_id:
                raise ValueError(f"Actor {actor.get('actor_id')} is missing openrouter_model_id.")
            reasoning = normalize_reasoning(actor.get("reasoning")) if isinstance(actor.get("reasoning"), dict) else None
        players.append(
            PlayerConfig(
                player_id=str(actor["player_id"]),
                name=str(actor.get("display_name") or actor["player_id"]),
                openrouter_model_id=model_id,
                model_display_name=str(actor.get("display_name") or derive_model_display_name(model_id)),
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                reasoning=reasoning,
            )
        )
    if len(players) != EXPECTED_LONG_HORIZON_PLAYERS:
        raise ValueError(f"Campaign rows must define exactly {EXPECTED_LONG_HORIZON_PLAYERS} players.")
    return players


def _completed_run_exists(run_dir: Path) -> bool:
    required = [
        "events.jsonl",
        "actions.jsonl",
        "decisions.jsonl",
        "summary.json",
        "scorecard.json",
        "scorecard_players.json",
        "replay_report.json",
        "state_replay_report.json",
        "artifact_replay_report.json",
        "trace_summary.json",
        "failure_summary.json",
    ]
    return all((run_dir / name).exists() for name in required)


def _run_dir_is_empty(run_dir: Path) -> bool:
    return not run_dir.exists() or not any(run_dir.iterdir())


def _campaign_result_entry(
    row: dict[str, Any],
    *,
    status: str,
    run_dir: Path,
    error: str | None = None,
) -> dict[str, Any]:
    summary = _read_json(run_dir / "summary.json")
    scorecard = _read_json(run_dir / "scorecard.json")
    scorecard_players = _read_json_value(run_dir / "scorecard_players.json")
    usage = _read_json(run_dir / "usage.json")
    cost_report = _read_json(run_dir / "cost_report.json")
    replay_report = _read_json(run_dir / "replay_report.json")
    state_replay_report = _read_json(run_dir / "state_replay_report.json")
    artifact_replay_report = _read_json(run_dir / "artifact_replay_report.json")
    trace_summary = _read_json(run_dir / "trace_summary.json")
    failure_summary = _read_json(run_dir / "failure_summary.json")
    run_metrics = _dict(scorecard.get("run")) if scorecard else {}

    return {
        "schema_version": "v1",
        "campaign_protocol_version": LONG_CAMPAIGN_PROTOCOL_VERSION,
        "campaign_id": row.get("campaign_id"),
        "benchmark_id": row.get("benchmark_id"),
        "run_index": row.get("run_index"),
        "run_id": row.get("run_id"),
        "seed": row.get("seed"),
        "seed_label": row.get("seed_label"),
        "seed_cohort": row.get("seed_cohort"),
        "repetition_index": row.get("repetition_index"),
        "seat_permutation": row.get("seat_permutation"),
        "permutation_id": row.get("permutation_id"),
        "status": status,
        "error": error,
        "run_dir": str(run_dir),
        "contains_baseline": bool(row.get("contains_baseline")),
        "baseline_strategies": _dict(row.get("baseline_strategies")),
        "summary": {
            "winner_player_id": summary.get("winner_player_id") if summary else None,
            "turn_count": summary.get("turn_count") if summary else None,
            "reason": summary.get("reason") if summary else None,
            "decision_stats": summary.get("decision_stats") if summary else None,
        },
        "run_metrics": {
            "winner_player_id": run_metrics.get("winner_player_id"),
            "game_end_reason": run_metrics.get("game_end_reason"),
            "final_turn_index": run_metrics.get("final_turn_index"),
            "total_event_count": run_metrics.get("total_event_count"),
            "total_applied_action_count": run_metrics.get("total_applied_action_count"),
            "total_property_purchase_count": run_metrics.get("total_property_purchase_count"),
            "total_trade_proposed": run_metrics.get("total_trade_proposed"),
            "total_trade_accepted": run_metrics.get("total_trade_accepted"),
            "total_bankruptcies": run_metrics.get("total_bankruptcies"),
            "reliability_metrics": run_metrics.get("reliability_metrics"),
            "usage_metrics": run_metrics.get("usage_metrics"),
            "decision_stats": run_metrics.get("decision_stats"),
        },
        "players": _campaign_result_players(row, summary, scorecard_players),
        "usage": usage,
        "cost_report": cost_report,
        "replay_report": _compact_replay_report(replay_report),
        "state_replay_report": _compact_replay_report(state_replay_report),
        "artifact_replay_report": _compact_replay_report(artifact_replay_report),
        "trace_summary": trace_summary,
        "failure_summary": failure_summary,
        "artifact_counts": {
            "events": _jsonl_line_count(run_dir / "events.jsonl"),
            "actions": _jsonl_line_count(run_dir / "actions.jsonl"),
            "decisions": _jsonl_line_count(run_dir / "decisions.jsonl"),
            "prompts": _file_count(run_dir / "prompts"),
            "replay_steps": _jsonl_line_count(run_dir / "replay_steps.jsonl"),
            "replay_flags": _jsonl_line_count(run_dir / "replay_flags.jsonl"),
            "review_queue": _jsonl_line_count(run_dir / "review_queue.jsonl"),
        },
        "prompt_pipeline": _prompt_marker(
            "Campaign result extraction reads completed artifacts only; it does not alter model-facing payloads."
        ),
    }


def _campaign_result_players(
    row: dict[str, Any],
    summary: dict[str, Any],
    scorecard_players: Any,
) -> list[dict[str, Any]]:
    by_player = _scorecard_players_by_id(scorecard_players)
    summary_players = _dict(summary.get("players")) if summary else {}
    results: list[dict[str, Any]] = []
    for actor in _list(row.get("actors")):
        player_id = str(actor.get("player_id"))
        score = _dict(by_player.get(player_id))
        summary_player = _dict(summary_players.get(player_id))
        net_worth = _first_number(score.get("final_net_worth_estimate"), summary_player.get("net_worth_estimate"))
        results.append(
            {
                "player_id": player_id,
                "seat_index": actor.get("seat_index"),
                "actor_id": actor.get("actor_id"),
                "actor_type": actor.get("actor_type"),
                "display_name": actor.get("display_name"),
                "openrouter_model_id": actor.get("openrouter_model_id"),
                "baseline_id": actor.get("baseline_id"),
                "roster_actor_ref": actor.get("roster_actor_ref"),
                "final_rank": score.get("final_rank"),
                "winner": bool(score.get("winner", player_id == summary.get("winner_player_id"))),
                "bankrupt": bool(score.get("bankrupt", summary_player.get("bankrupt", False))),
                "turns_played": _first_number(score.get("turns_played"), summary_player.get("turns_played")),
                "turns_survived": _first_number(score.get("turns_survived"), summary_player.get("turns_played")),
                "final_cash": _first_number(score.get("final_cash"), summary_player.get("cash")),
                "final_net_worth_estimate": net_worth,
                "primary_score": _first_number(score.get("primary_score"), net_worth),
                "opponents_bankrupted": _first_number(score.get("opponents_bankrupted")),
                "final_property_count": _first_number(score.get("final_property_count")),
                "final_complete_color_group_count": _first_number(score.get("final_complete_color_group_count")),
                "final_developed_monopoly_count": _first_number(score.get("final_developed_monopoly_count")),
                "rent_collected": _first_number(score.get("rent_collected")),
                "rent_paid": _first_number(score.get("rent_paid")),
                "net_rent_flow": _first_number(score.get("net_rent_flow")),
                "trades_proposed": _first_number(score.get("trades_proposed")),
                "trades_accepted": _first_number(score.get("trades_accepted")),
                "decision_count": _first_number(score.get("decision_count")),
                "valid_first_response_rate": _first_number(score.get("valid_first_response_rate")),
                "retry_rate": _first_number(score.get("retry_rate")),
                "fallback_rate": _first_number(score.get("fallback_rate")),
                "total_input_tokens": _first_number(score.get("total_input_tokens")),
                "total_output_tokens": _first_number(score.get("total_output_tokens")),
                "total_reasoning_tokens": _first_number(score.get("total_reasoning_tokens")),
                "total_cached_tokens": _first_number(score.get("total_cached_tokens")),
                "total_tokens": _first_number(score.get("total_tokens")),
                "total_cost": _first_number(score.get("total_cost")),
                "cost_per_decision": _first_number(score.get("cost_per_decision")),
                "cost_per_turn_survived": _first_number(score.get("cost_per_turn_survived")),
                "cost_per_net_worth_point": _first_number(score.get("cost_per_net_worth_point")),
                "score_matrix": score.get("score_matrix"),
            }
        )
    if any(player.get("final_rank") is None for player in results):
        _fill_missing_ranks(results)
    return results


def _write_campaign_dynamic_artifacts(
    paths: dict[str, Path],
    config: dict[str, Any],
    plan: dict[str, Any],
    run_entries: list[dict[str, Any]],
) -> None:
    results = {"schema_version": "v1", "runs": run_entries}
    leaderboard = _leaderboard_payload(config, run_entries)
    statistics = _statistics_payload(config, plan, run_entries)
    baseline_comparison = _baseline_comparison_payload(config, run_entries, leaderboard)

    _write_jsonl(paths["results"], run_entries)
    _write_csv(paths["results_csv"], _results_csv_rows(run_entries))
    _write_json(paths["run_results"], results)
    _write_json(paths["leaderboard"], leaderboard)
    _write_csv(paths["leaderboard_csv"], _leaderboard_csv_rows(leaderboard))
    _write_json(paths["statistics"], statistics)
    _write_json(paths["baseline_comparison"], baseline_comparison)
    paths["paper_report"].parent.mkdir(parents=True, exist_ok=True)
    paths["paper_report"].write_text(
        _paper_report_markdown(config, plan, run_entries, leaderboard, statistics, baseline_comparison),
        encoding="utf-8",
    )
    _write_json(paths["execution_result"], _execution_result_payload(config, paths, run_entries))
    manifest = {
        **plan["campaign_manifest"],
        "planning_only": False,
        "execution_status": _campaign_execution_status(run_entries),
        "completed_run_count": sum(1 for entry in run_entries if entry["status"] in {"completed", "resumed_completed"}),
        "failed_run_count": sum(1 for entry in run_entries if entry["status"] == "failed"),
        "skipped_run_count": sum(
            1 for entry in run_entries if entry["status"] in {"not_runnable", "not_started_max_runs_limit"}
        ),
        "artifacts": [
            "campaign_config.json",
            "campaign_manifest.json",
            "seed_manifest.json",
            "model_roster.json",
            "baseline_roster.json",
            "run_matrix.json",
            "run_matrix.jsonl",
            "results.jsonl",
            "results.csv",
            "run_results.json",
            "leaderboard.json",
            "leaderboard.csv",
            "statistics.json",
            "baseline_comparison.json",
            "paper_report.md",
            "execution_result.json",
            "batch_runner_compatibility.json",
            "artifact_manifest.json",
        ],
        "prompt_pipeline": _prompt_marker(
            "Campaign execution/reporting adds research artifacts only; LLM prompt payloads remain unchanged."
        ),
    }
    _write_json(paths["campaign_manifest"], manifest)
    _write_json(paths["artifact_manifest"], _artifact_manifest(paths))


def _leaderboard_payload(config: dict[str, Any], run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    rows = _completed_actor_rows(run_entries)
    by_actor: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_actor.setdefault(str(row["actor_id"]), []).append(row)
    leaderboard_rows: list[dict[str, Any]] = []
    for actor_id, actor_rows in sorted(by_actor.items()):
        net_worth = [_number(row.get("final_net_worth_estimate")) for row in actor_rows]
        ranks = [_number(row.get("final_rank")) for row in actor_rows]
        costs = [_number(row.get("total_cost")) for row in actor_rows]
        tokens = [_number(row.get("total_tokens")) for row in actor_rows]
        fallbacks = [_number(row.get("fallback_rate")) for row in actor_rows]
        retries = [_number(row.get("retry_rate")) for row in actor_rows]
        turns = [_number(row.get("turns_survived")) for row in actor_rows]
        wins = sum(1 for row in actor_rows if row.get("winner"))
        bankruptcies = sum(1 for row in actor_rows if row.get("bankrupt"))
        metadata = actor_rows[0]
        row_payload = {
            "actor_id": actor_id,
            "actor_type": metadata.get("actor_type"),
            "display_name": metadata.get("display_name"),
            "openrouter_model_ids": _unique(row.get("openrouter_model_id") for row in actor_rows),
            "baseline_ids": _unique(row.get("baseline_id") for row in actor_rows),
            "game_count": len(actor_rows),
            "win_count": wins,
            "win_rate": _rate(wins, len(actor_rows)),
            "bankruptcy_count": bankruptcies,
            "bankruptcy_rate": _rate(bankruptcies, len(actor_rows)),
            "final_net_worth": _numeric_stats(net_worth),
            "final_rank": _numeric_stats(ranks),
            "turns_survived": _numeric_stats(turns),
            "total_cost": _numeric_stats(costs),
            "total_tokens": _numeric_stats(tokens),
            "fallback_rate": _numeric_stats(fallbacks),
            "retry_rate": _numeric_stats(retries),
            "average_cost_per_game": round(sum(costs) / len(costs), 10) if costs else None,
            "average_tokens_per_game": round(sum(tokens) / len(tokens), 4) if tokens else None,
            "average_final_net_worth": round(mean(net_worth), 4) if net_worth else None,
            "average_final_rank": round(mean(ranks), 4) if ranks else None,
        }
        leaderboard_rows.append(row_payload)
    leaderboard_rows.sort(
        key=lambda row: (
            row.get("win_rate") or 0,
            row.get("average_final_net_worth") or -10**9,
            -(row.get("average_final_rank") or 10**9),
        ),
        reverse=True,
    )
    for index, row in enumerate(leaderboard_rows, start=1):
        row["leaderboard_rank"] = index
    return {
        "schema_version": "v1",
        "leaderboard_version": "long_horizon_leaderboard_v1",
        "campaign_id": config["campaign_id"],
        "primary_score": "final_net_worth_estimate",
        "ranking_note": "Rows sort by win rate, average final net worth, then average final rank.",
        "rows": leaderboard_rows,
        "prompt_pipeline": _prompt_marker("Leaderboard is post-hoc and not model-facing."),
    }


def _statistics_payload(
    config: dict[str, Any],
    plan: dict[str, Any],
    run_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    completed = [entry for entry in run_entries if entry["status"] in {"completed", "resumed_completed"}]
    run_turns = [_number(entry["summary"].get("turn_count")) for entry in completed]
    run_costs = [_number(_nested(entry, ("run_metrics", "usage_metrics", "total_cost"))) for entry in completed]
    run_decisions = [
        _number(_nested(entry, ("run_metrics", "decision_stats", "total_resolved"))) for entry in completed
    ]
    run_fallbacks = [
        _number(_nested(entry, ("run_metrics", "reliability_metrics", "fallback_rate"))) for entry in completed
    ]
    return {
        "schema_version": "v1",
        "statistics_version": "long_horizon_campaign_statistics_v1",
        "campaign_id": config["campaign_id"],
        "planned_run_count": len(plan["run_matrix"]),
        "recorded_run_count": len(run_entries),
        "status_counts": _status_counts(run_entries),
        "completed_run_count": len(completed),
        "execution_coverage": _rate(len(completed), len(plan["run_matrix"])),
        "run_level": {
            "turn_count": _numeric_stats(run_turns),
            "resolved_decision_count": _numeric_stats(run_decisions),
            "fallback_rate": _numeric_stats(run_fallbacks),
            "total_cost": _numeric_stats(run_costs),
        },
        "by_seed": _by_seed_stats(run_entries),
        "seat_effects": _seat_effect_stats(run_entries),
        "failure_taxonomy": _failure_taxonomy_aggregate(run_entries),
        "replay_verification": _replay_verification_aggregate(run_entries),
        "prompt_pipeline": _prompt_marker("Statistics are derived after execution and are not included in prompts."),
    }


def _baseline_comparison_payload(
    config: dict[str, Any],
    run_entries: list[dict[str, Any]],
    leaderboard: dict[str, Any],
) -> dict[str, Any]:
    baseline_rows = [row for row in leaderboard.get("rows", []) if row.get("actor_type") == "baseline"]
    baseline_net_worth_values = [
        _number(row.get("average_final_net_worth")) for row in baseline_rows if row.get("average_final_net_worth") is not None
    ]
    baseline_mean = round(mean(baseline_net_worth_values), 4) if baseline_net_worth_values else None
    rows: list[dict[str, Any]] = []
    for row in leaderboard.get("rows", []):
        avg_net_worth = _number(row.get("average_final_net_worth"))
        total_cost = _nested(row, ("total_cost", "mean"))
        baseline_normalized = (
            round(avg_net_worth / baseline_mean, 6)
            if isinstance(baseline_mean, (int, float)) and baseline_mean != 0
            else None
        )
        rows.append(
            {
                "actor_id": row.get("actor_id"),
                "actor_type": row.get("actor_type"),
                "display_name": row.get("display_name"),
                "game_count": row.get("game_count"),
                "win_rate": row.get("win_rate"),
                "average_final_net_worth": avg_net_worth,
                "average_final_rank": row.get("average_final_rank"),
                "baseline_normalized_net_worth": baseline_normalized,
                "average_total_cost": total_cost,
                "net_worth_per_dollar": (
                    round(avg_net_worth / float(total_cost), 6)
                    if isinstance(total_cost, (int, float)) and total_cost > 0 and avg_net_worth is not None
                    else None
                ),
            }
        )
    return {
        "schema_version": "v1",
        "baseline_comparison_version": "long_horizon_baseline_comparison_v1",
        "campaign_id": config["campaign_id"],
        "baseline_actor_count": len(baseline_rows),
        "baseline_mean_final_net_worth": baseline_mean,
        "rows": rows,
        "note": "Use baseline-normalized values only when the selected roster contains deterministic baseline actors.",
        "prompt_pipeline": _prompt_marker("Baseline comparison is computed from artifacts only."),
    }


def _execution_result_payload(
    config: dict[str, Any],
    paths: dict[str, Path],
    run_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "campaign_id": config["campaign_id"],
        "status": _campaign_execution_status(run_entries),
        "run_count": len(run_entries),
        "completed_count": sum(1 for entry in run_entries if entry["status"] in {"completed", "resumed_completed"}),
        "failed_count": sum(1 for entry in run_entries if entry["status"] == "failed"),
        "campaign_dir": str(paths["campaign_dir"]),
        "artifacts": {
            "results": str(paths["results"]),
            "run_results": str(paths["run_results"]),
            "leaderboard": str(paths["leaderboard"]),
            "statistics": str(paths["statistics"]),
            "baseline_comparison": str(paths["baseline_comparison"]),
            "paper_report": str(paths["paper_report"]),
        },
        "prompt_pipeline": _prompt_marker("Execution status artifact is post-hoc and not model-facing."),
    }


def _runnable_with_current_batch_runner(actors: list[dict[str, Any]]) -> bool:
    return all(actor["actor_type"] == "llm" and bool(actor["enabled"]) for actor in actors)


def _runnable_with_long_runner(actors: list[dict[str, Any]]) -> bool:
    for actor in actors:
        if actor["actor_type"] == "llm" and bool(actor["enabled"]):
            continue
        if actor["actor_type"] == "baseline" and actor.get("baseline_id") in BASELINE_IDS:
            continue
        return False
    return True


def _baseline_strategies(actors: list[dict[str, Any]]) -> dict[str, str]:
    return {
        str(actor["player_id"]): str(actor["baseline_id"])
        for actor in actors
        if actor["actor_type"] == "baseline" and actor.get("baseline_id")
    }


def _run_id(
    *,
    campaign_id: str,
    seed: int,
    repetition_index: int,
    permutation_id: str,
    max_turns: int,
    actors: list[dict[str, Any]],
    run_index: int,
) -> str:
    digest = _sha256_short(
        {
            "campaign_id": campaign_id,
            "seed": seed,
            "repetition_index": repetition_index,
            "permutation_id": permutation_id,
            "max_turns": max_turns,
            "actors": [
                {
                    "seat_index": actor["seat_index"],
                    "actor_id": actor["actor_id"],
                    "roster_slot_index": actor["roster_slot_index"],
                    "actor_type": actor["actor_type"],
                }
                for actor in actors
            ],
        }
    )
    return f"{_safe_id(campaign_id)}-{run_index:04d}-{seed}-{digest}"


def _resume_key(
    config: dict[str, Any],
    seed: int,
    repetition_index: int,
    permutation_id: str,
    actors: list[dict[str, Any]],
) -> str:
    return _sha256_short(
        {
            "benchmark_id": config["benchmark_id"],
            "campaign_id": config["campaign_id"],
            "seed": seed,
            "repetition_index": repetition_index,
            "permutation_id": permutation_id,
            "max_turns": config["max_turns"],
            "actors": [
                {
                    "seat_index": actor["seat_index"],
                    "roster_actor_ref": actor["roster_actor_ref"],
                    "actor_type": actor["actor_type"],
                }
                for actor in actors
            ],
        },
        length=16,
    )


def _artifact_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    campaign_dir = paths["campaign_dir"]
    artifacts: list[dict[str, Any]] = []
    for label, path in sorted(paths.items()):
        if label in {"campaign_dir", "artifact_manifest"}:
            continue
        entry: dict[str, Any] = {
            "label": label,
            "path": str(path),
            "relative_path": _relative_path(campaign_dir, path),
            "exists": path.exists(),
        }
        if path.exists() and path.is_file():
            data = path.read_bytes()
            entry["bytes"] = len(data)
            entry["sha256"] = hashlib.sha256(data).hexdigest()
        artifacts.append(entry)
    return {
        "schema_version": "v1",
        "manifest_version": "long_horizon_campaign_artifact_manifest_v1",
        "campaign_dir": str(campaign_dir),
        "artifacts": artifacts,
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Artifact inventory is post-hoc and does not affect prompts.",
        },
    }


def _completed_actor_rows(run_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in run_entries:
        if entry.get("status") not in {"completed", "resumed_completed"}:
            continue
        for player in _list(entry.get("players")):
            row = {
                **player,
                "campaign_id": entry.get("campaign_id"),
                "run_id": entry.get("run_id"),
                "run_index": entry.get("run_index"),
                "seed": entry.get("seed"),
                "repetition_index": entry.get("repetition_index"),
                "permutation_id": entry.get("permutation_id"),
                "turn_count": _nested(entry, ("summary", "turn_count")),
                "game_end_reason": _nested(entry, ("summary", "reason")),
            }
            rows.append(row)
    return rows


def _by_seed_stats(run_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for entry in run_entries:
        seed = entry.get("seed")
        if isinstance(seed, int):
            by_seed.setdefault(seed, []).append(entry)
    rows: list[dict[str, Any]] = []
    for seed, entries in sorted(by_seed.items()):
        completed = [entry for entry in entries if entry.get("status") in {"completed", "resumed_completed"}]
        winner_actor_counts: dict[str, int] = {}
        net_worth_values: list[float] = []
        for entry in completed:
            winner = _nested(entry, ("summary", "winner_player_id"))
            for player in _list(entry.get("players")):
                if player.get("player_id") == winner:
                    _increment(winner_actor_counts, str(player.get("actor_id")))
                net_worth_values.append(_number(player.get("final_net_worth_estimate")))
        rows.append(
            {
                "seed": seed,
                "run_count": len(entries),
                "completed_count": len(completed),
                "winner_actor_counts": winner_actor_counts,
                "final_net_worth": _numeric_stats(net_worth_values),
            }
        )
    return rows


def _seat_effect_stats(run_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in _completed_actor_rows(run_entries):
        actor_id = row.get("actor_id")
        seat_index = row.get("seat_index")
        if actor_id is None or not isinstance(seat_index, int):
            continue
        groups.setdefault((str(actor_id), seat_index), []).append(row)
    results: list[dict[str, Any]] = []
    for (actor_id, seat_index), rows in sorted(groups.items()):
        net_worth = [_number(row.get("final_net_worth_estimate")) for row in rows]
        ranks = [_number(row.get("final_rank")) for row in rows]
        wins = sum(1 for row in rows if row.get("winner"))
        results.append(
            {
                "actor_id": actor_id,
                "seat_index": seat_index,
                "game_count": len(rows),
                "win_rate": _rate(wins, len(rows)),
                "final_net_worth": _numeric_stats(net_worth),
                "final_rank": _numeric_stats(ranks),
            }
        )
    return results


def _failure_taxonomy_aggregate(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    review_required = 0
    total = 0
    for entry in run_entries:
        summary = _dict(entry.get("failure_summary"))
        total += int(summary.get("total_findings") or 0)
        review_required += int(summary.get("review_required") or 0)
        for key, value in _dict(summary.get("by_finding_type") or summary.get("by_type")).items():
            _increment(by_type, str(key), int(value or 0))
        for key, value in _dict(summary.get("by_severity")).items():
            _increment(by_severity, str(key), int(value or 0))
    return {
        "total_findings": total,
        "review_required": review_required,
        "by_finding_type": by_type,
        "by_severity": by_severity,
    }


def _replay_verification_aggregate(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    state_status_counts: dict[str, int] = {}
    artifact_status_counts: dict[str, int] = {}
    mismatch_count = 0
    for entry in run_entries:
        report = _dict(entry.get("replay_report"))
        status = str(report.get("status") or "missing")
        state_report = _dict(entry.get("state_replay_report"))
        artifact_report = _dict(entry.get("artifact_replay_report"))
        state_status = str(report.get("state_status") or state_report.get("status") or "missing")
        artifact_status = str(report.get("artifact_status") or artifact_report.get("status") or "missing")
        _increment(status_counts, status)
        _increment(state_status_counts, state_status)
        _increment(artifact_status_counts, artifact_status)
        if status not in {"ok", "passed"}:
            mismatch_count += 1 if report else 0
    return {
        "status_counts": status_counts,
        "state_status_counts": state_status_counts,
        "artifact_status_counts": artifact_status_counts,
        "non_ok_report_count": mismatch_count,
    }


def _campaign_execution_status(run_entries: list[dict[str, Any]]) -> str:
    if not run_entries:
        return "not_started"
    status_counts = _status_counts(run_entries)
    if status_counts.get("failed"):
        return "partial_with_failures"
    if status_counts.get("not_runnable") or status_counts.get("not_started_max_runs_limit"):
        return "partial"
    return "completed"


def _results_csv_rows(run_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in run_entries:
        players = _list(entry.get("players"))
        if not players:
            rows.append(
                {
                    "run_id": entry.get("run_id"),
                    "run_index": entry.get("run_index"),
                    "seed": entry.get("seed"),
                    "status": entry.get("status"),
                    "player_id": None,
                    "actor_id": None,
                    "actor_type": None,
                    "seat_index": None,
                    "final_rank": None,
                    "winner": None,
                    "final_net_worth_estimate": None,
                    "total_cost": None,
                    "total_tokens": None,
                }
            )
            continue
        for player in players:
            rows.append(
                {
                    "run_id": entry.get("run_id"),
                    "run_index": entry.get("run_index"),
                    "seed": entry.get("seed"),
                    "status": entry.get("status"),
                    "player_id": player.get("player_id"),
                    "actor_id": player.get("actor_id"),
                    "actor_type": player.get("actor_type"),
                    "seat_index": player.get("seat_index"),
                    "final_rank": player.get("final_rank"),
                    "winner": player.get("winner"),
                    "final_net_worth_estimate": player.get("final_net_worth_estimate"),
                    "turns_survived": player.get("turns_survived"),
                    "decision_count": player.get("decision_count"),
                    "fallback_rate": player.get("fallback_rate"),
                    "retry_rate": player.get("retry_rate"),
                    "total_cost": player.get("total_cost"),
                    "total_tokens": player.get("total_tokens"),
                }
            )
    return rows


def _leaderboard_csv_rows(leaderboard: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _list(leaderboard.get("rows")):
        rows.append(
            {
                "leaderboard_rank": row.get("leaderboard_rank"),
                "actor_id": row.get("actor_id"),
                "actor_type": row.get("actor_type"),
                "display_name": row.get("display_name"),
                "game_count": row.get("game_count"),
                "win_rate": row.get("win_rate"),
                "average_final_net_worth": row.get("average_final_net_worth"),
                "average_final_rank": row.get("average_final_rank"),
                "average_cost_per_game": row.get("average_cost_per_game"),
                "average_tokens_per_game": row.get("average_tokens_per_game"),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8")


def _paper_report_markdown(
    config: dict[str, Any],
    plan: dict[str, Any],
    run_entries: list[dict[str, Any]],
    leaderboard: dict[str, Any],
    statistics: dict[str, Any],
    baseline_comparison: dict[str, Any],
) -> str:
    completed_count = statistics["completed_run_count"]
    lines = [
        "# Long-Horizon Economic Agency In Monopoly Campaign Report",
        "",
        "## Prompt Invariant",
        "",
        (
            "This campaign report is generated from post-hoc run artifacts only. It does not change "
            "prompt text, prompt structure, tool schemas, retry wording, or any model-facing content."
        ),
        "",
        "## Campaign Configuration",
        "",
        _markdown_table(
            [
                ("Campaign ID", config["campaign_id"]),
                ("Benchmark", config["benchmark_id"]),
                ("Seed cohort", config["seed_cohort"]),
                ("Model roster", config["model_roster"]),
                ("Repetitions per seed", config["repetitions_per_seed"]),
                ("Seat permutation", config["seat_permutation"]),
                ("Max turns", config["max_turns"]),
                ("Planned runs", len(plan["run_matrix"])),
                ("Completed runs", completed_count),
                ("Execution status", statistics["status_counts"]),
            ],
            headers=("Field", "Value"),
        ),
        "",
        "## Leaderboard",
        "",
        _leaderboard_markdown_table(leaderboard),
        "",
        "## Baseline Comparison",
        "",
        _baseline_markdown_table(baseline_comparison),
        "",
        "## Statistical Summary",
        "",
        _markdown_table(
            [
                ("Turn count", statistics["run_level"]["turn_count"]),
                ("Resolved decisions", statistics["run_level"]["resolved_decision_count"]),
                ("Fallback rate", statistics["run_level"]["fallback_rate"]),
                ("Total cost", statistics["run_level"]["total_cost"]),
            ],
            headers=("Metric", "Summary"),
        ),
        "",
        "## Failure Taxonomy",
        "",
        _markdown_table(
            [
                ("Total findings", statistics["failure_taxonomy"]["total_findings"]),
                ("Review required", statistics["failure_taxonomy"]["review_required"]),
                ("By finding type", statistics["failure_taxonomy"]["by_finding_type"]),
                ("By severity", statistics["failure_taxonomy"]["by_severity"]),
            ],
            headers=("Metric", "Value"),
        ),
        "",
        "## Replay Verification",
        "",
        _markdown_table(
            [
                ("Status counts", statistics["replay_verification"]["status_counts"]),
                ("State status counts", statistics["replay_verification"]["state_status_counts"]),
                ("Artifact status counts", statistics["replay_verification"]["artifact_status_counts"]),
                ("Non-ok reports", statistics["replay_verification"]["non_ok_report_count"]),
            ],
            headers=("Metric", "Value"),
        ),
        "",
        "## Representative Runs",
        "",
        _representative_runs_markdown(run_entries),
        "",
        "## Limitations",
        "",
        (
            "Treat this report as a campaign artifact, not a final paper result. It records fixed seeds, "
            "seat assignments, baselines, scorecards, replay checks, and trace summaries, but human analysis "
            "is still required for qualitative claims about negotiation, deception, safety, and strategic intent."
        ),
        "",
    ]
    return "\n".join(lines)


def _leaderboard_markdown_table(leaderboard: dict[str, Any]) -> str:
    rows = []
    for row in _list(leaderboard.get("rows"))[:20]:
        rows.append(
            (
                row.get("leaderboard_rank"),
                row.get("actor_id"),
                row.get("actor_type"),
                row.get("game_count"),
                row.get("win_rate"),
                row.get("average_final_net_worth"),
                row.get("average_final_rank"),
                row.get("average_cost_per_game"),
            )
        )
    return _markdown_table(
        rows,
        headers=(
            "Rank",
            "Actor",
            "Type",
            "Games",
            "Win Rate",
            "Avg Net Worth",
            "Avg Rank",
            "Avg Cost",
        ),
    )


def _baseline_markdown_table(baseline_comparison: dict[str, Any]) -> str:
    rows = []
    for row in _list(baseline_comparison.get("rows"))[:20]:
        rows.append(
            (
                row.get("actor_id"),
                row.get("actor_type"),
                row.get("win_rate"),
                row.get("average_final_net_worth"),
                row.get("baseline_normalized_net_worth"),
                row.get("net_worth_per_dollar"),
            )
        )
    return _markdown_table(
        rows,
        headers=("Actor", "Type", "Win Rate", "Avg Net Worth", "Baseline Norm", "Net Worth / $"),
    )


def _representative_runs_markdown(run_entries: list[dict[str, Any]]) -> str:
    completed = [entry for entry in run_entries if entry.get("status") in {"completed", "resumed_completed"}]
    if not completed:
        return "No completed runs are available yet."
    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in completed:
        best = max(
            (_number(player.get("final_net_worth_estimate")) for player in _list(entry.get("players"))),
            default=float("-inf"),
        )
        scored.append((best, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    best_entry = scored[0][1]
    worst_entry = scored[-1][1]
    return _markdown_table(
        [
            ("Highest winning/net-worth run", best_entry.get("run_id"), best_entry.get("run_dir")),
            ("Lowest winning/net-worth run", worst_entry.get("run_id"), worst_entry.get("run_dir")),
        ],
        headers=("Label", "Run ID", "Run Directory"),
    )


def _markdown_table(rows: list[Any], *, headers: tuple[str, ...]) -> str:
    normalized = [tuple(_format_markdown_cell(value) for value in row) for row in rows]
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in normalized]
    return "\n".join([header, divider, *body])


def _format_markdown_cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _numeric_stats(values: list[float]) -> dict[str, Any]:
    filtered = [value for value in values if math.isfinite(value)]
    if not filtered:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "stdev": None,
            "ci95": None,
        }
    return {
        "count": len(filtered),
        "mean": round(mean(filtered), 6),
        "median": round(median(filtered), 6),
        "min": round(min(filtered), 6),
        "max": round(max(filtered), 6),
        "stdev": round(stdev(filtered), 6) if len(filtered) > 1 else 0.0,
        "ci95": _bootstrap_mean_ci(filtered),
    }


def _bootstrap_mean_ci(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"method": "deterministic_bootstrap_mean", "lower": None, "upper": None, "resamples": 0}
    if len(values) == 1:
        value = round(values[0], 6)
        return {"method": "deterministic_bootstrap_mean", "lower": value, "upper": value, "resamples": 1}
    resamples = 500
    rng = random.Random(_deterministic_int({"bootstrap_values": [round(value, 6) for value in values]}))
    means = []
    for _ in range(resamples):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(mean(sample))
    means.sort()
    return {
        "method": "deterministic_bootstrap_mean",
        "lower": round(_percentile(means, 0.025), 6),
        "upper": round(_percentile(means, 0.975), 6),
        "resamples": resamples,
    }


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return values[low]
    weight = position - low
    return values[low] * (1 - weight) + values[high] * weight


def _status_counts(run_entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in run_entries:
        _increment(counts, str(entry.get("status") or "unknown"))
    return counts


def _scorecard_players_by_id(scorecard_players: Any) -> dict[str, dict[str, Any]]:
    if isinstance(scorecard_players, list):
        return {
            str(player["player_id"]): player
            for player in scorecard_players
            if isinstance(player, dict) and player.get("player_id")
        }
    if isinstance(scorecard_players, dict):
        return {
            str(player_id): player
            for player_id, player in scorecard_players.items()
            if isinstance(player, dict)
        }
    return {}


def _compact_replay_report(report: dict[str, Any]) -> dict[str, Any]:
    if not report:
        return {}
    return {
        "status": report.get("status"),
        "state_status": report.get("state_status"),
        "artifact_status": report.get("artifact_status"),
        "comparison_scope": report.get("comparison_scope"),
        "canonicalization": report.get("canonicalization"),
        "first_mismatch_index": report.get("first_mismatch_index"),
        "matched": report.get("matched"),
        "mismatch_count": report.get("mismatch_count"),
        "diff_path": report.get("diff_path"),
        "event_hashes_path": report.get("event_hashes_path"),
    }


def _fill_missing_ranks(players: list[dict[str, Any]]) -> None:
    ranked = sorted(
        players,
        key=lambda player: (
            bool(player.get("winner")),
            _number(player.get("final_net_worth_estimate")),
            _number(player.get("final_cash")),
        ),
        reverse=True,
    )
    for index, player in enumerate(ranked, start=1):
        if player.get("final_rank") is None:
            player["final_rank"] = index


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_json_value(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _jsonl_line_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def _file_count(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file())


def _nested(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_number(*values: Any) -> float | int | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float) and math.isfinite(value):
            return value
    return None


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return 0.0


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 6)


def _unique(values: Any) -> list[Any]:
    seen: set[str] = set()
    out: list[Any] = []
    for value in values:
        if value is None:
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=True)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _increment(mapping: dict[str, int], key: str, amount: int = 1) -> None:
    mapping[key] = mapping.get(key, 0) + amount


def _prompt_marker(note: str) -> dict[str, str]:
    return {
        "status": "unchanged",
        "note": note,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _deterministic_int(payload: dict[str, Any]) -> int:
    return int(_sha256_short(payload, length=16), 16)


def _sha256_short(payload: dict[str, Any], *, length: int = 10) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _safe_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return safe.strip(".-") or "campaign"


def _relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan or execute a monopoly-long-v1 research campaign.")
    parser.add_argument("--config", required=True, help="Path to a long-horizon campaign config JSON file.")
    parser.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR, help="Directory where campaign artifacts are written.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force dry_run=true in the persisted campaign_config. This planner never spends model budget.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the expanded campaign matrix. Dry-run configs still require --force-execute.",
    )
    parser.add_argument(
        "--force-execute",
        action="store_true",
        help="Execute even when the config has dry_run=true.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Execute at most this many runnable cells; useful for smoke tests.",
    )
    args = parser.parse_args(argv)

    config = load_campaign_config(args.config)
    if args.dry_run:
        config["dry_run"] = True
    if args.execute:
        result = asyncio.run(
            run_campaign(
                config,
                runs_dir=args.runs_dir,
                max_runs=args.max_runs,
                force_execute=bool(args.force_execute),
            )
        )
        print(json.dumps(result, sort_keys=True))
        return 0

    campaign_dir = write_campaign_plan(config, runs_dir=args.runs_dir)
    matrix_path = campaign_dir / "run_matrix.jsonl"
    run_count = len(matrix_path.read_text(encoding="utf-8").splitlines()) if matrix_path.exists() else 0
    print(
        json.dumps(
            {
                "campaign_dir": str(campaign_dir),
                "run_count": run_count,
                "dry_run": bool(config.get("dry_run")),
                "prompt_pipeline": "unchanged",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
