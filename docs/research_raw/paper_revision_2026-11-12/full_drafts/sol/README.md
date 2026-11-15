# Sol's complete scientific revision

Open [manuscript.pdf](manuscript.pdf). The native source is [manuscript.tex](manuscript.tex). The paper includes the complete main argument, bibliography, eight incidents, both full prompts, all sixteen necessary-collateral entry fields, full offer-form/completion tables and the twenty-game map.

The thesis connects stated economic opportunities with executed choices, giving local financing evidence greater weight than the unexplained bargaining contrast. See [initial_position.md](initial_position.md), [evidence_map.md](evidence_map.md), [findings_and_limits.md](findings_and_limits.md), [literature_reading.md](literature_reading.md), and [handoff.md](handoff.md).

## Reproduce the analysis and PDF

Requirements: Python with NumPy, Matplotlib, PyMuPDF and Pillow; LuaLaTeX, BibTeX and latexmk. The original repository and saved games must remain at their recorded relative paths for source verification. The scripts find the repository root from their own paths. No engine/model imports or new evaluations occur.

From this directory:

```sh
PAPER_PYTHON=python3 bash build.sh
```

To run just the saved-record arithmetic:

```sh
python3 tools/analyze.py > qa/analysis_output.txt
```

To check an already built PDF and source preservation:

```sh
python3 tools/verify.py
```

The local build used `/tmp/monopoly-astra-rewrite-venv/bin/python` and `/Library/TeX/texbin/latexmk`. These are local executable locations, not required absolute paths. `build.sh` accepts `PAPER_PYTHON` and adds the standard MacTeX path if needed. The main-prose count is a documented command-stripped estimate in `qa/document_checks.json`.

## Analysis records

- `data/offer_analysis.json` contains all form/completion/stage cells, proposer/recipient strata, exact five-block resampling and exclusions. All 3,125 ordered block draws are enumerated, without random Monte Carlo variability.
- `data/finance_analysis.json` contains the sixteen entry rows and selected texts, all nineteen observed collateral uses and the thirty-three mortgage actions.
- `data/game_map.json` and `data/stored_replay_reports.json` identify seeds, rotations, seats, runs and both historical comparison modes.
- `data/eliminations_inherited.json` retains all sixty historical elimination classifications; executable witnesses are not rerun.
- Four quote manifests preserve original paths, hashes, JSON pointers and spans. `qa/public_delivery_checks.json` records checked receipt for displayed public messages.
- `qa/protected_hash_checks.json` gives every matched protected input, including every hash in the November 12 baseline manifest. `final_file_hashes.json` freezes the review package after inspection.
- `qa/render/` contains every rendered page and contact sheets. `qa/visual_inspection.md` records the final inspection.

Neither a successful build nor source-exact quotation checks establish scientific validity. The paper distinguishes fresh arithmetic and reading from inherited semantic codes, historical feasibility witnesses and replay executions. The bands summarize sensitivity of selected observed blocks, not validation of a selected hypothesis. No hypothetical baseline score appears.

This is an independent complete draft, frozen for a separately requested all-four cross-review. It is not a submission, publication or final integration.
