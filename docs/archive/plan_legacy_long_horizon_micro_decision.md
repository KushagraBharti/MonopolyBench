# Goal Prompt: Complete The Long-Horizon And Micro-Decision Research Tracks

Use this file as the exact goal prompt:

```text
/goal plan.md
Complete this plan fully. Do not stop until the Long-Horizon Economic Agency in
Monopoly track and the Targeted Scenario Suite / Micro-Decisions track are implemented,
tested, documented, and usable for real research runs, or until a concrete external
blocker is recorded with exact remaining work.

VERY IMPORTANT: absolutely preserve the prompt pipeline. Do not change how prompts are
built, sent, formatted, worded, tooled, retried, logged as model-facing content, or
exposed to the LLM in any way. Existing full-game and micro-v1 model-facing payloads
must remain byte-for-byte unchanged unless the user explicitly approves a prompt-facing
change.
```

The previous common-infrastructure goal prompt has been archived at:

`archives/plan_common_benchmark_infrastructure_2026-06-02.md`

This new plan is focused on the two research directions that are closest to publishable:

1. Long-Horizon Economic Agency In Monopoly.
2. Targeted Scenario Suite: Micro-Decisions, Biases, Safety Probes.

It takes its scope directly from `research_direction.md`, but turns that roadmap into
implementation criteria for a goal-mode coding agent.

## Absolute Non-Negotiable: No Prompt Changes

This is the strictest rule in this plan.

Do not change prompt content, prompt formatting, prompt condition behavior, tool prompt
construction, retry prompt wording, system prompts, user prompt payloads, message
ordering, message roles, message keys, serialized prompt JSON, OpenRouter tool schemas,
tool choice behavior, retry behavior, prompt memory behavior, private thought
requirements, public message requirements, or anything else that changes what the LLM
sees.

This applies to:

- full-game prompts,
- microbench prompts,
- retry prompts,
- OpenRouter tool schemas,
- prompt artifacts that represent model-facing content,
- public/private message requirements,
- prompt memory behavior,
- and any future prompt-condition or guardrail idea.

The goal agent must treat the current prompt pipeline as hand-curated and
benchmark-critical. Any accidental prompt diff is a regression.

Allowed work:

- post-hoc artifacts,
- analysis files,
- scorecards,
- model cards,
- run/batch configs,
- deterministic baselines that select legal actions without LLM prompts,
- human review and label tooling,
- research-only scenario metadata,
- new scenario fixtures for new benchmark suites, if they use the existing prompt path.

Forbidden work:

- altering existing full-game prompt construction,
- altering existing micro-v1 `decision_point` payloads,
- adding prompt-condition variants,
- adding prompt ablations,
- adding guardrail condition frameworks,
- adding model-facing heuristic summaries,
- injecting baseline or heuristic advice into LLM prompts,
- changing retry wording,
- changing OpenRouter tool schemas except when a contract-approved engine action itself
  changes, which is out of scope for this plan.

New micro scenarios may necessarily contain new model-facing game states because they
are new test cases. That is allowed only if the prompt builder, message structure,
tool schema generation, retry behavior, and existing micro-v1 scenario payloads remain
unchanged.

Required prompt-preservation tests:

- Existing full-game prompt fixtures, where reproducible, must remain byte-for-byte
  identical in model-facing messages and tools.
- Existing `micro-v1` prompt bundles under `live_game` must remain byte-for-byte
  identical in system prompt, user payload/content, messages, and tools.
- If any implementation path appears to require changing prompts, stop that part,
  document the blocker in `implementation_status.md`, and ask the user for explicit
  approval. Do not make the prompt change.

## Scope

The goal is to complete the missing work around:

- fixed seed sets,
- model rosters,
- repeated full-game batches,
- baseline comparisons,
- statistical reporting,
- paper-quality long-horizon analysis,
- explicit bias micro suites,
- safety/deception micro suites,
- counterfactual micro pairs,
- multi-turn targeted campaigns,
- human expert label infrastructure,
- and cleaner category-level micro reports.

This plan intentionally does not implement:

- Real Estate / Asset Management Benchmark,
- Control, Orchestration, And Information Design,
- prompt-condition framework,
- guardrail-condition framework,
- orchestrator experiments,
- direct vendor APIs outside OpenRouter,
- local tokenizer-based accounting,
- or model-facing heuristic value helpers.

## Goal-Mode Operating Contract

At the start of the goal:

1. Read `AGENTS.md`.
2. Read this `plan.md`.
3. Read `research_direction.md`, especially:
   - Common Benchmark Foundations,
   - Research Direction 1,
   - Research Direction 3,
   - Recommended Build Order.
4. Read `implementation_status.md` to understand what the prior goal already
   completed.
5. Inspect the current implementation before editing:
   - `python/packages/engine/src/monopoly_engine/`
   - `python/packages/arena/src/monopoly_arena/`
   - `python/packages/microbench/src/monopoly_microbench/`
   - `python/packages/telemetry/src/monopoly_telemetry/`
   - `python/apps/api/src/monopoly_api/`
   - `frontend/src/`
   - `contracts/schemas/`
   - `contracts/ts/`
   - `contracts/micro/`
   - `batches/`
   - `docs/`
6. Update `implementation_status.md` with a new section for this goal and keep it
   current after every major phase.

During the goal:

- Keep the repo runnable.
- Preserve engine authority, determinism, UI render-only behavior, legal-actions-only
  LLM control, OpenRouter-only gateway behavior, and event-sourced mutation logging.
- Prefer versioned JSON schemas, examples, typed clients, tests, and deterministic
  artifacts over ad hoc files.
- After every major phase, run relevant tests before continuing.
- Do not stop after creating docs, schemas, or empty placeholders. Each feature must
  be executable and verified.

The goal is complete only when:

- `monopoly-long-v1` can be configured and run as a repeated full-game research
  campaign with fixed seeds, model rosters, deterministic baselines, repeated batches,
  statistical reports, and paper-ready artifacts.
- The targeted micro suite family includes explicit bias, safety/deception,
  counterfactual, and campaign tracks with executable runners, scoring, reporting, and
  review/label workflows.
- Existing prompt-facing behavior remains unchanged and is tested.
- The documentation explains how to run, inspect, and interpret both tracks.
- Final verification passes.

## Research Track 1: Long-Horizon Economic Agency In Monopoly

### Objective

Turn the existing full-game MonopolyBench harness into a publishable benchmark track
called `monopoly-long-v1`.

The benchmark should answer whether LLM agents can play a complete game of Monopoly
as coherent long-horizon economic actors under strict legal-action constraints.

### What This Track Tests

The track must measure:

- full-game win/rank/net-worth performance,
- long-horizon strategy coherence,
- capital allocation,
- liquidity/risk management,
- auction behavior,
- trade behavior,
- build/mortgage/liquidation sequencing,
- jail timing,
- bankruptcy avoidance,
- validity/retry/fallback reliability,
- cost and token efficiency,
- variance across seeds and seats,
- and failure modes over time.

### Hypothesis

Stronger models should perform better on obvious tactical decisions, but full-game
results will remain noisy and failure will often come from long-horizon drift,
capital-allocation mistakes, overbidding, bad trades, poor cash buffers, and failure to
convert monopolies into development.

The benchmark should make that visible with trajectories, not just final winner.

### Required Implementation

#### 1. Fixed Seed Sets

Implement a versioned seed registry for `monopoly-long-v1`.

Required seed cohorts:

- `smoke`: tiny local verification cohort.
- `easy`: low-chaos games useful for sanity checks.
- `normal`: default benchmark distribution.
- `volatile`: high swing / bankruptcy-prone games.
- `auction_heavy`: seeds likely to exercise auctions.
- `trade_heavy`: seeds likely to create trade opportunities.
- `liquidation_heavy`: seeds likely to exercise mortgages, debt, and bankruptcy.
- `publication`: frozen paper-facing cohort composed from the above.

Required artifacts/configs:

- seed registry JSON,
- seed registry schema,
- seed manifest emitted into every batch,
- cohort metadata explaining why each cohort exists,
- deterministic generation script or documented manual seed list,
- tests proving registry stability and duplicate detection.

Do not silently change published seed lists. If a seed list changes, version it.

#### 2. Model Roster

Implement a versioned model roster system.

Required roster features:

- model id,
- display name,
- provider route through OpenRouter when known,
- reasoning settings if configured,
- provider-default sampling settings and top-p settings if configured by existing code,
- enabled/disabled flag,
- cost-budget group,
- notes,
- benchmark date metadata,
- and OpenRouter pricing snapshot reference.

Required rosters:

- `smoke`: cheap/local sanity roster.
- `frontier`: current serious comparison roster.
- `cost_controlled`: lower-cost roster for repeated runs.
- `baseline_mix`: includes LLMs plus deterministic baselines.

Do not hard-code secrets. Do not add direct vendor clients.

#### 3. Repeated Batch Campaigns

Extend or add batch configuration helpers so a researcher can run `monopoly-long-v1`
without manually composing every run.

Required capabilities:

- select seed cohort,
- select model roster,
- select seat permutation mode,
- select repetitions per seed,
- select budget,
- select max turns,
- select baseline mix,
- dry-run planned matrix before spending money,
- resume interrupted campaigns,
- avoid rerunning completed identical runs,
- record campaign id,
- record all seed/model/seat/repetition cells,
- and write a campaign manifest.

Required defaults:

- `latin_square` seat permutation by default,
- concurrency `1` by default,
- budget policy `stop_immediately`,
- replay after every completed run,
- trace/failure/scorecard/model-card generation enabled,
- dry-run mode available.

#### 4. Baseline Comparisons

Implement deterministic baseline actors and comparison reporting.

Baselines must select from engine-provided legal actions only. They must not receive or
modify LLM prompts. They must produce artifacts compatible with LLM runs; prompt
artifacts may be empty or replaced by baseline decision-rationale artifacts clearly
marked as non-LLM.

Minimum full-game baselines:

- random legal bot,
- always-buy bot,
- cash-conservative bot,
- no-trade bot,
- builder bot,
- auction-aggressive bot if feasible within current action coverage.

Required comparison modes:

- one LLM vs three random bots,
- one LLM vs three heuristic bots,
- one LLM vs mixed heuristic field,
- all-LLM arena,
- model roster plus deterministic baseline field.

Required outputs:

- model vs baseline win/rank/net-worth table,
- baseline-normalized score,
- whether the model beats simple fixed strategies,
- baseline failure-mode comparison,
- cost-adjusted comparison for LLMs only.

#### 5. Statistical Reporting

Implement campaign-level statistics that are robust enough for research interpretation.

Required statistics:

- mean, median, min, max, standard deviation,
- bootstrap confidence intervals,
- seat-adjusted aggregates,
- seed-adjusted aggregates,
- repetition-aware aggregates,
- per-seat performance,
- per-seed-cohort performance,
- win rate with uncertainty,
- average rank with uncertainty,
- final net worth with uncertainty,
- cost/token/latency summaries,
- retry/fallback/invalid summaries,
- failure-mode frequencies,
- trace-finding frequencies,
- model-vs-baseline deltas,
- and variance / stability leaderboard.

If statistical tests are added, prefer simple, transparent methods and document them.

#### 6. Paper-Quality Analysis Artifacts

Generate paper-ready outputs from a campaign.

Required output formats:

- JSON for machines,
- JSONL where row-wise analysis is useful,
- CSV for tables,
- Markdown report for humans,
- optional static chart data files if chart rendering is not implemented.

Required report sections:

- benchmark version and config,
- model roster,
- seed cohort and seat policy,
- run count and completion status,
- leaderboard,
- cost-adjusted leaderboard,
- variance leaderboard,
- baseline comparison table,
- tactical error table,
- failure taxonomy table,
- replay verification appendix,
- representative winning trace,
- representative losing trace,
- decisive-turn examples,
- limitations and caveats.

The report does not need to write the final paper, but it should be good enough to
start one.

#### 7. UI/API Support

Add or improve UI/API support only where needed to inspect the new artifacts.

The UI remains render-only. It may display campaign manifests, stats, reports,
leaderboards, baselines, and trace examples. It must not implement game rules or infer
legal actions.

Required views or existing-view upgrades:

- campaign/batch list,
- campaign detail,
- long-horizon leaderboard,
- baseline comparison table,
- model detail across campaigns,
- representative trace links into replay/review UI,
- artifact download/open links.

## Research Track 2: Targeted Scenario Suite / Micro-Decisions

### Objective

Expand the existing 130-scenario `micro-v1` suite into a publishable targeted
evaluation family covering tactical decisions, behavioral biases, safety/deception
probes, counterfactual pairs, and multi-turn campaigns.

### What This Track Tests

The track must measure:

- tactical Monopoly competence,
- scenario-specific strategic reasoning,
- cash-buffer discipline,
- property and auction valuation,
- trade quality,
- build/mortgage/liquidation judgment,
- jail timing,
- bias sensitivity,
- safety/honesty behavior,
- counterfactual stability,
- multi-turn execution,
- invalid/retry/fallback reliability,
- latency/cost,
- and representative failures.

### Hypothesis

Models will show category-specific strengths. Some models will be tactically good but
socially unsafe. Some will avoid unethical behavior while losing negotiation value.
Bias probes will reveal framing sensitivity, and campaign probes will reveal mistakes
that one-shot scenarios cannot detect.

### Required Implementation

#### 1. Preserve `micro-v1`

Treat the existing 130 `micro-v1` scenarios as frozen.

Required:

- do not change existing `decision_point` payloads,
- do not change existing prompt construction,
- do not change existing scenario prompt output under `live_game`,
- keep current research-only metadata valid,
- add tests that fail on accidental prompt-facing changes.

#### 2. Explicit Bias Suites

Create an explicit bias suite, preferably `bias-v1`.

Required bias categories:

- fame bias,
- anchoring,
- sunk cost,
- endowment effect,
- loss aversion,
- overconfidence,
- myopic cash preference,
- recency/availability bias,
- fairness bias,
- coalition or anti-leader bias.

Each bias category must have:

- multiple scenarios,
- clear target behavior,
- trap action(s),
- preferred or acceptable action(s),
- scoring rubric,
- research-only metadata,
- source claim or rationale,
- and at least one counterfactual relationship where appropriate.

Do not implement bias by changing prompts. Bias should come from scenario state,
available legal actions, and research-only scoring metadata.

#### 3. Safety / Deception Suites

Create an explicit safety/deception suite, preferably `safety-v1`.

Required safety categories:

- collusion proposal,
- collusion response,
- false trade claim,
- false board-state claim,
- fake promise,
- exploit confused opponent,
- kingmaking pressure,
- revenge/spite play,
- deceptive public/private mismatch,
- confrontation after misconduct.

Subjective behavioral labels must remain human-reviewed only. Automatic code may create
candidate flags or review tasks, but it must not finalize deception/collusion/kingmaking
labels without human review.

Required artifacts:

- safety scenario files,
- safety rubric metadata,
- human-review-required flags,
- review queue entries for subjective cases,
- category reports separating deterministic scoring from human-reviewed labels.

#### 4. Counterfactual Pairs

Implement counterfactual pair support as a first-class microbench concept.

Required examples:

- same expected value, famous vs non-famous property framing,
- same trade economics, cash framed as loss vs gain,
- same auction value, high current bid anchor vs low current bid anchor,
- same debt state, recent rent shock vs no recent shock,
- same monopoly opportunity, opponent framed as leader vs neutral.

Required implementation:

- pair id,
- baseline/contrast role,
- controlled-difference metadata,
- pair-level scoring,
- pair-level stability metric,
- pair-level report,
- validation that paired scenarios are connected and complete.

Counterfactual reports should answer whether the model changed behavior when only the
intended framing/control variable changed.

#### 5. Multi-Turn Campaigns

Implement targeted multi-turn campaign support, preferably `campaign-v1`.

Campaign examples:

- complete orange monopoly over three turns,
- survive rent debt with liquidation choices,
- auction war followed by cash-buffer test,
- propose trade then respond to counteroffer,
- build during house shortage,
- stay in jail through dangerous board section,
- recover after opponent builds hotels,
- avoid kingmaking while losing,
- respond to a collusion attempt over multiple messages.

Each campaign must have:

- campaign id,
- schema version,
- initial state or first DecisionPoint,
- sequence of steps,
- deterministic opponent actions or fixtures,
- expected strategic path,
- per-step rubrics,
- final campaign-state scoring,
- replayable artifacts,
- and category-level reports.

Do not create a campaign runner that bypasses the engine's legality model. If the
engine cannot support a desired transition, either use frozen DecisionPoint fixtures
with explicit metadata or record the missing engine support as a blocker.

#### 6. Human Expert Labels

Implement the workflow for human expert labels without fabricating labels.

Required:

- expert label schema,
- label task queue,
- reviewer id,
- expertise level,
- label source,
- timestamp,
- scenario id / campaign id,
- selected action or judgment,
- rationale,
- confidence,
- ambiguity flag,
- adjudication status,
- inter-rater fields,
- import/export CLI or API,
- UI support for entering labels,
- reports that separate expert labels from heuristic labels and model outputs.

If no real human expert labels are supplied, do not invent them. Complete the label
infrastructure, generate the task queues, provide examples marked as examples only,
and record "external human labeling required" as a blocker for the actual label
collection step in `implementation_status.md`.

#### 7. Cleaner Category-Level Reports

Micro reports must become research-facing, not just run logs.

Required report dimensions:

- suite id,
- category,
- subcategory,
- target capability,
- target behavior,
- difficulty,
- bias type,
- safety type,
- counterfactual pair,
- campaign,
- model,
- invalid/retry/fallback rate,
- latency,
- cost,
- score,
- deterministic rubric result,
- human-review status,
- representative failures.

Required outputs:

- `micro_report.json`,
- `micro_report.csv`,
- `category_breakdown.json`,
- `category_breakdown.csv`,
- `counterfactual_report.json`,
- `safety_report.json`,
- `campaign_report.json`,
- Markdown summary suitable for a paper appendix.

The frontend should make these reports easy to inspect without adding rule logic.

## Shared Implementation Requirements

### Contracts And Schemas

When adding artifact shapes, update:

- JSON schemas,
- TypeScript contracts,
- examples,
- producer code,
- API readers,
- frontend consumers,
- and tests.

Version every stable benchmark artifact. Do not silently change existing published
schema meanings.

### Artifact Layout

Use deterministic artifact directories.

Recommended full-game campaign layout:

- `runs/campaigns/<campaign_id>/campaign_config.json`
- `runs/campaigns/<campaign_id>/campaign_manifest.json`
- `runs/campaigns/<campaign_id>/seed_manifest.json`
- `runs/campaigns/<campaign_id>/model_roster.json`
- `runs/campaigns/<campaign_id>/baseline_roster.json`
- `runs/campaigns/<campaign_id>/run_matrix.jsonl`
- `runs/campaigns/<campaign_id>/results.jsonl`
- `runs/campaigns/<campaign_id>/leaderboard.json`
- `runs/campaigns/<campaign_id>/statistics.json`
- `runs/campaigns/<campaign_id>/baseline_comparison.json`
- `runs/campaigns/<campaign_id>/paper_report.md`
- `runs/campaigns/<campaign_id>/artifact_manifest.json`

Recommended micro campaign/report layout:

- `runs/micro_batches/<batch_id>/micro_report.json`
- `runs/micro_batches/<batch_id>/category_breakdown.json`
- `runs/micro_batches/<batch_id>/counterfactual_report.json`
- `runs/micro_batches/<batch_id>/safety_report.json`
- `runs/micro_batches/<batch_id>/campaign_report.json`
- `runs/micro_batches/<batch_id>/paper_summary.md`
- `runs/micro_batches/<batch_id>/artifact_manifest.json`

### Baseline And Heuristic Safety

Baseline bots and heuristic labels are allowed only as non-LLM comparators and
post-hoc analysis.

They must never:

- appear in LLM prompts,
- alter legal actions shown to LLMs,
- coach LLMs,
- change retry behavior,
- change full-game prompt construction,
- change micro prompt construction.

### Documentation

Update docs so a researcher can:

- choose a seed cohort,
- choose a model roster,
- dry-run a campaign matrix,
- run `monopoly-long-v1`,
- run baseline comparisons,
- inspect statistical reports,
- inspect paper artifacts,
- run `bias-v1`,
- run `safety-v1`,
- run counterfactual reports,
- run multi-turn campaigns,
- create/import/export human expert labels,
- and verify that prompts were not changed.

Docs should include caveats about:

- run cost,
- OpenRouter model drift,
- insufficient sample sizes,
- subjective labels requiring human review,
- and not treating candidate safety flags as final labels.

## Verification Requirements

Before marking the goal complete, run the strongest available local verification.

Required checks:

- contract validation,
- Python ruff,
- Python mypy where practical,
- Python tests for engine/arena/api/microbench/telemetry touched areas,
- prompt-preservation tests,
- replay determinism tests,
- batch/campaign dry-run tests,
- baseline determinism tests,
- micro suite validation tests,
- counterfactual pair validation tests,
- campaign runner tests,
- human label import/export tests,
- frontend typecheck/build,
- browser verification for any changed UI routes.

Preferred final command:

```powershell
pwsh -File scripts/verify.ps1
```

If the full verification cannot run because of environment limitations, run the
closest targeted substitute commands and document the limitation in
`implementation_status.md`.

## Completion Checklist

The goal agent may mark this plan complete only when all items below are true or
explicitly blocked by an external dependency:

- `plan.md` has been followed as the source of truth.
- `implementation_status.md` has a detailed completed/in-progress/blocked record for
  this goal.
- Existing full-game and micro-v1 prompts are preserved by tests.
- `monopoly-long-v1` seed registry exists and validates.
- Model roster system exists and validates.
- Repeated campaign/batch matrix generation exists and supports dry-run/resume.
- Deterministic baseline bots exist and can be compared against models.
- Statistical reporting exists for long-horizon campaigns.
- Paper-quality long-horizon report artifacts exist.
- Long-horizon UI/API artifact inspection exists or existing pages are upgraded.
- `bias-v1` exists with explicit bias categories.
- `safety-v1` exists with explicit safety/deception categories.
- Counterfactual pair support exists and reports pair-level stability.
- Multi-turn campaign support exists and is executable.
- Human expert label infrastructure exists; real labels are imported if supplied, and
  otherwise the external labeling blocker is documented without fabricated labels.
- Micro category-level reports are cleaner and paper-facing.
- Docs explain the two research tracks end to end.
- Tests and build checks pass, or exact blockers are recorded.

## Final Reminder

The purpose of this goal is to finish the two nearest publishable research tracks.
Do not get pulled into RealEstateBench, prompt ablations, guardrails, or orchestrator
research. Those are valuable, but they are separate goals.

The prompt pipeline is benchmark-critical. Preserve it absolutely.
