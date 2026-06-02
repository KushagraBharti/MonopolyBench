from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from .run_files import RunFiles
from .writer_jsonl import append_jsonl


REVIEW_LABEL_VERSION = "review_label_v1"
REVIEW_SUMMARY_VERSION = "review_summary_v1"
DEFAULT_REVIEWER_ID = "local_reviewer"


def append_review_label(run_files: RunFiles, payload: dict[str, Any]) -> dict[str, Any]:
    label = normalize_review_label(run_files, payload)
    append_jsonl(run_files.review_labels_path, label)
    summary = build_review_summary(run_files)
    run_files.write_json_artifact(run_files.review_summary_path, summary)
    return label


def normalize_review_label(run_files: RunFiles, payload: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    reviewer_id = payload.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        reviewer_id = DEFAULT_REVIEWER_ID
    selected_labels = payload.get("selected_labels")
    if not isinstance(selected_labels, list):
        selected_labels = []
    selected_labels = [str(label) for label in selected_labels if isinstance(label, str) and label.strip()]
    evidence_references = payload.get("evidence_references")
    if not isinstance(evidence_references, list):
        evidence_references = []
    label = {
        "schema_version": "v1",
        "label_version": REVIEW_LABEL_VERSION,
        "label_id": str(payload.get("label_id") or _label_id(run_files.run_id, payload, now)),
        "run_id": run_files.run_id,
        "queue_item_id": payload.get("queue_item_id"),
        "reviewer_id": reviewer_id,
        "reviewed_at": str(payload.get("reviewed_at") or now),
        "selected_labels": selected_labels,
        "confidence": payload.get("confidence"),
        "notes": payload.get("notes") if isinstance(payload.get("notes"), str) else "",
        "adjudication_status": str(payload.get("adjudication_status") or "unadjudicated"),
        "gold_label": bool(payload.get("gold_label", False)),
        "evidence_references": evidence_references,
    }
    return label


def build_review_summary(run_files: RunFiles) -> dict[str, Any]:
    labels = read_review_labels(run_files)
    by_label: dict[str, int] = {}
    by_reviewer: dict[str, int] = {}
    gold_label_count = 0
    for label in labels:
        reviewer_id = str(label.get("reviewer_id") or DEFAULT_REVIEWER_ID)
        by_reviewer[reviewer_id] = by_reviewer.get(reviewer_id, 0) + 1
        if label.get("gold_label"):
            gold_label_count += 1
        selected = label.get("selected_labels")
        if not isinstance(selected, list):
            continue
        for item in selected:
            label_id = str(item)
            by_label[label_id] = by_label.get(label_id, 0) + 1
    return {
        "schema_version": "v1",
        "review_summary_version": REVIEW_SUMMARY_VERSION,
        "run_id": run_files.run_id,
        "label_count": len(labels),
        "gold_label_count": gold_label_count,
        "by_label": by_label,
        "by_reviewer": by_reviewer,
    }


def read_review_labels(run_files: RunFiles) -> list[dict[str, Any]]:
    if not run_files.review_labels_path.exists():
        return []
    labels: list[dict[str, Any]] = []
    for line in run_files.review_labels_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            labels.append(parsed)
    return labels


def _label_id(run_id: str, payload: dict[str, Any], reviewed_at: str) -> str:
    source = json.dumps(
        {
            "run_id": run_id,
            "queue_item_id": payload.get("queue_item_id"),
            "reviewer_id": payload.get("reviewer_id") or DEFAULT_REVIEWER_ID,
            "reviewed_at": reviewed_at,
            "selected_labels": payload.get("selected_labels"),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]
    return f"review_label_{digest}"
