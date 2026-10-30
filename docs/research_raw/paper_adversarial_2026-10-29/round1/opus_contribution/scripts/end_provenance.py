"""Read-only full-denominator check of the label 'END on a buildable menu = chose not to build'.
For every decision whose delivered menu includes build_houses_or_hotel and whose applied action is end_turn,
classify provenance: engine fallback/default; received content/tool name conflict (content parses as a JSON
pseudo-call whose name/action differs from the applied tool); or consistent/other.
Also records the response condition of the applied attempt (standard vs action-only recovery).
Usage: python3 -I end_provenance.py saved_games/railway-research-*/game-*"""
import json, sys, os, collections
NAME = {'openai': 'Sol', 'google': 'Gemini', 'anthropic': 'Opus', 'x-ai': 'Grok'}
tot = collections.Counter()
for g in sys.argv[1:]:
    p = os.path.join(g, 'run', 'decisions.jsonl')
    if not os.path.exists(p):
        continue
    menus = {}
    for line in open(p):
        r = json.loads(line)
        if r['phase'] == 'decision_started':
            menus[r['decision_id']] = r['prompt_payload']['action_state'].get('available_actions', [])
            continue
        if 'build_houses_or_hotel' not in menus.get(r['decision_id'], []):
            continue
        m = NAME[r['openrouter_model_id'].split('/')[0]]
        act = r['final_action']['action']
        tot[(m, 'build_menu')] += 1
        if act != 'end_turn':
            tot[(m, 'nonEND_' + ('build' if act == 'build_houses_or_hotel' else 'other'))] += 1
            continue
        tot[(m, 'END')] += 1
        if r.get('fallback_used'):
            tot[(m, 'END_default')] += 1
            continue
        valid = [a for a in r['attempts'] if a.get('outcome') == 'valid']
        a = valid[-1] if valid else r['attempts'][-1]
        cond = a.get('response_condition')
        c = a.get('assistant_content') or ''
        cname = None
        try:
            cj = json.loads(c)
            if isinstance(cj, dict):
                cname = cj.get('name') or cj.get('action')
        except Exception:
            pass
        if cname and cname != 'end_turn':
            tot[(m, 'END_content_conflict')] += 1
        else:
            tot[(m, 'END_consistent_or_unparsed')] += 1
            tot[(m, 'END_consistent_cond_' + str(cond))] += 1
for m in ['Sol', 'Gemini', 'Opus', 'Grok']:
    print(m, {k[1]: v for k, v in sorted(tot.items()) if k[0] == m})
