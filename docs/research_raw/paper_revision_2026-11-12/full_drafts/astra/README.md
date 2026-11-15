# Independent Astra manuscript, 12 November 2026

Read `manuscript.pdf`. This is a complete independent version prepared before opening the Sol, Opus or Fable 5.2 versions from this round. It is frozen for all-four cross-review, not a final integrated release.

The active document is `manuscript.tex`, which includes six new main-text section files and `sections/supplement.tex`. The four quotation macro files and their manifests preserve quotations verified in earlier rounds. The analysis reads existing records only.

## Build

From this directory, with Python packages numpy, matplotlib, PyMuPDF and Pillow, and LuaLaTeX/latexmk installed:

```sh
PAPER_PYTHON=/path/to/python bash build.sh
/path/to/python tools/verify_document.py
```

The authoring environment used `/tmp/monopoly-astra-rewrite-venv/bin/python` and `/Library/TeX/texbin`. Override `PAPER_PYTHON` for another installation. The scripts locate the repository relative to this package. They require its saved games and retained research artifacts. This is a repository-contained analysis package, not an independently portable export.

`build.sh` reads saved decisions and retained ledgers, checks the offer classifications and financing arithmetic, generates tables and figures, and compiles the paper. It performs no engine execution, replay, model query or evaluation. `tools/verify_document.py` validates selected quotations against original fields, checks protected hashes, inspects the PDF's text and bounding boxes, and renders every page.

Outputs include `data/revision_analysis.json`, `data/necessary_collateral.json`, generated table fragments, two figure PDFs, and `qa/verification.json`. The copied ledgers retain their historical provenance; their presence does not imply that every earlier analysis was independently rerun.

See `evidence_map.md` for direct versus inherited checks, `findings_and_limits.md` for scientific judgments, `literature_notes.md` for reading scope, and `handoff.md` for unresolved editorial decisions.
