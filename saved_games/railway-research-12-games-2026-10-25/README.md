# Twelve completed Railway research games

All 12 games are saved side by side in this folder. Games 01 to 04 are the first campaign; games 05 to 12 are the second. Existing exploratory saved games were left untouched. No games, purchases, deployments, or paid model requests were started for this download and audit. Two final campaign export snapshots were prepared on the server.

Each game folder preserves the server package unchanged, including `run/`, `quality_check/`, `analysis/`, `cloud/`, the saved-game manifest and the storage manifest. The original per-game ZIPs and both final campaign ZIPs are in `archives/`. Campaign metadata, freeze manifests, preflights and server receipts are in `campaigns/`. Its `original-campaign-storage-manifest.json` describes the original ZIP layout, before the games were moved side by side here. The original campaign ZIP remains complete and verified.

`game-index.csv` maps all 12 local folders to their run IDs, job IDs, source SHAs and archive hashes. `audit/download-index.json` records download provenance and manifest hashes. `audit/verification.json` contains the per-game inspection, and `audit/<run_id>/independent-replay.json` contains newly computed replay results. Canonical game files were not regenerated or overwritten.

## Integrity results

- 12 of 12 original game ZIPs and 2 of 2 final campaign ZIPs passed full member-size and SHA-256 verification against their manifests. All extracted game inventories also passed.
- 12 of 12 games passed newly computed state and artifact replay using saved settings and applied actions. The strict completed-run validator passed for every game, including artifact hashes, terminal snapshot, summary and terminal event agreement.
- Every game ended by BANKRUPTCY with no turn cap, medium effort, complete analysis and quality-check outputs. Event sequences were unique and contiguous. Resolved decisions and applied actions matched in identity, order and payload.
- All successful physical calls returned the requested model and permitted provider. The archived calls retain intent, response, billing metadata and transport-failure evidence. Recorded costs reconcile with the live job totals.
- Campaign freeze/config hashes and embedded seed-draw, analysis-contract and run-matrix hashes passed. All three independent seed blocks have the complete cyclic four-seat rotation. There are no technical reruns, recorded pauses, repairs or recovered jobs in these 12.
- An exact-value scan of extracted files found no configured production password, API-key or export-token values. This is not a complete public-release privacy review.

## Research caveats

These are 12 games across three independent seed blocks, with four correlated seat rotations per seed. They are not 12 independent seeds. Keep the old exploratory corpus separate. The first four use source 42f85183 and the next eight use d6808534; the original source, image and treatment identities remain recorded. Independent replay passed against the local engine.

There are 24 recorded deterministic engine-default actions after exhausted invalid-output recovery. These are part of the configured execution policy, not clean model answers. Preserve and disclose their per-game and per-model rates. Claude refusal recovery also occurred; records distinguish standard requests from same-model requests without a private-thought requirement. Configured Opus 4.8 fallback does not imply it was used. No physical Opus 4.8 calls appear in this collection.

Cost metadata contains 859 missing-cost calls and 3 unknown-cost calls. The recorded known subtotal is $82.684898, including $44.893302 in reported OpenRouter charges and $37.791596 in reported upstream provider charges. This is not a complete final invoice and does not independently establish any OpenAI free-token discount. Missing or unknown charges remain missing or unknown, never zero.

Six physical xAI/Grok calls failed and were retried: three total timeouts and three invalid-JSON responses. No recorded HTTP 429 or 5xx responses appear in these 12 game call ledgers. No game ended prematurely from those failures. The original transport evidence remains in each cloud ledger and call directory. These observations, model refusals, invalid actions and recovery rates should remain visible in paper analyses rather than selectively excluding affected games.

## Game ledger

| Game | Seed | Turns | Winner | Defaults | Replay |
| --- | --- | --- | --- | --- | --- |
| 1 | 751774554 | 216 | google/gemini-4-argon | 0 | Passed |
| 2 | 751774554 | 102 | google/gemini-4-argon | 5 | Passed |
| 3 | 751774554 | 283 | google/gemini-4-argon | 0 | Passed |
| 4 | 751774554 | 166 | x-ai/grok-4.7 | 2 | Passed |
| 5 | 2506298840 | 170 | openai/gpt-6.1-sol | 16 | Passed |
| 6 | 2506298840 | 126 | openai/gpt-6.1-sol | 0 | Passed |
| 7 | 2506298840 | 150 | openai/gpt-6.1-sol | 1 | Passed |
| 8 | 2506298840 | 139 | openai/gpt-6.1-sol | 0 | Passed |
| 9 | 2573692901 | 88 | openai/gpt-6.1-sol | 0 | Passed |
| 10 | 2573692901 | 75 | google/gemini-4-argon | 0 | Passed |
| 11 | 2573692901 | 145 | x-ai/grok-4.7 | 0 | Passed |
| 12 | 2573692901 | 166 | anthropic/claude-opus-5.5 | 0 | Passed |

## Scope of this review

This review verifies preservation, completion, deterministic replay, routing, accounting reconciliation and the recorded study design. It does not certify scientific conclusions or replace qualitative social coding and manuscript review. The downloads stay local; nothing was committed or pushed. Use the game packages and their recorded source identities for further analysis.
