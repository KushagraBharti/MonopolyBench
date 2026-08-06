# MonopolyBench related work and bibliography workstream

Date: 2026-07-28  
Scope: scholarly positioning and bibliography audit only  
Manuscript inspected: `monopolybench_ieee_draft_v0_1.tex` (all 847 lines)  
Supporting material inspected: `AGENTS.md`, the 2026-07-28 research handoff and GPT-5.6 synthesis, and the existing research notes and Prism exports under `docs/research_raw/`.

This is a downstream research note. It does not modify the canonical TeX or any saved-game artifact.

## 1. Evidence convention and bottom line

- **Verified fact (V):** directly supported by a primary paper, archival proceedings page, publisher record, or the benchmark owner's official page.
- **Inference (I):** a comparison or novelty judgment made by reading those sources together. An inference is not a fact asserted by any cited paper.
- **Not documented (ND):** the feature is not described in the cited primary source or official public page. This is deliberately narrower than claiming that the implementation does not contain it.

**Positioning conclusion (I).** MonopolyBench should not claim to be the first interactive-agent benchmark, long-horizon business benchmark, multi-agent economic benchmark, negotiation benchmark, strategic-game benchmark, process-aware social benchmark, or learned Monopoly agent. AgentBench, \(\tau\)-bench, Vending-Bench/Arena, CoffeeBench, Market-Bench, Cattle Trade, AgenticPay, M3-Bench, DSGBench, and prior Monopoly Markov/RL work collectively foreclose those broad claims.

The defensible novelty is the **joint measurement design**:

> MonopolyBench combines a rules-complete asset-and-solvency game with engine-issued legal action menus; durable ownership, negotiated transfer, auctions, mortgages, development, rent, forced liquidation, and bankruptcy; separately logged public communication and model-produced private rationales; decision/attempt/action/event/snapshot artifacts; deterministic engine-state replay and stricter artifact-provenance comparison; provider usage and cost telemetry; evidence-indexed trajectory review; and a planned bridge from observed full-game decisions to frozen micro-scenarios.

No single component above is claimed to be new. The contribution is their integration into one auditable benchmark surface.

## 2. Recommended related-work structure

Keep the section to four short subsections in this order:

1. **Interactive and tool-using agents.** Establish AgentBench's multi-environment interactive evaluation and \(\tau\)-bench's policy-constrained tool use with terminal database-state verification. Use these as protocol antecedents, not economic competitors.
2. **Long-horizon economic environments.** Move from Vending-Bench's single-agent business operation to Vending-Bench Arena, CoffeeBench, Market-Bench, and EconGym. Concede their priority on long horizons, commercial interaction, supply chains, and heterogeneous economies.
3. **Strategic games and negotiation.** Treat Cattle Trade as the closest direct comparison; then distinguish the breadth of DSGBench, the process-aware social analysis of M3-Bench, and the clean utility/welfare measurements in bargaining, multi-stakeholder negotiation, and AgenticPay.
4. **Monopoly modeling and learning.** Cite Ash and Bishop for Markov landing/rent analysis and Arun et al./Bonjour et al. for learned Monopoly policies. State that MonopolyBench studies off-the-shelf language agents, communication, reliability, cost, and replayable evidence rather than proposing a stronger learned Monopoly policy.

The final paragraph should state the narrow conjunction claim above and immediately add that replay means deterministic reconstruction **conditional on the recorded applied action sequence**, not deterministic regeneration of LLM outputs.

## 3. Precise novelty matrix

| Prior work | Verified scope from primary source | What must be conceded | MonopolyBench-specific distinction (inference) | Status |
|---|---|---|---|---|
| AgentBench [agentbench] | Eight interactive environments; multi-turn open-ended agent generation; 29 API/open models in the ICLR version. | Interactive multi-environment LLM-agent evaluation predates MonopolyBench. | Depth in one shared economic game, endogenous adaptive peers, exact economic protocol objects, replay and cost/provenance auditing. | V + I |
| \(\tau\)-bench [taubench] | Simulated user, domain APIs and policy guidelines; end-of-conversation database-state comparison; \(pass^k\). | Policy-constrained state-changing tool use and state-based verification are established. | The evaluated object is competitive economic policy over a shared trajectory, not user-goal completion; action validity is separated from economic quality. | V + I |
| Vending-Bench [vendingbench] | A single agent operates a vending business, managing inventory, orders, prices and daily fees over runs exceeding 20M tokens. | Long-horizon business coherence and capital acquisition are not new. | Closed multi-player asset economy with adversarial transfers, rent shocks, liquidation and a hard bankruptcy endpoint. | V + I |
| Vending-Bench Arena [vendingarena] | Competing vending agents share a location, email one another, send money and trade goods; the official page reports price wars and evolving rounds. | Multi-agent commercial competition, communication and trade are direct precedents. | Fixed board/rules contract, legally enumerable actions, mortgages/development/rent, and replay/provenance claims. These features are ND on the cited Arena page, so phrase as “MonopolyBench additionally documents,” not “Arena lacks.” | V + I/ND |
| Cattle Trade [cattletrade] | Competitive 50–60-turn game with auctions, hidden-offer trade challenges, bargaining, bluffing, opponent modeling and resource allocation; logs bids/offers/counteroffers/card choices; evaluates 242 games. | This is the closest precedent and defeats any “first long-horizon multi-agent economic game” claim. | MonopolyBench uses a different, rules-complete asset/solvency economy with recurring rent, mortgages, building inventory, forced liquidation and bankruptcy, plus decision/action/event/snapshot replay and full-to-micro linkage. | V + I |
| DSGBench [dsgbench] | Six strategic games, five evaluation dimensions and automated decision tracking. | Long-horizon strategic-game breadth and fine-grained behavior tracking are established. | MonopolyBench argues depth, economic mechanism coverage, communication evidence and replay/provenance in one environment; several latter features are ND in the primary abstract and should not be framed as DSGBench absences without inspecting its released artifacts. | V + I/ND |
| M3-Bench [m3bench] | Four-level mixed-motive suite; jointly analyzes behavioral trajectories, expressed reasoning and communication through BTA/RPA/CCA. | “What agents do, think and say” and process-aware social portraits are not novel phrases or concepts. | MonopolyBench grounds analogous evidence in authoritative cash/ownership/rent/solvency transitions and later actions. Call private rationales model-produced process proxies, not latent beliefs. | V + I |
| Xia et al. [bargaining] | Asymmetric incomplete-information buyer/seller bargaining with quantitative buyer and seller gains and a real-price dataset. | Scorable language bargaining predates MonopolyBench. | Monopoly trades are repeated, multi-party and path-dependent: a deal alters later rent, development, liquidity and bargaining power. | V + I |
| Abdelnabi et al. [stakeholder] | Multi-agent, multi-issue, semantically rich negotiation games with scorable role objectives and greedy/adversarial participants. | Multi-stakeholder negotiation, competition/cooperation and manipulation-oriented evaluation are established. | MonopolyBench embeds negotiation inside a persistent engine-authoritative economy and links utterances to exact applied transfers and downstream solvency. | V + I |
| AgenticPay [agenticpay] | More than 110 bilateral to many-to-many buyer/seller tasks; private constraints/valuations; multi-round language negotiation; feasibility, efficiency and welfare metrics. | Broad agentic-commerce negotiation and clean welfare scoring are direct precedents. | MonopolyBench offers longer endogenous portfolio dynamics and bankruptcy; AgenticPay offers cleaner private-value welfare estimands. Present these as complementary strengths. | V + I |
| Market-Bench [marketbench] | Configurable multi-agent supply chain; budget-constrained procurement auctions, retail pricing and marketing; complete bid/price/sale/balance-sheet trajectories. | Multi-agent economic competition, auctions and balance-sheet logging are established. | MonopolyBench has bilateral durable-asset trades, recurring opponent-to-opponent rent transfers, mortgages, forced liquidation, bankruptcy and exact legal menus. | V + I |
| CoffeeBench [coffeebench] | Six heterogeneous firms over 90 simulated days; communication, transactions, cash, inventory and pricing; one evaluated roaster faces fixed reference firms. | Long-horizon heterogeneous firm economies and communication/transaction traces are established. | MonopolyBench uses four simultaneously evaluated LLM players in a symmetric ruleset and isolates strategic behavior from fixed-reference-agent assumptions; do not claim greater market realism. | V + I |
| EconGym [econgym] | Modular testbed with 11 role types, 25+ economic tasks and scaling to 100k agents. | Breadth, heterogeneity and macroeconomic scale belong to EconGym. | MonopolyBench is a compact language-agent audit environment with natural-language bargaining and action-level evidence, not a general economic simulator. | V + I |
| Ash and Bishop [monopoly_markov] | Markov-chain approximation of Monopoly; limiting landing frequencies and expected property income/rent. | Probabilistic Monopoly valuation long predates this project. | Use as a baseline feature source, not as proof of universally optimal color groups or a complete multiplayer strategy oracle. | V + I |
| Arun et al.; Bonjour et al. [monopoly_rl], [monopoly_drl] | Learned Monopoly policies against fixed/defined opponents; Bonjour et al. provide full-game state/action representations and a hybrid DRL/fixed-policy method for uneven action frequencies. | Learned Monopoly play and full-state RL environments are established. | MonopolyBench evaluates off-the-shelf LLMs' communication and economic trajectories while measuring serialization, retries, fallbacks, provider cost and realized-path replay; it is not presently a policy-optimality claim. | V + I |

## 4. Publication-ready LaTeX replacement prose

This block can replace the current `Related Work` section. It intentionally avoids “first” claims and treats the micro-scenario bridge as planned until the fixture/results contract is frozen.

```latex
\section{Related Work}
\label{sec:related}

\subsection{Interactive and Tool-Using Agents}

AgentBench established broad interactive evaluation across eight environments, measuring language models in multi-turn observe--act loops rather than only static question answering \cite{agentbench}. The more domain-specific $\tau$-bench evaluates agents that converse with a simulated user while operating APIs under policy constraints; it verifies task completion by comparing the resulting database state with an annotated goal state and measures consistency with $\mathrm{pass}^k$ \cite{taubench}. These benchmarks motivate state-grounded evaluation and repeated interaction. \Bench\ asks a different question: conditional on legal execution, do successive choices form a coherent economic policy against adaptive agents in a shared, path-dependent environment? We therefore report interface reliability separately from economic outcomes.

\subsection{Long-Horizon Economic Environments}

Vending-Bench isolates long-horizon coherence through a single agent's operation of a simulated vending business, including inventory, ordering, pricing, and recurring fees over runs exceeding 20 million tokens \cite{vendingbench}. Vending-Bench Arena adds co-located competitors that can communicate, transfer money, and trade goods \cite{vendingarena}. More recent environments broaden the economic setting. Market-Bench models budget-constrained procurement auctions and retail competition while logging bids, prices, sales, and balance sheets \cite{marketbench}; CoffeeBench evaluates communication and transactions among heterogeneous firms over a 90-day supply-chain simulation \cite{coffeebench}; and EconGym provides a modular testbed spanning heterogeneous households, firms, banks, and governments across more than 25 economic tasks \cite{econgym}.

These works establish long-horizon business operation and multi-agent commerce as benchmark targets. \Bench\ instead emphasizes a compact, closed asset-and-solvency economy. Durable property ownership, negotiated transfer, open auctions, mortgages, finite building inventory, recurring rent, forced liquidation, and bankruptcy create mechanically explicit links between an early decision and later bargaining power or collapse. The narrower domain sacrifices market realism and breadth in exchange for complete rule enforcement and decision-level auditability.

\subsection{Strategic Games and Negotiation}

DSGBench evaluates long-horizon decision making across six strategic games using five scoring dimensions and automated decision tracking \cite{dsgbench}. Cattle Trade is the closest economic-game comparison: its 50--60-turn matches combine auctions, hidden offers, bargaining, bluffing, opponent modeling, and resource allocation, and its evaluation covers 242 games with logged behavioral traces \cite{cattletrade}. M3-Bench complements outcome metrics with process-aware analysis of behavioral trajectories, model-produced reasoning, and communication in mixed-motive games \cite{m3bench}. Accordingly, neither strategic-game evaluation nor joint action--reasoning--communication analysis is new in isolation.

Negotiation benchmarks provide cleaner local estimands. Xia et al.\ formalize buyer--seller bargaining as an asymmetric incomplete-information game with quantitative gains \cite{bargaining}. Abdelnabi et al.\ construct scorable multi-agent, multi-issue negotiations that vary cooperative, competitive, greedy, and adversarial stakeholders \cite{stakeholder}. AgenticPay extends language-mediated buyer--seller negotiation from bilateral bargaining to many-to-many markets and reports feasibility, efficiency, and welfare \cite{agenticpay}. \Bench\ complements these controlled utility settings by embedding repeated negotiations in an evolving portfolio: a transfer can complete a color group, alter development rights and liquidity, redirect future rent, and change bankruptcy risk. Public messages, model-produced private rationales, applied actions, and subsequent events are retained as distinct evidence streams; the rationale is treated as an expressed process trace, not privileged access to a model's true belief or intent.

\subsection{Monopoly Modeling and Learning}

Monopoly has long served as a sequential-decision testbed. Ash and Bishop approximate movement with a Markov process and derive limiting landing frequencies and expected property returns \cite{monopoly_markov}. Arun et al.\ train a reinforcement-learning Monopoly agent \cite{monopoly_rl}. Bonjour et al.\ define full-game state and action representations and combine deep reinforcement learning for frequent, complex decisions with fixed policies for sparse decisions, outperforming their standard DRL comparison against fixed-policy opponents \cite{monopoly_drl}. These studies provide useful probability features and non-language baselines, but they primarily optimize or analyze Monopoly play.

\Bench\ instead contributes an audit-oriented measurement stack for language agents. The engine alone mutates state and emits legal action menus; the benchmark records decisions, attempts, applied actions, events, snapshots, communication, usage, cost, and replay evidence. Determinism is scoped to engine-transition replay conditional on the engine version, seed, settings, identities, and recorded action sequence, not to regeneration of provider outputs. The distinguishing claim is therefore the conjunction of a rules-complete asset-and-solvency economy, legal-action enforcement, public/private language traces, split state-versus-artifact replay, and a planned bridge from observed full-game decisions to frozen micro-scenarios--not priority over long-horizon economic, negotiation, strategic-game, or Monopoly-learning benchmarks.
```

## 5. Verified IEEE-style `\bibitem` entries

The entries below prefer archival versions when one exists. URLs point to primary publisher/proceedings records or arXiv. ArXiv-only 2026 papers should remain labeled preprints unless they acquire archival venues before submission.

```latex
\bibitem{agentbench}
X. Liu, H. Yu, H. Zhang, Y. Xu, X. Lei, H. Lai, Y. Gu, H. Ding, K. Men, K. Yang, S. Zhang, X. Deng, A. Zeng, Z. Du, C. Zhang, S. Shen, T. Zhang, Y. Su, H. Sun, M. Huang, Y. Dong, and J. Tang, ``AgentBench: Evaluating LLMs as agents,'' in \emph{Proc. Int. Conf. Learn. Representations (ICLR)}, 2024. [Online]. Available: \url{https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html}. arXiv:2308.03688.

\bibitem{taubench}
S. Yao, N. Shinn, P. Razavi, and K. Narasimhan, ``$\tau$-bench: A benchmark for tool-agent-user interaction in real-world domains,'' in \emph{Proc. Int. Conf. Learn. Representations (ICLR)}, 2025. [Online]. Available: \url{https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html}. arXiv:2406.12045.

\bibitem{vendingbench}
A. Backlund and L. Petersson, ``Vending-Bench: A benchmark for long-term coherence of autonomous agents,'' arXiv:2502.15840, 2025. [Online]. Available: \url{https://arxiv.org/abs/2502.15840}

\bibitem{vendingarena}
Andon Labs, ``Vending-Bench Arena.'' [Online]. Available: \url{https://andonlabs.com/evals/vending-bench-arena}. Accessed: Jul. 28, 2026.

\bibitem{dsgbench}
W. Tang, Y. Zhou, E. Xu, K. Cheng, M. Li, and L. Xiao, ``DSGBench: A diverse strategic game benchmark for evaluating LLM-based agents in complex decision-making environments,'' in \emph{Proc. IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP)}, Barcelona, Spain, 2026, doi: 10.1109/ICASSP55912.2026.11460704. [Online]. Available: \url{https://doi.org/10.1109/ICASSP55912.2026.11460704}. arXiv:2503.06047.

\bibitem{cattletrade}
R. M\"uller and C. M\"uller, ``Cattle Trade: A multi-agent benchmark for LLM bluffing, bidding, and bargaining,'' arXiv:2605.14537, 2026. [Online]. Available: \url{https://arxiv.org/abs/2605.14537}

\bibitem{m3bench}
S. Xie, Z. Shi, H. Shen, G. Huang, Y. Ma, and X. Jing, ``M3-BENCH: Process-aware evaluation of LLM agents social behaviors in mixed-motive games,'' arXiv:2601.08462, 2026. [Online]. Available: \url{https://arxiv.org/abs/2601.08462}

\bibitem{bargaining}
T. Xia, Z. He, T. Ren, Y. Miao, Z. Zhang, Y. Yang, and R. Wang, ``Measuring bargaining abilities of LLMs: A benchmark and a buyer-enhancement method,'' in \emph{Findings Assoc. Comput. Linguistics: ACL 2024}, Bangkok, Thailand, 2024, pp. 3579--3602, doi: 10.18653/v1/2024.findings-acl.213. [Online]. Available: \url{https://aclanthology.org/2024.findings-acl.213/}. arXiv:2402.15813.

\bibitem{stakeholder}
S. Abdelnabi, A. Gomaa, S. Sivaprasad, L. Sch\"onherr, and M. Fritz, ``Cooperation, competition, and maliciousness: LLM-stakeholders interactive negotiation,'' in \emph{Advances in Neural Information Processing Systems}, vol. 37, 2024, doi: 10.52202/079017-2658. [Online]. Available: \url{https://proceedings.neurips.cc/paper_files/paper/2024/hash/984dd3db213db2d1454a163b65b84d08-Abstract-Datasets_and_Benchmarks_Track.html}

\bibitem{agenticpay}
X. Liu, S. Gu, and D. Song, ``AgenticPay: A multi-agent LLM negotiation system for buyer-seller transactions,'' arXiv:2602.06008, 2026. [Online]. Available: \url{https://arxiv.org/abs/2602.06008}

\bibitem{marketbench}
Y. Zheng, H. Duan, Z. Zhang, Y. Zhu, X. Min, and G. Zhai, ``Market-Bench: Benchmarking large language models on economic and trade competition,'' arXiv:2604.05523, 2026. [Online]. Available: \url{https://arxiv.org/abs/2604.05523}

\bibitem{coffeebench}
I. Sugiura, D. Hattori, K. Araragi, K. Ogawa, S. Onose, T. Makino, T. Usuki, and T. Ishida, ``CoffeeBench: Benchmarking long-horizon LLM agents in heterogeneous multi-agent economies,'' arXiv:2606.16613, 2026. [Online]. Available: \url{https://arxiv.org/abs/2606.16613}

\bibitem{econgym}
Q. Mi, Q. Yang, Z. Fan, W. Fan, H. Ma, C. Ma, S. Xia, B. An, J. Wang, and H. Zhang, ``EconGym: A scalable AI testbed with diverse economic tasks,'' in \emph{Advances in Neural Information Processing Systems}, vol. 38, 2025. [Online]. Available: \url{https://proceedings.neurips.cc/paper_files/paper/2025/hash/40d45b1e23d00d5895e65778e85cf8ee-Abstract-Datasets_and_Benchmarks_Track.html}

\bibitem{monopoly_markov}
R. B. Ash and R. L. Bishop, ``Monopoly as a Markov process,'' \emph{Math. Mag.}, vol. 45, no. 1, pp. 26--29, 1972, doi: 10.1080/0025570X.1972.11976187. [Online]. Available: \url{https://doi.org/10.1080/0025570X.1972.11976187}

\bibitem{monopoly_rl}
E. Arun, H. Rajesh, D. Chakrabarti, H. Cherala, and K. George, ``Monopoly using reinforcement learning,'' in \emph{Proc. TENCON 2019--2019 IEEE Region 10 Conf.}, Kochi, India, 2019, pp. 858--862, doi: 10.1109/TENCON.2019.8929523. [Online]. Available: \url{https://doi.org/10.1109/TENCON.2019.8929523}

\bibitem{monopoly_drl}
T. Bonjour, M. Haliem, A. O. Alsalem, S. Thomas, H. Li, V. Aggarwal, M. Kejriwal, and B. K. Bhargava, ``Decision making in Monopoly using a hybrid deep reinforcement learning approach,'' \emph{IEEE Trans. Emerg. Topics Comput. Intell.}, vol. 6, no. 6, pp. 1335--1344, Dec. 2022, doi: 10.1109/TETCI.2022.3166555. [Online]. Available: \url{https://doi.org/10.1109/TETCI.2022.3166555}. arXiv:2103.00683.

\bibitem{hasbro_rules}
Hasbro, ``Monopoly: Property trading game---classic rules,'' 2007. [Online]. Available: \url{https://www.hasbro.com/common/instruct/00009.pdf}. Accessed: Jul. 28, 2026.
```

## 6. Citation-to-claim mapping

| ID | Manuscript-ready claim | Citation(s) | Fact or inference | Verification note |
|---|---|---|---|---|
| C1 | AgentBench contains eight interactive environments for multi-turn agent evaluation. | `agentbench` | V | ICLR 2024 proceedings abstract. |
| C2 | \(\tau\)-bench supplies domain APIs/policies, verifies final database state, and defines \(pass^k\). | `taubench` | V | ICLR 2025 proceedings/arXiv abstract. |
| C3 | Vending-Bench requires inventory, ordering and pricing over runs exceeding 20M tokens. | `vendingbench` | V | arXiv abstract. |
| C4 | Arena agents compete at one location and can email, transfer money and trade goods. | `vendingarena` | V | Andon Labs official evolving evaluation page. Non-archival. |
| C5 | Cattle Trade combines auctions, bargaining, bluffing and resource allocation over 50–60 turns, logs behavior, and reports 242 games. | `cattletrade` | V | arXiv abstract. |
| C6 | DSGBench contains six strategic games, five scoring dimensions and automated decision tracking. | `dsgbench` | V | IEEE Xplore/arXiv abstract. |
| C7 | M3-Bench analyzes behavior, expressed reasoning and communication in mixed-motive games. | `m3bench` | V | arXiv abstract/method. Avoid calling rationale hidden thought. |
| C8 | Xia et al. formalize asymmetric incomplete-information bargaining and quantify both parties' gains. | `bargaining` | V | ACL Anthology archival record and paper. |
| C9 | Abdelnabi et al. offer scorable multi-party, multi-issue negotiation with cooperative, competitive and adversarial roles. | `stakeholder` | V | NeurIPS official proceedings. |
| C10 | AgenticPay spans 110+ tasks and reports feasibility, efficiency and welfare. | `agenticpay` | V | arXiv abstract. |
| C11 | Market-Bench logs bids, prices, sales and balance sheets in procurement/retail competition. | `marketbench` | V | arXiv abstract. |
| C12 | CoffeeBench is a 90-day heterogeneous six-firm economy in which one evaluated roaster interacts with fixed reference firms. | `coffeebench` | V | arXiv abstract. |
| C13 | EconGym supplies 11 role types, 25+ economic tasks and up-to-100k-agent simulations. | `econgym` | V | NeurIPS 2025 official proceedings abstract. |
| C14 | Ash and Bishop derive limiting landing frequencies and expected property income using a Markov approximation. | `monopoly_markov` | V | Mathematics Magazine publisher record/paper. |
| C15 | Bonjour et al. combine DRL and fixed policies to address uneven action frequencies and compare against fixed-policy opponents. | `monopoly_drl` | V | IEEE article/arXiv abstract and publisher metadata. |
| C16 | MonopolyBench's novelty is the conjunction of economic mechanics, protocol objects, split replay, language and telemetry. | preceding works + repository contract | I | This is a scoped synthesis. It requires a final implementation-feature table backed by repository tests/artifacts. |
| C17 | MonopolyBench is more auditable, but not more economically realistic, than heterogeneous supply-chain/economic simulators. | `marketbench`, `coffeebench`, `econgym` | I | State as design tradeoff, not measured superiority. |
| C18 | Repeated Monopoly trades are more path-dependent than one-shot bargaining because transfers alter later rent, development, liquidity and solvency. | `hasbro_rules` + engine contract | I | Mechanically grounded inference; do not call it empirically harder without an experiment. |

## 7. Audit of the manuscript's current references

| Current key | Finding | Action |
|---|---|---|
| `agentbench` | Authors/title/arXiv ID are correct, but the entry stops at the 2023 preprint. | Upgrade to ICLR 2024 proceedings; retain arXiv ID. |
| `taubench` | Authors/title/arXiv ID are correct, but the archival ICLR 2025 version is omitted. | Upgrade to ICLR 2025 proceedings; retain arXiv ID. |
| `vendingbench` | Metadata is correct. | Retain, adding URL and explicit preprint status. |
| `vendingarena` | Official primary web page, but it is dynamic and not a scholarly paper. The manuscript's year `2026` describes later rounds, while the page's first documented round is Nov. 2025; the page does not expose a stable publication date. | Cite Andon Labs as organizational author without inventing a publication year, include an access date, and do not treat it as peer reviewed. Archive a page snapshot for reproducibility if permitted. |
| `dsgbench` | Preprint metadata is substantially correct, but the paper now has an IEEE ICASSP 2026 record and DOI. | Replace with archival IEEE entry and retain arXiv ID. |
| `cattletrade` | Verified arXiv preprint metadata. | Retain as an arXiv-only 2026 preprint unless archival publication appears. |
| `m3bench` | Verified arXiv preprint metadata. | Retain as an arXiv-only 2026 preprint; change prose from “think” to “model-produced reasoning” or “expressed rationale.” |
| `bargaining` | Current preprint metadata is correct but weak relative to its archival version. | Cite Findings of ACL 2024, pages 3579–3602, DOI 10.18653/v1/2024.findings-acl.213; optionally retain arXiv ID. |
| `monopoly_drl` | Current entry is incomplete and one author's initials are underspecified. It omits the IEEE journal publication. | Replace with IEEE TETCI vol. 6, no. 6, pp. 1335–1344, DOI 10.1109/TETCI.2022.3166555. |
| `monopoly_markov` | Bernard's 2017 personal PDF is informal and does not support the manuscript's compound claim that several named color groups and “three houses” are broadly strongest. | Remove from the main bibliography. Replace with Ash and Bishop (1972). Delete or separately source the color-group/three-house strategy claim; the Ash–Bishop citation alone does not verify that exact sentence. |
| `hasbro_rules` | The Hasbro PDF resolves and supports classic mechanics, auctions and the wealth objective. It contains both speed-die and classic rules. | Retain, identify the classic-rules portion, add access date, and separately document which edition/deviations MonopolyBench implements. |
| `beergame_site` | An official lab/project page can be a primary source for that project, but it is non-archival and peripheral to the paper's narrow comparison. | Remove from the main related-work section unless supply-chain coordination becomes a substantive comparison. If retained, cite the responsible institution and access date after verifying page authorship/date. |
| `beergame_hbr` | The entry contains literal `[TODO]` author fields and was not bibliographically complete. HBR is also a secondary practitioner article, not the primary technical source for the system. | Remove. Do not submit with this entry. Replace only if the underlying technical paper is identified and directly used. |

Additional audit findings:

- There are no duplicate `\bibitem` keys inside the current IEEE draft.
- `monopolybench.tex` at the repository root is an untouched IEEE sample/template containing placeholder references `b1`--`b7`; those are not MonopolyBench scholarly references and must not be merged into the paper bibliography.
- The Prism copy duplicates the current IEEE draft's bibliography. Treat it as an export, not an independent source.
- Several research notes cite ResearchGate, generic search results, blog posts, or ChatGPT tracking URLs. Those are useful discovery aids but should not appear as technical evidence in the paper.
- `Market-Bench` is name-ambiguous in 2026: arXiv:2604.05523 is the multi-agent supply-chain benchmark intended here; arXiv:2604.23897 is a different software-agent market-participation benchmark, and arXiv:2512.12264 is a quantitative-trading code benchmark. Always include title and arXiv ID.
- Vending-Bench Arena is an evolving webpage. Claims tied to particular rounds require a dated snapshot and should not be generalized as a fixed benchmark-paper result.

## 8. Claims to avoid or rewrite

1. **Avoid:** “MonopolyBench is the first long-horizon economic LLM benchmark.”  
   **Use:** “MonopolyBench studies long-horizon economic agency in a rules-complete asset-and-solvency game with replayable protocol artifacts.”
2. **Avoid:** “Existing benchmarks only score final outcomes.”  
   **Use:** “Several adjacent benchmarks already log decisions or process signals; MonopolyBench links these signals to authoritative economic transitions and split replay.”
3. **Avoid:** “No prior benchmark combines auctions, bargaining and resource constraints.”  
   **Reason:** Cattle Trade directly does.
4. **Avoid:** “M3-Bench reads what models truly think.”  
   **Use:** “M3-Bench and MonopolyBench analyze model-produced rationales as process evidence.”
5. **Avoid:** “Monopoly Markov analysis proves orange/light-blue/red/yellow and three houses are optimal.”  
   **Use:** a narrower landing-frequency/expected-income claim, or add a primary source that proves each specific heuristic under explicit rules.
6. **Avoid:** “Deterministic benchmark” without qualification.  
   **Use:** “deterministically replayable engine transitions conditional on the recorded applied action sequence.”
7. **Avoid:** “More realistic than Vending-Bench/Market-Bench/CoffeeBench/EconGym.”  
   **Use:** “mechanically narrower and more explicitly auditable.”

## 9. Final integration checklist

- Recheck all 2026 arXiv records immediately before submission for new versions, changed author order, or archival venues.
- Freeze or archive all web-only sources, especially Vending-Bench Arena and Hasbro rules, and record access dates.
- Add a paper comparison table using only documented features; use “not documented” rather than unsupported negative claims.
- Keep implemented and planned features separate. The full-game-to-micro bridge must remain “planned” until fixtures, manifests and results exist.
- Run a citation-key check after integration and compile under `IEEEtran`.
- Ensure every MonopolyBench-side comparison feature resolves to repository documentation/tests or released artifacts; external citations cannot verify the project's own implementation.
