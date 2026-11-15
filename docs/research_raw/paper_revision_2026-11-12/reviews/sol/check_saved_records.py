"""Read saved observations only. No engine import, execution, or provider calls."""
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
import re
import statistics

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ROOT = BASE.parents[2]
SOURCES = {}

def read(p, lines=False):
    p = Path(p)
    data = p.read_bytes()
    SOURCES[str(p.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return [json.loads(x) for x in data.splitlines() if x] if lines else json.loads(data)

manifest = read(BASE / 'four_draft_manifest.json')
hashes = []
for name, expected in manifest['files'].items():
    actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
    hashes.append({'path': name, 'expected': expected, 'actual': actual, 'matches': actual == expected})
assert all(r['matches'] for r in hashes)
baseline = read(BASE/'baseline_manifest.json')
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in baseline.items())

maps = read(BASE / 'full_drafts/sol/data/game_map.json')
records = {}
replays = []
for g in maps:
    run = ROOT / g['source_run']
    rs = read(run / 'decisions.jsonl', True)
    records[g['game']] = {phase: {int(r['decision_id'].rsplit('-', 1)[1]): r for r in rs if r['phase'] == phase}
                          for phase in ['decision_started', 'decision_resolved']}
    for mode in ['artifact', 'state']:
        r = read(run / (mode + '_replay_report.json'))
        assert r['status'] == 'passed' and r['original_canonical_hash'] == r['replay_canonical_hash']
        replays.append({'game': g['game'], 'mode': mode, 'count': r['original_compared_event_count'],
                        'excluded': r['excluded_event_types']})

board = read(ROOT / 'contracts/data/board.json')
spaces = {re.sub('[^A-Z0-9]+', '_', s['name'].upper()).strip('_'): s for s in board['spaces']}
costs = board['house_cost_by_group']
episodes = read(BASE / 'full_drafts/sol/data/liquidation_episodes.json')
fable = {(e['game'], e['first_decision']): e for e in read(BASE / 'full_drafts/fable_5_2/data/b2_debt_episodes.json')}
debt = []
for e in episodes:
    g, k = e['game'], e['first_decision']
    st = records[g]['decision_started'][k]
    r = records[g]['decision_resolved'][k]
    p = st['prompt_payload']; you = p['game_state']['you']
    opts = p['action_state']['scenario']['options']
    owned = you['holdings']['owned']; listed = opts['mortgageable_space_keys']
    c = you['cash']
    s = sum((5 if h['hotel'] else h['houses']) * costs.get(spaces[h['space_key']]['group'], 0) // 2 for h in owned)
    m0 = sum(spaces[x]['price'] // 2 for x in listed)
    m1 = sum(spaces[h['space_key']]['price'] // 2 for h in owned if not h['mortgaged'] and h['space_key'] not in listed)
    bound = c + s + m0 + m1
    assert bound == e['upper_bound'] == fable[g,k]['bound']
    assert r['final_action']['action'] == e['actions'][0] == fable[g,k]['first_action']
    cls = 'above_bound' if bound < e['debt'] else 'menu_restricted' if (g,k)==(7,338) else 'payable'
    tier = 'listed' if c+m0 >= e['debt'] else 'sales' if c+m0+s >= e['debt'] else 'released' if bound >= e['debt'] else 'above'
    last = r['attempts'][-1]
    provider = last.get('raw_response', {}).get('choices', [{}])[0].get('message', {}).get('reasoning')
    memory = json.dumps(p['game_state'].get('memory', {}), ensure_ascii=False)
    extra = []
    for did in e['decisions']:
        rr = records[g]['decision_resolved'][int(did.rsplit('-',1)[1])]
        a = rr['final_action']
        if a['action'] == 'mortgage_property' and a['args']['space_key'] not in listed:
            extra.append(a['args']['space_key'])
    debt.append({'game':g,'decision':k,'model':fable[g,k]['model'],'class':cls,'tier':tier,'cash':c,'salvage':s,'listed':m0,'released':m1,'bound':bound,'debt':e['debt'],
                 'outcome':e['outcome'],'first_action':r['final_action']['action'],'fallback':r['fallback_used'],
                 'sale_offered':bool(opts['sellable_building_space_keys']),'mortgage_offered':bool(listed),'actions':len(e['actions']),
                 'released_mortgages_used':extra,'note':r['final_action'].get('private_thought'),'provider':provider,
                 'memory_dollar_amounts':re.findall(r'\$[0-9][0-9,]*',memory)})
necessary = [r for r in debt if r['class']=='payable' and r['tier']=='released']
assert len(necessary)==16
g20_events=read(ROOT/maps[19]['source_run']/'events.jsonl',True)
g20_cash=[e['payload'] for e in g20_events if e['turn_index']==108 and e['type']=='CASH_CHANGED' and e['payload']['player_id']=='p3']
g20_amounts={reason:sum(p['delta'] for p in g20_cash if p['reason']==reason) for reason in ['SELL_BUILDING','MORTGAGE','RENT']}
assert g20_amounts=={'SELL_BUILDING':700,'MORTGAGE':665,'RENT':-1400}
assert records[20]['decision_started'][337]['prompt_payload']['game_state']['you']['cash']==14
first = {c: dict(Counter(r['first_action'] for r in debt if r['class']==c)) for c in ['payable','above_bound','menu_restricted']}
above = [r for r in debt if r['class']=='above_bound']
first_details = [{'game':r['game'],'decision':r['decision'],'action':r['first_action'],'sale_offered':r['sale_offered'],'mortgage_offered':r['mortgage_offered'],'fallback':r['fallback']} for r in above]

offers = read(BASE / 'full_drafts/sol/data/offers.json')
def form(r):
    a,b = r['offer'],r['request']
    if a['properties'] and b['properties']: return 'swap'
    if not a['get_out_of_jail_cards'] and not b['get_out_of_jail_cards']:
        if b['properties'] and not a['properties'] and a['cash']>0 and b['cash']==0: return 'cash_bid'
        if a['properties'] and not b['properties'] and b['cash']>0 and a['cash']==0: return 'cash_ask'
    return 'other'
def counts(rs): return {'n':len(rs), **dict(Counter(r['response'] for r in rs))}
legal = [r for r in offers if r['accept_available']]
opening = [r for r in legal if r['exchange_index']==0]
tables = {stage:{f:{c:counts([r for r in rs if form(r)==f and r['completion_cell']==c]) for c in ['author_only','recipient_only','both','neither']}
                 for f in ['swap','cash_bid','cash_ask','other']} for stage,rs in [('opening',opening),('later',[r for r in legal if r['exchange_index']>0])]}
strata = {side:{m:{f:{c:counts([r for r in opening if r[side+'_model']==m and form(r)==f and r['completion_cell']==c])
                       for c in ['author_only','neither']} for f in ['swap','cash_bid']} for m in ['Sol','Gemini','Opus','Grok']} for side in ['author','recipient']}
semantic = [r for r in legal if r['completion_cell'] in ['recipient_only','both'] and r['response']=='reject_trade']
assert len(semantic)==74
capacity={}
for f in ['swap','cash_bid']:
    rows=[r for r in opening if form(r)==f and r['completion_cell']=='author_only']
    def bucket(r):
        n=r['author_cash_if_accepted']/min(costs[g] for g in r['author_new_groups'])
        return '0' if n<1 else '1-2' if n<3 else '3-5' if n<6 else '6+'
    capacity[f]={b:counts([r for r in rows if bucket(r)==b]) for b in ['0','1-2','3-5','6+']}
def list_value(r):
    return r['offer']['cash']-r['request']['cash']+sum(spaces[k]['price'] for k in r['offer']['properties'])-sum(spaces[k]['price'] for k in r['request']['properties'])
list_values={c:{'median':statistics.median(list_value(r) for r in opening if form(r)=='swap' and r['completion_cell']==c),
                'positive':counts([r for r in opening if form(r)=='swap' and r['completion_cell']==c and list_value(r)>0])} for c in ['author_only','neither']}
conflicts = set()
for r in opening:
    if r['author_model']!='Grok': continue
    d = records[r['game']]['decision_resolved'][r['offer_decision']]
    content = d['attempts'][-1].get('assistant_content') or ''
    m = re.search(r'"name"\s*:\s*"([a-z_]+)"',content)
    if m and m[1]!='propose_trade': conflicts.add(r['thread_id'])
def gap(rs):
    a,b = [[r for r in rs if r['completion_cell']==c] for c in ['author_only','neither']]
    return 100*(sum(r['response']=='reject_trade' for r in a)/len(a)-sum(r['response']=='reject_trade' for r in b)/len(b))
def percentile(xs,q):
    xs=sorted(xs);p=(len(xs)-1)*q;lo=int(p);hi=min(lo+1,len(xs)-1)
    return xs[lo]+(xs[hi]-xs[lo])*(p-lo)
resampling = {}
for name,rs in [('swaps',[r for r in opening if form(r)=='swap']),('no_grok',[r for r in opening if form(r)=='swap' and r['author_model']!='Grok']),
                ('no_conflicts',[r for r in opening if form(r)=='swap' and r['thread_id'] not in conflicts]),('cash_bids',[r for r in opening if form(r)=='cash_bid'])]:
    blocks=[[r for r in rs if (r['game']-1)//4==b] for b in range(5)]
    samples=[gap([r for b in draw for r in blocks[b]]) for draw in itertools.product(range(5), repeat=5)]
    resampling[name]={'point':gap(rs),'block_gaps':[gap(b) for b in blocks], 'percentiles':[percentile(samples,q) for q in [.025,.975]],
                      'leave_one_out':[gap([r for r in rs if (r['game']-1)//4 != b]) for b in range(5)]}

qchecks=[]
for author in ['astra','sol','opus','fable_5_2']:
    folder=BASE/'full_drafts'/author/'data'
    for path in sorted(set(folder.glob('*quote*manifest*.json')) | set(folder.glob('*transcript*manifest*.json'))):
        obj=read(path)
        for q in obj.get('quotes',[]):
            if 'json_pointer' not in q: continue
            source=ROOT/q['source']; raw=source.read_bytes()
            SOURCES[str(source.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
            assert hashlib.sha256(raw).hexdigest()==q['source_sha256']
            field=json.loads(raw.splitlines()[q['jsonl_line_1based']-1])
            for key in q['json_pointer'].strip('/').split('/'):
                field=field[int(key)] if isinstance(field,list) else field[key]
            assert hashlib.sha256(field.encode()).hexdigest()==q['field_sha256']
            spans=q.get('spans')
            if spans:
                for sp in spans:
                    start,end=sp.get('span',sp.get('span_codepoints'))
                    assert field[start:end]==sp.get('text',sp.get('excerpt'))
            elif 'span_codepoints' in q:
                start,end=q['span_codepoints'];assert field[start:end]==q['excerpt']
            qchecks.append({'author':author,'manifest':path.name,'id':q['id'],'source_field_and_span_match':True})

ints=Counter()
intent_files=0
request_settings=Counter()
for coll in sorted((ROOT/'saved_games').glob('railway-research-*-games-2026-10-*')):
    for p in sorted(coll.glob('game-*/cloud/calls/*.intent.json')):
        obj=read(p); payload=obj.get('payload') or obj.get('request_payload') or obj.get('request') or obj
        if 'model' not in payload:
            # Historical intent stores the actual outgoing body in request_body.
            payload=obj.get('request_body',payload)
        ints[(payload.get('model'),payload.get('tool_choice'))]+=1;intent_files+=1
        request_settings[(json.dumps(payload.get('reasoning'),sort_keys=True),payload.get('parallel_tool_calls'),
                          'temperature' in payload,'top_p' in payload,'max_tokens' in payload)]+=1

usage={}
for g in records.values():
    for r in g['decision_resolved'].values():
        model=r['openrouter_model_id'];u=usage.setdefault(model,{'attempts':0,'reasoning_tokens':[],'completion_tokens':[]})
        for a in r['attempts']:
            u['attempts']+=1
            raw=a.get('raw_response') or {};us=raw.get('usage') or {}
            n=(us.get('completion_tokens_details') or {}).get('reasoning_tokens')
            if n is not None:u['reasoning_tokens'].append(n)
            if us.get('completion_tokens') is not None:u['completion_tokens'].append(us['completion_tokens'])
for u in usage.values():
    for field in ['reasoning_tokens','completion_tokens']:
        ns=u.pop(field);u[field+'_n']=len(ns);u[field+'_mean_where_reported']=statistics.mean(ns) if ns else None
        u[field+'_zero']=ns.count(0)

# Opus manifest uses decision index and channel rather than JSON pointers.
for q in read(BASE/'full_drafts/opus/data/quote_manifest.json')['quotes']:
    r=records[q['game']]['decision_resolved'][q['decision']]
    if q['field'] in ['private_thought','public_message']:
        field=r['final_action'][q['field']]
    elif q['field'] in ['content','assistant_content']:
        field=r['attempts'][q['selected_attempt']]['assistant_content']
    else:
        field=r['attempts'][q['selected_attempt']]['raw_response']['choices'][0]['message']['reasoning']
    assert hashlib.sha256(field.encode()).hexdigest()==q['field_sha256']
    for span in q['text'].split(' [...] '):
        assert span in field,(q['id'],span)
    qchecks.append({'author':'opus','manifest':'quote_manifest.json','id':q['id'],'source_field_and_span_match':True})

# G18 text and selected contextual delivery, checked in actual stored requests.
g18=[]
for k,r in records[18]['decision_resolved'].items():
    if 421<=k<=461 and 'opus' in r['openrouter_model_id']:
        fields=[r['final_action'].get('private_thought') or '',r['final_action'].get('public_message') or '']
        for a in r['attempts']:
            fields += [a.get('assistant_content') or '',a.get('raw_response',{}).get('choices',[{}])[0].get('message',{}).get('reasoning') or '']
        g18.append({'decision':k,'inheritance_terms':re.findall(r'inherit\w*|estate|creditor',' '.join(fields),re.I)})
receipts=[]
for g,k,recipient in [(15,175,'Sol'),(19,135,'Sol'),(7,42,'Sol'),(13,250,'Opus'),(13,252,'Opus'),(20,96,'Grok'),(20,101,'Grok'),(18,431,'Sol'),(18,441,'Opus'),(18,442,'Sol')]:
    msg=records[g]['decision_resolved'][k]['final_action']['public_message']
    hits=[j for j,st in records[g]['decision_started'].items() if j>k and recipient.lower() in st['player_name'].lower() and msg in json.dumps(st['prompt_payload'],ensure_ascii=False)]
    assert hits,(g,k,recipient)
    receipts.append({'game':g,'decision':k,'recipient':recipient,'first_request':min(hits)})

out={'scope':'Saved-record reading, arithmetic and resampling only. No new evaluation.',
     'frozen_hashes':{'entries':len(hashes),'all_match':True},'debt_first_actions':first,'above_bound_first_details':first_details,
     'baseline_hashes':{'entries':len(baseline),'all_match':True},'capacity_bins':capacity,'list_value_checks':list_values,
     'debt_tiers':{t:dict(Counter(r['outcome'] for r in debt if r['class']=='payable' and r['tier']==t)) for t in ['listed','sales','released']},
     'necessary':necessary,'released_use_episodes':sum(bool(r['released_mortgages_used']) and r['outcome']=='paid' for r in debt),
     'g20_payment_amounts':g20_amounts,'g20_next_cash':14,
     'released_mortgages_used':sum(len(r['released_mortgages_used']) for r in debt if r['outcome']=='paid'),
     'one_action_payments':sum(r['outcome']=='paid' and r['actions']==1 for r in debt),
     'offer_tables':tables,'strata':strata,'offer_totals':counts(offers),'legal_offers':len(legal),'semantic_population':dict(Counter(r['completion_cell'] for r in semantic)),
     'block_resampling':resampling,'quote_checks':qchecks,'intent_files':intent_files,'intent_tool_choice':[[list(k),v] for k,v in ints.items()],
     'request_settings':[[list(k),v] for k,v in request_settings.items()],'reported_usage':usage,
     'g18_text_screen':g18,'receipts':receipts,'replays':replays,'sources':SOURCES}
(HERE/'saved_record_checks.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
(HERE/'frozen_hash_check.json').write_text(json.dumps({'phase':'cross-review verification','entries':hashes},indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['frozen_hashes','debt_first_actions','debt_tiers','released_use_episodes','released_mortgages_used','one_action_payments','offer_totals','legal_offers','semantic_population','intent_files','intent_tool_choice']},indent=2))
print('Quote checks',len(qchecks),'sources',len(SOURCES))
