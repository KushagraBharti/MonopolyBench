"""Read-only manuscript checks; the only output is beside this script.

This is a fresh event reducer for numerical figure claims, not a new experiment.
It does not rerun the retained engine branches or classify intention.
"""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').exists())
P2 = ROOT / 'docs/research_raw/paper_phase2_2026-10-28/core_review'
P3 = ROOT / 'docs/research_raw/paper_phase3_2026-10-29'


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    retained = read(P2 / 'sol/corpus_economics_audit.json')
    provenance = read(P2 / 'astra/development_aggregation_check.json')
    board = read(ROOT / 'contracts/data/board.json')
    spaces = {s['index']: s for s in board['spaces']}
    colors = defaultdict(list)
    for i, s in spaces.items():
        if s['kind'] == 'PROPERTY':
            colors[s['group']].append(i)
    key_to_index = {re.sub(r'[^A-Z0-9]+', '_', s['name'].upper()).strip('_'): i
                    for i, s in spaces.items()}
    acquisitions, completions, bilateral = Counter(), Counter(), Counter()
    proposals, eligible, proposing, proposal_count = defaultdict(set), defaultdict(set), defaultdict(set), Counter()
    spending = defaultdict(lambda: {'spend': 0, 'salvage': 0, 'whole': 0, 'post': 0})
    original_hashes, nontrade_winners, outcomes, stock_zero = {}, [], [], set()
    completion_trace, g15_events = [], []
    totals = Counter()
    for rel, expected_hash in provenance['event_source_hashes'].items():
        path = ROOT / rel
        assert digest(path) == expected_hash
        game = int(re.search(r'game-(\d+)-', rel).group(1))
        run = path.parent
        config, summary = read(run / 'run_config.json'), read(run / 'summary.json')
        names = {p['player_id']: p['name'] for p in config['players']}
        winner = summary['winner_player_id']
        events, actions = rows(path), rows(run / 'actions.jsonl')
        original_hashes[rel] = expected_hash
        outcomes.append({'game': game, 'winner': names[winner], 'seat': winner,
                         'seed': config['seed'], 'turns': summary['turn_count']})
        totals['events'] += len(events)
        owner, level, last = dict.fromkeys(spaces), dict.fromkeys(spaces, 0), {}
        cash = dict.fromkeys(names, 1500)
        active = set()
        auction = False
        winner_trade = False
        trade_before, trade_parties = None, None

        def complete():
            return {(p, c) for p in names for c, ids in colors.items()
                    if all(owner[i] == p for i in ids)}

        def close_boundary():
            nonlocal active, trade_before
            after = complete()
            for p, c in after - active:
                latest = max((last[i] for i in colors[c]), key=lambda r: r[0])
                completions[latest[1]] += 1
                completion_trace.append({'game': game, 'player': p, 'group': c,
                                         'closing_event': latest[0], 'route': latest[1]})
            active = after
            if trade_before is not None:
                gained = after - trade_before
                bilateral[sum(any(p == who for p, c in gained) for who in trade_parties)] += 1
                trade_before = None

        for e in events:
            typ, payload = e['type'], e['payload']
            if game == 15 and e['seq'] in {711, 718, 1159, 1422, 1424, 1491, 1564, 1566,
                                          1641, 1870, 1985, 1995}:
                g15_events.append(e)
            if typ == 'AUCTION_STARTED': auction = True
            if typ == 'AUCTION_ENDED': auction = False
            if typ == 'TRADE_ACCEPTED':
                assert trade_before is None
                trade_before = complete()
                trade_parties = {payload['initiator_player_id'], payload['counterparty_player_id']}
                winner_trade |= winner in trade_parties
                totals['trades'] += 1
            if typ == 'PROPERTY_PURCHASED':
                i, p = payload['space_index'], payload['player_id']
                route = 'inheritance' if owner[i] is not None else 'auction' if auction else 'direct'
                if route == 'inheritance': assert payload['price'] == 0
                owner[i] = p
                last[i] = (e['seq'], route)
                acquisitions[route] += 1
            if typ == 'PROPERTY_TRANSFERRED':
                i = payload['space_index']
                assert owner[i] == payload['from_player_id']
                owner[i] = payload['to_player_id']
                last[i] = (e['seq'], 'trade')
                acquisitions['trade'] += 1
            if typ in {'HOUSE_BUILT', 'HOTEL_BUILT', 'HOUSE_SOLD', 'HOTEL_SOLD'}:
                i, p, count = payload['space_index'], payload['player_id'], payload['count']
                c = spaces[i]['group']
                u = spending[(game, p, c)]
                price = board['house_cost_by_group'][c]
                if typ.endswith('BUILT'):
                    if not u['spend']:
                        u['first'] = e['seq']
                        u['inherited'] = any(last[j][1] == 'inheritance' for j in colors[c])
                    u['spend'] += price * count
                    level[i] = 5 if typ == 'HOTEL_BUILT' else level[i] + count
                else:
                    u['salvage'] += (price // 2) * count
                    level[i] = 4 if typ == 'HOTEL_SOLD' else level[i] - count
            if typ == 'RENT_PAID':
                i = payload['space_index']
                if spaces[i]['kind'] == 'PROPERTY' and level[i] > 0:
                    u = spending[(game, payload['to_player_id'], spaces[i]['group'])]
                    u['whole'] += payload['amount']
                    if u['spend']: u['post'] += payload['amount']
            if typ == 'CASH_CHANGED':
                p = payload['player_id']
                cash[p] += payload['delta']
                reason = payload.get('reason')
                if reason == 'BUILD': totals['construction_cash'] -= payload['delta']
                if reason == 'SELL_BUILDING': totals['salvage_cash'] += payload['delta']
                if reason == 'BANKRUPTCY': totals['eliminations'] += 1
                if reason == 'BANKRUPTCY_ASSETS_TO_BANK':
                    for i in spaces:
                        if owner[i] == p:
                            owner[i], level[i] = None, 0
                            last.pop(i, None)
            if typ in {'LLM_DECISION_REQUESTED', 'GAME_ENDED'}:
                close_boundary()
        assert not winner_trade or game not in {14, 15}
        if not winner_trade: nontrade_winners.append(game)
        # Direct checks of every original initial payload against the event reducer
        # are in retained phase 2. Re-read source payloads here for opportunity units.
        for d in rows(run / 'decisions.jsonl'):
            if d.get('phase') != 'decision_started': continue
            totals['initial_payloads'] += 1
            state = d['prompt_payload']['game_state']
            if state['bank']['houses_remaining'] == 0: stock_zero.add(game)
            menu = d['prompt_payload']['action_state']
            if d['decision_type'] == 'POST_TURN_ACTION_DECISION' and 'propose_trade' in menu['available_actions']:
                eligible[names[d['player_id']]].add((game, d['turn_index']))
        for a in actions:
            if a['action']['action'] == 'propose_trade':
                name = names[a['actor_player_id']]
                proposing[name].add((game, a['turn_index']))
                proposal_count[name] += 1
        assert cash[winner] == summary.get('final_cash', cash[winner])
    own = {k: v for k, v in spending.items() if v['spend']}
    assert len(own) == 103
    for u in retained['spending_units']:
        new = own[(u['game'], u['actor'], u['group'])]
        assert [new[k] for k in ['spend', 'salvage', 'whole', 'post']] == [u[k] for k in [
            'spend', 'salvage', 'whole_game_developed_rent', 'developed_rent_after_first_own_spend']]
    sums = {k: sum(v[k] for v in own.values()) for k in ['spend', 'salvage', 'whole', 'post']}
    assert (sums['spend'], sums['whole'], sums['post']) == (103450, 93000, 92550)
    assert sums['spend'] == totals['construction_cash']
    assert sums['salvage'] == totals['salvage_cash']
    assert sum(u['whole'] == 0 for u in own.values()) == 40
    assert acquisitions == Counter(direct=475, auction=72, trade=207, inheritance=397)
    assert completions == Counter(direct=16, auction=9, trade=63, inheritance=121)
    assert bilateral == Counter({0: 60, 1: 43, 2: 10})
    assert sorted(nontrade_winners) == [14, 15]
    assert totals['events'] == 50918 and totals['initial_payloads'] == 6989 and totals['eliminations'] == 60
    assert own[(19, 'p1', 'DARK_BLUE')]['spend'] == 2000
    winner_seats = {r['game']: r['seat'] for r in outcomes}
    winner_units = {k: v for k, v in own.items() if k[1] == winner_seats[k[0]]}
    first_routes = {}
    for r in sorted(completion_trace, key=lambda r: (r['game'], r['closing_event'])):
        first_routes.setdefault((r['game'], r['player'], r['group']), r['route'])
    winner_counts = {'spending_units': len(winner_units),
                     'with_inherited_deed': sum(v['inherited'] for v in winner_units.values()),
                     'first_completed_by_estate': sum(first_routes[k] == 'inheritance' for k in winner_units)}
    assert winner_counts == {'spending_units': 58, 'with_inherited_deed': 34,
                             'first_completed_by_estate': 30}
    g15_groups = sorted([r for r in completion_trace if r['game'] == 15 and r['player'] == 'p1'],
                        key=lambda r: r['closing_event'])
    assert g15_groups[0]['group'] == 'ORANGE' and g15_groups[0]['closing_event'] == 711
    assert own[(15, 'p1', 'ORANGE')]['first'] == 718
    assert own[(15, 'p1', 'ORANGE')]['whole'] == 3250
    assert next(r for r in g15_groups if r['group'] == 'GREEN')['closing_event'] == 1995
    assert (15, 'p1', 'GREEN') not in own
    neg = {m: {'eligible_turns': len(eligible[m]), 'proposing_turns': len(proposing[m]),
               'proposals': proposal_count[m]} for m in eligible}
    expected_neg = read(P2 / 'astra/negotiation_units.json')['summary']['initiation']
    assert all(all(v == expected_neg[m][k] for k, v in row.items()) for m, row in neg.items())
    # Exported figures are checked against retained audits, with exact provenance.
    export = read(P3 / 'astra/exhibits/t05_spending_units.json')
    assert len(export) == len(own)
    debt = read(P3 / 'astra/exhibits/t06_eliminations.json')
    assert len(debt) == 60
    assert sum(d['full'] < d['owed'] for d in debt) == 56
    assert sum(d['accessible'] >= d['owed'] for d in debt) == 3
    assert [(d['game'], d['full'], d['accessible'], d['owed']) for d in debt if d['accessible'] != d['full']] == [(7, 1310, 440, 750)]
    recovery = read(P2 / 'sol/build_recovery_audit.json')
    assert len([d for d in recovery['defaults'] if 'opus' in d['model']]) == 61
    assert recovery['summary']['opus_all61_same_allocation_legal_after_interleaving']
    # This validates retained legal-proof provenance; it does not rerun the engine.
    proof_files = ['g12_public_claim_checks.json', 'elimination_upper_bounds.json',
                   'g07_stock_retention_check.json', 'g20_sample_financing_checks.json',
                   'g16_liquidity_and_development_checks.json']
    proofs = {str((P2 / 'sol' / f).relative_to(ROOT)): digest(P2 / 'sol' / f) for f in proof_files}
    keys = set(re.findall(r'@[^{]+\{([^,]+),', (P3 / 'references.bib').read_text()))
    tex = '\n'.join((HERE / f).read_text() for f in ['methods_economics.tex',
                         'framing_conduct_bridge.tex', 'title_abstract.tex', 'economic_figures.tex'])
    cites = {k.strip() for group in re.findall(r'\\cite\{([^}]+)\}', tex) for k in group.split(',')}
    assert not (cites - keys)
    protected = read(HERE.parents[1] / 'protected_sources.json')
    assert all(digest(ROOT / path) == value for path, value in protected.items())
    report = {'status': 'pass', 'fresh_original_event_reduction': dict(totals),
              'acquisitions': dict(acquisitions), 'completions': dict(completions),
              'bilateral_completion_sides': dict(bilateral), 'spending_units': len(own),
              'spending_sums': sums, 'negotiation': neg, 'nontrade_winners': sorted(nontrade_winners),
              'zero_house_games': sorted(stock_zero), 'citation_keys': sorted(cites),
              'winner_spending_units': winner_counts, 'protected_source_hashes': protected,
              'g15_winner_group_sequence': g15_groups, 'g15_original_event_endpoints': g15_events,
              'original_event_hashes': original_hashes, 'retained_legal_proof_hashes': proofs,
              'limits': 'Fresh reduction of canonical events and original initial payload opportunity counts; source targets were known. No fresh engine branch, provider call, new game, blind annotation, semantic census, causal estimate, or public-release verification. The 61 reorderability and 60 accessibility classifications are provenance-checked retained proofs.',
              'script_sha256': digest(Path(__file__))}
    (HERE / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'spending_units', 'spending_sums', 'nontrade_winners']}))


if __name__ == '__main__':
    main()
