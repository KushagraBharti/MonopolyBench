"""Read-only helpers over the saved research games.

Nothing here imports the rules engine, the arena, a replay tool or a model client.
Every function reads stored JSON or JSONL and does arithmetic on it.
"""
import functools
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "contracts").is_dir() and (p / "saved_games").is_dir())
DATA = PKG / "data"
SECTIONS = PKG / "sections"
ASSETS = PKG / "assets"

# G1..G20 -> canonical run directory. Copied from the 12 November package and checked
# against the directories on disk by 01_episodes.py.
GAME_MAP = json.loads((DATA / "game_map.json").read_text()) if (DATA / "game_map.json").exists() else {}
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
SHORT = {
    "MEDITERRANEAN_AVENUE": "Mediterranean", "BALTIC_AVENUE": "Baltic", "ORIENTAL_AVENUE": "Oriental",
    "VERMONT_AVENUE": "Vermont", "CONNECTICUT_AVENUE": "Connecticut", "ST_CHARLES_PLACE": "St. Charles",
    "STATES_AVENUE": "States", "VIRGINIA_AVENUE": "Virginia", "ST_JAMES_PLACE": "St. James",
    "TENNESSEE_AVENUE": "Tennessee", "NEW_YORK_AVENUE": "New York", "KENTUCKY_AVENUE": "Kentucky",
    "INDIANA_AVENUE": "Indiana", "ILLINOIS_AVENUE": "Illinois", "ATLANTIC_AVENUE": "Atlantic",
    "VENTNOR_AVENUE": "Ventnor", "MARVIN_GARDENS": "Marvin Gardens", "PACIFIC_AVENUE": "Pacific",
    "NORTH_CAROLINA_AVENUE": "North Carolina", "PENNSYLVANIA_AVENUE": "Pennsylvania",
    "PARK_PLACE": "Park Place", "BOARDWALK": "Boardwalk", "READING_RAILROAD": "Reading RR",
    "PENNSYLVANIA_RAILROAD": "Pennsylvania RR", "B_O_RAILROAD": "B&O RR", "SHORT_LINE": "Short Line",
    "ELECTRIC_COMPANY": "Electric Co.", "WATER_WORKS": "Water Works",
}


def mortgage_value(space_key):
    return SPACES[space_key]["price"] // 2


def run_dir(g):
    return ROOT / GAME_MAP[str(g)]


def decisions_path(g):
    return run_dir(g) / "decisions.jsonl"


@functools.lru_cache(maxsize=4)
def load(g):
    """Return (started, resolved, line_numbers) keyed by zero-based decision number."""
    started, resolved, lines = {}, {}, {}
    with open(decisions_path(g)) as f:
        for n, line in enumerate(f, 1):
            r = json.loads(line)
            i = int(r["decision_id"].rsplit("-", 1)[1])
            if r["phase"] == "decision_started":
                started[i] = r
            else:
                resolved[i] = r
                lines[i] = n
    return started, resolved, lines


@functools.lru_cache(maxsize=24)
def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def text_sha256(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def who(r):
    return NAME.get(r.get("player_name"), r.get("player_name"))


def message(attempt):
    try:
        return attempt["raw_response"]["choices"][0]["message"]
    except Exception:
        return {}


def provider_text(r, attempt=-1):
    """Readable reasoning text returned by the provider with one attempt, or ''."""
    return message(r["attempts"][attempt]).get("reasoning") or ""


def provider_detail_types(r, attempt=-1):
    return sorted({x.get("type") for x in (message(r["attempts"][attempt]).get("reasoning_details") or []) if x.get("type")})


FIN_ACTIONS = ("declare_bankruptcy", "mortgage_property", "sell_houses_or_hotel")


def named_action(content, allowed=None):
    """Last action name spelled out in assistant content, or None.

    This sees a conflict only where the content contains a parseable name. In the
    liquidation decisions only Grok's content does, so absence of a hit for another
    system is not evidence of agreement.
    """
    if not content:
        return None
    names = re.findall(r'"name"\s*:\s*"([a-z_]+)"', content)
    if allowed:
        names = [n for n in names if n in allowed]
    return names[-1] if names else None


def tex(s):
    """Escape text for LaTeX body use. Keeps Unicode; lualatex handles it."""
    if s is None:
        return ""
    out = []
    for ch in str(s):
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch == "→":
            out.append(r"\(\rightarrow\)")
        elif ch == "≥":
            out.append(r"\(\geq\)")
        elif ch == "≤":
            out.append(r"\(\leq\)")
        elif ch == "×":
            out.append(r"\(\times\)")
        elif ch == "≈":
            out.append(r"\(\approx\)")
        elif ch == "−":
            out.append(r"\(-\)")
        elif ch == '"':
            out.append(r"\char34{}")
        elif ch == "<":
            out.append(r"\textless{}")
        elif ch == ">":
            out.append(r"\textgreater{}")
        elif ch == "|":
            out.append(r"\textbar{}")
        else:
            out.append(ch)
    return "".join(out)


def money(n):
    return f"{n:,}"


def write_json(name, obj):
    path = DATA / name
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    return path


def read_json(name):
    return json.loads((DATA / name).read_text())
