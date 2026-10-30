# Independent paper readiness assessment, Sol, 2026-10-27

We can begin drafting one integrated paper now. We are not submission ready. The immediate task is to turn a functioning research system and a rich observational cohort into a reproducible scientific argument. More paid games are not an automatic prerequisite. The new opportunity and deployment measurements require validation before publication, and the historical manuscript needs a substantial rewrite.

My recommended central claim is that MonopolyBench supports opportunity-aware longitudinal evaluation of economic agents. Its records let researchers distinguish assembling productive assets, obtaining access and financing to use them, choosing among actually available actions, and the consequences for both trading parties. The present cohort demonstrates why those distinctions matter. This is a bounded contribution about an environment, measurements, and observed behavior, rather than a general model ranking or a validated scalar of economic intelligence.

The proposed 40% findings, 40% environment and infrastructure, 20% validation is a useful flexible target. Lead the abstract and opening exhibit with a supported economic result. Explain enough methods before the detailed results that the reader can assess it. Infrastructure deserves a full contribution. Its scientific purpose should organize that section, rather than a tour of implementation files.

## Scope, provenance, and independence

I read AGENTS.md, both current parent discussions, the available historical imports, prior Sol and Opus delegate findings, and the relevant repository workstreams. I independently inspected the current engine, replay, telemetry, baseline, public-state fixture reconstruction, rule tests, adversarial artifact tests, cloud validation record, manuscript, and paper assets. I fetched primary texts for AgentMonopoly, FinBoardBench, Cattle Trade, NegotiationArena, and AgentBoard. I directly debated the full paper argument with Astra, Opus, and Fable, including the objections and corrections below.

The current discussions are [MonopolyBench Economic Capability and Alignment](t3-thread://v1/ef389b99-261b-4fa6-b535-706d79392595) and [Explain MonopolyBench Benchmark Design](t3-thread://v1/cfa77083-1e43-4701-abea-805566ff8d52). Their latest user corrections supersede the earlier split into two papers and the tendency to emphasize fallback accounting.

Evidence labels in this memo have the following meaning.

- **Verified** means I checked the underlying repository material or computed the quantity in this round.
- **Inherited** means I read another researcher's report or an archived validation record but did not rerun that experiment.
- **Inference** means an interpretation of the evidence, not an identified causal effect.
- **Proposal** means work or framing that has not yet been completed.

I made no changes to the engine, prompts, policies, canonical runs, or existing manuscript. No provider calls, paid games, deployment, or commits occurred. All new files are in this dated directory.

## Reproduction and experiment design

**Verified.** [sol_reproduce.py](sol_reproduce.py) reads the two collection indices and their 20 known run directories. It reconstructs ownership and cash from canonical events, distinguishes voluntary buying and auctions from bankruptcy inheritance, follows actual transfers after each accepted trade, and extracts selected management menus from the 20 decision ledgers. It does not infer trade direction from the original initiator's offer because counteroffers can reverse authorship.

The script asserts contiguous event sequences, exact requested-decision versus action identity order, final cash equality for all 80 player-games, and final ownership equality for all 20 terminal snapshots. These checks passed. They validate parts of this reconstruction, not every scientific interpretation or time window. Source file hashes are in [sol_source_hashes.csv](sol_source_hashes.csv).

| Corpus fact | Independently reproduced result |
| --- | --- |
| Games and players | 20 games, four configured participants per game |
| Design | Five seeds, four cyclic seat rotations per seed |
| Endings | All 20 end by bankruptcy, without a turn cap |
| Decision and event counts | 6,989 applied decisions and 50,918 events |
| Negotiation | 526 initial proposals, 394 counters, 113 accepted trades |
| Nominal effort | Medium for all configured endpoints |
| Rules and execution | audit_corrected_v2; finance_before_bankruptcy_v2; fail_without_action_v2 |
| Interaction limits | 20 trade exchanges, 200 auction actions |
| Model roster | Opus 5.5, GPT-6.1 Sol, Gemini 4 Argon, Grok 4.7 |

The two roots are `saved_games/railway-research-12-games-2026-10-25/` and `saved_games/railway-research-8-games-2026-10-26/`. [sol_games.csv](sol_games.csv) preserves the exact package path for every game. Model names here identify configured participants under their recorded execution conditions, including refusal recovery. They do not mean bare model weights under an identical computational budget.

**Verified.** Games 1 to 4 use source `42f85183`; games 5 to 20 use `d6808534`. The source diff changes cloud concurrency and UI presentation, with no engine or prompt changes. The executable fingerprints nevertheless differ and should remain in methods and released manifests. The first source identity is perfectly associated with the first seed block, so those runs cannot independently estimate a source-version effect. See each collection's `game-index.csv` and `audit/cohorts.json`, and `python/packages/arena/src/monopoly_arena/treatment.py:9` for fingerprint scope.

**Verified.** Every model occupies every absolute seat once within each seed. Cyclic rotations preserve relative opponent order, so they cover four of the 24 possible orders. There is one roster and one live realization per seed-rotation cell. The observations do not identify opponent robustness or live-provider repeatability. Thousands of decisions do not create thousands of independent strength comparisons.

The eight older games remain a separate exploratory mechanism corpus. The July workstream memos and `paper/claim_source_audit.md` concern that historical corpus. They are useful sources for cases and prior analysis, not current-cohort result tables.

## Findings that can support the paper

### 1. Negotiation role matters, and initiation is an incomplete behavioral profile

**Verified.** Counts below come from events and the reconstruction, rather than model explanations. Completed trades count participation once per side, so the column sums to twice the number of trades.

| Configured participant | Wins | Initial proposals | Completed as initiator | Completed as recipient | All completed participation | Rent received |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sol | 8 | 132 | 19 | 41 | 60 | $41,299 |
| Gemini | 7 | 18 | 11 | 25 | 36 | $42,360 |
| Opus | 3 | 240 | 44 | 26 | 70 | $23,995 |
| Grok | 2 | 136 | 39 | 21 | 60 | $13,500 |

Gemini received 205 initial offers and closed 25 deals begun by others. Low initiation therefore coexists with substantial recipient-side participation. Calling it non-negotiating would misdescribe the records. Opus initiates most frequently but has fewer wins and less cumulative rent than Sol or Gemini. The highest-proposal participant wins only two of the 20 games.

**Inference.** These facts motivate measuring roles, terms, opportunities, and follow-through separately. They do not show that initiating negotiations reduces performance, that Gemini's trade selection is globally optimal, or that cumulative rent measures intrinsic strength. Longer survival generates more opportunities to collect rent, receive offers, and act. Per-roll rates can describe activity, but do not remove endogenous exposure.

**Counterexamples.** Both game 14 Sol and game 15 Gemini win with zero completed trades participated in. Negotiation is one route to productive ownership. It is not necessary in every successful trajectory. In game 14, Sol completes orange by buying Tennessee at turn 47, then buys six houses, mortgages other assets, and adds three more houses in the same turn. In game 15, Gemini completes orange at the same turn, buys six houses, mortgages assets, and adds two more.

Exact anchors are game 14 `campaign-8d77f7b822c6458fa9a5be0e884f74ef-1-a12c9b8580`, events 643, 650 to 655, 661, 667, 673, and 679 to 681; game 15 `campaign-8d77f7b822c6458fa9a5be0e884f74ef-2-291c6c4036`, events 711, 718 to 728, 734, 740, 746, 752, and 753. Their package paths are in [sol_games.csv](sol_games.csv).

### 2. Trade effects are bilateral, and cash pressure changes their interpretation

**Verified.** Of 113 accepted trades, 60 newly complete no color group, 43 complete a group for exactly one side, and 10 complete one for each side. This yields 63 trade-completed color-group episodes. [sol_trades.csv](sol_trades.csv) records both parties, cash before and after settlement, actual property transfers, and event IDs.

| Participant granting a group while receiving none | Trades | Pre-trade cash below $150 | Median cash before acceptance | Median cash after settlement |
| --- | ---: | ---: | ---: | ---: |
| Sol | 8 | 4 | $178 | $812.50 |
| Gemini | 5 | 1 | $287 | $537 |
| Opus | 20 | 12 | $79.50 | $265.50 |
| Grok | 10 | 4 | $294.50 | $650 |

Pre-trade means the ledger balance at `TRADE_ACCEPTED`, before its cash effects. Post-trade includes the complete settlement, including mortgage-transfer interest. Fable independently reproduced these exact pre/post values after we resolved a transaction-boundary discrepancy.

**Inference.** Some one-sided completions are consistent with liquidity-seeking asset sales. The Opus pattern is particularly clear. A trade that strengthens a rival can also buy immediate solvency. Counting such exchanges as generosity, poor negotiation, or harmful trade without considering price, liquidity, and alternatives would prejudge the economic question.

**Claim boundary.** New color-group ownership is a deterministic consequence, not a value oracle. These counts omit other benefits such as blocker retention, railroad consolidation, compensation, survival, and financing. They cannot establish whether a trade was mutually beneficial or regretful. Follow-up should report cash and productive consequences for both sides, rather than replace an LLM judge with an equally unsupported completion-quality score.

### 3. Opportunity assembly, access, and deployment are different measurable stages

**Verified exploratory computation.** Trade-group episodes retain acquisition turn, first actual management decision, first build, legal build availability, and ownership loss. Follow-up ends when the group loses a constituent deed. Rent is counted after acquisition and only while the owner retains the group. This corrects the earlier use of first-ever builds and whole-game group rent as post-trade consequences.

| Participant | Player-games with no non-inherited color group, out of 20 | Trade-completed groups | Built on first management turn | Build legal on entry to that turn | Built that turn among entry-eligible groups |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sol | 1 | 17 | 16 | 15 | 14 of 15 |
| Gemini | 2 | 18 | 17 | 13 | 13 of 13 |
| Opus | 2 | 15 | 7 | 7 | 5 of 7 |
| Grok | 5 | 13 | 3 | 7 | 2 of 7 |

Across 63 acquired groups, 43 receive a build during the owner's first actual `POST_TURN_ACTION_DECISION` turn. At entry, 42 groups have a constituent street in the recorded `buildable_space_keys` and expose the build action. Of these, 34 receive a build that turn. If legality becomes available later during that turn through financing or unmortgaging, the eligible denominator rises to 54, with 43 built. Availability here means at least one currently legal building purchase. It does not mean that the desired full development plan is affordable or executable.

The two-stage denominator matters. Evaluating only eventual group owners would omit one player-game for Sol, two each for Gemini and Opus, and five for Grok in which no group is assembled through buying, auctions, or trades. Conditioning only on a legal first management menu would also hide financing and access decisions that help create that menu.

**Verified reconciliation with peers.** A next-own-turn computation finds 41 deployments, whereas the first actual management-window computation finds 43. The difference is game 6 Opus pink and game 8 Gemini dark blue.

- Game 6 pink is acquired at turn 74. Its first management menu is at turn 85, decision `campaign-c0761df29478459ab4cea725626ea259-1-f79cf92b21-dec-000159`. It exposes pink building options and the group is built then.
- Game 8 dark blue is acquired at turn 77. Its first management menu is at turn 87, decision `campaign-c0761df29478459ab4cea725626ea259-3-c0ff63802e-dec-000182`. It exposes dark-blue building options; financing and development follow that turn.

Astra independently checked both raw menus and intervening jail decisions. This resolves the count difference, rather than treating it as noise.

**Interpretation accepted after Astra's objection.** Neither window is universally correct. First-menu responsiveness factors out the route to management access. Jail decisions can include paying to leave or rolling again, so the delay is partly endogenous strategy. Publish acquisition-to-access delay, access and financing choices, and action at the offered opportunity as different quantities. The earlier fixed global-turn threshold was especially asymmetric as an opportunity-use denominator for trade recipients, but a declared elapsed-time measure still asks a legitimate speed question.

**Not yet a final publication result.** These new rates need independently specified scenario checks and targeted audit of boundary cases. Do not use the earlier 74% rent headline, win fractions over group episodes, or the claim that acquisition is not the bottleneck. Groups in the same game share owners, outcomes, and opponents. A group-level win fraction is not an independent game-level sample.

### 4. Seed blocks reveal heterogeneity that an aggregate win count conceals

**Verified.** All 30 within-seed game pairs have identical ordered raw dice pairs through the shorter stream's end. [sol_dice_checks.csv](sol_dice_checks.csv) preserves each comparison. It does not claim identical turn indices, landings, jail choices, player-specific exposure, or downstream states.

| Seed | Games | Winning models in rotation order | Winning seats, numbered from zero |
| --- | --- | --- | --- |
| 751774554 | 1 to 4 | Gemini, Gemini, Gemini, Grok | 2, 1, 0, 0 |
| 2506298840 | 5 to 8 | Sol, Sol, Sol, Sol | 1, 0, 3, 2 |
| 2573692901 | 9 to 12 | Sol, Gemini, Grok, Opus | 1, 1, 1, 1 |
| 3648314310 | 13 to 16 | Opus, Sol, Gemini, Sol | 0, 0, 0, 2 |
| 2766649504 | 17 to 20 | Sol, Opus, Gemini, Gemini | 1, 3, 0, 3 |

One block has the same seat winning with every model; another has Sol winning from every seat. Those are descriptive contrasts worth tracing. They do not cleanly separate luck and skill. Earlier decisions alter the mapping between a common draw stream and each player's economic exposure.

The first builder wins 17 of 20 games. The counterexamples are game 15, where Opus builds first and Gemini wins; game 17, where Opus builds first and Sol wins; and game 20, where Grok builds first and Gemini wins. The eventual winner has the largest net rent in 18 of 20 games, unlike the 8 of 8 observation in the older corpus. Neither statistic establishes that developing first causes victory. They can motivate a trajectory figure, rather than a universal strategy claim.

## Social evidence and interpretation

**Verified current case.** Game 16 contains anti-leader appeals, retained blockers, financing-aware trades, and attempted exceptions. It is a good social-economic case. The canonical run is `campaign-8d77f7b822c6458fa9a5be0e884f74ef-3-6f1cbd6799` under `saved_games/railway-research-8-games-2026-10-26/game-16-386turns-24b86ed0/run/events.jsonl`.

- Event 2711, turn 203, records Sol keeping Illinois and Pacific off-limits to Gemini.
- Event 2808, turn 207, records Opus offering North Carolina to Gemini for $450.
- Event 2976, turn 217, records Sol negotiating $400 plus Electric and North Carolina for the dark blues while explicitly reserving development liquidity. Event 2982 accepts it; events 2983 to 2989 settle it; building begins at event 3007 after additional financing.
- Event 3036 repeats Opus's warning against trading with the leader. Event 3260 offers North Carolina to that leader again, now for $180.

The record supports appeals for restraint, responses, actual bargaining, and exceptions. It does not yet establish a binding reciprocal coalition, prohibited collusion, or breach of a precisely specified promise.

**Verified historical case.** Run `mock-2413970733-53b199c1` has an economically consequential assurance and same-turn reversal. Events 3607 and 3612 to 3624 record GPT-5.5's assurance that yellow will remain blocked, Claude's stated reliance, and the sale of Ventnor and Short Line for $300. After an attempted railroad sale fails, events 3642 to 3669 record GPT selling Ventnor to Gemini for $250, completing yellow. See `saved_games/frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview/run/events.jsonl` and decisions 545 to 556.

This is strong evidence of assurance, reliance, and incompatible subsequent conduct. Deliberate deception from the outset is not identified. A changed plan under financing pressure remains plausible. Present it as a historical mechanism case, not current-roster prevalence.

**Verified provenance objection from Opus.** Game 1 decision 112 has `reject_trade` in response content and `accept_trade` in the structured tool call, with identical public/private arguments. The parser and applied event follow the tool call. I opened the raw `*_dec-000112_response.json` and confirmed equality of those arguments. The stored file is under the game 1 run's `prompts/` directory. Acceptance is event 754. The later Gemini light-blue deal is event 788, with development beginning at event 859 and hotels following at 876 to 878.

This qualifies the narrative that Grok deliberately assembled the upstream package. Gemini's counteroffers and builds remain observable responses to its actual opportunities. Content is not privileged ground truth about intention. The available evidence does not identify model, provider, gateway, or forced-tool choice as the cause. Removing a few contradictory trade records cannot reconstruct an unaffected game because the transferred deeds alter later opportunities.

I agree with Astra that such records remain observable communication/action disagreements. Flag response inconsistency, preserve the message and action, and adjudicate intentional deception separately. Blanket exclusion would bias a descriptive say/do alignment count.

**Verified prompt constraint.** `python/packages/arena/src/monopoly_arena/player_config.py:14` permits competitive deception. Existing games can support descriptive honesty, assurance, and coordination analysis. Deception alone cannot establish instruction violation. A claim about following an honesty or anti-collusion constraint requires that constraint to have actually been imposed.

**Proposal.** Keep current social conduct as a precise worked episode and the historical assurance as a labeled case unless systematic adjudication earns more prominence. A prospective commitment-incentive study is optional for this paper. It becomes necessary for a causal incentive claim, not merely because a bounded observational commitment case appears in the abstract. Public-state `fixture_engine` supports legality checks, not hidden decks or stochastic continuations. I did not verify an existing end-to-end runner for branching a saved game with reconstructed memory. Such a study needs a separate design and authorized implementation scope.

## Infrastructure is an independent contribution

**Verified assessment.** The system is substantially ahead of its July manuscript. The contribution is a usable experimental workflow with a clear boundary between the game and the agent, not merely a large log archive. Three aspects deserve main-text treatment.

1. The engine determines state, legal parameterized choices, and event transitions. Public observations and bounded memory define the agent's actual decision problem. They are distinct from an analyst's complete saved trajectory. The paper must explain the rules and observation design because they determine what economic behavior can occur.
2. Decisions, attempts, applied actions, events, and snapshots can be joined into a replayable account of economic consequences. The new jail-window analysis and the ambiguous trade response demonstrate why these distinctions are scientifically useful. `python/packages/engine/src/monopoly_engine/replay.py:29` rebuilds transitions from initial conditions and recorded actions. It does not reproduce live provider generation.
3. Durable execution, campaign freezes, source identities, physical-call records, inspection endpoints, and verified packages make longitudinal experiments practical for another researcher. The release should show one complete path from configuring a roster to reproducing a result and inspecting its decisive decisions. Detailed schemas and recovery internals belong in the appendix.

**Verified rules limitation.** The environment is a declared Monopoly variant. `docs/benchmark_audit_fixes.md:25` explicitly retains inherited developments, bank returns without immediate auction, surrender, jail-restricted management, and no competing auction for scarce buildings. Neither standard-rules fidelity nor rules-complete classic Monopoly is defensible wording.

**Verified analysis limitation.** The current `direct_property_purchase_count` is not a valid voluntary-acquisition quantity. `python/packages/telemetry/src/monopoly_telemetry/expanded_metrics.py:680` counts all `PROPERTY_PURCHASED`; `python/packages/engine/src/monopoly_engine/engine.py:3004` also emits that event for inherited deeds at price zero. The new reconstruction separates these routes. This issue matters because terminal holdings and inherited groups can otherwise be mistaken for opportunity creation. It is not a reason to redesign the engine or make accounting errors the paper's theme.

## Validation evidence and the remaining measurement gap

**Verified by inspection.** Existing tests specify meaningful expected behavior, beyond checking that the program starts.

| Claim | Existing concrete evidence | What it supports |
| --- | --- | --- |
| Financing and turn continuation implement declared rules | `python/packages/engine/tests/test_audit_regressions.py:18`, `:35`, and `:52` specify jail fine financing, one recorded movement, birthday financing, and return to the original owner | Declared rule semantics in these scenarios |
| Development respects physical and ownership constraints | Same file `:66`, `:79`, and `:89` tests house inventory, developed-group transfers, and mortgaged-sibling rent | Specific interacting rule guarantees |
| Recorded paths detect corruption | `python/packages/arena/tests/test_audit_regressions.py:111` deletes, modifies, duplicates, reorders, and appends actions, and malforms event data | Artifact rejection properties, not just self-consistent normal replay |
| Completion means a complete preserved run | Same file `:134` damages completion markers and inventory entries | Release-integrity checks |
| Recovery preserves completed response work | Same file `:75` and `:157` exercises append repair and saved-response reuse | Bounded recovery guarantees |
| Basic event metrics correspond to known records | `python/packages/telemetry/tests/test_expanded_metrics.py` specifies trades, auctions, cash, and mortgage examples | Existing metric accounting in those cases |

**Inherited validation, independently inspected record.** `docs/research_protocol/cloud_runner_validation.md:76` records two uncapped five-process mock batches with killed/recovered workers, all ten completing by bankruptcy with replay and package verification. This is end-to-end system evidence, not real-model strategic calibration. Each collection README and audit reports record all 20 October games passing state and artifact replay. I did not rerun those full replays in this round.

**Inherited fresh execution, log inspected.** Astra ran `scripts/verify.sh` in this round. Its log at `/tmp/monopolybench-paper-readiness-verify-20261027.log` ends with all checks passed and records 591 Python passes, two skips, and 36 frontend passes, plus contracts, lint, typing, and build. I inspected the log and relevant tests. I did not run a duplicate expensive suite.

**Material missing evidence.** The new trade-group, window, legal-eligibility, and post-acquisition consequence computations are not validated merely because the old tests pass. Before publishing them, freeze definitions and check hand-verifiable cases with independently specified expected ownership, cash, mortgages, legal choices, jail access, settlement direction, and ownership loss. Include actual corpus boundary cases, especially games 6 and 8. Agreement among researchers on aggregate counts is helpful but is not an independent reference value for every construct.

**Response to Fable's challenge.** I agree that the cohort contrasts cannot validate their own measurements. I do not require a new baseline tournament. `python/packages/arena/src/monopoly_arena/baselines.py:88` ends the turn or constructs an empty trade; its current policies cannot supply a meaningful traded-group denominator. A baseline run can validate pipeline operation or naturally acquired-group development. Use it if that is the stated claim. For traded-group timing, controlled state/menu scenarios and audited real episodes address the actual question more directly. Fable accepted this distinction and withdrew the tournament requirement.

We should distinguish verifying an exact descriptive quantity from showing that a score measures strategic competence. The latter needs stronger reference behavior or a defensible value model. This paper can contribute the former without pretending to have established the latter.

## Primary literature and the novelty test

**Verified primary-source comparisons.** These comparisons describe the versions fetched on 2026-10-27. Absence from a paper is not evidence that a capability or code release cannot exist elsewhere.

| Work | What already exists | What MonopolyBench must add |
| --- | --- | --- |
| [AgentMonopoly v2](https://arxiv.org/html/2610.29330v2), sections 4 and 5 | Proposal and acceptance profiles, public/private messages and actions, repeated seeds, rotated orders, opponent and persona comparisons. Its Table 3 totals 140 games. | Exact longitudinal ownership, financing, access, and deployment analysis. Do not claim that agent Monopoly, multiple behavioral measures, seed rotation, or words/actions comparison is new. |
| [FinBoardBench v1](https://arxiv.org/html/2605.27896v1), sections 3.2 and 4.2 | Dynamic liquidity and monetization analysis. Monopoly trade quality is judged separately for proposer and receiver. The explicit arbitrage chain in section 4.2 concerns Acquire. | Menu-grounded and bilateral Monopoly consequences over time, with transparent opportunity and timing denominators. Conversion as a broad idea is already established. |
| [Cattle Trade v1](https://arxiv.org/html/2605.14537), sections 3 and 4 | Economic multi-agent play, trace analysis, resource discipline, and code-agent calibration. | Persistent rent-producing capital, endogenous development access, financing, and bankruptcy feedback, accompanied by validated analyses. Activity versus efficiency is not novel by itself. |
| [NegotiationArena, ICML 2024](https://proceedings.mlr.press/v235/bianchi24a.html) | An environment plus substantive findings about multi-turn bargaining and behavioral tactics. | Consequences of bargaining embedded in a persistent competitive portfolio rather than isolated negotiation utility. |
| [AgentBoard](https://arxiv.org/abs/2401.13178) | Fine-grained progress analysis and an evaluation toolkit beyond final success. | Economic quantities that explain particular decision opportunities and subsequent interactions, with independently checkable semantics. A dashboard or process metric alone is insufficient novelty. |

**Inference.** A contribution claim about exact, opportunity-aware economic analysis plus a reusable verified research workflow is credible. No individual ingredient establishes blanket superiority. Inspectability is useful; avoiding an LLM judge does not automatically make a measurement a better measure of strategic value. Shared recorded dice streams strengthen this design, but I found no basis to claim they are exclusive to MonopolyBench. AgentMonopoly also repeats its seeds across rotations.

The current evidence can establish a more specific advance than another general assertion that models mishandle money. It can show how initiating and receiving negotiations, retaining cash, jail and management access, and available development choices produce different descriptions of the same trajectory. To earn a strong venue, the paper needs to execute that analysis and release it clearly, not merely promise that the logs make it possible.

## Manuscript and artifact readiness

**Verified.** `monopolybench_ieee_draft_v0_1.tex:30` has a July abstract centered on eight games, fallback provenance, and auditing. `monopolybench.tex` is an IEEE template. `paper/final_build_manifest.json` is dated 2026-07-28, and its referenced `output/pdf/MonopolyBench.pdf` and anonymous supplement ZIP are absent from this checkout. The architecture and historical house-lock PDFs/PNGs do exist. The manuscript bibliography lacks the two current closest Monopoly papers. Treat old polished assets as historical starting material, not proof that a current submission package is ready.

**Proposal for the manuscript argument.** Start with recipient bargaining and productive deployment as observed economic behavior, then show why the environment's rule, observation, execution, and evidence design allows these questions to be studied. Present validation against the claims actually made. Social conduct can provide one bounded example of the interaction between language and economic incentives; the paper need not promise a complete account of deception, commitments, and collusion.

| Planned output | Available sources | Remaining work before publication |
| --- | --- | --- |
| Cohort and seed-seat table | `sol_games.csv`, source configurations and freeze records | Preserve source/execution conditions; display five blocks instead of an overprecise leaderboard |
| Negotiation role and bilateral trade figure | `sol_player_games.csv`, `sol_trades.csv` | Use both roles, terms, and opportunity exposure; avoid quality labels from volume |
| Opportunity assembly/access/use figure | `sol_trade_groups.csv`, exact decision IDs and menus | Validate new quantities; retain elapsed delay and endogenous access, not only conditional conversion |
| Traced economic episode | Game 14 or 15 natural development; game 16 dark-blue financing; qualified game 1 recipient negotiation | Pick a clear main example and a counterexample; disclose material provenance |
| Architecture and workflow figure | Existing architecture asset, current code, cloud/replay record | Redraw around actual current workflow and scientific uses; avoid historical inaccuracies |
| Focused validation table | Rule scenarios, adversarial artifact tests, cloud records, new metric checks | State each property and scope; distinguish old recorded validation from fresh execution |
| Reproducible review package | Self-contained current game packages and new derived tables | Freeze analysis scripts, definitions, source hashes and exact figure inputs; regenerate manuscript assets |

## What remains, and what can wait

**Necessary while drafting.** Select a finite set of claims; freeze and validate their derived analyses; resolve remaining event-boundary disagreements; trace the main examples and counterexamples; rewrite the manuscript around the current corpus and declared rules; refresh related work; and produce a reproducible release and rendered manuscript. The new deployment table is an analysis result under development, rather than a finished headline to copy uncritically into the abstract.

**Necessary only for stronger claims.** General model rankings require evidence across enough independent variation for the desired precision and opponent scope. Causal effects of communication, promises, or jail strategy require a defined counterfactual design. Population claims about deception or collusion need systematic coding, adjudication, and coverage. A validated economic-competence score needs an external criterion or known reference behaviors. No fixed new game count follows from these statements.

**Desirable future work.** Broader rosters and relative orders, repeated provider realizations, stronger economic baselines, and prospective commitment continuations could strengthen or extend the research. They are not prerequisites to explaining the present environment and bounded observations well. Choose them when a concrete unresolved claim justifies the cost and implementation work.

## Independent verdict for Astra

Start drafting now. The strongest integrated paper pairs a useful and well-tested experimental system with systematic, opportunity-aware analysis of how agents assemble assets, obtain access and financing, and use them. The economic evidence is already substantive, with recipient-side participation, bilateral trade effects under cash pressure, and seed-dependent trajectories. The new legal-menu-conditioned deployment analysis is promising and reproducible but still needs measurement validation. Social cases deserve precise descriptions and proportionate prominence.

I challenged the earlier conversion headline, causal luck/skill labels, exclusive novelty claims, and the idea that a baseline tournament is an automatic prerequisite. I accepted Astra's objection that conditioning on first management access removes part of timing strategy, and Opus's objection to an unqualified game 1 story. Fable reproduced the core counts and accepted the cash-boundary and baseline-scope corrections. The remaining disagreement is about how ambitious the social claim should be. My position is that an observational case does not mechanically require an intervention, while a causal commitment claim does.

The material remaining work is claim selection, independently checked derived analysis, precise social interpretation, and rebuilding the manuscript/release. It is not an unspecified demand for more games or another broad infrastructure rewrite.
