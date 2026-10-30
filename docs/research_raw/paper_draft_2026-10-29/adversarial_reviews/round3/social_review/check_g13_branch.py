"""Independently replay the focal prefix and execute its two-action witness."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'python/packages/engine/src'))
sys.dont_write_bytecode = True
from monopoly_engine.engine import Engine

def read(path):
    return json.loads(path.read_text())

def main():
    manifest = read(ROOT / 'docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json')
    run = ROOT / next(g['run'] for g in manifest['games'] if g['game'] == 13)
    config = read(run / 'run_config.json')
    paths = [run / n for n in ['run_config.json', 'actions.jsonl', 'events.jsonl']]
    paths += sorted((ROOT / 'python/packages/engine/src/monopoly_engine').glob('*.py'))
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    rows = [json.loads(line) for line in (run / 'actions.jsonl').open()]
    original = [json.loads(line) for line in (run / 'events.jsonl').open()]
    engine = Engine(**{k: config[k] for k in ['seed', 'players', 'run_id', 'max_turns', 'start_ts_ms', 'ts_step_ms', 'max_trade_exchanges', 'max_auction_actions']})
    replay = []
    for row in rows[:252]:
        _, ev, d, _ = engine.advance_until_decision(max_steps=10000)
        replay += ev
        assert d['decision_id'] == row['decision_id']
        _, ev, _, _ = engine.apply_action(row['action'], decision_meta=row['decision_meta'])
        replay += ev
    _, ev, decision, _ = engine.advance_until_decision(max_steps=10000)
    replay += ev
    assert decision['decision_id'].endswith('-dec-000252')
    assert replay == original[:len(replay)], 'Full prefix mismatch'
    before = engine.get_snapshot()
    assert decision['player_id'] == 'p4'
    witness = []
    for name, args in [('accept_trade', {}), ('mortgage_property', {'space_key': 'VENTNOR_AVENUE'})]:
        action = {'schema_version': 'v1', 'decision_id': decision['decision_id'], 'action': name,
                  'args': args, 'public_message': 'Independent review witness.'}
        errors = engine.validate_action_for_decision(action, decision)
        assert errors == [], errors
        _, ev, new_decision, _ = engine.apply_action(action)
        witness.append({'decision': decision, 'action': action, 'validation_errors': errors,
                        'emitted_events': ev, 'snapshot': engine.get_snapshot()})
        decision = new_decision
        if decision is None:
            _, _, decision, _ = engine.advance_until_decision(max_steps=10000)
    player = next(p for p in engine.state.players if p.player_id == 'p4')
    assert player.cash == 295
    assert engine.state.turn_index == 107
    assert decision['player_id'] == 'p4'
    assert decision['decision_type'] == 'POST_TURN_ACTION_DECISION'
    result = {'source_hashes': sources, 'prefix_actions': 252, 'matched_original_events': len(replay),
              'prefix_match': True, 'before': before, 'witness': witness,
              'endpoint': {'cash': player.cash, 'turn_index': engine.state.turn_index,
                           'next_decision': decision['decision_type'], 'next_actor': decision['player_id'],
                           'cash_above_200': player.cash - 200,
                           'scope': 'Legal financing before ending turn 107. No new roll, counterparty choice, or later LLM continuation.'}}
    (OUT / 'g13_branch_result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['prefix_actions', 'matched_original_events', 'prefix_match', 'endpoint']}))

if __name__ == '__main__':
    main()
