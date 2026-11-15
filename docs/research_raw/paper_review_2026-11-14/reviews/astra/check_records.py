"""Read saved records only. No engine, policies, transitions, or model calls."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'contracts').is_dir())
BASE = ROOT / 'docs/research_raw/paper_revision_2026-11-12'
PAPER = BASE / 'integrated'
sources = {}

def read(path, lines=False):
    b = path.read_bytes()
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(b).hexdigest()
    return [json.loads(x) for x in b.splitlines()] if lines else json.loads(b)

pin = read(BASE / 'final_manuscript_manifest.json')
pin_entries = pin['files']
assert all(hashlib.sha256((BASE / p).read_bytes()).hexdigest() == h for p,h in pin_entries.items())
games = read(PAPER / 'data/game_map.json')
episodes = read(PAPER / 'data/liquidation_episodes.json')
board = read(ROOT / 'contracts/data/board.json')
spaces = {re.sub('[^A-Z0-9]+', '_', s['name'].upper()).strip('_'): s for s in board['spaces']}
cost = board['house_cost_by_group']
records = {}
for g, folder in games.items():
    rows = read(ROOT / folder / 'decisions.jsonl', True)
    records[int(g)] = {phase: {int(r['decision_id'].rsplit('-',1)[1]): r for r in rows if r['phase']==phase}
                       for phase in ['decision_started','decision_resolved']}

rows = []
for e in episodes:
    g,d = e['game'],e['first_decision']
    start = records[g]['decision_started'][d]
    result = records[g]['decision_resolved'][d]
    payload = start['prompt_payload']
    you = payload['game_state']['you']
    holdings = you['holdings']['owned']
    opts = payload['action_state']['scenario']['options']
    m0 = sum(spaces[k]['price']//2 for k in opts['mortgageable_space_keys'])
    salvage = sum((5 if h['hotel'] else h['houses'])*cost.get(spaces[h['space_key']].get('group'),0)//2 for h in holdings)
    mstar = sum(spaces[h['space_key']]['price']//2 for h in holdings if not h['mortgaged'])
    u0,u = you['cash']+salvage+m0,you['cash']+salvage+mstar
    assert u==e['upper_bound']
    attempt = result['attempts'][-1]
    msg = attempt.get('raw_response',{}).get('choices',[{}])[0].get('message',{})
    necessity = u0<e['debt']<=u
    row = {'game':g,'decision':d,'turn':e['turn'],'model':e['model'],'outcome':e['outcome'],
           'debt':e['debt'],'cash':you['cash'],'M0':m0,'S':salvage,'Mstar':mstar,'U0':u0,'Ustar':u,
           'necessity_inequality':necessity,'above_bound':u<e['debt'],
           'holdings':holdings,'bank':payload['game_state']['bank'],'options':opts,
           'applied_action':result['final_action'],'provider_reasoning':msg.get('reasoning'),
           'reasoning_details':[{k:v for k,v in detail.items() if k in {'type','text','format','index'}}
                                for detail in (msg.get('reasoning_details') or [])],
           'assistant_content':attempt.get('assistant_content'),
           'memory':payload['game_state']['memory'], 'response_condition':attempt.get('response_condition'),
           'recorded_actions':e['actions'],'fallback':result['fallback_used'],
           'source':str((ROOT/games[str(g)]/'decisions.jsonl').relative_to(ROOT))}
    rows.append(row)

necessary = [r for r in rows if r['necessity_inequality']]
futile = [r for r in rows if r['above_bound'] and r['applied_action']['action']!='declare_bankruptcy']
assert len(necessary)==16 and Counter(r['outcome'] for r in necessary)=={'paid':14,'bankrupt':2}
assert len(futile)==6
summary = {'episodes':len(rows),'outcomes':dict(Counter(r['outcome'] for r in rows)),
           'necessity':len(necessary),'necessity_outcomes':dict(Counter(r['outcome'] for r in necessary)),
           'above_bound_financing':[(r['game'],r['decision'],r['model']) for r in futile],
           'percent_of_episodes':100*16/188,'percent_of_demonstrated_payable':100*16/131,
           'percentage_using_incommensurate_decision_denominator':100*16/6989,
           'pin_entries_passed':len(pin_entries)}

out={'summary':summary,'rows':rows,'sources':sources}
(HERE/'record_checks.json').write_text(json.dumps(out,indent=2)+'\n')
for name, selected in [('sixteen_channels',necessary),('six_above_bound',futile)]:
    text=[]
    for r in selected:
        text += [f"## G{r['game']} d{r['decision']} {r['model']} ({r['outcome']})",
                 f"D={r['debt']}, C={r['cash']}, S={r['S']}, M0={r['M0']}, U0={r['U0']}, U*={r['Ustar']}",
                 '**Applied action and note**',json.dumps(r['applied_action'],ensure_ascii=False),
                 '**Provider reasoning field**',str(r['provider_reasoning']),
                 '**Assistant content**',str(r['assistant_content']),
                 '**Observed action sequence**',', '.join(r['recorded_actions']),
                 '**Delivered memory**',json.dumps(r['memory'],ensure_ascii=False),
                 '**Source**',r['source'],'']
    (HERE/(name+'.md')).write_text('\n\n'.join(text)+'\n')
print(json.dumps(summary,indent=2))
