from __future__ import annotations

import asyncio
import json
import os
import shutil
import signal
import subprocess
import sys
import time

from .cloud_campaign import enqueue_cells
from .cloud_preflight import preflight
from .execution_policy import data_root
from .job_store import JobStore
from .worker import writer_lock


class Supervisor:
    def __init__(self, store: JobStore):
        self.store = store
        self.children: dict[str, subprocess.Popen] = {}
        self.finalizer: subprocess.Popen | None = None

    def tick(self) -> None:
        store = self.store
        store.execute("UPDATE cells SET status=(SELECT status FROM jobs WHERE jobs.job_id=cells.job_id) WHERE job_id IS NOT NULL")
        store.execute("UPDATE campaigns SET status='done' WHERE status='running' AND EXISTS(SELECT 1 FROM cells WHERE cells.campaign_id=campaigns.campaign_id) AND NOT EXISTS(SELECT 1 FROM cells WHERE cells.campaign_id=campaigns.campaign_id AND (cells.status NOT IN ('completed','failed','cancelled') OR (cells.status='failed' AND cells.rerun_count=0)))")
        for job_id, process in list(self.children.items()):
            if process.poll() is not None:
                del self.children[job_id]
        for job in store.rows("SELECT * FROM jobs WHERE status='running'"):
            if job["job_id"] in self.children:
                continue
            try:
                with writer_lock(store.root / "runs" / job["run_id"] / ".writer.lock"):
                    store.execute("UPDATE jobs SET status='recovering' WHERE job_id=? AND status='running'", (job["job_id"],))
            except BlockingIOError:
                pass
        if self.finalizer is None or self.finalizer.poll() is not None:
            candidates = store.rows("SELECT * FROM jobs WHERE status IN ('finalizing','failed','cancelled') AND export_status IS NULL ORDER BY created_at LIMIT 1")
            candidates = [job for job in candidates if job["job_id"] not in self.children]
            if candidates:
                self.finalizer = subprocess.Popen([sys.executable, "-m", "monopoly_arena.finalizer", "--job", candidates[0]["job_id"]])
        for job in store.rows("SELECT * FROM jobs WHERE status='failed' AND kind='campaign'"):
            cell = store.rows("SELECT * FROM cells WHERE campaign_id=? AND cell_index=?", (job["campaign_id"], job["cell_index"]))[0]
            if cell["rerun_count"] == 0:
                config = json.loads(job["config_json"])
                config["run_id"] += "-rerun1"
                rerun = store.create_job(config, kind="campaign", key="rerun:"+job["job_id"], campaign_id=job["campaign_id"], cell_index=job["cell_index"], rank=job["execution_rank"], rerun_of=job["job_id"])
                store.execute("UPDATE cells SET rerun_count=1,job_id=?,status='queued' WHERE campaign_id=? AND cell_index=?", (rerun["job_id"], job["campaign_id"], job["cell_index"]))
        if store.state("drain") or store.state("account_stop"):
            return
        if shutil.disk_usage(store.root).free < float(os.getenv("MB_DISK_RESERVE_GB", "5"))*1e9:
            return
        store.execute("UPDATE jobs SET status='recovering',pause_reason=NULL WHERE status='paused' AND job_id IN (SELECT job_id FROM pauses WHERE next_retry_at<=?)", (time.time(),))
        enqueue_cells(store)
        ready = store.rows("""SELECT jobs.* FROM jobs LEFT JOIN campaigns USING(campaign_id)
            WHERE jobs.status='recovering' OR (jobs.status='queued' AND (jobs.kind='smoke' OR campaigns.status='running'))
            ORDER BY jobs.status='recovering' DESC,jobs.kind='smoke' DESC,execution_rank,jobs.created_at""")
        active = len(set(self.children) | {row["job_id"] for row in store.rows("SELECT job_id FROM jobs WHERE status='running'")})
        for job in ready:
            if job["job_id"] in self.children:
                continue
            if active >= min(5, int(os.getenv("MB_MAX_ACTIVE_GAMES", "5"))):
                break
            if job["status"] == "queued" and not store.state("preflight", {}).get("passed"):
                continue
            try:
                with writer_lock(store.root / "runs" / job["run_id"] / ".writer.lock"):
                    pass
            except BlockingIOError:
                continue
            execution = store.claim(job["job_id"])
            if execution:
                self.children[job["job_id"]] = subprocess.Popen([sys.executable, "-m", "monopoly_arena.worker", "--job", job["job_id"], "--execution", execution])
                store.audit("launch", {"job_id": job["job_id"], "execution_id": execution})
                active += 1


def main() -> None:
    store = JobStore(data_root())
    with writer_lock(store.root / ".supervisor.lock"):
        store.set_state("drain", False)
        store.execute("UPDATE jobs SET status='recovering',pause_reason=NULL WHERE status='paused' AND pause_reason='drain'")
        stopping = False

        def stop(*_: object) -> None:
            nonlocal stopping
            stopping = True
            store.set_state("drain", True)

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        asyncio.run(preflight(store))
        supervisor = Supervisor(store)
        while not stopping:
            supervisor.tick()
            time.sleep(2)
        deadline = time.monotonic() + int(os.getenv("RAILWAY_DEPLOYMENT_DRAINING_SECONDS", "180")) - 10
        while any(p.poll() is None for p in supervisor.children.values()) and time.monotonic() < deadline:
            time.sleep(1)
        for process in supervisor.children.values():
            if process.poll() is None:
                process.kill()
                process.wait()
        if supervisor.finalizer and supervisor.finalizer.poll() is None:
            supervisor.finalizer.terminate()


if __name__ == "__main__":
    main()
