"""Opus final review helper: print applied decisions in a range from saved records.

Usage: python3 -I dump_decisions.py GAME FIRST LAST [--full]
Reads decisions.jsonl only. Prints decision type, actor, cash, applied action,
args, public message, private note and (with --full) provider reasoning text.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
gm = json.load(open(ROOT / 'docs/research_raw/paper_revision_2026-11-12/integrated/data/game_map.json'))
g, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
full = '--full' in sys.argv
st, rs = {}, {}
for l in open(ROOT / gm[str(g)] / 'decisions.jsonl'):
    x = json.loads(l)
    n = int(x['decision_id'].rsplit('-', 1)[1])
    if a <= n <= b:
        (st if x['phase'] == 'decision_started' else rs)[n] = x
for n in sorted(rs):
    x = rs[n]; s = st.get(n, {})
    p = s.get('prompt_payload') or {}
    you = (p.get('game_state') or {}).get('you', {})
    fa = x['final_action']
    print(f"== d{n} t{x['turn_index']} {x['decision_type']} {x['player_id']} {x['player_name']} cash={you.get('cash')} cond={[t.get('response_condition') for t in x['attempts']]} fb={x['fallback_used']}")
    print('   ACTION', fa['action'], json.dumps(fa.get('args'))[:400])
    if fa.get('public_message'): print('   PUBLIC', fa['public_message'])
    if fa.get('private_thought'): print('   NOTE  ', fa['private_thought'])
    if full:
        m = (((x['attempts'][-1].get('raw_response') or {}).get('choices') or [{}])[0]).get('message', {})
        if m.get('reasoning'): print('   REASON', m['reasoning'].strip().replace('\n', ' ')[:1500])
        if x['attempts'][-1].get('assistant_content'): print('   CONTENT', str(x['attempts'][-1]['assistant_content'])[:400])
    if x['decision_type'] in ('TRADE_RESPONSE_DECISION',):
        ast = p.get('action_state', {})
        print('   OFFER', json.dumps(ast.get('scenario', ast))[:500])
