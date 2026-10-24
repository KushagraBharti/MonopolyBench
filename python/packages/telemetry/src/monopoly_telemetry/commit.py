"""Durable action commits and conservative repair of interrupted append tails."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .run_files import RunFiles
from .writer_jsonl import append_jsonl


def write_commit(files: RunFiles, action: dict[str, Any], decision: dict[str, Any],
                 events: list[dict[str, Any]]) -> None:
    key = hashlib.sha256(action["decision_id"].encode()).hexdigest()
    path = files.run_dir / "commits" / f"{key}.json"
    record = {"action": action, "decision": decision, "events": events}
    if path.exists() and json.loads(path.read_text(encoding="utf-8")) != record:
        raise ValueError("Conflicting durable action commit")
    files.write_json_artifact(path, record)


def repair_committed_tails(files: RunFiles) -> None:
    """Only restore bytes represented by complete commits; reject contradictions."""
    def read(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not all(isinstance(record, dict) for record in records):
            raise ValueError("Non-object record in canonical journal")
        return records

    try:
        commits = [json.loads(path.read_text(encoding="utf-8"))
                   for path in (files.run_dir / "commits").glob("*.json")]
        commits.sort(key=lambda commit: commit["events"][0]["seq"])
        expected_by_path = (
            (files.actions_path, [commit["action"] for commit in commits], "decision_id"),
            (files.decisions_path, [commit["decision"] for commit in commits], "decision_id"),
            (files.events_path, [event for commit in commits for event in commit["events"]], "seq"),
        )
        repairs: list[tuple[Path, dict[str, Any]]] = []
        for path, expected, key in expected_by_path:
            rows = read(path)
            if path == files.decisions_path:
                rows = [row for row in rows if row.get("phase") == "decision_resolved"]
            indexed = {row[key]: row for row in rows}
            expected_ids = [row[key] for row in expected]
            if len(indexed) != len(rows) or len(set(expected_ids)) != len(expected_ids):
                raise ValueError(f"Duplicate records in {path.name} or its commits")
            expected_keys = set(expected_ids)
            if commits and key == "decision_id" and set(indexed) - expected_keys:
                raise ValueError(f"Unknown committed record in {path.name}")
            present_ids = [row[key] for row in rows if row[key] in expected_keys]
            if present_ids != expected_ids[:len(present_ids)]:
                raise ValueError(f"Missing or reordered record in {path.name} is not an append tail")
            last_seq = max(indexed, default=0) if key == "seq" else None
            for row in expected:
                prior = indexed.get(row[key])
                if prior is not None:
                    if prior != row:
                        raise ValueError(f"Conflicting committed record in {path.name}")
                else:
                    if last_seq is not None:
                        if row[key] != last_seq + 1:
                            raise ValueError("Missing event is not a contiguous append tail")
                        last_seq = row[key]
                    repairs.append((path, row))
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Malformed committed journal: {exc}") from exc

    # Validate every journal and every commit before changing any canonical bytes.
    # A write failure can leave a shorter valid prefix; rerunning remains idempotent.
    for path, row in repairs:
        append_jsonl(path, row)
