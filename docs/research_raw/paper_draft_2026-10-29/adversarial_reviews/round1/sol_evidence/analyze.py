import json, hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
manifest=ROOT/'docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json'
games=json.loads(manifest.read_text())['games']
counts=Counter(); rows=[]; sources=[]
for g in games:
    p=ROOT/g['run']/'events.jsonl'
    es=[json.loads(l) for l in p.read_text().splitlines()]
    c=Counter(e['type'] for e in es); counts.update(c)
    rows.append({'game':g['game'],'events':len(es),'decisions':c['LLM_DECISION_REQUESTED'],'trades':c['TRADE_ACCEPTED']})
    sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
p=ROOT/'docs/research_raw/paper_phase2_2026-10-28/core_review/sol/build_recovery_audit.json'
x=json.loads(p.read_text()); checked=[]
def allocation(plan):
    c=Counter()
    for a in plan:c[(a['space_key'],a['kind'])]+=a['count']
    return c
for d in x['defaults']:
    if 'opus' not in d['model']:continue
    for t in d['plan_tests']:
        r=t['test']; checked.append({'game':d['game'],'decision':d['decision_id'],'same_multiset':allocation(t['received_plan'])==allocation(r['interleaved_plan']),'retained_legal':r['legal'],'cash_delta':r['before_cash']-r['after_cash']})
result={'raw_event_counts':dict(counts),'games':rows,'construction_witness_record_checks':checked,'sources':sources,'scope':'Raw event recount; retained witness algebra, not fresh engine execution.'}
(OUT/'analysis_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'events':sum(r['events'] for r in rows),'decisions':counts['LLM_DECISION_REQUESTED'],'trades':counts['TRADE_ACCEPTED'],'witnesses':len(checked),'same_multiset':sum(r['same_multiset'] for r in checked)},indent=2))
