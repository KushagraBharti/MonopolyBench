#!/usr/bin/env python3
"""Cross-review check of the ownership-transfer numbers Astra and Sol retain.

Tracks deed ownership through stored events and counts (a) eliminations and
their creditors, (b) deeds and newly completed color groups moved by estates
and by trades, (c) whether a non-final elimination followed rent on a
developed color property, and (d) whether the first estate went to the
eventual winner.  Stored events and prompts only.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

from ro_corpus import board, complete_groups, load_all, write_json

BK = board()["by_key"]
IDX = {v["index"]: k for k, v in BK.items()}


def main():
    games = load_all()
    out = {"games": {}}
    tot = Counter()
    first_estate_to_winner = 0
    first_estate_rows = []
    nonterminal_rows = []
    for gn, g in games.items():
        owner = {}
        winner = [e for e in g.events if e["type"] == "GAME_ENDED"][0]["payload"]["winner_player_id"]
        elim = []          # (turn, debtor, creditor or None)
        pending = None     # bankruptcy in progress: {"debtor":..., "creditor":...}
        estate_deeds = Counter()
        estate_groups = Counter()
        trade_deeds = 0
        trade_groups = 0
        events = g.events
        n_alive = 4
        for i, e in enumerate(events):
            t, p = e["type"], e["payload"]
            if t == "PROPERTY_PURCHASED":
                key = IDX[p["space_index"]]
                if p.get("price") == 0 and pending and p["player_id"] == pending["creditor"]:
                    before = complete_groups(k for k, o in owner.items() if o == p["player_id"])
                    owner[key] = p["player_id"]
                    after = complete_groups(k for k, o in owner.items() if o == p["player_id"])
                    pending["deeds"] += 1
                    pending["groups"] |= (after - before)
                else:
                    owner[key] = p["player_id"]
            elif t == "AUCTION_ENDED" and p.get("winner_player_id"):
                owner[p["property_space"]] = p["winner_player_id"]
            elif t == "PROPERTY_TRANSFERRED":
                key = IDX[p["space_index"]]
                to = p["to_player_id"]
                before = complete_groups(k for k, o in owner.items() if o == to)
                owner[key] = to
                after = complete_groups(k for k, o in owner.items() if o == to)
                trade_deeds += 1
                trade_groups += len(after - before)
            elif t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY_CASH" and p.get("delta", 0) >= 0:
                # creditor receives the debtor's cash
                if pending is None:
                    pending = {"creditor": p["player_id"], "deeds": 0, "groups": set(), "turn": e["turn_index"]}
                else:
                    pending["creditor"] = p["player_id"]
            elif t == "CASH_CHANGED" and p.get("reason") in ("BANKRUPTCY", "BANKRUPTCY_ASSETS_TO_BANK"):
                debtor = p["player_id"]
                n_alive -= 1
                if p["reason"] == "BANKRUPTCY_ASSETS_TO_BANK":
                    for k in [k for k, o in owner.items() if o == debtor]:
                        del owner[k]
                    rec = {"debtor": debtor, "creditor": None, "turn": e["turn_index"], "deeds": 0, "groups": set(),
                           "terminal": n_alive == 1}
                    pending = None
                else:
                    if pending is None:
                        pending = {"creditor": None, "deeds": 0, "groups": set(), "turn": e["turn_index"]}
                    rec = pending
                    rec["debtor"] = debtor
                    rec["terminal"] = n_alive == 1
                    # creditor may be identified only by the following zero-price purchases
                    if rec["creditor"] is None:
                        for f in events[i + 1:i + 40]:
                            if f["type"] == "PROPERTY_PURCHASED" and f["payload"].get("price") == 0:
                                rec["creditor"] = f["payload"]["player_id"]
                                break
                            if f["type"] == "TURN_ENDED":
                                break
                elim.append(rec)
            elif t == "TURN_ENDED":
                pending = None
        for r in elim:
            r["groups"] = sorted(r["groups"])
        nonterm = [r for r in elim if not r["terminal"]]
        term = [r for r in elim if r["terminal"]]
        tot["eliminations"] += len(elim)
        tot["nonterminal"] += len(nonterm)
        tot["terminal"] += len(term)
        tot["nonterminal_to_player"] += sum(r["creditor"] is not None for r in nonterm)
        tot["nonterminal_estate_deeds"] += sum(r["deeds"] for r in nonterm)
        tot["nonterminal_estate_groups"] += sum(len(r["groups"]) for r in nonterm)
        tot["terminal_estate_deeds"] += sum(r["deeds"] for r in term)
        tot["terminal_estate_groups"] += sum(len(r["groups"]) for r in term)
        tot["trade_deeds"] += trade_deeds
        tot["trade_groups"] += trade_groups
        tot["nonterminal_to_eventual_winner"] += sum(r["creditor"] == winner for r in nonterm)
        if elim:
            fe = elim[0]
            first_estate_to_winner += fe["creditor"] == winner
            first_estate_rows.append({"game": gn, "first_out": g.model[fe["debtor"]],
                                      "creditor": g.model.get(fe["creditor"]), "winner": g.model[winner],
                                      "creditor_is_winner": fe["creditor"] == winner})
        out["games"][gn] = [{"turn": r["turn"], "debtor": g.model[r["debtor"]],
                             "creditor": g.model.get(r["creditor"]), "terminal": r["terminal"],
                             "deeds": r["deeds"], "groups": r["groups"]} for r in elim]
    out["totals"] = dict(tot)
    out["first_estate_creditor_is_winner"] = first_estate_to_winner
    out["first_estate_rows"] = first_estate_rows

    # rent on a developed color property, from the debtor's first liquidation prompt
    dev = 0
    rows = []
    debts = json.loads((__import__("pathlib").Path(__file__).resolve().parents[1] / "data/check_debts.json").read_text())
    elim_eps = [r for r in debts["all_rows"] if r["outcome"] == "eliminated"]
    for r in elim_eps:
        g = games[r["game"]]
        st = g.started[r["decision"]]
        gs = st["prompt_payload"]["game_state"]
        sc = st["prompt_payload"]["action_state"]["scenario"]
        alive = 1 + sum(not o["bankrupt"] for o in gs["others"])
        pos = gs["you"]["position"]
        cred = sc.get("owed_to_player_id")
        developed = False
        if sc.get("reason") == "RENT" and cred:
            for o in gs["others"]:
                if o["player_id"] == cred:
                    for h in o["holdings"]["owned"]:
                        if h["space_key"] == pos and (h["houses"] > 0 or h["hotel"]) and BK[pos]["group"] not in ("RAILROAD", "UTILITY"):
                            developed = True
        rows.append({"game": r["game"], "decision": r["decision"], "alive": alive, "reason": sc.get("reason"),
                     "creditor": g.model.get(cred), "position": pos, "developed_color_rent": developed})
    nonterm = [x for x in rows if x["alive"] > 2]
    out["eliminations_from_debt_ledger"] = len(rows)
    out["nonterminal_eliminations"] = len(nonterm)
    out["nonterminal_after_developed_color_rent"] = sum(x["developed_color_rent"] for x in nonterm)
    out["nonterminal_other"] = [x for x in nonterm if not x["developed_color_rent"]]
    write_json("check_economy.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "games"}, indent=1))


if __name__ == "__main__":
    main()
