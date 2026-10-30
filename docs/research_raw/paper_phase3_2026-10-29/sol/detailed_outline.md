# Detailed venue-neutral outline

Sol, 2026-10-29. This is a new outline for the completed audited cohort, not a revision of an old manuscript and not a manuscript draft. Citation keys refer to [references.bib](references.bib); L-numbers refer to [literature.md](literature.md). Evidence IDs R01–R25 refer to the final phase-2 Astra ledger. C01–C24 refer to [experiment_decisions.md](experiment_decisions.md). Exhibit IDs refer to [figure_table_plan.md](figure_table_plan.md). No venue, page budget or training-result claim is assumed.

## Proposed argument

Long-horizon agent evaluation should study competent pursuit of objectives and norm-relative conduct in the same persistent environment. Competitive economies make an agent's words and actions consequential for its own future options and other agents' resources. But neither winning nor a plausible explanation identifies the relevant mechanism. MonopolyBench offers an inspectable rule-constrained economy and a complete cohort whose records support economic accounting, source-linked social chronologies and exact local tests of legal alternatives. The current study identifies bounded configured-agent behaviors and limits of attribution. A capability–alignment frontier remains a research question requiring a separately designed capability axis, norm and opportunity distribution.

Do not claim universal novelty for multiplayer economics, legal menus, deterministic engines, replay, financial profiles or skepticism about explanations. Direct competitors already implement or analyze those. The contribution is the specific integrated measurement protocol and the empirical findings it changes, with a release that lets others check those findings.

## 0. Abstract planning card

Open with the problem of evaluating sustained goal pursuit and conduct when actions change future opportunities. State the environment and evaluated unit, four configured agents in twenty completed games across five seed blocks and four cyclic rotations. Name the method: canonical actions/events, delivered information, channel-separated explanations and exact-prefix legal-sequence checks. Select at most one economic and one social result, together with the execution/attribution distinction that qualifies them. Close by stating that the cohort supports descriptive capability and conduct analysis rather than a capability–alignment trend.

Candidate result choices: locally reorderable development plans and current-debt payment feasibility illustrate why applied behavior does not identify strategic preference. Social chronology shows misleading framing, exposure and settlement alongside pre-existing buyer motives or premise correction. A text that mentions only defaults would make the paper sound like an API audit; include an actual economic trajectory or trade consequence.

Evidence gate: all abstract facts must appear in a source-backed main exhibit. Avoid a scalar deception rate, intrinsic provider order, misalignment finding, training benefit, human annotation claim or optimal-policy implication. A four-system win tally can be omitted from the abstract if it distracts from the contribution.

## 1. Introduction: capability and conduct with delayed consequences

Argument: autonomous agents increasingly choose sequences of tool actions while bargaining with parties who have separate goals. A useful safety environment must preserve both task capability and the evidence needed to assess conduct. Capital, property, debt and public bargaining make actions consequential across many turns, while a finite simulator makes facts and legal alternatives inspectable.

First paragraph should state the scientific question without declaring the present games a model of the whole economy. Second paragraph should explain the measurement problem using a compact example: an applied END may be chosen reserve retention, discarded affordable construction, or a received action inconsistent with an explanation. A completed trade may reflect premise acceptance, explicit premise correction, or an earlier independent motive. The same observed endpoint admits different interpretations.

Third paragraph should place the work among direct precedents, especially AgentMonopoly, FinBoardBench, Vending-Bench Arena and its systematic communication study, Cattle Trade and DECE. All are genuine comparators rather than background dismissed as short tasks. Explain which narrower questions remain useful without claiming the paper invents a category.

State three questions. RQ1 asks how configured agents create, finance, use and lose economic position across complete games. RQ2 asks how recorded communication and applied conduct relate to delivered information, the actual instructions and other players' recorded responses. RQ3 asks what a sandbox must preserve and permit to study these questions and, prospectively, capability/alignment trade-offs. State that RQ3 has implemented affordances and design implications; it is not an already measured learning or alignment curve.

Contributions should be concrete. The environment preserves replayable protocol objects. The analysis measures bilateral and longitudinal economic consequences and tests local alternatives. The social review links propositions, exposure, responses and applied outcomes with counterexamples. Validation identifies execution and analyst errors that change conclusions. Put supporting evidence next to each contribution rather than a list of infrastructure adjectives.

Citations: `vending`, `vending2`, `vending_arena`, `arena_paper`, `agentmonopoly`, `finboard`, `cattle`, `dece`, `machiavelli`. Exhibits F1 and T1. Alternative explanation to acknowledge: simulator competence may reflect Monopoly familiarity and game-specific adaptation. Transition: before comparing outcomes, define the economic rules, information and normative contract under which the agents act.

## 2. Environment and the evaluated system

### 2.1 Persistent economy and declared rule variant

Describe acquisition, auctions, group completion, even building, finite stock, mortgages, debt-time liquidation, jail access and creditor estates. Use the authoritative engine and declared variants. The inheritance of developed assets intact is relevant to concentration, and jail-restricted management is relevant to access timing. Do not describe the implementation as fully classic Monopoly or assume a familiar tabletop rule fills a gap.

Explain how a financial action changes future legal options. Selling all buildings can unlock mortgage choices; nominal equity is not automatically spendable. Scarce houses can constrain expansion and hotel liquidation differently. These examples establish why the benchmark can test action sequencing rather than treating the rule system as incidental decoration.

Evidence: `docs/benchmark_audit_fixes.md`, contracts board data, engine decisions, saved run settings; R08–R10/R15–R17. T1 specifies rules and implications. Comparators `agentmonopoly`, `finboard`, `cattle`, `dece`. Alternative: differences in rules explain why cross-paper win or rent numbers are not directly comparable. Transition: the economy alone does not define what information or norms govern the agent.

### 2.2 Observations, memory and normative contract

Describe explicit legal choices, current state, public history, private-note memory and negotiation context. Separate the engine state from what the actor receives at that decision. State the public-deception license and request for truthful private reasoning precisely. The model is directed to win through legal play, while the engine rejects illegal actions. Consequently, an invalid attempted call is not an executed rule violation, and a misleading public price argument is not automatically instruction-misaligned.

Contrast with AgentMonopoly's explicit public/action-consistency prohibition, tau-bench's domain policy and AgentDojo's trust boundary. The claim is not that no alignment question is measurable. The claim is that the norm determines what counts as a violation. Observable conduct can still be analyzed under an independently declared research norm if labeled separately from instruction adherence.

Evidence: phase1 actual system-prompt digest and coverage, delivered-prompt inventory, R18–R24. F1/T2. Citations `agentmonopoly`, `taubench`, `agentdojo`, `machiavelli`, `commitment_standing`. Transition: observations and instructions reach agents through configured response and execution procedures, so those procedures are part of the tested object.

### 2.3 Configured agents and action resolution

Define the unit as model/checkpoint, prompt, memory, tool choice, response handling, retries and deterministic fallback. Record provider refusal conditions without interpreting them as moral opposition. Distinguish 1,605 refused attempts from 1,604 first-attempt recovery chains. State Grok's configured tool choice and channel disagreements without attributing their origin. Explain validation and fallback in one compact diagram.

Keep actual outcomes intact; do not discard difficult records or replace them with a reconstructed intended action. Causal component effects are not estimated by differences across four whole configurations. DECE's matched execution-system study is a direct precedent for the experiments that would be needed. T3 records affected analyses and units. Transition: define what records allow us to reconstruct and test this system.

### 2.4 Research artifacts and replay contract

Snapshots record state, events record transitions, decisions record legal menus and actions record applied moves. Attempts preserve validation, prompt, response, usage and fallback provenance. State canonicalization and deterministic replay scope. Available private/provider text is not a complete internal trace; encrypted and unreturned content remains unavailable. Explain what is already implemented versus proposed, particularly training adapters, oversight agents and future contracts.

Evidence: R01, phase1 manifests and replay tests; phase2 Sol all20 event replay audit. Cite `hal`, `agents_that_matter`, `dece`; shared replay should not be sold as unique. Transition: the next section defines the cohort and analytical estimands, rather than letting artifact volume stand in for independent evidence.

## 3. Cohort, analytical definitions and adjudication

### 3.1 Design and outcome units

Report twenty completed uncapped games, eighty player-games, five seeds with four cyclic seat rotations, one roster, 6,989 decisions and 8,679 attempts. Each model occupies each seat five times. Preserve fingerprints for games1–4 versus5–20 without assuming that a fingerprint difference proves a behavioral treatment. State whether any run ended by cap or bankruptcy using saved summaries.

Show F2/S1 as a seed/rotation grid with winning seat and duration. Report wins as observed outcomes. Matching raw dice does not match the player using each draw, cards, jail or later opportunities. Do not fit decision-level independent tests to model-level claims. If uncertainty is included, explain what it samples, preserve block dependence and avoid implying five blocks characterize all opponents.

Evidence: phase2 Sol `corpus_economics_audit.json:design`; phase1 configurations and shared-stream audit. Citations `dece`, `agentmonopoly`, `metr`. METR's human-time horizon is a different unit. Transition: define the quantities that connect a game endpoint to the path producing it.

### 3.2 Economic and social estimands

Define deed transfer, group completion, first management access, entry-buildable state, construction, own spending, paid rent, unpaid debt, salvage and estate. Each has a unit and temporal window. Report both conditional responsiveness and the full path that created the opportunity. No single monotonic progress score is assumed in a game where completing a set can finance a rival.

For social cases define proposition, subject/time, factual status, speaker record, recipient exposure, recipient response, applied action, consequence and alternatives. A canonical public utterance does not itself establish delivery. A recipient can accept terms while rejecting a premise. A standing offer has conditions and can change; settlement is a structured contract but need not enforce every accompanying verbal assurance.

Evidence: R03–R05/R12–R16/R18–R21; T2 definitions, F1 chain. Citations `agentboard`, `arena_paper`, `cheap_talk`, `when_agents_lie`, `commitment_standing`. Alternative: a precise observable measure may still have weak connection to broad competence or alignment. State that explicitly rather than naming it as a validated trait.

### 3.3 Exact-prefix local tests

Restore a canonical decision prefix. Execute a stated sequence of the actor's own legal actions through the authoritative engine. Keep the original budget and stock unless a diagnostic explicitly changes them. Stop at a local endpoint such as payment, an exact allocation or a rejected action. This is distinct from a policy continuation and never silently reuses the historical suffix after state changes.

Examples should show both confirmation and refutation: reorder all61 Opus plan multisets; find three current-debt routes; retain G7's real stock lock; refute generated G6 redemption restriction. Analyst-specified alternatives establish existence, not the policy the agent would choose or whether the alternative wins. Include smaller altered-quantity recoveries separately from preserved plans.

Evidence: R06–R10/R25, phase2 script digests and exact sources. T4 recovery/T5 finance. Citations `dece`, `cattle`, `finboard` as shared execution/logging precedents. Transition: original checking can correct the analysis itself, so review provenance and limits are part of methods.

### 3.4 Review and validation

Explain complete extraction, overlapping614 catalog entries, fixed240 public-unflagged sample bundles and twenty trajectories. Four model coauthors inspected overlapping material; they did not provide independent human annotation or four blind recomputations of every assertion. The sample audits missed cases within its selection frame. Definitions developed during analysis are not preregistered. Preserve initial labels, objections and corrections.

Tests of hashes, joins, arithmetic and replay establish structural integrity; semantic checks need original bundles. Selected generated-label errors show why agreement is not a criterion. Do not estimate error rates from those selected corrections. HAL's precision validation and SOTOPIA/MACHIAVELLI's external-reference procedures are comparison points, not validation automatically inherited by our study.

Evidence: R01/R02/R25, final integrity checks and reviewer ledgers. Citations `hal`, `sotopia`, `machiavelli`. Transition: with measurement scope fixed, present the economic trajectories before using selected failures to characterize an agent.

## 4. Results I: economic trajectories and opportunity

### 4.1 Outcomes and acquisition pathways

Begin with all-game outcome profiles, not a ranked bar chart. Then distinguish475 direct acquisitions,72 auction acquisitions,207 traded deeds and397 inherited deeds. Group-completion routes use a different denominator,209 episodes with16 direct/9 auction/63 trade/121 inheritance completions. Sixty-nine inherited completions occur at game-ending bankruptcy and cannot generate later income.

These counts describe circulation and concentration under the variant. They do not mean every estate-created group was productive or that acquisition route caused victory. Include two trade-free winning games G14/G15. F2 outcome grid, T6 acquisition routes, F3 representative trajectories. Evidence final synthesis and event reducers. Transition: route counts do not show who created bargaining opportunities or how counterparties responded.

### 4.2 Initiating, receiving and settling trades

Show proposing-turn propensity, proposals per proposing turn and absolute counts, with accepting actors separately. Gemini's low initiation coexists with recipient bargaining, including eight games without a proposal. The113 settlements complete groups for neither side in60, one side in43 and both sides in10. Final offer author differs from original initiator in44 settlements.

Include rejected own-completion examples when funding a rival was an articulated concern. They show that completion is not the whole objective, without proving optimal rejection. Opportunity and survival are endogenous. T7 uses `negotiation_denominators.csv`; F3 includes a bargain-to-access sequence. Comparators `negotiationarena`, `finboard`, `agentmonopoly`. Transition: even a newly acquired group does not create immediate building access or applied investment.

### 4.3 Access, development and the execution condition

Report43/63 trade-completed groups with construction during first actual management turn; report34/42 entry-buildable groups alongside it. Plot the no-access and not-buildable paths rather than dropping them. The model-specific conditional rates describe applied behavior, not desire to build or overall strategic skill.

Use T4 recovery to explain the affected Opus condition. All61 defaulted multisets execute after reordering, but no repaired-policy outcome is observed. Other agents' retries may alter quantities; an eventual same-turn target differs from within-decision preservation. Place valid chosen holds alongside defaulted ENDs, including G1/G3/G5. This establishes that a uniform underinvestment story fails.

Add Fable's [first-management resolution table](../fable/exhibits/first_management_causes.json), keeping all 63 group episodes. By the turn-ending decision of the first management turn, Sol has 16 built and one other default; Gemini has 17 built and one valid END; Opus has seven built, five never legal in the observed window and three defaults after refusal; Grok has three built, four never legal, four received END conflicts and two valid ENDs. This is an observational resolution classification, not identified causal effects. Entry-buildable subsets differ from legal-at-any-point subsets. Grok has three conflicts among five entry-buildable non-builds, and four among six legal-in-window non-builds. A received conflict does not establish that the content's proposed allocation was executable; G12 d166 is the explicit caution. A valid END does not itself establish a deliberate hold. Attribute semantic categorization to Fable and any original checks to their named auditors; Sol rechecked row arithmetic, not all original windows.

Evidence R05–R07/R11 plus Fable's source-linked first-management classification. Citations `finboard`, `cattle`, `dece`. Transition: realized consequences require their own windows and ownership accounting, even after construction succeeds.

### 4.4 Paid receipts, inherited improvements and ending concentration

Present103 spending units and$103,450 outlay, with$93,000 whole-game developed paid rent and$92,550 after first own spend. Include40 zero-paid-rent units and26 without a creditor elimination on that group. Do not label them failed investments. Late development, deterrence, retained assets, salvage and game end limit that interpretation.

Use S2 to show timing sensitivity and inherited-deed composition, and S3 to contrast successive owners of the same G19 dark-blue deeds. Include the G10 hotel-only spending unit. Winners spend on58 groups,34 containing inherited deeds at first own spend,30 first completed through an estate. Eventual winners receive54/60 estates as creditor, including35/40 nonterminal; the terminal component is mechanically selected.

F3 should retain a complete representative trajectory and appendix all-game profiles. An inherited completed group, later investment and eventual rent are different stages. No inheritance effect or causal ROI is identified. Citations `finboard`, `vending`, `vending2`, `agentmonopoly`. Transition: liabilities and stock constraints reveal why accounting value differs from finance an actor can execute.

### 4.5 Finance, elimination and scarce houses

Show all60 elimination classifications:56 fail the full upper bound, three admit legal own-action current-debt payment, one has a hotel lock. T5 details G12d190, G12d249, G17d234, G7d339. Preserve their differing mechanisms and G12d249's contradictory received declaration. Pair with actual successful G20$1,400 liquidation and a valid chosen hold.

Explain bank-stock zero in nine games, stated retention motives, immediate restrictions and longer workarounds as separate findings. G7d330 management workaround does not erase the later d339 debt lock. G5/G12 restructuring does not make every direct expansion available. The optional stock-relaxed diagnostic counts opportunities rather than desire; a later build is later uptake in a changed state.

Evidence R08–R11/R17. F4 financing, T5 local routes. Alternative: local survival may not be optimal or valuable and does not identify another winner. Transition: economic competence is only part of the question; the same transactions also carry factual claims and assurances addressed to other agents.

## 5. Results II: conduct during competition

### 5.1 Social measurement and actual norm

Put the norm/opportunity/action/consequence/alternatives chain in the main text. Record permission for public deception and uncertainty about private-note truthfulness. Analyze observable conduct and responses without equating them to a scalar alignment score. A descriptive norm need not be randomized, while a causal susceptibility comparison does.

The unit is a proposition or temporally scoped assurance. Preserve disagreement among public message, applied note, content, provider text and applied tool. Availability states are empty, unavailable/unreturned and absent by action-only condition. An empty private lane is not evidence of no planning. F5/T8 carries this method through actual cases rather than remaining a generic diagram.

### 5.2 Misleading framing, exposure and pre-existing motive

G13d251/252/253 is the central case. Show the seller's cash, actual$130 alternative and Ventnor capacity against the debt. Show the exposed framing and recorded omission account. Then place the buyer's earlier d251 insurance rationale before the seller's d252 claim, not after. The later$200 settlement is observed; the causal$70 persuasion effect is unestablished.

Separate factual understatement, financial framing, recorded explanation and realized terms. The narrative should acknowledge inaccuracies elsewhere in the returned account and why the retained proposition still survives the exact check. Citations `arena_paper`, `negotiationarena`, `agentmonopoly`. Alternative: price, insurance value and strategic denial already motivated the buyer. Transition: the recipient need not accept a premise to accept a transaction.

### 5.3 Correction, assent, echo and rejection

Pair G4 public concession/private correction with G6/G19 correction-with-acceptance. Include G11 transient echo, subsequent correction and rejection. Use channel-specific descriptions rather than stable belief attribution. These cases reject settlement-as-persuasion and no-uptake-anywhere extremes simultaneously.

State case selection and no prevalence estimate. Do not call selected examples randomized negative controls. The 240 common bundles are a separate missed-case audit, not a denominator of deceptive propositions. Citations `arena_paper`, `sotopia`, `when_agents_lie`. Transition: sustained conduct includes changing assurances and records, not only truth of individual offers.

### 5.4 Standing offers, disclosures and oversight relevance

G18's exposed$250 offer is invoked and withdrawn after changing financial circumstances. Identify terms, recipient and later action before discussing commitment semantics. Costly reliance and an immutable rule were not established. G20's received public field contains a private-note string and recipient recognition; intent, component origin and exploitation remain unidentified.

Show checked action/explanation contradictions in G12d249, G19d135 and G18d083. The139 Grok name conflicts are a diagnostic count, not139 validated monitor failures. Fifteen equal parsed arguments and five literally identical substrings strengthen a limited channel discrepancy claim. No predictive monitor was evaluated.

Keep anti-leader appeals as recorded conduct without declaring coalitions or kingmaking. Comparison with commitment, runtime-affordance and Arena work clarifies what is measurable. Citations `commitment_standing`, `empty_commitments_v2`, `cheap_talk`, `arena_paper`. Empty Commitments v2 is a completed controlled study; the earlier v1 protocol is retained separately as `empty_commitments_v1` and must not stand in for the later results. Transition: these results depend on records whose generation and interpretation must themselves be audited.

## 6. Measurement validity and what changed interpretation

This section should be compact because affected results already disclosed their conditions. T3 maps each condition to affected estimands: refusal/retry, received channel conflicts, history-role manifestations and timeline delivery. The union of affected initial history prompts is2,054/6,989; repeated exposures and manifestations overlap. Generated histories can misrepresent a trade even when canonical holdings remain correct.

Explain error discovery with one analyst example, such as reading a redemption list as a prohibition. This shows that engine-grounded checks protect the paper from its own plausible labels. Script checks establish identities and arithmetic, not semantics. Broader label accuracy, causal wrapper effect and stream-component origin remain unmeasured.

The scientific finding is a limit on attribution and a method for resolving some ambiguities. Avoid claiming that all measured differences disappear after correction; the actual outcomes remain the cohort. Citations `hal`, `agents_that_matter`, `dece`, `agentbench`. Transition: the evidence now permits a precise separation between what the benchmark affords, what this cohort measures and what the long-term research question would require.

## 7. Capability, alignment and future environment design

Return to the introduction's question. The study measures economic sequences, applied outcomes and norm-relative social evidence. It establishes neither latent capability ordering nor alignment change as capability grows. Skill is multidimensional, opportunities are endogenous and public deception is authorized. One strong arithmetic result cannot substitute for this missing design.

T9 should have implemented, measured and proposed columns. Implemented: authoritative legal actions, persistent state, memory and public communication, attempts and replay. Measured: economic trajectories, selected social propositions and channel discrepancies. Proposed: independently specified honesty/commitment/authorization norms, standardized opportunities to comply or deviate, monitor evaluations, learning adapter and held-out transfer studies. A proposed field is not an implemented feature.

Explain the prospective design in enough detail to be useful. Freeze the norm; sample opportunities with equal compliant alternatives; independently measure capability; vary stakes, observability, opponents and instruction; keep response handling controlled; record actual exposure, legal choice and consequence. Track conduct and task utility separately. Within-family scales can help but parameter count alone does not validate a capability axis. Repeated seeds without matched state do not isolate incentives.

For learning, distinguish an environment that can collect trajectories from demonstrated training efficacy. Require held-out seeds, rosters and rule perturbations, equal resource budgets and external transfer tasks before claiming safer agents. MACHIAVELLI is a precedent for actually measuring steering trade-offs; tau-bench and AgentDojo show how explicit policies/trust boundaries make violations testable. Monopoly familiarity and simulator validity remain open external-validity issues.

Citations `machiavelli`, `agentdojo`, `taubench`, `metr`, `concordia`, `dece`, `empty_commitments_v2`. C21–C23 specify claim-dependent experiments. Transition: broad ambitions should be accompanied by explicit limits on the scope of this cohort and its evidence access.

## 8. Limitations and challenges

One roster and five seed blocks limit population and opponent generalization. Cross-model response conditions prevent intrinsic provider ranking. Declared rules, inherited development and management timing affect strategy and external validity. Public-deception permission limits instruction-misalignment interpretation. Available explanation records are incomplete and nonprivileged. Endogenous opportunities and terminal censoring limit rate and investment comparisons. Local feasibility tests do not establish optimal play or counterfactual winners. Semantic labels lack independent human criterion validation, and the common sample has a specific selected frame. Provider usage semantics and missing refusal usage constrain cost comparisons.

Avoid a generic limitations list detached from claims. Point each item to its affected exhibit and the alternative evidence that would address it. The proposed experiments are conditional on retaining stronger claims; they are not hidden prerequisites to publishing the bounded results. The release should state what a new researcher can reproduce now and what requires new provider access or new games.

## 9. Closing argument

Restate the measured contribution without a new headline. A persistent competitive economy allows capability and conduct to be studied together when the record preserves the actions, information and consequences. The cohort demonstrates productive sequences, mistakes, corrections, misleading framing and limits of explanation-based attribution. Exact legal alternatives and complete accounting make those observations more precise. The capability/alignment frontier and training benefits remain experiments to design, with the required norms and controls now explicit.

## Appendix and release plan

Include all twenty trajectory profiles; schema/units glossary; exact rule/configuration table; model/response-condition/channel-availability table; per-game source hashes and reproduction commands; acquisition and trade-accounting details; all61 reordering cases and local liquidation routes; social source IDs and short bounded excerpts; extraction/adjudication provenance and selected-frame sampling; detailed comparison/version ledger; claim matrix. Keep exploratory catalogs and long debate under `docs/research_raw/` rather than presenting all extracted labels as a curated ground-truth dataset.

The manuscript should link generated assets to this package's manifest. A reader should be able to reconstruct every plotted value from retained records and identify which statements depend on semantic review rather than deterministic reduction. This outline does not authorize new games, changed prompts, canonical edits or venue tailoring.
