"""Check 2. The refusal-to-sale pairs behind "13 of 14".

Existing-record arithmetic on the frozen Fable pair ledger and offer ledger.
For each one-sided sale that followed an earlier refusal by the same holder,
print the terms the holder first declined beside the terms that settled, so
that "cash fell" can be read against "price rose". Also gives the base rate
of falling holder cash in multi-turn pairs that never settled, and who put
the deed on the market when the holder was short of cash.
"""
import json
import hashlib
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DY = ROOT / "full_drafts/fable_5_2/data/a6_dyads.json"
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
OPU = ROOT / "full_drafts/opus/data/offers_rebuilt.json"
OUT = HERE.parent / "data/c2_refusal_to_sale.json"

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
dy = json.load(open(DY))
led = {(r["game"], r["decision"]): r for r in json.load(open(LED))}
opu = {(r["game"], r["decision"]): r for r in json.load(open(OPU))}

BOARD = json.load(open(ROOT.parents[2] / "contracts/data/board.json"))


def find_spaces(b):
    if isinstance(b, dict):
        for k in ("spaces", "board", "tiles"):
            if k in b:
                return b[k]
    return b


import re

price = {}
for s in find_spaces(BOARD):
    if isinstance(s, dict) and s.get("price") is not None:
        # same key rule the saved prompts use: non-alphanumerics to underscores, upper case
        price[re.sub(r"[^A-Za-z0-9]+", "_", s["name"].strip()).strip("_").upper()] = s["price"]


def holder_side(row, holder):
    """Deeds and net cash moving from/to the holder under this offer."""
    if row["author"] == holder:
        gives, gets = row["author_gives"], row["recipient_gives"]
    else:
        gives, gets = row["recipient_gives"], row["author_gives"]
    return {
        "holder_gives_deeds": sorted(gives["properties"]),
        "holder_gets_deeds": sorted(gets["properties"]),
        "net_cash_to_holder": gets["cash"] - gives["cash"],
    }


rows14 = []
for d in dy:
    if not (d["settled"] and d.get("one_sided") and d.get("holder_declined_on_earlier_turn")):
        continue
    g, holder = d["game"], d["holder"]
    # first request written by the completer that the holder declined on an earlier turn
    first = None
    for r in d["requests"]:
        if r["written_by"] == "completer" and r["response"] in ("reject_trade", "counter_trade") and r["turn"] < d["settle_turn"]:
            first = r
            break
    sale = led[(g, d["settle_decision"])]
    f_row = led[(g, first["decision"])]
    fs, ss = holder_side(f_row, holder), holder_side(sale, holder)
    same_bundle = fs["holder_gives_deeds"] == ss["holder_gives_deeds"] and fs["holder_gets_deeds"] == ss["holder_gets_deeds"]
    list_first = sum(price.get(k, 0) for k in fs["holder_gives_deeds"])
    list_sale = sum(price.get(k, 0) for k in ss["holder_gives_deeds"])
    thread_init = opu[(g, d["settle_decision"])]["initiator"]
    rows14.append({
        "game": g, "group": d["group"], "holder": d["holder_model"], "buyer": d["completer_model"],
        "first_decline_turn": first["turn"], "first_decline_response": first["response"],
        "holder_cash_at_first_decline": first["holder_cash"],
        "declined_net_cash_to_holder": fs["net_cash_to_holder"],
        "declined_holder_gives": fs["holder_gives_deeds"], "declined_holder_gets": fs["holder_gets_deeds"],
        "sale_turn": d["settle_turn"], "holder_cash_at_sale": d["settle_holder_cash"],
        "sale_net_cash_to_holder": ss["net_cash_to_holder"],
        "sale_holder_gives": ss["holder_gives_deeds"], "sale_holder_gets": ss["holder_gets_deeds"],
        "same_deed_bundle": same_bundle,
        "list_price_declined_bundle": list_first, "list_price_sale_bundle": list_sale,
        "cash_fell": d["settle_holder_cash"] < first["holder_cash"],
        "price_vs_declined": ("higher" if ss["net_cash_to_holder"] > fs["net_cash_to_holder"] else
                              "lower" if ss["net_cash_to_holder"] < fs["net_cash_to_holder"] else "equal"),
        "sale_offer_written_by": "holder" if sale["author"] == holder else "buyer",
        "sale_thread_opened_by": "holder" if thread_init == holder else "buyer",
        "holder_cash_under_100_at_sale": d["settle_holder_cash"] < 100,
    })

rows14.sort(key=lambda r: (r["game"], r["group"]))

# base rate: multi-turn pairs that never settled
uns = [d for d in dy if not d["settled"] and d["first_turn"] != d["last_turn"]]
dirs = Counter("lower" if d["last_holder_cash"] < d["first_holder_cash"] else
               "higher" if d["last_holder_cash"] > d["first_holder_cash"] else "equal" for d in uns)
# among unsettled multi-turn pairs whose first request was declined by the holder while holding >= 300
uns_rich = [d for d in uns if d["first_holder_cash"] >= 300]
dirs_rich = Counter("lower" if d["last_holder_cash"] < d["first_holder_cash"] else
                    "higher" if d["last_holder_cash"] > d["first_holder_cash"] else "equal" for d in uns_rich)

# unsettled pairs in which the holder at some point held under $100 while a request was live
uns_low = [d for d in dy if not d["settled"] and d["min_holder_cash"] < 100]

# who opens the thread in which a completion request reaches the holder, by holder cash band
legal = [r for r in led.values() if r["accept_available"] and r["completion_cell"] == "author_only"]


def band(c):
    return "lt100" if c < 100 else "100_299" if c < 300 else "ge300"


init = defaultdict(Counter)
init_by_model = defaultdict(Counter)
for r in legal:
    o = opu[(r["game"], r["decision"])]
    who = "holder_opened_thread" if o["initiator"] == r["recipient"] else "buyer_opened_thread"
    init[band(r["recipient_cash_before"])][who] += 1
    init_by_model[(r["recipient_model"], band(r["recipient_cash_before"]))][who] += 1

# rejection of completion requests by who opened the thread and holder cash
rej = defaultdict(lambda: [0, 0])
for r in legal:
    o = opu[(r["game"], r["decision"])]
    who = "holder_opened" if o["initiator"] == r["recipient"] else "buyer_opened"
    k = f'{who}|{band(r["recipient_cash_before"])}'
    rej[k][1] += 1
    rej[k][0] += r["response"] == "reject_trade"
rej_no_opus = defaultdict(lambda: [0, 0])
for r in legal:
    if r["recipient_model"] == "Opus":
        continue
    o = opu[(r["game"], r["decision"])]
    who = "holder_opened" if o["initiator"] == r["recipient"] else "buyer_opened"
    k = f'{who}|{band(r["recipient_cash_before"])}'
    rej_no_opus[k][1] += 1
    rej_no_opus[k][0] += r["response"] == "reject_trade"

# one-sided sales: holder cash bands and who opened the settling thread
one = [d for d in dy if d["settled"] and d.get("one_sided")]
sale_bands = Counter(band(d["settle_holder_cash"]) for d in one)
sale_open = defaultdict(Counter)
for d in one:
    o = opu[(d["game"], d["settle_decision"])]
    sale_open[band(d["settle_holder_cash"])]["holder" if o["initiator"] == d["holder"] else "buyer"] += 1
sale_bands_no_opus = Counter(band(d["settle_holder_cash"]) for d in one if d["holder_model"] != "Opus")
sale_by_holder = defaultdict(Counter)
for d in one:
    sale_by_holder[d["holder_model"]][band(d["settle_holder_cash"])] += 1

res = {
    "inputs": {str(p.relative_to(ROOT)): sha(p) for p in (DY, LED, OPU)},
    "rows": rows14,
    "summary": {
        "n": len(rows14),
        "cash_fell": sum(r["cash_fell"] for r in rows14),
        "price_vs_declined": dict(Counter(r["price_vs_declined"] for r in rows14)),
        "same_deed_bundle": sum(r["same_deed_bundle"] for r in rows14),
        "same_bundle_price_vs_declined": dict(Counter(r["price_vs_declined"] for r in rows14 if r["same_deed_bundle"])),
        "cash_fell_and_price_not_higher": sum(r["cash_fell"] and r["price_vs_declined"] != "higher" for r in rows14),
        "holder_under_100_at_sale": sum(r["holder_cash_under_100_at_sale"] for r in rows14),
        "sale_offer_written_by": dict(Counter(r["sale_offer_written_by"] for r in rows14)),
        "sale_thread_opened_by": dict(Counter(r["sale_thread_opened_by"] for r in rows14)),
        "median_declined_cash_terms": st.median(r["declined_net_cash_to_holder"] for r in rows14),
        "median_sale_cash_terms": st.median(r["sale_net_cash_to_holder"] for r in rows14),
    },
    "unsettled_multi_turn_pairs": {
        "n": len(uns), "holder_cash_direction_first_to_last": dict(dirs),
        "n_first_cash_ge300": len(uns_rich), "direction_first_cash_ge300": dict(dirs_rich),
        "median_first": st.median(d["first_holder_cash"] for d in uns),
        "median_last": st.median(d["last_holder_cash"] for d in uns),
    },
    "unsettled_pairs_with_holder_under_100_at_some_request": len(uns_low),
    "unsettled_pairs_total": sum(not d["settled"] for d in dy),
    "completion_requests_thread_opener_by_holder_cash": {k: dict(v) for k, v in init.items()},
    "completion_requests_thread_opener_by_holder_model_cash": {str(k): dict(v) for k, v in sorted(init_by_model.items())},
    "completion_request_rejection_by_opener_and_cash": {k: v for k, v in sorted(rej.items())},
    "completion_request_rejection_by_opener_and_cash_no_opus_holder": {k: v for k, v in sorted(rej_no_opus.items())},
    "one_sided_sales_by_holder_cash_band": dict(sale_bands),
    "one_sided_sales_by_holder_cash_band_no_opus_holder": dict(sale_bands_no_opus),
    "one_sided_sales_by_holder_model_and_band": {k: dict(v) for k, v in sale_by_holder.items()},
    "one_sided_sales_settling_thread_opened_by": {k: dict(v) for k, v in sale_open.items()},
}
OUT.write_text(json.dumps(res, indent=1))

print(json.dumps(res["summary"], indent=1))
for r in rows14:
    print(f'G{r["game"]:<2} {r["group"]:<10} {r["holder"]:>6}->{r["buyer"]:<6} '
          f'declined t{r["first_decline_turn"]:<3} cash ${r["holder_cash_at_first_decline"]:<5} terms {r["declined_net_cash_to_holder"]:>5} '
          f'| sale t{r["sale_turn"]:<3} cash ${r["holder_cash_at_sale"]:<5} terms {r["sale_net_cash_to_holder"]:>5} '
          f'| same bundle {str(r["same_deed_bundle"]):5} price {r["price_vs_declined"]:6} written by {r["sale_offer_written_by"]:6} thread by {r["sale_thread_opened_by"]}')
for k in ("unsettled_multi_turn_pairs", "unsettled_pairs_with_holder_under_100_at_some_request", "unsettled_pairs_total",
          "completion_requests_thread_opener_by_holder_cash", "completion_request_rejection_by_opener_and_cash",
          "completion_request_rejection_by_opener_and_cash_no_opus_holder",
          "one_sided_sales_by_holder_cash_band", "one_sided_sales_by_holder_cash_band_no_opus_holder",
          "one_sided_sales_by_holder_model_and_band", "one_sided_sales_settling_thread_opened_by"):
    print(k, json.dumps(res[k]))
