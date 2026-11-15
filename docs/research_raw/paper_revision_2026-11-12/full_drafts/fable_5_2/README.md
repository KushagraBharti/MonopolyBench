# Fable 5.2 complete draft, 12 November 2026

A complete manuscript written independently by Fable 5.2 for the 12 November revision, before any cross-review. Read `manuscript.pdf`. Start with `handoff.md` for status and `findings_and_limits.md` for the argument, the dissent and the limits.

**Title.** What a Move Unlocks: Stated Consequences and Actions of LLM Agents in Twenty Monopoly Games.

## Files

| Path | Purpose |
|---|---|
| `manuscript.pdf`, `manuscript.tex`, `preamble.tex`, `references.bib` | The paper. 31 pages, references start on page 17. |
| `sections/introduction.tex`, `setting.tex`, `own.tex`, `rival.tex`, `talk.tex`, `discussion.tex`, `appendix.tex` | Authored sections. |
| `sections/facts.tex`, `tables.tex`, `quotes.tex`, `prompt_*.tex`, `refusal_message.tex` | Generated. Do not edit by hand. |
| `analysis/` | Scripts for every tabulation, table, figure, quotation and check. |
| `data/` | Script outputs. `facts_index.txt` lists every number the text cites. `quote_manifest.json` locates every quotation. |
| `assets/` | Two figures, PDF and PNG. |
| `qa/document_checks.json`, `qa/render/`, `qa/manuscript_text.txt` | Build checks, two-page contact sheets, extracted text. |
| `initial_position.md` | Position recorded before any tabulation or prose. |
| `findings_and_limits.md` | Findings with levels, dissent, corrections, limits, and exactly what literature was read. |
| `evidence_map.md` | Claim to record to script, with fresh, reconciled, read, reading, pattern or inherited status. |
| `handoff.md` | Status for cross-review. |
| `source_manifest.json` | Hashes of inputs and package files. |

## Build

Requirements: LuaLaTeX with `latexmk` (TeX Live at `/Library/TeX/texbin` on this machine) and Python with NumPy, Matplotlib, Pillow and PyMuPDF. The provisioned environment is `/tmp/monopoly-astra-rewrite-venv/bin/python`. Set `PYTHON` to use another interpreter.

```sh
./build.sh            # rebuild data, quotes, tables, figures, PDF, checks, manifest
./build.sh --tex-only # compile the PDF from the generated files already present
```

The full build takes about half a minute. Run one script alone from `analysis/`, for example `python b1_offers.py`.

| Script | Reads | Writes |
|---|---|---|
| `corpus.py` | loader for the twenty saved games | (imported) |
| `b1_offers.py` | `decisions.jsonl` | offer ledger, full form by completion table, strata, composition, sensitivity ranges, counters, pattern matches |
| `b2_debt.py` | `decisions.jsonl`, `events.jsonl` | debt episodes, three tiers, sixteen cases, nineteen uses, first texts |
| `b3_conditions.py` | attempts, prompts, usage, request records | refusals, prompt text and diff, request settings |
| `b4_provenance.py` | run reports, `game-index.csv`, `git show` of two source commits | game map, seeds, commits, both replay comparisons, tool choice |
| `b5_incidents.py` | prompts, actions, events | asserted facts for the eight incidents |
| `build_quotes.py` | `decisions.jsonl` | `sections/quotes.tex`, quote manifest, the sixteen readings |
| `build_tables.py` | the outputs above | `sections/facts.tex`, `sections/tables.tex`, `data/facts_index.txt` |
| `make_figures.py` | the outputs above | `assets/*.pdf`, `assets/*.png` |
| `verify_document.py` | the PDF, the log, the manifests | `qa/document_checks.json` |
| `render_pages.py`, `write_manifest.py` | the PDF, the package | contact sheets, `source_manifest.json` |

The text cites numbers as `\fact{key}`. An unknown key is a LaTeX error, so a changed tabulation either changes the paper or stops the build. Quotations are generated from stored fields. `verify_document.py` re-reads each one by file hash, line and JSON pointer and fails on any mismatch.

Resampling uses stored observations only. Seed-block resampling enumerates all 3,125 ordered resamples of the five blocks. Game resampling draws 20,000 resamples with NumPy seed 20261112.

## Inputs

- The twenty saved games under `saved_games/railway-research-12-games-2026-10-25/` and `saved_games/railway-research-8-games-2026-10-26/`.
- `contracts/data/board.json`.
- Five retained files from earlier paper work, read for reconciliation or inherited results. `source_manifest.json` lists them with hashes.
- The four quotation files of the previous integrated paper, read to confirm that reused quotations are character-identical.

## Scope

No game, engine run, replay, baseline, synthetic test, branch, rollout, provider probe or model query. No engine import. No edit outside this directory. No commit or push. No subagent. Earlier engine-executed checks, stored replay reports and earlier reason codes are used as inherited results and labeled as such in the paper.
