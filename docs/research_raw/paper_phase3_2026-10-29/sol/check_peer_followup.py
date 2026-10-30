"""Recount peer-derived tables without claiming a new original-artifact audit."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PATHS=[BASE/'fable/exhibits/first_management_causes.json',
       BASE/'fable/exhibits/first_management_causes.csv',
       BASE/'fable/exhibits/house_stock_report.json',
       BASE/'fable/exhibits/house_stock_series.csv']

def main():
    d=json.loads(PATHS[0].read_text());h=json.loads(PATHS[2].read_text())
    rows=d['rows'];assert len(rows)==63
    assert len({(r['game'],r['player'],r['group']) for r in rows})==63
    summary={}
    for model,expected in d['summary'].items():
        rs=[r for r in rows if r['model']==model]
        counts=Counter(r['cause'] for r in rs)
        assert len(rs)==expected['groups']
        assert all(counts[c]==expected[c] for c in d['causes'])
        entry=[r for r in rs if r['entry_legal']]
        window=[r for r in rs if r['legal_any_menu_that_turn']]
        summary[model]={'all':dict(counts),'groups':len(rs),
                        'entry':dict(Counter(r['cause'] for r in entry)),
                        'legal_any_window':dict(Counter(r['cause'] for r in window))}
    counts=Counter(r['cause'] for r in rows)
    assert counts==Counter(built=43,never_legal_in_window=9,default_after_refusal=3,
                           default_other=1,received_conflict=4,valid_end=3)
    residuals=[{'model':r['model'],'game':r['game'],'group':r['group'],
                'category':r['cause'],'ending_decision':r['decisions'][-1]['decision_id']}
               for r in rows if r['cause'] not in ['built','never_legal_in_window']]
    assert all(r['decisions'][-1]['applied']=='end_turn' for r in rows
               if r['cause'] not in ['built','never_legal_in_window'])
    checked=sum(g['decisions_checked'] for g in h['games'])
    mismatches=sum(g['decision_mismatches'] for g in h['games'])
    zeros=[g['game'] for g in h['games'] if g['min_houses']==0]
    assert checked==6989 and mismatches==0
    assert zeros==[3,4,5,6,7,9,12,14,18]
    report={'source_hashes':{str(p.relative_to(BASE)):sha256(p.read_bytes()).hexdigest() for p in PATHS},
            'first_management_groups':len(rows),'summary':summary,'totals':dict(counts),
            'terminal_cases':residuals,'stock_report':{'decisions_checked':checked,
            'reported_mismatches':mismatches,'zero_stock_games':zeros},
            'scope':'Sol recount of Fable derived tables and metadata. Original reconstruction, window/channel categorization and source matching remain attributed to Fable. No independent original replay or new semantic annotation.',
            'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'peer_followup_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'groups':len(rows),'categories':dict(counts),'stock_checks':checked,'reported_stock_mismatches':mismatches}))

if __name__=='__main__':main()
