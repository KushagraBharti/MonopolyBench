# MonopolyBench Research Directions

This file is the canonical research roadmap. It should stay readable and current: enough detail to explain what each research direction is, why it matters, and what evidence would make it publishable, without becoming a raw source dump or implementation log. Historical drafts and long goal prompts live in `docs/archive/`; raw model research outputs live in `docs/research_raw/`; operational analysis details belong in `analysis.md` and `analysis_process.md`.

MonopolyBench should not be framed as "LLMs play Monopoly." The stronger framing is that MonopolyBench tests whether off-the-shelf LLM agents can operate as durable economic agents under enforceable rules, scarce capital, repeated bargaining, adversarial incentives, public/private communication gaps, and bankruptcy pressure. The deterministic engine, legal-action-only interface, full artifact trail, and replayable state transitions make the benchmark useful for both performance analysis and behavior analysis.

The current near-term paper should center on Direction 1 and Direction 3. Direction 1 gives the benchmark its long-horizon economic spine. Direction 3 gives the diagnostic microscope for tactical errors, behavioral biases, deception, collusion, and manual review. Direction 2 and Direction 4 remain valuable follow-up tracks, but they should not distract from turning the current Monopoly benchmark into a rigorous, replayable, analyzable research system.

## Direction 1: Long-Horizon Economic Agency

Direction 1 is the primary full-game benchmark track. Four LLM agents play complete Monopoly games through engine-provided legal actions. The point is not simply to crown a winner in a single game; the point is to study whether models can sustain coherent economic behavior across hundreds of stochastic, adversarial, state-dependent decisions.

The research question is: can LLM agents survive and compound wealth while managing property acquisition, cash buffers, auctions, trades, mortgages, houses/hotels, jail timing, rent shocks, liquidation, and bankruptcy pressure? Monopoly is useful here because every local decision is simple enough to inspect, but the consequences compound. A model can make valid legal actions and still fail because it overbids, hoards cash, underbuilds, empowers a leader, exits jail at the wrong time, or liquidates the wrong assets under pressure.

The main outcome metrics should report survival, rank, final net worth, net-worth AUC, cash AUC, bankruptcy order, and cost-adjusted performance. The deeper analysis should connect those outcomes to trajectory signals: rent power, rent exposure, liquidity-at-risk, monopoly completion, development timing, auction discipline, trade surplus, mortgage dependency, liquidation quality, invalid attempts, fallbacks, reasoning tokens, latency, and total OpenRouter cost. The goal is to explain wins and collapses, not just record them.

Direction 1 needs repeated controlled runs before it can support model-ranking claims. Single games are case studies and artifact-validation runs. Serious comparisons need fixed seed cohorts, seat rotations, stable rosters, prompt/rules hashes, replay verification, provider metadata, pricing snapshots, and uncertainty estimates. Results should be bootstrapped by game or seed, not by treating every decision in one trajectory as independent evidence.

The core deliverables are full-game artifacts that can be inspected and replayed: event/action/decision logs, per-turn snapshots, prompt/response records, usage and cost summaries, replay reports, scorecards, model-level breakdowns, review queues, and analysis plots. A strong run report should include net-worth and cash timelines, rent and property development graphs, auction/trade tables, bankruptcy postmortems, cost/reasoning outlier tables, and a short human-readable interpretation.

Direction 1 becomes publishable when the benchmark can answer questions like: which failures are local tactical mistakes versus long-horizon drift? Do liquidity metrics predict bankruptcy better than raw net worth? Does reasoning effort buy better decisions or just more cost? Do models that trade more win more, or only when the trades create real surplus? Are winners robust across seats, seeds, and opponent rosters?

## Direction 2: Real Estate And Asset-Management Extension

Direction 2 is a future expansion track. Monopoly is already a simplified asset economy: agents buy properties, collect rent, develop assets, take on mortgage liability, manage liquidity, and fail through bankruptcy. Direction 2 asks whether the same benchmark philosophy can generalize into a more realistic real-estate or asset-management environment.

The motivation is to move from a known board-game economy to a domain closer to finance, operations, and business decision-making. A future RealEstateBench-style environment could test property valuation, capital budgeting, debt service, portfolio construction, leasing, renovation, negotiation, liquidity planning, market shocks, and long-horizon return. This would connect MonopolyBench to practical questions about autonomous economic agents in domains with real financial analogs.

This direction should remain future-facing for now. It is attractive, but it is also expensive and easy to scope-creep. The current Monopoly system already provides a cleaner closed environment with complete rules, deterministic replay, bounded actions, and inspectable consequences. That makes it the right place to solve the benchmark methodology first.

Useful preparatory work for Direction 2 includes collecting real-estate simulation references, identifying which Monopoly metrics transfer cleanly, and deciding what a deterministic asset-management ruleset would require. The important inherited principles are engine authority, legal-action constraints, full artifacts, replayable state, usage/cost accounting, and downstream analysis that never leaks into prompts.

Direction 2 should not introduce direct vendor APIs, hidden nondeterminism, unversioned rules, or prompt changes into the current benchmark. If it becomes active later, it should be treated as a separate benchmark track with its own schemas, manifests, scenarios, and evaluation design.

## Direction 3: Targeted Scenario Suite

Direction 3 is the diagnostic layer. Full games show what happened; targeted scenarios help explain why it happened. The suite uses frozen Monopoly states to test specific tactical decisions, behavioral biases, negotiation behavior, deception risk, collusion risk, public/private mismatch, and safety-relevant strategic behavior.

The core research question is: when a model fails in a full game, can we isolate the underlying capability gap? A full-game bankruptcy might come from a bad auction, bad trade, missed build, poor liquidation, overconfidence, unsafe collusion, or simple schema failure. A targeted scenario suite can test those mechanisms directly, with controlled states and repeatable scoring.

The tactical suite should cover acquisition decisions, auctions, trade proposals, trade responses, mortgage/unmortgage choices, house/hotel building, liquidation triage, jail strategy, rent-shock recovery, opponent blocking, and no-op/end-turn discipline. The safety and behavior suite should cover false board-state claims, false trade-economics claims, fake promises, exploit attempts, collusion-like no-bid agreements, market-allocation analogs, public/private mismatch, kingmaking, spite, and coercive threats.

Bias probes should be built as counterfactual pairs. A bias claim is weak if it only says "the model overpaid for Boardwalk." A stronger claim compares matched states where only an irrelevant framing variable changes, such as famous versus non-famous property name, high versus low anchor, loss versus gain framing, or leader versus neutral opponent identity. The expected economic action should remain the same across the pair, and the analysis should measure whether the model shifts anyway.

Each scenario should be a durable artifact, not just a prompt. It needs a stable fixture ID, source state, legal action set, state hash, prompt condition, expected or acceptable actions, scoring rule, bias/safety metadata, cost and token fields, and human-review fields. If a scenario comes from a full game, it should link back to the source run, turn, decision, state, prompt, response, and event window.

Direction 3 becomes most valuable when it connects back to Direction 1. Critical full-game states should be extracted into fixtures: high-regret decisions, bankruptcy windows, major trades, contested auctions, monopoly-creating moments, public/private mismatch candidates, and top reasoning/cost outliers. Then models can be re-queried on those same states outside the full-game context. The comparison between in-game action and isolated micro action helps separate local tactical weakness from long-horizon context drift.

The core deliverables are scenario registries, scenario result tables, category reports, counterfactual-pair reports, safety review queues, human label workflows, and micro-to-full mapping tables. Human review matters here. Automated flags can identify candidates, but deception, collusion, spite, and kingmaking labels should be reviewed with a codebook, evidence snippets, confidence levels, and adjudication.

## Direction 4: Control, Orchestration, And Information Design

Direction 4 studies how model behavior changes when the orchestration layer changes. It covers prompt conditions, memory windows, information visibility, private/public channels, agent identity, guardrail conditions, tool policies, retry policies, and orchestrator design.

This matters because LLM-agent behavior is not only a property of the model. It also depends on what the agent sees, how legal actions are described, whether opponents are named, whether private thought is requested, how much history is included, whether public messages are visible, and whether the system asks for competitive play, safety, deception avoidance, or cooperation. These conditions can affect competence, cost, reliability, deception, collusion, and negotiation style.

Direction 4 should be handled carefully because prompt and orchestration changes alter the benchmark surface. The default benchmark should remain stable. Any intervention must be versioned as an explicit experimental condition, logged in the run manifest, and analyzed separately from the default full-game and micro-suite results.

Examples of useful Direction 4 studies include named versus anonymized opponents, private-thought enabled versus disabled, different memory windows, public-message-only versus public/private artifacts, fixed persona versus default prompt, legal-action format variants, reasoning-effort ablations, safety guardrail conditions, and orchestrator policies that summarize or hide parts of the state. Each condition should be designed to answer one clear question rather than bundled with unrelated changes.

The deliverables for Direction 4 are condition registries, prompt/rules hashes, controlled ablation runs, manifest fields that fully describe the intervention, and analysis comparing behavior across conditions. This track should not be mixed into the main benchmark leaderboard unless the condition is explicitly part of the benchmark definition.

## Cross-Cutting Requirements

All directions depend on the same benchmark foundations. The engine must stay authoritative and deterministic. The UI must stay render-only. LLMs must remain legal-action constrained. OpenRouter must remain the only gateway unless the project explicitly revises that policy. Every serious run needs artifacts, manifests, usage/cost accounting, replay verification, and enough traceability to support manual review.

The documentation stack should stay separated by purpose. `research_direction.md` explains the research roadmap. `analysis.md` explains what signals and metrics we analyze. `analysis_process.md` should explain the repeatable workflow after a run finishes. `docs/artifact_reference.md` explains artifacts. Raw research outputs belong in `docs/research_raw/`. Old plans and historical status files belong in `docs/archive/`.

The next practical step is to integrate the Pro and Deep Research outputs into `analysis.md` and `analysis_process.md` without dumping them wholesale. The analysis files should become structured, human-written, and repeatable: enough rigor for research, but not so verbose that every future run becomes impossible to review.
