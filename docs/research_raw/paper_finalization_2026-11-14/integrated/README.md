# Financial Assessment and Strategic Bargaining by LLM Agents

Named preprint by **Kushagra Bharti**, November 2026. Start with [manuscript.pdf](manuscript.pdf). The source and evidence package is [release.zip](release.zip); [ACTIVE_SOURCES.md](ACTIVE_SOURCES.md) identifies the compiled sections. All eight incident histories, both text channels for the sixteen focal debts, prompts and cohort mapping are in the supplement.

The paper integrates four independent complete manuscripts by Astra, Sol, Opus and Fable 5.2, followed by whole-paper cross-review and source-based adjudication. The decision record is `../final_review/ADJUDICATION.md`. The assistants are disclosed as research tools, not human authors or independent human validators. This is an observational study of the existing twenty games; no new evaluation was run for the revision. No submission or acceptance is asserted.

## Build the document

```sh
bash build.sh
```

The default build uses the packaged static LaTeX, bibliography, figures and generated text. Install LuaLaTeX, latexmk, BibTeX and the TeX Gyre/Latin Modern fonts. It needs neither the saved-game archive nor network access. The result is `manuscript.pdf`.

The shipped PDF hash identifies that exact file. Builds in another directory can change the PDF's internal identifier while reproducing the same page text and rendered contents. A changed binary hash after rebuilding does not itself mean the findings changed.

## Check archive integrity

Before rebuilding or regenerating files:

```sh
python3 tools/package_release.py --verify
```

`release_manifest.json` gives SHA-256 hashes for every packaged file, including the shipped PDF; `release.sha256` gives the ZIP hash. The archive omits superseded section fragments, local Python environments and build/render intermediates. The complete research history remains in the repository.

## Recheck the original records

These optional commands require a complete MonopolyBench checkout with the `saved_games` paths in `data/game_map.json` and historical research inputs. They read stored records and write regenerated derived files in this package. Use a copy when preserving shipped-file hashes.

```sh
python3 tools/refresh_records.py
python3 tools/prepare.py
python3 tools/check_sources.py
python3 tools/check_integrated_additions.py
python3 tools/check_stated_totals.py
python3 tools/check_assessment_subset.py
```

- `refresh_records.py` re-extracts the 188 first responses, resource sums, corpus totals and the 108/12/9/2 continuation-proof partition. Group keys are sorted for stable output.
- `prepare.py` verifies the complete first-response record and generates the sixteen-case text supplement.
- `check_sources.py` checks retained quotations and 920 offer/action joins, and reads historical audit/replay reports without executing them.
- `check_integrated_additions.py` checks the thirty preservation cases, the 29 menus offering a sale, and the G7 quotations and public-message receipt.
- `check_stated_totals.py` reproduces the supplemental numeric-presence screen. Matching a value is not whole-response accuracy.
- `check_assessment_subset.py` verifies the 37-entry population and the 21 additional selected fields. It preserves model-assisted labels; it does not validate their semantics automatically.

None imports the engine, executes a policy, searches game states, replays a game or queries a model. Bargaining classifications and resampling outputs come from `docs/research_raw/paper_revision_2026-11-12/integrated/`, whose scripts, seeds and input hashes remain available. Do not regenerate files in that protected historical directory.

## Inspect the PDF

```sh
python3 -m venv /tmp/monopoly-paper-env
/tmp/monopoly-paper-env/bin/pip install pymupdf pillow
PAPER_PYTHON=/tmp/monopoly-paper-env/bin/python bash build.sh --verify
```

This optional verification requires the repository archive. It checks displayed quotations and focal fields against source records, historical-file preservation, document diagnostics and page boundaries. It writes page renders and contact sheets under `qa/`. The historical payment witnesses, reachability search and replay results are not rerun.

See [evidence_map.md](evidence_map.md) for claim-to-record mapping and [VERIFICATION.md](VERIFICATION.md) for final release checks.
