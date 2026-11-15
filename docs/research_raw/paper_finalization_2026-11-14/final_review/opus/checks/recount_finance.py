#!/usr/bin/env python3
"""Independent read-only recount of finance claims in the integrated candidate.

Reads only: saved decisions.jsonl files (mapped by the integrated data/game_map.json),
contracts/data/board.json, and the retained episode boundaries in
integrated/data/liquidation_episodes.json. Recomputes entry sums from the first
liquidation prompt rather than reusing the packaged episodes_188.json, then compares.
No engine import, replay, policy, search or model call. Writes only into this folder.
"""
import json, re, hashlib, collections, pathlib

REPO = pathlib.Path('/Users/kushagra/CS-Projects/MonopolyBench')
INT = REPO / 'docs/research_raw/paper_finalization_2026-11-14/integrated'
OUT = pathlib.Path(__file__).resolve().parent

board = json.loads((REPO / 'contracts/data/board.json').read_text())
hc = {k: int(v) for k, v in board['house_cost_by_group'].items()}
def norm(name):
    return re.sub(r'_+', '_', re.sub(r'[^A-Z0-9]', '_', name.upper())).strip('_')
SP = {norm(s['name']): s for s in board['spaces'] if s.get('price')}
GROUP = collections.defaultdict(list)
for k, s in SP.items():
    GROUP[s['group']].append(k)

gmap = json.loads((INT / 'data/game_map.json').read_text())
eps = json.loads((INT / 'data/liquidation_episodes.json').read_text())
packaged = {(e['game'], e['decision']): e for e in json.loads((INT / 'data/episodes_188.json').read_text())}

cache = {}
def records(game):
    if game not in cache:
        p = REPO / gmap[str(game)] / 'decisions.jsonl'
        started, resolved = {}, {}
        for line in p.read_text().splitlines():
            r = json.loads(line)
            (started if r['phase'] == 'decision_started' else resolved if r['phase'] == 'decision_resolved' else {})[r['decision_id']] = r
        cache[game] = (started, resolved)
    return cache[game]

WITNESS = {(12, 190), (17, 234), (12, 249)}
rows = []
mismatch = []
for e in eps:
    g = int(e['game']); d0 = int(e['first_decision'])
    decs = eval(e['decisions']) if isinstance(e['decisions'], str) else e['decisions']
    started, resolved = records(g)
    s0 = started[decs[0]]
    gs = s0['prompt_payload']['game_state']; ac = s0['prompt_payload']['action_state']
    sc = ac['scenario']; opts = sc['options']
    you = gs['you']; owned = you['holdings']['owned']
    C = you['cash']; D = sc['owed_amount']
    S = 0; Mstar = 0; hotels = collections.Counter(); houses_by_group = collections.Counter()
    for h in owned:
        sp = SP[h['space_key']]
        if not h['mortgaged']:
            Mstar += sp['price'] // 2
        if sp['kind'] == 'PROPERTY':
            c = hc.get(sp['group'], 0)
            if h['hotel']:
                S += 5 * (c // 2); hotels[sp['group']] += 1
            else:
                S += h['houses'] * (c // 2); houses_by_group[sp['group']] += h['houses']
    M0 = sum(SP[k]['price'] // 2 for k in opts.get('mortgageable_space_keys', []))
    U0, Us = C + S + M0, C + S + Mstar
    actions = [resolved[x]['final_action']['action'] for x in decs]
    first = actions[0]
    outcome = e['outcome']
    sold_units = 0
    for x in decs:
        fa = resolved[x]['final_action']
        if fa['action'] == 'sell_houses_or_hotel':
            for it in fa['args'].get('sell_plan', []):
                sold_units += it.get('count', 1)
    pk = packaged[(g, d0)]
    for k, v in (('cash', C), ('debt', D), ('S', S), ('M0', M0), ('Mstar', Mstar)):
        if pk[k] != v:
            mismatch.append((g, d0, k, pk[k], v))
    rows.append(dict(game=g, decision=d0, model=e['model'], C=C, D=D, S=S, M0=M0, Mstar=Mstar,
                     U0=U0, Ustar=Us, outcome=outcome, first=first, actions=actions,
                     sold_units=sold_units, hotels=sum(hotels.values()),
                     forced=not (opts.get('mortgageable_space_keys') or opts.get('sellable_building_space_keys'))))

out = {}
out['episodes'] = len(rows)
out['packaged_field_mismatches'] = mismatch
paid = [r for r in rows if r['outcome'] == 'paid']
out['paid'] = len(paid)
payable = [r for r in rows if r['outcome'] == 'paid' or (r['game'], r['decision']) in WITNESS]
out['payable'] = len(payable)
cat = collections.Counter()
for r in payable:
    if r['C'] + r['M0'] >= r['D']: c = 'initial'
    elif r['U0'] >= r['D']: c = 'sale_no_release'
    else: c = 'release_required'
    r['cat'] = c; cat[c] += 1
out['partition'] = dict(cat)
out['partition_paid'] = dict(collections.Counter(r['cat'] for r in payable if r['outcome'] == 'paid'))
# development preservation
dev = [r for r in rows if r['C'] + r['M0'] >= r['D'] and r['S'] > 0]
out['dev_population'] = len(dev)
out['dev_all_paid'] = all(r['outcome'] == 'paid' for r in dev)
out['dev_no_sale'] = sum('sell_houses_or_hotel' not in r['actions'] for r in dev)
out['dev_sellers'] = [(r['game'], r['decision'], r['model'], r['actions'], r['sold_units'], r['C'], r['D'], r['M0'], r['S']) for r in dev if 'sell_houses_or_hotel' in r['actions']]
out['dev_by_model'] = dict(collections.Counter(r['model'].split()[0] for r in dev))
out['dev_cash_only_impossible'] = all(r['C'] < r['D'] for r in dev)
# Does any no-sale member own buildings it could not have sold (sanity: all had sale options?)
# first-action table
fa = collections.Counter()
for r in rows:
    region = 'covers' if r['Ustar'] >= r['D'] else 'short'
    fa[(region, 'declare' if r['first'] == 'declare_bankruptcy' else 'finance')] += 1
out['first_action'] = {f'{a}/{b}': v for (a, b), v in sorted(fa.items())}
out['short_forced'] = sum(1 for r in rows if r['Ustar'] < r['D'] and r['forced'])
out['short_starts'] = [(r['game'], r['decision'], r['model'].split()[0], r['first']) for r in rows if r['Ustar'] < r['D'] and r['first'] != 'declare_bankruptcy']
out['covers_declares'] = [(r['game'], r['decision'], r['model'].split()[0]) for r in rows if r['Ustar'] >= r['D'] and r['first'] == 'declare_bankruptcy']
# sixteen
six = [r for r in payable if r['cat'] == 'release_required']
out['sixteen'] = [(r['game'], r['decision'], r['model'].split()[0], r['D'], r['U0'], r['Ustar'], r['outcome']) for r in six]
# unlisted collateral population (Mstar > M0) — relevant to Fable's 5/37 denominator
out['unlisted_collateral_entries'] = sum(1 for r in rows if r['Mstar'] > r['M0'])
out['unlisted_collateral_by_region'] = dict(collections.Counter(
    ('payable:' + r.get('cat', '?')) if r in payable else ('short' if r['Ustar'] < r['D'] else 'other')
    for r in rows if r['Mstar'] > r['M0']))
(OUT / 'recount_finance.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps(out, indent=1))
