# Findings and limits: Fable 5.2 complete draft, 12 November 2026

This file states the argument of `manuscript.pdf`, the level each finding reaches, where I dissent, what I corrected, and what I did not do. Every number here is in `data/facts_index.txt`.

## Thesis

The agents state what a move will make possible before they make it, for themselves and for rivals, and their actions agree with those statements. For the agent's own financing the statements are accurate in a set of cases fixed by rule arithmetic. For rivals the statements are as frequent and less exact, and the refusals follow the event of completing a color group and the form of the offer. They do not follow the measured size of the rival's opportunity.

Title: *What a Move Unlocks: Stated Consequences and Actions of LLM Agents in Twenty Monopoly Games*.

I use referee A's five levels once, in the methods: stated, accurate, consistent with the action, sensitive, effective. Each result is tagged with the highest level it reaches.

## Findings

### 1. The decision to quit separates payable from unpayable debts (level 3)

- 188 debt episodes. 131 payable, 56 above every own asset, 1 menu-restricted (G7 Opus).
- At the first menu, agents declared bankruptcy in 50 of the 56 debts above every asset and in 3 of the 131 payable debts.
- 128 of 131 payable debts were paid. 62 needed only cash and listed mortgages, 53 needed building sales as well, 16 needed mortgages that the first menu did not list.
- 67 payments took one action. The median paid debt was 36% of the debtor's asset bound. The 97.7% payment rate says little about difficulty.

The 50 of 56 against 3 of 131 comparison is new in this draft. I computed it after reading the reviews. No other author has reproduced it yet.

### 2. Sixteen debts needed mortgages the menu did not list (level 3, accurate content)

- Fourteen were paid. Two ended in a declared bankruptcy at the first decision (G12 Sol d190, G17 Gemini d234).
- First stored text, my reading: thirteen count the unlisted mortgages before any sale, one raises them as an open question (G20 Opus d291), two leave them out. Both that leave them out are the failures.
- Channel: nine applied private notes, five provider-returned explanations (all five are Opus under action-only recovery). Both failures are applied private notes.
- The liquidation prompt gives no price, mortgage value or sale value, and does not say that selling buildings releases mortgages. The values in these texts are recalled board facts.
- I checked fifteen stated figures against the records. Fourteen are equal. Sol's G2 note says $430 for yellow mortgages worth $400.
- By system: Sol 2 of 3, Gemini 5 of 6, Opus 5 of 5, Grok 2 of 2. By seed block: 4/4, 3/3, 1/2, 1/1, 5/6.
- Gemini counted Park Place and Boardwalk in G5 and left out the same two deeds in G17. Its returned text in G5 shows the sum being revised inside one response.
- Nineteen payments used a mortgage absent from the first menu. Fourteen are the necessary cases. Five were optional (four Gemini in G3, one Sol in G18).

### 3. A completing opening is almost never accepted (count)

- 3 acceptances in 186 opening swaps and cash bids that would complete only the proposer's group. 137 rejections, 46 counters.
- 21 acceptances in 175 for the same forms when nobody's group is completed.

### 4. Swaps are refused and cash bids are countered (association, exploratory)

- Opening swaps rejected: 95 of 116 completing the proposer only, 37 of 72 completing nobody (+30.5 points). Completing both: 34 of 48.
- Opening cash bids rejected: 42 of 70 against 67 of 103 (−5.0 points).
- Counters: 26 of 70 completing cash bids, 20 of 116 completing swaps (+19.9 points, same sign in all five seed blocks).
- Within every recipient the swap gap is positive (15 to 51 points). Within every recipient the cash-bid gap is between 0 and 9 points. The pooled −5 is composition.
- Composition: Grok wrote 36 of the 72 comparison swaps and 15 of their 17 acceptances. 13 of those acceptances answered openings whose text named another action. Without conflicting openings the gap is +22.6 (93/112 against 26/43). Without Grok-authored swaps it is +16.7 (90/108 against 24/36). Standardized by proposer: 16.0, 18.1, 21.5 by weighting.
- Sensitivity of the swap gap: five of five seed blocks positive, leave-one-block-out 28.7 to 33.3, seed-block resampling 24.2 to 35.5, game resampling 13.8 to 47.8. Without Grok-authored swaps: four of five blocks, leave-one-out 9.4 to 22.1, block resampling −3.8 to 31.9, game resampling −2.1 to 37.5.
- Cash-bid gap: leave-one-out −8.3 to −2.3, block resampling −18.0 to 3.2, game resampling −22.9 to 10.7. The paper says the records show no gap and do not show that one is absent.

### 5. What refusals say, and how the systems differ (level 1 to 3, pattern matches)

- Completion or blocking terms: 93 of 95 rejections of completing swaps and 42 of 42 rejections of completing cash bids. Stated reasons do not separate the forms.
- Gemini rejected 62 of 67 completing openings, with reciprocity wording in 28 of 62. Grok rejected 54 of 61, with commitment wording in 38 of 54. Sol rejected 18 of 40 and countered 22. Opus countered 15 of 18.
- These are regular-expression counts. They are not semantic codes.

### 6. Refusal does not follow the size of the rival's opportunity (no level 4)

- Completing swaps rejected by the proposer's post-trade house capacity: 4 of 8 (none), 26 of 33 (one or two), 42 of 48 (three to five), 23 of 27 (six or more). Cash bids: 2 of 3, 13 of 19, 7 of 20, 20 of 28.
- At list price the completing swaps offer the recipient more (median $170 against $80). Among swaps that favor the recipient at list, 86 of 103 completing ones are rejected against 24 of 48.
- Both checks are crude. List price ignores blocking value, which is the thing in question.

### 7. Eight incidents

Main text: G20 payment, G15 refusal, G2 pricing, G13 insurance pitch. Appendix A: G7 bluff and financed sale, G19 correction, G20 appeal, G18 withdrawal. All eight have context, exact quotations, channel labels, receipt checks where a message was public, a reading and a continuation. The two failed sums (G12, G17) and the G5 contrast are quoted inside the finance result.

Details added or corrected against the previous paper:

- G15. One turn before Sol's offers, Opus told the table not to hand Sol the last piece of any set. That message is in Grok's prompt at d169. Gemini also refused Sol that turn.
- G2. Grok bid first and Sol's $450 was a counter to it. Opus held $845 when it bid $325.
- G7. Sol's note figures ($184 left after three houses, Gemini at $45) are correct. Gemini offered $520 before paying $700.
- G13. The seller's own note uses 4/36. Its public message says 5/36.
- G18. Two players remain, so the estate has no later use. No Opus text from d421 to d461 mentions inheriting, an estate or a creditor. Text returned with the d431 assurance already says more cash would help the opponent last longer.
- G20 payment. Five of the eight mortgages were on deeds absent from the first menu. Gemini's private estimate of Sol's liquidation value includes them.

## Where I dissent

1. **From the integrated paper, which carried my title.** "Bargaining over a rival's next move" named an interpretation the swap and cash split cannot carry. The split stays as an exploratory association with its composition and ranges beside it. It is not the thesis.
2. **From making fourteen of sixteen the headline, which Opus and I argued for on 11 November.** Astra's objection holds. Sixteen cases with two failures, surfaced by a referee, cannot carry a paper alone. I lead with the question and put the full-debt comparison (50 of 56 against 3 of 131) in front of the sixteen.
3. **From referee B on three points.** The offers are not "contaminated". They were real offers that recipients answered. "A loop pays 131 of 131" is an unexecuted prediction and I do not print it. An unfinished byline does not show that no human did the work.
4. **From referee A on the baseline.** A reactive baseline is not the only way to calibrate the finance result. The partition by first-menu sums does it from stored records. A loop cannot quit, so it would not face the decision where both failures occur. I say in the limitations that the baseline is untested.
5. **From the earlier position that the paper should print no ranges.** I print four kinds and state their target.
6. **From an assumption in the charter and in my own initial position.** I expected seed-block resampling to be the conservative range. It is narrower than game resampling for the swap gap (24.2 to 35.5 against 13.8 to 47.8), because the five blocks are more alike than the games inside a block. I report both and call neither a confidence interval.
7. **From the previous paper's secondary results.** Asking-price medians, construction receipts and first-estate concentration are not in this manuscript. Both referees found them weakly identified and I found nothing that strengthens them. Holder cash is kept as one appendix paragraph with its confounds.

## Corrections applied

| Item | What the manuscript now says |
|---|---|
| G18 motive | Withholding survival cash from the last opponent. No inheritance statement exists. |
| Replay | Both stored comparisons named: full event stream (50,918 events, nothing excluded) and state-relevant events (24,506 events, four LLM event types dropped, identifiers and time renumbered). Read, not rerun. |
| Grok tool choice | "required" for Grok and "auto" for the others, read from 8,687 saved request records and from source at both run commits. |
| 61 of 74 reason codes | Stated as a disjoint population (38 recipient-only, 36 both). Not used to explain the form result. |
| Cash-bid contrast | Estimate and ranges reported. No claim of absence. |
| Ten actions | Described as execution of an aggregate budget with refreshed menus. Not ten steps of lookahead. |
| Feasibility | A sufficient sum is not a plan. The three payment sequences are inherited. |
| Reproducibility | Repository URL, source commits, seeds, game map, package entry point. |
| Response conditions | Opus recovery and Grok conflicts in the setup, with counts. |

## Limits

- One cohort: five seeds, four rotations, one roster. No ranking.
- Every contrast was chosen after the games were inspected. Nothing here is confirmed on new games.
- No value reference, no baseline, no human annotation.
- The readings of the sixteen texts are mine. Three other assistants read them on 11 November and singled out the same tentative case. That is agreement among model readers.
- Pattern matches are crude.
- The three payment sequences, the G7 menu search, the two replay comparisons and the 74 reason codes are inherited.
- Opus and Grok ran under altered response conditions that reached every player.

## What I did not do

- No game, engine run, replay, baseline, synthetic state, branch, rollout, provider probe or model query.
- No edit outside `full_drafts/fable_5_2/`. No commit or push. No subagent.
- I did not open any other author's 12 November draft.
- I did not recode the 74 rejections.
- I did not recompute the asking-price, construction or first-estate analyses of the previous paper.

## Literature: exactly what was read

No source was read in full for this draft. Two were opened on 12 November through a summarizing fetch tool. The rest rely on readings recorded on 11 November in `../../../paper_revision_2026-11-11/full_drafts/fable_5_2/literature_inspiration.md`.

| Citation | What I read | When | How the paper uses it |
|---|---|---|---|
| Valmeekam et al. 2023, PlanBench | NeurIPS proceedings abstract page through a summarizing fetch tool: title, authors, venue, and a summary of the abstract with one short excerpt | 12 Nov | One clause in the introduction and two sentences in related work, limited to the abstract |
| Jehiel, Moldovanu and Stacchetti 1996 | RePEc record through the same tool: bibliographic data and the first sentence of the abstract | 12 Nov | One clause in related work, limited to that sentence. No theorem is cited |
| Jehiel and Moldovanu 1995 | Pages 1321 to 1323 of the article | 11 Nov | One clause: externalities can delay agreement |
| Guhe and Lascarides 2014 | Pages 2, 4, 5, 6 and 9 of the PDF | 11 Nov, cross-review | Prior symbolic-agent embargoes with controlled outcome comparisons |
| Cosentino et al. 2026 | arXiv abstract and most of the HTML version through a fetch tool | 11 Nov | Modeling a counterpart is not using the model |
| Bianchi et al. 2024 | PMLR page and abstract | 11 Nov | Tactics change payoffs |
| Lewis et al. 2017 | arXiv abstract | 11 Nov | One clause of background |
| Li et al. 2026 | arXiv abstract and most of the HTML version | 11 Nov | Messages checked against simulator state |
| Wu et al. 2026, Hu et al. 2026 | arXiv abstract and HTML through a fetch tool | 11 Nov | Nearest Monopoly benchmarks |
| Müller and Müller 2026 | arXiv abstract | 11 Nov | Scripted agents and resource discipline |
| Anthropic 2026 documentation | Full page as returned | 11 Nov | Appendix E: a documented refusal category that the saved responses do not name |
| Turpin et al. 2023, Lanham et al. 2023 | Not re-read. Inherited entries | | Stated reasons need not reflect the process |

I cite nothing for a claim beyond what the row says I read. Venue rules, page limits and acceptance judgments in the two referee reports are not used.
