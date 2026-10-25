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


def test_pending_append_cannot_bless_corrupt_committed_prefix(tmp_path, monkeypatch):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    journal = Journal(store, job["job_id"], execution)
    target = store.root / "runs" / job["run_id"] / "events.jsonl"
    journal.write(target, b'{"x":1}\n', append=True)
    apply = journal._apply
    monkeypatch.setattr(journal, "_apply", lambda record: (_ for _ in ()).throw(RuntimeError("crash")))
    with pytest.raises(RuntimeError):
        journal.write(target, b'{"x":2}\n', append=True)
    monkeypatch.setattr(journal, "_apply", apply)
    target.write_bytes(b'{"x":9}\n')
    with pytest.raises(ValueError, match="contradiction"):
        journal.recover()
    assert target.read_bytes() == b'{"x":9}\n'
    assert journal.last()["commit_seq"] == 1


def test_recovery_rejects_missing_committed_journal_records(tmp_path, monkeypatch):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    journal = Journal(store, job["job_id"], execution)
    journal.write(store.root / "runs" / job["run_id"] / "config.json", b'{}')
    journal.path.write_bytes(b"")
    (store.root / "runs" / job["run_id"] / "config.json").unlink()
    with pytest.raises(ValueError, match="Journal coverage"):
        journal.recover()


def test_new_writes_after_restart_are_not_repairs(tmp_path, monkeypatch):
    store, job, _ = setup_job(tmp_path, monkeypatch)
    store.execute("UPDATE jobs SET status='recovering' WHERE job_id=?", (job["job_id"],))
    journal = Journal(store, job["job_id"], store.claim(job["job_id"]))
    journal.recover()
    journal.write(store.root / "runs" / job["run_id"] / "events.jsonl", b'{"x":1}\n', append=True)
    assert store.job(job["job_id"])["repaired"] == 0


@pytest.mark.parametrize("folder", ["prompts", "state", "quality_check", "snapshots"])
def test_recovery_quarantines_interrupted_atomic_write(tmp_path, monkeypatch, folder):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    journal = Journal(store, job["job_id"], execution)
    base = store.root / "runs" / job["run_id"] / folder
    if folder == "quality_check":
        base = store.root / folder / job["run_id"]
    elif folder == "snapshots":
        base = journal.directory / folder
    target = base / "evidence.json"
    apply = journal._apply
    monkeypatch.setattr(journal, "_apply", lambda record: (_ for _ in ()).throw(RuntimeError("crash")))
    with pytest.raises(RuntimeError):
        journal.write(target, b'{"complete":true}')
    base.mkdir(parents=True, exist_ok=True)
    leftover = base / ".write-killed"
    leftover.write_bytes(b'{"complete":tr')
    monkeypatch.setattr(journal, "_apply", apply)
    journal.recover()
    assert target.read_bytes() == b'{"complete":true}'
    assert not leftover.exists()
    quarantined = list((journal.directory / "recovery/quarantine").rglob(".write-killed"))
    assert len(quarantined) == 1 and quarantined[0].read_bytes() == b'{"complete":tr'
    assert store.job(job["job_id"])["repaired"] == 1
    journal.recover()


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


def mock_transport(*, refused=False):
    def response(request):
        if request.method == "GET":
            return httpx.Response(200, json={"data": []})
        payload = json.loads(request.content)
        choice = {"message": {"tool_calls": [{"id": "t", "type": "function", "function": {"name": "invalid", "arguments": "{}"}}]}}
        if refused:
            # A plausible partial tool call must never be used after refusal.
            choice.update(finish_reason="content_filter", native_finish_reason="refusal")
            choice["message"]["refusal"] = "Provider declined."
            choice["message"]["tool_calls"][0]["function"] = {"name": payload["tools"][0]["function"]["name"], "arguments": json.dumps({"public_message": "rejected partial", "private_thought": "rejected partial"})}
        if refused == "recover" and payload["model"] == "anthropic/claude-opus-4.8":
            offered = {t["function"]["name"] for t in payload["tools"]}
            name = next(name for name in ["buy_property", "end_turn", "drop_out"] if name in offered)
            choice = {"message": {"tool_calls": [{"id": "fallback", "type": "function", "function": {
                "name": name, "arguments": json.dumps({"public_message": "fallback model move"}),
            }}]}, "finish_reason": "tool_calls"}
        return httpx.Response(200, json={"id": "mock", "model": payload["model"], "provider": payload["provider"]["only"][0], "choices": [choice], "usage": {"cost": 0.001, "prompt_tokens": 10, "completion_tokens": 2}})
    return httpx.MockTransport(response)


@pytest.mark.parametrize("analysis_fails,refused", [(False, False), (True, False), (False, True), (False, "recover")])
def test_worker_full_smoke_and_terminal_replay(tmp_path, monkeypatch, analysis_fails, refused):
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport(refused=refused))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    assert store.job(job["job_id"])["status"] == "finalizing"
    run = store.root / "runs" / job["run_id"]
    events = read_jsonl_strict(run / "events.jsonl")
    assert events[-1]["type"] == "GAME_ENDED"
    if refused is True:
        resolved = [d for d in read_jsonl_strict(run / "decisions.jsonl") if d.get("phase") == "decision_resolved"]
        assert resolved
        assert all(d["fallback_reason"] == "provider_refusal_after_retry" for d in resolved)
        assert all(len(d["attempts"]) == (3 if d["openrouter_model_id"] == "anthropic/claude-opus-5.5" else 2) for d in resolved)
        assert all(a["outcome"] == "refused" and a["parsed_tool_call"] is None for d in resolved for a in d["attempts"])
        assert all(a["action"]["private_thought"] == "fallback" for a in read_jsonl_strict(run / "actions.jsonl"))
        assert "rejected partial" not in (run / "events.jsonl").read_text()
    if refused == "recover":
        resolved = [d for d in read_jsonl_strict(run / "decisions.jsonl") if d.get("phase") == "decision_resolved" and d["openrouter_model_id"] == "anthropic/claude-opus-5.5"]
        assert resolved and all(len(d["attempts"]) == 3 for d in resolved)
        assert all(not d["fallback_used"] and d["sequence_meta"]["model_fallback_used"] for d in resolved)
        assert all(d["attempts"][-1]["requested_model"] == "anthropic/claude-opus-4.8" for d in resolved)
        assert all("private_thought" not in d["final_action"] for d in resolved)
        assert "rejected partial" not in (run / "events.jsonl").read_text()
    from monopoly_arena.worker import make_runner
    from monopoly_telemetry.run_files import build_run_files
    client = CloudClient(store, job["job_id"])
    runner = make_runner(store, job, client, build_run_files(store.root / "runs", job["run_id"]), recover=True)
    assert runner._engine.is_game_over()
    asyncio.run(client.aclose())
    if analysis_fails:
        import importlib.util
        original_spec = importlib.util.spec_from_file_location
        def spec(name, location):
            result = original_spec(name, location)
            original_exec = result.loader.exec_module
            def load(module):
                original_exec(module)
                def fail(_):
                    raise RuntimeError("analysis unavailable")
                module.generate_analysis = fail
            result.loader.exec_module = load
            return result
        monkeypatch.setattr(importlib.util, "spec_from_file_location", spec)
    from monopoly_arena.finalizer import finalize
    asyncio.run(finalize(store, job["job_id"]))
    final = store.job(job["job_id"])
    assert final["status"] == ("failed" if analysis_fails else "completed"), final["pause_reason"]
    assert final["replay_status"] == "passed"
    assert final["analysis_status"] == ("failed" if analysis_fails else "completed")
    from monopoly_telemetry.export import unpack_verified
    package = store.rows("SELECT * FROM exports")[0]
    unpack_verified(Path(package["path"]), tmp_path / "exported")
    assert (tmp_path / "exported" / ("cloud/analysis_error.json" if analysis_fails else "analysis/manifest.json")).exists()
    assert json.loads((tmp_path / "exported/cloud/ledger.json").read_text())["jobs"][0]["replay_status"] == "passed"
    if refused:
        findings = read_jsonl_strict(run / "failure_findings.jsonl")
        assert any(f["finding_type"] == "provider_refusal" and f["severity"] == "high" for f in findings)
        assert not any(f["finding_type"] == "missing_tool_call" for f in findings)
    if refused == "recover":
        # Opus 4.8 is never a participant: its usage sits under the Opus 5.5 seat it rescued.
        claude_decisions = len(resolved)
        usage = json.loads((tmp_path / "exported/run/usage.json").read_text())
        assert "anthropic/claude-opus-4.8" not in usage["by_model"]
        claude = usage["by_model"]["anthropic/claude-opus-5.5"]
        assert claude["cost"] == pytest.approx(0.003 * claude_decisions)
        assert claude["own_model"]["attempt_count"] == 2 * claude_decisions
        assert claude["own_model"]["cost"] == pytest.approx(0.002 * claude_decisions)
        fallback = claude["fallback_models"]["anthropic/claude-opus-4.8"]
        assert (fallback["attempt_count"], fallback["decision_count"]) == (claude_decisions, claude_decisions)
        assert fallback["cost"] == pytest.approx(0.001 * claude_decisions)
        assert fallback["triggers"] == ["explicit_provider_refusal_after_same_model_retry"]
        assert usage["fallback_attempt_count"] == claude_decisions
        import csv
        rows = {row["openrouter_model_id"]: row for row in csv.DictReader(
            (tmp_path / "exported/analysis/tables/model_usage.csv").open())}
        assert "anthropic/claude-opus-4.8" not in rows
        claude_row = rows["anthropic/claude-opus-5.5"]
        assert int(claude_row["fallback_model_calls"]) == claude_decisions
        assert claude_row["fallback_models"] == "anthropic/claude-opus-4.8"
        assert float(claude_row["fallback_model_cost"]) == pytest.approx(0.001 * claude_decisions)
        assert int(claude_row["calls"]) == 3 * claude_decisions


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


def test_new_campaign_cannot_claim_the_previous_execution_policy(tmp_path, monkeypatch):
    store, _, _ = setup_job(tmp_path, monkeypatch)
    config = json.loads((Path(__file__).resolve().parents[4] / "campaigns" / "monopoly-long-v2-frontier-2026q4.json").read_text())
    config["execution_policy_version"] = "execution_policy_v1"
    with pytest.raises(ValueError, match="execution policy"):
        freeze(store, config)
    assert store.rows("SELECT * FROM campaigns") == []


def test_worker_rejects_old_policy_before_any_model_call(tmp_path, monkeypatch):
    store, _, _ = setup_job(tmp_path, monkeypatch)
    config = run_config(42, "previous-policy", max_turns=5)
    config["execution_policy_version"] = "execution_policy_v1"
    job = store.create_job(config, kind="smoke", key="previous-policy")
    with pytest.raises(ValueError, match="execution policy"):
        asyncio.run(play(store, job["job_id"], store.claim(job["job_id"])))
    assert store.rows("SELECT * FROM calls") == []
    assert not (store.root / "runs" / job["run_id"]).exists()


def test_freeze_failure_cannot_publish_campaign(tmp_path, monkeypatch):
    import time
    store, _, _ = setup_job(tmp_path, monkeypatch)
    store.set_state("preflight", {"passed": True, "created_at": time.time(), **build_identity()})
    config = json.loads((Path(__file__).resolve().parents[4] / "campaigns" / "monopoly-long-v2-frontier-2026q4.json").read_text())
    config.update(campaign_id="freeze-crash", execution_order_seed=42, seeds=[1])
    def fail(path, data):
        if path.name == "preflight.json":
            raise OSError("disk full")
        atomic_write(path, data)
    monkeypatch.setattr("monopoly_arena.cloud_campaign.atomic_write", fail)
    with pytest.raises(OSError):
        freeze(store, config)
    assert not store.rows("SELECT * FROM campaigns")
    assert not store.rows("SELECT * FROM cells")


def test_campaign_exports_serialize_revisions(tmp_path, monkeypatch):
    from monopoly_arena.campaign_export import export_campaign
    from monopoly_arena.worker import writer_lock
    import time
    store, _, _ = setup_job(tmp_path, monkeypatch)
    store.set_state("preflight", {"passed": True, "created_at": time.time(), **build_identity()})
    config = json.loads((Path(__file__).resolve().parents[4] / "campaigns" / "monopoly-long-v2-frontier-2026q4.json").read_text())
    config.update(campaign_id="export-test", execution_order_seed=42, seeds=[1])
    freeze(store, config)
    with writer_lock(store.root / "campaigns/export-test/.export.lock"):
        with pytest.raises(ValueError, match="already being prepared"):
            export_campaign(store, "export-test")
    first = export_campaign(store, "export-test")
    second = export_campaign(store, "export-test")
    assert first != second
    assert [r["revision"] for r in store.rows("SELECT revision FROM exports ORDER BY revision")] == [1, 2]


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


def test_resume_waits_for_old_writer_and_preserves_cancel(tmp_path, monkeypatch):
    from monopoly_arena.worker import writer_lock
    store, job, _ = setup_job(tmp_path, monkeypatch)
    job_id = job["job_id"]
    with writer_lock(store.root / "runs" / job["run_id"] / ".writer.lock"):
        store.pause(job_id, "operator")
        with pytest.raises(ValueError, match="finishing"):
            store.resume(job_id)
        store.pause(job_id, "provider_unavailable")
        assert store.job(job_id)["pause_reason"] == "operator"
    store.resume(job_id)
    assert store.job(job_id)["status"] == "recovering"
    store.execute("UPDATE jobs SET status='cancelled' WHERE job_id=?", (job_id,))
    store.pause(job_id, "provider_unavailable")
    assert store.job(job_id)["status"] == "cancelled"
    assert not store.rows("SELECT * FROM pauses WHERE job_id=?", (job_id,))


@pytest.mark.parametrize("error", ["disk", "sqlite"])
@pytest.mark.parametrize("cancelled", [False, True])
def test_worker_disk_full_pauses_without_overwriting_cancellation(tmp_path, monkeypatch, cancelled, error):
    import errno
    import sqlite3
    from monopoly_arena.worker import main
    store, job, execution = setup_job(tmp_path, monkeypatch)
    monkeypatch.setenv("MB_DATA_DIR", str(store.root))
    monkeypatch.setattr("sys.argv", ["worker", "--job", job["job_id"], "--execution", execution])
    async def fail(*args):
        if cancelled:
            store.execute("UPDATE jobs SET status='cancelled' WHERE job_id=?", (job["job_id"],))
        if error == "sqlite":
            raise sqlite3.OperationalError("database or disk is full")
        raise OSError(errno.ENOSPC, "disk full")
    monkeypatch.setattr("monopoly_arena.worker.play", fail)
    main()
    current = store.job(job["job_id"])
    assert current["status"] == ("cancelled" if cancelled else "paused")
    if not cancelled:
        assert current["pause_reason"] == "storage"
    assert store.rows("SELECT ended_at FROM executions WHERE execution_id=?", (execution,))[0]["ended_at"]


def test_finalizer_skips_locked_oldest_job(tmp_path, monkeypatch):
    from monopoly_arena.supervisor import Supervisor
    from monopoly_arena.worker import writer_lock
    store, first, _ = setup_job(tmp_path, monkeypatch)
    second = store.create_job(run_config(8, "second", max_turns=5), kind="smoke", key="second")
    store.execute("UPDATE jobs SET status='cancelled'")
    store.set_state("drain", True)
    launched = []
    monkeypatch.setattr("monopoly_arena.supervisor.subprocess.Popen", lambda command: launched.append(command))
    with writer_lock(store.root / "runs" / first["run_id"] / ".writer.lock"):
        Supervisor(store).tick()
    assert len(launched) == 1 and launched[0][-1] == second["job_id"]


def test_shutdown_cancels_inflight_preflight(tmp_path, monkeypatch):
    from monopoly_arena.supervisor import run_supervisor
    store, _, _ = setup_job(tmp_path, monkeypatch)
    stopped = False
    cancelled = False
    async def stalled(_):
        nonlocal stopped, cancelled
        stopped = True
        try:
            await asyncio.Event().wait()
        finally:
            cancelled = True
    monkeypatch.setattr("monopoly_arena.supervisor.preflight", stalled)
    monkeypatch.setattr("monopoly_arena.supervisor.Supervisor.tick", lambda self: None)
    asyncio.run(asyncio.wait_for(run_supervisor(store, lambda: stopped), timeout=3))
    assert cancelled


def test_cloud_outage_pause_resumes_with_one_durable_call_owner(tmp_path, monkeypatch):
    """PR #2's resolver call journal must not shadow the cloud ledger after a pause."""
    original = OpenRouterClient.__init__
    posts = 0
    def response(request):
        nonlocal posts
        if request.method == "POST":
            posts += 1
            if 5 <= posts <= 7:  # Three transport attempts fail mid-game, then the job pauses.
                return httpx.Response(503, json={"error": {"message": "upstream unavailable"}})
        return mock_transport().handle_request(request)
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=httpx.MockTransport(response))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    (tmp_path / "reference").mkdir()
    reference, baseline, reference_execution = setup_job(tmp_path / "reference", monkeypatch)
    posts = -10_000  # The reference game never sees the outage.
    asyncio.run(play(reference, baseline["job_id"], reference_execution))
    posts = 0
    (tmp_path / "paused").mkdir()
    store, job, execution = setup_job(tmp_path / "paused", monkeypatch)
    with pytest.raises(OperationalPause) as exc:
        asyncio.run(play(store, job["job_id"], execution))
    assert exc.value.reason == "provider_unavailable"
    store.pause(job["job_id"], exc.value.reason)
    store.resume(job["job_id"])
    asyncio.run(play(store, job["job_id"], store.claim(job["job_id"])))
    assert store.job(job["job_id"])["status"] == "finalizing"
    run = store.root / "runs" / job["run_id"]
    assert not (run / "calls").exists()
    for name in ("events.jsonl", "actions.jsonl"):
        assert (run / name).read_bytes() == (reference.root / "runs" / baseline["run_id"] / name).read_bytes()
    ledger = {row["call_id"]: row for row in store.rows("SELECT * FROM calls WHERE job_id=?", (job["job_id"],))}
    attempts = [attempt for row in read_jsonl_strict(run / "decisions.jsonl") if row["phase"] == "decision_resolved"
                for attempt in row["attempts"]]
    assert attempts and all(ledger[attempt["call_id"]]["state"] == "responded" for attempt in attempts)
    assert sum(row["state"] == "failed" for row in ledger.values()) == 3


@pytest.mark.parametrize("stage", ["summary", "analysis"])
def test_storage_full_during_finalization_stays_retryable(tmp_path, monkeypatch, stage):
    import errno
    import importlib.util
    from monopoly_arena.finalizer import finalize
    from monopoly_telemetry.run_files import RunFiles
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    full = OSError(errno.ENOSPC, "No space left on device")
    with monkeypatch.context() as patch:
        if stage == "summary":
            patch.setattr(RunFiles, "write_summary", lambda self, summary: (_ for _ in ()).throw(full))
        else:
            original_spec = importlib.util.spec_from_file_location
            def spec(name, location):
                result = original_spec(name, location)
                original_exec = result.loader.exec_module
                def load(module):
                    original_exec(module)
                    module.generate_analysis = lambda _: (_ for _ in ()).throw(full)
                result.loader.exec_module = load
                return result
            patch.setattr(importlib.util, "spec_from_file_location", spec)
        with pytest.raises(OSError):
            asyncio.run(finalize(store, job["job_id"]))
    assert store.job(job["job_id"])["status"] == "finalizing"
    assert not store.rows("SELECT * FROM exports")
    asyncio.run(finalize(store, job["job_id"]))
    final = store.job(job["job_id"])
    assert (final["status"], final["replay_status"], final["analysis_status"]) == ("completed", "passed", "completed")


@pytest.mark.parametrize("mode", ["credits", "byok", "byok_flag_only_in_generation", "upstream_without_flag",
                                  "byok_without_upstream", "byok_flag_only_in_completion"])
def test_generation_cost_backfills_the_physical_call_ledger(tmp_path, monkeypatch, mode):
    from monopoly_telemetry.execution_cost import execution_cost
    from monopoly_telemetry.run_files import build_run_files
    from monopoly_telemetry.usage import build_usage_report
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    count = 0
    def response(request):
        nonlocal count
        if request.method == "GET" and request.url.path.endswith("/generation"):
            data = {"id": request.url.params["id"], "total_cost": 1.25, "tokens_prompt": 10, "tokens_completion": 2}
            if mode != "credits":
                data.update(total_cost=0, is_byok=True, upstream_inference_cost=1.25)
            if mode == "byok_without_upstream":
                del data["upstream_inference_cost"]
            if mode == "byok_flag_only_in_completion":
                del data["is_byok"]  # The saved BYOK flag must survive the merge.
            return httpx.Response(200, json={"data": data})
        if request.method == "GET":
            return httpx.Response(200, json={"data": []})
        payload = json.loads(request.content)
        count += 1
        usage = {"prompt_tokens": 10, "completion_tokens": 2}
        if mode in {"byok_flag_only_in_generation", "byok_without_upstream"}:
            usage.update(cost=0)  # Looks like a known free call until generation reveals BYOK.
        elif mode == "upstream_without_flag":
            usage.update(cost=0, cost_details={"upstream_inference_cost": 1.25})
        elif mode == "byok_flag_only_in_completion":
            usage.update(cost=0, is_byok=True)  # Missing until generation supplies the upstream bill.
        return httpx.Response(200, json={"id": f"gen-{count}", "model": payload["model"], "provider": payload["provider"]["only"][0], "choices": [{"message": {"tool_calls": [{"id": "t", "type": "function", "function": {"name": "invalid", "arguments": "{}"}}]}}], "usage": usage})
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=httpx.MockTransport(response))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    calls = store.rows("SELECT * FROM calls WHERE job_id=?", (job["job_id"],))
    assert len(calls) == count > 0
    totals = execution_cost(calls)
    usage = build_usage_report(build_run_files(store.root / "runs", job["run_id"]))
    if mode == "byok_without_upstream":
        # BYOK evidence without the provider bill turns a reported $0 into an unknown cost.
        assert all(call["cost_status"] == "missing" and call["total_cost"] is None for call in calls)
        assert totals["known_total"] == 0 and totals["missing_calls"] == count
        assert usage["totals"]["cost"] is None and usage["missing_cost_attempt_count"] == count
        return
    assert all(call["cost_status"] == "known" and call["total_cost"] == 1.25 for call in calls)
    assert totals["known_total"] == 1.25 * count and totals["missing_calls"] == 0
    assert totals["provider_charge"] == (0 if mode == "credits" else 1.25 * count)
    # The ledger and usage accounting v2 must agree on the same calls.
    assert usage["totals"]["cost"] == pytest.approx(totals["known_total"])


def test_cloud_worker_applies_the_no_progress_guard(tmp_path, monkeypatch):
    from monopoly_arena import llm_runner, worker
    assert llm_runner.MAX_DECISIONS_PER_TURN == 1000
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    monkeypatch.setattr(worker, "MAX_DECISIONS_PER_TURN", 1)
    with pytest.raises(RuntimeError, match="No-progress guard"):
        asyncio.run(play(store, job["job_id"], execution))
    actions = read_jsonl_strict(store.root / "runs" / job["run_id"] / "actions.jsonl")
    assert actions and len({row["turn_index"] for row in actions}) == len(actions)


def test_exported_analysis_tables_include_byok_upstream_cost(tmp_path, monkeypatch):
    import csv
    from monopoly_arena.finalizer import finalize
    from monopoly_telemetry.export import unpack_verified
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    count = 0
    def response(request):
        nonlocal count
        if request.method == "GET":
            return httpx.Response(200, json={"data": []})
        payload = json.loads(request.content)
        count += 1
        usage = {"prompt_tokens": 10, "completion_tokens": 2, "cost": 0, "is_byok": True,
                 "cost_details": {"upstream_inference_cost": 1.25}}
        return httpx.Response(200, json={"id": f"gen-{count}", "model": payload["model"], "provider": payload["provider"]["only"][0], "choices": [{"message": {"tool_calls": [{"id": "t", "type": "function", "function": {"name": "invalid", "arguments": "{}"}}]}}], "usage": usage})
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=httpx.MockTransport(response))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    asyncio.run(finalize(store, job["job_id"]))
    assert store.job(job["job_id"])["status"] == "completed"
    unpack_verified(Path(store.rows("SELECT * FROM exports")[0]["path"]), tmp_path / "exported")
    rows = list(csv.DictReader((tmp_path / "exported/analysis/tables/model_usage.csv").open()))
    assert rows and sum(float(row["cost"]) for row in rows) == pytest.approx(1.25 * count)
    assert json.loads((tmp_path / "exported/cloud/usage_byok.json").read_text())["totals"]["cost"] == pytest.approx(1.25 * count)


def test_exported_analysis_keeps_unknown_cost_unknown(tmp_path, monkeypatch):
    import csv
    from monopoly_arena.finalizer import finalize
    from monopoly_telemetry.export import unpack_verified
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    count = 0
    def response(request):
        nonlocal count
        if request.method == "GET":
            return httpx.Response(200, json={"data": {}})  # Neither catalog nor generation reveals cost.
        payload = json.loads(request.content)
        count += 1
        usage = {"prompt_tokens": 10, "completion_tokens": 2, **({"cost": 1.25} if count % 2 else {})}
        return httpx.Response(200, json={"id": f"gen-{count}", "model": payload["model"], "provider": payload["provider"]["only"][0], "choices": [{"message": {"tool_calls": [{"id": "t", "type": "function", "function": {"name": "invalid", "arguments": "{}"}}]}}], "usage": usage})
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=httpx.MockTransport(response))
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    asyncio.run(finalize(store, job["job_id"]))
    assert store.job(job["job_id"])["status"] == "completed"
    unpack_verified(Path(store.rows("SELECT * FROM exports")[0]["path"]), tmp_path / "exported")
    tables = tmp_path / "exported/analysis/tables"
    rows = list(csv.DictReader((tables / "model_usage.csv").open()))
    known = sum(float(row["known_cost_subtotal"]) for row in rows)
    missing = sum(int(row["missing_cost_calls"]) for row in rows)
    assert known == pytest.approx(1.25 * ((count + 1) // 2)) and missing == count // 2 > 0
    assert any(row["cost"] == "" for row in rows)  # A model with an unknown call has no total.
    calls = list(csv.DictReader((tables / "per_call_usage.csv").open()))
    assert sum(row["cost"] == "" for row in calls) == missing
    reports = [path.read_text() for path in (tmp_path / "exported/analysis/reports").glob("*.md")]
    usage_report = next(text for text in reports if "## Model Usage" in text)
    assert "unknown ($" in usage_report


def test_supervisor_honors_frozen_campaign_concurrency(tmp_path, monkeypatch):
    import time
    from monopoly_arena.supervisor import Supervisor
    store, smoke, _ = setup_job(tmp_path, monkeypatch)
    store.execute("UPDATE jobs SET status='completed' WHERE job_id=?", (smoke["job_id"],))
    store.set_state("preflight", {"passed": True})
    store.execute("INSERT INTO campaigns VALUES(?,?,?,?,?,?,?)",
                  ("limited", encode({"concurrency": 2}), "sha", "running", time.time(), "test", "test"))
    for i in range(4):
        store.create_job(run_config(i, f"limited-{i}", max_turns=5), kind="campaign", key=f"limited-{i}",
                         campaign_id="limited", cell_index=i, rank=i)
    launched = []
    class Child:
        def __init__(self, command):
            launched.append(command)
        def poll(self):
            return None
    monkeypatch.setattr("monopoly_arena.supervisor.subprocess.Popen", Child)
    supervisor = Supervisor(store)
    supervisor.tick()
    supervisor.tick()
    assert len(launched) == 2  # Five global slots, but the campaign was frozen with concurrency 2.
    # A pause request changes status before the live worker reaches its boundary and exits.
    for command in launched:
        store.execute("UPDATE jobs SET status='paused' WHERE job_id=?", (command[command.index("--job") + 1],))
    supervisor.tick()
    assert len(launched) == 2


def test_failed_replay_verdict_survives_a_raised_finalization(tmp_path, monkeypatch):
    from monopoly_arena import replay_verification
    from monopoly_arena.finalizer import finalize
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    asyncio.run(play(store, job["job_id"], execution))
    build = replay_verification.build_replay_verification_reports
    def failing(run_files):
        reports = build(run_files)
        for report in reports.values():
            report["status"] = "failed"
        return reports
    monkeypatch.setattr(replay_verification, "build_replay_verification_reports", failing)
    asyncio.run(finalize(store, job["job_id"]))
    final = store.job(job["job_id"])
    assert (final["status"], final["replay_status"]) == ("failed", "failed")


def test_recovered_worker_reads_the_decision_log_once(tmp_path, monkeypatch):
    from monopoly_arena import worker
    store, job, execution = setup_job(tmp_path, monkeypatch)
    original = OpenRouterClient.__init__
    def init(self, **kwargs):
        original(self, **kwargs)
        self._client = httpx.AsyncClient(transport=mock_transport())
        self._api_key = "dummy"
    monkeypatch.setattr(OpenRouterClient, "__init__", init)
    record = CloudClient._record_result
    calls = 0
    def crash(self, call_id, result):
        nonlocal calls
        calls += 1
        if calls == 4:
            raise RuntimeError("crash after a saved response")
        record(self, call_id, result)
    monkeypatch.setattr(CloudClient, "_record_result", crash)
    with pytest.raises(RuntimeError):
        asyncio.run(play(store, job["job_id"], execution))
    monkeypatch.setattr(CloudClient, "_record_result", record)
    reads = []
    strict = worker.read_jsonl_strict
    def counting(path):
        reads.append(path.name)
        return strict(path)
    monkeypatch.setattr(worker, "read_jsonl_strict", counting)
    store.execute("UPDATE jobs SET status='recovering' WHERE job_id=?", (job["job_id"],))
    asyncio.run(play(store, job["job_id"], store.claim(job["job_id"])))
    assert store.job(job["job_id"])["status"] == "finalizing"
    assert reads.count("decisions.jsonl") == 1
    starts = [row["decision_id"] for row in strict(store.root / "runs" / job["run_id"] / "decisions.jsonl")
              if row["phase"] == "decision_started"]
    assert len(starts) == len(set(starts))


@pytest.mark.parametrize("action", ["pause", "cancel"])
@pytest.mark.parametrize("success", [True, False])
def test_control_during_inflight_request_blocks_next_post_and_retry(tmp_path, monkeypatch, action, success):
    """An admitted request can finish, but control must prevent every later POST."""
    store, job, _ = setup_job(tmp_path, monkeypatch)
    posts = []

    async def run():
        entered, release = asyncio.Event(), asyncio.Event()

        async def complete(self, **payload):
            posts.append(payload)
            entered.set()
            await release.wait()
            if success:
                return OpenRouterResult(True, 200, {"model": "test", "provider": "openai", "usage": {"cost": 0.01}}, None, None, "test")
            return OpenRouterResult(False, 503, {"error": {"message": "unavailable"}}, "unavailable", "http_error", "test")

        monkeypatch.setattr(OpenRouterClient, "create_chat_completion", complete)
        client = CloudClient(store, job["job_id"])
        payload = {"model": "test", "messages": [], "provider": {"only": ["openai"]}}
        try:
            client.begin_decision("in-flight")
            pending = asyncio.create_task(client.create_chat_completion(**payload))
            await asyncio.wait_for(entered.wait(), 2)
            if action == "pause":
                store.pause(job["job_id"], "operator")
            else:
                store.execute("UPDATE jobs SET status='cancelled' WHERE job_id=?", (job["job_id"],))
            release.set()
            if success:
                assert (await pending).ok
            else:
                with pytest.raises(OperationalPause):
                    await pending
            client.begin_decision("next-decision")
            with pytest.raises(OperationalPause):
                await client.create_chat_completion(**payload)
        finally:
            await client.aclose()

    asyncio.run(run())
    assert len(posts) == 1
    calls = store.rows("SELECT * FROM calls WHERE job_id=?", (job["job_id"],))
    assert len(calls) == 1 and calls[0]["state"] == ("responded" if success else "failed")
    assert store.job(job["job_id"])["status"] == ("paused" if action == "pause" else "cancelled")
