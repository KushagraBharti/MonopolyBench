"""Snapshot campaign evidence without hiding failed, cancelled or unstarted cells."""
from pathlib import Path
import tempfile
import time
import uuid
from typing import Any

from monopoly_telemetry.execution_cost import execution_cost
from monopoly_telemetry.export import package_zip, unpack_verified
from monopoly_telemetry.inventory import write_inventory
from monopoly_telemetry.writer_jsonl import atomic_write
from .job_store import JobStore, encode


def export_campaign(store: JobStore, campaign_id: str) -> str:
    with store.connect() as db:
        db.execute("BEGIN")
        campaign = db.execute("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
        if not campaign:
            raise KeyError(campaign_id)
        evidence: dict[str, Any] = {"campaign": dict(campaign)}
        for table in ("jobs", "cells", "campaign_amendments"):
            evidence[table] = [dict(row) for row in db.execute(f"SELECT * FROM {table} WHERE campaign_id=?", (campaign_id,))]
        calls = [dict(row) for row in db.execute("SELECT calls.* FROM calls JOIN jobs USING(job_id) WHERE jobs.campaign_id=?", (campaign_id,))]
        packages = [dict(row) for row in db.execute("SELECT exports.*,jobs.run_id,jobs.cell_index FROM exports JOIN jobs ON jobs.job_id=exports.scope_id WHERE exports.scope='job' AND jobs.campaign_id=?", (campaign_id,))]
        evidence["launch_order"] = [dict(row) for row in db.execute("SELECT executions.* FROM executions JOIN jobs USING(job_id) WHERE jobs.campaign_id=? ORDER BY executions.started_at", (campaign_id,))]
        revision = db.execute("SELECT COALESCE(MAX(revision),0)+1 FROM exports WHERE scope='campaign' AND scope_id=?", (campaign_id,)).fetchone()[0]
    with tempfile.TemporaryDirectory(dir=store.root, prefix="campaign-export-") as tmp:
        root = Path(tmp)
        atomic_write(root / "campaign.json", encode(evidence).encode())
        atomic_write(root / "cost.json", encode(execution_cost(calls)).encode())
        path = store.root / "campaigns" / campaign_id / "preflight.json"
        if path.exists():
            atomic_write(root / "preflight.json", path.read_bytes())
        manifest_path = path.parent / "freeze_manifest.json"
        if manifest_path.exists():
            atomic_write(root / "freeze_manifest.json", manifest_path.read_bytes())
        for package in packages:
            unpack_verified(Path(package["path"]), root / campaign_id / f"{package['cell_index']}-{package['run_id']}")
        manifest = write_inventory(root)
        export_id = uuid.uuid4().hex
        destination = store.root / "exports" / f"{export_id}.zip"
        package_zip(root, destination)
        store.execute("INSERT INTO exports VALUES(?,?,?,?,?,?,?,?,?)", (export_id, "campaign", campaign_id, revision, "campaign", str(destination), destination.stat().st_size, manifest["tree_sha256"], time.time()))
    return export_id
