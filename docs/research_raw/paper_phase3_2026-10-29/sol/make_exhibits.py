"""Publication alternates from frozen audited JSON, with semantic assertions."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter, FixedLocator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
P2=ROOT/'docs/research_raw/paper_phase2_2026-10-28/core_review'
OUT=HERE/'exhibits'
OUT.mkdir(exist_ok=True)
INPUTS=[P2/'sol/corpus_economics_audit.json',P2/'astra/development_aggregation_check.json',
        P2/'astra/negotiation_units.json',P2/'sol/build_recovery_audit.json']
data=json.loads(INPUTS[0].read_text());other=json.loads(INPUTS[1].read_text())
units=data['spending_units'];design=data['design'];tot=data['totals']
assert len(units)==103 and len(design)==20
assert sum(u['spend'] for u in units)==103450==other['summary']['spend']
assert sum(u['whole_game_developed_rent'] for u in units)==93000
assert sum(u['developed_rent_after_first_own_spend'] for u in units)==92550
assert sum(u['winner_actor'] for u in units)==58
assert sum(u['whole_game_developed_rent']==0 for u in units)==40
assert sum(len(u['rent_events']) for u in units)>0
assert sorted(len([d for d in design if d['seed']==s]) for s in set(d['seed'] for d in design))==[4]*5

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'svg.fonttype':'none','savefig.facecolor':'white'})
NAMES={'gpt-6.1-sol':'Sol','gemini-4-argon':'Gemini Argon','claude-opus-5.5':'Opus','grok-4.7':'Grok'}
COLORS={'Sol':'#27627B','Gemini Argon':'#A25E26','Opus':'#755A83','Grok':'#547044'}
captions={}
def save(fig,name,caption):
    fig.savefig(OUT/f'{name}.png',dpi=220,bbox_inches='tight')
    fig.savefig(OUT/f'{name}.svg',bbox_inches='tight')
    plt.close(fig);captions[name]=caption

# S1. Keep seed blocks visible rather than rank bars.
fig,ax=plt.subplots(figsize=(9,4.5));seeds=list(dict.fromkeys(d['seed'] for d in design))
for d in design:
    row=seeds.index(d['seed']);col=(d['game']-1)%4;n=NAMES[d['winner_name']]
    ax.add_patch(plt.Rectangle((col,row),1,1,facecolor=COLORS[n],edgecolor='white',lw=2))
    ax.text(col+.5,row+.48,f"G{d['game']:02d}  {n}\nWinner seat {d['winner'][1:]}\n{d['turns']} turns",ha='center',va='center',color='white',fontsize=9)
ax.set(xlim=(0,4),ylim=(5,0),xticks=[.5,1.5,2.5,3.5],xticklabels=['Rotation 1','Rotation 2','Rotation 3','Rotation 4'],yticks=[i+.5 for i in range(5)],yticklabels=[f'Block {i+1}\nseed {s}' for i,s in enumerate(seeds)])
ax.tick_params(length=0,pad=8)
for spine in ax.spines.values():spine.set_visible(False)
ax.set_title('Observed winners across seed blocks and cyclic rotations',loc='left',pad=15)
save(fig,'s1_seed_rotation','Twenty completed games, grouped by five seed blocks and four cyclic seat rotations. Cells report the winning configured agent, seat and game turns. Shared seeds do not produce identical opportunities; one observed trajectory occupies each cell. These are cohort outcomes, not an intrinsic model ranking.')

# S2. No ROI line; mark inherited development and retain zero receipts.
fig,(ax,b)=plt.subplots(1,2,figsize=(10,5.1),gridspec_kw={'width_ratios':[1.6,1]})
for inherited,marker,label in [(False,'o','No inherited deed at first own spend'),(True,'^','Inherited deed at first own spend')]:
    us=[u for u in units if any(v=='inheritance' for v in u['deed_routes_at_first_own_spend'].values())==inherited]
    ax.scatter([u['spend'] for u in us],[u['developed_rent_after_first_own_spend'] for u in us],marker=marker,s=43,alpha=.65,color='#27627B' if inherited else '#A25E26',label=label,edgecolor='white',linewidth=.5)
ax.set(xlabel='Own construction outlay (game dollars)',ylabel='Paid developed rent after first own spend\n(game dollars)',ylim=(-100,None))
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
handles,legend_labels=ax.get_legend_handles_labels()
fig.legend(handles,legend_labels,loc='lower center',ncol=2,fontsize=8,frameon=False)
ax.set_title('103 spending units, including 40 with no paid rent',loc='left',fontsize=10)
vals=[103450,93000,92550];labels=['Own construction\noutlay','Whole-game paid\ndeveloped rent','Paid rent after\nfirst own spend']
b.barh(range(3),vals,color=['#62676B','#27627B','#5B8396']);b.set_yticks(range(3),labels);b.invert_yaxis();b.set_xlim(0,125000)
for i,v in enumerate(vals):b.text(v+1800,i,f'{v:,}',va='center',fontsize=9)
b.set_xlabel('Sum across spending units (game dollars)');b.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
b.xaxis.set_major_locator(FixedLocator([0,50000,100000]))
b.set_title('A timing filter removes 450 dollars',loc='left',fontsize=10)
fig.suptitle('Construction and observed rent require distinct accounting windows',x=.01,ha='left',fontsize=13);fig.tight_layout(rect=[0,.06,1,1])
save(fig,'s2_spending_windows','Each point is one game/player/color group with positive own house or hotel spending. Paid developed rent is shown after the first own expenditure; triangles contain an inherited deed at that point. Totals compare this window with whole-game receipts. The 450-dollar difference is pre-spending income from inherited G2 light blues. Paid rent excludes unpaid bankruptcy debts. Neither window is incremental return; inherited improvements, salvage, acquisition cost, timing and terminal censoring remain separate.')

# S3. Two observed spending units on the same deeds, without an intervention claim.
us=sorted([u for u in units if u['game']==19 and u['group']=='DARK_BLUE'],key=lambda u:u['first_own_spend_event'])
assert len(us)==2 and sum(u['whole_game_developed_rent'] for u in us)==1575
d=next(d for d in design if d['game']==19)
fig,axes=plt.subplots(2,1,figsize=(9,5),sharex=True)
for ax,u in zip(axes,us):
    n=NAMES[d['seats'][u['actor']]];start=u['first_complete_route']['boundary_seq']
    xs=[start];ys=[0];total=0
    for e in u['rent_events']:total+=e['amount'];xs.append(e['seq']);ys.append(total)
    ax.step(xs,ys,where='post',color=COLORS[n],lw=2)
    ax.scatter([xs[-1]],[total],color=COLORS[n],zorder=3)
    ax.annotate(f'{total:,}',(xs[-1],total),xytext=(8,5),textcoords='offset points',fontsize=9)
    ax.axvline(u['first_own_spend_event'],color=COLORS[n],ls=':',alpha=.8)
    ax.scatter([start],[0],color=COLORS[n],marker='s',zorder=3)
    ax.set_ylabel('Cumulative paid rent\n(game dollars)');ax.set_ylim(-60,1750);ax.set_title(f"{n}, {u['actor']}: {u['spend']:,} spent, {u['salvage']:,} sale proceeds, {total:,} paid rent",loc='left',fontsize=10)
    ax.text(.98,.15,f"Completion by {u['first_complete_route']['route'].replace('_',' ')}",transform=ax.transAxes,ha='right',fontsize=9)
axes[-1].set_xlabel('Canonical event sequence in game 19 (events, not turns or elapsed time)')
fig.suptitle('The same dark-blue deeds under successive owners',x=.01,ha='left',fontsize=13);fig.tight_layout()
save(fig,'s3_g19_dark_blue','Observed receipts for two game/player/dark-blue spending units on the same deeds in G19. Squares mark observed complete-ownership boundaries; dotted lines mark first own spending. Lines stop at each unit\'s last paid-rent event, not at the end of ownership. Panels share scales and retain different owners, inherited routes and spending/sale histories. Event order is not time at risk. This contrast does not identify an owner effect, a return caused by construction, or a counterfactual investment outcome.')

with (OUT/'spending_units.csv').open('w') as f:
    fields=['game','actor','group','spend','salvage','whole_game_developed_rent','developed_rent_after_first_own_spend','winner_actor','inherited_at_first_own_spend']
    w=csv.DictWriter(f,fields);w.writeheader()
    for u in units:w.writerow({**{k:u[k] for k in fields[:-1]},'inherited_at_first_own_spend':any(v=='inheritance' for v in u['deed_routes_at_first_own_spend'].values())})
neg=json.loads(INPUTS[2].read_text())['summary']['initiation']
with (OUT/'negotiation_denominators.csv').open('w') as f:
    fields=['model','eligible_decisions','proposals','eligible_turns','proposing_turns','zero_proposal_games','turn_propensity','intensity'];w=csv.DictWriter(f,fields);w.writeheader()
    for model,u in neg.items():w.writerow(dict(model=model,**u,turn_propensity=u['proposing_turns']/u['eligible_turns'],intensity=u['proposals']/u['proposing_turns']))
manifest={'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha256(p.read_bytes()).hexdigest()} for p in INPUTS],
          'upstream_game_hashes':data['source_hashes'],'captions':captions,'checks':{'spending_units':103,'outlay':103450,'whole_game_rent':93000,'post_first_spend_rent':92550,'zero_rent_units':40,'winner_spending_units':58,'games':20,'seed_blocks':5},
          'limits':'Reporting transformations rechecked here; upstream event reconstruction adopted from phase2, not rerun as part of figure generation.',
          'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
manifest['outputs']={p.name:sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in {'.png','.svg','.csv'}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest['checks']))
