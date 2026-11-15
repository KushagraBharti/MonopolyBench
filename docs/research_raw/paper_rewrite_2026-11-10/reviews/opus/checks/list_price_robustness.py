"""Read-only robustness of the list-price comparison: restrict to pure cash-for-deed
offers with no mortgage-transfer interest (unmortgaged deeds), and split by first vs
later offer and by responder configuration. No engine, no model."""
import json, statistics as st
ROOT = '/Users/kushagra/CS-Projects/MonopolyBench'
PKG = ROOT + '/docs/research_raw/paper_rewrite_2026-11-10'
O = json.load(open(PKG + '/data/agenda_offers.json'))
board = json.load(open(ROOT + '/contracts/data/board.json'))
price = {s['name'].upper().replace(' ', '_').replace('.', ''): s['price'] for s in board['spaces'] if s.get('price')}
price['B_O_RAILROAD'] = next(s['price'] for s in board['spaces'] if s['name'].startswith('B'))
L = [r for r in O if r['accept_available']]
def buys(r):  # author pays cash only, receives deeds only
    return not r['offer']['properties'] and r['request']['properties'] and r['request']['cash'] == 0 and r['offer']['cash'] > 0
def sells(r):  # author gives deeds only, asks cash only
    return r['offer']['properties'] and not r['request']['properties'] and r['offer']['cash'] == 0 and r['request']['cash'] > 0
def ratio(r, kind):
    if kind == 'buy':
        return r['net_cash_author_to_recipient'] / sum(price[k] for k in r['request']['properties'])
    return -r['net_cash_author_to_recipient'] / sum(price[k] for k in r['offer']['properties'])
def interest(r):
    return r['author_interest_if_accepted'] + r['recipient_interest_if_accepted']
out = {}
for cell, kind, f in [('author_only', 'buy', buys), ('neither', 'buy', buys), ('recipient_only', 'sell', sells), ('neither', 'sell', sells)]:
    for label, cond in [('all', lambda r: True), ('no_interest', lambda r: interest(r) == 0),
                        ('first_offer', lambda r: r['exchange_index'] == 0), ('later_offer', lambda r: r['exchange_index'] > 0)]:
        rs = [r for r in L if r['completion_cell'] == cell and f(r) and cond(r)]
        if rs:
            out[f'{cell}|{kind}|{label}'] = dict(n=len(rs), median_ratio_to_list=round(st.median(ratio(r, kind) for r in rs), 3))
json.dump(out, open(PKG + '/reviews/opus/checks/list_price_robustness.json', 'w'), indent=1)
for k, v in out.items():
    print(k, v)
