"""Shared helpers for the observable-behavior review (Sonnet public scope).

Reads only: public_review/game-XX.jsonl and contracts/data/board.json.
"""
import json
import re

ROOT = "/Users/kushagra/CS-Projects/MonopolyBench"
PR = ROOT + "/docs/research_raw/paper_phase2_2026-10-28/public_review"
OUT = ROOT + "/docs/research_raw/paper_phase2_2026-10-28/reviewers/sonnet_public"

BOARD = json.load(open(ROOT + "/contracts/data/board.json"))


def _key(name):
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


IDX2KEY = {}
KEY2IDX = {}
KEY2PRICE = {}
KEY2GROUP = {}
KEY2NAME = {}
for s in BOARD["spaces"]:
    k = _key(s["name"])
    IDX2KEY[s["index"]] = k
    KEY2IDX[k] = s["index"]
    KEY2NAME[k] = s["name"]
    if s.get("price"):
        KEY2PRICE[k] = s["price"]
        KEY2GROUP[k] = s["group"]
HOUSE_COST = BOARD["house_cost_by_group"]

SHORT = {
    "MEDITERRANEAN_AVENUE": "MED", "BALTIC_AVENUE": "BAL", "READING_RAILROAD": "RDG",
    "ORIENTAL_AVENUE": "ORI", "VERMONT_AVENUE": "VER", "CONNECTICUT_AVENUE": "CON",
    "ST_CHARLES_PLACE": "STC", "ELECTRIC_COMPANY": "ELE", "STATES_AVENUE": "STA",
    "VIRGINIA_AVENUE": "VIR", "PENNSYLVANIA_RAILROAD": "PRR", "ST_JAMES_PLACE": "STJ",
    "TENNESSEE_AVENUE": "TEN", "NEW_YORK_AVENUE": "NYA", "KENTUCKY_AVENUE": "KEN",
    "INDIANA_AVENUE": "IND", "ILLINOIS_AVENUE": "ILL", "B_O_RAILROAD": "BO",
    "ATLANTIC_AVENUE": "ATL", "VENTNOR_AVENUE": "VEN", "WATER_WORKS": "WW",
    "MARVIN_GARDENS": "MAR", "PACIFIC_AVENUE": "PAC", "NORTH_CAROLINA_AVENUE": "NCA",
    "PENNSYLVANIA_AVENUE": "PEA", "SHORT_LINE": "SL", "PARK_PLACE": "PKP", "BOARDWALK": "BW",
}
GSHORT = {"BROWN": "BR", "LIGHT_BLUE": "LB", "PINK": "PK", "ORANGE": "OR", "RED": "RD",
          "YELLOW": "YL", "GREEN": "GR", "DARK_BLUE": "DB", "RAILROAD": "RR", "UTILITY": "UT"}
GORDER = ["BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED", "YELLOW", "GREEN", "DARK_BLUE", "RAILROAD", "UTILITY"]
for k in list(KEY2GROUP):
    if k not in SHORT:
        SHORT[k] = k[:3]
# sanity: every priced key has a short code
for k in KEY2PRICE:
    assert k in SHORT, k

MODEL_SHORT = {
    "anthropic/claude-opus-5.5": "Opus",
    "openai/gpt-6.1-sol": "Sol",
    "google/gemini-4-argon": "Argon",
    "x-ai/grok-4.7": "Grok",
}


def sk(k):
    return SHORT.get(k, k)


def load_game(g):
    rows = []
    with open("%s/game-%02d.jsonl" % (PR, g)) as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def bundle_str(b):
    parts = []
    if b.get("cash"):
        parts.append("$%d" % b["cash"])
    for p in b.get("properties", []):
        parts.append(sk(p))
    if b.get("get_out_of_jail_cards"):
        parts.append("GOOJx%d" % b["get_out_of_jail_cards"])
    return "+".join(parts) if parts else "nothing"


def holdings_str(pl):
    """Compact holdings by group: LB:ORI0,VER0 ; mortgaged '~' ; houses digit ; hotel H."""
    by = {}
    for o in pl["holdings"]["owned"]:
        k = o["space_key"]
        g = KEY2GROUP.get(k, "?")
        lvl = "H" if o.get("hotel") else str(o.get("houses", 0))
        s = sk(k) + ("~" if o.get("mortgaged") else "") + (lvl if g not in ("RAILROAD", "UTILITY") else "")
        by.setdefault(g, []).append(s)
    out = []
    for g in GORDER:
        if g in by:
            out.append("%s:%s" % (GSHORT[g], ",".join(by[g])))
    return " ".join(out) if out else "-"


def book_value(pl):
    v = pl["cash"]
    for o in pl["holdings"]["owned"]:
        k = o["space_key"]
        pr = KEY2PRICE.get(k, 0)
        v += pr // 2 if o.get("mortgaged") else pr
        g = KEY2GROUP.get(k)
        hc = HOUSE_COST.get(g, 0)
        n = 5 if o.get("hotel") else o.get("houses", 0)
        v += hc * n
    return v


def all_players(obs):
    """Return dict pid -> player-state (self + others) for an observation."""
    d = {obs["you"]["player_id"]: obs["you"]}
    for o in obs["others"]:
        d[o["player_id"]] = o
    return d
