"""Read-only dump of resolved decisions in a saved game.
Usage: python3 -I dump_decisions.py <decisions.jsonl> <start> <end> [maxchars]"""
import json, sys
path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
for line in open(path):
    r = json.loads(line)
    if r['phase'] != 'decision_resolved':
        continue
    k = int(r['decision_id'].rsplit('-', 1)[1])
    if not (a <= k <= b):
        continue
    print('=' * 100)
    print(f"d{k} turn={r['turn_index']} {r['player_id']} {r['player_name']} {r['decision_type']} fallback={r['fallback_used']} retry={r['retry_used']}")
    print('FINAL', json.dumps(r['final_action'])[:mx])
    for i, at in enumerate(r['attempts']):
        print(f'-- attempt {i} keys={sorted(at.keys())}')
        raw = at.get('raw_response') or {}
        try:
            msg = raw['choices'][0]['message']
        except Exception:
            msg = {}
        if msg.get('content'):
            print('  CONTENT:', str(msg['content'])[:mx])
        if msg.get('reasoning'):
            print('  REASONING:', str(msg['reasoning'])[:mx])
        for tc in msg.get('tool_calls') or []:
            print('  TOOL:', tc['function']['name'], tc['function']['arguments'][:mx])
        for kk in ('error', 'validation_error', 'refusal', 'status'):
            if at.get(kk):
                print(f'  {kk}:', str(at[kk])[:400])
