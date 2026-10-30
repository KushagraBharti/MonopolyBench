"""Record an explicitly supplied read boundary, never infer reading from parsing."""
import argparse
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
sys.path.insert(0, str(BASE))
from prepare_reading_chunks import decode
from prepare_game_reading import restore

p = argparse.ArgumentParser()
p.add_argument('game', type=int)
p.add_argument('last_page', type=int)
p.add_argument('last_complete_decision', type=int)
a = p.parse_args()
source = BASE / 'full_review' / f'game-{a.game:02d}'
manifest = json.loads((source / 'manifest.json').read_text())
data = restore(decode(json.loads((source / 'behavior.json').read_text())), json.loads((source / 'behavior_json_strings.json').read_text()))['packets']
target = OUT / f'game-{a.game:02d}'
target.mkdir(parents=True, exist_ok=True)
rows = []
for i, packet in enumerate(data[:a.last_complete_decision + 1]):
    attempts = []
    for attempt in packet['attempts']:
        calls = attempt.get('parsed_tool_calls') or []
        fields = []
        for call in calls:
            args = call.get('arguments', {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = {}
            fields.append({k: 'read' if k in args else 'not_returned' for k in ('public_message', 'private_thought')})
        channels = []
        raw = attempt.get('provider_response') or {}
        for choice in raw.get('choices', []):
            message = choice.get('message') or {}
            channels.append({'content': 'read' if message.get('content') else 'not_returned', 'reasoning': 'read' if message.get('reasoning') else 'not_returned', 'refusal': 'read' if message.get('refusal') else 'not_returned', 'details': [{'type': d.get('type'), 'status': 'unavailable_encrypted' if d.get('type') == 'reasoning.encrypted' else 'read'} for d in message.get('reasoning_details') or []]})
        attempts.append({'index': attempt['attempt_index_zero_based'], 'outcome': attempt['outcome'], 'condition': attempt['response_condition'], 'assistant_content': 'read' if attempt.get('assistant_content') else 'not_returned', 'tool_channels': fields, 'provider_channels': channels, 'reason': attempt.get('reason'), 'error_type': attempt.get('error_type'), 'error_message': attempt.get('error_message'), 'validation_errors': attempt['validation_errors'], 'prompt': 'read'})
    action = packet['applied_action']['action']
    rows.append({'decision_id': packet['decision_id'], 'turn': packet['turn_index'], 'player': packet['player_id'], 'applied_action': action, 'attempts': attempts, 'resolution': packet['resolution'], 'event_range': [packet['events'][0]['seq'], packet['events'][-1]['seq']], 'source': manifest['sources'][i], 'status': 'read_all_available_channels', 'observation_and_legal_menu': 'read'})
(target / 'coverage.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
progress = {'game': a.game, 'last_page_read': a.last_page, 'pages_total': len(manifest['pages']), 'complete_decisions_read': len(rows), 'decisions_total': len(data), 'attempts_read': sum(len(r['attempts']) for r in rows), 'next_page': a.last_page + 1, 'next_incomplete_decision': a.last_complete_decision + 1, 'complete': len(rows) == len(data)}
(target / 'progress.json').write_text(json.dumps(progress, indent=2) + '\n')
print(json.dumps(progress))
