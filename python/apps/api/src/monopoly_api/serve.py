"""Container PID 1: coordinate draining before stopping HTTP service."""
import os
import signal
import subprocess
import sys
import time

from monopoly_arena.execution_policy import data_root
from monopoly_arena.job_store import JobStore


def main() -> None:
    store = JobStore(data_root())
    supervisor = subprocess.Popen([sys.executable, "-m", "monopoly_arena.supervisor"])
    web = subprocess.Popen([sys.executable, "-m", "uvicorn", "monopoly_api.main:app", "--host", "0.0.0.0", "--port", os.getenv("PORT", "8000"), "--workers", "1"])
    stopping = False

    def stop(*_: object) -> None:
        nonlocal stopping
        stopping = True
        store.set_state("drain", True)
        supervisor.terminate()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while not stopping and supervisor.poll() is None and web.poll() is None:
        time.sleep(0.5)
    unexpected = not stopping
    if unexpected:
        stop()
    try:
        supervisor.wait(timeout=max(1, int(os.getenv("RAILWAY_DEPLOYMENT_DRAINING_SECONDS", "180"))-5))
    except subprocess.TimeoutExpired:
        supervisor.kill()
        supervisor.wait()
    web.terminate()
    try:
        web.wait(timeout=4)
    except subprocess.TimeoutExpired:
        web.kill()
    if unexpected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
