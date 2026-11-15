# Verification record for the Fable 5.2 cross-review

11 November 2026. This file says what I read, what I recomputed, what I took on trust, and what could still be wrong. `./run_all.sh` re-runs every check and rebuilds the PDF. `file_hashes.json` lists a SHA-256 for every file in this directory except itself.

## Scope and compliance

- I wrote only under `reviews/fable_5_2/`. Temporary files went to the session scratchpad outside the repository.
- I ran no game, engine, replay, branch, model evaluation call, synthetic test or baseline. No script imports engine code. Rebuilding state or episodes from saved events is event reduction and not a new replay.
- I used no subagent and sent no message to a peer.
- I made no edit to a frozen draft, a canonical record, a prompt, the engine or any shared file. I made no commit and no push. `git status` shows the same two untracked directories as at the start.
- I read no review except root's `reviews/astra/delivered_drafts_review.md`, and that only after writing `initial_position.md`. A `reviews/opus/` directory appeared while I worked. I did not open it.

## Frozen drafts

`four_draft_hashes.json` has SHA-256 `b8741a1aef3fc5a7b57b7ed6d790b720c4800282fcb6de5eb6219f53ff8a1ce3` and 235 entries (Astra 46, Sol 53, Opus 63, Fable 73).

| Check | Match | Mismatch | Missing | File |
|---|---|---|---|---|
| Before reading | 235 | 0 | 0 | `hash_check_before.json` |
| After the last write | 235 | 0 | 0 | `hash_check_after.json` |

## What I read

For each of the four packages: `manuscript.tex`, every file under `sections/`, generated tables, `evidence_map.md`, `findings_and_limits.md`, `handoff.md`, `initial_position.md`, `literature_inspiration.md` and the README or build note. I read my own draft as the rendered text in `qa/manuscript_text.txt`, since its numbers are macros in the source. I viewed every figure asset of Astra, Sol and Opus and four of my own six as images. I did not page through the three peer PDFs. Their rendering was verified by their authors and is not re-verified here.

## Checks

All scripts are under `tools/` and write to `data/`. "Ledger" means `full_drafts/fable_5_2/data/a2_offer_ledger.json` unless stated. Check 1 confirms that it equals Opus's independent rebuild (`full_drafts/opus/data/offers_rebuilt.json`) on completion cell, response, both parties' cash, opening flag, recipient and acceptance legality for all 920 rows.

| Script | Reads | Establishes |
|---|---|---|
| `c1_cash_by_cell.py` | Both offer ledgers | Cross-ledger agreement (0 mismatches). Rejection by holder cash and completion cell, by recipient, thread position and block. The completion gap inside each cash band |
| `c2_refusal_to_sale.py` | Fable pair ledger, both offer ledgers, board file | The 14 refusal-to-sale pairs with declined and accepted terms. Base rate of falling cash in 38 unsettled pairs. Who opened the thread. Sales by holder cash band and holder |
| `c3_defensive_contrast.py` | Ledger, Fable price rows, board file | Opus's opening contrast with a like-for-like baseline, by block, recipient and game. Cash bids by price band. The capacity cut by recipient |
| `c3b_offer_type.py`, `c3c_swap_table.py` | Ledger | Opening and later offers by form (swap, cash bid, offer to sell) and completion cell, by recipient, author and block |
| `c3d_dedup.py` | Ledger | The same contrasts on the first occurrence of each bundle, without Grok authors, without Opus, and by game and recipient pair |
| `c3e_grok_conflict_openings.py` | Ledger, twenty `decisions.jsonl` files | The 64 conflict-opened threads, rebuilt from the proposing decisions (17 settle, as in the drafts). Contrasts without them |
| `c4_seller_conversion.py` | Fable pair, episode and conversion files | Seller outcomes by whether the seller held a complete group at the sale, at the player-game level |
| `c5_debt_census.py` | Twenty `decisions.jsonl` and `events.jsonl` files, the four drafts' episode files | An independent liquidation census closed on events. Engine defaults and Grok text and call disagreements inside episodes. Row-by-row agreement of the four drafts |
| `c6_distress_populations.py` | Ledger | The three "distress sale" populations from one source |
| `c7_landings_and_misc.py` | Sol, Opus and Fable group files, Opus's reason-code join | The two 150 and 63 partitions of landings and their cross table. Three building-timing definitions. First-window causes. G1 and G15 concentration |
| `c8_spot_checks.py` | Ledger, Fable price rows | Concessions (199 rows). Leave-one-block-out ranges. The ask gradient. The seven same-deed rows under first, median and last ask |
| `c9_cash_sensitivity.py` | Ledger | Thresholds, quartiles, mortgage status of requested deeds, recipient by stage, and game concentration of the holder-cash contrast |
| `c10_quote_sources.py` | Eleven quotation manifests in the four packages, canonical sources | File hash, field hash and span for 210 manifest entries (106 distinct). All pass |
| `build_quotes.py` | G20 `decisions.jsonl` and `events.jsonl` | Four new quotation cards with a manifest, and assertions of the state facts around the G20 payment |
| `c11_prose_facts.py` | All outputs above, plus sources for three notes | 105 assertions tying every number in `replacement_prose.tex` to a check output, and confirming that its printed form occurs in the TeX |
| `build_findings.py` | The four drafts | `findings.json`, with every quoted passage found verbatim in the named frozen file and its line and file hash recorded |

## Evidence status

Fresh in this review, from saved records or frozen ledgers:

- The split of opening offers by form and every number in Table 1 of `replacement_prose.tex`.
- The holder-cash tables for standard-condition holders, the thread-opener counts and the three sale populations.
- The declined and accepted terms in the 14 pairs.
- The seller outcomes by group ownership.
- The liquidation census (188, 128, 60, 67, 61, 180, 89, 68, 102, no engine default, one Grok disagreement in a paid episode).
- The same-deed rows and the three summaries.
- The G20 payment facts and the four cards.
- The two payable-declaration notes (G12 d190, G17 d234), re-read from source, with $340 and $375 of mortgage value that selling buildings would unlock.

Reproduced from another author's definition, with the same result:

- Opus's opening contrast, block gaps, concessions and capacity cut.
- Astra's leave-one-block-out ranges (opening 3.0 to 25.0, later 10.0 to 15.7).
- Sol's eleven of twelve ask cells and its 21 of 48.
- My own draft's cash bands, 13 of 14, 9 of 14 against 1 of 29, and ask gradient.

Independent rebuilds agree, as confirmed here, on the 920-row offer ledger (Fable and Opus), the 188 debt episodes with bounds (all four), and landings and rent for the 63 trade-completed groups (Sol, Opus, Fable).

Inherited and not rerun by anyone in this revision:

- Legal payment sequences for three eliminations and the restricted search for G7.
- Execution of defaulted build plans.
- Full replay of the twenty action streams.
- The first-management-turn classification of the 63 groups and its causes.
- The two model-assisted readings of 74 rejections. I recounted the G1 and G15 concentration from their row files and did not recode anything.
- The count of 2,054 prompts with misattributed history.

Taken from one draft without my own check: Opus's null on opponent standing (67%, 70%, 67%), the per-system bid medians, the refusal time bins, token and cost fields, and each draft's own render and quote-presence checks.

## Literature

I checked three sources, for relevance and novelty only.

1. Guhe and Lascarides, "The Effectiveness of Persuasion in The Settlers of Catan", IEEE CIG 2014, doi 10.1109/CIG.2014.6932861. Fetched from the Edinburgh Research Explorer (`pure.ed.ac.uk/ws/portalfiles/portal/19353900/CIG2014.pdf`, 9 pages, SHA-256 `5a673eb2e2fb3db6c641d34afb693099eb6486aaa7dbf0c10761086b563cd458`). I read the text layer of page 2 (abstract and introduction), page 4 (the embargo and block moves and the JSettlers default), pages 5 and 6 (simulation setup and embargo results) and page 9 (conclusion). I did not read pages 3, 7 and 8 in full. The two short phrases quoted in `replacement_prose.tex` are on page 4. A single web search located the paper. I did not rely on the search summary.
2. Cosentino et al., arXiv 2605.16575v1. The abstract page, through a summarizing fetch tool that returns a model-written summary with short excerpts. I used it only to confirm the framing that three drafts already cite from fuller readings.
3. Hu et al. (FinBoardBench), arXiv 2605.27896v1. The abstract page, through the same tool. I use one claim from the abstract, that models favor acquiring assets over keeping liquidity.

I read nothing else. Bibliographic details for the other entries in `replacement_prose.tex` are copied from the drafts' checked `.bib` files.

## Build

`replacement_prose.tex` compiles with LuaHBTeX 1.24.0 (TeX Live 2026) in two passes to a 9-page PDF with no overfull box, undefined reference or missing character. I inspected page images from three builds, namely pages 1, 3 and 7 of the first, pages 5, 9 and 10 of the second, and pages 6 and 8 of the final 9-page build. I also checked the final log. `qa/` holds page images and extracted text of the final build. The four quotation cards are generated from source by `build_quotes.py`. No quotation is typed by hand. Analysis scripts ran under Python 3.14.7. Page rendering used the PyMuPDF install in `/tmp/monopoly-astra-rewrite-venv`, which is a local convenience.

## Small numeric points

- Opus prints a median elimination debt of $925. The 30th and 31st values are $900 and $925, so the median is $912.50.
- The last accepted Opus first attempt in G1 to G4 is at 16:14:55 UTC. Two drafts print 16:14 and two print 16:15.
- Mortgage cells differ slightly between drafts because of bundles that mix mortgaged and unmortgaged deeds. Sol and Opus count such a bundle as mortgaged, I list it separately, and Astra keeps single-deed offers only.
- Rejection-reason concentration is 31 of the 61 agreed codes and 34 of the 74 rows.

## Remaining risks

1. The offer-form split is new today and is mine alone. It is a post hoc cut on games already studied. Its size ranges from 17 to 34 points with the treatment of Grok's conflicting calls, and most game and recipient pairs show no within-pair difference.
2. Both offer ledgers were rebuilt from the same saved prompts. Their agreement rules out a transcription error and does not rule out a shared misreading of the prompt format.
3. My classification of offer form uses only the deeds, cash and cards in each offer. It ignores which deeds are mortgaged and how close each party is to a group.
4. The Grok conflict parse is one regular expression over assistant text, the same rule as my frozen draft. It reproduces 64 threads and 17 settlements. A different parser could move a few threads.
5. The holder-cash result for Grok rests on 11 low-cash requests, and Sol's on three games for 19 of 26.
6. The G20 incident is one payment. It shows that such planning occurs. It gives no rate.
7. I read one new paper. A fuller search of the Catan and Diplomacy negotiation literature may find closer precedents for the stated-reason and pricing results.
8. Nothing here validates the semantic codes, estimates an effect, or scores a decision.
