"""Check voluntary development alternatives and unowned completion deeds."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 5 and int(u['decision_id'][-6:]) in {101, 251, 300}}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[101]['source_run']
    engine, decision = restore(run, bundles[101]['decision_id'])
    unowned_by_group = {}
    for space in engine.state.board:
        if space.kind == 'PROPERTY' and space.owner_id is None:
            unowned_by_group.setdefault(space.group, []).append(space.index)
    assert len(unowned_by_group) == 8
    results = {}
    for n, key, kind, cash in [(251, 'PARK_PLACE', 'HOUSE', 274),
                               (300, 'ST_CHARLES_PLACE', 'HOTEL', 337)]:
        engine, decision = restore(run, bundles[n]['decision_id'])
        player_id = decision['player_id']
        if n == 300:
            assert engine.state.bank.houses_remaining == 5
            assert sum(s.houses for s in engine.state.board if s.owner_id == player_id) == 24
        decision, result = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
            {'space_key': key, 'kind': kind, 'count': 1}]})
        assert next(p['cash'] for p in result['snapshot']['players'] if p['player_id'] == player_id) == cash
        results[str(n)] = result
    assert results['300']['snapshot']['bank']['houses_remaining'] == 9
    report = {'unowned_by_group_at101': unowned_by_group, 'branches': results,
              'limits': 'Exact recorded prefixes and one legal development alternative. No modeled recipient reliance, later denial, optimality or winner counterfactual.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g05_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G05 sample completion and construction checks pass.')


if __name__ == '__main__':
    main()
