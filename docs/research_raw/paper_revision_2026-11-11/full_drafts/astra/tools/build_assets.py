"""Publication assets from existing-record tabulations; no gameplay execution."""
from pathlib import Path
import collections
import json
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[4]
OLD=ROOT/'docs/research_raw/paper_rewrite_2026-11-10'
A=json.loads((HERE/'data/analysis.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                    'axes.spines.right':False,'pdf.fonttype':42,'savefig.facecolor':'white'})
fig,ax=plt.subplots(figsize=(7.2,4.4))
rows=[r for r in A['price_cells'] if r['kind']=='ask' and r['stage']=='all' and
      r['False']['n'] and r['True']['n']]
assert len(rows)==7
for i,r in enumerate(rows):
    left,right=r['False'],r['True']
    ax.plot([left['median_ratio'],right['median_ratio']],[i,i],color='#b9bec4',lw=2,zorder=1)
    for point,color,marker,offset in [(left,'#465766','o',-.18),(right,'#b15e20','s',.18)]:
        ax.scatter(point['median_ratio'],i,color=color,marker=marker,s=42,zorder=3)
        ax.annotate(f"n={point['n']}",(point['median_ratio'],i),xytext=(0,11 if offset<0 else -17),
                    textcoords='offset points',ha='center',fontsize=8.3)
ax.set_yticks(range(len(rows)),[r['author']+' · '+('mortgaged' if r['mortgaged'] else 'unmortgaged') for r in rows])
ax.invert_yaxis();ax.set_ylim(len(rows)-.45,-.65);ax.set_xlim(0,4.55)
ax.set_xlabel('Median requested cash / board purchase price')
ax.scatter([],[],label='Buyer does not complete',color='#465766',marker='o')
ax.scatter([],[],label='Buyer completes',color='#b15e20',marker='s')
ax.legend(loc='lower right',frameon=False,fontsize=8.8)
ax.grid(axis='x',color='#eeeeee');ax.set_axisbelow(True)
fig.tight_layout();fig.savefig(HERE/'assets/asking_prices.pdf');fig.savefig(HERE/'assets/asking_prices.png',dpi=180);plt.close(fig)

debts=json.loads((HERE/'data/liquidation_episodes.json').read_text())
hist=collections.Counter(len(r['actions']) for r in debts if r['outcome']=='paid')
fig,axes=plt.subplots(1,2,figsize=(7.2,3.5),gridspec_kw={'width_ratios':[1,1.35]})
ax=axes[0];xs=sorted(hist);ax.bar(xs,[hist[x] for x in xs],color='#375c75',width=.68)
for x in xs:ax.text(x,hist[x]+1,str(hist[x]),ha='center',fontsize=9)
ax.set_ylim(0,76);ax.set_xticks([1,2,3,4,5,6,7,10]);ax.set_xlabel('Actions before payment');ax.set_ylabel('Paid episodes')
ax.set_title('128 executed payments',loc='left',fontsize=11)
ax=axes[1];labels=['Paid: one action','Paid: multiple actions','Insufficient asset bound','Menu restriction','Payable declaration'];vals=[67,61,56,1,3]
assert sum(vals)==188
bars=ax.barh(range(5),vals,color=['#375c75','#587f97','#898b8b','#b7a17b','#b15e20'])
for i,v in enumerate(vals):ax.text(v+1,i,str(v),va='center',fontsize=9)
ax.set_yticks(range(5),labels,fontsize=9);ax.invert_yaxis();ax.set_xlim(0,76);ax.set_xlabel('Episodes');ax.set_title('188 liquidation episodes',loc='left',fontsize=11)
fig.tight_layout(w_pad=2);fig.savefig(HERE/'assets/liquidation_paths.pdf');fig.savefig(HERE/'assets/liquidation_paths.png',dpi=180);plt.close(fig)

def esc(s):
    return s.replace('&',r'\&').replace('_',r'\_').replace('%',r'\%')
lines=[r'\begin{table}[ht]\centering\small',r'\begin{tabular}{@{}lrrr@{}}\toprule',
       r'Completion & All: N (A/C/R) & Opening: N (A/C/R) & Later: N (A/C/R)\\\midrule']
for cell,label in [('author_only','Author only'),('recipient_only','Recipient only'),('both','Both'),('neither','Neither')]:
    vals=[]
    for stage in ['all','opening','later']:
        r=A['responses'][cell+'/'+stage]
        vals.append(f"{r['n']} ({r.get('accept_trade',0)}/{r.get('counter_trade',0)}/{r.get('reject_trade',0)})")
    lines.append(label+' & '+' & '.join(vals)+r'\\')
lines += [r'\bottomrule\end{tabular}',r'\caption{All 918 acceptance-legal offers. A/C/R denote acceptance, counter and rejection.}\label{tab:offerfull}\end{table}']
(HERE/'sections/offer_table.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{longtable}{@{}llrrrr@{}}',r'\caption{Rejection counts by recipient and thread position. Cells show rejected/received.}\label{tab:strata}\\',
       r'\toprule Recipient & Position & Author only & Recipient only & Both & Neither\\\midrule\endhead']
for model in ['Sol','Gemini','Opus','Grok']:
    for stage in ['opening','later']:
        vals=[]
        for cell in ['author_only','recipient_only','both','neither']:
            r=A['by_recipient'][model][cell+'/'+stage];vals.append(f"{r.get('reject_trade',0)}/{r['n']}")
        lines.append(model+' & '+stage+' & '+' & '.join(vals)+r'\\')
lines += [r'\bottomrule\end{longtable}']
(HERE/'sections/strata_table.tex').write_text('\n'.join(lines)+'\n')

# Copy the two exact system prompts from a saved first refusal/recovery chain.
offers=json.loads((OLD/'data/agenda_offers.json').read_text())
run=ROOT/next(r['source_run'] for r in offers if r['game']==1)
rows=[json.loads(l) for l in (run/'decisions.jsonl').read_text().splitlines()]
chain=next(r for r in rows if r['phase']=='decision_resolved' and len(r['attempts'])==2 and
           r['attempts'][1].get('response_condition')=='same_model_without_private_thought')
initial=next(r for r in rows if r['phase']=='decision_started' and r['decision_id']==chain['decision_id'])
for label,messages in [('standard',initial['prompt_messages']),('recovery',chain['attempts'][1]['prompt_messages'])]:
    prompt=next(m['content'] for m in messages if m['role']=='system')
    (HERE/'data'/f'{label}_system_prompt.txt').write_text(prompt)
    wrapped='\n'.join(textwrap.fill(line,width=88,replace_whitespace=False,break_long_words=False,break_on_hyphens=False) for line in prompt.splitlines())
    assert ''.join(prompt.split())==''.join(wrapped.split())
    (HERE/'data'/f'{label}_system_prompt_wrapped.txt').write_text(wrapped+'\n')
    (HERE/'sections'/f'{label}_prompt.tex').write_text('\\begingroup\\scriptsize\n\\begin{verbatim}\n'+wrapped+'\n\\end{verbatim}\n\\endgroup\n')
print('Built two figures, two native tables, and verbatim standard/recovery prompts.')
