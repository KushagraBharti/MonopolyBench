from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic, interleaved exact-history repetition manifest."
    )
    parser.add_argument("--fixtures", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--roster", default="frontier_medium_4lab")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--execution-order-seed", type=int, required=True)
    parser.add_argument("--cost-budget", type=float, default=10.0)
    args = parser.parse_args()
    if args.repetitions < 1:
        raise SystemExit("--repetitions must be positive")

    repo_root = Path(__file__).resolve().parents[2]
    fixtures_dir = (repo_root / args.fixtures).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    fixture_manifest_path = fixtures_dir / "manifest.json"
    fixture_manifest = _read_json(fixture_manifest_path)
    if fixture_manifest.get("schema_version") != "trajectory_fixture_collection_manifest_v2":
        raise SystemExit(
            "Repetition planning requires trajectory fixture collection v2 ordered inputs."
        )
    if not fixture_manifest.get("all_exact_history"):
        raise SystemExit("Fixture collection did not pass exact-history validation.")
    fixture_rows = [row for row in _list(fixture_manifest.get("fixtures")) if isinstance(row, dict)]

    roster_path = repo_root / "contracts" / "research" / "monopoly_long_v1_model_rosters.json"
    registry = _read_json(roster_path)
    roster = _dict(_dict(registry.get("rosters")).get(args.roster))
    if not roster:
        raise SystemExit(f"Unknown roster: {args.roster}")
    actors_by_id = _dict(registry.get("actors"))
    actors = [_dict(actors_by_id.get(str(actor_id))) for actor_id in _list(roster.get("actor_ids"))]
    if any(not actor or actor.get("actor_type") != "llm" for actor in actors):
        raise SystemExit("Repetition roster must contain four enabled LLM actors.")

    calls: list[dict[str, Any]] = []
    for fixture in fixture_rows:
        fixture_id = str(fixture["fixture_id"])
        fixture_dir = fixtures_dir / str(fixture["relative_path"])
        fixture_payload = _read_json(fixture_dir / "fixture.json")
        ordered_inputs = _dict(fixture_payload.get("ordered_prompt_inputs"))
        if (
            fixture_payload.get("schema_version") != "trajectory_fixture_v2"
            or not ordered_inputs.get("decision")
            or not ordered_inputs.get("memory")
        ):
            raise SystemExit(f"Fixture {fixture_id} lacks v2 ordered prompt inputs.")
        source_dir = fixture_dir / "source"
        source_hashes = {
            "system_sha256": _sha256_file(source_dir / "original_system.txt"),
            "user_sha256": _sha256_file(source_dir / "original_user.json"),
            "tools_sha256": _sha256_file(source_dir / "original_tools.json"),
        }
        for actor in actors:
            for repetition_index in range(args.repetitions):
                identity = {
                    "experiment_id": args.experiment_id,
                    "fixture_id": fixture_id,
                    "actor_id": actor["actor_id"],
                    "model_id": actor["openrouter_model_id"],
                    "repetition_index": repetition_index,
                }
                digest = _sha256_json(identity)
                order_key = _sha256_json(
                    {
                        **identity,
                        "execution_order_seed": args.execution_order_seed,
                    }
                )
                calls.append(
                    {
                        "schema_version": "exact_history_repetition_call_v1",
                        "repetition_id": f"rep-{digest[:20]}",
                        "execution_rank": None,
                        "execution_order_key": order_key,
                        "fixture_id": fixture_id,
                        "fixture_relative_path": str(
                            fixture_dir.relative_to(repo_root)
                        ).replace("\\", "/"),
                        "source_run_id": fixture.get("source_run_id"),
                        "source_decision_id": fixture.get("source_decision_id"),
                        "source_category": fixture.get("category"),
                        "actor_id": actor["actor_id"],
                        "model_id": actor["openrouter_model_id"],
                        "provider_constraint": actor.get("provider"),
                        "reasoning": actor.get("reasoning"),
                        "repetition_index": repetition_index,
                        "prompt_mode": "regenerated_exact_history",
                        **source_hashes,
                        "status": "planned",
                    }
                )
    ordered_calls = _interleaved_order(calls)
    for rank, call in enumerate(ordered_calls):
        call["execution_rank"] = rank

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output_dir / "calls.jsonl", ordered_calls)
    manifest = {
        "schema_version": "fixture_repetition_manifest_v1",
        "experiment_id": args.experiment_id,
        "status": "planned_not_executed",
        "provider_calls": 0,
        "source_fixture_manifest": str(fixture_manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "source_fixture_manifest_sha256": _sha256_file(fixture_manifest_path),
        "source_fixture_collection_tree_sha256": fixture_manifest.get(
            "collection_tree_sha256"
        ),
        "roster_id": args.roster,
        "roster_version": roster.get("version"),
        "roster_registry_sha256": _sha256_file(roster_path),
        "models": [
            {
                "actor_id": actor["actor_id"],
                "model_id": actor["openrouter_model_id"],
                "provider_constraint": actor.get("provider"),
                "reasoning": actor.get("reasoning"),
                "sampling_policy": "provider_default_unseeded",
            }
            for actor in actors
        ],
        "fixture_count": len(fixture_rows),
        "repetitions_per_model_fixture": args.repetitions,
        "planned_call_count": len(ordered_calls),
        "execution_order_seed": args.execution_order_seed,
        "execution_order_algorithm": (
            "SHA-256 keyed sort followed by deterministic greedy interleaving that avoids "
            "repeating model and fixture when an alternative remains"
        ),
        "max_consecutive_same_model": _max_consecutive(ordered_calls, "model_id"),
        "max_consecutive_same_fixture": _max_consecutive(ordered_calls, "fixture_id"),
        "cost_budget": args.cost_budget,
        "budget_policy": "stop_immediately_preserve_all_planned_calls",
        "technical_rerun_policy": (
            "Retain the original failed call; any generally authorized rerun receives a new "
            "repetition ID and does not replace the original."
        ),
        "calls_jsonl": "calls.jsonl",
        "calls_jsonl_sha256": _sha256_file(output_dir / "calls.jsonl"),
        "source_commit": _git_head(repo_root),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": (
                "The manifest schedules prompts regenerated from persisted v2 ordered inputs "
                "only after byte equality with the saved source passes. Fixture IDs, source "
                "actions, scores, labels, and outcomes are not included in provider messages."
            ),
        },
    }
    _write_json(output_dir / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "fixture_count": len(fixture_rows),
                "planned_call_count": len(ordered_calls),
                "max_consecutive_same_model": manifest["max_consecutive_same_model"],
                "max_consecutive_same_fixture": manifest["max_consecutive_same_fixture"],
                "provider_calls": 0,
            },
            sort_keys=True,
        )
    )
    return 0


def _interleaved_order(calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pending = sorted(calls, key=lambda row: str(row["execution_order_key"]))
    result: list[dict[str, Any]] = []
    while pending:
        previous = result[-1] if result else None
        selected_index = 0
        if previous is not None:
            for index, candidate in enumerate(pending):
                if (
                    candidate["model_id"] != previous["model_id"]
                    and candidate["fixture_id"] != previous["fixture_id"]
                ):
                    selected_index = index
                    break
            else:
                for index, candidate in enumerate(pending):
                    if candidate["model_id"] != previous["model_id"]:
                        selected_index = index
                        break
        result.append(pending.pop(selected_index))
    return result


def _max_consecutive(rows: list[dict[str, Any]], key: str) -> int:
    maximum = 0
    current = 0
    previous: Any = object()
    for row in rows:
        value = row.get(key)
        if value == previous:
            current += 1
        else:
            previous = value
            current = 1
        maximum = max(maximum, current)
    return maximum


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
