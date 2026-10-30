# Final integrated rendering and regression check

The final PDF has 35 pages, four figures, thirteen tables and eighteen bibliography entries. PDF SHA-256: `976c9644d7829f59655ea211d4473d92a49173f4308707d159c8ff7168f8c2dd`.

Root inspected all pages as 110-dpi contact sheets, then full-size details for the corrected references, G13 wording, financing figure, release/census distinction, executable commands, spending figure and final appendix page. The last edit shortened repetitive appendix prose: pixel comparison shows pages 1–34 unchanged from the inspected 36-page render, and the new page 35 was inspected at 140 dpi. The previous short page 36 is gone. Original renders and details remain in the repository's `qa/final_render/`; bulky images are not shipped in the source ZIP.

Confirmed in the final rendering:

- Financing points are nominal upper bounds, with the separate filled G7 accessible endpoint and an explicit caption; no annotation covers the payable points.
- Spending-panel zero-receipt counts are outside the data area. All markers and the legend remain readable.
- Section and appendix references render as numbers/letters, not literal `refsec`/`refapp` strings.
- The two reproduction commands retain executable spaces in both visible text and PDF extraction.
- No sideways pages, clipped captions, empty pages or Launch links. No overfull boxes, missing glyphs or unresolved references/citations in the final log. Programmatic page-bound checks pass.
- All 80 opportunity cells, 663 END records and 126 case summary records agree with the displayed native tables and retained rows under their declared units. The portable verifier compares nested artifact results as well. These are package consistency checks; original-source verification is separately attributed to the reviewers.
- One intact copied package passes, while five isolated corruptions (three new data fields, one native table row and one reference command) fail. `verifier_regression.json` records the tested verifier hash.
- Focused Ruff checks pass for the new aggregation, verification, regression and packaging tools.

The frozen first-draft baseline's 73 files and original ZIP, and the round-3 baseline's 59 files, remain hash-identical. The six protected sources pass. Git reports no tracked-file changes. All work is in research-output directories; no canonical engine, prompt or saved game was edited.

The nested behavioral artifact has SHA-256 `bd0de225dc6e0ecb215326504d11afa51bb5ed8164da87b63c9fcc3072cc74f6`. Its clean-environment report and independent review reruns reproduce all 50,918 events, 126 case outputs and nine tests. This is distinct from manuscript rendering. Exact final manuscript archive extraction/build results are recorded outside the archive in `final_package_verification.json` to avoid a self-referential archive hash.

This report covers the integrated files after the reviewers' frozen snapshots. It does not upgrade their checks to blind annotation, external scientific replication, causal persuasion evidence, or a perfect-paper rating.
