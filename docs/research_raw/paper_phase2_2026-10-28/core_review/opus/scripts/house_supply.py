"""Read-only bank house supply per game from building events (32 houses, 12 hotels). HOUSE_BUILT takes houses;
HOTEL_BUILT returns that deed's 4 houses; HOUSE_SOLD returns houses; HOTEL_SOLD takes 4 houses back onto the deed
(the engine requires bank houses >= 4 for that). Buildings transferred to a creditor stay on the board (declared variant).
Reports minimum bank houses, events at zero, and which player's build reached zero. Exposure only: whether any player
was actually denied a legal build by shortage is NOT computed here. Usage: python3 scripts/house_supply.py > house_supply.log"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import game_dirs, decisions, events, ALIAS

tot = collections.Counter()
for g, run in sorted(game_dirs().items()):
    st, rs = decisions(run)
    seat = {}
    for s in st.values():
        seat.setdefault(s["player_id"], ALIAS[s["openrouter_model_id"]])
    houses = collections.Counter(); bank = 32; mn = 32; zero_by = []; holders_at_zero = None
    zero_events = 0
    for e in events(run):
        t, p = e["type"], e.get("payload", {})
        i = p.get("space_index")
        if t == "HOUSE_BUILT":
            houses[i] += p.get("count", 1); bank -= p.get("count", 1)
            if bank == 0:
                zero_by.append((e["seq"], seat[p["player_id"]]))
        elif t == "HOTEL_BUILT":
            bank += houses[i]; houses[i] = 0
        elif t == "HOUSE_SOLD":
            houses[i] -= p.get("count", 1); bank += p.get("count", 1)
        elif t == "HOTEL_SOLD":
            houses[i] += 4; bank -= 4
        if bank < 0:
            print(f"G{g} NEGATIVE bank {bank} at seq {e['seq']} (model of event semantics wrong)")
        mn = min(mn, bank)
        if bank == 0 and t.startswith(("HOUSE", "HOTEL")):
            zero_events += 1
    tot["games"] += 1
    tot["games_bank_zero"] += mn == 0
    print(f"G{g:2d} min_bank_houses {mn:2d} | reached 0 by: {', '.join(f'seq{s} {m}' for s, m in zero_by) or '-'}")
print(json.dumps(tot))
