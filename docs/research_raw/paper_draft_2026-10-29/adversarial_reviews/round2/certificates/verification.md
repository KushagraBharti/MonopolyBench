# Verification record

The original artifact, rather than an earlier review, supplied the starting inputs. `initial_position.md` records the prior position. `artifact_initial_hashes.json` records the initial file hashes. The original archive and extracted package are retained in `reviewed_source/` and `portable_original/` so the failure remains reproducible after the coordinator's correction.

The reviewer used Python 3.14.7 at `/Users/kushagra/.local/bin/python3`. The replay and tests did not need third-party packages in this interpreter. I did not install dependencies, call providers, or access the network. An initial nested-directory run selected an older system Python and failed on `dataclass(slots=True)`, outside the declared Python >=3.10 requirement. Repeating that run with the explicit 3.14 executable succeeded.

Commands below run from the repository root unless stated otherwise.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/research_raw/paper_adversarial_2026-10-29/executable_audit/run_audit.py --output docs/research_raw/paper_adversarial_2026-10-29/round2/certificates/fresh_results.json
PYTHONDONTWRITEBYTECODE=1 python3 docs/research_raw/paper_adversarial_2026-10-29/round2/certificates/adversarial_checks.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/research_raw/paper_adversarial_2026-10-29/round2/certificates/extra_checks.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/research_raw/paper_adversarial_2026-10-29/round2/certificates/recheck_fix.py
```

The first command ran before the coordinator's correction. Its output is preserved as `fresh_results.json` and `fresh_run.log`. For exact original replay now, run the same `run_audit.py` from `portable_original/historical-claim-audit/` with output in this review directory. That extraction produced `portable_results.json`, exactly equal to the original fresh output. The later `recheck_fix.py` deliberately loads the revised live runner and records its hash.

| Check | Result | Evidence |
| --- | --- | --- |
| Full original replay | 20 games, 50,918 events, every original event digest matched | `fresh_run.log`, `fresh_results.json` |
| Original ZIP replay | Complete output equal to original fresh run | `portable_run.log`, `portable_results.json` |
| Canonical file linkage | 80 source files and 8 engine/board sources match; unchanged at review end | `original_hashes.json`, `original_final_hashes.json` |
| Population and prefixes | 126 unique cases, 60 eliminations, 66 defaults; source-line hashes, actors, decisions, prefix hashes verified | `adversarial_results.json` |
| Construction preservation | All 63 executed target attempts preserve deed/kind counts in plan and emitted events; cash debit agrees | `adversarial_results.json` |
| Submitted target validity | All 70 well-formed submitted encodings fail | `verification_facts.json` |
| Payment witnesses | All three paths re-executed, exact events reproduced, original debt amount/reason paid | `adversarial_results.json` |
| Bound successors | 139 historical atomic successors, 42 sales and 97 mortgages; resource potential never increases | `extra_results.json` |
| Deduplication | 10 nonterminal paths collapse to 7 states with equal pending debt and menus | `extra_results.json` |
| Bundled original tests | 8 passed before the new failure was identified | `bundled_tests.log` |
| False certificate repro | Six-state atomic graph certifies impossibility; legal bundled sale pays actual Illinois rent 750 | `adversarial_results.json` |
| Historical G7 action scope | Bundled sale rejects because its action name is unoffered; one-state mortgage graph remains complete | `adversarial_results.json` |
| Guard correction | False certificate refused; bundled witness still pays; all historical results and replay digests preserved | `fix_recheck.json` |

`coordinator_changes_during_review.json` records live artifact changes seen after the original freeze. These are distinct from reviewer writes. The reviewed original remains available in the preserved ZIP. No canonical originals or engine source files changed according to the 88-file before/after comparison.

This was an artifact audit. It did not modify product behavior, so the repository-wide API/frontend verification suite was not run. The checks above directly exercise the replay, source, certificate, and construction claims under review. No broader paper claims or semantic provider transcripts were reviewed.
