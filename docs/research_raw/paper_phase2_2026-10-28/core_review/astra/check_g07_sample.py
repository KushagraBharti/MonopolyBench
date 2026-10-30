"""Check the final fixed sample's rent, completion and current access claims."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    targets = {101, 168, 203, 263, 302, 319}
    units = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
             if u['game'] == 7 and int(u['decision_id'][-6:]) in targets}
    packets = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in units.items()}
    run = ROOT / packets[101]['source_run']
    results = {}
    for n in sorted(targets):
        engine, decision = restore(run, packets[n]['decision_id'])
        actor = next(p for p in engine.state.players if p.player_id == decision['player_id'])
        result = {'cash': actor.cash, 'menu': decision, 'bank': engine.get_snapshot()['bank']}
        if n == 101:
            unowned = {s.group for s in engine.state.board
                       if s.kind == 'PROPERTY' and s.owner_id is None}
            assert len(unowned) == 8
            result['unowned_color_groups'] = sorted(unowned)
        if n == 168:
            assert actor.cash == 74
            assert [engine.state.board[i].houses for i in [37, 39]] == [2, 3]
            result['dark_blue_rents'] = [engine._calculate_rent(engine.state.board[i], actor, 7)
                                         for i in [37, 39]]
            assert result['dark_blue_rents'] == [500, 1400]
        if n == 203:
            changes = [e for e in packets[n]['canonical_event_segment']
                       if e['type'] == 'CASH_CHANGED' and e['payload']['player_id'] == actor.player_id
                       and e['payload']['reason'] == 'JAIL_FINE']
            assert not changes
            result['recorded_jail_fines'] = changes
        if n in {263, 302}:
            assert actor.cash == 11
            levels = [engine.state.board[i].houses for i in [16, 18, 19]]
            assert levels == ([2, 3, 3] if n == 263 else [3, 3, 3])
            result['orange_rents'] = [engine._calculate_rent(engine.state.board[i], actor, 7)
                                      for i in [16, 18, 19]]
            assert result['orange_rents'] == ([200, 550, 600] if n == 263 else [550, 550, 600])
        if n == 319:
            assert actor.cash == 16 and engine.state.bank.houses_remaining == 2
            assert 'sell_houses_or_hotel' not in packets[n]['initial_prompt']['payload']['action_state']['available_actions']
            assert not packets[n]['resolution']['fallback_used']
        results[str(n)] = result
    report = {'results': results, 'sources': units,
              'related_branch_report': 'g07_claim_checks.json',
              'limits': 'Exact recorded prefixes and current predicates. Earlier329/330 release sequences and183 financing are recorded separately. No winner or optimality claim.',
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in units.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g07_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G07 final sample checks pass.')


if __name__ == '__main__':
    main()
