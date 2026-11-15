# Verification and scope

All writes for this review are under `docs/research_raw/paper_finalization_2026-11-14/final_review/sol/`. The candidate and four frozen drafts were read only. No game, engine import or execution, replay, policy, search over game states, synthetic scenario, provider call, judge probe or new annotation study was performed. No subagent, commit, push, external message or memory write was used. Repository behavioral tests were not run because they would exceed the explicit no-new-evaluations scope.

## Reading order and coverage

1. Read `FINAL_REVIEW_BRIEF.md` and `BRIEF.md` first, then the complete four manuscript arguments and their appendices and handoffs. Read their dissent and build instructions as well. The review used active LaTeX input graphs, numerical tables, recorded quote fields and full-channel supplements. Superseded integrated section prose was also inspected and distinguished from active claims.
2. Read the entire integrated argument, all appendix sections, the sixteen complete response records, eight full incidents, all active figures/tables, prompts, README, evidence map and the relevant build/check scripts. Inspected every integrated page in the five contact sheets under `document_build/qa/`.
3. Wrote `initial_position.md` before opening `INTEGRATION_DECISIONS.md`. The transcript records that order. No other reviewer's final-review folder was opened.
4. Read the integration decisions and assessed adopted and declined content. The final review retains an independent disagreement about preference language and identifies the strongest omitted positive example.

The repeated note, explanation and assistant-content fields for all sixteen cases match across all four frozen drafts and the integrated extraction. `reviewer_checks.json` records 116 nonempty field-hash comparisons, 29 per draft. Reformatting of a repeated field is not treated as new scientific evidence. Distinct authored interpretations, numerical qualifications and incident continuations were read separately. This was not an independent manual recoding of the full 188-response or 920-offer populations.

## Pins

The initial comparison in `pin_before.json` confirms all 2,396 listed files with zero mismatches. Manifest SHA-256 is `a362c4c6d020adb115a50b919d85d3db6777d223189493d7c4edd1517885e269`. The integrated PDF is `e5c44bebfb1d6b0b7c434d875261be63b11e4c6457396ee97596457a0c840dae`.

`historical_pin_before.json` confirms all 84 files in the November 12 `final_manuscript_manifest.json`, with zero mismatches. The final comparisons are recorded in `pin_after.json` and `historical_pin_after.json`. They cover the same files and manifest bytes, not merely the PDFs. No pinned file was edited.

## Isolated static build and document checks

Copied static TeX, bibliography, assets, data and inspection tools to `document_build/` inside this review directory. The first build ran before source-refresh commands and required no raw game input:

```sh
bash docs/research_raw/paper_finalization_2026-11-14/final_review/sol/document_build/build.sh
```

It succeeded using LuaLaTeX 1.24.0 and latexmk. There are 29 pages. Main text ends on page 7, references occupy the remainder of pages 7 and 8, and the appendix starts on page 9. The source declares 10-point type and 0.75-inch margins. Figure labels, tables, long fields, transcript cards and prompts were visually inspected. The automated check found no reported overfull boxes, missing characters, undefined references, warnings, out-of-page text or blank pages. `document_build/qa/verification.json` contains the result.

The rebuilt PDF SHA-256 is `b3cf0a468f1b43fc8fdd520b99cefb8b3dd6722e66a18e735dc061dba6cfdaad`. It differs from the frozen PDF, so I do not claim bitwise build reproducibility. All 29 per-page text extractions are identical, and all 29 page renders at 72 dpi are byte-identical in their pixel samples. See `document_build/qa/build_comparison.json`. Metadata visible through PyMuPDF also matches. The original candidate hash remains unchanged.

Verification used the already installed document-only Python environment in the frozen Sol draft, with `PYTHONDONTWRITEBYTECODE=1`, and wrote all results in the review copy. No environment installation or library modification was performed. The system Python lacked PyMuPDF; that dependency check did not affect the build.

## Existing-record checks actually rerun

Read each invoked script before running it. All commands below targeted the review copy under `document_build/tools/`:

| Script | Observed result |
|---|---|
| `refresh_records.py` | 6,989 decisions, 8,679 attempts, 50,918 events; 188 debt entries; 62/53/16 partition; 108/12/9/2 proof-premise partition |
| `prepare.py` | Original fields for all 188 first responses checked; 29 nonempty fields printed across sixteen focal cases |
| `check_sources.py` | 59 retained quote entries checked; 920 original response/action joins; $51,997 paid; 180 mortgage and 89 sale calls; 67 one-action and 61 multi-action payments; 84 protected historical files unchanged |
| `check_integrated_additions.py` | All thirty preservation memberships and episode action sequences checked against original resolved decisions; 28 without sales; three G7 spans checked; recipient receipt of the public counter checked |
| `check_stated_totals.py` | 43/48 numeric matches, with first matches in thirty notes and thirteen explanations; per-configuration cells reproduced |
| `verify_document.py` | 23 displayed casebook quote uses and all 29 focal fields present in PDF and exact original sources; no document diagnostics or page-boundary failures |
| `reviewer_checks.py` | 116 repeated-field hashes match; 121 entries with unlisted principal; selected 37 subset confirmed; 74 refusal population disjoint from author-only/neither offers; 63/63/61/4/9 coding counts and historical source byte identity confirmed |

The regenerated `episodes_188.json` is a fresh extraction of existing records. It is not a newly collected evaluation. The source checks read saved historical replay and audit reports, then confirm their reported statuses. They do not execute those reports' procedures.

## Source reasoning versus inherited execution

I inspected `_resolve_pending_payment`, `_mortgageable_space_indices`, `_sellable_building_space_indices` and `_validate_sell_plan` in `python/packages/engine/src/monopoly_engine/engine.py`. This supports the invariant, positive-proceeds termination, persistent mortgages, hotel-stock obstruction, final-state bundle validation and no-dead-end reasoning. The recorded holdings supply complete ownership/evenness and the four premise classes. I accepted the proof as mathematical source reasoning. No state transition, policy or trajectory search was run.

The three executable payment witnesses, G7 restricted-menu search, construction audit, original replay results, negotiation classifications, resampling draws, semantic labels and longer historical incident event traces remain inherited. The review checked original response/action joins and selected quote reception, but did not independently regenerate every historical classification or continuation. Reading twenty passing report pairs and the 50,918-event comparison total is not rerunning replay. Model-reader agreement is not human validation.

## Claim-directed literature checks

These are targeted primary passages, not claims of full fresh reading of every cited work:

| Primary source | Passage checked and conclusion |
|---|---|
| [FinBoardBench v1](https://arxiv.org/html/2605.27896v1) | Appendix C property management and mortgage rules, especially the financing paragraph. Supports the statement that financing by mortgage and building sale is prior work. Does not verify the executable policy for declaring on a payable debt. |
| [ACPBench v1](https://arxiv.org/html/2410.05669v1) | Section 3.2, action reachability. Confirms the prerequisite/reachability construct. The AAAI page returned Access Denied, code 721f8919e3f51e7f; the original arXiv paper was available. |
| [PlanBench o1 evaluation v1](https://arxiv.org/html/2409.13373v1) | Table 3 and unsolvable-instance discussion document false impossibility on solvable instances. Supports the integrated general comparison without adding a new result. |
| [The Menu Is an Execution Prior](https://aclanthology.org/2026.emnlp-main.1577.pdf) | Table 6 and section 4.3 hold candidates fixed and change ordering. Supports presentation sensitivity in that study, not a causal result here. |
| [Guhe and Lascarides](https://www.pure.ed.ac.uk/ws/files/19353900/CIG2014.pdf) | Section VI says embargo recipients always comply. Supports the integrated qualification about imposed compliance. |
| [AgentMonopoly v2](https://arxiv.org/html/2610.29330v2) | Environment and scope passages document persona/behavior analysis and negative-cash elimination. Supports the local comparison. |
| [Commerce communication study v3](https://arxiv.org/html/2608.14825v3) | Methods classify each email; Stage A has a human-label validation set. Supports the integrated population/validation distinction. |
| [Hasbro comparator](https://www.hasbro.com/common/instruct/monins.pdf) | Selling, mortgage and bankruptcy clauses. Confirms the shared mortgage-release rule and the settlement/hotel-sale differences discussed in the paper. |

Other comparisons retain the prior primary-source readings documented in the drafts' evidence maps. No literature experiment was executed, and no novelty-absence guarantee is inferred.

## Release limits

The static local build, original-record checks and pinned-file checks succeeded. The provisional archive was neither regenerated nor judged as a final release. I did not test a fresh anonymous download, external repository availability or an extracted final archive outside this checkout. The final packaging step remains the owner's already identified task. Unreferenced superseded section fragments are an optional source-navigation concern, not missing scientific analysis.
