"""Verify retained quote spans, source preservation, and compiled presentation."""
import hashlib,json,re,unicodedata
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in HERE.parents if (p/'contracts').is_dir())
QA=HERE/'qa'; QA.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:''.join(c.casefold() for c in unicodedata.normalize('NFKC',s) if c.isalnum())
case=(HERE/'sections/casebook.tex').read_text()
used=re.findall(r'\\TranscriptQuote\{([^}]+)\}',case)
assert len(re.findall(r'\\TranscriptTitle\{',case))==8
quotes={}
m=json.loads((HERE/'data/transcript_manifest.json').read_text())
for q in m['quotes']: quotes[q['id']]=[(m['fields'][s['field_id']],s['span'],s['text']) for s in q['excerpts']]
for q in json.loads((HERE/'data/opus_quote_manifest.json').read_text())['quotes']:
    quotes[q['id']]=[(q,q['span_codepoints'],q['excerpt'])]
for file,key in [('fable_quote_manifest','excerpts'),('additional_quote_manifest','spans'),('integration_quote_manifest','spans'),('finalization_quote_manifest','spans')]:
    for q in json.loads((HERE/'data'/f'{file}.json').read_text())['quotes']:
        quotes[q['id']]=[(q,s['span'],s['text']) for s in q[key]]
doc=pymupdf.open(HERE/'manuscript.pdf')
body='\n'.join(p.get_text(clip=pymupdf.Rect(0,0,p.rect.width,p.rect.height-40)) for p in doc)
normalized=norm(body); cache={}
def original(field):
    p=ROOT/field['source']; blob=cache.setdefault(p,p.read_bytes())
    assert hashlib.sha256(blob).hexdigest()==field['source_sha256'],p
    obj=json.loads(blob.splitlines()[field['jsonl_line_1based']-1]) if field.get('jsonl_line_1based') else json.loads(blob)
    for key in field['json_pointer'].lstrip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~'); obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert hashlib.sha256(obj.encode()).hexdigest()==field['field_sha256']
    return obj
for qid in used:
    for field,(a,b),span in quotes[qid]:
        assert original(field)[a:b]==span,qid
        assert norm(span) in normalized,('quote missing',qid)
fields=json.loads((HERE/'data/all_channels_manifest.json').read_text())['fields']
for f in fields:
    assert original(f)==f['text']
    assert norm(f['text']) in normalized,('field missing',f['game'],f['decision'],f['channel'])
base=ROOT/'docs/research_raw/paper_revision_2026-11-12'
pin=json.loads((base/'final_manuscript_manifest.json').read_text())['files']
for p,h in pin.items(): assert sha(base/p)==h,('protected changed',p)
log=(HERE/'build/manuscript.log').read_text()
diagnostics=[l for l in log.splitlines() if any(x in l for x in ['Overfull','Missing character','undefined','LaTeX Warning','Package natbib Warning'])]
outside=[]; blank=[]
for i,p in enumerate(doc,1):
    if len(p.get_text().strip())<30: blank.append(i)
    for block in p.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for s in line['spans']:
                if not p.rect.contains(pymupdf.Rect(s['bbox'])): outside.append([i,s['text']])
    p.get_pixmap(matrix=pymupdf.Matrix(.8,.8)).save(QA/f'p{i:02}.png')
for start in range(0,len(doc),6):
    sheet=Image.new('RGB',(1200,1650),'#dddddd'); draw=ImageDraw.Draw(sheet)
    for i in range(start,min(start+6,len(doc))):
        im=Image.open(QA/f'p{i+1:02}.png'); im.thumbnail((580,510)); x=(i-start)%2*600+10;y=(i-start)//2*550+25
        draw.text((x,y-20),f'Page {i+1}',fill='black');sheet.paste(im,(x,y))
    sheet.save(QA/f'contact_{start+1:02}.png')
(QA/'extracted.txt').write_text(body)
result=dict(pages=len(doc),quotes=len(used),initial_fields=len(fields),protected_files=len(pin),diagnostics=diagnostics,outside=outside,blank=blank,pdf_sha256=sha(HERE/'manuscript.pdf'))
(QA/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert not(diagnostics or outside or blank)
