# Methods, protocol, reproducibility, and evaluation-design workstream

Date: 2026-07-28  
Scope: paper prose and research design only  
Target manuscript: `monopolybench_ieee_draft_v0_1.tex`  
Frozen evidence: read-only; no `run/`, `quality_check/`, code, or root TeX was modified

## Executive handoff

The paper should describe MonopolyBench as a **deterministic-transition benchmark with stochastic, provider-mediated action generation**. The rules engine is authoritative: it produces decision points and legal actions, applies one structured action per decision, mutates state, and emits events. The model is not replayed to reproduce a completed game. A completed game is replayed by reconstructing its initial configuration and reapplying its recorded action sequence.

This yields two distinct reproducibility tests:

1. **State replay** asks whether state-relevant engine transitions match after the documented canonicalization.
2. **Strict artifact replay** asks whether the entire event stream, including model-observation and provenance fields, matches.

Those tests must never be collapsed. Run 191 (`mock-83265-81ed4937`) has aggregate status `state_passed_artifact_failed`: state replay passes across 1,640 state-relevant events, while strict artifact replay first differs at sequence 669. The original `LLM_DECISION_RESPONSE` for decision `mock-83265-81ed4937-dec-000096` records the fallback-applied `reject_trade` action as `valid=false` with `error="fallback:illogical_after_retry"`; replay reconstructs the same applied action as `valid=true` with `error=null`. There are no missing or extra actions and no decision-ID mismatch. The defect is therefore bounded to fallback provenance, not state progression. Run 191 can support state-grounded, explicitly qualified case-study claims; it cannot be called strict-artifact-clean.

The current eight-game corpus is an audited descriptive corpus, not a balanced leaderboard. It contains 1,391 playable turns, 3,696 engine-produced decisions, 3,790 model attempts, 94 corrective retries, 100 invalid attempts, six deterministic fallbacks, 20,474,750 recorded tokens, and \$113.84159595 in recorded cost. All eight games pass state replay and seven pass strict artifact replay. Seats, rosters, endpoint versions, and model versions are unbalanced, so the corpus supports instrumentation, integrity, cost, reliability, and named mechanism case studies—not provider rankings, population prevalence, or causal strategy claims.

## Sources audited

The following were read completely or inspected as the controlling structured artifacts:

- `AGENTS.md`
- `monopolybench_ieee_draft_v0_1.tex`
- `monopolybench.tex` (the untouched IEEE template at the canonical root)
- `analysis/analysis.md`
- `analysis/analysis_process.md`
- `analysis/analysis_automated.md`
- `docs/artifact_reference.md`
- `docs/research_raw/monopolybench_research_handoff_2026-07-28.md`
- Run 191 and Run 273 `analysis/reports/integrity_report.md`
- Run 191 and Run 273 standard-analysis, generated-output, and qualitative-review manifests
- Run 191 and Run 273 `analysis/quality/replay_verification.json`
- representative `events.jsonl`, `actions.jsonl`, `decisions.jsonl`, `usage_attempts.jsonl`, snapshots, `run_config.json`, and `experiment_manifest.json`
- both canonical `semantic_metric_status.json` files

Evidence authority follows the repository order: events, actions, decisions, prompt/response artifacts, snapshots, frozen quality-check artifacts, deterministic analysis outputs, human review outputs, and only then manuscript prose.

## Non-negotiable methodological positions

1. Say **deterministic engine transition replay**, not “deterministic LLM benchmark” without qualification.
2. A decision, an attempt, an applied action, and an event are different units. Retries increase attempts, not decisions.
3. The independent replication unit is the game or randomized seed-seat block, not the turn, decision, call, or player row.
4. State replay and strict artifact replay are separate gates.
5. Public messages and private rationales are logged model artifacts. A private rationale is not direct access to cognition or ground-truth intent.
6. Human-reviewed semantic labels and oracle-dependent counterfactual quantities must remain downstream of the model-facing prompt.
7. Exact provider request facts must be reported as sent or omitted. The frozen eight-game manifests record nominal OpenRouter reasoning effort `medium`, no explicit output/reasoning-token budget, and no explicit `temperature` request field.
8. The four paper-facing evaluation layers are: primary endpoints, secondary mechanisms, diagnostic integrity/operations, and exploratory behavioral evidence. Oracle-dependent regret and counterfactual value remain a separately named future layer until implemented and validated.
9. Every rate must expose numerator, denominator, eligibility rule, unresolved count, missingness, and censoring rule.
10. Every table row and plotted mark must resolve through a generated table to raw IDs and frozen hashes.

## Drop-in publication-ready LaTeX

The following blocks use packages already loaded by the current IEEE draft (`amsmath`, `booktabs`, `tabularx`, and `array`). Labels can be renamed during integration.

### Benchmark environment and protocol objects

```latex
\section{Benchmark Environment}
\label{sec:environment}

\subsection{Environment and Authority Boundary}

\Bench\ is a four-player, turn-based asset-and-solvency environment implementing
the configured Monopoly ruleset, including seeded movement and card draws,
property acquisition, auctions, bilateral trades, color-group development,
rent, jail, mortgages, legal liquidation, and bankruptcy. A game terminates
when one player remains solvent or when a predeclared run cap is reached.
Endpoint semantics are part of the experimental configuration: in a bankruptcy
game the winner is the last non-bankrupt player, whereas players still active
at a run cap are treated as right-censored for bankruptcy analyses.

The rules engine is the sole authority over game state. It generates legal
decision menus, validates and applies structured actions, advances seeded
random processes, and emits append-only events. Language-model agents cannot
mutate state directly and may select only from the legal actions exposed for
the current decision. The arena constructs model requests and handles response
parsing, validation, one configured corrective retry, and deterministic
fallback. Telemetry records the resulting protocol objects and provider
metadata. The API streams server state, and the frontend renders that state
without implementing rules or inferring legality.

\subsection{Protocol Objects}

Four objects form the stable replay and explanation boundary. A snapshot is an
authoritative serialized checkpoint. An event is an ordered state transition
or major marker. A decision records the acting player, decision type,
model-visible context, legal choice surface, attempts, and resolution metadata.
An action is the structured move applied for that decision. Table~\ref{tab:protocol}
states the corresponding identifiers and artifact surfaces.

\begin{table*}[t]
\caption{Stable protocol objects and their traceability fields. Fields shown
are the minimum join surface used by the released artifacts.}
\label{tab:protocol}
\centering
\small
\begin{tabularx}{\textwidth}{p{0.12\textwidth}p{0.19\textwidth}Xp{0.20\textwidth}}
\toprule
\textbf{Object} & \textbf{Authority} & \textbf{Key fields and joins} & \textbf{Canonical artifact} \\
\midrule
Snapshot & Engine & \texttt{run\_id}, \texttt{turn\_index}, phase,
active player, players, bank, board, auction, and trade state &
\texttt{state/turn\_*.json} \\
Event & Engine & \texttt{run\_id}, \texttt{event\_id}, contiguous
\texttt{seq}, \texttt{turn\_index}, actor, type, and payload; decision-linked
events carry \texttt{decision\_id} in their payload &
\texttt{events.jsonl} \\
Decision & Engine/arena & \texttt{decision\_id}, type, player, turn,
model identifiers, prompt payload, nested attempts, validation outcomes,
retry/fallback fields, final action, and emitted event sequence range &
\texttt{decisions.jsonl} \\
Action & Engine input & \texttt{decision\_id}, actor, decision type, turn,
action name, arguments, public message, and private rationale &
\texttt{actions.jsonl} \\
\bottomrule
\end{tabularx}
\end{table*}

\subsection{Decision Loop}
\label{sec:decision_loop}

For decision \(d\), the engine emits a menu \(A_d\) of legal structured
actions for one acting player. The arena serializes the model-visible state,
bounded history, communication fields, and legal action schemas, and queries
the configured OpenRouter endpoint. An attempt is accepted only if it parses,
satisfies the tool schema, and matches the current legal menu. If the initial
attempt is invalid, the arena performs the configured corrective retry.
If no valid action is recovered, a deterministic fallback selects an action
from \(A_d\). Exactly one action is then applied, and the engine emits the
resulting events. Telemetry writes the decision, every attempt, the applied
action, emitted event identifiers and sequence range, state checkpoints,
usage, cost, latency, and validation or fallback provenance.

Thus a \emph{decision} is one engine-produced choice point; an \emph{attempt}
is one provider response for that decision; an \emph{action} is the single
structured move ultimately applied; and an \emph{event} is an emitted
consequence or marker. Corrective retries increase the attempt count but do
not create additional decisions or applied actions.
```

### Artifact and replay contract

```latex
\subsection{Artifact and Replay Contract}
\label{sec:artifact_contract}

Each released saved game is self-contained. The frozen evidence layer contains
the raw \texttt{run/} tree and the human-readable \texttt{quality\_check/}
tree. The run tree includes ordered events, applied actions, decisions and
attempts, prompt/response artifacts, snapshots, run and seat configuration,
provider usage and cost, scorecards, and replay reports. Source manifests
record exact file inventories, byte counts, and SHA-256 hashes. A downstream
\texttt{analysis/} tree contains deterministically generated tables and plots,
integrity and coverage reports, episode reconstructions, evidence-indexed
qualitative review, validation outputs, and generated-output manifests.
Derived analysis may be regenerated, but frozen run and quality-check files
are never rewritten.

Replay uses the recorded applied-action sequence rather than new model calls.
Given the same engine version, engine seed, settings, player identities, and
applied actions, the verifier reconstructs the event trajectory. We report two
non-interchangeable results. \emph{State replay} compares state-relevant
events after excluding model-observation events and normalizing global event
identifier, sequence, and timestamp fields to a state-event index.
\emph{Strict artifact replay} compares the canonicalized full event stream,
including model request/response, public-message, private-rationale, and
fallback-provenance events. The aggregate report preserves both
\texttt{state\_status} and \texttt{artifact\_status}; a run may therefore be
\texttt{state\_passed\_artifact\_failed}.

This distinction is material in Run~191
(\texttt{mock-83265-81ed4937}). State replay matches all 1,640 state-relevant
events. Strict artifact replay first differs at sequence 669, where the
original log preserves a fallback-applied \texttt{reject\_trade} response as
\texttt{valid=false} with
\texttt{error=fallback:illogical\_after\_retry}, while replay reconstructs
the same applied action as valid with no error. No action is missing or extra,
and decision identifiers reconcile. We therefore classify the run as
state-valid but not strict-artifact-clean.
```

### Four-layer evaluation hierarchy

```latex
\section{Evaluation Design}
\label{sec:evaluation}

\subsection{Evaluation Hierarchy}

We organize evaluation into four layers rather than a single composite score.
The hierarchy separates game outcomes, mechanisms, operational validity, and
semantically interpreted behavior.

\begin{table*}[t]
\caption{Four-layer evaluation hierarchy. Availability refers to the evidence
required before a quantity can support a paper claim.}
\label{tab:evaluation_hierarchy}
\centering
\small
\begin{tabularx}{\textwidth}{p{0.17\textwidth}p{0.27\textwidth}Xp{0.20\textwidth}}
\toprule
\textbf{Layer} & \textbf{Examples} & \textbf{Interpretation} &
\textbf{Evidence requirement} \\
\midrule
Primary endpoints & Survival winner and order, terminal balance-sheet value,
normalized trajectory AUC, first-attempt validity, cost per decision &
Answers the preregistered outcome and deployment questions; model comparisons
require balanced replication. & Frozen complete runs, state replay, declared
endpoint and valuation, seed-seat inference. \\
Secondary mechanisms & Monopoly completion and development, realized rent,
liquidity and liquidation, negotiation and auction episodes, mortgage use &
Explains how an observed outcome developed; does not by itself establish
optimality or causality. & Exact episodes and source IDs; replication for
prevalence; oracle only when counterfactual language is used. \\
Diagnostic integrity and operations & State/artifact replay, invalid attempts,
retries, fallbacks, missing usage, tokens, cost, latency, provider route &
Measures research-artifact health and structured-agent operability separately
from economic quality. & Attempt-level reconciliation and raw provider
semantics with missingness preserved. \\
Exploratory behavioral evidence & Factual errors, public/private mismatch,
promise lifecycle, deception and collusion candidates, negotiation style &
Supports evidence-linked cases and hypothesis generation, not automatic trait
or prevalence claims. & Human review, source citations, alternatives,
confidence, and adjudication for high-risk labels. \\
\bottomrule
\end{tabularx}
\end{table*}

Oracle-dependent regret, trade surplus, avoidable-bankruptcy counterfactuals,
and branch values are not silently folded into these layers. When reported,
they must name the oracle tier, value convention, horizon, continuation policy,
randomness coupling, and sensitivity interval. Until such an oracle is
implemented and validated, these fields remain null or are labeled as
reviewed tactical assessments rather than ground-truth action values.
```

### Full-game protocol and statistical design

```latex
\section{Full-Game Experimental Protocol}
\label{sec:protocol}

\subsection{Treatment Definition and Run Freezing}

Before a study block begins, we freeze the engine and contract versions,
ruleset and endpoint policy, exact model identifiers, player identities,
system and user prompt templates, legal-action schemas and ordering policy,
communication and memory policy, corrective-retry wording, deterministic
fallback policy, provider-routing restrictions, reasoning request, and every
sampling parameter that is explicitly sent. We separately record omitted
parameters rather than replacing them with presumed provider defaults. Each
run records its engine seed, cap, seat assignment, execution date, resolved
provider metadata where available, and pricing snapshot. Failed, incomplete,
and provider-error attempts remain in the systems and cost population.

The engine seed controls engine-side random processes; it does not seed or
determinize provider generation. A nominal reasoning setting or temperature
is a treatment field, not a guarantee of identical future outputs. Execution
order within a study block is randomized to reduce confounding by provider or
backend drift. The benchmark contract is not changed mid-block.

\subsection{Seeds, Seats, and Replication}

For a fixed four-model roster, one seed block consists of a predeclared engine
seed and four cyclic seat rotations, so each model occupies each seat once.
Across blocks, base order is varied; if budget permits, the design expands
toward all 24 seat permutations. Distinct rosters and model versions are
analyzed as distinct treatments rather than pooled as exchangeable players.
The game or randomized seed-seat block is the independent replication unit.
Turns, decisions, attempts, calls, and the four player rows within one game
are dependent observations.

The eight released games are a selected pilot corpus with unequal seats,
rosters, model versions, and caps. We use them for pipeline validation and
named descriptive case studies. They are not used to estimate a population
leaderboard or provider-level causal effects.

\subsection{Endpoints, Censoring, and Estimation}

In bankruptcy-terminated games, the final solvent player is the survival
winner and bankruptcy events define finish order. In capped games, players
still active at the cap are right-censored for bankruptcy; bankruptcy to a
player, bankruptcy to the bank, and non-bankrupt termination remain distinct
mechanisms. We report raw turn and normalized game time \(u=t/T_g\).

For repeated full-game studies, finish order is analyzed with a
game-conditional Plackett--Luce model or pairwise survival with a
Bradley--Terry-style model. Continuous player-game outcomes are analyzed with
paired seed-block contrasts or mixed-effects models including seat and
predeclared treatment factors. Uncertainty is clustered or bootstrapped at
the game/seed-block level, never at the turn or decision level. We report
effect sizes and intervals, use Holm adjustment for the small confirmatory
endpoint family, and apply Benjamini--Hochberg adjustment within separately
named exploratory families. Sample size is chosen by simulation of the exact
seat-seed schedule to meet a preregistered interval-width or power target.
```

### Metric definitions and denominators

```latex
\subsection{Metric Definitions}
\label{sec:metrics}

Let \(g\) index games, \(i\) players, \(t\) end-of-turn checkpoints, \(d\)
decisions, \(a\) attempts, and \(e\) negotiation or auction episodes.
Longitudinal quantities use end-of-turn checkpoints so that phases emitting
more internal events do not receive extra weight.

\paragraph{Outcome and trajectory.}
For bankruptcy games, \(Y_{ig}^{\mathrm{win}}=1\) only for the last solvent
player. Finish order is obtained from ordered bankruptcy events, with active
players tied or censored at a capped endpoint. We define a versioned
descriptive balance-sheet measure
\begin{equation}
W_{igt} =
C_{igt}
 P^{\mathrm{unmort}}_{igt}
 P^{\mathrm{mort\mbox{-}adj}}_{igt}
 B^{\mathrm{liq}}_{igt},
\label{eq:wealth}
\end{equation}
where \(C\) is cash, the two \(P\) terms are declared unmortgaged and
mortgage-adjusted property values, and \(B^{\mathrm{liq}}\) is declared
building liquidation value. The exact valuation convention is versioned and
components are reported separately; \(W\) is not asserted to be a universal
strategic-value oracle. Durable economic position is summarized by
\begin{equation}
\operatorname{nAUC}_{ig}
=
\frac{1}{T_g}
\sum_{t=1}^{T_g}
\frac{W_{ig,t-1}+W_{igt}}{2}.
\label{eq:nauc}
\end{equation}
We additionally report productive capital---developed monopolies,
houses/hotels, realized rent received and paid, net rent, and turns with
monopoly control---so inert holdings are not conflated with rent production.

\paragraph{Reliability.}
Decisions, rather than attempts, are the primary denominator:
\begin{align}
\operatorname{FirstAttemptValidity}_{ig}
&=
\frac{\#\{d:\text{attempt }0\text{ is parse-, schema-, and legal-valid}\}}
{\#\{d:\text{model action required}\}}, \\
\operatorname{RetryRecovery}_{ig}
&=
\frac{\#\{d:\text{attempt }0\text{ invalid and a retry is valid}\}}
{\#\{d:\text{attempt }0\text{ invalid}\}}, \\
\operatorname{FallbackRate}_{ig}
&=
\frac{\#\{d:\text{applied action is a deterministic fallback}\}}
{\#\{d:\text{model action required}\}}.
\end{align}
We separately report invalid attempts divided by all attempts and retain
parse, schema, illegal-action, policy-validation, provider-error, timeout,
empty-response, and missing-usage categories. A retry is an additional
attempt, not an additional decision.

\paragraph{Cost and latency.}
Let \(K_{iga}\) be recorded provider/OpenRouter cost for attempt \(a\).
We report total cost, cost per attempt, cost per decision,
\(\sum_a K_{iga}/N^{\mathrm{first\mbox{-}valid}}_{ig}\), and cost per
player-game, together with median, p95, p99, and maximum latency. Cost per
first-pass-valid decision is labeled explicitly; deterministic fallback
decisions are not silently counted as valid model selections. Missing usage
is retained as missing rather than estimated. Input, output, reasoning,
cached, and provider-reported total tokens remain separate, and reasoning
tokens are not added to output tokens unless the recorded provider semantics
state that they are additional.

\paragraph{Negotiation and auctions.}
A negotiation episode begins with an initial proposal and ends in acceptance,
rejection without counter, expiration, withdrawal, invalidation, or the run
endpoint. Counteroffers remain in the same episode and do not inflate the
initial-proposal denominator. For player \(i\),
\begin{equation}
\operatorname{InitiatedAcceptance}_{ig}
=
\frac{\#\{\text{accepted terminal episodes initiated by }i\}}
{\#\{\text{terminal episodes initiated by }i\}}.
\end{equation}
Unresolved episodes are reported separately and post-episode windows are
right-censored at bankruptcy or game end. We report episode depth, speaker
alternations, resolution latency, transferred cash/assets, monopoly or blocker
effects, liquidity change, and downstream development or realized rent over a
declared horizon. ``Value creating,'' surplus, and third-party welfare terms
are reserved for a declared branch/value oracle.

For auctions, the eligibility denominator is the number of auctions in which
the player could legally bid. We report participation, bids, dropout price,
winner, winning price, deed-price reference, pre-bid cash or declared legal
liquidity, color-group completion/blocking status, and downstream development.
A price/deed ratio is descriptive aggression, not proof of overpayment.

\paragraph{Liquidity and avoidability.}
When a versioned legal-liquidation optimizer is available, immediate legal
liquidity and solvency margin are
\begin{align}
L_i(s) &=
C_i(s)+\max_{\ell\in\mathcal{L}_i(s)}
\operatorname{CashRaised}(\ell),\\
SM^{\mathrm{now}}_i(s) &= L_i(s)-\operatorname{DueNow}_i(s),
\end{align}
where \(\mathcal{L}_i(s)\) contains only engine-valid unilateral liquidation
plans. ``Immediate-menu avoidable'' means that an action in the frozen
observed decision menu satisfies the current debt. A short-horizon
avoidability claim additionally names horizon \(H\), continuation policy, and
randomness coupling. Reviewer narrative without a validated counterfactual is
not presented as causal avoidability.
```

### Claim gating

```latex
\subsection{Claim Gating}
\label{sec:claim_gating}

\begin{table*}[t]
\caption{Claim gates. Passing state replay does not imply strict artifact
replay, and a complete case study does not imply a population comparison.}
\label{tab:claim_gating}
\centering
\small
\begin{tabularx}{\textwidth}{p{0.17\textwidth}p{0.25\textwidth}Xp{0.18\textwidth}}
\toprule
\textbf{Gate} & \textbf{Required evidence} & \textbf{Permitted claim} &
\textbf{Excluded claim} \\
\midrule
State validity & Frozen configuration and actions; passed state replay or an
explicitly scoped unaffected artifact defect & State trajectory, legal action,
economic transition, and named mechanism facts & Unqualified claims if state
replay fails \\
Strict provenance & Passed full artifact replay; reconciled attempts,
messages, fallback metadata, usage, and hashes & Exact research-log and
provenance fidelity & Calling a state-only pass fully artifact-replay-clean \\
Case study & Complete evidence packet, exact IDs, relevant state/provenance
gate, and reviewed interpretation with alternatives & ``In this named run''
mechanism or communication case & Prevalence, provider trait, or causal
strategy conclusion \\
Population/ranking & Preregistered balanced seed-seat blocks, fixed treatment
contract, failed-run inclusion rules, uncertainty, and multiplicity control &
Roster-, version-, prompt-, route-, and date-bounded comparisons & General
provider superiority or rank from selected games \\
\bottomrule
\end{tabularx}
\end{table*}

High-risk communication claims have an additional semantic gate: exact
message/decision/event evidence, state-grounded truth status, plausible
strategic benefit, benign alternatives, reviewer confidence, and independent
adjudication. Mutually beneficial trade is not collusion, and public/private
difference alone is not deception.
```

### Reproducibility statement

```latex
\subsection{Reproducibility}
\label{sec:reproducibility}

\Bench\ guarantees deterministic replay of engine transitions conditional on
the engine and contract versions, engine seed, settings, player identities,
and recorded applied-action sequence. It does not guarantee deterministic
regeneration of language-model actions. Provider sampling, backend routing,
endpoint updates, network timing, and latency can vary and are recorded as
observational metadata; they must not affect engine progression.

Each released game preserves its decisions, all provider attempts, applied
actions, ordered events, snapshots, prompt/response artifacts, usage and cost,
run configuration, replay reports, and file manifests. Exact source trees and
generated analysis trees are inventoried with byte counts and SHA-256 hashes.
The saved analysis archive is validated for entry-set and byte parity, with
its final ZIP hash stored outside the ZIP to avoid self-reference. These
frozen artifacts remain inspectable even if a future provider endpoint drifts.

The released pilot manifests record nominal OpenRouter reasoning effort
\texttt{medium}; no explicit output-token or reasoning-token budget is sent,
and no explicit \texttt{temperature} request field is recorded. We report
these as request facts rather than inferring provider defaults or equal
reasoning compute across models. Run~191 is reported exactly as
\texttt{state\_passed\_artifact\_failed}: its state trajectory replays, while
strict artifact replay preserves the bounded fallback-provenance mismatch at
sequence 669 described in Section~\ref{sec:artifact_contract}.
```

## Manuscript methodological audit

The table below covers the methodological overclaims and unsupported planned components in the current draft. Line numbers refer to the worktree copy read on 2026-07-28.

| Draft lines | Current wording or implication | Problem | Required disposition |
|---|---|---|---|
| 49–50 | “deterministic multi agent benchmark” and “pair full game traces with targeted micro scenarios”; winning behavior is “associated” with profiles | Determinism is unscoped; no frozen publication micro manifest/results are reported; “associated” sounds inferential | Say deterministic-transition engine; call micro work a planned/existing infrastructure bridge until a frozen result population exists; replace association with audited traces “exhibit” or “illustrate” mechanisms |
| 63, 74, 756 | benchmark itself called deterministic | Provider action generation is stochastic/provider-dependent | Qualify every use as deterministic engine transition/applied-action replay |
| 69, 356–371 | micro scenarios provide attribution and the benchmark “includes” the suite | Controlled attribution requires a frozen fixture manifest, repeated queries, action-order policy, scoring/oracle tier, and uncertainty; counts/results remain absent | Present as protocol/design or future evaluation component, not completed empirical evidence |
| 75 | trajectory framework presented without a primary/secondary hierarchy | Six topical classes do not state which metrics can carry claims | Replace with the four-layer hierarchy and a small preregistered primary family |
| 76, 375–426 | “introduce” micro suite, placeholder counts, proposed rubric and outputs | Planned component is not publication-ready; hidden preferred/acceptable/risky labels require validated value conventions | Move to future-work/protocol subsection unless final manifest and results are frozen |
| 77, 179–195 | artifact set is “implementation dependent” and lists an intended core | The repository now has a stable frozen-package and replay contract; list omits source hashes, split replay, analysis/qualitative manifests, validation, and ZIP parity | Replace with the artifact/replay contract above |
| 89–93, 99 | system framed as enabling “causal trajectories” | Recorded temporal mechanisms are not causal effects; opponent actions and dice are endogenous/confounded | Use “mechanism-resolved trajectories” or “traceable trajectories”; reserve causal language for declared branch estimands |
| 107, 296–313 | system “enables analysis of deception, collusion...” | It enables candidate extraction and reviewed cases, not automatic or population-level measurement | Require D/C rubric, source evidence, alternatives, human adjudication, and bounded candidate language |
| 120 | “standard Monopoly mechanics” | Ruleset/version/house-rule policy is not named; endpoint cap semantics are underspecified | Say “configured ruleset,” record ruleset/engine hashes, and define capped-game censoring |
| 130 | engine “deterministic” and owns randomness/replay | Correct only conditional on version, seed, settings, identities, and applied actions | Add the condition explicitly |
| 145–160 | decision loop goes directly from invalid/valid response to applied action | Omits the established corrective retry and deterministic fallback sequence; blurs decisions and attempts | Use the replacement decision loop |
| 164–177 | private rationales treated as the model’s private reasoning/intent | Logged rationale is model-generated evidence, not verified cognition | Call it a private rationale/intent report and preserve epistemic limitation |
| 181–194 | `decisions.jsonl` described as decisions, retries, fallbacks without unit distinction | The file contains started/resolved decision rows and nested attempts; raw row counts can double decisions | Define decision/attempt/action/event; count unique resolved decision IDs |
| 187 | `state/` called per-turn snapshots without cadence/version language | Snapshot cadence is a declared artifact property and terminal checkpoints can differ from playable turns | Say authoritative checkpoints at declared cadence and report playable versus terminal-only indices |
| 197–213 | six equal metric classes | Mixes claim-bearing endpoints, mechanisms, diagnostics, and reviewed labels | Replace with four-layer hierarchy; keep future oracle metrics separately gated |
| 215–234 | terminal net worth and “opponents bankrupted” listed as self-explanatory | Net-worth valuation is convention-dependent; “bankrupted” needs direct-creditor attribution | Version the balance-sheet convention and distinguish direct creditor, bank bankruptcy, and survival order |
| 236–255 | downstream consequences used to imply action quality | Realized continuation is dice- and opponent-confounded | Label as descriptive realized consequences; use branch/oracle only for counterfactual value |
| 257–276 | trade/auction effects described without episode and denominator rules | Raw messages/events can inflate counts; face value does not establish surplus or overpayment | Define canonical episodes, explicit denominators, and oracle boundary |
| 278–292 | “whether liquidation preserved a path to survival” included as an ordinary metric | Counterfactual survival requires an exact menu or branch/liquidation optimizer | Split immediate-menu, short-horizon branch, and narrative review; do not report one generic avoidability metric |
| 315–333 | “calls and attempts” and token totals presented without provider semantics | Calls/attempts/decisions are conflated; reasoning tokens may be included in output totals; terminal cost is survival-dependent | Use attempt rows, raw token semantics, common-horizon/player-game normalizations, and explicit missingness |
| 335–351 | taxonomy includes deception, collusion, exploitative bargaining as peer metrics | These are human-review families, not deterministic numerical outputs | Move to exploratory behavioral layer and state review coverage/adjudication |
| 431 | empirical section reports “two analysis bundles” | The evidence base now contains eight completed standardized/exhaustively reviewed games | Describe the eight-game audited corpus; retain selected canonical cases by name |
| 435, 438 | Run 191 has 583 “model calls,” “apparent winner,” and replay “pending” | Factually wrong and methodologically misleading | Report 583 decisions/actions, 604 attempts, 21 retries, 23 invalid attempts, two fallbacks, winner as last survivor, state pass, strict artifact fail at sequence 669 |
| 454–466 | Run 191 usage table labels counts “Calls” | The per-player numbers are decision counts in the draft’s source table, not necessarily attempt counts | Relabel only after resolving each column to `model_usage.csv`/attempt rows; use “decisions” or “attempts” exactly |
| 469–489 | Run 191 strategy described as controlled risk and rent “decisive” | “Controlled” imputes quality/intent; “decisive” can imply causality | Use evidence-linked case-study language: observed leverage, realized rent flows, and subsequent bankruptcy sequence |
| 496–519 | Run 273 called “the cleanest current full game artifact” | Seven games are strict-artifact clean; Run 273 is the longest canonical fully replay-clean case used here, not the only clean game | Rephrase accordingly |
| 537–555 | victory “associated” with rent engine; net-rent advantage “dominant” | Acceptable only as a named-run descriptive mechanism, not general association/causal effect | Anchor to Run 273 and say the trace exhibits development followed by realized rent transfers |
| 561–575 | cross-run pattern says winners were agents that converted control into rent pressure | Selected two-run generalization; ignores counterexamples and design imbalance | Present as a hypothesis motivated by audited cases; do not infer prevalence |
| 601–617 | full-game protocol says fixed temperature and fixed seeds | Completed manifests do not record explicit temperature; seed type is ambiguous; neither makes provider outputs deterministic | Record sent/omitted fields; distinguish engine seed from provider sampling; randomize temporal execution |
| 610, 617 | seat permutation mentioned without replication unit | Four player rows in one game are dependent | Define cyclic seat rotations within seed blocks and infer at the game/seed-block level |
| 611 | “replay verification” is one item | State and strict artifact replay have different claim implications | Require and report both statuses |
| 619–631 | publication micro protocol omits repeated queries, action-order randomization, oracle tier, and source-state hashes | Insufficient for attribution or robustness | Add fixture provenance, repetitions, identity/memory variants, action-order seeds, oracle tier, and paired uncertainty |
| 633–653 | claim-gating table has generic “replay agreement” and permits a “nearly complete” case study | Flattens state/artifact replay and lacks state/provenance/case/population separation | Replace with four gates above; missingness must be claim-specific |
| 647 | “model strategic profile” from repeated behavior in trajectories | A named-run player profile is not a stable model trait | Use “run-local strategic pattern” unless replicated across balanced blocks |
| 649 | leaderboard requires repeated seeds/seats and confidence intervals only | Also needs fixed prompt/rules/route/version treatment, incomplete-run rules, provider/date controls, and clustered inference | Use full protocol above |
| 650 | deception/collusion evidence requirement allows transcript evidence or human review | High-risk claims require state-grounded truth, alternatives, and adjudication; private rationale alone is insufficient | Add semantic gate |
| 658–669 | existing plots called “paper ready”; trade/auction/micro figures listed | Automation guide calls current plots analysis-grade; trade surplus/value and micro concordance require unimplemented oracle/query work | Mark each figure available, derived-but-needs-polish, human-gated, oracle-gated, or future-query-gated |
| 676–680 | pilots “show” distinct model strategic profiles | Stronger than selected case-study evidence | Say the named traces illustrate different observed pathways |
| 682–693 | combined evaluation described as intended but reads partly as current results | Micro attribution and transcript rates are not yet a frozen result population | Keep as design statement and label future components |
| 695–711 | economic agency linked to real businesses, portfolios, supply chains, real estate | External validity is unvalidated | Frame as a stylized construct and a hypothesis for external validation, not demonstrated transfer |
| 730–733 | any replay mismatch makes a run suitable only for qualitative work | Too coarse: a strict provenance-only mismatch can leave state-grounded quantitative facts intact | Use split gates; disclose the exact affected claim surface |
| 742–744 | version drift logging omits explicit sent/omitted parameter semantics | Provider defaults can change and reasoning controls are non-equivalent | Record request payload, omitted fields, route, resolved provider, date, and raw usage semantics |
| 753–760 | conclusion again calls benchmark deterministic and says models exhibit profiles from initial traces | Repeats determinism and cross-run generalization issues | Scope determinism; describe audited case-study pathways |
| 814–845 | author notes, TODOs, candidate slots, and candidate framing remain inside the paper | Not a methodological result and not submission-ready | Remove from submission manuscript; preserve in research handoff only |

## Traceability map for paper tables and diagrams

### Recommended Fig. 1: authority, decision, and evidence flow

Use one left-to-right or top-to-bottom vector diagram:

```text
engine state + seeded RNG
  -> decision_id + legal action menu
  -> arena prompt + OpenRouter attempt_index
  -> validation -> retry -> deterministic fallback
  -> one applied action
  -> engine events [seq_start, seq_end] + snapshot
  -> frozen artifacts + hashes
  -> state replay | strict artifact replay
  -> deterministic metrics | human review | future branch oracle
```

Every arrow should name its join:

| Arrow | Traceable fields |
|---|---|
| Engine to decision | `run_id`, `decision_id`, `turn_index`, `decision_type`, `player_id`, `prompt_payload.action_state.available_actions` |
| Decision to attempt | `decision_id`, `attempt_index`, model slug/resolved model/provider, request/response hashes, validation outcome |
| Attempt to action | `final_action`, `retry_used`, `fallback_used`, `fallback_reason`, `applied` |
| Action to events | `decision_id`, `emitted_event_ids`, `emitted_event_seq_start`, `emitted_event_seq_end` |
| Events to state | `seq`, `turn_index`, event type/payload, snapshot checkpoint/state hash where available |
| Frozen evidence to replay | engine version/config, seed, player identities, ordered `actions.jsonl`, canonical event hashes |
| Evidence to analysis | generated table row plus `run_id`, decision/event/message IDs, metric version, source hashes |

### Recommended Fig. 2: split replay oracle

Show a single recorded action stream branching into:

- **State replay:** exclude `LLM_DECISION_REQUESTED`, `LLM_DECISION_RESPONSE`, `LLM_PUBLIC_MESSAGE`, and `LLM_PRIVATE_THOUGHT`; normalize `event_id`, `seq`, and `ts_ms` to state-event order; compare state-relevant canonical hashes.
- **Strict artifact replay:** canonicalize the full event stream; compare all event/provenance hashes.

Include Run 273 as `passed/passed` and Run 191 as `passed/failed at seq=669`. The diagram should visually place the Run 191 difference in the provenance branch, not the state branch.

### Recommended Table 1: run manifest and integrity

Minimum columns:

`run_id`, saved-game path, source commit, engine seed, cap, endpoint, exact model IDs, seat order, reasoning request, `temperature_sent`, output-budget fields sent/omitted, decisions, attempts, retries, invalid attempts, fallbacks, state replay, artifact replay, first mismatch, missing usage attempts, source-tree hash.

Primary sources:

- `run/run_config.json`
- `run/experiment_manifest.json`
- `run/seat_assignment.json`
- `run/usage_attempts.jsonl`
- `analysis/quality/replay_verification.json`
- `analysis/manifests/source_artifact_hashes.json`
- `analysis/reports/integrity_report.md`

### Recommended Table 2: estimands and denominators

Minimum columns:

`metric`, `estimand`, `unit`, `numerator`, `denominator`, `eligibility`, `censoring`, `availability`, `source table`, `claim layer`.

Rows should include survival winner/order, nAUC, first-attempt validity, retry recovery, fallback rate, cost/decision, cost/first-pass-valid decision, initiated-trade acceptance, auction participation, realized net rent, and immediate-menu avoidability.

### Recommended Table 3: claim gates

Use the four-gate LaTeX table above. Add an optional final column with the current corpus result:

- State validity: `8/8 pass`
- Strict provenance: `7/8 pass`
- Case-study review: `8 completed packages`
- Population/ranking: `not satisfied by selected corpus`

### Recommended Table 4: artifact-to-claim provenance

| Claim surface | Required raw objects | Derived evidence | Gate |
|---|---|---|---|
| State/economic mechanism | events, actions, decisions, snapshots | state/event tables, episode table, state replay | State validity |
| Structured reliability | decisions and nested attempts, usage attempts | decision and attempt reconciliation | State + diagnostic completeness |
| Exact prompt/provenance | prompts/responses, decision attempts, observation events | strict artifact replay, prompt hashes | Strict provenance |
| Communication case | public/private artifacts plus state/action outcome | evidence index, reviewer label, alternatives/adjudication | Case study + semantic gate |
| Model comparison | all above across balanced blocks | preregistered estimators and intervals | Population/ranking |

## Current corpus wording that is safe to publish

> We release eight completed, artifact-audited bankruptcy games as descriptive case studies rather than a model leaderboard. Across 1,391 playable turns, the corpus contains 3,696 engine-produced decisions, 3,790 model attempts, 94 corrective retries, 100 invalid attempts, six deterministic fallbacks, 20.47 million recorded tokens, and \$113.84 in recorded inference cost. All eight games pass deterministic state replay, and seven pass strict artifact replay. The selected games use unbalanced seats, rosters, endpoint versions, and model versions; we therefore use them to validate the measurement and evidence pipeline and to motivate a preregistered repeated-game design.

## Run 191 wording that must be preserved

> Run 191 (`mock-83265-81ed4937`) ended by bankruptcy after 191 playable turns with OpenAI GPT 5.5 as the last surviving player. It contains 583 decisions and applied actions, 604 model attempts, 21 corrective retries, 23 invalid attempts, and two deterministic fallbacks. State replay passes across 1,640 state-relevant events. Strict artifact replay compares 3,972 events and first differs at sequence 669 (`mock-83265-81ed4937-evt-000669`, decision `mock-83265-81ed4937-dec-000096`): the original `LLM_DECISION_RESPONSE` preserves the fallback provenance `valid=false` and `error="fallback:illogical_after_retry"` for the applied `reject_trade` action, whereas replay reconstructs the same applied action as `valid=true` with no error. There are no missing or extra actions and no decision-ID mismatch. We therefore treat the run as state-valid but not strict-artifact-clean.

## Components that remain planned or gated

These should not be written in the present tense as completed paper results:

- a frozen publication micro-scenario manifest and balanced result set;
- repeated micro queries with randomized action order and identity/context variants;
- micro/full choice and value concordance;
- branch counterfactuals under declared continuation and RNG coupling;
- a validated strategic value or regret oracle;
- trade bilateral surplus and third-party welfare estimates;
- auction willingness-to-pay, winner’s-curse, synergy, and blocker values;
- short-horizon avoidable-bankruptcy rates;
- calibrated LLM-judge panels and judge-human validation;
- population rates of deception, collusion, promises, or negotiation styles;
- balanced full-game seed-seat blocks;
- uncertainty-aware model rankings;
- provider-level or model-family causal comparisons;
- causal claims about reasoning effort, cost, or strategy;
- a single aggregate MonopolyBench score;
- paper-ready versions of every analysis plot.

The repository contains infrastructure or schemas for several of these items, but infrastructure is not evidence. Each component becomes claim-bearing only after its manifest, population, denominator, validation, and uncertainty procedure are frozen.

## Final integration checklist

1. Replace the current environment, decision-loop, artifact, evaluation, protocol, claim-gating, and reproducibility prose with the scoped LaTeX above.
2. Correct all Run 191 counts and replay language exactly.
3. Reframe the empirical corpus as eight audited descriptive games and selected named cases.
4. Remove “associated,” “decisive,” “causal trajectory,” and stable “model profile” language unless the sentence is explicitly a hypothesis or a named-run observation.
5. Mark micro, oracle, branch, judge-rate, and balanced-ranking components as planned until frozen results exist.
6. Resolve every manuscript number to a table cell and every qualitative statement to an evidence-index row plus raw IDs.
7. Include both replay statuses in every run table.
8. Report explicit request fields and omissions; do not invent a temperature value or provider default.
9. Preserve failed/incomplete calls and runs in reliability/cost populations.
10. Remove TODOs and author-facing draft appendices from the submission version.

