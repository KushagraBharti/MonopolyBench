from __future__ import annotations

import json
from typing import Any


def _try_parse_json(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped:
        return None
    if stripped[0] not in "[{" or stripped[-1] not in "]}":
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _normalize_prompt_payload(payload: Any) -> Any:
    if isinstance(payload, list):
        return [_normalize_prompt_payload(item) for item in payload]
    if isinstance(payload, dict):
        normalized = {}
        for key, value in payload.items():
            if key == "content" and isinstance(value, str):
                parsed = _try_parse_json(value)
                if parsed is not None:
                    normalized["content_raw"] = value
                    normalized["content"] = _normalize_prompt_payload(parsed)
                    continue
            normalized[key] = _normalize_prompt_payload(value)
        return normalized
    return payload


def format_quality_payload(raw_text: str) -> str | None:
    try:
        payload: Any = json.loads(raw_text)
    except json.JSONDecodeError:
        return None
    normalized = _normalize_prompt_payload(payload)
    return json.dumps(normalized, indent=2, ensure_ascii=False, sort_keys=True)
