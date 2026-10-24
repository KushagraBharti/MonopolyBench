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
        run_id = store.job(job_id)["run_id"]
        self.allowed_roots = (self.root / "runs" / run_id, self.root / "quality_check" / run_id, self.directory / "snapshots")

    def target_path(self, name: str) -> Path:
        path = self.root / name
        if Path(name).is_absolute() or ".." in Path(name).parts or not any(path.is_relative_to(root) for root in self.allowed_roots):
            raise ValueError("Unsafe journal path")
        if any(part.is_symlink() for part in (path, *path.parents)) or not path.resolve().is_relative_to(self.root.resolve()):
            raise ValueError("Unsafe journal path")
        return path

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

    def _apply(self, record: dict[str, Any], *, repairing: bool = False) -> None:
        self.fenced()
        last = self.last()
        if record["journal_seq"] != last["commit_seq"] + 1:
            raise ValueError("Journal sequence gap")
        offsets = json.loads(last["offsets_json"])
        repairs = []
        # Validate all targets before changing any file.
        for target in record["targets"]:
            path = self.target_path(target["path"])
            data = base64.b64decode(target["data"], validate=True)
            if hashlib.sha256(data).hexdigest() != target["sha256"] or len(data) != target["length"]:
                raise ValueError("Corrupt journal payload")
            old = path.read_bytes() if path.exists() else b""
            offset = target["offset"]
            if target["append"]:
                committed = offsets.get(target["path"], {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()})
                if offset != committed["bytes"] or hashlib.sha256(old[:offset]).hexdigest() != committed["sha256"]:
                    raise ValueError(f"Committed prefix contradiction: {path}")
                if len(old) < offset or len(old) > offset+len(data) or old[offset:] != data[:len(old)-offset]:
                    raise ValueError(f"Journal contradiction: {path}")
            elif old not in (data, base64.b64decode(target["previous"])):
                raise ValueError(f"Journal overwrite contradiction: {path}")
            if repairing and ((target["append"] and len(old) < offset+len(data)) or (not target["append"] and old != data)):
                repairs.append({"path": target["path"], "start": len(old) if target["append"] else 0, "end": offset+len(data), "sha256": target["sha256"]})
        # Persist the repair intent before touching bytes. A restart after the writes
        # but before the ledger commit must retain evidence that repair was needed.
        receipt = self.directory / "recovery" / "repairs" / f"{record['journal_seq']}.json"
        if repairs and not receipt.exists():
            atomic_write(receipt, encode({"commit_seq": record["journal_seq"], "files": repairs}).encode())
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
            elif old != data:
                if old and ("/prompts/" in str(path) or "/quality_check/" in str(path)):
                    archive = path.parent / "interrupted" / f"r{self.generation}" / f"{record['journal_seq']}-{path.name}"
                    atomic_write(archive, old)
                atomic_write(path, data)
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
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT execution_id FROM executions WHERE job_id=? ORDER BY fencing_token DESC LIMIT 1", (self.job_id,)).fetchone()
            if not current or current[0] != self.execution_id:
                raise RuntimeError("Stale writer fencing token")
            db.execute("INSERT INTO commits VALUES(?,?,?,?,?,?,?,?,?,?,?)", (self.job_id, record["journal_seq"], record["journal_seq"], encode(offsets), last["last_event_seq"], last["action_count"], record["decision_id"], last["snapshot_path"], last["snapshot_sha256"], self.generation, time.time()))
            db.execute("UPDATE jobs SET last_progress_at=? WHERE job_id=?", (time.time(), self.job_id))
            if repairing and receipt.exists():
                db.execute("UPDATE jobs SET repaired=1 WHERE job_id=?", (self.job_id,))

    def recover(self) -> None:
        self.fenced()
        immutable: dict[str, dict[str, Any]] = {}
        records = []
        committed = self.last()
        if self.path.exists():
            data = self.path.read_bytes()
            if data and not data.endswith(b"\n"):
                end = data.rfind(b"\n") + 1
                tail = data[end:]
                atomic_write(self.directory / "recovery" / "quarantine" / hashlib.sha256(tail).hexdigest(), tail)
                atomic_write(self.path, data[:end])
            records = read_jsonl_strict(self.path)
        if len(records) not in {committed["commit_seq"], committed["commit_seq"] + 1}:
            raise ValueError("Journal coverage contradicts committed ledger")
        for expected, record in enumerate(records, 1):
            if record["journal_seq"] != expected:
                raise ValueError("Journal sequence gap")
            if len({t["path"] for t in record["targets"]}) != len(record["targets"]):
                raise ValueError("Duplicate journal target")
            for target in record["targets"]:
                self.target_path(target["path"])
                payload = base64.b64decode(target["data"], validate=True)
                if len(payload) != target["length"] or hashlib.sha256(payload).hexdigest() != target["sha256"]:
                    raise ValueError("Corrupt journal payload")
                if not target["append"]:
                    previous = base64.b64decode(target["previous"], validate=True)
                    if hashlib.sha256(previous).hexdigest() != target["previous_sha256"]:
                        raise ValueError("Corrupt journal previous payload")
                    if expected <= committed["commit_seq"]:
                        immutable[target["path"]] = {"bytes": target["length"], "sha256": target["sha256"]}
        pending = records[committed["commit_seq"]:]
        pending_targets = {t["path"]: t for r in pending for t in r["targets"]}
        streams = json.loads(committed["offsets_json"])
        expected_files = {**immutable, **streams}
        # Verify the old committed boundary before a pending write can replace its
        # hashes. An interrupted overwrite may already contain its new bytes.
        for name, expected in expected_files.items():
            path = self.target_path(name)
            old = path.read_bytes() if path.exists() else b""
            target = pending_targets.get(name)
            if target and name in streams:
                old = old[:expected["bytes"]]
            elif target:
                previous = base64.b64decode(target["previous"] or "")
                if len(previous) != expected["bytes"] or hashlib.sha256(previous).hexdigest() != expected["sha256"]:
                    raise ValueError(f"Committed overwrite contradiction: {name}")
                if old == base64.b64decode(target["data"]):
                    old = previous
            if not path.exists() or len(old) != expected["bytes"] or hashlib.sha256(old).hexdigest() != expected["sha256"]:
                raise ValueError(f"Committed file contradiction: {name}")
        job = self.store.job(self.job_id)
        tracked = set(expected_files) | set(pending_targets)
        for directory in (self.root / "runs" / job["run_id"], self.root / "quality_check" / job["run_id"], self.directory / "snapshots"):
            for path in directory.rglob("*"):
                if path.is_symlink():
                    raise ValueError("Symlink in canonical artifacts")
                if path.is_file() and path.name.startswith(".write-"):
                    # SIGKILL can interrupt atomic_write before rename. Preserve
                    # these bytes outside the canonical tree; they are never a
                    # source of truth for completing the journaled transition.
                    relative = path.relative_to(self.root)
                    destination = self.directory / "recovery" / "quarantine" / "temporary" / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if destination.exists():
                        destination = destination.with_name(destination.name + "-" + hashlib.sha256(path.read_bytes()).hexdigest())
                    os.replace(path, destination)
                    fsync_directory(destination.parent)
                    fsync_directory(path.parent)
                    continue
                if path.is_file() and path.name != ".writer.lock" and "interrupted" not in path.parts and path.relative_to(self.root).as_posix() not in tracked:
                    raise ValueError(f"Unjournaled canonical file: {path}")
        for record in pending:
            self._apply(record, repairing=True)

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
