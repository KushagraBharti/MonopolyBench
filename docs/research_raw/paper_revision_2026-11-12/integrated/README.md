# Integrated manuscript, 12 November 2026

Read manuscript.pdf. The title is *Stated Plans and Economic Actions of LLM Agents in Twenty Monopoly Games*.

This completed revision integrates four independent full manuscripts, all-four cross-reviews, and three final whole-paper reviews. Astra wrote and reviewed the whole paper alongside Sol, Opus and Fable 5.2. The final PDF has 21 pages, eight main-text incidents, 21 quotation cards, the complete offer census, all sixteen initial financing fields, both prompts, the seed/game map and the research-question map. It has not been submitted or published.

## Rebuild

From this folder, with Python packages numpy, matplotlib, PyMuPDF and Pillow and a LuaLaTeX/latexmk installation:

    PAPER_PYTHON=/path/to/python bash build.sh
    /path/to/python tools/verify_document.py

The authoring environment uses /tmp/monopoly-astra-rewrite-venv/bin/python and /Library/TeX/texbin. The scripts locate this repository relative to their own path. They require the archived games and historical research artifacts, so this is a repository-contained package.

The build reads stored records, recomputes descriptive tables and resampling summaries, extracts source-linked quotations, and compiles LaTeX. It does not execute the game engine, replay, a baseline, a synthetic scenario, or a model query. Historical engine witnesses and replay results are explicitly distinguished from these checks.

See evidence_map.md, INTEGRATION_DECISIONS.md, adjudication.json and FINAL_REVIEW_DECISIONS.md for provenance and the disposition of all final findings. qa/verification.json records the final PDF hash and mechanical checks; ../final_manuscript_manifest.json pins the completed package. The original 78-file review pin is preserved separately and intentionally describes the earlier reviewed version.

The bibliography and source reading notes are in literature_notes.md. Human authorship and venue formatting remain with the project owner; no human author or human annotation has been invented. This package remains local and uncommitted. The repository URL hosts the historical implementation and games; it does not yet distribute this completed source folder.
