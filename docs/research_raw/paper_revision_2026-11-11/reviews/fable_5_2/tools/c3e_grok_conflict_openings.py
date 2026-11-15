"""Check 3e. Opening contrasts without threads opened by a Grok call whose
assistant text names a different action.

Read-only. For each opening offer written by Grok, the proposing decision is
the decision immediately before the first response in the thread. Its selected
attempt's assistant text is parsed with one regular expression for an action
name (the rule used in the frozen Fable draft). A thread is conflict-opened if
that name differs from the applied propose_trade call.
"""
import json, re, glob, hashlib
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPO = ROOT.parents[2]
NAME_RE = re.compile(r'"name"\s*:\s*"([a-z_]+)"')
led = [r for r in json.load(open(ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"))]
games = {}
for c in ("railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26"):
    for g in sorted((REPO / "saved_games" / c).glob("game-[0-9][0-9]-*")):
        games[int(g.name.split("-")[1])] = g / "run"
need = {}
for r in led:
    if r["opening"] and r["author_model"] == "Grok":
        need.setdefault(r["game"], []).append(r)
conflict_threads, named_threads, checked = set(), set(), 0
for gno, rows in need.items():
    order, resolved, started = [], {}, {}
    for line in open(games[gno] / "decisions.jsonl"):
        d = json.loads(line)
        if d["phase"] == "decision_started":
            order.append(d["decision_id"]); started[d["decision_id"]] = d
        else:
            resolved[d["decision_id"]] = d
    for r in rows:
        k = r["decision"] - 1
        # walk back to the author's proposing decision
        while k >= 0 and not (started[order[k]]["player_id"] == r["author"] and resolved[order[k]]["final_action"]["action"] == "propose_trade"):
            k -= 1
        assert k >= 0 and r["decision"] - k <= 2, (gno, r["decision"], k)
        res = resolved[order[k]]
        sel = res["attempts"][-1]
        content = sel.get("assistant_content")
        if content is None:
            try:
                content = sel["raw_response"]["choices"][0]["message"].get("content")
            except Exception:
                content = None
        checked += 1
        if content:
            m = NAME_RE.search(content)
            if m:
                named_threads.add(r["thread_id"])
                if m.group(1) != "propose_trade":
                    conflict_threads.add(r["thread_id"])

def typ(r):
    ag, rg = r["author_gives"], r["recipient_gives"]
    if ag["properties"] and rg["properties"]: return "swap"
    if rg["properties"]: return "bid"
    if ag["properties"]: return "offer_to_sell"
    return "no_deeds"

def t(rows):
    n = len(rows); a = sum(r["response"] == "accept_trade" for r in rows); c = sum(r["response"] == "counter_trade" for r in rows)
    return {"n": n, "A": a, "C": c, "R": n - a - c, "reject_pct": round(100 * (n - a - c) / n, 1) if n else None}

op = [r for r in led if r["opening"] and r["accept_available"]]
keep = [r for r in op if r["thread_id"] not in conflict_threads]
res = {
    "grok_openings_checked": checked, "grok_openings_with_named_text": len(named_threads),
    "conflict_opened_threads": len(conflict_threads),
    "conflict_opened_threads_settled": len({r["thread_id"] for r in led if r["thread_id"] in conflict_threads and r["response"] == "accept_trade"}),
    "accepted_neither_opening_swaps_grok_authored": sum(1 for r in op if typ(r) == "swap" and r["completion_cell"] == "neither" and r["response"] == "accept_trade" and r["author_model"] == "Grok"),
    "of_which_conflict_opened": sum(1 for r in op if typ(r) == "swap" and r["completion_cell"] == "neither" and r["response"] == "accept_trade" and r["author_model"] == "Grok" and r["thread_id"] in conflict_threads),
    "opening_without_conflict_threads": {ty: {c: t([r for r in keep if typ(r) == ty and r["completion_cell"] == c]) for c in ("neither", "both", "author_only")} for ty in ("swap", "bid")},
    "opening_all_author_only_vs_neither_without_conflict_threads": {c: t([r for r in keep if r["completion_cell"] == c]) for c in ("author_only", "neither")},
    "conflict_opened_by_type_and_cell": dict(Counter(f'{typ(r)}|{r["completion_cell"]}' for r in op if r["thread_id"] in conflict_threads)),
}
(HERE.parent / "data/c3e_grok_conflict_openings.json").write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(k, json.dumps(v))

# by block and recipient, swaps only, without conflict-opened threads
sw = [r for r in keep if typ(r) == "swap"]
extra = {
    "swap_by_block": {b: {c: t([r for r in sw if r["block"] == b and r["completion_cell"] == c]) for c in ("neither", "author_only")} for b in range(1, 6)},
    "swap_by_recipient": {m: {c: t([r for r in sw if r["recipient_model"] == m and r["completion_cell"] == c]) for c in ("neither", "author_only")} for m in ("Sol", "Gemini", "Opus", "Grok")},
    "bid_by_block": {b: {c: t([r for r in keep if typ(r) == "bid" and r["block"] == b and r["completion_cell"] == c]) for c in ("neither", "author_only")} for b in range(1, 6)},
}
res["without_conflict_threads_cuts"] = extra
(HERE.parent / "data/c3e_grok_conflict_openings.json").write_text(json.dumps(res, indent=1))
for k, v in extra.items():
    print(k)
    for kk, vv in v.items():
        print("   ", kk, {c: f'{x["R"]}/{x["n"]} ({x["reject_pct"]}%)' for c, x in vv.items()})
