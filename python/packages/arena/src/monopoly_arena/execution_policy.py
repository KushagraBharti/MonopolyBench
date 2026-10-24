"""Cloud-only operational policy. None of these values enter model prompts."""
from __future__ import annotations

import os
from pathlib import Path

VERSION = "execution_policy_v1"
OUTAGE_INTERVAL = 300
OUTAGE_RETRIES = 12
UNKNOWN_PER_DECISION = 1
UNKNOWN_PER_GAME = 3
MODELS = ["anthropic/claude-opus-5.5", "openai/gpt-6.1-sol", "google/gemini-4-argon", "x-ai/grok-4.7"]


def data_root() -> Path:
    return Path(os.environ.get("MB_DATA_DIR", "/data/monopolybench"))


class OperationalPause(Exception):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(detail or reason)
        self.reason = reason


def error_pause(status: int | None, error_type: str | None, body: str | None) -> str:
    if status in (401, 403) or error_type == "no_api_key":
        return "account_error"
    if status == 402:
        import json
        try:
            error = json.loads(body or "{}").get("error", {})
            metadata = error.get("metadata", {})
            reason = str(metadata.get("reason", error.get("reason", ""))).lower()
            source = str(metadata.get("limit_source", "")).lower()
        except (ValueError, AttributeError):
            reason = source = ""
        if source in {"in_flight", "inflight", "concurrency"} or "in_flight" in reason or "in-flight" in reason:
            return "credit_admission"
        return "account_error"
    return "provider_unavailable"
