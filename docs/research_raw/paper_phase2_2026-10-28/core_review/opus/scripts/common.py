"""Shared read-only loaders for Opus core-review checks. Reads canonical saved games only."""
import json, glob, os, csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
SG = os.path.join(ROOT, "saved_games")
COLLECTIONS = ["railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26"]
ALIAS = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Argon",
         "x-ai/grok-4.7": "Grok", "anthropic/claude-opus-5.5": "Opus"}


def game_dirs():
    out = {}
    for c in COLLECTIONS:
        for d in sorted(glob.glob(os.path.join(SG, c, "game-[0-9]*"))):
            n = int(os.path.basename(d).split("-")[1])
            out[n] = os.path.join(d, "run")
    return dict(sorted(out.items()))


def jl(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def decisions(run):
    """Return (started, resolved) dicts keyed by decision_id."""
    st, rs = {}, {}
    for r in jl(os.path.join(run, "decisions.jsonl")):
        (st if r["phase"] == "decision_started" else rs)[r["decision_id"]] = r
    return st, rs


def action_state(started):
    u = json.loads(started["prompt_messages"][1]["content"])
    return u["action_state"], u["game_state"]


def events(run):
    return list(jl(os.path.join(run, "events.jsonl")))
