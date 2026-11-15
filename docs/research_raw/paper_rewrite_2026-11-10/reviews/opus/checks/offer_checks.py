"""Read-only re-tabulation of the retained offer ledger (agenda_offers.json) and
board list prices. Tests: cash direction vs list price; counter content; cash-poor
completing sales; thread position. No engine, no model."""
import json, statistics as st, collections
ROOT = '/Users/kushagra/CS-Projects/MonopolyBench'
PKG = ROOT + '/docs/research_raw/paper_rewrite_2026-11-10'
O = json.load(open(PKG + '/data/agenda_offers.json'))
board = json.load(open(ROOT + '/contracts/data/board.json'))
price = {}
for s in board['spaces']:
    if s.get('price'):
        price[s['name'].upper().replace(' ', '_').replace('.', '')] = s['price']
price['B_O_RAILROAD'] = next(s['price'] for s in board['spaces'] if s['name'].startswith('B'))
res = {}
legal = [r for r in O if r['accept_available']]
res['n_all'] = len(O); res['n_legal'] = len(legal)
cells = collections.Counter((r['completion_cell'], r['response']) for r in legal)
res['cells'] = {f'{a}|{b}': c for (a, b), c in sorted(cells.items())}
# pure cash-for-deeds purchases by the author (author gives only cash, receives only deeds)
def lp(keys):
    return sum(price[k] for k in keys)
out = {}
for cell in ['author_only', 'recipient_only', 'both', 'neither']:
    rows = [r for r in legal if r['completion_cell'] == cell]
    # author buys: author offers cash only, requests deeds only
    buy = [r for r in rows if not r['offer']['properties'] and r['request']['properties'] and r['request']['cash'] == 0 and r['offer']['cash'] > 0]
    # author sells: author offers deeds only, requests cash only
    sell = [r for r in rows if r['offer']['properties'] and not r['request']['properties'] and r['offer']['cash'] == 0 and r['request']['cash'] > 0]
    def summ(rs, sign):
        diffs = [sign * r['net_cash_author_to_recipient'] - lp(r['request']['properties'] if sign == 1 else r['offer']['properties']) for r in rs]
        ratios = [(sign * r['net_cash_author_to_recipient']) / lp(r['request']['properties'] if sign == 1 else r['offer']['properties']) for r in rs]
        if not rs:
            return None
        return dict(n=len(rs), median_cash_minus_list=st.median(diffs), share_above_list=sum(d > 0 for d in diffs) / len(rs),
                    median_ratio=round(st.median(ratios), 3),
                    accepted=sum(r['response'] == 'accept_trade' for r in rs),
                    accepted_median_cash_minus_list=(st.median([d for d, r in zip(diffs, rs) if r['response'] == 'accept_trade']) if any(r['response'] == 'accept_trade' for r in rs) else None))
    out[cell] = dict(n=len(rows), author_buys=summ(buy, 1), author_sells=summ(sell, -1))
res['pure_cash_deed_vs_list_price'] = out
# cash direction: completing side pays (Fable claim 373/429)
pay = 0; tot = 0
for r in legal:
    if r['completion_cell'] == 'author_only':
        tot += 1; pay += r['net_cash_author_to_recipient'] > 0
    if r['completion_cell'] == 'recipient_only':
        tot += 1; pay += r['net_cash_author_to_recipient'] < 0
res['completing_side_pays'] = [pay, tot]
# deed direction: in one-sided offers, does the completing side receive more deeds than it gives?
recv = 0
for r in legal:
    if r['completion_cell'] == 'author_only':
        recv += len(r['request']['properties']) > 0
    if r['completion_cell'] == 'recipient_only':
        recv += len(r['offer']['properties']) > 0
res['completing_side_receives_a_deed'] = [recv, tot]
# counter content (Opus draft claim): join each counter to the next row of the same thread
by_thread = collections.defaultdict(list)
for r in O:
    by_thread[r['thread_id']].append(r)
for t in by_thread.values():
    t.sort(key=lambda r: r['exchange_index'])
cc = collections.Counter(); cash_up = collections.Counter(); deltas = collections.defaultdict(list)
for t in by_thread.values():
    for i, r in enumerate(t):
        if r['response'] != 'counter_trade':
            continue
        if i + 1 >= len(t):
            cc['no_next_row'] += 1; continue
        n = t[i + 1]
        assert n['author'] == r['recipient'], (r['thread_id'], i)
        keeps_orig_author = bool(n['recipient_new_groups'])  # original author is now recipient
        counterer_gets = bool(n['author_new_groups'])
        key = (r['completion_cell'], 'keep_author' if keeps_orig_author else 'drop_author', 'counterer_completes' if counterer_gets else 'counterer_no')
        cc[key] += 1
        # counterer net cash: under original offer counterer is recipient: +net_cash(orig); under counter, counterer is author: -net_cash(new)
        delta = (-n['net_cash_author_to_recipient']) - (r['net_cash_author_to_recipient'])
        deltas[key].append(delta); cash_up[key] += delta > 0
res['counter_content'] = {'|'.join(k) if isinstance(k, tuple) else k: dict(n=v, cash_up=cash_up.get(k, 0), median_delta=(st.median(deltas[k]) if deltas.get(k) else None)) for k, v in sorted(cc.items(), key=lambda x: str(x[0]))}
json.dump(res, open(PKG + '/reviews/opus/checks/offer_checks.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
