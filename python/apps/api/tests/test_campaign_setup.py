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
    # No supervisor or provider runs in this test; only the explicit control state changes.
    assert not store.rows("SELECT * FROM jobs") and not store.rows("SELECT * FROM calls")
    store.execute("UPDATE campaigns SET status='done' WHERE campaign_id=?", (campaign["campaign_id"],))
    assert client.post(path + "/run", json={}).status_code == 409
    assert client.post(path + "/pause", json={}).status_code == 409
    assert client.get(path).json()["status"] == "done"
