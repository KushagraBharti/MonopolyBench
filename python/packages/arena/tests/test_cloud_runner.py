import asyncio
import json
from pathlib import Path

import httpx
import pytest

from monopoly_arena.cloud_campaign import run_config, freeze, amend
from monopoly_arena.cloud_client import CloudClient
from monopoly_arena.execution_policy import OperationalPause
from monopoly_arena.job_store import JobStore, encode
from monopoly_arena.journal import Journal
from monopoly_arena.openrouter_client import OpenRouterClient, OpenRouterResult
from monopoly_arena.worker import play, build_identity
from monopoly_telemetry.writer_jsonl import atomic_write, read_jsonl_strict


def setup_job(tmp_path, monkeypatch, run_id="cloud-test"):
    monkeypatch.setenv("MB_DISK_RESERVE_GB", "0")
    identity = {"git_sha": "test", "image_digest": "test"}
    identity_file = tmp_path / "build.json"
    identity_file.write_text(json.dumps(identity))
    monkeypatch.setenv("MB_BUILD_INFO", str(identity_file))
    store = JobStore(tmp_path / "data")
    job = store.create_job(run_config(7, run_id, max_turns=5), kind="smoke", key=run_id)
    return store, job, store.claim(job["job_id"])


@pytest.mark.parametrize("cut", [0, 1, 4, 8])
def test_journal_repairs_partial_append(tmp_path, monkeypatch, cut):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    journal = Journal(store, job["job_id"], execution)
    target = store.root / "runs" / job["run_id"] / "events.jsonl"
    apply = journal._apply
    monkeypatch.setattr(journal, "_apply", lambda record: (_ for _ in ()).throw(RuntimeError("crash")))
    with pytest.raises(RuntimeError):
        journal.write(target, b'{"x":1}\n', append=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b'{"x":1}\n'[:cut])
    monkeypatch.setattr(journal, "_apply", apply)
    journal.recover()
    assert target.read_bytes() == b'{"x":1}\n'
    assert journal.last()["commit_seq"] == 1
    journal.recover()


def test_journal_contradiction_keeps_evidence(tmp_path, monkeypatch):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    journal = Journal(store, job["job_id"], execution)
    target = store.root / "runs" / job["run_id"] / "events.jsonl"
    journal.write(target, b'{"x":1}\n', append=True)
    target.write_bytes(b'{"x":9}\n')
    with pytest.raises(ValueError, match="contradiction"):
        journal.recover()
    assert target.read_bytes() == b'{"x":9}\n'


def test_claim_and_idempotency(tmp_path, monkeypatch):
    store, job, _ = setup_job(tmp_path, monkeypatch)
    assert store.claim(job["job_id"]) is None
    same = store.create_job(json.loads(job["config_json"]), kind="smoke", key="cloud-test")
    assert same["job_id"] == job["job_id"]
    with pytest.raises(ValueError):
        store.create_job(run_config(8, "other", max_turns=5), kind="smoke", key="cloud-test")


def test_response_reused_without_network(tmp_path, monkeypatch):
    store, job, _ = setup_job(tmp_path, monkeypatch)
    count = 0
    async def complete(self, **kwargs):
        nonlocal count
        count += 1
        return OpenRouterResult(True, 200, {"model": kwargs["model"], "provider": "openai", "usage": {"cost": 0.01}}, None, None, "test")
    monkeypatch.setattr(OpenRouterClient, "create_chat_completion", complete)
    async def run():
        for _ in range(2):
            client = CloudClient(store, job["job_id"])
            client.begin_decision("decision1")
            result = await client.create_chat_completion(model="openai/gpt-6.1-sol", messages=[], provider={"only": ["openai"]})
            assert result.ok
            await client.aclose()
    asyncio.run(run())
    assert count == 1


@pytest.mark.parametrize("status,reason", [(401, "account_error"), (402, "account_error"), (403, "account_error"), (503, "provider_unavailable")])
def test_operational_errors_do_not_fallback(tmp_path, monkeypatch, status, reason):
    store, job, _ = setup_job(tmp_path, monkeypatch)
    async def complete(self, **kwargs):
        return OpenRouterResult(False, status, None, "failed", "http_error", None)
    monkeypatch.setattr(OpenRouterClient, "create_chat_completion", complete)
    async def run():
        client = CloudClient(store, job["job_id"])
        with pytest.raises(OperationalPause) as exc:
            await client.create_chat_completion(model="test", messages=[])
        assert exc.value.reason == reason
        await client.aclose()
    asyncio.run(run())


def mock_transport():
    def response(request):
        if request.method == "GET":
            return httpx.Response(200, json={"data": []})
        payload = json.loads(request.content)
        return httpx.Response(200, json={"id": "mock", "model": payload["model"], "provider": payload["provider"]["only"][0], "choices": [{"message": {"tool_calls": [{"id": "t", "type": "function", "function": {"name": "invalid", "arguments": "{}"}}]}}], "usage": {"cost": 0.001, "prompt_tokens": 10, "completion_tokens": 2}})
    return httpx.MockTransport(response)


def test_worker_full_smoke_and_terminal_replay(tmp_path, monkeypatch):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    assert store.job(job["job_id"])["status"] == "finalizing"
    run = store.root / "runs" / job["run_id"]
    events = read_jsonl_strict(run / "events.jsonl")
    assert events[-1]["type"] == "GAME_ENDED"
    from monopoly_arena.worker import make_runner
    from monopoly_telemetry.run_files import build_run_files
    client = CloudClient(store, job["job_id"])
    runner = make_runner(store, job, client, build_run_files(store.root / "runs", job["run_id"]), recover=True)
    assert runner._engine.is_game_over()
    asyncio.run(client.aclose())
    from monopoly_arena.finalizer import finalize
    asyncio.run(finalize(store, job["job_id"]))
    assert store.job(job["job_id"])["status"] == "completed", store.job(job["job_id"])["pause_reason"]
    from monopoly_telemetry.export import unpack_verified
    package = store.rows("SELECT * FROM exports")[0]
    unpack_verified(Path(package["path"]), tmp_path / "exported")
    assert (tmp_path / "exported" / "analysis" / "manifest.json").exists()


def test_campaign_freeze_and_amend(tmp_path, monkeypatch):
    import time
    store, _, _ = setup_job(tmp_path, monkeypatch)
    store.set_state("preflight", {"passed": True, "created_at": time.time(), **build_identity()})
    config = json.loads((Path(__file__).resolve().parents[4] / "campaigns" / "monopoly-long-v2-frontier-2026q4.json").read_text())
    config.update(campaign_id="test", execution_order_seed=42, seeds=[1, 2])
    freeze(store, config)
    assert len(store.rows("SELECT * FROM cells")) == 8
    freeze(store, config)
    amend(store, "test", [3], "Additional seed block")
    assert len(store.rows("SELECT * FROM cells")) == 12
    with pytest.raises(ValueError):
        amend(store, "test", [1], "Duplicate")


def test_unknown_request_limit(tmp_path, monkeypatch):
    store, job, _ = setup_job(tmp_path, monkeypatch)
    client = CloudClient(store, job["job_id"])
    raw = '{"model":"test","messages":[]}'
    import hashlib
    for i in range(2):
        call_id = str(i)
        atomic_write(client.directory / f"{call_id}.intent.json", encode({"payload_sha256": hashlib.sha256(raw.encode()).hexdigest()}).encode())
        store.execute("INSERT INTO calls(call_id,job_id,decision_id,resolver_stage,state,created_at) VALUES(?,?,?,0,'intent',?)", (call_id, job["job_id"], "d", i))
    client.begin_decision("d")
    with pytest.raises(ValueError, match="limit"):
        asyncio.run(client.create_chat_completion(model="test", messages=[]))
    asyncio.run(client.aclose())


@pytest.mark.parametrize("boundary", ["initialize", "advance", "action", "artifact", "prompt", "wire"])
def test_recovery_after_journal_fsync_preserves_events_and_actions(tmp_path, monkeypatch, boundary):
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    # Same engine run ID and seed in two independent data roots.
    (tmp_path / "reference").mkdir()
    reference, baseline, execution = setup_job(tmp_path / "reference", monkeypatch)
    asyncio.run(play(reference, baseline["job_id"], execution))
    (tmp_path / "interrupted").mkdir()
    store, job, execution = setup_job(tmp_path / "interrupted", monkeypatch)
    original_apply = Journal._apply
    crashed = False
    def crash(self, record):
        nonlocal crashed
        if not crashed and record["kind"] == boundary:
            crashed = True
            raise RuntimeError("simulated process death")
        original_apply(self, record)
    monkeypatch.setattr(Journal, "_apply", crash)
    with pytest.raises(RuntimeError, match="process death"):
        asyncio.run(play(store, job["job_id"], execution))
    monkeypatch.setattr(Journal, "_apply", original_apply)
    store.execute("UPDATE jobs SET status='recovering' WHERE job_id=?", (job["job_id"],))
    execution = store.claim(job["job_id"])
    asyncio.run(play(store, job["job_id"], execution))
    for name in ("events.jsonl", "actions.jsonl"):
        assert (store.root / "runs" / job["run_id"] / name).read_bytes() == (reference.root / "runs" / baseline["run_id"] / name).read_bytes()


def test_production_shaped_preflight_against_mock(tmp_path, monkeypatch):
    import importlib.util
    from monopoly_arena.cloud_preflight import preflight
    script = Path(__file__).resolve().parents[4] / "scripts" / "mock_openrouter_server.py"
    spec = importlib.util.spec_from_file_location("mock_server", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    store, _, _ = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=httpx.ASGITransport(app=module.app))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    report = asyncio.run(preflight(store))
    assert report["passed"], report.get("error")


def test_cloud_preserves_local_events_actions_prompts_and_snapshots(tmp_path, monkeypatch):
    from monopoly_arena.llm_runner import LlmRunner
    from monopoly_arena.player_config import build_single_player_config
    from monopoly_telemetry import init_run_files
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    config = json.loads(job["config_json"])
    local = init_run_files(tmp_path / "local" / "runs", job["run_id"])
    runner = LlmRunner(seed=7, players=[build_single_player_config(**p) for p in config["players"]], run_id=job["run_id"], openrouter=OpenRouterClient(), run_files=local, max_turns=5, event_delay_s=0)
    asyncio.run(runner.run())
    asyncio.run(play(store, job["job_id"], execution))
    cloud = store.root / "runs" / job["run_id"]
    for name in ("events.jsonl", "actions.jsonl"):
        assert (cloud / name).read_bytes() == (local.run_dir / name).read_bytes()
    for directory in ("state", "prompts"):
        paths = [p.relative_to(local.run_dir) for p in (local.run_dir / directory).glob("*") if directory == "state" or any(p.name.endswith(suffix) for suffix in ("_system.txt", "_user.json", "_tools.json"))]
        for path in paths:
            assert (cloud / path).read_bytes() == (local.run_dir / path).read_bytes(), str(path)


@pytest.mark.parametrize("stage", [0, 1])
def test_saved_stage_response_reused_after_crash(tmp_path, monkeypatch, stage):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    requests = []
    def response(request):
        if request.method == "POST":
            requests.append(request.content)
        return mock_transport().handle_request(request)
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=httpx.MockTransport(response))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    record = CloudClient._record_result
    crashed = False
    def crash(self, call_id, result):
        nonlocal crashed
        if not crashed and self.stage-1 == stage:
            crashed = True
            raise RuntimeError("response saved before crash")
        record(self, call_id, result)
    monkeypatch.setattr(CloudClient, "_record_result", crash)
    with pytest.raises(RuntimeError):
        asyncio.run(play(store, job["job_id"], execution))
    before = list(requests)
    monkeypatch.setattr(CloudClient, "_record_result", record)
    store.execute("UPDATE jobs SET status='recovering' WHERE job_id=?", (job["job_id"],))
    asyncio.run(play(store, job["job_id"], store.claim(job["job_id"])))
    assert store.job(job["job_id"])["status"] == "finalizing"
    assert all(requests.count(payload) == 1 for payload in before)


def test_outage_counters_survive_restart_and_manual_resume(tmp_path, monkeypatch):
    store, job, _ = setup_job(tmp_path, monkeypatch)
    count = 0
    async def fail(self, **kwargs):
        nonlocal count
        count += 1
        return OpenRouterResult(False, 503, None, "outage", "http_5xx", None)
    monkeypatch.setattr(OpenRouterClient, "create_chat_completion", fail)
    async def attempt():
        client = CloudClient(store, job["job_id"])
        client.begin_decision("d")
        try:
            with pytest.raises(OperationalPause) as exc:
                await client.create_chat_completion(model="test", messages=[])
            return exc.value
        finally:
            await client.aclose()
    asyncio.run(attempt())
    assert count == 3
    # A process restart alone cannot reset the three transport attempts.
    exc = asyncio.run(attempt())
    assert count == 3
    store.pause(job["job_id"], exc.reason)
    for retry in range(1, 13):
        store.execute("UPDATE jobs SET status='running' WHERE job_id=?", (job["job_id"],))
        exc = asyncio.run(attempt())
        store.pause(job["job_id"], exc.reason)
        assert count == 3+retry
    pause = store.rows("SELECT * FROM pauses")[0]
    assert pause["retries_used"] == 12 and pause["next_retry_at"] is None
    store.resume(job["job_id"])
    asyncio.run(attempt())
    assert count == 18


def test_scheduler_slots_priority_and_live_lock(tmp_path, monkeypatch):
    from monopoly_arena.supervisor import Supervisor
    from monopoly_arena.worker import writer_lock
    store, first, _ = setup_job(tmp_path, monkeypatch)
    store.set_state("preflight", {"passed": True})
    store.execute("UPDATE jobs SET status='queued' WHERE job_id=?", (first["job_id"],))
    for i in range(6):
        store.create_job(run_config(i, f"queued-{i}", max_turns=5), kind="smoke", key=f"queue-{i}", rank=6-i)
    launched = []
    class Child:
        def __init__(self, command):
            launched.append(command)
        def poll(self):
            return None
    monkeypatch.setattr("monopoly_arena.supervisor.subprocess.Popen", Child)
    supervisor = Supervisor(store)
    with writer_lock(store.root / "runs" / first["run_id"] / ".writer.lock"):
        supervisor.tick()
        assert store.job(first["job_id"])["status"] == "queued"
    assert len(launched) == 5
    supervisor.tick()
    assert len(launched) == 5
    ranks = [store.job(command[command.index("--job")+1])["execution_rank"] for command in launched]
    assert ranks == sorted(ranks)
