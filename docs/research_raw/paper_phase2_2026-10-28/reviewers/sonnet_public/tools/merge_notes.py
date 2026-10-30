"""Rebuild coverage.jsonl + progress.json from hand-written notes/gXX-pNNN.txt files.

Note line format:  LINE|note text|CAND,CAND   (LINE = 1-based source line in game-XX.jsonl; cands optional)
Idempotent: always rebuilds from all notes files.  Prints a concise summary only.
"""
import glob, json, os, re, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

REV_SONNET = {"reviewer": "Sonnet 5.5 (sonnet_public)", "model": "claude-sonnet-5-5",
              "effort": "unreported by harness (assignment text: Sonnet xhigh)"}
REV_HAIKU = {"reviewer": "Haiku 5.5 (sonnet_public scope; continued after user model switch)", "model": "claude-haiku-5-5",
             "effort": "unreported by harness"}
SWITCH_AFTER_GAME = 3  # games 1-3 by Sonnet 5.5; games 4-20 by Haiku 5.5 (user-selected model switch, 2026-10-28)
def rev(g):
    return REV_SONNET if g <= SWITCH_AFTER_GAME else REV_HAIKU
cands = set()
cp = OUT + "/candidates.jsonl"
if os.path.exists(cp):
    for line in open(cp):
        cands.add(json.loads(line)["candidate_id"])

cov = {}
problems = []
for nf in sorted(glob.glob(OUT + "/notes/g*-p*.txt")):
    m = re.search(r"g(\d+)-p(\d+)", nf)
    g = int(m.group(1))
    for raw in open(nf):
        raw = raw.rstrip("\n")
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split("|")
        try:
            ln = int(parts[0])
        except ValueError:
            problems.append("bad line %s: %s" % (os.path.basename(nf), raw[:60])); continue
        note = parts[1].strip() if len(parts) > 1 else ""
        cl = [c.strip() for c in parts[2].split(",") if c.strip()] if len(parts) > 2 else []
        if len(note.split()) < 2:
            problems.append("short note g%d #%d" % (g, ln))
        for c in cl:
            if c not in cands:
                problems.append("unknown cand %s at g%d #%d" % (c, g, ln))
        if (g, ln) in cov:
            problems.append("duplicate g%d #%d in %s" % (g, ln, os.path.basename(nf)))
        cov[(g, ln)] = (note, cl)

manifest = json.load(open(PR + "/manifest.json"))
totals = {f["game"]: f["decisions"] for f in manifest["files"]}
rows_out = []
progress = {"version": "sonnet_public_progress_v1", "numbering": "display number #N = 1-based line N of public_review/game-XX.jsonl; exact decision_id ends -dec-(N-1), zero-padded to 6 digits (e.g. #113 = ...-dec-000112). Turn numbers (tN) are global engine turn_index values (one per player turn), not own-turn counts.", "updated": datetime.datetime.now().isoformat(timespec="seconds"),
            "reading_copy": "reading/gXX/pNNN.txt: compact rendering of every public_review record (all public messages verbatim, all actions, legal-option summaries, financial events, cash for all players each decision, holdings checkpoints). Omits: raw public_timeline_last_20 (recomputed on demand by tools/exposure.py), full menu lists beyond counts.",
            "coverage_status_meaning": "reviewed_via_compact_copy = the decision block (including its public message, action, options summary and economic events) was read in the compact copy and given a hand-written note",
            "games": {}}
for g in sorted(totals):
    rows = load_game(g)
    n = totals[g]
    assert len(rows) == n
    done = sorted(ln for (gg, ln) in cov if gg == g)
    remaining = [ln for ln in range(1, n + 1) if (g, ln) not in cov]
    # ranges
    rng = []
    for ln in remaining:
        if rng and rng[-1][1] == ln - 1:
            rng[-1][1] = ln
        else:
            rng.append([ln, ln])
    for ln in done:
        r = rows[ln - 1]
        note, cl = cov[(g, ln)]
        rows_out.append({"game": g, "decision_id": r["decision_id"], **rev(g), "status": "reviewed_via_compact_copy",
                         "source_file": "docs/research_raw/paper_phase2_2026-10-28/public_review/game-%02d.jsonl" % g,
                         "source_line": ln, "display_number": ln, "decision_id_zero_based_suffix": int(r["decision_id"].rsplit("-dec-", 1)[1]), "turn_index": r["turn_index"], "player_id": r["player_id"],
                         "decision_type": r["decision_type"], "applied_action": r["applied_action"]["action"],
                         "fallback_used": r["fallback_used"], "retry_used": r["retry_used"], "attempt_outcomes": [x["outcome"] + "/" + ("std" if x["response_condition"] == "standard" else "nothought") for x in r["attempt_metadata"]], "note": note, "candidate_ids": cl})
    progress["games"][str(g)] = {"decisions": n, "reviewed": len(done), "remaining": len(remaining),
                                 "remaining_line_ranges": rng,
                                 "remaining_decision_ids": [rows[ln - 1]["decision_id"] for ln in remaining],
                                 "narrative_final": os.path.exists(OUT + "/narratives/g%02d.md" % g) and ("FINAL" in open(OUT + "/narratives/g%02d.md" % g).read(400))}
progress["total_decisions"] = sum(totals.values())
progress["total_reviewed"] = len(rows_out)
progress["total_remaining"] = progress["total_decisions"] - len(rows_out)
with open(OUT + "/coverage.jsonl", "w") as f:
    for r in rows_out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(progress, open(OUT + "/progress.json", "w"), indent=1)
print("reviewed %d / %d ; remaining %d ; problems %d" % (len(rows_out), progress["total_decisions"], progress["total_remaining"], len(problems)))
for g in sorted(totals):
    p = progress["games"][str(g)]
    if p["reviewed"]:
        print(" g%02d %d/%d%s" % (g, p["reviewed"], p["decisions"], " remaining:" + str(p["remaining_line_ranges"][:3]) if p["remaining"] else " DONE"))
unk = [p for p in problems if p.startswith("unknown cand")]
oth = [p for p in problems if not p.startswith("unknown cand")]
if unk: print("unknown-candidate refs (blocks not yet written):", len(unk), sorted({p.split()[2] for p in unk}))
for p in oth[:25]:
    print("PROBLEM:", p)
