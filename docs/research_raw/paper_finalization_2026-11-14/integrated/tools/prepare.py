"""Render stored text after checking it against raw records. No engine imports."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in HERE.parents if (p / 'contracts').is_dir())
data = json.loads((HERE / 'data/complete_financing_records.json').read_text())
cache = {}
def esc(s):
    replacements = {'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$',
                    '#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}',
                    '^':r'\textasciicircum{}','→':r'$\rightarrow$','≥':r'$\geq$',
                    '≤':r'$\leq$'}
    return ''.join(replacements.get(c,c) for c in s).replace('\n\n', '\n\\par\n').replace('\t',' ')

output=[]; fields=[]
for r in data['rows']:
    path=ROOT/r['source']
    if path not in cache:
        blob=path.read_bytes()
        assert hashlib.sha256(blob).hexdigest()==data['sources'][r['source']]
        cache[path] = {int(o['decision_id'].rsplit('-',1)[1]):(i,o) for i,line in enumerate(blob.splitlines(),1)
                       if (o:=json.loads(line))['phase']=='decision_resolved'}
    line,obj=cache[path][r['decision']]
    assert obj['final_action']==r['applied_action']
    last=obj['attempts'][-1]
    message=last.get('raw_response',{}).get('choices',[{}])[0].get('message',{})
    assert message.get('reasoning')==r['provider_reasoning']
    assert last.get('assistant_content')==r['assistant_content']
    if not r['necessity_inequality']: continue
    output += [rf"\subsubsection*{{G{r['game']} d{r['decision']}: {esc(r['model'])}; {r['outcome']}}}",
               rf"Debt \${r['debt']}; cash \${r['cash']}; $U_0={r['U0']}$; $U_*={r['Ustar']}$. Applied action: \texttt{{{esc(r['applied_action']['action'])}}}."]
    channels=[('Authored private note',r['applied_action'].get('private_thought'),'/final_action/private_thought'),
              ('Returned explanation',r['provider_reasoning'],f"/attempts/{len(obj['attempts'])-1}/raw_response/choices/0/message/reasoning"),
              ('Assistant content',r['assistant_content'],f"/attempts/{len(obj['attempts'])-1}/assistant_content")]
    for label,value,pointer in channels:
        output.append(r'\paragraph{'+label+r'.}')
        if value:
            output.append(r'{\small '+esc(value)+r'\par}')
            fields.append(dict(game=r['game'],decision=r['decision'],channel=label,text=value,
                               source=r['source'],source_sha256=data['sources'][r['source']],
                               jsonl_line_1based=line,json_pointer=pointer,
                               field_sha256=hashlib.sha256(value.encode()).hexdigest()))
        else: output.append(r'\textit{Absent.}')
    output.append(r'\medskip')
(HERE/'sections/all_channels.tex').write_text('\n\n'.join(output)+'\n')
(HERE/'data/all_channels_manifest.json').write_text(json.dumps({'fields':fields},indent=2)+'\n')
assert len(data['rows'])==188
assert sum(r['necessity_inequality'] for r in data['rows'])==16
print(f'Checked 188 first responses; rendered {len(fields)} fields for all 16 necessity episodes.')
