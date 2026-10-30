# Sol initial LaTeX review position

Written 2026-10-29 before reading new peer findings or shared conversion files. At this first inventory, `latex/` did not yet exist. This is an overlapping full-scope review of the formatting of steps 11–14, not a new manuscript, literature review, or scientific analysis.

I read the repository AGENTS.md, the complete integrated `paper_outline.md`, `figures_and_tables.md`, Astra's nine frozen exhibit captions, and my prior `sol/handoff.md`. The existing Markdown remains the authority for the argument and claim bounds. The existing generated datasets remain the authority for table values. The conversion should not resolve scientific questions or expand claims.

The outline must remain recognizably an outline. Preserve its preferred and alternative titles, abstract plan, three RQs, all eight top-level sections, subsection hierarchy, drafting gates, alternatives, transitions, and future-study boundary. Preserve the comparable economic/social depth, norm-explicit framing, source uncertainty, and scope of exact-prefix checks. References to literature can remain named references or source links; no `.bib` or literature-review rewrite is authorized.

All nine frozen figure captions must retain units, denominators, provenance and limiting statements. Use the existing vector PDFs in figure environments. Include the coauthored exhibit inventory and selection guidance. Do not present alternative grids as independent datasets, cash as wealth, rent receipts as ROI, received channel conflict as intentional deception, or a local payment sequence as future survival.

All nine numeric datasets must appear as native LaTeX tables, including long data tables. Retain the source row counts and keys. Raw numbers or documented display rounding must reconcile to CSV/JSON; units, missing/empty values and Boolean meanings need explicit notes. Long tables need repeated headings, readable columns, and no dropped rows. The dense event-level cash table must remain reconstructable rather than silently aggregated into a new table.

Cross-references should resolve within each standalone document and allow later reuse of figure/table snippets. Labels must not hard-code a final manuscript ordering. Build commands must work with local LuaLaTeX/latexmk without paid services. Output paths for my review, build logs, renderings and proposed replacements will remain under `latex_review/sol/`.

The final bounded check will compare sources, captions and every native-table row, compile available shared documents with outputs confined to this review directory, check logs/references, and inspect rendered pages. A clean compiler run alone does not establish table fidelity or visual quality. I will identify exactly which source revision and rendered pages I checked and state any remaining limits.
