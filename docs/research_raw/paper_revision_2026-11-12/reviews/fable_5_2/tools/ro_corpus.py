"""Read-only loader for the twenty saved research games (cross-review copy).

Written for the 12 November cross-review so that the checks do not import any
frozen draft's code.  Reads ``decisions.jsonl``, ``events.jsonl``,
``players.json`` and the board contract.  Imports no engine or arena code,
executes no game or replay and contacts no provider.
"""
from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
SAVED = REPO / "saved_games"
COLLECTIONS = [
    SAVED / "railway-research-12-games-2026-10-25",
    SAVED / "railway-research-8-games-2026-10-26",
]
BOARD_PATH = REPO / "contracts" / "data" / "board.json"
REVISION = REPO / "docs/research_raw/paper_revision_2026-11-12"
OUT = Path(__file__).resolve().parents[1] / "data"

LABEL = {
    "gpt-6.1-sol": "Sol",
    "gemini-4-argon": "Gemini",
    "claude-opus-5.5": "Opus",
    "grok-4.7": "Grok",
}
MODELS = ["Sol", "Gemini", "Opus", "Grok"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def space_key(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_").upper()


@lru_cache(maxsize=1)
def board() -> dict:
    spec = json.loads(BOARD_PATH.read_text())
    by_key = {}
    for s in spec["spaces"]:
        if s.get("price") is None:
            continue
        key = space_key(s["name"])
        by_key[key] = {
            "key": key,
            "index": s["index"],
            "group": s["group"],
            "price": s["price"],
            "mortgage": s["price"] // 2,
            "house_cost": spec["house_cost_by_group"].get(s["group"]),
        }
    groups: dict[str, list[str]] = {}
    for row in by_key.values():
        groups.setdefault(row["group"], []).append(row["key"])
    color = {g: ks for g, ks in groups.items() if g not in ("RAILROAD", "UTILITY")}
    return {"by_key": by_key, "color_groups": color}


def complete_groups(owned) -> set[str]:
    owned = set(owned)
    return {g for g, ks in board()["color_groups"].items() if set(ks) <= owned}


class Game:
    def __init__(self, number: int, run: Path):
        self.number = number
        self.run = run
        self.block = (number - 1) // 4 + 1
        players = json.loads((run / "players.json").read_text())["players"]
        self.model = {p["player_id"]: LABEL[p["name"]] for p in players}
        self.started, self.resolved = {}, {}
        with open(run / "decisions.jsonl") as f:
            for line in f:
                rec = json.loads(line)
                k = int(rec["decision_id"].rsplit("-", 1)[1])
                (self.started if rec["phase"] == "decision_started" else self.resolved)[k] = rec
        assert sorted(self.started) == sorted(self.resolved) == list(range(len(self.started)))
        self.n = len(self.started)
        self._events = None

    @property
    def events(self) -> list[dict]:
        if self._events is None:
            self._events = [json.loads(line) for line in open(self.run / "events.jsonl")]
        return self._events

    def holdings(self, k: int) -> dict:
        gs = self.started[k]["prompt_payload"]["game_state"]
        out = {}
        for p in [gs["you"]] + gs["others"]:
            out[p["player_id"]] = {
                "cash": p["cash"],
                "bankrupt": p["bankrupt"],
                "owned": {h["space_key"]: h for h in p["holdings"]["owned"]},
            }
        return out

    def selected_attempt(self, k: int):
        sel = None
        for a in self.resolved[k]["attempts"]:
            if a.get("outcome") == "valid":
                sel = a
        return sel

    def provider_reasoning(self, k: int):
        a = self.selected_attempt(k) or self.resolved[k]["attempts"][-1]
        msg = ((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message") or {}
        return msg.get("reasoning")


def game_dirs() -> dict[int, Path]:
    out = {}
    for coll in COLLECTIONS:
        for p in sorted(coll.glob("game-[0-9][0-9]-*")):
            if p.is_dir():
                out[int(p.name.split("-")[1])] = p / "run"
    assert sorted(out) == list(range(1, 21)), sorted(out)
    return out


@lru_cache(maxsize=1)
def load_all() -> dict[int, Game]:
    return {n: Game(n, run) for n, run in game_dirs().items()}


def write_json(name: str, obj) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return path
