# Verification: what I checked and what I inherited

Fable 5.2 xhigh, final review, 12 November 2026.

## Pin

| When | Result |
|---|---|
| Before reading, 02:58 | 78 of 78 manifest entries match. PDF `f0312183aa8794ec08614966570395e55abd769410ff99f06992f25f314ed8a1`. |
| After writing, 03:36 | 78 of 78 match. Same PDF hash. No file outside `final_review/` under this revision folder has a modification time after 02:58. `git status` shows no change to any tracked file. |

The manifest does not pin `integrated/qa/` or `integrated/build/`. I did not use `qa/` page images or `qa/extracted.txt`. I rendered the pinned PDF myself.

## Boundary

I read saved files, did arithmetic on them, and built one LaTeX document in my own folder. I ran no game, engine, replay, baseline, branch, synthetic scenario, provider probe or model query. I used no subagent. I wrote only under `final_review/fable_5_2/` and my scratch directory. I made no commit. My modification-time scan printed file names inside the other final reviewers' folders. I opened none of those files.

## How to rerun my checks

From `final_review/fable_5_2/tools/`:

    python3 rebuild.py    # rebuilds 188 episodes and 920 responses from decisions.jsonl
    python3 checks.py     # recomputes every figure below and matches 35 new quoted spans
    python3 cards.py      # matches the 20 cards used in the paper against source fields

Outputs are `data/episodes.json`, `data/offers.json`, `data/checks.json` and `data/cards.json`. The scripts import only the standard library. They read `decisions.jsonl`, `events.jsonl`, the replay reports and `cloud/calls/*.intent.json` of the twenty canonical runs, and the integrated paper's sources.

## Checked against raw saved records

"Rebuilt" means I recomputed it from `decisions.jsonl` with my own code and compared.

| Claim in the paper | Where | Result |
|---|---|---|
| 188 financing episodes, 128 paid, 60 eliminated | 3.1 | Rebuilt. Debt, cash, generous bound and action list match the integrated ledger in all 188. Paid or eliminated is taken from the ledger, because four eliminations end without a declaration. |
| 67 one-action payments, 61 of two to ten, 180 mortgages, 89 sales, $51,997, no fallback | 3.1 | Rebuilt. All match. |
| 62, 53 and 16 payable debts by resource class, with 62, 52 and 14 paid | Table 2 | Rebuilt from entry states. Match. |
| 56 debts above the bound, 50 immediate declarations, 8 bankruptcy-only menus, 6 that liquidate first | 3.1 | Rebuilt. Match. Five of the six are Grok. |
| 3 payable declarations at the first menu | 3.1 | Rebuilt. G12 d190, G12 d249, G17 d234. |
| G7 Opus: $1,310 nominal, $750 debt, $440 reachable, no building sale offered | 3.1, App. D | Checked. Menu lists two mortgages and no sellable building. Bank houses 0. Holdings 4, 4 and a hotel on pink. |
| Sixteen necessity rows: debt, U0, U*, outcome | Table 9, Fig. 1 | Rebuilt. All 16 rows match. |
| Sixteen printed initial texts | App. B.1 | All 16 equal the source field after whitespace normalization. Channel labels are right: 11 notes and 5 Opus returned texts. |
| 13 state the resource, 1 tentative, 2 omit | Abstract, 3.2 | I read all sixteen and agree. This is one more model reading. It is not human annotation. |
| System split 2 of 3, 5 of 6, 5 of 5, 2 of 2 | 3.2 | Rebuilt. Match. |
| 19 payments use 33 mortgages absent from the first menu, and the five non-necessary cases | 3.2, App. B | Rebuilt. Match, including the five named episodes. |
| G12 d190 and G17 d234 sums and omitted collateral | 3.2 | Checked against requests and notes. |
| G12 d249: note, assistant content and applied call | 3.2 | Checked. |
| G5: carried note, returned text, applied note, $149 | 3.2 | Checked. Wording issue in FR-F52-08. |
| G20 payment: $49, two sales, eight mortgages, $700, $665, $14, Gemini's $675 and $690 | Incident 1 | Checked from decisions and events. |
| 920 responses: 113, 394, 413. 918 with legal acceptance. 526 threads | 4.1 | Rebuilt from the raw requests. Zero row differences from `data/offers.json` on completion, response, stage, legality and both models. |
| Every cell of Tables 3 and 5 | 4.1, App. A | Rebuilt. All match. |
| Proposer table, recipient table, 90/108 against 24/36, 93/112 against 26/43 | Tables 4 and 7, 4.1 | Rebuilt. Match. The conflict screen is my own and finds the same 64 openings. |
| Grok writes 36 of 72 comparator swaps and 15 of 17 acceptances, 13 from conflicting calls | 4.1 | Rebuilt. Match. |
| Block gaps and leave-one-block-out ranges | Fig. 2, Table 6 | Rebuilt. 28.7 to 33.3, 9.4 to 22.1, 15.7 to 26.0, -8.3 to -2.3. |
| 111 counters with 79 keeping the deed exchange, and 81 of 110 | 4.3 | Rebuilt. Match. |
| Cash bands 17/69 and 120/175, 44 counters, 43 later, 21 facing Opus, Gemini 10 of 11 | 5.1 | Rebuilt. Match. |
| 74 refusals of recipient-completing offers, 38 and 36 | 4.2 | Rebuilt. 62 of the 74 are by Gemini and Grok. |
| Grok: 139 conflicts, 64 of 136 openings, 7 of 28 acceptances | 2.2, 4.1 | Rebuilt with a name-in-content screen. Match. |
| 6,989 decisions, 8,679 attempts | 2.2 | Counted. Match. |
| Opus refusals 64/84, 40/60, 30/53, 80/109, then 1,390 of 1,390. One later refusal at G2 d129 | 2.2, App. E | Counted. Match. |
| 8,687 saved requests. Grok required tool choice, others automatic. Medium effort. No temperature, nucleus or token cap | 2.2, Table 1 | Read from all `cloud/calls/*.intent.json`. 1,705 required for Grok. 6,982 automatic for the others. |
| Liquidation instruction text | 2.1 | Identical in all 338 liquidation requests. |
| Both printed prompts | App. E | Equal to stored system prompts after whitespace normalization. |
| Two replay comparisons | App. D | All 20 artifact reports passed with an empty exclusion list over 50,918 events. All 20 state reports passed with four LLM event types excluded. I read the reports. I ran no replay. |
| Wins 8, 7, 3, 2 and 7, 7, 3, 3. The two block patterns. Turn range | 8, Table 11 | Checked by arithmetic on the printed table. |
| Twenty quotation cards | all incidents | `cards.py`: all 20 found in the named field of the named decision with the named system. The 13 labelled full field are exact. |
| G15: cash, three offers, Opus's appeal delivered, Grok bankrupt to Gemini 18 turns later, Sol never completes | Incident 2 | Checked. Earlier notes and appeals in FR-F52-02. |
| G2: $325 bid, $450 ask to Grok, warning delivered, $520 and three houses, $475 ceiling, turn-69 reversal, $44 rent, loss to Gemini | Incident 3 | Checked. |
| G19: proposal, abort note, end-turn content, correction, no group completed | Incident 4 | Checked. |
| G7: $625 ask, $600 against a private $625, Park Place and three houses with $84 left, $350 bid, $700 ask and its stated reason, five mortgages, four houses, turn-71 build, turn-72 sale, $270, elimination by Sol | Incident 5 | Checked. |
| G13: $35, $200, $130 counter, omission sentence, $1,926, $16, both buyer motives, missed roll, turn-114 auction, turn-150 bankruptcy to Sol, 5/36 in the earlier note and 4/36 later | Incident 6 | Checked. |
| G20 appeal: $500, $222, appeal delivered, three houses, Vermont $150 and $50, Opus's two later cash offers, Grok out first | Incident 7 | Checked. Cash path in FR-F52-12. |
| G18: public messages, withdrawal text, redemptions, bids and asks | Incident 8 | Checked. Returned text at d431 and turn count in FR-F52-01. |
| Purchase prompts carry price, group, house cost and rents. Liquidation menus carry keys only | 2.2 | Checked on one purchase request and on the sixteen first liquidation requests. |

## Recomputed from derived or stored files only

| Item | Source | Note |
|---|---|---|
| Seven same-deed asking pairs and the seller-by-mortgage cells | `integrated/data/single_deed_prices.json` | I recomputed cell medians. The definition of an ask and of a completing buyer is inherited. |
| Three payment witnesses and the G7 search | `paper_agenda_revision_2026-10-29/baseline/data/certificate_results.json` | Read. Steps and final cash agree with entry-state arithmetic. Not executed. |
| Share of sentences that bound an inference | LaTeX sources | Keyword screen. Approximate. |

## Inherited, not checked by me

- The 61 of 74 semantic reading, its 27/38 and 34/36 split, and the shares from Gemini, Grok, G1 and G15.
- Section 3.3: first-window building (16/17, 17/18, 7/15, 3/13 and the twenty other windows), $57,378 and $53,810, 38 of 40 eliminations, 227 deeds, 52 and 69 completions.
- Fourteen resistance-to-settlement histories and the median cash figures.
- 9/58 and 17/56 concession acceptances.
- Resampling percentiles in Tables 6 and 8. I rebuilt the inputs and the block and omission values, not the 3,125 and 20,000 draws.
- 2,054 prompts with misattributed trade summaries. I saw examples in the timelines I read.
- Cost figures, reasoning-token means and the 149 and 107 delivery counts.
- Rule statements in Appendix D other than the G7 menu.
- Source commits, repository URL and all bibliography entries. I opened no cited paper in this review.
- The root verifier's 738 protected entries and 234 frozen draft files.

## Rendering

Ghostscript 125 dpi PNG of each of the 21 pages of the pinned PDF, read page by page. Text, cards, tables and both figures are legible. Defects are in FR-F52-17. My replacement document builds with LuaLaTeX with no warning, and I inspected all six of its pages.
