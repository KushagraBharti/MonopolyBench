"""Read-only: for each game, how the winner's built-on colour groups were assembled (purchase/auction, accepted trade,
creditor inheritance), the winner's accepted-trade count, and creditors of all 60 eliminations.
Mechanical provenance only (first acquisition route of each deed the winner held when it first built on that group);
no counterfactual or causal claim. Usage: python3 scripts/winner_sources.py > winner_sources.log"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, game_dirs, decisions, events, ALIAS

board = json.load(open(os.path.join(ROOT, "contracts", "data", "board.json")))
GROUP = {s["index"]: s.get("group") for s in board["spaces"]}
NAME = {s["index"]: s["name"] for s in board["spaces"]}
bounds = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bankruptcy_bounds.json")))
out = []
tot = collections.Counter()
for g, run in sorted(game_dirs().items()):
    st, rs = decisions(run)
    seat = {}
    for s in st.values():
        seat.setdefault(s["player_id"], ALIAS[s["openrouter_model_id"]])
    ev = events(run)
    winner = next(e["payload"].get("winner_player_id") for e in ev if e["type"] == "GAME_ENDED")
    route = {}  # space_index -> (owner, route) latest acquisition route per owner
    in_trade = False
    in_bk = False
    first_build = {}
    trades_w = 0
    creditors = []
    pending = None
    elim_seqs = {b["elimination_event_seq"]: b for b in bounds if b["game"] == g}
    for e in ev:
        t, p = e["type"], e.get("payload", {})
        if t == "TRADE_ACCEPTED":
            in_trade = True
            if winner in (p.get("initiator_player_id"), p.get("counterparty_player_id")):
                trades_w += 1
            continue
        if t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_CASH" and p.get("delta", 0) > 0:
            pending = p["player_id"]
            continue
        if t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY":
            in_bk = True
            b = elim_seqs.get(e["seq"])
            creditors.append([b and b["decision"], p.get("player_id"), pending])
            pending = None
            continue
        if t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_ASSETS_TO_BANK" and creditors and creditors[-1][2] is None:
            creditors[-1][2] = "bank"
        if t == "PROPERTY_TRANSFERRED" and in_trade:
            route[p.get("space_index")] = (p.get("to_player_id") or p.get("player_id"), "trade")
            continue
        if t == "PROPERTY_PURCHASED":
            if in_bk and p.get("price") == 0:
                route[p["space_index"]] = (p["player_id"], "inherited")
                if creditors and creditors[-1][2] is None:
                    creditors[-1][2] = p["player_id"]
            else:
                route[p["space_index"]] = (p["player_id"], "bought")
            continue
        if t in ("LLM_DECISION_REQUESTED", "TURN_STARTED", "TURN_ENDED"):
            in_trade = False
            in_bk = False
        if t in ("HOUSE_BUILT",) and p.get("player_id") == winner:
            grp = GROUP[p["space_index"]]
            if grp not in first_build:
                members = [i for i, gg in GROUP.items() if gg == grp]
                first_build[grp] = {NAME[i]: route.get(i, (None, "?"))[1] for i in members}
    for c in creditors:
        if c[2] is None:
            c[2] = "UNRESOLVED"
    kinds = collections.Counter()
    for grp, m in first_build.items():
        rts = set(m.values())
        k = "inherited" if "inherited" in rts else ("trade" if "trade" in rts else "bought_only")
        kinds[k] += 1
    wcred = sum(1 for c in creditors if c[2] == winner)
    tot["games"] += 1
    tot["winner_trades>0"] += trades_w > 0
    tot["winner_built_groups"] += len(first_build)
    for k, v in kinds.items():
        tot["groups_" + k] += v
    tot["any_trade_or_inherited_built_group"] += bool(kinds["trade"] or kinds["inherited"])
    tot["eliminations"] += len(creditors)
    tot["winner_creditor"] += wcred
    tot["bank_creditor"] += sum(1 for c in creditors if c[2] == "bank")
    tot["unresolved_creditor"] += sum(1 for c in creditors if c[2] == "UNRESOLVED")
    tot["terminal_to_winner"] += bool(creditors and creditors[-1][2] == winner)
    out.append(f"G{g:2d} winner {winner}/{seat[winner]:5s} accepted_trades_as_party {trades_w:2d} | built groups: "
               + "; ".join(f"{grp}:{'/'.join(sorted(set(m.values())))}" for grp, m in first_build.items())
               + f" | creditors: " + ", ".join(f"{c[0]}->{c[1]}/{seat.get(c[1])} to {c[2]}" for c in creditors))
print("\n".join(out))
print(json.dumps(tot))
