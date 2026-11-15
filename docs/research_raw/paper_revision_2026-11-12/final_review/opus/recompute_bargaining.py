"""Opus final review: independent recomputation of printed bargaining numbers.

Reads integrated/data/offers.json (the frozen 920-response ledger) only.
No engine, replay, model query or new game. Written independently of
integrated/tools/analyze.py; form definitions follow the paper's prose.
"""
import json, itertools, sys
from collections import Counter
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
LEDGER = HERE.parents[1] / 'integrated' / 'data' / 'offers.json'
offers = json.load(open(LEDGER))
out = {}

def form(r):
    a, b = r['offer'], r['request']  # offer: author gives; request: author asks
    jail = a['get_out_of_jail_cards'] or b['get_out_of_jail_cards']
    if a['properties'] and b['properties']:
        return 'swap'
    if b['properties'] and not a['properties'] and a['cash'] > 0 and b['cash'] == 0 and not jail:
        return 'cash_bid'
    if a['properties'] and not b['properties'] and b['cash'] > 0 and a['cash'] == 0 and not jail:
        return 'cash_ask'
    return 'other'

legal = [r for r in offers if r['accept_available']]
out['n_responses'] = len(offers)
out['n_legal'] = len(legal)
out['responses_all'] = dict(Counter(r['response'] for r in offers))
out['threads'] = len({r['thread_id'] for r in offers})
cells = ['author_only', 'recipient_only', 'both', 'neither']
forms = ['swap', 'cash_bid', 'cash_ask', 'other']

def tally(rs):
    c = Counter(r['response'] for r in rs)
    return [len(rs), c.get('accept_trade', 0), c.get('counter_trade', 0), c.get('reject_trade', 0)]

for stage, pred in [('opening', lambda r: r['exchange_index'] == 0), ('later', lambda r: r['exchange_index'] > 0)]:
    out[stage] = {f: {c: tally([r for r in legal if pred(r) and form(r) == f and r['completion_cell'] == c]) for c in cells} for f in forms}

opening = [r for r in legal if r['exchange_index'] == 0]

def rate(rs):
    return sum(r['response'] == 'reject_trade' for r in rs) / len(rs) if rs else float('nan')

def gap(rs, f):
    a = [r for r in rs if form(r) == f and r['completion_cell'] == 'author_only']
    n = [r for r in rs if form(r) == f and r['completion_cell'] == 'neither']
    if not a or not n:
        return float('nan')
    return 100 * (rate(a) - rate(n))

def cnt(rs, f, c):
    s = [r for r in rs if form(r) == f and r['completion_cell'] == c]
    return f"{sum(r['response']=='reject_trade' for r in s)}/{len(s)}"

out['by_proposer'] = {m: (cnt([r for r in opening if r['author_model'] == m], 'swap', 'author_only'),
                          cnt([r for r in opening if r['author_model'] == m], 'swap', 'neither'),
                          round(gap([r for r in opening if r['author_model'] == m], 'swap'), 1))
                      for m in ['Sol', 'Gemini', 'Opus', 'Grok']}
out['by_recipient'] = {m: {f: (cnt([r for r in opening if r['recipient_model'] == m], f, 'author_only'),
                               cnt([r for r in opening if r['recipient_model'] == m], f, 'neither'),
                               round(gap([r for r in opening if r['recipient_model'] == m], f), 1))
                           for f in ['swap', 'cash_bid']}
                       for m in ['Sol', 'Gemini', 'Opus', 'Grok']}
# proposer composition of neither-completing swaps and their acceptances
nsw = [r for r in opening if form(r) == 'swap' and r['completion_cell'] == 'neither']
out['neither_swaps_by_author'] = dict(Counter(r['author_model'] for r in nsw))
out['neither_swap_accepts_by_author'] = dict(Counter(r['author_model'] for r in nsw if r['response'] == 'accept_trade'))

pops = {
    'all_swaps': (opening, 'swap'),
    'no_grok_authors': ([r for r in opening if r['author_model'] != 'Grok'], 'swap'),
    'cash_bids': (opening, 'cash_bid'),
}
block = lambda r: (r['game'] - 1) // 4
for name, (rs, f) in pops.items():
    bg = [gap([r for r in rs if block(r) == b], f) for b in range(5)]
    bcounts = [(cnt([r for r in rs if block(r) == b], f, 'author_only'), cnt([r for r in rs if block(r) == b], f, 'neither')) for b in range(5)]
    loo = [gap([r for r in rs if block(r) != b], f) for b in range(5)]
    # exact enumeration of 5^5 intact-block samples
    draws = []
    for s in itertools.product(range(5), repeat=5):
        sample = [r for b in s for r in rs if block(r) == b]
        draws.append(gap(sample, f))
    draws = sorted(x for x in draws if x == x)
    def pct(v, q):
        k = (len(v) - 1) * q
        lo, hi = int(k), min(int(k) + 1, len(v) - 1)
        return v[lo] + (v[hi] - v[lo]) * (k - lo)
    out[name] = {'pooled': round(gap(rs, f), 1), 'block_gaps': [round(x, 1) for x in bg], 'block_counts': bcounts,
                 'loo_range': [round(min(loo), 1), round(max(loo), 1)],
                 'intact_block_2.5_97.5': [round(pct(draws, .025), 1), round(pct(draws, .975), 1)],
                 'share_draws_le_0': round(sum(x <= 0 for x in draws) / len(draws), 3)}

# within-proposer x recipient check for the no-Grok population (descriptive)
json.dump(out, sys.stdout, indent=1, default=str)
print()
