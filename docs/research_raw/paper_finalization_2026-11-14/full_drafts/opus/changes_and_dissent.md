# Changes from the 12 November paper, independent judgments and dissent (Opus)

I wrote this draft from the saved records, the 12 November integrated package, the three November 14 input files and all four November 14 reviews and cross-reviews, including Astra's continued-financing argument. I did not open any other author's draft in `paper_finalization_2026-11-14/full_drafts/`.

## 1. The central question changed

The 12 November paper asked whether agents anticipate what their actions make available and whether later behavior realizes that assessment. Its abstract led with "Agents pay fourteen", the ten-action G20 sequence, and the claim that the findings "document prospective financial assessment followed by dependent execution".

This draft asks a narrower question: **when an obligation arrives, what do these agents count, how accurately do they value it, and does the applied action follow the count?** It then asks how the same agents reason about rivals' finances in bargaining. I chose this question because it is the one the evidence answers exactly. Debt feasibility can be checked against holdings, every value an agent states can be checked against the board, and the first-menu choice is observed for all 188 episodes. The title changed to match: *Financial Assessment and Strategic Conduct of LLM Agents in Twenty Monopoly Games*.

## 2. What was removed or reframed

| 12 November text | This draft | Reason |
|---|---|---|
| "Agents pay fourteen" as the headline; "dependent execution" | Payment is reframed as evidence of continuing (Proposition 1) | Continuing valid financing suffices in all 131 payable states |
| "One successful sequence realizes an announced budget across ten actions" | Incident 1 is presented as exact valuation by both players, with a forced end state | D = U* − 14 and every increment exceeds $14 |
| "Thirteen state the subsequent mortgages or an aggregate budget" | Five-way rubric: 5 explicit, 3 ordered, 5 inclusive, 1 tentative, 2 omissions | The old count mixed recognition with inclusion |
| "The initial statements show which resources agents count before choosing whether to proceed" | Removed. Notes are statements generated with the action, and field order is not used | Joint generation |
| "The reproducible result" | Removed | Each state was observed once |
| "The cash-bid difference is negative only when pooled" | Pooled −5.0; within recipients −0.2 to +8.5 | Grok's within-recipient gap is −0.245 |
| Six above-bound starts covered in one clause | Table 5, with every channel in Appendix F | The statement-action analysis needs the contrary cases |
| Selection rule: note when present, otherwise provider field | Both channels printed for all sixteen, plus a JSON supplement | The old rule hid Sol's settlement rationale |
| Middle category label resting on the bound | Label kept, with its justification stated (47 routes, 1 witness, 5 derived routes) | The bound alone does not prove a route |
| Engine variants listed as plain rules | Table 2 contrasts the published rules with the engine | The variants were undisclosed and change what a stop means |
| Eight incidents in the main text | Five in the main text (G20, G15, G2, G7, G13) and three in Appendix H (G19, G20 appeal, G18) | The brief asks for at least five; this keeps the main text within page limits |
| Twelve references | Thirty, organized by construct | Primary-source comparison by construct |
| Appendix F named files without paths | Appendix A gives the full repository paths, commit `863f8ef7`, both run commits and source hashes | Release precision |

## 3. What is new in this draft

1. **First-menu declarations by entry region and system (Table 3).** I proposed this decomposition on 12 and 14 November. The same numbers appeared in the earlier paper as a sentence; here they are the backbone of §3.1.
2. **Development-preserving financing.** This finding is new in this draft. In the 62 debts payable from cash and listed mortgages, 30 players held buildings and 28 paid without selling any. In the 47 sale-requiring payments without released collateral, sales exceeded the residual need by $2 to $94. Fable reported a version of this with a median of $30 over 52 episodes, which includes the five released-collateral payments. I restricted the summary to the 47 no-release payments and got a median of $38. I present it only as a description under one cost ordering, as Astra cautioned. I do not adopt Fable's inference that an oracle would mostly report zeros.
3. **G7 New York negotiation, recast as "bargaining over development budgets".** In the earlier paper, the G7 incident was mainly the bluff. Reading d141 to d145 shows each side computing the other's mortgage-backed building capacity: Sol's "$700 … three houses on each blue with $184 left, while p1 has only $45 before mortgages", Gemini's "$604 … exact $600", and Sol's "can mortgage non-orange assets, so its claimed development constraint is overstated". This is the clearest evidence in the corpus for the strategic financial reasoning the brief asks the paper to emphasize.
4. **Rival liquidity tracking.** Grok's G18 turn-78 note computes every opponent's liquidation capacity against Boardwalk's rent. I offer it as an example, not a census.
5. **Settlement-rule reasoning in Grok's texts.** G17 d396 says "Standard Monopoly rules require bankrupt players to turn over all assets to the creditor", and G19 d224 says "The engine might enforce different rules". These sit beside Gemini's fee motive and distinguish strategic choices about the estate from false budgets.
6. **Payload check over all 338 liquidation prompts.** This confirms that the holdings and menus carry keys and flags only.

## 4. Independent judgments on contested points

**J1. Proposition 1 covers all 131 payable states, and I accept it as a source proof.** I re-derived the entry premises from the original decision records, not from Astra's `record_checks.json`, and reproduced the 108/12/9/2 classes. I checked the two-entry extension against `engine.py`. A cleaner way to state Astra's invariant is R = 32 − (houses held by other players, which are constant during the debtor's liquidation) − (houses locked in the debtor's groups that still hold a hotel). Locked houses increase only when a downgrade leaves a group with another hotel, which is impossible with one hotel per group. So R cannot fall. While a hotel remains, either the bank holds four houses or a free house is listed. The argument is correct as stated. It still rests on one author's extension plus my check, not on four reviews, and the paper says it is not an executed baseline. The configured fallback is itself a valid cash-raising policy, so the proposition covers it too. I deliberately do not print "the fallback would pay 131/131", because readers would take that as a measured score.

**J2. Payment is a consequence, not a separate accomplishment.** This was my RD-4 in cross-review. The paper's measurements are the text, the stop decision, the financing order and text–action agreement. Payment appears only as context.

**J3. The U0 identity belongs in the main text.** Both false budgets equal U0, and several successful texts pass through the same subtotal. This is stated as a description of texts. No mechanism is drawn from it, and the candidate explanations stay unranked.

**J4. Inclusive budgets are weaker evidence about the prerequisite, but they are not empty.** Astra was right that the inclusive texts name sale-first orders (G4 d308 starts with an Illinois sale; G6 orders the Boardwalk mortgage first). The paper says both things.

**J5. G18 d344 is accurate recall of a published rule that the engine does not apply.** I hold this firmly. Calling it faulty recall puts the benchmark's undisclosed variant on the model. I do not extend it into Fable's broader claim that "the agents play by the rulebook". G19's precondition is a false rule, and one case is not a population claim.

**J6. The named-action scan supports only a narrow sentence.** "Every observed conflict comes from Grok, the only configuration whose free text names actions." It is not evidence that other systems never conflict. No 179/188 figure appears anywhere in the paper.

**J7. Bargaining stays exploratory and secondary.** The completion contrast is reported with its composition sensitivity and its interval spanning zero. The paper claims neither an effect nor a null. The 61/74 reading is kept as a separate population.

## 5. Dissent

**D1. From the team synthesis's framing of "selective financing" through G13 alone.** G13 is the clearest single example, but the population-level evidence for selective financing is the mortgage-first regularity (28 of 30). The synthesis did not mention it. I made it a main-text finding because it describes all 62 easy debts rather than one selected case.

**D2. From keeping G20 d327 as the central budget illustration** (Sol, and Astra's original review). I keep it as Incident 1, but labelled as exact valuation with a forced end state, and paired with Gemini's matching creditor estimate. It is the strongest valuation case and the weakest planning case.

**D3. From Fable's preference for three main-text incidents.** The brief requires at least five. I chose five that carry financial content. G7 is reframed around development budgets and G13 around survival bargaining.

**D4. From any reading of the two failures as "premature abandonment" or "planted-number steering".** The paper reports two false budgets followed by declaration. Sol's provider field adds a settlement belief, and the settlement rules were undisclosed. A rate of premature abandonment is not estimable from two cases observed once each.

**D5. From the brief's phrase "selective financing" if it is read as optimal.** I make no optimality claim for G13 or for the mortgage-first ordering. Rent, position and rebuilding are outside the local cost ordering.

**D6. A judgment against the integrated package's own wording.** Its literature notes and the earlier related-work sentence on Guhe and Lascarides said they "study when persuasion and trade restrictions improve game outcomes". I verified that their embargo recipients always comply. The sentence is corrected to say the study measures the value of successful persuasion, not its efficacy.

## 6. Points I could not resolve

- I did not reread the earlier package's incident continuations beyond the spot checks listed in `evidence_map.md`. Those continuations are inherited.
- The 61/74 coding has no human validation, and neither does my coding of the sixteen texts. Claude Opus 5.5 coded texts that include Claude Opus 5.5's own outputs. This is disclosed in Appendix K.
- Whether FinBoardBench's engine enforces "bankruptcy when recovery is impossible", or whether that is prompt text only, remains unverified.
