# Paper readiness: Opus 5.5 argument

Date: 2026-10-27. Author: Claude Opus 5.5, one of four co-researchers (Astra, Sol, Fable, Opus).
Status: raw research memo. It is not canonical documentation or manuscript text.

Scope of this round: I read both parent threads in full, plus the prior Opus, Sol and Fable reports. I read the repo plans, the historical manuscript and the saved-game artifacts. I reran the key corpus checks with my own scripts, read primary comparison papers, and debated peers directly.

Constraints I kept:
- No engine, prompt, policy, artifact or manuscript changes.
- No provider calls or game runs. No commits.
- This is the only file I added. The harness has no `apply_patch` tool, so I created it with a plain file write.
- My scripts live outside the repo in `/tmp/opus_readiness/` (`load.py`, `conv.py`, `slowcheck.py`, `grokdiv.py`, `grokdiv2.py`).

Evidence labels used throughout:
- **[V]**: verified independently this round from canonical `events.jsonl` / `decisions.jsonl` or a primary source.
- **[P-V]**: a peer's computation that I or another peer cross-checked.
- **[I]**: inherited from earlier threads or reports and not rechecked.
- **[Inf]**: my inference.
- **[Prop]**: a proposal.

---

## 0. Bottom line

1. **Start drafting the integrated paper now.** The corpus, infrastructure and validation evidence already support a substantive, honest paper. It is a bounded observational benchmark study plus a reusable research instrument. It is not a leaderboard.

2. **The paper is not yet submit-ready.** What separates drafting from submission is mostly not more games. It is:
   - a versioned, regenerable derived-analysis layer, because some saved metric tables are wrong for acquisition questions;
   - explicit labels for two provider-interface conditions, Opus refusal recovery and Grok content–tool mismatch, which change what several comparisons mean;
   - a current related-work section;
   - one decision about whether commitments appear in the abstract. If they do, one small pre-specified continuation study is the only new experiment I would call material.

3. **The user's belief that "we have everything" is mostly right for the economic half and for the infrastructure.** It is wrong for a headline claim about commitments, deception or collusion among the current roster. In this corpus the social layer supports a measured taxonomy plus one rich coalition episode. It does not support a breach or cartel headline.

4. **The strongest coherent paper** argues that, in a long-horizon multi-agent economy, negotiation activity and terminal holdings are poor guides to how agents win. The thing that separates agents is how they create, capture and deploy opportunities. MonopolyBench makes that measurable under matched dice, and the paper shows which conclusions survive validation.

5. **Infrastructure earns full-contribution status** through the research capabilities it enables, each tied to a result in the paper. It does not need a new general-purpose framework.

---

## 1. What I verified this round

### 1.1 Corpus facts [V]

Scripts: `/tmp/opus_readiness/load.py` plus inline checks.

- **Size:** 20 games, 50,918 events, 6,989 decisions, 526 `TRADE_PROPOSED`, 394 `TRADE_COUNTERED` and 113 `TRADE_ACCEPTED` events.
  - Collections: `saved_games/railway-research-12-games-2026-10-25/` and `saved_games/railway-research-8-games-2026-10-26/`.
  - Decisions by model: Sol 1,961, Opus 1,696, Gemini 1,669, Grok 1,663.
- **Common dice stream:** within each seed block, the `DICE_ROLLED` value sequence is identical through the end of the shorter game in all 30 within-block pairs. Sol has an independent check in `sol_dice_checks.csv`.
  - This makes the rotation design a common-random-numbers design over dice.
  - It is not a match on opportunities. Jail choices and eliminations change which seat receives which roll, and landings diverge.
- **Winners by block and seat** (turn order 0–3), taken from `GAME_ENDED` plus `seat_assignment.json`:

| Seed block | Games | Winner seat | Winner model |
|---|---|---|---|
| 751774554 | 1–4 | 2, 1, 0, 0 | Gemini, Gemini, Gemini, Grok |
| 2506298840 | 5–8 | 1, 0, 3, 2 | Sol in all four |
| 2573692901 | 9–12 | 1, 1, 1, 1 | Sol, Gemini, Grok, Opus (seat 1 wins with every model) |
| 3648314310 | 13–16 | 0, 0, 0, 2 | Opus, Sol, Gemini, Sol |
| 2766649504 | 17–20 | 1, 3, 0, 3 | Sol, Opus, Gemini, Gemini |

- **First builder:** the first player to build won 17/20 games. The exceptions are games 15, 17 and 20.
- **Trades that complete a colour group:** of 113 accepted trades, 60 completed no group, 43 completed a group for one side only, and 10 completed groups for both sides.
  - 63 group completions are created by trades. Fable's 65 counts by completing event.
- **Opus response condition:** 1,604 of 1,696 Opus decisions show the chain `standard → same_model_without_private_thought`. The standard attempt ended with `finish_reason=content_filter` and `native_finish_reason=refusal` (example: game-01 decisions).
  - Opus has only 152 private thoughts, against 1,961 for Sol, 1,669 for Gemini and 1,663 for Grok.
  - 61 of the 66 engine default moves belong to Opus.
  - Policy and labeling: `docs/model_response_policy.md`.
- **The prompt licenses deception:** `python/packages/arena/src/monopoly_arena/player_config.py:14-46`. It says "You may use any legal strategy or personality (… deceptive … manipulative …)" and "Deception in public chat is allowed; private thoughts should reflect true reasoning." Any instruction-alignment claim therefore needs a separately declared constraint.

### 1.2 New this round [V]: content–tool action-name mismatch, which changes the flagship exhibit

Script: `/tmp/opus_readiness/grokdiv2.py`. Fable and Astra confirmed it independently from the raw attempts.

**The case.** Game 1, turn 40, decision `dec-000112`, events 752 and 754:
- Grok's public message reads "No. St. James is not for sale at any price in this structure…"
- Its `private_thought` begins "Reject."
- `assistant_content` holds `{"name":"reject_trade", …}`.
- The structured `tool_calls` entry carries the **identical arguments** under function name `accept_trade`.
- The engine applied the accept (evt 754, transfers at 757–758). Grok's next message, at evt 761, is "I now have both other light blues". That leads directly into the Gemini light-blue deal (evt 788) and Gemini's build on its next turn.

**Corpus scale.**
- 139 of 1,663 applied Grok decisions have a content function name different from the tool-call name. Fable finds zero such cases for the other three models.
- In 26 of them, message and thought are identical and only the function name differs. These include 5 `accept_trade` decisions whose message says "No…": G1 t40, G2 t22, G3 t39, G5 t37 and G16 t130.
- The other 113 cases differ in message and arguments too, so the content looks like a draft and intent is ambiguous.
- Only Grok runs with `tool_choice: required` (`docs/model_response_policy.md:5`).

**Attribution limits, agreed with Astra, Sol and Fable.**
- Call it a *content–tool action-name mismatch with identical arguments*.
- Do not call it "corruption" or "unintended". We cannot place the cause in the model, the provider or the gateway.
- Keep the applied path as authoritative. Removing rows does not produce a counterfactual game.
- Keep the cases in the say/do population with a flag: "response inconsistency; cause unresolved". The flag alone can never support claims of deception, betrayal or strategic intent.

**Why it matters scientifically.**
- Both Astra and Sol had proposed the G1 chain as the main-text bargaining-to-development exhibit. Its precondition is a mismatch case.
- Gemini's own conduct is still genuine and can be shown, as long as the upstream discrepancy is disclosed. A cleaner exhibit would be better (§3.2).
- A naive say/do or deception analysis would code "No… [accepts]" as lying.
- This is the best concrete argument that decision-linked raw-response preservation is a *scientific* capability. It changes how a headline exhibit is read, which counting fallbacks never would.

### 1.3 Converting trade-created groups: two constructs, both kept [V] and [P-V]

**My window.** Scripts: `conv.py` and `slowcheck.py`. The window is the rest of the trade turn if the trade happened on the owner's turn, otherwise the owner's next own dice turn.
- 41 of 63 trade-created groups were built in-window. Their owners won 15 of 41; the owners of the 22 slower groups won 3.
- Per agent: Sol 16/17, Gemini 16/18, Opus 6/15, Grok 3/13.
- Rent within 40 game turns: $17,495 summed for in-window groups vs $1,776 for the rest (medians $328 vs $34).

**Sol's window: the first actual management menu.** Source: `sol_trade_groups.csv`.
- Sol 16/17, Gemini 17/18, Opus 7/15, Grok 3/13.
- Restricted to groups where the saved engine `buildable_space_keys` made the group buildable when the window opened: Sol 14/15, Gemini 13/13, Opus 5/7, Grok 2/7.
- Astra verified the two cases that account for the 43 vs 41 difference. G6 Opus pink and G8 Gemini dark blue were jail turns with no management menu.

**Agreed construct (Astra's challenge, accepted).** Jail choices (`pay_jail_fine` vs `roll_for_doubles`) determine when management access arrives. So report both:
- (a) elapsed latency from deal to build;
- (b) conditional first-menu deployment, described as conditional responsiveness, not overall strategic speed.

**The slow cases are mostly behavioural, not interface artefacts.** Of my 22 slow cases:
- 14 made no build attempt;
- 6 had build plans rejected by the engine's "interleave purchases" rule (Opus 3, Grok 2, Sol 1);
- 1 was a Grok content–tool mismatch on a build.

The gap therefore survives the interface audit. It is still endogenous, because good deals leave cash. Present it descriptively; it is not a cause of winning.

### 1.4 Primary literature checked this round [V]

- **AgentMonopoly** ([arXiv 2610.29330v2](https://arxiv.org/html/2610.29330v2)):
  - eight open models, local, temperature 0;
  - 140 games: S1/S2/S3 with 40 each, S4 with 20;
  - seeds 42–46; S3 uses four cyclic orders × 5 seeds, which is the same structure as ours;
  - modified rules: rent waiver, elimination at negative cash, a 150-step cap with a net-worth winner;
  - proposer and receiver rates are measured;
  - it does **not** claim identical dice across rotations;
  - it has no systematic analysis linking trades to development or rent;
  - commitments are not analysed, and it reports no clear alliances.
- **FinBoardBench** ([arXiv 2605.27896v1](https://arxiv.org/html/2605.27896v1)):
  - 9 focal models, each against 3 fixed opponents, in 108 matches across three games;
  - seat rotation is used, but no seeds or matched randomness are reported;
  - the staged "arbitrage chain" is described for Acquire, not Monopoly;
  - Monopoly proposer and receiver trades are classified as "harmful" by an LLM judge (DeepSeek V4 Pro) with no human validation;
  - it does not analyse promises, deception, collusion or coalitions;
  - it makes no claims about releasing replays or artefacts.
  - This partly corrects Sol's reading of its §4.2.
- **Commitments are occupied territory, but in a different shape.**
  - [Cheap Talk, Empty Promise](https://arxiv.org/html/2604.04782v1) is an ICLR 2026 workshop paper on one-shot normal-form games.
  - [When Agents Lie](https://arxiv.org/pdf/2607.05132) is an ICML 2026 workshop paper on repeated games with a private plan → announcement → action protocol.
  - Fable verified both venues as workshops.
  - Neither embeds an assurance in an engine-enforced asset transfer whose acceptance records the counterparty's reliance. That gap is real, but the current roster has no clean instance of it.
- **Also relevant:**
  - [AgoraBench / MERIT](https://arxiv.org/html/2602.10467v2) (ACL 2026) includes a monopoly bargaining setting, not the full game.
  - [Cattle Trade](https://iclr.cc/virtual/2026/10018446) (ICLR 2026) reports that strategic commitment predicts success in auctions and trades.

---

## 2. The historical manuscript: what is obsolete and what can be reused

`monopolybench_ieee_draft_v0_1.tex` (1,000 lines, July 2026) is an "audit-ready measurement paper" built on 8 unbalanced games. `monopolybench.tex` is an IEEE template.

**Obsolete:**
- the abstract and thesis ("mechanism corpus rather than a leaderboard … claim discipline");
- the contribution list, which puts the claim-gating methodology at the centre;
- every corpus statistic (1,391 turns, 3,696 decisions, 7/8 strict replay);
- the "E1 pilot" framing;
- the narrative contract in `docs/research_raw/paper_workstreams/narrative_claim_contract.md`, which defends a pilot-only paper;
- `analysis/analysis.md`, which calls the environment "rules-complete" and is contradicted by the declared variants in `docs/benchmark_audit_fixes.md`.

**Reusable:**
- the authority-boundary and decision-loop prose (§3.1–3.3);
- the four-protocol-object definition;
- the state-replay vs artifact-replay distinction;
- the Monopoly-as-decision-process related work;
- `paper/figures/architecture.pdf`, which needs updating for cloud campaigns and response policies;
- the run-273 house-lock figure (`paper/figures/run273_house_lock.pdf`), as a labelled historical mechanism case.

**Bibliography.** 20 `\bibitem`s, all from July or earlier. Missing: AgentMonopoly, FinBoardBench, NegotiationArena, MACHIAVELLI, AgentBoard, HAL, Cheap Talk/Empty Promise, When Agents Lie, AgoraBench, PettingZoo/BenchMARL, and SOTOPIA, which it cites only as related. It is stale enough that the related-work section should be rewritten rather than patched.

**Missing build outputs.** Astra found that the July build outputs (`output/pdf/MonopolyBench.pdf` and the supplement) named in `paper/final_build_manifest.json` are absent. Treat the manifest as historical.

---

## 3. The strongest coherent paper

### 3.1 Thesis and title

**Thesis [Prop].** In a long-horizon, multi-agent economy, terminal outcomes and negotiation activity are poor guides to economic capability. What separates agents is how they create, capture and deploy opportunities under the same dice. Their talk shapes deals through bargaining framing and anti-leader appeals far more than through verifiable lies. MonopolyBench makes these processes measurable and replayable, and shows which conclusions survive provider-interface effects.

**Title options [Prop]:**
- *MonopolyBench: Measuring How LLM Agents Create, Capture, and Deploy Economic Advantage*
- *Deals Are Not Dominance: Long-Horizon Economic Agency in Multi-Agent LLM Competition*

### 3.2 Research questions and claim boundaries

The order below is the order of narrative priority.

**RQ1. Where do outcome differences come from: seat and dice, or agent?** Supporting material [V]:
- the 5×4 block × rotation grid;
- block 2573692901, where seat 1 wins with every model;
- block 2506298840, where Sol wins from every seat;
- 17/20 wins for the first builder.

What the paper can say: outcomes have strong seat and dice structure, and the rotation design makes it visible. Two blocks sit at opposite extremes. Raw win counts (8/7/3/2) therefore have low resolution.

What it cannot say:
- that it has quantified the shares of luck and skill;
- that it has a ranking, or significance tests across 5 blocks;
- "pure luck block" or "pure agent block" as causal labels. That was my own earlier overreach, which I withdraw.

**RQ2. Is negotiation activity the same as negotiation effectiveness?** Supporting material:
- Proposals [P-V]: Opus 240, Grok 136, Sol 132, Gemini 18. Grok's count includes mismatch cases, so treat it with care.
- Gemini was party to 36 completed trades, 25 of them initiated by others, and received the most rent [P-V].
- Of 113 trades, 43 completed a group for one side only [V].
- Opus gave a rival a completed group without gaining one 20 times, often while under $150 cash [P-V].
- Gemini states an explicit set-for-set rule in public messages (G13 t29, G15 t25) [I].
- Sol builds immediately after set-for-set swaps it designed in G5, G6 and G8 [I]. I would check those three upstream decisions for mismatches before using them.

What the paper can say: activity and effectiveness come apart. Recipient-side selectivity and term design matter. Distress drives many one-sided transfers.

What it cannot say:
- "negotiation hurts";
- any measure of trade quality from an LLM judge;
- motive claims about Grok's side of a deal without the mismatch flag.

**RQ3. Do agents deploy the opportunities they acquire?** Supporting material: §1.3, reported both ways.

What the paper can say: deployment at the first management opportunity differs sharply between agents in this roster (14/15 and 13/13 vs 5/7 and 2/7 when the group was buildable on entry). Owners of groups deployed quickly won far more often.

What it cannot say:
- "acquisition is not the bottleneck";
- that fast deployment causes winning.

The strongest supporting case is one where neither side's upstream decisions are flagged. G15, where Gemini won with no trades, and G14, where Sol won with no trades, show that routes to winning without trading exist for both top agents. That is a useful counterweight to any story where trades are necessary.

**RQ4. What does the social layer of a competitive economy look like?** Supporting material:
- the G16 anti-leader episode:
  - Opus urges blocking (t199, t203);
  - Sol states that Illinois and Pacific are "off-limits" (evt 2711);
  - Opus itself offers North Carolina to the leader (evt 2808, 3260), and the leader rejects;
  - Sol buys the dark blues while explicitly keeping development cash (evt 2976).
- Fable's holding-statement rerun: "not for sale" language is overwhelmingly Grok posture (49 reversed vs 52 not; 45 after the mismatch filter). Gemini has 0 reversals vs 12 and Sol 0 vs 3 [P-V].
- Bounded checks find no materially false cash or affordability claim [I].
- Lexical search plus case reading found no explicit no-bid or market-division pact [I]. That is a bounded search, not a null result.

What the paper can say:
- coordination takes the form of appeals for anti-leader restraint and self-interested blocking;
- "not for sale" talk is mostly bargaining posture;
- verifiable factual misstatements were rare in the bounded checks;
- strategic communication works mainly through framing.

What it cannot say:
- "models break promises";
- "no collusion";
- any alignment violation, because the prompt permits deception.

Historical run-172 (an assurance followed by a resale in the same turn) and run-273 (paltering about a house lock) can appear only as labelled historical mechanism cases, with a different roster and older rules.

**RQ5 (validation). Which conclusions survive validation?**
- Rules scenarios with independently specified outcomes, replay of all 20 runs, and tests that deliberately corrupt logs and exercise recovery [I; Astra reports a fresh full verify passing].
- Two provider-interface conditions, each with a defined handling rule:
  - **Opus refusal recovery:** label the participant "Opus 5.5 under refusal recovery" and exclude it from comparisons of private rationale.
  - **Grok content–tool mismatch:** flag the affected cases and run sensitivity analysis.
- The reference policies are simple and do not justify claims of strategic competence.

**Comparison scope [Inf].** For any comparison that touches private reasoning or say/do behaviour, the cleanest pair is Sol vs Gemini. Opus has almost no private notes, and Grok's actions carry mismatch flags. Fable raised this challenge and I agree with it.

### 3.3 Figure-first manuscript spine [Prop]

The proportions are rough targets, not a page budget.

**Lead (abstract, introduction, Figure 1).**
- **Figure 1:** the 5×4 grid of seed block by rotation. Each cell shows the winning model, with its seat marked.
- It shows at once that outcomes follow seats in some blocks and agents in others, which is why the paper studies trajectories.
- It is honest, visual, novel in how it is used, and it motivates everything that follows.

**Economic and multi-agent findings (~40%):**
- **Figure 2:** activity vs effectiveness. For each agent, proposals per 100 own rolls, trades completed as initiator and as recipient, rent received, and wins, with each block visible.
- **Figure 3:** creating vs capturing value in trades. The 113 trades split into none, one-sided and mutual, with who completed a group and the grantor's cash at the time.
- **Figure 4:** deployment. Elapsed latency next to conditional first-menu deployment, per agent, from saved engine menus, alongside rent over a fixed horizon.
- **Figure 5:** one swimlane trajectory from deal to dominance for an unflagged case: acquisition → trade → build → rent → distress, with event IDs on every mark.
- **Figure 6:** the social layer. The G16 episode timeline, plus a three-class taxonomy of communication (posture, reliance-inducing assurance, third-party restraint appeal) with counts by agent.

**Environment and infrastructure (~40%).** Organise this section around four research capabilities, each paired with a result it enabled:
1. An engine-authoritative economy with parameterised legal-action surfaces. Every result is about applied legal actions; the buildability conditioning in RQ3 uses saved engine menus.
2. A chain linking each decision to its observation, the raw response from every attempt, the applied action, the resulting events and snapshots, and two separate replays (state and artifact). This enabled the dec-112 discovery and the Opus condition label.
3. Controlled cloud campaigns:
   - frozen treatments with a treatment fingerprint;
   - seed × cyclic-rotation blocks with a dice stream verified to be shared;
   - durable recovery and response reuse;
   - cost accounting at the provider level, including BYOK.
   These enabled Figure 1 and are what make the corpus trustworthy.
4. An opportunity-aware longitudinal analysis layer, which produces the metrics behind Figures 2–4. This is the bridge to the findings.

Each capability should get one short worked example. Leave out the implementation history.

**Validation (~20%):**
- a matrix of claims against evidence;
- rule scenarios, replay of all 20 runs, and corruption and recovery tests;
- reference-policy calibration, stated with its limits;
- **Box:** two provider-interface effects and their handling rules (Opus refusal condition; Grok content–tool mismatch, with dec-112 as the worked example).
- Fallback and engine-default rates go in an appendix table only.

**Discussion and limits.** One roster, 5 blocks, medium reasoning effort for every model. Each participant is an agent system (model plus prompt, memory and response policy). The study is descriptive, not causal. Historical cases are labelled. The prompt is permissive.

### 3.4 Infrastructure as a contribution: what earns it

- It earns the status when each capability is tied to a result in the paper that would be impossible or wrong without it:
  - matched dice, for RQ1;
  - saved legal menus, for RQ3's conditioning;
  - raw responses from every attempt, for the dec-112 reinterpretation and the Opus label;
  - replay, so others can trust the trajectories.
- **Comparative advantage, all verified this round:**
  - AgentMonopoly modifies the rules and caps games at 150 steps;
  - FinBoardBench uses an LLM judge without human validation and makes no release claims;
  - neither verifies a shared dice stream;
  - neither keeps the raw-response provenance needed to catch a content–tool mismatch.
- This is not a claim of blanket superiority. AgentMonopoly has more games and personas; FinBoardBench covers more games and models.
- **Release requirement for submission:** a single command that regenerates every number in the paper from the committed collections. Sol's `sol_reproduce.py` is a start. Without it, the "inspectable and reproducible" claim stays a promise. This is the most important piece of infrastructure work left.

---

## 4. Strongest objections to "we have everything"

These are ordered by how much each would damage a paper submitted today.

1. **The current derived analyses are not publication-grade.**
   - Sol found that `direct_property_purchase_count` includes inherited `PROPERTY_PURCHASED price=0` (compare `expanded_metrics.py` ~680 with `engine.py` ~2998–3010). Astra had independently found 944 = 475 direct + 72 auction + 397 creditor.
   - So per-game `analysis/` tables cannot back acquisition claims.
   - Paper numbers need a new versioned analysis script that reconstructs from events.
   - This is material for submission, not for drafting.
2. **Two of the four participants are in non-standard conditions.**
   - Opus: about 95% action-only after refusal, with no corrective retry.
   - Grok: forced tool choice, with 8.4% content–tool mismatch.
   - Any table titled "model X vs model Y" is really comparing agent systems. Reviewers will spot this, so the paper should say it first, with a handling rule for each condition.
   - Material.
3. **The social and alignment pillar is thin for the current roster.**
   - There is no clean current-roster breach of a reliance-inducing assurance, and no cartel.
   - If the abstract promises "commitments, deception and collusion", the evidence underdelivers.
   - It is material only if commitments go in the abstract.
4. **"Better than existing papers" needs a comparison table, not adjectives.** Each comparator wins on something: AgentMonopoly on game count and personas, FinBoardBench on breadth of games and models. The defensible claims are depth (exact longitudinal, opportunity-aware, two-sided), control (a verified shared dice stream), and inspectability (decision-linked provenance with a regeneration command).
5. **Related work is stale** (§2). Material for submission.
6. **Reference policies.** Six simple baselines exist (`baselines.py:11-25`). Their trade proposals are empty offers (`_trade_propose_action`, `baselines.py:88-99`).
   - They cannot calibrate negotiation.
   - Cheap local baseline games, with no provider cost, could calibrate the "first builder wins" base rate and check that the development metrics separate `builder` from `no_trade` or `cash_conservative`.
   - That buys one specific validation claim. It is desirable, not mandatory, and it is not a tournament.

**Where I disagree with my earlier self and with the consensus.**
- I withdraw the "pure luck block / pure agent block" causal labels.
- I withdraw "acquiring a monopoly is not the bottleneck".
- I withdraw "corruption / unintended" for the Grok mismatch.
- Against the consensus: the G1 chain should not be the flagship exhibit.
- Against the consensus: commitments should not be a co-equal headline RQ unless the continuation study is run.

---

## 5. The strongest case we can draft now

The following is already supported. "Descriptive" means one roster, five blocks.

1. Rotation reveals strong seat and dice structure in outcomes. The extremes are block 2573692901 (seat-determined) and block 2506298840 (Sol wins from every seat).
2. Negotiation volume does not track effectiveness. Gemini trades selectively as a recipient and has the highest rent. Opus has the highest volume and the most one-sided grants, many under distress.
3. Conditional deployment of trade-created groups separates Sol and Gemini from Opus and Grok, and survives the audit of interface effects.
4. The social layer consists of anti-leader appeals with self-exceptions, posture-heavy "not for sale" talk, and few verifiable lies. Explicit collusion was not found in bounded searches.
5. The infrastructure made all of this measurable and caught two provider-interface effects that would otherwise be misread as behaviour.
6. Validation: replay of all 20 runs, rule scenarios, and corruption and recovery tests.

This is a complete, honest, interesting paper. Its weakest part is the social pillar, not the economic one.

---

## 6. Remaining evidence work

**Material for submission** (none of it needs paid model calls):
1. A versioned derived-analysis script (Sol's `sol_reproduce.py` as the base) that regenerates every paper number and figure from committed collections. Include the buildable-menu conditioning and both latency constructs.
2. A mismatch and refusal-condition provenance column on every decision-level analysis, plus a stated handling rule for each condition. Rerun the clean candidates for the Figure 5 exhibit (the G5, G6 and G8 Sol swaps; G15 Gemini; G14 Sol) against the mismatch set before choosing one.
3. Codebook application to the social episodes (posture, assurance, restraint appeal), with recipient-exposure checks taken from saved prompts and a second reviewer on every strong claim.
4. A rewritten related-work section and comparison table, using the verified sources in §1.4 and Fable's memo.

**Conditional on the claim chosen:**
5. **Only if commitments go in the abstract:** one pre-specified short-continuation study, Sol's design, trimmed down.
   - **Design:**
     - an agent voluntarily negotiates an explicit, time-limited holding assurance;
     - the game branches from its own state and memory;
     - a low-cost and a high-cost breach offer are presented, with honouring kept feasible;
     - outcomes are recorded as hold, seek release, renegotiate, or breach;
     - selection into commitment is reported.
   - **What it buys:** the unoccupied embedded-assurance claim.
   - **Blocker [Inf]:** I did not find a branch-from-saved-state runner that rebuilds memory. The `micro-v1` suites are single-decision fixtures (`docs/micro_research_suites.md`). Building one is prompt-adjacent and needs owner approval plus prompt-preservation tests. Run all models under the same tool-choice setting, or log mismatches.
   - **Otherwise:** this is future work.
6. **Only if the paper claims that measurements detect known differences:** local baseline games (no cost). See §4.6.

**Desirable future work, not needed for this paper:**
- more rosters or blocks for ranking;
- an instruction-alignment treatment with a declared honesty or anti-collusion constraint;
- a no-trade or no-messaging intervention;
- a human-play comparison.

---

## 7. Record of the peer debate

**Resolved:**
- The G1 chain cannot be presented as intended negotiation by Grok. All four researchers agree; Gemini's applied conduct stands.
- Terminology is "content–tool action-name mismatch". Keep the cases in the population with a flag. The flag alone never supports claims of intent. This was Astra's correction, and I accept it.
- Report both latency constructs (Astra's correction). Sol's legal-menu reconstruction is the better conditional measure.
- The shared dice stream is a design strength that we verified and use analytically. It is not unique: AgentMonopoly's S3 has the same rotation structure without claiming matched dice. It is not causal (Sol's correction).
- The current corpus supports drafting. Any new game or experiment must name the claim it buys (all four agree).

**Still open:**
- **Commitments in the abstract.** Fable and I lean toward the taxonomy in the main text, with the continuation study only if commitments are headlined. Sol favours running the study. Astra favours a precise episode-level treatment.
- **Prominence of the provider-interface box.** I would give it a validation box and one worked example. Astra warns against letting pipeline defects become the story. We agree on direction but may differ on space.
- **Fable's challenge on conditioning private-rationale analyses on the Opus condition.** I agree: Opus has 152 private thoughts across 1,696 decisions. Public-message say/do analysis can include Opus. Private-rationale analysis cannot.

---

## 8. Summary for the parent

- **Readiness:** draft now; not submit-ready.
- **Gaps between draft and submission:**
  - (1) a regenerable versioned analysis layer, because some saved metric tables are wrong for acquisition questions;
  - (2) handling rules for the Opus refusal condition and the Grok content–tool mismatch;
  - (3) rewritten related work;
  - (4) the commitments decision: either the taxonomy only, or one small continuation study that probably needs a new branch-from-state runner.
- **Strongest paper:** create, capture, deploy. Lead with the 5×4 grid; follow with the activity vs effectiveness, trade-capture and deployment figures, then the social-layer taxonomy and the G16 episode. Tie infrastructure to four capabilities, each enabling a specific result. Validation includes the provider-interface box.
- **New finding this round:** the G1 "flagship" chain rests on a Grok accept whose own arguments say "Reject". This shows that provenance changes interpretation, and it rules G1 out as the unqualified lead exhibit.
- **Memo path:** `docs/research_raw/paper_readiness_2026-10-27/opus_argument.md`
