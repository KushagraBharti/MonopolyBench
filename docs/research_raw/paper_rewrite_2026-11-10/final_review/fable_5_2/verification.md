# Verification record

Fable 5.2 xhigh, final whole-paper review, 11 November 2026. All paths are relative to
`docs/research_raw/paper_rewrite_2026-11-10/` unless they start with `saved_games/`,
`contracts/` or another repository folder.

## Pin

| Item | Result |
|---|---|
| `integrated/manuscript.pdf` SHA-256 | `8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5`, matches the pin |
| `integrated/qa/integrated_file_hashes.json` | 38 of 38 entries match, checked before reading and again at 07:06 UTC after all work |
| `baseline_source_hashes.json` | 272 of 272 protected files match |
| Repository HEAD | `a10419d239ff75f9e75a77d1634261a6ca24148c`, the checkpoint named in Appendix E |
| Frozen-draft manifest (81 files) | not re-hashed by me; the root's result is inherited |

Nine files under `integrated/data/` are outside the 38-file manifest. Seven are byte-identical
to the copy in the package `data/` folder, and the three quote manifests match
`integrated/source_manifest.json`. Their hashes at review time:

| File | SHA-256 |
|---|---|
| `data/agenda_offers.json` | `a2eb94342fe0d9c29ffe2c52baf9d29353e9c6309191e2b60c2eb8d14197216a` |
| `data/fable_quote_manifest.json` | `262843535759f5e0888585a82a2aaad34e092de50315fc24b6cb6f7cc4d514e0` |
| `data/first_management_windows.json` | `03512ecf45cdb49b59f14b479e6ace81d2692646f85fa6b52d035b227ab9c3bf` |
| `data/opus_quote_manifest.json` | `761f837872b8b743d6e0cac3495e801b3b445540b5369534a4ef15c2c610fcc3` |
| `data/t01_cohort.json` | `4839cdd176973c6f3bea45e4c0b7b9d16c3520ff3b0c1921d528ced73f5ecf2e` |
| `data/t03_trade_groups.json` | `e3f16a4afd534eecd4a8087cd07901485cff83fb5c3f55e28955c5f8cab5a1c9` |
| `data/t06_eliminations.json` | `ead910d4ac999c86642fff813fe915fac6e3001c92a794862fc59a927c0ebf34` |
| `data/t09_entry_nonbuild_records.json` | `fc1aebcc34d7dc0d16189cc59c864aa309d1d964c2e772365fc8acde0d9c1bab` |
| `data/transcript_manifest.json` | `4a0a4a7a657e418d79e3046e45bf3b613d12049557fd79a919c8db69ed7d0db2` |

## Order of reading

1. Hashed the PDF and the 38 files. While doing so I saw `integrated/README.md`,
   `qa/render_review.md` and `source_manifest.json`.
2. Read `manuscript.tex`, `preamble.tex` and all seventeen section files in document order.
3. Rendered the pinned PDF and viewed pages 1 to 28 and 30 to 33.
4. Wrote `initial_position.md`. I have not edited it since.
5. Read `final_review/astra/root_review.md`, `integrated/integration_decisions.md` and
   `integrated/evidence_map.md`, then the retained evidence listed below. Page 29 was viewed
   at this stage.

Other reviewers' folders and root adjudication files appeared under `final_review/` while I
worked. I did not open them. I sent no message and started no subagent.

## Scope kept

I ran no game, engine code, replay, branch, synthetic test, reference policy or model
evaluation query. My eleven scripts import only the Python standard library, plus PyMuPDF in
the one render script. No script imports the engine. The only build was a LuaLaTeX syntax
check of my own replacement prose, with a copied preamble, inside `build/`.

Every write is under `final_review/fable_5_2/`. I edited no shared file and no frozen draft.

## Checks performed

Scripts are in `tools/`, outputs in `checks/`. All ran with `python3 -I`.

| Script | Sources read | What it establishes |
|---|---|---|
| `check_offers.py` | `data/agenda_offers.json`, `data/t01_cohort.json` | Tables 2, 3 and 8 in every cell; 920, 918, 526; the two ineligible offers (G4 d219, G12 d228); 132/18/240/136 initiations; 414; 44; 32 and 81; block and game robustness counts; all 394 counter joins; Table 4; the coincidence of the two 92-counter predicates; 88, 85 within 88, $125; counter composition; nineteen accepted offers; 74 and its splits; every cash-at-settlement figure; 373 of 429; 309 of 313; four medians |
| `check_response_conditions.py` | 20 `decisions.jsonl`, 20 `events.jsonl` (line count) | 50,918 events; Table 1; 1,604, 1,605, 214 + 1 of 306, 1,390; one refusal text; the three-stage policy and the unused fallback model |
| `check_windows_prices_conflicts.py` | `contracts/data/board.json`, original prompts for the nine windows, `data/first_management_windows.json`, `data/resolution_conditions.json`, offer ledger | Table 11 in every cell; both G1 menus listing a build; four Grok notes and their $198, $220 and $110 figures; all sixteen Table 9 medians and counts; fifteen jail-card offers excluded; redemption overcharge principals 50, 90, 100, 110, 200 and no transfer-interest mismatch, by arithmetic; 64, 17, 7/1/3; first-window causes |
| `check_name_conflicts.py` | 20 `decisions.jsonl`, conflict ledger | 139 conflicts re-derived, identical set to the ledger; 1,068 selected responses with a named action in content, by a simple pattern |
| `check_estates_from_events.py` | 20 `events.jsonl`, cohort, board | 905 and $121,154; 113; 207; 107 and $28,425; $431 in 30 interest events; 397, 227, 202; $7,843, $7,148; 54, 35, 19; 18 and 16 games; G13's terminal estate to the bank; 57 eliminations ending on a color group with a player creditor |
| `check_quotes.py` | three quote files, 20 `decisions.jsonl` | 49 declared cards, 35 displayed, all found verbatim in the stated game, decision, attempt and channel; speakers match models; 17 "excerpt" labels on complete fields |
| `dump_decisions.py`, `dump_events.py` | named games | The incident reads below |
| `count_hedges.py` | section sources | Approximate density of scope-limiting sentences |
| `render_pinned_pdf.py` | pinned PDF | 33 page images and text in `render/` |
| `build_findings.py` | section sources | Asserts each quoted passage in `findings.json` sits at the stated file and line |

Three checks were run inline and are not saved as scripts: the row join of the two reason
codings (61 agreed; 29, 27, 4, 1 by configuration; 34 and 27 by cell), the route and rent
tabulation from `paper_phase1_2026-10-28/sol/group_episodes.jsonl`, and the tag counts in
`data/agenda_temporal_rows.jsonl` and `data/agenda_recurrence.json`. Each is a few lines over
the named file and the results are in `findings.json`.

## Original records read for incidents

| Incident | Records | Result |
|---|---|---|
| G2 | d117 to d129, d197, d198; events for turns 69 to 86 | Card figures confirmed. Sol's $450 ask to Grok at d119, mortgaged transfer, $26, $286, $410, six Gemini houses at turn 86 found |
| G15 | d167 to d176; estate events | Three offers and three refusals; $730, $333, $830, $233, $583, $480; first elimination at turn 81; estates as described |
| G7 | d42, d43; green purchases, turns 95 and 110 to 112 | Card confirmed. Auction at $171, elimination owing $1,400, estate to Sol, three houses at turn 112 found |
| G19 | d135, d136; offer ledger | Card confirmed. Cell is "neither"; Sol's note says "strictly favorable swap" |
| G20 | d94 to d102, d326 to d337; later offers | Chronology confirmed, including the malformed first attempt at d97 and $49 + $700 + $665 |
| G12 | d249 in full; d161 to d166 | Card confirmed. The note derives the five-sale route |
| G13 | d249 to d254 in full, d149 to d151; events for turns 55 to 114 and 146 to 150 | Card confirmed. Pennsylvania mortgaged at turn 63 and never redeemed; no Grok build in the game |
| G18 | d419 to d448; later offers | Card confirmed. The $150 and $225 bids are Opus's |
| G16 | d158 to d160, d601, d602 | Virginia plan confirmed. No liquidation at d602 |
| Holds and controls | G3 d176, G1 d426, G1 d119, G15 d129, G3 d362 to d364, G11 d255, G8 d159 to d163 | As described in the paper; G8 details in FF-D02 |

## Rendered pages

I rendered all 33 pages of the pinned PDF with PyMuPDF and viewed each one. No text, table,
caption or card is clipped. Both figures are legible. The two longtables repeat their headers.
Layout observations are in FF-W04. The PyMuPDF install is the one the README names at
`/tmp/monopoly-astra-rewrite-venv`; I used it read-only.

## Literature

| Source | How read | Confirmed |
|---|---|---|
| AgentMonopoly engine at `2434f427` | archived file in `integrated/qa/literature/`, SHA-256 matches `sources.json` | accept or reject only (line 359); bankruptcy on negative balance with no liquidation step; creditor receives properties with buildings unchanged (lines 536 to 545). The file holds no prompt text |
| AgentMonopoly, arXiv 2610.29330v2 | HTML through a fetch tool | title and authors; Section 4 and Appendix A.2 on bluffing and non-contradiction; Section 4 on negative-cash elimination; no statement on estates or counteroffers |
| FinBoardBench, arXiv 2605.27896v1 | HTML through a fetch tool | title and authors; Section 3.2 counter share; Appendix E five failures and recorded fallback; Appendix C.3 buildings sold to the bank |
| DECE, arXiv 2610.35773v1 | abstract page through a fetch tool | name, ten Eurogames, matched harness studies |
| Arena, arXiv 2608.14825v3 | abstract page through a fetch tool | 2,583 emails, twenty one-year runs, ground-truth state, two other judge families. Promise follow-through not confirmed at this level |

The fetch tool returns passages extracted by a small model. I did not read raw HTML. Other
references were not rechecked.

## Limits

- The witnesses, the hotel-lock search, the replays, the snapshot and memory reconstructions,
  and the 113 settlement predictions are inherited. I checked their printed summaries against
  retained ledgers only.
- Semantic labels are inherited. I joined and counted them and did not recode any row.
- Not re-derived: the 15 and 5 argument-equality counts, the history-formatter counts, the
  6,882, 149 and 13 delivery counts, the 1,394 memory count, the 103 spending units and their
  rent figures, the proposal-propensity turns, and the "developed" qualifier in the 57.
- For G8 and G13 I report that the content plans meet the cash, stock and evenness conditions
  by reading the recorded menu. That is not an engine check.
- The 1,068 denominator in FF-S02 and the hedge counts in FF-W02 come from simple patterns.
- I verified that each replacement number matches a source. I did not rebuild the manuscript
  with the replacements applied.
