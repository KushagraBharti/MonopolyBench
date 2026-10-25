from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.parse import urlparse

import anyio
from fastapi import WebSocket, WebSocketDisconnect

from monopoly_arena.job_store import JobStore
from .auth import Auth, COOKIE


def committed_batches(store: JobStore, job: dict[str, Any], cursor: int, through: int | None = None) -> list[dict[str, Any]]:
    rows = store.rows("SELECT * FROM commits WHERE job_id=? AND commit_seq>? AND (? IS NULL OR commit_seq<=?) ORDER BY commit_seq LIMIT 50", (job["job_id"], cursor, through, through))
    if not rows:
        return []
    name = f"runs/{job['run_id']}/events.jsonl"
    prior = store.rows("SELECT offsets_json FROM commits WHERE job_id=? AND commit_seq=?", (job["job_id"], rows[0]["commit_seq"]-1))
    start = json.loads(prior[0]["offsets_json"]).get(name, {}).get("bytes", 0) if prior else 0
    batches = []
    for commit in rows:
        end = json.loads(commit["offsets_json"]).get(name, {}).get("bytes", 0)
        events = []
        if end > start:
            with (store.root / name).open("rb") as handle:
                handle.seek(start)
                events = [json.loads(line) for line in handle.read(end-start).splitlines()]
        snapshot = json.loads((store.root / commit["snapshot_path"]).read_text()) if commit["snapshot_path"] else None
        batches.append({"schema_version": "v2", "job_id": job["job_id"], "run_id": job["run_id"], "commit_seq": commit["commit_seq"], "recovery_generation": commit["recovery_generation"], "last_event_seq": commit["last_event_seq"], "snapshot": snapshot, "events": events})
        start = end
    return batches


class GameTailer:
    def __init__(self, store: JobStore, job: dict[str, Any]):
        self.store, self.job = store, job
        last = store.rows("SELECT MAX(commit_seq) AS seq FROM commits WHERE job_id=?", (job["job_id"],))
        self.cursor = last[0]["seq"] or 0
        self.viewers: set[asyncio.Queue] = set()
        self.task: asyncio.Task | None = None

    def publish(self, batch: dict[str, Any] | None) -> None:
        for queue in tuple(self.viewers):
            if queue.full():
                # Disconnect lagging viewers; each can backfill from its last
                # commit without holding up the tailer or game workers.
                while not queue.empty():
                    queue.get_nowait()
                queue.put_nowait(None)
                self.viewers.remove(queue)
            else:
                queue.put_nowait(batch)

    async def run(self) -> None:
        try:
            while self.viewers:
                batches = await asyncio.to_thread(committed_batches, self.store, self.job, self.cursor)
                for batch in batches:
                    self.cursor = batch["commit_seq"]
                    self.publish(batch)
                    await asyncio.sleep(0)
                await asyncio.sleep(0 if batches else 0.5)
        except Exception:
            self.publish(None)


class LiveHub:
    """One tailer per viewed game; bounded, independent viewer queues."""
    def __init__(self, store: JobStore):
        self.store = store
        self.tailers: dict[str, GameTailer] = {}

    def subscribe(self, job: dict[str, Any]) -> tuple[GameTailer, asyncio.Queue, int]:
        tailer = self.tailers.get(job["job_id"])
        if tailer is None or tailer.task is None or tailer.task.done():
            tailer = GameTailer(self.store, job)
            self.tailers[job["job_id"]] = tailer
        queue: asyncio.Queue = asyncio.Queue(maxsize=32)
        tailer.viewers.add(queue)
        if tailer.task is None:
            tailer.task = asyncio.create_task(tailer.run())
        return tailer, queue, tailer.cursor

    async def unsubscribe(self, tailer: GameTailer, queue: asyncio.Queue) -> None:
        tailer.viewers.discard(queue)
        if not tailer.viewers:
            if self.tailers.get(tailer.job["job_id"]) is tailer:
                del self.tailers[tailer.job["job_id"]]
            if tailer.task:
                tailer.task.cancel()
                await asyncio.gather(tailer.task, return_exceptions=True)


async def live(websocket: WebSocket, job_id: str, store: JobStore, auth: Auth, hub: LiveHub) -> None:
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
    tailer, queue, cutoff = hub.subscribe(job)
    if cursor > cutoff:
        cursor, generation = 0, -1

    async def send(batch: dict[str, Any]) -> None:
        nonlocal cursor, generation
        reset = generation != batch["recovery_generation"]
        await asyncio.wait_for(websocket.send_json({**batch, "type": "SNAPSHOT" if reset else "EVENT", "reset": reset}), 5)
        cursor, generation = batch["commit_seq"], batch["recovery_generation"]

    async def stream() -> None:
        await asyncio.wait_for(websocket.send_json({"type": "HELLO", "schema_version": "v2", "job_id": job_id, "run_id": job["run_id"]}), 5)
        # Subscribe before backfilling a fixed boundary so concurrent commits
        # cannot fall between historical reads and live delivery.
        while cursor < cutoff:
            batches = await asyncio.to_thread(committed_batches, store, job, cursor, cutoff)
            if not batches:
                raise RuntimeError("Committed backfill has a gap")
            for batch in batches:
                await send(batch)
        while True:
            batch = await queue.get()
            if batch is None:
                await websocket.close(code=1013)
                return
            if batch["commit_seq"] > cursor:
                await send(batch)

    async def disconnected() -> None:
        while True:
            await websocket.receive_text()

    tasks = [asyncio.create_task(stream()), asyncio.create_task(disconnected())]
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    except (WebSocketDisconnect, asyncio.TimeoutError, RuntimeError, OSError, ValueError):
        pass
    finally:
        # ASGI cancellation can arrive while a disconnect is already cleaning
        # up. Finish releasing the shared tailer even under a cancelled scope.
        with anyio.CancelScope(shield=True):
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            await hub.unsubscribe(tailer, queue)
            try:
                await websocket.close()
            except (RuntimeError, WebSocketDisconnect):
                pass
