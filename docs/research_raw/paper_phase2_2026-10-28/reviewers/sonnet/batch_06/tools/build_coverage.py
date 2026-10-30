#!/usr/bin/env python3
"""Builds coverage.jsonl + progress.json from notes.jsonl (reviewer-written notes) and structural packet data.
Only decisions that have a reviewer note are emitted as reviewed.  Channel statuses are derived from what the
packet actually contains; they do not replace reading."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reader
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'claude-sonnet-5-5/xhigh'
units = reader.load_units()
manifest_ids = [r['decision_id'] for u, r in units]
notes = {}
fn = os.path.join(base, 'notes.jsonl')
if os.path.exists(fn):
    for l in open(fn):
        d = json.loads(l); notes[d['idx']] = d
rows = []
for gi, (u, r) in enumerate(units):
    if gi not in notes:
        continue
    aa = r['applied_action_record']['action']
    pub, pri = aa.get('public_message'), aa.get('private_thought')
    readable, opaque_only, per = [], [], []
    for a in r['attempts']:
        raw = a['raw_response']
        m = raw['choices'][0]['message'] if raw and raw.get('choices') else {}
        rd = m.get('reasoning_details') or []
        has = bool(m.get('reasoning') or m.get('content') or any(x.get('type') in ('reasoning.text', 'reasoning.summary') and (x.get('text') or x.get('summary')) for x in rd))
        per.append(has)
    prov = 'reviewed' if all(per) else ('unavailable' if not any(per) else 'partial')
    detail = {}
    detail['public'] = 'empty' if not pub else 'text'
    detail['private'] = 'absent' if pri is None else ('empty' if pri == '' else 'text')
    detail['provider_per_attempt_readable'] = per
    cond = [a['response_condition'] for a in r['attempts']]
    detail['attempt_conditions'] = cond
    detail['attempt_outcomes'] = [a['outcome'] for a in r['attempts']]
    rows.append({
        'decision_id': r['decision_id'], 'game': r['game'], 'reviewer': REV, 'status': 'reviewed',
        'player_id': r['player_id'], 'model': r['model'], 'decision_type': r['decision_type'], 'turn_index': r['turn_index'],
        'attempts_reviewed': [a['attempt_index_zero_based'] for a in r['attempts']],
        'channels': {'observation_and_menu': 'reviewed', 'applied_action': 'reviewed', 'events': 'reviewed',
                     'public': 'reviewed', 'private': 'reviewed' if pri else 'unavailable', 'provider': prov},
        'channel_detail': detail,
        'note': notes[gi]['note'], 'candidate_ids': notes[gi]['candidate_ids'],
        'source_packet': u['packet'], 'source_packet_line': u['packet_line'], 'manifest_index': gi,
        'event_segment': [r['source_lines']['event_segment_start'], r['source_lines']['event_segment_end']],
    })
with open(os.path.join(base, 'coverage.jsonl'), 'w') as f:
    for x in rows:
        f.write(json.dumps(x, ensure_ascii=False) + '\n')
reviewed_ids = [x['decision_id'] for x in rows]
remaining = [d for i, d in enumerate(manifest_ids) if i not in notes]
prog = {
    'reviewer': REV, 'reviewer_model': 'claude-sonnet-5-5', 'effort': 'xhigh', 'batch': reader.BATCH, 'games': sorted({r['game'] for u, r in units}),
    'expected_decisions': len(manifest_ids), 'reviewed_count': len(reviewed_ids), 'partial_count': 0,
    'remaining_count': len(remaining), 'reviewed_idx_range_contiguous_through': (min(set(range(len(manifest_ids))) - set(notes)) - 1) if remaining else len(manifest_ids) - 1,
    'remaining_decision_ids': remaining, 'partial_decision_ids': [],
    'status': 'complete' if not remaining else 'in_progress',
    'remaining_work': ('none' if not remaining else 'chronological reading continues from first remaining idx; shortlist.md, game_narratives.md and final candidate polish pending until all decisions read'),
}
json.dump(prog, open(os.path.join(base, 'progress.json'), 'w'), indent=1)
print('reviewed', len(reviewed_ids), 'remaining', len(remaining))
