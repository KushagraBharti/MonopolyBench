# Opus initial position (written before drafting; before reading any other full draft)

Date: 2026-11-10. Author stream: Opus xhigh (model `claude-opus-5-5`), acting as a full independent coauthor.

## What I read before writing this

- `../../rewrite_contract.md` (complete).
- The user critique attachment (complete, 693 lines).
- The north-star transcription and the coverage assessment in `../../../research_guidance_2026-10-29/`.
- Every section of the baseline manuscript in `../../../paper_draft_2026-10-29/sections/` that the compiled paper uses, plus `adversarial_review.md` and the agenda negotiation review (`adversarial_reviews/agenda/negotiation/findings.md`).
- Retained data in `../../data/` (identical byte-for-byte to the baseline `data/`; checked with `diff -rq`).

I have not opened `../fable_5_2/`, `../sol/`, or `../../coauthors/sol/initial_position.md`.

## Thesis I intend to defend

The paper should be an observational study of how four configured LLM agents bargain, build, finance and fail across twenty complete four-player games. The central result is a chain:

1. **Bargaining is rival-sensitive, and rival completion is priced, not only refused.** Offers that would complete the *current offer author's* color group are the least often accepted (19/289) and most often rejected (159/289), even though they carry a median +$200 net cash to the recipient. My own re-tabulation of the retained offer ledger adds what the earlier draft lacked: in 92 of the 111 counters to such offers, the counteroffer still gives the author the completion and asks for more money (85 of the 88 counters that keep the author's completion and give the counterer none raise the counterer's cash, median +$125). Initiators who open by seeking their own completion settle 26 of 187 threads, and in 24 of those settlements they still complete their group after raising their cash by a median $97.50 over the opening. This is the population answer to the user's Q1 example, at the observational level.
2. **The pattern is configuration-dependent, and the paper must say so.** Checking the claim across recipients, I find the acceptance gradient in Sol, Gemini and Grok but not in Opus (Opus accepts 7/52 author-only versus 5/42 recipient-only offers, and almost never rejects outright). Reject-versus-counter style differs sharply by configuration (Gemini 180/242 rejects, Opus 19/189). Rejection shares for author-only offers exceed those for recipient-only offers in all five seed blocks; acceptance shares do not (block 3 reverses). Earlier "consistent across games, blocks and configurations" language is therefore not supported as stated.
3. **Trade completion turns into development only when the configured agent can execute a build.** The 63 trade-completed groups lead to first-window construction in 16/17 Sol, 17/18 Gemini, 7/15 Opus and 3/13 Grok cases. The Opus shortfall is dominated by refusal-recovery defaults whose submitted purchase multisets were all executable after atomic reordering (61/61). An economic agent that chooses a sound allocation but cannot express it legally does not receive its value.
4. **Nominal wealth is not accessible liquidity, in both directions.** 56/60 eliminations are below a generous own-asset upper bound. Three are payable at the current debt through legal sales and mortgages that the current menu does not display (current menu-only finance is below the debt in all three). One (G7 d339) has $1,310 nominal value and only $440 accessible because of the hotel/stock rule.
5. **Distress and creditor inheritance are where the sharpest conduct appears.** The G13 insurance pitch, the G18 standing-offer withdrawal and the G20 cash-denial appeal all occur where a player's solvency or a rival's development is at stake, and players argue explicitly about who will inherit. The eventual winner receives the estate in 54/60 eliminations (35/40 nonterminal; my re-tabulation from `agenda_flows.json` reproduces both). Denial purchases end up passing to creditors (G18 Illinois; G13 yellows at d311). This is descriptive, not an effect on winning.

The connecting claim: for an economic agent in a multi-party market, the trade price, the ability to execute the follow-on investment, the true liquidity position and the end-of-life transfer of assets are linked. Evaluations that score any one in isolation (a win, a settlement, a reserve, a bankruptcy) misdescribe the agent.

## Where I agree with the contract

- Behavioral identity, not an auditing-method paper. Legal-sequence checks, provenance and replay are supporting methods with declared scope.
- Configuration and information defects go before results: 2,054/6,989 prompts with a trade-history formatter manifestation; Opus refusal in 1,605/1,696 decisions; 1,394/1,696 Opus decisions without model-authored private memory; 139 selected Grok name conflicts.
- No new evaluations of any kind. No intent, persuasion, optimality, ranking or "financially justified bankruptcy" claims.
- Keep incidents distinct and contextual; consolidate limitations in one place.

## Where I disagree with or would sharpen the contract

1. **Rival sensitivity must be reported with its exception.** The contract's framing invites a universal claim. The Opus recipient pattern and the block-3 acceptance reversal should appear in the main result, not in a footnote. Opus's response condition (action-only, no private note) is a plausible but untested correlate.
2. **Counter content is the strongest bargaining evidence, not reject counts.** Reject/counter shares are dominated by configuration style. The counteroffer analysis (does the counter keep the rival's completion; what happens to the cash) is less style-dependent and says more about bargaining. I will lead with it.
3. **"Distress bargaining" is not a measured population construct.** No retained ledger defines distress. A cash-on-hand cut is descriptive and threshold-dependent (132 of 339 cash-seeking legal offers come from authors holding under $100; 18 of those 132 are accepted). I will use it once, labelled, and otherwise treat distress through incidents.
4. **Incidents belong inside the results they illuminate.** Rather than a separate "contextual conduct" section of five alarming cases, I place the G11 competence case and the G7 bluff with bargaining, G12 with finance, and G13/G18/G20/G3/G19 in a section on distress, inheritance and conduct. G20 d1 disclosure goes to the appendix.
5. **Treat Opus as a different condition from the start.** Saying "Opus" for a configuration whose first attempt was refused in 94.6% of decisions invites model-level readings. I will label the condition explicitly in the cohort table and when Opus-specific numbers appear.
6. **The reference-policy pilot and scenario audit belong in a short appendix.** They support the Q8/C answer (the supplied comparators are not competent strategic baselines) but are not part of the behavioral study.
7. **Do not let the eight questions organize the paper.** They organize one discussion subsection with a coverage table. The paper's organization follows the economic chain.

## Planned structure

Title (provisional): *Bargaining, Building and Bankruptcy: An Observational Study of LLM Agents in Twenty Complete Monopoly Games*.

1. Introduction (problem, the chain, four contributions, scope sentence).
2. Environment, cohort and conditions (rules that matter; configurations; response/information conditions up front).
3. Measurement and validation (units, ledgers, legal-sequence tests, semantic coding with reviewer models named, what checks establish).
4. Bargaining (population, rival completion priced, configuration heterogeneity, initiation/settlement roles, G11 and G7 incidents).
5. From completion to development (first-window outcomes, defaults, executable targets, recovery, holds).
6. Liquidity, elimination and inheritance (financing census, three payable cases, G7 lock, G12 incident, estates, spending/receipts).
7. Distress, coordination and conduct (G13, G18, G20, G3, G19 incidents; corrections; channel conflicts).
8. Plans, forecasts and repeated errors (temporal sample, recurrence) — compact.
9. Related work.
10. Discussion: what this means for evaluating economic agents; coverage of Q1–Q8 and A–C.
11. Limitations (one consolidated section).
12. Conclusion.
Appendices: cohort/rules; response and channel conditions; offer-ledger re-tabulations; certificates; additional incidents; temporal exhibits; pilot/scenario audit; review provenance.
