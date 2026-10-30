"""Test: for Grok's content/tool name mismatches (phase-1 table), is the applied tool's private_thought or
public_message identical/near-identical to the same player's PREVIOUS applied decision text (stale echo)?
Compare against a baseline: all Grok decisions without mismatch. Read-only."""
import json, os, collections, difflib
from common import game_dirs, decisions, ROOT
MM = os.path.join(ROOT, "docs/research_raw/paper_phase1_2026-10-28/opus/opus_response_mismatches.jsonl")
mm = {json.loads(l)["decision_id"] for l in open(MM) if json.loads(l)["model"] == "Grok"}
res = collections.Counter(); ex = []
for g, run in game_dirs().items():
    st, rs = decisions(run)
    last = {}
    for d in sorted(rs):
        r = rs[d]
        if r["openrouter_model_id"] != "x-ai/grok-4.7":
            continue
        fa = r.get("final_action") or {}
        priv, pub = fa.get("private_thought") or "", fa.get("public_message") or ""
        pid = r["player_id"]
        if pid in last:
            lp, lpub = last[pid]
            sim = difflib.SequenceMatcher(None, priv, lp).ratio() if priv and lp else 0
            k = "mismatch" if d in mm else "other"
            res[(k, "n")] += 1
            res[(k, "priv_exact_prev")] += bool(priv) and priv == lp
            res[(k, "priv_sim>=0.8")] += sim >= 0.8
            res[(k, "pub_exact_prev")] += bool(pub) and pub == lpub
            if d in mm and sim >= 0.8 and len(ex) < 8:
                ex.append((g, d[-6:], round(sim, 2), priv[:90]))
        last[pid] = (priv, pub)
for k in ("mismatch", "other"):
    n = res[(k, "n")]
    print(k, n, {m: f"{res[(k, m)]} ({res[(k, m)]/n:.1%})" for m in ("priv_exact_prev", "priv_sim>=0.8", "pub_exact_prev")})
for e in ex: print(e)
