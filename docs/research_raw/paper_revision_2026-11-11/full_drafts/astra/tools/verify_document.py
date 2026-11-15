"""Check original quotation spans, source preservation, and PDF presentation."""
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import pymupdf
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[4]
OLD=ROOT/'docs/research_raw/paper_rewrite_2026-11-10'
QA=HERE/'qa';QA.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:''.join(c.casefold() for c in unicodedata.normalize('NFKC',s) if c.isalnum())
sections=[p for p in (HERE/'sections').glob('*.tex') if p.name not in ['transcript_quotes.tex','opus_quotes.tex','fable_quotes.tex']]
prose='\n'.join(p.read_text() for p in sections)
used=re.findall(r'\\TranscriptQuote\{([^}]+)\}',prose)
assert len(used)==len(set(used))
assert len(re.findall(r'\\TranscriptTitle\{',prose))==8
quotes={}
m=json.loads((HERE/'data/transcript_manifest.json').read_text())
for q in m['quotes']:
    quotes[q['id']]=[(m['fields'][s['field_id']],s['span'],s['text']) for s in q['excerpts']]
for q in json.loads((HERE/'data/opus_quote_manifest.json').read_text())['quotes']:
    quotes[q['id']]=[(q,q['span_codepoints'],q['excerpt'])]
for q in json.loads((HERE/'data/fable_quote_manifest.json').read_text())['quotes']:
    quotes[q['id']]=[(q,s['span'],s['text']) for s in q['excerpts']]
doc=pymupdf.open(HERE/'manuscript.pdf');text='\n'.join(p.get_text() for p in doc); normalized=norm(text)
sources={};checked=[]
for qid in used:
    for field,(start,stop),excerpt in quotes[qid]:
        p=ROOT/field['source'];blob=sources.setdefault(p,p.read_bytes())
        assert hashlib.sha256(blob).hexdigest()==field['source_sha256']
        obj=json.loads(blob.splitlines()[field['jsonl_line_1based']-1]) if field.get('jsonl_line_1based') else json.loads(blob)
        for key in field['json_pointer'].lstrip('/').split('/'):
            key=key.replace('~1','/').replace('~0','~');obj=obj[int(key)] if isinstance(obj,list) else obj[key]
        assert hashlib.sha256(obj.encode()).hexdigest()==field['field_sha256']
        assert obj[start:stop]==excerpt,qid
        assert norm(excerpt) in normalized,('rendered quote missing',qid)
    checked.append(qid)
protected={}
for p in [HERE.parents[1]/'baseline_hashes.json',OLD/'baseline_source_hashes.json',OLD/'reviews/astra/review_source_hashes.json']:
    for k,v in json.loads(p.read_text()).items():
        if isinstance(v,str):
            target=ROOT/k
            if not target.exists():target=OLD/k
            assert target.exists(),k
            assert sha(target)==v,('protected changed',k)
            protected[str(target)]=v
for k,v in json.loads((HERE/'data/source_hashes.json').read_text()).items():assert sha(ROOT/k)==v
log=(HERE/'build/manuscript.log').read_text()
diagnostics=[l for l in log.splitlines() if any(x in l for x in ['Overfull','Missing character','undefined','LaTeX Warning','Package natbib Warning'])]
outside=[];launch=[];blank=[]
for n,p in enumerate(doc,1):
    if len(p.get_text().strip())<30:blank.append(n)
    for b in p.get_text('dict')['blocks']:
        for line in b.get('lines',[]):
            for s in line['spans']:
                if not p.rect.contains(pymupdf.Rect(s['bbox'])*p.rotation_matrix):outside.append([n,s['text']])
    launch += [[n,l]for l in p.get_links() if l['kind']==pymupdf.LINK_LAUNCH]
    pix=p.get_pixmap(matrix=pymupdf.Matrix(.9,.9));pix.save(QA/f'p{n:02}.png')
for start in range(0,len(doc),6):
    sheet=Image.new('RGB',(1100,1500),'#dddddd');draw=ImageDraw.Draw(sheet)
    for i in range(start,min(start+6,len(doc))):
        im=Image.open(QA/f'p{i+1:02}.png');im.thumbnail((530,465))
        x=(i-start)%2*550+10;y=(i-start)//2*500+20
        draw.text((x,y-17),f'Page {i+1}',fill='black');sheet.paste(im,(x,y))
    sheet.save(QA/f'contact_{start+1:02}.png')
(QA/'extracted.txt').write_text(text)
result=dict(pages=len(doc),quotes=len(used),original_quote_files=len(sources),protected_files=len(protected),
            diagnostics=diagnostics,outside=outside,launch=launch,blank=blank,pdf_sha256=sha(HERE/'manuscript.pdf'))
(QA/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert not(diagnostics or outside or launch or blank)
