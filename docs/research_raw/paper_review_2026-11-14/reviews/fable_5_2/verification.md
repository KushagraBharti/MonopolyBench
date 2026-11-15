# Verification record, Fable 5.2

Review of 14 November 2026. This file lists what I checked, how, and what I did not check.

## Pin

`../../../paper_revision_2026-11-12/final_manuscript_manifest.json` lists 84 files.

| When | Files | Mismatches | Manifest SHA-256 | PDF SHA-256 |
|---|---|---|---|---|
| Before any work | 84 | 0 | 04d0a0d3…5e5460 | 5ab7b1c4…518e52 |
| After the six outputs were written | 84 | 0 | 04d0a0d3…5e5460 | 5ab7b1c4…518e52 |

I edited no file under `paper_revision_2026-11-12/` or any earlier folder.

## Scope kept

- No game, engine execution, replay, saved-request probe, baseline run, synthetic state, policy rollout, provider call or verifier search.
- No prompt, engine or manuscript change.
- No commit and no push by me. A checkpoint commit `863f8ef7` by the repository owner's account appeared at 19:18 on 14 November while I was working. It contains files from this folder as they stood then. I did not make it. Before it, local `origin/main` was `a10419d23` of 29 October.
- No subagents.
- I wrote only under `reviews/fable_5_2/`. Temporary files (rendered PDF pages, extracted paper text) went to the session scratchpad.
- I did not open `reviews/astra/`, `reviews/sol/` or `reviews/opus/` before these six outputs were complete. I listed directory names once when creating my folder and saw file names in `git status`.
- `initial_position.md` was written before any raw record, source file or outside paper was opened for this round. Its SHA-256 is 11e341a8…47d24f.

## What I read in full

- `BRIEF.md` and all three input files.
- The 12 November manuscript: every section source, all sixteen initial fields, all generated tables, the five quotation-card files, and the stored system prompt. I rendered the PDF to images and looked at pages 5 to 7 for the layout claims. I extracted the text of all 21 pages for word counts and the reference list.
- `handoff.md`, `evidence_map.md`, `FINAL_REVIEW_DECISIONS.md`, `INTEGRATION_DECISIONS.md`, `findings_and_limits.md`, `literature_notes.md` and `README.md` in the integrated folder.

I did not open the recovery prompt file separately. The command that would have printed it failed after printing the standard prompt, and I relied on the manuscript's description of it.

## Checks on original records

All scripts are in `tools/`, use the Python standard library, and only read `decisions.jsonl` files, the board contract and the integrated paper's data files. `lib.py` is a copy of the read-only helper from my 12 November final review.

| Check | Script | Output | Result |
|---|---|---|---|
| Rebuild all financing episodes from raw decisions | `episodes.py` | `data/episodes_188.json` | 188 episodes, none unmatched against the paper's ledger |
| Outcomes, first actions, forced menus, payment action counts | `census.py` | printed | 128 paid, 60 eliminated. 132 and 56 by bound, 3 and 50 first-menu declarations, 8 forced, 6 above-bound financing starts. 180 mortgages, 89 sales, $51,997. 67 one-action payments |
| Resource partition and the middle row of Table 2 | `partition.py` | printed | 62, 53, 16 payable and 62, 52, 14 paid. In the middle row 47 paid without a released mortgage, 5 paid with one, 1 declared. 19 payments use 33 released mortgages |
| Every channel for the sixteen first decisions | `sixteen_dump.py`, `dump.py` | `data/sixteen_first_decisions.txt` | Read in full. Applied note, public message, assistant content, provider text, attempts, menu, bank stock, holdings, ten carried notes |
| Executed routes and end cash for the sixteen | `sixteen_routes.py` | `data/sixteen_routes.json` | Read in full |
| Every channel for every decision of the six above-bound attempts | `six_dump.py` | `data/six_above_bound.txt` | Read in full, with long Grok provider summaries read at head and tail |
| Named action in content against applied call, all liquidation decisions | `conflicts.py` | `data/liquidation_named_vs_applied.json` | 338 decisions, 9 conflicts, all Grok |
| G20 d291 and G20 d327 cash sequences | inline script | printed | 275, 725, 845, 955, then $25. 49 plus 700 plus 665 minus 1,400 is 14 |
| Note argument position, channel availability, timeline entries | inline script | printed | Note last in 42/42 Sol, 35/38 Grok, 23/50 Gemini first liquidation calls. G18 d313's timeline shows Gemini's sale and mortgage |
| Exact interval and Fisher arithmetic | `stats.py` | printed | 61.7 to 98.4. p = 0.039 against 115, 0.13 against 53 |
| Liquidation composition without search | `composition.py` | `data/liquidation_composition.json` | Sales in 2 of 62 where listed mortgages sufficed. No excess sale of $100 or more in the 52 that needed one |
| Keyword screen for two rule beliefs | `rule_screen.py` | printed | Inherited-interest wording in 8 liquidation decisions, 7 Grok |
| Opening-offer contrasts from raw decisions | `bargaining_recount.py` | printed | 920 responses, 918 with legal acceptance, and all four contrasts and eight recipient strata as printed in the paper |
| Provenance of the necessity cut | `grep` in the 11 November feedback folder | printed | The cut first appears in the referee's inline review of 11 November |
| Citation counts | `grep` over section sources | printed | 16 keys on 11 November, 12 on 12 November |

## Checks on source code

Read with `git show` and directly, at run commits `42f85183` and `d6808534` and in the working tree. The two run commits differ only in campaign setup, execution policy, supervisor, one API file, tests and one schema. The working tree has no change under `python/` or `contracts/` since the second.

- `python/packages/arena/src/monopoly_arena/decision_resolver.py`, `_fallback_action`, lines 624 to 817.
- `python/packages/arena/src/monopoly_arena/llm_runner.py`, `_fallback_action`, lines 709 to 895. Unreferenced.
- `python/packages/engine/src/monopoly_engine/engine.py`: `_build_liquidation_decision`, `_compute_liquidation_options`, the two payment-queue entry points, `_resolve_pending_payment`, `_mortgageable_space_indices`, `_sellable_building_space_indices`, `_apply_mortgage`, `_apply_sell_plan`, `_validate_sell_plan`, `_unmortgage_cost`, `_handle_bankruptcy`, and the trade interest calls.

The statement that every sequence of offered financing actions pays in a hotel-free state is an inference from this code. I did not run the fallback or any other policy, and I did not trace a policy through a state step by step. For G20 d327 the argument is a bound: two hotel downgrades need eight bank houses and the state has fifteen.

The no-release routes for five episodes in the middle row of Table 2 are hand arithmetic from recorded holdings and the sale rule. They were not executed.

## Checks on literature

See `literature_matrix.md` for each source, version and depth. In short: three PDFs were read as extracted text on this machine (PlanBench, the EMNLP 2026 menu paper, the Hasbro rules). The rest were read through a fetch tool that returns a model's summary with short quotes, and two long pages were covered only to their first 100,000 characters.

I sent no project or personal detail to any outside service. I did not fetch the project's own public repository, because its URL carries the owner's name. Its state was read from local git refs.

## Limits

1. **Model reading.** The sixteen-case table, the carried-note table and every description of a text are my reading. I am a language model. None of it is human validation. I am an Anthropic model, as is one of the four evaluated systems (Claude Opus 5.5). I am a different model from it.
2. **Conflict detection covers one system.** Only Grok's assistant content names an action in liquidation decisions. A text-versus-call conflict in another system would not be found by `conflicts.py`. For the other three I compared notes with calls only in the episodes I read in full.
3. **The other 172 first texts were not coded.** I read all channels for the sixteen necessity episodes and for every decision of the six above-bound attempts. For the rest I have the applied action and the named-action check.
4. **Keyword screens.** `rule_screen.py` matches words. It can miss paraphrases and can match sentences that mention a rule without relying on it. I read every hit it printed.
5. **Hotel states.** For the 23 payable debts with a hotel at entry I make no claim about what a fixed policy would do, apart from G20 d327.
6. **Inherited results.** The three payment witnesses for the payable declarations and the G7 menu search come from the stored audit of October. The 61 of 74 semantic count comes from earlier model codings. The 139 Grok conflict total and the refusal accounting come from earlier rounds. I did not redo these.
7. **Incidents.** I did not recheck the eight incidents or the 21 quotation cards this round.
8. **Literature.** No search was run beyond the sources the feedback names. Nothing in this review supports a claim that some analysis has never been done.
9. **Costs, ratings and acceptance.** I verified the arithmetic of the per-decision cost and nothing else. I adopt no rating and make no forecast.
10. **Timeline claims.** I did not verify "25 hours" or the full sequence of earlier titles.

## Files in this folder

- `initial_position.md`, `review.md`, `claim_ledger.json` (108 entries, generated by `tools/build_ledger.py`), `literature_matrix.md`, `recommendations.md`, `verification.md`.
- `tools/`: the scripts named above.
- `data/`: their outputs.
- `cross_review.md` was added afterwards, once the six outputs above were complete. It does not change them.
