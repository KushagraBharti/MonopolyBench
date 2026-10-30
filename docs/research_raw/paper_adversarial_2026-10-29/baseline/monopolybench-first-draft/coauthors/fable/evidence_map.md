# Evidence map for `setup_related.tex` (Fable, 2026-10-29)

Every numerical or social assertion in my sections is traced here to an original audited file. Paths are relative to the repository root. "Original" means a canonical saved-game artifact or the frozen source; "audited" means a phase-1/2/3 output whose script and hashes are retained. I did not re-run the phase-2 semantic judgments; where a number rests on a peer's audit, the peer is named.

## Rules and configuration (§2.1, Table `tab:rules`)

| Assertion | Source | Note |
|---|---|---|
| Standard 40-space US board, names and prices | `contracts/data/board.json` (read 2026-10-29) | Confirms AgentMonopoly's renamed streets are a difference |
| $1,500 start; 32 houses; 12 hotels | `python/packages/engine/src/monopoly_engine/models.py` lines 7–9 | `DEFAULT_STARTING_CASH`, `DEFAULT_HOUSES`, `DEFAULT_HOTELS` |
| $200 salary; $200 income tax; $100 luxury tax; $50 jail fine; hotel after four houses; three doubles to jail | `engine.py` lines 36–37, 609, 680; `prompting.py` lines 458–460 | `JAIL_FINE = 50`, `HOUSE_LIMIT = 4` |
| Free Parking pays nothing | no `FREE_PARKING` payout logic in `engine.py` (grep 2026-10-29) | Space exists in `board.json` as kind `FREE_PARKING` |
| Get Out of Jail Free card exists; transfers to creditor at bankruptcy | `engine.py` lines 1296, 2951–2975 | Phase-1 note: no dedicated card-transfer event |
| Open ascending auction in seat order; no-bid deed stays unowned; no forced later auction | `engine.py` `_auction_bidders_in_order`, `_apply_auction_bid`, `_finalize_auction(..., reason="NO_BIDS")`; `docs/benchmark_audit_fixes.md` ("bank-returned properties become unowned without immediate auctions") | Max 200 auction actions (`run_config.json`) |
| Trades: cash, deeds, jail cards; accept/reject/counter; 20 exchanges; 10% interest on received mortgaged deed; no deed from a developed group | `run_config.json` `max_trade_exchanges: 20`; `engine.py` lines 1774, 1778–1799, 1924–1938 (`MORTGAGE_INTEREST`), 1979 (`TRADE_EXPIRED`), 1993 (`TRADE_RESPONSE_DECISION`) | Interest = ceil(0.1 × mortgage value) per deed |
| Ordered build plan validated entry by entry | `docs/benchmark_audit_fixes.md` Findings 1–8; `engine.py` lines 2785–2796, 2854 | Phase-2: 61 Opus plans rejected as uneven-in-order yet executable interleaved |
| Hotel sale requires four bank houses; building sale returns half cost; zero bank houses blocks the next house purchase only (own sales and hotel conversions elsewhere can return houses) | `engine.py` lines 2543–2569 (`_buildable_space_indices`, `_sellable_building_space_indices`), 2840, 2849 | G7 d339 hotel lock rests on this rule; G12 d312 restructuring route (Sol's audit) shows reallocation under zero stock |
| Mortgage = price // 2; redemption = `int(math.ceil(value * 1.1))` in floating point | `engine.py` lines 2484–2490 | Checked 2026-10-29 over all 16 board principals: engine charges one dollar above exact ceil(11m/10) for m ∈ {50, 90, 100, 110, 200} (prices 100, 180, 200, 220, 400), e.g. $111 for a $100 principal; trade interest `ceil(m * 0.1)` equals the exact value for every board principal |
| Liquidation menu: mortgage, sell buildings, declare; no trade | `engine.py` `_build_liquidation_decision` lines 1422–1460 | Menu has no `propose_trade` |
| Sales unlock mortgages within the same liquidation | `docs/benchmark_audit_fixes.md`; phase-2 `core_review/opus/bankruptcy_bounds.json` (`menu_mortgage_only` vs `accessible`) | |
| Declaration accepted while finance remains (surrender) | `docs/benchmark_audit_fixes.md` ("voluntary bankruptcy is surrender even if financing remains") | |
| Automatic elimination when no mortgage or sale option; jail-fine insolvency on third failed roll | `engine.py` lines 2402–2405, 564–565 | Four automatic eliminations in cohort: phase-3 `astra/exhibits/t06_eliminations.csv`, caption F6 |
| Creditor inherits deeds intact, mortgage flags, cash, jail cards; no interest; bank bankruptcy returns buildings and frees deeds | `engine.py` `_handle_bankruptcy` lines 2951–3030 | `PROPERTY_PURCHASED` with price 0 to creditor |
| No management phase while remaining in jail | `engine.py` lines 1495–1497 (`if player.in_jail: self._end_turn(...)`); `docs/benchmark_audit_fixes.md` | |
| No turn cap; all games end by bankruptcy; 75–386 turns | `run_config.json` `max_turns: null`; `saved_games/railway-research-*/game-index.csv` (turns 75 for G10, 386 for G16); `saved_games/railway-research-12-games-2026-10-25/README.md` | |
| Seeded RNG, synthetic timestamps | `run_config.json` `engine.deterministic_rng_seed`, `event_timestamps {start_ts_ms: 0, ts_step_ms: 250}` | |
| Treatment `audit_corrected_v2`; two fingerprints | `run_config.json` (G1: `2f471f70…`); `railway-research-8-games-2026-10-26/game-index.csv` (G13–20: `9a15ddc8…`) | |
| 475 / 72 / 207 / 397 deed acquisitions | `docs/research_raw/paper_phase1_2026-10-28/phase1_results.json` `economic_results.deed_routes`; re-verified in `coauthors/sol/verification.json` (2026-10-29) | |
| 16 / 9 / 63 / 121 group completions; 69 terminal inherited | `coauthors/sol/verification.json` `completions`; `phase1_results.json` `peer_validation.terminal_inheritance_episodes = 69` | Sol's fresh reduction, 2026-10-29 |
| Nine games reach zero bank houses | `docs/research_raw/paper_phase3_2026-10-29/fable/exhibits/house_stock_report.json` (validated against all 6,989 delivered bank states, 0 mismatches); Sol's `verification.json` `zero_house_games = [3,4,5,6,7,9,12,14,18]` | |

## Information and normative contract (§2.2, Table `tab:contracts`)

| Assertion | Source |
|---|---|
| Six decision types | `engine.py` lines 391, 1311, 1362, 1416, 1454, 1993 |
| Game-state payload fields (cash, position, jail, holdings with houses/hotel/mortgaged, jail cards; bank houses/hotels; unowned spaces; memory) | `python/packages/arena/src/monopoly_arena/prompting.py` lines 487–565 (`build_game_state_payload`) |
| Player names in the payload are the model names | `prompting.py` `"name": player.get("name")`; `run/seat_assignment.json` (`player_name` = `gpt-6.1-sol` etc.) |
| 20-entry public timeline; 10 private notes | `prompting.py` lines 51–53, 100–101 (`public_timeline_last_20`, `your_private_thoughts_last_10`) |
| Public message and private thought required on each action | `prompting.py` lines 86–88; `SYSTEM_PROMPT_V1` |
| Identical initial system prompt for all 6,989 decisions | `phase1_results.json` `initial_system_prompt_sha256_counts` (one hash, 6,989) |
| 6,882 non-empty public messages; 149 not inserted (94 building merge, 55 unsummarized event) | `docs/research_raw/paper_phase1_2026-10-28/sol_round2/public_delivery_summary.json` |
| 2,054 of 6,989 initial prompts with ≥1 trade-history defect manifestation; 44 accepted trades affected | `docs/research_raw/paper_phase2_2026-10-28/core_review/astra/negotiation_units.json` (R22); `core_review/sol/trade_timeline_audit.json` |
| Prompt wording quoted | `python/packages/arena/src/monopoly_arena/player_config.py` `SYSTEM_PROMPT_V1` (read 2026-10-29, unchanged) |
| One corrective retry then deterministic fallback | `docs/model_response_policy.md`; `run_config.json` `fallback_policy: finance_before_bankruptcy_v2` |
| Normative-contract table rows | `docs/research_raw/paper_phase3_2026-10-29/opus/exhibits/normative_contracts.md` (Opus, checked by me against the prompt and Arena §2.1–2.2/§4.1/App. D in phase 3) |

## Participants and conditions (§2.3, Table `tab:conditions`)

| Assertion | Source |
|---|---|
| OpenRouter IDs, provider pins, `allow_fallbacks: false`, effort `medium`, `top_p: null` | `contracts/research/monopoly_long_v1_model_rosters.json`; `run_config.json` `players[]` |
| No temperature or nucleus parameter set | grep of `player_config.py` and `openrouter_client.py` for `temperature|top_p|max_tokens` returns nothing (2026-10-29) |
| Grok `tool_choice="required"`, others `auto`; Opus rejects forced tool use | `player_config.py` `tool_choice_for_model` (lines ~356–364); `docs/model_response_policy.md` |
| Decisions 1,961 / 1,669 / 1,696 / 1,663; attempts 1,991 / 1,689 / 3,301 / 1,698; cost 18.72 / 18.59 / ≥48.80 / ≥55.60 (attempts missing cost 0 / 0 / 1,600 / 3); completion tokens 128 / 368 / 410 / 4,041; latency 4.8 / 8.2 / 7.1 / 65.0 s | `docs/research_raw/paper_phase3_2026-10-29/opus/exhibits/cost_usage.csv` (Opus; cohort_overview.json scripts) |
| 8,679 attempts; 6,989 decisions; 50,918 events | `phase1_results.json` `visibility_totals` |
| Fallbacks 61 / 4 / 1 / 0 | `core_review/fable/methods_and_findings.md` §3 (66 fallbacks); `core_review/fable/fallback_inventory.json`; Opus's `h1_build_defaults_rows.json` |
| Opus 1,605 refused attempts over 1,605 decisions; 1,604 first-attempt refusals (standard→action-only chains); one second-attempt refusal at G2 d129; 60 action-only invalid → fallback | `phase1_results.json` `models.Opus.refused_attempts`, `decisions_with_refused_attempt`, `opus_decision_response_chains`; `paper_phase1_2026-10-28/opus/opus_response_audit.json` `attempt_chains.Opus` (`standard:illogical -> standard:refused`: 1). Wording corrected after Opus's step-15 review |
| Action-only recovery prompt removes the private-note field and the sentence asking that private thoughts reflect true reasoning | `python/packages/arena/src/monopoly_arena/prompting.py` lines 1226–1245 (`build_action_only_prompt_bundle`); `docs/model_response_policy.md` step 2 |
| Opus private memory empty 1,108, synthetic-only 286 (1,394 of 1,696) | `paper_phase1_2026-10-28/astra/memory_audit.json` `by_model` |
| Refusal share 0.57–0.76 in G1–4, 1.00 in G5–20 | `opus_response_audit.json` `opus_refusal_share_by_game` (0.762, 0.683, 0.566, 0.734; then 1.0) |
| Refusal text cites ToS output-duplication; cause unlocalized; Opus 4.8 never invoked | `docs/model_response_policy.md`; `saved_games/railway-research-12-games-2026-10-25/README.md` ("No physical Opus 4.8 calls"); phase-1 Astra methods draft |
| Grok 139 / 15 / 5 | `core_review/sol/received_name_conflict_audit.json` `summary` (139; 15 `exact_same_argument_name_only_conflicts`; 5 `literal_argument_json_substrings_equal`) |
| Seeds and rotations; seats 1–4 one-based | `game-index.csv` (seeds 751774554, 2506298840, 2573692901, 3648314310, 2766649504); `run/seat_assignment.json`; phase-3 F2 caption |
| Commits 42f85183 (G1–4) and d6808534 (G5–20); 18-file diff with no engine/prompt/resolver/model-client change | `game-index.csv` `git_sha`; `git diff --stat 42f85183 d6808534` (re-run 2026-10-29: 18 files, 281 insertions, 210 deletions; arena changes limited to `campaign_setup.py`, `execution_policy.py`, `supervisor.py`, one test) |
| Wins Sol 8, Gemini 7, Opus 3, Grok 2; seats 1–2 win 14/20 | `saved_games/*/README.md` ledgers and `game-index.csv` winners; `paper_phase3_2026-10-29/opus/outcome_dependence.json` |

## Artifacts and replay (§2.4)

| Assertion | Source |
|---|---|
| Per-game artifact inventory | `saved_games/railway-research-12-games-2026-10-25/game-01-216turns-6ede2b6e/run/` listing (events.jsonl, decisions.jsonl, state/, prompts/, usage_attempts.jsonl, replay_report.json, summary.json) |
| Full event replay 20/20 | `saved_games/*/README.md` ("12 of 12 … passed newly computed state and artifact replay"; 8-game collection likewise); `saved_games/*/audit/verification.json` |
| Memory reconstruction equal at 6,989 decisions; 20 branch checks (prefix identical, memory equal, suffix reproduced, divergence); 19/20 reference rollouts terminal | `docs/research_raw/paper_phase1_2026-10-28/opus/opus_sandbox_checks.json` `memory_reconstruction`, `branch_summary` |
| Six reference policies; no substantive trade proposals | `python/packages/arena/src/monopoly_arena/baselines.py` lines 11–16; phase-3 affordance ledger (Opus) |
| 130 micro scenarios, unused for cohort | `contracts/micro/scenarios/` (130 files); phase-3 affordance ledger |

## Related work (§7)

All factual statements about other papers are the versions and sections recorded in `docs/research_raw/paper_phase3_2026-10-29/reference_registry.json` and my `paper_phase3_2026-10-29/fable/literature.md` (sections inspected are listed there per source). Peer-attributed reads: FinBoardBench §4.3 and App. C.3 (Sol, Opus); DECE §3.2/§4.3/A.3 (Sol); Empty Commitments v2 §§2–5/App. E and Who May Release §§2–6/App. D (Sol). Arena study numbers (20 runs, 79 agent-runs, 2,583 emails, 13 models, 12.58%, promise enactment, single labeler, not redistributed) are from my own two-pass read of arXiv:2608.14825v3 §2.1–2.2, §4.1, §5.1, §6, App. A, B, D, H, I. AgentMonopoly facts are from arXiv:2610.29330v2 §3–5, Limitations, App. A.1/A.3 and the README at commit 2434f427. Cattle Trade, SOTOPIA, NegotiationArena, Concordia, MACHIAVELLI, MASK, Safetywashing, Emergent Collusion, the agent benchmarks and the CoT papers were checked at abstract/metadata level only, which is why the prose attributes to them only abstract-level claims.

## Limitations (§7.x)

| Assertion | Source |
|---|---|
| Rule misstatements by models (jail doubles bonus roll, bankruptcy interest, fabricated redemption restriction G6 C021 vs genuine locks G7 d338 / G15 d215) | `core_review/fable/methods_and_findings.md` §4.7; `core_review/astra/g06_claim_checks.json`, `g07_hotel_lock.json` |
| One liquidation prompt naming a single creditor for a pay-each-player card | G19 d263, `core_review/fable/methods_and_findings.md` §4.6 (incidence beyond this case unreported) |
| One public message containing a private-note string, recognized by the recipient | G20 d001/d004, `core_review/sol/additional_social_channel_checks.json` (R21) |
| 219/240 sample decisions ordinary play; extraction models Sonnet/Haiku/Terra; 614 catalog entries incl. 21 historical | `core_review/README.md`; `core_review/fable/methods_and_findings.md` §2 |
| 3 / 56 / 1 elimination split; mechanisms differ (G12 d249 received declaration vs survival content) | `core_review/opus/bankruptcy_bounds.json`; `core_review/astra/g12_channel_liquidation_check.json`; `core_review/sol/elimination_upper_bounds.json` (R08–R10) |

## Corrections received during drafting (applied or not applicable to my sections)

- Sol (2026-10-29): G15 Gemini's first completed group is ORANGE (e711, d094 turn 47; first build e718 d095; $3,250 developed orange rent at e1159/1491/1641/1870); brown (e1423–1424) and dark blue (e1565–1566) are inherited; GREEN completes only terminally (e1994–1995). My sections do not narrate G15; the older "natural green" phrasing must not reappear anywhere.
- Sol: G19 Gemini cumulative own dark-blue spend is $2,000; $1,200 is a single later step. Not used in my sections.
- Sol: winner spending units are 58 with 34 containing inherited deeds and 30 first completed through an estate; older 57/33 figures are superseded. Not used in my sections except as the 58/34/30 convention.
