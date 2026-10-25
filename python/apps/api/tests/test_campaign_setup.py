"""Campaign review/save/start boundaries without providers, supervisors or games."""
import hashlib
import json
import time

from fastapi.testclient import TestClient
import pytest

from monopoly_api.jobs_api import create_cloud_app
from monopoly_arena.cloud_campaign import enqueue_cells
from monopoly_arena.job_store import encode
from monopoly_arena.worker import build_identity
from monopoly_telemetry.export import unpack_verified


@pytest.fixture
def setup_client(tmp_path, monkeypatch):
    monkeypatch.setenv("MB_DASHBOARD_PASSWORD", "test-password")
    monkeypatch.setenv("MB_SESSION_SECRET", "s" * 64)
    monkeypatch.setenv("MB_EXPORT_TOKEN", "test-export")
    monkeypatch.delenv("MB_DEMO", raising=False)
    identity = tmp_path / "identity.json"
    identity.write_text(json.dumps({"git_sha": "preview", "image_digest": "preview-image"}))
    monkeypatch.setenv("MB_BUILD_INFO", str(identity))
    app = create_cloud_app(tmp_path / "data")
    store = app.state.store
    store.set_state("preflight", {"passed": True, "created_at": time.time(), **build_identity()})
    with TestClient(app, base_url="https://testserver") as client:
        client.post("/api/auth/login", json={"password": "test-password"})
        yield client, store, identity


def prepare(client, **overrides):
    response = client.post("/api/campaigns/prepare", json={"name": "Four full games", "seed_blocks": 1, "concurrency": 4, **overrides})
    assert response.status_code == 200, response.text
    return response.json()


def save(client, prepared, key="save-test-key"):
    return client.post("/api/campaigns/create", json={"preparation_id": prepared["preparation_id"], "idempotency_key": key})


def test_prepare_save_export_preserve_review_and_do_not_start(setup_client, tmp_path):
    client, store, _ = setup_client
    prepared = prepare(client, seed_blocks=2, concurrency=3)
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from monopoly_arena.research_registry import research_dir
    schemas = research_dir().parent / "schemas"
    registry = Registry().with_resources((p.name, Resource.from_contents(json.loads(p.read_text()))) for p in schemas.glob("*.json"))
    Draft202012Validator({"$ref": "cloud.schema.json#/$defs/campaignPreparation"}, registry=registry).validate(prepared)
    assert prepared["readiness"]["can_start"]
    assert len(prepared["cells"]) == 8 and not store.rows("SELECT * FROM campaigns")
    draw = prepared["config"]["research_freeze"]["seed_draw"]["content"]
    entropy = bytes.fromhex(draw["entropy_hex"])
    assert hashlib.sha256(entropy).hexdigest() == draw["entropy_sha256"]
    for row in draw["seeds"]:
        digest = hashlib.sha256(b"MonopolyBench/outcome-blind-seed-draw/v1\0" + draw["cohort_id"].encode() + b"\0" + entropy + row["draw_counter"].to_bytes(8, "big")).digest()
        assert digest.hex() == row["draw_digest_sha256"]
        assert int.from_bytes(digest[:4], "big") == row["seed"]
        assert row["seed"] not in draw["excluded_seeds"]
    first = save(client, prepared)
    assert first.status_code == 200, first.text
    frozen = first.json()
    assert frozen["status"] == "frozen" and frozen["config"] == prepared["config"]
    assert frozen["display_name"] == "Four full games"
    summary = client.get("/api/campaigns?summary=true").json()
    assert next(row for row in summary if row["campaign_id"] == frozen["campaign_id"]) == {
        "campaign_id": frozen["campaign_id"], "status": "frozen", "display_name": "Four full games"}
    assert len(frozen["cells"]) == 8 and all(c["job_id"] is None for c in frozen["cells"])
    assert save(client, prepared).json()["config_sha256"] == frozen["config_sha256"]
    enqueue_cells(store)
    assert not store.rows("SELECT * FROM jobs") and not store.rows("SELECT * FROM calls")
    for actual, expected in zip(frozen["cells"], prepared["cells"]):
        assert all(actual[k] == expected[k] for k in ["cell_index", "seed", "run_id", "execution_rank"])
        assert json.loads(actual["seat_order_json"]) == expected["models_by_seat"]
    export = client.post(f"/api/campaigns/{frozen['campaign_id']}/export", json={}).json()
    archive = tmp_path / "export.zip"
    archive.write_bytes(client.get(f"/api/exports/{export['export_id']}/download").content)
    unpack_verified(archive, tmp_path / "unpacked")
    evidence = json.loads((tmp_path / "unpacked/campaign.json").read_text())
    assert not evidence["jobs"] and not evidence["calls"]
    for record in frozen["config"]["research_freeze"].values():
        assert hashlib.sha256(encode(record["content"]).encode()).hexdigest() == record["sha256"]


def test_preparations_reserve_distinct_seeds_and_enforce_bounds(setup_client):
    client, _, _ = setup_client
    a = prepare(client, seed_blocks=2)
    b = prepare(client)
    assert not set(a["config"]["seeds"]) & set(b["config"]["seeds"])
    assert set(a["config"]["seeds"]) <= set(b["config"]["research_freeze"]["seed_draw"]["content"]["excluded_seeds"])
    for invalid in [{"seed_blocks": 0}, {"seed_blocks": 21}, {"seed_blocks": True}, {"concurrency": 6}, {"name": ""}, {"models": []}]:
        assert client.post("/api/campaigns/prepare", json={"name": "Test", **invalid}).status_code == 422
    assert client.post("/api/campaigns/prepare", json={"name": "   "}).status_code == 409
    assert save(client, a).status_code == 200
    assert save(client, b).status_code == 409


def test_source_change_blocks_save_and_run_without_mutating_campaign(setup_client):
    client, store, identity = setup_client
    a = prepare(client)
    frozen = save(client, a).json()
    b = prepare(client)
    identity.write_text(json.dumps({"git_sha": "new-version", "image_digest": "new-image"}))
    assert save(client, b, "second-test-key").status_code == 409
    before = store.rows("SELECT * FROM campaigns")
    campaign_id = frozen["campaign_id"]
    view = client.get(f"/api/campaigns/{campaign_id}").json()
    assert not view["readiness"]["can_start"]
    assert any("updated" in reason for reason in view["readiness"]["reasons"])
    assert client.post(f"/api/campaigns/{campaign_id}/run", json={}).status_code == 409
    assert store.rows("SELECT * FROM campaigns") == before
    assert not store.rows("SELECT * FROM jobs")


@pytest.mark.parametrize("blocker", ["account_stop", "drain", "stale_preflight", "failed_preflight", "storage", "demo"])
def test_start_rechecks_operational_readiness(setup_client, monkeypatch, blocker):
    client, store, _ = setup_client
    campaign = save(client, prepare(client)).json()
    if blocker in {"account_stop", "drain"}:
        store.set_state(blocker, True)
    elif blocker in {"stale_preflight", "failed_preflight"}:
        store.set_state("preflight", {"passed": blocker != "failed_preflight", "created_at": time.time() - 21601, **build_identity()})
    elif blocker == "demo":
        monkeypatch.setenv("MB_DEMO", "1")
    else:
        monkeypatch.setenv("MB_DISK_RESERVE_GB", "999999999")
    campaign_id = campaign["campaign_id"]
    assert client.post(f"/api/campaigns/{campaign_id}/run", json={}).status_code == 409
    assert client.get(f"/api/campaigns/{campaign_id}").json()["status"] == "frozen"
    assert not store.rows("SELECT * FROM jobs")


def test_explicit_start_is_required_and_repeat_start_is_idempotent(setup_client):
    client, store, _ = setup_client
    campaign = save(client, prepare(client)).json()
    path = f"/api/campaigns/{campaign['campaign_id']}"
    assert client.get(path).json()["status"] == "frozen"
    assert client.post(path + "/run", json={}).json()["status"] == "running"
    assert client.post(path + "/run", json={}).json()["status"] == "running"
    # Start materializes all board links immediately; no supervisor or provider runs.
    assert len(store.rows("SELECT * FROM jobs")) == 4 and not store.rows("SELECT * FROM calls")
    store.execute("UPDATE campaigns SET status='done' WHERE campaign_id=?", (campaign["campaign_id"],))
    assert client.post(path + "/run", json={}).status_code == 409
    assert client.post(path + "/pause", json={}).status_code == 409
    assert client.get(path).json()["status"] == "done"


def test_campaign_start_returns_every_board_and_individual_controls(setup_client):
    client, store, _ = setup_client
    saved = save(client, prepare(client)).json()
    path = f"/api/campaigns/{saved['campaign_id']}"
    response = client.post(path + "/run", json={})
    assert response.status_code == 200
    games = [cell["game"] for cell in response.json()["cells"]]
    assert len(games) == 4 and len({game["job_id"] for game in games}) == 4
    for game in games:
        assert game["status"] == "queued" and game["snapshot_kind"] == "initial_preview"
        assert len(game["snapshot"]["board"]) == 40 and len(game["snapshot"]["players"]) == 4
        assert game["allowed_actions"] == ["pause", "cancel"]
    assert not store.rows("SELECT * FROM commits") and not store.rows("SELECT * FROM calls")


def test_campaign_and_individual_pause_resume_and_cancel(setup_client):
    client, store, _ = setup_client
    saved = save(client, prepare(client)).json()
    path = f"/api/campaigns/{saved['campaign_id']}"
    cell_index = saved["cells"][0]["cell_index"]
    one = client.post(f"{path}/cells/{cell_index}/start", json={}).json()
    assert len(store.rows("SELECT * FROM jobs")) == 1
    assert one["status"] == "frozen"  # starting one does not authorize the other three
    job_id = next(c["job_id"] for c in one["cells"] if c["job_id"])
    assert store.state("individual_start:" + job_id)
    assert client.post(path + "/pause", json={}).status_code == 200
    assert store.job(job_id)["pause_reason"] == "campaign_operator"
    assert not store.state("individual_start:" + job_id)
    assert client.post(path + "/run", json={}).status_code == 200
    assert len(store.rows("SELECT * FROM jobs")) == 4
    assert store.job(job_id)["status"] == "recovering"
    assert client.post(f"/api/jobs/{job_id}/pause", json={}).status_code == 200
    assert store.job(job_id)["pause_reason"] == "operator"
    assert client.post(path + "/pause", json={}).status_code == 200
    assert client.post(path + "/run", json={}).status_code == 200
    assert store.job(job_id)["status"] == "paused"  # preserve an individual pause
    others = store.rows("SELECT * FROM jobs WHERE job_id!=?", (job_id,))
    assert all(j["status"] == "recovering" for j in others)
    assert client.post(path + "/pause", json={}).status_code == 200
    assert client.post(f"/api/jobs/{job_id}/resume", json={}).status_code == 200
    assert store.state("individual_start:" + job_id)
    assert client.get(path).json()["status"] == "paused"
    cancelled = client.post(path + "/cancel", json={}).json()
    assert cancelled["status"] == "cancelled"
    assert all(j["status"] == "cancelled" for j in store.rows("SELECT * FROM jobs"))
    assert client.post(path + "/run", json={}).status_code == 409
    assert client.post(f"{path}/cells/{cell_index}/start", json={}).status_code == 409
    assert not store.rows("SELECT * FROM calls")


def test_cancel_unstarted_campaign_keeps_records_and_creates_no_jobs(setup_client):
    client, store, _ = setup_client
    saved = save(client, prepare(client)).json()
    response = client.post(f"/api/campaigns/{saved['campaign_id']}/cancel", json={})
    assert response.status_code == 200
    assert all(cell["status"] == "cancelled" and not cell["allowed_actions"] for cell in response.json()["cells"])
    assert not store.rows("SELECT * FROM jobs")
    assert response.json()["config_sha256"] == saved["config_sha256"]


@pytest.mark.parametrize("turns,effort", [(None, "high"), (1, "low"), (300, "medium")])
def test_single_game_settings_launch_and_initial_board(setup_client, turns, effort):
    client, store, _ = setup_client
    response = client.post("/api/games/prepare", json={"effort": effort, "max_turns": turns, "cost_budget": 2.5})
    assert response.status_code == 200, response.text
    prepared = response.json()
    assert not store.rows("SELECT * FROM jobs")
    payload = {"preparation_id": prepared["preparation_id"], "idempotency_key": "single-launch-key"}
    first = client.post("/api/games", json=payload)
    second = client.post("/api/games", json=payload)
    assert first.status_code == second.status_code == 200
    job = first.json()[0]
    assert job["job_id"] == second.json()[0]["job_id"]
    assert job["kind"] == "single" and job["campaign_id"] is None
    assert job["config"]["max_turns"] == turns and job["config"]["cost_budget"] == 2.5
    assert all(p["reasoning"]["effort"] == effort for p in job["config"]["players"])
    assert len(job["snapshot"]["board"]) == 40 and job["snapshot_kind"] == "initial_preview"
    assert len(store.rows("SELECT * FROM jobs")) == 1 and not store.rows("SELECT * FROM calls")
    assert client.post("/api/smoke", json=payload).status_code == 409


def test_smoke_settings_and_budget_validation(setup_client):
    client, store, _ = setup_client
    for invalid in [{"cost_budget": 0}, {"cost_budget": -1}, {"cost_budget": True}, {"cost_budget": "Infinity"}, {"max_turns": 0}, {"max_turns": 10001}]:
        assert client.post("/api/games/prepare", json=invalid).status_code == 422
    prepared = client.post("/api/smoke/prepare", json={"effort": "low", "max_turns": 10, "count": 2, "cost_budget": 1}).json()
    configs = prepared["configs"]
    assert len(configs) == 2 and all(c["cost_budget"] == 1 and c["max_turns"] == 10 for c in configs)
    assert not store.rows("SELECT * FROM jobs")
    assert client.post("/api/games/prepare", json={"effort": "invalid"}).status_code == 409


def test_shared_campaign_budget_blocks_remaining_starts_and_resume(setup_client):
    client, store, _ = setup_client
    prepared = prepare(client, cost_budget=0.1)
    saved = save(client, prepared).json()
    assert saved["config"]["cost_budget"] == 0.1
    assert saved["config"]["max_turns"] is None
    path = f"/api/campaigns/{saved['campaign_id']}"
    cell = saved["cells"][0]
    one = client.post(f"{path}/cells/{cell['cell_index']}/start", json={}).json()
    job_id = next(c["job_id"] for c in one["cells"] if c["job_id"])
    store.execute("INSERT INTO calls(call_id,job_id,state,total_cost,cost_status) VALUES('spent',?,'responded',0.12,'known')", (job_id,))
    assert not client.get(path).json()["readiness"]["can_start"]
    assert client.post(path + "/run", json={}).status_code == 409
    assert len(store.rows("SELECT * FROM jobs")) == 1
    assert client.post(f"/api/jobs/{job_id}/pause", json={}).status_code == 200
    assert client.post(f"/api/jobs/{job_id}/resume", json={}).status_code == 409
    from monopoly_arena.campaign_controls import pause_shared_budget
    pause_shared_budget(store, job_id)
    assert client.get(path).json()["status"] == "paused"


def test_live_board_stream_uses_full_committed_engine_snapshots(setup_client):
    from monopoly_arena.journal import Journal
    from monopoly_engine import Engine
    client, store, _ = setup_client
    preparation = client.post("/api/games/prepare", json={"max_turns": 5}).json()
    job = client.post("/api/games", json={"preparation_id": preparation["preparation_id"], "idempotency_key": "live-board-preview"}).json()[0]
    config = job["config"]
    engine = Engine(seed=config["seed"], run_id=config["run_id"], players=config["players"], max_turns=5)
    journal = Journal(store, job["job_id"], store.claim(job["job_id"]))
    with journal.transition("initialize", snapshot=engine.get_snapshot()):
        pass
    with client.websocket_connect(f"wss://testserver/api/jobs/{job['job_id']}/ws") as socket:
        assert socket.receive_json()["type"] == "HELLO"
        first = socket.receive_json()
        assert len(first["snapshot"]["board"]) == 40
        _, events, _, _ = engine.advance_until_decision(max_steps=100)
        with journal.transition("advance", snapshot=engine.get_snapshot()):
            for event in events:
                journal.write(store.root / "runs" / config["run_id"] / "events.jsonl", (encode(event) + "\n").encode(), append=True)
        updated = socket.receive_json()
        assert updated["commit_seq"] > first["commit_seq"]
        assert updated["snapshot"] == engine.get_snapshot()
        assert updated["events"] == events
        assert len(updated["snapshot"]["players"]) == 4 and events
    committed = client.get(f"/api/jobs/{job['job_id']}").json()
    assert committed["snapshot_kind"] == "committed"
    assert not store.rows("SELECT * FROM calls")
