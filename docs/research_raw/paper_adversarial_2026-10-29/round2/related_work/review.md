# Related-work revision review

The replacement is in `related_work.tex`. It concentrates on seven primary papers plus the pinned AgentMonopoly repository. It uses existing bibliography keys and no comparison table: binary feature cells would obscure the different meanings of replay, failure records and feasibility checks.

The defensible contribution is a bounded audit of a specified historical claim. The related work should credit existing economic records, failure accounting, state checks, matched configuration studies and counterfactual rerunning. It should then explain what the current certificate does and does not prove. The proposed final paragraph does this without asserting that the combination is unique.

## Corrections to the inherited novelty review

- **FN-06 needs correction.** AgentMonopoly's pinned code has failure diagnostics and configurable retries. FinBoardBench expressly records system-forced fallback events. Do not infer absence of attempt accounting from incomplete reporting, or describe all invalid AgentMonopoly outputs as silent. See RW-01 and RW-02 in `findings.json`.
- **FN-04 needs a scoped formulation.** Session playback is the documented AgentMonopoly use of replay. Inspection of the named runner/server does not establish that no uninspected implementation or future release can re-execute actions. NegotiationArena already explicitly supports modified-game reruns. See RW-03.
- **FN-13 overclaims.** Complete economic events do not decide every economic proposition, recipient belief, intent, future agreement or counterfactual outcome. A feasibility verdict needs a specified endpoint and intervention class. Failed nonexhaustive search remains unresolved. The replacement follows the new claim protocol.
- **The proposed novelty sentence overclaims prefix validation.** The manuscript describes verified populations and audited prefixes. It does not validate every possible historical prefix. The replacement does not promote an architectural capability into universal evidence.
- **Arena deserves its full method credit.** Its single-author reference labels are one component, not its whole validation. The replacement includes state checks, reasoning audit, component audits and cross-judge replication.
- **DECE is a close intervention comparator.** Its matched configuration design belongs beside the local-action intervention distinction. Its title discrepancy is bibliographic, not substantive; retain the existing metadata-based citation.

## Release statement audit

The repository is public and its GitHub license metadata reports Apache-2.0. At remote commit [`1133b6b839162ec4929dd80b1a6a2397e2422616`](https://github.com/KushagraBharti/MonopolyBench/tree/1133b6b839162ec4929dd80b1a6a2397e2422616), the remote `saved_games` tree SHA exactly matches the local immutable Git tree. Both research cohort trees also match. Enumeration of those commit objects finds all twenty games, each with `events.jsonl`, `actions.jsonl`, `decisions.jsonl`, prompt files and state snapshots. Details are in `sources/release_audit.json`.

The inherited statement that there are 703 snapshots and 2,780 prompt files **per game** is incorrect: those are G1's counts. Counts vary across games. The two research cohort trees contain 118,653 tracked files in total; that figure also includes cohort-level material.

The new manuscript and adversarial-review/certificate directories are not tracked at that remote commit. The release audit therefore supports public engine and saved-game availability, not public availability or completeness of this revision's certificate suite. It does not certify every saved artifact's semantic validity or licensing independently. No public-release comparison with AgentMonopoly, DECE or FinBoardBench is used as a novelty argument.

Suggested introduction sentence, if a named repository is appropriate:

> The engine and the twenty saved games are publicly available in the MonopolyBench repository at commit 1133b6b; this revision adds the separately supplied certificate suite.

The current introduction's first clause is supportable. The second clause needs the suite actually supplied with the submission. Its external-test claim must be backed by the suite author's retained test evidence; I did not rerun it. `validation.tex` still describes a completed release and external test as outstanding, so the parent editor should reconcile that wording with the current claim protocol and the actual package delivered.

## Verification and limits

I independently opened the versioned primary sources, fetched their bytes, inspected the named sections and pinned code, and audited the public commit. This pass adds no experiments or model calls and does not rerun gameplay, replay, certificates or behavioral counts. Local manuscript descriptions of MonopolyBench's new certificate results are treated as author-provided evidence, not independently reproduced results.

The `sources/` directory preserves fetched bytes and a retrieval manifest. `source_hashes.json` records their SHA-256 digests and hashes of the local inputs read. `checks.json` reports the word count, bibliography-key check, TeX delimiter check and source-hash verification. Only this assigned directory was written.
