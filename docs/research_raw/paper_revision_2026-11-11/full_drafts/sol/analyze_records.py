"""Existing-record arithmetic only. Never imports engine, arena, or replay code."""
import json, re, hashlib, difflib
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
OLD=ROOT/'docs/research_raw/paper_rewrite_2026-11-10'
for d in ['data','assets','qa','sections','literature']:(HERE/d).mkdir(exist_ok=True)
hashes={}
def read(p,lines=False):
    b=p.read_bytes();hashes[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest()
    return [json.loads(x) for x in b.splitlines()] if lines else json.loads(b)
def write(n,x): (HERE/'data'/n).write_text(json.dumps(x,indent=2)+'\n')
offers=read(OLD/'integrated/data/agenda_offers.json')
cohort=read(OLD/'integrated/data/t01_cohort.json')
episodes=read(ROOT/'docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl',True)
elims=read(OLD/'integrated/data/t06_eliminations.json')
flows=read(OLD/'data/agenda_flows.json')
board=read(ROOT/'contracts/data/board.json')
spaces={re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces'] if s['price'] is not None}
groups=defaultdict(set)
for k,s in spaces.items():
    if s['kind']=='PROPERTY':groups[s['group']].add(k)
runpaths={r['game']:ROOT/r['source_run'] for r in offers}
starts={};resolved={};events={};byid={}
for g,p in runpaths.items():
    rows=read(p/'decisions.jsonl',True)
    starts[g]=[r for r in rows if r['phase']=='decision_started']
    resolved[g]=[r for r in rows if r['phase']=='decision_resolved']
    events[g]=read(p/'events.jsonl',True)
    byid[g]={r['decision_id']:r for r in starts[g]}
def fieldplayers(r):
    gs=r['prompt_payload']['game_state'];return [gs['you']]+gs['others']
def own(r,p):return next(x for x in fieldplayers(r) if x['player_id']==p)
def mod(name):
    return next(x for x in ['Sol','Gemini','Opus','Grok'] if x.lower() in name.lower())
legal=[r for r in offers if r['accept_available']]
joint=[]
for m in ['Sol','Gemini','Opus','Grok']:
    for stage in ['opening','later']:
        for cell in ['author_only','recipient_only','both','neither']:
            rr=[r for r in legal if r['recipient_model']==m and ('opening' if r['exchange_index']==0 else 'later')==stage and r['completion_cell']==cell]
            c=Counter(r['response'] for r in rr)
            joint.append(dict(model=m,stage=stage,cell=cell,n=len(rr),accept=c['accept_trade'],counter=c['counter_trade'],reject=c['reject_trade']))
write('joint_responses.json',joint)
price=[]
for r in legal:
    a,b=r['offer'],r['request'];kind=None
    if a['get_out_of_jail_cards'] or b['get_out_of_jail_cards']:continue
    if a['properties'] and not b['properties'] and a['cash']==0 and b['cash']>0:kind='ask';deeds=a['properties'];cash=b['cash'];seller=r['author']
    if b['properties'] and not a['properties'] and b['cash']==0 and a['cash']>0:kind='bid';deeds=b['properties'];cash=a['cash'];seller=r['recipient']
    if kind is None:continue
    st=byid[r['game']][r['decision_id']]
    holdings={d['space_key']:d for d in own(st,seller)['holdings']['owned']}
    mort=any(holdings[k]['mortgaged'] for k in deeds)
    price.append(dict(game=r['game'],decision=r['decision'],thread=r['thread_id'],kind=kind,model=r['author_model'],recipient=r['recipient_model'],seller=seller,deeds=deeds,cash=cash,ratio=cash/sum(spaces[k]['price'] for k in deeds),mortgaged=mort,stage='opening' if r['exchange_index']==0 else 'later',completion=r['completion_cell'],accepted=r['response']=='accept_trade'))
write('price_rows.json',price)
def summary(rr):return dict(n=len(rr),median=median(x['ratio'] for x in rr) if rr else None)
pcells=[]
for m in ['Sol','Gemini','Opus','Grok']:
    for mort in [False,True]:
        for stage in ['opening','later','all']:
            for cell in ['recipient_only','neither']:
                rr=[r for r in price if r['kind']=='ask' and r['model']==m and r['mortgaged']==mort and (stage=='all' or r['stage']==stage) and r['completion']==cell]
                pcells.append(dict(model=m,mortgaged=mort,stage=stage,cell=cell,**summary(rr)))
write('price_cells.json',pcells)
same=defaultdict(list)
for r in price:
    if r['kind']=='ask' and len(r['deeds'])==1:same[(r['game'],r['seller'],r['deeds'][0])].append(r)
pairs=[]
for (g,s,d),rr in same.items():
    a=[r for r in rr if r['completion']=='recipient_only'];b=[r for r in rr if r['completion']=='neither']
    if a and b:pairs.append(dict(game=g,seller=s,deed=d,model=rr[0]['model'],completion=summary(a),neither=summary(b),decisions=[r['decision'] for r in rr],direction=(median(r['ratio'] for r in a)>median(r['ratio'] for r in b))-(median(r['ratio'] for r in a)<median(r['ratio'] for r in b))))
write('same_deed.json',pairs)
# Same seller/deed/mortgage/stage restriction is intentionally sparse.
matched=[]
for (g,s,d),rr in same.items():
    for mort in [False,True]:
        for stage in ['opening','later']:
            aa=[r for r in rr if r['completion']=='recipient_only' and r['mortgaged']==mort and r['stage']==stage]
            bb=[r for r in rr if r['completion']=='neither' and r['mortgaged']==mort and r['stage']==stage]
            if aa and bb:matched.append(dict(game=g,seller=s,deed=d,mortgaged=mort,stage=stage,completion=summary(aa),neither=summary(bb)))
write('same_deed_stage_mortgage.json',matched)
# Time and observed movement exposure, retaining inherited episode boundaries.
trade=[]
for ep in episodes:
    if ep['route']!='trade':continue
    g=ep['game'];lo=ep['settlement_end_seq'];hi=ep['end_seq_exclusive'];ee=[e for e in events[g] if lo<e['seq']<hi]
    opp=[e for e in ee if e['type']=='PLAYER_MOVED' and e['actor']['player_id']!=ep['player_id']]
    inds={spaces[k]['index'] for k in groups[ep['group']]}
    land=[e for e in opp if e['payload']['to'] in inds]
    rent=[f for f in flows if f['game']==g and f['kind']=='paid_rent' and f['to']==ep['player_id'] and f.get('space_key') in groups[ep['group']] and lo<f['seq']<hi]
    assert sum(f['amount'] for f in rent)==ep['rent_until_loss_or_end']
    endturn=next(e['turn_index'] for e in events[g] if e['seq']==hi-1)
    trade.append(dict(game=g,player=ep['player_id'],model=ep['model'],group=ep['group'],completion_turn=ep['acquisition_turn'],end_turn=endturn,first_build_turn=ep['first_build_turn'],first_window=ep['built_first_management'],opponent_moves=len(opp),group_landings=len(land),rent=sum(f['amount'] for f in rent),ownership_turns=endturn-ep['acquisition_turn'],build_delay=ep['elapsed_to_build']))
write('development_exposure.json',trade)
exposure=[]
for early in [True,False]:
    rr=[r for r in trade if r['first_window']==early]
    exposure.append(dict(first_window=early,n=len(rr),rent=sum(r['rent'] for r in rr),opponent_moves=sum(r['opponent_moves'] for r in rr),group_landings=sum(r['group_landings'] for r in rr),median_completion=median(r['completion_turn'] for r in rr),median_duration=median(r['ownership_turns'] for r in rr),median_moves=median(r['opponent_moves'] for r in rr)))
write('exposure_summary.json',exposure)
# All episodes that reach a debt menu. Consecutive same-player debt decisions
# form one episode until a non-liquidation decision. Boundaries checked using
# the retained elimination-decision identifiers, not a new feasibility search.
debts=[]
for g,rr in starts.items():
    current=None
    for r in rr:
        if r['decision_type']!='LIQUIDATION_DECISION':current=None;continue
        sc=r['prompt_payload']['action_state']['scenario'];key=(r['player_id'],r['turn_index'],sc['owed_amount'],sc.get('owed_to_player_id'),sc['reason'])
        if current is None or current['_key']!=key:
            p=r['prompt_payload']['game_state']['you'];hh=p['holdings']['owned']
            salvage=sum((5 if d['hotel'] else d['houses'])*board['house_cost_by_group'][spaces[d['space_key']]['group']]//2 for d in hh if spaces[d['space_key']]['kind']=='PROPERTY')
            bound=p['cash']+salvage+sum(spaces[d['space_key']]['price']//2 for d in hh if not d['mortgaged'])
            current=dict(_key=key,game=g,player=r['player_id'],model=mod(r['player_name']),first_decision=r['decision_id'],decisions=[],debt=sc['owed_amount'],cash=p['cash'],bound=bound,reason=sc['reason'],creditor=sc.get('owed_to_player_id'));debts.append(current)
        current['decisions'].append(r['decision_id'])
elimkeys={(e['game'],e['decision']) for e in elims}
for d in debts:
    d.pop('_key')
    matches=[e for e in elims if e['game']==d['game'] and any(x.endswith(e['decision']) for x in d['decisions'])]
    d['outcome']='eliminated' if matches else 'paid'
    d['classification']='paid_observed' if not matches else ('inherited_payment_witness' if matches[0]['avoidable'] else 'below_own_asset_bound' if matches[0]['full']<matches[0]['owed'] else 'inherited_menu_lock')
    end=next(r for r in resolved[d['game']] if r['decision_id']==d['decisions'][-1])
    ee=[e for e in events[d['game']] if end['emitted_event_seq_start']<=e['seq']<=end['emitted_event_seq_end']]
    d['last_action_event_types']=[e['type'] for e in ee]
    if not matches:
        payments=[e for e in ee if (e['type']=='RENT_PAID' and e['payload'].get('from_player_id')==d['player'] and e['payload'].get('amount')==d['debt']) or (e['type']=='CASH_CHANGED' and e['payload'].get('player_id')==d['player'] and e['payload'].get('delta')==-d['debt'])]
        assert payments,(d,ee)
        d['observed_payment_events']=[e['seq'] for e in payments]
write('debt_episodes.json',debts)
assert sum(d['outcome']=='eliminated' for d in debts)==60
# First-estate positions use a simultaneous delivered state before the first
# bankruptcy action. Values are transparent accounting summaries, not utility.
first=[]
for g in sorted(runpaths):
    es=min((e for e in elims if e['game']==g),key=lambda e:e['elimination_event_seq'])
    st=next(r for r in starts[g] if r['decision_id'].endswith(es['decision']))
    fs=[f for f in flows if f['game']==g and f['kind']=='estate_deed' and f['elimination_index']==1]
    creditor=fs[0]['to'] if fs else None
    seq=es['elimination_event_seq'];positions=[]
    for p in fieldplayers(st):
        hh=p['holdings']['owned'];kk={d['space_key'] for d in hh}
        positions.append(dict(player=p['player_id'],model=mod(p['name']),cash=p['cash'],deeds=len(hh),complete_groups=sum(v<=kk for v in groups.values()),developed_groups=len({spaces[d['space_key']]['group'] for d in hh if d['houses'] or d['hotel']}),building_equivalents=sum(5 if d['hotel'] else d['houses'] for d in hh),prior_paid_rent=sum(f['amount'] for f in flows if f['game']==g and f['kind']=='paid_rent' and f['to']==p['player_id'] and f['seq']<seq)))
    cr=next(p for p in positions if p['player']==creditor)
    ranks={k:1+sum(p[k]>cr[k] for p in positions) for k in ['cash','deeds','complete_groups','developed_groups','building_equivalents','prior_paid_rent']}
    first.append(dict(game=g,turn=st['turn_index'],creditor=creditor,creditor_model=cr['model'],winner=cohort[g-1]['winner'],creditor_wins=cr['model']==cohort[g-1]['winner'],ranks=ranks,positions=positions,incoming_deeds=len(fs)))
write('first_estate_positions.json',first)
write('first_estate_unique_leads.json',{k:sum(sum(p[k]==max(z[k] for z in r['positions']) for p in r['positions'])==1 and r['ranks'][k]==1 for r in first) for k in ['cash','deeds','building_equivalents','prior_paid_rent']})
# Exact standard/recovery prompt difference from G2 d197, including schemas.
st=next(r for r in starts[2] if r['decision_id'].endswith('000197'))
res=next(r for r in resolved[2] if r['decision_id']==st['decision_id'])
standard=st['prompt_messages'][0]['content'];recovery=res['attempts'][1]['prompt_messages'][0]['content']
(HERE/'data/standard_system_prompt.txt').write_text(standard)
(HERE/'data/recovery_system_prompt.txt').write_text(recovery)
(HERE/'data/prompt_difference.diff').write_text(''.join(difflib.unified_diff(standard.splitlines(True),recovery.splitlines(True),fromfile='standard',tofile='recovery')))
promptdir=runpaths[2]/'prompts'
tool0=next(promptdir.glob('*000197_tools.json'));tool1=next(promptdir.glob('*000197_retry1_tools.json'))
tools0=read(tool0);tools1=read(tool1)
write('standard_tools.json',tools0);write('recovery_tools.json',tools1)
(HERE/'data/tool_difference.diff').write_text(''.join(difflib.unified_diff(json.dumps(tools0,indent=2).splitlines(True),json.dumps(tools1,indent=2).splitlines(True),fromfile='standard_tools',tofile='recovery_tools')))
# Check that deleting only private_thought properties/requirements exactly
# reconstructs this recovery schema. This compares records; no action is run.
import copy
stripped=copy.deepcopy(tools0)
for t in stripped:
    params=t['function']['parameters'];params['properties'].pop('private_thought',None)
    params['required']=[x for x in params['required'] if x!='private_thought']
assert stripped==tools1
write('prompt_sources.json',dict(game=2,decision=197,source=str((runpaths[2]/'decisions.jsonl').relative_to(ROOT)),standard_pointer='/prompt_messages/0/content',recovery_pointer='/attempts/1/prompt_messages/0/content',standard_sha256=hashlib.sha256(standard.encode()).hexdigest(),recovery_sha256=hashlib.sha256(recovery.encode()).hexdigest()))
# Figures have no resampling or new observations.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(7,3.6))
for i,r in enumerate(pairs):
    a=r['neither']['median'];b=r['completion']['median'];ax.plot([a,b],[i,i],color='#9099a0',lw=2);ax.scatter(a,i,color='#426780',marker='o',s=38);ax.scatter(b,i,color='#b85d32',marker='D',s=35)
ax.set_yticks(range(len(pairs)),[f"G{r['game']} {r['model']} · {r['deed'].replace('_',' ').title()}" for r in pairs]);ax.invert_yaxis();ax.set_xlabel('Median ask / deed list price');ax.scatter([],[],color='#426780',label='Completes neither');ax.scatter([],[],color='#b85d32',marker='D',label='Completes buyer');ax.legend(frameon=False,loc='lower right');fig.tight_layout();fig.savefig(HERE/'assets/same_deed.pdf');fig.savefig(HERE/'assets/same_deed.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.1,7.2));ordered=sorted(trade,key=lambda r:(not r['first_window'],r['completion_turn'],r['game']))
for i,r in enumerate(ordered):
    col='#426780' if r['first_window'] else '#b85d32';ax.plot([r['completion_turn'],r['end_turn']],[i,i],c=col,lw=2,alpha=.7)
    if r['first_build_turn'] is not None:ax.scatter(r['first_build_turn'],i,s=10,c='black',zorder=3)
    ax.text(400,i,f"{r['opponent_moves']:3d}    ${r['rent']:,}",fontsize=6.6,va='center',family='monospace')
ax.axhline(42.5,color='gray',ls=':',lw=.8);ax.text(400,-2,'Moves   Paid rent',fontsize=7);ax.set_ylim(64,-4);ax.set_xlim(0,530);ax.set_xticks([0,100,200,300]);ax.set_xlabel('Global game turn');ax.set_ylabel('Trade completion episodes, sorted by first-window build and acquisition');ax.set_yticks([21,53],['43 built in\nfirst window','20 others']);fig.tight_layout();fig.savefig(HERE/'assets/exposure.pdf');fig.savefig(HERE/'assets/exposure.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.1,3.6));metrics=['cash','deeds','building_equivalents','prior_paid_rent'];lab=['Cash','Deeds','Buildings (house equivalents)','Prior paid rent']
for j,k in enumerate(metrics):
    for i,r in enumerate(first):ax.scatter(i+1,j,c=['#315b79','#7b9baf','#d1a16e','#b95737'][r['ranks'][k]-1],s=45 if r['creditor_wins'] else 70,marker='o' if r['creditor_wins'] else 'X')
ax.set_yticks(range(4),lab);ax.invert_yaxis();ax.set_xticks(range(1,21));ax.set_xlabel('Game, immediately before first bankruptcy action');ax.set_xlim(.3,20.7)
for rank,col in enumerate(['#315b79','#7b9baf','#d1a16e','#b95737'],1):ax.scatter([],[],c=col,label=f'Rank {rank}',s=35)
ax.legend(ncol=4,frameon=False,bbox_to_anchor=(.5,1.25),loc='upper center');fig.tight_layout();fig.savefig(HERE/'assets/pre_estate.pdf');fig.savefig(HERE/'assets/pre_estate.png',dpi=180);plt.close(fig)
summary_data=dict(same_deed_directions=dict(Counter(r['direction'] for r in pairs)),matched_stage_mortgage_n=len(matched),debts=dict(Counter(d['classification'] for d in debts)),first_creditor_ranks={k:dict(Counter(r['ranks'][k] for r in first)) for k in metrics},exposure=exposure)
write('results.json',summary_data)
write('corpus_counts.json',dict(events=sum(len(x) for x in events.values()),decisions=sum(len(x) for x in starts.values()),resolved=sum(len(x) for x in resolved.values()),attempts=sum(len(r['attempts']) for rr in resolved.values() for r in rr)))
write('source_hashes.json',hashes)
print(json.dumps(summary_data,indent=2))
