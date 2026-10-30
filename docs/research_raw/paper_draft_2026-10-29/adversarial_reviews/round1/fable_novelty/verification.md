# Verification record (Fable novelty review, 2026-10-29)

## What I did myself

1. Read every section file of the frozen draft, the source bibliography, the evidence map, the README, `verification.json`, and the four figure PNGs. Saved `initial_position.md` before opening any prior review, the charter, or coauthor folders.
2. Fetched the primary comparator sources listed in `sources.md` and checked each specific comparator claim in `introduction.tex`, `economic_methods.tex`, `social_results.tex`, `discussion.tex`, `related_work.tex` and the appendix Table 9 against the fetched text.
3. Fetched four raw source files of the AgentMonopoly repository to test rule and infrastructure claims against code rather than README prose.
4. Ran `analysis/decompose_first_window.py` (read-only, frozen exports only). Output in `analysis/results.json`. It asserts the draft's 63/43/42/34/8 totals and produces the per-configuration decomposition that Figure 2 shows but the text omits.
5. Recomputed the floating-point ceiling check for all sixteen board principals from `contracts/data/board.json` and the two engine lines. Result: trade interest equals the exact ten percent for all sixteen principals; redemption overcharges by one dollar for principals 50, 90, 100, 110 and 200. This matches the appendix text exactly.
6. Confirmed the contract wording quoted in `social_results.tex` against `prompting.py` lines 1225–1250 and `player_config.py` line 38.
7. Confirmed the public release status of the repository and the tracked research games with `gh api` and `git ls-files`.

## Comparator claims in the draft: verdicts

| Draft passage | Verdict | Evidence |
|---|---|---|
| Arena study "analyzes 2,583 emails from twenty year-long runs, combining a language-model judge, deterministic checks against simulator records and reasoning-summary analysis" (related_work) | Verified | 2608.14825v3 abstract, §4.1 |
| "It also examines promise follow-through" | Verified | §5.1.3, App. D (525 verifiable transfer promises) |
| "Its validation uses a single-author label check, and the environment is not publicly redistributed" | Verified | §6, §2.1 |
| Arena "applies an external taxonomy to agents given no conduct instruction" | Verified | §2.1: instructions contain no conduct instruction; archived payloads contain no deception-related terms |
| Arena "reports no capability association under its economic ordering" (discussion) | Verified | §5.3.2: Spearman ρ = −0.07, p = 0.83; capability-gap OR 1.04 |
| AgentMonopoly "bankruptcy rule eliminates a cash-negative player without our mortgage-and-sale liquidation phase" | Verified | Paper §4; engine.py `_declare_bankruptcy` has no liquidation |
| "its prompt prohibits public/action contradictions" | Verified, and understated | agent.py: "CRITICAL: While you can lie about your motives, your public message must match the reality of your action" |
| "eight open-weight models range from 8B to 32B parameters and use temperature zero; a 150-step cap invokes a net-worth winner" | Verified in the paper; the cap and net-worth winner are not in the repository code read | Paper §4, App. A.1, Table 4; run_experiments.py `DEFAULT_MAX_TURNS = 600` |
| "paper reports 140 games, while the repository experiment table totals 120" | Verified | Table 3 (40+40+40+20); README table (40+40+20+20) |
| "Its paper and repository describe legal-action lists, a deterministic engine, replay and per-turn records" | Partly misleading | Paper App. A.1 describes "an interactive mode for online replay and analysis of game sessions"; README and code show per-turn snapshot files and no restore or re-execution function. "Replay" here is playback of a session file, not engine re-execution |
| FinBoardBench "Monopoly bankruptcy treatment sells buildings" | Approximately verified | App. C.3 / rules: buildings go to the bank when owed to a player, are demolished and auctioned when owed to the bank; the property passes to the creditor. "Returns buildings to the bank" is more precise than "sells" |
| DECE "evaluates complete model–harness configurations across economic games ... matched harness studies, persisted state, legal interfaces and replay" | Verified except "economic games" | §3.2, §4.3, App. D.7. The games are ten score-based Eurogames; Splendor, Century and Brass have economic themes. No trading between players |
| DECE "its inspected design excludes" dialogue | Verified | §3.1, App. A.1 |
| Vending-Bench 2 "simulated year with memory tools and adversarial suppliers" | Verified | Andon eval page |
| Emergent Collusion "within-family differences under designed violation opportunities" | Verified | Abstract |
| Cattle Trade "heuristic baselines" | Verified | Abstract: three deterministic code agents, two outperform most LLMs |
| Table 9 AgentMonopoly "Withdrawal of an offer: Not addressed" | Better stated as "not applicable" | engine.py: single offer with accept/reject only; no standing offer can exist |

## Draft claims about its own infrastructure that I checked

| Claim | Verdict | Evidence |
|---|---|---|
| Appendix rounding sentence | Verified exactly | `analysis/results.json` `rounding_check` |
| Action-only retry removes the private-note field and shortens the honesty clause | Verified | `prompting.py` `build_refusal_retry_bundle` |
| "The complete applied action streams replay" is engine re-execution | Verified as capability (not rerun) | `replay.py` `replay_actions` constructs an `Engine` from seed and players and feeds the recorded actions |
| "A publication release should package the permitted raw artifacts ... The present draft records what has been reproduced locally without representing the completed release" (validation) | Underclaim | The repository is public under Apache-2.0 and tracks all twenty games with events, actions, decisions, state snapshots, prompts, responses, retry files and usage |

## What I did not do

- I did not rerun any engine branch, replay, or memory reconstruction. The 20-replay and 6,989-window claims are inherited from the retained phase-1 checks.
- I did not re-reduce events for any economic count beyond the frozen exports. The 43/63 and related totals are checked against those exports only.
- I did not read the Arena agents' prompt (not published in the fetched text).
- I did not run any game, provider call, or paid experiment. I did not edit any canonical, prompt, engine or shared draft file.
- Prior review findings that I agree with are marked "inherited" in `findings.json`; I re-derived only those marked "checked".
