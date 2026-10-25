"""Resume all clears the account stop but keeps operator and campaign holds paused."""
import json
from jsonschema import Draft202012Validator
from monopoly_arena.cloud_campaign import run_config
from monopoly_arena.research_registry import research_dir
from monopoly_arena.worker import writer_lock

from test_campaign_setup import prepare, save


def smoke(store, name, **config):
    job = store.create_job({**run_config(len(name) * 7919, name, max_turns=5), **config}, kind="smoke", key=name)
    return job["job_id"]


def add_call(store, job_id, call_id, amount, status="known"):
    store.execute("INSERT INTO calls(call_id,job_id,state,total_cost,cost_status) VALUES(?,?,'responded',?,?)",
                  (call_id, job_id, amount, status))


def campaign_jobs(client, store, key="resume-all-key", **overrides):
    saved = save(client, prepare(client, **overrides), key=key).json()
    path = f"/api/campaigns/{saved['campaign_id']}"
    assert client.post(path + "/run", json={}).status_code == 200
    jobs = [row["job_id"] for row in store.rows("SELECT job_id FROM jobs WHERE campaign_id=? ORDER BY cell_index", (saved["campaign_id"],))]
    return path, jobs


def resume_all(client):
    response = client.post("/api/resume-all", json={})
    assert response.status_code == 200, response.text
    body = response.json()
    schema = json.loads((research_dir().parent / "schemas/cloud.schema.json").read_text())
    Draft202012Validator(schema["$defs"]["resumeAllResult"]).validate(body)
    return body, {entry["job_id"]: entry["reasons"] for entry in body["skipped"]}


def test_account_pauses_recover_and_operator_pauses_stay(setup_client):
    client, store, _ = setup_client
    account, operator = smoke(store, "account-paused"), smoke(store, "operator-paused")
    store.pause(account, "account_error", "402")
    store.pause(operator, "operator")
    assert store.state("account_stop")
    body, skipped = resume_all(client)
    assert store.state("account_stop") is None
    assert store.job(account)["status"] == "recovering"
    assert store.job(operator)["status"] == "paused" and store.job(operator)["pause_reason"] == "operator"
    assert list(skipped) == [operator] and body["waiting_for_worker"] == []
    assert client.get(f"/api/jobs/{operator}").json()["allowed_actions"] == ["resume", "cancel"]


def test_paused_campaign_children_stay_paused_and_resumable(setup_client):
    client, store, _ = setup_client
    path, jobs = campaign_jobs(client, store)
    account, held = jobs[0], jobs[1]
    store.pause(account, "account_error", "401")
    assert client.post(path + "/pause", json={}).status_code == 200
    assert store.job(held)["pause_reason"] == "campaign_operator"
    assert store.job(account)["pause_reason"] == "account_error"
    body, skipped = resume_all(client)
    assert store.state("account_stop") is None
    # Neither child becomes an unadmittable 'recovering' job under a paused campaign.
    assert set(skipped) == set(jobs) and body["waiting_for_worker"] == []
    for job_id in jobs:
        assert store.job(job_id)["status"] == "paused"
        assert not store.state("individual_start:" + job_id)
        assert client.get(f"/api/jobs/{job_id}").json()["allowed_actions"] == ["resume", "cancel"]
    assert client.post(f"/api/jobs/{account}/resume", json={}).status_code == 200
    assert store.job(account)["status"] == "recovering" and store.state("individual_start:" + account)
    assert client.post(path + "/run", json={}).status_code == 200
    assert store.job(held)["status"] == "recovering"


def test_running_or_individually_started_campaign_jobs_recover(setup_client):
    client, store, _ = setup_client
    path, jobs = campaign_jobs(client, store)
    store.pause(jobs[0], "account_error", "401")
    store.pause(jobs[1], "credit_admission", "in flight")
    _, skipped = resume_all(client)
    assert not skipped
    assert store.job(jobs[0])["status"] == store.job(jobs[1])["status"] == "recovering"

    second_path, other = campaign_jobs(client, store, key="resume-all-second")
    cell = client.get(second_path).json()["cells"][2]["cell_index"]
    assert client.post(second_path + "/pause", json={}).status_code == 200
    assert client.post(f"{second_path}/cells/{cell}/start", json={}).status_code == 200
    started = store.rows("SELECT job_id FROM cells WHERE campaign_id=? AND cell_index=?", (second_path.rsplit("/", 1)[1], cell))[0]["job_id"]
    store.pause(started, "account_error", "401")
    _, skipped = resume_all(client)
    assert started not in skipped and store.job(started)["status"] == "recovering"
    assert set(other) - {started} <= set(skipped)


def test_drain_disk_and_code_mismatch_keep_games_paused(setup_client, monkeypatch, tmp_path):
    client, store, identity = setup_client
    job = smoke(store, "guarded")
    store.pause(job, "account_error", "401")
    store.set_state("drain", True)
    _, skipped = resume_all(client)
    assert store.state("account_stop") is None and store.job(job)["status"] == "paused"
    assert any("maintenance" in reason for reason in skipped[job])
    store.set_state("drain", False)
    monkeypatch.setenv("MB_DISK_RESERVE_GB", "1e12")
    _, skipped = resume_all(client)
    assert store.job(job)["status"] == "paused" and any("Storage" in reason for reason in skipped[job])
    monkeypatch.delenv("MB_DISK_RESERVE_GB")
    identity.write_text('{"git_sha": "newer", "image_digest": "newer-image"}')
    _, skipped = resume_all(client)
    assert store.job(job)["status"] == "paused" and any("app was updated" in reason for reason in skipped[job])


def test_job_shared_and_unknown_budgets_fail_closed(setup_client):
    client, store, _ = setup_client
    spent, unknown = smoke(store, "spent", cost_budget=0.05), smoke(store, "unknown", cost_budget=5.0)
    add_call(store, spent, "spent-1", 0.10)
    add_call(store, unknown, "unknown-1", None, "missing")
    path, jobs = campaign_jobs(client, store, seed_blocks=1, cost_budget=0.05)
    add_call(store, jobs[3], "shared-1", 0.10)
    for job_id in (spent, unknown, *jobs):
        store.pause(job_id, "account_error", "402")
    _, skipped = resume_all(client)
    assert set(skipped) == {spent, unknown, *jobs}
    assert all(store.job(job_id)["status"] == "paused" for job_id in skipped)
    assert any("missing or unknown cost" in reason for reason in skipped[unknown])
    assert client.post(f"/api/jobs/{jobs[0]}/resume", json={}).status_code == 409


def test_demo_mode_resumes_test_games_only(setup_client, monkeypatch):
    client, store, _ = setup_client
    _, jobs = campaign_jobs(client, store)
    test_game = smoke(store, "demo-smoke")
    store.pause(test_game, "account_error", "401")
    store.pause(jobs[0], "account_error", "401")
    monkeypatch.setenv("MB_DEMO", "1")
    _, skipped = resume_all(client)
    assert store.job(test_game)["status"] == "recovering"
    assert store.job(jobs[0])["status"] == "paused" and any("Demo mode" in reason for reason in skipped[jobs[0]])


def test_live_writer_is_reported_as_waiting(setup_client):
    client, store, _ = setup_client
    job = smoke(store, "busy-writer")
    store.pause(job, "provider_unavailable", "503")
    with writer_lock(store.root / "runs" / store.job(job)["run_id"] / ".writer.lock"):
        body, skipped = resume_all(client)
    assert body["waiting_for_worker"] == [job] and not skipped
    assert store.job(job)["status"] == "paused"
