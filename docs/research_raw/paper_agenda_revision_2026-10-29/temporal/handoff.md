# Temporal extension complete

Integrate `temporal_results.tex`. It contains finished methods and results for Q2, Q4, Q5 and the strategy-text/execution question A. `exhibits.tex` provides three native LaTeX longitudinal panels. They compile together in `build/review_wrapper.pdf`, four pages, with zero overflow, missing-glyph or unresolved-reference reports. All four pages were rendered and visually inspected.

## New results

- All 240 fixed public-unflagged sample records were read afresh in full for public_message and applied private_thought. There are 59 forward-looking own-action passages, 36 opponent prospective-capacity/outcome passages, and 25 explicit correction or feedback references. These overlap and are candidate categories, not truth, skill or learning scores.
- Fifty-three private fields are absent, all Opus. None of these240 records is an engine fallback and no literal synthetic fallback note occurs. Four sampled named-content/action conflicts are linked to the retained independent audit. Primary coding never substitutes provider summaries for missing notes.
- All59 forward-looking candidates have dispositions: eight explicit landing-purchase policy rows searched through the entire remaining game; nineteen illustrative chronologies; thirty-two unscorable as single commitments with reasons and actual subsequent context retained.
- Of the eight landing-policy rows, six have no later named-target purchase menu, one leads to the stated purchase, and one does not. The latter is G16 d103→159: the legal affordable Virginia purchase is still advocated by the applied private note, while the received action starts an auction. Gemini wins for380 after d164. This is not identified strategic abandonment. Repeated G6 policy rows are not independent episodes. No adherence percentage is reported.
- G9 Sol's stated three-house dark-blue target at d64/turn29 is reached at d163/turn60. Multiple financing and trade steps intervene. It is evidence of realized target attainment, not a causal memory or optimality result.
- G20's Vermont-mortgage endpoint is achieved after an intervening unsuccessful sale offer; immediate action consistency and same-turn endpoint consistency differ.
- G20 and G17 auction records show explicit limit revision, but the G17 d228→23299-ceiling case respects the rule because the rival jumps to100 and the next minimum is101. The original next menu prevents a false inconsistency label.

## What this answers

**Q2, opponent modeling.** The record contains falsifiable forecasts of public capacities and possible outcomes. Some match later events. This is not a calibrated private-belief or theory-of-mind measure. Feasibility and actual choice remain distinct; an unpresented offer cannot validate a prediction of refusal.

**Q4, planning and memory.** Concrete targets can persist through a long realized sequence, and conditional plans may never receive an opportunity. Others are revised or fail amid channel conflict. This answers what was expressed and executed, while leaving causal memory benefit and horizon-general planning capacity unmeasured.

**Q5, adaptation.** Explicit revisions are visible, including within auctions without an asset purchase between statements. Revised explanations can still contain financial errors. This complements the parent's full-corpus feedback recurrence audit; it does not duplicate its counts or call repair learning.

**A, strategic language versus execution.** Realized success, stated revision, absent opportunity and action/note conflict are distinct observed relations. We can distinguish these relations at original decisions. We cannot infer global strategic rationality from convincing language or one realized target.

## Main artifacts

- `protocol.md`, `sample_manifest.json`: fixed all240 scope and the pre-coding sampling correction. The earlier200/40 labels are review outcomes, not sample strata.
- `codebook.md`: operational definitions, channel rules, exploratory and single-coder limits, and corrections.
- `manual_coding.py`: all240 manual row judgments. No classifier generates labels.
- `row_ledger.jsonl`: complete source-linked inventory, exact scoped fields/hashes, coding, endpoint dispositions and retained context.
- `landing_policy_endpoints.json`: exhaustive eight-row subset with actual menus and G16 auction events.
- `longitudinal_witnesses.json`, `forecast_endpoints.json`: original-record witnesses for nineteen own-plan chronologies and four opponent-forecast event checks.
- `results.json`, `channel_inventory.csv`: descriptive counts and unequal channel coverage.
- `source_hashes.json`, `validation.json`, `package_checks.json`, `excerpt_manifest.json`: source/script hashes,26 original-record assertions, displayed excerpt offsets, and build checks.

## Reproduction

From the repository root, run:

```sh
python3 docs/research_raw/paper_agenda_revision_2026-10-29/temporal/extract_sample.py
python3 docs/research_raw/paper_agenda_revision_2026-10-29/temporal/inspect_followups.py
python3 docs/research_raw/paper_agenda_revision_2026-10-29/temporal/audit_temporal.py
python3 docs/research_raw/paper_agenda_revision_2026-10-29/temporal/verify_package.py
python/.venv/bin/ruff check docs/research_raw/paper_agenda_revision_2026-10-29/temporal/*.py
```

The final verifier expects the local standalone LaTeX build. To rebuild it, run LuaLaTeX twice on `review_wrapper.tex` from this directory with `-output-directory=build`. All writes remain in this temporal directory.

## Limits requiring preservation

One fresh model-assisted semantic reader; no blind inter-rater agreement. Previous project reviews mean the extension is exploratory. The nineteen chronologies are selected illustrations, not a new denominator. The complete sample is public-unflagged, not all decisions. Source field counts cannot rank configurations with unequal channel availability. No engine branches or new provider calls were performed here. The cited named-conflict audit was cross-linked, not independently reparsed. Longitudinal text consistency is not an effect of memory, feedback or reasoning quality. No original manuscript, engine, prompt, game or literature file was changed.

The parent's fresh reviewer confirmed all240 fields,107 retained witness decisions and all eight landing searches. One medium wording correction was accepted: d241 applies one house and d242 ends despite building remaining available. The prose no longer calls one house the amount the changed state supports. This is a reported independent review, not a second semantic-coder agreement estimate.

Final review additions extend the G17 rival forecast through its actual elimination and distinguish G3's doubles continuation from a later endpoint after opponent decisions. I independently checked the original action/menu suffix and dice events, added four assertions, and preserved these corrections in the codebook. The complete G17 suffix has no delivered build menu; this is not a claim that all alternative financing sequences were impossible.
