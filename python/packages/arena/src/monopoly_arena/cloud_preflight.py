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
from .player_config import build_single_player_config
from .prompting import PromptMemory, build_space_key_by_index, build_prompt_bundle
from .route_validator import validate_route
from .worker import build_identity


async def preflight(store: JobStore) -> dict:
    import asyncio
    import os
    client = OpenRouterClient(base_url=os.getenv("MB_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), max_retries=0)
    report = {"version": "openrouter_campaign_preflight_v3", "created_at": time.time(), **build_identity(), "passed": False, "routes": []}
    try:
        for spec in player_specs():
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
            bundle = build_prompt_bundle(decision, player, memory=memory, space_key_by_index=spaces)
            from .prompting import build_openrouter_tools, build_compact_decision
            payload: dict[str, Any] = {"model": player.openrouter_model_id, "messages": bundle.messages, "tools": build_openrouter_tools(build_compact_decision(decision)), "tool_choice": "auto", "parallel_tool_calls": False, "reasoning": player.reasoning, "provider": player.provider}
            result = await asyncio.wait_for(client.create_chat_completion(**payload), 1200)
            if not result.ok:
                raise ValueError(result.error_type)
            validate_route(payload, result.response_json or {})
            attempt = resolver._attempt_from_response(bundle, result, 0, 0, include_prompt=False)
            _, errors, _, _ = resolver._build_action_from_attempt(decision, attempt)
            report["routes"].append({"model": player.openrouter_model_id, "result": asdict(result), "valid": not errors})
            if errors:
                raise ValueError(f"Illegal preflight tool call: {errors}")
        report["passed"] = True
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        await client.aclose()
    atomic_write(store.root / "preflight" / f"{uuid.uuid4().hex}.json", encode(report).encode())
    store.set_state("preflight", report)
    return report
