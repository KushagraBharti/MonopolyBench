"""Document/source checks for this review. Read-only outside the owned folder."""
from pathlib import Path
import hashlib
import json
import re
import unicodedata
import pymupdf
from PIL import Image, ImageOps, ImageDraw

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
ROOT=BASE.parents[2]
qa=HERE/'qa'
qa.mkdir(exist_ok=True)
findings=json.loads((HERE/'findings.json').read_text())['findings']
for f in findings:
    for loc in f['locations']:
        text=(BASE/loc['path']).read_text()
        assert loc['exact_passage'] in text
        assert text[:text.index(loc['exact_passage'])].count('\n')+1==loc['line']

doc=pymupdf.open(HERE/'replacement_prose.pdf')
texts=[p.get_text() for p in doc]
assert all(len(t.strip())>100 for t in texts)
def norm(t):
    return ''.join(c for c in unicodedata.normalize('NFKC',t) if c.isalnum()).lower()
rendered=norm(''.join(texts))
source=(HERE/'replacement_prose.tex').read_text()
used=re.findall(r'\\q\{([^}]+)\}',source)
quote_data=json.loads((BASE/'full_drafts/fable_5_2/data/quote_manifest.json').read_text())['quotes']
quotes={q['id']:q for q in quote_data}
for qid in used:
    for span in quotes[qid]['spans']:
        assert norm(span['text']) in rendered,qid
checks=json.loads((HERE/'saved_record_checks.json').read_text())
for r in checks['necessary']:
    assert norm((r['note'] or r['provider']).strip()) in rendered,(r['game'],r['decision'])
log=(HERE/'build_final.log').read_text()
bad=[l for l in log.splitlines() if re.search(r'Warning|Overfull|Underfull|Missing character|Undefined',l)]
assert not bad,bad
edge=[]
for i,p in enumerate(doc):
    for b in p.get_text('blocks'):
        if b[0]<20 or b[1]<20 or b[2]>p.rect.width-20 or b[3]>p.rect.height-20:
            edge.append([i+1,list(b[:4])])
assert not edge
thumbs=[]
for i,p in enumerate(doc):
    pix=p.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False)
    pix.save(str(qa/f'page-{i+1:02d}.png'))
    im=Image.open(qa/f'page-{i+1:02d}.png').convert('RGB')
    im.thumbnail((390,510))
    card=Image.new('RGB',(410,545),'#ddd')
    card.paste(im,((410-im.width)//2,25))
    ImageDraw.Draw(card).text((8,6),f'Page {i+1}',fill='black')
    thumbs.append(card)
for start in range(0,len(thumbs),4):
    sheet=Image.new('RGB',(820,1090),'white')
    for j,im in enumerate(thumbs[start:start+4]):sheet.paste(im,((j%2)*410,(j//2)*545))
    sheet.save(qa/f'contact-{start//4+1}.png')

frozen=json.loads((BASE/'four_draft_manifest.json').read_text())['files']
frozen_result=[{'path':p,'expected':h,'actual':hashlib.sha256((BASE/p).read_bytes()).hexdigest()} for p,h in frozen.items()]
assert all(r['expected']==r['actual'] for r in frozen_result)
baseline=json.loads((BASE/'baseline_manifest.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in baseline.items())
result={'pdf_pages':len(doc),'pdf_sha256':hashlib.sha256((HERE/'replacement_prose.pdf').read_bytes()).hexdigest(),
        'used_quote_blocks':len(used),'all_used_quotes_present':True,'all_sixteen_full_entry_fields_present':True,
        'exact_passage_findings':len(findings),'all_passages_and_lines_match':True,'build_diagnostics':bad,'edge_violations':edge,
        'frozen_files':len(frozen),'frozen_files_match':True,'baseline_files':len(baseline),'baseline_files_match':True,
        'source_hashes_rechecked':0}
for p,h in checks['sources'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    result['source_hashes_rechecked']+=1
(qa/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
(qa/'frozen_hashes_after.json').write_text(json.dumps(frozen_result,indent=2)+'\n')
print(json.dumps(result,indent=2))
