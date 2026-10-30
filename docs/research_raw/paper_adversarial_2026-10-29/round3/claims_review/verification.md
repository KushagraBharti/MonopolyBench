# Verification record

Scope: claims and empirical sufficiency of the immutable round-3 baseline. All retained reviewer outputs are under `round3/claims_review/`. No new model calls, paid experiments, canonical edits, engine edits, prompt edits, or manuscript edits occurred.

## Order and independence

1. Read repository instructions and the PDF and Unslop skills.
2. Read `manuscript.tex`, every included section, every input table, and both economic/social appendices from `round3/baseline/`.
3. Wrote `initial_position.md` before opening prior reviews or inspecting the artifact implementation. The task itself disclosed the earlier atomic-search flaw and the new guard; this was known in advance.
4. Verified all 59 entries in `baseline_manifest.json`. No mismatch. See `baseline_integrity.json`.
5. Extracted the frozen ZIP into `claims_review/extracted/`, read the README, runner, freezer, and tests, and installed the pinned dependencies in a reviewer-local Python 3.14.7 environment. Added PDF libraries for reading the manuscript. Dependency download used the network; no scientific data were fetched and no model service was used.
6. Executed the current runner and tests. Consulted the earlier review reports only after step 3. The parent later raised the financing-figure question; I confirmed it against code, data, the figure image and PDF text.
7. Wrote and ran a separate source/count/event check using canonical local records. This script does not import the freezer or runner.

## Executed checks

The following commands are relative to the repository unless a working directory is shown. The virtual environment was installed inside this review directory. It can be recreated from the bundled requirements.

```sh
# cwd: round3/claims_review/extracted/historical-claim-audit
../../.venv/bin/python run_audit.py --output ../../reproduced.json
../../.venv/bin/python test_certificates.py

# cwd: repository root
python3 docs/research_raw/paper_adversarial_2026-10-29/round3/claims_review/check_claim_counts.py
```

The runner matches all 50,918 canonical events, twenty terminal histories and 126 selected prefixes. `reproduced.json` equals the bundle's `results.json` as a complete parsed JSON object. Results are 56 upper-bound impossibility certificates, three payment witnesses and one mortgage-only negative graph. For default attempts, there are 63 reachable targets, seven cash-deficient targets, one malformed target and 61 missing parseable targets. Sixty-three of 66 decisions contain a reachable recorded target, and all 66 allow some construction. All nine supplied tests pass, including the regression that refuses the bundled-sale counterexample.

The final archived test rerun pins `TMPDIR` to `claims_review/tmp`; its output is `test_certificates.log`. The first test execution used the system temporary directory for one self-cleaning test fixture. It left no retained files there. The dependency environment and download cache were removed after verification to avoid bundling hundreds of megabytes of generated packages with this review.

`check_claim_counts.py` independently reads the original cohort files referenced in `games.json`. It verifies 80 source-file hashes and 252 source start/resolution line hashes, reconstructs the bankruptcy/default population, and compares all 132 extracted attempt fields and plans. It also reduces the freshly emitted construction events and debits for each of the 63 successful target witnesses and compares them with the target counts and costs. All final checks pass. The output is `claim_count_checks.json`.

The script additionally reports finite descriptive concentration: defaults occur in seven games, 55/66 are in G5 and G13, and 61/66 belong to Opus. Seventy well-formed attempted targets have 19 distinct deed/kind/count multisets. These are not 19 independent mechanisms, and no inference is made from that diagnostic.

The financing generator plots `accessible` for all sixty rows and labels the axis accordingly; 59 rows set `accessible` equal to `full`. The current certificate runner does not maximize those estates. The figure and its scope concern are reported in CR-01. The older maximum-finance computation was not independently rerun in this review.

## PDF and manuscript inspection

The frozen PDF has 36 pages. Pypdf extracted every page into `manuscript_extracted.txt`. The manuscript was read in full through its LaTeX sources, including all input tables and appendices; PDF text confirmed the title, abstract, relevant numerical passages and the financing axis on page 12. The original `assets/financing.png` was visually inspected. This was a claims review, not a full rendered-page typography audit.

The frozen PDF SHA-256 is `ae3f786298ef597a69dddbd6c7c788ce746776ca230e685a44ce5e89ddc8cad1`. The baseline manifest has 59 entries and matched before and after review.

## Earlier reports consulted after the initial position

- Round 1 `opus_contribution/review.md`, including the central-contribution and full-denominator arguments. The first combined tool output was truncated, so this is not claimed as a full close reading of every paragraph.
- Round 1 `fable_novelty/review.md`.
- Round 2 `certificates/review.md`, with the generic atomic-search counterexample and its bounded fix.
- Round 2 `related_work/review.md`, including corrections to inherited novelty claims.
- Round 2 `resolution/review.md`, including parser and recipient-delivery limits.

Their results informed the unresolved-issue comparison. They are not counted as this reviewer's independent verification. I did not inspect the other concurrent round-3 review findings.

## Reviewer implementation errors and corrections

The first runner command used one extra `..` in its virtual-environment path and failed before execution. The corrected command succeeded. The relative interpreter path emitted a harmless Python prefix warning; the later absolute-path test command ran without it.

An initial version of my construction-event check assumed explicit key fields in `board.json`, yielding null names and false mismatches. The board stores names, and the engine derives normalized keys from them. I corrected my checker to normalize the saved names and reran it; all 63 comparisons passed. This was a reviewer-script error, not an artifact discrepancy. The final script and final results are retained.

## Limits

This review re-executed the frozen portable inputs in a fresh local virtual environment. It was not an external-team replication or a new container isolation exercise. Code inspection confirms that the runner reads its vendored engine, packaged board, and local inputs. The original-record check necessarily used the repository's saved games.

I did not independently repeat the full economic event reductions, all 6,989 delivered-memory reconstructions, all social chronology checks, the public-release audit, or the primary-literature audit. I did not test every possible supported graph, validate a generic solver, run new agent continuations, or measure annotation accuracy, attention, latent belief, or causal persuasion. The prior search flaw is assessed against the guard now present, not against the superseded implementation.

The repository's application verification suite was not run because this task changes no application or benchmark behavior. The artifact execution, nine tests, canonical-source checks and baseline-integrity checks cover the reviewed claim surface. Final JSON syntax and existence checks were performed for the deliverables.
