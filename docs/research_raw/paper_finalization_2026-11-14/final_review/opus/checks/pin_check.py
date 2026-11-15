#!/usr/bin/env python3
"""Read-only pin check: hashes files listed in the two manifests. No evaluation."""
import hashlib, json, sys, datetime, pathlib
REPO = pathlib.Path('/Users/kushagra/CS-Projects/MonopolyBench')
FIN = REPO/'docs/research_raw/paper_finalization_2026-11-14'
H12 = REPO/'docs/research_raw/paper_revision_2026-11-12/final_manuscript_manifest.json'
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()
out={'checked_at': datetime.datetime.now().isoformat()}
man = FIN/'integration_review_manifest.json'
out['finalization_manifest_sha256']=sha(man)
m=json.load(open(man))
bad=[]
for rel,h in m['files'].items():
    p=FIN/rel
    if not p.exists(): bad.append((rel,'missing'))
    elif sha(p)!=h: bad.append((rel,'mismatch'))
out['finalization_entries']=len(m['files']); out['finalization_bad']=bad
pdf=FIN/'integrated/build/manuscript.pdf'
out['integrated_pdf_sha256']=sha(pdf) if pdf.exists() else None
out['nov12_manifest_sha256']=sha(H12)
m2=json.load(open(H12)); files=m2['files']
bad2=[]
items = files.items() if isinstance(files,dict) else [(x['path'],x['sha256']) for x in files]
for rel,h in items:
    p=REPO/rel if not pathlib.Path(rel).is_absolute() else pathlib.Path(rel)
    if not p.exists():
        p2=H12.parent/rel
        p=p2
    if not p.exists(): bad2.append((rel,'missing'))
    elif sha(p)!=h: bad2.append((rel,'mismatch'))
out['nov12_entries']=len(files); out['nov12_bad']=bad2
print(json.dumps(out,indent=1))
