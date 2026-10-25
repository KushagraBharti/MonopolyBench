"""Run concurrent game processes against loopback fixtures, optionally killing one.

Results live in a temporary directory printed at completion. No production keys
or host URLs are inherited by the child processes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

from monopoly_arena.cloud_campaign import run_config
from monopoly_arena.job_store import JobStore
from monopoly_telemetry.export import unpack_verified


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=5)
    parser.add_argument("--turns", type=int, default=5, help="0 means uncapped")
    parser.add_argument("--interrupt", action="store_true")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="monopoly-cloud-soak-"))
    repo = Path(__file__).resolve().parents[1]
    build = root / "build.json"
    build.write_text(json.dumps({"git_sha": "mock-soak", "image_digest": "mock-soak"}))
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {key: value for key, value in os.environ.items() if not any(word in key.upper() for word in ("TOKEN", "SECRET", "API_KEY", "PASSWORD")) and not key.startswith("MB_")}
    env.update(MB_TEST_MODE="1", MB_OPENROUTER_BASE_URL=f"http://127.0.0.1:{port}/api/v1", MB_MOCK_PORT=str(port), OPENROUTER_API_KEY="mock-only", MB_DATA_DIR=str(root / "data"), MB_DISK_RESERVE_GB="0", MB_BUILD_INFO=str(build))
    os.environ["MB_BUILD_INFO"] = str(build)
    store = JobStore(root / "data")
    children: list[subprocess.Popen] = []
    with (root / "mock.log").open("w") as log:
        mock = subprocess.Popen([sys.executable, str(repo / "scripts/mock_openrouter_server.py")], env=env, stdout=log, stderr=log)
        try:
            for _ in range(100):
                try:
                    with urlopen(env["MB_OPENROUTER_BASE_URL"]+"/models", timeout=1):
                        break
                except OSError:
                    if mock.poll() is not None:
                        raise RuntimeError("Mock server failed; inspect "+str(root / "mock.log"))
                    time.sleep(0.1)
            jobs = []
            handles = []
            for i in range(args.games):
                job = store.create_job(run_config(100+i, f"soak-{i}", max_turns=args.turns or None), kind="smoke", key=f"soak-{i}")
                jobs.append(job)
                execution = store.claim(job["job_id"])
                handle = (root / f"worker-{i}.log").open("w")
                handles.append(handle)
                children.append(subprocess.Popen([sys.executable, "-m", "monopoly_arena.worker", "--job", job["job_id"], "--execution", execution], env=env, stdout=handle, stderr=handle))
            deadline = time.monotonic()+args.timeout
            interrupted = False
            while any(p.poll() is None for p in children):
                if time.monotonic() > deadline:
                    raise TimeoutError("Soak timed out; evidence at "+str(root))
                if args.interrupt and not interrupted:
                    job = jobs[0]
                    if store.rows("SELECT * FROM calls WHERE job_id=?", (job["job_id"],)) and children[0].poll() is None:
                        children[0].kill()
                        children[0].wait()
                        store.execute("UPDATE jobs SET status='recovering' WHERE job_id=?", (job["job_id"],))
                        execution = store.claim(job["job_id"])
                        children[0] = subprocess.Popen([sys.executable, "-m", "monopoly_arena.worker", "--job", job["job_id"], "--execution", execution], env=env, stdout=handles[0], stderr=handles[0])
                        interrupted = True
                time.sleep(0.1)
            for job in jobs:
                current = store.job(job["job_id"])
                if current["status"] != "finalizing":
                    raise AssertionError(current)
                subprocess.run([sys.executable, "-m", "monopoly_arena.finalizer", "--job", job["job_id"]], env=env, check=True, stdout=log, stderr=log, timeout=300)
                current = store.job(job["job_id"])
                if current["status"] != "completed":
                    raise AssertionError(current)
                package = store.rows("SELECT * FROM exports WHERE scope_id=?", (job["job_id"],))[0]
                unpack_verified(Path(package["path"]), root / "verified" / job["run_id"])
            for handle in handles:
                handle.close()
            print(json.dumps({"games": args.games, "turns": args.turns or None, "interrupted": interrupted, "verified": True, "evidence": str(root)}))
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill()
                    child.wait()
            mock.terminate()
            mock.wait(timeout=5)


if __name__ == "__main__":
    main()
