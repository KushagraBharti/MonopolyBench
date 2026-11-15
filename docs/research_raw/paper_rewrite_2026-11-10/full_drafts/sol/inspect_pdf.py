"""Document rendering and geometry inspection only; no benchmark execution."""
import json
import re
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
doc=pymupdf.open(HERE/'manuscript.pdf')
out=HERE/'qa'
out.mkdir(exist_ok=True)
pages=[]
violations=[]
texts=[]
for i,page in enumerate(doc):
    t=page.get_text()
    texts.append(t)
    p=out/f'page-{i+1:02d}.png'
    page.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(p)
    for b in page.get_text('dict')['blocks']:
        if 'lines' not in b: continue
        for line in b['lines']:
            for s in line['spans']:
                x0,y0,x1,y1=s['bbox']
                if x0<0 or y0<0 or x1>page.rect.width+.5 or y1>page.rect.height+.5:
                    violations.append({'page':i+1,'bbox':s['bbox'],'text':s['text']})
    pages.append({'page':i+1,'characters':len(t),'image':str(p.relative_to(HERE))})
for start in range(0,len(doc),9):
    sheet=Image.new('RGB',(1320,3*620),'#d9d9d9')
    dr=ImageDraw.Draw(sheet)
    for k,i in enumerate(range(start,min(start+9,len(doc)))):
        im=Image.open(out/f'page-{i+1:02d}.png');im.thumbnail((420,580))
        x=(k%3)*440+(440-im.width)//2;y=(k//3)*620+30
        sheet.paste(im,(x,y));dr.text((x,y-20),f'Page {i+1}',fill='black')
    sheet.save(out/f'contact-{start//9+1}.png')
log=(HERE/'manuscript.log').read_text()
report={'pages':len(doc),'text_characters':sum(map(len,texts)),
    'page_geometry_violations':violations,
    'undefined_citations_or_references':bool(re.search(r'undefined|Citation.*Warning',log)),
    'overfull_boxes':len(re.findall('Overfull',log)),
    'underfull_boxes':len(re.findall('Underfull',log)),
    'rendered_pages':pages,
    'visual_inspection':'Direct visual inspection is documented separately in qa/render_review.md.'}
(HERE/'render_checks.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'manuscript.txt').write_text('\n\n'.join(texts))
print(json.dumps({k:v for k,v in report.items() if k!='rendered_pages'},indent=2))
