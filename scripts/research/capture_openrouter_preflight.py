from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
REQUIRED_TOOL_PARAMETERS = {"tools", "tool_choice"}
DEFAULT_MINIMUM_AVAILABLE = 110.0
PREFLIGHT_TOOL_NAME = "monopolybench_route_ack"
PREFLIGHT_ROUTE_TOKEN = "MONOPOLYBENCH_ROUTE_OK"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture an authenticated, secret-free OpenRouter endpoint and credit preflight."
    )
    parser.add_argument("--roster", default="frontier_medium_4lab")
    parser.add_argument(
        "--output",
        default="analysis/research_protocol/control_audit/openrouter_preflight.json",
    )
    parser.add_argument(
        "--minimum-available",
        type=float,
        default=DEFAULT_MINIMUM_AVAILABLE,
        help="Minimum available OpenRouter credits required to authorize paid execution.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    api_key = os.getenv("OPENROUTER_API_KEY") or _read_env_value(
        repo_root / ".env", "OPENROUTER_API_KEY"
    )
    if not api_key:
        raise SystemExit(
            "OPENROUTER_API_KEY is not available in the environment or repository .env file."
        )

    registry_path = (
        repo_root / "contracts" / "research" / "monopoly_long_v1_model_rosters.json"
    )
    registry = _read_json(registry_path)
    roster = _dict(_dict(registry.get("rosters")).get(args.roster))
    if not roster:
        raise SystemExit(f"Unknown roster: {args.roster}")
    actors_by_id = _dict(registry.get("actors"))
    actors = [
        _dict(actors_by_id.get(str(actor_id)))
        for actor_id in _list(roster.get("actor_ids"))
    ]
    if any(not actor for actor in actors):
        raise SystemExit(f"Roster {args.roster} references an unresolved actor.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "MonopolyBench-research-preflight/1",
        "X-Title": "MonopolyBench E1 Route Preflight",
    }
    models_response = _get_json(f"{OPENROUTER_BASE_URL}/models", headers=headers)
    credits_response = _get_json(f"{OPENROUTER_BASE_URL}/credits", headers=headers)
    catalog_by_id = {
        str(model.get("id")): model
        for model in _list(_dict(models_response.get("body")).get("data"))
        if isinstance(model, dict) and model.get("id")
    }

    model_checks: list[dict[str, Any]] = []
    for actor in actors:
        model_id = str(actor.get("openrouter_model_id") or "")
        provider = _dict(actor.get("provider"))
        provider_only = [str(value) for value in _list(provider.get("only"))]
        endpoint_response = _get_json(
            f"{OPENROUTER_BASE_URL}/models/{model_id}/endpoints",
            headers=headers,
        )
        endpoint_data = _dict(_dict(endpoint_response.get("body")).get("data"))
        endpoints = [
            endpoint
            for endpoint in _list(endpoint_data.get("endpoints"))
            if isinstance(endpoint, dict)
        ]
        matching_endpoints = [
            endpoint
            for endpoint in endpoints
            if not provider_only
            or _endpoint_matches_any_provider(endpoint, provider_only)
        ]
        required_parameters = set(REQUIRED_TOOL_PARAMETERS)
        if isinstance(actor.get("reasoning"), dict):
            required_parameters.add("reasoning_effort")
        parameter_complete = [
            endpoint
            for endpoint in matching_endpoints
            if required_parameters.issubset(
                {str(value) for value in _list(endpoint.get("supported_parameters"))}
            )
        ]
        billing_policy = _dict(actor.get("billing_policy"))
        tool_call_check = _tool_route_check(
            actor=actor,
            billing_policy=billing_policy,
            headers=headers,
        )
        model_checks.append(
            {
                "actor_id": actor.get("actor_id"),
                "model_id": model_id,
                "reasoning": actor.get("reasoning"),
                "provider_route": provider,
                "billing_policy": billing_policy,
                "catalog_present": model_id in catalog_by_id,
                "catalog_entry": catalog_by_id.get(model_id),
                "endpoint_request": {
                    key: value
                    for key, value in endpoint_response.items()
                    if key != "body"
                },
                "endpoint_model": {
                    key: value
                    for key, value in endpoint_data.items()
                    if key != "endpoints"
                },
                "matching_endpoint_count": len(matching_endpoints),
                "parameter_complete_endpoint_count": len(parameter_complete),
                "required_parameters": sorted(required_parameters),
                "matching_endpoints": matching_endpoints,
                "tool_call_check": tool_call_check,
                "route_ready": bool(
                    model_id in catalog_by_id
                    and parameter_complete
                    and tool_call_check["route_ready"]
                ),
            }
        )

    credits_body = _dict(credits_response.get("body"))
    credits_data = _dict(credits_body.get("data"))
    total_credits = _number_or_none(credits_data.get("total_credits"))
    total_usage = _number_or_none(credits_data.get("total_usage"))
    available_credits = (
        round(total_credits - total_usage, 10)
        if total_credits is not None and total_usage is not None
        else None
    )
    payload = {
        "schema_version": "v1",
        "preflight_version": "openrouter_campaign_preflight_v2",
        "observed_at_utc": _utc_now(),
        "source_commit": _git_head(repo_root),
        "roster_id": args.roster,
        "roster_version": roster.get("version"),
        "sampling_policy": {
            "temperature": "provider_default_not_sent",
            "top_p": "provider_default_not_sent",
            "reasoning": "actor-specific reasoning.effort is sent",
            "interpretation": (
                "Model generation remains stochastic and ecological. Endpoint routing, request payloads, "
                "and observation times are frozen or recorded; unexposed provider internals are not."
            ),
        },
        "models_request": {
            key: value for key, value in models_response.items() if key != "body"
        },
        "model_checks": model_checks,
        "credits_request": {
            key: value for key, value in credits_response.items() if key != "body"
        },
        "credits": {
            "total_credits": total_credits,
            "total_usage": total_usage,
            "available_credits": available_credits,
            "minimum_available_required": args.minimum_available,
        },
        "verdict": {
            "all_models_present": all(
                check["catalog_present"] for check in model_checks
            ),
            "all_tool_calls_ready": all(
                _dict(check.get("tool_call_check")).get("tool_call_valid") is True
                for check in model_checks
            ),
            "all_billing_policies_satisfied": all(
                _dict(check.get("tool_call_check")).get("billing_policy_satisfied")
                is True
                for check in model_checks
            ),
            "openai_byok_ready": all(
                _dict(check.get("tool_call_check")).get("byok_requirement_satisfied")
                is True
                for check in model_checks
                if _dict(check.get("billing_policy")).get("mode") == "byok_required"
            ),
            "all_routes_ready": all(check["route_ready"] for check in model_checks),
            "credit_balance_available": available_credits is not None,
            "paid_pilot_authorized_by_preflight": bool(
                all(check["route_ready"] for check in model_checks)
                and available_credits is not None
                and available_credits >= args.minimum_available
            ),
        },
        "provenance": {
            "registry_path": str(registry_path.relative_to(repo_root)).replace(
                "\\", "/"
            ),
            "registry_sha256": _sha256_file(registry_path),
            "models_body_sha256": _sha256_json(models_response.get("body")),
            "credits_body_sha256": _sha256_json(credits_response.get("body")),
            "api_key_persisted": False,
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": (
                "This script sends a separate preflight-only forced tool call to each route. "
                "It never constructs or changes a MonopolyBench game prompt."
            ),
        },
    }

    output_path = (repo_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(output_path),
                "all_routes_ready": payload["verdict"]["all_routes_ready"],
                "available_credits": available_credits,
                "model_count": len(model_checks),
            },
            sort_keys=True,
        )
    )
    return 0 if payload["verdict"]["paid_pilot_authorized_by_preflight"] else 1


def _tool_route_check(
    *,
    actor: dict[str, Any],
    billing_policy: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    model_id = str(actor.get("openrouter_model_id") or "")
    payload: dict[str, Any] = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Call {PREFLIGHT_TOOL_NAME} with route_token exactly "
                    f"{PREFLIGHT_ROUTE_TOKEN}. Do not answer in text."
                ),
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": PREFLIGHT_TOOL_NAME,
                    "description": "Acknowledge the MonopolyBench route preflight.",
                    "parameters": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["route_token"],
                        "properties": {
                            "route_token": {
                                "type": "string",
                                "enum": [PREFLIGHT_ROUTE_TOKEN],
                            }
                        },
                    },
                },
            }
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": PREFLIGHT_TOOL_NAME},
        },
        "parallel_tool_calls": False,
        "usage": {"include": True},
    }
    provider = _dict(actor.get("provider"))
    if provider:
        payload["provider"] = provider
    reasoning = _dict(actor.get("reasoning"))
    if reasoning:
        payload["reasoning"] = reasoning

    result = _post_json(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        payload=payload,
    )
    body = _dict(result.get("body"))
    usage = _dict(body.get("usage"))
    tool_call = _first_tool_call(body)
    arguments = _parse_tool_arguments(tool_call)
    tool_call_valid = bool(
        _dict(tool_call.get("function")).get("name") == PREFLIGHT_TOOL_NAME
        and arguments.get("route_token") == PREFLIGHT_ROUTE_TOKEN
    )
    expected_provider = str(billing_policy.get("expected_provider") or "")
    provider_matches = bool(
        expected_provider and body.get("provider") == expected_provider
    )
    model_matches = body.get("model") == model_id
    byok_required = billing_policy.get("mode") == "byok_required"
    byok_requirement_satisfied = not byok_required or usage.get("is_byok") is True
    billing_policy_satisfied = bool(
        provider_matches and model_matches and byok_requirement_satisfied
    )
    route_ready = bool(
        result.get("ok") is True and tool_call_valid and billing_policy_satisfied
    )
    return {
        "schema_version": "v1",
        "request_payload_sha256": _sha256_json(payload),
        "observed_at_utc": result.get("observed_at_utc"),
        "http_status": result.get("status"),
        "ok": result.get("ok") is True,
        "request_id": result.get("request_id") or body.get("id"),
        "model_requested": model_id,
        "model_returned": body.get("model"),
        "model_matches": model_matches,
        "provider_route_sent": provider,
        "provider_returned": body.get("provider"),
        "expected_provider": expected_provider,
        "provider_matches": provider_matches,
        "billing_mode": billing_policy.get("mode"),
        "is_byok": usage.get("is_byok"),
        "byok_requirement_satisfied": byok_requirement_satisfied,
        "billing_policy_satisfied": billing_policy_satisfied,
        "tool_call_valid": tool_call_valid,
        "tool_call": tool_call,
        "usage": usage,
        "response_body_sha256": _sha256_json(body) if body else None,
        "error": result.get("error"),
        "route_ready": route_ready,
    }


def _first_tool_call(body: dict[str, Any]) -> dict[str, Any]:
    choices = _list(body.get("choices"))
    if not choices or not isinstance(choices[0], dict):
        return {}
    message = _dict(choices[0].get("message"))
    tool_calls = _list(message.get("tool_calls"))
    if not tool_calls or not isinstance(tool_calls[0], dict):
        return {}
    return tool_calls[0]


def _parse_tool_arguments(tool_call: dict[str, Any]) -> dict[str, Any]:
    raw = _dict(tool_call.get("function")).get("arguments")
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _post_json(
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    request = urllib.request.Request(url, data=raw, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            response_raw = response.read()
            return {
                "url": url,
                "status": int(response.status),
                "ok": True,
                "request_id": response.headers.get("x-request-id")
                or response.headers.get("openrouter-request-id"),
                "observed_at_utc": _utc_now(),
                "body": json.loads(response_raw.decode("utf-8")),
                "error": None,
            }
    except urllib.error.HTTPError as error:
        response_raw = error.read().decode("utf-8", errors="replace")
        return {
            "url": url,
            "status": int(error.code),
            "ok": False,
            "request_id": error.headers.get("x-request-id")
            or error.headers.get("openrouter-request-id"),
            "observed_at_utc": _utc_now(),
            "body": {},
            "error": response_raw,
        }
    except urllib.error.URLError as error:
        return {
            "url": url,
            "status": None,
            "ok": False,
            "request_id": None,
            "observed_at_utc": _utc_now(),
            "body": {},
            "error": str(error),
        }


def _get_json(url: str, *, headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            return {
                "url": url,
                "status": int(response.status),
                "request_id": response.headers.get("x-request-id")
                or response.headers.get("openrouter-request-id"),
                "observed_at_utc": _utc_now(),
                "body": json.loads(raw.decode("utf-8")),
            }
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"OpenRouter GET {url} failed with HTTP {error.code}: {raw}"
        ) from error


def _endpoint_matches_any_provider(
    endpoint: dict[str, Any], provider_slugs: list[str]
) -> bool:
    tag = str(endpoint.get("tag") or "").lower()
    return any(tag == slug.lower() for slug in provider_slugs)


def _read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip("\"'")
    return None


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(value: Any) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _number_or_none(value: Any) -> float | None:
    return (
        float(value)
        if isinstance(value, (int, float)) and not isinstance(value, bool)
        else None
    )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
