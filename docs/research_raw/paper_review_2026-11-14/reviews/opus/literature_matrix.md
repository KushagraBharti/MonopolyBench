# Literature and comparator matrix (Opus, 14 November 2026)

## Access method

All online sources were read through the session's web-fetch tool, which returns a *model-generated summary* of the page. Where I asked for quotations, short passages were returned verbatim, but they still pass through that summariser. "Depth" below therefore means what I could inspect through that channel:

- **abstract page** — the arXiv abstract or venue landing page.
- **HTML full text (partial)** — the arXiv HTML rendering, queried for specific sections. Long pages were truncated, typically after about 100k characters.
- **code** — raw repository files.

I did not download or execute any code from these sources. I make no novelty claim from absence: when a search did not find something, that is recorded as "not found", not as "does not exist".

## Planning, reachability and infeasibility

| Source | URL / version | Depth read | Methods relevant here | Bearing on this paper | Remaining uncertainty |
|---|---|---|---|---|---|
| ACPBench (Kokel, Katz, Srinivas, Sohrabi), AAAI 2025 | arxiv.org/abs/2410.05669 v3 (rev. 27 Feb 2026); project page ibm.github.io/ACPBench | Abstract + HTML full text (task definitions; first ~100k chars) + project page | 7 tasks over 13 PDDL domains. Hand-written templates render them as natural language. Action Reachability: whether an action "can be made applicable from the given state through some sequence of actions". Single-turn question answering (boolean/MCQ), 10 items per domain per task. No acting agent. | The construct "resources/actions that become available after other actions" is established. MonopolyBench differs: an acting agent, natural states, an irreversible stop, and its own money at stake. | Exact item totals are not stated; I did not read the results tables. |
| ACPBench Hard, ICLR 2026 | arxiv.org/abs/2503.24378 v2 (27 Feb 2026) | Abstract | Generative (open-ended) versions of the tasks plus Next Action. "Validation algorithms for each task." | Generative reachability with validators exists. | Validator details and any action-reachability results not read. |
| LLMs Still Can't Plan; Can LRMs? (Valmeekam, Stechly, Kambhampati) | arxiv.org/abs/2409.13373 v1 (20 Sep 2024); HTML | HTML section "Performance on Unsolvable Instances" | 100 Blocksworld goals made unsatisfiable. o1 explicitly flags 27% (BW) and 16% (Randomized Mystery BW). False impossibility: "11.5% of instances are incorrectly claimed to be impossible" (Randomized Mystery BW); 0% on BW (Table 3). | False-infeasibility judgments on solvable problems are documented, so their occurrence is not novel. | Venue of this preliminary report not checked. |
| PlanBench (Valmeekam et al.), NeurIPS 2023 D&B | arxiv.org/abs/2206.10498 v4 | Abstract page only this round | Extensible benchmark of planning and reasoning about change. Obfuscated/randomized "Mystery" domains are confirmed indirectly through the o1 paper. | Already cited by the paper for planning versus retrieval. | Ref B's "~26,000 prompts" not verified. Full test-case list not re-read. |
| AutoPlanBench (Stein, Fišer, Hoffmann, Koller) | arxiv.org/abs/2311.09830 v2; coli-saar.github.io/autoplanbench | Search snippets + project page summaries | Automatic PDDL-to-natural-language conversion; 12 domains. Compares plan generation with ReAct-style interactive action choice. Dead-end (irreversible) domains are hard. Later version: "Automating the Generation of Prompts for LLM-based Action Choice in PDDL Planning". | Interactive versus whole-plan generation is not new. | Venue of the later version not verified. Detailed results not read. |
| The Menu Is an Execution Prior (Yan, Lin, Wang) | arxiv.org/abs/2609.09395 v1 (8 Sep 2026), comments "Accepted to EMNLP 2026 Main" | Abstract page | Learned pre-execution tool menus, coverage plus producer-before-consumer ordering. ToolBench online success rises from 0.737 to 0.898. | Menu composition and order affect agent success. Its menus are fixed before execution: no runtime unlocking, feasibility judgment or giving up. | The claimed same-candidate order ablation is **not verified** from the abstract. |
| LLM-Modulo position paper (Kambhampati et al.), ICML 2024 | proceedings.mlr.press/v235/kambhampati24a.html | Abstract page | LLMs as approximate knowledge sources inside a generate–test loop with external model-based verifiers. | A verifier that supplies routes is an assisted condition, not a contribution. | Full text not re-read. |
| Reasoning or Reciting? (Wu et al.), NAACL 2024 | aclanthology.org/2024.naacl-long.102 | Abstract page | Default versus counterfactual task variants across 11 tasks. Consistent drops under counterfactual conditions. | The only design that separates recall of the standard release rule from rule application. The current paper cannot make that separation. | Counterfactual-comprehension-check details not re-read. |
| Do LLM Agents Execute the Plans They Declare? (Oota, Herrera, Cabot Sagrera, López de Prado, Khan) | subbareddy248.github.io/projects/declaration-gap-site/ → arXiv 2609.38108 (preprint) | Project page | Declared planning mode routed to matching executors. Structural plan adherence: Plan+ReAct preserves the declared structure in only 22–45% of trajectories. | Declared-plan versus execution is an active topic. This paper's statement–action analysis must be positioned against it. | The arXiv page itself was not opened. Exact date unknown. |
| Unpropagated refutation / atomic chess (ICML 2026) | icml.cc/virtual/2026/67788; icml.cc/virtual/2026/78907 (Co & Konuganti, "Probing Policy-Level Memorization in Reasoning LLMs via Atomic Chess") | Virtual-site abstracts | 200 prior-conflicting positions, rule given verbatim in the system prompt. The agent reasons that a move violates the rule, then submits it via its tool call. | Grok's within-call contradictions (G9 d194, G20 d273, G12 d249) belong to this family. A statement–action gap is not new. | Title and authors of 67788 not captured. Full papers not read. |
| How Memory Management Impacts LLM Agents (Xiong et al.), ACL 2026 | aclanthology.org/2026.acl-long.27 | Abstract page | Add/delete memory operations; experience-following; error propagation from stored experiences. | Any carried-note study (Ref B/D) must cite it. "Memory errors carrying forward" is not new. | No quantitative results read. |
| MafiaScope (Karpov, Grigorenko, Ayuyev) | arxiv.org/abs/2607.10645 v3 (30 Oct 2026) | Abstract page + search snippets | Non-invasive belief probes on conversation copies; "counterfactual replay branches from saved states"; probe repeatability. | Saved-state replay/branching is a method precedent, not a contribution. | The "672-game" corpus figure was **not found**. A snippet mentions "200+ cross-model games". |
| PokerBench (Zhuang et al.), AAAI 2025 | arxiv.org/abs/2501.08328 v2 | Abstract page | 11,000 poker spots. Higher-scoring models win more in head-to-head play. | Ref D's validation template. The analogy is weak for liquidation: stop errors here are rare (3/131 payable). | Gameplay-validation details not read. |

## Economic and agent-environment comparators

| Source | URL / version | Depth read | Verified facts | Bearing | Remaining uncertainty |
|---|---|---|---|---|---|
| AgentMonopoly (Wu, Li, Marsault, Huang, Cheng) | arxiv.org/abs/2610.29330 v2 (22 Oct 2026); HTML; github.com/SuELS-Group/Agent_Monopoly (README, `backend/rules.json`, `backend/engine.py`, `backend/agent.py`) | HTML (methods) + README + three raw code files | **Setup:** 140 games in the paper (40/40/40/20), but the README table lists 120. 8 local open-weight models; seeds 42–46; temperature 0.0 per the paper (code default 0.5, overridable). Oldenburg street names; 150-step limit; persona on P1 only; trades reported per 100 dice rolls; no statistical tests. **Code:** `agent.py` loads `rules.json` into the system prompt, and `rules.json` says "You CANNOT mortgage a property if ANY property in its color group has houses". The prompt forbids public messages that contradict the action. `engine.py` eliminates a player as soon as its balance goes negative and has no sell-building action. | Confirms both referees on "no debt rescue" and Ref B on "rules in prompt". MonopolyBench agents receive no rules, which is the design contrast to state. | Whether `rules.json` is always injected under every configuration was not traced. |
| FinBoardBench (Hu et al.) | arxiv.org/abs/2605.27896 v1; HTML | HTML (methods, Table 2, abstract) | 3 games; 9 focal models; 108 matches; fixed 3-model opponent roster; seat rotation. **Monopoly fund-raising manager** with MORTGAGE, SELL_BUILDING, "or bankruptcy when recovery is impossible". DeepSeek V4 Pro judge, no human validation reported. Up to 5 action-execution failures before a forced fallback. Thinking table ≈ 4/36 vs 10/36 wins (extraction garbled). Static→dynamic claim asserted in the abstract. | **Multi-step liquidation is not unique to MonopolyBench.** The distinctive feature is voluntary declaration on payable debts, the precondition for observing premature stops. | Whether "only when recovery is impossible" is enforced by the engine or is prompt text only. |
| Vending-Bench (Backlund & Petersson) | arxiv.org/abs/2502.15840 v1; HTML | HTML (methods/results) | 9 models plus one human (5 h, day 67); 5 runs per configuration; 2,000-message cap. Capital ($100/$500/$2,500), fee ($0/$2/$5) and memory (10k/30k/60k) varied. Larger memory performed worse. r = 0.167 between "Days Until Sales Stop" and "Days Until Full Memory". | Controlled variation and repeats. Ref D's "10 models" is incorrect (9 + human). | — |
| Vending-Bench 2 (Andon Labs) | andonlabs.com/evals/vending-bench-2 | Page summary | One-year horizon, $500 start, scored on final balance. Adversarial suppliers and disruptions. ~$63k reference = $206/day × 302 days (≈$62.2k) from stated assumptions. Leaderboard "±" undefined. Gemini 4 Argon #5 ($13,718 ± $3,100), GPT-6 Sol #4, GPT-6.1 Sol #6; Grok 4.7 and Claude Opus 5.5 not visible in the top 10. | Ref D's "external capability axis available today" is only partly true, and the axis is contested. | Full leaderboard ("66 more") not expanded. |
| Epoch AI review of VB2 | epoch.ai/benchmarks/vending-bench-2/review | Page summary | Rated "Flawed": the tokenizer counts encrypted reasoning, giving unequal usable context; exploitable environment. One official run each for two models inspected, and no exploits seen in them. | Supports Referee A: prominent benchmarks are not pristine controls. | Redacted exploit details. |
| Emergent Misaligned Communication (Li, Petersson, Acquisti, Bakker) | arxiv.org/abs/2608.14825 v3 (21 Aug 2026); HTML | Abstract + HTML methods (first 100k chars) | 2,583 emails; 20 runs; 13 models; 12.6% labelled misaligned. 50-email check labelled by one author, who is also the codebook author (92.0% agreement, sensitivity 0.571). Mixed-effects logistic regressions and run-level cluster bootstrap. Judges: Claude Sonnet 4.6, Gemini 3.5 Flash, GPT-5.6 Terra. Term-level prompt check on 52/58 payloads. | Population-level communication analysis versus selected incidents. Its human validation is weaker than "hand-labeled set" suggests. | No venue on arXiv. Ref D's "NeurIPS 2026" is unverified. |
| AutoVend (Shi, Li et al., StepFun) | arxiv.org/abs/2610.36980 v2; HTML | HTML (methods) | 5 LLM agents; 20 machines; 180 days; 40,000 CNY start; 3 runs per LLM; frozen world/seed. Newsvendor + order-up-to baseline: only GPT-6.1 Sol beats it (309.35k vs 210.97k CNY), in all 3 runs. Conditional pricing regret at fixed site/assortment/inventory. Early/late comparison declared non-causal. | A reference policy calibrates performance. For the sixteen necessity states, the never-quit reference's outcome is derivable from code. | — |
| Project Vend (Anthropic) | anthropic.com/research/project-vend-1 | **Not opened this round** | — | Referee A's description inherited. | Unverified. |

## Rules sources

| Source | URL | Depth | Content used | Uncertainty |
|---|---|---|---|---|
| Hasbro customer-help FAQ: owing more than you can pay | hasbro-new.custhelp.com/app/answers/detail/a_id/83/... | Page summary | Sell buildings or mortgage. Hotels sell for half cost "and are exchanged for 4 Houses". Mortgaging requires first selling all buildings in the color set. On bankruptcy to a player, the new owner must repay the mortgage or pay the Bank 10% now. | Silent on what happens to houses/hotels on bankruptcy to a player. |
| Hasbro official rules PDF | hasbro.com/common/instruct/monins.pdf | **Download succeeded, text extraction failed** (LZW/scan, no extractor available). SHA-256 64efc743…94a | — | The classic rule requiring buildings to be sold to the bank on bankruptcy to a player is recalled, **not re-verified** this round. |

## Comparators cited by Referee A but not checked this round

ReAct (ICLR 2023), Language Models as Zero-Shot Planners (ICML 2022), Embodied Agent Interface (NeurIPS 2024 D&B), Robotouille (ICLR 2025) and NegotiationArena (ICML 2024) are known to me from prior knowledge but were not re-read. LexiCon (NeurIPS 2025 D&B), Planning in the Dark (AAAI 2025) and Hybrid Monopoly decision making (IEEE TETCI 2022) were not opened. None of my conclusions depends on them. They should be read before being cited.

## Summary of what the literature changes

1. **Not novel, and must not be claimed:**
   - action reachability;
   - false impossibility;
   - interactive versus whole-plan;
   - menu sensitivity;
   - verifier assistance;
   - statement–action gaps;
   - memory error propagation;
   - saved-state replay;
   - LLM Monopoly with multi-step liquidation (FinBoardBench).
2. **Possibly distinctive, but not proven by absence.** Naturally reached multi-agent states, with:
   - a sound arithmetic necessity certificate and legal witnesses;
   - an irreversible *voluntary* stop on payable debts;
   - agents not told the rules, including undisclosed settlement variants;
   - both the decision text and the received call recorded.
3. **Design contrasts worth stating:**
   - AgentMonopoly and the atomic-chess work put the rules in the prompt; MonopolyBench does not.
   - FinBoardBench appears to permit bankruptcy only when recovery is impossible; MonopolyBench permits it anytime.
