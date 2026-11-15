# Verification record: Opus cross-review

Reviewer: Opus xhigh (Claude Opus 5.5, `claude-opus-5-5`). Date: 2026-11-10. No subagents.

## Scope of reading

- **Astra:** `manuscript.tex`, `main.tex`, `conduct.tex`, `discussion.tex`, `appendix.tex`, `transcript_quotes.tex`, handoff, evidence map, figure decisions, initial position, literature updates, README.
- **Sol:** `manuscript.tex`, `conduct.tex`, `temporal_discussion.tex`, `appendices.tex`, handoff, evidence map, figure decisions, literature updates, initial position. Its `transcript_quotes.tex` is byte-identical to the shared file (`diff`).
- **Opus (own):** every file in `sections/` (main sections, eight appendices, six generated tables, `opus_quotes.tex`), handoff, evidence map, figure decisions, initial position, literature updates.
- **Fable 5.2:** every file in `sections/` (main sections, six appendices, `generated_tables.tex`, `quotes_supplement.tex`), handoff, evidence map, figure decisions, initial position, literature updates.
- **Not read:** the peer PDFs page by page. I read the LaTeX sources in full and relied on Astra's render review for peer page layout.
- **Order:** `initial_position.md` was written before I opened any file in `reviews/astra/`. I then read `all_four_review.md`, `comparison_in_progress.md`, `counteroffer_checks.json`, `fable_addition_checks.json`, `new_quote_checks.json`, `literature_followup.md` and `render_review.md`, and the `review_source_hashes.json` listing.

## Checks performed in this review

All scripts are in `checks/`, read retained or canonical files only, and import no engine code. Outputs sit beside them.

| Check | Script / output | Inputs | Result |
|---|---|---|---|
| Construction access for the nine never-legal windows | `never_legal_access.py` → `never_legal_access.json` | `data/first_management_windows.json`, canonical `decisions.jsonl` prompts for every window decision, `contracts/data/board.json`. Rules read (not run) from `engine.py` `_buildable_space_indices`, `_unmortgage_cost`, `_mortgage_value` | 2 of 9 cash-feasible (redeem + one house) at the window's first decision (G14 Grok, G16 Grok). 7 of 9 feasible if the owner also mortgages its own deeds outside the group. 2 not feasible (G15 Opus, G20 Opus). G16 Opus redeemed Park Place and stopped at \$75. Bank stock was positive in all nine. |
| Opus first-window composition | read of the `first_management_windows.json` summary | same | Opus 15 = 7 built, 5 never legal, 3 default after refusal. Opus window-eligible 10: 7 built, 3 defaults (`t03_trade_groups.json`). |
| Offer cells, cash direction, list price, counter join | `offer_checks.py` → `offer_checks.json` | `data/agenda_offers.json`, `board.json` | Cells reproduce 920/918 and all four rows. The completing side receives a deed in 429/429 one-sided offers and pays in 373/429. List-price medians as in `review.md` §6. Counter join reproduces 92/111, 88 → 85 up (median +125), 13 swaps (−560), 6 drops, neither 135/164. |
| List-price robustness | `list_price_robustness.py` → `list_price_robustness.json` | same | Buyer bids show no consistent completion markup. Seller asks are higher in every split, but the gap shrinks within strata (see "Reviewer errors" below). |
| Cash-poor settlements and thread position | `settlement_checks.py` → `settlement_checks.json` | `data/agenda_offers.json` | 48 completing paid settlements, 21 with a seller under \$100, medians \$194 v \$571. Opus is the seller in 21 of the 48 and in 13 of the 21. First and later cells reproduce Fable's position table. |
| Completion routes | inline script → `route_checks.json` | `paper_phase1_2026-10-28/sol/group_episodes.jsonl`, `data/t01_cohort.json` | 121 estate completions = 52 during play + 69 terminal. Winner-owned: 45/52 estate (during play) v 18/63 trade. Rent: 14/52 estate groups (\$11,472) v 51/63 trade groups (\$57,378). |
| Grok content v received names | inline read of `data/resolution_conditions.json` | same | 139 selected conflicts: 60 end→propose, 22 build→end, 11 buy→auction, 6 reject→accept, 1 counter→accept, 5 declare→mortgage, 2 declare→sell, 1 sell→declare. G20 d97 is mortgage→end. |
| G2 incident facts | inline reads | `agenda_offers.json` G2 d124–128 and d197–198, `agenda_flows.json`, `t05_spending_units.json`, `t06_eliminations.json`, `group_episodes.jsonl` | Offer chain confirmed. Sol's yellows collected \$44 of rent and \$0 of developed rent (corrects my draft). Elimination at d239 with \$77 against \$1,300 confirmed. |
| G15 state | inline read of the canonical G15 d168 prompt | `decisions.jsonl` | Gemini holds three houses on each orange, Sol has \$730 and Grok \$333. The holdings match Fable's setup. |
| Block 3 and block 4 patterns | inline read | `group_episodes.jsonl`, `t01_cohort.json` | Block 3: seat 2 buys dark blues at turn 29 in G9–12, and the owner wins all four. Block 4: seat 1 completes orange by purchase at turn 47 in G13–15, and the owner wins all three. |
| Baseline integrity | inline sha256 | `baseline_source_hashes.json` | 272 of 272 unchanged. |
| Draft integrity since Astra's review | inline sha256 | `reviews/astra/review_source_hashes.json` | 81 of 81 unchanged. |
| Findings passages | `build_findings.py` → `../findings.json` | four draft source trees | All 61 quoted passages are exact substrings at the stated line numbers. |

## Inherited, not re-derived

The following results come from the 29 October certificate package and reviews (or from named peers) and are reported with their scope:

- Every engine execution: the three payment witnesses and their remainders, the G7 restricted search, the 61/63 reachable multisets and the 70-target diagnostics, full replay of 50,918 events, and reconciliation of the 6,989 prompts and 10,235 snapshots.
- The formatter and delivery counts.
- The 74-rejection and 240-sample semantic codes.
- Token and latency figures.
- Recipient-prompt delivery for the shared-manifest incidents.
- Fable's reading that Grok's notes defer redemption at its four never-legal purchases. I did not re-read those notes.
- The G15 "drops cash, adds Kentucky" step, from Fable's ledger reading.
- The G18 Illinois purpose statement.
- Astra's G15/G11 delivery checks and its 79/88 pure-cash counter refinement.

## Literature checks (primary arXiv abstract pages, fetched 2026-11-10)

| Source | Checked claim | Result |
|---|---|---|
| Yang et al., 2610.05830v1 | My draft: a contamination-claim audit with matched controls and scorer validation | Supported. The reproduction scorer also failed its validation gate. |
| Liang & Xu, 2608.07538v1 | My draft: provider identity predicts surplus capture better than capability rank | Supported at abstract level. Full text not read. |
| Cosentino et al., 2605.16575v1 | My draft and Fable: accurate preference modeling; anchoring | Supported, but accuracy is conditional on the agent being given partner preference information. "Concede too readily" is only partly supported (weakly compensated concessions by the informed side). |
| Shah et al., 2512.13063v1 (NeurIPS 2025 workshop) | Fable: anchoring at extremes; "concede too readily" | Anchoring supported. Ready concession is not (the abstract stresses rigidity). |
| Müller & Müller, 2605.14537v1 | Fable: "coherent spending predicts rank" | Not supported as worded. The abstract says strategic coherence is associated with rank more strongly than spending volume or any single subskill. |
| Chen et al., 2606.18543v2 | Fable: all models below a rule-based baseline | Supported. |
| Li et al., 2608.14825v3 | All drafts: 2,583 emails, 20 runs, 1.58× low-inventory odds, rank does not predict misalignment, cross-judge replication | Supported. |
| Wu et al., 2610.29330v2 | All drafts: four families at two sizes, persona effects, larger models not consistently winning, five seeds | Supported at abstract level. Rule-level comparisons (inheritance, single-offer trades) remain inherited from the 29 October source review. |

I did not read any full paper in this pass.

## Render and build scope

`replacement_prose.tex` was compiled with LuaLaTeX in `build/`, using the shared `preamble.tex`, the shared quote macros, my draft's `opus_quotes.tex` and Fable's `quotes_supplement.tex`, plus a merged copy of the two draft bibliographies (copied into `build/`; originals untouched).

- The result is 12 pages with no LaTeX errors and no overfull boxes.
- One undefined reference (`sec:conditions`) is expected, because that label belongs to the integrated paper.
- All 16 `\TranscriptQuote` IDs used are declared in the three quote files; undeclared IDs would render silently as nothing.
- Probed quote strings were found in the PDF text with PyMuPDF from the repository virtualenv.
- I inspected pages 3, 4 and 10 at 70 dpi.

I did not rebuild any peer PDF.

## Reviewer errors found and corrected during this review

1. **Seller-side list-price gap overstated in the initial position.** `initial_position.md` reports pooled seller asks of 1.63× v 1.08× list as "sellers mark up completing deeds". The later robustness split shows the gap shrinks to 2.31× v 1.82× among unmortgaged deeds and 2.21× v 1.85× among later offers. `review.md`, `findings.json` (OPR-03) and `replacement_prose.tex` use the stratified wording ("somewhat higher in every split"). The initial position is left as written, as the record of an unanchored view.
2. **G7 v G2.** My initial position put G7 in the main text. After reading Astra's review I changed to G2 (with the arithmetic flag), with G7 as a contrast. This change was influenced by Astra and is disclosed in `review.md` §5.
3. **G2 rent claim.** While writing the G2 replacement card I found that my own draft's "collects no rent" is wrong: \$44 of rent, \$0 developed (added as OPR-33). My initial position had missed it.
4. **Findings build.** The first build of `findings.json` failed eight passage matches because of escaped apostrophes in raw strings and three wrong line numbers. Corrected; all 61 now verify.
5. **Wording fixes in my own outputs.** In replacement prose: "valid end-of-turn choices" → "actions" (the ledger disclaims choice), and "Six involve Grok" → five once G2 replaced G7. "Players priced and refused trades in terms of who would inherit" was narrowed to three named exchanges. In `review.md`: "a third of initial prompts" → 2,054 of 6,989 (29%).
6. **Interpretive caveat on the access check.** The "own other mortgages" route counts deeds from other incomplete groups. In G1 Grok's dark-blue case that means mortgaging New York, an orange deed. This is legal under the engine's mortgage rule (no buildings), but it would sacrifice another group. The check states feasibility only.

## Limits of this review

- The access arithmetic uses the window's first decision and the engine's rules as read in source. It does not simulate the sequence and does not consider jail or bank stock beyond the recorded counts.
- List-price ratios ignore bundle context.
- I did not re-read the 74 rejection texts or the 240-sample decisions.
- I am the same model family as one evaluated configuration (Opus) and wrote one of the four drafts. Several of my findings correct claims about that configuration in both directions: the default-loss overclaim, and the never-legal reclassification of two illiquid Opus windows versus three that were financeable. Readers should weigh that overlap.
- This review does not establish the integrated paper's correctness or acceptance.

## Writes and side effects

Writes were confined to `reviews/opus/`: the six deliverables, `checks/` and `build/`. I made no edits to drafts, canonical games, engine, prompts, the prior paper, the outline or the literature review. No commit, push, game, model evaluation, engine run, synthetic test or reference policy. I sent no messages to peers.
