from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .run_files import RunFiles


TRACE_ANALYZER_VERSION = "trace_analyzer_v1"
FAILURE_TAXONOMY_VERSION = "failure_taxonomy_v1"
REVIEW_LABEL_VERSION = "review_label_v1"


def write_trace_failure_artifacts(run_files: RunFiles) -> dict[str, Any]:
    events = _read_jsonl(run_files.events_path)
    decisions = _read_jsonl(run_files.decisions_path)
    board_spec = _load_board_spec()
    trace_findings = _build_trace_findings(run_files.run_id, events, decisions, board_spec)
    failure_findings = _build_failure_findings(run_files.run_id, decisions, trace_findings)
    review_queue = _build_review_queue(run_files.run_id, trace_findings, failure_findings)
    trace_summary = _summarize_findings(run_files.run_id, trace_findings, "trace")
    failure_summary = _summarize_findings(run_files.run_id, failure_findings, "failure")
    _write_jsonl(run_files.trace_findings_path, trace_findings)
    _write_jsonl(run_files.failure_findings_path, failure_findings)
    _write_jsonl(run_files.review_queue_path, review_queue)
    run_files.write_json_artifact(run_files.trace_summary_path, trace_summary)
    run_files.write_json_artifact(run_files.failure_summary_path, failure_summary)
    return {
        "trace_summary": trace_summary,
        "failure_summary": failure_summary,
        "review_queue_count": len(review_queue),
    }


def _build_trace_findings(
    run_id: str,
    events: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    board_spec: dict[str, Any],
) -> list[dict[str, Any]]:
    price_by_key = _price_by_space_key(board_spec)
    findings: list[dict[str, Any]] = []
    for event in events:
        event_type = str(event.get("type") or "")
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        if event_type == "RENT_PAID":
            amount = _int(payload.get("amount"))
            if amount >= 100:
                findings.append(
                    _finding(
                        run_id=run_id,
                        kind="trace",
                        finding_type="large_rent_payment",
                        severity="high" if amount >= 500 else "medium",
                        confidence=1.0,
                        event=event,
                        player_id=payload.get("from_player_id"),
                        summary=f"{payload.get('from_player_id')} paid {amount} rent to {payload.get('to_player_id')}",
                        human_review_required=False,
                        details={"amount": amount, "to_player_id": payload.get("to_player_id")},
                    )
                )
        elif event_type == "AUCTION_ENDED":
            property_key = _normalize_space_key(str(payload.get("property_space") or ""))
            winning_bid = _optional_int(payload.get("winning_bid"))
            price = price_by_key.get(property_key)
            if winning_bid is not None and price is not None and winning_bid > price:
                findings.append(
                    _finding(
                        run_id=run_id,
                        kind="trace",
                        finding_type="auction_over_list_price",
                        severity="high" if winning_bid > price * 1.5 else "medium",
                        confidence=1.0,
                        event=event,
                        player_id=payload.get("winner_player_id"),
                        summary=f"{payload.get('winner_player_id')} won {property_key} for {winning_bid} over list {price}",
                        human_review_required=False,
                        details={"property_space": property_key, "winning_bid": winning_bid, "list_price": price},
                    )
                )
        elif event_type in {"TRADE_ACCEPTED", "TRADE_REJECTED", "TRADE_COUNTERED", "TRADE_PROPOSED"}:
            findings.append(
                _finding(
                    run_id=run_id,
                    kind="trace",
                    finding_type=event_type.lower(),
                    severity="medium" if event_type == "TRADE_ACCEPTED" else "low",
                    confidence=1.0,
                    event=event,
                    player_id=payload.get("initiator_player_id"),
                    summary=f"{event_type} between {payload.get('initiator_player_id')} and {payload.get('counterparty_player_id')}",
                    human_review_required=False,
                    details={"exchange_index": payload.get("exchange_index")},
                )
            )
        elif event_type == "GAME_ENDED":
            findings.append(
                _finding(
                    run_id=run_id,
                    kind="trace",
                    finding_type="game_ended",
                    severity="high",
                    confidence=1.0,
                    event=event,
                    player_id=payload.get("winner_player_id"),
                    summary=f"Game ended with winner {payload.get('winner_player_id')} due to {payload.get('reason')}",
                    human_review_required=False,
                    details={"reason": payload.get("reason")},
                )
            )
    for decision in decisions:
        if decision.get("phase") != "decision_resolved":
            continue
        if decision.get("fallback_used"):
            findings.append(
                _decision_finding(
                    run_id=run_id,
                    finding_type="fallback_used",
                    severity="high",
                    confidence=1.0,
                    decision=decision,
                    summary=f"{decision.get('player_id')} used fallback for {decision.get('decision_type')}",
                    human_review_required=False,
                    details={"fallback_reason": decision.get("fallback_reason")},
                )
            )
    return _with_ids(findings)


def _build_failure_findings(
    run_id: str,
    decisions: list[dict[str, Any]],
    trace_findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for finding in trace_findings:
        if finding["finding_type"] in {"auction_over_list_price", "large_rent_payment", "fallback_used"}:
            failures.append(_failure_from_trace(finding))
    for decision in decisions:
        if decision.get("phase") != "decision_resolved":
            continue
        if decision.get("fallback_used"):
            failures.append(
                _decision_finding(
                    run_id=run_id,
                    finding_type="fallback_used",
                    severity="high",
                    confidence=1.0,
                    decision=decision,
                    summary=f"Fallback used after {decision.get('fallback_reason')}",
                    human_review_required=False,
                    details={"fallback_reason": decision.get("fallback_reason")},
                )
            )
            if decision.get("retry_used"):
                failures.append(
                    _decision_finding(
                        run_id=run_id,
                        finding_type="retry_failed",
                        severity="high",
                        confidence=1.0,
                        decision=decision,
                        summary="Corrective retry did not produce a valid action",
                        human_review_required=False,
                        details={"fallback_reason": decision.get("fallback_reason")},
                    )
                )
        for attempt in decision.get("attempts", []):
            if not isinstance(attempt, dict):
                continue
            for error in attempt.get("validation_errors") or []:
                label = _label_from_validation_error(str(error))
                failures.append(
                    _decision_finding(
                        run_id=run_id,
                        finding_type=label,
                        severity="high" if label in {"schema_failure", "missing_tool_call", "unknown_tool"} else "medium",
                        confidence=1.0,
                        decision=decision,
                        summary=str(error),
                        human_review_required=False,
                        details={"validation_error": str(error)},
                    )
                )
    return _with_ids(failures)


def _build_review_queue(
    run_id: str,
    trace_findings: list[dict[str, Any]],
    failure_findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for finding in [*trace_findings, *failure_findings]:
        if not finding.get("human_review_required"):
            continue
        queue.append(
            {
                "schema_version": "v1",
                "review_label_version": REVIEW_LABEL_VERSION,
                "queue_item_id": f"review-{len(queue):06d}",
                "run_id": run_id,
                "decision_id": finding.get("decision_id"),
                "turn_index": finding.get("turn_index"),
                "player_id": finding.get("player_id"),
                "model_id": finding.get("model_id"),
                "finding_ids": [finding.get("finding_id")],
                "failure_ids": [finding.get("finding_id")] if finding.get("kind") == "failure" else [],
                "severity": finding.get("severity"),
                "reason_for_review": finding.get("finding_type"),
                "suggested_labels": [finding.get("finding_type")],
                "status": "unreviewed",
                "reviewer_id": "local_reviewer",
            }
        )
    return queue


def _finding(
    *,
    run_id: str,
    kind: str,
    finding_type: str,
    severity: str,
    confidence: float,
    event: dict[str, Any],
    player_id: Any,
    summary: str,
    human_review_required: bool,
    details: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "trace_analyzer_version": TRACE_ANALYZER_VERSION,
        "failure_taxonomy_version": FAILURE_TAXONOMY_VERSION,
        "kind": kind,
        "run_id": run_id,
        "finding_id": None,
        "finding_type": finding_type,
        "severity": severity,
        "confidence": confidence,
        "status": "candidate" if human_review_required else "deterministic",
        "turn_index": event.get("turn_index"),
        "decision_id": _event_decision_id(event),
        "player_id": player_id,
        "model_id": None,
        "event_seq_start": event.get("seq"),
        "event_seq_end": event.get("seq"),
        "supporting_event_ids": [event.get("event_id")],
        "supporting_decision_ids": [_event_decision_id(event)] if _event_decision_id(event) else [],
        "summary": summary,
        "details": details,
        "human_review_required": human_review_required,
        "human_review_status": "unreviewed" if human_review_required else "not_required",
        "tags": [finding_type],
    }


def _decision_finding(
    *,
    run_id: str,
    finding_type: str,
    severity: str,
    confidence: float,
    decision: dict[str, Any],
    summary: str,
    human_review_required: bool,
    details: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "trace_analyzer_version": TRACE_ANALYZER_VERSION,
        "failure_taxonomy_version": FAILURE_TAXONOMY_VERSION,
        "kind": "failure" if finding_type not in {"fallback_used"} else "trace",
        "run_id": run_id,
        "finding_id": None,
        "finding_type": finding_type,
        "severity": severity,
        "confidence": confidence,
        "status": "candidate" if human_review_required else "deterministic",
        "turn_index": decision.get("turn_index"),
        "decision_id": decision.get("decision_id"),
        "player_id": decision.get("player_id"),
        "model_id": decision.get("openrouter_model_id"),
        "event_seq_start": decision.get("emitted_event_seq_start"),
        "event_seq_end": decision.get("emitted_event_seq_end"),
        "supporting_event_ids": decision.get("emitted_event_ids", []),
        "supporting_decision_ids": [decision.get("decision_id")],
        "summary": summary,
        "details": details,
        "human_review_required": human_review_required,
        "human_review_status": "unreviewed" if human_review_required else "not_required",
        "tags": [finding_type],
    }


def _failure_from_trace(finding: dict[str, Any]) -> dict[str, Any]:
    failure = dict(finding)
    failure["kind"] = "failure"
    failure["finding_id"] = None
    return failure


def _with_ids(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for index, finding in enumerate(findings):
        finding["finding_id"] = f"{finding['kind']}-{index:06d}"
    return findings


def _summarize_findings(run_id: str, findings: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    review_required = 0
    for finding in findings:
        _increment(by_type, str(finding.get("finding_type")))
        _increment(by_severity, str(finding.get("severity")))
        if finding.get("human_review_required"):
            review_required += 1
    return {
        "schema_version": "v1",
        "trace_analyzer_version": TRACE_ANALYZER_VERSION,
        "failure_taxonomy_version": FAILURE_TAXONOMY_VERSION,
        "run_id": run_id,
        "kind": kind,
        "total_findings": len(findings),
        "review_required": review_required,
        "by_type": by_type,
        "by_severity": by_severity,
    }


def _label_from_validation_error(error: str) -> str:
    lowered = error.lower()
    if "no tool call" in lowered:
        return "missing_tool_call"
    if "exactly one tool call" in lowered or "multiple" in lowered:
        return "multiple_tool_calls"
    if "not legal" in lowered or "unknown tool" in lowered:
        return "unknown_tool"
    if "missing required public_message" in lowered:
        return "missing_required_public_message"
    if "missing required private_thought" in lowered:
        return "missing_required_private_thought"
    return "schema_failure"


def _event_decision_id(event: dict[str, Any]) -> str | None:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    value = payload.get("decision_id")
    return value if isinstance(value, str) else None


def _price_by_space_key(board_spec: dict[str, Any]) -> dict[str, int]:
    prices: dict[str, int] = {}
    for space in board_spec.get("spaces", []):
        if not isinstance(space, dict):
            continue
        name = space.get("name")
        price = space.get("price")
        if isinstance(name, str) and isinstance(price, int):
            prices[_normalize_space_key(name)] = price
    return prices


def _normalize_space_key(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    return cleaned.strip("_").upper()


def _increment(mapping: dict[str, int], key: str) -> None:
    mapping[key] = mapping.get(key, 0) + 1


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def _optional_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


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


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _resolve_repo_root() -> Path:
    start = Path(__file__).resolve()
    current = start if start.is_dir() else start.parent
    for parent in [current, *current.parents]:
        if (parent / "contracts").is_dir():
            return parent
    raise RuntimeError("Repo root not found (expected contracts/).")


def _load_board_spec() -> dict[str, Any]:
    board_path = _resolve_repo_root() / "contracts" / "data" / "board.json"
    return json.loads(board_path.read_text(encoding="utf-8"))
