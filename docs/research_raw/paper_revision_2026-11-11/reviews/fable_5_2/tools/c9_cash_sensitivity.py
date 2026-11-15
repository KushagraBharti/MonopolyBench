"""Check 9. Sensitivity of the holder-cash contrast (Fable) to thresholds,
mortgage status of the requested deed, thread position and recipient.

Existing-record arithmetic on the frozen Fable offer ledger.
"""
import json, hashlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"
OUT = HERE.parent / "data/c9_cash_sensitivity.json"
legal = [r for r in json.load(open(LED)) if r["accept_available"]]
ao = [r for r in legal if r["completion_cell"] == "author_only"]


def t(rows):
    n = len(rows); j = sum(r["response"] == "reject_trade" for r in rows)
    return [j, n, round(100 * j / n, 1) if n else None]


res = {"n_completion_requests": len(ao)}
# thresholds
th = {}
for lo in (50, 100, 150, 200):
    for hi in (300, 500):
        for scope, rows in (("all", ao), ("no_opus_holder", [r for r in ao if r["recipient_model"] != "Opus"]),
                            ("no_opus_holder_opening", [r for r in ao if r["recipient_model"] != "Opus" and r["opening"]]),
                            ("no_opus_holder_later", [r for r in ao if r["recipient_model"] != "Opus" and not r["opening"]])):
            th[f"lt{lo}_vs_ge{hi}|{scope}"] = {"low": t([r for r in rows if r["recipient_cash_before"] < lo]),
                                                "high": t([r for r in rows if r["recipient_cash_before"] >= hi])}
res["thresholds"] = th
# quartiles of holder cash among non-Opus holders
no = sorted([r for r in ao if r["recipient_model"] != "Opus"], key=lambda r: r["recipient_cash_before"])
q = len(no) // 4
res["quartiles_no_opus_holder"] = [{"cash_range": [c[0]["recipient_cash_before"], c[-1]["recipient_cash_before"]], "reject": t(c),
                                    "opening_share": round(sum(r["opening"] for r in c) / len(c), 2)}
                                   for c in (no[:q], no[q:2 * q], no[2 * q:3 * q], no[3 * q:])]
# mortgage status of the requested deeds
def mort(r):
    req = set(r["recipient_gives"]["properties"]); m = set(r["recipient_gives_mortgaged"])
    return "mortgaged" if req and req <= m else "unmortgaged" if not (req & m) else "mixed"
ms = {}
for b, lo, hi in (("lt100", -1e9, 100), ("100_299", 100, 300), ("ge300", 300, 1e9)):
    rows = [r for r in ao if lo <= r["recipient_cash_before"] < hi]
    ms[b] = {k: t([r for r in rows if mort(r) == k]) for k in ("unmortgaged", "mortgaged", "mixed")}
    rows = [r for r in rows if r["recipient_model"] != "Opus"]
    ms[b + "|no_opus_holder"] = {k: t([r for r in rows if mort(r) == k]) for k in ("unmortgaged", "mortgaged", "mixed")}
res["by_mortgage_status_of_requested_deeds"] = ms
# recipient x stage x band
rs = {}
for m in ("Sol", "Gemini", "Opus", "Grok"):
    for stage in ("opening", "later"):
        for b, lo, hi in (("lt100", -1e9, 100), ("100_299", 100, 300), ("ge300", 300, 1e9)):
            rs[f"{m}|{stage}|{b}"] = t([r for r in ao if r["recipient_model"] == m and r["opening"] == (stage == "opening") and lo <= r["recipient_cash_before"] < hi])
res["recipient_stage_band"] = rs
# games: sign of low-high gap for non-Opus holders
by_game = defaultdict(lambda: [[], []])
for r in ao:
    if r["recipient_model"] == "Opus":
        continue
    if r["recipient_cash_before"] < 100:
        by_game[r["game"]][0].append(r)
    elif r["recipient_cash_before"] >= 300:
        by_game[r["game"]][1].append(r)
sg = {"both": 0, "lower_when_poor": 0, "higher_when_poor": 0, "equal": 0}
for g, (lo, hi) in by_game.items():
    if lo and hi:
        sg["both"] += 1
        d = t(lo)[2] - t(hi)[2]
        sg["lower_when_poor" if d < 0 else "higher_when_poor" if d > 0 else "equal"] += 1
res["by_game_no_opus_holder"] = sg
# where do completion requests to poor holders come from: distinct holders and games
low = [r for r in ao if r["recipient_cash_before"] < 100]
res["low_cash_requests"] = {"n": len(low), "distinct_game_holder": len({(r["game"], r["recipient"]) for r in low}),
                            "distinct_threads": len({r["thread_id"] for r in low}),
                            "by_holder_model": {m: sum(r["recipient_model"] == m for r in low) for m in ("Sol", "Gemini", "Opus", "Grok")},
                            "top_game_holder_counts": sorted(defaultdict(int, {}).items())}
cnt = defaultdict(int)
for r in low:
    cnt[f'G{r["game"]} {r["recipient_model"]}'] += 1
res["low_cash_requests"]["top_game_holder_counts"] = sorted(cnt.items(), key=lambda kv: -kv[1])[:10]
OUT.write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(k, json.dumps(v)[:2400])
