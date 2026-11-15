# Handoff: Fable 5.2 complete draft

12 November 2026. The draft is complete and I have stopped. It awaits the separate whole-paper cross-review. I claim no score and no acceptance.

## What was completed

A complete manuscript written by one author from the saved records and the prior feedback. It is a new paper with a new thesis and structure. It is not an edit of the integrated paper.

- `manuscript.pdf`: 31 pages. Title, abstract, introduction, setting and method, two results sections, a section on third parties and talk, discussion, related work, limitations, conclusion, 14 references, seven appendices.
- Main prose: 5,977 words by the counter in `analysis/verify_document.py` (six main section files, excluding abstract, quotations, tables, captions, source notes, references and appendices). Abstract: about 290 words.
- 2 figures, 7 main tables, 8 appendix tables, 29 quotation cards, 26 inline quotations.
- Eight incidents: four in the main text (G20 payment, G15, G2, G13) and four in Appendix A (G7, G19, G20 appeal, G18).
- Own analysis from raw records in `analysis/`, outputs in `data/`, and a one-command build.
- `initial_position.md` (written before any tabulation), `findings_and_limits.md`, `evidence_map.md`, `README.md`.

**Title.** What a Move Unlocks: Stated Consequences and Actions of LLM Agents in Twenty Monopoly Games.

**Thesis.** The agents state what a move will make possible before they make it, and their actions agree. For their own financing the statements are accurate in cases fixed by rule arithmetic. For rivals the refusals follow the event of completion and the form of the offer, and do not follow the size of the rival's opportunity.

## Strongest findings

1. **Quit or continue.** At the first menu, agents declared bankruptcy in 50 of 56 debts above every own asset and in 3 of 131 payable debts.
2. **Sixteen debts needed mortgages the menu did not list.** Fourteen paid. The first stored text counts the unlisted mortgages in thirteen, raises them in one, and leaves them out in both failures. The prompt supplies neither the release rule nor any value. Fourteen of fifteen stated figures equal the records.
3. **A completing opening is almost never accepted.** 3 of 186.
4. **Swaps are refused and cash bids are countered.** Rejection 95/116 against 37/72 for swaps, a gap of 16.7 to 30.5 points depending on which proposers are counted. Counters 26/70 for completing cash bids against 20/116 for completing swaps. Within every recipient the swap gap is positive and the cash-bid gap is between 0 and 9 points.
5. **Refusals mention the rival's set under both forms, and the systems refuse differently.** Gemini states a reciprocity rule, Grok states never-sell commitments, Sol and Opus name prices.
6. **No response to size.** Rejection does not rise with the houses the proposer could then afford.

Items 1 and the refusal-wording counts in 5 are new in this draft and no other author has reproduced them.

## Scientific dissent

- I withdraw the title I proposed for the integrated paper. The swap and cash split is an exploratory association with stated composition and ranges. It is not the thesis.
- I no longer argue that fourteen of sixteen should be the headline. Astra's objection holds. The full-debt comparison comes first and the sixteen are the hard subset.
- Against referee B: the offers are not contaminated, "a loop pays 131 of 131" is unexecuted and unprinted, and an unfinished byline is not evidence about who did the work.
- Against referee A: the first-menu partition calibrates difficulty from stored records. A loop cannot quit, so a baseline would not test the decision where both failures occur. The paper says the baseline is untested.
- Seed-block resampling is narrower than game resampling for the swap gap (24.2 to 35.5 against 13.8 to 47.8). I expected the reverse. Both are printed and neither is called a confidence interval.
- I dropped asking-price medians, construction receipts and first-estate concentration from the manuscript. Holder cash is one appendix paragraph.

`findings_and_limits.md` has the full list.

## Checks run

`./build.sh` rebuilds everything in about twelve seconds and ends with `qa/document_checks.json`.

- **Ledgers.** Offer ledger rebuilt from `decisions.jsonl` and equal to the integrated ledger on 12 fields for 920 of 920 rows. Debt episodes rebuilt and equal on identity, debt, actions, outcome and bound for 188 of 188.
- **Quotations.** 55 quotation spans generated from source and re-read by file hash, line, field pointer and span. 23 of 29 cards are character-identical to the previous paper's definitions. All used quotations are present in the PDF text.
- **Receipt.** 12 public messages checked against the counterparty's stored prompt. All found.
- **Numbers.** 229 `\fact{}` citations of 178 keys, none undefined. Incident amounts typed in prose are asserted in `analysis/b5_incidents.py`.
- **Rendered pages.** I inspected all 31 pages as two-page contact sheets after the final layout (`qa/render/`). No LaTeX diagnostics, no blank page, no text near a page edge. Body text is 11 pt. Figure labels print at 8.1 to 9.1 pt and the prompt listing at 8.3 pt. The smallest text is the commit hashes in Table 14 at 7.6 pt.
- **Frozen inputs.** `baseline_manifest.json` has SHA-256 `4aa83b66…23152faa2b` before and after, and its 72 files are unchanged. Git reports no change under `saved_games`, `contracts`, `python`, `frontend` or `scripts`. No file under the 11 November or 10 November paper folders is newer than my first file.
- **Source checks.** G18 d421 to d461 searched for inheritance terms in every Opus text field: none. Both stored replay reports read for all twenty runs. Tool choice read from 8,687 saved request records and from source at both run commits.

## Limits and weakest points

- Everything is retrospective on one cohort. No contrast is confirmed on new games.
- The sixteen-case result has two failures. The classification of the texts is my reading, with exact spans in Appendix C. No human annotated them.
- The 50 of 56 comparison treats declaring on an unpayable debt as agreement with payability. Continuing on such a debt is not an error, and the paper does not call it one.
- The refusal-wording table is regular expressions. The reciprocity and commitment patterns were written after reading examples.
- The capacity measure ignores what the proposer could still mortgage.
- Related work rests on abstract-level reading for several citations. The table in `findings_and_limits.md` says exactly what was read. PlanBench and Jehiel, Moldovanu and Stacchetti were read only as a tool-written summary of the abstract page.
- Inherited and not redone: three engine-executed payment sequences, the G7 menu search, both replay comparisons, the 74 reason codes.
- The abstract is long at about 290 words.
- Main-text figures and tables push the references to page 17. A venue format would need the tables cut or moved.

## Decisions for cross-review to test

1. Whether the paper should lead with the question or with one result.
2. Whether the quit-or-continue comparison deserves its place in front of the sixteen.
3. Four incidents in the main text and four in the appendix. The charter asks for eight in the package. I read that as allowing a casebook.
4. Dropping the price, construction and estate results.
5. Printing game-resampling ranges at all, given five seed blocks and one roster.
6. The wording "level three" for G13 and G7, where a statement covers both the writer's and a rival's options.

## Unresolved human-author metadata

The byline is "MonopolyBench project" with a footnote that the draft was prepared by one LLM research assistant under the owner's direction. The owner needs to supply the human author line and the venue's required statement of LLM assistance. Appendix G describes roles and names no human. Nothing in the paper is addressed to a referee.

## Charter notes

- I followed the scope. No objection that required deviation.
- The charter asks for "variation across the five seed blocks" and for not treating twenty games as twenty seed draws. I report per-block values, leave-one-block-out and exact block resampling, and add game resampling as a second view. I flag above that the block view turned out narrower.
- "13 explicit + 1 tentative" is stated as a model-assisted reading in the methods, the table caption and Appendix C.

## Compliance

- I wrote only under `full_drafts/fable_5_2/`. Temporary logs went to the session scratchpad.
- No game, engine run, replay, baseline, synthetic test, branch, rollout, provider probe or model query. No engine import. `git show` was used to read source text at two commits.
- No subagent. No commit or push.
- I did not open or list any other author's 12 November draft.
- Web: two abstract pages fetched on 12 November, recorded in `findings_and_limits.md`.
