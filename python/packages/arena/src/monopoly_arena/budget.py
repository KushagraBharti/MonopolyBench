"""Optional recorded-spend thresholds, independent of prompts and game state."""
from __future__ import annotations

import json
import math
from typing import Any, Literal, TypedDict

from monopoly_telemetry.execution_cost import execution_cost

from .execution_policy import OperationalPause
from .job_store import JobStore


class BudgetScope(TypedDict):
    scope: Literal["job", "campaign"]
    limit: float
    known_total: float
    unaccounted_calls: int
    in_flight_calls: int


class BudgetStatus(TypedDict):
    blocked: bool
    reason: Literal["budget", "budget_unknown"] | None
    detail: str
    scopes: list[BudgetScope]


def _limit(config_json: str) -> float | None:
    value = json.loads(config_json).get("cost_budget")
    if value is None:
        return None
    try:
        valid = type(value) in {int, float} and math.isfinite(value) and value > 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError("cost_budget must be a positive finite USD amount")
    return float(value)


def _scope(scope: Literal["job", "campaign"], limit: float,
           calls: list[dict[str, Any]]) -> BudgetScope:
    settled = [call for call in calls if call["state"] != "intent"]
    # Malformed ledger amounts are unaccounted, never usable reported charges.
    accounted = [call for call in settled if type(call["total_cost"]) in {int, float}
                 and math.isfinite(call["total_cost"]) and call["total_cost"] >= 0]
    return {"scope": scope, "limit": limit,
            "known_total": execution_cost(accounted)["known_total"],
            "unaccounted_calls": len(settled) - sum(call["cost_status"] == "known" for call in accounted),
            "in_flight_calls": len(calls) - len(settled)}


_JOB_CALLS = "SELECT * FROM calls WHERE job_id=? ORDER BY rowid"
_CAMPAIGN_CALLS = ("SELECT calls.* FROM calls JOIN jobs ON jobs.job_id=calls.job_id "
                   "WHERE jobs.campaign_id=? ORDER BY calls.rowid")


def _decide(scopes: list[BudgetScope]) -> BudgetStatus:
    for scope in scopes:
        if scope["known_total"] >= scope["limit"]:
            return {"blocked": True, "reason": "budget", "scopes": scopes,
                    "detail": f"{scope['scope'].capitalize()} recorded spend ${scope['known_total']:.6g} reached the ${scope['limit']:.6g} budget."}
    for scope in scopes:
        if scope["unaccounted_calls"]:
            return {"blocked": True, "reason": "budget_unknown", "scopes": scopes,
                    "detail": f"{scope['scope'].capitalize()} budget cannot be checked: {scope['unaccounted_calls']} settled call(s) have missing or unknown cost."}
    return {"blocked": False, "reason": None, "detail": "", "scopes": scopes}


def budget_status(store: JobStore, job_id: str) -> BudgetStatus:
    """Return a read-only budget decision from one ledger snapshot.

    Optional top-level cost_budget values are positive finite USD numbers. Null
    or absent values disable that scope. Invalid limits raise ValueError; an
    unknown job raises KeyError. Scopes are ordered job then campaign. Campaign
    accounting includes every attached job and rerun, regardless of job status.

    A reached limit takes precedence over unaccounted settled calls in either
    scope. Otherwise any missing/unknown settled cost blocks capped execution.
    Intent calls are disclosed as in flight and excluded from accounting. This
    is a recorded-spend threshold, not a reservation or guaranteed hard cap;
    concurrent/in-flight requests can overshoot. No ledger or job state changes.
    """
    scopes: list[BudgetScope] = []
    with store.connect() as db:
        db.execute("BEGIN")
        job = db.execute("SELECT config_json,campaign_id FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if job is None:
            raise KeyError(job_id)
        limit = _limit(job["config_json"])
        if limit is not None:
            calls = [dict(row) for row in db.execute(_JOB_CALLS, (job_id,))]
            scopes.append(_scope("job", limit, calls))
        if job["campaign_id"] is not None:
            campaign = db.execute("SELECT config_json FROM campaigns WHERE campaign_id=?", (job["campaign_id"],)).fetchone()
            limit = _limit(campaign["config_json"]) if campaign else None
            if limit is not None:
                calls = [dict(row) for row in db.execute(_CAMPAIGN_CALLS, (job["campaign_id"],))]
                scopes.append(_scope("campaign", limit, calls))
    return _decide(scopes)


def campaign_budget_statuses(store: JobStore, campaign_id: str) -> dict[str, BudgetStatus]:
    """Return budget_status for every job attached to a campaign from one snapshot.

    Each value equals budget_status(store, job_id) taken at the same instant,
    but the campaign-wide ledger is read once instead of once per job. Keys
    follow job insertion order. A job whose own cost_budget is invalid is
    omitted so callers fall back to budget_status and surface its ValueError;
    an invalid campaign limit raises ValueError as budget_status would. This is
    a request-local read for responses only, never cached: workers and
    admission keep calling budget_status/check_budget for a fresh decision.
    """
    with store.connect() as db:
        db.execute("BEGIN")
        jobs = db.execute("SELECT job_id,config_json FROM jobs WHERE campaign_id=? ORDER BY rowid", (campaign_id,)).fetchall()
        if not jobs:
            return {}
        campaign = db.execute("SELECT config_json FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
        campaign_limit = _limit(campaign["config_json"]) if campaign else None
        job_limits: dict[str, float | None] = {}
        for job in jobs:
            try:
                job_limits[job["job_id"]] = _limit(job["config_json"])
            except ValueError:
                pass
        calls: list[dict[str, Any]] = []
        if campaign_limit is not None or any(limit is not None for limit in job_limits.values()):
            calls = [dict(row) for row in db.execute(_CAMPAIGN_CALLS, (campaign_id,))]
    by_job: dict[str, list[dict[str, Any]]] = {job_id: [] for job_id in job_limits}
    for call in calls:
        by_job.setdefault(call["job_id"], []).append(call)
    shared = _scope("campaign", campaign_limit, calls) if campaign_limit is not None else None
    statuses: dict[str, BudgetStatus] = {}
    for job_id, limit in job_limits.items():
        scopes: list[BudgetScope] = []
        if limit is not None:
            scopes.append(_scope("job", limit, by_job[job_id]))
        if shared is not None:
            scopes.append(shared.copy())
        statuses[job_id] = _decide(scopes)
    return statuses


def check_budget(store: JobStore, job_id: str) -> None:
    """Raise OperationalPause with budget_status reason/detail when blocked."""
    status = budget_status(store, job_id)
    if status["reason"] is not None:
        raise OperationalPause(status["reason"], status["detail"])


# Both names expose the same read-only guard for API admission and client use.
budget_guard = check_budget
