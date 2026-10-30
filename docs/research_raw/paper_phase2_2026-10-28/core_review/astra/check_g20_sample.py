"""Financing checks at recorded action opportunities; no hypothetical debt."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {191, 192, 200, 235, 256, 257, 272}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 20 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[200]['source_run']

    def actor(b, pid):
        state = b['initial_prompt']['payload']['game_state']
        return next(p for p in [state['you'], *state['others']] if p['player_id'] == pid)

    prior_financing = {}
    for n, pid, keys, layers, spare, expected in [
        (191, 'p4', ['PACIFIC_AVENUE', 'NORTH_CAROLINA_AVENUE', 'PENNSYLVANIA_AVENUE'],
         2, ['READING_RAILROAD', 'ELECTRIC_COMPANY', 'PENNSYLVANIA_RAILROAD'], 1383),
        (192, 'p1', ['KENTUCKY_AVENUE', 'INDIANA_AVENUE', 'ILLINOIS_AVENUE'], 1, [], 566),
    ]:
        a, b = actor(bundles[n], pid), actor(bundles[200], pid)
        assert a['cash'] == b['cash'] and a['holdings'] == b['holdings']
        old_bank = bundles[n]['initial_prompt']['payload']['game_state']['bank']
        new_bank = bundles[200]['initial_prompt']['payload']['game_state']['bank']
        assert all(old_bank[k] == new_bank[k] for k in ['houses_remaining', 'hotels_remaining'])
        engine, decision = restore(run, bundles[n]['decision_id'])
        assert decision['player_id'] == pid
        steps = []
        for _ in range(layers):
            for key in keys:
                decision, result = apply(engine, decision, 'sell_houses_or_hotel', {
                    'sell_plan': [{'space_key': key, 'kind': 'HOUSE', 'count': 1}]})
                steps.append(result)
        for key in [*keys, *spare]:
            decision, result = apply(engine, decision, 'mortgage_property', {'space_key': key})
            steps.append(result)
        assert next(p.cash for p in engine.state.players if p.player_id == pid) == expected
        prior_financing[n] = {'cash': expected, 'steps': steps,
                              'boundary': 'Same focal cash/holdings and building stock as200; NOT same whole bank inventory or future trajectory.'}

    engine, decision = restore(run, bundles[200]['decision_id'])
    _, build200 = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': 'ST_CHARLES_PLACE', 'kind': 'HOUSE', 'count': 1}]})
    assert next(p['cash'] for p in build200['snapshot']['players'] if p['player_id'] == 'p2') == 51
    engine, decision = restore(run, bundles[257]['decision_id'])
    decision, accept257 = apply(engine, decision, 'accept_trade', {})
    assert decision['player_id'] == 'p3'
    steps257 = [accept257]
    for key in ['ORIENTAL_AVENUE', 'B_O_RAILROAD', 'ATLANTIC_AVENUE', 'MARVIN_GARDENS', 'PARK_PLACE']:
        decision, result = apply(engine, decision, 'mortgage_property', {'space_key': key})
        steps257.append(result)
    decision, result = apply(engine, decision, 'unmortgage_property', {'space_key': 'NEW_YORK_AVENUE'})
    steps257.append(result)
    plan = [{'space_key': k, 'kind': 'HOUSE', 'count': 1} for _ in range(2)
            for k in ['ST_JAMES_PLACE', 'TENNESSEE_AVENUE', 'NEW_YORK_AVENUE']]
    _, result = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': plan})
    steps257.append(result)
    assert next(p.cash for p in engine.state.players if p.player_id == 'p3') == 64
    assert all(engine.state.board[i].hotel for i in [1, 3])

    # Earlier $400 offer: six houses become possible by liquidating the browns.
    engine, decision = restore(run, bundles[235]['decision_id'])
    decision, result = apply(engine, decision, 'accept_trade', {})
    steps235 = [result]
    for key in ['ORIENTAL_AVENUE', 'B_O_RAILROAD', 'ATLANTIC_AVENUE', 'PARK_PLACE']:
        decision, result = apply(engine, decision, 'mortgage_property', {'space_key': key})
        steps235.append(result)
    decision, result = apply(engine, decision, 'unmortgage_property', {'space_key': 'NEW_YORK_AVENUE'})
    steps235.append(result)
    for kind, rounds in [('HOTEL', 1), ('HOUSE', 4)]:
        for _ in range(rounds):
            for key in ['MEDITERRANEAN_AVENUE', 'BALTIC_AVENUE']:
                decision, result = apply(engine, decision, 'sell_houses_or_hotel', {
                    'sell_plan': [{'space_key': key, 'kind': kind, 'count': 1}]})
                steps235.append(result)
    _, result = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': plan})
    steps235.append(result)
    assert next(p.cash for p in engine.state.players if p.player_id == 'p3') == 91
    assert all(not engine.state.board[i].hotel and not engine.state.board[i].houses for i in [1, 3])

    a = actor(bundles[272], 'p1')
    assert a['cash'] == 52
    assert 52 + 75 + 110 + 110 + 120 == 467
    assert 467 - 50 == 417
    report = {'scope': 'Twelve complete fixed bundles; additional191/192/235/257 applied state/menu checked, not full provider bundles.',
              'd200_prior_access_financing': prior_financing, 'd200_legal_single_house': build200,
              'd257_conditional_actual_offer_six_houses_preserving_browns': steps257,
              'd235_conditional_actual_offer_six_houses_liquidating_browns': steps235,
              'd272_full_before_fine': 467, 'd272_full_after_fine': 417,
              'limits': 'No invented debt or out-of-turn control. Conditional acceptance is not actual agreement. No optimality, rationale causation or changed winner.',
              'source_units': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g20_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G20 passes: prior-access1383/566; own build51; conditional six oranges64 preserving browns or91 liquidating browns.')


if __name__ == '__main__':
    main()
