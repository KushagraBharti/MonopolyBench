"""Prepare outcome-blind campaign records without launching games or calling models."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import random
import shutil
import time
import uuid
from typing import Any

from .cloud_campaign import freeze
from .execution_policy import MODELS
from .job_store import JobStore, encode
from .research_registry import load_seed_registry, research_dir, validate_campaign_config
from .worker import build_identity


def readiness(store: JobStore, campaign: dict[str, Any], *, require_study: bool = True) -> dict[str, Any]:
    identity = build_identity()
    config = campaign.get("config") or json.loads(campaign.get("config_json") or "{}")
    reasons = []
    if campaign.get("status") not in {"draft", "frozen", "paused", "running"}:
        reasons.append("This campaign has finished or was cancelled.")
    if not config.get("seeds"):
        reasons.append("This older draft has no games. Create a new campaign to choose its settings.")
    if any(campaign.get(key, identity[key]) != identity[key] for key in ("git_sha", "image_digest")):
        reasons.append("The app was updated after this campaign was saved. Create a new campaign on the current version; this campaign's records will be kept.")
    preflight = store.state("preflight", {})
    if require_study and (not preflight.get("passed") or time.time() - preflight.get("created_at", 0) > 21600
            or any(preflight.get(key) != identity[key] for key in ("git_sha", "image_digest"))):
        reasons.append("Check model connections before starting. A passing check on this app version is needed within six hours.")
    if store.state("account_stop"):
        reasons.append("Model requests are paused. Check your provider keys and available credits.")
    if store.state("drain"):
        reasons.append("The server is finishing existing work before maintenance. Try again when maintenance ends.")
    if shutil.disk_usage(store.root).free < float(os.getenv("MB_DISK_RESERVE_GB", "5")) * 1e9:
        reasons.append("Storage is below the reserved space. Free space or expand storage before starting.")
    if require_study and os.getenv("MB_DEMO") == "1":
        reasons.append("Demo mode supports test games only. Full campaigns need the research workspace.")
    if config.get("cost_budget") is not None and campaign.get("campaign_id"):
        jobs = store.rows("SELECT job_id FROM jobs WHERE campaign_id=? LIMIT 1", (campaign["campaign_id"],))
        if jobs:
            from .budget import budget_status
            budget = budget_status(store, jobs[0]["job_id"])
            if budget["blocked"]:
                reasons.append(budget["detail"])
    return {"can_start": not reasons, "reasons": reasons}


def prepare(store: JobStore, *, name: str, seed_blocks: int, concurrency: int, cost_budget: float | None = None) -> dict[str, Any]:
    if not name.strip() or len(name) > 80 or not 1 <= seed_blocks <= 20 or not 1 <= concurrency <= 5:
        raise ValueError("Choose a campaign name, 4 to 80 games in balanced groups of four, and 1 to 5 simultaneous games.")
    template = research_dir().parents[1] / "campaigns" / "monopoly-q4-recovery-v3-four-game-relay-20261025.json"
    config = json.loads(template.read_text())
    preparation_id = uuid.uuid4().hex
    campaign_id = "campaign-" + preparation_id
    identity = build_identity()
    entropy = os.urandom(32)
    # Serialize reservations so concurrent preparations cannot select the same seed.
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        excluded = {r["seed"] for cohort in load_seed_registry()["cohorts"].values() for r in cohort.get("seeds", [])}
        excluded.update(config["research_freeze"]["seed_draw"]["content"]["excluded_seeds"])
        excluded.update(r[0] for r in db.execute("SELECT seed FROM jobs UNION SELECT seed FROM cells"))
        for row in db.execute("SELECT value_json FROM account_state WHERE key LIKE 'campaign_preparation:%'"):
            excluded.update(json.loads(row[0])["config"]["seeds"])
        exclusion_record = sorted(excluded)
        draws: list[dict[str, Any]] = []
        counter = 0
        while len(draws) < seed_blocks:
            digest = hashlib.sha256(b"MonopolyBench/outcome-blind-seed-draw/v1\0" + campaign_id.encode() + b"\0" + entropy + counter.to_bytes(8, "big")).digest()
            seed = int.from_bytes(digest[:4], "big")
            if seed not in excluded:
                draws.append({"seed": seed, "draw_counter": counter, "draw_digest_sha256": digest.hex()})
                excluded.add(seed)
            counter += 1
        seeds = [r["seed"] for r in draws]
        order_seed = int.from_bytes(hashlib.sha256(b"MonopolyBench/execution-order/v1\0" + entropy).digest()[:4], "big")
        config.update(campaign_id=campaign_id, study_label=name.strip(), seed_cohort=campaign_id,
                      seeds=seeds, concurrency=concurrency, execution_order_seed=order_seed)
        if cost_budget is not None:
            import math
            if type(cost_budget) not in {int, float} or not math.isfinite(cost_budget) or cost_budget <= 0:
                raise ValueError("The recorded-spend threshold must be a positive finite USD amount.")
            config["cost_budget"] = cost_budget
            config["budget_policy"] = "recorded_spend_pause_threshold_existing_funding_only_no_purchases"
        analysis = copy.deepcopy(config["research_freeze"]["analysis_contract"]["content"])
        analysis.update(version="cloud_campaign_analysis_v1", behavior_source_commit=identity["git_sha"], status="recorded_before_execution",
                        claim_boundary=f"{seed_blocks} independent seed blocks, {seed_blocks * 4} correlated seat rotations. Report seed-level uncertainty and small-sample limits; no sample-size or power guarantee.")
        analysis["design"].update(cohort_role="owner_created_controlled_evaluation", independent_seed_blocks=seed_blocks, planned_games=seed_blocks * 4, seeds=seeds)
        analysis["social_review"]["coverage"] = "All games chronologically, every turn; no keyword-only exclusion."
        limits = analysis["stopping_and_reruns"]
        for key in list(limits):
            if key.startswith("max_execution_jobs_for_"):
                del limits[key]
        limits["max_execution_jobs"] = seed_blocks * 8
        if cost_budget is not None:
            analysis["billing"]["recorded_spend_pause_threshold_usd"] = cost_budget
            analysis["billing"]["launch_gate"] = "Pause new requests at the reported-spend threshold; missing costs pause capped execution. In-flight and concurrent calls may overshoot. Existing funds only, no purchases."
            limits["monetary_stop"] = analysis["billing"]["launch_gate"]
        order = list(range(seed_blocks * 4))
        random.Random(order_seed).shuffle(order)
        ranks = {index: rank for rank, index in enumerate(order)}
        cells: list[dict[str, Any]] = []
        for index in range(seed_blocks * 4):
            seed = seeds[index // 4]
            offset = index % 4
            models = MODELS[offset:] + MODELS[:offset]
            suffix = hashlib.sha256(encode([seed, models, None]).encode()).hexdigest()[:10]
            cells.append({"campaign_id": campaign_id, "cell_index": index, "run_id": f"{campaign_id}-{index}-{suffix}",
                          "seed": seed, "execution_rank": ranks[index], "models_by_seat": models, "status": "planned_not_started"})
        cells.sort(key=lambda r: r["execution_rank"])
        draw = {"cohort_id": campaign_id, "count": seed_blocks, "created_at": time.time(), "source_commit": identity["git_sha"],
                "status": "recorded_before_execution", "entropy_hex": entropy.hex(), "entropy_sha256": hashlib.sha256(entropy).hexdigest(),
                "excluded_seeds": exclusion_record, "seeds": draws, "first_draw_preserved": True, "outcome_information_used": False,
                "execution_order_seed": order_seed, "execution_order_method": "First big-endian uint32 of SHA-256(MonopolyBench/execution-order/v1 NUL || entropy bytes).",
                "registration": "Durable server preparation reserved before freeze; embedded cohort record supplements the packaged seed registry. This is not external preregistration."}
        matrix = {"status": "recorded_before_execution", "source_commit": identity["git_sha"], "planned_games": len(cells),
                  "independent_seed_blocks": seed_blocks, "concurrency": concurrency, "cells": cells}
        records = {"seed_draw": draw, "analysis_contract": analysis, "run_matrix": matrix}
        config["research_freeze"] = {key: {"path": f"campaigns/{campaign_id}/{key}.json", "sha256": hashlib.sha256(encode(value).encode()).hexdigest(), "content": value} for key, value in records.items()}
        validate_campaign_config(config)
        prepared = {"preparation_id": preparation_id, "config": config, "cells": cells, **identity}
        db.execute("INSERT INTO account_state VALUES(?,?,?)", ("campaign_preparation:" + preparation_id, encode(prepared), time.time()))
    store.audit("campaign_prepare", {"preparation_id": preparation_id, "campaign_id": campaign_id}, "dashboard")
    return {**prepared, "readiness": readiness(store, {"status": "draft", "config": config, **identity})}


def create(store: JobStore, preparation_id: str, idempotency_key: str) -> str:
    prepared = store.state("campaign_preparation:" + preparation_id)
    if not prepared:
        raise ValueError("This review is no longer available. Create a new campaign.")
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        key = "campaign_creation:" + idempotency_key
        old = db.execute("SELECT value_json FROM account_state WHERE key=?", (key,)).fetchone()
        if old and json.loads(old[0]) != preparation_id:
            raise ValueError("This save request belongs to a different campaign. Review the settings again.")
        if not old:
            db.execute("INSERT INTO account_state VALUES(?,?,?)", (key, encode(preparation_id), time.time()))
    config = prepared["config"]
    existing = store.rows("SELECT * FROM campaigns WHERE campaign_id=?", (config["campaign_id"],))
    if existing:
        return config["campaign_id"]
    identity = build_identity()
    if any(prepared[key] != identity[key] for key in ("git_sha", "image_digest")):
        raise ValueError("The app was updated during review. Create a new campaign to use the current version.")
    check = readiness(store, {"status": "draft", "config": config, **identity})
    if not check["can_start"]:
        raise ValueError(" ".join(check["reasons"]))
    freeze(store, config)
    return config["campaign_id"]
