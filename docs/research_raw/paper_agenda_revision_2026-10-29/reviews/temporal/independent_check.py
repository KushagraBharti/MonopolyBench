"""Review retained temporal rows against originals, without importing the reducer."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SOURCE = HERE.parents[1] / 'temporal'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    inspected = {str(p.relative_to(REPO)): sha(p) for p in SOURCE.iterdir()
                 if p.is_file() and p.suffix in {'.json', '.jsonl', '.md', '.py', '.tex'}}
    sample = load(SOURCE / 'sample_fields.json')
    ledger = [json.loads(x) for x in (SOURCE / 'row_ledger.jsonl').read_text().splitlines()]
    by_id = {x['id']: x for x in sample}
    games = {}
    hashes = {}
    for row in sample:
        game = row['game']
        if game in games:
            continue
        directory = REPO / row['source_run']
        actions = {}
        for line, text in enumerate((directory / 'actions.jsonl').read_text().splitlines(), 1):
            obj = json.loads(text)
            actions[obj['decision_id']] = (line, obj)
        decisions = {}
        resolved = {}
        for line, text in enumerate((directory / 'decisions.jsonl').read_text().splitlines(), 1):
            obj = json.loads(text)
            if obj['phase'] == 'decision_started':
                decisions[obj['decision_id']] = (line, obj['prompt_payload'], obj['player_id'], obj['turn_index'])
            elif obj['phase'] == 'decision_resolved':
                resolved[obj['decision_id']] = (line, obj['fallback_used'])
        events = [json.loads(x) for x in (directory / 'events.jsonl').read_text().splitlines()]
        games[game] = (actions, decisions, resolved, events)
        for name in ['actions.jsonl', 'decisions.jsonl', 'events.jsonl']:
            path = directory / name
            hashes[str(path.relative_to(REPO))] = sha(path)
    assert len(sample) == len(ledger) == len(by_id) == 240
    original_manifest = [json.loads(x) for x in (REPO / 'docs/research_raw/paper_phase2_2026-10-28/core_review/public_unflagged_sample.jsonl').read_text().splitlines()]
    assert {x['decision_id'] for x in sample} == {x['decision_id'] for x in original_manifest}
    for row in sample:
        original = next(x for x in original_manifest if x['decision_id'] == row['decision_id'])
        assert row['selection_rank'] == original['selection_rank']
        assert row['public_unflagged_pool_size'] == original['eligible_in_stratum']
    assert Counter(x['game'] for x in sample) == {g: 12 for g in range(1, 21)}
    assert set(Counter((x['game'], x['player_id']) for x in sample).values()) == {3}
    private_absent = 0
    for row in sample:
        a, d, r, _ = games[row['game']]
        line, action = a[row['decision_id']]
        _, payload, player, turn = d[row['decision_id']]
        assert line == row['source']['action_line']
        assert action['action']['action'] == row['action']
        assert action['action']['args'] == row['args']
        assert player == row['player_id'] and turn == row['turn_index']
        assert payload['action_state'] == row['menu']
        assert payload['game_state']['you']['cash'] == row['cash']
        assert payload['game_state']['you']['holdings'] == row['holdings']
        assert r[row['decision_id']][1] == row['fallback_used'] is False
        for field, record in row['fields'].items():
            expected = action['action'].get(field)
            assert expected == record['value']
            assert (field in action['action']) == record['present']
            if expected is not None:
                assert hashlib.sha256(expected.encode()).hexdigest() == record['sha256']
        private_absent += 'private_thought' not in action['action']
    assert private_absent == 53
    assert all('Opus' in x['model'] or 'opus' in x['model'] for x in sample
               if not x['fields']['private_thought']['present'])
    assert len({x['id'] for x in ledger if 'P' in x['semantic_tags']}) == 59
    tags = Counter(t for x in ledger for t in x['semantic_tags'])
    assert tags['P'] == 59 and tags['O'] == 36 and tags['R'] == 25
    assert all(x['plan_endpoint'] is not None for x in ledger if 'P' in x['semantic_tags'])
    assert all(x['plan_endpoint'] is None for x in ledger if 'P' not in x['semantic_tags'])

    checked_records = set()

    def check_record(value):
        if isinstance(value, list):
            for child in value:
                check_record(child)
        elif isinstance(value, dict):
            src = value.get('source')
            if isinstance(src, dict) and 'action_line' in src and 'action' in value:
                game, decision = value['game'], value['decision_id']
                aa, dd, rr, ee = games[game]
                aline, obj = aa[decision]
                dline, payload, actor, turn = dd[decision]
                assert value['action'] == obj['action'], (game, decision, 'action')
                assert src['action_line'] == aline
                assert src['started_line'] == dline
                assert src['resolved_line'] == rr[decision][0]
                assert value['actor'] == actor and value['turn'] == turn
                assert value['menu'] == payload['action_state']
                assert value['cash_before'] == payload['game_state']['you']['cash']
                assert value['holdings_before'] == payload['game_state']['you']['holdings']
                assert value['bank_before'] == payload['game_state']['bank']
                assert value['events'] == [ee[line - 1] for line in src['event_lines']]
                for field, digest in value['field_sha256'].items():
                    assert hashlib.sha256(obj['action'][field].encode()).hexdigest() == digest
                checked_records.add((game, decision))
            for child in value.values():
                if isinstance(child, (dict, list)):
                    check_record(child)

    for name in ['landing_policy_endpoints.json', 'longitudinal_witnesses.json', 'forecast_endpoints.json']:
        check_record(load(SOURCE / name))

    landing = load(SOURCE / 'landing_policy_endpoints.json')
    traces = load(SOURCE / 'longitudinal_witnesses.json')
    assert len(landing) == 8 and len(traces) == 19
    plan_ids = {x['id'] for x in ledger if 'P' in x['semantic_tags']}
    landing_ids = {x['id'] for x in landing}
    trace_ids = {x['id'] for x in traces}
    assert landing_ids.isdisjoint(trace_ids)
    assert landing_ids | trace_ids <= plan_ids
    assert len(plan_ids - landing_ids - trace_ids) == 32
    independent_landing = []
    for policy in landing:
        row = by_id[policy['id']]
        aa, dd, _, _ = games[row['game']]
        opportunities = []
        for decision, (_, payload, actor, _) in dd.items():
            ix = int(decision.rsplit('-', 1)[1])
            if actor != row['player_id'] or ix <= row['decision_index']:
                continue
            menu = payload['action_state']
            if menu['decision_type'] == 'BUY_OR_AUCTION_DECISION' and menu['scenario']['landed_space'] in policy['target_deeds']:
                opportunities.append((ix, decision, aa[decision][1]['action']['action']))
        opportunities.sort()
        assert [x[1] for x in opportunities] == [x['decision_id'] for x in policy['all_matching_opportunities']]
        status = ('no_observed_opportunity' if not opportunities else
                  ('purchase_applied' if opportunities[0][2] == 'buy_property' else 'purchase_not_applied'))
        assert status == policy['status']
        independent_landing.append({'id': policy['id'], 'targets': policy['target_deeds'], 'opportunities': opportunities, 'status': status})

    # Compact original endpoint evidence for manual inspection. No provider summaries.
    selected = {2: [161, 162, 163, 164, 256], 3: [207],
                9: [64, 65, 66, 67, 102, 162, 163, 164],
                14: [145, 146, 147, 148, 149],
                16: [103, 159, 160, 161, 162, 163, 164, 165],
                17: [162, 164, 166, 168, 169, 170, 171, 172, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 240, 241, 242, 243, 246, 252, 253, 254, 255, 256, 257, 261, 264, 267],
                19: [220, 221, 222, 223, 224, 225],
                20: [40, 41, 42, 43, 44, 45, 46, 47, 99, 100, 101, 102, 103, 104]}
    context = []
    for game, indices in selected.items():
        aa, dd, _, ee = games[game]
        for decision, (_, payload, actor, turn) in dd.items():
            ix = int(decision.rsplit('-', 1)[1])
            if ix not in indices:
                continue
            context.append({'game': game, 'decision': ix, 'actor': actor, 'turn': turn,
                            'cash': payload['game_state']['you']['cash'],
                            'holdings': payload['game_state']['you']['holdings'],
                            'menu': payload['action_state'], 'action': aa[decision][1]['action']})
    (HERE / 'original_endpoint_context.json').write_text(json.dumps(context, indent=2) + '\n')
    g3events = [x for x in games[3][3] if 1485 <= x['seq'] <= 1496]
    assert [x['payload']['is_double'] for x in g3events if x['type'] == 'DICE_ROLLED'] == [True, False]
    assert all(x['actor']['player_id'] == 'p1' for x in g3events if x['type'] == 'DICE_ROLLED')
    (HERE / 'g03_doubles_endpoint_events.json').write_text(json.dumps(g3events, indent=2) + '\n')
    g17later = [x for x in context if x['game'] == 17 and x['actor'] == 'p1' and x['decision'] > 231]
    management = [x for x in g17later if x['menu']['decision_type'] == 'POST_TURN_ACTION_DECISION']
    assert [x['decision'] for x in management] == [257, 261, 264]
    assert not any('build_houses_or_hotel' in x['menu']['available_actions'] for x in management)
    assert not any(x['action']['action'] == 'build_houses_or_hotel' for x in g17later)
    assert g17later[-1]['decision'] == 267 and g17later[-1]['action']['action'] == 'declare_bankruptcy'
    output = {'inspected_source_hashes': inspected, 'canonical_source_hashes': hashes,
              'sample_rows': len(sample), 'private_absent': private_absent, 'source_mismatches': 0,
              'tags_recounted_not_independently_relabelled': dict(tags),
              'unique_original_witness_decisions_verified': len(checked_records),
              'landing_recount': independent_landing,
              'landing_status_counts': dict(Counter(x['status'] for x in independent_landing)),
              'g03_first_stock_endpoint_before_any_opponent_action': True,
              'g17_rival_management_until_elimination': [257, 261, 264],
              'g17_rival_build_menus_until_elimination': 0,
              'limits': ['Source equality and endpoint checks do not validate every semantic label.',
                         'No engine execution, provider query, theory-of-mind or causal-learning test performed.']}
    (HERE / 'source_checks.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if 'hashes' not in k and k != 'landing_recount'}, indent=2))


if __name__ == '__main__':
    main()
