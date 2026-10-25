"""Campaign admission and scheduling tests without workers or provider calls."""

import json
from pathlib import Path
import time

import pytest

from monopoly_arena.campaign_controls import (
    cancel_campaign,
    pause_campaign,
    run_campaign,
    start_cell,
)
from monopoly_arena.cloud_campaign import enqueue_cells, freeze, run_config
from monopoly_arena.job_store import JobStore
from monopoly_arena.journal import Journal
from monopoly_arena.supervisor import Supervisor
from monopoly_arena.worker import build_identity, writer_lock


@pytest.fixture
def store(tmp_path, monkeypatch):
    identity_file = tmp_path / "build.json"
    identity_file.write_text(json.dumps({"git_sha": "test", "image_digest": "test"}))
    monkeypatch.setenv("MB_BUILD_INFO", str(identity_file))
    monkeypatch.setenv("MB_DISK_RESERVE_GB", "0")
    monkeypatch.setenv("MB_MAX_ACTIVE_GAMES", "5")
    ledger = JobStore(tmp_path / "data")
    ledger.set_state("preflight", {"passed": True, "created_at": time.time(), **build_identity()})
    return ledger


@pytest.fixture
def processes(monkeypatch):
    children = []

    class Child:
        def __init__(self, command):
            self.command = command
            self.returncode = None
            children.append(self)

        def poll(self):
            return self.returncode

    # Patch subprocess itself so neither worker nor finalizer can spawn a process.
    monkeypatch.setattr("monopoly_arena.supervisor.subprocess.Popen", Child)
    return children


@pytest.fixture
def campaign(store, processes):
    config = json.loads(
        (Path(__file__).resolve().parents[4] / "campaigns" / "monopoly-long-v2-frontier-2026q4.json").read_text()
    )
    config.update(campaign_id="controls-test", seeds=[1], execution_order_seed=42, concurrency=2)
    freeze(store, config)
    return config["campaign_id"]


def cells(store, campaign):
    return store.rows("SELECT * FROM cells WHERE campaign_id=? ORDER BY cell_index", (campaign,))


def jobs(store):
    return store.rows("SELECT * FROM jobs ORDER BY cell_index")


def workers(processes):
    return [child for child in processes if "monopoly_arena.worker" in child.command]


def test_run_materializes_all_four_jobs_without_launching(store, campaign, processes):
    assert len(cells(store, campaign)) == 4
    assert not jobs(store)
    run_campaign(store, campaign)
    original = jobs(store)
    assert len(original) == 4
    assert {job["status"] for job in original} == {"queued"}
    assert {cell["job_id"] for cell in cells(store, campaign)} == {job["job_id"] for job in original}
    assert not processes
    assert not store.rows("SELECT * FROM executions")
    run_campaign(store, campaign)
    assert jobs(store) == original


@pytest.mark.parametrize("status", ["running", "paused", "frozen"])
def test_finished_campaign_reaches_done_even_when_paused(store, campaign, processes, status):
    run_campaign(store, campaign)
    store.execute("UPDATE jobs SET status='completed',export_status='ready'")
    store.execute("UPDATE campaigns SET status=?", (status,))
    Supervisor(store).tick()
    assert store.rows("SELECT status FROM campaigns")[0]["status"] == "done"
    assert not processes


@pytest.mark.parametrize("status", ["queued", "paused", "finalizing", "failed"])
def test_paused_campaign_with_unfinished_cell_stays_paused(store, campaign, processes, status):
    run_campaign(store, campaign)
    store.execute("UPDATE jobs SET status='completed',export_status='ready'")
    job = jobs(store)[0]
    store.execute("UPDATE jobs SET status=? WHERE job_id=?", (status, job["job_id"]))
    store.execute("UPDATE campaigns SET status='paused'")
    Supervisor(store).tick()
    assert store.rows("SELECT status FROM campaigns")[0]["status"] == "paused"
    assert not workers(processes)


@pytest.mark.parametrize("campaign_status", ["frozen", "paused"])
def test_individual_start_is_idempotent_and_admitted_without_campaign_run(
    store, campaign, processes, campaign_status
):
    store.execute("UPDATE campaigns SET status=?", (campaign_status,))
    start_cell(store, campaign, 2)
    original = jobs(store)
    start_cell(store, campaign, 2)
    assert jobs(store) == original
    assert len(original) == 1
    job = original[0]
    assert job["cell_index"] == 2
    assert store.state("individual_start:" + job["job_id"]) is True
    assert store.rows("SELECT status FROM campaigns")[0]["status"] == campaign_status
    assert not processes
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    assert len(workers(processes)) == 1
    assert len(store.rows("SELECT * FROM executions")) == 1
    assert len(jobs(store)) == 1


def test_pause_gates_campaign_before_pausing_jobs_and_preserves_manual_pause(
    store, campaign, monkeypatch, processes
):
    run_campaign(store, campaign)
    queued, running, recovering, manual = jobs(store)
    store.claim(running["job_id"])
    store.execute("UPDATE jobs SET status='recovering' WHERE job_id=?", (recovering["job_id"],))
    store.pause(manual["job_id"], "operator", "keep this game paused")
    manual_pause = store.rows("SELECT * FROM pauses WHERE job_id=?", (manual["job_id"],))
    for job in jobs(store):
        store.set_state("individual_start:" + job["job_id"], True)
    pause = store.pause
    observed = []

    def gated_pause(job_id, reason):
        observed.append(store.rows("SELECT status FROM campaigns")[0]["status"])
        pause(job_id, reason)

    monkeypatch.setattr(store, "pause", gated_pause)
    pause_campaign(store, campaign)
    assert observed == ["paused"] * 3
    assert store.rows("SELECT * FROM pauses WHERE job_id=?", (manual["job_id"],)) == manual_pause
    for job in (queued, running, recovering):
        current = store.job(job["job_id"])
        assert (current["status"], current["pause_reason"]) == ("paused", "campaign_operator")
    assert all(store.state("individual_start:" + job["job_id"]) is False for job in jobs(store))
    Supervisor(store).tick()
    assert not workers(processes)


def test_run_resumes_only_campaign_operator_pauses(store, campaign, processes):
    run_campaign(store, campaign)
    campaign_job, manual, outage, budget = jobs(store)
    for job, reason in ((manual, "operator"), (outage, "provider_unavailable"), (budget, "budget")):
        store.pause(job["job_id"], reason)
    pause_campaign(store, campaign)
    preserved = store.rows("SELECT * FROM pauses WHERE job_id!=? ORDER BY job_id", (campaign_job["job_id"],))
    run_campaign(store, campaign)
    assert store.job(campaign_job["job_id"])["status"] == "recovering"
    assert store.job(campaign_job["job_id"])["pause_reason"] is None
    assert store.rows("SELECT * FROM pauses WHERE job_id!=? ORDER BY job_id", (campaign_job["job_id"],)) == preserved
    assert all(store.job(job["job_id"])["status"] == "paused" for job in (manual, outage, budget))
    assert not processes


def test_busy_writer_defers_campaign_resume_then_fences_old_execution(store, campaign, processes):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    original_execution = store.claim(job["job_id"])
    old_journal = Journal(store, job["job_id"], original_execution)
    pause_campaign(store, campaign)
    supervisor = Supervisor(store)
    with writer_lock(store.root / "runs" / job["run_id"] / ".writer.lock"):
        run_campaign(store, campaign)
        # Leave a slot for this recovery after its writer releases the lock.
        for other in jobs(store):
            if other["job_id"] != job["job_id"]:
                store.pause(other["job_id"], "operator")
        supervisor.tick()
        assert store.job(job["job_id"])["status"] == "paused"
        assert store.job(job["job_id"])["pause_reason"] == "campaign_operator"
        assert len(store.rows("SELECT * FROM executions WHERE job_id=?", (job["job_id"],))) == 1
        assert job["job_id"] not in supervisor.children
        old_journal.fenced()
    supervisor.tick()
    assert job["job_id"] in supervisor.children
    executions = store.rows("SELECT * FROM executions WHERE job_id=? ORDER BY fencing_token", (job["job_id"],))
    assert [execution["fencing_token"] for execution in executions] == [1, 2]
    assert store.state("resume_epoch:" + job["job_id"]) == 1
    with pytest.raises(RuntimeError, match="Stale writer fencing token"):
        old_journal.fenced()


@pytest.mark.parametrize("individual", [False, True])
def test_paused_campaign_outage_recovery_requires_individual_override(store, campaign, processes, individual):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    store.execute("UPDATE campaigns SET status='paused'")
    store.set_state("individual_start:" + job["job_id"], individual)
    store.pause(job["job_id"], "provider_unavailable")
    store.execute("UPDATE pauses SET next_retry_at=0 WHERE job_id=?", (job["job_id"],))
    supervisor = Supervisor(store)
    supervisor.tick()
    assert store.job(job["job_id"])["status"] == ("running" if individual else "paused")
    assert len(workers(processes)) == int(individual)


def test_individual_resume_flag_admits_paused_campaign_job(store, campaign, processes):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    pause_campaign(store, campaign)
    # Mirrors the API resume contract; API request handling belongs to its tests.
    store.resume(job["job_id"])
    store.set_state("individual_start:" + job["job_id"], True)
    Supervisor(store).tick()
    assert store.job(job["job_id"])["status"] == "running"
    assert len(workers(processes)) == 1
    assert len(jobs(store)) == 1


def test_live_paused_children_keep_campaign_slots_until_exit(store, campaign, processes):
    run_campaign(store, campaign)
    supervisor = Supervisor(store)
    supervisor.tick()
    assert len(workers(processes)) == 2
    first_ids = set(supervisor.children)
    pause_campaign(store, campaign)
    run_campaign(store, campaign)
    supervisor.tick()
    assert len(workers(processes)) == 2
    assert set(supervisor.children) == first_ids
    for job_id in first_ids:
        store.pause(job_id, "operator")
        supervisor.children[job_id].returncode = 0
    supervisor.tick()
    assert len(workers(processes)) == 4
    assert not first_ids & set(supervisor.children)
    assert len(supervisor.children) == 2


def test_global_concurrency_includes_individually_started_and_single_jobs(
    store, campaign, processes, monkeypatch
):
    monkeypatch.setenv("MB_MAX_ACTIVE_GAMES", "1")
    start_cell(store, campaign, 0)
    single = store.create_job(run_config(9, "single-test"), kind="single", key="single-test", rank=-1)
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    assert list(supervisor.children) == [single["job_id"]]
    assert len(workers(processes)) == 1
    store.execute("UPDATE jobs SET status='completed' WHERE job_id=?", (single["job_id"],))
    supervisor.children[single["job_id"]].returncode = 0
    supervisor.tick()
    assert len(workers(processes)) == 2
    assert len(supervisor.children) == 1


@pytest.mark.parametrize("status", ["queued", "running", "recovering", "paused"])
def test_cancel_stops_active_and_unmaterialized_games(store, campaign, processes, status):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    store.execute("UPDATE jobs SET status=? WHERE job_id=?", (status, job["job_id"]))
    cancel_campaign(store, campaign)
    assert store.job(job["job_id"])["status"] == "cancelled"
    assert store.job(job["job_id"])["ended_at"] is not None
    assert store.state("individual_start:" + job["job_id"]) is None
    assert all(cell["status"] == "cancelled" for cell in cells(store, campaign) if cell["job_id"] is None)
    enqueue_cells(store)
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    assert len(jobs(store)) == 1
    assert not workers(processes)
    assert {cell["status"] for cell in cells(store, campaign)} == {"cancelled"}
    with pytest.raises(ValueError, match="cancelled"):
        start_cell(store, campaign, 1)


def test_cancelled_campaign_suppresses_failed_job_rerun(store, campaign, processes):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    store.execute("UPDATE jobs SET status='failed' WHERE job_id=?", (job["job_id"],))
    cancel_campaign(store, campaign)
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    assert len(jobs(store)) == 1
    assert store.job(job["job_id"])["status"] == "failed"
    assert not store.rows("SELECT * FROM jobs WHERE rerun_of_job_id IS NOT NULL")
    assert not workers(processes)


def test_cancelled_campaign_remains_terminal_after_run_request(store, campaign, processes):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    store.execute("UPDATE jobs SET status='failed' WHERE job_id=?", (job["job_id"],))
    cancel_campaign(store, campaign)
    try:
        run_campaign(store, campaign)
    except ValueError:
        pass  # Rejecting the request or leaving cancellation intact are both safe.
    supervisor = Supervisor(store)
    supervisor.tick()
    assert store.rows("SELECT status FROM campaigns")[0]["status"] == "cancelled"
    assert len(jobs(store)) == 1
    assert not workers(processes)


@pytest.mark.parametrize("individual", [False, True])
def test_technical_rerun_retains_original_and_same_seed_seats_once(store, campaign, processes, individual):
    if individual:
        start_cell(store, campaign, 0)
    else:
        run_campaign(store, campaign)
    original = jobs(store)[0]
    store.execute("UPDATE jobs SET status='failed' WHERE job_id=?", (original["job_id"],))
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    reruns = store.rows("SELECT * FROM jobs WHERE rerun_of_job_id=?", (original["job_id"],))
    assert len(reruns) == 1
    rerun = reruns[0]
    assert rerun["job_id"] != original["job_id"]
    config = json.loads(original["config_json"])
    assert json.loads(rerun["config_json"]) == {**config, "run_id": original["run_id"] + "-rerun1"}
    assert rerun["seed"] == original["seed"]
    assert rerun["execution_rank"] == original["execution_rank"]
    assert bool(store.state("individual_start:" + rerun["job_id"])) is individual
    assert store.job(original["job_id"]) == original | {"status": "failed"}
    cell = cells(store, campaign)[original["cell_index"]]
    assert (cell["job_id"], cell["rerun_count"]) == (rerun["job_id"], 1)
    # A second technical failure consumes no further retry or replacement job.
    store.execute("UPDATE jobs SET status='failed' WHERE job_id=?", (rerun["job_id"],))
    supervisor.tick()
    assert len(store.rows("SELECT * FROM jobs WHERE rerun_of_job_id IS NOT NULL")) == 1


def test_completed_game_does_not_get_strategic_rerun(store, campaign, processes):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    store.execute("UPDATE jobs SET status='completed' WHERE job_id=?", (job["job_id"],))
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    assert len(jobs(store)) == 1
    assert not workers(processes)
    with pytest.raises(ValueError, match="finished"):
        start_cell(store, campaign, 0)


def test_cancel_between_validation_and_start_cannot_reopen(store, campaign, monkeypatch):
    import monopoly_arena.campaign_controls as controls
    original = controls._controllable

    def cancel_after_check(current_store, campaign_id, *, starting=False):
        original(current_store, campaign_id, starting=starting)
        if starting:
            cancel_campaign(current_store, campaign_id)

    monkeypatch.setattr(controls, "_controllable", cancel_after_check)
    with pytest.raises(ValueError, match="cancelled"):
        run_campaign(store, campaign)
    assert store.rows("SELECT status FROM campaigns")[0]["status"] == "cancelled"
    assert not jobs(store)


def test_cancel_between_cell_selection_and_job_insertion_creates_nothing(store, campaign, monkeypatch):
    original = store.create_job
    cancelled = False

    def cancel_before_insert(*args, **kwargs):
        nonlocal cancelled
        if not cancelled:
            cancel_campaign(store, campaign)
            cancelled = True
        return original(*args, **kwargs)

    monkeypatch.setattr(store, "create_job", cancel_before_insert)
    run_campaign(store, campaign)
    assert store.rows("SELECT status FROM campaigns")[0]["status"] == "cancelled"
    assert not jobs(store)


def test_terminal_campaign_job_lookup_remains_idempotent(store, campaign):
    start_cell(store, campaign, 0)
    job = jobs(store)[0]
    cancel_campaign(store, campaign)
    repeated = store.create_job(json.loads(job["config_json"]), kind="campaign", key=job["idempotency_key"], campaign_id=campaign)
    assert repeated["job_id"] == job["job_id"] and repeated["status"] == "cancelled"
    assert len(jobs(store)) == 1
