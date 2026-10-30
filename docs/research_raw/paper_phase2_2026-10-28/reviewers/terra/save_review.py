#!/usr/bin/env python3
"""Save manually read, contiguous decisions; does not perform semantic review."""
import json
import sys
from pathlib import Path

phase = Path(__file__).resolve().parents[2]
root = phase.parents[2]
batch, first, last = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
note = sys.argv[4]
units = json.loads((phase / 'batches' / f'{batch}.json').read_text())['units']
directory = Path(__file__).parent / batch
progress_path = directory / 'progress.json'
progress = json.loads(progress_path.read_text())
with (directory / 'coverage.jsonl').open('a') as coverage:
    for index in range(first, last + 1):
        unit = units[index]
        assert progress['remaining_ids'][0] == unit['decision_id']
        rec = json.loads((root / unit['packet']).read_text().splitlines()[unit['packet_line'] - 1])
        row = {'decision_id': unit['decision_id'], 'game': unit['game'], 'reviewer': 'gpt-6.1-terra/xhigh', 'status': 'reviewed',
               'attempts_reviewed': [a['attempt_index_zero_based'] for a in rec['attempts']],
               'channels': {k: 'reviewed' for k in ['observation_and_menu', 'applied_action', 'events', 'public', 'private', 'provider']},
               'note': note, 'candidate_ids': [], 'source_packet': unit['packet'], 'source_packet_line': unit['packet_line']}
        coverage.write(json.dumps(row) + '\n')
        progress['reviewed_ids'].append(progress['remaining_ids'].pop(0))
        progress['reviewed'] += 1
        progress['remaining'] -= 1
progress['remaining_work'] = f'Continue {batch} index {last + 1}.'
progress_path.write_text(json.dumps(progress, indent=2) + '\n')
