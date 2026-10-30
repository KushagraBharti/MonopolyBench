"""Original sample checks; local replays and rent calculations, no rollouts."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {220, 234, 235, 236, 269}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 19 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[234]['source_run']
    engine, decision = restore(run, bundles[234]['decision_id'])
    plan = [{'space_key': k, 'kind': 'HOUSE', 'count': 1} for _ in range(3)
            for k in ['KENTUCKY_AVENUE', 'INDIANA_AVENUE', 'ILLINOIS_AVENUE']]
    _, branch = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': plan})
    assert next(p['cash'] for p in branch['snapshot']['players'] if p['player_id'] == 'p1') == 262
    engine, decision = restore(run, bundles[234]['decision_id'])
    observed = []
    for n in [234, 235, 236]:
        assert decision['decision_id'] == bundles[n]['decision_id']
        a = bundles[n]['applied_action_record']['action']
        decision, result = apply(engine, decision, a['action'], a['args'])
        observed.append(result)
    assert next(p['cash'] for p in observed[0]['snapshot']['players'] if p['player_id'] == 'p1') == 1162
    assert next(p['cash'] for p in observed[-1]['snapshot']['players'] if p['player_id'] == 'p1') == 262
    assert all(bundles[n]['turn_index'] == bundles[234]['turn_index'] for n in [235, 236])
    engine, _ = restore(run, bundles[269]['decision_id'])
    owner = next(p for p in engine.state.players if p.player_id == 'p4')
    rail_rents = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [5, 15, 25]]
    assert rail_rents == [100, 100, 100]
    engine, decision = restore(run, bundles[220]['decision_id'])
    owner = next(p for p in engine.state.players if p.player_id == 'p4')
    pink_rents = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [11, 13, 14]]
    assert pink_rents == [450, 450, 500]
    mortgages = []
    for key in ['KENTUCKY_AVENUE', 'ILLINOIS_AVENUE']:
        decision, result = apply(engine, decision, 'mortgage_property', {'space_key': key})
        mortgages.append(result)
    assert next(p['cash'] for p in mortgages[-1]['snapshot']['players'] if p['player_id'] == 'p2') == 502
    report = {'scope': 'Twelve complete sample bundles; adjacent 235/236 applied actions checked only.',
              'd234_interleaved_original': branch, 'd234_236_observed': observed,
              'd269_active_rail_rents': rail_rents, 'd220_pink_rents': pink_rents,
              'd220_legal_current_management_mortgages': mortgages,
              'limits': 'No invented debt, future opponent turn or winner. Current finances cover pink schedule but not light-blue hotels.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g19_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G19 sample checks pass: nine-house original legal; same-turn recovery reaches it; rail rents100; pink450/450/500 covered by502.')


if __name__ == '__main__':
    main()
