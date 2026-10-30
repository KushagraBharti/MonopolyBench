# MonopolyBench: Verifying Behavioral Claims from Agent Trajectories

[manuscript.pdf](manuscript.pdf) is the revised paper; [manuscript.tex](manuscript.tex) is its LaTeX entry point. This venue-neutral draft includes the complete paper and appendices. The earlier outline and literature review remain unchanged. It has not been submitted.

The revision centers on historical claims with declared endpoints: action provenance, reachable construction, current-debt payment, and delivered information. It includes a census of 663 END actions and a separate executable audit of all 60 eliminations and 66 construction-default decisions. Selected social cases test particular inferences; they do not estimate deception, persuasion, or latent intention. The results do not establish model rankings or a capability–alignment trend.

## Rebuild the paper

Tested with Python 3.14.7 and TeX Live 2026 (LuaLaTeX, latexmk and BibTeX). Fonts are TeX Gyre Pagella, TeX Gyre Heros and Latin Modern Mono. The LaTeX preamble lists the required packages. Install the pinned plotting/PDF-check dependencies in a virtual environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-manuscript.txt
python tools/build_exhibits.py
python tools/build_adversarial_tables.py
bash build.sh
python tools/verify_draft.py --portable
python tools/test_package_verifier.py
```

Build auxiliaries go to `build/`; the PDF is copied to the package root. The four vector figures and generated tables use retained datasets. `references.bib` is the print bibliography; `references_source.bib` preserves the source-verification notes. No web lookup or model account is needed after installing dependencies.

The portable verifier checks numerical invariants, row-level END classification, certificate summary consistency, all 80 game/configuration opportunity cells, table agreement, nested artifact consistency, citations, references, copyable commands, PDF geometry and build diagnostics. Its regression tests deliberately corrupt new data fields and require failure. These checks do not independently re-derive the original census or establish semantic validity. In the original repository, omit `--portable` to also compare the six protected-source hashes and nine retained tables against their originals.

## Execute the behavioral audit

Extract [artifacts/historical-claim-audit.zip](artifacts/historical-claim-audit.zip). In its `historical-claim-audit/` directory, install its separate `requirements.txt` in a fresh environment, then run:

```sh
python run_audit.py --output reproduced.json
python test_certificates.py
```

This small artifact contains the unchanged engine and board, all twenty original action streams, settings, per-event digests, a fixed case manifest, expected results and nine tests. It replays all 50,918 events and re-executes all 126 cases without a repository checkout. Population completeness and copied attempts were checked separately against the full canonical records; they are not re-extracted from this small bundle. Its first-payment witnesses do not establish maximal liquidation, future survival, or a changed winner. A reviewer found a bundled-sale counterexample to the initial generic atomic search. The revised checker refuses a negative graph certificate whenever building-sale actions are offered; the historical G7 mortgage-only certificate is unaffected. See the artifact README and paper appendix for scope.

`data/certificate_clean_environment.json` records a clean extracted run. Reviewers independently re-executed the fixed artifact and checked original source linkage. This is model-assisted verification within the project, not external scientific replication or human gold-standard annotation.

## Review and provenance

- [adversarial_review.md](adversarial_review.md) records accepted, narrowed and rejected findings across three review rounds.
- `adversarial_reviews/` preserves the nine specialist reports and their checked-versus-inherited limits. Earlier coauthor drafts and first-draft reviews remain under `coauthors/` and `final_review/`; they are historical and may contain subsequently corrected claims.
- [evidence_map.md](evidence_map.md) maps manuscript claims to retained analyses and new audits. [integration_log.md](integration_log.md) records writing and revision decisions.
- `verification.json` records final manuscript checks. `figure_manifest.json`, `package_manifest.json` and the artifact manifests identify the shipped inputs and outputs.
- `qa/verifier_regression.json` and `qa/final_render_review.md` record final regression and visual checks. `tools/package_draft.py` creates the revised ZIP and rejects missing required inputs; `tools/check_package.py` verifies its file hashes.

The engine and twenty saved games are public at <https://github.com/KushagraBharti/MonopolyBench>, inspected at commit `1133b6b839162ec4929dd80b1a6a2397e2422616`. Public path availability was checked, not semantic correctness of every released field. This revised manuscript, review package and executable audit are new local outputs; they have not been pushed to that public commit. Full source-dependent analyses require the saved-game repository paths recorded in the evidence map.

All money is game currency except explicitly marked OpenRouter USD. Decision indices are zero-based within each numbered game. Canonical games, engine, prompts, original outline and literature review were not changed. No paid model call, new cohort game, training experiment, commit or push was made for this revision. The verifier's synthetic regression is a test fixture, not an additional research game.
