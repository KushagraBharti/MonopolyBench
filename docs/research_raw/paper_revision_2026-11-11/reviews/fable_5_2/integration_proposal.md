# Integration proposal by Fable 5.2

11 November 2026. This is a complete architecture for the integrated paper. It names the claim, the title and abstract priorities, each section with its source draft and word budget, the figures and tables, all eight incidents, and the question map. Finished text for the parts that change most is in `replacement_prose.tex`. Reasons are in `review.md` and `findings.json`.

## The claim

LLM agents bargain over what a trade would let a rival do next. The paper supports four statements, in this order of strength.

1. The agents treat a rival's completion as a reason to refuse or to charge, and the instrument depends on the form of the offer. They refuse swaps and they price cash.
2. The attention is to a category. It is not a calibrated valuation.
3. The guard weakens as the holder's cash runs down. This is clear for Sol, thin for Grok and absent for Gemini, and Opus hardly refuses at any level.
4. Execution is reliable where the game supplies a menu and an immediate check. Open-ended follow-through is less uniform and depends partly on response conditions.

Everything else (rent after development, estates, pre-estate positions) is context for these four.

## Title

Recommended: **Bargaining over a rival's next move. Strategic attention, liquidity and execution in twenty LLM Monopoly games.**

Acceptable alternatives are root's "Bargaining over Rivals' Opportunities" and Sol's "LLM bargaining over competitors' future options". I would not use "Guarding the Last Deed", because cash bids are not guarded against by refusal, or my own "Until They Need the Cash", because 23 of 43 one-sided sales came from holders with $100 or more. I would keep "strategy" out of the title, since the paper cannot assess strategy quality.

## Abstract priorities

The abstract should contain, in this order:

1. The economic object in one sentence (a trade changes what each party can do to the others).
2. The cohort in one sentence with 6,989 decisions, 920 responses and 188 debt episodes.
3. The offer-form result with counts (swaps 95 of 116 against 37 of 72, cash bids 60% against 65%).
4. The price result, with asks higher in eleven of twelve seller, mortgage and stage cells.
5. The stated reasons, 61 of 74, named as model-assisted readings.
6. The limit, which is that same-deed asks are mixed and cited quantities are sometimes wrong.
7. Liquidity as a moderator, with the unevenness across systems said in words.
8. Execution, with 128 of 131 payable debts paid and 61 through several actions.
9. The scope, which is observational, five seeds, one roster, one system under recovery, no ranking and no decision scored.

The abstract should not contain a pooled rejection percentage by holder cash, the seller-conversion split, rent totals, estate shares, "categorical rule", "premium", or "reasoning" as a description of the census. The drafted abstract in `replacement_prose.tex` follows this list at about 250 words.

## Sections

The target is 6,800 to 7,300 words of main prose outside quotations, tables and references.

| # | Section | Words | Take from | Change |
|---|---|---|---|---|
| 1 | Introduction | 650 | `replacement_prose.tex` | New. Four results, three contributions, five boundaries, the question sentence |
| 2 | Setting and conditions | 900 | Fable 2.1 to 2.4 for structure and the prompt excerpt. Opus Table 1 (rule conventions) with the auction row corrected. Sol's sentence defining strategic attention | State the three conditions once. Add one sentence that every contrast is exploratory |
| 3 | Bargaining over what a rival can do next | 1,500 | `replacement_prose.tex` Section 2 | New Table 1 by offer form. Incidents 1 and 2 follow |
| 4 | The guard weakens with the holder's cash | 900 | `replacement_prose.tex` Section 3 | Replaces Fable 4 and 5.1 and Opus 4.5. Incidents 3, 4 and 5 follow |
| 5 | Execution with and without a menu | 1,000 | `replacement_prose.tex` Section 4 for the census and the last paragraph. Opus 5.1 for exposure (two paragraphs and the lifecycle figure). Sol 5.3 for estates (one paragraph) | Incident 8. One paragraph on estates and pre-estate positions, with the case table in the appendix |
| 6 | What is said and what settles | 400 | Opus Section 6 | Incidents 6 and 7. The G7 bluff is cited from Incident 3 |
| 7 | Discussion | 700 | `replacement_prose.tex` Section 5, then Opus 7.4 ("Conditions are part of the environment") cut to one paragraph | Question map as a short paragraph with the table in the appendix |
| 8 | Related work | 450 | Sol's section for LLM negotiation and Monopoly benchmarks. `replacement_prose.tex` for the new paragraph on trade denial | Cite only what an author read |
| 9 | Limitations | 300 | Opus Section 9 as the base, plus the paragraph in `replacement_prose.tex` | One consolidated section |
| 10 | Conclusion | 150 | New, four sentences matching the four statements | |

Order within Section 3: offer form, then price, then stated reasons, then the calibration null. The reader should meet behavior before explanations.

## Conditions

State each condition once in Section 2 and again only where it changes a number.

- Opus recovery. Use my setup paragraph (exact refusal message, five-place diff, 1,604 of 1,696 decisions, 162 of 189 trade responses, 1,394 prompts with no note of its own, 60 of 61 defaults). Opus's ten-minute table goes in the appendix. The recovery prompt keeps the permission to deceive. The trigger is unconfirmed.
- Grok text and call. 139 of 1,068. Sixty-four threads opened that way. This condition now matters for one main result. Twenty-nine of the 72 non-completing opening swaps and 13 of their 17 acceptances were conflict-opened, and Section 3 reports the contrast with and without them.
- History summaries. 2,054 prompts, inherited count. Current terms and holdings are correct.
- Rules not stated to agents, and board values present only in purchase prompts. The G20 payment shows the agents supplying mortgage and resale values themselves.

## Figures

1. **Opening responses by offer form.** New, from `data/c3c_swap_table.json` and `data/c3e_grok_conflict_openings.json`. Stacked accept, counter and reject bars for five rows (swap completing the proposer, both, nobody; cash bid completing the bidder, nobody) with counts printed. A second panel shows the swap contrast for each recipient as paired points, with hollow markers for the version without conflict-opened threads.
2. **Cash prices.** Fable's `fig_prices` (asks and bids by the buyer's distance to completion, every offer, mortgage status marked). Sol's same-deed figure goes to the appendix with G4 flagged.
3. **Liquidity.** Two panels. The left panel shows responses to completion requests by holder cash for standard-condition holders, separately for opening and later offers, with Opus as a faint fourth series. The right panel shows the seller's cash at each of the 43 one-sided sales against the 57 cash settlements that complete nobody, with Opus marked, in the style of Opus's `distress` figure.
4. **All 188 debt episodes.** Fable's `fig_debt` (debt against own-asset bound, paid and eliminated classes). Astra's action-count histogram as an inset or appendix panel.
5. **From completion to income.** Opus's `lifecycle` figure, all 63 groups with landings.

The appendix figures are pre-estate positions (Sol's rank plot, which needs no valuation) and the same-deed rows.

## Tables

Main text:

1. Systems and conditions (Fable Table 1 with Opus's condition column).
2. Opening offers by form and completion (`replacement_prose.tex` Table 1).
3. Debt episodes by system, with paid, payable eliminations, bound below debt and menu lock (Sol Table 4).
4. Building after a trade-completed group, by system, with first-management-turn counts, causes of the 20 unbuilt windows, landings and rent per landing (Fable Table 5 plus the cause row).

Appendix: full census by recipient, thread position and cell (identical in all four drafts). Offer form by recipient, block and treatment of conflict threads. Seller by mortgage by stage ask cells (Sol). The seven same-deed rows with first, median and last ask, mortgage status, turn and seller cash. Concessions by cell and recipient (Opus). The capacity cut by recipient. The 14 refusal-to-sale pairs with declined and accepted terms (`data/c2_refusal_to_sale.json`). Pre-estate case table with cash, deeds, buildings, prior rent and asset index per game. Cohort. Question map.

## The eight incidents

Each keeps context, source-exact cards, what happened, what it shows and a source line. Target 26 cards or fewer in the main text.

| # | Game | Mechanism | Section | Cards | Base text |
|---|---|---|---|---|---|
| 1 | G2 | A blocker priced by what the buyer could build and by whom it could be resold to. The roles reverse once the bidder is broke | 3 | 3: Sol d119 note (resale), Sol d124 price, Sol d124 note | Opus's version cut from seven cards. Say that Grok's opening bid was a conflicting call. Keep the wrong house count |
| 2 | G15 | A recipient refuses its own complete group three times after the proposer meets its stated objection | 3 | 3: Grok d169 note, Sol d174, Grok d175 | Sol's or Fable's text. One sentence on Opus's public appeal at d166. End on Sol's note about waiting until opponents need cash, which leads into Section 4 |
| 3 | G7 | A liquid holder declines, and later sells a rival's completing deed to pay for its own houses. A buyer times its bid to the holder's cash. A "final" price below a private limit settles | 4 | 4: Sol d39, Grok d42 public and private, Sol d142 note | Fable's Incident 5. The bluff is one sentence here and is cited from Section 6 |
| 4 | G13 | Distress used as a bargaining position, with an available mortgage left out of the pitch | 4 | 3: Grok d250, Grok d252 returned explanation, Opus d253 | Sol's text, which handles the probability claim most carefully. Drop "about 12%" |
| 5 | G18 | A buyer withdraws a standing offer once the seller weakens and bids lower afterward | 4 | 3: Opus d431, Sol d441, Opus d442 with its returned explanation | Opus's or Sol's text. No reliance and no claim that the assurance was insincere |
| 6 | G19 | A recipient corrects a false premise and accepts the terms on their merits | 6 | 2: Grok d135, Sol d136 | Astra's compact text. Competent correction. The proposal was a conflicting call |
| 7 | G20, from turn 22 | A public appeal to stop a sale from becoming houses, followed by its author and by one other player and ignored by a third | 6 | 3: Gemini d96, Grok d97 note, Gemini d101 | Fable's or Opus's text. One appeal, its author's follow-through, one private agreement and one counterexample. Not a cartel |
| 8 | G20, turns 107 to 108, with G12 | Execution on a defined problem. A ten-step payment that creditor and debtor had both priced at $1,414, beside a payable debt that ends in a contradictory bankruptcy | 5 | 5: Gemini d325, Sol d327, Sol d336, then Grok's G12 note and public message | The G20 half is new, in `replacement_prose.tex` (drop the d329 card if space is short). The G12 half is Sol's text cut to one paragraph. Say that its message was delivered to nobody |

These are the eight mechanisms of the earlier drafts with one change. The eighth slot now pairs the G12 failure with a success on the same task, so the set contains competent execution as well as competent correction (G19). The count is 26 cards. G1 (Boardwalk sold at a quarter of list) is covered by the price paragraph in Section 4 and goes to the appendix with G11 and G3 as controls.

Grok takes part in seven of the eight. Say so once in the limitations, with the reason. Its notes are the longest and only its responses carry text beside the call. The G20 payment and G18 involve no Grok response.

## Question map

A compact table in the appendix with a paragraph in the discussion. Rows follow Sol's and my versions with these entries.

| Question | Supported here | Not measured |
|---|---|---|
| 1. Strategic reasoning | Agents refuse trades that would help them because of what a rival gains. Swaps completing only the proposer are refused 95 of 116 at the opening. Stated rival consequence in 61 of 74 refusals of own completion (inherited readings) | Whether any refusal was right. Regret, exploitability |
| 2. Opponent modeling | Exact reading of rivals' public cash and collateral (G20: two systems price one estate at $1,414). Notes on building capacity, resale and inheritance | Calibrated beliefs about hidden intentions |
| 3. Negotiation, cooperation, deception | Full response census by offer form. Repricing as the general way to disagree. Authorized bluffs, an omission, a correction, a withdrawn assurance, a denial appeal | Persuasion effects, joint surplus, prevalence of deception |
| 4. Planning and memory | A ten-action liquidation carried to its stated remainder. A multi-turn building target reached in G9 (inherited). Opus mostly without its own notes | Benefit of memory. A plan-completion rate |
| 5. Adaptation and learning | Offer revisions inside threads. Terms that change with the holder's cash | Learning caused by feedback. Unfamiliar opponents |
| 6. Economic decisions and risk | Prices relative to list by role. 128 of 131 payable debts paid. Buildings kept where mortgages suffice (2 of 68 exceptions) | Whether any price or reserve was right |
| 7. Collective dynamics | Estates concentrate with players already ahead. Public appeals to deny a rival drew partial compliance | Coalition stability. Effect of an appeal |
| 8. Validity | State rebuilt from events matches every prompt. Two independent offer ledgers agree. Conditions stated with the results they touch | A ranking. Play under a repaired interface |
| A. Strategic or sounding strategic | Stated rival reasons agree with the refusal pattern for swaps. Cited quantities are sometimes wrong and show no gradient | A general relation between explanation and play quality |
| B. General and multi-agent capability | Nothing | Any relationship |
| C. Skill, luck, weak opponents | Wins by system and by seat are similarly uneven. First creditors were mostly already ahead | Shares of skill and chance |

## Build

- Adopt the Fable package's `\fact{}` discipline (every prose number is a key lookup and an undefined key stops the build) and its quote generator.
- Keep both offer ledgers. Mine and Opus's were built independently and agree on all 920 rows for the fields compared. The integrated build should assert that agreement.
- Keep Astra's closure of liquidation episodes on payment events and Sol's delivery checks for public messages.
- Carry my check scripts (`tools/c1` to `c11`) forward as regression tests on the numbers in Sections 3 to 5.

## Decisions for the owner

1. Title, from the three candidates above.
2. Whether the offer-form split leads the paper. It is one author's cut from one day and needs a second author's reproduction first.
3. Whether a human will label the 74 refusal rows. That needs no model call and would turn inherited codes into checked evidence.
4. Whether the eighth incident may pair two games. If not, the G20 payment should replace G12 as the main card set and G12 becomes one sentence, since the census already counts it.
5. The human author line.
