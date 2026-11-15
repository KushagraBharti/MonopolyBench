#!/usr/bin/env python3
"""Read-only check of the 84-file November 12 historical manuscript pin."""
import hashlib, json, sys, os
BASE = os.path.abspath(sys.argv[1])   # .../paper_revision_2026-11-12
OUT = sys.argv[2]
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()
mp = os.path.join(BASE, 'final_manuscript_manifest.json')
m = json.load(open(mp))
bad, missing, ok = [], [], 0
for rel, want in sorted(m['files'].items()):
    p = os.path.join(BASE, rel)
    if not os.path.isfile(p): missing.append(rel); continue
    if sha(p) == want: ok += 1
    else: bad.append(rel)
res = {'manifest': 'paper_revision_2026-11-12/final_manuscript_manifest.json',
       'manifest_sha256': sha(mp), 'listed': len(m['files']), 'ok': ok,
       'mismatch': bad, 'missing': missing}
json.dump(res, open(OUT, 'w'), indent=1)
print(res)
