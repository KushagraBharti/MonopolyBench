"""Astra reproduction of Fable's offer-form split using the earlier ledger.

Reads saved records only. No engine, model, synthetic scenario or new game.
"""
from pathlib import Path
from collections import Counter,defaultdict
from statistics import median
import json,re,hashlib

HERE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in HERE.parents if (p/'contracts').is_dir())
sources={}
def read(p,jsonl=False):
    blob=p.read_bytes();sources[str(p.relative_to(ROOT))]=hashlib.sha256(blob).hexdigest()
    return [json.loads(s) for s in blob.splitlines() if s] if jsonl else json.loads(blob)
offers=read(HERE/'data/offers.json')
legal=[r for r in offers if r['accept_available']]
def form(r):
    a,b=r['offer'],r['request']
    if a['properties'] and b['properties']:return 'swap'
    if b['properties'] and not a['properties'] and a['cash']>0 and b['cash']==0 and not a['get_out_of_jail_cards'] and not b['get_out_of_jail_cards']:return 'cash_bid'
    return 'other'
def count(rs):return {'n':len(rs),**dict(Counter(r['response'] for r in rs))}
def tab(rs):
    return {f:{c:count([r for r in rs if form(r)==f and r['completion_cell']==c])
               for c in ['author_only','neither','both','recipient_only']} for f in ['swap','cash_bid','other']}
opening=[r for r in legal if r['exchange_index']==0]
result={'opening':tab(opening),'later':tab([r for r in legal if r['exchange_index']>0]),
        'by_block':{b:tab([r for r in opening if (r['game']-1)//4+1==b]) for b in range(1,6)},
        'by_recipient':{m:tab([r for r in opening if r['recipient_model']==m]) for m in ['Sol','Gemini','Opus','Grok']}}
assert result['opening']['swap']['author_only']=={'n':116,'accept_trade':1,'counter_trade':20,'reject_trade':95}
assert result['opening']['swap']['neither']=={'n':72,'accept_trade':17,'counter_trade':18,'reject_trade':37}
assert result['opening']['cash_bid']['author_only']=={'n':70,'accept_trade':2,'counter_trade':26,'reject_trade':42}
assert result['opening']['cash_bid']['neither']=={'n':103,'accept_trade':4,'counter_trade':32,'reject_trade':67}

# Use the recorded proposing decision, rather than inferring it from adjacency.
runs={r['game']:r['source_run'] for r in offers}; starts={}; resolved={}
for game,run in runs.items():
    rows=read(ROOT/run/'decisions.jsonl',True)
    starts[game]={int(r['decision_id'].rsplit('-',1)[1]):r for r in rows if r['phase']=='decision_started'}
    resolved[game]={int(r['decision_id'].rsplit('-',1)[1]):r for r in rows if r['phase']=='decision_resolved'}
conflicts=[]
for r in offers:
    if r['exchange_index'] or r['author_model']!='Grok':continue
    k=r['offer_decision'];k=k if isinstance(k,int) else int(k.rsplit('-',1)[1])
    rec=resolved[r['game']][k]
    assert rec['final_action']['action']=='propose_trade'
    att=rec['attempts'][-1];text=att.get('assistant_content')
    if text is None:text=att.get('raw_response',{}).get('choices',[{}])[0].get('message',{}).get('content')
    match=re.search(r'"name"\s*:\s*"([a-z_]+)"',text or '')
    if match and match[1]!='propose_trade':conflicts.append({'thread':r['thread_id'],'game':r['game'],'decision':k,'content_action':match[1]})
conf={r['thread'] for r in conflicts};assert len(conf)==64
result['conflict_openings']=conflicts
result['without_conflict_openings']=tab([r for r in opening if r['thread_id'] not in conf])
assert result['without_conflict_openings']['swap']['author_only']['reject_trade']==93
assert result['without_conflict_openings']['swap']['neither']=={'n':43,'accept_trade':4,'counter_trade':13,'reject_trade':26}
def positive_swap_gap(t):
    a,b=t['swap']['author_only'],t['swap']['neither']
    return a.get('reject_trade',0)/a['n']>b.get('reject_trade',0)/b['n']
assert all(positive_swap_gap(t) for t in result['by_block'].values())
assert all(positive_swap_gap(t) for t in result['by_recipient'].values())
clean=[r for r in opening if r['thread_id'] not in conf]
result['without_conflict_by_block']={b:tab([r for r in clean if (r['game']-1)//4+1==b]) for b in range(1,6)}
result['without_conflict_by_recipient']={m:tab([r for r in clean if r['recipient_model']==m]) for m in ['Sol','Gemini','Opus','Grok']}
assert sum(positive_swap_gap(t) for t in result['without_conflict_by_block'].values())==4
assert all(positive_swap_gap(t) for t in result['without_conflict_by_recipient'].values())
result['cash_by_recipient']={m:{band:count([r for r in legal if r['completion_cell']=='author_only' and r['recipient_model']==m and pred(r['recipient_cash_before'])]) for band,pred in [('under100',lambda c:c<100),('300plus',lambda c:c>=300)]} for m in ['Sol','Gemini','Opus','Grok']}

# Compare terms within the previously defined holder/completer histories.
dyads=read(HERE/'data/paired_bargaining.json');paired=[]
index={(r['game'],r['decision']):r for r in offers}
for d in dyads:
    if not(d['settled'] and d.get('one_sided') and d.get('holder_declined_on_earlier_turn')):continue
    first=next(r for r in d['requests'] if r['written_by']=='completer' and r['response'] in ['reject_trade','counter_trade'] and r['turn']<d['settle_turn'])
    old=index[(d['game'],first['decision'])];new=index[(d['game'],d['settle_decision'])]
    def holder_cash_terms(r):
        n=r['offer']['cash']-r['request']['cash']
        return n if r['recipient']==d['holder'] else -n
    before,after=holder_cash_terms(old),holder_cash_terms(new)
    assert before==first['net_cash_to_holder'] and after==d['settle_net_cash_to_holder']
    paired.append({'game':d['game'],'group':d['group'],'before_decision':first['decision'],
                   'settle_decision':d['settle_decision'],'before_cash_terms':before,'after_cash_terms':after,
                   'price_change':'higher' if after>before else 'lower' if after<before else 'equal'})
assert len(paired)==14 and Counter(r['price_change'] for r in paired)=={'higher':8,'lower':4,'equal':2}
result['paired_terms']=paired

# The six same-mortgage-status overlaps and the exceptional G4 row.
prices=read(HERE/'data/single_deed_prices.json');groups=defaultdict(list)
for r in prices:
    if r['kind']=='ask':groups[(r['game'],r['author'],r['deed'])].append(r)
pairs=[]
for key,rs in groups.items():
    a=[r for r in rs if r['completes']];b=[r for r in rs if not r['completes']]
    if not a or not b:continue
    a.sort(key=lambda r:r['decision']);b.sort(key=lambda r:r['decision'])
    sign=lambda v:'higher' if v>0 else 'lower' if v<0 else 'equal'
    pairs.append({'key':key,'same_mortgage_status':len({r['mortgaged'] for r in rs})==1,
                  'median':sign(median(r['cash'] for r in a)-median(r['cash'] for r in b)),
                  'first':sign(a[0]['cash']-b[0]['cash']),
                  'completing':a,'other':b})
assert len(pairs)==7 and sum(p['same_mortgage_status'] for p in pairs)==6
assert Counter(p['median'] for p in pairs if p['same_mortgage_status'])=={'higher':4,'lower':1,'equal':1}
result['same_deed_pairs']=pairs

# G20: check the announced plan against original menus and payment events.
st=starts[20];recs=resolved[20]
ep=[recs[k]['final_action']['action'] for k in range(327,337)]
cash=[st[k]['prompt_payload']['game_state']['you']['cash'] for k in range(327,338)]
assert ep.count('sell_houses_or_hotel')==2 and ep.count('mortgage_property')==8
assert cash[0]==49 and cash[-1]==14
events=read(ROOT/runs[20]/'events.jsonl',True)
turn=[r for r in events if r['turn_index']==108]
sale=sum(r['payload']['delta'] for r in turn if r['type']=='CASH_CHANGED' and r['payload'].get('reason')=='SELL_BUILDING')
mortgage=sum(r['payload']['delta'] for r in turn if r['type']=='CASH_CHANGED' and r['payload'].get('reason')=='MORTGAGE')
rent=[r for r in turn if r['type']=='RENT_PAID']
assert sale==700 and mortgage==665 and rent[0]['payload']['amount']==1400
assert 49+sale+mortgage==1414
result['g20_payment']={'actions':ep,'cash_at_prompts':cash,'sales':sale,'mortgages':mortgage,'rent':1400,'remaining':14,
                      'notes':{k:recs[k]['final_action']['private_thought'] for k in [325,327,329,336]}}
result['sources']=sources
(HERE/'qa/fable_cross_review_reproduction.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['opening','without_conflict_openings','cash_by_recipient','g20_payment']},indent=2))
