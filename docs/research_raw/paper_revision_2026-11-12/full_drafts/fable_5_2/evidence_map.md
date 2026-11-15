# Evidence map: Fable 5.2 complete draft, 12 November 2026

Each row gives a claim in `manuscript.pdf`, the records behind it, the script that computes it, and its status.

Status words:

- **Fresh**: computed in this draft from `decisions.jsonl`, `events.jsonl` or other saved run files.
- **Reconciled**: fresh, and equal to an earlier ledger on every compared field.
- **Read**: I read stored text or a stored report. No computation beyond counting.
- **Reading**: my classification of stored text. One model reader, no human annotation.
- **Pattern**: a regular-expression count over stored text.
- **Inherited**: taken from earlier work in this project and not redone.

All scripts are in `analysis/`. All outputs are in `data/`. The scripts import no engine code.

## Corpus and conditions

| Claim | Records | Script and output | Status |
|---|---|---|---|
| 20 games, 50,918 events, 6,989 decisions, 8,679 attempts, 75 to 386 turns | all run directories | `b4_provenance.py`, `b4_provenance.json` | Fresh |
| Seeds, seat orders, winners, elimination order, source commit per game | `replay_report.json`, `players.json`, events, `game-index.csv` | `b4_provenance.py` | Fresh |
| Wins 8, 7, 3, 2 by system and 7, 7, 3, 3 by seat | events | `b4_provenance.py` | Fresh |
| Tool choice "required" for Grok, "auto" for the others | 8,687 `cloud/calls/*.intent.json` request records. Source at commits 42f85183 and d6808534 read with `git show` | `b4_provenance.py` | Fresh, read |
| Medium reasoning effort, no temperature, nucleus or token setting | the same request records | `b4_provenance.py` | Fresh |
| Opus: 1,604 of 1,696 first attempts refused, one message, 214 of 306 in G1 to G4, all 1,390 in G5 to G20, 0 of 1,604 recovery requests refused | attempt records | `b3_conditions.py`, `b3_conditions.json` | Fresh |
| Standard prompt text and recovery diff | first system message of every decision and recovery attempt | `b3_conditions.py`, `build_prompt_listing.py` | Fresh |
| Grok: 139 responses whose text names another action than the call, 64 of 136 trade openings, 7 of 28 acceptances. No such response from another system | selected attempts | `b1_offers.py` (`census`) | Fresh |
| Engine fallback resolved 61 Opus, 4 Sol, 1 Gemini, 0 Grok decisions. The named fallback model was never used | decision records, `run_config.json` | `b3_conditions.py` | Fresh |
| Replay: full event stream equal in 20 runs, 50,918 events, nothing excluded | `artifact_replay_report.json` | `b4_provenance.py` | Read. The replays were executed on 25 and 26 October and not rerun |
| Replay: state-relevant events equal in 20 runs, 24,506 events, four LLM event types dropped | `state_replay_report.json` | `b4_provenance.py` | Read. Same |
| The liquidation prompt has no price, mortgage value or release rule | liquidation prompts and tool schemas | `b3_conditions.py` (`board_fields_by_phase`), direct reading of G20 d327 | Fresh, read |
| Provider cost fields sum to USD 141.71 | usage fields | `b3_conditions.py` | Fresh. Not an invoice |

## Debts

| Claim | Records | Script and output | Status |
|---|---|---|---|
| 188 episodes, 128 paid, 60 eliminated | liquidation decisions and events | `b2_debt.py`, `b2_debt_episodes.json` | Reconciled with `paper_revision_2026-11-11/integrated/data/liquidation_episodes.json` on identity, debt, actions, outcome and bound (188 of 188) |
| 56 debts above every own asset | first-menu state | `b2_debt.py` | Fresh. Agrees with the inherited classification |
| Three eliminations were payable (G12 Sol, G12 Grok, G17 Gemini) | `paper_rewrite_2026-11-10/data/t06_eliminations.json` | `b2_debt.py` joins it | Inherited. The payment sequences were executed on the engine earlier and not here |
| G7 Opus: menu offered no sale, bank had no houses | first-menu prompt | `b2_debt.py`, `b5_incidents.py` | Fresh for the menu and state. The search of the menu is inherited |
| Tiers 62, 53, 16 with 62, 52, 14 paid | first-menu cash, listed deeds, buildings, unlisted deeds | `b2_debt.py` | Fresh. Asserted in the script |
| Quit at first menu: 50 of 56 above bound, 3 of 131 payable | first applied action | `b2_debt.py` (`first_menu_decision`) | Fresh. New in this draft |
| 67 one-action payments, 180 mortgages, 89 sales, median debt 36% of bound | applied actions | `b2_debt.py` | Fresh |
| 19 payments used a mortgage absent from the first menu, 33 such mortgages, 14 necessary and 5 optional | first and later menus, applied actions | `b2_debt.py` | Fresh |
| Sixteen first texts: 13 count, 1 raises, 2 leave out | applied note or provider-returned reasoning at the first decision | `build_quotes.py` (`READINGS`), `b6_readings.json`, `b2_first_texts.json` | Reading. Exact spans verified against source |
| 14 of 15 stated figures equal the records | the same texts and `b2_debt_episodes.json` | `build_quotes.py` | Fresh arithmetic on my reading of which figure is stated |
| G20 payment: 2 sales for $700, 8 mortgages for $665, rent $1,400, $49 to $14 | decisions d327 to d336, turn-108 events, next prompt | `b5_incidents.py` | Fresh. Asserted |

## Offers

| Claim | Records | Script and output | Status |
|---|---|---|---|
| 920 offers, 526 threads, 918 acceptance-legal, 113 accepts, 394 counters, 413 rejections | trade-response decisions | `b1_offers.py`, `b1_offer_ledger.json` | Reconciled with `paper_revision_2026-11-11/integrated/data/offers.json` on 12 fields, 920 of 920 rows |
| Full table by stage, form and completion | ledger | `b1_offers.py` (`full_table`) | Fresh |
| Opening swaps 95/116, 37/72, 34/48. Cash bids 42/70, 67/103 | ledger | `b1_offers.py` | Fresh. Asserted. Equal to the previous paper |
| 3 of 186 and 21 of 175 accepted | ledger | `build_tables.py` from `b1_offers.json` | Fresh |
| Proposer, recipient and seed-block strata | ledger | `b1_offers.py` | Fresh. Proposer table equals referee B's |
| Without Grok authors 90/108 and 24/36. Without conflicting openings 93/112 and 26/43 | ledger and the proposing decisions | `b1_offers.py` | Fresh. Asserted |
| Standardized gaps 16.0, 18.1, 21.5 | ledger | `b1_offers.py` | Fresh |
| Per-block values, leave-one-block-out, seed-block resampling (3,125 resamples, exact), game resampling (20,000 draws, seed 20261112) | ledger | `b1_offers.py` (`sensitivity`) | Fresh. Resampling of stored observations. Game ranges agree with referee B and with Opus's 11 November check to within rounding |
| Counters 26/70 and 20/116. 15 of 26 keep the bundle and ask more cash | ledger, next offer in thread | `b1_offers.py` (`counters`) | Fresh |
| Completion terms 93/95 and 42/42, building terms 83/95 and 35/42 | rejection text | `b1_offers.py` (`keyword_screen`) | Pattern |
| Refusal wording by recipient | rejection text | `b1_offers.py` (`refusal_wording`) | Pattern. New in this draft |
| Rejection by proposer's house capacity | ledger, board prices | `b1_offers.py` (`rival_capacity`) | Fresh. Coarse measure |
| List-value medians and rejection among favorable swaps | ledger, board prices | `b1_offers.py` (`list_value`) | Fresh. Crude |
| 61 of 74 reason codes, all in recipient-completing offers | `paper_agenda_revision_2026-10-29/negotiation/rejection_reason_coding.json` and `reviews/negotiation/reason_comparison.json` | `b1_offers.py` (`semantic_codes`) | Inherited codes. Population join is fresh |
| Holder-cash counts | ledger | `b1_offers.py` (`holder_cash`) | Fresh |

## Incidents

Every quotation is generated by `build_quotes.py` from `decisions.jsonl` and listed in `data/quote_manifest.json` with file hash, line, field pointer, character span and field hash. `verify_document.py` re-reads each one. Twenty-three of the 29 cards repeat a quotation of the previous paper and are character-identical to it. Receipt is checked by finding the message in the counterparty's stored prompt.

| Incident | Facts asserted in `b5_incidents.py` | Receipt checked |
|---|---|---|
| 1. G20 payment | holdings, 2 sales, 8 mortgages (5 on unlisted deeds), $700, $665, $1,400, $14, two players left, elimination 7 turns later | Private notes. No receipt claimed |
| 2. G15 refusal | cash $730 and $333, three offers, three rejections, post-trade cash, Opus appeal in Grok's prompt, Grok eliminated at turn 81 to Gemini, Sol never completes yellow or green | d174 at d175, d175 at d176 |
| 3. G2 pricing | Grok's $200 bid, $450 and $650 asks, Opus cash $845, $520 buys three houses, private ceiling, reversal at turn 69 with $17, $44 rent, both bankrupt to Gemini | Opus's "final" at d128, Sol's reply at d129 |
| 4. G13 pitch | $35, nine squares, $200 rent, four railroads, Ventnor mortgage $130, $16 interest, missed roll, green at turn 114, bankruptcy at turn 150 to Sol | d250 at d251, d252 at d253 |
| 5. G7 | $650, $575, $625, $600, ceiling, $800 and States for Park Place, $84, $350, $700, $520, 5 mortgages, 4 and 3 houses, $270 rent, elimination at 125 | "final" at d43 |
| 6. G19 | terms, both pink, no group completed, abort note, content names another action | false message at d136, reply at d137 |
| 7. G20 appeal | Illinois for $500, $222, build, Vermont offer, refusal, mortgage, Opus's later offers, none settled | appeal at d97, refusal at d102 |
| 8. G18 | two players left, no inheritance term in Opus text d421 to d461, bids, redemptions, rents, $49, elimination at 197 | assurance at d432 and d441, invocation at d442, withdrawal at d443 |

## What the build checks

`./build.sh` ends with `analysis/verify_document.py`, which writes `qa/document_checks.json`:

- 55 quotations re-read from source by hash, line, pointer and span.
- Every quotation used is present in the PDF text.
- No LaTeX diagnostic lines.
- No blank page and no text near a page edge.
- The 72 files in `../../baseline_manifest.json` are unchanged, and git reports no change under `saved_games`, `contracts`, `python`, `frontend` or `scripts`.
- Every `\fact{}` key exists. 229 citations of 178 keys.
- Main prose word count, with the method stated.
- Eight incidents, four in the main text and four in the appendix.
