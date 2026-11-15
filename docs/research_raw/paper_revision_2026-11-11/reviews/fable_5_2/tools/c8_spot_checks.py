"""Check 8. Spot recomputation of headline numbers from the other drafts.

Existing-record arithmetic on the frozen Fable offer ledger and price rows.
(a) Opus: cash concessions on an unchanged non-cash bundle (9 of 58, 24 of 86).
(b) Astra: author-only against recipient-only rejection, by stage, leave one
    seed block out.
(c) Sol: seller by mortgage by stage ask cells (11 of 12).
(d) Fable: asks by the buyer's distance to completion.
(e) Same seller, game and single deed: first, median and last ask.
"""
import json, hashlib, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
PURE = ROOT / "full_drafts/fable_5_2/data/a6_pure_offers.json"
SOLP = ROOT / "full_drafts/sol/data/price_rows.json"
ASTP = ROOT / "full_drafts/astra/data/single_deed_prices.json"
OUT = HERE.parent / "data/c8_spot_checks.json"
led = json.load(open(LED))
legal = [r for r in led if r["accept_available"]]
res = {}

# (a) concessions
threads = defaultdict(list)
for r in led:
    threads[r["thread_id"]].append(r)
conc = []
for t, rows in threads.items():
    rows.sort(key=lambda r: r["exchange_index"])
    last_by_author = {}
    for r in rows:
        prev = last_by_author.get(r["author"])
        if prev is not None and r["accept_available"]:
            same = (sorted(prev["author_gives"]["properties"]) == sorted(r["author_gives"]["properties"])
                    and sorted(prev["recipient_gives"]["properties"]) == sorted(r["recipient_gives"]["properties"])
                    and prev["author_gives"]["get_out_of_jail_cards"] == r["author_gives"]["get_out_of_jail_cards"]
                    and prev["recipient_gives"]["get_out_of_jail_cards"] == r["recipient_gives"]["get_out_of_jail_cards"])
            delta = r["net_cash_author_to_recipient"] - prev["net_cash_author_to_recipient"]
            if same and delta > 0:
                conc.append((r, delta))
        last_by_author[r["author"]] = r
a = {"concessions": len(conc)}
for cell in ("author_only", "recipient_only", "both", "neither"):
    sub = [(r, d) for r, d in conc if r["completion_cell"] == cell]
    a[cell] = {"n": len(sub), "accepted": sum(r["response"] == "accept_trade" for r, d in sub),
               "countered": sum(r["response"] == "counter_trade" for r, d in sub),
               "rejected": sum(r["response"] == "reject_trade" for r, d in sub),
               "median_concession": st.median(d for r, d in sub) if sub else None,
               "by_recipient": {m: [sum(r["response"] == "accept_trade" for r, d in sub if r["recipient_model"] == m),
                                    sum(r["recipient_model"] == m for r, d in sub)] for m in ("Sol", "Gemini", "Opus", "Grok")},
               "by_recipient_cash_band": {b: [sum(r["response"] == "accept_trade" for r, d in sub if lo <= r["recipient_cash_before"] < hi),
                                              sum(lo <= r["recipient_cash_before"] < hi for r, d in sub)]
                                          for b, lo, hi in (("lt100", -10**9, 100), ("100_299", 100, 300), ("ge300", 300, 10**9))},
               "by_offer_type": {t: [sum(r["response"] == "accept_trade" for r, d in sub if bool(r["author_gives"]["properties"]) == (t == "with_deeds")),
                                     sum(bool(r["author_gives"]["properties"]) == (t == "with_deeds") for r, d in sub)]
                                 for t in ("cash_only_from_author", "with_deeds")}}
res["a_concessions"] = a

# (b) author-only vs recipient-only
b = {}
for stage, rows in (("opening", [r for r in legal if r["opening"]]), ("later", [r for r in legal if not r["opening"]])):
    def rate(rs, cell):
        s = [r for r in rs if r["completion_cell"] == cell]
        return sum(r["response"] == "reject_trade" for r in s), len(s)
    ao, ro = rate(rows, "author_only"), rate(rows, "recipient_only")
    loo = []
    for blk in range(1, 6):
        x, y = rate([r for r in rows if r["block"] != blk], "author_only"), rate([r for r in rows if r["block"] != blk], "recipient_only")
        loo.append(round(100 * (x[0] / x[1] - y[0] / y[1]), 1))
    b[stage] = {"author_only": ao, "recipient_only": ro, "gap": round(100 * (ao[0] / ao[1] - ro[0] / ro[1]), 1), "leave_one_block_out": loo}
res["b_author_vs_recipient_only"] = b

# (c) Sol price cells
sp = json.load(open(SOLP))
res["c_sol_price_rows_fields"] = sorted(sp[0].keys()) if isinstance(sp, list) else list(sp.keys())

# (d) and (e) from Fable pure offers
pure = json.load(open(PURE))
asks = [r for r in pure if r["kind"] == "ask"]
d = {}
for mst in ("unmortgaged", "mortgaged"):
    for miss in (2, 1, 0):
        s = [r["ratio"] for r in asks if r.get("color") and len(r["deeds"]) == 1 and r["mstat"] == mst and r["missing_after"] == miss]
        d[f"{mst}|missing_after_{miss}"] = {"n": len(s), "median": round(st.median(s), 2) if s else None}
res["d_ask_gradient"] = d
groups = defaultdict(lambda: {"completing": [], "other": []})
for r in asks:
    if len(r["deeds"]) != 1:
        continue
    groups[(r["game"], r["seller_model"], r["deeds"][0])]["completing" if r["buyer_completes"] else "other"].append(r)
e = []
for k, v in sorted(groups.items()):
    if v["completing"] and v["other"]:
        c = sorted(v["completing"], key=lambda r: r["decision"])
        o = sorted(v["other"], key=lambda r: r["decision"])
        def cmp(x, y):
            return "higher" if x > y else "lower" if x < y else "equal"
        e.append({"game": k[0], "seller": k[1], "deed": k[2],
                  "completing_asks": [[r["cash"], r["turn"], r["mstat"], r["seller_cash"]] for r in c],
                  "other_asks": [[r["cash"], r["turn"], r["mstat"], r["seller_cash"]] for r in o],
                  "first": cmp(c[0]["cash"], o[0]["cash"]),
                  "median": cmp(st.median(r["cash"] for r in c), st.median(r["cash"] for r in o)),
                  "last": cmp(c[-1]["cash"], o[-1]["cash"]),
                  "all_completing_above_all_other": min(r["cash"] for r in c) > max(r["cash"] for r in o),
                  "same_mortgage_status": {r["mstat"] for r in c} == {r["mstat"] for r in o},
                  "turn_gap": [min(r["turn"] for r in c + o), max(r["turn"] for r in c + o)]})
res["e_same_deed_rows"] = e
res["e_summary"] = {s: dict(Counter(r[s] for r in e)) for s in ("first", "median", "last")}
res["e_summary_same_mortgage_status"] = {s: dict(Counter(r[s] for r in e if r["same_mortgage_status"])) for s in ("first", "median", "last")}
OUT.write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(k, json.dumps(v)[:3000])
