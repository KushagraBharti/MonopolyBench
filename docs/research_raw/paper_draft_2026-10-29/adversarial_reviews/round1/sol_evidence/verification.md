# Verification scope

Read the frozen section sources and extracted the 34-page PDF to pdf_text.txt. Tool output for long reads was truncated; section source reads supplemented the PDF extraction. No visual layout certification was performed. Initial position was saved before opening retained phase-2 audit outputs. No previous reviewer report or coordinator charter was opened. Applied the PDF and unslop skills.

Executed analyze.py from repository root with Python. Independently counted raw canonical events across the 20 manifest-listed runs: 50,918 events, 6,989 decision requests and 113 accepted trades. Output includes per-game counts and SHA-256 hashes for every events.jsonl. This is a raw recount, not a rerun of the manuscript verifier.

Independently compared received and repaired construction purchase multisets in 61 retained Opus diagnostic records: all 61 agree after expanding counts. Legal flags, engine-produced events, complete replay, memory equality and affordability remain retained results, not fresh engine executions in this review. No new games, paid calls, canonical edits, prompt edits, commits or pushes occurred.

Did not independently recompute 43/63, 34/42, spending/rent totals, all liquidation bounds, channel missingness or review coverage. Those claims were assessed for definitions and inferential scope. No claim of complete scientific validation follows from the raw recount.

Sources: frozen sections/*.tex, manuscript.pdf and evidence_map.md; phase1/sol/manifest.json and its 20 saved-game event paths; phase2/core_review/sol/build_recovery_audit.json, elimination_upper_bounds.json and corpus_economics_audit.json. Analysis_results.json records exact raw source hashes. Literature sources and verification limits are recorded in sources.md.

Reproduce the performed analysis with `python docs/research_raw/paper_adversarial_2026-10-29/round1/sol_evidence/analyze.py` from repository root. PDF extraction used local .venv with pypdf 6.21.4. The first extraction attempts failed because system pypdf and pdftotext were unavailable; the local extraction then succeeded.
