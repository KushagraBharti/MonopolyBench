"""Read saved records and perform arithmetic only. Never import project code."""
from pathlib import Path
import collections as co
import hashlib
import itertools
import json
import re
import unicodedata
import numpy as np
import pymupdf

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[1]
ROOT = next(p for p in BASE.parents if (p / 'contracts').is_dir())
PAPER = BASE / 'integrated'
read = lambda p: json.loads(p.read_text())
jl = lambda p: [json.loads(s) for s in p.read_text().splitlines() if s]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
num = lambda r: int(r['decision_id'].rsplit('-', 1)[1])
norm = lambda s: ''.join(c.casefold() for c in unicodedata.normalize('NFKC', s) if c.isalnum())
games = read(PAPER / 'data/game_map.json')
records = {}
for g, run in games.items():
    p = ROOT / run
    # Read events, actions, decisions in the repository's required order.
    ev, ac, de = jl(p/'events.jsonl'), jl(p/'actions.jsonl'), jl(p/'decisions.jsonl')
    records[int(g)] = dict(events=ev, actions={num(r):r for r in ac},
        starts={num(r):r for r in de if r['phase']=='decision_started'},
        resolved={num(r):r for r in de if r['phase']=='decision_resolved'}, path=p)
result = {'scope':'Existing-file checks and arithmetic only; no engine, replay or model execution.'}
result['corpus'] = dict(events=sum(len(r['events']) for r in records.values()),
    decisions=sum(len(r['resolved']) for r in records.values()),
    attempts=sum(len(x['attempts']) for r in records.values() for x in r['resolved'].values()))

# All displayed quotation spans and full initial fields, from original files.
qs = {}
m = read(PAPER/'data/transcript_manifest.json')
for q in m['quotes']:
    qs[q['id']] = [(m['fields'][s['field_id']],s['span'],s['text']) for s in q['excerpts']]
for name, span_key, text_key in [('opus_quote_manifest','span_codepoints','excerpt')]:
    for q in read(PAPER/f'data/{name}.json')['quotes']:
        qs[q['id']] = [(q,q[span_key],q[text_key])]
for name, key in [('fable_quote_manifest','excerpts'),('additional_quote_manifest','spans'),('integration_quote_manifest','spans')]:
    for q in read(PAPER/f'data/{name}.json')['quotes']:
        qs[q['id']] = [(q,s['span'],s['text']) for s in q[key]]
prose = '\n'.join((PAPER/f'sections/{n}.tex').read_text() for n in ['scientific_introduction','study','finance','negotiation','conduct','interpretation','supplement'])
used = re.findall(r'\\TranscriptQuote\{([^}]+)\}',prose)
doc = pymupdf.open(PAPER/'manuscript.pdf')
pdf = norm('\n'.join(p.get_text(clip=pymupdf.Rect(0,0,p.rect.width,p.rect.height-40)) for p in doc))
def original(f):
    p = ROOT/f['source']
    assert sha(p)==f['source_sha256']
    v = json.loads(p.read_text().splitlines()[f['jsonl_line_1based']-1]) if f.get('jsonl_line_1based') else read(p)
    for k in f['json_pointer'].lstrip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~')
        v=v[int(k)] if isinstance(v,list) else v[k]
    assert hashlib.sha256(v.encode()).hexdigest()==f['field_sha256']
    return v
for qid in used:
    for f,(a,b),txt in qs[qid]:
        assert original(f)[a:b]==txt,(qid,'source span')
        assert norm(txt) in pdf,(qid,'PDF text')
fields=read(PAPER/'data/initial_text_manifest.json')['fields']
for f in fields:
    assert original(f)==f['text']
    assert norm(f['text']) in pdf
result['quote_checks']=dict(cards=len(used),full_initial_fields=len(fields),incidents=prose.count('\\TranscriptTitle{'),pages=len(doc))

# Reconcile every offer row with its original delivered prompt and applied action.
offers=read(PAPER/'data/offers.json')
offer_checks=[]
for o in offers:
    st=records[o['game']]['starts'][o['decision']]
    rr=records[o['game']]['resolved'][o['decision']]
    assert rr['final_action']['action']==o['response']
    assert records[o['game']]['actions'][o['decision']]['action']==rr['final_action']
    payload=st['prompt_payload']['action_state']
    assert ('accept_trade' in payload['available_actions'])==o['accept_available']
    scenario=payload['scenario']
    # The current offer is part of the actual recipient prompt, not the public log.
    incoming=scenario.get('current_offer') or scenario.get('offer')
    if incoming is None:
        incoming=next((v for v in scenario.values() if isinstance(v,dict) and 'offer' in v and 'request' in v),None)
    if incoming is not None:
        if 'if_you_accept' in incoming:
            assert incoming['if_you_accept']['you_receive']==o['offer'] and incoming['if_you_accept']['you_give']==o['request']
        else:
            assert incoming['offer']==o['offer'] and incoming['request']==o['request']
        offer_checks.append((o['game'],o['decision']))
result['offer_original_checks']=dict(responses=len(offers),delivered_terms=len(offer_checks),counts=dict(co.Counter(o['response'] for o in offers)),accept_available=sum(o['accept_available'] for o in offers))
def form(o):
    a,b=o['offer'],o['request']
    if a['properties'] and b['properties']: return 'Swap'
    if not a['get_out_of_jail_cards'] and not b['get_out_of_jail_cards']:
        if b['properties'] and not a['properties'] and a['cash']>0 and b['cash']==0:return 'Cash bid'
        if a['properties'] and not b['properties'] and b['cash']>0 and a['cash']==0:return 'Cash ask'
    return 'Other'
count=lambda rs:[len(rs)]+[sum(r['response']==a for r in rs) for a in ['accept_trade','counter_trade','reject_trade']]
ra=read(PAPER/'data/revision_analysis.json')
for stage in ['Opening','Later']:
    for f in ['Swap','Cash bid','Cash ask','Other']:
        for c in ['author_only','recipient_only','both','neither']:
            rs=[o for o in offers if o['accept_available'] and (o['exchange_index']==0)==(stage=='Opening') and form(o)==f and o['completion_cell']==c]
            assert count(rs)==ra['full_offer_table'][stage][f][c]
result['full_table_cells_checked']=32

# Financial resource sums, membership and first actions for all episodes.
board=read(ROOT/'contracts/data/board.json')
spaces={re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces']}
cost=board['house_cost_by_group']
episodes=read(PAPER/'data/liquidation_episodes.json')
req=co.Counter();paidreq=co.Counter();first=co.defaultdict(co.Counter);necessary=[];unlocked=[]
for e in episodes:
    st=records[e['game']]['starts'][e['first_decision']]
    s=st['prompt_payload'];you=s['game_state']['you'];owned=you['holdings']['owned'];opts=s['action_state']['scenario']['options']
    c=you['cash'];m0=sum(spaces[k]['price']//2 for k in opts['mortgageable_space_keys'])
    salvage=sum((5 if h['hotel'] else h['houses'])*cost.get(spaces[h['space_key']]['group'],0)//2 for h in owned)
    mm=sum(spaces[h['space_key']]['price']//2 for h in owned if not h['mortgaged'])
    assert c+salvage+mm==e['upper_bound']
    acts=[];absent=[]
    for did in e['decisions']:
        d=int(did.rsplit('-',1)[1]);rr=records[e['game']]['resolved'][d];a=rr['final_action'];acts.append(a['action'])
        assert records[e['game']]['actions'][d]['action']==a
        if a['action']=='mortgage_property' and a['args']['space_key'] not in opts['mortgageable_space_keys']:absent.append(a['args']['space_key'])
    assert acts==e['actions']
    payable=e['outcome']=='paid' or (e['game'],e['first_decision']) in [(12,190),(12,249),(17,234)]
    category='payable' if payable else 'above_bound' if e['upper_bound']<e['debt'] else 'menu_restricted'
    first[category][acts[0]]+=1
    if payable:
        requirement='initial_mortgages' if c+m0>=e['debt'] else 'sales' if c+m0+salvage>=e['debt'] else 'released_mortgages'
        req[requirement]+=1
        if e['outcome']=='paid':paidreq[requirement]+=1
    if c+m0+salvage<e['debt']<=e['upper_bound']:necessary.append([e['game'],e['first_decision'],e['outcome'],c+m0+salvage,e['upper_bound']])
    if absent and e['outcome']=='paid':unlocked.append([e['game'],e['first_decision'],absent])
result['finance']=dict(episodes=len(episodes),outcomes=dict(co.Counter(e['outcome'] for e in episodes)),requirements=req,paid_by_requirement=paidreq,first_actions=first,necessary=necessary,unlocked=unlocked,unlocked_mortgages=sum(len(x[2]) for x in unlocked))

# Independently reconstruct the conflict exclusion and exact block arithmetic.
all_opening=[o for o in offers if o['exchange_index']==0]
opening=[o for o in all_opening if o['accept_available']]
conf=set()
for o in all_opening:
    if o['author_model']!='Grok':continue
    rr=records[o['game']]['resolved'][int(str(o['offer_decision']).rsplit('-',1)[-1])]
    t=rr['attempts'][-1].get('assistant_content') or ''
    named=re.search(r'"name"\s*:\s*"([a-z_]+)"',t)
    if named and named[1]!='propose_trade':conf.add(o['thread_id'])
swaps=[o for o in opening if form(o)=='Swap']
pops={'All swaps':swaps,'No Grok authors':[o for o in swaps if o['author_model']!='Grok'],
    'No conflicting openings':[o for o in swaps if o['thread_id'] not in conf], 'Cash bids':[o for o in opening if form(o)=='Cash bid']}
pair=lambda rs:[count([o for o in rs if o['completion_cell']==c]) for c in ['author_only','neither']]
gap=lambda rs:100*(pair(rs)[0][3]/pair(rs)[0][0]-pair(rs)[1][3]/pair(rs)[1][0])
rng=np.random.default_rng(20261112)
sb=rng.integers(0,5,(20000,5));sr=rng.integers(0,4,(20000,5,4));hg=(4*sb[:,:,None]+sr).reshape(20000,20);ig=rng.integers(0,20,(20000,20))
stability={}
for name,rs in pops.items():
    bc=np.array([pair([o for o in rs if (o['game']-1)//4==b]) for b in range(5)])
    totals=bc[np.array(list(itertools.product(range(5),repeat=5)))].sum(axis=1)
    val=100*(totals[:,0,3]/totals[:,0,0]-totals[:,1,3]/totals[:,1,0])
    br=np.percentile(val,[2.5,97.5]).tolist()
    loo=[gap([o for o in rs if (o['game']-1)//4!=b]) for b in range(5)]
    blocks=[gap([o for o in rs if (o['game']-1)//4==b]) for b in range(5)]
    alternatives={};gc=np.array([pair([o for o in rs if o['game']==g]) for g in range(1,21)])
    for label,sample in [('Individual games',ig),('Blocks then games',hg)]:
        v=gc[sample].sum(axis=1);v=v[(v[:,0,0]>0)&(v[:,1,0]>0)]
        alternatives[label]=np.percentile(100*(v[:,0,3]/v[:,0,0]-v[:,1,3]/v[:,1,0]),[2.5,97.5]).tolist()
    expected=ra['stability'][name]
    assert np.allclose(br,expected['resampling_percentiles'])
    assert np.allclose(loo,expected['leave_one_block_out'])
    assert np.allclose(blocks,expected['block_gaps'])
    assert all(np.allclose(v,expected['alternative_resampling'][k]) for k,v in alternatives.items())
    stability[name]=dict(gap=gap(rs),blocks=blocks,loo=loo,intact_block_range=br,alternatives=alternatives)
result['stability']=stability
result['conflicting_opening_threads']=len(conf)

# Read the historical comparisons, without replaying anything.
result['replay_reports']={}
for g,r in records.items():
    result['replay_reports'][g]={f:read(r['path']/f) for f in ['artifact_replay_report.json','state_replay_report.json']}

(OUT/'saved_record_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['replay_reports']},indent=2))
