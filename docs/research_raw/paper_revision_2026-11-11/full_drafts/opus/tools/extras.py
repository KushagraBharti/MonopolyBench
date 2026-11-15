"""Capacity gradient, opponent standing and same-deed ask pairs (fresh arithmetic).

Capacity: for opening and later offers whose acceptance completes only the
author's group, the author's cash after the exchange is compared with the
house cost of the newly completed group (one house; a full first layer).
Standing: asset value from the delivered request (cash + list price of
unmortgaged deeds + half list of mortgaged deeds + building cost), ranked
among living players; response by who leads.
Same-deed pairs: every game in which one seller asked cash for the same
deed set from a buyer the deed would complete and from one it would not.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"


def main():
    spaces, groups, _ = corpus.board()
    D = corpus.build_cache()
    rows = [r for r in json.loads((OUT / "offers_rebuilt.json").read_text()) if r["accept_legal"]]
    res = {}
    cap = defaultdict(Counter)
    for r in rows:
        if r["cell"] != "Author only":
            continue
        grp = r["author_new"][0]
        hc = spaces[groups[grp][0]]["house_cost"]
        cash = r["author_cash_after"]
        band = "full layer" if cash >= hc * len(groups[grp]) else ("one house" if cash >= hc else "less than one house")
        cap[(band, "opening" if r["opening"] else "later")][r["response"]] += 1
    res["capacity_author_only"] = {f"{k[0]}|{k[1]}": {"n": sum(v.values()), **v} for k, v in cap.items()}

    def worth(p):
        w = p["cash"]
        for h in p["holdings"]["owned"]:
            s = spaces[h["space_key"]]
            w += s["price"] // 2 if h["mortgaged"] else s["price"]
            if s["house_cost"]:
                w += s["house_cost"] * (h["houses"] + (5 if h["hotel"] else 0))
        return w
    stand = defaultdict(Counter)
    for r in rows:
        gs = D["games"][r["game"]]["decisions"][r["decision"]]["payload"]["game_state"]
        pl = [gs["you"]] + [o for o in gs["others"] if not o["bankrupt"]]
        W = {p["player_id"]: worth(p) for p in pl}
        lead = max(W, key=lambda k: W[k])
        who = "author leads" if lead == r["author"] else ("recipient leads" if lead == r["recipient"] else "third player leads")
        stand[(who, "opening" if r["opening"] else "later")][r["response"]] += 1
    res["standing"] = {f"{k[0]}|{k[1]}": {"n": sum(v.values()), **v} for k, v in stand.items()}

    P = json.loads((OUT / "pricing.json").read_text())["rows"]
    by = defaultdict(list)
    for p in P:
        if p["kind"] == "ask":
            by[(p["game"], p["seller"], tuple(p["deeds"]))].append(p)
    pairs = []
    for (g, s, deeds), xs in sorted(by.items()):
        comp = [x for x in xs if x["buyer_completes"]]
        oth = [x for x in xs if not x["buyer_completes"]]
        if not comp or not oth:
            continue
        def seq(ys):
            return [{"decision": y["decision"], "turn": y["turn"], "buyer": y["buyer_model"], "cash": y["cash"],
                     "mortgaged": y["any_mortgaged"], "seller_cash": y["seller_cash"], "opening": y["opening"]} for y in ys]
        fc, fo = comp[0]["cash"], oth[0]["cash"]
        pairs.append({"game": g, "seller_model": xs[0]["seller_model"], "deeds": list(deeds),
                      "completing": seq(comp), "other": seq(oth),
                      "first_ask_direction": "higher" if fc > fo else ("lower" if fc < fo else "equal"),
                      "mortgage_status_same": len({y["any_mortgaged"] for y in xs}) == 1,
                      "min_completing_vs_max_other": "higher" if min(y["cash"] for y in comp) > max(y["cash"] for y in oth) else "overlap"})
    res["same_deed_pairs"] = pairs
    res["same_deed_summary"] = {
        "pairs": len(pairs), "single_deed_pairs": sum(len(p["deeds"]) == 1 for p in pairs),
        "first_ask_single": Counter(p["first_ask_direction"] for p in pairs if len(p["deeds"]) == 1),
        "single_same_mortgage_status": Counter(p["first_ask_direction"] for p in pairs if len(p["deeds"]) == 1 and p["mortgage_status_same"]),
        "all_completing_above_all_other_single": Counter(p["min_completing_vs_max_other"] for p in pairs if len(p["deeds"]) == 1),
    }
    (OUT / "extras.json").write_text(json.dumps(res, indent=1, default=dict))
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["capacity_author_only"], indent=0))
    print(json.dumps(r["standing"], indent=0))
    print(json.dumps(r["same_deed_summary"], default=dict))
    for p in r["same_deed_pairs"]:
        print(p["game"], p["seller_model"], p["deeds"], p["first_ask_direction"], p["mortgage_status_same"], p["min_completing_vs_max_other"],
              [(c["turn"], c["buyer"], c["cash"], c["mortgaged"], c["seller_cash"]) for c in p["completing"]],
              [(c["turn"], c["buyer"], c["cash"], c["mortgaged"], c["seller_cash"]) for c in p["other"]])
