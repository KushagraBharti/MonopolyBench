# Initial position: Opus xhigh, final whole-paper review

Written 2026-11-12 after reading, and before opening `integrated/INTEGRATION_DECISIONS.md`, `integrated/adjudication.json`, the integrated README/handoff/evidence map, or any November 12 cross-review or final-review folder.

Disclosure: my session memory index carries one-line summaries of my own and Fable's earlier cross-reviews. They mention an omitted liquidation note, a 50/56 quit-or-continue comparison, Grok composition behind 3/186, and a capacity null at ceiling. I did not open those files. The position below rests on what I read in this session.

## What I read

- `FINAL_REVIEW.md` and `CHARTER.md`.
- Both full referee reports: `inline_review.md` (4/10) and `attached_review.txt` (5/10, all 649 lines).
- `integrated/manuscript.tex` and every active section: introduction, study, cohort table, finance, necessary rows and all sixteen initial texts, negotiation, the opening/proposer/recipient/stability/resampling/full-offer tables, conduct, interpretation (discussion, related work, limitations, conclusion), the supplement, both prompt files and all five quote-macro files.
- All 21 rendered pages of the pinned PDF, at 80 dpi. I re-rendered page 19 at 150 dpi to check that the prompts are legible.

Pin check before reading: 78/78 manifest entries match. The PDF SHA-256 is `f0312183…ed8a1`.

## Scientific judgment

**The paper states a coherent and worthwhile result.** Its best contribution is in the finance section, which is honestly bounded:

- 16 debts can be paid only with mortgages that become available after building sales.
- 14 are paid. In 13 of those, the first text names the released mortgages or gives a budget that includes them. In one (G20 d291) it raises them as a question.
- Both failures add up correctly but leave out the released collateral, then declare immediately.

I read all sixteen printed fields myself. I agree with the split: 12 explicit, 1 aggregate (G20 d327), 1 tentative (G20 d291), 2 omissions. The arithmetic in Table 9 matches the texts I checked: G12 = 53 + 225 + 130 = 408, and the omitted red mortgages are 340. G17 = 500 + 30 = 530, and the omitted mortgages are 375. G20 = 49 + 700 + 665 − 1,400 = 14.

This is a genuine statement-then-action observation. It improves on a bare 128/131 payment rate, and the paper keeps the two apart.

**The 188/131/128 census and the requirement table are sound.** The paper correctly separates financing requirements from difficulty, and calls the first-action counts context, not a classifier score.

**Bargaining is presented as composition-sensitive and exploratory, which is right.**

- All nine opening cells are printed, including both-completing at 34/48.
- The paper prints both proposer and recipient strata, the no-Grok drop (30.5 to 16.7 points) and the no-conflict variant (22.6).
- All three resampling schemes appear in the appendix, with an explicit "does not correct selection" statement.
- The 61/74 semantic population is now declared disjoint from the headline cells. That fixes the referee's most specific population complaint.

**The eight incidents are well chosen and mostly carefully hedged.** Each names its channel. G18 no longer claims an inheritance motive. G13 now shows the buyer weighing both estate outcomes.

## Substantive concerns to verify, in priority order

1. **The meaning of the necessary-collateral statements for LLM interpretation.** The rule that releases mortgages after building sales is the official Monopoly rule, and is presumably familiar from pretraining. The paper says the prompt does not enumerate it, and that liquidation states identify deeds without their values.
   - If that holds, the successful texts show a familiar rule applied to state-specific quantities, with mortgage values recalled or carried. That is positive and informative, but it is not discovery of a dependency, and the paper should say so.
   - I need to check whether the liquidation prompt or legal-action payload hints at locked mortgages, for example with a "sell buildings first" note or a list of locked deeds. Such a hint would shrink "anticipation" to reading the prompt.

2. **The cash-bid direction.** The introduction says the cash-bid comparison "points in the other direction." That is true only pooled (−5.0). Within each recipient the cash-bid gaps run from −0.2 to +8.5, all at or above zero. The direction is itself a composition result, and the introduction should not present it as a contrast in sign.

3. **The no-Grok block values.** Figure 2 appears to show one seed block with a negative no-Grok difference, around −23. The text gives only the leave-one-block-out range (9.4–22.1), plus the statement that the *unfiltered* difference stays positive across blocks. A reader of the prose alone would not learn that one of five blocks reverses once Grok's offers are removed. This needs a number check.

4. **The abstract's "completing and non-completing swaps."** Both-completing swaps (34/48) are also completing. The contrast is proposer-only against neither.

5. **The Opus "provider-returned explanation" channel.** Five of the fourteen successes rest on it. I need to check what the field is (a provider summary or raw reasoning text) and whether it comes from the recovery attempt. If it is a summary, the paper should say that the "statement" is provider-mediated.

6. **Incident source spans.** These need source checks: the new G13 buyer text, the G5 revision text, the prior public warnings in G2 and G15, the G18 withdrawal, the G20 Opus follow-on offers, G7's $700 and $270, and G15's "eighteen turns later."

7. **Replay description.** "Artifact replay … empty excluded-event list" and "state replay removes four observational LLM event types" should be checked against the stored replay reports. The referee flagged a discrepancy between drafts here.

8. **Smaller wording issues, low priority.** G13 says "recognizes a $130 Ventnor mortgage," but the note itself does not state a value. "Sensitive to offer form" in the conclusion invites a causal reading. "Establish" in the abstract is stronger than "document." The prompts are set in scriptsize verbatim: legible, but small.

## What I do not expect to recommend

I do not expect to recommend a structural rewrite, new evaluations, cutting the eight incidents, or a numerical uncertainty summary presented as correcting selection.

The paper's scope and hedging are mostly right. The remaining risks are narrower:

- framing sentences in the abstract and introduction that outrun the appendix tables;
- the prompt-information question behind "anticipation";
- the accuracy of individual incident continuations.
