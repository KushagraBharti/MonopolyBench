# Evidence map

Paths are relative to this draft directory unless they start with `docs/` or `saved_games/`, which are relative to the repository root. Every number in the manuscript is a `\fact{key}` lookup or a generated table row. `data/facts_index.txt` lists each key with its value. A missing key stops the build.

## Status vocabulary

- **Fresh.** Rebuilt here from canonical `events.jsonl`, `decisions.jsonl`, `players.json` and `contracts/data/board.json`.
- **Reconciled.** Fresh, and compared row by row or total by total with an earlier ledger.
- **Inherited.** From earlier work. Not rerun here.
- **Read.** A named field, source file or web page read in this session.
- **Document.** Build and render checks only.

## Scripts

| Script | Output | What it does |
|---|---|---|
| `analysis/corpus.py` | (loader) | Loads the twenty games, pairs decision records, maps player ids to systems. Self-check prints 50,918 events, 6,989 decisions, 8,679 attempts. |
| `analysis/state_track.py` | `data/state_track_validation.json` | Folds events into cash, ownership, mortgage and building state. Compares with all 6,989 delivered prompts. Zero mismatches. |
| `analysis/a1_conditions.py` | `data/a1_conditions.json` | System prompts and diff, refusal census and timing, attempt outcomes, private-note windows, usage and cost fields, channels, request payload keys, tool descriptions, board fields by phase. |
| `analysis/a2_offer_ledger.py` | `data/a2_offer_ledger.json`, `..._reconciliation.json` | One row per trade response from the responder's delivered prompt. Reconciled with the earlier ledger on 920 of 920 rows and 16 fields. |
| `analysis/a3_groups.py` | `data/a3_group_episodes.json`, `a3_group_summary.json` | 209 group-completion episodes with route, timing, landings, rent, building. |
| `analysis/a4_debt.py` | `data/a4_debt_episodes.json`, `a4_debt_summary.json` | 188 debt episodes with the own-asset bound at the first menu. Eliminations reconciled with the earlier ledger. |
| `analysis/a5_estates.py` | `data/a5_pre_estate.json`, `..._summary.json` | Each game's four positions before its first elimination. |
| `analysis/a6_bargaining.py` | `data/a6_bargaining.json`, `a6_pure_offers.json`, `a6_dyads.json` | Prices, counter repricing, responses by holder cash, 148 pairs, fates, Grok text and call parse and exclusion sensitivity. |
| `analysis/a7_conversion.py` | `data/a7_conversion.json`, `a7_trade_groups.json`, `a7_landings.json` | The 63 trade-completed groups, seller conversion after one-sided sales, cohort outcomes. |
| `analysis/a8_estates_flows.py` | `data/a8_estate_flows.json` | Estate deed and cash transfers, creditor identity, developed-rent debts. |
| `analysis/a9_incident_checks.py` | `data/a9_incident_checks.json` | Asserts the factual statements made around the incidents (cash, prices, turns, outcomes). |
| `analysis/build_quotes.py` | `sections/quotes.tex`, `data/quote_manifest.json` | Generates every quotation from `decisions.jsonl` with hashes and spans. Checks reused quotes against the earlier definitions. Records delivery to the counterparty. |
| `analysis/build_prompt_listing.py` | `sections/prompt_*.tex`, `sections/refusal_message.tex` | Exact stored prompt, diff and refusal message. |
| `analysis/build_tables.py` | `sections/facts.tex`, `sections/tables.tex`, `data/facts.json` | Flattens summaries into facts, adds derived percentages, writes table rows. |
| `analysis/make_figures.py` | `assets/fig_*.pdf` | Six figures from `data/`. |
| `analysis/verify_document.py` | `qa/document_checks.json` | Re-reads every quotation from source by hash, line and pointer. Checks rendered presence, log, pages, frozen baseline files and word counts. |
| `analysis/render_pages.py` | `qa/render/`, `qa/manuscript_text.txt` | Two-page contact sheets and extracted text of the built PDF. |
| `analysis/write_manifest.py` | `source_manifest.json` | Hashes of inputs and package files. |

## Claims and sources

### Setting and conditions

| Claim | Status | Source |
|---|---|---|
| 20 games, 6,989 decisions, 8,679 attempts, 50,918 events | Fresh | `corpus.py` self-check |
| Event-derived state equals delivered state in all prompts | Fresh | `state_track_validation.json` |
| One standard system prompt (6,989 uses), one action-only prompt (1,604 uses), five-hunk diff | Fresh, read | `a1_conditions.json: system_prompt` |
| Action-only prompt keeps "Deception in public chat is allowed" and the bluff list | Read | same; `sections/prompt_diff.tex` |
| Action-only tool schemas equal the standard ones minus `private_thought` in all 1,604 requests; user payload adds one `response_instruction` field | Fresh | `a1_conditions.json: action_only_census` (reads `prompts/*_tools.json` and `*_retry1_tools.json`) |
| 1,605 refusals, one message, `content_filter` / `refusal` | Fresh | `a1_conditions.json: opus_refusals` |
| Action-only refused 0 of 1,604; 60 invalid | Fresh | same |
| G1 to G4 time course: 68 of 160 then 146 of 146; ten-minute bins | Fresh | same |
| 1,394 Opus prompts with no model-written note in the window (1,108 empty, 286 fallback text) | Fresh | `a1_conditions.json: private_note_windows` |
| Provider documentation on `reasoning_extraction` | Read | `https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5`, read 11 November 2026 |
| Grok text names an action in 1,068 selected responses, 139 disagree with the call | Fresh, reconciled | `a6_bargaining.json: grok_sensitivity`; equals the earlier census |
| 64 of 136 Grok threads opened by a conflicting call; 17 settle; 11 conflicting responses | Fresh, reconciled | same |
| Request payload keys; tool choice required for Grok, auto for others; no temperature, nucleus or length parameter | Fresh | `a1_conditions.json: request_payloads` (8,687 call intents) |
| Reasoning and output token fields; cost fields $76.04, $141.71, $141.39 | Fresh | `a1_conditions.json: usage`, `usage_totals`; BYOK-aware total computed in session |
| Board parameters by decision type | Fresh | `a1_conditions.json: board_fields_by_phase` |
| Tool descriptions, one per tool | Fresh | `a1_conditions.json: tool_descriptions` |
| Rule conventions in Appendix A | Read | `python/packages/engine/src/monopoly_engine/engine.py`: trade validation (lines 1755 to 1775), transfer interest (1779 to 1787), bankruptcy handling (2951 to 3028), sale menu (2552 to 2572), mortgage validation (2575 to 2588), redemption (2488 to 2490) |
| Redemption overcharge at five mortgage values | Fresh arithmetic | computed from the board file with the engine's formula |
| 2,054 prompts with misattributed history | Inherited | earlier history audit |

### Bargaining

| Claim | Status | Source |
|---|---|---|
| 526 threads, 920 responses, 918 acceptance-legal; cells by completion and stage | Fresh, reconciled | `a6_bargaining.json: census`; ledger reconciliation |
| Responses and threads by system; repeated opening bundles | Fresh | same |
| 507 pure cash-for-deed offers, 200 asks, 307 bids; pooled medians | Fresh, reconciled | `a6_bargaining.json: prices`; pooled values equal the earlier appendix table |
| Ask and bid medians by author and mortgage status; by stage; by seller cash | Fresh | same |
| Gradient by buyer's distance to completion (Figure 1) | Fresh | `a6_pure_offers.json` |
| Seven same game, seller and deed cases: 4, 2, 1 | Fresh | `a6_bargaining.json: prices.same_game_seller_deed_pairs` |
| Counter repricing 79 of 111 and 81 of 110; retention 92 and 87 | Fresh, reconciled | `a6_bargaining.json: counters` |
| Rival consequence coded in 61 of 74; own-cash in 41 of 74; kappa 0.79 and 0.77; splits by system, cell and game | Inherited (joined here) | `docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/rejection_reason_coding.json`, `.../reviews/negotiation/reason_comparison.json` |
| Rejection by holder cash; per block; leave one block out; exclusions | Fresh | `a6_bargaining.json: holder_cash` |
| 24% of completion requests reach holders under $100, against 8% | Fresh | same |
| 148 pairs, 63 settled, 43 one-sided, 20 mutual; holder cash at settlement | Fresh | `a6_dyads.json`, `a6_bargaining.json: dyads` |
| 13 of 14 lower from the holder's first refusal; 14 of 18 from the first offer; medians | Fresh | `a6_bargaining.json: dyads.from_first_holder_decline`, `within_dyad_one_sided_later_turn` |
| Distress prices: Opus 0.66 (8), others 2.25 (6); 7 of 8 below list, 5 of 6 above | Fresh | `a6_bargaining.json: dyads.one_sided_pure_cash_settlements` |
| Fates of the 85 unsettled pairs | Fresh | `a6_bargaining.json: dyads.unsettled_fates` |

### Conversion, debt and estates

| Claim | Status | Source |
|---|---|---|
| 209 completion episodes by route; rent by route | Fresh, reconciled | `a3_group_summary.json`; equals earlier totals |
| 63 trade-completed groups: timing, cash, landings, rent, spend | Fresh | `a7_trade_groups.json`, `a7_conversion.json` |
| Built in the first management turn: 16, 17, 7, 3; causes for the 20 unbuilt | Inherited | `docs/research_raw/paper_rewrite_2026-11-10/data/first_management_windows.json` |
| Four Grok notes defer redemption or building | Inherited | earlier root check |
| Landings 213, rent $57,378, rent per landing, block ordering | Fresh | `a7_conversion.json` |
| Seller conversion: 9 of 14 against 1 of 29; windows 4, 8, 12; player-game counts | Fresh | `a7_conversion.json: seller_conversion` |
| 188 debt episodes, 128 paid, 60 eliminated; bound at first menu | Fresh | `a4_debt_summary.json` |
| 56 eliminations below the bound | Fresh, reconciled | same |
| Three payable eliminations have legal payment sequences; G7 has none on the menu | Inherited | `docs/research_raw/paper_rewrite_2026-11-10/data/t06_eliminations.json` and the earlier certificate suite |
| Sol G12 and Gemini G17 notes omit mortgages unlocked by sales | Read | G12 d190 and G17 d234 notes and holdings |
| G7 menu offered no building sale with bank houses at zero | Read | G7 d338 and d339 prompts; engine sale-menu source |
| Estates: 54 of 60 and 35 of 40 creditors are winners; 397, 227, 202 deeds; 57 developed-rent debts | Fresh, reconciled | `a8_estate_flows.json` |
| First creditor is the winner in 18; leads assets in 15, rent in 15; discordant games | Fresh | `a5_pre_estate.json`, `a5_pre_estate_summary.json` |
| Wins by system and seat | Fresh | `a7_conversion.json: cohort` |

### Inherited statements in the question table

| Claim | Status | Source |
|---|---|---|
| G9 building target reached | Inherited | earlier temporal analysis |
| Uneven-build recurrence, 9 of 50 against 54 of 59 | Inherited | earlier recurrence ledger |

## The eight incidents

Every quotation is generated by `build_quotes.py` and rechecked by `verify_document.py`. Facts around the quotations are asserted in `a9_incident_checks.py`.

| Incident | Quotations | Facts checked from records |
|---|---|---|
| 1. G2 | 5 cards (3 reused, 2 new) | Cash 137, 161, 435, 17; asks 450, 650, 600; turns 44, 45, 69; Opus out at turn 72 owing Gemini 1,300; Sol built 2 houses, sold at turn 73, out at turn 85; Gemini wins |
| 2. G15 | 5 cards (3 reused, 2 new) | Turn 63; cash 730 and 333; three Grok rejections and one Gemini rejection; Grok first out at turn 81 to Gemini; Sol never completes yellow or green |
| 3. G1 | 3 cards (1 reused, 2 new), 1 inline | Seven swap offers from turn 69; cash 453 then 18; sale at 100, list 400; group held 94 turns, 5 landings, $70; Opus out at turn 126 owing Gemini 550 |
| 4. G13 | 4 cards (all reused) | Cash 35 at Atlantic; Ventnor unmortgaged, mortgage value 130; offers 200, 130, 200; interest 16; auction 650 at turn 114; next square not Short Line; rent 200 at turn 146; out at turn 150 on Short Line to Sol |
| 5. G7 | 5 cards (2 reused, 3 new), 1 inline | Turn 25 cash 1,150; asks 650, sale 600; turn 67 Park Place for 800 and a deed; cash 84; bids 350 at turns 53 and 68; sale 700; Gemini 5 mortgages and 4 houses; Sol 3 houses within 8 turns; Gemini orange rent 270; out at turn 125 |
| 6. G20 | 4 cards (all reused), 2 inline | Sale 500 at turn 22, cash 222; build 3 houses to cash 7; Vermont 150 refused; mortgage 50; later Opus bids; reds 2 landings, $126; Grok out at turn 84 |
| 7. G12 | 3 cards (all reused) | Debt 250, cash 43; houses 2, 2, 3; text names a sale; call declares bankruptcy; estate to Opus. Five-sale payment route inherited |
| 8. G18 | 5 cards (4 reused, 1 new), 1 inline | Turn 181 cash 615 and 294; bids 200, 250; ask 600; four "still stands" messages by turn 187; rents 750 twice; cash 49; bundles 450, 350; 250 refused; Opus cash 2,125; redemptions turns 190, 192; bids 150, 225; asks 450, 350, 300; Sol out at turn 197 |

Appendix controls: G19 (3 cards), G11 (3 cards), G3 (3 cards), all reused. The G17 public message in Section 6 is new.

Of 44 cards, 33 repeat earlier checked definitions and match them character for character (`quote_manifest.json: text_identical_to_reused_definition`). Delivery of a public message to the named counterparty is recorded for 24 of 25 checked messages. The exception is the G12 bankruptcy message, which I do not claim was delivered.

## Literature

See `literature_inspiration.md` for what was read for each citation.

## Document

`qa/document_checks.json` records the PDF hash, 39 pages, no blank page, no LaTeX diagnostics, 50 quotations rechecked against 12 source files, all used quotations present in the PDF text, and no change to the 78 files frozen in `../../baseline_hashes.json`. `qa/render/` holds two-page contact sheets of the final PDF. `source_manifest.json` hashes the 61 canonical inputs, the retained inputs and the package files.
