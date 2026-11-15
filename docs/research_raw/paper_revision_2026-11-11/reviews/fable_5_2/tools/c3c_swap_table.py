"""Check 3c. Opening offers in which the author gives at least one deed
("swaps"), by completion cell, with recipient, author and block cuts.
Existing-record arithmetic on the frozen Fable offer ledger."""
import json, hashlib
from collections import defaultdict, Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
OPU = ROOT / "full_drafts/opus/data/offers_rebuilt.json"
OUT = HERE.parent / "data/c3c_swap_table.json"
led = [r for r in json.load(open(LED)) if r["accept_available"]]
opu = {(r["game"], r["decision"]): r for r in json.load(open(OPU))}

def typ(r):
    ag, rg = r["author_gives"], r["recipient_gives"]
    if ag["properties"] and rg["properties"]:
        return "swap"            # deeds move both ways
    if rg["properties"] and not ag["properties"]:
        return "bid"             # author asks for deeds, gives no deed
    if ag["properties"] and not rg["properties"]:
        return "offer_to_sell"   # author gives deeds, asks for none
    return "no_deeds"

def t(rows):
    n = len(rows)
    a = sum(r["response"] == "accept_trade" for r in rows); c = sum(r["response"] == "counter_trade" for r in rows); j = n - a - c
    return {"n": n, "A": a, "C": c, "R": j, "reject_pct": round(100 * j / n, 1) if n else None}

res = {}
for stage in ("opening", "later"):
    rows = [r for r in led if r["opening"] == (stage == "opening")]
    s = {}
    for ty in ("swap", "bid", "offer_to_sell", "no_deeds"):
        s[ty] = {c: t([r for r in rows if typ(r) == ty and r["completion_cell"] == c]) for c in ("neither", "recipient_only", "both", "author_only")}
    res[stage] = s
op = [r for r in led if r["opening"] and typ(r) == "swap"]
res["opening_swaps_by_recipient"] = {m: {c: t([r for r in op if r["recipient_model"] == m and r["completion_cell"] == c]) for c in ("neither", "recipient_only", "both", "author_only")} for m in ("Sol", "Gemini", "Opus", "Grok")}
res["opening_swaps_by_author"] = {m: {c: t([r for r in op if r["author_model"] == m and r["completion_cell"] == c]) for c in ("neither", "recipient_only", "both", "author_only")} for m in ("Sol", "Gemini", "Opus", "Grok")}
res["opening_swaps_by_block"] = {b: {c: t([r for r in op if r["block"] == b and r["completion_cell"] == c]) for c in ("neither", "both", "author_only")} for b in range(1, 6)}
# net cash direction inside one-sided opening swaps: does the proposer also pay?
ao = [r for r in op if r["completion_cell"] == "author_only"]
ne = [r for r in op if r["completion_cell"] == "neither"]
def cashdir(rows):
    return dict(Counter("author_pays" if r["net_cash_author_to_recipient"] > 0 else "author_receives" if r["net_cash_author_to_recipient"] < 0 else "no_cash" for r in rows))
res["opening_swap_cash_direction"] = {"author_only": cashdir(ao), "neither": cashdir(ne)}
res["opening_swap_reject_by_cash_direction"] = {
    "author_only": {k: t([r for r in ao if ("author_pays" if r["net_cash_author_to_recipient"] > 0 else "author_receives" if r["net_cash_author_to_recipient"] < 0 else "no_cash") == k]) for k in ("author_pays", "no_cash", "author_receives")},
    "neither": {k: t([r for r in ne if ("author_pays" if r["net_cash_author_to_recipient"] > 0 else "author_receives" if r["net_cash_author_to_recipient"] < 0 else "no_cash") == k]) for k in ("author_pays", "no_cash", "author_receives")}}
# Grok conflict-opened threads among opening swaps (inherited conflict list is not in the ledger; use Opus sensitivity file if present)
sens = json.load(open(ROOT / "full_drafts/opus/data/sensitivity.json"))
conf = set(sens.get("grok_conflict_opened_threads") or []) if isinstance(sens.get("grok_conflict_opened_threads"), list) else None
if conf is not None:
    res["opening_swaps_without_grok_conflict_threads"] = {c: t([r for r in op if r["thread_id"] not in conf and r["completion_cell"] == c]) for c in ("neither", "both", "author_only")}
    res["grok_conflict_threads_listed"] = len(conf)
# distinct threads and games behind the swap cells
res["support"] = {c: {"offers": len([r for r in op if r["completion_cell"] == c]), "games": len({r["game"] for r in op if r["completion_cell"] == c}),
                      "game_recipient_pairs": len({(r["game"], r["recipient"]) for r in op if r["completion_cell"] == c})} for c in ("neither", "both", "author_only")}
# by game sign
bg = defaultdict(lambda: [[], []])
for r in op:
    if r["completion_cell"] == "author_only": bg[r["game"]][0].append(r)
    if r["completion_cell"] == "neither": bg[r["game"]][1].append(r)
sg = Counter()
for g, (x, y) in bg.items():
    if x and y:
        d = t(x)["reject_pct"] - t(y)["reject_pct"]
        sg["positive" if d > 0 else "negative" if d < 0 else "zero"] += 1
res["opening_swaps_by_game_sign"] = dict(sg)
OUT.write_text(json.dumps(res, indent=1))
f = lambda x: f'{x["A"]}/{x["C"]}/{x["R"]} n={x["n"]} rej {x["reject_pct"]}%' if x["n"] else "-"
for stage in ("opening", "later"):
    print("==", stage)
    for ty, s in res[stage].items():
        print(f"  {ty:14s}", " | ".join(f"{c}: {f(v)}" for c, v in s.items()))
for k in ("opening_swaps_by_recipient", "opening_swaps_by_author", "opening_swaps_by_block"):
    print("==", k)
    for m, s in res[k].items():
        print(f"  {m!s:8s}", " | ".join(f"{c}: {f(v)}" for c, v in s.items()))
for k in ("opening_swap_cash_direction", "opening_swap_reject_by_cash_direction", "support", "opening_swaps_by_game_sign", "grok_conflict_threads_listed", "opening_swaps_without_grok_conflict_threads"):
    if k in res: print(k, json.dumps(res[k]))
