from __future__ import annotations

import argparse
import asyncio
import importlib
import json
from pathlib import Path
from typing import Any, Callable

from monopoly_telemetry import build_experiment_manifest, build_review_cost_aggregate, init_run_files, usage_calls_jsonl

from .batch_artifacts import (
    DEFAULT_SEAT_MODE,
    batch_paths,
    build_batch_run_specs,
    build_run_entry,
    normalized_batch_config,
    should_stop_for_budget,
    write_batch_dynamic_artifacts,
    write_batch_static_artifacts,
)
from .llm_runner import LlmRunner
from .openrouter_client import OpenRouterClient
from .paths import default_players_config_path, resolve_repo_path, resolve_repo_root
from .player_config import build_player_configs


async def run_batch(
    config: dict[str, Any],
    *,
    runs_dir: Path | None = None,
    openrouter_factory: Callable[[], Any] | None = None,
) -> Path:
    batch_id = str(config.get("batch_id") or config.get("output_dir") or "batch")
    batch_type = str(config.get("batch_type") or "full_game")
    if batch_type == "micro_suite":
        return await _run_micro_suite_batch(
            config,
            batch_id=batch_id,
            runs_dir=runs_dir,
            openrouter_factory=openrouter_factory,
        )
    if batch_type == "mixed":
        return await _run_mixed_batch(
            config,
            batch_id=batch_id,
            runs_dir=runs_dir,
            openrouter_factory=openrouter_factory,
        )
    seeds = [int(seed) for seed in config.get("seeds", []) if isinstance(seed, (int, float))]
    matches = int(config.get("matches", len(seeds) if seeds else 0))
    players_path = config.get("players")
    max_turns = int(config.get("max_turns", 200))
    max_trade_exchanges = int(config.get("max_trade_exchanges", 20))
    max_auction_actions = int(config.get("max_auction_actions", 200))
    players_file = (
        resolve_repo_path(str(players_path))
        if players_path
        else default_players_config_path()
    )

    if matches <= 0:
        raise ValueError("Batch matches must be >= 1.")
    if not seeds:
        raise ValueError("Batch config must include a non-empty seeds list.")

    runs_root = resolve_repo_path(str(runs_dir)) if runs_dir else resolve_repo_root() / "runs"
    players = build_player_configs(requested_players=None, config_path=players_file)
    factory = openrouter_factory or OpenRouterClient
    seat_mode = str(config.get("seat_permutation") or DEFAULT_SEAT_MODE)
    batch_seed = int(config.get("batch_seed") or seeds[0])
    normalized_config = normalized_batch_config(
        {
            **config,
            "matches": matches,
            "seeds": seeds,
            "players": str(players_file),
            "seat_permutation": seat_mode,
            "batch_seed": batch_seed,
            "max_turns": max_turns,
        },
        batch_id=batch_id,
        runs_root=runs_root,
    )
    paths = batch_paths(runs_root, batch_id)
    specs = build_batch_run_specs(
        batch_id=batch_id,
        seeds=seeds,
        matches=matches,
        players=players,
        seat_mode=seat_mode,
        batch_seed=batch_seed,
        max_turns=max_turns,
        max_trade_exchanges=max_trade_exchanges,
        max_auction_actions=max_auction_actions,
    )
    metadata_client = factory()
    pricing_snapshot = await _openrouter_metadata_snapshot(metadata_client, method_name="get_models")
    credits_before = await _openrouter_metadata_snapshot(metadata_client, method_name="get_credits")
    await _maybe_close(metadata_client)
    write_batch_static_artifacts(
        paths=paths,
        config=normalized_config,
        players=players,
        specs=specs,
        pricing_snapshot=pricing_snapshot,
        credits_before=credits_before,
    )

    run_entries: list[dict[str, Any]] = _read_existing_run_entries(paths["run_index"]) if normalized_config["resume"] else []
    seen_run_ids = {str(entry.get("run_id")) for entry in run_entries}
    budget_stop_reason = should_stop_for_budget(normalized_config, run_entries)

    for spec in specs:
        if budget_stop_reason:
            break
        if spec.run_id in seen_run_ids:
            continue
        run_files = init_run_files(runs_root, spec.run_id)
        if normalized_config["resume"] and run_files.summary_path.exists():
            entry = build_run_entry(spec=spec, run_dir=run_files.run_dir, status="completed")
            run_entries.append(entry)
            seen_run_ids.add(spec.run_id)
            budget_stop_reason = should_stop_for_budget(normalized_config, run_entries)
            write_batch_dynamic_artifacts(
                paths=paths,
                config=normalized_config,
                run_entries=run_entries,
                credits_before=credits_before,
                credits_after={},
                budget_stop_reason=budget_stop_reason,
            )
            continue
        runner = LlmRunner(
            seed=spec.seed,
            players=spec.players,
            run_id=spec.run_id,
            openrouter=factory(),
            run_files=run_files,
            max_turns=max_turns,
            event_delay_s=0,
            max_trade_exchanges=max_trade_exchanges,
            max_auction_actions=max_auction_actions,
            seat_assignment_metadata=spec.seat_metadata,
        )

        run_files.write_snapshot(runner.get_snapshot())

        async def on_event(event: dict[str, Any]) -> None:
            run_files.write_event(event)

        async def on_snapshot(snapshot: dict[str, Any]) -> None:
            run_files.write_snapshot(snapshot)

        async def on_summary(summary: dict[str, Any]) -> None:
            run_files.write_summary(summary)

        async def on_decision(entry: dict[str, Any]) -> None:
            run_files.write_decision(entry)

        try:
            await runner.run(
                on_event=on_event,
                on_snapshot=on_snapshot,
                on_summary=on_summary,
                on_decision=on_decision,
            )
            entry = build_run_entry(spec=spec, run_dir=run_files.run_dir, status="completed")
        except Exception as exc:
            entry = build_run_entry(spec=spec, run_dir=run_files.run_dir, status="failed", error=str(exc))
            if not normalized_config["continue_on_failure"]:
                run_entries.append(entry)
                write_batch_dynamic_artifacts(
                    paths=paths,
                    config=normalized_config,
                    run_entries=run_entries,
                    credits_before=credits_before,
                    credits_after={},
                    budget_stop_reason=budget_stop_reason,
                )
                raise
        run_entries.append(entry)
        seen_run_ids.add(spec.run_id)
        budget_stop_reason = should_stop_for_budget(normalized_config, run_entries)
        write_batch_dynamic_artifacts(
            paths=paths,
            config=normalized_config,
            run_entries=run_entries,
            credits_before=credits_before,
            credits_after={},
            budget_stop_reason=budget_stop_reason,
        )

    credits_client = factory()
    credits_after = await _openrouter_metadata_snapshot(credits_client, method_name="get_credits")
    await _maybe_close(credits_client)
    write_batch_dynamic_artifacts(
        paths=paths,
        config=normalized_config,
        run_entries=run_entries,
        credits_before=credits_before,
        credits_after=credits_after,
        budget_stop_reason=budget_stop_reason,
    )

    return paths["run_index_jsonl"]


async def _run_mixed_batch(
    config: dict[str, Any],
    *,
    batch_id: str,
    runs_dir: Path | None,
    openrouter_factory: Callable[[], Any] | None,
) -> Path:
    runs_root = resolve_repo_path(str(runs_dir)) if runs_dir else resolve_repo_root() / "runs"
    parent_dir = runs_root / "batches" / batch_id
    parent_dir.mkdir(parents=True, exist_ok=True)
    component_entries: list[dict[str, Any]] = []
    if config.get("seeds"):
        full_config = {
            **config,
            "batch_type": "full_game",
            "batch_id": str(config.get("full_game_batch_id") or f"{batch_id}-full-game"),
        }
        full_index = await run_batch(full_config, runs_dir=runs_root, openrouter_factory=openrouter_factory)
        component_entries.append({"component_type": "full_game", "run_index_jsonl": str(full_index)})
    micro_config = {
        **config,
        "batch_type": "micro_suite",
        "batch_id": str(config.get("micro_batch_id") or f"{batch_id}-micro-suite"),
    }
    micro_index = await _run_micro_suite_batch(
        micro_config,
        batch_id=micro_config["batch_id"],
        runs_dir=runs_root,
        openrouter_factory=openrouter_factory,
    )
    component_entries.append({"component_type": "micro_suite", "run_index_jsonl": str(micro_index)})
    parent_index = parent_dir / "run_index.jsonl"
    _write_jsonl(parent_index, component_entries)
    _write_json(
        parent_dir / "batch_config.json",
        {
            "schema_version": "v1",
            "batch_protocol_version": "batch_protocol_v1",
            "batch_id": batch_id,
            "batch_type": "mixed",
            "components": component_entries,
            "prompt_pipeline": {
                "status": "unchanged",
                "note": "Mixed batch orchestration does not change prompt construction, content, tools, or retry behavior.",
            },
        },
    )
    return parent_index


async def _run_micro_suite_batch(
    config: dict[str, Any],
    *,
    batch_id: str,
    runs_dir: Path | None,
    openrouter_factory: Callable[[], Any] | None,
) -> Path:
    runs_root = resolve_repo_path(str(runs_dir)) if runs_dir else resolve_repo_root() / "runs"
    paths = batch_paths(runs_root, batch_id)
    batch_dir = paths["batch_dir"]
    batch_dir.mkdir(parents=True, exist_ok=True)
    suite_id = str(config.get("micro_suite_id") or config.get("suite_id") or "micro-v1")
    prompt_condition = str(config.get("prompt_condition") or "live_game")
    scenario_ids = [
        str(value)
        for value in config.get("scenario_ids", [])
        if isinstance(value, str)
    ] or None
    model_configs = _micro_model_configs(config)
    if not model_configs:
        players_path = config.get("players")
        players_file = resolve_repo_path(str(players_path)) if players_path else default_players_config_path()
        model_configs = [
            {
                "openrouter_model_id": player.openrouter_model_id,
                "model_display_name": player.model_display_name,
                "reasoning": player.reasoning,
            }
            for player in build_player_configs(requested_players=None, config_path=players_file)
        ]
    if not model_configs:
        raise ValueError("Micro-suite batch requires at least one model id.")
    model_ids = [str(row["openrouter_model_id"]) for row in model_configs]

    micro_runner = importlib.import_module("monopoly_microbench.runner")
    micro_catalog = importlib.import_module("monopoly_microbench.catalog")
    run_scenario = getattr(micro_runner, "run_scenario")
    micro_config_cls = getattr(micro_runner, "MicroRunConfig")
    suite = micro_catalog.get_suite(suite_id)
    selected_scenarios = scenario_ids or list(suite["scenario_ids"])
    normalized_config = {
        **normalized_batch_config(
            {
                **config,
                "batch_type": "micro_suite",
                "matches": len(model_ids) * len(selected_scenarios),
                "seeds": [],
                "players": config.get("players"),
            },
            batch_id=batch_id,
            runs_root=runs_root,
        ),
        "micro_suite_id": suite_id,
        "scenario_ids": selected_scenarios,
        "model_ids": model_ids,
        "models": model_configs,
        "prompt_condition": prompt_condition,
    }
    _write_json(paths["batch_config"], normalized_config)
    _write_json(paths["model_config"], {"schema_version": "v1", "models": model_configs})
    _write_json(
        paths["experiment_manifest"],
        build_experiment_manifest(
            experiment_id=batch_id,
            benchmark_tracks=["micro_suite"],
            models=model_configs,
            reasoning_policy=None,
            batch_type="micro_suite",
            run_count=len(model_configs) * len(selected_scenarios),
        ),
    )

    metadata_client = (openrouter_factory or OpenRouterClient)()
    pricing_snapshot = await _openrouter_metadata_snapshot(metadata_client, method_name="get_models")
    credits_before = await _openrouter_metadata_snapshot(metadata_client, method_name="get_credits")
    await _maybe_close(metadata_client)
    _write_json(paths["model_pricing_snapshot"], pricing_snapshot)

    result_entries: list[dict[str, Any]] = []
    budget_stop_reason: str | None = None
    factory = openrouter_factory or OpenRouterClient
    continue_on_failure = bool(config.get("continue_on_failure", False))
    for model_config in model_configs:
        model_id = str(model_config["openrouter_model_id"])
        reasoning = model_config.get("reasoning") if isinstance(model_config.get("reasoning"), dict) else None
        for scenario_id in selected_scenarios:
            if budget_stop_reason:
                break
            run_id = f"{batch_id}-{_safe_micro_id(model_id)}-{scenario_id}"
            try:
                result = await run_scenario(
                    micro_config_cls(
                        scenario_id=scenario_id,
                        openrouter_model_id=model_id,
                        prompt_condition=prompt_condition,
                        reasoning=reasoning,
                        run_id=run_id,
                    ),
                    runs_dir=runs_root,
                    openrouter_factory=factory,
                )
                status = "completed"
                error = None
            except Exception as exc:
                if not continue_on_failure:
                    raise
                result = {}
                status = "failed"
                error = str(exc)
            entry = {
                "schema_version": "v1",
                "batch_protocol_version": "batch_protocol_v1",
                "batch_type": "micro_suite",
                "batch_id": batch_id,
                "run_index": len(result_entries),
                "run_id": run_id,
                "status": status,
                "error": error,
                "run_dir": str(runs_root / "micro" / run_id),
                "suite_id": suite_id,
                "scenario_id": scenario_id,
                "model_id": model_id,
                "reasoning": reasoning,
                "prompt_condition": prompt_condition,
                "result": result,
            }
            result_entries.append(entry)
            budget_stop_reason = _micro_should_stop_for_budget(normalized_config, result_entries)
            _write_micro_batch_dynamic(paths, normalized_config, result_entries, credits_before, {}, budget_stop_reason)
        if budget_stop_reason:
            break
    credits_client = factory()
    credits_after = await _openrouter_metadata_snapshot(credits_client, method_name="get_credits")
    await _maybe_close(credits_client)
    _write_micro_batch_dynamic(paths, normalized_config, result_entries, credits_before, credits_after, budget_stop_reason)
    return paths["run_index_jsonl"]


async def _openrouter_metadata_snapshot(client: Any, *, method_name: str) -> dict[str, Any]:
    method = getattr(client, method_name, None)
    if method is None:
        return {
            "schema_version": "v1",
            "source": f"openrouter_{method_name}",
            "status": "unavailable",
            "reason": f"client_has_no_{method_name}",
        }
    result = await method()
    return {
        "schema_version": "v1",
        "source": f"openrouter_{method_name}",
        "status": "ok" if getattr(result, "ok", False) else "error",
        "status_code": getattr(result, "status_code", None),
        "request_id": getattr(result, "request_id", None),
        "error": getattr(result, "error", None),
        "error_type": getattr(result, "error_type", None),
        "data": getattr(result, "response_json", None),
    }


async def _maybe_close(client: Any) -> None:
    close = getattr(client, "aclose", None)
    if close is not None:
        await close()


def _read_existing_run_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    rows = parsed.get("runs") if isinstance(parsed, dict) else []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _micro_model_ids(config: dict[str, Any]) -> list[str]:
    return [str(row["openrouter_model_id"]) for row in _micro_model_configs(config)]


def _micro_model_configs(config: dict[str, Any]) -> list[dict[str, Any]]:
    values = config.get("model_ids") or config.get("models") or []
    model_configs: list[dict[str, Any]] = []
    if isinstance(values, list):
        for value in values:
            if isinstance(value, str):
                model_configs.append({"openrouter_model_id": value, "reasoning": _dict(config.get("reasoning")) or None})
            elif isinstance(value, dict):
                model_id = value.get("openrouter_model_id") or value.get("model_id") or value.get("id")
                if isinstance(model_id, str):
                    reasoning = value.get("reasoning") if isinstance(value.get("reasoning"), dict) else config.get("reasoning")
                    model_configs.append(
                        {
                            "openrouter_model_id": model_id,
                            "model_display_name": value.get("model_display_name") or value.get("display_name"),
                            "reasoning": reasoning if isinstance(reasoning, dict) else None,
                        }
                    )
    return model_configs


def _micro_should_stop_for_budget(config: dict[str, Any], entries: list[dict[str, Any]]) -> str | None:
    if str(config.get("budget_policy") or "stop_immediately") != "stop_immediately":
        return None
    token_budget = config.get("token_budget")
    if isinstance(token_budget, (int, float)):
        actual_tokens = 0
        for entry in entries:
            usage_path = Path(str(entry.get("run_dir"))) / "usage.json"
            usage = _read_json(usage_path)
            totals = usage.get("totals") if isinstance(usage.get("totals"), dict) else {}
            total_tokens = totals.get("total_tokens") if isinstance(totals, dict) else None
            if isinstance(total_tokens, (int, float)):
                actual_tokens += int(total_tokens)
        if actual_tokens >= int(token_budget):
            return f"actual_tokens_{actual_tokens}_meets_or_exceeds_budget_{int(token_budget)}"
    return None


def _write_micro_batch_dynamic(
    paths: dict[str, Path],
    config: dict[str, Any],
    entries: list[dict[str, Any]],
    credits_before: dict[str, Any],
    credits_after: dict[str, Any],
    budget_stop_reason: str | None,
) -> None:
    _write_json(paths["run_index"], {"schema_version": "v1", "runs": entries})
    _write_jsonl(paths["run_index_jsonl"], entries)
    _write_jsonl(paths["results"], entries)
    leaderboard = _micro_leaderboard(entries)
    _write_json(paths["leaderboard"], leaderboard)
    _write_json(paths["category_breakdown"], _micro_category_breakdown(entries))
    _write_json(paths["scorecard_summary"], {"schema_version": "v1", "batch_type": "micro_suite", "leaderboard": leaderboard})
    _write_json(paths["statistical_summary"], _micro_statistical_summary(entries))
    _write_json(paths["usage_summary"], _micro_usage_summary(entries))
    _write_json(paths["token_report"], _micro_token_report(entries))
    _write_json(paths["cost_report"], _micro_cost_report(entries))
    review_cost_aggregate = build_review_cost_aggregate(
        batch_id=str(config.get("batch_id") or "micro_suite"),
        batch_type="micro_suite",
        entries=entries,
    )
    _write_json(paths["review_cost_aggregate"], review_cost_aggregate)
    _write_jsonl(paths["review_cost_calls"], usage_calls_jsonl(review_cost_aggregate))
    _write_json(
        paths["budget_report"],
        {
            "schema_version": "v1",
            "budget_report_version": "micro_batch_budget_report_v1",
            "budget_policy": config.get("budget_policy"),
            "token_budget": config.get("token_budget"),
            "actual_tokens": _micro_total_tokens(entries),
            "cost_budget": config.get("cost_budget"),
            "actual_cost": _micro_total_cost(entries),
            "stop_reason": budget_stop_reason,
            "credits_before": credits_before,
            "credits_after": credits_after,
            "source": "openrouter_actuals_only",
            "local_tokenizer_estimates_used": False,
        },
    )
    _write_json(paths["batch_manifest"], _micro_batch_manifest(config, entries, paths))
    _write_json(paths["artifact_manifest"], _simple_artifact_manifest(paths))


def _micro_leaderboard(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for entry in entries:
        model_id = str(entry.get("model_id") or "unknown")
        row = by_model.setdefault(model_id, {"model_id": model_id, "scenario_count": 0, "completed_count": 0, "scores": []})
        row["scenario_count"] += 1
        if entry.get("status") == "completed":
            row["completed_count"] += 1
        result = _dict(entry.get("result"))
        score = _dict(result.get("score"))
        total = score.get("total")
        if isinstance(total, (int, float)):
            row["scores"].append(float(total))
    rows: list[dict[str, Any]] = []
    for row in by_model.values():
        scores = row.pop("scores")
        row["average_score"] = sum(scores) / len(scores) if scores else None
        row["completion_rate"] = row["completed_count"] / row["scenario_count"] if row["scenario_count"] else 0
        rows.append(row)
    rows.sort(key=lambda row: (row.get("average_score") or 0, row.get("completion_rate") or 0), reverse=True)
    return {
        "schema_version": "v1",
        "leaderboard_version": "micro_suite_leaderboard_v1",
        "rankings": rows,
    }


def _micro_category_breakdown(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, dict[str, Any]] = {}
    for entry in entries:
        result = _dict(entry.get("result"))
        category = str(result.get("category") or "unknown")
        score = _dict(result.get("score"))
        total = score.get("total")
        row = by_category.setdefault(category, {"category": category, "count": 0, "scores": []})
        row["count"] += 1
        if isinstance(total, (int, float)):
            row["scores"].append(float(total))
    rows = []
    for row in by_category.values():
        scores = row.pop("scores")
        row["average_score"] = sum(scores) / len(scores) if scores else None
        rows.append(row)
    return {"schema_version": "v1", "category_breakdown_version": "micro_suite_category_breakdown_v1", "categories": rows}


def _micro_statistical_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    scores: list[float] = []
    for entry in entries:
        result = _dict(entry.get("result"))
        score = _dict(result.get("score"))
        total = score.get("total")
        if isinstance(total, (int, float)):
            scores.append(float(total))
    return {
        "schema_version": "v1",
        "statistical_summary_version": "micro_suite_statistical_summary_v1",
        "scenario_count": len(entries),
        "completed_count": sum(1 for entry in entries if entry.get("status") == "completed"),
        "score": {
            "count": len(scores),
            "mean": sum(scores) / len(scores) if scores else None,
            "min": min(scores) if scores else None,
            "max": max(scores) if scores else None,
        },
    }


def _micro_usage_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "usage_accounting_version": "micro_batch_usage_summary_v1",
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "total_tokens": _micro_total_tokens(entries),
        "total_cost": _micro_total_cost(entries),
    }


def _micro_token_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "usage_accounting_version": "micro_batch_token_report_v1",
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "totals": _micro_usage_totals(entries),
        "by_model": _micro_usage_by_key(entries, "model_id"),
        "by_run": _micro_usage_by_key(entries, "run_id"),
    }


def _micro_cost_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "usage_accounting_version": "micro_batch_cost_report_v1",
        "source": "openrouter_actuals_only",
        "local_tokenizer_estimates_used": False,
        "total_actual_cost": _micro_total_cost(entries),
        "by_model": _micro_usage_by_key(entries, "model_id"),
        "by_run": _micro_usage_by_key(entries, "run_id"),
    }


def _micro_total_tokens(entries: list[dict[str, Any]]) -> int:
    return int(_micro_usage_totals(entries).get("total_tokens") or 0)


def _micro_total_cost(entries: list[dict[str, Any]]) -> float:
    return round(float(_micro_usage_totals(entries).get("cost") or 0.0), 10)


def _micro_usage_totals(entries: list[dict[str, Any]]) -> dict[str, Any]:
    total = _empty_usage_totals()
    for entry in entries:
        _add_usage_totals(total, _run_usage_totals(entry))
    total["cost"] = round(float(total["cost"]), 10)
    return total


def _micro_usage_by_key(entries: list[dict[str, Any]], key: str) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        group_key = str(entry.get(key) or "unknown")
        row = grouped.setdefault(group_key, _empty_usage_totals())
        row["run_count"] = int(row.get("run_count") or 0) + 1
        _add_usage_totals(row, _run_usage_totals(entry))
    for row in grouped.values():
        row["cost"] = round(float(row["cost"]), 10)
    return grouped


def _run_usage_totals(entry: dict[str, Any]) -> dict[str, Any]:
    usage = _read_json(Path(str(entry.get("run_dir"))) / "usage.json")
    totals = usage.get("totals") if isinstance(usage.get("totals"), dict) else {}
    row = _empty_usage_totals()
    if not isinstance(totals, dict):
        return row
    for key in row:
        value = totals.get(key)
        if isinstance(value, (int, float)):
            row[key] = float(value) if key == "cost" else int(value)
    if not isinstance(totals.get("input_tokens"), (int, float)) and isinstance(totals.get("prompt_tokens"), (int, float)):
        row["input_tokens"] = int(totals["prompt_tokens"])
    if not isinstance(totals.get("output_tokens"), (int, float)) and isinstance(totals.get("completion_tokens"), (int, float)):
        row["output_tokens"] = int(totals["completion_tokens"])
    return row


def _empty_usage_totals() -> dict[str, Any]:
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
        "cost": 0.0,
        "latency_ms": 0,
    }


def _add_usage_totals(target: dict[str, Any], row: dict[str, Any]) -> None:
    for key, value in row.items():
        if not isinstance(value, (int, float)):
            continue
        if key == "cost":
            target[key] = float(target.get(key) or 0.0) + float(value)
        else:
            target[key] = int(target.get(key) or 0) + int(value)


def _micro_batch_manifest(config: dict[str, Any], entries: list[dict[str, Any]], paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "batch_manifest_version": "micro_suite_batch_manifest_v1",
        "batch_id": config.get("batch_id"),
        "batch_type": "micro_suite",
        "batch_dir": str(paths["batch_dir"]),
        "run_count": len(entries),
        "runs": [
            {
                "run_index": entry.get("run_index"),
                "run_id": entry.get("run_id"),
                "run_dir": entry.get("run_dir"),
                "status": entry.get("status"),
                "scenario_id": entry.get("scenario_id"),
                "model_id": entry.get("model_id"),
            }
            for entry in entries
        ],
    }


def _simple_artifact_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    batch_dir = paths["batch_dir"]
    artifacts = []
    for label, path in sorted(paths.items()):
        if label == "batch_dir":
            continue
        artifacts.append({"label": label, "path": str(path), "exists": path.exists()})
    return {
        "schema_version": "v1",
        "manifest_version": "batch_artifact_manifest_v1",
        "batch_dir": str(batch_dir),
        "artifacts": artifacts,
    }


def _safe_micro_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in value) or "model"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m monopoly_arena.batch_run")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--runs-dir", type=str, default=None)
    args = parser.parse_args(argv)

    config_path = resolve_repo_path(args.config)
    runs_dir = resolve_repo_path(args.runs_dir) if args.runs_dir else None
    config = _load_config(config_path)
    asyncio.run(run_batch(config, runs_dir=runs_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
