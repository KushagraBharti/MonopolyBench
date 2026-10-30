# Verification log: opus_contribution, round 1

All checks were read-only. No canonical, prompt, engine or draft file was edited. I ran no new games, provider calls or engine branches. Scripts are in `scripts/` and were run with `python3 -I` from the repository root.

## Order of work

1. Read `baseline/monopolybench-first-draft/manuscript.tex`, every `sections/*.tex` and `evidence_map.md` in full. I extracted the PDF text with macOS PDFKit (`/tmp/pdftext.swift`, a throwaway script) because poppler is not installed. Result: 34 pages, text consistent with the sources.
2. Wrote `initial_position.md` before opening `charter.md`, `coauthors/`, `final_review/`, `qa/`, or any phase folder. The other round-1 folders were empty when I listed them.
3. Checked primary records (below), then read the charter and grepped the prior reviews and phase folders to classify each finding as new or inherited.

## Checks I performed

| Check | Method | Result |
|---|---|---|
| G13 d250–254 actions, notes, reasoning | `scripts/dump_decisions.py` on G13 `run/decisions.jsonl` | Confirms draft quotes. d252 reasoning (21,134 chars) contains "I will frame the $130 offer as leaving me $35 short of Short Line, omitting that I could mortgage Ventnor … slightly deceptive, but p1 may not calculate the mortgage themselves." |
| d251 rationale follows d250 and precedes d252 | same, plus `scripts/g13_delivery_outcome.py` | Confirmed. d250 is delivered in d251 attempt 1 (action-only condition). The d251 reasoning mentions solvency. |
| Buyer motive before d250 | `scripts/g13_prior_motive.py` (d200–253, pattern search of Opus channels) | No independent Opus solvency motive found. d204 uses Grok's poverty as leverage. |
| Seller campaign before d250 | same script, public messages | Appeals at d218, d233 and d243. Sol corrects publicly at d244. d243 and d244 are delivered to Opus at d251 and d253; d218 is not (out of window). |
| 5/36 claim | Board arithmetic: Atlantic is 26, Short Line is 35, so a roll of 9 is needed, which is 4/36 | d250 public "5/36" is false. Grok's d252 reasoning self-corrects. Phase-2 `core_review/fable/debate.md:88` already flagged it. |
| d253 echo | Text comparison | "player 2 would inherit the yellows plus Pennsylvania" (d253) vs "gpt inherits the yellows plus Pennsylvania" (d252). |
| G13 consequence | `scripts/g13_delivery_outcome.py`, plus an inline scan of events around d311 | Turn 150: Grok rolls 5+1 and moves 29→35 (Short Line). d311 declares bankruptcy with "Can't cover the $200". Events 2295–2300 move $49 to p2 and give p2 spaces 26, 27 and 29. p2 is later eliminated by Luxury Tax at d355, and p1 (Opus) wins. |
| Ventnor route feasibility | **Not rerun.** I relied on the draft and on phase-2 `astra/g13_claim_checks.json` | The draft states $295; Grok's own reasoning computes the same $295. |
| G18 standing-offer delivery | Inline Python over G18 `decisions.jsonl` (d441 `decision_started` prompt, d442 attempt prompt) | "My Pacific offer still stands" appears 3 times in Sol's delivered `public_timeline_last_20` at d441, and 3 times in Opus's prompt at d442. **Draft claim confirmed.** |
| G4 d147–152 | Inline Python dump | The d148 note records "$150/house build cost" and an "If p1 insists on taking Orange" contingency before d149's "$200 a house". Draft confirmed. |
| Transport of Grok conflicts | Read `python/packages/arena/src/monopoly_arena/openrouter_client.py` (streams only if `stream_callback`); `rg stream_callback` finds it set only in `python/apps/api/src/monopoly_api/micro.py`; `scripts/raw_transport_check.py` over every game's `cloud/calls` | All Grok bodies are single JSON documents (1,695) apart from 11 "other". 147 have a content pseudo-call whose name differs from the tool name, all in JSON bodies. G19 d135 is body `3552adc5…response.json`: content `end_turn`, tool `propose_trade`, and the tool's `private_thought` says "Abort this trade. Do not send it." |
| Full-denominator END provenance | `scripts/end_provenance.py` → `scripts/end_provenance_output.txt` | Build-legal menus 1,225; END 663; defaults 66 (61/4/1/0, matching the draft appendix); detected conflicts 24 (all Grok); Opus 61/104. |
| Entry-buildable residual composition | Read `data/t09_entry_nonbuild_records.json` | Defaults: Opus G2, Sol G4, Opus G18. Conflicts: Grok G8, G12, G20. Holds: Grok G1, G15. |

## Literature verification (web, 2026-10-29)

| Source | Status |
|---|---|
| AgentMonopoly arXiv 2610.29330v2 (Wu, Li, Marsault, Huang, Cheng; v2 revised 22 Oct 2026) | Abstract page fetched. It confirms four families at two sizes, persona control, five seeds per configuration and open code. The abstract page does not state the legal-action, replay or prompt-prohibition details. I did **not** re-verify those against the full text or repository. |
| Arena arXiv 2608.14825v3 (Li, Petersson, Acquisti, Bakker; revised 21 Aug 2026) | HTML fetched via the WebFetch summarizer, first 100k of 161k characters. Confirms 2,583 emails across 20 runs and 13 models; a single-author 50-email check with 92.0% Tier-1 agreement (§5.1.1); sensitivity 0.571 and specificity 0.977 (App. A); replication with two other judge families (§4.3, 93.3% and 94.0%); follow-through 56.9% vs 31.5% (§5.1.3); no public redistribution (§2.1 footnote). These are summarizer outputs; exact sentences should be confirmed directly before quoting. |
| ABA Model Rule 4.1 cmt. [2] | The ABA primary pages returned HTTP 403. The courtrules.net New Hampshire page reproduces the "2004 ABA Model Rule Comment" with the phrases "Estimates of price or value placed on the subject of a transaction" and "a party's intentions as to an acceptable settlement of a claim". Verification is therefore **secondary**. |
| DECE, FinBoardBench, NegotiationArena, others | Not re-verified in this review; inherited from the draft's verified package. |

## Inherited, not checked by me

Counts I did not recompute: 6,989 / 8,679 / 50,918; 43/63; 34/42; 56/3/1 eliminations and their legal routes; 61/61 reorderable multisets; 44/113, 26/413 and 232/394 formatter manifestations; 2,054 prompts; 149 / 6,733 / 6,720 delivery figures; replay 20/20; 6,989 memory windows; 10,235 snapshots; and all spending-unit and receipt totals. I also did not check whether the G13, G4, G6 or G19 recipient prompts contained reversed trade summaries (OC-08 remains open).

## My own near-error (recorded deliberately)

My first G18 delivery check searched the per-attempt `prompt_messages` of the resolved record and found zero "still stands". For single-attempt decisions the delivered prompt lives on the `decision_started` record. Re-checking that record found 3 occurrences. The draft's claim is correct. This is the same evaluator-error pattern the paper describes: a record-layout assumption that produces a confident false negative.

## Discrepancy to reconcile

My detector finds 147 Grok bodies with a content pseudo-call name that differs from the tool name. The draft reports 139 action-name conflicts (138 parseable plus 1 malformed). The definitions differ: I count calls including non-applied attempts and parse `content` JSON `name`/`action`. I have not reconciled the two at record level, and this is not a claim that the draft is wrong.
