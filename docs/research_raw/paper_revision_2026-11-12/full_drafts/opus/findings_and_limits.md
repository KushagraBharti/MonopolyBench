# Findings and limits: Opus independent draft

## Thesis

When these agents wrote down, before acting, how an action would change the options available to themselves or to others, the applied action followed what they wrote, whether the statement was right or wrong. The exception is Grok, whose applied calls sometimes contradict its own text. The sharpest evidence concerns the agent's own changing menu. The bargaining evidence concerns rivals' options and is broader but weaker.

## Findings, with the level each reaches

Levels: stated, accurate, consistent, sensitive, effective. Nothing reaches sensitive or effective.

1. **Necessary released collateral (accurate, consistent).** In 16 of 188 debts, cash plus every building's salvage plus every listed mortgage falls short, and only mortgages released by selling buildings can close the gap. Agents pay 14 (Gemini 5/6, Opus 5/5, Sol 2/3, Grok 2/2). In 13 of the 14 payments, the first-decision text states the released mortgages or a budget including them (9 applied notes, 4 Opus provider-returned texts). The fourteenth raises them as an open check. In 12 of the 13 explicit texts every stated amount is correct. Both bankruptcies (G12 Sol d190, G17 Gemini d234) follow totals that omit the released mortgages and declare at the first decision.
2. **Most debts were easy.** 62 of 131 payable debts needed no sale and all were paid; 67 of 128 payments took one action; median debt is 36% of the own-asset bound. The decision that needs foresight is whether to stop.
3. **Execution length is not dependency depth.** Tier N sequences take 2–10 actions with one kind of prerequisite (clear the group's buildings, then mortgage). G20's ten actions follow a stated budget and one ordering rule, not an ordered ten-step plan. Its stated $14 remainder is exact. The creditor's $1,414 total is right but its parts are off by $25 in opposite directions.
4. **Released collateral is used beyond necessity.** 19 payments use 33 mortgages absent from the first menu; 14 are necessary cases and 5 are optional.
5. **Opening-offer form pattern (population description, level not assignable).** Proposer-only swaps are rejected 95/116 against 37/72; cash bids 42/70 against 67/103. The swap sign holds within Sol, Opus and Grok as proposers and within all four recipients, and in 5/5 seed blocks. The size depends on proposer mix: 30.5 points overall, 22.6 without conflicting Grok openings, 16.7 without Grok-authored offers, and 16.0–21.5 when proposer-standardized. Two-stage resampling for the last version spans −10.0 to +40.9. The cash-bid interval (−26.5 to +11.4) does not establish that completion is irrelevant to cash bids.
6. **Reasons do not separate the forms (stated).** Rejections of completing swaps and completing cash bids mention completion (93/95, 42/42) and building (83/95, 35/42) alike. What differs is the action: cash bids draw counters (26/70 against 20/116), often with the same deeds at a higher price. The 61/74 rival-consequence codes come from a disjoint population (recipient-completing offers) and cannot explain the headline cells.
7. **Two alternative explanations narrowed, neither removed.** At list prices, completing swaps offer recipients more than comparison swaps and are still refused more. Rejection does not rise with the proposer's post-trade house budget. Both checks are crude and post hoc.
8. **Incidents.** G15 and G7 compute rival building cash correctly and act on it (accurate, consistent). G2 prices against the buyer's budget with a wrong house count (stated, consistent). G19 corrects a false premise while accepting good terms (accurate, consistent). G13 omits an available mortgage in public and admits it privately (stated; accurate in private; no persuasion effect identified). G20's public appeal is followed by its author's own refusal (stated, consistent). G18 withdraws an assurance from the last opponent to avoid funding its survival, with no inheritance language (stated, consistent).
9. **Configured systems.** Opus played 1,604 of 1,696 decisions on the recovery prompt after a single repeated ToS refusal message. Grok ran with `tool_choice: "required"`, and 139 of its 1,068 content-naming responses conflict with the applied call. These conditions changed the offers other agents faced.

## Limits

- One cohort of twenty games, five seeds, one cyclic seat order, fixed roster. No ranking of models; 8/7/3/2 wins are confounded with seat and seed.
- Both main contrasts were identified retrospectively. Resampling describes spread within the cohort. It does not confirm a selected hypothesis, and recomputation is not replication.
- Text classification is one LLM reading; the 61/74 codes are earlier LLM readings. No human annotation.
- No baseline policy, value reference, counterfactual rollout or matched-state test. Nothing shows a choice was good, that a reactive liquidation policy would fail, or that recipients respond to rival opportunity as such.
- Recorded text is what systems returned, not how they computed. Opus's text is provider-returned reasoning under recovery.
- Inherited without rerunning: offer-ledger reconstruction, 61/74 codes, three payment witnesses and the G7 menu search, historical replay executions, fourteen paired histories, cost and token accounting.
- The analysis package and the ledgers it reads live in untracked local folders, not in any commit.

## What would test these findings (not done; outside this charter)

- A fresh cohort with the tier N and form definitions frozen in advance.
- Matched negotiation states that hold the recipient's offered terms fixed and vary whether the proposer can build.
- A specified reactive liquidation policy run on the stored debt-entry states, to calibrate difficulty.
- Human annotation of the sixteen first-decision texts and the 74 coded rejections.

## Dissent recorded

- Against the 11 November title "Bargaining over a Rival's Next Move": the form pattern cannot carry that interpretation because reasons do not differ by form, the size depends on proposer mix and no sensitivity was measured.
- Against my own 11 November recommendation to keep about three incidents: the charter's eight are retained, each with one job and a level, at about 1,300 main-text words in total.
- Against any reading of 128/131 as difficulty evidence, and against the inline review's untested "a loop pays 131 of 131."
- Partial dissent from Fable's 11 November phrase "refusal triggered by completion": completion was not manipulated, so "triggered" is causal. The draft says "completion is usually met with refusal in a swap and with a higher price in a cash bid."
- Against calling the comparator swaps "giveaways": list price ignores mortgages, complementarity and blocking value.
