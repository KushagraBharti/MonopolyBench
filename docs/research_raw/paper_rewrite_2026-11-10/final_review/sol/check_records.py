"""Document review only: original field reads and retained-ledger arithmetic.

No engine imports, execution, replay, model calls or hypothetical states.
"""
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

OUT = Path(__file__).resolve().parent
BASE = OUT.parents[1]
REPO = BASE.parents[2]
INT = BASE / 'integrated'
sources = {}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p, lines=False):
    p = Path(p)
    sources[str(p.relative_to(REPO))] = sha(p)
    return ([json.loads(x) for x in p.read_text().splitlines()] if lines
            else json.loads(p.read_text()))

report = {'scope': __doc__}
pins = read(INT / 'qa/integrated_file_hashes.json')['files']
assert all(sha(INT / n) == h for n,h in pins.items())
assert sha(INT/'manuscript.pdf') == '8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5'
report['pins'] = {'files': len(pins), 'mismatches': [], 'pdf': sha(INT/'manuscript.pdf')}
protected = read(BASE/'baseline_source_hashes.json')
assert all(sha(REPO / n) == h for n,h in protected.items())
frozen = read(BASE/'reviews/astra/review_source_hashes.json')
assert all(sha(REPO/n if (REPO/n).exists() else BASE/n) == h for n,h in frozen.items() if isinstance(h,str))
report['preservation'] = {'protected':len(protected), 'frozen':sum(isinstance(h,str) for h in frozen.values())}

offers = read(BASE/'data/agenda_offers.json')
legal = [o for o in offers if o['accept_available']]
stage = defaultdict(Counter)
recipient = defaultdict(Counter)
for o in legal:
    stage[(o['completion_cell'], 'opening' if o['exchange_index']==0 else 'later')][o['response']] += 1
    recipient[(o['recipient_model'],o['completion_cell'])][o['response']] += 1
report['offer_cells'] = [{'cell':k[0],'stage':k[1],**v} for k,v in sorted(stage.items())]
report['recipient_cells'] = [{'recipient':k[0],'cell':k[1],**v} for k,v in sorted(recipient.items())]
threads = defaultdict(list)
for o in offers: threads[o['thread_id']].append(o)
pairs=[]
for rows in threads.values():
    rows.sort(key=lambda o:o['exchange_index'])
    for a,b in zip(rows,rows[1:]):
        assert a['response']=='counter_trade' and a['recipient']==b['author']
        pairs.append((a,b))
assert len(pairs)==394
counter=[]
for cell in ['author_only','neither']:
    pp=[(a,b) for a,b in pairs if a['completion_cell']==cell and a['request']['properties']]
    retain=pure=0
    for a,b in pp:
        retain += set(a['request']['properties']) <= set(b['offer']['properties'])
        same=all(sorted(a[x]['properties'])==sorted(b[y]['properties']) and
                 a[x]['get_out_of_jail_cards']==b[y]['get_out_of_jail_cards']
                 for x,y in [('offer','request'),('request','offer')])
        pure += same and -b['net_cash_author_to_recipient'] > a['net_cash_author_to_recipient']
    counter.append([cell,len(pp),retain,pure])
assert counter==[['author_only',111,92,79],['neither',110,87,81]]
report['counter_common_predicate']=counter
all111=[(a,b) for a,b in pairs if a['completion_cell']=='author_only']
only88=[(a,b) for a,b in all111 if b['recipient_new_groups'] and not b['author_new_groups']]
report['counter_cash_denominator']={}
for label,rr in [('all111',all111),('retains_only_original_author88',only88)]:
    changes=[-b['net_cash_author_to_recipient']-a['net_cash_author_to_recipient'] for a,b in rr]
    report['counter_cash_denominator'][label]={'n':len(rr),'cash_improves':sum(x>0 for x in changes),'median_change':median(changes)}
assert report['counter_cash_denominator']=={'all111':{'n':111,'cash_improves':89,'median_change':100},'retains_only_original_author88':{'n':88,'cash_improves':85,'median_change':125}}
conflicts=read(BASE/'data/resolution_conditions.json')['selected_grok_conflicts']
conflict_ids={(r['game'],int(r['decision_id'].rsplit('-',1)[1])) for r in conflicts}
accepted=[o for o in offers if o['completion_cell']=='author_only' and o['response']=='accept_trade']
report['author_only_acceptances']={'n':len(accepted),'later':sum(o['exchange_index']>0 for o in accepted),
 'low_cash':sum(o['recipient_cash_before']<100 for o in accepted),'opus':sum(o['recipient_model']=='Opus' for o in accepted),
 'conflicts':sum((o['game'],o['decision']) in conflict_ids for o in accepted)}
report['reason_population']=dict(Counter(o['recipient_model'] for o in legal if o['response']=='reject_trade' and o['completion_cell'] in ['recipient_only','both']))
cohort=read(BASE/'data/t01_cohort.json')
winners={r['game']:r['winner'] for r in cohort}
flows=read(BASE/'data/agenda_flows.json')
estate=[r for r in flows if r['kind'].startswith('estate_')]
report['flow_types']=dict(Counter(r['kind'] for r in flows))
estate_creditors=defaultdict(set)
for r in estate: estate_creditors[(r['game'],r['elimination_index'])].add(r['to_model'])
report['winner_creditors']={
 'nonterminal':sum(v=={winners[g]} for (g,i),v in estate_creditors.items() if i<3),
 'terminal':sum(v=={winners[g]} for (g,i),v in estate_creditors.items() if i==3),
 'terminal_bank':[g for (g,i),v in estate_creditors.items() if i==3 and v=={'BANK'}]}
report['estate_deeds']={'nonterminal':sum(r['kind']=='estate_deed' and r['elimination_index']<3 for r in estate),
 'nonterminal_to_winner':sum(r['kind']=='estate_deed' and r['elimination_index']<3 and r['to_model']==winners[r['game']] for r in estate)}
eps=read(REPO/'docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl',True)
report['episode_routes']=dict(Counter(r['route'] for r in eps))
report['episode_example']=eps[0]
nonterminal=[r for r in eps if r['route']=='creditor_inheritance' and r['access_status']!='no_access_before_game_end']
report['nonterminal_estate_groups']={'n':len(nonterminal),'winner_owned':sum(r['model']==winners[r['game']] for r in nonterminal)}
report['episode_rent']={route:{'n':sum(r['route']==route for r in eps),
   'rent':sum(r['rent_until_loss_or_end'] for r in eps if r['route']==route),
   'positive':sum(r['rent_until_loss_or_end']>0 for r in eps if r['route']==route)}
   for route in sorted({r['route'] for r in eps})}
spend=read(BASE/'data/t05_spending_units.json')
report['spending']={k:sum(r[k] for r in spend) for k in ['spend','paid_developed_rent_after_first_own_spend','paid_developed_rent_whole_game']}
report['spending'].update(n=len(spend), zero=sum(r['paid_developed_rent_whole_game']==0 for r in spend),
 zero_no_elimination=sum(r['paid_developed_rent_whole_game']==0 and r['creditor_eliminations_on_group']==0 for r in spend))
cert=read(BASE/'data/certificate_results.json')
elims=[r for r in cert['results'] if r['kind']=='elimination']
for r in elims:
    bound=r['bound']
    assert bound['cash']+sum(d['salvage']+d['unmortgaged_capacity'] for d in bound['estate'])==bound['full_upper']
report['certificate_arithmetic']={'eliminations':len(elims),'types':dict(Counter(r['certificate'] for r in elims)),
 'upper_below_debt':sum(r['bound']['full_upper']<r['debt'] for r in elims),
 'retained_summary':cert['summary'],'engine_execution_in_this_review':False}

board=read(REPO/'contracts/data/board.json')
bykey={re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces'] if s['price'] is not None}
runs={o['game']:REPO/o['source_run'] for o in offers}
cache={}
def records(g):
    if g not in cache: cache[g]=read(runs[g]/'decisions.jsonl',True)
    return cache[g]
def decision(g,d,phase):
    return next(r for r in records(g) if r['phase']==phase and int(r['decision_id'].rsplit('-',1)[1])==d)

windows=read(BASE/'data/first_management_windows.json')['rows']
report['window_causes']=dict(Counter(r['cause'] for r in windows))
access=[]
for w in windows:
    if w['cause']!='never_legal_in_window':continue
    g=w['game'];d=int(w['first_mgmt_decision'].rsplit('-',1)[1])
    p=decision(g,d,'decision_started')['prompt_payload']
    own=p['game_state']['you'];opts=p['action_state']['scenario']['options']
    target={k for k,v in bykey.items() if v['group']==w['group']}
    holdings={h['space_key']:h for h in own['holdings']['owned']}
    redemption=sum(math.ceil(bykey[k]['price']//2*1.1) for k in target if holdings[k]['mortgaged'])
    collateral={k:bykey[k]['price']//2 for k in opts.get('mortgageable_space_keys',[]) if k not in target}
    house=board['house_cost_by_group'][w['group']]
    access.append({'game':g,'decision':d,'model':w['model'],'group':w['group'],'cash':own['cash'],
       'redemption':redemption,'house':house,'outside_menu_mortgages':collateral,
       'budget':own['cash']+sum(collateral.values())-redemption-house,
       'cash_only':own['cash']>=redemption+house,
       'action':decision(g,d,'decision_resolved')['final_action']})
report['access']=access
assert sum(r['cash_only'] for r in access)==2 and sum(r['budget']>=0 for r in access)==7
prices=[]
for o in legal:
    a,b=o['offer'],o['request']
    if a['get_out_of_jail_cards'] or b['get_out_of_jail_cards']:continue
    if not a['properties'] and b['properties'] and a['cash']>0 and b['cash']==0:
        role='bid';cash=a['cash'];deeds=b['properties']
    elif a['properties'] and not b['properties'] and b['cash']>0 and a['cash']==0:
        role='ask';cash=b['cash'];deeds=a['properties']
    else: continue
    prices.append({'role':role,'cell':o['completion_cell'],'ratio':cash/sum(bykey[k]['price'] for k in deeds),
       'interest':o['author_interest_if_accepted']+o['recipient_interest_if_accepted'],'opening':o['exchange_index']==0})
report['price_cuts']=[]
for subset in ['all','unmortgaged','opening','later']:
    for role,cell in [('bid','author_only'),('bid','neither'),('ask','recipient_only'),('ask','neither')]:
        rr=[r for r in prices if r['role']==role and r['cell']==cell and
            (subset!='unmortgaged' or r['interest']==0) and (subset!='opening' or r['opening']) and
            (subset!='later' or not r['opening'])]
        report['price_cuts'].append([subset,role,cell,len(rr),median(r['ratio'] for r in rr)])

man=read(INT/'data/transcript_manifest.json')
qmap={q['id']:[(man['fields'][s['field_id']],s['span'],s['text']) for s in q['excerpts']] for q in man['quotes']}
for q in read(INT/'data/opus_quote_manifest.json')['quotes']:
    qmap[q['id']]=[(q,q['span_codepoints'],q['excerpt'])]
for q in read(INT/'data/fable_quote_manifest.json')['quotes']:
    qmap[q['id']]=[(q,s['span'],s['text']) for s in q['excerpts']]
prose='\n'.join(p.read_text() for p in (INT/'sections').glob('*.tex') if not p.name.endswith('quotes.tex'))
used=re.findall(r'\\TranscriptQuote\{([^}]+)\}',prose)
source_fields=[]
quote_files=set()
rawcache={}
for qid in used:
    for f,span,excerpt in qmap[qid]:
        p=REPO/f['source'];quote_files.add(str(p.relative_to(REPO)))
        if p not in rawcache:rawcache[p]=p.read_bytes();sources[str(p.relative_to(REPO))]=sha(p)
        assert sha(p)==f['source_sha256']
        raw=rawcache[p]
        obj=json.loads(raw.splitlines()[f['jsonl_line_1based']-1]) if f.get('jsonl_line_1based') else json.loads(raw)
        for key in f['json_pointer'].lstrip('/').split('/'):
            key=key.replace('~1','/').replace('~0','~')
            obj=obj[int(key)] if isinstance(obj,list) else obj[key]
        assert hashlib.sha256(obj.encode()).hexdigest()==f['field_sha256']
        assert obj[slice(*span)]==excerpt
        source_fields.append({'id':qid,'field':obj,'span':span,'source':f['source'],'pointer':f['json_pointer']})
report['quotes']={'cards':len(used),'spans':len(source_fields),'original_files':len(quote_files)}
(OUT/'original_quote_fields.json').write_text(json.dumps(source_fields,indent=2)+'\n')
report['source_sha256']=sources
(OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['source_sha256','episode_example','access','recipient_cells']},indent=2))
