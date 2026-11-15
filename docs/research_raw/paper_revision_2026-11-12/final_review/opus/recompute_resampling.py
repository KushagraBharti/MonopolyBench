"""Opus final review: approximate check of game and two-stage resampling ranges.
Own RNG seed (7), so percentiles should match the paper only approximately."""
import json, random
from pathlib import Path
L = Path(__file__).resolve().parents[1].parent / 'integrated' / 'data' / 'offers.json'
offers = json.load(open(L))
def form(r):
    a, b = r['offer'], r['request']
    jail = a['get_out_of_jail_cards'] or b['get_out_of_jail_cards']
    if a['properties'] and b['properties']: return 'swap'
    if b['properties'] and not a['properties'] and a['cash'] > 0 and b['cash'] == 0 and not jail: return 'cash_bid'
    return 'x'
op = [r for r in offers if r['accept_available'] and r['exchange_index'] == 0]
pops = {'all_swaps': ([r for r in op if form(r) == 'swap'], ),
        'no_grok': ([r for r in op if form(r) == 'swap' and r['author_model'] != 'Grok'], ),
        'cash_bids': ([r for r in op if form(r) == 'cash_bid'], )}
def stats(rs):
    by = {g: [0, 0, 0, 0] for g in range(1, 21)}
    for r in rs:
        c = r['completion_cell']; rej = r['response'] == 'reject_trade'
        if c == 'author_only': by[r['game']][0] += rej; by[r['game']][1] += 1
        elif c == 'neither': by[r['game']][2] += rej; by[r['game']][3] += 1
    return by
def gap(by, games):
    a = sum(by[g][0] for g in games); an = sum(by[g][1] for g in games)
    n = sum(by[g][2] for g in games); nn = sum(by[g][3] for g in games)
    return None if not an or not nn else 100 * (a / an - n / nn)
rng = random.Random(7)
res = {}
for name, (rs,) in pops.items():
    by = stats(rs)
    ind, two = [], []
    for _ in range(20000):
        ind.append(gap(by, [rng.randrange(1, 21) for _ in range(20)]))
        blocks = [rng.randrange(5) for _ in range(5)]
        two.append(gap(by, [4 * b + rng.randrange(4) + 1 for b in blocks for _ in range(4)]))
    def p(v):
        v = sorted(x for x in v if x is not None); k = lambda q: v[int(round((len(v) - 1) * q))]
        return [round(k(.025), 1), round(k(.975), 1)]
    res[name] = {'individual_games': p(ind), 'blocks_then_games': p(two)}
print(json.dumps(res, indent=1))
