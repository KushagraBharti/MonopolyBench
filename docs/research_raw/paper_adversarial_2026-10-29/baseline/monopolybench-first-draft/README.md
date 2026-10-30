# Complete first manuscript draft

The entry point is [manuscript.tex](manuscript.tex); [manuscript.pdf](manuscript.pdf) is the compiled paper. The manuscript is new. The existing phase-3 outline, outline PDF, literature review and bibliography are unchanged.

The 34-page draft includes the complete abstract, introduction, environment, methods, economic results, social results, infrastructure validation, discussion, related work, limitations, conclusion and appendices. It contains four manuscript-sized vector figures, ten numbered tables and 32 cited references. It is venue-neutral and has not been submitted.

## Build

With TeX Live and LuaLaTeX installed:

```sh
bash build.sh
```

Build auxiliaries go to `build/`; the PDF is copied to the package root. `references.bib` is the print bibliography. `references_source.bib` retains the copied source-verification notes, which were removed from the printed entries without changing bibliographic claims. The print copy also preserves Vending-Bench 2's capitalization and prints its URL once.

To regenerate the four figures and two generated tables, use Python with Matplotlib:

```sh
python tools/build_exhibits.py
```

To check the built manuscript with PyMuPDF:

```sh
python tools/verify_draft.py --portable
```

Inside the original repository, omit `--portable` to also compare the protected outline/literature hashes and the nine copied data files against their source exports. The portable check validates numerical invariants, citations, references, log diagnostics and PDF geometry; it does not have the original repository files needed for those additional comparisons.

## Provenance and review

- [evidence_map.md](evidence_map.md) maps the integrated claims and figures to retained analyses.
- `coauthors/sol`, `coauthors/opus` and `coauthors/fable` preserve the co-written sections, source maps and accepted objections. Astra wrote the integrated manuscript and performed the final assembly.
- `final_review/` preserves the three independent integration-review reports. Their scopes differ; reading an existing result is not relabeled independent replication.
- [integration_log.md](integration_log.md) records substantive writing-stage corrections and review dispositions.
- [verification.json](verification.json) records the final local manuscript checks. `figure_manifest.json` records the figure inputs and outputs.

This is a manuscript source package, not the complete public benchmark release. The nine copied aggregate tables support rebuilding the figures; the saved games and executable engine-branch proofs remain in the repository locations identified by the evidence map. The draft explicitly states the outstanding public-release, external-reproduction and experimental limits.

All currency is game dollars except the explicitly marked OpenRouter cost in USD. All game-decision references are zero-based within the numbered game. No original game, engine, prompt, outline or literature-review artifact was changed, and no new game or training experiment was run for this draft.
