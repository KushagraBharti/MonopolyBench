"""Read-only access to the twenty saved MonopolyBench research games.

This module reads canonical saved records (events, decisions, snapshots,
board data) and never imports the engine or calls a model. A compact cache
is written to the session scratch directory given by OPUS_CACHE (or a
local ``.cache`` folder) so repeated analyses do not re-read 354 MB of
decision logs. Every analysis that uses the cache also records the
SHA-256 of the source files it was built from.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import pickle
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
SAVED = REPO / "saved_games"
BOARD_PATH = REPO / "contracts" / "data" / "board.json"
CACHE_DIR = Path(os.environ.get("OPUS_CACHE", Path(__file__).resolve().parent / ".cache"))

LABEL = {
    "openai/gpt-6.1-sol": "Sol",
    "google/gemini-4-argon": "Gemini",
    "anthropic/claude-opus-5.5": "Opus",
    "x-ai/grok-4.7": "Grok",
}
CONFIGS = ["Sol", "Gemini", "Opus", "Grok"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def game_dirs() -> list[tuple[int, Path]]:
    out = []
    for p in sorted(glob.glob(str(SAVED / "railway-research-*" / "game-[0-9][0-9]-*"))):
        m = re.search(r"game-(\d+)-", p)
        out.append((int(m.group(1)), Path(p) / "run"))
    out.sort()
    assert [g for g, _ in out] == list(range(1, 21)), out
    return out


def normalize_key(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_").upper()


def board():
    b = json.loads(BOARD_PATH.read_text())
    spaces = {}
    for s in b["spaces"]:
        if s["kind"] in ("PROPERTY", "RAILROAD", "UTILITY"):
            key = normalize_key(s["name"])
            spaces[key] = {
                "index": s["index"], "name": s["name"], "kind": s["kind"],
                "group": s["group"], "price": s["price"],
                "mortgage": s["price"] // 2,
                "house_cost": b["house_cost_by_group"].get(s["group"]),
                "rents": b["property_rent_tables"].get(str(s["index"])),
            }
    groups = {}
    for k, s in spaces.items():
        groups.setdefault(s["group"], []).append(k)
    by_index = {s["index"]: k for k, s in spaces.items()}
    return spaces, groups, by_index


def _slim_attempt(a: dict) -> dict:
    raw = a.get("raw_response") or {}
    usage = raw.get("usage") if isinstance(raw, dict) else None
    choice = (raw.get("choices") or [{}])[0] if isinstance(raw, dict) else {}
    msg = choice.get("message") or {}
    return {
        "condition": a.get("response_condition"),
        "outcome": a.get("outcome"),
        "reason": a.get("reason"),
        "errors": a.get("validation_errors"),
        "refusal": msg.get("refusal"),
        "finish_reason": choice.get("finish_reason"),
        "native_finish_reason": choice.get("native_finish_reason"),
        "returned_model": raw.get("model") if isinstance(raw, dict) else None,
        "usage": usage,
        "content": a.get("assistant_content"),
        "reasoning_text": msg.get("reasoning"),
        "tool_call": a.get("parsed_tool_call"),
        "start_ms": a.get("request_start_ms"),
        "end_ms": a.get("response_end_ms"),
        "has_prompt": bool(a.get("prompt_messages")),
        "system_prompt": next((m["content"] for m in (a.get("prompt_messages") or []) if m.get("role") == "system"), None),
    }


def build_cache(force: bool = False) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / "corpus.pkl"
    if path.exists() and not force:
        return pickle.loads(path.read_bytes())
    games = {}
    hashes = {}
    for g, run in game_dirs():
        files = {n: run / n for n in ["events.jsonl", "decisions.jsonl", "players.json", "summary.json", "run_config.json", "seat_assignment.json"]}
        for n, p in files.items():
            hashes[f"G{g:02d}/{n}"] = sha256(p)
        events = [json.loads(l) for l in open(files["events.jsonl"])]
        players = json.loads(files["players.json"].read_text())["players"]
        pmodel = {p["player_id"]: LABEL[p["openrouter_model_id"]] for p in players}
        summary = json.loads(files["summary.json"].read_text())
        cfg = json.loads(files["run_config.json"].read_text())
        seats = json.loads(files["seat_assignment.json"].read_text())["assignments"]
        started, resolved = {}, {}
        order = []
        system_prompts = set()
        with open(files["decisions.jsonl"]) as f:
            for line_no, line in enumerate(f, 1):
                d = json.loads(line)
                did = d["decision_id"]
                idx = int(did.rsplit("-", 1)[1])
                if d["phase"] == "decision_started":
                    sysmsg = next((m["content"] for m in d["prompt_messages"] if m["role"] == "system"), None)
                    system_prompts.add(sysmsg)
                    started[idx] = {
                        "type": d["decision_type"], "player": d["player_id"], "turn": d["turn_index"],
                        "timestamp": d["timestamp"], "payload": d["prompt_payload"],
                        "reasoning": d.get("reasoning"), "line": line_no,
                        "system_sha": hashlib.sha256((sysmsg or "").encode()).hexdigest(),
                    }
                    order.append(idx)
                else:
                    resolved[idx] = {
                        "final_action": d.get("final_action"), "fallback_used": d.get("fallback_used"),
                        "fallback_reason": d.get("fallback_reason"), "retry_used": d.get("retry_used"),
                        "attempts": [_slim_attempt(a) for a in d.get("attempts", [])],
                        "seq_start": d.get("emitted_event_seq_start"), "seq_end": d.get("emitted_event_seq_end"),
                        "sequence_meta": {k: v for k, v in (d.get("sequence_meta") or {}).items() if k != "response_policy"},
                        "line": line_no, "timestamp": d.get("timestamp"),
                    }
        decisions = {i: {**started[i], **{"res": resolved.get(i)}} for i in order}
        games[g] = {
            "run": str(run.relative_to(REPO)), "events": events, "decisions": decisions,
            "pmodel": pmodel, "winner": summary["winner_player_id"], "turns": summary["turn_count"],
            "seed": cfg["seed"], "fingerprint": cfg.get("treatment_fingerprint"),
            "seats": {a["player_id"]: a["seat_index"] for a in seats},
            "n_system_prompts": len(system_prompts),
        }
    data = {"games": games, "hashes": hashes, "board_sha256": sha256(BOARD_PATH)}
    path.write_bytes(pickle.dumps(data))
    return data


def snapshot_paths(run: Path):
    return sorted(glob.glob(str(REPO / run / "state" / "turn_*.json")))


if __name__ == "__main__":
    import sys
    d = build_cache(force="--force" in sys.argv)
    print({g: (len(v["events"]), len(v["decisions"])) for g, v in d["games"].items()})
