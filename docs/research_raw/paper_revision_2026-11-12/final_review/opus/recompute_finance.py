"""Opus final review: independent recomputation of the debt-requirement partition.

Reads the frozen liquidation episode ledger for episode boundaries and outcomes,
then recomputes C, S, M0, M* from the first decision's stored prompt payload and
contracts/data/board.json. Reads saved files only; no engine or model execution.
Mortgage value = price/2; building salvage = house_cost/2 per house, hotel counted
as five buildings (hotel + four houses returned through downgrades).
"""
import json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[5]
INT = ROOT / 'docs/research_raw/paper_revision_2026-11-12/integrated'
board = json.load(open(ROOT / 'contracts/data/board.json'))
gm = json.load(open(INT / 'data/game_map.json'))
eps = json.load(open(INT / 'data/liquidation_episodes.json'))

def key(name):
    return re.sub(r'[^A-Z0-9]+', '_', name.upper().replace('&', '')).strip('_')
price, group = {}, {}
for s in board['spaces']:
    if s.get('price'):
        k = key(s['name']); price[k] = s['price']; group[k] = s['group']
house_cost = board['house_cost_by_group']

starts = {}
def load(g):
    if g not in starts:
        d = {}
        for l in open(ROOT / gm[str(g)] / 'decisions.jsonl'):
            x = json.loads(l)
            if x['phase'] == 'decision_started':
                d[int(x['decision_id'].rsplit('-', 1)[1])] = x
        starts[g] = d
    return starts[g]

rows = []
missing = Counter()
for e in eps:
    st = load(e['game'])[e['first_decision']]
    p = st['prompt_payload']
    you = p['game_state']['you']; sc = p['action_state']['scenario']
    C = you['cash']; D = sc['owed_amount']
    S = 0; Mstar = 0
    for h in you['holdings']['owned']:
        k = h['space_key']
        if k not in price: missing[k] += 1; continue
        if group[k] in house_cost:
            S += (h['houses'] + 5 * bool(h['hotel'])) * house_cost[group[k]] // 2
        if not h['mortgaged']:
            Mstar += price[k] // 2
    M0 = sum(price[k] // 2 for k in sc['options'].get('mortgageable_space_keys', []))
    U0, Us = C + S + M0, C + S + Mstar
    rows.append(dict(game=e['game'], d=e['first_decision'], model=e['model'].split()[0], outcome=e['outcome'],
                     C=C, S=S, M0=M0, Ms=Mstar, D=D, U0=U0, Us=Us, cash_ok=(C == e['cash'] and D == e['debt'])))

out = {'n': len(rows), 'outcomes': dict(Counter(r['outcome'] for r in rows)),
       'prompt_matches_ledger_cash_debt': sum(r['cash_ok'] for r in rows), 'unpriced_keys': dict(missing)}
def cat(r):
    if r['C'] + r['M0'] >= r['D']: return 'cash+initial mortgages'
    if r['U0'] >= r['D']: return 'sales needed, released not necessary'
    if r['Us'] >= r['D']: return 'released necessary'
    return 'above generous bound'
tab = defaultdict(Counter)
for r in rows:
    tab[cat(r)][r['outcome']] += 1
out['partition'] = {k: dict(v) for k, v in tab.items()}
out['necessary_rows'] = [f"G{r['game']} d{r['d']} {r['model']} D={r['D']} U0={r['U0']} U*={r['Us']} {r['outcome']}"
                         for r in rows if cat(r) == 'released necessary']
json.dump(out, sys.stdout, indent=1)
print()
