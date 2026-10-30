# Full-corpus behavioral review

The user authorized parallel extraction on 2026-10-29 UTC. This replaces the earlier requirement that one Terra thread read all twenty games serially. The required coverage is unchanged: every decision, applied action, public utterance, recorded private note and available readable provider text, including every attempt. Encrypted or unreturned material is unavailable.

The existing Terra xhigh session and two additional Astra xhigh reviewers cover disjoint complete-game ranges. Two rounds of new Terra delegates ended prematurely; their partial artifacts remain preserved and do not count as completed games. The additional reviewers inherit the main session's model. Claude Code's public-scope continuation is managed by the user and supplies a separate overlapping review; it does not replace full-channel coverage.

| Reviewer | Games | Decisions | Output ownership |
| --- | --- | ---: | --- |
| Existing Terra thread | 1–6 | 2,259 | `reviewers/terra/` |
| Additional Astra reviewer B | 7–13 | 2,074 | `reviewers/astra_parallel_b/` |
| Additional Astra reviewer C | 14–20 | 2,656 | `reviewers/astra_parallel_c/` |

These are assignments, not completed coverage. There are 6,989 required decisions in total. The existing seven packet batches are file organization only and do not restrict game assignments.

## Reading and recording

Use `../paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl` to select exact assigned decisions and locate their source packets. `review_page.py` can page a record without truncating it. Review all unique available content; exact duplicate representations may be referenced once with their source paths retained. Reading tools and parsing do not count as semantic review.

Record one concise coverage row per actually read decision, with source references and channel/attempt coverage. Ordinary decisions need no long written commentary. Keep substantive prose for consequential cases, informative counterexamples, and each player's game trajectory. Candidate ranking must not determine what is read.

Write a game note for each completed game in the assigned output directory, naming the actual reviewer and exact decision/event references. Use a local index for the assigned range. `RESEARCH_NOTES.md` is the single central entry point; the main Astra session maintains it to avoid concurrent writers. Preserve initial judgments and later corrections separately. These additional extraction reviewers do not replace the four core coauthors' joint adjudication.

Do not send routine per-decision or per-chunk messages to the main thread. Save checkpoints to files and continue to the next record and game. A checkpoint is not a stopping point. Use durable notes and context compaction for continuity. Final completion requires every assigned record, all game narratives, a ranked shortlist and an honest coverage audit. Only an actual enforced blocker justifies an incomplete handoff.

No production prompts, engine, schemas or canonical runs may change. No new provider calls or games. Do not launch additional agents. The four core researchers will jointly review the combined shortlist, disputes and selected ordinary decisions afterward. These first passes do not constitute final adjudication or complete steps 9–10.
