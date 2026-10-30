# MonopolyBench: Auditing Strategic Execution and Interaction in Multi-Agent Games

[manuscript.pdf](manuscript.pdf) is the revised paper; [manuscript.tex](manuscript.tex) is its LaTeX entry point. This venue-neutral draft includes the complete paper and appendices. The earlier outline and literature review remain unchanged. It has not been submitted.

The revision addresses the eight research questions and three broader questions in the saved guidance through explicit measurable targets. It adds a complete census of 920 negotiation responses, separate transfer networks, a temporal reading of all 240 fixed-sample public/private records, construction-error recurrence, and a new reference-policy readiness study. The previous census of 663 END actions, executable audit of all 60 eliminations and 66 defaults, and eight contextual transcript incidents remain.

[question_status.md](question_status.md) states the answer and unresolved part of every question. The paper does not claim to have measured causal learning, unfamiliar-opponent transfer, optimal policy, or the relationship between general and multi-agent capability. New controlled model studies remain unexecuted; their design requirements are in the appendix.

**Current scope:** the user has ruled out new controlled evaluations, including additional unpaid pilot games. The spending-cap question is withdrawn. Further work uses existing saved games and completed artifacts. The unexecuted designs are hypothetical limitations discussion, not scheduled work or a condition for finishing this paper.

## Rebuild the paper

Tested with Python 3.14.7 and TeX Live 2026 (LuaLaTeX, latexmk and BibTeX). Fonts are TeX Gyre Pagella, TeX Gyre Heros and Latin Modern Mono. The LaTeX preamble lists the required packages. Install the pinned plotting/PDF-check dependencies in a virtual environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-manuscript.txt
python tools/build_exhibits.py
python tools/build_adversarial_tables.py
python tools/build_transcript_cards.py
python tools/build_agenda_exhibits.py
bash build.sh
python tools/verify_draft.py --portable
python tools/test_package_verifier.py
python tools/verify_agenda.py
python tools/test_agenda_verifier.py
```

Build auxiliaries go to `build/`; the PDF is copied to the package root. The four vector figures and generated tables use retained datasets. `references.bib` is the print bibliography; `references_source.bib` preserves the source-verification notes. No web lookup or model account is needed after installing dependencies.

The portable verifier checks numerical invariants, row-level END classification, certificate summary consistency, all 80 game/configuration opportunity cells, table agreement, nested artifact consistency, citations, references, copyable commands, PDF geometry and build diagnostics. Its regression tests deliberately corrupt new data fields and require failure. These checks do not independently re-derive the original census or establish semantic validity. In the original repository, omit `--portable` to also compare the six protected-source hashes and nine retained tables against their originals.

## Contextual transcript exhibits

Five main-text cases present concealment, withdrawal under financial distress, a cash-denial appeal, a misleading building claim, and a bargaining-limit bluff. Three appendix cases separate consequential execution or disclosure failures from evidence of malicious intent. Each has a setup, labelled verbatim cards, actual outcome, and interpretation. They are selected examples, not a severity ranking or a deception-rate estimate.

The 28 native LaTeX cards use 30 exact spans retained in `data/transcript_manifest.json`, alongside complete decoded source fields, character offsets, source-file/field hashes, JSON pointers, line numbers, response conditions and review provenance. `tools/build_transcript_cards.py` regenerates the cards. The verifier checks source spans, typeset text and their presence in the PDF; the repository mode also reloads the original saved-game fields. The source reviews and final integration review are preserved under `adversarial_reviews/transcripts/`. The pre-transcript manuscript and source package are archived separately in the original repository's `paper_transcripts_2026-10-29/baseline/` directory.

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

## Research-agenda extension

The complete source-dependent extension is archived in artifacts/research-agenda-audit.zip. It contains protocols, scripts, retained ledgers, twenty baseline-only pilot runs, two repeat runs, original-source linkage, reviewer checks and preserved semantic disagreements. Unlike the historical certificate ZIP, these scripts require the repository and its Python environment; the archive does not claim to be a standalone engine distribution. The paper's retained data and figure regeneration remain portable.

All 20 baseline pilot action streams replay exactly: 19,494 applied decisions and 179,816 events. Nineteen games are censored at 1,000 decisions, and no censored winner is invented. These are **new reference-policy games**, separate from the 20 historical LLM games. Eleven of 130 supplied reference actions fail engine legality checks. The follow-up static-state screen is exploratory; passing it does not validate strategic optimality.

Fresh specialist reviews independently checked the new negotiation census, temporal endpoints, and recurrence/pilot results. They identified semantic coding disagreements, same-turn recurrence concentration, unsuccessful corrections, and temporal opportunity errors, all retained with their dispositions. These are model-assisted checks within the project, not external or human replication. The second negotiation coder's accidental initial exposure is disclosed.

The agenda verifier joins all offers and threads, recomputes typed transfers and recurrence from retained rows, and checks sampled field hashes and pilot/scenario totals. Nine deliberately corrupted fields must be rejected. These are consistency checks, separate from the original-source reviews and engine executions.

All money is game currency except explicitly marked OpenRouter USD. Decision indices are zero-based within each numbered game. Canonical games, engine, prompts, original outline and literature review were not changed. No paid model call, new LLM cohort game, training experiment, commit or push was made for this revision. The offline pilot and its two exact repeats are explicitly separated from both the historical cohort and synthetic regression tests.
