from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

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

from .settings import Settings


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
            system_prompt=request.system_prompt,
            reasoning=request.reasoning,
            prompt_condition=request.prompt_condition,
            baseline=request.baseline,
        ),
        runs_dir=settings.runs_dir,
        openrouter_factory=openrouter_factory,
    )
    return {"run_id": result["run_id"], "result": result}


async def run_micro_batch(
    *,
    settings: Settings,
    request: MicroBatchRequest,
    openrouter_factory: Callable[[], OpenRouterClient],
) -> dict[str, Any]:
    return await run_batch(
        suite_id=request.suite_id,
        model_ids=request.openrouter_model_ids,
        baseline=request.baseline,
        prompt_condition=request.prompt_condition,
        reasoning=request.reasoning,
        scenario_ids=request.scenario_ids,
        runs_dir=settings.runs_dir,
        openrouter_factory=openrouter_factory,
    )


def get_micro_scenario_detail(scenario_id: str) -> dict[str, Any]:
    return load_scenario(scenario_id)


def get_micro_run(run_id: str, *, runs_dir: Path) -> dict[str, Any]:
    return get_run(run_id, runs_dir=runs_dir)


def get_micro_batch(batch_id: str, *, runs_dir: Path) -> dict[str, Any]:
    return get_batch(batch_id, runs_dir=runs_dir)


def get_micro_batch_leaderboard(batch_id: str, *, runs_dir: Path) -> dict[str, Any]:
    return get_batch_leaderboard(batch_id, runs_dir=runs_dir)
