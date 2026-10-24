"""Frozen v2 campaigns; append-only seed blocks and deterministic cyclic seats."""
from __future__ import annotations

import hashlib
import json
import random
import time
from typing import Any

from monopoly_telemetry.writer_jsonl import atomic_write
from .execution_policy import MODELS, VERSION
from .job_store import JobStore, encode
from .player_config import default_provider_for_model
from .worker import build_identity


def player_specs(models: list[str] | None = None, effort: str = "medium") -> list[dict[str, Any]]:
    models = models or MODELS
    if len(models) != 4 or any(model not in MODELS for model in models) or effort not in {"low", "medium", "high"}:
        raise ValueError("Choose four supported models and low, medium, or high effort")
    return [{"player_id": f"p{i+1}", "name": model.split("/")[1], "openrouter_model_id": model,
             "reasoning": {"effort": effort}, "provider": default_provider_for_model(model)} for i, model in enumerate(models)]


def run_config(seed: int, run_id: str, models: list[str] | None = None, effort: str = "medium", max_turns: int | None = None) -> dict[str, Any]:
    return {**build_identity(), "seed": seed, "run_id": run_id, "players": player_specs(models, effort),
            "max_turns": max_turns, "max_trade_exchanges": 20, "max_auction_actions": 200,
            "execution_policy_version": VERSION}


def freeze(store: JobStore, config: dict[str, Any]) -> dict[str, Any]:
    from .research_registry import validate_campaign_config
    validate_campaign_config(config)
    import re
    if not re.fullmatch(r"[A-Za-z0-9_-]+", config["campaign_id"]):
        raise ValueError("Unsafe campaign ID")
    preflight = store.state("preflight", {})
    identity = build_identity()
    if not preflight.get("passed") or time.time() - preflight.get("created_at", 0) > 21600 or preflight.get("git_sha") != identity["git_sha"]:
        raise ValueError("A passing preflight on current code within six hours is required")
    seeds = config.get("seeds", [])
    if not seeds or len(set(seeds)) != len(seeds) or any(type(seed) is not int or not 0 <= seed < 2**32 for seed in seeds):
        raise ValueError("Provide distinct preregistered unsigned 32-bit seeds")
    if config.get("max_turns") is not None or config.get("seat_permutation") != "cyclic_4":
        raise ValueError("Full games require uncapped cyclic_4 configuration")
    if config.get("model_roster") != "frontier_2026q4_medium_4lab" or config.get("max_trade_exchanges", 20) != 20 or config.get("max_auction_actions", 200) != 200:
        raise ValueError("Cloud v2 requires the registered Q4 roster and unchanged negotiation limits")
    if config.get("rerun_policy") != {"max_reruns_per_cell": 1, "same_seed_and_seats": True} or config.get("billing", {}).get("enforcement") != "observe" or config.get("repetitions_per_seed") != 1:
        raise ValueError("Cloud v2 requires the frozen rerun and observational billing policies")
    campaign_id = config["campaign_id"]
    raw = encode(config)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
        if existing:
            if existing["config_sha256"] != digest:
                raise ValueError("Frozen campaign is immutable; use an amendment")
            return dict(existing)
        db.execute("INSERT INTO campaigns VALUES(?,?,?,?,?,?,?)", (campaign_id, raw, digest, "frozen", time.time(), identity["git_sha"], identity["image_digest"]))
        insert_cells(db, campaign_id, seeds, config["execution_order_seed"], 0)
    atomic_write(store.root / "campaigns" / campaign_id / "campaign.json", raw.encode())
    atomic_write(store.root / "campaigns" / campaign_id / "preflight.json", encode(preflight).encode())
    from .research_registry import research_dir
    hashes = {name: hashlib.sha256((research_dir() / name).read_bytes()).hexdigest() for name in ("monopoly_long_v1_model_rosters.json", "monopoly_long_v1_seed_registry.json")}
    atomic_write(store.root / "campaigns" / campaign_id / "freeze_manifest.json", encode({**identity, "registry_sha256": hashes, "config_sha256": digest}).encode())
    store.audit("freeze", {"campaign_id": campaign_id, "config_sha256": digest})
    return store.rows("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,))[0]


def insert_cells(db: Any, campaign_id: str, seeds: list[int], order_seed: int, start: int) -> None:
    matrix = [(seed, MODELS[offset:] + MODELS[:offset]) for seed in seeds for offset in range(4)]
    order = list(range(len(matrix)))
    random.Random(order_seed).shuffle(order)
    ranks = {index: rank+start for rank, index in enumerate(order)}
    for index, (seed, models) in enumerate(matrix, start):
        run_id = f"{campaign_id}-{index}-{hashlib.sha256(encode([seed, models, None]).encode()).hexdigest()[:10]}"
        db.execute("INSERT INTO cells(campaign_id,cell_index,run_id,seed,seat_order_json,execution_rank,status) VALUES(?,?,?,?,?,?,'queued')", (campaign_id, index, run_id, seed, encode(models), ranks[index-start]))


def amend(store: JobStore, campaign_id: str, seeds: list[int], reason: str) -> None:
    if not reason.strip() or not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or not 0 <= s < 2**32 for s in seeds):
        raise ValueError("An amendment needs a reason and distinct unsigned 32-bit seeds")
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        config = db.execute("SELECT config_json FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
        if not config:
            raise KeyError(campaign_id)
        old = db.execute("SELECT seed FROM cells WHERE campaign_id=?", (campaign_id,)).fetchall()
        if set(seeds) & {r[0] for r in old}:
            raise ValueError("Seed already registered")
        start = len(old)
        insert_cells(db, campaign_id, seeds, json.loads(config[0])["execution_order_seed"], start)
        index = db.execute("SELECT COUNT(*) FROM campaign_amendments WHERE campaign_id=?", (campaign_id,)).fetchone()[0]
        db.execute("INSERT INTO campaign_amendments VALUES(?,?,?,?,?,?)", (campaign_id, index, reason, encode({"add_seeds": seeds}), encode(list(range(start, start+4*len(seeds)))), time.time()))


def enqueue_cells(store: JobStore) -> None:
    cells = store.rows("SELECT cells.* FROM cells JOIN campaigns USING(campaign_id) WHERE campaigns.status='running' AND cells.job_id IS NULL ORDER BY cells.execution_rank")
    for cell in cells:
        campaign = store.rows("SELECT git_sha,image_digest FROM campaigns WHERE campaign_id=?", (cell["campaign_id"],))[0]
        identity = build_identity()
        if any(campaign[key] != identity.get(key) for key in ("git_sha", "image_digest")):
            store.execute("UPDATE cells SET not_started_reason='code_identity_mismatch' WHERE campaign_id=? AND cell_index=?", (cell["campaign_id"], cell["cell_index"]))
            continue
        job = store.create_job(run_config(cell["seed"], cell["run_id"], json.loads(cell["seat_order_json"])), kind="campaign", key=f"cell:{cell['campaign_id']}:{cell['cell_index']}", campaign_id=cell["campaign_id"], cell_index=cell["cell_index"], rank=cell["execution_rank"])
        store.execute("UPDATE cells SET job_id=? WHERE campaign_id=? AND cell_index=?", (job["job_id"], cell["campaign_id"], cell["cell_index"]))
