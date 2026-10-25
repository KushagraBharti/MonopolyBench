"""Persistent local credentials and explicit, isolated demo configuration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets

from monopoly_arena.execution_policy import data_root
from monopoly_telemetry.writer_jsonl import atomic_write

SECRET_NAMES = ("MB_DASHBOARD_PASSWORD", "MB_SESSION_SECRET", "MB_EXPORT_TOKEN")
DEFAULT_DASHBOARD_PASSWORD = "monopoly"


def prepare_runtime(root: Path) -> bool:
    root.mkdir(parents=True, exist_ok=True)
    demo = os.getenv("MB_DEMO", "0") == "1"
    mode = "demo" if demo else "production"
    marker = root / "runtime_mode.json"
    if marker.exists() and json.loads(marker.read_text())["mode"] != mode:
        raise ValueError("This volume belongs to a different runtime mode. Use a separate volume for demo and real games.")
    if demo and not marker.exists() and (root / "ledger.sqlite").exists():
        raise ValueError("Demo mode requires its own fresh volume; existing research data cannot be converted to demo data.")
    atomic_write(marker, json.dumps({"mode": mode}).encode())

    path = root / "runtime_secrets.json"
    saved = json.loads(path.read_text()) if path.exists() else {}
    values = {name: os.getenv(name) or saved.get(name) or secrets.token_urlsafe(32) for name in SECRET_NAMES[1:]}
    values["MB_DASHBOARD_PASSWORD"] = os.getenv("MB_DASHBOARD_PASSWORD") or DEFAULT_DASHBOARD_PASSWORD
    if any(not isinstance(value, str) for value in values.values()) or len(values["MB_SESSION_SECRET"]) < 32:
        raise ValueError("Runtime secrets must be strings; MB_SESSION_SECRET must contain at least 32 characters")
    atomic_write(path, json.dumps(values).encode())
    path.chmod(0o600)
    os.environ.update(values)
    if values["MB_DASHBOARD_PASSWORD"] == DEFAULT_DASHBOARD_PASSWORD:
        print("Dashboard login: password 'monopoly' (no username).", flush=True)
    else:
        print("Dashboard login: password set by MB_DASHBOARD_PASSWORD (no username).", flush=True)
    if demo:
        # Explicitly replace inherited credentials and routes before any child
        # process starts. Test mode also rejects every non-loopback gateway.
        os.environ.update(MB_TEST_MODE="1", OPENROUTER_API_KEY="mock-only",
                          MB_OPENROUTER_BASE_URL="http://127.0.0.1:8765/api/v1", MB_MOCK_PORT="8765",
                          MB_DISK_RESERVE_GB="0")
        print("DEMO MODE: local mock models only; no paid provider requests. Data is excluded from research.", flush=True)
    elif not os.getenv("OPENROUTER_API_KEY"):
        print("Set OPENROUTER_API_KEY to run real models. The dashboard is available; new games will wait for preflight.", flush=True)
    return demo


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--show-password", action="store_true")
    group.add_argument("--show-export-token", action="store_true")
    args = parser.parse_args()
    name = "MB_DASHBOARD_PASSWORD" if args.show_password else "MB_EXPORT_TOKEN"
    values = json.loads((data_root() / "runtime_secrets.json").read_text())
    print(values[name])


if __name__ == "__main__":
    main()
