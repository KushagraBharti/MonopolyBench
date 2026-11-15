"""Package existing evidence and check saved-record arithmetic. No engine imports.

All writes are under this independent draft. This is extraction, not evaluation.
"""
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
(HERE / 'qa').mkdir(exist_ok=True)
ROOT = next(p for p in HERE.parents if (p / "contracts/data/board.json").exists())
OLD = ROOT / "docs/research_raw/paper_revision_2026-11-12/integrated"
REVIEW = ROOT / "docs/research_raw/paper_review_2026-11-14/reviews"
inputs = {}

def read(p, lines=False):
    raw = p.read_bytes()
    inputs[str(p.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return [json.loads(x) for x in raw.splitlines()] if lines else json.loads(raw)

def esc(s):
    out = str(s).translate(str.maketrans({"—": " -- ", "–": "-", "→": " then ", "’": "'", "“": '"', "”": '"', "≥": ">=", "≤": "<="}))
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in out)

games = read(OLD / "data/game_map.json")
episodes = read(OLD / "data/liquidation_episodes.json")
board = read(ROOT / "contracts/data/board.json")
spaces = {re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces']}
groups = {}
for k,s in spaces.items():
    if s['kind']=='PROPERTY': groups.setdefault(s['group'],set()).add(k)
records = {}
counts = Counter()
for g,folder in games.items():
    rows = read(ROOT/folder/'decisions.jsonl',True)
    records[int(g)] = {phase:{int(r['decision_id'].rsplit('-',1)[1]):r for r in rows if r['phase']==phase} for phase in ['decision_started','decision_resolved']}
    counts['decisions'] += len(records[int(g)]['decision_resolved'])
    counts['attempts'] += sum(len(r['attempts']) for r in records[int(g)]['decision_resolved'].values())
    counts['events'] += len(read(ROOT/folder/'events.jsonl',True))
extracted = []
payable_declarations = {(12,190),(12,249),(17,234)}
for e in episodes:
    g,d=e['game'],e['first_decision']
    start=records[g]['decision_started'][d]; resolved=records[g]['decision_resolved'][d]
    payload=start['prompt_payload']; you=payload['game_state']['you']; owned=you['holdings']['owned']
    options=payload['action_state']['scenario']['options']
    m0=sum(spaces[k]['price']//2 for k in options['mortgageable_space_keys'])
    salvage=sum((5 if h['hotel'] else h['houses'])*board['house_cost_by_group'].get(spaces[h['space_key']].get('group'),0)//2 for h in owned)
    mstar=sum(spaces[h['space_key']]['price']//2 for h in owned if not h['mortgaged'])
    c=you['cash']; u=c+salvage+mstar
    assert u==e['upper_bound']
    a=resolved['attempts'][-1]; msg=a.get('raw_response',{}).get('choices',[{}])[0].get('message',{})
    row=dict(game=g,decision=d,turn=e['turn'],model=e['model'],cash=c,debt=e['debt'],S=salvage,M0=m0,Mstar=mstar,U0=c+salvage+m0,Ustar=u,outcome=e['outcome'],applied_action=resolved['final_action'],provider_reasoning=msg.get('reasoning'),reasoning_details=[{k:v for k,v in x.items() if k in ['type','text','format','index']} for x in msg.get('reasoning_details',[]) or []],assistant_content=a.get('assistant_content'),attempt_index=a.get('attempt_index',len(resolved['attempts'])-1),response_condition=a.get('response_condition'),fallback=resolved['fallback_used'],memory=payload['game_state']['memory'],holdings=owned,bank=payload['game_state']['bank'],options=options,actions=e['actions'],source=games[str(g)]+'/decisions.jsonl',decision_id=resolved['decision_id'])
    extracted.append(row)
assert counts=={'decisions':6989,'attempts':8679,'events':50918}
assert len(extracted)==188 and Counter(r['outcome'] for r in extracted)=={'paid':128,'bankrupt':60}
necessary=[r for r in extracted if r['U0']<r['debt']<=r['Ustar']]
assert len(necessary)==16 and sum(r['outcome']=='paid' for r in necessary)==14
payable=[r for r in extracted if r['outcome']=='paid' or (r['game'],r['decision']) in payable_declarations]
partition=Counter('initial' if r['cash']+r['M0']>=r['debt'] else 'sale_no_release' if r['U0']>=r['debt'] else 'release_required' for r in payable)
assert partition=={'initial':62,'sale_no_release':53,'release_required':16}
proof=[]
for r in payable:
    owned={h['space_key']:h for h in r['holdings']}
    developed=sorted({spaces[k]['group'] for k,h in owned.items() if h['houses'] or h['hotel']})
    assert all(groups[g]<=owned.keys() for g in developed)
    assert all(max(5 if owned[k]['hotel'] else owned[k]['houses'] for k in groups[g])-min(5 if owned[k]['hotel'] else owned[k]['houses'] for k in groups[g])<=1 for g in developed)
    hotels_by_group={g:sum(owned[k]['hotel'] for k in groups[g]) for g in developed}
    hotels=sum(hotels_by_group.values()); b=r['bank']['houses_remaining']
    h=sum(owned[k]['houses'] for g in developed if hotels_by_group[g]==0 for k in groups[g])
    if not hotels: category='hotel_free'
    elif r['cash']+r['M0']>=r['debt']: category='initial_mortgages'
    elif b>=4*hotels: category='stocked_downgrades'
    else:
        assert all(n<=1 for n in hotels_by_group.values()) and b+h>=4
        category='recyclable_stock'
    proof.append(dict(game=r['game'],decision=r['decision'],category=category,hotels=hotels,bank_houses=b,free_houses=h,hotels_by_group=hotels_by_group))
assert Counter(r['category'] for r in proof)=={'hotel_free':108,'initial_mortgages':12,'stocked_downgrades':9,'recyclable_stock':2}
for name,data in [('episodes_188',extracted),('sixteen_channels',necessary),('continuation_premises',proof),('game_map',games)]:
    (HERE/'data'/f'{name}.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
for n in ['offers.json','analysis.json','revision_analysis.json','paired_bargaining.json','transcript_manifest.json','opus_quote_manifest.json','fable_quote_manifest.json','additional_quote_manifest.json','integration_quote_manifest.json','source_hashes.json']:
    shutil.copyfile(OLD/'data'/n,HERE/'data'/n)
    inputs[str((OLD/'data'/n).relative_to(ROOT))]=hashlib.sha256((OLD/'data'/n).read_bytes()).hexdigest()
for n in ['full_offer_table.tex','cohort_table.tex','block_counts.tex','recipient_rows.tex','resampling_alternatives.tex']:
    table=(OLD/'sections'/n).read_text()
    if n=='block_counts.tex':
        table=table.replace(r'for the populations of Figure~\ref{fig:stability}', 'for the opening-offer comparisons')
    if n=='full_offer_table.tex':
        head=r'\toprule Stage & Form & Newly completes & N & Accept & Counter & Reject\\\midrule'
        table=table.replace(head+r'\endhead',head+r'\endfirsthead'+'\n'+head+r'\endhead')
    (HERE/'sections'/n).write_text(table)
for n in ['standard_system_prompt.txt','recovery_system_prompt.txt']:
    shutil.copyfile(OLD/'data'/n,HERE/'data'/n)
shutil.copyfile(REVIEW/'astra/continued_financing_argument.md',HERE/'data/inherited_continued_financing_argument.md')
text=[]
for r in necessary:
    text += [r'\Needspace{8\baselineskip}\subsection*{G%d d%d, %s, %s}'%(r['game'],r['decision'],esc(r['model'].split(' with ')[0]),r['outcome']),r'\noindent Debt \$%d; cash \$%d; $U_0=\$%d$; $U_*=\$%d$. Final attempt %d.\par'%(r['debt'],r['cash'],r['U0'],r['Ustar'],r['attempt_index'])]
    for label,value in [('Authored note',r['applied_action'].get('private_thought')),('Provider reasoning field',r['provider_reasoning']),('Assistant content',r['assistant_content'])]:
        text += [r'\paragraph{%s.} %s'%(label,esc(value) if value else 'Absent in this returned record.')]
    text += [r'\paragraph{Applied action.} \texttt{%s}. Observed sequence: %s.'%(esc(r['applied_action']['action']),esc(', '.join(r['actions'])))]
(HERE/'sections/sixteen_full.tex').write_text('\n\n'.join(text)+'\n')
(HERE/'data/input_hashes.json').write_text(json.dumps(inputs,indent=2)+'\n')
(HERE/'qa/record_checks.json').write_text(json.dumps(dict(corpus=counts,partition=partition,proof_categories=Counter(r['category'] for r in proof),no_engine_or_provider_execution=True),indent=2)+'\n')
print(json.dumps(dict(corpus=counts,partition=partition,proof_categories=Counter(r['category'] for r in proof))))
