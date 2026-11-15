#!/usr/bin/env python3
"""Read-only rechecks run inline during the review, consolidated for reproduction.

- 61/74 population, cells and concentration (packaged offers.json + reason_comparison.json)
- opening-swap proposer cells
- G7 d139-d152 trace from the raw decision log
- liquidation assistant-content observability by system (raw logs)
- per-game run commit (cloud/execution_manifest.json) and engine/board hashes at both commits (git blobs)
No engine import, replay, policy, search or model call. Writes only recount_other.json here.
"""
import json, collections, hashlib, subprocess, pathlib, ast

REPO = pathlib.Path('/Users/kushagra/CS-Projects/MonopolyBench')
INT = REPO / 'docs/research_raw/paper_finalization_2026-11-14/integrated'
OUT = pathlib.Path(__file__).resolve().parent
gm = json.loads((INT / 'data/game_map.json').read_text())
res = {}

offers = json.loads((INT / 'data/offers.json').read_text())
legal = [r for r in offers if str(r['accept_available']) == 'True']
res['responses'] = dict(collections.Counter(r['response'] for r in offers))
res['legal'] = len(legal)
rec = [r for r in legal if r['completion_cell'] in ('recipient_only', 'both') and r['response'] == 'reject_trade']
res['recipient_completing_legal_rejections'] = dict(collections.Counter(r['completion_cell'] for r in rec))
cmp = json.loads((INT / 'data/reason_comparison.json').read_text())
D = cmp['categories']['D']
cell = {'G%02dd%d' % (int(r['game']), int(r['decision'])): r['completion_cell'] for r in rec}
res['common_positive_by_cell'] = dict(collections.Counter(cell[k] for k in D['common_positive_keys']))
res['disagreement_keys'] = D['reviewer_only_keys'] + D['first_pass_only_keys']
res['comparison_scope'] = cmp['scope']
res['by_game_top'] = collections.Counter(int(r['game']) for r in rec).most_common(3)
res['by_recipient'] = dict(collections.Counter(r['recipient_model'] for r in rec))

def lit(x):
    return ast.literal_eval(x) if isinstance(x, str) else x
op = [r for r in legal if str(r['exchange_index']) == '0' and lit(r['offer'])['properties'] and lit(r['request'])['properties']]
cells = collections.defaultdict(lambda: [0, 0])
for r in op:
    if r['completion_cell'] in ('author_only', 'neither'):
        c = cells[(r['author_model'], r['completion_cell'])]
        c[0] += r['response'] == 'reject_trade'; c[1] += 1
res['proposer_cells'] = {f'{m}:{k}': f'{v[0]}/{v[1]}' for (m, k), v in sorted(cells.items())}

def resolved(game, lo, hi):
    out = {}
    for line in open(REPO / gm[str(game)] / 'decisions.jsonl'):
        r = json.loads(line)
        if r['phase'] == 'decision_resolved':
            n = int(r['decision_id'][-6:])
            if lo <= n <= hi:
                fa = r['final_action']
                out[n] = dict(player=r['player_name'], action=fa['action'], args=fa.get('args'),
                              public=fa.get('public_message'), note=fa.get('private_thought'))
    return out
res['g7_trace'] = resolved(7, 139, 152)

names = ('declare_bankruptcy', 'mortgage_property', 'sell_houses_or_hotel')
obs = collections.defaultdict(lambda: [0, 0, 0])
for g in range(1, 21):
    for line in open(REPO / gm[str(g)] / 'decisions.jsonl'):
        r = json.loads(line)
        if r['phase'] != 'decision_resolved' or r['decision_type'] != 'LIQUIDATION_DECISION':
            continue
        content = r['attempts'][-1].get('assistant_content')
        o = obs[r['player_name'].split()[0]]
        o[0] += 1; o[1] += bool(content and str(content).strip()); o[2] += bool(content and any(n in str(content) for n in names))
res['liquidation_content_decisions_withcontent_namesaction'] = dict(obs)

res['run_commits'] = {}
for g in range(1, 21):
    m = json.loads((REPO / gm[str(g)].rsplit('/run', 1)[0] / 'cloud/execution_manifest.json').read_text())
    res['run_commits'][g] = m['git_sha']
res['rules_hashes'] = {}
for c in sorted(set(res['run_commits'].values())):
    res['rules_hashes'][c] = {f: hashlib.sha256(subprocess.run(['git', '-C', str(REPO), 'show', f'{c}:{f}'], capture_output=True, check=True).stdout).hexdigest()
                              for f in ('python/packages/engine/src/monopoly_engine/engine.py', 'contracts/data/board.json')}
(OUT / 'recount_other.json').write_text(json.dumps(res, indent=1) + '\n')
print(json.dumps({k: v for k, v in res.items() if k != 'g7_trace'}, indent=1))
