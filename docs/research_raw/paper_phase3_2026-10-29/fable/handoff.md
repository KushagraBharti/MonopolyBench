# Fable phase-3 handoff (steps 11–14), 2026-10-29

All work is under `docs/research_raw/paper_phase3_2026-10-29/fable/`. No canonical game, prompt, engine, prior research record, commit or push was changed. No paid provider call and no new game. Scripts are read-only and were run with `python -I` from outside the data directories.

## Deliverables
- `initial_position.md` — independent full-scope position, saved before reading any phase-3 peer proposal.
- `literature.md` — 15 primary sources inspected today with URLs, versions, sections and status labels (PR/WS/PP/EP/SW), bounded comparisons, "not reported in inspected sections" where applicable, and a list of failed or unverified references. Includes the Vending-Bench Arena paper (arXiv:2608.14825v3), AgentMonopoly paper and repository (140 vs 120 games recorded), FinBoardBench, Cattle Trade, DECE, the promise papers, SOTOPIA, NegotiationArena, Concordia, MACHIAVELLI, the agent benchmarks, METR, HAL, evaluation-validity and CoT-faithfulness references.
- `references.bib` — 33 entries, each with the checked URL and status in its note field.
- `comparison.json` — 12 sources × 21 dimensions with per-cell provenance; bounded differentiators; claims not to make.
- `experiment_decisions.md` — claim-to-experiment matrix in four tiers (existing support / existing-log analysis / optional strengthening / experiment only if claimed). Decision: no ready claim needs a new paid game.
- `figure_table_plan.md` — seven main figures, seven tables, six appendix exhibits with source paths, units, caption text, checks and verification needs; audit notes for Astra's build.
- `detailed_outline.md` — venue-neutral outline with argument, evidence IDs, exhibits, citation keys, alternative explanations and transitions per section; cross-cutting manuscript rules.
- `debate.md` — chronological record with authorship, accepted corrections, my own errors, unresolved dissent.
- `exhibits/house_stock_series.csv`, `house_stock_report.json`, `house_stock_grid.png` (script `scripts/house_stock_series.py`): bank houses/hotels after every building event in all 20 games; validated against the delivered bank state at all 6,989 decision requests (0 mismatches); minima equal both phase-2 audits; nine zero-stock games; first-zero turns; decisions taken at zero stock.
- `exhibits/first_management_causes.json|csv` (script `scripts/first_management_causes.py`): first-management-turn outcome of all 63 trade-completed groups by cause (built / never legal in window / default after refusal / other default / received conflict / valid END); reconciles with Opus's eight-case residual on the 42 entry-buildable groups.

## What is established, in one paragraph
The twenty-game cohort supports configured-agent economic profiles, exact local feasibility findings and a bounded social chronology (Astra R01–R25), none of which requires new games. The closest competitors (Arena paper, AgentMonopoly, FinBoardBench, DECE) already provide multi-agent economics, legal menus, deterministic engines, replay, state-checked speech and explanation disclaimers; the bounded differentiators are exact-prefix multistep applied-vs-feasible auditing, integrated all-player longitudinal consequences under a declared inheritance variant, all-channel per-attempt provenance with declared availability, a normative contract that permits public deception (so social findings are chronologies, not a misalignment class), public replayable artifacts, and uncapped bankruptcy endings with a liquidation phase.

## Original-check limitations
- Literature: abstracts only for AgentBench, WebArena, OSWorld, τ-bench, AgentDojo, MLE-bench, TheAgentCompany, SOTOPIA, Concordia, MACHIAVELLI, AgentBoard, HAL, Cattle Trade, DECE, the promise papers and the CoT papers; full html for AgentMonopoly v2, FinBoardBench v1 (selected sections) and the Arena paper; pages for Vending-Bench 2, Arena and METR. FinBoardBench §4.3/App. C.3 and DECE §3.2/§4.3/A.3 are Sol's and Opus's reads, attributed. Zhu et al. and Miller were located by search, not fetched. `commitment_standing` and `empty_commitments` (Sol's references) are unverified by me.
- Data: my two new scripts validate against delivered prompt states and the phase-2 audits; they do not re-derive the phase-2 semantic judgments. G13 d251/d253 returned reasoning was re-read in the original decision records today; other case quotes rely on the phase-2 checks cited.
- Exhibits: two built and inspected; the rest are specifications. Astra's nine figures were inspected and reconciled against audit files; caption requests are in `debate.md` D6.
- The CRN-horizon medians (75.5 landing, 78 seat) are from my phase-1 CSV and should be recomputed at regeneration.

## Suggested next steps for root assembly
1. Merge the three outlines (Astra, Sol, mine) section by section; the section structures are compatible (environment → design → economic → social → validity → capability/alignment → limitations).
2. Adopt one seat convention (one-based) and one short name for Gemini 4 Argon across all exhibits.
3. Add the first-management cause split under Astra's F04 or as a companion table; add the stock grid to the appendix with the hotel-conversion note.
4. Decide on the optional codings (dissent preserved in `debate.md`).
5. Keep `comparison.json` cells with their provenance when building the related-work table; do not promote "not reported in inspected sections" to "absent".
