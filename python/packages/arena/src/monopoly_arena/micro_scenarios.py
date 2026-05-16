from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.validators import validator_for  # type: ignore[import-untyped]

from .paths import resolve_repo_root
from .schema_registry import get_schema, get_schema_registry


def micro_scenarios_dir() -> Path:
    return resolve_repo_root() / "contracts" / "micro"


def _scenario_paths() -> list[Path]:
    root = micro_scenarios_dir()
    nested = root / "scenarios"
    paths = list(sorted(nested.glob("*.json"))) if nested.exists() else []
    paths.extend(path for path in sorted(root.glob("*.json")) if path.name != "micro-v1.json")
    return paths


@lru_cache(maxsize=1)
def _micro_validator() -> Draft202012Validator:
    schema = get_schema("micro_scenario.schema.json")
    validator_cls = validator_for(schema)
    validator_cls.check_schema(schema)
    return validator_cls(schema, registry=get_schema_registry())


def _format_errors(payload: dict[str, Any]) -> list[str]:
    validator = _micro_validator()
    errors: list[str] = []
    for error in validator.iter_errors(payload):
        if error.path:
            path = "$"
            for part in error.path:
                path += f"[{part}]" if isinstance(part, int) else f".{part}"
        else:
            path = "$"
        errors.append(f"{path}: {error.message}")
    return errors


def list_micro_scenarios() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in _scenario_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_micro_scenario(payload)
        items.append(payload)
    return items


def load_micro_scenario(scenario_id: str) -> dict[str, Any]:
    for payload in list_micro_scenarios():
        if payload.get("scenario_id") == scenario_id:
            return payload
    raise FileNotFoundError(f"Unknown micro scenario '{scenario_id}'.")


def validate_micro_scenario(payload: dict[str, Any]) -> None:
    errors = _format_errors(payload)
    if errors:
        raise ValueError("; ".join(errors))
    decision_point = payload.get("decision_point", {})
    focal_player_id = payload.get("focal_player_id")
    if decision_point.get("player_id") != focal_player_id:
        raise ValueError("focal_player_id must match decision_point.player_id.")
