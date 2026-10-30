# Opus review of the shared LaTeX conversion (steps 11–14)

Opus (claude-opus-5-5), 2026-10-29. This is a full-scope, bounded review. It covers the outline hierarchy and text, all nine captions, the nine native tables, the peer exhibits, the build, PDF pagination and readability, and reuse in a later manuscript. Everything I wrote is in `latex_review/opus/`. I did not edit shared `latex/` files, original artifacts, `literature_review.md` or any `.bib` file. I made no paid calls, ran no games and made no commits.

My position from before I read any peer's files is in [initial_position.md](initial_position.md). Statuses in the findings table are as of **snapshot3**, a copy of shared `latex/` at the 14:31 generator, compiled in my own folder, and were later updated to the 14:34 source. **The closing verdict is in [Final pass](#final-pass-pinned-shared-build-144827) below**, run on Astra's shared 14:48:27 build and pinned by sha256 in [final_1448/](final_1448/).

## How each claim was checked

| Check | Inspected source | Rendered PDF | Tool |
|---|---|---|---|
| Sentence preservation: outline (236 sentences), captions (116), `figures_and_tables.md` (45), my two exhibit md files (45) | Markdown | Yes, against PDF text | [pdf_text_audit.py](pdf_text_audit.py). Lowercase alphanumeric substring match; every miss inspected by hand. |
| Table cell fidelity: all rows of T1–T9 against the original CSVs | Generated `.tex` snippets | — | [table_fidelity.py](table_fidelity.py). Mutation-tested: it catches a planted single-cell change (`owed` 500→550). |
| Data-copy identity: `latex/data` against `astra/exhibits` | 18 files, byte compare | — | `cmp` |
| Log health: missing glyphs, undefined references, overfull boxes, float-too-large | `.log` | — | regex in pdf_text_audit.py |
| Identifier corruption: hyphens inserted into underscore codes | — | Yes, PDF text | pymupdf line scan |
| Page images | — | Yes: every page as contact sheets; problem pages at full resolution | [render_pages.py](render_pages.py) with pymupdf |
| Effective figure text size | Figure PDFs, span sizes | Placement scale | pymupdf |
| Probes: siunitx rounding, τ glyph, SVG→PDF conversion | — | Yes | [probe/](probe/), [converted/](converted/) |

Snapshots: [snapshot1](snapshot1/) holds Astra's 14:26 source; [snapshot2](snapshot2/) holds the same source plus my patch; [snapshot3](snapshot3/) holds Astra's 14:31 source. Each has `snapshot_sha256.txt` and `snapshot_time.txt`. snapshot2 is not a separate copy; its sha file is snapshot1's, and it differs only by my patch.

## Findings

Severity: **A** = wrong or illegible content in the PDF, or lost substantive content; **B** = provenance, consistency or reuse defect; **C** = cosmetic.

| ID | Sev. | Finding and evidence | Proposed fix | Status at snapshot3 |
|---|---|---|---|---|
| D1 | A | T5 runs 33.9 pt past the landscape page (5 overfull boxes in the log). On pp18–21, "First spend event" overprints the sideways running header and its values are illegible. Sol confirmed. | Right-aligned p-columns for the four long headers. Tested in snapshot2: 0 overfull, 103/103 rows match. | **Fixed** by Astra's `\shortstack` headers |
| D2 | A | T8 inserts hyphens into canonical event codes, 33 times: `ELECTED_CHAIR-MAN_PAY_EACH_PLAYER_50` ×16, `BIRTHDAY_COL-LECT_10_FROM_EACH_PLAYER` ×12, `CONSULTANCY_FEE_COL-LECT_25` ×3, `INCOME_TAX_REFUND_COL-LECT_20` ×1, `BUILDING_LOAN_MATURES_RE-CEIVE_150` ×1. The hyphen survives copy-paste. | Reason column `>{\ttfamily}l`, or route it through Astra's new `code_columns`/`\path`. Tested: 0 broken. | Open at snapshot3 (33 remain). **Fixed in 14:34 source**: `code_columns=(6,)` renders reasons through `\path`. |
| D3 | B | Every outline and index link is `\href{run:../…}`: a PDF Launch action that viewers block and that resolves relative to wherever the PDF is opened (Fable's finding). They also render cyan, because hyperref's default `filecolor` is not overridden. In `figures_and_tables.pdf` the index links F1–F9 and T1–T9 to external PNG/CSV files, although the same PDF contains them. | Inside the same PDF, use `\ref{fig:…}`/`\ref{tab:…}`. Across files, print the text with a footnoted repository path. At minimum add `filecolor=blue!45!black`. | Colour **fixed** in the 14:34 preamble; Launch actions remain open |
| D4 | C | Missing spaces in rendered notes: T5 "outlay103450 … receipts93000 … receipts92550", T7 "All61", T8 "Initial1500", T9 "attempt0". | Patch inserts spaces and comma grouping. | **Fixed in 14:34** `prepare_sources.py` (lint: 0 hits). The same pattern recurs in `prepare_supplement.py`; see C11. |
| D5 | C | T2 headers overflow by 3.8 pt twice (new with `\shortstack`). | Wrap at width ≈10 or use p-columns. | Open |
| C1 | A | T2 drops `response_condition`. The F3 caption says "The table retains all four configured response conditions"; the note names only Opus and Grok and loses "retry budget affected". | Note listing all four verbatim (in the patch). Sol: name the header "Proposals / eligible decisions (%)" and state that it is F3's eligible-decision frequency. | **Fixed in 14:34**: all four conditions are listed in the note |
| C2 | A | The T6 note gives the full bound as "building-sale proceeds plus **unlocked** mortgage values and cash". My `bankruptcy_bounds.py` counts every unmortgaged deed, assuming all buildings are sold first. Sol agrees. | "Full bound = cash plus half the house cost for every building level plus the mortgage value of every unmortgaged deed, ignoring the bank-house restriction. No help from another player is assumed." | **Fixed in 14:34**, verbatim |
| C3 | A | Caption provenance lost: the six-sentence preface of `exhibit_captions.md` is gone, including "Every numeric panel reads retained audit outputs or canonical events" and "Figures are candidates for the main text and supplement, not a requirement to print nine full-page figures". Every caption's leading data link ("underlying table", "group table, bilateral table, eight residual records", "103-row table", "60-row table", "event table") is stripped, so no caption names its table. | End each caption with "Data: Table~\ref{tab:…}." (F2→T1, F3→T2, F4→T3/T4/T9, F5→T5, F6→T6, F7→T7, F9→T8). Restore the preface as the §1 introduction. | Open |
| C4 | A | `figures_and_tables.md` was not converted in the 14:26 build (0/45 sentences). | — | **Fixed**: `exhibit_index.tex`, 43/45. The two misses are the H1 and a splitter artifact; all six bullets were checked separately. |
| C5 | A | Peer exhibits are linked but not included: §3 is "The peer exhibit index is being assembled". | Native snippets for my three exhibits: [proposed/opus_exhibits.tex](proposed/opus_exhibits.tex). | Astra's 14:34 `prepare_supplement.py` adds S-numbered peer figures (Sol S1–S3, Fable grid) and tables (S01–S04); not yet built into a shared PDF. See C10. |
| C6 | B | ID collision in my own exhibits: the md headings say "T6. Normative contracts" and "T7. Affordance ledger", and the ledger cites "(M1, T4)". These are proposal numbers; shared T6 and T7 are different tables. | Renamed OC-1, OC-2 and OC-3 in my snippet, with an identifier note. | Proposal ready |
| C7 | B | My `outcome_grid.svg` renders an **all-black page** through rsvg-convert, because it uses CSS `var()` fills; Fable reproduced this. Rendered, it also prints the i.i.d. reference p-values that `integration_log.md:20` excludes, says "Argon", and labels rotations zero-based r0–r3 (its CSV is fully zero-based). | Index it without rendering it. If it must be shown, use [converted/outcome_grid.pdf](converted/outcome_grid.pdf) with a caption stating that the nulls are excluded and r0–r3 = rotations 1–4. | Indexed only, as recommended |
| C8 | B | Straight ASCII `"` in my exhibit md files render as a closing glyph at both ends with the shared converter. The shared md sources have 0 straight quotes. | Handled in my generator; Astra is told. | Proposal ready |
| C9 | B | Two source-wording flags. (a) Outline §4.2 and the README say "change quantity"; T7 measures the purchase multiset. (b) The F7 row of `figures_and_tables.md` says "selected uneven-build rejections", but the population is all such decisions. | (a) Fixed by Astra with a disclosed conversion footnote; Sol's audit fields confirm it. (b) Still verbatim; Astra's call. | (a) Fixed; (b) open |
| C10 | A | Astra's `prepare_supplement.py` does not convert my affordance ledger. It writes a new three-row tabularx in Astra's words, paraphrasing outline §6, and drops the Layer-1 rows (reference policies and 130 micro-scenarios marked "implemented, not measured"), the Layer-2 evidence map and the eight Layer-3 missing affordances (Fable flagged this; I verified it). Outline §2.4 links this exhibit. One source cell does overstate: "visible to all players" contradicts outline §3.3, where a logged utterance is not necessarily delivered. | **Author's ruling:** convert the exhibit faithfully (my OC-2) and attach a disclosed conversion-correction footnote to that cell, plus a §6 scope footnote on the reset row. Astra's compact table may stay only if labelled as a restatement and placed after OC-2. | Sent to Astra |
| C11 | C | Missing spaces in `prepare_supplement.py` note strings: "Boolean1=yes,0=no", "has43 builds,9 … and3", "has34 … plus3 defaults,3 conflicts and2", "including1600 … and3 Grok", "and31.5%", "section6". The S2 caption prints "93000"/"92550" without separators. | Insert spaces and separators. | Sent to Astra |
| C12 | B | **My own error, found through Fable's note:** my OC-3 marked only Opus's cost as a lower bound, but Grok also has 3 uncosted attempts. Astra's S03 note had this right. | Fixed in my generator: ≥ wherever `attempts_missing_cost` > 0. | Fixed in my proposal |
| C13 | C | S04, which converts my normative contracts from the CSV, drops the md caption sentence: "The same act has a different normative status across environments, so rates and labels do not transfer between them." The Arena App. D attribution is kept. | Add that sentence to the S04 note. | Sent to Astra |
| R1 | B | `\thefigure`=F and `\thetable`=T: any numbered peer float becomes F10 or T10, which reads like a shared exhibit that does not exist. | `\caption*` plus a manual LoT entry, or a separate prefix (as in my snippet). | **Fixed in 14:34**: the supplement resets counters with an S prefix and unique `\theH…` |
| R2 | C | The sha256 sits only in `source_manifest.json`, not in each snippet. | One comment line per snippet. | Open |
| R3 | B | Reuse portability: the snippets avoid fontspec-only constructs (`\ensuremath{\tau}` etc.), which is good. `longtable` cannot be used in two-column venue classes, so T5, T6 and T8 must stay one-column or appendix material. | Note this in the selection notes. | Open (advisory) |
| P1 | B | T1 fingerprint lines were appended on every plain rerun (Sol's finding). I reproduced 2→4 lines on the 14:26 generator. | — | **Fixed** in 14:31 (`t1_written` guard) |

### Verified correct (no action)

- **Outline:** 234/236 sentences are verbatim in the PDF. The two misses are deliberate: the H1 is retitled, and the "quantity" wording is corrected with a disclosed footnote that cites the audit field.
- **Outline structure:** section numbers 1–8 and 2.1–5.4 match the source; the front matter is unnumbered. The three RQs and the bold run-in labels are intact.
- **Glyphs and references:** 0 missing glyphs (τ is mapped to `\ensuremath{\tau}`), 0 undefined references and 0 overfull boxes in the outline.
- **Data copies:** 18/18 `latex/data` files are byte-identical to `astra/exhibits`; 9/9 figure assets are identical (Sol). No raster images are in the nine figures (Sol).
- **Table cells:**
  - Every cell in T1 and T3–T8 matches the CSV. T8 has 631/631 rows, T5 103/103 and T6 60/60. T9 has all values; `applied_action` is stated once as uniformly `end_turn`. Sol independently reports all 837 rows matching in exact cell order.
  - T2 rounds half-even consistently, matching F3's 1.12, and prints the exact fractions. siunitx is not used, so nothing is re-rounded.
- **Caption counts:** the caption numbers are recomputed from the tables:
  - 24/16 zero-rent units;
  - $450 timing difference;
  - 56 eliminations below the full bound;
  - greedy = full in 59 of 60 cases;
  - 4 automatic eliminations;
  - 58/34 winner units.
- **Figure legibility:** with landscape pages for F1, F3, F4, F5, F7 and F9, effective minimum text is ≥5.9 pt for every figure except F5 (5.1 pt). F5 is height-capped at 4.4 in to leave room for its two-paragraph caption. F8 in portrait is 5.95 pt minimum and visually legible.

## Proposals in this folder

- [proposed/prepare_sources.proposed.diff](proposed/prepare_sources.proposed.diff). A 32-line diff against the 14:26 generator, covering D1, D2, D4, C1 and C2. It was tested end to end in [snapshot2](snapshot2/): 0 overfull boxes, 0 broken identifiers, values still matching. D3's `filecolor` is a one-line preamble option, applied in snapshot2.
- [proposed/opus_exhibits.tex](proposed/opus_exhibits.tex) and its generator [make_opus_exhibits.py](proposed/make_opus_exhibits.py): OC-1 normative contracts, OC-2 the three-layer affordance ledger, OC-3 cost and usage. The test build has 8 pages, 0 overfull boxes and every prose sentence present; two checker misses were confirmed as extraction artifacts (a page break and a wrapped cell).
- [proposed/t06_eliminations.tex](proposed/t06_eliminations.tex) and its generator. A reference T6 that keeps the greedy route counts (houses, hotels and mortgages: 134/5/157). It compiles under pdflatex in 2 pages with 0 overfull boxes, and is optional.
- [converted/outcome_grid.pdf](converted/outcome_grid.pdf) and [print_safe_svg.py](print_safe_svg.py). A print-safe derived copy of my grid. No data or text changes; the source sha256 is recorded.

## Peer exchange (summary)

- **Sol** accepted five table-note corrections: the T6 bound definitions and automatic-row timing, the T8 balance-after-event wording, the T2 rounding trap, latency as observational, and Gemini (Argon). Sol confirmed C9a from the audit fields. Sol independently confirmed D1–C3 and contributed P1 and the T2 header wording.
- **Fable** reconciled the 63 versus 42 denominators exactly. Three later-buildable, non-built groups (G13 Opus LIGHT_BLUE, G13 Grok YELLOW, G14 Gemini YELLOW) explain the 4/4/3 versus 3/3/2 split. Fable challenged two of my exhibits (Arena App. D attribution; zero-based outcome-grid CSV), and I accepted both. Fable contributed D3, the Launch-action point.
- **I opposed** Fable's proposal to re-typeset F1 and F8 natively. Both PDFs already carry extractable text (F8: 237 words; F1: 88), a re-typeset would break the manifest hash chain, and the brief allows vector diagrams. Fable agreed: both stay as the hashed PDFs, and Fable's F1 transcription stays optional in Fable's own folder.
- **Process error (mine).** My informational reply to Fable reached the thread 13 seconds after Fable's run had completed, and it started a new run (ordinal 2) instead of steering the old one. The package rules forbid restarting a finished coauthor by message. I reported this to Astra, the owning parent, at once, asked Astra to cancel the run if unwanted, and sent no further messages to finished peers.
- **Astra** accepted the numbering, τ, landscape, T6 header, T8 wording, T9 and "quantity" fixes. Astra kept half-even rounding to match F3, which I accept because it is disclosed and not re-rounded.

## Limits

- I did not re-run the phase-2 reducers. Table values are checked against the frozen CSVs, not recomputed from the saved games.
- Sentence coverage is substring matching on normalized text. It shows that the words are present, not that their emphasis or placement is right; those I checked visually on the rendered pages.
- Text extraction from wrapped table cells interleaves columns. Table content was therefore checked at the `.tex` level (cells) and visually, not by PDF substring.
- My snapshots compile in my folder, so `run:` links resolve differently there. Link targets were checked as strings, not by opening them in a viewer.

## Final pass: pinned shared build 14:48:27

The PDFs and logs are copied into [final_1448/](final_1448/) with their sha256 values: `paper_outline.pdf` f46a72e5…, `figures_and_tables.pdf` 940935cc…. `source_sha256.txt` pins every source file. Every check below was run on **Astra's rendered output**, not on my rebuild, unless a row says otherwise.

| Check | Result |
|---|---|
| Pages | Outline 10; exhibit book 62 |
| Logs | 0 overfull boxes, 0 missing glyphs, 0 undefined references or citations, no rerun warning; both documents |
| Outline text | Every sentence present except the deliberate H1 retitle and the footnoted "quantity" correction. Thirteen raw checker misses were each traced: 10 are `\artifactref` footnote markers glued to link text, and 3 are sentences split by a page break. |
| Captions | 108/116. The 8 misses are expected: the file heading, "Figure selection", the preface path sentence rewritten to `astra/…` with footnotes, and the five stripped link stubs, now replaced by "Underlying data: Table …" inside each caption. |
| `figures_and_tables.md` | Every sentence present except its H1, once footnote markers are stripped |
| My exhibits (OC-1–OC-3) | All prose present. OC-2 carries both disclosed footnotes. Grok and Opus are marked ≥. Astra's paraphrase table is gone. The remaining checker misses are wrapped-cell interleaving (chunk overlap 0.92–0.98). |
| Table cells | T1 and T3–T9 match the CSVs in every cell (T8 631/631, T5 103/103, T6 60/60). T2 values and all four response conditions are present verbatim. |
| Copies | 18/18 data files and 9/9 figure PDFs byte-identical to `astra/exhibits` |
| Identifiers | 0 hyphen-broken canonical codes (`\tok`/`\path`) |
| Orientation | 0 sideways figure pages and 0 note-only pages. The 14:43/14:45 regression is resolved (see below). |
| Reproducibility | Rebuilding the 14:43 source with `build.sh` in [snapshot4/latex_asis](snapshot4/latex_asis/) gave page-identical text, rotation and page size for all 10 and 75 pages. The bytes differ (PDF ID/path). |
| Visual | Every page inspected as contact sheets in `final_1448/render_*`. Figures F1–F9 and S1–S4 are upright with complete captions. |

### Regression found and resolved during review (most severe finding)

In the 14:43 and 14:45 shared builds, `complete_conversion.py` appended the "Underlying data" note after `\end{figure}`. This produced 7 pages holding only that note. In pdflscape it also shipped F3, F4, F5, F7 and F9 with page `/Rotate 90` but unrotated content (caption text direction (1,0)): they displayed sideways, with the figure and caption clipped. 38/116 caption sentences were absent from the PDF, including "$103,450", "This is neither net ROI…" and "Cash is not liquidatable wealth…". I reproduced the defect from source with `build.sh`. I then tested a fix, [proposed/fix_data_pointer.py](proposed/fix_data_pointer.py), which moves each pointer inside its caption: 68 pages, 0 sideways, 0 note-only, 108/116 caption sentences. The 14:46 and later builds place the pointer inside the caption.

### Remaining items at close (all minor)

1. p55 holds only the "Opus peer exhibits" heading and identifier note: **my snippet's structure**. Fix: move those two lines inside the first `landscape`. Tested as [proposed/opus_exhibits_v2.tex](proposed/opus_exhibits_v2.tex) (sha256 02cb9c4b…) in [snapshot5](snapshot5/). The hash-tracked v1 (`28d16345…`, recorded in `supplement_manifest.json`) is deliberately left unchanged.
2. Duplicate renderings: S03 and OC-3 (cost), S04 and OC-1 (normative contracts). Their values agree. Keep one of each, or caption S03/S04 as compact views.
3. `complete_conversion.py` copies Fable's T6a/T9a from `latex_review/fable/proposed/snippets` without `track()`, so they have no recorded hash. Mine is tracked.
4. Cosmetic short pages: p48 (indexed-alternative paragraph), p15 and p16 (one small table each).

### Not checked by me

- The cell values of Fable's T6a/T9a companions; Astra's log says Sol checked them.
- S01/S02 cell values against Fable's JSON.
- Whether the `\artifactref` archive paths open the intended files; I checked them as strings only.
- Byte-for-byte reproducibility across machines or TeX versions; the README itself disclaims it.

Table values are verified against the frozen CSVs, not recomputed from saved games.
