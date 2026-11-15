# Astra's complete-paper comparison, in progress

This is root-author work, not a delegation summary. Astra wrote and froze a complete independent 23-page paper before opening the new Sol or Opus drafts. I have now read Sol's complete manuscript, conduct, temporal/discussion and appendix sources, and Opus's complete main and appendix prose, generated response/block/game/cash/initiation tables, new quote definitions and analysis scripts. I have read both handoffs. Fable 5.2's completed draft has not yet arrived, so this is not the promised all-four comparison or an integration decision.

No draft is edited by this review. No engine, game, model evaluation, policy pilot or synthetic test is run. The accompanying checks only read retained ledgers and original source fields.

## Working judgment

All three completed drafts support a behavioral account of bargaining, executable development, liquidity and creditor inheritance. This is a more coherent scientific object than the old audit-method framing. The quality difference is not mainly the thesis. It is the choice of positive evidence, the precision of its interpretation, and the amount of repeated defense surrounding it.

Sol has the clearest continuous economic argument and careful finance distinctions. Astra has the most compact main architecture and an economical construction exhibit. Opus contributes the most useful new evidence: what counteroffers change, configuration heterogeneity, and two new chronological incidents. None is ready to become the integrated version unchanged. In particular, positive framing must not turn into stronger facts than the data establish.

## Findings requiring correction before integration

### O1. The new G2 quote contains a substantial uncorrected financial error

`opus/sections/opus_quotes.tex` quotes Sol's G2 d124 note: "$520, enough for nine yellow houses immediately." Yellow houses cost $150, so nine cost $1,350, and $520 alone buys three. Opus's incident interpretation presents this as computation of the rival's building capacity without identifying the error. The quote remains exact and should remain unaltered. Its interpretation must distinguish correct residual cash from the false building-capacity claim.

This strengthens the paper's scientific substance: the agent expressly considers a rival's construction but miscalculates its cash-based scale. It does not establish the maximum available through collateral or the optimal price. `new_quote_checks.json` independently verifies all ten new source spans. All six quoted public messages, including the terminal refusals omitted by Opus's five-item delivery script, appear in the relevant counterparty's next canonical request.

### O2. The Opus construction shortfall is overstated

The abstract says most of one configuration's first-window shortfall comes from defaults. Its conclusion says one configuration "lost most of its development" to defaults. Among Opus's fifteen trade-completed groups, seven build; the eight residuals contain five never-buildable windows and three defaults. Thus defaults are not most of the whole-window shortfall, and lost total development is not measured. In the entry-buildable subset, both nonbuilds are defaults. Use the appropriate population explicitly. Sixty-one reachable defaulted purchase multisets cannot be converted into a lost-development or lost-income total.

### O3. Not every text channel disagrees with the applied action

The G12 reading, conduct synthesis and discussion repeatedly say the action contradicts "every text channel" in G12 and G19. Their public messages support the received bankruptcy or proposal. Assistant content and the attached private note oppose it. The strong supported finding is this specific conflict, not unanimous text against action. Astra and Sol already preserve the channel distinction.

### O4. Feasible allocation, valid expression and valuable investment remain different

`opus/sections/construction.tex` calls a reachable allocation "sound" and says it "cannot be expressed" in the interface and "earns nothing." The allocation can be expressed by legal ordering; the submitted encoding failed. Feasibility does not establish investment quality, and immediate default does not establish zero later income. Replace with: "The configuration failed to execute a requested allocation that was reachable in the same state after reordering." The recovery-table caption also needs the G2 d129 exception: its invalid plan precedes its refusal, while sixty other Opus defaults follow refusal recovery.

### O5. Mortgage-only subtotals are not the displayed menu

The new observation that cash plus immediately displayed mortgages falls short in all three payable eliminations is useful. However, Opus's discussion says the "displayed options understated finance." The menu also displays sales. The understatement belongs to a mortgage-only subtotal, not necessarily to the menu or information supplied. G12 d249's survival witness uses sales alone. Sol's two collateral-omission cases and Grok's received-call contradiction must stay separate.

### O6. Refusal occurrence is not recovery occurrence

There are 1,605 refused attempts in 1,605 affected decisions: 1,604 first-attempt refusals plus G2 d129's refusal after an invalid first attempt. The latter does not trigger another action-only recovery. Opus's configuration table incorrectly labels 1,605 as decisions using refusal recovery. Its appendix correctly describes the exception. Use 1,604 first-refusal recovery chains where that is the intended quantity. Sol's count of affected decisions is not erroneous.

### O7. Counteroffer caption and terminology need repair

The counter table says omitted cells have fewer than two counters, then lists omitted cells of six and five. State exactly which cells are shown or display the full transition table. "Gives the counterer nothing" in the abstract/handoff must read "does not complete a group for the counterer"; these trades can transfer cash or other assets. "Author completion" must say "author-only completion" when referring to the 289-offer denominator.

The script originally tests whether any group completes rather than whether the same group remains. My independent retained-ledger check confirms the distinction happens not to change this result: all 92 preserve the same original author's newly complete group. The recheck also finds 79 of the 88 original-author-only counters preserve the entire noncash bundle and increase the counterer's cash. The other nine alter noncash terms, so their cash changes must not be called pure price changes. All 88 have the same cash delta before and after transfer-interest accounting. See `counteroffer_checks.json`.

### O8. A useful new incident is not evidence of a population concentration

Opus qualifies its selected transcripts in several places, but the contribution heading "conduct concentrates near it" and the recommendation to start audits at pressure points remain stronger than a purposive selection establishes. Describe the selected cases' economic stakes. Do not present concentration or a validated review-priority rule as a finding. Likewise, G18's deterioration and stated economic reason do not prove the underlying value changed because of distress. Attribute that reason to Opus's explanation.

### O9. A few broad negatives need narrower scope

"The records contain no probability forecasts" is too broad, since movement-probability statements plainly occur. Scope it to the coded opponent-prediction targets and check the coding definition. A same-response note favoring purchase means the record does not establish deliberate abandonment; it cannot prove that deliberate change is impossible. Absence of a standing-offer object establishes no engine-enforced commitment, not the absence of every conceivable conduct norm.

### A1. My own abstract and bargaining interpretation need the new heterogeneity

Astra's independent paper states the pooled rejection contrast and differing response styles but omits the within-configuration acceptance reversal for Opus. Add that exception in the main result. Do not replace it with a new universal "rival sensitivity" claim: charging more in counteroffers occurs in every completion category and is not a specific rival-completion premium.

My sentence "Recipients consequently do not respond to incoming cash alone" draws too much from different group medians. The examples and coded stated reasons establish some explicit attention to relative positions; the medians alone do not. Link that interpretation to the textual evidence instead.

### S1. Sol's causal verbs and literature labels need small corrections

"Offers ... induce counters" should be "receive counters." Its discussion of economic sequence need not be described as an identified "causal order." The finance and current-debt interpretation are otherwise especially careful. Calling Empty Commitments' ontology "validated" needs a precise primary-source basis or should be removed. A count of author-only rejection cannot by itself establish relative-gain aversion.

### P1. Every draft still contains research-process language unsuitable for a finished paper

Remove references to "the user's" questions, screenshots, a parallel author who will check later, and the no-new-evaluation instruction from scientific exposition. Retain truthful information about what analyses were performed, retrospective selection, research assistance and inherited checks in a concise reproducibility statement. The complete working history belongs in the evidence archive. The main paper should make sense to a reader who has never seen this conversation.

## What to carry forward

1. The complete offer-response table and distinct responder styles, followed by counteroffer content. Retain exact denominators and the Opus exception. Do not headline only a weak sufficient-completion refutation or a uniform causal rival effect.
2. Sol's acquisition-to-development-to-finance-to-creditor narrative, with Astra's compact two-population development chart. Keep the whole-window and entry populations visibly separate.
3. Positive financing successes next to the payable errors and hotel lock. Most current debts are unpayable; that is not a judgment about how agents arrived there.
4. The G2 and G11 additions, subject to the G2 arithmetic correction, offer stronger economic continuity than seven incidents located entirely in a separate conduct section. G2 connects rival-price reasoning, a bluff, reversed trading direction, construction, salvage and estate transfer. G11 shows correction followed by rejection of a genuinely completing offer.
5. Tentative seven main incidents: G2, G11, G12, G13, G18, G20 financial denial and G19 correction with acceptance. Place each near the result it illuminates. G3, G7 and G20 disclosure remain inspectable appendix contrasts. This is a proposal for the all-four debate, not a settled selection. G7 is cleaner as an isolated bluff, and a shorter G2 can omit its private capacity error only if the interpretation no longer credits that computation.
6. Keep a concise map of all eight motivating questions plus A–C. Unanswered constructs remain explicitly unanswered. Remove duplicate narrative coverage and extensive future-experiment designs. Temporal behavior can occupy a compact section with a positive achieved target and a well-specified execution conflict.
7. Reproducibility should show the public repository/checkpoint and exact source artifacts. It should not consume the scientific narrative or imply independent semantic validation. Keep the original outlines and drafts unchanged.

## Checks completed in this review so far

- Full source reading for Sol and Opus prose as described above; Astra is my own frozen complete draft.
- Independent, peer-informed join of all 394 counters, using actor reversal, exchange continuity, group identity, noncash bundle equality and interest-adjusted cash checks.
- Recomputed the four responder acceptance cells, including Opus's 7/52 versus 5/42 reversal.
- Ten new quote spans, file and field hashes checked against original G2/G11 decision records.
- All six quoted public messages checked as complete strings in the actual counterparty's next canonical request.
- Read G2 d129's original attempt chain to resolve the refusal/recovery count distinction.
- Checked that the 397 estate-deed rows are player transfers, so Astra's player-creditor denominator is correct. The bank estate has no deed row in this ledger.

Not yet performed: all-four comparison, a new integrated build, final cross-author debate, or independent re-execution of any historical feasibility audit. No claim of final-package approval is made.
