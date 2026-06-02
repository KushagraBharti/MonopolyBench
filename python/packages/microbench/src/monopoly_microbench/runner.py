from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable

from monopoly_arena import OpenRouterClient, build_single_player_config
from monopoly_arena.decision_resolver import SharedDecisionResolver
from monopoly_arena.prompting import PromptMemory, build_space_key_by_index
from monopoly_telemetry import write_usage_artifacts
from monopoly_telemetry.writer_jsonl import append_jsonl

from .artifacts import batch_dir, compact_result_for_jsonl, micro_run_files
from .catalog import get_suite, load_scenario
from .paths import default_runs_dir
from .scorer import score_action


@dataclass(frozen=True)
class MicroRunConfig:
    scenario_id: str
    openrouter_model_id: str | None = None
    name: str | None = None
    reasoning: dict[str, Any] | None = None
    prompt_condition: str = "live_game"
    run_id: str | None = None


async def run_scenario(
    config: MicroRunConfig,
    *,
    runs_dir: Path | None = None,
    openrouter_factory: Callable[[], Any] = OpenRouterClient,
) -> dict[str, Any]:
    scenario = load_scenario(config.scenario_id)
    decision = json.loads(json.dumps(scenario["decision_point"]))
    focal_player_id = scenario["focal_player_id"]
    focal_name = next(
        (player.get("name") for player in decision["state"]["players"] if player["player_id"] == focal_player_id),
        focal_player_id,
    )
    player_config = build_single_player_config(
        player_id=focal_player_id,
        name=config.name or str(focal_name),
        openrouter_model_id=config.openrouter_model_id,
        system_prompt=_system_prompt_for_condition(config.prompt_condition),
        reasoning=config.reasoning,
    )
    run_id = config.run_id or generate_micro_run_id(
        scenario_id=scenario["scenario_id"],
        model_id=player_config.openrouter_model_id,
        prompt_condition=config.prompt_condition,
    )
    run_files = micro_run_files(runs_dir or default_runs_dir(), run_id)
    scenario_for_run = json.loads(json.dumps(scenario))
    scenario_for_run["run_id"] = run_id
    scenario_for_run["prompt_condition"] = config.prompt_condition
    scenario_for_run["decision_point"]["run_id"] = run_id
    if config.prompt_condition != "live_game":
        scenario_for_run["decision_point"]["micro_prompt_condition"] = config.prompt_condition
    scenario_for_run["decision_point"]["state"]["run_id"] = run_id
    decision = scenario_for_run["decision_point"]
    run_files.run_dir.mkdir(parents=True, exist_ok=True)
    if run_files.quality_dir is not None:
        run_files.quality_dir.mkdir(parents=True, exist_ok=True)
    (run_files.run_dir / "scenario.json").write_text(
        json.dumps(scenario_for_run, separators=(",", ":"), ensure_ascii=True),
        encoding="utf-8",
    )
    run_files.write_snapshot(decision["state"])

    resolver = SharedDecisionResolver(
        openrouter=openrouter_factory(),
        run_files=run_files,
        prompt_memory=PromptMemory(space_key_by_index=build_space_key_by_index()),
        space_key_by_index=build_space_key_by_index(),
    )

    async def log_writer(entry: dict[str, Any]) -> None:
        run_files.write_decision(entry)

    outcome = await resolver.resolve_decision(decision=decision, player_config=player_config, log_writer=log_writer)
    close = getattr(resolver._openrouter, "aclose", None)
    if close is not None:
        maybe = close()
        if asyncio.iscoroutine(maybe):
            await maybe
    if outcome.fallback_used:
        raise RuntimeError(f"Micro model run failed without a valid action: {outcome.fallback_reason or 'fallback_used'}")
    action = outcome.action
    latency_ms = _latency_from_attempts(outcome.attempts)

    run_files.write_action(
        {
            "decision_id": decision["decision_id"],
            "actor_player_id": focal_player_id,
            "decision_type": decision["decision_type"],
            "turn_index": decision["turn_index"],
            "action": action,
            "prompt_condition": config.prompt_condition,
        }
    )
    score = score_action(scenario_for_run, action, fallback_used=bool(outcome.fallback_used))
    result = {
        "schema_version": "v1",
        "run_id": run_id,
        "suite_id": scenario["suite_id"],
        "scenario_id": scenario["scenario_id"],
        "category": scenario["category"],
        "model": {
            "openrouter_model_id": player_config.openrouter_model_id,
            "model_display_name": player_config.model_display_name,
            "reasoning": player_config.reasoning,
        },
        "prompt_condition": config.prompt_condition,
        "outcome": {
            "action": action,
            "retry_used": bool(outcome.retry_used),
            "fallback_used": bool(outcome.fallback_used),
            "fallback_reason": outcome.fallback_reason,
            "latency_ms": latency_ms,
        },
        "score": score,
    }
    (run_files.run_dir / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), ensure_ascii=True),
        encoding="utf-8",
    )
    summary = {
        "run_id": run_id,
        "mode": "micro",
        "scenario_id": scenario["scenario_id"],
        "suite_id": scenario["suite_id"],
        "category": scenario["category"],
        "title": scenario["title"],
        "description": scenario["description"],
        "tags": scenario["tags"],
        "focal_player_id": focal_player_id,
        "decision_id": decision["decision_id"],
        "decision_type": decision["decision_type"],
        "prompt_condition": config.prompt_condition,
        "player": {
            "player_id": player_config.player_id,
            "name": player_config.name,
            "openrouter_model_id": player_config.openrouter_model_id,
            "model_display_name": player_config.model_display_name,
            "reasoning": player_config.reasoning,
        },
        "result": {
            "retry_used": bool(outcome.retry_used),
            "fallback_used": bool(outcome.fallback_used),
            "fallback_reason": outcome.fallback_reason,
            "final_action": action,
            "latency_ms": latency_ms,
            "score": score,
        },
    }
    run_files.write_summary(summary)
    write_usage_artifacts(run_files)
    run_files.write_json_artifact(
        run_files.pricing_snapshot_path,
        {
            "schema_version": "v1",
            "source": "openrouter_get_models",
            "status": "unavailable",
            "reason": "micro_run_resolver_closed_before_metadata_snapshot",
        },
    )
    run_files.write_artifact_manifest()
    return result


async def run_suite(
    suite_id: str,
    *,
    model_id: str | None = None,
    prompt_condition: str = "live_game",
    reasoning: dict[str, Any] | None = None,
    runs_dir: Path | None = None,
    openrouter_factory: Callable[[], Any] = OpenRouterClient,
) -> list[dict[str, Any]]:
    suite = get_suite(suite_id)
    results: list[dict[str, Any]] = []
    for scenario_id in suite["scenario_ids"]:
        results.append(
            await run_scenario(
                MicroRunConfig(
                    scenario_id=scenario_id,
                    openrouter_model_id=model_id,
                    prompt_condition=prompt_condition,
                    reasoning=reasoning,
                ),
                runs_dir=runs_dir,
                openrouter_factory=openrouter_factory,
            )
        )
    return results


async def run_batch(
    *,
    suite_id: str,
    model_ids: list[str],
    prompt_condition: str = "live_game",
    reasoning: dict[str, Any] | None = None,
    scenario_ids: list[str] | None = None,
    runs_dir: Path | None = None,
    openrouter_factory: Callable[[], Any] = OpenRouterClient,
) -> dict[str, Any]:
    root = runs_dir or default_runs_dir()
    batch_id = f"micro-batch-{suite_id}-{int(time.time() * 1000)}"
    out_dir = batch_dir(root, batch_id)
    suite = get_suite(suite_id)
    selected = scenario_ids or suite["scenario_ids"]
    config = {
        "batch_id": batch_id,
        "suite_id": suite_id,
        "model_ids": model_ids,
        "prompt_condition": prompt_condition,
        "scenario_ids": selected,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=True), encoding="utf-8")
    failures_path = out_dir / "failures.jsonl"
    result_items: list[dict[str, Any]] = []
    model_targets = model_ids
    if not model_targets:
        raise ValueError("At least one OpenRouter model id is required.")
    for model in model_targets:
        for scenario_id in selected:
            try:
                result = await run_scenario(
                    MicroRunConfig(
                        scenario_id=scenario_id,
                        openrouter_model_id=model,
                        prompt_condition=prompt_condition,
                        reasoning=reasoning,
                    ),
                    runs_dir=root,
                    openrouter_factory=openrouter_factory,
                )
            except Exception as exc:
                append_jsonl(failures_path, {"scenario_id": scenario_id, "model": model, "error": str(exc)})
                raise
            result_items.append(result)
            append_jsonl(out_dir / "results.jsonl", compact_result_for_jsonl(result))
    leaderboard = build_leaderboard(result_items)
    (out_dir / "leaderboard.json").write_text(json.dumps(leaderboard, indent=2, ensure_ascii=True), encoding="utf-8")
    (out_dir / "category_breakdown.json").write_text(
        json.dumps(leaderboard.get("category_breakdown", {}), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    return {"batch_id": batch_id, "leaderboard": leaderboard}


async def run_batch_with_progress(
    *,
    suite_id: str,
    model_id: str,
    prompt_condition: str = "live_game",
    reasoning: dict[str, Any] | None = None,
    scenario_ids: list[str] | None = None,
    runs_dir: Path | None = None,
    openrouter_factory: Callable[[], Any] = OpenRouterClient,
    progress_callback: Callable[[dict[str, Any]], Awaitable[None] | None] | None = None,
) -> dict[str, Any]:
    root = runs_dir or default_runs_dir()
    batch_id = f"micro-batch-{suite_id}-{int(time.time() * 1000)}"
    out_dir = batch_dir(root, batch_id)
    suite = get_suite(suite_id)
    selected = scenario_ids or suite["scenario_ids"]
    config = {
        "batch_id": batch_id,
        "suite_id": suite_id,
        "model_ids": [model_id],
        "prompt_condition": prompt_condition,
        "scenario_ids": selected,
        "continue_on_failure": True,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=True), encoding="utf-8")
    result_items: list[dict[str, Any]] = []
    failure_items: list[dict[str, Any]] = []
    await _emit_progress(
        progress_callback,
        {
            "event": "batch_started",
            "batch_id": batch_id,
            "suite_id": suite_id,
            "model": model_id,
            "total": len(selected),
        },
    )
    for index, scenario_id in enumerate(selected, start=1):
        await _emit_progress(
            progress_callback,
            {
                "event": "scenario_started",
                "batch_id": batch_id,
                "scenario_id": scenario_id,
                "index": index,
                "total": len(selected),
            },
        )
        try:
            result = await run_scenario(
                MicroRunConfig(
                    scenario_id=scenario_id,
                    openrouter_model_id=model_id,
                    prompt_condition=prompt_condition,
                    reasoning=reasoning,
                ),
                runs_dir=root,
                openrouter_factory=openrouter_factory,
            )
        except Exception as exc:  # pragma: no cover - exercised through integration paths
            failure = {
                "scenario_id": scenario_id,
                "model": model_id,
                "error": str(exc),
            }
            failure_items.append(failure)
            append_jsonl(out_dir / "failures.jsonl", failure)
            await _emit_progress(
                progress_callback,
                {
                    "event": "scenario_failed",
                    "batch_id": batch_id,
                    "scenario_id": scenario_id,
                    "index": index,
                    "total": len(selected),
                    "failure": failure,
                },
            )
            continue
        result_items.append(result)
        append_jsonl(out_dir / "results.jsonl", compact_result_for_jsonl(result))
        await _emit_progress(
            progress_callback,
            {
                "event": "scenario_completed",
                "batch_id": batch_id,
                "scenario_id": scenario_id,
                "index": index,
                "total": len(selected),
                "result": result,
            },
        )
    leaderboard = build_leaderboard(result_items)
    (out_dir / "leaderboard.json").write_text(json.dumps(leaderboard, indent=2, ensure_ascii=True), encoding="utf-8")
    (out_dir / "category_breakdown.json").write_text(
        json.dumps(leaderboard.get("category_breakdown", {}), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    await _emit_progress(
        progress_callback,
        {
            "event": "batch_completed",
            "batch_id": batch_id,
            "total": len(selected),
            "completed": len(result_items),
            "failed": len(failure_items),
            "leaderboard": leaderboard,
        },
    )
    return {"batch_id": batch_id, "leaderboard": leaderboard, "results": result_items, "failures": failure_items}


def get_run(run_id: str, *, runs_dir: Path | None = None) -> dict[str, Any]:
    run_dir = (runs_dir or default_runs_dir()) / "micro" / run_id
    if not run_dir.exists():
        raise FileNotFoundError(run_id)
    payload = {
        "run_id": run_id,
        "summary": json.loads((run_dir / "summary.json").read_text(encoding="utf-8")),
        "scenario": json.loads((run_dir / "scenario.json").read_text(encoding="utf-8")),
        "result": json.loads((run_dir / "result.json").read_text(encoding="utf-8")),
        "decision_bundle": None,
        "artifact_paths": _artifact_paths(run_dir),
    }
    decisions = _read_jsonl(run_dir / "decisions.jsonl")
    resolved = next((entry for entry in reversed(decisions) if entry.get("phase") == "decision_resolved"), None)
    if resolved is not None:
        payload["decision_bundle"] = {
            "decision_id": resolved["decision_id"],
            "decision_type": resolved["decision_type"],
            "final_action": resolved.get("final_action"),
            "retry_used": resolved.get("retry_used"),
            "fallback_used": resolved.get("fallback_used"),
            "fallback_reason": resolved.get("fallback_reason"),
            "timing": {"latency_ms": resolved.get("latency_ms")},
            "attempts": resolved.get("attempts", []),
        }
    else:
        payload["decision_bundle"] = {
            "decision_id": payload["scenario"]["decision_point"]["decision_id"],
            "decision_type": payload["scenario"]["decision_point"]["decision_type"],
            "final_action": payload["result"]["outcome"]["action"],
            "retry_used": payload["result"]["outcome"]["retry_used"],
            "fallback_used": payload["result"]["outcome"]["fallback_used"],
            "fallback_reason": payload["result"]["outcome"]["fallback_reason"],
            "timing": {"latency_ms": payload["result"]["outcome"]["latency_ms"]},
            "attempts": [],
        }
    return payload


def get_batch(batch_id: str, *, runs_dir: Path | None = None) -> dict[str, Any]:
    path = (runs_dir or default_runs_dir()) / "micro_batches" / batch_id
    if not path.exists():
        raise FileNotFoundError(batch_id)
    return {
        "batch_id": batch_id,
        "config": json.loads((path / "config.json").read_text(encoding="utf-8")),
        "leaderboard": json.loads((path / "leaderboard.json").read_text(encoding="utf-8")),
        "results": _read_jsonl(path / "results.jsonl"),
        "failures": _read_jsonl(path / "failures.jsonl"),
    }


def get_batch_leaderboard(batch_id: str, *, runs_dir: Path | None = None) -> dict[str, Any]:
    return get_batch(batch_id, runs_dir=runs_dir)["leaderboard"]


def export_batch(batch_id: str, *, fmt: str, out: Path, runs_dir: Path | None = None) -> Path:
    batch = get_batch(batch_id, runs_dir=runs_dir)
    rows = batch["results"]
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "jsonl":
        out.write_text("\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n", encoding="utf-8")
        return out
    if fmt != "csv":
        raise ValueError("Export format must be csv or jsonl.")
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in rows for key in row}))
        writer.writeheader()
        writer.writerows(rows)
    return out


def score_run(run_id: str, *, runs_dir: Path | None = None, write: bool = False) -> dict[str, Any]:
    detail = get_run(run_id, runs_dir=runs_dir)
    scenario = detail["scenario"]
    action = detail["result"]["outcome"]["action"]
    score = score_action(scenario, action, fallback_used=bool(detail["result"]["outcome"].get("fallback_used")))
    if write:
        run_dir = (runs_dir or default_runs_dir()) / "micro" / run_id
        result = detail["result"]
        result["score"] = score
        (run_dir / "result.json").write_text(json.dumps(result, separators=(",", ":"), ensure_ascii=True), encoding="utf-8")
    return {"run_id": run_id, "score": score}


def build_leaderboard(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_model.setdefault(result["model"]["openrouter_model_id"], []).append(result)
    rows: list[dict[str, Any]] = []
    category_breakdown: dict[str, dict[str, Any]] = {}
    for model, items in sorted(by_model.items()):
        total = sum(float(item["score"]["total"]) for item in items)
        count = len(items)
        categories: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            categories.setdefault(item["category"], []).append(item)
        cat_scores = {
            category: round(sum(float(i["score"]["total"]) for i in cat_items) / len(cat_items), 6)
            for category, cat_items in sorted(categories.items())
        }
        category_breakdown[model] = cat_scores
        rows.append(
            {
                "model": model,
                "scenario_count": count,
                "average_score": round(total / count, 6) if count else 0.0,
                "fallback_rate": round(sum(1 for item in items if item["outcome"]["fallback_used"]) / count, 6) if count else 0.0,
                "retry_rate": round(sum(1 for item in items if item["outcome"]["retry_used"]) / count, 6) if count else 0.0,
                "invalid_rate": round(sum(1 for item in items if item["score"]["label"] == "invalid") / count, 6) if count else 0.0,
                "average_latency_ms": round(
                    sum(int(item["outcome"]["latency_ms"] or 0) for item in items) / count,
                    2,
                )
                if count
                else 0.0,
                "category_scores": cat_scores,
            }
        )
    rows.sort(key=lambda row: float(row["average_score"]), reverse=True)
    return {"rows": rows, "category_breakdown": category_breakdown}


def generate_micro_run_id(*, scenario_id: str, model_id: str, prompt_condition: str = "live_game") -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in f"{scenario_id}-{model_id}-{prompt_condition}")
    if len(safe) > 64:
        digest = hashlib.sha1(safe.encode("utf-8")).hexdigest()[:10]
        safe = f"{safe[:24]}-{digest}"
    return f"micro-{safe}-{int(time.time() * 1000)}"


async def _emit_progress(
    callback: Callable[[dict[str, Any]], Awaitable[None] | None] | None,
    event: dict[str, Any],
) -> None:
    if callback is None:
        return
    maybe = callback(event)
    if asyncio.iscoroutine(maybe):
        await maybe




def _latency_from_attempts(attempts: list[Any]) -> int | None:
    if not attempts:
        return None
    values = [attempt.latency_ms for attempt in attempts if getattr(attempt, "latency_ms", None) is not None]
    return sum(int(value) for value in values) if values else None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _artifact_paths(run_dir: Path) -> dict[str, Any]:
    prompt_dir = run_dir / "prompts"
    state_dir = run_dir / "state"
    return {
        "run_dir": str(run_dir),
        "scenario": str(run_dir / "scenario.json"),
        "result": str(run_dir / "result.json"),
        "summary": str(run_dir / "summary.json"),
        "actions": str(run_dir / "actions.jsonl"),
        "decisions": str(run_dir / "decisions.jsonl"),
        "state": [str(path) for path in sorted(state_dir.glob("*.json"))] if state_dir.exists() else [],
        "prompts": [str(path) for path in sorted(prompt_dir.iterdir())] if prompt_dir.exists() else [],
    }


def _system_prompt_for_condition(prompt_condition: str) -> str | None:
    if prompt_condition != "live_game":
        raise ValueError("Micro prompt condition must be live_game.")
    return None
