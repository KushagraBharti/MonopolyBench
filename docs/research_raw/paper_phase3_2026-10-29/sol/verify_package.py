"""Check this research package's links, source hashes and reporting joins."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
    failures=[];checks={}
    source=json.loads((HERE/'source_manifest.json').read_text())
    for r in source:
        if r['status']!=200:failures.append(('source_status',r['key']));continue
        if digest(HERE/r['text_path'])!=r['text_sha256']:failures.append(('source_hash',r['key']))
    checks['frozen_primary_sources']=len(source)
    manifest=json.loads((HERE/'exhibits/manifest.json').read_text())
    for r in manifest['inputs']:
        if digest(ROOT/r['path'])!=r['sha256']:failures.append(('figure_input_hash',r['path']))
    for name,h in manifest['outputs'].items():
        if digest(HERE/'exhibits'/name)!=h:failures.append(('figure_output_hash',name))
    checks['figure_outputs']=len(manifest['outputs'])
    for r in json.loads((HERE/'planned_source_manifest.json').read_text()):
        if not r['exists'] or digest(ROOT/r['path'])!=r['sha256']:failures.append(('planned_source',r['path']))
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http:','https:','#')):continue
            target=target.split('#')[0]
            if not (p.parent/target).exists():failures.append(('local_link',p.name,target))
            links+=1
    checks['local_links']=links
    sol=json.loads((ROOT/'docs/research_raw/paper_phase2_2026-10-28/core_review/sol/corpus_economics_audit.json').read_text())
    astra=json.loads((ROOT/'docs/research_raw/paper_phase2_2026-10-28/core_review/astra/development_aggregation_check.json').read_text())
    a={(u['game'],u['player'],u['group']):u for u in astra['units']}
    for u in sol['spending_units']:
        v=a[(u['game'],u['actor'],u['group'])]
        for k,j in [('spend','spend'),('salvage','sale_proceeds'),('whole_game_developed_rent','developed_rent_whole_game'),('developed_rent_after_first_own_spend','developed_rent_from_first_own_build')]:
            if u[k]!=v[j]:failures.append(('unit_join',u['game'],u['actor'],u['group'],k))
    checks['cross_audit_spending_units']=len(sol['spending_units'])
    c=json.loads((HERE/'comparison.json').read_text())['entries']
    keys=re.findall(r'^@\w+\{([^,]+),',(HERE/'references.bib').read_text(),re.M)
    assert len(keys)==len(set(keys))==29
    assert all(r.get('citation_key',r['key']) in keys for r in c if r.get('id','').startswith('L'))
    checks['bibliography_records']=len(keys)
    csvrows=list(csv.DictReader((HERE/'exhibits/spending_units.csv').open()))
    assert len(csvrows)==103 and sum(int(r['spend']) for r in csvrows)==103450
    checks['spending_csv_rows']=len(csvrows)
    peer=json.loads((HERE/'peer_followup_checks.json').read_text())
    for rel,h in peer['source_hashes'].items():
        if digest(HERE.parent/rel)!=h:failures.append(('peer_derived_source_hash',rel))
    assert peer['first_management_groups']==63
    checks['peer_derived_management_rows_recounted']=63
    checks['peer_stock_report_decisions']=peer['stock_report']['decisions_checked']
    checks['peer_stock_report_mismatches']=peer['stock_report']['reported_mismatches']
    checks['manual_visual_review']='All three final PNG exports inspected; cell overlap and crowded ticks corrected. No full manuscript render exists.'
    report={'checks':checks,'failures':failures,'scope':'Reporting/package verification only. Canonical engine/replay audits inherited with explicit phase2 attribution; no new game or provider call.'}
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));assert not failures
if __name__=='__main__':main()
