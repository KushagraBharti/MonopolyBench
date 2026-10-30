"""Read-only: for each Grok call in a saved game's cloud/calls, classify the raw HTTP body as a single
JSON document vs SSE stream, and compare the content pseudo-call name with the tool_call name.
Usage: python3 -I raw_transport_check.py <game_dir> [decision_suffix]"""
import json, sys, glob, os, collections
g = sys.argv[1]; want = sys.argv[2] if len(sys.argv) > 2 else None
stats = collections.Counter()
for f in glob.glob(os.path.join(g, 'cloud', 'calls', '*.response.json')):
    d = json.load(open(f))
    intent_path = f.replace('.response.json', '.intent.json')
    intent = json.load(open(intent_path)) if os.path.exists(intent_path) else {}
    req = d.get('request_payload_raw') or ''
    if 'grok' not in req[:200]:
        continue
    body = (d.get('response_text') or '').lstrip()
    kind = 'sse' if body.startswith('data:') or '\ndata:' in body[:500] else ('json' if body.startswith('{') else 'other')
    stats['grok_calls_' + kind] += 1
    rj = d.get('response_json') or {}
    try:
        m = rj['choices'][0]['message']
    except Exception:
        continue
    tc = (m.get('tool_calls') or [{}])[0].get('function', {}).get('name')
    c = m.get('content') or ''
    cname = None
    try:
        cj = json.loads(c)
        cname = cj.get('name') if isinstance(cj, dict) else None
    except Exception:
        pass
    if cname and tc and cname != tc:
        stats['content_pseudo_call_name_differs_' + kind] += 1
        did = json.dumps(intent)[:2000]
        if want and want in did:
            print('MATCH', os.path.basename(f), kind, 'content', cname, 'tool', tc)
print(dict(stats))
