"""Write an honest checkpoint for the first ten partially inspected records."""
import json
from pathlib import Path

root = Path('docs/research_raw/paper_phase2_2026-10-28')
out = root / 'reviewers/terra_parallel_b'
ledger = Path('docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl')
rows = [json.loads(line) for line in ledger.open()]
assigned = [r for r in rows if 7 <= r['game'] <= 13]
notes = [
    'p1 bought Vermont for $100; cited early investment and trade leverage.',
    'p1 ended turn; doubled roll led to a further turn.',
    'p1 bought St. James for $180, citing orange and jail exit probabilities.',
    'p1 ended turn before other players had purchased property.',
    'p2 ended while holding no assets; subsequent $14 rent to p1.',
    'p2 ended with $1,486 after rent; recorded preference to conserve cash.',
    'p3 bought St. Charles for $140 after refusal and public-only retry.',
    'p3 ended after refusal and public-only retry.',
    'p4 ended without assets; recorded preference to conserve cash.',
    'p1 bought Indiana for $220, recording $1,234 pre-purchase cash.',
]
coverage = []
for i, r in enumerate(assigned[:10]):
    coverage.append({
        'decision_id': r['decision_id'], 'game': 7, 'reviewer': 'Terra xhigh',
        'status': 'partial', 'attempts_reviewed': [0, 1] if i in (6, 7) else [0],
        'channels': {'observation_and_menu': 'partial', 'applied_action': 'reviewed',
                     'events': 'partial', 'public': 'reviewed',
                     'private': 'unavailable' if i in (6, 7) else 'reviewed',
                     'provider': 'partial'},
        'note': notes[i], 'candidate_ids': [], 'source_packet': r['packet'],
        'source_packet_line': r['packet_line'],
    })
(out / 'coverage.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in coverage))
(out / 'progress.json').write_text(json.dumps({
    'reviewer': 'Terra xhigh', 'expected_count': len(assigned), 'reviewed_count': 0,
    'partial_ids': [r['decision_id'] for r in assigned[:10]],
    'remaining_ids': [r['decision_id'] for r in assigned[10:]],
    'remaining_work': 'Complete every partial record, then semantically review every remaining record and terminal events; write game narratives and ranked shortlist.',
}, indent=2) + '\n')
