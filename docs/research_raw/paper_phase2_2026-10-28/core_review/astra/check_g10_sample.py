"""Sampled chosen holds and local conditional trade/access checks."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    chosen = {111, 131, 132, 133}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 10 and int(u['decision_id'][-6:]) in chosen}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[132]['source_run']
    engine, decision = restore(run, bundles[131]['decision_id'])
    decision, accepted = apply(engine, decision, 'accept_trade', {})
    cash = {p['player_id']: p['cash'] for p in accepted['snapshot']['players']}
    assert cash['p3'] == 489 and cash['p4'] == 441
    assert decision['player_id'] == 'p3' and decision['decision_type'] == 'POST_TURN_ACTION_DECISION'
    next_decision, end = apply(engine, decision, 'end_turn', {})
    assert next_decision is None
    _, suffix, next_decision, _ = engine.advance_until_decision(max_steps=100_000)
    assert next_decision['player_id'] == 'p1'
    assert any(e['type'] == 'SENT_TO_JAIL' and e['payload']['player_id'] == 'p4' for e in suffix)
    assert not any(e['type'] == 'LLM_DECISION_REQUESTED' and e['payload']['player_id'] == 'p4' for e in suffix)
    engine, decision = restore(run, bundles[133]['decision_id'])
    _, fourths = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': k, 'kind': 'HOUSE', 'count': 1}
        for k in ['ORIENTAL_AVENUE', 'VERMONT_AVENUE', 'CONNECTICUT_AVENUE']]})
    assert next(p['cash'] for p in fourths['snapshot']['players'] if p['player_id'] == 'p1') == 4
    owner = next(p for p in engine.state.players if p.player_id == 'p1')
    rents = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [6, 8, 9]]
    assert rents == [400, 400, 450] and 489 >= max(rents)
    direct_pairs = [(a, b) for a in range(1, 7) for b in range(1, 7) if 5 + a + b in [6, 8, 9]]
    assert len(direct_pairs) == 5
    engine, decision = restore(run, bundles[111]['decision_id'])
    _, reserve_alternative = apply(engine, decision, 'build_houses_or_hotel', {'build_plan': [
        {'space_key': 'PARK_PLACE', 'kind': 'HOUSE', 'count': 1}]})
    assert next(p['cash'] for p in reserve_alternative['snapshot']['players'] if p['player_id'] == 'p2') == 137
    report = {'d131_artificial_acceptance': accepted, 'return_control_player': 'p3',
              'd131_branch_end': end, 'immediate_recorded_draw_suffix': suffix,
              'next_decision': next_decision,
              'd133_three_fourth_houses': fourths, 'four_house_light_blue_rents': rents,
              'reading_direct_light_blue_ordered_dice_pairs': direct_pairs,
              'd111_second_park_house_alternative': reserve_alternative,
              'limits': 'd131 adjacent action/menu read, not its complete provider bundle. Acceptance artificial; immediate suffix uses recorded draws unavailable to agents. No later LLM continuation, optimality, bankruptcy or winner conclusion. Five pairs exclude indirect card movement.',
              'sources': sources,
              'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                                for u in sources.values()},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / 'g10_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G10 sample checks pass:489 covers four-house LB; trade returns seller control; buyer next goes to jail; chosen-hold alternatives legal.')


if __name__ == '__main__':
    main()
