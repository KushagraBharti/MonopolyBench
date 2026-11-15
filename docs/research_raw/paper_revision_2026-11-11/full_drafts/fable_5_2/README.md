# Fable 5.2 independent draft

A complete paper written independently for the 11 November 2026 revision, before any cross-review. Read `manuscript.pdf`. Start with `handoff.md` for status and `findings_and_limits.md` for the argument and its limits.

**Title.** LLM Agents Withhold a Rival's Monopoly Until They Need the Cash: Bargaining, liquidity and default in twenty games of Monopoly.

## Files

| Path | Purpose |
|---|---|
| `manuscript.pdf`, `manuscript.tex`, `preamble.tex`, `references.bib` | The paper. |
| `sections/*.tex` | Authored sections: `introduction`, `setting`, `attention`, `liquidity`, `conversion`, `default`, `discussion`, `appendix`. |
| `sections/facts.tex`, `tables.tex`, `quotes.tex`, `prompt_*.tex`, `refusal_message.tex` | Generated. Do not edit by hand. |
| `analysis/` | Scripts for every tabulation, table, figure, quotation and check. |
| `data/` | Script outputs. `facts_index.txt` lists every number the text can cite. |
| `assets/` | Figures, PDF and PNG. |
| `qa/document_checks.json`, `qa/render/`, `qa/manuscript_text.txt` | Build checks, page contact sheets, extracted text. |
| `initial_position.md` | Position recorded before the work. |
| `findings_and_limits.md` | Findings, null results, corrections, objections. |
| `evidence_map.md` | Claim to source map, fresh against inherited. |
| `literature_inspiration.md` | What was read and how it is used. |
| `handoff.md` | Status for cross-review. |
| `source_manifest.json` | Hashes of inputs and package files. |

## Build

Requirements: LuaLaTeX with `latexmk` (TeX Live 2026 at `/Library/TeX/texbin` on this machine) and Python with Matplotlib, Pillow and PyMuPDF. The provisioned environment is `/tmp/monopoly-astra-rewrite-venv/bin/python`. Set `PYTHON` to use another interpreter.

```sh
./build.sh            # rebuild data, quotes, tables, figures, PDF, checks, manifest
./build.sh --tex-only # compile the PDF from the generated files already present
```

The full build takes under two minutes. It reads the twenty saved games under `saved_games/railway-research-*`, `contracts/data/board.json` and ten retained files from earlier paper directories (listed in `source_manifest.json`). It imports no engine code, runs no game and makes no model call. It writes only inside this directory.

The text cites numbers as `\fact{key}`. An unknown key is a LaTeX error, so a changed tabulation either changes the paper or stops the build. `analysis/verify_document.py` re-reads every quotation from `decisions.jsonl` by file hash, line and JSON pointer and fails on any mismatch.

## Scope

No new games, engine runs, replays, synthetic tests, baselines or model evaluation calls. No edits outside this directory. No commits. Earlier engine-executed checks and semantic readings are used as inherited results and are labeled as such in the paper.
