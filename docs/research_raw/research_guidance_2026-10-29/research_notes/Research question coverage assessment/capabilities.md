# Capability question coverage assessment

Assessment date: 29 October 2026. Scope: current 40-page manuscript, assigned questions 1, 2 and 5, and deeper questions A and B. All six screenshots were visually read. Their wording and supplied metric list are preserved in [source_transcription.md](source_transcription.md). This is a read-only assessment of the paper and retained audits. It is not a new source-level replay, literature review or experiment. Nothing in the manuscript, outline, prompts, engine or canonical games was changed.

The status vocabulary below distinguishes **strong narrow answer**, **partial descriptive answer**, **case evidence only**, and **not evaluated**. These are qualitative judgments of coverage, not percentages or model performance scores. An environment that supports a test has not necessarily run that test. The present paper explicitly contributes a bounded method for validating behavioral claims, not a comprehensive measurement of intelligence. [Current introduction](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/introduction.tex:15)

## 1. Strategic reasoning and rationality

### Takeaway

**Partial descriptive answer.** The paper demonstrates selected forward-looking reasoning, rival-sensitive decisions and failures of feasibility or execution. It does not determine whether participants maximize winning probability, estimate regret or exploitability, or compare them against strategic reference policies. The screenshot's specific example, refusing own gains to avoid empowering a rival, is present; the full optimization question is not answered. [Economic results, pp. 8–13](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex); [additional social cases, p. 36](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/social_detail.tex)

### Cited findings

- The clearest direct answer to the screenshot's trade example is G11 d258. Grok rejects an exchange that really would complete its pinks, stating that it would also complete Sol's greens and provide construction cash. The immediately preceding d256 rejection corrects a false pink-completion claim; d257 repairs the offer and still receives a rejection. Thus own set completion is demonstrably insufficient for acceptance in this case. The manuscript gives this chronology in the additional social appendix, p. 36. [Manuscript](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/social_detail.tex:5); [retained original-channel audit](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/sol/g11_social_channel_checks.json)
- G3 d176 and G1 d426 are checked, valid holds with expressed reserve reasons and executable construction alternatives. Those are examples of stated trade-offs, not proof the holds maximize eventual reward. [Economic results, p. 11](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:46); [G3 retained audit](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/sol/g03_opus_restraint_check.json)
- All 60 eliminations are classified against own-asset current-debt payment: 56 fail a generous upper bound, three have legal payment witnesses, and one has a legal hotel-access restriction. This measures a narrow feasibility endpoint, not whether survival is strategically preferable. [Economic results, pp. 11–13](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:48); [certificate summary](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/data/certificate_results.json)
- The paper retains different forms of apparent noninvestment: 43 first-window builds out of 63 trade-completed groups, nine unbuilt groups without a legal build opportunity during that window, four defaults, four content/tool conflicts and three remaining valid ENDs. This avoids attributing every unbuilt group to strategic restraint. [Economic results, p. 9](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:30)
- Win counts are descriptive cohort outcomes. Each participant faces the same other three model configurations, only five seed blocks are present, and response conditions differ. The paper expressly refuses an intrinsic capability ordering. [Setup](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/setup.tex:34); [limitations, p. 26](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/limitations.tex:5)

### Inferences

The defensible answer is: these configured agents sometimes record and act on rival-sensitive trade-offs, but legal financing, action execution and factual accounting fail in identifiable cases. This does not amount to a general rationality score. The paper's strongest research contribution here is preventing the evaluator from mistaking a default, absent opportunity or erroneous feasibility assumption for a preference. A correct prediction of one consequence still does not value all alternatives.

The question is presently scattered between economics and the social appendix. A reader interested in strategic ability could miss the G11 example because it is introduced as a counterexample to inference about deception rather than as an example of considering a rival's gain. A small question-to-answer synthesis could improve the paper without additional data.

### Gaps

**Writing or synthesis only, not performed here:** explicitly answer the screenshot's trade example and pair the successful rival-sensitive rejection with one failed feasibility forecast. State the objective under discussion. Current-debt payment is a test endpoint; being the last nonbankrupt player is the assigned game objective. They should not be treated as interchangeable utilities.

**Existing-log analysis:** prespecify a taxonomy for trade-response reasons, including own completion, rival completion, rival funding, liquidity, timing and reserve capacity. Code all eligible responses, preserve channel provenance, inspect the stated financial mechanism, and publish both the denominator and uncertain interpretations. Add factual rule and arithmetic checks only where the original observation contains the information needed. This would estimate the frequency of recorded considerations, not their optimality or causal role.

**New evaluation needed for the full question:** use held-out states with defined objectives and valid alternatives, and compare actual choices with specified reference policies or a solver on tractable subproblems. For game-level action value, use repeated continuations under fixed opponent policies and report uncertainty, not the single historical dice suffix. Define regret against the chosen comparator; do not call it optimal-policy regret unless the comparator is established as optimal. A credible design must vary states, opponent mixtures and seeds while holding response policies fixed or explicitly treating them as factors. Proposed designs are not executed by this assessment.

## 2. Opponent modeling and theory of mind

### Takeaway

**Case evidence only.** The manuscript documents reasoning about rival resources, incentives and likely consequences. It does not score opponent predictions, calibrate beliefs, establish mental-state inference, or show that an opponent model improves decisions. The screenshot's cash-saving-for-auction example is not presently an explicit tested result in the paper. [Social results](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/social_results.tex); [setup observation contract](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/setup.tex:6)

### Cited findings

- Opponents' cash, holdings and model names are visible, while their private notes and future random state are not. Computing a rival's currently feasible construction is therefore public-state tactical reasoning, not by itself a test of theory of mind. [Setup, pp. 2–3](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/setup.tex:6)
- G11 d258 links a trade refusal to the opponent's prospective green completion and financing. G20's main-text appeal asks the others to stop funding Grok, and Grok labels that a cash boycott. These are concrete records of strategic interaction and competing incentives. They are not scored predictions of another agent's hidden goals. [G11 appendix, p. 36](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/social_detail.tex:5); [G20 transcript, pp. 17–18](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/transcript_conduct.tex:57)
- G13 traces the buyer's response to the seller's appeal and subsequent omission. It establishes delivered information and a repeated estate-denial rationale, but the buyer's text never says the cheaper mortgage-financed route is impossible. The observed price difference does not identify a persuasion effect. [G13 transcript, pp. 15–16](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/transcript_conduct.tex:3)
- The retained research has unused opponent-forecast material. At G7 d182, Grok says Opus with $719 cannot afford three houses on each pink. The next actual management prefix admits two railroad mortgages and nine interleaved houses, ending at $19. The historical action is a default. This distinguishes a feasible-opponent-action forecast from the opponent's realized execution. It is present in the retained audit, not developed as a separate opponent-modeling result in the current paper. I read the report and its recorded forecast but did not rerun the engine branch. [Retained audit](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/sol/g07_sample_finance_check.json); [synthesis, lines 73ff.](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/sol/methods_and_findings.md:73)
- The paper explicitly distinguishes exposure from attention, belief and reliance, and cautions against treating provider explanations as privileged measurements of computation. [Methods, pp. 7–8](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/methods.tex:4)

### Inferences

There are at least three different proposed tests here: anticipating legal opportunities from public resources, forecasting another actor's next behavior, and inferring beliefs or intentions. The current paper chiefly addresses the first and checks boundaries of the third. Treating all three as theory of mind would overstate coverage.

The G7 example is especially useful conceptually: a false inability forecast can coincide with no actual build because the opponent fails to execute. Scoring only the realized outcome could reward a factually wrong opponent model. A future assessment must separately score possible actions, predicted chosen actions and resolution failures.

### Gaps

**Writing or synthesis only:** explicitly label the current examples as rival-sensitive tactical reasoning and explain what is observed. Avoid implying that a model's assertion about another model's belief validates that belief. The absent prediction/calibration result should be named as a gap, not hidden in a general limitation.

**Existing-log analysis:** identify every spontaneous, falsifiable opponent forecast before its outcome, with actor, target, proposition, horizon, information available, uncertainty and resolution condition. Check deterministic financial claims against legal access and behavioral predictions against subsequent events. Report the eligible denominator and abstentions. Because spontaneous predictions are selected and usually nonprobabilistic, this cannot provide an unbiased calibration score, and unsupported mental-state claims must remain unresolved.

**New evaluation needed:** use controlled opponents with known, varied policies, held-out opponent changes, and a prespecified prediction interface. Elicit probabilities before actions and score them with a proper scoring rule; compare against a state-only baseline that has the same public cash and holdings. For beliefs or knowledge, construct information-asymmetry tasks with known delivered information, rather than use another LLM's private note as a gold-standard mind state. Intervene on opponent history or policy while keeping public economic state fixed when feasible. These would be new versioned task conditions and prompt changes, requiring later authorization.

## 5. Adaptability and learning

### Takeaway

**Local correction examples exist; learning is not evaluated.** The manuscript measures retry repair and shows a proposal revised after a correction. It does not establish sustained strategic improvement, response to unfamiliar opponents, transfer to held-out conditions, or learning across games. The task cannot be answered merely by pointing to the fact that the agents play a long game. [Retry results, pp. 10–11](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:38); [G11 correction, p. 36](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/social_detail.tex:5)

### Cited findings

- Following an uneven-build rejection, some legal construction is applied in 25/29 Sol, 18/19 Gemini and 5/5 Grok decisions; the original purchase multiset is preserved in only 20/29, 6/19 and 5/5 respectively. Opus's 61 cases end in defaults under an exhausted refusal-recovery condition. These are within-decision response-resolution outcomes, not learned strategy changes. [Recovery table data](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/data/t07_build_recovery.json); [manuscript explanation, p. 11](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:44)
- G11 d257 explicitly acknowledges the earlier missing-St.-Charles error and changes the proposed bundle. Grok's d256 explanation corrects its own transient echo before rejection. This shows recorded local revision. It does not show that either actor later avoids the same error in a comparable situation. [Manuscript, p. 36](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/social_detail.tex:5); [original-channel report](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/sol/g11_social_channel_checks.json)
- The study gives agents twenty public timeline entries and ten private notes. Refusal recovery leaves 1,394 of 1,696 Opus decision memories without a model-authored private note, including 286 windows containing only synthetic fallback notes. Hence participants have materially different delivered feedback histories. A failure to improve after an error may reflect missing feedback as well as persistent policy failure. [Setup](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/setup.tex:6); [validation, p. 22](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/validation.tex:24)
- Every evaluated agent faces the same other three models, with visible identities. No unfamiliar-opponent or cross-game-learning condition is evaluated. The paper does not train a policy. [Limitations, p. 26](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/limitations.tex:5); [infrastructure, pp. 22–23](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/validation.tex:28)
- The retained G8 trajectory assessment describes Sol changing from a preference for a monopoly-free board to a Park Place trade after orange development appears. This is a candidate within-game policy change, not a validated learning measure or a current main-text result. I did not reread the full original G8 trajectory in this assessment. [Retained G8 assessment](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_phase2_2026-10-28/core_review/sol/game_assessments.md:49)

### Inferences

The minimum distinctions are: correcting an invalid response, revising a stated factual claim, changing policy after an observed consequence, retaining that revision at a later comparable opportunity, and transferring improvement to a new opponent or game. The current paper measures the first and illustrates the second. It does not measure the latter three.

An agent selling houses after rent or changing its price after losing cash is responding to a changed state. That alone is not evidence it learned a better policy. Likewise, repetitions within the existing cohort do not imply persistent knowledge carried from one game to another. No cross-game memory intervention or learning curve is reported.

### Gaps

**Writing or synthesis only:** explicitly separate response repair from adaptation and state that the paper has no learning result. The G11 correction can remain as a concrete local revision, with its endpoint stated.

**Existing-log analysis:** build a temporal error-and-feedback ledger. For each opportunity, identify the mistake or adverse outcome, whether feedback was actually delivered, whether it remained in memory, and the next comparable opportunity. Separate state-driven necessity from a documented policy revision and preserve cases with no repeat opportunity. Estimate recurrence only within a stated error class and configuration. Repeat-opportunity selection and changing resources prevent a causal learning conclusion, but the result would be more informative than anecdotes.

**New evaluation needed:** repeatedly expose agents to matched opponent policies and identifiable strategy failures, randomize access to feedback or memory, and evaluate later matched opportunities and a held-out policy shift. Prespecify what improves, such as fewer invalid plans, better prediction scores or higher expected utility against the same opponent distribution. Compare with a no-feedback condition and use independent games or episodes as the statistical unit. Cross-game adaptation requires an explicit persistent-memory design; weight learning requires an actual training procedure. Neither is supplied by the current logs.

## A. Strategic knowledge versus strategic execution

### Takeaway

**Strong narrow answer, full dichotomy unresolved.** This is the current paper's closest match to the screenshots. It proves that recorded plans, explanations and applied actions can diverge in consequential, measurable ways. It does not establish that the models possess general strategic knowledge, that fluent explanations are merely performance, or that coherent execution is strategically good. [Abstract](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/abstract.tex); [conclusion](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/conclusion.tex)

### Cited findings

- Across 1,225 management menus listing construction, 663 applied actions are END. There are 66 defaults and 24 detected selected content/tool-name conflicts; the remaining 573 have no detected name conflict and are explicitly not treated as verified strategic choices. This is a complete defined population, not just vivid quotes. [Economic results, pp. 9–11](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:34); [resolution data](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/data/resolution_conditions.json)
- All 61 Opus defaulted allocations are reachable after atomic expansion and reordering, while the submitted encodings are invalid. Across all configurations, 63 of 66 defaulted decisions contain at least one reachable target. This demonstrates a gap between a stated construction target and legal execution. It does not validate the target's expected value. [Economic results](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:38); [certificate results](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/data/certificate_results.json)
- G12 d249's received bankruptcy action is accompanied by content requesting house sales and final explanations opposing bankruptcy. A legal five-sale route pays the debt. This is a consequential same-response inconsistency rather than proof of deliberate surrender or a single stable mistaken belief. [Economics](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/economic_results.tex:70); [transcript control](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/transcript_controls.tex)
- All 139 selected Grok name disagreements are already in the saved nonstreamed JSON response bodies. The evidence excludes local streaming assembly for these particular conflicts, but not generation, provider processing or gateway causes. Sol and Gemini's selected assistant-content fields are empty, so absence of this detectable form is not a comparable consistency score. [Validation, p. 22](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/validation.tex:20)

### Inferences

Calling this simply "strong coverage of strategic intelligence" would be misleading. A model can consistently execute a bad strategy, or describe a good target in an invalid encoding. A response can contain both a correct recommendation and contradictory arithmetic. The evidence supports separating proposition correctness, stated target, encoding validity, resolution origin, applied action and observed consequence. Strategic value remains a further question.

The current result is stronger than "models sometimes make mistakes" because it has defined populations, source records and executable witnesses. Its scope is narrower than proving a strategic-knowledge/execution decomposition across all decisions or models. The paper should preserve that exact boundary even if the guiding research program broadens.

### Gaps

**Writing or synthesis only:** frame the existing result as a direct, bounded response to question A. A compact table could pair a stated plan, whether the plan is factually and legally sound, the received/applied action, and the local consequence. Avoid calling every discrepancy a knowing failure to follow an intended plan.

**Existing-log analysis:** prespecify a broader plan-to-action alignment population and code causal ambiguity, missing channels and reversals. Distinguish objective facts, financial forecasts, conditional plans and rhetoric. Evaluate plan quality independently of whether execution matches it. A blinded annotation exercise with source-grounded adjudication could test whether the audit improves label validity; the present four coauthor reviews are not that experiment.

**New evaluation needed for the broad dichotomy:** combine independent strategic knowledge tests with matched decision tasks and held-out outcome evaluation. Compare action-only and explanation-plus-action conditions under controlled resolution policies, and separately score factual reasoning, legality and expected decision quality. Such interventions change the benchmark condition and must be versioned. Merely asking for more reasoning is not a valid assay of latent strategic knowledge.

## B. General intelligence versus multi-agent intelligence

### Takeaway

**Not evaluated.** The paper has no independently measured general-capability axis and no controlled set of capability tiers. Its four heterogeneous configurations and twenty outcome records cannot determine whether math, coding or general reasoning predicts negotiation, opponent modeling or multiplayer performance. [Discussion, p. 23](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/discussion.tex:17)

### Cited findings

- The paper explicitly says capability and response policies were not independently varied and makes no intrinsic model-ranking claim. [Introduction](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/introduction.tex:15)
- It proposes an independently measured capability axis with multiple within-family tiers and fixed or deliberately varied prompts, memory, retries, tool choice and resources. That is an experimental design discussion, not a result. Its specific published-literature comparisons were not reverified in this read-only assessment. [Discussion, pp. 23–24](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/discussion.tex:21)
- The observed common effort label does not match compute: reported mean completion tokens differ from 128 for Sol to 4,041 for Grok, with different provider semantics and recovery policies. This adds a condition that any comparison must explicitly handle. [Setup](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_draft_2026-10-29/sections/setup.tex:30)

### Inferences

There is no honest prose-only route from this cohort to an answer. External leaderboard numbers attached to these four names would still confound family, inference condition, resources and gameplay exposure, and four points would provide very weak evidence. Saying the paper has a discussion of the question must not be counted as answering it.

The screenshot's question also differs from capability versus alignment. Better multi-agent task performance is not the same outcome as more or less dishonesty. The current discussion mostly formulates the latter design. A future program should declare which dependent variable it intends to explain and retain both if both matter.

### Gaps

**Writing or synthesis only:** explicitly state "not tested" for general-to-multi-agent transfer, and distinguish it from the capability–alignment question. Do not imply that the observed win order supports independence from general capability.

**Existing-log analysis:** the present cohort can inform measurement definitions and sample-size planning, but cannot supply the absent independent capability variation. Descriptive profiles are possible; a general-capability relationship is not identified.

**New evaluation needed:** recruit multiple capability levels within several model families, measure independent math/coding/reasoning ability under documented compatible settings, and run a prespecified multi-agent task battery. Separate negotiation quality, opponent-prediction accuracy, financial feasibility, learning and game outcomes. Vary opponent mixtures and seeds, account for family and game dependence, and evaluate predictions on held-out models or conditions. Compare complete configured systems or explicitly vary compute and recovery policy; do not silently attribute their effects to base-model intelligence. The minimum credible sample size requires an effect-size and power analysis, not an arbitrary promise that a fixed small count suffices.
