"""Independent checks of Opus cross-review additions; saved records only."""
from pathlib import Path
from collections import Counter
import json,hashlib,re

HERE=Path(__file__).resolve().parents[1]
REPO=next(p for p in HERE.parents if (p/'contracts').is_dir())
hashes={}
def read(p,lines=False):
    b=p.read_bytes();hashes[str(p.relative_to(REPO))]=hashlib.sha256(b).hexdigest()
    return [json.loads(x) for x in b.splitlines()] if lines else json.loads(b)

offers=read(HERE/'data/offers.json')
legal=[r for r in offers if r['accept_available']]
def counts(rs):
    return {'n':len(rs),**dict(Counter(r['response'] for r in rs))}
def compare(rs):
    return {k:counts([r for r in rs if r['completion_cell']==cell and r['request']['properties']])
            for k,cell in [('completion','author_only'),('other','neither')]}
op=[r for r in legal if r['exchange_index']==0]
out={'opening':compare(op),'later':compare([r for r in legal if r['exchange_index']>0]),
     'by_block':{b:compare([r for r in op if (r['game']-1)//4+1==b]) for b in range(1,6)},
     'by_recipient':{m:compare([r for r in op if r['recipient_model']==m]) for m in ['Sol','Gemini','Opus','Grok']}}
out['standard_opening_cash']={k:compare([r for r in op if r['recipient_model']!='Opus' and cond(r['recipient_cash_before'])])
                              for k,cond in [('<100',lambda c:c<100),('100-299',lambda c:100<=c<300),('300+',lambda c:c>=300)]}
assert out['opening']['completion']['reject_trade']==138 and out['opening']['other']['reject_trade']==105
assert out['opening']['other']['n']==176

board=read(REPO/'contracts/data/board.json')
spaces={re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces']}
eps=read(HERE/'data/liquidation_episodes.json')
runs={r['game']:r['source_run'] for r in offers}
records={}
for g,p in runs.items():
    rows=read(REPO/p/'decisions.jsonl',True)
    records[g]={'start':{r['decision_id']:r for r in rows if r['phase']=='decision_started'},
                'end':{r['decision_id']:r for r in rows if r['phase']=='decision_resolved'}}
unlocked=[]
for ep in eps:
    if ep['outcome']!='paid':continue
    rec=records[ep['game']];first=rec['start'][ep['decisions'][0]]
    opt=first['prompt_payload']['action_state']['scenario']['options']
    initial=set(opt['mortgageable_space_keys'])
    holdings=first['prompt_payload']['game_state']['you']['holdings']['owned']
    builtgroups={spaces[h['space_key']]['group'] for h in holdings if h['houses'] or h['hotel']}
    sales=[];rows=[]
    for did in ep['decisions']:
        r=rec['end'][did]['final_action']
        if r['action']=='sell_houses_or_hotel':sales.append(did)
        if r['action']=='mortgage_property':
            key=r['args']['space_key']
            if key not in initial:
                current=rec['start'][did]['prompt_payload']['action_state']['scenario']['options']['mortgageable_space_keys']
                assert sales and key in current and spaces[key]['group'] in builtgroups
                rows.append({'decision':did,'deed':key,'mortgage_value':spaces[key]['price']//2,'earlier_sales':sales[:]})
    if rows:unlocked.append({'game':ep['game'],'first_decision':ep['first_decision'],'model':ep['model'],'rows':rows})
out['unlocked_collateral']={'episodes':len(unlocked),'actions':sum(len(r['rows']) for r in unlocked),
                           'by_model':dict(Counter(r['model'] for r in unlocked)),'rows':unlocked}
assert len(unlocked)==19 and sum(len(r['rows']) for r in unlocked)==33
notes=[]
for g,k in [(12,190),(17,234)]:
    rec=records[g];did=next(d for d in rec['start'] if int(d.split('-')[-1])==k)
    d=rec['start'][did];r=rec['end'][did];opts=d['prompt_payload']['action_state']['scenario']['options']
    hs=d['prompt_payload']['game_state']['you']['holdings']['owned']
    initial=set(opts['mortgageable_space_keys'])
    collateral=[h['space_key'] for h in hs if not h['mortgaged'] and h['space_key'] not in initial]
    notes.append({'game':g,'decision':k,'cash':d['prompt_payload']['game_state']['you']['cash'],
                  'debt':d['prompt_payload']['action_state']['scenario']['owed_amount'],
                  'listed_mortgages':sorted(initial),'unlisted_unmortgaged':collateral,
                  'unlisted_mortgage_value':sum(spaces[key]['price']//2 for key in collateral),
                  'applied_action':r['final_action']})
assert [n['unlisted_mortgage_value'] for n in notes]==[340,375]
out['payable_elimination_notes']=notes
out['sources']=hashes
(HERE/'qa/unlocked_collateral_check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['sources','by_block','by_recipient','unlocked_collateral']},indent=2))
print('unlocked',out['unlocked_collateral']['episodes'],out['unlocked_collateral']['actions'],out['unlocked_collateral']['by_model'])
