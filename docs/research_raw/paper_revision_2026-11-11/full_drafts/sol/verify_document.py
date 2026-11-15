"""Source correspondence, PDF diagnostics, and rendering; no engine execution."""
import hashlib,json,re,unicodedata
from pathlib import Path
import pymupdf
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;ROOT=H.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return ''.join(c.casefold() for c in unicodedata.normalize('NFKC',t) if c.isalnum())
def field(f):
 p=ROOT/f['source'];assert sha(p)==f['source_sha256'],p
 b=p.read_bytes();x=json.loads(b.splitlines()[f['jsonl_line_1based']-1]) if f.get('jsonl_line_1based') else json.loads(b)
 for k in f['json_pointer'].lstrip('/').split('/'):
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 assert hashlib.sha256(x.encode()).hexdigest()==f['field_sha256']
 return x
mapping={}
m=json.loads((H/'data/transcript_manifest.json').read_text())
for q in m['quotes']:mapping[q['id']]=[(m['fields'][s['field_id']],s['span'],s['text']) for s in q['excerpts']]
for q in json.loads((H/'data/opus_quote_manifest.json').read_text())['quotes']:mapping[q['id']]=[(q,q['span_codepoints'],q['excerpt'])]
for q in json.loads((H/'data/fable_quote_manifest.json').read_text())['quotes']:mapping[q['id']]=[(q,s['span'],s['text']) for s in q['excerpts']]
sectiontext='\n'.join(p.read_text() for p in (H/'sections').glob('*.tex') if p.name not in ['transcript_quotes.tex','opus_quotes.tex','fable_quotes.tex'])
used=re.findall(r'\\TranscriptQuote\{([^}]+)\}',sectiontext)
incidents=re.findall(r'\\Incident\{([^}]+)\}',sectiontext);assert len(incidents)==8
doc=pymupdf.open(H/'manuscript.pdf');pdftext='\n'.join(p.get_text() for p in doc)
np=norm(re.sub(r'^\d+\s*$','',pdftext,flags=re.M))
checks=[]
delivery=[]
raw_cache={}
for q in used:
 for f,(a,b),t in mapping[q]:
  assert field(f)[a:b]==t,q
  assert norm(t) in np,('render',q)
 checks.append(q)
 for f,_,_ in mapping[q]:
  if f['json_pointer'] in ['/final_action/public_message','/action/public_message']:
   fieldsrc=ROOT/f['source'];src=fieldsrc.parent/'decisions.jsonl'
   if src not in raw_cache:raw_cache[src]=[json.loads(x) for x in src.read_bytes().splitlines()]
   rows=raw_cache[src]
   source_row=json.loads(fieldsrc.read_bytes().splitlines()[f['jsonl_line_1based']-1])
   r=next(x for x in rows if x['phase']=='decision_resolved' and x['decision_id']==source_row['decision_id'])
   message=field(f)
   dn=int(r['decision_id'].rsplit('-',1)[1])
   seen=[]
   for st in rows:
    if st['phase']=='decision_started' and st['player_id']!=r['player_id'] and int(st['decision_id'].rsplit('-',1)[1])>dn and message in json.dumps(st['prompt_payload'],ensure_ascii=False):
     seen.append(dict(recipient=st['player_id'],decision=st['decision_id'],delta=int(st['decision_id'].rsplit('-',1)[1])-dn));break
   if not seen:
    assert q=='g12_d249_public_bankruptcy',('unexpected absent delivery',q)
   delivery.append(dict(quote=q,full_message_delivery=seen[0] if seen else None,scope='First later other-player request carrying the complete source field; no belief inference.'))
for kind in ['standard','recovery']:
 t=(H/f'data/{kind}_system_prompt.txt').read_text();assert norm(t) in np,kind
inputs=json.loads((H/'data/source_hashes.json').read_text());assert all(sha(ROOT/p)==h for p,h in inputs.items())
copied=json.loads((H/'data/copied_sources.json').read_text())
assert all(sha(ROOT/r['source'])==r['sha256']==sha(H/k) for k,r in copied.items())
log=(H/'build/manuscript.log').read_text()
diagnostics=[x for x in log.splitlines() if any(y in x for y in ['Overfull','Missing character','undefined','Warning'])]
assert not diagnostics,diagnostics
outside=[];blank=[]
out=H/'qa/render';out.mkdir(exist_ok=True)
for i,p in enumerate(doc,1):
 if len(p.get_text().strip())<30:blank.append(i)
 for b in p.get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   for s in line['spans']:
    if not p.rect.contains(pymupdf.Rect(s['bbox'])):outside.append([i,s['text']])
 assert not any(l['kind']==pymupdf.LINK_LAUNCH for l in p.get_links())
 p.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(out/f'page_{i:02}.png')
assert not outside,outside
assert not blank,blank
for start in range(1,len(doc)+1,6):
 sheet=Image.new('RGB',(1020,950),'#e1e5e8');dr=ImageDraw.Draw(sheet)
 for n in range(start,min(start+6,len(doc)+1)):
  im=Image.open(out/f'page_{n:02}.png');im.thumbnail((325,440));j=n-start;x=15+(j%3)*335;y=25+(j//3)*470
  sheet.paste(im,(x,y));dr.text((x,y-15),str(n),fill='black')
 sheet.save(out/f'contact_{start:02}.png')
(H/'qa/document_checks.json').write_text(json.dumps(dict(pdf_sha256=sha(H/'manuscript.pdf'),pages=len(doc),incidents=incidents,source_exact_rendered_quotes=checks,quote_count=len(checks),source_inputs_unchanged=len(inputs),copied_sources_unchanged=len(copied),full_prompt_text_rendered=True,diagnostics=diagnostics,outside=outside,blank=blank),indent=2)+'\n')
(H/'qa/public_delivery_checks.json').write_text(json.dumps(delivery,indent=2)+'\n')
(H/'qa/pdf_text.txt').write_text(pdftext)
print(f'{len(doc)} pages; {len(checks)} exact quote cards; eight incidents; full prompts; clean log and bounds. All {len(inputs)} numerical inputs unchanged.')
