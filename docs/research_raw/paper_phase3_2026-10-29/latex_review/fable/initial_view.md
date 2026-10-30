# Fable: independent full-scope review of the LaTeX conversion (steps 11–14 package)

Written 2026-10-29 before opening any file under `latex_review/sol/` or `latex_review/opus/` and before any `latex/` output existed. Peer messages that had arrived before this file was written: Sol (two formatting notes), Opus (four numbered points) and Astra (accepted-fix list). Where a point below was raised first by a peer it is attributed; everything else is my own inspection.

Scope: conversion of `paper_outline.md`, `figures_and_tables.md`, `astra/exhibit_captions.md`, the nine `astra/exhibits/t0*.csv` datasets, and the indexed peer exhibits into `latex/`. Not in scope: `literature_review.md`, `references.bib`, engine, prompts, canonical games, new analysis. Nothing in this folder changes shared files.

## 0. What I inspected (source side)

| Item | Checked how |
|---|---|
| `paper_outline.md` (3,115 words, 29 headings, 14 markdown links, 17 bold run-ins, 11 `$`, 29 `_`, 1 em dash, 7 en dashes, 1 `τ`) | full read; character census by script |
| `astra/exhibit_captions.md` (1,480 words; 9 captions + 3 encoding/version notes + figure-selection paragraph; 17 `$`, 9 em dashes) | full read |
| `figures_and_tables.md` (557 words; 9-row figure table, 6 retained peer exhibits, draft-selection rules) | full read |
| `astra/exhibits/manifest.json` | script and source hashes read; 9×3 figure exports and 9×2 table exports listed |
| T1–T9 CSVs | every headline number recomputed (section 1) |
| F1–F9 PNGs | viewed; caption claims cross-checked against the rendered panels (section 2) |
| F1–F9 PDFs | mediabox and font type read from the PDF stream (all single-page, TrueType/Type 42 embedded, no Type 3) |
| `astra/build_exhibits.py` | `font.size` 10, per-figure `figsize` and annotation `fontsize` values read for the print-scale table |
| Peer exhibits named in `figures_and_tables.md` | formats, dimensions, provenance files and CSV headers read; SVG→PDF conversion tested with `rsvg-convert` |
| Toolchain | TeX Live 2026 (`latexmk` 4.88, LuaHBTeX 1.24), all needed packages present; `rsvg-convert` present; `gs` present (for rasterising and text extraction); no `pdftoppm`, `pdffonts`, `inkscape`, `pymupdf` |

## 1. Numbers recomputed from the CSVs (any `.tex` cell that disagrees is a defect)

- T5 (`t05_spending_units.csv`): 103 rows; outlay 103,450; paid developed rent after first own spend 92,550; whole game 93,000; sale proceeds 13,500; 40 zero-rent units, of which 26 with no creditor elimination; 58 winner units (34 with an inherited deed) and 45 other units (1 with an inherited deed); zero-rent split 24 winners / 16 others; the only row where whole-game ≠ post-spend is G2 p2 LIGHT_BLUE (850 vs 400, the $450 in the F5 caption). Per configuration: Sol 35, Gemini 34, Opus 21, Grok 13.
- T6 (`t06_eliminations.csv`): 60 rows; 56 declared, 4 automatic (`mortgage_property`); 3 rows with `avoidable = True` (G12 dec-000190 Sol 748 vs 500; G12 dec-000249 Grok 613 vs 250; G17 dec-000234 Gemini 905 vs 550); 56 rows with full upper bound < owed; exactly one row with accessible ≠ full (G7 dec-000339 Opus, 440 vs 1,310 under 750). `menu_mortgage_only` differs from `accessible` in 22 rows. `steps` lists: 296 entries in total, longest 23, eight empty.
- T1 (`t01_cohort.csv`): 20 rows; wins Sol 8, Gemini 7, Opus 3, Grok 2; winner seats 1:7, 2:7, 3:3, 4:3; 3,226 turns in total; two fingerprints (`2f471f70…` games 1–4, `9a15ddc8…` games 5–20); block 2 all Sol, block 3 all seat 2.
- T3 (`t03_trade_groups.csv`): 63 trade groups, 54 eligible during window, 42 entry-eligible, 34 entry-eligible built, 43 first-management built, 0 without access.
- T4: 60/43/10 = 113.
- T7 (`t07_build_recovery.csv`): rejections 29/19/61/5 = 114; recoveries 25/18/0/5 = 48; same multiset 20/6/0/5 = 31; changed 5/12/0/0 = 17; defaults 4/1/61/0 = 66.
- T2 (`t02_negotiation.csv`): proposals 132/18/240/136 = 526; propensities 83/834, 16/766, 160/660, 106/676; intensities 1.590…, 1.125, 1.5, 1.283…
- T8 (`t08_cash_trajectories.csv`): 631 rows (G14 180, G15 197, G19 254); every game starts at seq 9, turn 0, cash 1,400 after `buy_property` and ends at a `BANKRUPTCY` row with cash 0 for the eliminated player; 31 distinct `reason` tokens.
- T9 (`t09_entry_nonbuild_records.csv`): 8 rows; 3 `engine_default` (G2 Opus, G4 Sol, G18 Opus; `selected_content_name` and `selected_attempt_index` empty), 3 `received_content_tool_conflict` (G8, G12, G20 Grok), 2 `consistent_end_with_stated_reserve` (G1, G15 Grok).

Numbers in the outline that are not derivable from these tables and must be carried verbatim: 50,918 events; 6,989 decisions; 8,679 attempts; 80 player-games; 475/72/207/397 deed routes; 209 group episodes; 69 terminal inherited completions; 113 settlements; 44 final terms authored by the non-initiator; 2,054 initial prompts; 614 catalog items; 21 historical entries; 240-decision sample; 54/60 and 35/40 creditor-winner counts; 139/15/5 Grok conflict counts; 30 winner groups first completed via estate; G13 $130/$200/$35; G18 $250; 18-file diff.

## 2. Figure–caption cross-checks (rendered PNGs vs caption text)

| Figure | Checked | Result |
|---|---|---|
| F2 | seats one-based; block 2 Sol sweep; block 3 seat-2 sweep; 1–4 vs 5–20 footer | matches caption and T1 |
| F3 | 83/834, 16/766, 160/660, 106/676; 1.59, 1.12, 1.50, 1.28 | matches T2; 1.12 is Python half-even display of 1.125 |
| F4 | left 17/16, 18/17, 15/7, 13/3; right 14+1, 13, 5+2, 2+3+2 | matches T3; residual 3 defaults (Sol 1, Opus 2) + 3 conflicts + 2 holds matches T9 |
| F5 | 58/34 and 45/1 panel titles; 24/16 zero-rent annotations; linear-below-100/log-above axis; diamonds and dark edges | matches T5 and the encoding note |
| F6 | 56/3/1 legend; G12 Sol, G12 Grok, G17 Gemini, G07 Opus labels; horizontal 440→1,310 segment at 750; circles vs squares | matches T6 and the encoding note |
| F7 | 20/5/4, 6/12/1, 61, 5 | matches T7 |
| F8 | panel texts: d251/d252/d253, $130/$200, $35+$130+$130=$295, d135/d136, d255/d256; channel labels | consistent with caption; wording in the figure is evidence and must not be paraphrased in LaTeX (Opus's point, accepted) |
| F9 | three panels G14 Sol wins, G15 Gemini wins, G19 Gemini wins; cash ($) vs global turn | matches T8 |
| F1 | five boxes, two footer lines | pure text; see section 4.6 |

No caption–figure contradiction found.

## 3. Conversion defects to prevent, with proposed treatment

### 3.1 Units (three different quantities look like money)
- Game currency: all of T5, T6, T8, F5, F6, F8, F9 and every `$` in the outline and captions.
- Real USD: only `opus/exhibits/cost_usage.csv` (`known_cost_usd`, `known_cost_per_decision_usd`), a lower bound for Opus because 1,600 refused attempts lack cost.
- Counts/ratios: T2, T3, T4, T7, T9.
Proposal: two macros (`\gd{103450}` → `\$103,450` game dollars; `\usd{141.71}` → `USD 141.71`) and column headers that say "(game \$)" or "(USD)". Never one macro for both. (Also raised by Sol; agreed.)

### 3.2 Rounding and display
- T2 ratios have 16–17 significant digits in the CSV. Display: propensity and eligible-decision rate to 3 d.p. or 1 d.p. percent; intensity and decisions-per-turn to 2 d.p.; give the exact fraction (83/834 etc.) beside any rounded value, as F3 does.
- Pre-round in the generator with Python formatting (round-half-even on the binary value; 1.125 → 1.12 matches F3) and set `\sisetup{round-mode=none}` so `siunitx` (default `round-half=up`, which prints 1.13) never re-rounds. (Opus and Astra reached the same conclusion.)
- Money: thousands separators, no decimals (all values are integers).

### 3.3 Identifiers and escaping
- 29 underscores in the outline, 39 in the captions, 60 in `figures_and_tables.md`, and every property/group/reason token in T5, T6, T8, T9 (`LIGHT_BLUE`, `PENNSYLVANIA_RAILROAD`, `SCHOOL_FEES_PAY_50`). Escape as `\_` or use `\path{}`/`\detokenize`; a single unescaped underscore aborts the build or silently subscripts.
- `$` (11 + 17 occurrences) must become `\$`; `&` none; `%` none; `τ` once (`τ-bench`) must be `$\tau$-bench` because Latin Modern under `fontspec` lacks the glyph (Opus observed U+FFFD).
- T9 `decision_id` values are 60+ characters with a per-game campaign prefix; T9 `source` paths are 90+ characters. Print `dec-000119` style short IDs and give the campaign prefix and source path once per game in the table notes; keep `line`. Empty `selected_content_name` / `selected_attempt_index` cells (the three engine defaults) must print as "—" with a note "absent: no model-selected content", never as 0 (Sol's point; agreed).
- T1 fingerprints: print the first 8 hex characters; both full 64-hex values in the table note.
- T6 `decision` values (`dec-000315`) are already short; `steps` cannot sit in a column (up to 23 items). Proposal: the main longtable shows the step count, and a separate appendix list prints every sequence in source order (296 entries). Content is preserved, not dropped.
- T6 `avoidable` must be headed "current debt payable by own legal sequence" (yes for 3 rows); it says nothing about survival or an alternative winner (Sol's point; agreed).

### 3.4 Long tables and pagination
- T5 (103 rows × 12 columns): `longtable`, `\footnotesize`, repeated header, continuation marker, ≈2.5 pages. Landscape not needed if the two boolean columns are rendered as single characters.
- T6 (60 rows × 14 printed columns + step count): `longtable`, landscape via `pdflscape`, ≈2 pages; plus the step appendix (≈3 pages).
- T8 (631 rows × 7 columns): single-column would run ≈12 pages. Proposal: a two-record-per-line longtable in source order (left record, then right record), ≈6–7 pages, with the pairing stated in the note. Initial balances are rows in the table already (seq 9, turn 0); do not add separate rows that are not in the CSV.
- T9 (8 rows × 12 columns): landscape or split into a main table (game, model, group, decision, turn, category, applied action, content name, attempt index, outcomes) and a provenance note table (campaign prefix, source path, line).
- Repeated headers must carry units on every page, not only on the first.

### 3.5 Figures: formats, inclusion and print scale
- The nine shared figures have single-page vector PDFs with embedded TrueType fonts; include with `\includegraphics` by path into `astra/exhibits/`, not copies, so the manifest hashes remain the provenance.
- Print scale at a 6.5 in text width, from the PDF mediaboxes and the plotting script's font sizes (smallest annotation first):

| Figure | PDF width (in) | scale at 6.5 in | smallest text (pt, source → printed) |
|---|---|---|---|
| F4 | 11.72 | 0.555 | 7.7 → 4.3 |
| F9 | 12.12 | 0.536 | 8.0 → 4.3 |
| F5 | 10.72 | 0.607 | 8.0 → 4.9 |
| F3 | 10.32 | 0.630 | 8.0 → 5.0 |
| F7 | 9.92 | 0.655 | 8.0 → 5.2 |
| F1 | 9.19 | 0.707 | 7.8 → 5.5 |
| F8 | 9.04 | 0.719 | 7.8 → 5.6 (box body 8.8 → 6.3) |
| F2 | 8.24 | 0.789 | 8.4 → 6.6 |
| F6 | 6.89 | 0.943 | 8.0 → 7.5 |

  Six of nine fall below 6 pt. Treatment in this package: landscape or own-page placement for F4, F9, F5, F3, F7 (9 in on letter → 5.9–7.3 pt). A manuscript stage should regenerate at ≤7 in `figsize`; that is a plotting-script change and is out of scope now.
- Peer exhibits: Sol's s1–s3 are PNG (220 dpi) + SVG, no PDF; my house-stock grid is PNG only (160 dpi, 1760×1600, ≈270 dpi effective at 6.5 in); Opus's outcome grid is SVG only. `rsvg-convert` converts Sol's SVGs but substitutes fonts and shows spacing artifacts ("Com pletion by bank purchase" in s3); the `svg` package needs Inkscape, which is absent. Opus's SVG renders entirely black through `rsvg-convert` because it uses CSS `var()` fills; it cannot be converted with local tools. Proposal: include Sol's and my PNGs with a "raster include; regenerable by <script>" note; index Opus's grid without rendering it, or render a native 5×4 tabular from `outcome_grid.csv` with the note that that CSV is zero-based (`rotation_in_block`, `winner_turn_order` 0–3) and uses "Argon", while the shared convention is one-based and "Gemini".

### 3.6 Markdown links → LaTeX references
Fourteen links in the outline. Proposal: exhibit links become `\cref{fig:f04}`-style references into `figures_and_tables.tex` plus a footnote with the repository path; the two links to `experiment_decisions.md` and `literature_review.md` become `\path{}` text because those documents are not converted. The link text must stay ("F4", "Sol's G19 successive-owner exhibit", "Fable's stock grid") so the outline reads the same.

### 3.7 Hierarchy and text preservation
- Source structure: one H1; unnumbered H2 "Working title and central argument", "Abstract plan", "Appendix and drafting gates"; numbered H2 1–8; H3 2.1–2.4, 3.1–3.4, 4.1–4.4, 5.1–5.4. Use `\section*` for the three unnumbered parts and let LaTeX number 1–8 and the subsections; verify the printed numbers equal the source numbers (a stray `\section` before "1." shifts everything).
- Keep the preface paragraph ("Prepared 2026-10-29 … No venue or page limit is assumed."), the three-item RQ list as `enumerate`, the italic title candidates, and the 17 bold run-ins (`\textbf{Evidence/exhibit:}` etc.) as run-in labels, not as headings.
- Section 6 title contains an em dash; set as `---`.
- No sentence may be dropped, merged or reworded. Any wording correction (Astra proposes "change quantity" → "change allocation" in 4.2) must be footnoted as a correction with its source: the audit field is `allocation_changing_within_decision`, the T7 column is `changed_purchase_multiset`, the F7 caption says "purchase multiset"; the audit rows do not record house counts, so "purchase multiset" is the only term shared by all three sources.
- Citations lines ("**Citations:** AgentMonopoly, DECE, …") can stay plain text; if converted to `\cite`, every key must resolve against the unchanged `references.bib` and the names must still print.

### 3.8 Captions and reuse
- Each caption in `exhibit_captions.md` mixes definition, limits, encoding notes and process provenance ("Sol's earlier G13 d225 typo is corrected to d251"; "developed from Astra's initial position and Sol's explicit challenge"). Proposal: `\caption{definition + limits}` and an `\exhibitnotes{}` block under the figure for encoding/version/provenance text. Nothing is deleted; the manuscript stage can lift captions without the process history.
- Keep the source IDs visible: `\renewcommand{\thefigure}{F\arabic{figure}}`, `\thetable` → `T…`, and a separate counter or prefix for peer exhibits (S1–S3, O1–O3, Fb1–Fb2), so "F4" in the outline is the same label the reader sees.
- Figure placement must follow `figures_and_tables.md`: F7 may be a table; F9, stock grid and alternative grids are supplement candidates; condition/default annotations must not be removed.

### 3.9 Build reproducibility and checks
- `latexmkrc` with `$pdf_mode = 4` (lualatex), `-interaction=nonstopmode -halt-on-error`, out-of-tree `build/` directory, `SOURCE_DATE_EPOCH` exported and `\pdfvariable suppressoptionalinfo` set so repeated builds give byte-identical PDFs where possible.
- Verification to run on each compiled PDF: page count; `gs -sDEVICE=txtwrite` text extraction, then grep for every number in section 1 and every heading; zero undefined references; overfull `\hbox` count (long paths and wide tables are the likely sources); every F-caption sentence present verbatim.

## 4. Resolved with peers before the shared build (attribution)
- Opus: F1/F8 stay as the manifest PDFs; legibility by placement, not re-typesetting. I withdrew the native-F8 proposal; a native F1 is kept in my folder only as an optional transcription verified against the PDF text layer.
- Opus: denominator labelling of my all-63 cause split vs the 42-group T9 residual; the three later-buildable non-built groups (G13 Opus LIGHT_BLUE, G13 Grok YELLOW, G14 Gemini YELLOW) explain every difference.
- Opus: `cost_usage.csv` in USD; Arena percentages in `normative_contracts.csv` must stay attributed to Arena App. D.
- Sol: T6 "payable current debt" wording; T9 absent cells; game dollars vs USD.
- Astra: landscape wide figures; native longtables with repeated headers; T8 all 631 rows in source order; half-even display for T2.

## 5. What this folder contains (updated after the audit)
- `initial_view.md` (this file; sections 0–4 unchanged since first written).
- `audit_of_shared_latex.md`: audit of the shared package snapshot taken at 14:31, with defects in priority order and the checks performed.
- `snapshot_143125/`: rsync copy of `latex/` (without `data/` and `assets/`) with extracted page text (`*.txt`) and page renders (`hi/`).
- `proposed/gen_fable_snippets.py`: read-only generator (run with `python3 -I`) that writes `proposed/snippets/`: `macros_fable.tex` (no-Launch link macro, currency macros, `\tok`), `t02_negotiation_with_conditions.tex`, `t06_liquidation_routes.tex`, `t09_provenance.tex`, `fable_first_management_causes.tex`, `fable_house_stock_summary.tex`, `fable_house_stock_grid_figure.tex`.
- `proposed/test_fable_snippets.tex`, `proposed/latexmkrc`, `proposed/build/` (PDF, log, page PNGs) and `proposed/linktest/` (the one-line `run:` Launch-action test).
- The earlier plan in this section (a full parallel set of t01–t09 snippets and a native F8) was dropped after Opus's objection that re-typesetting frozen exhibits adds drift risk; only replacements for identified defects were produced.
