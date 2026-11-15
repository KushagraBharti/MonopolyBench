"""Check 3. Opus's opening contrast under a like-for-like baseline and a price control.

Existing-record arithmetic on the frozen offer ledgers.

(a) Opus compares opening offers that complete only the author's group with all
    opening offers that complete nobody. Every author-completing offer asks the
    recipient for a deed. The neither population also holds offers to sell a deed
    to the recipient. This splits the baseline.
(b) For pure cash bids (the author pays cash and receives deeds, nothing else),
    rejection by whether the deed would complete the bidder, inside bands of
    cash / list price and by mortgage status, so the contrast can be read at a
    comparable price.
(c) The capacity cut behind "categorical, not graded", by recipient.
"""
import json
import hashlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
PURE = ROOT / "full_drafts/fable_5_2/data/a6_pure_offers.json"
OPU = ROOT / "full_drafts/opus/data/offers_rebuilt.json"
OPRICE = ROOT / "full_drafts/opus/data/pricing.json"
OUT = HERE.parent / "data/c3_defensive_contrast.json"
BOARD = json.load(open(ROOT.parents[2] / "contracts/data/board.json"))

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
led = json.load(open(LED))
pure = json.load(open(PURE))
opu = {(r["game"], r["decision"]): r for r in json.load(open(OPU))}
legal = [r for r in led if r["accept_available"]]


def tab(rows):
    n = len(rows)
    j = sum(r["response"] == "reject_trade" for r in rows)
    a = sum(r["response"] == "accept_trade" for r in rows)
    return {"n": n, "reject": j, "accept": a, "reject_pct": round(100 * j / n, 1) if n else None}


def gap(a, b):
    return round(a["reject_pct"] - b["reject_pct"], 1) if a["n"] and b["n"] else None


res = {"inputs": {str(p.relative_to(ROOT)): sha(p) for p in (LED, PURE, OPU, OPRICE)}}

# ---------------------------------------------------------------- (a)
op = [r for r in legal if r["opening"]]
ao = [r for r in op if r["completion_cell"] == "author_only"]
ne = [r for r in op if r["completion_cell"] == "neither"]
ne_req = [r for r in ne if r["recipient_gives"]["properties"]]
ne_sell = [r for r in ne if not r["recipient_gives"]["properties"]]
a = {
    "author_only": tab(ao), "neither_all": tab(ne),
    "neither_asks_recipient_for_deed": tab(ne_req),
    "neither_no_deed_asked": tab(ne_sell),
}
a["gap_vs_all"] = gap(a["author_only"], a["neither_all"])
a["gap_vs_like_for_like"] = gap(a["author_only"], a["neither_asks_recipient_for_deed"])
a["by_block"] = {}
for b in range(1, 6):
    x, y = tab([r for r in ao if r["block"] == b]), tab([r for r in ne_req if r["block"] == b])
    a["by_block"][b] = {"author_only": x, "neither_asks_deed": y, "gap": gap(x, y)}
a["leave_one_block_out"] = {}
for b in range(1, 6):
    x, y = tab([r for r in ao if r["block"] != b]), tab([r for r in ne_req if r["block"] != b])
    a["leave_one_block_out"][b] = gap(x, y)
a["by_recipient"] = {}
for m in ("Sol", "Gemini", "Opus", "Grok"):
    x, y = tab([r for r in ao if r["recipient_model"] == m]), tab([r for r in ne_req if r["recipient_model"] == m])
    a["by_recipient"][m] = {"author_only": x, "neither_asks_deed": y, "gap": gap(x, y)}
x = tab([r for r in ao if "Opus" not in (r["recipient_model"], r["author_model"])])
y = tab([r for r in ne_req if "Opus" not in (r["recipient_model"], r["author_model"])])
a["without_opus_either_side"] = {"author_only": x, "neither_asks_deed": y, "gap": gap(x, y)}
x = tab([r for r in ao if r["recipient_model"] != "Opus"])
y = tab([r for r in ne_req if r["recipient_model"] != "Opus"])
a["without_opus_recipient"] = {"author_only": x, "neither_asks_deed": y, "gap": gap(x, y)}
# by game: sign of the gap in games with both kinds
by_game = defaultdict(lambda: [[], []])
for r in ao:
    by_game[r["game"]][0].append(r)
for r in ne_req:
    by_game[r["game"]][1].append(r)
signs = {"positive": 0, "negative": 0, "zero": 0, "games_with_both": 0}
for g, (x, y) in by_game.items():
    if x and y:
        signs["games_with_both"] += 1
        d = tab(x)["reject_pct"] - tab(y)["reject_pct"]
        signs["positive" if d > 0 else "negative" if d < 0 else "zero"] += 1
a["by_game_sign"] = signs
res["a_opening_contrast"] = a

# ---------------------------------------------------------------- (b)
bids = [r for r in pure if r["kind"] == "bid"]


def rband(x):
    return "lt1" if x < 1 else "1_to_2" if x < 2 else "ge2"


b = {"n_bids": len(bids)}
for scope, rows in (("opening", [r for r in bids if r["opening"]]), ("all", bids)):
    s = {}
    for comp in (True, False):
        sub = [r for r in rows if r["buyer_completes"] == comp]
        s["completes_bidder" if comp else "other"] = {
            "all": tab(sub),
            "by_ratio": {k: tab([r for r in sub if rband(r["ratio"]) == k]) for k in ("lt1", "1_to_2", "ge2")},
            "by_mortgage": {k: tab([r for r in sub if r["mstat"] == k]) for k in sorted({r["mstat"] for r in rows})},
            "by_seller_model": {m: tab([r for r in sub if r["seller_model"] == m]) for m in ("Sol", "Gemini", "Opus", "Grok")},
            "by_seller_model_ratio": {f"{m}|{k}": tab([r for r in sub if r["seller_model"] == m and rband(r["ratio"]) == k])
                                      for m in ("Sol", "Gemini", "Opus", "Grok") for k in ("lt1", "1_to_2", "ge2")},
            "unmortgaged_by_ratio": {k: tab([r for r in sub if r["mstat"] == "unmortgaged" and rband(r["ratio"]) == k]) for k in ("lt1", "1_to_2", "ge2")},
            "unmortgaged_no_opus_seller_by_ratio": {k: tab([r for r in sub if r["mstat"] == "unmortgaged" and r["seller_model"] != "Opus" and rband(r["ratio"]) == k]) for k in ("lt1", "1_to_2", "ge2")},
            "no_opus_seller_by_ratio": {k: tab([r for r in sub if r["seller_model"] != "Opus" and rband(r["ratio"]) == k]) for k in ("lt1", "1_to_2", "ge2")},
            "by_bidder_model": {m: tab([r for r in sub if r["buyer_model"] == m]) for m in ("Sol", "Gemini", "Opus", "Grok")},
        }
    b[scope] = s
res["b_pure_cash_bids"] = b

# ---------------------------------------------------------------- (c)
house = BOARD["house_cost_by_group"]
group_of = {s.get("key") or s["name"].upper().replace(" ", "_").replace(".", ""): s.get("group") for s in BOARD["spaces"] if s.get("group")}
size = defaultdict(int)
for k, g in group_of.items():
    size[g] += 1


def capacity(r):
    g = r["author_new_groups"][0]
    cash_after = r["author_cash_before"] - r["author_gives"]["cash"] + r["recipient_gives"]["cash"] - r.get("author_interest_if_accepted", 0)
    hc = house[g]
    if cash_after >= hc * size[g]:
        return "full_layer"
    if cash_after >= hc:
        return "one_house"
    return "less"


c = {}
ao_all = [r for r in legal if r["completion_cell"] == "author_only"]
for scope, rows in (("opening", [r for r in ao_all if r["opening"]]), ("later", [r for r in ao_all if not r["opening"]])):
    c[scope] = {"pooled": {k: tab([r for r in rows if capacity(r) == k]) for k in ("full_layer", "one_house", "less")}}
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        c[scope][m] = {k: tab([r for r in rows if capacity(r) == k and r["recipient_model"] == m]) for k in ("full_layer", "one_house", "less")}
res["c_capacity_cut"] = c

OUT.write_text(json.dumps(res, indent=1))


def s(t):
    return f'{t["reject"]}/{t["n"]} ({t["reject_pct"]}%)' if t["n"] else "-"


print("(a) opening:", {k: s(v) for k, v in a.items() if isinstance(v, dict) and "n" in v})
print("    gap vs all neither", a["gap_vs_all"], "| like for like", a["gap_vs_like_for_like"])
for k, v in a["by_block"].items():
    print("    block", k, s(v["author_only"]), s(v["neither_asks_deed"]), v["gap"])
print("    leave one block out", a["leave_one_block_out"])
for k, v in a["by_recipient"].items():
    print("    recipient", k, s(v["author_only"]), s(v["neither_asks_deed"]), v["gap"])
print("    without Opus either side", s(a["without_opus_either_side"]["author_only"]), s(a["without_opus_either_side"]["neither_asks_deed"]), a["without_opus_either_side"]["gap"])
print("    without Opus recipient", s(a["without_opus_recipient"]["author_only"]), s(a["without_opus_recipient"]["neither_asks_deed"]), a["without_opus_recipient"]["gap"])
print("    by game", a["by_game_sign"])
for scope in ("opening", "all"):
    print(f"(b) pure cash bids, {scope}")
    for key in ("all",):
        print("   all:", s(b[scope]["completes_bidder"]["all"]), "vs", s(b[scope]["other"]["all"]))
    for sub in ("by_ratio", "by_mortgage", "unmortgaged_by_ratio", "no_opus_seller_by_ratio", "unmortgaged_no_opus_seller_by_ratio", "by_seller_model", "by_bidder_model", "by_seller_model_ratio"):
        print("  ", sub)
        for k in b[scope]["completes_bidder"][sub]:
            print(f'      {k:16s} completes {s(b[scope]["completes_bidder"][sub][k]):18s} other {s(b[scope]["other"][sub][k])}')
print("(c) capacity")
for scope in c:
    for m, v in c[scope].items():
        print("  ", scope, m, {k: s(t) for k, t in v.items()})
