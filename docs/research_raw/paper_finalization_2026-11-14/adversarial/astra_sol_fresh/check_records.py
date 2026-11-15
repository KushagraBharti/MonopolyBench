"""Read-only arithmetic and provenance checks. No engine imports or transitions."""
import ast
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / 'contracts').is_dir())
DRAFT = ROOT / 'docs/research_raw/paper_finalization_2026-11-14/full_drafts/astra'
read = lambda f: json.loads((DRAFT / 'data' / f).read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
data = read('complete_financing_records.json')
episodes = read('liquidation_episodes.json')
board = json.loads((ROOT / 'contracts/data/board.json').read_text())
spaces = {re.sub('[^A-Z0-9]+', '_', s['name'].upper()).strip('_'): s for s in board['spaces']}
groups = defaultdict(set)
for k, s in spaces.items():
    if s['kind'] == 'PROPERTY':
        groups[s['group']].add(k)
cost = dict(BROWN=50, LIGHT_BLUE=50, PINK=100, ORANGE=100, RED=150,
            YELLOW=150, GREEN=200, DARK_BLUE=200)
raw = {}
events = {}
for f, h in data['sources'].items():
    p = ROOT / f
    assert sha(p) == h
    if p.name != 'decisions.jsonl':
        continue
    raw[f] = {int(o['decision_id'].rsplit('-', 1)[1]): o
              for l in p.read_text().splitlines()
              if (o := json.loads(l)).get('phase') == 'decision_resolved'}
    events[f] = [json.loads(l) for l in p.with_name('events.jsonl').read_text().splitlines()]

premises = []
partition = Counter()
for r in data['rows']:
    o = raw[r['source']][r['decision']]
    a = o['attempts'][-1]
    payload = a['prompt_payload']
    if payload is None:
        suffix = '_retry1' if len(o['attempts']) > 1 else ''
        payload = json.loads((ROOT / r['source']).parent.joinpath('prompts',
            f"decision_{o['decision_id']}{suffix}_user.json").read_text())
    state = payload['game_state']
    scenario = payload['action_state']['scenario']
    assert state['you']['cash'] == r['cash']
    assert state['you']['holdings']['owned'] == r['holdings']
    assert state['bank'] == r['bank']
    assert scenario['owed_amount'] == r['debt'] and scenario['options'] == r['options']
    assert o['final_action'] == r['applied_action']
    assert a['raw_response']['choices'][0]['message'].get('reasoning') == r['provider_reasoning']
    assert a.get('assistant_content') == r['assistant_content']
    owned = {h['space_key']: h for h in r['holdings']}
    principal = sum(spaces[k]['price'] // 2 for k, h in owned.items() if not h['mortgaged'])
    initial = sum(spaces[k]['price'] // 2 for k in r['options']['mortgageable_space_keys'])
    salvage = sum((5 if h['hotel'] else h['houses']) * cost.get(spaces[k].get('group'), 0) // 2
                  for k, h in owned.items())
    assert (initial, principal, salvage) == (r['M0'], r['Mstar'], r['S'])
    assert r['U0'] == r['cash'] + initial + salvage
    assert r['Ustar'] == r['cash'] + principal + salvage
    assert r['necessity_inequality'] == (r['U0'] < r['debt'] <= r['Ustar'])
    payable = r['outcome'] == 'paid' or (r['game'], r['decision']) in {(12,190), (12,249), (17,234)}
    if not payable:
        continue
    partition['initial' if r['cash'] + initial >= r['debt'] else
              'sales_no_release' if r['U0'] >= r['debt'] else 'release_needed'] += 1
    developed = {spaces[k]['group'] for k, h in owned.items() if h['hotel'] or h['houses']}
    assert all(groups[g] <= owned.keys() for g in developed)
    assert all(max(5 if owned[k]['hotel'] else owned[k]['houses'] for k in groups[g]) -
               min(5 if owned[k]['hotel'] else owned[k]['houses'] for k in groups[g]) <= 1
               for g in developed)
    hotels = {g: sum(owned[k]['hotel'] for k in groups[g]) for g in developed}
    free = sum(owned[k]['houses'] for g in developed if not hotels[g] for k in groups[g])
    n = sum(hotels.values())
    b = r['bank']['houses_remaining']
    support = ('hotel_free' if n == 0 else 'initial_mortgages_suffice' if r['cash'] + initial >= r['debt']
               else 'all_downgrades_stocked' if b >= 4*n else 'recyclable_single_hotels'
               if max(hotels.values()) <= 1 and b+free >= 4 else 'uncovered')
    assert support != 'uncovered' and r['Ustar'] >= r['debt']
    premises.append(dict(game=r['game'], decision=r['decision'], support=support,
                         bank_houses=b, hotel_free_houses=free, hotels_by_group=hotels))

paid = [e for e in episodes if e['outcome'] == 'paid']
totals = Counter(a for e in paid for a in e['actions'])
no_release = 0
additional_release = []
for e in episodes:
    r = next(r for r in data['rows'] if (r['game'], r['decision']) == (e['game'], e['first_decision']))
    ds = [raw[r['source']][int(d.rsplit('-', 1)[1])] for d in e['decisions']]
    assert [d['final_action']['action'] for d in ds] == e['actions'] == r['recorded_actions']
    ev = [v for v in events[r['source']] if any(d['emitted_event_seq_start'] <= v['seq'] <= d['emitted_event_seq_end'] for d in ds)]
    if e['outcome'] == 'paid':
        payer = ds[0]['player_id']
        assert any(v['type'] == 'CASH_CHANGED' and v['payload'].get('player_id') == payer
                   and v['payload'].get('delta') == -e['debt'] for v in ev)
        released = [d['final_action']['args']['space_key'] for d in ds
                    if d['final_action']['action'] == 'mortgage_property'
                    and d['final_action']['args']['space_key'] not in r['options']['mortgageable_space_keys']]
        if r['cash']+r['M0'] < r['debt'] <= r['U0']:
            if released:
                additional_release.append([r['game'], r['decision']])
            else:
                no_release += 1
    else:
        assert any(v['type'] == 'CASH_CHANGED' and
                   v['payload'].get('reason','').startswith('BANKRUPTCY') for v in ev)

offers = read('offers.json')
styles = {m: dict(Counter(o['response'] for o in offers if o['recipient_model'] == m))
          for m in ['Sol','Gemini','Opus','Grok']}
def form(o):
    a, b = o['offer'], o['request']
    if a['properties'] and b['properties']: return 'swap'
    if a['cash'] and not a['properties'] and b['properties'] and not b['cash']: return 'cash_bid'
    return 'other'
comparison = [o for o in offers if o['accept_available'] and o['exchange_index'] == 0
              and form(o) == 'swap' and not o['recipient_new_groups']]
assert len(comparison) == 188
cells = defaultdict(Counter)
for o in comparison:
    cells[(o['author_model'], 'proposer_only' if o['author_new_groups'] else 'neither')][o['response']] += 1
counts = {m: {s: dict(cells[(m,s)]) for s in ['proposer_only','neither']} for m in ['Sol','Gemini','Opus','Grok']}
stability = read('revision_analysis.json')['stability']
gaps = {}
for label, s in stability.items():
    a,b = s['counts']
    gap = 100*(a[3]/a[0]-b[3]/b[0])
    assert abs(gap-s['gap_pp']) < 1e-10
    draws=[]
    for indexes in itertools.product(range(5), repeat=5):
        sums=[[sum(s['by_block'][i][j][k] for i in indexes) for k in range(4)] for j in range(2)]
        draws.append(100*(sums[0][3]/sums[0][0]-sums[1][3]/sums[1][0]))
    draws.sort()
    def percentile(p):
        x=(len(draws)-1)*p; lo=int(x); hi=min(lo+1,len(draws)-1)
        return draws[lo]+(draws[hi]-draws[lo])*(x-lo)
    interval = [percentile(.025), percentile(.975)]
    assert all(abs(x-y)<1e-8 for x,y in zip(interval,s['resampling_percentiles']))
    gaps[label] = dict(gap_pp=gap, block_percentiles=interval, draws=len(draws))

engine = 'python/packages/engine/src/monopoly_engine/engine.py'
names = {'_resolve_pending_payment','_mortgageable_space_indices','_sellable_building_space_indices',
         '_validate_sell_plan','_apply_mortgage','_apply_sell_plan'}
def methods(s):
    ls=s.splitlines()
    return {n.name:'\n'.join(ls[n.lineno-1:n.end_lineno]) for n in ast.walk(ast.parse(s))
            if isinstance(n,ast.FunctionDef) and n.name in names}
current = methods((ROOT/engine).read_text())
source_matches={}
for commit in ['42f85183fa772b2ab3759cc49987e5ed6cc9efcc','d6808534a831862682a6940f394c6c87bb2691cb']:
    source_matches[commit] = methods(subprocess.check_output(['git','show',f'{commit}:{engine}'],cwd=ROOT,text=True)) == current
    assert source_matches[commit]

result = dict(method='Saved-record arithmetic, field checks, and source text comparison only; no evaluation.',
              raw_sources_verified=len(raw), first_responses_verified=len(data['rows']),
              episode_outcomes=dict(Counter(e['outcome'] for e in episodes)),
              paid_debt=sum(e['debt'] for e in paid), paid_action_counts=dict(totals),
              paid_action_lengths=dict(Counter(len(e['actions']) for e in paid)),
              payable_partition=dict(partition), proof_coverage=dict(Counter(p['support'] for p in premises)),
              proof_premises=premises, middle_observed_no_release=no_release,
              middle_with_release=additional_release, offer_responses=dict(Counter(o['response'] for o in offers)),
              offer_accept_legal=sum(o['accept_available'] for o in offers), response_styles=styles,
              opening_swap_comparison=counts, grok_comparison_authored=sum(o['author_model']=='Grok' for o in comparison),
              rejection_gaps=gaps, collection_source_method_matches=source_matches)
(OUT/'record_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['proof_premises']},indent=2))
