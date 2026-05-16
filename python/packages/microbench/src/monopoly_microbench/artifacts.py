from __future__ import annotations

from pathlib import Path
from typing import Any

from monopoly_telemetry import RunFiles, build_run_files


def micro_run_files(runs_dir: Path, run_id: str) -> RunFiles:
    return build_run_files(
        runs_dir / "micro",
        run_id,
        quality_base_dir=runs_dir.parent / "quality_check" / "micro",
    )


def batch_dir(runs_dir: Path, batch_id: str) -> Path:
    path = runs_dir / "micro_batches" / batch_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def compact_result_for_jsonl(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": result["run_id"],
        "suite_id": result["suite_id"],
        "scenario_id": result["scenario_id"],
        "category": result["category"],
        "model": result["model"]["openrouter_model_id"],
        "prompt_condition": result["prompt_condition"],
        "score_total": result["score"]["total"],
        "score_label": result["score"]["label"],
        "retry_used": result["outcome"]["retry_used"],
        "fallback_used": result["outcome"]["fallback_used"],
        "latency_ms": result["outcome"]["latency_ms"],
    }
