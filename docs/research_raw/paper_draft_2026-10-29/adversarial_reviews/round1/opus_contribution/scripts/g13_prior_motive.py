"""Read-only: G13 decisions 200-253. Print every public message, plus every p1 (Opus)
returned reasoning / content that mentions p4/grok solvency, yellows, Short Line or Pennsylvania.
Usage: python3 -I g13_prior_motive.py <decisions.jsonl>"""
import json, re, sys
pat = re.compile(r'(solven|bankrupt|yellow|short line|pennsylvania|p4|grok|insurance|inherit)', re.I)
for line in open(sys.argv[1]):
    r = json.loads(line)
    if r['phase'] != 'decision_resolved':
        continue
    k = int(r['decision_id'].rsplit('-', 1)[1])
    if not (200 <= k <= 253):
        continue
    fa = r['final_action']
    pm = fa.get('public_message', '')
    print(f"d{k} t{r['turn_index']} {r['player_id']} {r['decision_type']} {fa['action']} {json.dumps(fa.get('args'))[:160]}")
    if pm:
        print('   PUB:', pm[:400])
    if r['player_id'] == 'p1':
        for i, at in enumerate(r['attempts']):
            try:
                m = at['raw_response']['choices'][0]['message']
            except Exception:
                continue
            txt = (m.get('reasoning') or '') + '\n' + (m.get('content') or '')
            hits = [s.strip() for s in re.split(r'(?<=[.!?])\s+', txt) if pat.search(s)]
            for h in hits[:8]:
                print(f'   [p1 att{i}]', h[:300])
