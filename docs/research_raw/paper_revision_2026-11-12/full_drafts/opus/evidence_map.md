# Evidence map: Opus independent draft, 12 November 2026

Every claim in `manuscript.pdf` maps to a row here. "Checked" means recomputed or re-read from stored records by a script in `analysis/` during this draft. "Inherited" means taken from earlier work without rerunning. No row depends on a new game, engine execution, replay execution, baseline, synthetic state, provider probe or model query.

## Inputs

| Input | Used for | Status |
|---|---|---|
| `saved_games/railway-research-*/game-*/run/decisions.jsonl`, `events.jsonl`, `players.json`, replay reports | All record checks | Read directly; SHA-256 of every file read is stored under `sources` in each `data/*.json` |
| `paper_revision_2026-11-11/integrated/data/offers.json` (sha256 `a2eb9434…`) | 920-response offer ledger | Inherited reconstruction of post-trade holdings; every count here recomputed from it |
| `paper_revision_2026-11-11/integrated/data/liquidation_episodes.json` | 188 debt episodes | Inherited episode boundaries; bound, tiers, actions and texts recomputed from first menus and applied actions |
| `paper_agenda_revision_2026-10-29/negotiation/rejection_reason_coding.json` and `reviews/negotiation/reason_comparison.json` | 61/74 codes | Inherited LLM codes; membership and counts rejoined |
| `contracts/data/board.json` | Prices, mortgage values, house costs | Read directly |
| Git history at `42f85183…` and `d6808534…` (`git show`, read-only) | Tool choice, refusal policy, fallback policy | Read directly |
| Inherited bib files and printed prompt texts | Bibliography, Appendix B | Byte copies; hashes equal `baseline_manifest.json` |

## Claims

| Manuscript claim | Evidence | Status |
|---|---|---|
| 20 games, 5 seeds, cyclic rotations; seeds 751774554, 2506298840, 2573692901, 3648314310, 2766649504; commits; seat orders; winners 8/7/3/2, by seat 7/7/3/3 | `data/provenance.json` (`cohort`, `seeds_in_block_order`, `wins_*`) | Checked |
| 50,918 events; artifact replay compares all 50,918 with no exclusions; state replay compares 24,506 after dropping four LLM event types and renumbering; both pass in 20/20 | `data/provenance.json` (`replay_totals`, per-game `replay`) | Checked by reading stored reports; replay executions inherited, not rerun |
| 6,989 decisions; 8,679 attempts; per-system decisions/attempts; Opus 1,604 recovery decisions; fallback counts 61/4/1/0 | `data/provenance.json` (`response_conditions`) | Checked |
| 1,605 refusals, one identical message, `content_filter/refusal` | `data/provenance.json` (`refusals`) | Checked |
| Grok `tool_choice: "required"`, others `auto`, at both commits; `claude_refusal_recovery_v1`; `finance_before_bankruptcy_v2`; named Opus fallback model | `data/provenance.json` (`configuration_at_run_commits`) | Checked from source at both commits |
| Grok: 1,068 responses name an action in content, 139 conflict; 64 conflicting opening threads | `data/provenance.json`; `data/offers_analysis.json` (`grok_conflict_openings`) | Checked |
| 2,054 prompts with misattributed past-trade summaries | Earlier condition audit | Inherited |
| Printed prompts equal stored G1 system messages up to line wrapping | `data/provenance.json` (`printed_prompts_match_g1_records`) plus token comparison in this draft | Checked |
| 920 responses: 113/394/413; recipient splits; Opus 162/189 under recovery | `data/offers_analysis.json` (`population`) | Checked |
| Full opening and later tables (918 legal offers) | `data/offers_analysis.json` (`full_table`) | Checked |
| Headline cells 95/116 vs 37/72; 42/70 vs 67/103; both-party swaps 34/48; recipient-completing sales 29/45; later 8/39 vs 7/34, 13/61 vs 13/73 | `full_table` | Checked |
| Grok wrote 36/72 comparator swaps and 15/17 acceptances; 13 of 15 from conflicting openings; $4,020 net list value | `comparator_swap_composition` | Checked |
| Opus wrote 110/173 headline cash bids | `cash_bid_composition` | Checked |
| Composition versions 30.5 / 22.6 / 16.7; cash −5.0 / −4.1 / −8.6 | `composition_versions` | Checked |
| Proposer gaps Sol +6.2, Opus +18.8, Grok +26.4; standardized 16.0 / 21.5 / 18.1; recipient gaps all positive; 7 of 9 pairs positive | `strata`, `swap_gap_standardised_by_proposer`, `author_recipient_swap_pairs` | Checked |
| Seed blocks: swap gap positive 5/5 (19.4–40.5), drop-one 28.7–33.3; without Grok-authored 4/5, block 4 −23.5 | `seed_blocks` | Checked |
| Two-stage intervals +12.3 to +48.8; +1.4 to +45.7; −10.0 to +40.9; cash −26.5 to +11.4; games-only and blocks-only in Table 10 | `resampling` (20,000 draws, seed 20261112) | Checked (retrospective description, not confirmation) |
| Median net list value +170 vs +80; positive-value swaps 86/103 vs 24/48, 81/95 vs 18/25 without Grok | `headline_offer_terms`, `swaps_with_positive_net_list_value` | Checked (crude list-price measure) |
| Rejection by proposer house capacity (26/33, 42/48, 23/27; cash 13/19, 7/20, 20/28) | `proposer_only_by_house_capacity` | Checked |
| Counters: 26 of 70 cash bids, 20 of 116 swaps; 15 of 26 keep deeds and ask more cash | `full_table`, `opening_counters` | Checked |
| Keyword screen 93/95, 83/95, 42/42, 35/42 | `keyword_screen` | Checked (regex, not coding) |
| 61/74 codes: population disjoint from headline cells; 27/38, 34/36; Gemini 29, Grok 27; 31 in G1/G15 | `semantic_population` | Membership checked; codes inherited |
| Holder-cash rejection by system (Sol 4/26 vs 25/45 …) | `proposer_only_requests_by_holder_cash` | Checked |
| Fourteen paired histories (13 cash falls, 5 same bundle, 8 more cash) | 11 November integration `tools/check_offer_forms.py` | Inherited |
| 188 episodes; 128 paid; 56 above bound; G7 menu-restricted ($440 vs $750, bank houses 0, no sale offered); 3 payable declarations | `data/finance_analysis.json`; `quote_manifest.json` (`g7_d338_menu`) | Partition and G7 menu checked; payment witnesses and G7 menu search inherited |
| Tiers A 62/62, B 53/52, N 16/14; 67 one-action payments; median debt/bound 0.36; 180 mortgages, 89 sales, $51,997; no fallback in payments | `finance_analysis.json` | Checked; own-asset bound equals ledger bound in 188/188 |
| N by system: Gemini 5/6, Opus 5/5, Sol 2/3, Grok 2/2; gap $12–$326 | `necessary` | Checked |
| 19 uses / 33 mortgages = 14 necessary + 5 optional (G3 Gemini ×4, G18 Sol d428) | `unlocked_uses`, `optional_uses` | Checked |
| First-decision text: 13 explicit (9 notes, 4 Opus returned reasoning), 1 open check, 2 omit; 12 of 13 with all stated amounts correct; G2 $430 vs $400; G4/G8 unvalued | `data/necessary_text_reading.json`; spans verified in `provenance.json` (`necessary_reading`) | Spans checked against originals; classification is a single LLM reading, not human annotation |
| Sequences 2–10 actions, sales precede first released mortgage | `necessary_paid_structure` | Checked |
| G20: $700 sales, $665 mortgages, $1,400 rent, $14 remainder; 2 sales + 8 mortgages, 5 released; creditor components $675/$690 | `quote_manifest.json` (`g20_payment`), `finance_rows.json` | Checked |
| G12 d249: note and content describe payment; applied call declares | `quote_manifest.json` (`g12_d249_applied`, quotes `g12-*`) | Checked |
| Eight incidents: 49 quotation spans in original fields; 24 public-message receipts in the addressee's next stored prompt | `data/quote_manifest.json` | Checked |
| Incident outcomes: G15 offers and post-trade cash, Grok's blockers pass to Gemini, Sol never completes yellow or green; G2 reversal and yellows to Gemini; G19 trade completes no group; G7 prices $600/$700, five mortgages, four orange houses, three dark-blue houses, Sol wins; G13 $200 + $16 interest, NC auction turn 114, Atlantic to Sol; G20 Vermont mortgaged d102, Opus bids, Grok first out, Gemini wins; G18 two-player at d421, redemptions d445/d448, bids and asks, Opus wins | `quote_manifest.json` (`outcome_checks`) plus events read for G2/G7 builds | Checked; G7 "$270 orange rent" was not used |
| G18: no Opus text d421–461 mentions inherit/estate/creditor | `provenance.json` (`g18_opus_text_hits`, `g18_inheritance_terms_found` = []) | Checked |
| G13 probability: a direct nine from Atlantic is 4/36; Grok's next note uses 4/36 | Board arithmetic; quote `g13-fourth` | Checked |
| Usage USD 141.71; reasoning-token means | Earlier draft accounting | Inherited |
| Construction defaults, first-estate counts, exposure summaries | Not used in this draft | n/a |

## Literature read for this draft (12 November 2026)

| Source | Scope read |
|---|---|
| Valmeekam et al., PlanBench (NeurIPS 2023 D&B) | Proceedings abstract page |
| Duan et al., GTBench (NeurIPS 2024) | Proceedings abstract page |
| Bonjour et al., Monopoly hybrid DRL (IEEE TETCI 2022) | First page and abstract of the author PDF |
| All other citations | Inherited from earlier drafts' verified bibliography; not re-read here |

The five-step evidence ladder adapts the construct table in the attached 11 November referee report. The paper does not attribute it in prose because the report is not a publication; this note records the source.
