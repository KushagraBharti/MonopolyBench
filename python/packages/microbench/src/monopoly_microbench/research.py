from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.exceptions import ValidationError  # type: ignore[import-untyped]
from monopoly_arena.schema_registry import get_schema_registry

from .catalog import get_suite, list_scenarios
from .paths import campaigns_dir, counterfactual_pairs_dir, default_runs_dir, research_suites_dir


MICRO_RESEARCH_SCHEMA_ID = "micro_research.schema.json"


def list_research_suites() -> list[dict[str, Any]]:
    suites = [_load_json(path) for path in sorted(research_suites_dir().glob("*.json"))]
    for suite in suites:
        validate_research_suite(suite)
    return suites


def get_research_suite(suite_id: str) -> dict[str, Any]:
    for suite in list_research_suites():
        if suite["suite_id"] == suite_id:
            return suite
    raise FileNotFoundError(f"Unknown micro research suite '{suite_id}'.")


def list_counterfactual_pair_registries() -> list[dict[str, Any]]:
    registries = [_load_json(path) for path in sorted(counterfactual_pairs_dir().glob("*.json"))]
    for registry in registries:
        validate_counterfactual_pair_registry(registry)
    return registries


def list_counterfactual_pairs() -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for registry in list_counterfactual_pair_registries():
        for pair in registry["pairs"]:
            pairs.append({**pair, "suite_id": registry["suite_id"]})
    return pairs


def list_micro_campaign_registries() -> list[dict[str, Any]]:
    registries = [_load_json(path) for path in sorted(campaigns_dir().glob("*.json"))]
    for registry in registries:
        validate_micro_campaign_registry(registry)
    return registries


def list_micro_campaigns() -> list[dict[str, Any]]:
    campaigns: list[dict[str, Any]] = []
    for registry in list_micro_campaign_registries():
        for campaign in registry["campaigns"]:
            campaigns.append({**campaign, "suite_id": registry["suite_id"]})
    return campaigns


def validate_research_suite(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{MICRO_RESEARCH_SCHEMA_ID}#/$defs/microResearchSuite")
    _assert_prompt_pipeline_unchanged(payload, f"research suite {payload.get('suite_id')}")


def validate_counterfactual_pair_registry(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{MICRO_RESEARCH_SCHEMA_ID}#/$defs/counterfactualPairRegistry")
    _assert_prompt_pipeline_unchanged(payload, f"counterfactual registry {payload.get('suite_id')}")
    pair_ids = [pair["pair_id"] for pair in payload["pairs"]]
    if len(set(pair_ids)) != len(pair_ids):
        raise ValueError(f"{payload['suite_id']}: duplicate counterfactual pair ids.")


def validate_micro_campaign_registry(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{MICRO_RESEARCH_SCHEMA_ID}#/$defs/microCampaignRegistry")
    _assert_prompt_pipeline_unchanged(payload, f"campaign registry {payload.get('suite_id')}")
    campaign_ids = [campaign["campaign_id"] for campaign in payload["campaigns"]]
    if len(set(campaign_ids)) != len(campaign_ids):
        raise ValueError(f"{payload['suite_id']}: duplicate campaign ids.")


def validate_research_catalog() -> dict[str, Any]:
    scenario_ids = {scenario["scenario_id"] for scenario in list_scenarios()}
    suite_ids = {suite["suite_id"] for suite in [get_suite("micro-v1")]}
    pairs = {pair["pair_id"]: pair for pair in list_counterfactual_pairs()}
    campaigns = {campaign["campaign_id"]: campaign for campaign in list_micro_campaigns()}
    research_suites = list_research_suites()
    for suite in research_suites:
        if suite["source_suite_id"] not in suite_ids:
            raise ValueError(f"{suite['suite_id']}: unknown source_suite_id {suite['source_suite_id']}.")
        _require_known_scenarios(suite["scenario_ids"], scenario_ids, suite["suite_id"])
        for category in suite["categories"]:
            _require_known_scenarios(category["scenario_ids"], scenario_ids, f"{suite['suite_id']}/{category['category_id']}")
            unknown_pairs = [
                pair_id for pair_id in category.get("counterfactual_pair_ids", []) if pair_id not in pairs
            ]
            if unknown_pairs:
                raise ValueError(f"{suite['suite_id']}/{category['category_id']}: unknown pairs {unknown_pairs}.")
        unknown_pairs = [pair_id for pair_id in suite.get("counterfactual_pair_ids", []) if pair_id not in pairs]
        if unknown_pairs:
            raise ValueError(f"{suite['suite_id']}: unknown counterfactual pairs {unknown_pairs}.")
        unknown_campaigns = [campaign_id for campaign_id in suite.get("campaign_ids", []) if campaign_id not in campaigns]
        if unknown_campaigns:
            raise ValueError(f"{suite['suite_id']}: unknown campaigns {unknown_campaigns}.")
    for pair in pairs.values():
        _require_known_scenarios(
            [pair["baseline_scenario_id"], pair["contrast_scenario_id"]],
            scenario_ids,
            pair["pair_id"],
        )
    for campaign in campaigns.values():
        _require_known_scenarios(campaign["step_scenario_ids"], scenario_ids, campaign["campaign_id"])
    return {
        "schema_version": "v1",
        "research_suite_count": len(research_suites),
        "counterfactual_pair_count": len(pairs),
        "campaign_count": len(campaigns),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Research catalog validation reads post-hoc metadata only.",
        },
    }


def build_human_review_queue(suite_id: str) -> list[dict[str, Any]]:
    suite = get_research_suite(suite_id)
    tasks: list[dict[str, Any]] = []
    for category in suite["categories"]:
        if not category["human_review_required"]:
            continue
        for scenario_id in category["scenario_ids"]:
            tasks.append(
                _review_task(
                    task_id=f"task-{suite_id}-{category['category_id']}-{scenario_id}",
                    task_type="safety_label" if suite["suite_family"] == "safety" else "scenario",
                    suite_id=suite_id,
                    label_dimensions=[category["category_id"], *suite["report_dimensions"]],
                    scenario_id=scenario_id,
                )
            )
    known_pair_ids = set(suite.get("counterfactual_pair_ids", []))
    for pair in list_counterfactual_pairs():
        if pair["pair_id"] in known_pair_ids and pair["human_review_required"]:
            tasks.append(
                _review_task(
                    task_id=f"task-{suite_id}-{pair['pair_id']}",
                    task_type="counterfactual_pair",
                    suite_id=suite_id,
                    label_dimensions=["counterfactual_stability", "controlled_difference_quality"],
                    counterfactual_pair_id=pair["pair_id"],
                )
            )
    known_campaign_ids = set(suite.get("campaign_ids", []))
    for campaign in list_micro_campaigns():
        if campaign["campaign_id"] in known_campaign_ids and campaign["human_review_required"]:
            tasks.append(
                _review_task(
                    task_id=f"task-{suite_id}-{campaign['campaign_id']}",
                    task_type="campaign",
                    suite_id=suite_id,
                    label_dimensions=["strategic_path_completion", "subjective_safety_label"],
                    campaign_id=campaign["campaign_id"],
                )
            )
    return tasks


def validate_expert_label(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{MICRO_RESEARCH_SCHEMA_ID}#/$defs/expertLabel")
    if payload.get("human_review_only") is not True:
        raise ValueError(f"{payload.get('label_id')}: expert labels must be human_review_only=true.")
    if str(payload.get("label_source") or "").lower().startswith("llm"):
        raise ValueError(f"{payload.get('label_id')}: LLM-generated subjective labels are not allowed.")


def read_expert_labels(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    labels: list[dict[str, Any]]
    if path.suffix.lower() == ".jsonl":
        labels = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            parsed = parsed.get("labels", [])
        if not isinstance(parsed, list):
            raise ValueError(f"{path} must contain a label array or JSONL rows.")
        labels = [label for label in parsed if isinstance(label, dict)]
    for label in labels:
        validate_expert_label(label)
    return labels


def build_static_research_report(
    suite_id: str,
    *,
    runs_dir: Path | None = None,
    result_batch_id: str | None = None,
    labels_path: Path | None = None,
) -> dict[str, Any]:
    validate_research_catalog()
    suite = get_research_suite(suite_id)
    scenarios_by_id = {scenario["scenario_id"]: scenario for scenario in list_scenarios()}
    pairs_by_id = {pair["pair_id"]: pair for pair in list_counterfactual_pairs()}
    campaigns_by_id = {campaign["campaign_id"]: campaign for campaign in list_micro_campaigns()}
    root = runs_dir or default_runs_dir()
    result_rows = _load_batch_result_rows(root, result_batch_id) if result_batch_id else []
    labels = read_expert_labels(labels_path) if labels_path is not None else []
    review_queue = build_human_review_queue(suite_id)
    label_summary = _label_summary(labels, review_queue)
    category_rows = [
        _category_row(suite, category, result_rows=result_rows, labels=labels) for category in suite["categories"]
    ]
    scenario_rows = [
        _scenario_row(suite, scenarios_by_id[scenario_id], result_rows=result_rows, labels=labels)
        for scenario_id in suite["scenario_ids"]
    ]
    pair_rows = [
        _counterfactual_pair_row(pairs_by_id[pair_id], result_rows=result_rows, labels=labels)
        for pair_id in suite.get("counterfactual_pair_ids", [])
        if pair_id in pairs_by_id
    ]
    campaign_rows = [
        _micro_campaign_row(campaigns_by_id[campaign_id], result_rows=result_rows, labels=labels)
        for campaign_id in suite.get("campaign_ids", [])
        if campaign_id in campaigns_by_id
    ]
    result_join = _result_join_report(suite, result_batch_id, result_rows, scenario_rows, category_rows)
    return {
        "micro_report": {
            "schema_version": "v1",
            "report_version": "micro_research_report_v1",
            "suite_id": suite_id,
            "suite_family": suite["suite_family"],
            "source_suite_id": suite["source_suite_id"],
            "scenario_count": len(scenario_rows),
            "category_count": len(category_rows),
            "report_dimensions": suite["report_dimensions"],
            "scenarios": scenario_rows,
            "result_batch_id": result_batch_id,
            "joined_result_count": len(result_rows),
            "human_review_task_count": len(review_queue),
            "human_label_count": len(labels),
            "prompt_pipeline": _prompt_marker(),
        },
        "category_breakdown": {
            "schema_version": "v1",
            "suite_id": suite_id,
            "categories": category_rows,
            "prompt_pipeline": _prompt_marker(),
        },
        "counterfactual_report": {
            "schema_version": "v1",
            "suite_id": suite_id,
            "pair_count": len(pair_rows),
            "pairs": pair_rows,
            "joined_result_count": len(result_rows),
            "prompt_pipeline": _prompt_marker(),
        },
        "safety_report": {
            "schema_version": "v1",
            "suite_id": suite_id,
            "enabled": suite["suite_family"] == "safety",
            "human_review_only": True,
            "categories": category_rows if suite["suite_family"] == "safety" else [],
            "human_label_summary": label_summary if suite["suite_family"] == "safety" else {},
            "candidate_flags_are_final_labels": False,
            "prompt_pipeline": _prompt_marker(),
        },
        "campaign_report": {
            "schema_version": "v1",
            "suite_id": suite_id,
            "campaign_count": len(campaign_rows),
            "campaigns": campaign_rows,
            "joined_result_count": len(result_rows),
            "prompt_pipeline": _prompt_marker(),
        },
        "result_join": result_join,
        "human_review_queue": review_queue,
        "expert_labels": labels,
        "label_summary": label_summary,
        "paper_summary": _paper_summary(
            suite,
            category_rows,
            pair_rows,
            campaign_rows,
            review_queue,
            result_join,
            label_summary,
        ),
    }


def write_static_research_report(
    suite_id: str,
    *,
    runs_dir: Path | None = None,
    batch_id: str | None = None,
    result_batch_id: str | None = None,
    labels_path: Path | None = None,
) -> Path:
    report = build_static_research_report(
        suite_id,
        runs_dir=runs_dir,
        result_batch_id=result_batch_id,
        labels_path=labels_path,
    )
    root = runs_dir or default_runs_dir()
    out_dir = root / "micro_batches" / (batch_id or f"micro-research-{suite_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "micro_report.json", report["micro_report"])
    _write_csv(out_dir / "micro_report.csv", report["micro_report"]["scenarios"])
    _write_json(out_dir / "category_breakdown.json", report["category_breakdown"])
    _write_csv(out_dir / "category_breakdown.csv", report["category_breakdown"]["categories"])
    _write_json(out_dir / "counterfactual_report.json", report["counterfactual_report"])
    _write_json(out_dir / "safety_report.json", report["safety_report"])
    _write_json(out_dir / "campaign_report.json", report["campaign_report"])
    _write_json(out_dir / "result_join.json", report["result_join"])
    _write_csv(out_dir / "result_join.csv", report["result_join"]["scenario_rows"])
    _write_jsonl(out_dir / "human_review_queue.jsonl", report["human_review_queue"])
    _write_jsonl(out_dir / "expert_labels.jsonl", report["expert_labels"])
    _write_json(out_dir / "label_summary.json", report["label_summary"])
    (out_dir / "paper_summary.md").write_text(report["paper_summary"], encoding="utf-8")
    _write_json(out_dir / "artifact_manifest.json", _artifact_manifest(out_dir))
    return out_dir


def _category_row(
    suite: dict[str, Any],
    category: dict[str, Any],
    *,
    result_rows: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    result_summary = _result_summary(
        [row for row in result_rows if row.get("scenario_id") in set(category["scenario_ids"])]
    )
    category_labels = [
        label for label in labels if label.get("scenario_id") in set(category["scenario_ids"])
    ]
    return {
        "suite_id": suite["suite_id"],
        "suite_family": suite["suite_family"],
        "category_id": category["category_id"],
        "title": category["title"],
        "scenario_count": len(category["scenario_ids"]),
        "counterfactual_pair_count": len(category.get("counterfactual_pair_ids", [])),
        "human_review_required": category["human_review_required"],
        "target_behavior": category["target_behavior"],
        "trap_behaviors": "; ".join(category["trap_behaviors"]),
        "preferred_behaviors": "; ".join(category["preferred_behaviors"]),
        "scoring_notes": category["scoring_notes"],
        "result_count": result_summary["result_count"],
        "model_count": result_summary["model_count"],
        "average_score": result_summary["average_score"],
        "preferred_or_acceptable_rate": result_summary["preferred_or_acceptable_rate"],
        "invalid_rate": result_summary["invalid_rate"],
        "retry_rate": result_summary["retry_rate"],
        "fallback_rate": result_summary["fallback_rate"],
        "human_label_count": len(category_labels),
    }


def _scenario_row(
    suite: dict[str, Any],
    scenario: dict[str, Any],
    *,
    result_rows: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    metadata = scenario.get("research_metadata") or {}
    scenario_results = [row for row in result_rows if row.get("scenario_id") == scenario["scenario_id"]]
    result_summary = _result_summary(scenario_results)
    scenario_labels = [label for label in labels if label.get("scenario_id") == scenario["scenario_id"]]
    return {
        "suite_id": suite["suite_id"],
        "suite_family": suite["suite_family"],
        "scenario_id": scenario["scenario_id"],
        "source_suite_id": scenario["suite_id"],
        "category": scenario["category"],
        "difficulty": scenario["difficulty"],
        "target_capability": metadata.get("target_capability"),
        "target_behavior": metadata.get("target_behavior"),
        "bias_type": _matching_category_ids(suite, scenario["scenario_id"]) if suite["suite_family"] == "bias" else "",
        "safety_type": _matching_category_ids(suite, scenario["scenario_id"]) if suite["suite_family"] == "safety" else "",
        "counterfactual_pair_id": metadata.get("counterfactual_pair_id"),
        "human_review_required": any(
            scenario["scenario_id"] in category["scenario_ids"] and category["human_review_required"]
            for category in suite["categories"]
        ),
        "result_count": result_summary["result_count"],
        "model_count": result_summary["model_count"],
        "models": ";".join(result_summary["models"]),
        "average_score": result_summary["average_score"],
        "best_score": result_summary["best_score"],
        "score_label_counts": json.dumps(result_summary["score_label_counts"], sort_keys=True),
        "preferred_or_acceptable_rate": result_summary["preferred_or_acceptable_rate"],
        "invalid_rate": result_summary["invalid_rate"],
        "retry_rate": result_summary["retry_rate"],
        "fallback_rate": result_summary["fallback_rate"],
        "average_latency_ms": result_summary["average_latency_ms"],
        "human_label_count": len(scenario_labels),
        "human_review_status": "labeled" if scenario_labels else "queued_or_unlabeled",
        "prompt_metadata_visibility": metadata.get("visibility"),
    }


def _counterfactual_pair_row(
    pair: dict[str, Any],
    *,
    result_rows: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    baseline = [row for row in result_rows if row.get("scenario_id") == pair["baseline_scenario_id"]]
    contrast = [row for row in result_rows if row.get("scenario_id") == pair["contrast_scenario_id"]]
    baseline_by_model = _best_result_by_model(baseline)
    contrast_by_model = _best_result_by_model(contrast)
    per_model: list[dict[str, Any]] = []
    for model in sorted(set(baseline_by_model) & set(contrast_by_model)):
        base = baseline_by_model[model]
        other = contrast_by_model[model]
        delta = float(other["score_total"]) - float(base["score_total"])
        per_model.append(
            {
                "model": model,
                "baseline_run_id": base.get("run_id"),
                "contrast_run_id": other.get("run_id"),
                "baseline_score": base.get("score_total"),
                "contrast_score": other.get("score_total"),
                "score_delta": round(delta, 6),
                "absolute_score_delta": round(abs(delta), 6),
                "baseline_action": base.get("action_name"),
                "contrast_action": other.get("action_name"),
                "action_changed": base.get("action_name") != other.get("action_name"),
                "stability_band_pass": abs(delta) <= 0.15,
            }
        )
    pair_labels = [label for label in labels if label.get("counterfactual_pair_id") == pair["pair_id"]]
    return {
        **pair,
        "models_with_both_results": len(per_model),
        "average_score_delta": _mean_or_none([float(row["score_delta"]) for row in per_model]),
        "average_absolute_score_delta": _mean_or_none([float(row["absolute_score_delta"]) for row in per_model]),
        "stability_band_pass_rate": _rate(
            sum(1 for row in per_model if row["stability_band_pass"]),
            len(per_model),
        ),
        "per_model_results": per_model,
        "human_label_count": len(pair_labels),
        "human_review_status": "labeled" if pair_labels else "queued_or_unlabeled",
    }


def _micro_campaign_row(
    campaign: dict[str, Any],
    *,
    result_rows: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    step_ids = campaign["step_scenario_ids"]
    by_model_step: dict[str, dict[str, dict[str, Any]]] = {}
    for row in result_rows:
        scenario_id = row.get("scenario_id")
        model = row.get("model")
        if scenario_id not in step_ids or not isinstance(model, str):
            continue
        by_model_step.setdefault(model, {})[str(scenario_id)] = row
    per_model: list[dict[str, Any]] = []
    for model, by_step in sorted(by_model_step.items()):
        complete = all(step_id in by_step for step_id in step_ids)
        step_scores = [float(by_step[step_id]["score_total"]) for step_id in step_ids if step_id in by_step]
        per_model.append(
            {
                "model": model,
                "complete_step_count": len(step_scores),
                "required_step_count": len(step_ids),
                "complete_sequence": complete,
                "average_step_score": _mean_or_none(step_scores),
                "preferred_or_acceptable_step_rate": _rate(
                    sum(
                        1
                        for step_id in step_ids
                        if step_id in by_step and by_step[step_id].get("score_label") in {"preferred", "acceptable"}
                    ),
                    len(step_ids),
                ),
                "step_run_ids": [by_step[step_id].get("run_id") for step_id in step_ids if step_id in by_step],
            }
        )
    campaign_labels = [label for label in labels if label.get("campaign_id") == campaign["campaign_id"]]
    return {
        **campaign,
        "models_with_any_results": len(per_model),
        "models_with_complete_sequence": sum(1 for row in per_model if row["complete_sequence"]),
        "average_sequence_score": _mean_or_none(
            [float(row["average_step_score"]) for row in per_model if row["average_step_score"] is not None]
        ),
        "per_model_results": per_model,
        "stateful_engine_status": (
            "not_required_fixture_sequence"
            if campaign["replay_mode"] == "fixture_sequence"
            else "blocked_until_engine_stateful_micro_campaign_support"
        ),
        "human_label_count": len(campaign_labels),
        "human_review_status": "labeled" if campaign_labels else "queued_or_unlabeled",
    }


def _result_join_report(
    suite: dict[str, Any],
    result_batch_id: str | None,
    result_rows: list[dict[str, Any]],
    scenario_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "result_join_version": "micro_research_result_join_v1",
        "suite_id": suite["suite_id"],
        "result_batch_id": result_batch_id,
        "joined_result_count": len(result_rows),
        "joined_model_count": len({row.get("model") for row in result_rows if row.get("model")}),
        "scenario_rows": [
            {
                "scenario_id": row["scenario_id"],
                "category": row["category"],
                "result_count": row["result_count"],
                "model_count": row["model_count"],
                "average_score": row["average_score"],
                "preferred_or_acceptable_rate": row["preferred_or_acceptable_rate"],
                "retry_rate": row["retry_rate"],
                "fallback_rate": row["fallback_rate"],
                "human_label_count": row["human_label_count"],
            }
            for row in scenario_rows
        ],
        "category_rows": [
            {
                "category_id": row["category_id"],
                "result_count": row["result_count"],
                "model_count": row["model_count"],
                "average_score": row["average_score"],
                "preferred_or_acceptable_rate": row["preferred_or_acceptable_rate"],
                "retry_rate": row["retry_rate"],
                "fallback_rate": row["fallback_rate"],
                "human_label_count": row["human_label_count"],
            }
            for row in category_rows
        ],
        "prompt_pipeline": _prompt_marker(),
    }


def _load_batch_result_rows(runs_dir: Path, result_batch_id: str) -> list[dict[str, Any]]:
    batch_results_path = runs_dir / "micro_batches" / result_batch_id / "results.jsonl"
    if not batch_results_path.exists():
        raise FileNotFoundError(f"Micro result batch not found: {batch_results_path}")
    rows: list[dict[str, Any]] = []
    for compact in _read_jsonl(batch_results_path):
        row = dict(compact)
        run_id = str(row.get("run_id") or "")
        full = _load_micro_result(runs_dir, run_id)
        if full:
            row.update(
                {
                    "suite_id": full.get("suite_id", row.get("suite_id")),
                    "scenario_id": full.get("scenario_id", row.get("scenario_id")),
                    "category": full.get("category", row.get("category")),
                    "model": _dict(full.get("model")).get("openrouter_model_id", row.get("model")),
                    "score_total": _dict(full.get("score")).get("total", row.get("score_total")),
                    "score_label": _dict(full.get("score")).get("label", row.get("score_label")),
                    "retry_used": _dict(full.get("outcome")).get("retry_used", row.get("retry_used")),
                    "fallback_used": _dict(full.get("outcome")).get("fallback_used", row.get("fallback_used")),
                    "latency_ms": _dict(full.get("outcome")).get("latency_ms", row.get("latency_ms")),
                    "action_name": _dict(_dict(full.get("outcome")).get("action")).get("action"),
                    "action_args": _dict(_dict(full.get("outcome")).get("action")).get("args"),
                }
            )
        rows.append(row)
    return rows


def _load_micro_result(runs_dir: Path, run_id: str) -> dict[str, Any]:
    if not run_id:
        return {}
    path = runs_dir / "micro" / run_id / "result.json"
    if not path.exists():
        return {}
    return _load_json(path)


def _result_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [_number(row.get("score_total")) for row in rows if row.get("score_total") is not None]
    labels = [str(row.get("score_label") or "unknown") for row in rows]
    label_counts: dict[str, int] = {}
    for label in labels:
        _increment(label_counts, label)
    return {
        "result_count": len(rows),
        "model_count": len({row.get("model") for row in rows if row.get("model")}),
        "models": sorted({str(row.get("model")) for row in rows if row.get("model")}),
        "average_score": _mean_or_none(scores),
        "best_score": max(scores) if scores else None,
        "score_label_counts": label_counts,
        "preferred_or_acceptable_rate": _rate(
            sum(1 for label in labels if label in {"preferred", "acceptable"}),
            len(labels),
        ),
        "invalid_rate": _rate(sum(1 for label in labels if label == "invalid"), len(labels)),
        "retry_rate": _rate(sum(1 for row in rows if row.get("retry_used")), len(rows)),
        "fallback_rate": _rate(sum(1 for row in rows if row.get("fallback_used")), len(rows)),
        "average_latency_ms": _mean_or_none([_number(row.get("latency_ms")) for row in rows if row.get("latency_ms") is not None]),
    }


def _best_result_by_model(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_model: dict[str, dict[str, Any]] = {}
    for row in rows:
        model = row.get("model")
        if not isinstance(model, str):
            continue
        previous = by_model.get(model)
        if previous is None or _number(row.get("score_total")) > _number(previous.get("score_total")):
            by_model[model] = row
    return by_model


def _label_summary(labels: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> dict[str, Any]:
    by_judgment: dict[str, int] = {}
    by_reviewer: dict[str, int] = {}
    by_target: dict[str, int] = {}
    task_ids = {task["task_id"] for task in tasks}
    task_match_count = 0
    confidences: list[float] = []
    for label in labels:
        _increment(by_judgment, str(label.get("judgment")))
        _increment(by_reviewer, str(label.get("reviewer_id")))
        target = label.get("scenario_id") or label.get("counterfactual_pair_id") or label.get("campaign_id") or label.get("task_id")
        _increment(by_target, str(target))
        if label.get("task_id") in task_ids:
            task_match_count += 1
        if isinstance(label.get("confidence"), (int, float)):
            confidences.append(float(label["confidence"]))
    return {
        "schema_version": "v1",
        "label_summary_version": "micro_research_human_label_summary_v1",
        "human_review_only": True,
        "label_count": len(labels),
        "matched_task_count": task_match_count,
        "unmatched_task_count": len(labels) - task_match_count,
        "by_judgment": by_judgment,
        "by_reviewer": by_reviewer,
        "by_target": by_target,
        "average_confidence": _mean_or_none(confidences),
        "prompt_pipeline": _prompt_marker(),
    }


def _matching_category_ids(suite: dict[str, Any], scenario_id: str) -> str:
    return ";".join(
        category["category_id"] for category in suite["categories"] if scenario_id in category["scenario_ids"]
    )


def _review_task(
    *,
    task_id: str,
    task_type: str,
    suite_id: str,
    label_dimensions: list[str],
    scenario_id: str | None = None,
    counterfactual_pair_id: str | None = None,
    campaign_id: str | None = None,
) -> dict[str, Any]:
    task: dict[str, Any] = {
        "schema_version": "v1",
        "task_id": task_id,
        "task_type": task_type,
        "suite_id": suite_id,
        "label_dimensions": sorted(set(label_dimensions)),
        "status": "queued",
        "human_review_only": True,
        "prompt_pipeline": _prompt_marker(),
    }
    if scenario_id is not None:
        task["scenario_id"] = scenario_id
    if counterfactual_pair_id is not None:
        task["counterfactual_pair_id"] = counterfactual_pair_id
    if campaign_id is not None:
        task["campaign_id"] = campaign_id
    _validate_schema(task, f"{MICRO_RESEARCH_SCHEMA_ID}#/$defs/expertLabelTask")
    return task


def _paper_summary(
    suite: dict[str, Any],
    category_rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    campaign_rows: list[dict[str, Any]],
    review_queue: list[dict[str, Any]],
    result_join: dict[str, Any],
    label_summary: dict[str, Any],
) -> str:
    lines = [
        f"# {suite['title']}",
        "",
        suite["description"],
        "",
        "- Prompt pipeline: unchanged",
        f"- Source suite: `{suite['source_suite_id']}`",
        f"- Scenario count: {len(suite['scenario_ids'])}",
        f"- Category count: {len(category_rows)}",
        f"- Counterfactual pairs: {len(pair_rows)}",
        f"- Campaigns: {len(campaign_rows)}",
        f"- Human review tasks: {len(review_queue)}",
        f"- Joined model results: {result_join['joined_result_count']}",
        f"- Imported human labels: {label_summary['label_count']}",
        "",
        "## Categories",
        "",
    ]
    lines.extend(
        (
            f"- `{row['category_id']}`: {row['scenario_count']} scenarios; "
            f"human_review_required={row['human_review_required']}; "
            f"joined_results={row['result_count']}; avg_score={row['average_score']}"
        )
        for row in category_rows
    )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- This is a research-only report; model-run metrics are joined only from completed batch artifacts.",
            "- Subjective safety, deception, collusion, and kingmaking labels are human-reviewed only.",
            "- Current counterfactual pairs include first-pass related fixtures; future fixture work should tighten controlled differences.",
            "",
        ]
    )
    return "\n".join(lines)


def _artifact_manifest(out_dir: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    for path in sorted(out_dir.iterdir()):
        if path.name == "artifact_manifest.json" or not path.is_file():
            continue
        data = path.read_bytes()
        artifacts.append(
            {
                "label": path.stem,
                "path": str(path),
                "relative_path": path.name,
                "exists": True,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return {
        "schema_version": "v1",
        "manifest_version": "micro_research_artifact_manifest_v1",
        "artifact_dir": str(out_dir),
        "artifacts": artifacts,
        "prompt_pipeline": _prompt_marker(),
    }


def _require_known_scenarios(scenario_ids: list[str], known_ids: set[str], label: str) -> None:
    missing = [scenario_id for scenario_id in scenario_ids if scenario_id not in known_ids]
    if missing:
        raise ValueError(f"{label}: unknown scenario ids {missing[:5]}.")


def _validate_schema(payload: dict[str, Any], schema_ref: str) -> None:
    validator = Draft202012Validator({"$ref": schema_ref}, registry=get_schema_registry())
    try:
        validator.validate(payload)
    except ValidationError as error:
        path = "/" + "/".join(str(part) for part in error.absolute_path)
        raise ValueError(f"{schema_ref} validation failed at {path}: {error.message}") from error


def _assert_prompt_pipeline_unchanged(payload: dict[str, Any], label: str) -> None:
    marker = payload.get("prompt_pipeline")
    if not isinstance(marker, dict) or marker.get("status") != "unchanged":
        raise ValueError(f"{label} must declare prompt_pipeline.status='unchanged'.")


def _prompt_marker() -> dict[str, str]:
    return {
        "status": "unchanged",
        "note": "Micro research artifacts are post-hoc and never included in model-facing prompts.",
    }


def _load_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return parsed


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 6)


def _increment(mapping: dict[str, int], key: str, amount: int = 1) -> None:
    mapping[key] = mapping.get(key, 0) + amount


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
