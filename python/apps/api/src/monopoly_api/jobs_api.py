from __future__ import annotations

import json
import os
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
from monopoly_arena.campaign_setup import prepare as prepare_campaign, create as create_campaign, readiness
from monopoly_arena.campaign_controls import pause_campaign, run_campaign, cancel_campaign, start_cell
from monopoly_arena.budget import BudgetStatus, budget_status, campaign_budget_statuses
from monopoly_arena.cloud_preflight import preflight
from monopoly_arena.execution_policy import MODELS, data_root
from monopoly_arena.job_store import JobStore
from monopoly_telemetry.execution_cost import execution_cost
from monopoly_telemetry.inventory import safe_path
from .auth import Auth, COOKIE, SESSION_SECONDS
from .live import live, LiveHub
from .cloud_readers import CloudReaders
from .paths import resolve_repo_root


class Login(BaseModel):
    password: str


class Smoke(BaseModel):
    model_config = ConfigDict(extra="forbid")
    models: list[str] = Field(default_factory=lambda: list(MODELS))
    effort: str = "medium"
    max_turns: int = Field(default=5, ge=5, le=10)
    count: int = Field(default=1, ge=1, le=20)
    cost_budget: float | None = Field(default=None, gt=0, allow_inf_nan=False, strict=True)


class SingleGame(BaseModel):
    model_config = ConfigDict(extra="forbid")
    models: list[str] = Field(default_factory=lambda: list(MODELS))
    effort: str = "medium"
    max_turns: int | None = Field(default=None, ge=1, le=10000, strict=True)
    cost_budget: float | None = Field(default=None, gt=0, allow_inf_nan=False, strict=True)


class Launch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preparation_id: str
    idempotency_key: str = Field(min_length=8, max_length=128)


class Amendment(BaseModel):
    seeds: list[int]
    reason: str


class CampaignSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=80)
    seed_blocks: int = Field(default=1, ge=1, le=20, strict=True)
    concurrency: int = Field(default=4, ge=1, le=5, strict=True)
    cost_budget: float | None = Field(default=None, gt=0, allow_inf_nan=False, strict=True)


def create_cloud_app(root: Path | None = None) -> FastAPI:
    store = JobStore(root or data_root())
    auth = Auth()
    app = FastAPI(title="MonopolyBench cloud", docs_url=None, redoc_url=None, openapi_url=None)
    app.middleware("http")(auth.middleware)
    app.state.store = store
    hub = LiveHub(store)
    readers = CloudReaders(store)

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
    def login(body: Login, request: Request):
        response = JSONResponse({"ok": True})
        response.set_cookie(COOKIE, auth.login(body.password), httponly=True, secure=auth.cookie_secure(request), samesite="lax", max_age=SESSION_SECONDS)
        return response

    @app.post("/api/auth/logout")
    def logout(request: Request):
        response = JSONResponse({"ok": True})
        response.delete_cookie(COOKIE, secure=auth.cookie_secure(request), httponly=True, samesite="lax")
        return response

    @app.get("/api/status")
    def status():
        return {"demo": os.getenv("MB_DEMO") == "1", "account_stop": store.state("account_stop"), "drain": store.state("drain", False), "free_disk": shutil.disk_usage(store.root).free, "active_workers": len(store.rows("SELECT job_id FROM jobs WHERE status='running'")), "cost": execution_cost(store.rows("SELECT * FROM calls")), "preflight": store.state("preflight"), "models": MODELS}

    @app.get("/api/jobs")
    def jobs(status: str | None = None, kind: str | None = None, campaign: str | None = None, search: str = "", cursor: int = 0, archived: bool = False):
        rows = store.rows("""SELECT * FROM jobs WHERE (? IS NULL OR status=?) AND (? IS NULL OR kind=?)
            AND (? IS NULL OR campaign_id=?) AND archived=? AND (run_id LIKE ? OR config_json LIKE ? OR campaign_id LIKE ?)
            ORDER BY created_at DESC,job_id LIMIT 50 OFFSET ?""", (status, status, kind, kind, campaign, campaign, int(archived), "%"+search+"%", "%"+search+"%", "%"+search+"%", max(0, cursor)))
        budgets = campaign_budget_statuses(store, campaign) if campaign is not None else None
        return {"jobs": [job_detail(row["job_id"], budgets) for row in rows], "next_cursor": cursor+50 if len(rows) == 50 else None}

    @app.get("/api/jobs/{job_id}")
    def detail(job_id: str):
        return job_detail(job_id)

    def job_detail(job_id: str, budgets: dict[str, BudgetStatus] | None = None):
        # budgets is a request-local campaign snapshot; never reuse it across requests.
        job = store.job(job_id)
        job["config"] = json.loads(job.pop("config_json"))
        job["outcome"] = json.loads(job.pop("outcome_json") or "null")
        job["cost"] = execution_cost(store.rows("SELECT * FROM calls WHERE job_id=?", (job_id,)))
        job["pauses"] = store.rows("SELECT * FROM pauses WHERE job_id=?", (job_id,))
        job["allowed_actions"] = ({"queued": ["pause", "cancel"], "running": ["pause", "cancel"], "recovering": ["pause", "cancel"], "paused": ["resume", "cancel"], "completed": ["archive"], "failed": ["archive"], "cancelled": ["archive"]}).get(job["status"], [])
        commits = store.rows("SELECT * FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job_id,))
        job["snapshot"] = json.loads((store.root / commits[0]["snapshot_path"]).read_text()) if commits and commits[0]["snapshot_path"] else None
        job["snapshot_kind"] = "committed" if job["snapshot"] else "initial_preview"
        if job["snapshot"] is None:
            # An engine-produced initial board is a display preview, never a canonical checkpoint.
            from monopoly_engine import Engine
            config = job["config"]
            job["snapshot"] = Engine(seed=config["seed"], run_id=config["run_id"],
                                     players=[{"player_id": p["player_id"], "name": p["name"]} for p in config["players"]],
                                     max_turns=config["max_turns"], max_trade_exchanges=config.get("max_trade_exchanges", 20),
                                     max_auction_actions=config.get("max_auction_actions", 200)).get_snapshot()
        job["budget"] = budgets[job_id] if budgets is not None and job_id in budgets else budget_status(store, job_id)
        job["commit_seq"] = commits[0]["commit_seq"] if commits else 0
        now = time.time()
        job["elapsed_seconds"] = max(0, (job["ended_at"] or now) - job["started_at"]) if job["started_at"] else None
        job["progress_age_seconds"] = max(0, now - job["last_progress_at"]) if job["last_progress_at"] else None
        job["slow"] = job["status"] == "running" and time.time() - (job["last_progress_at"] or job["started_at"] or job["created_at"]) > 300
        return job

    @app.post("/api/jobs/{job_id}/{action}")
    def control(job_id: str, action: str):
        job = detail(job_id)
        if action not in job["allowed_actions"]:
            raise HTTPException(409, "Action is not allowed in this state")
        if action == "pause":
            store.pause(job_id, "operator", expected_status=job["status"])
            store.set_state("individual_start:" + job_id, False)
        elif action == "resume":
            check = readiness(store, {"status": "paused", "config": {"seeds": [job["seed"]]}, "git_sha": job["git_sha"], "image_digest": job["image_digest"]}, require_study=job["campaign_id"] is not None)
            if not check["can_start"] or job["budget"]["blocked"]:
                raise HTTPException(409, " ".join(check["reasons"]) or job["budget"]["detail"])
            store.resume(job_id)
            if job["campaign_id"]:
                store.set_state("individual_start:" + job_id, True)
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
        # Clearing the account stop is the owner's intent. Only account/provider pauses
        # resume here; operator and campaign holds keep their own Resume/Run controls.
        store.set_state("account_stop", None)
        campaigns = {row["campaign_id"]: row["status"] for row in store.rows("SELECT campaign_id,status FROM campaigns")}
        budgets: dict[str, dict[str, BudgetStatus]] = {}
        waiting, skipped = [], []
        for job in store.rows("SELECT * FROM jobs WHERE status='paused' ORDER BY created_at,job_id"):
            job_id, campaign_id = job["job_id"], job["campaign_id"]
            if job["pause_reason"] == "operator":
                reasons = ["Paused by the operator. Resume this game individually."]
            elif campaign_id and (job["pause_reason"] == "campaign_operator" or campaigns.get(campaign_id) != "running" and not store.state("individual_start:" + job_id)):
                reasons = ["Held by its campaign. Run the campaign or start this game from the campaign page."]
            else:
                if campaign_id and campaign_id not in budgets:
                    budgets[campaign_id] = campaign_budget_statuses(store, campaign_id)
                scoped = budgets.get(campaign_id, {})
                reasons = readiness(store, {"status": "paused", "config": {"seeds": [job["seed"]]}, "git_sha": job["git_sha"], "image_digest": job["image_digest"]},
                                    require_study=campaign_id is not None, budgets=scoped)["reasons"]
                budget = scoped.get(job_id) or budget_status(store, job_id)
                if budget["blocked"] and budget["detail"] not in reasons:
                    reasons.append(budget["detail"])
            if reasons:
                skipped.append({"job_id": job_id, "reasons": reasons})
                continue
            try:
                store.resume(job_id)
            except ValueError:
                waiting.append(job_id)
        store.audit("resume_all", {"waiting_for_worker": waiting, "skipped": [entry["job_id"] for entry in skipped]}, "dashboard")
        return {"ok": True, "waiting_for_worker": waiting, "skipped": skipped}

    def prepare_games(models: list[str], effort: str, max_turns: int | None, count: int, cost_budget: float | None, kind: str):
        preparation = secrets.token_hex(16)
        configs = [run_config(secrets.randbits(32), f"{kind}-{preparation}-{i}", models, effort, max_turns) for i in range(count)]
        if cost_budget is not None:
            for config in configs:
                config["cost_budget"] = cost_budget
        result = {"preparation_id": preparation, "kind": kind, "configs": configs, "created_at": time.time(), "cost_estimate": None, "preflight": store.state("preflight")}
        store.set_state("prepare:"+preparation, result)
        return result

    @app.post("/api/smoke/prepare")
    def prepare(body: Smoke):
        return prepare_games(body.models, body.effort, body.max_turns, body.count, body.cost_budget, "smoke")

    @app.post("/api/games/prepare")
    def prepare_single(body: SingleGame):
        return prepare_games(body.models, body.effort, body.max_turns, 1, body.cost_budget, "single")

    def launch_games(body: Launch, kind: str):
        prepared = store.state("prepare:"+body.preparation_id)
        if not prepared:
            raise HTTPException(404, "Preparation not found")
        if prepared.get("kind", "smoke") != kind:
            raise HTTPException(409, "This preparation belongs to a different run type.")
        from monopoly_arena.worker import build_identity
        identity = build_identity()
        if any(config.get(key) != identity[key] for config in prepared["configs"] for key in ("git_sha", "image_digest")):
            raise HTTPException(409, "The app was updated after review. Prepare the game again.")
        with store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            key = "launch:" + body.idempotency_key
            previous = db.execute("SELECT value_json FROM account_state WHERE key=?", (key,)).fetchone()
            if previous and json.loads(previous[0]) != body.preparation_id:
                raise ValueError("Idempotency key already belongs to another preparation")
            db.execute("INSERT OR IGNORE INTO account_state VALUES(?,?,?)", (key, json.dumps(body.preparation_id), time.time()))
        jobs = [store.create_job(config, kind=kind, key=f"{kind}:{body.preparation_id}:{i}") for i, config in enumerate(prepared["configs"])]
        store.audit(kind + "_launch", {"jobs": [j["job_id"] for j in jobs]}, "dashboard")
        return [detail(job["job_id"]) for job in jobs]

    @app.post("/api/smoke")
    def smoke(body: Launch):
        return launch_games(body, "smoke")

    @app.post("/api/games")
    def single(body: Launch):
        return launch_games(body, "single")

    def campaign_file(campaign_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", campaign_id):
            raise HTTPException(400, "Invalid campaign id")
        return resolve_repo_root() / "campaigns" / f"{campaign_id}.json"

    @app.get("/api/campaigns")
    def campaigns(summary: bool = False):
        frozen = {row["campaign_id"]: row for row in store.rows("SELECT * FROM campaigns")}
        for path in (resolve_repo_root() / "campaigns").glob("*.json"):
            config = json.loads(path.read_text())
            if config.get("campaign_config_version") == "long_horizon_campaign_config_v2":
                frozen.setdefault(config["campaign_id"], {"campaign_id": config["campaign_id"], "status": "draft", "config_json": json.dumps(config)})
        if summary:
            return [{"campaign_id": key, "status": row["status"],
                     "display_name": json.loads(row["config_json"]).get("study_label") or key}
                    for key, row in frozen.items()]
        return [campaign(campaign_id) for campaign_id in frozen]

    @app.post("/api/campaigns/prepare")
    def campaign_prepare(body: CampaignSettings):
        return prepare_campaign(store, **body.model_dump())

    @app.post("/api/campaigns/create")
    def campaign_create(body: Launch):
        return campaign(create_campaign(store, body.preparation_id, body.idempotency_key))

    @app.get("/api/campaigns/{campaign_id}")
    def campaign(campaign_id: str):
        rows = store.rows("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,))
        if not rows:
            path = campaign_file(campaign_id)
            if not path.exists():
                raise KeyError(campaign_id)
            result = {"campaign_id": campaign_id, "status": "draft", "config": json.loads(path.read_text()), "cells": []}
        else:
            result = {**rows[0], "config": json.loads(rows[0]["config_json"]), "cells": store.rows("SELECT cells.*,jobs.status AS job_status FROM cells LEFT JOIN jobs ON cells.job_id=jobs.job_id WHERE cells.campaign_id=? ORDER BY cells.execution_rank", (campaign_id,)), "amendments": store.rows("SELECT * FROM campaign_amendments WHERE campaign_id=?", (campaign_id,))}
        result["display_name"] = result["config"].get("study_label") or campaign_id
        # One consistent campaign ledger read serves every cell and readiness in this response.
        budgets = campaign_budget_statuses(store, campaign_id) if rows else {}
        for cell in result["cells"]:
            cell["models_by_seat"] = json.loads(cell["seat_order_json"])
            cell["game"] = job_detail(cell["job_id"], budgets) if cell["job_id"] else None
            cell["allowed_actions"] = cell["game"]["allowed_actions"] if cell["game"] else (["start"] if cell["status"] != "cancelled" and result["status"] not in {"done", "cancelled"} else [])
        result["readiness"] = readiness(store, result, budgets=budgets)
        result["allowed_actions"] = [] if result["status"] in {"draft", "done", "cancelled"} else ["run", "pause", "cancel"]
        result["exports"] = export_entries(campaign_id)
        return result

    @app.post("/api/campaigns/{campaign_id}/cells/{cell_index}/start")
    def campaign_cell_start(campaign_id: str, cell_index: int):
        current = campaign(campaign_id)
        if current["status"] in {"draft", "done", "cancelled"}:
            raise HTTPException(409, "This campaign cannot start games.")
        check = readiness(store, {**current, "status": "frozen"})
        if not check["can_start"]:
            raise HTTPException(409, " ".join(check["reasons"]))
        start_cell(store, campaign_id, cell_index)
        return campaign(campaign_id)

    @app.post("/api/campaigns/{campaign_id}/freeze")
    def freeze_campaign(campaign_id: str):
        if os.getenv("MB_DEMO") == "1":
            raise HTTPException(409, "Demo mode supports smoke games only; use a separate volume for research campaigns")
        return freeze(store, json.loads(campaign_file(campaign_id).read_text()))

    @app.post("/api/campaigns/{campaign_id}/amend")
    def amend_campaign(campaign_id: str, body: Amendment):
        amend(store, campaign_id, body.seeds, body.reason)
        return campaign(campaign_id)

    @app.post("/api/campaigns/{campaign_id}/{action}")
    def campaign_control(campaign_id: str, action: str):
        current = campaign(campaign_id)
        if action not in {"run", "pause", "cancel"} or current["status"] == "draft":
            if action == "export" and current["status"] != "draft":
                from monopoly_arena.campaign_export import export_campaign
                return {"export_id": export_campaign(store, campaign_id)}
            raise HTTPException(409, "Freeze the campaign before running it")
        if action == "run":
            check = readiness(store, {**current, "status": "frozen"})
            if not check["can_start"]:
                raise HTTPException(409, " ".join(check["reasons"]))
        if current["status"] in {"done", "cancelled"}:
            raise HTTPException(409, "This campaign has finished or was cancelled.")
        if action == "run":
            run_campaign(store, campaign_id)
        elif action == "pause":
            pause_campaign(store, campaign_id)
        else:
            cancel_campaign(store, campaign_id)
        return campaign(campaign_id)

    @app.post("/api/preflight/run")
    async def run_preflight():
        return await preflight(store)

    @app.get("/api/preflight/latest")
    def latest_preflight():
        return store.state("preflight")

    @app.get("/api/exports")
    def exports():
        return export_entries()

    def export_entries(campaign_id: str | None = None):
        rows = store.rows("""SELECT exports.*,jobs.kind AS job_kind,jobs.run_id,jobs.cell_index,
            COALESCE(jobs.campaign_id,CASE WHEN exports.scope='campaign' THEN exports.scope_id END) AS campaign_id,
            campaigns.config_json AS campaign_config_json
            FROM exports LEFT JOIN jobs ON exports.scope='job' AND exports.scope_id=jobs.job_id
            LEFT JOIN campaigns ON campaigns.campaign_id=COALESCE(jobs.campaign_id,CASE WHEN exports.scope='campaign' THEN exports.scope_id END)
            WHERE (? IS NULL OR (exports.scope='campaign' AND exports.scope_id=?))
            ORDER BY exports.created_at DESC,exports.export_id DESC""", (campaign_id, campaign_id))
        for row in rows:
            config_json = row.pop("campaign_config_json")
            campaign_name = json.loads(config_json).get("study_label") if config_json else None
            if row["scope"] == "campaign":
                row["display_name"] = campaign_name or row["scope_id"]
                row["run_kind"] = "campaign"
                row["source_url"] = "/campaigns/" + row["scope_id"]
            else:
                row["run_kind"] = row["job_kind"]
                if row["job_kind"] == "campaign":
                    number = row["cell_index"] + 1 if row["cell_index"] is not None else ""
                    row["display_name"] = f"Game {number}" + (f" · {campaign_name}" if campaign_name else "")
                else:
                    row["display_name"] = "Model test" if row["job_kind"] == "smoke" else "Single game"
                row["source_url"] = "/games/" + row["scope_id"]
            row["download_url"] = "/api/exports/" + row["export_id"] + "/download"
        return rows

    @app.get("/api/dashboard")
    def dashboard():
        groups = store.rows("SELECT kind,status,COUNT(*) AS count FROM jobs WHERE archived=0 GROUP BY kind,status")
        totals = {"games": sum(g["count"] for g in groups if g["kind"] == "single"),
                  "tests": sum(g["count"] for g in groups if g["kind"] == "smoke"),
                  "campaigns": store.rows("SELECT COUNT(*) AS count FROM campaigns")[0]["count"],
                  "exports": store.rows("SELECT COUNT(*) AS count FROM exports")[0]["count"]}
        activity = {name: sum(g["count"] for g in groups if g["status"] == name)
                    for name in ("running", "queued", "paused", "finalizing", "recovering")}
        recent_jobs = store.rows("SELECT job_id FROM jobs WHERE archived=0 ORDER BY created_at DESC,job_id DESC LIMIT 6")
        recent_campaigns = store.rows("SELECT campaign_id FROM campaigns ORDER BY frozen_at DESC,campaign_id DESC LIMIT 4")
        preflight_report = store.state("preflight")
        connection = {key: preflight_report[key] for key in ("passed", "created_at") if key in preflight_report} if preflight_report else None
        return {"totals": totals, "activity": activity,
                "recent_jobs": [detail(row["job_id"]) for row in recent_jobs],
                "recent_campaigns": [campaign(row["campaign_id"]) for row in recent_campaigns],
                "recent_exports": export_entries()[:6],
                "status": {"active_workers": activity["running"], "account_stop": store.state("account_stop"),
                           "drain": store.state("drain", False), "free_disk": shutil.disk_usage(store.root).free,
                           "preflight": connection}}

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

    @app.get("/api/jobs/{job_id}/decisions")
    def decisions(job_id: str, cursor: int = 0):
        return readers.decisions(store.job(job_id), max(0, cursor))

    @app.get("/api/jobs/{job_id}/decisions/{decision_id}")
    def decision_bundle(job_id: str, decision_id: str):
        bundle = readers.bundle(store.job(job_id), decision_id)
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
        published = readers.artifacts(job)
        entries = {entry["path"]: directory / entry["path"] for entry in published}
        commits = store.rows("SELECT offsets_json FROM commits WHERE job_id=? ORDER BY commit_seq DESC LIMIT 1", (job_id,))
        offsets = json.loads(commits[0]["offsets_json"]) if commits else {}
        if path is None:
            return published
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
        if Path(path).suffix in {".png", ".svg", ".ico", ".webmanifest"}:
            asset = dist / path
            if not asset.resolve().is_relative_to(dist.resolve()) or not asset.is_file():
                raise HTTPException(404)
            return FileResponse(asset)
        return FileResponse(dist / "index.html")

    return app
