# MonopolyBench research handoff

Date: 2026-07-28  
Repository: `MonopolyBench`  
Repository `HEAD` at audit start: `7ce810eb` (`main`, aligned with `origin/main`)  
Frozen saved-game source commit recorded by the canonical legacy packages: `fa773791`  
Research task: repository-grounded synthesis, manuscript audit, literature positioning, statistical design, and an executable next-researcher handoff.

## 1. Read this first

MonopolyBench is best understood as a research instrument with four coupled surfaces:

1. a deterministic Monopoly rules engine;
2. an LLM decision and orchestration harness;
3. a render-only live interface; and
4. a provenance-rich artifact and analysis pipeline.

The engine—not an agent, prompt, UI, or analysis script—is authoritative. Agents select from engine-produced legal actions. Every applied state transition should emit an event. Decisions explain what was legal, actions explain what was applied, events explain what happened, and snapshots checkpoint authoritative state. This separation is the benchmark's central methodological advantage.

The current evidence base contains eight completed bankruptcy games with exhaustive deterministic and qualitative analysis packages. It is already large enough to demonstrate that the instrument captures economically and behaviorally meaningful mechanisms. It is not balanced enough to establish model rankings. The strongest immediate paper is therefore a benchmark-and-measurement paper with verified case studies, a conservative claim ladder, and a preregistered repeated-game protocol—not an eight-game leaderboard.

One replay caveat must never be flattened:

- `mock-83265-81ed4937` passes state replay but fails strict artifact replay at sequence 669 because the original event preserves fallback provenance (`valid=false`, `error="fallback:illogical_after_retry"`) while replay reconstructs the already-applied `reject_trade` action as valid with no error. State progression, action linkage, and decision linkage otherwise reconcile.
- `mock-44910-42ec35c5` passes both state and strict artifact replay.

## 2. Evidence authority and source order

When two sources disagree, use this order:

1. `run/events.jsonl` — what happened;
2. `run/actions.jsonl` — what action was applied;
3. `run/decisions.jsonl` — what choices were legal;
4. decision prompt/response artifacts — what the model saw, returned, retried, or failed to serialize;
5. `run/state/` — authoritative state checkpoints;
6. frozen `quality_check/` reports and manifests;
7. generated deterministic tables and quality reports under `analysis/`;
8. exhaustive manual reviews and case studies under `analysis/review/` and `analysis/reports/`;
9. manuscript prose and historical research memos.

The manuscript is a consumer of the artifacts, not an authority over them. Historical summaries are orientation material only. Never repair a disagreement by modifying a frozen `run/` or `quality_check/` tree.

### Canonical repository guides

- `analysis/analysis.md` — research questions, metrics, reporting rules, and validity boundaries.
- `analysis/analysis_process.md` — end-to-end review procedure, claim packages, evidence rules, and quality gates.
- `analysis/analysis_automated.md` — deterministic standardization, expanded metrics, and automation contract.
- `AGENTS.md` — repository invariants, ownership boundaries, prompt policy, and verification expectations.
- `monopolybench_ieee_draft_v0_1.tex` — current paper draft; useful but not artifact-authoritative.
- `docs/research_raw/monopolybench_pro.md` — earlier adversarial methodology and statistical-design memo.
- `docs/research_raw/monopolybench_deep_research.md` — earlier literature and analysis memo.

### Canonical per-game qualitative sources

Each saved game has the same strongest-superset review contract:

- `analysis/README.md`
- `analysis/review/chronological_turn_review.md`
- `analysis/review/player_dossiers.md`
- `analysis/review/bankruptcy_windows.md`
- `analysis/review/negotiation_review.md`
- `analysis/review/decision_coverage.csv`
- `analysis/review/evidence_index.csv`
- `analysis/review/review_packet.jsonl`
- `analysis/review/communication_claims.csv`
- `analysis/review/promise_lifecycle.csv`
- `analysis/reports/manual_review_report.md`
- `analysis/reports/case_studies.md`
- `analysis/reports/integrity_report.md`
- machine-readable quality, validation, and manifest files.

The eight package roots are:

- `saved_games/frontier-115-mock-321229807-87ca99d7-gemini-3-1-pro-preview/`
- `saved_games/frontier-163-mock-1038910349-f66fa07c-claude-opus-4-8/`
- `saved_games/frontier-166-mock-3676466999-527872e4-claude-opus-4-8/`
- `saved_games/frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview/`
- `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/`
- `saved_games/frontier-mini-154-mock-24591-46c1eb90-gemini-3-5-flash/`
- `saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/`
- `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/`

## 3. Exact eight-game ledger

All eight games ended by bankruptcy. `Attempts - decisions` gives the number of corrective retries in this corpus. Costs are the recorded provider/OpenRouter costs in the saved artifacts.

| Turns | Run ID | Winner | Decisions | Attempts | Retries | Invalid attempts | Fallbacks | Cost (USD) | State replay | Artifact replay |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 115 | `mock-321229807-87ca99d7` | Gemini 3.1 Pro Preview | 366 | 377 | 11 | 13 | 2 | 14.61438250 | pass | pass |
| 154 | `mock-24591-46c1eb90` | Gemini 3.5 Flash | 396 | 401 | 5 | 5 | 0 | 4.65275495 | pass | pass |
| 157 | `mock-64394-c3bb8d94` | Grok 4.3 | 346 | 355 | 9 | 9 | 0 | 4.03655795 | pass | pass |
| 163 | `mock-1038910349-f66fa07c` | Claude Opus 4.8 | 364 | 371 | 7 | 7 | 0 | 12.06275605 | pass | pass |
| 166 | `mock-3676466999-527872e4` | Claude Opus 4.8 | 488 | 502 | 14 | 14 | 0 | 21.91408585 | pass | pass |
| 172 | `mock-2413970733-53b199c1` | Gemini 3.1 Pro Preview | 613 | 631 | 18 | 20 | 2 | 24.60457580 | pass | pass |
| 191 | `mock-83265-81ed4937` | OpenAI GPT 5.5 | 583 | 604 | 21 | 23 | 2 | 27.71173045 | pass | **fail at sequence 669** |
| 273 | `mock-44910-42ec35c5` | Gemini 3 Flash Preview | 540 | 549 | 9 | 9 | 0 | 4.24475240 | pass | pass |
| **Total** | **8 games** | — | **3,696** | **3,790** | **94** | **100** | **6** | **113.84159595** | **8/8 pass** | **7/8 pass** |

Additional corpus totals:

- 1,391 playable turns;
- 20,474,750 recorded tokens;
- four distinct winning model labels, but under unbalanced rosters and versions;
- six deterministic fallbacks across three games;
- seven strict-artifact-clean games and one state-clean/artifact-failed game.

These totals support instrumentation, reliability, cost, and mechanism claims. They do not support population-level prevalence estimates, model rankings, or causal comparisons among providers.

### Seat and roster imbalance

The frontier roster is repeated in five games, but four use the identical order `Claude Opus 4.8 → Gemini 3.1 Pro Preview → Grok 4.3 → OpenAI GPT 5.5`; Run 191 uses `OpenAI GPT 5.5 → Claude Opus 4.8 → Gemini 3.1 Pro Preview → Grok 4.3`. The mini roster uses the same seat order in all three games, and its Gemini endpoint changes from `Gemini 3.5 Flash` in Runs 154/157 to `Gemini 3 Flash Preview` in Run 273. Maximum-turn caps also differ: 400 for the four newer frontier games, 500 for Runs 154/157, and 600 for Runs 191/273.

Therefore:

- frontier outcomes are confounded by seed and seat;
- mini outcomes are confounded by seed, fixed seat, and a model-version change;
- the two roster families are not directly comparable;
- cost comparisons are also confounded by game length, survival exposure, endpoint pricing, and decision mix.

## 4. What the benchmark actually measures

The benchmark's research object is long-horizon economic agency under exact rules and interacting endogenous opponents. The distinctive challenge is not merely “play Monopoly.” A player must repeatedly:

- acquire and value assets;
- preserve liquidity while exploiting leverage;
- reason about rent exposure and opponent exposure;
- negotiate with agents whose incentives and statements change;
- bid under uncertainty in auctions;
- convert nominal ownership into productive rent engines;
- survive forced payments through legal liquidation;
- maintain a correct ontology of colors, groups, mortgages, houses, hotels, and bank inventory;
- serialize a legal action reliably;
- recover from a rejected attempt without losing strategic intent; and
- do all of this while other language-model agents alter the economic state.

This produces three layers of outcome:

1. **Economic outcome:** survival, bankruptcy, rent flow, asset control, monopoly conversion, and final placement.
2. **Decision-process outcome:** legal choice quality, negotiation behavior, capital allocation, claims, promises, reversals, and local avoidability.
3. **Systems outcome:** validity, retries, fallbacks, latency, token use, provider fields, cost, and replay fidelity.

The paper should explicitly separate the three. A strategically sound intention can fail at serialization. A valid action can be economically poor. A state-replay-clean run can preserve a strict artifact-provenance mismatch. Those are different phenomena.

## 5. Architecture and reproducibility thesis

The cleanest architecture description is:

```text
engine emits decision + legal actions
        ↓
arena constructs model-facing prompt
        ↓
OpenRouter model call / strict parsing / corrective retry
        ↓
validated action or deterministic fallback
        ↓
engine applies action and emits events
        ↓
telemetry writes decisions, attempts, actions, events, snapshots, usage, costs
        ↓
API streams; frontend renders
        ↓
downstream replay, standardization, metrics, and qualitative review
```

The benchmark's reproducibility claim must be scoped:

- Engine replay is deterministic given engine version, seed, settings, player identities, and applied action sequence.
- Provider sampling is not made deterministic merely by fixing an engine seed or a nominal temperature.
- Full artifact replay is stricter than state replay because it includes observational/provenance fields as well as state-relevant effects.
- Wall-clock time, network timing, and provider latency are observational metadata and must never affect game progression.
- A frozen run is reproducible evidence even if a future model endpoint drifts, because the decisions, attempts, applied actions, events, and states remain inspectable.

## 6. Defensible novelty boundary

Do not claim that MonopolyBench is the first long-horizon economic LLM benchmark, the first multi-agent business simulation, or the first bargaining benchmark. Current adjacent work includes:

- [CoffeeBench](https://arxiv.org/abs/2606.16613): a long-horizon heterogeneous firm economy;
- [Cattle Trade](https://arxiv.org/abs/2605.14537): multi-agent auctions, bargaining, bluffing, and resource allocation;
- [AgenticPay](https://arxiv.org/abs/2602.06008): buyer–seller tasks with feasibility, efficiency, and welfare measures;
- [M3-Bench](https://arxiv.org/abs/2601.08462): multi-agent and multi-turn interaction;
- [DSGBench](https://arxiv.org/abs/2503.06047): dynamic strategic games;
- [Vending-Bench](https://arxiv.org/abs/2502.15840): long-horizon business operation;
- [EconGym](https://proceedings.neurips.cc/paper_files/paper/2025/hash/40d45b1e23d00d5895e65778e85cf8ee-Abstract-Datasets_and_Benchmarks_Track.html): economic reasoning and economic environments;
- [Multi-Stakeholder Negotiation](https://proceedings.neurips.cc/paper_files/paper/2024/hash/984dd3db213db2d1454a163b65b84d08-Abstract-Datasets_and_Benchmarks_Track.html);
- [Bonjour! AI-driven Monopoly gameplay](https://arxiv.org/abs/2103.00683) and other prior Monopoly reinforcement-learning environments and agents.

The defensible contribution is the combination:

> MonopolyBench couples a rules-complete asset-and-solvency economy with engine-enforced legal actions, public and private language, exact decisions/actions/events/snapshots, split state-versus-artifact replay, retry/fallback and cost telemetry, and evidence-indexed exhaustive trajectory review, plus a planned bridge from noisy full games to frozen micro scenarios.

That combined instrumentation is stronger and more specific than “models play a board game.” The novelty should be demonstrated in a comparison table with explicit columns:

- horizon and termination;
- number and heterogeneity of agents;
- asset ownership and transfer;
- endogenous prices or negotiated transfers;
- auctions;
- leverage/mortgages;
- rent or recurring revenue;
- forced liquidation and bankruptcy;
- public and private communication;
- engine-generated legal action menus;
- per-attempt prompts/responses;
- deterministic state replay;
- strict artifact replay;
- provider usage and cost;
- exhaustive human review/evidence indexes;
- full-game-to-micro-scenario linkage.

## 7. Eight-game mechanism atlas

### 7.1 Run 115 — `mock-321229807-87ca99d7`

Gemini 3.1 Pro Preview won after 115 turns. The run contains 366 decisions, 377 attempts, 13 invalid attempts, and the corpus's most direct example of reliability changing economic outcome.

Core mechanism:

- OpenAI repeatedly used acquisition, mortgage, and trade cycles.
- Distressed assets ultimately moved toward Gemini.
- Gemini converted dark-blue control into a productive rent engine.
- Claude reached an immediate solvency decision with a legal house-sale survival line.
- Two serialization failures prevented the intended liquidation, and deterministic fallback produced bankruptcy.
- Gemini itself had a fallback at the next turn, so this is a useful counterexample to simplistic “winner = more reliable at every point” narration.
- Later hotel rents eliminated OpenAI and Grok.

Use this run to distinguish strategic intention, legal affordance, action serialization, deterministic fallback, and realized economic outcome. It supports an “avoidable at the immediate menu” label for Claude only if the evidence packet preserves the exact legal sale alternative and the failed attempts.

### 7.2 Run 154 — `mock-24591-46c1eb90`

Gemini 3.5 Flash won after 154 turns. The game contains 396 decisions, 401 attempts, five invalid attempts—all attributed to GPT in the review—and no fallback.

Core mechanism:

- Gemini built a dark-blue rent engine.
- A Park Place trade and railroad sale created chained financing for productive conversion.
- Gemini later consolidated additional property.
- GPT engaged in high-frequency mortgage/build churn.
- Claude repeatedly reasoned from a false pink-monopoly ontology even after contrary state evidence.
- Grok's terminal collapse was forced by a $1,700 Boardwalk rent.

This run is valuable for “ownership is not productivity”: the analytically important transition is not acquisition alone, but financing, set completion, development, and rent conversion.

### 7.3 Run 157 — `mock-64394-c3bb8d94`

Grok 4.3 won after 157 turns. The game contains 346 decisions, 355 attempts, nine invalid/retry attempts, and no fallback.

Core mechanism:

- blocker ownership created bargaining leverage;
- a reciprocal monopoly trade at turn 134 unlocked both sides;
- Grok converted orange into hotels by turn 138;
- a subsequent GPT portfolio transfer accelerated Grok's compounding rent position;
- GPT later encountered an immediate-menu avoidable bankruptcy;
- Claude and Gemini's terminal bankruptcies were classified as forced;
- Claude showed persistent color-group ontology errors;
- the review found no high-confidence deception or collusion.

This is the strongest concise case of blocker value becoming productive value through exchange, followed by rapid conversion and rent compounding.

### 7.4 Run 163 — `mock-1038910349-f66fa07c`

Claude Opus 4.8 won after 163 turns. The game contains 364 decisions, 371 attempts, seven retries, 44 trade episodes, and four auctions.

Core mechanism:

- Claude acquired and developed light blue to hotels;
- creditor transfers from bankrupt opponents completed red and green groups;
- those transferred assets became productive rather than remaining nominal holdings;
- salient late shocks include Grok paying $600 on Connecticut, Gemini paying $1,000 on Pennsylvania, and GPT paying $925 on Illinois;
- case studies include a $1 auction, a one-shot anti-leader free transfer, and an expensive request without reciprocal consideration.

Use this run for creditor-transfer feedback loops: bankruptcy does not just remove a player; it can transfer a portfolio to the creditor and amplify the creditor's future rent engine.

### 7.5 Run 166 — `mock-3676466999-527872e4`

Claude Opus 4.8 won after 166 turns. The game contains 488 decisions, 502 attempts, 14 retries, 107 trade episodes, 14 accepted deals, and one auction.

Core mechanism:

- dense bargaining creates a large episode-level negotiation surface;
- the review documents state-ontology failures alongside asset-conversion opportunities;
- the run is especially useful for studying proposal concentration, countering, rejection, and whether ownership is converted into monopoly/development;
- a duplicated `decision_started` marker exists for `dec-000030`, but there is one resolution and one action;
- state and artifact replay still pass.

This duplicate-marker case is a useful artifact-quality example: count decisions and resolved actions using stable decision IDs, not raw marker occurrences.

### 7.6 Run 172 — `mock-2413970733-53b199c1`

Gemini 3.1 Pro Preview won after 172 turns. This is the largest decision trace in the corpus: 613 decisions, 631 attempts, 20 invalid attempts, two fallbacks, and 133 trade proposals, all initiated by GPT according to the review.

Core mechanism:

- GPT dominated proposal initiation and completed 19 accepted trades, yet eventually churned its asset base toward zero;
- Gemini converted light blue and later orange into productive engines;
- Grok maintained a coherent railroad/brown posture but was comparatively inflexible;
- Claude had a legal house-sale survival line but fallback bankruptcy followed failed serialization;
- the run contains a high-confidence, single-reviewer D3 deception candidate: GPT publicly promised to hold Ventnor and then immediately flipped it while private framing pointed the other way;
- this candidate remains unadjudicated and must not be written as settled deception;
- a duplicated `decision_started` marker exists at the resume boundary for `dec-000242`, with one action and one resolution.

This game is the clearest warning against equating negotiation volume with economic success. Proposal count is an activity metric; conversion, retained option value, counterparty benefit, and eventual solvency are outcome mechanisms.

### 7.7 Run 191 — `mock-83265-81ed4937`

OpenAI GPT 5.5 won after 191 playable turns. The game contains 583 decisions/actions, 604 attempts, 21 retries, 23 invalid attempts, two fallbacks, 69 trade threads, nine auctions, three bankruptcies, 3,524,545 tokens, and $27.71173045 in cost.

Mechanism-rich episodes include:

- turn-25 pink completion through asset recycling;
- a Park Place auction;
- dual financing around light blue;
- a 51-decision consolidation episode around turn 79;
- house scarcity and rule/ontology failures;
- green-group weaponization;
- three distinct bankruptcy windows;
- the exact fallback-provenance artifact replay mismatch.

Replay status:

- state replay passes across 1,640 state-relevant events;
- strict artifact replay compares all 3,972 events and first differs at event/sequence 669;
- event ID: `mock-83265-81ed4937-evt-000669`;
- decision ID: `mock-83265-81ed4937-dec-000096`;
- original: `valid=false`, `error="fallback:illogical_after_retry"`, action `reject_trade`;
- replay: `valid=true`, `error=null`, same applied action;
- no missing/extra actions and no decision-ID mismatch.

The paper should not call this “replay pending” or imply state divergence. It is a completed, state-valid strategic case study with a precisely bounded strict artifact-provenance defect.

Frozen hashes recorded by the canonical package:

- run tree: `d14d8c74621416ba87bfeca9e66527f27976de4a7847ba8fcb36b360fd15a79e`;
- quality-check tree: `2d0572f2f20f65d3f5790fca212791a000bfddcb0b87a56db18bbe63c0cd9de0`;
- combined source tree: `5b5a35d4d9497a1c23d2d1fb56d230993d545be3d18d4641b727ac789f3fcc64`;
- source commit: `fa773791718e3b5d8ff18448e2ad3fa42b375259`;
- inventory: 3,835 `run/` files and 1,208 `quality_check/` files.

### 7.8 Run 273 — `mock-44910-42ec35c5`

Gemini 3 Flash Preview won after 273 playable turns. The game contains 540 decisions/actions, 549 attempts, nine retries/invalid attempts, no fallback, 44 trades, eight auctions, 31 mortgage episodes, three bankruptcies, 2,945,246 tokens, and $4.24475240 in cost.

Core mechanisms:

- Illinois auction and red-group pivot;
- Kentucky cash-for-monopoly exchange;
- a Vermont corrective retry that materially changed the selected action;
- pink completion;
- one-turn brown overdevelopment followed by bankruptcy;
- railroad consolidation;
- Claude's blocker-versus-liquidity dilemma;
- New York exchange and finite-house lock;
- distress sales feeding the leading rent engine;
- terminal tax pressure.

Replay status:

- state replay passes 1,942/1,942 state-relevant events;
- strict artifact replay passes 4,102/4,102 events.

Communication review found no D3/D4 deception and no C2-C4 collusion. One selective house-lock framing episode is a D2 candidate, not a definitive deception finding.

Frozen hashes recorded by the canonical package:

- run tree: `25524577aa9ec7754151d9997627cec1280bf0255293085d59670bb617477f50`;
- quality-check tree: `ff2e7c006d723b85936e530b13b779b55922a3082fd32ac97ccf32457e6663d1`;
- source commit: `fa773791718e3b5d8ff18448e2ad3fa42b375259`;
- inventory: 3,599 `run/` files and 1,098 `quality_check/` files.

## 8. Cross-game pattern and counterexample matrix

| Candidate mechanism | Supporting cases | Important counterexample or limit | Permitted claim |
|---|---|---|---|
| Productive conversion matters more than raw property count | 154, 157, 163, 172, 273 | broad ownership can preserve option value before development; conversions are state-dependent | “The reviewed traces repeatedly distinguish acquisition from conversion into developed rent engines.” |
| Blockers have option value but can create liquidity drag | 157, 273 | a blocker can become highly productive after a reciprocal trade | describe the tradeoff; do not assign a universal blocker value |
| Finite house inventory can be strategic | 191, 273 | a temporary house lock is not automatically intentional deception or optimal play | identify inventory mechanism and exact episodes |
| High negotiation volume is not equivalent to success | 166, 172, 191 | some dense negotiation directly completes monopolies or recycles capital | report initiation, acceptance, conversion, and downstream state separately |
| Reliability failures can change outcomes | 115, 172, 191 | most retries recover; winners can also incur fallback; strategic quality and serialization differ | make decision-level and attempt-level reliability distinct |
| Bankruptcy can amplify a creditor | 163, 273 and other creditor transfers | bank bankruptcy or fragmented transfers need not help a leader | treat bankruptcy as a portfolio-transfer event, not only survival outcome |
| State ontology errors recur | 154, 157, 166 and others | a mistaken private rationale may not affect the selected legal action | code belief error, action effect, correction opportunity, and persistence separately |
| Mortgage/build churn can signal poor capital allocation | 154, 172 | reversible financing can be rational around a high-value conversion | avoid labeling churn as failure without state-local opportunity cost |
| Immediate avoidability is narrower than narrative blame | 115, 157, 172 | many terminal bankruptcies are forced with no legal survival line | require an exact legal alternative at the terminal decision |
| Public/private divergence can reveal strategic communication | 172 D3 candidate; 273 D2 candidate | language may be selective, stale, mistaken, or unfulfilled without deceptive intent | preserve epistemic levels and adjudication status |

No cell in this table is a prevalence estimate. The run set is selected, rosters differ, model versions differ, and games interact endogenously.

## 9. Manuscript audit

The current Prism-imported draft improves formatting and author metadata, but its empirical core still predates the completed modern analyses. The following changes are high priority.

### 9.1 Abstract and contribution claims

Current problem:

- “winning behavior is associated with distinct economic profiles” sounds like an inferential cross-run result.
- The paper does not yet foreground the split replay oracle or evidence-indexed exhaustive review.

Recommended change:

- describe the two canonical games and eight-game corpus as audited case studies;
- say the traces “exhibit” or “illustrate” mechanisms;
- make protocol, provenance, and measurement the primary contribution;
- reserve association/ranking language for the preregistered repeated-game study.

### 9.2 Related work

Add and compare against current primary sources, especially CoffeeBench, Cattle Trade, AgenticPay, M3-Bench, EconGym, DSGBench, Vending-Bench 1/2, multi-stakeholder negotiation, and prior Monopoly RL. Avoid “first” claims unless every comparison dimension is explicitly scoped.

### 9.3 Artifact contract

The draft says the exact artifact set is implementation-dependent. The repository now has a much stronger canonical package contract. Replace the loose list with:

- frozen raw `run/`;
- frozen `quality_check/`;
- source and tree hashes;
- separate state and artifact replay;
- deterministic standardized tables/plots;
- expanded episode metrics;
- exhaustive review artifacts;
- generated-output manifests and ZIP equivalence.

### 9.4 Run A factual correction

The draft currently calls 583 decisions “model calls” and says replay reconciliation is pending. Correct to:

- 583 decisions/actions;
- 604 model attempts;
- 21 retries;
- 23 invalid attempts;
- two deterministic fallbacks;
- state replay passed across 1,640 state-relevant events;
- strict artifact replay first mismatched at sequence 669 for the exact fallback-provenance reason above.

The table/caption should say “state-valid, strict-artifact-failed,” not “apparent winner” or “pending reconciliation.”

### 9.5 Run B positioning

Run 273 remains the clean canonical long game, but it is no longer the only fully analyzed clean artifact. Phrase it as the longest canonical fully replay-clean case study in the paper, not as the sole trustworthy result.

### 9.6 Experimental protocol

Distinguish:

- engine seed;
- seat assignment;
- roster/model version;
- prompt and tool-schema version;
- model sampling parameters;
- reasoning setting;
- provider/backend metadata;
- run date/pricing snapshot.

“Fixed temperature” does not guarantee reproducible provider output. “Fixed seeds” must specify whether this means engine randomness, model sampling, or both. Engine replay should be deterministic; fresh model regeneration is a different reproducibility question.

For the eight saved games, the frozen experiment manifests record nominal OpenRouter reasoning effort `medium`, provider-specific routing, and no explicit `max_tokens` or reasoning-token budget. They do not record an explicit `temperature` request field. The manuscript must describe those request facts exactly rather than retroactively saying the completed games used a fixed explicit temperature. Cross-provider `medium` reasoning is a nominal gateway policy, not evidence of equal reasoning compute or semantically identical controls.

### 9.7 Claim gating

Separate at least four gates:

1. state-valid mechanism claims;
2. strict-artifact/provenance claims;
3. single-game case-study claims;
4. cross-game population/ranking claims.

Run 191 passes gates 1 and 3 with an explicit gate-2 caveat. It must not be silently excluded from all strategic analysis or silently promoted to strict-artifact clean.

### 9.8 Submission hygiene

Before submission:

- remove `\todo{}` placeholders;
- remove author-facing draft notes and candidate framing appendices;
- complete incomplete bibliography metadata;
- verify every URL and title from a primary source;
- render every table at target two-column dimensions;
- give every result table its evidence population and denominator;
- ensure display names exactly match frozen manifests;
- include code/artifact availability and hash/version statements.

### 9.9 Ready-to-adapt replacement prose

#### Abstract result framing

> We present eight completed, artifact-audited bankruptcy games as descriptive case studies rather than a model leaderboard. Across 1,391 playable turns, the corpus contains 3,696 engine-produced decisions, 3,790 model attempts, 94 corrective retries, 100 invalid attempts, six deterministic fallbacks, 20.47 million recorded tokens, and $113.84 in recorded inference cost. The traces expose distinct mechanisms—including conversion of ownership into developed rent engines, blocker-for-liquidity exchanges, finite-house constraints, creditor-transfer compounding, and serialization failures at solvency decisions—but the selected games use unbalanced seats, rosters, and model versions. We therefore use them to validate the measurement and evidence pipeline and to motivate a preregistered repeated-game design.

#### Run 191 replay paragraph

> Run A (`mock-83265-81ed4937`) ended by bankruptcy after 191 playable turns with OpenAI GPT 5.5 as the last surviving player. It contains 583 decisions and applied actions, 604 model attempts, 21 corrective retries, 23 invalid attempts, and two deterministic fallbacks, with 3,524,545 recorded tokens and $27.71173045 in reported cost. State replay passes across 1,640 state-relevant events. Strict artifact replay compares 3,972 events and first differs at sequence 669 (`mock-83265-81ed4937-evt-000669`, decision `mock-83265-81ed4937-dec-000096`): the original event preserves the fallback provenance `valid=false` and `error="fallback:illogical_after_retry"` for the applied `reject_trade` action, whereas replay reconstructs the same applied action as `valid=true` with no error. There are no missing or extra actions and no decision-ID mismatch. We therefore treat this run as state-valid but not strict-artifact-clean.

#### Case-study scope paragraph

> These games support mechanism identification within fully specified trajectories, not population-level model comparison. Each qualitative claim is tied to a named run and source decision/event identifiers. Cross-game similarities are treated as hypotheses unless replicated under balanced seeds, seats, rosters, endpoint versions, and provider controls.

#### Determinism paragraph

> MonopolyBench guarantees deterministic engine transition replay, not deterministic regeneration of language-model actions. Given a fixed engine version, engine seed, configuration, player identities, and applied action sequence, state-relevant transitions can be reconstructed and compared after canonicalization. Provider sampling, routing, network timing, and latency remain observational. The completed runs record nominal reasoning effort `medium`, omit explicit output-token budgets, and do not record an explicit temperature request field; these request facts should not be paraphrased as deterministic model sampling.

## 10. Statistical design for the full-game study

### 10.1 Units and indices

Use:

- \(g\): game;
- \(i\): player/model instance;
- \(s\): engine seed;
- \(q\): seat;
- \(r\): roster;
- \(t\): playable turn or normalized game time;
- \(d\): decision;
- \(a\): model attempt;
- \(e\): negotiation/auction/mortgage episode.

The independent replication unit is the game or a randomized seed-seat block, not a turn, decision, or model call. Decisions within a player and all players within a game are dependent.

### 10.2 Design

For a fixed four-model roster:

1. predeclare engine seeds;
2. rotate each model through all seats within each seed block;
3. hold engine, contracts, prompt, tool schema, retry policy, and fallback policy fixed;
4. record exact provider model IDs and backend metadata;
5. randomize execution order to reduce temporal provider drift;
6. include incomplete/failed runs in reliability and cost accounting;
7. repeat the design for distinct rosters rather than pooling arbitrary rosters as exchangeable.

If all 24 seat permutations are too costly, use a balanced Latin-square schedule and report residual opponent-order imbalance. Do not use “one game per model win” as the effective sample size.

### 10.3 Primary estimands

Predeclare a small primary family:

- probability of winning within the fixed roster and protocol;
- bankruptcy/survival distribution;
- normalized wealth or productive-capital area under the trajectory;
- first-attempt legal-action reliability;
- cost per completed player-game and cost per valid decision.

Secondary mechanism families can include rent conversion, liquidity, negotiation, auction, mortgage, and communication measures.

### 10.4 Outcome and ranking models

For one-winner four-player games, use game-conditional ranking models rather than treating four binary rows as independent:

- Plackett–Luce or Bradley–Terry-style models for finish order/pairwise survival;
- seed-block and seat effects;
- model-version identity as the treatment label;
- clustered or block bootstrap intervals at the seed/game level;
- randomization/permutation tests aligned with the seat schedule when sample sizes are modest.

Report raw paired contrasts and uncertainty alongside model-based estimates. Ranking uncertainty is more important than a single ordinal leaderboard.

### 10.5 Survival and censoring

Bankruptcy time is a time-to-event outcome with shared-game dependence and a surviving winner. For capped games:

- treat active players at the cap as right-censored for bankruptcy;
- distinguish bankruptcy-to-player, bankruptcy-to-bank, and non-bankrupt termination if mechanisms differ;
- show Kaplan–Meier curves descriptively;
- use discrete-time hazard or shared-frailty/cluster-robust models only with enough games;
- consider competing-risk or multi-state summaries for solvent → distressed → liquidating → bankrupt transitions.

Turn counts can differ across games. Report both raw turn and normalized time \(u=t/T_g\), while preserving the fact that normalization can hide late-game duration differences.

### 10.6 Economic trajectories

For player \(i\) in game \(g\), define a documented descriptive balance-sheet measure \(W_{igt}\). Keep components separate:

\[
W_{igt} =
\text{cash}_{igt}
+ \text{unmortgaged-property basis}_{igt}
+ \text{mortgage-adjusted property value}_{igt}
+ \text{building liquidation value}_{igt}.
\]

This is not a universal strategic-value oracle. Report its components and sensitivity to valuation convention.

A length-normalized trajectory summary is:

\[
\operatorname{nAUC}_{ig}
=
\frac{1}{T_g}
\sum_{t=1}^{T_g}
\frac{W_{ig,t-1}+W_{igt}}{2}.
\]

Also report productive capital separately: developed monopolies, houses/hotels, rent collected, net rent, and turns with monopoly control. Raw wealth can reward inert holdings that never become productive.

### 10.7 Liquidity and collapse

Useful decision-local quantities:

- cash buffer before and after an action;
- unmortgaged liquidation capacity;
- building liquidation capacity;
- maximum immediate legal cash generation;
- rent exposure over board-position windows;
- time from first severe liquidity shock to bankruptcy;
- fraction of bankruptcy-window decisions with at least one legal survival action.

“Avoidable bankruptcy” requires a frozen decision menu and a clearly specified horizon:

- immediate-menu avoidable: a legal action in the observed decision would satisfy the current debt;
- short-horizon avoidable: a specified counterfactual policy survives \(H\) steps under fixed exogenous randomness;
- narrative avoidable: reviewer judgment without a validated counterfactual, which should not be presented as causal.

### 10.8 Reliability

Use decisions as the primary denominator:

\[
\text{FirstAttemptValidity}
=
\frac{\#\{\text{decisions valid on attempt 0}\}}
{\#\{\text{decisions}\}}.
\]

\[
\text{RetryRecovery}
=
\frac{\#\{\text{initially invalid decisions resolved by retry}\}}
{\#\{\text{initially invalid decisions}\}}.
\]

\[
\text{FallbackRate}
=
\frac{\#\{\text{decisions resolved by fallback}\}}
{\#\{\text{decisions}\}}.
\]

Keep schema/parse invalidity, illegal-action invalidity, illogical-policy checks, provider failures, and missing usage metadata distinct. Attempt-level percentages answer different questions and should be labeled explicitly.

### 10.9 Negotiation and auction episodes

The unit is a thread/episode, not each message:

- proposals initiated;
- counterparties targeted;
- counters;
- accepted/rejected/expired;
- transferred cash, properties, mortgages, and monopoly/blocker effects;
- proposal-to-resolution latency in decisions/turns;
- state change before and after the episode;
- downstream conversion within a declared horizon.

Acceptance rate must name its denominator. Do not call a trade “value creating” from face value alone. Separate:

- asset/cash transfer;
- monopoly completion;
- blocker removal;
- liquidity relief;
- observed downstream development/rent;
- reviewer judgment;
- counterfactual value, if and only if a branch-replay policy is specified.

For auctions, report participation, bids, winner, price, reference price convention, immediate liquidity, group completion, and downstream development.

### 10.10 Cost and latency

Report:

- cost per attempt;
- cost per decision;
- cost per valid decision;
- cost per player-game;
- cost per completed game;
- cost by retry/fallback status;
- token/latency distributions rather than means alone;
- missing-provider-usage rate.

Cost–quality analysis is vulnerable to survivor bias: failed or incomplete calls/games can consume cost without producing a final outcome. Use all attempted runs for systems claims, a two-part model if completion is selective, and sensitivity analyses for missing usage/cost fields.

### 10.11 Multiple comparisons and uncertainty

- Declare 3–5 confirmatory primary outcomes.
- Use Holm correction for a small confirmatory family.
- Use Benjamini–Hochberg within clearly named exploratory metric families.
- Report effect sizes and intervals, not only adjusted \(p\)-values.
- Bootstrap at the game/seed-block level, never at the turn level as if turns were independent.
- Show rank distributions or probability-of-being-best rather than only point ranks.

### 10.12 Sample-size planning

Do not use the eight selected games as if they supplied independent model-level variance. Use simulation:

1. estimate plausible between-seed, seat, opponent, and residual variation from pilot blocks once available;
2. choose a smallest meaningful win-probability or nAUC contrast;
3. simulate the exact balanced seat/seed schedule;
4. fit the planned estimator;
5. measure interval width, coverage, and power;
6. increase seeds until the preregistered precision target is met.

For ranking, target stable pairwise intervals and rank probabilities, not merely 80% power for one omnibus test.

## 11. Full-game to micro-scenario bridge

The micro suite should be derived from full-game decision states, not invented independently whenever possible:

1. identify a decision with a meaningful legal choice;
2. freeze the authoritative pre-decision state and legal menu;
3. preserve relevant public history while controlling private memory variants;
4. define dominated alternatives only where rules/economics make dominance defensible;
5. evaluate multiple samples/model versions under a fixed fixture;
6. optionally branch replay with a declared opponent policy and RNG design;
7. compare micro choice with the model's observed full-game choice.

Useful bridge measures:

\[
\text{ChoiceConcordance}
=
\frac{1}{N}\sum_j
\mathbb{1}\{a^{micro}_j=a^{full}_j\}.
\]

\[
\text{ValueConcordance}
=
\operatorname{corr}
\left(
\Delta U^{micro}_j,
\Delta U^{full}_j
\right),
\]

where \(U\) must be an explicitly documented local or branch-replay utility, not a hidden “optimal Monopoly” scalar.

Counterfactual branch results are conditional on the frozen state, opponent policy, horizon, and RNG coupling. They are not causal facts about what “would have happened” in the original multi-agent trajectory.

Preserve the repository's ordered oracle tiers:

| Tier | Continuation method | Valid use |
|---:|---|---|
| 0 | one-step accounting | immediate cash, ownership, mortgage, payment, and legal-solvency effects |
| 1 | recorded continuation while still legal | closest realized-path comparison after replacing one action |
| 2 | deterministic scripted policies | cheap reproducible branch estimates |
| 3 | heuristic/RL policy ensemble | continuation-value robustness |
| 4 | re-queried LLM agents | behaviorally richer but expensive and stochastic |
| 5 | policy-robust interval | min/mean/max advantage across declared continuation methods |

Do not collapse Tier 0 accounting, Tier 2 scripted replay, and Tier 4 regenerated-agent behavior into one “oracle.” Their estimands and uncertainty sources differ.

## 12. Communication, deception, and collusion

The benchmark has unusually strong evidence for communication research because public messages, private rationales, state, and action consequences are jointly available. Preserve epistemic limits.

For every material claim:

- exact source decision/message ID;
- speaker and audience;
- public text;
- private rationale available to the reviewer;
- state-grounded truth status at utterance time;
- later action or state outcome;
- promise target and deadline, if any;
- alternative explanations such as error, stale belief, ambiguity, or changed incentives;
- reviewer confidence and adjudication status.

Use graded labels:

- inaccurate or unsupported claim;
- selective framing;
- possible strategic misrepresentation;
- high-confidence deception candidate;
- adjudicated deception, only after independent review.

Similarly, mutually beneficial coordination is not collusion. Require an explicit benchmark policy for prohibited coordination, exclusion, kingmaking, or side-payment behavior before strong collusion labels.

## 13. Figures and tables for the paper

### Main paper

1. Architecture and evidence-flow diagram.
2. Artifact/replay oracle diagram showing state versus strict artifact replay.
3. Benchmark comparison matrix against current adjacent work.
4. Experimental-design diagram for seed blocks and seat rotations.
5. One replay-clean full-game trajectory figure from Run 273.
6. One reliability/outcome mechanism figure from Run 115 or 172.
7. One negotiation-to-conversion episode figure from Run 157, 163, or 273.
8. Corpus table with exact denominators and replay status.
9. Claim-gating table.
10. Planned full-study primary estimands table.

### Appendix/artifact paper

- per-player cash, net-worth components, property count, building count, and mortgage liability;
- rent collected/paid trajectories;
- negotiation and auction episode tables;
- bankruptcy-window timelines;
- first-attempt validity/retry/fallback matrices;
- per-model cost/token/latency distributions;
- evidence-indexed case-study packets;
- micro/full concordance plots;
- source and generated-output manifest summaries.

Every plotted line or table row should resolve to a generated table and then to raw IDs. Decorative plots without denominators or provenance are not publication-ready.

## 14. Claim ladder

### Safe now

- The system implements an engine-authoritative, legal-action-constrained Monopoly environment.
- The artifact pipeline records decisions, attempts, actions, events, snapshots, language, usage, cost, and replay evidence.
- Eight completed bankruptcy games have standardized and exhaustive review packages.
- The corpus contains the exact totals in Section 3.
- Seven games pass strict artifact replay; all eight pass state replay.
- Run 191 has the exact bounded sequence-669 provenance mismatch.
- Specific mechanisms occurred in named evidence-backed episodes.
- Full games reveal interactions among acquisition, conversion, liquidity, negotiation, and collapse that final win labels obscure.

### Safe with explicit “descriptive case study” language

- reviewed winners used different pathways, including rent-engine construction, bargaining/consolidation, blocker conversion, and creditor-transfer compounding;
- several losing trajectories involved ontology errors, unproductive churn, weak liquidity, or forced rent shocks;
- retries often recovered invalid attempts, while a small number of fallbacks changed terminal outcomes;
- public/private records expose candidate strategic framing and promise reversals.

### Not safe yet

- one provider/model family is better at Monopoly;
- one model is more deceptive, collusive, reliable, or economically rational in general;
- a mechanism is prevalent across models;
- a particular strategy causally caused victory;
- temperature or model seed makes the complete LLM game deterministic;
- a hidden scalar value function is a ground-truth Monopoly oracle;
- the benchmark is the first long-horizon economic or bargaining benchmark.

## 15. Recommended model-role workflow

The role split below follows the current [GPT-5.6 release description](https://openai.com/index/gpt-5-6/), [ChatGPT model-picker guidance](https://help-lb.openai.com/en/articles/20001354), and [developer model-selection guidance](https://developers.openai.com/api/docs/guides/latest-model). Those sources position Sol Pro for the highest-quality difficult, long-running work and quality-first deep analysis; they position Max/Ultra-style Codex use around high-effort execution and coordinated agent/tool work. The [scientific-collaborator report](https://cdn.openai.com/pdf/f4b4a5da-b2de-418d-9fcd-6b293e9dc157/oai_ai-as-a-scientific-collaborator_jan-2026.pdf) is also useful process guidance, but none of these product descriptions make model output self-verifying.

Use high-capability models as complementary research instruments:

- **GPT-5.6 Sol Pro:** a single long-running pass for mathematical design, adversarial manuscript review, cross-literature synthesis, and polished replacement prose. Give it explicit evidence files, exact replay caveats, primary-source requirements, and a fixed output contract.
- **Codex Max/Ultra execution layer:** repository-grounded extraction, browser and shell work, artifact reconciliation, exact paths and IDs, hash checks, integration, and verification. Treat model-generated prose as a hypothesis until checked against frozen artifacts.
- **Independent human/reviewer pass:** adjudicate high-stakes deception/collusion labels, confirm claim gating, and approve the final statistical protocol.

The essential rule is not “Pro writes, Codex accepts.” It is:

```text
frozen evidence → Pro synthesis → repository reconciliation → claim gate → manuscript
```

## 16. Prioritized execution roadmap

### P0 — paper truthfulness

1. Correct Run 191's replay wording and decision/attempt terminology.
2. Reframe the abstract from cross-run association to audited mechanism case studies.
3. Add current primary literature and a dimensional comparison matrix.
4. Replace loose artifact language with the frozen package/replay contract.
5. Distinguish engine seed, model sampling, seat, roster, and provider drift.
6. Remove draft-only notes and incomplete citations.

### P0 — experiment specification

1. Freeze primary estimands and denominators.
2. Freeze model IDs, prompt/tool schema, retry/fallback policy, engine version, pricing snapshot, and sampling settings.
3. Choose a balanced seat/seed design.
4. Define cap/censoring rules.
5. Define inclusion of incomplete and failed runs.
6. Simulate sample size and interval precision before spending on the full matrix.

### P1 — micro bridge

1. Extract fixtures from high-evidence decisions in the eight packages.
2. Prioritize immediate solvency, trade completion, blocker value, auction bidding, mortgage/build conversion, and communication probes.
3. Freeze fixture manifests and scoring tiers.
4. Run micro/full concordance with explicit uncertainty.

### P1 — analysis consistency

1. Regenerate package-level integrity prose so it acknowledges that the later qualitative layer now exists; several deterministic reports correctly describe their original task as deterministic-only but read stale when viewed as current package summaries.
2. Add a cross-package index with run IDs, replay status, review validation status, and report links.
3. Add automated assertions that every manuscript run statistic resolves to a canonical table cell.

### P2 — full study

1. Execute seed blocks and seat rotations.
2. Monitor artifact quality without changing the benchmark contract mid-block.
3. Preserve failed/incomplete attempts.
4. Run preregistered primary analysis.
5. Treat exploratory mechanism and communication findings as separate families.

## 17. Unresolved research decisions

- Which four-model roster is the primary comparison, and are model versions stable long enough to complete a block?
- What game cap and termination/censoring policy will be used?
- Which economic-balance-sheet convention is canonical?
- Which outcomes are confirmatory versus exploratory?
- What is the exact policy definition of deception, collusion, kingmaking, and prohibited coordination?
- Which opponent policy and RNG coupling define branch counterfactuals?
- How will provider/backend drift be recorded and analyzed?
- Will raw private rationales be released, redacted, or access-controlled?
- Is the first submission a benchmark paper, a measurement/case-study paper, or a combined instrument-plus-pilot paper?
- What compute/cost budget constrains the seed-by-seat matrix?

## 18. Next-researcher checklist

Before editing empirical prose:

- read the three analysis guides;
- read this handoff;
- inspect the relevant package `README.md`;
- confirm replay status in `analysis/reports/integrity_report.md`;
- resolve every number to `analysis/tables/` or `analysis/quality/`;
- resolve every qualitative claim to `evidence_index.csv` and a raw ID;
- never infer action legality from prose when `decisions.jsonl` exists;
- never infer applied outcome from rationale when `actions.jsonl` and `events.jsonl` exist;
- never call Run 191 replay-clean without the state/artifact distinction;
- never use the eight selected games as a balanced leaderboard;
- never edit frozen `run/` or `quality_check/`;
- rerun source-hash checks after any downstream work;
- verify the final analysis ZIP is byte-equivalent to the final `analysis/` tree where the package contract requires it.

## 19. Provenance note for this handoff

This handoff was assembled from the repository's manuscript, three analysis guides, historical research memos, and all eight current saved-game review packages. One dedicated GPT-5.6 Sol Pro project task was also completed for mathematical, literature, and manuscript synthesis. The full 112,232-character response remains in the linked [ChatGPT project conversation](https://chatgpt.com/g/g-p-6a695a6288888191b7bd6afc42ea2b12-monopolybench/c/6a695f12-e6a4-83ea-91df-6e3dfed06552), while its locally reconciled conclusions and provenance are preserved in `docs/research_raw/gpt-5-6-sol-pro_monopolybench_synthesis_2026-07-28.md`. No follow-up research prompt was submitted. Model output is preserved as research input, not treated as artifact authority.

The exact ten local files supplied to the single Pro pass, with byte counts and SHA-256 hashes, are recorded in `docs/research_raw/gpt-5-6-sol-pro_source_manifest_2026-07-28.csv`. The compact eight-game numeric/replay ledger is `docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv`; it was generated locally for the broader repository audit and was not sent in a second model task.

At task start, the worktree already contained a modified `monopolybench_ieee_draft_v0_1.tex` and an untracked `docs/research_raw/prism_2026-07-28/` import from the preceding Prism synchronization. Those are preserved as prior user work and are not silently normalized by this research pass.

No frozen saved-game `run/` or `quality_check/` file should change as a result of this research task.
