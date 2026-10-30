"""Append hand-authored case reviews (JSON lines in argv[1]) to ../case_reviews.jsonl after validation:
catalog_id exists, not already reviewed, required fields present, disposition in the allowed set.
Serialisation only; all semantic content is authored by hand in the input file."""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
CAT = os.path.join(HERE, "..", "..", "candidate_catalog.jsonl")
OUT = os.path.join(HERE, "..", "case_reviews.jsonl")
REQ = ["catalog_id", "reading_status", "original_checks", "episode_id", "supported_claims",
       "unsupported_or_corrected_claims", "alternative_explanations", "counterexamples", "channel_limits",
       "disposition", "reason"]
DISP = {"supported", "qualified", "contradicted", "unresolved", "historical/superseded"}
cat = {}
for l in open(CAT):
    r = json.loads(l); cat[r["catalog_id"]] = r
done = set()
if os.path.exists(OUT):
    done = {json.loads(l)["catalog_id"] for l in open(OUT) if l.strip()}
new = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for n in new:
    cid = n["catalog_id"]
    assert cid in cat, cid
    assert cid not in done, f"duplicate {cid}"
    for k in REQ:
        assert k in n, (cid, k)
    assert n["disposition"] in DISP, (cid, n["disposition"])
    c = cat[cid]
    n.update(game=c["game"], source_reviewer=c["source_reviewer"], entry_status=c["entry_status"],
             reviewer="Opus (claude-opus-5-5)", stage="independent_initial", date="2026-10-29")
    done.add(cid)
with open(OUT, "a") as f:
    for n in new:
        f.write(json.dumps(n, ensure_ascii=False) + "\n")
print("appended", len(new), "total", len(done))
