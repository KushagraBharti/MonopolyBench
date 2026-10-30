#!/usr/bin/env python3
"""Upsert candidate rows (JSON objects, one per line or a JSON list) from stdin into ../candidates.jsonl keyed by case_id."""
import sys, json, os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fn = os.path.join(base, 'candidates.jsonl')
cur = {}
order = []
if os.path.exists(fn):
    for l in open(fn):
        d = json.loads(l); cur[d['case_id']] = d; order.append(d['case_id'])
txt = sys.stdin.read().strip()
try:
    objs = json.loads(txt)
    if isinstance(objs, dict): objs = [objs]
except json.JSONDecodeError:
    objs = [json.loads(l) for l in txt.splitlines() if l.strip()]
for o in objs:
    o.setdefault('reviewer', 'claude-sonnet-5-5')
    o.setdefault('effort', 'xhigh')
    if o['case_id'] not in cur: order.append(o['case_id'])
    cur[o['case_id']] = o
with open(fn, 'w') as f:
    for k in order:
        f.write(json.dumps(cur[k], ensure_ascii=False) + '\n')
print('candidates now', len(cur))
