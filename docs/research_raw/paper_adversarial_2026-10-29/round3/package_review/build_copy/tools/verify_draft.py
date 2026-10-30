"""Verify manuscript inputs, numerical invariants, references and rendered PDF."""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--portable',action='store_true',help='Skip comparisons to original repository files outside this package.')
args=parser.parse_args()
report = {"checks": {}, "limits": [
    "Numerical invariants use retained audit exports; source-event recount is separately recorded by Sol.",
    "PDF text and geometry checks complement visual inspection, not semantic or causal validation.",
    "This is manuscript-package verification, not the complete public saved-game release."]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / "data" / f"{name}.json").read_text())


protected=json.loads((ROOT/"protected_sources.json").read_text())
report["protected_sources_format"] = type(protected).__name__
if isinstance(protected, dict) and not args.portable:
    for name,value in protected.items():
        path=Path(name)
        if not path.is_absolute(): path=REPO/path
        expected=value if isinstance(value,str) else value["sha256"]
        assert digest(path)==expected, name
report["checks"]["protected_sources_unchanged"]=len(protected) if not args.portable else 'not checked in portable mode'
source_tables=REPO/'docs/research_raw/paper_phase3_2026-10-29/astra/exhibits'
if not args.portable:
    for copied in (ROOT/'data').glob('t*.json'):
        assert digest(copied)==digest(source_tables/copied.name),copied.name
report['checks']['frozen_table_copies']=9 if not args.portable else 'not checked in portable mode'

cohort=read("t01_cohort")
assert len(cohort)==20 and len({r["seed"] for r in cohort})==5
assert sorted(r["game"] for r in cohort)==list(range(1,21))
assert Counter(r["winner"] for r in cohort)==dict(Sol=8,Gemini=7,Opus=3,Grok=2)
assert sum(r["winner_seat"] in [1,2] for r in cohort)==14
assert all(Counter(r["rotation"] for r in cohort if r["seed"]==s)=={1:1,2:1,3:1,4:1} for s in {r["seed"] for r in cohort})
report["checks"]["cohort"]=True

n=read("t02_negotiation")
assert sum(r["proposals"] for r in n)==526
for r in n:
    assert abs(r["proposing_turns"]/r["eligible_turns"]-r["own_turn_propensity"])<1e-12
    assert abs(r["proposals"]/r["proposing_turns"]-r["proposals_per_proposing_turn"])<1e-12
g=read("t03_trade_groups")
assert [sum(r[k] for r in g) for k in ["trade_groups","first_management_built","entry_eligible","entry_eligible_built","eligible_during_window"]]==[63,43,42,34,54]
b=read("t04_bilateral_completion")
assert {r["newly_completed_sides"]:r["trades"] for r in b}=={0:60,1:43,2:10}
res=read("t09_entry_nonbuild_records")
assert len(res)==8
assert sum('default' in r['category'] for r in res)==3
assert sum('conflict' in r['category'] for r in res)==3
assert sum('consistent_end' in r['category'] for r in res)==2
report["checks"]["negotiation_development"]=True

u=read("t05_spending_units")
assert len(u)==103
assert sum(r["spend"] for r in u)==103450
assert sum(r["paid_developed_rent_whole_game"] for r in u)==93000
assert sum(r["paid_developed_rent_after_first_own_spend"] for r in u)==92550
assert sum(r["paid_developed_rent_after_first_own_spend"]==0 for r in u)==40
assert sum(r["paid_developed_rent_after_first_own_spend"]==0 and r["creditor_eliminations_on_group"]==0 for r in u)==26
assert sum(r["winner"] for r in u)==58
assert sum(r["winner"] and r["inherited_deed_at_first_own_spend"] for r in u)==34
g19=[r for r in u if r["game"]==19 and r["configuration"]=="Gemini" and r["group"]=="DARK_BLUE"]
assert len(g19)==1 and g19[0]["spend"]==2000
report["checks"]["spending_and_g19_correction"]=True

e=read("t06_eliminations")
assert Counter(r["elimination"] for r in e)=={"declared":56,"automatic":4}
assert sum(r["full"]<r["owed"] for r in e)==56
assert sum(r["avoidable"] for r in e)==3
assert sum(r["accessible"]!=r["full"] for r in e)==1
assert all((r["accessible"]>=r["owed"])==r["avoidable"] for r in e)
r=read("t07_build_recovery")
assert sum(x["ended_in_default"] for x in r)==66
assert sum(x["changed_purchase_multiset"] for x in r)==17
report["checks"]["liquidation_and_recovery"]=True

texfiles=[ROOT/'manuscript.tex',ROOT/'preamble.tex',*sorted((ROOT/'sections').glob('*.tex'))]
text='\n'.join(f.read_text() for f in texfiles)
bib=(ROOT/'references.bib').read_text()
keys=set(re.findall(r'@\w+\{([^,]+),',bib))
used={k.strip() for group in re.findall(r'\\cite\w*(?:\[[^]]*\])*\{([^}]+)\}',text) for k in group.split(',')}
assert used<=keys,used-keys
labels=re.findall(r'\\label\{([^}]+)\}',text)
refs=set(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',text))
assert refs<=set(labels), refs-set(labels)
assert not [k for k,v in Counter(labels).items() if v>1]
assert not re.search(r'\b(?:TODO|TBD|FIXME)\b',text)
report['checks']['references']={'citations':len(used),'labels':len(labels),'unresolved':0}

log=(ROOT/'build/manuscript.log').read_text()
warnings=[line for line in log.splitlines() if any(term in line for term in ['Overfull','Missing character','undefined references','undefined citations'])]
assert not warnings,warnings
doc=pymupdf.open(ROOT/'manuscript.pdf')
outside=[];launch=[];pages=[]
for i,page in enumerate(doc):
    spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    for s in spans:
        box=pymupdf.Rect(s['bbox'])
        if box.x0 < -1 or box.y0 < -1 or box.x1 > page.rect.width+1 or box.y1 > page.rect.height+1:
            outside.append([i+1,s['text']])
    for link in page.get_links():
        if link.get('kind')==pymupdf.LINK_LAUNCH:launch.append(i+1)
    pages.append({'page':i+1,'words':len(page.get_text().split()),'width':page.rect.width,'height':page.rect.height})
assert not outside,outside
assert not launch,launch
report['checks']['pdf']={'pages':len(doc),'outside_page_spans':outside,'launch_links':launch,'warnings':warnings}
report['page_inventory']=pages
report['files']={str(f.relative_to(ROOT)):digest(f) for f in [*texfiles,ROOT/'references.bib',ROOT/'manuscript.pdf']}
report['status']='pass'
(ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'pass','pages':len(doc),'citations':len(used),'protected_sources':len(protected)}))
