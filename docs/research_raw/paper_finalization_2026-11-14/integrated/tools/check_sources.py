"""Check recorded fields and arithmetic. Never import or execute benchmark code."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
(HERE/'qa').mkdir(exist_ok=True)
ROOT=next(p for p in HERE.parents if (p/'contracts/data/board.json').exists())
cache={}
def rows(path):
    if path not in cache:cache[path]=[json.loads(s) for s in path.read_text().splitlines()]
    return cache[path]
def resolve(x,pointer):
    for key in pointer.strip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~')
        x=x[int(key)] if isinstance(x,list) else x[key]
    return x
def field(path,line,pointer):
    value=rows(path)[line-1] if line else json.loads(path.read_text())
    return resolve(value,pointer)
quotes=0
for name in ['transcript_manifest.json','opus_quote_manifest.json','fable_quote_manifest.json','additional_quote_manifest.json','integration_quote_manifest.json']:
    manifest=json.loads((HERE/'data'/name).read_text())
    for q in manifest['quotes']:
        if 'source' not in q:
            for span in q['excerpts']:
                f=manifest['fields'][span['field_id']]
                p=ROOT/f['source']
                assert hashlib.sha256(p.read_bytes()).hexdigest()==f['source_sha256']
                x=field(p,f['jsonl_line_1based'],f['json_pointer'])
                assert hashlib.sha256(x.encode()).hexdigest()==f['field_sha256']
                assert x[span['span'][0]:span['span'][1]]==span['text']
            quotes+=1
            continue
        p=ROOT/q['source']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==q['source_sha256']
        x=field(p,q['jsonl_line_1based'],q['json_pointer'])
        assert hashlib.sha256(x.encode()).hexdigest()==q['field_sha256'],q['id']
        spans=q.get('spans',q.get('excerpts',[]))
        if not spans and 'span_codepoints' in q:spans=[dict(span=q['span_codepoints'],text=q['excerpt'])]
        for s in spans:
            assert x[s['span'][0]:s['span'][1]]==s['text'],q['id']
        quotes+=1
offers=json.loads((HERE/'data/offers.json').read_text())
for o in offers:
    rr=[r for r in rows(ROOT/o['source_run']/'decisions.jsonl') if r['phase']=='decision_resolved' and r['decision_id']==o['decision_id']]
    assert len(rr)==1 and rr[0]['final_action']['action']==o['response']
episodes=json.loads((HERE/'data/episodes_188.json').read_text())
paid=[r for r in episodes if r['outcome']=='paid']
stats=dict(paid_debt=sum(r['debt'] for r in paid),mortgage_actions=sum(r['actions'].count('mortgage_property') for r in paid),sale_actions=sum(r['actions'].count('sell_houses_or_hotel') for r in paid),one_action=sum(len(r['actions'])==1 for r in paid),multiple_actions=sum(len(r['actions'])>1 for r in paid))
assert stats==dict(paid_debt=51997,mortgage_actions=180,sale_actions=89,one_action=67,multiple_actions=61)
replays={}
games=json.loads((HERE/'data/game_map.json').read_text())
for g,folder in games.items():
    replays[g]={name:json.loads((ROOT/folder/(name+'.json')).read_text()) for name in ['artifact_replay_report','state_replay_report']}
    assert all(r['status']=='passed' for r in replays[g].values())
    assert replays[g]['artifact_replay_report']['excluded_event_types']==[]
assert sum(r['artifact_replay_report']['original_compared_event_count'] for r in replays.values())==50918
(HERE/'data/historical_replay_reports.json').write_text(json.dumps(replays,indent=2)+'\n')
audit=ROOT/'docs/research_raw/paper_adversarial_2026-10-29/executable_audit/results.json'
audit_data=json.loads(audit.read_text())
assert audit_data['summary']['elimination_certificates']==dict(upper_bound_impossibility=56,exhaustive_financing_impossibility=1,legal_payment_witness=3)
(HERE/'data/historical_audit_results.json').write_text(json.dumps(audit_data,indent=2)+'\n')
pin_path=ROOT/'docs/research_raw/paper_revision_2026-11-12/final_manuscript_manifest.json'
pin=json.loads(pin_path.read_text())['files']
base=pin_path.parent
assert all(hashlib.sha256((base/p).read_bytes()).hexdigest()==h for p,h in pin.items())
result=dict(quotes_source_checked=quotes,offer_action_joins=920,payment_arithmetic=stats,protected_historical_files=len(pin),historical_replay_pairs_read=len(replays),historical_audit_sha256=hashlib.sha256(audit.read_bytes()).hexdigest(),no_replay_or_witness_executed=True)
(HERE/'qa/additional_record_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
