# Initial independent position (Fable 5.2 xhigh)

Recorded after reading the complete integrated manuscript and before opening
`final_review/astra/root_review.md`, `integrated/integration_decisions.md`,
`integrated/evidence_map.md` or any of the earlier cross-reviews in this session.

## What I had read when I wrote this

- Pinned PDF `integrated/manuscript.pdf`, SHA-256
  `8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5` (matches the pin).
- All 38 entries of `integrated/qa/integrated_file_hashes.json` re-hashed: 38 of 38 match.
- `manuscript.tex`, `preamble.tex`, and all seventeen `sections/*.tex` files, in document order.
- My own render of the pinned PDF; pages 1–28 and 30–33 inspected as images at this point.
- While pinning I also saw `integrated/README.md`, `qa/render_review.md` and
  `source_manifest.json`. Those describe the build and the presentation check. They are
  root-authored, so I note the exposure. Neither argues the scientific case.

Nothing below relies on a data file. The arithmetic is from numbers printed in the paper.

## Verdict before adjudication

The manuscript is a coherent, honest observational paper. Its accounting is internally
consistent everywhere I could test it from the page. I expect to recommend it as sound
with a short list of corrections, most of them wording and exposition. I found no
internal contradiction that would overturn a result.

My main reservation is not about truth. The paper states its findings less clearly than
its evidence allows, and it buries them under repeated disclaimers.

## Internal arithmetic that closes

- Table 1: decisions sum to 6,989 and attempts to 8,679. Opus's 3,301 attempts equal
  1,696 decisions plus 1,605 refusal-containing decisions.
- Table 2: every row, column and opening-plus-later total closes (918, 524, 394;
  113/393/412). The six quoted rejection percentages are right. The within-stage gaps are
  13.0 and 12.7 points against 27.9 pooled.
- Table 3: rows sum to 920 and to 113/394/413.
- Table 8: recipient rows reproduce Table 2's four category totals and all twelve A/C/R
  cells. Sol, Gemini and Grok show both stated orderings; Opus shows neither.
- The 74 reason-coded rejections equal 38 recipient-only plus 36 both, and split
  4/31/8/31 by recipient, as stated.
- First windows: 17+18+15+13 = 63, 16+17+7+3 = 43, 9+4+4+3 = 20, 34+3+3+2 = 42.
- Defaults: 70 + 1 + 61 = 132 attempts over 66 two-attempt decisions; 663 − 66 − 24 = 573.
- Table 11: all nine remainders equal cash + M − R − house. Two rows clear on cash alone,
  five more with outside mortgages, two fall short.
- Table 12: all 56 "Below debt" rows have bound below debt; the three payable rows and the
  hotel lock have bound at or above debt; four rows are automatic.
- Routes: 63+16+9+52+69 = 209; 54 = 35 + 19; $53,810 + $3,568 = $57,378, which also equals
  the four per-configuration receipts.
- Table 9: opening and later counts sum to the pooled counts in all four columns, and the
  stated orderings match the printed medians.
- Winner counts 8/7/3/2 and the three seat patterns agree with Table 7.

## Concerns I intend to test against sources

Ranked by how much they could matter.

1. **Table 4, author-only row.** The prose says ninety-two counters "preserve the same
   original author's newly complete group". The table heads the same 92 "All requested
   deeds retained". Those are different predicates. Retaining every requested deed implies
   keeping the completion, but not the reverse. Either the two counts coincide in the
   data or the table mislabels one. This is the new claim most worth attacking.
2. **"Eighty-five improve the counterer's net cash, with a median increase of $125."**
   The denominator is not stated. It could be 111, 92 or 88.
3. **G16 liquidation sentence.** "Actual staged liquidation can succeed … In G16,
   extensive liquidation instead reaches $1,393." Table 12 gives G16 d602 cash of $288
   and a bound of $1,393. If the $1,393 is the bound, the sentence presents a ceiling as
   an executed liquidation.
4. **G12 d249 "The note also contains arithmetic errors."** The quoted span ($350 > $207)
   is correct arithmetic. The claim needs the unquoted part of the note.
5. **G15 "three times".** The card shows two refusals, and the source range d168–175
   could hold four offer/response pairs.
6. **G20 chronology.** "That decision's received call ends management … After later
   construction". I want the decision sequence, and whether this window is one of the
   four first-window conflicts.
7. **Uneven-build denominators.** "Including defaults gives 20/29, 6/19" adds defaults to
   uneven-build rejections, yet seven non-Opus default targets "exceed cash". Those may
   not be uneven-build failures.
8. **Semantic claims about four Grok deferral notes** and the three quoted misquotes
   ($198, $220, $110).
9. **Related-work facts**: AgentMonopoly at `2434f427` (single offers, negative-cash
   elimination, buildings intact to creditor, bluffing prompt), FinBoardBench §3.2 and
   App. E. "Its prompt" has an unclear antecedent.
10. **Seed-block and game robustness counts** (five blocks, 17 of 19 games, four blocks,
    13 games) and the cash-threshold cuts.
11. **Nine `data/*.json` files are outside the 38-file pin.** The exhibit builder reads
    them, so the pin does not cover the inputs of the generated rows.

## Exposition problems visible without any source

- **The abstract's headline is unlabeled.** "17, 18, 15 and 13 … 16, 17, 7 and 3" never
  says which system is which, and "one participant" is unnamed. A reader of the abstract
  alone cannot tell that the refusal-recovery participant is the one that built on 7.
- **Table 2 has four rows and the prose uses two.** The "neither" row is the natural
  reference: 63.9% opening and 15.9% later rejection. Against it, author-only offers are
  rejected about ten and five points more, recipient-only about three and eight points
  less. "Both" openings are rejected 34/48, close to author-only. None of this is said.
- **"Much of this pooled contrast changes"** is vague. The gap halves.
- **"Opus reverses both orderings"** overstates 7/52 against 5/42 (13.5% and 11.9%).
- **18 of 63 trade-completed groups belong to eventual winners.** With one winner among
  four players, a quarter is the reference share. Trade completion sits near it; direct
  purchase (12/16) and nonterminal estates (45/52) do not. The paper gives the counts and
  leaves the reader to notice.
- **Hedging is heavy and repetitive.** Most paragraphs end in a "not X" clause, and the
  same caveat often appears in text, caption, appendix and limitations. I will count
  these and propose specific cuts.
- **Unexplained populations**: the "fixed 240-decision sample" has no stated sampling
  rule, and "614 overlapping catalog entries" is never defined.
- **Ambiguous agents**: "Subsequent $150 and $225 offers also fail" (G18) does not say
  who offered.
- **Plural inflation in the abstract**: "financial-denial appeals" and "changed
  assurances" each describe one incident.
- **Layout**: Table 4 floats into §4.1 above the heading of the subsection that discusses
  it. Figure 2 lands between Transcript 5's "What happened" and "What this shows". Pages
  8, 10, 16, 24 and 33 are largely empty.

## Position on the eight incidents

G2, G15, G13, G18, G12 and G20 each tie a statement to a ledger consequence and earn
their place. G19 is a clean demonstration that acceptance is not endorsement, though the
card should say the swap completes nothing if that is what the ledger shows.

G7 is the thinnest. It shows a $25 gap between a public "final" and a private ceiling,
with no follow-through into construction, distress or succession, which is the paper's
own organizing frame. G2 already contains a public-final-versus-private-ceiling bluff.
My starting view is that G7 can stay only as a short contrast and would be better with
one sentence of ledger follow-through, or moved to the appendix. I regard this as an
editorial preference, not a defect.

## What I do not expect to ask for

No new games, replays, branches, reference policies or model calls. Every item above can
be settled by reading retained records or re-tabulating existing ledgers.
