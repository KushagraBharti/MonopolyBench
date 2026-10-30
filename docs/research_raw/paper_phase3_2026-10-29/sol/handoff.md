# Sol phase-3 handoff

Steps11–14 are complete for Sol's independent full-scope contribution, 2026-10-29. Start with [detailed_outline.md](detailed_outline.md), then [experiment_decisions.md](experiment_decisions.md), [literature.md](literature.md) and [figure_table_plan.md](figure_table_plan.md). [initial_position.md](initial_position.md) predates reading the three new peer proposals. [debate.md](debate.md) records direct substantive exchanges with Astra, Opus and Fable, accepted revisions, and the remaining emphasis question.

## Durable outputs

- A 24-row claim-sufficiency matrix distinguishes current support, saved-log analysis, optional validation and experiments necessary only for stronger claims. No new paid games are needed for the bounded descriptive paper.
- A 29-record bibliography and 32-record structured source comparison cover every named benchmark and close economic/social/validity competitors, including original Vending-Bench, Vending-Bench2, current Arena, and the Arena communication study v3. [source_manifest.json](source_manifest.json) freezes 32 primary-source texts with URL, timestamp and SHA256. Empty Commitments v1 and the later empirical v2 are separate records. Methods and relevant appendix sections were inspected; this is not a claim to have fully read every source or audited every repository.
- A detailed venue-neutral outline of about3,900 words includes argument, evidence, citations, exhibits, alternatives, transitions, limitations and a prospective capability/alignment/training agenda. It is an outline, not a full manuscript.
- Six core figure specifications and twelve table specifications identify actual source paths, units, caption text, checks and remaining work. Three alternate figures are already generated as PNG/SVG, with two CSV tables and source/output hashes in [exhibits/manifest.json](exhibits/manifest.json). T12 incorporates Fable's first-management resolution table with attribution; the stock-trace proposal now links Fable's completed exhibit.
- [verification.json](verification.json) records zero package-check failures:32 frozen-source hashes,8 figure/data outputs,103 cross-audit spending-unit joins,29 bibliography records and103 exported spending rows. [peer_followup_checks.json](peer_followup_checks.json) recounts Fable's63 resolution rows and stock-report totals without claiming a new original-artifact audit. Local links were checked. All three final PNGs were visually inspected and revised where labels collided.

## Scientific conclusions to carry forward

The paper should study sustained objective pursuit and social conduct together. It should not become finance-only, nor claim the present cohort measures misalignment growth. The supported object is the configured agent and its observed trajectory. Norms, opportunities, applied behavior, consequences and alternatives should be a core exhibit.

An independently specified norm can support bounded descriptive adherence without randomization. A causal comparison or capability/alignment frontier needs controlled opportunities and an independent capability axis. Public deception is authorized here. Neither private-note falsity nor received channel disagreement independently identifies dishonesty.

The proposed method contribution is narrow: restore an exact historical decision prefix, execute an explicitly stated sequence of the acting player's own legal actions, and stop at a local endpoint. This can distinguish applied outcomes, reorderable plans, accessible finance and erroneous labels. It cannot identify a changed game's winner or justify carrying the historical suffix forward.

The social chronologies should remain substantive main-text findings. Preserve the G13 buyer's earlier d251 motive, correction-with-settlement cases and G11 echo-then-rejection. Show channel availability and differences without privileged-intent inference. Action/explanation consistency is oversight-relevant, but139 name conflicts are a diagnostic count rather than139 validated monitor failures. Predictive monitor accuracy is not measured.

## Literature corrections that affect positioning

AgentMonopoly explicitly documents legal actions and deterministic gameplay, links speech/actions/outcomes, and limits explanation interpretation. DECE has replay/state/event records and matched execution-system studies. Cattle Trade has complete transitions and differentiated error policies. The Arena research paper conducts state-grounded communication and follow-through analysis. Broad first-menu, first-replay, first-economic-game and first-grounded-social claims should be removed.

AgentMonopoly appendixA.3 totals140 games; its inspected README table totals120. Preserve the source mismatch rather than deciding which experiments were actually run. FinBoardBench reports Monopoly investment profiles and Acquire monetization/redeployment; per-turn trajectory analysis was not found in inspected sections, which is narrower than claiming it is absent. Venue status is stated only when independently checked; versioned manuscripts and first-party pages remain separate.

## Original checks and limits

Fresh phase-3 work independently fetched and inspected primary-source methods/appendices, checked source/version identities, compared the two phase2 economic reducers at all103 spending-unit rows, asserted plot totals and design structure, generated assets, verified hashes and local links, and inspected all final images. The bibliography deliberately abbreviates long author lists with 'and others' rather than inventing metadata.

I did not rerun all engine tests, all20 canonical replays, every exact-prefix branch or the full original social review in this stage. Those remain attributed phase2 evidence, not claimed new replication. The original G13 omission report was reopened to correct my d225 transcription error to d251 after Fable challenged it. That correction and authorship remain in debate.md. No broad competitor-feature absence or exclusive novelty was verified. No new prevalence codebook was silently applied to the corpus.

In the follow-up, Fable flagged the newer Empty Commitments v2 and supplied the all63 first-management resolution table and stock report. Sol independently inspected the v2 methods/results and annotation appendix, retained v1 with an explicit historical key, and changed outline citations to v2. Sol rechecked the peer-derived table arithmetic, residual ending IDs and report totals; Fable retains authorship of the original reconstruction and category judgments. Grok's residual conflict counts are three of five entry-buildable non-builds and four of six legal-in-window non-builds. No received conflict is automatically a lost executable build.

No paid experiment, prompt/engine/protocol/canonical-game edit, full manuscript, venue selection, commit or push was made. All research deliverables are under this sol directory.

## Reproduction

From repository root run:

```sh
python3 docs/research_raw/paper_phase3_2026-10-29/sol/build_bibliography.py
uv run --with matplotlib --with pillow python docs/research_raw/paper_phase3_2026-10-29/sol/make_exhibits.py
python3 docs/research_raw/paper_phase3_2026-10-29/sol/check_peer_followup.py
python3 docs/research_raw/paper_phase3_2026-10-29/sol/verify_package.py
```

`fetch_sources.py` can refresh first-party pages, but doing so changes a literature snapshot. Preserve this source_manifest and source text as the audited version rather than replacing them during integration. A full benchmark verification is not a substitute for checking source interpretation or visual captions.
