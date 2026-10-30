# Opus phase-3 handoff (steps 11–14)

Opus (claude-opus-5-5), 2026-10-29. My full-scope contribution is complete. All files are in `phase3/opus/`.

No new games, provider calls, prompt, engine or canonical changes, full manuscript, venue selection, commits or pushes were made.

## Read in this order

1. `detailed_outline.md`: the step-14 venue-neutral outline. Each section gives its argument, evidence (R-IDs and files), exhibits, bib keys, alternative explanations and transitions. It ends with open dissent.
2. `experiment_decisions.md`: the step-11 claim-to-experiment matrix. Tiers are A (existing), B (existing-log), C (unpaid new artifacts, needs approval) and D (paid or treatment change, only for stronger claims). It includes the capability–alignment design and a removal rule.
3. `literature.md` + `references.bib` (63 entries) + `comparison.json` (6 close sources × 21 features): step 12.
4. `figure_table_plan.md` and `exhibits/`: step 13.
5. `deployment_residuals.md|.json`: a new existing-log result, reproduced independently by Fable and Astra.
6. `debate.md`: every exchange, with accepted corrections and open dissent. `initial_position.md` is unedited. It was saved before I read any new peer proposal, and it contains claims later corrected in the debate (P2's "structurally cannot", P3's monitorability headline).

## What this contribution adds

### Verified literature that changes positioning

- **The Vending-Bench Arena corpus paper exists.** Li, Petersson, Acquisti and Bakker, arXiv 2608.14825v3; I read §1–7 and App. A and D. It already measures:
  - state-checked false claims;
  - promise follow-through;
  - a cross-model capability test, which is null.

  Its agents' instructions contain no conduct instruction. Its environment is not redistributed.
- **The capability–alignment literature is mixed.** The Arena paper finds no association. Emergent Collusion (2609.24967) finds that within-family capability reaches collusion earlier. MASK and Safetywashing also bear on the question. Our cohort adds no point.
- **AgentMonopoly:**
  - 140 games by the paper's Table 3; its README lists 120.
  - The prompt prohibits public messages that contradict the action.
  - No liquidation step: bankruptcy occurs at cash below $0, per the README.
- **FinBoardBench:**
  - reports a Monopoly "Investment ROI" (§4.3);
  - uses classic bankruptcy;
  - analyses one focal model against fixed opponents.
- **DECE:**
  - no dialogue;
  - harness results are local and bounded;
  - includes baselines.
- **Venue corrections, from OpenReview, PMLR or the arXiv comments field:**
  - Cattle Trade and the two promise papers are workshop papers.
  - τ-bench was published at ICLR 2025.
  - The METR paper's arXiv title is now "…Long Software Tasks".

### New existing-log analyses

- **Outcome dependence.** Seats 1–2 win 14/20. One block is a model sweep, one a seat sweep. Under i.i.d. reference nulls that ignore dependence:
  - P(a prespecified agent wins ≥ 8 of 20) = 0.10;
  - P(any agent wins ≥ 8 of 20) = 0.40;
  - P(seats 1–2 win ≥ 14 of 20) = 0.058.

  So there is no ranking or seat effect. Files: `outcome_dependence.json`, `scripts/outcome_dependence.py`.
- **Cost and usage.**
  - Known OpenRouter cost is $141.71. Opus's figure is a lower bound because 1,600 attempts have no cost recorded.
  - Grok used 4,041 completion tokens per decision; Sol used 128.
  - All four agents ran at reasoning effort "medium".
  - Files: `exhibits/cost_usage.csv`, `cohort_overview.json`.
- **Deployment residual.** The eight entry-buildable trade groups not built in their first management turn break down as:
  - 3 engine defaults (Opus 2, Sol 1);
  - 3 Grok received `end_turn` calls whose content requests a build or build financing (not called lost executable builds);
  - 2 explicit Grok holds.

  Fable (all 63 groups, classified by turn-ending decision) and Astra (final post-turn decision) each reproduced this independently. Astra's F4 now shows the decomposition.
- **Grok `tool_choice="required"`** is confirmed at both run commits (`player_config.py:328–334`). It is the only configured agent with received-name conflicts.
- **The fingerprint diff** between run commits 42f85183 and d6808534 changes campaign-concurrency limits, UI, API plumbing, docs and tests. No engine, prompt, resolver, player-config or OpenRouter-client file changed. No behavioral effect is inferred. The Opus refusal shift falls at the same boundary; report it as a coincidence only.

### Built exhibits

All are in `exhibits/` and carry provenance sidecars where generated.

- `outcome_grid.svg` and `.csv`: faceted single-hue form. A validator check showed four categorical hues fail all-pairs separation in a grid. The figure was rendered and visually inspected.
- `normative_contracts.md` and `.csv`: 3 contracts × 7 behaviors. Fable checked it against the prompt and the Arena sections.
- `affordance_ledger.md`: environment / analysis protocol / unimplemented, using Fable's three-layer split.
- `cost_usage.csv`.

### Challenges that changed peer exhibits

Astra adopted the following:
- the F4 residual decomposition;
- the F5 re-encoding: winner facet, inherited marker, elimination ring, instead of model colour;
- F8 expanded to three chronologies;
- the one-based seat convention.

Still open: the F6 G12 Sol marker renders washed out under a label box (S7).

## Accepted corrections to my own initial position

- **P2.** "Cannot produce an instruction-violation result" became "applied rule violations are engine-prevented; attempted invalid actions are recorded; the private-honesty norm can be breached in principle but false notes do not identify dishonesty here". This is non-identification, not impossibility (Astra).
- **P3.** Monitorability as a headline was withdrawn. 139 is a diagnostic count. A cross-agent rate is undefined (Fable's channel-table counterexample). The checked received-call conflicts stay in the social chronology (Sol, Fable, Astra).
- **Normative comparison.** "The contracts differ; contradiction is prohibited there and is not the same measured violation here", rather than "all our contradictions are authorized" (Sol).
- **G13 d251.** Astra's literal paraphrase was right; our phase-2 "inheritance windfall" is an interpretation. The buyer also opened at $130 itself.

## Open dissent and integration notes

1. Abstract scope: Sol allows one economic result; I argue for two, alongside the execution qualification. Minor.
2. Sol's bibliography lacks the capability–alignment set and Moloch's Bargain. Mine lacked Sol's two commitment preprints, which I verified and added (2610.01045 v2 title drift noted). Integrate both.
3. Placement of the cost table: §5 context (mine) or an appendix.
4. Naming: "Gemini (Argon)" at first mention, then "Gemini".
5. The F6 rendering fix is pending.

## Original-check limits

- **Methods claims** about competitors come from full-text sections I name. Many other sources were checked at abstract or metadata level only, and each is labelled as such.
- **Venues taken only from an aggregator** are marked unverified: *Patterns*, TMLR, *Nature Human Behaviour*, NeurIPS for Motwani, UIST, ACL for Market-Bench.
- **The Arena and VB2 pages** were read through a summarizing fetch. Their numbers are page values as of 2026-10-29.
- **Unverified and not to be cited:** "Soltes et al. 2026" and the HBS/Andon working paper.
- **DBLP** blocked automated queries, so venue checks used OpenReview and proceedings pages instead.
- **Phase-2 numbers (R01–R25)** are used as audited inputs. I did not re-run every phase-2 reducer or branch.
- **The deployment residual** reads only the owner's resolved decisions in that turn. Content is quoted solely to establish disagreement with the applied action, not intent.
- **Communication with Sol.** Sol had finished before my residual message, so that message was not delivered and was not re-sent as a new task. My comparison of Sol's final package is recorded in `debate.md`.

## Reproduction (from repository root)

```sh
O=docs/research_raw/paper_phase3_2026-10-29/opus
python3 -I $O/scripts/cohort_overview.py saved_games $O/cohort_overview.json
python3 -I $O/scripts/outcome_dependence.py $O/cohort_overview.json $O/outcome_dependence.json
python3 -I $O/scripts/build_outcome_grid.py $O/outcome_dependence.json $O/exhibits
python3 -I $O/scripts/deployment_residuals.py . $O/deployment_residuals.json
python3 -I $O/scripts/build_bib.py $O/arxiv_metadata.json $O/references.bib
python3 -I $O/scripts/build_comparison.py $O/arxiv_metadata.json $O/comparison.json
```

`arxiv_metadata.json` is the frozen parse of the arXiv abstract pages fetched on 2026-10-29, with each page's hash recorded. Refetching changes the snapshot. `scripts/arxiv_meta.py` and `scripts/html2txt.py` re-parse locally downloaded pages.
