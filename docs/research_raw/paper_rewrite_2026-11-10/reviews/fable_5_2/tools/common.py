"""Shared read-only loaders for the Fable 5.2 cross-review checks.

Reads retained ledgers and canonical saved-game records. Never imports the
engine, never calls a model, never writes outside reviews/fable_5_2/.
"""
from __future__ import annotations

import glob
import json
import os
import re
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.dirname(HERE)
PKG = os.path.dirname(os.path.dirname(REVIEW))  # paper_rewrite_2026-11-10
REPO = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
DATA = os.path.join(PKG, "data")
OUT = os.path.join(REVIEW, "data")

MODEL = {
    "openai/gpt-6.1-sol": "Sol",
    "google/gemini-4-argon": "Gemini",
    "anthropic/claude-opus-5.5": "Opus",
    "x-ai/grok-4.7": "Grok",
}


def ledger(name: str):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


@lru_cache(maxsize=None)
def game_dir(game: int) -> str:
    hits = glob.glob(
        os.path.join(REPO, "saved_games", "railway-research-*", f"game-{game:02d}-*")
    )
    assert len(hits) == 1, (game, hits)
    return os.path.join(hits[0], "run")


@lru_cache(maxsize=None)
def decisions(game: int):
    """Return {index: {"started": rec, "resolved": rec}} for one game."""
    out: dict[int, dict] = {}
    with open(os.path.join(game_dir(game), "decisions.jsonl")) as fh:
        for line_no, line in enumerate(fh, 1):
            rec = json.loads(line)
            idx = int(rec["decision_id"].rsplit("-", 1)[1])
            slot = out.setdefault(idx, {})
            key = "started" if rec["phase"] == "decision_started" else "resolved"
            rec["_line"] = line_no
            slot[key] = rec
    return out


@lru_cache(maxsize=None)
def events(game: int):
    out = []
    with open(os.path.join(game_dir(game), "events.jsonl")) as fh:
        for line in fh:
            out.append(json.loads(line))
    return out


@lru_cache(maxsize=None)
def board():
    with open(os.path.join(REPO, "contracts", "data", "board.json")) as fh:
        b = json.load(fh)
    spaces = {}
    for sp in b["spaces"]:
        key = re.sub(r"[^A-Z0-9]+", "_", sp["name"].upper().replace("&", "")).strip("_")
        spaces[key] = sp
    return b, spaces


def dump(name: str, obj) -> str:
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return path


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
