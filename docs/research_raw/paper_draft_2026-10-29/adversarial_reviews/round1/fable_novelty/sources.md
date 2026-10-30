# Sources inspected for the Fable novelty review (2026-10-29)

All fetches were made on 2026-10-29 through a page-to-markdown fetcher that answers questions against the page text. Where a page was longer than 100,000 characters, two passes were made (offset 0 and 100,000). "Verified" means the stated fact appears in the fetched text. "Not stated" means the fetched text does not mention it; absence of mention is not evidence of absence.

## Primary comparator sources

| Source | Version inspected | What was checked |
|---|---|---|
| AgentMonopoly paper | arXiv:2610.29330 abs page (v1 21 Oct 2026, v2 22 Oct 2026, current) and html v2 | Rules (§4, App. A.1), 150-step cap and net-worth winner, temperature 0, eight models 8B–32B (Table 4), 140 games (Table 3), prompt summary (App. A.2), legal-action lists, invalid-output recording, trade protocol, rent waiver, replay mode (App. A.1, Fig. 7), limitations |
| AgentMonopoly repository | github.com/SuELS-Group/Agent_Monopoly, `main` (README rendered page, raw README, raw `backend/engine.py`, raw `backend/agent.py`, raw `backend/run_experiments.py`, raw `backend/server.py`, git tree via API) | Apache-2.0; experiments table totals 120; bankruptcy semantics in code (creditor receives properties with buildings intact; no liquidation); single-offer trade with accept/reject only; even-build rule on build only; no house supply limit; no sell-buildings function; `DEFAULT_MAX_TURNS = 600` in the runner; no net-worth winner logic in the code read; session JSON per turn with last 50 log lines; prompts and raw LLM output not stored as fields; forced `pass` on parse failure or hallucinated target; no restore or replay function; prompt text: "ENCOURAGED to be deceitful", "public message must match the reality of your action", "SECRET RULE OVERRIDE: You are allowed to form secret alliances" |
| Vending-Bench Arena communication paper | arXiv:2608.14825 abs page (v1 14 Aug, v2 18 Aug, v3 21 Aug 2026) and html v3, two passes | 2,583 emails, 20 runs, 79 agent-runs, 13 models; Stage A/B/C pipeline; single-author 50-email check; 525 verifiable transfer promises; no conduct instruction (§2.1); environment not redistributed; replay not stated; legal-action list not stated; capability results (ρ = −0.07) |
| Vending-Bench | arXiv:2502.15840 abs page (v1 only, 20 Feb 2025) | Single version; abstract |
| Vending-Bench Arena page | andonlabs.com/evals/vending-bench-arena | 14 rounds; 3–5 agents; email, money and goods transfer; individual scoring; qualitative only; release not stated |
| Vending-Bench 2 page | andonlabs.com/evals/vending-bench-2 | Simulated year; note-taking and reminder tools; adversarial suppliers; no separate paper; release not stated |
| DECE | arXiv:2610.35773 html v1, two passes | Ten Eurogames; no dialogue (§3.1, App. A.1); 12 configurations, 480 primary matches, 1,032 total; matched harness studies (72 and 48 matches); persisted state, replay and resume (App. D.7); retries and fallbacks disabled for expansion results; branching and invalid-action audit not stated; release not stated; title "Eurogame" singular on arXiv |
| FinBoardBench | arXiv:2605.27896 html v1 | Three games; bankruptcy: buildings to the bank, property to the creditor with mortgage interest; structured trades with ACCEPT/REJECT/COUNTER and a reason field; 108 matches; one focal model vs three fixed opponents; judge-rated trades; release not stated |
| Emergent Collusion | arXiv:2609.24967 abs page (v1 21 Sep, v2 26 Sep 2026) | Two-agent verification protocol; 94% of trajectories; more capable models in the same family collude earlier |
| Cattle Trade | arXiv:2605.14537 abs page (v1 14 May 2026) | MALGAI workshop at ICLR 2026; seven LLMs and three code agents; 242 games; heuristic agents outperform most LLMs |

## Local sources

| Path | Use |
|---|---|
| `baseline/monopolybench-first-draft/sections/*.tex`, `references_source.bib`, `evidence_map.md`, `verification.json`, `assets/*.png` | Complete read of the frozen draft |
| `baseline/monopolybench-first-draft/data/t03_trade_groups.json`, `t09_entry_nonbuild_records.json`, `t06_eliminations.json`, `t01_cohort.json` | Read-only decomposition (`analysis/decompose_first_window.py`) |
| `contracts/data/board.json`; `python/packages/engine/src/monopoly_engine/engine.py` lines 1786 and 2490 | Rounding recheck |
| `python/packages/arena/src/monopoly_arena/prompting.py` lines 1225–1250; `player_config.py` line 38 | Contract wording |
| `python/packages/engine/src/monopoly_engine/replay.py` | Existence of action-stream replay |
| `git ls-files saved_games` and `gh api repos/KushagraBharti/MonopolyBench` | Public release status: public, Apache-2.0, 118,653 tracked files under `saved_games/railway-research-*`, including `run/events.jsonl`, `actions.jsonl`, `decisions.jsonl`, `state/`, `prompts/` with system, user, tools, response and retry files |
| Prior material read only after `initial_position.md` was saved: `charter.md`; `round1/sol_evidence/initial_position.md`; `baseline/.../final_review/{fable,opus,sol}/findings.md`; `coauthors/fable/critique_and_corrections.md`; `paper_phase3_2026-10-29/fable/literature.md`; `paper_phase3_2026-10-29/opus/exhibits/normative_contracts.md` | Marking inherited versus checked |

## Not available or not verified

- The Arena agents' own system prompt text (Appendix H holds judge prompts, not agent prompts).
- Whether DECE, FinBoardBench, Cattle Trade or the Arena paper release code or logs: not stated in the fetched text.
- AgentMonopoly's 150-step cap and net-worth winner: stated in the paper (§4, App. A.1) but not found in the repository code fetched (`run_experiments.py` uses a 600-turn default and prints the first non-bankrupt player). The paper governs what was run; the repository state may postdate or predate the experiments.
- The AgentMonopoly paper's "five seeds" per configuration and the identity of the renamed streets were not rechecked in this pass.
