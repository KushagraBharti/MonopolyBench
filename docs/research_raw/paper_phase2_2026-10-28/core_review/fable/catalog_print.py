#!/usr/bin/env python3
"""Fable's reading aid: print all catalog entries for a game (or 'terra') compactly but without dropping claims."""
import json, sys, re
CAT='/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/candidate_catalog.jsonl'
rows=[json.loads(l) for l in open(CAT)]
def refs(dr):
    out=[]
    for d in dr:
        ev=d.get('key_event_seqs') or []
        out.append(f"#{d.get('display_number')}({d.get('player_id')},t{d.get('turn_index')},{d.get('action')},ev{'/'.join(ev) if ev else d.get('event_seq_range')})")
    return ' '.join(out)
def pub(se):
    L=[]
    L.append(f"TITLE: {se.get('title')} | priority={se.get('priority')} | tags={se.get('tags')} | uncertainty={se.get('uncertainty')}")
    L.append(f"REFS: {refs(se.get('decision_refs',[]))}")
    if se.get('parties_and_roles'): L.append('PARTIES: '+' || '.join(se['parties_and_roles']))
    if se.get('observed_conduct'): L.append('OBSERVED: '+se['observed_conduct'])
    if se.get('quotes'):
        L.append('QUOTES: '+' || '.join(f"#{q.get('display_number')} {q.get('model')}:{q.get('text')!r}{'' if q.get('verified_exact_substring') else ' [UNVERIFIED]'}" for q in se['quotes']))
    for k in ['financial_evidence','supporting_evidence','contrary_evidence','alternative_interpretations','exposure_checks']:
        v=se.get(k)
        if v: L.append(k.upper()+': '+(' || '.join(map(str,v)) if isinstance(v,list) else str(v)))
    for k in ['inferred_motive_or_interpretation','endpoint','follow_up']:
        if se.get(k): L.append(k.upper()+': '+str(se[k]))
    if se.get('revision_history'): L.append('REVISIONS: '+json.dumps(se['revision_history'])[:600])
    return '\n  '.join(L)
def md(r):
    t=r['raw_markdown']
    t=re.sub(r'\]\((?:\.\./)+', '](', t)
    return t.strip()
sel=sys.argv[1]
for r in rows:
    if sel=='terra' and r['source_reviewer']!='terra': continue
    if sel!='terra' and str(r['game'])!=sel: continue
    print('='*90)
    print(f"{r['catalog_id']} [{r['source_reviewer']}/{r['entry_status']}] src={r['source_file'].split('/')[-2]}/{r['source_file'].split('/')[-1]}:{r['source_start_line']}-{r['source_end_line']}")
    if 'source_entry' in r: print('  '+pub(r['source_entry']))
    else: print('  SECTION: '+r.get('section','')); print('  '+md(r))
