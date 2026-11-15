"""Verify the frozen four-draft hashes. Read-only. Usage: python3 -I check_hashes.py <repo_root> <hash_json> <out_json>"""
import hashlib, json, sys, pathlib, datetime
root = pathlib.Path(sys.argv[1]); spec = json.load(open(sys.argv[2]))
res = {"checked_at_utc": datetime.datetime.utcnow().isoformat()+"Z", "n": len(spec), "mismatch": [], "missing": []}
for rel, h in sorted(spec.items()):
    p = root / rel
    if not p.exists(): res["missing"].append(rel); continue
    if hashlib.sha256(p.read_bytes()).hexdigest() != h: res["mismatch"].append(rel)
res["ok"] = not res["mismatch"] and not res["missing"]
json.dump(res, open(sys.argv[3], "w"), indent=2)
print(json.dumps({k: res[k] for k in ("n","ok")}), len(res["mismatch"]), len(res["missing"]))
