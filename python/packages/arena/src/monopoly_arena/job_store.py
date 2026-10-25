"""Short, serialized SQLite transactions; files hold research evidence."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import re
import time
from typing import Any, Iterator
import uuid

from monopoly_telemetry.writer_jsonl import atomic_write

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
 job_id TEXT PRIMARY KEY, run_id TEXT UNIQUE NOT NULL, kind TEXT NOT NULL,
 campaign_id TEXT, cell_index INTEGER, execution_rank INTEGER DEFAULT 0,
 rerun_of_job_id TEXT, config_json TEXT NOT NULL, config_sha256 TEXT NOT NULL,
 seed INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'queued', pause_reason TEXT,
 outcome_json TEXT, replay_status TEXT, analysis_status TEXT, export_status TEXT,
 repaired INTEGER DEFAULT 0, recovered INTEGER DEFAULT 0, git_sha TEXT NOT NULL,
 image_digest TEXT NOT NULL, idempotency_key TEXT UNIQUE, created_at REAL NOT NULL,
 started_at REAL, ended_at REAL, last_progress_at REAL, archived INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS executions (
 execution_id TEXT PRIMARY KEY, job_id TEXT NOT NULL, fencing_token INTEGER NOT NULL,
 pid INTEGER, started_at REAL, heartbeat_at REAL, ended_at REAL, exit_status TEXT,
 recovery_generation INTEGER DEFAULT 0, reason TEXT);
CREATE TABLE IF NOT EXISTS commits (
 job_id TEXT, commit_seq INTEGER, journal_seq INTEGER, offsets_json TEXT,
 last_event_seq INTEGER, action_count INTEGER, decision_id TEXT, snapshot_path TEXT,
 snapshot_sha256 TEXT, recovery_generation INTEGER, committed_at REAL,
 PRIMARY KEY(job_id, commit_seq));
CREATE TABLE IF NOT EXISTS calls (
 call_id TEXT PRIMARY KEY, job_id TEXT, decision_id TEXT, resolver_stage INTEGER,
 transport_attempt INTEGER, recovery_epoch INTEGER, state TEXT, http_status INTEGER,
 error_type TEXT, model_returned TEXT, provider_returned TEXT, generation_id TEXT,
 is_byok INTEGER, usage_cost REAL, upstream_cost REAL, total_cost REAL,
 cost_status TEXT, created_at REAL, completed_at REAL);
CREATE TABLE IF NOT EXISTS pauses (
 job_id TEXT PRIMARY KEY, reason TEXT, retries_used INTEGER DEFAULT 0,
 next_retry_at REAL, since REAL, detail_json TEXT);
CREATE TABLE IF NOT EXISTS account_state (key TEXT PRIMARY KEY, value_json TEXT, updated_at REAL);
CREATE TABLE IF NOT EXISTS campaigns (
 campaign_id TEXT PRIMARY KEY, config_json TEXT, config_sha256 TEXT, status TEXT,
 frozen_at REAL, git_sha TEXT, image_digest TEXT);
CREATE TABLE IF NOT EXISTS cells (
 campaign_id TEXT, cell_index INTEGER, run_id TEXT, seed INTEGER, seat_order_json TEXT,
 execution_rank INTEGER, status TEXT, job_id TEXT, rerun_count INTEGER DEFAULT 0,
 not_started_reason TEXT, PRIMARY KEY(campaign_id, cell_index));
CREATE TABLE IF NOT EXISTS campaign_amendments (
 campaign_id TEXT, amendment_index INTEGER, reason TEXT, diff_json TEXT,
 affected_cells_json TEXT, created_at REAL, PRIMARY KEY(campaign_id, amendment_index));
CREATE TABLE IF NOT EXISTS exports (
 export_id TEXT PRIMARY KEY, scope TEXT, scope_id TEXT, revision INTEGER, kind TEXT,
 path TEXT, bytes INTEGER, manifest_sha256 TEXT, created_at REAL);
CREATE UNIQUE INDEX IF NOT EXISTS exports_scope_revision ON exports(scope,scope_id,revision);
-- Per-job and campaign-wide ledger reads (cost, budget, readiness) must not scan every call.
CREATE INDEX IF NOT EXISTS calls_job ON calls(job_id);
CREATE INDEX IF NOT EXISTS jobs_campaign ON jobs(campaign_id);
CREATE TABLE IF NOT EXISTS audit (ts REAL, actor TEXT, action TEXT, detail_json TEXT);
PRAGMA user_version=1;
"""


def encode(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class CampaignClosed(ValueError):
    """Admission lost a race with terminal campaign cancellation/completion."""


class JobStore:
    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.root / "ledger.sqlite", timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def rows(self, sql: str, args: tuple = ()) -> list[dict[str, Any]]:
        with self.connect() as db:
            return [dict(row) for row in db.execute(sql, args)]

    def execute(self, sql: str, args: tuple = ()) -> None:
        with self.connect() as db:
            db.execute(sql, args)

    def job(self, job_id: str) -> dict[str, Any]:
        rows = self.rows("SELECT * FROM jobs WHERE job_id=?", (job_id,))
        if not rows:
            raise KeyError(job_id)
        return rows[0]

    def state(self, key: str, default: Any = None) -> Any:
        rows = self.rows("SELECT value_json FROM account_state WHERE key=?", (key,))
        return json.loads(rows[0]["value_json"]) if rows else default

    def set_state(self, key: str, value: Any) -> None:
        self.execute("INSERT OR REPLACE INTO account_state VALUES(?,?,?)", (key, encode(value), time.time()))

    def audit(self, action: str, detail: Any, actor: str = "system") -> None:
        self.execute("INSERT INTO audit VALUES(?,?,?,?)", (time.time(), actor, action, encode(detail)))

    def create_job(self, config: dict[str, Any], *, kind: str, key: str,
                   campaign_id: str | None = None, cell_index: int | None = None,
                   rank: int = 0, rerun_of: str | None = None) -> dict[str, Any]:
        raw = encode(config)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        job_id = uuid.uuid4().hex
        run_id = config["run_id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id) or campaign_id is not None and not re.fullmatch(r"[A-Za-z0-9_-]+", campaign_id):
            raise ValueError("Unsafe run or campaign ID")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM jobs WHERE idempotency_key=?", (key,)).fetchone()
            if old:
                if old["config_sha256"] != digest:
                    raise ValueError("Idempotency key reused with different configuration")
                return dict(old)
            if campaign_id is not None:
                campaign = db.execute("SELECT status FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
                if campaign and campaign[0] in {"cancelled", "done"}:
                    raise CampaignClosed("This campaign has finished or was cancelled.")
            db.execute("""INSERT INTO jobs(job_id,run_id,kind,campaign_id,cell_index,execution_rank,
                rerun_of_job_id,config_json,config_sha256,seed,git_sha,image_digest,idempotency_key,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (job_id, run_id, kind, campaign_id, cell_index, rank, rerun_of, raw, digest,
                 config["seed"], config["git_sha"], config["image_digest"], key, time.time()))
        job = self.job(job_id)
        atomic_write(self.root / "jobs" / job_id / "job.json", encode(job).encode())
        return job

    def claim(self, job_id: str) -> str | None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row[0] not in {"queued", "recovering"}:
                return None
            token = db.execute("SELECT COALESCE(MAX(fencing_token),0)+1 FROM executions WHERE job_id=?", (job_id,)).fetchone()[0]
            execution = uuid.uuid4().hex
            db.execute("INSERT INTO executions(execution_id,job_id,fencing_token,started_at,heartbeat_at,recovery_generation) VALUES(?,?,?,?,?,?)",
                       (execution, job_id, token, time.time(), time.time(), token-1))
            db.execute("UPDATE jobs SET status='running',started_at=COALESCE(started_at,?) WHERE job_id=?", (time.time(), job_id))
            return execution

    def pause(self, job_id: str, reason: str, detail: str = "", *, expected_status: str | None = None) -> None:
        from .execution_policy import OUTAGE_INTERVAL, OUTAGE_RETRIES
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            job = db.execute("SELECT status,pause_reason FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not job:
                raise KeyError(job_id)
            if expected_status is not None and job["status"] != expected_status:
                raise ValueError("Job state changed; refresh before retrying")
            if job["status"] in {"cancelled", "failed", "completed", "finalizing"}:
                return
            if job["status"] == "paused" and job["pause_reason"] in {"operator", "campaign_operator", "drain"}:
                return
            old = db.execute("SELECT retries_used FROM pauses WHERE job_id=?", (job_id,)).fetchone()
            retries = old[0] + 1 if old else 0
            retry_at = time.time() + OUTAGE_INTERVAL if reason in {"provider_unavailable", "credit_admission"} and retries < OUTAGE_RETRIES else None
            db.execute("INSERT OR REPLACE INTO pauses VALUES(?,?,?,?,?,?)", (job_id, reason, retries, retry_at, time.time(), encode({"detail": detail})))
            db.execute("UPDATE jobs SET status='paused',pause_reason=? WHERE job_id=? AND status NOT IN ('cancelled','failed','completed')", (reason, job_id))
        if reason == "account_error":
            self.set_state("account_stop", {"reason": reason, "detail": detail})

    def resume(self, job_id: str) -> None:
        # A paused status is a boundary request, not proof that the writer has
        # exited. Keep its lock until the old execution records its final state.
        from .worker import writer_lock
        job = self.job(job_id)
        try:
            with writer_lock(self.root / "runs" / job["run_id"] / ".writer.lock"):
                self._resume_unlocked(job_id)
        except BlockingIOError as exc:
            raise ValueError("Worker is finishing its current request; retry resume after it stops") from exc

    def _resume_unlocked(self, job_id: str) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row or row[0] != "paused":
                raise ValueError("Only paused jobs can be resumed")
            key = "resume_epoch:" + job_id
            row = db.execute("SELECT value_json FROM account_state WHERE key=?", (key,)).fetchone()
            epoch = json.loads(row[0]) + 1 if row else 1
            db.execute("INSERT OR REPLACE INTO account_state VALUES(?,?,?)", (key, encode(epoch), time.time()))
            db.execute("DELETE FROM pauses WHERE job_id=?", (job_id,))
            db.execute("UPDATE jobs SET status='recovering',pause_reason=NULL WHERE job_id=? AND status='paused'", (job_id,))
