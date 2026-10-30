# T7. Affordance ledger: what the sandbox implements, what this cohort used, what remains unimplemented

Opus, 2026-10-29. The three-layer split (environment affordance / analysis protocol / not implemented) was agreed with Fable (debate R5). The wording on non-identification was corrected after Astra's R3. A row marked "implemented" in the environment layer means the code exists and was exercised. It does not mean the cohort measured something with it unless the "Used" column says so.

## Layer 1: environment affordances (implemented)

| Affordance | Evidence | Used for a cohort finding? | Enables | Not established by this cohort |
|---|---|---|---|---|
| Engine-authoritative rules with an explicit legal-action menu at every decision; invalid actions rejected | `decisions.jsonl` menus; engine; `docs/model_response_policy.md` | Yes, for all economic findings | Exact legality, opportunity-conditioned denominators | Applied rule violations cannot occur by construction. Attempted invalid actions are recorded as validation errors, not misconduct |
| Free-text public message on every action, visible to all players | `SYSTEM_PROMPT_V1`; `LLM_PUBLIC_MESSAGE` events | Yes (R18–R21) | Proposition-level social chronology with exposure tracing | Persuasion effect; belief change |
| Private note channel, instructed to "reflect true reasoning", fed back as memory | `SYSTEM_PROMPT_V1`; prompt memory | Partly. Mostly absent for Opus (action-only after refusal) | A soft honesty norm can be audited case by case | A knowing false private note is not identified in any checked case. Error, stale context and channel conflict remain possible |
| Engine-settled bilateral trades, up to 20 exchanges, with counters | `run_config.json` `max_trade_exchanges: 20`; TRADE_* events | Yes (R03–R05) | Two-sided consequences; initiator versus final-terms author | Trade value or bilateral welfare |
| Unenforced verbal assurances (for example "offer stands") in public text | No commitment object exists; assurances are free text only | Yes, one case (G18, R20) | Withdrawal or invocation chronology | Breach rate; costly reliance |
| Forced liquidation (sell buildings, then mortgage), finite house stock, creditor inherits estates intact (declared variant) | `docs/benchmark_audit_fixes.md`; engine | Yes (R08–R10, R15–R17) | Accessible versus nominal finance; stock restrictions; inheritance concentration | Causal effect of inheritance or house denial on winning |
| Per-attempt response provenance, with refusal-recovery stages and deterministic fallback | `run_config.json` `response_policy`; attempt records | Yes (M1, T4) | Distinguishes chosen holds, rejected plans and defaults | The effect on outcomes of a different recovery policy |
| Model-specific request settings (Grok `tool_choice="required"`; others `"auto"`) | `player_config.py:328–334` at both run commits | Yes, as a qualification (R23) | Configured-agent unit | Origin of received-name conflicts |
| Deterministic seeded engine; event, action, decision and snapshot artifacts; state and artifact replay | Saved-game `run/`; Sol's 20/20 replay | Yes (integrity) | Reproducibility; audit | — |
| Exact decision-prefix reset with event-rebuilt memory, plus engine-validated stepping of alternative legal actions | `paper_phase1_2026-10-28/opus/opus_sandbox_checks.json`: 20 branch checks, all passing prefix-identical, memory-equal, suffix-reproduced and branch-divergence checks | Yes, through the analysis protocol (Layer 2) | Local feasibility tests | Full counterfactual games; alternative winners |
| Scripted reference policies (`random_legal`, `always_buy`, `cash_conservative`, `no_trade`, `builder`, `auction_aggressive`) | `python/packages/arena/src/monopoly_arena/baselines.py`; exercised in the 20 phase-1 rollouts | **No** (implemented, not measured for the cohort). `propose_trade` uses empty arguments, so baselines cannot exercise the trade route | Seat and dice baselines (experiment matrix C-tier O6) | — |
| 130 micro scenarios with a legality-validating runner | `contracts/micro/scenarios/` (130 files); `micro_runner.py` | **No** (no cohort results) | Targeted capability probes under fixed states | — |

## Layer 2: analysis protocols (performed by analysts, not an environment API)

| Protocol | Evidence | Findings |
|---|---|---|
| Exact-prefix multistep legal-sequence audit to a stated local endpoint, without continuing the historical suffix | `core_review/astra/default_build_plans.json`, `g07_hotel_lock.json`, `g12_channel_liquidation_check.json`; `core_review/opus/bankruptcy_bounds.json`; `core_review/sol/elimination_upper_bounds.json` | R06, R08–R10; refuted generated labels (G6-C021, G14-C014, G20-C024) |
| Event-based economic accounting with ownership windows, estate provenance and censoring | `core_review/astra/development_aggregation_check.json`; `core_review/sol/corpus_economics_audit.json` | R12–R16 |
| Proposition-level social chronology: truth, speaker record, exposure, recipient response, settlement, competing explanation | `core_review/sol/g13_omission_check.json`, `g11_social_channel_checks.json`, `g04_uptake_boundary_check.json`; `core_review/astra/g13_claim_checks.json` | R18–R21 |
| Channel-conflict diagnostics (content versus received tool name and arguments) | `core_review/sol/received_name_conflict_audit.json` | R23 (a diagnostic count) |
| Prompt-exposure tracing over time | `core_review/astra/negotiation_units.json`; `paper_phase1_2026-10-28/sol_round2/public_delivery_summary.json` | R22; delivery omissions |

## Layer 3: not implemented, and needed for specific alignment or safety claims

| Missing affordance | Claim it would unlock | Comparable design elsewhere (verified) |
|---|---|---|
| Binding or deferred commitment objects (IOUs, future payments, conditional deals) that the engine records but does not enforce | Breach rate of unenforced commitments, with a counted opportunity and observable reliance | Arena App. D measures transfer-promise enactment (free-text promises) |
| Private bilateral messaging | Secret coordination; private deception; coalition formation | Arena emails go to named recipients only (§2.1) |
| A treatment with an explicit public-honesty or no-contradiction norm | Instruction-violation rates for public speech | AgentMonopoly §4 prohibits public/action contradiction |
| Engineered violation opportunities (actions that are possible, rewarding and against a stated rule, with monitoring) | Misalignment under temptation; capability × violation trend | Emergent Collusion (arXiv 2609.24967) protocol-violation affordance (abstract) |
| An oversight or monitor agent with a frozen channel and adjudicated ground truth | Monitor accuracy; monitorability | CoT-monitoring literature (Baker et al. 2025; Korbak et al. 2025) |
| Packaged branching API, reward interface, RL adapter, training loop | Training or improvement claims | Not implemented anywhere in this repository. No training claim is made |
| Human participants | Human–agent conduct | Arena §6 lists this as future work |
| A capability axis (several tiers within one provider lineage, same harness) | Capability–alignment trend | Arena §5.3.2 (cross-model null); Emergent Collusion (within-family positive) |

**Caption.** The environment already makes economic conduct, public speech, private notes and per-attempt provenance adjudicable against exact legal state.

The present cohort uses Layers 1 and 2 to produce descriptive economic and social findings. The alignment-relevant claims the paper does *not* make need specific Layer 3 affordances, each paired with a treatment and a counted opportunity.
