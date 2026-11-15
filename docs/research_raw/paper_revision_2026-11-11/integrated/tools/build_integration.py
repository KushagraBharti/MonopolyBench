"""Build manuscript tables/figures from owned, frozen record tabulations.

No engine import, simulation, model call, or newly played action.
"""
from pathlib import Path
from collections import Counter
import json, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in HERE.parents if (p/'contracts').is_dir())
DATA=HERE/'data'; SEC=HERE/'sections'; ASSETS=HERE/'assets'
def read(name): return json.loads((DATA/name).read_text())
def esc(s):
    replacements={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','"':r'\char34{}'}
    return ''.join(replacements.get(c,c) for c in s).replace('\n',r'\par ')

offers=read('offers.json'); legal=[r for r in offers if r['accept_available']]
assert len(offers)==920 and len(legal)==918
def pair(rs):
    return [[r for r in rs if r['completion_cell']==c and r['request']['properties']]
            for c in ['author_only','neither']]
def summary(rs):
    return {'n':len(rs),**dict(Counter(r['response'] for r in rs))}
def reject(rs): return sum(r['response']=='reject_trade' for r in rs)
def form(r):
    a,b=r['offer'],r['request']
    if a['properties'] and b['properties']:return 'swap'
    if b['properties'] and not a['properties'] and a['cash']>0 and b['cash']==0 and not a['get_out_of_jail_cards'] and not b['get_out_of_jail_cards']:return 'cash_bid'
    return 'other'
opening=[r for r in legal if r['exchange_index']==0]
later=[r for r in legal if r['exchange_index']>0]
summaries={s:[summary(rs) for rs in pair(rows)] for s,rows in [('opening',opening),('later',later)]}
assert [reject(r) for r in pair(opening)]==[138,105]
assert [len(r) for r in pair(opening)]==[187,176]
assert [reject(r) for r in pair(later)]==[21,20]
rows=[];forms={}
for f,label in [('swap','Swap'),('cash_bid','Cash bid')]:
    forms[f]=[summary(x) for x in pair([r for r in opening if form(r)==f])]
    for kind,x in zip(['Proposer only','Neither'],pair([r for r in opening if form(r)==f])):
        c=Counter(r['response'] for r in x)
        rows.append(f"{label} & {kind} & {len(x)} & {c['accept_trade']} & {c['counter_trade']} & {c['reject_trade']} \\\\")
assert [x['reject_trade'] for x in forms['swap']]==[95,37]
assert [x['n'] for x in forms['swap']]==[116,72]
assert [x['reject_trade'] for x in forms['cash_bid']]==[42,67]
assert [x['n'] for x in forms['cash_bid']]==[70,103]
table=r'''\begin{table}[t]\centering\small
\begin{tabularx}{\linewidth}{@{}lYrrrr@{}}\toprule
Opening form & Completes & Offers & Accept & Counter & Reject\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabularx}
\caption{Opening responses by offer form. Swaps exchange deeds in both directions and may include cash. Pure cash bids offer cash for deeds without reciprocal deeds or jail cards. Completion is evaluated after the proposed transfer. The two other opening deed requests in these completion categories are both rejected; the full 918-offer table is in the appendix.}
\label{tab:opening}\end{table}
'''
(SEC/'opening_table.tex').write_text(table)

# Verify unchanged-bundle concession subset against the owned offer ledger.
con=read('concessions.json')['concession_rows']; index={(r['game'],r['decision']):r for r in offers}
selected=[(c,index[(c['game'],c['decision'])]) for c in con]
cc={cell:summary([r for c,r in selected if c['cell']==cell and r['request']['properties']]) for cell in ['Author only','Neither']}
assert (cc['Author only']['n'],cc['Author only']['accept_trade'])==(58,9)
assert (cc['Neither']['n'],cc['Neither']['accept_trade'])==(56,17)

# Debt rows: names are preserved in source records, mapped only for display.
def model(s):
    return next(m for m,key in [('Sol','sol'),('Gemini','argon'),('Opus','opus'),('Grok','grok')] if key in s.lower())
eps=read('liquidation_episodes.json'); unlock=read('review_additions.json')['unlocked_collateral']
uc=Counter(model(r['model']) for r in unlock['rows']); debtrows=[]
for m in ['Sol','Gemini','Opus','Grok']:
    allm=[r for r in eps if model(r['model'])==m]; paid=[r for r in allm if r['outcome']=='paid']
    debtrows.append(f"{m} & {len(allm)} & {len(paid)} & {sum(len(r['actions'])>1 for r in paid)} & {uc[m]} \\\\")
debtrows.append(r'\midrule All &188&128&61&19\\\bottomrule')
(SEC/'debt_rows.tex').write_text('\n'.join(debtrows)+'\n')
assert len(eps)==188 and sum(r['outcome']=='paid' for r in eps)==128
assert len(unlock['rows'])==19 and sum(len(r['rows']) for r in unlock['rows'])==33

# New quote: preserve exact field, source bytes, metadata and spans.
quotes=read('additional_quote_manifest.json')['quotes']; tex=[]
for q in quotes:
    blob=(ROOT/q['source']).read_bytes();assert hashlib.sha256(blob).hexdigest()==q['source_sha256']
    obj=json.loads(blob.splitlines()[q['jsonl_line_1based']-1])
    for k in q['json_pointer'].strip('/').split('/'): obj=obj[k]
    assert hashlib.sha256(obj.encode()).hexdigest()==q['field_sha256']
    for sp in q['spans']: assert obj[slice(*sp['span'])]==sp['text']
    excerpt=r' \textnormal{[\ldots]} '.join(esc(sp['text']) for sp in q['spans'])
    tex.append(r'\DeclareTranscriptQuote{'+q['id']+'}{'+esc(q['metadata'])+'}{'+excerpt+'}')
(SEC/'additional_quotes.tex').write_text('\n'.join(tex)+'\n')

# Figures: accessible blue/orange plus redundant point and line encodings.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
colors=['#17678D','#B45B18']; markers=['o','s']
fig,axs=plt.subplots(1,2,figsize=(8.0,3.6),gridspec_kw={'width_ratios':[.9,1.25]})
for j,label in enumerate(['Proposer completes only','Neither completes; deed requested']):
    ys=[]
    for i,f in enumerate(['swap','cash_bid']):
        rs=[r for r in opening if form(r)==f]
        x=pair(rs)[j];n=len(x);r=reject(x);y=r/n*100;ys.append(y)
        axs[0].annotate(f'{r}/{n}',(i,y),xytext=(0,9 if j==0 else -17),textcoords='offset points',ha='center',fontsize=9)
    axs[0].plot([0,1],ys,marker=markers[j],color=colors[j],linestyle='-' if j==0 else '--',label=label)
axs[0].set(xticks=[0,1],xticklabels=['Swap','Cash bid'],ylim=(0,100),ylabel='Rejected offers (%)',title='A. Opening offer form\nAll configurations',xlim=(-.3,1.3))
cashdata={}
for j in range(2):
    ys=[]
    for i,(key,predicate) in enumerate([('<100',lambda c:c<100),('100–299',lambda c:100<=c<300),('≥300',lambda c:c>=300)]):
        rs=[r for r in opening if r['recipient_model']!='Opus' and predicate(r['recipient_cash_before'])]
        x=pair(rs)[j];n=len(x);r=reject(x);y=r/n*100;ys.append(y)
        cashdata.setdefault(key,[]).append(summary(x))
        axs[1].annotate(f'{r}/{n}',(i,y),xytext=(0,9 if j==0 else -17),textcoords='offset points',ha='center',fontsize=9)
    axs[1].plot(range(3),ys,marker=markers[j],color=colors[j],linestyle='-' if j==0 else '--')
axs[1].set(xticks=range(3),xticklabels=['Under $100','$100–299','$300 or more'],ylim=(0,100),title='B. Holder cash\nSol, Gemini and Grok openings',xlim=(-.3,2.3))
for ax in axs: ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,-.01),fontsize=9)
fig.tight_layout(rect=(0,.08,1,1));fig.savefig(ASSETS/'bargaining_conditions.pdf',bbox_inches='tight');fig.savefig(ASSETS/'bargaining_conditions.png',dpi=180,bbox_inches='tight');plt.close(fig)

fig,(ax,flow)=plt.subplots(1,2,figsize=(8.2,3.8),gridspec_kw={'width_ratios':[1,1.5]})
labels=['Debt paid','Above own-\nasset bound','Menu-restricted\nelimination','Payable\ndeclaration'];vals=[128,56,1,3]
ax.barh(range(4),vals,color=['#17678D','#90969B','#C99B57','#B45B18']);ax.invert_yaxis()
ax.set(yticks=range(4),yticklabels=labels,xlim=(0,150),xlabel='Episodes',title='A. All 188 episodes')
for i,v in enumerate(vals):ax.text(v+2,i,str(v),va='center',fontsize=10)
flow.set(xlim=(0,1),ylim=(0,1),title='B. Newly unlocked collateral');flow.axis('off')
for y,t in [(.82,'Sell buildings in\na developed group'),(.51,'Mortgage deeds absent\nfrom the first menu'),(.20,'Use the proceeds\nto pay the current debt')]:
    flow.add_patch(FancyBboxPatch((.02,y-.10),.96,.19,boxstyle='round,pad=.02',facecolor='#EDF3F6',edgecolor='#7B9BAA'))
    flow.text(.5,y,t,ha='center',va='center',fontsize=10)
for y in [.68,.37]:flow.annotate('',xy=(.5,y-.07),xytext=(.5,y+.03),arrowprops={'arrowstyle':'->','color':'#17678D'})
flow.text(.5,-.07,'19 payments · 33 new mortgages\nAll four systems',ha='center',fontsize=9.5)
fig.tight_layout();fig.savefig(ASSETS/'financial_execution.pdf',bbox_inches='tight');fig.savefig(ASSETS/'financial_execution.png',dpi=180,bbox_inches='tight');plt.close(fig)

out={'opening_later':summaries,'opening_forms':forms,'cash_opening_excluding_opus':cashdata,'concessions_deed_requests':cc,'unlocked_episodes':19,'unlocked_actions':33}
(DATA/'integration_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
