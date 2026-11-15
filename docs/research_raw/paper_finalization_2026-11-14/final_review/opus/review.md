# Final whole-paper review of the integrated candidate (Opus)

**Reviewed:** the integrated candidate, PDF SHA-256 `e5c44bebfb1d6b0b7c434d875261be63b11e4c6457396ee97596457a0c840dae`, pinned with all 2396 candidate and draft files by manifest `a362c4c6…885e269`. The pins were checked before and after this review, along with the November 12 historical pin (84/84).

**Scope read:** the brief, the final-review brief and the integration criteria; all four complete frozen drafts with their handoffs; and the whole integrated package (main text, supplement, casebook, all sixteen channel prints, tables, figures, README, evidence map, tools and the new data files). I formed `initial_position.md` (SHA-256 `fe4f1e14…cbf1ca2`) before opening `INTEGRATION_DECISIONS.md`. I read no other reviewer's final-review folder.

**Method:** source reading and arithmetic over the saved records; quote checks; and document builds confined to this folder. No game, engine import, replay, policy run, state search, synthetic case, provider call or judge call.

## 1. Verdict

The integrated candidate is a coherent, accurate observational paper about financial assessment and strategic economic conduct. It is ready for release once five local clarifications are made (M1–M5 below). Each fix is a sentence or a clause, and none requires restructuring. I found **no factual blocker**. All core counts I recomputed from raw decision logs reproduce exactly.

The main text ends on page 7 at normal 10 pt, so it is well inside the nine-page ceiling. The supplement is complete and legible. A static rebuild of the shipped sources in my own folder reproduces the pinned PDF's extracted text exactly. The copied verifier passes on that rebuild: 23 displayed quotes and 29 focal fields match canonical sources, and there are no diagnostics.

## 2. What the paper establishes, and whether it holds

**The interpretive move is right and well placed.** Section 3.1 and Appendix C show from source, under stated conditions, that any uninterrupted sequence of valid cash-raising actions pays in all 131 payable entries. The paper then moves its evidential weight onto what agents count, which assets they keep, whether they stop, and how text relates to the applied call.

I checked the proof against the engine routines and the recorded entry holdings.

- The invariant Q and the decreasing measure are correct for single sales, hotel downgrades, mortgages and valid bundles.
- The classes cover every entry: 108 hotel-free, 12 where cash plus listed mortgages suffice, 9 with stock for every downgrade, and 2 with recyclable stock.
- The two-entry R = B + H argument is sound for one hotel per hotel-bearing group. R starts at 8 in both G3 entries.
- The added bundle paragraph is correct. Bundles are validated only on the final state, and each unit operation leaves R unchanged or raises it.
- Engine and board data are byte-identical at both run commits (`122edf5f…`, `fc30829e…`).

The text keeps the result conditional and separate from asset selection, valuation and internal planning: "a source-based result, not a measured policy run". That is the correct calibration.

**Positive content is substantial and correctly bounded.** The paper preserves:

- G13's selective route under slack;
- G20's exact \$1,414 valuation with a forced end state, with the note/explanation attribution now correct (the explanation's components do sum to \$700 salvage and \$665 mortgage);
- G5's in-response revision;
- five explicit dependency statements and three ordered routes;
- the 28/30 development-preservation pattern;
- G15's sustained blocking policy;
- G2's buyer-specific pricing;
- G7's bluff and two-sided budget bargaining;
- G13's estate-based sale.

Contrary evidence is present without taking over: both false budgets as correct sums over incomplete inventories, the payable Grok declaration, all six above-bound starts, the composition sensitivity of the bargaining contrast, and undisclosed rule variants. This balance is the paper's main strength relative to earlier rounds.

**The selected-field rubric holds up.** I read every channel of all sixteen first responses. No non-selected channel would move a case into a stronger category, so the 5/3/5/1/2 split also holds under an all-channel reading. Fable's frozen draft coded it that way independently and got the same split. G6 d185 and G17 d254 sit at the inclusive/ordered boundary, and G18 d313's provider field ("After selling the buildings, I could mortgage Park Place") is the closest explicit/ordered call. The integration's choice to define the rule as the selected field and print everything else is correct. The robustness is worth one clause (O6).

## 3. Priority checks from the final-review brief

| Check | Finding |
|---|---|
| 131-state continuation stated as a conditional source result, separate from selection, valuation and planning | Yes. Correct premises, exclusions stated, and no "fallback would pay 131/131" score. Optional: the third class is asserted in one clause; O4 gives the one-line stock argument. |
| 28/30 defined and counted correctly; interpretation descriptive | The count is correct: 30 owners in the 62, 28 with no sale, both sellers Opus, each selling one States Avenue house. **Material (M1):** in G7 d318, one of the 28, the menu offered no building sale (one hotel, two bank houses), so "these choices preserve development" overstates by one case. Among debtors actually offered a sale, the pattern is 27 of 29. "Preference" is more motive-laden than the descriptive scope the paper promises. |
| Selected-field categories, all channels, disjoint 61/74 population clear | Rubric and channels: yes. 61/74: the population is disjoint and counted correctly (38 recipient-only + 36 both; 27 + 34 positives). **Material (M3):** the two readings were not blind to each other (the shipped comparison file records "first-row exposure"), and the 74 are concentrated (G1 22, G15 12). The main text says only that the readings "agree". |
| G7 richer budget sequence source-faithful; other incidents keep their economic meaning | Yes. I traced d139–d152 in the raw log. Every figure checks (\$184, \$604, \$45, \$450, \$95), the three new quotes are exact substrings, and the counter reaches Sol's next prompt. The other seven incidents keep their economic continuations in the casebook. Optional (O1) adds the strongest omitted positive insight (§6). |
| Whole-population and contrary evidence sufficient without overwhelming | Yes. The complete first-action table is in the supplement, and the six starts and G12 d249 are in the main text with an appendix. Optional (O3): the main text never references Table 13. |
| Literature locates the contribution accurately, without padding or novelty claims | Mostly. FinBoardBench, reachability, false impossibility, menus, counterfactual tasks, negotiation and Catan are accurate. I re-verified Cattle Trade and DECE. **Material (M4):** the brief explicitly requires memory and statement/action literature, and the integrated paper cites neither. Explanation-faithfulness work appears only in §2. |
| Release buildable and inspectable; actual hashes; static compilation versus original-record verification | The static build works and is portable: identical text, 29 pages. The README separates the static build from record refresh. **Material (M5):** the artifact appendix gives both commits without mapping games to them, and omits the engine and board hashes that identify the implemented rules. Hygiene: the README heading says "finalization in progress"; eleven unused `sections/*.tex` files ship in `release_manifest.json`; the PDF metadata author and title are empty (O5). The provisional zip and the stale `qa/portability.json` (28 pages) are known packaging steps, not scientific gaps. |
| Main paper within nine ordinary two-column pages; supplement legible | Yes: 7 main pages plus about 1.3 pages of references. With all of M1–M5 and O1–O6 applied, my amended build still ends the main text on page 7, with no warnings. |

## 4. Findings

`findings.json` gives exact passages and evidence for each.

### Factual blockers

None.

### Material

- **M1, development preservation as "choice".** See §3. Replacement text is in `replacement_prose.tex`.
- **M2, named-action observability.** "Explicit action naming is much more observable in Grok's content" implies nonzero observability elsewhere. In the raw liquidation records, assistant content names a liquidation action in 27 of 56 Grok decisions and in none of the other 282: Sol 0/93 and Gemini 0/89 with no content at all, and Opus 0/100 with content in 19. The exact statement is that the scan observes Grok only. Main text and supplement.
- **M3, 61/74 independence and concentration.** See §3.
- **M4, missing literature the brief requires.** Add one paragraph. Oota et al. (arXiv 2609.38108) find that declared plans are preserved in only 22–45% of Plan+ReAct trajectories. Co and Konuganti (ICML 2026 workshop) show agents reasoning that a move violates a stated rule and then submitting it. Xiong et al. (ACL 2026) report experience-following and error propagation from stored memory. I verified all three at their primary pages on 15 November. The paragraph locates Grok's channel conflicts within known statement/action gaps, and it says the carried \$130/\$30 figures cannot test memory reuse because they equal the current menu values. It adds about 75 words.
- **M5, versioned rules and per-game commits** in Appendix I. Values verified from git blobs and every run's `cloud/execution_manifest.json`.

### Optional (recommended where cheap)

- **O1/O1b/O1c, G7 positive insight** (§6).
- **O2, numeric presence.** Report the split: all 27 unpayable responses without locked collateral contain the figure, against 16 of the 21 with locked collateral. Of the five without a figure, two itemize released mortgages without a total. The other three (G3 d426, G5 d309, G8 d280) state exactly U0 as "maximum": the listed-only form of the two payable failures, here harmless. No exhaustive denominator is claimed, which respects root's correct rejection of 5/37.
- **O3, a pointer from §3.3 to Table 13.**
- **O4, the third proof class** in one clause.
- **O5, PDF metadata.**
- **O6, robustness clause for the selected-field rule.**
- **O7, release hygiene.** Update the README heading and status sentence. Either remove the eleven unused section files from the release or list them as retained historical sources. Regenerate `qa/portability.json` with the final archive.

## 5. Assessment of the integration decisions

**Agree:**

- Sol's opening contrast.
- Five compact incidents plus all eight in the appendix.
- The portable static build.
- The bootstrap terminology.
- Sol's row-level rubric.
- The explicit proposer table.
- F-01, F-02, M-01, M-02, E-01 and E-02 from the fresh adversarial review.
- Opus's 28/30 and G7 additions.
- Declining a "one value error" headline.
- Declining the rival-liquidity incident and a sales-excess optimum.
- Fable's bundled-sale clause.
- Keeping 43/48 in the supplement at its measurement level.
- **Declining 5/37 as an exhaustive denominator.** I reproduce 121 entries with M* > M0: 30 in the initial class, 53 middle, 16 necessity, 21 short and G7.
- Rejecting Fable's statement that published and implemented rules "agree on what can be raised". This is a good catch: the hotel-sale restriction is exactly what strands G7.
- Retaining long economic continuations in the casebook.
- Declining invented human attestation.

**Disagree, substantively:**

1. **"Keep the existing concise related-work discussion."** I agree that a novelty-disclaimer inventory should be avoided. But the finalization brief lists memory and statement/action literature among the distinctions related work must make, and the integrated text makes neither. M4 adds one short paragraph, not an inventory. This is the one place where I think the integrated paper does not yet meet the brief.
2. **Framing the 28/30 as "a positive choice description".** The count is right, but one member had no choice. The decision log did not catch G7 d318. This is minor in size, but it is exactly the kind of overstatement the paper otherwise avoids.
3. **"Do not promote the 3/132 versus 50/56 comparison."** I agree on no headline. The main text calls stopping decisions "more discriminating" than payment, and Table 13 is the population evidence for that sentence, yet the main text never references Table 13. O3 is a pointer only.

## 6. Strongest omitted positive insight

In G7, Gemini's public counter at d143 says that \$700 "leaves me with \$45 cash and unable to build". Its private note in the same response counts "\$450 in mortgageable non-Orange properties". At d144, Sol's note says Gemini "can mortgage non-orange assets, so its claimed development constraint is overstated", and Sol holds at \$700. At d146–d150, Gemini mortgages exactly \$450 (75 + 75 + 50 + 110 + 140) and builds four orange houses.

So a counterparty correctly discounts a strategic understatement of financing capacity. The understatement is confirmed by the speaker's own contemporaneous note and by its subsequent actions. This is the cleanest opponent-modeling evidence in the corpus: a rival's hidden budget, inferred correctly and acted on. It needs no causal claim (the record still does not identify why settlement happened at \$700), and it is entirely within the permitted-deception prompt.

The integrated text already has Sol "noting that Gemini can mortgage other deeds", but not the public/private contrast that makes the inference checkable. O1/O1b add it in two sentences, with exact substrings from the raw fields.

## 7. Ideas from the drafts and whether their loss matters

| Idea | Status in the integrated paper | Matters? |
|---|---|---|
| Opus: per-system first-menu stop table in main | Supplement table only | No; a pointer suffices (O3) |
| Opus: mortgage-before-sale with sales overshoot \$2–\$94 | Dropped | No. The overshoot is largely mechanical under auto-payment; the 28/30 carries the selection point |
| Opus/Fable: settlement-rule reasoning beyond G18 Gemini (Grok G17 d396 "standard rules", G19 "engine might enforce different rules", Grok G18 d313 inheritance) | Only the Gemini fee case | Mildly. One sentence could show that agents reason about what stopping hands over, not only about what can be raised. Optional; not proposed, to avoid main-text growth |
| Fable: 43/48 | Supplement, limited semantics | Correct placement; O2 adds the informative split |
| Fable: all-channel tier definition | Replaced by the selected-field rule | Correct; O6 records that the counts agree |
| Sol: engine/board hashes, function names in the proof appendix | Lost | Yes, for "versioned rules" (M5) |
| Sol: 61/74 "partly exposed" and concentration caveats | Lost | Yes (M3) |
| Opus/Fable/Sol: memory and statement/action citations | Lost | Yes (M4) |
| Fable: three listed-only maxima on unpayable debts | Lost with the 5/37 denominator | Worth keeping without the denominator (O2) |

## 8. Dissent and the few necessary changes

**Necessary for release:**

- M1–M5 (exact text in `replacement_prose.tex`; tested by compiling a copy under `amended_build/`).
- Normal final packaging: README status, archive regeneration and the release commit or archive hash in the release record.

**Not necessary but recommended:** O1 (G7), O2 (numeric split) and O5 (metadata).

**No new evaluation is needed or requested.** Nothing above depends on a new game, run, search or probe. Every number comes from saved records, source files and primary literature pages.

**I make no acceptance, score or novelty claim.**
