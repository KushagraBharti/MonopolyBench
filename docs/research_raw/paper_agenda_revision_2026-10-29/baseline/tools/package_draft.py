"""Create a portable manuscript package, excluding build caches and raw games."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
names=['manuscript.tex','manuscript.pdf','preamble.tex','.latexmkrc','build.sh',
       'README.md','evidence_map.md','integration_log.md','verification.json',
       'references.bib','references_source.bib','protected_sources.json','figure_manifest.json',
       'requirements-manuscript.txt','adversarial_review.md',
       'artifacts/historical-claim-audit.zip','qa/verifier_regression.json',
       'qa/final_render_review.md','qa/transcript_preview.html']
files=[ROOT/n for n in names]
missing=[str(f.relative_to(ROOT)) for f in files if not f.is_file()]
if missing:
    raise FileNotFoundError(f'Required package inputs missing: {missing}')
for folder,patterns in [('sections',['*.tex']),('assets',['*.pdf','*.png']),
                        ('data',['*.json']),('tools',['*.py']),
                        ('coauthors',['*/*.md','*/*.tex','*/verification.json']),
                        ('final_review',['*/findings.md','*/checks.json']),
                        ('qa',['g13_context_check.json','verifier_regression.json','final_render_review.md']),
                        ('adversarial_reviews',['**/*.md','**/*.json','**/*.py'])]:
    for pattern in patterns:files.extend((ROOT/folder).glob(pattern))
files=sorted({f for f in files if f.is_file()})
manifest={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
(ROOT/'package_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(ROOT/'package_manifest.json')
target=ROOT/'monopolybench-revised-draft.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as out:
    for f in files:
        entry=zipfile.ZipInfo('monopolybench-revised-draft/'+str(f.relative_to(ROOT)),date_time=(2026,10,29,0,0,0))
        entry.compress_type=zipfile.ZIP_DEFLATED
        entry.external_attr=0o644<<16
        out.writestr(entry,f.read_bytes())
print(json.dumps({'zip':str(target),'files':len(files),'bytes':target.stat().st_size}))
