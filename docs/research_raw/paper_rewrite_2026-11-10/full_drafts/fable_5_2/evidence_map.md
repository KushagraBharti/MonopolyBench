# Evidence map (Fable 5.2 full draft)

Every claim in `manuscript.tex` maps to one row below. Status codes:

- **R** recounted for this draft from canonical saved-game files.
- **T** re-tabulated for this draft from a retained ledger. The ledger's construction and its agreement with the engine are inherited.
- **T-new** a tabulation that did not exist before this draft. It has had no second reviewer.
- **I** inherited from the 29 October audit or its bounded source reviews. Not recomputed here.

No script in this folder runs the game engine, a reference policy or a model. I did not perform an independent engine audit. Engine-executed results (payment sequences, rebuilt build plans, the game-7 search, replay) are attributed to the 29 October certificate suite and its reviewers.

Paths are relative to `docs/research_raw/paper_rewrite_2026-11-10/` unless they start with `full_drafts/fable_5_2/` (written as `F/`) or name the repository root.

## Cohort and conditions (Section 2, Appendix A)

| Claim | Status | Evidence |
|---|---|---|
| 6,989 decisions, 8,679 attempts; per-system 1,961/1,991, 1,669/1,689, 1,696/3,301, 1,663/1,698 | R | `F/tools/census_decisions.py` over all twenty `saved_games/railway-research-*/game-NN-*/run/decisions.jsonl`; output `F/data/decision_census.json` |
| Opus: refusal in 1,605 decisions (1,604 first attempt); 215 of 306 in G1–4; 1,390 of 1,390 in G5–20; 1,544 applied actions without a note | R | same census |
| 66 engine defaults, all `end_turn` on management menus; 61 Opus, 4 Sol, 1 Gemini; by game 39/16/5/2/2/1/1 | R | same census |
| Same Terms-of-Service refusal message each time; trigger unknown | I | `../paper_draft_2026-10-29/sections/setup.tex`; memory note on refusal condition. Not re-read message by message here |
| G1–4 / G5–20 source revisions touch no engine, prompt or resolver file | I | 29 October appendix A |
| Grok: 139 applied decisions with text/tool-call name disagreement; all in non-streamed bodies | I for the ledger, T for the breakdown | `data/resolution_conditions.json`; breakdown 60/22/11/7 by `F/tools/retab_conflicts.py` |
| 64 of Grok's 136 threads opened by a disagreeing call; 17 settled; 7 of its 28 acceptances from disagreeing calls; 3 of those complete an Opus group | T-new | `F/tools/retab_conflicts.py` joining `resolution_conditions.json` to `agenda_threads.json` and `agenda_offers.json`; output `F/data/conflict_join.json` |
| Prompt wording on goal, strategies, public message, honesty sentence; honesty sentence absent from the action-only prompt | R | `python/packages/arena/src/monopoly_arena/player_config.py:14,31,38`, `prompting.py:1240-1243`; one saved standard and one saved action-only prompt from G1; `F/qa/quote_verification.json` |
| What each prompt shows (cash, holdings, model names, 20 timeline entries, 10 own notes) | I, spot-seen | 29 October setup; consistent with the one G11 prompt payload I inspected |
| Trade-history formatter: 44/113, 26/413, 232/394; 2,054 of 6,989 prompts. 149 of 6,882 public messages never reach a timeline | I | 29 October validation section |
| Tokens 128 vs 4,041 per decision | I | 29 October setup |
| Five rules, including "cannot build on mortgaged group" and intact creditor inheritance | R for the build rule and rent doubling, I for the rest | `python/packages/engine/src/monopoly_engine/engine.py:2526,2759-2760,2888-2889` read only; the rest from the 29 October setup |
| Wins 8/7/3/2; turns 75–386; seed blocks | T | `data/t01_cohort.json` |
| Block 3: seat 2 buys both dark blues by turn 29 in all four rotations and wins all four. Block 4: seat 1 completes orange by direct purchase on turn 47 in three rotations and wins those | T-new | `../paper_phase1_2026-10-28/sol/group_episodes.jsonl` joined to the cohort; `F/data/economy_retabulation.json` `first_completion_rows` |

## Measurement (Section 3)

| Claim | Status | Evidence |
|---|---|---|
| 920 responses, 918 acceptance-legal, 526 threads, 113 settlements, 44 with final writer ≠ initiator | T | `F/tools/retab_offers.py` on `data/agenda_offers.json` |
| Ledgers agree with engine: 6,989 states, 113 settlements, replay of 50,918 events | I | 29 October validation; `data/agenda_negotiation.json` validation block; `data/certificate_results.json` summary |
| Rent recorded by two independently built ledgers agrees on 209 of 209 episodes | T-new | `F/tools/retab_economy.py` (`episode_rent_crosscheck_against_flows`) |
| Coding of 74 rejections and of the 240-decision sample was done by GPT-6 Astra instances; overlap with participants | I | 29 October appendix D and `data/agenda_rejection_reasons.json` annotation field |
| All 28 retained quote fields and 30 spans match canonical files; 14 new quotes extracted by script | R | `F/tools/build_quotes.py`; `F/qa/quote_verification.json`; `F/data/transcript_manifest_supplement.json` |

## Bargaining (Section 4, Appendix C)

| Claim | Status | Evidence |
|---|---|---|
| First offers 32/137/355 of 524; later offers 81 accepted, 57 rejected of 394 | T | `F/data/offer_retabulation.json` `cells_first_offer`, `cells_later_offer` |
| Threads opened and settled per system 240/44, 136/39, 132/19, 18/11 | T | same, `threads_by_initiator_model` |
| Proposing share of eligible own turns 24/16/10/2 percent | I | `data/t02_negotiation.json` |
| 510 of 918 offers complete a group for someone; cells 289/140/81/408 with responses | T (matches Astra's re-count in the contract) | `cells_legal` |
| Completing side pays in 238 of 289 and 135 of 140; medians +200 / −350; accepted 18 of 19 and 23 of 24 at 200 / 275 | T-new | `cash_direction`, `cash_direction_accepted` |
| Completer paid net cash for 48 of 63 trade-completed groups, received for 9 | T-new | `F/data/economy_retabulation.json` `completing_terms_all` |
| Position stratification: 138/187 vs 31/51; 21/102 vs 7/89; 16/102 vs 22/89 | T-new | `cells_first_offer`, `cells_later_offer` |
| Rejection contrast in 5 of 5 blocks, 17 of 19 games (1 tie, 1 reversal), 3 of 4 recipients (not Opus); acceptance contrast in 4 of 5 blocks and 13 of 19 games | T-new. This replaces the earlier unverified consistency claim | `contrast_by_block`, `contrast_by_game`, `contrast_by_recipient` |
| Pattern unchanged without 11 disagreeing responses | T-new | `F/data/conflict_join.json` |
| Response styles 30/140/65, 26/36/180, 29/141/19, 28/77/149; Opus 162 action-only | T (matches the contract) | `recipient_style_all`, `response_condition_by_recipient` |
| 74 rejections of recipient-completing offers; 36 would also complete the writer's group | T | cells `recipient_only` + `both` rejections |
| 63 with a stated rival consequence (one reading); 61 agreed by a second; 66 with a note; 22 from G1, 12 from G15 | I | `data/agenda_rejection_reasons.json`; 29 October negotiation section |
| Incident 1 (G15 d168–175) terms, cash before and after, completion consequences | T for ledger facts, R for quotes | `data/agenda_offers.json` rows; canonical `decisions.jsonl` lines 338–350 |
| Incident 1 outcome: Grok first eliminated at turn 81, blockers to Gemini; Sol last | T | `data/agenda_flows.json` estate rows |
| Incident 1 "three houses on each orange" | stated in Gemini's own note, not state-checked | offer ledger note field |
| Cash-poor sellers: 21 of 48 completing sales under $100; medians $194 / $571; 9 of 57; thresholds; Opus 16 of 30; 6 of 21 later won | T-new, exploratory | `F/tools/retab_distress.py`; `F/data/distress_retabulation.json` |
| Table 3 cash-poor responses | T-new, exploratory | same |
| G1 Boardwalk sale facts (Opus $18, mortgaged Short Line, price path 150/50/100, estate four turns later to Gemini) | R for quotes and messages, T for cash and estates | canonical G1 `decisions.jsonl` d305–309; offer and flow ledgers |
| Incident 2 (G19 d135–136) | I for event-level facts, R for quotes and action chronology | retained manifest; canonical log check in this session; disagreement type from `resolution_conditions.json` |
| Incident 3 (G7 d41–43), including Sol's $625 ask at d41 | R | canonical G7 `decisions.jsonl`; retained manifest |

## Development (Section 5, Appendix D)

| Claim | Status | Evidence |
|---|---|---|
| Trade completions 17/18/15/13; built in first window 16/17/7/3; ever built 17/17/12/8 | T | `F/data/economy_retabulation.json` from the phase-1 episode ledger and `data/first_management_windows.json` |
| Rent on those groups $20,818 / $26,070 / $5,930 / $4,560; $53,810 on the 43 built, $3,568 on the 20 others | T-new, cross-checked against the flow ledger | same |
| First window in same turn for 35 of 63, within five turns for all but two | T | `elapsed_to_management` |
| Twenty unbuilt windows: 9 / 4 / 4 / 3 | T | `first_management_windows.json` causes |
| Seven of nine arrived mortgaged; two left $158 and $125 against a $200 house | T-new. The ledger says only "never legal in window". The reason is my reading of settlement interest, message text and the engine rule | `never_legal_rows`; offer ledger rows listed in Table 18 |
| Grok's four never-legal groups bought from Opus holding under $70, with notes deferring redemption | T-new for cash, read from ledger note fields | offer ledger rows G1 d289, G1 d309, G14 d203, G16 d229 |
| 42 buildable on entry: 34 built, 3 defaults, 3 disagreements, 2 valid ends | T | rows with `entry_legal` |
| All 61 Opus plans execute after splitting and even ordering; 63 of 66 decisions; attempt diagnostics | I | `data/certificate_results.json` summary; 29 October audit |
| Recovery table | I | `data/t07_build_recovery.json` |
| 663 / 66 / 24 / 573 end-of-turn provenance | I | `data/resolution_conditions.json` counts |
| Incident 4 (G20 d95–102) | I for prompt delivery and later Opus offers, R for quotes and chronology | retained manifest; canonical log check; offer ledger for the $500 Illinois sale and Grok's $222 |
| Spending units 103; $103,450; $93,000; by system | T | `data/t05_spending_units.json` |

## Insolvency and inheritance (Section 6, Appendix D)

| Claim | Status | Evidence |
|---|---|---|
| 60 eliminations; 56 declared, 4 automatic | R and T | census (56 `declare_bankruptcy`); `data/t06_eliminations.json` |
| 56 bound below debt, 3 payable, 1 hotel lock | T. The executions behind the 3 and the 1 are I | `t06_eliminations.json` joined to `certificate_results.json` |
| Median shortfall $360; 10 under $100; closest $18; median debt above $900 | T-new | `shortfall_vs_bound`, `debt_size` |
| 57 of 60 debts are rent on developed color groups | I | 29 October economic appendix |
| G12 Sol, G17 Gemini, G7 Opus narratives | I | 29 October economic results |
| Incident 5 (G12 d249) | I for the five-sale sequence, R for quotes and applied action | retained manifest; certificate suite |
| Only one disagreement has a received bankruptcy call | T | `content_to_received` in `F/data/conflict_join.json` |
| 209 completions: 63 trade, 16 purchase, 9 auction, 121 estate (69 at final elimination) | T | phase-1 episode ledger |
| Winner holds 18 of 63 trade, 45 of 52 live estate, 12 of 16 purchase, 2 of 9 auction | T-new | `live_by_route` |
| One creditor takes all three estates in 16 games; winner gets first estate in 18, second in 17, third in 19 | T-new | `elimination_rows` built from estate flows |
| 202 of 227 pre-final estate deeds to the winner | T | `estate_deeds` |
| Rent by route $57,378 / $23,070 / $11,472 / $3,358; $95,278 of $121,154; 14 of 52 estate groups collect any | T-new | `live_by_route`, `flow_totals` |
| Incident 6 (G13 d250–253, d311) | I for the exact-prefix $295 alternative, the content of Opus's returned explanation and prompt condition; R for quotes, chronology, d311 bankruptcy; T for cash $35 and $1,926, interest $16, later Sol elimination on a $100 tax | retained manifest and `qa/g13_context_check.json` of 29 October; canonical log; ledgers |
| Incident 7 (G18 d421–442) | R for the full message chronology and quotes; T for Sol $49, Opus $2,125; I for prompt delivery and later $150 / $225 offers | canonical G18 `decisions.jsonl`; offer ledger |
| G18 Illinois blocking purchase and reversal | T for the $100 sale from a seller holding $2; I for stated purpose and the red completion | offer ledger d336; 29 October social appendix |
| First complete group per game: 14 trade, 6 purchase; owner wins 15; built × won 12 / 3 / 4 / 1 | T-new | `first_completion_rows` |

## Plans, forecasts, errors (Section 7)

| Claim | Status | Evidence |
|---|---|---|
| 240-sample counts 59 / 36; eight landing policies 6 / 1 / 1; Opus notes absent in 53 of 60 | I | `data/agenda_temporal.json` |
| G16 Virginia: quotes, $371 vs $160, auction started, 56 decisions apart | R for quotes and action; I for the $380 auction result | canonical G16 lines 208 and 320; disagreement ledger |
| G9 target chronology | I | 29 October temporal exhibits |
| Grok's Boardwalk forecast realized: Opus eliminated four turns later owing $550 | T | elimination row G1 #1 |
| Recurrence table and 54 of 63 Opus | I | `data/agenda_recurrence.json`; 29 October recurrence section |

## Discussion, related work

| Claim | Status | Evidence |
|---|---|---|
| Statements about cited papers | abstract-page level, inspected 10 November 2026, or inherited from the 29 October registry | `literature_updates.md` |
| AgentMonopoly and FinBoardBench rule details (inheritance, single-offer trades, fallbacks) | I | 29 October related work and its round-2 review |

## Automated consistency checks

`F/tools/check_manuscript.py` recomputes 77 assertions from the JSON outputs and confirms the literals in the section files, checks that every quote id used is declared, that all 41 used excerpts occur in the text extracted from the built PDF, that citation keys and labels resolve, and that the log has no overfull box or undefined reference. Output: `F/qa/manuscript_checks.json` (0 failures on the final build).
