from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .paths import resolve_repo_root, resolve_repo_path
from .schema_registry import get_schema_registry


SEED_REGISTRY_PATH = "contracts/research/monopoly_long_v1_seed_registry.json"
MODEL_ROSTER_REGISTRY_PATH = "contracts/research/monopoly_long_v1_model_rosters.json"
RESEARCH_SCHEMA_ID = "research_registry.schema.json"
EXPECTED_LONG_HORIZON_PLAYERS = 4


def research_dir() -> Path:
    return resolve_repo_root() / "contracts" / "research"


def load_seed_registry(path: Path | str | None = None) -> dict[str, Any]:
    payload = _read_json(resolve_repo_path(str(path)) if path is not None else resolve_repo_path(SEED_REGISTRY_PATH))
    validate_seed_registry(payload)
    return payload


def load_model_roster_registry(path: Path | str | None = None) -> dict[str, Any]:
    payload = _read_json(
        resolve_repo_path(str(path)) if path is not None else resolve_repo_path(MODEL_ROSTER_REGISTRY_PATH)
    )
    validate_model_roster_registry(payload)
    return payload


def validate_seed_registry(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{RESEARCH_SCHEMA_ID}#/$defs/seedRegistry")
    _assert_prompt_pipeline_unchanged(payload, "seed registry")
    cohorts = _dict(payload.get("cohorts"))
    for cohort_key, cohort in cohorts.items():
        if not isinstance(cohort, dict):
            raise ValueError(f"Seed cohort '{cohort_key}' must be an object.")
        cohort_id = str(cohort.get("cohort_id") or "")
        if cohort_key != cohort_id:
            raise ValueError(f"Seed cohort key '{cohort_key}' does not match cohort_id '{cohort_id}'.")
        seen: set[int] = set()
        for entry in _list(cohort.get("seeds")):
            if not isinstance(entry, dict):
                raise ValueError(f"Seed cohort '{cohort_key}' contains a non-object seed entry.")
            seed_value = entry.get("seed")
            if not isinstance(seed_value, int):
                raise ValueError(f"Seed cohort '{cohort_key}' contains a non-integer seed.")
            seed = int(seed_value)
            if seed in seen:
                raise ValueError(f"Seed cohort '{cohort_key}' contains duplicate seed {seed}.")
            seen.add(seed)
        for source_cohort in _list(cohort.get("source_cohorts")):
            if source_cohort not in cohorts:
                raise ValueError(
                    f"Seed cohort '{cohort_key}' references unknown source cohort '{source_cohort}'."
                )


def validate_model_roster_registry(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{RESEARCH_SCHEMA_ID}#/$defs/modelRosterRegistry")
    _assert_prompt_pipeline_unchanged(payload, "model roster registry")
    actors = _dict(payload.get("actors"))
    rosters = _dict(payload.get("rosters"))
    for actor_key, actor in actors.items():
        if not isinstance(actor, dict):
            raise ValueError(f"Actor '{actor_key}' must be an object.")
        actor_id = str(actor.get("actor_id") or "")
        if actor_key != actor_id:
            raise ValueError(f"Actor key '{actor_key}' does not match actor_id '{actor_id}'.")
        actor_type = actor.get("actor_type")
        if actor_type == "llm" and not actor.get("openrouter_model_id"):
            raise ValueError(f"LLM actor '{actor_key}' must define openrouter_model_id.")
        if actor_type == "baseline" and not actor.get("baseline_id"):
            raise ValueError(f"Baseline actor '{actor_key}' must define baseline_id.")
    for roster_key, roster in rosters.items():
        if not isinstance(roster, dict):
            raise ValueError(f"Roster '{roster_key}' must be an object.")
        roster_id = str(roster.get("roster_id") or "")
        if roster_key != roster_id:
            raise ValueError(f"Roster key '{roster_key}' does not match roster_id '{roster_id}'.")
        actor_ids = _list(roster.get("actor_ids"))
        if len(actor_ids) != EXPECTED_LONG_HORIZON_PLAYERS:
            raise ValueError(
                f"Roster '{roster_key}' must define exactly {EXPECTED_LONG_HORIZON_PLAYERS} actors."
            )
        for actor_id in actor_ids:
            if actor_id not in actors:
                raise ValueError(f"Roster '{roster_key}' references unknown actor '{actor_id}'.")


def validate_campaign_config(payload: dict[str, Any]) -> None:
    _validate_schema(payload, f"{RESEARCH_SCHEMA_ID}#/$defs/campaignConfig")
    _assert_prompt_pipeline_unchanged(payload, "campaign config")


def get_seed_cohort(
    cohort_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    seed_registry = registry if registry is not None else load_seed_registry()
    validate_seed_registry(seed_registry)
    cohorts = _dict(seed_registry.get("cohorts"))
    cohort = cohorts.get(cohort_id)
    if not isinstance(cohort, dict):
        raise KeyError(f"Unknown seed cohort '{cohort_id}'.")
    return deepcopy(cohort)


def get_model_roster(
    roster_id: str,
    registry: dict[str, Any] | None = None,
    *,
    include_disabled: bool = False,
) -> dict[str, Any]:
    roster_registry = registry if registry is not None else load_model_roster_registry()
    validate_model_roster_registry(roster_registry)
    rosters = _dict(roster_registry.get("rosters"))
    actors_by_id = _dict(roster_registry.get("actors"))
    roster = rosters.get(roster_id)
    if not isinstance(roster, dict):
        raise KeyError(f"Unknown model roster '{roster_id}'.")
    actor_ids = [str(actor_id) for actor_id in _list(roster.get("actor_ids"))]
    actors = [deepcopy(actors_by_id[actor_id]) for actor_id in actor_ids]
    disabled = [str(actor.get("actor_id")) for actor in actors if not bool(actor.get("enabled"))]
    if disabled and not include_disabled:
        raise ValueError(
            f"Roster '{roster_id}' includes disabled actors: {', '.join(disabled)}. "
            "Enable them after confirming OpenRouter availability/pricing, or pass include_disabled=True for inspection."
        )
    return {
        "schema_version": "v1",
        "roster_id": roster_id,
        "roster": deepcopy(roster),
        "actors": actors,
        "prompt_pipeline": deepcopy(roster_registry.get("prompt_pipeline")),
    }


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


def _read_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return parsed


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
