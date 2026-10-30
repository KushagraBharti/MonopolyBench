"""Canonical-source crosschecks and deliberate corruptions for this extension."""
import copy
import json
from collections import Counter
from pathlib import Path

from analyze_negotiation import HERE, ROOT, digest, game_dirs, rows


def load():
    return {name: json.loads((HERE / f'{name}.json').read_text())
            for name in ['results', 'threads', 'offers', 'flows', 'concentration', 'games']}


def validate(data, source):
    result, threads, offers, flows = [data[x] for x in ['results', 'threads', 'offers', 'flows']]
    assert len({r['thread_id'] for r in threads}) == len(threads)
    assert len({r['decision_id'] for r in offers}) == len(offers)
    indexed = {r['decision_id']: r for r in offers}
    for thread in threads:
        local = [indexed[key] for key in thread['response_ids']]
        assert len(local) == thread['response_count'] == thread['counter_count'] + 1
        assert [r['exchange_index'] for r in local] == list(range(len(local)))
        assert local[-1]['response_seq'] == thread['terminal_seq']
        assert local[-1]['response'] == ('accept_trade' if thread['terminal'] == 'TRADE_ACCEPTED' else 'reject_trade')
        assert all(r['response'] == 'counter_trade' for r in local[:-1])
        assert all(r['thread_id'] == thread['thread_id'] for r in local)
    assert sum(len(t['response_ids']) for t in threads) == len(offers)
    for name, value in [('threads', len(threads)), ('responses', len(offers)),
                        ('settlements', sum(r['response'] == 'accept_trade' for r in offers)),
                        ('counters', sum(r['response'] == 'counter_trade' for r in offers)),
                        ('rejections', sum(r['response'] == 'reject_trade' for r in offers))]:
        assert result['counts'][name] == value == source['counts'][name], (name, value)
    for row in offers:
        original = source['decisions'][row['decision_id']]
        p = original['prompt_payload']
        offer = p['action_state']['scenario']['current_offer']
        assert row['author'] == offer['from_player_id']
        assert row['recipient'] == original['player_id']
        assert row['offer'] == offer['if_you_accept']['you_receive']
        assert row['request'] == offer['if_you_accept']['you_give']
        assert row['response'] == source['actions'][row['decision_id']]['action']['action']
        assert row['accept_available'] == ('accept_trade' in p['action_state']['available_actions'])
        # Alternative direct list-count calculation, independent of set-difference
        # code in the producer. It deliberately uses the delivered orientation.
        people = {s['player_id']: s for s in [p['game_state']['you'], *p['game_state']['others']]}
        for role in ['recipient', 'author']:
            player = row[role]
            give = offer['if_you_accept']['you_give' if role == 'recipient' else 'you_receive']
            receive = offer['if_you_accept']['you_receive' if role == 'recipient' else 'you_give']
            before = [d['space_key'] for d in people[player]['holdings']['owned']]
            after = [k for k in before if k not in give['properties']] + receive['properties']
            expected = []
            for group, keys in source['groups'].items():
                had = all(k in before for k in keys)
                has = all(k in after for k in keys)
                if has and not had:
                    expected.append(group)
            assert row[f'{role}_new_groups'] == sorted(expected)
            assert row[f'{role}_holdings_if_accepted'] == sorted(after)
    for kind, expected in source['flows'].items():
        assert sum(r['amount'] for r in flows if r['kind'] == kind) == expected
    assert len(data['concentration']) == source['counts']['decisions']
    assert sum(r['threads'] for r in data['games']) == len(threads)
    assert sum(r['settlements'] for r in data['games']) == result['counts']['settlements']
    for path, expected in result['source_hashes'].items():
        assert digest(ROOT / path) == expected


def main():
    import re
    board = json.loads((ROOT / 'contracts/data/board.json').read_text())
    groups = {}
    for s in board['spaces']:
        if s['kind'] == 'PROPERTY':
            groups.setdefault(s['group'], []).append(re.sub(r'[^A-Z0-9]+', '_', s['name'].upper()).strip('_'))
    source = {'counts': Counter(), 'decisions': {}, 'actions': {}, 'groups': groups, 'flows': Counter()}
    for run in game_dirs().values():
        for _, r in rows(run / 'decisions.jsonl'):
            if r['phase'] == 'decision_started':
                source['counts']['decisions'] += 1
                if r['decision_type'] == 'TRADE_RESPONSE_DECISION':
                    source['decisions'][r['decision_id']] = r
        for _, r in rows(run / 'actions.jsonl'):
            if r['decision_type'] == 'TRADE_RESPONSE_DECISION':
                source['actions'][r['decision_id']] = r
                source['counts']['responses'] += 1
        for _, e in rows(run / 'events.jsonl'):
            p, kind = e['payload'], e['type']
            for event_type, counter in [('TRADE_PROPOSED', 'threads'), ('TRADE_ACCEPTED', 'settlements'),
                                        ('TRADE_REJECTED', 'rejections'), ('TRADE_COUNTERED', 'counters')]:
                source['counts'][counter] += kind == event_type
            if kind == 'RENT_PAID': source['flows']['paid_rent'] += p['amount']
            if kind == 'PROPERTY_TRANSFERRED': source['flows']['trade_deed'] += 1
            if kind == 'PROPERTY_PURCHASED' and p['price'] == 0: source['flows']['estate_deed'] += 1
            if kind == 'CASH_CHANGED' and p['reason'] == 'TRADE_CASH' and p['delta'] > 0:
                source['flows']['trade_cash'] += p['delta']
            if kind == 'CASH_CHANGED' and p['reason'] == 'BANKRUPTCY_CASH' and p['delta'] < 0:
                source['flows']['estate_cash'] -= p['delta']
    data = load()
    validate(data, source)
    tests = [{'name': 'original canonical-source validation', 'pass': True}]
    mutations = [
        ('omitted offer', lambda d: d['offers'].pop()),
        ('duplicated offer', lambda d: d['offers'].append(copy.deepcopy(d['offers'][0]))),
        ('misattributed author', lambda d: d['offers'][0].update(author=d['offers'][0]['recipient'])),
        ('false completion', lambda d: d['offers'][0].update(recipient_new_groups=['GREEN'])),
        ('altered response', lambda d: d['offers'][0].update(response='accept_trade')),
        ('lost cash flow', lambda d: next(r for r in d['flows'] if r['kind']=='trade_cash').update(amount=99999)),
        ('invented count', lambda d: d['results']['counts'].update(threads=527)),
        ('wrong terminal', lambda d: d['threads'][0].update(terminal='TRADE_ACCEPTED')),
    ]
    for name, mutate in mutations:
        bad = copy.deepcopy(data)
        mutate(bad)
        try:
            validate(bad, source)
        except (AssertionError, KeyError):
            tests.append({'name': name, 'pass': True, 'corruption_rejected': True})
        else:
            raise AssertionError('Undetected mutation: ' + name)
    out = {'status': 'pass', 'tests': tests, 'canonical_counts': dict(source['counts']),
           'canonical_flow_totals': dict(source['flows']),
           'scope': 'Output/source consistency and mutations, not an independent semantic annotation or causal experiment.',
           'script_sha256': digest(Path(__file__))}
    (HERE / 'validation.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
