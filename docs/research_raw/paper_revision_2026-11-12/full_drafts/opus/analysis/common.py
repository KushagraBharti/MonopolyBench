"""Shared read-only helpers for the Opus 12 November draft.

Everything here reads stored records. Nothing imports the engine or arena,
runs a game, replays a game, calls a model or builds a synthetic state.
Every file read is hashed so outputs can name their inputs.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAFT = HERE.parent
REPO = next(p for p in DRAFT.parents if (p / "contracts").is_dir())
PRIOR = REPO / "docs/research_raw/paper_revision_2026-11-11/integrated"
OUT = DRAFT / "data"
OUT.mkdir(exist_ok=True)

SOURCES: dict[str, str] = {}


def _rel(p: Path) -> str:
    return str(p.resolve().relative_to(REPO))


def read_bytes(p: Path) -> bytes:
    blob = p.read_bytes()
    SOURCES[_rel(p)] = hashlib.sha256(blob).hexdigest()
    return blob


def read_json(p: Path):
    return json.loads(read_bytes(p))


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in read_bytes(p).splitlines() if line.strip()]


def write_json(name: str, obj) -> Path:
    path = OUT / name
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=False) + "\n")
    return path


# ---------------------------------------------------------------- board
@lru_cache(maxsize=1)
def board():
    b = read_json(REPO / "contracts/data/board.json")
    spaces = {re.sub("[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in b["spaces"]}
    return b, spaces


def mortgage_value(key: str) -> int:
    return board()[1][key]["price"] // 2


def list_price(key: str) -> int:
    return board()[1][key]["price"]


def group_of(key: str) -> str:
    return board()[1][key]["group"]


def house_cost(group: str) -> int:
    return board()[0]["house_cost_by_group"].get(group, 0)


# ---------------------------------------------------------------- ledgers
@lru_cache(maxsize=1)
def offers() -> list[dict]:
    """The 920-response offer ledger used by the 11 November integration.

    Its upstream copy is paper_rewrite_2026-11-10/data/agenda_offers.json
    (same SHA-256); earlier drafts rebuilt it against delivered prompts.
    """
    return read_json(PRIOR / "data/offers.json")


@lru_cache(maxsize=1)
def episodes() -> list[dict]:
    """The 188 explicit-liquidation episodes (Astra event reducer, reconciled)."""
    return read_json(PRIOR / "data/liquidation_episodes.json")


@lru_cache(maxsize=1)
def runs() -> dict[int, str]:
    return {r["game"]: r["source_run"] for r in offers()}


@lru_cache(maxsize=None)
def decisions(game: int) -> dict[str, dict[int, dict]]:
    rows = read_jsonl(REPO / runs()[game] / "decisions.jsonl")
    out: dict[str, dict[int, dict]] = {"decision_started": {}, "decision_resolved": {}}
    for r in rows:
        if r.get("phase") in out:
            out[r["phase"]][int(r["decision_id"].rsplit("-", 1)[1])] = r
    return out


def started(game: int, k: int) -> dict:
    return decisions(game)["decision_started"][k]


def resolved(game: int, k: int) -> dict:
    return decisions(game)["decision_resolved"][k]


def did_index(did: str) -> int:
    return int(did.rsplit("-", 1)[1])


def block_of(game: int) -> int:
    return (game - 1) // 4 + 1


# ---------------------------------------------------------------- offers
FORMS = ("swap", "cash_bid", "other")
CELLS = ("author_only", "recipient_only", "both", "neither")
CELL_LABEL = {"author_only": "Proposer only", "recipient_only": "Recipient only",
              "both": "Both", "neither": "Neither"}
FORM_LABEL = {"swap": "Swap", "cash_bid": "Cash bid", "other": "Other"}
MODELS = ("Sol", "Gemini", "Opus", "Grok")


def form(r: dict) -> str:
    """Offer form, identical to the 11 November integration definition.

    swap: deeds move in both directions (cash and jail cards may be added).
    cash_bid: the proposer offers only cash for deeds; no jail cards.
    other: everything else (deed-for-cash sales, gifts, card trades ...).
    """
    a, b = r["offer"], r["request"]
    if a["properties"] and b["properties"]:
        return "swap"
    if (b["properties"] and not a["properties"] and a["cash"] > 0 and b["cash"] == 0
            and not a["get_out_of_jail_cards"] and not b["get_out_of_jail_cards"]):
        return "cash_bid"
    return "other"


def stage(r: dict) -> str:
    return "opening" if r["exchange_index"] == 0 else "later"


def acr(rows) -> dict:
    c = Counter(r["response"] for r in rows)
    return {"n": len(rows), "A": c.get("accept_trade", 0), "C": c.get("counter_trade", 0),
            "R": c.get("reject_trade", 0)}


def net_list_value_to_recipient(r: dict) -> int:
    v = lambda side: side["cash"] + sum(list_price(k) for k in side["properties"])
    return v(r["offer"]) - v(r["request"])


def legal_offers() -> list[dict]:
    return [r for r in offers() if r["accept_available"]]


def sources_snapshot() -> dict:
    return dict(sorted(SOURCES.items()))
