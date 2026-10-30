"""Immediate legal financing checks after complete G16 sample reading."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 16 and int(u['decision_id'][-6:]) in {173, 261, 304, 322}}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[173]['source_run']

    def branch(n, actor, operations):
        engine, decision = restore(run, bundles[n]['decision_id'])
        records = []
        for name, args in operations:
            assert decision['player_id'] == actor
            decision, record = apply(engine, decision, name, args)
            records.append(record)
        return {'cash': next(p['cash'] for p in engine.get_snapshot()['players']
                             if p['player_id'] == actor), 'steps': records}

    def mortgage(key):
        return 'mortgage_property', {'space_key': key}

    def sale(key, kind='HOUSE'):
        return 'sell_houses_or_hotel', {'sell_plan': [{'space_key': key, 'kind': kind, 'count': 1}]}

    spare = branch(173, 'p3', [mortgage(k) for k in ['ELECTRIC_COMPANY', 'PACIFIC_AVENUE', 'BOARDWALK']])
    assert spare['cash'] == 592
    expanded = branch(173, 'p3', [mortgage(k) for k in ['ELECTRIC_COMPANY', 'PACIFIC_AVENUE', 'BOARDWALK']]
                      + [sale('MEDITERRANEAN_AVENUE', 'HOTEL')])
    assert expanded['cash'] == 617
    orange = ['ST_JAMES_PLACE', 'TENNESSEE_AVENUE', 'NEW_YORK_AVENUE']
    development = {}
    for count, expected in [(3, 615), (4, 565)]:
        keys = orange + (['ST_JAMES_PLACE'] if count == 4 else [])
        ops = [('unmortgage_property', {'space_key': 'NEW_YORK_AVENUE'})]
        ops += [mortgage(k) for k in ['ST_CHARLES_PLACE', 'STATES_AVENUE', 'WATER_WORKS', 'MARVIN_GARDENS']]
        ops += [('build_houses_or_hotel', {'build_plan': [
            {'space_key': k, 'kind': 'HOUSE', 'count': 1} for k in keys]})]
        ops += [sale(k) for k in reversed(keys)] + [mortgage(k) for k in orange]
        result = branch(261, 'p1', ops)
        assert result['cash'] == expected
        development[count] = result
    engine, decision = restore(run, bundles[322]['decision_id'])
    decision, acceptance = apply(engine, decision, 'accept_trade', {})
    assert decision['player_id'] == 'p2'
    assert next(p['cash'] for p in acceptance['snapshot']['players'] if p['player_id'] == 'p2') == 492
    decision, redemption = apply(engine, decision, 'unmortgage_property', {'space_key': 'PARK_PLACE'})
    decision, construction = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': 'BOARDWALK', 'kind': 'HOUSE', 'count': 1}]})
    assert next(p['cash'] for p in construction['snapshot']['players'] if p['player_id'] == 'p2') == 99
    observed = branch(304, 'p2', [('sell_houses_or_hotel', bundles[304]['applied_action_record']['action']['args'])])
    assert observed['cash'] == 5
    report = {
        'scope': 'All twelve common bundles read; local management financing and one artificial acceptance, no future game continuation.',
        'peer_exposure': 'Sol nominated 173, 261 and 322 before this source review. Independent code, not blind replication.',
        'd173_spare_only': spare, 'd173_with_hotel_downgrade': expanded,
        'd261_develop_then_liquidate': development,
        'd322_conditional_acceptance': [acceptance, redemption, construction],
        'd304_observed_valid_liquidation': observed,
        'source_units': sources,
        'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                          for u in sources.values()},
        'canonical_hashes': {n: hashlib.sha256((run / n).read_bytes()).hexdigest()
                             for n in ['events.jsonl', 'actions.jsonl', 'run_config.json']},
        'engine_sha256': hashlib.sha256((ROOT / 'python/packages/engine/src/monopoly_engine/engine.py').read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / 'g16_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G16 checks pass: 592/617; developed then liquidated 615/565; conditional seller build leaves 99; actual Opus survival leaves 5.')


if __name__ == '__main__':
    main()
