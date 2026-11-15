"""Read-only: cash-poor completing settlements (Fable claim), thread position,
and terminal vs nonterminal inheritance from retained ledgers."""
import json, statistics as st, collections
PKG = '/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_rewrite_2026-11-10'
O = json.load(open(PKG + '/data/agenda_offers.json'))
acc = [r for r in O if r['response'] == 'accept_trade']
res = {'settlements': len(acc)}
comp = []; noncomp = []
for r in acc:
    nc = r['net_cash_author_to_recipient']
    if nc == 0:
        continue
    seller = 'recipient' if nc > 0 else 'author'
    seller_cash = r['recipient_cash_before'] if seller == 'recipient' else r['author_cash_before']
    payer_completes = bool(r['author_new_groups']) if nc > 0 else bool(r['recipient_new_groups'])
    any_complete = bool(r['author_new_groups'] or r['recipient_new_groups'])
    row = dict(game=r['game'], dec=r['decision'], seller_model=(r['recipient_model'] if seller == 'recipient' else r['author_model']), seller_cash=seller_cash, cell=r['completion_cell'])
    if payer_completes:
        comp.append(row)
    elif not any_complete:
        noncomp.append(row)
res['completing_paid_settlements'] = len(comp)
res['completing_seller_cash_median'] = st.median(x['seller_cash'] for x in comp)
res['completing_seller_under_100'] = sum(x['seller_cash'] < 100 for x in comp)
res['noncompleting_cash_settlements'] = len(noncomp)
res['noncompleting_seller_cash_median'] = st.median(x['seller_cash'] for x in noncomp)
res['noncompleting_seller_under_100'] = sum(x['seller_cash'] < 100 for x in noncomp)
res['completing_seller_under_100_by_model'] = dict(collections.Counter(x['seller_model'] for x in comp if x['seller_cash'] < 100))
res['completing_seller_by_model'] = dict(collections.Counter(x['seller_model'] for x in comp))
# thread position
first = [r for r in O if r['accept_available'] and r['exchange_index'] == 0]
later = [r for r in O if r['accept_available'] and r['exchange_index'] > 0]
def tab(rs):
    c = collections.Counter((r['completion_cell'], r['response']) for r in rs)
    return {f'{a}|{b}': v for (a, b), v in sorted(c.items())}
res['first_offers'] = tab(first); res['later_offers'] = tab(later)
json.dump(res, open(PKG + '/reviews/opus/checks/settlement_checks.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
