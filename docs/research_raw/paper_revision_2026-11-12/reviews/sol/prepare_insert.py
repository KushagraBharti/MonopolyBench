"""Prepare owned review artifacts from frozen text and saved-record arithmetic."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
DRAFTS=BASE/'full_drafts'

def loc(path, passage):
    text=(DRAFTS/path).read_text()
    assert passage in text,(path,passage)
    return {'path':'full_drafts/'+path,'line':text[:text.index(passage)].count('\n')+1,'exact_passage':passage}

data=[
('SC-01','high','Keep the verified first-action census; narrow the discrimination interpretation',
 [('fable_5_2/sections/own.tex','The table does show discrimination at the first menu.'),
  ('fable_5_2/sections/own.tex','An agent that quits has judged the whole route from the first menu.')],
 'Original first decisions reproduce 50/56 above-bound declarations and 3/131 payable declarations. Eight of the fifty above-bound menus offer neither sale nor mortgage; the other forty-two offer a financing action. Six above-bound episodes continue before elimination. None of the fifty is a fallback. These actions do not measure calibrated beliefs or make continuing an error.',
 'Retain counts beside the full debt partition and describe applied first actions. Disclose the eight no-financing menus. Remove the claim that every declaration establishes assessment of the whole route or a classification accuracy score.'),
('SC-02','high','Selected numeric equality is not recalled-value or assessment accuracy',
 [('fable_5_2/sections/own.tex','Since the prompt supplies none of these values, each one is a board fact the system recalled.'),
  ('fable_5_2/sections/own.tex','its arithmetic is correct in all but one case'),
  ('fable_5_2/sections/discussion.tex','For their own debts the statements were accurate.')],
 'build_quotes.py selects fifteen heterogeneous checks. The two stated_maximum checks compare $408 and $530 with C+M0+S, not the full bounds $748 and $905. Many checked gaps and balances are derived quantities, not board constants. Delivered memory includes prior financing amounts, including G20 Sol $325 idle mortgage capacity. 14/15 is reproducible only as this selected-check statistic; it is not an exhaustive count of recalled values or correct statements.',
 'Print what was checked and separate partial-sum arithmetic, missing resources, numerical recall, and statement correctness. Prefer the case-level ledger and the $430/$400 error over a headline accuracy rate. Say the current menu omits a board-value table, without assigning every value to recall.'),
('SC-03','high','Resource requirements do not calibrate difficulty',
 [('opus/sections/finance.tex',r'\subsection{Most debts were easy}'),
  ('fable_5_2/sections/own.tex','The third row of Table~\\ref{tab:debt} is the hard set.'),
  ('fable_5_2/findings_and_limits.md','The partition by first-menu sums does it from stored records.')],
 'The 62/53/16 resource partition and 67 one-action payments reproduce. No evaluated reference policy, matched task family, or performance measure calibrates difficulty. G7 shows why a sufficient sum is not a legal sequence.',
 'Use requirements or dependency wording and state execution counts. Remove easy/hard labels, the claim that stopping alone needs foresight, and the handoff claim that sums provide difficulty calibration.'),
('SC-04','high','Coarse capacity strata do not establish insensitivity to rival opportunity',
 [('fable_5_2/sections/rival.tex','It does not follow the measured size of what the rival could do next, which level four would require.'),
  ('fable_5_2/sections/discussion.tex','They did not track the amount of building the rival could afford')],
 'Recomputed capacity-bin rejection counts are swaps 4/8,26/33,42/48,23/27 and cash bids 2/3,13/19,7/20,20/28. The measure uses post-trade cash divided by house cost, not full mortgage-enabled legal construction. Different states, proposers and compensation populate each bin; bins are small and retrospectively selected.',
 'Retain the observed lack of a monotonic ordering as exploratory description in the supplement. State that sensitivity is not identified, including whether agents respond to capacity or completion itself. Remove the event-versus-size conclusion from abstract and conclusion.'),
('SC-05','high','Selected statement-action matches cannot support a general predictive thesis',
 [('opus/sections/discussion.tex','Where channels agree, a stated plan is a good guide to the action that follows'),
  ('opus/sections/discussion.tex','the failures we can trace lie in the assessment rather than in carrying it out.'),
  ('opus/sections/discussion.tex','statements that counted those mortgages preceded fourteen payments')],
 'The complete debt population is defined, but plan/action agreement was not exhaustively measured across all 6,989 decisions or all narrated plans. Eight incidents were chosen for interpretability. In the necessary subset, thirteen texts assert/include the resource and one raises an open question. Grok conflicts are observed exceptions, not proof that all other plans predict execution.',
 'Limit correspondence to the enumerated episodes and checked statements. Preserve 13 explicit/aggregate plus 1 tentative in the conclusion. Do not characterize an unmeasured overall explanation-action relationship.'),
('SC-06','medium','Sol and Opus collapse the sale-offer population',
 [('sol/sections/bargaining.tex','Table~\\ref{tab:full} gives every form and completion category at both opening and later stages.'),
  ('opus/sections/design.tex','Other forms, mostly deed-for-cash sales, form a third class.')],
 'The four-form recount gives 96 legal opening cash asks and 104 later asks. Sol and Opus include them in other together with residual bundles. All 918 observations remain counted, but the economically distinct form is hidden. The 29/45 pooled own-completion other-form figure includes 26/41 cash asks and 3/4 residual offers.',
 'Use Astra/Fable four-form tables and definitions, including explicit zero cells or clearly marked zeros. Give opening/later populations. Preserve residual forms separately.'),
('SC-07','medium','Sol attributes the Park Place release example to the wrong episode',
 [('sol/sections/finance.tex','G18 Gemini identifies the one-house sale that releases Park Place.')],
 'Original G18 d309 Gemini sells eight pink houses and names the St. Charles mortgage. Original G8 d257 Gemini sells the Boardwalk house and anticipates Park Place/Boardwalk mortgages. The full entry fields printed in Sol already contain the correct texts.',
 'Replace G18 with G8 and identify the Boardwalk sale. This is a correction to my own draft, not an error in the 16/14 counts.'),
('SC-08','medium','Two-stage resampling changes the fixed-rotation design',
 [('opus/sections/design.tex','Our primary summary therefore resamples seed blocks and then games within each drawn block (20,000 draws)')],
 'Each original seed block contains each of four cyclic rotations once. Sampling its four games with replacement can duplicate one rotation and omit another. Exact intact-block resampling reproduces the 24.2 to 35.5 point range, while the two-stage calculation adds a separate reweighting of rotation cells.',
 'Prefer intact blocks for the fixed-rotation composition diagnostic. If retaining two-stage results, label the additional assumption and target; do not claim that they preserve the same four-rotation design or have future-seed coverage.'),
('SC-09','medium','Arithmetic sufficiency does not establish alternative executable routes',
 [('opus/sections/finance.tex','In the other five, four by Gemini in G3 and one by Sol in G18, the agents could have paid from listed mortgages and salvage alone.'),
  ('fable_5_2/sections/own.tex','In the other five the released deeds were one way to pay among several.')],
 'The 19/14/5 and 33-action counts reproduce. The five optional rows have C+M0+S at or above debt. That upper bound does not by itself establish a legal route excluding new mortgages under sale ordering and house-stock constraints; no such alternative route was run here. Actual payment establishes the observed route.',
 'Say five used released collateral despite arithmetic sufficiency of listed mortgages plus salvage. Do not assert several legal alternatives without a retained witness.'),
('SC-10','medium','Saved request intents strengthen and correct tool-choice provenance',
 [('sol/evidence_map.md','Request artifacts do not retain tool_choice')],
 '8,687 saved cloud/calls/*.intent.json payloads retain tool_choice: 1,705 Grok required and all other requests auto. Source agrees at both recorded commits. There are 8,679 attempts in resolved-decision records, so the two populations must not be conflated.',
 'Replace the source-only limitation in Sol evidence_map.md. State the evidence as stored outgoing request intents plus frozen source, and distinguish intent count from attempt count.'),
('SC-11','low','Specify the direct dice event in the G13 probability correction',
 [('astra/sections/conduct.tex',r"The seller's 5/36 claim is incorrect for a single roll, which gives 4/36")],
 'Atlantic to Short Line is a direct move of nine. Four of thirty-six equally likely two-dice outcomes total nine. Other movement and extra rolls are different events. The surrounding Astra caveat addresses doubles but leaves the first probability sentence less specific than Sol/Opus.',
 'Use: A direct dice move from Atlantic to Short Line requires nine, with probability 4/36. This does not quantify every way to arrive during a turn.')]

findings=[]
for fid,severity,title,locations,evidence,recommendation in data:
    findings.append({'id':fid,'severity':severity,'title':title,'locations':[loc(p,t) for p,t in locations],
                     'evidence':[{'source':'reviews/sol/saved_record_checks.json and cited frozen source passages','detail':evidence}],
                     'recommendation':recommendation,'status':'integration correction proposed; frozen inputs untouched'})
(HERE/'findings.json').write_text(json.dumps({'schema_version':'whole-paper-cross-review-v1','reviewer':'sol','findings':findings},indent=2)+'\n')

checks=json.loads((HERE/'saved_record_checks.json').read_text())
def esc(s):
    special={'\\':r'\textbackslash{}','$':r'\$','%':r'\%','&':r'\&','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','→':r'\ensuremath{\rightarrow}'}
    return ''.join(special.get(c,c) for c in s)
quotes=json.loads((DRAFTS/'fable_5_2/data/quote_manifest.json').read_text())['quotes']
qs=[]
for q in quotes:
    text=r' \textnormal{[\ldots]} '.join(esc(s['text']) for s in q['spans'])
    label=f"{q['speaker']}, {q['channel']}, G{q['game']} d{q['decision']}, attempt {q['selected_attempt']}"
    qs.append(r'\expandafter\gdef\csname reviewquote@'+q['id']+r'\endcsname{\begin{quote}\small\textit{'+esc(label)+r'.}\par '+text+r'\end{quote}}')
(HERE/'checked_quotes.tex').write_text('\n'.join(qs)+'\n')
rows=[]
for stage,forms in checks['offer_tables'].items():
    for f,cs in forms.items():
        for c,x in cs.items():
            rows.append(' & '.join([stage.capitalize(),{'swap':'Swap','cash_bid':'Cash bid','cash_ask':'Cash ask','other':'Other'}[f],{'author_only':'Proposer only','recipient_only':'Recipient only','both':'Both','neither':'Neither'}[c],str(x['n']),str(x.get('accept_trade',0)),str(x.get('counter_trade',0)),str(x.get('reject_trade',0))])+r' \\')
(HERE/'complete_offer_rows.tex').write_text('\n'.join(rows)+'\n'+r'\bottomrule'+'\n')
rows=[]
for r in checks['necessary']:
    text=r['note'] or r['provider']
    channel='Applied private note' if r['note'] else 'Provider-returned explanation'
    rows.append(r'\Needspace{8\baselineskip}\subsection*{G'+str(r['game'])+' d'+str(r['decision'])+', '+r['model']+'}\n'+r'{\small\textit{'+channel+r'. Full first resolved field.}\par '+esc(text.strip())+r'\par}')
(HERE/'checked_entry_fields.tex').write_text('\n'.join(rows)+'\n')
print('Prepared',len(findings),'exact-passage findings and',len(quotes),'quote definitions')
