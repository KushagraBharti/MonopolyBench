"""Read-only loader for the twenty saved research games.

Reads canonical ``events.jsonl`` and ``decisions.jsonl`` plus ``players.json``
and the board contract.  Imports no engine code, runs no game and makes no
model call.  Every analysis script in this directory builds on this loader so
that game numbering, model labels and source hashes are defined once.
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
OUT = Path(__file__).resolve().parents[1] / "data"

LABEL = {
    "gpt-6.1-sol": "Sol",
    "gemini-4-argon": "Gemini",
    "claude-opus-5.5": "Opus",
    "grok-4.7": "Grok",
}
MODELS = ["Sol", "Gemini", "Opus", "Grok"]
SEEDS = {1: 751774554, 2: 2506298840, 3: 2573692901, 4: 3648314310, 5: 2766649504}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_space_key(name: str) -> str:
    """Same rule as ``monopoly_engine.board.normalize_space_key`` (copied, not imported)."""
    return re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_").upper()


@lru_cache(maxsize=1)
def board() -> dict:
    spec = json.loads(BOARD_PATH.read_text())
    by_index, by_key = {}, {}
    for s in spec["spaces"]:
        if s["price"] is None:
            continue
        key = normalize_space_key(s["name"])
        row = {
            "index": s["index"],
            "key": key,
            "name": s["name"],
            "kind": s["kind"],
            "group": s["group"],
            "price": s["price"],
            "mortgage": s["price"] // 2,
            "house_cost": spec["house_cost_by_group"].get(s["group"]),
            "rents": spec["property_rent_tables"].get(str(s["index"])),
        }
        by_index[s["index"]] = row
        by_key[key] = row
    groups: dict[str, list[str]] = {}
    for row in by_index.values():
        groups.setdefault(row["group"], []).append(row["key"])
    color_groups = {g: ks for g, ks in groups.items() if g not in ("RAILROAD", "UTILITY")}
    return {
        "by_index": by_index,
        "by_key": by_key,
        "groups": groups,
        "color_groups": color_groups,
        "sha256": sha256_file(BOARD_PATH),
    }


def game_dirs() -> dict[int, Path]:
    out = {}
    for coll in COLLECTIONS:
        for p in sorted(coll.glob("game-[0-9][0-9]-*")):
            if not p.is_dir():
                continue
            n = int(p.name.split("-")[1])
            out[n] = p / "run"
    assert sorted(out) == list(range(1, 21)), sorted(out)
    return out


def block_of(game: int) -> int:
    return (game - 1) // 4 + 1


class Game:
    """One saved game: events, paired decision records and player labels."""

    def __init__(self, number: int, run: Path):
        self.number = number
        self.run = run
        self.block = block_of(number)
        self.rotation = (number - 1) % 4 + 1
        players = json.loads((run / "players.json").read_text())["players"]
        self.model = {p["player_id"]: LABEL[p["name"]] for p in players}
        self.pid_of = {v: k for k, v in self.model.items()}
        self.events_path = run / "events.jsonl"
        self.decisions_path = run / "decisions.jsonl"
        self.events = [json.loads(line) for line in open(self.events_path)]
        started, resolved = {}, {}
        self.decision_line = {}
        with open(self.decisions_path) as f:
            for lineno, line in enumerate(f, 1):
                rec = json.loads(line)
                k = int(rec["decision_id"].rsplit("-", 1)[1])
                if rec["phase"] == "decision_started":
                    started[k] = rec
                else:
                    resolved[k] = rec
                    self.decision_line[k] = lineno
        assert sorted(started) == sorted(resolved) == list(range(len(started)))
        self.started = started
        self.resolved = resolved
        self.n_decisions = len(started)
        end = [e for e in self.events if e["type"] == "GAME_ENDED"]
        assert len(end) == 1
        self.winner_pid = end[0]["payload"]["winner_player_id"]
        self.winner = self.model[self.winner_pid]
        self.turns = max(e["turn_index"] for e in self.events)
        # seat = position in turn order; players.json lists p1..p4 in seat order
        self.seat = {p["player_id"]: i + 1 for i, p in enumerate(players)}

    def source_hashes(self) -> dict:
        return {
            "events_sha256": sha256_file(self.events_path),
            "decisions_sha256": sha256_file(self.decisions_path),
        }

    # -- helpers -----------------------------------------------------------
    def dec_index(self, decision_id: str) -> int:
        return int(decision_id.rsplit("-", 1)[1])

    def state_before(self, k: int) -> dict:
        """Structured pre-decision state delivered to the acting player.

        Returns cash and holdings for all four players keyed by player id.
        Bankrupt players are present with whatever the prompt lists.
        """
        gs = self.started[k]["prompt_payload"]["game_state"]
        out = {}
        for p in [gs["you"]] + gs["others"]:
            out[p["player_id"]] = {
                "cash": p["cash"],
                "bankrupt": p["bankrupt"],
                "position": p["position"],
                "owned": {h["space_key"]: h for h in p["holdings"]["owned"]},
                "jail_cards": p.get("get_out_of_jail_cards", 0),
            }
        return {"players": out, "bank": gs["bank"], "turn": gs["metadata"]["turn_index"]}


@lru_cache(maxsize=1)
def load_all() -> dict[int, Game]:
    return {n: Game(n, run) for n, run in game_dirs().items()}


def write_json(name: str, obj) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    return path


def complete_groups(owned_keys) -> set[str]:
    """Color groups (not railroads/utilities) fully contained in ``owned_keys``."""
    owned = set(owned_keys)
    return {g for g, ks in board()["color_groups"].items() if set(ks) <= owned}


if __name__ == "__main__":
    games = load_all()
    tot_e = sum(len(g.events) for g in games.values())
    tot_d = sum(g.n_decisions for g in games.values())
    tot_a = sum(len(r["attempts"]) for g in games.values() for r in g.resolved.values())
    print("games", len(games), "events", tot_e, "decisions", tot_d, "attempts", tot_a)
    for n, g in games.items():
        print(n, g.block, g.rotation, g.turns, g.winner, g.seat[g.winner_pid], g.model)
