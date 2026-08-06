# Scientific Protocol v2: Controlled Stochastic Economic Agency

Status: pre-pilot protocol  
Protocol date: 2026-07-29  
Benchmark: `monopoly-long-v1`  
Current implementation commit at protocol drafting: `7ce810ebb71bbe102335304f43b17eaa45f43512`

## 1. Purpose and boundary

The study asks whether local economic competence survives composition across hundreds
of decisions in a persistent, adaptive, multi-agent economy. The ecological object is
the complete game trajectory. Controlled fixtures diagnose components of that
trajectory; they do not replace it.

The existing eight canonical saved games are an exploratory instrument-validation and
mechanism-discovery corpus. They may be used to:

- validate replay, extraction, metrics, and annotation instruments;
- construct pilot codebooks and nominate fixture families;
- estimate operational cost and likely event frequencies;
- illustrate named, bounded mechanisms.

They may not be used to:

- estimate confirmatory model effects;
- select favorable confirmatory seeds, endpoints, or hypotheses;
- tune a metric after observing confirmatory model contrasts;
- estimate population prevalence of strategic or social behavior.

No Monopoly rules, engine behavior, model-facing prompt text, tool schemas, memory
limits, retry wording, or fallback policy may change during this program.

## 2. Formal experimental object

Let a planned game cell be

\[
c=(b,r,s,\rho,\tau),
\]

where:

- \(b\) is an independently sampled engine seed block;
- \(r\) is the within-block repetition index;
- \(s\) is the cyclic seat permutation;
- \(\rho\) is the opponent roster/ecosystem;
- \(\tau\) is the execution-time and provider-routing record.

The realized trajectory is

\[
T_c = F(P,\rho,s;
\omega_{\mathrm{engine}},
\omega_{\mathrm{model}},
\omega_{\mathrm{interaction}},
\omega_{\mathrm{service}}),
\]

under frozen protocol \(P\). The four stochastic components denote engine chance,
unseeded provider/model generation, endogenous multiplayer feedback, and service-side
variation such as provider implementation or endpoint drift.

A fixed engine seed makes an observed engine trajectory replayable. It does not make
the model policy, strategic interaction, or cross-game study deterministic. Actions
can change later states and random-number consumption, so seat rotations sharing a
base seed are related block members, not identical dice exposures.

## 3. Research questions

### RQ1: Ecological performance

Under a frozen primary roster and declared seed distribution, how does model identity
change placement, survival, common-horizon economic trajectory, and terminal economic
state?

### RQ2: Long-horizon solvency

How do legal liquidity, development timing, rent exposure, mortgage cycles, and
liquidation choices relate to bankruptcy hazard and restricted survival time?

### RQ3: Local-to-global composition

Do repeated decisions on frozen trajectory-derived fixtures agree with the same
model's live-game actions, and does fixture-level competence explain coherent
full-game execution better than a terminal outcome alone?

### RQ4: Operational reliability and efficiency

How do first-attempt validity, retry recovery, deterministic fallback, provider usage,
latency, tokens, and cost vary across models, and how do those operational outcomes
co-occur with immediate state consequences?

### RQ5: Strategic communication

What adjudicated patterns of factual claims, promises, reversals, coalition signals,
collusion-like coordination, and public/private discrepancy occur among eligible
communication episodes?

RQ5 is secondary and behavioral. An exhaustive masked LLM judge discovers and
source-grounds candidates across every turn. Humans validate high-risk candidates and
a probability sample of judge-negative material. RQ5 becomes comparative only if
human confirmation, negative-audit, label-reliability, and precision gates pass.

## 4. Experimental layers

### Layer E0: Existing exploratory corpus

Eight completed saved games. Purpose: instrument validation, qualitative discovery,
cost estimation, and fixture nomination only.

### Layer E1: Calibration pilot

Two to three independent seed blocks, each expanded to all four cyclic seat rotations
under the candidate primary roster. Eight to twelve games total.

The E1 pilot is used to estimate nuisance quantities without presenting confirmatory
model contrasts:

- seat and model-by-seed dispersion;
- placement and bankruptcy event frequencies;
- common-horizon AUC variance;
- game duration and completion rates;
- retry/fallback and replay-failure rates;
- provider cost, token, and latency distributions;
- fixture extraction yield;
- communication-episode yield, judge-window coverage, and expected human-review load.

### Layer E2: Confirmatory ecological campaign

The final number of independent seed blocks is selected by the blinded E1
power/precision simulation. Every seed block contains four cyclic seat rotations. All
planned cells are run and retained.

The primary roster is fixed before the seed draw. Execution order is randomized and
frozen before the first call. All cells use the same engine, prompt, tool, memory,
retry, fallback, reasoning-effort, endpoint, and provider-routing contract.

### Layer R1: Stable-baseline calibration

Each primary model occupies one LLM seat against the same three deterministic
opponents. Seats are balanced across a smaller preregistered seed sample. This
estimates performance against a stable opponent field and separates basic engine
competence from behavior in an adaptive all-LLM ecosystem.

### Layer R2: Opponent-ecosystem robustness

A smaller alternate-roster or self-play design estimates opponent dependence. Results
are never pooled into the primary estimand. They are reported as transport or
interaction effects.

### Layer R3: Stress-distribution robustness

Preregistered seed strata cover ordinary, volatile, auction-heavy, trade-heavy, and
liquidation-heavy surfaces. These strata estimate conditional stress performance, not
natural-world prevalence. A stress seed can belong to a robustness ring but cannot be
silently substituted into the primary random seed distribution.

### Layer R4: Temporal/service robustness

A preregistered sentinel subset is repeated near the beginning, middle, and end of the
execution window. This estimates service-time instability. It does not make a mutable
endpoint an immutable model version.

### Layer D1: Existing controlled micro suite

The frozen 130-scenario suite measures isolated economic decisions under the existing
`live_game` prompt condition. Repetitions and model order are frozen in a manifest.

### Layer D2: Trajectory-derived exact-history fixtures

Consequential decisions are sampled from held-out E1/E2 games under a frozen selection
rule. The fixture retains the exact source decision, legal menu, bounded historical
memory, system/user/tool bytes, model configuration, and provenance hashes.

### Layer D3: One-step legal branches

Every legal action in selected fixtures is applied once after replaying the source
action prefix. Immediate state and event deltas are exact. No one-step result is
described as the value of the rest of the game.

Multi-step counterfactual rollouts are outside the confirmatory protocol until a
separate continuation and random-coupling contract is implemented and validated.

## 5. Units and dependence

- Primary design unit: seed block.
- Game unit: one seed/repetition/seat/roster cell.
- Player-game unit: one model trajectory in one game.
- Episode unit: one auction, trade, liquidation sequence, bankruptcy window, or
  communication lifecycle.
- Decision unit: one engine-issued legal decision.
- Attempt unit: one provider call for a decision.

Games, turns, decisions, attempts, offers, bids, and messages within the same seed
block are dependent. They are never counted as independent replicates. Bootstrap,
uncertainty, and mixed effects cluster at seed-block level unless a more conservative
level is declared.

## 6. Primary estimands

### 6.1 Roster-relative placement

For model \(m\), frozen protocol \(P\), primary roster \(\rho_0\), and declared seed
distribution \(D_0\):

\[
\theta_m^{\mathrm{place}}(P,\rho_0,D_0)
=
\Pr(m \text{ ranks ahead of its opponents}).
\]

The primary placement model is hierarchical Plackett--Luce with model-by-seed random
effects and fixed seat effects. Full placement order is used; win rate alone is not.

### 6.2 Restricted survival

\[
\theta_m^{\mathrm{surv}}(H)
=
\mathbb E[\min(T_m,H)],
\]

where \(T_m\) is bankruptcy time and \(H\) is the preregistered turn horizon. Capped
active players are right-censored rather than treated as winners or non-events.

### 6.3 Common-horizon economic trajectory

Net-worth AUC is normalized over a preregistered common horizon \(H_c\):

\[
\mathrm{AUC}_{m,g}^{(H_c)}
=
\frac{1}{H_c}\sum_{t=1}^{H_c} W_{m,g,t}.
\]

The horizon is chosen from blinded pilot duration distributions, not from observed
confirmatory model separation.

### 6.4 Primary family

The primary comparison family contains:

1. full placement order;
2. restricted survival at \(H\);
3. common-horizon net-worth AUC.

All other economic, behavioral, reliability, and cost outcomes are secondary or
diagnostic. Family-wise multiplicity is controlled using the preregistered procedure;
effect sizes and uncertainty are reported regardless of significance.

## 7. Secondary estimands

- bankruptcy hazard with time-varying legal liquidity, cash, rent exposure, and
  opponent rent power;
- terminal net worth and rank;
- legal-liquidity reserve and liquidation capacity;
- rent paid/received and property-development timing;
- monopoly completion and conversion;
- trade funnel, acceptance, exchange depth, and third-party externality;
- auction eligibility, participation, overbid, dropout, and acquisition;
- first-attempt validity, retry recovery, fallback, and technical-failure rates;
- token, cost, latency, and quality-efficiency frontiers;
- exhaustive judge-candidate counts and human-validated communication-label rates
  with explicit eligible denominators and judge-negative audit results.

Realized downstream outcomes are descriptive consequences. Regret, avoidability,
trade surplus, winner's curse, or causal action value requires the D3 branch contract
or a separately validated continuation oracle.

## 8. Confirmatory hypotheses

The hypotheses are model-agnostic. No model is preregistered as the expected winner.

- **H1 (placement):** model identity changes full placement likelihood under the
  primary roster after accounting for seat and model-by-seed variation.
- **H2 (survival):** model identity changes restricted survival under the primary
  roster.
- **H3 (trajectory):** model identity changes common-horizon net-worth AUC.
- **H4 (cross-scale concordance):** a model's repeated exact-history fixture action
  distribution is more concentrated on its original live action than a declared
  random-legal reference.
- **H5 (local-to-global association):** fixture-level branch competence is associated
  with preregistered full-game mechanism outcomes after seed-block clustering.

H4 and H5 become confirmatory only if the D2 extraction proof and D3 one-step branch
validation pass before E2. Otherwise they remain registered exploratory analyses.

Robustness and communication hypotheses are secondary:

- model effects interact with opponent ecosystem;
- model effects vary across stress strata;
- service-time sentinel repetitions reveal nonzero temporal instability;
- communication-label rates vary across models among eligible episodes.

## 9. Randomness policy

### 9.1 Engine seeds

Primary seeds are generated after protocol freeze using an auditable seed-draw
procedure. The draw script, entropy commitment, candidate universe, selected seeds,
and SHA-256 manifest are committed before execution. Seeds from E0 or hand-labeled
research cohorts are ineligible for the primary draw.

### 9.2 Seat assignment

Each primary seed is expanded to all four cyclic seat rotations. The base actor order
is itself randomized once per seed block before cyclic expansion. Seat order is
research configuration only and never enters prompts.

### 9.3 Model generation

Model generations are not assumed seedable. Provider-default stochastic generation is
part of the treatment because the current production request does not set temperature
or `top_p`. This is disclosed, preserved, and measured through repeated cells and
fixtures rather than described as deterministic.

### 9.4 Execution order

Every planned game cell receives a unique randomized execution rank in a frozen
manifest. Execution order is independent of model, seat, seed stratum, and expected
difficulty. Sentinel repetitions are inserted by preregistered rule.

### 9.5 Provider/service variation

Provider routing is pinned when the provider supports it. The endpoint identifier,
provider constraint, request timestamp, returned model/provider metadata, request ID,
usage semantics, and pricing snapshot are retained. Mutable endpoint implementations
are treated as time-indexed services, not timeless model versions.

### 9.6 Failed calls

Configured corrective retry and deterministic fallback remain part of the benchmark
treatment. They are never rerun manually to obtain a more favorable action.

## 10. Inclusion and exclusion

### 10.1 Planned-cell inclusion

Every preregistered cell appears in the campaign ledger with one of:

- completed;
- capped;
- provider failure;
- infrastructure failure;
- integrity failure;
- not started because a preregistered safety/budget stop fired.

No cell is removed because of winner, duration, ending type, unusual behavior,
unfavorable model performance, cost, or qualitative content.

### 10.2 Strategic-analysis eligibility

A completed or capped cell is eligible for state-based strategic analysis when:

- source config, players, seed, seat, endpoint, provider, prompt, and route metadata
  are present;
- decision/action reconciliation passes;
- engine state replay passes;
- required state/action/event artifacts are complete.

`state_passed_artifact_failed` cells remain eligible only for claims proven unaffected
by the bounded artifact defect. The defect and affected surfaces must be named.

### 10.3 Reliability-analysis eligibility

All attempted cells, including provider, retry, fallback, partial, and integrity
failures, are eligible for operational reliability analysis. Missingness is an
outcome, not an invisible exclusion.

### 10.4 Block completeness

The primary placement analysis uses complete four-rotation seed blocks. If a rotation
fails technically:

- the failed cell remains in the ledger and reliability analysis;
- the incomplete block is excluded from the complete-block placement likelihood;
- a preregistered attempted-cell sensitivity analysis is also reported;
- the cell is not selectively rerun unless the general rerun rule was triggered.

### 10.5 Permitted exclusions

Only the following may exclude a cell from the relevant strategic analysis:

- duplicate run ID or duplicate planned cell;
- corrupted/unreadable canonical action history;
- decision/action mismatch that prevents legal replay;
- state replay failure;
- unplanned prompt, engine, schema, endpoint, provider, route, or model change;
- secret or personally identifying data contamination;
- a preregistered global safety stop.

All exclusions require an immutable reason code and evidence path.

## 11. Generalization contract

The study uses bounded, explicit notions of generalization.

### Supported by E2

- Across seats: because every model occupies all four seats within each block.
- Across the primary seed distribution: because independent seeds are sampled from
  the declared distribution.
- Across stochastic generations within the execution window: to the degree measured
  by repetitions and sentinel cells.
- Under the exact primary opponent roster and frozen protocol.

### Requires robustness rings

- Across opponent rosters or self-play fields: R2 only.
- Across ordinary versus stress seed distributions: R3 only.
- Across provider implementations, routes, or calendar windows: R4 only.
- Across memory or context conditions: D2-specific registered comparisons only.

### Not claimed

- General superiority across all games, economic environments, or real markets.
- Stable properties of a model family after endpoint updates.
- Human economic competence.
- General deception, collusion, or alignment prevalence outside eligible Monopoly
  communication episodes.
- Causal long-run value from one realized continuation.

## 12. Communication study

The social study follows `social_evidence_codebook.md` and
`llm_judge_social_evidence_protocol.md`.

- Judge work runs as local, tool-assisted Codex/Claude Code research tasks over saved
  artifacts. It makes no OpenRouter or other external model API call.
- The primary judge reads every game chronologically in contiguous focal blocks of at
  most three turns. No lexical prefilter may remove a turn.
- Separate full-game specialist passes search for factual error, misleading omission,
  deception, promises and reversals, collusion-like coordination, auction suppression,
  kingmaking, public/private discrepancy, coercion, retaliation, dependency,
  gatekeeping, power seeking, correction, honesty, and counterexamples.
- Every candidate is expanded through its complete lifecycle and challenged in an
  independent judge context.
- Every focal window receives either a source-grounded candidate or an explicit
  machine-negative record.
- Model identity, provider, and final outcome are masked during the primary judge and
  human-verification passes.
- Humans validate compact candidate packets rather than discovering candidates by
  rereading every game. All high-risk publication candidates receive independent
  verification and adjudication.
- A preregistered probability sample of judge-negative windows is human-audited so
  false negatives are measurable.
- Judge candidates remain machine-generated evidence until human confirmation.
- Raw agreement, confirmation precision, negative-audit miss rate, Krippendorff's
  alpha, and Gwet's AC1 are reported where identified.

Human verification is not an E1/E2 execution gate. Failure of the social publication
gate downgrades the affected social claim; it does not invalidate the ecological
campaign or its economic results.

## 13. Pilot-to-final sample-size gate

E1 is not a miniature confirmatory study. Model labels and contrasts remain blinded
for nuisance estimation where practicable.

The following rules are fixed before E1:

- Let \(Q_{25}\) and \(Q_{75}\) be the 25th and 75th percentiles of terminal turn
  indices among integrity-eligible E1 games, computed without model labels.
- The common economic-trajectory horizon is
  \(H_c=\max(20,\min(200,10\lfloor Q_{25}/10\rfloor))\).
- The restricted-survival horizon is
  \(H=\max(H_c,\min(300,10\lfloor Q_{75}/10\rfloor))\).
- A normally completed game ending before a chosen horizon is extended as an
  absorbing terminal state. A technically interrupted game is not silently extended.
- Horizon selection fails rather than adapting if fewer than six of the eight
  planned E1 cells are integrity-eligible.
- The smallest effects of scientific interest are a 0.15 change in pairwise
  placement probability, \(\max(20,0.10H)\) turns of restricted survival, and
  \(\$300\) in common-horizon mean net-worth AUC. These are design targets, not
  thresholds for whether a result is interesting.
- Precision targets are 95% interval half-widths no larger than 0.10 for pairwise
  placement probability, 15 turns for restricted survival, and \(\$200\) for
  common-horizon mean net-worth AUC.
- Candidate confirmatory block counts are \(20,25,30,36,40,48,60\). A larger or
  differently structured design requires an explicit protocol amendment before E2.

Power calibration uses the complete four-rotation seed block as the independent
resampling unit. It controls the joint family containing all registered model
contrasts for placement, restricted survival, and common-horizon AUC. Null
calibration, interval coverage, and power are simulated under low, central, and high
model-by-seed variance, seat-effect, technical-attrition, and provider-drift
scenarios. The nuisance estimator removes model means before estimating dispersion;
the design must not be selected from observed pilot winners.

The final block count \(B\) is the smallest simulated design that simultaneously:

- achieves at least 0.90 power for the smallest meaningful primary placement effect
  under the preregistered low/central/high variance scenarios;
- achieves the target 95% interval width for restricted survival and common-horizon
  AUC;
- retains the target after the observed integrity/technical attrition rate;
- fits the approved OpenRouter cost and execution-time envelope;
- contains enough expected bankruptcy events for the planned survival model.

If no affordable design meets these criteria, the study changes its claim before E2:
it becomes an estimation study with precision targets, not an underpowered hypothesis
test.

The final design also locks:

- stochastic repeats per seed-seat cell;
- R1/R2/R3 robustness game counts;
- D1/D2 fixture counts and repetitions;
- judge-call coverage, expected candidate volume, human verification overlap, and
  judge-negative audit sample sizes.

## 14. Stop and rerun rules

Before E2, the preregistration specifies:

- maximum approved actual spend and token use;
- maximum consecutive provider failures;
- endpoint/provider mismatch threshold;
- systemic replay-failure threshold;
- prompt/tool hash mismatch threshold;
- acceptable missing-usage threshold;
- maximum execution-window duration.

A stopped campaign is retained exactly as stopped. Resumption uses the frozen manifest.
Individual strategic outcomes are never selectively rerun. A cell may be retried only
under a general technical-rerun rule that is applied without observing its model
outcome and retains both attempts.

## 15. Freeze and audit requirements

Before the first E2 provider call:

1. Commit the protocol and analysis code.
2. Commit the seed draw and randomized execution manifest.
3. Commit roster, endpoint, provider, reasoning, and date-window definitions.
4. Commit primary/secondary estimands and comparison families.
5. Commit integrity, inclusion, exclusion, stop, and rerun rules.
6. Commit D1/D2/D3 fixture and branch contracts.
7. Commit the social codebook, exhaustive judge protocol, Codex/Claude Code task
   profile, checkpoint/restart contract, output schemas, masking, negative-audit
   sampling rule, and instrument-development packet.
8. Hash every input and record the source commit.
9. Run contract, prompt-preservation, engine, replay, campaign, and analysis tests.
10. Produce a signed preregistration manifest containing all hashes.

After execution, raw run directories are frozen. Analysis is downstream and generates
new artifacts; it never rewrites canonical runs.

## 16. Required final campaign evidence

Completion of this protocol requires:

- a row for every planned cell;
- complete seed/seat/repetition/execution-order coverage;
- endpoint/provider/timestamp records;
- calls, retries, fallbacks, usage, cost, and missingness reconciliation;
- decision/action bijection;
- state and artifact replay reports;
- source and generated-output hashes;
- pilot-based power and budget report;
- diagnostic fixture repetition results;
- one-step branch results where registered;
- complete judge coverage and human-validation evidence for every
  publication-facing social claim;
- machine-readable manifests and a requirement-by-requirement audit.

Manuscript writing begins only after these evidence gates close.
