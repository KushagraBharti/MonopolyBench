from fastapi.testclient import TestClient
import pytest

from monopoly_api.jobs_api import create_cloud_app


@pytest.fixture
def cloud(tmp_path, monkeypatch):
    monkeypatch.setenv("MB_DASHBOARD_PASSWORD", "password")
    monkeypatch.setenv("MB_SESSION_SECRET", "s" * 64)
    monkeypatch.setenv("MB_EXPORT_TOKEN", "export-secret")
    app = create_cloud_app(tmp_path)
    with TestClient(app, base_url="https://testserver") as client:
        yield client, app.state.store


def test_cloud_auth_token_scope_csrf_and_legacy_controls(cloud):
    client, _ = cloud
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/jobs").status_code == 401
    export = {"Authorization": "Bearer export-secret"}
    assert client.get("/api/exports", headers=export).status_code == 200
    assert client.get("/api/jobs", headers=export).status_code == 401
    assert client.post("/api/resume-all", headers=export).status_code == 401
    response = client.post("/api/auth/login", json={"password": "password"})
    assert response.status_code == 200
    assert "Secure" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]
    assert client.get("/api/jobs").status_code == 200
    assert client.post("/api/resume-all", headers={"origin": "https://evil.example"}).status_code == 403
    assert client.post("/run/start", json={}).status_code in {404, 405}
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/jobs").status_code == 401


def test_login_rate_limit(cloud):
    client, _ = cloud
    for _ in range(10):
        assert client.post("/api/auth/login", json={"password": "wrong"}).status_code == 401
    assert client.post("/api/auth/login", json={"password": "password"}).status_code == 429


def test_smoke_preparation_is_immutable_and_launch_idempotent(cloud, monkeypatch, tmp_path):
    import json
    path = tmp_path / "build.json"
    path.write_text(json.dumps({"git_sha": "test", "image_digest": "test"}))
    monkeypatch.setenv("MB_BUILD_INFO", str(path))
    client, store = cloud
    client.post("/api/auth/login", json={"password": "password"})
    assert client.post("/api/smoke/prepare", json={"max_turns": 50}).status_code == 422
    prepared = client.post("/api/smoke/prepare", json={"count": 2}).json()
    payload = {"preparation_id": prepared["preparation_id"], "idempotency_key": "test-key-123"}
    first = client.post("/api/smoke", json=payload)
    second = client.post("/api/smoke", json=payload)
    assert first.status_code == second.status_code == 200
    assert [j["job_id"] for j in first.json()] == [j["job_id"] for j in second.json()]
    assert len(store.rows("SELECT * FROM jobs")) == 2
    job_id = first.json()[0]["job_id"]
    assert client.post(f"/api/jobs/{job_id}/resume").status_code == 409
    assert client.get(f"/api/jobs/{job_id}/artifacts?path=../ledger.sqlite").status_code == 409


def test_live_committed_snapshot_batch_and_export_range(cloud, monkeypatch, tmp_path):
    import json
    from monopoly_arena.cloud_campaign import run_config
    from monopoly_arena.journal import Journal
    from starlette.websockets import WebSocketDisconnect
    client, store = cloud
    path = tmp_path / "build.json"
    path.write_text(json.dumps({"git_sha": "test", "image_digest": "test"}))
    monkeypatch.setenv("MB_BUILD_INFO", str(path))
    job = store.create_job(run_config(42, "live-test", max_turns=5), kind="smoke", key="live-test")
    job_id = job["job_id"]
    execution = store.claim(job_id)
    journal = Journal(store, job_id, execution)
    snapshot = {"run_id": "live-test", "turn_index": 2, "phase": "START_TURN"}
    with journal.transition("advance", snapshot=snapshot):
        journal.write(store.root / "runs/live-test/events.jsonl", b'{"seq":1}\n{"seq":2}\n', append=True)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/api/jobs/{job_id}/ws"):
            pass
    client.post("/api/auth/login", json={"password": "password"})
    with client.websocket_connect(f"wss://testserver/api/jobs/{job_id}/ws") as socket:
        assert socket.receive_json()["type"] == "HELLO"
        message = socket.receive_json()
        assert message["snapshot"] == snapshot
        assert message["events"] == [{"seq": 1}, {"seq": 2}]
        assert message["commit_seq"] == 1 and message["reset"]
    package = tmp_path / "package.zip"
    package.write_bytes(bytes(range(100)))
    store.execute("INSERT INTO exports VALUES(?,?,?,?,?,?,?,?,?)", ("export-test", "job", job_id, 1, "completed", str(package), 100, "hash", 0))
    response = client.get("/api/exports/export-test/download", headers={"Range": "bytes=10-19"})
    assert response.status_code == 206 and response.content == bytes(range(10, 20))


def test_decision_pages_and_artifacts_only_expose_committed_bytes(cloud, monkeypatch, tmp_path):
    import json
    from monopoly_arena.cloud_campaign import run_config
    from monopoly_arena.journal import Journal, JournalRunFiles
    client, store = cloud
    path = tmp_path / "build.json"
    path.write_text(json.dumps({"git_sha": "test", "image_digest": "test"}))
    monkeypatch.setenv("MB_BUILD_INFO", str(path))
    job = store.create_job(run_config(42, "paged", max_turns=5), kind="smoke", key="paged")
    journal = Journal(store, job["job_id"], store.claim(job["job_id"]))
    files = JournalRunFiles.create(journal, job["run_id"])
    with journal.transition("decisions"):
        for i in range(301):
            for phase in ("decision_started", "decision_resolved"):
                files.write_decision({"decision_id": f"d{i}", "phase": phase, "player_id": "p1", "turn_index": i})
        journal.write(files.prompts_dir / "decision_d300_system.txt", b"committed prompt")
    committed = files.decisions_path.read_bytes()
    with files.decisions_path.open("ab") as handle:
        handle.write(b'{"decision_id":"unpublished","phase":"decision_started"}\n')
    (files.prompts_dir / "decision_unpublished_system.txt").write_text("unpublished prompt")
    client.post("/api/auth/login", json={"password": "password"})
    base = f"/api/jobs/{job['job_id']}"
    assert len(client.get(base + "/decisions").json()) == 50
    final = client.get(base + "/decisions?cursor=300").json()
    assert len(final) == 1 and final[0]["decision_id"] == "d300"
    bundle = client.get(base + "/decisions/d300").json()
    assert bundle["attempts"][0]["system_prompt"] == "committed prompt"
    assert client.get(base + "/decisions/unpublished").status_code == 404
    assert client.get(base + "/artifacts?path=decisions.jsonl").content == committed
