#!/usr/bin/env python3
"""Upsert per-decision review notes.  stdin lines:  idx ::: note ::: cand1,cand2   (cands optional)
Writes ../notes.jsonl (keyed by global manifest idx).  Notes are written by the reviewer after reading the chunk."""
import sys, json, os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fn = os.path.join(base, 'notes.jsonl')
cur = {}
if os.path.exists(fn):
    for l in open(fn):
        d = json.loads(l); cur[d['idx']] = d
n = 0
for line in sys.stdin:
    line = line.rstrip('\n')
    if not line.strip():
        continue
    parts = [p.strip() for p in line.split(' ::: ')]
    idx = int(parts[0]); note = parts[1]
    cands = [c for c in (parts[2].split(',') if len(parts) > 2 else []) if c.strip()]
    cur[idx] = {'idx': idx, 'note': note, 'candidate_ids': [c.strip() for c in cands]}
    n += 1
with open(fn, 'w') as f:
    for k in sorted(cur):
        f.write(json.dumps(cur[k], ensure_ascii=False) + '\n')
print('upserted', n, 'total notes', len(cur), 'max idx', max(cur))
