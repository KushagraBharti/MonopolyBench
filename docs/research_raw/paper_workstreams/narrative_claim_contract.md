# MonopolyBench narrative architecture and claim contract

Date: 2026-07-28  
Scope: publication narrative for an AAAI/IEEE-style benchmark-and-measurement paper  
Evidence status: eight-game pilot/mechanism corpus; not a leaderboard  
Manuscript source audited: `monopolybench_ieee_draft_v0_1.tex`

## Executive decision

The paper should be written as an **audit-ready measurement paper about long-horizon economic agency**, not as a paper about which model plays Monopoly best.

The strongest defensible thesis is:

> **MonopolyBench makes long-horizon economic agency auditable by coupling an engine-authoritative, legal-action-constrained multi-agent asset economy with a replay and provenance contract that links each model attempt to a decision, applied action, event range, state trajectory, communication artifact, and recorded cost. The current eight-game corpus validates that this measurement architecture can expose named mechanisms of accumulation, conversion, liquidity pressure, negotiation, reliability failure, and collapse; it does not estimate model rankings or mechanism prevalence.**

This thesis survives every known evidence limitation:

- it does not require the eight games to be balanced;
- it does not claim deterministic regeneration of model outputs;
- it does not turn a state-valid/strict-artifact-failed run into a replay-clean run;
- it does not require a hidden strategic-value oracle;
- it does not claim that model-authored private text is ground-truth intent;
- it does not require the planned micro-scenario suite to be complete; and
- it makes the artifact and claim discipline—not a model leaderboard—the scientific contribution.

The paper's core story should therefore be:

```text
terminal scores hide process
        ↓
Monopoly supplies a compact asset-and-solvency economy
        ↓
engine-generated legal menus separate strategy from rule mutation
        ↓
decision → attempt → action → event → state links make trajectories auditable
        ↓
split state/artifact replay distinguishes economic reproducibility from provenance fidelity
        ↓
eight audited games demonstrate mechanism visibility
        ↓
balanced seed/seat experiments are the next inferential stage, not a claim already earned
```

## Evidence registry

Use these evidence keys in notes, LaTeX comments, figure scripts, and claim-review checklists. Published prose may cite an artifact-availability appendix rather than expose repository paths inline, but the source mapping must remain in the manuscript source or paper evidence ledger.

### System and method evidence

- **E-SYSTEM:** `AGENTS.md`, especially “Core Invariants,” “Protocol Objects,” “Prompt And LLM Policy,” and “Artifact Policy.” This is the controlling architecture contract for engine authority, legal actions, state mutation, event emission, replay, and downstream-only analysis labels.
- **E-METRICS:** `analysis/analysis.md`, especially “Publication Boundary,” “Paper-Ready Metric Hierarchy,” “Metric Computation Principles,” “Claim Packages And Evidence Standards,” and “Threats To Validity.”
- **E-PROCESS:** `analysis/analysis_process.md`, especially “Analyst Reading Order,” “Claim Strength Levels,” Phases 1–3, “Replay Interpretation,” “Publication Gate,” and “Analysis Modes.”
- **E-AUTOMATION:** `analysis/analysis_automated.md`, especially “Current Automation Map,” “Source-To-Output Map,” “Current Automation Limits,” and “Research Readiness Checklist.”

### Corpus evidence

- **E-CORPUS:** `docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv`. This is the compact source for the eight run IDs, seeds, turn caps, seat orders, turns, winners, decisions, attempts, retries, invalid attempts, fallbacks, recorded tokens, recorded costs, and state/artifact replay status. Its total row records 8 games, 1,391 playable turns, 3,696 decisions, 3,790 model attempts, 94 retries, 100 invalid attempts, 6 deterministic fallbacks, 20,474,750 recorded tokens, and \$113.84159595 recorded cost; all eight pass state replay and seven pass strict artifact replay.
- **E-HANDOFF:** `docs/research_raw/monopolybench_research_handoff_2026-07-28.md`, especially Sections 2–9 and 14. This supplies the authority order, exact eight-game ledger, roster/seat/cap imbalance, mechanism atlas, manuscript corrections, and safe/unsafe claim ladder.

### Replay evidence

- **E-R191-INTEGRITY:** `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/analysis/reports/integrity_report.md`.
- **E-R191-REPLAY:** `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/run/replay_report.json` and `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/analysis/quality/replay_verification.json`.
- **E-R191-IDS:** event `mock-83265-81ed4937-evt-000669`; decision `mock-83265-81ed4937-dec-000096`. The original `LLM_DECISION_RESPONSE` preserves `valid=false` and `error="fallback:illogical_after_retry"` for applied action `reject_trade`; replay reconstructs the same action as `valid=true`, `error=null`. State replay passes 1,640 state-relevant events; strict artifact replay first differs at sequence 669; there are no missing or extra actions and no decision-ID mismatch.
- **E-R273-INTEGRITY:** `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/reports/integrity_report.md`. State replay passes 1,942/1,942 state-relevant events and strict artifact replay passes 4,102/4,102 events.

### Mechanism evidence

- **E-SOLVENCY-FALLBACK-115:** `saved_games/frontier-115-mock-321229807-87ca99d7-gemini-3-1-pro-preview/analysis/reports/case_studies.md`, Case 4. Threat construction `dec-000321`; liquidation `dec-000327`–`dec-000330`; post-transfer `dec-000331`; event sequence 2,136–2,214. At `dec-000330`, the legal house-sale line raised \$200 against a \$197 shortfall, but two schema-invalid attempts led to deterministic bankruptcy fallback. The supported counterfactual stops at immediate solvency with \$3; it does not establish later survival or a different winner.
- **E-SOLVENCY-FALLBACK-172:** `saved_games/frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview/analysis/reports/case_studies.md`, Case 6. Decision `mock-2413970733-53b199c1-dec-000582`; event sequence 3,818–3,830. Selling one house from each red was in the legal menu and raised \$225 against a \$187 shortfall; malformed output caused fallback bankruptcy. The claim is immediate-menu avoidability only.
- **E-BLOCKER-CONVERSION-157:** `saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/analysis/reports/case_studies.md`, Cases 2–4. The early option-creating exchange is `mock-64394-c3bb8d94-dec-000083`–`000086`, events 587–621. The Pacific auction and reciprocal Atlantic/Pacific exchange are `dec-000251`–`000265`, events 1,860–1,959. The later New York/Kentucky swap and orange conversion are `dec-000296`–`000305`, events 2,099–2,279.
- **E-CREDITOR-COMPOUNDING-163:** `saved_games/frontier-163-mock-1038910349-f66fa07c-claude-opus-4-8/analysis/reports/case_studies.md`, Cases 1 and 4. The light-blue trade/build sequence is `dec-000120`–`000124`, `trade-0025`, events 852–875. The creditor-transfer and red development sequence is `dec-000257`–`000267`, events 1,880–1,967.
- **E-HOUSE-SCARCITY-273:** `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/reports/case_studies.md`, CS-08 and CS-09. The New York exchange and finite-house sequence is `dec-000395`–`000422`, events beginning at 2,865, with snapshots `turn_0167.json`–`turn_0180.json`. The distress-sale feedback sequence is `dec-000514`–`000532`, events 3,878–4,028.
- **E-OVERDEVELOPMENT-273:** the same Run 273 case-study file, CS-05. `dec-000285`–`000293`, events 2,004–2,071, snapshots `turn_0108.json` and `turn_0109.json`. The observed one-turn build/hotel sequence was followed by next-roll liquidation and bankruptcy; `end_turn` was a legal accounting alternative, but eventual survival is not established.
- **E-COMMUNICATION-172:** `saved_games/frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview/analysis/reports/case_studies.md`, Case 5; `analysis/review/communication_claims.csv`; and `analysis/review/promise_lifecycle.csv`. Acquisition `dec-000545`–`000548`; immediate resale `dec-000551`–`000556`. This is a high-confidence single-reviewer D3 candidate, not an adjudicated deception finding.

Every qualitative claim should additionally resolve through the corresponding `analysis/review/evidence_index.csv`. The case-study Markdown is a readable index, not a replacement for events, actions, decisions, prompts/responses, and snapshots.

## Contribution hierarchy

The contribution order should determine title, abstract order, section space, and what survives a page-limit cut.

### Contribution 1 — Audit-ready measurement contract

**Headline contribution.** MonopolyBench defines a stable evidence path from engine-produced legal decision menus through model attempts, validation/retry/fallback, applied actions, emitted events, state checkpoints, communication artifacts, usage/cost records, and replay reports. The paper should emphasize that this contract separates:

1. economic outcome;
2. decision-process behavior; and
3. systems reliability/provenance.

This is stronger than “we log trajectories.” It says what each object proves and what it does not prove. Decisions establish the available choice surface. Attempts establish what the model returned and whether correction was needed. Actions establish what was applied. Events establish what happened. Snapshots checkpoint authoritative state. Replay tests reconstruction. This contribution is grounded in E-SYSTEM, E-PROCESS, and E-AUTOMATION.

### Contribution 2 — A compact asset-and-solvency environment for long-horizon agency

MonopolyBench places multiple language-model agents in an engine-authoritative economy with durable assets, recurring rents, bilateral transfers, auctions, mortgages, finite development inventory, forced liquidation, and bankruptcy. Natural-language communication is tied to enforceable economic actions rather than evaluated as dialogue alone.

The novelty claim is the **conjunction** of these features with the measurement contract. Do not claim novelty for any individual ingredient. Vending, strategic-game, negotiation, auction, market, social-agent, and prior Monopoly work already cover neighboring pieces.

### Contribution 3 — A layered evaluation and claim-gating methodology

The paper should define four evidence layers:

1. **Canonical observed facts:** state, legal menus, applied actions, events, usage, replay.
2. **Deterministic derived metrics:** versioned accounting and episode measures.
3. **Bounded counterfactuals:** only under declared action, horizon, continuation-policy, and randomness contracts.
4. **Qualitative interpretation:** evidence-indexed mechanism and communication review with explicit uncertainty.

This hierarchy replaces the draft's broad opposition to “a hidden heuristic oracle.” The position should be positive: different questions require different evidence layers. One-step solvency arithmetic is not the same estimand as a scripted branch rollout; neither is equivalent to a human strategic interpretation.

### Contribution 4 — Pilot validation through an eight-game mechanism corpus

The eight completed bankruptcy games validate artifact completeness, state replay, strict artifact replay in seven cases, attempt accounting, and evidence-indexed trajectory review. They also instantiate mechanisms including ownership-to-development conversion, blocker exchange, finite-house constraints, creditor-transfer compounding, and reliability failures at solvency decisions. These are **existence demonstrations in named trajectories**, not estimates of prevalence, provider traits, or model rank. See E-CORPUS and the mechanism keys above.

### Contribution 5 — Protocol for the inferential study

The balanced seed-block/seat-rotation design and the full-game-to-frozen-fixture bridge are valuable methodological specifications, but they should appear after the validated instrument and pilot. Until the campaign and suite are frozen and run, describe them as the **evaluation protocol enabled by the benchmark**, not as completed empirical contributions.

If space is tight, Contribution 5 moves to an appendix. Contributions 1–4 must remain.

## Venue-neutral section architecture

The budget below targets an eight-page, two-column main body excluding references. Word counts are prose targets, not literal page guarantees; figures and tables consume the remaining equivalent space. A seven-page venue can remove the detailed future-protocol section and compress the pilot from three vignettes to two.

| Section | Purpose | Target words | Main-body page equivalent | Required visual/table |
|---|---|---:|---:|---|
| Abstract | Problem, instrument, exact pilot scope, replay result, non-ranking boundary | 210–240 | 0.35 | None |
| 1. Introduction | Gap, research object, measurement thesis, pilot role, contributions | 800–950 | 1.10 | None |
| 2. Related Work and Novelty Boundary | Position against long-horizon business agents, strategic/economic games, negotiation/social behavior, and Monopoly RL | 550–700 | 0.75 | Dimensional comparison table |
| 3. Benchmark and Evidence Contract | Environment, engine authority, legal decisions, attempts/actions/events/states, communication, split replay, frozen package contract | 950–1,100 | 1.35 | Architecture/evidence-flow figure |
| 4. Evaluation Methodology | Evidence layers, outcome/mechanism/reliability metrics, units and denominators, qualitative review, claim gates | 700–850 | 1.00 | Compact evidence-layer or claim-gate table |
| 5. Pilot Corpus and Mechanism Case Studies | Exact corpus ledger, integrity summary, 2–3 named mechanisms, explicit non-ranking boundary | 1,050–1,250 | 1.65 | Corpus/integrity table; one trajectory figure; one mechanism figure |
| 6. Inferential Evaluation Protocol | Seed blocks, seat rotations, fixed roster/version, censoring, rank/trajectory estimands, micro-fixture bridge | 450–600 | 0.65 | Small design schematic or no visual |
| 7. Discussion, Limitations, and Ethics | What the instrument measures, external validity, provider drift, oracle limits, communication-label limits, trademark/game framing | 550–700 | 0.85 | None |
| 8. Conclusion | Instrument claim and next empirical step | 130–180 | 0.20 | None |
| **Total prose** |  | **5,390–6,570** | **7.90 including visuals/tables** | 4–5 main visuals/tables |

### Recommended results narrative

Use one corpus table and three complementary vignettes:

1. **Reliability can alter realized solvency without changing the legal engine.** Use Run 115 `dec-000330` or Run 172 `dec-000582`, but not both in full. The exact Tier-0 claim is that a legal sale covered the current shortfall and malformed model output led to fallback bankruptcy. Do not claim the player would have survived the game.
2. **Bargaining converts option value into productive control.** Use Run 157 Cases 2–4 or Run 163 Case 1. Show the chain from fragmented/blocking ownership to a legal exchange, development, and realized rent exposure. Do not describe the trade as globally optimal.
3. **Bankruptcy and finite inventory create feedback, not merely elimination.** Use Run 163 Case 4 for creditor-transfer compounding or Run 273 CS-08/09 for the house-supply mechanism. If both appear, one should be a figure and the other a short paragraph.

Run 191 should appear in the corpus integrity table and replay-methodology discussion. It can support strategic case-study prose because state replay passes, but its strict artifact-provenance defect must be stated exactly. It should not be the first or sole results vignette because reviewers may let the replay caveat dominate the paper.

## Claim ladder

### Tier A — Allowed without qualification beyond ordinary citation

These claims are factual if tied to the listed evidence:

- The engine is authoritative for state mutation and produces legal action menus. (E-SYSTEM)
- Model output is validated before an action is applied; retries and deterministic fallback are recorded. (E-SYSTEM, E-AUTOMATION)
- The stable protocol surface comprises snapshots, events, decisions, and actions. (E-SYSTEM)
- The artifact pipeline records attempt-, decision-, action-, event-, state-, prompt/response-, usage-, cost-, and replay-facing evidence. State only the fields actually present in the released package contract. (E-AUTOMATION; per-run integrity reports)
- Engine state-transition replay is deterministic conditional on the fixed engine/rules/configuration, player identities, seed state, and applied action sequence. (E-SYSTEM, E-PROCESS)
- The pilot corpus contains the exact E-CORPUS totals.
- All eight pilot games pass state replay; seven pass strict artifact replay. (E-CORPUS)
- Run `mock-83265-81ed4937` has the exact sequence-669 provenance mismatch described in E-R191-IDS.
- A named mechanism occurred in a named event/decision window when the prose stays at the level proven by canonical artifacts.

### Tier B — Allowed only with descriptive case-study language

Use “the trace exhibits,” “the reviewed episode illustrates,” “in this run,” or “the pilot corpus contains examples of”:

- ownership being converted into a developed rent engine;
- blocker ownership creating exchange option value;
- a creditor receiving and developing a bankrupt player's assets;
- finite house inventory constraining later development;
- a retry or fallback changing the applied action path;
- ontology errors organizing model-authored rationale and subsequent legal choices;
- public/private mismatch producing a communication-risk candidate;
- differing realized pathways among winners.

Every such sentence needs a run ID plus decision/event window or a direct reference to a table whose rows carry those IDs.

### Tier C — Allowed only as an explicitly labeled hypothesis or future estimand

- productively converted ownership predicts survival better than raw property count;
- liquidity discipline predicts bankruptcy hazard;
- negotiation conversion matters more than proposal volume;
- micro-scenario behavior predicts full-game mechanism failures;
- reasoning volume or cost is associated with decision quality after difficulty controls;
- models differ under a fixed roster;
- communication-risk rates differ by model or game phase.

Required wording: “We hypothesize,” “the pilot motivates,” “the preregistered study will estimate,” or “future balanced runs can test.” Do not place these in the abstract as findings.

### Tier D — Forbidden with the current corpus

- Any provider or model ranking.
- “Model X is better/worse at Monopoly,” more rational, more deceptive, more collusive, or more reliable in general.
- Mechanism prevalence claims such as “losers often,” “winners usually,” or “models tend to.”
- Causal statements that a strategy, trade, bid, house lock, or model rationale caused victory.
- Counterfactual claims beyond the proven horizon, including “the player would have survived” when only the current payment is established.
- “All eight games are replay-clean.”
- “Run 191 replay is pending” or “Run 191 state diverged.”
- “The benchmark is deterministic” without the engine-transition/applied-action qualification.
- “Fixed seed/temperature makes model behavior reproducible.” The completed manifests do not record an explicit temperature request.
- Calling 3,696 decisions “model calls” or calling 3,790 attempts “decisions.”
- Treating `attempts - decisions` as an inferred invalid count when exact attempt outcomes exist.
- Treating recorded cost as a model-intrinsic price independent of route, date, survival duration, decision mix, and missing usage.
- Treating reported reasoning tokens as comparable cognitive effort across providers.
- Treating a model-authored private rationale as hidden chain-of-thought, cognition, knowledge, or intent ground truth.
- Calling the Run 172 D3 candidate “deception” without independent adjudication.
- Calling ordinary reciprocal trade “collusion.”
- Claiming that the planned micro suite is complete, frozen, or empirically evaluated.
- Claiming a hidden scalar strategy heuristic is a ground-truth Monopoly oracle.
- Claiming MonopolyBench is the first long-horizon economic, multi-agent, bargaining, auction, or Monopoly-agent benchmark.
- Claiming direct external validity to real businesses, markets, finance, or human economic competence.

## Terminology contract

Use these substitutions consistently:

| Avoid | Required replacement |
|---|---|
| deterministic benchmark | benchmark with deterministic engine-transition replay conditional on the applied action sequence |
| model call, when counting decisions | engine-produced decision point |
| model call, when counting retries | model attempt |
| replay clean | state-replay clean and/or strict-artifact-replay clean, named separately |
| private thought proves intent | model-authored private rationale reports a plan or belief |
| avoidable bankruptcy | immediate-menu avoidable, short-horizon avoidable under oracle X, or narrative avoidability—name the level |
| cost | recorded provider/OpenRouter cost under the run's route and pricing context |
| token total | recorded token total under preserved provider semantics |
| standard Monopoly | the declared MonopolyBench ruleset, unless rules-completeness is separately enumerated |
| optimal/bad trade | observed transfer and downstream consequences; oracle-qualified value if available |
| winning strategy | realized pathway to survival in this trace |
| models differ | the reviewed traces exhibit different realized pathways |

## Exact abstract replacement in LaTeX

The following is publication-ready at the current evidence level. It is deliberately venue-neutral and does not require the planned micro suite to have results.

```latex
\begin{abstract}
Evaluations of language-model agents often reduce long interactions to task completion or terminal scores, obscuring how valid local choices accumulate into durable advantage, fragility, or failure. We introduce \Bench, an audit-ready environment for studying long-horizon economic agency in a multi-agent asset-and-solvency game. An authoritative rules engine produces legal-action menus and exclusively applies state transitions; language models select actions, communicate, and provide model-authored rationales without directly mutating game state. The resulting evidence contract links every model attempt to its decision, validation outcome, applied action, emitted events, state checkpoints, usage, cost, and replay record. We distinguish deterministic replay of engine transitions from stochastic regeneration of model behavior, and we separately test state replay and strict artifact-provenance replay.

We validate the pipeline on eight pilot games comprising 1,391 playable turns, 3,696 engine-produced decisions, and 3,790 model attempts. All eight games pass state replay; seven also pass strict artifact replay, while the remaining run preserves the applied action and state trajectory but differs in fallback-provenance metadata at one identified event. Evidence-indexed case studies expose mechanisms hidden by final win labels, including conversion of fragmented ownership into developed rent engines, blocker-for-liquidity exchanges, finite-house constraints, creditor-transfer compounding, and serialization failures at solvency decisions. Because the games use unbalanced seats, rosters, model versions, and turn caps, we treat them as a mechanism corpus rather than a leaderboard. \Bench\ contributes an instrument and claim discipline for connecting economic outcomes to inspectable decision processes, reliability, and cost.
% Evidence: E-CORPUS; E-R191-INTEGRITY; E-R273-INTEGRITY;
% E-BLOCKER-CONVERSION-157; E-CREDITOR-COMPOUNDING-163;
% E-HOUSE-SCARCITY-273; E-SOLVENCY-FALLBACK-115; E-SOLVENCY-FALLBACK-172.
\end{abstract}
```

Notes:

- “Audit-ready” is safer and more distinctive than unqualified “deterministic.”
- “Asset-and-solvency game” avoids overstating real-market external validity.
- The final sentence makes the paper's object explicit: instrument plus claim discipline.
- If the venue enforces a 200-word abstract, remove the mechanism list before removing the non-ranking caveat.

## Exact introduction replacement in LaTeX

```latex
\section{Introduction}
\label{sec:introduction}

Language models increasingly act through sequences of state-changing decisions rather than isolated answers. They call tools, negotiate with other actors, allocate resources, and continue from states created by their own earlier choices. In such settings, a terminal success label is an incomplete evaluation. Two agents can reach the same outcome through different levels of capital discipline, coordination, reliability, and cost; conversely, one early decision can remain latent until a failure many turns later. Interactive-agent benchmarks have broadened evaluation beyond static question answering \cite{agentbench,taubench}, while long-horizon business and strategic-game environments have shown the importance of persistent state, competition, and multi-step behavior \cite{vendingbench,dsgbench,cattletrade}. The remaining measurement problem is not only to run a long interaction, but to preserve enough structured evidence to explain how the interaction produced its outcome.

Economic games make this problem concrete. An agent must decide not only whether an action is legal, but how cash, assets, recurring income, bargaining leverage, and insolvency risk interact over time. Monopoly is not a model of a real economy, and performance in it should not be interpreted as business or financial competence. It is nevertheless a useful controlled testbed: durable property rights, auctions, bilateral exchange, development, mortgages, rent shocks, forced liquidation, and bankruptcy create a compact asset-and-solvency system in which earlier choices change later legal and economic constraints. Unlike one-shot bargaining, a complete game contains repeated opportunities to acquire, convert, trade, finance, and liquidate assets. Unlike an unconstrained text game, its state and rules can be made mechanically explicit. Prior work has studied Monopoly with probabilistic and reinforcement-learning methods \cite{monopoly_markov,monopoly_drl}; our focus is the auditable behavior of off-the-shelf language-model agents that also communicate and negotiate.

We introduce \Bench, an engine-authoritative multi-agent environment for studying long-horizon economic agency. The engine exclusively mutates state, generates legal decision menus, and emits the resulting events. A language model receives a model-facing state representation and an explicit action schema, then returns one selected action together with optional public communication and a model-authored private rationale. The orchestration layer validates the response against the current legal menu, performs the configured corrective retry when necessary, and applies a deterministic fallback if correction fails. This design removes illegal state mutation as a confound without supplying a strategy oracle: the agent remains free to choose any action that the engine has declared legal.
% Evidence: E-SYSTEM; E-AUTOMATION.

The primary contribution is an evidence contract for connecting those choices to outcomes. A decision records what the acting player was allowed to do; an attempt records what the model returned and whether it validated; an action records what the engine applied; events record the resulting transition; snapshots checkpoint authoritative state. Prompt/response artifacts, public messages, model-authored private rationales, provider usage, recorded cost, retries, and fallbacks remain linked to the same decision. This separation supports three analyses that should not be conflated: economic outcome, decision-process behavior, and systems reliability. It also supports a split replay oracle. State replay asks whether the state-relevant trajectory can be reconstructed from the applied action sequence. Strict artifact replay additionally compares observational and provenance fields. Neither claim implies deterministic regeneration of provider outputs.
% Evidence: E-SYSTEM; E-PROCESS; E-R191-INTEGRITY; E-R273-INTEGRITY.

We evaluate the instrument using eight completed bankruptcy games as an audited pilot corpus, not as a comparative leaderboard. The games contain 1,391 playable turns, 3,696 engine-produced decisions, 3,790 model attempts, 94 corrective retries, 100 invalid attempts, six deterministic fallbacks, 20,474,750 recorded tokens, and \$113.84159595 in recorded provider cost. All eight pass state replay, and seven pass strict artifact replay. In run \texttt{mock-83265-81ed4937}, strict artifact replay first differs at event \texttt{mock-83265-81ed4937-evt-000669}, decision \texttt{mock-83265-81ed4937-dec-000096}: the original record preserves fallback invalidity metadata for the applied \texttt{reject\_trade} action, whereas replay reconstructs the same applied action as valid. State replay still passes, with no missing or extra action and no decision-ID mismatch.
% Evidence: E-CORPUS; E-R191-IDS.

The pilot's purpose is mechanism visibility. Named trajectories connect fragmented ownership to negotiated control and development, bankruptcy transfers to new productive groups, finite house supply to later build constraints, and malformed solvency responses to deterministic fallback. For example, run \texttt{mock-1038910349-f66fa07c} links a light-blue trade and same-turn construction at decisions \texttt{dec-000120}--\texttt{dec-000124} to later rent and creditor-transfer effects; run \texttt{mock-44910-42ec35c5} records the New York exchange and finite-house sequence at decisions \texttt{dec-000395}--\texttt{dec-000422}; and run \texttt{mock-321229807-87ca99d7} contains a solvency decision at \texttt{dec-000330} where a legal \$200 house sale covered a \$197 current shortfall, but two schema-invalid attempts led to fallback bankruptcy. These examples establish that the artifact system can recover economically meaningful mechanisms. They do not establish that a model, provider, or strategy is generally superior, nor do they establish counterfactual outcomes beyond the immediate legal effects.
% Evidence: E-CREDITOR-COMPOUNDING-163; E-HOUSE-SCARCITY-273;
% E-SOLVENCY-FALLBACK-115.

This paper makes four contributions:
\begin{enumerate}
    \item We present an engine-authoritative, legal-action-constrained multi-agent asset-and-solvency environment that joins natural-language interaction to enforceable economic consequences.
    \item We define an audit-ready protocol linking decisions, model attempts, validation, applied actions, events, snapshots, communication, usage, cost, and split state-versus-artifact replay.
    \item We introduce a layered evaluation methodology that separates canonical facts, deterministic derived metrics, bounded counterfactuals, and qualitative interpretation, with explicit claim gates and source identifiers.
    \item We release an eight-game pilot mechanism corpus and use evidence-indexed case studies to validate the measurement pipeline while specifying the balanced seed-block, seat-rotation, and frozen-fixture protocol required for future model comparison.
\end{enumerate}

The paper therefore asks a measurement question before a ranking question: can a long-horizon multi-agent economic outcome be decomposed into inspectable choices, transitions, communication, reliability, and cost? The current corpus answers that instrumentation question and supplies hypotheses for the balanced study; it is not itself the balanced study.
```

### Introduction evidence review

The introduction contains only three empirical blocks:

1. the corpus totals and replay rates, sourced by E-CORPUS;
2. the exact Run 191 replay defect, sourced by E-R191-IDS; and
3. three named mechanism examples, sourced by E-CREDITOR-COMPOUNDING-163, E-HOUSE-SCARCITY-273, and E-SOLVENCY-FALLBACK-115.

Everything else is a system definition, motivation, scoped interpretation, or contribution statement tied to E-SYSTEM/E-PROCESS. This is the correct evidence density for an introduction.

## What to cut, merge, or move from the current manuscript

### Cut from the main paper

1. **The current cross-run “winning behavior is associated with distinct economic profiles” language.** It reads as inference from an unbalanced sample. Replace with “the reviewed traces exhibit named mechanisms.”
2. **The claim that the benchmark already “includes” a targeted micro-scenario suite.** The guides describe a design and runner, but the manuscript table still contains placeholder counts and no frozen results. Reframe as a fixture-extraction/evaluation protocol.
3. **The standalone “Planned Figures and Tables” section.** Planning notes do not belong in a submission.
4. **All `\todo{}` and `\note{}` content.**
5. **“Run A” and “Run B” as the empirical organizing frame.** Two cherry-picked games understate the eight-game corpus and make the paper appear result-selective. Use the corpus ledger first, then mechanism-titled vignettes.
6. **“Apparent winner” and “replay reconciliation pending” for Run 191.** Both are factually obsolete. Use the exact state-pass/artifact-fail wording.
7. **Candidate case-study, candidate framing, and author-note appendices.** These are drafting artifacts, not scholarly appendices.
8. **Any incomplete bibliography entry, especially the current Beer Game/HBR placeholder.** Remove it unless the full primary-source citation is verified.

### Merge

1. Merge **Benchmark Environment**, **System Architecture**, **Decision Loop**, **State/Communication/Memory**, and **Artifacts** into one section titled **Benchmark and Evidence Contract**. The manuscript currently repeats the same separation-of-concerns point several times.
2. Merge **Evaluation Philosophy**, the six metric subsections, and **Descriptive Trace Analysis Rather Than a Hidden Heuristic Oracle** into **Evaluation Methodology** organized by evidence layer and metric role.
3. Merge **Experimental Protocol** and **Claim Gating** into **Inferential Evaluation Protocol**. Claim gates should follow from units, balance, replay quality, and oracle status, not appear as an isolated policy table.
4. Merge **Discussion**, **Economic Agency as the Core Object**, and **Reliability as Instrumentation Rather Than Headline**. The latter two largely restate the introduction.
5. Merge **Limitations** and **Ethical and Safety Considerations** into one compact section unless the venue requires a separate ethics statement.

### Move to appendix or artifact supplement

1. Full artifact filenames and schema fields after the main evidence-flow figure.
2. Per-player final-state, rent, usage, token, cost, and latency tables.
3. Full metric taxonomy, formula variants, and net-worth valuation sensitivity.
4. Detailed D0–D4/C0–C4 communication codebook and reviewer protocol.
5. All eight per-run rows beyond the compact corpus/integrity table.
6. Complete run hashes, provider-route fields, pricing snapshots, and manifest details.
7. The full balanced-design model equations and power-simulation plan.
8. Micro-fixture schema, oracle tiers, action-equivalence tolerances, and branch-RNG contract.
9. Additional mechanism case studies, full event windows, and transcript excerpts.
10. Full replay diff payload for Run 191.

### Keep in the main paper

1. One architecture/evidence-flow figure.
2. One compact comparison table against adjacent benchmarks.
3. One corpus/integrity table with denominators and both replay layers.
4. One trajectory figure from strict-artifact-clean Run 273.
5. One mechanism figure showing a decision/action/event/state chain, preferably the solvency fallback or creditor-transfer sequence.
6. One short claim-gate table.

## Current-section disposition map

| Current section | Disposition | Replacement |
|---|---|---|
| Abstract | Replace completely | Exact abstract above |
| Introduction | Replace completely | Exact introduction above |
| Related Work | Retain but rewrite | Dimensional comparison; add current adjacent primary work; avoid first claims |
| Benchmark Environment | Merge | Benchmark and Evidence Contract |
| Evaluation Design | Rewrite | Four evidence layers plus small metric hierarchy |
| Targeted Micro Scenario Suite | Demote | Full-game-to-fixture protocol; no placeholder result claims |
| Full Game Pilot Runs | Replace | Eight-game corpus table plus mechanism vignettes |
| Descriptive Trace Analysis... | Merge | Evaluation methodology, not standalone advocacy |
| Experimental Protocol | Retain and tighten | Inferential Evaluation Protocol |
| Planned Figures and Tables | Delete | No replacement section |
| Discussion | Compress | Discussion, Limitations, and Ethics |
| Limitations | Merge | Discussion, Limitations, and Ethics |
| Ethical and Safety Considerations | Merge or venue appendix | Communication and external-validity limits |
| Conclusion | Rewrite | Instrument claim, pilot scope, next balanced study |
| Draft Notes / Candidate sections | Delete from submission | Preserve only in research workstream notes |

## Reviewer-risk analysis

### R1. “This is just Monopoly with LLMs.”

**Risk:** Critical.  
**Why reviewers may say it:** The current title and introduction foreground the game before the measurement architecture.  
**Response:** Lead with the audit problem and evidence contract. The comparison table must show the conjunction of legal menus, durable asset transfers, solvency, public/private language, per-attempt records, split replay, cost telemetry, and exhaustive evidence indexes. Do not claim novelty from Monopoly itself.

### R2. “Eight games cannot support model comparison.”

**Risk:** Critical.  
**Evidence:** E-CORPUS records fixed/repeated seat orders, changing model versions, two roster families, and different maximum-turn caps.  
**Response:** Agree structurally, not apologetically: the eight games are a mechanism and pipeline-validation corpus. Remove all ranking/association language. Include the balanced seed-block/seat-rotation design as the next inferential stage.

### R3. “Determinism is overstated.”

**Risk:** Critical.  
**Response:** Define determinism once: engine-transition replay conditional on fixed configuration and applied actions. Explicitly exclude provider-output regeneration. Show state and strict artifact replay as separate tests. Record omitted temperature rather than inferring a default.

### R4. “One of the flagship runs fails replay.”

**Risk:** High.  
**Evidence:** E-R191-IDS.  
**Response:** State the exact bounded defect. The same fallback action is applied and state replay passes; strict provenance differs at one event. Keep Run 191 in the corpus table, use Run 273 for the clean trajectory figure, and use Run 191 only where its state-valid evidence is appropriate.

### R5. “The paper lacks a strategic-quality ground truth or baseline.”

**Risk:** High.  
**Response:** Do not claim global optimality. Present the four evidence layers and distinguish accounting facts, immediate legal solvency, declared branch policies, and qualitative interpretation. Add simple scripted/RL/heuristic baselines only when their estimand is explicit; do not make an unvalidated scalar oracle the foundation of the current paper.

### R6. “The micro suite is vaporware.”

**Risk:** High if presented as completed; low if presented as protocol.  
**Response:** Remove placeholder counts and result language. Describe fixture extraction as a protocol enabled by full-game artifacts. If no frozen suite is available by submission, keep it to one subsection or appendix and do not list it as an empirical contribution.

### R7. “The artifact pipeline is large but scientifically unfocused.”

**Risk:** High.  
**Response:** Organize artifacts by proof obligation, not filename inventory: legal opportunity, model response, applied action, realized transition, state checkpoint, operational metadata, replay. The main paper needs one evidence-flow figure and one claim-gate table; exhaustive filenames belong in the supplement.

### R8. “The selected mechanisms are cherry-picked.”

**Risk:** High.  
**Response:** State the selection rule: mechanism diversity, evidence completeness, and complementary proof obligations—not model favorability. Show the full eight-run corpus table. Include both strong play and failure, and distinguish discovery examples from prevalence claims.

### R9. “Private rationales are unreliable or resemble chain-of-thought claims.”

**Risk:** High.  
**Response:** Use “model-authored private rationale” throughout. Treat it as a generated artifact that can be compared with public text and action, not as direct cognition or hidden chain-of-thought. Do not release or interpret it beyond the declared research policy without a privacy/release statement.

### R10. “Deception/collusion claims are sensational and under-validated.”

**Risk:** High.  
**Response:** Keep communication findings case-study-only. Preserve D/C levels, benign alternatives, reviewer confidence, and adjudication status. The Run 172 episode remains a D3 candidate, not a settled deception claim. Do not publish prevalence tables without opportunity denominators and independent human adjudication.

### R11. “Net worth and strategic value are arbitrary.”

**Risk:** Medium-high.  
**Response:** Version the accounting convention, show components, and distinguish accounting net worth from liquidation value and continuation value. Avoid using net worth as the sole outcome. Survival order, productive development, rent flow, liquidity, and reliability should remain separate dimensions.

### R12. “Cost comparisons are confounded.”

**Risk:** Medium-high.  
**Response:** Call them recorded route/date-specific costs. Report cost per decision and common-horizon sensitivity, preserve missing usage, and avoid treating reasoning tokens as comparable compute across providers. Total cost in the pilot validates accounting scale; it does not establish cost efficiency by model.

### R13. “Opponent dependence and multiplayer statistics are mishandled.”

**Risk:** Medium-high.  
**Response:** State that the independent unit is the game or seed block, not the decision. Use seat-balanced blocks, roster-relative estimands, and rank/survival models with clustered uncertainty in the future study. Never treat four player rows from one game as independent replicates.

### R14. “External validity is weak.”

**Risk:** Medium.  
**Response:** Concede that Monopoly is a stylized asset-and-solvency environment. Claim measurement of behavior inside that environment, not real-world business competence. External validation against independent economic-agent tasks is future work.

### R15. “Rules completeness, trademarks, and licensing are unclear.”

**Risk:** Medium.  
**Response:** Say “declared MonopolyBench ruleset” unless the supplement enumerates official-rule correspondence and deviations. Add a trademark/non-affiliation note if advised by the venue or counsel. Ensure released board assets and citations comply with project licensing.

### R16. “Provider/model drift prevents reproduction.”

**Risk:** Medium.  
**Response:** Separate frozen-run reproducibility from fresh endpoint regeneration. Release exact model slugs, resolved provider metadata where available, date, route policy, request facts, prompt/tool hashes, engine commit, and artifact hashes. The frozen run remains auditable even if the endpoint changes.

## Submission-facing title recommendations

Preferred:

> **MonopolyBench: Auditing Long-Horizon Economic Agency in Multi-Agent Language Models**

Alternative, more measurement-forward:

> **From Decisions to Collapse: Audit-Ready Evaluation of Economic Agency in Multi-Agent Language Models**

Avoid:

- “Evaluating Long Horizon Economic Agency...” without “auditing” or another measurement signal;
- “A Deterministic Benchmark...” because model behavior is not deterministically regenerated;
- titles that name frontier models or imply a leaderboard.

## Final author checklist

Before the root TeX is revised:

1. Accept the thesis and contribution order in this contract.
2. Replace abstract and introduction wholesale rather than line-editing the current framing.
3. Build the corpus/integrity table directly from E-CORPUS.
4. Choose two or three mechanism vignettes and preserve their exact decision/event windows.
5. Use Run 273 for the primary replay-clean trajectory figure.
6. Preserve the exact Run 191 sequence-669 statement wherever the run appears.
7. Add the current adjacent-work comparison and remove all “first” implications.
8. Version the net-worth and cost semantics used by every paper table.
9. Ensure every rate exposes numerator, denominator, eligibility, unresolved cases, and censoring.
10. Remove placeholders, draft notes, candidate appendices, and incomplete references.
11. Add artifact/code availability, source commit, package hashes, and replay-status documentation.
12. Conduct a final sentence-level claim audit using Tiers A–D above.

## Bottom line

The paper becomes publishable when it stops asking the pilot corpus to prove which model is best and instead shows, rigorously, **what evidence is required to explain a long-horizon multi-agent economic outcome**. MonopolyBench's defensible contribution is the coupling of a legally constrained economic environment with a precise, replay-aware evidence and claim contract. The eight games are valuable because they demonstrate that this instrument can recover mechanisms that a win label erases. Their scientific role is demonstration and hypothesis generation; balanced comparison comes next.
