from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MicroRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    openrouter_model_id: str | None = None
    name: str | None = None
    reasoning: dict[str, Any] | None = None
    prompt_condition: str = "live_game"


class MicroBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suite_id: str = "micro-v1"
    openrouter_model_ids: list[str] = Field(default_factory=list)
    prompt_condition: str = "live_game"
    reasoning: dict[str, Any] | None = None
    scenario_ids: list[str] | None = None
