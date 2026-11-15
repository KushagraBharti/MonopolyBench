"""Read-only helpers for the saved research games. No engine, replay or model imports."""
import json, os, re, functools
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "contracts").is_dir())
REV = ROOT / "docs/research_raw/paper_revision_2026-11-12"
INT = REV / "integrated"
GM = json.loads((INT / "data/game_map.json").read_text())
NAME = {"gpt-6.1-sol": "Sol", "gemini-4-argon": "Gemini", "claude-opus-5.5": "Opus", "grok-4.7": "Grok"}
BOARD = json.loads((ROOT / "contracts/data/board.json").read_text())


def key(name):
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", name.upper())).strip("_")


SPACES = {key(s["name"]): s for s in BOARD["spaces"] if "price" in s}
HOUSE_COST = BOARD["house_cost_by_group"]
COLORS = {}
for _k, _s in SPACES.items():
    if _s["kind"] == "PROPERTY":
        COLORS.setdefault(_s["group"], set()).add(_k)


def run_dir(g):
    return ROOT / GM[str(g)]


@functools.lru_cache(maxsize=3)
def load(g):
    """Return (started, resolved) dicts keyed by zero-based decision number."""
    started, resolved = {}, {}
    with open(run_dir(g) / "decisions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            i = int(r["decision_id"].rsplit("-", 1)[1])
            (started if r["phase"] == "decision_started" else resolved)[i] = r
    return started, resolved


def events(g):
    return [json.loads(line) for line in open(run_dir(g) / "events.jsonl")]


def who(r):
    return NAME.get(r.get("player_name"), r.get("player_name"))


def message(attempt):
    try:
        return attempt["raw_response"]["choices"][0]["message"]
    except Exception:
        return {}


def reasoning(r):
    """Reasoning text the provider returned with the final attempt, or ''."""
    return message(r["attempts"][-1]).get("reasoning") or ""


def named_action(r):
    """Action named in the final attempt's assistant content, if any."""
    c = r["attempts"][-1].get("assistant_content")
    if not c:
        return None
    m = re.search(r'"name"\s*:\s*"([a-z_]+)"', c)
    return m.group(1) if m else None
