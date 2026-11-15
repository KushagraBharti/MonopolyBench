"""Independent arithmetic checks of Fable's new existing-record claims.

Reads the older offer ledger and canonical events. No engine, simulation,
provider call, new annotation, or evaluation. Writes only in this review.
"""
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = HERE.parents[4]
sources = {}

def read(path, lines=False):
    path = Path(path)
    raw = path.read_bytes()
    sources[str(path.relative_to(REPO))] = hashlib.sha256(raw).hexdigest()
    return [json.loads(s) for s in raw.splitlines()] if lines else json.loads(raw)

offers = read(REPO / 'docs/research_raw/paper_rewrite_2026-11-10/data/agenda_offers.json')
fbase = BASE / 'full_drafts/fable_5_2/data'
fresh = read(fbase / 'a2_offer_ledger.json')
fk = {(r['game'], r['decision']): r for r in fresh}
fields = ['response', 'accept_available', 'author', 'recipient', 'completion_cell', 'author_new_groups', 'recipient_new_groups',
          'author_cash_before', 'recipient_cash_before', 'net_cash_author_to_recipient', 'turn', 'exchange_index']
for r in offers:
    f = fk[r['game'], r['decision']]
    assert all(r[k] == f[k] for k in fields)
    assert r['offer'] == f['author_gives'] and r['request'] == f['recipient_gives']

def tab(xs):
    return {'n': len(xs), 'responses': dict(Counter(r['response'] for r in xs)),
            'games': sorted({r['game'] for r in xs}), 'threads': len({r['thread_id'] for r in xs})}

def cash_tabs(xs):
    return {'under100': tab([r for r in xs if r['recipient_cash_before'] < 100]),
            '100to299': tab([r for r in xs if 100 <= r['recipient_cash_before'] < 300]),
            '300plus': tab([r for r in xs if r['recipient_cash_before'] >= 300])}

legal = [r for r in offers if r['accept_available']]
ao = [r for r in legal if r['completion_cell'] == 'author_only']
ne = [r for r in legal if r['completion_cell'] == 'neither' and r['request']['properties']]
out = {'offer_rows_compared': len(offers), 'cash': cash_tabs(ao), 'noncompleting_cash': cash_tabs(ne),
       'cash_by_model': {m: cash_tabs([r for r in ao if r['recipient_model'] == m]) for m in ['Sol','Gemini','Opus','Grok']},
       'cash_by_stage': {s: cash_tabs([r for r in ao if (r['exchange_index'] == 0) == s]) for s in [True,False]},
       'cash_by_block': {b: cash_tabs([r for r in ao if (r['game']-1)//4+1 == b]) for b in range(1,6)}}

# Reconstruct directed game/player-pair/group histories from the earlier ledger.
dyads = defaultdict(list)
for r in legal:
    for role, other in [('author','recipient'), ('recipient','author')]:
        for group in r[role+'_new_groups']:
            dyads[r['game'], r[role], r[other], group].append((r, role, other))
fd = read(fbase / 'a6_dyads.json')
fdk = {(d['game'], d['completer'], d['holder'], d['group']): d for d in fd}
assert dyads.keys() == fdk.keys()
changing, sales = [], []
for key, vals in dyads.items():
    vals.sort(key=lambda x: x[0]['decision'])
    f = fdk[key]
    assert [r['decision'] for r,_,_ in vals] == [x['decision'] for x in f['requests']]
    accepted = [(r, role, other) for r,role,other in vals if r['response'] == 'accept_trade']
    assert bool(accepted) == f['settled']
    if not accepted:
        continue
    assert len(accepted) == 1
    a, role, other = accepted[0]
    assert a['decision'] == f['settle_decision'] and a[other+'_cash_before'] == f['settle_holder_cash']
    if a['completion_cell'] == 'both':
        continue
    sales.append((key,a,role,other))
    earlier = [(r, rr, oo) for r,rr,oo in vals if r['turn'] < a['turn'] and rr == 'author' and r['response'] != 'accept_trade']
    if earlier:
        e,_,holder = earlier[0]
        changing.append({'game':key[0], 'buyer':key[1], 'seller':key[2], 'group':key[3],
                         'seller_model':a[other+'_model'], 'first_decision':e['decision'], 'settle_decision':a['decision'],
                         'first_cash':e[holder+'_cash_before'], 'settle_cash':a[other+'_cash_before'],
                         'first_net_cash':e['net_cash_author_to_recipient'],
                         'settle_net_cash':a['net_cash_author_to_recipient']*(1 if role=='author' else -1),
                         'first_deeds':e['request']['properties'],
                         'settle_deeds':a['request' if role=='author' else 'offer']['properties'],
                         'first_reciprocal_deeds':e['offer']['properties'],
                         'settle_reciprocal_deeds':a['offer' if role=='author' else 'request']['properties'],
                         'turn_gap':a['turn']-e['turn']})
assert len(sales) == 43 and len(changing) == 14
out['pair_counts'] = {'all':len(dyads),'settled':sum(d['settled'] for d in fd),'one_sided':len(sales)}
out['decline_to_sale'] = {'n':len(changing), 'cash_fell':sum(r['settle_cash']<r['first_cash'] for r in changing),
                         'median_first':median(r['first_cash'] for r in changing),'median_sale':median(r['settle_cash'] for r in changing),
                         'same_deeds_transferred':sum(sorted(r['first_deeds'])==sorted(r['settle_deeds']) and sorted(r['first_reciprocal_deeds'])==sorted(r['settle_reciprocal_deeds']) for r in changing),
                         'rows':changing}

# Independently count subsequent building events in the recorded streams.
events = {}
for r in offers:
    if r['game'] not in events:
        events[r['game']] = read(REPO/r['source_run']/'events.jsonl', lines=True)
conv = read(fbase/'a7_conversion.json')['seller_conversion']['rows']
ck = {(r['game'],r['seller_model'],r['group']):r for r in conv}
checked = []
for key,a,role,other in sales:
    seller = a[other]
    m = a[other+'_model']
    f = ck[a['game'],m,key[3]]
    built = {w:sum(e['payload'].get('count',1) for e in events[a['game']]
                 if e['seq']>a['response_seq'] and 0 <= e['turn_index']-a['turn']<=w
                 and e['type'] in ['HOUSE_BUILT','HOTEL_BUILT'] and e['payload']['player_id']==seller)
             for w in [4,8,12]}
    assert built == {int(k):v for k,v in f['houses_built_within'].items()}
    assert a[other+'_cash_before'] == f['seller_cash']
    # Use fresh-offer winner identity only as a cross-check; ledger has source game outcome.
    assert fk[a['game'],a['decision']][other+'_is_winner'] == f['seller_won']
    checked.append({**f,'seller':seller,'decision':a['decision'], 'built8':built[8]>0,
                    'other_deeds_received':a['offer' if role=='author' else 'request']['properties']})
sets = {k:{(r['game'],r['seller_model']) for r in checked if r['built8']==k} for k in [True,False]}
out['seller_conversion'] = {'rows_checked':len(checked), 'grouped_player_games':{str(k):len(v) for k,v in sets.items()},
                            'player_games_in_both':sorted(sets[True]&sets[False]),
                            'built_wins':sum(r['seller_won'] for r in checked if r['built8']),
                            'nonbuilt_wins':sum(r['seller_won'] for r in checked if not r['built8']),
                            'sales_with_no_cash_to_seller':[(r['game'],r['decision'],r['net_cash_to_seller']) for r in checked if r['net_cash_to_seller']<=0],
                            'rows':checked}

# Four independent debt tables must describe the same episodes.
fa = read(fbase/'a4_debt_episodes.json')
aa = read(BASE/'full_drafts/astra/data/liquidation_episodes.json')
ak = {(r['game'],r['first_decision']):r for r in aa}
assert len(fa)==len(ak)==188
for r in fa:
    a=ak[r['game'],r['first_decision']]
    assert r['debt']==a['debt'] and (r['outcome']=='paid')==(a['outcome']=='paid')
out['debt_rows_compared']=len(fa)
out['sources']=sources
(HERE/'fable_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
brief={k:v for k,v in out.items() if k not in ['sources','cash_by_model','cash_by_stage','cash_by_block']}
brief['decline_to_sale']={k:v for k,v in brief['decline_to_sale'].items() if k!='rows'}
brief['seller_conversion']={k:v for k,v in brief['seller_conversion'].items() if k!='rows'}
print(json.dumps(brief,indent=2))
