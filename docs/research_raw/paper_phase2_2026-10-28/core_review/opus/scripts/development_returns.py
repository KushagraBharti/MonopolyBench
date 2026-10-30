"""Read-only development-to-rent conversion. Per (game, player, colour group): building spend (HOUSE_BUILT/HOTEL_BUILT x
house_cost_by_group), building-sale proceeds (HOUSE_SOLD/HOTEL_SOLD x half cost; hotel sale counted as one unit), and
DEVELOPED rent actually received on that group's spaces (RENT_PAID amount > 2 x base rent, which only a built deed can
charge under board.json tables). Rent owed but unpaid at an elimination is NOT rent (it moves via BANKRUPTCY_CASH and
asset transfer) and is reported separately per creditor as bankruptcy cash. No causal or counterfactual claim.
Usage: python3 scripts/development_returns.py > development_returns.log"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, game_dirs, decisions, events, ALIAS, action_state

board = json.load(open(os.path.join(ROOT, "contracts", "data", "board.json")))
GROUP = {s["index"]: s.get("group") for s in board["spaces"]}
KIND = {s["index"]: s["kind"] for s in board["spaces"]}
RT = {int(k): v for k, v in board["property_rent_tables"].items()}
KEYIDX = {s["name"].upper().replace(" ", "_").replace(".", "").replace("&", ""): s["index"] for s in board["spaces"]}
BOUNDS = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bankruptcy_bounds.json")))
lethal_rows = []
HC = board["house_cost_by_group"]
rows = []
for g, run in sorted(game_dirs().items()):
    st, rs = decisions(run)
    seat = {}
    for s in st.values():
        seat.setdefault(s["player_id"], ALIAS[s["openrouter_model_id"]])
    ev = events(run)
    winner = next(e["payload"].get("winner_player_id") for e in ev if e["type"] == "GAME_ENDED")
    spend = collections.Counter(); sold = collections.Counter(); drent = collections.Counter(); urent = collections.Counter()
    hits = collections.Counter(); bkcash = collections.Counter()
    for e in ev:
        t, p = e["type"], e.get("payload", {})
        if t in ("HOUSE_BUILT", "HOTEL_BUILT"):
            gr = GROUP[p["space_index"]]
            spend[(p["player_id"], gr)] += HC[gr] * p.get("count", 1)
        elif t in ("HOUSE_SOLD", "HOTEL_SOLD"):
            gr = GROUP[p["space_index"]]
            sold[(p["player_id"], gr)] += HC[gr] // 2 * p.get("count", 1)
        elif t == "RENT_PAID" and KIND.get(p["space_index"]) == "PROPERTY":
            idx = p["space_index"]; gr = GROUP[idx]
            if p["amount"] > 2 * RT[idx][0]:
                drent[(p["to_player_id"], gr)] += p["amount"]; hits[(p["to_player_id"], gr)] += 1
            else:
                urent[(p["to_player_id"], gr)] += p["amount"]
        elif t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_CASH" and p.get("delta", 0) > 0:
            bkcash[p["player_id"]] += p["delta"]
    # elimination trigger square: eliminated player's position in the delivered state of the eliminating decision,
    # attributed to the creditor's group only if that square is a PROPERTY of the creditor's built group
    lethal = collections.Counter(); lethal_amt = collections.Counter()
    bk_cred = {}
    pend = None
    last_bk = None
    for e in ev:
        t, p = e["type"], e.get("payload", {})
        if t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_CASH" and p.get("delta", 0) > 0:
            pend = p["player_id"]
        elif t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY":
            bk_cred[e["seq"]] = pend; pend = None; last_bk = e["seq"]
        elif t == "PROPERTY_PURCHASED" and p.get("price") == 0 and last_bk and bk_cred.get(last_bk) is None:
            bk_cred[last_bk] = p["player_id"]
        elif t in ("LLM_DECISION_REQUESTED", "TURN_STARTED", "GAME_ENDED"):
            last_bk = None
    for b in [b for b in BOUNDS if b["game"] == g]:
        k = next(k for k in st if k.endswith(b["decision"]))
        a, gs = action_state(st[k])
        pos = gs["you"].get("position")
        idx = KEYIDX.get(pos)
        cred = bk_cred.get(b["elimination_event_seq"])
        grp = GROUP.get(idx) if idx is not None and KIND.get(idx) == "PROPERTY" else None
        lethal_rows.append(dict(game=g, decision=b["decision"], eliminated=seat[b["player"]], owed=b["owed"], square=pos,
                                creditor=cred and seat[cred], creditor_group=grp))
        if grp and cred:
            lethal[(cred, grp)] += 1; lethal_amt[(cred, grp)] += b["owed"]
    keys = sorted(set(spend) | set(drent) | set(lethal))
    for k in keys:
        rows.append(dict(game=g, player=k[0], model=seat[k[0]], group=k[1], winner=(k[0] == winner), spend=spend[k],
                         sale_proceeds=sold[k], developed_rent=drent[k], developed_hits=hits[k], undeveloped_rent=urent[k],
                         lethal_hits=lethal[k], lethal_owed=lethal_amt[k]))
    for pid, v in bkcash.items():
        rows.append(dict(game=g, player=pid, model=seat[pid], group="_BANKRUPTCY_CASH", winner=(pid == winner), spend=0,
                         sale_proceeds=0, developed_rent=0, developed_hits=0, undeveloped_rent=0, bankruptcy_cash=v,
                         lethal_hits=0, lethal_owed=0))
dev = [r for r in rows if r["spend"] > 0]
zero = [r for r in dev if r["developed_rent"] == 0]
zero_nolethal = [r for r in zero if r["lethal_hits"] == 0]
def summ(rs):
    s = sum(r["spend"] for r in rs); d = sum(r["developed_rent"] for r in rs)
    return dict(episodes=len(rs), spend=s, developed_rent=d, zero_rent=sum(1 for r in rs if r["developed_rent"] == 0),
                zero_rent_and_no_lethal_hit=sum(1 for r in rs if r["developed_rent"] == 0 and r["lethal_hits"] == 0),
                lethal_hits=sum(r["lethal_hits"] for r in rs))
out = {"all_built_episodes": summ(dev), "winner": summ([r for r in dev if r["winner"]]),
       "non_winner": summ([r for r in dev if not r["winner"]]),
       "by_model": {m: summ([r for r in dev if r["model"] == m]) for m in ("Argon", "Grok", "Opus", "Sol")},
       "inherited_only_rent_episodes": [(r["game"], r["model"], r["group"], r["developed_rent"]) for r in rows
                                         if r["spend"] == 0 and r["developed_rent"] > 0 and r["group"] != "_BANKRUPTCY_CASH"]}
for r in rows:
    if r["group"] != "_BANKRUPTCY_CASH":
        print(f"G{r['game']:2d} {r['player']}/{r['model']:5s} {'W' if r['winner'] else ' '} {r['group']:10s} spend {r['spend']:5d} "
              f"sold {r['sale_proceeds']:4d} dev_rent {r['developed_rent']:5d} ({r['developed_hits']} hits) undev_rent {r['undeveloped_rent']:4d} "
              f"lethal {r['lethal_hits']} (owed {r['lethal_owed']})")
print("ZERO-DEVELOPED-RENT EPISODES (spend>0):")
for r in zero:
    print(f"  G{r['game']} {r['model']} {r['group']} spend {r['spend']} sold {r['sale_proceeds']} winner={r['winner']} lethal_hits={r['lethal_hits']}")
print("ELIMINATION TRIGGER SQUARES:")
for L in lethal_rows:
    print(f"  G{L['game']} {L['decision']} {L['eliminated']} owed {L['owed']} at {L['square']} creditor {L['creditor']} group {L['creditor_group']}")
out_lethal = collections.Counter("creditor_colour_group_property" if L["creditor_group"] else ("bank_or_nonproperty" if True else "") for L in lethal_rows)
out["elimination_trigger"] = dict(out_lethal)
print(json.dumps(out, indent=1))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "development_returns.json"), "w"), indent=0)
