# Figure and table plan

Sol, 2026-10-29. Main-text economics and social evidence remain substantial. Measurement conditions qualify affected findings. They should not displace the subject with a gallery of software defects. All numerical exhibits use game dollars, not actual USD. Event sequence, global turn, own turn, decision and attempt are distinct units.

Three useful alternates are already generated and visually inspected in [exhibits/](exhibits/). [make_exhibits.py](make_exhibits.py) recreates PNG/SVG assets and CSVs from audited JSON, with semantic assertions. [manifest.json](exhibits/manifest.json) has exact input/output SHA256 values and upstream per-game digests. [planned_source_manifest.json](planned_source_manifest.json) supplies hashes for the additional proposed exhibits. Existing phase2 originals remain unchanged. Generation here verifies reporting transformations; it does not repeat every upstream engine/semantic audit.

Use `uv run --with matplotlib --with pillow python docs/research_raw/paper_phase3_2026-10-29/sol/make_exhibits.py` from the repository root. Literal captions for generated assets also live in the manifest. Inspect the exported asset at its intended paper width before final typesetting. SVG text stays text for editing; PNGs are standalone publication assets.

## Core figures

### F1. Instruction, opportunity, applied behavior, consequence and alternatives

Purpose: make the capability/conduct inference chain a main analytical exhibit. Put five columns across the page; under each distinguish the canonical record from an analyst inference. Add a branch for available explanation channels, with no arrow asserting that they determine hidden intent.

Sources: actual `python/packages/arena/src/monopoly_arena/player_config.py:SYSTEM_PROMPT_V1`; phase1 `astra/visibility_manifest.json`, `astra/memory_audit.json`; phase2 `core_review/astra/claims.md`, `sol/g13_omission_check.json`, `sol/received_name_conflict_audit.json`, `astra/g12_channel_liquidation_check.json`. IDs: G13d251/252/253 and G12d249. Units are instruction clause, decision, proposition, received/applied action, local consequence. Digests appear in planned-source manifest; packet/line hashes remain in reports.

Caption: "Evidence required for a conduct judgment. Instructions define the norm; delivered observations and legal choices establish the opportunity; received and applied actions establish conduct; events establish local consequences. Recorded explanations and recipient responses help distinguish interpretations but do not reveal unique hidden intent. A checked local alternative is not an alternate game outcome."

Audit: quote the exact normative clause; distinguish empty from unreturned text; use d251 as the earlier G13 buyer rationale, not the erroneous d225; ensure chronology is topological. Do not collapse failure to execute an action into an intended deviation.

### F2. Outcomes by seed block and seat rotation

Ready alternate S1, [PNG](exhibits/s1_seed_rotation.png), [SVG](exhibits/s1_seed_rotation.svg). Input phase2 `core_review/sol/corpus_economics_audit.json:design`, compared with saved configs by the upstream audit. Cell text names game, winning configured agent, seat and global turns. Each seed is a row; each cyclic rotation is a column. No ranked bars or standard errors from decisions.

Caption: "Twenty completed games, grouped by five seed blocks and four cyclic seat rotations. Cells report the winning configured agent, seat and game turns. Shared seeds do not produce identical opportunities; one observed trajectory occupies each cell. These are cohort outcomes, not an intrinsic model ranking."

Audit: twenty unique games, four per seed, each model five times per seat;8/7/3/2 tally; distinguish fingerprint boundary at game5 in methods rather than color-mapping it as causal treatment. Final inspection changed two-line cell text to three lines to prevent overlap.

### F3. Longitudinal economic paths

Main proposal: G19 alongside trade-free G14/G15. Four player lanes per game with cash in dollars and marks for acquisition, group completion, first own spend, sale, elimination and estate. Avoid a second axis called liquid net worth unless exact valuation semantics are stated. Cash can be plotted directly; accessible financing needs phase-specific legal computation. Appendix should keep all twenty complete trajectories, not only winners.

Actual sources: canonical `events.jsonl` and configs reached through the source_run field in phase1 `astra/review_packets/game-19-part-001.jsonl` and corresponding G14/G15 packets. Source IDs and canonical event digests are in phase2 Sol `corpus_economics_audit.json:source_hashes`; per-unit `rent_events`, `first_complete_route`, `first_own_spend_event` link the selected trajectory. The root synthesis must resolve each packet's `source_run` before rendering rather than globbing the first saved game with a matching label.

Ready useful subset S3, [PNG](exhibits/s3_g19_dark_blue.png), [SVG](exhibits/s3_g19_dark_blue.svg), contrasts G19 dark-blue spending units p3 and p1. Both share event-order and dollar scales. Actual values are$1,200 spend/$600 sale/$175 paid rent versus$2,000/$0/$1,400. This subset is not a replacement for a full economic trajectory.

Caption for full proposal: "Cash and selected asset events over the complete observed trajectories. Acquisition, spending, realized receipts and creditor transfers occur at different times. Event marks identify historical transitions; they do not estimate the causal contribution of a strategy to winning. Trade-free winners remain in the comparison."

Audit: starting cash and every cash delta reconcile to terminal summary, eliminated players stop at actual elimination, rent paid excludes unpaid debt, event marks use global turns without assigning the same x to unrelated decision counts. For S3 lines stop at last paid-rent event, not end of ownership; the caption says so.

### F4. Construction outlay and paid-rent windows

Ready alternate S2, [PNG](exhibits/s2_spending_windows.png), [SVG](exhibits/s2_spending_windows.svg), [data](exhibits/spending_units.csv). Sources phase2 Sol `corpus_economics_audit.json:spending_units` and Astra `development_aggregation_check.json:summary,units`. Unit is game/player/color with positive own house or hotel spending. Marker indicates whether an inherited deed is present at first own spend. No diagonal labeled profitability, no regression implying independent observations.

Caption: "Each point is one game/player/color group with positive own house or hotel spending. Paid developed rent is shown after the first own expenditure; triangles contain an inherited deed at that point. Totals compare this window with whole-game receipts. The450-dollar difference is pre-spending income from inherited G2 light blues. Paid rent excludes unpaid bankruptcy debts. Neither window is incremental return; inherited improvements, salvage, acquisition cost, timing and terminal censoring remain separate."

Audit:103 units, outlay103450, whole receipts93000, post-first-spend92550,40 zero receipts,58 winner units. G10 hotel-only unit included. Exact overlaps in the scatter mean fewer visible symbols than103; data retain every row, and marker jitter is not introduced. Companion table may list overlap multiplicities if typesetting obscures zeros. Revised x ticks and relocated legend after visual inspection.

### F5. Financing at elimination and actual rescue

Proposal: one all60 classification strip and four detailed rows, plus an actual G20 rescue. Sources phase2 `opus/bankruptcy_bounds.json`, `sol/elimination_upper_bounds.json`, `astra/g07_hotel_lock.json`, `astra/g12_channel_liquidation_check.json`, `sol/g20_sample_financing_checks.json`. The classification partitions60 into56 below a generous bound, three exact own-action payment routes and one hotel stock lock. Dollars on all axes; endpoints named current-debt payment or nominal upper bound.

Caption: "Local financing tests at applied elimination states. Fifty-six debts exceed even a full liquidation bound. Three states admit a legal own-action route paying the current debt. One nominally solvent estate is inaccessible under hotel/house-stock rules. Feasible payment does not establish optimal survival, a deliberate surrender or a counterfactual winner. G20 separately shows an actually executed rescue."

Audit: declared and automatic eliminations both included; omit no automatic marker; do not stack accessible and nominal values as additive resources; retain G12d249's channel conflict and G7's earlier management opportunity as distinct conditions.

### F6. Social chronology and case contrasts

Proposal: three panels minimum, G13 omission/prior motive, G4 or G6/G19 correction-with-settlement, G11 echo/correction/rejection. G18 offer withdrawal and G20 disclosure can be a fourth panel or a compact companion table. Five lanes per decision show public message, applied private note, non-applied content, provider text and applied tool. A separate marker shows actual recipient exposure. Never equate a speaker event with delivery.

Sources phase2 `sol/g13_omission_check.json`, `astra/g13_claim_checks.json`, `sol/g04_uptake_boundary_check.json`, `astra/g06_claim_checks.json`, `astra/g19_claim_checks.json`, `sol/g11_social_channel_checks.json`, `astra/g18_claim_checks.json`, `sol/additional_social_channel_checks.json`. All planned sources verified for existence; exact packet/line/decision references and hashes are in those reports. Unit is a temporally scoped proposition or assurance and its recipient response.

Caption: "Selected source-checked communication episodes. Misleading framing, exact exposure, recorded response and applied settlement are separate observations. The G13 buyer already articulates an insurance motive before the seller's focal framing. Other recipients correct a premise while accepting, or transiently echo it before rejecting. These contrasts neither estimate prevalence nor identify a causal persuasion effect. Public deception is allowed by the evaluated prompt."

Audit: final descriptions must match the full original bundles; short excerpts must preserve referents, conditionals and temporal order. Distinguish unavailable/unreturned, deliberately empty and action-only text. Preserve ownership errors elsewhere in a returned account without erasing the checked proposition. Use case contrasts, not experimental negative controls.

## Core and companion tables

| ID | Purpose, actual input and units | Caption text and verification |
|---|---|---|
| T1 | Rule/configuration ledger. `docs/benchmark_audit_fixes.md`, board JSON, saved run configs, phase2 `sol/corpus_economics_audit.json:design`. Rule clause and affected action slot | "Declared implementation and study settings. Rules that affect finance, access and estates define this cohort's economy." Check code/settings against documented variants; never fill gaps with remembered tabletop rules |
| T2 | Measurement glossary. Final phase2 claims and reducer methods. Decision/attempt/turn/deed/group/ownership interval/spending unit/settlement/proposition | "Definitions and denominators used in this study." Check each plotted quantity has exactly one defined unit and time window; distinguish canonical record from semantic code |
| T3 | Measurement conditions. Phase1 attempt inventory and phase2 recovery, name-conflict and negotiation audits. Attempt, chain, decision and affected initial-prompt union | "Configured response and observation conditions affecting interpretation." Report 1,605 refused attempts versus 1,604 first-attempt recovery chains, 139 name conflicts/15 equal parsed arguments/5 literal matches, and 2,054 affected prompts. No component-source or performance-effect claim |
| T4 | Recovery allocation. Phase2 `sol/build_recovery_audit.json:summary,defaults,uneven_rows`. Rejected decision and successful recovery | "Some-build recovery, exact purchase preservation and same-turn target attainment are distinct outcomes."19/29/5/61 rejection decisions;18/25/5/0 resolve;12/5/0 change quantities among successes. Check model mapping, hotel entries and chain order |
| T5 | Four local finance rows. Sources listed F5. Debt, nominal bound, executed route and endpoint in dollars | "Current-debt routes and a stock lock at exact historical prefixes." G12d190$500, G12d249$250, G17d234$550, G7d339$750. Never call all three the same omitted-mortgage mechanism |
| T6 | Acquisition and estate concentration. Phase1 `sol/results.json:deed_routes,group_routes`; phase2 economic audits. Deed transfer, group completion, elimination and winner spending group | "Acquisition routes and ending concentration use different units." Reconcile475/72/207/397 deeds,16/9/63/121 completions,58/34/30 winner spending groups and54/60 creditor events. Separate terminal19/20 and nonterminal35/40 |
| T7 | Negotiation profiles. Ready `exhibits/negotiation_denominators.csv` from Astra `negotiation_units.json:summary.initiation`. Own turns/decisions/proposal actions | "Initiation propensity and intensity describe configured-agent trajectories under endogenous opportunities." Absolute numerators and denominators accompany rates. Acceptance counts are accepting actors, not bilateral participations |
| T8 | Norm/opportunity/action/consequence/alternatives. Sources F1/F6 plus actual instruction. Proposition or local decision | "Norm-relative claims supported by the current record." Include rows for permitted misleading frame, exact payment route, contradictory received action, changed offer and disclosure. Private-note falsity alone is not proven dishonest intent |
| T9 | Affordance ledger. Verified implementation, measured findings, proposed treatment. Feature and possible claim | "What is implemented, measured and proposed for future capability/alignment studies." Never mark training adapter, predictive monitor, honesty treatment or binding contract protocol as implemented without code evidence |
| T10 | Primary-source comparison. `comparison.json`, `source_manifest.json`, `literature.md`. Exact version, section, task/contract/evidence type | "Comparison with inspected primary sources. Unreported in inspected sections does not imply absent." Include Arena paper v3 and page separately; AgentMonopoly paper140 versus README120; no first/only claims |
| T11 | Claim sufficiency. `experiment_decisions.md:C01-C24`. Claim and evidence requirement | "Existing support, saved-log analysis, optional validation and experiments required only for stronger claims." Tie every experiment to an estimand, no generic request for more games |
| T12 | First-management resolution, Fable's `../fable/exhibits/first_management_causes.json` and `.csv`. All 63 trade-completed groups; entry-buildable and legal-at-any-point subsets reported separately | "Observed first-management resolution combines legal availability, attempts and applied termination. Counts are classifications of the recorded window, not causal effects or strategic preferences." Totals are 43 built, nine never legal in the observed window, three defaults after refusal, one other default, four received conflicts and three valid ENDs. Check all63 row joins and ending decisions. Grok's entry residual is three conflicts/two valid ENDs; legal-in-window residual is four conflicts/two valid ENDs. Content plan legality remains a separate test, especially G12d166 |

## Additional alternate worth considering

A stock trace for the nine zero-stock games contextualizes G7 and retains nonbinding motives. Fable has now built `../fable/exhibits/house_stock_grid.png`, `house_stock_series.csv` and `house_stock_report.json`. Sol checked that the report totals 6,989 matched decision requests, zero discrepancies and the same nine zero-stock games. The event reconstruction and original matching are Fable's checks, not Sol's independent replay. Its unit is bank houses at canonical event boundaries; hotel conversions produce upward stock steps. Overlaying intended demand remains a separate coding task. A robust immediate-expansion diagnostic restores the exact prefix and executes one-house candidates with only stock relaxed, then compares historical legality. It does not measure desire, prior desire revealed by later uptake, or retention-caused denial. Hotel downgrade belongs to a distinct liquidation series.

A capability/conduct frontier figure is not warranted by current data. Replace it with the implemented/measured/proposed ledger, keeping axes and scoring hypothetical if a prospective design diagram is used. This protects the central research question without drawing an empirical curve that has not been measured.
