"""Zero-cost OpenRouter-compatible fixture server. Bind only to loopback by default.

MB_MOCK_SCENARIOS points to JSON mapping '<decision_id>:<stage>:<attempt>' to
scenario names. Counters use the request's decision ID and exact payload digest,
so interleaved games do not affect one another. Never reads real credentials.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()
attempts: dict[str, int] = defaultdict(int)
stages: dict[str, list[str]] = defaultdict(list)


def value_for(schema: dict[str, Any]) -> Any:
    if "enum" in schema:
        return schema["enum"][0]
    if "const" in schema:
        return schema["const"]
    if "anyOf" in schema:
        return value_for(schema["anyOf"][0])
    kind = schema.get("type")
    if kind == "object":
        return {key: value_for(schema.get("properties", {}).get(key, {})) for key in schema.get("required", [])}
    if kind == "array":
        return [value_for(schema.get("items", {})) for _ in range(schema.get("minItems", 0))]
    if kind in {"integer", "number"}:
        return schema.get("minimum", 0)
    if kind == "boolean":
        return False
    return "mock"


@app.post("/api/v1/chat/completions")
async def completion(request: Request):
    payload = await request.json()
    raw = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    user = json.loads(payload["messages"][-1]["content"])

    def find_decision(obj: Any) -> str | None:
        if isinstance(obj, dict):
            if "decision_id" in obj:
                return str(obj["decision_id"])
            for item in obj.values():
                found = find_decision(item)
                if found:
                    return found
        return None

    decision = request.headers.get("x-mb-mock-decision") or find_decision(user) or digest
    if digest not in stages[decision]:
        stages[decision].append(digest)
    stage = int(request.headers.get("x-mb-mock-stage", stages[decision].index(digest)))
    attempt = int(request.headers.get("x-mb-mock-attempt", attempts[digest]))
    attempts[digest] += 1
    scenario_file = os.getenv("MB_MOCK_SCENARIOS")
    scenarios = json.loads(Path(scenario_file).read_text()) if scenario_file else {}
    scenario = scenarios.get(f"{decision}:{stage}:{attempt}", scenarios.get("default", "valid"))
    if scenario in {"401", "403", "429", "500", "503", "402", "402_temporary"}:
        status = int(scenario.split("_")[0])
        return JSONResponse({"error": {"message": "Mock rejection", "metadata": {"limit_source": "in_flight" if scenario.endswith("temporary") else "credits", "reason": scenario}}}, status_code=status)
    if scenario == "slow":
        await asyncio.sleep(60)
    if scenario == "trickle":
        async def trickle():
            for _ in range(100):
                yield b" "
                await asyncio.sleep(1)
        return StreamingResponse(trickle(), media_type="application/json")
    tools = payload.get("tools", [])
    preferred = ["buy_property", "build_houses_or_hotel", "end_turn", "drop_out", "reject_trade", "roll_dice", "pay_jail_fine"]
    # A deliberately asymmetric legal fixture concentrates property ownership,
    # exercises building and bankruptcy, and makes uncapped soaks terminate.
    game = user["game_state"]
    solvent = [player["player_id"] for player in [game["you"], *game["others"]] if player.get("cash", 0) > 0]
    fixture_buyer = min(solvent) if solvent else game["you"]["player_id"]
    if game["metadata"]["you_player_id"] == fixture_buyer:
        preferred.insert(0, "bid_auction")
    else:
        preferred.insert(0, "start_auction")
    tool = next((t for name in preferred for t in tools if t["function"]["name"] == name), tools[0])
    name = tool["function"]["name"]
    args = value_for(tool["function"].get("parameters", {}))
    if name == "build_houses_or_hotel":
        options = user["action_state"]["scenario"]["options"]["buildable_space_keys"]
        owned = user["game_state"]["you"]["holdings"]["owned"]
        candidates = [space for space in owned if space["space_key"] in options]
        selected = min(candidates, key=lambda space: space.get("houses", 0))
        args["build_plan"] = [{"space_key": selected["space_key"], "kind": "HOTEL" if selected.get("houses", 0) == 4 else "HOUSE", "count": 1}]
    response = {"id": "mock-"+digest[:20], "model": payload["model"], "provider": payload["provider"]["only"][0],
                "choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{"id": "call_mock", "type": "function", "function": {"name": "invalid" if scenario == "invalid" else name, "arguments": "{" if scenario == "malformed" else json.dumps(args)}}]}, "finish_reason": "tool_calls"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0.001, "is_byok": False}}
    if scenario == "byok":
        response["usage"] = {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0, "is_byok": True, "cost_details": {"upstream_inference_cost": 0.002}}
    if scenario == "missing_cost":
        response["usage"].pop("cost")
    if scenario == "wrong_model":
        response["model"] = "wrong/model"
    if scenario == "wrong_provider":
        response["provider"] = "wrong"
    return response


@app.get("/api/v1/models")
def models():
    from monopoly_arena.execution_policy import MODELS
    return {"data": [{"id": m, "pricing": {"prompt": "0.000002", "completion": "0.00001"}} for m in MODELS]}


@app.get("/api/v1/models/{model:path}/endpoints")
def endpoints(model: str):
    return {"data": {"id": model, "endpoints": [{"supported_parameters": ["tools", "tool_choice", "reasoning"]}]}}


@app.get("/api/v1/generation")
def generation(id: str):
    return {"data": {"id": id, "total_cost": 0.001, "tokens_prompt": 100, "tokens_completion": 20}}


@app.get("/api/v1/credits")
def credits():
    return {"data": {"total_credits": 100000, "total_usage": 0}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("MB_MOCK_PORT", "8765")))
