from __future__ import annotations

import asyncio
from collections import Counter
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from typing import Callable

from .cloud_campaign import enqueue_cells
from .campaign_controls import resume_campaign_jobs
from .cloud_preflight import preflight
from .execution_policy import data_root, MAX_ACTIVE_GAMES, DEFAULT_ACTIVE_GAMES
from .job_store import JobStore, CampaignClosed
from .worker import writer_lock


class Supervisor:
    def __init__(self, store: JobStore):
        self.store = store
        self.children: dict[str, subprocess.Popen] = {}
        self.finalizer: subprocess.Popen | None = None

    def tick(self) -> None:
        store = self.store
        store.execute("UPDATE cells SET status=(SELECT status FROM jobs WHERE jobs.job_id=cells.job_id) WHERE job_id IS NOT NULL")
        store.execute("UPDATE campaigns SET status='done' WHERE status IN ('running','paused','frozen') AND EXISTS(SELECT 1 FROM cells WHERE cells.campaign_id=campaigns.campaign_id) AND NOT EXISTS(SELECT 1 FROM cells WHERE cells.campaign_id=campaigns.campaign_id AND (cells.status NOT IN ('completed','failed','cancelled') OR (cells.status='failed' AND cells.rerun_count=0)))")
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
            candidates = store.rows("SELECT * FROM jobs WHERE status IN ('finalizing','failed','cancelled') AND export_status IS NULL ORDER BY created_at")
            for candidate in candidates:
                if candidate["job_id"] in self.children or store.state("finalize_retry:" + candidate["job_id"], 0) > time.time():
                    continue
                try:
                    with writer_lock(store.root / "runs" / candidate["run_id"] / ".writer.lock"):
                        pass
                except BlockingIOError:
                    continue
                self.finalizer = subprocess.Popen([sys.executable, "-m", "monopoly_arena.finalizer", "--job", candidate["job_id"]])
                break
        for job in store.rows("SELECT jobs.* FROM jobs JOIN campaigns USING(campaign_id) WHERE jobs.status='failed' AND jobs.kind='campaign' AND campaigns.status!='cancelled'"):
            cell = store.rows("SELECT * FROM cells WHERE campaign_id=? AND cell_index=?", (job["campaign_id"], job["cell_index"]))[0]
            if cell["rerun_count"] == 0:
                config = json.loads(job["config_json"])
                config["run_id"] += "-rerun1"
                try:
                    rerun = store.create_job(config, kind="campaign", key="rerun:"+job["job_id"], campaign_id=job["campaign_id"], cell_index=job["cell_index"], rank=job["execution_rank"], rerun_of=job["job_id"])
                except CampaignClosed:
                    continue
                store.execute("UPDATE cells SET rerun_count=1,job_id=?,status='queued' WHERE campaign_id=? AND cell_index=?", (rerun["job_id"], job["campaign_id"], job["cell_index"]))
                if store.state("individual_start:" + job["job_id"]):
                    store.set_state("individual_start:" + rerun["job_id"], True)
        if store.state("drain") or store.state("account_stop"):
            return
        if shutil.disk_usage(store.root).free < float(os.getenv("MB_DISK_RESERVE_GB", "5"))*1e9:
            return
        for campaign in store.rows("SELECT campaign_id FROM campaigns WHERE status='running'"):
            resume_campaign_jobs(store, campaign["campaign_id"])
        store.execute("""UPDATE jobs SET status='recovering',pause_reason=NULL WHERE status='paused'
            AND job_id IN (SELECT job_id FROM pauses WHERE next_retry_at<=?)
            AND (campaign_id IS NULL OR campaign_id IN (SELECT campaign_id FROM campaigns WHERE status='running')
                 OR EXISTS(SELECT 1 FROM account_state WHERE key='individual_start:'||jobs.job_id AND value_json='true'))""", (time.time(),))
        enqueue_cells(store)
        ready = store.rows("""SELECT jobs.* FROM jobs LEFT JOIN campaigns USING(campaign_id)
            WHERE jobs.status IN ('recovering','queued') AND (jobs.kind IN ('smoke','single') OR campaigns.status='running'
                OR EXISTS(SELECT 1 FROM account_state WHERE key='individual_start:'||jobs.job_id AND value_json='true'))
            ORDER BY jobs.status='recovering' DESC,jobs.kind='smoke' DESC,execution_rank,jobs.created_at""")
        running = store.rows("SELECT job_id,campaign_id FROM jobs WHERE status='running'")
        # A live child still occupies its slot after a pause request, until its process exits.
        live = set(self.children) | {row["job_id"] for row in running}
        active = len(live)
        # A frozen campaign's concurrency also bounds its simultaneous games and paid requests.
        campaign_limits = {row["campaign_id"]: int(json.loads(row["config_json"]).get("concurrency") or 1)
                           for row in store.rows("SELECT campaign_id,config_json FROM campaigns")}
        live_campaigns = store.rows(f"SELECT job_id,campaign_id FROM jobs WHERE job_id IN ({','.join('?' * len(live))})",
                                    tuple(live)) if live else []
        campaign_active = Counter(row["campaign_id"] for row in live_campaigns if row["campaign_id"])
        for job in ready:
            if job["job_id"] in self.children:
                continue
            if active >= min(MAX_ACTIVE_GAMES, int(os.getenv("MB_MAX_ACTIVE_GAMES", str(DEFAULT_ACTIVE_GAMES)))):
                break
            campaign_id = job["campaign_id"]
            if campaign_id and campaign_active[campaign_id] >= campaign_limits.get(campaign_id, 1):
                continue
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
                if campaign_id:
                    campaign_active[campaign_id] += 1


async def run_supervisor(store: JobStore, stopping: Callable[[], bool]) -> None:
    # Preflight can take minutes. Keep recovery and the drain signal responsive
    # while new jobs remain gated on a fresh successful report.
    store.set_state("preflight", {"passed": False, "status": "running"})
    check = asyncio.create_task(preflight(store))
    supervisor = Supervisor(store)
    try:
        while not stopping():
            supervisor.tick()
            await asyncio.sleep(2)
    finally:
        check.cancel()
        await asyncio.gather(check, return_exceptions=True)
        deadline = time.monotonic() + max(0, int(os.getenv("RAILWAY_DEPLOYMENT_DRAINING_SECONDS", "180")) - 10)
        processes = list(supervisor.children.values())
        if supervisor.finalizer:
            processes.append(supervisor.finalizer)
        while any(p.poll() is None for p in processes) and time.monotonic() < deadline:
            await asyncio.sleep(0.5)
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.wait()


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
        asyncio.run(run_supervisor(store, lambda: stopping))


if __name__ == "__main__":
    main()
