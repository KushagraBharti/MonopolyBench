# Literature updates (checked 2026-11-10)

All checks used arXiv abstract pages, the ACL Anthology, or proceedings listings reached through web search. For most recent preprints only the abstract page was read; the manuscript cites them only for claims their abstracts state. Nothing here was taken from the critique's citations without opening the source.

## Existing baseline entries re-checked for newer versions

| Key | Version in baseline bib | Latest found | Note |
|---|---|---|---|
| `wu2026agentmonopoly` (AgentMonopoly, 2610.29330) | v2 (22 Oct 2026) | v2 | No newer version. Abstract: four model families at two sizes, persona instructions change wording and some actions, larger models do not consistently win more, five seeds per configuration. |
| `zhang2026dece` (DECE, 2610.35773) | v1 (26 Oct 2026) | v1 | 12 model-harness configurations, 480 three-player matches in the primary study; same model differs across harnesses. |
| `li2026arena` (Vending-Bench Arena communication, 2608.14825) | v3 (21 Aug 2026) | v3 | 2,583 emails, 20 runs, 12.6% labeled misaligned; misalignment rises under low inventory; no evidence capable models exploit weaker ones. |
| `hu2026finboardbench` (2605.27896) | v1 | v1 | Models favor immediate asset purchases over keeping enough cash. Used in Related Work. |
| `shi2026emergentcollusion` (2609.24967) | v2 | v2 (26 Sep 2026) | 53 pages; collusion in 94% of trajectories across 10 models in a designed verification setting. |

## Added entries

| Key | Source and version inspected | Why cited |
|---|---|---|
| `hardy2026reliability` | arXiv 2610.00651v1 (30 Sep 2026) | Complete model-scaffold systems rank reliably (0.935-0.994) while underlying-model rankings do not (0.148-0.841); supports describing configured systems. Full text not read. |
| `yang2026measurementfirst` | arXiv 2610.05830v1 (5 Oct 2026), journal ref NeurIPS 2026 Workshop LCFM | Matched controls and scorer validation, with explicitly bounded conclusions. Named by the critique; verified. |
| `kapoor2024agentsthatmatter` | arXiv 2407.01502v1 | Cost-aware, reproducible agent evaluation. |
| `chen2025cotfaithful` | arXiv 2505.05410v1 | Reasoning text does not always reflect computation; supports channel caution. |
| `cosentino2026counterparty` | arXiv 2605.16575v1 (15 May 2026) | Agents model counterparty preferences but agreements follow anchors; close to the bargaining results. |
| `liang2026supplychain` | arXiv 2608.07538v1 (29 Jul 2026) | Supply-chain bargaining vs Perfect Bayesian Equilibrium; provider identity predicts surplus division. |
| `chen2026ceobench` | arXiv 2606.18543v2 (22 Jul 2026) | Long-horizon startup management; one of the user's listed leads (Q4), verified. |
| `duan2024gtbench` | arXiv 2402.12348v2; NeurIPS 2024 proceedings listing | Critique comparator. Proceedings title says "Capabilities", arXiv says "Limitations"; recorded in the bib note. |
| `huang2025gamabench` | arXiv 2403.11807v7, comments "Accepted to ICLR 2025" | Critique comparator (GAMA/gamma-Bench); one of the user's listed leads. |
| `abdelnabi2024stakeholders` | arXiv 2309.17234v2; NeurIPS 2024 Datasets and Benchmarks listing | Critique comparator for scorable multi-party negotiation. |
| `yao2025spinbench` | arXiv 2503.12349v5 (15 Oct 2025) | User-listed lead for Q1/Q5/Q8; verified. |
| `lewis2017dealornodeal` | ACL Anthology D17-1259, EMNLP 2017 pp. 2443-2453 | Negotiation dialogue background. |
| `metafair2022cicero` | Science 378(6624):1067-1074, doi 10.1126/science.ade9097 | Language plus strategy in a multi-agent game. Bibliographic record via PubMed listing; full text not read. |
| `park2024aideception` | Patterns 5(5):100988, doi 10.1016/j.patter.2024.100988 | Deception survey. Bibliographic data via search; full text not read. |
| `scheurer2023pressure` | arXiv 2311.07590v4 | Deception under business pressure; parallels conduct at solvency points without implying the same mechanism. |
| `fish2024collusion` | arXiv 2404.00806v6 (31 Aug 2026), comments "Accepted to EC 2026" | LLM pricing collusion; Q7 context. |
| `bonjour2022monopolyrl` | arXiv 2103.00683v4, comments "accepted in IEEE TETCI" | Prior Monopoly RL work. |

## Searched, not cited

- A November 2026 search found no new Monopoly-specific LLM paper beyond AgentMonopoly, FinBoardBench and the public MonopolyBench repository.
- "Do LLM Agents Negotiate Rationally?" (arXiv 2608.14613) and ERPBench (2609.04667) appeared in search results. Not opened; not cited.
- "Is Anyone Enforcing the Cartel?" (arXiv 2610.28787, RL-trained market agents) appeared in search. Not opened; not cited.
- BargainArena / utility-feedback bargaining (2505.22998) appeared in search. Not opened; not cited.
- User-listed leads not checked: Cattle Trade (already in baseline bib, not re-opened), Decrypto, AvalonBench, Agent Island, CoopEval, MINDGAMES, CoffeeBench, MarketSim. None is cited for a claim in this draft.

## Novelty position

The draft claims no firstness for replay, failure logging, state-grounded claim checking or counterfactual restoration; AgentMonopoly, FinBoardBench, DECE, NegotiationArena and the Arena study already cover parts of each. The stated contribution is the cohort-level account of how rival completion was priced, completion turned into construction, debts were financed or not, and estates moved, checked against legal options and delivered information.
