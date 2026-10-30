# Fable novelty review of the frozen first draft (round 1, 2026-10-29)

Scope: complete read of the 34-page draft; strongest-comparator attack led from primary sources; read-only analysis of the frozen exports. Deliverables in this folder: `initial_position.md` (written before any prior report was opened), `findings.json` (17 findings with stable IDs), `proposed_revision.tex`, `verification.md`, `sources.md`, `analysis/decompose_first_window.py` and `analysis/results.json`. Nothing outside this folder was written. No game, prompt, engine, canonical artifact or shared draft file was touched.

## 1. What the paper is, and what knowledge changes because of it

The draft is an exploratory cohort study of twenty uncapped four-player Monopoly games between four frontier configurations, with an unusually complete record (legal menus, every attempt, delivered memory, events) and an unusually disciplined refusal to overclaim. After verification against the primary comparators, I can state what it adds and what it does not.

**What changes if the paper is believed.**

1. In deployed frontier configurations, a measurable share of economically consequential actions were produced by the harness's resolution of a response rather than by the agent's stated plan: 61 of 61 defaulted construction plans were affordable and legal when reordered; one of three payable bankruptcies was declared by a received tool call whose content requested a house sale; three of eight unbuilt entry-buildable groups ended through received actions that contradicted their text; 139 Grok content/tool conflicts include four accepted trades whose text argued rejection. This is a result about evaluation practice: report attempts, retries and fallbacks as part of the measured system and audit applied actions against attempted ones before interpreting an END or a bankruptcy. It generalizes beyond Monopoly. None of the four comparators records or reports attempt chains (verified: AgentMonopoly forces a silent `pass`; FinBoardBench logs a system fallback after five failures; DECE disables retries for its expansion and does not describe them for its primary results; the Arena paper does not state attempt handling).
2. A settlement is not evidence of persuasion. Five chronologies show recipients correcting a false premise and accepting on their own terms, or echoing then rejecting. This is a methodological caution with n = 5 and a specific contract; it does not generalize as a rate.
3. "Current menu" and "reachable legal sequence" differ, and the difference decides feasibility verdicts (mortgages that unlock only after sales; hotel downgrades blocked by bank stock). This is the paper's clearest conceptual contribution to opportunity accounting, and it is demonstrably absent from the comparators' analysis (AgentMonopoly performs no counterfactual or alternative-action analysis and suggests it as future work, §5.3).

**What does not change.** No ranking, no rate, no effect, no capability–alignment relation. The paper says all of this, repeatedly.

## 2. The strongest-comparator attack

I re-fetched every comparator at the cited version and, for AgentMonopoly, read four raw source files from the repository's `main` branch. The full verdict table is in `verification.md`; the comparison matrix is in `proposed_revision.tex` (Table `tab:capability-matrix`). Summary:

**AgentMonopoly (2610.29330v2; repo `main`).** The draft's specific claims are correct: cash-negative elimination with no liquidation, prohibition on public/action contradiction, eight open-weight 8B–32B models at temperature zero, 150-step cap with net-worth winner, 140 games in the paper versus 120 in the README. The draft is wrong by omission or imprecision in four places:

- "replay" (related work) is session playback in a dashboard; the code has no restore or re-execution function (`server.py` INIT always creates a new state; `engine.py` has no restore; `run_experiments.py` writes snapshots every five turns and never reads them back except to build a report). The draft's own replay is engine re-execution with restored hidden state. One word for both erases the paper's clearest infrastructure difference. (FN-04)
- Trades there are a single offer answered by accept or reject (`_process_trade_proposal`). The draft's counteroffer attribution finding (44 of 113 settlements authored by the non-initiator) cannot arise in that protocol. Related work should say so. (FN-05)
- Invalid outputs there are forced to `pass` without a corrective retry and are not reported numerically. The draft's attempt-level provenance is a verifiable differentiator it never claims. (FN-06)
- A player-creditor there also inherits buildings intact (`_declare_bankruptcy`), so the draft's inheritance contrast with FinBoardBench should not be read as a MonopolyBench peculiarity. (FN-07)

Version ambiguity to record: the paper's 150-step cap and net-worth rule are not in the runner code read today (`DEFAULT_MAX_TURNS = 600`, first non-bankrupt player printed as winner). The paper governs; the discrepancy belongs beside the 140/120 note. (FN-14)

**Vending-Bench Arena communication paper (2608.14825v3).** All draft claims verified: 2,583 emails, 20 runs, LLM judge plus deterministic checks plus reasoning audit, promise follow-through, single-author 50-email check, environment not redistributed, no conduct instruction, no capability association (ρ = −0.07). One strengthening the draft can make from the paper itself: Arena's deterministic checks apply only to claims the simulator's logs resolve, with an insufficient-data verdict and intraday balance claims excluded; in MonopolyBench every economic proposition is decidable from the complete event log and feasibility is decidable by execution. (FN-13)

**DECE (2610.35773v1).** Verified: complete-configuration framing, matched harness studies, persisted state, replay and resume (App. D.7), no dialogue. The draft's gloss "economic games" and "controlled economic conditions" is wrong: ten score-based Eurogames with no trading or dialogue. (FN-08)

**FinBoardBench (2605.27896v1).** Verified with one precision fix ("returns buildings to the bank", not "sells"), and one omission: it evaluates one focal model against three fixed opponents with structured accept/reject/counter trades and a judge. (FN-12)

**Release status.** The Arena environment is not redistributed; DECE, FinBoardBench and Cattle Trade state no release in the fetched text; AgentMonopoly releases code but not logs. MonopolyBench's repository is public under Apache-2.0 and tracks all twenty games with events, actions, decisions, 703 state snapshots and 2,780 prompt/response/retry files per game. The draft says the release is outstanding and names no URL. This is the single largest underclaim in the paper. (FN-03)

**Defensible novelty statement.** "Among inspected systems, MonopolyBench is the only one that records, for every decision, the legal menu, every response attempt with its retry condition, the memory delivered, and the resulting events, and whose engine can restore any recorded prefix and branch from it. We use that record to show that applied actions must be audited against attempted ones, and to adjudicate feasibility claims by execution rather than by inspection." Everything in that sentence is checked. Nothing about "first economic sandbox", "first multiplayer benchmark" or "first state-checked communication" is defensible, and the draft correctly avoids those.

## 3. Central-idea challenge

**Is the protocol a contribution or a habit?** The abstract and introduction name "an exact-prefix audit procedure" as a contribution. The methods section describes it by example in one paragraph. There is no statement of inputs, admissible endpoints, certificate types, or how a conditional diagnostic is to be reported. Without that, the contribution is "we looked carefully". With it, the paper has a reusable method that the rivals verifiably lack. I supply a boxed procedure with three certificate types (feasible route, exhaustive infeasibility, rule lock) in `proposed_revision.tex`. (FN-02)

**What would falsify the central interpretation, and is the test possible in the retained record?** The central interpretation is that endpoints must be decomposed into opportunity, reachable sequence, response resolution and consequence. It would be falsified if the decomposition never changed a reading. It does: the per-configuration first-window split in Figure 2 (Sol 16/17, Gemini 17/18, Opus 7/15, Grok 3/13) decomposes, from the frozen exports, into nine groups never buildable in the window (all Opus or Grok), three buildable only later and unbuilt, and eight entry-buildable non-builds split 3 defaults / 3 conflicts / 2 holds. The gap is mostly access, then resolution, then choice. The prose never states this; the figure shows it without explanation. This is the paper's best evidence for its own thesis, and it is missing. (FN-01)

**Does the best rival already do it?** No. AgentMonopoly reports behavior profiles and persona effects with 140 games and a within-family size axis, and it suggests testing "decisions in identical game situations" as future work. It does not have attempt records, restore-and-branch, multi-exchange negotiation, or a liquidation phase. DECE has replay-and-resume and matched harness studies but no dialogue and no attempt accounting. Arena has the richest communication corpus but no replay, no legal menus and no complete ground truth.

## 4. External validity, rule quirks, size and dependence

- **Rule artifacts.** Intact creditor inheritance, non-auction of bank-returned deeds, no trade during liquidation, no management window in jail, and the one-dollar redemption overcharge are declared. The 54/60 winner-as-creditor and 57/60 developed-rent eliminations are plausibly inheritance-driven. The paper says "not a causal estimate" but offers no read-only diagnostic. The retained events allow one: for each elimination, whether the estate carried buildings and what the creditor later collected on inherited development. I recommend it as an optional existing-data analysis, reported descriptively. (FN-07)
- **The redemption overcharge is an implementation deviation, not a rule.** The appendix sentence is numerically exact (recomputed for all sixteen principals: trade interest exact everywhere; redemption +1 for 50, 90, 100, 110, 200). It should be labelled a known deviation with a statement of whether any verdict depends on it (the smallest payable margin in Table 4 is $8). (FN-16)
- **Size and dependence.** Five seed blocks; one block won entirely by Sol; one block won from seat 2 by all four. The paper handles this honestly. But the name "MonopolyBench" promises a score the paper deliberately does not deliver, and the introduction should say so as a position rather than leave it as an absence. (FN-17)
- **The Opus condition.** 1,604 of 1,696 decisions under a different prompt and tool schema, coinciding with a source-version boundary. The abstract now says so; no exhibit marks the row. Every table and figure with Opus needs a dagger. (FN-09)
- **Does a 34-page exploratory paper justify its scope?** Not as organized. Seven distinct results are each stated, re-stated with caveats, and restated in discussion, appendix Table 10 and conclusion. G4, G6, G11, G20 d1 and the G20 d235 budget branch are illustrative, not load-bearing. Target about twenty pages before references, with the chronologies and the case index in an appendix. (FN-10)

## 5. Findings by kind (details and exact passages in `findings.json`)

| ID | Severity | Kind | Provenance | One line |
|---|---|---|---|---|
| FN-01 | high | presentation | checked | Figure 2 per-configuration split unstated; decomposition is the thesis's best evidence |
| FN-02 | high | missing evidence | checked | Protocol claimed, never specified; boxed procedure supplied |
| FN-03 | high | presentation | checked | Public Apache-2.0 release with all twenty games exists; draft says it is outstanding |
| FN-15 | high | presentation | checked | Transferable result (resolution-produced actions) buried; lead with it |
| FN-04 | medium | demonstrated error | checked | AgentMonopoly "replay" is session playback, no restore in code |
| FN-05 | medium | missing evidence | checked | AgentMonopoly trades are single-offer; attribution finding cannot arise there |
| FN-06 | medium | missing evidence | checked | Attempt-level provenance differentiates from all four comparators; unclaimed |
| FN-07 | medium | missing evidence | checked | AgentMonopoly code also inherits buildings intact; rule-artifact share unexamined (optional analysis) |
| FN-08 | medium | demonstrated error | checked | DECE is Eurogames without dialogue, not "economic games" |
| FN-09 | medium | presentation | checked+inherited | Opus row unmarked in every exhibit |
| FN-10 | medium | taste | checked | Length not justified by distinct results |
| FN-13 | medium | missing evidence | checked | Arena ground truth is partial; ours is complete; say so from their paper |
| FN-11 | low | demonstrated error | checked | Table 9 cells: "not applicable" for withdrawal; quote the prompt |
| FN-12 | low | presentation | checked | FinBoardBench is focal-agent; we evaluate all four |
| FN-14 | low | presentation | checked | AgentMonopoly cap/winner rule in paper, not in runner code |
| FN-16 | low | presentation | checked | Redemption overcharge is a deviation; bound its effect |
| FN-17 | low | taste | checked | Say why no leaderboard score is proposed |

Prior-review findings I checked and found already resolved in the frozen draft (not re-listed): the 8B–32B/temperature/150-step sentence (final-review Fable F3), the single-author/not-redistributed clause (F4), the corrective-retry grouping (F5), the rounding sentence (F6; recomputed and exact), the G13 "prior motive" chronology (Opus H1; the draft now says the buyer weighs solvency after the seller's d250 appeal), the action-only trigger (Opus H2), the G20 d257 diagnostic acceptance (Sol 1).

## 6. Advisory scorecard

| Dimension | Score | Reason |
|---|---|---|
| Significance | 5/10 | One transferable result and one transferable method; the social findings are careful but local to one contract and five chronologies. |
| Soundness | 7/10 | Claims bounded; comparator facts verified with the exceptions in FN-04, FN-08, FN-11. Downgraded for the unexamined rule-artifact share and the unmarked harness condition. |
| Novelty | 5/10 | Raised from my pre-verification 4. Verified differentiators: attempt records, restore-and-branch, multi-exchange threads, liquidation-phase feasibility tests, deception-permitting contract. The draft argues from rule differences rather than from these. |
| Clarity | 4/10 | Honest but exhausting; contribution described, not specified; key decomposition in a figure only; caveats repeated five times. |
| Reproducibility | 6/10 | Artifacts public with prompts and responses; engine replays action streams. The paper does not say so; no external reproduction; analysis directories untracked. |

## 7. Three strongest rejection reasons

1. **No identifiable scientific claim.** Five seed blocks, four configurations at one condition each, no ranking, no rate, no effect estimate. The advertised protocol is shown by example and never specified or evaluated against an alternative.
2. **The best rival already occupies the genre.** AgentMonopoly offers Monopoly with a deterministic engine, legal menus, a bluffing prompt, open code, 140 games and a within-family size axis. The draft distinguishes itself by rule variants rather than by the measurement capabilities the rival verifiably lacks.
3. **A confounded cohort presented as a peer comparison.** One configuration played 1,604 of 1,696 decisions under a different prompt and tool schema, the shift coincides with a source-version boundary, and every exhibit presents that configuration as a peer row.

## 8. Three changes most likely to improve the paper

1. **Lead with the resolution-produced-action result and the opportunity decomposition.** Open the abstract with it; add Table `tab:first-window-decomposition`; put the exact-prefix procedure in a box with its three certificate types. (FN-01, FN-02, FN-15)
2. **Rewrite related work as a sourced capability matrix.** Attempt records, restore-and-branch, negotiation protocol, liquidation phase, estate rule, conduct contract, ground truth, release. Correct the AgentMonopoly "replay" and DECE "economic games" glosses. (FN-04 to FN-08, FN-12 to FN-14)
3. **State the public release, mark the Opus condition everywhere, and cut to about twenty pages.** (FN-03, FN-09, FN-10)

## 9. Decisions only the author can make

- Whether to name the repository URL (Variant A in `proposed_revision.tex`) or use an anonymized statement (Variant B).
- Whether to run the optional read-only inheritance diagnostic (FN-07) before the next round.
- Whether to accept the length cut (FN-10), which is a taste judgment.
