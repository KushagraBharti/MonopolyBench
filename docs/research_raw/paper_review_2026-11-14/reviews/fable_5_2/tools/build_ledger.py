"""Write claim_ledger.json for the 14 November review. Content only; no game data is read here.

Source tags
  R1 = inputs/pasted-text-2.txt (the 5.5/10 report)
  R2 = inputs/pasted-text-3.txt (the comparator discussion)
  I1 = inputs/inline_feedback.md lines 5-599 (the experimental program)
  I2 = inputs/inline_feedback.md lines 603-705 (the v3 referee report, 4/10)
  I3 = inputs/inline_feedback.md lines 709-781 (the comparator table)
  I4 = inputs/inline_feedback.md lines 783-859 (the liquidation and oracle proposal)
Verdicts: confirmed, partly supported, incorrect, unverified, proposal.
Basis: "checked" means I checked it this round against the named record or source.
       "inherited" means I rely on an earlier team result I did not redo.
"""
import json
from pathlib import Path

L = []


def add(id, source, locator, claim, kind, severity, verdict, evidence, basis, implication):
    L.append(dict(id=id, source=source, locator=locator, claim=claim, kind=kind, severity=severity,
                  verdict=verdict, evidence=evidence, basis=basis, implication=implication))


# ---------------------------------------------------------------- R1: the 5.5/10 report
add("R1-01", "R1", "section 2", "The paper accounts for all 188 financing episodes, 131 demonstrated-payable debts and sixteen necessary-collateral cases.",
    "empirical", "medium", "confirmed",
    "tools/episodes.py rebuilds 188 episodes from raw decisions.jsonl with zero unmatched against data/liquidation_episodes.json. tools/partition.py gives 62/53/16 payable and 62/52/14 paid. tools/census.py gives 128 paid and 60 eliminated.",
    "checked", "The census is sound and should stay.")
add("R1-02", "R1", "section 4, table", "The 13+1+2 reading splits by channel as 9 notes and 4 provider texts stating the resource, 1 tentative provider text, 2 note omissions. All five provider-text cases are Opus.",
    "empirical", "medium", "confirmed",
    "data/sixteen_first_decisions.txt. Opus first decisions in G4 d308, G6 d185, G11 d203, G17 d254, G20 d291 are all action-only recovery responses with no applied note. The other eleven carry an applied note.",
    "checked", "Channel belongs in the analysis and not only in a provenance column. Provider reasoning precedes the call. The note is an argument of the call.")
add("R1-03", "R1", "section 5", "G20 d291 Opus text confuses its accounting. It says '$725 short even after' the listed proceeds and compares $680 with the $1,000 debt. The true remaining shortfall is $45. The route then goes 725, 845, 955, plus $70, leaving $25.",
    "empirical", "medium", "confirmed",
    "Raw G20 d291 to d294. Cash 275, pink sales 450, Illinois 120, Indiana 110, States 70. The next own decision shows cash 25. The provider text reads as quoted.",
    "checked", "Keep the case as tentative recognition. Annotate the accounting error in the appendix.")
add("R1-04", "R1", "section 5", "At G20 d291 the menu lists Indiana and Illinois as mortgage targets and the pinks only as sale targets. The prompt does not state the release rule.",
    "empirical", "low", "confirmed",
    "Raw scenario options at G20 d291. The stored system prompt (integrated/data/standard_system_prompt.txt) has no rules text.",
    "checked", "None beyond R1-03.")
add("R1-05", "R1", "section 6", "The necessity test is one-way. U0 >= D does not prove a route that avoids released mortgages, so the Table 2 label 'released mortgages not necessary' is stronger than the bound proves. At most five paid episodes need scrutiny.",
    "method", "medium", "partly supported",
    "The logic is right in general because nominal salvage can be blocked (G7). No episode is misclassified. Of the 53, 47 were paid with no released mortgage (observed witnesses), one is G12 d249 with a stored audit witness, and five used released collateral (G3 d228, d356, d461, d482; G18 d428). For each of the five I derived a no-release route by hand from the recorded holdings and the sale rule as coded. Those five routes were not executed in the engine. For hotel-free states the bound is exact, because every building is sellable in some order.",
    "checked", "Relabel the row or add a sentence. No count changes.")
add("R1-06", "R1", "section 7", "Ten actions are not ten hard planning decisions. A simple reactive policy might complete much of the population.",
    "method", "high", "confirmed",
    "Stronger than stated. Code reading of engine.py (_mortgageable_space_indices, _sellable_building_space_indices, _resolve_pending_payment) shows that in a hotel-free state every maximal sequence of offered financing actions raises exactly U* and the engine pays as soon as cash covers the debt. 108 of 131 payable debts and 15 of the 16 are hotel-free. See I2-06.",
    "checked", "The payment count measures not stopping. This is the largest change to how the finance result should be worded.")
add("R1-07", "R1", "section 8", "Bargaining arithmetic reproduces: 30.51, 16.67, 22.57 and -5.05 points.",
    "empirical", "low", "confirmed",
    "tools/bargaining_recount.py from raw decisions: 95/116 vs 37/72, 90/108 vs 24/36, 93/112 vs 26/43, 42/70 vs 67/103.",
    "checked", "None.")
add("R1-08", "R1", "section 8C", "The introduction says the cash-bid difference is negative 'only when pooled', but the Grok recipient stratum is -0.245.",
    "empirical", "low", "confirmed",
    "sections/scientific_introduction.tex line 11 against sections/recipient_rows.tex (19/24 vs 27/34). The wording entered through final-review finding OFR-02, which I reviewed and did not catch.",
    "checked", "One-sentence correction when the manuscript is next opened.")
add("R1-09", "R1", "section 8D", "The 61/74 semantic count needs a written codebook.",
    "measurement", "medium", "confirmed",
    "The manuscript prints no criterion. evidence_map.md records the 61/74 as inherited LLM codings by two GPT-6 Astra instances.",
    "inherited", "State the criterion or drop the count from the body. It is not human validation.")
add("R1-10", "R1", "section 8E", "The fourteen settlement pairs are selected on eventual settlement.",
    "inference", "low", "confirmed",
    "The appendix already says the selection 'conditions on settlement'. The main text says only that the histories are not an effect of liquidity.",
    "checked", "Minor wording.")
add("R1-11", "R1", "section 9", "For a financing-centred paper most incidents should move to the appendix.",
    "editorial", "medium", "proposal",
    "INTEGRATION_DECISIONS.md records that the owner asked for five to eight contextual transcripts in the body.",
    "checked", "Human decision. I recommend three in the body (G20 payment, G13, G7).")
add("R1-12", "R1", "section 10", "ReAct, Zero-Shot Planners, PlanBench, Embodied Agent Interface, Robotouille, LexiCon, Planning in the Dark, NegotiationArena and the hybrid Monopoly paper set the relevant standards.",
    "literature", "low", "unverified",
    "I re-read PlanBench this round (arXiv v4 PDF). The others I did not open this round. The venues named match what I know for ReAct, Huang et al., Embodied Agent Interface, Robotouille and NegotiationArena. LexiCon and Planning in the Dark I have not read.",
    "not checked", "No claim in the paper should lean on these without a fresh read.")
add("R1-13", "R1", "section 10", "A September 2026 preprint, 'Do LLM Agents Execute the Plans They Declare?', overlaps the title's 'stated plans'.",
    "literature", "medium", "confirmed",
    "Project page read. arXiv 2609.38108, Oota et al. A declared plan there is a chosen planning mode routed to an executor, measured on ALFWorld, Mind2Web, SWE-bench Verified and WebArena. Full paper not read.",
    "checked", "Cite and distinguish, or retitle.")
add("R1-14", "R1", "sections 3 and 11", "The more interesting contribution is correct arithmetic over an incomplete inventory, ending in a false impossibility claim.",
    "science", "high", "partly supported",
    "Both failed sums equal U0 exactly (408 and 530) and both texts assert impossibility. That is two episodes. PlanBench's o1 evaluation already reports false impossibility on solvable instances, so occurrence is not new.",
    "checked", "Supports re-centring on the stop decision. Does not support a rate or a cause.")
add("R1-15", "R1", "section 11", "Next study: finish existing-record analysis, build state families, separate assessment from execution, add a verifier and a reactive reference, test one explanation on fresh states.",
    "design", "high", "proposal",
    "Step 1 is existing-record work. Steps 2 to 5 need engine execution, synthetic states and provider calls.",
    "checked", "Step 1 is in scope now. The rest needs changed authorization.")
add("R1-16", "R1", "section 12", "Main text reaches page 12. The abstract's first sentence suggests statements were coded across both full populations.",
    "editorial", "medium", "confirmed",
    "Rendered PDF: references begin on page 12. The abstract says the corpus 'connects all 920 negotiation responses and 188 financing episodes to ... prospective statements'. Statements were read for 16 episodes and 74 rejections.",
    "checked", "Fix the abstract sentence. I did not check any venue page limit.")
add("R1-17", "R1", "verdict", "5.5/10 overall and a simulated 3/6.",
    "rating", "low", "unverified",
    "A judgment. Not a finding I can test.",
    "not checked", "Not adopted.")

# ---------------------------------------------------------------- R2: the comparator discussion
add("R2-01", "R2", "section 2", "AgentMonopoly reports 140 games in four series, eight models, five seeds per configuration, elimination when cash goes negative and a 150-step limit.",
    "literature", "medium", "confirmed",
    "arXiv 2610.29330v2 HTML. Table 3 sums to 140 (40, 40, 40, 20). 'a player is eliminated when its cash balance becomes negative'. The repository README sums to 120 because it lists 20 cross-family games. See I3-01.",
    "checked", "The two referees quote two different counts from the same project.")
add("R2-02", "R2", "section 2", "AgentMonopoly already connects language with behavior, so that alone does not differentiate the paper.",
    "literature", "high", "confirmed",
    "The paper compares persona word frequencies in messages and explanations with action rates. The analysis is descriptive with no agreement metric.",
    "checked", "The title's general claim is not a differentiator.")
add("R2-03", "R2", "section 2", "AgentMonopoly's environment does not expose the post-obligation debt-rescue problem.",
    "literature", "high", "confirmed",
    "Immediate elimination is stated in the paper ('a player is eliminated when its cash balance becomes negative') and in the README. R2 does not mention that FinBoardBench's Monopoly does have a fund-raising prompt with MORTGAGE, SELL_BUILDING and bankruptcy actions. FinBoardBench reports no analysis of that phase.",
    "checked", "The setting is not unique to this project. What I did not find elsewhere is any analysis of it. Absence in two papers is not a novelty claim.")
add("R2-04", "R2", "section 3", "FinBoardBench has nine focal models, three games, 108 matches, a fixed three-model opponent pool with seat rotation, and a thinking-mode comparison on three models.",
    "literature", "low", "confirmed",
    "arXiv 2605.27896v1 HTML. Opponents are DeepSeek V4 Flash, Qwen-3.5-397B-A17B and Gemini-3.1-Flash-Lite-Preview.",
    "checked", "None.")
add("R2-05", "R2", "section 3", "The FinBoardBench thinking table sums to 4/36 against 10/36 wins and its conclusion is stronger than that supports.",
    "literature", "low", "partly supported",
    "Four matches per cell and the conclusion wording are confirmed. I could not read the table cells cleanly enough to confirm the 4 and 10. A Fisher test on 4/36 vs 10/36 gives p = 0.13 two-sided, which is the referee's own point.",
    "checked", "Not a model to copy.")
add("R2-06", "R2", "section 3", "FinBoardBench judges trade and auction quality with DeepSeek V4 Pro and no human validation. A judge label is not economic ground truth.",
    "literature", "medium", "confirmed",
    "Paper text. No human validation is reported.",
    "checked", "Supports keeping trade value unmeasured. Contradicts I3-13.")
add("R2-07", "R2", "section 4", "Vending-Bench runs five repeats per condition capped at 2,000 messages, varies capital, fee and memory for GPT-4o mini, and has one human participant for five hours.",
    "literature", "low", "confirmed",
    "arXiv 2502.15840v1 HTML.",
    "checked", "None.")
add("R2-08", "R2", "section 5", "Vending-Bench 2 scores final balance over one simulated year. The $63,000 figure is a calculation under assumptions. Epoch AI's review found unequal usable context and exploitable behavior, and saw no exploit in the two official traces it inspected.",
    "literature", "low", "confirmed",
    "andonlabs.com/evals/vending-bench-2 and epoch.ai/benchmarks/vending-bench-2/review (dated 21 October 2026, rated Flawed).",
    "checked", "Supports keeping the paper's disclosure of unequal response conditions.")
add("R2-09", "R2", "section 5", "The Arena communication study classifies 2,583 emails from 20 runs across 13 models, with replication by judges from other model families.",
    "literature", "medium", "confirmed",
    "arXiv 2608.14825v3 abstract and the first 100,000 characters of the HTML. Human validation there is 50 emails labeled by the codebook author.",
    "checked", "Their human check is small and not independent. It is still more than this paper has.")
add("R2-10", "R2", "section 6", "AutoVend compares five agents with a rule-based policy over 20 sites and 180 days, with three executions per model in one frozen world.",
    "literature", "low", "confirmed",
    "arXiv 2610.36980v2 HTML.",
    "checked", "None.")
add("R2-11", "R2", "section 6", "128/131 and 14/16 are weakly calibrated until a reactive reference is run.",
    "method", "high", "partly supported",
    "The concern is right. A run is not needed to answer it for hotel-free states, where the answer follows from the menu rules. See R1-06.",
    "checked", "State the structural property in the paper. Do not present it as a measured baseline.")
add("R2-12", "R2", "section 7E", "In G17 the initial calculation reaches $530 against $550 while omitting $375 of released collateral.",
    "empirical", "low", "confirmed",
    "Raw G17 d234. Park Place 175 plus Boardwalk 200.",
    "checked", "None.")
add("R2-13", "R2", "section 5", "Project Vend ran a physical shop and its later phase changed several things at once.",
    "literature", "low", "unverified",
    "Not opened this round.",
    "not checked", "No use in the paper.")
add("R2-14", "R2", "section 8", "Priorities: score the sixteen texts on separate dimensions, add a transparent reference, run a fresh 2x2 information experiment, give the paper one centre.",
    "design", "high", "proposal",
    "The first is existing-record work and I give my own reading in review.md. The second is analytic for most states. The third needs changed authorization. The fourth is an editorial decision.",
    "checked", "See recommendations.md.")
add("R2-15", "R2", "section 9", "Nine models, three games, hundreds of games, a human tournament, an optimal solver and a physical deployment are not required.",
    "judgment", "low", "confirmed",
    "I agree. Each is needed only for a claim the paper does not make.",
    "checked", "Contradicts parts of I3-13.")

# ---------------------------------------------------------------- I1: the experimental program
add("I1-01", "I1", "novelty table", "ACPBench (AAAI 2025) tests action reachability. ACPBench Hard (ICLR 2026) adds generative tasks and validators.",
    "literature", "high", "confirmed",
    "arXiv 2410.05669v3 and 2503.24378v2 HTML. Action reachability asks whether an action can eventually be applied from the current state. All tasks are single-turn. In ACPBench Hard it is the hardest task, with the best model near 13%.",
    "checked", "The construct is established. Neither benchmark has an interactive agent or a stop decision.")
add("I1-02", "I1", "novelty table", "The PlanBench evaluation of o1 examines false impossibility judgments.",
    "literature", "high", "confirmed",
    "arXiv 2409.13373v1 HTML. On solvable instances o1-preview wrongly claimed unsolvability in 0% of Blocksworld and 11.5% of Randomized Mystery Blocksworld. One-shot plan generation from full PDDL.",
    "checked", "Occurrence of false infeasibility is not a new finding.")
add("I1-03", "I1", "novelty table", "AutoPlanBench compares non-interactive plan generation with interactive action selection.",
    "literature", "medium", "confirmed",
    "arXiv 2311.09830v4 HTML (ICAPS 2025 extended). Basic 100, CoT 125, Act 174, ReAct 194 of 260. No analysis of declared unsolvability or early stopping.",
    "checked", "Interactive execution being easier than one-shot planning is established.")
add("I1-04", "I1", "novelty table", "'The Menu Is an Execution Prior' (EMNLP 2026) includes an experiment that holds candidate tools fixed and changes only their order.",
    "literature", "medium", "confirmed",
    "EMNLP 2026 pp. 35904-35917, full PDF text read. Table 6: same 32 official candidates reordered raises ToolBench success from 0.737 to 0.773. The paper is about menu construction, not feasibility judgments or stopping.",
    "checked", "Generic menu sensitivity is studied. Its link to termination is not.")
add("I1-05", "I1", "novelty table", "LLM-Modulo (ICML 2024) is a position paper on pairing LLMs with external verifiers.",
    "literature", "low", "confirmed",
    "arXiv 2402.01817v3 abstract. Self-described position paper, PMLR 235.",
    "checked", "Adding a verifier is not a contribution in itself.")
add("I1-06", "I1", "section 2", "Central question: do interfaces centred on currently executable actions cause agents to conclude wrongly that a task is impossible?",
    "design", "high", "proposal",
    "Existing evidence is two episodes whose sums equal U0, against fourteen successes under the same interface. The corpus has no interface variation, so it cannot identify a cause.",
    "checked", "A candidate question for new work. Not a conclusion available now.")
add("I1-07", "I1", "section 4", "First ask whether any sequence of legal cash-raising actions can reach an unpaid dead end.",
    "method", "high", "confirmed",
    "Answered by code reading. No dead end in hotel-free states. Dead ends can occur when a hotel needs four bank houses that are not there (G7 d338, bank stock 0, no sale offered). The sell-plan validator accepts a bundled hotel-then-houses sale with net-zero stock, which the single-step menu does not offer when stock is short.",
    "checked", "The structural question has an answer without running a policy.")
add("I1-08", "I1", "section 4", "Strengthen the necessity classification by checking payability with initially unavailable mortgages prohibited.",
    "method", "medium", "partly supported",
    "A search is out of scope. For hotel-free states the bound is already exact, since reachable finance without released mortgages equals U0. G20 d327 has two hotels and 15 bank houses, enough for both downgrades in any order.",
    "checked", "The sixteen-case classification does not need a search.")
add("I1-09", "I1", "section 5", "The game prompt lets an agent decide financing is undesirable, so a diagnostic task needs an explicit pay-if-possible objective.",
    "method", "medium", "confirmed",
    "The scenario note reads 'Declare bankruptcy only when you cannot or should not raise enough cash.' The engine also permits bankruptcy on a payable debt, which the official rules do not.",
    "checked", "Both failures state infeasibility as their reason, so they are errors by their own account.")
add("I1-10", "I1", "section 6", "Experiment A: independent assessment and execution instances per state.",
    "design", "medium", "proposal",
    "Changes: a new assessment prompt. Identifies the marginal rate of correct feasibility judgments and the marginal payment rate per state. It does not identify their joint within one response.",
    "checked", "Needs changed authorization.")
add("I1-11", "I1", "section 6", "Experiment B1 changes only how the same information is organized. B2 compares a filtered menu, a broad catalog and a filtered menu with an informational catalog.",
    "design", "high", "proposal",
    "B1 changes prompt structure, which the repository policy treats as a benchmark change needing the owner's explicit request. B2's broad catalog breaks the repository invariant that agents choose only from engine-emitted legal actions. The informational catalog states preconditions, which is the release rule in other words.",
    "checked", "Needs changed authorization and a versioned prompt policy.")
add("I1-12", "I1", "section 6", "Experiment C compares a generic reconsider instruction, a rule reminder, explicit values, a structured inventory and a supplied witness.",
    "design", "medium", "proposal",
    "Each arm changes the delivered prompt. The generic-reconsider control is the right comparison for 'another attempt'.",
    "checked", "Needs changed authorization.")
add("I1-13", "I1", "section 7", "Include payable, dependency, impossible and nominally-sufficient-but-blocked states, on fresh state families, and do not keep old notes when quantities are altered.",
    "design", "medium", "proposal",
    "Sound cautions. The last one conflicts with I4-11, which resets debts on existing holdings.",
    "checked", "If new states are ever authorized, follow this and not I4-11.")
add("I1-14", "I1", "section 8", "An illustrative pilot of 128 execution episodes.",
    "design", "low", "proposal",
    "Not a power calculation by its own statement. No cost is endorsed here.",
    "not checked", "Human decision.")
add("I1-15", "I1", "section 9", "Retitle to 'Financial Feasibility and Premature Termination in LLM Agents' and restructure around a controlled study.",
    "editorial", "medium", "proposal",
    "The title fits a paper with a controlled study. The present corpus has none.",
    "checked", "Not for the present paper.")
add("I1-16", "I1", "section 10", "A second route asks whether agents assess a rival's executable opportunities or react to group completion.",
    "design", "medium", "proposal",
    "No reference value for trades exists in the corpus. The capacity proxy tried on 12 November was flat near an 80 to 88% ceiling.",
    "inherited", "Not available from existing data.")

# ---------------------------------------------------------------- I2: the v3 referee report
add("I2-01", "I2", "verdict", "4/10, reject at the named venues, workshop accept.",
    "rating", "low", "unverified", "A judgment.", "not checked", "Not adopted.")
add("I2-02", "I2", "verdict", "The headline is 16 episodes, 0.2% of the corpus.",
    "statistical", "medium", "partly supported",
    "16/6,989 = 0.23% divides episodes by decisions. The sixteen are 8.5% of 188 episodes and 12.2% of 131 payable debts, and contain 58 decisions.",
    "checked", "The subset is small. The quoted denominator is the wrong unit.")
add("I2-03", "I2", "verdict and item 1", "The 14-of-16 cut came from the referee's script and one reading, and was promoted with no validation.",
    "provenance", "medium", "partly supported",
    "The cut does originate in the 11 November referee text (paper_revision_2026-11-11/feedback/.../inline_review.md line 75). The team then recomputed the bounds from records, printed all sixteen fields and changed 'all 14' to 13 plus 1 tentative. No human coded anything.",
    "checked", "Say plainly that the reading is model-assisted. Human coding is an owner decision.")
add("I2-04", "I2", "what v3 fixed", "Every new number checked reproduces, including the 132/56 first-action split.",
    "empirical", "low", "confirmed",
    "tools/census.py: 132 and 56, with 3 and 50 declarations, 8 forced menus, 42 and 6.",
    "checked", "None.")
add("I2-05", "I2", "item 2", "The fallback mortgages the first listed deed, else sells one building level, and declares only when nothing is listed.",
    "code", "high", "confirmed",
    "decision_resolver.py _fallback_action, lines 624-817, identical at both run commits and at HEAD. It is in the arena package, not the engine. A second, unreferenced copy in llm_runner.py declares bankruptcy before trying to mortgage.",
    "checked", "The description is accurate for the active policy. The stale copy would do the opposite.")
add("I2-06", "I2", "item 2", "Any order of sales and mortgages reaches U*, so that loop pays 16 of 16 by construction.",
    "method", "high", "confirmed",
    "Follows from the coded menu rules for the fifteen hotel-free states. G20 d327 has two hotels and 15 bank houses, and each downgrade needs four, so no order blocks. The engine applies payment once cash covers the debt. This is an analytic inference. I did not execute the fallback.",
    "checked", "Fourteen of sixteen paid means fourteen of sixteen did not stop.")
add("I2-07", "I2", "item 3", "Note and first action are arguments of one tool call. The five Opus cases use a different channel and are pooled with nine notes.",
    "measurement", "high", "confirmed",
    "Tool calls carry the action as the function name and the note as an argument. In first liquidation calls the note is the last argument in 42/42 Sol, 35/38 Grok and 23/50 Gemini responses. Opus recovery responses have no note argument.",
    "checked", "'Prospective' holds for later actions only. The note may justify the first action as easily as cause it.")
add("I2-08", "I2", "item 4", "The unlock is a published rule. PlanBench backs its claims with about 26,000 prompts including domains with misleading or random names.",
    "literature", "medium", "confirmed",
    "Hasbro rules PDF, MORTGAGES section. PlanBench arXiv v4 PDF: about 26,250 prompts, with obfuscations that are 'either misleading words or random alphanumeric strings'.",
    "checked", "The paper already says the episodes test application of a familiar rule.")
add("I2-09", "I2", "item 4", "G18 d344: Gemini mortgages before bankruptcy because it 'forces p4 to pay the 10% mortgage transfer fee'. The engine charges no such fee on inherited deeds.",
    "empirical", "high", "confirmed",
    "Raw G18 d344 applied note. engine.py _handle_bankruptcy reassigns owner with no cash delta. _trade_interest_cost applies only to trades. The official rules do charge the new owner 10% at once, so the agent applied the published rule.",
    "checked", "The agent followed the rulebook where the engine departs from it.")
add("I2-10", "I2", "item 4", "G19 d224: Grok writes 'Must liquidate both reds before bankruptcy is valid'. No such rule exists.",
    "empirical", "medium", "confirmed",
    "Raw G19 d224 applied note, and d225 'Engine may reject bankruptcy while a mortgageable asset remains'. The engine always lists declare_bankruptcy. The same response's assistant content names declare_bankruptcy.",
    "checked", "A wrong belief about this engine, written into the note of a call that contradicts its own content.")
add("I2-11", "I2", "item 5", "Six agents financed a debt they could not pay. Five are Grok. In G9 d194 the note says declare and the call mortgages. In G20 d273 the note says 'Declare now' and the call sells a house.",
    "empirical", "high", "confirmed",
    "tools/census.py and data/six_above_bound.txt. G7 d286, G9 d194, G17 d396, G19 d224, G20 d273 (Grok) and G18 d344 (Gemini). One detail is off: the call at G9 d194 mortgages one deed, and the episode has four mortgage calls. The referee does not say that in all five Grok cases the assistant content names declare_bankruptcy while the received call finances.",
    "checked", "Five of the six 'financing starts' are call-versus-content conflicts. Only G18 d344 is a coherent choice.")
add("I2-12", "I2", "item 6", "The selection rule hides text in the failures. Sol's provider summary at G12 d190 adds that bankruptcy 'might transfer property anyway'. Gemini's provider text at G17 d234 ends by saying it will look for additional options.",
    "empirical", "high", "confirmed",
    "Raw provider fields. Sol: 'It seems like bankruptcy might transfer property anyway, so declaring insolvency could be the best option without needing further actions.' Gemini: 'so I will have to start thinking of additional options.' Gemini's readable text also stops before any conclusion in the successful G8 d257.",
    "checked", "Print both channels for all sixteen. Neither second channel mentions the released collateral.")
add("I2-13", "I2", "item 7", "Both failed sums reuse a reserve figure from carried notes, $130 for Sol at turns 69 and 73 and $30 for Gemini at turn 68. G13 and G20 d327 carried similar figures and went past them. Four of five Opus successes had no carried notes.",
    "empirical", "high", "partly supported",
    "Every stated fact is confirmed. The figure is also the sum of the mortgages the first menu lists (M0 = 130 and 30), so it is recomputable from the menu and is not evidence of anchoring on the note. G13 carried $445 = M0 and G20 d327 carried $325 = M0 and both paid. G5 carried '$774 < $900' and G18 d313 carried 'unpaid even after selling all 5 houses', and both paid.",
    "checked", "On the records, a carried partial inventory precedes success in four episodes and failure in two.")
add("I2-14", "I2", "item 8", "14 of 16 has an exact 95% interval of 62% to 98%. Per system 2/3, 5/6, 5/5, 2/2. Section 3.2 says 'reproducible'. Failures concentrate where the unlock is needed, 2/16 against 1/115, Fisher p = 0.04.",
    "statistical", "medium", "partly supported",
    "tools/stats.py: Clopper-Pearson 61.7 to 98.4, Fisher 0.039. 'reproducible result' is at finance.tex line 38. The p-value depends on pooling 62 debts that need no sale. Against the 53 that need a sale it is 0.13. The comparison was chosen after looking, the single comparison failure is a call conflict, and the sixteen sit in twelve games.",
    "checked", "Replace 'reproducible' with 'repeated'. Do not print the p-value.")
add("I2-15", "I2", "bargaining", "The contrast is deflated and still in the abstract. The ranges are bootstrap intervals. Table 4 omits gaps under five offers while Figure 2 plots block gaps from cells of 3 and 4. Section 4.3 counts an n = 1 cell.",
    "statistical", "medium", "confirmed",
    "3,125 = 5^5 is the full block-bootstrap distribution. Captions of Table 4 and Figure 2. negotiation.tex line 46 says completing-buyer cells contain 1 to 17 asks.",
    "checked", "Shorten the bargaining section and apply one small-cell rule throughout.")
add("I2-16", "I2", "paper-level", "The thesis is existential. Three titles and three theses in three drafts, each tracking the last review.",
    "judgment", "medium", "partly supported",
    "The conclusion does say statements 'sometimes align closely with later action'. Titles changed across the 10, 11 and 12 November rounds. I did not audit every earlier title.",
    "inherited", "Fix the question before any further draft.")
add("I2-17", "I2", "paper-level", "Related work fell from 16 references to 12. NegotiationArena, Vending-Bench, Cattle Trade and DECE are gone.",
    "editorial", "low", "confirmed",
    "Citation keys in the 11 November and 12 November integrated sources: 16 and 12.",
    "checked", "Restore what the argument uses. No quota.")
add("I2-18", "I2", "paper-level", "About 8,200 words over 12 two-column pages.",
    "editorial", "low", "partly supported",
    "Section prose is about 6,600 words plus a 214-word abstract. Extracted text of PDF pages 1 to 12 is about 8,300 words including cards, captions, tables and the first reference page.",
    "checked", "The main text is long for any nine-page format.")
add("I2-19", "I2", "paper-level", "Appendix F names files that are not at the cited repository, whose last commit is 29 October.",
    "artifact", "medium", "confirmed",
    "True when the referee looked and when this round began: local origin/main was a10419d23 of 29 October 2026 and docs/research_raw/paper_revision_2026-11-12/ was untracked. At 19:18 on 14 November a checkpoint commit 863f8ef7, which I did not make, added that folder, and the local origin/main ref now points at it. I did not query the remote. The named files now sit under docs/research_raw/paper_revision_2026-11-12/integrated/, a path the appendix does not give.",
    "checked", "The appendix should cite the folder path and commit.")
add("I2-20", "I2", "paper-level", "The repository URL carries the owner's name, there is no author block, and the human contribution is unstated. Appendix C is still present. Page 6 has a half-column blank and Incident 2 is split by a table and a figure.",
    "editorial", "low", "confirmed",
    "manuscript.tex author is empty. supplement.tex prints the URL and the question map with the row 'No independent capability axis available'. Rendered pages 6 and 7.",
    "checked", "Owner decisions on authorship and anonymity. Layout is mechanical.")
add("I2-21", "I2", "questions 1-4", "Replay each saved request 30 times per model. Strip carried notes. State the rule or add values. Change the rule.",
    "design", "high", "proposal",
    "All are provider calls on edited or unedited historical prompts. A replay identifies today's response distribution at one delivered context. Sending one agent's request to another model gives that model a different player's name and notes. See review.md section 6.",
    "checked", "Needs changed authorization.")
add("I2-22", "I2", "question 5", "What do the first texts say across all 188 episodes, including the six futile ones?",
    "design", "high", "proposal",
    "Existing-record work. I read all channels for the sixteen and for every decision of the six. I counted named-action conflicts for all 338 liquidation decisions. I did not code the other first texts.",
    "checked", "In scope now. Needs a written criterion, and the result is a model reading.")
add("I2-23", "I2", "question 6 and step 3", "Compute value destroyed relative to the cheapest sufficient plan and relative to the fallback. Run the fallback from the 131 payable states.",
    "design", "high", "proposal",
    "Both need a search or a policy execution, which the standing scope forbids. A search-free description is possible: with cash plus listed mortgages sufficient, agents sold buildings in 2 of 62 paid episodes, and where a sale was required no paid episode sold $100 or more beyond the minimum left after listed mortgages.",
    "checked", "The description suggests little variance on natural states under a mortgage-first cost ordering.")
add("I2-24", "I2", "step 3", "Have two humans code the 16 texts and the 74 rejections.",
    "design", "medium", "proposal",
    "No human coder is on the team. The assistants must not label their reading as human validation.",
    "checked", "Human decision.")
add("I2-25", "I2", "steps 1-2", "Replay probes cost about $40 and each ablation arm about $40.",
    "cost", "low", "unverified",
    "USD 141.39 over 6,989 decisions is $0.020 per decision and $0.016 per attempt. Refused Opus attempts are unpriced and Opus needs two calls per decision. I make no cost estimate.",
    "checked", "No cost is endorsed.")
add("I2-26", "I2", "verdict", "This is the third manuscript in 25 hours with zero new measurements.",
    "provenance", "low", "partly supported",
    "No new evaluations were run, which is the standing rule. New measurements on existing records were added in each round. I did not verify the hour count.",
    "not checked", "None.")

# ---------------------------------------------------------------- I3: the comparator table
add("I3-01", "I3", "table", "AgentMonopoly has 120 games per its repository.",
    "literature", "low", "partly supported",
    "The repository README lists 40, 40, 20 and 20. The paper's Table 3 lists 40, 40, 40 and 20, which is 140.",
    "checked", "Cite the paper's count and note the README.")
add("I3-02", "I3", "AgentMonopoly", "Its prompt carries a rules file stating that houses must be sold before a group can be mortgaged.",
    "literature", "medium", "unverified",
    "The paper says the acting agent receives 'the rules'. Neither the paper text nor the README I could read states the sentence. I did not open the repository's backend files.",
    "checked", "Do not repeat the specific sentence.")
add("I3-03", "I3", "AgentMonopoly", "It renames streets to places in Oldenburg, runs at temperature 0 on local open-weight models, reports proposals per 100 dice rolls, and forbids public messages that contradict the action.",
    "literature", "medium", "confirmed",
    "arXiv 2610.29330v2 HTML for all four.",
    "checked", "The last point is a design difference worth stating. This paper's prompt permits deception and has unpoliced channel conflicts.")
add("I3-04", "I3", "FinBoardBench", "Five corrective retries with error feedback, against one here.",
    "literature", "low", "confirmed",
    "Appendix E: at most five execution failures in Monopoly's main decision phase, then a forced fallback.",
    "checked", "A harness difference. Not a defect of this paper.")
add("I3-05", "I3", "Vending-Bench", "The context-fill analysis gives a correlation of 0.167. A memory ablation found larger memory did worse.",
    "literature", "low", "confirmed",
    "arXiv 2502.15840v1: Pearson 0.167 across nine models. GPT-4o mini at 10k, 30k and 60k tokens.",
    "checked", "The memory ablation is the kind of test the carried-note question would need.")
add("I3-06", "I3", "Vending-Bench", "The v2 board lists Gemini 4 Argon, Grok 4.7 and GPT-6 Sol with scores and standard errors, so an external capability axis is available.",
    "literature", "low", "partly supported",
    "The visible top ten shows GPT-6 Sol, Gemini 4 Argon and GPT-6.1 Sol with a plus-or-minus value whose statistic is not labeled. Grok 4.7 and Claude Opus 5.5 are not in the visible ten. The evaluated system here is GPT-6.1 Sol.",
    "checked", "Four points on one audited-as-flawed benchmark do not make a capability curve. The appendix row can say so.")
add("I3-07", "I3", "Li et al.", "It classifies all 2,583 emails, checks the classifier against a hand-labeled set, repeats with three judge families, uses mixed-effects models and a cluster bootstrap, and verified that prompts contain no conduct instruction. This paper's prompt suggests deception.",
    "literature", "medium", "confirmed",
    "arXiv 2608.14825v3 HTML. The hand-labeled set is 50 emails by one annotator who wrote the codebook. 52 of 58 payloads were machine-readable. The MonopolyBench system prompt says 'bluff, deceive' and 'Deception in public chat is allowed'.",
    "checked", "Nothing here can be called emergent conduct, and the paper does not call it that.")
add("I3-08", "I3", "table", "This paper has one replicate per condition, no manipulated variable, no reference point and no headline metric.",
    "judgment", "high", "confirmed",
    "Twenty games, five seeds, four rotations, no repeated seed and rotation cell, no intervention.",
    "checked", "Accurate description of an observational corpus.")
add("I3-09", "I3", "where ahead", "Neither Monopoly paper reports a statistical test.",
    "literature", "low", "confirmed",
    "AgentMonopoly reports none. FinBoardBench reports percentile bars and no test.",
    "checked", "None.")
add("I3-11", "I3", "table", "Vending-Bench evaluates 10 models with 5 runs each, and the Arena study is a NeurIPS 2026 paper.",
    "literature", "low", "unverified",
    "Vending-Bench arXiv v1 lists nine LLMs plus one human. I did not read a later version. The arXiv v3 page for the Arena study that I read names no venue.",
    "checked", "Cite versions actually read.")
add("I3-10", "I3", "what to take", "Take rules in the prompt, same-model tables, one manipulated factor, a fixed opponent pool, a judge label on every trade, one headline score, five replicates, a memory ablation, a human or scripted reference, construct definitions, a human-labeled set and mixed-effects models.",
    "design", "medium", "proposal",
    "Several items contradict R2 (judge labels, fixed pool, human reference) and one contradicts I4's own 'unstated rule' arm (rules in the prompt). All but construct definitions need new games or calls.",
    "checked", "See review.md section 7.")

# ---------------------------------------------------------------- I4: the liquidation and oracle proposal
add("I4-01", "I4", "taken", "Saved-state branching and repeated probes at fixed states already ship in MafiaScope on a 672-game corpus.",
    "literature", "medium", "confirmed",
    "arXiv 2607.10645v3 HTML (30 October 2026). Replay from saved snapshots, 220 continuations from 11 decisions, five repeated probes at nine saved states, 672 recorded games.",
    "checked", "Replay probing is a method to cite, not a contribution.")
add("I4-02", "I4", "taken", "The gap between a model's own rule check and its tool call is named unpropagated refutation, with a 200-position atomic-chess benchmark.",
    "literature", "medium", "partly supported",
    "ICML 2026 workshop poster (Agents in the Wild), Co and Konuganti. 200 positions, rule stated in the system prompt. The gap itself is described qualitatively. The measured quantity is Win% loss.",
    "checked", "A named precedent for say-do gaps. It is a workshop paper with no gap metric.")
add("I4-03", "I4", "taken", "Counterfactual rules as a recall control are Wu et al. 2024.",
    "literature", "low", "confirmed",
    "NAACL 2024 long paper, 11 tasks, default-to-counterfactual drop. The abstract page does not list the tasks.",
    "checked", "Cite if any altered-rule arm is ever run.")
add("I4-04", "I4", "taken", "Memory errors compounding into later decisions is studied at ACL 2026 as error propagation.",
    "literature", "low", "confirmed",
    "Xiong et al., ACL 2026 long, abstract read. Full paper not read.",
    "checked", "A carried-note effect would not be new as a general idea.")
add("I4-05", "I4", "open 1", "Liquidation scored against a computed optimum is open. AgentMonopoly has no liquidation and FinBoardBench does not score it.",
    "literature", "medium", "partly supported",
    "Consistent with what I read in both papers. FinBoardBench has a fund-raising phase with no metric. Two papers do not establish that nobody has done it, as the referee also says.",
    "checked", "No 'to our knowledge' claim without a real search.")
add("I4-06", "I4", "open 2", "A planted number in the agent's notes moving a later money decision is open, with n = 2 here.",
    "design", "high", "proposal",
    "See I2-13. The observed figure equals the menu's listed mortgage total and four episodes with a carried partial inventory paid.",
    "checked", "A hypothesis with thin and mixed support in the records.")
add("I4-07", "I4", "open 3", "The engine departs from standard Monopoly and the prompt carries no rules.",
    "empirical", "medium", "confirmed",
    "Against the official rules PDF the engine differs in at least four ways that bear on liquidation: bankruptcy may be declared on a payable debt, buildings pass intact to a player creditor, inherited mortgaged deeds carry no interest, and a hotel sale is offered only when the bank holds four houses. The stored system prompt has no rules text.",
    "checked", "A keyword screen finds the inherited-interest belief in 8 liquidation decisions, 7 of them Grok.")
add("I4-07b", "I4", "open 3", "One agent mortgaged to dodge a fee the engine does not charge.",
    "empirical", "low", "incorrect",
    "G18 d344 note: mortgaging 'before declaring bankruptcy forces p4 to pay the 10% mortgage transfer fee'. Gemini mortgaged to make the creditor pay a fee, not to avoid one. The engine charges nobody.",
    "checked", "The episode is still a case of acting on the published rule.")
add("I4-08", "I4", "the paper", "Claim: frontier agents fail a sub-task that 15 lines of code solve, and the failure is steerable by a number in their own notes.",
    "science", "high", "partly supported",
    "First half: 3 of 131 payable debts ended in declaration and one of those is a call that contradicts its own text. Second half has no test behind it.",
    "checked", "Not a claim the present paper can make.")
add("I4-09", "I4", "oracle", "Compute the minimum-restoration-cost plan by exhaustive search, with cost equal to building value lost plus 10% to lift each mortgage, and score regret in dollars.",
    "design", "high", "proposal",
    "Assumes the agent will restore the position, that rent lost while mortgaged is zero, that bank-stock effects on rivals are zero and that local cost tracks winning. The engine's lift cost uses a float ceiling that overcharges $1 on five principals. A search is out of scope.",
    "checked", "Identifies excess local liquidation cost under a stipulated objective. It is not 'value destroyed'.")
add("I4-10", "I4", "metrics", "Action-only metrics: paid when payable, declared when unpayable, regret.",
    "design", "medium", "proposal",
    "'Declared when unpayable' is not a correctness criterion. Eight of 56 such menus offer only bankruptcy, the debtor is eliminated either way, and five of the six observed departures are call conflicts.",
    "checked", "Only 'paid when payable' has a clear right answer.")
add("I4-11", "I4", "states", "Use the 188 natural episodes, the same holdings with the debt reset into the unlock band, and states from self-play of scripted baselines.",
    "design", "medium", "proposal",
    "Resetting a debt leaves notes and timeline that describe the original quantities, which I1-13 warns against. Scripted self-play is an engine execution.",
    "checked", "Needs changed authorization.")
add("I4-12", "I4", "validation", "The template is PokerBench: 11,000 spots plus a check that higher-scoring models win more. The version here hands liquidation to the solver in 20 fresh games and measures the change in eliminations.",
    "design", "high", "partly supported",
    "PokerBench has 1,000 plus 10,000 spots. Higher score meant more winnings among three checkpoints of one fine-tuned model, and GPT-4 beat the best checkpoint with a lower score. PokerBench never placed a solver in live play. Every complete game here eliminates exactly three players, so the count of eliminations cannot change.",
    "checked", "The proposed outcome is degenerate. Agents already paid 128 of 131 payable debts.")
add("I4-13", "I4", "cost", "About $0.02 per call, $150 for the core, $75 per arm, $140 for validation games.",
    "cost", "low", "unverified",
    "The per-decision mean matches the accounting field. Everything else is a forecast.",
    "checked", "No cost is endorsed.")
add("I4-14", "I4", "order of work", "Compute regret on the 128 paid episodes first. Median regret near zero means the construct is saturated.",
    "design", "high", "proposal",
    "A search is out of scope. The search-free description in I2-23 points toward saturation under a mortgage-first ordering.",
    "checked", "Evidence against building the oracle first.")
add("I4-15", "I4", "fixes", "Rename private_thought and smoke-test for refusals, set one reasoning budget, log call-versus-text conflicts, fix the float interest bug and the hotel menu lock, delete the stale fallback, commit the appendix files.",
    "code", "medium", "partly supported",
    "Confirmed code facts: _unmortgage_cost uses math.ceil(value * 1.1), a hotel deed is sellable only with four bank houses, and LlmRunner._fallback_action is unreferenced. The refusal trigger is not identified, so renaming the field is a guess that needs provider calls. Conflict logging can be done on existing records. I count 9 named-action conflicts in 338 liquidation decisions, all Grok.",
    "checked", "Engine and prompt changes are forbidden in this round. Conflict counting is in scope.")
add("I4-16", "I4", "paper-level", "Nine pages, one claim, named human authors, mixed-effects logistic models with state as a random effect, at least 40 references.",
    "editorial", "low", "proposal",
    "A reference count is an arbitrary quota. Mixed-effects models suit a designed study and do not rescue sixteen retrospective episodes.",
    "checked", "Authorship and venue are owner decisions.")
add("I4-17", "I4", "estimate", "A real planted-number effect gets a plausible 6, without it a 5, and the current draft stays a 4.",
    "rating", "low", "unverified", "A forecast.", "not checked", "Not adopted.")

# ---------------------------------------------------------------- F: findings of this review that no referee stated
add("F-01", "this review", "tools/conflicts.py", "In 338 liquidation decisions the action named in assistant content differs from the applied call 9 times, all Grok. Seven are 'content names declare, call finances' on unpayable debts.",
    "empirical", "high", "confirmed",
    "data/liquidation_named_vs_applied.json. 27 of Grok's 56 liquidation decisions name an action in content.",
    "checked", "Of the nine first actions that go against the bound, six are Grok call conflicts. This revises the first-action finding I contributed on 12 November.")
add("F-02", "this review", "data/sixteen_first_decisions.txt", "A carried note with an incomplete inventory preceded payment in G5 d263 and G18 d313 as well as in G13 d195 and G20 d327.",
    "empirical", "medium", "confirmed",
    "G5 turn 141 note: 'my total liquidatable cash + houses is $774 < $900'. G18 turn 90 note: 'only roll 4 (Virginia $700) is unpaid even after selling all 5 houses ($500)'.",
    "checked", "Weakens the anchoring hypothesis.")
add("F-03", "this review", "Hasbro rules PDF and engine.py", "Agents applied official rules that the engine does not implement: interest on inherited mortgaged deeds, and liquidation before bankruptcy.",
    "empirical", "medium", "confirmed",
    "Official text: 'the new owner must at once pay the Bank the amount of interest on the loan'. Engine: no charge. Screen hits: G7 d287, G9 d195-197, G15 d203, G16 d447, G17 d397 (Grok), G18 d344 (Gemini).",
    "checked", "Behavior tracks the published rulebook in both directions. A keyword screen, not validated coding.")
add("F-04", "this review", "G18 d313 prompt", "Grok's request at G18 d313 shows Gemini selling all pink houses and then mortgaging St. Charles one turn earlier.",
    "empirical", "low", "confirmed",
    "public_timeline_last_20 entries at turns 105 and 109.",
    "checked", "The two G18 episodes are not independent. The timeline can demonstrate the dependency.")
add("F-05", "this review", "game count", "Twenty complete games produce exactly sixty eliminations, three per game.",
    "statistical", "medium", "confirmed",
    "128 paid plus 60 eliminated episodes. No turn cap.",
    "checked", "Any outcome defined as a change in the number of eliminations is zero by design.")

out = Path(__file__).resolve().parents[1] / "claim_ledger.json"
doc = {
    "review": "paper_review_2026-11-14, Fable 5.2",
    "verdict_vocabulary": ["confirmed", "partly supported", "incorrect", "unverified", "proposal"],
    "basis_vocabulary": {"checked": "checked this round against the named record or primary source",
                         "inherited": "relies on an earlier team result not redone this round",
                         "not checked": "not examined this round"},
    "sources": {"R1": "inputs/pasted-text-2.txt", "R2": "inputs/pasted-text-3.txt",
                "I1": "inputs/inline_feedback.md, experimental program (lines 5-599)",
                "I2": "inputs/inline_feedback.md, v3 referee report (lines 603-705)",
                "I3": "inputs/inline_feedback.md, comparator table (lines 709-781)",
                "I4": "inputs/inline_feedback.md, liquidation and oracle proposal (lines 783-859)"},
    "note": "One discrete claim is marked incorrect (I4-07b). Other parts I found wrong sit inside 'partly supported' entries: I2-02 (unit of the denominator), I2-11 (one deed at G9 d194), I2-13 (the anchoring reading), I3-01 (game count against the paper), I4-12 (PokerBench design and the eliminations outcome). Entries with id F-xx are findings of this review that no referee stated.",
    "claims": L,
}
out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
import collections
print(len(L), collections.Counter(c["verdict"] for c in L), collections.Counter(c["basis"] for c in L))
assert len({c["id"] for c in L}) == len(L)
