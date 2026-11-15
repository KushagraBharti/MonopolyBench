#!/usr/bin/env python3
"""Reproduce the supplement's 43/48 numeric-presence count independently and
list match contexts for reading. Reads packaged episodes_188.json only. Read-only."""
import json, re, collections, pathlib
INT = pathlib.Path('/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_finalization_2026-11-14/integrated')
E = json.loads((INT/'data/episodes_188.json').read_text())
num = re.compile(r'(?<![\w.])\$?\s?(\d{1,3}(?:,\d{3})+|\d+)(?![\w]|\.\d)')
out=[]; c=collections.Counter(); strict=0
for e in E:
    if e['Ustar'] >= e['debt']: continue
    o=e['options']
    if not (o['mortgageable_space_keys'] or o['sellable_building_space_keys']): continue
    C,D,U=e['cash'],e['debt'],e['Ustar']
    cand={U:'U*',U-C:'U*-C',D-U:'D-U*'}
    for bad in (0,C,D,D-C): cand.pop(bad,None)
    hits=[]
    for ch,t in (('note',e['applied_action'].get('private_thought')),('provider',e['provider_reasoning']),('content',e['assistant_content'])):
        if not t: continue
        for m in num.finditer(t):
            n=int(m.group(1).replace(',',''))
            if n in cand: hits.append((ch,cand[n],n,t[max(0,m.start()-70):m.end()+40].replace('\n',' ')))
    kinds={h[1] for h in hits}
    out.append(dict(g=e['game'],d=e['decision'],model=e['model'].split()[0],C=C,D=D,U=U,U0=e['U0'],hits=hits))
    c['n']+=1; c['match']+=bool(hits); strict += ('U*' in kinds)
print(dict(c), 'responses containing the U* value itself:', strict)
for r in out:
    h=r['hits'][0] if r['hits'] else None
    print(f"G{r['g']} d{r['d']} {r['model']:<16} D={r['D']} U*={r['U']} U0={r['U0']} :: " + (f"[{h[0]}:{h[1]}={h[2]}] ...{h[3]}..." if h else 'NO MATCH'))
