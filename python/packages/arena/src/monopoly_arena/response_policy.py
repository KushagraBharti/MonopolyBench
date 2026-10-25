"""Versioned refusal recovery. Metadata stays downstream of model decisions."""
from __future__ import annotations

from typing import Any

# One explicit target, never a router alias or an implicit provider fallback.
REFUSAL_FALLBACKS = {"anthropic/claude-opus-5.5": "anthropic/claude-opus-4.8"}
POLICY_VERSION = "claude_refusal_recovery_v1"


def policy_manifest() -> dict[str, Any]:
    return {"version": POLICY_VERSION, "fallback_models": dict(REFUSAL_FALLBACKS),
            "stages": ["standard", "same_model_without_private_thought", "fallback_without_private_thought"],
            "trigger": "explicit_provider_refusal", "max_resolver_calls": 3}


def participant_label(model_id: str) -> str:
    label = model_id.split("/")[-1]
    target = REFUSAL_FALLBACKS.get(model_id)
    return f"{label} with {target.split('/')[-1]} fallback" if target else label
