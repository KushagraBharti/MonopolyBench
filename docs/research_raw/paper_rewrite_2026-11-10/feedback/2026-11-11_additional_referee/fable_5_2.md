# Fable 5.2 assessment of the additional referee review

11 November 2026. Assessment only. I changed no manuscript, canonical file, outline or code.

## Scope

I read the whole critique in `user_review.md` and all eighteen current LaTeX sources of the integrated manuscript (`manuscript.tex` and the seventeen files in `integrated/sections/`). I also read the rewrite contract, the cross-review contract, the root's integrated review and my own final review. I did not read `astra.md`, `opus.md` or `sol.md` in this folder, or the root's output file, so this position is independent.

I ran no game, engine call, replay, model call, synthetic test or baseline. I read saved decision records, saved prompt files, the retained offer ledger, the board price file and engine source, and I did arithmetic on them.

## Bottom line

The referee is right about the paper's two largest problems and wrong about several remedies and details.

The counts hold. The referee rebuilt them and so did I, twice. The problems are in what the paper says about the counts. One of four players ran under a broken response condition that the paper describes vaguely and, in two sentences, inaccurately. Two of the three numbers in the abstract are close to bookkeeping facts about Monopoly. The most behavioral results sit in hedged prose or an appendix.

Most of the referee's remedies need new games, baselines or ablations. The owner has ruled those out. What remains is a revision of description and emphasis, plus a few tabulations of logs we already hold.

## Principal issues in plain English

1. **The paper does not say what happened to Opus.** All 1,605 refusals carry one provider message, a block for "reverse engineering or duplicating model outputs". The retry prompt differs from the standard prompt only where the standard one mentions private thoughts and reasoning. It removes the private-thought field from the prompt and the tool schema, and it drops the requests to reason honestly. It keeps the permission to deceive. Opus answered that retry prompt 1,604 times with no refusal. The paper quotes none of this, so a reader can conclude that Opus refused to deceive. That reading is false on our own records.

2. **Opus played under different conditions in most of the corpus.** In games 5 to 20 it wrote no private notes and had no corrective retry. Its results describe "Opus without notes or a second try". Its 61 construction defaults follow from the lost retry. The paper says this in pieces. It should say it once, early, and label Opus's rows that way.

3. **Two of three headline numbers are close to accounting facts.** Built groups collect most rent because houses multiply rent and early builders have more turns. Winners inherit most estates because the strongest rent position is the usual creditor and the usual winner. Most bankrupt players could not pay. The body hedges each claim and the abstract leads with them anyway.

4. **Twenty games in one seating order cannot separate system, seat and luck.** Wins are 8, 7, 3 and 2 by system and 7, 7, 3 and 3 by seat. Both splits are compatible with equal chances. Every system sits directly after the same opponent in all twenty games. The paper prints no interval or test anywhere.

5. **Nothing in the paper can call a decision good or bad.** There is no baseline player, value reference or human label. The bargaining results describe what agents did and said. They cannot say whether Grok's three refusals in G15 were wise.

6. **The evidence about reasons and conduct depends on LLM readers and hand-picked transcripts.** The 61 of 74 result comes from two instances of one model, one partly unblinded, with no human check. Six of eight incidents involve Grok, whose tool calls contradict its own text in 139 decisions.

7. **The prompt shapes the conduct we report, and the paper never shows it.** The system prompt lists deceptive, manipulative and hostile play as options and says the public message can be used to "negotiate, bluff, deceive, cooperate, intimidate". It contains no rules and no house variants. Prices and rents appear only in purchase prompts. The deception we report was invited.

## Strongest new finding

The Opus refusal can be traced in our own logs, and the trace contradicts the manuscript in two places.

- `setup.tex` line 50 says the action-only prompt "omits that sentence" about deception. The saved prompt files show it omits only the private-thought half. "Deception in public chat is allowed" stays, and so does "bluff, deceive ... intimidate".
- Appendix C.1 says the jump in refusals "coincides with the source-commit boundary". Timestamps say otherwise. Games 1 to 4 started together at 15:39 UTC on 25 October. In ten-minute bins, refused first attempts were 16 of 56, 17 of 37, 23 of 37, 19 of 26, 12 of 16 and 12 of 19. From 16:39 onward all 115 were refused. Counted per game, 68 of 160 first attempts were refused up to each game's last accepted standard response, then 146 of 146. Games 5 to 20 add 1,390 of 1,390.

The logs tie the refusal to the private-thought request. Standard attempts were refused 1,605 times in 1,697. Action-only attempts were refused 0 times in 1,604. The logs do not say why the rate rose from 29% to 100% within an hour. That cause stays unknown, as the rewrite contract requires. The referee's link to a named Anthropic refusal category is an outside claim that I did not check.

## Best scientific lead

The referee's question 8 points at a real result, and half of it survives my check.

I reproduced all sixteen medians in the board-price table, then split them by seller and mortgage status. Each figure is the median asking price divided by list price, first for a buyer whose group the deed completes and second for other buyers, with counts in parentheses.

| Seller | Unmortgaged deeds | Mortgaged deeds |
|---|---|---|
| Sol | 2.81 (17) against 2.00 (27) | 1.50 (18) against 0.62 (8) |
| Opus | 2.00 (16) against 1.50 (17) | 0.67 (18) against 0.53 (18) |
| Grok | 4.14 (4) against 1.82 (15) | 1.25 (13) against 0.63 (24) |

Sellers ask more of a completing buyer in all six cells. Gemini writes too few asks to compare.

The buyer side does not hold. Sol bids more for deeds that complete its own group (2.70 against 1.60 unmortgaged). Grok bids less (1.28 against 1.67). Opus is mixed. "Buyers bid no premium" is a pooled figure that averages opposite behaviors.

Within one game, the same seller prices the same single deed for both kinds of buyer in only seven cases. The ask is higher for the completing buyer in four, lower in two and equal in one. G2 is one of the four.

These are asking prices, not settled prices. Cells are small, and offers in one thread depend on each other. This belongs in the main text beside G2 as a description of how sellers price a rival's completion. It is not an estimate of a premium.

## What my checks found

| Referee claim | Result |
|---|---|
| One refusal string, 1,605 times | Confirmed. Every refusal has finish reason `content_filter`. |
| Refusal share 76%, 67%, 57%, 73% in G1 to G4, then 100% | Confirmed. |
| The switch follows wall clock, not the commit boundary | Confirmed. The last accepted standard responses fall between 16:14 and 16:38 UTC. |
| Prompt wording on private thoughts, personalities and deception | Confirmed from the saved system prompt. The tool schema requires `private_thought`. |
| Reported reasoning tokens average 38, 254, 259 and 3,589 | Confirmed. Sol reports zero on 65.1% of responses. The largest Grok completion is 69,595 tokens. All 6,989 decisions record effort "medium". I found no token cap in the arena package. |
| 88 of 240 Opus openings repeat a deed bundle | Confirmed, with context the referee left out. Sol repeats in 27 of 132 and Grok in 26 of 136. Only 15 of the 88 repeat the cash terms too. |
| About $218 in recorded charges, $11 a game | Wrong. That figure adds two overlapping cost fields. Counting each charge once gives $141.39, about $7 a game. The 1,600 refused Opus attempts carry no usage record. I checked no invoice. |
| Wins 7, 7, 3, 3 by seat. Seat 2 wins all of block 3. | Confirmed from the paper's own table. |
| Exact test p of about 0.18 for wins by system | Confirmed (0.177). The same test for seats gives 0.36. |
| Fisher tests of 0.08 and 0.014 on Table 2 | Confirmed as arithmetic. They ignore clustering, as the referee says. |
| 25% power for a 40% win rate | Holds for a strict threshold. A one-sided 5% test has 40% power. Low either way. |
| One cyclic seating order | Confirmed in all twenty games. |
| Short Line chance is 11.7% with doubles | Confirmed. Minor. |
| `baselines.py` exists | Confirmed. |
| Two rules missing from the paper | Confirmed by reading engine source. The engine refuses to trade a deed in a developed group. A creditor inherits mortgaged deeds without paying interest. |

One fact comes from the paper's own tables and is not in its prose. The G7 hotel lock is the final elimination of a game Sol won. The lock ended that game.

## What to reject or qualify in the critique

- **"No notes, no memory."** Opus had no private notes. It still received the public timeline, the board state and trade history.
- **"The model that thinks least wins most."** Reported reasoning tokens are a billing field that providers fill differently. They do not measure thinking. The win split is also compatible with chance.
- **"A rollout oracle is sitting there unused."** Determinism gives exact replay of recorded actions. A value estimate needs someone to play out the rest of the game. That means new model calls or scripted players, and both are out of scope. Scripted play would also value positions under scripted opponents.
- **"Harness outcomes."** This is established for the 61 defaults. It is not established for the 240 proposals or the repeats. Of Opus's eight unbuilt groups, three are defaults. The other five never had a build option on that group, mostly because a deed was mortgaged.
- **"Bankrupt players were insolvent."** Not quite a tautology. This engine lets a player declare bankruptcy while able to pay. The finding is that players almost never did. Three of 56 declared bankruptcies came with a payable debt, and one of those three is a Grok call that contradicts its own text.
- **"Nothing you observed is emergent."** The paper never claims emergence. The fix is to print the prompt.
- **"The eight transcripts estimate nothing."** They are not meant to. Keep eight, as the owner asked, and attach to each a count of how common its mechanism is.
- **The "Not evaluated" row.** Keep the question map. Introduce the eight questions and A to C in the introduction so the table has a referent.
- **Statistics.** Add honest ranges. Do not add model-based p-values. Twenty games in five seed blocks, with response condition tied to system, would make such numbers look more exact than the data are.
- **"Merge into an instrument paper."** This conflicts with the rewrite contract, which rejected the audit framing. It is the owner's decision. My view is to keep the behavioral paper and name the full record as one stated contribution.
- **Scores, venue predictions, the comparison table and all claims about other papers.** These are the referee's assertions. I verified none of them.

## The ten "fatal problems"

| # | Critique | Judgment | What fits inside the rule |
|---|---|---|---|
| 1 | Opus arm misdescribed | Accept. Qualify "no memory". | Quote the string and the prompt difference, give the time course, fix two sentences. |
| 2 | "Medium" is not one condition | Accept the fact. Reject the inference about thinking. | Print the reported-token table with zero shares. Say no cap was set. |
| 3 | Grok mismatch | Accept. Already disclosed. | Add the response census without the 64 conflict-opened threads. |
| 4 | Twenty games | Accept the limit. The cost figure is wrong. | State the seat split, the exact test and the fixed seating order. |
| 5 | No statistics | Partly accept. | Game-resampled ranges for three contrasts and a seed-by-seat table. |
| 6 | No baselines or value reference | Accept as a limit. Reject the oracle claim. | Say plainly that no decision is scored. |
| 7 | Headlines restate rules | Mostly accept. | Reorder the abstract. Restate the bankruptcy result as "3 of 56 declarations were payable". |
| 8 | Semantic evidence | Accept the limits. Reject cutting transcripts. | Report agreement between the two existing codings. Lead with 27 of 38. |
| 9 | Validity holes | Accept the facts. "Fixing" needs new runs. | Print the prompt. Add one table of known defects and the results each touches. |
| 10 | Thin novelty | Not verified. The positioning advice is fair. | Add a contributions list. |

## What the paper should lead with

These results are behavioral, not bookkeeping.

- **Sellers price a rival's completion, and recipients refuse their own.** G2 shows one seller asking $450 from a buyer with no yellows and $650 from a buyer the deed completes. The seller split above gives it a population. In 27 of 38 refusals of an offer completing only the recipient's group, both readers found a stated consequence for the rival. Lead with that cell. The 34 of 36 for both-completing offers is less surprising.
- **Similar completions, unequal building.** The four systems complete 17, 18, 15 and 13 groups by trade and build on 16, 17, 7 and 3. Say for each system what stopped the unbuilt groups, and separate choices from response-handling losses.
- **Agents bargain over who will inherit.** G13, G18 and the G1 Boardwalk note show players pricing a rival's survival. The 202 of 227 figure explains why that concern is rational under this rule. It supports the finding and should not be the headline.
- **Low-cash sellers release completing deeds.** Twenty-one of 48 such sellers hold under $100. This is distress selling.

The referee says the paper is rediscovering bargaining with externalities, the holdout problem and fire sales. One paragraph using those terms would help. I checked none of the suggested citations.

For G2, add that house prices are absent from Sol's prompt at that decision. Its nine-house error is recall, not misreading.

## What changes in the prior plan

1. The integrated manuscript is not final. The Opus description must be corrected before anyone posts it.
2. The abstract and introduction should lead with behavior and treat rent, estates and debts as context.
3. The seller-side price split moves to the main text. This reverses part of an earlier decision that I supported.
4. Add a short uncertainty passage with seat results, the exact test, the fixed seating order and game-level ranges.
5. Add the verbatim system prompt, its difference from the retry prompt, a contributions list, plain definitions for private terms and the recorded cost.
6. Run five tabulations on existing logs: seed-by-seat pairs, the census without Grok conflict threads, agreement between the two codings, settled prices by completion, and cash margins at the five overcharged redemption amounts.
7. Optional for the owner: hand-label the 74 rejections. That is reading, not a model call.

Nothing changes on reruns, baselines, ablations, the eight incidents, the question map or any count.

Four decisions belong to the owner. They are the framing, the venue, the author line and the hand labels. Without new games I would not aim at a main conference track.

## Corrections to my own earlier review

- I wrote "The paper is sound." The counts are. I verified Opus's counts and never asked whether the paper says what the refusal was. I missed both inaccurate sentences and checked no timestamps.
- I ranked the debt classification and creditor concentration among the strongest findings. They are the best verified. They are not the most informative.
- I agreed to keep price ratios out of the main text. The seller split changes my view for asking prices.

## Checked and not checked

Checked directly in this pass: the refusal string, counts and timing. Both system prompts and the tool schema. Reported token and cost fields. Seating order. Repeated openings. The price table and its splits. The exact tests, power and roll arithmetic. Two engine rules, by reading source. The G7 elimination order, from the paper's tables.

Inherited or unverified: the Anthropic documentation claim. Every statement about other papers, venues and deadlines. The 61 of 74 codings and their game concentration. The 240-decision sample. Grok's 139 conflicts, which I re-derived in my earlier review and not again here. All witnesses, replays and snapshot checks. The prompt-history defect counts. Actual invoices. The other coauthors' assessments.

I kept two read-only scripts outside the repository, in the session scratchpad, because this task allowed one written file. They are `/private/tmp/claude-501/-Users-kushagra-CS-Projects-MonopolyBench/df40d677-6001-4760-bcd5-d79d2aca98c6/scratchpad/fable_census.py` and `/private/tmp/claude-501/-Users-kushagra-CS-Projects-MonopolyBench/df40d677-6001-4760-bcd5-d79d2aca98c6/scratchpad/fable_offers.py`.

## Simple synthesis

The numbers are right. The story on top of them needs work.

1. The paper hides what happened to Opus. The provider block disappears when the request for private reasoning is removed, and the permission to deceive is still in that prompt. So Opus did not refuse to deceive. It then played most games without notes or a second try. Say so plainly and fix two wrong sentences.
2. The abstract leads with results that mostly follow from Monopoly's rules. Lead with behavior. Sellers charge more when a deed completes a rival's set. Players refuse their own monopoly to deny a rival. Players bargain over who inherits.
3. Twenty games in one seating order cannot rank systems. Seat predicts winners about as well as system does. Say it with the numbers.
4. No decision in the paper is scored as good or bad, and the reasons come from LLM readers. State that once and move on.
5. Print the prompt. It invites deception and gives no rules.
6. The referee's reruns, baselines and ablations are outside the agreed scope. A handful of log tabulations and a rewrite of emphasis are inside it.
