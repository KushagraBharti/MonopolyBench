# Opus xhigh: assessment of the 11 November additional referee review

11 November 2026. I read all of `user_review.md`, every current `integrated/sections/*.tex` file and `integrated/manuscript.tex`, the integration decisions, my own 11 November final review, and the team memory on the Opus refusal condition. This is an assessment only. I did not edit the manuscript, outline, canonical files or code. I ran no games, engine calls, replays or model calls. Numbers marked "checked" come from reading saved game files or retained ledgers in this session and doing arithmetic on them.

Conflict disclosure: I am Claude Opus 5.5, the same model identifier as the evaluated Opus configuration. Several findings below cut against how the paper reads the Opus arm. I have not softened them.

Evidence labels:

- **Checked.** Recomputed here from `saved_games/railway-research-*` or `integrated/data/`.
- **Inherited.** Taken from earlier team audits and not rerun.
- **Unverified.** The referee's assertion, which I did not check.

## Short verdict

On the four points that matter most to a research reader, the referee is right:

- The paper describes the Opus arm incompletely, and in one place wrongly.
- The abstract leads with numbers that mostly restate the rules.
- The agents were never told the rules the paper analyses.
- The paper gives no uncertainty statements, even where existing data allow them.

The referee is wrong or overstated on several specifics: reasoning tokens, cost, statistical power, the "rollout oracle", and "nothing is emergent". Most of its remedies need new runs, which the project has ruled out.

This changes my 11 November position. I then called the integrated paper "a sound observational account" that needed only local fixes. The accounting is still sound, and nothing the referee found breaks a table. The interpretation does need a targeted rewrite: the abstract, the setup, the framing of the bargaining results, and the discussion. The results themselves stay.

## Principal issues

**1. The Opus arm is a different treatment, and the paper does not say why or when.** (checked)

- The provider text never appears in the paper. Every refused Opus response carries the same text: "This request was blocked as it seems to violate Anthropic's Terms of Service restrictions on reverse engineering or duplicating model outputs". Each has `finish_reason=content_filter` and `native_finish_reason=refusal`.
  - The paper calls this a "provider refusal", right beside a prompt that permits deception and asks for honest private reasoning.
  - A reader will assume Opus refused to deceive. That reading is wrong.
- The appendix says the jump "coincides with the source-commit boundary". The timestamps say otherwise. G1 to G4 ran in one campaign on one commit. Opus first attempts refused, by time of day on 25 October (UTC):

  | Time window | Refused first attempts |
  |---|---|
  | 15:30 to 16:00 | 34 of 95 |
  | 16:00 to 16:30 | 53 of 77 |
  | After 16:39 | 115 of 115 |

  - The last accepted first attempts in those games fall between 16:14 and 16:38. The games themselves ran until between 16:38 and 18:09.
  - Per-game refusal shares in G1 to G4 are 0.76, 0.67, 0.57 and 0.73. Every first attempt in G5 to G20 is refused.
  - The switch happened by clock time inside a campaign, not at the code change.
- The likely trigger is the private-note requirement, not a proven cause. The action-only request drops the `private_thought` field and was never refused in 1,604 uses (inherited).
- For 16 games and most of 4 more, Opus played with no model-authored private notes, one attempt, and no corrective retry.
  - The setup section says this.
  - The abstract still lists Opus's 15 trade completions and 7 first-window builds beside the other systems as if they were comparable.

**2. The headline numbers mostly show the rules at work.** I accept this with one qualification.

- "$53,810 of $57,378" is close to mechanical. Houses multiply rent, and groups developed early are exposed to rent for more turns.
- "202 of 227 inherited deeds to winners" follows from the paper's own count of 57 eliminations in 60. Almost every debtor goes bankrupt on the leader's developed group, so the leader is the creditor.
- "56 of 60 debts exceed the bound" says that bankrupt players were insolvent.
- These numbers describe how the game snowballs under intact inheritance. That is a property of the environment and deserves one paragraph. It is not a finding about agents and should not lead the abstract.
- The qualification: two things here are behavioral, and they should headline instead.
  - The breakdown behind the conversion gap: who failed to build, and why.
  - The four eliminations that were not insolvent.

**3. The agents were never told the rules the paper analyses.** (checked) The paper discloses that prices are missing from prompts. It does not disclose that rules are missing.

- The system prompt contains no Monopoly rules. The tool descriptions say only "Build houses or a hotel on your monopolies" and "Declare bankruptcy when you cannot pay."
- Nothing tells the agents about the house variants:
  - buildings pass intact to a player-creditor;
  - estates carry mortgages without interest;
  - assets returned to the bank are not auctioned;
  - build plans are validated entry by entry;
  - a hotel can be sold only when four bank houses exist;
  - built property cannot be traded (`engine.py:1772`).
- The paper's rules section also omits the last two.
- This changes how to read the social-science claims. Under the official rules, a bankrupt player's buildings go back to the bank. So the estate negotiations in G13 and G18 rest on the agents' prior knowledge of a rule this game changed without telling them.
- The build tool schema has a per-entry `count` field. It invites the "three houses on one deed" encoding that the validator rejects, which partly explains Opus's 61 build defaults.
- The fix needs no new runs:
  - state in §2 what the agents were and were not told;
  - list each house variant beside the official rule;
  - read the estate and construction results as play under an unannounced variant.

**4. The paper reports no uncertainty, even where the data allow it.** I accept this in part.

- Checked arithmetic:
  - Win counts of 8/7/3/2 give an exact multinomial p of 0.18 against equal chances.
  - Seat counts of 7/7/3/3 give p = 0.36.
  - The rejection gaps give naive Fisher p of 0.08 for opening offers and 0.014 for later offers, before any clustering by thread or game.
- Treating the data as "declared finite populations" defends the counts. But the abstract generalizes to "these configured systems", and the discussion compares models by win totals.
- Fixes from existing data:
  - one sentence saying the win counts cannot separate the models;
  - exact or game-clustered intervals for the two or three contrasts the paper relies on;
  - the coder-agreement statistics in issue 6.
- I do not adopt the referee's 25% power figure. An exact one-sided binomial test at α ≤ 0.05 gives about 0.40 power for a true 40% win rate. The conclusion is the same either way: twenty games cannot rank four systems.

**5. Opus's condition shapes the whole trading market, not just Opus's own rows.** (checked; new)

- Opus's condition also changed the market every other player traded in. The paper attaches the condition only to Opus's own counts.
- Opus opens 240 of the 526 threads.
  - In 88 of them (37%), it re-offers a deed bundle it had already pitched to the same player in that game.
  - The rate is 20% for Sol (27 of 132) and 19% for Grok (26 of 136).
  - That fits play without notes, but it is confounded with the model.
- Opus is the seller in 13 of the 21 low-cash sales of completing deeds (inherited, main text). It is also the low-price seller; see the strongest finding below.
- The bargaining results need an Opus split, as the paper already splits out Grok's call/text conflicts.

**6. The text-coding evidence is better than the referee says, but the coders are not independent.** Existing files answer part of this.

- Checked on the 74 rejections:
  - Each Astra reader assigned the rival-consequence code 63 times.
  - They agree on 70 of 74 rows: 61 coded yes by both, 9 coded no by both.
  - Cohen's κ is 0.79. This answers the referee's Q6, apart from the human comparison.
- The design problem remains:
  - both coders come from the same model family;
  - one coder had partial prior exposure;
  - 34 of the 61 agreed rows come from G1 and G15.
- If the author labels the 74 rows by hand, that makes no model or engine calls, so it falls outside the ban on new evaluations. Whether to do it is the owner's decision.
- The 240-decision planning sample is drawn from an "earlier pool of public-message-unflagged records" that the paper never explains. Explain it in one sentence or drop the sample's counts.

**7. The paper does not state its contribution or its authors.** I accept this.

- The title states no finding.
- The abstract uses model labels it never defines and lists numbers without making a claim.
- There is no contributions list.
- Discussion §8.3 refers to "eight motivating questions" that the paper never introduces earlier.
- The byline "MonopolyBench project" names no human. Name the human author or authors, and keep the LLM roles in the provenance appendix. The integration decisions already reject listing models as authors.

## Strongest new finding

Under the standard condition, sellers ask a large premium when a deed would complete the buyer's group. The cheap, distressed sales of completing deeds come mostly from Opus under action-only recovery.

Source and check: checked from `integrated/data/agenda_offers.json` and board list prices. My cuts reproduce Table 9's pooled counts (131/176/87/113) and medians (1.312/1.389/1.625/1.083).

| Seller asks (cash ÷ list price) | Deed completes the buyer's group | Completes neither |
|---|---|---|
| Sol | 2.32 (35 offers) | 1.80 (35) |
| Grok | 2.00 (17) | 1.05 (39) |
| Opus | 0.93 (34) | 0.88 (35) |
| All except Opus | 2.29 (53) | 1.39 (78) |

- **Seller asks.** Sol and Grok each ask much more when the deed would complete the buyer's group. This is holdout pricing: the seller charges for the value the deed creates for the buyer. Opus asks below list price either way.
- **Buyer bids.** Bids show no consistent completion premium. Grok bids 0.5 times list for completing deeds and 1.54 times otherwise. Opus and Sol bid more for completing deeds. The premium is therefore one-sided.
- **Distressed settlements.** There are 22 accepted pure cash-for-deed sales that complete the buyer's group.
  - In 14 of them the seller holds under $100, and Opus is the seller in 9 of those 14.
  - Those 14 sales settle at a median of 0.89 times list.
  - The 6 low-cash sales by other sellers settle at a median of 2.25 times list.
- **Consequence.** The paper's pattern of cash-poor sellers releasing completing deeds (21 of 48 sellers below $100) is largely the trace of Opus's condition. It is not general fire-sale behavior.
- **Caveats.** None of these comparisons are matched. Deed mix, game state and negotiation stage differ, and the low-cash non-Opus cell has only six sales. This is a descriptive regularity, not an estimate.
- **Why it matters.** Seller holdout pricing of a rival's gain is the cleanest economic result that holds across models in this corpus. It sits in an appendix table, while the abstract leads with rent totals. The referee pointed at it in Q8. With the model split, it becomes the paper's best economic result, and it connects directly to the economics of holdouts and of sales with externalities.

## Disposition of the referee's numbered points

**1. The Opus arm is a prompt artifact and is misdescribed.**

- Evidence status:
  - Checked: the message, the two regimes, the clock timing and the 88/240 repeats.
  - Unverified: the Anthropic `reasoning_extraction` documentation.
- Disposition: keep the core.
  - Quote the message and give the clock-based timing.
  - Call the private-note requirement the plausible trigger, not the proven cause, unless root confirms the documentation.
- Qualify "7 of 15 is a harness outcome". Opus's 8 unbuilt groups are 3 defaults and 5 windows with no construction option. Those 5 are financing states that the record shows without notes.
- Write "no private-note memory", not "no memory". Opus still received the game state and 20 public timeline entries.

**2. "Medium reasoning" is not one condition.**

- Evidence status: checked.
- Disposition: qualify.
- Sol's `reasoning_tokens` is null (not reported) in 1,292 of 1,991 attempts. It is not zero.
- Where tokens are reported, the means are Sol 108, Gemini 267, Opus 281 and Grok 3,589.
- Grok's largest completion is 69,595 tokens, and no `max_tokens` is set.
- The referee's "38 average, 65% zero" counts missing values as zero.
- Reject "the model that thinks least wins most". Reported tokens are provider accounting, not a measure of cognition.
- Do report the distribution and the missing values.

**3. Grok's call/text mismatches contaminate the negotiation data.**

- Evidence status: the paper already discloses the 64 threads and 17 settlements.
- Disposition: qualify.
- These were real offers that other players had to answer, so they belong in the population.
- Add one sensitivity line: re-tabulate the main offer table without the 64 conflict-initiated threads. This is arithmetic only.

**4. Twenty games cannot support claims about systems.**

- Evidence status: p = 0.18 and p = 0.36 checked; cost checked.
- Disposition: keep the conclusion.
- Reject the cost figure.
  - Recorded provider charges total $141.71 across the 20 games, about $7 a game.
  - 1,600 refused Opus attempts and 3 Grok attempts have no price.
  - I could not reproduce the referee's $218. Root is checking.
- "n = 20 was a $200 decision" does not bear on this paper, because new runs are ruled out.

**5. There are no inferential statistics.**

- Evidence status: Fisher values checked.
- Disposition: keep, limited to existing data (see issue 4).
- Qualify "duplicate-style design never analyzed".
  - Rotations share a seed, but the random draws diverge once the players act differently.
  - A comparison within seed blocks is therefore descriptive, not a paired causal test.
- The single cyclic seat order is already disclosed.

**6. There are no baselines and no value reference.**

- Disposition: out of scope.
- Reject "a rollout oracle is sitting there unused".
  - A value estimate needs new engine runs and assumed policies for every player.
  - Replaying a game deterministically does not produce a value.
- Keep the paper's refusal to grade individual decisions, and state it plainly in rows 1, 3 and 6 of the question map.

**7. The headlines restate the rules.**

- Evidence status: reasoning checked against the paper's own 57/60.
- Disposition: keep, with the qualification in issue 2.

**8. The semantic evidence is weak.**

- Evidence status: κ and marginals checked.
- Disposition: keep in part (see issue 6).
- The text already splits the 74 into 36 both-completing and 38 recipient-only rejections.

**9. The environment has validity holes.**

- Evidence status: prompt text and engine rule checked.
- Keep the rules-not-delivered point. It is new to the paper.
- Change the wording on deception. The prompt suggests deception, not just permits it:
  - it lists "deceptive", "manipulative" and "hostile" among the personalities;
  - it invites public messages that "bluff, deceive, … intimidate";
  - the paper's "explicitly permits" understates this.
- Reject "nothing you observed is emergent" as a criticism, because the paper never claims emergence.
- The paper already discloses the other items:
  - 2,054 garbled trade histories;
  - 149 undelivered messages;
  - the $1 redemption overcharge;
  - the G7 menu lock;
  - visible model names.

**10. Novelty is thin.**

- Evidence status: literature claims unverified.
- Disposition: qualify.
- The paper already credits FinBoardBench's counteroffers.
- What is distinctive here:
  - creditors inherit buildings intact;
  - debtors face a liquidation menu;
  - every counteroffer step is recorded;
  - each trade is linked to later building and estates.
- Add a few sentences on the economics of holdouts, sales with externalities and fire sales. Do not start a broad new literature review.

**Writing (title, abstract, contributions, byline, length).**

- Keep the points on the title, abstract, contributions and byline.
- Page length depends on the venue, which is the user's decision.
- Ignore repository hygiene and the em-dash count when revising the paper.

**Nits (cost wording, the Short Line probability, two "92"s).**

- Evidence status: checked.
- Fix only the nits that affect a claim:
  - Report the cost, or delete "unless identified as provider USD".
  - G13: counting doubles, the chance of landing exactly nine squares ahead next turn is about 12%, against 14.6% for eight squares. My calculation ignores cards and jail. "Overstates" still holds, but "4/36" is the first-roll probability only.
  - Rename one of the two different "92"s.

The referee's ten questions, sorted by what existing data can answer:

- **Q1 (cost and design).** Answered above.
- **Q6 (coder agreement).** Answered except for the human comparison.
- **Q7 (the overcharge and the G7 lock).**
  - Saved prompts can show, by arithmetic, whether the $1 redemption overcharge crossed an affordability line.
  - The G7 counterfactual needs a replay and is out of scope.
- **Q8 (the ask/bid asymmetry).** Answered by the strongest finding.
- **Q10 (falsifiability).** Add one sentence per main claim saying what record would contradict it.
- **Out of scope.** Q2, Q3's `tool_choice` test, Q4, the causal form of Q5, and Q9 all need new runs.

## What changes the prior plan

- **Opus moves into the main text.** The final integration moved "detailed refusal … accounting" to the appendix. Reverse that for Opus:
  - quote the message and give the timing in §2;
  - split Opus out of the market-level bargaining results.
- **The abstract and introduction lead with behavior.**
  - Headline the seller holdout pricing, the rival-sensitive refusals (61/74, κ = 0.79), counter repricing, and the breakdown of the conversion gap.
  - Report the rent shares, estate concentration and 56/60 as properties of the environment.
- **§2 gains a rule-information paragraph.** The rules section gains the two missing rules: built property cannot be traded, and estates carry mortgages without interest.
- **The paper gains minimal uncertainty statistics from existing data.** The earlier plan deliberately had none.
- **Table 9's seller-ask side, split by model, moves from the appendix into the bargaining section.**
- **The question map changes in two places.** The eight questions and A to C get introduced in the introduction, and row B's "Not evaluated" becomes a statement of what the design lacks: a measure of general capability. All eleven rows stay.
- **The eight incidents stay, but each card cites a population number.** Eight is within the requested range of five to eight.
  - If space forces cuts, G19 and G7 are the easiest to drop.
  - Six of the eight involve Grok. Say so once, not three times.
- **My earlier verdict changes.** I said the paper "does not need another full rewrite". That was right about the numbers and wrong about the framing.

## What not to adopt

- Reported reasoning tokens as a measure of thinking.
- "No memory" for Opus. Opus lacked private-note memory, not all memory.
- Deterministic replay as a value oracle.
- Three figures I could not reproduce, or that count missing values as zero:
  - the $218 cost;
  - the 25% power figure;
  - "Sol averages 38 reasoning tokens with 65% zero".
- The external claims, until someone checks them:
  - the Anthropic documentation;
  - the Li et al. methods;
  - MindGames;
  - Cattle Trade;
  - venue programs and dates.
- The proposed rerun, harness fixes, ablations, baselines, same-model tables and value oracle. All are new evaluations and out of scope for this paper.
- The venue scores and acceptance predictions. They are opinions, not evidence.

## What I checked, inherited, and left unverified

Checked in this session:

- the refusal string and finish reasons;
- per-game refusal shares;
- the clock timing in G1 to G4, by half-hour bin and against a 16:39 cutoff;
- the null reasoning-token counts and the reported means;
- Grok's 69,595-token completion;
- the $141.71 recorded cost;
- the system prompt text and the tool descriptions;
- the absence of rule text from one game's full set of prompts;
- `engine.py:1772`;
- the 88/240 repeated bundles;
- the Fisher, multinomial and power arithmetic;
- κ = 0.79, from both retained coding ledgers;
- the ask and bid ratios by model, and the settled-price split;
- the Short Line probability.

Inherited from earlier audits:

- the action-only request was never refused in 1,604 uses;
- estates carry mortgages without interest (phase 1 memo);
- Opus as seller in 13 of the 21 low-cash completing sales;
- all population tables, witnesses and replays.

Unverified: everything in the referee's list of external sources.

## For the user

The referee read the paper closely and is mostly right about what matters. Some of its numbers are wrong, and it asks for things you have ruled out. In plain terms:

1. **Opus's results are not normal play.** Anthropic's filter blocked almost every request that asked Opus to write private reasoning, so Opus played without notes or retries. The block reached 100% partway through the first batch of games, at a point in clock time. The paper never shows the block message and wrongly ties the switch to a code change. Fix the description, and do not present Opus as comparable to the other models.
2. **The abstract's three numbers mostly describe Monopoly's rules.** Built groups earn more, the leader collects the estates, and bankrupt players were broke. Lead with the agents' behavior instead.
3. **The agents were never told the house rules.** That includes the creditor-inheritance rule the paper is built around. Say so, and read the estate bargaining in that light.
4. **Twenty games cannot rank the models.** The win counts are consistent with chance. Add a few honest uncertainty numbers from data you already have.
5. **The paper's best economic result is buried in the appendix.** Sol and Grok ask roughly double for a deed that would complete the buyer's set. The cheap distressed sales come mostly from Opus, so they reflect its broken condition rather than general agent behavior.
6. **The two AI readers agree well (κ = 0.79), but they are not independent humans.** Labeling the 74 rows yourself would be the cheapest way to add credibility, and it needs no new runs.
7. **Put a human name on the paper.** State the contribution in the title and the introduction.

None of this needs new games or model calls. It needs a targeted rewrite of the framing, not of the results.
