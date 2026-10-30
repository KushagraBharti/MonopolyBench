"""Read-only: (1) which Grok framing messages appear in the delivered prompts of G13 d251/d253 (every attempt);
(2) the response condition of each attempt; (3) G13 events after d253 involving p4 rent/bankruptcy.
Usage: python3 -I g13_delivery_outcome.py <run_dir>"""
import json, sys, os
run = sys.argv[1]
needles = {
    'd218': 'If I fold on an orange, they inherit Pennsylvania',
    'd243': '8/36 I hit Opus',
    'd244_correction': 'Pennsylvania would not complete Opus',
    'd250': "5/36 is Short Line",
    'd252': '$130 leaves me $35 short',
}
for line in open(os.path.join(run, 'decisions.jsonl')):
    r = json.loads(line)
    if r['phase'] != 'decision_resolved':
        continue
    k = int(r['decision_id'].rsplit('-', 1)[1])
    if k not in (251, 253):
        continue
    for i, at in enumerate(r['attempts']):
        blob = json.dumps(at.get('prompt_messages'), ensure_ascii=False)
        print(f'd{k} attempt {i} condition={at.get("response_condition")} outcome={at.get("outcome")} reason={str(at.get("reason"))[:120]}')
        print('    delivered:', {n: (s in blob or s.replace("$", "\\u0024") in blob) for n, s in needles.items()})
print('--- events after seq of d253 involving p4 or bankruptcy ---')
start = None
for line in open(os.path.join(run, 'decisions.jsonl')):
    r = json.loads(line)
    if r['phase'] == 'decision_resolved' and r['decision_id'].endswith('-000253'):
        start = r['emitted_event_seq_start']
for line in open(os.path.join(run, 'events.jsonl')):
    e = json.loads(line)
    if e['seq'] < start:
        continue
    p = json.dumps(e['payload'])
    if e['type'] in ('RENT_PAID', 'BANKRUPTCY_DECLARED', 'PLAYER_BANKRUPT', 'PLAYER_ELIMINATED', 'GAME_ENDED', 'TAX_PAID', 'TRADE_ACCEPTED', 'PROPERTY_MORTGAGED') or 'BANKRUPT' in e['type']:
        if 'p4' in p or 'BANKRUPT' in e['type'] or e['type'] == 'GAME_ENDED' or (e.get('actor') or {}).get('player_id') == 'p4':
            print(e['seq'], e['turn_index'], e['type'], (e.get('actor') or {}).get('player_id'), p[:260])
