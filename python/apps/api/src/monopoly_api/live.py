from __future__ import annotations

import asyncio
import json
from urllib.parse import urlparse

from fastapi import WebSocket, WebSocketDisconnect

from monopoly_arena.job_store import JobStore
from .auth import Auth, COOKIE


async def live(websocket: WebSocket, job_id: str, store: JobStore, auth: Auth) -> None:
    origin = websocket.headers.get("origin")
    if not auth.valid(websocket.cookies.get(COOKIE)) or origin and urlparse(origin).netloc != websocket.headers.get("host"):
        await websocket.close(code=4401)
        return
    try:
        job = store.job(job_id)
        cursor = max(0, int(websocket.query_params.get("after", "0")))
        generation = int(websocket.query_params.get("generation", "-1"))
    except (KeyError, ValueError):
        await websocket.close(code=4404)
        return
    await websocket.accept()
    try:
        await websocket.send_json({"type": "HELLO", "schema_version": "v2", "job_id": job_id, "run_id": job["run_id"]})
        while True:
            rows = store.rows("SELECT * FROM commits WHERE job_id=? AND commit_seq>? ORDER BY commit_seq LIMIT 50", (job_id, cursor))
            for commit in rows:
                offsets = json.loads(commit["offsets_json"])
                name = f"runs/{job['run_id']}/events.jsonl"
                end = offsets.get(name, {}).get("bytes", 0)
                prior = store.rows("SELECT offsets_json FROM commits WHERE job_id=? AND commit_seq=?", (job_id, commit["commit_seq"]-1))
                start = json.loads(prior[0]["offsets_json"]).get(name, {}).get("bytes", 0) if prior else 0
                reset = generation != commit["recovery_generation"]
                events = []
                if end > start:
                    with (store.root / name).open("rb") as handle:
                        handle.seek(start)
                        events = [json.loads(line) for line in handle.read(end-start).splitlines()]
                snapshot = json.loads((store.root / commit["snapshot_path"]).read_text()) if commit["snapshot_path"] else None
                await asyncio.wait_for(websocket.send_json({"type": "SNAPSHOT" if reset else "EVENT", "schema_version": "v2", "job_id": job_id, "run_id": job["run_id"], "commit_seq": commit["commit_seq"], "recovery_generation": commit["recovery_generation"], "last_event_seq": commit["last_event_seq"], "snapshot": snapshot, "events": events, "reset": reset}), 5)
                cursor, generation = commit["commit_seq"], commit["recovery_generation"]
            try:
                await asyncio.wait_for(websocket.receive_text(), 0.5)
            except asyncio.TimeoutError:
                pass
    except (WebSocketDisconnect, asyncio.TimeoutError, RuntimeError):
        return
