"""Run from the Python workspace with uv; sends four paid production-shaped probes."""
import asyncio
import json

from monopoly_arena.cloud_preflight import preflight
from monopoly_arena.execution_policy import data_root
from monopoly_arena.job_store import JobStore

if __name__ == "__main__":
    report = asyncio.run(preflight(JobStore(data_root())))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
