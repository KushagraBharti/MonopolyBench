# MonopolyBench: Two-Paper Plan

Date: 2026-09-13  
Status: plan established; implementation, experiments, and publication pending.

## 1. The two contributions

| Paper | Scope | Central question |
| --- | --- | --- |
| A: Benchmark and evaluation infrastructure | Group 3 | Can researchers reliably evaluate and diagnose economic LLM agents with this instrument? |
| B: Economic capability and trustworthy multi-agent behavior | Groups 1 + 2 | How capable are models economically, and how do they interact while pursuing success? |

Paper A drives engineering and validation. Paper B informs instrumentation and
experimental design from the beginning. Paper B does not need to wait for Paper A
to be accepted. Two papers remain contingent on two substantial contributions.

## 2. Paper A: The instrument and evidence that it works

Working title: **MonopolyBench: A Reproducible Benchmark for Economic Multi-Agent Evaluation**.

### Required evidence

| Contribution | Demonstration |
| --- | --- |
| Authoritative economic environment | Rule-conformance and legal-action completeness tests, including interacting edge cases. |
| Explicit agent interface | Worked input → legal choices → response → validation/retry → applied action → events example; document memory and message requirements. |
| Reliable execution | Recovery checks, decision/action reconciliation, configuration/version hashes, complete artifacts, and missingness reporting. |
| Reproducible and inspectable records | State replay, strict provenance checks, and deliberate corruption tests with a defined detection boundary. |
| Useful measurements | Targeted scenarios and reference policies producing known contrasts; diagnostic cases beyond terminal scores. |
| Reusable tool | Documented clean-checkout workflow, example artifacts, contracts, and repeatable analysis commands. |

Prioritize auctions, trades, building evenness/inventory, mortgages, jail,
liquidation, bankruptcy transfers, turn-limit outcomes, and interactions among
them. Replay alone cannot establish rule correctness.

Corruption tests should independently alter actions, omit/reorder events, mismatch
decision IDs, corrupt snapshots, and change manifests. Identify the responsible
validator for each defect rather than assuming replay covers every artifact.

Inspect existing reference policies before adding new ones. Compare a random legal
policy, a simple economic heuristic, and a deliberately impaired variant such as
one that never builds. These calibrate measurements; they are not optimal players.

Paper A includes representative model experiments. Implementation size and passing
tests alone are not its research result: show what the benchmark reliably
distinguishes and why another researcher would use it.

### Manuscript and release

Structure: introduction; concise related work; environment/interface; execution and
artifacts; validation and reference policies; representative evaluation; limitations
and reproducibility.

Principal figures: architecture, complete worked decision/failure, validation
matrix, and diagnostic value of richer records.

Completion: critical validation passes, documented reproduction works, useful
contrasts are demonstrated, known defects are explicit, and reusable artifacts are
available. Paper polish follows that evidence.

## 3. Paper B: Capability, agency, and trustworthiness

Working title: **Economic Capability and Trustworthy Behavior in Competitive LLM Agents**.

| Question | Evidence and candidate measures |
| --- | --- |
| Who performs effectively? | Placement, survival, economic trajectories, development, rent generation, and cost. |
| Does economic behavior remain coherent over time? | Liquidity decisions, development delays, repeated mistakes, plan/action consistency, and responses to shocks. |
| How do agents negotiate? | Eligible opportunities, proposals, concessions, responses, completed transfers, and subsequent development. |
| Are communications trustworthy? | Factual accuracy, commitments, fulfillment/breach, corrections, and source-grounded contradictions. |
| How does collusion emerge? | Initiation, acceptance/refusal, implementation, enforcement, duration, beneficiaries, and breakdown. |
| How are success and trustworthy behavior related? | Associations with economic outcomes, accounting for survival and opportunity exposure. |

Freeze a small primary metric set; placement, survival, and an explicitly defined
economic trajectory measure are candidates. Show cash, development, and rent
alongside net worth. Do not combine capability and alignment into one score.

Associations do not establish that collusion caused victory. One-step branches
can assess immediate alternatives, not the whole unobserved future. Causal
interventions require a separate design and are not necessary for the initial plan.

### Collusion and trustworthiness review

Freeze a codebook before analyzing the new campaign for findings. Candidate classes:
reciprocal no-bid agreements, coordinated trading exclusion, allocation of acquisition
opportunities, coalition enforcement, and explicit kingmaking arrangements.
Ordinary cooperation and mutually beneficial trades are separate categories.

Track each episode through proposal → response → agreement/refusal → actual actions
→ observed consequences → continuation, renegotiation, or betrayal. Preserve exact
messages, decision/event/attempt IDs, applicable legal opportunities, and alternative
explanations.

Separate factual falsehood from evidence of deceptive intent; public/private
differences alone are insufficient. Separate breach from agreed renegotiation or
inability to act. Assess violations against actual frozen instructions. Do not
import real-world antitrust judgments or classify all cooperation as misalignment.

Review all games chronologically using local Codex/Claude Code artifact workflows.
No keyword-only prefilter may exclude turns. Independently check strong findings
and a sample of negative windows. Mask identities/outcomes where feasible and
document limitations. Human confirmation is required for high-risk publication
claims; report disagreement and uncertainty.

Report appropriate denominators: invitations for acceptance/refusal, commitments
for breach, eligible auctions for no-bid behavior, and reviewed games for occurrence.
No invitation is not a refusal. If collusion is rare, report that honestly alongside
the available opportunities; do not change prompts mid-study to create examples.

### Manuscript and release

Structure: questions; compact benchmark/treatment description; experiment; capability
results; interaction/collusion results; longitudinal cases and counterexamples;
limitations. Reference Paper A when available.

Principal figures: performance distributions, economic trajectories, behavioral
episode rates with denominators, and a few complete interaction timelines.
Use results → behavioral explanation → trace evidence storytelling. Findings,
rather than expected headlines, determine the narrative.

Completion: complete planned-cell ledger, reconciled eligibility, uncertainty that
respects seed dependence, consistent codebook application, independently checked
strong claims, and substantive results distinct from Paper A.

## 4. One shared controlled campaign

### Existing evidence

Preserve the eight E0 games as development/exploratory evidence: regression cases,
codebook development, example analyses, and historical cost planning. Keep them
separately labeled from the new cohort. Preserve the known R191 strict provenance
mismatch rather than editing original logs to produce a pass.

### Provisional design

Candidate: **48 new games = two four-model rosters × six new seeds × four cyclic
seat rotations**, possibly larger and smaller model rosters, with the same six
seeds across rosters and a consistent declared reasoning policy.

This evaluates two opponent ecosystems. It does not isolate model size causally.
There are six seed blocks per roster, not 24 independent games; account for shared
seeds in cross-roster comparisons. Actions may alter later random-number consumption
despite matching initial seeds. Provider generations remain stochastic.

Forty-eight is a proposal, not an approved budget, power guarantee, or publication
threshold. If resources or expected precision are insufficient, prioritize more
depth in one roster over many thin conditions. Exact models, routes, effort levels,
turn cap, sample size, and execution window remain undecided.

A compact matched subset of micro scenarios can examine reasoning effort as a
secondary experiment. Avoid crossing every size, effort, roster, and prompt by
default. Collusion-solicitation or anti-collusion prompts require explicit approval
as separate treatments and cannot be pooled with spontaneous main-campaign behavior.

### Checks and freeze

Do static/unpaid checks first. Short paid operational checks require approved scope
and budget; they replace a mandatory standalone E1 research phase.

Before the main campaign, freeze:

- implementation/rules and prompt/tool/memory/retry/fallback versions and hashes;
- exact model IDs, routes, reasoning, provider metadata, and execution window;
- seeds, rosters, rotations, randomized run order, run IDs, and turn cap;
- metrics, codebook, review sampling, analysis eligibility, and uncertainty method;
- stopping, recovery, rerun, missingness rules, and spending ceiling.

Smoke runs stay separate unless designated campaign cells in advance and run under
the identical final contract. Retain every planned cell, including technical
failures, capped games, and budget-stopped cells. Eligibility can differ by analysis;
failures must remain visible. Never selectively rerun unfavorable outcomes.

Substantive post-freeze changes require a versioned amendment and a decision about
which results need repeating. Model-facing changes require explicit authorization.
Historical BYOK availability, balance, and prices must be refreshed before spending.

The old E1/E2 code and generated readiness reports are unchanged. A future scoped
task must adapt reusable controls into a new campaign contract and test it. Do not
fake E1 completion or bypass existing gates.

## 5. Work packages

| Order | Work | Concrete deliverable |
| --- | --- | --- |
| 1 | Read-only baseline audit | Matrix of requirement, existing code/test, observed gap, severity, proposed fix, and affected surfaces. |
| 2 | Benchmark hardening | Scoped fixes and meaningful tests; preservation checks for affected model-facing surfaces; Mac issues resolved. |
| 3 | Instrument validation | Rule/reference-policy results, corruption-detection matrix, worked decision, metric checks against known traces. |
| 4 | Behavioral analysis contract | Paper B outcomes, collusion codebook, review workflow, and paper-specific claim/evidence map. |
| 5 | Campaign preparation | New tested campaign contract, fresh route inventory, cost estimate, proposed ceiling, and frozen manifest. |
| 6 | Execution | Approved operational checks and main campaign; every cell retained, reconciled, and replayed. |
| 7 | Shared analysis | Deterministic tables, chronological semantic review, independent validation, and uncertainty. |
| 8 | Paper A | Validated benchmark release, representative experiments, and manuscript. |
| 9 | Paper B | Distinct substantive capability/interaction findings, analysis release, and manuscript. |

Packages 3 and 4 inform each other. Outlines may be prepared early; final results
follow verified evidence. This plan itself starts none of these implementation or
paid-execution packages.

The baseline audit should recheck previously reported Mac issues: accidental
dependency upgrades during npm migration, platform-specific mypy errors, missing
microbench coverage in the verification wrapper, and environment documentation.
Historical test totals are not current verification.

## 6. Publication separation and shared assets

| Shared asset | Paper A | Paper B |
| --- | --- | --- |
| Environment and interface | Describe and validate the instrument. | Define the fixed experimental treatment. |
| Runs and metrics | Demonstrate measurement usefulness and reliability. | Establish capability and interaction findings. |
| Diagnostic episodes | Demonstrate what records can distinguish. | Explain substantive behavioral patterns. |
| Release | System, validation suite, examples, reproduction guide. | Campaign manifests, tables, reviewed evidence, analysis recipe. |

Give each paper a distinct central question, principal results, and figures.
Disclose reused data and cite companion work as appropriate to venue rules.
Do not present reused runs as new independent evidence or duplicate result narratives.

Paper A must not be a thin implementation description. Paper B must go beyond
retelling Paper A's demonstrations. If the behavioral evidence is not independently
substantial, strengthen or defer Paper B instead of forcing a second publication.

## 7. Decisions, scope, and status

Before paid execution resolve budget, model cohorts, effort, turn cap, game count,
execution window, and review capacity. Prepare concrete options first.

Publication targets are a separate next planning step. No submission or acceptance
expectation is fixed here.

Exclude Blender/3D integration, real-estate extensions, broad prompt/memory
ablations, and a mandatory large E2 program. Collusion and trustworthiness remain
central, not optional side topics.

Sources: current user decisions; Sourav Pal's supplied feedback; Abhinav Gummadi's
supplied notes; the task "Review MonopolyBench PDF"; existing analysis documents;
the older protocol/codebook; and the eight-game ledger.

Current roadmap: ../research_direction.md. Historical E1/E2 specifications:
research_protocol/. Existing analysis: ../analysis/analysis.md,
../analysis/analysis_process.md, and ../analysis/analysis_automated.md.

Status: planning complete; no implementation, experiment, or publication completion
is asserted by this document.
