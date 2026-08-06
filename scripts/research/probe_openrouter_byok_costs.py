from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import subprocess
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_ROSTER = "frontier_medium_4lab"
DEFAULT_OUTPUT_ROOT = "analysis/research_protocol/control_audit"
PROMPTS = [
    "Reply with exactly one unusual adjective for a purple bicycle.",
    "Invent one harmless law for a city run by housecats. Use one sentence.",
    "Return a JSON object with keys color and number; choose any color and integer.",
    "Write a seven-word motto for an overly ambitious sandwich.",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Make small secret-free OpenRouter probes and reconcile BYOK, tokens, and cost."
    )
    parser.add_argument("--roster", default=DEFAULT_ROSTER)
    parser.add_argument("--calls-per-model", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--shuffle-seed", type=int, default=2026072902)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--actor-id",
        action="append",
        default=[],
        help="Limit the probe to one or more actor IDs. May be repeated.",
    )
    parser.add_argument(
        "--omit-provider-constraint",
        action="store_true",
        help="Diagnostic only: omit the roster provider object from requests.",
    )
    parser.add_argument(
        "--omit-provider-only",
        action="store_true",
        help="Diagnostic only: retain provider controls except the `only` allowlist.",
    )
    args = parser.parse_args()

    if args.calls_per_model < 1:
        raise SystemExit("--calls-per-model must be at least 1.")
    if args.max_tokens < 32:
        raise SystemExit("--max-tokens must be at least 32.")

    repo_root = Path(__file__).resolve().parents[2]
    api_key = os.getenv("OPENROUTER_API_KEY") or _read_env_value(
        repo_root / ".env",
        "OPENROUTER_API_KEY",
    )
    if not api_key:
        raise SystemExit(
            "OPENROUTER_API_KEY is unavailable; no provider request was made."
        )

    registry_path = (
        repo_root / "contracts/research/monopoly_long_v1_model_rosters.json"
    )
    registry = _read_json(registry_path)
    roster = _dict(_dict(registry.get("rosters")).get(args.roster))
    actors_by_id = _dict(registry.get("actors"))
    actors = [
        _dict(actors_by_id.get(str(actor_id)))
        for actor_id in _list(roster.get("actor_ids"))
    ]
    if len(actors) != 4 or any(
        not actor or actor.get("actor_type") != "llm" for actor in actors
    ):
        raise SystemExit("The selected roster must contain exactly four LLM actors.")
    requested_actor_ids = {str(value) for value in args.actor_id}
    if requested_actor_ids:
        actors = [
            actor
            for actor in actors
            if str(actor.get("actor_id")) in requested_actor_ids
        ]
        resolved_actor_ids = {str(actor.get("actor_id")) for actor in actors}
        missing_actor_ids = requested_actor_ids - resolved_actor_ids
        if missing_actor_ids:
            raise SystemExit(
                f"Actor IDs are not in roster {args.roster}: {sorted(missing_actor_ids)}"
            )

    observed_at = _utc_now()
    run_stamp = observed_at.replace("-", "").replace(":", "").replace(".", "")
    run_stamp = run_stamp.replace("+00:00", "Z")
    output_dir = (repo_root / args.output_root / f"openrouter_byok_probe_{run_stamp}").resolve()
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing probe directory: {output_dir}")
    response_dir = output_dir / "responses"
    response_dir.mkdir(parents=True)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "MonopolyBench-BYOK-cost-probe/1",
        "X-Title": "MonopolyBench BYOK Cost Probe",
    }
    credits_before = _get_json(
        f"{OPENROUTER_BASE_URL}/credits",
        headers=headers,
    )

    plan = _build_plan(
        actors,
        calls_per_model=args.calls_per_model,
        shuffle_seed=args.shuffle_seed,
    )
    call_rows: list[dict[str, Any]] = []
    for execution_index, item in enumerate(plan, start=1):
        actor = _dict(item["actor"])
        prompt = str(item["prompt"])
        call_id = f"call-{execution_index:03d}-{actor['actor_id']}"
        payload: dict[str, Any] = {
            "model": actor["openrouter_model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": args.max_tokens,
            "stream": False,
            "usage": {"include": True},
        }
        if not args.omit_provider_constraint:
            provider = dict(_dict(actor.get("provider")))
            if args.omit_provider_only:
                provider.pop("only", None)
            payload["provider"] = provider
        if isinstance(actor.get("reasoning"), dict):
            payload["reasoning"] = actor["reasoning"]

        result = _post_json(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            payload=payload,
        )
        response_path = response_dir / f"{call_id}.json"
        response_path.write_text(
            json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        body = _dict(result.get("body"))
        usage = _dict(body.get("usage"))
        call_rows.append(
            {
                "schema_version": "openrouter_byok_probe_call_v1",
                "call_id": call_id,
                "execution_index": execution_index,
                "actor_id": actor.get("actor_id"),
                "model_requested": actor.get("openrouter_model_id"),
                "model_returned": body.get("model"),
                "provider_constraint": actor.get("provider"),
                "provider_constraint_sent": not args.omit_provider_constraint,
                "provider_only_omitted": args.omit_provider_only,
                "provider_returned": body.get("provider"),
                "reasoning": actor.get("reasoning"),
                "prompt_index": item["prompt_index"],
                "prompt": prompt,
                "prompt_sha256": _sha256_text(prompt),
                "max_tokens": args.max_tokens,
                "http_status": result.get("status"),
                "ok": result.get("ok") is True,
                "request_id": result.get("request_id") or body.get("id"),
                "response_id": body.get("id"),
                "finish_reason": _finish_reason(body),
                "usage": usage,
                "response_path": _relative(repo_root, response_path),
                "observed_at_utc": result.get("observed_at_utc"),
                "error": result.get("error"),
            }
        )
        print(
            json.dumps(
                {
                    "actor_id": actor.get("actor_id"),
                    "call": item["prompt_index"],
                    "cost": _number_or_zero(usage.get("cost")),
                    "execution_index": execution_index,
                    "is_byok": usage.get("is_byok"),
                    "ok": result.get("ok") is True,
                    "total_tokens": _integer(usage.get("total_tokens")),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    credits_after = _get_json(
        f"{OPENROUTER_BASE_URL}/credits",
        headers=headers,
    )
    ledger_path = output_dir / "calls.jsonl"
    ledger_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n"
            for row in call_rows
        ),
        encoding="utf-8",
    )

    summary = _summarize(
        call_rows,
        credits_before=credits_before,
        credits_after=credits_after,
    )
    summary.update(
        {
            "schema_version": "openrouter_byok_cost_probe_v1",
            "probe_version": "openrouter_byok_cost_probe_v1",
            "started_at_utc": observed_at,
            "completed_at_utc": _utc_now(),
            "roster_id": args.roster,
            "calls_per_model_planned": args.calls_per_model,
            "planned_call_count": len(plan),
            "recorded_call_count": len(call_rows),
            "max_tokens": args.max_tokens,
            "shuffle_seed": args.shuffle_seed,
            "actor_filter": sorted(requested_actor_ids),
            "provider_constraint_sent": not args.omit_provider_constraint,
            "provider_only_omitted": args.omit_provider_only,
            "prompts": PROMPTS,
            "call_ledger": _relative(repo_root, ledger_path),
            "response_directory": _relative(repo_root, response_dir),
            "source_commit": _git_head(repo_root),
            "provenance": {
                "script": _relative(repo_root, Path(__file__).resolve()),
                "script_sha256": _sha256_file(Path(__file__).resolve()),
                "registry": _relative(repo_root, registry_path),
                "registry_sha256": _sha256_file(registry_path),
                "api_key_loaded": True,
                "api_key_persisted": False,
            },
            "interpretation": {
                "reported_usage_cost": (
                    "Sum of response usage.cost fields exactly as reported by OpenRouter."
                ),
                "credit_delta": (
                    "Difference between authenticated OpenRouter available-credit snapshots. "
                    "It can include unrelated concurrent account activity."
                ),
                "byok": (
                    "Per-call usage.is_byok is the primary evidence that a provider key "
                    "served the request."
                ),
            },
        }
    )
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    summary_path.with_suffix(".md").write_text(
        _markdown(summary),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "byok_calls": summary["totals"]["byok_calls"],
                "failed_calls": summary["totals"]["failed_calls"],
                "output": _relative(repo_root, summary_path),
                "reported_cost": summary["totals"]["reported_usage_cost"],
                "successful_calls": summary["totals"]["successful_calls"],
                "total_tokens": summary["totals"]["total_tokens"],
            },
            sort_keys=True,
        )
    )
    return 0 if summary["totals"]["successful_calls"] == len(plan) else 2


def _build_plan(
    actors: list[dict[str, Any]],
    *,
    calls_per_model: int,
    shuffle_seed: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for actor in actors:
        for call_index in range(calls_per_model):
            prompt_index = call_index % len(PROMPTS)
            rows.append(
                {
                    "actor": actor,
                    "prompt_index": prompt_index + 1,
                    "prompt": PROMPTS[prompt_index],
                }
            )
    random.Random(shuffle_seed).shuffle(rows)
    return rows


def _summarize(
    rows: list[dict[str, Any]],
    *,
    credits_before: dict[str, Any],
    credits_after: dict[str, Any],
) -> dict[str, Any]:
    per_actor: dict[str, dict[str, Any]] = {}
    for row in rows:
        actor_id = str(row.get("actor_id"))
        bucket = per_actor.setdefault(
            actor_id,
            {
                "actor_id": actor_id,
                "model_requested": row.get("model_requested"),
                "calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "byok_calls": 0,
                "non_byok_calls": 0,
                "unknown_byok_calls": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
                "reported_usage_cost": 0.0,
                "reported_upstream_inference_cost": 0.0,
                "providers_returned": Counter(),
            },
        )
        usage = _dict(row.get("usage"))
        bucket["calls"] += 1
        if row.get("ok") is True:
            bucket["successful_calls"] += 1
        else:
            bucket["failed_calls"] += 1
        if usage.get("is_byok") is True:
            bucket["byok_calls"] += 1
        elif usage.get("is_byok") is False:
            bucket["non_byok_calls"] += 1
        else:
            bucket["unknown_byok_calls"] += 1
        bucket["prompt_tokens"] += _integer(usage.get("prompt_tokens"))
        bucket["completion_tokens"] += _integer(usage.get("completion_tokens"))
        bucket["reasoning_tokens"] += _integer(
            _dict(usage.get("completion_tokens_details")).get("reasoning_tokens")
        )
        bucket["total_tokens"] += _integer(usage.get("total_tokens"))
        bucket["reported_usage_cost"] += _number_or_zero(usage.get("cost"))
        bucket["reported_upstream_inference_cost"] += _number_or_zero(
            _dict(usage.get("cost_details")).get("upstream_inference_cost")
        )
        provider = str(row.get("provider_returned") or "unknown")
        bucket["providers_returned"][provider] += 1

    normalized: list[dict[str, Any]] = []
    for value in per_actor.values():
        value["providers_returned"] = dict(
            sorted(_counter(value["providers_returned"]).items())
        )
        value["reported_usage_cost"] = round(value["reported_usage_cost"], 12)
        value["reported_upstream_inference_cost"] = round(
            value["reported_upstream_inference_cost"],
            12,
        )
        normalized.append(value)
    normalized.sort(key=lambda value: value["actor_id"])

    before_available = _available_credits(credits_before)
    after_available = _available_credits(credits_after)
    credit_delta = (
        round(before_available - after_available, 12)
        if before_available is not None and after_available is not None
        else None
    )
    return {
        "totals": {
            "calls": sum(value["calls"] for value in normalized),
            "successful_calls": sum(
                value["successful_calls"] for value in normalized
            ),
            "failed_calls": sum(value["failed_calls"] for value in normalized),
            "byok_calls": sum(value["byok_calls"] for value in normalized),
            "non_byok_calls": sum(value["non_byok_calls"] for value in normalized),
            "unknown_byok_calls": sum(
                value["unknown_byok_calls"] for value in normalized
            ),
            "prompt_tokens": sum(value["prompt_tokens"] for value in normalized),
            "completion_tokens": sum(
                value["completion_tokens"] for value in normalized
            ),
            "reasoning_tokens": sum(
                value["reasoning_tokens"] for value in normalized
            ),
            "total_tokens": sum(value["total_tokens"] for value in normalized),
            "reported_usage_cost": round(
                sum(value["reported_usage_cost"] for value in normalized),
                12,
            ),
            "reported_upstream_inference_cost": round(
                sum(
                    value["reported_upstream_inference_cost"]
                    for value in normalized
                ),
                12,
            ),
            "openrouter_available_credit_before": before_available,
            "openrouter_available_credit_after": after_available,
            "openrouter_available_credit_delta": credit_delta,
        },
        "per_model": normalized,
        "credits_before": _credit_snapshot(credits_before),
        "credits_after": _credit_snapshot(credits_after),
    }


def _get_json(url: str, *, headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    return _execute_request(request)


def _post_json(
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    request = urllib.request.Request(url, data=raw, headers=headers, method="POST")
    return _execute_request(request)


def _execute_request(request: urllib.request.Request) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            raw = response.read()
            return {
                "ok": True,
                "url": request.full_url,
                "status": int(response.status),
                "request_id": response.headers.get("x-request-id")
                or response.headers.get("openrouter-request-id"),
                "observed_at_utc": _utc_now(),
                "body": json.loads(raw.decode("utf-8")),
            }
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            body: Any = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw_text": raw}
        return {
            "ok": False,
            "url": request.full_url,
            "status": int(error.code),
            "request_id": error.headers.get("x-request-id")
            or error.headers.get("openrouter-request-id"),
            "observed_at_utc": _utc_now(),
            "body": body,
            "error": f"HTTP {error.code}",
        }
    except urllib.error.URLError as error:
        return {
            "ok": False,
            "url": request.full_url,
            "status": None,
            "request_id": None,
            "observed_at_utc": _utc_now(),
            "body": {},
            "error": str(error.reason),
        }


def _credit_snapshot(response: dict[str, Any]) -> dict[str, Any]:
    data = _dict(_dict(response.get("body")).get("data"))
    return {
        "observed_at_utc": response.get("observed_at_utc"),
        "status": response.get("status"),
        "request_id": response.get("request_id"),
        "total_credits": _number_or_none(data.get("total_credits")),
        "total_usage": _number_or_none(data.get("total_usage")),
        "available_credits": _available_credits(response),
    }


def _available_credits(response: dict[str, Any]) -> float | None:
    data = _dict(_dict(response.get("body")).get("data"))
    credits = _number_or_none(data.get("total_credits"))
    usage = _number_or_none(data.get("total_usage"))
    if credits is None or usage is None:
        return None
    return round(credits - usage, 12)


def _finish_reason(body: dict[str, Any]) -> Any:
    choices = _list(body.get("choices"))
    if not choices or not isinstance(choices[0], dict):
        return None
    return choices[0].get("finish_reason")


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
    return _dict(value)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _counter(value: Any) -> Counter[str]:
    return value if isinstance(value, Counter) else Counter()


def _integer(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    return 0


def _number_or_zero(value: Any) -> float:
    result = _number_or_none(value)
    return result if result is not None else 0.0


def _number_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _relative(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _markdown(payload: dict[str, Any]) -> str:
    totals = _dict(payload.get("totals"))
    lines = [
        "# OpenRouter BYOK Cost Probe",
        "",
        f"- Successful calls: {totals.get('successful_calls')}/{totals.get('calls')}",
        f"- BYOK calls: {totals.get('byok_calls')}",
        f"- Non-BYOK calls: {totals.get('non_byok_calls')}",
        f"- Total tokens: {totals.get('total_tokens')}",
        f"- Reported usage cost: ${_number_or_zero(totals.get('reported_usage_cost')):.8f}",
        (
            "- OpenRouter available-credit delta: "
            f"${_number_or_zero(totals.get('openrouter_available_credit_delta')):.8f}"
        ),
        "",
        "| Actor | Calls | BYOK | Prompt | Completion | Reasoning | Total | Cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for value in _list(payload.get("per_model")):
        row = _dict(value)
        lines.append(
            f"| {row.get('actor_id')} | {row.get('calls')} | {row.get('byok_calls')} | "
            f"{row.get('prompt_tokens')} | {row.get('completion_tokens')} | "
            f"{row.get('reasoning_tokens')} | {row.get('total_tokens')} | "
            f"${_number_or_zero(row.get('reported_usage_cost')):.8f} |"
        )
    lines.extend(
        [
            "",
            "The credit delta is an account-level before/after observation and may include",
            "unrelated concurrent activity. Per-call `usage.is_byok` is the routing evidence.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
