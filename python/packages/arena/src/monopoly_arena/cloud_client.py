"""Record each physical POST and reuse responses at the exact resolver stage."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, replace
import hashlib
import json
import os
import time
from typing import Any
import uuid

from monopoly_telemetry.execution_cost import call_cost
from monopoly_telemetry.writer_jsonl import atomic_write
from .execution_policy import OperationalPause, UNKNOWN_PER_DECISION, UNKNOWN_PER_GAME, error_pause
from .job_store import JobStore, encode
from .openrouter_client import OpenRouterClient, OpenRouterResult
from .route_validator import validate_route


class CloudClient(OpenRouterClient):
    # The resolver must not add a second call journal or deadline around this client.
    durable_call_records = True

    def __init__(self, store: JobStore, job_id: str):
        super().__init__(max_retries=0, base_url=os.getenv("MB_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
        self.store, self.job_id = store, job_id
        self.directory = store.root / "jobs" / job_id / "calls"
        self.decision_id = ""
        self.stage = 0
        self.observation_scope = "start"

    def begin_decision(self, decision_id: str) -> None:
        self.decision_id, self.stage = decision_id, 0

    def boundary(self) -> None:
        job = self.store.job(self.job_id)
        if self.store.state("account_stop"):
            raise OperationalPause("account_error")
        if self.store.state("drain"):
            raise OperationalPause("drain")
        if job["status"] in {"paused", "cancelled"}:
            raise OperationalPause(job["pause_reason"] or "operator")
        import shutil
        if shutil.disk_usage(self.store.root).free < float(os.getenv("MB_DISK_RESERVE_GB", "5"))*1e9:
            raise OperationalPause("storage")

    async def create_chat_completion(self, **kwargs: Any) -> OpenRouterResult:
        stage = self.stage
        self.stage += 1
        raw = json.dumps(kwargs, separators=(",", ":"), ensure_ascii=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        previous = self.store.rows("SELECT * FROM calls WHERE job_id=? AND decision_id=? AND resolver_stage=? ORDER BY created_at", (self.job_id, self.decision_id, stage))
        for call in previous:
            intent = json.loads((self.directory / f"{call['call_id']}.intent.json").read_text())
            if intent["payload_sha256"] != digest:
                raise ValueError("Resumed resolver request differs from saved payload")
            response_path = self.directory / f"{call['call_id']}.response.json"
            if response_path.exists():
                response_bytes = response_path.read_bytes()
                receipt = self.directory / f"{call['call_id']}.response.sha256"
                if not receipt.exists() or receipt.read_text() != hashlib.sha256(response_bytes).hexdigest():
                    raise ValueError("Saved response hash mismatch")
                result = OpenRouterResult(**json.loads(response_bytes))
                self._record_result(call["call_id"], result)
                call.update(state="responded" if result.ok else "failed", http_status=result.status_code, error_type=result.error_type)
                if result.ok or result.error_type == "invalid_json":
                    if result.ok:
                        validate_route(kwargs, result.response_json or {})
                    return replace(result, call_id=call["call_id"])
            elif call["state"] == "intent":
                self.store.execute("UPDATE calls SET state='unknown',cost_status='unknown' WHERE call_id=?", (call["call_id"],))
        unknown = self.store.rows("SELECT decision_id FROM calls WHERE job_id=? AND state='unknown'", (self.job_id,))
        if len(unknown) > UNKNOWN_PER_GAME or sum(c["decision_id"] == self.decision_id for c in unknown) > UNKNOWN_PER_DECISION:
            raise ValueError("Interrupted-request repeat limit exceeded")
        pauses = self.store.rows("SELECT * FROM pauses WHERE job_id=?", (self.job_id,))
        attempt_limit = 1 if pauses else 3
        outage_round = pauses[0]["retries_used"] + 1 if pauses else 0
        retry_epoch = self.store.state("resume_epoch:" + self.job_id, 0)
        start_attempt = 0
        for call in previous:
            intent = json.loads((self.directory / f"{call['call_id']}.intent.json").read_text())
            if intent.get("outage_round", 0) == outage_round and intent.get("retry_epoch", 0) == retry_epoch and call["state"] == "failed":
                start_attempt = max(start_attempt, call["transport_attempt"] + 1)
        if start_attempt >= attempt_limit:
            last = previous[-1]
            saved = json.loads((self.directory / f"{last['call_id']}.response.json").read_text())
            raise OperationalPause(error_pause(last["http_status"], last["error_type"], saved.get("response_text")), last["error_type"] or "request failed")
        for attempt in range(start_attempt, attempt_limit):
            self.boundary()
            if os.getenv("MB_TEST_MODE") == "1":
                self._extra_headers = {"X-MB-Mock-Decision": self.decision_id, "X-MB-Mock-Stage": str(stage), "X-MB-Mock-Attempt": str(attempt)}
            call_id = uuid.uuid4().hex
            atomic_write(self.directory / f"{call_id}.intent.json", encode({"call_id": call_id, "decision_id": self.decision_id, "resolver_stage": stage, "transport_attempt": attempt, "outage_round": outage_round, "retry_epoch": retry_epoch, "payload": kwargs, "payload_raw": raw, "payload_sha256": digest, "after_interruption": bool(unknown)}).encode())
            self.store.execute("INSERT INTO calls(call_id,job_id,decision_id,resolver_stage,transport_attempt,state,cost_status,created_at) VALUES(?,?,?,?,?,'intent','unknown',?)", (call_id, self.job_id, self.decision_id, stage, attempt, time.time()))
            try:
                result = await asyncio.wait_for(super().create_chat_completion(**kwargs), float(os.getenv("MB_REQUEST_DEADLINE_S", "1200")))
            except asyncio.TimeoutError:
                result = OpenRouterResult(False, None, None, "Total deadline exceeded", "total_timeout", None, raw)
            response_bytes = encode(asdict(result)).encode()
            atomic_write(self.directory / f"{call_id}.response.sha256", hashlib.sha256(response_bytes).hexdigest().encode())
            atomic_write(self.directory / f"{call_id}.response.json", response_bytes)
            self._record_result(call_id, result)
            if result.ok:
                validate_route(kwargs, result.response_json or {})
                return replace(result, call_id=call_id)
            if result.error_type == "invalid_json":
                return replace(result, call_id=call_id)
            reason = error_pause(result.status_code, result.error_type, result.response_text)
            if reason != "provider_unavailable" or attempt == attempt_limit - 1:
                raise OperationalPause(reason, result.error_type or "request failed")
            await asyncio.sleep(0.5 * 2**attempt)
        raise AssertionError("Unreachable")

    def _record_result(self, call_id: str, result: OpenRouterResult) -> None:
        body = result.response_json or {}
        cost = call_cost(body.get("usage"), unknown=result.error_type in {"network_error", "total_timeout"})
        self.store.execute("""UPDATE calls SET state=?,http_status=?,error_type=?,model_returned=?,provider_returned=?,generation_id=?,is_byok=?,usage_cost=?,upstream_cost=?,total_cost=?,cost_status=?,completed_at=COALESCE(completed_at,?) WHERE call_id=?""", ("responded" if result.ok else "failed", result.status_code, result.error_type, body.get("model"), body.get("provider"), body.get("id"), cost["is_byok"], cost["usage_cost"], cost["upstream_cost"], cost["total_cost"], cost["cost_status"], time.time(), call_id))

    async def get_generation(self, generation_id: str) -> OpenRouterResult:
        result = await super().get_generation(generation_id)
        payload = result.response_json if result.ok and isinstance(result.response_json, dict) else {}
        data = payload.get("data")
        if isinstance(data, dict):
            calls = self.store.rows("SELECT call_id,is_byok,usage_cost,upstream_cost,total_cost,cost_status FROM calls WHERE job_id=? AND generation_id=? AND cost_status!='unknown'", (self.job_id, generation_id))
            for call in calls:
                # Fill only what the completion omitted; never replace a reported value.
                current = (None if call["is_byok"] is None else bool(call["is_byok"]), call["usage_cost"], call["upstream_cost"])
                byok = current[0] if current[0] is not None else data.get("is_byok")
                charge = current[1] if current[1] is not None else data.get("total_cost")
                upstream = current[2] if current[2] is not None else data.get("upstream_inference_cost")
                cost = call_cost({"cost": charge, "is_byok": byok, "cost_details": {"upstream_inference_cost": upstream}})
                # Persist any change, including a known charge that BYOK evidence makes unknown.
                if (cost["is_byok"], cost["usage_cost"], cost["upstream_cost"], cost["total_cost"], cost["cost_status"]) != (*current, call["total_cost"], call["cost_status"]):
                    self.store.execute("UPDATE calls SET is_byok=?,usage_cost=?,upstream_cost=?,total_cost=?,cost_status=? WHERE call_id=?",
                                       (cost["is_byok"], cost["usage_cost"], cost["upstream_cost"], cost["total_cost"], cost["cost_status"], call["call_id"]))
        return result

    async def _get_json(self, **kwargs: Any) -> OpenRouterResult:
        # Cache metadata observations to make response reuse deterministic.
        name = hashlib.sha256(encode([self.observation_scope, kwargs]).encode()).hexdigest()
        path = self.directory.parent / "observations" / f"{name}.json"
        if path.exists():
            return OpenRouterResult(**json.loads(path.read_text()))
        try:
            result = await asyncio.wait_for(super()._get_json(**kwargs), 60)
        except asyncio.TimeoutError:
            result = OpenRouterResult(False, None, None, "Metadata deadline exceeded", "total_timeout", None)
        atomic_write(path, encode(asdict(result)).encode())
        return result
