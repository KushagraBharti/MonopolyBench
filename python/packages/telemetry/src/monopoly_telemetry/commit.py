"""Durable action commits and conservative repair of interrupted append tails."""
from __future__ import annotations

import hashlib
import json
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
    def read(path):
        if not path.exists():
            return []
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not all(isinstance(record, dict) for record in records):
            raise ValueError("Non-object record in canonical journal")
        return records

    commits = [json.loads(path.read_text(encoding="utf-8"))
               for path in (files.run_dir / "commits").glob("*.json")]
    commits.sort(key=lambda commit: commit["events"][0]["seq"])
    for commit in commits:
        for path, expected, key in (
            (files.actions_path, [commit["action"]], "decision_id"),
            (files.decisions_path, [commit["decision"]], "decision_id"),
            (files.events_path, commit["events"], "seq"),
        ):
            rows = read(path)
            if path == files.decisions_path:
                rows = [row for row in rows if row.get("phase") == "decision_resolved"]
            indexed = {row[key]: row for row in rows}
            if len(indexed) != len(rows):
                raise ValueError(f"Duplicate records in {path.name}")
            for row in expected:
                prior = indexed.get(row[key])
                if prior is not None:
                    if prior != row:
                        raise ValueError(f"Conflicting committed record in {path.name}")
                else:
                    if key == "seq" and indexed and row[key] <= max(indexed):
                        raise ValueError("Missing event is not an append tail")
                    append_jsonl(path, row)
                    indexed[row[key]] = row
