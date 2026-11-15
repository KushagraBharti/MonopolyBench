# Integration proposal (Fable 5.2)

A complete-paper architecture with keep, cut and rewrite decisions for every section. It does not touch the original outline, the literature review, the prior manuscript or any frozen draft. `replacement_prose.tex` holds the finished text for every block marked R0 to R13 and compiles stand-alone (`build/replacement_build.pdf`, 20 pages). Finding identifiers refer to `findings.json`.

## 1. Thesis and title

Thesis: four configured systems completed similar numbers of color groups by trade and realized very different amounts from them. The difference was made after the deal, in cash position and at the execution layer. Bargaining over completion was contested and less distinctive than a pooled table suggests. Nearly every bankruptcy was unpayable, and estates went to the player already collecting rent.

Title: *Bargaining, building and bankruptcy: four configured LLM systems in twenty complete games of Monopoly* (Opus's title, shortened). Astra's "Bargaining, Development, and Inheritance in MonopolyBench" is acceptable. I prefer the first because it names the object of study as configured systems.

Abstract: R0. It leads with conversion, gives the unbuilt partition and the 61 reachable requests, then the bargaining result with its two qualifications, then eliminations and estates, then scope.

## 2. Architecture and length

| # | Section | Base text | Replacement | Target words |
|---|---|---|---|---|
| 1 | Introduction | Fable paragraphs 1 and 2, Opus G2 vignette | R1 | 800 |
| 2 | Environment, cohort and conditions | Opus `setup.tex` (rules list, configuration table, conditions table) | R2 for three paragraphs | 750 |
| 3 | Measurement | Sol units and "checked evidence and inherited validation"; Opus legal-sequence tests | R3 for two paragraphs | 550 |
| 4 | Bargaining over completion | none | R4, full | 1,450 plus incidents 780 |
| 5 | From completion to development | Fable conversion subsection, table and figure; Opus END table | R5 for two subsections; G20 kept | 900 plus incident 250 |
| 6 | Liquidity and elimination | Sol text and figure; four-case table | R6 for two paragraphs; G12 kept | 500 plus incident 250 |
| 7 | Estates and the bargaining around them | none | R7, full; G13 and G18 cards kept | 550 plus incidents 650 |
| 8 | Plans, forecasts and repeated errors | Opus `temporal.tex` | one sentence scoped (Astra O9) | 350 |
| 9 | Related work | Sol | R9 for one paragraph | 500 |
| 10 | Discussion and question coverage | none | R8 | 500 plus table |
| 11 | Limitations | none | R10 | 450 |
| 12 | Conclusion | none | R11 | 200 |

That is about 9,400 words of main prose including incident setup and reading, a little over the contract's upper target. If it must come down, cut in this order: the per-system ask ratios in R4 section 4.3 to the appendix (120 words), section 8 to two paragraphs (120 words), the Boardwalk note in R7 to the appendix (130 words).

Results begin on page 5 if section 2 holds to one table and four paragraphs. No draft currently reaches a result before page 6.

## 3. Section decisions

### Setup

- **Keep** Opus's five-item rules list and its conditions table. It is the most compact statement of the conditions in any draft.
- **Keep** Fable's configuration table column "condition that departs from the standard path".
- **Rewrite** the refusal paragraph (R2) so that 1,605 refused attempts, 1,604 recovery chains and the G2 d129 exception are stated once (FX-D07).
- **Rewrite** the honesty sentence (R2, FX-S02).
- **Keep and move up** the seed-block paragraph (R2, FX-S01). It belongs with the cohort description because it tells the reader how to read every later split by winner.
- **Cut** Astra's and Sol's long prose on Grok conflicts in setup. The conditions table row plus the pair counts in a footnote (60 end-to-propose, 22 build-to-end, 11 buy-to-auction, 7 accept against a rejecting text) is enough.
- **Cut** the winner grid from the main text (all four drafts agree).

### Measurement

- **Keep** Sol's units paragraph and its subsection separating checked from inherited evidence.
- **Keep** Opus's legal-sequence paragraph with the bound and the bundled-sale restriction, and its claim-class support table in the appendix.
- **Add** R3: offer position, deed direction, pure repricing, and the two-system scope of the coded reasons.
- **Cut** the long description of the 614-entry catalog and the earlier review passes to one sentence and an appendix pointer.

### Bargaining (R4, full replacement)

Order: volume and roles; responses by cell and position (Table "cells"); recipients (Table "styles"); counters with a baseline (Table "counters"); the nineteen acceptances and thread outcomes; stated reasons; two incidents; G19 as the control on reading a settlement.

- **Keep** from Fable: the position split, the conflict condition on Grok's openings and acceptances, block and game stability counts.
- **Keep** from Opus: counter content, per-recipient heterogeneity with the Opus exception in the main result, thread outcomes, the G2 incident.
- **Keep** from Astra and Sol: the sentence that settlement after a counter is association and not an effect of countering; six of 221 recipient-completing offers also break a recipient group.
- **Cut** Fable's "The completing side pays" and "Completing deeds are released by cash-poor holders" (FX-B03, FX-B06). Two sentences on seller cash survive in the appendix with the Opus share.
- **Cut** Opus's specificity sentence and its abstract sentence on counters (FX-B02).
- **Rewrite** every sentence that calls the pooled contrast rival sensitivity (FX-B01, FX-B04).

### Development

- **Keep** Fable's first subsection, Table "conversion" and Figure "conversion", with one change to the paragraph after the table: say that the two low rows belong to the two configurations with nonstandard response conditions and stop there.
- **Rewrite** "Why twenty groups were not built on" and "The default path" (R5; FX-D01, FX-D02, FX-D04).
- **Keep** Opus's END table and Table "recovery". Correct "Sol's seven-house target" to Gemini's (FX-D03).
- **Keep** the two reserve examples (G3 d176, G1 d426) from Astra, in one sentence each.
- **Keep** the G20 incident here, as Fable has it.
- **Cut** every "lost value", "lost development" and "earns nothing".

### Liquidity

- **Keep** Sol's subsection and figure. Sol's axes put debt on the horizontal. Opus and Fable put the bound there. Use the Opus orientation with Fable's open and filled G7 squares.
- **Rewrite** the payable-cases paragraph (R6, FX-L01) and add the reverse-direction paragraph (FX-L02).
- **Keep** the G12 incident in the Opus or Fable form with the two-sentence change in the R6 comment (FX-L03).
- **Keep** the two staged-finance contrasts (G20 d327 to 336, G16 d602).
- **Move** spending units and receipts to two sentences plus the appendix figure. The successive-owner example from Sol (G19 dark blue) is worth keeping as one sentence.

### Estates (R7, full replacement)

- Headline the forty eliminations before the last (FX-I01).
- Lead with concentration and the order of rent and estate. Give volumes for scale (FX-I03).
- Keep Fable's Figure "routes" in the appendix with its terminal bar.
- Replace all four G13 outcomes and readings and the G18 reading (FX-I02, FX-I04).
- Close with the four sequences in which a blocking or protected deed reaches a rival through an estate.
- **Cut** Fable's "The first monopoly and the outcome" subsection to the appendix cohort table.

### Plans, forecasts and repeated errors

- **Keep** Opus's three paragraphs. They are the shortest adequate treatment.
- Scope "the records contain no probability forecasts" to the coded opponent statements.
- Keep the recurrence table in the appendix. Keep G16 d103 to d159 as the one worked case.

### Related work

- **Base** on Sol, which states the inspected version and depth for each source.
- **Add** R9 for Monopoly and financial board games (FX-R01, FX-R03).
- **Add** from Opus and Fable, at the scope of their abstracts: Cosentino et al., Shah et al., LLM-Stakeholders, Hardy et al., Yang et al., Cattle Trade with the corrected paraphrase (FX-R02).
- **Cut** Opus's wider inventory (CICERO, deception survey, pricing collusion, GTBench, GAMA-Bench, SPIN-Bench) to at most two sentences, or to a footnote. None is used in an argument.
- **Fix** bibliography keys (FX-R04).

### Discussion, limitations, conclusion

- R8 gives four discussion paragraphs and one coverage table. Sol's separate prose coverage of the eight questions is cut. The three broader questions are table rows with two sentences after the table.
- R10 gives six limitation paragraphs. Each caveat appears once in its results section, in one sentence, and once here.
- R11 is the conclusion.

### Appendix

A. Cohort table with first completion per game (Fable). Units table. Rules detail (Astra).
B. Conditions detail and the norms comparison table (Opus), with the AgentMonopoly column attributed as in R9.
C. Bargaining tables: recipient by cell, block, game (Opus or Fable generated tables), counter content by system, one-deed price ratios, seller cash with the Opus share.
D. Development: the unbuilt-window table (R12), END provenance, recovery, defaults by game.
E. Eliminations: all sixty (Fable), four-case table, claim-class support table (Opus), routes figure.
F. Further incidents: G7, G11, G3, G20 d1, the proposition table (Opus), the rejected G12 d195 label.
G. Temporal exhibits (Opus).
H. Corrections made during the research (Astra's table).
I. Research roles and provenance (R12). The readiness pilot in one paragraph (Fable's wording).

## 4. Figures and tables in the main text

| Exhibit | Source | Note |
|---|---|---|
| Table 1, configurations | Fable or Opus | one table, with the departing condition per row |
| Table 2, conditions | Opus | shortened to five rows |
| Table 3, responses by cell and position | R4 | replaces every draft's cell table |
| Table 4, recipients | R4 | |
| Table 5, counters with baseline | R4 | may move to the appendix if space is short |
| Figure 1, responses and position | new, from Table 3 | stacked bars, opening and later side by side. Not built in this review |
| Table 6 and Figure 2, conversion | Fable | relabel "not legal to build" as "construction never listed" |
| Table 7, recovery after uneven-build rejection | Opus or Fable | |
| Figure 3, debt against own-asset bound | Opus | |
| Table 8, four eliminations above the bound | Astra or Opus | drop the "Menu" narrative, keep the column |
| Table 9, coverage | R8 | full page |

I built no new figure. Figure 1 is a proposal.

## 5. Incidents

Seven in the main text, each beside the result it illustrates. All quotations are generated macros. "Delivery" says who verified that the quoted public messages were in recipients' prompts.

| Incident | Placement | Channels shown | Delivery | Corrections the text must state | Outcome | Supports | Does not support |
|---|---|---|---|---|---|---|---|
| **G2** d124 to 128, d197 to 198 | Bargaining | Sol public, Sol note, Opus public, Opus note, Opus public (action-only), Sol note | Checked by Opus and Astra (to the counterparty) and here (all four public messages, to every other player) | The note's "nine yellow houses" is wrong: \$520 buys three. Opus held \$17 at the reversal. Sol collected \$44, none on a built deed. | No trade at turn 45. Sale at turn 69. Opus out at 72, Sol at 85, both to Gemini, who builds and wins | Pricing a rival's completion in both channels; an authorized bluff that ends a thread; the whole path | That any refusal or sale was a mistake; what \$475 would have done |
| **G15** d168 to 175 | Bargaining | Sol public and note, Grok public and note, Sol public, Grok public | Checked here and by Astra | State that the offer completes both sides. Cash figures match the ledger | No trade. Grok out first, 18 turns later. Blockers to Gemini | The first question's own example in a four-player state | That refusing was better |
| **G19** d135 to 136 | Bargaining, as control | Grok public, Grok note, Grok content, Sol public | Inherited | States Avenue is pink | Trade executes | Settlement is not belief; a proposal can contradict its own note | A plan to mislead |
| **G20** d95 to 102 | Development | Gemini public, Grok note, Grok public, Gemini public | Inherited | Sol had stated the same reluctance before the appeal. Opus later offered cash twice | Gemini refuses; Grok mortgages | A rival's building cash as a target; an open appeal | A working boycott |
| **G12** d249 | Liquidity | Grok content, Grok note, Grok public | Not applicable | The public message agrees with the call. The note has slips. Five sales pay (inherited witness) | Bankruptcy applied; estate to Opus | A payable debt lost to a call its own text opposes | A decision to surrender, or its absence |
| **G13** d250 to 253, d311 | Estates | Grok public twice, Grok note, Grok returned reasoning, Opus public | Inherited | 4 in 36, not 5 in 36. Grok did not land on Short Line next roll. Opus completed green at auction seven turns later | \$200 paid. Grok out 43 turns later to Sol | Solvency priced and sold; a recorded omission rationale | That the omission moved the price; how long the sale kept Grok in |
| **G18** d421 to 442 | Estates | Opus public, Sol public, Opus public, Opus returned reasoning | Inherited | The reason is Opus's stated one. The deed would also have completed Opus's group | No sale at \$250 | A likely creditor declining to prolong a debtor | Insincerity when offered; reliance |

Appendix, with exact quotes kept: G7 d42 to 43 (the same bluff, settling), G11 d255 to 258 (two-player refusal and a corrected false premise), G3 d362 to 364 (false stock obstacle with a contrary note), G1 d309 (Boardwalk note; redemption is \$221 here), G20 d1 (private note delivered as chat), G16 d103 to d159 (plan lost at the response layer), G4 and G6 short notes, and the rejected G12 d195 label.

Why these and not the baseline seven. G3 and G7 are the two baseline cases with the least at stake: Gemini had already held before the false obstacle, and the G7 gap is \$25. G2 and G15 answer the first research question directly and connect to the estate result. Five of the seven involve Grok. Sol is a speaker in four, Opus in three, Gemini in one. The limitations paragraph says why.

## 6. Coverage levels to preserve

The table in R8 is the proposal. These levels must not drift upward in integration.

| Question | Supported | Not supported |
|---|---|---|
| 1 Strategic reasoning | Census of responses; two systems' stated rival reasons; two cases; three payable debts | Optimal choice; a rival effect; regret |
| 2 Opponent modeling | Cases of public-capacity accounting, one of them wrong | Forecast accuracy; hidden-belief inference |
| 3 Negotiation, deception | Census of 920 responses with position and counter content; styles; cases of bluff, omission, withdrawal, correction | Effectiveness; agreement bias or its absence; a deception rate; persuasion |
| 4 Planning, memory | Census of completion to building to rent; one 31-turn target; one plan lost at the response layer | Plan-completion rate; adequacy of reserves; memory benefit |
| 5 Adaptation | Observed sequences after validator feedback | Learning; adaptation to an opponent |
| 6 Economics, risk | Census of financing at 60 eliminations; stated reserve holds with the enabling action on the menu; offered price ratios | Ex ante value; reserve policy; a completion premium |
| 7 Collective behavior | Census of estate flows; one appeal | Coalition frequency; any effect |
| 8 Validity | Conditions stated and counted; seat and seed dependence shown | Transfer; ranking |
| A Talk and action | Census of 139 disagreements for one system; cases; reachable requests invalid as written | A general relation |
| B General and multi-agent capability | Nothing | The relationship |
| C Skill and luck | Seven games follow a seat, four a system | A decomposition |

## 7. Wording rules for integration

These follow from the findings and from Astra's review.

- "Construction was never listed in the window", not "never buildable" or "could not be built on".
- "Requested a purchase that was reachable in that state and invalid as written", not "sound", "affordable plan lost" or "cannot be expressed".
- "Rejected more often", not "resist", "refuse or price a rival's completion" as a general statement.
- "Counters reprice", not "price the completion".
- "Grok played 43 more turns", not "bought time" or "lasted".
- "The eventual winner is the creditor in 35 of 40", not "54 of 60", and never "121 against 63".
- "Does not establish", not "cannot be read as".
- No "mostly", "mainly" or "usually" without the count beside it.
- No hand-typed quotation fragments. Paraphrase or use a macro.
- No reference to "the user", screenshots, drafts or review rounds in the paper (Astra P1).

## 8. Provenance and authorship

- Use Fable's three statuses (recounted from canonical logs, re-tabulated from a retained ledger, inherited) in one appendix table, with Opus's row structure. R12 gives the rows for the new quantities.
- State in the methods that no engine execution was performed after 29 October.
- Research roles: R12. The paragraph names the overlap exactly. Two assistants carry the model identifiers of two players, and the other two share developers with them.
- The byline is the human author's decision. Many venues do not accept language models as authors. The project treats the four assistants as coauthors of the work, and the paper should say so in the roles paragraph in whatever form the venue allows. I make no recommendation beyond candor.
- Source hashes: Astra's `review_source_hashes.json` and the baseline hash file cover the frozen drafts and ledgers. The integrated package should carry one manifest for the final build inputs.

## 9. Literature

- Sol's file is the base bibliography. Merge the 13 Fable additions and the 9 Opus-only entries that are actually cited. One key per work.
- Mark each entry with what was read (full text, sections, abstract page) as Sol and Fable do.
- Claims about the AgentMonopoly repository cite the repository entry and its commit and say "repository" in the sentence (FX-R01).
- FinBoardBench: creditor buildings sold to the bank, counteroffers supported, five execution failures before a recorded forced fallback, one focal model against three fixed LLM opponents (FX-R03).
- My literature checks went through a fetch tool that summarizes. Someone should confirm the FinBoardBench appendix letters against the HTML before a camera-ready.

## 10. Decisions I leave to the parent, with my vote

| Decision | My vote | Dissent to preserve if overruled |
|---|---|---|
| Lead result | Conversion first, bargaining second | Astra and Opus lead with bargaining. If bargaining leads, Table 3 with position must be the first exhibit |
| Counter table in main text | Yes, with the neither row | If only the author-only rows are printed, record FX-B02 as a dissent |
| "373 of 429" | Cut | Astra would keep it |
| Estate headline | 35 of 40, then rent by route | Astra would lead with 52 and 227 against 63 and 207 |
| Seed-block paragraph | Main text, section 2 | Not in Astra's plan |
| Incidents | Seven inside results | Agreed with Astra |
| Separate conduct section | No | Astra and Sol drafts have one. Astra's review agrees to embed |
| Seller-cash tabulation | Appendix, two sentences | I wrote it. I no longer think it earns main-text space |
| First-completion table | Appendix | Same |
| G3 in main text | No | Astra and Sol drafts have it. Astra's review moves it |

## 11. Order of work

1. Merge preambles and quote files. Generate one quote manifest covering the 28 baseline fields, Opus's 10, Fable's 14 and the 2 inline excerpts added here. Relabel the eight whole-field cards.
2. Assemble sections 2 and 3 from the named bases with R2 and R3.
3. Drop in R4 to R8, R10, R11 whole.
4. Regenerate Tables 3 to 5 from one script. `tools/check_offers.py` computes all of them.
5. Rebuild the conversion and finance figures from the Fable and Opus scripts. Build Figure 1.
6. Run a numbers checker of the kind in `tools/check_replacement_numbers.py` over the whole integrated source.
7. Fresh adversarial review on the integrated PDF.

## 12. Minimal delta against the current `integrated/` text

`integrated/` appeared while this review was in progress. I read it once, after writing sections 1 to 11, at about 05:49 UTC on 11 November (PDF hash prefix `0feea7e4c8014626`). It is close to this proposal in architecture: conditions first, incidents beside results, the nonterminal estate population, eight incidents of which seven are the seven proposed in section 5. If the parent keeps its sections, the following twelve insertions from block R13 of `replacement_prose.tex` close the findings that still apply.

| R13 item | File and anchor in `integrated/` | Finding |
|---|---|---|
| 13a | `manuscript.tex`, abstract sentence beginning "Among 111 counteroffers" | FX-B02, FX-B04 |
| 13b | `sections/bargaining.tex` line 26, the two sentences on 373/429 | FX-B03 |
| 13c | `sections/bargaining.tex` line 28, after "21/102 versus 7/89" | FX-B04 |
| 13d | `sections/bargaining.tex` line 56, first two sentences | FX-B02 |
| 13e | `sections/bargaining.tex` line 56, after "sixty-one of seventy-four" | FX-B05 |
| 13f | `sections/bargaining.tex` line 88, after the medians | FX-B06 |
| 13g | `sections/bargaining.tex` lines 65 and 67 (G2) | FX-C02 |
| 13h | `sections/development.tex` line 14, first four sentences | FX-D01, FX-D05 |
| 13i | `sections/finance_inheritance.tex` line 14, after the payable cases | FX-L01, FX-L02 |
| 13j | `sections/finance_inheritance.tex` line 73 (G13 finding) | FX-I02 |
| 13k | `sections/temporal_discussion.tex` line 60, after the seat-2 sentence | FX-S01 |
| 13l | `sections/related_limits.tex` lines 7 and 9 | FX-R01, FX-R03 |

Also change the conclusion's "Counteroffers often preserve a rival's completion while changing compensation" to "Counteroffers reprice a requested deed at similar rates whether or not it completes a group", and relabel the eight whole-field cards in the merged quote file (FX-C06).

Line numbers are those of the snapshot and will drift.
