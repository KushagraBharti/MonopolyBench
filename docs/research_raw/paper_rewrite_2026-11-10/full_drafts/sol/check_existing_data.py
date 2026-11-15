"""Read-only consistency checks and plots of existing retained data. No engine imports."""
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
OLD = HERE.parents[2] / 'paper_draft_2026-10-29'
DATA = OLD / 'data'
report = {'scope': 'Retained-ledger retabulation and original quote checks; no new games, model calls, engine execution or verifier tests.', 'inputs': {}}

def read(name):
    p = DATA / (name + '.json')
    report['inputs'][str(p.relative_to(REPO))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return json.loads(p.read_text())

offers = read('agenda_offers')
assert len(offers) == 920
cells = []
for cell in ['author_only', 'recipient_only', 'both', 'neither']:
    rows = [r for r in offers if r['accept_available'] and r['completion_cell'] == cell]
    counts = Counter(r['response'] for r in rows)
    cells.append({'cell': cell, 'n': len(rows), **counts,
                  'median_net_cash_to_recipient': statistics.median(r['net_cash_author_to_recipient'] for r in rows)})
assert [r['n'] for r in cells] == [289, 140, 81, 408]
assert [r['median_net_cash_to_recipient'] for r in cells] == [200, -350, -100, 100]
report['completion_cells'] = cells
report['all_response_styles'] = {m: dict(Counter(r['response'] for r in offers if r['recipient_model'] == m)) for m in ['Sol','Opus','Gemini','Grok']}
spend = read('t05_spending_units')
report['spending'] = {'units': len(spend), 'outlay': sum(r['spend'] for r in spend),
    'whole_rent': sum(r['paid_developed_rent_whole_game'] for r in spend),
    'post_rent': sum(r['paid_developed_rent_after_first_own_spend'] for r in spend),
    'zero': sum(r['paid_developed_rent_after_first_own_spend']==0 for r in spend),
    'zero_without_elimination': sum(r['paid_developed_rent_after_first_own_spend']==0 and r['creditor_eliminations_on_group']==0 for r in spend)}
elim = read('t06_eliminations')
report['eliminations'] = {'n':len(elim),'below_upper':sum(r['full']<r['owed'] for r in elim),
    'payment_route_recorded':sum(r['avoidable'] for r in elim), 'access_less_than_nominal':sum(r['accessible']!=r['full'] for r in elim)}
assert report['eliminations'] == {'n':60,'below_upper':56,'payment_route_recorded':3,'access_less_than_nominal':1}
windows = read('first_management_windows')['rows']
report['windows'] = dict(Counter(r['cause'] for r in windows))
assert len(windows)==63 and sum(r['built_first_mgmt_turn'] for r in windows)==43
cohort = read('t01_cohort')
report['wins'] = dict(Counter(r['winner'] for r in cohort))
winners = {r['game']: r['winner'] for r in cohort}
flows = read('agenda_flows')
report['typed_flows'] = {}
for kind in sorted({r['kind'] for r in flows}):
    rows = [r for r in flows if r['kind']==kind]
    nonterminal = [r for r in rows if not r.get('terminal_estate',False)]
    report['typed_flows'][kind] = {'events':len(rows),'amount':sum(r['amount'] for r in rows),
        'winner_amount':sum(r['amount'] for r in rows if r.get('to_model')==winners[r['game']]),
        'nonterminal_amount':sum(r['amount'] for r in nonterminal),
        'nonterminal_winner_amount':sum(r['amount'] for r in nonterminal if r.get('to_model')==winners[r['game']])}
assert report['typed_flows']['estate_deed']['nonterminal_amount']==227
assert report['typed_flows']['estate_deed']['nonterminal_winner_amount']==202
assert report['typed_flows']['estate_cash']['nonterminal_amount']==7843
assert report['typed_flows']['estate_cash']['nonterminal_winner_amount']==7148
cert = read('certificate_results')
report['inherited_certificate_summary'] = cert['summary']

m = json.loads((HERE/'transcript_manifest.json').read_text())
quote_checks = []
source_cache = {}
for fid, field in m['fields'].items():
    p = REPO / field['source']
    if p not in source_cache:
        source_cache[p] = p.read_bytes()
    raw = source_cache[p]
    assert hashlib.sha256(raw).hexdigest() == field['source_sha256']
    if field.get('jsonl_line_1based'):
        obj = json.loads(raw.decode().splitlines()[field['jsonl_line_1based']-1])
    else:
        obj = json.loads(raw)
    for part in field['json_pointer'].strip('/').split('/'):
        part = part.replace('~1','/').replace('~0','~')
        obj = obj[int(part)] if isinstance(obj,list) else obj[part]
    assert obj == field['text'], fid
    assert hashlib.sha256(obj.encode()).hexdigest() == field['field_sha256']
for q in m['quotes']:
    for ex in q['excerpts']:
        t = m['fields'][ex['field_id']]['text']
        assert t[ex['span'][0]:ex['span'][1]] == ex['text']
    quote_checks.append(q['id'])
report['original_quote_fields'] = len(m['fields'])
report['quote_definitions_checked'] = quote_checks
report['quote_macros_byte_identical'] = (HERE/'transcript_quotes.tex').read_bytes() == (OLD/'sections/transcript_quotes.tex').read_bytes()
(HERE/'data_checks.json').write_text(json.dumps(report,indent=2)+'\n')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
(HERE/'assets').mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(8.0,3.5))
left = [0]*4
for key,label,color in [('accept_trade','Accept','#26756b'),('counter_trade','Counter','#c79a42'),('reject_trade','Reject','#9b5353')]:
    vals = [100*r.get(key,0)/r['n'] for r in cells]
    ax.barh(range(4),vals,left=left,label=label,color=color,height=.62)
    for i,(v,l) in enumerate(zip(vals,left)):
        if v>5: ax.text(l+v/2,i,f'{v:.1f}%',ha='center',va='center',color='white',fontsize=9)
    left = [a+b for a,b in zip(left,vals)]
ax.set_yticks(range(4),[f'{x} (n={r["n"]})' for x,r in zip(['Author only','Recipient only','Both','Neither'],cells)])
ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Responses among acceptance-legal offers (%)');ax.legend(loc='lower center',bbox_to_anchor=(.5,1.0),ncol=3,frameon=False)
fig.tight_layout();fig.savefig(HERE/'assets/offer_responses.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(6.8,4.3))
for r in elim:
    positive = r['avoidable']
    ax.scatter(r['owed'],r['full'],s=32,marker='s' if r['elimination']=='automatic' else 'o',facecolors='#26756b' if positive else 'none',edgecolors='#26756b' if positive else '#6c737b',alpha=.85)
    if r['accessible']!=r['full']:
        ax.plot([r['owed'],r['owed']],[r['accessible'],r['full']],color='#b6593b',lw=1.7)
        ax.scatter(r['owed'],r['accessible'],marker='D',s=36,color='#b6593b')
        ax.annotate('G7: accessible $440',xy=(r['owed'],r['accessible']),xytext=(1050,300),fontsize=9,arrowprops={'arrowstyle':'-','color':'#b6593b'})
lim=max(max(r['owed'],r['full']) for r in elim)+100
ax.plot([0,lim],[0,lim],ls='--',color='#a0a0a0',lw=1)
ax.set(xlim=(0,lim),ylim=(0,lim),xlabel='Current debt (game dollars)',ylabel='Generous own-asset upper bound (game dollars)')
fig.tight_layout();fig.savefig(HERE/'assets/debt_finance.pdf');plt.close(fig)
print(json.dumps({k:v for k,v in report.items() if k not in ['inputs','inherited_certificate_summary','quote_definitions_checked']},indent=2))
