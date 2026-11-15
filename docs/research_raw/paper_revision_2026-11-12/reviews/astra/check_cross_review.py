"""Read-only checks of new peer claims. No engine imports or evaluations."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROUND = HERE.parents[1]
REPO = next(p for p in HERE.parents if (p / 'saved_games').is_dir())
DATA = ROUND / 'full_drafts/astra/data'
episodes = json.loads((DATA / 'liquidation_episodes.json').read_text())
games = json.loads((DATA / 'game_map.json').read_text())
targets = {(e['game'], e['first_decision']): e for e in episodes}
rows = []
channels = {}
sources = {}
g15 = []
for game, run in games.items():
    game = int(game)
    path = REPO / run / 'decisions.jsonl'
    sources[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open() as f:
        for line in f:
            rec = json.loads(line)
            if rec['phase'] != 'decision_resolved':
                continue
            decision = int(rec['decision_id'].rsplit('-', 1)[1])
            model = rec['openrouter_model_id']
            c = channels.setdefault(model, Counter())
            c['decisions'] += 1
            action = rec['final_action']
            attempts = rec['attempts']
            recovery = any(a.get('response_condition') == 'same_model_without_private_thought' for a in attempts)
            c['recovery_decisions'] += recovery
            if recovery:
                c['recovery_with_applied_note'] += bool(action.get('private_thought'))
                c['recovery_with_model_note'] += bool(action.get('private_thought')) and not rec['fallback_used']
                c['recovery_fallback'] += bool(rec['fallback_used'])
            valid = [a for a in attempts if a.get('outcome') == 'valid']
            if valid:
                a = valid[-1]
                content = a.get('assistant_content') or ''
                named = re.search(r'"name"\s*:\s*"([a-z_]+)"', content)
                if named:
                    c['named_action_regex'] += 1
                    c['conflicting_named_action_regex'] += named[1] != action['action']
            if (game, decision) in targets:
                e = targets[(game, decision)]
                assert action['action'] == e['actions'][0]
                if e['outcome'] == 'paid' or (game, decision) in {(12, 190), (12, 249), (17, 234)}:
                    cls = 'payable'
                elif e['upper_bound'] < e['debt']:
                    cls = 'above_bound'
                else:
                    cls = 'menu_restricted'
                rows.append({'game': game, 'decision': decision, 'model': model, 'class': cls,
                             'first_action': action['action'], 'fallback': rec['fallback_used'],
                             'outcome': e['outcome'], 'debt': e['debt'], 'bound': e['upper_bound']})
            if game == 15 and 168 <= decision <= 175:
                g15.append({'decision': decision, 'action': action})
assert len(rows) == 188
summary = {}
for cls in ['payable', 'above_bound', 'menu_restricted']:
    selected = [r for r in rows if r['class'] == cls]
    summary[cls] = {'episodes': len(selected), 'first_actions': dict(Counter(r['first_action'] for r in selected)),
                    'first_fallback': sum(r['fallback'] for r in selected)}
assert summary['above_bound']['first_actions']['declare_bankruptcy'] == 50
assert summary['payable']['first_actions']['declare_bankruptcy'] == 3
peer = json.loads((ROUND / 'full_drafts/fable_5_2/data/b6_readings.json').read_text())
invalid_maximum_examples = [r for r in peer['rows'] if r['code'] == 'omits']
assert all(r['stated_number_check']['equal'] for r in invalid_maximum_examples)
out = {'scope': 'Saved-record arithmetic and text-field inspection only; no engine execution or new evaluation',
       'first_decisions': summary, 'channels': channels, 'episode_rows': rows, 'g15_sequence': g15,
       'fable_accuracy_metric': {'checks': peer['stated_numbers_checked'], 'equal_to_selected_target': peer['stated_numbers_equal_records'],
                               'omitted_resource_maxima_counted_equal': invalid_maximum_examples,
                               'reading': 'The two false maximum-liquidity claims are compared with the incomplete U0 subtotal, not full available finance. Equality of those subtractions is not correctness of the complete claims.'},
       'sources': sources}
(HERE / 'checks.json').write_text(json.dumps(out, indent=2) + '\n')
frozen = json.loads((ROUND / 'four_draft_manifest.json').read_text())['files']
bad = [p for p, h in frozen.items() if hashlib.sha256((ROUND / p).read_bytes()).hexdigest() != h]
assert not bad, bad
print(json.dumps({'first_decisions': summary, 'channels': channels, 'frozen_files': len(frozen)}, indent=2))
