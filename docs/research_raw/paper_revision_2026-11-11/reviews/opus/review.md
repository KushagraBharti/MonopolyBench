# Opus whole-paper cross-review of the four frozen drafts

11 November 2026. Reviewer: Opus research assistant (Claude Opus 5.5). This model shares an identifier with one evaluated configuration and wrote one of the four drafts. I read all four complete packages: Astra, Sol, Opus and Fable 5.2. That covered main text, appendices, generated tables, the resolved `\fact{}` values, main figures, handoffs, positions, findings and evidence notes. I wrote `initial_position.md` before opening root's provisional review in `reviews/astra/`. I did not open `reviews/fable_5_2/`. Every new number below comes from existing-record arithmetic by the scripts in `tools/`, with outputs in `data/` (see `verification.md`). No game, engine run, replay, synthetic test, model call or prompt edit was made.

## 1. Verdict

**The four papers agree on most facts and differ on the claim. The strongest supported claim combines my draft's defensive-refusal pattern with Fable's liquidity evidence and keeps Sol's attention-versus-effectiveness discipline.** In one sentence:

> LLM agents in these games guard the deed that would complete a rival's colour group, and the guard is negotiable in cash. Completion requests are refused more often than comparable deed requests at every level of the holder's cash. Cash-poor holders engage more with every request. Completing deeds change hands disproportionately when holders are short of cash or can turn the proceeds into their own houses, and both sides of the table reason explicitly about that liquidity.

This claim is better supported than any single draft's headline, and in several places it corrects all four.

- It rests on observed choices with a composition-matched comparator, not only on recorded explanations (Section 3.2).
- It turns Fable's liquidity evidence into a statement the data actually support. "Withhold *until* they need the cash" fails at the offer level once stage and the Opus responder are separated. "The guard persists and cash need makes it negotiable" holds (Section 3.9).
- It joins bargaining and finance through one economic variable, holder cash. The successful-debt census then sits naturally in the argument instead of standing beside it as a separate execution leg (Section 3.3).
- It keeps the boundaries all four drafts share. It identifies no seller premium, no causal liquidity effect, no effectiveness score and no model ranking.

Root's provisional integrated claim, "bargaining over rivals' opportunities plus successful economic execution", was written before Fable was delivered. It is defensible but weaker on three counts. It leads with a comparator that understates the defensive contrast. It leaves liquidity, the variable the agents themselves discuss most when they release a blocker, out of the central argument. Its execution leg rests on a scaffolded success count instead of the more informative static-menu planning error (Section 5).

## 2. The four papers as complete arguments

**Astra: *Strategic Attention and Economic Execution in LLM Monopoly Agents*.** Its strength is balance: bargaining, financing and conduct in about 6,200 words, with a clear liquidation census (188/128/60, 61 multi-action payments, figure of action counts) and well-scoped incident cards. Its weakness is that the scientific centre is split. "Attention" rests mainly on the inherited semantic codes and the author-only versus recipient-only contrast, which changes two things at once (who completes and who gives a deed). "Execution" rests on payment success, which the liquidation menu heavily scaffolds: it states the amount owed, the shortfall and the legal options. Calling this "executed multi-step reasoning" (`astra/sections/discussion.tex:8`) claims more than a sequence of valid actions shows. The prose is clean and the incidents are the most compact of the four.

**Sol: *LLM bargaining over competitors' future options*.** Its strength is conceptual precision. It defines strategic attention as an observable property and separates effectiveness explicitly. Its G2 reading of a resale network (Sol considers Grok reselling Marvin Gardens to Opus) is the best single example of third-party option reasoning. Its price strata (11 of 12 seller × mortgage × stage cells) and its prior-rent account of first creditors (15/20) are careful. Its weakness is that the paper's centre is defined largely by what does not hold, "the most useful negative result" (`sol/sections/discussion.tex:9`), with no sharp positive behavioural regularity in observed choices. It also keeps a small count error: "thirty-four common-positive labels come from G1 and G15" (`sol/sections/bargaining.tex:24`) should be 31 of 61 agreed labels, or 34 of 74 coded rows.

**Opus (mine): *Guarding the Last Deed*.** Its strength is the population analysis: a new opening comparator (author-only versus neither), a cash-concession unit, block, recipient and condition sensitivity tables, and the rebuilt 920-offer ledger. Its weaknesses are material, and Section 4 corrects them. The comparator mixes offers that request a deed with offers that do not. The "categorical, not graded" mechanism rests on one capacity cut that does not survive stratification. "Opus is not defensive" judges a counter-heavy responder by its rejection rate. The paper is also too long (32 pages, 31 cards).

**Fable 5.2: *LLM Agents Withhold a Rival's Monopoly Until They Need the Cash*.** Its strength is that it adds the variable the others underused. It contributes the holder-cash split, a pair-level unit (148 holder × buyer × group pairs), the 14 refusal-then-sale sequences, a seller conversion table, the 131-payable denominator, the observation that only 2 of 68 building-sale payments sold buildings when first-menu mortgages sufficed, G17 as the informative estate case, and excellent new transcripts. G2 d128: "I have no monopoly to develop with the proceeds". G18 d420: "Only sell the green monopoly blocker for a major liquidity swing". G7 d141 is a bid timed to the holder's $84. G15 d176: "reassess monopoly trades when opponents need cash". G1 d309 shows a buyer pricing the alternative estate. Its `\fact{}` build discipline and quote generator are the best engineering of the four. Its weaknesses are in the headline. The title's "until", the abstract's 25% versus 69% split, and the seller build/win contrast (9/14 versus 1/29) all overstate what the units support (Section 3.9). The main text runs about 8,200 words in 39 pages.

## 3. The brief's questions

### 3.1 What is the strongest supported claim?

I separate four kinds of statement.

- **Empirical regularity in choices.** Completion requests are refused more often than comparable deed requests at openings (3.2). Cash-poor holders reject fewer deed requests of every kind and counter more (3.9). Completing sales come disproportionately from cash-poor holders (3.9). Payable debts are almost always paid (3.3).
- **New descriptive denominators.** All 188 debt episodes; 148 pairs; 63 trade-group exposure histories; pre-estate ranks.
- **Familiar game mechanics.** Developed groups collect most rent; creditors inherit; first creditors usually win. These are context, not findings about LLMs.
- **Unmeasured latent abilities.** Calibrated opponent beliefs, effectiveness, learning, persuasion, transfer, and the general versus multi-agent relationship.

The proposed central claim uses only the first two kinds.

### 3.2 Which bargaining comparisons survive alternatives?

**Composition-matched opening contrast (fresh).** An author-only offer always asks the recipient for a deed. The "neither" cell mixes 176 openings that request a deed with 62 that do not, and the latter are mostly sell offers rejected at 75.8% (47/62). Matching on "requests at least one deed from the recipient" gives:

| Openings | Completion requests | Other deed requests | Difference |
|---|---|---|---|
| All | 138/187 (73.8%) | 105/176 (59.7%) | +14.1 |
| Block 1 / 2 / 3 / 4 / 5 | 30/43, 20/24, 23/31, 31/41, 34/48 | 13/31, 38/58, 25/39, 16/25, 13/23 | +27.9, +17.8, +10.1, +11.6, +14.3 |
| Recipient Sol / Gemini / Opus / Grok | 19/41, 62/67, 3/18, 54/61 | 7/42, 60/72, 2/16, 36/46 | +29.7, +9.2, +4.2, +10.2 |
| Later offers, all | 21/102 (20.6%) | 20/108 (18.5%) | +2.1 |

The matched contrast is larger than my draft's +9.9 (author-only versus all neither). It is positive in every block and for every recipient, including Opus, so "Opus reverses" no longer holds. It is essentially absent in later offers, which are selected continuations. Recipient-only openings are rejected at 31/51 (60.8%), the same as other deed requests. Being offered one's own completion barely lowers opening rejection. Being asked for a rival's completion raises it.

**Concessions (reproduced and matched).** I reproduce exactly the 199 cash concessions on an unchanged bundle, 9/58 versus 24/86 accepted, from 38 and 43 threads. Against concessions that request a deed, the contrast is 9/58 (15.5%) versus 17/56 (30.4%). Without Opus recipients it is 4/42 versus 11/45. Repeated concessions in one thread are dependent. This is supporting evidence, not a second independent test.

**Counters are generic.** Of the counters to author-only offers, 79 of 111 keep the bundle and ask for more cash, against 81 of 110 for non-completing deed requests (all drafts). Repricing is how these agents bargain. What differs for completing deeds is whether they refuse at the threshold.

**Asks versus bids.** Asks to completing buyers are higher in all six seller × mortgage cells with at least three asks per side (Fable; Astra's single-deed figure agrees). Unmortgaged single-deed asks rise with the buyer's proximity to a complete group: 1.61 (n = 3), 1.80 (45), 2.32 (37). Bids barely move (1.45, 1.41, 1.59) and change sign across systems. Sol bids more for its own completion, Grok less. My heading "Asking prices rise, bids do not" and "holders price a rival's completion more consistently than buyers price their own" flatten this heterogeneity. Sol's formulation, that buyer ordering changes across configurations and cuts, is correct.

**Same seller, game and deed: 4/2/1 versus 5/1/1 reconciled (fresh).** The seven rows are below.

| Row | Completing-buyer asks (turn, $, seller cash) | Other-buyer ask | Median | First ask |
|---|---|---|---|---|
| G1 Opus Boardwalk | t122: 100, 150 (cash 18) | t103: 350 (cash 48) | lower | lower |
| G2 Sol Marvin Gardens | t45: 600, 650 (161) | t44: 450 (137) | higher | higher |
| G4 Opus Boardwalk | t152: 450 (110); t155: 100, 175, 250 (60); t164: 150 (210) | t74: 280 (95) | lower | higher |
| G15 Opus Baltic | t49: 120, 150, 180; t52: 100 (8) | t49: 100 (8) | higher | higher |
| G16 Grok Marvin Gardens | t250: 1,200 (93) | t144: 400 (251) | higher | higher |
| G17 Grok Mediterranean | t81: 35 (324) | t81: 35 (324) | equal | equal |
| G20 Grok New York | t68: 400, 400 (16) | t65: 120 (41) | higher | higher |

Only G4 changes direction between estimands. Opus's first completing ask exceeds the other ask, then falls as its cash falls. The four comparisons made within three turns of each other (G2, G15, G17, G20) give three higher and one equal. Both lower rows are 19 or more turns apart, with the seller's cash lower at the completing asks. I recommend printing all seven rows with both estimands and the turn gap. Using no single summary, the paper should say the deed-level evidence is mixed and that its reversals coincide with distant timing and seller distress. No premium is identified, and choosing the contemporaneous subset because it looks cleaner would be the selection the brief warns against.

**Rival-capacity gradient (fresh; corrects my draft).** My draft pooled completion openings across holder cash and reported a flat 75%, 76%, 55% profile. Stratified by holder cash, among liquid (≥$300) non-Opus holders, rejection rises with the rival's post-trade building cash: 7/10 (no house), 21/29 (one house), 89/110 (a full layer). The pattern is weak and confounded with deed and price, but it is not flat. "Responses do not change with the proposer's post-trade building cash" and the categorical-rule mechanism should be withdrawn.

### 3.3 Does the liquidation census close?

Yes. The Astra, Sol/Fable and Opus ledgers have identical episode keys and identical paid/eliminated partitions for all 188 episodes. The only label difference is "bankrupt" versus "eliminated". Paid episodes contain 269 actions (180 mortgages, 89 building-sale actions), 61 multi-decision episodes, and zero engine fallbacks. One paying decision is a Grok content/call disagreement: G1 d471 applies a mortgage while its content names a house sale. All 41 Opus payments run under action-only recovery (82 decisions with `retry_used`). "Payable" is 131 = 128 observed payments + 3 inherited payment witnesses. It excludes the G7 menu lock and the 56 debts above the own-asset bound. It is an ex post feasibility denominator, not a difficulty measure.

The census matters less as a success rate than for what it shows about execution quality and the shape of the failures:

- **Execution quality (Fable fresh; not recomputed by me).** Only 2 of 68 payments that sold buildings did so when first-menu mortgages would have covered the shortfall. My draft found that debtors who could do either mortgaged first in 40 of 51 episodes.
- **Unlocked collateral used (fresh).** In 19 paid episodes from all four systems (Gemini 9, Opus 5, Sol 3, Grok 2), the debtor later mortgaged a deed that became mortgageable only after a building sale: 33 actions, all after sales. Mortgage arguments were checked against the canonical `space_key` field, and the total of 180 paid mortgages reproduces.
- **The failures share one error (fresh from canonical prompts).** G12 Sol d190 sums $53 cash, $225 house salvage and $130 of listed mortgages into $408 against $500. G17 Gemini d234 sums $500 salvage and $30 into $530 against $550. Both omit the mortgages that selling the buildings would unlock: $340 and $375. Both agents treated the first menu's list of mortgageable deeds as fixed. Agents moving step by step through the re-presented menu used exactly that collateral.

This is precise multi-step planning evidence, a static first-menu lookahead failure, and it is more informative than either the 128 successes or the three failures alone. G17 also matters downstream. The payable bankruptcy handed Park Place and Boardwalk with five houses to Sol, the poorest player at the table, and Sol won.

### 3.4 Development exposure and pre-inheritance positions

The exposure results are consistent across drafts and belong in context, not in the headline. First-window-built and other trade groups have median durations of 62 and 63.5 turns, landing rates of 4.0 and 4.3 per 100 turns, and rent of $359 versus $57 per landing. Opus's $374/$20 conditions on development at the landing, a different estimand. Rent per landing mostly reflects the rent schedule.

The behavioural content is the system-level conversion gap: first-window construction on 33 of 35 Sol and Gemini groups versus 10 of 28 Opus and Grok groups. That gap is tied to acquisition terms (mortgaged deeds at completion 2, 4, 7, 5; median post-trade cash $684, $610, $268, $448) and to response conditions (Opus defaults, Grok conflicts).

Pre-estate proxies coexist without contradiction. The first creditor leads or ties in prior paid rent in 15 of 20 games, in buildings in 12 (Sol), and in the asset index in 15 (Opus and Fable), but in cash in only 8. The measurement times differ slightly: before the eliminating action, before the first bankruptcy action, or at the first menu. Root documents $80 and $120 differences in G18 and G19. The informative content is the five discordant games, G17 above all. No draft should infer that an estate did not matter because the creditor already led.

### 3.5 Quotations, channels and delivered context

I independently re-verified 44 argument-bearing quotations from Fable's manifest against the canonical `decisions.jsonl`: file hash, line, JSON pointer, field hash and exact span offsets. All 44 match (`data/quote_spotcheck.json`). They include every quotation I propose for the integrated incidents. I also checked the two payable-bankruptcy notes directly from the canonical prompts and responses.

Channel issues that must stay attached to interpretations:

- G1's Opus side has no private note (recovery). Grok's note supplies the buyer's reasoning.
- G13's "omission" quote is a returned provider explanation, not the applied note. The applied note sets a $165 floor and names the Ventnor route.
- G12's public bankruptcy message has no later recipient exposure (Sol's check), so it makes no reception claim.
- G19's proposal is a Grok conflict call. The proposer's note says to abort, so the false public claim is not a coherent plan.

None of the drafts counts authorised bluffing as misalignment. Keep that.

### 3.6 Prompt and provider condition

All four drafts now state the condition correctly, with small wording differences I verified.

- **System prompt.** The recovery system prompt drops the private-thought field, "reason honestly", "private thoughts should reflect true reasoning", "both messages" and "concise reasoning". It adds "Return only a legal tool call and its public_message. Do not include private_thought or a reasoning transcript."
- **User payload.** The payload separately adds `response_instruction`: "Return a legal tool call with public_message. Do not return private_thought or a reasoning transcript."
- **What is kept.** Both the deception sentence and the bluff/deceive list survive.
- **Timing.** The last non-refused first attempts are 16:14:55–16:38:11 UTC. Astra and Sol's "16:15" and Opus and Fable's "16:14" are roundings of the same record.
- **Interpretation.** The documented `reasoning_extraction` category is consistent with the record but unconfirmed.

The integrated paper should state the condition once in the setup with exact counts. It should reappear only where it changes a result: Opus's counter-heavy responses, distress sale prices, construction defaults and absent notes. The full diff goes in an appendix. Usage tokens and cost belong in an appendix table (BYOK-aware $141.39; never add the two overlapping fields).

### 3.7 Literature

I read three things for this review.

- **FinBoardBench v1.** The archived text of arXiv:2605.27896v1, abstract and §3.1–3.2, local copy from 29 October. In its Monopoly games, "among 86 completed deals initiated by advanced LLMs, 82 finish within one round", and only 33.3% of negotiation decisions are counters. Its models keep buying with cash below $500, which it describes as "overvaluing asset accumulation while underestimating liquidity preservation". Those models ran in non-thinking mode against fixed opponents. This is the closest prior liquidity claim in the same game, and it should be cited for what it is: a purchase-side liquidity failure in a different harness. Our records instead show liquidity as the margin on which blockers are released, with counters in 394 of 920 responses and 81 of 113 settlements after at least one counter. No model-generation or harness effect may be inferred from that contrast.
- **Cosentino et al.** The arXiv abstract page for v1 (fetched today). It reports that agents model the counterparty accurately but do not reliably convert that model into better bargains, that final agreements track opening anchors, and that "sellers are more accommodating overall". It supports the attention-versus-effectiveness framing as an established distinction, not a new one.
- **Jehiel and Moldovanu (1995).** The bibliographic record (Econometrica 63(6):1321–1335, IDEAS). Identity-dependent negative externalities can cause delay. In Monopoly the seller itself bears the externality, so the analogy is interpretive.

I did not re-read AgentMonopoly, the Arena study or Shleifer and Vishny. Earlier team readings are recorded in the drafts' literature notes.

Novelty is modest. LLM Monopoly, counteroffers, opponent modelling versus strategy, and liquidity failures in board games all exist in prior work. What this cohort adds is a complete-population, recipient-view account of how a completion externality and the holder's liquidity jointly shape refusal, counter, release and price, followed into debts and estates. The related-work paragraph should make that comparative point and nothing broader.

### 3.8 Unanswered questions

Keep all eight questions plus A–C, with the coverage table in the discussion or an appendix. Under the no-new-evaluation scope, the following remain unmeasured, and none is a negative capability finding:

- the general versus multi-agent relationship (B);
- learning caused by feedback;
- persuasion effects;
- transfer to unfamiliar opponents;
- calibrated beliefs about hidden information;
- effectiveness of prices and refusals;
- separate shares of skill and chance in winning.

The new results strengthen two rows. Row 2 (opponent modelling): buyers open completion requests to cash-poor holders about twice as often as other deed requests, 20/169 versus 9/160 without Opus, and their notes say so. Row 4 (planning): the static-menu lookahead failure versus 19 executed unlocked-collateral payments.

### 3.9 Fable's liquidity narrative

I checked each claim against its unit.

**(a) Cash-band rejection contrast (offer unit).** The headline 17/69 (24.6%) versus 120/175 (68.6%) mixes three things. 43 of the 69 low-cash completion requests are later offers, rejected at 9.3%. 21 go to Opus, which rejects 0 of 21. Low cash also lowers rejection of other deed requests, 5/22 versus 109/224. At openings among standard-condition holders, the completion increment persists in every cash band:

| Openings, standard-condition holders | <$100 | $100–299 | ≥$300 |
|---|---|---|---|
| Completion requests rejected | 13/20 (65.0%) | 17/24 (70.8%) | 105/125 (84.0%) |
| Other deed requests rejected | 4/9 (44.4%) | 7/13 (53.8%) | 92/138 (66.7%) |
| Increment | +20.6 | +17.0 | +17.3 |

By system, Gemini rejects 10 of 10 completion openings even under $100. Sol and Grok shift to counters. Opus counters at every level. Root's join shows that Sol's 26 low-cash completion requests come from only 9 threads in 6 games. Cash need lowers rejection of deed requests in general; it does not dissolve the guard at the threshold. Offers to cash-poor holders were not more generous: the median net cash offered is $165 below $100, $200 at $100–299 and $150 at ≥$300.

**(b) Refusal-to-sale sequences (pair unit).** In 13 of 14 the holder's cash was lower at the sale. Only 8 of the 14 holders, and 5 of 11 without Opus, were under $100 at the sale. Several sold with $444–774. The sequences are selected on an eventual sale. Unsettled multi-turn pairs also drift down (25 of 38 lower; medians $671.50 to $516), less steeply. This supports "release followed a fall in cash", not "release when cash ran out".

**(c) Thresholds.** The $100 and $300 bands and the eight-turn window were chosen after earlier work on the same records (Fable says so). The four- and twelve-turn sensitivities are reported. The cash bands should be presented as descriptive strata, with the opening-matched table above as the primary display.

**(d) Post-sale build/win (sale and player-game units).** 9/14 versus 1/29 sales and 8/13 versus 1/21 player-games. I restricted the comparison to sellers who already held a complete group at the sale, using my completion ledger. The split persists at 9/13 versus 0/9 sales and 8/12 versus 0/8 player-games, so the "must already own a group" objection alone does not explain it. However, 7 of the 9 group-holding non-builders had under $100 at the sale. "Built within eight turns" is also partly an outcome of the same strength that predicts winning. The split is conditioned on future behaviour and on the eventual winner. It is a description of trajectories, not a liquidity effect. It should not be in the abstract, and "separates the trajectories" should go.

**(e) "Until."** The title is not warranted. At openings the guard persists at every cash level among standard-condition holders. Gemini does not release. Opus never guards by refusal. The low-price distress sales are an Opus pattern under recovery: 0.66 times list, n = 8, against 2.25, n = 6, for standard-condition sellers. The strongest defensible version is that cash need makes the guard negotiable.

**(f) Is liquidity the central story or supporting evidence?** It is the hinge, but not the whole story. The defensive refusal is the primary regularity. Liquidity is its most important qualifier and the bridge to finance. The integrated title should say both.

## 4. Corrections to my own draft

1. Replace the opening comparator with the matched one: 73.8% versus 59.7%, +14.1, all blocks and all recipients positive. Report the later-offer null.
2. Withdraw "responses do not change with the proposer's post-trade building cash", "attention without calibration" and the categorical-rule mechanism, from the abstract, introduction, Section 4.4, Discussion 6.2 and the conclusion. The stratified gradient is weak and confounded but present.
3. Replace "its bargaining is not defensive" with: "Opus rarely rejects; it counters 75% of offers it receives, its asks rise for completing buyers, and it is the main source of below-list distress sales." Its condition and model remain inseparable.
4. Replace "Asking prices rise, bids do not" and "A market that clears under distress" with Sol's heterogeneous-bid formulation and with "completing sales in the observed population come disproportionately from cash-poor holders". The latter is a selected population, not a clearing mechanism (root agrees).
5. Remove the new "about 12% with doubles" aside in G13. Fix the rule table row that says auction prompts give prices and rents; they give the group only.
6. Cut G2 to three cards and the paper to roughly 20 main cards.

## 5. Dissent

**From root's provisional integration.** Root accepts my +9.9 comparator and "Opus's response ordering reverses". Both should be updated to the matched comparator. Root's central claim omits liquidity. After Fable, that omission is no longer defensible: liquidity is the variable the agents name when they release (G2 d128, G18 d420, G7 d142) and when they time bids (G7 d141, G15 d176). Root's execution leg should be rewritten around the static-menu planning error, the unlocked-collateral successes and the 2-of-68 building-preservation rate, not the bare 128. I agree with root's twelve material findings otherwise, including withdrawing my categorical claim.

**From Fable.** On the title, the abstract's lead contrast, and the abstract's build/win and 3.0× rent-per-landing claims, as set out in Section 3.9. Also: "forced liquidation is the one financial task every system handled reliably" implies a negative finding about other tasks that the cohort does not measure. I accept Fable's evidence and transcripts as the most valuable additions of this round.

**From Astra.** Successful payment is a positive execution result, but the menu scaffolds it, and it should not stand as the second headline in "strategic attention and economic execution". The more scientific execution result is the contrast between incremental success and static-lookahead failure.

**From Sol.** Sol's framing is the right interpretive frame but should not centre the paper on a negative valuation result. The positive regularity is the composition-matched refusal and its liquidity qualifier.

## 6. Remaining risks for any integrated paper

- Every contrast is exploratory and chosen after inspecting these games. The matched comparator, cash bands and windows are post hoc descriptive cuts. They need to be labelled so, with all cells shown.
- Offers are clustered in threads and pairs. Five seed blocks are the only replication unit.
- The recovery condition is inseparable from the Opus model, and it shapes the market faced by the other three agents. Gemini contributes almost no asks.
- The semantic codes come from two same-family LLM readers without human validation. The eight incidents are purposive, and seven involve Grok.
- No effectiveness reference exists. "Guarding" and "releasing" describe choices, not good play.
- Novelty is modest relative to FinBoardBench, AgentMonopoly and Cosentino et al.
