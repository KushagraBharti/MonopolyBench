from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MicroRunRequest(BaseModel):
    scenario_id: str
    openrouter_model_id: str | None = None
    name: str | None = None
    system_prompt: str | None = None
    reasoning: dict[str, Any] | None = None
    prompt_condition: str = "default"
    baseline: str | None = None


class MicroBatchRequest(BaseModel):
    suite_id: str = "micro-v1"
    openrouter_model_ids: list[str] = Field(default_factory=list)
    prompt_condition: str = "default"
    reasoning: dict[str, Any] | None = None
    baseline: str | None = None
    scenario_ids: list[str] | None = None
