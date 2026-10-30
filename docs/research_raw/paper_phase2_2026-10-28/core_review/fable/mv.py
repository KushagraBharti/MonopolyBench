#!/usr/bin/env python3
"""Fable's compact multi-decision viewer: mv.py GAME DEC [DEC...] [--n N] (truncation per field)."""
import json, sys
sys.path.insert(0, '/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/fable')
from bundle_view import load
N=700
argv=sys.argv[1:]
if '--n' in argv:
    i=argv.index('--n'); N=int(argv[i+1]); argv=argv[:i]+argv[i+2:]
args=[a for a in argv if not a.startswith('--')]
g=int(args[0])
def T(x,n=N):
    s=x if isinstance(x,str) else json.dumps(x)
    return s if len(s)<=n else s[:n]+'…'
for d in args[1:]:
    d=int(d); rec,led=load(g,d)
    ip=rec.get('initial_prompt',{}).get('payload',{}); gs=ip.get('game_state',{}); ast=ip.get('action_state',{}); you=gs.get('you',{})
    menu=[a.get('name') if isinstance(a,dict) else a for a in (ast.get('legal_actions') or ast.get('actions') or [])]
    print('='*90); print(f"G{g} d{d} (#{d+1}) {rec.get('player_id')} {rec.get('model')} t{rec.get('turn_index')} {rec.get('decision_type')} cash={you.get('cash')} pos={you.get('position')}")
    print('  MENU:', menu if menu else T(ast,300))
    for a in rec.get('attempts',[]):
        rr=a.get('raw_response') or {}
        reasoning=None
        if isinstance(rr,dict):
            try: msg=rr['choices'][0]['message']; reasoning=msg.get('reasoning') or (msg.get('reasoning_details') or [{}])[0].get('summary') or (msg.get('reasoning_details') or [{}])[0].get('text')
            except Exception: reasoning=rr.get('reasoning')
        print(f"  -- attempt {a.get('attempt_index_zero_based')} {a.get('response_condition')} outcome={a.get('outcome')} verr={T(a.get('validation_errors'),200)}")
        if a.get('assistant_content'): print('     CONTENT:', T(a['assistant_content']))
        if a.get('parsed_tool_calls'): print('     TOOLS:', T(a['parsed_tool_calls']))
        if reasoning: print('     REASONING:', T(reasoning))
        if isinstance(rr,dict) and rr.get('refusal'): print('     REFUSAL:', T(rr['refusal'],120))
    print('  APPLIED:', T(rec.get('applied_action_record'),N))
    res=rec.get('resolution'); 
    if res: print('  RESOLUTION:', T(res,300))
