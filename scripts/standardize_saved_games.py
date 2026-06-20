from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator


REPO_ROOT = Path(__file__).resolve().parents[1]
SAVED_ROOT = REPO_ROOT / "saved_games"
GLOBAL_ARCHIVE_ROOT = SAVED_ROOT / "archive"
BOARD_PATH = REPO_ROOT / "contracts" / "data" / "board.json"

DEFAULT_SAVED_GAMES = [
    "frontier-191-mock-83265-81ed4937-openai-gpt-5-5",
    "frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview",
]

EXPECTED_RUN_TOP_LEVEL = [
    "actions.jsonl",
    "artifact_manifest.json",
    "asset_flow.jsonl",
    "auction_threads.jsonl",
    "behavioral_flags.jsonl",
    "cash_flow.jsonl",
    "cost_report.json",
    "decision_index.json",
    "decisions.jsonl",
    "event_hashes.json",
    "events.jsonl",
    "experiment_manifest.json",
    "failure_findings.jsonl",
    "failure_summary.json",
    "negotiation_threads.jsonl",
    "player_timelines.json",
    "players.json",
    "pricing_snapshot.json",
    "prompts",
    "replay_diff.json",
    "replay_flags.jsonl",
    "replay_navigation.json",
    "replay_report.json",
    "replay_steps.jsonl",
    "review_cost_aggregate.json",
    "review_cost_calls.jsonl",
    "review_queue.jsonl",
    "run_config.json",
    "scorecard_decisions.jsonl",
    "scorecard_events.jsonl",
    "scorecard_players.json",
    "scorecard.json",
    "seat_assignment.json",
    "state",
    "summary.json",
    "timeline.json",
    "trace_findings.jsonl",
    "trace_summary.json",
    "turn_index.json",
    "usage_attempts.jsonl",
    "usage_decisions.jsonl",
    "usage.json",
]

STANDARD_ANALYSIS_DIR_NAME = "analysis"

ROOT_PRESERVE_NAMES = {
    "run",
    "quality_check",
    STANDARD_ANALYSIS_DIR_NAME,
    "saved_game_manifest.json",
}

HOUSE_COST_BY_GROUP = {
    "BROWN": 50,
    "LIGHT_BLUE": 50,
    "PINK": 100,
    "ORANGE": 100,
    "RED": 150,
    "YELLOW": 150,
    "GREEN": 200,
    "DARK_BLUE": 200,
}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def stringify(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def flatten(row: dict[str, Any]) -> dict[str, Any]:
    return {key: stringify(value) for key, value in row.items()}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        seen: set[str] = set()
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{key: stringify(value) for key, value in row.items()} for row in rows])


def safe_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def safe_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def ensure_inside(child: Path, parent: Path) -> None:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    if child_resolved != parent_resolved and parent_resolved not in child_resolved.parents:
        raise RuntimeError(f"Refusing to operate outside {parent_resolved}: {child_resolved}")


def next_available(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = path.with_name(f"{stem}_v{index:03d}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find available archive path for {path}")


def move_preserving(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if destination.exists():
        raise RuntimeError(f"Refusing to overwrite existing path: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def global_archive_dir(saved_dir: Path) -> Path:
    return GLOBAL_ARCHIVE_ROOT / saved_dir.name


def archive_existing_zip(saved_dir: Path, archive_dir: Path, folder_name: str, standard_dir: Path) -> None:
    root_zip = saved_dir / f"{folder_name}-analysis.zip"
    if not root_zip.exists() or standard_dir.exists():
        return
    legacy_zip = next_available(archive_dir / "zips" / f"{folder_name}-legacy-analysis.zip")
    move_preserving(root_zip, legacy_zip)


def standardize_layout(saved_dir: Path) -> dict[str, Any]:
    folder_name = saved_dir.name
    run_dir = saved_dir / "run"
    quality_dir = saved_dir / "quality_check"
    archive_dir = global_archive_dir(saved_dir)
    standard_dir = saved_dir / STANDARD_ANALYSIS_DIR_NAME
    legacy_standard_dir = saved_dir / f"{folder_name}-analysis"
    local_archives_dir = saved_dir / "archives"
    legacy_run_analysis_dir = run_dir / "analysis"

    ensure_inside(saved_dir, SAVED_ROOT)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_existing_zip(saved_dir, archive_dir, folder_name, standard_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    preserved = set(ROOT_PRESERVE_NAMES)
    preserved.add(f"{folder_name}-analysis.zip")

    if legacy_standard_dir.exists() and not standard_dir.exists():
        move_preserving(legacy_standard_dir, standard_dir)
    elif legacy_standard_dir.exists() and standard_dir.exists():
        move_preserving(legacy_standard_dir, next_available(archive_dir / "analysis_dirs" / "legacy-standard-analysis"))

    if legacy_run_analysis_dir.exists():
        move_preserving(legacy_run_analysis_dir, next_available(archive_dir / "analysis_dirs" / "legacy-run-analysis"))

    if local_archives_dir.exists():
        move_preserving(local_archives_dir, next_available(archive_dir / "previous-local-archives"))

    moved: list[dict[str, str]] = []
    for child in sorted(saved_dir.iterdir(), key=lambda item: item.name.lower()):
        if child.name in preserved:
            continue
        destination = run_dir / child.name
        if child.suffix.lower() == ".zip":
            destination = next_available(archive_dir / "zips" / child.name)
        if child == run_dir or child == quality_dir or child == standard_dir:
            continue
        move_preserving(child, destination)
        moved.append({"from": str(child.relative_to(saved_dir)), "to": str(destination.relative_to(saved_dir))})

    return {
        "saved_game": folder_name,
        "run_dir": str(run_dir.relative_to(saved_dir)),
        "quality_check_dir": str(quality_dir.relative_to(saved_dir)) if quality_dir.exists() else None,
        "archive_dir": str(archive_dir.relative_to(SAVED_ROOT)),
        "standard_analysis_dir": STANDARD_ANALYSIS_DIR_NAME,
        "moved_items": moved,
    }


def snapshot_sort_key(path: Path) -> tuple[int, int]:
    match = re.search(r"turn_(\d{4})(?:_decision_(\d{4}))?\.json$", path.name)
    if not match:
        return (10**9, 10**9)
    turn = int(match.group(1))
    decision = int(match.group(2) or 0)
    return (turn, decision)


def canonical_state_files(state_dir: Path) -> list[Path]:
    if not state_dir.exists():
        return []
    return sorted(
        [path for path in state_dir.glob("turn_*.json") if "_decision_" not in path.name],
        key=snapshot_sort_key,
    )


def board_asset_values(snapshot: dict[str, Any], player_ids: list[str]) -> dict[str, dict[str, int]]:
    values = {
        player_id: {
            "property_value": 0,
            "building_value": 0,
            "mortgage_liability": 0,
            "property_count": 0,
            "mortgaged_count": 0,
            "houses": 0,
            "hotels": 0,
        }
        for player_id in player_ids
    }
    for space in snapshot.get("board", []):
        owner = space.get("owner_id")
        if owner not in values:
            continue
        price = safe_int(space.get("price"))
        group = space.get("group")
        houses = safe_int(space.get("houses"))
        hotel = bool(space.get("hotel"))
        house_cost = HOUSE_COST_BY_GROUP.get(str(group), 0)
        values[owner]["property_value"] += price
        values[owner]["building_value"] += houses * house_cost + (5 * house_cost if hotel else 0)
        values[owner]["property_count"] += 1
        values[owner]["houses"] += houses
        values[owner]["hotels"] += 1 if hotel else 0
        if space.get("mortgaged"):
            values[owner]["mortgage_liability"] += price // 2
            values[owner]["mortgaged_count"] += 1
    return values


def load_players(run_dir: Path, summary: dict[str, Any]) -> list[dict[str, Any]]:
    players_doc = read_json(run_dir / "players.json", {"players": []})
    players = players_doc.get("players") or []
    if players:
        return players
    return [
        {"player_id": player_id, "name": data.get("name", player_id)}
        for player_id, data in (summary.get("players") or {}).items()
    ]


def normalize_usage(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        normalized.append(
            {
                "call_index": index,
                "run_id": row.get("run_id"),
                "decision_id": row.get("decision_id"),
                "attempt_index": safe_int(row.get("attempt_index")),
                "turn_index": safe_int(row.get("turn_index")),
                "decision_type": row.get("decision_type") or "",
                "player_id": row.get("player_id") or "",
                "openrouter_model_id": row.get("openrouter_model_id") or "",
                "model_display_name": row.get("model_display_name") or "",
                "finish_reason": row.get("finish_reason") or "",
                "accounting_status": row.get("accounting_status") or "",
                "input_tokens": safe_int(row.get("input_tokens") or row.get("prompt_tokens")),
                "output_tokens": safe_int(row.get("output_tokens") or row.get("completion_tokens")),
                "reasoning_tokens": safe_int(row.get("reasoning_tokens")),
                "total_tokens": safe_int(row.get("total_tokens")),
                "cached_tokens": safe_int(row.get("cached_tokens") or row.get("cache_read_tokens")),
                "cost": safe_float(row.get("cost")),
                "latency_ms": safe_int(row.get("latency_ms")),
                "retry_used": bool(row.get("retry_used")),
                "fallback_used": bool(row.get("fallback_used")),
                "fallback_reason": row.get("fallback_reason") or "",
                "error_type": row.get("error_type") or "",
                "openrouter_status_code": row.get("openrouter_status_code") or "",
                "generation_id": row.get("generation_id") or row.get("openrouter_request_id") or "",
            }
        )
    return normalized


def extract_decision_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        selected = row.get("selected_action") or row.get("action") or {}
        if not isinstance(selected, dict):
            selected = {}
        output.append(
            {
                "decision_row_index": index,
                "phase": row.get("phase") or "",
                "turn_index": row.get("turn_index"),
                "decision_id": row.get("decision_id") or "",
                "decision_type": row.get("decision_type") or "",
                "player_id": row.get("player_id") or "",
                "attempts": len(row.get("attempts") or []),
                "retry_count": max(0, len(row.get("attempts") or []) - 1),
                "fallback_used": bool(row.get("fallback_used")),
                "validation_errors": stringify(row.get("validation_errors") or []),
                "selected_action_type": selected.get("action_type") or selected.get("type") or selected.get("name") or "",
                "selected_action": stringify(selected),
                "latency_ms": row.get("latency_ms") or "",
            }
        )
    return output


def extract_event_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        event_type = row.get("event_type") or row.get("type") or row.get("kind") or ""
        output.append(
            {
                "seq": row.get("seq"),
                "turn_index": row.get("turn_index"),
                "event_type": event_type,
                "player_id": row.get("player_id") or row.get("active_player_id") or "",
                "payload": stringify(row.get("payload") or row),
            }
        )
    return output


def state_tables(run_dir: Path, players: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    player_ids = [player.get("player_id") or player.get("name") for player in players]
    player_ids = [player_id for player_id in player_ids if player_id]
    state_rows: list[dict[str, Any]] = []
    holding_rows: list[dict[str, Any]] = []
    bank_rows: list[dict[str, Any]] = []
    for path in canonical_state_files(run_dir / "state"):
        snapshot = read_json(path, {})
        if not snapshot:
            continue
        turn_index = safe_int(snapshot.get("turn_index"))
        asset_values = board_asset_values(snapshot, player_ids)
        bank = snapshot.get("bank") or {}
        bank_rows.append(
            {
                "turn_index": turn_index,
                "phase": snapshot.get("phase") or "",
                "active_player_id": snapshot.get("active_player_id") or "",
                "houses_remaining": safe_int(bank.get("houses_remaining")),
                "hotels_remaining": safe_int(bank.get("hotels_remaining")),
                "snapshot_file": path.name,
            }
        )
        for player in snapshot.get("players", []):
            player_id = player.get("player_id")
            values = asset_values.get(player_id, {})
            cash = safe_int(player.get("cash"))
            net_worth = cash + safe_int(values.get("property_value")) + safe_int(values.get("building_value")) - safe_int(
                values.get("mortgage_liability")
            )
            state_rows.append(
                {
                    "turn_index": turn_index,
                    "phase": snapshot.get("phase") or "",
                    "active_player_id": snapshot.get("active_player_id") or "",
                    "player_id": player_id,
                    "cash": cash,
                    "net_worth_estimate": net_worth,
                    "position": safe_int(player.get("position")),
                    "in_jail": bool(player.get("in_jail")),
                    "jail_turns": safe_int(player.get("jail_turns")),
                    "doubles_count": safe_int(player.get("doubles_count")),
                    "bankrupt": bool(player.get("bankrupt")),
                    "property_value": safe_int(values.get("property_value")),
                    "building_value": safe_int(values.get("building_value")),
                    "mortgage_liability": safe_int(values.get("mortgage_liability")),
                    "property_count": safe_int(values.get("property_count")),
                    "mortgaged_count": safe_int(values.get("mortgaged_count")),
                    "houses": safe_int(values.get("houses")),
                    "hotels": safe_int(values.get("hotels")),
                    "snapshot_file": path.name,
                }
            )
        for space in snapshot.get("board", []):
            if not space.get("owner_id"):
                continue
            holding_rows.append(
                {
                    "turn_index": turn_index,
                    "space_index": safe_int(space.get("index")),
                    "space_name": space.get("name") or "",
                    "space_kind": space.get("kind") or "",
                    "space_group": space.get("group") or "",
                    "price": safe_int(space.get("price")),
                    "owner_id": space.get("owner_id") or "",
                    "mortgaged": bool(space.get("mortgaged")),
                    "houses": safe_int(space.get("houses")),
                    "hotel": bool(space.get("hotel")),
                }
            )
    return state_rows, holding_rows, bank_rows


def to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def money_formatter(value: float, _pos: int | None = None) -> str:
    return f"${value:,.0f}"


def integer_formatter(value: float, _pos: int | None = None) -> str:
    return f"{value:,.0f}"


def save_line_plot(
    df: pd.DataFrame,
    path: Path,
    title: str,
    x_column: str,
    y_columns: list[str],
    y_label: str,
    y_money: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
    if df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        for column in y_columns:
            if column in df:
                ax.plot(df[x_column], df[column], linewidth=1.8, label=column)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax.yaxis.set_major_formatter(FuncFormatter(money_formatter if y_money else integer_formatter))
        ax.grid(True, alpha=0.25)
        if len(y_columns) > 1:
            ax.legend(loc="best", fontsize=8)
    ax.set_title(title)
    ax.set_xlabel(x_column.replace("_", " ").title())
    ax.set_ylabel(y_label)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_bar_plot(df: pd.DataFrame, path: Path, title: str, x_column: str, y_column: str, y_label: str, y_money: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6), dpi=160)
    if df.empty or x_column not in df or y_column not in df:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        ax.bar(df[x_column].astype(str), df[y_column])
        ax.tick_params(axis="x", rotation=25)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
        ax.yaxis.set_major_formatter(FuncFormatter(money_formatter if y_money else integer_formatter))
        ax.grid(True, axis="y", alpha=0.25)
    ax.set_title(title)
    ax.set_xlabel(x_column.replace("_", " ").title())
    ax.set_ylabel(y_label)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def percentile(series: pd.Series, q: float) -> float:
    if series.empty:
        return 0.0
    return float(series.quantile(q))


def table_from_counter(counter: Counter[str], key_name: str, value_name: str = "count") -> list[dict[str, Any]]:
    return [{key_name: key, value_name: value} for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0]))]


def build_file_inventory(saved_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    standard_prefix = f"{STANDARD_ANALYSIS_DIR_NAME}/"
    standard_zip = f"{saved_dir.name}-analysis.zip"
    for path in sorted(saved_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(saved_dir).as_posix()
        if rel == standard_zip or rel == "saved_game_manifest.json" or rel.startswith(standard_prefix):
            continue
        area = "other"
        if rel.startswith("run/"):
            area = "run"
        elif rel.startswith("quality_check/"):
            area = "quality_check"
        rows.append(
            {
                "relative_path": rel,
                "area": area,
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
            }
        )
    summary = []
    for area, group in pd.DataFrame(rows).groupby("area") if rows else []:
        summary.append(
            {
                "area": area,
                "files": int(len(group)),
                "size_bytes": int(group["size_bytes"].sum()),
                "size_mb": round(float(group["size_bytes"].sum()) / (1024 * 1024), 3),
            }
        )
    return rows, summary


def generate_analysis(saved_dir: Path) -> dict[str, Any]:
    folder_name = saved_dir.name
    run_dir = saved_dir / "run"
    quality_dir = saved_dir / "quality_check"
    out_dir = saved_dir / STANDARD_ANALYSIS_DIR_NAME
    tables_dir = out_dir / "tables"
    plots_dir = out_dir / "plots"
    reports_dir = out_dir / "reports"
    coverage_dir = out_dir / "coverage"

    archive_current_standard_analysis_dir(saved_dir, out_dir)
    for directory in [tables_dir, plots_dir, reports_dir, coverage_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    archive_current_standard_zip(saved_dir)

    board_doc = read_json(BOARD_PATH, {})
    if isinstance(board_doc, dict) and board_doc.get("house_cost_by_group"):
        HOUSE_COST_BY_GROUP.update(board_doc["house_cost_by_group"])

    summary = read_json(run_dir / "summary.json", {})
    players = load_players(run_dir, summary)
    player_ids = [player.get("player_id") or player.get("name") for player in players]
    player_ids = [player_id for player_id in player_ids if player_id]

    usage_rows = normalize_usage(read_jsonl(run_dir / "usage_attempts.jsonl"))
    decisions_rows = extract_decision_rows(read_jsonl(run_dir / "decisions.jsonl"))
    action_rows = [flatten(row) for row in read_jsonl(run_dir / "actions.jsonl")]
    event_rows = extract_event_rows(read_jsonl(run_dir / "events.jsonl"))
    state_rows, holding_rows, bank_rows = state_tables(run_dir, players)
    trace_rows = [flatten(row) for row in read_jsonl(run_dir / "trace_findings.jsonl")]
    failure_rows = [flatten(row) for row in read_jsonl(run_dir / "failure_findings.jsonl")]
    review_rows = [flatten(row) for row in read_jsonl(run_dir / "review_queue.jsonl")]
    cash_flow_rows = [flatten(row) for row in read_jsonl(run_dir / "cash_flow.jsonl")]
    asset_flow_rows = [flatten(row) for row in read_jsonl(run_dir / "asset_flow.jsonl")]
    auction_thread_rows = [flatten(row) for row in read_jsonl(run_dir / "auction_threads.jsonl")]
    negotiation_thread_rows = [flatten(row) for row in read_jsonl(run_dir / "negotiation_threads.jsonl")]

    usage_df = to_frame(usage_rows)
    decisions_df = to_frame(decisions_rows)
    events_df = to_frame(event_rows)
    state_df = to_frame(state_rows)
    holdings_df = to_frame(holding_rows)
    bank_df = to_frame(bank_rows)

    run_summary_rows = [
        {
            "saved_game": folder_name,
            "run_id": summary.get("run_id", ""),
            "winner_player_id": summary.get("winner_player_id", ""),
            "turn_count": summary.get("turn_count", ""),
            "end_reason": summary.get("reason", ""),
            "total_decisions": (summary.get("decision_stats") or {}).get("total_decisions", ""),
            "invalid_attempts": (summary.get("decision_stats") or {}).get("invalid_attempts", ""),
            "fallbacks": (summary.get("decision_stats") or {}).get("fallbacks", ""),
            "summary_total_cost": (summary.get("token_usage") or {}).get("total_cost", ""),
            "summary_total_tokens": (summary.get("token_usage") or {}).get("total_tokens", ""),
            "usage_rows": len(usage_rows),
            "decision_rows": len(decisions_rows),
            "action_rows": len(action_rows),
            "event_rows": len(event_rows),
            "state_snapshots": len(canonical_state_files(run_dir / "state")),
        }
    ]

    player_rows: list[dict[str, Any]] = []
    summary_players = summary.get("players") or {}
    for player in players:
        player_id = player.get("player_id") or player.get("name")
        final = summary_players.get(player_id, {})
        provider = player.get("provider") or {}
        reasoning = player.get("reasoning") or {}
        player_rows.append(
            {
                "player_id": player_id,
                "name": player.get("name") or player_id,
                "openrouter_model_id": player.get("openrouter_model_id") or "",
                "model_display_name": player.get("model_display_name") or "",
                "provider_only": stringify(provider.get("only") or []),
                "provider_allow_fallbacks": provider.get("allow_fallbacks", ""),
                "reasoning_effort": reasoning.get("effort") or "",
                "final_cash": final.get("cash", ""),
                "final_net_worth_estimate": final.get("net_worth_estimate", ""),
                "final_property_value_estimate": final.get("property_value_estimate", ""),
                "final_building_value_estimate": final.get("building_value_estimate", ""),
                "final_mortgage_liability_estimate": final.get("mortgage_liability_estimate", ""),
                "bankrupt": final.get("bankrupt", ""),
                "turns_played": final.get("turns_played", ""),
            }
        )

    model_usage_rows: list[dict[str, Any]] = []
    if not usage_df.empty:
        numeric_cols = ["input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "cached_tokens", "cost", "latency_ms"]
        for column in numeric_cols:
            usage_df[column] = pd.to_numeric(usage_df[column], errors="coerce").fillna(0)
        for player_id, group in usage_df.groupby("player_id", dropna=False):
            model_usage_rows.append(
                {
                    "player_id": player_id,
                    "openrouter_model_id": first_non_empty(group, "openrouter_model_id"),
                    "model_display_name": first_non_empty(group, "model_display_name"),
                    "calls": int(len(group)),
                    "retry_attempts": int((group["attempt_index"] > 0).sum()),
                    "fallback_rows": int(group["fallback_used"].astype(bool).sum()),
                    "input_tokens": int(group["input_tokens"].sum()),
                    "output_tokens": int(group["output_tokens"].sum()),
                    "reasoning_tokens": int(group["reasoning_tokens"].sum()),
                    "total_tokens": int(group["total_tokens"].sum()),
                    "cached_tokens": int(group["cached_tokens"].sum()),
                    "cost": round(float(group["cost"].sum()), 6),
                    "avg_latency_ms": round(float(group["latency_ms"].mean()), 2),
                    "median_latency_ms": round(float(group["latency_ms"].median()), 2),
                    "p95_latency_ms": round(percentile(group["latency_ms"], 0.95), 2),
                    "max_latency_ms": int(group["latency_ms"].max()),
                    "max_output_tokens": int(group["output_tokens"].max()),
                    "max_reasoning_tokens": int(group["reasoning_tokens"].max()),
                }
            )

    per_turn_usage_rows: list[dict[str, Any]] = []
    per_turn_total_rows: list[dict[str, Any]] = []
    if not usage_df.empty:
        grouped = usage_df.groupby(["turn_index", "player_id"], dropna=False)
        for (turn_index, player_id), group in grouped:
            per_turn_usage_rows.append(
                {
                    "turn_index": int(turn_index),
                    "player_id": player_id,
                    "calls": int(len(group)),
                    "cost": round(float(group["cost"].sum()), 6),
                    "input_tokens": int(group["input_tokens"].sum()),
                    "output_tokens": int(group["output_tokens"].sum()),
                    "reasoning_tokens": int(group["reasoning_tokens"].sum()),
                    "total_tokens": int(group["total_tokens"].sum()),
                    "latency_ms": int(group["latency_ms"].sum()),
                }
            )
        for turn_index, group in usage_df.groupby("turn_index", dropna=False):
            per_turn_total_rows.append(
                {
                    "turn_index": int(turn_index),
                    "calls": int(len(group)),
                    "cost": round(float(group["cost"].sum()), 6),
                    "input_tokens": int(group["input_tokens"].sum()),
                    "output_tokens": int(group["output_tokens"].sum()),
                    "reasoning_tokens": int(group["reasoning_tokens"].sum()),
                    "total_tokens": int(group["total_tokens"].sum()),
                    "latency_ms": int(group["latency_ms"].sum()),
                }
            )

    decision_type_rows = (
        table_from_counter(Counter(row.get("decision_type", "") for row in decisions_rows), "decision_type")
        if decisions_rows
        else []
    )
    event_type_rows = (
        table_from_counter(Counter(row.get("event_type", "") for row in event_rows), "event_type")
        if event_rows
        else []
    )
    events_by_turn_rows: list[dict[str, Any]] = []
    if not events_df.empty:
        for turn_index, group in events_df.groupby("turn_index", dropna=False):
            events_by_turn_rows.append({"turn_index": turn_index, "events": int(len(group))})

    top_tables = {
        "top_costliest_calls.csv": sorted(usage_rows, key=lambda row: safe_float(row.get("cost")), reverse=True)[:30],
        "top_slowest_calls.csv": sorted(usage_rows, key=lambda row: safe_int(row.get("latency_ms")), reverse=True)[:30],
        "top_output_token_calls.csv": sorted(usage_rows, key=lambda row: safe_int(row.get("output_tokens")), reverse=True)[:30],
        "top_reasoning_token_calls.csv": sorted(usage_rows, key=lambda row: safe_int(row.get("reasoning_tokens")), reverse=True)[:30],
    }

    artifact_presence_rows = []
    for name in EXPECTED_RUN_TOP_LEVEL:
        path = run_dir / name
        artifact_presence_rows.append(
            {
                "artifact": name,
                "exists": path.exists(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
                "size_bytes": sum(child.stat().st_size for child in path.rglob("*") if child.is_file())
                if path.is_dir()
                else path.stat().st_size
                if path.exists()
                else 0,
            }
        )

    file_inventory_rows, file_inventory_summary_rows = build_file_inventory(saved_dir)

    table_sets = {
        "run_summary.csv": run_summary_rows,
        "players.csv": player_rows,
        "model_usage.csv": model_usage_rows,
        "per_call_usage.csv": usage_rows,
        "per_turn_usage_by_player.csv": per_turn_usage_rows,
        "per_turn_usage_total.csv": per_turn_total_rows,
        "decisions.csv": decisions_rows,
        "decision_type_counts.csv": decision_type_rows,
        "actions.csv": action_rows,
        "events.csv": event_rows,
        "event_counts.csv": event_type_rows,
        "events_by_turn.csv": events_by_turn_rows,
        "state_by_turn_player.csv": state_rows,
        "property_holdings_by_turn.csv": holding_rows,
        "bank_inventory_by_turn.csv": bank_rows,
        "trace_findings.csv": trace_rows,
        "failure_findings.csv": failure_rows,
        "review_queue.csv": review_rows,
        "cash_flow.csv": cash_flow_rows,
        "asset_flow.csv": asset_flow_rows,
        "auction_threads.csv": auction_thread_rows,
        "negotiation_threads.csv": negotiation_thread_rows,
    }
    for filename, rows in table_sets.items():
        write_csv(tables_dir / filename, rows)
    for filename, rows in top_tables.items():
        write_csv(tables_dir / filename, rows)
    write_csv(coverage_dir / "artifact_presence.csv", artifact_presence_rows)
    write_csv(coverage_dir / "file_inventory.csv", file_inventory_rows)
    write_csv(coverage_dir / "file_inventory_summary.csv", file_inventory_summary_rows)

    make_plots(plots_dir, usage_df, state_df, bank_df, events_df, decisions_df, model_usage_rows)

    manifest = {
        "schema_version": "saved_game_standard_analysis_v1",
        "saved_game": folder_name,
        "run_id": summary.get("run_id"),
        "run_dir": "run",
        "standard_analysis_dir": STANDARD_ANALYSIS_DIR_NAME,
        "global_archive_dir": str(global_archive_dir(saved_dir).relative_to(SAVED_ROOT)),
        "quality_check_dir": "quality_check" if quality_dir.exists() else None,
        "tables": sorted(path.name for path in tables_dir.glob("*.csv")),
        "plots": sorted(path.name for path in plots_dir.glob("*.png")),
        "reports": ["analysis_report.md", "coverage_report.md", "data_dictionary.md"],
        "artifact_presence": {
            row["artifact"]: bool(row["exists"]) for row in artifact_presence_rows
        },
        "counts": {
            "usage_rows": len(usage_rows),
            "decision_rows": len(decisions_rows),
            "action_rows": len(action_rows),
            "event_rows": len(event_rows),
            "state_player_rows": len(state_rows),
            "property_holding_rows": len(holding_rows),
            "quality_check_files": len(list(quality_dir.glob("*"))) if quality_dir.exists() else 0,
        },
    }
    write_json(out_dir / "manifest.json", manifest)
    write_reports(reports_dir, folder_name, summary, manifest, run_summary_rows[0], player_rows, model_usage_rows, artifact_presence_rows)
    create_standard_zip(saved_dir, out_dir)
    write_saved_game_manifest(saved_dir, manifest, file_inventory_summary_rows)
    return manifest


def first_non_empty(df: pd.DataFrame, column: str) -> Any:
    if column not in df:
        return ""
    for value in df[column]:
        if value not in (None, ""):
            return value
    return ""


def make_plots(
    plots_dir: Path,
    usage_df: pd.DataFrame,
    state_df: pd.DataFrame,
    bank_df: pd.DataFrame,
    events_df: pd.DataFrame,
    decisions_df: pd.DataFrame,
    model_usage_rows: list[dict[str, Any]],
) -> None:
    if not state_df.empty:
        for column in ["cash", "net_worth_estimate", "property_value", "building_value", "mortgage_liability", "property_count"]:
            pivot = state_df.pivot_table(index="turn_index", columns="player_id", values=column, aggfunc="last").reset_index()
            save_line_plot(
                pivot,
                plots_dir / f"{column}_by_turn.png",
                f"{column.replace('_', ' ').title()} By Turn",
                "turn_index",
                [column for column in pivot.columns if column != "turn_index"],
                column.replace("_", " ").title(),
                y_money=column not in {"property_count"},
            )
        for column in ["houses", "hotels"]:
            pivot = state_df.pivot_table(index="turn_index", columns="player_id", values=column, aggfunc="last").reset_index()
            save_line_plot(
                pivot,
                plots_dir / f"{column}_by_turn.png",
                f"{column.title()} By Turn",
                "turn_index",
                [column for column in pivot.columns if column != "turn_index"],
                column.title(),
            )
    if not bank_df.empty:
        save_line_plot(
            bank_df,
            plots_dir / "bank_inventory_by_turn.png",
            "Bank Building Inventory By Turn",
            "turn_index",
            ["houses_remaining", "hotels_remaining"],
            "Remaining Buildings",
        )
    if not usage_df.empty:
        per_turn = usage_df.groupby("turn_index", as_index=False)[
            ["cost", "input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "latency_ms"]
        ].sum()
        save_line_plot(per_turn, plots_dir / "cost_by_turn.png", "Cost By Turn", "turn_index", ["cost"], "Cost", y_money=True)
        save_line_plot(
            per_turn,
            plots_dir / "tokens_by_turn.png",
            "Tokens By Turn",
            "turn_index",
            ["input_tokens", "output_tokens", "reasoning_tokens"],
            "Tokens",
        )
        per_turn["calls"] = usage_df.groupby("turn_index").size().values
        save_line_plot(per_turn, plots_dir / "calls_by_turn.png", "LLM Calls By Turn", "turn_index", ["calls"], "Calls")
        usage_sorted = usage_df.sort_values("call_index").copy()
        usage_sorted["cumulative_cost"] = usage_sorted["cost"].cumsum()
        save_line_plot(
            usage_sorted,
            plots_dir / "cumulative_cost_by_call.png",
            "Cumulative Cost By Call",
            "call_index",
            ["cumulative_cost"],
            "Cumulative Cost",
            y_money=True,
        )
        save_line_plot(usage_sorted, plots_dir / "cost_per_call.png", "Cost Per Call", "call_index", ["cost"], "Cost", y_money=True)
        save_line_plot(
            usage_sorted,
            plots_dir / "latency_per_call.png",
            "Latency Per Call",
            "call_index",
            ["latency_ms"],
            "Latency Ms",
        )
        save_line_plot(
            usage_sorted,
            plots_dir / "reasoning_tokens_per_call.png",
            "Reasoning Tokens Per Call",
            "call_index",
            ["reasoning_tokens"],
            "Reasoning Tokens",
        )
        save_line_plot(
            usage_sorted,
            plots_dir / "output_tokens_per_call.png",
            "Output Tokens Per Call",
            "call_index",
            ["output_tokens"],
            "Output Tokens",
        )
    if model_usage_rows:
        model_df = pd.DataFrame(model_usage_rows)
        save_bar_plot(model_df, plots_dir / "cost_by_model.png", "Cost By Model", "player_id", "cost", "Cost", y_money=True)
        save_bar_plot(model_df, plots_dir / "calls_by_model.png", "Calls By Model", "player_id", "calls", "Calls")
        save_bar_plot(
            model_df,
            plots_dir / "reasoning_tokens_by_model.png",
            "Reasoning Tokens By Model",
            "player_id",
            "reasoning_tokens",
            "Reasoning Tokens",
        )
        save_bar_plot(
            model_df,
            plots_dir / "total_tokens_by_model.png",
            "Total Tokens By Model",
            "player_id",
            "total_tokens",
            "Total Tokens",
        )
    if not events_df.empty:
        event_counts = events_df.groupby("event_type", as_index=False).size().rename(columns={"size": "count"})
        event_counts = event_counts.sort_values("count", ascending=False).head(25)
        save_bar_plot(event_counts, plots_dir / "event_counts.png", "Top Event Counts", "event_type", "count", "Events")
    if not decisions_df.empty:
        decision_counts = decisions_df.groupby("decision_type", as_index=False).size().rename(columns={"size": "count"})
        decision_counts = decision_counts.sort_values("count", ascending=False).head(25)
        save_bar_plot(
            decision_counts,
            plots_dir / "decision_type_counts.png",
            "Decision Type Counts",
            "decision_type",
            "count",
            "Decisions",
        )


def write_reports(
    reports_dir: Path,
    folder_name: str,
    summary: dict[str, Any],
    manifest: dict[str, Any],
    run_summary: dict[str, Any],
    player_rows: list[dict[str, Any]],
    model_usage_rows: list[dict[str, Any]],
    artifact_presence_rows: list[dict[str, Any]],
) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    missing = [row["artifact"] for row in artifact_presence_rows if not row["exists"]]
    lines = [
        f"# Standardized Analysis: {folder_name}",
        "",
        "## Run",
        "",
        f"- Run ID: `{summary.get('run_id', '')}`",
        f"- Winner: `{summary.get('winner_player_id', '')}`",
        f"- Turns: `{summary.get('turn_count', '')}`",
        f"- End reason: `{summary.get('reason', '')}`",
        f"- Usage rows: `{run_summary.get('usage_rows')}`",
        f"- Decision rows: `{run_summary.get('decision_rows')}`",
        f"- Action rows: `{run_summary.get('action_rows')}`",
        f"- Event rows: `{run_summary.get('event_rows')}`",
        "",
        "## Players",
        "",
        "| Player | Model | Effort | Final Cash | Final Net Worth | Bankrupt |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in player_rows:
        lines.append(
            f"| {row['player_id']} | {row['openrouter_model_id']} | {row['reasoning_effort']} | "
            f"{row['final_cash']} | {row['final_net_worth_estimate']} | {row['bankrupt']} |"
        )
    lines.extend(["", "## Model Usage", "", "| Player | Calls | Cost | Input | Output | Reasoning | Total | P95 Latency Ms |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for row in model_usage_rows:
        lines.append(
            f"| {row['player_id']} | {row['calls']} | ${row['cost']:.6f} | {row['input_tokens']} | "
            f"{row['output_tokens']} | {row['reasoning_tokens']} | {row['total_tokens']} | {row['p95_latency_ms']} |"
        )
    lines.extend(
        [
            "",
            "## Standardized Outputs",
            "",
            f"- Tables: `{len(manifest.get('tables', []))}`",
            f"- Plots: `{len(manifest.get('plots', []))}`",
            "- Reports: `analysis_report.md`, `coverage_report.md`, `data_dictionary.md`",
            "",
            "Legacy and previous analysis artifacts are preserved under `saved_games/archive/<saved-game>/`. This folder is the current standardized cross-run analysis layer.",
        ]
    )
    (reports_dir / "analysis_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    coverage_lines = [
        f"# Coverage Report: {folder_name}",
        "",
        "## Canonical Run Artifact Presence",
        "",
        f"- Expected top-level run artifacts: `{len(artifact_presence_rows)}`",
        f"- Present: `{sum(1 for row in artifact_presence_rows if row['exists'])}`",
        f"- Missing: `{len(missing)}`",
        "",
    ]
    if missing:
        coverage_lines.extend(["## Missing", ""])
        coverage_lines.extend(f"- `{name}`" for name in missing)
    else:
        coverage_lines.append("No canonical run top-level artifacts are missing.")
    coverage_lines.extend(
        [
            "",
            "## Layout Contract",
            "",
            "- `run/`: canonical raw run artifacts.",
            "- `quality_check/`: request/response quality-check text files.",
            "- `analysis/`: current standardized cross-run analysis.",
            f"- `saved_games/archive/{folder_name}/`: preserved legacy analysis and previous generated zips.",
        ]
    )
    (reports_dir / "coverage_report.md").write_text("\n".join(coverage_lines) + "\n", encoding="utf-8")

    dictionary_lines = [
        f"# Data Dictionary: {folder_name}",
        "",
        "## Tables",
        "",
        "- `run_summary.csv`: one-row run summary and artifact counts.",
        "- `players.csv`: player/model configuration plus final summary values.",
        "- `model_usage.csv`: token, cost, retry, fallback, and latency totals by player/model.",
        "- `per_call_usage.csv`: one row per OpenRouter call attempt.",
        "- `per_turn_usage_by_player.csv`: token/cost totals by turn and player.",
        "- `per_turn_usage_total.csv`: token/cost totals by turn.",
        "- `decisions.csv`: flattened decision resolution rows.",
        "- `actions.csv`: applied engine actions.",
        "- `events.csv`: canonical event stream flattened for scanning.",
        "- `event_counts.csv`: event type frequency.",
        "- `events_by_turn.csv`: event volume by turn.",
        "- `state_by_turn_player.csv`: player cash, position, asset values, and computed net worth by turn.",
        "- `property_holdings_by_turn.csv`: owned property snapshots by turn.",
        "- `bank_inventory_by_turn.csv`: bank house/hotel inventory by turn.",
        "- `trace_findings.csv`, `failure_findings.csv`, `review_queue.csv`: review and issue traces.",
        "- `cash_flow.csv`, `asset_flow.csv`, `auction_threads.csv`, `negotiation_threads.csv`: domain-specific telemetry streams.",
        "- `top_*_calls.csv`: highest cost, latency, output-token, and reasoning-token call outliers.",
        "",
        "## Coverage",
        "",
        "- `coverage/artifact_presence.csv`: expected canonical artifact presence.",
        "- `coverage/file_inventory.csv`: recursive file inventory.",
        "- `coverage/file_inventory_summary.csv`: file counts and size by area.",
    ]
    (reports_dir / "data_dictionary.md").write_text("\n".join(dictionary_lines) + "\n", encoding="utf-8")


def write_saved_game_manifest(saved_dir: Path, analysis_manifest: dict[str, Any], file_inventory_summary: list[dict[str, Any]]) -> None:
    folder_name = saved_dir.name
    root_entries = sorted(path.name for path in saved_dir.iterdir())
    manifest = {
        "schema_version": "saved_game_layout_v1",
        "saved_game": folder_name,
        "layout": {
            "run_dir": "run",
            "quality_check_dir": "quality_check",
            "standard_analysis_dir": STANDARD_ANALYSIS_DIR_NAME,
            "standard_analysis_zip": f"{folder_name}-analysis.zip",
            "global_archive_dir": str(global_archive_dir(saved_dir).relative_to(SAVED_ROOT)),
        },
        "root_entries": root_entries,
        "analysis_manifest": f"{STANDARD_ANALYSIS_DIR_NAME}/manifest.json",
        "file_inventory_summary": file_inventory_summary,
        "preservation_policy": "Canonical run artifacts stay in this saved-game folder. Legacy analysis, previous standard analyses, and old share zips are preserved under saved_games/archive instead of deleted.",
    }
    write_json(saved_dir / "saved_game_manifest.json", manifest)


def create_standard_zip(saved_dir: Path, analysis_dir: Path) -> None:
    folder_name = saved_dir.name
    zip_path = saved_dir / f"{folder_name}-analysis.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(analysis_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(saved_dir).as_posix())


def archive_current_standard_zip(saved_dir: Path) -> None:
    folder_name = saved_dir.name
    zip_path = saved_dir / f"{folder_name}-analysis.zip"
    if not zip_path.exists():
        return
    archive_dir = global_archive_dir(saved_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    move_preserving(zip_path, next_available(archive_dir / "zips" / f"{folder_name}-previous-standard-analysis.zip"))


def archive_current_standard_analysis_dir(saved_dir: Path, analysis_dir: Path) -> None:
    if not analysis_dir.exists():
        return
    archive_dir = global_archive_dir(saved_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    move_preserving(analysis_dir, next_available(archive_dir / "analysis_dirs" / "previous-standard-analysis"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Standardize saved MonopolyBench game folders.")
    parser.add_argument("saved_games", nargs="*", default=DEFAULT_SAVED_GAMES)
    args = parser.parse_args()

    saved_dirs = [SAVED_ROOT / name for name in args.saved_games]
    for saved_dir in saved_dirs:
        if not saved_dir.exists():
            raise FileNotFoundError(saved_dir)
        standardize_layout(saved_dir)
    manifests = [generate_analysis(saved_dir) for saved_dir in saved_dirs]
    print(json.dumps({"standardized": [manifest["saved_game"] for manifest in manifests]}, indent=2))


if __name__ == "__main__":
    main()
