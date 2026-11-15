"""Source/quote correspondence and document QA, never engine execution."""
import hashlib,json,re,unicodedata
from pathlib import Path
import pymupdf
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parents[1]
ROOT=next(p for p in H.parents if (p/'contracts').is_dir())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return ''.join(c.casefold() for c in unicodedata.normalize('NFKC',t) if c.isalnum())
cache={}
def field(f):
    p=ROOT/f['source'];assert sha(p)==f['source_sha256'],p
    if p not in cache:cache[p]=p.read_bytes().splitlines()
    x=json.loads(cache[p][f['jsonl_line_1based']-1]) if f.get('jsonl_line_1based') else json.loads(p.read_bytes())
    for k in f['json_pointer'].lstrip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
    assert hashlib.sha256(x.encode()).hexdigest()==f['field_sha256']
    return x
mapping={};m=json.loads((H/'data/transcript_manifest.json').read_text())
for q in m['quotes']:mapping[q['id']]=[(m['fields'][s['field_id']],s['span'],s['text']) for s in q['excerpts']]
for q in json.loads((H/'data/opus_quote_manifest.json').read_text())['quotes']:mapping[q['id']]=[(q,q['span_codepoints'],q['excerpt'])]
for q in json.loads((H/'data/fable_quote_manifest.json').read_text())['quotes']:mapping[q['id']]=[(q,s['span'],s['text']) for s in q['excerpts']]
for q in json.loads((H/'data/additional_quote_manifest.json').read_text())['quotes']:mapping[q['id']]=[(q,s['span'],s['text']) for s in q['spans']]
sectionfiles=['introduction','methods','finance','bargaining','continuations','discussion','appendix']
sectiontext='\n'.join((H/f'sections/{f}.tex').read_text() for f in sectionfiles)
used=re.findall(r'\\TranscriptQuote\{([^}]+)\}',sectiontext)
incidents=re.findall(r'\\TranscriptTitle\{([^}]+)\}',sectiontext);assert len(incidents)==8
doc=pymupdf.open(H/'manuscript.pdf');pdftext='\n'.join(p.get_text() for p in doc)
np=norm(re.sub(r'^\d+\s*$','',pdftext,flags=re.M));checks=[];delivery=[];records={}
for q in used:
    for f,(a,b),t in mapping[q]:
        assert field(f)[a:b]==t,q
        assert norm(t) in np,('render',q)
    checks.append(q)
    for f,_,_ in mapping[q]:
        if f['json_pointer'] not in ['/final_action/public_message','/action/public_message']:continue
        src=ROOT/f['source'];dsrc=src.parent/'decisions.jsonl'
        if dsrc not in records:records[dsrc]=[json.loads(x) for x in dsrc.read_bytes().splitlines()]
        rows=records[dsrc];original=json.loads(src.read_bytes().splitlines()[f['jsonl_line_1based']-1])
        r=next(x for x in rows if x['phase']=='decision_resolved' and x['decision_id']==original['decision_id'])
        dn=int(r['decision_id'].rsplit('-',1)[1]);message=field(f);seen=[]
        for st in rows:
            if st['phase']=='decision_started' and st['player_id']!=r['player_id'] and int(st['decision_id'].rsplit('-',1)[1])>dn and message in json.dumps(st['prompt_payload'],ensure_ascii=False):
                seen.append({'recipient':st['player_id'],'decision_id':st['decision_id']});break
        assert seen,('missing claimed receipt',q)
        delivery.append({'quote':q,'first_later_other_player_request':seen[0]})
finance=json.loads((H/'data/finance_analysis.json').read_text())
for r in finance['necessary']:
    t=r['private_note'] or r['provider_reasoning'];assert norm(t) in np,('finance text',r['game'],r['decision'])
    src=ROOT/r['source_run']/'decisions.jsonl'
    if src not in records:records[src]=[json.loads(x) for x in src.read_bytes().splitlines()]
    original=next(d for d in records[src] if d['phase']=='decision_resolved' and d['decision_id']==r['decision_id'])
    if r['private_note']:assert original['final_action']['private_thought']==t
    else:assert original['attempts'][-1]['raw_response']['choices'][0]['message']['reasoning']==t
for kind in ['standard','recovery']:
    text=(H/f'data/{kind}_system_prompt.txt').read_text();assert norm(text) in np,kind
protected={}
for file in [ROOT/'docs/research_raw/paper_revision_2026-11-12/baseline_manifest.json',H/'data/source_hashes.json',H/'data/analysis_sources.json']:
    protected.update(json.loads(file.read_text()))
hash_checks={}
for p,h in protected.items():
    actual=sha(ROOT/p);assert actual==h,('changed source',p)
    hash_checks[p]={'expected':h,'actual':actual,'matched':True}
(H/'qa/protected_hash_checks.json').write_text(json.dumps(hash_checks,indent=2)+'\n')
# Additional exact source check on the highlighted payment, no state mutation.
game_map=json.loads((H/'data/game_map.json').read_text());g20=ROOT/game_map[19]['source_run']
ev=[json.loads(x) for x in (g20/'events.jsonl').read_bytes().splitlines()]
turn=[e for e in ev if e['turn_index']==108]
sales=sum(e['payload']['delta'] for e in turn if e['type']=='CASH_CHANGED' and e['payload'].get('reason')=='SELL_BUILDING')
mortgages=sum(e['payload']['delta'] for e in turn if e['type']=='CASH_CHANGED' and e['payload'].get('reason')=='MORTGAGE')
rent=[e for e in turn if e['type']=='RENT_PAID'][0]['payload']['amount']
assert (sales,mortgages,rent)==(700,665,1400)
log=(H/'build/manuscript.log').read_text()
diagnostics=[x for x in log.splitlines() if any(k in x for k in ['Overfull','Missing character','undefined','Warning'])]
assert not diagnostics,diagnostics
outside=[];blank=[];out=H/'qa/render';out.mkdir(exist_ok=True)
for i,p in enumerate(doc,1):
    if len(p.get_text().strip())<30:blank.append(i)
    for b in p.get_text('dict')['blocks']:
        for line in b.get('lines',[]):
            for s in line['spans']:
                if not p.rect.contains(pymupdf.Rect(s['bbox'])):outside.append([i,s['text']])
    assert not any(l['kind']==pymupdf.LINK_LAUNCH for l in p.get_links())
    p.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(out/f'page_{i:02}.png')
assert not outside,outside
assert not blank,blank
for start in range(1,len(doc)+1,4):
    sheet=Image.new('RGB',(1000,1350),'#e1e5e8');dr=ImageDraw.Draw(sheet)
    for n in range(start,min(start+4,len(doc)+1)):
        im=Image.open(out/f'page_{n:02}.png');im.thumbnail((475,640));j=n-start;x=15+(j%2)*495;y=25+(j//2)*665
        sheet.paste(im,(x,y));dr.text((x,y-15),str(n),fill='black')
    sheet.save(out/f'contact_{start:02}.png')
main='\n'.join((H/f'sections/{f}.tex').read_text() for f in sectionfiles[:-1])
main=re.sub(r'\\begin\{(table|figure)\}.*?\\end\{\1\}',' ',main,flags=re.S)
main=re.sub(r'\\(?:section|subsection|label|ref|cite|path|input|TranscriptQuote|TranscriptSource|TranscriptTitle)\*?(?:\[[^]]*\])?\{[^{}]*\}(?:\{[^{}]*\})?',' ',main)
main=re.sub(r'(?<!\\)\$[^$]*(?<!\\)\$',' ',main)
words=len(re.findall(r"\b[\w]+(?:['-][\w]+)*\b",main))
report={'pdf_sha256':sha(H/'manuscript.pdf'),'pages':len(doc),'approximate_main_prose_words':words,'word_count_scope':'Six main sections, excluding abstract, quotation cards, captions, tables, display figures, appendices and citation metadata. Command-stripped estimate, not venue word count.','incidents':incidents,'source_exact_rendered_quotes':checks,'quote_count':len(checks),'necessary_entry_fields_rendered':16,'protected_source_hashes_checked':len(protected),'diagnostics':diagnostics,'outside_page':outside,'blank_pages':blank,'g20_payment':{'sales':sales,'mortgages':mortgages,'rent':rent,'cash_before':49,'remainder':14}}
(H/'qa/document_checks.json').write_text(json.dumps(report,indent=2)+'\n')
(H/'qa/public_delivery_checks.json').write_text(json.dumps(delivery,indent=2)+'\n')
(H/'qa/pdf_text.txt').write_text(pdftext)
print(json.dumps(report,indent=2))
