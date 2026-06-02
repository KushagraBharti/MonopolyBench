from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from monopoly_engine import canonical_event_lines, replay_actions
from monopoly_telemetry import RunFiles


REPLAY_REPORT_VERSION = "replay_report_v1"
MAJOR_EVENT_TYPES = {
    "GAME_ENDED",
    "LLM_DECISION_REQUESTED",
    "LLM_DECISION_RESPONSE",
    "AUCTION_STARTED",
    "AUCTION_ENDED",
    "TRADE_PROPOSED",
    "TRADE_ACCEPTED",
    "TRADE_REJECTED",
    "TRADE_COUNTERED",
    "TRADE_EXPIRED",
    "PROPERTY_PURCHASED",
    "PROPERTY_TRANSFERRED",
    "RENT_PAID",
    "HOUSE_BUILT",
    "HOTEL_BUILT",
    "HOUSE_SOLD",
    "HOTEL_SOLD",
    "PROPERTY_MORTGAGED",
    "PROPERTY_UNMORTGAGED",
    "SENT_TO_JAIL",
    "CASH_CHANGED",
}


def write_replay_verification_artifacts(run_files: RunFiles) -> dict[str, Any]:
    report = build_replay_verification_report(run_files)
    original_events = _read_jsonl(run_files.events_path)
    _write_jsonl(run_files.replay_steps_path, _build_replay_steps(original_events))
    _write_jsonl(run_files.replay_flags_path, _build_replay_flags(original_events))
    run_files.write_json_artifact(run_files.replay_navigation_path, _build_replay_navigation(original_events))
    run_files.write_json_artifact(run_files.event_hashes_path, _build_event_hashes(original_events, report))
    run_files.write_json_artifact(run_files.replay_diff_path, _build_replay_diff(report))
    run_files.write_json_artifact(run_files.replay_report_path, report)
    return report


def build_replay_verification_report(run_files: RunFiles) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()
    original_events = _read_jsonl(run_files.events_path)
    actions = _read_jsonl(run_files.actions_path)
    run_config = _read_json(run_files.run_config_path)
    players = _replay_players(run_config)
    base_report: dict[str, Any] = {
        "schema_version": "v1",
        "replay_report_version": REPLAY_REPORT_VERSION,
        "run_id": run_files.run_id,
        "attempted": False,
        "status": "not_attempted",
        "started_at": started_at,
        "finished_at": None,
        "original_event_count": len(original_events),
        "replay_event_count": None,
        "original_canonical_hash": _hash_lines(canonical_event_lines(original_events)),
        "replay_canonical_hash": None,
        "first_mismatch_index": None,
        "first_mismatch_original_event": None,
        "first_mismatch_replay_event": None,
        "missing_actions": 0,
        "extra_actions": 0,
        "missing_events": None,
        "extra_events": None,
        "decision_id_mismatch": False,
        "error": None,
        "run_config_used": {
            "seed": run_config.get("seed"),
            "max_turns": run_config.get("max_turns", 200),
            "start_ts_ms": run_config.get("start_ts_ms", 0),
            "ts_step_ms": run_config.get("ts_step_ms", 250),
            "max_trade_exchanges": run_config.get("max_trade_exchanges", 20),
            "max_auction_actions": run_config.get("max_auction_actions", 200),
            "player_count": len(players),
        },
    }
    if not original_events:
        base_report["status"] = "failed"
        base_report["error"] = "events.jsonl is empty or missing"
        base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
        return base_report
    if not actions:
        base_report["status"] = "failed"
        base_report["error"] = "actions.jsonl is empty or missing"
        base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
        return base_report
    if not isinstance(run_config.get("seed"), int):
        base_report["status"] = "failed"
        base_report["error"] = "run_config.json missing integer seed"
        base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
        return base_report
    if not players:
        base_report["status"] = "failed"
        base_report["error"] = "run_config.json missing replay players"
        base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
        return base_report

    base_report["attempted"] = True
    try:
        replayed_events = replay_actions(
            seed=int(run_config["seed"]),
            players=players,
            run_id=run_files.run_id,
            actions=actions,
            max_turns=int(run_config.get("max_turns", 200)),
            start_ts_ms=int(run_config.get("start_ts_ms", 0)),
            ts_step_ms=int(run_config.get("ts_step_ms", 250)),
            max_trade_exchanges=int(run_config.get("max_trade_exchanges", 20)),
            max_auction_actions=int(run_config.get("max_auction_actions", 200)),
        )
    except ValueError as exc:
        base_report["status"] = "failed"
        base_report["error"] = str(exc)
        base_report["decision_id_mismatch"] = "Decision id mismatch" in str(exc)
        base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
        return base_report
    except Exception as exc:  # pragma: no cover - defensive report path
        base_report["status"] = "failed"
        base_report["error"] = str(exc)
        base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
        return base_report

    original_lines = canonical_event_lines(original_events)
    replay_lines = canonical_event_lines(replayed_events)
    first_mismatch = _first_mismatch(original_lines, replay_lines)
    base_report["replay_event_count"] = len(replayed_events)
    base_report["replay_canonical_hash"] = _hash_lines(replay_lines)
    base_report["first_mismatch_index"] = first_mismatch
    if len(original_lines) > len(replay_lines):
        base_report["missing_events"] = len(original_lines) - len(replay_lines)
        base_report["extra_events"] = 0
    elif len(replay_lines) > len(original_lines):
        base_report["missing_events"] = 0
        base_report["extra_events"] = len(replay_lines) - len(original_lines)
    else:
        base_report["missing_events"] = 0
        base_report["extra_events"] = 0
    if first_mismatch is not None:
        base_report["first_mismatch_original_event"] = (
            original_events[first_mismatch] if first_mismatch < len(original_events) else None
        )
        base_report["first_mismatch_replay_event"] = (
            replayed_events[first_mismatch] if first_mismatch < len(replayed_events) else None
        )
    base_report["status"] = "passed" if first_mismatch is None else "failed"
    base_report["finished_at"] = datetime.now(timezone.utc).isoformat()
    return base_report


def _build_event_hashes(events: list[dict[str, Any]], report: dict[str, Any]) -> dict[str, Any]:
    canonical_lines = canonical_event_lines(events)
    return {
        "schema_version": "v1",
        "event_hashes_version": "event_hashes_v1",
        "run_id": report.get("run_id"),
        "canonicalization": "monopoly_engine.canonical_event_lines",
        "event_count": len(events),
        "stream_sha256": _hash_lines(canonical_lines),
        "replay_stream_sha256": report.get("replay_canonical_hash"),
        "events": [
            {
                "index": index,
                "seq": events[index].get("seq") if index < len(events) else None,
                "event_id": events[index].get("event_id") if index < len(events) else None,
                "type": events[index].get("type") if index < len(events) else None,
                "canonical_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
            }
            for index, line in enumerate(canonical_lines)
        ],
    }


def _build_replay_diff(report: dict[str, Any]) -> dict[str, Any]:
    status = report.get("status")
    return {
        "schema_version": "v1",
        "replay_diff_version": "replay_diff_v1",
        "run_id": report.get("run_id"),
        "status": "no_diff" if status == "passed" else "diff_or_error",
        "replay_status": status,
        "first_mismatch_index": report.get("first_mismatch_index"),
        "first_mismatch_original_event": report.get("first_mismatch_original_event"),
        "first_mismatch_replay_event": report.get("first_mismatch_replay_event"),
        "original_event_count": report.get("original_event_count"),
        "replay_event_count": report.get("replay_event_count"),
        "missing_events": report.get("missing_events"),
        "extra_events": report.get("extra_events"),
        "decision_id_mismatch": report.get("decision_id_mismatch"),
        "error": report.get("error"),
        "original_canonical_hash": report.get("original_canonical_hash"),
        "replay_canonical_hash": report.get("replay_canonical_hash"),
    }


def _build_replay_steps(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": "v1",
            "step_index": index,
            "run_id": event.get("run_id"),
            "event_id": event.get("event_id"),
            "seq": event.get("seq"),
            "turn_index": event.get("turn_index"),
            "type": event.get("type"),
            "decision_id": _event_decision_id(event),
            "is_major": event.get("type") in MAJOR_EVENT_TYPES,
            "event": event,
        }
        for index, event in enumerate(events)
    ]


def _build_replay_flags(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        event_type = event.get("type")
        if event_type not in MAJOR_EVENT_TYPES:
            continue
        flags.append(
            {
                "schema_version": "v1",
                "flag_id": f"flag-{index:06d}",
                "run_id": event.get("run_id"),
                "step_index": index,
                "seq": event.get("seq"),
                "turn_index": event.get("turn_index"),
                "event_id": event.get("event_id"),
                "event_type": event_type,
                "decision_id": _event_decision_id(event),
                "category": _flag_category(str(event_type)),
                "severity": _flag_severity(str(event_type)),
                "summary": _flag_summary(event),
            }
        )
    return flags


def _build_replay_navigation(events: list[dict[str, Any]]) -> dict[str, Any]:
    navigation: dict[str, Any] = {
        "schema_version": "v1",
        "navigation_version": "replay_navigation_v1",
        "turns": {},
        "decisions": {},
        "event_types": {},
        "important_steps": [],
        "failures": [],
        "negotiations": [],
        "auctions": [],
        "bankruptcies": [],
        "cash_collapses": [],
        "model_decisions": [],
    }
    for index, event in enumerate(events):
        turn = str(event.get("turn_index"))
        navigation["turns"].setdefault(turn, []).append(index)
        event_type = str(event.get("type"))
        navigation["event_types"].setdefault(event_type, []).append(index)
        decision_id = _event_decision_id(event)
        if decision_id:
            navigation["decisions"].setdefault(decision_id, []).append(index)
        if event_type in MAJOR_EVENT_TYPES:
            navigation["important_steps"].append(index)
        if event_type in {"LLM_DECISION_REQUESTED", "LLM_DECISION_RESPONSE"}:
            navigation["model_decisions"].append(index)
        if event_type.startswith("TRADE_"):
            navigation["negotiations"].append(index)
        if event_type.startswith("AUCTION_"):
            navigation["auctions"].append(index)
        payload = _dict(event.get("payload"))
        if event_type == "CASH_CHANGED" and str(payload.get("reason", "")).startswith("BANKRUPTCY"):
            navigation["bankruptcies"].append(index)
            navigation["failures"].append(index)
        if event_type == "CASH_CHANGED" and isinstance(payload.get("delta"), int) and payload["delta"] <= -200:
            navigation["cash_collapses"].append(index)
    return navigation


def _flag_category(event_type: str) -> str:
    if event_type.startswith("TRADE_"):
        return "negotiation"
    if event_type.startswith("AUCTION_"):
        return "auction"
    if event_type in {"LLM_DECISION_REQUESTED", "LLM_DECISION_RESPONSE"}:
        return "model_decision"
    if event_type in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
        return "development"
    if event_type in {"PROPERTY_PURCHASED", "PROPERTY_TRANSFERRED", "PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"}:
        return "asset"
    if event_type in {"RENT_PAID", "CASH_CHANGED"}:
        return "cash_flow"
    return "game"


def _flag_severity(event_type: str) -> str:
    if event_type in {"GAME_ENDED", "TRADE_ACCEPTED", "AUCTION_ENDED", "RENT_PAID"}:
        return "high"
    if event_type in {"LLM_DECISION_RESPONSE", "PROPERTY_TRANSFERRED", "PROPERTY_PURCHASED"}:
        return "medium"
    return "low"


def _flag_summary(event: dict[str, Any]) -> str:
    event_type = str(event.get("type"))
    payload = _dict(event.get("payload"))
    if event_type == "RENT_PAID":
        return f"{payload.get('from_player_id')} paid {payload.get('amount')} rent to {payload.get('to_player_id')}"
    if event_type == "AUCTION_ENDED":
        return f"Auction ended for {payload.get('property_space')} with winner {payload.get('winner_player_id')}"
    if event_type.startswith("TRADE_"):
        return f"{event_type} between {payload.get('initiator_player_id')} and {payload.get('counterparty_player_id')}"
    if event_type == "LLM_DECISION_RESPONSE":
        return f"{payload.get('player_id')} chose {payload.get('action_name')}"
    return event_type


def _event_decision_id(event: dict[str, Any]) -> str | None:
    payload = _dict(event.get("payload"))
    value = payload.get("decision_id")
    return value if isinstance(value, str) else None


def _replay_players(run_config: dict[str, Any]) -> list[dict[str, Any]]:
    players: list[dict[str, Any]] = []
    for entry in _list(run_config.get("players")):
        if not isinstance(entry, dict):
            continue
        player_id = entry.get("player_id")
        name = entry.get("name")
        if isinstance(player_id, str):
            players.append({"player_id": player_id, "name": name if isinstance(name, str) else player_id})
    return players


def _first_mismatch(original_lines: list[str], replay_lines: list[str]) -> int | None:
    for index, (original, replayed) in enumerate(zip(original_lines, replay_lines)):
        if original != replayed:
            return index
    if len(original_lines) != len(replay_lines):
        return min(len(original_lines), len(replay_lines))
    return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _hash_lines(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")
