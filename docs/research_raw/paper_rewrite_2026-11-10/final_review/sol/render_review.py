"""Render and inspect the pinned document, with no build or gameplay execution."""
import hashlib,json,re,unicodedata
from pathlib import Path
import pymupdf
from PIL import Image,ImageDraw

OUT=Path(__file__).resolve().parent
INT=OUT.parents[1]/'integrated'
R=OUT/'render'
R.mkdir(exist_ok=True)
doc=pymupdf.open(INT/'manuscript.pdf')
assert len(doc)==33
texts=[p.get_text() for p in doc]
(OUT/'manuscript_text.txt').write_text('\n\f\n'.join(texts))
def norm(s):return ''.join(c.casefold() for c in unicodedata.normalize('NFKC',s) if c.isalnum())
whole=norm('\n'.join(texts))
quotes=json.loads((OUT/'original_quote_fields.json').read_text())
for q in quotes:assert norm(q['field'][slice(*q['span'])]) in whole,q['id']
outside=[]
launches=[]
for pn,p in enumerate(doc,1):
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for s in l['spans']:
                if not p.rect.contains(pymupdf.Rect(s['bbox'])*p.rotation_matrix):outside.append([pn,s['text']])
    launches += [pn for l in p.get_links() if l['kind']==pymupdf.LINK_LAUNCH]
for start in range(0,len(doc),6):
    sheet=Image.new('RGB',(1500,1470),'#ddd')
    draw=ImageDraw.Draw(sheet)
    for offset in range(min(6,len(doc)-start)):
        i=start+offset
        pix=doc[i].get_pixmap(matrix=pymupdf.Matrix(.78,.78),alpha=False)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        im.thumbnail((480,695))
        x=offset%3*500+10;y=offset//3*735+25
        draw.text((x,y-20),f'Page {i+1}',fill='black')
        sheet.paste(im,(x,y))
    sheet.save(R/f'contact_{start+1:02d}_{min(start+6,len(doc)):02d}.png')
for i,p in enumerate(doc,1):
    pix=p.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False)
    pix.save(R/f'page_{i:02d}.png')
report={'pages':len(doc),'pdf_sha256':hashlib.sha256((INT/'manuscript.pdf').read_bytes()).hexdigest(),
  'outside_text_spans':outside,'launch_actions':launches,'blank_pages':[i+1 for i,t in enumerate(texts) if len(t.strip())<30],
  'original_excerpt_spans_present':len(quotes),
  'page_headings':[{'page':i+1,'first_text':t[:180]} for i,t in enumerate(texts)]}
(OUT/'render_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
