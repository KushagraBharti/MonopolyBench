# Opus initial review position: LaTeX conversion of steps 11–14

Opus (claude-opus-5-5), 2026-10-29. Written before reading any peer's `latex_review/` file and before `latex/` existed. One caveat: Sol's short chat summary arrived while I was drafting. Its overlapping points are marked **[also Sol]**. I reached them independently, from the source checks listed at the end.

Scope: the whole conversion. That covers outline hierarchy and text, all nine captions and their encoding notes, the nine table datasets, the peer exhibits, the build, PDF readability and reuse in a later manuscript. I propose fixes only in this folder. I do not touch shared LaTeX, original artifacts, `literature_review.md` or any `.bib`.

## A. Source inventory I will audit against

| Source | Facts that define a faithful conversion |
|---|---|
| `paper_outline.md` | 3,115 words and 28 headings. The headings are: title (H1); `Working title…`, `Abstract plan`, sections `1.`–`8.` and `Appendix and drafting gates` (H2); subsections 2.1–2.4, 3.1–3.4, 4.1–4.4 and 5.1–5.4 (H3). Three numbered RQs. Bold run-in labels: **Evidence/exhibit(s):**, **Alternative:**, **Citations:**, **Transition:**. 14 links: 9 shared figures, Sol S3, Fable stock grid, Opus affordance ledger, `experiment_decisions.md` and `literature_review.md`. Non-ASCII: `τ` (in τ-bench), en/em dashes and curly quotes. |
| `figures_and_tables.md` | 557 words; a 9-row figure table; the coauthored-exhibit list; draft selection; 34 links; `×`. |
| `astra/exhibit_captions.md` | 1,480 words; 9 captions; 3 encoding/source notes (F2 source version, F5 encoding, F6 encoding); the "Figure selection" paragraph; em/en dashes. |
| Tables T1–T9 | Rows: 20, 4, 4, 3, 103, 60, 631, 4 and 8. Total 837, plus headers. The manifest's 9 checks pass. |
| Peer exhibits | **Sol:** S1/S2/S3 (PNG at 220 dpi and SVG, no PDF), `negotiation_denominators.csv`, `spending_units.csv` (103 rows). **Fable:** stock grid (PNG only, 160 dpi), `house_stock_series.csv` (1,136 change rows), `first_management_causes.csv` (4 summary rows; the JSON holds all 63 rows). **Opus:** `outcome_grid.svg` (SVG only), `normative_contracts.md/.csv` (7 rows), `affordance_ledger.md`, `cost_usage.csv` (4 rows). |

## B. Defects I expect to check, and the fix I would propose

### B1. Hierarchy and text

1. **Double or shifted numbering.** The outline hard-codes `1.`–`8.` and `2.1`–`5.4`. If `Working title` and `Abstract plan` become numbered `\section`s, Introduction becomes §3 and every number in the text is wrong. Fix: make those two and the appendix `\section*`, and number sections 1–8 so that LaTeX numbering equals the source numbering. Alternatively, put the source number in the heading text with `\section*`.
2. **Run-in labels dropped.** **Evidence/exhibit:**, **Alternative:** and **Transition:** carry the outline's structure. Keep them as `\paragraph*{…}` or `\textbf{…}` run-ins. Each label occurrence in the source should map to one in the PDF.
3. **Links.** Each of the 14 outline links needs a clear target. A figure in the package should get `\cref{fig:…}` while keeping the link text. A file outside the package should get `\path{…}` relative to the base, not the `latex/` folder. A hyperlink that silently resolves relative to `latex/` breaks.
4. **Escaping hazards.** I will grep the rendered PDF text for the following:
   - every `$` amount, since an unescaped `$` silently enters math mode;
   - `%`, which is a comment;
   - underscores in tokens such as `end_turn`, `tool_choice="required"` and `decisions.jsonl`;
   - `τ`. With Latin Modern under fontspec it is a missing glyph, and lualatex only warns in the log ("Missing character"). For a pdflatex venue template, write `$\tau$`-bench.
5. **"Step" versus section numbers.** "steps 15", "17–18" and "11–14" are project stages. They must not become `\ref`s or be renumbered.

### B2. Captions

1. All nine captions must be complete, with every limit sentence ("not ROI", "Cash, not wealth", "selected contrasts, not prevalence rates", "No $70 persuasion effect…") and every "Source:" line. The three encoding notes must be present, either in the caption or as an attached figure note.
2. Use `\caption[short]{long}` so the List of Figures stays readable.
3. "Left:/Right:" panel references in F3 and F4 must match the rendered panel order.
4. Captions must not say "PNG/SVG". The LaTeX build includes the PDF.

### B3. Tables: units, rounding and representation

- **Rounding.** State the rule once, compute from the integer numerators and denominators, and round half up. Trap: Gemini proposals per proposing turn is 18/16 = 1.125. Python's `round(1.125, 2)` gives **1.12** (banker's rounding), while siunitx's default gives **1.13**. The generator and the typeset value must agree.
- **Currency.** Game dollars and provider USD are different quantities. Label game amounts "game \$" and costs "USD". **[also Sol]**

| Table | Units and representation to check |
|---|---|
| T1 cohort | Seat is one-based, p1–p4. Turns are game turns. Seed is an integer without grouping. Shorten the 64-hex fingerprint to 8 characters and give the two full values in the note, with games 1–4 and 5–20. |
| T2 negotiation | Count columns stay integers. Propensity and eligible-decision rate in % (1 dp). Proposals per proposing turn and eligible decisions per turn are **ratios** (2 dp), not %. **[also Sol]** Keep the response-condition column, as the caption promises. |
| T3 trade groups | Reorder into logical flow: groups → first-management built → buildable during window → entry-buildable → entry-buildable built → without access. Add a labelled sum row (63, 43, 54, 42, 34, 0); every sum matches the captions. |
| T4 bilateral | Rows for 0/1/2 newly completed sides = neither/one/both: 60/43/10. Total 113 settlements. |
| T5 spending | Longtable with the header repeated and continuation marks. Game-\$ columns right-aligned with comma grouping. Booleans as Yes/No, not a glyph. Totals row: outlay 103,450; sale proceeds 13,500; after-first-spend rent 92,550; whole-game rent 93,000. Keep the event sequence as an integer. |
| T6 eliminations | **Rename `avoidable`.** It reads as "elimination avoidable", which the F6 caption explicitly disclaims. Use "Own legal sequence pays current debt". **[also Sol]** Define the bounds from my phase-2 script: `menu` = cash plus currently mortgageable deeds (first screen); `accessible` = cash plus greedy own liquidation under the bank-house rule; `full` = cash plus half building value plus all unmortgaged mortgage values, ignoring bank stock. For the four automatic rows, the bounds are computed at the triggering decision state. The `steps` strings run up to 686 characters, so typeset counts (sales, mortgages) and point to the CSV/JSON for the sequence. |
| T7 recovery | Opus's 0/0/0 must not read as "never preserves". Add a note that the refusal condition leaves no corrective attempt and that all 61 are legal after interleaving. |
| T8 cash | 631 rows, about 12–14 pages at `\footnotesize`. `cash` is the **balance after the event**, not the change. Turn-zero initial balances are not rows. Reason codes in `\texttt` with underscores escaped. Belongs in an appendix or a separate tables PDF; a per-game summary may sit beside it. |
| T9 residuals | Show the short decision ID with the game, and give the full campaign ID or the path:line in the note or a second line. Category names must match the caption: engine default, received END/content conflict, consistent END with stated reserve. An empty selected attempt is not attempt 0. **[also Sol]** |

### B4. Extra peer exhibits

| Exhibit | Treatment |
|---|---|
| Opus `outcome_grid.svg` | SVG only. Avoid `svg.sty`, which needs shell escape and Inkscape. Pre-convert with `rsvg-convert -f pdf` in a script that records hashes. |
| Sol S1–S3 | Same treatment. Prefer the SVG→PDF route over the 220 dpi PNG. |
| Fable stock grid | PNG only. At `\textwidth` the effective resolution is about 270 dpi, which is acceptable. Note that it is raster. |
| Normative contracts | Native table. |
| Affordance ledger | Native table or structured list. |
| Cost/usage | Native table. Keep the Opus lower-bound note and the `Argon`/Gemini naming. |
| Fable first-management summary | Native table. Do not mix its whole-window denominators (4 defaults, 4 conflicts, 3 valid ENDs) with F4's eight entry-buildable residuals (3/3/2) without labels. |
| Fable stock series, Sol cross-check CSVs | Indexed with path and role, not dumped. |

### B5. Readability: effective figure text size

The PDFs are wide, set at a 10 pt base with labels at 7.7–9 pt. At a 6.5 in text width, the scale factors are:

| Figure | Natural width | Scale | Effective text |
|---|---|---|---|
| F9 | 12.1 in | 0.54 | ≈4.2–5.4 pt |
| F4 | 11.7 in | 0.55 | ≈4.4–5.5 pt |
| F5 | 10.7 in | 0.61 | — |
| F3 | 10.3 in | 0.63 | — |
| F7 | 9.9 in | 0.66 | — |

Below about 6 pt the text is hard to read. Without regenerating artifacts, the fix is a landscape page or `\textheight`-width rotation for F4 and F9, or wider margins only in the figures document. Changing the figure size is an exhibit change for the manuscript stage.

### B6. Reuse in a later manuscript

1. One snippet per figure or table. Snippets carry no `\documentclass`, geometry or package loading. Use stable labels (`fig:f04-…`, `tab:t06-…`).
2. Keep snippets compilable by pdflatex: no fontspec-only constructs; `$\tau$`.
3. `longtable` fails in two-column templates. Mark the long tables as one-column or appendix-only.
4. Put the source CSV path and its SHA-256 from the manifest in each table snippet. Ideally the build checks the hash, so a stale snippet is detectable.

### B7. Build checks I will run on the rendered PDFs

- `latexmk -lualatex` from a clean copy in my own folder.
- Log greps: undefined references and citations, "Missing character", overfull boxes over 1 pt, float-too-large, rerun warnings.
- `gs -sDEVICE=txtwrite`: word and phrase coverage of the outline and captions, the `$` amounts, all claim-limit phrases, and per-table row counts.
- `gs -sDEVICE=png16m` page renders, which I inspect visually.
- Page count and size, and figure scaling.

## C. Source-level discrepancies to flag, not silently fix

1. **Outline §4.2 and the README:** "Successful retry may change **quantity**", and the README's "Recovery can change quantities". T7/F7 and Sol's audit measure a changed **purchase multiset (allocation)**. A same-count reallocation is not a quantity change, and the audit holds only a boolean `allocation_preserved_within_decision`. Proposed source wording: "may change the purchase allocation". Preserve the original until Astra rules on it, and record the change in the integration log.
2. **`figures_and_tables.md`, F7 row:** "selected uneven-build rejections". F7's caption defines the population as all decisions with an uneven-intermediate-building rejection. "Selected" suggests sampling. Proposed: "decisions with an uneven-build rejection".
3. **Naming:** the cost table uses `Argon` while all other exhibits use `Gemini`. The LaTeX version should say "Gemini (Argon)" in its header, not a third form.

## Checks behind this position

- Read in full: `paper_outline.md`, `figures_and_tables.md`, `astra/exhibit_captions.md`, `astra/handoff.md`, `README.md` and my `opus/handoff.md`.
- Printed all small CSVs. Recomputed T5 totals (103,450 / 92,550 / 93,000 / 13,500; 58/34; 40/26), T6 counts (56 declared / 4 automatic; 3 payable; G7 440/1,310/750), T3 column sums and the T2 ratio derivations.
- Read the T6 bound definitions in `phase2/core_review/opus/scripts/bankruptcy_bounds.py` and the Sol recovery-audit summary.
- Read the PDF MediaBoxes and font types: all nine are Type 42 with no Type 3. Read `rcParams` and the `fontsize` and `figsize` calls in `build_exhibits.py`.
- PIL: sizes and dpi of the peer PNGs. Checked SVG widths.
- Tools: `latexmk` and `lualatex` (TeX Live 2026), `gs` and `rsvg-convert` are available; `pdftotext` is not.
