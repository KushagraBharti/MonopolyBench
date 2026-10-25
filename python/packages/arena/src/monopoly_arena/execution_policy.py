"""Cloud execution policy version and operational limits.

v3 adds bounded, attributed Claude refusal recovery to v2's tool/refusal fixes. The
version is recorded in execution artifacts, never injected into prompts.
"""
from __future__ import annotations

import os
from pathlib import Path

VERSION = "execution_policy_v3"
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


def storage_full(exc: BaseException) -> bool:
    """Disk or ledger exhaustion is a retryable storage pause, never a game failure."""
    import errno
    import sqlite3
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, OSError) and current.errno in {errno.ENOSPC, errno.EDQUOT}:
            return True
        if isinstance(current, sqlite3.OperationalError) and (
                getattr(current, "sqlite_errorcode", None) == getattr(sqlite3, "SQLITE_FULL", 13)
                or "database or disk is full" in str(current)):
            return True
        current = current.__cause__ or current.__context__
    return False


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
