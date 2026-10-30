"""Finite, read-only audit of saved decisions, requests, and formatter exposure.

Writes only beside this script. Does not import the reviewed audit or peer reports.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.dont_write_bytecode = True
for package in ('engine', 'arena', 'telemetry'):
    sys.path.insert(0, str(ROOT / 'python/packages' / package / 'src'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def records(path):
    return [(i, json.loads(line)) for i, line in enumerate(path.open(), 1)]


def named(content):
    if not content:
        return None, 'empty'
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        names = re.findall(r'"name"\s*:\s*"([a-z_]+)"', content)
        return (names[0], 'malformed_explicit_name') if names and len(set(names)) == 1 else (None, 'unparsed')
    if isinstance(obj, dict) and isinstance(obj.get('name'), str):
        return obj['name'], 'json_name'
    return None, 'no_named_call'


def nested_names(obj, path='$'):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('name', 'action', 'tool_name', 'function_name') and isinstance(v, str):
                found.append({'path': path + '.' + k, 'value': v})
            found.extend(nested_names(v, path + '.' + k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(nested_names(v, f'{path}[{i}]'))
    return found


def equal_paths(obj, target, path='$'):
    hits = []
    if obj == target:
        hits.append(path)
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits.extend(equal_paths(v, target, path + '.' + k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(equal_paths(v, target, f'{path}[{i}]'))
    return hits


def main():
    manifest_path = ROOT / 'docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json'
    manifest = read(manifest_path)
    audit_path = ROOT / 'docs/research_raw/paper_adversarial_2026-10-29/conditions_audit.json'
    reviewed = read(audit_path)
    aliases = {'openai/gpt-6.1-sol': 'Sol', 'google/gemini-4-argon': 'Gemini',
               'anthropic/claude-opus-5.5': 'Opus', 'x-ai/grok-4.7': 'Grok'}
    focal = {(c['game'], c['decision_id']) for c in reviewed['chronology_conditions']}
    counts = defaultdict(Counter)
    parser_counts = defaultdict(Counter)
    denominators = defaultdict(Counter)
    end_records, conflicts, focal_records, bad_rows, outside_parser = [], [], [], [], []
    issues = []
    initial_timeline_checks = Counter()
    hashes = {str(manifest_path.relative_to(ROOT)): sha(manifest_path.read_bytes()),
              str(audit_path.relative_to(ROOT)): sha(audit_path.read_bytes())}
    historical = {}
    for game in manifest['games']:
        g = game['game']
        run = ROOT / game['run']
        for leaf in ('events.jsonl', 'actions.jsonl', 'decisions.jsonl'):
            hashes[str((run / leaf).relative_to(ROOT))] = sha((run / leaf).read_bytes())
        events = records(run / 'events.jsonl')
        event_by_id = {e['event_id']: e for _, e in events}
        actions = {r['decision_id']: (n, r) for n, r in records(run / 'actions.jsonl')}
        starts = {}
        # Load the actual historical formatter at each run's recorded source SHA.
        # Its imported current helper is not used by PromptMemory.update.
        source_sha = game['source_sha']
        if source_sha not in historical:
            code = subprocess.check_output(['git', 'show', source_sha + ':python/packages/arena/src/monopoly_arena/prompting.py'], cwd=ROOT)
            module_name = 'monopoly_arena.historical_prompting_' + source_sha
            module = types.ModuleType(module_name)
            module.__package__ = 'monopoly_arena'
            sys.modules[module_name] = module
            namespace = module.__dict__
            exec(compile(code, source_sha + ':prompting.py', 'exec'), namespace)
            historical[source_sha] = namespace
            hashes[source_sha + ':python/packages/arena/src/monopoly_arena/prompting.py'] = sha(code)
            for leaf in ('openrouter_client.py', 'decision_resolver.py'):
                original = subprocess.check_output(['git', 'show', source_sha + ':python/packages/arena/src/monopoly_arena/' + leaf], cwd=ROOT)
                hashes[source_sha + ':python/packages/arena/src/monopoly_arena/' + leaf] = sha(original)
        memory = historical[source_sha]['PromptMemory']()
        bad = []
        requested_memory = {}
        for event_line, event in events:
            memory.update(event)
            p = event.get('payload', {})
            actor = event.get('actor', {}).get('player_id')
            if event['type'] == 'LLM_DECISION_REQUESTED':
                requested_memory[p['decision_id']] = {'seq': event['seq'], 'timeline': json.loads(json.dumps(memory.snapshot_for_player(p['player_id'])['public_timeline_last_20']))}
            defect = None
            if event['type'] == 'TRADE_COUNTERED' and actor == p.get('counterparty_player_id'):
                defect = 'counter_self_partner'
            if event['type'] in ('TRADE_ACCEPTED', 'TRADE_REJECTED') and actor == p.get('initiator_player_id'):
                defect = 'accepted_reversed' if event['type'] == 'TRADE_ACCEPTED' else 'rejected_offer_misattributed'
            if defect:
                row = memory.snapshot_for_player(actor)['public_timeline_last_20'][-1]
                assert row['event_type'] == event['type']
                item = {'game': g, 'event_line': event_line, 'seq': event['seq'], 'event_id': event['event_id'],
                        'defect': defect, 'row': row, 'actor': actor, 'canonical_payload': p}
                bad.append(item)
                bad_rows.append(item)
        for line_no, row in records(run / 'decisions.jsonl'):
            did = row['decision_id']
            if row['phase'] == 'decision_started':
                starts[did] = row
                continue
            if row['phase'] != 'decision_resolved':
                continue
            model = aliases[row['openrouter_model_id']]
            base = {'game': g, 'decision_id': did, 'model': model, 'decision_line': line_no,
                    'decision_path': str((run / 'decisions.jsonl').relative_to(ROOT))}
            den = denominators[model]
            den['resolved_decisions'] += 1
            den['attempts'] += len(row['attempts'])
            valid = [i for i, a in enumerate(row['attempts']) if a['outcome'] == 'valid']
            if len(valid) > 1:
                issues.append({**base, 'issue': 'multiple_valid'})
            selected = valid[-1] if valid and not row['fallback_used'] else None
            if selected is None and not row['fallback_used']:
                issues.append({**base, 'issue': 'no_valid_without_fallback'})
            if selected is not None:
                den['selected_attempts'] += 1
                den['selected_model:' + row['attempts'][selected]['requested_model']] += 1
                den['selected_condition:' + row['attempts'][selected]['response_condition']] += 1
                assert selected == len(row['attempts']) - 1
                assert row['attempts'][selected]['parsed_tool_call']['name'] == row['final_action']['action']
            else:
                den['engine_default_decisions'] += 1
            assert row['applied'] is True
            action_line, logged = actions[did]
            if logged['decision_meta']['valid'] is not True:
                den['logged_action_meta_invalid'] += 1
                assert row['fallback_used']
            assert logged['action'] == row['final_action']
            start = starts[did]
            initial_timeline_checks['checked'] += 1
            if start['prompt_payload']['game_state']['memory']['public_timeline_last_20'] == requested_memory[did]['timeline']:
                initial_timeline_checks['matches_historical_formatter_at_request_event'] += 1
            else:
                issues.append({**base, 'issue': 'initial_timeline_differs_from_historical_reconstruction'})
            selected_conflict = False
            selected_form = 'none'
            selected_name = None
            for index, attempt in enumerate(row['attempts']):
                name, shape = named(attempt.get('assistant_content'))
                tool = attempt.get('parsed_tool_call')
                is_selected = index == selected
                parser_counts[model][('selected:' if is_selected else 'unselected:') + shape] += 1
                if is_selected:
                    selected_form, selected_name = shape, name
                    selected_conflict = bool(name and tool and name != tool['name'])
                content = attempt.get('assistant_content')
                if name is None and content:
                    try:
                        nested = nested_names(json.loads(content))
                    except json.JSONDecodeError:
                        nested = []
                    if nested:
                        outside_parser.append({**base, 'attempt_index': index, 'selected': is_selected,
                                               'form': shape, 'nested_names': nested, 'tool': tool})
                if not name or not tool or name == tool['name']:
                    continue
                path = run.parent / 'cloud/calls' / (attempt['call_id'] + '.response.json')
                saved = read(path)
                body, req = json.loads(saved['response_text']), json.loads(saved['request_payload_raw'])
                message = body['choices'][0]['message']
                wire_tool = message['tool_calls'][0]['function']
                assert req.get('stream') is not True
                assert len(body['choices']) == 1 and len(message['tool_calls']) == 1
                assert body == saved['response_json']
                assert body['choices'] == saved['response_json']['choices'] == attempt['raw_response']['choices']
                assert {k for k in set(body) | set(attempt['raw_response']) if body.get(k) != attempt['raw_response'].get(k)} == {'openrouter_generation'}
                assert message.get('content') == content
                assert wire_tool['name'] == tool['name'] and wire_tool['arguments'] == tool['arguments']
                assert saved['ok'] is True and saved['status_code'] == 200
                conflicts.append({**base, 'attempt_index': index, 'selected': is_selected, 'form': shape,
                                  'content_name': name, 'tool_name': tool['name'], 'outcome': attempt['outcome'],
                                  'response_path': str(path.relative_to(ROOT)), 'response_sha256': sha(path.read_bytes()),
                                  'requested_model': req['model'], 'returned_model': body['model'],
                                  'provider': body.get('provider'), 'stream_field': req.get('stream'),
                                  'raw_vs_saved_differing_top_keys': [k for k in set(body) | set(saved['response_json']) if body.get(k) != saved['response_json'].get(k)],
                                  'raw_vs_attempt_differing_top_keys': [k for k in set(body) | set(attempt['raw_response']) if body.get(k) != attempt['raw_response'].get(k)],
                                  'response_is_raw_nonstreamed_json': True, 'action_line': action_line})
            if 'build_houses_or_hotel' in start['prompt_payload']['action_state'].get('available_actions', []):
                counts[model]['construction_tool_listed'] += 1
                if row['final_action']['action'] == 'end_turn':
                    emitted = [event_by_id[eid] for eid in row['emitted_event_ids']]
                    assert any(e['type'] == 'TURN_ENDED' and e['turn_index'] == row['turn_index'] for e in emitted)
                    category = 'engine_default' if row['fallback_used'] else 'received_name_conflict' if selected_conflict else 'no_detected_name_conflict'
                    counts[model]['applied_end'] += 1
                    counts[model][category] += 1
                    end_records.append({**base, 'action_line': action_line, 'category': category, 'selected_attempt': selected,
                                        'turn_ended_event_ids': [e['event_id'] for e in emitted if e['type'] == 'TURN_ENDED'],
                                        'content_form': selected_form, 'content_name': selected_name,
                                        'selected_requested_model': row['attempts'][selected]['requested_model'] if selected is not None else None,
                                        'selected_condition': row['attempts'][selected]['response_condition'] if selected is not None else None,
                                        'fallback_reason': row['fallback_reason']})
            if (g, did) in focal:
                selected_attempt = row['attempts'][selected] if selected is not None else None
                payload = (selected_attempt.get('prompt_payload') if selected_attempt else None) or start['prompt_payload']
                timeline = payload['game_state']['memory']['public_timeline_last_20']
                matches = []
                for b in bad:
                    paths = equal_paths(payload, b['row'])
                    if paths:
                        assert b['row'] in timeline
                        assert b['seq'] < requested_memory[did]['seq']
                        matches.append({'seq': b['seq'], 'defect': b['defect'], 'paths': paths})
                initial_timeline = start['prompt_payload']['game_state']['memory']['public_timeline_last_20']
                transport_path = run.parent / 'cloud/calls' / (selected_attempt['call_id'] + '.response.json') if selected_attempt else None
                request_payload_equal = None
                if transport_path:
                    saved = read(transport_path)
                    request = json.loads(saved['request_payload_raw'])
                    user_messages = [m['content'] for m in request['messages'] if m['role'] == 'user']
                    assert len(user_messages) == 1
                    request_payload_equal = json.loads(user_messages[0]) == payload
                    assert request_payload_equal
                focal_records.append({**base, 'selected_attempt': selected,
                                      'selected_requested_model': selected_attempt['requested_model'] if selected_attempt else None,
                                      'selected_condition': selected_attempt['response_condition'] if selected_attempt else None,
                                      'applied_action': row['final_action']['action'], 'timeline_length': len(timeline),
                                      'request_event_seq': requested_memory[did]['seq'],
                                      'initial_timeline_length': len(initial_timeline), 'timeline_equal_initial': timeline == initial_timeline,
                                      'request_payload_equals_selected_payload': request_payload_equal,
                                      'response_path': str(transport_path.relative_to(ROOT)) if transport_path else None,
                                      'response_sha256': sha(transport_path.read_bytes()) if transport_path else None,
                                      'matches': matches})
    expected = {m: dict(c) for m, c in counts.items()}
    assert expected == reviewed['counts']
    ours = {(r['game'], r['decision_id'], r['attempt_index']) for r in conflicts if r['selected'] and r['model'] == 'Grok'}
    theirs = {(r['game'], r['decision_id'], r['attempt_index']) for r in reviewed['selected_grok_conflicts']}
    assert ours == theirs
    for r in focal_records:
        prior = next(c for c in reviewed['chronology_conditions'] if (c['game'], c['decision_id']) == (r['game'], r['decision_id']))
        assert {(m['seq'], m['defect']) for m in r['matches']} == {(m['seq'], m['defect']) for m in prior['matched_formatter_rows']}
    result = {'counts': expected, 'denominators': dict(denominators), 'parser_counts': dict(parser_counts),
              'conflict_scope': dict(Counter(('selected_' if r['selected'] else 'unselected_') + r['form'] for r in conflicts)),
              'conflicts': conflicts, 'end_records': end_records, 'focal_records': focal_records,
              'independently_derived_bad_rows': bad_rows, 'outside_top_level_parser': outside_parser,
              'source_hashes': hashes, 'issues': issues,
              'initial_timeline_checks': dict(initial_timeline_checks),
              'script_sha256': sha(Path(__file__).read_bytes())}
    (HERE / 'independent_results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('counts', 'denominators', 'parser_counts', 'conflict_scope', 'issues')}, indent=2))
    print('outside_top_level_parser', len(outside_parser), 'focal_records', len(focal_records), 'bad_rows', len(bad_rows))


if __name__ == '__main__':
    main()
