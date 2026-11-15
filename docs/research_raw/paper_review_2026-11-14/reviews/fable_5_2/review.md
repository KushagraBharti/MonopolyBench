# Review of the 14 November feedback, Fable 5.2

Independent assessment, written before opening any peer review of this round. Every number below that I call checked was recomputed this round from raw `decisions.jsonl` files, engine source at the run commits, or a primary paper. The scripts are in `tools/` and their outputs in `data/`. Nothing was executed in the engine, replayed, or sent to a provider. The 84-file pin matched before I started.

Source tags: R1 is `pasted-text-2.txt` (the 5.5/10 report), R2 is `pasted-text-3.txt` (the comparator discussion), and I1 to I4 are the four pieces in `inline_feedback.md` in order (the experimental program, the v3 referee report, the comparator table, the liquidation and oracle proposal).

## 1. Verdict in brief

The referees are right about the paper's main weakness and wrong about several of the remedies.

The finance section is the only part with a checkable answer, and its headline is worded more strongly than the evidence allows. Reading the engine shows that paying a payable debt needs nothing except not declaring bankruptcy. Fourteen of sixteen paid therefore means fourteen of sixteen did not stop. The informative decision is the one at the first menu, and the paper has that decision for all 188 episodes.

Checking that decision against every text channel changes the picture again. Nine first actions go against what the player's assets could cover. Six of the nine are Grok tool calls that contradict the action named in the same response. That leaves three coherent departures in 188 episodes. Two are the false infeasibility declarations the paper already describes. The third is a deliberate mortgage on an unpayable debt, justified by an official Monopoly rule that the engine does not apply.

So the corpus supports a narrow and clean observational statement. Agents almost always continue when their assets cover a debt and stop when they do not. The two times one stopped wrongly, its sum equalled the cash, salvage and mortgages visible on the menu, and left out what a sale would release. The corpus cannot say how often that happens, why, or what would prevent it.

None of the three new theses in the feedback can be supported from existing data. The planted-number idea rests on a coincidence the records explain more simply. The regret metric encodes a contestable objective and looks saturated on the natural states. The interface hypothesis has no variation to test it on. Each needs an intervention that the standing scope forbids, and whether to lift that scope is the owner's decision.

I recommend that the present paper stay observational, shrink its claim about anticipation, lead with the stop decision, print both text channels, report call-versus-text conflicts as a result, and cut the bargaining section to what survives composition.

## 2. What the records show

### 2.1 Payment measures not stopping

The v3 referee (I2) says the fallback policy would pay all sixteen necessity debts because any order of sales and mortgages reaches the upper bound. I checked this against the source. The engine and resolver files are the same at both run commits, and the current tree has no change under `python/` or `contracts/` since the second.

The description of the policy is accurate. `decision_resolver.py` lines 624 to 817 mortgage the first listed deed, otherwise sell one building level at the first listed space, and declare only when neither is listed. This lives in the arena package and not the engine. A second copy in `llm_runner.py` is unreferenced and does the opposite. It checks `declare_bankruptcy` before `mortgage_property`, so it would declare at every liquidation menu.

The structural claim follows from three pieces of engine code.

- A deed can be mortgaged when it is unmortgaged and no deed in its group has a building (`_mortgageable_space_indices`). Mortgaging never removes a sale option.
- A building can be sold from any deed at the group's highest level (`_sellable_building_space_indices`). In a group with no hotel, some deed always qualifies until the group is empty. Selling never removes a mortgage option and adds to bank stock.
- After each action the engine pays the debt as soon as cash covers it (`_resolve_pending_payment`). There is no separate pay action.

In a state with no hotel, every maximal sequence of offered financing actions therefore raises exactly cash plus all salvage plus every unmortgaged deed, which is U*. If U* covers the debt, the sequence pays. The only way to fail is to declare.

Hotels are the exception. A hotel deed is listed for sale only when the bank holds four houses, so a sequence can reach a state with assets left and nothing offered. G7 d338 is that case, with bank stock at zero. The sell-plan validator checks stock and evenness only at the end of a plan, so a bundled hotel-then-houses sale would pass with net-zero stock, but the menu does not offer a sale at all when no deed qualifies.

Fifteen of the sixteen necessity states have no hotel. G20 d327 has two brown hotels and fifteen bank houses. Two downgrades need eight houses in the worst order, so no order blocks. The claim holds for all sixteen. I derived this from code and recorded state. I did not run the fallback.

Across the corpus, 108 of the 131 payable debts are hotel-free. For those the statement is a property of the rules. For the other 23 I make no claim beyond the fact that the agents paid all of them.

This is the largest correction to my own earlier position. On 12 November I insisted the paper never print "a loop pays 131 of 131", because no loop had been run. That was the right rule for a measured baseline. It was a poor reason to stay silent about a property of the menu. The manuscript says continuing "need not imply that a player has worked out a complete route". The stronger and true sentence is that continuing is sufficient.

Two consequences follow. The paper's phrase "dependent execution" describes a sequence that any continuing player completes. And the reactive reference policy that R1, R2 and I1 ask for does not need to be run to know its result on most states. A paragraph with code citations answers the question.

### 2.2 The stop decision, restated

By applied first action the counts are as printed. Assets cover the debt in 132 episodes and agents declare in 3. Assets fall short in 56 and agents declare in 50, where 8 menus offer nothing else. Six start financing a debt they cannot pay.

I read every channel for all nine departures and counted named-action conflicts across all 338 liquidation decisions (`tools/conflicts.py`). Grok's assistant content names an action in 27 of its 56 liquidation decisions. In 9 of those the named action differs from the received call. No other system's assistant content names an action in a liquidation decision, so this check can detect a conflict only for Grok.

| Episode | System | Assets cover debt | Text | Received call |
|---|---|---|---|---|
| G12 d190 | Sol | yes | Note and provider summary both conclude payment is impossible | declare |
| G17 d234 | Gemini | yes | Note concludes payment is impossible | declare |
| G12 d249 | Grok | yes | Content names a sale, note describes a sale route | declare |
| G7 d286 | Grok | no | Content names declare with a correct sum. The applied note is a verbatim copy of a turn-101 note | mortgage |
| G9 d194 | Grok | no | Content names declare. The applied note says "Declare bankruptcy now" | mortgage |
| G17 d396 | Grok | no | Content names declare. The applied note says the sale is "forced and insufficient" | sell |
| G19 d224 | Grok | no | Content names declare. The applied note says liquidation must precede a valid bankruptcy | mortgage |
| G20 d273 | Grok | no | Content names declare. The applied note says "Declare now" | sell |
| G18 d344 | Gemini | no | Note says the mortgage will not cover the debt but will force the creditor to pay a 10% fee | mortgage |

Six of the nine are Grok calls that contradict the action named in the same response. The paper reports that five of the six above-bound cases "start financing" and that none is a fallback. Both statements are true and together they mislead. Five of the six were not choices to finance.

The v3 referee found two of these (G9 d194 and G20 d273) and read them as statements diverging from actions. That is correct as far as it goes. The fuller description is that Grok's text and Grok's call come apart in a specific, countable way, concentrated in exactly the cases the paper treats as decisions. One detail in the referee's account is off. The call at G9 d194 mortgages one deed. The episode contains four mortgage calls.

G9 shows something else. After the first conflicting mortgage, Grok's later notes adopt a reason for continuing. At d196 the provider summary says "I have already mortgaged Mediterranean Avenue and Pennsylvania Avenue. I will continue that strategy for consistency". The stated plan followed the action.

I contributed the first-action count on 12 November and presented the departures as agent decisions. That was incomplete. The corrected statement is that the applied first action agrees with the asset bound in 179 of 188 episodes, and in six of the nine exceptions the response's own text names the bound-consistent action. I did not code the notes of the other 179 for a stated feasibility judgment.

### 2.3 The two failures in both channels

The referee is right that the selection rule hid text where it mattered.

At G12 d190 Sol's note totals $53 cash, $225 salvage and $130 of listed mortgages to $408 against $500. The provider summary repeats the sum and adds "It seems like bankruptcy might transfer property anyway, so declaring insolvency could be the best option without needing further actions". That is a second rationale. Having judged payment impossible, Sol reasons that liquidating first would be pointless. Neither channel mentions the red mortgages.

At G17 d234 Gemini's note totals $500 salvage and $30 for Baltic to $530 against $550. The provider text stops earlier. It counts the $500 and ends "so I will have to start thinking of additional options". It reports 333 reasoning tokens and shows about seventy words.

That ending should not be read as Gemini considering the released collateral and rejecting it. Gemini's readable text stops in the same way in a success. At G8 d257 it ends "I need to make a more holistic plan" with no mention of the released mortgages, and the note in the same response states them. At G18 d309 the readable text covers only the house sale and the note adds the mortgage. Gemini's readable field often ends before the conclusion. The paper's caution that completeness is not established is correct and now has direct examples.

Both failed sums equal U0 to the dollar. Both texts assert impossibility in plain words ("No legal liquidation can save me", "I cannot raise $550"). Under the game prompt a player may decline to finance, so the texts matter. These two are errors by their own account.

### 2.4 The carried-note hypothesis

The referee says both failed sums reuse a reserve figure from the agent's own earlier notes, and proposes that a number in the notes steers the decision. I read the ten carried notes in all sixteen first requests.

| Episode | Carried notes about liquidation capacity | Outcome |
|---|---|---|
| G1 d476 Grok | Full inventory with the rule. "yellows cannot be mortgaged while it stands", "yellow mortgages ~$400 as reserve" | paid |
| G2 d216 Sol | "all spare collateral already mortgaged". No figure for the yellows | paid |
| G4 d270 Gemini | An earlier payment by house sales. No capacity figure | paid |
| G4 d308 Opus | Ten stale notes from turns 62 to 65, about a purchase | paid |
| G5 d263 Gemini | "my total liquidatable cash + houses is $774 < $900" at turn 141. Salvage only | paid after revising |
| G6 d185 Opus | None | paid |
| G8 d257 Gemini | An earlier payment. No capacity figure | paid |
| G11 d203 Opus | None | paid |
| G12 d190 Sol | "$130 emergency mortgage capacity" six times, turns 57 to 73 | declared |
| G13 d195 Gemini | "$445 in mortgageable non-Dark-Blue properties" in three notes at turn 75 | paid |
| G17 d234 Gemini | "$30 emergency reserve" for Baltic once, turn 68 | declared |
| G17 d254 Opus | None | paid |
| G18 d309 Gemini | The rule applied to a rival. "p3 must sell all 5 Dark Blue houses and mortgage a Dark Blue property" | paid |
| G18 d313 Grok | "only roll 4 (Virginia $700) is unpaid even after selling all 5 houses ($500)" at turn 90. Salvage only | paid |
| G20 d291 Opus | None | paid |
| G20 d327 Sol | "$325 idle mortgage capacity" three times, turns 102 to 104, and once more without the figure at turn 106 | paid |

Every fact the referee states is confirmed, including the turn numbers and the four Opus episodes with no notes. The interpretation is weaker than presented, for three reasons.

First, the figure is not a foreign number. $130 is what Baltic and two light blues mortgage for. $30 is Baltic. Those are the mortgages the first menu lists. An agent that counts only listed mortgages writes $130 or $30 with or without a note. The match to the dollar cannot separate anchoring on a note from recomputing the menu.

Second, the same kind of figure appears before successes. G13 carried $445 and G20 d327 carried $325. Each equals that state's listed mortgage total, and each agent went past it. The referee names these two.

Third, there are two more counterexamples the referee does not name. G5 carried an explicit infeasibility comparison for the same deeds and same system as the G17 failure, and Gemini revised it and paid. G18 d313 carried a salvage-only maximum and Grok paid.

Among episodes with an applied note, a carried partial inventory precedes success four times and failure twice. There is no dose pattern either. Sol repeated its figure six times before failing and three times before succeeding.

The hypothesis is not refuted. A carried partial inventory is present in both failures. It is not supported well enough to be a headline, and only an intervention that plants a figure different from the menu total could test it.

### 2.5 What the sixteen texts state

R1 and R2 both ask for the sixteen texts to be scored on separate dimensions. This is my reading, made from the full fields and the executed routes in `data/sixteen_routes.json`. It is one model's reading with source in hand. It is not human validation.

| Episode | Field | How the released resource appears | Figures | Executed route | Cash after |
|---|---|---|---|---|---|
| G1 d476 Grok | note | States the rule. Sale first, then one yellow mortgage | Correct | As stated | $56 |
| G2 d216 Sol | note | States the rule. Marvin plus one other | Yellow total given as $430, true $400 | As stated | $103 |
| G4 d270 Gemini | note | Ordered list. Sell four houses, then mortgage two yellows | Sale value correct, mortgages not valued | As stated | $86 |
| G4 d308 Opus | provider | Budget. Seven houses plus three red mortgages total $910 | Correct, equals U* | Used two of three mortgages | $0 |
| G5 d263 Gemini | note | States the rule. Budget $1,049, remainder $149 | Correct, equals U* | As stated | $149 |
| G6 d185 Opus | provider | Budget with an order. Boardwalk first, then houses, then pinks | Correct, $770 raised matches U* | Order as stated, one pink mortgage | $58 |
| G8 d257 Gemini | note | States the rule. Sale "will also unlock" both dark blues | Mortgages not valued | Boardwalk and Baltic | $13 |
| G11 d203 Opus | provider | Budget in two stages, $276 then $556, remainder $56 | Correct, equals U0 then U* | As stated, everything | $56 |
| G12 d190 Sol | note | Omitted. Sum equals U0 | Correct for what is counted | Declared | |
| G13 d195 Gemini | note | Ordered list. Sell, mortgage Park Place plus $335 elsewhere | Correct | As stated, exact | $28 |
| G17 d234 Gemini | note | Omitted. Sum equals U0 | Correct for what is counted | Declared | |
| G17 d254 Opus | provider | Budget. Five houses plus three red mortgages total $843 | Correct, equals U* | One mortgage sufficed | $63 |
| G18 d309 Gemini | note | States the rule. Sale "will allow me to mortgage St. Charles" | Correct | As stated | $32 |
| G18 d313 Grok | note | Ordered list. Houses yield $500, "still need to mortgage PP or BW afterward" | Correct | As stated | $126 |
| G20 d291 Opus | provider | Posed as a question | Compares $680 of proceeds with the $1,000 debt and omits $275 cash | Sold, then three mortgages | $25 |
| G20 d327 Sol | note | Aggregate budget $1,414, remainder $14 | Correct, equals U* | Everything | $14 |

Five notes state the enabling relation in words (G1, G2, G5, G8, G18 d309). Three more give an ordered list that implies it (G4 d270, G13, G18 d313). Five give a budget that includes the released deeds, four of them Opus provider texts and one Sol's aggregate. One asks. Two omit.

Six texts state a total that equals U* exactly. Three state a remainder that the route then realizes to the dollar (G5, G11, G20 d327). One has a wrong figure and pays anyway. One has confused accounting and pays anyway. R1's reading of G20 d291 is confirmed in every number.

The team's "thirteen plus one plus two" survives. It was always coarser than the texts. The split above is the more informative statement and costs no new evidence.

### 2.6 Statement and action are one response

The referee is right. The action is the function name of the tool call and the private note is one of its arguments. In first liquidation calls the note is the last argument in 42 of 42 Sol responses, 35 of 38 Grok responses and 23 of 50 Gemini responses. Within a response the note is written after the action is chosen.

The five Opus texts are a different object. They are a provider reasoning field written before the call, in action-only recovery responses that have no note argument. The paper pools nine texts written after the action name with five written before it.

"Prospective" is accurate for one thing. The text at the first decision comes before the menu shows the released mortgages. It is not accurate for the first action. For the two failures the note and the declaration arrive together, and the note may justify the declaration as easily as cause it. G9 in section 2.2 is a recorded case of reasons following an action.

### 2.7 Rule recall runs in both directions

The paper says the financing dependency is a published rule and that the episodes show its application. The referee adds that the corpus shows recall misfiring. I checked the official rulebook text and the engine.

The official rules say that before an improved property can be mortgaged, all buildings on its color group must be sold. The engine matches. The same rulebook says a player is bankrupt when they owe more than they can pay, that a bankrupt player's buildings are sold to the bank with the cash going to the creditor, that the new owner of a mortgaged deed must at once pay 10% interest, and that hotels may be sold at once. The engine differs on all four. It lets a player declare on a payable debt, passes buildings intact, charges nothing on inherited mortgaged deeds, and offers a hotel sale only when the bank holds four houses. The system prompt states none of this.

At G18 d344 Gemini mortgages on an unpayable debt because that "forces p4 to pay the 10% mortgage transfer fee". The engine charges no fee. The referee's quote is exact. The referee's later description of this agent as mortgaging "to dodge a fee" has the direction wrong. Gemini meant to impose one.

At G19 d224 Grok's note says "Must liquidate both reds before bankruptcy is valid", and at d225 "Engine may reject bankruptcy while a mortgageable asset remains". The engine always offers the declaration.

A keyword screen over all liquidation notes and provider texts finds the inherited-interest belief in eight decisions, seven of them Grok (G7 d287, G9 d195 to d197, G15 d203, G16 d447, G17 d397) and one Gemini. In five the applied action was a mortgage. This is a screen and not a validated coding.

So the agents play by the rulebook. Where the engine agrees with it they are right, and where the engine departs they are wrong. That is a coherent description of the information condition and it is better evidence for recall than the sixteen successes alone. It is still a handful of episodes.

### 2.8 The middle row of Table 2

R1 notes that U0 at or above the debt does not prove a route that avoids released mortgages. The logic is right. No episode is misclassified.

Of the 53 episodes in that row, 47 were paid with no released mortgage, which is an observed witness each. One is G12 d249, where the stored audit sells five pink houses. Five were paid using released collateral (G3 d228, d356, d461, d482 and G18 d428). For each of the five I checked by hand that building sales alone, or with the listed mortgages, cover the debt under the sale rule as coded. Those five checks were not executed in the engine and should be labeled that way if used.

For hotel-free states the bound is exact in both directions, because every building is sellable in some order. I1's proposed search with released mortgages prohibited is not needed for the sixteen.

### 2.9 Statistics

The exact 95% interval for 14 of 16 is 61.7% to 98.4%. The referee's figure is right.

The Fisher test offered "in your favor" gives p = 0.039 for 2 of 16 against 1 of 115. I would not print it. The comparison group pools 62 debts that need no sale, where this failure cannot arise. Against the 53 that need a sale the value is 0.13. The split was chosen after looking. The single failure in the comparison group is a Grok call conflict. The sixteen sit in twelve games, with two each in G4, G17, G18 and G20, and at G18 d313 Grok's request shows Gemini's sale-then-mortgage from one turn earlier.

"0.2% of the corpus" divides sixteen episodes by 6,989 decisions. The sixteen are 8.5% of episodes and 12.2% of payable debts, and contain 58 decisions. The subset is small. The quoted share uses the wrong unit.

"Reproducible result" in section 3.2 is wrong. Each state was observed once. I passed that word twice.

The appendix ranges are the percentile block bootstrap, fully enumerated. The paper calls them descriptive, which is fair. The referee's inconsistency point stands. Table 4 suppresses gaps for cells under five while Figure 2 plots block gaps from cells of three and four.

### 2.10 A search-free look at liquidation quality

I4 proposes regret against a minimum-restoration-cost plan and says a median near zero would mean the construct is saturated. A search is out of scope. A description under the same cost ordering is not.

Mortgaging costs 10% to undo and selling a building costs 100%. In 62 paid episodes cash plus listed mortgages covered the debt. In 30 of those the player held buildings. Buildings were sold in 2, both Opus, $50 each. In the 52 paid episodes that required a sale, none sold $100 or more beyond the minimum left after using every listed mortgage, and the median excess was $30, which is less than one building in most groups.

This is a crude bound and no optimum. It ignores the released-collateral trade-off and all strategy. It still says that these agents already take the cheap route when one exists. On natural states the proposed metric would probably have little variance.

## 3. Bargaining and conduct

All four contrasts reproduce from raw decisions (30.51, 16.67, 22.57 and -5.05 points). The recipient strata reproduce, including Grok at -0.25, which makes the introduction's "negative only when pooled" literally wrong. That wording came in through a final-review finding that I read and did not catch.

The largest single feature of the opening-swap comparison is an interface artifact. Grok wrote 36 of the 72 neither-completing swaps and 15 of their 17 acceptances, and 13 of those 15 came from calls whose content named a different action. With Grok's offers removed the gap is 16.7 points with a block range through zero.

I agree with I2 that an honest null does not earn three pages and a place in the abstract. What survives is descriptive. Systems differ in how they respond to disagreement, two countering and two rejecting, with similar acceptance totals. Proposer composition and call conflicts move the pooled contrast more than completion does. Refusal text often names a consequence for the rival, by a model coding with no written criterion.

The incidents are accurate as far as I have checked in earlier rounds, and I did not recheck them here. Their weakness is selection. I would keep three in the body because they tie to finance (G20's payment, G13's solvency bargain, G7's financing sale) and move five to the appendix. The owner asked for five to eight in the body, so this is the owner's call.

On conduct the comparison with Li et al. is fair. Their agents received no conduct instruction. This system prompt says "bluff, deceive" and "Deception in public chat is allowed". Nothing here is emergent and the paper does not claim it is. AgentMonopoly forbids public messages that contradict the action. This harness allows them, and does not police a call that contradicts its own content either.

## 4. Literature and novelty

Details and reading depth are in `literature_matrix.md`. The summary is that every named objection I could check holds.

- ACPBench has an action reachability task, and ACPBench Hard a generative version that is its hardest task. Both are single-turn.
- The PlanBench evaluation of o1 reports false claims of unsolvability on solvable instances, 0% and 11.5% in two domains.
- AutoPlanBench compares one-shot and interactive action choice.
- The EMNLP 2026 menu paper has a same-candidates order ablation.
- LLM-Modulo is a position paper on external verification.
- MafiaScope ships saved-state replay and repeated probes.
- The atomic-chess workshop paper names the gap between a rule check and the call that follows.
- An ACL 2026 paper studies error propagation in agent memory.

What I did not find in the two Monopoly comparators is any analysis of post-obligation liquidation. AgentMonopoly eliminates a player at negative cash. FinBoardBench has a fund-raising prompt and reports nothing about it, which R2 does not mention. Two papers do not license "to our knowledge".

The honest novelty statement for the present corpus is small. It has a complete population of naturally occurring liquidation decisions in full multi-agent games, with an exact feasibility label for each and every text channel preserved. That is a dataset property and a careful description. It is not a finding about planning.

## 5. What each proposed intervention changes and identifies

| Proposal | What it changes | What it identifies | What it does not | Status |
|---|---|---|---|---|
| Run a reactive policy on saved entry states (R1, R2, I1, I2) | Nothing an agent sees. Executes engine and policy | Payment under a fixed rule, a property of rules and states | Anything about agents. Already known analytically for 108 of 131 | Engine execution, out of scope |
| Feasibility search or verifier (R1, I1, I4) | Nothing an agent sees | Exact payability labels | Agent behavior. The corpus already has 128 payments, 3 stored witnesses, 56 bounds and 1 menu search | Search, out of scope |
| Replay the sixteen saved requests 30 times per model (I2) | Date and provider state. For other models, the player identity and the author of the notes | Today's first-action distribution at one delivered context | The historical counterfactual. Cross-model comparison at "identical states", since the request names another model and carries its notes. Opus through the same channel, since its standard prompt is refused | Provider calls, out of scope |
| Strip carried notes (I2, I4) | All memory, including the rule statements some notes carry | Effect of having any notes at those states | The effect of the reserve figure | Provider calls and prompt edit |
| Plant a reserve figure R (I4) | A forged note | Effect of a note-stated figure on declaring, if R differs from the menu total | Whether natural notes had that effect | Provider calls and prompt edit |
| State the release rule, or supply values (R1, R2, I2) | Prompt content. Stating that a sale releases specific mortgages hands over the deduction | Whether rule salience or value recall limits behavior | Much, at a base rate of 2 failures in 16 | Prompt change |
| Altered rule (I2, I4) | Engine and prompt | Recall against stated-rule following | | Engine change. The corpus already has an unstated-variant analog in section 2.7 |
| Reorganized representation, or filtered against broad catalog (I1) | Prompt structure, tool schemas. The broad catalog breaks the rule that agents choose only engine-listed actions | Effect of interface on feasibility judgment and stopping | | Prompt policy change |
| Independent assessment and execution runs (I1, R2) | A new assessment prompt | Marginal rates of correct judgment and of payment per state | Their relation within a response | Provider calls |
| Minimum-restoration-cost regret (I4) | Nothing an agent sees | Excess local liquidation cost under a stipulated objective | Value destroyed, or decision quality for winning | Search, out of scope |
| Solver plays liquidation in 20 fresh games (I4) | The agent system | Effect of replacing a sub-policy on who wins and when | A change in eliminations, which is three per game by design | New games |
| Two humans code 16 texts and 74 rejections (I2, R1) | Nothing | Agreement of model readings with human readings | | Owner decision. No assistant can supply it |
| Sixteen-case matrix, 188-episode statement and action table (R1, R2, I2) | Nothing | A fuller description of existing records | Causes or rates beyond this cohort | In scope now |
| Same-model tables, fixed opponents, personas, judge labels (I3) | New games or model judgments | Model-level contrasts, or unvalidated trade labels | Anything about the finance question | New games |

Three points deserve more than a table cell.

The replay gate has an identification problem that the referee calls a strength. "Every model then faces identical states" is true of the board and false of the prompt. A saved request says who the player is and contains that player's own notes. Sent to another model, it tests that model reading someone else's memory under someone else's name. For the note hypothesis that confound sits on the variable of interest. The two referees also disagree here. I1 treats the historical sixteen as discovery data and wants fresh states for confirmation. I2 makes the same sixteen the gate.

The regret metric assumes the player will restore the position, that rent lost while a deed is mortgaged is zero, that returning houses to the bank has no effect on rivals, and that local cost tracks winning. The records contradict each assumption somewhere. Gemini at G13 kept Boardwalk and Kentucky unmortgaged on purpose and ended with $28. Grok's notes in G17 and Gemini's in G18 reason about bank house stock as a weapon. Most deeds mortgaged in end-game debts are never lifted. PokerBench, which the referee offers as the template, reports the same gap between closeness to a solver and winning. Its best fine-tuned model lost to GPT-4 despite the higher benchmark score.

"Declared when unpayable" is not a correctness criterion. Eight of the 56 menus offer nothing else. The debtor is eliminated either way, so a win objective is indifferent. Five of the six observed departures are call conflicts. Only "paid when payable" has a right answer, and the agents meet it 128 times in 131.

## 6. Where the referees contradict each other

- I3 recommends a judge label on every trade. R2 says such labels are not economic ground truth and praises the paper's restraint. I side with R2.
- I2 makes thirty replays of the sixteen historical states the gate. I1 and R1 say those states are discovery data and confirmation needs fresh ones.
- I2 says no further work on this data moves anything and to stop rewriting. R1 says finishing the existing-record analysis would make the paper substantially more informative. On the evidence of this review R1 is right. Three of the findings above came from records already on disk.
- I3 says take rules in the prompt. I4 names the unstated house rule as one of three open questions. The second depends on not doing the first.
- I3 says take a fixed opponent pool and a human reference. R2 says neither is needed unless the claim changes.
- R2 says AgentMonopoly has 140 games. I3 says 120. The paper's table gives 140 and the repository README gives 120.
- I1 warns that telling the agent a sale releases specific mortgages is derived assistance and not a formatting change. I2 lists "rule stated" and "values supplied" as routine arms.
- I1 warns against keeping old notes when quantities are altered. I4 proposes resetting debts on existing holdings.
- R1 calls the thirteen-plus-one reading defensible. I2 calls it unvalidated. Both are true. It is defensible as a reading and no human has checked it.
- I2 says the task needs no anticipation and I4 proposes a paper whose claim is that agents fail a task fifteen lines of code solve. On the records they fail it three times in 131, once through a call conflict.

## 7. Where I disagree with the referees and with prior team work

With the referees:

- The planted-number headline (I4) is not supported by the records in the way presented. Section 2.4.
- Regret as the fallback headline (I4) would probably be a null on natural states and measures a stipulated objective. Sections 2.10 and 5.
- A reactive policy does not need to be run to settle the calibration question for most states (R1, R2, I1). Section 2.1.
- The Fisher p-value is not a point in the paper's favor. Section 2.9.
- "Unvalidated" is fair. "Twenty minutes of work" is not something this team can do, and a model reading must not be relabeled.
- Cross-model replay does not remove a confound. It adds one. Section 5.
- I do not adopt any rating, acceptance estimate or cost figure. I also do not adopt a reference quota.

With the team's earlier work, mine included:

- The headline "prospective financial assessment followed by dependent execution" overstates. Execution is not dependent on the assessment in any sense the records can show.
- The first-action paragraph treats six call conflicts as decisions.
- The selection rule for the sixteen fields was defensible and still hid a second rationale in one failure.
- "Reproducible" and "negative only when pooled" are errors that three final reviews, mine among them, let through.
- The paper lists the engine's house variants as rules without saying they depart from the rulebook it cites. That matters once the claim is that agents apply published rules.
- Appendix F named files that were not in the repository when the referee looked. A checkpoint commit made during this round, not by me, has since added the package under `docs/research_raw/paper_revision_2026-11-12/integrated/`. The appendix still gives no folder path.

## 8. What changed my assessment

Four things, in order of weight.

1. The menu makes continuation sufficient. I had blocked this statement. I now think it must be in the paper.
2. The departures at the first menu are mostly call conflicts. My own count hid that.
3. The second text channel exists for the failures and shows a further rationale in one. My selection rule was too tidy.
4. The agents' rule beliefs match the rulebook where the engine does not. I had treated the engine's variants as background. They are part of the result.

Two things did not change. I still think the sixteen full fields are the best evidence the paper has, read as text and not as a success rate. And I still think no new headline should be adopted because a referee proposes it. The v3 referee's observation that each draft's thesis tracked the last review is accurate, and the planted-number thesis would be a fourth instance.

## 9. Whole-paper judgment

**Science.** The paper asks whether agents anticipate what their actions make available and whether behavior realizes the assessment. The data can answer a smaller question. At the moment a debt arrives, does the agent's first move agree with what its assets can cover, and what does its text count? The answer is yes in 179 of 188 by action, and the texts in the sixteen dependency cases mostly count the right things. That is worth reporting. It is not a planning result.

**Reasoning.** The paper's inference from text plus payment to "anticipation followed by execution" joins two things the design does not connect. Payment follows from continuing. The text shows the model wrote the released resource down at decision one. Whether writing it down mattered is unidentified, and G9 shows reasons can follow actions.

**Finance.** The exact parts are the bounds, the routes and the remainders, and they hold. The economic content is thin by design. Agents take the cheap route when one exists. Nothing in the corpus prices a liquidation choice against a strategic alternative.

**Bargaining.** The census is complete and the main contrast does not survive composition. The section documents an instrument problem as much as a behavior.

**Conduct.** Accurate, selected, and licensed by the prompt. Illustration only.

**Novelty.** Small and specific. A complete, labeled, natural population of liquidation decisions with all channels. Every general claim nearby has precedent.

**Inference.** Twenty games, five seeds, no repeated cell, no intervention. Any rate is a description of this cohort.

**Information conditions.** No rules and no values in the prompt, a rulebook the agents know, an engine that departs from it in four ways, carried notes that sometimes hold the rule and sometimes a partial inventory, and a timeline that can show another player doing the same thing a turn earlier. The paper states most of this in pieces. It should state it once, as the conditions under which the texts were written.

**Measurement.** Three instruments are mixed. The applied call, the note written after the call's name, and provider text written before it and sometimes cut short. One system's calls contradict its own text at a measurable rate. Any statement-and-action claim has to say which statement.

## 10. Strongest dissent

Against the feedback. The most confident proposal in it, a paper claiming that agents fail a task fifteen lines of code solve and that the failure is steerable by a number in their notes, is the one the records support least. The failure occurred in two coherent cases. The number is the menu's own total. A carried partial inventory preceded twice as many successes as failures. The fallback metric would probably be flat, and the validation outcome is fixed at three eliminations per game. I would not commit the project to that thesis on this evidence, and I would not present it to the owner as the obvious next step.

Against the team. The integrated paper's central sentence, that the findings "document prospective financial assessment followed by dependent execution", should not survive. All four of us signed it. The execution depends on nothing but not stopping.

## 11. What remains scientifically unresolved

1. Whether the false infeasibility pattern recurs at a fixed state or across states. Each state was seen once.
2. Why it happens. Counting only what the menu shows, carrying forward a partial inventory, and failing to apply a known rule all fit two cases.
3. Whether a written assessment precedes and shapes the action or follows and explains it. The design cannot say, and one system shows the two coming apart.
4. Whether liquidation quality varies enough to measure, and under which objective.
5. Whether agents follow the published rules or the environment when the two differ and nothing is stated. A few episodes say the rules.
6. Whether completion affects refusal once proposer and channel conflicts are held fixed. The cells are too small.
7. Whether any semantic reading in the paper would survive a human coder.

Items 1, 2, 3 and 5 need interventions. Item 4 needs a search and an argued objective. Item 6 needs more games. Item 7 needs a person.

## 12. What should stay in the present paper

Keep:

- The complete 188-episode census, the resource partition, and the first-action counts.
- Both false infeasibility declarations, with both channels printed.
- All sixteen initial fields in full, with the second channel added.
- The G20 exact-budget sequence as an illustration of a measured category.
- The channel definitions and the disclosures about Opus refusals and Grok's tool-choice setting.
- The proposer-composition correction of the swap contrast, briefly, as a caution about pooled contrasts in interacting systems.
- The 920-response table.
- The limitations section.

Add from existing records:

- One paragraph, with code references, that continuing is sufficient for payment in hotel-free states.
- The nine named-action conflicts in liquidation and what they do to the six "financing starts".
- The episodes where agents apply rulebook rules the engine lacks, with the rulebook cited and the engine's departures named as departures.
- The carried-note table.
- The sixteen-case split of section 2.5, labeled as a model reading.

Correct:

- "reproducible" to "repeated".
- "negative only when pooled".
- The abstract sentence that implies statements were coded for both full populations.
- The Table 2 middle label, or a sentence on its witnesses.
- Appendix F's file pointers, which need the folder path and commit.

Reduce:

- "Anticipation" and "dependent execution" as claims.
- Bargaining to a short section and an appendix.
- Incidents in the body, subject to the owner's earlier request.

Whether to run any of the proposed experiments is not something this review decides. `recommendations.md` separates that from the work available now.
