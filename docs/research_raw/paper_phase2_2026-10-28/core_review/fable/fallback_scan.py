#!/usr/bin/env python3
"""Fable's inventory of every decision with resolution.fallback_used, with my own legality/affordability check of the last requested build plan.
Legal-interleaving check: a final allocation is reachable one house at a time iff, within each colour group, the final house counts differ by at most 1
AND the player owns the whole group AND no mortgaged deed in the group (engine disallows building on groups with mortgages, per observed menus).
Affordability: sum(count*house_cost) <= cash. Bank supply: houses_remaining >= total requested houses. This is my check, not the engine's."""
import json, os, glob, sys
ROOT='/Users/kushagra/CS-Projects/MonopolyBench'
board=json.load(open(os.path.join(ROOT,'contracts/data/board.json')))
hc=board['house_cost_by_group']; grp={}
for s in board['spaces']:
    if 'group' in s:
        k=s['name'].upper().replace('.','').replace(' ','_').replace('&','_').replace('B__O','B_O'); grp[k]=s['group']
pk=sorted(glob.glob(os.path.join(ROOT,'docs/research_raw/paper_phase1_2026-10-28/astra/review_packets/game-*-part-*.jsonl')))
out=[]
for p in pk:
    with open(p) as f:
        for line in f:
            if '"fallback_used": true' not in line: continue
            rec=json.loads(line)
            res=rec.get('resolution',{})
            if not res.get('fallback_used'): continue
            you=rec['initial_prompt']['payload']['game_state']['you']; bank=rec['initial_prompt']['payload']['game_state']['bank']
            holdings={h['space_key']:h for h in you['holdings']['owned']}
            chain=[(a.get('response_condition'),a.get('outcome'),(a.get('validation_errors') or [''])[0][:70]) for a in rec.get('attempts',[])]
            # last build plan requested
            plan=None; planname=None
            for a in rec.get('attempts',[]):
                for tc in a.get('parsed_tool_calls') or []:
                    try: args=json.loads(tc.get('arguments') or '{}')
                    except Exception: args=None
                    if tc.get('name')=='build_houses_or_hotel' and args and 'build_plan' in args: plan=args['build_plan']; planname=tc.get('name')
                    elif tc.get('name') and tc.get('name')!='build_houses_or_hotel': planname=planname or tc.get('name')
            verdict='no_build_plan'; cost=None; final=None
            if plan:
                final={}; cost=0; hotels=0
                for it in plan:
                    k=it.get('space_key'); c=int(it.get('count',1) or 1); kind=it.get('kind','HOUSE')
                    if k is None: verdict='malformed_plan'; break
                    g=grp.get(k); 
                    if kind=='HOTEL': hotels+=c; final[k]=final.get(k,holdings.get(k,{}).get('houses',0))+5*c; cost+=c*hc.get(g,0)
                    else: final[k]=final.get(k,holdings.get(k,{}).get('houses',0))+c; cost+=c*hc.get(g,0)
                if verdict!='malformed_plan':
                    groups={grp.get(k) for k in final}
                    even=True; owns=True; mort=False
                    for g in groups:
                        members=[k for k,gg in grp.items() if gg==g]
                        counts=[]
                        for m in members:
                            if m not in holdings: owns=False; continue
                            if holdings[m].get('mortgaged'): mort=True
                            counts.append(final.get(m,holdings[m].get('houses',0)+(5 if holdings[m].get('hotel') else 0)))
                        if counts and max(counts)-min(counts)>1: even=False
                    nh=sum(int(it.get('count',1) or 1) for it in plan if it.get('kind','HOUSE')!='HOTEL')
                    afford=cost<=you['cash']; supply=nh<=bank.get('houses_remaining',99)
                    verdict=('LEGAL_INTERLEAVED' if (even and owns and not mort) else 'not_evenly_reachable') + ('/affordable' if afford else '/UNAFFORDABLE') + ('' if supply else '/NO_BANK_HOUSES')
            out.append({'game':rec['game'],'dec':int(rec['decision_id'].rsplit('-',1)[1]),'player':rec['player_id'],'model':rec['model'].split('/')[-1],'turn':rec['turn_index'],'cash':you['cash'],'bank_houses':bank.get('houses_remaining'),'chain':chain,'applied':rec['applied_action_record']['action']['action'],'plan':plan,'plan_cost':cost,'my_check':verdict,'fallback_reason':res.get('fallback_reason')})
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fallback_inventory.json'),'w'),indent=1)
import collections
print('total fallbacks',len(out)); print(collections.Counter(o['model'] for o in out)); print(collections.Counter(o['my_check'] for o in out)); print(collections.Counter((o['model'],o['my_check']) for o in out))
for o in out:
    if 'UNAFFORDABLE' in o['my_check'] or 'not_evenly' in o['my_check'] or 'malformed' in o['my_check'] or 'no_build' in o['my_check'] or 'NO_BANK' in o['my_check']:
        print(o['game'],o['dec'],o['model'],o['cash'],o['bank_houses'],o['my_check'],o['plan_cost'],o['chain'])
