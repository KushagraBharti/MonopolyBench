"""Typeset new numerical tables from analyze_records.py outputs."""
import json
from pathlib import Path
H=Path(__file__).resolve().parent
joint=json.loads((H/'data/joint_responses.json').read_text())
ss=[r'\begin{longtable}{@{}llrrrr@{}}',r'\caption{Joint recipient and stage cells for acceptance-legal offers. Each entry is A/C/R.}\label{tab:joint}\\',r'\toprule Recipient & Stage & \multicolumn{1}{c}{Author only} & \multicolumn{1}{c}{Recipient only} & \multicolumn{1}{c}{Both} & \multicolumn{1}{c}{Neither}\\\midrule\endfirsthead',r'\toprule Recipient & Stage & Author only & Recipient only & Both & Neither\\\midrule\endhead',r'\bottomrule\endfoot']
for m in ['Sol','Gemini','Opus','Grok']:
 for stage in ['opening','later']:
  rr=[next(r for r in joint if r['model']==m and r['stage']==stage and r['cell']==c) for c in ['author_only','recipient_only','both','neither']]
  ss.append(m+' & '+stage.title()+' & '+' & '.join(f"{r['accept']}/{r['counter']}/{r['reject']}" for r in rr)+r' \\')
ss.append(r'\end{longtable}')
(H/'sections/joint_table.tex').write_text('\n'.join(ss)+'\n')
cells=json.loads((H/'data/price_cells.json').read_text())
ss=[r'\begin{longtable}{@{}lllrr@{}}',r'\caption{Seller asks by author, mortgage status, and stage. Ratios are cash divided by total deed list price; counts appear in parentheses.}\label{tab:pricecells}\\',r'\toprule Seller & Mortgage & Stage & Completes buyer & Neither\\\midrule\endfirsthead',r'\toprule Seller & Mortgage & Stage & Completes buyer & Neither\\\midrule\endhead',r'\bottomrule\endfoot']
for m in ['Sol','Gemini','Opus','Grok']:
 for mort in [False,True]:
  for stage in ['opening','later']:
   rr=[next(r for r in cells if r['model']==m and r['mortgaged']==mort and r['stage']==stage and r['cell']==c) for c in ['recipient_only','neither']]
   if not any(r['n'] for r in rr):continue
   vals=[f"{r['median']:.3f} ({r['n']})" if r['n'] else '0 offers' for r in rr]
   ss.append(' & '.join([m,'Yes' if mort else 'No',stage.title()]+vals)+r' \\')
ss.append(r'\end{longtable}')
(H/'sections/price_table.tex').write_text('\n'.join(ss)+'\n')
def esc(s):
 return ''.join({'\\':r'\textbackslash{}','{':r'\{','}':r'\}','$':r'\$','&':r'\&','#':r'\#','_':r'\_','%':r'\%','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s)
for kind in ['standard','recovery']:
 txt=(H/f'data/{kind}_system_prompt.txt').read_text()
 (H/f'sections/{kind}_prompt.tex').write_text(r'\begingroup\footnotesize\ttfamily\raggedright\setlength{\parindent}{0pt}'+'\n'+'\n'.join(esc(line)+r'\par' for line in txt.splitlines())+'\n'+r'\endgroup'+'\n')
