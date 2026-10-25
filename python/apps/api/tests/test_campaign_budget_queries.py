"""Campaign responses read the shared budget ledger once and stay fail-closed."""
from contextlib import contextmanager

import pytest

from monopoly_arena.budget import budget_status, campaign_budget_statuses, check_budget
from monopoly_arena.campaign_setup import readiness
from monopoly_arena.execution_policy import OperationalPause
from monopoly_arena.job_store import encode

from test_campaign_setup import prepare, save

CAMPAIGN_SCAN = "FROM calls JOIN jobs"


@contextmanager
def traced(store):
    statements: list[str] = []
    original = store.connect

    @contextmanager
    def connect():
        with original() as db:
            db.set_trace_callback(statements.append)
            yield db

    store.connect = connect
    try:
        yield statements
    finally:
        del store.connect


def add_call(store, job_id, call_id, amount, status="known"):
    store.execute("INSERT INTO calls(call_id,job_id,state,total_cost,cost_status) VALUES(?,?,'responded',?,?)",
                  (call_id, job_id, amount, status))


@pytest.fixture
def capped_campaign(setup_client):
    client, store, _ = setup_client
    saved = save(client, prepare(client, seed_blocks=5, cost_budget=100.0)).json()
    path = f"/api/campaigns/{saved['campaign_id']}"
    assert client.post(path + "/run", json={}).status_code == 200
    jobs = [row["job_id"] for row in store.rows("SELECT job_id FROM jobs WHERE campaign_id=?", (saved["campaign_id"],))]
    assert len(jobs) == 20
    for index, job_id in enumerate(jobs):
        for attempt in range(3):
            add_call(store, job_id, f"{index}-{attempt}", 0.01)
    return client, store, saved["campaign_id"], path, jobs


def test_many_cell_campaign_reads_campaign_ledger_once(capped_campaign):
    client, store, campaign_id, path, jobs = capped_campaign
    with traced(store) as statements:
        view = client.get(path).json()
    # Previously every cell plus readiness re-read the campaign ledger (21 scans here).
    assert sum(CAMPAIGN_SCAN in sql for sql in statements) == 1
    assert sum(" FROM calls" in sql for sql in statements) == len(jobs) + 1
    games = {cell["job_id"]: cell["game"] for cell in view["cells"]}
    assert set(games) == set(jobs)
    for job_id, game in games.items():
        assert game["budget"] == budget_status(store, job_id)
        assert game["budget"]["scopes"] == [{"scope": "campaign", "limit": 100.0, "known_total": pytest.approx(0.6),
                                              "unaccounted_calls": 0, "in_flight_calls": 0}]
    assert view["readiness"] == readiness(store, view) and view["readiness"]["can_start"]


def test_missing_settled_cost_still_blocks_every_cell_and_fresh_checks(capped_campaign):
    client, store, campaign_id, path, jobs = capped_campaign
    assert not client.get(path).json()["cells"][0]["game"]["budget"]["blocked"]
    add_call(store, jobs[-1], "missing", None, "missing")
    with traced(store) as statements:
        view = client.get(path).json()
    assert sum(CAMPAIGN_SCAN in sql for sql in statements) == 1
    # No zero charge is inferred and no response cache hides the new ledger row.
    assert {cell["game"]["budget"]["reason"] for cell in view["cells"]} == {"budget_unknown"}
    assert not view["readiness"]["can_start"]
    assert any("missing or unknown cost" in reason for reason in view["readiness"]["reasons"])
    with pytest.raises(OperationalPause) as exc:
        check_budget(store, jobs[0])
    assert exc.value.reason == "budget_unknown"
    assert client.post(path + "/run", json={}).status_code == 409


def test_campaign_filtered_jobs_share_one_budget_read(capped_campaign):
    client, store, campaign_id, _, jobs = capped_campaign
    with traced(store) as statements:
        response = client.get("/api/jobs", params={"campaign": campaign_id})
    assert response.status_code == 200
    assert sum(CAMPAIGN_SCAN in sql for sql in statements) == 1
    assert {job["job_id"] for job in response.json()["jobs"]} == set(jobs)


def test_batched_statuses_match_single_job_reads(setup_client):
    _, store, _ = setup_client
    store.execute("INSERT INTO campaigns(campaign_id,config_json) VALUES('shared',?)", (encode({"cost_budget": 1}),))
    config = {"seed": 7, "git_sha": "test", "image_digest": "test"}
    capped = store.create_job({**config, "run_id": "capped", "cost_budget": 0.5}, kind="smoke", key="capped", campaign_id="shared")["job_id"]
    plain = store.create_job({**config, "run_id": "plain"}, kind="smoke", key="plain", campaign_id="shared")["job_id"]
    invalid = store.create_job({**config, "run_id": "invalid", "cost_budget": -1}, kind="smoke", key="invalid", campaign_id="shared")["job_id"]
    store.create_job({**config, "run_id": "other"}, kind="smoke", key="other")
    add_call(store, capped, "a", 0.5)
    add_call(store, plain, "b", 0.25)
    add_call(store, plain, "c", None, "unknown")
    statuses = campaign_budget_statuses(store, "shared")
    assert list(statuses) == [capped, plain]
    for job_id, status in statuses.items():
        assert status == budget_status(store, job_id)
    assert statuses[capped]["reason"] == "budget" and statuses[plain]["reason"] == "budget_unknown"
    with pytest.raises(ValueError, match="positive finite USD"):
        budget_status(store, invalid)
    assert campaign_budget_statuses(store, "absent") == {}


def test_ledger_reads_use_job_and_campaign_indexes(setup_client):
    _, store, _ = setup_client
    with store.connect() as db:
        for sql in ["SELECT * FROM calls WHERE job_id=? ORDER BY rowid",
                    "SELECT calls.* FROM calls JOIN jobs ON jobs.job_id=calls.job_id WHERE jobs.campaign_id=? ORDER BY calls.rowid",
                    "SELECT job_id FROM jobs WHERE campaign_id=? LIMIT 1"]:
            plan = " ".join(row["detail"] for row in db.execute("EXPLAIN QUERY PLAN " + sql, ("x",)))
            assert "SCAN calls" not in plan and "SCAN jobs" not in plan, plan
