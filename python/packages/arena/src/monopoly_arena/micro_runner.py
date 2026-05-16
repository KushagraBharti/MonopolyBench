from __future__ import annotations

import asyncio
import copy
import json
import time
from typing import Any

from monopoly_telemetry import RunFiles

from .decision_resolver import SharedDecisionResolver
from .player_config import PlayerConfig
from .prompting import PromptMemory, build_space_key_by_index


class MicroRunner:
    def __init__(
        self,
        *,
        scenario: dict[str, Any],
        player_config: PlayerConfig,
        run_id: str,
        openrouter: Any,
        run_files: RunFiles,
    ) -> None:
        self._scenario = copy.deepcopy(scenario)
        self._player_config = player_config
        self._run_id = run_id
        self._openrouter = openrouter
        self._run_files = run_files
        self._space_key_by_index = build_space_key_by_index()
        self._prompt_memory = PromptMemory(space_key_by_index=self._space_key_by_index)
        self._resolver = SharedDecisionResolver(
            openrouter=openrouter,
            run_files=run_files,
            prompt_memory=self._prompt_memory,
            space_key_by_index=self._space_key_by_index,
        )

    def prepare_scenario(self) -> dict[str, Any]:
        scenario = copy.deepcopy(self._scenario)
        scenario["run_id"] = self._run_id
        decision = scenario["decision_point"]
        decision["run_id"] = self._run_id
        decision["state"]["run_id"] = self._run_id
        return scenario

    async def run(self) -> dict[str, Any]:
        scenario = self.prepare_scenario()
        decision = scenario["decision_point"]

        self._run_files.run_dir.mkdir(parents=True, exist_ok=True)
        (self._run_files.run_dir / "scenario.json").write_text(
            json.dumps(scenario, separators=(",", ":"), ensure_ascii=True),
            encoding="utf-8",
        )
        self._run_files.write_snapshot(decision["state"])

        async def log_writer(entry: dict[str, Any]) -> None:
            self._run_files.write_decision(entry)

        outcome = await self._resolver.resolve_decision(
            decision=decision,
            player_config=self._player_config,
            log_writer=log_writer,
        )
        self._run_files.write_action(
            {
                "decision_id": decision["decision_id"],
                "actor_player_id": decision["player_id"],
                "decision_type": decision["decision_type"],
                "turn_index": decision["turn_index"],
                "action": outcome.action,
            }
        )
        resolved_entry = self._resolver.build_decision_log_entry(
            decision=decision,
            player_config=self._player_config,
            phase="decision_resolved",
            action=outcome.action,
            attempts=outcome.attempts,
            retry_used=outcome.retry_used,
            fallback_used=outcome.fallback_used,
            fallback_reason=outcome.fallback_reason,
            applied=False,
            sequence_meta=outcome.sequence_meta,
        )
        self._run_files.write_decision(resolved_entry)

        summary = {
            "run_id": self._run_id,
            "mode": "micro",
            "scenario_id": scenario["scenario_id"],
            "suite_id": scenario["suite_id"],
            "category": scenario["category"],
            "title": scenario["title"],
            "description": scenario["description"],
            "tags": scenario["tags"],
            "focal_player_id": scenario["focal_player_id"],
            "decision_id": decision["decision_id"],
            "decision_type": decision["decision_type"],
            "player": {
                "player_id": self._player_config.player_id,
                "name": self._player_config.name,
                "openrouter_model_id": self._player_config.openrouter_model_id,
                "model_display_name": self._player_config.model_display_name,
                "reasoning": self._player_config.reasoning,
            },
            "result": {
                "retry_used": outcome.retry_used,
                "fallback_used": outcome.fallback_used,
                "fallback_reason": outcome.fallback_reason,
                "final_action": outcome.action,
                "request_start_ms": resolved_entry.get("request_start_ms"),
                "response_end_ms": resolved_entry.get("response_end_ms"),
                "latency_ms": resolved_entry.get("latency_ms"),
            },
        }
        self._run_files.write_summary(summary)
        return {
            "scenario": scenario,
            "decision": decision,
            "outcome": outcome,
            "summary": summary,
        }

    async def aclose(self) -> None:
        close = getattr(self._openrouter, "aclose", None)
        if close is None:
            return
        result = close()
        if asyncio.iscoroutine(result):
            await result


def generate_micro_run_id(*, scenario_id: str, model_id: str) -> str:
    ts_ms = int(time.time() * 1000)
    safe_scenario = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in scenario_id)
    safe_model = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in model_id)
    return f"micro-{safe_scenario}-{safe_model}-{ts_ms}"
