from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, AsyncIterator, Callable

from monopoly_arena import OpenRouterClient
from monopoly_microbench import (
    MicroBatchRequest,
    MicroRunConfig,
    MicroRunRequest,
    get_batch,
    get_batch_leaderboard,
    get_run,
    get_suite,
    list_scenario_summaries,
    list_suites,
    load_scenario,
    run_batch,
    run_scenario,
)
from monopoly_microbench.artifacts import batch_dir, compact_result_for_jsonl
from monopoly_microbench.runner import build_leaderboard
from monopoly_telemetry import build_experiment_manifest, build_review_cost_aggregate, usage_calls_jsonl
from monopoly_telemetry.writer_jsonl import append_jsonl

from .settings import Settings


MICRO_BATCH_PARALLEL_LIMIT = 20


def list_micro_scenario_summaries() -> list[dict[str, Any]]:
    return list_scenario_summaries()


def list_micro_suites() -> list[dict[str, Any]]:
    return list_suites()


def get_micro_suite(suite_id: str) -> dict[str, Any]:
    return get_suite(suite_id)


async def run_micro_scenario(
    *,
    settings: Settings,
    request: MicroRunRequest,
    openrouter_factory: Callable[[], OpenRouterClient],
) -> dict[str, Any]:
    result = await run_scenario(
        MicroRunConfig(
            scenario_id=request.scenario_id,
            openrouter_model_id=request.openrouter_model_id,
            name=request.name,
            reasoning=request.reasoning,
            prompt_condition=request.prompt_condition,
        ),
        runs_dir=settings.runs_dir,
        openrouter_factory=openrouter_factory,
    )
    return {"run_id": result["run_id"], "result": result}


async def stream_micro_scenario(
    *,
    settings: Settings,
    request: MicroRunRequest,
) -> AsyncIterator[str]:
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def stream_callback(event: dict[str, Any]) -> None:
        await queue.put({"event": "llm_delta", "data": event})

    def openrouter_factory() -> OpenRouterClient:
        return OpenRouterClient(stream_callback=stream_callback)

    async def run() -> dict[str, Any]:
        return await run_micro_scenario(
            settings=settings,
            request=request,
            openrouter_factory=openrouter_factory,
        )

    task = asyncio.create_task(run())
    yield _sse("status", {"state": "started"})
    try:
        while not task.done():
            try:
                item = await asyncio.wait_for(queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            yield _sse(item["event"], item["data"])
        while not queue.empty():
            item = queue.get_nowait()
            yield _sse(item["event"], item["data"])
        result = await task
        yield _sse("result", result)
        yield _sse("status", {"state": "complete"})
    except asyncio.CancelledError:
        task.cancel()
        raise
    except Exception as exc:
        yield _sse("error", {"message": str(exc)})


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'), ensure_ascii=True)}\n\n"


async def run_micro_batch(
    *,
    settings: Settings,
    request: MicroBatchRequest,
    openrouter_factory: Callable[[], OpenRouterClient],
) -> dict[str, Any]:
    return await run_batch(
        suite_id=request.suite_id,
        model_ids=request.openrouter_model_ids,
        prompt_condition=request.prompt_condition,
        reasoning=request.reasoning,
        scenario_ids=request.scenario_ids,
        runs_dir=settings.runs_dir,
        openrouter_factory=openrouter_factory,
    )


async def stream_micro_batch(
    *,
    settings: Settings,
    request: MicroBatchRequest,
) -> AsyncIterator[str]:
    root = settings.runs_dir
    batch_id = f"micro-batch-{request.suite_id}-{int(time.time() * 1000)}"
    out_dir = batch_dir(root, batch_id)
    suite = get_suite(request.suite_id)
    selected = request.scenario_ids or suite["scenario_ids"]
    model_targets = request.openrouter_model_ids
    if not model_targets:
        raise ValueError("At least one OpenRouter model id is required.")
    config = {
        "batch_id": batch_id,
        "suite_id": request.suite_id,
        "model_ids": request.openrouter_model_ids,
        "prompt_condition": request.prompt_condition,
        "scenario_ids": selected,
        "reasoning": request.reasoning,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=True), encoding="utf-8")
    (out_dir / "experiment_manifest.json").write_text(
        json.dumps(
            build_experiment_manifest(
                experiment_id=batch_id,
                benchmark_tracks=["micro_suite"],
                models=[
                    {"openrouter_model_id": model_id, "reasoning": request.reasoning}
                    for model_id in request.openrouter_model_ids
                ],
                reasoning_policy=request.reasoning,
                batch_type="micro_suite",
                run_count=len(model_targets) * len(selected),
            ),
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    results: list[dict[str, Any]] = []

    async def run_one(scenario_id: str, model: str | None) -> None:
        async def stream_callback(event: dict[str, Any]) -> None:
            await queue.put(
                {
                    "event": "llm_delta",
                    "data": {
                        "scenario_id": scenario_id,
                        "model": model,
                        **event,
                    },
                }
            )

        def openrouter_factory() -> OpenRouterClient:
            return OpenRouterClient(stream_callback=stream_callback)

        await queue.put({"event": "scenario_started", "data": {"scenario_id": scenario_id, "model": model}})
        try:
            result = await run_scenario(
                MicroRunConfig(
                    scenario_id=scenario_id,
                    openrouter_model_id=model,
                    prompt_condition=request.prompt_condition,
                    reasoning=request.reasoning,
                ),
                runs_dir=root,
                openrouter_factory=openrouter_factory,
            )
            append_jsonl(out_dir / "results.jsonl", compact_result_for_jsonl(result))
            result_event = {
                "scenario_id": scenario_id,
                "model": result["model"]["openrouter_model_id"],
                "run_id": result["run_id"],
                "action": result["outcome"]["action"],
                "score": result["score"],
                "retry_used": result["outcome"]["retry_used"],
                "fallback_used": result["outcome"]["fallback_used"],
                "latency_ms": result["outcome"]["latency_ms"],
            }
            await queue.put({"event": "scenario_result", "data": result_event})
            await queue.put({"event": "task_done", "data": {"scenario_id": scenario_id, "result": result}})
        except Exception as exc:  # pragma: no cover - failure artifact path
            append_jsonl(out_dir / "failures.jsonl", {"scenario_id": scenario_id, "model": model, "error": str(exc)})
            await queue.put({"event": "scenario_error", "data": {"scenario_id": scenario_id, "model": model, "message": str(exc)}})
            await queue.put({"event": "task_done", "data": {"scenario_id": scenario_id, "result": None}})

    work_items = [(scenario_id, model) for model in model_targets for scenario_id in selected]
    yield _sse(
        "status",
        {
            "state": "started",
            "batch_id": batch_id,
            "scenario_count": len(selected),
            "task_count": len(work_items),
            "parallel_limit": MICRO_BATCH_PARALLEL_LIMIT,
        },
    )
    try:
        for wave_index, start in enumerate(range(0, len(work_items), MICRO_BATCH_PARALLEL_LIMIT), start=1):
            wave_items = work_items[start : start + MICRO_BATCH_PARALLEL_LIMIT]
            tasks = [asyncio.create_task(run_one(scenario_id, model)) for scenario_id, model in wave_items]
            yield _sse(
                "status",
                {
                    "state": "wave_started",
                    "batch_id": batch_id,
                    "wave_index": wave_index,
                    "wave_size": len(tasks),
                    "wave_scenario_ids": [scenario_id for scenario_id, _model in wave_items],
                    "completed_count": len(results),
                    "task_count": len(work_items),
                },
            )
            completed_in_wave = 0
            while completed_in_wave < len(tasks):
                item = await queue.get()
                if item["event"] == "task_done":
                    result_item = item["data"].get("result")
                    if result_item is not None:
                        results.append(result_item)
                    completed_in_wave += 1
                    continue
                yield _sse(item["event"], item["data"])
            for task in tasks:
                await task
            yield _sse(
                "status",
                {
                    "state": "wave_complete",
                    "batch_id": batch_id,
                    "wave_index": wave_index,
                    "completed_count": len(results),
                    "task_count": len(work_items),
                },
            )
        leaderboard = build_leaderboard(results)
        (out_dir / "leaderboard.json").write_text(json.dumps(leaderboard, indent=2, ensure_ascii=True), encoding="utf-8")
        (out_dir / "category_breakdown.json").write_text(
            json.dumps(leaderboard.get("category_breakdown", {}), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        _write_stream_batch_usage_artifacts(out_dir, batch_id=batch_id, results=results)
        yield _sse("batch_result", {"batch_id": batch_id, "leaderboard": leaderboard})
        yield _sse("status", {"state": "complete", "batch_id": batch_id})
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        yield _sse("error", {"message": str(exc), "batch_id": batch_id})


def _write_stream_batch_usage_artifacts(out_dir: Path, *, batch_id: str, results: list[dict[str, Any]]) -> None:
    entries = [
        {
            "run_index": index,
            "run_id": result.get("run_id"),
            "status": "completed",
            "run_dir": str(out_dir.parent.parent / "micro" / str(result.get("run_id") or "")),
            "scenario_id": result.get("scenario_id"),
            "model_id": _model_id_from_result(result),
            "result": result,
        }
        for index, result in enumerate(results)
    ]
    aggregate = build_review_cost_aggregate(batch_id=batch_id, batch_type="micro_suite", entries=entries)
    (out_dir / "review_cost_aggregate.json").write_text(
        json.dumps(aggregate, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    (out_dir / "review_cost_calls.jsonl").write_text(
        "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in usage_calls_jsonl(aggregate)),
        encoding="utf-8",
    )


def _model_id_from_result(result: dict[str, Any]) -> str | None:
    model = result.get("model")
    if not isinstance(model, dict):
        return None
    value = model.get("openrouter_model_id")
    return str(value) if isinstance(value, str) else None


def get_micro_scenario_detail(scenario_id: str) -> dict[str, Any]:
    return load_scenario(scenario_id)


def get_micro_run(run_id: str, *, runs_dir: Path) -> dict[str, Any]:
    return get_run(run_id, runs_dir=runs_dir)


def get_micro_batch(batch_id: str, *, runs_dir: Path) -> dict[str, Any]:
    return get_batch(batch_id, runs_dir=runs_dir)


def get_micro_batch_leaderboard(batch_id: str, *, runs_dir: Path) -> dict[str, Any]:
    return get_batch_leaderboard(batch_id, runs_dir=runs_dir)
