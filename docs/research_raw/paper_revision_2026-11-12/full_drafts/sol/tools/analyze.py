"""Saved-record arithmetic and block resampling only. No engine imports.

Run from any directory. All outputs stay within the Sol package.
"""
from pathlib import Path
from collections import Counter
import hashlib, itertools, json, re, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in HERE.parents if (p/'contracts').is_dir())
sources={}
def read(p, lines=False):
    b=p.read_bytes(); sources[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest()
    return [json.loads(x) for x in b.splitlines() if x] if lines else json.loads(b)
def save(name,obj): (HERE/'data'/name).write_text(json.dumps(obj,indent=2)+'\n')
offers=read(HERE/'data/offers.json'); episodes=read(HERE/'data/liquidation_episodes.json')
def form(r):
    a,b=r['offer'],r['request']
    if a['properties'] and b['properties']: return 'swap'
    if b['properties'] and not a['properties'] and a['cash']>0 and b['cash']==0 and not a['get_out_of_jail_cards'] and not b['get_out_of_jail_cards']: return 'cash_bid'
    return 'other'
cells=['author_only','recipient_only','both','neither']; forms=['swap','cash_bid','other']
models=['Sol','Gemini','Opus','Grok']
legal=[r for r in offers if r['accept_available']]
opening=[r for r in legal if r['exchange_index']==0]
def count(rs): return {'n':len(rs),**dict(Counter(r['response'] for r in rs))}
def table(rs):return {f:{c:count([r for r in rs if form(r)==f and r['completion_cell']==c]) for c in cells} for f in forms}
def pair(rs,f): return [count([r for r in rs if form(r)==f and r['completion_cell']==c]) for c in ['author_only','neither']]
def gap(rs,f='swap'):
    a,b=pair(rs,f)
    return 100*(a.get('reject_trade',0)/a['n']-b.get('reject_trade',0)/b['n']) if a['n'] and b['n'] else None
out={'full':table(legal),'opening':table(opening),'later':table([r for r in legal if r['exchange_index']>0]),
     'proposer':{m:table([r for r in opening if r['author_model']==m]) for m in models},
     'recipient':{m:table([r for r in opening if r['recipient_model']==m]) for m in models}}
runs={r['game']:r['source_run'] for r in offers};records={}; game_map=[]; replay=[]
cohort=read(ROOT/'docs/research_raw/paper_rewrite_2026-11-10/data/t01_cohort.json')
for g,path in sorted(runs.items()):
    rows=read(ROOT/path/'decisions.jsonl',True)
    records[g]={p:{r['decision_id']:r for r in rows if r['phase']==p} for p in ['decision_started','decision_resolved']}
    cfg=read(ROOT/path/'run_config.json')
    a=read(ROOT/path/'artifact_replay_report.json'); s=read(ROOT/path/'state_replay_report.json')
    assert a['status']==s['status']=='passed' and a['excluded_event_types']==[]
    assert a['original_canonical_hash']==a['replay_canonical_hash'] and s['original_canonical_hash']==s['replay_canonical_hash']
    replay.append({'game':g,'artifact_events':a['original_compared_event_count'],'state_events':s['original_compared_event_count'],'artifact_hash':a['original_canonical_hash'],'state_hash':s['original_canonical_hash']})
    game_map.append({**cohort[g-1],'source_run':path,'run_id':cfg['run_id'],'seat_order':[p['name'] for p in cfg['players']]})
save('game_map.json',game_map);save('stored_replay_reports.json',replay)
conf=set()
for r in offers:
    if r['exchange_index'] or r['author_model']!='Grok':continue
    k=r['offer_decision']; d=next(v for did,v in records[r['game']]['decision_resolved'].items() if int(did.rsplit('-',1)[1])==k)
    a=d['attempts'][-1]; content=a.get('assistant_content') or a.get('raw_response',{}).get('choices',[{}])[0].get('message',{}).get('content') or ''
    m=re.search(r'"name"\s*:\s*"([a-z_]+)"',content)
    if m and m[1]!='propose_trade':conf.add(r['thread_id'])
assert len(conf)==64
out['without_conflict_openings']=table([r for r in opening if r['thread_id'] not in conf])
out['without_grok_authors']=table([r for r in opening if r['author_model']!='Grok'])
weights={ref:{} for ref in ['author_only','neither','pooled']}
for ref in weights:
    numerator=denominator=0
    for m in models:
        a,b=pair([r for r in opening if r['author_model']==m],'swap')
        w=a['n'] if ref=='author_only' else b['n'] if ref=='neither' else a['n']+b['n']
        numerator+=w*(a.get('reject_trade',0)/a['n']-b.get('reject_trade',0)/b['n']); denominator+=w
        weights[ref][m]=w
    weights[ref]['gap_pp']=100*numerator/denominator
out['standardized']=weights
# All 5^5 ordered resamples of five whole seed blocks, retaining four rotations
# and every dependent negotiation in each selected block. Exact enumeration.
out['block_sensitivity']=[]
for b in range(1,6):
    rows=[r for r in opening if (r['game']-1)//4+1==b]
    out['block_sensitivity'].append({'block':b,'seed':cohort[4*(b-1)]['seed'],'swap':pair(rows,'swap'),'cash_bid':pair(rows,'cash_bid'),
       'swap_gap':gap(rows),'cash_gap':gap(rows,'cash_bid'),
       'drop_block_swap_gap':gap([r for r in opening if (r['game']-1)//4+1!=b]),
       'drop_block_cash_gap':gap([r for r in opening if (r['game']-1)//4+1!=b],'cash_bid')})
resampling={}
for name,f,rows in [('swap','swap',opening),('cash_bid','cash_bid',opening),('swap_without_grok','swap',[r for r in opening if r['author_model']!='Grok'])]:
    counts=np.array([[[c.get('reject_trade',0),c['n']] for c in pair([r for r in rows if (r['game']-1)//4==b],f)] for b in range(5)])
    values=[]
    for sample in itertools.product(range(5),repeat=5):
        z=counts[list(sample)].sum(axis=0)
        if np.all(z[:,1]>0):values.append(float(100*(z[0,0]/z[0,1]-z[1,0]/z[1,1])))
    resampling[name]={'point_pp':gap(rows,f),'percentile_95_band_pp':np.quantile(values,[.025,.975]).tolist(),'defined_samples':len(values),'total_samples':3125}
out['block_resampling']=resampling
save('offer_analysis.json',out)

board=read(ROOT/'contracts/data/board.json'); costs=board['house_cost_by_group']
spaces={re.sub('[^A-Z0-9]+','_',s['name'].upper()).strip('_'):s for s in board['spaces']}
necessary=[]; unlocked=[]; initial_enough=0
for e in episodes:
    rec=records[e['game']];did=e['decisions'][0];start=rec['decision_started'][did]['prompt_payload'];you=start['game_state']['you'];opts=start['action_state']['scenario']['options'];initial=set(opts['mortgageable_space_keys'])
    listed=sum(spaces[k]['price']//2 for k in initial)
    salvage=sum((5 if h['hotel'] else h['houses'])*costs.get(spaces[h['space_key']]['group'],0)//2 for h in you['holdings']['owned'])
    bound=you['cash']+salvage+sum(spaces[h['space_key']]['price']//2 for h in you['holdings']['owned'] if not h['mortgaged'])
    assert bound==e['upper_bound']
    if e['outcome']=='paid' and you['cash']+listed>=e['debt']: initial_enough+=1
    extra=[];sales=[]
    for d in e['decisions']:
        a=rec['decision_resolved'][d]['final_action']
        if a['action']=='sell_houses_or_hotel':sales.append(d)
        if a['action']=='mortgage_property' and a['args']['space_key'] not in initial:
            k=a['args']['space_key'];assert sales and k in rec['decision_started'][d]['prompt_payload']['action_state']['scenario']['options']['mortgageable_space_keys']
            extra.append({'decision_id':d,'deed':k,'mortgage_value':spaces[k]['price']//2})
    if e['outcome']=='paid' and extra:unlocked.append({'game':e['game'],'decision':e['first_decision'],'model':e['model'],'extra':extra})
    if you['cash']+listed+salvage<e['debt']<=bound:
        r=rec['decision_resolved'][did];att=r['attempts'][-1];msg=att.get('raw_response',{}).get('choices',[{}])[0].get('message',{})
        necessary.append({'game':e['game'],'decision':e['first_decision'],'model':e['model'],'outcome':e['outcome'],'cash':you['cash'],'salvage':salvage,'listed_mortgages':listed,'initial_total':you['cash']+salvage+listed,'debt':e['debt'],'bound':bound,
          'private_note':r['final_action'].get('private_thought'),'provider_reasoning':msg.get('reasoning'),'assistant_content':att.get('assistant_content'),'first_action':r['final_action']['action'],'source_run':runs[e['game']],'decision_id':did})
assert len(necessary)==16 and Counter(r['outcome'] for r in necessary)=={'paid':14,'bankrupt':2}
assert len(unlocked)==19 and sum(len(r['extra']) for r in unlocked)==33
finance={'episodes':len(episodes),'outcomes':dict(Counter(e['outcome'] for e in episodes)),'one_action_payments':sum(e['outcome']=='paid' and len(e['actions'])==1 for e in episodes),'initial_cash_mortgages_sufficient_payments':initial_enough,'necessary':necessary,'unlocked_uses':unlocked}
save('finance_analysis.json',finance)

def acr(c): return f"{c['n']} ({c.get('accept_trade',0)}/{c.get('counter_trade',0)}/{c.get('reject_trade',0)})"
labels={'swap':'Swap','cash_bid':'Cash bid','other':'Other'}; clabel={'author_only':'Proposer only','recipient_only':'Recipient only','both':'Both','neither':'Neither'}
lines=[]
for f in forms:
    for c in cells:lines.append(f"{labels[f]} & {clabel[c]} & {acr(out['full'][f][c])} & {acr(out['opening'][f][c])} & {acr(out['later'][f][c])} \\")
# TeX row terminators need two backslashes.
(HERE/'sections/full_offer_rows.tex').write_text('\n'.join(x+'\\' for x in lines)+'\n')
for group,key in [('proposer','author_model'),('recipient','recipient_model')]:
    lines=[]
    for m in models:
        for f in ['swap','cash_bid']:
            a,b=pair([r for r in opening if r[key]==m],f)
            lines.append(f"{m} & {labels[f]} & {acr(a)} & {acr(b)} \\")
    (HERE/f'sections/{group}_rows.tex').write_text('\n'.join(x+'\\' for x in lines)+'\n')
def shortmodel(m):return next(v for k,v in [('gpt','Sol'),('gemini','Gemini'),('claude','Opus'),('grok','Grok')] if m.startswith(k))
lines=[]
for e in necessary:lines.append(f"G{e['game']} d{e['decision']} & {shortmodel(e['model'])} & {e['cash']} & {e['salvage']} & {e['listed_mortgages']} & {e['debt']} & {e['bound']} & {e['outcome']} \\")
(HERE/'sections/necessary_rows.tex').write_text('\n'.join(x+'\\' for x in lines)+'\n')
def tex(s):
    escapes={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(escapes.get(c,c) for c in s).replace('\n\n',r'\par ')
texts=[]
for e in necessary:
    channel='applied private note' if e['private_note'] else 'returned provider explanation'
    t=e['private_note'] or e['provider_reasoning']
    texts.append(r'\Needspace{10\baselineskip}\subsection*{G%d d%d, %s, %s}'%(e['game'],e['decision'],shortmodel(e['model']),e['outcome']))
    texts.append(r'{\small\textit{%s. Full field from the first resolved decision.}\par %s\par}'%(channel,tex(t)))
(HERE/'sections/necessary_texts.tex').write_text('\n'.join(texts)+'\n')
lines=[]
for g in game_map:
    short=g['source_run'].split('/')[-2]
    lines.append(f"G{g['game']} & {g['seed']} & {g['rotation']} & {g['winner']} & {g['turns']} & \\texttt{{{short}}} \\")
(HERE/'sections/game_rows.tex').write_text('\n'.join(x+'\\' for x in lines)+'\n')
lines=[]
for b in out['block_sensitivity']:
    fmt=lambda p:'/'.join(str(p.get(k,0)) for k in ['reject_trade','n'])
    a,c=b['swap'];d,e=b['cash_bid']
    lines.append(f"{b['block']} & {fmt(a)} & {fmt(c)} & {b['swap_gap']:.1f} & {fmt(d)} & {fmt(e)} & {b['cash_gap']:.1f} \\")
(HERE/'sections/block_rows.tex').write_text('\n'.join(x+'\\' for x in lines)+'\n')
for filename in ['full_offer_rows','proposer_rows','recipient_rows','necessary_rows','game_rows','block_rows']:
    p=HERE/f'sections/{filename}.tex'
    p.write_text(p.read_text()+r'\bottomrule'+'\n')
# Plot all five block estimates instead of connecting unordered offer forms.
fig,ax=plt.subplots(figsize=(7.2,3.2)); colors=['#215a80','#b16a21']
for i,(f,col) in enumerate(zip(['swap_gap','cash_gap'],colors)):
    ax.scatter([b[f] for b in out['block_sensitivity']],np.arange(1,6)+(i-.5)*.15,c=col,s=45,label=['Swap','Cash bid'][i])
ax.axvline(0,color='gray',lw=.8);ax.set_yticks(range(1,6),[f'Seed block {i}' for i in range(1,6)]);ax.invert_yaxis();ax.set_xlabel('Opening rejection gap, proposer-only minus neither (percentage points)');ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(HERE/'assets/block_sensitivity.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.8));ys=np.arange(16)
ax.barh(ys,[r['initial_total'] for r in necessary],color='#a4b4bf',label='Cash + all salvage + initial mortgages')
ax.barh(ys,[r['bound']-r['initial_total'] for r in necessary],left=[r['initial_total'] for r in necessary],color='#397ca1',label='Additional mortgage principal')
ax.scatter([r['debt'] for r in necessary],ys,c=['#b13c31' if r['outcome']=='bankrupt' else '#111111' for r in necessary],marker='|',s=130,zorder=3)
ax.set_yticks(ys,[f"G{r['game']} d{r['decision']}" for r in necessary],fontsize=8);ax.invert_yaxis();ax.set_xlabel('Game dollars; vertical mark is the debt (red = declared bankruptcy)');ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),fontsize=8,frameon=False);ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(HERE/'assets/necessary_collateral.pdf');plt.close(fig)
save('analysis_sources.json',sources)
print(json.dumps({'opening':out['opening'],'standardized':weights,'resampling':resampling,'blocks':out['block_sensitivity'],'necessary':[{k:r[k] for k in ['game','decision','outcome','cash','salvage','listed_mortgages','debt','bound']} for r in necessary],'replay_totals':{k:sum(r[k] for r in replay) for k in ['artifact_events','state_events']}},indent=2))
