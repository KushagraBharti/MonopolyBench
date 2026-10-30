"""Local sample checks; no hypothetical debt or future outcome."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {80, 111, 177, 189, 254}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 8 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[177]['source_run']
    engine, decision = restore(run, bundles[177]['decision_id'])
    assert bundles[177]['applied_action_record']['action']['action'] == 'end_turn'
    plan = [{'space_key': k, 'kind': 'HOUSE', 'count': 1} for _ in range(2)
            for k in ['ST_JAMES_PLACE', 'TENNESSEE_AVENUE', 'NEW_YORK_AVENUE']]
    plan.append({'space_key': 'NEW_YORK_AVENUE', 'kind': 'HOUSE', 'count': 1})
    _, branch = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': plan})
    assert next(p['cash'] for p in branch['snapshot']['players'] if p['player_id'] == 'p1') == 4
    engine, decision = restore(run, bundles[254]['decision_id'])
    owner = next(p for p in engine.state.players if p.player_id == 'p3')
    rents = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [11, 13, 14]]
    assert rents == [625, 625, 700]
    assert decision['decision_type'] == 'JAIL_DECISION'
    payload = bundles[254]['initial_prompt']['payload']
    assert payload['game_state']['you']['cash'] == 254
    assert 'sell_houses_or_hotel' not in payload['action_state']['available_actions']
    assert engine.state.board[12].name == 'Electric Company'
    orange_liquidation_accounting = 254 + 6 * 50 + 90 + 90 + 100
    assert orange_liquidation_accounting == 834
    engine, _ = restore(run, bundles[189]['decision_id'])
    assert engine.state.board[27].owner_id == 'p2'
    assert engine.state.board[31].owner_id == 'p2'
    assert engine.state.board[29].owner_id == 'p4'
    engine, _ = restore(run, bundles[80]['decision_id'])
    owner = next(p for p in engine.state.players if p.player_id == 'p3')
    rails = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [5, 15, 25, 35]]
    assert rails == [200] * 4
    report = {'d177_interleaved_allocation': branch, 'd254_pink_rents': rents,
              'd254_nominal_liquidation_accounting_not_jail_access': orange_liquidation_accounting,
              'd189_yellow_pair_error': 'Ventnor is yellow; Pacific is green; Marvin is held by p4.',
              'd80_ordinary_rail_rents': rails,
              'limits': 'No financing action added to a jail menu; no alternative winner, optimality or persuasion.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g08_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G08 sample checks pass: interleaved700 leaves4; pink625/625/700; jail action scope retained.')


if __name__ == '__main__':
    main()
