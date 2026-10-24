from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any

from monopoly_telemetry.run_files import build_run_files
from monopoly_telemetry.execution_cost import execution_cost_report
from monopoly_telemetry.inventory import write_inventory, inventory
from monopoly_telemetry.export import package_zip
from monopoly_telemetry.writer_jsonl import atomic_write
from .cloud_client import CloudClient
from .execution_policy import data_root
from .job_store import JobStore, encode
from .worker import make_runner, writer_lock


async def finalize(store: JobStore, job_id: str) -> None:
    job = store.job(job_id)
    if store.rows("SELECT * FROM exports WHERE scope='job' AND scope_id=?", (job_id,)):
        return
    files = build_run_files(store.root / "runs", job["run_id"])
    completed = job["status"] == "finalizing"
    if completed:
        client = CloudClient(store, job_id)
        client.observation_scope = "end"
        try:
            runner = make_runner(store, job, client, files, recover=True)
            if not runner._engine.is_game_over():
                raise ValueError("Finalizer requires a terminal engine")
            if job["kind"] == "campaign" and runner._engine.build_summary().get("reason") != "BANKRUPTCY":
                raise ValueError("Paper games must end by bankruptcy")
            await runner.run()
            from monopoly_telemetry.usage import build_usage_report
            atomic_write(store.root / "jobs" / job_id / "usage_byok.json", encode(build_usage_report(files, byok_aware=True)).encode())
            for path in (files.state_replay_report_path, files.artifact_replay_report_path):
                report = json.loads(path.read_text())
                if report.get("status") not in {"pass", "passed", "ok"}:
                    raise ValueError(f"Replay verification failed: {path.name}")
        except Exception as exc:
            completed = False
            store.execute("UPDATE jobs SET status='failed',pause_reason=? WHERE job_id=?", (f"Finalization: {exc}", job_id))
        finally:
            await client.aclose()
    directory = store.root / "jobs" / job_id
    calls = store.rows("SELECT * FROM calls WHERE job_id=?", (job_id,))
    atomic_write(directory / "execution_cost.json", encode(execution_cost_report(directory, calls)).encode())
    atomic_write(directory / "artifact_inventory.json", encode(inventory(files.run_dir)).encode())
    with tempfile.TemporaryDirectory(dir=store.root, prefix="package-") as temporary:
        staging = Path(temporary)
        if files.run_dir.exists():
            shutil.copytree(files.run_dir, staging / "run", ignore=shutil.ignore_patterns(".writer.lock"))
        if files.quality_dir and files.quality_dir.exists():
            shutil.copytree(files.quality_dir, staging / "quality_check")
        shutil.copytree(directory, staging / "cloud")
        # Compact only the export copy; live recovery evidence remains available until publication.
        journal = staging / "cloud" / "journal.jsonl"
        if journal.exists() and completed:
            from monopoly_telemetry.writer_jsonl import read_jsonl_strict
            rows = read_jsonl_strict(journal)
            for row in rows:
                for target in row["targets"]:
                    target.pop("data", None)
                    target.pop("previous", None)
            atomic_write(staging / "cloud" / "journal_index.jsonl", ("\n".join(encode(r) for r in rows)+"\n").encode())
            journal.unlink()
        frozen = {table: store.rows(f"SELECT * FROM {table} WHERE job_id=?", (job_id,)) for table in ("jobs", "executions", "commits", "calls", "pauses")}
        if completed:
            try:
                import importlib.util
                script = Path(__file__).resolve().parents[5] / "scripts" / "standardize_saved_games.py"
                spec = importlib.util.spec_from_file_location("cloud_analysis", script)
                if spec is None or spec.loader is None:
                    raise RuntimeError("Analysis module unavailable")
                module: Any = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.SAVED_ROOT = staging.parent
                module.GLOBAL_ARCHIVE_ROOT = staging.parent / "archive"
                module.generate_analysis(staging)
            except Exception as exc:
                completed = False
                store.execute("UPDATE jobs SET status='failed',analysis_status='failed',pause_reason=? WHERE job_id=?", (f"Analysis: {exc}", job_id))
                atomic_write(staging / "cloud" / "analysis_error.json", encode({"error": str(exc)}).encode())
                if (directory / "journal.jsonl").exists():
                    shutil.copyfile(directory / "journal.jsonl", staging / "cloud" / "journal.jsonl")
        if not (staging / "saved_game_manifest.json").exists():
            atomic_write(staging / "saved_game_manifest.json", encode({"run_id": job["run_id"], "kind": job["kind"], "status": "completed" if completed else store.job(job_id)["status"]}).encode())
        ended_at = time.time()
        final_status = "completed" if completed else store.job(job_id)["status"]
        frozen["jobs"] = [{**store.job(job_id), "status": final_status, "ended_at": ended_at, "export_status": "ready", "replay_status": "passed" if completed else "failed", "analysis_status": "completed" if completed else "unavailable"}]
        atomic_write(staging / "cloud" / "ledger.json", encode(frozen).encode())
        manifest = write_inventory(staging)
        export_id = job_id + "-1"
        destination = store.root / "exports" / f"{export_id}.zip"
        package_zip(staging, destination)
        with store.connect() as db:
            db.execute("INSERT INTO exports VALUES(?,?,?,?,?,?,?,?,?)", (export_id, "job", job_id, 1, "completed" if completed else "diagnostic", str(destination), destination.stat().st_size, manifest["tree_sha256"], time.time()))
            db.execute("UPDATE jobs SET status=?,export_status='ready',replay_status=?,analysis_status=?,ended_at=? WHERE job_id=?", (final_status, "passed" if completed else "failed", "completed" if completed else "unavailable", ended_at, job_id))
        if completed:
            atomic_write(directory / "journal_index.jsonl", (staging / "cloud" / "journal_index.jsonl").read_bytes())
            (directory / "journal.jsonl").unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    args = parser.parse_args()
    store = JobStore(data_root())
    job = store.job(args.job)
    with writer_lock(store.root / "runs" / job["run_id"] / ".writer.lock"):
        try:
            asyncio.run(finalize(store, args.job))
        except Exception as exc:
            # Packaging/storage failures remain retryable, but must not create a
            # tight crash loop that starves other games' finalizers.
            store.set_state("finalize_retry:" + args.job, time.time() + 60)
            store.execute("UPDATE jobs SET pause_reason=? WHERE job_id=?", (f"Export pending: {type(exc).__name__}: {exc}", args.job))
            store.audit("finalizer_failed", {"job_id": args.job, "error": str(exc)})
            raise


if __name__ == "__main__":
    main()
