"""Mask first-pass codes and spans before fresh semantic adjudication."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[1]/'negotiation/rejection_reason_coding.json'
d=json.loads(SOURCE.read_text())
rows=[{k:v for k,v in r.items() if k not in {'codes','evidence'}} for r in d['rows_data']]
assert len(rows)==74
(HERE/'masked_rows.json').write_text(json.dumps(rows,indent=2)+'\n')
(HERE/'coding_protocol.json').write_text(json.dumps({
 'definitions':d['definitions'],
 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'population':d['population'],
 'exposure_limit':'Initial schema inspection accidentally exposed existing aggregate counts and first row codes, plus a fragment of the second row. All later reading used masked rows. This is not a fully blinded review.',
 'scope':'Complete applied public/private fields; recorded reasons, not latent motives or verified reasoning.'
},indent=2)+'\n')
print('Masked',len(rows),'rows')
