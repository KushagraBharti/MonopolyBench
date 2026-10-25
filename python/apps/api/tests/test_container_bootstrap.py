import json
from pathlib import Path
import runpy

from fastapi.testclient import TestClient
import pytest

from monopoly_api.bootstrap import prepare_runtime, SECRET_NAMES
from monopoly_api.jobs_api import create_cloud_app


@pytest.fixture
def clean_environment(monkeypatch):
    for name in (*SECRET_NAMES, "MB_DEMO", "MB_LOCAL_HTTP", "MB_TEST_MODE", "OPENROUTER_API_KEY", "MB_OPENROUTER_BASE_URL", "MB_MOCK_PORT", "MB_DISK_RESERVE_GB"):
        monkeypatch.setenv(name, "")


@pytest.mark.parametrize("saved_password", [None, "old-generated-password"])
def test_default_login_preserves_secrets_without_saving_provider_key(tmp_path, monkeypatch, clean_environment, saved_password):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-provider-key")
    monkeypatch.setenv("MB_LOCAL_HTTP", "1")
    if saved_password:
        (tmp_path / "runtime_secrets.json").write_text(json.dumps({
            "MB_DASHBOARD_PASSWORD": saved_password, "MB_SESSION_SECRET": "s" * 32,
            "MB_EXPORT_TOKEN": "existing-export-token",
        }))
    assert not prepare_runtime(tmp_path)
    first = json.loads((tmp_path / "runtime_secrets.json").read_text())
    assert set(first) == set(SECRET_NAMES)
    assert first["MB_DASHBOARD_PASSWORD"] == "monopoly"
    if saved_password:
        assert first["MB_SESSION_SECRET"] == "s" * 32
        assert first["MB_EXPORT_TOKEN"] == "existing-export-token"
    assert (tmp_path / "runtime_secrets.json").stat().st_mode & 0o777 == 0o600
    with TestClient(create_cloud_app(tmp_path), base_url="https://localhost") as client:
        assert client.post("/api/auth/login", json={"password": "monopoly"}).status_code == 200
        assert client.get("/api/jobs").status_code == 200
    for name in SECRET_NAMES:
        monkeypatch.delenv(name)
    prepare_runtime(tmp_path)
    assert json.loads((tmp_path / "runtime_secrets.json").read_text()) == first


def test_explicit_password_override_is_used_for_login(tmp_path, monkeypatch, clean_environment):
    monkeypatch.setenv("MB_DASHBOARD_PASSWORD", "custom-password")
    prepare_runtime(tmp_path)
    with TestClient(create_cloud_app(tmp_path), base_url="https://localhost") as client:
        assert client.post("/api/auth/login", json={"password": "monopoly"}).status_code == 401
        assert client.post("/api/auth/login", json={"password": "custom-password"}).status_code == 200


@pytest.mark.parametrize("configured", ["", "monopoly"])
def test_remote_deployment_refuses_the_public_default_password(tmp_path, monkeypatch, clean_environment, configured):
    monkeypatch.setenv("MB_DASHBOARD_PASSWORD", configured)
    monkeypatch.setenv("MB_LOCAL_HTTP", "0")
    with pytest.raises(ValueError, match="MB_DASHBOARD_PASSWORD"):
        prepare_runtime(tmp_path)
    assert not (tmp_path / "runtime_secrets.json").exists()
    monkeypatch.setenv("MB_DASHBOARD_PASSWORD", "private-deployment-password")
    prepare_runtime(tmp_path)
    assert json.loads((tmp_path / "runtime_secrets.json").read_text())["MB_DASHBOARD_PASSWORD"] == "private-deployment-password"


def test_demo_overrides_paid_route_and_refuses_shared_research_volume(tmp_path, monkeypatch, clean_environment):
    import os
    monkeypatch.setenv("MB_DEMO", "1")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-real-key")
    monkeypatch.setenv("MB_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    assert prepare_runtime(tmp_path)
    assert os.environ["OPENROUTER_API_KEY"] == "mock-only"
    assert os.environ["MB_OPENROUTER_BASE_URL"] == "http://127.0.0.1:8765/api/v1"
    assert os.environ["MB_TEST_MODE"] == "1"
    monkeypatch.setenv("MB_DEMO", "0")
    with pytest.raises(ValueError, match="different runtime mode"):
        prepare_runtime(tmp_path)


def test_demo_refuses_existing_unmarked_ledger(tmp_path, monkeypatch, clean_environment):
    (tmp_path / "ledger.sqlite").touch()
    monkeypatch.setenv("MB_DEMO", "1")
    with pytest.raises(ValueError, match="fresh volume"):
        prepare_runtime(tmp_path)


def test_demo_cannot_freeze_research_campaign(tmp_path, monkeypatch, clean_environment):
    import os
    monkeypatch.setenv("MB_DEMO", "1")
    prepare_runtime(tmp_path)
    with TestClient(create_cloud_app(tmp_path), base_url="https://localhost") as client:
        client.post("/api/auth/login", json={"password": os.environ["MB_DASHBOARD_PASSWORD"]})
        assert client.get("/api/status").json()["demo"]
        response = client.post("/api/campaigns/monopoly-long-v2-frontier-2026q4/freeze")
        assert response.status_code == 409 and "Demo" in response.json()["detail"]


@pytest.mark.parametrize("url,local,secure", [("http://localhost", True, False), ("http://127.0.0.1", True, False), ("http://public.example", True, True), ("https://localhost", True, True), ("http://localhost", False, True)])
def test_local_cookie_exception_is_explicit_and_host_limited(tmp_path, monkeypatch, clean_environment, url, local, secure):
    monkeypatch.setenv("MB_LOCAL_HTTP", "1")
    prepare_runtime(tmp_path)
    monkeypatch.setenv("MB_LOCAL_HTTP", "1" if local else "0")
    import os
    with TestClient(create_cloud_app(tmp_path), base_url=url) as client:
        response = client.post("/api/auth/login", json={"password": os.environ["MB_DASHBOARD_PASSWORD"]})
        assert ("Secure" in response.headers["set-cookie"]) == secure
        if not secure or url.startswith("https:"):
            assert client.get("/api/jobs").status_code == 200


def test_build_identity_ignores_stale_host_manifest_and_tracks_source(tmp_path):
    script = Path(__file__).resolve().parents[4] / "scripts/build_manifest.py"
    build = runpy.run_path(str(script))["build_manifest"]
    (tmp_path / "python").mkdir()
    (tmp_path / "frontend").mkdir()
    (tmp_path / "python/uv.lock").write_text("locked-python")
    (tmp_path / "frontend/package-lock.json").write_text("locked-node")
    first = build(tmp_path)
    assert first["git_sha"].startswith("source:")
    (tmp_path / "build_info.json").write_text(json.dumps({"git_sha": "a" * 40, "source_sha256": "stale"}))
    assert build(tmp_path) == first
    registered = build(tmp_path, "b" * 40)
    (tmp_path / "build_info.json").write_text(json.dumps(registered))
    assert build(tmp_path)["git_sha"] == "b" * 40
    (tmp_path / "python/.env").write_text("PRIVATE_KEY=test")
    assert build(tmp_path) == registered
    (tmp_path / "python/worker.py").write_text("changed runtime")
    assert build(tmp_path)["source_sha256"] != first["source_sha256"]
    assert build(tmp_path)["git_sha"].startswith("source:")
