"""Dashboard totals, section isolation and authenticated export downloads."""
import asyncio
import json

from monopoly_arena.cloud_campaign import run_config
from monopoly_arena.finalizer import finalize
from monopoly_telemetry.export import unpack_verified

from test_campaign_setup import prepare, save


def validate(value, definition):
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from monopoly_arena.research_registry import research_dir
    schemas = research_dir().parent / "schemas"
    registry = Registry().with_resources((path.name, Resource.from_contents(json.loads(path.read_text()))) for path in schemas.glob("*.json"))
    Draft202012Validator({"$ref": "cloud.schema.json#/$defs/" + definition}, registry=registry).validate(value)


def test_dashboard_counts_all_rows_and_separates_sections(setup_client):
    client, store, _ = setup_client
    for index in range(52):
        job = store.create_job(run_config(index, f"single-{index}"), kind="single", key=f"s-{index}")
        if index == 0:
            store.execute("UPDATE jobs SET archived=1,status='completed' WHERE job_id=?", (job["job_id"],))
    for index in range(3):
        store.create_job(run_config(index, f"test-{index}", max_turns=5), kind="smoke", key=f"t-{index}")
    campaign = save(client, prepare(client)).json()
    client.post(f"/api/campaigns/{campaign['campaign_id']}/run", json={})
    view = client.get("/api/dashboard").json()
    validate(view, "dashboard")
    assert view["totals"] == {"games": 51, "tests": 3, "campaigns": 1, "exports": 0}
    assert view["activity"]["queued"] == 58
    assert len(view["recent_jobs"]) == 6 and len(view["recent_campaigns"]) == 1
    assert len(client.get("/api/jobs?kind=single").json()["jobs"]) == 50
    assert {job["kind"] for job in client.get("/api/jobs?kind=smoke").json()["jobs"]} == {"smoke"}
    assert len(client.get("/api/jobs?kind=single&archived=true").json()["jobs"]) == 1
    assert not store.rows("SELECT * FROM calls")


def test_export_library_survives_refresh_and_downloads_verified_packages(setup_client, tmp_path):
    client, store, _ = setup_client
    campaign = save(client, prepare(client)).json()
    path = f"/api/campaigns/{campaign['campaign_id']}"
    exports = [client.post(path + "/export", json={}).json()["export_id"] for _ in range(2)]
    refreshed = client.get(path).json()
    assert [row["revision"] for row in refreshed["exports"]] == [2, 1]
    assert {row["export_id"] for row in refreshed["exports"]} == set(exports)
    for kind in ["single", "smoke"]:
        job = store.create_job(run_config(42, f"export-{kind}", max_turns=5), kind=kind, key=f"export-{kind}")
        client.post(f"/api/jobs/{job['job_id']}/cancel", json={})
        # Diagnostic finalization has no provider client/calls. Never finalize a live writer.
        asyncio.run(finalize(store, job["job_id"]))
    library = client.get("/api/exports").json()
    assert len(library) == 4 and {entry["run_kind"] for entry in library} == {"single", "smoke", "campaign"}
    assert all("campaign_config_json" not in row for row in library)
    for index, entry in enumerate(library):
        validate(entry, "exportEntry")
        assert entry["display_name"]
        assert client.get(entry["source_url"].replace("/games/", "/api/jobs/").replace("/campaigns/", "/api/campaigns/")).status_code == 200
        response = client.get(entry["download_url"])
        assert response.status_code == 200 and len(response.content) == entry["bytes"]
        archive = tmp_path / f"package-{index}.zip"
        archive.write_bytes(response.content)
        unpack_verified(archive, tmp_path / f"verified-{index}")
    overview = client.get("/api/dashboard").json()
    validate(overview, "dashboard")
    assert overview["totals"]["exports"] == 4 and len(overview["recent_exports"]) == 4
    assert not store.rows("SELECT * FROM calls")


def test_dashboard_remains_session_protected_and_export_token_scope_stays_narrow(setup_client):
    client, _, _ = setup_client
    client.cookies.clear()
    assert client.get("/api/dashboard").status_code == 401
    bearer = {"Authorization": "Bearer test-export"}
    assert client.get("/api/dashboard", headers=bearer).status_code == 401
    assert client.get("/api/exports", headers=bearer).status_code == 200
    assert client.post("/api/campaigns/prepare", json={"name": "No session"}, headers=bearer).status_code == 401
