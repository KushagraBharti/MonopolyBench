from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MATRIX_DIR = "analysis/research_protocol/pilot/e1_analysis_matrix"
DEFAULT_CAMPAIGN_DIR = "runs/campaigns/monopoly-long-v1-e1-pilot-random-v1"
DEFAULT_BUDGET = "analysis/research_protocol/pilot/budget_projection.json"
DEFAULT_OUTPUT = "analysis/research_protocol/pilot/power_simulation.json"
DEFAULT_DESIGN_LOCK = "analysis/research_protocol/pilot/design_lock.json"
CANDIDATE_BLOCKS = (20, 25, 30, 36, 40, 48, 60)
MODEL_COUNT = 4
PAIR_INDEXES = tuple(
    (left, right)
    for left in range(MODEL_COUNT)
    for right in range(left + 1, MODEL_COUNT)
)
SIMULATION_SEED = 2026072902


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Simulate the final ecological design from blinded E1 nuisance estimates."
    )
    parser.add_argument("--matrix-dir", default=DEFAULT_MATRIX_DIR)
    parser.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    parser.add_argument("--budget-projection", default=DEFAULT_BUDGET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--draws", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=SIMULATION_SEED)
    parser.add_argument(
        "--maximum-campaign-cost",
        type=float,
        default=None,
        help="Approved confirmatory primary-campaign cost ceiling; required for design lock.",
    )
    parser.add_argument("--write-design-lock", action="store_true")
    parser.add_argument("--design-lock-output", default=DEFAULT_DESIGN_LOCK)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()
    if args.draws < 1000:
        raise ValueError("Publication-facing simulation requires at least 1,000 draws.")

    repo_root = Path(__file__).resolve().parents[2]
    matrix_dir = (repo_root / args.matrix_dir).resolve()
    campaign_dir = (repo_root / args.campaign_dir).resolve()
    budget_path = (repo_root / args.budget_projection).resolve()
    output_path = (repo_root / args.output).resolve()
    matrix_manifest_path = matrix_dir / "manifest.json"
    matrix_manifest = _read_json(matrix_manifest_path)
    if matrix_manifest.get("status") != "complete":
        payload = _blocked_payload(
            repo_root=repo_root,
            matrix_manifest_path=matrix_manifest_path,
            matrix_manifest=matrix_manifest,
            draws=args.draws,
            seed=args.seed,
        )
        _write_json(output_path, payload)
        output_path.with_suffix(".md").write_text(_blocked_markdown(payload), encoding="utf-8")
        print(
            json.dumps(
                {
                    "output": _relative(repo_root, output_path),
                    "provider_calls": 0,
                    "status": payload["status"],
                },
                sort_keys=True,
            )
        )
        return 0

    block_rows = _read_csv(matrix_dir / "block_summary.csv")
    matrix = _balanced_matrix(block_rows)
    horizons = _dict(matrix_manifest.get("horizons"))
    survival_horizon = _required_number(
        horizons.get("restricted_survival_horizon"), "restricted survival horizon"
    )
    endpoint_specs = {
        "placement": {
            "column": "mean_placement_superiority",
            "smallest_effect": 0.15,
            "precision_half_width": 0.10,
            "variance_floor": 0.15,
        },
        "survival": {
            "column": "mean_restricted_survival",
            "smallest_effect": max(20.0, 0.10 * survival_horizon),
            "precision_half_width": 15.0,
            "variance_floor": max(10.0, 0.05 * survival_horizon),
        },
        "net_worth_auc": {
            "column": "mean_net_worth_auc",
            "smallest_effect": 300.0,
            "precision_half_width": 200.0,
            "variance_floor": 150.0,
        },
    }
    nuisance = _nuisance_estimates(matrix, endpoint_specs)
    observed_attrition = _observed_attrition(campaign_dir)
    scenarios = {
        "low": {"sd_multiplier": 0.75, "attrition_rate": 0.0},
        "central": {"sd_multiplier": 1.0, "attrition_rate": observed_attrition},
        "high": {
            "sd_multiplier": 1.5,
            "attrition_rate": max(0.10, observed_attrition + 0.05),
        },
    }
    rng = random.Random(args.seed)
    candidate_results: list[dict[str, Any]] = []
    for blocks in CANDIDATE_BLOCKS:
        scenario_results: dict[str, Any] = {}
        for scenario_name, scenario in scenarios.items():
            scenario_results[scenario_name] = _simulate_scenario(
                blocks=blocks,
                endpoint_specs=endpoint_specs,
                nuisance=nuisance,
                scenario=scenario,
                draws=args.draws,
                rng=rng,
            )
        candidate_results.append(
            {
                "planned_seed_blocks": blocks,
                "planned_games": blocks * 4,
                "scenarios": scenario_results,
            }
        )

    block_costs = _e1_block_costs(campaign_dir)
    cost_results = _cost_projections(
        block_costs=block_costs,
        candidate_blocks=CANDIDATE_BLOCKS,
        draws=max(args.draws, 5000),
        rng=rng,
    )
    for candidate in candidate_results:
        blocks = int(candidate["planned_seed_blocks"])
        candidate["cost_projection"] = cost_results.get(str(blocks))
        candidate["scientific_gate_passed"] = _scientific_gate(candidate)
        p95_cost = _nested_number(candidate, ("cost_projection", "p95"))
        candidate["approved_budget_gate_passed"] = bool(
            args.maximum_campaign_cost is not None
            and p95_cost is not None
            and p95_cost <= args.maximum_campaign_cost
        )
        candidate["all_gates_passed"] = bool(
            candidate["scientific_gate_passed"]
            and candidate["approved_budget_gate_passed"]
        )

    selected = next(
        (
            int(candidate["planned_seed_blocks"])
            for candidate in candidate_results
            if candidate["all_gates_passed"]
        ),
        None,
    )
    scientific_recommendation = next(
        (
            int(candidate["planned_seed_blocks"])
            for candidate in candidate_results
            if candidate["scientific_gate_passed"]
        ),
        None,
    )
    status = (
        "design_selected"
        if selected is not None
        else (
            "simulation_complete_budget_approval_required"
            if scientific_recommendation is not None and args.maximum_campaign_cost is None
            else "no_candidate_passed"
        )
    )
    payload = {
        "schema_version": "e1_power_simulation_v1",
        "generated_at_utc": _utc_now(),
        "status": status,
        "source_commit": _git_head(repo_root),
        "provider_calls": 0,
        "simulation": {
            "draws_per_null_or_alternative_condition": args.draws,
            "seed": args.seed,
            "candidate_seed_blocks": list(CANDIDATE_BLOCKS),
            "games_per_seed_block": 4,
            "joint_family": (
                "all six model-pair contrasts across placement, restricted survival, "
                "and common-horizon net-worth AUC"
            ),
            "familywise_alpha": 0.05,
            "minimum_power": 0.90,
            "minimum_interval_coverage": 0.90,
            "precision_criterion": "90th percentile simultaneous 95% half-width",
        },
        "endpoint_specs": endpoint_specs,
        "nuisance_estimates": nuisance,
        "variance_and_attrition_scenarios": scenarios,
        "observed_e1_attrition_rate": observed_attrition,
        "candidate_results": candidate_results,
        "scientific_recommended_seed_blocks": scientific_recommendation,
        "approved_maximum_campaign_cost": args.maximum_campaign_cost,
        "selected_seed_blocks": selected,
        "downstream_counts_if_selected": (
            _downstream_counts(selected) if selected is not None else None
        ),
        "provenance": {
            "matrix_manifest": _relative(repo_root, matrix_manifest_path),
            "matrix_manifest_sha256": _sha256_file(matrix_manifest_path),
            "block_summary": _relative(repo_root, matrix_dir / "block_summary.csv"),
            "block_summary_sha256": _sha256_file(matrix_dir / "block_summary.csv"),
            "campaign_run_results": _relative(repo_root, campaign_dir / "run_results.json"),
            "campaign_run_results_sha256": _sha256_file(
                campaign_dir / "run_results.json"
            ),
            "budget_projection": _relative(repo_root, budget_path),
            "budget_projection_sha256": (
                _sha256_file(budget_path) if budget_path.is_file() else None
            ),
            "script": _relative(repo_root, Path(__file__).resolve()),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Simulation consumes blinded downstream E1 summaries only.",
        },
    }
    _write_json(output_path, payload)
    output_path.with_suffix(".md").write_text(_markdown(payload), encoding="utf-8")

    if args.write_design_lock:
        if selected is None or args.maximum_campaign_cost is None:
            raise ValueError(
                "Cannot write a design lock without a selected design and approved cost ceiling."
            )
        design_lock_path = (repo_root / args.design_lock_output).resolve()
        design_lock = _design_lock_payload(
            repo_root=repo_root,
            power_path=output_path,
            power=payload,
            selected_blocks=selected,
        )
        _write_json(design_lock_path, design_lock)

    print(
        json.dumps(
            {
                "output": _relative(repo_root, output_path),
                "provider_calls": 0,
                "scientific_recommended_seed_blocks": scientific_recommendation,
                "selected_seed_blocks": selected,
                "status": status,
            },
            sort_keys=True,
        )
    )
    return 0


def _blocked_payload(
    *,
    repo_root: Path,
    matrix_manifest_path: Path,
    matrix_manifest: dict[str, Any],
    draws: int,
    seed: int,
) -> dict[str, Any]:
    return {
        "schema_version": "e1_power_simulation_v1",
        "generated_at_utc": _utc_now(),
        "status": "blocked_e1_analysis_matrix_incomplete",
        "source_commit": _git_head(repo_root),
        "provider_calls": 0,
        "requested_draws": draws,
        "simulation_seed": seed,
        "candidate_seed_blocks": list(CANDIDATE_BLOCKS),
        "matrix_manifest": {
            "path": _relative(repo_root, matrix_manifest_path),
            "exists": matrix_manifest_path.exists(),
            "sha256": (
                _sha256_file(matrix_manifest_path) if matrix_manifest_path.is_file() else None
            ),
            "status": matrix_manifest.get("status"),
        },
        "blockers": [
            "The validated E1 analysis matrix is incomplete.",
            "No empirical variance, attrition, cost, horizon, or design recommendation was computed.",
        ],
        "provenance": {
            "script": _relative(repo_root, Path(__file__).resolve()),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "This blocked precheck makes no model or provider call.",
        },
    }


def _balanced_matrix(
    rows: list[dict[str, str]],
) -> dict[str, dict[str, dict[str, float]]]:
    by_seed_actor: dict[tuple[str, str], dict[str, float]] = {}
    actors: set[str] = set()
    seeds: set[str] = set()
    for row in rows:
        seed = str(row.get("seed"))
        actor = str(row.get("actor_code"))
        key = (seed, actor)
        if key in by_seed_actor:
            raise ValueError(f"Duplicate block-summary row for {seed}/{actor}.")
        actors.add(actor)
        seeds.add(seed)
        by_seed_actor[key] = {
            "placement": _required_number(
                row.get("mean_placement_superiority"), "placement"
            ),
            "survival": _required_number(
                row.get("mean_restricted_survival"), "survival"
            ),
            "net_worth_auc": _required_number(
                row.get("mean_net_worth_auc"), "net worth AUC"
            ),
        }
    if len(actors) != MODEL_COUNT:
        raise ValueError(f"Expected four blinded actors, found {len(actors)}.")
    for seed in seeds:
        if {actor for row_seed, actor in by_seed_actor if row_seed == seed} != actors:
            raise ValueError(f"Seed {seed} does not contain all four actors.")
    result: dict[str, dict[str, dict[str, float]]] = {}
    for seed in sorted(seeds):
        result[seed] = {
            actor: by_seed_actor[(seed, actor)] for actor in sorted(actors)
        }
    return result


def _nuisance_estimates(
    matrix: dict[str, dict[str, dict[str, float]]],
    endpoint_specs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    seeds = sorted(matrix)
    actors = sorted(next(iter(matrix.values())))
    result: dict[str, Any] = {}
    for endpoint, spec in endpoint_specs.items():
        values = [[matrix[seed][actor][endpoint] for actor in actors] for seed in seeds]
        row_means = [statistics.fmean(row) for row in values]
        column_means = [
            statistics.fmean(values[row_index][column] for row_index in range(len(values)))
            for column in range(len(actors))
        ]
        grand = statistics.fmean(value for row in values for value in row)
        residuals = [
            values[row_index][column]
            - row_means[row_index]
            - column_means[column]
            + grand
            for row_index in range(len(values))
            for column in range(len(actors))
        ]
        degrees_of_freedom = max(1, (len(seeds) - 1) * (len(actors) - 1))
        residual_sd = math.sqrt(sum(value * value for value in residuals) / degrees_of_freedom)
        floor = _required_number(spec.get("variance_floor"), f"{endpoint} variance floor")
        result[endpoint] = {
            "pilot_seed_blocks": len(seeds),
            "residual_degrees_of_freedom": degrees_of_freedom,
            "label_blind_two_way_residual_sd": residual_sd,
            "variance_floor_sd": floor,
            "central_sd": max(residual_sd, floor),
            "model_means_not_emitted": True,
        }
    return result


def _simulate_scenario(
    *,
    blocks: int,
    endpoint_specs: dict[str, dict[str, Any]],
    nuisance: dict[str, Any],
    scenario: dict[str, float],
    draws: int,
    rng: random.Random,
) -> dict[str, Any]:
    attrition = float(scenario["attrition_rate"])
    sds = {
        endpoint: float(_dict(nuisance[endpoint])["central_sd"])
        * float(scenario["sd_multiplier"])
        for endpoint in endpoint_specs
    }
    null_maxima: list[float] = []
    effective_blocks: list[int] = []
    for _ in range(draws):
        usable = _usable_block_count(blocks, attrition, rng)
        effective_blocks.append(usable)
        endpoint_data = {
            endpoint: _simulate_block_matrix(usable, sd, effect=None, rng=rng)
            for endpoint, sd in sds.items()
        }
        null_maxima.append(_global_max_stat(endpoint_data))
    threshold = _quantile(sorted(null_maxima), 0.95)
    false_positive_rate = sum(value > threshold for value in null_maxima) / draws

    endpoint_results: dict[str, Any] = {}
    for endpoint, spec in endpoint_specs.items():
        effect_size = float(spec["smallest_effect"])
        rejected = 0
        covered = 0
        half_widths: list[float] = []
        estimates: list[float] = []
        for _ in range(draws):
            usable = _usable_block_count(blocks, attrition, rng)
            endpoint_data: dict[str, list[list[float]]] = {}
            for candidate_endpoint, sd in sds.items():
                effect = effect_size if candidate_endpoint == endpoint else None
                endpoint_data[candidate_endpoint] = _simulate_block_matrix(
                    usable,
                    sd,
                    effect=effect,
                    rng=rng,
                )
            if _global_max_stat(endpoint_data) > threshold:
                rejected += 1
            estimate, standard_error = _pair_estimate_and_se(
                endpoint_data[endpoint],
                0,
                1,
            )
            half_width = threshold * standard_error
            estimates.append(estimate)
            half_widths.append(half_width)
            if abs(estimate - effect_size) <= half_width:
                covered += 1
        precision_target = float(spec["precision_half_width"])
        p90_half_width = _quantile(sorted(half_widths), 0.90)
        endpoint_results[endpoint] = {
            "smallest_effect": effect_size,
            "power": rejected / draws,
            "simultaneous_interval_coverage": covered / draws,
            "mean_estimated_effect": statistics.fmean(estimates),
            "median_simultaneous_half_width": statistics.median(half_widths),
            "p90_simultaneous_half_width": p90_half_width,
            "precision_target_half_width": precision_target,
            "precision_gate_passed": p90_half_width <= precision_target,
        }
    return {
        "planned_seed_blocks": blocks,
        "attrition_rate": attrition,
        "effective_seed_blocks": _distribution(effective_blocks),
        "endpoint_sd": sds,
        "joint_critical_value": threshold,
        "empirical_familywise_type_i_error": false_positive_rate,
        "familywise_type_i_gate_passed": false_positive_rate <= 0.055,
        "endpoints": endpoint_results,
    }


def _simulate_block_matrix(
    blocks: int,
    sd: float,
    *,
    effect: float | None,
    rng: random.Random,
) -> list[list[float]]:
    effects = [0.0] * MODEL_COUNT
    if effect is not None:
        effects[0] = effect / 2
        effects[1] = -effect / 2
    scale = sd * math.sqrt(MODEL_COUNT / (MODEL_COUNT - 1))
    rows: list[list[float]] = []
    for _ in range(max(2, blocks)):
        residuals = [rng.gauss(0.0, scale) for _ in range(MODEL_COUNT)]
        center = statistics.fmean(residuals)
        rows.append(
            [
                effects[index] + residuals[index] - center
                for index in range(MODEL_COUNT)
            ]
        )
    return rows


def _global_max_stat(endpoint_data: dict[str, list[list[float]]]) -> float:
    maximum = 0.0
    for matrix in endpoint_data.values():
        for left, right in PAIR_INDEXES:
            estimate, standard_error = _pair_estimate_and_se(matrix, left, right)
            if standard_error == 0:
                statistic = math.inf if estimate != 0 else 0.0
            else:
                statistic = abs(estimate) / standard_error
            maximum = max(maximum, statistic)
    return maximum


def _pair_estimate_and_se(
    matrix: list[list[float]],
    left: int,
    right: int,
) -> tuple[float, float]:
    differences = [row[left] - row[right] for row in matrix]
    estimate = statistics.fmean(differences)
    if len(differences) < 2:
        return estimate, math.inf
    standard_error = statistics.stdev(differences) / math.sqrt(len(differences))
    return estimate, standard_error


def _usable_block_count(planned: int, attrition: float, rng: random.Random) -> int:
    return max(2, sum(1 for _ in range(planned) if rng.random() >= attrition))


def _scientific_gate(candidate: dict[str, Any]) -> bool:
    scenarios = _dict(candidate.get("scenarios"))
    for scenario in scenarios.values():
        payload = _dict(scenario)
        if payload.get("familywise_type_i_gate_passed") is not True:
            return False
        for endpoint in _dict(payload.get("endpoints")).values():
            result = _dict(endpoint)
            if _number(result.get("power")) < 0.90:
                return False
            if _number(result.get("simultaneous_interval_coverage")) < 0.90:
                return False
            if result.get("precision_gate_passed") is not True:
                return False
    return True


def _observed_attrition(campaign_dir: Path) -> float:
    results = [_dict(value) for value in _list(_read_json(campaign_dir / "run_results.json").get("runs"))]
    if not results:
        return 0.0
    complete = sum(1 for row in results if row.get("status") in {"completed", "resumed_completed"})
    return max(0.0, min(1.0, 1 - complete / len(results)))


def _e1_block_costs(campaign_dir: Path) -> list[float]:
    results = [_dict(value) for value in _list(_read_json(campaign_dir / "run_results.json").get("runs"))]
    by_seed: dict[str, float] = defaultdict(float)
    for row in results:
        if row.get("status") not in {"completed", "resumed_completed"}:
            continue
        cost = _nested_number(row, ("run_metrics", "usage_metrics", "total_cost"))
        if cost is None:
            cost = _nested_number(row, ("cost_report", "total_actual_cost"))
        if cost is None:
            raise ValueError(f"Completed run {row.get('run_id')} lacks actual cost.")
        by_seed[str(row.get("seed"))] += cost
    if not by_seed:
        raise ValueError("No E1 block costs are available.")
    return list(by_seed.values())


def _cost_projections(
    *,
    block_costs: list[float],
    candidate_blocks: tuple[int, ...],
    draws: int,
    rng: random.Random,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for blocks in candidate_blocks:
        totals = [
            sum(rng.choice(block_costs) for _ in range(blocks))
            for _ in range(draws)
        ]
        result[str(blocks)] = _distribution(totals)
    return result


def _downstream_counts(blocks: int) -> dict[str, Any]:
    primary_games = blocks * 4
    temporal_sentinel_games = max(8, math.ceil(primary_games * 0.10))
    return {
        "primary_seed_blocks": blocks,
        "primary_games": primary_games,
        "stochastic_live_repetitions": 0,
        "temporal_sentinel_games": temporal_sentinel_games,
        "stable_baseline_seed_blocks_per_model": 8,
        "stable_baseline_games_per_model": 32,
        "opponent_ecosystem_seed_blocks_per_roster": 8,
        "opponent_ecosystem_games_per_roster": 32,
        "stress_seed_blocks": 8,
        "stress_games": 32,
        "trajectory_fixtures": 24,
        "fixture_repetitions_per_model": 3,
        "fixture_query_count": 24 * 4 * 3,
        "note": (
            "Live stochasticity is measured through independent primary seed blocks and "
            "temporal sentinels; full duplicate live-cell repetition is not required."
        ),
    }


def _design_lock_payload(
    *,
    repo_root: Path,
    power_path: Path,
    power: dict[str, Any],
    selected_blocks: int,
) -> dict[str, Any]:
    downstream = _downstream_counts(selected_blocks)
    return {
        "schema_version": "e1_design_lock_v1",
        "generated_at_utc": _utc_now(),
        "status": "locked_for_preregistration_build",
        "source_commit": _git_head(repo_root),
        "selected_primary_seed_blocks": selected_blocks,
        "selected_primary_games": selected_blocks * 4,
        "approved_maximum_campaign_cost": power.get("approved_maximum_campaign_cost"),
        "scientific_gates_passed": True,
        "power_simulation": _relative(repo_root, power_path),
        "power_simulation_sha256": _sha256_file(power_path),
        "downstream_counts": downstream,
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "The design lock is a downstream preregistration input.",
        },
    }


def _self_test() -> int:
    rng = random.Random(17)
    endpoint_specs = {
        "placement": {
            "smallest_effect": 0.15,
            "precision_half_width": 0.20,
        },
        "survival": {
            "smallest_effect": 20.0,
            "precision_half_width": 30.0,
        },
        "net_worth_auc": {
            "smallest_effect": 300.0,
            "precision_half_width": 400.0,
        },
    }
    nuisance = {
        "placement": {"central_sd": 0.10},
        "survival": {"central_sd": 10.0},
        "net_worth_auc": {"central_sd": 100.0},
    }
    result = _simulate_scenario(
        blocks=30,
        endpoint_specs=endpoint_specs,
        nuisance=nuisance,
        scenario={"sd_multiplier": 1.0, "attrition_rate": 0.05},
        draws=300,
        rng=rng,
    )
    if not 0.0 <= result["empirical_familywise_type_i_error"] <= 0.10:
        raise AssertionError("Familywise error calibration self-test failed.")
    if set(_dict(result["endpoints"])) != set(endpoint_specs):
        raise AssertionError("Endpoint coverage self-test failed.")
    print("E1 power-simulation self-test passed.")
    return 0


def _distribution(values: list[float] | list[int]) -> dict[str, float | int]:
    ordered = sorted(float(value) for value in values)
    return {
        "count": len(ordered),
        "mean": statistics.fmean(ordered),
        "median": statistics.median(ordered),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "p05": _quantile(ordered, 0.05),
        "p95": _quantile(ordered, 0.95),
    }


def _quantile(ordered: list[float], probability: float) -> float:
    if not ordered:
        raise ValueError("Cannot compute a quantile from an empty sequence.")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _required_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric.")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric, got {value!r}.") from exc


def _nested_number(payload: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    if isinstance(current, bool) or not isinstance(current, (int, float)):
        return None
    return float(current)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


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


def _blocked_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# E1 Power Simulation",
            "",
            f"Status: **{payload.get('status')}**.",
            "",
            "The simulator refused to estimate power or select a design because the",
            "validated E1 nuisance-analysis matrix is incomplete.",
            "",
        ]
    )


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# E1 Power and Precision Simulation",
        "",
        f"- Status: **{payload.get('status')}**",
        f"- Scientific recommendation: {payload.get('scientific_recommended_seed_blocks')}",
        f"- Budget-approved selection: {payload.get('selected_seed_blocks')}",
        f"- Approved cost ceiling: {payload.get('approved_maximum_campaign_cost')}",
        "- Provider calls: 0",
        "",
        "| Blocks | Games | Scientific gate | Budget gate | P95 cost |",
        "|---:|---:|---|---|---:|",
    ]
    for candidate in _list(payload.get("candidate_results")):
        row = _dict(candidate)
        p95 = _nested_number(row, ("cost_projection", "p95"))
        lines.append(
            f"| {row.get('planned_seed_blocks')} | {row.get('planned_games')} | "
            f"{row.get('scientific_gate_passed')} | {row.get('approved_budget_gate_passed')} | "
            f"{p95 if p95 is not None else '—'} |"
        )
    lines.extend(
        [
            "",
            "Model identities are absent from the nuisance matrix and no observed pilot",
            "winner is used to select the design.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
