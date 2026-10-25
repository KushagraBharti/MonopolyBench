import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def setup_client(tmp_path, monkeypatch):
    import json
    import time
    from fastapi.testclient import TestClient
    from monopoly_api.jobs_api import create_cloud_app
    from monopoly_arena.worker import build_identity
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
