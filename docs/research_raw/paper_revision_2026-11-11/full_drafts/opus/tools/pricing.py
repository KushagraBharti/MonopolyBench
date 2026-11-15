"""Cash-for-deed prices relative to board list price.

Population: acceptance-legal offers in which one side transfers only cash
and the other only deeds (no jail cards, no deeds both ways). An ask is
written by the deed holder (seller); a bid by the cash payer (buyer).
Ratio = cash / sum of the board list prices of the deeds. The buyer
"completes" when the deeds newly complete one of its colour groups.

Outputs medians by author configuration, buyer completion, mortgage status
and thread stage; every same-game/same-seller/same-deed-set pair priced
to buyers with different completion status; and settled sales.
Block-level (seed-cluster) summaries are given for the pooled ask contrast.
"""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"


def load():
    spaces, groups, _ = corpus.board()
    rows = json.loads((OUT / "offers_rebuilt.json").read_text())
    data = corpus.build_cache()
    block = {g: (g - 1) // 4 + 1 for g in range(1, 21)}
    out = []
    for r in rows:
        if not r["accept_legal"]:
            continue
        gives, asks = r["author_gives"], r["author_asks"]
        if gives["jail"] or asks["jail"]:
            continue
        if gives["properties"] and not gives["cash"] and asks["cash"] and not asks["properties"]:
            kind, deeds, cash = "ask", gives["properties"], asks["cash"]
            seller, buyer = r["author"], r["recipient"]
            buyer_completes = bool(r["recipient_new"])
            seller_completes = bool(r["author_new"])
            mortgaged = r["deeds_to_recipient_mortgaged"]
        elif asks["properties"] and not asks["cash"] and gives["cash"] and not gives["properties"]:
            kind, deeds, cash = "bid", asks["properties"], gives["cash"]
            seller, buyer = r["recipient"], r["author"]
            buyer_completes = bool(r["author_new"])
            seller_completes = bool(r["recipient_new"])
            mortgaged = r["deeds_to_author_mortgaged"]
        else:
            continue
        lst = sum(spaces[k]["price"] for k in deeds)
        game = data["games"][r["game"]]
        out.append({**{k: r[k] for k in ("game", "decision", "turn", "thread", "stage", "opening", "response", "author_model", "recipient_model", "author", "recipient", "selected_condition")},
                    "block": block[r["game"]], "kind": kind, "deeds": sorted(deeds), "cash": cash, "list": lst,
                    "ratio": cash / lst, "seller": seller, "buyer": buyer,
                    "seller_model": game["pmodel"][seller], "buyer_model": game["pmodel"][buyer],
                    "buyer_completes": buyer_completes, "seller_completes": seller_completes,
                    "any_mortgaged": bool(mortgaged), "seller_cash": r["recipient_cash"] if kind == "bid" else r["author_cash"],
                    "buyer_cash": r["author_cash"] if kind == "bid" else r["recipient_cash"],
                    "deed_groups": sorted({spaces[k]["group"] for k in deeds}),
                    "kinds": sorted({spaces[k]["kind"] for k in deeds})})
    return out


def med(xs):
    return round(st.median(xs), 3) if xs else None


def cell(xs):
    return {"n": len(xs), "median": med([x["ratio"] for x in xs])}


def main():
    P = load()
    res = {"population": {"asks": sum(p["kind"] == "ask" for p in P), "bids": sum(p["kind"] == "bid" for p in P)}}
    # pooled and split medians
    tab = {}
    for kind in ("ask", "bid"):
        for who in ["All", "Sol", "Gemini", "Opus", "Grok", "All but Opus"]:
            for mort in ["any", False, True]:
                for stage in ["any", "opening", "later"]:
                    sel = [p for p in P if p["kind"] == kind
                           and (who == "All" or (who == "All but Opus" and p["author_model"] != "Opus") or p["author_model"] == who)
                           and (mort == "any" or p["any_mortgaged"] == mort)
                           and (stage == "any" or p["opening"] == (stage == "opening"))]
                    tab[f"{kind}|{who}|mort={mort}|{stage}"] = {
                        "completes": cell([p for p in sel if p["buyer_completes"]]),
                        "not": cell([p for p in sel if not p["buyer_completes"]])}
    res["medians"] = tab
    # single street deeds only, to reduce composition
    singles = [p for p in P if len(p["deeds"]) == 1 and p["kinds"] == ["PROPERTY"]]
    res["single_street_deed"] = {}
    for kind in ("ask", "bid"):
        for who in ["All", "Sol", "Gemini", "Opus", "Grok"]:
            sel = [p for p in singles if p["kind"] == kind and (who == "All" or p["author_model"] == who)]
            res["single_street_deed"][f"{kind}|{who}"] = {"completes": cell([p for p in sel if p["buyer_completes"]]), "not": cell([p for p in sel if not p["buyer_completes"]])}
    # within-block ask contrast (seed clusters)
    res["ask_by_block"] = {}
    for b in range(1, 6):
        sel = [p for p in P if p["kind"] == "ask" and p["block"] == b]
        res["ask_by_block"][b] = {"completes": cell([p for p in sel if p["buyer_completes"]]), "not": cell([p for p in sel if not p["buyer_completes"]])}
    res["bid_by_block"] = {}
    for b in range(1, 6):
        sel = [p for p in P if p["kind"] == "bid" and p["block"] == b]
        res["bid_by_block"][b] = {"completes": cell([p for p in sel if p["buyer_completes"]]), "not": cell([p for p in sel if not p["buyer_completes"]])}
    # same game, same seller, same deed set, priced (ask or bid) to buyers that differ in completion
    groups = defaultdict(list)
    for p in P:
        groups[(p["game"], p["seller"], tuple(p["deeds"]))].append(p)
    pairs = []
    for (g, s, deeds), xs in groups.items():
        asks = [x for x in xs if x["kind"] == "ask"]
        comp = [x for x in asks if x["buyer_completes"]]
        non = [x for x in asks if not x["buyer_completes"]]
        if comp and non:
            pairs.append({"game": g, "seller": s, "seller_model": xs[0]["seller_model"], "deeds": list(deeds),
                          "completing_asks": [(x["decision"], x["buyer_model"], x["cash"], x["opening"], x["any_mortgaged"]) for x in comp],
                          "other_asks": [(x["decision"], x["buyer_model"], x["cash"], x["opening"], x["any_mortgaged"]) for x in non],
                          "max_completing": max(x["cash"] for x in comp), "max_other": max(x["cash"] for x in non),
                          "first_completing": comp[0]["cash"], "first_other": non[0]["cash"]})
    res["same_seller_deed_ask_pairs"] = pairs
    # including bids received by the seller as the price signal is the buyer's, not the seller's: kept separate
    res["settled_sales"] = []
    for p in P:
        if p["response"] == "accept_trade":
            res["settled_sales"].append({k: p[k] for k in ("game", "decision", "kind", "seller_model", "buyer_model", "deeds", "cash", "list", "ratio", "buyer_completes", "seller_cash", "any_mortgaged", "selected_condition")})
    sold = res["settled_sales"]
    res["settled_summary"] = {}
    for comp in (True, False):
        for low in (True, False):
            xs = [x for x in sold if x["buyer_completes"] == comp and (x["seller_cash"] < 100) == low]
            res["settled_summary"][f"buyer_completes={comp}|seller_cash<100={low}"] = {"n": len(xs), "median_ratio": med([x["ratio"] for x in xs]),
                                                                                     "opus_sellers": sum(x["seller_model"] == "Opus" for x in xs)}
    (OUT / "pricing.json").write_text(json.dumps({"rows": P, **res}, indent=1))
    return res


if __name__ == "__main__":
    r = main()
    for k, v in r["medians"].items():
        if "|any|any" in k or ("mort=any|" in k and ("opening" in k or "later" in k)) or "|any" in k:
            pass
    for k in [k for k in r["medians"] if k.endswith("mort=any|any")]:
        print(k, r["medians"][k])
    print("--- mortgage split")
    for k in [k for k in r["medians"] if "|any" in k and "mort=any" not in k]:
        print(k, r["medians"][k])
    print("--- stage split")
    for k in [k for k in r["medians"] if "mort=any" in k and not k.endswith("|any")]:
        print(k, r["medians"][k])
    print("--- single deed", json.dumps(r["single_street_deed"], indent=0))
    print("--- by block ask", r["ask_by_block"])
    print("--- by block bid", r["bid_by_block"])
    print("--- pairs")
    for p in r["same_seller_deed_ask_pairs"]:
        print(p)
    print(r["settled_summary"])
