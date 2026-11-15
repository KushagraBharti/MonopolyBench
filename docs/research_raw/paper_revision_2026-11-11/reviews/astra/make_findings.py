"""Record exact frozen-draft passages for the whole-paper cross-review."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
items=[
('AR01','high','astra/sections/discussion.tex','executed multi-step reasoning',
 'Applied financing sequences establish successful execution, not an internal reasoning algorithm.',
 'Use successful multistep financing. Preserve all positive payment counts.', 'verified action census; cognitive interpretation unmeasured'),
('AR02','medium','sol/sections/bargaining.tex','thirty-four common-positive labels',
 'The agreed positive keys include 21 G1 and 10 G15 rows, totaling 31. Thirty-four is a different sample count.',
 'Use 31 of 61 agreed codes; retain the 61/74 and 27/38 results.', 'verified retained-code join'),
('AR03','medium','astra/sections/bargaining.tex','thirty-four records come from G1 and G15',
 'The preceding subject is the agreed 61, so this wording mixes denominators in my own draft too.',
 'Use 31 of the 61 agreed codes, or explicitly name the 74-record population if retaining 34.', 'verified retained-code join'),
('AR04','high','opus/sections/discussion.tex','The quantities the agents cite do not organise',
 'Cash bands are not an equivalence test or complete measure of executable development; observed rejection is 100/134,32/42,6/11.',
 'Do not claim responses lack calibration or use a categorical rule. Present the exploratory cash table with its limits or omit it.', 'verified tabulation; proposed mechanism not established'),
('AR05','medium','opus/sections/bargaining.tex','Asking prices rise, bids do not',
 'Buyer bids differ by configuration and filter. Pooling is not a common directional result.',
 'Use higher asks in descriptive strata, mixed matched comparisons, and heterogeneous buyer bids.', 'verified pricing tables and seven matched overlaps'),
('AR06','medium','opus/sections/setup.tex','Prices and rents appear only in purchase and auction prompts',
 'Purchase prompts supply those fields; auction prompts supply group. Surrounding prose already gives the correct distinction.',
 'Correct the table once; keep full information fields in the appendix.', 'source contradiction; canonical census inherited and compared'),
('AR07','high','fable_5_2/manuscript.tex','Until They Need the Cash',
 'Low cash is not demonstrated financial need, and most low-cash completion requests are countered rather than accepted.',
 'Use cash-pressure or resource-dependent bargaining in the title; report 17 rejects,44 counters,8 accepts out of69.', 'independent old-ledger reproduction'),
('AR08','medium','fable_5_2/sections/liquidity.tex','general effect of needing money',
 'The observed cash association does not identify an effect or inability to finance elsewhere.',
 'Say rejection is also associated with holder cash for noncompleting requests; distinguish countering, acceptance and cash need.', 'independent cash-band and comparator counts'),
('AR09','medium','fable_5_2/sections/liquidity.tex','The sharper evidence follows a pair through time',
 'The fourteen sequences condition on settlement, and reciprocal deed terms change in nine of them.',
 'Name the directed group-pair unit, the selection and changed terms; keep13/14 cash declines as trajectory evidence.', 'all148 pairs and14 sequences independently reconstructed'),
('AR10','high','fable_5_2/sections/conversion.tex','Sales are not independent',
 'Player-game categories overlap: G17 Sol is in both. The43 exchanges also include two holders paying net cash rather than receiving proceeds.',
 'Use completion exchanges as the unit; disclose overlap. A cash-proceeds analysis uses41 positive-net-cash exchanges (9/13 vs1/28). Keep the association supporting.', '43 construction rows checked against canonical events; cash direction from old ledger'),
('AR11','high','fable_5_2/sections/conversion.tex','The difference in rent does not come from exposure',
 'Similar aggregate landing rates and durations do not remove group quality, landing timing, opponent count or state differences.',
 'Report the observed exposure measures and realized rent per landing without an exhaustive or causal explanation.', 'source and exposure-table comparison; causal decomposition not measured'),
('AR12','medium','fable_5_2/sections/discussion.tex','higher in every coarse cut',
 'The manuscript itself reports block exceptions and heterogeneous configurations; matched cases are mixed.',
 'Name the supported strata and exceptions; do not summarize all cuts as uniform.', 'author tables inspected; seven matched overlaps independently reconciled'),
('AR13','medium','fable_5_2/sections/discussion.tex','so no general bias toward agreement appears',
 'Observed acceptance rate lacks a decision-value or psychological baseline; selection of proposals also matters.',
 'State that most recorded offers are countered or rejected. Leave agreement bias unmeasured.', 'interpretation of known full response census'),
('AR14','medium','fable_5_2/sections/discussion.tex','Here the natural buyer of a completing deed',
 'A below-list cutoff is not a fair-value or forced-sale measure; the constrained-natural-buyer mechanism is not tested.',
 'Use fire-sale literature only as conceptual context with the mismatch stated, or omit it. Do not call above-list sales evidence against its prediction.', 'primary AEA abstract directly read; source theory not empirically tested here'),
('AR15','medium','fable_5_2/sections/discussion.tex','Our records add a liquidation menu',
 'FinBoardBench also allows liquidation. Feature absence is not established by the cited comparison.',
 'Describe the additional trajectory analysis and artifact detail rather than implying the comparator lacks liquidation.', 'earlier primary comparator read; no new implementation audit'),
('AR16','medium','fable_5_2/sections/default.tex','Estates also end most of the stand-offs',
 'The85 records are directed group-pairs; estate completions are reused and37 of58 outcomes are terminal.',
 'Describe pair fates, split21 continuing-play and37 terminal, and avoid58 distinct causal resolutions.', 'unit and algorithm read; no independent fate-event recount in this pass'),
('AR17','medium','fable_5_2/sections/default.tex','and all four systems do it well',
 'Strong local payment success is supported, but it is conditional on actual menu-supplied financing and demonstrated ability to pay.',
 'Retain128/131 prominently and scope it to the observed task. Do not infer general financial rationality.', 'allfour debt episode sets reconciled;3witnesses inherited'),
('AR18','medium','opus/sections/discussion.tex','A coherent reading is that the agents apply a categorical rule',
 'A possible interpretation is subsequently called the same demonstrated separation as a controlled study. The present records do not test this mechanism.',
 'Use the controlled study as prior motivation; state the present behavior without identifying a generic cognitive routine.', 'primary Cosentino v1 read through design/results'),
]
out=[]
for ident,severity,rel,needle,issue,resolution,scope in items:
    path=BASE/'full_drafts'/rel
    lines=path.read_text().splitlines()
    matches=[(i+1,l) for i,l in enumerate(lines) if needle in l]
    assert matches,(ident,needle)
    line,passage=matches[0]
    out.append({'id':ident,'severity':severity,'path':str(path.relative_to(BASE)),
                'line':line,'exact_passage':passage,'issue':issue,'proposed_resolution':resolution,
                'verification_scope':scope,'evidence':['review.md','delivered_comparison.json','fable_comparison.json']})
(HERE/'findings.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(out),'exact-passage findings')
