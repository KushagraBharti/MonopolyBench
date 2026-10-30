"""Source assertions for G15 common-sample semantic boundaries."""

import hashlib
import json
from pathlib import Path

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    selected = {35, 169, 180, 262, 271}
    sources = {int(u['decision_id'][-6:]): u for u in rows(LEDGER)
               if u['game'] == 15 and int(u['decision_id'][-6:]) in selected}
    bundles = {n: rows(ROOT / u['packet'])[u['packet_line'] - 1] for n, u in sources.items()}
    run = ROOT / bundles[180]['source_run']
    b = bundles[169]
    note = b['applied_action_record']['action']['private_thought']
    raw = b['attempts'][0]['raw_response']['choices'][0]['message']['reasoning']
    assert "one house each ($600)" in note
    assert "I could build one house on a single green property for $200, leaving $33" in raw
    assert b['initial_prompt']['payload']['game_state']['you']['cash'] - 100 == 233
    assert 233 < 600 and 233 >= 200
    survivor = next(p for p in bundles[262]['initial_prompt']['payload']['game_state']['others']
                    if p['player_id'] == 'p4')
    assert survivor['cash'] == 11
    assert [p['space_key'] for p in survivor['holdings']['owned'] if not p['mortgaged']] == ['READING_RAILROAD']
    assert all(not p['houses'] and not p['hotel'] for p in survivor['holdings']['owned'])
    engine, decision = restore(run, bundles[180]['decision_id'])
    decision, sale = apply(engine, decision, 'sell_houses_or_hotel', bundles[180]['applied_action_record']['action']['args'])
    assert next(p['cash'] for p in sale['snapshot']['players'] if p['player_id'] == 'p3') == 76
    assert [sale['snapshot']['board'][i]['houses'] for i in [37, 39]] == [0, 1]
    owned = bundles[271]['initial_prompt']['payload']['game_state']['you']['holdings']['owned']
    assert len([p for p in owned if p['space_key'] in ['READING_RAILROAD', 'PENNSYLVANIA_RAILROAD', 'B_O_RAILROAD', 'SHORT_LINE']]) == 3
    assert 'three rails owned' in bundles[271]['applied_action_record']['action']['private_thought']
    report = {
        'scope': 'All twelve common bundles fully read. One recorded liquidation replay; source assertions, no conditional trade or future play.',
        'd169_semantic_boundary': {'applied_note': note, 'provider_acknowledges_single_house': True,
                                   'post_offer_cash': 233, 'one_each_cost': 600,
                                   'limit': 'No full-layer mandatory-rule error established by this wording. No recipient action access asserted.'},
        'd262_current_opponent_financing_upper_bound': 111,
        'd180_observed_one_house_sale': sale,
        'd271_owned_railroads': 3,
        'source_units': sources,
        'packet_hashes': {u['packet']: hashlib.sha256((ROOT / u['packet']).read_bytes()).hexdigest()
                          for u in sources.values()},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / 'g15_sample_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print('G15 checks pass: qualified full-layer statement, 111 current opponent bound, observed one-house sale leaves 76, three owned railroads.')


if __name__ == '__main__':
    main()
