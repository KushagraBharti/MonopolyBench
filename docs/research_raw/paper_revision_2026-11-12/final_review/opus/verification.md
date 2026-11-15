# Verification record, Opus final review

All work used existing saved files, arithmetic, and document builds inside `final_review/opus/`. Nothing else was run: no game, engine or replay execution, baseline, synthetic scenario, provider probe, model or evaluation query, web search, subagent, commit or push. I did not open any other final reviewer's folder. I opened the November 12 cross-review findings only after `initial_position.md` was written, and only my own (`reviews/opus`) and Fable's G5, G13 and G15 entries, which the adjudication cites.

## Pin

- **Before** (`pin_check_before.txt`): 78 entries, 0 mismatches. PDF SHA-256 `f0312183aa8794ec08614966570395e55abd769410ff99f06992f25f314ed8a1`.
- **After** (`pin_check_after.txt`): 78 entries, 0 mismatches, same PDF hash.
- **Write-scope check.** At handoff I listed recently modified files outside `final_review/opus/` to confirm I had written nothing elsewhere. The listing printed only file names from the `sol`, `fable_5_2` and `astra` final-review folders, which those reviewers' own sessions were writing concurrently. I did not open or read any of them.

## Rendering

- I rendered all 21 pages with Ghostscript at 80 dpi and page 19 at 150 dpi, and inspected each page. The images were scratch files only and are not kept here. Text was also extracted with Ghostscript `txtwrite`.
- `replacement_prose.tex` compiles with LuaLaTeX into `build/` with no errors or box warnings.

## Checked by me in this review (fresh)

Scripts in this folder: `recompute_bargaining.py`, `recompute_resampling.py`, `recompute_finance.py`, `dump_decisions.py`, `extract_spans.py`. Each output JSON sits beside its script.

### Offers (from `integrated/data/offers.json`)
- **Census.** 920 responses (113 accept, 394 counter, 413 reject) across 526 threads; 918 legally acceptable.
- **Tables.** Every opening and later cell in Tables 3 and 5, using my own form classifier.
- **Proposer strata.** 44/50, 4/8, 42/50, 5/8 against 9/11, 0/2, 15/23, 13/36.
- **Recipient strata** for swaps and cash bids, including −0.2 to +8.5.
- **Block summaries.** Pooled gaps 30.5, 16.7 and −5.0. Leave-one-block-out ranges. Block values: all swaps 35.3, 40.5, 27.6, 33.5, 19.4; no-Grok 27.5, 45.5, 6.0, −23.5, 11.1.
- **Resampling.** Intact-block 2.5/97.5 percentiles from all 3,125 draws match exactly. My own-seed game and two-stage resamples come within about 0.5 point of Table 8.
- **Cash bands.** 17/69 and 120/175; 44 counters; 43 later; 21 facing Opus; Gemini 10/11.
- **Rejection population.** The 74 recipient-completing rejections split 38/36.

### Original decisions (`decisions.jsonl`)
- **Grok conflicts.** 64 of 136 Grok openings conflict with the assistant content, and 13 of the 15 accepted Grok-authored neither-completing swaps are among them. 7 of 28 Grok acceptances conflict.
- **Acceptances by system.** Sol 30, Opus 29, Grok 28, Gemini 26.

### Debts
For all 188 ledger episodes, I recomputed C, S, M0 and M* from the first-decision prompt payload and `contracts/data/board.json`. Prompt cash and debt match the ledger in 188/188.
- **Partition.** 62 / 54 (52 paid, plus G7 Opus menu-restricted and G12 d249 Grok) / 16 (14 paid) / 56.
- **Necessity rows.** All sixteen D, U0, U* and outcomes match Table 9 exactly.
- **Action counts.** 180 mortgages, 89 sales, $51,997, 67 one-action payments.
- **First actions.** 50/56 immediate declarations; 4 mortgage and 2 sell first; 8 bankruptcy-only menus.
- **Released collateral.** 19 payments use mortgages absent from the first menu, 33 mortgages in total, including the five named non-necessary episodes.

### Sixteen initial texts
I read all sixteen in the PDF and source. My classification is 12 explicit, 1 aggregate (G20 d327), 1 tentative (G20 d291) and 2 omissions. I checked every arithmetic sum in the texts against U0/U*.

### Information in the liquidation state
The G20 d327 payload contains only space keys, the scenario note and holdings, with no price, cost, salvage or mortgage-value field.

### Provider channels
- **Opus.** In the five Opus necessity episodes, the returned `reasoning.text` runs 59–105 words against 220–429 reported reasoning tokens.
- **Gemini.** G5 d263 returns `reasoning.text` (158 words, 516 tokens) and `reasoning.encrypted`.

### Incidents (decisions plus events)
- **G20 payment.** d324–d337, $500 + $200 in sales, eight mortgages, cash $14.
- **G5.** The t141 carried note, the d263 two-block reasoning, the d266 $149.
- **G15.** d160–d176, the d166 appeal present in the d169 prompt, the d162/d165 policy notes, and Grok's bankruptcy to Gemini at t81 with transfers.
- **G2.** d112–d130 and d195–d200, the d122 warning in the d124 prompt, houses at t69 and sales at t73, $44 rent at t77, and bankruptcy to Gemini at t85.
- **G19.** d135–d137 channels and holdings after the trade.
- **G7.** d40–d44 and d138–d160, then events: three dark-blue houses at t71, one sold at t72, $270 orange rent, and Gemini's elimination at t125.
- **G13.**
  - d249–d256: the exact omission span is present; the d250 note gives 5/36 and d252 gives 4/36; the $16 interest is correct.
  - Later events: Grok moves 26→29 at t111, Opus wins the NC auction at t114, and Grok goes bankrupt to Sol on Short Line at t150 (d311).
- **G20 coordination.** d93–d103, d128–d131 and d155–d161; elimination order p1 (Grok) t84, p2 t97, p3 t115.
- **G18.** d421–d462, including the d431 and d438 reasoning spans.
- **G12 d249.** Cash, houses, note, content and applied call.

### New spans proposed in the replacement prose
Nine spans (`extracted_spans.json`) are exact substrings of their saved fields. Each is recorded with game, decision, decisions.jsonl line, attempt, channel, response condition, offset and field SHA-256.

### Response conditions
- **Opus refusals.** 64/84, 40/60, 30/53 and 80/109 in G1–G4; 1,390/1,390 in G5–G20; 1,604 first-attempt refusals; one later refusal (G2 d129); zero refusals among recovery attempts.
- **Requests.** 8,687 saved call intents: Grok `tool_choice` "required" in 1,705; Opus, Sol and Gemini "auto". No temperature, top_p or token-cap key in any intent.

### Replay and cohort
- All 20 artifact and state replay reports pass.
- Artifact `excluded_event_types` is empty; state replay excludes exactly the four LLM event types and normalizes id/seq/ts. The run config uses ts start 0, step 250.
- 50,918 events; each `events.jsonl` line count equals the report count.
- Seeds match Table 11.
- Wins 8/7/3/2 by system and 7/7/3/3 by seat; one block won by Sol from every seat; one block won from seat 2 by every system.

## Inherited, not re-derived in this review

- The 61/74 semantic agreement and its row-level codes. I checked only the per-game totals (sum 61, G1+G15 = 31) in `root_delivered_checks.json`. These are earlier LLM-assisted readings, not human annotation.
- The three payable-declaration engine witnesses and the G7 menu-restricted search. These are prior engine-executed results; I did not rerun them.
- The episode detector that defines the 188 episode boundaries. I used the frozen ledger and checked its cash/debt against prompts.
- First-window development counts (16/17, 17/18, 7/15, 3/13); trade-group receipts ($57,378 and $53,810); 38/40 nonterminal eliminations; 227 deeds; 52 and 69 completions.
- Single-deed asking-price medians and the seven same-deed pairs. I confirmed only G2's 650/600 (median 625) and the 450 ask in the records.
- The fourteen resistance-to-settlement pairs.
- The 139-response Grok conflict census beyond the 64 openings and 7 acceptances I recounted.
- The 2,054 trade-summary misattributions, the 149 undelivered and 107 empty public messages, and the 338-payload count for the liquidation instruction. I saw the instruction verbatim in each liquidation payload I opened.
- Cost totals (USD 141.71 and 141.39), the reasoning-token means, and the fallback-model statement.
- Literature content: I relied on `literature_notes.md` and accessed no references.
- The integrated verifier's checks (twenty cards, sixteen fields, 738 protected entries, 234 frozen drafts). I re-verified quoted spans only where listed above.
