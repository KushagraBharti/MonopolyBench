from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


NUMERIC_FIELDS = (
    "calls",
    "successful_calls",
    "failed_calls",
    "byok_calls",
    "non_byok_calls",
    "unknown_byok_calls",
    "prompt_tokens",
    "completion_tokens",
    "reasoning_tokens",
    "total_tokens",
    "reported_usage_cost",
    "reported_upstream_inference_cost",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate canonical and diagnostic OpenRouter probe summaries."
    )
    parser.add_argument("--canonical-summary", action="append", required=True)
    parser.add_argument("--attempt-summary", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    canonical_paths = [(repo_root / value).resolve() for value in args.canonical_summary]
    attempt_paths = [(repo_root / value).resolve() for value in args.attempt_summary]
    canonical = _aggregate_successful_calls(canonical_paths, repo_root=repo_root)
    all_attempts = _aggregate_summaries(attempt_paths)

    canonical_models = _dict(canonical.get("per_model"))
    canonical_valid = (
        len(canonical_models) == 4
        and all(
            _integer(value.get("calls")) == 4
            and _integer(value.get("successful_calls")) == 4
            and _integer(value.get("failed_calls")) == 0
            for value in canonical_models.values()
        )
    )
    payload = {
        "schema_version": "openrouter_byok_probe_consolidated_v1",
        "status": "complete" if canonical_valid else "incomplete",
        "canonical_requirement": "exactly four successful calls for each of four models",
        "canonical_requirement_passed": canonical_valid,
        "canonical_probe": canonical,
        "all_attempts": all_attempts,
        "source_summaries": [
            {
                "path": _relative(repo_root, path),
                "sha256": _sha256_file(path),
                "roles": [
                    role
                    for role, paths in (
                        ("canonical", canonical_paths),
                        ("all_attempts", attempt_paths),
                    )
                    if path in paths
                ],
            }
            for path in sorted(set(canonical_paths + attempt_paths))
        ],
        "cost_interpretation": {
            "actual_reported_cost": (
                "Sum of OpenRouter response usage.cost for the selected calls."
            ),
            "upstream_reference_cost": (
                "Sum of cost_details.upstream_inference_cost; BYOK calls can have a "
                "nonzero reference cost while usage.cost is zero."
            ),
            "credit_snapshot_note": (
                "The immediate account credit snapshots did not yet change. Per-call "
                "usage.cost is retained as the call-level billing evidence."
            ),
        },
    }
    output_path = (repo_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    output_path.with_suffix(".md").write_text(_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "canonical_calls": canonical["totals"]["calls"],
                "canonical_cost": canonical["totals"]["reported_usage_cost"],
                "canonical_tokens": canonical["totals"]["total_tokens"],
                "output": _relative(repo_root, output_path),
                "status": payload["status"],
                "total_attempts": all_attempts["totals"]["calls"],
            },
            sort_keys=True,
        )
    )
    return 0 if canonical_valid else 2


def _aggregate_successful_calls(
    paths: list[Path],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        summary = _read_json(path)
        ledger_path = repo_root / str(summary.get("call_ledger"))
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            row = _dict(json.loads(line))
            if row.get("ok") is True:
                rows.append(row)

    per_model: dict[str, defaultdict[str, float]] = {}
    model_names: dict[str, str] = {}
    providers: dict[str, defaultdict[str, int]] = {}
    for row in rows:
        actor_id = str(row.get("actor_id"))
        usage = _dict(row.get("usage"))
        bucket = per_model.setdefault(actor_id, defaultdict(float))
        provider_bucket = providers.setdefault(actor_id, defaultdict(int))
        model_names[actor_id] = str(row.get("model_requested"))
        bucket["calls"] += 1
        bucket["successful_calls"] += 1
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
        bucket["reported_usage_cost"] += _number(usage.get("cost"))
        bucket["reported_upstream_inference_cost"] += _number(
            _dict(usage.get("cost_details")).get("upstream_inference_cost")
        )
        provider_bucket[str(row.get("provider_returned") or "unknown")] += 1
    return _normalize(
        per_model,
        model_names=model_names,
        providers=providers,
        source_count=len(paths),
    )


def _aggregate_summaries(paths: list[Path]) -> dict[str, Any]:
    per_model: dict[str, defaultdict[str, float]] = {}
    model_names: dict[str, str] = {}
    providers: dict[str, defaultdict[str, int]] = {}
    for path in paths:
        summary = _read_json(path)
        for raw in _list(summary.get("per_model")):
            row = _dict(raw)
            actor_id = str(row.get("actor_id"))
            bucket = per_model.setdefault(actor_id, defaultdict(float))
            provider_bucket = providers.setdefault(actor_id, defaultdict(int))
            model_names[actor_id] = str(row.get("model_requested"))
            for field in NUMERIC_FIELDS:
                bucket[field] += _number(row.get(field))
            for provider, count in _dict(row.get("providers_returned")).items():
                provider_bucket[str(provider)] += _integer(count)

    return _normalize(
        per_model,
        model_names=model_names,
        providers=providers,
        source_count=len(paths),
    )


def _normalize(
    per_model: dict[str, defaultdict[str, float]],
    *,
    model_names: dict[str, str],
    providers: dict[str, defaultdict[str, int]],
    source_count: int,
) -> dict[str, Any]:
    normalized: dict[str, dict[str, Any]] = {}
    for actor_id in sorted(per_model):
        values = per_model[actor_id]
        normalized[actor_id] = {
            "actor_id": actor_id,
            "model_requested": model_names[actor_id],
            **{
                field: (
                    round(values[field], 12)
                    if "cost" in field
                    else int(values[field])
                )
                for field in NUMERIC_FIELDS
            },
            "providers_returned": dict(sorted(providers[actor_id].items())),
        }
    totals = {
        field: (
            round(sum(_number(row[field]) for row in normalized.values()), 12)
            if "cost" in field
            else sum(_integer(row[field]) for row in normalized.values())
        )
        for field in NUMERIC_FIELDS
    }
    return {
        "summary_count": source_count,
        "totals": totals,
        "per_model": normalized,
    }


def _markdown(payload: dict[str, Any]) -> str:
    canonical = _dict(payload.get("canonical_probe"))
    totals = _dict(canonical.get("totals"))
    lines = [
        "# Consolidated OpenRouter BYOK Probe",
        "",
        f"- Canonical requirement passed: **{payload.get('canonical_requirement_passed')}**",
        f"- Calls: {totals.get('calls')}",
        f"- Total tokens: {totals.get('total_tokens')}",
        f"- Reported cost: **${_number(totals.get('reported_usage_cost')):.8f}**",
        f"- BYOK calls: {totals.get('byok_calls')}",
        f"- Non-BYOK calls: {totals.get('non_byok_calls')}",
        "",
        "| Model | Calls | BYOK | Prompt | Completion | Reasoning | Total | Cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for raw in _dict(canonical.get("per_model")).values():
        row = _dict(raw)
        lines.append(
            f"| {row.get('model_requested')} | {row.get('calls')} | "
            f"{row.get('byok_calls')} | {row.get('prompt_tokens')} | "
            f"{row.get('completion_tokens')} | {row.get('reasoning_tokens')} | "
            f"{row.get('total_tokens')} | "
            f"${_number(row.get('reported_usage_cost')):.8f} |"
        )
    attempts = _dict(payload.get("all_attempts"))
    attempt_totals = _dict(attempts.get("totals"))
    lines.extend(
        [
            "",
            "## All attempts",
            "",
            f"- Attempts: {attempt_totals.get('calls')}",
            f"- Successful: {attempt_totals.get('successful_calls')}",
            f"- Failed: {attempt_totals.get('failed_calls')}",
            f"- Tokens: {attempt_totals.get('total_tokens')}",
            f"- Reported cost: ${_number(attempt_totals.get('reported_usage_cost')):.8f}",
            "",
            "Four failed attempts were Anthropic requests with the roster's explicit",
            '`provider.only=["anthropic"]` filter. Unfiltered diagnostic requests returned',
            "provider `Anthropic`, `is_byok=true`, and zero reported cost.",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return _dict(json.loads(path.read_text(encoding="utf-8")))


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _number(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _integer(value: Any) -> int:
    return int(_number(value))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
