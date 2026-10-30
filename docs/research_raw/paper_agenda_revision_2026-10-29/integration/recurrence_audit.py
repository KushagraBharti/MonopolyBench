"""Observe construction-error recurrence; never modifies games or runs models."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACKETS = ROOT / 'docs/research_raw/paper_phase1_2026-10-28/astra/review_packets'
ERROR = 'Uneven intermediate building operation'
BUILD = 'build_houses_or_hotel'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(unit, source):
    attempts = []
    for item in unit['attempts']:
        parsed = item.get('parsed_tool_call') or {}
        prompt = item.get('prompt') or {}
        payload = prompt.get('payload') or {}
        notes = payload.get('action_state', {}).get('scenario', {}).get('notes', [])
        attempts.append({
            'index': item['attempt_index_zero_based'],
            'name': parsed.get('name'), 'outcome': item.get('outcome'),
            'condition': item.get('response_condition'),
            'uneven': any(ERROR in str(e) for e in item.get('validation_errors', [])),
            'feedback_delivered': any(ERROR in str(n) for n in notes),
            'validation_errors': item.get('validation_errors', []),
            'feedback_notes': notes if any(ERROR in str(n) for n in notes) else [],
        })
    errors = [a['index'] for a in attempts if a['uneven']]
    delivered = any(a['feedback_delivered'] and any(i < a['index'] for i in errors) for a in attempts)
    return {
        'game': unit['game'], 'player_id': unit['player_id'], 'model': unit['model'],
        'decision_id': unit['decision_id'], 'decision_index': int(unit['decision_id'].rsplit('-', 1)[1]),
        'turn_index': unit['turn_index'], 'source': source,
        'applied_action': unit['applied_action_record']['action']['action'],
        'fallback': unit['resolution'].get('fallback_used', False),
        'attempts': attempts, 'construction_submission': any(a['name'] == BUILD for a in attempts),
        'uneven_error': bool(errors), 'corrective_feedback_delivered': delivered,
    }


def analyze(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['game'], row['player_id'])].append(row)
    episodes = []
    for key, actor_rows in sorted(groups.items()):
        actor_rows.sort(key=lambda r: r['decision_index'])
        first_feedback = True
        for i, row in enumerate(actor_rows):
            if not row['uneven_error']:
                continue
            future = [(j, r) for j, r in enumerate(actor_rows[i+1:], i+1) if r['construction_submission']]
            next_j, nxt = future[0] if future else (None, None)
            first = row['corrective_feedback_delivered'] and first_feedback
            if first:
                first_feedback = False
            next_builds = [a for a in nxt['attempts'] if a['name'] == BUILD] if nxt else []
            episodes.append({
                'game': key[0], 'player_id': key[1], 'model': row['model'],
                'decision_id': row['decision_id'], 'source': row['source'],
                'delivered_feedback': row['corrective_feedback_delivered'],
                'first_feedback_episode_in_player_game': first,
                'applied_construction_here': row['applied_action'] == BUILD,
                'next_decision_id': nxt['decision_id'] if nxt else None,
                'next_source': nxt['source'] if nxt else None,
                'next_same_global_turn': nxt['turn_index'] == row['turn_index'] if nxt else None,
                'actor_decisions_to_next_submission': next_j-i if nxt else None,
                'next_first_submission_uneven': next_builds[0]['uneven'] if nxt else None,
                'next_any_submission_uneven': nxt['uneven_error'] if nxt else None,
                'next_applied_construction': nxt['applied_action'] == BUILD if nxt else None,
                'censored_no_later_submission': nxt is None,
            })
    return episodes


def summarize(episodes):
    def stats(items):
        observed = [x for x in items if x['next_decision_id'] is not None]
        return {
            'episodes': len(items), 'next_submission_observed': len(observed),
            'no_later_submission': len(items)-len(observed),
            'next_first_repeats': sum(x['next_first_submission_uneven'] for x in observed),
            'next_any_repeats': sum(x['next_any_submission_uneven'] for x in observed),
            'next_same_turn': sum(x['next_same_global_turn'] for x in observed),
            'next_later_turn': sum(not x['next_same_global_turn'] for x in observed),
            'next_later_turn_repeats': sum(x['next_first_submission_uneven'] for x in observed if not x['next_same_global_turn']),
            'next_applied_build': sum(x['next_applied_construction'] for x in observed),
            'player_games': len({(x['game'], x['player_id']) for x in items}),
        }
    output = {}
    selections = {
        'all_uneven': episodes,
        'delivered_feedback': [x for x in episodes if x['delivered_feedback']],
        'feedback_and_applied_build': [x for x in episodes if x['delivered_feedback'] and x['applied_construction_here']],
        'feedback_without_applied_build': [x for x in episodes if x['delivered_feedback'] and not x['applied_construction_here']],
        'first_delivered_per_player_game': [x for x in episodes if x['first_feedback_episode_in_player_game']],
    }
    for name, items in selections.items():
        output[name] = {'total': stats(items), 'by_model': {m: stats([x for x in items if x['model']==m]) for m in sorted({x['model'] for x in episodes})}}
    return output


def main():
    rows, hashes = [], {}
    for path in sorted(PACKETS.glob('game-*-part-*.jsonl')):
        data = path.read_bytes()
        hashes[str(path.relative_to(ROOT))] = digest(data)
        for number, line in enumerate(data.splitlines(), 1):
            if line.strip():
                rows.append(compact(json.loads(line), {'packet': str(path.relative_to(ROOT)), 'line': number, 'line_sha256': digest(line)}))
    assert len(rows) == len({x['decision_id'] for x in rows}) == 6989
    assert len({x['game'] for x in rows}) == 20
    actual = Counter(x['model'] for x in rows if x['uneven_error'])
    assert sorted(actual.values()) == [5, 19, 29, 61], actual
    episodes = analyze(rows)
    result = {
        'protocol_sha256': digest((HERE/'recurrence_protocol.md').read_bytes()),
        'script_sha256': digest(Path(__file__).read_bytes()), 'source_hashes': hashes,
        'decisions': len(rows), 'construction_submission_decisions': sum(x['construction_submission'] for x in rows),
        'uneven_error_decisions': len(episodes), 'summary': summarize(episodes), 'episodes': episodes,
        'scope': 'Observed next construction submission within the same player-game. No causal feedback, durable learning, optimality, or across-game training claim.',
    }
    (HERE/'recurrence_rows.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
    (HERE/'recurrence_results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['decisions','construction_submission_decisions','uneven_error_decisions','summary']},indent=2))


if __name__ == '__main__':
    main()
