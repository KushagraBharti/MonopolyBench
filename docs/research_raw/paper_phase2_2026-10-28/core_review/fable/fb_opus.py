#!/usr/bin/env python3
"""Fable: shape of the plan in the last (illogical) attempt of every Opus fallback.
For each Opus fallback decision: validation error text, action name, build_plan entries, max count per entry,
final-state evenness (given current houses per space), total cost vs cash."""
import json, sys
sys.path.insert(0,'/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/fable')
from bundle_view import load
BOARD=json.load(open('/Users/kushagra/CS-Projects/MonopolyBench/contracts/data/board.json'))
import re
def K(n): return re.sub(r'[^A-Z0-9]+','_',n.upper()).strip('_')
spaces={K(s['name']):s for s in BOARD['spaces'] if s.get('kind')=='PROPERTY'}
def house_cost(key):
    s=spaces.get(key,{})
    return BOARD.get('house_cost_by_group',{}).get(s.get('group'))
inv=json.load(open('fallback_inventory.json'))
rows=[]
for o in inv:
    if 'claude' not in o['model']: continue
    g,d=o['game'],o['dec']; rec,_=load(g,d)
    att=rec['attempts']; last=att[-1]
    you=rec['initial_prompt']['payload']['game_state']['you']; cash=you.get('cash')
    houses={p.get('space_key') or p.get('key'):(p.get('houses') or 0)+(5 if p.get('hotel') else 0) for p in you.get('properties',[]) if isinstance(p,dict)}
    tc=(last.get('parsed_tool_calls') or [{}])[0]; name=tc.get('name'); 
    try: args=json.loads(tc.get('arguments') or '{}') if isinstance(tc.get('arguments'),str) else (tc.get('arguments') or {})
    except Exception: args={}
    plan=args.get('build_plan') or []
    maxc=max([e.get('count',1) for e in plan],default=0)
    cost=0; final=dict(houses)
    for e in plan:
        k=e.get('space_key'); c=e.get('count',1); hc=house_cost(k) or 0
        cost+=hc*c; final[k]=final.get(k,0)+(c if e.get('kind')=='HOUSE' else c)
    groups={}
    for e in plan:
        grp=spaces.get(e.get('space_key'),{}).get('group'); groups.setdefault(grp,set()).add(e.get('space_key'))
    even=True
    for grp in groups:
        members=[k for k,s in spaces.items() if s.get('group')==grp]
        vals=[final.get(k,0) for k in members]
        if max(vals)-min(vals)>1: even=False
    rows.append(dict(game=g,dec=d,n_attempts=len(att),last_cond=last.get('response_condition'),outcome=last.get('outcome'),verr=(last.get('validation_errors') or [''])[0][:90],action=name,entries=len(plan),max_count=maxc,cost=cost,cash=cash,affordable=(cost<=cash) if plan else None,final_even=even if plan else None))
json.dump(rows,open('fallback_opus_plans.json','w'),indent=1)
import collections
print('n Opus fallbacks',len(rows))
print('by validation error:',collections.Counter(r['verr'] for r in rows).most_common())
print('by action:',collections.Counter(r['action'] for r in rows).most_common())
pl=[r for r in rows if r['action']=='build_houses_or_hotel']
print('build plans:',len(pl),'max_count>=2:',sum(r['max_count']>=2 for r in pl),'affordable:',sum(bool(r['affordable']) for r in pl),'final_even:',sum(bool(r['final_even']) for r in pl),'affordable&even&maxc>=2:',sum(r['max_count']>=2 and r['affordable'] and r['final_even'] for r in pl))
print('per game:',sorted(collections.Counter(r['game'] for r in rows).items()))
for r in rows:
    if r['action']!='build_houses_or_hotel' or r['max_count']<2 or not r['affordable'] or not r['final_even']:
        print(' odd:',r)
