# Whole-paper cross-review by Fable 5.2

11 November 2026. I read all four complete packages, recorded `initial_position.md`, ran the checks listed in `verification.md`, and only then read root's provisional `reviews/astra/delivered_drafts_review.md`. I read no other review. Every number below that is not attributed to a draft comes from a script under `tools/` and an output under `data/`. `findings.json` gives the exact passages. `replacement_prose.tex` gives finished text for the central argument.

## Verdict

No draft has the central claim right on its own, and that includes mine. The four papers study one object, the deed that completes a color group, and each found one true thing about it.

- Opus found the right baseline for defensive bargaining.
- I found that holder liquidity is the largest correlate of refusal, and so, with different filters, did Opus and Sol.
- Sol has the right frame, which separates attention from effectiveness.
- Astra has the right bound, which is the full liquidation census.

The checks change two headlines. Opus's opening contrast (74% against 64%) is real and is carried entirely by swaps. Recipients reject 82% of opening swaps that would complete only the proposer's group and 51% of swaps that complete nobody. They reject cash bids for a completing deed no more often than other cash bids (60% against 65%). My own liquidity headline (25% against 69%) is inflated by Opus as holder and by thread position, my title's "until" is not warranted, and my within-pair and seller-conversion results are weaker than I wrote.

The claim I now defend is this. These agents bargain over what a trade would let a rival do next. They refuse it when it comes as a swap and they price it when it comes as cash. The attention is to a category and is not a calibrated valuation. It weakens as the holder's cash runs down, clearly for one system. Where the game supplies a menu and an immediate check, all four systems execute. I propose the title "Bargaining over a rival's next move".

## The four papers

### Astra

Strengths. It is the shortest and best-proportioned draft (about 6,200 words, 17 cards). It keeps strategic attention and strategic effectiveness apart in one clean sentence. It introduced the liquidation census with closure on original payment events, which is the most useful new denominator in the revision. Its discussion is the only one that says a paid debt is directly checkable without a rollout oracle, which is right.

Objections. Its lead comparison is author-only against recipient-only offers, which compares being asked for a deed with being offered one (FBL-01). It gives the census equal billing with bargaining and calls it "executed financial reasoning" and "executed multi-step reasoning" (FBL-08). Sixty-seven of the 128 payments take one action with a median shortfall of $35, and the menu offers nothing except mortgage, building sale and bankruptcy. "Sixty-one require two to ten" is unverified, since nobody showed that a two-action payment could not have been made in one. Its sentence on G1 and G15 concentration is ambiguous and reads as wrong (FBL-10).

### Sol

Strengths. It has the best definitions. "Strategic attention" is defined as an observable property of recorded conduct, and the paper says what would contradict its claim. Its seller by mortgage by stage table is the strongest form of the asking-price result, and I reproduced it exactly (11 of 12 cells). It checks message delivery and found that the G12 bankruptcy message reached nobody. Its exposure table kills the "early builders had more exposure" objection.

Objections. The stated central finding, that consequences "enter bargaining at several distances", is a reading of four selected incidents plus the inherited 61 of 74 codes (FBL-09). The paper reports no positive behavioral contrast of its own and its abstract leads with what is not identified. A reader finishes it knowing what the agents talk about and not what they do differently. The distress sentence gives 21 of 48 against "thirty ... overall" without the denominator of 107 (FBL-12). "Thirty-four common-positive labels" should be 31 (FBL-10).

### Opus

Strengths. It asks the best economic question and chooses the best comparison. Author-completing openings against neither-completing openings holds the direction of the request closer to fixed than anything in the other drafts. The concession result (9 of 58 against 24 of 86) is new and I reproduced all 199 rows. The lifecycle figure is the best figure in the four papers. It rebuilt the offer ledger independently, and that rebuild agrees with mine on every field I compared (920 rows, no mismatch).

Objections. The headline contrast pools three kinds of proposal and disappears for cash bids (FBL-01). "Categorical, not graded" rests on one cut that sits at a ceiling for two recipients, has 11 offers in its low cell, and confounds price with the grouping (FBL-02). The same population responds in a graded way to the holder's own cash. "Asking prices rise, bids do not" and "a market that clears under distress" turn heterogeneous cells into mechanisms (FBL-12, FBL-13). The paper is 32 pages with 31 cards, seven of them for G2.

### Fable (my own)

Strengths I would keep. The prompt excerpt and five-hunk diff in the setup. The pair as a unit for following a deed. The debt scatter of all 188 episodes against the own-asset bound. The three-way evidence labels (fresh, inherited, contextual). The `\fact{}` build, in which an undefined number stops the build.

Corrections I owe.

1. The title is wrong. Of 43 one-sided completing sales, 23 came from holders with $100 or more and 17 from holders with $300 or more. Without Opus as holder, 8 of 23 came from under $100 and 10 of 23 from $300 or more. Gemini shows no cash pattern and Opus hardly refuses at all (FBL-03).
2. The abstract's 25% against 69% is a pooled number. Twenty-one of the 69 low-cash requests went to Opus, which rejected none, and 43 of the 69 were later offers. For standard-condition holders the honest contrast is 13 of 20 against 105 of 125 at the opening and 4 of 28 against 12 of 24 later. It is Sol's pattern (4 of 26 against 25 of 45), with 19 of Sol's 26 low-cash requests from three games, and Grok's on few cases (3 of 11 against 46 of 52) (FBL-04).
3. "The sharper evidence" is not sharper. In the 14 refusal-to-sale pairs the cash to the holder was also higher at the sale in 8, the deeds exchanged differed in 9, and five refused swaps later sold for cash alone. In 38 unsettled multi-turn pairs holder cash also fell in 25 (FBL-05).
4. Nine of 14 against 1 of 29 is mostly group ownership. Twenty of the 29 non-builders held no group and could not build. Inside group holders the split is 8 of 12 against 0 of 8 player-games. Sellers won 10 of the 43 sales and buyers 11 (FBL-06).
5. The Sol and Gemini against Opus and Grok building contrast reads as a ranking (FBL-07).
6. G19, the one incident of competent correction, sits in my appendix, and the draft is the longest of the four (FBL-16).
7. Two economics citations rest on abstracts (FBL-23).

One thing I got right and would defend. I reported that low cash also softens refusals of deeds that complete nothing. That sentence is what makes the liquidity result interpretable, and the integrated paper needs it.

## Headlines tested

| Headline | Draft | Reproduced | What a like-for-like cut shows | Verdict |
|---|---|---|---|---|
| Opening rejection 74% against 64% (author-only against neither) | Opus | Yes, with block gaps | Swaps 82% against 51%. Cash bids 60% against 65%. Without conflict-opened Grok threads, swaps 83% against 60% | Keep as the first sentence. Lead with the split by offer form |
| Author-only against recipient-only, about 13 points within stage | Astra, Sol, Fable | Yes, with leave-one-out ranges | Compares requests with offers | Table only |
| Concessions accepted 9 of 58 against 24 of 86 | Opus | Yes, all 199 | With no deed from the author, 3 of 34 against 13 of 43. No variation with holder cash (4 of 24, 2 of 13, 3 of 21) | Keep as support |
| Asks higher for completing buyers | All | Yes | 11 of 12 seller, mortgage and stage cells. Reverses in blocks 1 and 5 pooled. Same-deed 4, 1, 1 on six matched rows | Direction only |
| Responses flat in the rival's building cash | Opus | Yes | Ceiling for Gemini and Grok. Low cell of 11 is lower. Price confounded | Null on one cut |
| Holders under $100 reject 25%, $300 or more 69% | Fable | Yes | Standard holders 65% against 84% at the opening, 14% against 50% later. Sol clear, Grok thin, Gemini absent | Moderator, by system |
| Cash lower in 13 of 14 refusal-to-sale pairs | Fable | Yes | Price higher in 8. Bundle changed in 9. Base rate 25 of 38 | Appendix table |
| Completing sales come from cash-poor sellers | Opus 14 of 22, Sol 21 of 48, Fable 20 of 43 | All three | Against 7 of 31, 9 of 59 and 9 of 57. Without Opus 6 of 11, 8 of 27, 8 of 23 | Keep, with one primary definition |
| Sellers who built won 9 of 14, others 1 of 29 | Fable | Yes | Group holders 8 of 12 against 0 of 8 player-games. No group 1 of 18 | One paragraph, no abstract |
| 128 of 188 paid, 61 multi-action, 128 of 131 payable | Astra, Sol, Opus, Fable | Yes, from events | 67 single-action. No engine default. One Grok text and call disagreement | Keep as execution under a menu |
| First creditor already ahead in 15 of 20 | Opus, Fable (assets), Sol (rent) | Agreed across drafts | Buildings 12, cash 8, deeds 6. The two 15s name different games | Context, one case table |
| Built at once 16 of 17, 17 of 18, 7 of 15, 3 of 13 | All (inherited) | Counts agree | 9 no legal build, 4 defaults, 4 conflicting calls, 3 valid ends | Report with causes |

## Reconciliations

Same seller, game and deed. The seven rows are in FBL-11. Four, two, one uses the median of each sequence of asks. Five, one, one uses the first ask. Only G4 moves, and G4 compares a mortgaged Boardwalk at turns 152 to 164 with the same deed unmortgaged at turn 74. On the six rows where mortgage status matches, both summaries give four higher, one lower and one equal. I recommend that statement plus a separate sentence on G4. It rests on a reason and it is not the more dramatic count. Both lower cases are Opus selling Boardwalk with $210 or less.

The liquidation census. I rebuilt it from `decisions.jsonl` and `events.jsonl` without using any draft's code. It gives 338 liquidation decisions, 188 episodes, 128 paid, 60 eliminated and none unclosed. Every paid episode has a cash event for the exact amount, and all 108 paid rent episodes have a matching `RENT_PAID` event. The four drafts' episode files agree with it and with each other on every key, debt, outcome, action count and bound. Paid episodes contain 269 actions, 180 mortgages and 89 building sales, and no engine default. Success includes one incompatible channel. In G1 at turn 210 a Grok mortgage action carries text that names a different action, and the episode still pays. The 131 payable episodes are the 128 payments plus three inherited payment witnesses. The G7 menu lock is outside it. No paid episode has a bound below its debt, so the bound behaves as an upper bound on all 128. Paying is local solvency. It says nothing about the spending that led to the debt, and 102 of the 128 paid episodes belong to players later eliminated.

Distress populations. Opus counts cash-for-deed sales (22 and 31). Sol counts any net-cash settlement that completes the payer (48 of 107). I count settlements that complete exactly one party (43). All three reproduce from one ledger. The direction holds under each and without Opus as seller.

Landings. Sol and I split the 213 landings by first-management-turn class and get 150 and 63. Opus splits them by whether a building stood at the landing and also gets 150 and 63. The coincidence is real. The cross table is 133 and 17 against 17 and 46.

Other small points are in `findings.json` (FBL-10, FBL-18 to FBL-22).

## The brief's questions

1. Strongest claim. The empirical findings are the offer-form asymmetry, the ask cells, the concession gap and the holder-cash gradient for standard-condition holders. The new descriptive denominators are the 188 debt episodes, the 43 one-sided sales, the 63 groups with exposure and the 20 pre-estate positions. Familiar game mechanics are that developed groups earn most rent and that creditors who collect lethal rent are ahead. Unmeasured abilities are calibrated valuation, a decision rule, modeling of hidden beliefs, learning, persuasion and transfer.
2. Bargaining comparisons. See the table above. Mortgage status does not explain the cash gradient. Asking and bidding differ in kind, which is the main new result of this review.
3. Census. It closes. See above.
4. Exposure and pre-estate. Exposure is similar across classes and rent per landing is not, which describes rent schedules as much as choices. The pre-estate proxies can coexist in one table. Eighteen of twenty is conditioned on the winner.
5. Quotations. Every manifest entry in the four packages passes an independent check of file hash, field hash and span (106 distinct entries, including the two returned-explanation files). Channel labels are correct. Two disclosures should survive integration. Grok's opening bid in G2 was a conflicting call (Opus), and G12's bankruptcy message was delivered to nobody (Sol).
6. Conditions. All four state the essentials correctly. The recovery prompt keeps the permission to deceive. The 1,605 refusals share one message. Token zeros are not absence of reasoning. The trigger is unconfirmed. My setup and Opus's are the most compact. One trivial difference is that the last accepted first attempt is at 16:14:55, printed as 16:14 or 16:15.
7. Literature. See below.
8. Unanswered. General against multi-agent capability, causal learning, persuasion effects, transfer to unfamiliar opponents, human validation of the codes, and the value of any decision.
9. The liquidity paper. It is supporting evidence for bargaining over rivals' opportunities. It is not the central story.

## Where the checks changed my initial position

- I predicted that the defensive gap might exist only for liquid holders. It does not. Pooled, the gap is near zero under $100, and that is a composition effect. Within Sol, Gemini and Grok the gap is positive under $100 as well, and at the opening it is 17 to 21 points in every cash band. The two regularities add.
- I expected Opus's opening contrast to be the best single test. It is the best baseline, and it hides the split by offer form.
- I expected the seller-conversion split to be nothing more than group ownership. Most of it is. A split remains inside group holders, on 20 player-games.
- I did not expect prior work on trade denial in Catan agents. It bears directly on the novelty statement.

## Root's provisional review

I agree with root on the capacity analysis, the buyer generalization, the concession unit, the 31 against 34 correction, the pre-estate timing, the exposure paragraph, the G13 probability and the information table. My census check matches root's, including the single Grok disagreement.

I challenge three points.

1. Root would use the opening contrast and the debt census as the headline numbers. The opening contrast should not appear alone. A referee who splits it by offer form will find that it vanishes for cash bids, and the paper is stronger for saying so first. The split also explains why prices matter. Cash is where the agents charge and do not refuse.
2. Root asks for the census to be prominent as successful financing. I agree on the wording and would go further on the framing. Its scientific content is the contrast between a task with a menu and an immediate check and tasks without one. The G20 payment, in which two systems price the same estate at $1,414 and one executes ten actions to a $14 remainder, shows planning better than the count does.
3. Root would declare the median summary for the same-deed rows. I would state the six mortgage-matched rows, where the two summaries agree, and treat G4 separately.

Root wrote before my draft arrived. Its working title, "Bargaining over Rivals' Opportunities", is close to mine, and I would accept either. I would drop "LLM Strategy" from its subtitle, since strategy quality is what the paper cannot assess.

## Literature

I checked three sources for this review. Details are in `verification.md`.

- Guhe and Lascarides (IEEE CIG 2014) give symbolic Catan agents explicit embargo and block moves, note that the JSettlers baseline already refuses to trade with a player near victory, and measure win rates under imposed compliance. No draft cites it. Denying a rival an opportunity through trade is therefore established in game-playing agents (FBL-14). The paper's contribution is narrower than "agents refuse trades because of rivals".
- Cosentino et al. (arXiv 2605.16575v1) already separate counterparty modeling from strategic use in a controlled two-party setting. Three drafts cite it accurately. Sol's and my framing of attention against effectiveness cannot be claimed as new.
- FinBoardBench (arXiv 2605.27896v1) reports in its abstract that models favor acquisition over liquidity. My draft's liquidity story extends that claim to what holders do with a blocker. It does not introduce liquidity as a topic.

## Dissent and remaining risks

- I dissent from any abstract that carries a single pooled rejection percentage for completion, including my own.
- I dissent from dropping liquidity to a sentence. Three authors found it independently under three filters, and it is the largest association in the corpus. It belongs in its own section as a moderator with system-by-system counts.
- The offer-form split is my own post hoc cut from today. Nobody else has reviewed it. Its size depends on how conflict-opened Grok threads are treated, and in 13 of 21 game and recipient pairs with both kinds of swap the two rejection shares are equal. It should be checked by a second author before it leads the paper.
- The semantic codes remain two readings by one model family. A human pass over 74 rows needs no model call and would change their standing.
- Every contrast in the paper is exploratory and was chosen after seeing these games. The integrated limitations should say so once.
