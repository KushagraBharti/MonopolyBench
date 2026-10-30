# Overlapping economic and social extraction

## User-approved scope update

After Sonnet's provider rejected the full-channel request, the user selected a narrower second review. Sonnet now reviews actions, public chat, legal options and financial records in `public_review/`; its fresh outputs belong in `reviewers/sonnet_public/`. Terra continues the full-channel review described below. Their overlap covers observable conduct and economics. Private/provider-channel findings do not have two-extractor coverage. The earlier partial Sonnet outputs remain preserved as historical work and are not silently counted as a completed full-corpus review.

The user authorized steps 9–10 only. Terra xhigh and Sonnet xhigh are the first-pass drivers. Each independently examines ALL 20 games and all 6,989 decisions, including every action, public message, recorded private thought and available readable provider reasoning trace from every attempt. The seven batches organize files and saved progress; they are not separate stopping points. Continue through the full corpus before the final handoff. Astra, Sol, Opus and Fable then examine the combined shortlist, disputes and counterexamples together. Do not begin later paper phases.

## Coverage and reading

One review point is an applied decision and all its recorded attempts, actual observations, legal options, applied action, related events, public message, private note and readable provider text or summaries. Read chronological game context. All 20 games and all 6,989 decisions belong to the plan; rankings never determine which records are read.

Use the batch manifest to find each original packet and line. Packet files can be large. Read bounded portions without dropping text after an arbitrary character limit. Read all distinct available text, preserving differences between draft content, tool arguments, selected versus rejected attempts, public versus private text and provider summaries. Exact duplicate representations need not be read twice if the equality and original field references are retained. Opaque encrypted data is unavailable, not readable reasoning. System instructions, rule/configuration files and original tool schemas remain available from the source run and must be inspected when needed to interpret a choice.

Prefer primary event/action/decision records to previously written research interpretations. Do not read the other extractor's labels before saving your initial judgments. The earlier core-team analyses are not a list of cases to rediscover. Search for additional patterns, normal play and counterexamples. Do not infer behavior solely from regex hits, source parsing or model names.

The codebook is `../paper_phase1_2026-10-28/astra/behavior_review_contract.json`. It is provisional and this corpus is exploratory. Candidate labels may be added with a definition and examples. No fixed number of interesting cases is required. Keep both successful and failed strategies, fulfilled and broken assurances, ordinary competition and non-trade routes.

## Output files

Write only within your assigned `reviewers/<model>/<batch>/` directory. Preserve partial work incrementally. Every output names the actual reviewer model and effort.

`coverage.jsonl` has one row for each genuinely reviewed decision, with:

- `decision_id`, `game`, `reviewer`, `status`;
- `attempts_reviewed`, containing all reviewed zero-based attempt indexes;
- `channels`, mapping `observation_and_menu`, `applied_action`, `events`, `public`, `private`, `provider` to `reviewed`, `unavailable`, or `partial`;
- `note`, a concise neutral observation or interpretation for this decision;
- `candidate_ids`, possibly empty, and `source_packet`/`source_packet_line`.

`candidates.jsonl` contains episode-level candidates rather than duplicates for every related decision. Each row has:

- `case_id`, `game`, `decision_ids`, relevant `event_ids`, `attempt_refs`, participants and roles;
- `title`, `categories`, and a concrete account of what happened;
- source-attributed quote spans and numerical economic evidence;
- observed action, public claim, private note, provider text, and the origin/availability of each;
- earlier exposure and focal-decision availability when influence or reliance is claimed;
- subsequent consequences with an explicit follow-up endpoint;
- supporting evidence, contradictions, alternative explanations, unresolved questions;
- `priority` from 1 to 5 and `priority_reason`, plus confidence in the proposed interpretation.

Priority describes research value, not how sensational the case sounds. Rank repeated consequential mechanisms, clear financial consequences, well-supported interactions, cross-model contrasts, informative failures and counterexamples highly. The core team needs the strongest examples and the cases that could undermine them.

`shortlist.md` ranks the most informative episodes, links every candidate to sources, and identifies disagreements that need core-team judgment. Preserve a complete candidate list; do not delete lower-ranked cases to meet a quota. `game_narratives.md` explains each game and each player's strategy, turning points and outcome. `progress.json` records expected, reviewed, partial and remaining IDs plus remaining work. A partial batch is useful; do not label unread records reviewed to claim completion.

## Interpretation

Keep actual actions authoritative. Contradictory channels do not identify which component caused them or what the model truly intended. Public statements are not necessarily delivered to another player. Earlier delivery can matter after a statement disappears from the latest prompt. Distinguish observable false content, knowledge, forecasts, misleading implications, assurances, actual breaches and intent.

Count original trade initiators, final-offer authors and acceptors separately. Track both parties' cash/assets, mortgage interest, completed groups, retained liquidity and subsequent development/rents. Include non-trade routes, jail/access choices, auctions, financing, failure and successful restraint. A legal build is not automatically optimal. Bankruptcy creditors are fixed by debt; listed financing choices do not establish enough liquidity. Treat arithmetic bounds as screens until a legal sequence is established.

Report candidate counts as candidate counts. Decisions within games and seed blocks are dependent. Missing private/provider evidence is not a negative label. Filtered lists and agreement between LLM reviewers are not human-validated prevalence estimates.

## Core-team handoff

After both reviewers' independent outputs are saved, combine the union of their candidates, keep each judgment separately, link overlapping episodes and expose disagreements. The four core researchers review the shortlist and selected unflagged records to check missed cases. Their adjudication must retain the evidence and the reason for any changed label. Phase 2 ends with validated economic tables, supported behavioral findings, representative cases, counterexamples and an explicit coverage report. Stop there for the user's next checkpoint.
