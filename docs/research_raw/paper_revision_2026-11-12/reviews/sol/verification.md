# Verification and handoff

Completed 12 November 2026. All authored files, generated analysis, build outputs and renders are under `docs/research_raw/paper_revision_2026-11-12/reviews/sol/`.

## Reading and independence

- Read `CROSS_REVIEW.md` and `CHARTER.md` fully, and all 649 lines of `attached_review.txt` and all 129 lines of `inline_review.md` in the specified November 11 feedback folder.
- Read all four complete November 12 manuscript entry files, their substantive sections, appendices, quotation definitions, complete tables, prompts, handoffs, evidence maps and findings/limits. Fable's numeric macros were also resolved against its generated facts. The common inherited bibliography is byte-identical across Astra, Sol and Opus; Fable's bibliography and Opus's additional entries were read separately.
- `initial_position.md` was written after the charter and external feedback, before substantive draft cross-reading and before any new peer review. It discloses that the four manuscript entry files had already been inspected.
- Opened no other November 12 review folder and no new integration file. Read the four frozen authors as scientific alternatives, including my own Sol manuscript. Did not contact peers or launch a subagent.

## Fresh saved-record checks

`check_saved_records.py` reads original decision records for all twenty games and the retained ledgers. It imports no engine, arena or model client. `saved_record_checks.json` retains source hashes and row-level evidence.

| Check | Result |
|---|---|
| Entry resource bounds | Recomputed from original delivered holdings and menus in 188/188 episodes; equal to the retained ledger and Fable's independently rebuilt bounds |
| First applied action | Original resolved action equals both episode ledgers in 188/188 rows |
| Full first-action comparison | Above bound: 50 declarations, 4 mortgages, 2 sales. Payable: 3 declarations, 73 mortgages, 55 sales. Restricted G7: mortgage |
| Menus behind first declarations | 8/50 above-bound first declarations offer neither sale nor mortgage; 42 offer financing. All fifty are model actions, not fallback |
| Payable resource partition | 62/53/16 episodes with 62/52/14 payments |
| Necessary subset | All sixteen original selected first fields read, retained and printed; 13 explicit/aggregate successful statements, 1 tentative, 2 omission failures. Interpretation is a model reading |
| Necessity versus use | 19 paid use episodes, 33 mortgages absent from entry menus; 14 necessary and 5 with sufficient initial-resource arithmetic |
| G20 payment | Original turn-108 cash events give sales +$700, mortgages +$665 and rent -$1,400. Entry $49 and next decision $14 agree. No replay |
| Offer populations | 920 responses; 918 legal acceptances; 524 legal openings and 394 legal later offers. Full four-form tables and proposer/recipient strata recomputed from retained rows |
| Cash asks | 96 openings and 104 later offers, kept distinct from residual forms |
| Semantic population | All 74 membership rows rejoined: 38 recipient-only and 36 both-completing direct rejections; disjoint from proposer-only/neither focal cells. Labels not recoded |
| Composition and uncertainty | Original Grok opening calls checked for action-name disagreement; all four exact intact-block resampling variants recomputed over 3,125 draws each |
| New explanatory slices | Capacity-bin counts and list-price medians/positive-value subsets recomputed. Their substantive limitations are retained |
| Numerical claims | Read all sixteen fields, Fable's fifteen selected check definitions and Opus's statement-level reading. G2 $430/$400 and the two incorrectly labeled maximum assessments are explicit. The 14/15 statistic is not adopted as recalled-value accuracy |
| Configuration | Read 8,687 saved outgoing request intents. Grok required, others auto; medium effort, parallel calls off, no temperature, top-p or max-tokens field. These intents are distinct from 8,679 resolved-record attempts |
| Response-size/accounting claims | Reported reasoning-token means reproduce. Reporting denominators are Sol 1,991, Gemini 1,689, Opus 1,701 and Grok 1,695. Opus has 3,301 attempts and Grok 1,698, so missing usage is explicit. Completion-token accounting was also recomputed, but no comparative cognition or new response-size result is inferred |
| Quotations | 160 manifest entries checked against original fields and spans, including duplicates across authors; this is not 160 independent quotations or judgments |
| Receipt | Ten selected public messages found in subsequent original counterpart requests, including G13, G18, G19, G15, G7 and G20. Receipt is not belief or persuasion |
| G18 motive | Read Opus's original d421–461 text fields; no inherit/estate/creditor terms. The earlier d431 survival explanation and d442 withdrawal remain distinct from terminal inheritance |
| Stored replay reports | Read all twenty artifact and twenty state reports; within-mode hashes equal and statuses pass. Counts total 50,918 full events and 24,506 state events. No replay executed |

Original episode boundaries, the full offer reconstruction, event-based outcomes and the three payable-failure classifications are retained historical inputs. I recomputed bounds, joins, actions and tables without independently rebuilding the entire event detector. The historical three legal payment witnesses and G7 search were not executed. The complete 61/74 reason labels, most investment/rent/estate summaries and most non-G20 incident continuations remain inherited from source-linked frozen analyses. This pass checks quotation correspondence and selected receipts; it does not recreate every prior inference.

The current provider refusal category is not queried or inferred. No external literature was newly fetched. Related-work substance and bibliographic metadata are inherited from the frozen packages and their disclosed reading histories, rather than certified by this review as newly read full papers. Cost accounting is inherited; reasoning/completion reporting fields were checked directly. No human coding or authorship is claimed.

## Document and finding checks

`prepare_insert.py` writes eleven findings with stable IDs SC-01 through SC-11. Every location includes an exact frozen passage and its one-based source line; `verify_review.py` confirms all passages and line numbers. Findings include corrections to my own offer-form table, finance example and request-artifact evidence map. The strongest proposed account and positive observations appear in `review.md` and `integration_proposal.md`, independently of the findings list.

`replacement_prose.tex` is a finished standalone integrated core insert. It contains an abstract, introduction, methods, financial and bargaining results, interpretation, conclusion, all eight incidents, the complete four-form/stage/completion table, all sixteen full entry fields, the eight questions plus A-C and artifact/replay prose. Its short related-work paragraph and four references provide context for these replacement sections; it is not offered as a complete replacement of the four frozen full manuscripts' literature coverage or reproducibility package.

Build commands from this directory:

```sh
python check_saved_records.py > saved_record_checks.log
python prepare_insert.py
lualatex -interaction=nonstopmode -halt-on-error replacement_prose.tex > build.log
lualatex -interaction=nonstopmode -halt-on-error replacement_prose.tex > build_final.log
/tmp/monopoly-astra-rewrite-venv/bin/python verify_review.py
```

The Python environment for rendering supplies PyMuPDF and Pillow; the analysis itself uses the standard library. The temporary environment path is an available local dependency, not a portable installation instruction. The ordinary LuaLaTeX packages are named in the native source. The PDF skill's create-operation marker ran successfully before document creation.

Final PDF: 13 pages; SHA-256 `6165c4178dbea0b0de90a0e31bce2b0aa313bf17a062c2dd55ed140a53230233`. The final log has no LaTeX warnings, unresolved references/citations, missing glyphs, overfull or underfull diagnostics. All twelve displayed quotation blocks and all sixteen full entry fields occur in extracted PDF text. No page is blank and no text block crosses the checked page margins. I inspected every page in contact sheets and re-inspected affected entry-field pages and the question map after fixing a split heading. Renders are in `qa/`; numerical checks are in `qa/verification.json`.

## Preservation and scope

All 234 frozen draft hashes matched at entry, before any review output was written. They matched again during saved-record verification and after the final build. All 72 baseline-manifest paths match. Final verification also rehashes all 8,765 input paths recorded by the analysis. Per-path frozen comparisons are retained in `frozen_hash_check.json` and `qa/frozen_hashes_after.json`. Git status has the same three pre-existing untracked research directory trees; no tracked source change is reported. I did not overwrite, edit or delete any frozen draft or canonical input.

There were no games, engine executions, replay executions, synthetic tests, baselines, counterfactuals, rollouts, provider/model queries, repository test runs, branches, commits, pushes or messages to finished peers. The repository's general verification script was not run because this assignment explicitly prohibits new evaluations. All computation was saved-record arithmetic, resampling, source/quote validation or document building/rendering. No subagents were used.

The six requested deliverables are complete: `initial_position.md`, `review.md`, `findings.json`, `integration_proposal.md`, `replacement_prose.tex` and this file. The compiled PDF, source includes and check scripts accompany them. No canonical integration was changed. Human-author metadata and publication of local research artifacts remain the owner's subsequent responsibilities. This assignment stops at handoff.
