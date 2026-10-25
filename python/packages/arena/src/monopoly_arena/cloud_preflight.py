from __future__ import annotations

from dataclasses import asdict
import time
import uuid
from typing import Any

from monopoly_engine import Engine
from monopoly_telemetry.writer_jsonl import atomic_write
from .cloud_campaign import player_specs
from .decision_resolver import SharedDecisionResolver
from .job_store import JobStore, encode
from .openrouter_client import OpenRouterClient
from .player_config import build_single_player_config, tool_choice_for_model, default_provider_for_model
from .prompting import PromptMemory, build_space_key_by_index, build_refusal_retry_bundle
from .response_policy import REFUSAL_FALLBACKS, policy_manifest
from .route_validator import validate_route
from .worker import build_identity


async def preflight(store: JobStore) -> dict:
    import asyncio
    import os
    class CheckedClient(OpenRouterClient):
        async def create_chat_completion(self, **payload: Any) -> Any:
            result = await super().create_chat_completion(**payload)
            observations.append({"request": payload, "result": asdict(result)})
            if result.ok:
                validate_route(payload, result.response_json or {})
            return result

    observations: list[dict[str, Any]] = []
    client = CheckedClient(base_url=os.getenv("MB_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), max_retries=0)
    report = {"version": "openrouter_campaign_preflight_v4", "created_at": time.time(), **build_identity(), "response_policy": policy_manifest(), "passed": False, "routes": []}
    try:
        specs = player_specs()
        for target in sorted(set(REFUSAL_FALLBACKS.values())):
            specs.append({"player_id": "p1", "name": target, "openrouter_model_id": target,
                          "reasoning": {"effort": "medium"}, "provider": default_provider_for_model(target)})
        for spec in specs:
            observations.clear()
            players = [{"player_id": f"p{i+1}", "name": f"Player {i+1}"} for i in range(4)]
            engine = Engine(seed=42, run_id="preflight-fixture", players=players)
            _, _, decision, _ = engine.advance_until_decision(max_steps=100)
            if decision is None:
                raise ValueError("Preflight fixture has no decision")
            spec["player_id"] = decision["player_id"]
            player = build_single_player_config(**spec)
            spaces = build_space_key_by_index()
            memory = PromptMemory(space_key_by_index=spaces)
            resolver = SharedDecisionResolver(openrouter=client, prompt_memory=memory, space_key_by_index=spaces, run_files=None, rules_validator=lambda d, a: engine.validate_action_for_decision(a, d))
            if player.openrouter_model_id in REFUSAL_FALLBACKS.values():
                bundle, tools = build_refusal_retry_bundle(decision, player, memory=memory, space_key_by_index=spaces)
                payload: dict[str, Any] = {"model": player.openrouter_model_id, "messages": bundle.messages, "tools": tools, "tool_choice": tool_choice_for_model(player.openrouter_model_id), "parallel_tool_calls": False, "reasoning": player.reasoning, "provider": player.provider}
                result = await asyncio.wait_for(client.create_chat_completion(**payload), 1200)
                attempt = resolver._attempt_from_response(bundle, result, 0, 0, include_prompt=False)
                attempt.response_condition = "fallback_without_private_thought"
                _, errors, _, _ = resolver._build_action_from_attempt({**decision, "micro_prompt_condition": "no_private_thought"}, attempt)
                valid = result.ok and not errors
            else:
                outcome = await resolver.resolve_decision(decision=decision, player_config=player, log_writer=None)
                valid = not outcome.fallback_used
            report["routes"].append({"model": player.openrouter_model_id, "result": observations[-1]["result"],
                "attempts": list(observations), "valid": valid})
            if not valid:
                raise ValueError(f"No valid preflight action for {player.openrouter_model_id}; provider refused or returned an invalid tool")
        report["passed"] = True
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        await client.aclose()
    atomic_write(store.root / "preflight" / f"{uuid.uuid4().hex}.json", encode(report).encode())
    store.set_state("preflight", report)
    return report
