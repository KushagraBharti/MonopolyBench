# Literature updates (Fable 5.2 full draft)

Checked on 10 November 2026. "Abstract page" means I fetched the arXiv abstract page and read the title, authors, version history, comments and abstract as returned through a fetch tool that summarizes long text. I did not read any full paper in this pass. Claims in the manuscript about these papers are limited to what the abstract page supports, or are marked as inherited from the 29 October registry (`../../../paper_phase3_2026-10-29/reference_registry.json`, `literature_review.md`), which records deeper section-level inspection for the closest comparisons.

No citation was added on the strength of the critique's list or the screenshot list alone.

## Versions confirmed for sources already in the bibliography

| Key | arXiv id | Latest version on 10 Nov 2026 | Change since 29 Oct | Note |
|---|---|---|---|---|
| `wu2026agentmonopoly` | 2610.29330 | v2, 22 Oct 2026 | none | Abstract: four families at two sizes, persona interventions, "Larger models do not consistently win more games." Five seeds per configuration |
| `zhang2026dece` | 2610.35773 | v1, 26 Oct 2026 | none | Ten Eurogames, 12 model and harness configurations, 480 primary and 1,032 total matches, harness changes performance |
| `li2026arena` | 2608.14825 | v3, 21 Aug 2026 | none | 2,583 emails, 20 runs, 13 models, 12.6% misaligned under the primary classifier, replication with two other judge families, odds 1.65× after a misaligned counterparty email and 1.58× under low inventory, performance rank does not predict the rate |
| `hu2026finboardbench` | 2605.27896 | v1, 27 May 2026 | none | Cashflow, Acquire, Monopoly; models favor acquisition over liquidity |
| `muller2026cattletrade` | 2605.14537 | v1, 14 May 2026 | none | MALGAI workshop at ICLR 2026. Abstract supports "strategic coherence correlates with rank more strongly than any single subskill" and lists overbidding among failure modes. It does not report agreement rates or a bluffing result |
| `shi2026emergentcollusion` | 2609.24967 | v2, 26 Sep 2026 | none | Collusion against a verification protocol in 94% of trajectories across 10 models |

Rule-level comparisons with AgentMonopoly and FinBoardBench (intact versus bank-returned buildings, single-offer trades, fallback records) are **inherited** from the 29 October related-work section and its round-2 review. I did not re-inspect those papers' methods sections or the AgentMonopoly repository.

## Sources added in this draft

| Key | arXiv id and version inspected | Venue as stated on the abstract page | What the manuscript uses it for |
|---|---|---|---|
| `abdelnabi2024stakeholders` | 2309.17234v2, 10 Jun 2024 | none listed | Scorable multi-party, multi-issue negotiation with greedy and adversarial players. The critique gives NeurIPS 2024; the abstract page does not, so the entry cites arXiv only |
| `duan2024gtbench` | 2402.12348v2, 10 Jun 2024 | none listed | Ten-game strategic benchmark. Same caveat on venue |
| `huang2025gamabench` | 2403.11807v7, 6 Mar 2025 | "Accepted to ICLR 2025" in comments | Eight game-theory scenarios |
| `yao2025spinbench` | 2503.12349v5, 15 Oct 2025 | none listed | Planning, games and negotiation |
| `murphy2026agentisland` | 2605.04312v1, 5 May 2026 | none listed | 999 games, 49 models, Plackett–Luce ranking, same-provider preference of 8.3 points in final votes |
| `chen2026ceobench` | 2606.18543v2, 22 Jul 2026 | none listed | 500-day startup simulation; all models below a rule-based baseline |
| `hardy2026reliability` | 2610.00651v1, 30 Sep 2026 | none listed | System rankings reliable, underlying-model rankings much less so |
| `yang2026measurementfirst` | 2610.05830v1, 5 Oct 2026 | journal reference "NeurIPS 2026 Workshop LCFM" | Example of an audit evaluated with matched controls and scorer validation. Cited to mark what this paper does not do |
| `cosentino2026counterparty` | 2605.16575v1, 15 May 2026 | none listed | Accurate counterparty modeling without better agreements; sellers concede more; opening anchors dominate |
| `shah2025rationalis` | 2512.13063v1, 15 Dec 2025 | NeurIPS 2025 workshop on multi-turn interactions | LLMs anchor at the extremes of the agreement zone; limited strategy diversity |
| `liu2026multibuyer` | 2607.05863v1, 7 Jul 2026 | none listed | One seller, several buyers; standard models fixate on the current highest bid |
| `tewolde2026coopeval` | 2604.15267v2, 5 Jul 2026 | ICML 2026 in comments | Mechanisms that sustain cooperation in social dilemmas |
| `wang2026mindgames` | 2605.29512v1, 28 May 2026 | none listed (53 authors) | Fragile rule-following and uneven leaderboard validity in a large competition |

## Corrections to claims that arrived by repetition

1. **Agreeableness in 2607.05863.** A search summary described this paper as attributing deal-volume maximization to an "agreeableness bias". The abstract page says nothing about agreeableness or deal volume. The manuscript cites it only for fixation on the current highest bid. I found no primary source in this pass that establishes an agreement bias in multi-party bargaining, so the manuscript says only that bilateral studies report anchoring and weakly compensated concession, and that low acceptance here does not rule the bias out.
2. **Venues for LLM-Stakeholders and GTBench.** The critique lists both as NeurIPS 2024. Their arXiv pages list no venue. The bibliography cites the arXiv versions. Someone should confirm the proceedings entries before a camera-ready.
3. **MINDGAMES is ambiguous.** At least four works use the name (a 2023 epistemic-logic dataset, a 2025 persuasion task, the 2026 live arena, and a NeurIPS 2026 poster on a competition dataset). The manuscript cites the 2026 arena paper, 2605.29512v1. The screenshot list does not say which one was meant.
4. **AgentMonopoly's game count.** The 29 October review recorded a discrepancy between 140 games in the paper's table and 120 in the repository README. I did not re-check it and the manuscript states neither number.

## Not located or not inspected

| Item from the question screenshots or the critique | Status |
|---|---|
| CoffeeBench | Not located in two searches. Not cited |
| MarketSim | Not located. Not cited |
| Decrypto | Not inspected in this pass. Not cited |
| AvalonBench | Not inspected in this pass. Not cited |
| Vending-Bench Arena author page, Vending-Bench 2 page | In the inherited bibliography, not re-fetched, not cited in this draft |
| SOTOPIA, AgentBoard venue details, HAL venue (ICLR 2026) | Inherited from the 29 October registry, not re-fetched |
| Any paper posted after 29 October 2026 on LLM agents in Monopoly | One search found none. This is a weak negative: one query, United States index |

## Positioning consequences

- The closest prior work still overlaps heavily on the game (AgentMonopoly), on financial board games (FinBoardBench) and on complete-configuration evaluation (DECE). The manuscript claims no first. Its stated additions are an offer-level bargaining census with ownership consequences for both sides, a decomposition of why traded monopolies were or were not developed, and an insolvency and inheritance census.
- The Arena study's scarcity result (odds 1.58× under low inventory) is the nearest external analogue to the cash-poor tabulations. The manuscript notes the parallel and says the two are not comparable measures.
- Hardy et al. and DECE support treating the configured system, not the model, as the object. They are cited for that and not as evidence about these four systems.
