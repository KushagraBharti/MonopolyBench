# Verification record (Fable 5.2 cross-review)

Written 2026-11-11. Everything here was done by me in this session, without subagents. Nothing in this review ran the game engine, a game, a model call, a synthetic test, a reference policy or a transfer test. "Checked" below always means a re-tabulation of a retained ledger or a reading of canonical saved-game records.

## 1. What was read, and in what order

1. `cross_review_contract.md`, `rewrite_contract.md`, the repository `CLAUDE.md`.
2. Astra draft: `manuscript.tex`, `main.tex`, `conduct.tex`, `discussion.tex`, `appendix.tex`, `transcript_quotes.tex`, `handoff.md`, `literature_updates.md`.
3. Sol draft: `manuscript.tex`, `conduct.tex`, `temporal_discussion.tex`, `appendices.tex`, `handoff.md`, `literature_updates.md`.
4. Opus draft: every file under `sections/` including the generated tables and `opus_quotes.tex`, `preamble.tex`, `handoff.md`, `literature_updates.md`.
5. Fable 5.2 draft: every file under `sections/`, `handoff.md`, `literature_updates.md`.
6. The user critique (attachment `…e93d92bb…txt`) and the question transcription under `research_guidance_2026-10-29/`.
7. Five checks of my own (section 2, rows 1 to 5).
8. **`initial_position.md` written.** The unread `reviews/astra/all_four_review.md` had SHA-256 prefix `8784a3406df9a546`.
9. `reviews/astra/`: `all_four_review.md`, `comparison_in_progress.md`, `check_counteroffers.py`, the three JSON outputs, `literature_followup.md`, `render_review.md`.
10. Further checks, literature fetches, the replacement prose and the reports.
11. `integrated/` (appeared during the review): `manuscript.tex`, all section files except the appendix, and `integration_decisions.md`, read once after step 10. Not edited.

Not read: `reviews/sol/`, `reviews/opus/`, the appendix of `integrated/`, the evidence maps and figure-decision notes of the four drafts beyond what the handoffs quote, the full 29 October manuscript.

## 2. Checks performed

All scripts are in `tools/`, all outputs in `data/`. They import nothing from the engine.

| # | Script | Reads | Establishes | Result |
|---|---|---|---|---|
| 1 | `check_offers.py` | `data/agenda_offers.json`, `contracts/data/board.json` | Cells by response, position, recipient, block, game; counter content with a non-completion baseline; pure repricing; asks relative to offer and list; deed direction against cash direction; one-deed price ratios; thread outcomes; seller cash | Reproduces every count in the four drafts that I tested. New: 87 of 110 and 81 of 110 baselines; 309 of 313; 1.56 against 1.54; position split |
| 2 | `check_windows.py` | `data/first_management_windows.json`, canonical `decisions.jsonl` of ten games | Menus, cash, mortgaged deeds and applied notes in the nine windows that never listed construction | Four Grok windows with redemption on the menu and a reserve note; five Opus windows without notes; eight with a mortgaged group deed |
| 3 | `check_economy.py` | phase-1 episode ledger, `agenda_flows.json`, `t01_cohort.json`, `t06_eliminations.json` | Routes, terminal and in-play estates, rent by route, creditors, first completions, seed-block purchases, elimination partition | 121 = 69 + 52; 45 of 52; 35 of 40; 16 and 18 games; \$11,472; blocks 3 and 4 confirmed |
| 4 | `check_quotes.py` | `opus_quotes.tex`, `quotes_supplement.tex`, canonical `decisions.jsonl` | Exact spans, speaker, attempt label, and presence of each public message in every other live player's next delivered prompt | 24 of 24 spans found; 15 of 15 public messages delivered to every other player checked; eight Fable cards labelled "excerpt" are whole fields |
| 5 | `check_records.py` | canonical records, `resolution_conditions.json`, `agenda_rejection_reasons.json`, flows, eliminations, spending units | Actor at G2 d243; conflict joins; bankruptcy-related conflicts; Grok's cash path in G13; liquidation menus and notes at four eliminations; split of the 74 rejections; arithmetic in quoted notes; incident chronologies | See findings FX-D03, FX-L01, FX-L02, FX-I02, FX-B05, FX-C01, FX-C05 |
| 6 | `build_review_quotes.py` | canonical `decisions.jsonl` (G14, G16) | Two inline excerpts used by R5, each occurring exactly once in the named note | `review_quotes.tex`, `data/review_quote_manifest.json` |
| 7 | `check_replacement_numbers.py` | outputs of 1, 2, 3, 5 and the offer ledger | Every number I print in `replacement_prose.tex` that I recomputed, and presence of each literal in the TeX | 105 assertions, 0 failed |
| 8 | `check_frozen.py` | `baseline_source_hashes.json`, `reviews/astra/review_source_hashes.json` | That frozen sources and drafts are unchanged; hashes of the 39 inputs my scripts read | 272 of 272 and 81 of 81 match |

Also read directly, without a script of their own: the engine functions `_buildable_space_indices` and `_unmortgageable_space_indices` (to confirm when construction and redemption are listed), and one standard and one action-only system prompt (G13 d252, G13 d251) to confirm the two deception sentences quoted in R2.

To reproduce, from `tools/`: `python3 check_offers.py; python3 check_windows.py; python3 check_economy.py; python3 check_quotes.py; python3 check_records.py; python3 build_review_quotes.py; python3 check_replacement_numbers.py; python3 check_frozen.py`. Any Python 3 works. No third-party package is needed.

## 3. Inherited results I did not re-execute

- All engine executions: three payment witnesses, the G7 mortgage-only search, 63 of 70 reorderable construction targets, replay of 50,918 events, state reconciliation with 6,989 prompts and 10,235 snapshots, the G3 and G13 exact-prefix alternatives.
- The 61 agreed rival-consequence codes and the 240-decision coding. My split of the 74 uses the first reader's codes because the retained file does not itemize the agreed set.
- Formatter, delivery, memory-window, token, latency and refusal-message counts.
- Recipient delivery for the 28 baseline quotations.
- 57 of 60 debts as rent on a developed group, recovery and recurrence tables, the END provenance table.
- Astra's reading of the G2 d129 attempt chain.

Where the replacement prose uses one of these it says "earlier audit" or "inherited", and R12 prints the split.

## 4. Render and build

- The four draft PDFs were not rebuilt. I rendered them with PyMuPDF into contact sheets (`render/*_contact_*.png`, 50 dpi, eight pages per sheet) and looked at all eighteen sheets, and at three pages at reading size: Fable 7 and 18, Sol 10. Page counts 23, 25, 43, 39. I did not read every page at full size and did not validate figure marks against data.
- What the sheets show. No clipped text, no table or card running off a page, no missing glyph boxes in any of the four. Astra: one figure (page 8), seven incidents on pages 11 to 15. Sol: offer figure page 7, finance figure page 10, a short last page of references. Opus: conditions table page 5, the coverage table alone on page 26, references on pages 28 to 30 with long notes, and several half-empty appendix pages (41 to 43). Fable: figures on pages 7, 13, 16 and 18, coverage table on page 24, a dense all-eliminations table on page 35, and a nearly empty last page. Sol plots the bound on the vertical axis and debt on the horizontal. Opus and Fable plot them the other way round. The integrated paper needs one orientation.
- `replacement_prose.tex` compiles stand-alone through `build/replacement_build.tex` with `latexmk -lualatex`: 20 pages, 0 overfull boxes, 0 undefined references or citations, no text block outside a page. The only warnings are four hyperref "empty link" notices from labels that I stubbed because they live in unchanged material (`inc:insurance`, `inc:bankruptcy`, `app:incidents`, `tab:recovery`). The wrapper reads the Fable preamble, the three quote files and the Fable bibliography by relative path and writes only under `build/`.
- I looked at all three contact sheets of that PDF and at pages 5 and 18 at 80 dpi.
- I built no figure.

## 5. Citations inspected

Fetched on 11 November 2026 through a tool that converts a page to text and answers questions about it with a small model. It does not return long verbatim passages, so I report section pointers and paraphrase, and I put no quotation from these sources in the replacement prose. A person should confirm the appendix letters before a camera-ready.

| Source | Page fetched | What I confirmed | Consequence |
|---|---|---|---|
| AgentMonopoly, arXiv:2610.29330v2 | HTML | Four families (Qwen3, DeepSeek-R1, Gemma, Mistral) at two sizes; five seeds; Table 3 sums to 140 games; prompt encourages bluffing and prohibits public messages contradicting the action (Section 4, Appendix A.2); elimination when cash becomes negative (Sections 4 and 6); "larger models do not consistently win more games". **Not stated in the paper:** what happens to a bankrupt player's property, and whether a recipient can counter | FX-R01. The three drafts' statements about its creditor rule and single-offer trades rest on the earlier repository inspection, which I did not repeat |
| FinBoardBench, arXiv:2605.27896v1 | HTML | Appendix C.3: player creditor receives property, buildings sold to the bank. Appendix D: trade manager with accept, reject, counter. Appendix E: at most five action execution failures, then a forced fallback recorded as system-forced. Section 3.1: one focal model against three fixed LLM opponents. Section 3.2: purchases continue under low liquidity | FX-R03, R9 |
| Arena communication study, arXiv:2608.14825 | abstract page, v3 | 2,583 emails, 20 runs, 13 models, 12.6 percent labelled misaligned, replication with two other judge families, odds 1.65 and 1.58, rank does not predict rate | Matches Sol, Opus and Fable |
| DECE, arXiv:2610.35773 | abstract page, v1 | Singular "Eurogame" in the title; ten games, 12 configurations, 480 primary and 1,032 total matches; same model differs across harnesses | Matches |
| Cattle Trade, arXiv:2605.14537 | abstract page, v1 | Strategic coherence correlates with rank more than spending volume or any single subskill; two heuristic agents outperform most LLMs; 242 games | FX-R02. My draft's "coherent spending predicts rank" is wrong |
| Cosentino et al., arXiv:2605.16575 | abstract page, v1 | Accurate counterparty modeling does not reliably improve outcomes; agreements follow opening anchors | FX-R02. My draft's "concede without compensation" is not in the abstract |

Not checked by me: every other entry in the four bibliographies, the AgentMonopoly repository, MERIT, Empty Commitments, Hardy et al., Yang et al. I rely on Sol's and Astra's notes for those and say so.

Bibliography keys: Sol and Astra use `yang2026measurement`, Opus and Fable use `yang2026measurementfirst`. `merit2026` exists only in Sol's file. Nine entries exist only in Opus's.

## 6. Errors of mine, found and corrected

**In my frozen draft** (not edited; recorded as findings): FX-B03, FX-B06, FX-D01, FX-D02, FX-D05, FX-I01, FX-I02, FX-I04, FX-C05, FX-C06, FX-R02, FX-S02, and Astra's F6, F7, F9, F10.

**In `initial_position.md`** (left as written):
- I ranked G2 as the lead incident and did not notice that its note's "nine yellow houses" is wrong. Astra's O1 caught it. Recorded as FX-X01.
- I attributed "building sales that the displayed mortgage options did not reveal" to the Opus abstract. It is in the Opus introduction, contribution item 3. Corrected in `findings.json`.

**While preparing this review** (corrected before delivery):
- `check_windows.py` first asserted that every decision listed for a window followed the completing settlement. The ledger also lists same-turn decisions before it. The script now skips those and reports them.
- The first replacement draft said six of seven incidents involve Grok (five), thirty percent of prompts (29), "first bids" where the offers are bids at any position, "the two deeds Grok refused to trade" (one), and repeated Opus's "after raising its cash offer by a median" where cash rises in 18 of 24 threads.
- The first replacement draft "corrected" a \$239 figure in the G1 note that the displayed excerpt does not contain. The sentence now corrects only the displayed \$220.
- The first replacement draft typed three short quotation fragments by hand (two from the G2 messages, one from a fetched FinBoardBench summary). All three are now paraphrased, and the two note excerpts in R5 are generated.
- `findings.json` initially carried eleven wrong line numbers and two passages that did not match their files. A script now checks every passage against its file.
- The integration proposal first said Sol speaks in three of the seven incidents (four) and that Opus and Astra checked five and six G2 messages (G2 has four public messages).

## 7. Frozen sources and write scope

- `check_frozen.py`: all 272 hashes in `baseline_source_hashes.json` and all 81 draft hashes that Astra recorded match the files on disk after my work.
- `git status` shows no change to any tracked file. The only untracked path is the rewrite package, as at the start.
- Every file I created is under `reviews/fable_5_2/`. Python bytecode caches are under `reviews/fable_5_2/tools/__pycache__/`.
- No commit, no push, no message to any peer.

## 8. Limits of this review

- I am one language model reading four drafts, one of them my own. The findings on my own draft are the ones I could see, and Astra saw five that I did not.
- The stratifications I add (position, deed direction, pure repricing, price relative to list) were chosen after seeing the data, like every other cut in this project. They correct two overreadings. They do not identify anything.
- The window check is arithmetic on cash and collateral. It supports "construction was never listed, for a stated reason in four windows and with little cash in five". It does not show which windows could have reached a house.
- G13's cash path is the observed path. It says nothing about the path without the sale.
- The snapshot of `integrated/` is one reading of a moving target.
- Nothing here makes the paper acceptable at any venue. Section 7 of `review.md` gives three reasons a careful reviewer could still reject the best version of it.
