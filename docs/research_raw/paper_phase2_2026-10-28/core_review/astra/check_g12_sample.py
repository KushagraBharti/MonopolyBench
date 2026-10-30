"""Reachable financing versus present menus in original fixed sample."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {73, 178, 242, 274, 292, 312}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 12 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[73]['source_run']
    routes = {
        73: [('mortgage_property', {'space_key': k}) for k in
             ['VERMONT_AVENUE', 'PENNSYLVANIA_RAILROAD', 'KENTUCKY_AVENUE', 'INDIANA_AVENUE']]
        + [('build_houses_or_hotel', {'build_plan': [
            {'space_key': k, 'kind': 'HOUSE', 'count': 1} for k in ['PARK_PLACE', 'BOARDWALK']]})],
        178: [('mortgage_property', {'space_key': k}) for k in
              ['BALTIC_AVENUE', 'ORIENTAL_AVENUE', 'VERMONT_AVENUE']]
        + [('build_houses_or_hotel', {'build_plan': [
            {'space_key': 'ILLINOIS_AVENUE', 'kind': 'HOUSE', 'count': 1}]})],
        242: [('mortgage_property', {'space_key': 'BALTIC_AVENUE'}),
              ('build_houses_or_hotel', {'build_plan': [
                  {'space_key': 'ORIENTAL_AVENUE', 'kind': 'HOUSE', 'count': 1}]})],
        312: [('sell_houses_or_hotel', {'sell_plan': [
            {'space_key': 'CONNECTICUT_AVENUE', 'kind': 'HOUSE', 'count': 1}]}),
              ('build_houses_or_hotel', {'build_plan': [
                  {'space_key': 'KENTUCKY_AVENUE', 'kind': 'HOUSE', 'count': 1}]}),
              ('mortgage_property', {'space_key': 'READING_RAILROAD'}),
              ('sell_houses_or_hotel', {'sell_plan': [
                  {'space_key': 'STATES_AVENUE', 'kind': 'HOUSE', 'count': 1}]}),
              ('build_houses_or_hotel', {'build_plan': [
                  {'space_key': 'INDIANA_AVENUE', 'kind': 'HOUSE', 'count': 1}]}),
              ('mortgage_property', {'space_key': 'PENNSYLVANIA_RAILROAD'}),
              ('build_houses_or_hotel', {'build_plan': [
                  {'space_key': 'ILLINOIS_AVENUE', 'kind': 'HOTEL', 'count': 1}]})]}
    expected = {73: ('p2', 15), 178: ('p3', 33), 242: ('p2', 5), 312: ('p2', 26)}
    results = {}
    for n, route in routes.items():
        engine, decision = restore(run, bundles[n]['decision_id'])
        assert decision['decision_type'] == 'POST_TURN_ACTION_DECISION'
        steps = []
        for name, args in route:
            decision, result = apply(engine, decision, name, args)
            steps.append(result)
        player, final_cash = expected[n]
        assert next(p['cash'] for p in result['snapshot']['players'] if p['player_id'] == player) == final_cash
        results[str(n)] = steps
    assert results['312'][-1]['snapshot']['bank']['houses_remaining'] == 4
    engine, decision = restore(run, bundles[274]['decision_id'])
    snapshot = engine.get_snapshot()
    assert snapshot['bank']['houses_remaining'] == 0
    assert sum(s['houses'] for s in snapshot['board'] if s['owner_id'] == 'p2') == 32
    p4 = next(p for p in engine.state.players if p.player_id == 'p4')
    rents = {str(s.index): engine._calculate_rent(s, p4, 7)
             for s in engine.state.board if s.owner_id == 'p4'}
    assert max(rents.values()) == 26
    report = {'routes': results, 'd274_opponent_rents': rents,
              'limits': 'Actual decision prefixes and legal management sequences only. Adjacent73 read for state/menu/action, not full provider text. Sol nominated242/312 before independent implementation. Reallocation and mortgage costs are not neutral; no improved strategy, actual future acceptance, winner or causal influence inferred.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g12_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G12 sample financing/stock checks pass.')


if __name__ == '__main__':
    main()
