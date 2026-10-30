"""Rent ledger for one game: every RENT_PAID event (payer, owner, space, amount) and bankruptcy markers,
with per (payer,owner) totals. Usage: rent_ledger.py GAME [payer_pid owner_pid]. Read-only.
Note: RENT_PAID amount is the amount actually paid; a debt left unpaid at bankruptcy is not a rent payment."""
import sys, json, collections
from common import game_dirs, events
g = int(sys.argv[1]); flt = sys.argv[2:4]
ev = events(game_dirs()[g])
tot = collections.Counter()
for e in ev:
    if e["type"] == "RENT_PAID":
        p = e["payload"]
        k = (p.get("payer_player_id") or p.get("from_player_id"), p.get("owner_player_id") or p.get("to_player_id"))
        tot[k] += p.get("amount", 0)
        if not flt or list(k) == flt:
            print(e["seq"], e["turn_index"], json.dumps(p))
    if e["type"] in ("GAME_ENDED",) or "BANKRUPT" in e["type"]:
        print(e["seq"], e["turn_index"], e["type"], json.dumps(e["payload"])[:300])
print({f"{a}->{b}": v for (a, b), v in sorted(tot.items())})
