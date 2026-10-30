#!/usr/bin/env python3
"""Per-attempt check of every build plan tried in each fallback decision (not just the last). Same rules as fallback_scan.py."""
import json, os, importlib.util
H=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('bv',os.path.join(H,'bundle_view.py')); bv=importlib.util.module_from_spec(spec); spec.loader.exec_module(bv)
board=json.load(open('/Users/kushagra/CS-Projects/MonopolyBench/contracts/data/board.json')); hc=board['house_cost_by_group']; grp={}
for s in board['spaces']:
    if 'group' in s: grp[s['name'].upper().replace('.','').replace(' ','_').replace('&','_').replace('B__O','B_O')]=s['group']
inv=json.load(open(os.path.join(H,'fallback_inventory.json')))
rows=[]
for o in inv:
    if o['model']=='claude-opus-5.5': continue
    rec,_=bv.load(o['game'],o['dec']); you=rec['initial_prompt']['payload']['game_state']['you']; bank=rec['initial_prompt']['payload']['game_state']['bank']
    holdings={h['space_key']:h for h in you['holdings']['owned']}
    for a in rec['attempts']:
        for tc in a.get('parsed_tool_calls') or []:
            if tc.get('name')!='build_houses_or_hotel': continue
            try: plan=json.loads(tc.get('arguments') or '{}').get('build_plan')
            except Exception: plan=None
            if not plan: rows.append((o['game'],o['dec'],a['attempt_index_zero_based'],'unparseable')); continue
            cost=0; final={}; ok=True; n=0
            for it in plan:
                k=it.get('space_key'); c=int(it.get('count',1) or 1)
                if not k or k not in grp: ok=False; break
                final[k]=final.get(k,holdings.get(k,{}).get('houses',0))+c; cost+=c*hc.get(grp[k],0); n+=c
            if not ok: rows.append((o['game'],o['dec'],a['attempt_index_zero_based'],'malformed')); continue
            groups={grp[k] for k in final}; even=True
            for g in groups:
                counts=[final.get(m,holdings.get(m,{}).get('houses',0)) for m,gg in grp.items() if gg==g and m in holdings]
                if max(counts)-min(counts)>1: even=False
            rows.append((o['game'],o['dec'],a['attempt_index_zero_based'],f"cost={cost} cash={you['cash']} {'affordable' if cost<=you['cash'] else 'UNAFFORDABLE'} {'even-reachable' if even else 'uneven'} bank={bank.get('houses_remaining')} n={n} {a['outcome']}: {(a.get('validation_errors') or [''])[0][:50]}"))
for r in rows: print(r)
