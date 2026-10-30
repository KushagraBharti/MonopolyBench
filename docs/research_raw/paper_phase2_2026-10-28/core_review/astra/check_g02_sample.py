"""Local rent/geography checks supplement existing seven-house replay."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {149, 162, 226, 245, 246, 266, 273}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 2 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[273]['source_run']
    engine, decision = restore(run, bundles[273]['decision_id'])
    p2 = next(p for p in engine.state.players if p.player_id == 'p2')
    orange_rents = {str(i): engine._calculate_rent(engine.state.board[i], p2, 7) for i in [16, 18, 19]}
    assert orange_rents == {'16': 550, '18': 550, '19': 600}
    pairs = [(a, b) for a in range(1, 7) for b in range(1, 7) if 10 + a + b in [16, 18, 19]]
    assert len(pairs) == 14
    assert engine._calculate_rent(engine.state.board[15], p2, 7) == 200
    assert 15 - 10 == 5 and 12 - 10 == 2
    utilities = {}
    for n in [245, 246]:
        engine, decision = restore(run, bundles[n]['decision_id'])
        p2 = next(p for p in engine.state.players if p.player_id == 'p2')
        # Landing suppresses rent on a mortgaged square before calling this helper.
        utilities[str(n)] = {str(i): 0 if engine.state.board[i].mortgaged else
                             engine._calculate_rent(engine.state.board[i], p2, 7)
                             for i in [12, 28]}
    assert utilities['245'] == {'12': 70, '28': 0}
    assert utilities['246'] == {'12': 70, '28': 70}
    engine, decision = restore(run, bundles[226]['decision_id'])
    p1 = next(p for p in engine.state.players if p.player_id == 'p1')
    assert engine.state.board[27].mortgaged and engine.state.board[29].mortgaged
    assert engine._calculate_rent(engine.state.board[26], p1, 7) == 44
    for n, minimum in [(149, 76), (162, 193)]:
        state = bundles[n]['initial_prompt']['payload']
        assert state['game_state']['you']['cash'] == 67
        assert state['action_state']['scenario']['min_next_bid'] == minimum
        assert 'mortgage_property' not in state['action_state']['available_actions']
    report = {'d273_orange_rents': orange_rents, 'direct_death_ordered_pairs': pairs,
              'utility_redemption_rents_on_dice7': utilities,
              'd226_active_atlantic_rent_with_sibling_mortgages': 44,
              'existing_quantity_recovery_report': 'g02_claim_checks.json',
              'limits': 'Direct roll arithmetic excludes card-mediated moves.245 adjacent read for state/action only; no full provider coverage claimed. Correcting explanation figures does not evaluate optimality or future outcomes.',
              'verification_revision': 'Initial test incorrectly assumed _calculate_rent itself suppresses mortgaged-square rent; the actual landing handler does so first (engine.py834). Added that explicit predicate. Active Electric comparison unchanged.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g02_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G02 sample rent, utility and auction checks pass.')


if __name__ == '__main__':
    main()
