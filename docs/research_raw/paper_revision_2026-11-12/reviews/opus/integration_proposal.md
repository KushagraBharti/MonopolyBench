# Integration proposal (Opus)

One paper, built from the best supported version of each claim in the four drafts, corrected by the checks in `review.md`. `replacement_prose.tex` writes out the title, abstract, introduction, both results sections and the discussion paragraph that carry the claim. Section numbers below refer to the proposed paper.

## Title and claim

**Title.** What a Move Unlocks: Stated Consequences and Applied Actions of LLM Agents in Twenty Monopoly Games (Fable's title, "Applied" for "Actions" to match the channel vocabulary).

**Claim, in one paragraph.** Some moves change what can be done next. Selling a group's buildings lets its deeds be mortgaged; selling the last deed of a group lets a rival build. We ask whether LLM agents state such consequences before acting, whether the statements match the state, and whether the applied action agrees. For the agent's own finances, the answer is yes in a set fixed by rule arithmetic: the first-decision text counts collateral that no prompt lists or values at that point, the choice to quit or continue separates payable from unpayable debts even at similar shortfalls, and the two failures follow sums that leave the released collateral out. For rivals, recipients name the completion in nearly every refusal and the systems state distinct refusal policies, but the form-dependent rejection pattern depends on who wrote the offers and nothing in the records explains it. No result shows that a choice was good.

## Section plan

1. **Introduction** (about 700 words). Fable's opening (what a move unlocks; two places to ask). Evidence ladder stated once (Fable's and my wording). Findings in two paragraphs, own then rival, then one sentence on the eight incidents. Contributions: the debt census with first-choice and first-text links; the complete offer census with composition and uncertainty; eight sourced incidents. Configured systems, not models.

2. **Setting and method** (about 1,300 words).
   - Game and interface: Fable's paragraph, plus the liquidation scenario note quoted in full (OPX-01), plus the field inventory: trade and liquidation prompts carry no group, price, rent or mortgage value.
   - Cohort and configurations: my Table 1 (decisions, attempts, tool choice, recovery, fallback), with tool choice cited from 8,687 request records and source at both commits (Fable; corrects Sol's evidence map).
   - Opus recovery and Grok channel conflicts: Fable's two paragraphs.
   - Channels and receipt: Fable's four-channel paragraph.
   - Measures: offers (Sol's operational definitions), debts (Fable's four sums, with Astra's sentence that tiers are requirements, not difficulty).
   - Uncertainty: my two-stage resampling as the single interval, with per-block and leave-one-block-out values shown first; one sentence on why block-only resampling is narrow; Sol's sentence on what recounting does and does not validate.
   - Text readings: one model reader, spans printed (Fable, Sol).

3. **The agent's own options** (about 1,400 words).
   - 3.1 All 188 debts: Fable's table extended with a visible-shortfall column; 128/131 paid; 67 one-action payments; median debt 36 percent of the bound. Requirement language only.
   - 3.2 Quit or continue: the 72 visible-shortfall debts (50/56 against 2/16; 15/19 at matched shortfall); G12 Grok as a channel conflict; continuers are five Grok and one Gemini; the scenario note.
   - 3.3 Sixteen debts: Fable's table plus Sol's appendix of all sixteen first-decision fields; 13 count, 1 raises, 2 omit; channels; G5/G17 Gemini contrast on the same two deeds; G1 Grok note as the example; values and rule absent from the environment, with the carried-note qualification (OPX-05).
   - 3.4 Incident 1, G20 payment (body card): budget, not an ordered plan; creditor's components; five released mortgages.
   - 3.5 Nineteen uses (14 necessary, 5 optional) in two sentences.

4. **A rival's options** (about 1,500 words).
   - 4.1 Census: 920 responses, 918 acceptance-legal; counters dominate Sol and Opus, rejections Gemini and Grok; openings rarely settle outside Grok's offers (11/389; Grok 21/135; later 81/394) (OPX-03).
   - 4.2 Opening table by form and completion (Astra's complete table with zero cells).
   - 4.3 Swap/cash contrast with composition: proposer table with gaps suppressed below five offers (OPX-12); recipient table; Grok's share of comparator swaps and acceptances; three composition versions; proposer- and recipient-standardized gaps with weights (OPX-09); per-block, leave-one-out and two-stage interval figure (my Figure 2 layout with Fable's open-circle blocks).
   - 4.4 Replies and reasons: counters with both baselines (OPX-08); keyword screen; refusal styles with baselines; the prompts never label completion; 61/74 as a disjoint population with its exact definition.
   - 4.5 Two alternatives narrowed: list value and capacity, with the ceiling caveat (OPX-04).
   - 4.6 Incidents 2 and 3 (body cards): G15 with Opus's prior appeal; G2 with Grok's public warning and the earlier $450 ask (OPX-10).

5. **Third parties and the uses of talk** (about 700 words). Fable's structure: the estate mechanism (35 of 40 nonterminal estates to the eventual winner); Incident 4, G13 (body card, with Grok's turn-150 bankruptcy on Short Line and Opus's win); one-paragraph summaries of G7, G19, G20 appeal and G18, each pointing to the casebook.

6. **Discussion** (about 600 words). What the two results share; why the finance evidence is sharper (a checkable endpoint, not better reasoning); what the bargaining records cannot separate (Fable's rule-versus-keyword paragraph, without "tracked the event of completion"); configured systems; one paragraph on what a prospective test would vary (matched states, fixed definitions), stated as future work without predicted results.

7. **Related work** (about 450 words). Union of Fable's and Sol's paragraphs, keeping only claims each author recorded having read. Cite Guhe and Lascarides for embargoes, Jehiel et al. descriptively, AgentMonopoly, FinBoardBench, Cattle Trade (workshop and arXiv kept distinct), NegotiationArena, Cosentino et al., PlanBench, Li et al., Vending-Bench, faithfulness work.

8. **Limitations** (about 350 words). Astra's compact version plus: the scenario note shapes the quit decision; readings are one model's; the three retrospective slices added in review; inherited executions.

9. **Conclusion** (about 150 words).

Main prose target: about 5,800 words.

## Appendix plan

A. Casebook: G7, G19, G20 appeal, G18 (Fable's text, with Astra's G13 and G18 qualifications and the continuation facts checked in review section 3.12).
B. Offer tables: full 918-offer table by stage (Sol), later offers, recipient strata, block table, resampling table with all three units and why they differ (mine), capacity, keyword and wording tables with baselines, counter changes, thread settlement, 61/74 population, composition of accepted openings at list value.
C. Debt tables: sixteen rows (mine or Fable's) and all sixteen first-decision fields (Sol); 188-episode partition with visible-shortfall column; carried-note inventory for the sixteen; the three payable declarations; G7 menu restriction; above-bound continuers.
D. Reproducibility: repository, checkpoint, both run commits, seeds, game map (Sol's or mine), both replay comparisons (all drafts agree), analysis entry point.
E. Prompts and response conditions: both prompts (Sol's full text, Fable's diff), the liquidation note, refusal message, Opus timing, usage.
F. Research questions: the table below.
G. Research assistance and provenance: no human annotation; no human byline invented.

Economic context that Astra and Sol keep (first-window builds, construction receipts, first-estate counts, asking-price pairs) goes in a short supplement section labeled as inherited context, with Sol's exposure caveat, or is dropped. It should not return to the body.

## Eight questions and A to C

| Question | Supported answer | Not measured |
|---|---|---|
| 1. Strategic reasoning | Stated consequences of sales for own collateral and of trades for rivals; first choice to quit agrees with payability (50/56 vs 2/16 where visible sums fall short) | Optimal play, regret |
| 2. Opponent modeling | Post-trade cash and building budgets computed for rivals (G15, G7), some wrong (G2); creditor's liquidation estimate (G20) | Calibrated beliefs |
| 3. Cooperation, negotiation, deception | Full census; stated refusal policies by system; bluff, omission, correction, appeal, withdrawn assurance | Effect of any tactic |
| 4. Planning and memory | Sixteen dependent debts with prospective text; G20 ten-action execution of a budget; carried notes hold liquidity figures and twice the release rule; G9 three-house target reached | Memory benefit, lookahead depth |
| 5. Adaptation | Counters that keep the bundle and change the price; G5 correction within one response | Learning across games |
| 6. Economics and risk | 188-debt requirement partition; quit-or-continue | Optimal liquidation, reserves |
| 7. Collective dynamics | Public warnings before refusals (G2, G15) and the G20 appeal, receipt checked; estates go to the eventual winner in 35 of 40 | Coalition effects |
| 8. Evaluation validity | Recovery path, forced tool choice, channel conflicts, misattributed summaries, scenario note; both replay comparisons | Behavior under a repaired interface |
| A. Talk and action | Where channels agree, applied actions follow statements, right or wrong; Grok's 139 conflicts are the exception | Whether better explanations go with better play |
| B. General and multi-agent ability | No independent capability measure | Any relation |
| C. Skill, chance, weak opponents | Wins by system and seat; winners without trades (G14, G15) | Causal shares |

## What to drop or reword everywhere

- "Easy", "hard set", "calibrates difficulty" (OPX-06).
- "Because of", "to deny", "follows/attaches to the event of completion", "does not follow the size" (OPX-04, OPX-11).
- "Board fact the system recalled" without the carried-note qualification (OPX-05).
- "Planning" without "stated" (OPX-13).
- Block-only bands as the only interval (OPX-07).
- 3/186 against 21/175 as a completion effect (OPX-03).

## Open decisions for the owner

- Human byline, venue and AI-assistance statement.
- Whether the economic context section stays in the supplement.
- Whether to commit the analysis package so the repository URL supports reproduction.
