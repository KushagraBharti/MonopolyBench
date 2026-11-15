# Independent complete manuscript by Sol

**Financial assessment and strategic conduct in twenty LLM Monopoly games**

Named preprint by Kushagra Bharti, 14 November 2026. The complete manuscript and appendix are in [manuscript.pdf](manuscript.pdf); editable entry point [manuscript.tex](manuscript.tex). This is an independent whole-paper draft for integration. No other new author draft was read.

From this directory, build the self-contained document with LuaLaTeX, BibTeX, latexmk, and the TeX Gyre fonts:

```sh
bash build.sh
```

The build uses only packaged sources. It does not execute analysis, an engine, a model, a policy, or a replay. It sets `SOURCE_DATE_EPOCH=1794614400` and writes intermediate files under `build/`.

Optional PDF verification and rendering require PyMuPDF and Pillow:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-document.txt
.venv/bin/python tools/verify.py
```

The existing local `.venv` was used for verification. The environment is not part of the release archive. The exact recorded environment versions are in `qa/environment.txt`.

Optional refresh from the repository's existing saved records:

```sh
python3 tools/prepare.py
```

Read the script first. It extracts original decision fields, recomputes resource sums and continuation premises, and copies historical tables with the local caption/continuation-head corrections. It never imports the engine or executes transitions. It overwrites this draft's generated data/sections only. The default build needs no refresh. Additional source checks can be run with `python3 tools/check_sources.py`; they read original records and stored historical reports, never execute them.

`data/episodes_188.json` preserves objective first-response fields for every debt entry; `data/sixteen_channels.json` contains all focal notes, provider text, content, actions, memory, and provenance. The appendix prints every nonempty focal field. `data/continuation_premises.json` supplies the 108/12/9/2 source-proof premise partition. `data/game_map.json` maps the full canonical saved-game directories. Historical quote manifests and bargaining ledgers are included with inherited status documented in `evidence_map.md`.

Read `handoff.md` for integration decisions, `changes_and_dissent.md` for substantive independent judgments, and `verification.md` for the precise checks and their limits. No new evaluation, engine execution, search, provider call, subagent, commit, or push occurred.
