"""Verify and render this document. No game, policy, provider, or model execution."""
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parents[1]
doc=fitz.open(HERE/'manuscript.pdf')
pages=[p.get_text() for p in doc]
(HERE/'qa/extracted.txt').write_text('\n\f\n'.join(pages))
reference_page=next(i+1 for i,s in enumerate(pages) if s.startswith('References\n'))
appendix_page=next(i+1 for i,s in enumerate(pages) if 'Financing rubric and complete first-response' in s)
log=(HERE/'build/manuscript.log').read_text()
diagnostics=[s for s in log.splitlines() if any(k in s for k in ['Overfull','LaTeX Warning','Missing character','undefined'])]
assert not diagnostics,diagnostics
assert reference_page-1<=9,(reference_page,appendix_page)
assert all(s.strip() for s in pages)
assert doc.metadata['author']=='Kushagra Bharti'
def norm(s):
    s=unicodedata.normalize('NFKC',s).replace('\u00ad','')
    for a,b in [('—',''),('–',''),('→','then'),('’',"'"),('“','"'),('”','"')]:s=s.replace(a,b)
    return re.sub(r'[^a-zA-Z0-9]','',s).lower()
alltext=norm(''.join(p.get_text(clip=fitz.Rect(0,0,p.rect.width,p.rect.height-35)) for p in doc))
fields=json.loads((HERE/'data/sixteen_channels.json').read_text())
checked=0
for r in fields:
    for x in [r['applied_action'].get('private_thought'),r['provider_reasoning'],r['assistant_content']]:
        if x:
            assert norm(x) in alltext,(r['game'],r['decision'],x[:60])
            checked+=1
offers=json.loads((HERE/'data/offers.json').read_text())
assert len(offers)==920
assert Counter(r['response'] for r in offers)=={'accept_trade':113,'counter_trade':394,'reject_trade':413}
assert sum(r['accept_available'] for r in offers)==918
episodes=json.loads((HERE/'data/episodes_188.json').read_text())
assert len(episodes)==188
assert Counter(r['outcome'] for r in episodes)=={'paid':128,'bankrupt':60}
outside=[]
for i,p in enumerate(doc):
    for b in p.get_text('dict')['blocks']:
        for line in b.get('lines',[]):
            for s in line['spans']:
                x0,y0,x1,y1=s['bbox']
                if x0 < 15 or x1 > p.rect.width-15 or y0 < 12 or y1 > p.rect.height-12:outside.append((i+1,s['text']))
    p.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(HERE/'qa'/f'page-{i+1:02}.png')
assert not outside,outside
for start in range(0,len(doc),6):
    thumbs=[]
    for i in range(start,min(start+6,len(doc))):
        im=Image.open(HERE/'qa'/f'page-{i+1:02}.png').convert('RGB')
        im.thumbnail((425,550));thumbs.append((i+1,im))
    sheet=Image.new('RGB',(3*445,2*585),'#dadada');draw=ImageDraw.Draw(sheet)
    for n,(idx,im) in enumerate(thumbs):
        x=(n%3)*445+10;y=(n//3)*585+25
        sheet.paste(im,(x,y));draw.text((x,y-18),f'Page {idx}',fill='black')
    sheet.save(HERE/'qa'/f'contact-{start+1:02}.png')
result=dict(pages=len(doc),main_pages=reference_page-1,reference_start=reference_page,appendix_start=appendix_page,full_channel_fields_verified=checked,latex_diagnostics=diagnostics,out_of_page_spans=outside,pdf_sha256=hashlib.sha256((HERE/'manuscript.pdf').read_bytes()).hexdigest(),rendered_pages=len(doc),verification_scope='Document build/render and retained-record arithmetic only; no evaluation')
(HERE/'qa/verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
