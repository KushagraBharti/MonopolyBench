from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import random
import re
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

from monopoly_telemetry import build_experiment_manifest, build_review_cost_aggregate, usage_calls_jsonl

from .player_config import PlayerConfig


BATCH_PROTOCOL_VERSION = "batch_protocol_v1"
DEFAULT_BATCH_BUDGET = 50.0
DEFAULT_BATCH_CONCURRENCY = 1
DEFAULT_SEAT_MODE = "latin_square"


@dataclass(slots=True)
class BatchRunSpec:
    index: int
    seed: int
    run_id: str
    players: list[PlayerConfig]
    seat_metadata: dict[str, Any]


def build_batch_run_specs(
    *,
    batch_id: str,
    seeds: list[int],
    matches: int,
    players: list[PlayerConfig],
    seat_mode: str,
    batch_seed: int,
    max_turns: int,
    max_trade_exchanges: int,
    max_auction_actions: int,
) -> list[BatchRunSpec]:
    if not seeds:
        raise ValueError("Batch config must include a non-empty seeds list.")
    specs: list[BatchRunSpec] = []
    for index in range(matches):
        seed = seeds[index % len(seeds)]
        ordered_players, permutation_id, seed_material = _players_for_seat_mode(
            players=players,
            mode=seat_mode,
            batch_id=batch_id,
            batch_seed=batch_seed,
            game_seed=seed,
            run_index=index,
            model_ids=[player.openrouter_model_id for player in players],
            max_turns=max_turns,
            max_trade_exchanges=max_trade_exchanges,
            max_auction_actions=max_auction_actions,
        )
        run_id = generate_run_id(
            batch_id,
            index,
            seed,
            ordered_players,
            max_turns=max_turns,
            max_trade_exchanges=max_trade_exchanges,
            max_auction_actions=max_auction_actions,
            permutation_id=permutation_id,
        )
        specs.append(
            BatchRunSpec(
                index=index,
                seed=seed,
                run_id=run_id,
                players=ordered_players,
                seat_metadata={
                    "batch_id": batch_id,
                    "batch_run_index": index,
                    "permutation_mode": seat_mode,
                    "permutation_id": permutation_id,
                    "permutation_seed_material": seed_material,
                },
            )
        )
    return specs


def generate_run_id(
    batch_id: str,
    index: int,
    seed: int,
    players: list[PlayerConfig],
    *,
    max_turns: int,
    max_trade_exchanges: int,
    max_auction_actions: int,
    permutation_id: str | None = None,
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
            "permutation_id": permutation_id,
        },
        sort_keys=True,
    )
    digest = hashlib.sha1(seed_blob.encode("utf-8")).hexdigest()[:8]
    return f"{batch_id}-{index:03d}-{seed}-{digest}"


def batch_paths(runs_root: Path, batch_id: str) -> dict[str, Path]:
    batch_dir = runs_root / "batches" / batch_id
    return {
        "batch_dir": batch_dir,
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
        "experiment_manifest": batch_dir / "experiment_manifest.json",
        "review_cost_aggregate": batch_dir / "review_cost_aggregate.json",
        "review_cost_calls": batch_dir / "review_cost_calls.jsonl",
        "budget_report": batch_dir / "budget_report.json",
        "model_failure_breakdown": batch_dir / "model_failure_breakdown.json",
        "failure_leaderboard": batch_dir / "failure_leaderboard.json",
        "top_findings": batch_dir / "top_findings.jsonl",
        "model_trace_breakdown": batch_dir / "model_trace_breakdown.json",
        "failure_trace_breakdown": batch_dir / "failure_trace_breakdown.json",
        "review_queue": batch_dir / "review_queue.jsonl",
        "artifact_manifest": batch_dir / "artifact_manifest.json",
        "model_cards_dir": batch_dir / "model_cards",
    }


def normalized_batch_config(config: dict[str, Any], *, batch_id: str, runs_root: Path) -> dict[str, Any]:
    cost_budget = config.get("cost_budget", DEFAULT_BATCH_BUDGET)
    concurrency = config.get("concurrency", DEFAULT_BATCH_CONCURRENCY)
    return {
        "schema_version": "v1",
        "batch_protocol_version": BATCH_PROTOCOL_VERSION,
        "batch_id": batch_id,
        "batch_type": str(config.get("batch_type") or "full_game"),
        "seeds": [int(seed) for seed in config.get("seeds", []) if isinstance(seed, (int, float))],
        "matches": int(config.get("matches", 0)),
        "players": config.get("players"),
        "seat_permutation": str(config.get("seat_permutation") or DEFAULT_SEAT_MODE),
        "batch_seed": int(config.get("batch_seed") or 0),
        "max_turns": int(config.get("max_turns") or 200),
        "batch_artifact_dir": str(runs_root / "batches" / batch_id),
        "run_artifact_root": str(runs_root),
        "cost_budget": float(cost_budget) if isinstance(cost_budget, (int, float)) else DEFAULT_BATCH_BUDGET,
        "cost_budget_unit": str(config.get("cost_budget_unit") or "usd_openrouter_reported"),
        "budget_policy": str(config.get("budget_policy") or "stop_immediately"),
        "token_budget": config.get("token_budget"),
        "concurrency": int(concurrency) if isinstance(concurrency, (int, float)) else DEFAULT_BATCH_CONCURRENCY,
        "resume": bool(config.get("resume", True)),
        "continue_on_failure": bool(config.get("continue_on_failure", False)),
        "replay_after_run": bool(config.get("replay_after_run", True)),
        "build_scorecard_after_run": bool(config.get("build_scorecard_after_run", True)),
        "build_trace_after_run": bool(config.get("build_trace_after_run", True)),
        "build_failure_taxonomy_after_run": bool(config.get("build_failure_taxonomy_after_run", True)),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Batch orchestration does not change prompt construction, content, tools, or retry behavior.",
        },
    }


def write_batch_static_artifacts(
    *,
    paths: dict[str, Path],
    config: dict[str, Any],
    players: list[PlayerConfig],
    specs: list[BatchRunSpec],
    pricing_snapshot: dict[str, Any],
    credits_before: dict[str, Any],
) -> None:
    batch_dir = paths["batch_dir"]
    batch_dir.mkdir(parents=True, exist_ok=True)
    paths["model_cards_dir"].mkdir(parents=True, exist_ok=True)
    _write_json(paths["batch_config"], config)
    _write_json(paths["model_config"], _model_config(players))
    _write_json(
        paths["experiment_manifest"],
        build_experiment_manifest(
            experiment_id=str(config.get("batch_id") or "batch"),
            benchmark_tracks=["full_game"],
            models=_model_config(players)["models"],
            reasoning_policy=None,
            batch_type=str(config.get("batch_type") or "full_game"),
            run_count=len(specs),
        ),
    )
    _write_json(paths["seed_manifest"], _seed_manifest(config, specs))
    _write_json(paths["seat_manifest"], _seat_manifest(config, specs))
    _write_json(paths["model_pricing_snapshot"], pricing_snapshot)
    _write_json(paths["budget_report"], _budget_report(config, [], credits_before=credits_before))


def write_batch_dynamic_artifacts(
    *,
    paths: dict[str, Path],
    config: dict[str, Any],
    run_entries: list[dict[str, Any]],
    credits_before: dict[str, Any],
    credits_after: dict[str, Any],
    budget_stop_reason: str | None,
) -> None:
    batch_dir = paths["batch_dir"]
    batch_dir.mkdir(parents=True, exist_ok=True)
    _write_json(paths["run_index"], {"schema_version": "v1", "runs": run_entries})
    _write_jsonl(paths["run_index_jsonl"], run_entries)
    results = [_result_entry(entry) for entry in run_entries]
    _write_jsonl(paths["results"], results)
    leaderboard = _leaderboard(run_entries)
    model_cards = _write_model_cards(paths["model_cards_dir"], run_entries, leaderboard)
    _write_json(paths["leaderboard"], leaderboard)
    _write_json(paths["scorecard_summary"], _scorecard_summary(run_entries, leaderboard))
    _write_json(paths["category_breakdown"], _category_breakdown(run_entries))
    _write_json(paths["statistical_summary"], _statistical_summary(run_entries))
    _write_json(paths["replay_report"], _batch_replay_report(run_entries))
    _write_json(paths["trace_summary"], _batch_trace_summary(run_entries))
    _write_json(paths["failure_summary"], _batch_failure_summary(run_entries))
    _write_json(paths["cost_report"], _batch_cost_report(run_entries))
    _write_json(paths["token_report"], _batch_token_report(run_entries))
    _write_json(paths["usage_summary"], _batch_usage_summary(run_entries))
    review_cost_aggregate = build_review_cost_aggregate(
        batch_id=str(config.get("batch_id") or "batch"),
        batch_type=str(config.get("batch_type") or "full_game"),
        entries=run_entries,
    )
    _write_json(paths["review_cost_aggregate"], review_cost_aggregate)
    _write_jsonl(paths["review_cost_calls"], usage_calls_jsonl(review_cost_aggregate))
    _write_json(paths["model_failure_breakdown"], _model_failure_breakdown(run_entries))
    _write_json(paths["failure_leaderboard"], _failure_leaderboard(run_entries))
    _write_jsonl(paths["top_findings"], _top_findings(run_entries))
    _write_json(paths["model_trace_breakdown"], _model_trace_breakdown(run_entries))
    _write_json(paths["failure_trace_breakdown"], _failure_trace_breakdown(run_entries))
    _write_json(
        paths["budget_report"],
        _budget_report(
            config,
            run_entries,
            credits_before=credits_before,
            credits_after=credits_after,
            stop_reason=budget_stop_reason,
        ),
    )
    _write_jsonl(paths["review_queue"], _batch_review_queue(run_entries))
    _write_json(paths["batch_manifest"], _batch_manifest(config, run_entries, paths, model_cards))
    _write_json(paths["artifact_manifest"], _artifact_manifest(paths))


def build_run_entry(
    *,
    spec: BatchRunSpec,
    run_dir: Path,
    status: str,
    error: str | None = None,
) -> dict[str, Any]:
    summary = _read_json(run_dir / "summary.json")
    scorecard = _read_json(run_dir / "scorecard.json")
    usage = _read_json(run_dir / "usage.json")
    cost_report = _read_json(run_dir / "cost_report.json")
    replay_report = _read_json(run_dir / "replay_report.json")
    state_replay_report = _read_json(run_dir / "state_replay_report.json")
    artifact_replay_report = _read_json(run_dir / "artifact_replay_report.json")
    trace_summary = _read_json(run_dir / "trace_summary.json")
    failure_summary = _read_json(run_dir / "failure_summary.json")
    seat_assignment = _read_json(run_dir / "seat_assignment.json")
    return {
        "schema_version": "v1",
        "batch_protocol_version": BATCH_PROTOCOL_VERSION,
        "run_index": spec.index,
        "run_id": spec.run_id,
        "seed": spec.seed,
        "status": status,
        "error": error,
        "run_dir": str(run_dir),
        "seat_assignment": seat_assignment,
        "summary": {
            "winner_player_id": summary.get("winner_player_id"),
            "turn_count": summary.get("turn_count"),
            "reason": summary.get("reason"),
        },
        "scorecard": scorecard,
        "usage": usage,
        "cost_report": cost_report,
        "replay_report": replay_report,
        "state_replay_report": state_replay_report,
        "artifact_replay_report": artifact_replay_report,
        "trace_summary": trace_summary,
        "failure_summary": failure_summary,
    }


def batch_actual_cost(run_entries: list[dict[str, Any]]) -> float:
    total = 0.0
    for entry in run_entries:
        value = _run_actual_cost(entry)
        if isinstance(value, (int, float)):
            total += float(value)
    return round(total, 10)


def batch_actual_tokens(run_entries: list[dict[str, Any]]) -> int:
    total = 0
    for entry in run_entries:
        value = _run_actual_tokens(entry)
        if isinstance(value, int):
            total += value
    return total


def _run_actual_cost(entry: dict[str, Any]) -> float | None:
    cost_report = _dict(entry.get("cost_report"))
    value = cost_report.get("total_actual_cost")
    return float(value) if isinstance(value, (int, float)) else None


def _run_actual_tokens(entry: dict[str, Any]) -> int | None:
    usage = _dict(entry.get("usage"))
    totals = _dict(usage.get("totals"))
    value = totals.get("total_tokens")
    if isinstance(value, (int, float)):
        return int(value)
    token_report = _dict(entry.get("token_report"))
    token_totals = _dict(token_report.get("totals"))
    value = token_totals.get("total_tokens")
    return int(value) if isinstance(value, (int, float)) else None


def should_stop_for_budget(config: dict[str, Any], run_entries: list[dict[str, Any]]) -> str | None:
    if str(config.get("budget_policy") or "stop_immediately") != "stop_immediately":
        return None
    budget = config.get("cost_budget")
    if isinstance(budget, (int, float)):
        actual = batch_actual_cost(run_entries)
        if actual >= float(budget):
            return f"actual_cost_{actual}_meets_or_exceeds_budget_{float(budget)}"
        preflight = budget_preflight_estimate(config, run_entries)
        estimate = preflight.get("estimated_next_run_cost")
        remaining = preflight.get("remaining_budget")
        if isinstance(estimate, (int, float)) and isinstance(remaining, (int, float)) and estimate > remaining:
            return f"remaining_budget_{remaining}_less_than_historical_max_run_cost_{estimate}"
    token_budget = config.get("token_budget")
    if isinstance(token_budget, (int, float)):
        actual_tokens = batch_actual_tokens(run_entries)
        if actual_tokens >= int(token_budget):
            return f"actual_tokens_{actual_tokens}_meets_or_exceeds_budget_{int(token_budget)}"
        token_preflight = token_budget_preflight_estimate(config, run_entries)
        token_estimate = token_preflight.get("estimated_next_run_tokens")
        token_remaining = token_preflight.get("remaining_token_budget")
        if (
            isinstance(token_estimate, (int, float))
            and isinstance(token_remaining, (int, float))
            and token_estimate > token_remaining
        ):
            return f"remaining_token_budget_{token_remaining}_less_than_historical_max_run_tokens_{token_estimate}"
    return None


def budget_preflight_estimate(config: dict[str, Any], run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    budget = config.get("cost_budget")
    actual = batch_actual_cost(run_entries)
    remaining = round(float(budget) - actual, 10) if isinstance(budget, (int, float)) else None
    historical_costs = [
        float(cost)
        for cost in (_run_actual_cost(entry) for entry in run_entries)
        if isinstance(cost, (int, float)) and float(cost) > 0
    ]
    estimate = max(historical_costs) if historical_costs else None
    return {
        "source": "historical_max_actual_run_cost" if estimate is not None else "unavailable_no_known_prior_run_cost",
        "estimated_next_run_cost": estimate,
        "historical_run_costs": historical_costs,
        "remaining_budget": remaining,
        "would_exceed_remaining_budget": bool(
            estimate is not None and remaining is not None and estimate > remaining
        ),
        "local_tokenizer_estimates_used": False,
    }


def token_budget_preflight_estimate(config: dict[str, Any], run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    budget = config.get("token_budget")
    actual = batch_actual_tokens(run_entries)
    remaining = int(budget) - actual if isinstance(budget, (int, float)) else None
    historical_tokens = [
        int(tokens)
        for tokens in (_run_actual_tokens(entry) for entry in run_entries)
        if isinstance(tokens, int) and tokens > 0
    ]
    estimate = max(historical_tokens) if historical_tokens else None
    return {
        "source": "historical_max_actual_openrouter_tokens" if estimate is not None else "unavailable_no_known_prior_token_usage",
        "estimated_next_run_tokens": estimate,
        "historical_run_tokens": historical_tokens,
        "actual_tokens": actual,
        "remaining_token_budget": remaining,
        "would_exceed_remaining_token_budget": bool(
            estimate is not None and remaining is not None and estimate > remaining
        ),
        "local_tokenizer_estimates_used": False,
    }


def safe_model_card_id(model_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", model_id.strip())
    return safe.strip("._-") or "unknown_model"


def _players_for_seat_mode(
    *,
    players: list[PlayerConfig],
    mode: str,
    batch_id: str,
    batch_seed: int,
    game_seed: int,
    run_index: int,
    model_ids: list[str],
    max_turns: int,
    max_trade_exchanges: int,
    max_auction_actions: int,
) -> tuple[list[PlayerConfig], str, dict[str, Any]]:
    normalized = mode.lower().strip()
    if normalized == "none":
        normalized = "configured_order"
    seed_material = {
        "batch_id": batch_id,
        "batch_seed": batch_seed,
        "game_seed": game_seed,
        "run_index": run_index,
        "mode": normalized,
        "model_ids": model_ids,
        "max_turns": max_turns,
        "max_trade_exchanges": max_trade_exchanges,
        "max_auction_actions": max_auction_actions,
    }
    if normalized == "configured_order":
        return list(players), "configured_order:0", seed_material
    if normalized == "full":
        permutations = list(itertools.permutations(players))
        selected = list(permutations[run_index % len(permutations)])
        return selected, f"full:{run_index % len(permutations)}", seed_material
    if normalized == "seeded_random":
        selected = list(players)
        seed_int = _deterministic_int(seed_material)
        random.Random(seed_int).shuffle(selected)
        return selected, f"seeded_random:{run_index}", seed_material
    if normalized != "latin_square":
        raise ValueError(f"Unsupported seat_permutation mode: {mode}")
    offset = run_index % len(players)
    selected = list(players[offset:]) + list(players[:offset])
    return selected, f"latin_square:{offset}", seed_material


def _deterministic_int(payload: dict[str, Any]) -> int:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def _model_config(players: list[PlayerConfig]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "model_config_version": "model_config_v1",
        "models": [
            {
                "player_id": player.player_id,
                "name": player.name,
                "openrouter_model_id": player.openrouter_model_id,
                "model_display_name": player.model_display_name,
                "reasoning": player.reasoning,
                "system_prompt_logged": False,
            }
            for player in players
        ],
    }


def _seed_manifest(config: dict[str, Any], specs: list[BatchRunSpec]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "seed_manifest_version": "seed_manifest_v1",
        "batch_id": config["batch_id"],
        "batch_seed": config.get("batch_seed"),
        "seeds": config.get("seeds", []),
        "assignments": [{"run_index": spec.index, "run_id": spec.run_id, "seed": spec.seed} for spec in specs],
    }


def _seat_manifest(config: dict[str, Any], specs: list[BatchRunSpec]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "seat_manifest_version": "seat_manifest_v1",
        "batch_id": config["batch_id"],
        "permutation_mode": config.get("seat_permutation"),
        "assignments": [
            {
                "run_index": spec.index,
                "run_id": spec.run_id,
                "seed": spec.seed,
                "permutation_id": spec.seat_metadata["permutation_id"],
                "permutation_seed_material": spec.seat_metadata["permutation_seed_material"],
                "players": [
                    {
                        "seat_index": seat_index,
                        "player_id": player.player_id,
                        "player_name": player.name,
                        "openrouter_model_id": player.openrouter_model_id,
                        "model_display_name": player.model_display_name,
                    }
                    for seat_index, player in enumerate(spec.players)
                ],
            }
            for spec in specs
        ],
    }


def _result_entry(entry: dict[str, Any]) -> dict[str, Any]:
    summary = _dict(entry.get("summary"))
    replay_report = _dict(entry.get("replay_report"))
    cost_report = _dict(entry.get("cost_report"))
    return {
        "schema_version": "v1",
        "batch_protocol_version": BATCH_PROTOCOL_VERSION,
        "run_index": entry.get("run_index"),
        "run_id": entry.get("run_id"),
        "seed": entry.get("seed"),
        "status": entry.get("status"),
        "run_dir": entry.get("run_dir"),
        "winner_player_id": summary.get("winner_player_id"),
        "turn_count": summary.get("turn_count"),
        "reason": summary.get("reason"),
        "replay_status": replay_report.get("status"),
        "state_replay_status": replay_report.get("state_status")
        or _dict(entry.get("state_replay_report")).get("status"),
        "artifact_replay_status": replay_report.get("artifact_status")
        or _dict(entry.get("artifact_replay_report")).get("status"),
        "total_actual_cost": cost_report.get("total_actual_cost"),
    }


def _leaderboard(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for entry in run_entries:
        scorecard = _dict(entry.get("scorecard"))
        for player in _list(scorecard.get("players")):
            if not isinstance(player, dict):
                continue
            model_id = str(player.get("openrouter_model_id") or "unknown")
            row = by_model.setdefault(
                model_id,
                {
                    "model_id": model_id,
                    "model_display_name": player.get("model_display_name"),
                    "game_count": 0,
                    "win_count": 0,
                    "final_net_worth_values": [],
                    "rank_values": [],
                    "total_cost": 0.0,
                    "seat_indices": [],
                },
            )
            row["game_count"] += 1
            row["win_count"] += 1 if player.get("winner") else 0
            _append_number(row["final_net_worth_values"], player.get("final_net_worth_estimate"))
            _append_number(row["rank_values"], player.get("final_rank"))
            _append_number(row["seat_indices"], player.get("seat_index"))
            _add_cost_for_model(row, entry, model_id)
    rows = []
    for row in by_model.values():
        final_values = row.pop("final_net_worth_values")
        rank_values = row.pop("rank_values")
        seat_indices = row.pop("seat_indices")
        row["win_rate"] = row["win_count"] / row["game_count"] if row["game_count"] else 0
        row["average_final_net_worth"] = mean(final_values) if final_values else None
        row["median_final_net_worth"] = median(final_values) if final_values else None
        row["final_net_worth_ci95"] = _mean_ci95(final_values)
        row["average_rank"] = mean(rank_values) if rank_values else None
        row["rank_distribution"] = _distribution(rank_values)
        row["win_rate_ci95"] = _proportion_ci95(row["win_count"], row["game_count"])
        row["seats_played"] = sorted(set(seat_indices))
        row["cost_adjusted_score"] = (
            row["average_final_net_worth"] / row["total_cost"]
            if row["average_final_net_worth"] is not None and row["total_cost"] > 0
            else None
        )
        rows.append(row)
    rows.sort(
        key=lambda item: (
            item.get("win_rate") or 0,
            item.get("average_final_net_worth") or 0,
            -(item.get("total_cost") or 0),
        ),
        reverse=True,
    )
    return {
        "schema_version": "v1",
        "leaderboard_version": "leaderboard_v1",
        "rankings": rows,
        "ranking_modes": {
            "primary": "winner_then_average_final_net_worth",
            "available": [
                "net_worth",
                "winner_completion",
                "speed",
                "reliability_cost_adjusted",
                "combined_experimental",
            ],
        },
        "score_matrix": {
            "primary_score": "average_final_net_worth",
            "secondary_score": "win_rate",
            "speed_score": "average_turns_to_win_when_available",
            "reliability_cost_adjusted": "cost_adjusted_score",
            "rank_distribution": "counts of final ranks per model",
        },
    }


def _scorecard_summary(run_entries: list[dict[str, Any]], leaderboard: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "scorecard_summary_version": "scorecard_summary_v1",
        "run_count": len(run_entries),
        "completed_run_count": sum(1 for entry in run_entries if entry.get("status") == "completed"),
        "leaderboard": leaderboard.get("rankings", []),
    }


def _category_breakdown(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    event_counts: dict[str, int] = {}
    for entry in run_entries:
        scorecard = _dict(entry.get("scorecard"))
        run = _dict(scorecard.get("run"))
        counts = _dict(run.get("event_counts"))
        for key, value in counts.items():
            if isinstance(value, int):
                event_counts[key] = event_counts.get(key, 0) + value
    return {
        "schema_version": "v1",
        "category_breakdown_version": "category_breakdown_v1",
        "event_counts": event_counts,
    }


def _statistical_summary(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    turn_counts: list[int] = []
    costs: list[float] = []
    for entry in run_entries:
        summary = _dict(entry.get("summary"))
        turn_count = summary.get("turn_count")
        if isinstance(turn_count, int):
            turn_counts.append(turn_count)
        cost_report = _dict(entry.get("cost_report"))
        actual_cost = cost_report.get("total_actual_cost")
        if isinstance(actual_cost, (int, float)):
            costs.append(float(actual_cost))
    return {
        "schema_version": "v1",
        "statistical_summary_version": "statistical_summary_v1",
        "turn_count": _stats(turn_counts),
        "actual_cost": _stats(costs),
        "total_tokens": _stats([tokens for tokens in (_run_actual_tokens(entry) for entry in run_entries) if isinstance(tokens, int)]),
    }


def _batch_replay_report(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    state_statuses: dict[str, int] = {}
    artifact_statuses: dict[str, int] = {}
    for entry in run_entries:
        replay_report = _dict(entry.get("replay_report"))
        status = str(replay_report.get("status") or "missing")
        statuses[status] = statuses.get(status, 0) + 1
        state_report = _dict(entry.get("state_replay_report"))
        artifact_report = _dict(entry.get("artifact_replay_report"))
        state_status = str(replay_report.get("state_status") or state_report.get("status") or "missing")
        artifact_status = str(replay_report.get("artifact_status") or artifact_report.get("status") or "missing")
        state_statuses[state_status] = state_statuses.get(state_status, 0) + 1
        artifact_statuses[artifact_status] = artifact_statuses.get(artifact_status, 0) + 1
    passed = statuses.get("passed", 0)
    state_passed = state_statuses.get("passed", 0)
    artifact_passed = artifact_statuses.get("passed", 0)
    return {
        "schema_version": "v1",
        "replay_report_version": "batch_replay_report_v2",
        "run_count": len(run_entries),
        "status_counts": statuses,
        "state_status_counts": state_statuses,
        "artifact_status_counts": artifact_statuses,
        "pass_rate": passed / len(run_entries) if run_entries else 0,
        "state_pass_rate": state_passed / len(run_entries) if run_entries else 0,
        "artifact_pass_rate": artifact_passed / len(run_entries) if run_entries else 0,
    }


def _batch_trace_summary(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for entry in run_entries:
        summary = _dict(entry.get("trace_summary"))
        by_type = _dict(summary.get("by_finding_type"))
        for key, value in by_type.items():
            if isinstance(value, int):
                counts[key] = counts.get(key, 0) + value
    return {
        "schema_version": "v1",
        "trace_summary_version": "batch_trace_summary_v1",
        "by_finding_type": counts,
    }


def _batch_failure_summary(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for entry in run_entries:
        summary = _dict(entry.get("failure_summary"))
        by_type = _dict(summary.get("by_finding_type"))
        for key, value in by_type.items():
            if isinstance(value, int):
                counts[key] = counts.get(key, 0) + value
    return {
        "schema_version": "v1",
        "failure_summary_version": "batch_failure_summary_v1",
        "by_finding_type": counts,
    }


def _batch_cost_report(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    by_run: dict[str, Any] = {}
    for entry in run_entries:
        report = _dict(entry.get("cost_report"))
        usage = _dict(entry.get("usage"))
        totals = _dict(usage.get("totals"))
        run_id = str(entry.get("run_id"))
        by_run[run_id] = {
            "total_actual_cost": report.get("total_actual_cost"),
            "input_tokens": totals.get("input_tokens") or totals.get("prompt_tokens"),
            "output_tokens": totals.get("output_tokens") or totals.get("completion_tokens"),
            "total_tokens": totals.get("total_tokens"),
            "reasoning_tokens": totals.get("reasoning_tokens"),
            "missing_usage_attempt_count": report.get("missing_usage_attempt_count"),
        }
        for model_id, model_row in _dict(report.get("by_model")).items():
            if not isinstance(model_row, dict):
                continue
            aggregate = by_model.setdefault(
                str(model_id),
                {
                    "decision_count": 0,
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "reasoning_tokens": 0,
                    "latency_ms": 0,
                },
            )
            aggregate["decision_count"] += int(model_row.get("decision_count") or 0)
            if isinstance(model_row.get("cost"), (int, float)):
                aggregate["cost"] += float(model_row["cost"])
            for field, source_field in (
                ("input_tokens", "input_tokens"),
                ("output_tokens", "output_tokens"),
                ("total_tokens", "total_tokens"),
                ("reasoning_tokens", "reasoning_tokens"),
                ("latency_ms", "latency_ms"),
            ):
                value = model_row.get(source_field)
                if not isinstance(value, (int, float)) and field == "input_tokens":
                    value = model_row.get("prompt_tokens")
                if not isinstance(value, (int, float)) and field == "output_tokens":
                    value = model_row.get("completion_tokens")
                if isinstance(value, (int, float)):
                    aggregate[field] += int(value)
    for row in by_model.values():
        row["cost"] = round(float(row["cost"]), 10)
    return {
        "schema_version": "v1",
        "usage_accounting_version": "batch_usage_accounting_v1",
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "total_actual_cost": batch_actual_cost(run_entries),
        "by_run": by_run,
        "by_model": by_model,
    }


def _batch_token_report(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "prompt_tokens": 0,
        "input_tokens": 0,
        "completion_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "native_prompt_tokens": 0,
        "native_completion_tokens": 0,
        "native_total_tokens": 0,
        "reasoning_tokens": 0,
        "cached_tokens": 0,
    }
    for entry in run_entries:
        usage = _dict(entry.get("usage"))
        run_totals = _dict(usage.get("totals"))
        for key in totals:
            if isinstance(run_totals.get(key), (int, float)):
                totals[key] += int(run_totals[key])
        if not isinstance(run_totals.get("input_tokens"), (int, float)) and isinstance(run_totals.get("prompt_tokens"), (int, float)):
            totals["input_tokens"] += int(run_totals["prompt_tokens"])
        if not isinstance(run_totals.get("output_tokens"), (int, float)) and isinstance(run_totals.get("completion_tokens"), (int, float)):
            totals["output_tokens"] += int(run_totals["completion_tokens"])
    by_model: dict[str, dict[str, Any]] = {}
    by_run: dict[str, dict[str, Any]] = {}
    for entry in run_entries:
        run_id = str(entry.get("run_id") or "unknown")
        usage = _dict(entry.get("usage"))
        run_totals = _dict(usage.get("totals"))
        by_run[run_id] = _usage_token_row(run_totals)
        for model_id, row in _dict(usage.get("by_model")).items():
            current = by_model.setdefault(str(model_id), _empty_token_row())
            _add_token_row(current, _usage_token_row(_dict(row)))
    return {
        "schema_version": "v1",
        "usage_accounting_version": "batch_token_report_v1",
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "totals": totals,
        "by_model": by_model,
        "by_run": by_run,
    }


def _batch_usage_summary(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "usage_accounting_version": "batch_usage_summary_v1",
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "cost_report": _batch_cost_report(run_entries),
        "token_report": _batch_token_report(run_entries),
        "actual_cost": batch_actual_cost(run_entries),
        "actual_tokens": batch_actual_tokens(run_entries),
        "run_count": len(run_entries),
    }


def _empty_token_row() -> dict[str, Any]:
    return {
        "prompt_tokens": 0,
        "input_tokens": 0,
        "completion_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "native_prompt_tokens": 0,
        "native_completion_tokens": 0,
        "native_total_tokens": 0,
        "reasoning_tokens": 0,
        "cached_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }


def _usage_token_row(source: dict[str, Any]) -> dict[str, Any]:
    row = _empty_token_row()
    for key in row:
        value = source.get(key)
        if isinstance(value, (int, float)):
            row[key] = int(value)
    if not isinstance(source.get("input_tokens"), (int, float)) and isinstance(source.get("prompt_tokens"), (int, float)):
        row["input_tokens"] = int(source["prompt_tokens"])
    if not isinstance(source.get("output_tokens"), (int, float)) and isinstance(source.get("completion_tokens"), (int, float)):
        row["output_tokens"] = int(source["completion_tokens"])
    return row


def _add_token_row(target: dict[str, Any], row: dict[str, Any]) -> None:
    for key, value in row.items():
        if isinstance(value, (int, float)):
            target[key] = int(target.get(key) or 0) + int(value)


def _model_failure_breakdown(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for entry in run_entries:
        run_dir = Path(str(entry.get("run_dir")))
        for finding in _read_jsonl(run_dir / "failure_findings.jsonl"):
            model_id = str(finding.get("model_id") or "unknown")
            row = by_model.setdefault(model_id, {"model_id": model_id, "total_failures": 0, "by_finding_type": {}, "by_severity": {}})
            row["total_failures"] += 1
            _increment(row["by_finding_type"], str(finding.get("finding_type") or "unknown"))
            _increment(row["by_severity"], str(finding.get("severity") or "unknown"))
    return {
        "schema_version": "v1",
        "failure_taxonomy_version": "batch_model_failure_breakdown_v1",
        "models": sorted(by_model.values(), key=lambda row: row["total_failures"], reverse=True),
    }


def _failure_leaderboard(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    rows = _model_failure_breakdown(run_entries)["models"]
    return {
        "schema_version": "v1",
        "failure_taxonomy_version": "failure_leaderboard_v1",
        "ranking_mode": "fewest_total_failures_then_fewest_high_severity",
        "rankings": sorted(
            rows,
            key=lambda row: (
                row.get("total_failures") or 0,
                _dict(row.get("by_severity")).get("high", 0),
                str(row.get("model_id")),
            ),
        ),
    }


def _top_findings(run_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    severity_order = {"high": 3, "medium": 2, "low": 1}
    for entry in run_entries:
        run_dir = Path(str(entry.get("run_dir")))
        for path_name in ("failure_findings.jsonl", "trace_findings.jsonl"):
            for finding in _read_jsonl(run_dir / path_name):
                row = dict(finding)
                row["batch_run_id"] = entry.get("run_id")
                row["batch_run_index"] = entry.get("run_index")
                rows.append(row)
    rows.sort(
        key=lambda row: (
            severity_order.get(str(row.get("severity") or ""), 0),
            1 if row.get("human_review_required") else 0,
            str(row.get("finding_type") or ""),
        ),
        reverse=True,
    )
    return rows[:200]


def _model_trace_breakdown(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for entry in run_entries:
        run_dir = Path(str(entry.get("run_dir")))
        for finding in _read_jsonl(run_dir / "trace_findings.jsonl"):
            model_id = str(finding.get("model_id") or "unknown")
            row = by_model.setdefault(model_id, {"model_id": model_id, "total_findings": 0, "by_finding_type": {}, "by_severity": {}})
            row["total_findings"] += 1
            _increment(row["by_finding_type"], str(finding.get("finding_type") or "unknown"))
            _increment(row["by_severity"], str(finding.get("severity") or "unknown"))
    return {
        "schema_version": "v1",
        "trace_analyzer_version": "batch_model_trace_breakdown_v1",
        "models": sorted(by_model.values(), key=lambda row: row["total_findings"], reverse=True),
    }


def _failure_trace_breakdown(run_entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "trace_analyzer_version": "batch_failure_trace_breakdown_v1",
        "failure_breakdown": _model_failure_breakdown(run_entries),
        "trace_breakdown": _model_trace_breakdown(run_entries),
    }


def _budget_report(
    config: dict[str, Any],
    run_entries: list[dict[str, Any]],
    *,
    credits_before: dict[str, Any],
    credits_after: dict[str, Any] | None = None,
    stop_reason: str | None = None,
) -> dict[str, Any]:
    total_actual = batch_actual_cost(run_entries)
    budget = float(config.get("cost_budget") or DEFAULT_BATCH_BUDGET)
    preflight = budget_preflight_estimate(config, run_entries)
    token_preflight = token_budget_preflight_estimate(config, run_entries)
    token_budget = config.get("token_budget")
    token_budget_value = int(token_budget) if isinstance(token_budget, (int, float)) else None
    total_actual_tokens = batch_actual_tokens(run_entries)
    return {
        "schema_version": "v1",
        "budget_report_version": "budget_report_v1",
        "budget": budget,
        "token_budget": token_budget_value,
        "cost_budget_unit": config.get("cost_budget_unit"),
        "budget_policy": config.get("budget_policy"),
        "total_actual_cost": total_actual,
        "total_estimated_cost": None,
        "total_unknown_cost": None,
        "total_actual_tokens": total_actual_tokens,
        "remaining_budget": round(budget - total_actual, 10),
        "remaining_token_budget": token_budget_value - total_actual_tokens if token_budget_value is not None else None,
        "preflight": preflight,
        "token_preflight": token_preflight,
        "stop_policy": "stop_immediately_when_actual_cost_or_tokens_meet_budget_or_preflight_estimate_exceeds_remaining_budget",
        "stop_reason": stop_reason,
        "credits_before": credits_before,
        "credits_after": credits_after,
    }


def _batch_review_queue(run_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in run_entries:
        run_dir = Path(str(entry.get("run_dir")))
        review_path = run_dir / "review_queue.jsonl"
        for item in _read_jsonl(review_path):
            item = dict(item)
            seat_assignment = _dict(entry.get("seat_assignment"))
            item["batch_id"] = item.get("batch_id") or seat_assignment.get("batch_id")
            item["run_id"] = item.get("run_id") or entry.get("run_id")
            rows.append(item)
    return rows


def _write_model_cards(
    model_cards_dir: Path,
    run_entries: list[dict[str, Any]],
    leaderboard: dict[str, Any],
) -> list[dict[str, Any]]:
    model_cards_dir.mkdir(parents=True, exist_ok=True)
    cards = [_model_card(model_id, run_entries, leaderboard) for model_id in _model_ids(run_entries)]
    written: list[dict[str, Any]] = []
    for card in cards:
        safe_id = safe_model_card_id(str(card["model_id"]))
        json_path = model_cards_dir / f"{safe_id}.json"
        markdown_path = model_cards_dir / f"{safe_id}.md"
        _write_json(json_path, card)
        markdown_path.write_text(_model_card_markdown(card), encoding="utf-8")
        written.append(
            {
                "model_id": card["model_id"],
                "json_path": str(json_path),
                "markdown_path": str(markdown_path),
            }
        )
    return written


def _model_card(model_id: str, run_entries: list[dict[str, Any]], leaderboard: dict[str, Any]) -> dict[str, Any]:
    player_rows: list[dict[str, Any]] = []
    model_run_entries: list[dict[str, Any]] = []
    for entry in run_entries:
        scorecard = _dict(entry.get("scorecard"))
        matched = [
            {**player, "_run_id": entry.get("run_id"), "_run_dir": entry.get("run_dir")}
            for player in _list(scorecard.get("players"))
            if isinstance(player, dict) and str(player.get("openrouter_model_id") or "unknown") == model_id
        ]
        if matched:
            model_run_entries.append(entry)
            player_rows.extend(matched)
    usage_rows = _usage_for_model(run_entries, model_id)
    failure_counts = _failure_counts_for_model(run_entries, model_id)
    latency_values = _numeric_values(player_rows, "average_decision_latency_ms")
    final_net_worth = _numeric_values(player_rows, "final_net_worth_estimate")
    ranks = _numeric_values(player_rows, "final_rank")
    turns_survived = _numeric_values(player_rows, "turns_survived")
    leaderboard_row = next(
        (
            row
            for row in _list(leaderboard.get("rankings"))
            if isinstance(row, dict) and str(row.get("model_id") or "unknown") == model_id
        ),
        {},
    )
    total_decisions = sum(int(row.get("decision_count") or 0) for row in usage_rows)
    total_cost = sum(float(row.get("cost") or 0.0) for row in usage_rows)
    total_tokens = _sum_usage_field(usage_rows, "total_tokens")
    prompt_tokens = _sum_usage_field(usage_rows, "prompt_tokens")
    completion_tokens = _sum_usage_field(usage_rows, "completion_tokens")
    reasoning_tokens = _sum_usage_field(usage_rows, "reasoning_tokens")
    cached_tokens = _sum_usage_field(usage_rows, "cached_tokens")
    wins = sum(1 for row in player_rows if row.get("winner"))
    bankruptcy_count = sum(1 for row in player_rows if row.get("bankrupt"))
    valid_first_response_count = sum(
        int(row.get("decision_count") or 0) - int(row.get("retry_count") or row.get("retries_used") or 0)
        for row in player_rows
    )
    retry_count = sum(int(row.get("retry_count") or row.get("retries_used") or 0) for row in player_rows)
    fallback_count = sum(int(row.get("fallback_count") or row.get("fallbacks_used") or 0) for row in player_rows)
    return {
        "schema_version": "v1",
        "model_card_version": "model_card_v1",
        "model_id": model_id,
        "model_display_name": leaderboard_row.get("model_display_name"),
        "openrouter_route": model_id,
        "provider_route_observations": None,
        "date_tested": datetime.now(timezone.utc).isoformat(),
        "benchmark_version": "monopolybench_common_infra_v1",
        "engine_version": None,
        "contract_version": "v1",
        "scoring_version": "scorecard_v1",
        "failure_taxonomy_version": "failure_taxonomy_v1",
        "prompt_pipeline": {
            "status": "unchanged",
            "markdown_private_thought_policy": "links_only_no_private_thought_excerpts",
        },
        "seed_set": sorted({entry.get("seed") for entry in model_run_entries if entry.get("seed") is not None}),
        "seat_coverage": sorted(
            {
                int(row["seat_index"])
                for row in player_rows
                if isinstance(row.get("seat_index"), int)
            }
        ),
        "full_game_count": len(player_rows),
        "micro_scenario_count": 0,
        "decisions": {
            "total_decisions": total_decisions,
            "valid_first_response_count": valid_first_response_count,
            "valid_first_response_rate": (
                valid_first_response_count / total_decisions if total_decisions else None
            ),
            "retry_count": retry_count,
            "retry_rate": retry_count / total_decisions if total_decisions else None,
            "fallback_count": fallback_count,
            "fallback_rate": fallback_count / total_decisions if total_decisions else None,
        },
        "latency_ms": {
            "average": mean(latency_values) if latency_values else None,
            "p50": _percentile(latency_values, 50),
            "p90": _percentile(latency_values, 90),
            "p95": _percentile(latency_values, 95),
        },
        "usage": {
            "source": "openrouter_actuals_only",
            "local_tokenizer_estimates_used": False,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "reasoning_tokens": reasoning_tokens,
            "cached_tokens": cached_tokens,
            "total_cost": round(total_cost, 10),
            "cost_per_game": round(total_cost / len(player_rows), 10) if player_rows else None,
            "cost_per_decision": round(total_cost / total_decisions, 10) if total_decisions else None,
            "cost_per_score_point": (
                round(total_cost / sum(final_net_worth), 10)
                if final_net_worth and sum(final_net_worth) != 0
                else None
            ),
        },
        "performance": {
            "win_rate": wins / len(player_rows) if player_rows else None,
            "average_rank": mean(ranks) if ranks else None,
            "median_rank": median(ranks) if ranks else None,
            "bankruptcy_rate": bankruptcy_count / len(player_rows) if player_rows else None,
            "average_final_net_worth": mean(final_net_worth) if final_net_worth else None,
            "median_final_net_worth": median(final_net_worth) if final_net_worth else None,
            "average_turns_survived": mean(turns_survived) if turns_survived else None,
            "primary_score": leaderboard_row.get("average_final_net_worth"),
        },
        "behavior": {
            "auction_metrics": _sum_player_fields(player_rows, ["auction_bids_placed", "auctions_won", "auctions_dropped"]),
            "trade_metrics": _sum_player_fields(
                player_rows,
                ["trades_proposed", "trades_received", "trades_accepted", "trades_rejected", "counters_made"],
            ),
            "build_mortgage_metrics": _sum_player_fields(
                player_rows,
                ["houses_built", "hotels_built", "mortgages", "unmortgages"],
            ),
            "failure_taxonomy_counts": failure_counts,
            "reviewed_behavioral_labels": {},
        },
        "representative_runs": {
            "winning_run": _representative_run(player_rows, model_run_entries, winner=True),
            "losing_run": _representative_run(player_rows, model_run_entries, winner=False),
        },
        "caveats": [
            "Model card is derived from available run and batch artifacts.",
            "Private thoughts are not quoted in markdown by default; inspect replay/review artifacts for full text.",
            "OpenRouter usage fields are null or zero when OpenRouter did not return actual accounting data.",
        ],
        "artifact_links": [
            {
                "run_id": entry.get("run_id"),
                "run_dir": entry.get("run_dir"),
                "scorecard": str(Path(str(entry.get("run_dir"))) / "scorecard.json"),
                "replay": str(Path(str(entry.get("run_dir"))) / "replay_report.json"),
                "state_replay": str(Path(str(entry.get("run_dir"))) / "state_replay_report.json"),
                "artifact_replay": str(Path(str(entry.get("run_dir"))) / "artifact_replay_report.json"),
                "review_queue": str(Path(str(entry.get("run_dir"))) / "review_queue.jsonl"),
            }
            for entry in model_run_entries
        ],
    }


def _model_card_markdown(card: dict[str, Any]) -> str:
    usage = card.get("usage", {})
    performance = card.get("performance", {})
    decisions = card.get("decisions", {})
    behavior = card.get("behavior", {})
    links = card.get("artifact_links", [])
    link_lines = "\n".join(
        f"- `{item.get('run_id')}`: `{item.get('run_dir')}`" for item in links if isinstance(item, dict)
    )
    return "\n".join(
        [
            f"# {card.get('model_display_name') or card.get('model_id')}",
            "",
            f"- Model id: `{card.get('model_id')}`",
            f"- Model card version: `{card.get('model_card_version')}`",
            "- Prompt pipeline: unchanged",
            "- Private thoughts: linked via replay/review artifacts, not quoted here",
            "",
            "## Performance",
            "",
            f"- Full games: {card.get('full_game_count')}",
            f"- Win rate: {performance.get('win_rate')}",
            f"- Average rank: {performance.get('average_rank')}",
            f"- Average final net worth: {performance.get('average_final_net_worth')}",
            f"- Bankruptcy rate: {performance.get('bankruptcy_rate')}",
            "",
            "## Reliability And Cost",
            "",
            f"- Total decisions: {decisions.get('total_decisions')}",
            f"- Valid first-response rate: {decisions.get('valid_first_response_rate')}",
            f"- Retry rate: {decisions.get('retry_rate')}",
            f"- Fallback rate: {decisions.get('fallback_rate')}",
            f"- Total tokens: {usage.get('total_tokens')}",
            f"- Total cost: {usage.get('total_cost')}",
            f"- Cost per decision: {usage.get('cost_per_decision')}",
            "",
            "## Failure Counts",
            "",
            json.dumps(behavior.get("failure_taxonomy_counts", {}), indent=2, sort_keys=True),
            "",
            "## Artifact Links",
            "",
            link_lines or "- No run artifacts available.",
            "",
        ]
    )


def _model_ids(run_entries: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    for entry in run_entries:
        scorecard = _dict(entry.get("scorecard"))
        for player in _list(scorecard.get("players")):
            if isinstance(player, dict):
                seen.add(str(player.get("openrouter_model_id") or "unknown"))
    return sorted(seen)


def _usage_for_model(run_entries: list[dict[str, Any]], model_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in run_entries:
        usage = _dict(entry.get("usage"))
        by_model = _dict(usage.get("by_model"))
        row = by_model.get(model_id)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _failure_counts_for_model(run_entries: list[dict[str, Any]], model_id: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in run_entries:
        run_dir = Path(str(entry.get("run_dir")))
        for finding in _read_jsonl(run_dir / "failure_findings.jsonl"):
            if finding.get("model_id") != model_id:
                continue
            finding_type = str(finding.get("finding_type") or "unknown")
            counts[finding_type] = counts.get(finding_type, 0) + 1
    return counts


def _sum_usage_field(rows: list[dict[str, Any]], field: str) -> int:
    return sum(int(row.get(field) or 0) for row in rows if isinstance(row.get(field), (int, float)))


def _sum_player_fields(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, int | float]:
    totals: dict[str, int | float] = {field: 0 for field in fields}
    for row in rows:
        for field in fields:
            if isinstance(row.get(field), (int, float)):
                totals[field] += row[field]
    return totals


def _representative_run(
    player_rows: list[dict[str, Any]],
    run_entries: list[dict[str, Any]],
    *,
    winner: bool,
) -> dict[str, Any] | None:
    matching_rows = [row for row in player_rows if bool(row.get("winner")) == winner]
    if not matching_rows:
        return None
    selected = max(matching_rows, key=lambda row: row.get("final_net_worth_estimate") or 0)
    run_id = selected.get("_run_id")
    entry = next((entry for entry in run_entries if entry.get("run_id") == run_id), None)
    return {
        "run_id": run_id,
        "run_dir": selected.get("_run_dir") or (entry.get("run_dir") if isinstance(entry, dict) else None),
        "final_net_worth_estimate": selected.get("final_net_worth_estimate"),
        "final_rank": selected.get("final_rank"),
    }


def _percentile(values: list[Any], percentile: int) -> float | None:
    numbers = sorted(float(value) for value in values if isinstance(value, (int, float)))
    if not numbers:
        return None
    index = max(0, min(len(numbers) - 1, round((percentile / 100) * (len(numbers) - 1))))
    return numbers[index]


def _batch_manifest(
    config: dict[str, Any],
    run_entries: list[dict[str, Any]],
    paths: dict[str, Path],
    model_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "batch_manifest_version": "batch_manifest_v1",
        "batch_id": config["batch_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "batch_dir": str(paths["batch_dir"]),
        "run_count": len(run_entries),
        "runs": [
            {
                "run_index": entry.get("run_index"),
                "run_id": entry.get("run_id"),
                "run_dir": entry.get("run_dir"),
                "status": entry.get("status"),
            }
            for entry in run_entries
        ],
        "model_cards": model_cards,
    }


def _artifact_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    artifacts = []
    batch_dir = paths["batch_dir"]
    for label, path in sorted(paths.items()):
        if label == "batch_dir":
            continue
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    artifacts.append(_artifact_manifest_entry(f"{label}:{child.name}", batch_dir, child))
            continue
        entry: dict[str, Any] = {
            "label": label,
            "path": str(path),
            "relative_path": _relative_path(batch_dir, path),
            "exists": path.exists(),
        }
        if path.exists() and path.is_file():
            data = path.read_bytes()
            entry["bytes"] = len(data)
            entry["sha256"] = hashlib.sha256(data).hexdigest()
        artifacts.append(entry)
    return {
        "schema_version": "v1",
        "manifest_version": "batch_artifact_manifest_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "batch_dir": str(batch_dir),
        "artifacts": artifacts,
    }


def _artifact_manifest_entry(label: str, batch_dir: Path, path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "relative_path": _relative_path(batch_dir, path),
        "exists": path.exists(),
    }
    if path.exists() and path.is_file():
        data = path.read_bytes()
        entry["bytes"] = len(data)
        entry["sha256"] = hashlib.sha256(data).hexdigest()
    return entry


def _stats(values: list[int] | list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None, "ci95": None}
    return {
        "count": len(values),
        "mean": mean(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "ci95": _mean_ci95(values),
    }


def _mean_ci95(values: list[Any]) -> dict[str, float] | None:
    numbers = [float(value) for value in values if isinstance(value, (int, float))]
    if not numbers:
        return None
    avg = mean(numbers)
    if len(numbers) == 1:
        return {"lower": avg, "upper": avg, "margin": 0.0}
    margin = 1.96 * stdev(numbers) / math.sqrt(len(numbers))
    return {"lower": avg - margin, "upper": avg + margin, "margin": margin}


def _proportion_ci95(successes: int, total: int) -> dict[str, float] | None:
    if total <= 0:
        return None
    p = successes / total
    margin = 1.96 * math.sqrt((p * (1 - p)) / total)
    return {"lower": max(0.0, p - margin), "upper": min(1.0, p + margin), "margin": margin}


def _distribution(values: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if isinstance(value, (int, float)):
            key = str(int(value))
            counts[key] = counts.get(key, 0) + 1
    return counts


def _increment(mapping: dict[str, int], key: str) -> None:
    mapping[key] = mapping.get(key, 0) + 1


def _add_cost_for_model(row: dict[str, Any], entry: dict[str, Any], model_id: str) -> None:
    cost_report = _dict(entry.get("cost_report"))
    by_model = _dict(cost_report.get("by_model"))
    model_cost = _dict(by_model.get(model_id))
    if isinstance(model_cost.get("cost"), (int, float)):
        row["total_cost"] += float(model_cost["cost"])


def _append_number(target: list[Any], value: Any) -> None:
    if isinstance(value, (int, float)):
        target.append(value)


def _numeric_values(rows: list[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(field)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return values


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def _relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
