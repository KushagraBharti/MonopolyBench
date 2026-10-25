from __future__ import annotations

import argparse
import asyncio
from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import time
from typing import Iterator, Any

from monopoly_telemetry.writer_jsonl import atomic_write, read_jsonl_strict
from .cloud_client import CloudClient
from .execution_policy import OperationalPause, VERSION, data_root, storage_full
from .job_store import JobStore, encode
from .journal import Journal, JournalRunFiles
from .llm_runner import MAX_DECISIONS_PER_TURN, LlmRunner
from .player_config import build_single_player_config


@contextmanager
def writer_lock(path: Path) -> Iterator[None]:
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def build_identity() -> dict[str, Any]:
    path = Path(os.getenv("MB_BUILD_INFO", "build_info.json"))
    if path.exists():
        identity = json.loads(path.read_text())
        if os.getenv("MB_IMAGE_DIGEST"):
            identity["image_digest"] = os.environ["MB_IMAGE_DIGEST"]
        return identity
    import subprocess
    return {"git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "image_digest": os.getenv("MB_IMAGE_DIGEST", "development")}


def make_runner(store: JobStore, job: dict, client: CloudClient, files: Any, *, recover: bool) -> LlmRunner:
    config = json.loads(job["config_json"])
    players = [build_single_player_config(**p) for p in config["players"]]
    return LlmRunner(seed=config["seed"], players=players, run_id=job["run_id"], openrouter=client,
                     run_files=files, max_turns=config["max_turns"], event_delay_s=0,
                     max_trade_exchanges=20, max_auction_actions=200,
                     resume_actions=read_jsonl_strict(files.actions_path) if recover else None,
                     resume_events=read_jsonl_strict(files.events_path) if recover else None,
                     resume_at_boundary=True)


async def play(store: JobStore, job_id: str, execution_id: str) -> None:
    job = store.job(job_id)
    import hashlib
    if hashlib.sha256(job["config_json"].encode()).hexdigest() != job["config_sha256"]:
        raise ValueError("Frozen job configuration hash mismatch")
    frozen_path = store.root / "jobs" / job_id / "job.json"
    if not frozen_path.exists():
        atomic_write(frozen_path, encode(job).encode())
    elif json.loads(frozen_path.read_text())["config_sha256"] != job["config_sha256"]:
        raise ValueError("Frozen job file contradicts ledger")
    identity = build_identity()
    if any(job[key] != identity.get(key) for key in ("git_sha", "image_digest")):
        raise ValueError("Recovery code identity differs from frozen job")
    journal = Journal(store, job_id, execution_id)
    journal.recover()
    files = JournalRunFiles.create(journal, job["run_id"])
    client = CloudClient(store, job_id)
    recover = files.run_config_path.exists()
    if recover:
        store.execute("UPDATE jobs SET recovered=1 WHERE job_id=?", (job_id,))
    else:
        pricing = await client.get_models()
        from dataclasses import asdict
        atomic_write(journal.directory / "pricing_start.json", encode(asdict(pricing)).encode())
        endpoints = {}
        for player in json.loads(job["config_json"])["players"]:
            model = player["openrouter_model_id"]
            endpoints[model] = asdict(await client._get_json(path=f"/models/{model}/endpoints", auth_required=False))
        import platform
        from .player_config import DEFAULT_SYSTEM_PROMPT
        source_hashes = {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() for name in ("prompting.py", "decision_resolver.py", "player_config.py", "execution_policy.py")}
        atomic_write(journal.directory / "execution_manifest.json", encode({**identity, "execution_policy_version": VERSION, "python": platform.python_version(), "endpoints": endpoints, "source_sha256": source_hashes, "prompt_sha256": hashlib.sha256(DEFAULT_SYSTEM_PROMPT.encode()).hexdigest(), "kind": job["kind"]}).encode())
    if recover:
        runner = make_runner(store, job, client, files, recover=True)
    else:
        with journal.transition("initialize"):
            runner = make_runner(store, job, client, files, recover=False)

    async def heartbeat() -> None:
        while True:
            store.execute("UPDATE executions SET heartbeat_at=?,pid=? WHERE execution_id=?", (time.time(), os.getpid(), execution_id))
            await asyncio.sleep(10)

    heart = asyncio.create_task(heartbeat())
    # A resumed decision already has its canonical decision_started row; read the log once.
    started = {row["decision_id"] for row in read_jsonl_strict(files.decisions_path)
               if row.get("phase") == "decision_started"} if recover else set()
    turn = runner._engine.state.turn_index
    decisions_this_turn = sum(row.get("turn_index") == turn for row in read_jsonl_strict(files.actions_path)) if recover else 0
    try:
        while not runner._engine.is_game_over():
            client.boundary()
            _, events, decision, _ = runner._engine.advance_until_decision(max_steps=1)
            snapshot = runner.get_snapshot()
            if events:
                with journal.transition("advance", snapshot=snapshot):
                    for event in events:
                        files.write_event(event)
                        runner._prompt_memory.update(event)
                        if event["type"] in {"LLM_DECISION_REQUESTED", "TURN_ENDED", "GAME_ENDED"}:
                            files.write_snapshot(snapshot)
            if decision is None:
                continue
            if decision["turn_index"] != turn:
                turn, decisions_this_turn = decision["turn_index"], 0
            decisions_this_turn += 1
            if decisions_this_turn > MAX_DECISIONS_PER_TURN:
                raise RuntimeError(f"No-progress guard: more than {MAX_DECISIONS_PER_TURN} decisions in one turn; game is incomplete")
            client.begin_decision(decision["decision_id"])

            async def log(entry: dict[str, Any]) -> None:
                if entry.get("phase") == "decision_started":
                    if entry["decision_id"] in started:
                        return
                    started.add(entry["decision_id"])
                files.write_decision(entry)

            outcome = await runner._resolve_decision(decision, log)
            _, events, _, _ = runner._engine.apply_action(outcome.action, decision_meta=outcome.decision_meta)
            snapshot = runner.get_snapshot()
            with journal.transition("action", decision["decision_id"], snapshot):
                files.write_action({"decision_id": decision["decision_id"], "actor_player_id": decision["player_id"], "decision_type": decision["decision_type"], "turn_index": decision["turn_index"], "action": outcome.action, "decision_meta": outcome.decision_meta})
                files.write_decision(runner._build_decision_log_entry(decision=decision, player_config=runner._player_configs[decision["player_id"]], phase="decision_resolved", action=outcome.action, attempts=outcome.attempts, retry_used=outcome.retry_used, fallback_used=outcome.fallback_used, fallback_reason=outcome.fallback_reason, action_events=events, applied=True, sequence_meta=outcome.sequence_meta, automated=outcome.automated))
                for event in events:
                    files.write_event(event)
                    runner._prompt_memory.update(event)
                    if event["type"] in {"LLM_DECISION_REQUESTED", "TURN_ENDED", "GAME_ENDED"}:
                        files.write_snapshot(snapshot)
            store.execute("DELETE FROM pauses WHERE job_id=?", (job_id,))
        store.execute("UPDATE jobs SET status='finalizing',outcome_json=? WHERE job_id=? AND status='running'", (encode(runner._engine.build_summary()), job_id))
    finally:
        heart.cancel()
        await client.aclose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--execution", required=True)
    args = parser.parse_args()
    store = JobStore(data_root())
    job = store.job(args.job)
    signal.signal(signal.SIGTERM, lambda *_: store.set_state("drain", True))
    try:
        with writer_lock(store.root / "runs" / job["run_id"] / ".writer.lock"):
            try:
                asyncio.run(play(store, args.job, args.execution))
            except OperationalPause as exc:
                store.pause(args.job, exc.reason, str(exc))
            except Exception as exc:
                if storage_full(exc):
                    store.pause(args.job, "storage", str(exc))
                else:
                    store.execute("UPDATE jobs SET status='failed',pause_reason=?,ended_at=? WHERE job_id=? AND status NOT IN ('cancelled','completed')", (f"{type(exc).__name__}: {exc}", time.time(), args.job))
                store.audit("worker_failed", {"job_id": args.job, "error": str(exc)})
            finally:
                store.execute("UPDATE executions SET ended_at=?,exit_status=? WHERE execution_id=?", (time.time(), store.job(args.job)["status"], args.execution))
    except BlockingIOError:
        return


if __name__ == "__main__":
    main()
