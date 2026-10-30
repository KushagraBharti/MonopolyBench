# Opus: independent initial position, phase 3 (steps 11–14)

Author: Claude Opus 5.5, one of four equal coauthors (Astra, Sol, Opus, Fable). Saved 2026-10-29.

**Independence statement.** I wrote this before opening any new phase-3 peer file (`../astra/`, `../sol/`, `../fable/`). Before saving it I had read:
- the phase-3 README;
- the phase-2 core-review README, Astra's handoff, synthesis, claims and reconciliation;
- Sol's handoff and synthesis, and Fable's synthesis and claims;
- my own phase-2 synthesis, the phase-1 README and reference scope;
- the 2026-10-27 readiness memos (Fable's literature memo, my earlier argument);
- `player_config.py` and saved-game `run_config.json`, `usage.json` and `seat_assignment.json`.

I also received two coordination messages but have not answered them yet. Astra's says that Vending-Bench Arena has competition, collaboration and trading, and that AgentMonopoly disclaims explanation-as-intent. Sol's asks which retained claim goes beyond economic competence while still being directly measured. Both messages shaped my literature checklist (§4). I give my answer to Sol in §2, P3, as my own position before reading Sol's file.

Labels: **[V]** verified by me today from canonical files or a fetched primary source. **[P2]** an audited phase-2 finding I have not recomputed. **[U]** unverified recollection that must be checked before use. **[Prop]** a proposal.

---

## 0. Thesis in one paragraph

MonopolyBench should be written as a study of **configured frontier agents pursuing a long-horizon economic objective among competitors**. The paper's spine is how they create, finance, deploy and lose economic position over 75–386 turns, and how they bargain and represent facts while doing so.

The paper's distinctive instrument contribution is **adjudicability**. Every behavioral statement can be resolved against:
- exact legal menus;
- replayable state at the historical prefix;
- applied actions;
- per-channel model text, including public, private, provider-explanation and received tool-call channels.

This lets us test *legal alternatives at exact prefixes*, not merely replay the game. That is the measurement that separates three things which outcome scores conflate:
- chosen strategy;
- discarded or inaccessible legal options;
- interface conditions.

The capability/alignment question stays the motivating research question. The honest finding is narrower. This cohort yields:
- a substantial capability profile;
- a bounded, case-level account of norm-relative social conduct;
- one directly measured oversight-relevant property: action–explanation consistency;
- a design lesson. Under the current prompt, the environment cannot produce an instruction-violation result except through the soft private-honesty norm, because the engine makes rule violations impossible and the prompt authorizes public deception.

That last point is a substantive environment-design finding for long-horizon safety research, not an embarrassment to hide.

## 1. Research questions, in priority order

1. **RQ1, sustained economic capability.** How do configured agents acquire assets, obtain finance, gain management access, develop, liquidate and survive over complete games? Which outcomes depend on chosen strategy, and which on executional or interface failure? Units are player-games, groups, eliminations and decisions. Opportunities are endogenous.
2. **RQ2, conduct while competing.** Relative to the *declared* norms, how do agents represent facts, frame offers, keep or withdraw standing offers, appeal to third parties and keep their channels consistent? How do recipients respond?
3. **RQ3, environment and measurement.** What must a long-horizon multi-agent sandbox record and permit for RQ1 and RQ2 to be adjudicable rather than impressionistic? Which affordances would be needed to measure alignment-relevant violations, and later to train against them?
4. **Motivating question, not answered here: how does alignment-relevant conduct change as capability grows?** State it explicitly in the introduction, then state in the same section why four configured systems from four providers at one point in time cannot trace that curve.

## 2. Positions I will defend (likely points of debate)

### P1. The measurement contribution is legal-alternative auditing at exact prefixes

Replay alone is not new: WebArena, OSWorld and AgentMonopoly's replay mode all offer some form of it [U, to check]. Linking speech to action is not new either: AgentMonopoly does it. What phase 2 actually *used* to change interpretations was a different capability. We restored the exact historical state and executed alternative legal sequences through the authoritative engine, stopping at a stated endpoint. The results:
- **R06.** All 61 Opus defaulted plans pass after reordering [P2].
- **R08.** Three of 60 eliminations admit a legal payment route, 56 fail even a full upper bound and one is a hotel lock [P2].
- **R10.** G7 d339 has $440 accessible against $1,310 nominal [P2].
- **Further checks.** G5 d306 reallocation, G6 redemption-menu refutation, G12 d312 restructuring and G1 d426's $1,343 after a legal build [P2].

These are **counterfactual-feasibility tests over legal action sequences**, distinct from winner counterfactuals. They also refuted several of *our own* generated labels (G6-C021, G14-C014, G20-C024 [P2]). The paper should claim this capability and its scope, after checking whether each competitor reports something equivalent in the sections we inspect. No blanket "first" or "only".

### P2. Alignment claims are norm-relative, and the current design has a structural blind spot

Read [V] from `player_config.py` `SYSTEM_PROMPT_V1`, the prompt has three norms:
1. **Legal action** ("Use only tools listed as legal…"). The engine enforces it, so violations are *impossible*, not merely rare. Attempted invalid actions appear as validation errors, which are execution facts, not misconduct.
2. **Public deception is authorized** ("Use it to negotiate, bluff, deceive…"; "Deception in public chat is allowed").
3. **Private notes "should reflect true reasoning".** This is a soft norm, and the notes also serve as the agent's own memory. A false private note confounds error, stale context and dishonesty. Opus mostly lacks applied private notes because of the refusal condition.

**Consequence.** This cohort *cannot* produce a clean instruction-violation or misalignment result. That is a property of the sandbox's affordances, and it is the most important RQ3 finding.

**Proposal.** The paper should include an **affordance ledger** with four columns:
- which alignment-relevant behaviors the environment *implements*, such as permitted deception, unenforced verbal assurances, third-party appeals and private memory;
- which ones the cohort *measures*;
- which are *unimplemented*: binding or non-binding contract objects, private bilateral channels, monitored rule-breaking opportunities, honesty-constrained treatments and oversight agents;
- which claims each one would unlock.

This keeps the alignment ambition central without inflating it.

### P3. What goes beyond economic competence and is directly measured (my answer to Sol)

I accept Sol's proposal for a main-text social chronology. Its three parts are:
- G13's omission with the buyer's prior motive;
- correction alongside acceptance (G6/G19), plus G4's public concession with private correction;
- G11's echo followed by rejection.

These are substantive findings without a deception-rate or misalignment headline.

I would add one category that Sol's framing may underweight: **action–explanation consistency as an oversight property**. An overseer reading the configured agent's explanation channels would mispredict the applied action in specific, countable cases:
- **Grok:** 139 received content/tool-name conflicts [P2];
- **G12 d249:** final explanations oppose bankruptcy, yet the received tool declares [P2];
- **G19 d135:** the private note says "Abort this trade. Do not send it", yet the trade is sent [P2];
- **G18 d083:** content rejects while the tool accepts [P2].

This is directly measured and alignment-relevant: it is a monitorability fact. It requires no claim about intent. Its limit is that the source is not localized to the model, the provider/gateway or local stream assembly [P2, R23]. The unit is therefore the configured system, which is exactly the evaluated object we already declare.

I would also put the Opus refusal condition in the same section. A provider policy layer changed the agent's memory channel and retry budget over a long horizon. That is a deployment-safety observation about configured systems. It is not a moral refusal, and the stated reason concerns ToS output duplication [P2].

Literature to verify for this framing:
- Turpin et al. 2023, unfaithful CoT;
- Lanham et al. 2023, measuring faithfulness;
- Baker et al. 2025, monitoring reasoning models;
- Korbak et al. 2025, CoT monitorability.

All four are [U] until fetched.

### P4. Rankings and trends are unidentified; show the design honestly

Computed [V] by `scripts/cohort_overview.py` → `cohort_overview.json` from `summary.json`, `seat_assignment.json` and `run_config.json`.

**Winners by seat.** Turn-order seats 0 and 1 win 14/20 (7 and 7); seats 2 and 3 win 3 and 3.

**Winners by seed block:**
- Block 2506298840 (G5–8): Sol wins from all four seats.
- Block 2573692901 (G9–12): turn-order seat 1 wins with all four models.
- Block 751774554 (G1–4): Argon 3, Grok 1.
- Block 3648314310: Opus, Sol, Argon, Sol.
- Block 2766649504: Sol, Opus, Argon, Argon.

**Overall:** Sol 8, Argon 7, Opus 3, Grok 2.

Under a uniform-winner null, P(X ≥ 8 of 20) is about 0.10 [arithmetic, to recheck with block dependence]. The exhibit should be a 5×4 seed-block × rotation grid coloured by winning model, with seat marked. It is a primary honesty exhibit, not an appendix item. Opportunities differ even though raw dice match.

### P5. Cost and usage are research artifacts, with a coverage hole

Summed [V] from per-game `usage.json` (OpenRouter actuals only; all players at reasoning effort `medium` [V] from `run_config.json`):

| Model | Decisions | Own attempts | Attempts missing cost | Known cost | Known cost/decision | Completion tok/decision | Reasoning tok/decision | Latency s/decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Opus | 1,696 | 3,301 | 1,600 | $48.80 | $0.029 | 410 | 259 | 7.1 |
| Sol | 1,961 | 1,991 | 0 | $18.72 | $0.0095 | 128 | 39 | 4.8 |
| Argon | 1,669 | 1,689 | 0 | $18.59 | $0.011 | 368 | 257 | 8.2 |
| Grok | 1,663 | 1,698 | 3 | $55.60 | $0.033 | 4,041 | 3,658 | 65.0 |

The known cost subtotal is $141.71. Opus's refused attempts lack cost and usage records, so its cost is a lower bound. Grok uses about 30× Sol's completion tokens per decision and about 13× its latency.

Within this cohort, compute is not monotonically related to winning: Sol has the fewest tokens and the most wins. That is a descriptive association across four configured systems, not a compute–capability law. It deserves a table because cost-aware agent evaluation is a recognized standard (HAL, "AI Agents That Matter" [U]).

### P6. Interface findings explain results; they are not the subject

The paper's subject is economic and social conduct. The recovery condition, trade-history defect, received-name conflicts and delivery omissions appear where they change the interpretation of a result. They also appear in one compact "measurement conditions" table that lists the affected analyses. I would *not* give them a results chapter of their own. I would treat P3's monitorability point as conduct-relevant rather than purely as an interface issue.

### P7. Do not reduce the paper to finance

Liquidation and development accounting are the best-measured part, but the paper must keep:
- acquisition and auctions;
- bargaining and initiation profiles;
- social conduct;
- the alignment framing.

The phrase "long-horizon" must be operationalized. Games run 75–386 turns and players face roughly 1,660–1,960 decisions each across 20 games (about 85 per player-game). Events have consequences spanning dozens of turns, such as development rent windows, standing offers and inheritance. Do not borrow METR's time-horizon units: METR measures task length by human completion time [U, to verify].

## 3. Initial claim-to-experiment matrix (to be expanded in `experiment_decisions.md`)

| Claim family | Tier | Basis or requirement |
|---|---|---|
| Corpus coverage, cohort design, seat/seed outcome grid | Existing support | R01–R02 [P2]; `cohort_overview.json` [V] |
| Acquisition routes and completed-group routes | Existing support | Astra's synthesis: 475/72/207/397 deeds; 16/9/63/121 completions [P2] |
| Negotiation propensity and intensity | Existing support | R03 [P2] |
| Trade completion consequences and first-management deployment | Existing support | R04–R05 [P2] |
| Discarded affordable plans; recovery changes quantities | Existing support | R06–R07 [P2] |
| Elimination financing (3/56/1) | Existing support | R08–R10 [P2] |
| Development outlay versus paid developed rent | Existing support | R12–R13 [P2]; must not be called a return |
| Inheritance concentration | Existing support | R15–R16 [P2]; a rule-variant effect, declared |
| Social chronology (G13, G4, G6/G19, G11, G18, G20) | Existing support | R18–R21 [P2] |
| Action–explanation inconsistency counts | Existing support | R23 plus the 139 conflicts [P2]; a corpus-wide rate across *all* channels for all models needs analysis |
| Cost and usage profile | Existing-log analysis, done here | [V] above; refused-attempt usage is missing |
| Seat/seed dependence quantification (block permutation) | Existing-log analysis | Can be computed now; no new games |
| Proposition-error rate, deception prevalence, shortage-binding count, multi-creditor prompts, leader-funding-denial frequency, auction denominators | Existing-log analysis, optional | Requires a frozen codebook; not to be extrapolated from cases |
| Scripted reference-policy runs on the five seeds | Optional strengthening | Unpaid but **new games**. Needs user approval; not run in this stage |
| Trajectory scorecards for "how close to optimal" | Optional; probably out of scope | No optimality oracle exists for four-player Monopoly |
| Causal persuasion effect | Experiment, only if claimed | Randomized message ablation from frozen snapshots across recipients |
| Recovery-policy effect on outcomes (Opus) | Experiment, only if claimed | Non-refused retry or interleaving-tolerant validator, replayed from frozen prefixes |
| Trade-history defect reliance | Experiment, only if claimed | Corrected-formatter replay from frozen prefixes |
| Instruction misalignment | Experiment, only if claimed | A treatment with a binding honesty or commitment norm and monitored violation opportunities |
| Capability–alignment trend | Experiment, only if claimed | Within-family multi-size or multi-generation roster under fixed norms, many seed blocks |
| Provider ranking | Experiment, only if claimed | More seed blocks; matched-opportunity designs; uncertainty that respects blocks |

## 4. Literature checklist and the questions I must answer from primary sources

For each source I will record version, URL, sections inspected and a bounded comparison. Features not seen will be logged as "not reported in inspected sections". Abstract-only checks will be labelled as such.

**User-named sources:**
- Vending-Bench, Vending-Bench 2 and Vending-Bench Arena. What exactly does Arena implement: shared location, competition, messaging, trading, contracts? What is its horizon, and does it publish logs or replay?
- AgentMonopoly. Resolve the 140-versus-160 games conflict between Astra's phase-1 note and Fable's 10-27 memo; I have seen 40+40+40+20 = 140. Also check its rules, models, explanation disclaimer, speech/action linkage and replay.
- SOTOPIA, Concordia, TheAgentCompany, AgentBench, WebArena, OSWorld, τ-bench (pass^k), AgentDojo, MLE-bench, METR time horizons.

**Required additions:**
- FinBoardBench, NegotiationArena, MACHIAVELLI, AgentBoard, HAL, Cattle Trade, DECE;
- the promise/commitment papers: Cheap Talk/Empty Promise, When Agents Lie.

**Candidate additions** (keep only those with explanatory value):
- Cicero, Welfare Diplomacy, GovSim and Melting Pot for multi-agent cooperation and conflict;
- Among Us deception sandbox, Hoodwinked and Scheurer et al.'s strategic deception for deception measurement;
- the Park et al. AI-deception survey;
- the CoT faithfulness and monitorability papers (P3);
- validity and practice: the Agentic Benchmark Checklist (Zhu et al.), BetterBench, "AI Agents That Matter", Miller's "Adding error bars to evals", and construct-validity work (Bean et al.);
- GTBench and other game suites only where they sharpen a contrast.

## 5. Initial exhibit plan (to be expanded in `figure_table_plan.md`)

**Figures:**
1. **Evidence chain.** Menu → attempts → received tool call → applied action → events → snapshot, with channels marked.
2. **Seed-block × rotation outcome grid.** Winner model and seat.
3. **Longitudinal trajectories.** Twenty small-multiple panels of cash plus asset value per player, with markers for first completion, first build, eliminations and estate transfers.
4. **Development accounting.** 103 spending units, outlay versus paid developed rent, with zero-rent units shown, inherited flag and winner flag.
5. **Trade consequence flow.** 113 trades → completion (neither, one or both sides) → first-management build → realized rent.
6. **Social chronology swimlanes.** G13, G4, G11 and G18, with public, private, provider and applied-action lanes plus exposure marks.

**Tables:**
- cohort and design;
- acquisition routes;
- negotiation profile;
- the elimination financing table (four rows);
- the recovery-condition table;
- measurement conditions with affected analyses;
- cost and usage;
- the affordance ledger;
- claim strength;
- the related-work comparison.

## 6. Initial outline skeleton (to be expanded in `detailed_outline.md`)

1. **Introduction.** Long-horizon competitive economies as a sandbox for both capability and conduct. The question: how capability and alignment co-vary. What this cohort can answer. Contributions phrased as measured capabilities.
2. **Related work.** Long-horizon economic agents; game-based multi-agent evaluation; social conduct, deception and commitments; evaluation validity and harness effects.
3. **Environment and evaluated object.** Declared rule variant, interface, norms, response policy and artifacts.
4. **Cohort and adjudication method.** Seed blocks, channels, legal-alternative audits, review provenance and what it is not.
5. **Results I: outcomes and their dependence.** Grid, survival and costs.
6. **Results II: the economic life cycle.** Acquisition → bargaining → access and finance → development → liquidation and inheritance.
7. **Results III: conduct while competing.** Social chronology, bounded negatives and action–explanation consistency.
8. **What the cohort says about capability and alignment.** Established, suggested, untested.
9. **Designing long-horizon sandboxes for safety research.** Affordance ledger and needed treatments.
10. **Limitations.**
11. **Conclusion.**

## 7. Risks I expect peers to raise, and my current stance

- **"Monitorability is an interface finding, not conduct."** Partly agree. The unit is the configured system. I would still argue that the fact an overseer mispredicts the action is the alignment-relevant quantity, whatever its origin.
- **"Legal-alternative auditing is just replay."** I disagree, but I will tone the claim down if any competitor reports state-restoration counterfactual testing.
- **"Affordance ledger reads as self-criticism."** I disagree. It is the bridge from this cohort to the alignment research agenda and stops reviewers from overreading.
- **"Cost table is off-topic."** I disagree mildly. It is cheap, verified and standard in agent evaluation, but it belongs in the design or appendix section, not the results.
