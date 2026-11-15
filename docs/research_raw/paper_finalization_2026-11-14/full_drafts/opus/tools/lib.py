"""Shared read-only helpers for the Opus finalization draft.

Every function here reads stored JSON records (saved games, board data and the
retained integrated-package ledgers). Nothing imports or executes the rules
engine, a policy, a replay, a search or a model/provider call.
"""
from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAFT = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "contracts").is_dir() and (p / "saved_games").is_dir())
INTEGRATED = ROOT / "docs/research_raw/paper_revision_2026-11-12/integrated"
BOARD_FILE = ROOT / "contracts/data/board.json"
GAME_MAP_FILE = INTEGRATED / "data/game_map.json"
EPISODE_FILE = INTEGRATED / "data/liquidation_episodes.json"
OFFER_FILE = INTEGRATED / "data/offers.json"
FIRST_ACTION_FILE = INTEGRATED / "data/first_action_checks.json"

MODEL_LABEL = {
    "gpt-6.1-sol": "Sol",
    "gemini-4-argon": "Gemini",
    "claude-opus-5.5": "Opus",
    "grok-4.7": "Grok",
}


def label(model_name: str) -> str:
    for k, v in MODEL_LABEL.items():
        if k in model_name:
            return v
    return model_name


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha256_text(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def space_key(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


@lru_cache(maxsize=1)
def board():
    b = json.loads(BOARD_FILE.read_text())
    spaces = {}
    for s in b["spaces"]:
        if s.get("price"):
            spaces[space_key(s["name"])] = s
    groups: dict[str, list[str]] = {}
    for k, s in spaces.items():
        groups.setdefault(s["group"], []).append(k)
    return spaces, groups, b["house_cost_by_group"]


def mortgage_value(key: str) -> int:
    spaces, _, _ = board()
    return spaces[key]["price"] // 2


def unit_salvage(key: str) -> int:
    spaces, _, hc = board()
    return hc.get(spaces[key]["group"], 0) // 2


def group_of(key: str) -> str:
    spaces, _, _ = board()
    return spaces[key]["group"]


@lru_cache(maxsize=1)
def game_map() -> dict[str, str]:
    return json.loads(GAME_MAP_FILE.read_text())


def decisions_path(game: int) -> Path:
    return ROOT / game_map()[str(game)] / "decisions.jsonl"


def events_path(game: int) -> Path:
    return ROOT / game_map()[str(game)] / "events.jsonl"


@lru_cache(maxsize=None)
def decisions(game: int) -> dict[int, dict]:
    out: dict[int, dict] = {}
    with decisions_path(game).open() as fh:
        for line in fh:
            r = json.loads(line)
            idx = int(r["decision_id"].rsplit("-", 1)[1])
            out.setdefault(idx, {})[r["phase"]] = r
    return out


def decision(game: int, idx: int) -> dict:
    return decisions(game)[idx]


def message_of(attempt: dict) -> dict | None:
    raw = attempt.get("raw_response") or {}
    choices = raw.get("choices") or []
    if not choices:
        return None
    return choices[0].get("message")


def episodes() -> list[dict]:
    return json.loads(EPISODE_FILE.read_text())


def entry_state(game: int, idx: int) -> dict:
    """Resource accounting at the first liquidation menu of an episode."""
    spaces, groups, hc = board()
    s = decision(game, idx)["decision_started"]
    gs = s["prompt_payload"]["game_state"]
    sc = s["prompt_payload"]["action_state"]["scenario"]
    you = gs["you"]
    holdings = you["holdings"]["owned"]
    owned = {h["space_key"]: h for h in holdings}
    C = you["cash"]
    D = sc["owed_amount"]
    listed_m = list(sc["options"].get("mortgageable_space_keys", []))
    listed_s = list(sc["options"].get("sellable_building_space_keys", []))
    M0 = sum(mortgage_value(k) for k in listed_m)
    S = 0
    for h in holdings:
        u = unit_salvage(h["space_key"])
        S += (5 * u) if h["hotel"] else h["houses"] * u
    Mstar = sum(mortgage_value(h["space_key"]) for h in holdings if not h["mortgaged"])
    developed = sorted({group_of(k) for k, h in owned.items() if h["houses"] or h["hotel"]})
    complete = all(set(groups[g]) <= set(owned) for g in developed)
    level = lambda k: 5 if owned[k]["hotel"] else owned[k]["houses"]
    even = complete and all(
        max(level(k) for k in groups[g]) - min(level(k) for k in groups[g]) <= 1 for g in developed
    )
    hotels_by_group = {g: sum(1 for k in groups[g] if owned.get(k, {}).get("hotel")) for g in developed} if complete else {}
    houses_free = sum(
        owned[k]["houses"] for g in developed if hotels_by_group.get(g, 0) == 0 for k in groups[g]
    ) if complete else None
    bank = gs["bank"]
    return {
        "game": game,
        "decision": idx,
        "turn": s["turn_index"],
        "player": s["player_id"],
        "model": label(s["player_name"]),
        "C": C,
        "D": D,
        "M0": M0,
        "S": S,
        "Mstar": Mstar,
        "U0": C + S + M0,
        "Ustar": C + S + Mstar,
        "listed_mortgages": listed_m,
        "listed_sales": listed_s,
        "developed_groups": developed,
        "complete": complete,
        "even": even,
        "hotels_by_group": hotels_by_group,
        "hotels": sum(hotels_by_group.values()),
        "houses_in_hotel_free_groups": houses_free,
        "bank_houses": bank["houses_remaining"],
        "bank_hotels": bank["hotels_remaining"],
        "holdings": holdings,
        "menu_actions": [a if isinstance(a, str) else a.get("action") for a in s["prompt_payload"]["action_state"].get("available_actions", [])],
    }


def write_json(name: str, obj) -> Path:
    path = DRAFT / "data" / name
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    return path
