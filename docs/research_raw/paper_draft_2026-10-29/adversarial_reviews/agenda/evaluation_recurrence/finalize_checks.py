"""Freeze the bounded review's checked counts and source revision."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
BASE=ROOT/'docs/research_raw/paper_agenda_revision_2026-10-29'
r=json.loads((HERE/'canonical_recurrence.json').read_text())
e=json.loads((HERE/'evaluation_reexecution.json').read_text())
def selected_stats(rows):
    obs=[x for x in rows if x['next']]
    return dict(episodes=len(rows),observed_next=len(obs),repeated=sum(bool(x['repeat']) for x in obs),
                same_turn=sum(bool(x['same_turn']) for x in obs))
subsets={
    'feedback_with_applied_build':selected_stats([x for x in r['episodes'] if x['feedback'] and x['repaired_here']]),
    'feedback_without_applied_build':selected_stats([x for x in r['episodes'] if x['feedback'] and not x['repaired_here']]),
}
sources=[BASE/'evaluation'/p for p in ['README.md','evaluation_results.tex','protocol.json','run_offline.py','verify_offline.py','check_fixture_states.py','fixture_state_checks_protocol.json']]
sources += [BASE/'integration'/p for p in ['recurrence_audit.py','recurrence_protocol.md','recurrence_results.json','test_recurrence.py']]
sources += [ROOT/'docs/research_raw/paper_draft_2026-10-29/sections/recurrence_results.tex']
payload={
    'review_status':'bounded review complete; no final manuscript rendering claim',
    'findings':[{'id':'ER-M1','severity':'medium','finding':'Corrective-request exposure is not successful repair','correction':'Retitle and distinguish 48/44/4 applied-build episodes from six/six/five without a build'},
                {'id':'ER-M2','severity':'medium','finding':'Same-turn proximity is hidden in main table','correction':'State 18/50 same-turn and 8/32 later-turn repeats'},
                {'id':'ER-L1','severity':'low','finding':'Registered local pilot wording','correction':'Use locally frozen protocol'},
                {'id':'ER-L2','severity':'low','finding':'Network guard is not a general sandbox or paid budget executor','correction':'Keep current narrow scope and future-run implementation prerequisites'}],
    'high_findings':0,
    'canonical_recurrence_summary':r['summary'],
    'recurrence_repair_strata':subsets,
    'canonical_decisions':r['decisions'],
    'canonical_construction_decisions':r['construction'],
    'packet_fields_mismatched':json.loads((HERE/'packet_comparison.json').read_text())['mismatches'],
    'recurrence_diagnostics':r['diagnostic'],
    'replayed_games':e['replayed_games'],'replayed_actions':e['replayed_actions'],'replayed_events':e['replayed_events'],
    'pilot_statuses':e['statuses'],'winner_records':e['winners'],
    'fixture_rejections':e['fixture_rejections'],'invalid_references':e['invalid_references'],
    'state_flag_cases':e['state_flag_cases'],'keyword_scenarios':e['keyword_scenarios'],
    'both_screens_pass':e['both_screens_pass'],
    'engine_exact_bytes_equal':e['engine_exact_bytes_equal'],'engine_sha256':e['engine_sha256'],
    'protected_files':e['protected_files'],'protected_hash_mismatches':e['protected_hash_mismatches'],
    'guard_tests':json.loads((HERE/'guard_tests.json').read_text()),
    'repeat_comparisons':json.loads((HERE/'repeat_comparison.json').read_text()),
    'supplied_recurrence_tests':{'executed':6,'passed':6},
    'paid_arms_status':'design only, not execution-ready or experimentally answered',
    'sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    'limits':['No independent engine implementation','No provider calls or model games','No final integrated PDF review','No fixture optimality certification','No causal feedback or transfer experiment'],
}
assert subsets['feedback_with_applied_build']['observed_next']==44
assert subsets['feedback_with_applied_build']['repeated']==4
assert subsets['feedback_without_applied_build']['observed_next']==6
assert subsets['feedback_without_applied_build']['repeated']==5
(HERE/'checks.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps(subsets,indent=2))
