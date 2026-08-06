# MonopolyBench paper presentation plan

Date: 2026-07-28

Scope: paper presentation architecture only. This plan does not change the manuscript, figures, benchmark code, saved runs, quality checks, or analysis data.

Evidence basis:

- `AGENTS.md`
- `monopolybench_ieee_draft_v0_1.tex` and the current 9-page integrated PDF
- `docs/research_raw/monopolybench_research_handoff_2026-07-28.md`
- `docs/research_raw/monopolybench_eight_run_ledger_2026-07-28.csv`
- `paper/figures/architecture.pdf` and `.png`
- `paper/figures/run273_house_lock.pdf` and `.png`
- Read-only checks of the standardized Run 115 and Run 273 analysis tables/review reports to resolve figure definitions and captions

## 1. Presentation thesis

The strongest 8-10 page paper is a benchmark-and-measurement paper, not an eight-game leaderboard. Its visual hierarchy should make three claims easy to verify:

1. MonopolyBench separates legal state transition from model choice and records the complete evidence chain.
2. The eight audited games validate the measurement surface and expose named mechanisms, with explicit replay and design limits.
3. A balanced seed-seat protocol is required before population-level model comparison.

Every main-paper figure or table should answer one of those claims. Per-player scorecards, long metric inventories, and exploratory plots belong in the appendix or artifact package.

## 2. Recommended main-paper visual set

| Order | Item | Format and target footprint | Main message | Priority |
|---|---|---|---|---|
| Fig. 1 | Execution, evidence, and replay boundaries | Two-panel `figure*`, full width, 0.45-0.55 page including caption | Only the engine mutates state; frozen artifacts support two distinct replay checks | Required |
| Table I | Positioning against adjacent benchmarks | `table*`, full width, at most 10 rows and 7 compact feature columns, 0.35-0.45 page | The contribution is a combination of instrumentation properties, not a broad "first" claim | Required |
| Table II | Audited eight-game corpus | `table*`, full width, 0.45-0.55 page | Exact evidence population, reliability denominators, cost, and replay status | Required |
| Fig. 2 | Run 273 finite-house mechanism | Two-panel `figure*`, full width, 0.60-0.70 page including caption | A replay-clean trajectory couples economic state to a finite shared resource without asserting population-level causality | Required |
| Fig. 3 | Run 115 reliability-to-outcome chain | Single-column vertical flow or compact full-width horizontal flow, 0.30-0.40 page | Strategic intent, serialization validity, fallback, and economic effect are distinct | Required |
| Table III | Claim gates | Single column if legible; otherwise `table*`, 0.25-0.35 page | State, provenance, case-study, and ranking claims require different evidence | Required |
| Table IV | Primary full-study estimands | Compact five-row table, 0.30-0.40 page | The future leaderboard protocol has predeclared units and uncertainty | Main text at 9-10 pages; appendix at 8 pages |

Do not add separate main-paper figures for rent, development, trade networks, auctions, latency, and cost. Those are useful appendix views, but together they would turn the main paper into a plot catalog and crowd out the evidence contract.

## 3. Exact main-paper tables

### Table I: adjacent-benchmark positioning

Use the following schema:

| Benchmark | Horizon / termination | Assets and recurring returns | Market mechanism | Language visibility | Legal-action constraint | Replay and per-attempt evidence |
|---|---|---|---|---|---|---|
| MonopolyBench | Long full game; bankruptcy or cap | Transferable deeds, mortgages, buildings, rent, forced liquidation | Purchases, auctions, bilateral trades | Public messages plus logged private rationale | Engine-generated legal action menu | Decisions, attempts, actions, events, snapshots; state and strict-artifact replay; usage and cost |

Candidate comparison rows are CoffeeBench, Cattle Trade, AgenticPay, M3-Bench, DSGBench, Vending-Bench, EconGym, Multi-Stakeholder Negotiation, and prior Monopoly RL. Do not populate those rows from memory or secondary summaries. Each cell must be verified against a primary paper or official artifact and cited at row level. Use `Yes`, `No`, and `NR` rather than checkmarks so the table remains understandable in text extraction and grayscale. Keep "strict artifact replay" separate from ordinary environment reset or trajectory logging.

Proposed caption:

> **Table I. Positioning of MonopolyBench against adjacent economic and multi-agent benchmarks.** Columns report observable benchmark properties, not a quality ranking. `NR` means that the cited primary source does not report the property. MonopolyBench's contribution is the joint presence of a rules-complete asset-and-solvency economy, engine-issued legal choices, public/private language artifacts, per-attempt records, and separate state and strict-artifact replay; no individual column is claimed as unique.

### Table II: audited eight-game corpus

Use a full-width table with grouped narrow numeric columns. Preserve exact model display names, or define short codes immediately below the table and map each code to the exact frozen-manifest name.

| Run | Turns | Winner | Decisions | Attempts | Retries | Invalid | Fallbacks | Cost (USD) | State / artifact replay |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 115 | 115 | Gemini 3.1 Pro Preview | 366 | 377 | 11 | 13 | 2 | 14.61438250 | pass / pass |
| 154 | 154 | Gemini 3.5 Flash | 396 | 401 | 5 | 5 | 0 | 4.65275495 | pass / pass |
| 157 | 157 | Grok 4.3 | 346 | 355 | 9 | 9 | 0 | 4.03655795 | pass / pass |
| 163 | 163 | Claude Opus 4.8 | 364 | 371 | 7 | 7 | 0 | 12.06275605 | pass / pass |
| 166 | 166 | Claude Opus 4.8 | 488 | 502 | 14 | 14 | 0 | 21.91408585 | pass / pass |
| 172 | 172 | Gemini 3.1 Pro Preview | 613 | 631 | 18 | 20 | 2 | 24.60457580 | pass / pass |
| 191 | 191 | OpenAI GPT 5.5 | 583 | 604 | 21 | 23 | 2 | 27.71173045 | pass / fail at seq. 669 |
| 273 | 273 | Gemini 3 Flash Preview | 540 | 549 | 9 | 9 | 0 | 4.24475240 | pass / pass |
| Total | 1,391 | - | 3,696 | 3,790 | 94 | 100 | 6 | 113.84159595 | 8/8 pass / 7/8 pass |

The table note should add the exact corpus total of 20,474,750 recorded tokens. Per-run seed, maximum-turn cap, seat order, and token count belong in the extended appendix ledger because they make the main table too wide.

Proposed caption:

> **Table II. Audited descriptive corpus of eight completed bankruptcy games.** Decisions are engine-produced choice points; attempts include corrective retries; fallbacks are counted per resolved decision, not per attempt row. Costs copy the frozen provider/OpenRouter records. All eight games pass state replay, while Run 191 is state-valid but first differs under strict artifact replay at event sequence 669. The games use unbalanced seats, rosters, caps, and endpoint versions and therefore do not constitute a model leaderboard.

### Table III: claim gates

| Gate | Minimum evidence | Claim allowed now | Corpus status |
|---|---|---|---|
| State-valid mechanism | Applied action and event linkage plus passing state replay | A named mechanism occurred in a specified trajectory | 8/8 games pass |
| Strict provenance | Passing strict artifact replay, including observational provenance fields | Exact artifact-level equivalence | 7/8 pass; Run 191 first differs at seq. 669 |
| Single-game case study | Named run, exact decision/event IDs, complete artifacts, and reviewed evidence | Bounded interpretation of that case | 8 exhaustive review packages |
| Population or ranking | Balanced seeds and seats, fixed roster/version/protocol, and game-level uncertainty | Model comparison, prevalence, or rank probability | Not met by the selected corpus |

Proposed caption:

> **Table III. Evidence gates for MonopolyBench claims.** State replay, strict artifact replay, case-study interpretation, and population-level comparison answer different questions. Run 191 passes the state and case-study gates with an explicit provenance caveat; it must be neither discarded from all mechanism analysis nor promoted to strict-artifact-clean evidence.

### Table IV: preregistered primary estimands

| Estimand | Independent unit | Reported summary | Uncertainty / safeguard |
|---|---|---|---|
| Win probability within a fixed roster and protocol | Seed-seat game block | Game-conditional winner or finish-order contrast | Seat effects plus block bootstrap or design-aligned permutation |
| Bankruptcy / survival distribution | Player-game within a shared game | Survival curve and bankruptcy mechanism | Right-censor capped survivors; cluster by game |
| Normalized wealth or productive-capital trajectory | Player-game trajectory | Length-normalized area under a documented balance-sheet or productive-capital curve | Game/block bootstrap and valuation sensitivity |
| First-attempt legal-action reliability | Decision, summarized within game | Decisions valid on attempt 0 / all decisions | Keep retry recovery and fallback rate separate; cluster by game |
| Cost | Attempt, decision, and player-game | Cost per valid decision and per completed player-game | Report distributions, incomplete runs, and missing provider fields |

Proposed caption:

> **Table IV. Primary estimands for the balanced full-game study.** The independent replication unit is the game or randomized seed-seat block, not a turn, decision, attempt, or player row treated in isolation. Secondary negotiation, auction, liquidity, mortgage, rent, and communication measures remain exploratory families.

## 4. Figure architecture and captions

### Fig. 1: execution and replay contract

Recommended composition:

- Panel (a), online execution: contracts -> authoritative engine -> decision plus legal actions -> arena/OpenRouter -> validation -> corrective retry or deterministic fallback -> applied action -> engine events and snapshot.
- Panel (b), evidence and verification: telemetry freezes decisions, all attempts, applied actions, events, snapshots, prompt/response artifacts, usage, and cost. State replay compares state-relevant transitions. Strict artifact replay additionally compares provenance fields. The API reads the live server stream; the render-only UI does not receive its live state from the frozen package.
- Draw a complete enclosing boundary around deterministic engine transitions. Do not represent it with only a dashed top edge.
- Show provider sampling, routing, latency, and wall-clock time outside the deterministic boundary.

Proposed caption:

> **Fig. 1. MonopolyBench execution, evidence, and replay boundaries.** (a) The authoritative engine emits each decision and its explicit legal actions. The arena queries an LLM through OpenRouter, validates the response, performs the configured corrective retry when needed, and otherwise selects a deterministic fallback; only the engine applies the resulting action and changes state. (b) Telemetry freezes decisions, attempts, actions, events, snapshots, prompts/responses, usage, and cost. State replay compares state-relevant transitions reconstructed from the applied action sequence, whereas strict artifact replay also compares observational and provenance fields. Provider sampling, routing, latency, and wall-clock time are recorded but do not drive engine progression. The API streams server snapshots/events to a render-only UI.

### Fig. 2: Run 273 finite-house mechanism

Retain the paired trajectory and bank-inventory concept, but revise the graphic before publication:

- Remove the title inside the plotting area; the LaTeX caption supplies the title.
- Define accounting net worth in the caption as `cash + property value + building value - mortgage liability`.
- Rename the gray band from "house-lock window" to "lock construction and interruption, turns 167-180." The standardized start-of-turn inventory is 11 houses at turn 167, 2 at turns 168-171, 0 at turns 172-173, 2 at turns 174-180, and 0 again from turn 181 until a later interruption.
- End each net-worth trace at bankruptcy, or use a clearly labeled post-bankruptcy convention. Flat zero lines currently look like continuing observations.
- Direct-label traces near their rightmost valid point and use dash/marker redundancy. Do not rely on red, orange, blue, and green alone.
- Keep the two panels aligned on playable-turn index. The figure must remain full width; it is not legible as a one-column plot.

Proposed caption:

> **Fig. 2. Accounting trajectories and finite bank-house inventory in replay-clean Run 273 (`mock-44910-42ec35c5`).** Top: accounting net worth, defined as cash plus property value plus building value minus mortgage liability, by playable-turn index. Bottom: houses remaining in the bank, out of 32. Dotted lines mark bankruptcy at turns 110 (OpenAI GPT 5.4 Mini), 167 (Claude Haiku 4.5), and 273 (Grok 4.3); Gemini 3 Flash Preview was the last survivor. Shading spans turns 167-180, from the New York exchange and immediate nine-house Orange build through a temporary forced-sale interruption; start-of-turn inventory first reaches zero at turn 172 and returns to zero at turn 181. The alignment illustrates a finite-inventory mechanism in one trajectory, not a population-level causal effect or proof that scarcity alone produced the economic divergence. State replay passes 1,942/1,942 state-relevant events and strict artifact replay passes 4,102/4,102 events.

### Fig. 3: Run 115 serialization and fallback chain

Use a compact decision-local flow rather than a full-game chart:

1. Debt state: Boardwalk rent $1,400; cash $1,203; shortfall $197.
2. Engine menu: sell buildings or declare bankruptcy.
3. Sufficient legal line: sell eight brown houses at $25 each, raising $200 and leaving $3 after payment.
4. Attempt 0: intended sale, schema-invalid.
5. Corrective attempt 1: same intended sale, schema-invalid.
6. Deterministic fallback: declare bankruptcy; immediate elimination and creditor transfer.

The legal line can be a dashed branch labeled "immediate survival only"; do not continue it to a hypothetical winner. The observed path should be solid. Put `dec-000330` and turn 95 in the figure.

Proposed caption:

> **Fig. 3. A decision-local reliability failure changed the applied economic outcome in Run 115.** At turn 95 (`dec-000330`), Claude Opus 4.8 owed $1,400 with $1,203 cash. The engine exposed building sale or bankruptcy; selling eight brown houses for $200 was legal, exceeded the $197 shortfall, and would leave $3 after payment. Both the initial and corrective model attempts selected that line but failed schema validation, so deterministic fallback selected bankruptcy. The bounded counterfactual establishes immediate survival only, not eventual victory. This was one of two fallback decisions among 366 applied decisions in the run; the run contains 13 invalid attempts among 377 attempts.

## 5. Audit of the existing figures

### `paper/figures/architecture.*`

Strengths:

- It visibly centers the authoritative engine and legal-action constraint.
- It distinguishes contracts, arena, telemetry, research package, and render-only UI.
- It already states the important determinism caveat.
- The PDF is vector and the PNG is 2,192 x 1,021 at approximately 300 dpi.

Current publication audit:

- The live API/UI path is now visually separate from the frozen research-package and replay paths.
- State replay and strict-artifact replay are identified as distinct comparison surfaces.
- The top connector labels are separated and no longer overlap arrows or box edges.
- The landscape geometry remains appropriate only at full text width.
- The regenerated figure uses embedded DejaVu Sans Type 0/TrueType fonts; no Type 3 font remains.

Risk of overclaim:

- The wording "deterministic transition boundary" is defensible only around engine transitions conditioned on the applied action sequence. It must not visually enclose provider calls or imply deterministic model regeneration.
- "State and strict-artifact replay" should be two outputs with different comparison surfaces, not a single undifferentiated capability.

### `paper/figures/run273_house_lock.*`

Strengths:

- The shared x-axis makes the resource constraint and player trajectories jointly inspectable.
- Exact bankruptcy markers and the 32-house starting inventory are visible.
- The PDF is vector and the PNG is 2,137 x 1,418 at approximately 300 dpi.
- Run 273 is the longest canonical fully replay-clean case study in the audited corpus.

Remaining publication problems:

- The blue dotted bankruptcy/checkpoint line at index 167 crosses both the upper annotation ("exchange and house-scarcity window") and the lower annotation ("bank supply reaches 0"). Move both annotations horizontally away from 167 or add a small opaque white bounding box.
- GPT-5.4 Mini and Gemini 3 Flash are both solid traces. Their colors differ, but grayscale and color-deficient readers do not receive a fully redundant identity encoding. Give one trace a distinct dash pattern or marker.
- Bankrupt-player series continue at zero. The dotted bankruptcy markers and caption explain this, but terminating each series at its bankruptcy checkpoint would remove any residual suggestion that post-elimination net worth continues to be measured.
- The regenerated figure uses embedded DejaVu Sans Type 0/TrueType fonts; no Type 3 font remains.

Risk of overclaim:

- The figure can support the occurrence of a finite-inventory mechanism and the exact episode. By itself it cannot prove that the lock caused victory, that the strategy is generally optimal, or that selective public framing was deceptive.
- Avoid captions such as "dominant economic signal," "decisive proof," or "caused economic divergence." The reviewed case study may discuss an observed mechanism, but the plot does not identify a population-level causal effect.

## 6. Current integrated-manuscript presentation audit

Audit target: the 9-page PDF compiled 2026-07-28 20:41:07 PDT, SHA-256
`68E74CF0FA22589D380EC773361D60813B22FFFE2FFEFCA75815BD3685FEB956`.
Every page was re-rendered at 150 dpi; pages 4, 6, and 7 were also inspected
at 300 dpi.

Resolved in the current artifact:

- The architecture connector labels are separated and legible.
- Both included figure PDFs use embedded Type 0/TrueType fonts; a recursive font-resource scan found no Type 3 or unembedded font.
- Tables II and III use readable footnote-size text without clipping or cell collisions.
- The final bibliography page is column-balanced.
- Full-width floats remain with their captions and appear near their first discussion.
- No visible TODO, placeholder, draft-colored text, clipping, orphaned heading, or margin overflow remains.

Remaining defects, in priority order:

1. **Submission-blocking typography/toolchain mismatch.** The build log reports
   `TU/ptm` shapes unavailable and substitutes `TU/lmr/m/n`; the PDF font
   inventory confirms Latin Modern Roman regular throughout the body, with no
   bold or italic Latin Modern shapes. This means the document is fully
   embedded but does not preserve the requested Times family or all emphasis.
   Compile the unchanged source with the standard `pdflatex`/`latexmk -pdf`
   IEEEtran path. If XeLaTeX is mandatory, explicitly configure a complete
   Times-compatible OpenType family and recheck every bold, italic, small-caps,
   and monospaced use. The final log should contain no "font shape undefined"
   warnings.
2. **Figure 2 annotation collision.** On page 7, the blue dotted line at
   checkpoint 167 intersects the text in both panels. Move the annotations
   away from the line or give them opaque white bounding boxes.
3. **Corpus-table semantics.** On page 6, Table II labels its first column
   `Run`, while the caption defines that column as the engine seed. Rename the
   header to `Seed`; the total-row label may remain `Total`.
4. **Grayscale redundancy.** Figure 2 uses solid lines for both GPT-5.4 Mini
   and Gemini 3 Flash. Give one a distinct dash or marker so identity does not
   depend only on orange versus green.

The log has no overfull-box warning. Its remaining underfull-box messages are
not accompanied by visible gaps severe enough to require layout surgery.
Page 9 has expected unused lower-page space after balancing a short terminal
bibliography and does not need filler.

## 7. Page-level information hierarchy

Target nine pages inclusive of references, with a hard ceiling of ten. Treat one page as two column-equivalents.

| Page | Content | Float budget and hierarchy |
|---:|---|---|
| 1 | Title, abstract, introduction, three concise contributions | No float. Abstract leads with instrument, audited corpus totals, and non-leaderboard caveat. |
| 2 | Related work and novelty boundary | Table I across the top or bottom. Text explains the combination claim and avoids "first." |
| 3 | Benchmark task, decision loop, architecture, artifact contract | Fig. 1 across the top. The text below defines decisions, attempts, actions, events, snapshots, and the two replay checks. |
| 4 | Measurement philosophy and audited evidence population | Table II across the top; Table III below or in one column. Explain why turns/decisions are dependent observations, not independent replications. |
| 5 | Replay-clean trajectory case study | Fig. 2 receives most of the page. Limit prose to the turn-167 trade/build chain, inventory facts, and bounded interpretation. |
| 6 | Reliability and a second mechanism case | Fig. 3 plus a short Run 191 replay-caveat paragraph. Negotiation-to-conversion evidence gets one compact paragraph; detailed episode matrices move out of the main text. |
| 7 | Balanced full-study protocol and micro-scenario bridge | Table IV if space permits. Show seed blocks and seat rotation in text or a tiny schematic, not an additional large figure. |
| 8 | Discussion, limitations, ethics, artifact availability, conclusion | Consolidate limitations into 3-4 high-value paragraphs. Start references if possible. |
| 9 | References | No author notes or candidate appendices. |
| 10 | Optional overflow only | Use only if venue permits and references or Table IV cannot fit legibly. Do not fill it with exploratory plots. |

Eight-page fallback:

1. Move Table IV to the supplement and summarize its five estimands in prose.
2. Render Fig. 3 as a compact one-column flow.
3. Shorten the benchmark comparison matrix to the six closest comparators.
4. Merge discussion, ethics, availability, and conclusion.
5. Never reclaim space by shrinking figure text below 8 pt, scaling tables blindly, or removing replay/design caveats.

Ten-page expansion:

- Keep Table IV in the main text.
- Add a compact three-row mechanism/counterexample table for Runs 157, 163, and 273.
- Add no more than one extra evidence-rich case panel. Prefer negotiation-to-conversion over a generic cost bar chart.

## 8. Appendix and supplemental hierarchy

Move the following out of the main paper:

1. Extended eight-run ledger: exact seed, maximum-turn cap, full seat order, per-run tokens, full-precision cost, and replay detail.
2. Per-player cash, net-worth components, property count, houses/hotels, and mortgage liability.
3. Rent collected/paid trajectories and per-player rent tables.
4. Negotiation, auction, and mortgage episode tables with explicit denominators.
5. Bankruptcy-window timelines and immediate-menu avoidability proofs.
6. First-attempt validity, retry-recovery, and fallback matrices by decision type.
7. Per-model token, cost, latency, missing-usage, and incomplete-run distributions.
8. The full mechanism/counterexample matrix and evidence-indexed case packets.
9. Artifact manifests, tree hashes, source commit, generated-output manifest, and ZIP equivalence.
10. Micro-scenario category definitions and full/full-micro concordance plots after the manifest is frozen.

Every appendix plot must name its generated source table. Every qualitative row must resolve to a decision/event ID or evidence-index entry.

## 9. IEEE/AAAI readability and accessibility checks

- Place the two existing multi-panel figures only at full text width.
- Use vector PDF for figures. Regenerate Matplotlib PDFs with `pdf.fonttype = 42` and `ps.fonttype = 42`, or use LaTeX/PGF text. Confirm that the final PDF contains no Type 3 fonts.
- Use at least 8 pt text at final placement, 0.8 pt strokes, and markers that remain visible in print. Do not use `\resizebox` to hide an over-wide table.
- Use a color-vision-safe palette and redundant encodings: color plus dash pattern plus direct label or marker. Test grayscale.
- Remove titles from inside plots. Use panel labels `(a)` and `(b)` in a consistent top-left position.
- Use `booktabs`, no vertical table rules, decimal alignment for money, and explicit units in headers.
- Define every abbreviation in the caption or table note. Captions must state the population, denominator, replay status, and whether a result is descriptive.
- Cite each float in the text before it appears. Keep the caption on the same page and avoid a full-width float several pages after its first reference.
- Use exact frozen-manifest model names. If short codes are necessary, provide one mapping and use it consistently.
- Provide concise alt text in the paper source or submission metadata where supported. The caption should remain independently understandable to a reader who cannot distinguish color.
- Verify that URLs, underscores, code identifiers, and dollar signs do not create clipping or overfull boxes.

## 10. Full-PDF visual inspection checklist

### Content and claim checks

- [ ] PDF is 8-10 pages under the target venue's counting rule.
- [ ] No `TODO`, placeholder, red draft text, candidate-author note, or internal planning appendix remains.
- [ ] Abstract, Table II, and conclusion all describe the eight games as audited descriptive case studies, not a leaderboard.
- [ ] Run 191 is labeled state-valid and strict-artifact-failed at sequence 669 everywhere.
- [ ] Run 273 is labeled the longest canonical fully replay-clean case study, not the only trustworthy run.
- [ ] Every result table states its evidence population and denominator.
- [ ] Every numeric cell is checked against the eight-run ledger or a named generated table.
- [ ] Every qualitative mechanism names a run and resolves to decision/event evidence.
- [ ] Display names exactly match frozen manifests.
- [ ] No caption claims population-level causality, prevalence, deception, collusion, or model superiority.

### Rendering checks

- [ ] Compile at least twice; references, figure numbers, and cross-references resolve.
- [ ] Render every page to PNG at 150 dpi for full-page inspection and 300 dpi for float inspection.
- [ ] Inspect every page at fit-to-page and every figure/table at 100 percent zoom.
- [ ] No clipped text, overlapping labels, overfull boxes, broken glyphs, black squares, or orphaned captions.
- [ ] No table uses text below 8 pt at final size.
- [ ] Fig. 1 arrows have unambiguous directions and do not cross labels.
- [ ] Fig. 2 labels, line identities, bankruptcy markers, and the house-inventory trace remain legible in grayscale.
- [ ] Fig. 3 clearly separates the observed fallback path from the bounded immediate-survival branch.
- [ ] Full-width floats fit within both margins and do not leave a nearly empty column.
- [ ] Captions are readable and remain with their figures/tables.
- [ ] Page breaks do not separate a section heading from all following text.

### PDF and venue checks

- [ ] All fonts are embedded; `pdffonts` reports no Type 3 fonts.
- [ ] Page size, margins, columns, headers/footers, and page numbering match the selected IEEE or AAAI template.
- [ ] Hyperlinks work and do not print as colored boxes unless the venue permits them.
- [ ] References are complete, primary-source titles/URLs are verified, and no author field contains `[TODO]`.
- [ ] The PDF is searchable; model names, identifiers, and table text extract correctly.
- [ ] A grayscale print or print-preview remains interpretable.
- [ ] File size and image resolution meet the venue limit; raster fallbacks are at least 300 dpi.
- [ ] The final artifact/code availability statement names the version/hash surface used by the paper.

## 11. Cut order if the paper overruns

Cut in this order:

1. Move Table IV to supplement.
2. Shorten the adjacent-work matrix to the closest six benchmarks.
3. Reduce case-study prose, keeping Figs. 2-3 and their exact captions.
4. Merge limitations and ethics.
5. Move secondary metric definitions and the micro-category list to supplement.

Do not cut the corpus denominator, replay split, Run 191 caveat, unbalanced-design caveat, or figure legibility. Those are part of the scientific result, not optional presentation detail.
