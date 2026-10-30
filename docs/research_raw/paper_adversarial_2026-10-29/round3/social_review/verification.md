# Verification record

The frozen round-three manifest matches all 59 baseline files. The review reads the manuscript's main social section, extended social chronologies, abstract, methods, setup, claim protocol, discussion, limitations and conclusion, with surrounding main-text and appendix context. This is source review, not PDF rendering or a literature replication.

No prior peer report was consulted. `initial_position.md` predates the original-source case adjudication. All manually created files and scripts are in this review directory. No canonical paper, run, prompt, engine or artifact file was intentionally changed. No paid/model call or external continuation was made.

## Reproducible checks

Run from the repository root:

```sh
python docs/research_raw/paper_adversarial_2026-10-29/round3/social_review/audit_focal.py
python docs/research_raw/paper_adversarial_2026-10-29/round3/social_review/verify_focal.py
python docs/research_raw/paper_adversarial_2026-10-29/round3/social_review/check_g13_branch.py
python docs/research_raw/paper_adversarial_2026-10-29/round3/social_review/write_findings.py
```

The extractor reads original run paths from `docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json`. It extracts 90 fixed decision bundles across seven games, including surrounding negotiation and G18 follow-up. It reads JSONL files to locate those indices, but does not semantically classify the rest of the games. The bundles preserve full initial and resolved records, action rows, emitted events, and per-attempt prompt-file references.

The finite checks pass 40 assertions covering selected delivery, action-only refusal recovery, selected user-file agreement, conflicting received proposals and assistant END content, recipient correction, G4 cost retention and redemption timing, G11 correction order, G18 follow-up and liquidation order, and G20 disclosure and recognition. `focal_checks.json` records each assertion and, for exposure, its exact selected attempt and timeline indices.

The independent G13 witness replays 252 original actions through the repository engine and compares all 1,801 prefix events exactly, including full event dictionaries. At d252 it executes two validated actions: accept the existing $130 offer, then mortgage Ventnor at the resulting p4 management decision. No state mutation bypasses the validator. Cash reaches $295 during turn 107 before ending that turn or consuming another roll. The endpoint is financing capacity, not an observed rent payment. The branch output preserves the starting snapshot, legal decisions, witness actions, events and resulting snapshots. It also hashes every imported engine source file and its original inputs.

## Evidence and limits

`source_hashes.json` contains 625 original/frozen source hashes. `findings.json` repeats full hashes for the exact sources of each finding. `baseline_integrity.json` contains the 59 manifest comparisons. `focal_bundles.json` preserves 90 case bundles; extraction is not a claim that every sentence in every long provider explanation received a separate semantic label.

The final integrity pass rechecks the source hashes, branch inputs and every finding/case reference against the files on disk. `final_integrity.json` records zero source mismatches and matching reference hashes. This check concerns the frozen baseline, not subsequent edits to a live draft.

The paper's exact aggregate rates, all-twenty-game formatter census, seven-overlap disclosure count, 139 name conflicts, and literature comparisons were not independently rederived in this finite review. No counterfactual recipient model was invoked. No causal message effect, latent belief, general intent prevalence, model ranking or complete-paper assurance is claimed.

The G13 witness is an independent implementation for the selected prefix and two-step route. Its expected endpoint was known from the frozen manuscript before execution. That is independent execution and checking, not a blinded discovery. The source check does not adopt a prior reviewer's result as an independent derivation.
