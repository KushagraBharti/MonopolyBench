# Phase 1 foundation, Sol

2026-10-28. This is a downstream research contribution. The engine, prompts, policies, canonical games, and manuscripts remain unchanged. I read AGENTS.md, all four readiness memos, both repository reproduction scripts, the available `/tmp/opus_readiness/` scripts, the retained rules and response policy, relevant engine/arena code, and the official Vending-Bench paper and pages. No games, provider calls, deployment, commits, or additional agents were started.

## Research argument

Proposed central question: **How do LLM agents sustain goal-directed capability during long competitive interactions, and how do their communications and actions relate to commitments, other participants' interests, and explicit instructions?** A second contribution asks what an inspectable, controlled environment must preserve to make those questions testable and to support future agent improvement.

Capability includes planning, learning about opponents within a game, negotiation, resource use, adaptation, and sustained execution. Economic measurements provide consequences for these behaviors. Social conduct includes cooperation, coordination, deception, manipulation, betrayal, alliances, disadvantage to opponents, and kingmaking, with definitions, opportunity denominators, and counterexamples. Explicit instruction compliance is a separate construct. A competitive action can harm an opponent while pursuing the assigned objective. The current system prompt permits public deception. Neither permission nor game success settles a broader alignment judgment. A private explanation is a recorded self-report, not direct access to latent computation or a test that the report is honest.

The earlier recommendation in my own readiness memo to keep social evidence to one bounded example was premature for the user's updated ambition. Phase 1 does not establish how common these behaviors are. Phase 2 should examine all 20 games across all four visibility levels, including every proposal, counter, rejection, accepted transaction, non-trade route, financial consequence, unsuccessful attempt, and relevant counterexample. No lexical search or top-case selection can substitute for that coverage. Capability growth across model releases, effects of training, and causal effects of a social strategy need separately defined comparisons. They are not established by the current cohort.

Vending-Bench motivates measuring coherence and resource acquisition over long horizons. Its original paper also connects those capabilities to safety evaluation. Arena adds individually scored competitors who can communicate and trade. These are direct precedents for the combined capability and alignment ambition, not reasons to narrow this paper to finance. See the [original paper](https://arxiv.org/html/2502.15840v1), [Vending-Bench 2](https://andonlabs.com/evals/vending-bench-2), and [Arena](https://andonlabs.com/evals/vending-bench-arena). The phase-3 comparison should retain AgentMonopoly, FinBoardBench, Cattle Trade, the promise papers, SOTOPIA, Concordia, The Agent Company, AgentBench, WebArena, OSWorld, tau-bench, AgentDojo, MLE-bench, and METR Time Horizon. I did not conduct a full new review of that set in phase 1. Novelty must name evidenced dimensions. AgentMonopoly's Table 3 totals 140, not 160; the corrected readiness memo supersedes Fable's arithmetic.

## Implemented outputs and verification

`economics.py` independently reconstructs deed routes, ownership episodes, bilateral trade settlement, cash, loss and reacquisition, and recorded management opportunities. `reproduce.py` reads the two explicit October indexes and writes all outputs here. It does not import or execute the readiness reducers. The new tests independently specify expected outcomes.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python -m pytest -q -p no:cacheprovider docs/research_raw/paper_phase1_2026-10-28/sol
python/.venv/bin/ruff check --no-cache docs/research_raw/paper_phase1_2026-10-28/sol
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase1_2026-10-28/sol/reproduce.py
```

The focused suite passes **31 tests**. Lint passes. `verification.log` and `reproduction.log` retain execution output. These checks cover direct purchase versus auction and creditor inheritance; reversed counteroffer authorship; interest-inclusive settlement boundaries; group loss, reacquisition and bank return; group-specific legal menus; access after jail; financing later within a window; missing menus; loss before access; terminal and incomplete-record censoring; provider-text versus token/opaque fields; response disagreement units; and synthetic private-note provenance. Five real-record cases cover both jail windows, the game-1 mortgage-interest settlement, and both no-trade winners.

The corpus run verifies contiguous event sequences, ordered event/action/start/resolved decision identities, exact resolved/applied action equality for all 6,989 decisions, and terminal ownership and cash in all 20 games. All 30 within-block raw dice-prefix comparisons pass. These establish the stated accounting and finite window semantics. They do not prove economic optimality, establish social labels, or replace replay verification. The full repository suite and full engine replay were not rerun because no production code changed. Existing replay reports remain inherited evidence, explicitly distinct from this execution.

The package includes `manifest.json` with source paths and SHA-256 hashes; `results.json`; 1,151 deed acquisitions in `deed_acquisitions.jsonl`; 209 group episodes in `group_episodes.jsonl`; 113 bilateral settlements in `trade_settlements.jsonl`; 1,446 decision-linked negotiation events in `negotiation_event_inventory.jsonl`; 6,989 decision-origin records; 8,679 attempt records; and separately flagged response disagreements. All semantic-review statuses remain pending.

## Independent cohort and methods check

The 20 primary games contain 50,918 events, 6,989 applied decisions, 526 initial proposals, 394 counters, 413 rejections, and 113 accepted trades. There are five seeds and four cyclic rotations per seed. Every model occupies each absolute seat once per block, while cyclic rotation preserves relative opponent order. First builders win 17 games. Games 14 and 15 have winning participants with no completed-trade participation, and both complete orange through direct purchases at turn 47.

All configs agree on `audit_corrected_v2`, `finance_before_bankruptcy_v2`, `fail_without_action_v2`, 20 trade exchanges, 200 auction actions, and no turn cap. All games end by bankruptcy. The roster is Opus 5.5, GPT-6.1 Sol, Gemini 4 Argon, and Grok 4.7 at nominal medium effort, with recorded provider pins. Medium is provider-native, not equal compute. Opus uses the declared refusal-recovery treatment; Grok uses required tool choice. Two source hashes and two executable fingerprints remain visible. I checked the source diff: cloud execution/control and frontend changes do not change engine or prompt source. The first source version is confined to the first seed block, so version effects cannot be estimated independently.

Actual initial prompt messages have one common system-text SHA-256 across all 6,989 starts. This does not mean all attempts share that prompt: action-only refusal recovery changes the response requirement. The observation contains each player's public cash, position, jail and bankruptcy state, holdings and development; bank inventory and unowned properties; a bounded public timeline; the acting player's recent private notes; and decision-specific options and histories. The observed maxima are 20 public timeline entries and 10 private notes. It is constructed public information, not the engine's full hidden state or an unbounded transcript. The method name `build_full_state` must not be used to claim omniscient observations.

Keep ordinary Monopoly explanations short: obtain property groups, develop them to collect rent, negotiate transfers, finance obligations, and avoid bankruptcy. Declare retained variants separately: creditor inheritance keeps development without mortgage-transfer interest; bank returns do not trigger immediate auctions; voluntary bankruptcy is surrender; management is generally restricted to the active player's post-turn phase and by jail; scarce buildings have no competing-purchase auction. Voluntary trades of mortgaged deeds do charge interest. Those two interest statements concern different routes.

Raw dice pairs match across rotations, but their uses can differ. At draw index 37 in seed 2573692901, games 9 and 10 both draw 5 and 1; one record is ordinary movement and the other is `CARD_UTILITY_RENT`. Shared draw streams therefore do not equalize landings, exposure, decision opportunities, or all stochastic roles. This strengthens the case for tracing trajectories and constrains luck-versus-skill language. The inferential units remain games nested in five blocks, not thousands of independent decisions or group episodes.

## Economic reconstruction results and definitions

The 944 `PROPERTY_PURCHASED` records comprise **475 direct purchases, 72 auction purchases, and 397 creditor inheritances**. Another 207 deeds move through accepted trades. Previous ownership and auction context identify the route; price zero alone is insufficient. A new unowned zero-price purchase fails explicitly as unknown provenance. This avoids the old reducer's direct-purchase ambiguity.

The 113 trades complete a color group for neither side in 60 cases, one side in 43, and both sides in 10. These produce 63 trade-completed group episodes. Across every acquisition route there are 209 group episodes: 16 completed by a direct purchase, 9 by auction, 63 by trade, and 121 by inheritance. These labels identify the final acquisition event, not how every constituent deed was obtained. Each episode retains constituent last-acquisition routes, and the complete deed history is available. Inheritance is often a consequence of an already strong position. Counting it as deliberate opportunity assembly would confuse cause and consequence.

| Recorded participant | Trade groups | Built in first actual management turn | Entry eligible | Built among entry eligible | Eligible at some point in that turn |
| --- | ---: | ---: | ---: | ---: | ---: |
| Sol | 17 | 16 | 15 | 14 | 17 |
| Gemini | 18 | 17 | 13 | 13 | 18 |
| Opus | 15 | 7 | 7 | 5 | 10 |
| Grok | 13 | 3 | 7 | 2 | 9 |
| Total | 63 | 43 | 42 | 34 | 54 |

These reproduce the reconciled numbers independently. All 63 trade episodes have an observed management window. The code also handles missing access and incomplete windows without silently treating them as declined opportunities. It stops follow-up at ownership loss. Reacquisition creates a new episode. A terminal group is observed until game end; finite follow-up is not a claim about future building or rent.

Entry eligibility requires both the saved build action and a group-specific buildable key. It means at least one purchase was legal, not that a full development plan was legal, affordable or optimal. Financing or unmortgaging can create eligibility later within the same turn. A cash-based affordability proxy cannot replace the recorded menu. Game 1 event 1989 illustrates the transaction boundary: Opus has $68 and Grok $347 before acceptance; they have $168 and $229 after settlement, including Grok's $18 mortgage-transfer interest.

Access and delay remain outcomes. Game 6 Opus acquires pink at turn 74 and manages/builds at 85 after two `roll_for_doubles` choices. Game 8 Gemini acquires dark blue at 77 and manages/builds at 87 after `roll_for_doubles` then `pay_jail_fine`. These explain why first actual management gives 43 deployments while a next-own-turn definition gives 41. Neither is universally preferable. Report conditional use with elapsed delay and the actual access choices. Non-inherited group acquisition is absent in 1 Sol, 2 Gemini, 2 Opus and 5 Grok player-games. Conditional deployment must not erase that denominator.

## Four visibility levels and corrections

1. **Applied actions and consequences.** All 6,989 action records join exactly to starts, resolved decisions and events. Ownership, cash and settlement comparisons use engine events. The negotiation inventory includes every one of the 1,446 proposal/counter/accept/reject events and links each through emitted event IDs, without labeling its strategic quality.
2. **Public messages.** There are 6,989 public-message events, of which 6,882 contain non-whitespace text. Event presence is not evidence that a substantive utterance occurred. Preserve silent messages and distinguish deterministic fallback from selected model output.
3. **Private notes.** The 5,445 private-note events include **66 deterministic fallback notes**, leaving 5,379 nonfallback final-action notes. Opus's 152 events comprise only **91 nonfallback notes plus 61 synthetic `fallback` notes**. Sol has 1,957 nonfallback plus 4 fallback notes; Gemini 1,668 plus 1; Grok 1,663 plus 0. The prior 152 count was correct as an event count but cannot be called 152 model rationales. `decision_inventory.jsonl` records origin. Missing notes remain missing.
4. **Provider-returned reasoning fields.** Readable provider-labeled text exists in at least one attempt for 4,834 decisions; opaque data exists for 4,016 decisions, with overlap. Selected valid attempts contain such text for 4,764 decisions; 70 decisions have text only in unselected attempts. Provider summaries retain their labels, encrypted fields remain opaque, and reasoning-token counts are usage metadata. All attempts, including refused or invalid ones, must remain distinct from the final applied action.

The independent availability counts agree with Astra's inventory. Of 8,679 physical response JSON files, 8,676 equal the ledger's raw response. The three differences are ledger `raw_response: null` with physical `invalid_json` error envelopes in game 2 decision 61, game 3 decision 183, and game 7 decision 153. These preserve error metadata, not missing readable reasoning. They are enumerated in `results.json`.

Two proportionate interface corrections are now explicit. There are **139 selected-valid-response action-name disagreements** for Grok: 138 parseable content objects and one malformed content record with a recoverable name. The old figure of 26 identifies equal stripped public messages, not identical arguments. Twenty-five also have equal stripped private notes; **15 have identical complete arguments**. All-attempt disagreements number 148 because nine invalid initial attempts are additional. Game 1 decision 112 remains an exact-argument reject/accept inconsistency. Applied tools remain authoritative; no provider cause, intent, deception label, or counterfactual winner follows.

Opus has 1,605 refused attempts affecting 1,605 decisions. Of its 1,696 decisions, 1,604 have the standard-to-action-only chain, 91 are standard-only, and one has an ordinary standard corrective retry that refuses, game 2 decision 129. Thus 1,604 recovery chains and 1,605 refusals are compatible. This reconciles units rather than treating the difference as disagreement about behavior.

## Sandbox and improvement claims

Existing code provides an engine with decision and action stepping, explicit legal menus, deterministic seeded transition/replay, simple reference policies, versioned fixtures and microbench legality checks, frozen campaign settings, recorded response attempts, and state/event inspection. These support repeatable evaluation, failure analysis, dataset construction, and prospective controlled interventions. The simulated property/cash ledger bounds in-game consequences, and model actions are restricted to game tools.

This is an inspectable game sandbox, not evidence of secure execution of arbitrary agent code. Provider text leaves the process through OpenRouter, and no broad network/OS security claim is established. I found no Gym/PettingZoo adapter, training loop, policy optimization, reward-learning experiment, or demonstrated training improvement in the inspected source. Snapshot restoration for a single public legality check does not reconstruct hidden RNG and deck state for arbitrary continuations. Micro campaign aggregation is not continuous training. Replay preserves recorded actions; it does not rerun stochastic provider generations. Future RL and improvement work can build on these affordances, but requires its own state/reset API, action encoding, reward definitions, train/evaluation split, and experiments.

## Open issues and peer objections

- Freeze route labels as final-acquisition-event labels and retain histories. Set completion, rent, cash, survival and social conduct must remain distinct outcomes; completion is not a trade-value oracle.
- The opportunity analysis is tested accounting, not a validated scalar of intelligence. Do not turn the 43/63 result, first-builder association or block patterns into a causal claim.
- The 26-identical-arguments and 152-model-private-thought statements need correction wherever inherited. The latter directly affects phase-2 evidence attribution, even though interface handling remains a small part of the paper.
- No phase-1 search establishes absence of collusion, betrayal, manipulation or deception. Economic and social extraction must preserve chronological game context and include counterexamples across all 20 games. Historical runs can supply labeled references, not pooled current-roster prevalence.
- Comparison claims need primary-source checks of the exact claimed dimension. Logging, rotations, process measures, or Monopoly alone do not establish novelty. No blanket additional games are required by the present descriptive contribution.

I sent findings and objections directly to Astra and, after authentication was restored, to Opus and Fable during their running turns. The latest Astra steering messages could not be delivered because that thread was idle; no new turn was triggered. This memo and its generated records retain those updates. Peer replies may further refine the definitions, but no semantic-review completion is claimed here.
