"""Transcribe channel inventory only for a manually confirmed read prefix.

This tool does not read semantically, select candidates, or assign behavioral
labels. The reviewer must supply the last completely read decision index.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent.parent
ROOT = PHASE.parents[2]
sys.path.insert(0, str(PHASE))
from prepare_reading_chunks import decode

parser = argparse.ArgumentParser()
parser.add_argument('--game', type=int, required=True)
parser.add_argument('--through', type=int, required=True)
args = parser.parse_args()
folder = PHASE / 'full_review' / f'game-{args.game:02d}'
manifest = json.loads((folder / 'manifest.json').read_text())
raw = (folder / 'behavior.json').read_text()
packets = decode(json.loads(raw))['packets']
target = HERE / f'game-{args.game:02d}'
target.mkdir(exist_ok=True)

def channels(value, path=''):
    out = []
    if isinstance(value, dict):
        for key, item in value.items():
            p = path + '/' + key
            if key == 'signature' or key == 'data' and value.get('type') == 'reasoning.encrypted':
                out.append({'path': p, 'status': 'opaque_unavailable'})
            elif key in {'content', 'reasoning', 'text', 'summary', 'refusal', 'public_message', 'private_thought', 'assistant_content'}:
                state = 'not_returned' if item is None else 'read_empty' if item == '' else 'read'
                out.append({'path': p, 'status': state})
                if isinstance(item, (dict, list)):
                    out.extend(channels(item, p))
            else:
                out.extend(channels(item, p))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            out.extend(channels(item, path + '/' + str(i)))
    return out

offset = len('{"packets":[\n')
encoded = json.loads(raw)['packets']
rows = []
for i, (p, ep, source) in enumerate(zip(packets, encoded, manifest['sources'])):
    size = len(json.dumps(ep, ensure_ascii=False, separators=(',', ':')))
    pages = [offset // 24000 + 1, (offset + size - 1) // 24000 + 1]
    offset += size + 2
    if i > args.through:
        continue
    line = (ROOT / source['packet']).read_text().splitlines()[source['packet_line'] - 1]
    assert hashlib.sha256(line.encode()).hexdigest() == source['source_line_sha256']
    assert json.loads(line)['decision_id'] == p['decision_id']
    action = p['applied_action']['action']
    attempts = []
    for a in p['attempts']:
        inventory = channels(a)
        attempts.append({'index': a['attempt_index_zero_based'], 'outcome': a['outcome'],
                         'condition': a['response_condition'], 'validation_errors': a['validation_errors'],
                         'channels': inventory, 'prompt_and_tool_calls': 'read'})
    rows.append({'decision_id': p['decision_id'], 'turn': p['turn_index'], 'player': p['player_id'],
                 'status': 'read_complete', 'applied_action': action['action'], 'args': action['args'],
                 'applied_public': 'read' if action.get('public_message') else 'read_empty',
                 'applied_private': 'read' if 'private_thought' in action else 'not_returned',
                 'observation_and_legal_menu': 'read', 'attempts': attempts,
                 'events': [p['events'][0]['seq'], p['events'][-1]['seq']],
                 'pages': pages, 'source': source})
(target / 'coverage.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
print(json.dumps({'game': args.game, 'manually_confirmed_decisions': len(rows),
                  'attempts': sum(len(r['attempts']) for r in rows), 'last_decision': rows[-1]['decision_id']}))
