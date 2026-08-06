from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from prove_prompt_reconstruction import _run_source  # noqa: E402


DEFAULT_SELECTION = "analysis/research_protocol/architecture_proof/selection.json"
DEFAULT_OUTPUT = "analysis/research_protocol/architecture_proof/fixtures_v2"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build canonical exact-history trajectory fixtures without provider calls."
    )
    parser.add_argument("--selection", default=DEFAULT_SELECTION)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT)
    parser.add_argument("--source-partition", default="exploratory_instrument_calibration")
    parser.add_argument("--source-campaign-id")
    args = parser.parse_args()

    selection_path = (REPO_ROOT / args.selection).resolve()
    output_dir = (REPO_ROOT / args.output_dir).resolve()
    selection = _read_json(selection_path)
    selected = _list(selection.get("decisions"))
    if not selected or not all(isinstance(row, dict) for row in selected):
        raise SystemExit("Selection must contain a non-empty decisions array.")
    selection_sha256 = _sha256_file(selection_path)
    extraction_commit = _git_head()

    by_game: dict[str, list[dict[str, Any]]] = {}
    for row in selected:
        by_game.setdefault(str(row["saved_game"]), []).append(row)

    materials: list[dict[str, Any]] = []
    for saved_game, game_selection in by_game.items():
        saved_game_dir = REPO_ROOT / "saved_games" / saved_game
        _comparisons, _memory_rows, game_materials = _run_source(
            saved_game_dir,
            game_selection,
        )
        materials.extend(game_materials)

    order = {str(row["selection_id"]): index for index, row in enumerate(selected)}
    materials.sort(key=lambda row: order[str(_dict(row["selection"])["selection_id"])])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "selection.json").write_bytes(selection_path.read_bytes())

    fixture_rows: list[dict[str, Any]] = []
    for material in materials:
        fixture_rows.append(
            _write_fixture(
                material,
                output_dir=output_dir,
                source_partition=args.source_partition,
                source_campaign_id=args.source_campaign_id,
                selection_sha256=selection_sha256,
                extraction_commit=extraction_commit,
            )
        )

    manifest = {
        "schema_version": "trajectory_fixture_collection_manifest_v2",
        "status": "complete",
        "provider_calls": 0,
        "source_partition": args.source_partition,
        "source_campaign_id": args.source_campaign_id,
        "selection_path": _relative(selection_path),
        "selection_sha256": selection_sha256,
        "extraction_commit": extraction_commit,
        "fixture_count": len(fixture_rows),
        "fixtures": fixture_rows,
        "all_exact_history": all(row["integrity_status"] == "pass_exact_history" for row in fixture_rows),
        "collection_tree_sha256": _tree_hash(output_dir, exclude={"manifest.json"}),
        "tree_hash_excludes": ["manifest.json"],
        "script": _relative(Path(__file__).resolve()),
        "script_sha256": _sha256_file(Path(__file__).resolve()),
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Fixture extraction replays and copies source artifacts without any provider call.",
        },
    }
    _write_json(output_dir / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "fixture_count": len(fixture_rows),
                "all_exact_history": manifest["all_exact_history"],
                "provider_calls": 0,
            },
            sort_keys=True,
        )
    )
    return 0 if manifest["all_exact_history"] else 1


def _write_fixture(
    material: dict[str, Any],
    *,
    output_dir: Path,
    source_partition: str,
    source_campaign_id: str | None,
    selection_sha256: str,
    extraction_commit: str,
) -> dict[str, Any]:
    selection = _dict(material["selection"])
    comparison = _dict(material["comparison"])
    saved_game_dir = Path(material["saved_game_dir"])
    run_dir = Path(material["run_dir"])
    config = _dict(material["run_config"])
    player = _dict(material["player_entry"])
    artifacts = material["prompt_artifacts"]
    selection_id = str(selection["selection_id"])
    fixture_id = _safe_id(f"{source_partition}-{selection_id}")
    fixture_dir = output_dir / fixture_id
    if fixture_dir.exists() and any(fixture_dir.iterdir()):
        raise FileExistsError(
            f"{fixture_dir} already exists and is non-empty; use a new output directory for an immutable rebuild."
        )
    source_dir = fixture_dir / "source"
    reconstructed_dir = fixture_dir / "reconstructed"
    provenance_dir = fixture_dir / "provenance"
    for directory in (source_dir, reconstructed_dir, provenance_dir):
        directory.mkdir(parents=True, exist_ok=True)

    saved_manifest_path = saved_game_dir / "saved_game_manifest.json"
    saved_manifest = _read_json(saved_manifest_path)
    source_commit = str(saved_manifest.get("source_commit") or "")
    actions_path = run_dir / "actions.jsonl"
    events_path = run_dir / "events.jsonl"
    decisions_path = run_dir / "decisions.jsonl"
    run_config_path = run_dir / "run_config.json"
    immutable_source_paths = [
        saved_manifest_path,
        run_config_path,
        actions_path,
        events_path,
        decisions_path,
        artifacts.system_path,
        artifacts.user_path,
        artifacts.tools_path,
        artifacts.response_path,
        artifacts.parsed_path,
    ]
    before_hashes = {_relative(path): _sha256_file(path) for path in immutable_source_paths}

    actions = _read_jsonl(actions_path)
    events = _read_jsonl(events_path)
    decision_id = str(comparison["decision_id"])
    target_action_index = next(
        index for index, row in enumerate(actions) if str(row.get("decision_id")) == decision_id
    )
    request_event_index = next(
        index
        for index, event in enumerate(events)
        if event.get("type") == "LLM_DECISION_REQUESTED"
        and _dict(event.get("payload")).get("decision_id") == decision_id
    )
    action_prefix = actions[:target_action_index]
    event_prefix = events[: request_event_index + 1]

    run_ref = {
        "saved_game": saved_game_dir.name,
        "source_run_id": config.get("run_id"),
        "source_commit": source_commit,
        "saved_game_manifest": _relative(saved_manifest_path),
        "run_tree_sha256": _nested(saved_manifest, ("source_freeze", "run_tree_sha256")),
        "quality_check_tree_sha256": _nested(
            saved_manifest,
            ("source_freeze", "quality_check_tree_sha256"),
        ),
        "combined_tree_sha256": _nested(
            saved_manifest,
            ("source_freeze", "combined_tree_sha256"),
        ),
    }
    _write_json(source_dir / "run_ref.json", run_ref)
    _write_json(source_dir / "run_config.json", config)
    _write_json(source_dir / "decision.json", material["engine_decision"])
    _write_ordered_json(source_dir / "decision_ordered.json", material["engine_decision"])
    _write_json(source_dir / "decision_started.json", material["decision_started"])
    _write_json(source_dir / "target_action.json", material["source_action_entry"])
    _write_jsonl(source_dir / "action_prefix.jsonl", action_prefix)
    _write_jsonl(source_dir / "event_prefix.jsonl", event_prefix)
    (source_dir / "original_system.txt").write_bytes(material["original_system"])
    (source_dir / "original_user.json").write_bytes(material["original_user"])
    (source_dir / "original_tools.json").write_bytes(material["original_tools"])
    (source_dir / "original_response.json").write_bytes(artifacts.response_path.read_bytes())
    (source_dir / "original_parsed.json").write_bytes(artifacts.parsed_path.read_bytes())

    _write_json(reconstructed_dir / "engine_decision.json", material["engine_decision"])
    _write_ordered_json(
        reconstructed_dir / "engine_decision_ordered.json",
        material["engine_decision"],
    )
    _write_json(
        reconstructed_dir / "memory_snapshot.json",
        {
            "engine_replay": material["engine_replay_memory"],
            "recorded_event_reconstruction": material["recorded_event_memory"],
        },
    )
    _write_ordered_json(
        reconstructed_dir / "prompt_memory_ordered.json",
        material["engine_replay_memory"],
    )
    (reconstructed_dir / "regenerated_system.txt").write_bytes(material["replay_system"])
    (reconstructed_dir / "regenerated_user.json").write_bytes(material["replay_user"])
    (reconstructed_dir / "regenerated_tools.json").write_bytes(material["replay_tools"])
    _write_json(reconstructed_dir / "comparison.json", comparison)

    exact_history = bool(
        comparison.get("system_exact_replay")
        and comparison.get("user_exact_replay")
        and comparison.get("tools_exact_replay")
        and comparison.get("system_exact_recorded_event")
        and comparison.get("user_exact_recorded_event")
        and comparison.get("tools_exact_recorded_event")
    )
    fixture = {
        "schema_version": "trajectory_fixture_v2",
        "fixture_id": fixture_id,
        "source_campaign_id": source_campaign_id,
        "source_partition": source_partition,
        "source_saved_game": saved_game_dir.name,
        "source_run_id": config.get("run_id"),
        "source_turn_index": comparison.get("turn_index"),
        "source_decision_id": decision_id,
        "source_attempt_index": 0,
        "decision_type": comparison.get("decision_type"),
        "actor_player_id": comparison.get("player_id"),
        "source_model_id": player.get("openrouter_model_id"),
        "source_provider_constraint": player.get("provider"),
        "source_reasoning": player.get("reasoning"),
        "category": selection.get("category"),
        "stratum": selection.get("category"),
        "integrity_status": "pass_exact_history" if exact_history else "failed_exact_history",
        "state_replay_status": _nested(
            saved_manifest,
            ("deterministic_analysis", "state_replay_status"),
        ),
        "artifact_replay_status": _nested(
            saved_manifest,
            ("deterministic_analysis", "artifact_replay_status"),
        ),
        "prompt_mode": "exact_history",
        "ordered_prompt_inputs": {
            "decision": "source/decision_ordered.json",
            "memory": "reconstructed/prompt_memory_ordered.json",
            "note": (
                "These JSON objects preserve insertion order. The sorted JSON companions are "
                "for human inspection only and cannot be used for byte-exact prompt replay."
            ),
        },
        "source_commit": source_commit,
        "extraction_commit": extraction_commit,
        "selection_manifest_sha256": selection_sha256,
        "action_prefix_count": len(action_prefix),
        "event_prefix_count": len(event_prefix),
        "source_action_name": comparison.get("action_name"),
        "epistemic_note": (
            "The exact source prompt and immediate legal decision are preserved. "
            "This fixture does not identify long-run counterfactual value."
        ),
    }
    _write_json(fixture_dir / "fixture.json", fixture)

    after_hashes = {_relative(path): _sha256_file(path) for path in immutable_source_paths}
    if before_hashes != after_hashes:
        raise RuntimeError(f"Source artifact changed while extracting {fixture_id}.")
    _write_json(
        provenance_dir / "source_hashes.json",
        {
            "schema_version": "trajectory_fixture_source_hashes_v2",
            "hash_algorithm": "sha256",
            "source_files_unchanged": True,
            "files": [
                {"path": path, "sha256": digest}
                for path, digest in sorted(before_hashes.items())
            ],
        },
    )
    generated_hashes = _file_hashes(
        fixture_dir,
        exclude={
            "provenance/generated_hashes.json",
            "provenance/manifest.json",
        },
    )
    _write_json(
        provenance_dir / "generated_hashes.json",
        {
            "schema_version": "trajectory_fixture_generated_hashes_v2",
            "hash_algorithm": "sha256",
            "excludes": [
                "provenance/generated_hashes.json",
                "provenance/manifest.json",
            ],
            "files": generated_hashes,
        },
    )
    fixture_manifest = {
        "schema_version": "trajectory_fixture_manifest_v2",
        "fixture_id": fixture_id,
        "status": fixture["integrity_status"],
        "provider_calls": 0,
        "file_count_before_manifest": len(generated_hashes) + 1,
        "fixture_tree_sha256_before_manifest": _tree_hash(
            fixture_dir,
            exclude={"provenance/manifest.json"},
        ),
        "source_files_unchanged": True,
        "prompt_comparison": {
            "system_exact": comparison.get("system_exact_replay"),
            "user_exact": comparison.get("user_exact_replay"),
            "tools_exact": comparison.get("tools_exact_replay"),
            "recorded_event_system_exact": comparison.get("system_exact_recorded_event"),
            "recorded_event_user_exact": comparison.get("user_exact_recorded_event"),
            "recorded_event_tools_exact": comparison.get("tools_exact_recorded_event"),
            "ordered_inputs_persisted": True,
        },
    }
    _write_json(provenance_dir / "manifest.json", fixture_manifest)
    return {
        "fixture_id": fixture_id,
        "relative_path": fixture_id,
        "source_saved_game": saved_game_dir.name,
        "source_run_id": config.get("run_id"),
        "source_decision_id": decision_id,
        "category": selection.get("category"),
        "integrity_status": fixture["integrity_status"],
        "fixture_tree_sha256": _tree_hash(fixture_dir),
    }


def _file_hashes(root: Path, *, exclude: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in exclude:
            continue
        rows.append(
            {
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    return rows


def _tree_hash(root: Path, *, exclude: set[str] | None = None) -> str:
    excluded = exclude or set()
    stream = bytearray()
    for row in _file_hashes(root, exclude=excluded):
        stream.extend(str(row["relative_path"]).encode("utf-8"))
        stream.extend(b"\0")
        stream.extend(str(row["sha256"]).encode("ascii"))
        stream.extend(b"\n")
    return hashlib.sha256(bytes(stream)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_ordered_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    )


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _nested(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip(".-")


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
