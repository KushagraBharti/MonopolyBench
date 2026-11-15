"""Read-only checks of the new reviews. No engine imports or evaluations."""
from pathlib import Path
from collections import Counter
import json,re,hashlib

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'contracts').is_dir())
PAPER=ROOT/'docs/research_raw/paper_revision_2026-11-11/integrated'
sources={}
def read(p,lines=False):
    blob=p.read_bytes();sources[str(p.relative_to(ROOT))]=hashlib.sha256(blob).hexdigest()
    return [json.loads(x) for x in blob.splitlines()] if lines else json.loads(blob)
offers=read(PAPER/'data/offers.json');episodes=read(PAPER/'data/liquidation_episodes.json')
swaps=[r for r in offers if r['accept_available'] and r['exchange_index']==0 and r['offer']['properties'] and r['request']['properties']]
cells={}
for m in ['Sol','Opus','Grok','Gemini']:
    cells[m]={}
    for c in ['author_only','neither']:
        rows=[r for r in swaps if r['author_model']==m and r['completion_cell']==c]
        cells[m][c]={'n':len(rows),**dict(Counter(r['response'] for r in rows))}
gaps={m:c['author_only']['reject_trade']/c['author_only']['n']-c['neither'].get('reject_trade',0)/c['neither']['n'] for m,c in cells.items()}
weighted={}
for name in ['author_only','neither','pooled']:
    weights={m:c[name]['n'] if name!='pooled' else c['author_only']['n']+c['neither']['n'] for m,c in cells.items()}
    weighted[name]=sum(gaps[m]*w for m,w in weights.items())/sum(weights.values())

board=read(ROOT/'contracts/data/board.json');costs=board['house_cost_by_group']
spaces={re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces']}
book_transfers={}
for name in ['Grok','Other']:
    accepted=[r for r in offers if r['exchange_index']==0 and r['response']=='accept_trade' and ((r['author_model']=='Grok')==(name=='Grok'))]
    value=lambda side:side['cash']+sum(spaces[k]['price'] for k in side['properties'])
    book_transfers[name]={'offers':len(accepted),'net_list_value_to_recipient':sum(value(r['offer'])-value(r['request']) for r in accepted)}
assert book_transfers=={'Grok':{'offers':21,'net_list_value_to_recipient':4700},'Other':{'offers':11,'net_list_value_to_recipient':340}}
runs={r['game']:r['source_run'] for r in offers};records={}
for game,path in runs.items():
    rows=read(ROOT/path/'decisions.jsonl',True)
    records[game]={phase:{r['decision_id']:r for r in rows if r['phase']==phase} for phase in ['decision_started','decision_resolved']}
necessary=[];first_menu_enough=0
for e in episodes:
    did=e['decisions'][0];start=records[e['game']]['decision_started'][did]
    payload=start['prompt_payload'];you=payload['game_state']['you'];opts=payload['action_state']['scenario']['options']
    listed=sum(spaces[k]['price']//2 for k in opts['mortgageable_space_keys'])
    salvage=sum((5 if h['hotel'] else h['houses'])*costs.get(spaces[h['space_key']]['group'],0)//2 for h in you['holdings']['owned'])
    if e['outcome']=='paid' and you['cash']+listed>=e['debt']:first_menu_enough+=1
    if you['cash']+listed+salvage<e['debt']<=e['upper_bound']:
        resolved=records[e['game']]['decision_resolved'][did];att=resolved['attempts'][-1]
        msg=att.get('raw_response',{}).get('choices',[{}])[0].get('message',{})
        necessary.append({'game':e['game'],'decision':e['first_decision'],'model':e['model'],
                          'outcome':e['outcome'],'cash':you['cash'],'listed_mortgages':listed,'salvage':salvage,
                          'debt':e['debt'],'upper_bound':e['upper_bound'],'private_note':resolved['final_action'].get('private_thought'),
                          'provider_reasoning':msg.get('reasoning'),'assistant_content':att.get('assistant_content')})
out={'proposer_cells':cells,'standardized_gap_by_reference_weights':weighted,'opening_accepted_book_transfers':book_transfers,
     'necessary_unlocked_collateral':necessary,'necessary_outcomes':dict(Counter(r['outcome'] for r in necessary)),
     'paid_initial_cash_plus_listed_mortgages_enough':first_menu_enough,
     'scope':'Arithmetic necessity under the generous asset formula, not an executable feasibility proof or semantic annotation.',
     'sources':sources}
(HERE/'astra_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['sources','necessary_unlocked_collateral']},indent=2))
for r in necessary:print(r['game'],r['decision'],r['model'],r['outcome'],r['cash'],r['listed_mortgages'],r['salvage'],r['debt'])
