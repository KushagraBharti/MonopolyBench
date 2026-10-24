from __future__ import annotations

import json
from pathlib import Path
import re
import secrets
import shutil
import time

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from monopoly_arena.cloud_campaign import freeze, amend, run_config
from monopoly_arena.cloud_preflight import preflight
from monopoly_arena.execution_policy import MODELS, data_root
from monopoly_arena.job_store import JobStore
from monopoly_telemetry.execution_cost import execution_cost
from monopoly_telemetry.inventory import safe_path
from .auth import Auth, COOKIE, SESSION_SECONDS
from .live import live, LiveHub
from .paths import resolve_repo_root


class Login(BaseModel):
    password: str


class Smoke(BaseModel):
    model_config = ConfigDict(extra="forbid")
    models: list[str] = Field(default_factory=lambda: list(MODELS))
    effort: str = "medium"
    max_turns: int = Field(default=5, ge=5, le=10)
    count: int = Field(default=1, ge=1, le=20)


class Launch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preparation_id: str
    idempotency_key: str = Field(min_length=8, max_length=128)


class Amendment(BaseModel):
    seeds: list[int]
    reason: str


def create_cloud_app(root: Path | None = None) -> FastAPI:
    store = JobStore(root or data_root())
    auth = Auth()
    app = FastAPI(title="MonopolyBench cloud", docs_url=None, redoc_url=None, openapi_url=None)
    app.middleware("http")(auth.middleware)
    app.state.store = store
    hub = LiveHub(store)

    @app.exception_handler(KeyError)
    async def missing(_: Request, exc: KeyError):
        return JSONResponse({"detail": "Not found"}, status_code=404)

    @app.exception_handler(ValueError)
    async def invalid(_: Request, exc: ValueError):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.get("/api/health")
    def health():
        from monopoly_arena.worker import build_identity
        return {"ok": True, "mode": "cloud", "git_sha": build_identity()["git_sha"]}

    @app.post("/api/auth/login")
    def login(body: Login):
        response = JSONResponse({"ok": True})
        response.set_cookie(COOKIE, auth.login(body.password), httponly=True, secure=True, samesite="lax", max_age=SESSION_SECONDS)
        return response

    @app.post("/api/auth/logout")
    def logout():
        response = JSONResponse({"ok": True})
        response.delete_cookie(COOKIE, secure=True, httponly=True, samesite="lax")
        return response

    @app.get("/api/status")
    def status():
        return {"account_stop": store.state("account_stop"), "drain": store.state("drain", False), "free_disk": shutil.disk_usage(store.root).free, "active_workers": len(store.rows("SELECT job_id FROM jobs WHERE status='running'")), "cost": execution_cost(store.rows("SELECT * FROM calls")), "preflight": store.state("preflight"), "models": MODELS}

    @app.get("/api/jobs")
    def jobs(status: str | None = None, kind: str | None = None, campaign: str | None = None, search: str = "", cursor: int = 0, archived: bool = False):
        rows = store.rows("""SELECT * FROM jobs WHERE (? IS NULL OR status=?) AND (? IS NULL OR kind=?)
            AND (? IS NULL OR campaign_id=?) AND archived=? AND (run_id LIKE ? OR config_json LIKE ? OR campaign_id LIKE ?)
            ORDER BY created_at DESC,job_id LIMIT 50 OFFSET ?""", (status, status, kind, kind, campaign, campaign, int(archived), "%"+search+"%", "%"+search+"%", "%"+search+"%", max(0, cursor)))
        return {"jobs": [detail(row["job_id"]) for row in rows], "next_cursor": cursor+50 if len(rows) == 50 else None}

    @app.get("/api/jobs/{job_id}")
    def detail(job_id: str):
        job = store.job(job_id)
        job["config"] = json.loads(job.pop("config_json"))
        job["outcome"] = json.loads(job.pop("outcome_json") or "null")
        job["cost"] = execution_cost(store.rows("SELECT * FROM calls WHERE job_id=?", (job_id,)))
        job["pauses"] = store.rows("SELECT * FROM pauses WHERE job_id=?", (job_id,))
        job["allowed_actions"] = ({"queued": ["cancel"], "running": ["pause", "cancel"], "recovering": ["cancel"], "paused": ["resume", "cancel"], "completed": ["archive"], "failed": ["archive"], "cancelled": ["archive"]}).get(job["status"], [])
        commits = store.rows("SELECT * FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job_id,))
        job["snapshot"] = json.loads((store.root / commits[0]["snapshot_path"]).read_text()) if commits and commits[0]["snapshot_path"] else None
        job["commit_seq"] = commits[0]["commit_seq"] if commits else 0
        job["slow"] = job["status"] == "running" and time.time() - (job["last_progress_at"] or job["started_at"] or job["created_at"]) > 300
        return job

    @app.post("/api/jobs/{job_id}/{action}")
    def control(job_id: str, action: str):
        job = detail(job_id)
        if action not in job["allowed_actions"]:
            raise HTTPException(409, "Action is not allowed in this state")
        if action == "pause":
            store.pause(job_id, "operator", expected_status="running")
        elif action == "resume":
            store.resume(job_id)
        elif action == "cancel":
            with store.connect() as db:
                changed = db.execute("UPDATE jobs SET status='cancelled',ended_at=? WHERE job_id=? AND status=?", (time.time(), job_id, job["status"])).rowcount
                if not changed:
                    raise HTTPException(409, "Job state changed; refresh before retrying")
        elif action == "archive":
            store.execute("UPDATE jobs SET archived=1 WHERE job_id=?", (job_id,))
        store.audit(action, {"job_id": job_id}, "dashboard")
        return detail(job_id)

    @app.post("/api/resume-all")
    def resume_all():
        store.set_state("account_stop", None)
        waiting = []
        for job in store.rows("SELECT job_id FROM jobs WHERE status='paused'"):
            try:
                store.resume(job["job_id"])
            except ValueError:
                waiting.append(job["job_id"])
        store.audit("resume_all", {}, "dashboard")
        return {"ok": True, "waiting_for_worker": waiting}

    @app.post("/api/smoke/prepare")
    def prepare(body: Smoke):
        preparation = secrets.token_hex(16)
        configs = [run_config(secrets.randbits(32), f"smoke-{preparation}-{i}", body.models, body.effort, body.max_turns) for i in range(body.count)]
        result = {"preparation_id": preparation, "configs": configs, "created_at": time.time(), "cost_estimate": None, "preflight": store.state("preflight")}
        store.set_state("prepare:"+preparation, result)
        return result

    @app.post("/api/smoke")
    def smoke(body: Launch):
        prepared = store.state("prepare:"+body.preparation_id)
        if not prepared:
            raise HTTPException(404, "Preparation not found")
        with store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            key = "launch:" + body.idempotency_key
            previous = db.execute("SELECT value_json FROM account_state WHERE key=?", (key,)).fetchone()
            if previous and json.loads(previous[0]) != body.preparation_id:
                raise ValueError("Idempotency key already belongs to another preparation")
            db.execute("INSERT OR IGNORE INTO account_state VALUES(?,?,?)", (key, json.dumps(body.preparation_id), time.time()))
        jobs = [store.create_job(config, kind="smoke", key=f"smoke:{body.preparation_id}:{i}") for i, config in enumerate(prepared["configs"])]
        store.audit("smoke_launch", {"jobs": [j["job_id"] for j in jobs]}, "dashboard")
        return jobs

    def campaign_file(campaign_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", campaign_id):
            raise HTTPException(400, "Invalid campaign id")
        return resolve_repo_root() / "campaigns" / f"{campaign_id}.json"

    @app.get("/api/campaigns")
    def campaigns():
        frozen = {row["campaign_id"]: row for row in store.rows("SELECT * FROM campaigns")}
        for path in (resolve_repo_root() / "campaigns").glob("*.json"):
            config = json.loads(path.read_text())
            if config.get("campaign_config_version") == "long_horizon_campaign_config_v2":
                frozen.setdefault(config["campaign_id"], {"campaign_id": config["campaign_id"], "status": "draft", "config_json": json.dumps(config)})
        return list(frozen.values())

    @app.get("/api/campaigns/{campaign_id}")
    def campaign(campaign_id: str):
        rows = store.rows("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,))
        if not rows:
            path = campaign_file(campaign_id)
            if not path.exists():
                raise KeyError(campaign_id)
            return {"campaign_id": campaign_id, "status": "draft", "config": json.loads(path.read_text()), "cells": []}
        return {**rows[0], "config": json.loads(rows[0]["config_json"]), "cells": store.rows("SELECT cells.*,jobs.status AS job_status FROM cells LEFT JOIN jobs ON cells.job_id=jobs.job_id WHERE cells.campaign_id=? ORDER BY cells.execution_rank", (campaign_id,)), "amendments": store.rows("SELECT * FROM campaign_amendments WHERE campaign_id=?", (campaign_id,))}

    @app.post("/api/campaigns/{campaign_id}/freeze")
    def freeze_campaign(campaign_id: str):
        return freeze(store, json.loads(campaign_file(campaign_id).read_text()))

    @app.post("/api/campaigns/{campaign_id}/amend")
    def amend_campaign(campaign_id: str, body: Amendment):
        amend(store, campaign_id, body.seeds, body.reason)
        return campaign(campaign_id)

    @app.post("/api/campaigns/{campaign_id}/{action}")
    def campaign_control(campaign_id: str, action: str):
        current = campaign(campaign_id)
        if action not in {"run", "pause"} or current["status"] == "draft":
            if action == "export" and current["status"] != "draft":
                from monopoly_arena.campaign_export import export_campaign
                return {"export_id": export_campaign(store, campaign_id)}
            raise HTTPException(409, "Freeze the campaign before running it")
        store.execute("UPDATE campaigns SET status=? WHERE campaign_id=?", ("running" if action == "run" else "paused", campaign_id))
        store.audit("campaign_"+action, {"campaign_id": campaign_id}, "dashboard")
        return campaign(campaign_id)

    @app.post("/api/preflight/run")
    async def run_preflight():
        return await preflight(store)

    @app.get("/api/preflight/latest")
    def latest_preflight():
        return store.state("preflight")

    @app.get("/api/exports")
    def exports():
        return store.rows("SELECT exports.*,jobs.kind AS job_kind,jobs.run_id,jobs.cell_index,COALESCE(jobs.campaign_id,CASE WHEN exports.scope='campaign' THEN exports.scope_id END) AS campaign_id FROM exports LEFT JOIN jobs ON exports.scope_id=jobs.job_id ORDER BY exports.created_at")

    @app.get("/api/exports/{export_id}/download")
    def download(export_id: str):
        rows = store.rows("SELECT * FROM exports WHERE export_id=?", (export_id,))
        if not rows:
            raise KeyError(export_id)
        store.audit("export_download", {"export_id": export_id})
        return FileResponse(rows[0]["path"], media_type="application/zip", filename=f"{export_id}.zip")

    @app.get("/api/jobs/{job_id}/export")
    def job_export(job_id: str):
        rows = store.rows("SELECT export_id FROM exports WHERE scope='job' AND scope_id=?", (job_id,))
        if not rows:
            raise HTTPException(409, "Package is not ready")
        return download(rows[0]["export_id"])

    def decision_index(job_id: str):
        from monopoly_telemetry.run_files import build_run_files
        from .decision_index import DecisionIndex
        job = store.job(job_id)
        commits = store.rows("SELECT offsets_json FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job_id,))
        name = f"runs/{job['run_id']}/decisions.jsonl"
        end = json.loads(commits[0]["offsets_json"]).get(name, {}).get("bytes", 0) if commits else 0
        rows = []
        if end:
            with (store.root / name).open("rb") as handle:
                rows = [json.loads(line) for line in handle.read(end).splitlines()]
        files = build_run_files(store.root / "runs", job["run_id"])
        prompts = [files.run_dir / entry["path"] for entry in artifacts(job_id) if entry["path"].startswith("prompts/")]
        return DecisionIndex(files, entries=rows, prompt_paths=prompts)

    @app.get("/api/jobs/{job_id}/decisions")
    def decisions(job_id: str, cursor: int = 0):
        rows = decision_index(job_id).ordered()
        return rows[max(0, cursor):max(0, cursor)+50]

    @app.get("/api/jobs/{job_id}/decisions/{decision_id}")
    def decision_bundle(job_id: str, decision_id: str):
        bundle = decision_index(job_id).get_bundle(decision_id)
        if bundle is None:
            raise KeyError(decision_id)
        return bundle

    @app.get("/api/jobs/{job_id}/snapshots")
    def snapshots(job_id: str, cursor: int = 0):
        store.job(job_id)
        return store.rows("SELECT commit_seq,snapshot_path,snapshot_sha256,last_event_seq FROM commits WHERE job_id=? AND snapshot_path IS NOT NULL ORDER BY commit_seq LIMIT 50 OFFSET ?", (job_id, max(0, cursor)))

    @app.get("/api/jobs/{job_id}/artifacts")
    def artifacts(job_id: str, path: str | None = None):
        job = store.job(job_id)
        directory = store.root / "runs" / job["run_id"]
        job_directory = store.root / "jobs" / job_id
        frozen_inventory = job_directory / "artifact_inventory.json"
        names: set[str] = set()
        if frozen_inventory.exists():
            names = {entry["path"] for entry in json.loads(frozen_inventory.read_text())["files"]}
        elif (job_directory / "journal.jsonl").exists():
            commits = store.rows("SELECT commit_seq FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job_id,))
            committed = commits[0]["commit_seq"] if commits else 0
            data = (job_directory / "journal.jsonl").read_bytes()
            prefix = f"runs/{job['run_id']}/"
            for line in data[:data.rfind(b"\n")+1].splitlines():
                record = json.loads(line)
                if record["journal_seq"] <= committed:
                    names.update(target["path"][len(prefix):] for target in record["targets"] if target["path"].startswith(prefix))
        entries = {name: directory / name for name in names if name != ".writer.lock"}
        commits = store.rows("SELECT offsets_json FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job_id,))
        offsets = json.loads(commits[0]["offsets_json"]) if commits else {}
        if path is None:
            return [{"path": name, "bytes": offsets.get(f"runs/{job['run_id']}/{name}", {}).get("bytes", p.stat().st_size)} for name, p in entries.items()]
        safe_path(path)
        if path not in entries or not entries[path].resolve().is_relative_to(directory.resolve()):
            raise KeyError(path)
        committed = offsets.get(f"runs/{job['run_id']}/{path}")
        if committed:
            with entries[path].open("rb") as handle:
                return Response(handle.read(committed["bytes"]), media_type="application/x-ndjson")
        return FileResponse(entries[path])

    @app.websocket("/api/jobs/{job_id}/ws")
    async def websocket(websocket: WebSocket, job_id: str):
        await live(websocket, job_id, store, auth, hub)

    dist = resolve_repo_root() / "frontend" / "dist"
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}")
    def frontend(path: str):
        if path.startswith("api/") or not (dist / "index.html").exists():
            raise HTTPException(404)
        return FileResponse(dist / "index.html")

    return app
