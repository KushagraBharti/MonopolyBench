"""Local sample financing diagnostics with exact recorded action opportunities."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {82, 119, 138, 163, 211}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 9 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[211]['source_run']
    engine, decision = restore(run, bundles[211]['decision_id'])
    assert not bundles[211]['resolution']['fallback_used']
    decision, mortgage = apply(engine, decision, 'mortgage_property', {'space_key': 'PENNSYLVANIA_RAILROAD'})
    _, build = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': k, 'kind': 'HOUSE', 'count': 1} for k in ['ST_CHARLES_PLACE', 'STATES_AVENUE']]})
    assert next(p['cash'] for p in build['snapshot']['players'] if p['player_id'] == 'p1') == 44
    engine, decision = restore(run, bundles[82]['decision_id'])
    decision, acceptance = apply(engine, decision, 'accept_trade', {})
    assert decision['player_id'] == 'p2' and decision['decision_type'] == 'POST_TURN_ACTION_DECISION'
    _, funded = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': 'PARK_PLACE', 'kind': 'HOUSE', 'count': 1}]})
    assert next(p['cash'] for p in funded['snapshot']['players'] if p['player_id'] == 'p2') == 27
    engine, decision = restore(run, bundles[163]['decision_id'])
    a = bundles[163]['applied_action_record']['action']
    _, actual = apply(engine, decision, a['action'], a['args'])
    owner = next(p for p in engine.state.players if p.player_id == 'p2')
    rents = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [37, 39]]
    assert rents == [1100, 1400]
    engine, _ = restore(run, bundles[119]['decision_id'])
    owner = next(p for p in engine.state.players if p.player_id == 'p2')
    two_house = engine._calculate_rent(engine.state.board[39], owner, 7)
    assert two_house == 600
    report = {'d211_legal_finance_then_two_pink_houses': [mortgage, build],
              'd82_artificial_acceptance_then_seller_build': [acceptance, funded],
              'd163_actual_build': actual, 'd163_dark_blue_rents': rents,
              'd119_two_house_boardwalk_rent': two_house,
              'd138_cash_plus_clear_collateral': 845 + 30 + 90 + 100 + 160,
              'limits': 'd211 is an alternative current management allocation, not optimality. d82 acceptance is artificial and demonstrates only conditional immediate financing. No future rollout or winner.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g09_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G09 sample checks pass: chosen hold has legal two-house alternative;170 sale conditionally funds PP; rents verified.')


if __name__ == '__main__':
    main()
