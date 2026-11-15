# Fable 5.2: initial position for the whole-paper cross-review

11 November 2026. I wrote this after reading all four complete packages and before opening any file under `reviews/astra/` or any other review. It records what I believe going into verification. Where the checks change it, `review.md` says so.

## What I read

For each of Astra, Sol, Opus and my own draft I read the manuscript source, every section, the appendices, the generated tables, the figures as rendered images, `evidence_map.md`, `findings_and_limits.md`, `handoff.md`, `initial_position.md` and `literature_inspiration.md`. I read `revision_contract.md` and `cross_review_brief.md` first. I verified all 235 entries of `four_draft_hashes.json` before reading (235 match, none missing). I have run no new arithmetic yet. The positions below rest on reading alone.

## The four theses in one line each

- Astra: agents attend to rivals when they bargain, and they execute checkable finance (128 of 188 liquidation episodes paid, 61 in several actions).
- Sol: agents bargain over competitors' future options (construction funds, resale, estates), and that attention is not the same as effective valuation.
- Opus: agents bargain defensively over the deed that completes a rival's group. The rule is categorical and not graded, and completing deeds sell mainly under distress.
- Fable: rival-aware bargaining is shared by all four systems. Holder liquidity decides when blockers move, and what the cash becomes separates trajectories.

All four papers study the same object, which is the deed that completes somebody's color group. They agree on most numbers. They differ on which comparison leads and on how much weight the financial records carry.

## What I think the strongest supported claim is

No single draft has it. I expect the integrated claim to join two results that two authors found independently.

1. Opus's opening contrast is the best test of defensive bargaining in the four papers. It compares requests that would complete only the proposer's group with requests that complete nobody. Both are requests written by the other side, so the baseline is right. My own draft and Astra's compared author-only offers with recipient-only offers, which mixes giving with getting. The gap is 74% against 64%, positive in all five seed blocks and for each standard-condition recipient. It is modest in size.
2. My holder-cash result is the largest association in any draft (25% against 69% rejection of completion requests), and three authors found the same thing with three different filters. Opus reports 14 of 22 completing cash sales from sellers under $100. Sol reports 21 of 48. I report 20 of 43. Independent agreement under different definitions is worth more than any one of the cuts.

Put together, the claim I expect to defend is this. These agents treat a trade as a change in what a rival can do next, they guard the completing deed while they are liquid, and the guard weakens as the holder's cash runs down. Sol's distinction between attention and effectiveness is the right interpretive frame for it, and Sol's title register is the most defensible. Astra's liquidation census is the bound on the other side. It shows what the agents do when the task has a menu and an immediate check.

A specific prediction I will test before I commit. My draft reports that low cash also softens refusals of deeds that complete nothing (23% against 49%). If rejection under $100 is the same for completing and non-completing requests while it differs by twenty points at $300 or more, then the defensive gap exists only for liquid holders. That would turn two headline results into one. It could also be a composition effect of Opus as the poor holder, so I will cut it by recipient and by thread position.

## Where I expect to concede on my own draft

- The title's "until" is not warranted. By my own count 23 of the 43 one-sided completing sales came from holders with $100 or more. Gemini does not show the cash pattern as a holder, and Opus hardly refuses at any cash level. "Until they need the cash" describes Sol and Grok.
- The within-pair result (cash lower at the sale in 13 of 14) is the same cross-sectional association seen inside a pair. Refusals are selected on high cash and sales on low cash, so some fall is built in. I also did not check whether the price rose between the refusal and the sale. In G7 the holder refused $350 and later sold at $700. If most of the 14 sold at a higher price, "released for want of cash" and "sold when the price was met" are not separated.
- The seller-conversion contrast (9 of 14 against 1 of 29) is the most exposed number in my abstract. A seller can build only on a complete group of its own, so the split is close to "held a monopoly at the time of the sale". Thirteen and 21 player-games are the honest units. It should leave the abstract unless a split by group-holding survives.
- The buyer-side contrast (Sol and Gemini 33 of 35, Opus and Grok 10 of 28) reads as a model ranking under conditions that forbid one. Seven of the eighteen unbuilt windows on the low side are engine defaults or conflicting calls.
- My draft is the longest and puts G19, the one incident of competent correction, in an appendix. The brief asks for competence and execution in the main set.

## Where I expect to object to the others

- Opus's "categorical, not graded" rests on one cut by the proposer's post-trade cash. Gemini and Grok reject about nine in ten opening requests, so those cells sit at a ceiling. The low-cash cell has 11 offers and is lower (55%). Post-trade cash also falls when the proposer offers more money, so price is confounded with the grouping. The same population shows a graded response to the holder's own cash. I read the flat cut as a null on one variable, not as evidence of a rule.
- Opus's and Sol's distress shares condition on settlement and use different populations. The integrated paper needs one definition with the others as sensitivity.
- Astra's finance framing gives the liquidation census equal billing with bargaining. Of the 128 payments, 67 take one action. The menu offers mortgages, building sales and bankruptcy and nothing else, so paying mostly means not declaring bankruptcy early. I think 128 of 131 is a floor on execution and a good correction to a failure-only denominator. It is not evidence about strategy.
- Sol's "several distances" (construction funds, resale, inheritance) is the most interesting idea about reasoning in the four papers. Its population support is the inherited 61 of 74 codes. The rest is four incidents. It should organize the incidents and the discussion without being presented as a measured structure.
- Astra and Sol both say 34 of the agreed 61 rival codes come from G1 and G15. Opus and I count 31 of the 61 and 34 of the 74 rows. One of these is wrong and I will recount.
- Same seller, game and deed comparisons appear as 4 higher, 2 lower, 1 equal in three drafts and as 5, 1, 1 in Opus's. I expect the difference to be median against first ask, with G4 as the case that moves. The paper should print the seven rows.

## Checks I will run before writing the review

1. Offer-level rejection by holder cash and completion category, cut by recipient, thread position and seed block.
2. The 14 refusal-to-sale pairs with the refused and accepted terms side by side.
3. Seller conversion split by whether the seller held a complete group at the sale.
4. The seven same-deed rows under both summaries, with mortgage status and turn.
5. The debt census in all four packages, row by row, with closure on payment or bankruptcy events, engine defaults and Grok channel conflicts inside paid episodes.
6. The three populations behind 14 of 22, 20 of 43 and 21 of 48.
7. The split of the 213 landings, which Sol and Opus both report as 150 and 63 under two different partitions.
8. The G1 and G15 concentration count.

## Scope

I will read saved records and the four frozen packages only. I will run no game, engine, replay, model call, synthetic test or baseline. I will write only under `reviews/fable_5_2/`.
