"""Write-ahead byte journal. A commit publishes an entire engine transition."""
from __future__ import annotations

import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Iterator

from monopoly_telemetry.run_files import RunFiles, build_run_files
from monopoly_telemetry.writer_jsonl import append_jsonl, atomic_write, fsync_directory, read_jsonl_strict
from .job_store import JobStore, encode


class Journal:
    def __init__(self, store: JobStore, job_id: str, execution_id: str):
        self.store, self.job_id, self.execution_id = store, job_id, execution_id
        self.root = store.root
        self.directory = self.root / "jobs" / job_id
        self.path = self.directory / "journal.jsonl"
        self.pending: dict[str, dict[str, Any]] | None = None
        self.generation = store.rows("SELECT recovery_generation FROM executions WHERE execution_id=?", (execution_id,))[0]["recovery_generation"]

    def last(self) -> dict[str, Any]:
        rows = self.store.rows("SELECT * FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (self.job_id,))
        return rows[0] if rows else {"commit_seq": 0, "offsets_json": "{}", "last_event_seq": -1, "action_count": 0, "snapshot_path": None, "snapshot_sha256": None}

    def fenced(self) -> None:
        rows = self.store.rows("SELECT execution_id FROM executions WHERE job_id=? ORDER BY fencing_token DESC LIMIT 1", (self.job_id,))
        if not rows or rows[0]["execution_id"] != self.execution_id:
            raise RuntimeError("Stale writer fencing token")

    @contextmanager
    def transition(self, kind: str, decision_id: str | None = None, snapshot: dict | None = None) -> Iterator[None]:
        if self.pending is not None:
            raise RuntimeError("Nested journal transition")
        self.pending = {}
        try:
            yield
            self.fenced()
            last = self.last()
            seq = last["commit_seq"] + 1
            if snapshot is not None:
                self.write(self.directory / "snapshots" / f"{seq}.json", encode(snapshot).encode())
            targets = list(self.pending.values())
            record = {"journal_seq": seq, "kind": kind, "decision_id": decision_id,
                      "recovery_generation": self.generation, "targets": targets}
            append_jsonl(self.path, record)
            self._apply(record)
        finally:
            self.pending = None

    def write(self, path: Path, data: bytes, append: bool = False) -> None:
        if self.pending is None:
            with self.transition("artifact"):
                self.write(path, data, append)
            return
        name = path.relative_to(self.root).as_posix()
        if name in self.pending:
            prior = self.pending[name]
            old = base64.b64decode(prior["data"])
            if append:
                data = old + data
            prior.update(data=base64.b64encode(data).decode(), length=len(data), sha256=hashlib.sha256(data).hexdigest())
            return
        existing = path.read_bytes() if path.exists() else b""
        if not append and existing == data:
            return
        # Overwrites preserve their exact previous bytes in the durable record.
        self.pending[name] = {"path": name, "offset": len(existing) if append else 0,
                              "previous_sha256": hashlib.sha256(existing).hexdigest() if not append else None,
                              "previous": base64.b64encode(existing).decode() if not append else None,
                              "length": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                              "data": base64.b64encode(data).decode(), "append": append}

    def _apply(self, record: dict[str, Any]) -> None:
        last = self.last()
        offsets = json.loads(last["offsets_json"])
        repairs = []
        # Validate all targets before changing any file.
        for target in record["targets"]:
            path = self.root / target["path"]
            if path.resolve().is_relative_to(self.root.resolve()) is False or path.is_symlink():
                raise ValueError("Unsafe journal path")
            data = base64.b64decode(target["data"], validate=True)
            if hashlib.sha256(data).hexdigest() != target["sha256"] or len(data) != target["length"]:
                raise ValueError("Corrupt journal payload")
            old = path.read_bytes() if path.exists() else b""
            offset = target["offset"]
            if target["append"]:
                if len(old) < offset or len(old) > offset+len(data) or old[offset:] != data[:len(old)-offset]:
                    raise ValueError(f"Journal contradiction: {path}")
            elif old not in (data, base64.b64decode(target["previous"])):
                raise ValueError(f"Journal overwrite contradiction: {path}")
        for target in record["targets"]:
            path = self.root / target["path"]
            data = base64.b64decode(target["data"])
            old = path.read_bytes() if path.exists() else b""
            if target["append"]:
                offset = target["offset"]
                if len(old) < offset+len(data):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("ab") as handle:
                        handle.write(data[len(old)-offset:])
                        handle.flush()
                        os.fsync(handle.fileno())
                    fsync_directory(path.parent)
                    repairs.append({"path": target["path"], "start": len(old), "end": offset+len(data), "sha256": target["sha256"]})
            elif old != data:
                if old and ("/prompts/" in str(path) or "/quality_check/" in str(path)):
                    archive = path.parent / "interrupted" / f"r{self.generation}" / f"{record['journal_seq']}-{path.name}"
                    atomic_write(archive, old)
                atomic_write(path, data)
                repairs.append({"path": target["path"], "start": 0, "end": len(data), "sha256": target["sha256"]})
            # Only append streams need offsets in every commit. Immutable file hashes
            # live in the journal, avoiding quadratic ledger growth as prompts accumulate.
            if target["append"]:
                offsets[target["path"]] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            if path.name == "events.jsonl":
                events = [json.loads(line) for line in data.splitlines()]
                if events:
                    last["last_event_seq"] = events[-1].get("seq", events[-1].get("event_seq", -1))
            if path.name == "actions.jsonl":
                last["action_count"] += len(data.splitlines())
            if path.parent == self.directory / "snapshots":
                last["snapshot_path"], last["snapshot_sha256"] = target["path"], target["sha256"]
        self.fenced()
        with self.store.connect() as db:
            db.execute("INSERT INTO commits VALUES(?,?,?,?,?,?,?,?,?,?,?)", (self.job_id, record["journal_seq"], record["journal_seq"], encode(offsets), last["last_event_seq"], last["action_count"], record["decision_id"], last["snapshot_path"], last["snapshot_sha256"], self.generation, time.time()))
            db.execute("UPDATE jobs SET last_progress_at=? WHERE job_id=?", (time.time(), self.job_id))
        if self.generation and repairs:
            append_jsonl(self.directory / "recovery" / "repairs.jsonl", {"commit_seq": record["journal_seq"], "files": repairs})
            self.store.execute("UPDATE jobs SET repaired=1 WHERE job_id=?", (self.job_id,))

    def recover(self) -> None:
        immutable: dict[str, dict[str, Any]] = {}
        if self.path.exists():
            data = self.path.read_bytes()
            if data and not data.endswith(b"\n"):
                end = data.rfind(b"\n") + 1
                tail = data[end:]
                atomic_write(self.directory / "recovery" / "quarantine" / hashlib.sha256(tail).hexdigest(), tail)
                atomic_write(self.path, data[:end])
            records = read_jsonl_strict(self.path)
            for expected, record in enumerate(records, 1):
                if record["journal_seq"] != expected:
                    raise ValueError("Journal sequence gap")
                for target in record["targets"]:
                    payload = base64.b64decode(target["data"], validate=True)
                    if len(payload) != target["length"] or hashlib.sha256(payload).hexdigest() != target["sha256"]:
                        raise ValueError("Corrupt journal payload")
                    if not target["append"]:
                        immutable[target["path"]] = {"bytes": target["length"], "sha256": target["sha256"]}
                if expected > self.last()["commit_seq"]:
                    self._apply(record)
        expected_files = {**immutable, **json.loads(self.last()["offsets_json"])}
        for name, expected in expected_files.items():
            path = self.root / name
            if not path.exists() or path.stat().st_size != expected["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
                raise ValueError(f"Committed file contradiction: {name}")
        job = self.store.job(self.job_id)
        tracked = set(expected_files)
        for directory in (self.root / "runs" / job["run_id"], self.root / "quality_check" / job["run_id"]):
            for path in directory.rglob("*"):
                if path.is_symlink():
                    raise ValueError("Symlink in canonical artifacts")
                if path.is_file() and path.name != ".writer.lock" and "interrupted" not in path.parts and path.relative_to(self.root).as_posix() not in tracked:
                    raise ValueError(f"Unjournaled canonical file: {path}")

    def compact(self) -> None:
        records = read_jsonl_strict(self.path)
        index = []
        for record in records:
            for target in record["targets"]:
                target.pop("data", None)
                target.pop("previous", None)
            index.append(encode(record))
        atomic_write(self.directory / "journal_index.jsonl", ("\n".join(index)+"\n").encode())
        # Keep the journal until the immutable package is published; deletion is a separate operation.


class JournalRunFiles(RunFiles):
    journal: Journal

    @classmethod
    def create(cls, journal: Journal, run_id: str) -> JournalRunFiles:
        result = cls(**vars(build_run_files(journal.root / "runs", run_id)))
        result.journal = journal
        return result

    def _write_text(self, path: Path, text: str, encoding: str = "utf-8") -> None:
        self.journal.write(path, text.encode(encoding))

    def _append(self, path: Path, row: dict[str, Any]) -> None:
        self.journal.write(path, (json.dumps(row, separators=(",", ":"), ensure_ascii=True)+"\n").encode(), append=True)

    def write_event(self, event: dict[str, Any]) -> None:
        self._append(self.events_path, event)

    def write_action(self, action_entry: dict[str, Any]) -> None:
        self._append(self.actions_path, action_entry)

    def write_decision(self, decision_entry: dict[str, Any]) -> None:
        self._append(self.decisions_path, decision_entry)

    def write_prompt_artifacts(self, **kwargs: Any) -> None:
        with self.journal.transition("prompt", kwargs.get("decision_id")):
            super().write_prompt_artifacts(**kwargs)

    def write_quality_artifacts(self, **kwargs: Any) -> None:
        with self.journal.transition("wire", kwargs.get("decision_id")):
            super().write_quality_artifacts(**kwargs)
