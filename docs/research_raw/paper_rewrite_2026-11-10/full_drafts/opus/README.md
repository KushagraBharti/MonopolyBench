# Opus independent full draft

*Bargaining, Building and Bankruptcy: An Observational Study of LLM Agents in Twenty Complete Monopoly Games.* Complete manuscript in [manuscript.pdf](manuscript.pdf), source in [manuscript.tex](manuscript.tex).

Start with [handoff.md](handoff.md) for the thesis, new evidence, choices and dissent. [evidence_map.md](evidence_map.md) marks every claim as checked here, new here, or inherited. [figure_table_decisions.md](figure_table_decisions.md) explains what moved where. [literature_updates.md](literature_updates.md) records the versions inspected on 2026-11-10. [initial_position.md](initial_position.md) was written before drafting.

## Rebuild

```sh
python3 tools/retabulate.py
python3 tools/build_tables.py
python3 tools/build_opus_quotes.py
python3 tools/check_delivery.py
latexmk -lualatex -interaction=nonstopmode -outdir=build manuscript.tex
cp build/manuscript.pdf manuscript.pdf
```

The scripts need only the Python standard library. They read the shared ledgers in `../../data/` and, for quotes and delivery, the canonical saved games under the repository's `saved_games/railway-research-12-games-2026-10-25/`. They write only inside this folder. Figures and shared quote macros are read from `../../assets/` and `../../sections/`.

## Scope

No game, model query, engine run, reference-policy run or synthetic test was executed for this draft. Canonical games, engine, prompts, the original manuscript and shared root files were not modified. Nothing was committed or pushed.
