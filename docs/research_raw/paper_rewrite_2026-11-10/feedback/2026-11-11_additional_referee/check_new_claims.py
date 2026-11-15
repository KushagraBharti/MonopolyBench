"""Read-only census of saved response metadata. No engine or model execution."""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]

def utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).isoformat() if ms else None

paths = sorted((ROOT / 'saved_games').glob('railway-research-*/game-??-*/run/decisions.jsonl'))
assert len(paths) == 20
refusals = Counter()
model_stats = defaultdict(Counter)
games = {}
sources = {}
for path in paths:
    sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    game = int(path.parents[1].name.split('-')[1])
    g = Counter()
    last_nonrefused = None
    end = 0
    refused_times = []
    for line in path.open():
        row = json.loads(line)
        if row['phase'] != 'decision_resolved':
            continue
        model = row['openrouter_model_id']
        model_stats[model]['decisions'] += 1
        model_stats[model]['recorded_medium_effort_decisions'] += (row.get('reasoning') or {}).get('effort') == 'medium'
        attempts = row.get('attempts', [])
        end = max(end, row.get('response_end_ms') or 0)
        if 'opus' in model:
            g['decisions'] += 1
            g['last_opus_response_ms'] = max(g['last_opus_response_ms'], row.get('response_end_ms') or 0)
            if attempts[0]['outcome'] == 'refused':
                g['first_refused'] += 1
                refused_times.append(attempts[0]['response_end_ms'])
            else:
                last_nonrefused = max(last_nonrefused or 0, attempts[0]['response_end_ms'])
        for attempt in attempts:
            s = model_stats[model]
            s['attempts'] += 1
            raw = attempt.get('raw_response') or {}
            choices = raw.get('choices') or []
            if attempt.get('outcome') == 'refused':
                s['refused'] += 1
                for choice in choices:
                    refusals[choice.get('message', {}).get('refusal') or '<absent>'] += 1
                if 'stop_details' in json.dumps(raw):
                    s['refusal_has_stop_details'] += 1
            usage = raw.get('usage') or {}
            if usage:
                s['usage_records'] += 1
                s['completion_max'] = max(s['completion_max'], usage.get('completion_tokens') or 0)
            value = (usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
            if value is not None:
                s['reasoning_reported_n'] += 1
                s['reasoning_sum'] += value
                s['reasoning_zero_n'] += value == 0
                s['reasoning_max'] = max(s['reasoning_max'], value)
            cost = usage.get('cost')
            upstream = (usage.get('cost_details') or {}).get('upstream_inference_cost')
            if cost is not None:
                s['usage_cost_sum'] += cost
                s['usage_cost_n'] += 1
            if upstream is not None:
                s['upstream_cost_sum'] += upstream
                s['upstream_cost_n'] += 1
            chosen = upstream if usage.get('is_byok') and upstream is not None else cost
            if chosen is not None:
                s['byok_aware_known_cost'] += chosen
                s['byok_aware_known_cost_n'] += 1
    g['last_nonrefused_first_utc'] = utc(last_nonrefused)
    g['last_game_response_utc'] = utc(end)
    g['last_opus_response_utc'] = utc(g.pop('last_opus_response_ms'))
    g['refused_first_after_last_nonrefused'] = sum(t > (last_nonrefused or 0) for t in refused_times)
    g['refusal_fraction'] = g['first_refused'] / g['decisions']
    games[str(game)] = dict(g)
for s in model_stats.values():
    s['mean_reported_reasoning_per_reported_record'] = s['reasoning_sum'] / s['reasoning_reported_n']
    s['zero_fraction_of_reported_reasoning'] = s['reasoning_zero_n'] / s['reasoning_reported_n']
result = {'scope': 'Saved response metadata only; no causal inference, engine execution, or invoice verification.',
          'sources': sources, 'refusal_strings': dict(refusals), 'per_model': dict(model_stats),
          'opus_by_game': games}
result['cost_field_totals'] = {key: sum(s[key] for s in model_stats.values())
                             for key in ['usage_cost_sum', 'upstream_cost_sum', 'byok_aware_known_cost']}
result['cost_field_totals']['adding_both_fields_not_a_spend_estimate'] = (
    result['cost_field_totals']['usage_cost_sum'] + result['cost_field_totals']['upstream_cost_sum'])
assert sum(s['decisions'] for s in model_stats.values()) == 6989
assert sum(s['attempts'] for s in model_stats.values()) == 8679
(HERE / 'checked_response_metadata.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k != 'sources'}, indent=2))
