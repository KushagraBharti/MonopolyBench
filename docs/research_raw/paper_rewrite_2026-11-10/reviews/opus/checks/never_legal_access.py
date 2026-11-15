"""Read-only arithmetic check of the nine trade-completed groups whose first
management window never listed construction. Reads retained window ledger,
board data and canonical decision prompts. Runs no engine code and no model."""
import json, glob, math, sys
ROOT = '/Users/kushagra/CS-Projects/MonopolyBench'
PKG = ROOT + '/docs/research_raw/paper_rewrite_2026-11-10'
board = json.load(open(ROOT + '/contracts/data/board.json'))
price = {}; group = {}
for s in board['spaces']:
    key = s['name'].upper().replace(' ', '_').replace('.', '').replace('&', '').replace('__', '_')
    price[s['index']] = s.get('price'); group[s['index']] = s.get('group')
house_cost = board['house_cost_by_group']
fm = json.load(open(PKG + '/data/first_management_windows.json'))
games = sorted(glob.glob(ROOT + '/saved_games/railway-research-*/game-*/run/decisions.jsonl'))
def load_dec(game, dec_suffix):
    f = games[game - 1]
    for line in open(f):
        r = json.loads(line)
        if r.get('decision_id', '').endswith(dec_suffix):
            return r
# space_key -> price/group via prompt holdings names; build map from board names
name2 = {}
for s in board['spaces']:
    if s.get('price'):
        k = s['name'].upper().replace(' ', '_').replace('.', '')
        name2[k] = s
name2['B_O_RAILROAD'] = next(s for s in board['spaces'] if s['name'].startswith('B'))
out = []
for r in fm['rows']:
    if r['cause'] != 'never_legal_in_window':
        continue
    rec = []
    for d in r['decisions']:
        dd = load_dec(r['game'], d['decision_id'][-10:])
        you = dd['prompt_payload']['game_state']['you']
        opts = dd['prompt_payload']['action_state']['scenario']['options']
        bank = dd['prompt_payload']['game_state']['bank']
        rec.append((d['decision_id'][-10:], you['cash'], opts.get('unmortgageable_space_keys'), opts.get('buildable_space_keys'), opts.get('mortgageable_space_keys'), bank['houses_remaining'], dd['prompt_payload']['action_state']['available_actions']))
    dd = load_dec(r['game'], r['first_mgmt_decision'][-10:])
    you = dd['prompt_payload']['game_state']['you']
    owned = you['holdings']['owned']
    g = r['group']; hc = house_cost[g]
    grp = [o for o in owned if name2[o['space_key']]['group'] == g]
    mort_grp = [o['space_key'] for o in grp if o['mortgaged']]
    redeem = sum(int(math.ceil((name2[k]['price'] // 2) * 1.1)) for k in mort_grp)
    other_mortgage = sum(name2[o['space_key']]['price'] // 2 for o in owned
                         if name2[o['space_key']]['group'] != g and not o['mortgaged'] and o['houses'] == 0 and not o['hotel'])
    cash = you['cash']
    out.append(dict(game=r['game'], player=r['player'], model=r['model'], group=g, decision=r['first_mgmt_decision'][-10:],
                    cash=cash, mortgaged_in_group=mort_grp, redemption_cost=redeem, house_cost=hc,
                    cash_after_redeem=cash - redeem,
                    redeem_and_one_house_from_cash=(cash - redeem) >= hc,
                    other_clear_mortgage_value=other_mortgage,
                    redeem_and_one_house_with_other_mortgages=(cash + other_mortgage - redeem) >= hc,
                    houses_remaining=rec[0][5], window_decisions=rec))
json.dump(out, open(PKG + '/reviews/opus/checks/never_legal_access.json', 'w'), indent=1)
for o in out:
    print(o['game'], o['model'], o['group'], o['decision'], 'cash', o['cash'], 'mortgaged', o['mortgaged_in_group'], 'redeem', o['redemption_cost'], 'house', o['house_cost'],
          'cash_only', o['redeem_and_one_house_from_cash'], 'with_other_mortgages', o['redeem_and_one_house_with_other_mortgages'], 'stock', o['houses_remaining'])
    for w in o['window_decisions']:
        print('   ', w)
