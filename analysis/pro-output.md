**Run A — `mock-83265-81ed4937`: replay status exactly `state_passed_artifact_failed`.** State replay passes all 1,640 state-relevant comparisons. Strict artifact replay first differs at sequence/index 669, event `mock-83265-81ed4937-evt-000669`, decision `mock-83265-81ed4937-dec-000096`, because the original response records `valid=false`, `error="fallback:illogical_after_retry"` for `reject_trade`, whereas replay represents the already-applied fallback as `valid=true`, `error=null`. There are no missing actions, extra actions, or decision-ID mismatches. 

**Run B — `mock-44910-42ec35c5`: state replay passed and full artifact replay passed.** State replay passes 1,942/1,942 state-relevant comparisons; strict artifact replay passes 4,102/4,102 events, with no missing actions, extra actions, or decision-ID mismatch. 

# 1. Executive research snapshot

MonopolyBench is currently strongest as a **replayable benchmark methodology plus two exhaustive, source-linked full-game case studies**. It is not yet a comparative model benchmark in the inferential sense. The two canonical games establish that the system can preserve long LLM-agent trajectories, enforce legal action surfaces, reconcile decisions and attempts, retain prompts and responses, account for usage and cost, reconstruct economic mechanisms, and support state-level replay and evidence-linked qualitative review. They do not estimate stable model effects, model rankings, deception prevalence, or causal cost-quality relationships.

The strongest defensible scientific thesis is:

> **MonopolyBench operationalizes durable economic agency as sequences of legally constrained decisions in a deterministic-transition, multi-agent asset economy. It links survival and wealth trajectories to capital allocation, bargaining, development, liquidity, reliability, and inference cost through replayable artifacts and, prospectively, controlled counterfactual fixtures.**

The paper should make four immediate changes.

First, replace every unqualified use of **“deterministic benchmark”** with a precise statement: the engine transition is deterministic conditional on the frozen initial state, RNG/deck state, and applied actions; model outputs remain stochastic and provider-dependent.

Second, recast the two current runs as **pipeline-validation and mechanism case studies**. Run A is state-replay-valid but not strict-artifact-replay-clean. Run B passes both layers. Neither run belongs in a leaderboard.

Third, replace the draft’s opposition between “descriptive analysis” and “heuristic oracle” with a layered standard:

1. deterministic facts and accounting;
2. descriptive trajectory metrics;
3. evidence-linked qualitative interpretation;
4. explicit branch/oracle tiers for counterfactual claims;
5. balanced campaigns for comparative claims.

Fourth, remove or temporarily quarantine manuscript numbers that cannot be traced from the attached evidence packages to a named generated table, metric definition, and manifest hash. This applies especially to the draft’s total-token, aggregate rent, terminal net-worth, property-count, and mortgage-liability tables. They may be correct, but the present brief does not contain enough provenance to certify them.

The latest research memo already defines the correct publication boundary, availability tags, metric hierarchy, branch tiers, and seed-block design.  The process guide correctly requires integrity before interpretation, descriptive before inferential analysis, and evidence-linked review after automated triage.  The automation guide makes clear that descriptive episode metrics exist, while regret, trade surplus, branch counterfactuals, robust cross-run inference, and adjudicated semantic labels remain incomplete or manual. 

# 2. Source reconciliation and authoritative fact table

## 2.1 Source hierarchy

The controlling source order should be:

| Priority | Source                                                                        | Controlling role                                                                                  |
| -------: | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
|        1 | [Research brief](sandbox:/mnt/data/Pasted%20text.txt)                         | Required output, nonnegotiable facts, current task boundary.                                      |
|        2 | [Latest IEEE manuscript](sandbox:/mnt/data/monopolybench_ieee_draft_v0_1.tex) | Current prose to revise, not the controlling source for run facts.                                |
|        3 | [analysis.md](sandbox:/mnt/data/analysis.md)                                  | Research framing, metric definitions, formulas, claim boundaries, future design.                  |
|        4 | [analysis_process.md](sandbox:/mnt/data/analysis_process.md)                  | Ideal integrity-first workflow and publication gates.                                             |
|        5 | [analysis_automated.md](sandbox:/mnt/data/analysis_automated.md)              | What is actually automated now versus planned.                                                    |
|        6 | Integrity report for each run                                                 | Controlling deterministic counts, cost, endpoint, preservation, and replay status.                |
|        7 | Exhaustive/manual review report                                               | Controlling attempt-level and qualitative reconciliation, subject to its stated epistemic limits. |
|        8 | Case studies                                                                  | Mechanism narratives with exact source IDs; interpretations remain case-specific.                 |

When sources conflict:

* The integrity report overrides the manuscript’s stale replay wording.
* `analysis_automated.md` overrides aspirational workflow language about what already exists.
* Canonical events, applied actions, snapshots, and raw attempt artifacts override prose summaries.
* A model’s `private_thought` field is evidence of text emitted into a private channel, not direct access to cognition.
* A case-study interpretation never overrides deterministic state or legality.
* No counterfactual claim is promoted to fact without branch analysis.

## 2.2 Authoritative run facts

| Field                      | Run A                                                         | Run B                                                          |
| -------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------- |
| Canonical run ID           | `mock-83265-81ed4937`                                         | `mock-44910-42ec35c5`                                          |
| Saved-game name            | `frontier-191-mock-83265-81ed4937-openai-gpt-5-5`             | `frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview` |
| Frozen source commit       | `fa773791718e3b5d8ff18448e2ad3fa42b375259`                    | Same                                                           |
| Playable turns             | `0..190`, 191 playable turns                                  | `0..272`, 273 playable turns                                   |
| Terminal-only checkpoint   | `191`                                                         | `273`                                                          |
| Winner                     | OpenAI GPT 5.5                                                | Gemini 3 Flash Preview                                         |
| Endpoint                   | Bankruptcy; last survivor                                     | Bankruptcy; last survivor                                      |
| Winner cash                | $718                                                          | $3,921                                                         |
| Events                     | 3,972                                                         | 4,102                                                          |
| Resolved decisions/actions | 583/583                                                       | 540/540                                                        |
| Attempts                   | 604                                                           | 549                                                            |
| Retry decisions            | 21                                                            | 9                                                              |
| Invalid attempts           | 23                                                            | 9                                                              |
| Deterministic fallbacks    | 2                                                             | 0                                                              |
| Negotiation/trade units    | 69 trade threads                                              | 44 trade episodes, 7 accepted                                  |
| Auctions                   | 9                                                             | 8                                                              |
| Mortgage activity          | 41 openings, 21 unmortgages                                   | 31 mortgage/unmortgage episodes                                |
| Bankruptcy windows         | 3                                                             | 3                                                              |
| Recorded OpenRouter cost   | `$27.71173045`                                                | `$4.24475240`                                                  |
| Missing usage              | One HTTP 503 attempt, `dec-000389`; null, not imputed         | None                                                           |
| State replay               | Pass, 1,640 comparisons                                       | Pass, 1,942 comparisons                                        |
| Strict artifact replay     | Fail first at sequence 669, explained representation mismatch | Pass, 4,102 comparisons                                        |
| Publication use now        | State-grounded case study with strict artifact caveat         | Fully replay-clean case study                                  |
| Ranking use now            | No                                                            | No                                                             |

Run A facts are controlled by its integrity and exhaustive review packages.   Run B facts are controlled by its corresponding packages.  

## 2.3 Precise benchmark reconstruction

### Contracts

The contracts layer defines JSON schemas, board specifications, shared types, legal action payloads, event structures, and validation rules. It is the interface boundary among the engine, arena, telemetry, API, and frontend.

### Engine

The engine owns:

* canonical game state;
* rule application;
* legal-action generation;
* dice and card resolution;
* auctions, trades, mortgages, buildings, rent, liquidation, and bankruptcy;
* exclusive state mutation;
* state-relevant event emission;
* replay from frozen state/RNG plus applied actions.

The official rules establish auctions after a declined purchase, finite stocks of 32 houses and 12 hotels, even building and selling constraints, mortgage rules, bankruptcy transfers, and the last-player-standing endpoint. 

The appropriate claim is:

> Given the same canonical initial state, ruleset, RNG/deck schedule, and applied action sequence, the engine state trajectory is replayable.

The inappropriate claim is:

> The benchmark or LLM behavior is deterministic.

### Arena

The arena owns:

* model-facing prompt construction;
* current OpenRouter request routing;
* response parsing;
* schema validation;
* legal-action matching;
* corrective retries;
* deterministic fallback selection after retry exhaustion.

Invalid attempts do not mutate game state. An attempt can therefore matter to cost, latency, reliability, and the model’s emitted language without becoming an applied action.

### Telemetry

Telemetry records the research evidence surface:

* `events.jsonl`: authoritative chronology;
* `actions.jsonl`: engine-applied actions;
* `decisions.jsonl`: decision surfaces, attempts, validation, retry, and fallback metadata;
* `state/`: canonical checkpoints;
* `prompts/` and `quality_check/`: requests, raw responses, parsed outputs, and human-readable audit files;
* usage and cost artifacts;
* scorecards and summaries;
* state and artifact replay reports;
* trace/failure findings;
* generated tables, figures, manifests, and evidence indexes.

### API and frontend

The FastAPI layer controls execution and streaming. The React frontend is render-only and must not compute authoritative rules or state. A UI mismatch is therefore a display defect, not a competing state source.

### Public and private communication

A public message is part of the game’s observable social interaction. A private field is an analysis-facing model output. It may support a documented public/private discrepancy, but it is not hidden chain-of-thought ground truth, a reliable utility function, or proof of intent.

### Replay contract

The split replay design is scientifically preferable to a single pass/fail flag:

* **State replay** asks whether state-relevant transitions reproduce.
* **Artifact replay** asks whether the complete event log, including observational metadata and fallback representation, reproduces exactly.

Run A demonstrates why the distinction is necessary. The applied action path and canonical state reproduce, while one response-event representation does not. Calling the run either fully “failed” or fully “clean” would discard information.

# 3. Benchmark thesis and novelty boundary

## 3.1 Recommended thesis

> MonopolyBench is a rules-complete, replay-oriented environment for evaluating off-the-shelf language models as long-horizon economic agents. It exposes an enumerable legal action surface over a persistent asset economy and records the connection among model calls, communication, applied actions, economic state, reliability, and cost. Its distinctive contribution is not any single Monopoly mechanic or agent capability, but the auditable conjunction of durable ownership, bargaining, auctions, development, collateral, liquidity shocks, legal liquidation, bankruptcy, and natural-language interaction.

## 3.2 What MonopolyBench is not first at

MonopolyBench should not claim to be first at:

* long-horizon autonomous agents;
* simulated business management;
* multi-agent economic competition;
* auctions;
* negotiation or bargaining;
* bluffing or deception evaluation;
* social interaction benchmarks;
* game-theoretic LLM evaluation;
* Monopoly strategy modeling;
* Monopoly reinforcement learning;
* trajectory logging;
* LLM-as-a-judge analysis;
* uncertainty-aware model rankings.

The research memo already draws this boundary correctly. 

## 3.3 Strongest differentiator

The strongest defensible differentiator is the combination of:

1. **Persistent rivalrous assets.** Ownership today changes future rent, trading leverage, and solvency.
2. **Multiple coupled allocation mechanisms.** Direct purchase, auction, trade, development, mortgage, liquidation, and bankruptcy interact.
3. **Enumerated legal actions.** Strategic quality can be separated from rule execution.
4. **Hard insolvency.** Failure culminates in legal liquidation and terminal transfer rather than an arbitrary task score.
5. **Communication with enforceable consequences.** Negotiation changes canonical ownership and cash.
6. **Model-call-to-state provenance.** Calls, attempts, actions, events, and snapshots can be joined.
7. **Split replay.** State correctness and full artifact fidelity are independently testable.
8. **Mechanism-level case extraction.** Full-game decisions can become frozen micro fixtures and branch states.
9. **Joint quality, reliability, and cost accounting.** The system preserves operational burden without reducing agency to tool compliance.

## 3.4 “First” language

A categorical first-ever claim is not advisable. At most, after a systematic benchmark/code audit, the paper might claim:

> To our knowledge, MonopolyBench is the first released LLM-agent benchmark to combine a rules-complete Monopoly economy, heterogeneous off-the-shelf language agents, public and private communication artifacts, legal-action enforcement, exact applied-action state replay, and per-attempt provider telemetry.

Even this formulation needs a reproducible literature-search appendix and code-level comparison against Cattle Trade, Agent Island, Market-Bench, Vending-Bench Arena, and emerging Diplomacy/social-deduction harnesses. The safer and stronger publication language is **“distinctive conjunction”**, not “first.”

# 4. Current primary-literature map with links

The map below reflects primary papers and official benchmark pages checked through July 28, 2026.

## 4.1 General agent and reliability benchmarks

| Primary source and date                                              | Established contribution                                                                                                                                         | MonopolyBench overlap                                                                      | MonopolyBench gap/addition                                                                                                |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| [AgentBench](https://arxiv.org/abs/2308.03688), August 7, 2023       | Eight interactive environments for multi-turn LLM-agent evaluation; identifies long-term reasoning, decision-making, and instruction-following failures.         | Interactive agent evaluation and trajectory failures.                                      | MonopolyBench is one deep, adversarial asset economy rather than a broad environment collection. ([arXiv][1])             |
| [τ-bench](https://arxiv.org/abs/2406.12045), June 17, 2024           | Rule-constrained tool-agent-user interaction, state-based evaluation, and repeated-trial reliability through `pass^k`.                                           | Policy compliance, tool validity, dynamic state, repeated reliability.                     | MonopolyBench adds multi-agent interference, ownership, solvency, bargaining, and bankruptcy. ([arXiv][2])                |
| [ToolPRMBench](https://arxiv.org/abs/2601.12294), January 18, 2026   | Step-level evaluation packets with interaction history, correct/chosen actions, plausible alternatives, tool metadata, multi-LLM verification, and human checks. | Direct methodological precedent for decision-level action comparison and evidence packets. | MonopolyBench can mine packets from endogenous economic trajectories and add branch values and state hashes. ([arXiv][3]) |
| [AgentRewardBench](https://arxiv.org/abs/2504.08942), April 11, 2025 | Expert-reviewed benchmark of automatic evaluators for web-agent trajectories; shows that neither rule nor LLM judges dominate universally.                       | Validates the need to calibrate downstream semantic judges.                                | MonopolyBench has deterministic state facts but still needs human-gold validation for semantic labels. ([arXiv][4])       |

## 4.2 Long-horizon and economic-agent benchmarks

| Primary source and date                                                                                                                                 | Established contribution                                                                                                                                     | MonopolyBench overlap                                                                      | MonopolyBench gap/addition                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Vending-Bench](https://arxiv.org/abs/2502.15840), February 20, 2025                                                                                    | Long-running vending-business operation over more than 20 million tokens per run; exposes derailment and coherence failures.                                 | Long-horizon economic operation, capital, pricing, inventory, and cost.                    | Long-horizon business operation is not new. MonopolyBench adds adversarial ownership, legal liquidation, rent transfer, and multiplayer bankruptcy. ([arXiv][5])             |
| [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2) and [Arena](https://andonlabs.com/evals/vending-bench-arena), released November 18, 2025 | Year-long business operation; Arena adds competing machines, communication, transfers, trade, collaboration, and price wars.                                 | This is a direct precedent for multi-agent commercial competition and misconduct analysis. | MonopolyBench offers a smaller, closed, rules-complete economy with enumerable legal actions, durable deeds, mortgages, buildings, and exact state replay. ([Andon Labs][6]) |
| [Market-Bench](https://arxiv.org/abs/2604.05523), April 7, 2026                                                                                         | Multi-agent retailers compete in procurement auctions, pricing, marketing, and buyer choice, with balance-sheet trajectories.                                | Economic competition, auctions, budgets, capital growth, semantic behavior.                | Market-Bench is broader in supply-chain realism; MonopolyBench is deeper in property-level auditability and insolvency mechanics. ([arXiv][7])                               |
| [MarketBench](https://arxiv.org/abs/2604.23897), April 26, 2026                                                                                         | Tests whether agents accurately self-report task success probability and token cost and whether auctions approximate full-information allocation.            | Cost-quality calibration and market allocation.                                            | MonopolyBench should borrow calibration analysis but studies endogenous board-state competition rather than task markets. ([arXiv][8])                                       |
| [Cattle Trade](https://arxiv.org/abs/2605.14537), May 14, 2026                                                                                          | A multi-agent economic game with auctions, hidden-offer trade challenges, bargaining, bluffing, opponent modeling, and resource discipline across 242 games. | Closest direct competitor for “economic game plus bidding, bargaining, and bluffing.”      | MonopolyBench adds standard Monopoly collateral, rent shocks, development ladders, mortgages, legal liquidation, and exact state/action replay. ([arXiv][9])                 |
| [StockBench](https://arxiv.org/abs/2510.02209), October 2, 2025                                                                                         | Multi-month trading-agent evaluation using return, maximum drawdown, and downside-risk metrics.                                                              | Sequential capital allocation and risk management.                                         | Not multiplayer and lacks enforceable bargaining/ownership transfer, but its risk-metric discipline is useful for drawdown and exposure design. ([arXiv][10])                |

## 4.3 Strategic multi-agent games and rankings

| Primary source and date                                                                             | Established contribution                                                                                                     | MonopolyBench overlap                                                            | MonopolyBench gap/addition                                                                                                                                           |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [GAMA-Bench](https://arxiv.org/abs/2403.11807), March 18, 2024                                      | Eight game-theory environments, dynamic scoring, robustness, and generalization analysis.                                    | Multi-agent strategy and game-based decision evaluation.                         | GAMA-Bench owns breadth; MonopolyBench argues depth, persistent assets, hard solvency, and replay provenance. ([arXiv][11])                                          |
| [DSGBench](https://arxiv.org/abs/2503.06047), March 8, 2025                                         | Six strategic games with fine-grained capability dimensions and decision tracking.                                           | Long-term strategic decision traces.                                             | MonopolyBench offers one substantially deeper economic mechanism stack rather than six-game breadth. ([arXiv][12])                                                   |
| [Agent Island](https://arxiv.org/abs/2605.04312), May 5, 2026                                       | Dynamic multiplayer benchmark, released logs, 999 games, 49 models, and Bayesian Plackett–Luce ranking with uncertainty.     | Multiplayer strategic ranking and behavioral log analysis.                       | It sets the methodological bar MonopolyBench must meet before publishing rankings; MonopolyBench adds richer financial and legal mechanism accounting. ([arXiv][13]) |
| [Playing repeated games with LLMs](https://www.nature.com/articles/s41562-025-02172-y), May 8, 2025 | Behavioral-game-theory study across repeated 2×2 games, with opponent effects, coordination failures, and robustness checks. | Cooperation, competition, retaliation, opponent sensitivity, framing robustness. | MonopolyBench is much less controlled but substantially richer and longer-horizon; it should borrow matched framing and robustness methodology. ([Nature][14])       |

## 4.4 Negotiation and social interaction

| Primary source and date                                                                       | Established contribution                                                                           | MonopolyBench overlap                                                                 | MonopolyBench gap/addition                                                                                                                                                                    |
| --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SOTOPIA](https://arxiv.org/abs/2310.11667), October 18, 2023                                 | Open-ended social interaction spanning coordination, collaboration, exchange, and competition.     | Social communication and mixed motives.                                               | MonopolyBench is socially narrower but has canonical economic facts, legal actions, and enforceable financial consequences. ([arXiv][15])                                                     |
| [CICERO / Diplomacy](https://www.science.org/doi/10.1126/science.ade9097), November 22, 2022  | Human-level Diplomacy through strategic reasoning and natural-language negotiation.                | Long-horizon negotiation, cooperation, competition, trust, and tactical coordination. | Diplomacy remains the stronger precedent for alliance negotiation; MonopolyBench offers off-the-shelf model auditing, exact asset accounting, cost telemetry, and bankruptcy. ([Science][16]) |
| [Deal or No Deal?](https://arxiv.org/abs/1706.05125), June 16, 2017                           | Hidden-utility multi-issue negotiation with objectively scorable agreements and dialogue rollouts. | Bargaining, hidden reservation values, and language-action coupling.                  | Its utility is much cleaner; MonopolyBench adds repeated negotiations whose outcomes alter future leverage and survival. ([arXiv][17])                                                        |
| [Measuring Bargaining Abilities of LLMs](https://arxiv.org/abs/2402.15813), February 24, 2024 | Formal asymmetric incomplete-information bargaining benchmark and deal/profit metrics.             | Offer construction, deal rates, and side asymmetry.                                   | MonopolyBench embeds bargaining inside a changing multiplayer economy and therefore requires episode and continuation-value accounting. ([arXiv][18])                                         |

## 4.5 Deception, collusion, and process-aware social behavior

| Primary source and date                                                                                                                                                          | Established contribution                                                                                                          | MonopolyBench overlap                                                           | MonopolyBench gap/addition                                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [MACHIAVELLI](https://arxiv.org/abs/2304.03279), April 6, 2023                                                                                                                   | Measures reward, ethical violations, deception, power seeking, and disutility across 134 text games.                              | Reward-safety tradeoffs and behavior labeling.                                  | MonopolyBench has narrower narratives but exact financial externalities, legal action sets, and multiplayer state consequences. ([arXiv][19])                                                           |
| [AI Deception: A Survey](https://arxiv.org/abs/2308.14752), August 28, 2023                                                                                                      | Defines deception around systematic induction of false beliefs for an outcome other than truth.                                   | Provides a high-level definition for D-label design.                            | MonopolyBench must operationalize truth, knowledge support, strategic benefit, recipient, and later action rather than infer deception from tone. ([arXiv][20])                                         |
| [Algorithmic Collusion by LLMs](https://arxiv.org/abs/2404.00806), March 31, 2024, and [Strategic Collusion of LLM Agents](https://arxiv.org/abs/2410.00031), September 19, 2024 | Demonstrate supracompetitive pricing and market-division behavior; prompt wording and auctions can matter.                        | Bid suppression, market/property allocation, reciprocity, and third-party harm. | MonopolyBench can connect coordination language to exact auctions, deeds, liquidity, and rival effects, but should call it “collusion-like game behavior,” not a legal antitrust finding. ([arXiv][21]) |
| [M3-BENCH](https://arxiv.org/abs/2601.08462), January 13, 2026                                                                                                                   | Process-aware evaluation combining behavioral trajectories, reasoning artifacts, and communication content in mixed-motive games. | Very close to MonopolyBench’s action/public/private evidence separation.        | MonopolyBench adds state authority, solvency, property-level economics, and replay; it should avoid implying process-aware social evaluation is new. ([arXiv][22])                                      |
| [Mini-Mafia](https://arxiv.org/abs/2509.23023), September 27, 2025                                                                                                               | Bayesian decomposition of deception, detection, and disclosure in a controlled social-deduction game.                             | Deception and communication role analysis.                                      | Social-deduction tasks have cleaner role-ground-truth; MonopolyBench’s ordinary bargaining requires a much higher bar for intent-like labels. ([arXiv][23])                                             |

## 4.6 Monopoly and evaluator methodology

| Primary source and date                                                                                                    | Established contribution                                                                                                 | MonopolyBench role                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Bonjour et al., hybrid DRL Monopoly](https://arxiv.org/abs/2103.00683), March 1, 2021                                     | Defines full Monopoly state/action representations and combines DRL with fixed policies for skewed decision frequencies. | Mandatory baseline/context citation. It proves full-game Monopoly decision learning predates MonopolyBench; its representations and policies should inform oracle baselines. ([arXiv][24]) |
| [Ash and Bishop, “Monopoly as a Markov Process”](https://www.tandfonline.com/doi/abs/10.1080/0025570X.1972.11976187), 1972 | Computes limit landing frequencies and expected returns under simplifying assumptions.                                   | Supports movement and expected-rent baselines, with assumptions stated rather than treated as universal ground truth. ([ResearchGate][25])                                                 |
| [From Generation to Judgment](https://arxiv.org/abs/2411.16594), November 25, 2024                                         | Taxonomy and reliability challenges for LLM-as-a-judge.                                                                  | Supports a calibrated downstream judge layer rather than unvalidated semantic scores. ([arXiv][26])                                                                                        |
| [Preference Leakage](https://arxiv.org/abs/2502.01534), February 3, 2025                                                   | Demonstrates same-model, inheritance, and same-family preference leakage in LLM judges.                                  | Requires identity masking, heterogeneous judge panels, and same-family bias audits before semantic rates enter the paper. ([arXiv][27])                                                    |

# 5. Section-by-section manuscript audit matrix

The audit below refers to line numbers in the [latest TeX draft](sandbox:/mnt/data/monopolybench_ieee_draft_v0_1.tex).

**Status codes**

* **Supported now**
* **Supported with caveat**
* **Descriptive only**
* **Future work**
* **Requires new analysis**
* **Requires balanced experiments**
* **Remove/rephrase**

| Manuscript location                                                 | Status                                   | Audit and required revision                                                                                                                                                                                               |
| ------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Title, line 30                                                      | Remove/rephrase                          | Add hyphens and avoid generic “systems.” Recommended: **“MonopolyBench: Replayable Evaluation of Long-Horizon Economic Agency in Multi-Agent Language Models.”**                                                          |
| Abstract opening, line 50                                           | Supported with caveat                    | The short-horizon critique is defensible but needs AgentBench, τ-bench, Vending-Bench, and Cattle Trade context. Do not imply most current benchmarks remain static without qualification.                                |
| “deterministic multi agent benchmark,” line 50                      | Remove/rephrase                          | Replace with **“benchmark with a deterministic-transition, replayable rules engine.”** LLM outputs are not deterministic.                                                                                                 |
| Abstract mechanics list                                             | Supported now                            | Acquisition, auctions, trades, rent, liquidity, mortgages, liquidation, and bankruptcy are implemented and visible in both runs.                                                                                          |
| “records every decision … model call, token count, and cost entry”  | Supported with caveat                    | Run A has one HTTP 503 attempt with null usage/cost. Say “records all attempts and preserves returned usage, with missing provider usage retained as null.”                                                               |
| “pair full game traces with targeted micro scenarios”               | Future work                              | The design exists, but no completed micro-suite result is attached. Say “defines a bridge to targeted fixtures” until run.                                                                                                |
| “Initial frontier model runs show winning behavior is associated …” | Remove/rephrase                          | Two different rosters cannot support an association. Replace with “Two reviewed traces illustrate distinct realized mechanisms.”                                                                                          |
| Introduction, lines 59–61                                           | Supported with caveat                    | Good motivation. Add citations and avoid implying MonopolyBench uniquely reveals compounding decisions.                                                                                                                   |
| “deterministic multi agent benchmark,” line 63                      | Remove/rephrase                          | Same determinism correction.                                                                                                                                                                                              |
| Monopoly rationale, lines 63–65                                     | Supported now                            | Good bounded framing. Add rules citation and explicitly call Monopoly stylized.                                                                                                                                           |
| Legal-action separation, line 67                                    | Supported with caveat                    | Correct architecture. Replace “rules engine is authoritative and deterministic” with conditional replay language.                                                                                                         |
| Full-game and micro modes, line 69                                  | Supported with caveat/Future work        | Full-game mode is demonstrated. Micro mode is designed but not empirically executed.                                                                                                                                      |
| Contribution 1, line 74                                             | Remove/rephrase                          | Replace “deterministic benchmark” with “replay-oriented benchmark with an authoritative deterministic-transition engine.”                                                                                                 |
| Contribution 2, line 75                                             | Supported with caveat                    | Metric framework exists, but many advanced measures are not implemented. Add availability labels or limit to current descriptive metrics.                                                                                 |
| Contribution 3, line 76                                             | Future work                              | Scenario-suite design is a methodological contribution; do not imply released results.                                                                                                                                    |
| Contribution 4, line 77                                             | Supported now                            | Artifact pipeline is real and demonstrated. Mention split replay and missingness preservation.                                                                                                                            |
| Contribution 5, line 78                                             | Descriptive only                         | Recast as two exhaustive case studies, not “frontier model results” in a comparative sense.                                                                                                                               |
| Contribution 6, line 79                                             | Remove/rephrase                          | The current memo explicitly requires branch/oracle tiers. Replace with “descriptive-first evaluation supplemented by declared, sensitivity-tested counterfactual oracles.”                                                |
| Related work: AgentBench/τ-bench                                    | Supported with caveat                    | Expand to distinguish broad interactive evaluation, rule-following reliability, and MonopolyBench’s persistent multiplayer economy.                                                                                       |
| Related work: long-horizon economic simulation                      | Requires revision                        | Add Vending-Bench 2/Arena, Market-Bench, MarketBench, Cattle Trade, Agent Island, and StockBench.                                                                                                                         |
| Related work: social behavior, lines 103–107                        | Requires revision                        | Add SOTOPIA, CICERO, Deal or No Deal, repeated games, collusion work, MACHIAVELLI, Mini-Mafia/social deduction, and judge reliability.                                                                                    |
| Monopoly Markov claim, line 111                                     | Remove/rephrase                          | The claim that several color groups are generally strongest and three houses are valuable is too compressed and source-sensitive. Cite Ash–Bishop precisely and state assumptions.                                        |
| Monopoly DRL, lines 111–113                                         | Supported now                            | Bonjour et al. is the required comparison. Add that it uses trained policies against fixed-policy agents, whereas MonopolyBench audits off-the-shelf language agents.                                                     |
| Task definition, lines 118–122                                      | Supported now                            | Add finite house inventory and clarify endpoint semantics for turn caps.                                                                                                                                                  |
| Six-component architecture, lines 124–135                           | Supported now                            | Strong section. Add directional arrows and identify telemetry as downstream/read-only.                                                                                                                                    |
| Architecture figure plan                                            | Requires new analysis/design             | Publishable now after producing a clean diagram. Must visually separate stochastic/provider model calls from deterministic state mutation.                                                                                |
| Decision loop, lines 145–160                                        | Supported now                            | Add attempt indexing, retry/fallback source, pre/post state hashes, and the rule that only applied actions mutate state.                                                                                                  |
| State/private rationale, lines 162–177                              | Remove/rephrase                          | Replace “private rationale” with **“model-reported private analysis field.”** Do not describe it as cognition.                                                                                                            |
| Artifact list, lines 179–195                                        | Requires revision                        | Add `state_replay_report.json`, `artifact_replay_report.json`, `usage_attempts.jsonl`, request/response hashes, manifests, source hashes, and evidence indexes.                                                           |
| Evaluation philosophy, lines 200–213                                | Supported with caveat                    | The trajectory is the substantive object, but the independent inferential unit is the seed block. Add endpoint hierarchy and units.                                                                                       |
| Outcome metrics, lines 215–234                                      | Supported with caveat                    | Define terminal winner separately from net worth; define net-worth convention; distinguish playable turn count from terminal marker.                                                                                      |
| Economic metrics, lines 236–255                                     | Supported with caveat                    | Add AUC definitions, censoring, opportunity denominators, legal liquidity, and metric provenance.                                                                                                                         |
| Market/negotiation metrics, lines 257–276                           | Supported with caveat                    | Use canonical negotiation episodes rather than raw proposal events. List price and downstream rent do not establish value.                                                                                                |
| Liquidity/collapse, lines 278–294                                   | Requires new analysis                    | Legal liquidity, solvency margin, and “preserved a path to survival” need an engine-side liquidation optimizer or branch oracle.                                                                                          |
| Social metrics, lines 296–313                                       | Supported with caveat                    | Candidate extraction is possible; prevalence or D/C conclusions need human adjudication. Add D0–D4 and C0–C4 operational standards.                                                                                       |
| Cost/reliability, lines 315–333                                     | Supported now with caveat                | Preserve raw token semantics, attempts versus decisions, missing usage, provider routes, and survivor-dependent exposure.                                                                                                 |
| Metric taxonomy table                                               | Requires revision                        | Split into primary endpoints, secondary mechanisms, diagnostics, exploratory behavioral labels, and oracle-dependent metrics.                                                                                             |
| Micro-suite purpose, lines 353–371                                  | Future work                              | Strong rationale. Reframe “includes” as “will include” until a frozen suite exists.                                                                                                                                       |
| Micro category table                                                | Future work                              | Placeholder counts must not appear in submitted paper. Add fixture IDs, source runs, context variants, repetitions, and action-order randomization.                                                                       |
| Micro scoring, lines 399–410                                        | Remove/rephrase                          | Replace subjective `preferred/acceptable/risky/trap` as the primary scheme with legality, branch-value/regret, robustness, and human-reviewed communication components. Rubrics may remain for explicitly clear fixtures. |
| Run A opening, line 435                                             | Remove/rephrase                          | “Apparent winner,” “583 model calls,” and “replay reconciliation pending” are stale. Correct to 583 decisions, 604 attempts, exact winner, and exact split status.                                                        |
| Run A final table                                                   | Requires source-table verification       | Winner cash is verified. Terminal net worth, property/building counts, and liabilities need named table provenance and valuation version. Terminal post-bankruptcy ownership also includes creditor transfers.            |
| Run A usage table                                                   | Partly supported                         | Per-player decision/invalid counts are supported by the review. Costs/tokens need direct generated-table provenance. “Calls” must mean attempts, not decisions.                                                           |
| Run A rent table                                                    | Requires source-table verification       | Do not publish until reconciled to a named rent-flow table and event totals. Even then, label as realized-path, dice-dependent transfer totals.                                                                           |
| Run A mechanism prose                                               | Descriptive only                         | Replace broad “negotiation dominance” with exact Pink completion, T79 consolidation, green development, and bankruptcy-window evidence.                                                                                   |
| Run B opening, line 496                                             | Supported with revision                  | State “273 playable turns, terminal-only marker 273.” Report both state and full artifact replay.                                                                                                                         |
| Run B token/final-net tables                                        | Requires source-table verification       | Cost is verified. Total tokens, final net worth, and per-player values need table provenance and valuation definitions.                                                                                                   |
| Run B rent/development prose                                        | Descriptive only                         | Mechanism is supported, but exact aggregate rent and portfolio totals need generated-table provenance.                                                                                                                    |
| Cross-run pattern, lines 561–577                                    | Descriptive only                         | “Winner converted asset control into rent pressure” is an observation from two traces, not a general association. Keep as a hypothesis-generation paragraph.                                                              |
| “Descriptive rather than oracle,” lines 579–596                     | Remove/rephrase                          | Preserve transparency argument, but add tiered counterfactual evaluation. Regret, trade surplus, and avoidable bankruptcy cannot remain permanently unmeasured.                                                           |
| Full-game protocol, lines 603–615                                   | Remove/rephrase                          | The current request policy omitted temperature and `max_tokens`. Record omission as a request fact; do not rewrite it as “fixed temperature.”                                                                             |
| Seat permutation, line 617                                          | Supported now as design                  | Expand from seat rotation to seed blocks, model-by-seed interactions, route/date controls, and roster-relative estimands.                                                                                                 |
| Micro protocol                                                      | Future work                              | Add repeated queries, full/compressed/minimal context, action-order counterbalancing, identity masking, branch policy, and oracle version.                                                                                |
| Claim-gating table                                                  | Requires revision                        | Separate state replay from artifact replay. A “strategic profile” cannot be generalized from repeated decisions in one run. Add case-study, replicated, and paper-claim levels.                                           |
| Figure 1 architecture                                               | Publishable now                          | Generate immediately.                                                                                                                                                                                                     |
| Figures 2–4 trajectories/rent/development                           | Descriptive only                         | Publishable as case-study figures with exact run IDs, replay caveats, and source-table metadata.                                                                                                                          |
| Figure 5 trade network                                              | Requires new deterministic export/polish | Can be descriptive now if based on canonical episodes. It must not imply surplus.                                                                                                                                         |
| Figure 6 auction behavior                                           | Descriptive now; oracle later            | Bid/deed-price/liquidity plot is possible. “Overbid” or winner’s curse requires WTP oracle.                                                                                                                               |
| Figure 7 cost/latency                                               | Supported now                            | Add raw token semantics, usage coverage, and common-horizon caveat.                                                                                                                                                       |
| Figure 8 micro results                                              | Future work                              | No data yet.                                                                                                                                                                                                              |
| Discussion, lines 676–680                                           | Remove/rephrase                          | Replace “apparent victory,” aggregate profiles, and comparative tone with exact reviewed mechanisms.                                                                                                                      |
| Full-game/micro discussion, lines 682–693                           | Supported with caveat                    | Good methodological argument; distinguish demonstrated full games from planned fixtures.                                                                                                                                  |
| Economic-agency list, lines 695–711                                 | Supported as construct definition        | Present as operational dimensions, not validated latent traits.                                                                                                                                                           |
| Reliability discussion, lines 713–717                               | Supported with caveat                    | Reliability is not merely instrumentation; it is a deployment endpoint and may alter trajectories through fallback actions and cost.                                                                                      |
| Limitation: stylized economy                                        | Supported now                            | Retain and strengthen external-validity caveat.                                                                                                                                                                           |
| Limitation: no ranking                                              | Supported now                            | Add fixed-roster and provider/date relativity.                                                                                                                                                                            |
| Limitation: replay, lines 730–732                                   | Remove/rephrase                          | A state-pass/artifact-fail run can support state-grounded figures. State which artifact family each claim requires rather than requiring universal “replay clean.”                                                        |
| Limitation: context-dependent strategy                              | Supported now                            | Add declared oracle tiers rather than permanent avoidance.                                                                                                                                                                |
| Limitation: social labels                                           | Supported now                            | Add human-gold, double-coding, adjudication, and judge-bias requirements.                                                                                                                                                 |
| Ethics                                                              | Supported with caveat                    | Replace “ethical track” speculation with a clearly separate intervention condition if implemented. Never use game collusion language as a legal conclusion.                                                               |
| Conclusion, lines 753–760                                           | Remove/rephrase                          | Correct determinism and replace two-winner strategic-profile claims with pipeline and mechanism-case evidence.                                                                                                            |
| Bibliography                                                        | Requires major revision                  | Add primary sources above; remove incomplete HBR entry; replace weak Markov citation; archive mutable official pages with access dates; verify Beer Game relevance before retaining.                                      |
| Draft notes, lines 814–845                                          | Stale                                    | Run A no longer awaits general reconciliation; it has an exact split result. Candidate case-study slots are now filled by the attached evidence packages.                                                                 |

# 6. Mathematical and statistical design

## 6.1 Experimental condition and units

Define an experimental condition

[
c =
(\mathcal M, P, R, \rho, \iota, e, d),
]

where:

* (\mathcal M) is the four-model roster;
* (P) is the prompt and communication policy;
* (R) is the rules/action-schema version;
* (\rho) is the provider routing and fallback policy;
* (\iota) is the identity condition, such as anonymous or named;
* (e) is the endpoint policy;
* (d) is the bounded date/model-version window.

The outcome of model (m) is inherently **roster-relative**. Opponent behavior changes auctions, trades, rents, and survival. The potential outcome is therefore closer to

[
Y_m(s,\mathcal M_{-m},c,\xi)
]

than to an isolated treatment response, where (s) is seat and (\xi) is the exogenous stochastic schedule.

The required hierarchy is:

[
\text{experiment}
\supset
\text{seed block}
\supset
\text{game}
\supset
\text{player-game}
\supset
\text{turn}
\supset
\text{decision}
\supset
\text{attempt}.
]

Decisions and attempts are repeated measurements, not independent replicates. The independent design unit for the primary full-game comparison is the **seed block**.

For a four-model roster, each seed block contains four cyclic seat rotations. Across blocks, the base permutation and exogenous seed bundle vary.

## 6.2 Eligibility sets

Every rate needs a declared eligibility set.

For model-required decisions of type (q),

[
\mathcal D_{m,q}
================

{d:
model(d)=m,,
type(d)=q,,
d \text{ required a model call},,
run(d) \text{ passes the applicable integrity gate}
}.
]

For trade initiation,

[
\mathcal E^{trade,init}_{m}
===========================

{e:
m \text{ authored the initial canonical proposal in episode } e}.
]

For auctions,

[
\mathcal E^{auction,elig}_{m}
=============================

{e:
m \text{ was alive and legally permitted to bid in auction } e}.
]

Counters are descendants of an initial proposal and do not inflate the initial-proposal denominator. Unresolved episodes stay unresolved; they are not silently converted to rejection.

## 6.3 Placement and survival

### Placement likelihood

Let (\pi_g=(\pi_{g1},\ldots,\pi_{gJ})) be final placement in game (g), winner first. A hierarchical Plackett–Luce model is

[
P(\pi_g\mid\boldsymbol\eta_g)
=============================

\prod_{k=1}^{J-1}
\frac{\exp(\eta_{\pi_{gk},g})}
{\sum_{\ell=k}^{J}\exp(\eta_{\pi_{g\ell},g})}.
]

Use

[
\eta_{m,g}
==========

\alpha_m
+
\gamma_{seat(m,g)}
+
\delta_{\rho(g)}
+
\kappa_{date(g)}
+
u_{m,b(g)},
]

where (u_{m,b}\sim N(0,\sigma^2_{\text{model}\times\text{seed}})) captures model-specific seed sensitivity. A common block intercept would cancel from a Plackett–Luce choice denominator and therefore does not identify seed heterogeneity; the random effect must vary by model or contrast.

Report:

* posterior mean ability differences;
* pairwise beat probabilities;
* 95% credible intervals;
* probability of each rank;
* probability that each model is top-ranked;
* sensitivity excluding route fallbacks or integrity-caveated games.

Do not report a single sorted list without uncertainty.

### Pairwise alternative

Define

[
Y_{mn,g}=I(rank_{m,g}<rank_{n,g}).
]

A Bradley–Terry composite model is

[
\operatorname{logit}P(Y_{mn,g}=1)
=================================

(\alpha_m-\alpha_n)
+
(\gamma_{s_m}-\gamma_{s_n})
+
(u_{m,b}-u_{n,b}).
]

The six pairwise outcomes from one four-player game are dependent. Use seed-block bootstrap or cluster-robust inference; do not treat them as six independent games.

### Turn-cap games

A bankruptcy game and a turn-limit game estimate different endpoints. For capped games:

* surviving players are censored for bankruptcy-time analysis;
* placement rules must be declared before running;
* a net-worth winner must not be pooled with last-survivor winners without an endpoint indicator or separate analysis;
* ties require a tie-capable ranking likelihood.

## 6.4 Net worth and AUC

Define a versioned accounting convention:

[
NW_{i,t}
========

C_{i,t}
+
P^{book}*{i,t}
+
B^{book}*{i,t}
--------------

M_{i,t}.
]

The paper must state whether:

* deeds use printed price, purchase basis, or another value;
* buildings use purchase cost or liquidation value;
* mortgage liability is principal only or principal plus immediate interest;
* transferred assets are valued before or after creditor fees.

A second quantity should be reported:

[
NW^{liq}_{i,t}
==============

C_{i,t}
+
L^{unilateral}_{i,t},
]

where (L^{unilateral}) is realizable cash under legal immediate unilateral liquidation. This is distinct from accounting net worth.

### Game-horizon AUC

Let (t_0<\cdots<t_K=T_g) be canonical checkpoints. Define (\widetilde{NW}_{i,t}=0) after bankruptcy:

[
AUC^{game}_{i,g}
================

\frac{1}{T_g-t_0}
\sum_{k=1}^{K}
\frac{
\widetilde{NW}*{i,t*{k-1}}
+
\widetilde{NW}*{i,t_k}
}{2}
(t_k-t*{k-1}).
]

This incorporates both wealth and survival and is a defensible co-primary endpoint.

### Alive-only AUC

[
AUC^{alive}_{i,g}
=================

\frac{1}{\tau_{i,g}-t_0}
\int_{t_0}^{\tau_{i,g}}NW_i(t),dt,
]

where (\tau_i) is bankruptcy or game end. This can make an early bankrupt player with a briefly strong position look good, so it should be secondary and never substituted for game-horizon AUC.

### Common-horizon AUC

For a predeclared (h),

[
AUC^{h}_{i,g}
=============

\frac{1}{h}
\int_0^h \widetilde{NW}_i(t),dt.
]

This supports early/midgame comparison without giving longer games more opportunities. The horizon must be preregistered, not chosen after inspecting model separation.

### Outcome model

For continuous player-game outcomes:

[
Y_{m,b,r}
=========

\mu
+
\alpha_m
+
\gamma_{seat(m,b,r)}
+
u_b
+
v_{b,r}
+
\epsilon_{m,b,r}.
]

Because four outcomes within one game are correlated and sometimes nearly compositional, use either:

* a multivariate residual structure;
* within-game centered outcomes;
* or a seed-block cluster bootstrap.

Terminal net worth in bankruptcy games has structural zeros for eliminated players. Treat it as descriptive or use a two-part survival/conditional-value model. Do not fit an ordinary Gaussian model and treat all zeroes as continuous measurements.

Also report the **pre-transfer exit estate**:

[
Estate^{exit}*i =
NW*{i,\tau_i^-},
]

which is often more informative about the mechanism of bankruptcy than the canonical terminal zero.

## 6.5 Bankruptcy hazard

At each eligible player-turn interval, define

[
B_{i,g,t+1}
===========

I(i\text{ becomes bankrupt before the next checkpoint}),
]

conditional on (i) being alive at (t).

A discrete-time complementary-log-log model is

[
\log[-\log(1-h_{i,g,t})]
========================

\lambda(t)
+
\alpha_{model(i)}
+
\gamma_{seat(i,g)}
+
\boldsymbol\beta^\top X_{i,g,t^-}
+
u_{b(g)}
+
v_g,
]

where (X_{t^-}) may include:

* legal liquidity;
* risk-adjusted solvency margin;
* rent exposure;
* mortgage ratio;
* recent shock magnitude;
* development concentration;
* phase;
* opponent rent power.

Use lagged pre-event covariates only. The winner is right-censored at game end. Survivors in capped games are also censored.

This is a **predictive mechanism model**, not a causal model. Liquidity, development, and mortgage states are consequences of prior model actions and opponent behavior. A coefficient on legal liquidity does not identify the causal effect of “holding one more dollar.”

## 6.6 Legal liquidity and risk

Define the legal unilateral liquidation set (\mathcal L_i(s)). It must obey:

* even selling;
* hotel-to-house bank inventory constraints;
* improvement removal before mortgage;
* property ownership and mortgage rules;
* ruleset-specific interest.

Then

[
L_i(s)
======

C_i(s)
+
\max_{\ell\in\mathcal L_i(s)}
CashRaised(\ell).
]

Immediate solvency margin is

[
SM^{now}_{i,t}
==============

L_i(s_t)-DueNow_{i,t}.
]

For horizon (H), define a distribution of future obligations (O_{i,t:t+H}). With upper-tail expected shortfall,

[
SM^{risk}_{i,t,H,\alpha}
========================

## L_i(s_t)

ES_{\alpha}(O_{i,t:t+H}).
]

The implementation must state:

* movement model;
* opponent policies;
* horizon;
* whether multiple landings are counted;
* card/jail assumptions;
* tail convention;
* Monte Carlo error.

Until that exists, use **cash**, **known debt**, **mortgageable assets**, and **realized shock windows**, not a fabricated “liquidity-at-risk” value.

## 6.7 Reliability without pseudoreplication

Classify each model-required decision into mutually exclusive final process states:

1. `first_pass_valid`;
2. `retry_recovered`;
3. `fallback_applied`;
4. `unresolved_provider_or_validator_failure`.

For decision (d),

[
V_d = I(\text{attempt 0 parsed, satisfied schema, and matched a legal action}).
]

First-pass validity is

[
FPV_m
=====

\frac{\sum_{d\in\mathcal D_m}V_d}
{|\mathcal D_m|}.
]

Retry recovery is

[
Recovery_m
==========

\frac{
#{d:V_d=0,\exists k>0\text{ valid model attempt}}
}{
#{d:V_d=0}
}.
]

Fallback dependency is

[
Fallback_m
==========

\frac{#{d:\text{applied action source is deterministic fallback}}}
{|\mathcal D_m|}.
]

A mixed logistic model for first-pass validity is

[
\operatorname{logit}P(V_d=1)
============================

\alpha_{model(d)}
+
\beta_{type(d)}
+
\beta_1\log(1+|A_d|)
+
\beta_2 contextTokens_d
+
\beta_3 phase_d
+
u_{block}
+
u_{game}
+
u_{player\text{-}game}.
]

Two estimands should be distinguished:

* **Ecological reliability:** reliability on the decisions a model’s own trajectory generated.
* **Standardized reliability:** predicted reliability under a common fixture or common decision-type distribution.

The ecological estimate is operationally real but confounded by post-treatment decision mix. The standardized estimate requires adequate overlap and should preferably use the micro suite.

## 6.8 Regret with oracle uncertainty

Let (Q_{d,a,k}) be the value of action (a) for endpoint (k), such as:

* survival probability at horizon (H);
* win probability;
* expected net worth at (H);
* expected solvency margin.

Do not collapse these into one scalar unless weights are declared in advance.

Given branch/oracle posterior draw (\ell),

[
R_{d,k}^{(\ell)}
================

## \max_{a\in A_d}Q_{d,a,k}^{(\ell)}

Q_{d,a_d,k}^{(\ell)}.
]

Report:

* posterior median regret;
* 95% interval;
* (P(R_{d,k}\le\epsilon_k));
* action-value range;
* oracle tier and continuation policy.

Normalized regret is

[
R^{norm}_{d,k}
==============

\frac{R_{d,k}}
{Q^{max}*{d,k}-Q^{min}*{d,k}}.
]

If the denominator is below an oracle-resolution threshold, mark the decision `value_indistinguishable`; do not manufacture a precise normalized value.

Full-game regret is an ecological process measurement because models encounter different states. Comparative regret should primarily use a common frozen fixture set:

[
R_{m,f,r}
=========

\alpha_m+\delta_{family(f)}+u_f+\epsilon_{m,f,r}.
]

Fixture, not response, is the replication structure.

## 6.9 Trade and auction denominators

### Trade funnel

For model (m):

[
Acceptance^{init}_m
===================

\frac{
#\text{accepted episodes initiated by }m
}{
#\text{terminal episodes initiated by }m
}.
]

Also report:

[
Yield^{proposal}_m
==================

\frac{
#\text{accepted initiated episodes}
}{
#\text{all initial proposals}
},
]

which keeps unresolved episodes in the denominator.

Received-offer acceptance is

[
Acceptance^{recv}_m
===================

\frac{
#\text{accepted offers received}
}{
#\text{terminal response-eligible offers received}
}.
]

Report accepted, rejected-without-counter, countered, expired, withdrawn, invalidated, and unresolved counts separately.

For resolution outcome, use a multinomial model or cause-specific discrete hazard over exchange number. Do not drop unresolved episodes.

### Auction funnel

[
Entry_m
=======

\frac{#\text{auctions entered}}
{#\text{auctions legally eligible}},
]

[
WinGivenEntry_m
===============

\frac{#\text{auction wins}}
{#\text{auctions entered}}.
]

Bid/deed-price ratios, bid increments, and liquidity consumed are descriptive. They do not establish overpayment. Winner’s curse requires state-specific willingness to pay:

[
v_i(s,p)
========

\sup_b
\left{
b:
Q_i(s^{win}(p,b))
\ge
Q_i(s^{drop})
\right}.
]

### Trade value

For accepted trade (e),

[
\Delta Q_{i,e}
==============

Q_i(s^{after}_e)-Q_i(s^{before}_e).
]

Then:

[
Surplus_e
=========

\Delta Q_{proposer,e}
+
\Delta Q_{counterparty,e},
]

[
Externality_e
=============

\sum_{j\notin parties(e)}\Delta Q_{j,e}.
]

These quantities are oracle-dependent. Deed price, realized later rent, and private prose are not substitutes.

## 6.10 Cost-quality relationships

Let (c) index model-call attempts and (Cost_c) be returned provider/gateway cost.

Player cost through common horizon (h) is

[
C_{i,g}(h)
==========

\sum_{c:
player(c)=i,,
turn(c)\le \min(h,\tau_i)}
Cost_c.
]

Report:

* total recorded cost;
* cost per model-required decision;
* cost per first-pass-valid decision;
* retry/invalid cost share;
* common-horizon cumulative cost;
* cost while at risk;
* top-tail cost and latency share.

Do not interpret low terminal cost as efficiency without survival context. A bankrupt player makes fewer future calls.

Avoid using `cost / net-worth AUC` as the sole efficiency measure. Ratios become unstable when the denominator is small and obscure the joint outcome. Prefer:

* quality-cost scatterplots;
* Pareto frontiers;
* model effects at fixed quality or cost;
* or net benefit (Quality-\lambda Cost) across a sensitivity range of declared (\lambda).

An observational full-game model can be written as

[
Quality_d
=========

\alpha_{model}
+
\beta_1\log(1+Cost_d)
+
\beta_2 context_d
+
\beta_3|A_d|
+
\beta_4 type_d
+
u_{block}
+
u_{game}
+
u_{player\text{-}game}
+
\epsilon_d.
]

This estimates association, not the causal effect of spending or reasoning. Difficult decisions may elicit more tokens and still receive worse actions.

A causal reasoning-effort result requires a randomized fixture experiment:

[
Effort\in{\text{low},\text{medium},\text{high}}
]

assigned within model-fixture pairs, with identical state, action order randomization, repeated calls, and provider semantics preserved.

OpenRouter currently documents reasoning tokens as output tokens for billing and notes that providers differ in whether reasoning content is exposed. Raw `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `total_tokens`, and cost must therefore be retained without double counting. ([OpenRouter][28]) Routing and fallback policy are also treatment metadata, because OpenRouter can prioritize, restrict, or fall back across providers. ([OpenRouter][29])

## 6.11 Micro-to-full concordance

The original full-game action is one stochastic realization. Therefore, exact match to that one action is descriptive, not a stable ground truth.

For fixture (f), estimate action distributions under repeated full-context and micro-context queries:

[
\widehat p^{full}_f(a),
\qquad
\widehat p^{micro}_f(a).
]

Original-action concordance is

[
FMC^{orig}
==========

\frac1N\sum_{f=1}^N
\widehat p^{micro}_f(a_f^{original}).
]

Distributional concordance is

[
DC
==

1-
\frac1N\sum_f
\frac12\sum_{a\in A_f}
\left|
\widehat p^{full}_f(a)
----------------------

\widehat p^{micro}_f(a)
\right|.
]

Value loss from context compression is

[
\Delta V_f
==========

## E_{a\sim \widehat p^{micro}_f}[Q_f(a)]

E_{a\sim \widehat p^{full}_f}[Q_f(a)].
]

Epsilon-optimality must be reported independently:

[
EO^{micro}
==========

\frac{1}{NR}
\sum_{f,r}
I(Q_f^*-Q_f(a_{f,r}^{micro})\le\epsilon_f).
]

A model can be action-inconsistent but value-consistent when several actions are near-equivalent.

The current memo’s aggregate value-concordance formula can be dominated by high-swing fixtures and can become negative. Prefer the fixture-normalized form

[
VC
==

1-
\frac1N\sum_f
\frac{
\left|
Q_f(a_f^{full})
---------------

R^{-1}\sum_r Q_f(a_{f,r}^{micro})
\right|
}{
Q_f^{max}-Q_f^{min}+\epsilon_0
}.
]

Report raw normalized absolute error as well; clipping a display score to ([0,1]) must not hide poor performance.

## 6.12 Branch-counterfactual estimands

For fixed continuation policy (\pi) and common exogenous schedule (\xi),

[
\Delta_H^{controlled}(a,b;\pi,\xi)
==================================

## U_i(s_H^{a,\pi,\xi})

U_i(s_H^{b,\pi,\xi}).
]

This is a controlled action effect under a declared continuation.

A natural-response estimand re-queries agents after divergence:

[
\Delta_H^{natural}(a,b)
=======================

E[
U_i(s_H^{a,\Pi^a,\Xi^a})
------------------------

U_i(s_H^{b,\Pi^b,\Xi^b})
].
]

It is behaviorally more realistic but combines focal-action effect, opponent adaptation, and new model stochasticity.

Report:

* one-step exact accounting;
* recorded-continuation where still legal;
* scripted-policy results;
* heuristic/RL policy ensemble;
* re-queried-agent results;
* policy-robust min/mean/max interval.

A sequential mutable RNG is inadequate for paired branches when one action changes the number of random draws. Use counter-based or subsystem-specific random streams keyed by turn, player, subsystem, and draw index.

## 6.13 Multiple testing and rank uncertainty

Recommended confirmatory hierarchy:

1. **Co-primary endpoint 1:** placement/survival ordering.
2. **Co-primary endpoint 2:** game-horizon net-worth AUC.
3. **Key secondary:** first-pass validity, legal liquidity/hazard, trade and development mechanisms.
4. **Exploratory:** D/C labels, bias probes, detailed action families.

Use Holm correction across the two co-primary omnibus tests or a predeclared closed-testing procedure. Pairwise model contrasts are tested only after the corresponding omnibus model effect.

Within secondary families, apply Benjamini–Hochberg FDR separately to:

* capital allocation;
* liquidity;
* auction behavior;
* trade/negotiation;
* reliability/cost;
* strategic communication;
* bias perturbations.

Always report effect estimates and intervals before adjusted (q)-values.

Rank reporting should include:

* posterior rank probabilities;
* pairwise superiority probabilities;
* expected rank;
* credible intervals;
* sensitivity by seat, route, date, prompt version, and fallback policy.

## 6.14 Sample size and power strategy

No defensible fixed (N) can be computed from the two current games. They use different rosters and are not replicate seed blocks.

Use simulation-based design:

1. **Choose smallest effects of scientific interest.** Define them on native scales, such as a pairwise beat-probability difference, a net-worth-AUC difference, or a first-pass-validity difference.
2. **Run an internal calibration batch.** An operational starting batch of 8–12 seed blocks, or 32–48 games, is reasonable for variance calibration but is not itself a claim of power.
3. **Estimate nuisance parameters blindly.** Estimate seat effects, model-by-seed variance, within-game dependence, event rates, AUC dispersion, and integrity-exclusion rates without examining confirmatory model contrasts.
4. **Simulate full campaigns.** For each candidate block count (B), generate at least 5,000 synthetic campaigns under:

   * null effects;
   * smallest meaningful effects;
   * weak/moderate/strong seat effects;
   * low/high model-by-seed interaction;
   * provider drift and missing-run scenarios.
5. **Run the exact planned analysis** on every synthetic campaign.
6. **Select the smallest (B)** satisfying all preregistered criteria:

   * familywise type-I error at or below 0.05;
   * at least 0.90 power for the smallest meaningful primary effect;
   * at least 0.90 interval coverage;
   * acceptable rank-probability calibration;
   * predeclared CI-width or credible-interval precision targets.
7. **Use blinded sample-size re-estimation** after the calibration batch if needed. Do not stop based on observed model winners.
8. **Set a maximum block and budget cap** before confirmatory analysis.

For rare D/C behaviors, full-game prevalence studies will be inefficient. Use enriched frozen fixtures for detection and retain full games for ecological case discovery.

# 7. Canonical Run A and Run B evidence/claim ledger

## 7.1 Run A — `mock-83265-81ed4937`

| Claim                                                                                                           | Exact evidence                                                                                       | Strength                                     | Caveat                                                                                           |
| --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| GPT 5.5 is the canonical winner                                                                                 | Final `turn_0191.json`; bankruptcy endpoint; winner cash $718                                        | Canonical fact                               | Checkpoint 191 is terminal-only; playable turns are 0–190.                                       |
| Replay status is `state_passed_artifact_failed`                                                                 | `state_replay_report.json`; `artifact_replay_report.json`; first mismatch `evt-000669`, `dec-000096` | Canonical fact                               | Never call this a full artifact pass.                                                            |
| 583 decisions/actions, 604 attempts, 21 retry decisions, 23 invalid attempts, 2 fallbacks                       | Integrity and review reconciliation                                                                  | Canonical fact                               | Decisions, attempts, and calls must not be conflated.                                            |
| Recorded cost is $27.71173045                                                                                   | Reconciled usage/cost artifacts                                                                      | Canonical fact                               | One HTTP 503 attempt has null usage/cost and is not estimated.                                   |
| Pink completion created the first major rent engine                                                             | `dec-000040..000074`; `evt-000313..000524`; `turn_0025..0027`                                        | Reviewed mechanism case                      | No branch proves that every enabling trade was irrational for the counterparties.                |
| GPT converted Virginia plus asset recycling into 3/3/3 Pink                                                     | B&O+$250 trade, mortgages/sales, nine-house build                                                    | Canonical sequence plus interpretation       | Exact continuation value remains unknown.                                                        |
| Park Place auction imposed a $650 liquidity burden on Gemini                                                    | `dec-000081..000093`; `evt-000578..000652`                                                           | Canonical mechanism                          | $650/list-price ratio does not itself prove overpayment.                                         |
| T33 light-blue thread caused the strict artifact mismatch                                                       | `dec-000095/000096`; `evt-000669/000672`                                                             | Canonical fact                               | Fallback delayed the eventual valid T35 deal; downstream materiality beyond that is unestimated. |
| Claude and Gemini later exchanged Connecticut for $280                                                          | `dec-000099..000103`; `evt-000696..000719`                                                           | Canonical fact                               | Bilateral surplus not computed.                                                                  |
| T79 was a 51-decision consolidation market                                                                      | `dec-000279..000329`; `evt-001858..002135`; `turn_0079*`                                             | Canonical fact                               | Order effects are untested.                                                                      |
| GPT spent $1,180 cash plus utilities/card and acquired New York, St. James, Marvin, Pacific, and North Carolina | T79 actions and trade events                                                                         | Canonical fact                               | It obtained pairs/blockers, not an immediate new color monopoly.                                 |
| Counterparties independently retained decisive blockers                                                         | Rejected Tennessee, red, dark-blue, and other structures                                             | Reviewed interpretation                      | No evidence of a coordinated anti-GPT agreement.                                                 |
| Claude’s light-blue house occupancy contributed to house scarcity                                               | `dec-000340..000344`, later bank inventories                                                         | Observed mechanism                           | No counterfactual quantifies scarcity’s marginal effect.                                         |
| GPT’s repeated T99 attempts to trade improved dark blues were rule failures                                     | `dec-000386`, `000387`, `000391`                                                                     | Canonical reliability fact                   | Invalid proposals were never applied.                                                            |
| GPT’s green development became the elimination engine                                                           | `dec-000412..000421`, `000427`; later rent events                                                    | Reviewed realized-path mechanism             | Landing outcomes remain stochastic.                                                              |
| Grok’s T113 bankruptcy followed fragmented collateral and North Carolina rent                                   | `dec-000379..381`, `000430..431`; `evt-002488..2510`, `002839..2855`                                 | Canonical immediate cause                    | Earlier sale/trade paths are counterfactual.                                                     |
| Gemini’s T126 bankruptcy followed dark-blue build/unwind and exhausted legal action surface                     | `dec-000369..000473`; `evt-003111..3124`                                                             | Canonical immediate cause                    | Earlier asset-allocation alternatives are untested.                                              |
| Claude’s final collapse followed T177/T179 green rents and T190 Pacific obligation                              | `dec-000531..000582`; `evt-003556..3971`                                                             | Canonical chain plus reviewed interpretation | It does not prove every prior blocker-retention decision was wrong.                              |
| No D3 supported intentional falsehood                                                                           | Exhaustive review                                                                                    | Reviewed case conclusion                     | Not a prevalence estimate and not yet a human-gold rate.                                         |
| No C3 implemented collusion/noncompetition                                                                      | Exhaustive review                                                                                    | Reviewed case conclusion                     | C0/C1 ordinary exchange and isolated C2-like proposals remain distinct.                          |

Run A’s complete qualitative reconciliation and case narratives support these entries.  

## 7.2 Run B — `mock-44910-42ec35c5`

| Claim                                                                        | Exact evidence                                                      | Strength                        | Caveat                                                                                    |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------- |
| Gemini 3 Flash Preview is the canonical winner                               | `evt-004101`, terminal snapshot, winner cash $3,921                 | Canonical fact                  | Checkpoint 273 is terminal-only; playable turns are 0–272.                                |
| Both replay layers pass                                                      | 1,942 state events; 4,102 full artifact events                      | Canonical fact                  | Legacy manifest drift remains documented but is not a replay blocker.                     |
| 540 decisions/actions, 549 attempts, 9 invalid first attempts, 0 fallbacks   | Integrity and review reconciliation                                 | Canonical fact                  | Retry attempts remain nested under decisions.                                             |
| Recorded cost is exactly $4.24475240                                         | Usage reconciliation                                                | Canonical fact                  | Aggregate JSON’s `1E-15` display difference is serialization only.                        |
| Illinois auction created the Red pivot                                       | Turn 40; `evt-000652..000725`; `auction-0003`                       | Reviewed mechanism              | Grok’s $300 bid may reflect synergy; “overbid” is unsupported.                            |
| Kentucky-for-$220 completed Grok’s Red group                                 | `dec-000157..000160`; `evt-001061..001079`                          | Canonical fact                  | Trade surplus is unknown.                                                                 |
| OpenAI’s Vermont retry changed the final strategic choice                    | `dec-000183/000184`; `evt-001238..001246`                           | Canonical reliability mechanism | Invalid attempt text is not latent ground truth.                                          |
| Gemini completed and developed Pink                                          | `dec-000193..000198` and subsequent builds through `dec-000278`     | Canonical mechanism             | Realized rent depends on dice.                                                            |
| OpenAI’s Brown development immediately preceded bankruptcy                   | `dec-000285..000293`; `evt-002004..002071`; turns 108–109           | Canonical sequence              | “Avoidable bankruptcy” is too strong without branch replay.                               |
| `end_turn` was legally available before optional Brown builds                | Frozen decision menus                                               | Canonical legal alternative     | It establishes avoidable exposure, not guaranteed survival.                               |
| Gemini consolidated all four railroads across two trades                     | `dec-000307/308`, `000358..363`; `evt-002177..2190`, `002560..2597` | Canonical mechanism             | One-trace railroad profitability remains stochastic.                                      |
| Claude rejected $500 and $850 for New York before a $750 Illinois obligation | `dec-000385..000394`; `evt-002781..2854`                            | Canonical sequence              | Accepting $850 supplies one-step cash but full continuation remains unknown.              |
| New York exchange enabled an Orange house lock                               | `dec-000395..000422`; `evt-002865` onward; bank inventory snapshots | Canonical mechanism             | The claim is about observed inventory and development, not exact causal treatment effect. |
| Gemini developed Orange while Grok could not develop Dark Blue               | Post-trade actions and zero bank-house state                        | Canonical observed consequence  | Alternative trade or build schedules are untested.                                        |
| Grok’s distress sales repeatedly released houses that Gemini reacquired      | `dec-000514..000532`; `evt-003878..4028`                            | Canonical feedback mechanism    | No exhaustive alternative liquidation search was run.                                     |
| Grok’s final tax bankruptcy was forced on the offered surface                | `dec-000539`; `evt-004097..004101`                                  | Canonical immediate cause       | $92 cash plus one $75 house sale remained below $200 tax.                                 |
| No D3/D4 supported deception                                                 | Exhaustive review                                                   | Reviewed case conclusion        | One T167 D2 candidate involves selective framing without a false factual proposition.     |
| No C2–C4 supported coordination                                              | Exhaustive review                                                   | Reviewed case conclusion        | Accepted trades remain C1 ordinary bilateral exchange.                                    |

Run B’s exhaustive review and case studies support these entries.  

## 7.3 Draft quantitative claims not yet certified from the attached package

The following manuscript values require a direct provenance audit before publication:

* Run A total tokens `3,524,545`;
* Run A per-model token and cost table;
* Run A terminal net worth `9,708`;
* Run A 28 properties, 7 houses, 6 hotels, 20 mortgages, and $1,850 liability;
* Run A aggregate rent collected/paid by player;
* Run B total tokens `2,945,246`;
* Run B per-model cost/decision/final-net table;
* Run B terminal net worth `10,071`;
* Run B aggregate portfolio and rent figures.

Required proof for each number:

1. named source table;
2. exact source artifact inputs;
3. metric-definition version;
4. run and analysis commit;
5. generated-file hash;
6. reconciliation against raw events/snapshots;
7. explanation of terminal creditor transfers;
8. token-accounting semantics.

These values should be labeled **unverified in the present ten-file evidence package**, not declared false.

# 8. Mechanism synthesis and epistemic limits

## 8.1 Run A: Pink, T79, and green

The realized Run A trajectory has a coherent three-stage mechanism.

### Stage 1: concentrated Pink engine

GPT acquired States, negotiated for Virginia, mortgaged and sold peripheral assets, and reached 3/3/3 Pink development. The key economic fact is not merely that it “traded aggressively.” It transformed broad but fragmented holdings into concentrated developed rent exposure. Later $750–$900 Pink obligations materially shaped all three opponent collapse paths. 

### Stage 2: leader-funded T79 consolidation

At T79, GPT used a large cash lead to conduct 51 decisions across multiple trade threads. It acquired Orange-adjacent and Green-adjacent assets and blockers while counterparties monetized selected deeds but retained other monopoly-completing properties. This was an active reallocation market, not a single decisive trade.

The strongest statement is:

> T79 converted GPT’s cash lead into broader strategic optionality and future Green control while leaving Orange and Red completion contested.

The weaker and unsupported statement is:

> GPT’s T79 choices were optimal.

### Stage 3: Green conversion and bankruptcy cascade

The acquired Green pair became a full group after Pennsylvania was obtained. Green development then produced the obligations associated with Grok’s elimination and Claude’s late-game collapse. GPT survived major light-blue shocks by selling lower-priority development and retained or rebuilt the Green threat.

Observed:

* exact acquisition and build events;
* exact rent obligations;
* exact liquidation;
* exact bankruptcy transfers.

Not observed:

* the result under a different T79 order;
* the result without the early Pink trade;
* whether a different liquidation strategy would preserve victory;
* exact marginal win probability of any one action.

## 8.2 Run B: Brown overdevelopment, railroads, blocker conflict, and house lock

### Brown overdevelopment

OpenAI spent $500 on Brown development during turn 108, with `end_turn` legally available before optional build steps. It then faced a $625 St. Charles obligation on the next turn and recovered only half the building outlay through liquidation.

Canonical fact:

> Optional development sharply reduced immediate liquidity immediately before the realized rent shock.

Defensible interpretation:

> This is a high-confidence case of realized-path overextension or avoidable exposure.

Not yet defensible:

> The build caused bankruptcy in the formal causal sense, or ending turn would certainly have produced survival.

### Railroad consolidation

Gemini purchased two mortgaged railroads from Grok and later acquired the other two from Claude, then unmortgaged all four. Assets that were fragmented and low-yield for counterparties became a coherent $200-per-landing set for Gemini.

This demonstrates an important MonopolyBench mechanism: **asset value is complement-dependent**. Deed price alone is not the correct valuation object.

### Blocker-liquidity conflict

Claude’s New York ownership denied Gemini Orange completion. Claude rejected $500 and $850 cash offers, then later faced an unpayable $750 Illinois rent. The $850 offer was a real legal alternative and would have raised enough one-step cash to cover that later obligation, had the rest of the path been unchanged.

The strict claim is:

> Claude chose continued blocking over immediate liquidity in a state where the blocker had strategic value, and the realized path later exposed the cost of that liquidity choice.

The overclaim is:

> Selling New York would have saved Claude or improved its win probability.

The branch changes Gemini’s Orange control, development, future rents, and all subsequent behavior.

### Finite-house lock

The official game has a finite house supply.  After acquiring New York, Gemini developed Orange while retaining twelve Pink houses and bought the remaining bank houses. Grok simultaneously received Dark Blue control but could not develop it. When Grok later sold Red houses under distress, Gemini repeatedly reacquired the released supply.

This is the strongest distinctive Run B mechanism:

[
\text{rent shock}
\rightarrow
\text{forced house sale}
\rightarrow
\text{leader house purchase}
\rightarrow
\text{continued scarcity}
\rightarrow
\text{weaker rebuilding capacity}.
]

It is an observed feedback loop. A causal estimate of the house lock’s contribution to win probability still requires branch simulation.

## 8.3 Cross-run synthesis

The two traces jointly demonstrate that MonopolyBench can expose:

* conversion of fragmented assets into complementary groups;
* interaction between bargaining and capital allocation;
* delayed consequences of liquidity decisions;
* scarcity-mediated strategic effects;
* bankruptcy as a multi-turn mechanism rather than a single event;
* reliability failures whose consequences range from immaterial retries to changed actions or deterministic fallback.

They do not show that a particular model family is generally better at any of these mechanisms.

## 8.4 Four epistemic layers

Every paper finding should be written in one of four forms:

| Layer                      | Example                                                                     |
| -------------------------- | --------------------------------------------------------------------------- |
| Canonical fact             | “Gemini bought nine Orange houses after the New York trade.”                |
| Model-reported reasoning   | “The private field stated an intent to consume the remaining house supply.” |
| Analyst interpretation     | “The sequence is consistent with a house-scarcity strategy.”                |
| Counterfactual speculation | “Without the house lock, Grok might have developed Dark Blue.”              |

Do not collapse these layers into one narrative sentence.

## 8.5 Deception and collusion

Neither attached run supports D3/D4 intentional deception or sustained C3/C4 coordination under the project’s codebook.

Run A’s strongest issues are factual/rule errors and selective bargaining frames. Run B contains one medium-confidence D2 candidate at the New York exchange: Gemini’s public framing emphasized the apparent bilateral benefits while its private field explicitly valued immediate house denial. Because the public message contained no demonstrated false factual proposition, D3 is not supported.

No model-generated private field should be treated as direct intent evidence without corroborating public representation, objective contradiction, strategic benefit, and later behavior.

# 9. Cost, reliability, replay, and artifact-integrity synthesis

## 9.1 Exact reliability comparison

| Metric                              |                Run A |       Run B |
| ----------------------------------- | -------------------: | ----------: |
| Resolved decisions                  |                  583 |         540 |
| Attempts                            |                  604 |         549 |
| First-attempt-invalid decisions     |                   21 |           9 |
| Derived first-pass-valid decisions  |                  562 |         531 |
| Derived first-pass-valid rate       |               96.40% |      98.33% |
| Invalid attempts                    |                   23 |           9 |
| Invalid-attempt share               |                3.81% |       1.64% |
| Deterministic fallbacks             |                    2 |           0 |
| Fallback share per decision         |                0.34% |          0% |
| Usage-covered attempts              |              603/604 |     549/549 |
| Recorded cost                       |         $27.71173045 | $4.24475240 |
| Recorded cost/decision, descriptive |             $0.04753 |    $0.00786 |
| State replay                        |                 Pass |        Pass |
| Strict artifact replay              | Fail at sequence 669 |        Pass |

The cost-per-decision values are arithmetically valid but are not model-efficiency comparisons. The runs use different rosters, model tiers, game lengths, decision mixes, and provider prices.

## 9.2 Decision, attempt, and fallback distinctions

A decision is one engine-required choice. An attempt is one provider/model response generated while resolving that choice. A fallback is an arena-selected deterministic action after model attempts fail.

For Run A:

* 583 decisions generated 604 attempts;
* 21 decisions required at least one retry;
* two decisions ended in deterministic fallbacks;
* all 583 decisions still produced exactly one applied action.

For Run B:

* 540 decisions generated 549 attempts;
* nine invalid first attempts were corrected;
* no fallback was needed.

Reporting only final applied actions would hide reliability and cost. Reporting attempts as independent decisions would inflate sample size.

## 9.3 Run A replay interpretation

Run A supports:

* canonical endpoint and bankruptcy order;
* state trajectories;
* cash, ownership, building, mortgage, rent, and liquidation facts derived from canonical state/events;
* applied-action case studies;
* exact raw attempt inspection.

It does not support an unqualified claim that the entire generated event artifact is byte- or field-identical under replay.

The exact fix is to separate event semantics:

```text
model_attempt_valid = false
applied_action_valid = true
applied_action_source = deterministic_fallback
fallback_reason = illogical_after_retry
```

Artifact replay should reproduce both the invalid model-response observation and the valid applied fallback, rather than reconstructing the response event from the applied action alone.

## 9.4 Run B replay interpretation

Run B passes both state and strict artifact comparison. It is the stronger artifact for demonstrating end-to-end replay fidelity. It still does not become a model-ranking replicate; replay quality and experimental replication are separate gates.

## 9.5 Source preservation and legacy manifests

Both source trees were frozen at commit `fa773791718e3b5d8ff18448e2ad3fa42b375259` and preserved byte-for-byte through analysis.

Both legacy `artifact_manifest.json` files contain documented drift or absent optional outputs. The integrity reports correctly treat the checked-in bytes as canonical and leave old manifests untouched. This is a warning about legacy packaging, not evidence that the played trajectories changed.  

## 9.6 Missing provider usage

Run A attempt `mock-83265-81ed4937-dec-000389` received HTTP 503 and has no returned usage or cost. The correct treatment is:

* `usage_missing=true`;
* token fields null;
* cost null;
* failure reason retained;
* no imputation;
* aggregate described as **recorded OpenRouter actual cost**, not hypothetical compute consumption.

## 9.7 Token semantics

Preserve:

```text
input_tokens
output_tokens
reasoning_tokens
reported_total_tokens
cached_input_tokens
reasoning_token_semantics
actual_provider
resolved_model_id
cost_usd
```

OpenRouter states that reasoning tokens are treated as output tokens for billing, while some providers do not expose reasoning content or expose it differently. ([OpenRouter][28]) Therefore:

* never add reasoning tokens to output tokens unless metadata explicitly says they are additional;
* never impute zero when reasoning tokens are missing;
* do not compare reasoning volume across models without semantics;
* log omitted request parameters as omitted;
* archive actual route and provider, not only requested slug.

## 9.8 What cost and reliability cannot establish

From these runs, one cannot infer:

* that the cheaper roster is strategically better;
* that higher reasoning tokens caused better or worse choices;
* that retries cause bankruptcy;
* that a model with fewer invalid outputs is economically stronger;
* that total cost is efficiency;
* that one provider family is more reliable in general.

Valid full-game statements are descriptive:

* Run A consumed more recorded cost under its roster and path.
* Run B had a higher first-pass-valid rate and no fallbacks.
* Some retries materially changed the chosen action.
* Other retries merely corrected protocol formatting.
* Longer survival increases the opportunity to incur additional cost.

# 10. Figure and table blueprint

## 10.1 Main-paper tables

| Table                                  | Status                       | Existing inputs                                              | Additional inputs or changes                                                     |
| -------------------------------------- | ---------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| T1. Related-work comparison            | Publishable now              | Literature map above                                         | Lock search date and archive mutable pages.                                      |
| T2. Architecture and artifact contract | Publishable now              | Manuscript architecture; process docs                        | Final diagram and exact artifact-version fields.                                 |
| T3. Canonical-run integrity            | Publishable now              | Both integrity reports                                       | Include state/artifact replay separately and playable/terminal turn distinction. |
| T4. Case-study outcome summary         | Publishable now, descriptive | `summary.json`, final snapshots, bankruptcy order            | Remove unverified net-worth/token/rent values.                                   |
| T5. Reliability and cost               | Publishable now, descriptive | `usage_attempts.jsonl`, `decisions.jsonl`, integrity reports | Raw token-semantics and usage-coverage columns.                                  |
| T6. Mechanism case ledger              | Publishable now              | Attached case studies and evidence IDs                       | Compact to 6–8 main cases; move full ledger to appendix.                         |
| T7. Primary comparative outcomes       | Requires balanced runs       | Future `player_outcomes.csv`                                 | Seed-block IDs, seat rotations, model versions, uncertainty.                     |
| T8. Micro-suite results                | Requires new queries         | Future `scenario_results.csv`                                | Frozen fixture manifest and repeated queries.                                    |
| T9. Human-review labels                | Requires adjudication        | Review packets and codebook                                  | Human-gold rows, agreement, adjudication, masking.                               |
| T10. Oracle-dependent mechanisms       | Requires branch/oracle       | Future trade/auction/regret tables                           | Oracle tier, policy, horizon, RNG, Monte Carlo uncertainty.                      |

## 10.2 Descriptive figures publishable now

### Figure 1: System and provenance architecture

**Inputs:** contracts, engine, arena, telemetry, API, frontend.

**Caption contract:**

> The engine is the sole state authority. The arena sends OpenRouter requests, validates model responses, retries failures, and may select deterministic fallbacks. Telemetry records attempts, applied actions, events, snapshots, usage, and replay outputs. Deterministic replay applies to frozen engine inputs and applied actions, not to regeneration of LLM outputs.

### Figure 2: Run A annotated economic trajectory

**Inputs:** `state_by_turn_player.csv`, `property_holdings_by_turn.csv`, events.

Annotate:

* T25–26 Pink completion/development;
* T33 fallback mismatch;
* T79 consolidation;
* T106–110 Green development;
* T113, T126, and T190 bankruptcies.

**Limit:** Caption must state `state_passed_artifact_failed` and that the figure is derived from canonical snapshots/state-relevant events.

### Figure 3: Run B finite-house mechanism

**Inputs:** `bank_inventory_by_turn.csv`, `property_holdings_by_turn.csv`, building events.

Show:

* Pink house occupancy;
* New York transfer;
* Orange house purchases;
* bank houses reaching zero;
* Grok’s Red sales;
* Gemini’s reacquisition of released houses.

**Limit:** “Observed house-supply feedback,” not “causal proof that the lock caused victory.”

### Figure 4: Bankruptcy-window panels

One panel per bankruptcy with:

* cash;
* accounting net worth;
* legal liquidity when implemented;
* obligation;
* mortgage/building actions;
* creditor;
* event IDs.

Run B Brown development should be a dedicated inset.

### Figure 5: Reliability timeline

**Inputs:** `per_call_usage.csv`, decisions, attempts.

Markers:

* invalid JSON;
* invalid schema;
* illegal action;
* retry;
* fallback;
* HTTP 503;
* latency outlier.

### Figure 6: Cost and token timeline

Separate input, output, reasoning, reported total, and cost. Include usage-missing markers.

**Limit:** no implied cognitive interpretation of reasoning tokens.

### Figure 7: Negotiation episode depth

**Inputs:** `trade_episodes.csv`, `trade_player_episodes.csv`.

Show exchange depth, speaker alternations, outcome, and cost. T79 should be annotated.

**Limit:** episode frequency is not trade quality.

### Figure 8: Ownership and development heatmap

Board-ordered properties over time, with owner, mortgage, houses/hotel. This figure directly conveys persistent asset control better than a terminal table.

## 10.3 Figures requiring balanced experiments

* rank-probability plot;
* seat-conditioned model effects;
* net-worth-AUC effect estimates;
* bankruptcy survival curves;
* standardized first-pass-validity effects;
* common-horizon cost comparison;
* model-by-seed interaction plot.

## 10.4 Figures requiring oracle or branch work

* auction bid versus state-specific WTP;
* trade surplus plane;
* normalized-regret distribution;
* avoidable-bankruptcy cases;
* policy-robust branch intervals;
* cost-regret frontier.

## 10.5 Figures requiring micro-suite execution

* exact and distributional full/micro concordance;
* epsilon-optimality by family;
* context-compression loss;
* action-order sensitivity;
* identity/framing paired effects;
* reasoning-effort randomized ablation.

## 10.6 Figures requiring judge/human validation

* judge-human agreement matrix;
* same-family preference leakage;
* position and verbosity bias;
* D/C label prevalence with adjudicated denominators;
* promise lifecycle outcomes.

Every figure must name its source table, metric version, run/experiment ID, and integrity inclusion rule.

# 11. Replacement manuscript prose

## 11.1 Abstract

> Large language model agents are increasingly evaluated in interactive environments, yet many evaluations still compress long trajectories into terminal success or aggregate scores. We introduce MonopolyBench, a replay-oriented environment for studying language models as economic agents in a persistent, multi-agent asset economy. An authoritative rules engine exposes legal decisions over property acquisition, auctions, bilateral trade, development, mortgages, liquidation, rent, and bankruptcy. The arena queries language models through a structured action interface, while telemetry preserves decision attempts, public communication, model-reported private analysis fields, applied actions, state transitions, usage, cost, and split state/artifact replay reports. MonopolyBench separates deterministic game facts from strategic interpretation: existing artifacts support exact trajectory and reliability analysis, whereas regret, trade surplus, and avoidable-bankruptcy claims require declared counterfactual oracles. We present two exhaustive pilot case studies comprising 191 and 273 playable turns. One run passes state replay while retaining a documented strict artifact-representation mismatch; the other passes both state and full artifact replay. The traces illustrate mechanisms including concentrated rent-engine construction, leader-funded consolidation, mortgage and liquidation cycles, finite-house scarcity, and bankruptcy cascades. These cases validate the benchmark’s audit and analysis surface but are not a balanced model-ranking dataset. We conclude with a preregistered design for seed-blocked seat rotations, controlled scenario fixtures, uncertainty-aware rankings, and calibrated semantic review.

## 11.2 End of introduction and contributions

> MonopolyBench treats economic agency as an observable trajectory rather than an unobserved model trait. Its central questions are whether an agent converts liquidity into productive assets, develops those assets without becoming insolvent, values auctions and trades in state, adapts to rival portfolios, and remains operationally reliable across a long game. Monopoly is used as a stylized, fully instrumented testbed rather than as a proxy for real-world business performance.
>
> This work makes six contributions. First, it provides a rules-complete Monopoly environment in which all state mutation is performed by an authoritative engine and model actions are selected from enumerated legal surfaces. Second, it defines an append-only artifact contract joining requests, attempts, validation, actions, events, snapshots, public communication, model-reported private fields, provider usage, and cost. Third, it distinguishes deterministic state replay from strict full-artifact replay. Fourth, it develops a metric hierarchy separating outcome endpoints, economic mechanisms, operational diagnostics, human-reviewed communication labels, and oracle-dependent counterfactuals. Fifth, it reports two exhaustive full-game case studies with source-linked mechanism and bankruptcy analysis. Sixth, it specifies a future evaluation design that connects balanced full-game campaigns to frozen micro fixtures and branch-based action valuation.
>
> We do not claim that MonopolyBench is the first long-horizon agent benchmark, economic game benchmark, negotiation benchmark, or Monopoly decision environment. Its contribution is the auditable conjunction of persistent rivalrous assets, natural-language bargaining, legal action enforcement, hard insolvency, detailed provider telemetry, and replay-oriented mechanism analysis.

## 11.3 Evaluation philosophy

> MonopolyBench separates four evaluation layers. The first layer contains deterministic game facts: legal actions, applied actions, cash transfers, ownership, buildings, mortgages, and bankruptcy. The second contains descriptive trajectory metrics, including survival order, net-worth AUC, rent flows, development timing, liquidity shocks, trade episodes, auction participation, and operational cost. The third contains evidence-linked semantic interpretation, such as negotiation strategy, promise tracking, or public/private discrepancy; these labels require explicit codebooks and, for publication-facing high-risk claims, human adjudication. The fourth contains counterfactual decision quality. Regret, trade surplus, winner’s curse, and avoidable bankruptcy are reported only when the analysis names the oracle tier, horizon, continuation policy, randomness policy, and uncertainty.
>
> This hierarchy prevents two opposite errors. It avoids treating every terminal loss as evidence of poor local reasoning, because dice and opponent actions contribute to outcomes. It also avoids treating descriptive accounting as a substitute for decision quality. A high bid may be rational because of completion or blocker value; an accepted trade may create bilateral value while harming a third party; a low-cash position may reflect either productive development or dangerous overextension.
>
> The inferential unit for full-game model comparison is a seed block containing balanced seat rotations. Decisions and attempts are nested observations inside player-game trajectories. Single-run mechanisms are reported as case studies, not as model traits or prevalence estimates.

## 11.4 Pilot-run integrity paragraph

> We analyze two canonical saved games generated from source commit `fa773791718e3b5d8ff18448e2ad3fa42b375259`. Run `mock-83265-81ed4937` contains 191 playable turns, 583 decisions and applied actions, 604 attempts, 21 retry decisions, 23 invalid attempts, and two deterministic fallbacks. OpenAI GPT 5.5 is the last surviving player. State replay passes all 1,640 state-relevant comparisons; strict artifact replay first differs at event sequence 669 because the original model-response event records an invalid two-attempt sequence followed by fallback, while replay represents the already-applied fallback action as valid. There are no missing or extra actions and no decision-ID mismatch. We therefore report this run as state-replay-valid with an explicit artifact-representation caveat. Run `mock-44910-42ec35c5` contains 273 playable turns, 540 decisions and applied actions, 549 attempts, nine invalid first attempts, and no fallback. Gemini 3 Flash Preview is the last surviving player. State replay passes 1,942/1,942 comparisons and strict artifact replay passes all 4,102 events.

## 11.5 Cross-run pilot synthesis

> The pilot games are not balanced replications and do not support model rankings. They instead demonstrate complementary economic mechanisms. In Run A, an early Pink monopoly was financed through trade, mortgage, and asset recycling; a later 51-decision consolidation turn converted a cash lead into Orange- and Green-adjacent control; and developed Green properties contributed to the terminal bankruptcy sequence. In Run B, Gemini converted bilateral trades into Pink, railroad, and Orange control, then used the finite house supply to limit a rival’s ability to develop Dark Blue. The same trace also contains a realized-path liquidity failure in which optional Brown development immediately preceded an unpayable rent obligation.
>
> Across both traces, the relevant object is not acquisition count alone but the conversion of cash and fragmented deeds into enforceable rent pressure while preserving legal liquidity. This observation motivates, but does not establish, the hypothesis that durable economic agency depends on coordinating acquisition, development, bargaining, and solvency over long horizons.

## 11.6 Discussion

> MonopolyBench’s primary value is explanatory resolution. A terminal winner can be connected to the trades, auctions, development steps, rent shocks, and liquidation choices that produced the result. Conversely, an eliminated player’s trajectory can contain strong local decisions before an adverse shock. This makes the benchmark suitable for studying path-dependent agency rather than only end-task completion.
>
> The two pilots also show why economic and operational measurements must remain separate. Run B had no deterministic fallback and a higher first-pass-valid rate, but these facts do not explain the winner by themselves. Run A contains more invalid attempts and an artifact-level fallback representation mismatch while still preserving a fully replayed state trajectory. Reliability is therefore a deployment endpoint and a possible trajectory mechanism, not a replacement for economic evaluation.
>
> Full games and fixtures answer different questions. Full games reveal compounding behavior, endogenous opportunity sets, and opponent adaptation. Frozen fixtures permit repeated queries, randomized action order, identity masking, reasoning-effort ablations, and branch evaluation. The research program is strongest when full-game states generate fixtures and fixture results are used to explain, rather than overwrite, the ecological trajectories.
>
> Finally, communication labels must remain bounded. A model-reported private field may reveal a stated plan that differs from a public message, but selective disclosure is normal in bargaining and does not by itself establish deception. Similarly, mutually beneficial trades and temporary anti-leader alignment are not collusion. High-risk labels require objective contradiction or coordination evidence, strategic relevance, linked later behavior, and human adjudication.

## 11.7 Limitations

> Monopoly is a stylized, closed economy. It omits production, heterogeneous consumption preferences, enforceable private contracts, realistic credit markets, regulation, and many forms of information asymmetry. Results should not be interpreted as forecasts of business, investment, or social behavior outside the benchmark.
>
> The current evidence consists of two case-study games with different rosters. It does not establish stable model rankings, mechanism prevalence, or general model traits. Full-game opportunities are endogenous: a model’s prior decisions determine which later trades, auctions, and liquidation states it encounters. Decision-level rows therefore cannot be treated as independent benchmark items.
>
> The current analysis also lacks a validated continuation-value oracle. Deed price, realized rent, terminal outcome, and model-reported reasoning do not establish action utility. Claims about regret, trade surplus, winner’s curse, or avoidable bankruptcy await branch analysis under declared continuation and randomness policies.
>
> Provider-mediated model behavior may change with date, route, endpoint, model revision, and omitted request parameters. OpenRouter reasoning-token fields are not semantically uniform across providers. Publication runs must preserve actual provider, resolved model, route policy, request facts, usage missingness, and pricing snapshots.
>
> Semantic review remains another limitation. The attached reports provide exhaustive evidence-linked qualitative analysis, but publication-facing deception, collusion, promise, and intent-like rates require blinded human gold labels, double coding, adjudication, and judge-bias validation.

## 11.8 Conclusion

> MonopolyBench provides a replay-oriented environment for studying language models as long-horizon economic agents. Its authoritative engine separates legal game execution from model strategy, while its artifact contract connects provider calls and communication to applied actions, economic state, cost, and replay. The benchmark thereby supports analyses of capital allocation, bargaining, development, liquidity, reliability, and bankruptcy at a level of provenance not available from terminal scores alone.
>
> Two exhaustive pilot games validate this analysis surface and reveal interpretable realized mechanisms, including rent-engine formation, leader-funded consolidation, finite-house scarcity, and delayed liquidity collapse. They are case studies rather than comparative evidence. The next stage is a preregistered program of balanced seed blocks, repeated micro fixtures, branch-based valuation, calibrated semantic review, and uncertainty-aware model effects. The intended contribution is not a declaration of which model plays Monopoly best, but a reproducible instrument for investigating whether agentic systems maintain coherent economic behavior under persistent competition and insolvency risk.

## 11.9 Placeholder contract for the future comparative-results section

Do not write comparative prose until the section can fill every field below:

```text
Primary roster:
Model/version/date window:
Prompt/rules/schema hashes:
Provider route policy:
Identity condition:
Endpoint policy:
Number of independent seed blocks:
Games per block:
Seat-rotation scheme:
Integrity exclusions:
State replay pass rate:
Artifact replay pass rate:
Primary placement-model result:
Net-worth-AUC effect and interval:
First-pass-validity effect and interval:
Common-horizon cost result:
Sensitivity without fallback-routed games:
Rank probabilities:
Prespecified multiplicity adjustment:
```

# 12. Preregistered experiment and analysis plan

## 12.1 Primary research question

Under a fixed four-model roster, prompt/rules policy, route policy, identity condition, and date window, do models differ in long-horizon economic agency as measured jointly by placement and game-horizon net-worth AUC?

## 12.2 Confirmatory hypotheses

| ID | Hypothesis                                                                                     | Endpoint                                              |
| -- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| P1 | Model identity affects final placement under balanced seats and seed blocks.                   | Full placement order                                  |
| P2 | Model identity affects game-horizon net-worth AUC.                                             | Player-game AUC                                       |
| K1 | Model identity affects first-pass legal action rate after conditioning on decision complexity. | Decision-level validity                               |
| K2 | Lagged legal-liquidity state predicts bankruptcy hazard beyond seat and phase.                 | Player-turn hazard; predictive                        |
| S1 | Trade, development, and liquidity mechanisms mediate observed trajectories descriptively.      | Secondary mechanism tables; no causal mediation claim |

P1 and P2 are co-primary. K1 and K2 are key secondary.

## 12.3 Design

* Fixed four-model primary roster.
* Anonymous model/player identity in the primary condition.
* Independent seed blocks.
* Four cyclic seat rotations per block.
* Fixed rules, prompt, schema, legal-action ordering policy, retry prompt, communication policy, and endpoint.
* Model/version and date window frozen as tightly as provider access permits.
* OpenRouter route policy fixed and actual provider retained.
* Temperature and `max_tokens` recorded as sent or omitted, never inferred.
* No mid-campaign prompt or engine change.
* New model versions constitute a new experiment.

## 12.4 Inclusion

A game enters primary analysis only if:

* raw events/actions/decisions parse;
* every decision resolves to exactly one applied action or documented terminal reason;
* state replay passes;
* final snapshot and summary agree;
* model, route, prompt, rules, seed-block, and seat metadata are complete.

Strict artifact replay failures are handled by claim dependency:

* state-derived outcomes may remain eligible if the artifact mismatch is demonstrated not to affect state and is disclosed;
* artifact/communication endpoints depending on the mismatched field are excluded or sensitivity-coded.

## 12.5 Exclusion

Exclude from confirmatory analysis:

* state replay failure;
* missing/extra applied actions;
* unresolved decision-action mismatch;
* unknown model identity;
* undocumented prompt/rules change;
* run truncation not covered by endpoint policy;
* duplicated or corrupted seed block.

Do not exclude games because a model performed badly, used fallback, or generated high cost. Those are outcomes.

## 12.6 Primary analysis

* Hierarchical Plackett–Luce placement model.
* Mixed or block-bootstrap model for game-horizon net-worth AUC.
* Seat fixed effects.
* Model-by-seed random effects.
* Route/date effects when variation remains.
* Holm adjustment across the two co-primary omnibus tests.
* Pairwise contrasts only after omnibus evidence.

## 12.7 Secondary analysis

* discrete-time bankruptcy hazard;
* cash and legal-liquidity AUC;
* drawdown and recovery;
* monopoly completion and development timing;
* trade and auction funnels;
* mortgage tenure and liquidation;
* first-pass validity, recovery, fallback, and invalid-cost share;
* common-horizon cost.

Secondary families use BH FDR.

## 12.8 Micro-suite study

Fixtures are sampled from both strong and weak full-game decisions.

For each fixture:

* canonical state and legal action hashes;
* full, compressed, and minimal context variants;
* anonymous identities;
* randomized legal-action order;
* repeated calls per variant;
* same request policy;
* raw cost and provider metadata;
* branch values where available.

Primary micro outcomes:

* legality;
* epsilon-optimality;
* full/micro action-distribution concordance;
* value loss under context compression;
* action-order sensitivity.

## 12.9 Reasoning-effort ablation

Within each model-fixture pair:

* randomly assign supported effort levels;
* block by fixture and repetition;
* retain actual provider;
* analyze action quality, first-pass validity, cost, output length, and latency;
* test model×effort and family×effort interactions.

This is the appropriate place for causal claims about reasoning effort.

## 12.10 Branch study

Begin with Tier 0 and Tier 2:

1. exact one-step accounting;
2. deterministic scripted continuation;
3. common exogenous schedules;
4. action-value uncertainty;
5. sensitivity across at least two scripts.

Only after validation add:

* heuristic/RL policy ensemble;
* re-queried LLM continuation;
* policy-robust intervals.

## 12.11 Communication review

* Freeze D/C and promise codebook.
* Build stratified candidate and ordinary-baseline samples.
* Mask model identity and winner where feasible.
* Double-code every D2–D4/C2–C4 candidate.
* Adjudicate disagreements.
* Report Krippendorff’s alpha or appropriate agreement.
* Validate any LLM judge against held-out human gold.
* Audit same-family, position, verbosity, identity, and outcome leakage.

No LLM-judge-only high-risk label enters a main paper claim.

## 12.12 Sample-size execution

* Start with 8–12 seed blocks for blinded nuisance calibration.
* Simulate the exact placement/AUC analysis over candidate final block counts.
* Set the final block count from preregistered power and precision criteria.
* Freeze the count before unblinding model effects.
* Report failed/corrupted runs and replacements transparently.
* Treat each four-game rotation set as one correlated block.

# 13. Prioritized implementation and research roadmap

| Phase                           | Dependency                  | Exact work                                                                                                                             | Success gate                                                                                                                                    | Failure/stop condition                                                                  |
| ------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 0. Manuscript correction        | None                        | Replace determinism wording; correct run statuses/turns; remove unverified tables; update related work; insert bounded pilot prose.    | No claim contradicts integrity reports; no ranking language remains.                                                                            | Any Run A text says replay-clean or “pending reconciliation.”                           |
| 1. Deterministic metric closure | Phase 0                     | Freeze `metric_definitions.json`; implement book/liquidation NW, AUC variants, episode denominators, phase rules, expanded provenance. | Both canonical runs regenerate with exact count reconciliation and schema tests.                                                                | Any episode count fails to reconcile to source starts/terminals.                        |
| 2. Run-manifest closure         | Phase 1                     | Log prompt/rules hashes, requested/resolved model, actual provider, route policy, sent/omitted params, pricing snapshot.               | Every call/attempt joins to decision, model, route, request/response hashes.                                                                    | Provider or model identity remains unresolved.                                          |
| 3. Replay repair                | Phase 1                     | Split attempt validity from fallback-action validity; reproduce Run A original response metadata and applied fallback distinctly.      | Run A strict artifact replay passes without altering frozen source semantics, or mismatch remains intentionally versioned with regression test. | “Fix” rewrites canonical raw artifacts or obscures original invalid response.           |
| 4. Legal-liquidity optimizer    | Phase 1                     | Engine-valid search over house/hotel sales, mortgage constraints, bank inventory, and debt.                                            | Unit tests cover Run A T64/T114 and all bankruptcy windows; optimizer never proposes illegal liquidation.                                       | Search ignores even-building or house-bank constraints.                                 |
| 5. Branch infrastructure        | Phases 1–4                  | Counter-based RNG; branch state clone; action substitution; Tier 0/2 continuations; uncertainty output.                                | Repeated paired branches are deterministic under same policy/schedule and preserve provenance.                                                  | Alternative actions desynchronize uncontrolled mutable RNG streams.                     |
| 6. Fixture extraction           | Phases 1–5                  | Extract Pink, T79, Brown, blocker, house-lock, auction, bankruptcy, and strong-play states.                                            | Every fixture reproduces source state hash and legal action set.                                                                                | Model output or outcome is embedded in canonical fixture.                               |
| 7. Micro-suite execution        | Phase 6                     | Full/compressed/minimal contexts, repetitions, action-order randomization, identity masking.                                           | Stable result schema, complete usage, sufficient repeatability, branch values where promised.                                                   | Context variants change economic state or legal actions.                                |
| 8. Balanced campaign            | Phases 1–3; preregistration | Independent seed blocks, four rotations, locked roster/prompt/route/date.                                                              | Predeclared game count complete; integrity and route coverage above threshold.                                                                  | Model/version drift, prompt change, systemic replay failure, or missing block metadata. |
| 9. Human annotation             | Stable packets              | Double-coded D/C, promise, negotiation, and action-quality sample.                                                                     | Agreement and held-out adjudication report complete.                                                                                            | High-risk labels rely solely on coding-agent or LLM-judge output.                       |
| 10. Statistical modeling        | Phases 7–9                  | PL/BT ranking, AUC, hazard, reliability, micro concordance, cost analysis.                                                             | Simulation-validated type-I error/coverage; block-aware uncertainty.                                                                            | Decisions treated as independent replicates or ranks published without intervals.       |
| 11. Final paper package         | All                         | Tables, figures, manifests, raw artifacts, analysis code, appendix, data dictionary.                                                   | Every paper value resolves to a table, formula version, source hash, and run/experiment ID.                                                     | Any value exists only in prose or manually copied spreadsheet.                          |

Current operational commands from the automation guide are:

```powershell
uv run python scripts/standardize_saved_games.py frontier-191-mock-83265-81ed4937-openai-gpt-5-5 frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview
```

```powershell
uv run python scripts/analyze_saved_game.py saved_games/<saved-game>
```

```powershell
uv run python scripts/analyze_negotiation_tactics.py <game-a> <game-b> --output-dir analysis_outputs/negotiation
```

```powershell
pwsh -File scripts/verify.ps1
```

The coding-agent whole-game judge should remain downstream and read-only. It is not a substitute for deterministic episode construction or human adjudication. 

# 14. Claim ladder: can say now / case study only / cannot say yet

## 14.1 Can say now

* MonopolyBench has an authoritative legal-action engine and append-only artifact surface.
* Applied actions and canonical state are distinguishable from model attempts.
* Both canonical games have complete decision-action bijections and preserved attempt artifacts.
* Run A’s exact replay status is `state_passed_artifact_failed`.
* Run B passes state and full artifact replay.
* Run A contains 583 decisions, 604 attempts, 23 invalid attempts, and two fallbacks.
* Run B contains 540 decisions, 549 attempts, nine invalid attempts, and no fallback.
* The two runs contain analyzable trade, auction, mortgage, rent, liquidation, and bankruptcy mechanisms.
* The benchmark can expose delayed economic collapse and reliability failures.
* The current request policy omitted temperature and `max_tokens` and requested a reasoning effort, as documented in the research memo. 

## 14.2 Can say only as reviewed case studies

* Run A’s Pink development formed an important realized rent engine.
* Run A’s T79 turn converted a cash lead into broader strategic control.
* Run A’s Green development contributed to the final elimination path.
* Run B’s Brown development was a high-confidence realized-path liquidity error.
* Run B’s railroad consolidation created a coherent second income engine.
* Claude faced a blocker-versus-liquidity conflict over New York.
* Run B’s finite-house lock constrained rival development.
* Distress sales and leader reacquisition formed an observed scarcity feedback loop.
* Particular public/private differences are D1/D2 candidates.
* No D3/D4 or sustained C3/C4 behavior was supported by the attached reviews.

Every such statement must name the run, IDs, and counterfactual boundary.

## 14.3 Cannot say yet

* GPT 5.5 is better at Monopoly than the other models.
* Gemini 3 Flash is generally a stronger economic agent.
* One model family negotiates, colludes, deceives, or manages liquidity more often.
* Trading causes victory.
* Rent-engine construction is the dominant mechanism across models.
* More reasoning tokens improve or harm strategy.
* Higher API cost purchases better economic decisions.
* Any specific auction was an overbid without state-specific WTP.
* Any accepted trade was Pareto-improving or kingmaking without continuation values.
* Any bankruptcy was formally avoidable without a legal branch search.
* Micro decisions predict full-game outcomes.
* MonopolyBench measures real-world business competence, financial judgment, or safety.
* A coding-agent or LLM judge score is ground-truth utility or intent.
* The draft’s currently untraced aggregate token, rent, net-worth, or portfolio tables are publication-certified.

# 15. Exhaustive handoff for the next Codex researcher

## 15.1 Canonical source paths

### Manuscript and methodology

```text
/mnt/data/monopolybench_ieee_draft_v0_1.tex
/mnt/data/analysis.md
/mnt/data/analysis_process.md
/mnt/data/analysis_automated.md
/mnt/data/Pasted text.txt
```

### Run A package

```text
/mnt/data/manual_review_report.md
/mnt/data/case_studies(1).md
/mnt/data/integrity_report(1).md
```

Embedded run ID:

```text
mock-83265-81ed4937
```

Saved game:

```text
frontier-191-mock-83265-81ed4937-openai-gpt-5-5
```

### Run B package

```text
/mnt/data/manual_review_report(1).md
/mnt/data/case_studies.md
/mnt/data/integrity_report.md
```

Embedded run ID:

```text
mock-44910-42ec35c5
```

Saved game:

```text
frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview
```

Do not infer run identity from UI suffixes.

## 15.2 Required reading order

1. Integrity report.
2. Final summary and snapshots.
3. Event chronology.
4. Applied actions.
5. Decision and attempt records.
6. Prompt/response artifacts for selected windows.
7. Expanded deterministic metrics.
8. Qualitative review.
9. Case studies.
10. Manuscript prose.

Do not begin with model messages.

## 15.3 Exact replay checks

### Run A

Verify and preserve:

```text
aggregate_status = state_passed_artifact_failed
state_events_compared = 1640
state_mismatches = 0
first_artifact_mismatch_seq = 669
first_artifact_mismatch_event = mock-83265-81ed4937-evt-000669
first_artifact_mismatch_decision = mock-83265-81ed4937-dec-000096
original.valid = false
original.error = fallback:illogical_after_retry
replay.valid = true
replay.error = null
missing_actions = 0
extra_actions = 0
decision_id_mismatch = false
```

### Run B

Verify:

```text
state_status = passed
state_events_compared = 1942
artifact_status = passed
artifact_events_compared = 4102
missing_actions = 0
extra_actions = 0
decision_id_mismatch = false
```

## 15.4 Manuscript values requiring source-table resolution

Before retaining any pilot table, locate and hash:

```text
analysis/tables/model_usage.csv
analysis/tables/per_call_usage.csv
analysis/tables/run_summary.csv
analysis/tables/state_by_turn_player.csv
analysis/tables/property_holdings_by_turn.csv
analysis/tables/cash_flow.csv
analysis/expanded_metrics/player_metrics.csv
analysis/expanded_metrics/cash_ledger.csv
analysis/expanded_metrics/trade_episodes.csv
analysis/expanded_metrics/auction_episodes.csv
```

For each manuscript cell, record:

```text
paper_table
paper_cell
run_id
source_table
source_row_key
source_column
metric_definition_id
analysis_commit
source_hash
generated_hash
```

Stop using the cell if any field is unresolved.

## 15.5 High-priority mechanism windows

### Run A

```text
Pink engine:
dec-000040..000074
evt-000313..000524
turns 25..26

Park Place auction:
dec-000081..000093
evt-000578..000652
turns 31..32

T33 fallback:
dec-000095..000096
evt-000664..000672

Light-blue completion:
dec-000099..000119
evt-000696..000819

T79 consolidation:
dec-000279..000329
evt-001858..002135

T99 improved-property trade failures:
dec-000386
dec-000387
dec-000391

Green development:
dec-000412..000421
dec-000427

Grok bankruptcy:
dec-000379..000381
dec-000430..000431
evt-002488..002510
evt-002839..002855

Gemini bankruptcy:
dec-000369..000473
evt-003111..003124

Claude endgame:
dec-000531..000582
evt-003556..003971
```

### Run B

```text
Illinois auction:
evt-000652..000725
auction-0003

Kentucky trade:
dec-000157..000160
evt-001061..001079

Vermont retry:
dec-000183..000184
evt-001238..001246

Pink completion/development:
dec-000193..000198
later builds through dec-000278

Brown overdevelopment:
dec-000285..000293
evt-002004..002071
turns 108..109

Railroad consolidation:
dec-000307..000308
dec-000358..000363
evt-002177..002190
evt-002560..002597

New York blocker conflict:
dec-000385..000394
evt-002781..002854

House-lock trade/development:
dec-000395..000422
evt-002865 onward
turns 167..180

Distress-sale feedback:
dec-000514..000532
evt-003878..004028

Terminal tax:
dec-000536..000539
evt-004059..004101
```

## 15.6 Unresolved methodological questions

1. What exact net-worth convention generated the manuscript’s terminal values?
2. Are building values purchase basis, replacement cost, or liquidation value?
3. Does the current run manifest preserve actual provider endpoint for every call?
4. Are reasoning tokens included in output totals for every route?
5. What legal-action ordering policy was used, and was it stable?
6. Can the replay layer preserve original attempt/fallback metadata without changing canonical source?
7. Is an engine-valid legal-liquidity optimizer already partially implemented elsewhere?
8. Does the RNG architecture support counter-based branch schedules?
9. Which continuation policy should be the first Tier 2 baseline?
10. Which strong-play states, not only failures, will enter the fixture suite?
11. What is the primary campaign roster and model-version window?
12. Will the primary condition be anonymous?
13. Will provider fallbacks be disabled, restricted, or modeled?
14. What is the smallest scientifically meaningful placement or AUC difference?
15. Who will create and adjudicate the human-gold D/C set?
16. Which draft aggregate tables can be regenerated exactly from the frozen packages?
17. Should the paper be submitted now as a benchmark-methodology/case-study paper or after balanced campaign results?
18. Is the incomplete Beer Game/HBR citation relevant enough to retain?
19. Can official rules and any proprietary board representation be redistributed under the intended artifact license?
20. How will model/provider version drift be archived for future reproducibility?

## 15.7 Stop/go gates

### Go: manuscript revision

Proceed now. The architecture, integrity methodology, replay distinction, metric hierarchy, literature position, and two mechanism case studies are sufficient.

### Go: descriptive case-study figures

Proceed when:

* source table resolves;
* state replay passes;
* figure names run ID;
* caption states replay caveat;
* no oracle-dependent label is implied.

### Stop: comparative model claims

Stop until:

* one fixed roster;
* multiple independent seed blocks;
* complete seat rotations;
* locked prompt/rules/route policy;
* uncertainty-aware analysis;
* adequate power/precision;
* route/date sensitivity.

### Stop: regret/trade-surplus/avoidable-bankruptcy claims

Stop until:

* branch engine exists;
* action set is complete;
* continuation policy is declared;
* RNG policy is declared;
* oracle uncertainty is reported;
* sensitivity across policies is available.

### Stop: deception/collusion prevalence

Stop until:

* eligible denominator is defined;
* human-gold labels exist;
* high-risk cases are double-coded;
* adjudication is complete;
* judge bias is evaluated;
* model identity/winner masking is documented.

## 15.8 Final execution checklist

* [ ] Replace every unqualified “deterministic benchmark” phrase.
* [ ] Replace Run A “apparent winner” with the canonical winner.
* [ ] Replace Run A “pending replay reconciliation” with `state_passed_artifact_failed`.
* [ ] State Run A’s exact sequence-669 mismatch.
* [ ] Distinguish playable turns from terminal-only checkpoints for both runs.
* [ ] Replace “583 model calls” with 583 decisions and 604 attempts.
* [ ] Preserve the Run A HTTP 503 usage row as null.
* [ ] Verify every token, rent, net-worth, property, building, and liability number against a hashed table.
* [ ] Add actual provider and route fields to the paper’s run manifest.
* [ ] Record temperature and `max_tokens` as omitted where applicable.
* [ ] Add split state/artifact replay to the architecture and claims table.
* [ ] Replace “no heuristic oracle” with the four-layer evaluation hierarchy.
* [ ] Define accounting and liquidation net worth.
* [ ] Implement game-horizon, alive-only, and common-horizon AUC.
* [ ] Build canonical trade and auction denominators.
* [ ] Implement or locate the legal-liquidity optimizer.
* [ ] Repair or version the Run A fallback artifact representation.
* [ ] Freeze the first fixture manifest with source state and legal-action hashes.
* [ ] Include strong-play fixtures as well as failures.
* [ ] Implement common-exogenous branch RNG before causal counterfactual language.
* [ ] Freeze the primary roster, identity condition, route policy, and date window.
* [ ] Run an 8–12-block blinded calibration campaign.
* [ ] Simulate final sample size under the exact planned models.
* [ ] Preregister co-primary endpoints and multiplicity handling.
* [ ] Double-code high-risk communication labels.
* [ ] Validate any LLM judge on held-out human gold.
* [ ] Generate rank probabilities rather than a point leaderboard.
* [ ] Trace every paper table and figure to source hashes and metric versions.
* [ ] Package raw artifacts, analysis tables, figures, manifests, code, and data dictionary together.
* [ ] Do not submit any sentence that turns the two canonical games into a prevalence estimate or model ranking.

[1]: https://arxiv.org/abs/2308.03688?utm_source=chatgpt.com "AgentBench: Evaluating LLMs as Agents"
[2]: https://arxiv.org/abs/2406.12045?utm_source=chatgpt.com "$τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
[3]: https://arxiv.org/abs/2601.12294?utm_source=chatgpt.com "ToolPRMBench: Evaluating and Advancing Process Reward Models for Tool-using Agents"
[4]: https://arxiv.org/abs/2504.08942?utm_source=chatgpt.com "AgentRewardBench: Evaluating Automatic Evaluations of Web Agent Trajectories"
[5]: https://arxiv.org/abs/2502.15840?utm_source=chatgpt.com "Vending-Bench: A Benchmark for Long-Term Coherence of Autonomous Agents"
[6]: https://andonlabs.com/evals/vending-bench-arena?utm_source=chatgpt.com "Vending-Bench Arena"
[7]: https://arxiv.org/abs/2604.05523?utm_source=chatgpt.com "Market-Bench: Benchmarking Large Language Models on Economic and Trade Competition"
[8]: https://arxiv.org/abs/2604.23897?utm_source=chatgpt.com "MarketBench: Evaluating AI Agents as Market Participants"
[9]: https://arxiv.org/abs/2605.14537?utm_source=chatgpt.com "Cattle Trade: A Multi-Agent Benchmark for LLM Bluffing, Bidding, and Bargaining"
[10]: https://arxiv.org/abs/2510.02209?utm_source=chatgpt.com "StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?"
[11]: https://arxiv.org/abs/2403.11807?utm_source=chatgpt.com "How Far Are We on the Decision-Making of LLMs? Evaluating LLMs' Gaming Ability in Multi-Agent Environments"
[12]: https://arxiv.org/abs/2503.06047?utm_source=chatgpt.com "DSGBench: A Diverse Strategic Game Benchmark for Evaluating LLM-based Agents in Complex Decision-Making Environments"
[13]: https://arxiv.org/abs/2605.04312?utm_source=chatgpt.com "Agent Island: A Saturation- and Contamination-Resistant Benchmark from Multiagent Games"
[14]: https://www.nature.com/articles/s41562-025-02172-y?utm_source=chatgpt.com "Playing repeated games with large language models"
[15]: https://arxiv.org/abs/2310.11667?utm_source=chatgpt.com "SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents"
[16]: https://www.science.org/doi/10.1126/science.ade9097?utm_source=chatgpt.com "Human-level play in the game of Diplomacy by combining ..."
[17]: https://arxiv.org/abs/1706.05125?utm_source=chatgpt.com "Deal or No Deal? End-to-End Learning for Negotiation Dialogues"
[18]: https://arxiv.org/abs/2402.15813?utm_source=chatgpt.com "Measuring Bargaining Abilities of LLMs: A Benchmark and A Buyer-Enhancement Method"
[19]: https://arxiv.org/abs/2304.03279?utm_source=chatgpt.com "Do the Rewards Justify the Means? Measuring Trade-Offs Between Rewards and Ethical Behavior in the MACHIAVELLI Benchmark"
[20]: https://arxiv.org/abs/2308.14752?utm_source=chatgpt.com "AI Deception: A Survey of Examples, Risks, and Potential Solutions"
[21]: https://arxiv.org/abs/2404.00806?utm_source=chatgpt.com "Algorithmic Collusion by Large Language Models"
[22]: https://arxiv.org/abs/2601.08462?utm_source=chatgpt.com "M3-BENCH: Process-Aware Evaluation of LLM Agents Social Behaviors in Mixed-Motive Games"
[23]: https://arxiv.org/abs/2509.23023?utm_source=chatgpt.com "Deceive, Detect, and Disclose: Large Language Models Play Mini-Mafia"
[24]: https://arxiv.org/abs/2103.00683?utm_source=chatgpt.com "Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach"
[25]: https://www.researchgate.net/publication/257947135_Monopoly_as_a_Markov_Process?utm_source=chatgpt.com "(PDF) Monopoly as a Markov Process"
[26]: https://arxiv.org/abs/2411.16594?utm_source=chatgpt.com "From Generation to Judgment: Opportunities and Challenges of LLM-as-a-judge"
[27]: https://arxiv.org/abs/2502.01534?utm_source=chatgpt.com "Preference Leakage: A Contamination Problem in LLM-as-a-judge"
[28]: https://openrouter.ai/docs/guides/best-practices/reasoning-tokens?utm_source=chatgpt.com "Reasoning Tokens - Improve AI Model Decision Making"
[29]: https://openrouter.ai/docs/guides/routing/provider-selection?utm_source=chatgpt.com "Provider Routing - Smart Multi-Provider Request ..."
