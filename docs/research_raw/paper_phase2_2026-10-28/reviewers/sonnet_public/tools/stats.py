"""usage: stats.py GAME -> aggregate counts for narrative headers (programmatic aid; not semantic review)"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
g = int(sys.argv[1]); rows = load_game(g)
ev = collections.Counter(); acts = collections.Counter(); byseat = collections.defaultdict(collections.Counter)
bank = []; end = None; accepted = []; auctions = []
att = collections.Counter()
for i, r in enumerate(rows, 1):
    a = r["applied_action"]["action"]; acts[a] += 1; byseat[r["player_id"]][a] += 1
    for x in r["attempt_metadata"]:
        att[(r["player_id"], x["outcome"])] += 1
    for e in r["events"]:
        ev[e["type"]] += 1
        if e["type"] == "TRADE_ACCEPTED": accepted.append((i, e["payload"]["initiator_player_id"], e["payload"]["counterparty_player_id"], e["payload"]["exchange_index"]))
        if e["type"] == "AUCTION_ENDED": auctions.append((i, sk(e["payload"]["property_space"]), e["payload"].get("winner_player_id"), e["payload"].get("winning_bid")))
        if e["type"] == "GAME_ENDED": end = (i, e["payload"], r["turn_index"])
    if a == "declare_bankruptcy": bank.append((i, r["player_id"], r["turn_index"]))
seats = {r["player_id"]: MODEL_SHORT.get(r["model"]) for r in rows}
print("seats", seats)
print("end", end); print("bankruptcies", bank)
print("accepted trades (line, initiator, acceptor-side, idx):", accepted)
print("auctions:", auctions)
print("counts: proposals", acts["propose_trade"], "counters", acts["counter_trade"], "accepts", acts["accept_trade"], "rejects", acts["reject_trade"],
      "builds", acts["build_houses_or_hotel"], "mortgage", acts["mortgage_property"], "unmort", acts["unmortgage_property"], "sell", acts["sell_houses_or_hotel"],
      "auction_started", acts["start_auction"], "buys", acts["buy_property"])
for s in sorted(byseat):
    c = byseat[s]
    print(" ", s, seats[s], "propose", c["propose_trade"], "counter", c["counter_trade"], "accept", c["accept_trade"], "reject", c["reject_trade"], "build", c["build_houses_or_hotel"], "start_auction", c["start_auction"], "buy", c["buy_property"], "mort", c["mortgage_property"], "bid", c["bid_auction"], "drop", c["drop_out"])
for pid in sorted(seats):
    e = pr = 0
    for r in rows:
        if r["player_id"] == pid and r["decision_type"] == "POST_TURN_ACTION_DECISION" and "propose_trade" in r["action_state"]["available_actions"]:
            e += 1; pr += r["applied_action"]["action"] == "propose_trade"
    print("  eligible propose_trade post-turn decisions", pid, seats[pid], pr, "/", e)
fb = [(i+1, r["player_id"]) for i, r in enumerate(rows) if r["fallback_used"]]
print("fallback-flagged decisions:", len(fb), fb[:20])
print("attempts non-valid by seat:", {k: v for k, v in att.items() if k[1] != "valid"})
last = rows[-1]["observation"]
pl = all_players(last)
print("final-decision cash:", {p: pl[p]["cash"] for p in sorted(pl)})
