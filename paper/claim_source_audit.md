# MonopolyBench manuscript claim-to-source audit

Date: 2026-07-28  
Scope: `monopolybench_ieee_draft_v0_1.tex` and its two publication figures  
Evidence policy: repository artifacts are authoritative; prose and model-generated synthesis are not

## Authority order

1. Frozen `saved_games/<name>/run/` artifacts and authoritative snapshots/events.
2. Frozen `saved_games/<name>/quality_check/` and replay reports.
3. Deterministically generated `analysis/` tables, reconciliation JSON, and manifests.
4. Evidence-indexed qualitative review resolving to exact decisions, actions, events, prompts/responses, and snapshots.
5. The eight-run ledger and research handoff as reconciled cross-run indices.

The main corpus index is:

- `docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv`
- `docs/research_raw/monopolybench_research_handoff_2026-07-28.md`

## Corpus table

Every short run label in manuscript Table II maps by playable-turn count to
one unique ledger row; the ledger preserves its exact engine seed and run ID.
Exact unrounded values are:

| Run ID | Turns | Decisions/actions | Attempts | Retries | Invalid attempts | Fallback decisions | Tokens | Cost USD | State replay | Artifact replay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `mock-321229807-87ca99d7` | 115 | 366 | 377 | 11 | 13 | 2 | 1,988,867 | 14.61438250 | pass | pass |
| `mock-24591-46c1eb90` | 154 | 396 | 401 | 5 | 5 | 0 | 2,043,461 | 4.65275495 | pass | pass |
| `mock-64394-c3bb8d94` | 157 | 346 | 355 | 9 | 9 | 0 | 1,820,013 | 4.03655795 | pass | pass |
| `mock-1038910349-f66fa07c` | 163 | 364 | 371 | 7 | 7 | 0 | 1,884,152 | 12.06275605 | pass | pass |
| `mock-3676466999-527872e4` | 166 | 488 | 502 | 14 | 14 | 0 | 2,790,853 | 21.91408585 | pass | pass |
| `mock-2413970733-53b199c1` | 172 | 613 | 631 | 18 | 20 | 2 | 3,477,613 | 24.60457580 | pass | pass |
| `mock-83265-81ed4937` | 191 | 583 | 604 | 21 | 23 | 2 | 3,524,545 | 27.71173045 | pass | fail (first: sequence 669) |
| `mock-44910-42ec35c5` | 273 | 540 | 549 | 9 | 9 | 0 | 2,945,246 | 4.24475240 | pass | pass |
| **Total** | **1,391** | **3,696** | **3,790** | **94** | **100** | **6** | **20,474,750** | **113.84159595** | **8/8** | **7/8** |

Per-run cross-checks:

- `saved_games/<name>/analysis/tables/run_summary.csv`
- `saved_games/<name>/analysis/quality/call_reconciliation.json`
- `saved_games/<name>/analysis/quality/replay_verification.json`
- `saved_games/<name>/analysis/reports/integrity_report.md`

Table II rounds tokens to millions and cost to two decimals only for
presentation. The manuscript prose preserves the exact aggregate totals.

## Decision and attempt accounting

Claim: 3,602 decisions were valid on their first attempt; 94 received a
corrective retry; 88 recovered; six resolved through fallback; the stream
contains 100 invalid attempts.

Derivation from the reconciled corpus:

- `D = 3,696`
- `A = 3,790`
- `R = A - D = 94`
- first-attempt-valid decisions: `D - R = 3,602`
- retry recoveries: `R - F = 94 - 6 = 88`
- invalid attempts: `R + F = 100`, because each fallback has an invalid
  corrective attempt in addition to its invalid initial attempt
- first-attempt validity: `3,602 / 3,696 = 97.456710%`
- invalid-attempt rate: `100 / 3,790 = 2.638522%`
- fallback rate: `6 / 3,696 = 0.162338%`

Sources: each run's `analysis/quality/call_reconciliation.json`, reconciled in
the eight-run ledger.

## Usage and cost

Claim: recorded usage is 20,474,750 tokens and $113.84159595, with coverage
for 3,789 of 3,790 attempts.

Sources:

- exact aggregate and per-run totals: eight-run ledger
- missing attempt:
  `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/analysis/quality/call_reconciliation.json`
- missing key:
  `decision_id=mock-83265-81ed4937-dec-000389`, `attempt_index=0`

The missing usage and cost remain null. The standardized per-call CSV's zero
materialization is not interpreted as zero consumption.

## Replay claims

### Run 191

Sources:

- `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/run/replay_report.json`
- `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/run/events.jsonl`
- `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/run/actions.jsonl`
- `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/analysis/quality/replay_verification.json`
- `saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5/analysis/reports/integrity_report.md`

Exact finding:

- state replay: 1,640 state-relevant events pass
- strict artifact replay: 3,972 events compared; two fallback-response
  mismatches, first at sequence/index 669
- mismatch 1: event `mock-83265-81ed4937-evt-000669`, decision
  `mock-83265-81ed4937-dec-000096`, applied action `reject_trade`; original
  `valid=false`, `error=fallback:illogical_after_retry`; replay
  `valid=true`, `error=null`
- mismatch 2: event `mock-83265-81ed4937-evt-001202`, decision
  `mock-83265-81ed4937-dec-000186`, applied action `drop_out`; original
  `valid=false`, `error=fallback:malformed_after_retry`; replay
  `valid=true`, `error=null`
- no missing/extra action and no decision-ID mismatch
- controlling classification: `state_passed_artifact_failed`

The standard replay report records the first mismatch, as designed. A complete
comparison of the two fallback-resolved response events identifies the second;
both preserve the recorded applied action and leave state replay unchanged.

### Run 273

Sources:

- `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/quality/replay_verification.json`
- `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/reports/integrity_report.md`

Exact finding:

- state replay: 1,942/1,942
- strict artifact replay: 4,102/4,102

## Cross-run descriptive claims

### Winner-side net rent

Claim: the winner has the largest net rent in all eight saved games.

Source field:
`saved_games/<name>/analysis/expanded_metrics/player_metrics.csv`,
columns `winner` and `rent_net`.

Exact run-level winner values and margins over the next-best player:

| Run ID | Winner net rent | Next-best | Margin |
|---|---:|---:|---:|
| `mock-321229807-87ca99d7` | 939 | 8 | 931 |
| `mock-24591-46c1eb90` | 2,796 | 63 | 2,733 |
| `mock-64394-c3bb8d94` | 1,912 | 258 | 1,654 |
| `mock-1038910349-f66fa07c` | 3,643 | -945 | 4,588 |
| `mock-3676466999-527872e4` | 3,148 | 395 | 2,753 |
| `mock-2413970733-53b199c1` | 2,058 | 293 | 1,765 |
| `mock-83265-81ed4937` | 4,832 | -859 | 5,691 |
| `mock-44910-42ec35c5` | 6,828 | -258 | 7,086 |

Winner net rent median/range: 2,972 / 939--6,828.  
Margin median/range: 2,743 / 931--7,086.

The manuscript treats this only as a deterministic consistency check. The
exact ranges and medians remain here rather than being promoted as an
independent predictor, population estimate, or causal result.

### Trade-proposal volume

Claim: the player sending the most initial trade proposals lost in five of
eight games.

Source field:
`saved_games/<name>/analysis/expanded_metrics/player_metrics.csv`,
columns `trade_proposals_sent` and `winner`.

Top-proposer counts by run:
85, 36, 24, 40, 106, 133, 65, and 21. The top proposer won only in runs
`mock-24591-46c1eb90`, `mock-83265-81ed4937`, and
`mock-44910-42ec35c5`.

The exact Run 172 counterexample is sourced to
`saved_games/frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview/analysis/reports/case_studies.md`
and the standardized trade/property tables: GPT initiated all 133 proposals
and all 19 accepted deals, received 13 deeds, transferred 17, built and later
sold eight houses, and reached `mock-2413970733-53b199c1-dec-000602` without a
deed available to liquidate.

## Mechanism table and prose

### Serialization at solvency: Run 115

Sources:

- `saved_games/frontier-115-mock-321229807-87ca99d7-gemini-3-1-pro-preview/analysis/reports/case_studies.md`, Case 4
- decisions `mock-321229807-87ca99d7-dec-000327` through `...000330`
- events `...evt-002176` through `...evt-002206`
- exact focal decision `...dec-000330`

Verified facts: $1,203 cash, $1,400 due, $197 shortfall, eight legally saleable
brown houses, $200 sale proceeds, two invalid attempts, fallback bankruptcy.
The bounded alternative stops at current-payment survival with $3.

### Blocker exchange and productive conversion: Run 157

Sources:

- `saved_games/frontier-mini-157-mock-64394-c3bb8d94-grok-4-3/analysis/reports/case_studies.md`, CS03 and CS04
- auction/trade decisions `...dec-000251` through `...000265`
- second trade/development `...dec-000296` through `...000305`
- events `...evt-001860` through `...evt-002279`

Verified facts: a $321 minimum bid exceeded $317 cash; retry selected dropout;
Atlantic/Pacific exchange completed green/yellow; New York/Kentucky exchange
completed orange/red; the orange recipient built three hotels four turns
later.

### Creditor-transfer feedback: Run 163

Sources:

- `saved_games/frontier-163-mock-1038910349-f66fa07c-claude-opus-4-8/analysis/reports/case_studies.md`, Cases 1 and 4
- light-blue trade/build: decisions `...dec-000120` through `...000124`,
  events `...evt-000852` through `...000875`
- bankruptcy/creditor build: decisions `...dec-000257` through `...000267`,
  events `...evt-001880` through `...001967`

Verified facts: $320 Vermont/Connecticut purchase; same-turn 3/3/4 build;
later debtor transfer of $295 and seven deeds; red/green completion; red
development to 4/4/4.

### Finite-house constraint: Run 273

Sources:

- `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/reports/case_studies.md`, CS-08 and CS-09
- exchange/build decisions `...dec-000395` through `...000422`
- distress/reacquisition decisions `...dec-000514` through `...000532`
- events `...evt-002865` through `...004028`
- snapshots `run/state/turn_0167.json` through `turn_0180.json` and
  `turn_0256.json` through `turn_0265.json`

Verified facts: eleven bank houses before the exchange; nine purchased after
New York; the final two subsequently purchased; two and then six houses
released through distress sales and reacquired.

### Communication boundary cases: Runs 172 and 273

Sources:

- Run 172:
  `saved_games/frontier-172-mock-2413970733-53b199c1-gemini-3-1-pro-preview/analysis/review/communication_claims.csv`,
  `promise_lifecycle.csv`, and decisions `...dec-000545` through `...000556`
- Run 273:
  `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/review/communication_claims.csv`,
  claim `CLAIM-000395`, and raw public/private-analysis events
  `...evt-002863`/`...evt-002864`

Verified Run 172 sequence: GPT's public offer said it would retain Ventnor as
a Yellow blocker; the model-authored private analysis field treated Ventnor as future
bargaining leverage; Claude's response relied on blocker value; GPT then
offered and sold Ventnor to Gemini, completing Yellow. The review label is a
high-confidence, single-reviewer D3 candidate with acute liquidity pressure
and an intervening rejection retained as changed-plan alternatives. It is not
an adjudicated deception finding and is not used as a paper-level deception
result.

Verified Run 273 boundary: Gemini's public proposition at decision 395 was not
shown false, although its private analysis field described a plan to consume
the remaining houses. The review supports a D2 selective-framing candidate,
not D3
deception. Neither case supports a prevalence estimate.

## Source-freeze inventory audit

The supplementary `run115_source_file_inventory.csv` supplies the 3,163
per-file SHA-256 rows absent from Run 115's legacy aggregate-only freeze
record. Recomputing its `run/` and `quality_check/` rows under the recorded
`relative_path<TAB>bytes<TAB>sha256<LF>` algorithm yields, respectively,
`75f647ae4c86656e1f21fa008015883fe5e2c71caa320071214fea1ab94a4842`
and
`ad9dbfbdb2a02cfa52e26ed4022952916569ed9859f602c3dc760ce8fa5c7913`,
exactly matching the canonical manifest.

## Figure audit

### `paper/figures/architecture.pdf`

The diagram is conceptual and source-backed by:

- `AGENTS.md`, sections Core Invariants, Protocol Objects, Directory Ownership,
  Prompt And LLM Policy, and Artifact Policy
- run package layouts and replay reports

The live API/UI stream is visually separate from the frozen artifact path.
The caption limits determinism to recorded-action engine replay.

### `paper/figures/run273_house_lock.pdf`

Data sources:

- `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/tables/state_by_turn_player.csv`
- `saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview/analysis/tables/bank_inventory_by_turn.csv`
- `paper/scripts/generate_run273_figure.py`

The x-axis is authoritative state checkpoint index. First snapshots with the
three losing players bankrupt occur at 110, 167, and 273; their bankruptcy
events occur on playable turn indices 109, 166, and 272. The shaded interval
is checkpoints 167--180, covering decisions `...dec-000395` through
`...000422`.

The face-value asset-balance proxy is:

`cash + printed price of currently owned deeds + current installed building
stock at printed construction cost - mortgage principal proxy`.

It is not market, liquidation, continuation, or expected discounted-rent
value.

## Bibliography audit

Primary-source verification was completed for all twenty bibliography
entries. The following corrections were applied relative to the Prism draft
and early workstream:

- DSGBench uses archival IEEE author order and pages 16987--16991.
- The current M3-Bench v2 record uses five authors and the plural title phrase
  "Social Behaviors."
- Bonjour et al. names match the printed IEEE article.
- The Hasbro item uses the booklet's printed title.
- GAMA-Bench uses the archival ICLR 2025 title, "Competing Large Language
  Models in Multi-Agent Gaming Environments," rather than its stale arXiv
  title.
- SOTOPIA is cited as an ICLR 2024 paper, and CICERO uses the Science article
  title, group-author form, pages, and DOI.
- Vending-Bench, Cattle Trade, M3-Bench, AgenticPay, and CoffeeBench remain
  explicitly labeled arXiv preprints where applicable.
- ToolPRMBench and AgentRewardBench use their current primary arXiv records.
- All twenty entries appear in exact first-citation order; cited keys and
  bibliography keys form a one-to-one set with no missing, uncited, or
  duplicated entries.
- The NeurIPS 2024 stakeholder-negotiation entry includes its canonical
  proceedings pages, 83548--83599.
- OpenRouter reasoning-token, API-parameter, and provider-routing claims cite
  a consolidated entry containing the three corresponding official pages.
- The incomplete Beer Game/HBR item was removed.

## Intentionally removed or bounded claims

- The unimplemented targeted micro-scenario suite is not presented as a
  completed contribution or result.
- The corpus is eight games, not two.
- Run 191 replay is reconciled, not pending; it is not called fully
  artifact-clean.
- Replay is reported as verified in a fixed compatible engine/contract
  environment. The paper does not claim that every legacy package records a
  run-time engine commit or ruleset hash.
- Run 273 is one of seven strict-artifact-clean runs, not uniquely "cleanest."
- 3,696 decisions are not called model calls; 3,790 attempts are not called
  decisions.
- Model-authored private analysis fields are not treated as hidden cognition
  or true intent.
- No deception/collusion prevalence, strategy causality, avoidable-game,
  provider-ranking, or model-superiority claim is made.
- Costs are recorded route/date/exposure-dependent totals, not fair
  cross-model prices.
- The face-value asset-balance proxy is not treated as a universal strategic
  oracle.

## Final manuscript build audit

- LaTeX source SHA-256:
  `9afe64decdc02fbaa1dcb96419796b2fbd87fe9f7383d7f2a1c9b1281db7f72c`
- Sealed PDF SHA-256:
  `13d6e661b9fc771b26011c19103dddd91cc3f6f4474f11b8d3eae5327324596c`
- Build: three `pdfLaTeX` passes with MiKTeX-pdfTeX 4.27 / MiKTeX 26.5
- Output: nine US-Letter pages (612 by 792 points)
- Cross-reference gate: 20 unique citation keys, 20 bibliography entries,
  exact first-citation order, and no missing, uncited, or duplicated keys
- Mechanical gate: no LaTeX, package, font, overfull-box, unresolved-reference,
  or unresolved-citation warning; no Type 3 fonts; all fonts embedded
- Visual gate: every page inspected at 2x rendering in color, with a grayscale
  contact-sheet pass for figures and line-style legibility
- Scope gate: no MonopolyBench runtime, engine, contract, frontend, or
  benchmark-pipeline code, and no frozen
  `saved_games/*/{run,quality_check}` source file, changed during paper
  finalization; edits are confined to manuscript and paper-support artifacts
