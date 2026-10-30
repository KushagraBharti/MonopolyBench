"""Render the read-only coverage assessment. Does not inspect game artifacts."""
from pathlib import Path
import html
import json

BASE = Path(__file__).resolve().parent
data = json.loads((BASE / "coverage.json").read_text())
assert list(data["questions"]) == [f"Q{i}" for i in range(1, 9)] + ["A", "B", "C"]
e = html.escape
rows = []
details = []
for key, q in data["questions"].items():
    cells = []
    for field in ["observations", "measurement", "causal_or_transfer"]:
        c = q[field]
        cells.append(f'<td class="{e(c["kind"])}" title="{e(c["detail"])}"><span>{e(c["label"])}</span></td>')
    rows.append(f'<tr><th scope="row"><span class="key">{e(key)}</span> {e(q["question"])}</th>{"".join(cells)}</tr>')
    details.append(f'''<details class="question"><summary>{e(key)}. {e(q["question"])}</summary>
<p class="status">{e(q["status"])}</p><p><strong>Current evidence.</strong> {e(q["strength"])}</p>
<p><strong>Gap.</strong> {e(q["gap"])}</p><p><strong>Writing.</strong> {e(q["writing"])}</p>
<p><strong>Existing logs.</strong> {e(q["existing_logs"])}</p><p><strong>New evaluation.</strong> {e(q["new_evaluation"])}</p>
<p class="muted">Current manuscript pages: {e(q["pages"])}. All improvements are proposals.</p></details>''')

page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Research question coverage</title><style>
:root{color-scheme:light dark;font-family:var(--font-sans,Arial,sans-serif);color:var(--foreground,#242b34)}
*{box-sizing:border-box}html,body{margin:0;padding:0;background:transparent}main{padding:0;background:transparent}
h2{font-size:21px;line-height:1.3;letter-spacing:-.02em;margin:0 0 10px;font-weight:650}
p{font-size:14px;line-height:1.48;margin:8px 0 13px}.muted{color:var(--muted-foreground,#687482)}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:12.5px;line-height:1.3}
col:first-child{width:40%}col{width:20%}thead th{font-size:11.5px;line-height:1.35;font-weight:600;text-align:center;vertical-align:bottom;padding:8px 5px 11px;color:var(--muted-foreground,#687482);border-bottom:2px solid var(--border,#d6dde5)}
thead th:first-child{text-align:left}tbody th{text-align:left;font-weight:550;padding:10px 9px 10px 0;border-bottom:1px solid var(--border,#d6dde5)}
td{padding:8px 5px;text-align:center;vertical-align:middle;border-bottom:1px solid var(--border,#d6dde5)}
td span{display:block;border-radius:5px;padding:7px 3px}td.present span{color:var(--success,#24744b);background:color-mix(in srgb,var(--success,#24744b) 11%,transparent)}
td.bounded span{color:var(--info,#3169a2);background:color-mix(in srgb,var(--info,#3169a2) 11%,transparent)}
td.cases span{color:var(--warning,#a87818);background:color-mix(in srgb,var(--warning,#a87818) 11%,transparent)}
td.absent span{color:var(--muted-foreground,#687482);background:color-mix(in srgb,var(--muted-foreground,#687482) 7%,transparent)}
.key{font-size:10.5px;color:var(--muted-foreground,#687482);font-weight:650;white-space:nowrap}.note{font-size:12px;line-height:1.45;color:var(--muted-foreground,#687482);margin:13px 0}
details{margin:12px 0 0}summary{cursor:pointer;font-size:14px;line-height:1.4;font-weight:600;padding:10px 0;color:var(--foreground,#242b34)}
.question{border-top:1px solid var(--border,#d6dde5);padding-top:4px;margin-top:4px}.question p{font-size:13px}.status{font-weight:600;color:var(--info,#3169a2)}
@media(max-width:450px){h2{font-size:19px}p{font-size:13px}table{font-size:11.5px}thead th{font-size:10.5px;padding:7px 3px}tbody th{padding:10px 5px 10px 0}td{padding:6px 2px}td span{padding:7px 2px}.key{font-size:10px}}
</style></head><body><main>
<h2>What the current paper answers</h2>
<p>The draft has strong results for specific execution and financing questions. It does <strong>not yet answer the full eight-question agenda</strong>. The three broader questions are included below.</p>
<table aria-label="Qualitative coverage by research question and evidence type"><colgroup><col><col><col><col></colgroup><thead><tr><th scope="col">Research question</th><th scope="col">Descriptive<br>observations</th><th scope="col">Systematic target<br>measurement</th><th scope="col">Causal or<br>transfer test</th></tr></thead><tbody>
''' + "\n".join(rows) + '''</tbody></table>
<p class="note"><strong>Narrow</strong> means a measured subproblem, not the whole question. Q8 validates specified claims; it does not establish generalization. A separates text from execution; it does not settle genuine strategic intelligence.</p>
<p class="note">These columns describe evidence types, <strong>not a universal maturity ladder</strong>. A descriptive question can be answered observationally. “Not run” refers to a causal or transfer test of the broad question, not the paper's executable local diagnostics. No completion percentages are assigned.</p>
<details><summary>What to improve for each question</summary>''' + "\n".join(details) + '''</details>
<p class="note">Read-only assessment of the current 40-page draft. The manuscript and outline remain unchanged; no proposed analysis or experiment has begun.</p>
</main></body></html>'''
(BASE / "coverage.html").write_text(page)
print(json.dumps({"questions": len(data["questions"]), "html": str(BASE / "coverage.html")}))
