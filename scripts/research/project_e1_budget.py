from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PREFLIGHT = "analysis/research_protocol/control_audit/openrouter_preflight.json"
DEFAULT_OUTPUT = "analysis/research_protocol/pilot/budget_projection.json"
PRIMARY_MODELS = (
    "openai/gpt-5.5",
    "anthropic/claude-opus-4.8",
    "google/gemini-3.1-pro-preview",
    "x-ai/grok-4.3",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project the E1 campaign and fixture budget."
    )
    parser.add_argument("--preflight", default=DEFAULT_PREFLIGHT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--full-games", type=int, default=8)
    parser.add_argument("--fixtures", type=int, default=24)
    parser.add_argument("--models", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--fixture-input-tokens", type=int, default=5000)
    parser.add_argument("--fixture-output-tokens", type=int, default=500)
    parser.add_argument("--bootstrap-draws", type=int, default=50000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260729)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    preflight_path = (repo_root / args.preflight).resolve()
    preflight = _read_json(preflight_path)
    pricing_by_model = _base_endpoint_pricing(preflight)

    game_rows: list[dict[str, Any]] = []
    for saved_game in sorted((repo_root / "saved_games").iterdir()):
        if not saved_game.is_dir() or not saved_game.name.startswith("frontier-"):
            continue
        if saved_game.name.startswith("frontier-mini-"):
            continue
        cost_path = saved_game / "run" / "cost_report.json"
        summary_path = saved_game / "run" / "summary.json"
        if not cost_path.exists():
            continue
        cost_report = _read_json(cost_path)
        summary = _read_json(summary_path) if summary_path.exists() else {}
        current_price_estimate, current_price_by_model = _reprice_game(
            cost_report, pricing_by_model
        )
        game_rows.append(
            {
                "saved_game": saved_game.name,
                "run_id": cost_report.get("run_id"),
                "turn_count": summary.get("turn_count"),
                "actual_cost": _number(cost_report.get("total_actual_cost")),
                "current_base_endpoint_price_estimate": current_price_estimate,
                "current_base_endpoint_price_by_model": current_price_by_model,
                "cost_report_sha256": _sha256_file(cost_path),
            }
        )
    if not game_rows:
        raise SystemExit("No medium-frontier saved-game cost reports were found.")

    actual_costs = [float(row["actual_cost"]) for row in game_rows]
    repriced_costs = [
        float(row["current_base_endpoint_price_estimate"])
        for row in game_rows
        if row["current_base_endpoint_price_estimate"] is not None
    ]
    bootstrap_actual = _bootstrap_sums(
        actual_costs,
        sample_size=args.full_games,
        draws=args.bootstrap_draws,
        seed=args.bootstrap_seed,
    )
    bootstrap_repriced = _bootstrap_sums(
        repriced_costs,
        sample_size=args.full_games,
        draws=args.bootstrap_draws,
        seed=args.bootstrap_seed + 1,
    )

    fixture_call_count = args.fixtures * args.models * args.repeats
    calls_per_model = args.fixtures * args.repeats
    fixture_cost_by_model: dict[str, float] = {}
    for model_id in PRIMARY_MODELS:
        pricing = pricing_by_model.get(model_id)
        if not pricing:
            continue
        fixture_cost_by_model[model_id] = (
            0.0
            if pricing.get("billing_mode") == "byok_required"
            else round(
                calls_per_model
                * (
                    args.fixture_input_tokens * float(pricing["prompt"])
                    + args.fixture_output_tokens * float(pricing["completion"])
                ),
                10,
            )
        )
    fixture_cost_estimate = round(sum(fixture_cost_by_model.values()), 10)

    empirical_max_envelope = max(actual_costs) * args.full_games
    repriced_max_envelope = (
        max(repriced_costs) * args.full_games if repriced_costs else 0.0
    )
    game_envelope = repriced_max_envelope
    game_campaign_ceiling = _round_up(game_envelope, 10)
    diagnostics_reserve = _round_up(fixture_cost_estimate, 5)
    end_to_end_gate = _round_up((game_envelope + diagnostics_reserve) * 1.10, 10)

    available_credits = _nested_number(preflight, ("credits", "available_credits"))
    payload = {
        "schema_version": "v1",
        "budget_projection_version": "e1_budget_projection_v1",
        "generated_at_utc": _utc_now(),
        "source_commit": _git_head(repo_root),
        "design": {
            "full_games": args.full_games,
            "fixtures": args.fixtures,
            "models": args.models,
            "repeats_per_model_fixture": args.repeats,
            "fixture_call_count": fixture_call_count,
            "fixture_input_tokens_assumed": args.fixture_input_tokens,
            "fixture_output_tokens_assumed": args.fixture_output_tokens,
            "bootstrap_draws": args.bootstrap_draws,
            "bootstrap_seed": args.bootstrap_seed,
        },
        "historical_medium_frontier_games": game_rows,
        "historical_actual_cost": _distribution_summary(actual_costs),
        "current_base_endpoint_repriced_cost": _distribution_summary(repriced_costs),
        "bootstrap_eight_game_actual": _distribution_summary(bootstrap_actual),
        "bootstrap_eight_game_repriced": _distribution_summary(bootstrap_repriced),
        "fixture_projection": {
            "cost_by_model": fixture_cost_by_model,
            "estimated_total_cost": fixture_cost_estimate,
            "diagnostics_reserve": diagnostics_reserve,
            "note": (
                "Fixture projection is a planning assumption, not provider billing evidence. "
                "Actual usage and cost replace it after E1."
            ),
        },
        "gates": {
            "empirical_max_full_game_envelope": round(empirical_max_envelope, 10),
            "repriced_max_full_game_envelope": round(repriced_max_envelope, 10),
            "budget_basis": "current_routes_with_required_byok_charged_at_zero",
            "byok_models": sorted(
                model_id
                for model_id, pricing in pricing_by_model.items()
                if pricing.get("billing_mode") == "byok_required"
            ),
            "full_game_campaign_cost_ceiling": game_campaign_ceiling,
            "end_to_end_available_credit_gate": end_to_end_gate,
            "contingency_fraction": 0.10,
            "current_available_credits": available_credits,
            "credit_gate_passed": bool(
                available_credits is not None and available_credits >= end_to_end_gate
            ),
        },
        "provenance": {
            "preflight_path": str(preflight_path.relative_to(repo_root)).replace(
                "\\", "/"
            ),
            "preflight_sha256": _sha256_file(preflight_path),
            "script": str(Path(__file__).resolve().relative_to(repo_root)).replace(
                "\\", "/"
            ),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "This projection reads downstream usage artifacts and makes no provider calls.",
        },
    }
    output_path = (repo_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    report_path = output_path.with_suffix(".md")
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output_path),
                "report": str(report_path),
                "game_campaign_ceiling": game_campaign_ceiling,
                "end_to_end_gate": end_to_end_gate,
                "credit_gate_passed": payload["gates"]["credit_gate_passed"],
            },
            sort_keys=True,
        )
    )
    return 0


def _base_endpoint_pricing(preflight: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for check in _list(preflight.get("model_checks")):
        if not isinstance(check, dict):
            continue
        endpoints = [
            value
            for value in _list(check.get("matching_endpoints"))
            if isinstance(value, dict)
        ]
        if not endpoints:
            continue
        endpoint = endpoints[0]
        pricing = _dict(endpoint.get("pricing"))
        prompt = _float_or_none(pricing.get("prompt"))
        completion = _float_or_none(pricing.get("completion"))
        cache_read = _float_or_none(pricing.get("input_cache_read"))
        if prompt is None or completion is None:
            continue
        result[str(check["model_id"])] = {
            "prompt": prompt,
            "completion": completion,
            "input_cache_read": cache_read if cache_read is not None else prompt,
            "billing_mode": _dict(check.get("billing_policy")).get("mode"),
        }
    return result


def _reprice_game(
    cost_report: dict[str, Any],
    pricing_by_model: dict[str, dict[str, Any]],
) -> tuple[float | None, dict[str, float | None]]:
    rows: dict[str, float | None] = {}
    for model_id, usage_value in _dict(cost_report.get("by_model")).items():
        usage = _dict(usage_value)
        pricing = pricing_by_model.get(str(model_id))
        if not pricing:
            rows[str(model_id)] = None
            continue
        if pricing.get("billing_mode") == "byok_required":
            rows[str(model_id)] = 0.0
            continue
        prompt = (
            _first_number(usage.get("input_tokens"), usage.get("prompt_tokens")) or 0.0
        )
        completion = (
            _first_number(usage.get("output_tokens"), usage.get("completion_tokens"))
            or 0.0
        )
        cached = min(
            prompt,
            _first_number(usage.get("cached_tokens"), usage.get("cache_read_tokens"))
            or 0.0,
        )
        noncached = max(0.0, prompt - cached)
        rows[str(model_id)] = round(
            noncached * pricing["prompt"]
            + cached * pricing["input_cache_read"]
            + completion * pricing["completion"],
            10,
        )
    known = [value for value in rows.values() if value is not None]
    return (round(sum(known), 10) if len(known) == len(rows) and rows else None), rows


def _bootstrap_sums(
    values: list[float],
    *,
    sample_size: int,
    draws: int,
    seed: int,
) -> list[float]:
    if not values:
        return []
    rng = random.Random(seed)
    return [sum(rng.choice(values) for _ in range(sample_size)) for _ in range(draws)]


def _distribution_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    ordered = sorted(values)
    return {
        "count": len(values),
        "mean": round(statistics.fmean(values), 10),
        "median": round(statistics.median(values), 10),
        "minimum": round(ordered[0], 10),
        "maximum": round(ordered[-1], 10),
        "p05": round(_quantile(ordered, 0.05), 10),
        "p25": round(_quantile(ordered, 0.25), 10),
        "p75": round(_quantile(ordered, 0.75), 10),
        "p95": round(_quantile(ordered, 0.95), 10),
    }


def _quantile(ordered: list[float], probability: float) -> float:
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _markdown_report(payload: dict[str, Any]) -> str:
    gates = _dict(payload["gates"])
    actual = _dict(payload["historical_actual_cost"])
    repriced = _dict(payload["current_base_endpoint_repriced_cost"])
    bootstrap = _dict(payload["bootstrap_eight_game_repriced"])
    fixture = _dict(payload["fixture_projection"])
    return "\n".join(
        [
            "# E1 Budget Projection",
            "",
            "This is an operational planning artifact based on the five exploratory",
            "medium-frontier games. It is not a scientific performance analysis.",
            "",
            f"- Historical all-paid per-game cost: mean ${actual.get('mean'):.2f}, "
            f"range ${actual.get('minimum'):.2f}–${actual.get('maximum'):.2f}.",
            f"- Current OpenAI-BYOK repricing: mean ${repriced.get('mean'):.2f}, "
            f"range ${repriced.get('minimum'):.2f}–${repriced.get('maximum'):.2f}.",
            f"- OpenAI-BYOK eight-game bootstrap: mean ${bootstrap.get('mean'):.2f}, "
            f"95th percentile ${bootstrap.get('p95'):.2f}.",
            f"- Eight-game BYOK-adjusted maximum envelope: "
            f"${gates.get('repriced_max_full_game_envelope'):.2f}.",
            f"- Repeated-fixture point estimate: ${fixture.get('estimated_total_cost'):.2f}; "
            f"reserved ${fixture.get('diagnostics_reserve'):.2f}.",
            f"- Full-game campaign ceiling: ${gates.get('full_game_campaign_cost_ceiling'):.2f}.",
            f"- End-to-end available-credit gate with 10% contingency: "
            f"${gates.get('end_to_end_available_credit_gate'):.2f}.",
            f"- Gate currently passed: **{gates.get('credit_gate_passed')}**.",
            "",
            "No provider call is authorized by this projection.",
            "",
        ]
    )


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _round_up(value: float, increment: int) -> int:
    return int(math.ceil(value / increment) * increment)


def _nested_number(payload: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return _float_or_none(current)


def _first_number(*values: Any) -> float | None:
    for value in values:
        parsed = _float_or_none(value)
        if parsed is not None:
            return parsed
    return None


def _number(value: Any) -> float:
    parsed = _float_or_none(value)
    if parsed is None:
        raise ValueError(f"Expected numeric value, got {value!r}")
    return parsed


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
