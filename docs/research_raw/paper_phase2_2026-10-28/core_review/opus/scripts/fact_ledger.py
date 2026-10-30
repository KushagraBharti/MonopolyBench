"""Compact canonical fact ledger for one game (read-only): accepted trades with the correct author/direction,
auction results, building cash by player/group, unmortgages, eliminations. Usage: fact_ledger.py GAME"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, game_dirs, decisions, events, ALIAS

g = int(sys.argv[1])
run = game_dirs()[g]
st, rs = decisions(run)
seat = {}
for s in st.values():
    seat.setdefault(s["player_id"], ALIAS[s["openrouter_model_id"]])
board = json.load(open(os.path.join(ROOT, "contracts", "data", "board.json")))
NAME = {s["index"]: s["name"] for s in board["spaces"]}
GROUP = {s["index"]: s.get("group", s.get("kind")) for s in board["spaces"]}
dec_of = {}
last = None
ev = events(run)


def who(p):
    return f"{p}/{seat.get(p, '?')}"


def b(x):
    parts = []
    if x.get("cash"):
        parts.append(f"${x['cash']}")
    parts += x.get("properties", [])
    if x.get("get_out_of_jail_cards"):
        parts.append(f"{x['get_out_of_jail_cards']}xGOOJF")
    return "+".join(parts) or "nothing"


print("seats:", {p: m for p, m in sorted(seat.items())})
build = collections.defaultdict(lambda: collections.Counter())
sale = collections.defaultdict(lambda: collections.Counter())
pending_build = None
for e in ev:
    t, p = e["type"], e["payload"]
    if t == "LLM_DECISION_RESPONSE":
        last = p["decision_id"][-6:]
    if t == "TRADE_ACCEPTED":
        author = p["initiator_player_id"] if p["exchange_index"] % 2 == 0 else p["counterparty_player_id"]
        other = p["counterparty_player_id"] if author == p["initiator_player_id"] else p["initiator_player_id"]
        print(f"TRADE  seq{e['seq']} t{e['turn_index']} d{last}: {who(author)} gives {b(p['offer'])} ; {who(other)} gives {b(p['request'])}")
    if t == "AUCTION_ENDED":
        print(f"AUCTION seq{e['seq']} t{e['turn_index']} d{last}: {p.get('property_space')} -> {who(p.get('winner_player_id'))} ${p.get('winning_bid')} ({p.get('reason')})")
    if t == "CASH_CHANGED" and p.get("reason") == "BUILD":
        pending_build = (p["player_id"], -p["delta"])
    if t in ("HOUSE_BUILT", "HOTEL_BUILT") and pending_build:
        build[pending_build[0]][GROUP[p["space_index"]]] += 0  # group touched
        build[pending_build[0]]["_groups_" + GROUP[p["space_index"]]] = 1
    if t == "CASH_CHANGED" and p.get("reason") == "BUILD":
        pass
    if t == "CASH_CHANGED" and p.get("reason") == "SELL_BUILDING":
        sale[p["player_id"]]["total"] += p["delta"]
    if t == "PROPERTY_UNMORTGAGED":
        print(f"UNMORT seq{e['seq']} t{e['turn_index']} d{last}: {who(p['player_id'])} {NAME[p['space_index']]} ${p.get('amount', p.get('cost', '?'))}")
    if t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY":
        print(f"ELIM   seq{e['seq']} t{e['turn_index']} d{last}: {who(p['player_id'])}")
    if t == "GAME_ENDED":
        print("END", json.dumps(p)[:200])
# per-player build cash by group (attribute each BUILD cash event to the groups of following builds)
bg = collections.defaultdict(collections.Counter)
cur = None
for e in ev:
    t, p = e["type"], e["payload"]
    if t == "CASH_CHANGED" and p.get("reason") == "BUILD":
        cur = [p["player_id"], -p["delta"], collections.Counter()]
        bg[p["player_id"]]["_cash"] += -p["delta"]
    elif t in ("HOUSE_BUILT", "HOTEL_BUILT") and cur:
        cur[2][GROUP[p["space_index"]]] += p.get("count", 1)
    elif cur and t not in ("HOUSE_BUILT", "HOTEL_BUILT"):
        for grp in cur[2]:
            bg[cur[0]][grp] += cur[1] if len(cur[2]) == 1 else 0
        if len(cur[2]) > 1:
            bg[cur[0]]["_multi"] += cur[1]
        cur = None
for pl in sorted(bg):
    print("BUILD$", who(pl), dict(bg[pl]), "| SALES$", sale[pl]["total"])
