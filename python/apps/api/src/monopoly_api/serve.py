"""Run the complete container, draining games before stopping HTTP and mock IO."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from urllib.request import urlopen

from monopoly_arena.execution_policy import data_root
from monopoly_arena.job_store import JobStore
from monopoly_arena.worker import writer_lock
from .bootstrap import prepare_runtime
from .paths import resolve_repo_root


def stop_process(process: subprocess.Popen | None, timeout: float) -> None:
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass
    # Children share the process group; a supervisor crash must not leave game
    # writers running after the top-level service exits.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def remove_abandoned_staging(root: Path) -> None:
    """A killed finalizer or campaign export cannot clean its staging tree. Under the
    runtime lock no export can be in progress, so any remaining tree is abandoned."""
    for pattern in ("package-*", "campaign-export-*"):
        for path in root.glob(pattern):
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)


def serve(root: Path, demo: bool) -> None:
    remove_abandoned_staging(root)
    store = JobStore(root)
    supervisor = web = mock = None
    stopping = False

    def stop(*_: object) -> None:
        nonlocal stopping
        stopping = True
        store.set_state("drain", True)
        if supervisor and supervisor.poll() is None:
            supervisor.terminate()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        if demo:
            mock = subprocess.Popen([sys.executable, str(resolve_repo_root() / "scripts/mock_openrouter_server.py")], start_new_session=True)
            deadline = time.monotonic() + 30
            while not stopping:
                if mock.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("Local demo gateway did not start")
                try:
                    with urlopen("http://127.0.0.1:8765/api/v1/models", timeout=1):
                        break
                except OSError:
                    time.sleep(0.1)
            if not store.rows("SELECT job_id FROM jobs WHERE idempotency_key='builtin-demo'"):
                from monopoly_arena.cloud_campaign import run_config
                store.create_job(run_config(42, "demo-smoke", max_turns=5), kind="smoke", key="builtin-demo")
        if stopping:
            return
        web = subprocess.Popen([sys.executable, "-m", "uvicorn", "monopoly_api.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000"), "--workers", "1"], start_new_session=True)
        supervisor = subprocess.Popen([sys.executable, "-m", "monopoly_arena.supervisor"], start_new_session=True)
        while not stopping:
            if any(p is not None and p.poll() is not None for p in (web, supervisor, mock)):
                raise RuntimeError("A required container process exited; restarting the service")
            time.sleep(0.5)
    finally:
        store.set_state("drain", True)
        stop_process(supervisor, max(1, int(os.getenv("RAILWAY_DEPLOYMENT_DRAINING_SECONDS", "180"))-5))
        stop_process(web, 4)
        stop_process(mock, 1)


def main() -> None:
    root = data_root()
    with writer_lock(root / ".runtime.lock"):
        serve(root, prepare_runtime(root))


if __name__ == "__main__":
    main()
