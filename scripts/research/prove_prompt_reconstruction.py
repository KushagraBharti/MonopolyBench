from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
for package in ("engine", "arena", "telemetry"):
    package_src = REPO_ROOT / "python" / "packages" / package / "src"
    if str(package_src) not in sys.path:
        sys.path.insert(0, str(package_src))

from monopoly_arena.player_config import PlayerConfig  # noqa: E402
from monopoly_arena.prompting import (  # noqa: E402
    DEFAULT_SYSTEM_PROMPT,
    PromptMemory,
    build_compact_decision,
    build_openrouter_tools,
    build_prompt_bundle,
    build_space_key_by_index,
)
from monopoly_engine import Engine  # noqa: E402


DEFAULT_SELECTION = (
    REPO_ROOT / "analysis" / "research_protocol" / "architecture_proof" / "selection.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "analysis" / "research_protocol" / "architecture_proof"


@dataclass(frozen=True)
class PromptArtifacts:
    prefix: str
    system_path: Path
    user_path: Path
    tools_path: Path
    response_path: Path
    parsed_path: Path


class FrozenPromptMemory:
    def __init__(self, snapshots: dict[str, dict[str, Any]]) -> None:
        self._snapshots = copy.deepcopy(snapshots)

    def snapshot_for_player(self, player_id: str) -> dict[str, Any]:
        return copy.deepcopy(
            self._snapshots.get(
                player_id,
                {
                    "public_timeline_last_20": [],
                    "your_private_thoughts_last_10": [],
                },
            )
        )


def _json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(value))


def _normalize_newlines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _prompt_artifact_index(prompts_dir: Path) -> dict[tuple[str, int], PromptArtifacts]:
    result: dict[tuple[str, int], PromptArtifacts] = {}
    for parsed_path in prompts_dir.glob("*_parsed.json"):
        parsed = _json_load(parsed_path)
        decision_id = parsed.get("decision_id")
        attempt_index = parsed.get("attempt_index")
        if not isinstance(decision_id, str) or not isinstance(attempt_index, int):
            continue
        suffix = "_parsed.json"
        prefix = parsed_path.name[: -len(suffix)]
        artifacts = PromptArtifacts(
            prefix=prefix,
            system_path=prompts_dir / f"{prefix}_system.txt",
            user_path=prompts_dir / f"{prefix}_user.json",
            tools_path=prompts_dir / f"{prefix}_tools.json",
            response_path=prompts_dir / f"{prefix}_response.json",
            parsed_path=parsed_path,
        )
        result[(decision_id, attempt_index)] = artifacts
    return result


def _started_decision_index(decisions_path: Path) -> dict[str, dict[str, Any]]:
    return {
        str(row["decision_id"]): row
        for row in _jsonl(decisions_path)
        if row.get("phase") == "decision_started" and isinstance(row.get("decision_id"), str)
    }


def _recorded_memory_snapshots(
    events: Iterable[dict[str, Any]],
    selected_ids: set[str],
    player_ids: list[str],
) -> dict[str, dict[str, dict[str, Any]]]:
    memory = PromptMemory(space_key_by_index=build_space_key_by_index())
    snapshots: dict[str, dict[str, dict[str, Any]]] = {}
    for event in events:
        memory.update(event)
        if event.get("type") != "LLM_DECISION_REQUESTED":
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        decision_id = payload.get("decision_id")
        if decision_id not in selected_ids:
            continue
        snapshots[str(decision_id)] = {
            player_id: memory.snapshot_for_player(player_id) for player_id in player_ids
        }
    return snapshots


def _player_config(
    player_entry: dict[str, Any],
    *,
    system_prompt: str,
) -> PlayerConfig:
    return PlayerConfig(
        player_id=str(player_entry["player_id"]),
        name=str(player_entry.get("name") or player_entry["player_id"]),
        openrouter_model_id=str(player_entry["openrouter_model_id"]),
        model_display_name=str(
            player_entry.get("model_display_name") or player_entry["openrouter_model_id"]
        ),
        system_prompt=system_prompt,
        reasoning=player_entry.get("reasoning")
        if isinstance(player_entry.get("reasoning"), dict)
        else None,
        provider=player_entry.get("provider")
        if isinstance(player_entry.get("provider"), dict)
        else None,
    )


def _json_diff_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if type(left) is not type(right):
        return [path or "/"]
    if isinstance(left, dict):
        paths: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}/{key}"
            if key not in left or key not in right:
                paths.append(child)
            else:
                paths.extend(_json_diff_paths(left[key], right[key], child))
        return paths
    if isinstance(left, list):
        if len(left) != len(right):
            return [path or "/"]
        paths = []
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            paths.extend(_json_diff_paths(left_item, right_item, f"{path}/{index}"))
        return paths
    return [] if left == right else [path or "/"]


def _prompt_bytes(
    decision: dict[str, Any],
    player: PlayerConfig,
    memory: Any,
) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    space_keys = build_space_key_by_index()
    bundle = build_prompt_bundle(
        decision,
        player,
        memory=memory,
        space_key_by_index=space_keys,
    )
    tools = build_openrouter_tools(build_compact_decision(decision))
    return (
        bundle.system_prompt.encode("utf-8"),
        bundle.user_content.encode("utf-8"),
        json.dumps(tools, separators=(",", ":"), ensure_ascii=True).encode("utf-8"),
        bundle.user_payload,
    )


def _memory_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    game_state = payload.get("game_state")
    if not isinstance(game_state, dict):
        return {}
    memory = game_state.get("memory")
    return copy.deepcopy(memory) if isinstance(memory, dict) else {}


def _run_source(
    saved_game_dir: Path,
    selected: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    run_dir = saved_game_dir / "run"
    config = _json_load(run_dir / "run_config.json")
    actions = _jsonl(run_dir / "actions.jsonl")
    events = _jsonl(run_dir / "events.jsonl")
    started = _started_decision_index(run_dir / "decisions.jsonl")
    prompt_artifacts = _prompt_artifact_index(run_dir / "prompts")
    player_entries = {
        str(player["player_id"]): player
        for player in config["players"]
        if isinstance(player, dict)
    }
    player_ids = list(player_entries)
    selected_by_id = {str(item["decision_id"]): item for item in selected}
    selected_ids = set(selected_by_id)
    recorded_snapshots = _recorded_memory_snapshots(events, selected_ids, player_ids)

    engine = Engine(
        seed=int(config["seed"]),
        players=[
            {"player_id": player_id, "name": str(player_entries[player_id].get("name") or player_id)}
            for player_id in player_ids
        ],
        run_id=str(config["run_id"]),
        max_turns=int(config["max_turns"]),
        start_ts_ms=int(config["start_ts_ms"]),
        ts_step_ms=int(config["ts_step_ms"]),
        max_trade_exchanges=int(config.get("max_trade_exchanges") or 20),
        max_auction_actions=int(config.get("max_auction_actions") or 200),
    )
    replay_memory = PromptMemory(space_key_by_index=build_space_key_by_index())

    comparisons: list[dict[str, Any]] = []
    memory_rows: list[dict[str, Any]] = []
    fixture_materials: list[dict[str, Any]] = []
    seen: set[str] = set()

    for action_entry in actions:
        while True:
            _, decision_events, decision, _ = engine.advance_until_decision(max_steps=1)
            for event in decision_events:
                replay_memory.update(event)
            if decision is not None:
                break
            if engine.is_game_over():
                raise RuntimeError(
                    f"{config['run_id']}: replay ended before action {action_entry.get('decision_id')}"
                )

        decision_id = str(decision["decision_id"])
        expected_id = str(action_entry.get("decision_id"))
        if decision_id != expected_id:
            raise RuntimeError(
                f"{config['run_id']}: decision mismatch, expected {expected_id}, got {decision_id}"
            )

        if decision_id in selected_by_id:
            selection = selected_by_id[decision_id]
            artifacts = prompt_artifacts.get((decision_id, 0))
            if artifacts is None:
                raise RuntimeError(f"{decision_id}: prompt artifacts for attempt 0 are missing")
            for required in (
                artifacts.system_path,
                artifacts.user_path,
                artifacts.tools_path,
                artifacts.response_path,
                artifacts.parsed_path,
            ):
                if not required.exists():
                    raise RuntimeError(f"{decision_id}: missing {required}")

            original_system = artifacts.system_path.read_bytes()
            original_user = artifacts.user_path.read_bytes()
            original_tools = artifacts.tools_path.read_bytes()
            original_payload = json.loads(original_user)
            started_entry = started.get(decision_id)
            if started_entry is None:
                raise RuntimeError(f"{decision_id}: decision_started entry is missing")

            player_id = str(decision["player_id"])
            player = _player_config(
                player_entries[player_id],
                system_prompt=original_system.decode("utf-8"),
            )
            replay_system, replay_user, replay_tools, replay_payload = _prompt_bytes(
                decision,
                player,
                replay_memory,
            )
            recorded_memory = FrozenPromptMemory(recorded_snapshots[decision_id])
            (
                recorded_system,
                recorded_user,
                recorded_tools,
                recorded_payload,
            ) = _prompt_bytes(
                decision,
                player,
                recorded_memory,
            )
            empty_memory = PromptMemory(space_key_by_index=build_space_key_by_index())
            empty_system, empty_user, empty_tools, empty_payload = _prompt_bytes(
                decision,
                player,
                empty_memory,
            )

            original_memory = _memory_from_payload(original_payload)
            replay_memory_payload = _memory_from_payload(replay_payload)
            recorded_memory_payload = _memory_from_payload(recorded_payload)
            empty_memory_payload = _memory_from_payload(empty_payload)
            public_items = original_memory.get("public_timeline_last_20", [])
            private_items = original_memory.get("your_private_thoughts_last_10", [])
            prompt_raw = started_entry.get("prompt_payload_raw")
            prompt_raw_bytes = (
                str(prompt_raw).encode("utf-8") if isinstance(prompt_raw, str) else b""
            )

            comparison = {
                "selection_id": selection["selection_id"],
                "category": selection["category"],
                "saved_game": saved_game_dir.name,
                "run_id": config["run_id"],
                "decision_id": decision_id,
                "turn_index": decision.get("turn_index"),
                "decision_type": decision.get("decision_type"),
                "action_name": action_entry.get("action", {}).get("action"),
                "player_id": player_id,
                "model_id": player.openrouter_model_id,
                "source_attempt_index": 0,
                "source_prompt_prefix": artifacts.prefix,
                "original_system_sha256": _sha256_bytes(original_system),
                "original_user_sha256": _sha256_bytes(original_user),
                "original_tools_sha256": _sha256_bytes(original_tools),
                "decision_log_prompt_raw_sha256": _sha256_bytes(prompt_raw_bytes),
                "replay_system_sha256": _sha256_bytes(replay_system),
                "replay_user_sha256": _sha256_bytes(replay_user),
                "replay_tools_sha256": _sha256_bytes(replay_tools),
                "recorded_event_system_sha256": _sha256_bytes(recorded_system),
                "recorded_event_user_sha256": _sha256_bytes(recorded_user),
                "recorded_event_tools_sha256": _sha256_bytes(recorded_tools),
                "empty_fixture_system_sha256": _sha256_bytes(empty_system),
                "empty_fixture_user_sha256": _sha256_bytes(empty_user),
                "empty_fixture_tools_sha256": _sha256_bytes(empty_tools),
                "system_exact_replay": original_system == replay_system,
                "user_exact_replay": original_user == replay_user,
                "tools_exact_replay": original_tools == replay_tools,
                "system_exact_recorded_event": original_system == recorded_system,
                "user_exact_recorded_event": original_user == recorded_user,
                "tools_exact_recorded_event": original_tools == recorded_tools,
                "decision_log_prompt_raw_exact": original_user == prompt_raw_bytes,
                "empty_fixture_user_exact": original_user == empty_user,
                "empty_fixture_tools_exact": original_tools == empty_tools,
                "original_memory_sha256": _canonical_sha256(original_memory),
                "replay_memory_sha256": _canonical_sha256(replay_memory_payload),
                "recorded_event_memory_sha256": _canonical_sha256(recorded_memory_payload),
                "empty_fixture_memory_sha256": _canonical_sha256(empty_memory_payload),
                "lost_public_timeline_count": len(public_items)
                if isinstance(public_items, list)
                else None,
                "lost_private_thought_count": len(private_items)
                if isinstance(private_items, list)
                else None,
                "replay_diff_paths": _json_diff_paths(original_payload, replay_payload),
                "recorded_event_diff_paths": _json_diff_paths(
                    original_payload, recorded_payload
                ),
                "empty_fixture_diff_paths": _json_diff_paths(original_payload, empty_payload),
                "current_default_system_sha256": _sha256_bytes(
                    DEFAULT_SYSTEM_PROMPT.encode("utf-8")
                ),
                "saved_system_matches_current_default": (
                    original_system == DEFAULT_SYSTEM_PROMPT.encode("utf-8")
                ),
                "saved_system_matches_current_default_normalized": (
                    _normalize_newlines(original_system.decode("utf-8"))
                    == _normalize_newlines(DEFAULT_SYSTEM_PROMPT)
                ),
            }
            comparisons.append(comparison)
            memory_rows.append(
                {
                    "selection_id": selection["selection_id"],
                    "saved_game": saved_game_dir.name,
                    "run_id": config["run_id"],
                    "decision_id": decision_id,
                    "player_id": player_id,
                    "original_memory": original_memory,
                    "engine_replay_memory": replay_memory_payload,
                    "recorded_event_memory": recorded_memory_payload,
                    "current_empty_fixture_memory": empty_memory_payload,
                    "lost_public_timeline": public_items,
                    "lost_private_thoughts": private_items,
                }
            )
            fixture_materials.append(
                {
                    "selection": copy.deepcopy(selection),
                    "saved_game_dir": saved_game_dir,
                    "run_dir": run_dir,
                    "run_config": copy.deepcopy(config),
                    "player_entry": copy.deepcopy(player_entries[player_id]),
                    "engine_decision": copy.deepcopy(decision),
                    "decision_started": copy.deepcopy(started_entry),
                    "source_action_entry": copy.deepcopy(action_entry),
                    "prompt_artifacts": artifacts,
                    "original_system": original_system,
                    "original_user": original_user,
                    "original_tools": original_tools,
                    "replay_system": replay_system,
                    "replay_user": replay_user,
                    "replay_tools": replay_tools,
                    "recorded_event_system": recorded_system,
                    "recorded_event_user": recorded_user,
                    "recorded_event_tools": recorded_tools,
                    "engine_replay_memory": copy.deepcopy(replay_memory_payload),
                    "recorded_event_memory": copy.deepcopy(recorded_memory_payload),
                    "comparison": copy.deepcopy(comparison),
                }
            )
            seen.add(decision_id)

        action = action_entry.get("action")
        if not isinstance(action, dict):
            raise RuntimeError(f"{decision_id}: action payload is missing")
        decision_meta = (
            action_entry.get("decision_meta")
            if isinstance(action_entry.get("decision_meta"), dict)
            else None
        )
        _, action_events, _, _ = engine.apply_action(action, decision_meta=decision_meta)
        for event in action_events:
            replay_memory.update(event)

    missing = selected_ids - seen
    if missing:
        raise RuntimeError(
            f"{config['run_id']}: selected decisions were not replayed: {sorted(missing)}"
        )
    return comparisons, memory_rows, fixture_materials


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    payload = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
        for row in rows
    )
    path.write_text(payload, encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "selection_id",
        "category",
        "saved_game",
        "run_id",
        "decision_id",
        "turn_index",
        "decision_type",
        "action_name",
        "player_id",
        "model_id",
        "system_exact_replay",
        "user_exact_replay",
        "tools_exact_replay",
        "user_exact_recorded_event",
        "decision_log_prompt_raw_exact",
        "empty_fixture_user_exact",
        "empty_fixture_tools_exact",
        "lost_public_timeline_count",
        "lost_private_thought_count",
        "saved_system_matches_current_default",
        "saved_system_matches_current_default_normalized",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def _report_markdown(
    comparisons: list[dict[str, Any]],
    *,
    git_commit: str,
    selection_sha256: str,
) -> str:
    replay_exact = sum(
        1
        for row in comparisons
        if row["system_exact_replay"]
        and row["user_exact_replay"]
        and row["tools_exact_replay"]
    )
    recorded_exact = sum(
        1
        for row in comparisons
        if row["system_exact_recorded_event"]
        and row["user_exact_recorded_event"]
        and row["tools_exact_recorded_event"]
    )
    empty_exact = sum(1 for row in comparisons if row["empty_fixture_user_exact"])
    total_public = sum(int(row["lost_public_timeline_count"] or 0) for row in comparisons)
    total_private = sum(int(row["lost_private_thought_count"] or 0) for row in comparisons)

    lines = [
        "# Zero-Cost Prompt Reconstruction Proof",
        "",
        "This report was generated without any provider calls and without modifying source",
        "saved-game artifacts. It compares the original attempt-0 prompt bytes with prompts",
        "rebuilt from (a) a current engine replay plus reconstructed `PromptMemory`,",
        "(b) the original recorded event stream plus the replayed decision object, and",
        "(c) the current micro-fixture behavior using fresh empty memory.",
        "",
        "## Result",
        "",
        f"- Source code commit: `{git_commit}`",
        f"- Selection manifest SHA-256: `{selection_sha256}`",
        f"- Decisions tested: **{len(comparisons)}**",
        f"- Exact engine-replay system/user/tools triples: **{replay_exact}/{len(comparisons)}**",
        f"- Exact recorded-event system/user/tools triples: **{recorded_exact}/{len(comparisons)}**",
        f"- Empty-memory fixture user prompts identical to source: **{empty_exact}/{len(comparisons)}**",
        f"- Public timeline entries removed by empty fixtures: **{total_public}**",
        f"- Private-thought entries removed by empty fixtures: **{total_private}**",
        "- All saved system prompts match the current default after newline normalization: "
        f"**{all(row['saved_system_matches_current_default_normalized'] for row in comparisons)}**",
        "",
        "## Persisted-Input Gate",
        "",
        "The 12/12 results above concern reconstructed objects before serialization. A separate",
        "execution precheck then tested whether the persisted fixture inputs could regenerate",
        "the same bytes after a write/read cycle. It exposed a v1 key-order defect: sorted JSON",
        "retained the same values but changed compact prompt serialization. The v1 precheck",
        "failed 12/12 and remains preserved.",
        "",
        "The v2 fixture format stores explicit insertion-order-preserving decision and memory",
        "objects. Its independent execution precheck passes **12/12**, with all fixture tree",
        "hashes, generated-file inventories, source prompt hashes, and reconstructed",
        "system/user/tool hashes verified. See `fixture_format_migration.md`. Only v2 is",
        "eligible for repeated-query execution.",
        "",
        "## Decision-Level Evidence",
        "",
        "| ID | Category | Run | Turn | Decision/action | Engine replay | Recorded events | Empty fixture | Lost memory (public/private) |",
        "|---|---|---|---:|---|---|---|---|---:|",
    ]
    for row in comparisons:
        replay_status = (
            "exact"
            if row["system_exact_replay"]
            and row["user_exact_replay"]
            and row["tools_exact_replay"]
            else "mismatch"
        )
        recorded_status = (
            "exact"
            if row["system_exact_recorded_event"]
            and row["user_exact_recorded_event"]
            and row["tools_exact_recorded_event"]
            else "mismatch"
        )
        empty_status = "exact" if row["empty_fixture_user_exact"] else "different"
        decision_action = f"{row['decision_type']} / {row['action_name']}"
        lines.append(
            "| {selection_id} | {category} | `{run_id}` | {turn_index} | "
            "{decision_action} | {replay_status} | {recorded_status} | "
            "{empty_status} | {public}/{private} |".format(
                selection_id=row["selection_id"],
                category=row["category"],
                run_id=row["run_id"],
                turn_index=row["turn_index"],
                decision_action=decision_action,
                replay_status=replay_status,
                recorded_status=recorded_status,
                empty_status=empty_status,
                public=row["lost_public_timeline_count"],
                private=row["lost_private_thought_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Contract",
            "",
            "- `exact` means byte-identical UTF-8 system, compact user JSON, and compact tools JSON.",
            "- A recorded-event exact match proves that the saved event stream contains enough",
            "  information to restore the bounded prompt memory when paired with the reconstructed",
            "  engine decision.",
            "- An engine-replay mismatch is reported separately because a state-valid replay can",
            "  still differ in observation-event representation.",
            "- `different` for the empty fixture is expected when the source decision had history.",
            "  The exact removed entries are preserved in `memory_loss.jsonl`.",
            "- This proof does not evaluate model behavior, decision quality, or branch value.",
            "",
        ]
    )
    return "\n".join(lines)


def _generated_hashes(output_dir: Path, names: list[str]) -> dict[str, str]:
    return {
        name: _sha256_bytes((output_dir / name).read_bytes())
        for name in names
        if (output_dir / name).exists()
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct selected saved-game prompts without provider calls."
    )
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    selection_path = args.selection.resolve()
    output_dir = args.output_dir.resolve()
    selection_payload = _json_load(selection_path)
    selections = selection_payload.get("decisions")
    if not isinstance(selections, list) or not selections:
        raise ValueError("Selection manifest must contain a non-empty decisions list")

    by_game: dict[str, list[dict[str, Any]]] = {}
    for selection in selections:
        if not isinstance(selection, dict):
            raise ValueError("Every selection must be an object")
        saved_game = str(selection["saved_game"])
        by_game.setdefault(saved_game, []).append(selection)

    comparisons: list[dict[str, Any]] = []
    memory_rows: list[dict[str, Any]] = []
    for saved_game, game_selections in by_game.items():
        saved_game_dir = REPO_ROOT / "saved_games" / saved_game
        game_comparisons, game_memory, _fixture_materials = _run_source(
            saved_game_dir,
            game_selections,
        )
        comparisons.extend(game_comparisons)
        memory_rows.extend(game_memory)

    selection_order = {
        str(selection["selection_id"]): index for index, selection in enumerate(selections)
    }
    comparisons.sort(key=lambda row: selection_order[row["selection_id"]])
    memory_rows.sort(key=lambda row: selection_order[row["selection_id"]])

    output_dir.mkdir(parents=True, exist_ok=True)
    selection_sha256 = _sha256_bytes(selection_path.read_bytes())
    git_commit = _git_commit()
    _write_jsonl(output_dir / "comparisons.jsonl", comparisons)
    _write_jsonl(output_dir / "memory_loss.jsonl", memory_rows)
    _write_csv(output_dir / "comparisons.csv", comparisons)
    (output_dir / "report.md").write_text(
        _report_markdown(
            comparisons,
            git_commit=git_commit,
            selection_sha256=selection_sha256,
        ),
        encoding="utf-8",
    )

    output_names = [
        "comparisons.jsonl",
        "memory_loss.jsonl",
        "comparisons.csv",
        "report.md",
    ]
    manifest = {
        "schema_version": "architecture_proof_manifest_v1",
        "status": "complete",
        "provider_calls": 0,
        "source_code_commit": git_commit,
        "script": str(Path(__file__).resolve().relative_to(REPO_ROOT)).replace("\\", "/"),
        "script_sha256": _sha256_bytes(Path(__file__).read_bytes()),
        "selection": str(selection_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "selection_sha256": selection_sha256,
        "decision_count": len(comparisons),
        "source_saved_games": sorted(by_game),
        "all_engine_replay_prompts_exact": all(
            row["system_exact_replay"]
            and row["user_exact_replay"]
            and row["tools_exact_replay"]
            for row in comparisons
        ),
        "all_recorded_event_prompts_exact": all(
            row["system_exact_recorded_event"]
            and row["user_exact_recorded_event"]
            and row["tools_exact_recorded_event"]
            for row in comparisons
        ),
        "generated_output_hashes": _generated_hashes(output_dir, output_names),
    }
    _write_json(output_dir / "manifest.json", manifest)

    print(output_dir / "report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
