"""Confirm that this review changed nothing outside reviews/fable_5_2/.

1. Recompute every hash in baseline_source_hashes.json (the 29 October
   sources frozen at the start of the rewrite).
2. Recompute every hash in reviews/astra/review_source_hashes.json (the four
   frozen drafts as Astra recorded them).
3. Record hashes of the inputs this review's scripts read.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import PKG, REPO, dump, game_dir  # noqa: E402


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def flatten(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v):
                out[k] = v
            else:
                flatten(v, out)
    elif isinstance(obj, list):
        for v in obj:
            flatten(v, out)


def verify(manifest_path):
    flat: dict = {}
    flatten(json.load(open(manifest_path)), flat)
    ok = changed = missing = 0
    changed_paths = []
    for rel, h in flat.items():
        cands = [rel, os.path.join(PKG, rel), os.path.join(REPO, rel), os.path.join(PKG, "..", rel)]
        hit = [c for c in cands if os.path.isfile(c)]
        if not hit:
            missing += 1
            continue
        if sha(hit[0]) == h:
            ok += 1
        else:
            changed += 1
            changed_paths.append(rel)
    return {"entries": len(flat), "match": ok, "changed": changed, "not_located": missing, "changed_paths": changed_paths}


report = {
    "baseline_source_hashes": verify(os.path.join(PKG, "baseline_source_hashes.json")),
    "astra_review_source_hashes": verify(os.path.join(PKG, "reviews", "astra", "review_source_hashes.json")),
}
inputs = [os.path.join(PKG, "data", n) for n in (
    "agenda_offers.json", "agenda_flows.json", "first_management_windows.json", "resolution_conditions.json",
    "t01_cohort.json", "t05_spending_units.json", "t06_eliminations.json", "agenda_rejection_reasons.json")]
inputs.append(os.path.join(PKG, "..", "paper_phase1_2026-10-28", "sol", "group_episodes.jsonl"))
inputs.append(os.path.join(REPO, "contracts", "data", "board.json"))
inputs += [os.path.join(game_dir(g), "decisions.jsonl") for g in range(1, 21)]
inputs += sorted(glob.glob(os.path.join(PKG, "full_drafts", "*", "manuscript.pdf")))
inputs += [os.path.join(PKG, "full_drafts", "opus", "sections", "opus_quotes.tex"),
           os.path.join(PKG, "full_drafts", "fable_5_2", "sections", "quotes_supplement.tex"),
           os.path.join(PKG, "sections", "transcript_quotes.tex"),
           os.path.join(PKG, "reviews", "astra", "all_four_review.md"),
           os.path.join(PKG, "reviews", "astra", "comparison_in_progress.md")]
report["inputs_read"] = {os.path.relpath(os.path.abspath(p), REPO): sha(p) for p in inputs}
dump("review_source_hashes.json", report)
print(json.dumps({k: v for k, v in report.items() if k != "inputs_read"}, indent=1))
print("inputs hashed:", len(report["inputs_read"]))
