import asyncio
import json

import pytest

from monopoly_arena.budget import budget_guard, budget_status, check_budget
from monopoly_arena.cloud_client import CloudClient
from monopoly_arena.execution_policy import OperationalPause
from monopoly_arena.job_store import JobStore, encode
from monopoly_arena.openrouter_client import OpenRouterClient, OpenRouterResult
from monopoly_telemetry.execution_cost import call_cost


def job(store, name="game", *, budget=None, campaign=None, rerun_of=None):
    config = {"run_id": name, "seed": 7, "git_sha": "test", "image_digest": "test"}
    if budget is not None:
        config["cost_budget"] = budget
    return store.create_job(config, kind="smoke", key=name, campaign_id=campaign, rerun_of=rerun_of)["job_id"]


def campaign(store, budget):
    store.execute("INSERT INTO campaigns(campaign_id,config_json) VALUES(?,?)", ("campaign", encode({"cost_budget": budget})))


def call(store, job_id, amount=None, *, state="responded", status="known", usage=None):
    cost = call_cost(usage) if usage is not None else {"total_cost": amount, "cost_status": status}
    call_id = str(len(store.rows("SELECT call_id FROM calls")))
    store.execute("INSERT INTO calls(call_id,job_id,state,total_cost,cost_status) VALUES(?,?,?,?,?)",
                  (call_id, job_id, state, cost["total_cost"], cost["cost_status"]))


def test_no_cap_preserves_missing_cost_behavior(tmp_path):
    store = JobStore(tmp_path)
    target = job(store)
    call(store, target, state="unknown", status="unknown")
    call(store, target, status="missing")
    assert budget_status(store, target) == {"blocked": False, "reason": None, "detail": "", "scopes": []}
    budget_guard(store, target)


@pytest.mark.parametrize("amount", [1, 1.1])
def test_job_threshold_pauses_without_mutating_job(tmp_path, amount):
    store = JobStore(tmp_path)
    target = job(store, budget=1)
    call(store, target, amount)
    before = store.job(target)
    status = budget_status(store, target)
    assert status["reason"] == "budget"
    assert status["scopes"][0]["known_total"] == amount
    with pytest.raises(OperationalPause) as exc:
        check_budget(store, target)
    assert exc.value.reason == "budget"
    assert str(exc.value) == status["detail"]
    assert store.job(target) == before
    assert store.rows("SELECT * FROM pauses") == []


def test_campaign_counts_all_jobs_reruns_and_physical_calls(tmp_path):
    store = JobStore(tmp_path)
    campaign(store, 1)
    original = job(store, "original", campaign="campaign")
    rerun = job(store, "rerun", campaign="campaign", rerun_of=original)
    target = job(store, "target", campaign="campaign")
    unrelated = job(store, "unrelated")
    store.execute("UPDATE jobs SET status='failed',archived=1 WHERE job_id=?", (original,))
    call(store, original, .2, state="failed")
    call(store, original, .3)
    call(store, rerun, usage={"cost": .1, "is_byok": True, "cost_details": {"upstream_inference_cost": .4}})
    call(store, unrelated, 100)
    status = budget_status(store, target)
    assert status["reason"] == "budget"
    assert status["scopes"] == [{"scope": "campaign", "limit": 1, "known_total": 1,
                                  "unaccounted_calls": 0, "in_flight_calls": 0}]


@pytest.mark.parametrize("state,status,amount", [
    ("responded", "missing", None), ("failed", "missing", None),
    ("unknown", "unknown", None), ("failed", "unknown", .1),
    ("responded", "known", None), ("responded", "known", -1),
    ("responded", "known", float("inf")),
])
def test_unaccounted_settled_calls_fail_closed(tmp_path, state, status, amount):
    store = JobStore(tmp_path)
    target = job(store, budget=1)
    call(store, target, amount, state=state, status=status)
    result = budget_status(store, target)
    assert result["reason"] == "budget_unknown"
    assert result["scopes"][0]["unaccounted_calls"] == 1
    with pytest.raises(OperationalPause) as exc:
        budget_guard(store, target)
    assert exc.value.reason == "budget_unknown"


def test_below_threshold_discloses_in_flight_without_treating_it_as_missing(tmp_path):
    store = JobStore(tmp_path)
    target = job(store, budget=1)
    call(store, target, .25)
    call(store, target, state="intent", status="unknown")
    result = budget_status(store, target)
    assert not result["blocked"]
    assert result["scopes"] == [{"scope": "job", "limit": 1, "known_total": .25,
                                  "unaccounted_calls": 0, "in_flight_calls": 1}]


def test_campaign_unknown_cost_in_another_job_blocks_target(tmp_path):
    store = JobStore(tmp_path)
    campaign(store, 1)
    target = job(store, campaign="campaign")
    other = job(store, "other", campaign="campaign")
    call(store, other, state="intent", status="unknown")
    assert not budget_status(store, target)["blocked"]
    store.execute("UPDATE calls SET state='unknown' WHERE job_id=?", (other,))
    result = budget_status(store, target)
    assert result["reason"] == "budget_unknown"
    assert result["scopes"][0]["unaccounted_calls"] == 1
    assert result["scopes"][0]["in_flight_calls"] == 0


@pytest.mark.parametrize("reached_scope", ["job", "campaign"])
def test_reached_scope_precedes_other_scope_unknown_cost(tmp_path, reached_scope):
    store = JobStore(tmp_path)
    campaign(store, 1 if reached_scope == "campaign" else 10)
    target = job(store, budget=1 if reached_scope == "job" else 10, campaign="campaign")
    call(store, target, 1)
    call(store, target, status="missing")
    result = budget_status(store, target)
    assert result["reason"] == "budget"
    assert result["detail"].startswith(reached_scope.capitalize())
    assert [scope["scope"] for scope in result["scopes"]] == ["job", "campaign"]


@pytest.mark.parametrize("scope", ["job", "campaign"])
@pytest.mark.parametrize("limit", [0, -1, True, "1", float("nan"), float("inf"), float("-inf"), 10**400])
def test_invalid_limits_are_rejected(tmp_path, scope, limit):
    store = JobStore(tmp_path)
    campaign(store, limit if scope == "campaign" else None)
    target = job(store, budget=limit if scope == "job" else None, campaign="campaign")
    with pytest.raises(ValueError, match="positive finite USD"):
        budget_status(store, target)


def test_boundary_blocks_new_requests_but_saved_response_remains_reusable(tmp_path, monkeypatch):
    monkeypatch.setenv("MB_DISK_RESERVE_GB", "0")
    store = JobStore(tmp_path)
    target = job(store, budget=1)
    payloads = []

    async def complete(self, **kwargs):
        payloads.append(kwargs)
        return OpenRouterResult(True, 200, {"model": "test", "provider": "openai", "usage": {"cost": 1}}, None, None, "test")

    monkeypatch.setattr(OpenRouterClient, "create_chat_completion", complete)

    async def run():
        payload = {"model": "test", "messages": [], "provider": {"only": ["openai"]}}
        for _ in range(2):
            client = CloudClient(store, target)
            try:
                client.begin_decision("saved")
                assert (await client.create_chat_completion(**payload)).ok
                with pytest.raises(OperationalPause) as exc:
                    client.boundary()
                assert exc.value.reason == "budget"
                client.begin_decision("new")
                with pytest.raises(OperationalPause) as exc:
                    await client.create_chat_completion(**payload)
                assert exc.value.reason == "budget"
            finally:
                await client.aclose()

    asyncio.run(run())
    assert payloads == [{"model": "test", "messages": [], "provider": {"only": ["openai"]}}]
    assert len(store.rows("SELECT * FROM calls")) == 1
    saved_payload = json.loads(next((tmp_path / "jobs" / target / "calls").glob("*.intent.json")).read_text())["payload"]
    assert saved_payload == payloads[0]


def test_budget_is_checked_before_transport_retry(tmp_path, monkeypatch):
    monkeypatch.setenv("MB_DISK_RESERVE_GB", "0")
    store = JobStore(tmp_path)
    target = job(store, budget=1)
    requests = []

    async def complete(self, **kwargs):
        requests.append(kwargs)
        return OpenRouterResult(False, 503, {"usage": {"cost": 1}}, "unavailable", "http_error", "test")

    async def no_sleep(seconds):
        pass

    monkeypatch.setattr(OpenRouterClient, "create_chat_completion", complete)
    monkeypatch.setattr("monopoly_arena.cloud_client.asyncio.sleep", no_sleep)

    async def run():
        client = CloudClient(store, target)
        try:
            with pytest.raises(OperationalPause) as exc:
                await client.create_chat_completion(model="test", messages=[])
            assert exc.value.reason == "budget"
        finally:
            await client.aclose()

    asyncio.run(run())
    assert len(requests) == 1
    assert len(store.rows("SELECT * FROM calls")) == 1
