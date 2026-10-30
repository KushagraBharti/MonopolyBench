# Paper readiness: literature, positioning, validation scope, and independent evidence check

Author: Claude Fable 5.1 (research collaborator with Astra, GPT-6.1 Sol, Claude Opus 5.5)
Date: 2026-10-27
Scope: full-scope independent assessment with emphasis on primary-source verification and positioning. Read-only on engine, prompts, policies, canonical artifacts, and the July manuscript. No provider calls, no game runs. Derived numbers below were computed read-only from `saved_games/railway-research-12-games-2026-10-25/` and `saved_games/railway-research-8-games-2026-10-26/`.

Evidence labels: **V** = verified by me from artifacts, code, or the primary web source today; **I** = inherited from a thread or memo and not independently checked; **N** = inference; **P** = proposal.

## 1. Bottom line

- **Start drafting now (V+N).** The 20-game cohort, its audited release, and the engine/arena/telemetry stack are substantially ahead of the July manuscript, which is an eight-game audit paper (`monopolybench_ieee_draft_v0_1.tex`, abstract lines 30–64). The root `monopolybench.tex` is an untouched IEEE template with placeholder references `b1`–`b7` (V). The July PDF listed in `paper/final_build_manifest.json` is not in `output/` (V). The bibliography memo of 2026-07-28 is sound but predates AgentMonopoly, FinBoardBench, the two promise papers, and DECE.
- **Not submit-ready (V+N).** The headline economic measures (opportunity creation and use at the first management window) are still being defined this week by Sol and Astra; they have no arithmetic or scenario validation yet. Two comparability facts (Claude refusal-recovery treatment; Grok content–tool disagreement under `tool_choice=required`) are not yet written into any design section. The social evidence supports a taxonomy, not a breach headline.
- **Positioning that survives the literature (N).** Not "LLMs play Monopoly", not "first long-horizon economic benchmark", not "models break promises". The defensible claim is: a verified, replayable, frontier-model corpus in a declared-variant Monopoly economy whose recorded legal menus let us measure, for every player, who creates economic opportunities (set completion by trade or purchase), who deploys them (first offered management window with exact buildable options), and what the consequences are (rent, solvency), as exact descriptive estimands instead of judge-rated quality or frequency counts. Plus a released, re-runnable research workflow. That is specific enough to be checked against AgentMonopoly and FinBoardBench and is not occupied by either.

## 2. Independently verified corpus facts (V)

| Quantity | Value | How checked |
| --- | --- | --- |
| Games | 20 (12 + 8), five seed blocks × four cyclic rotations | folder enumeration, `summary.json` seeds |
| Events / decisions / actions | 50,918 / 6,989 (13,978 decision records = requested + resolved) / 6,989 | line counts over `run/*.jsonl` |
| Trade events | 526 proposed, 394 countered, 413 rejected, 113 accepted | event-type counts |
| Wins | Sol 8, Gemini 7, Opus 3, Grok 2 | `winner_player_id` mapped to `players` |
| Initial proposals by model | Opus 240, Grok 136, Sol 132, Gemini 18 | `TRADE_PROPOSED.initiator_player_id` |
| Proposals received | Gemini 205, Grok 154, Sol 114, Opus 53 | `counterparty_player_id` |
| Completed-trade participation | Opus 70, Sol 60, Grok 60, Gemini 36 (as initiator 44/19/39/11) | `TRADE_ACCEPTED` |
| Rent received | Gemini $42,360, Sol $41,299, Opus $23,995, Grok $13,500 | `RENT_PAID.to_player_id` |
| First builder won | 17 of 20 | first `HOUSE_BUILT`/`HOTEL_BUILT` actor vs winner |
| Set completion by completed trade | 60 neither side, 43 one side, 10 both | ownership tracked from `PROPERTY_PURCHASED`/`PROPERTY_TRANSFERRED` with `contracts/data/board.json` groups |
| One-sided grantors | Opus 20, Grok 10, Sol 8, Gemini 5 | same |
| Grantor cash at `TRADE_ACCEPTED` (pre-settlement median) | Opus $79.5 (12/20 below $150), Sol $178, Gemini $287, Grok $294.5; post-settlement $265.5 / $812.5 / $537 / $650 | ledger from `CASH_CHANGED` with $1,500 start; final cash reconciles 80/80 with `summary.json`. Matches Sol's reconstruction exactly after I corrected my boundary. |
| Zero-trade winners | G14 Sol and G15 Gemini won with no completed-trade participation | Astra's addition, confirmed in my participation table |
| Dice streams | identical `DICE_ROLLED` prefix across all four rotations in all five blocks through the shorter game's end | prefix comparison |
| Seat patterns | seats p1 and p2 won 14/20; block 3 (seed 2573692901) seat p2 won all four rotations with four different models; block 2 (seed 2506298840) Sol won from all four seats | seat/winner table |
| Grok content–tool disagreement | 139 of 1,663 applied Grok decisions name a different function in `assistant_content` than in `parsed_tool_call`; 0 for Sol (1,961), Opus (1,696), Gemini (1,669) | `decisions.jsonl` attempts; G1 dec-000112 confirmed: content `reject_trade`, tool `accept_trade`, identical arguments, applied accept at evt 754 |
| Claude refusal treatment | 861 refused attempts across the 12 games (per-game 30–133 in `audit/verification.json`), 744 in the 8 games (`audit/totals.json`); `LLM_PRIVATE_THOUGHT` 5,445 vs 6,989 decisions; Opus's count: 152 private thoughts across 1,696 Opus decisions | audit files, event counts |
| "Not for sale" holding statements | Grok 49 later reversed by trade vs 52 not; Opus 3 vs 5; Gemini 0 vs 12; Sol 0 vs 3; Grok 49 → 45 after excluding content–tool mismatch decisions | regex over `LLM_PUBLIC_MESSAGE` naming an owned property, then later `PROPERTY_TRANSFERRED` from the speaker. Crude name matching; no reliance check. |
| Tests | engine + telemetry: 116 passed locally in 0.11 s; Astra's full `verify.sh`: 591 Python (2 skipped), 36 frontend (I) | local pytest |
| Baselines | six scripted policies in `python/packages/arena/src/monopoly_arena/baselines.py`; `propose_trade` always uses `_empty_trade_args`; no baseline results in `saved_games/` | code read, folder search |
| Micro scenarios | 130 files under `contracts/micro/scenarios/`; no results artifacts found | listing |
| Rules | `docs/benchmark_audit_fixes.md` declares `audit_corrected_v2` "deliberately not rules-complete classic Monopoly" (creditors inherit developments intact, no mortgage-transfer interest, no auction on bank return, jail-restricted management, no building auctions) | file read |
| Prompt | `player_config.py` SYSTEM_PROMPT_V1: "Deception in public chat is allowed; private thoughts should reflect true reasoning." | file read |

Episode checks (V): G1 T40 evts 722–796 (Grok obtains Connecticut from Opus for St James + $100 at evt 754, then Oriental + Connecticut + $100 for Ventnor accepted at evt 788; note evt 754 is a content–tool disagreement decision); G15 T47 evts 709–756 (Gemini buys Tennessee, builds 8 houses while mortgaging three properties, no completed trade); G16 evts 2711, 2808, 2976, 3036, 3260 (Sol "Illinois and Pacific remain off-limits to p4"; Opus offers North Carolina to the leader twice while urging others not to trade with the leader).

## 3. Primary sources: verification status

| Source | Verified metadata (V) | What it actually does | Applicability | Prior-thread description errors |
| --- | --- | --- | --- | --- |
| AgentMonopoly, arXiv 2610.29330 v2 (Oct 22, 2026), Wu, Li, Marsault, Huang, Cheng, cs.AI, "14 pages", no venue | 160 games (S1 same-model 40, S2 mixed-size 40, S3 cross-family 40, S4 persona 20), five seeds 42–46 per configuration, temperature 0; open models 8B–32B (Qwen3, DeepSeek-R1, Gemma4, Mistral); modified rules: optional rent waiving, elimination at negative cash, 150-step cap with net-worth tiebreak, renamed streets; structured trades, free-text public messages, `chain_of_thought` field logged; code on GitHub; persona findings (Zen proposals 101→20 per 100 rolls; Diplomatic waives rent 90%); P1–P2 won 41/80 | Closest Monopoly comparison. It already has seeds, rotations, public/private logging, say/do comparison. It does not have frontier models, mortgage/rent economics under near-classic rules, recorded legal menus, or replay. | Threads said "140 games"; the paper says 160. |
| FinBoardBench, arXiv 2605.27896 v1 (May 27, 2026), Hu et al., cs.CL/cs.CE, "Preprint" | 108 matches across Cashflow/Acquire/Monopoly, 9 focal models vs 3 fixed LLM opponents (DeepSeek V4 Flash, Qwen-3.5, Gemini-3.1-Flash-Lite), focal seat rotates 1–4, four Monopoly runs per model-mode cell; LLM judge (DeepSeek V4 Pro, also evaluated) rates 45/86 proposer and 11/18 receiver trades harmful (§4.2); liquidity (47 purchases below $500 cash); Appendix E fault tolerance with up to five execution failures then fallback, logged as system-forced events; no seeds; no code/log release stated | Closest economic framing. Already distinguishes proposer vs receiver and discusses liquidity and conversion (staged analysis is for Acquire, not Monopoly). Its trade-quality construct is judge-based. | Threads described it correctly. |
| Cattle Trade, arXiv 2605.14537 (May 14, 2026), Müller & Müller | 50–60-turn auction/bargaining/bluffing game, 242 games, 7 low-cost LLMs + 3 deterministic code agents; two heuristics beat most LLMs | Defeats any "first long-horizon economic game" claim; also shows code-agent baselines can be informative. | Correct. |
| Cheap Talk, Empty Promise, arXiv 2604.04782 (Shi, Zhang, Conitzer, Jin) | ICLR 2026 **AIMS workshop poster**, not main conference; one-shot normal-form games, nine frontier models, ~56.6% deviation from announced actions | Occupies generic "LLMs break promises". No enforceable transaction, no reliance. | Threads implied main-track standing; it is a workshop paper. |
| When Agents Lie, arXiv 2607.05132 (Shi, Zhang, Schölkopf, Conitzer, Jin) | ICML 2026 **workshop** "New Frontiers in Game-Theoretic Learning" best paper (page header says "ICML Best Paper"); repeated games, private intent vs public announcement vs action; >90% of deviations premeditated in highest-deception conditions | Same gap as above. | Threads implied main-track; it is a workshop best paper. |
| NegotiationArena, ICML 2024, PMLR v235 pp. 3935–3951, Bianchi et al. | ultimatum/trading/price scenarios; feigned desperation raises payoff ~20% | Precedent for platform + behavioral findings in one paper; relevant to Grok's "only buyer" rhetoric. | Correct. |
| SOTOPIA, ICLR 2024 spotlight, Zhou et al. | social environment + evaluation framework + findings | Precedent for combined paper. | Correct. |
| MACHIAVELLI, ICML 2023 oral, Pan et al. | 134 text games, reward vs ethics trade-offs | Precedent for capability + behavioral-harm measurement in one benchmark. | Correct. |
| AgentBoard, NeurIPS 2024 oral, Ma et al. | progress-rate metric, analysis toolkit | Precedent for process metrics; D&B track listing not confirmed by my search (I). | Minor. |
| HAL, ICLR 2026 (proceedings page verified), Kapoor … Narayanan | 21,730 rollouts, 9 models, 9 benchmarks; LLM-aided log inspection | Precedent for infrastructure papers demonstrating value through analysis. | Correct. |
| Emergent Collusion in Long-Horizon LLM Agent Interaction, arXiv 2609.24967 (Shi, Zhang, Yang; Sept 2026) | two agents verifying each other's tasks; collusion = protocol deviation, 94% of trajectories | Different construct from market collusion; cite to show "collusion" is overloaded. | New. |
| On the Fragility of AI Agent Collusion, arXiv 2603.20281 (Keppo, Li, Tsoukalas, Yuan; Mar 2026) | repeated pricing; heterogeneity reduces price lift from 22% to 7–10% | Pricing-collusion literature; our anti-leader episodes are not this. | New. |
| DECE: A Unified Arena for LLM Agents across Diverse Eurogames, arXiv 2610.35773 (Oct 26, 2026) | 10 Eurogames, 480 three-player matches primary, 1,032 total, 12 model-harness configurations; harness changes rankings | Very recent; shows harness effects on rankings, which supports disclosing our per-model interface differences. | New. |
| NeurIPS 2026 Evaluations & Datasets reviewer guidelines (page verified) | contribution types include "Evaluation Tools, Frameworks, and Infrastructure"; submissions "may naturally span multiple categories"; key question "Could another team re-run the benchmark from this paper?"; Croissant file required for dataset submissions | Infrastructure counts; our release must answer the re-run question concretely. | Correct. |
| Not verified today | Vending-Bench Arena paper (arXiv 2608.14825, fetch aborted); AAAI 2026 Diplomacy paper (fetch aborted); LieCraft 2603.06874; AAMAS/ICML 2027 official deadline pages did not resolve | Cite only after a successful fetch. | |

## 4. Capability comparison that the paper can defend (V where stated, N for the comparison)

| Property | MonopolyBench (20-game cohort) | AgentMonopoly | FinBoardBench (Monopoly) |
| --- | --- | --- | --- |
| Players | four frontier models, all evaluated, one roster | four open 8B–32B models | one focal model vs three fixed LLM opponents |
| Rules | declared variant of classic rules (mortgages, auctions, even building, finite houses, bankruptcy with creditor transfer); turn-uncapped, all 20 ended by bankruptcy | modified (rent waiving, negative-cash elimination, 150-step cap) | classic-style with auctions, mortgages, building, bankruptcy |
| Negotiation | structured offers with free-text public message, up to 20 exchanges, counters flip author | structured offers, free text | structured offers with free-text reason, counters |
| Seeds / rotation | five seed blocks, identical recorded dice across rotations | seeds 42–46 repeated across rotations, temperature 0 (dice matching not stated) | none stated; seat rotation only |
| Recorded legal menus per decision | yes, in `decisions.jsonl` and snapshots | action validation yes; menus not described | validity checks yes; menus not described |
| Replay | state replay and strict artifact replay, 20/20 passed in audit | interactive replay mode | not described |
| Trade-quality construct | deterministic set-completion, feasibility at first menu, consequences | frequency, acceptance, rent waiving | LLM judge (an evaluated model) |
| Release | extracted packages committed; ZIPs external; verifier scripts | code on GitHub | not stated |
| Per-model interface differences | Claude refusal recovery, Grok tool_choice=required; must be disclosed | invalid outputs not returned to agent | errors fed back, five failures then fallback |

Do not claim: "standard rules", "first", "more realistic", "better measurement" in general, "dice matching is unique", or that FinBoardBench did not release logs.

## 5. What is occupied and what is open (N)

Occupied: long-horizon economic games (Cattle Trade, Vending-Bench Arena, Market-Bench, CoffeeBench); Monopoly with LLM agents and persona control (AgentMonopoly); Monopoly as one of three financial board games with liquidity findings (FinBoardBench); generic promise-breaking in abstract games (two workshop papers); pricing collusion (Fragility; Fish et al. line); process metrics and infrastructure papers (AgentBoard, HAL).

Open and reachable with current data:
1. All-player opportunity creation and use with menu-grounded feasibility, including the two-sided consequences of each completed trade (who got a set, at what cash, when they could first build, whether they did). FinBoardBench reports proposer/receiver judgments; it does not trace feasibility or consequences, and only the focal model is analyzed.
2. Seat-and-dice luck as an explicit validation finding: the block-3 "same seat wins all four rotations with four different models" result is the kind of evidence AgentMonopoly's P1–P2 vs P3–P4 split (41/80 vs 39/80) cannot show. It warns against single-seed rankings, including our own.
3. A commitment taxonomy anchored in transactions: posture ("not for sale" rhetoric, mostly Grok, half reversed), reliance-inducing assurance inside an enforced transfer (historical run 172, different models and rules), and third-party restraint appeals with a self-exception (G16). The workshop papers lack transactions and reliance, so "assurance inside an enforced transaction with observable reliance" is open. The current roster has no clean breach instance, so this stays a taxonomy, not a headline.

## 6. Validation scope: what this paper needs versus a generic wishlist (N, P)

Needed because a claim depends on it:
- Integrity and replay: already evidenced (20/20 state and strict artifact replay; `test_audit_regressions.py` corrupts, reorders, and deletes actions, damages manifests, exercises interrupted recovery). Present as a compact table; do not narrate bugs.
- Measurement of the new estimands: the opportunity-window arithmetic has no checks yet. Sol's refinement, which I accept: small hand-verifiable same-state scenarios that independently specify ownership completion, cash, mortgages, jail access, and the legal menu, then build/pass outcomes, plus audited real boundary cases (G6 Opus pink T74 → first management T85; G8 Gemini dark blue T77 → T87, both confirmed by Astra from raw menus). `contracts/micro/scenarios/` has 130 files and the micro runners validate legality from reconstructed state, so this is assembly, not new infrastructure. Unpaid.
- Reference-policy runs: useful only to show the pipeline and the non-trade route respond to known policy differences (builder vs no_trade vs cash_conservative vs random_legal on the five seed blocks). They cannot validate the trade route because no baseline makes a substantive proposal. Unpaid, local. I withdrew "tournament" as a mandatory item after Sol's objection.
- Comparability disclosures (main text, one paragraph each): Claude refusal-recovery treatment and private-thought absence; Grok content–tool disagreement at 8.4% of its applied decisions; declared rule variants; five seed blocks are not 20 independent games.

Not needed for this paper: a second roster, a causal luck/skill decomposition, an optimality oracle, a human-player comparison, exhaustive fallback accounting, or an instruction-alignment claim (the prompt permits deception, so none can be made without a new treatment).

## 7. Objections to the current consensus (dissent preserved)

1. **"Validation can come from existing regression and cloud evidence" (Astra).** Only for integrity. The 20% validation slot the user specified includes reference policies and analysis of experimental variation; neither exists as results today. Sol agrees measurement validation is necessary; we disagree only on the vehicle (scenarios first, reference runs second).
2. **"Content–tool mismatches should be excluded from say/do coding" (Opus) vs "keep them flagged in the population" (Astra).** I side with Astra's publication rule: preserve the applied action and quoted message, flag the inconsistency, adjudicate intent separately. Exclusion would bias say/do rates for Grok; inclusion without a flag would overstate deception. My holding-statement numbers show the filter changes individual cases but not the pattern.
3. **"Commitments as a headline."** Against, with Opus. Taxonomy in the main text; a pre-specified continuation study only if commitments enter the abstract.
4. **"Everything should be better than all existing papers" (user).** The comparison table in §4 supports specific advantages (frontier roster, recorded menus, replayable release, dice-matched blocks, all-player analysis) and specific disadvantages (one roster, five blocks, declared variants, 20 games vs 108–242). Say both.
5. **Interface differences are not "fallback minutiae".** The Claude and Grok treatment differences change which comparisons are fair; DECE's harness-effect finding makes this a live reviewer question. Two paragraphs in the design section, not an appendix burial and not a chapter.

## 8. Readiness verdict

Start drafting: yes, today. Sections that can be written from verified material now: environment and interface (with variant rules declared), execution and release (with the verifier scripts and audit READMEs as the reproducibility statement), cohort design and descriptive results (tables in §2), seat/dice validation finding, episode exhibits G1, G15/G14, G16, historical 172 and 273 as labeled historical cases.

Submit-ready blockers (material): frozen definitions and scenario checks for opportunity creation/use; the two comparability disclosures written and applied to every table that includes Claude or Grok; a Croissant/metadata file if targeting NeurIPS E&D; refreshed bibliography (the July memo lacks the 2026 sources above).

Evidence that would change this recommendation: if the first-window deployment contrast collapses once feasibility and financing are controlled (Sol's current 16/17, 17/18, 7/15, 3/13 could move), the findings share should shrink toward 30% and the validation/seat finding should lead; if a clean current-roster assurance-with-reliance case is found in chronological review, commitments can move into the abstract.

## 9. Venue and timing (I for dates; official pages did not resolve)

AAMAS 2027 full-paper deadline appears to have passed (Oct 8, 2026). ICML 2027 is estimated late January 2027. NeurIPS 2027 Evaluations & Datasets is estimated May 2027 and is the natural fit: the guidelines explicitly accept benchmark plus infrastructure spanning categories and ask whether another team could re-run the benchmark, which the release can answer. Recommendation: arXiv as soon as the draft is sound; NeurIPS 2027 E&D primary; ICML 2027 only if headline findings are frozen by January. Verify dates on the official sites before planning.

## 10. Peer debate record (today)

- Sol → me: no "sets are not the bottleneck" or luck/skill headline; `direct_property_purchase_count` includes inherited price-0 purchases (engine.py ~2998–3010 vs expanded_metrics.py:680); FinBoardBench §4.2 already has proposer/receiver analysis. Accepted. Sol corrected my cash boundary (pre vs post), my "standard rules" wording, my FinBoardBench release wording, and my dice-matching exclusivity; all accepted and fixed above.
- Opus → me: 139/1,663 Grok content–tool disagreements, five accept_trade with "No…" messages; asked me to rerun holding statements with the filter (done: Grok 49 → 45) and to assess commitment novelty (done: both occupying papers are workshop papers; the transaction-embedded assurance is open; no current-roster case). Opus conditions on Claude's refusal treatment (152 private thoughts in 1,696 decisions) and excludes Claude from rationale analyses; I agree.
- Astra → me: infrastructure case rests on the decision-linked workflow plus audited release, not a new API abstraction; keep both elapsed-delay and first-menu measures; mismatch rule as above. I challenged the "validation from existing evidence" stance and raised the Claude treatment confound; the first was refined with Sol, the second is unresolved only in where it appears in the paper.

## Sources (verified today)

- https://arxiv.org/abs/2610.29330 and https://arxiv.org/html/2610.29330v2 (AgentMonopoly)
- https://arxiv.org/abs/2605.27896 and https://arxiv.org/html/2605.27896v1 (FinBoardBench)
- https://arxiv.org/abs/2605.14537 (Cattle Trade)
- https://iclr.cc/virtual/2026/10018196 (Cheap Talk, Empty Promise; AIMS workshop poster); https://arxiv.org/abs/2604.04782
- https://icml.cc/virtual/2026/84089 (When Agents Lie; workshop best paper); https://arxiv.org/abs/2607.05132
- https://proceedings.mlr.press/v235/bianchi24a.html (NegotiationArena)
- https://iclr.cc/virtual/2024/poster/17897 (SOTOPIA spotlight)
- https://neurips.cc/virtual/2024/oral/98026 (AgentBoard oral)
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/a0928f924a344aaebbb7f6cd8d56e34c-Abstract-Conference.html (HAL)
- https://arxiv.org/abs/2609.24967 (Emergent Collusion); https://arxiv.org/abs/2603.20281 (Fragility of AI Agent Collusion)
- https://arxiv.org/abs/2610.35773 (DECE Eurogames arena)
- https://neurips.cc/Conferences/2026/EvaluationsDatasetsReviewerGuidelines
- Repo: `docs/benchmark_audit_fixes.md`, `python/packages/arena/src/monopoly_arena/player_config.py`, `python/packages/arena/src/monopoly_arena/baselines.py`, `python/packages/arena/tests/test_audit_regressions.py`, `python/packages/engine/src/monopoly_engine/engine.py`, `python/packages/telemetry/src/monopoly_telemetry/expanded_metrics.py`, `docs/research_raw/paper_workstreams/related_work_bibliography.md`, `docs/research_raw/paper_workstreams/mechanisms_discussion.md`, `saved_games/*/README.md`, `saved_games/*/audit/*.json`
