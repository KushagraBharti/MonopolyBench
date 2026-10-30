# MonopolyBench: integrated paper outline

Prepared 2026-10-29 from overlapping full-scope work by Astra, Sol, Opus and Fable. This is the step-14 outline, not the manuscript. Individual proposals and debate remain under each researcher's directory. Astra integrated the final structure and reconciled the generated figures; the exact final wording below has not undergone another four-person manuscript review. No venue or page limit is assumed.

## Working title and central argument

**Preferred working title:** *MonopolyBench: Studying Long-Horizon Agent Capability and Social Conduct in a Competitive Economy*.

**Alternative emphasizing the research program:** *MonopolyBench: A Replayable Sandbox for Studying Agent Capability and Alignment*. Use this only if the abstract immediately distinguishes the current descriptive results from future alignment experiments, and the release package is complete.

The paper asks how agents sustain goal-directed economic behavior and how they conduct themselves toward other agents over the same long trajectory. MonopolyBench provides persistent resources, competing interests, consequential negotiation, constrained financing and inspectable state. The current cohort supports economic profiles and source-grounded social explanations. Exact historical-prefix tests expose when nominal assets are inaccessible, an apparently skipped investment was a discarded plan, or a generated behavioral label was wrong. These findings inform how to design and audit long-horizon safety sandboxes. They do not establish how alignment changes with capability growth.

Keep three research questions throughout:

1. **Capability:** How do the evaluated systems acquire, negotiate, finance, develop, liquidate and preserve economic position across complete games?
2. **Conduct:** What do they claim, conceal, promise, coordinate and revise, relative to their actual instructions and counterparties' delivered information?
3. **Evaluation design:** Which records and actionable opportunities allow these behaviors to be interpreted reliably, and what additional experimental design is needed for capability–alignment comparisons and training?

Contributions should be concrete: the environment and replayable research records; bilateral and longitudinal analysis of a complete cohort; exact-prefix legal-alternative auditing with demonstrated scope; and norm-explicit social chronologies that preserve conflicting channels and counterexamples. Shared infrastructure is acknowledged rather than claimed as first. Release status must be stated honestly until steps 17–18 finish.

## Abstract plan

Open with the joint capability/conduct question. Introduce the persistent four-player economy and the 20-game, five-seed, four-rotation cohort. Describe the analysis method in one sentence. Include one economic result and one social contrast, plus the result that applied non-building can arise through different execution paths. End with the supported evaluation-design implication and the boundary of the current study.

Candidate economic numbers are the 60-elimination financing split or the eight-case development residual; use one, not a list of all totals. The social result should pair misleading framing with recipient correction or a prior motive. Do not lead with a model leaderboard, a deception rate or a generic claim that agents become misaligned as they improve. Final title and abstract are written after the manuscript, in step 15.

## 1. Introduction: capability and conduct with delayed consequences

Develop the motivation from Vending-Bench's economic autonomy question and the user's broader capability/alignment ambition. Show why competing agents create endogenous opportunities: an offer changes another player's assets and financing, a cash payment can fund a rival's development, and a debt can transfer a portfolio. The environment's value is controllable complexity and inspectability, not a claim to reproduce the whole economy.

Introduce the inference problem with two compact contrasts. An applied END can represent a reserve preference, a rejected build followed by default, or a received action that disagrees with its accompanying text. A settled deal can coexist with explicit rejection of its sales pitch. These examples connect economic and social evaluation from the beginning.

Place the work alongside AgentMonopoly, FinBoardBench, Vending-Bench Arena and its communication study, Cattle Trade and DECE. Capability/alignment evidence from Arena, MASK, Safetywashing and Emergent Collusion motivates a designed future comparison; it is not one uniform trend that our win counts can extend. End with the three RQs and the specific contributions.

**Evidence/exhibit:** [F1 evidence chain](astra/exhibits/f01_evidence_chain.png), the residual audit and G13 chronology. **Alternative:** game familiarity, declared variants and wrapper conditions may explain behavior. **Transition:** specify the environment, instruction contract and evaluated configurations before interpreting any result.

## 2. Environment, instructions and evaluated agents

### 2.1 Economy and rule variant

Explain purchases, auctions, trades, complete color groups, even building, finite houses/hotels, mortgages, jail management and bankruptcy in student-readable terms. Describe the actual variant: developed property can pass intact to creditors; debt-time sales can unlock mortgages; a hotel downgrade requires bank houses. Separate mortgage interest on a traded deed from the creditor-inheritance rule. Avoid an unqualified claim of classic or standard Monopoly.

A compact rule-and-implication table should connect each relevant mechanic to the analysis it enables. For example, selling buildings before mortgaging makes finance a legal sequence; inherited development complicates attribution of rent to own construction; jail limits access to management. State rules from the frozen engine and saved configuration rather than recollection of tabletop play.

### 2.2 Information and normative contract

Describe state, legal menus, trade histories, 20-entry public timeline and ten private-note memory entries. State the actual instructions: pursue victory through legal actions, public deception permitted, private notes requested to reflect true reasoning. These define different questions. Engine rejection prevents applied illegal moves but does not prove no invalid attempts. Public bluffing is not automatically instruction misalignment; false private text does not independently establish dishonest intent.

Include the three-environment normative-contract table developed by Opus: our contract, AgentMonopoly's bluffing-plus-say/do constraint, and Arena's externally coded communication taxonomy. Keep contractual permission distinct from an external normative judgment. An explicitly declared norm can support descriptive adherence without randomization; causal comparison needs more design.

### 2.3 Configured participants and action resolution

Introduce full model identifiers once, then Sol, Gemini (Argon), Opus and Grok. Use seats 1–4 consistently. Explain that inference settings, memory, tool choice, response handling and retries are part of the evaluated system. Provider-native “medium” effort does not equalize compute. Opus's recorded ToS refusal is not a moral refusal of deception; its cause remains unlocalized. Grok uses required tool choice; disagreement between received channels remains a diagnostic, not provider blame.

Place a compact condition table here and detailed counts in the supplement. Explain attempt versus decision units, authored versus synthetic memory and the unused configured fallback model. This is enough setup to make later economic profiles interpretable without letting interface details dominate the introduction.

### 2.4 Artifact and replay contract

Explain snapshots, events, legal decisions, applied actions and per-attempt prompt/response records. Applied actions remain authoritative. Distinguish full event replay, memory reconstruction, exact state reset, local legal-alternative tests and fresh policy continuation. The system's existing reset/recovery components support branching at tested prefixes; no packaged RL adapter, reward interface or training result is claimed.

**Evidence/exhibits:** rule table; condition/channel table; [Opus affordance ledger](opus/exhibits/affordance_ledger.md). **Citations:** AgentMonopoly, DECE, HAL, WebArena, OSWorld, τ-bench, AgentDojo. **Transition:** these records are the measurement instrument; the cohort and estimands determine what it measures.

## 3. Study design and analysis protocol

### 3.1 Frozen cohort and dependence

Report 20 complete games, 80 player-games, five seeds with four rotations, 50,918 events, 6,989 decisions and 8,679 attempts. Each participant occupies each seat five times. Show all outcomes in [F2](astra/exhibits/f02_seed_rotation_winners.png). Shared raw dice do not give identical opportunities because the uses and recipients of draws diverge.

Two treatment fingerprints coincide with games 1–4 versus 5–20. The inspected commit diff concerns concurrency plumbing, UI, documentation and tests, with no engine, prompt, resolver or model-client file change. Neither a behavioral effect nor its absence follows from the source diff. The refusal-share shift at that boundary is a coincidence in the data, not an identified cause.

Avoid independent-decision significance tests and chance-model p-values that ignore block structure. Descriptive counts and a transparent outcome grid are more defensible than a universal ranking from five blocks. Report horizon as game turns, decisions, attempts and available token accounting; METR's human-time horizon is a different construct.

### 3.2 Economic units and time windows

Define deed acquisitions separately from group completions; distinguish final acquisition route from the routes of constituent deeds. Specify trade author, original initiator and responder. Define first actual management turn, entry buildability, later buildability and elapsed delay. Keep whole trajectories alongside conditional responsiveness because prior play creates access and funding.

Define a spending unit as one game/player/color group with any own house or hotel construction. Separate whole-game paid developed rent from receipts after first own expenditure, unpaid debt and inherited estate value. Define self-financing at a specified debt as an executable own-action sequence, excluding assumed trade assistance. These definitions belong in a concise table, with edge cases and scripts in an appendix.

### 3.3 Social evidence and review

For each proposition or assurance record: subject/time, factual status, speaker observation, available channels, prior and current recipient exposure, applied action, later consequence and alternatives. A logged utterance is not necessarily delivered; a past exposure can matter even after it leaves the current window. Keep intent unresolved where error, conflict or missing evidence remains. Do not turn a fluent summary into privileged ground truth about the agent.

Describe full first-pass extraction, overlapping 614 catalog items including 21 historical entries, all 20 trajectories and the fixed 240-decision original-bundle sample. Preserve Sonnet/Haiku attribution for the public pass. Four model coauthors are not human annotators, and iterative debate is not independent blind replication of every assertion. Definitions developed during exploration are not preregistered. The sample frame limits prevalence inference.

### 3.4 Exact-prefix legal-alternative audits

Restore a saved decision prefix, verify the historical event match, execute a specified legal sequence for the acting player, and stop at a defined local endpoint. Report whose action opportunity is used and any altered condition. A legal existence proof is not an optimal policy, a predicted opponent response or an alternative winner. Historical suffixes cannot simply be replayed unchanged after a divergent state.

Show validation of both model claims and our own extracted labels: reordered builds, accessible financing, the genuine hotel lock and a fabricated redemption restriction refuted by the engine. Separate structural integrity, accounting correctness, semantic validity and causal identification.

**Evidence/exhibits:** method diagram, definitions table, phase-2 source/hash ledger. **Citations:** AgentBoard, HAL, Arena communication study, MACHIAVELLI, SOTOPIA, explanation-faithfulness literature. **Transition:** follow the economic life cycle before interpreting social tactics within it.

## 4. Economic behavior across complete games

### 4.1 Acquisition, bargaining and winning routes

Begin with deed routes: 475 direct, 72 auction, 207 trade and 397 inherited acquisitions. Then distinguish 209 complete-group episodes, including 69 terminal inherited completions with no future opportunity. Do not mix these denominators. G14 Sol and G15 Gemini demonstrate actual wins without accepted trades.

[F3](astra/exhibits/f03_negotiation_profiles.png) reports proposing-turn propensity and proposals per proposing turn, with absolute counts and eligible-decision rates in its table. Gemini's low initiation coexists with recipient bargaining. Across 113 settlements, group completion benefits neither/one/both sides in 60/43/10 cases. In 44 the final terms are authored by the other party than the thread initiator. These are consequences and roles, not a complete welfare score.

Pair acceptance with rejections that would complete the recipient's group but finance a rival. Discuss cash retained, mandatory transfer interest and timing. Use original terms and before/after state, not a guessed intrinsic property value.

### 4.2 Development and execution

[F4](astra/exhibits/f04_opportunity_and_deployment.png) shows 43/63 trade-completed groups developed in the first actual management turn and 34/42 among entry-buildable groups. Its visible residual is essential: three defaults, three received END/content conflicts and two consistent ENDs with stated reserve rationales. These are record classifications, not three causally lost builds or a repaired willingness rate. The all-63 resolution table distinguishes never-legal windows as well.

Use [F7](astra/exhibits/f07_build_recovery.png) or a compact table to explain all 61 Opus defaulted multisets that are executable after interleaving. Successful retry may change quantity: 12/18 Gemini and 5/25 Sol recoveries do; 0/5 Grok do. Preserve valid chosen holds as counterexamples. Access choices, defaulted actions and stated restraint all belong in capability analysis, but they must not be assigned the same mechanism.

### 4.3 Investment, income and inheritance

[F5](astra/exhibits/f05_spending_and_receipts.png) follows 103 spending units: $103,450 own outlay, $93,000 whole-game paid developed rent and $92,550 after first own spend. Forty units collect zero developed rent; 26 also cause no creditor elimination. Explain exposure, salvage, deterrence, unpaid debts and inherited development before interpreting this pattern. Do not label the ratio ROI.

Use [Sol's G19 successive-owner exhibit](sol/exhibits/s3_g19_dark_blue.png) as the concrete trajectory; [F9 cash paths](astra/exhibits/f09_cash_trajectories.png) provides trade-free contrasts. Of 58 winner spending groups, 34 contain an inherited deed at first own expenditure, but only 30 first complete through an estate. Eventual winners are creditors in 54/60 eliminations, including 35/40 nonterminal ones. These characterize concentration under the declared variant, not a causal inheritance advantage.

### 4.4 Financing, liquidation and finite stock

[F6](astra/exhibits/f06_elimination_financing.png) shows all 60 eliminations: 56 below even a generous upper bound; three with a legal current-debt payment sequence; one hotel lock with $440 accessible against $750 owed despite $1,310 nominal equity. G12's received declaration contradicts its accompanying sales recommendation, so the three payable debts do not share one reasoning mechanism. Include successful staged liquidation as a counterexample.

[Fable's stock grid](fable/exhibits/house_stock_grid.png) records nine games reaching zero houses and reconciles all 6,989 delivered bank states. Zero stock is not proof of thwarted demand. Distinguish direct build restrictions, costly reallocation, earlier management workarounds and the later G7 debt phase. Local finance statements never become claims about a changed winner.

**Transition:** the transactions that move these resources also carry claims, assurances and appeals. Economic consequences alone do not identify how their language worked.

## 5. Social conduct during economic competition

This section should have comparable analytical depth to the economic section, with original source references and meaningful contrasting cases rather than a short anecdote box. Social evidence is not restricted to dishonesty: conditional cooperation, selective bargaining, anti-leader appeals and changed plans all matter.

### 5.1 Misleading framing and recipient response

[F8](astra/exhibits/f08_social_chronology.png) uses three contrasts. G13 places the buyer's earlier d251 $130 counteroffer and recorded solvency rationale before the seller's d252 omission and the d253 $200 acceptance. The $130 route is legally sufficient with existing collateral. The pitch is delivered; settlement follows; a $70 persuasion effect is not identified.

G19 shows explicit premise correction with acceptance, while the proposer's own call includes an abort instruction. G11 shows a transient false echo, verification and rejection within the recipient's record. G4 and G6 extend the dossier with prior correct knowledge, public concession and correction-with-settlement. These cases support proposition-specific statements and forbid a general immunity or absence-of-uptake conclusion.

### 5.2 Offers, assurances and changed plans

Analyze G18's standing $250 offer, later invocation and withdrawal after intervening rent and liquidation. Distinguish a feasible offer from an irrevocable promise and identify conditions, expiry and actual reliance. Costly reliance or dishonesty at inception is not established. Contrast free-form bargaining posture, explicit future assurances and structured settlements; they impose different evidentiary requirements.

### 5.3 Cooperation, opposition and third-party effects

Trace anti-leader appeals and refusals to fund rivals, including occasions when the speaker continues self-interested trade. Evaluate whether a proposal became an agreement and whether the agreement was acted on. No cartel, binding coalition or deliberate kingmaking is identified in the adjudicated current-cohort cases. This is a bounded finding, not proof of universal absence. Bankruptcy's creditor is fixed by the debt, so an estate recipient alone cannot reveal a chosen beneficiary.

### 5.4 Disclosure and conflicting channels

Include the G20 private-note text appearing in a public field and recipient recognition. Preserve source uncertainty. Use the Grok name-conflict count as context, with 15 equal parsed argument objects versus five identical serialized substrings. Separate those records from ordinary changes of plan and the behavior of external monitors. Missing private text, provider summaries and selected response conditions have different detection opportunities; no cross-model deception-rate table follows from their raw counts.

**Citations:** Arena study, NegotiationArena, AgentMonopoly, SOTOPIA, the two workshop promise papers, Empty Commitments v2 and Who May Release. **Transition:** these findings expose requirements for the evaluation instrument and for future alignment experiments.

## 6. What the sandbox makes measurable—and what remains untested

Combine instrument validation and the alignment agenda in one substantial section. Summarize the response-policy mechanics, the 2,054 initial prompts carrying at least one trade-history defect manifestation, and timeline omissions. State their demonstrated consequences and scope without attributing every later decision to them. Explain why original-record and engine checks also corrected the researchers' labels.

Use a three-layer affordance ledger: implemented environment features; analyses actually performed; unimplemented experimental/training interfaces. Exact reset and local branching are implemented and tested at stated prefixes; full-prompt equality beyond memory, provider suffixes, general rollout termination, RL rewards/training and real-world transfer are not thereby demonstrated. One reference-policy rollout required truncation, so bankruptcy termination is an observed property of this cohort rather than a universal guarantee.

Specify a prospective capability–alignment study: fixed norms with genuine opportunities to comply or violate; an independently measured capability axis or within-lineage tiers; controlled prompts, memory, budgets and response handling; matched situations and repeated policy continuations; held-out assessment of utility and norm adherence. Examples include truthful financial disclosure, protected information, transaction authorization and commitments with a defined release authority. No scalar should silently trade all violations against profit.

Explain what new experiments would answer and keep them outside current results. The current corpus can motivate and test the measurement machinery; it cannot supply a capability-growth trend or training benefit. See [experiment decisions](experiment_decisions.md).

## 7. Related work and limitations

Use the [literature review](literature_review.md) throughout the introduction/methods and collect a concise comparison here if the manuscript reads better that way. A compact table should compare environment, norm, economic mechanics, observation, evaluation unit and verification method. “Not reported in inspected sections” is not a negative feature assertion. Keep version and repository discrepancies visible in the supplement.

Limitations: one roster and five blocks; declared game variants and possible prior Monopoly familiarity; endogenous opportunity and survival; unequal response/channel conditions; no human gold-standard semantic annotation; exploratory definitions; dependence among groups/decisions; selected case studies without population deception rates; no direct real-world safety transfer, human baseline or RL result. Discuss these limits alongside what the environment genuinely allows a researcher to check.

## 8. Conclusion

Answer the three RQs at the demonstrated level: full economic paths reveal different acquisition, financing and deployment patterns; social chronologies connect bargaining to consequences without collapsing explanation into intent; precise records and legal-sequence tests materially change interpretations. End with a concrete research direction for controlled capability/alignment work, not a claim that the relationship has already been measured.

## Appendix and drafting gates

Appendices: complete configurations/rules; channel availability; all-game profiles; definition/scenario tests; exact-prefix proof traces; social dossiers with attempt/channel provenance; stock/dice-use traces; cost and usage with missingness; review provenance and correction history; versioned primary-source comparison; reproduction instructions.

Before step 15, use this outline and the frozen exhibit captions. Keep the public artifact release, clean-environment reproduction and final PDF checks as steps 17–18. Do not repeat canonical games merely to increase sample count. If a stronger claim enters the manuscript, consult its specific evidence gate rather than silently borrowing support from the current descriptive results.
