import sys,json; sys.path.insert(0,'.')
import dec
from boardinfo import *
D=dec.ROOT+'/docs/research_raw/paper_revision_2026-11-12/integrated/data/'
eps=json.load(open(D+'liquidation_episodes.json'))
fa={(r['game'],r['decision']):r for r in json.load(open(D+'first_action_checks.json'))['rows']}
def entry(g,i):
    s=dec.get(g,i)['decision_started']; gs=s['prompt_payload']['game_state']; sc=s['prompt_payload']['action_state']['scenario']
    hold=gs['you']['holdings']['owned']; C=gs['you']['cash']
    M0=sum(mval(k) for k in sc['options'].get('mortgageable_space_keys',[]))
    S=0; Sg={}
    for h in hold:
        k=h['space_key']; c=hcost(k)
        v=(5*(c//2)) if h['hotel'] else h['houses']*(c//2)
        S+=v; Sg[SP[k]['group']]=Sg.get(SP[k]['group'],0)+v
    Mstar=sum(mval(h['space_key']) for h in hold if not h['mortgaged'])
    hotgroups={SP[h['space_key']]['group'] for h in hold if h['hotel']}
    S_nohotel=sum(v for gname,v in Sg.items() if gname not in hotgroups)
    return dict(C=C,D=sc['owed_amount'],M0=M0,S=S,Mstar=Mstar,U0=C+S+M0,Ustar=C+S+Mstar,S_nohotel=S_nohotel,hotgroups=sorted(hotgroups),bank=gs['bank']['houses_remaining'])
res=[]
for e in eps:
    g,i=e['game'],e['first_decision']; x=entry(g,i); x.update(game=g,dec=i,model=e['model'],outcome=e['outcome'],cat=fa[(g,i)]['category'],stored_U=e['upper_bound'])
    res.append(x)
json.dump(res,open('partition.json','w'),indent=1)
# checks
bad=[r for r in res if r['Ustar']!=r['stored_U']]
print('Ustar mismatches vs stored upper_bound:',[(r['game'],r['dec'],r['Ustar'],r['stored_U']) for r in bad])
pay=[r for r in res if r['cat']=='payable']
a=[r for r in pay if r['C']+r['M0']>=r['D']]
b=[r for r in pay if r['C']+r['M0']<r['D']<=r['U0']]
c=[r for r in pay if r['U0']<r['D']<=r['Ustar']]
other=[r for r in pay if not (r in a or r in b or r in c)]
print('payable',len(pay),'A',len(a),sum(r['outcome']=='paid' for r in a),'B',len(b),sum(r['outcome']=='paid' for r in b),'C',len(c),sum(r['outcome']=='paid' for r in c),'other',[(r['game'],r['dec']) for r in other])
print('above_bound',sum(r['cat']=='above_bound' for r in res),'Ustar<D among above',sum(r['Ustar']<r['D'] for r in res if r['cat']=='above_bound'))
print('generous bound covers (Ustar>=D):',sum(r['Ustar']>=r['D'] for r in res),'short:',sum(r['Ustar']<r['D'] for r in res))
for (g,i) in [(3,228),(3,356),(3,461),(3,482),(18,428)]:
    r=[x for x in res if x['game']==g and x['dec']==i][0]
    print(g,i,r['model'][:12],r['cat'],'C',r['C'],'D',r['D'],'M0',r['M0'],'S',r['S'],'S_nohotel',r['S_nohotel'],'hot',r['hotgroups'],'bank',r['bank'],'C+M0+S_nohotel>=D?',r['C']+r['M0']+r['S_nohotel']>=r['D'])
