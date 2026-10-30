"""Local sample branches; no future-agent policy or winner inference."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def cash(record, player):
    return next(p['cash'] for p in record['snapshot']['players'] if p['player_id'] == player)


def main():
    chosen = {66, 219, 235, 239}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 11 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[66]['source_run']
    engine, decision = restore(run, bundles[66]['decision_id'])
    decision, house = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': 'PARK_PLACE', 'kind': 'HOUSE', 'count': 1}]})
    assert cash(house, 'p2') == 63
    _, ended = apply(engine, decision, 'end_turn', {})
    _, suffix, decision, _ = engine.advance_until_decision(max_steps=100_000)
    assert decision['player_id'] == 'p2' and decision['decision_type'] == 'BUY_OR_AUCTION_DECISION'
    decision, bought = apply(engine, decision, 'buy_property', {})
    assert cash(bought, 'p2') == 163 and bought['snapshot']['board'][8]['owner_id'] == 'p2'
    jail = {}
    for name in ['pay_jail_fine', 'roll_for_doubles']:
        engine, decision = restore(run, bundles[219]['decision_id'])
        _, result = apply(engine, decision, name, {})
        jail[name] = result
    assert cash(jail['pay_jail_fine'], 'p2') == cash(jail['roll_for_doubles'], 'p2') == 830
    assert jail['pay_jail_fine']['snapshot']['players'] == jail['roll_for_doubles']['snapshot']['players']
    assert jail['pay_jail_fine']['snapshot']['board'] == jail['roll_for_doubles']['snapshot']['board']
    engine, decision = restore(run, bundles[235]['decision_id'])
    p4 = next(p for p in engine.state.players if p.player_id == 'p4')
    p2 = next(p for p in engine.state.players if p.player_id == 'p2')
    rents = {str(i): engine._calculate_rent(engine.state.board[i], p4, 7) for i in [1, 3]}
    assert rents == {'1': 160, '3': 320}
    before_rent = engine._calculate_rent(engine.state.board[37], p2, 7)
    decision, hotel = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': 'PARK_PLACE', 'kind': 'HOTEL', 'count': 1}]})
    after_rent = engine._calculate_rent(engine.state.board[37], p2, 7)
    assert (before_rent, after_rent, cash(hotel, 'p2')) == (1300, 1500, 835)
    engine, decision = restore(run, bundles[239]['decision_id'])
    assert engine.get_snapshot()['bank']['houses_remaining'] == 15
    reds_needed = sum(4 - engine.get_snapshot()['board'][i]['houses'] for i in [21, 23, 24])
    assert reds_needed == 7
    _, brown_hotels = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': key, 'kind': 'HOTEL', 'count': 1}
        for key in ['MEDITERRANEAN_AVENUE', 'BALTIC_AVENUE']]})
    assert cash(brown_hotels, 'p4') == 213
    assert brown_hotels['snapshot']['bank']['houses_remaining'] == 23
    report = {'d066': {'house': house, 'end': ended, 'recorded_next_draw': suffix, 'vermont_buy': bought},
              'd219': jail, 'd235': {'hotel': hotel, 'park_rents': [before_rent, after_rent],
                                    'actual_brown_rents': rents},
              'd239': {'affordable_hotels': brown_hotels, 'red_houses_needed_for_four_each': reds_needed},
              'limits': 'Sol nominated d066/d219 before this independent implementation. Draws are historical and unknown to the agent. Jail equality is players/board, not messages, memory or later continuation. Stock check does not prove optimal construction or denial. No winner counterfactual.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g11_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G11 sample branch checks pass.')


if __name__ == '__main__':
    main()
