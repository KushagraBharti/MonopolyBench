# Verification and limits

## Reading and independence

I read repository `AGENTS.md`, the rewrite and cross-review contracts, and the complete main/appendix TeX texts of Astra, Sol, Opus and Fable 5.2, including all included generated tables, transcript definitions and handoffs. I read the research-question transcription and consulted the original critique. `initial_position.md` was written before opening Astra's cross-review. I then read `reviews/astra/all_four_review.md`, `comparison_in_progress.md`, counteroffer checks and checker, new-quote checks, Fable-addition checks, literature follow-up and render review. I did not contact completed peers or spawn agents.

The four PDFs have 23, 25, 43 and 39 pages respectively. Their complete text is extracted under `render/`; every page was visually inspected in contact sheets. The source TeX, rather than thumbnail readability, supplied the substantive reading of all prose, appendices, tables and transcripts. `source_manifest.json` records the frozen manuscript/PDF and supporting document hashes at review entry.

## Performed record checks

`check_existing_records.py` reads retained data and original source files only. It imports no engine, runs no game, creates no synthetic state and calls no model. Its generated `performed_checks.json` records input hashes and results.

- Re-tabulated the 918 acceptance-legal offer cells, configuration exceptions and opening/later-response differences.
- Joined all 394 counters to their next offer with exchange-index continuity, actor reversal, exact completed-group identity, noncash bundle equality and cash accounting. Reproduced 111 author-only counters, 92 retaining the original group, 88 with only that party completing, 85 cash increases and 79 unchanged noncash bundles with cash increases. Interest-adjusted cash deltas agree in the 88 subset. Cash increases in other categories remain visible.
- Reproduced 373/429 completing-side cash direction, 107 cash settlements, 48 payer-completing sales, 21 sellers below $100 in those 48, the $194/$571 medians and the $50/$100/$150/$200 threshold cuts.
- Joined the inherited 139 conflict IDs to actual thread/response ledgers, reproducing 64 conflicting Grok openings, seventeen settlements from those threads, eleven conflicting trade responses and seven acceptances, three completing Opus groups. This is a join, not a fresh raw-response conflict classifier.
- Re-tabulated all 209 completion episodes, 52 nonterminal inherited completions, the four per-owner trade-episode rent totals, the full first-window outcome population and Opus's five no-option/three-default residual split.
- Reloaded every retained quote field represented by thirty spans, ten Opus supplementary spans and fourteen Fable supplementary quote records. All 54 checked spans/records match original field values, offsets and file/field hashes. Some refer to overlapping source fields; 54 is not a count of distinct incidents. Checked fourteen new public-message records as complete strings in the next actual opponent request. Source reading confirms the corresponding counterparties in these focal threads. These checks establish excerpt fidelity and exposure, not attention, belief or persuasion.
- Read the original G2 event 1566, with a $44 Atlantic payment to Sol at turn 77. Compared it with the $44 completion-episode total and the separate spending unit's $0 developed rent, $300 construction spending and $150 salvage. This newly identifies the overbroad zero-rent statement in Opus's proposed G2 narrative.
- Read original G2 d129's attempt outcomes, `illogical` then `refused`, confirming the exception to first-refusal recovery.
- Inspected original G15 d169 public state and the offered cash consequences. The source has 19 bank houses and clear holdings, and the ledger gives $830/$233. Read `_buildable_space_indices` and `_validate_build_plan` in the engine source, without importing or executing them. The $600 figure buys three green houses, while one costs $200. This is arithmetic and rule-source inspection, not a new historical witness, maximum-finance search or strategic-value calculation.

The static G15 rule reading must not be reported as an executed acceptance/build continuation. Likewise I did not newly recompute all cash/estate/conflict classifications from raw events. Their retained-ledger foundations remain inherited.

## Inherited scientific results

Twenty-game replay; the 6,989 prompt and 10,235 snapshot reconciliations; full memory and delivery reconstruction; 113 transfer checks; 56 bound negatives, three payment witnesses and the G7 restricted lock; 61 Opus reordered construction targets; recovery/recurrence ledgers; raw-response localization and parsed-versus-literal argument counts; reason coding and temporal coding all originate in earlier work. I inspected and re-tabulated selected retained outputs, but did not rerun engine certificates, replay, reference policies, fixtures, model calls, annotation studies or transfer tests.

The bound and witness results are evidence about the preserved implementation. The bundled-sale limitation remains. No document check establishes intended-rule correctness or general semantic accuracy.

## Primary literature checks in this pass

These were targeted section readings, not full-paper reviews or comparator executions. Exact versions and direct primary links follow.

- [AgentMonopoly v2](https://arxiv.org/html/2610.29330v2), §4 and Appendix A.2. Checked its action/language interface and the explicit permission to bluff with a restriction against messages contradicting actions. Earlier implementation-level inheritance/trade comparisons remain inherited; I did not inspect its repository here.
- [Arena communication study v3](https://arxiv.org/html/2608.14825v3), §§4.2–4.3, §5.2.2 and Appendix F. Checked full-pipeline replacement-judge replication and the observational, judge-sensitive inventory association. This supports specific credit for its design, not transferring its taxonomy or rate to this cohort.
- [Counterparty Modeling v1](https://arxiv.org/html/2605.16575v1), §3.3 and adjoining metric passages. The informed condition supplies a coarse ranked preference summary, not full utility weights. Keep that information condition in any summary of expressed partner modeling.
- [Empty Commitments v2](https://arxiv.org/html/2610.01045v2), §§3.4 and 5.6, with the adjacent component description. The paper reports human-label comparisons of specified components. My earlier phrase "validated ontology" was broader than the checked claim; it should be removed or scoped.

I did not newly read the complete FinBoardBench, DECE, MERIT, CEO-Bench or the broader literature inventory. Their claims must retain earlier verification scopes. The replacement's narrow FinBoardBench/DECE/NegotiationArena summaries rely on retained source reviews, not a fresh full-text comparison in this pass.

## Document build and render

The frozen four manuscripts were not edited or rebuilt. Contact sheets for all 130 pages are in `render/`. They show no obvious page clipping at that scale, but do not establish full-resolution quality of every mark. Astra/Sol are more compact; Opus/Fable reserve much more main and appendix space for condition and population tables. The early-results delay and dense Fable estate table warrant editorial compression rather than deletion of conditions.

I compiled the proposed replacement passages in isolation through `replacement_preview.tex`, using unchanged quote definitions from the source package and a local byte-copy of Sol's bibliography. The preview is an 11-page proposed-prose artifact, not a complete integrated 8,300-word manuscript or a replacement for its evidence appendix. Build outputs are confined to `reviews/sol/build/`.

The final LuaLaTeX/latexmk build succeeds. `render_checks.json` records zero overfull/underfull, undefined-citation/reference, missing-character or warning diagnostics in the final log; zero detected out-of-page text spans; and all sixteen used quote macros present in normalized extracted PDF text. I inspected all eleven pages in a contact sheet and pages 3, 6 and 8 at larger size. Native transcript cards are readable in those inspected pages. No figures are newly drawn in this prose preview. An integrated full-paper build and final all-exhibit verification remain parent work.

## Reviewer mistakes and corrections

1. My initial note suspected the Sol artifact relative path. Direct resolution confirms the ZIP exists; I cleared the suspicion and did not manufacture a finding.
2. My first field loader assumed every manifest field had a JSONL line. Some provider sources are complete JSON files with a null line locator. I corrected the loader and reran all checks successfully; no source values changed.
3. I briefly attributed the phrase "built on without return" to Astra's summary in commentary. Exact passage checking locates it in Opus's G2 interpretation. The final review states that Astra did not flag the zero-rent wording, rather than attributing that wording to Astra.
4. The preview initially lacked Fable's inline-quote declaration and used a bibliography path resolved differently by BibTeX's build directory. I added a local wrapper macro and a local bibliography copy. The final build has no such unresolved diagnostics.
5. This review corrects my frozen draft's causal G13 wording, induced-counter wording, unscoped ontology validation and categorical intention inference. My original draft remains unchanged as required.

## Preservation and scope

All 272 frozen sources in `baseline_source_hashes.json` match their expected hashes. The review-entry hashes of the four full-draft documents/PDFs are checked again at completion. No original outline, literature review, independent full draft, canonical saved game, engine, prompt or prior paper was edited. No commit or push was made. All authored files, copied bibliography and compilation/render output for this pass are inside `reviews/sol/`.

The deliverables are the six requested review files plus source-check scripts/results, preservation hashes and isolated preview/render evidence. The final scientific claims still have the observational and semantic limits stated in the review. A successful build and preserved inputs do not promise a perfect paper or acceptance.
