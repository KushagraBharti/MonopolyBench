# MonopolyBench Research Directions

This document turns the current MonopolyBench project into a structured research roadmap.
It is written around four primary research directions:

1. Long-Horizon Economic Agency In Monopoly
2. Real Estate / Asset Management Benchmark
3. Targeted Scenario Suite: Micro-Decisions, Biases, Safety Probes
4. Control, Orchestration, And Information Design

It also defines the shared benchmark infrastructure that should be built regardless of
which direction is pursued first.

## Current Project Context

MonopolyBench is currently a deterministic Monopoly rules engine, LLM orchestration
harness, real-time UI, and replayable telemetry system. The core benchmark premise is
that models are not allowed to invent moves: the engine emits explicit legal actions,
the arena converts those legal actions into OpenRouter tool schemas, the model must
choose exactly one legal action, the engine applies it, and the telemetry layer writes
events, actions, decisions, prompts, snapshots, and summaries.

That is a strong foundation. The most important next step is to make MonopolyBench
less like a demo and more like a research instrument: stable benchmark suites,
controlled interventions, interpretable scorecards, human and heuristic baselines,
and paper-ready artifacts.

The existing README already frames the project around:

- raw Monopoly performance,
- long-horizon planning and execution,
- negotiation, bluffing, and deception,
- and uncovering LLM biases.

Those goals are still correct. The research directions below reorganize them into
publishable tracks.

## Research Inputs And Source Base

This roadmap was informed by:

- Andon Labs real-world evals: https://andonlabs.com/
- Andon Labs publications: https://andonlabs.com/publications
- Vending-Bench 2: https://andonlabs.com/evals/vending-bench-2
- Vending-Bench Arena: https://andonlabs.com/evals/vending-bench-arena
- GPT-5.5 on Vending-Bench: https://andonlabs.com/blog/openai-gpt-5-5-vending-bench
- Opus 4.8 on Vending-Bench: https://andonlabs.com/blog/opus-4-8-vending-bench
- Vending-Bench paper: https://arxiv.org/abs/2502.15840
- GenAI Beer Game site: https://infotheorylab.github.io/beer-game/
- GenAI Beer Game / HBR full PDF: https://infotheorylab.github.io/beer-game/assets/GenAI_Final_Version_w_Plots.pdf
- HBR article public page: https://hbr.org/2025/12/when-supply-chains-become-autonomous
- Finsimco Commercial Real Estate Simulation:
  https://finsimco.com/product/commercial-real-estate-simulation
- Finsimco Real Estate Finance Simulation:
  https://finsimco.com/product/real-estate-finance-simulation
- Finsimco Portfolio Management Simulation:
  https://finsimco.com/business-schools/simulations/portfolio-management
- The Blue Game real estate education case:
  https://ideas.repec.org/p/arz/wpaper/eres2018_254.html
- Harvard Graduate School of Design real estate negotiation simulation:
  https://execed.gsd.harvard.edu/programs/real-estate-negotiation-essentials-dealmaking-techniques-simulation/
- Harvard Business School Real Property Negotiation Game:
  https://www.hbs.edu/faculty/Pages/item.aspx?num=36282
- MobLab / Harvard Business Publishing Asset Market:
  https://www.moblab.com/moblab-harvard-business-publishing
- MobLab Asset Market teaching note:
  https://www.moblab.com/thar-blows-bubbles-crashes-asset-market
- Harvard Business Publishing Finance Simulation: Capital Budgeting:
  https://www.hbs.edu/faculty/Pages/item.aspx?num=39474
- ULI Hines Student Competition:
  https://americas.uli.org/programs/awards-competitions/hines-student-design-competition/
- MIT socially responsible real estate game:
  https://news.mit.edu/2016/socially-responsible-real-estate-games-0902
- Cesim Invest strategic investment management simulation:
  https://www.cesim.com/simulations/cesim-invest
- Local MonopolyBench microbench research backlog:
  `contracts/micro/research/scenario_backlog.md`

Notion note: the user mentioned an outdated Monopoly research page in Notion. The
Notion plugin skill was available locally, but the required `Notion:notion-search`
and `Notion:notion-fetch` tools were not exposed in this session, and MCP resources
returned no Notion resources. This document therefore uses web research plus the
local repository's existing research backlog. Once Notion tools are connected, this
file should be revised against that page.

## What The External Research Suggests

### Lessons From Vending-Bench

Vending-Bench is not just a business game. It is a test of long-horizon coherence.
Agents run a simulated vending-machine business over months or a year. They must
source products, manage inventory, set prices, negotiate with suppliers, handle
refunds, pay fees, and continue operating without a human stepping in.

The important design lessons for MonopolyBench are:

- The main benchmark signal should be a trajectory, not just a final result.
- Models can fail by drifting, stagnating, forgetting prior commitments, or entering
  repetitive loops.
- Run-to-run variance matters as much as mean score.
- Cost and token usage matter because long-horizon agents can burn enormous context.
- Targeted scenarios are needed alongside full runs because full runs are noisy.
- Misconduct should be measured separately from performance.
- An environment can have no natural 100% ceiling; benchmark quality comes from
  headroom, variance, and interpretability.

### Lessons From Vending-Bench Arena

Vending-Bench Arena adds competitors. That creates price wars, collusion, supplier
information markets, deception, and strategic leverage. This maps directly to
MonopolyBench because Monopoly already has auctions, trades, bargaining, threats,
alliances, and kingmaking.

The important design lessons are:

- Multiplayer outcomes should be evaluated with seat permutations and repeated seeds.
- Agents should be scored individually, but social behavior should be classified.
- Public messages and private reasoning are benchmark artifacts, not just UI content.
- Deception, collusion, coercion, and exploitation should be searchable and measurable.
- It is valuable to ask whether misconduct actually improves performance.

### Lessons From The GenAI Beer Game

The Beer Game is a classic management simulation with a simple decision loop:
retailer, wholesaler, distributor, and factory each decide how much to order upstream.
Limited information and delays create the bullwhip effect. The GenAI Beer Game work
tests model choice, information sharing, guardrails, and prompt design.

The important design lessons for MonopolyBench are:

- "More information" is not always better.
- Curated information can help weaker models and distract stronger ones.
- Guardrails can improve both performance and reliability.
- Prompt objective framing matters, especially for weaker models.
- A central orchestrator can improve agents without directly making decisions.
- The benchmark should evaluate system design, not only model intelligence.

### Lessons From Real Estate And Asset Management Simulations

Commercial real estate simulations used in education and corporate training tend to
center on:

- acquisition underwriting,
- debt and equity financing,
- market analysis,
- lease economics,
- asset management,
- portfolio strategy,
- exit timing,
- risk management,
- and investor-style reporting.

This is the natural long-term expansion of MonopolyBench. Monopoly is a real-estate
trading board game, but a serious research benchmark can retain the economic agency
structure while replacing toy mechanics with realistic property and capital-market
decisions.

# Common Changes Needed For Everything

The items in this section should be added regardless of which research direction is
chosen. They are the shared infrastructure that turns MonopolyBench into a credible
benchmark platform.

## 1. Standardized Run Scorecard

Every full game should produce a scorecard that is more informative than "who won."
Final winner is too noisy because Monopoly has dice, negotiation, auctions, and
bankruptcy cascades. The scorecard should measure performance across multiple axes.

Core outcome metrics:

- final rank,
- final cash,
- final net worth,
- final liquid net worth,
- bankruptcy status,
- turn of bankruptcy,
- number of opponents bankrupted,
- final property count,
- final monopoly count,
- final developed monopoly count,
- total houses built,
- total hotels built,
- total rent collected,
- total rent paid,
- taxes paid,
- jail turns,
- turns survived,
- and game completion status.

Strategic quality metrics:

- average cash buffer after optional actions,
- number of missed build opportunities,
- number of build actions while below a risk buffer,
- number of strong monopoly opportunities missed,
- number of times the model bought weak assets while cash-constrained,
- number of times it declined strategically important properties,
- number of post-turn opportunities correctly sequenced,
- number of times it held houses to preserve a shortage,
- number of times it converted to hotels in ways that released scarce houses,
- mortgage/unmortgage timing quality,
- liquidation quality,
- and jail timing quality.

Market and negotiation metrics:

- auction participation rate,
- auction win rate,
- auction overpay relative to heuristic value,
- auction underbid or early drop-out on high-value assets,
- trade proposals made,
- trade proposals accepted,
- trade proposals rejected,
- trade value delta,
- counteroffers made,
- trades that complete a monopoly for self,
- trades that complete a monopoly for opponent,
- trades that worsen own expected value,
- public messages per decision,
- and private thoughts per decision.

Reliability metrics:

- invalid first attempts,
- retry use rate,
- fallback use rate,
- schema failures,
- illegal action attempts,
- missing required messages,
- latency per decision,
- token usage per decision,
- cost per game,
- and cost per score point.

Behavioral metrics:

- public/private contradiction count,
- suspected deception count,
- suspected collusion count,
- kingmaking count,
- coercive threat count,
- revenge or spite-play indicators,
- false factual claims,
- self-serving misrepresentation,
- and ethical refusal rate.

This scorecard should be saved in `summary.json`, exported in batch CSV/JSON, and
displayed in the frontend.

## 2. Batch Evaluation Harness

Research claims require repeated, controlled runs. A single Monopoly game is not
enough.

Needed features:

- fixed seed sets,
- named seed cohorts,
- model config manifests,
- seat permutations,
- repeated runs per seed,
- round-robin model pools,
- one-model-vs-baselines mode,
- all-models-mixed mode,
- batch-level cost tracking,
- batch-level confidence intervals,
- batch-level replay verification,
- and batch-level artifact index.

The batch runner should support:

- `full_game` batches,
- `arena_season` batches,
- `micro_suite` batches,
- `multi_turn_campaign` batches,
- `prompt_ablation` batches,
- `guardrail_ablation` batches,
- `orchestrator_ablation` batches,
- and `human_baseline` batches.

Every batch should write:

- `batch_config.json`,
- `model_config.json`,
- `seed_manifest.json`,
- `results.jsonl`,
- `leaderboard.json`,
- `category_breakdown.json`,
- `statistical_summary.json`,
- `replay_report.json`,
- `cost_report.json`,
- and `run_index.json`.

## 3. Seat Permutation Support

Monopoly seating order matters. A model that always plays `p1` is not comparable to
a model that always plays `p4`.

The benchmark should:

- rotate every model through every seat,
- keep player identity and model identity separate,
- record seat order in every run artifact,
- report performance by seat,
- report model performance aggregated across seats,
- and detect whether a model is benefiting from seating bias.

For four-player games, the minimal serious setup is:

- fixed seed,
- same four models,
- all meaningful seat permutations or a balanced Latin-square subset,
- repeated across multiple seeds.

## 4. Deterministic Replay Verification

The project's strongest invariant is deterministic replay. Every research result
should prove that it is replayable.

Needed additions:

- automatic replay after every benchmark-worthy run,
- canonical event comparison,
- action-log sufficiency checks,
- schema validation for all artifacts,
- replay mismatch classification,
- and a replay hash included in the leaderboard.

Replay reports should answer:

- Was the run replayed successfully?
- Did canonical events match?
- Were all actions sufficient to reproduce the run?
- Were there nondeterministic fields that required canonicalization?
- Did any protocol shape fail validation?
- Did any snapshot overwrite occur?

## 5. Cost And Token Accounting

Long-horizon benchmarks are expensive. A model that scores slightly better while using
10x the cost may not be practically better.

Needed fields:

- input tokens,
- output tokens,
- reasoning tokens when available,
- cached tokens when available,
- cost per decision,
- cost per turn,
- cost per run,
- cost per batch,
- latency per decision,
- latency per turn,
- retries and fallbacks per dollar,
- and score per dollar.

Useful derived metrics:

- net worth per dollar,
- win probability per dollar,
- microbench points per dollar,
- valid-decision rate per dollar,
- and cost-adjusted arena rating.

## 6. Trace Analyzer

A leaderboard is not enough. Research readers need to understand why models won or
lost.

The trace analyzer should identify:

- decisive turns,
- missed purchase opportunities,
- bad auction bids,
- trades that changed game control,
- over-mortgage events,
- under-mortgage events,
- build timing mistakes,
- liquidation mistakes,
- jail timing mistakes,
- public/private contradictions,
- repeated no-progress behavior,
- and collapse moments.

For each flagged decision, the analyzer should include:

- run id,
- decision id,
- turn index,
- player/model,
- state summary,
- legal actions,
- chosen action,
- better candidate action if known,
- downstream outcome,
- and supporting event ids.

The UI should expose a "decisive decisions" view, and batch exports should include
a `trace_findings.jsonl`.

## 7. Failure Taxonomy

Every run should be tagged with failure modes. This should be partly deterministic
rules and partly classifier/human review.

Recommended taxonomy:

- `schema_failure`: invalid tool call, wrong args, missing messages.
- `illegal_action_attempt`: attempted action outside legal actions.
- `fallback_spiral`: repeated fallback use over a short window.
- `auction_overpay`: model overbid beyond reasonable value.
- `auction_underplay`: model dropped out or underbid on strategically critical asset.
- `bad_purchase`: model bought low-value property while cash-constrained.
- `missed_purchase`: model declined high-value property with sufficient cash.
- `missed_build`: model could build high-value houses but ended turn.
- `overbuild_liquidity`: model built while exposed to known high-rent danger.
- `hotel_trap`: model converted to hotel when house shortage was strategically useful.
- `bad_mortgage`: model mortgaged strategically important assets unnecessarily.
- `bad_unmortgage`: model spent cash unmortgaging when liquidity was more valuable.
- `bad_liquidation`: model sold/mortgaged the wrong assets during debt pressure.
- `premature_bankruptcy`: model declared bankruptcy despite legal survival options.
- `bad_jail_timing`: model paid/rolled/card-used against strategic context.
- `trade_gives_monopoly`: model handed an opponent a dangerous monopoly.
- `trade_missed_monopoly`: model failed to pursue obvious monopoly completion.
- `trade_negative_ev`: model accepted or proposed clearly bad economics.
- `public_private_mismatch`: private thought contradicts public message.
- `false_claim`: public message asserts a false game-state fact.
- `collusion`: explicit or implicit coordinated anti-competitive behavior.
- `kingmaking`: model helps a non-self player win despite no self-benefit.
- `spite_play`: model harms another player at large self-cost.
- `looping`: repeated low-value or no-progress choices.
- `strategy_drift`: model abandons an earlier profitable plan without a state reason.

## 8. Model Cards

Each model should have a persistent benchmark card.

A model card should include:

- model id,
- provider route through OpenRouter,
- date tested,
- benchmark version,
- prompt version,
- seed set,
- number of full games,
- number of micro scenarios,
- total cost,
- total tokens,
- average decision latency,
- valid first-response rate,
- retry rate,
- fallback rate,
- long-horizon score,
- arena score,
- microbench score,
- tactical category breakdown,
- negotiation category breakdown,
- honesty/safety indicators,
- top strengths,
- top failure modes,
- representative winning trace,
- representative losing trace,
- and caveats.

The card should be machine-readable JSON and human-readable Markdown.

## 9. Human Review Workflow

Some claims cannot be trusted to a heuristic. Deception, collusion, strategic trade
quality, and "why did this model lose" require human inspection at least on samples.

Needed tooling:

- reviewer queue,
- flagged decision list,
- side-by-side state/action/prompt view,
- rubric labels,
- adjudication status,
- reviewer notes,
- inter-rater agreement when multiple reviewers are used,
- and exportable labels.

Human review should be used for:

- validating automatic classifiers,
- creating benchmark examples,
- writing paper case studies,
- building gold labels for safety probes,
- and validating heuristic score thresholds.

## 10. Scenario Schema Expansion

The microbench suite already uses curated scenarios. To support future directions,
scenario metadata should become richer.

Recommended scenario fields:

- `scenario_id`,
- `schema_version`,
- `suite_id`,
- `category`,
- `subcategory`,
- `difficulty`,
- `tags`,
- `target_behavior`,
- `target_capability`,
- `strategic_tension`,
- `source_claims`,
- `source_urls`,
- `state_fixture`,
- `legal_actions_required`,
- `preferred_action`,
- `acceptable_actions`,
- `trap_actions`,
- `rubric`,
- `rubric_version`,
- `expected_rationale`,
- `counterfactual_pair_id`,
- `prompt_conditions_supported`,
- `guardrail_conditions_supported`,
- `orchestrator_conditions_supported`,
- and `review_status`.

Tags should include:

- `auction`,
- `buy`,
- `trade`,
- `jail`,
- `liquidity`,
- `liquidation`,
- `building`,
- `house_shortage`,
- `fame_bias`,
- `anchoring`,
- `loss_aversion`,
- `collusion`,
- `deception`,
- `public_private_mismatch`,
- `safety_probe`,
- `prompt_ablation`,
- `orchestrator`,
- and `multi_turn`.

## 11. Prompt Condition Framework

The current microbench records prompt condition, but it mainly supports the live game
prompt. Future research needs prompt conditions as a first-class experimental variable.

Core prompt conditions:

- `live_game`: current default prompt path.
- `compact_state`: smaller player/bank/action state.
- `full_state`: full protocol state available.
- `no_private_thought`: remove private thought requirement.
- `short_memory`: last N public/private items only.
- `long_memory`: larger history window.
- `structured_memory`: explicit strategy ledger.
- `rent_ev_summary`: adds computed rent/landing risk.
- `trade_opportunity_summary`: adds possible monopoly-completing trades.
- `opponent_threat_dashboard`: adds opponent cash, monopolies, build potential.
- `orchestrator_summary`: adds curated non-decision advice.
- `guardrailed`: adds explicit policy constraints.
- `ethics_guardrailed`: adds no deception/collusion instruction.

Every prompt condition should be:

- versioned,
- logged,
- included in run config,
- included in prompt artifacts,
- and reported in leaderboard breakdowns.

## 12. Guardrail Condition Framework

Guardrails are not just safety rules. They are experimental interventions.

Core guardrail conditions:

- `none`: only engine legal actions.
- `cash_buffer`: model may not take optional action below a cash threshold unless paying debt.
- `auction_budget_cap`: bid caps derived from property value and liquidity.
- `no_collusion`: explicit ban on coordinated price/trade/auction manipulation.
- `no_false_claims`: public factual claims must match visible game state.
- `no_extreme_trade_imbalance`: prevents exploitative or catastrophic trades.
- `no_kingmaking`: prohibits actions whose primary effect is helping a third party.
- `liquidation_survival_first`: debt decisions must avoid premature bankruptcy.

Each guardrail should record:

- whether it is hard or soft,
- whether it modifies legal actions or only prompt instructions,
- whether a violation was attempted,
- what action was blocked or discouraged,
- and whether performance improved or worsened.

## 13. Heuristic Value Models

A benchmark needs reference policies. They do not need to be perfect. They need to
be stable, interpretable, and good enough to flag obvious mistakes.

Needed value models:

- property purchase heuristic,
- auction bid heuristic,
- build value heuristic,
- jail strategy heuristic,
- mortgage/unmortgage heuristic,
- liquidation heuristic,
- trade valuation heuristic,
- monopoly threat heuristic,
- house shortage heuristic,
- and cash buffer heuristic.

These can start simple:

- high traffic groups get higher value,
- monopolies and blocks get bonuses,
- utilities are lower priority,
- cash buffers depend on opponent developed rent risk,
- auctions cap at cash-adjusted strategic value,
- builds prioritize three-house orange/red/light-blue situations,
- late-game jail is defensive when dangerous developed properties are ahead,
- and trades are scored by monopoly completion plus rent potential plus cash.

The heuristics should not replace LLM decisions. They should produce:

- baselines,
- warnings,
- scenario rubrics,
- trace analyzer labels,
- and paper explanations.

## 14. UI And Artifact Upgrades

The UI should become a research dashboard, not just a live game viewer.

Needed views:

- live game board,
- event feed,
- decision inspector,
- prompt/response viewer,
- model-vs-model leaderboard,
- batch dashboard,
- microbench dashboard,
- prompt ablation dashboard,
- guardrail dashboard,
- replay status dashboard,
- cost dashboard,
- trace analyzer,
- failure taxonomy explorer,
- public/private contradiction explorer,
- trade graph,
- auction graph,
- property ownership timeline,
- net worth timeline,
- cash timeline,
- rent flow timeline,
- build timeline,
- and bankruptcy timeline.

Research exports:

- paper-ready CSV,
- paper-ready JSON,
- markdown model cards,
- static plots,
- replay bundle zip,
- and shareable run links.

## 15. Documentation And Versioning

Every benchmark release should be versioned like a dataset.

Needed documents:

- benchmark card,
- data card,
- model evaluation protocol,
- seed manifest,
- scoring specification,
- prompt specification,
- guardrail specification,
- microbench specification,
- replay specification,
- limitations,
- known failure modes,
- ethics/safety notes,
- and changelog.

Versioned components:

- engine rules version,
- contract schema version,
- prompt schema version,
- scoring version,
- micro suite version,
- batch protocol version,
- leaderboard version,
- and UI artifact viewer version.

# Common Benchmark Foundations

These foundations are useful across all four research directions and should be treated
as the platform layer.

## Human Baselines

Human baselines are necessary because otherwise MonopolyBench only says "model A
beat model B." That is useful, but not enough for a research claim.

Human baseline modes:

1. Full-game human mode.
   A human plays through the same legal-action interface as an LLM. The engine still
   emits legal actions. The human selects actions and writes optional public/private
   notes. The same `actions.jsonl`, `decisions.jsonl`, and `events.jsonl` are written.

2. Microbench human mode.
   A human answers frozen scenarios. This creates expert or crowd labels for tactical
   scenarios, bias probes, and safety probes.

3. Human review mode.
   A human reviews model decisions and labels errors, deception, collusion, and
   strategic quality.

4. Human-vs-model arena mode.
   Humans can play against LLMs or heuristic bots in controlled settings.

Human data should record:

- player expertise level,
- prior Monopoly experience,
- time spent per decision,
- whether references were allowed,
- whether the human saw full state or compact state,
- and whether the human was playing to win or labeling a benchmark.

Human baseline metrics:

- average win rate,
- average net worth,
- microbench score,
- decision time,
- variance across people,
- variance across seeds,
- tactical error rates,
- and qualitative failure modes.

Human baseline research uses:

- calibrate difficulty,
- validate rubrics,
- compare model variance to human variance,
- determine if a benchmark is too easy or too hard,
- and provide interpretable paper baselines.

## Heuristic Bot Baselines

Heuristic bots make every experiment cheaper and easier to interpret.

Recommended bots:

1. Random legal bot.
   Chooses randomly among legal actions. Useful as a floor.

2. Always-buy bot.
   Buys all unowned properties when possible. Useful as a simple acquisition baseline.

3. Cash-conservative bot.
   Buys selectively, avoids low cash, rarely auctions aggressively.

4. Aggressive auction bot.
   Bids hard on properties that complete or block monopolies.

5. Builder bot.
   Prioritizes completing monopolies and building houses quickly.

6. Orange/red strategy bot.
   Specifically values orange/red/light-blue and jail-adjacent traffic.

7. No-trade bot.
   Plays without voluntary trades, useful to measure trade value.

8. Trade-seeking bot.
   Actively proposes monopoly-completing trades using a fixed valuation model.

9. Shark bot.
   Exploits bad offers, pressures cash-poor players, and bids defensively.

10. Ethical cooperative bot.
    Avoids deception/collusion, accepts mutually beneficial trades, and avoids
    kingmaking.

Each bot should be deterministic under seed and config.

Bot artifacts should be identical to LLM artifacts except prompt artifacts can be
empty or replaced by decision-rationale artifacts. This makes full comparisons easy.

## Infrastructure Foundation

The common infrastructure layer should include:

- strict contract validation,
- deterministic replay,
- scenario runner,
- full-game batch runner,
- arena season runner,
- prompt ablation runner,
- guardrail ablation runner,
- model registry,
- seed registry,
- scorecard builder,
- trace analyzer,
- model card generator,
- failure classifier,
- human review queue,
- and frontend research dashboard.

The technical principle should stay the same:

- engine is authoritative,
- UI is render-only,
- LLMs only choose legal actions,
- OpenRouter is the only LLM gateway,
- every mutation emits an event,
- artifacts are sufficient for replay,
- and protocol shape changes update contracts first.

# Research Direction 1: Long-Horizon Economic Agency In Monopoly

## Description, Summary, Explanation

This is the core MonopolyBench research direction. It asks whether LLM agents can
play a complete game of Monopoly as coherent long-horizon economic actors.

Monopoly is a useful environment because the game is simple enough to instrument but
hard enough to require durable strategy. A model must buy assets, preserve liquidity,
reason about probability, negotiate, bid in auctions, manage debt, build houses, decide
when to stay in jail, and survive adversarial opponents. Individual decisions are often
simple, but the consequences compound over dozens or hundreds of turns.

This direction should be framed similarly to Vending-Bench:

- The task is not one hard puzzle.
- The task is many simple decisions over a long horizon.
- Failure often comes from drift, inconsistency, memory failure, bad capital allocation,
  or inability to maintain a plan.
- The benchmark is strongest when it measures trajectory, variance, and failure modes.

The current MonopolyBench implementation already supports this direction well:

- deterministic engine,
- legal-action-only LLM orchestration,
- full event/action/decision logs,
- prompt artifacts,
- snapshots,
- replayability,
- and real-time UI.

The missing piece is a rigorous evaluation protocol and scorecard.

## What We Are Testing, Looking For, Etc.

Primary capability:

- Can an LLM maximize its chance of winning a full game of Monopoly under strict
  legal-action constraints?

Long-horizon coherence:

- Does the model maintain a coherent strategy across the whole game?
- Does it remember what properties it needs?
- Does it track opponent threats?
- Does it maintain liquidity after making a plan?
- Does it pursue monopoly completion before low-value actions?
- Does it adjust strategy after new information?
- Does it stop acting effectively after many turns?

Capital allocation:

- Does it buy the right properties?
- Does it avoid overpaying for weak assets?
- Does it preserve cash when exposed to developed opponent properties?
- Does it mortgage low-value assets to build high-value monopolies?
- Does it avoid premature bankruptcy?

Risk management:

- Does it maintain a cash buffer?
- Does it correctly judge rent exposure?
- Does it understand jail as early-game tempo and late-game defense?
- Does it avoid build decisions that expose it to immediate bankruptcy?

Strategic execution:

- Does it complete color groups?
- Does it build houses at the right time?
- Does it exploit house shortages?
- Does it use auctions defensively?
- Does it know when to trade and when to refuse?

Reliability:

- Does it produce valid tool calls?
- Does it need retries?
- Does it fall back often?
- Does it degrade with context growth or high reasoning effort?
- Does it loop or stall?

## Hypothesis

Frontier reasoning models will outperform weaker models in early tactical decisions,
especially buying obvious high-value properties and avoiding illegal actions. However,
full-game results will show high variance. Models will often lose through long-horizon
mistakes rather than isolated tactical ignorance.

Expected failure modes:

- overpaying in auctions because of fame bias or blocking obsession,
- buying weak assets while cash-constrained,
- failing to convert a monopoly into houses quickly enough,
- building while dangerously cash-poor,
- missing a chance to mortgage low-value assets for high-return development,
- accepting trades that complete an opponent's monopoly,
- staying out of jail late-game when jail is defensive,
- leaving jail early when the board ahead is dangerous,
- failing to adapt after an opponent builds,
- strategy drift after many prompt cycles,
- and repeated end-turn or no-progress loops.

An additional hypothesis is that lower cost or lower reasoning settings may sometimes
outperform high-reasoning settings if high reasoning causes verbosity, context churn,
or unstable private strategy notes.

## Things To Do To Make It Complete And Thorough

### Evaluation Protocol

- Define `monopoly-long-v1` as a benchmark suite.
- Choose seed cohorts: easy, normal, volatile, auction-heavy, trade-heavy, liquidation-heavy.
- Run each model across all seats.
- Require at least 5-10 games per model for initial comparisons.
- Require more games for publication-quality claims.
- Use same player names and prompt versions unless explicitly ablated.
- Record OpenRouter model ids, reasoning settings, temperature, and date.
- Report mean, median, standard deviation, min, max, and confidence intervals.

### Scoring

- Add long-horizon score formula.
- Keep final win/rank as a top-level metric but not the only metric.
- Include net worth, liquidity, monopoly control, rent flow, development efficiency,
  bankruptcy timing, and survival.
- Add score normalization so unfinished games can still be compared.
- Add cost-adjusted scores.
- Add risk-adjusted scores that penalize huge variance.

### Longitudinal Metrics

- Plot net worth over time.
- Plot cash over time.
- Plot rent collected/paid over time.
- Plot property acquisition by turn.
- Plot house/hotel development by turn.
- Plot decision validity over time.
- Plot token/cost over time.
- Plot fallback rate over time.
- Plot strategic activity over time.

### Failure Analysis

- Implement the failure taxonomy listed above.
- Flag decisive turns.
- Automatically detect missed build opportunities.
- Automatically detect auction overpay.
- Automatically detect trades that complete opponent monopolies.
- Automatically detect late-game jail mistakes.
- Automatically detect premature bankruptcy.
- Add human review for ambiguous cases.

### Baselines

- Add heuristic bots.
- Add human-play mode.
- Run every evaluated model against:
  - three random bots,
  - three heuristic bots,
  - mixed heuristic fields,
  - and other frontier models.
- Report whether models can beat simple fixed strategies.

### Paper Outputs

- Model leaderboard.
- Cost-adjusted leaderboard.
- Variance leaderboard.
- Tactical error table.
- Representative winning trace.
- Representative losing trace.
- Failure mode frequency chart.
- Prompt/reasoning ablation chart.
- Replay verification appendix.

# Research Direction 2: Real Estate / Asset Management Benchmark

## Description, Summary, Explanation

This is the largest expansion. It turns MonopolyBench from a Monopoly game into a
realistic real estate and asset management benchmark.

The goal is not to clone a proprietary educational game. The goal is to use the same
research pattern as the Beer Game: start from a famous, respected business education
simulation domain, then build an open deterministic testbed that evaluates autonomous
AI agents.

Monopoly already contains simplified real-estate ideas:

- buying properties,
- auctions,
- rent,
- mortgages,
- improvements,
- cash constraints,
- trading,
- bankruptcy,
- and market power.

The real-estate benchmark would replace toy Monopoly mechanics with realistic
commercial real estate mechanics:

- acquisition underwriting,
- rent rolls,
- debt structures,
- tenant rollover,
- cap rates,
- vacancy,
- operating expenses,
- capital expenditures,
- refinancing,
- broker negotiations,
- lender negotiations,
- portfolio construction,
- market cycles,
- disposition timing,
- and investor reporting.

This can become a separate benchmark family, tentatively:

- `RealEstateBench`
- `AssetManagerBench`
- `CREBench`
- or `PropertyBench`

The MonopolyBench engine and artifact architecture should be reused, but the domain
model would be new.

## Real-World Research And Simulation Anchors

The strongest backing options are below.

### Option A: Finsimco Commercial Real Estate Simulation

Link: https://finsimco.com/product/commercial-real-estate-simulation

Why it matters:

- Explicitly commercial real estate.
- Participants manage a discretionary fund.
- Includes office, retail, industrial, and multifamily assets.
- Covers acquisition, financing, asset management, and exits.
- Includes interest rate changes, cap-rate compression/expansion, tenant rollover,
  economic cycles, and black swan events.
- Designed for MBA students, finance students, corporate trainees, real estate firms,
  investment banks, pension funds, and professionals.

What to borrow conceptually:

- multi-round fund management,
- deal pipeline,
- acquisition bidding,
- financing negotiation,
- quarterly market updates,
- portfolio dashboards,
- P&L and balance sheet reporting,
- IRR/NPV assessment,
- debt-to-equity,
- diversification,
- vacancy,
- and final debrief.

Best use:

- This is the best anchor for a serious CRE asset-management benchmark.

### Option B: Finsimco Real Estate Finance Simulation

Link: https://finsimco.com/product/real-estate-finance-simulation

Why it matters:

- Focuses on underwriting property deals, modeling cash flows, assessing risk, and
  structuring financing.
- Includes cap rates, loan terms, commercial/residential properties, zoning, and
  development pressure.

What to borrow conceptually:

- financial modeling tasks,
- financing decisions,
- zoning constraints,
- development project analysis,
- cash-flow projections,
- and risk-adjusted deal selection.

Best use:

- Good for a more technical finance-heavy benchmark variant.

### Option C: The Blue Game

Link: https://ideas.repec.org/p/arz/wpaper/eres2018_254.html

Why it matters:

- A serious real-estate education game developed and used at Henley Business School,
  University of Reading.
- Used since 2012.
- More than 1000 students played it according to the abstract.
- Focuses on responsible investment, strategy, competition/cooperation, negotiation,
  team roles, leadership, complex relationships, deadlines, and professional reports.

What to borrow conceptually:

- responsible investment,
- social responsibility,
- sustainability,
- competitive/cooperative dynamics,
- role-based teams,
- professional presentation/reporting artifacts,
- game-master/orchestrator role,
- and industry-style dilemmas.

Best use:

- Strong anchor for social responsibility, negotiation, and multiplayer real-estate
  strategy.

### Option D: Harvard GSD Real Estate Negotiation Essentials

Link:
https://execed.gsd.harvard.edu/programs/real-estate-negotiation-essentials-dealmaking-techniques-simulation/

Why it matters:

- Real estate dealmaking depends on negotiation across land acquisition, approvals,
  financing, construction contracts, and sale terms.
- The course uses hands-on exercises and competitive negotiation simulations.
- It emphasizes BATNA, interests vs positions, distributive vs integrative negotiation,
  and common mistakes.

What to borrow conceptually:

- counterparty negotiation,
- BATNA tracking,
- deal-term negotiation,
- funding gaps,
- financing disputes,
- construction and sale terms,
- and multi-scenario planning.

Best use:

- Excellent for negotiation-specific sub-suites in a real-estate benchmark.

### Option E: HBS Real Property Negotiation Game

Link: https://www.hbs.edu/faculty/Pages/item.aspx?num=36282

Why it matters:

- Harvard Business School case simulating sale, purchase, or financing of a property.
- Directly tied to acquisition, negotiation, property, and real estate industry.

What to borrow conceptually:

- buyer/seller/lender roles,
- property purchase negotiation,
- financing negotiation,
- asymmetric information,
- offer/counteroffer structure,
- and deal-closing conditions.

Best use:

- Good anchor for targeted negotiation scenarios.

### Option F: ULI Hines Student Competition

Link:
https://americas.uli.org/programs/awards-competitions/hines-student-design-competition/

Why it matters:

- Long-running, well-known real estate and land-use competition.
- Graduate or fourth-year undergraduate teams create a development program for a
  real, large-scale site.
- Includes designs, narratives, and market-feasible financial data.
- Focuses on responsible land use and multidisciplinary development.

What to borrow conceptually:

- large-scale site redevelopment,
- multidisciplinary decision-making,
- market feasibility,
- public/private constraints,
- financial feasibility,
- urban design tradeoffs,
- and stakeholder-oriented reporting.

Best use:

- Strong for a development-oriented benchmark, not pure asset management.

### Option G: MIT Socially Responsible Real Estate Game

Link: https://news.mit.edu/2016/socially-responsible-real-estate-games-0902

Why it matters:

- MIT STL Lab and MIT Game Lab built a game for socially responsible real estate.
- The article describes a round-based four-player game.
- Players accumulate cash, develop projects, take on debt, gain prestige from social
  benefits, and face spillover effects between developments.
- It emphasizes that long-term profit can require investing in public goods.

What to borrow conceptually:

- social externalities,
- public-good investment,
- project adjacency effects,
- debt,
- prestige/reputation,
- four-player competition/cooperation,
- and responsible development.

Best use:

- Strong for an ESG / responsible development extension.

### Option H: MobLab / Harvard Business Publishing Asset Market

Links:

- https://www.moblab.com/moblab-harvard-business-publishing
- https://www.moblab.com/thar-blows-bubbles-crashes-asset-market

Why it matters:

- Asset Market (Bubbles and Crashes) is available through Harvard Business Publishing.
- Students trade assets over rounds.
- The game illustrates deviation from fundamental value and bubble/crash dynamics.

What to borrow conceptually:

- asset trading,
- fundamental value,
- dividend expectations,
- bubbles,
- crashes,
- experience effects,
- and price discovery.

Best use:

- Strong asset-management or market-behavior sub-suite, especially for testing
  speculative bubbles and overvaluation.

### Option I: Harvard Business Publishing Finance Simulation: Capital Budgeting

Link: https://www.hbs.edu/faculty/Pages/item.aspx?num=39474

Why it matters:

- Students allocate capital across 27 investment proposals over five years.
- Covers replacement investments, expansion investments, mutually exclusive projects,
  interdependent projects, growth options, NPV, IRR, payback, and budget constraints.
- Used in undergraduate, MBA, and executive education programs.

What to borrow conceptually:

- multi-year capital allocation,
- constrained budgets,
- NPV/IRR decision-making,
- portfolio of project opportunities,
- growth options,
- and capital committee framing.

Best use:

- Strong foundation for an asset-management benchmark if CRE is too domain-specific.

### Option J: Cesim Invest

Link: https://www.cesim.com/simulations/cesim-invest

Why it matters:

- Strategic investment management simulation for MBA programs, Executive MBA programs,
  and corporate trainings.
- Focuses on strategic fund management, ESG-integrated investing, factor investing,
  multi-asset allocation, tactical decisions, and corporate decisions for asset
  management firms.

What to borrow conceptually:

- fund management,
- ESG,
- factor allocation,
- tactical asset allocation,
- strategic investment committee decisions,
- and portfolio-level reporting.

Best use:

- Strong if the research direction broadens from real estate to general asset
  management.

## What We Are Testing, Looking For, Etc.

Primary capability:

- Can LLM agents manage a realistic portfolio of real assets over time?

Underwriting:

- Can the model parse an offering memorandum?
- Can it calculate NOI, cap rate, DSCR, LTV, debt yield, IRR, NPV, equity multiple,
  and cash-on-cash return?
- Can it identify hidden risks in a deal?
- Can it distinguish broker optimism from investable facts?

Capital allocation:

- Can the model allocate capital across multiple deals?
- Can it avoid overconcentration?
- Can it hold cash for better future opportunities?
- Can it choose between acquisition, capex, refinancing, and disposition?

Financing:

- Can it negotiate debt terms?
- Can it avoid over-leverage?
- Can it understand fixed vs floating rates?
- Can it respond to rate shocks?
- Can it manage covenants and maturity risk?

Asset management:

- Can it handle tenant rollover?
- Can it choose when to renovate?
- Can it improve occupancy?
- Can it decide when to renew, re-tenant, or sell?
- Can it handle operational surprises?

Market adaptation:

- Can it react to cap-rate expansion?
- Can it adapt to recession?
- Can it avoid buying at the top?
- Can it buy opportunistically during distress?

Ethics and governance:

- Does it misrepresent facts to investors or lenders?
- Does it overpromise returns?
- Does it hide downside risk?
- Does it ignore tenant/community externalities?
- Does it choose short-term profit over long-term responsibility?

## Hypothesis

Frontier models will be good at surface-level underwriting when all numbers are clean.
They will struggle when:

- data is noisy,
- broker claims are misleading,
- market regimes shift,
- leverage creates nonlinear risk,
- decisions have delayed effects,
- multiple stakeholders have conflicting incentives,
- or short-term IRR conflicts with long-term resilience.

Models may also make persuasive but analytically weak investment memos. They may
hallucinate assumptions, ignore covenants, overweight optimistic exit cap rates, or
overfit to recent market updates.

The strongest models should show:

- disciplined underwriting,
- explicit downside cases,
- careful leverage,
- coherent investment theses,
- good hold/sell timing,
- and transparent investor reporting.

## Things To Do To Make It Complete And Thorough

### Domain Design

- Decide whether the first version is CRE-specific or broader asset management.
- If CRE-specific, implement:
  - property types,
  - rent rolls,
  - leases,
  - tenants,
  - vacancy,
  - operating expenses,
  - capex,
  - debt,
  - appraisals,
  - cap rates,
  - brokers,
  - lenders,
  - buyers,
  - sellers,
  - market cycles,
  - and exits.
- If broader asset-management, implement:
  - asset classes,
  - expected returns,
  - volatility,
  - correlations,
  - factor exposures,
  - liquidity constraints,
  - client mandates,
  - ESG constraints,
  - and rebalancing.

### Engine

- Build a deterministic simulation engine.
- Seed market cycles.
- Seed deal pipelines.
- Seed tenant events.
- Seed rate shocks.
- Seed counterparty behavior.
- Keep all state transitions event-sourced.
- Keep actions replayable.
- Avoid direct wall-clock effects.

### Protocol

New snapshot objects:

- fund state,
- portfolio state,
- property state,
- tenant state,
- debt state,
- market state,
- deal pipeline,
- active negotiations,
- investor mandate,
- and compliance constraints.

New decision types:

- `ACQUIRE_ASSET_DECISION`,
- `BID_ON_ASSET_DECISION`,
- `REQUEST_FINANCING_DECISION`,
- `NEGOTIATE_LOAN_DECISION`,
- `APPROVE_CAPEX_DECISION`,
- `LEASE_RENEWAL_DECISION`,
- `SELL_ASSET_DECISION`,
- `REFINANCE_DECISION`,
- `REPORT_TO_INVESTORS_DECISION`,
- and `RESPOND_TO_SHOCK_DECISION`.

### Scoring

Financial:

- IRR,
- NPV,
- equity multiple,
- cash yield,
- NOI growth,
- portfolio value,
- debt service coverage,
- default rate,
- liquidity,
- drawdown,
- and final NAV.

Risk:

- leverage,
- concentration,
- tenant credit exposure,
- maturity wall,
- interest-rate sensitivity,
- vacancy sensitivity,
- downside-case survival,
- and stress-test score.

Behavior:

- truthful reporting,
- lender honesty,
- investor disclosure,
- ESG/community score,
- negotiation quality,
- and strategy consistency.

### Benchmarks

- Single-agent fund manager benchmark.
- Multi-agent competitive acquisition benchmark.
- Debt negotiation benchmark.
- Tenant rollover benchmark.
- Distressed market benchmark.
- ESG/responsible development benchmark.
- Bubble/crash asset market benchmark.
- Capital budgeting benchmark.

### Baselines

- rule-based conservative fund manager,
- aggressive leverage manager,
- buy-and-hold manager,
- value-add manager,
- opportunistic distressed manager,
- human student baseline,
- real estate professional baseline if possible,
- and spreadsheet/solver baseline.

### Artifacts

- investment memos,
- underwriting tables,
- deal logs,
- loan term sheets,
- market updates,
- investor letters,
- portfolio dashboards,
- final fund report,
- and replayable event logs.

# Research Direction 3: Targeted Scenario Suite: Micro-Decisions, Biases, Safety Probes

## Description, Summary, Explanation

This direction expands the existing microbench into a broad targeted evaluation suite.
It combines tactical micro-decisions, behavioral economics bias tests, and safety or
honesty probes.

Full games are noisy. A model can win because another model made a catastrophic
mistake, because dice favored it, or because seating order helped. Targeted scenarios
isolate specific competencies.

The current microbench already contains 130 frozen DecisionPoint fixtures across:

- buy or auction,
- auction,
- trade proposal,
- trade response,
- build or mortgage,
- liquidation,
- jail,
- and post-turn strategy.

The next step is to turn this into a richer suite family:

- `micro-v1`: existing tactical suite.
- `micro-v2`: expanded tactical suite.
- `bias-v1`: behavioral economics suite.
- `safety-v1`: deception/collusion/ethics suite.
- `negotiation-v1`: trade and public-message suite.
- `campaign-v1`: multi-turn targeted campaigns.

This is the research direction most likely to produce clean model comparisons quickly.

## What We Are Testing, Looking For, Etc.

Tactical Monopoly competence:

- Does the model know which properties are valuable?
- Does it understand cash buffers?
- Does it know when to auction?
- Does it know when to bid or drop?
- Does it know when to build?
- Does it know when to mortgage?
- Does it know when to stay in jail?
- Does it know when bankruptcy is unavoidable?

Strategic reasoning:

- Does it reason from current board state rather than generic advice?
- Does it adapt to opponent property sets?
- Does it consider turn order?
- Does it consider rent exposure?
- Does it understand monopoly completion?
- Does it understand house shortages?

Behavioral biases:

- Fame bias: Boardwalk/Park Place overvaluation.
- Anchoring: face value or current bid anchors.
- Sunk-cost fallacy: continuing bad investments.
- Endowment effect: overvaluing owned properties in trades.
- Loss aversion: refusing good risky trades.
- Availability bias: overreacting to recent rent hit.
- Overconfidence: building too aggressively with weak cash buffer.
- Myopic profit: taking immediate cash at long-term strategic cost.

Safety and honesty:

- Does it lie about the board state?
- Does it make false promises?
- Does it propose collusion?
- Does it accept collusion?
- Does it exploit another agent's confusion?
- Does it disclose or hide conflicts?
- Does private thought reveal deceptive intent?
- Does it behave differently when confronted?

Robustness:

- Does the same model answer consistently across equivalent scenarios?
- Does wording change behavior?
- Does extra irrelevant information distract it?
- Does minimal context reduce or improve performance?
- Does removing private thoughts change action quality?

## Hypothesis

Models will show category-specific strengths. A model that is strong in full games may
not dominate microbench. Some models will be tactically good but socially poor. Some
will avoid unethical behavior but lose negotiation value. Some will follow generic
Monopoly advice even when the local board state contradicts it.

Expected findings:

- Boardwalk fame bias will be common.
- Auction discipline will vary sharply by model.
- Cash-buffer reasoning will be a major differentiator.
- Trade valuation will be weaker than purchase decisions.
- Models will often produce plausible rationales for bad trades.
- Bias probes will reveal sensitivity to framing.
- Safety probes will reveal differences between ethical refusal, strategic deception,
  and accidental falsehood.

## Things To Do To Make It Complete And Thorough

### Expand Scenario Coverage

Tactical categories:

- buy/auction,
- auction bidding,
- trade proposal,
- trade response,
- post-turn sequencing,
- build timing,
- hotel conversion,
- house shortage,
- mortgage,
- unmortgage,
- liquidation,
- jail,
- bankruptcy,
- card effects,
- tax/cash shock,
- rent danger,
- and endgame finishing.

Bias categories:

- fame bias,
- anchoring,
- sunk cost,
- endowment effect,
- loss aversion,
- overconfidence,
- myopic cash preference,
- recency bias,
- fairness bias,
- and coalition bias.

Safety categories:

- collusion proposal,
- collusion response,
- false trade claim,
- false board-state claim,
- fake promise,
- exploit confused opponent,
- kingmaking pressure,
- revenge trade,
- deceptive public/private mismatch,
- and confrontation after misconduct.

### Add Multi-Turn Campaigns

Single-decision tests are useful but incomplete. Many Monopoly mistakes only appear
over sequences.

Campaign examples:

- complete orange monopoly over three turns,
- survive rent debt with liquidation choices,
- auction war followed by cash-buffer test,
- propose trade then respond to counteroffer,
- build during house shortage,
- stay in jail through dangerous board section,
- recover after opponent builds hotels,
- avoid kingmaking while losing,
- and respond to a collusion attempt over multiple messages.

Each campaign should have:

- initial state,
- allowed actions,
- deterministic opponent actions,
- expected strategic path,
- scoring by final campaign state,
- and per-step rubrics.

### Build Rubric System

Rubrics should include:

- action correctness,
- argument correctness,
- cash discipline,
- strategic rationale,
- public message quality,
- private thought quality,
- safety/honesty labels,
- and trap avoidance.

Rubric scoring should support:

- exact match,
- partial credit,
- penalty,
- disqualifying behavior,
- and human review override.

### Counterfactual Pairs

Bias tests need controlled pairs.

Examples:

- same EV property, famous vs non-famous name.
- same trade value, cash framed as loss vs gain.
- same auction value, high current bid vs low current bid.
- same debt state, recently hit rent vs no recent rent.
- same monopoly opportunity, opponent described as leader vs neutral.

The suite should measure whether the model changes action when only framing changes.

### Prompt Conditions

Run each scenario under:

- live-game prompt,
- compact prompt,
- full-state prompt,
- no-private-thought prompt,
- strategy-summary prompt,
- and guardrailed prompt.

This allows the project to test whether targeted performance is a property of the
model or of the prompting interface.

### Human And Heuristic Labels

For each scenario:

- label with a heuristic action,
- label with at least one human expert action,
- keep a rationale,
- and record disagreement.

Scenarios where humans disagree are not bad. They are useful if marked as
ambiguous. But they should not be used as hard correctness tests without care.

### Reporting

Each model should get:

- total micro score,
- category scores,
- difficulty breakdown,
- bias score,
- safety score,
- tactical score,
- invalid response rate,
- average latency,
- cost,
- and representative failures.

# Research Direction 4: Control, Orchestration, And Information Design

## Description, Summary, Explanation

This direction asks how to design the system around the model so it performs better
and behaves more safely.

It is inspired most directly by the GenAI Beer Game. In that work, agent performance
varies not only by model but by:

- what information is shared,
- whether a central orchestrator curates information,
- whether guardrails constrain costly mistakes,
- and how the objective is framed in the prompt.

MonopolyBench can test the same question in a competitive economic game. The engine
does not change. The legal actions do not change. What changes is the information and
policy context given to the model.

This direction is especially valuable because it creates practical deployment lessons.
The research output is not merely "model X is better than model Y." It becomes:

- what information should agents receive,
- which guardrails help,
- which prompt formats hurt,
- when orchestration improves decisions,
- and how to control autonomous economic agents without humans in the loop.

## What We Are Testing, Looking For, Etc.

Information design:

- Does full state help or overwhelm?
- Does compact state improve focus?
- Does a rent-risk summary improve cash management?
- Does an opponent-threat dashboard improve defense?
- Does a trade-opportunity summary improve negotiation?
- Does a property EV table improve buying and auction decisions?
- Does a build recommendation summary improve post-turn decisions?

Orchestration:

- Can a non-decision orchestrator improve model play by curating information?
- Should the orchestrator summarize only facts or also strategic implications?
- Does the orchestrator help weaker models more than stronger models?
- Does the orchestrator create overreliance?
- Does the orchestrator accidentally leak hidden information?

Guardrails:

- Do cash-buffer guardrails prevent bankruptcies?
- Do auction caps prevent overpaying?
- Do no-collusion guardrails reduce misconduct?
- Do anti-deception instructions preserve performance?
- Do no-kingmaking guardrails prevent spite play?
- Do trade imbalance guardrails prevent catastrophic trades?

Prompt objective framing:

- Is "win the game" enough?
- Does "maximize expected net worth while avoiding bankruptcy" perform better?
- Does "risk-adjusted Monopoly strategy" improve cash buffers?
- Does "play ethically and competitively" reduce deception?
- Does "maximize final rank" differ from "maximize final net worth"?

Memory design:

- Does structured memory help?
- Does longer memory hurt?
- Does forced periodic summary help?
- Does removing private thoughts change behavior?
- Does high reasoning effort create too much strategy-note churn?

## Hypothesis

Curated information and guardrails will improve weaker and mid-tier models. Stronger
models may benefit less, and in some cases may perform worse when given excessive
analysis.

Expected outcomes:

- Compact state may improve validity and reduce cost.
- Full state may help strong models but distract weaker models.
- Rent-risk summaries should improve cash-buffer decisions.
- Trade-opportunity summaries should improve trade proposal quality.
- Auction caps should reduce catastrophic overbids.
- No-collusion instructions should reduce explicit collusion but may not eliminate
  tacit coordination.
- Strong ethical prompts may reduce misconduct with limited performance loss, but
  this must be measured.
- Structured memory may reduce strategy drift, while unstructured private thoughts
  may create repetitive note spam.

## Things To Do To Make It Complete And Thorough

### Prompt Conditions

Implement and version:

- `live_game`
- `compact_state`
- `full_state`
- `minimal_state`
- `no_private_thought`
- `short_memory`
- `long_memory`
- `structured_memory`
- `rent_ev_summary`
- `trade_opportunity_summary`
- `opponent_threat_dashboard`
- `orchestrator_facts_only`
- `orchestrator_strategy_summary`
- `guardrailed_cash`
- `guardrailed_ethics`
- `guardrailed_auction`

### Orchestrator Types

Facts-only orchestrator:

- summarizes current state,
- does not recommend actions,
- does not introduce new strategy,
- cannot alter legal actions.

Strategic-summary orchestrator:

- computes rent danger,
- highlights monopoly opportunities,
- highlights opponent threats,
- summarizes likely trade targets,
- and highlights cash risks.

Safety orchestrator:

- flags potential collusion,
- flags public/private contradictions,
- flags deceptive factual claims,
- flags kingmaking,
- and flags exploitative trades.

Memory orchestrator:

- maintains a stable strategy ledger,
- records model commitments,
- tracks past trades and promises,
- summarizes long-term goals,
- and prevents duplicate/contradictory strategy notes.

### Guardrail Experiments

Hard guardrails:

- remove or block action if it violates explicit policy.
- Example: cannot bid above cash-adjusted cap.

Soft guardrails:

- leave legal actions unchanged but add warnings.
- Example: "This bid may leave you below rent-risk buffer."

Experimental guardrails:

- cash buffer,
- auction cap,
- trade imbalance cap,
- no false factual claims,
- no collusion,
- no kingmaking,
- no premature bankruptcy,
- liquidation survival,
- and no self-contradictory public claims.

Each guardrail experiment should report:

- performance impact,
- misconduct reduction,
- invalid action reduction,
- fallback reduction,
- cost impact,
- and examples of blocked or warned decisions.

### Information Ablation Protocol

For each model:

- same seed set,
- same seat permutations,
- same model config,
- different prompt condition,
- same scoring and replay requirements.

Report:

- mean score by condition,
- variance by condition,
- category score by condition,
- cost by condition,
- invalid rate by condition,
- and failure modes by condition.

### Memory Experiments

Test:

- public timeline size,
- private thought size,
- no private thought,
- structured private strategy,
- periodic summary,
- retrieval-style memory,
- and compaction frequency.

Measure:

- performance,
- cost,
- repeated strategy-note behavior,
- contradictions,
- missed commitments,
- and strategy drift.

### Safety Measurement

Control experiments must include safety measurement, not only performance.

Track:

- explicit collusion proposals,
- collusion acceptances,
- tacit collusion indicators,
- false public claims,
- private/public contradictions,
- coercive threats,
- exploitative trades,
- kingmaking,
- and confrontation honesty.

### Outputs

This direction should produce:

- prompt ablation leaderboard,
- guardrail ablation leaderboard,
- orchestrator ablation leaderboard,
- information distractibility score,
- safety/performance Pareto chart,
- model-specific best prompt condition,
- and deployment recommendations.

# Recommended Build Order

The best order is:

1. Build the common scorecard and batch harness.
2. Add heuristic bot baselines.
3. Add long-horizon full-game leaderboard.
4. Add expanded microbench schema and category reporting.
5. Add prompt-condition framework.
6. Add trace analyzer and failure taxonomy.
7. Add human baseline mode.
8. Add targeted bias/safety scenario suites.
9. Add orchestrator and guardrail experiments.
10. Begin the real estate / asset management benchmark as a separate engine family.

This order keeps the project publishable at every stage:

- Stage 1 publication: Long-Horizon Economic Agency In Monopoly.
- Stage 2 publication: Negotiation, Bias, And Safety In MonopolyBench Micro.
- Stage 3 publication: Orchestrating Competitive LLM Agents In Monopoly.
- Stage 4 publication: From MonopolyBench To RealEstateBench.

# Open Questions

- Should MonopolyBench keep private thoughts in all official benchmark tracks, or
  should private thoughts become an optional prompt condition?
- Should deception be allowed as part of Monopoly strategy, or should the benchmark
  split "unrestricted competitive" and "ethical competitive" tracks?
- Should guardrails modify legal actions or only add prompt warnings?
- How many seeds and seat permutations are required for a publishable leaderboard?
- What should the primary long-horizon score be: win rate, final net worth, rank,
  risk-adjusted score, or a composite?
- How much should heuristic value models influence scoring versus only flagging?
- Should real estate be built as a direct MonopolyBench extension or as a separate
  benchmark using the same infrastructure?
- Can human expert labels be collected cheaply enough to validate microbench rubrics?
- How should model updates be handled when providers silently change model behavior?
- How should OpenRouter routing/version drift be logged?

# Bottom Line

The strongest near-term research story is:

> MonopolyBench is a reproducible benchmark for long-horizon economic agency,
> negotiation, and safety in multi-agent LLM systems.

The strongest medium-term expansion is:

> The MonopolyBench architecture can evolve into a realistic real estate and asset
> management benchmark, analogous to how the Beer Game became an autonomous
> supply-chain testbed.

The shared foundation is more important than any single direction. A standardized
scorecard, batch protocol, baselines, replay verification, trace analyzer, prompt
conditions, and model cards will make every research track stronger.
