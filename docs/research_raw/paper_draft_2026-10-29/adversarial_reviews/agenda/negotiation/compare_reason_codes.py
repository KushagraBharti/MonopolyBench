"""Post-lock comparison. This does not adjudicate disagreements by vote."""
import collections
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXT=HERE.parents[1]/'negotiation'
own=json.loads((HERE/'own_74_row_ledger.json').read_text())
prior=json.loads((EXT/'rejection_reason_coding.json').read_text())['rows_data']
assert [(x['game'],x['decision'])for x in own]==[(x['game'],x['decision'])for x in prior]
result={}
disagreements=[]
for code in 'DCRTFN':
    a={i for i,x in enumerate(own) if code in x['reviewer_codes']}
    b={i for i,x in enumerate(prior) if code in x['codes']}
    result[code]={'reviewer_positive':len(a),'first_pass_positive':len(b),'common_positive':len(a&b),
                  'either_positive':len(a|b),'both_negative':74-len(a|b),'disagreement_rows':len(a^b),
                  'common_positive_keys':[f"G{own[i]['game']:02}d{own[i]['decision']:03}"for i in sorted(a&b)],
                  'reviewer_only_keys':[f"G{own[i]['game']:02}d{own[i]['decision']:03}"for i in sorted(a-b)],
                  'first_pass_only_keys':[f"G{own[i]['game']:02}d{own[i]['decision']:03}"for i in sorted(b-a)]}
for x,y in zip(own,prior):
    if set(x['reviewer_codes'])!=set(y['codes']):
        disagreements.append({'review_row':x['review_row'],'game':x['game'],'decision':x['decision'],
                              'reviewer_codes':x['reviewer_codes'],'original_codes':y['codes'],
                              'reviewer_rationale':x['reviewer_rationale'],'original_evidence':y['evidence'],
                              'public_message':x['public_message'],'applied_private_note':x['applied_private_note']})
(HERE/'reason_comparison.json').write_text(json.dumps({'categories':result,'exact_row_agreement':74-len(disagreements),
 'rows':74,'disagreements':len(disagreements),'scope':'Two model-assisted coding passes, not independent human labels or gold standard. Shared source, first row exposure and category-boundary ambiguity prevent a blind validation claim.'},indent=2)+'\n')
(HERE/'disagreements.json').write_text(json.dumps(disagreements,indent=2)+'\n')
print(json.dumps({c:{k:v for k,v in x.items() if not k.endswith('_keys')}for c,x in result.items()},indent=2))
