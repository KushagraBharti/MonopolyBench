from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.validators import validator_for  # type: ignore[import-untyped]
from monopoly_arena.decision_resolver import validate_decision_action
from monopoly_arena.schema_registry import get_schema, get_schema_registry

from .paths import scenarios_dir, suites_dir


def _validator(schema_id: str) -> Draft202012Validator:
    schema = get_schema(schema_id)
    validator_cls = validator_for(schema)
    validator_cls.check_schema(schema)
    return validator_cls(schema, registry=get_schema_registry())


@lru_cache(maxsize=1)
def _scenario_validator() -> Draft202012Validator:
    return _validator("micro_scenario.schema.json")


@lru_cache(maxsize=1)
def _suite_validator() -> Draft202012Validator:
    return _validator("micro_suite.schema.json")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def list_scenarios() -> list[dict[str, Any]]:
    scenarios = [_load_json(path) for path in sorted(scenarios_dir().glob("*.json"))]
    for scenario in scenarios:
        validate_scenario(scenario)
    return scenarios


def list_scenario_summaries(*, suite_id: str | None = None) -> list[dict[str, Any]]:
    suite_ids = set(get_suite(suite_id)["scenario_ids"]) if suite_id else None
    summaries: list[dict[str, Any]] = []
    for scenario in list_scenarios():
        if suite_ids is not None and scenario["scenario_id"] not in suite_ids:
            continue
        decision = scenario["decision_point"]
        summaries.append(
            {
                "scenario_id": scenario["scenario_id"],
                "suite_id": scenario["suite_id"],
                "category": scenario["category"],
                "difficulty": scenario["difficulty"],
                "title": scenario["title"],
                "description": scenario["description"],
                "tags": scenario["tags"],
                "focal_player_id": scenario["focal_player_id"],
                "decision_type": decision["decision_type"],
                "scoring_mode": scenario["evaluation"]["scoring_mode"],
            }
        )
    return summaries


def load_scenario(scenario_id: str) -> dict[str, Any]:
    for scenario in list_scenarios():
        if scenario["scenario_id"] == scenario_id:
            return scenario
    raise FileNotFoundError(f"Unknown micro scenario '{scenario_id}'.")


def list_suites() -> list[dict[str, Any]]:
    suites = [_load_json(path) for path in sorted(suites_dir().glob("*.json"))]
    for suite in suites:
        validate_suite(suite)
    return suites


def get_suite(suite_id: str | None = None) -> dict[str, Any]:
    target = suite_id or "micro-v1"
    for suite in list_suites():
        if suite["suite_id"] == target:
            return suite
    raise FileNotFoundError(f"Unknown micro suite '{target}'.")


def validate_scenario(payload: dict[str, Any]) -> None:
    errors = [_format_error(error) for error in _scenario_validator().iter_errors(payload)]
    if errors:
        raise ValueError("; ".join(errors))
    decision = payload["decision_point"]
    focal_player_id = payload["focal_player_id"]
    if decision.get("player_id") != focal_player_id:
        raise ValueError(f"{payload['scenario_id']}: focal_player_id must match decision_point.player_id.")
    active_player_id = decision.get("state", {}).get("active_player_id")
    if active_player_id != focal_player_id and not payload.get("notes", {}).get("active_player_exception"):
        raise ValueError(f"{payload['scenario_id']}: active_player_id must match focal_player_id.")
    for legal in decision.get("legal_actions", []):
        if "args_schema" not in legal:
            raise ValueError(f"{payload['scenario_id']}: legal action missing args_schema.")
        try:
            Draft202012Validator.check_schema(legal["args_schema"])
        except Exception as exc:
            raise ValueError(
                f"{payload['scenario_id']}: legal action {legal.get('action')} has invalid args_schema: {exc}"
            ) from exc
    for action in [payload["reference_policy"]["action"], *payload["evaluation"].get("preferred_actions", [])]:
        action_errors = validate_decision_action(decision, action)
        semantic_errors = [err for err in action_errors if "Missing required" not in err]
        if semantic_errors:
            raise ValueError(f"{payload['scenario_id']}: reference/scored action is not legal: {semantic_errors}")
    total = sum(float(item["max_points"]) for item in payload["evaluation"]["rubric"])
    if total <= 0:
        raise ValueError(f"{payload['scenario_id']}: rubric total must be positive.")
    _validate_references(payload)


def validate_suite(payload: dict[str, Any]) -> None:
    errors = [_format_error(error) for error in _suite_validator().iter_errors(payload)]
    if errors:
        raise ValueError("; ".join(errors))
    scenario_ids = payload["scenario_ids"]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError(f"{payload['suite_id']}: duplicate scenario ids.")
    scenarios = {scenario["scenario_id"]: scenario for scenario in list_scenarios()}
    missing = [scenario_id for scenario_id in scenario_ids if scenario_id not in scenarios]
    if missing:
        raise ValueError(f"{payload['suite_id']}: missing scenarios: {missing[:5]}")
    counts = Counter(scenarios[scenario_id]["category"] for scenario_id in scenario_ids)
    for category, meta in payload["categories"].items():
        target = int(meta["target_count"])
        if counts[category] != target:
            raise ValueError(
                f"{payload['suite_id']}: category {category} expected {target}, found {counts[category]}."
            )


def validate_all() -> dict[str, Any]:
    scenarios = list_scenarios()
    suites = list_suites()
    return {"scenario_count": len(scenarios), "suite_count": len(suites)}


def _validate_references(payload: dict[str, Any]) -> None:
    board = payload["decision_point"]["state"]["board"]
    space_keys = {space.get("name", "").replace(" ", "_").replace(".", "").upper() for space in board}
    player_ids = {player["player_id"] for player in payload["decision_point"]["state"]["players"]}
    for criterion in payload["evaluation"]["rubric"]:
        params = criterion.get("params", {})
        for key in ("space_key", "request_space_key", "offer_space_key", "property_space_key"):
            if key in params and params[key] not in space_keys:
                raise ValueError(f"{payload['scenario_id']}: unknown space_key {params[key]}.")
        if "player_id" in params and params["player_id"] not in player_ids:
            raise ValueError(f"{payload['scenario_id']}: unknown player_id {params['player_id']}.")


def _format_error(error: Any) -> str:
    path = "$"
    for part in error.path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{path}: {error.message}"
