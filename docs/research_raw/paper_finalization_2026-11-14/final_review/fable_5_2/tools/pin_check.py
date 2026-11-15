#!/usr/bin/env python3
"""Read-only pin check. Hashes every file listed in the integration review
manifest and reports mismatches / missing / (optionally) the manifest's own hash.
Writes nothing outside the path given as argv[2]."""
import hashlib, json, sys, os
ROOT = os.path.abspath(sys.argv[1])
OUT = sys.argv[2]
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()
mpath = os.path.join(ROOT, 'integration_review_manifest.json')
m = json.load(open(mpath))
bad, missing, ok = [], [], 0
for rel, want in sorted(m['files'].items()):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        missing.append(rel); continue
    got = sha(p)
    if got == want: ok += 1
    else: bad.append((rel, want, got))
res = {
    'manifest_sha256': sha(mpath),
    'manifest_expected': 'a362c4c6d020adb115a50b919d85d3db6777d223189493d7c4edd1517885e269',
    'integrated_pdf_sha256': sha(os.path.join(ROOT, 'integrated/manuscript.pdf')),
    'integrated_pdf_expected': 'e5c44bebfb1d6b0b7c434d875261be63b11e4c6457396ee97596457a0c840dae',
    'listed': len(m['files']), 'ok': ok, 'mismatch': bad, 'missing': missing,
}
json.dump(res, open(OUT, 'w'), indent=1)
print({k: (v if not isinstance(v, list) else len(v)) for k, v in res.items()})
