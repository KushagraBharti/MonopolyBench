# Results and quantitative synthesis

Date: 2026-07-28

Scope: the eight completed saved games listed in `docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv`

Claim status: finite-corpus, descriptive, and mechanism-oriented; **not a balanced model leaderboard**

## 1. Executive result

The audited corpus contains eight completed four-player games, all ending by bankruptcy before the configured cap. Across 1,391 playable turns, the engine produced 3,696 unique decisions and 3,696 applied actions. The arena made 3,790 model attempts: 3,602 decisions were valid on their first attempt, 94 received a corrective retry, 88 of those retries recovered, and six resolved through deterministic fallback. The attempt stream therefore contains 100 invalid attempts. Recorded usage totals 20,474,750 tokens and $113.84159595, with one of 3,790 attempts lacking OpenRouter usage and cost rather than being estimated.

All eight games pass state replay. Seven pass strict full-artifact replay. Run `mock-83265-81ed4937` is state-valid but strict-artifact-failed at sequence 669: the original event preserves fallback provenance for an applied `reject_trade`, while replay reconstructs the same applied action as valid. This is a bounded provenance mismatch, not state divergence.

The strongest cross-run descriptive pattern is within-game rent conversion: the eventual winner has the largest net rent in all eight observed trajectories. Winner net rent ranges from +$939 to +$6,828 (median +$2,972), and the within-game margin over the next-best player ranges from $931 to $7,086 (median $2,743). This is an empirical invariant of these eight selected traces, not an estimated population rate and not proof that net rent caused victory. A useful counterexample concerns bargaining volume: the player who initiated the most trade episodes lost in five of eight games. Proposal volume is therefore not a defensible proxy for negotiation quality or economic success.

No confidence interval, hypothesis test, or model ranking is warranted from this corpus. Seeds, seats, roster families, endpoint versions, game caps, survival exposure, decision mixes, and provider prices are not balanced. The results support measurement validity, exact reliability and cost accounting, and named mechanism case studies.

## 2. Source-key convention

Every number below resolves to a frozen or generated artifact using these keys.

- **Ledger key `L[run_id]`:** row `run_id=<run_id>` in `docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv`. The total row is `saved_game=TOTAL`.
- **Run key `S[run_id]`:** the sole row with `run_id=<run_id>` in `saved_games/<saved_game>/analysis/tables/run_summary.csv`.
- **Terminal key `E[run_id]`:** row `event_type=GAME_ENDED` in `saved_games/<saved_game>/analysis/tables/events.csv`; `seq` is the event sequence and `turn_index` is the synthetic terminal index. Playable-turn counts are row `event_type=TURN_STARTED` in `analysis/tables/event_counts.csv`.
- **Player key `P[run_id, player_id]`:** row `player_id=<player_id>` in `saved_games/<saved_game>/analysis/expanded_metrics/player_metrics.csv`.
- **Attempt key `U[run_id, player_id]`:** row `player_id=<player_id>` in `saved_games/<saved_game>/analysis/tables/model_usage.csv`. Here `calls` means attempts, not unique decisions. Per-player `cost` is display-rounded in this CSV; exact run cost comes from the ledger and call-reconciliation JSON.
- **Call key `C[run_id]`:** `saved_games/<saved_game>/analysis/quality/call_reconciliation.json`, especially `decisions` and `usage_and_cost`. For Run 191, the missing-usage key is `decision_id=mock-83265-81ed4937-dec-000389`, `attempt_index=0`.
- **Replay key `R[run_id]`:** `saved_games/<saved_game>/analysis/reports/integrity_report.md` and the package’s `analysis/quality/replay_verification.json` (or split replay JSONs where used).
- **Review key `M[run_id]`:** `saved_games/<saved_game>/analysis/reports/manual_review_report.md`.

Exact run-root resolution:

| Run ID | `<saved_game>` |
|---|---|
| `mock-321229807-87ca99d7` | `frontier-115-mock-321229807-87ca99d7-gemini-3-1-pro-preview` |
| `mock-24591-46c1eb90` | `frontier-mini-154-mock-24591-46c1eb90-gemini-3-5-flash` |
| `mock-64394-c3bb8d94` | `frontier-mini-157-mock-64394-c3bb8d94-grok-4-3` |
| `mock-1038910349-f66fa07c` | `frontier-163-mock-1038910349-f66fa07c-claude-opus-4-8` |
| `mock-3676466999-527872e4` | `frontier-166-mock-3676466999-527872e4-claude-opus-4-8` |
| `mock-2413970733-53b199c1` | `frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview` |
| `mock-83265-81ed4937` | `frontier-191-mock-83265-81ed4937-openai-gpt-5-5` |
| `mock-44910-42ec35c5` | `frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview` |

Derived summaries identify their numerator, denominator, or row set. Quartiles use the median-of-halves convention on the eight run-level values.

## 3. Audited run design, outcome, and terminal markers

Roster codes keep the table readable:

- **F1:** Claude Opus 4.8 → Gemini 3.1 Pro Preview → Grok 4.3 → OpenAI GPT 5.5.
- **F2:** OpenAI GPT 5.5 → Claude Opus 4.8 → Gemini 3.1 Pro Preview → Grok 4.3.
- **M1:** OpenAI GPT 5.4 mini → Claude Haiku 4.5 → Gemini 3.5 Flash → Grok 4.3.
- **M2:** OpenAI GPT 5.4 Mini → Claude Haiku 4.5 → Gemini 3 Flash Preview → Grok 4.3.

| Run ID | Seed | Roster | Cap | Playable turns | Terminal `(turn, seq)` | Winner (seat) | State replay | Artifact replay |
|---|---:|---|---:|---:|---:|---|---|---|
| `mock-321229807-87ca99d7` | 321229807 | F1 | 400 | 115 | `(115, 2487)` | Gemini 3.1 Pro Preview (2) | pass | pass |
| `mock-24591-46c1eb90` | 24591 | M1 | 500 | 154 | `(154, 2915)` | Gemini 3.5 Flash (3) | pass | pass |
| `mock-64394-c3bb8d94` | 64394 | M1 | 500 | 157 | `(157, 2605)` | Grok 4.3 (4) | pass | pass |
| `mock-1038910349-f66fa07c` | 1038910349 | F1 | 400 | 163 | `(163, 2693)` | Claude Opus 4.8 (1) | pass | pass |
| `mock-3676466999-527872e4` | 3676466999 | F1 | 400 | 166 | `(166, 3340)` | Claude Opus 4.8 (1) | pass | pass |
| `mock-2413970733-53b199c1` | 2413970733 | F1 | 400 | 172 | `(172, 4072)` | Gemini 3.1 Pro Preview (2) | pass | pass |
| `mock-83265-81ed4937` | 83265 | F2 | 600 | 191 | `(191, 3971)` | OpenAI GPT 5.5 (1) | pass | **fail at seq. 669** |
| `mock-44910-42ec35c5` | 44910 | M2 | 600 | 273 | `(273, 4101)` | Gemini 3 Flash Preview (3) | pass | pass |

**Sources.** Seed, roster, cap, playable-turn count, winner, and replay summary: `L[run_id]`. Terminal turn and sequence: `E[run_id]`. Every terminal payload has `reason="BANKRUPTCY"` and the winner shown above. `TURN_STARTED` and `TURN_ENDED` each occur exactly `playable turns` times, on indices `0..T-1`; `GAME_ENDED` occurs once at synthetic index `T`.

All games ended before the cap. Observed duration was 28.750%–45.500% of the configured cap (`L[run_id].turns / L[run_id].max_turns`), so this corpus has no cap-censored game. The aggregate of 1,391 is a count of playable turns, not the sum of terminal indices plus one.

### Seat and roster confounding

F1 repeats four times with model and seat perfectly aliased: Claude is always seat 1, Gemini seat 2, Grok seat 3, and GPT seat 4. F2 contributes one partial rotation, not a complete seat schedule. M1 repeats twice with a fixed order; M2 retains the seat pattern but changes the Gemini endpoint. The observed winner seats are 1 in three games, 2 in two, 3 in two, and 4 in one. These counts describe the saved games only; they cannot separate seat, seed, endpoint, or opponent effects.

The ledger contains **six exact winning model labels**: Claude Opus 4.8 and Gemini 3.1 Pro Preview each appear twice; Gemini 3.5 Flash, Gemini 3 Flash Preview, Grok 4.3, and OpenAI GPT 5.5 each appear once. The research handoff’s phrase “four distinct winning model labels” should be corrected: four is the number of **provider families** among winners (Google, Anthropic, OpenAI, and xAI), not the number of exact model labels. Source: grouping `L[all].winner` without normalizing endpoint names.

## 4. Audited decision, attempt, reliability, usage, and replay table

| Run ID | Decisions | Attempts | Retries | Invalid attempts | Fallback decisions | Recorded tokens | Recorded cost (USD) | Usage-bearing attempts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `mock-321229807-87ca99d7` | 366 | 377 | 11 | 13 | 2 | 1,988,867 | 14.61438250 | 377/377 |
| `mock-24591-46c1eb90` | 396 | 401 | 5 | 5 | 0 | 2,043,461 | 4.65275495 | 401/401 |
| `mock-64394-c3bb8d94` | 346 | 355 | 9 | 9 | 0 | 1,820,013 | 4.03655795 | 355/355 |
| `mock-1038910349-f66fa07c` | 364 | 371 | 7 | 7 | 0 | 1,884,152 | 12.06275605 | 371/371 |
| `mock-3676466999-527872e4` | 488 | 502 | 14 | 14 | 0 | 2,790,853 | 21.91408585 | 502/502 |
| `mock-2413970733-53b199c1` | 613 | 631 | 18 | 20 | 2 | 3,477,613 | 24.60457580 | 631/631 |
| `mock-83265-81ed4937` | 583 | 604 | 21 | 23 | 2 | 3,524,545 | 27.71173045 | 603/604 |
| `mock-44910-42ec35c5` | 540 | 549 | 9 | 9 | 0 | 2,945,246 | 4.24475240 | 549/549 |
| **Finite-corpus total** | **3,696** | **3,790** | **94** | **100** | **6** | **20,474,750** | **113.84159595** | **3,789/3,790** |

**Sources.** Counts, tokens, and exact run costs: `L[run_id]`, cross-checked to `S[run_id]` and `C[run_id]`. Usage-bearing attempts: `C[run_id].usage_and_cost.missing_usage_attempt_count`. The total row is the exact column sum over the eight non-total ledger rows; usage coverage is `3,790 - 1`.

The Run 191 missing-usage attempt is `C[mock-83265-81ed4937].usage_and_cost.missing_usage_attempts[decision_id=mock-83265-81ed4937-dec-000389, attempt_index=0]`. The preserved raw provider payload reports an upstream 503, while the recorded wrapper status is 200. Tokens and cost are null in the reconciliation JSON and are not estimated. `analysis/tables/per_call_usage.csv` materializes that row as zero with `accounting_status=missing_openrouter_usage`; the JSON is authoritative for the null-versus-zero distinction. Therefore $113.84159595 and 20,474,750 are **recorded totals**, not a claim that the missing attempt consumed zero tokens or zero billed cost.

### Exact decision/attempt reconciliation

Let \(D=3{,}696\) decisions, \(A=3{,}790\) attempts, \(R=A-D=94\) corrective retry attempts, \(F=6\) fallback decisions, and \(I=100\) invalid attempts.

- First-attempt-valid decisions: \(D-R=3{,}602\), or 97.456710% of decisions.
- Initially invalid decisions: \(R=94\), or 2.543290% of decisions.
- Retry recoveries: \(R-F=88\), or 93.617021% of initially invalid decisions.
- Deterministic fallbacks: \(F=6\), or 0.162338% of decisions.
- Invalid attempts: \(I/A=100/3{,}790=2.638522\%\).
- Valid attempts: \(D-F=3{,}690\); a fallback applies an engine-selected action after both model attempts remain invalid.

The identity \(I=R+F=100\) holds because every retry-bearing decision has one invalid initial attempt, and each of the six fallback decisions has one additional invalid corrective attempt. These are finite-corpus accounting ratios, not uncertainty-bearing estimates of future model reliability.

The standard `model_usage.csv` field `fallback_rows` flags both attempts belonging to a fallback decision. It sums to 12 attempt rows across the corpus (four each in Runs 115, 172, and 191), but there are only six fallback **decisions**. Publication tables should use `P[run_id, player_id].fallback_decisions` or `L[run_id].fallbacks`.

### Protocol-row reconciliation

| Run ID | Unique decisions | Raw decision rows | Applied actions | Interpretation |
|---|---:|---:|---:|---|
| `mock-321229807-87ca99d7` | 366 | 732 | 366 | one start + one resolution per decision |
| `mock-24591-46c1eb90` | 396 | 792 | 396 | one start + one resolution per decision |
| `mock-64394-c3bb8d94` | 346 | 692 | 346 | one start + one resolution per decision |
| `mock-1038910349-f66fa07c` | 364 | 728 | 364 | one start + one resolution per decision |
| `mock-3676466999-527872e4` | 488 | 977 | 488 | one duplicate start marker for `dec-000030` |
| `mock-2413970733-53b199c1` | 613 | 1,227 | 613 | one duplicate start marker for `dec-000242` |
| `mock-83265-81ed4937` | 583 | 1,166 | 583 | one start + one resolution per decision |
| `mock-44910-42ec35c5` | 540 | 1,080 | 540 | one start + one resolution per decision |

**Sources.** `S[run_id].total_decisions`, `.decision_rows`, and `.action_rows`; duplicate-marker details: `M[mock-3676466999-527872e4]` and `M[mock-2413970733-53b199c1]`. The duplicate markers have one resolution, action, attempt chain, and replayed effect. Unique decision IDs—not raw protocol rows—are the denominator.

## 5. Finite-corpus descriptive summaries

These are summaries of the eight observed games. Because the game set is selected and treatments are not randomized or balanced, the table deliberately reports no standard errors, confidence intervals, or \(p\)-values.

| Run-level metric | Total | Median | IQR | Range |
|---|---:|---:|---:|---:|
| Playable turns | 1,391 | 164.5 | 155.5–181.5 | 115–273 |
| Decisions | 3,696 | 442.0 | 365.0–561.5 | 346–613 |
| Attempts | 3,790 | 451.5 | 374.0–576.5 | 355–631 |
| Corrective retries | 94 | 10.0 | 8.0–16.0 | 5–21 |
| Invalid attempts | 100 | 11.0 | 8.0–17.0 | 5–23 |
| Fallback decisions | 6 | 0.0 | 0.0–2.0 | 0–2 |
| Recorded tokens | 20,474,750 | 2,417,157 | 1,936,509.5–3,211,429.5 | 1,820,013–3,524,545 |
| Recorded cost (USD) | 113.84159595 | 13.338569275 | 4.448753675–23.259330825 | 4.03655795–27.71173045 |

**Source and formula.** For each column, take `L[all].<metric>` over the eight non-total rows. Total is the exact sum. Median and quartiles use the median-of-halves convention.

Across the finite corpus, recorded cost is $0.030801298 per decision and $0.030037360 per attempt; recorded tokens are 5,539.705 per decision. The median run-level cost per decision is $0.036534723 (range $0.007860653–$0.047532985). These divisions use `L[all].total_cost_usd`, `.decisions`, `.attempts`, and `.total_tokens`. They are exposure-normalized accounting descriptions, not fair provider comparisons: endpoint pricing, survival length, decision type, retry incidence, reasoning behavior, and roster differ.

## 6. Cross-run observations and counterexamples

### 6.1 Rent conversion is the strongest observed within-game outcome signal

| Run ID | Winner | Winner net rent | Next-best net rent | Within-game margin |
|---|---|---:|---:|---:|
| `mock-321229807-87ca99d7` | Gemini 3.1 Pro Preview | +$939 | +$8 | $931 |
| `mock-24591-46c1eb90` | Gemini 3.5 Flash | +$2,796 | +$63 | $2,733 |
| `mock-64394-c3bb8d94` | Grok 4.3 | +$1,912 | +$258 | $1,654 |
| `mock-1038910349-f66fa07c` | Claude Opus 4.8 | +$3,643 | -$945 | $4,588 |
| `mock-3676466999-527872e4` | Claude Opus 4.8 | +$3,148 | +$395 | $2,753 |
| `mock-2413970733-53b199c1` | Gemini 3.1 Pro Preview | +$2,058 | +$293 | $1,765 |
| `mock-83265-81ed4937` | OpenAI GPT 5.5 | +$4,832 | -$859 | $5,691 |
| `mock-44910-42ec35c5` | Gemini 3 Flash Preview | +$6,828 | -$258 | $7,086 |

**Sources.** Winner and every rent value are `P[run_id, player_id].winner` and `.rent_net`. “Next-best” is `max(rent_net)` among the three rows with `winner=False`; margin is winner minus next-best.

The winner is the within-game net-rent leader in 8/8 observed games. Winner net rent has median +$2,972 and range +$939 to +$6,828; the margin has median $2,743 and range $931 to $7,086. Do not attach a binomial interval to 8/8: the games are neither randomly sampled nor exchangeable. The defensible claim is that all eight reviewed trajectories exhibit a winner-side rent-conversion advantage. The case reviews show different routes to that advantage—direct development, blocker exchange, house scarcity, and creditor-transfer compounding—so the table does not identify one causal policy.

### 6.2 Trade volume is not outcome quality

| Run ID | Highest proposal count (player) | Winner proposal count | Did the top proposer win? |
|---|---:|---:|---|
| `mock-321229807-87ca99d7` | 85 (OpenAI GPT 5.5) | 0 | no |
| `mock-24591-46c1eb90` | 36 (Gemini 3.5 Flash) | 36 | yes |
| `mock-64394-c3bb8d94` | 24 (OpenAI GPT 5.4 mini) | 0 | no |
| `mock-1038910349-f66fa07c` | 40 (OpenAI GPT 5.5) | 1 | no |
| `mock-3676466999-527872e4` | 106 (OpenAI GPT 5.5) | 0 | no |
| `mock-2413970733-53b199c1` | 133 (OpenAI GPT 5.5) | 0 | no |
| `mock-83265-81ed4937` | 65 (OpenAI GPT 5.5) | 65 | yes |
| `mock-44910-42ec35c5` | 21 (Gemini 3 Flash Preview) | 21 | yes |

**Sources.** `P[run_id, player_id].trade_proposals_sent`; winner flag from the same row. The highest-proposal player lost in 5/8 games. This is a counterexample to interpreting proposal count, message count, or accepted-deal count as negotiation quality. Episode terms, conversion into productive assets, retained liquidity, and downstream state must remain separate.

### 6.3 Reliability and economic success are distinct

The corpus contains direct counterexamples in both directions.

- In Run 273, Claude Haiku 4.5 had 88 decisions, 88 attempts, and zero invalid attempts but lost; the winner had 190 decisions, 192 attempts, and two invalid attempts (`P/U[mock-44910-42ec35c5, ...]`).
- In Run 163, OpenAI GPT 5.5 had 126 decisions, 126 attempts, and zero invalid attempts but lost; Claude won with the same zero-invalid profile (`P/U[mock-1038910349-f66fa07c, ...]`).
- In Run 115, the winner incurred one deterministic fallback, while Claude’s different fallback at `dec-000330` caused an immediately avoidable bankruptcy despite a sufficient legal house-sale line (`P[mock-321229807-87ca99d7, Gemini 3.1 Pro Preview]`; `M[mock-321229807-87ca99d7]`).
- In Run 172, Claude’s two invalid serialization attempts at `dec-000582` caused fallback bankruptcy even though selling one house from each red property would cover the $187 shortfall; the winner had no fallback (`M[mock-2413970733-53b199c1]`).
- In Run 157, GPT’s terminal menu exposed at least $1,022 against $950 owed, but its private arithmetic undercounted house-sale proceeds and it declared bankruptcy (`M[mock-64394-c3bb8d94]`).

These named cases support a systems claim: reliability incidents can be economically immaterial, temporarily delaying, or terminally decisive. They do not support a general model-reliability ranking because decision exposure and roster assignment differ.

### 6.4 Terminal outcomes and replay should not be flattened

All 24 eliminated player-games ended in the eight bankruptcy trajectories (`sum(P[all].bankrupt=True)=24`), but immediate avoidability is a decision-local label, not a global causal judgment. The manual reviews establish exact immediate-menu survival lines in Runs 115, 157, and 172. Many counterexample terminal menus were forced; Run 273’s GPT loss is explicitly “avoidable-risk” rather than deterministically avoidable because the legal alternative occurred one turn earlier and future rolls are counterfactual. Do not convert these labels into a prevalence estimate without a harmonized machine-readable adjudication table and independent review.

Run 191 must be described as **state-valid, strict-artifact-failed**, not “replay pending,” “replay clean,” or “state divergent.” The exact mismatch is `mock-83265-81ed4937-evt-000669`, decision `mock-83265-81ed4937-dec-000096`: original `valid=false`, `error="fallback:illogical_after_retry"`; replay `valid=true`, `error=null`; same applied `reject_trade`; zero missing/extra actions and no decision-ID mismatch (`R[mock-83265-81ed4937]`).

## 7. Recommendations for existing publication figures and tables

No current plot should be dropped into the main paper without a caption and event annotations. The underlying data are publication-useful; the generated PNGs are strong bases.

### Main-paper candidates

1. **Run 273 trajectory panel (best clean long-game figure).**
   - Existing plots:
     - `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/plots/net_worth_estimate_by_turn.png`
     - `.../analysis/plots/houses_by_turn.png`
     - optionally `.../analysis/plots/bank_inventory_by_turn.png`
   - Source tables:
     - `.../analysis/tables/state_by_turn_player.csv`, keyed by `(turn_index, player_id)`
     - `.../analysis/tables/bank_inventory_by_turn.csv`, keyed by `turn_index`
   - Publication use: a two-panel trajectory showing economic divergence and the finite-house mechanism.
   - Required edits: mark bankruptcy turns 109, 166, and 272; mark the turn-167 New York exchange; state that net worth is a derived estimate; use colorblind-safe lines and direct labels.
   - Exact annotation keys: bankruptcy events `mock-44910-42ec35c5-evt-002066`, `mock-44910-42ec35c5-evt-002850`, and `mock-44910-42ec35c5-evt-004098` in `analysis/tables/events.csv`; the New York exchange is `decision_id=mock-44910-42ec35c5-dec-000395`/`mock-44910-42ec35c5-dec-000396` and accepted-trade event `mock-44910-42ec35c5-evt-002870`, followed by Orange build decisions `mock-44910-42ec35c5-dec-000397` through `mock-44910-42ec35c5-dec-000403`. These keys are also indexed in `analysis/reports/integrity_report.md` and `analysis/reports/case_studies.md`.

2. **Run 115 fallback-to-outcome mechanism panel.**
   - Existing plots:
     - `saved_games/frontier-115-mock-321229807-87ca99d7-gemini-3-1-pro-preview/analysis/plots/net_worth_estimate_by_turn.png`
     - `.../analysis/plots/houses_by_turn.png`
   - Source tables and evidence:
     - `.../analysis/tables/state_by_turn_player.csv`
     - `.../analysis/expanded_metrics/decision_metrics.csv`, keyed by `decision_id`
     - `M[mock-321229807-87ca99d7]`, especially `dec-000330` and `dec-000331`
   - Publication use: annotate Claude’s turn-95 legal house-sale line, fallback bankruptcy, creditor transfer, and Gemini’s next-turn fallback. This is the clearest separation of strategic intention, serialization, fallback, and economic effect.

3. **Run 166 house-scarcity/creditor-transfer panel.**
   - Existing plots:
     - `saved_games/frontier-166-mock-3676466999-527872e4-claude-opus-4-8/analysis/plots/houses_by_turn.png`
     - `.../analysis/plots/bank_inventory_by_turn.png`
     - `.../analysis/plots/building_value_by_turn.png`
   - Publication use: mark the turn-139 eight-house dark-blue build and the later $1,300 Park Place obligations. This supports a mechanism claim without implying cross-run superiority.
   - Exact annotation keys: build decisions `mock-3676466999-527872e4-dec-000434` through `mock-3676466999-527872e4-dec-000436`; Gemini’s $1,300 obligation and terminal menu at `mock-3676466999-527872e4-dec-000465` with effect range `mock-3676466999-527872e4-evt-003135` through `mock-3676466999-527872e4-evt-003151`; GPT’s $1,300 obligation and terminal menu at `mock-3676466999-527872e4-dec-000487` with effect range `mock-3676466999-527872e4-evt-003329` through `mock-3676466999-527872e4-evt-003340`. Source: `analysis/reports/manual_review_report.md`, with the canonical event rows in `analysis/tables/events.csv`.

### Main-paper tables

1. **Corpus accounting and replay table:** use the table in Section 4 of this memo. It is stronger than the current manuscript’s two-run presentation because it exposes exact denominators, missing usage, and split replay status.
2. **Roster/seat table:** use Section 3, or move the full roster definitions to an appendix and retain roster code, seed, cap, winner seat, and replay in the main paper.
3. **Within-game rent table:** use Section 6.1 as a compact result table or appendix table. Its claim is descriptive and within-game; do not sort it into a model leaderboard.

### Appendix-only candidates

- Per-run `cost_by_model.png`, `total_tokens_by_model.png`, `latency_per_call.png`, and `reasoning_tokens_per_call.png`. These are useful systems diagnostics but are confounded by survival exposure, decision type, provider pricing, and missing/heterogeneous reasoning-token semantics.
- Per-run `expanded_metrics/player_metrics.csv`, keyed by `player_id`, for the full rent, trade, auction, mortgage, development, and reliability appendix.
- `expanded_metrics/trade_episodes.csv`, `auction_episodes.csv`, and `mortgage_episodes.csv` for named case studies. Episode tables are preferable to message-level counts.

### Do not use as-is

- `analysis/tables/model_usage.csv` for exact corpus cost totals: player costs are display-rounded, so their sum differs from the exact call-ledger total by up to about one micro-dollar per run. Use `call_reconciliation.json` or the eight-run ledger for exact totals.
- A pooled “cost by model” figure across these games: the design does not balance survival, seat, game length, model version, or decision mix.
- A win-count bar chart: with six exact winning labels and unbalanced rosters, it would visually imply a leaderboard the design cannot support.

## 8. Publication-ready LaTeX for Results

The following text is written to replace the current two-run pilot framing. It assumes the manuscript already defines `\Bench`, `booktabs`, and `table*`.

```latex
\section{Audited Pilot Results}
\label{sec:results}

\subsection{Corpus and claim scope}

We present eight completed bankruptcy games as audited descriptive case
studies, not as a model leaderboard.  The games span 1,391 playable turns and
contain 3,696 engine-produced decisions, 3,696 applied actions, and 3,790 model
attempts.  All games ended before their configured turn cap.  The design is
not balanced: four frontier games use one fixed model--seat assignment, one
frontier game uses a partial rotation, two mini-roster games share a fixed
assignment, and the longest mini-roster game changes the Gemini endpoint.
Seeds, seats, endpoint versions, opponent composition, and maximum-turn
settings are therefore confounded.  We report finite-corpus totals, medians,
and ranges, and make no population-level ranking or prevalence claim.

\begin{table*}[t]
\caption{Audited eight-game corpus. $D$ is the number of unique engine
decisions and applied actions; $A$ is the number of model attempts; $R=A-D$
is the number of corrective retry attempts; $I$ is the number of invalid
attempts; and $F$ is the number of fallback-resolved decisions. Costs are
recorded OpenRouter costs. Run 191 has one attempt with missing usage and
cost, which is not estimated.}
\label{tab:eight_game_corpus}
\centering
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrrrrrcc}
\toprule
Run & Turns & $D$ & $A$ & $R$ & $I$ & $F$ & Cost (\$) &
State & Artifact \\
\midrule
321229807 & 115 & 366 & 377 & 11 & 13 & 2 & 14.61438250 & pass & pass \\
24591      & 154 & 396 & 401 &  5 &  5 & 0 &  4.65275495 & pass & pass \\
64394      & 157 & 346 & 355 &  9 &  9 & 0 &  4.03655795 & pass & pass \\
1038910349 & 163 & 364 & 371 &  7 &  7 & 0 & 12.06275605 & pass & pass \\
3676466999 & 166 & 488 & 502 & 14 & 14 & 0 & 21.91408585 & pass & pass \\
2413970733 & 172 & 613 & 631 & 18 & 20 & 2 & 24.60457580 & pass & pass \\
83265      & 191 & 583 & 604 & 21 & 23 & 2 & 27.71173045 & pass & fail$^\dagger$ \\
44910      & 273 & 540 & 549 &  9 &  9 & 0 &  4.24475240 & pass & pass \\
\midrule
Total & 1,391 & 3,696 & 3,790 & 94 & 100 & 6 &
113.84159595 & 8/8 & 7/8 \\
\bottomrule
\multicolumn{10}{l}{\footnotesize $^\dagger$State replay passes; strict artifact
replay first differs at sequence 669 in fallback-validity provenance.}
\end{tabular}
\end{table*}

\subsection{Reliability, usage, and replay}

Of the 3,696 decisions, 3,602 were valid on the first attempt
(97.456710\%).  Ninety-four decisions received a corrective retry; 88
recovered and six resolved through deterministic fallback.  Because each
fallback decision contains an invalid initial attempt and an invalid
corrective attempt, the attempt stream contains 100 invalid attempts
(2.638522\% of 3,790 attempts).  The fallback rate is 0.162338\% per
decision.  These are accounting ratios for the observed corpus, not estimates
of future model reliability.

The artifact stream records 20,474,750 tokens and \$113.84159595.  Usage and
cost are present for 3,789 of 3,790 attempts.  The missing record is the first
attempt for decision \texttt{mock-83265-81ed4937-dec-000389}; its upstream
provider response was an error, and the missing fields remain null rather
than being imputed.  Median run cost is \$13.338569275 (range
\$4.03655795--\$27.71173045).  These costs are not directly comparable across
models because game length, survival exposure, decision mix, endpoint price,
and retry incidence differ.

All eight action sequences pass deterministic state replay.  Seven also pass
strict full-artifact replay.  Run 191 is state-valid but not
strict-artifact-clean: at event \texttt{mock-83265-81ed4937-evt-000669},
decision \texttt{mock-83265-81ed4937-dec-000096}, the original event records
\texttt{valid=false} and
\texttt{error="fallback:illogical\_after\_retry"} for the applied
\texttt{reject\_trade}; replay reconstructs the same applied action as valid
with no error.  State progression, action count, and decision linkage agree.

\subsection{Economic mechanisms}

The eventual winner has the largest net rent in every observed game.  Winner
net rent ranges from \$939 to \$6,828 (median \$2,972), while the within-game
margin over the next-best player ranges from \$931 to \$7,086 (median
\$2,743).  We interpret this as a recurring descriptive signature of
productive conversion in the reviewed trajectories, not as a causal estimate:
the case reviews identify different paths, including direct development,
blocker exchange, finite-house constraints, and creditor-transfer
compounding.

Negotiation volume supplies an important counterexample.  The player who
initiated the most trade episodes lost in five of eight games.  In four of
those games the winner initiated no trade episode, and in another the winner
initiated one.  Proposal count therefore measures market activity, not
negotiation quality.  Accepted terms, liquidity effects, monopoly completion,
development, and downstream rent must be analyzed separately.

Reliability is likewise distinct from economic success.  Several losing
players completed their runs without an invalid attempt, while the Run 115
winner incurred a fallback.  Conversely, two serialization failures at
solvency decisions in Runs 115 and 172 bypassed legal house-sale survival
lines and produced fallback bankruptcy.  These cases show why \Bench\ reports
strategic choice, action serialization, fallback policy, and economic effect
as separate layers.

\subsection{Interpretive boundary}

The eight games validate the benchmark's measurement and evidence pipeline and
expose auditable mechanisms that final win labels obscure.  They do not
identify a best model.  Confirmatory comparison requires preregistered engine
seeds, balanced seat rotations, fixed rosters and endpoint versions, frozen
prompt/tool/retry contracts, and game-level uncertainty analysis.
```

## 9. Final manuscript handoff notes

1. Replace the current Run A phrase “583 model calls” with “583 decisions and applied actions, 604 model attempts, 21 corrective retries, 23 invalid attempts, and two deterministic fallbacks.”
2. Replace “replay reconciliation is pending” with the exact state-pass/artifact-fail sequence-669 paragraph above.
3. Do not call Run 273 the only trustworthy or only replay-clean game. It is the longest fully replay-clean audited case study.
4. Use “six exact winning model labels across four provider families,” not “four winning model labels.”
5. Keep `calls`, `attempts`, `decisions`, raw decision protocol rows, retry attempts, invalid attempts, and fallback decisions as separate quantities.
6. Preserve the single missing-usage attempt as null in prose and analysis. Do not infer zero cost from the standardized CSV’s zero materialization.
7. Keep rent and negotiation observations explicitly within-game and descriptive. Do not sort the corpus by win count or imply a balanced leaderboard.
8. State that all 1,391 turns are playable `TURN_STARTED`/`TURN_ENDED` turns and that each terminal marker occurs at the next synthetic index.
