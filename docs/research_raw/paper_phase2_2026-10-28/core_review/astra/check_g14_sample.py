"""Local source checks for fully read G14 sample bundles; no future outcomes."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    selected = {145, 146, 147, 148, 190, 191}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 14 and int(u['decision_id'][-6:]) in selected}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[145]['source_run']
    engine, decision = restore(run, bundles[145]['decision_id'])
    plan = [{'space_key': key, 'kind': 'HOUSE', 'count': 1}
            for _ in range(4) for key in ['MEDITERRANEAN_AVENUE', 'BALTIC_AVENUE']]
    _, branch = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': plan})
    assert next(p['cash'] for p in branch['snapshot']['players'] if p['player_id'] == 'p2') == 619
    assert [branch['snapshot']['board'][i]['houses'] for i in [1, 3]] == [4, 4]
    engine, decision = restore(run, bundles[145]['decision_id'])
    observed = []
    for n in [145, 146, 147, 148]:
        assert decision['decision_id'] == bundles[n]['decision_id']
        action = bundles[n]['applied_action_record']['action']
        decision, result = apply(engine, decision, action['action'], action['args'])
        observed.append(result)
    assert next(p['cash'] for p in observed[0]['snapshot']['players'] if p['player_id'] == 'p2') == 919
    assert next(p['cash'] for p in observed[-1]['snapshot']['players'] if p['player_id'] == 'p2') == 619
    assert all(bundles[n]['turn_index'] == bundles[145]['turn_index'] for n in [146, 147, 148])
    engine, decision = restore(run, bundles[190]['decision_id'])
    financing = []
    for n in [190, 191]:
        assert decision['decision_id'] == bundles[n]['decision_id']
        action = bundles[n]['applied_action_record']['action']
        decision, result = apply(engine, decision, action['action'], action['args'])
        financing.append(result)
    assert next(p['cash'] for p in financing[-1]['snapshot']['players'] if p['player_id'] == 'p2') == 20
    report = {
        'scope': 'Complete twelve sampled bundles read; adjacent 146-148 and 191 only applied actions/events checked.',
        'original_allocation_interleaved': branch,
        'observed_same_turn_recovery': observed,
        'observed_staged_financing': financing,
        'limits': 'Local legal allocation and observed continuation only; no future winner, optimum, or unchanged memory claim.',
        'source_units': sources,
        'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                          for u in sources.values()},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / 'g14_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G14: original eight houses legal; retry two, same-turn eventual eight; staged mortgages pay debt leaving 20.')


if __name__ == '__main__':
    main()
