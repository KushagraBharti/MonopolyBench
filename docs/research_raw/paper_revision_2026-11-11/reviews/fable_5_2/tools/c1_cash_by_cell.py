"""Check 1. Rejection by holder (recipient) cash and completion cell.

Existing-record arithmetic only. Reads two independently rebuilt offer ledgers
from the frozen drafts (Fable a2 and Opus offers_rebuilt), confirms they agree
on the fields used, then tabulates rejection by recipient cash band and
completion cell, cut by recipient, thread position and seed block.

No engine import, no model call, no replay.
"""
import json
import hashlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # paper_revision_2026-11-11
FAB = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
OPU = ROOT / "full_drafts/opus/data/offers_rebuilt.json"
OUT = HERE.parent / "data/c1_cash_by_cell.json"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


fab = json.load(open(FAB))
opu = json.load(open(OPU))

# --- cross-ledger agreement on the fields this check uses -------------------
ok = {(r["game"], r["decision"]): r for r in opu}
cellmap = {"Author only": "author_only", "Recipient only": "recipient_only",
           "Both": "both", "Neither": "neither"}
mismatch = []
for r in fab:
    o = ok.get((r["game"], r["decision"]))
    if o is None:
        mismatch.append(("missing", r["game"], r["decision"]))
        continue
    oc = cellmap.get(o["cell"], o["cell"].lower().replace(" ", "_"))
    for name, a, b in [
        ("cell", r["completion_cell"], oc),
        ("response", r["response"], o["response"]),
        ("recipient_cash", r["recipient_cash_before"], o["recipient_cash"]),
        ("author_cash", r["author_cash_before"], o["author_cash"]),
        ("opening", r["opening"], o["opening"]),
        ("recipient_model", r["recipient_model"], o["recipient_model"]),
        ("accept", r["accept_available"], o["accept_legal"]),
    ]:
        if a != b:
            mismatch.append((name, r["game"], r["decision"], a, b))

legal = [r for r in fab if r["accept_available"]]


def band(c):
    if c < 100:
        return "lt100"
    if c < 300:
        return "100_299"
    return "ge300"


def requests_deed(r):
    """The author asks the recipient for at least one deed."""
    return len(r["recipient_gives"]["properties"]) > 0


def tab(rows):
    n = len(rows)
    a = sum(r["response"] == "accept_trade" for r in rows)
    c = sum(r["response"] == "counter_trade" for r in rows)
    j = sum(r["response"] == "reject_trade" for r in rows)
    return {"n": n, "accept": a, "counter": c, "reject": j,
            "reject_pct": round(100 * j / n, 1) if n else None}


def cut(rows, key):
    d = defaultdict(list)
    for r in rows:
        d[key(r)].append(r)
    return {str(k): tab(v) for k, v in sorted(d.items(), key=lambda kv: str(kv[0]))}


res = {
    "inputs": {str(FAB.relative_to(ROOT)): sha(FAB), str(OPU.relative_to(ROOT)): sha(OPU)},
    "ledger_rows": len(fab),
    "cross_ledger_mismatches": mismatch,
    "legal_offers": len(legal),
}

# Populations. "author_only" is a completion request. Comparison populations:
#  neither_all        : every neither-completing legal offer (Opus's baseline)
#  neither_asks_deed  : neither-completing offers that ask the recipient for a deed
pops = {
    "author_only": [r for r in legal if r["completion_cell"] == "author_only"],
    "neither_all": [r for r in legal if r["completion_cell"] == "neither"],
    "neither_asks_deed": [r for r in legal if r["completion_cell"] == "neither" and requests_deed(r)],
    "recipient_only": [r for r in legal if r["completion_cell"] == "recipient_only"],
    "both": [r for r in legal if r["completion_cell"] == "both"],
}
res["population_sizes"] = {k: len(v) for k, v in pops.items()}
res["author_only_asks_deed"] = sum(requests_deed(r) for r in pops["author_only"])

by = {}
for name, rows in pops.items():
    by[name] = {
        "all": tab(rows),
        "by_band": cut(rows, lambda r: band(r["recipient_cash_before"])),
        "by_band_opening": cut([r for r in rows if r["opening"]], lambda r: band(r["recipient_cash_before"])),
        "by_band_later": cut([r for r in rows if not r["opening"]], lambda r: band(r["recipient_cash_before"])),
        "by_recipient_band": cut(rows, lambda r: (r["recipient_model"], band(r["recipient_cash_before"]))),
        "by_recipient_opening_band": cut(rows, lambda r: (r["recipient_model"], "opening" if r["opening"] else "later", band(r["recipient_cash_before"]))),
        "by_block_band": cut(rows, lambda r: (r["block"], band(r["recipient_cash_before"]))),
        "no_opus_recipient_by_band": cut([r for r in rows if r["recipient_model"] != "Opus"], lambda r: band(r["recipient_cash_before"])),
        "no_opus_either_by_band": cut([r for r in rows if "Opus" not in (r["recipient_model"], r["author_model"])], lambda r: band(r["recipient_cash_before"])),
        "no_opus_recipient_opening_by_band": cut([r for r in rows if r["recipient_model"] != "Opus" and r["opening"]], lambda r: band(r["recipient_cash_before"])),
        "no_opus_recipient_later_by_band": cut([r for r in rows if r["recipient_model"] != "Opus" and not r["opening"]], lambda r: band(r["recipient_cash_before"])),
    }
res["tables"] = by


# The defensive gap (author_only minus neither) inside each cash band.
def gap(a, b):
    if not a or not b or not a["n"] or not b["n"]:
        return None
    return round(a["reject_pct"] - b["reject_pct"], 1)


gaps = {}
for base in ("neither_all", "neither_asks_deed"):
    g = {}
    for scope in ("by_band", "by_band_opening", "by_band_later", "no_opus_recipient_by_band",
                  "no_opus_either_by_band", "no_opus_recipient_opening_by_band",
                  "no_opus_recipient_later_by_band"):
        g[scope] = {}
        for b in ("lt100", "100_299", "ge300"):
            a = by["author_only"][scope].get(b)
            n = by[base][scope].get(b)
            g[scope][b] = {"author_only": a, base: n, "gap_points": gap(a, n)}
    # by recipient
    g["by_recipient_band"] = {}
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        for b in ("lt100", "100_299", "ge300"):
            k = str((m, b))
            a = by["author_only"]["by_recipient_band"].get(k)
            n = by[base]["by_recipient_band"].get(k)
            g["by_recipient_band"][f"{m}|{b}"] = {"author_only": a, base: n, "gap_points": gap(a, n)}
    g["by_block_band"] = {}
    for blk in range(1, 6):
        for b in ("lt100", "ge300"):
            k = str((blk, b))
            a = by["author_only"]["by_block_band"].get(k)
            n = by[base]["by_block_band"].get(k)
            g["by_block_band"][f"{blk}|{b}"] = {"author_only": a, base: n, "gap_points": gap(a, n)}
    gaps[base] = g
res["defensive_gap_within_cash_band"] = gaps

# Opus's opening contrast, reproduced, then inside cash bands.
op = [r for r in legal if r["opening"]]
res["opening_contrast"] = {
    "author_only": tab([r for r in op if r["completion_cell"] == "author_only"]),
    "neither": tab([r for r in op if r["completion_cell"] == "neither"]),
}

# How much of the recipient-cash association is recipient identity?
res["band_share_by_recipient_author_only"] = cut(
    pops["author_only"], lambda r: (band(r["recipient_cash_before"]), r["recipient_model"]))

OUT.write_text(json.dumps(res, indent=1))


def show(t):
    return f'{t["reject"]}/{t["n"]} ({t["reject_pct"]}%)' if t and t["n"] else "-"


print("cross-ledger mismatches:", len(mismatch))
print("population sizes:", res["population_sizes"], "author_only asking a deed:", res["author_only_asks_deed"])
print("opening contrast:", show(res["opening_contrast"]["author_only"]), "vs", show(res["opening_contrast"]["neither"]))
for base in ("neither_all", "neither_asks_deed"):
    print("\n=== baseline", base)
    for scope, g in gaps[base].items():
        print(" ", scope)
        for k, v in g.items():
            print(f"    {k:18s} author_only {show(v['author_only']):18s} base {show(v[base]):18s} gap {v['gap_points']}")
