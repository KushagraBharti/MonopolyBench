"""Descriptive analysis of saved observations. No engine or model imports."""
from pathlib import Path
from collections import Counter
from itertools import product
import json, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in HERE.parents if (p/'contracts').is_dir())
read=lambda name:json.loads((HERE/'data'/name).read_text())
offers=read('offers.json'); legal=[r for r in offers if r['accept_available']]
opening=[r for r in legal if r['exchange_index']==0]
finance=read('necessary_collateral.json')
necessary=finance['necessary_unlocked_collateral']
eps=read('liquidation_episodes.json')
cells=['author_only','recipient_only','both','neither']
names=['Proposer only','Recipient only','Both','Neither']
models=['Sol','Gemini','Opus','Grok']
def form(r):
    a,b=r['offer'],r['request']
    if a['properties'] and b['properties']:return 'Swap'
    if not a['get_out_of_jail_cards'] and not b['get_out_of_jail_cards']:
        if b['properties'] and not a['properties'] and a['cash']>0 and b['cash']==0:return 'Cash bid'
        if a['properties'] and not b['properties'] and b['cash']>0 and a['cash']==0:return 'Cash ask'
    return 'Other'
def count(rs):
    c=Counter(r['response'] for r in rs)
    return [len(rs),c['accept_trade'],c['counter_trade'],c['reject_trade']]
def pair(rs):return [count([r for r in rs if r['completion_cell']==c]) for c in ['author_only','neither']]
def gap(rs):
    a,b=pair(rs)
    return 100*(a[3]/a[0]-b[3]/b[0]) if a[0] and b[0] else None
tab={stage:{f:{c:count([r for r in rows if form(r)==f and r['completion_cell']==c]) for c in cells}
            for f in ['Swap','Cash bid','Cash ask','Other']}
     for stage,rows in [('Opening',opening),('Later',[r for r in legal if r['exchange_index']>0])]}
rows=[]
for stage,forms in tab.items():
    for f,cc in forms.items():
        for c,name in zip(cells,names):rows.append(' & '.join(map(str,[stage,f,name]+cc[c]))+r' \\')
(HERE/'sections/full_offer_table.tex').write_text(r'''\begin{longtable}{@{}lllrrrr@{}}
\caption{All legally acceptable offers. Counts include structurally empty cells. A cash ask offers deeds for cash; other forms include jail cards or nonstandard bundles.}\label{tab:full-offers}\\
\toprule Stage & Form & Newly completes & N & Accept & Counter & Reject\\\midrule\endhead
'''+ '\n'.join(rows)+r'\bottomrule\end{longtable}'+'\n')
orows=[]
for c,name in zip(cells,names):
    values=[]
    for f in ['Swap','Cash bid','Cash ask','Other']:
        n,a,k,r=tab['Opening'][f][c]
        values.append(f'{n} [{a}/{k}/{r}]')
    orows.append(' & '.join([name]+values)+r' \\')
(HERE/'sections/opening_complete.tex').write_text(r'''\begin{table*}[t]\centering\small
\begin{tabular}{@{}lrrrr@{}}\toprule
Newly completes & Swap & Cash bid & Cash ask & Other\\\midrule
'''+ '\n'.join(orows)+r'''
\bottomrule\end{tabular}
\caption{Every opening offer where acceptance is legal: N [accept/counter/reject]. Swaps transfer deeds in both directions; cash bids request deeds; cash asks offer deeds. The other category retains bundles outside these definitions. Completion concerns proposed ownership, not immediate ability to build. The appendix gives all later offers too.}\label{tab:opening-all}
\end{table*}'''+'\n')
swap=[r for r in opening if form(r)=='Swap']
proposer={m:pair([r for r in swap if r['author_model']==m]) for m in models}
prows=[]
for m,(a,b) in proposer.items():prows.append(f'{m} & {a[3]}/{a[0]} & {b[3]}/{b[0]} & {100*(a[3]/a[0]-b[3]/b[0]):.1f}'+r' \\')
(HERE/'sections/proposer_rows.tex').write_text('\n'.join(prows)+'\n'+r'\bottomrule'+'\n')
conf={r['thread'] for r in json.loads((HERE/'qa/fable_cross_review_reproduction.json').read_text())['conflict_openings']}
populations={'All swaps':swap,'No Grok authors':[r for r in swap if r['author_model']!='Grok'],
             'No conflicting openings':[r for r in swap if r['thread_id'] not in conf],
             'Cash bids':[r for r in opening if form(r)=='Cash bid']}
stability={}
for name,rs in populations.items():
    bc=[pair([r for r in rs if (r['game']-1)//4==b]) for b in range(5)]
    draws=[]
    for sample in product(range(5),repeat=5):
        a=np.sum([bc[b][0] for b in sample],axis=0);b=np.sum([bc[b][1] for b in sample],axis=0)
        if a[0] and b[0]:draws.append(100*(a[3]/a[0]-b[3]/b[0]))
    loo=[gap([r for r in rs if (r['game']-1)//4!=b]) for b in range(5)]
    blockg=[gap([r for r in rs if (r['game']-1)//4==b]) for b in range(5)]
    stability[name]={'gap_pp':gap(rs),'counts':pair(rs),'by_block':bc,'block_gaps':blockg,
                     'leave_one_block_out':loo,'resampling_percentiles':np.percentile(draws,[2.5,97.5]).tolist(),
                     'valid_resamples':len(draws),'total_resamples':3125}
rows=[]
for name,s in stability.items():
    lo,hi=s['resampling_percentiles'];loo=s['leave_one_block_out']
    rows.append(f"{name} & {s['gap_pp']:.1f} & [{lo:.1f}, {hi:.1f}] & [{min(loo):.1f}, {max(loo):.1f}]"+r' \\')
(HERE/'sections/stability_rows.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(6.6,2.8))
for i,(name,s) in enumerate(stability.items()):
    lo,hi=s['resampling_percentiles']; ax.plot([lo,hi],[i,i],color='#8b9ca8',lw=3)
    ax.scatter(s['block_gaps'],[i]*5,s=25,marker='|',color='#b35806',zorder=3)
    ax.scatter([s['gap_pp']],[i],s=40,color='#2166ac',zorder=4)
ax.axvline(0,color='gray',lw=.6);ax.set(yticks=range(4),yticklabels=list(stability),xlabel='Rejection difference, percentage points');ax.invert_yaxis()
ax.grid(axis='x',alpha=.15);fig.tight_layout()
fig.savefig(HERE/'assets/bargaining_stability.pdf');fig.savefig(HERE/'assets/bargaining_stability.png',dpi=180);plt.close(fig)

bykey={(e['game'],e['first_decision']):e for e in eps}
nr=[]
for r in necessary:
    m=next(m for m,k in [('Sol','sol'),('Gemini','argon'),('Opus','opus'),('Grok','grok')] if k in r['model'].lower())
    base=r['cash']+r['listed_mortgages']+r['salvage']
    channel='Provider text' if m=='Opus' else 'Private note'
    nr.append(f"G{r['game']} d{r['decision']} & {m} & {r['debt']:,} & {base:,} & {r['upper_bound']:,} & {r['outcome']} & {channel}"+r' \\')
(HERE/'sections/necessary_rows.tex').write_text('\n'.join(nr)+'\n'+r'\bottomrule'+'\n')
assert len(necessary)==16 and sum(r['outcome']=='paid' for r in necessary)==14
assert count(legal)==[918,113,393,412]
assert pair(swap)==[[116,1,20,95],[72,17,18,37]]
# Non-necessary categories separate 62 immediately mortgage-funded payments,
# 52 payments requiring sale but not new collateral, and the conflicting Grok declaration.
fig,ax=plt.subplots(figsize=(6.5,2.7))
labels=['Cash + initial mortgages','Sales sufficient without new mortgages','Newly available mortgages necessary']
paid=[62,52,14];declared=[0,1,2]
ax.barh(range(3),paid,color='#2166ac',label='Paid');ax.barh(range(3),declared,left=paid,color='#b35806',label='Declared')
for i,(p,d) in enumerate(zip(paid,declared)):ax.text(p+d+1,i,f'{p}/{p+d} paid',va='center')
ax.set(yticks=range(3),yticklabels=labels,xlim=(0,78),xlabel='Demonstrated-payable episodes');ax.invert_yaxis();ax.legend(frameon=False,loc='lower right')
fig.tight_layout();fig.savefig(HERE/'assets/debt_requirements.pdf');fig.savefig(HERE/'assets/debt_requirements.png',dpi=180);plt.close(fig)

# An explicit entry point maps every displayed G identifier to its canonical saved run.
runs={r['game']:r['source_run'] for r in offers}
(HERE/'data/game_map.json').write_text(json.dumps(runs,indent=2)+'\n')
hashes={str((HERE/'data'/n).relative_to(ROOT)):hashlib.sha256((HERE/'data'/n).read_bytes()).hexdigest() for n in ['offers.json','liquidation_episodes.json','necessary_collateral.json']}
out={'full_offer_table':tab,'proposer':proposer,'stability':stability,'sources':hashes,
     'uncertainty_contract':'Exact enumeration of 5^5 samples of five whole seed blocks with replacement. Central 95% empirical resampling range, not selection-adjusted confidence, independent replication or causal identification.'}
(HERE/'data/revision_analysis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'offers':len(offers),'legal':len(legal),'opening':len(opening),'stability':stability},indent=2))
