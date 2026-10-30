# Independent execution record

All commands ran on 29 October 2026. Work stayed in `round3/package_review/`; source histories and original engine files were read only. No new games or model/provider calls were used.

## Baseline and manuscript build

- The frozen manifest contains 59 files; every SHA-256 matched. See `baseline_integrity.json` and `baseline_integrity_final.json`.
- Copied the entire frozen directory to `build_copy/`, including `.latexmkrc`.
- Ran `bash build.sh` in the copy using TeX Live 2026 LuaLaTeX, latexmk and BibTeX. Exit status 0, 36 pages. Full log: `build.log` and `build_copy/build/manuscript.log`.
- Original PDF SHA-256: `ae3f786298ef597a69dddbd6c7c788ce746776ca230e685a44ce5e89ddc8cad1`.
- Recompiled PDF SHA-256: `27a939e224187fff59d11b5b1baa69ef4fa05b654fff7fdda45b21f49dfbedf2`.
- Every extracted page text and raster image matches the original. Byte equality is not claimed. See `render_comparison.json`.
- Poppler executables were unavailable. PyMuPDF 2.0 rendered all pages at 1.4 scale; defect crops use 2.3 scale and the cohort table close-up uses 3 scale. All 36 pages were visually opened, not merely text-extracted. See `rendered_review.md`.

The review environment used Python 3.14.7. `review_environment.json` records the installed Python packages. A separate environment installed only the five exact dependencies listed by the certificate bundle. After all checks, the temporary virtual environments and download cache were removed. Logs, output JSON, the mutation package and all rendered evidence remain. Recreate the environments from the recorded dependencies to rerun the checks.

## Manuscript portable verification

The exact initial command was:

```sh
python build_copy/tools/verify_draft.py --portable
```

It failed because the frozen snapshot does not contain `protected_sources.json`; the verifier opens that file even in portable mode. Full failure: `portable_verifier_initial.log`.

The coordinator then explicitly requested restoration of the unchanged protected manifest from `docs/research_raw/paper_draft_2026-10-29/protected_sources.json` into the isolated copy. The file SHA-256 is `c829d57ab500fd753b926cc73769abc7d2c1bf3d9cb65c38dd7cc3b78e356148`. See `restored_file_provenance.json`. No baseline file changed.

The same command then passed with 36 pages, 18 citations and six protected-source entries. Portable mode does not validate those six external sources. It also reported no page-boundary spans, launch links or the checked LaTeX warnings. Full output: `portable_verifier_restored.log`; detailed report: `build_copy/verification.json`.

That pass misses the three broken references, collapsed commands, overlapping Figure 4 notes and unchecked new datasets. An isolated corruption probe demonstrates the latter. Changing three new data values to `999999` still produces a pass. See `verifier_mutation_probe.json`; the mutation does not affect the baseline, rendered evidence or independent checks.

## Independent table and input checks

Ran `python audit_package.py` using the review environment. Exit status 0. The script derives counts from original decision histories, reads positioned text from the independently compiled PDF, reaggregates retained records, and writes `independent_checks.json`. The full concise execution output is `independent_checks.log`.

It checks every numerical row of Tables 1, 3, 4, 5, 6, 8 and 12. It reproduces 6,989 decisions and 8,679 attempts directly from original histories; all 80 original file hashes match the supplied provenance. It reconstructs the 663-record END partition and matches all 66 default identities to the histories. All 20 per-game rows and all 80 opportunity cells agree. There are 26 zero-group cells and 40 zero-entry cells. The seven figure inputs and eight generated-image hashes match their manifest.

All other native tables were visually inspected and compared with source prose and scope. The review did not re-adjudicate every social proposition. Eighteen bibliography entries render. A separate link scan found 65 internal links with valid page destinations and 27 external link annotations. See `link_audit.json`.

## Standalone certificate bundle

Safely extracted `build_copy/artifacts/historical-claim-audit.zip` into `certificate_extracted/`, after checking for absolute or parent-traversal entry paths. ZIP inventory: `certificate_zip_inventory.txt`. The original ZIP SHA-256 is `bd0de225dc6e0ecb215326504d11afa51bb5ed8164da87b63c9fcc3072cc74f6`.

Created a fresh Python 3.14.7 environment and installed exactly:

```text
pydantic==2.12.5
pydantic_core==2.41.5
annotated-types==0.7.0
typing_extensions==4.15.0
typing-inspection==0.4.2
```

From the extracted artifact directory, ran:

```sh
python run_audit.py --output ../../reproduced_certificates.json
python test_certificates.py
```

Both commands exited 0. The first invocation used an interpreter path containing `../..`, which caused two Python prefix warnings but did not affect execution. The nine-test command used the normalized absolute interpreter path and passed without those warnings. Full logs: `certificate_audit.log`, `certificate_tests.log`.

The audit replays 20 games and 50,918 events, checks 126 prefixes, and produces the following finite-corpus classifications:

| Population | Reproduced result |
|---|---:|
| Elimination bound impossibility | 56 |
| Legal current-debt payment witness | 3 |
| Restricted exhaustive financing impossibility | 1 |
| Default decisions | 66 |
| Default decisions with a reachable recorded target | 63 |
| Default decisions permitting some legal construction | 66 |
| Reachable well-formed attempted targets | 63 |
| Well-formed attempted targets exceeding current cash | 7 |
| Malformed attempted target | 1 |
| Attempts without a parseable target | 61 |

`reproduced_certificates.json` is structurally identical to both the bundle's `results.json` and the manuscript's `data/certificate_results.json`. All 80 artifact hashes and all 72 input hashes match. All eight copied engine/board source files match their original paths and recorded digests; the license matches. This is a new execution of the retained package. It is not a new derivation of the earlier semantic findings or external scientific replication.

## Frozen packager check

Ran `python tools/package_draft.py` in `build_copy/`. It exits 0 and creates a 60-entry ZIP, but omits the nested certificate ZIP because the frozen script does not enumerate `artifacts/`. Named missing files are silently dropped. The snapshot also omits the live README, so that generated test ZIP has no README. See `frozen_packager.log` and `frozen_packager_inventory.json`. The coordinator is updating the live packager and README; this test is not a verdict on that later archive.

Before release, verify the exact final archive manifest, extract it afresh, build and run its portable verifier, then execute the included nested certificate package. Re-render and inspect the pages affected by the reference, command and figure changes.
