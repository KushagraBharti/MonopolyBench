# Initial position, Fable 5.2

Written 14 November 2026, before any source checking.

## What I had read when I wrote this

- `BRIEF.md`.
- All three input files in full: `pasted-text-2.txt` (the 5.5/10 report), `pasted-text-3.txt` (the comparator discussion), and `inline_feedback.md` (the experimental program, the v3 referee report at 4/10, the comparator table, and the liquidation and oracle proposal).
- The complete 12 November manuscript: every section source, all sixteen initial fields, every generated table, the quotation cards, both prompts as printed, and the rendered PDF pages 5 to 7 for the layout claims.
- `handoff.md`, `evidence_map.md`, `FINAL_REVIEW_DECISIONS.md`, `INTEGRATION_DECISIONS.md`, `findings_and_limits.md`, `literature_notes.md` and `README.md` in the integrated folder.
- The 84-file pin, which matched (84 of 84, zero mismatches) before I started.

I had not yet opened any raw game record, engine source, prompt file or outside paper for this round. I had not opened the `astra` or `sol` folders that already exist under `reviews/`, and I will not open them before handoff. Everything below is what I believe before checking. Where I name a number from the feedback, I am repeating the referee's claim and have not verified it.

## My prior position, stated so it can be tested

In the 12 November round I wrote a full draft titled "What a Move Unlocks" and then reviewed the integrated paper. I held four positions that this feedback puts under pressure.

1. I treated the sixteen necessary-collateral episodes as the paper's best evidence, and the "thirteen plus one plus two" reading as its central result.
2. I argued that the paper must never print a sentence such as "a loop pays 131 of 131", because no such policy had been run.
3. I supported the fixed selection rule that prints the applied private note when one exists and the provider text otherwise.
4. I accepted keeping finance and bargaining together under one statement-and-action title, with eight incidents in the body.

I also contributed the first-action count (declarations at the first menu in 50 of 56 above-bound debts and 3 of 131 payable ones), which I still think is the most useful thing I added.

## Where I expect the referees to be right

**The payment count carries little information about planning.** The v3 referee says the engine's own fallback would pay all sixteen because any order of sales and mortgages reaches the upper bound. I blocked that kind of sentence before because nobody had run it. That was the right rule for a measured baseline and the wrong reason to stay silent about a structural property. If the menu semantics make cash-raising monotone, then "fourteen of sixteen paid" is close to "fourteen of sixteen did not stop", and the paper should say so. I expect the claim to hold for most of the sixteen and to need a caveat where hotels and bank stock are involved, because the manuscript's own G7 case shows a state where no building sale is offered. I will check the fallback code and the menu generator and I will not execute either.

**The note and the first action are one response.** The private note is an argument of the same tool call that carries the first action. The paper's phrase "prospective" is accurate about later actions and later menus. It is not accurate about the first action. For the two failures this matters most, because the note and the declaration arrive together and the note may justify the choice as easily as cause it. The five Opus texts are a different object again, a provider reasoning field written before the call.

**"Reproducible" is the wrong word in section 3.2.** Each state was observed once. I let that word through in two rounds.

**The statement-and-action analysis covers too little of what the title promises.** A paper with this title should analyze the cases where statement and action diverge. The six above-bound financing attempts and the G12 d249 conflict get a clause and a paragraph. I expect the referee's two examples (G9 d194 and G20 d273) to be real and I will read both channels and the applied action for all six.

**Both channels should be printed for the two failures.** My selection rule was defensible as a rule and still hid text where it mattered most. If the provider text for G12 d190 and G17 d234 adds a second rationale or a statement of intent, the paper's description of the failures as "omit that collateral and declare" is incomplete.

**The bargaining half has no finding of its own.** The swap contrast is correctly deflated to 16.7 points with a range that includes zero, and it still sits in the abstract. I agreed to that. I now think the referees are right that an honest null does not earn three pages.

**The literature section is thin for a planning claim.** Twelve cited works, one on planning.

## Where I expect to disagree

**"0.2% of the corpus."** Sixteen over 6,989 divides episodes by decisions. The sixteen are 16 of 188 financing episodes and 16 of 131 payable debts. The denominator the referee chose is rhetorical. The underlying point, that the headline rests on a small retrospective subset, stands without it.

**The carried-note mechanism.** The referee says both failed sums reuse a reserve figure from the agent's own earlier notes "to the dollar" ($130 for Sol, $30 for Gemini). Before checking, I suspect a common cause. $130 is what Baltic and two light blues mortgage for, and $30 is Baltic alone. Those are the mortgages the first menu lists. An earlier note and the failed sum would agree to the dollar if both simply added the currently mortgageable deeds. If so, the figure is not a planted anchor. It is the same incomplete inventory computed twice. I will read the carried notes and the menus to see which reading the records support, and I will look at the counterexamples the referee names.

**"The task needs no anticipation, therefore the statements show nothing."** The first half may be right. The second does not follow. Whether a loop can finish the task and whether the agent stated the released resource before the menu showed it are separate questions. The paper already says continuing "need not imply that a player has worked out a complete route". What the referee's point changes is which observation is informative. It moves the weight from the fourteen payments to the stop decision and to the text.

**The Fisher test offered "in your favor".** Two of sixteen against one of 115 was chosen after looking, the episodes cluster within games and agents, and the single failure in the comparison group is a channel conflict of a different kind. I will reproduce the arithmetic and I do not expect to recommend printing a p-value.

**Minimum-restoration-cost regret.** The proposal scores a liquidation against the cheapest plan, where cost is building value lost plus ten percent to lift each mortgage. That assumes the agent intends to restore the position, that every deed is worth restoring, that rent forgone while mortgaged is zero, and that the local objective lines up with winning. It also needs a search, which is outside present scope. I expect to classify it as a proposal that identifies excess local liquidation cost under a stipulated objective, and not "value destroyed".

**Replay probes as the gate.** Sending the sixteen saved requests thirty times each identifies today's response distribution at a fixed prompt. It does not replay the historical game. Sending one agent's saved request to another model hands that model someone else's private notes as its own memory, which is a new confound and not the removal of one. The two referees also disagree with each other here. The experimental program says the historical sixteen are discovery data and confirmation needs fresh states. The v3 referee makes the same sixteen the gate.

**Validation by handing liquidation to a solver.** The corpus already limits what that could show. Agents paid 128 of 131 payable debts, so a solver could change at most three eliminations in twenty games through the pay-or-declare decision. I doubt this resembles what PokerBench did and I will read that paper.

**Judge labels on every trade.** The v3 referee recommends borrowing them from FinBoardBench. The comparator report says they are not economic ground truth and praises the paper's restraint. These two pieces contradict each other and I side with the second.

**Ratings, costs and acceptance odds.** I will not adopt 4/10, 5.5/10, "a plausible 6", or any dollar estimate. None of them is a finding.

## What I think the paper is, before checking

The financing section is the only part with a locally checkable answer, and both referees are right about that. The honest version of its result is narrower than the manuscript's and in one respect sharper than the referees allow.

The task of paying a payable debt appears to be solvable by not stopping. If that survives the code check, the scientifically interesting decision is the one at the first menu, where an agent chooses between continuing and declaring. The paper has that decision for all 188 episodes. Three payable debts ended in declaration. Two of them wrote a sum that left out the one resource the menu did not yet show, and the third is a call that contradicts its own note. Six agents went the other way and started financing a debt they could not pay. That is a complete, small population about stopping, with text attached to each case. It is observational and it cannot say why.

I do not think the present data can support any of the three theses the feedback proposes (interface causes false infeasibility, a planted note figure steers the decision, or regret against an optimum). Each needs an intervention or a search that the standing scope forbids. I expect to recommend that the present paper stay observational, shrink its claim about anticipation, promote the stop decision, print both channels, and give the divergences the space the title implies. Whether to run any of the proposed experiments is a human decision that changes authorization. It is not something this review can grant.

## What would change my mind during checking

- If the fallback or a simple loop can reach a dead end in any of the sixteen states, the "no anticipation needed" claim weakens and the payment count regains some meaning.
- If the carried notes contain a figure that is not derivable from the first menu and still matches the failed sum, the anchoring hypothesis deserves more than an appendix sentence.
- If the provider text in either failure shows the agent considering the released collateral and then declaring anyway, "omitted the resource" is the wrong description and the failures become stop decisions made with the resource in view.
- If the six above-bound attempts are mostly cases where note and action agree on a hopeless but harmless try, the divergence story is thinner than the referee says.
- If ACPBench, the PlanBench o1 evaluation or AutoPlanBench do not actually contain what the feedback attributes to them, the novelty objections lose force.

## Risks in my own review

I wrote one of the four drafts and reviewed the integration twice. I have a stake in the necessary-collateral result and in the first-action count. I will try to treat both as claims to test. I will also try not to swing the other way and adopt whichever thesis the most recent referee prefers, which is the pattern the v3 referee identifies in the last three drafts and is a fair criticism of the team, me included.
