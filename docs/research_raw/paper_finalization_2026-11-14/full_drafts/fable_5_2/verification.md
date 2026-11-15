# Verification

Fable 5.2, 14 November 2026. This file says what was checked for this draft, how, and what was not.

## Scope compliance

- No game was played. The rules engine was not imported or executed. No replay, policy, baseline, search or synthetic state was run. No model or provider was called. No subagent was used.
- Engine source was read. Stored JSON and JSONL were read. Arithmetic was done on stored records. LaTeX was compiled and the PDF was rendered.
- Eight web pages were fetched to confirm bibliographic details of cited papers. That is literature access, not an evaluation.
- Every file written is inside `docs/research_raw/paper_finalization_2026-11-14/full_drafts/fable_5_2/`.
- The other authors' new drafts under `full_drafts/astra/` and `full_drafts/sol/` were not opened.
- No commit, push or branch was made. `git log -1` is still `863f8ef79`.
- The 84 files pinned in `paper_revision_2026-11-12/final_manuscript_manifest.json` were rehashed after the work. 84 match, 0 differ.
- Persistent memory was not updated, because the instruction was to write only in this folder.

## What was read before writing

The brief. `TEAM_SYNTHESIS.md`. The three files in `inputs/` in full. All four `review.md` and all four `cross_review.md` in the 14 November package. Astra's `continued_financing_argument.md`. The four literature matrices. The complete 12 November integrated manuscript source, its evidence map, handoff, findings, literature notes, integration decisions and final-review decisions. The engine functions named in Appendix B.

## Build

Command: `PAPER_PYTHON=/Users/kushagra/CS-Projects/MonopolyBench/python/.venv/bin/python bash build.sh`

The build was run from a deleted `build/` directory and exits 0. Two consecutive full builds of the same sources produced byte-identical PDFs, checked once during the work. `SOURCE_DATE_EPOCH` is fixed in `build.sh`.

Final PDF: `manuscript.pdf`, 29 pages. Its SHA-256 is recorded in `qa/verification.json` and in `MANIFEST.sha256`.

## Automated checks

`tools/08_verify.py` runs 36 checks and all pass. Output is in `qa/verification_output.txt` and `qa/verification.json`.

**Numbers.** 23 statements in the manuscript source are tied to values recomputed from `data/*.json`. The script asserts the value and then requires the matching phrase in the source. They cover the census, the partition, the middle-row support, the coverage classes, the first-action table, the selective-financing counts, the stated-total counts, the tiers, the carried-note counts, corpus size, refusals, channel conflicts, the response counts and the swap contrasts. A further 44 assertions fix the values behind them and the values that tables print from generated rows.

**Quotations.** 47 quotations are used. Each is asserted to occur verbatim in its stored field at extraction time, again at verification time with the field hash, and in the PDF text.

**Full texts.** All sixteen first responses are found in the PDF paragraph by paragraph, for both channels. Eleven have an authored note and sixteen a provider field.

**Evidence spans.** `tools/07_tables.py` asserts that each of the sixteen tier-evidence spans occurs in the named channel, and that each carried-note span occurs in the notes delivered with that request.

**Layout.** The conclusion is on page 9 and the references start on page 9. Body type is 10 pt TeX Gyre Termes. Side margins are one inch, with punctuation protruding by under 2.5 pt from microtype. The page is US letter.

**Log.** No undefined reference or citation, no missing character, no overfull box wider than 3 pt.

**Length.** 5,500 authored words in the main text, plus 698 words of quoted model text and a 221-word abstract.

## Page inspection

All 29 pages were rendered at 88 dpi to `qa/p01.png` to `qa/p29.png` and reviewed, the nine main pages individually and the appendix through five contact sheets and six full-size pages. Problems found and fixed during inspection:

- the title broke over three lines;
- the opening-offer table wrapped its first column, so it now spans both columns;
- the figure legend overlapped the first group label and one label was clipped;
- two appendix tables were too wide;
- math letters were in a different face from the text, so letters and digits in math now use the text face;
- one appendix quotation printed a 2,800-character field inline, so it is now the key sentence.

No clipped text, blank page or split table remains that I could see.

## Checks made by hand in this round

- The engine, resolver and board files have the same blob hash at both run commits and in the working tree.
- Every incident fact stated in the main text was compared with the raw decision records: cash figures, offers, replies, routes, eliminations and turn numbers. The evidence map lists them.
- The rubric was applied to both channels of all sixteen responses, not to one selected field. The tiers did not change from the 14 November reading.
- Every mortgage and resale value stated in the sixteen selected fields was compared with board values. One is wrong, Sol's $430.
- The five unpayable responses without an exact figure were read directly and are quoted in Appendix F.
- Astra's two-entry argument was re-derived for bundled sale plans and its premises recomputed (see `changes_and_dissent.md`, section 5).
- The stored system prompts were regenerated from the raw records and are identical to the 12 November copies.

## Inherited, not rechecked

- The three legal payment sequences for the declared payable debts, and their $38, $180 and $43 remainders.
- The restricted menu search for G7.
- The replay comparisons of the twenty games.
- The 61 of 74 reading of refusal texts.
- The fourteen resistance-to-settlement histories and the six matched price pairs.
- Grok's required tool-choice setting as verified against saved request files.
- The cost figure.
- For incidents: that Sol never completed either group in G15, Opus's later cash offers in G20, and that a second $750 rent brought Sol to $49 in G18.
- Literature read only by other authors: the Catan paper, the Jehiel et al. abstract, NegotiationArena, Lewis et al., He et al., and AgentMonopoly's rules file.

## Known limits of the checks

- The tier coding is one model's reading. The spans are checked for presence. The judgment is not checked by anything.
- The number match can pass on a coincidence. All 43 matches were printed with context and read once. Figures equal to the debt, the cash or the shortfall are excluded.
- The verifier checks that a phrase with the right number is in the source. It does not parse every number in the prose. I proofread the final text of sections 1 to 6 against the data once after the last substantive edit.
- No person has read this draft.
