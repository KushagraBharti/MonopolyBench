# Initial position

Fable 5.2, whole-paper final review, 15 November 2026.

Written before opening `INTEGRATION_DECISIONS.md`, the `adversarial/` folder or any other reviewer's `final_review` folder. The task brief itself told me three root decisions in advance: the 28/30 count was rechecked against actions, the 43/48 numeric-presence count is kept only in the supplement, and the 5/37 claim was declined because 121 entries have unlisted collateral. Everything else below is my own reading.

## What I read

- `FINAL_REVIEW_BRIEF.md`, `BRIEF.md`, `INTEGRATION_CRITERIA.md`.
- The integrated candidate in full: `manuscript.tex`, `sections/main.tex`, `sections/final_supplement.tex`, every file those two input (all channels for the sixteen, casebook, rubric, tables, quote files, prompts), the bibliography as compiled, `README.md`, `evidence_map.md`, `build.sh`, all seven scripts under `tools/`, the QA records, and rendered pages 1 to 12 and 19 to 24 plus page 4 at full size.
- All four frozen drafts: main text, appendices, handoff, changes and dissent, evidence map, verification and README for Astra, Sol, Opus and Fable 5.2. Astra's draft is the base of the integrated candidate, so I read it as a diff against the candidate. Source-field printouts that repeat the same sixteen responses were compared by hash or read once.
- Eleven section files in `integrated/sections/` are not used by the build. Ten are byte-identical to the November 12 package and one to Sol's `sixteen_full.tex`. I did not re-read them as manuscript text.

## Pins

Both matched before reading: 2,396 of 2,396 files in `integration_review_manifest.json` (manifest SHA-256 `a362c4c6…e269`, PDF `e5c44beb…0dae`), and 84 of 84 in the November 12 `final_manuscript_manifest.json`.

## Overall judgment at this point

The candidate is a coherent observational paper and I would support its release after a short list of local changes. I have found no factual blocker so far. Every number I recomputed from the raw decision logs matches the manuscript.

The argument holds together in this order: payment is weak evidence because valid continuation suffices; the informative records are what agents count, what they keep and whether they stop; sixteen debts show the count going past the menu or stopping at it; bargaining shows the same accounting applied to rivals. The main text ends on page 7, so there is room for the few additions I think the paper needs.

## Checks completed before this note

All are arithmetic or reading over existing records. Nothing was executed.

| Claim | My result |
|---|---|
| 188 episodes, 128 paid, 60 eliminated, $51,997, 180 mortgages, 89 sale actions, 67 one-action and 61 multi-action payments, no fallback in a payment | Reproduced from `decisions.jsonl` |
| 131 payable; 62/53/16 with 62/52/14 paid | Reproduced. The three declared-payable witnesses are inherited |
| First actions: 3 declarations in 132 covered, 50 in 56 short, 8 forced menus, 6 above-bound starts | Reproduced, with the same six entries |
| 28 of 30 | Reproduced. Membership equals the shipped `development_preservation.json`. Both sellers are Opus, one house each |
| 108/12/9/2 proof classes; complete ownership and evenness in all 131 | Reproduced. G3 d456 has bank 0 and 8 free houses, G3 d461 has 6 and 2, one hotel per hotel-bearing group in both |
| Proof premises in the engine | Read `_resolve_pending_payment`, `_mortgageable_space_indices`, `_sellable_building_space_indices`, `_apply_sell_plan` and `_validate_sell_plan`. They say what Appendix C says. The bundled-sale paragraph is correct: with one hotel per group, a house in a hotel group cannot be sold unless the same plan removes the hotel |
| Rubric 5/3/5/1/2 and 11 notes plus 5 explanations | I read all sixteen selected fields and reach the same assignment. Every remainder in the rubric table matches the route arithmetic |
| 920 responses, 918 legal, 113/394/413, per-recipient counts, 110 of 173 cash bids by Opus | Reproduced from the stored ledger |
| 61 of 74, 27/38 and 34/36, each reading 63, four disagreements, nine common negatives, disjoint from the swap contrast | Reproduced from the two shipped coding files |
| G7 New York negotiation | All three new quotations and the sequence check out at d141 to d151. Five mortgages raise exactly $450, four orange houses are built on turn 68, Sol builds three dark-blue houses on turn 71 and sells one on turn 72, and orange rent after the sale totals $270 |
| Static build | Copied sources compile in my folder to 29 pages with text identical to the pinned PDF and no LaTeX warnings. The PDF bytes differ in 60 positions near the trailer, so the published hash is tied to the build directory |

## What each draft added, and what I expect to find kept or dropped

From reading the drafts against the candidate, not from the decision log.

- **Astra.** The base: structure, tone, the supplement. Kept.
- **Sol.** The two-case opening is adopted. The source constructions for the five middle-row payments are adopted in prose. Sol's six-row table of above-bound starts, its ownership-stakes figures and its wider related-work paragraphs are not in the candidate.
- **Opus.** The 28/30 finding and the richer G7 negotiation are adopted. Four things are reduced or gone: the first-menu table by region and system, the statement that every individual asset value in the sixteen texts is right except one aggregate, the observation that successful texts pass through the listed-only total, and the published-versus-implemented rules table.
- **Fable.** The bundled-sale extension is adopted. The 43/48 count is in the supplement with narrowed wording. The 5/37 count, the carried-note table and the other selective-financing counts are not in the candidate.

## Concerns I hold before reading the decisions

Ranked by how much they matter to the paper's argument.

1. **The abstract asks how agents assess resources that become usable after an action, and the main text answers from sixteen payable debts when the same judgment is on record in 37.** In 21 of the 48 unpayable first responses with a financing option, buildings lock further mortgages, so the full bound differs from the listed total. I read all 21. Sixteen contain the full-bound figure inside an itemization that names the released mortgages, two itemize them without a total, and three give the listed-only total as a maximum (Sol G3 d426, Opus G5 d309, Grok G8 d280). With the sixteen payable debts that makes 32 of 37 first responses that count or raise the locked collateral and five that stop at the listed total, from all four configurations. The supplement's 43/48 mixes these 21 with 27 cases that have nothing locked, and that split is where the information is. The objection I was told about (121 entries have unlisted collateral) is right about Fable's wording and does not touch the scoped population: episodes where listed resources fall short of the debt and buildings lock more. That set is exactly 37. I regard this as the strongest positive result missing from the main text, and also the right denominator for the two failures.

2. **"Decisions to stop" are named as a discriminating observation, and the main text then gives no population for them.** Section 3.3 says six above-bound episodes start financing but never says out of how many. The two-row first-action table sits in Appendix D as context for departures. One sentence in the main text would fix this without making it an accuracy score.

3. **Both failed totals equal the listed-only total exactly, and at least five successful fields state that same subtotal before adding released mortgages** (G1 $126, G2 $283, G5 $674, G11 $276, G18 d309 $412). The main text describes the two sums and does not say this. It is a description of texts and needs no claim about cause.

4. **The 28/30 paragraph says "preference".** In every menu that offers both actions, `mortgage_property` is listed before `sell_houses_or_hotel`, and a sale is offered in 29 of the 30 first menus. The paper cites work showing that menu order can change behavior. The count is right; the wording should stay descriptive and state the order.

5. **Literature wording.** The Arena study's human check is a 50-email single-annotator consistency set, and its labels come from model judges, so "with a human annotation check" overstates the contrast with this paper. The sentence grouping three negotiation papers as separating language from strategy fits He et al. better than the other two.

6. **Release.** Eleven unused section files ship in the package, and four contain wording the November 14 review withdrew. The entry-point path does not exist at any commit yet. `qa/portability.json` describes an earlier archive. The README still says finalization is in progress. These are packaging matters, and the brief already says the archive will be regenerated.

## What I will test against the decision log

- Whether the reason for declining 5/37 addresses the scoped population or only the wording.
- Whether dropping the U0 observation and the first-menu table was a judgment about overreach or about space.
- Whether anything from Sol's or Opus's drafts that bears on the eight incidents or the rules disclosure was lost without a recorded reason.
