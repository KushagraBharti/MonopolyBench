# Verification record (Opus finalization draft, 14 November 2026)

## Scope compliance

- **No new evaluations.** There was no game, rules-engine import or execution, replay, policy rollout, reference-policy run, solver or menu search, synthetic state, prompt or engine change, model or provider call, or judge call.
- **No subagents, commits or pushes.**
- **Write scope.** I wrote only inside `docs/research_raw/paper_finalization_2026-11-14/full_drafts/opus/`. Literature PDFs and HTML were downloaded to the session scratchpad, outside the repository, and searched there as text.
- **Other drafts.** I did not open any other author's folder under `paper_finalization_2026-11-14/full_drafts/`.
- **Script review.** I wrote every script in `tools/` and read each before running it. They read JSON records, board data and git blobs, do arithmetic, and write to `data/`, `sections/` and `qa/` in this folder. `tools/provenance.py` runs `git show <commit>:<path>` and `git rev-parse HEAD`, both read-only.
- **Network access.** Only for literature retrieval: arXiv and ACL Anthology abstract and BibTeX pages, the Hasbro rules PDF, the FinBoardBench HTML, the Guhe and Lascarides PDF, and the ICML workshop page. No request carried user or project details.
- **Protected manuscript.** The 12 November integrated manuscript's 84-file pin (`paper_revision_2026-11-12/final_manuscript_manifest.json`, SHA-256 `04d0a0d3ac02a337ebfc4c7426c184f85862e53d60984e8beaba724ab29e5460`) was checked after drafting: 84 entries, 0 mismatches.
- **Pre-existing changes.** The repository's other uncommitted changes (in `paper_review_2026-11-14/reviews/…`) were present before this task. I did not touch them.

## Mechanical checks (`tools/verify.py`, output in `qa/verification.json`)

| Check | Result |
|---|---|
| Quoted spans re-found verbatim in their original fields (note, public message, provider field, assistant content or carried note) | 55/55 |
| Prose number strings matching computed values | 37/37, plus per-system declaration counts and the named-action conflict count |
| Stated totals in the sixteen texts compared with U0, U* or the realized remainder | 18 of 18 comparable values match; one route total has no reference value (`data/sixteen_numeric_checks.json`) |
| Rule, resolver, runner, player-config and board sources | Byte-identical at both run commits and at head `863f8ef7` |
| Em dashes in authored prose (quotations excluded) | None |
| LaTeX warnings and overfull boxes | 0 and 0 |
| Undefined references or `??` in the PDF text | None |
| Pages | 22 in total; references begin on page 8, so the main text is under 8 pages |
| Main prose words, abstract through conclusion, without floats | 5,626, of which the abstract is about 290 |
| Deterministic rebuild | Two consecutive builds with an identical source tree produced identical PDF hashes |

I inspected every rendered page (`qa/p01.png` to `qa/p22.png`) at 90 dpi. I fixed wrapped identifiers in Table 1, an overfull Table 4, cramped labels in Table 6, flush-bottom gaps (now `\raggedbottom`) and the appendix float warnings. No clipped text or blank pages remain.

## Record checks run in this round

| Check | Result |
|---|---|
| U* for all 188 entries against the retained ledger | 0 mismatches |
| Partition | 62/53/16, with 62/52/14 paid |
| First-menu declarations | 1/116 for U0 ≥ D, 2/16 for U0 < D ≤ U*, 50/56 for U* < D; 8 menus offer only bankruptcy |
| Paid episodes | 128 payments with 180 mortgages and 89 sales; $51,997; 67 one-action payments; 0 fallback actions |
| Released collateral | 19 payments use 33 released mortgages; 14 of them are necessity payments |
| Financing order | Region A: 30 owners, 28 without any sale. Region B: 47 no-release payments, with excess of $2 to $94 and a median of $38 |
| Proposition 1 premises | All 131 entries are completely owned and even, with U* ≥ D. Classes: 108/12/9/2. G3 d456 has R = 0 + 8 and G3 d461 has R = 6 + 2 |
| Engine source read for the proposition | `_resolve_pending_payment`, `_build_liquidation_decision`, `_mortgageable_space_indices`, `_sellable_building_space_indices`, `_validate_sell_plan`, `_handle_bankruptcy`, `_trade_interest_cost`; resolver `_fallback_action` |
| Focal channels | 23 first decisions extracted with hashes. Opus attempt 0 is refused with no text; attempt 1 is recovery |
| Named-action scan | 338 liquidation decisions. Content names an action only for Grok (27/56). 9 conflicts, all Grok, 7 of them first actions |
| Liquidation payload fields | Across 338 payloads, holdings carry only `space_key`, `houses`, `hotel` and `mortgaged`; the menu carries only two key lists; no value or group fields |
| Corpus counts | 50,918 events; 6,989 decisions (Sol 1,961, Gemini 1,669, Opus 1,696, Grok 1,663); 8,679 attempts |
| Refusals | 1,604 Opus first-attempt refusals plus one later; every first attempt in G5 to G20 refused; G1 to G4: 64/84, 40/60, 30/53, 80/109 |
| Readable provider reasoning on final attempts | Sol 287/1,961; Gemini 1,316/1,669; Opus 1,560/1,696; Grok 1,662/1,663 |
| Bargaining re-tabulation | 920 responses (113/394/413) in 526 threads; opening swaps 95/116 vs 37/72 (30.5 points); no Grok authors 16.7; no conflicting openings 22.6; cash bids −5.0 pooled and −0.25 to +8.5 within recipients; 79/111 and 81/110 counters keep the non-cash exchange |
| Spot checks of inherited incident facts | G15 Grok cash $333 and the turn-33 "Don't sell Ventnor back to p4" note; G13 Opus accepts $200 at d253; G2 d119 to d128 sequence; G7 d141 to d146 sequence |
| Literature, read directly | Hasbro rules (selling, mortgage and bankruptcy clauses); FinBoardBench fund-raising and bankruptcy rules; Guhe and Lascarides embargo compliance; atomic-chess workshop abstract; arXiv and ACL metadata for 19 entries |

## Inherited and not rerun

- The 188-episode boundaries, from the earlier episode detector.
- The three engine-executed payment witnesses (leaving $38, $180 and $43) and the G7 restricted menu search.
- The offer classification behind the 920-response ledger, and the list of conflicting openings.
- Block-resampling and leave-one-block-out summaries.
- The 61/74 two-reader model coding.
- Incident continuations beyond the quoted fields and the spot checks above.
- The claim that every Opus refusal carried the same provider message.
- Replay-report results.

## Limitations of these checks

- The sixteen-text coding is mine (Claude Opus 5.5). It is not human annotation, and Claude Opus 5.5 is also one of the evaluated systems.
- Literature pages fetched as HTML were read as extracted text. Some peer-inherited facts (Menu Table 6, o1 Table 3, MafiaScope v3 figures) were not re-read by me in this round.
- `verify.py` matches number strings in the source. It cannot detect a correct number placed in a wrong sentence; I re-read the prose for that.
