"""Read original incident contexts and retained temporal rows; no execution."""
import json,runpy
from collections import Counter
from pathlib import Path
N=runpy.run_path(str(Path(__file__).with_name('check_records.py')))
OUT,BASE,REPO,read,decision,records,runs = [N[k] for k in ['OUT','BASE','REPO','read','decision','records','runs']]
def strings(o,p=''):
    if isinstance(o,str):yield p,o
    elif isinstance(o,list):
        for i,v in enumerate(o):yield from strings(v,p+'/'+str(i))
    elif isinstance(o,dict):
        for k,v in o.items():yield from strings(v,p+'/'+k)

deliveries=[]
for g,d,targets in [(2,124,[125]),(2,127,[128]),(2,197,[198]),(15,168,[169]),(15,169,[170]),
    (15,174,[175]),(15,175,[176]),(7,42,[43]),(19,135,[136]),(20,96,[97]),(20,101,[102]),
    (13,250,[251]),(13,252,[253]),(18,431,[441,442]),(18,441,[442]),
    (11,255,[256]),(11,256,[257]),(11,257,[258]),(11,258,[259]),(3,363,[364]),(20,1,[4])]:
    r=decision(g,d,'decision_resolved');msg=r['final_action']['public_message']
    for t in targets:
        target=decision(g,t,'decision_started')
        matches=[p for p,v in strings(target['prompt_payload']) if msg in v]
        deliveries.append({'game':g,'source_decision':d,'recipient_decision':t,'recipient':target['player_id'],'message':msg,'payload_paths':matches})
        assert matches,(g,d,t)

original_contexts=[]
for g,ds in [(2,[124,127,197,198,215]),(3,[176,194,363,364]),(7,[42,43,339]),
 (12,[190,249]),(13,[250,251,252,253,307,311]),(15,[168,169,170,171,174,175]),
 (16,[159,247,248,249]),(17,[234]),(18,[83,421,431,441,442]),(19,[135,136]),(20,[1,4,95,96,97,100,101,102,327,336])]:
    for d in ds:
        start=decision(g,d,'decision_started');end=decision(g,d,'decision_resolved')
        p=start['prompt_payload']
        original_contexts.append({'game':g,'decision':d,'turn':start['turn_index'],'player':start['player_id'],
          'cash':p['game_state']['you']['cash'],'own':p['game_state']['you'],
          'action_state':p['action_state'],'final_action':end['final_action'],
          'attempts':[{k:a.get(k) for k in ['attempt_index','assistant_content','parsed_tool_call','outcome','validation_errors','response_condition']} for a in end['attempts']]})

events={}
for g in [2,13,15,18]:
    ev=read(runs[g]/'events.jsonl',True)
    if g==2: chosen=[e for e in ev if e['seq']==1566 or (e['turn_index']==72 and e['type'] in ['PLAYER_BANKRUPT','PROPERTY_PURCHASED','CASH_TRANSFERRED'])]
    elif g==13: chosen=[e for e in ev if (e['turn_index'] in [111,114,146,150]) and e['type'] in ['PLAYER_MOVED','PROPERTY_PURCHASED','RENT_PAID','CASH_TRANSFERRED','PLAYER_BANKRUPT']]
    elif g==15: chosen=[e for e in ev if e['type']=='PLAYER_BANKRUPT']
    else:chosen=[e for e in ev if e['type'] in ['PLAYER_BANKRUPT','RENT_PAID'] and e['turn_index']>150]
    events[g]=chosen

temporal=read(BASE/'data/agenda_temporal_rows.jsonl',True)
sample=Counter((r['game'],r['player_id']) for r in temporal)
assert len(sample)==80 and set(sample.values())=={3}
tempcounts=Counter(t for r in temporal for t in r['semantic_tags'])
report={'scope':__doc__,'deliveries':deliveries,'contexts':original_contexts,'events':events,
 'temporal':{'n':len(temporal),'player_game_counts':sorted(set(sample.values())),
  'tags':dict(tempcounts),'absent_private':sum(not r['fields']['private_thought']['present'] for r in temporal),
  'pool_sizes':[r['public_unflagged_pool_size'] for r in temporal],
  'interpretation':'Retained labels only, not new semantic coding.'},'source_sha256':N['sources']}
(OUT/'context_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('Deliveries matched:',len(deliveries),'Original decision contexts:',len(original_contexts),'Temporal:',report['temporal']['tags'])
