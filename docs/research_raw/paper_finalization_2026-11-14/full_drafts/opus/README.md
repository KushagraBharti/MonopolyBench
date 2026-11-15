# Opus finalization draft (14 November 2026)

**Title:** *Financial Assessment and Strategic Conduct of LLM Agents in Twenty Monopoly Games*
**Author on the byline:** Kushagra Bharti (from the repository `CITATION.cff`). AI assistance is disclosed in Appendix K; assistants are not authors.

Read `manuscript.pdf`. It is a venue-neutral named preprint: two columns, 10 pt TeX Gyre Termes, 0.75 in side margins. The main text runs from page 1 to page 8, where the references begin. Appendices A to K run to page 22.

## Rebuild

Run this from this folder:

```
PAPER_PYTHON=python3 bash build.sh
```

Requirements:

- Python 3.10 or later, standard library only.
- LuaLaTeX and latexmk, with the packages named in `preamble.tex` and the TeX Gyre Termes and Heros fonts.
- Ghostscript (`gs`), which `tools/verify.py` uses for PDF text and page checks.
- A checkout of the MonopolyBench repository. The scripts find the repository root by walking up from their own path to the directory that contains both `contracts/` and `saved_games/`.

`build.sh` runs these steps in order:

1. `tools/finance.py`: the 188-episode census, entry bounds, the 62/53/16 partition, first actions, financing order and the Proposition 1 premises.
2. `tools/channels.py`: every text channel for the sixteen focal debts, the six above-bound starts and G12 d249, with SHA-256 hashes.
3. `tools/named_actions.py`: the named-action scan over all 338 liquidation decisions.
4. `tools/bargaining.py`: tabulations from the retained 920-response ledger.
5. `tools/provenance.py`: the cohort map, run commits and source-file hashes. It reads git blobs only.
6. `tools/conditions.py`: refusal and reasoning-field counts.
7. `tools/tables.py`: generated LaTeX tables, the TikZ figure and the appendix texts.
8. `tools/quotes.py`: checks every quoted span verbatim against its original record field. A missing span stops the build.
9. `latexmk -lualatex manuscript.tex`, then copies `build/manuscript.pdf` here.
10. `tools/verify.py`: re-checks quotes, prose numbers, source identity, the em-dash rule, LaTeX diagnostics, words and pages. It writes `qa/verification.json`.

No step imports or executes the rules engine. No step replays a game, runs a policy or search, builds a synthetic state, or calls a model or provider.

## Files

| Path | Content |
|---|---|
| `manuscript.tex`, `preamble.tex`, `sections/appendix.tex`, `references.bib` | Authored source |
| `sections/gen_*.tex` | Generated tables, figure, appendix texts and quotation macros. Do not edit them by hand. |
| `data/focal_channels.json` | Machine-readable supplement: all channels for the 23 focal first decisions, with field hashes and carried notes |
| `data/sixteen_rubric.json` | The author's model-assisted coding of the sixteen texts, with the rubric and its limits |
| `data/finance_census.json`, `data/continuation_premises.json` | Per-episode census and proof premises |
| `data/quote_registry.json`, `data/quote_manifest.json` | Quoted spans with field hashes and offsets |
| `data/bargaining_census.json`, `data/named_action_scan.json`, `data/provenance.json`, `data/response_conditions.json`, `data/sixteen_numeric_checks.json` | Other computed outputs |
| `qa/` | Script outputs, `verification.json`, rendered page images `p01.png` to `p22.png`, and extracted PDF text |
| `evidence_map.md` | Every claim with its evidence and status, plus the access depth for each literature source |
| `changes_and_dissent.md` | What changed from the 12 November integrated paper, my independent judgments, and my dissent |
| `verification.md` | What was checked, what is inherited, and the scope-compliance record |
| `handoff.md` | Summary for integration, with optional cuts |
