"""Recompute reviewed/remaining ID lists in ../progress.json from the review files.
Manual fields are preserved; pass key=value pairs (JSON values) to set others, e.g.
  python3 update_progress.py 'next="G15: ..."'
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OP = os.path.dirname(HERE)
CR = os.path.dirname(OP)
P = os.path.join(OP, "progress.json")


def ids(path, key):
    out = []
    if os.path.exists(path):
        for line in open(path):
            if line.strip():
                out.append(json.loads(line)[key])
    return out


d = json.load(open(P))
catalog = ids(os.path.join(CR, "candidate_catalog.jsonl"), "catalog_id")
reviewed = ids(os.path.join(OP, "case_reviews.jsonl"), "catalog_id")
sample = ids(os.path.join(CR, "public_unflagged_sample.jsonl"), "decision_id")
s_rev = ids(os.path.join(OP, "negative_control_reviews.jsonl"), "decision_id")
rs = set(reviewed)
d["catalog_ids_reviewed"] = reviewed
d["catalog_ids_remaining"] = [c for c in catalog if c not in rs]
d["catalog_counts"] = {"total": len(catalog), "reviewed": len(rs), "remaining": len(catalog) - len(rs)}
ss = set(s_rev)
d["sample_ids_reviewed"] = s_rev
d["sample_ids_remaining"] = [s for s in sample if s not in ss]
d["sample_counts"] = {"total": len(sample), "reviewed": len(ss), "remaining": len(sample) - len(ss)}
text = open(os.path.join(OP, "game_assessments.md")).read()
d["games_trajectory_assessed"] = sorted(int(n) for n in re.findall(r"^## Game (\d+)", text, re.M))
for arg in sys.argv[1:]:
    k, v = arg.split("=", 1)
    d[k] = json.loads(v)
json.dump(d, open(P, "w"), indent=1)
print(d["catalog_counts"], d["sample_counts"], d["games_trajectory_assessed"])
