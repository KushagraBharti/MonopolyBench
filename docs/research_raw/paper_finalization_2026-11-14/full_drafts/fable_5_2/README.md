# Complete independent draft, Fable 5.2, 14 November 2026

**Title:** What Can Be Raised? Financial Assessment and Economic Conduct of LLM Agents in Twenty Monopoly Games

**Read:** `manuscript.pdf` (29 pages: the main text ends on page 9, references run to page 10, and the appendix is pages 11 to 29).

This is one author's complete paper, written without opening the other authors' new drafts. It has not been submitted anywhere and makes no claim about a venue or a score. The human author is Kushagra Bharti, taken from `CITATION.cff`. No affiliation or email is given.

## Build

From this folder:

    PAPER_PYTHON=/path/to/python bash build.sh

The command used for the delivered PDF was

    PAPER_PYTHON=/Users/kushagra/CS-Projects/MonopolyBench/python/.venv/bin/python bash build.sh

Requirements: Python 3 with `matplotlib` and `PyMuPDF`, and a TeX installation with `lualatex`, `latexmk`, `bibtex` and the TeX Gyre fonts. The repository's `python/.venv` has both Python packages. `build.sh` adds `/Library/TeX/texbin` to the path.

The build runs seven scripts in `tools/` over the saved games, compiles `manuscript.tex`, copies the PDF to this folder and runs `tools/08_verify.py`. It exits non-zero if any of the 36 checks fails. A full build takes about two minutes.

The build reads stored JSON and JSONL. It does not import the rules engine, replay a game, run a policy, search states or call a model. `tools/lib.py` finds the repository root by walking up from its own location, so the folder must stay inside the repository.

## Layout

| Path | Contents |
|---|---|
| `manuscript.tex`, `preamble.tex`, `references.bib` | Document source |
| `sections/s1_intro.tex` to `s8_scope.tex`, `appendix.tex` | Authored text |
| `sections/gen_*.tex` | Generated table rows, quotations, full first responses and prompts. Do not edit by hand |
| `tools/01_episodes.py` | Rebuilds the 188 financing episodes from `decisions.jsonl` and `events.jsonl` |
| `tools/02_finance.py` | Census, payable partition, first actions, premises of the continued-financing argument |
| `tools/03_stated_totals.py` | Number match of stated totals against the full bound and the listed-only total |
| `tools/04_corpus.py` | Corpus counts, refusals, channel conflicts, cohort |
| `tools/05_bargaining.py` | Rebuilds and tabulates all 920 responses; enumerates the block bootstrap |
| `tools/06_quotes.py` | Extracts every quotation from its stored field, with hashes and offsets |
| `tools/07_tables.py` | Writes LaTeX fragments, the supplement and the figure |
| `tools/coding.py` | The author's tier coding of the sixteen first responses and of their carried notes |
| `tools/08_verify.py` | Checks the PDF against the data and the stored fields |
| `data/` | Generated JSON. `game_map.json` is the only input copied from the 12 November package |
| `supplement/` | Machine-readable release files (see below) |
| `assets/fig_sixteen.pdf` | Figure 1 |
| `qa/` | Build logs, `verification.json`, rendered page images |
| `evidence_map.md` | What each claim rests on, and whether it was recomputed or inherited |
| `changes_and_dissent.md` | What changed from the 12 November manuscript, my judgments and my dissent |
| `verification.md` | What was checked in this round and how |
| `handoff.md` | Summary for integration, with exact cuts |

## Supplement

| File | Contents |
|---|---|
| `supplement/episodes_188.csv` | One row per financing episode: sums, category, menu, first action, outcome, source line |
| `supplement/sixteen_first_texts.json` | Both text channels of the sixteen first responses, plus public message, assistant content, hashes, pointers, routes, tier coding and carried-note summary |
| `supplement/nine_departures.json` | Every channel of the nine first actions that depart from the asset bound |
| `supplement/stated_totals_unpayable.json` | The number match for all 56 unpayable debts |
| `supplement/system_prompt_standard.txt`, `system_prompt_recovery.txt` | The two stored system prompts |

## Scope

No game, engine step, replay, policy, search, synthetic state or model call was run for this draft. No file outside this folder was written. No commit was made.
