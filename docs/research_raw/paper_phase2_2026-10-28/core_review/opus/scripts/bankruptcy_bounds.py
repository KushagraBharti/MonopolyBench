"""Liquidation bounds at every elimination (read-only): 56 applied declare_bankruptcy plus engine-automatic
bankruptcies triggered by a final liquidation action (CASH_CHANGED reason BANKRUPTCY after a non-declare action).
Bounds for automatic rows are computed at the triggering decision state (before its action).

For each LIQUIDATION_DECISION whose final applied action is declare_bankruptcy, reconstruct the
declarer's holdings from the delivered game_state and simulate engine liquidation rules
(engine.py: _sellable_building_space_indices, _mortgageable_space_indices, sell refund = house_cost//2
per level, hotel downgrade needs bank houses >= 4, mortgage blocked while the group has buildings):

  menu_now   = cash + mortgage values of currently mortgageable deeds (as the menu shows) + one
               step of currently sellable buildings is NOT included (pure first-screen view)
  accessible = cash + greedy simulation: sell houses first (they return houses to the bank), then
               hotel downgrades when bank >= 4, then mortgage everything unlocked; repeat
  full       = cash + all building value at house_cost//2 per level + all unmortgaged mortgage values
               (ignores the bank-house constraint)

Trades are not modelled. Output rows to ../bankruptcy_bounds.json and a table to stdout.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, game_dirs, decisions, action_state, ALIAS

board = json.load(open(os.path.join(ROOT, "contracts", "data", "board.json")))
HC = board["house_cost_by_group"]
SP = {}
for s in board["spaces"]:
    if s.get("kind") in ("PROPERTY", "RAILROAD", "UTILITY"):
        import re
        key = re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_")
        SP[key] = s
GROUPS = {}
for k, s in SP.items():
    if s.get("kind") == "PROPERTY":
        GROUPS.setdefault(s["group"], []).append(k)


def keyfix(k):
    return k if k in SP else {"B_O_RAILROAD": "B_O_RAILROAD"}.get(k, k)


def simulate(cash, owned, bank_houses):
    st = {h["space_key"]: {"houses": h["houses"], "hotel": h["hotel"], "mortgaged": h["mortgaged"]} for h in owned}
    steps = []

    def level(k):
        return 5 if st[k]["hotel"] else st[k]["houses"]

    def full_groups():
        return [g for g, ks in GROUPS.items() if all(k in st for k in ks)]

    while True:
        acted = False
        # 1) sell a house (non-hotel) on a max-level deed
        for g in full_groups():
            ks = GROUPS[g]
            mx = max(level(k) for k in ks)
            if mx <= 0:
                continue
            for k in ks:
                if level(k) == mx and not st[k]["hotel"] and st[k]["houses"] > 0:
                    st[k]["houses"] -= 1; bank_houses += 1; cash += HC[g] // 2
                    steps.append(f"sell house {k}"); acted = True; break
            if acted:
                break
        if acted:
            continue
        # 2) downgrade a hotel on a max-level deed when bank >= 4
        for g in full_groups():
            ks = GROUPS[g]
            mx = max(level(k) for k in ks)
            for k in ks:
                if level(k) == mx and st[k]["hotel"] and bank_houses >= 4:
                    st[k]["hotel"] = False; st[k]["houses"] = 4; bank_houses -= 4; cash += HC[g] // 2
                    steps.append(f"sell hotel {k}"); acted = True; break
            if acted:
                break
        if acted:
            continue
        # 3) mortgage anything unlocked
        for k, v in st.items():
            if v["mortgaged"] or v["houses"] or v["hotel"]:
                continue
            g = SP[k].get("group") if SP[k].get("kind") == "PROPERTY" else None
            if g and any(st.get(x, {}).get("houses") or st.get(x, {}).get("hotel") for x in GROUPS[g]):
                continue
            v["mortgaged"] = True; cash += SP[k]["price"] // 2
            steps.append(f"mortgage {k}"); acted = True; break
        if not acted:
            return cash, steps


def full_bound(cash, owned):
    tot = cash
    for h in owned:
        k = h["space_key"]; s = SP[k]
        if s.get("kind") == "PROPERTY":
            lv = 5 if h["hotel"] else h["houses"]
            tot += lv * (HC[s["group"]] // 2)
        if not h["mortgaged"]:
            tot += s["price"] // 2
    return tot


rows = []
from common import events
for g, run in game_dirs().items():
    st, rs = decisions(run)
    # every elimination = CASH_CHANGED reason BANKRUPTCY; attribute to the decision whose response precedes it
    triggers = []
    last = None
    for e in events(run):
        if e["type"] == "LLM_DECISION_RESPONSE":
            last = e["payload"]["decision_id"]
        if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY":
            triggers.append((last, e["seq"]))
    # walk back from an automatic trigger to the first LIQUIDATION_DECISION of the same debt episode
    for d, seq in triggers:
        s = st[d]
        fa = ((rs.get(d) or {}).get("final_action") or {}).get("action")
        kind = "declared" if fa == "declare_bankruptcy" else "automatic"
        a, gs = action_state(s)
        you = gs["you"]; cash = you["cash"]; owned = you["holdings"]["owned"]
        liq = a.get("scenario") or a.get("liquidation") or a
        owed = liq.get("owed_amount") or a.get("owed_amount")
        opts = (liq.get("options") or a.get("options") or {})
        menu_now = cash + sum(SP[k]["price"] // 2 for k in opts.get("mortgageable_space_keys", []))
        acc, steps = simulate(cash, owned, gs["bank"]["houses_remaining"])
        full = full_bound(cash, owned)
        rows.append(dict(game=g, decision=d[-10:], model=ALIAS[s["openrouter_model_id"]], player=s["player_id"],
                         elimination=kind, applied_action=fa, elimination_event_seq=seq,
                         owed=owed, cash=cash, menu_mortgage_only=menu_now, accessible=acc, full=full,
                         bank_houses=gs["bank"]["houses_remaining"], avoidable=acc >= owed,
                         steps=steps))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "bankruptcy_bounds.json"), "w"), indent=1)
print(f"{'G':>3} {'decision':>11} {'model':6} {'kind':9} {'owed':>5} {'cash':>5} {'menu':>5} {'access':>6} {'full':>5} bank avoid")
for r in rows:
    print(f"{r['game']:>3} {r['decision']:>11} {r['model']:6} {r['elimination']:9} {r['owed']:>5} {r['cash']:>5} {r['menu_mortgage_only']:>5} {r['accessible']:>6} {r['full']:>5} {r['bank_houses']:>4} {'YES' if r['avoidable'] else ''}")
print("n", len(rows), "declared", sum(r["elimination"] == "declared" for r in rows), "automatic", sum(r["elimination"] == "automatic" for r in rows),
      "avoidable(accessible>=owed)", sum(r["avoidable"] for r in rows), "accessible==full", sum(r["accessible"] == r["full"] for r in rows))
