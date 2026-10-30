"""Verify chosen holds, unlocked collateral, and mortgage-count rent statements."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 1 and int(u['decision_id'][-6:]) in {318, 327, 426}}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[318]['source_run']
    routes = {}
    yellow = ['ATLANTIC_AVENUE', 'VENTNOR_AVENUE', 'MARVIN_GARDENS']
    rents = {}
    for n, expected in [(318, 1099), (426, 1418)]:
        engine, decision = restore(run, bundles[n]['decision_id'])
        assert decision['player_id'] == 'p4'
        steps = []
        if n == 318:
            owner = next(p for p in engine.state.players if p.player_id == 'p4')
            rail_owner = next(p for p in engine.state.players if p.player_id == 'p3')
            rents = {'park_place': engine._calculate_rent(engine.state.board[37], owner, 7),
                     'pennsylvania_railroad': engine._calculate_rent(engine.state.board[15], rail_owner, 7)}
            assert rents == {'park_place': 70, 'pennsylvania_railroad': 200}
            decision, result = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
                {'space_key': yellow[0], 'kind': 'HOUSE', 'count': 1}]})
            steps.append(result)
            assert next(p['cash'] for p in result['snapshot']['players'] if p['player_id'] == 'p4') == 169
        for key in yellow:
            decision, result = apply(engine, decision, 'sell_houses_or_hotel', {'sell_plan': [
                {'space_key': key, 'kind': 'HOUSE', 'count': 1}]})
            steps.append(result)
        for key in ['MEDITERRANEAN_AVENUE', 'NEW_YORK_AVENUE', 'PARK_PLACE'] + yellow:
            decision, result = apply(engine, decision, 'mortgage_property', {'space_key': key})
            steps.append(result)
        assert next(p['cash'] for p in result['snapshot']['players'] if p['player_id'] == 'p4') == expected
        routes[str(n)] = steps
    assert bundles[327]['initial_prompt']['payload']['game_state']['you']['cash'] == 3772
    charges = [e['payload']['delta'] for e in bundles[327]['canonical_event_segment']
               if e['type'] == 'CASH_CHANGED' and e['payload']['player_id'] == 'p3']
    assert charges == [-50, -12]
    report = {'routes': routes, 'd318_rents': rents, 'd327_cash_after': 3772 + sum(charges),
              'limits': 'Exact recorded decision prefixes, management actions only. No new debt, landing, future behavior, optimality or winner inferred. A no-house-sale policy differs from total financing access.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g01_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G01 sample financing, rent and jail checks pass.')


if __name__ == '__main__':
    main()
