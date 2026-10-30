# Initial position (written before opening charter.md, prior reviewer reports, or coauthor/final_review folders)

Reviewer: Fable (novelty / strongest-comparator focus). Date: 2026-10-29.
Basis: full read of `baseline/monopolybench-first-draft/sections/*.tex`, `references_source.bib`, `evidence_map.md`, `README.md`, `verification.json`, and the four figure PNGs. Nothing else yet.

## What the paper claims to be

A 34-page exploratory paper on twenty four-player Monopoly games between four frontier configurations (GPT-6.1 Sol, Gemini 4 Argon, Claude Opus 5.5, Grok 4.7) via OpenRouter. The stated contribution (intro, last paragraph) is threefold: (1) an integrated economic+social trajectory account, (2) an "exact-prefix adjudication protocol" applied both to agents' claims and to the authors' own research labels, (3) system validation plus requirements for a future norm-explicit evaluation. The paper explicitly disclaims novelty for replay, multiplayer economics and fact-checking of agent communication.

## My first-read judgment of the central idea

The paper is unusually honest and unusually hedged. Almost every paragraph ends with a "does not establish" clause. The honest reading of what knowledge changes:

1. **Demonstrated (strong):** Frontier agents in a long-horizon economic game lose economically available actions through *response-resolution mechanics* rather than through judgment: 61/61 Opus defaulted build plans were affordable and legal when reordered; 3/60 eliminations were payable by a legal sequence; 139 Grok tool-call/content conflicts including a bankruptcy declaration the content argued against. This is the most defensible and most transferable finding, and it is a finding about *harness + model as deployed*, which the paper correctly frames.
2. **Demonstrated (moderate):** A closed trade is not evidence of persuasion. Five chronologies show recipients correcting false premises and still accepting on their own terms. This is a methodological caution with a small n, but the chronologies are concrete.
3. **Demonstrated (infrastructure):** Full replay of 20 games, memory reconstruction for 6,989 windows, exact-prefix branching. This is engineering validation, not a scientific result, but it is the enabling condition for (1).
4. **Not demonstrated, and the paper says so:** any capability–alignment relationship, any model ranking, any deception rate.

## Where I expect the strongest-comparator attack to land

- **AgentMonopoly (Wu et al., 2610.29330):** same game, deterministic engine, legal-action list, replay, open code (Apache-2.0), 8 open-weight models with within-family size tiers, persona control, 120–140 games. On paper it already does "Monopoly + LLM + replay + behavior patterns" with *more* games, *a capability axis within families*, and *public code*. The draft's defence is: (a) frontier models vs. 8B–32B, (b) uncapped bankruptcy vs. 150-step cap, (c) liquidation phase vs. cash-negative elimination, (d) deception permitted vs. public/action contradiction prohibited, (e) exact-prefix auditing of specific claims. I need to verify each of these against the primary source. If AgentMonopoly also exposes per-turn records and replay, then "exact-prefix audit" is a *use* of infrastructure both have, not a new capability. The genuinely distinct element is the *audit of the evaluator's own labels*, and the *attempt-level provenance* (refusal chains, action-only retry, tool-name conflicts). I must check whether AgentMonopoly records attempts or only applied actions.
- **Vending-Bench Arena communication paper (Li et al., 2608.14825):** 2,583 emails, 20 runs, LLM judge + deterministic checks against simulator records, promise follow-through. The draft says "state-checked communication" is not new. The draft's distinction is exact historical menus + legal financing sequences + per-attempt resolution + explicit deception permission. I need to check whether Arena is public, whether its runs are replayable, and whether its "deterministic checks" are equivalent to engine-grounded truth.
- **DECE (Zhang et al., 2610.35773):** complete model–harness configurations, matched harness studies, replay, legal interfaces. If DECE already does controlled harness comparisons, then MonopolyBench's "configured participant" framing is adopted, not contributed. The draft admits this. Check whether DECE excludes dialogue (draft says yes).
- **FinBoardBench (Hu et al., 2605.27896):** Monopoly liquidity/investment summaries. Draft says its bankruptcy sells buildings. Verify.

## Candidate findings I already see (unlabelled by anyone else yet)

- **F-A (presentation/underclaim):** Figure 2 left panel shows first-window build rates by model: Sol 16/17, Gemini 17/18, Opus 7/15, Grok 3/13. The prose reports only the aggregate 43/63 and the right-panel 34/42 split. A reader will see a 3/13 vs 17/18 gap in the figure and find no sentence addressing it. Either state it with the Opus-default and Grok-conflict explanation attached, or remove the per-model facet. The current state is the worst of both.
- **F-B (central-idea challenge):** The "contribution" is defined as a protocol, but the protocol is never stated as a procedure a reader could apply elsewhere. "Exact-prefix adjudication" is described by example. A reader cannot tell what counts as a "declared local endpoint", how a branch is chosen, or how to report it. The abstract says the paper "contributes ... an exact-prefix audit procedure"; the methods section describes it in one paragraph (§Local legal-sequence tests). For this to be the contribution, it needs a boxed procedure and a statement of what it can and cannot adjudicate.
- **F-C (external validity / rule-engine quirks):** Intact creditor inheritance of buildings, non-auction of bank-returned deeds, `$111` redemption on a `$100` principal (float ceiling), mortgaged-deed trade interest rounded up, no new trade during liquidation, no management window while in jail. The paper declares these but the 54/60 creditor-is-winner statistic and the 57/60 developed-rent eliminations are plausibly *driven* by the inheritance variant. The paper says "not a causal estimate" but a reviewer will ask: how much of the economic picture is an artifact of a non-standard rule? The float-ceiling redemption bug is a benchmark defect, not a "rule"; it should be labelled as such.
- **F-D (size/dependence):** 20 games, 5 seeds, 4 rotations — effectively 5 independent seed blocks. The paper says this clearly. But 34 pages of analysis on 5 blocks invites the question whether the length is justified. The exploratory framing is defensible only if the paper is positioned as a methods + case paper, not a benchmark result paper. The title ("Auditing Economic Capability and Social Conduct") supports this, but "MonopolyBench" as a *benchmark* name implies a scoring instrument that is never delivered.
- **F-E (comparator precision):** The draft's related-work claims about AgentMonopoly (150-step cap, net-worth winner, temperature 0, cash-negative bankruptcy, prohibits public/action contradiction, 140 vs 120 games) and Arena (2,583 emails, single-author label check, not redistributed) are specific and falsifiable. Each must be checked against the primary source.
- **F-F (opportunity accounting):** The paper's strongest conceptual move is distinguishing "current menu" from "reachable legal sequence" (e.g. mortgage becomes available only after sales). If AgentMonopoly / DECE expose only current legal menus, this is a real contribution to *opportunity accounting* and deserves to be named as such rather than buried.
- **F-G (Opus refusal condition):** 1,605/1,696 Opus decisions under action-only recovery. This is both a confound and an interesting observation. The paper handles it honestly. But the Opus row in every table is effectively a *different harness condition*, and Table 1 presents it as a peer configuration. Each exhibit should mark the Opus row.
- **F-H (reproducibility):** No public release, no external replication, repository not named, model coauthor streams share families with evaluated participants. Paper says all this. Still a reproducibility ceiling.

## Preliminary advisory score (to be revised after verification)

- Significance: 5/10. Real but narrow; the transferable lesson is about harness-induced capability loss and evaluator audit.
- Soundness: 7/10. Claims are carefully bounded; the risk is comparator claims and rule-artifact framing.
- Novelty: 4/10 pending comparator verification. The infrastructure is not novel; the two-sided audit (agent + evaluator) and attempt-level provenance might be.
- Clarity: 5/10. Honest but exhausting; 34 pages, hedges everywhere, contribution stated as a protocol never boxed.
- Reproducibility: 4/10. Locally verified, not released.

## What I will do next

Verify every comparator claim against primary sources; inspect AgentMonopoly repository for attempt logging, replay, prompt text; check Arena paper for public availability and the "single-author label check" claim; check DECE for dialogue exclusion and replay; check FinBoardBench bankruptcy rule. Then read charter and prior reviews, mark inherited vs checked, and run read-only analysis on the per-model first-window split and rule-artifact exposure.
