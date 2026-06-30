from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from monopoly_engine import canonical_event_lines, replay_actions
from monopoly_telemetry import RunFiles


REPLAY_REPORT_VERSION = "replay_report_v2"
STATE_REPLAY_REPORT_VERSION = "state_replay_report_v1"
ARTIFACT_REPLAY_REPORT_VERSION = "artifact_replay_report_v1"
STATE_REPLAY_EXCLUDED_EVENT_TYPES = {
    "LLM_DECISION_REQUESTED",
    "LLM_DECISION_RESPONSE",
    "LLM_PUBLIC_MESSAGE",
    "LLM_PRIVATE_THOUGHT",
}
STATE_REPLAY_CANONICALIZATION = (
    "monopoly_engine.canonical_event_lines over state-relevant events after dropping "
    "LLM observation events and normalizing global event_id/seq/ts_ms to a state_event_index"
)
ARTIFACT_REPLAY_CANONICALIZATION = "monopoly_engine.canonical_event_lines over the full event stream"
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
    reports = build_replay_verification_reports(run_files)
    report = reports["replay_report"]
    state_report = reports["state_replay_report"]
    artifact_report = reports["artifact_replay_report"]
    original_events = _read_jsonl(run_files.events_path)
    _write_jsonl(run_files.replay_steps_path, _build_replay_steps(original_events))
    _write_jsonl(run_files.replay_flags_path, _build_replay_flags(original_events))
    run_files.write_json_artifact(run_files.replay_navigation_path, _build_replay_navigation(original_events))
    run_files.write_json_artifact(run_files.event_hashes_path, _build_event_hashes(original_events, artifact_report))
    run_files.write_json_artifact(run_files.replay_diff_path, _build_replay_diff(artifact_report))
    run_files.write_json_artifact(run_files.state_replay_report_path, state_report)
    run_files.write_json_artifact(run_files.artifact_replay_report_path, artifact_report)
    run_files.write_json_artifact(run_files.replay_report_path, report)
    return report


def build_replay_verification_report(run_files: RunFiles) -> dict[str, Any]:
    return build_replay_verification_reports(run_files)["replay_report"]


def build_replay_verification_reports(run_files: RunFiles) -> dict[str, dict[str, Any]]:
    started_at = datetime.now(timezone.utc).isoformat()
    original_events = _read_jsonl(run_files.events_path)
    actions = _read_jsonl(run_files.actions_path)
    run_config = _read_json(run_files.run_config_path)
    players = _replay_players(run_config)
    context = _replay_context(run_files, started_at, original_events, actions, run_config, players)
    if not original_events:
        return _failed_reports(context, "events.jsonl is empty or missing")
    if not actions:
        return _failed_reports(context, "actions.jsonl is empty or missing")
    if not isinstance(run_config.get("seed"), int):
        return _failed_reports(context, "run_config.json missing integer seed")
    if not players:
        return _failed_reports(context, "run_config.json missing replay players")

    context["attempted"] = True
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
        return _failed_reports(
            context,
            str(exc),
            decision_id_mismatch="Decision id mismatch" in str(exc),
        )
    except Exception as exc:  # pragma: no cover - defensive report path
        return _failed_reports(context, str(exc))

    finished_at = datetime.now(timezone.utc).isoformat()
    state_report = _build_stream_report(
        context,
        report_kind="state",
        version_key="state_replay_report_version",
        version=STATE_REPLAY_REPORT_VERSION,
        comparison_scope="engine_state_relevant_events",
        original_events=original_events,
        replayed_events=replayed_events,
        original_lines=_state_event_lines(original_events),
        replay_lines=_state_event_lines(replayed_events),
        finished_at=finished_at,
        excluded_event_types=sorted(STATE_REPLAY_EXCLUDED_EVENT_TYPES),
        canonicalization=STATE_REPLAY_CANONICALIZATION,
    )
    artifact_report = _build_stream_report(
        context,
        report_kind="artifact",
        version_key="artifact_replay_report_version",
        version=ARTIFACT_REPLAY_REPORT_VERSION,
        comparison_scope="full_event_artifact_stream",
        original_events=original_events,
        replayed_events=replayed_events,
        original_lines=canonical_event_lines(original_events),
        replay_lines=canonical_event_lines(replayed_events),
        finished_at=finished_at,
        excluded_event_types=[],
        canonicalization=ARTIFACT_REPLAY_CANONICALIZATION,
    )
    replay_report = _build_aggregate_replay_report(context, state_report, artifact_report, finished_at)
    return {
        "replay_report": replay_report,
        "state_replay_report": state_report,
        "artifact_replay_report": artifact_report,
    }


def _replay_context(
    run_files: RunFiles,
    started_at: str,
    original_events: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    run_config: dict[str, Any],
    players: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "run_id": run_files.run_id,
        "attempted": False,
        "started_at": started_at,
        "original_event_count": len(original_events),
        "action_count": len(actions),
        "missing_actions": 0,
        "extra_actions": 0,
        "decision_id_mismatch": False,
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


def _failed_reports(
    context: dict[str, Any],
    error: str,
    *,
    decision_id_mismatch: bool = False,
) -> dict[str, dict[str, Any]]:
    finished_at = datetime.now(timezone.utc).isoformat()
    failed_context = {
        **context,
        "decision_id_mismatch": decision_id_mismatch,
    }
    state_report = _failed_stream_report(
        failed_context,
        report_kind="state",
        version_key="state_replay_report_version",
        version=STATE_REPLAY_REPORT_VERSION,
        comparison_scope="engine_state_relevant_events",
        finished_at=finished_at,
        error=error,
        excluded_event_types=sorted(STATE_REPLAY_EXCLUDED_EVENT_TYPES),
        canonicalization=STATE_REPLAY_CANONICALIZATION,
    )
    artifact_report = _failed_stream_report(
        failed_context,
        report_kind="artifact",
        version_key="artifact_replay_report_version",
        version=ARTIFACT_REPLAY_REPORT_VERSION,
        comparison_scope="full_event_artifact_stream",
        finished_at=finished_at,
        error=error,
        excluded_event_types=[],
        canonicalization=ARTIFACT_REPLAY_CANONICALIZATION,
    )
    replay_report = _build_aggregate_replay_report(failed_context, state_report, artifact_report, finished_at)
    return {
        "replay_report": replay_report,
        "state_replay_report": state_report,
        "artifact_replay_report": artifact_report,
    }


def _failed_stream_report(
    context: dict[str, Any],
    *,
    report_kind: str,
    version_key: str,
    version: str,
    comparison_scope: str,
    finished_at: str,
    error: str,
    excluded_event_types: list[str],
    canonicalization: str,
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        version_key: version,
        "run_id": context["run_id"],
        "report_kind": report_kind,
        "comparison_scope": comparison_scope,
        "canonicalization": canonicalization,
        "attempted": context["attempted"],
        "status": "failed",
        "started_at": context["started_at"],
        "finished_at": finished_at,
        "original_event_count": context["original_event_count"],
        "replay_event_count": None,
        "original_compared_event_count": None,
        "replay_compared_event_count": None,
        "original_canonical_hash": None,
        "replay_canonical_hash": None,
        "first_mismatch_index": None,
        "first_mismatch_original_event": None,
        "first_mismatch_replay_event": None,
        "missing_actions": context["missing_actions"],
        "extra_actions": context["extra_actions"],
        "missing_events": None,
        "extra_events": None,
        "decision_id_mismatch": context["decision_id_mismatch"],
        "error": error,
        "excluded_event_types": excluded_event_types,
        "run_config_used": context["run_config_used"],
    }


def _build_stream_report(
    context: dict[str, Any],
    *,
    report_kind: str,
    version_key: str,
    version: str,
    comparison_scope: str,
    original_events: list[dict[str, Any]],
    replayed_events: list[dict[str, Any]],
    original_lines: list[str],
    replay_lines: list[str],
    finished_at: str,
    excluded_event_types: list[str],
    canonicalization: str,
) -> dict[str, Any]:
    first_mismatch = _first_mismatch(original_lines, replay_lines)
    missing_events, extra_events = _event_count_delta(len(original_lines), len(replay_lines))
    report: dict[str, Any] = {
        "schema_version": "v1",
        version_key: version,
        "run_id": context["run_id"],
        "report_kind": report_kind,
        "comparison_scope": comparison_scope,
        "canonicalization": canonicalization,
        "attempted": True,
        "status": "passed" if first_mismatch is None else "failed",
        "started_at": context["started_at"],
        "finished_at": finished_at,
        "original_event_count": len(original_events),
        "replay_event_count": len(replayed_events),
        "original_compared_event_count": len(original_lines),
        "replay_compared_event_count": len(replay_lines),
        "original_canonical_hash": _hash_lines(original_lines),
        "replay_canonical_hash": _hash_lines(replay_lines),
        "first_mismatch_index": first_mismatch,
        "first_mismatch_original_event": None,
        "first_mismatch_replay_event": None,
        "missing_actions": context["missing_actions"],
        "extra_actions": context["extra_actions"],
        "missing_events": missing_events,
        "extra_events": extra_events,
        "decision_id_mismatch": context["decision_id_mismatch"],
        "error": None,
        "excluded_event_types": excluded_event_types,
        "run_config_used": context["run_config_used"],
    }
    if first_mismatch is not None:
        report["first_mismatch_original_event"] = _event_for_compared_index(
            original_events,
            first_mismatch,
            excluded_event_types=excluded_event_types,
        )
        report["first_mismatch_replay_event"] = _event_for_compared_index(
            replayed_events,
            first_mismatch,
            excluded_event_types=excluded_event_types,
        )
    return report


def _build_aggregate_replay_report(
    context: dict[str, Any],
    state_report: dict[str, Any],
    artifact_report: dict[str, Any],
    finished_at: str,
) -> dict[str, Any]:
    state_status = str(state_report.get("status") or "missing")
    artifact_status = str(artifact_report.get("status") or "missing")
    if state_status == "passed" and artifact_status == "passed":
        status = "passed"
    elif state_status == "passed" and artifact_status != "passed":
        status = "state_passed_artifact_failed"
    else:
        status = "failed"
    return {
        "schema_version": "v1",
        "replay_report_version": REPLAY_REPORT_VERSION,
        "run_id": context["run_id"],
        "attempted": bool(state_report.get("attempted") or artifact_report.get("attempted")),
        "status": status,
        "status_semantics": "aggregate_state_and_artifact_replay",
        "state_status": state_status,
        "artifact_status": artifact_status,
        "started_at": context["started_at"],
        "finished_at": finished_at,
        "original_event_count": context["original_event_count"],
        "replay_event_count": artifact_report.get("replay_event_count"),
        "state_original_canonical_hash": state_report.get("original_canonical_hash"),
        "state_replay_canonical_hash": state_report.get("replay_canonical_hash"),
        "artifact_original_canonical_hash": artifact_report.get("original_canonical_hash"),
        "artifact_replay_canonical_hash": artifact_report.get("replay_canonical_hash"),
        "state_first_mismatch_index": state_report.get("first_mismatch_index"),
        "artifact_first_mismatch_index": artifact_report.get("first_mismatch_index"),
        "state_first_mismatch_original_event": state_report.get("first_mismatch_original_event"),
        "state_first_mismatch_replay_event": state_report.get("first_mismatch_replay_event"),
        "artifact_first_mismatch_original_event": artifact_report.get("first_mismatch_original_event"),
        "artifact_first_mismatch_replay_event": artifact_report.get("first_mismatch_replay_event"),
        "missing_actions": context["missing_actions"],
        "extra_actions": context["extra_actions"],
        "state_missing_events": state_report.get("missing_events"),
        "state_extra_events": state_report.get("extra_events"),
        "artifact_missing_events": artifact_report.get("missing_events"),
        "artifact_extra_events": artifact_report.get("extra_events"),
        "decision_id_mismatch": bool(
            state_report.get("decision_id_mismatch") or artifact_report.get("decision_id_mismatch")
        ),
        "error": state_report.get("error") or artifact_report.get("error"),
        "state_replay_report": {
            "artifact": "state_replay_report.json",
            "status": state_status,
            "comparison_scope": state_report.get("comparison_scope"),
        },
        "artifact_replay_report": {
            "artifact": "artifact_replay_report.json",
            "status": artifact_status,
            "comparison_scope": artifact_report.get("comparison_scope"),
        },
        # Compatibility aliases preserve the old strict event-stream fields.
        "original_canonical_hash": artifact_report.get("original_canonical_hash"),
        "replay_canonical_hash": artifact_report.get("replay_canonical_hash"),
        "first_mismatch_index": artifact_report.get("first_mismatch_index"),
        "first_mismatch_original_event": artifact_report.get("first_mismatch_original_event"),
        "first_mismatch_replay_event": artifact_report.get("first_mismatch_replay_event"),
        "missing_events": artifact_report.get("missing_events"),
        "extra_events": artifact_report.get("extra_events"),
        "run_config_used": context["run_config_used"],
    }


def _event_count_delta(original_count: int, replay_count: int) -> tuple[int, int]:
    if original_count > replay_count:
        return original_count - replay_count, 0
    if replay_count > original_count:
        return 0, replay_count - original_count
    return 0, 0


def _state_event_lines(events: list[dict[str, Any]]) -> list[str]:
    return canonical_event_lines(_state_replay_events(events))


def _state_replay_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state_events: list[dict[str, Any]] = []
    for event in events:
        if event.get("type") in STATE_REPLAY_EXCLUDED_EVENT_TYPES:
            continue
        normalized = dict(event)
        normalized.pop("event_id", None)
        normalized.pop("seq", None)
        normalized.pop("ts_ms", None)
        normalized["state_event_index"] = len(state_events)
        state_events.append(normalized)
    return state_events


def _event_for_compared_index(
    events: list[dict[str, Any]],
    compared_index: int,
    *,
    excluded_event_types: list[str],
) -> dict[str, Any] | None:
    filtered = [event for event in events if event.get("type") not in set(excluded_event_types)]
    return filtered[compared_index] if compared_index < len(filtered) else None


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
