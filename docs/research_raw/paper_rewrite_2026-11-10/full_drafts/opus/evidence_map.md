# Evidence map (Opus independent draft)

Status key: **C** = checked or computed while writing this draft (script or source read named); **I** = inherited from an earlier audit, reported with that audit's scope, not re-derived; **N** = new quantity first computed here.

Shared inputs live in `../../data/` (byte-identical to `../../../paper_draft_2026-10-29/data/`, checked with `diff -rq`). Draft outputs live in `data/`.

## Setup and conditions (Section 2)

| Claim | Status | Source |
|---|---|---|
| 20 games, 5 seeds x 4 rotations, 50,918 events, 6,989 decisions, 8,679 attempts | I | `t01_cohort.json`; baseline setup/validation |
| Turns 75 to 386; winners Sol 8, Gemini 7, Opus 3, Grok 2 | C | `t01_cohort.json` |
| Per-configuration decisions/attempts; token, latency and USD 141.71 lower bound | I | baseline Table 1 and setup text |
| 1,605 refused Opus attempts in 1,605 decisions (1,604 first + G2 d129 second); every first attempt from G5 refused | I | baseline appendix B, social contract; memory note on refusal shift |
| 1,394/1,696 Opus decisions without model-authored private memory (1,108 empty, 286 synthetic) | I | baseline validation |
| 66 defaults (61 Opus, 4 Sol, 1 Gemini) | I | `certificate_results.json`, `resolution_conditions.json` |
| 139 selected Grok conflicts; all in non-streamed bodies | I | `resolution_conditions.json` (`transport`) |
| Formatter: 44/113, 26/413, 232/394; >=1 in 2,054/6,989 prompts | I | baseline validation |
| 149/6,882 messages never in timeline | I | baseline validation |
| Readable reasoning 4,834 decisions; opaque 4,016 | I | baseline appendix B |
| Version boundary commits and diff contents | I | baseline appendix A |

## Measurement (Section 3)

| Claim | Status | Source |
|---|---|---|
| Prompt/snapshot reconciliation; replay of 50,918 events | I | baseline validation; certificate package |
| Second implementation reproduces 920 rows and 113 transitions | I | `../../../paper_draft_2026-10-29/adversarial_reviews/agenda/negotiation/findings.md` |
| Rejection-reason readers are Astra instances; second partly unblinded | I | baseline appendix A ("native instances of the same Astra research model"); `coding_protocol.json` exposure note |
| Bundled-sale counterexample and checker guard | I | baseline audit appendix |

## Bargaining (Section 4)

| Claim | Status | Source |
|---|---|---|
| 526 threads, 920 responses (113/394/413), 918 legal | C | `tools/retabulate.py` -> `data/opus_retabulation.json` |
| Completion cells: neither 60/169/179 (408); author-only 19/111/159 (289); recipient-only 24/78/38 (140); both 10/35/36 (81) | C | same (matches Astra's re-count in contract) |
| Median net cash to recipient: +200, -350, -100, +100; by response 200/230/180 in author-only | C/N | same |
| Counter content: 111 author-only counters -> 88 keep author only (85 raise, median +125), 4 keep both, 13 swap (median -560), 6 remove; neither 135/164 raise (+75); recipient-only 77/78 (+122.5); both 26/29 (+143) | N | same, `counter_content` |
| Thread outcomes by opening cell; 26/187 author-only openers settle; 24 keep initiator completion; median +97.50 | N | same, `threads_by_opening_cell`, `author_only_opening_settled` |
| Responder styles (Sol 65/140 of 235 etc.) and per-cell acceptance | C | same, `responder_all_920`, `responder_by_cell_legal` |
| Opus 162/189 action-only; under action-only accepts 7/47 author-only, 3/34 recipient-only | N | same, `opus_responder_*` |
| Keep-only counters priced: Sol 35/36 (+150), Gemini 7/7 (+130), Opus 34/36 (+77.5), Grok 9/9 (+260) | N | same, `counter_content_author_only_by_responder` |
| Reject share direction in 5/5 blocks and 17/19 games; acceptance reverses in block 3 | N | same, `direction_by_block`, `games_reject_share_author_gt_recipient` |
| 61/74 common rival-consequence codes; 4 boundary disputes; 2 role errors | I | `agenda_rejection_reasons.json`; negotiation review |
| 113 settlements: 60/43/10; 44 final author != initiator; 414 repeat-pair threads | I | baseline negotiation section; consistent with ledger |
| Initiation 83/834, 16/766, 160/660, 106/676; initiator settlements 19/132, 11/18, 44/240, 39/136 | I | `t02_negotiation.json`; baseline text |
| G2 incident quotes (7 spans) | C | `tools/build_opus_quotes.py` -> `data/opus_quote_manifest.json` (canonical `decisions.jsonl` lines 250, 256, 258, 396, 398) |
| G2 delivery of quoted messages | C | `tools/check_delivery.py` -> `data/opus_delivery_checks.json` |
| G2 actor identities (p1 Sol, p4 Opus) and response conditions | C | canonical `actions.jsonl`, `run_config.json`, quote manifest |
| G2 outcome: turn-69 trade (2 railroads + $100), Sol yellow spend $300 / rent $0 / sales $150, d239 $77 vs $1,300 Park Place to Gemini, Gemini $900 yellow spend, Gemini wins | C | `agenda_flows.json`, `t05_spending_units.json`, `t06_eliminations.json`, canonical G2 `events.jsonl` seq 1659-1668 |
| G11 incident quotes (3 spans) and delivery | C | quote manifest (lines 514, 518), delivery checks |
| G11 outcome: Pennsylvania from Gemini estate turn 81; Sol pays $2,000 Boardwalk turn 125; d325 $1,100; terminal estate to Grok | C | `agenda_flows.json`, `t06_eliminations.json` |
| G11 d256 provider explanation echoes then corrects | I | baseline social detail |

## Construction (Section 5)

| Claim | Status | Source |
|---|---|---|
| 63 groups; 16/17, 17/18, 7/15, 3/13; 9 never buildable, 4 defaults, 4 conflicts, 3 valid END; entry 34/42 with 3/3/2 residuals | I (summary re-read) | `first_management_windows.json`, `t03_trade_groups.json` |
| END census 1,225 / 663 / 66 / 24 / 573 | I | `resolution_conditions.json` |
| 132 attempts, 70 well-formed all invalid, 63 reachable, 7 over cash, 1 malformed, 61 unparseable; 63/66 decisions (61 Opus, 1 Sol, 1 Gemini) | I | `certificate_results.json` |
| 60 refusal->invalid retry->default chains; G2 d129 differs | I | baseline economic results |
| Recovery 20/29, 6/19, 5/5, 0/61; G2 d243 $208 vs $358 | I | `t07_build_recovery.json`; baseline |
| 55/66 defaults in G5 and G13 | I | baseline per-game table |
| G3 d176 and G1 d426 holds | I | baseline economic results |

## Liquidity and inheritance (Section 6)

| Claim | Status | Source |
|---|---|---|
| 60 eliminations, 56 declared, 4 automatic; 56 bound below debt; 3 payable; G7 lock | C (tabulation) / I (witnesses, search) | `retabulate.py` `eliminations`; `certificate_results.json` |
| Menu-only finance below debt in all three payable cases (183, 43, 30 vs 500, 250, 550) | N | `t06_eliminations.json` field `menu_mortgage_only` |
| Witness remainders $38, $43, $180; alternatives $8, $155 | I | baseline Table / certificate package |
| G7 d339 details | I | baseline economic results |
| G12 d249 incident quotes and outcome | I | shared manifest; baseline transcript controls |
| G12 winner Opus; estate to Opus | C | `t01_cohort.json`, flows |
| G20 d327-336; G16 d602 | I | baseline economic results |
| 103 units; $103,450; $93,000; $92,550; 40 zero; 26 without elimination; 57/60 rent eliminations; G19 dark blues | I | `t05_spending_units.json`; baseline appendix |
| Estates: 54/60 to winner, 35/40 nonterminal, 1 to bank; deeds 372/397, 202/227 | C | `retabulate.py` from flows, cohort, eliminations |
| Estate cash $7,148 of $7,843 nonterminal; winners' paid rent $78,737 of $121,154 | I | negotiation review (independently reproduced there) |
| G18 Illinois trade turn 120, estate to Sol turn 138; G13 yellows to Sol at turn 150 | C | `agenda_flows.json` |

## Conduct (Section 7)

| Claim | Status | Source |
|---|---|---|
| Cash-seeking offers 339; <$100: 132 (18/52/62); >=$700: 51 (13/32/6) | N | `retabulate.py` `cash_seeking_by_author_cash` |
| G13 chronology, events 1808-1812, $295 alternative, d244 correction, 4/36 | I | shared manifest; baseline transcript and review dispositions (OC-03, OC-05, SOC-R3-02) |
| G13 d251 public message ("lift it", $130) | C | offer ledger row d251 |
| G13 d311 elimination ($200 owed, $49) | C | `t06_eliminations.json` |
| G18 chronology d421-442; withdrawal explanation | I | shared manifest; baseline transcript |
| G18 Pacific from Grok estate (turn 138); later offers d454-461; Sol eliminated d463 owing $900; Pacific to Opus terminal | C | `agenda_flows.json`, offer ledger, `t06_eliminations.json` |
| G18 d442 is a recipient-only rejection by Opus | C | offer ledger |
| G20, G3, G19 chronologies and witness routes | I | shared manifest; baseline transcripts and source reviews |
| G6, G4, G11 echo, G12 d195 rejected label, G18 d83 conflict, G9/G16 funding refusals | I | baseline social detail and transcript controls |
| 15 equal-argument conflicts; 4 accept trades against message | I | baseline social results |

## Temporal (Section 8)

All counts (240 records, 53 empty Opus private fields, 59/36/25 codes, 8 landing policies 6/1/1, G9, G16, G2 d161, G19 d220, recurrence 114/54/50/9, 31/29/2, 54/63) are **I** from `agenda_temporal.json`, `agenda_landing_endpoints.json`, `agenda_longitudinal_witnesses.json`, `agenda_recurrence.json` and the baseline text.

## Discussion and appendices

Seed-block outcome patterns (block 2 all Sol; block 3 seat 2 under four configurations) are **C** from `t01_cohort.json`. Pilot and scenario numbers (Appendix G) are **I** from `agenda_evaluation.json` and `agenda_readiness.json`. Norms comparison table is **I** from the baseline appendix.

## Not performed in this draft

No engine replay, certificate re-execution, new legal-sequence witness, model call, game, reference-policy run or synthetic test. No re-reading of all provider reasoning. No human annotation. Delivery checks for shared-manifest incidents are inherited.
