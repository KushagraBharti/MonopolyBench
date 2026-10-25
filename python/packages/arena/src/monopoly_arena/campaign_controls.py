"""Operator controls preserve worker locks and individually paused games."""
from __future__ import annotations

import time
import json

from .cloud_campaign import enqueue_cells, create_cell_job
from .job_store import JobStore


def _controllable(store: JobStore, campaign_id: str, *, starting: bool = False) -> None:
    rows = store.rows("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,))
    if not rows:
        raise KeyError(campaign_id)
    campaign = rows[0]
    if campaign["status"] not in {"frozen", "paused", "running"}:
        raise ValueError("This campaign has finished or was cancelled.")
    if starting:
        from .worker import build_identity
        identity = build_identity()
        if any(campaign[key] != identity[key] for key in ("git_sha", "image_digest")):
            raise ValueError("The app version changed. Create a new campaign before starting games.")


def pause_campaign(store: JobStore, campaign_id: str) -> None:
    _controllable(store, campaign_id)
    # Gate admission first, then request boundary pauses. In-flight calls can finish.
    with store.connect() as db:
        changed = db.execute("UPDATE campaigns SET status='paused' WHERE campaign_id=? AND status IN ('frozen','running','paused')", (campaign_id,)).rowcount
        if not changed:
            raise ValueError("This campaign has finished or was cancelled.")
    for job in store.rows("SELECT * FROM jobs WHERE campaign_id=?", (campaign_id,)):
        store.set_state("individual_start:" + job["job_id"], False)
        if job["status"] in {"queued", "running", "recovering"}:
            store.pause(job["job_id"], "campaign_operator")
    store.audit("campaign_pause", {"campaign_id": campaign_id}, "dashboard")


def run_campaign(store: JobStore, campaign_id: str) -> None:
    _controllable(store, campaign_id, starting=True)
    with store.connect() as db:
        changed = db.execute("UPDATE campaigns SET status='running' WHERE campaign_id=? AND status IN ('frozen','running','paused')", (campaign_id,)).rowcount
        if not changed:
            raise ValueError("This campaign has finished or was cancelled.")
    # Materialize all games now so every board link is available in the response.
    enqueue_cells(store)
    resume_campaign_jobs(store, campaign_id)
    store.audit("campaign_run", {"campaign_id": campaign_id}, "dashboard")


def resume_campaign_jobs(store: JobStore, campaign_id: str) -> None:
    for job in store.rows("SELECT job_id FROM jobs WHERE campaign_id=? AND status='paused' AND pause_reason='campaign_operator'", (campaign_id,)):
        try:
            store.resume(job["job_id"])
        except ValueError:
            # The supervisor retries after the old writer exits; never steal its lock.
            pass


def start_cell(store: JobStore, campaign_id: str, cell_index: int) -> None:
    _controllable(store, campaign_id, starting=True)
    rows = store.rows("SELECT * FROM cells WHERE campaign_id=? AND cell_index=?", (campaign_id, cell_index))
    if not rows:
        raise KeyError(cell_index)
    cell = rows[0]
    if cell["status"] == "cancelled":
        raise ValueError("This game was cancelled and cannot be started.")
    job = store.job(cell["job_id"]) if cell["job_id"] else create_cell_job(store, cell)
    from .budget import budget_status
    budget = budget_status(store, job["job_id"])
    if budget["blocked"]:
        raise ValueError(budget["detail"])
    if job["status"] not in {"queued", "paused", "recovering", "running"}:
        raise ValueError("This game has finished and cannot be restarted.")
    if job["status"] == "paused":
        store.resume(job["job_id"])
    store.set_state("individual_start:" + job["job_id"], True)
    store.audit("campaign_cell_start", {"campaign_id": campaign_id, "cell_index": cell_index, "job_id": job["job_id"]}, "dashboard")


def cancel_campaign(store: JobStore, campaign_id: str) -> None:
    _controllable(store, campaign_id)
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE campaigns SET status='cancelled' WHERE campaign_id=?", (campaign_id,))
        db.execute("UPDATE jobs SET status='cancelled',ended_at=? WHERE campaign_id=? AND status IN ('queued','running','recovering','paused')", (time.time(), campaign_id))
        db.execute("UPDATE cells SET status='cancelled' WHERE campaign_id=? AND job_id IS NULL", (campaign_id,))
        for job in db.execute("SELECT job_id FROM jobs WHERE campaign_id=?", (campaign_id,)):
            db.execute("DELETE FROM account_state WHERE key=?", ("individual_start:" + job[0],))
    store.audit("campaign_cancel", {"campaign_id": campaign_id}, "dashboard")


def pause_shared_budget(store: JobStore, job_id: str) -> None:
    """One exhausted shared threshold holds every game, including queued jobs."""
    job = store.job(job_id)
    if not job["campaign_id"]:
        return
    rows = store.rows("SELECT config_json,status FROM campaigns WHERE campaign_id=?", (job["campaign_id"],))
    if rows and rows[0]["status"] in {"frozen", "running", "paused"} and json.loads(rows[0]["config_json"]).get("cost_budget") is not None:
        pause_campaign(store, job["campaign_id"])
