# Handoff: Opus complete draft, 11 November 2026 revision

Status: complete independent draft. Stopping here pending a fresh cross-review assignment. I did not open `full_drafts/astra`, `full_drafts/sol` or `full_drafts/fable_5_2`.

## The paper

`manuscript.pdf` (32 pages: main text pp. 1–21, references p. 22–23, appendices pp. 24–32), built from `manuscript.tex` and `sections/*.tex`. Title: *Guarding the Last Deed: Defensive Bargaining by LLM Agents in Twenty Games of Monopoly*. Main prose is about 7,500 words excluding transcript quotations, tables and references, at the top of the requested range.

**Central claim.** The agents bargain defensively over the deed that would complete a rival's colour group, an identity-dependent externality. The strongest evidence is behavioural, not stated: opening offers that would complete only the proposer's group are rejected 74% vs 64% for neutral openings, positive in all five seed blocks, every leave-one-block-out cut and each standard-condition recipient; cash concessions on completing bundles are accepted 9/58 vs 24/86. Stated reasons (inherited LLM-assisted codes) name the rival in 61/74 refusals of own completion. Limits are central to the claim: asks rise for completing buyers only in pooled data (three of five blocks; same-deed pairs mixed), bids show no matching premium, and responses do not vary with the rival's post-trade building cash. The paper reads this as categorical attention without graded calibration, and says nothing about effectiveness.

**Supporting results.** Completing deeds sell mostly under seller distress (14/22 vs 7/31; 6/11 vs 4/22 without Opus sellers). Trade-completed groups collect $374 per developed landing vs $20 undeveloped; 8 of 9 never-built groups had a mortgaged deed. 188 debt episodes, 128 paid; 3 of 131 demonstrably payable debts ended in elimination. The first creditor is already the asset leader in 15/20 games and wins 18/20.

**Eight incidents**, placed where they show mechanisms: G2 (one deed, two buyers, two prices; four new checked quotes), G15, G20, G12, G13, G18, G7, G19.

**Opus** is reported separately throughout: its condition (verbatim refusal string, within-game timing shift, exact prompt difference, documented `reasoning_extraction` explanation as plausible but unconfirmed) is in the setup; its bargaining is the exception to the defensive pattern; its condition is described as part of the other agents' environment.

## Files

- `initial_position.md`: position recorded before drafting.
- `evidence_map.md`: every claim with status (fresh / rebuilt-and-matched / inherited) and output file.
- `literature_inspiration.md`: what was read, exact support used, inherited verification, what was not cited.
- `findings_and_limits.md`: ranked findings, objections to the contract and earlier interpretations (including a correction of my own earlier assessment), unresolved limits.
- `BUILD.md`, `build.sh`: regeneration and build instructions.
- `tools/`: all analysis, figure, table, quote and verification scripts (read saved records only).
- `data/`: analysis outputs, `source_hashes.json`, inherited quote manifests (`data/inherited/`, unchanged copies), `new_quote_manifest.json`.
- `qa/`: `quote_checks.json` (31 cards all exact, labelled, decoded and rendered), `document_checks.json` (no LaTeX diagnostics, no text outside pages, no blank pages, output file hashes), `build_stdout.txt`, `render/` page images.
- `preamble_inherited.tex`, `references_inherited.bib`, `supplemental_inherited.bib`: unchanged copies of earlier files for provenance; `preamble.tex` and `references.bib` are the derivatives actually used.

## Scope compliance

No games, engine runs, replays, synthetic tests, model evaluation calls or baselines. No edits outside `full_drafts/opus/`; 78 protected baseline files verified unchanged; no commits or pushes. No subagents. Web access was used only to read literature and one documentation page.

## Points I expect cross-review to contest

1. Whether the central claim should be the response/concession contrast (my choice) or a pricing claim. I argue pricing is too unstable to lead.
2. The definition for same-seller, same-deed comparisons (my 5/1/1 first-ask count vs Fable's earlier 4/2/1).
3. Whether to keep Grok's G2 d120 card (it makes seven of eight incidents involve Grok).
4. Whether "categorical, not graded" overreads one flat capacity cut; the text marks it as one cut with confounded cells.
5. Byline: the draft says the author list is to be set by the project owner. No human name was invented.
