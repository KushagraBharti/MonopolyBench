"""Review-only recount from canonical decisions and retained offline artifacts."""
import collections
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/research_raw/paper_agenda_revision_2026-10-29'
PACKETS = ROOT / 'docs/research_raw/paper_phase1_2026-10-28/astra/review_packets'
ERROR = 'Uneven intermediate building operation'
BUILD = 'build_houses_or_hotel'


def main():
    records, source_hashes, diagnostic = [], {}, collections.Counter()
    for game in range(1, 21):
        packet = next(PACKETS.glob(f'game-{game:02d}-part-001.jsonl'))
        with packet.open() as f:
            example = json.loads(next(f))
        canonical = ROOT / example['source_run'] / 'decisions.jsonl'
        starts = {}
        digest = hashlib.sha256()
        with canonical.open('rb') as f:
            for line_no, raw in enumerate(f, 1):
                digest.update(raw)
                x = json.loads(raw)
                if x['phase'] == 'decision_started':
                    starts[x['decision_id']] = x['prompt_payload']
                    continue
                if x['phase'] != 'decision_resolved':
                    continue
                attempts = []
                for index, a in enumerate(x['attempts']):
                    payload = a.get('prompt_payload') or starts[x['decision_id']]
                    notes = payload.get('action_state', {}).get('scenario', {}).get('notes', [])
                    parsed = a.get('parsed_tool_call') or {}
                    other = a.get('parsed_tool_calls') or []
                    named_build = parsed.get('name') == BUILD
                    plural_build = any(p.get('name') == BUILD for p in other)
                    errors = a.get('validation_errors') or []
                    uneven = any(ERROR in e for e in errors)
                    feedback = any(ERROR in n for n in notes)
                    diagnostic['plural_build_without_singular'] += plural_build and not named_build
                    diagnostic['construction_malformed'] += named_build and a['outcome'] == 'malformed'
                    diagnostic['initial_prompt_feedback'] += feedback and index == 0
                    attempts.append(dict(index=index, name=parsed.get('name'), uneven=uneven,
                                         feedback=feedback, outcome=a['outcome'],
                                         response_condition=a.get('response_condition'),
                                         validation_errors=errors))
                error_indices = [a['index'] for a in attempts if a['uneven']]
                records.append(dict(game=game, actor=x['player_id'], model=x['openrouter_model_id'],
                                    id=x['decision_id'], number=int(x['decision_id'].rsplit('-', 1)[1]),
                                    turn=x['turn_index'], attempts=attempts,
                                    construction=any(a['name'] == BUILD for a in attempts),
                                    error=bool(error_indices),
                                    feedback=any(a['feedback'] and any(i<a['index'] for i in error_indices)
                                                 for a in attempts),
                                    applied=x['final_action']['action'], fallback=x['fallback_used'],
                                    source=str(canonical.relative_to(ROOT)), line=line_no))
        source_hashes[str(canonical.relative_to(ROOT))] = digest.hexdigest()
    groups = collections.defaultdict(list)
    for x in records:
        groups[(x['game'], x['actor'])].append(x)
    episodes = []
    for key, rows in sorted(groups.items()):
        rows.sort(key=lambda x:x['number'])
        seen_feedback = False
        for i,x in enumerate(rows):
            if not x['error']:
                continue
            future = next((y for y in rows[i+1:] if y['construction']), None)
            first = x['feedback'] and not seen_feedback
            seen_feedback |= x['feedback']
            next_build = next((a for a in future['attempts'] if a['name']==BUILD), None) if future else None
            episodes.append(dict(game=key[0], actor=key[1], id=x['id'], model=x['model'],
                                 feedback=x['feedback'], first_feedback=first,
                                 next=future['id'] if future else None,
                                 repeat=next_build['uneven'] if next_build else None,
                                 next_first_outcome=next_build['outcome'] if next_build else None,
                                 same_turn=x['turn']==future['turn'] if future else None,
                                 repaired_here=x['applied']==BUILD,
                                 next_applied=future['applied'] if future else None,
                                 source=x['source'], line=x['line']))
    def stats(rows):
        observed=[x for x in rows if x['next']]
        return dict(episodes=len(rows), observed=len(observed), repeated=sum(bool(x['repeat']) for x in observed),
                    same_turn=sum(bool(x['same_turn']) for x in observed),
                    later_turn=len([x for x in observed if not x['same_turn']]),
                    later_turn_repeated=sum(bool(x['repeat']) for x in observed if not x['same_turn']),
                    repaired_here=sum(x['repaired_here'] for x in rows),
                    malformed_next=sum(x['next_first_outcome']=='malformed' for x in observed),
                    next_applied_build=sum(x['next_applied']==BUILD for x in observed))
    selections={'all':episodes,'feedback':[x for x in episodes if x['feedback']],
                'first_feedback':[x for x in episodes if x['first_feedback']]}
    recurrence=dict(decisions=len(records), construction=sum(x['construction'] for x in records),
                    diagnostic=dict(diagnostic), summary={k:stats(v) for k,v in selections.items()},
                    by_model={k:{m:stats([x for x in v if x['model']==m]) for m in sorted({x['model'] for x in v})}
                              for k,v in selections.items()}, episodes=episodes, source_hashes=source_hashes)
    (OUT/'canonical_recurrence.json').write_text(json.dumps(recurrence,indent=2)+'\n')
    root_rows={x['decision_id']:x for x in map(json.loads,(BASE/'integration/recurrence_rows.jsonl').open())}
    mismatches=[]
    for x in records:
        y=root_rows[x['id']]
        pairs=[('construction',x['construction'],y['construction_submission']),('error',x['error'],y['uneven_error']),
               ('feedback',x['feedback'],y['corrective_feedback_delivered']),('applied',x['applied'],y['applied_action'])]
        mismatches.extend({'id':x['id'],'field':k,'canonical':a,'packet':b} for k,a,b in pairs if a!=b)
    (OUT/'packet_comparison.json').write_text(json.dumps({'decisions':len(records),'mismatches':mismatches},indent=2)+'\n')
    print(json.dumps({'canonical':recurrence['summary'],'diagnostic':recurrence['diagnostic'],'packet_mismatches':mismatches},indent=2))


if __name__=='__main__':
    main()
