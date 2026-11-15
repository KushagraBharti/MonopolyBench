# Fable 5.2: proposal for the single integrated paper

12 November 2026. This file says which frozen draft should supply each part of the integrated paper, what must change in it, and where my replacement text goes. Finding numbers refer to `findings.json`. Paths are relative to `paper_revision_2026-11-12/full_drafts/`.

## The claim in one paragraph

In twenty complete Monopoly games, four configured LLM systems often state what an action will make possible before they take it. For an agent's own finances the records can check those statements. In the sixteen debts that could be paid only with mortgages absent from the first menu, the first recorded text includes that collateral in thirteen of fourteen payments and leaves it out in both failures, the stated values are right in eight of nine cases, and the first action agrees with the text every time. For rivals the records show stated concern and a response pattern that depends on offer form and on who proposed, with no identified cause. Eight incidents show the statements in context. Nothing measures how a system computed, whether a choice was good, or how the models rank.

## Title and abstract

Use Sol's title: *Stated opportunities and executed choices: LLM agents in twenty Monopoly games*. It names what was measured. Astra's title says "planning" (XR-F52-10). Opus's title fits the debt half only. Mine names neither statements nor actions clearly.

Use the abstract in `replacement_prose.tex`. It leads with the question, gives the sixteen-case result with its counts, gives the bargaining result with both ends of its range, and ends with what the records do not show.

## Structure and sources

| Section | Take from | Change |
|---|---|---|
| 1 Introduction | `replacement_prose.tex` §1, which opens on Astra's two debts (`astra/sections/scientific_introduction.tex:3`) | Add the contribution list from `opus/sections/introduction.tex:18-23`, with "easy" removed |
| 2 Setting and method | `sol/sections/methods.tex` for rules, channels and definitions. `opus/sections/design.tex:12-18` for the configuration table | Add four offer forms. State the five levels once, in Sol's sentence at `methods.tex:38`. Replace the uncertainty paragraph with the policy below |
| 3 Own options: debts | `replacement_prose.tex` §2 | Insert Opus's figure `opus/assets/necessary_collateral.pdf` beside Table 2 |
| 4 Rivals' options: bargaining | `replacement_prose.tex` §3 for the census, composition, spread, replies and reasons | Add the G15 and G2 incidents from `opus/sections/bargaining.tex:53-70`, with the Opus appeal added to G15 (XR-F52-19) and turn 85 in G2 (XR-F52-15) |
| 5 Money, third parties and talk | `sol/sections/continuations.tex:2-9` for holder cash and prices, `:23-28` for construction and estates. `replacement_prose.tex` §4 for G13 | Name the population in the 4/9 sentence (XR-F52-13). Add G7, G19, the G20 appeal and G18 at the depths below |
| 6 What the records establish | `replacement_prose.tex` §5 with its level table | Follow with Sol's two paragraphs on future targets (`sol/sections/discussion.tex:16`) cut to one |
| 7 Related work | `opus/sections/discussion.tex:31-36` | It is the most complete and cites each source for one use |
| 8 Limitations | `sol/sections/discussion.tex:27-32` | Add that four language-model assistants read the sixteen texts after reading the same reports |
| 9 Conclusion | `opus/sections/discussion.tex:45-46` | Remove "The next step is" to keep within what was done |
| App. A Questions | `replacement_prose.tex` Appendix A | |
| App. B Sixteen texts | `replacement_prose.tex` Appendix B, or `sol/sections/necessary_texts.tex`, which prints the same fields | |
| App. C Offer tables | `astra/sections/full_offer_table.tex` for every cell at both stages. Opus's appendix tables for recipient strata, blocks, terms, capacity, the keyword screen and counters (`opus/sections/appendix.tex:49-105`) | Label the keyword screen and the capacity and list-value slices as descriptions (XR-F52-04, XR-F52-12) |
| App. D Incident cards | Full cards for G2, G7, the G20 appeal and G18 from `sol/sections/appendix.tex:5-57` | G7: "three turns later", and one house sold the next turn (XR-F52-15) |
| App. E Rules, prompts, response handling | `sol/sections/appendix.tex:116-148` | |
| App. F Reproducibility | `sol/sections/appendix.tex:150-168` for both replay comparisons and the game map, `opus/sections/appendix.tex:4` for the checkpoint | State that the analysis folders are untracked until the owner commits them |

Main text target is 5,500 to 6,000 words. My replacement sections come to about 3,900 words with the abstract. The setting, the remaining incidents, related work, limitations and conclusion from the sources above add about 2,400.

## Claims ledger

| Claim | Number | Level | Status in this review |
|---|---|---|---|
| Debts paid among those known payable | 128 of 131 | description | Recomputed from raw |
| Payable debts by resources needed | 62, 53, 16 | resource requirement, not difficulty | Recomputed from raw |
| Unlisted-collateral debts paid | 14 of 16 | accurate, consistent | Recomputed from raw |
| First text includes the collateral | 13, plus 1 question, 2 omissions | stated, accurate | Read again in full. Model reading |
| Stated values of unlisted mortgages | 8 of 9 correct | accurate | Hand-checked against the board |
| First action agrees with the text | 16 of 16 | consistent | First actions recomputed from raw. The texts are a model reading |
| Released collateral used | 19 payments, 33 mortgages | description | Recomputed from raw |
| First action on debts above every asset | 42 of 48 where a choice existed | description only | New in this review. Replaces 50 of 56 |
| Completing openings accepted | 3 of 186, 2 against the recipient's text | description | New in this review |
| Swap rejection gap | 30.5, 22.6, 16.7 points | description, cause not identified | Recomputed from raw |
| Cash-bid gap | −5.0 points, every range includes zero | no claim of absence | Recomputed from raw |
| Counters that keep the bundle | 79 of 111, 81 of 110 | description | Recomputed from raw |
| Rival consequence in refusals | 61 of 74, a disjoint set | stated | Inherited codes |
| Deeds and groups moved by estates | 227 deeds, 52 groups, plus 69 at the end | description | Recomputed from events |
| First estate to the eventual winner | 18 of 20 | description, confounded with prior strength | Recomputed from events |
| Construction in the first window, rent receipts | 16/17, 17/18, 7/15, 3/13, $57,378 | description | Inherited, not rechecked |

## Corrections to apply, by finding

1. Demote the first-action comparison to a table column and one paragraph (XR-F52-01).
2. Remove "easy", "hard" and "calibrates" from the debt section. Use Astra's sentence (XR-F52-02).
3. Replace the recalled-values sentences with the nine-texts statement and the exact description of the request (XR-F52-03).
4. Keep the capacity slices as an appendix description. No claim that refusals ignore size (XR-F52-04).
5. Use the full G13 acceptance text and date the odds error to the pitch (XR-F52-05, 06, 07).
6. Report response-side conflicts in one sentence each (XR-F52-08).
7. Print all three resampling units together (XR-F52-09).
8. No "planning" or "foresight" in title or summaries (XR-F52-10).
9. Scope the lesson about stated plans to the cases examined (XR-F52-11).
10. Keep keyword counts under their own name and out of the abstract (XR-F52-12).
11. Four offer forms in the main table (XR-F52-13).
12. Restore the economy subsection (XR-F52-16).

## Uncertainty policy

One paragraph in the method section and one table in the bargaining section.

- Counts are exact for this cohort. The contrasts were chosen after the games were inspected.
- Show the five seed-block values and the range when one block is left out.
- Show the middle 95% of resamples under three units: whole blocks (all 3,125 enumerated), games, and blocks then games. Say that whole blocks give the narrowest range and that it is not the precision of the estimate.
- State the two results that hold under every unit. The unfiltered swap gap stays positive. Without Grok-authored offers every range includes zero.
- Call nothing a confidence interval and print no p-value.

## Figures and tables

| Item | Source | Note |
|---|---|---|
| Figure 1, the sixteen debts | `opus/assets/necessary_collateral.pdf` | Keep the right-hand labels. Change "states them" to "includes them" to match the text |
| Figure 2, offer forms | `opus/assets/offer_forms.pdf` | Its right panel already shows block points and the widest range |
| Table, configurations | `opus/sections/design.tex:12-18` | |
| Table, all 188 debts | `replacement_prose.tex` Table 1 | |
| Table, the sixteen | `replacement_prose.tex` Table 2 | |
| Table, opening offers | `replacement_prose.tex` Table 3 | Four forms, zero cells shown |
| Table, proposers | `replacement_prose.tex` Table 4 | |
| Table, spread | `replacement_prose.tex` Table 5 | |
| Table, results by level | `replacement_prose.tex` Table 6 | |

Astra's `bargaining_stability.pdf` should not be the main figure as drawn, because its bars are the whole-block range alone.

## Incidents

Eight incidents, the same eight in every draft. Four full cards in the main text and four paragraphs that each keep one exact quotation, with their full cards in Appendix D.

| # | Incident | Main text | Source for the card | Change |
|---|---|---|---|---|
| 1 | G20 payment | Card in §3 | `replacement_prose.tex` §2.3 | |
| 2 | G15 refusal | Card in §4 | `opus/sections/bargaining.tex:53-61` | Add the Opus appeal one turn earlier |
| 3 | G19 correction | Short card in §5 | `opus/sections/bargaining.tex:72-81` | Optionally one sentence on the G11 exchange, where Sol concedes a corrected claim |
| 4 | G13 insurance | Card in §5 | `replacement_prose.tex` §4 | |
| 5 | G2 pricing | Paragraph in §4 | `sol/sections/appendix.tex:5-13` | Turn 85 |
| 6 | G7 bluff and sale | Paragraph in §5 | `opus/sections/conduct.tex:8-19` | Add the house sold the next turn |
| 7 | G20 appeal | Paragraph in §5 | `opus/sections/conduct.tex:35-45` | Pair with the G15 appeal |
| 8 | G18 withdrawal | Paragraph in §5 | `opus/sections/conduct.tex:47-58` | |

The G5 sequence and the G12 and G17 notes are supporting material inside the debt result. They are not incidents.

## What to leave out

- My refusal-style table by system (pattern counts written after reading examples).
- Any score for an unexecuted policy. Opus's sentence that a rule which never declares while an action is listed would avoid both failures is true by construction and may stay with its second half ("whether it would always reach payment we did not test").
- Asking-price medians as a main-text result. One sentence and the six same-deed pairs in the appendix, as Sol has them.
- Level tags on individual paragraphs. The level table carries them.

## Decisions for the project owner

1. The human author line and the venue's statement on LLM assistance. No draft supplies them and I do not propose them.
2. Human annotation of the sixteen first texts and the 74 coded rejections. Four language-model readings agree on the sixteen. That is not validation, and annotation would be new measurement.
3. Committing the analysis folders so that the repository URL supports the reproduction steps.
4. Whether a venue version should keep four full cards. The table in `review.md` ranks them by what each supports.

## Dissent I ask the integrator to record

- Against carrying my quit-or-continue comparison, my difficulty language or my size claim into the paper as findings.
- Against a main figure that shows only the whole-block resampling range.
- Against "planning" in the title.
- Against cutting the factual corrections (G19, and the G5 revision) to an appendix. They are among the few positive results that are checkable in full.
