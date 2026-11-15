"""Bargaining tabulations used in the manuscript (fresh arithmetic).

Inputs: data/offers_rebuilt.json (rebuilt from delivered prompts by
offers.py), data/pricing.json (pricing.py) and the two retained
LLM-assisted reason-coding ledgers (inherited semantic labels; joined, not
re-coded). Seed blocks are games 1-4, 5-8, 9-12, 13-16, 17-20.

Every contrast is reported pooled, by recipient/author configuration, by
seed block and with each block left out, because offers share threads,
players and boards and the design has only five seeds.
"""
from __future__ import annotations

import json
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"
NEG = corpus.REPO / "docs/research_raw/paper_agenda_revision_2026-10-29"
CODE1 = NEG / "negotiation/rejection_reason_coding.json"
CODE2 = NEG / "reviews/negotiation/reason_comparison.json"
CFG = ["Sol", "Gemini", "Opus", "Grok"]


def block(g):
    return (g - 1) // 4 + 1


def rate(xs, resp):
    return (sum(x["response"] == resp for x in xs), len(xs))


def pct(a):
    k, n = a
    return None if n == 0 else round(100 * k / n, 1)


def bundle(r):
    return (tuple(sorted(r["author_gives"]["properties"])), tuple(sorted(r["author_asks"]["properties"])),
            r["author_gives"]["jail"], r["author_asks"]["jail"])


def net_to_recipient(r):
    return r["author_gives"]["cash"] - r["author_asks"]["cash"]


def main():
    rows = json.loads((OUT / "offers_rebuilt.json").read_text())
    legal = [r for r in rows if r["accept_legal"]]
    res = {}
    # 1. census
    cells = ["Author only", "Recipient only", "Both", "Neither"]
    cen = {}
    for c in cells:
        for stage in ("all", "opening", "later"):
            xs = [r for r in legal if r["cell"] == c and (stage == "all" or r["opening"] == (stage == "opening"))]
            cen[f"{c}|{stage}"] = {"n": len(xs), **{k: sum(x["response"] == k for x in xs) for k in ("accept_trade", "counter_trade", "reject_trade")}}
    res["census"] = cen
    # 2. joint recipient x stage x cell
    joint = {}
    for m in CFG:
        for stage in ("opening", "later"):
            for c in cells:
                xs = [r for r in legal if r["recipient_model"] == m and r["opening"] == (stage == "opening") and r["cell"] == c]
                joint[f"{m}|{stage}|{c}"] = {"n": len(xs), **{k: sum(x["response"] == k for x in xs) for k in ("accept_trade", "counter_trade", "reject_trade")}}
    res["joint"] = joint
    # 3. opening rejection: author-only vs neither
    def open_contrast(sel):
        a = [r for r in sel if r["opening"] and r["cell"] == "Author only"]
        n = [r for r in sel if r["opening"] and r["cell"] == "Neither"]
        ra, rn = rate(a, "reject_trade"), rate(n, "reject_trade")
        return {"author_only": ra, "neither": rn, "diff_pp": None if not a or not n else round(pct(ra) - pct(rn), 1)}
    res["open_reject"] = {"pooled": open_contrast(legal)}
    for m in CFG:
        res["open_reject"][f"recipient={m}"] = open_contrast([r for r in legal if r["recipient_model"] == m])
    for b in range(1, 6):
        res["open_reject"][f"block={b}"] = open_contrast([r for r in legal if block(r["game"]) == b])
        res["open_reject"][f"without_block={b}"] = open_contrast([r for r in legal if block(r["game"]) != b])
    res["open_reject"]["standard_recipients_only"] = open_contrast([r for r in legal if r["recipient_model"] != "Opus"])
    # 4. within-thread concessions on an unchanged bundle
    by = defaultdict(list)
    for r in rows:
        by[r["thread"]].append(r)
    conc = []
    for t, xs in by.items():
        xs.sort(key=lambda r: r["stage"])
        last = {}
        for r in xs:
            p = last.get(r["author"])
            if p is not None and bundle(p) == bundle(r) and net_to_recipient(r) > net_to_recipient(p):
                conc.append({**{k: r[k] for k in ("game", "decision", "thread", "cell", "recipient_model", "author_model", "response", "stage")},
                             "concession": net_to_recipient(r) - net_to_recipient(p), "previous_response": None})
            last[r["author"]] = r
    res["concessions"] = {"n": len(conc)}
    for c in cells:
        xs = [x for x in conc if x["cell"] == c]
        res["concessions"][c] = {"n": len(xs), **{k: sum(x["response"] == k for x in xs) for k in ("accept_trade", "counter_trade", "reject_trade")},
                                 "median_concession": st.median([x["concession"] for x in xs]) if xs else None}
    for m in CFG:
        for c in ("Author only", "Neither"):
            xs = [x for x in conc if x["cell"] == c and x["recipient_model"] == m]
            res["concessions"][f"{c}|recipient={m}"] = {"n": len(xs), "accept": sum(x["response"] == "accept_trade" for x in xs)}
    for b in range(1, 6):
        for c in ("Author only", "Neither"):
            xs = [x for x in conc if x["cell"] == c and block(x["game"]) == b]
            res["concessions"][f"{c}|block={b}"] = {"n": len(xs), "accept": sum(x["response"] == "accept_trade" for x in xs)}
    res["concession_rows"] = conc
    # 5. counters that reprice the same noncash bundle (author-only and neither, requesting >=1 deed)
    rep = {}
    for c in ("Author only", "Neither"):
        cnt = 0
        same_more = 0
        for t, xs in by.items():
            xs = sorted(xs, key=lambda r: r["stage"])
            for i, r in enumerate(xs[:-1]):
                if r["cell"] != c or r["response"] != "counter_trade" or not r["accept_legal"] or not r["author_asks"]["properties"]:
                    continue
                nx = xs[i + 1]
                cnt += 1
                # counter terms are written by the former recipient: author/recipient swap
                same = (sorted(nx["author_asks"]["properties"]) == sorted(r["author_gives"]["properties"]) and
                        sorted(nx["author_gives"]["properties"]) == sorted(r["author_asks"]["properties"]) and
                        nx["author_asks"]["jail"] == r["author_gives"]["jail"] and nx["author_gives"]["jail"] == r["author_asks"]["jail"])
                # cash to counterer: counterer is r's recipient = nx author
                cash_r = r["author_gives"]["cash"] - r["author_asks"]["cash"]  # to counterer in r
                cash_n = nx["author_asks"]["cash"] - nx["author_gives"]["cash"]  # to counterer in nx
                if same and cash_n > cash_r:
                    same_more += 1
        rep[c] = {"counters_requesting_deed": cnt, "same_bundle_more_cash": same_more}
    res["counter_repricing"] = rep
    # 6. pricing summary and settled distress split
    P = json.loads((OUT / "pricing.json").read_text())
    pr = P["rows"]
    def med(xs):
        return round(st.median(xs), 3) if xs else None
    price = {}
    for kind in ("ask", "bid"):
        for who in ("All", "Sol", "Gemini", "Opus", "Grok", "Standard authors"):
            sel = [p for p in pr if p["kind"] == kind and (who == "All" or p["author_model"] == who or (who == "Standard authors" and p["author_model"] != "Opus"))]
            price[f"{kind}|{who}"] = {"completing": [len([p for p in sel if p["buyer_completes"]]), med([p["ratio"] for p in sel if p["buyer_completes"]])],
                                      "other": [len([p for p in sel if not p["buyer_completes"]]), med([p["ratio"] for p in sel if not p["buyer_completes"]])]}
        for b in range(1, 6):
            sel = [p for p in pr if p["kind"] == kind and p["block"] == b]
            price[f"{kind}|block={b}"] = {"completing": [len([p for p in sel if p["buyer_completes"]]), med([p["ratio"] for p in sel if p["buyer_completes"]])],
                                          "other": [len([p for p in sel if not p["buyer_completes"]]), med([p["ratio"] for p in sel if not p["buyer_completes"]])]}
    for who in ("Sol", "Opus", "Grok"):
        for mort in (False, True):
            sel = [p for p in pr if p["kind"] == "ask" and p["author_model"] == who and p["any_mortgaged"] == mort]
            price[f"ask|{who}|mortgaged={mort}"] = {"completing": [len([p for p in sel if p["buyer_completes"]]), med([p["ratio"] for p in sel if p["buyer_completes"]])],
                                                    "other": [len([p for p in sel if not p["buyer_completes"]]), med([p["ratio"] for p in sel if not p["buyer_completes"]])]}
    res["prices"] = price
    res["same_deed_pairs"] = P["same_seller_deed_ask_pairs"]
    sold = [p for p in pr if p["response"] == "accept_trade"]
    settle = {}
    for comp in (True, False):
        for excl in (False, True):
            xs = [p for p in sold if p["buyer_completes"] == comp and (not excl or p["seller_model"] != "Opus")]
            low = [p for p in xs if p["seller_cash"] < 100]
            settle[f"completes={comp}|exclude_opus_sellers={excl}"] = {
                "sales": len(xs), "seller_cash_lt_100": len(low),
                "median_ratio_low": med([p["ratio"] for p in low]), "median_ratio_rest": med([p["ratio"] for p in xs if p["seller_cash"] >= 100]),
                "median_seller_cash": med([p["seller_cash"] for p in xs]), "opus_sellers": sum(p["seller_model"] == "Opus" for p in xs)}
    res["settled_sales"] = settle
    # 7. reason codes (inherited semantic labels), joined to rebuilt offers
    c1 = json.loads(CODE1.read_text())
    c2 = json.loads(CODE2.read_text())
    keyrows = {f"G{r['game']:02d}d{r['decision']}": r for r in c1["rows_data"]}
    joinrows = {(r["game"], r["decision"]): r for r in rows}
    codes = {}
    for cat in ("D", "C"):
        info = c2["categories"][cat]
        common = set(info["common_positive_keys"])
        n = len(keyrows)
        a, b = info["first_pass_positive"], info["reviewer_positive"]
        agree = info["common_positive"] + info["both_negative"]
        po = agree / n
        pe = (a / n) * (b / n) + (1 - a / n) * (1 - b / n)
        kappa = (po - pe) / (1 - pe)
        by_cell, by_model = Counter(), Counter()
        tot_cell, tot_model = Counter(), Counter()
        for k, r in keyrows.items():
            o = joinrows[(r["game"], r["decision"])]
            assert o["response"] == "reject_trade" and o["recipient_new"], k
            tot_cell[o["cell"]] += 1
            tot_model[o["recipient_model"]] += 1
            if k in common:
                by_cell[o["cell"]] += 1
                by_model[o["recipient_model"]] += 1
        codes[cat] = {"rows": n, "first_pass": a, "reviewer": b, "common": info["common_positive"], "both_negative": info["both_negative"],
                      "disagreements": info["disagreement_rows"], "kappa": round(kappa, 3),
                      "common_by_cell": dict(by_cell), "rows_by_cell": dict(tot_cell),
                      "common_by_recipient": dict(by_model), "rows_by_recipient": dict(tot_model),
                      "games_G1_G15_share": sum(1 for k in common if k.startswith("G01") or k.startswith("G15"))}
    res["reason_codes"] = codes
    res["reason_sources"] = {"first_pass": str(CODE1.relative_to(corpus.REPO)), "first_pass_sha256": corpus.sha256(CODE1),
                             "comparison": str(CODE2.relative_to(corpus.REPO)), "comparison_sha256": corpus.sha256(CODE2)}
    (OUT / "bargaining.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["census"], indent=0))
    print(json.dumps(r["open_reject"], indent=0))
    print(json.dumps({k: v for k, v in r["concessions"].items()}, indent=0))
    print(json.dumps(r["counter_repricing"]))
    print(json.dumps(r["settled_sales"], indent=0))
    print(json.dumps(r["reason_codes"], indent=0))
    for k, v in r["prices"].items():
        print(k, v)
