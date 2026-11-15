"""Independent estate, trade-deed and rent counts read directly from canonical events.jsonl.

No engine import and no replay: this only reads recorded events.
Usage: python3 -I check_estates_from_events.py <repo_root> <out_json>
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

repo, out_path = Path(sys.argv[1]), Path(sys.argv[2])
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
runs = {r["game"]: r["source_run"] for r in json.loads((pkg / "data/agenda_offers.json").read_bytes())}
cohort = {g["game"]: g for g in json.loads((pkg / "data/t01_cohort.json").read_bytes())}
board = json.loads((repo / "contracts/data/board.json").read_bytes())
group = {s["index"]: s.get("group") for s in board["spaces"]}
COLORS = {"BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED", "YELLOW", "GREEN", "DARK_BLUE"}
tot = Counter()
per_game = {}
first_to_winner = all_three = 0
trigger = Counter()
for g in sorted(runs):
    ev = [json.loads(x) for x in (repo / runs[g] / "events.jsonl").read_bytes().splitlines()]
    winner = f"p{cohort[g]['winner_seat']}"
    tot["events"] += len(ev)
    tot["rent_payments"] += sum(e["type"] == "RENT_PAID" for e in ev)
    tot["rent_total"] += sum(e["payload"]["amount"] for e in ev if e["type"] == "RENT_PAID")
    # trade deeds and directed cash transfers
    tot["trade_accepted"] += sum(e["type"] == "TRADE_ACCEPTED" for e in ev)
    tot["trade_deeds"] += sum(e["type"] == "PROPERTY_TRANSFERRED" for e in ev)
    tot["trade_cash_transfers"] += sum(e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "TRADE_CASH"
                                       and e["payload"]["delta"] > 0 for e in ev)
    tot["trade_cash_total"] += sum(e["payload"]["delta"] for e in ev if e["type"] == "CASH_CHANGED"
                                   and e["payload"].get("reason") == "TRADE_CASH" and e["payload"]["delta"] > 0)
    tot["mortgage_interest_total"] += -sum(e["payload"]["delta"] for e in ev if e["type"] == "CASH_CHANGED"
                                           and e["payload"].get("reason") == "MORTGAGE_INTEREST")
    tot["mortgage_interest_events"] += sum(e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "MORTGAGE_INTEREST"
                                           for e in ev)
    elim = []
    for i, e in enumerate(ev):
        if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY":
            pid, t = e["payload"]["player_id"], e["turn_index"]
            j, deeds = i + 1, []
            while j < len(ev) and ev[j]["type"] == "PROPERTY_PURCHASED" and ev[j]["payload"].get("price") == 0:
                deeds.append((ev[j]["payload"]["player_id"], ev[j]["payload"]["space_index"]))
                j += 1
            cash = [x["payload"] for x in ev[max(0, i - 3):i] if x["type"] == "CASH_CHANGED"
                    and x["payload"].get("reason") == "BANKRUPTCY_CASH" and x["payload"]["delta"] > 0]
            creditor = cash[0]["player_id"] if cash else (deeds[0][0] if deeds else None)
            # trigger: last RENT-type debt context: find preceding PLAYER_MOVED of pid in the same turn
            mv = [x for x in ev[:i] if x["turn_index"] == t and x["type"] == "PLAYER_MOVED"]
            landed = mv[-1]["payload"]["to"] if mv else None
            elim.append({"turn": t, "debtor": pid, "creditor": creditor, "deeds": len(deeds),
                         "estate_cash": cash[0]["delta"] if cash else 0, "landed": landed,
                         "landed_group": group.get(landed)})
    assert len(elim) == 3, (g, len(elim))
    for k, x in enumerate(elim):
        terminal = k == 2
        tot["estate_deeds"] += x["deeds"]
        tot["estate_cash"] += x["estate_cash"]
        tot["elim_winner_creditor"] += x["creditor"] == winner
        tot["elim_bank_or_none"] += x["creditor"] is None
        if not terminal:
            tot["nonterminal_deeds"] += x["deeds"]
            tot["nonterminal_cash"] += x["estate_cash"]
            tot["nonterminal_winner_creditor"] += x["creditor"] == winner
            if x["creditor"] == winner:
                tot["nonterminal_deeds_to_winner"] += x["deeds"]
                tot["nonterminal_cash_to_winner"] += x["estate_cash"]
        else:
            tot["terminal_winner_creditor"] += x["creditor"] == winner
        trigger[(x["landed_group"] in COLORS, x["creditor"] is not None)] += 1
    first_to_winner += elim[0]["creditor"] == winner
    all_three += all(x["creditor"] == winner for x in elim)
    per_game[g] = {"winner": winner, "elims": elim}
out = {"totals": dict(tot), "first_estate_to_winner_games": first_to_winner, "all_three_to_winner_games": all_three,
       "landed_on_color_group_and_player_creditor": {str(k): v for k, v in trigger.items()}, "per_game": per_game}
out_path.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "per_game"}, indent=1))
print("non-winner creditors:", [(g, x["turn"], x["debtor"], x["creditor"]) for g, v in per_game.items()
                               for x in v["elims"] if x["creditor"] != v["winner"]])
