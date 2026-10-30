# Step 14: detailed venue-neutral outline (Opus)

Opus (claude-opus-5-5), 2026-10-29. This is an outline, not manuscript prose. Every section lists:
- its **argument** (what the section must establish);
- **evidence**, as audited claim IDs from the phase-2 ledger (R01–R25), my phase-3 analyses, and files;
- **exhibits**, from `figure_table_plan.md` and peers' built exhibits;
- **citations**, as keys in `references.bib`;
- **alternative explanations** the text must state;
- the **transition** to the next section.

Tier labels (A/B/C/D) come from `experiment_decisions.md`. Debate outcomes that changed this outline are noted inline and recorded in `debate.md`.

## 0. Frame

### Working title options (venue-neutral)

1. *Winning, Financing and Talking Over Hundreds of Turns: An Adjudicable Study of Frontier Agents in a Competitive Monopoly Economy*
2. *What It Takes to Read a Long Game: Capability and Conduct of Configured LLM Agents in Multi-Agent Monopoly*
3. *MonopolyBench: Long-Horizon Economic Competition and Social Conduct Among Frontier Agents, with Exact Legal-Alternative Audits*

I prefer (2) or (1). Avoid "benchmark" as the headline noun unless the release and validation package (steps 17–18) is complete.

### One-sentence thesis

In a rule-authoritative, four-player economy played to bankruptcy, the same terminal outcome can come from chosen strategy, a discarded or inaccessible legal option, or a provider/harness condition. Recording legal menus, per-attempt responses and replayable state, and testing legal alternatives at exact historical prefixes, makes those cases distinguishable. That changes what can honestly be said about agents' economic capability and conduct.

### Research questions

- **RQ1 (capability).** How do configured frontier agents acquire, finance, develop, liquidate and survive across complete games?
- **RQ2 (conduct).** Relative to the declared contract, how do they bargain, represent facts, keep or withdraw offers and appeal to third parties, and how do recipients respond?
- **RQ3 (environment).** What must a long-horizon multi-agent sandbox record and afford for RQ1 and RQ2 to be adjudicable, and to support later alignment research and training?

**The motivating question, stated and not answered:** how does alignment-relevant conduct change as capability grows?

### Contributions (each phrased as a measured capability with its scope)

1. **Cohort.** A complete, replayable cohort: 20 uncapped games ending by bankruptcy; 6,989 decisions; 8,679 attempts; five shared-dice seed blocks × four rotations; four configured frontier agents (R01; O1–O4).
2. **Analysis protocol.** Exact-prefix legal-alternative auditing that classifies discarded plans, accessible versus nominal finance, and refuted labels. Applied to all 66 defaults and all 60 eliminations (R06, R08–R10). Comparison is stated as "not found in inspected sections" of the closest competitors (`comparison.json`).
3. **Longitudinal economic profiles** that separate acquisition route, completion route, deployment, receipts and estates, including two trade-free wins and an inheritance-concentration account (R03–R05, R12–R17; deployment residual).
4. **A norm-explicit social chronology:** misleading framing with a recorded omission rationale; correction with acceptance; echo then rejection; offer withdrawal; a channel leak. Each case states its competing explanation and claims no prevalence or misalignment rate (R18–R21).
5. **An affordance ledger and normative-contract comparison** turning the alignment question into concrete environment requirements (T6, T7).

### Abstract skeleton (claims allowed, by tier)

- **Allowed (A):**
  - the cohort and design;
  - no model ranking or seat effect established;
  - the 61 discarded-but-legal plans;
  - the 3/56/1 elimination finance split;
  - development accounting is not ROI, with inheritance concentration;
  - the deployment residual is execution- or channel-dominated;
  - the misleading-framing case with exposure and settlement but no identified persuasion;
  - public deception is authorized, so no misalignment verdict;
  - environment requirements for alignment research.
- **Never in the abstract:**
  - ranking, trend, persuasion effect, deception or misalignment rate;
  - "first", "only", "more realistic";
  - causal claims about trading, inheritance or house denial.

---

## 1. Introduction

**Argument (5 paragraphs).**

1. **Why long-horizon competitive economies.** Agents increasingly act for separate principals over long horizons. Economic sandboxes make capital acquisition, a capability flagged as safety-relevant (`backlund2025vendingbench`), observable alongside social conduct with counterparties (`li2026arena`). Monopoly adds four features:
   - endogenous opportunity creation, through trades and auctions;
   - financing with legally sequenced access (sell before mortgage; hotel stock rules);
   - finite shared resources (the house supply);
   - creditor estates that concentrate assets.

   It also stays rule-authoritative and replayable.
2. **The motivating question** of how capability and alignment co-vary, and why the evidence so far is mixed and design-dependent:
   - an Arena null across 12 models (`li2026arena` §5.3.2);
   - within-family capability linked to earlier collusion under a violation affordance (`shi2026emergentcollusion`);
   - accuracy that is not honesty (`ren2025mask`);
   - safety metrics correlated with capability (`ren2024safetywashing`).

   State plainly that this paper does **not** add a point to that curve, and why: four configured systems, four providers, one time point, one contract.
3. **The measurement problem.** A terminal win, a plausible explanation or an applied END does not identify why it happened. In this cohort:
   - 61 "decisions not to build" are rejected but legal plans (R06);
   - three of five Grok non-builds in the deployment-residual population are received ENDs whose content requests a build;
   - one apparently solvent player is legally locked (R10).
4. **What we do.** Record menus, attempts, channels and state; audit legal alternatives at exact prefixes; keep norms explicit; report cases with competing explanations.
5. **Contributions and non-claims.** The list above, plus an explicit "we do not claim" list:
   - ranking;
   - a capability trend;
   - a persuasion effect;
   - a deception or misalignment rate;
   - optimal policy;
   - counterfactual winners;
   - a coalition or kingmaking.

**Evidence:** R06, R10, the deployment residual, O2.
**Exhibits:** optional teaser of F1 (G12 d249 evidence chain).
**Citations:** `backlund2025vendingbench`, `li2026arena`, `andon2026arena`, `shi2026emergentcollusion`, `ren2025mask`, `ren2024safetywashing`, `wu2026agentmonopoly`, `hu2026finboardbench`.

**Alternatives to acknowledge up front.** Monopoly is a stylized, luck-heavy game, and LLM-only populations are not human markets. Answer: we make no realism claim. The value is adjudicability under rich mechanics.

**Transition.** "Several recent environments study parts of this; we place ours precisely."

## 2. Related work (five families; bounded comparisons)

1. **Long-horizon economic agents.**
   - Vending-Bench, which is single-agent; its failures include believing undelivered orders had arrived. This parallels our phantom-build notes.
   - The VB2 and Arena author pages.
   - The Arena corpus paper, which already covers multi-agent commerce, state-checked false claims, follow-through, and a capability test.
   - Market-Bench, Magentic Marketplace and Cattle Trade (a workshop paper with code baselines and an error-policy taxonomy).

   **Our position:** a rule-authoritative economy with forced liquidation and estates; per-attempt provenance; exact-prefix feasibility audits; public replayable artifacts. Arena's environment is "not publicly redistributed" (§2.1 fn).
2. **Board-game agent evaluation.**
   - AgentMonopoly: 140 games (Table 3), with the README listing 120; legal_actions; a deterministic engine; personas; a size axis; no liquidation step (README).
   - FinBoardBench: a focal model versus fixed opponents; an LLM trade judge; an "Investment ROI" profile; classic bankruptcy.
   - DECE: complete-system unit; matched harness studies with bounded results; cost frontiers; non-LLM baselines; no dialogue.
   - BALROG and GameBench briefly, plus pre-LLM Monopoly RL (`bonjour2022monopoly`).

   **Our position:** shared infrastructure is acknowledged. Differences lie in mechanics, cohort and analysis protocol.
3. **Social conduct under a normative contract.**
   - SOTOPIA, NegotiationArena (desperation tactics pay about 20%), MACHIAVELLI (separate reward and ethics axes), Among Us (deception required by the objective), Moloch's Bargain, GovSim, Cicero.
   - The promise papers, both workshop papers.

   **Our position:** the same act has a different status under different contracts (T6). Ours permits public deception and asks for truthful private notes.
4. **Capability versus alignment.** Arena (null), Emergent Collusion (positive within family), MASK, Safetywashing.

   **Our position:** we specify the design that could answer the question (§10) rather than answer it.
5. **Validity, statistics and oversight.**
   - ABC checklist, BetterBench, HAL (cost; log inspection), Agents That Matter, error bars, lm-eval lessons.
   - The METR horizon definition, which is human time and not agent run length.
   - CoT faithfulness and monitorability (`turpin2023unfaithful`, `lanham2023faithfulness`, `baker2025monitoring`, `korbak2025monitorability`).

   **Our position:** explanation channels are non-privileged. Received-call conflicts are a diagnostic, not monitor accuracy.

**Exhibit:** T8 compact comparison, from `comparison.json`, with the caption rule "not reported in inspected sections".

**Alternative/threat.** Recent preprints from October 2026 (AgentMonopoly, DECE) may revise. Cite exact versions.

**Transition.** "We now specify exactly what our agents were, what they were told, and what they could do."

## 3. Environment, normative contract and the evaluated object

**Argument.** The evaluated unit is the configured agent: model, prompt, memory, response policy and request settings. The contract permits public deception. The engine is authoritative.

**Subsections.**

- **3.1 Rules.** The declared variant (`docs/benchmark_audit_fixes.md`):
  - creditors inherit developments intact;
  - no mortgage-transfer interest;
  - no auction on return to the bank;
  - jail-restricted management;
  - no building auctions;
  - finite house stock;
  - uncapped games ending by bankruptcy.

  Explain why the variant matters for inheritance concentration (§6.6). Contrast classic bankruptcy (`hu2026finboardbench` App. C.3) with negative-cash elimination (`wu2026agentmonopoly`).
- **3.2 Decision interface.**
  - Legal menus and tool schemas.
  - A free-text public message on every action.
  - A private note fed back as memory.
  - Trades of up to 20 exchanges.
  - Memory window and timeline.
  - Mention the trade-history formatter defect here only as a pointer (§8).
- **3.3 Normative contract.** Quote `SYSTEM_PROMPT_V1` lines:
  - public deception allowed;
  - private notes "should reflect true reasoning";
  - use only legal tools.

  Under this contract: applied rule violations cannot occur; attempted invalid actions are recorded; false public claims are authorized; false private notes are possible breaches of a soft norm, confounded with memory error. This is **non-identification, not impossibility** (Astra correction, debate R3). Include T6 normative contracts here or in §7.
- **3.4 Response policy and request settings.**
  - One corrective retry, then a deterministic fallback.
  - The Claude refusal → action-only stage. Its stated reason is a provider ToS restriction on output duplication, not a moral refusal.
  - Grok alone has `tool_choice="required"` (`player_config.py:328–334` at both run commits).
  - Reasoning effort "medium" for all.
- **3.5 Artifacts and replay.** Events, actions, decisions, attempts, snapshots and prompts; state and artifact replay; prefix reset (`opus_sandbox_checks.json`, 20 checks).

**Exhibits:** T1 (environment and contract); F1 (evidence chain); A2 (channel availability).
**Citations:** `wu2026agentmonopoly`, `hu2026finboardbench`, `zhang2026dece` (complete-system unit), `kapoor2026hal`.

**Alternatives.**
- "Results are artifacts of the variant rules." Partly true for inheritance. State it as rule-conditional.
- "Results are artifacts of harness differences." DECE shows harness effects can be large locally. Our unit is the configured agent, and we never rank.

**Transition.** "With the object defined, we describe the cohort and how claims were adjudicated."

## 4. Cohort and adjudication method

**Argument.** Every substantive claim is resolved against canonical records with an exact unit. Review provenance is reported honestly.

**Subsections.**

- **4.1 Design.**
  - Five seeds × four cyclic rotations; each agent occupies each seat once per block.
  - Raw dice prefixes are shared within a block, but opportunities diverge (A3, CRN horizon).
  - Treatment fingerprint differs between G1–4 and G5–20. Running `git diff` between the run commits 42f85183 and d6808534 shows 18 changed files: campaign-concurrency limits (5 → 8), UI, API job plumbing, documentation and tests. No engine, prompt, decision-resolver, player-configuration or OpenRouter-client file changed. No behavioral effect is inferred.
  - The Opus refusal rate shifts from 0.57–0.76 in G1–4 to 1.00 in G5–20 at the same boundary, with no model-facing code change. Report the coincidence only; do not attribute a cause.
  - All games are uncapped; lengths run 75–386 turns.
- **4.2 Evidence hierarchy.** Events → actions → menus → delivered prompts → applied notes and public messages → provider summaries → unapplied content. Model text is a recorded account, not intent (`turpin2023unfaithful`; the AgentMonopoly §4 disclaimer).
- **4.3 Legal-alternative audits.** The protocol:
  1. restore the prefix;
  2. execute the acting player's own legal sequence;
  3. stop at a stated endpoint;
  4. never continue the historical suffix.

  It yields classifications, not counterfactual games. Scope versus competitors: "not found in inspected sections".
- **4.4 Economic accounting definitions.**
  - spending unit = game × player × color with an own build;
  - developed rent = paid rent above the undeveloped rate;
  - ownership windows; estate provenance;
  - accessible versus nominal finance.
- **4.5 Social adjudication.** Proposition truth / speaker record by channel / exposure in the recipient's delivered prompts / recipient response / settlement / competing explanation. Never infer intent from one channel.
- **4.6 Review provenance.**
  - Full-channel extraction over all 6,989 decisions and 8,679 attempts by named model reviewers (Terra; Astra-started, Sol-completed). Public pass: 1,367 Sonnet and 5,622 Haiku decisions.
  - Four coauthor models adjudicated all 614 catalog entries and 240 fixed-sample bundles.
  - No human annotation, no inter-rater statistic, no preregistration. Codebooks are post hoc.
- **4.7 Uncertainty.** No decision-level p-values. Whole-game and whole-block dependence. The reference nulls in F2 are calibration aids only (`miller2024errorbars`).

**Exhibits:** A3 (CRN horizon); A6 (prefix-reset validation); A7 (claim-strength ladder).
**Citations:** `zhu2025abc`, `reuel2024betterbench`, `miller2024errorbars`, `biderman2024lessons`.

**Alternative/threat.**
- "LLM reviewers may share biases." The response is the explicit limits, original-checked retained claims and preserved disagreements, not majority votes.

**Transition.** "We begin with outcomes, because readers will ask 'who won' first, and the answer constrains everything after."

## 5. Results I: outcomes and their dependence

**Argument.** Wins are 8/7/3/2 (Sol/Gemini/Opus/Grok), but the design cannot rank agents or isolate seat advantage.
- One block is a model sweep (Sol, G5–8).
- One block is a seat sweep (seat 2, G9–12).
- Seats 1–2 win 14/20.
- Under i.i.d. reference nulls, which ignore dependence: P(prespecified agent ≥ 8) = 0.10; P(any agent ≥ 8) = 0.40; P(seats 1–2 ≥ 14) = 0.058.
- Both dice blocks and agents appear to matter, and the design cannot decompose them.

Add the cost and usage profile as context:
- known cost is $141.71; Opus's figure is a lower bound;
- Grok uses about 30× Sol's completion tokens per decision;
- the agent with the most wins used the fewest completion tokens per decision. This is descriptive, not a compute law (`zhang2026dece`; `muller2026cattletrade` §4.6 makes a similar token-versus-rank observation).

**Evidence:** O1–O3; `outcome_dependence.json`; `cost_usage.csv`.
**Exhibits:** F2 (my faceted grid or Astra's f02; one convention, one-based seats); A1 (cost and usage).

**Alternative explanations.**
- Seat order (moving first shapes early acquisition).
- Dice blocks.
- Opponent composition (one roster).
- Provider stochasticity (one realization per cell).
- Response conditions (Opus action-only; Grok forced tool choice).

**External context (discussion only, not validation).** VB2 single-agent placements for Sol, Gemini and Grok.

**Transition.** "Win counts hide how games were won. We follow the economic life cycle."

## 6. Results II: the economic life cycle

Each subsection pairs a measurement with its unit, its limit and at least one counterexample.

- **6.1 Acquisition and opportunity creation** (E1, E5).
  - Deed routes and completion routes.
  - Inherited completions; 69 are terminal.
  - Eighteen winners traded. G14 Sol and G15 Gemini won without trading; their routes were auctions, purchases and denied proposals.
  - Thirteen first winner-built groups contain a traded deed.
  - *Alternative:* trading as a cause of winning is not identified (D-only E8).
  - *Exhibits:* T2; F3 panels G14/G15.
- **6.2 Bargaining profiles** (E2, E3, E6).
  - Propensity versus intensity.
  - Gemini rarely proposes but bargains actively as a recipient.
  - Completion splits 60/43/10.
  - Rejections of own completion carry rival-financing reasons (G1 d294, G9 d137, G11 d258).
  - Contrast FinBoardBench's judge-rated "harmful" trades. Ours is a different construct.
  - *Alternatives:* endogenous eligibility; received-call conflicts making some applied Grok proposals or acceptances non-deliberate.
  - *Exhibits:* F4 (negotiation); T4 bilateral completion (Astra t04).
- **6.3 Deployment after acquisition** (E4 plus the residual).
  - 43/63 groups are built in the first management turn; 34/42 when buildable at entry.
  - **New:** all eight entry-buildable non-builds split into three engine defaults, three Grok received ENDs against build or finance content, and two explicit Grok holds.
  - Fable independently reconciled this over all 63 groups by the turn-ending decision.
  - So the per-agent conditional rates are not willingness to build.
  - *Exhibits:* Astra's F4 with F4b residual annotation; T4 (recovery).
- **6.4 Recovery changes what gets built** (F1, F2).
  - All 61 Opus defaulted plans execute after reordering.
  - Successful recoveries change purchases in 12/18 Gemini and 5/25 Sol cases, and in 0/5 Grok cases.
  - Chosen holds coexist: G3 d176 Opus prefers a $204 reserve; G1 d426 Grok has a correct $1,418 liquidation buffer; G5 d251 Gemini.
  - *Alternative:* a repaired policy might have produced a different game. Not run (D-only F11).
  - *Exhibits:* T4 / Astra f07.
- **6.5 Construction, receipts and censoring** (F5).
  - 103 units; $103,450 outlay; $93,000 whole-game paid developed rent and $92,550 after first own spend.
  - Forty units have zero rent, 26 of them with no creditor elimination either.
  - The G19 same-deed dark-blue contrast.
  - Explicitly **not ROI**, contrasting FinBoardBench §4.3.
  - *Alternatives:* deterrence; salvage; unpaid terminal debts; late construction; inherited buildings.
  - *Exhibits:* F6 / Astra f05 (re-encoded per debate); A5 two-window.
- **6.6 Liquidity, access and elimination** (F3, F4; R08–R11).
  - Of 60 eliminations: 56 fall below even the full bound, three admit a legal payment, and one is a hotel lock.
  - The three payable cases differ in mechanism. In G12 d249 the received declaration contradicts survival-recommending channels.
  - Successful staged liquidations are the counterexamples: G20 d327–336 pays $1,400 and keeps $14; G18 d428.
  - Access timing matters: no mortgage action exists in purchase menus.
  - Note that AgentMonopoly has no liquidation step, and FinBoardBench defines bankruptcy by "maximum liquidatable net worth" without the access/nominal split.
  - *Exhibits:* T3 / Astra f06 (after the label fix); F1.
- **6.7 Inheritance concentration and the house supply** (F6, F7; R15–R17).
  - The eventual winner is creditor in 54/60 eliminations (35/40 nonterminal).
  - 58 winner groups, 34 with inherited deeds, 30 first completed by estate.
  - 57 eliminations follow developed-colour rent.
  - Bank houses reach zero in nine games; there is a genuine G7 lock alongside costly workarounds (G5 d306, G12 d312).
  - *Alternatives:* inheritance as a rule effect; no binding-shortage count (B-tier F8); house denial not causal.
  - *Exhibits:* A4 stock series (Fable's stock grid is a strong supplement).

**Transition.** "Economic moves were negotiated in language. We now examine how agents represented facts and how recipients responded, under the actual contract."

## 7. Results III: conduct while competing

**Argument.** Under a contract that permits public deception, the cohort contains:
- delivered misleading financial framing with a recorded omission rationale;
- recipients who correct false premises and still accept favourable terms;
- a transient echo followed by correction and rejection;
- an exposed standing offer later withdrawn;
- a private-note leak;
- anti-leader appeals without an identified binding coalition.

These are substantive findings about competitive language and its limits. They are not misalignment verdicts or rates.

- **7.1 The norm and the opportunity.** T6 normative contracts.

  Why Arena's 12.58% is not comparable: a different contract and taxonomy, email-level judge coding versus our case adjudication.
- **7.2 Misleading framing with omission (G13 d250–253).**
  - Opportunity: the seller has $35; $130 plus a $130 Ventnor mortgage gives $295 against a $200 bill.
  - The d252 framing says $130 is insufficient. The returned explanation names the omission, and the applied note acknowledges the route.
  - Exposure: the buyer's d253 prompt contains the message.
  - Settlement at $200.
  - Competing explanation: at d251 the buyer had already opened at $130 (its applied action) and recorded that the payment "keeps p4 solvent enough to cover Short Line rent to p2". That is in the provider reasoning summary.

  Our achievability check (a legal sequence reaching $295) is a modal analogue of Arena's state-claim Stage B.
- **7.3 Boundary cases that constrain persuasion readings.**
  - G4 d148–152: the recipient's private note recorded the true $150 before the false claim, then gave public assent.
  - G6 d019–020 and G19 d135–136: correction with acceptance.
  - G11 d255–258: echo, then check, correction and rejection.
- **7.4 Offers and commitments (G18 d431/441/442).**
  - Invoked, then withdrawn after a $750 rent and liquidation. No costly reliance is shown.
  - Contrast Arena's App. D promise enactment, the workshop promise papers (`shi2026cheaptalk`, `shi2026agentslie`) and recent commitment-semantics preprints (`wei2026standing`, on who may release a promise; `tang2026emptycommitments`, on promises a runtime cannot fulfil; both found by Sol). Our setting has no commitment object (T7). The offer here is a feasible game action, so the question is withdrawal under changed conditions, not feasibility or standing.
- **7.5 Channel boundaries (G20 d001/d004).**
  - The received public field carries the private string, and the recipient notices it.
  - The origin is unlocalized.
- **7.6 Received-call conflicts.**
  - G12 d249 (declaration against survival-recommending explanations).
  - G19 d135 ("Abort this trade. Do not send it", then sent).
  - G18 d083.
  - The deployment-residual ENDs G8 d163 and G12 d166, whose received notes claim builds that never occurred.
  - Context: 139 Grok name conflicts as a diagnostic count, under `tool_choice="required"`.
  - No monitorability headline. A cross-agent rate is undefined (Fable's channel table; debate R4/S4).
- **7.7 Anti-leader appeals and funding refusals.**
  - G20 d096, G18 d335–344, G16, G14 d209.
  - Debt fixes the creditor, so estates do not reveal chosen beneficiaries.
  - No coalition, cartel or kingmaking is identified in the checked record. That is a bounded absence.

**Exhibits:** F7 multi-panel chronology (G13, G4/G6, G11, G18). I argue against Astra's single-case F8 in the main text (debate S5). T6.

**Citations:** `bianchi2024negotiationarena`, `shi2026cheaptalk`, `shi2026agentslie`, `li2026arena`, `golechha2025amongus`, `ren2025mask`, `elzou2025moloch`, `turpin2023unfaithful`, `baker2025monitoring`, `korbak2025monitorability`.

**Alternatives** for every case:
- recipient prior motives;
- arithmetic errors;
- stale context;
- channel conflicts;
- that "final" is ordinary bargaining posture (G7 d42).

**Transition.** "Several results above changed once we saw how responses were processed. We gather those conditions in one place."

## 8. What execution and records change (compact)

**Argument.** Interface conditions explain particular results. They are not the subject. One section plus one table, each item linked to the analyses it qualifies:
- Opus refusal → action-only (M1);
- the even-building validator × plan encoding × retry budget;
- Grok's received-call conflicts;
- the trade-history formatter defect (2,054 prompts, exposure not reliance);
- timeline delivery omissions;
- generated-label errors, which the audits also caught in our own extractors (R25).

**Exhibit:** T5.

**Alternative.** "These are bugs, fix and rerun." Fixing changes the treatment. The historical record must stay as run. Corrected treatments are D-tier.

**Transition.** "What, then, does this cohort say about capability and alignment?"

## 9. Capability and alignment: established, suggested, untested

**Argument.** Three columns.

**Established (A).**
- Sustained, partly competent economic pursuit: staged liquidations, reserve reasoning, timed trades, and financing sequences reaching exact targets.
- Repeated executional failures: invalid plan encodings, omitted unlocked collateral in three payable eliminations, phantom-build notes.
- Social conduct under a permissive contract: misleading framing with a recorded rationale, alongside recipients who correct premises.
- Configured-system properties that change both: refusal-recovery memory loss, received-call conflicts.

**Suggested (exploratory, labelled).**
- Proposition accuracy varies within agent and within response.
- Explanation channels sometimes disagree with applied actions, in ways that matter for outcomes (G12 d249).

**Untested here.**
- Ranking.
- Capability trend.
- Persuasion effect.
- Instruction-violation or deception rates.
- Monitor accuracy.
- Optimal policy.
- Counterfactual winners.

Place this against the literature: Arena null, Emergent Collusion positive, MASK, Safetywashing.

**Exhibit:** A7 claim-strength ladder (optional, main text).

**Transition.** "If this environment is to answer the untested questions, what must change?"

## 10. Designing long-horizon sandboxes for safety research

**Argument.** The environment already makes conduct adjudicable (Layers 1–2 of T7). Answering alignment questions needs specific Layer-3 affordances, each with a counted opportunity and a pre-specified outcome:
- commitment objects;
- private bilateral channels;
- norm treatments (T1/T2);
- engineered violation opportunities;
- monitors;
- a capability axis within a lineage;
- training interfaces.

Give the minimal design from `experiment_decisions.md` §6: tiers within at least two lineages, three norm treatments, 15–20+ blocks, replicate realizations, mixed-effects inference following Arena §4.2.

Distinguish **implemented** (replay, prefix reset, reference policies, micro scenarios) from **unimplemented** (branch API, rewards, RL adapter, training).

State the realistic-sandbox motivation without overclaiming realism. The game abstracts finance but preserves sequencing, scarcity, estates and bargaining. Those are the properties that make conduct and capability entangled.

**Exhibit:** T7 affordance ledger.
**Citations:** `shi2026emergentcollusion`, `lynch2025agentic`, `schoen2025antischeming`, `li2026arena`, `piatti2024govsim`, `golechha2025amongus`.

**Transition** to Limitations.

## 11. Limitations and threats to validity

1. **Sample.** One roster, five blocks, one realization per cell, and four providers with differing response conditions.
2. **Construct.**
   - Developed rent is not return.
   - Completion is not trade value.
   - Accessible finance excludes trade help.
   - Local feasibility is not survival.
3. **Channels.**
   - Visibility differs by model (Sol's summaries; encrypted fields; Opus action-only).
   - Explanations are not intent.
   - Received-call conflicts are unlocalized.
4. **Review.**
   - Model-based extraction and coauthor adjudication.
   - No human annotation, inter-rater statistic or preregistration.
   - Codebooks post hoc.
   - Selected corrections show the labels can be wrong.
5. **Rules.**
   - The declared variant (inheritance) shapes concentration.
   - Prompt-permitted deception shapes the social findings.
6. **Recency.** Competitor preprints are days or weeks old. Versions are pinned in the bib.
7. **External validity.** A game, not markets. LLM-only.

## 12. Conclusion

Restate the thesis and the three things a reader should take away:
- legal-alternative audits change interpretations;
- economic success here runs through deployment, finance access and estates, with execution failures alongside;
- competitive language misled and was corrected in specific, inspectable ways under a permissive contract.

Finish with the research agenda (§10).

## Appendices (planned)

- A. Full rules variant and prompt text.
- B. Channel availability per agent (A2).
- C. All 20 trajectories (A8).
- D. Elimination table (60 rows) and default-plan table (66 rows).
- E. Social case dossiers with packet line hashes.
- F. Full related-work comparison (`comparison.json`) with the inspected sections.
- G. Cost and usage (A1).
- H. Provenance manifests and regeneration commands.
- I. Review provenance (extractor identities; catalog; fixed sample).

## Open dissent and unresolved choices (for integration)

- **Single-case versus multi-panel social exhibit.** Astra's F8 is single-case; I argue for multi-panel. Unresolved until Astra replies.
- **Model colour encoding in the spending scatter.** I argue against it (ROI reading; CVD).
- **Naming.** "Gemini" versus "Argon": following Astra, use "Gemini (Argon)" at first mention.
- **Placement of the cost and usage table.** I place it in §5 as context. Peers may prefer an appendix.
- **Title noun.** "Benchmark" only after release validation (steps 17–18).
