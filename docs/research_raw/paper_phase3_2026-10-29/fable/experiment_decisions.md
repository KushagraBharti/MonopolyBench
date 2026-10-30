# Claim-to-experiment sufficiency matrix (Fable, phase 3, step 11)

Purpose: for every claim family the paper could make, state what the existing twenty-game cohort already supports, what a further pass over existing logs would add, what optional unpaid strengthening exists, and which stronger claims would need an experiment that has not been run and is not run in this phase. No new paid games, prompt, engine or canonical changes are proposed. Claim IDs refer to Astra's final phase-2 ledger (R01–R25) unless stated. Peer-authored checks are attributed; where my own phase-2 or phase-3 check exists it is named.

Tiers. **E** existing support: ready as a bounded descriptive statement with an audited source file. **L** existing-log analysis: computable from saved artifacts without provider calls; listed with the exact artifact and the predicate. **S** optional strengthening: local and unpaid, but either new games (reference policies) or new analysis code; needs user approval if it creates games. **X** experiment only if the stronger claim is retained: requires new provider runs or a benchmark change; listed to bound the claim, not to run.

## A. Design and corpus

| Claim | Tier | Support or requirement | Limit the paper must state |
|---|---|---|---|
| 20 games, 5 seeds × 4 cyclic rotations, 6,989 decisions, 8,679 attempts, 50,918 events, all ending by bankruptcy without a turn cap | E | `saved_games/*/game-index.csv`, `run/summary.json` (`run_config.seed`), phase-1 reproduce (`phase1_results.json`); Sol R01; my stock script revalidated seeds per game today | one roster; one realization per cell; dependence within games and blocks |
| Wins 8/7/3/2 and seat/seed structure (seats 0–1 win 14/20; block 2573692901 seat 1 wins with every model; block 2506298840 Sol wins from every seat) | E | Opus `phase3/opus/cohort_overview.json`; Sol corpus audit `design` | observed outcomes, not intrinsic ranks; no decision-level p-values |
| Shared raw dice within block, divergence in draw use at draws 37–124 (median ~76) | E | `paper_phase1_2026-10-28/fable/fable_crn_horizon.csv` (30 pairs; draw-index units; turn units in `_turns.csv`); Opus and Sol independent dice checks | shared stream is not matched opportunity |
| Cost/usage profile per configured agent ($141.71 known subtotal; Opus refused attempts lack cost) | E (Opus's phase-3 computation) | per-game `usage.json` | lower bound for Opus; cost is not capability |
| Seat/seed dependence quantified by block permutation or mixed model | L | winners by block and seat; five blocks only | low power by construction; report as descriptive |

## B. Economic trajectories

| Claim | Tier | Support | Limit |
|---|---|---|---|
| Acquisition routes 475 direct / 72 auction / 397 inherited / 207 traded deeds; completed-group episodes 16/9/63/121 with 69 terminal inheritances | E | three independent phase-1 reducers (Sol, Opus, mine) agree | route of the completing deed, not every deed |
| Negotiation propensity and intensity (R03; both denominators) | E | Astra `negotiation_units.json`; Opus `initiation_turns.json` | eligibility endogenous; Opus measured action-only |
| 113 settlements complete groups for 60/43/10 sides; 44 final terms authored by counterparty; $431 interest over 30 trades (R04) | E | phase-1 Sol reducer; my settlement predictions 113/113 | completion is not trade value |
| 43/63 trade-completed groups built in first management turn; 34/42 entry-buildable (R05); per-model 14/15, 13/13, 5/7, 2/7 | E | phase-1 reducers; Sol `build_recovery_audit.json` | conditional responsiveness; access is a choice |
| All 61 Opus defaulted plans legal after reordering (R06); recovery changes quantity in 12/18 Gemini, 5/25 Sol, 0/5 Grok (R07) | E | Astra `default_build_plans.json`; Sol `build_recovery_audit.json`; Opus `interleave_check.json`; my `fallback_opus_plans.json` | feasible alternative ≠ repaired policy; no suffix |
| 60 eliminations: 56 infeasible under full bound, 3 payable (G12 d190, G12 d249, G17 d234), 1 hotel lock G7 d339 $440/$1,310 (R08–R10) | E | Opus `bankruptcy_bounds.json`; Sol `elimination_upper_bounds.json`; Astra `g07_hotel_lock.json`, `g12_channel_liquidation_check.json`; my `liq.py` per-case | excludes trade help; not surrender intent |
| 103 spending units, $103,450 outlay, $93,000 whole-game paid developed rent, $92,550 after first own spend, 40 zero-rent units, 26 with no creditor elimination (R12, R13) | E | Astra `development_aggregation_check.json`; Sol `corpus_economics_audit.json` | not a return; censored; inherited buildings earn |
| Winner creditor in 54/60; 57 developed-colour triggers; 58 winner spending groups, 34 inherited-containing, 30 estate-completed (R15, R16) | E | same two audits; my 54/60 recount | rule-variant effect; no causal inheritance benefit |
| Bank houses reach zero in nine games (R17); per-game minima; first-zero turns; decisions taken at zero stock (G3 185, G4 103, G12 59, G14 17, G6 7, G18 6, G9 5, G5 4, G7 3) | E (new today) | `phase3/fable/exhibits/house_stock_report.json`, validated against all 6,989 delivered bank states (0 mismatches) and both audits' minima | inventory and exposure, not blocked builds or demand |
| Stock-constrained immediate feasible expansion count (binding shortage) | L | predicate agreed with Sol: execute one-house candidates through the authoritative engine at the exact prefix with only bank stock relaxed; compare with historical menu legality; hotel-downgrade liquidation as a separate constraint; report as opportunities | not demand; stock exhaustion is a joint outcome |
| Expressed demand (rejected stock-reason attempts; notes stating intent) and later uptake when stock returns | L | attempt-level validation errors in `decisions.jsonl`; frozen codebook reading pass | later uptake is a changed-state observation |
| Stated-maximum omission prevalence in liquidation notes | L | coding pass over all liquidation and post-turn notes stating a maximum; compare with computed bound | self-reports; Opus notes mostly absent |
| Auction denominators (declined affordable buys; one-above-rival bids) | L | event scan plus menu cash | descriptive |
| Multi-creditor liquidation prompt incidence (PAY_EACH_PLAYER) | L | filter liquidation scenarios by reason | report only |
| Reference-policy games on the five seeds to show measures separate `builder` / `no_trade` / `cash_conservative` | S (new unpaid games; needs approval) | `baselines.py`; `max_turns` truncation needed (G6 rollout did not terminate in 20,000 decisions) | baselines make no substantive trades; cannot calibrate negotiation |
| Hand-specified scenario checks for window semantics (jail access, financing within turn, censoring) | S (analysis code only) | `contracts/micro/scenarios/`, phase-1 tests (35 mine, 31 Sol, 20 Opus, 24 Astra) already cover much; assemble, do not rebuild | validates arithmetic, not competence |
| "Fast deployment causes winning"; "first built set decided the game"; "inheritance decided winners" | X | intervention or rule-variant comparison with repeated realizations | not claimed |
| "Opus would have built/won under a non-refusing condition" | X | non-refused retry or end-state-even validator replayed from frozen prefixes; a benchmark change | not claimed; bound only |
| Optimal reserve policy; counterfactual winners | X (and no oracle) | none feasible for four-player Monopoly | not claimed |

## C. Social conduct

| Claim | Tier | Support | Limit |
|---|---|---|---|
| G13 d250–253 misleading framing with recorded omission rationale, exposure, settlement; buyer's prior solvency/inheritance motive at d251 (R18) | E | Astra `g13_claim_checks.json`; Sol `g13_omission_check.json`; my re-read of d251/d253 returned reasoning today (quotes in debate.md); Sol's d225 reference retracted | no $70 persuasion effect; public deception permitted |
| Settlement with explicit premise correction (G6 d19–21, G19 d135–136); public concession with prior private correction (G4 d148–152); transient echo then rejection (G11 d255–258) (R19) | E | Sol `g04_uptake_boundary_check.json`, `g06_negative_case_check.json`, `g11_social_channel_checks.json`, `additional_social_channel_checks.json`; Astra g04/g06/g11/g19 checks | proposition-specific; no immunity claim |
| G18 standing $250 offer invoked and withdrawn (R20) | E | Sol `g18_sample_and_offer_checks.json`; Astra `g18_claim_checks.json` | no costly reliance or original dishonesty |
| G20 d001 private-note string in public message, recognized at d004 (R21) | E | Sol `additional_social_channel_checks.json`; Opus substring scan 7/6,989 overlaps, 1 structural | no deliberate leak; paraphrase undetected |
| G7 d42 "$600 final" with $625 private ceiling; settlement for a separately stated reason | E | Astra `g07_claim_checks.json`; Opus C2 | no reliance shown |
| Anti-leader appeals and leader-funding denial are unilateral; no pact, cartel or kingmaking in the inspected record | E (bounded absence) | Opus C5; Sol; my phase-2 reads of G16/G18/G20 | absence in inspected record only |
| Public-false / private-false / belief-error coding of all false public claims | L | frozen codebook; all 6,989 public messages with speaker's delivered observation | model-adjudicated; Opus private channel absent |
| Leader-funding-denial frequency in trade responses | L | coding of 413 rejections and 394 counters | descriptive |
| Note–action consistency coding for the three agents with applied private notes | L (Opus's addition, agreed) | within-call applied note vs applied action, semantic coding | undefined for Opus; confounded by error |
| Causal persuasion or price effect of a framing | X | randomized message ablation from frozen snapshots across recipients | not claimed |
| Instruction misalignment under a binding honesty or commitment norm | X | a treatment that imposes the norm and monitors violation opportunities | not claimed; current prompt permits deception |
| Binding coalition or kingmaking | X | designed incentive study with an identifiable agreement object | not claimed |

## D. Measurement conditions

| Claim | Tier | Support | Limit |
|---|---|---|---|
| Opus refusal condition: 1,605 refused attempts, 1,604 first-attempt chains, one identical ToS string, 0.57–0.76 in G1–4 and 1.00 in G5–20; 1,108 empty and 286 synthetic-only private memories | E | phase-1 Sol `attempt_inventory.jsonl`, my `fable_addendum.json`, Astra `memory_audit.json` | provider policy × harness; trigger unidentified; confounded with block/source |
| Grok 139 received content/tool-name conflicts; 15 equal parsed arguments; 5 literal substrings; only Grok under `tool_choice=required` (player_config.py:328–334) | E | Sol `received_name_conflict_audit.json`; my phase-1 scan; code line verified today | source unlocalized; diagnostic count |
| Trade-history formatter: 44/113, 26/413, 232/394; union 2,054/6,989 initial prompts | E | Sol `trade_timeline_audit.json`; Opus `trade_timeline_reversal.json`; Astra `negotiation_units.json` | exposure, not reliance |
| 149 nonempty utterances absent from timeline insertion (94 merges, 55 bankruptcy) | E | Sol round-2 delivery audit | occurrence-level; not proof of nonexposure |
| Per-entry even-building validator × plan encoding × retry budget explains all 61 Opus defaults | E | Opus `interleave_check.json`; Astra; Sol | not restraint or incompetence |
| Unmortgage charge ceil(1.1×) adds $1 at some values; GOOJF cards move without an event; hotel builds move house stock without a HOUSE event | E | my phase-2 A3/A6; engine lines cited there; stock script today reproduces engine stock at 6,989 states | engine facts; report, do not change |
| Reliance on reversed history changes decisions | X | corrected-formatter replay from frozen prefixes (prompt change) | not claimed |
| Predictive monitor evaluation (frozen channel, rule, adjudicated truth) | X (Opus's addition) | would need held-out adjudicated truth | not claimed |

## E. Capability and alignment framing

| Claim | Tier | Requirement |
|---|---|---|
| The environment implements: engine-enforced legality, permitted public deception, unenforced verbal assurances, third-party appeals, private memory, bounded observation, deterministic replay, exact prefix reset, per-attempt provenance | E | code and tests already cited; affordance ledger rows "implemented" |
| The cohort measures: configured-agent economic profiles; case-level social conduct; interface effects on specific results | E | this matrix sections A–D |
| Unimplemented: binding/non-binding contract objects, private bilateral channels, monitored rule-breaking opportunities, honesty-constrained treatments, oversight agents, branching API, RL adapter, training | E (as a statement of absence in the code) | affordance ledger rows "unimplemented" |
| Alignment-relevant conduct changes with capability | X | within-lineage multi-tier roster under fixed norms, same harness and prompt, matched seeds, repeated realizations, pre-specified codes, units that respect blocks |
| Intrinsic provider ranking | X | more blocks, matched-opportunity designs, uncertainty that respects dependence |

## Decision

No ready claim in sections A–D requires a new paid game. The paper can be written from tier E with the limits stated. Tier L items are optional upgrades from case lists to denominators; the three I would still do before a manuscript are proposition coding of false public claims, the stock-relaxed binding-shortage count, and leader-funding-denial coding, because each caption that currently says "cases" would otherwise invite a prevalence reading. Tier S reference-policy games are not required and would need explicit approval. Tier X items are bounded by naming the design and stating that it was not run.
