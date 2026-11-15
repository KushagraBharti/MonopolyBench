"""Check 3d. Opening offers by type and completion after removing repeats.

An opening offer is one per thread, but a proposer can reopen the same deed
bundle with the same recipient many times in one game. This keeps the first
opening for each (game, author, recipient, deeds given, deeds asked) and repeats
the swap and cash-bid contrasts, then gives the contrast at the level of
(game, recipient) pairs. Existing-record arithmetic on the frozen Fable ledger.
"""
import json
from collections import defaultdict, Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
led = [r for r in json.load(open(ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json")) if r["accept_available"] and r["opening"]]
led.sort(key=lambda r: (r["game"], r["decision"]))

def typ(r):
    ag, rg = r["author_gives"], r["recipient_gives"]
    if ag["properties"] and rg["properties"]: return "swap"
    if rg["properties"]: return "bid"
    if ag["properties"]: return "offer_to_sell"
    return "no_deeds"

def t(rows):
    n = len(rows); a = sum(r["response"] == "accept_trade" for r in rows); c = sum(r["response"] == "counter_trade" for r in rows)
    return {"n": n, "A": a, "C": c, "R": n - a - c, "reject_pct": round(100 * (n - a - c) / n, 1) if n else None}

seen, first = set(), []
for r in led:
    k = (r["game"], r["author"], r["recipient"], tuple(sorted(r["author_gives"]["properties"])), tuple(sorted(r["recipient_gives"]["properties"])))
    if k not in seen:
        seen.add(k); first.append(r)
res = {"opening_legal": len(led), "first_occurrence_of_bundle": len(first)}
for name, rows in (("all_openings", led), ("first_occurrence", first)):
    res[name] = {ty: {c: t([r for r in rows if typ(r) == ty and r["completion_cell"] == c]) for c in ("neither", "both", "author_only")} for ty in ("swap", "bid")}
    rr = [r for r in rows if r["author_model"] != "Grok"]
    res[name + "_without_grok_authors"] = {ty: {c: t([r for r in rr if typ(r) == ty and r["completion_cell"] == c]) for c in ("neither", "both", "author_only")} for ty in ("swap", "bid")}
    rr = [r for r in rows if "Opus" not in (r["author_model"], r["recipient_model"])]
    res[name + "_without_opus_either_side"] = {ty: {c: t([r for r in rr if typ(r) == ty and r["completion_cell"] == c]) for c in ("neither", "both", "author_only")} for ty in ("swap", "bid")}
# (game, recipient) pairs holding both kinds of opening swap
pairs = defaultdict(lambda: {"author_only": [], "neither": []})
for r in led:
    if typ(r) == "swap" and r["completion_cell"] in ("author_only", "neither"):
        pairs[(r["game"], r["recipient"])][r["completion_cell"]].append(r)
sign = Counter()
for k, v in pairs.items():
    if v["author_only"] and v["neither"]:
        a = t(v["author_only"])["reject_pct"]; b = t(v["neither"])["reject_pct"]
        sign["higher" if a > b else "lower" if a < b else "equal"] += 1
res["game_recipient_pairs_with_both_swap_kinds"] = dict(sign)
# accepted non-completing opening swaps by author, and Grok conflict status is not in this ledger
res["accepted_neither_opening_swaps_by_author"] = dict(Counter(r["author_model"] for r in led if typ(r) == "swap" and r["completion_cell"] == "neither" and r["response"] == "accept_trade"))
res["accepted_neither_opening_swaps_by_recipient"] = dict(Counter(r["recipient_model"] for r in led if typ(r) == "swap" and r["completion_cell"] == "neither" and r["response"] == "accept_trade"))
(HERE.parent / "data/c3d_dedup.json").write_text(json.dumps(res, indent=1))
f = lambda x: f'{x["A"]}/{x["C"]}/{x["R"]} n={x["n"]} rej {x["reject_pct"]}%'
for k, v in res.items():
    if isinstance(v, dict) and "swap" in v:
        print(k)
        for ty in ("swap", "bid"):
            print("   ", ty, " | ".join(f"{c}: {f(x)}" for c, x in v[ty].items() if x["n"]))
    else:
        print(k, v)
