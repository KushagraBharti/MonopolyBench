"""Incremental, bounded indexes over published cloud artifacts."""
from __future__ import annotations

from collections import OrderedDict
import json
from pathlib import Path
import threading
from typing import Any

from monopoly_arena.job_store import JobStore
from monopoly_telemetry.inventory import safe_path
from monopoly_telemetry.run_files import build_run_files
from .decision_index import DecisionIndex


class JobReadIndex:
    def __init__(self, store: JobStore, job: dict[str, Any]):
        self.store, self.job = store, job
        self.files: dict[str, dict[str, Any]] = {}
        self.journal_offset = 0
        self.decision_offset = 0
        self.revision = 0
        self.inventory_key: tuple[int, int] | None = None
        self.run_files = build_run_files(store.root / "runs", job["run_id"])
        self.prompt_paths: list[Path] = []
        self.decisions = DecisionIndex(self.run_files, entries=[], prompt_paths=self.prompt_paths)

    def refresh(self) -> None:
        store, job = self.store, self.job
        rows = store.rows("SELECT commit_seq,offsets_json FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job["job_id"],))
        revision = rows[0]["commit_seq"] if rows else 0
        offsets = json.loads(rows[0]["offsets_json"]) if rows else {}
        directory = store.root / "jobs" / job["job_id"]
        frozen = directory / "artifact_inventory.json"
        changed = False
        if frozen.exists():
            stat = frozen.stat()
            key = (stat.st_mtime_ns, stat.st_size)
            if key != self.inventory_key:
                self.files = {safe_path(entry["path"]): {"path": entry["path"], "bytes": entry["bytes"]} for entry in json.loads(frozen.read_text())["files"] if entry["path"] != ".writer.lock"}
                self.inventory_key = key
                changed = True
        elif revision > self.revision:
            prefix = f"runs/{job['run_id']}/"
            with (directory / "journal.jsonl").open("rb") as handle:
                handle.seek(self.journal_offset)
                while True:
                    line = handle.readline()
                    if not line or not line.endswith(b"\n"):
                        break
                    record = json.loads(line)
                    if record["journal_seq"] > revision:
                        break
                    for target in record["targets"]:
                        if target["path"].startswith(prefix):
                            name = safe_path(target["path"][len(prefix):])
                            self.files[name] = {"path": name, "bytes": target["offset"] + target["length"]}
                            changed = True
                    self.journal_offset = handle.tell()
        if changed:
            self.prompt_paths[:] = [self.run_files.run_dir / name for name in self.files if name.startswith("prompts/")]
        end = offsets.get(f"runs/{job['run_id']}/decisions.jsonl", {}).get("bytes", 0)
        if end > self.decision_offset:
            with self.run_files.decisions_path.open("rb") as handle:
                handle.seek(self.decision_offset)
                while handle.tell() < end:
                    line = handle.readline(end-handle.tell())
                    if not line.endswith(b"\n"):
                        raise ValueError("Incomplete committed decision record")
                    self.decisions.record_entry(json.loads(line))
                self.decision_offset = end
        self.revision = revision


class CloudReaders:
    def __init__(self, store: JobStore, capacity: int = 32):
        self.store, self.capacity = store, capacity
        self.indexes: OrderedDict[str, JobReadIndex] = OrderedDict()
        self.lock = threading.RLock()

    def _index(self, job: dict[str, Any]) -> JobReadIndex:
        job_id = job["job_id"]
        index = self.indexes.get(job_id)
        if index is None:
            index = JobReadIndex(self.store, job)
            self.indexes[job_id] = index
        self.indexes.move_to_end(job_id)
        while len(self.indexes) > self.capacity:
            self.indexes.popitem(last=False)
        index.refresh()
        return index

    def artifacts(self, job: dict[str, Any]) -> list[dict[str, Any]]:
        with self.lock:
            return [dict(entry) for entry in self._index(job).files.values()]

    def decisions(self, job: dict[str, Any], cursor: int) -> list[dict[str, Any]]:
        with self.lock:
            return self._index(job).decisions.ordered(limit=cursor+50)[cursor:]

    def bundle(self, job: dict[str, Any], decision_id: str) -> dict[str, Any] | None:
        with self.lock:
            return self._index(job).decisions.get_bundle(decision_id)
