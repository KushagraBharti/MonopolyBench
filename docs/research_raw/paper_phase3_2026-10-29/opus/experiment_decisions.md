# Step 11: claim-to-experiment sufficiency matrix (Opus)

Opus (claude-opus-5-5), 2026-10-29. No new games were run, no provider was called, and no benchmark behavior was changed.

This matrix applies the phase-2 audited ledger (Astra R01–R25, Sol and Fable ledgers, final reconciliation), adds the existing-log analyses I ran today, and is constrained by the literature (`literature.md`).

Peer corrections accepted in `debate.md` are applied here:
- 139 is a diagnostic count;
- "non-identification, not impossibility";
- no monitorability headline.

## Tiers

- **A, existing support.** Ready now from audited records, with a stated unit and limit.
- **B, existing-log analysis.** Computable from saved artifacts with no provider calls and no new games. Each B item says whether it is done, ready to run, or needs a frozen codebook. Codebooks written after inspecting the cohort are **not preregistration**.
- **C, optional strengthening without paid model calls.** Uses the engine or scripted policies, which may create **new (unpaid) games or rollouts**. C items change no benchmark behavior but are new artifacts, so they need explicit user approval. None was run.
- **D, experiment required only if the stronger claim is kept.** Needs paid model runs and/or a model-facing treatment change. Not to be run in this stage. Each D item lists the minimal design.

The descriptive paper needs **no B, C or D item** to be coherent. B items would turn case lists into denominators. C items calibrate. D items are only for stronger claims the paper should *not* make now.

---

## 1. Outcomes and design

| # | Claim (ready wording) | Unit / denominator | Evidence | Tier | Limit and what would change it |
|---|---|---|---|---|---|
| O1 | Twenty complete, uncapped games ending by bankruptcy: 6,989 decisions and 8,679 attempts across five seed blocks × four cyclic rotations | Games, decisions, attempts | R01; `cohort_overview.json` [V today] | A | None |
| O2 | Observed wins are Sol 8, Argon 7, Opus 3, Grok 2. Seats 1 and 2 win 7 and 7; seats 3 and 4 win 3 and 3 (one-based seat k = player p_k = turn order k−1; verified for all 80 assignments). One block (G5–8) is won by Sol from all four seats; another (G9–12) is won by seat 2 under all four models | Games; block × rotation cells | `outcome_dependence.json` [V today] | A | Under i.i.d. uniform reference nulls that *ignore* block dependence: P(prespecified model ≥ 8/20) = 0.102; P(any model ≥ 8) = 0.399; P(seats 1–2 ≥ 14/20) = 0.058. The post hoc chance of ≥ 2 sweep blocks is ≈ 0.009. So: **no model ranking and no seat effect are established**. Both block dice and configured agents appear to matter, and the design cannot decompose them |
| O3 | All four agents ran at reasoning effort "medium". Known OpenRouter cost is $141.71: Opus ≥ $48.80 (1,600 refused attempts lack cost), Sol $18.72, Argon $18.59, Grok $55.60. Grok uses 4,041 completion tokens/decision against Sol's 128 | Decisions; attempts | `cohort_overview.json` from per-game `usage.json` [V today] | A | A lower bound for Opus. No compute–capability law is implied. The cost of fallback stages is included per the usage files |
| O4 | Configured-agent (model + prompt + memory + response policy + tool_choice) is the evaluated unit | — | `run_config.json` response_policy; `player_config.py:328–334` (Grok `tool_choice="required"`, others `"auto"`, at both run commits) [V today] | A | DECE §4.3/§5 shows harness effects can be large in matched studies, but its result is local. Our ranking is model- and harness-conditional |
| O5 | "Model X is stronger than model Y" | — | — | **D only** | Minimal design: ≥ 15–20 seed blocks per roster with whole-block resampling; replicate realizations per cell (provider stochasticity); a fixed harness per model, or a matched harness swap à la DECE §4.3. Not needed for the paper |
| O6 | Seat-advantage magnitude | Games | — | C or D | **C:** scripted reference policies on the same five seeds (`baselines.py`) give a model-free seat baseline under the same dice. These are new unpaid games, so approval is needed. **D:** more blocks |

## 2. Acquisition, bargaining and deployment

| # | Claim | Unit | Evidence | Tier | Limit and change |
|---|---|---|---|---|---|
| E1 | Deed transfer routes: 475 purchases, 72 auctions, 397 creditor-inherited, 207 traded. Final acquisition route of the 209 completed-group episodes: 16/9/63/121. Sixty-nine inherited completions occur at the terminal bankruptcy | Deeds; ownership episodes | Astra synthesis; Sol `corpus_economics_audit.json` | A | The final route does not describe the whole group |
| E2 | Initiation propensity and intensity: Argon 16/766 (1.12), Grok 106/676 (1.28), Opus 160/660 (1.50), Sol 83/834 (1.59) | Eligible own turns; proposals | R03 | A | Eligibility is endogenous. Opus is action-only. Grok's received-name conflicts mean some applied proposals are not deliberate preferences |
| E3 | 113 settlements complete a group for neither, one or both sides: 60/43/10 | Settlements | R04 | A | Not trade quality. FinBoardBench's LLM-judge "harmful" rate (§4.2) is a different construct |
| E4 | 43/63 trade-completed groups are built in the owner's first management turn; 34/42 when buildable at entry. **All 8 entry-buildable non-builds are accounted for:** 3 engine defaults (Opus 2, Sol 1), 3 Grok received `end_turn` calls whose content requested a build or build financing, and 2 explicit Grok chosen holds | Groups | R05; `phase3/opus/deployment_residuals.json` [V today, existing-log analysis] | A (counts); B done (residual) | Conditional applied responsiveness, not willingness. The per-model residuals are almost entirely execution or channel conditions |
| E5 | Eighteen winners trade; G14 Sol and G15 Argon win without trading. In 13 games the first winner-built group contains a traded deed | Games | R14 | A | Not a causal role of trading |
| E6 | Refusals of own completion are recorded with rival-financing reasons (G1 d294, G9 d137, G11 d258) | Decisions | Sol and Astra synthesis | A | Reasons observable; optimality not established |
| E7 | Auction behavior denominators (bids, declines, one-above-rival bids) | Auctions | `auction_threads.jsonl` per game | **B, ready to run** | Fable listed this as needs-analysis. Deterministic, no codebook needed |
| E8 | "Trading/fast deployment causes winning" | — | — | **D only** | Matched-state intervention: fork from frozen prefixes with and without an accepted trade, the same model continuing. Paid and outcome-stochastic, so many replicates are needed |

## 3. Finance, development and liquidation

| # | Claim | Unit | Evidence | Tier | Limit and change |
|---|---|---|---|---|---|
| F1 | All 61 Opus defaulted build plans execute the same purchase multiset after legal reordering | Decisions | R06 | A | A local feasible alternative, not a repaired-policy outcome |
| F2 | Uneven-build recoveries change purchases in 12/18 successful Argon and 5/25 Sol cases, and in 0/5 Grok cases | Decisions | R07 | A | Build applied, allocation preserved, same-turn target and future suffix are different outcomes |
| F3 | Sixty eliminations: three admit a legal payment route for the current debt, 56 fail even a full upper bound, one hotel lock | Eliminations | R08–R10 | A | Excludes help through trades. Not surrender or optimality. **AgentMonopoly has no liquidation step** (README), so this analysis is scope-specific |
| F4 | Valid chosen holds coexist with defaults and channel-inconsistent ENDs | Decisions | R11 | A | Reserve optimality is unknown |
| F5 | 103 spending units: $103,450 outlay; $93,000 whole-game paid developed rent; $92,550 after first own spend; 40 with zero paid developed rent, of which 26 also produce no creditor elimination | Game × player × color | R12–R13 | A | Not ROI. Contrast FinBoardBench §4.3 "Investment ROI" under classic bankruptcy (App. C.3) |
| F6 | Winners spend on 58 groups: 34 contain inherited deeds, 30 first complete by estate. The winner is creditor in 54/60 eliminations (35/40 nonterminal). 57 eliminations follow developed-color rent | Groups; eliminations | R15–R16 | A | Concentration under the declared inheritance variant, not a causal benefit |
| F7 | Bank houses reach zero in nine games. Exact states show restrictions and costly workarounds | Games; selected states | R17 | A | No count of binding shortages |
| F8 | Count of decisions where a desired build was blocked by stock | Decisions | — | **B, ready (deterministic)** | Menus plus the bank stock series. "Desired" needs a stated operationalization (e.g., cash-affordable next house blocked only by stock) |
| F9 | Stated liquidation maxima versus computed accessible bounds across all liquidation notes | Liquidation decisions with a numeric note | — | **B, codebook** | Extract numbers semantically; compare with the `bankruptcy_bounds.py` logic |
| F10 | Multi-creditor liquidation prompts understate debt (G19 d263) | Liquidation scenarios with PAY_EACH_PLAYER | — | **B, ready (deterministic)** | Filter the scenario reason and compare owed amount with the charged amount |
| F11 | "Opus would have built or won under a non-refusing condition" | — | — | **D only** | Rerun Opus under a non-refused policy from frozen prefixes, or in new games. **Model-facing change**; needs explicit authorization |
| F12 | "Inheritance decided winners" | — | — | **D or C** | **C:** scripted-policy games under classic versus variant bankruptcy rules (engine configuration). That is a benchmark-rule change, so only as a separate declared treatment. **D:** LLM games under both rules |
| F13 | "Optimal reserve or development policy" | — | — | Not planned | No optimality oracle exists for four-player Monopoly. At most, C-tier heuristic comparisons (DECE D.8 style) |

## 4. Social conduct

The norm for every row is `SYSTEM_PROMPT_V1`:
- public deception and bluffing are permitted;
- private thoughts "should reflect true reasoning";
- the engine enforces legal actions.

The prompt permitting public deception does not authorize every public/action contradiction, and certainly not private falsehood (Sol's refinement, accepted).

| # | Claim | Unit | Evidence | Tier | Limit and change |
|---|---|---|---|---|---|
| S1 | G13 d250–253: misleading financial framing with a recorded omission rationale, recipient exposure and settlement. The buyer's prior d251 motive (insurance, estate denial) is recorded | Case | R18 | A | No belief change, no $70 persuasion effect, and no instruction violation under a permissive public norm. Arena-style Stage B would check *state* claims. Ours tests the *achievability* claim ($295 reachable) by executing a legal sequence |
| S2 | Public assent with a private correction made before the claim (G4); acceptance with explicit premise correction (G6, G19); a transient echo then rejection (G11) | Cases | R19 | A | Proposition-specific. No immunity claim |
| S3 | A standing offer is invoked and withdrawn after financial changes (G18) | Case | R20 | A | No costly reliance shown, and no immutable-offer norm. Promise follow-through rates exist in Arena App. D; ours is a case |
| S4 | A private-note string appears in a public message and is recognized by the recipient (G20 d001/d004) | Case | R21 | A | No intent or exploitation shown. The source is unlocalized |
| S5 | Anti-leader appeals, blocker retention and funding refusals occur; no checked case establishes a binding coalition, cartel or deliberate kingmaking | Cases | Astra and Sol synthesis | A | An absence bounded by the checked record. Arena reports cartels in a different environment and contract |
| S6 | Received-call conflicts: G12 d249, G19 d135 and G18 d083 are checked cases where explanation channels oppose the applied action. Grok has 139 received content/tool-name conflicts, a diagnostic count | Cases; Grok decisions | R09, R23; Fable channel table | A | Grok alone ran under `tool_choice="required"`. The source is unlocalized. A cross-model rate is undefined (Sol 0 and Argon 0 content beside the tool call; Opus 91 applied private notes). **No monitorability headline** (Fable's counterexample, my concession) |
| S7 | Corpus proposition coding: public-false / private-false / belief-error | All false factual propositions in public messages and private notes | — | **B, codebook** | The highest-value B item. Use Arena's Stage B pattern (claim extraction → deterministic check against events/menus) **plus** our modal checks for achievability claims. Report it as post hoc coding. Two independent coders, or a human-adjudicated sample, would be needed before any rate is called validated |
| S8 | Leader-funding-denial reasons in trade responses | Trade responses | — | **B, codebook** | Fable and Opus phase 2 |
| S9 | Within-call note–action consistency for Sol, Argon and Grok | Decisions with an applied private note | — | **B, codebook** | The only cross-model unit for action–explanation consistency. Not available for Opus |
| S10 | Promise/assurance follow-through rate | Explicit forward assurances | — | **B, codebook** | Follow Arena App. D: extract verifiable forward commitments and check the engine-settled outcome within a fixed window. The opportunity count may be small |
| S11 | Causal persuasion ("framing caused acceptance or price") | — | — | **D only** | Randomized message ablation or rewording at frozen prefixes, with the recipient model resampled many times per arm. Same state, same menu, message varied. Paid. Outcome: accept rate and price |
| S12 | Instruction misalignment or dishonesty | — | — | **D only** | See §6: a treatment with a binding norm and monitored violation opportunities |
| S13 | Predictive monitor accuracy | — | — | **D only** | Frozen input channel, a fixed prediction rule, adjudicated held-out truth (Sol's specification) |

## 5. Measurement conditions (explain affected results)

| # | Claim | Evidence | Tier | Note |
|---|---|---|---|---|
| M1 | Opus: 1,605 refused attempts; 1,604 first-attempt recovery chains; plus the G2 d129 second-attempt refusal. Rate 0.57–0.76 in G1–4, 1.00 in G5–20. Identical ToS output-duplication string | Phase-1 inventory | A | A provider-policy × harness interaction, not a safety refusal |
| M2 | Trade-history formatter defect: 44 reversed accepts, 26 misattributed rejects, 232 self-partner counters; present in 2,054 of 6,989 initial prompts | R22 | A | Exposure, not reliance. **D only** for reliance (corrected-formatter replay, prompt change) |
| M3 | 149 nonempty utterances absent from timeline insertion | Phase-1 delivery audit | A | Report where a result depends on it |
| M4 | Generated labels err through referent, tense, arithmetic and menu reading | R25 | A | Selected corrections, not an extractor error rate |

## 6. The capability–alignment question: what each design would establish

The cohort cannot place a point on a capability–alignment curve: four configured systems, four providers, one time point, one prompt. The literature is mixed:
- Arena: null across 12 models.
- Emergent Collusion: within-family capability is associated with earlier collusion under a protocol-violation affordance.
- MASK: accuracy rises without honesty rising.

So a future design has to fix the norm and supply violation affordances. Minimal design (D):

1. **Capability axis.** At least three tiers within each of at least two provider lineages, with one harness and one response policy per lineage. Report capability by an external measure, not our win rate. That avoids the circularity Safetywashing warns about.
2. **Norm treatments (model-facing; explicit approval needed).**
   - T0: current permissive prompt.
   - T1: a public-honesty and no-contradiction norm (AgentMonopoly-style).
   - T2: T1 plus explicit commitment objects.
3. **Violation affordances (environment additions).**
   - Unenforced IOUs or deferred payments that the engine records but does not enforce.
   - An optional private bilateral channel.
   - A monitor that can audit only a declared subset of channels.

   Each affordance must have a counted opportunity, so a breach rate has a denominator.
4. **Outcomes, pre-specified before running.**
   - Breach of unenforced commitments given an opportunity.
   - Rate of false factual and achievability claims, using S7's coding.
   - Contradiction between public message and action under T1.
   - Each economic profile from §§2–3.
5. **Inference.** Whole-block resampling. At least 15–20 seed blocks per roster. Replicate realizations. Mixed-effects models with block and agent-run random effects, following Arena §4.2.

None of this is required for the descriptive paper. The outline presents it as the research agenda the environment is built to support, with implemented and unimplemented parts labelled (affordance ledger, `figure_table_plan.md` T7).

## 7. Decisions

1. **No new paid experiment** is needed for any A-tier claim. None will be run in this stage.
2. **Recommended B analyses before a manuscript**, in priority order:
   - S7 proposition coding;
   - F8 binding-shortage count;
   - E7 auction denominators;
   - F10 multi-creditor incidence;
   - S10 assurance follow-through.

   E7, F8 and F10 are deterministic and can be built from existing scripts. S7 and S10 need a codebook frozen *before* coding the remaining games. State plainly that the codebook is post hoc relative to the inspected cohort.
3. **C items** (reference-policy seat baseline; rule-variant scripted comparison) are useful calibration in the style of DECE D.8 and Cattle Trade §3.3. They create new artifacts, so the decision belongs to the user and to Astra as integrator.
4. **D items** are listed in the paper only as "would require", attached to the specific claim the paper does *not* make.
5. **Removal rule.** Any sentence that implies O5, E8, F11, F12, S11, S12, S13 or a capability trend must be deleted, or rewritten into its A-tier form.
