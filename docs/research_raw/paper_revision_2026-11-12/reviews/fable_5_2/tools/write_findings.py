#!/usr/bin/env python3
"""Write ``findings.json`` for the Fable 5.2 cross-review.

The findings are authored here as Python literals so that LaTeX passages keep
their backslashes exactly, and the script checks that every quoted passage
occurs on the stated line of the stated frozen file before writing.
"""
from __future__ import annotations

import json
from pathlib import Path

REV = Path(__file__).resolve().parents[3]
FD = "full_drafts/"


def loc(path, line, passage):
    return {"file": path, "line": line, "passage": passage}


F = []


def add(fid, drafts, kind, severity, title, locations, evidence, recommendation, checked):
    F.append({"id": fid, "drafts": drafts, "kind": kind, "severity": severity, "title": title,
              "locations": locations, "evidence": evidence, "recommendation": recommendation,
              "check_status": checked})


add("XR-F52-01", ["fable_5_2"], "overreach", "major",
    "The quit-or-continue comparison is partly forced, partly definitional, and thin near the boundary",
    [loc(FD + "fable_5_2/sections/own.tex", 14, r"The table does show discrimination at the first menu. The agents quit almost always when no payment existed and almost never when one did. This is level three: the choice agrees with the arithmetic of the state."),
     loc(FD + "fable_5_2/manuscript.tex", 13, r"Agents declared bankruptcy at the first menu in \fact{d.above-bound.declared-at-first-menu} of \fact{d.above-bound.episodes} debts that exceeded everything they owned and in \fact{x.debt.payable.declared} of \fact{d.payable} payable debts."),
     loc(FD + "fable_5_2/sections/discussion.tex", 42, r"Agents almost always quit when no payment existed and continued when one did."),
     loc(FD + "fable_5_2/sections/appendix.tex", 209, r"quit or continue agrees with payability in \fact{x.debt.agree} of \fact{x.debt.known} debts")],
    "The counts reproduce from raw liquidation records: bankruptcy was the first applied action in 50 of 56 debts above every own asset and in 3 of 131 payable debts. Three facts change the reading. (1) Eight of the 56 first menus list declare_bankruptcy as the only action, so eight of the fifty were not choices. Among the 48 menus with another action, 42 declared first. (2) 128 of the 131 payable debts are payable because the agent paid them, so 'continued' is part of the definition on that side, and '178 of 187 agree' adds 128 definitional and 8 forced cases. (3) The two classes are far apart. 87 of 131 payable debts were under half the asset sum, and the 48 above-bound debts had assets covering a median 61% of the debt. Within a tenth of the boundary there are 3 payable debts (all paid) and 6 above-bound debts (3 declared first, 3 liquidated first). Source: data/check_debts.json, keys first_action, above_bound_menu, margin.",
    "Keep the first action as one column of the debt table and one paragraph (replacement_prose.tex, section 2.1). Remove it from the abstract, the introduction's lead, the conclusion and the question-1 row. Drop 'discrimination' and 'level three'.",
    "fresh, from stored records")

add("XR-F52-02", ["fable_5_2", "opus"], "construct", "major",
    "A first-menu resource partition is presented as measured difficulty",
    [loc(FD + "fable_5_2/sections/own.tex", 14, "Most payable debts were easy."),
     loc(FD + "fable_5_2/sections/own.tex", 21, r"The third row of Table~\ref{tab:debt} is the hard set."),
     loc(FD + "fable_5_2/handoff.md", 36, "Against referee A: the first-menu partition calibrates difficulty from stored records."),
     loc(FD + "opus/sections/finance.tex", 6, r"\subsection{Most debts were easy}"),
     loc(FD + "opus/sections/introduction.tex", 20, r"\item A complete debt census that separates easy from dependent liquidation"),
     loc(FD + "opus/sections/finance.tex", 17, "The decision that needs foresight is whether to stop"),
     loc(FD + "opus/sections/discussion.tex", 23, "Scoring execution length or success rates mostly measures easy states.")],
    "The 62/53/16 rows are arithmetic on the first menu (reproduced in data/check_debts.json, tiers_among_payable). They say which resources a payment needed. No reference policy was run on these states, so nothing measured how hard any row was, and a refreshed menu shows each released deed after the sale. 'Whether to stop is the decision that needs foresight' is an interpretation of the same partition.",
    "Use Astra's sentence (astra/sections/finance.tex:9): 'These categories characterize financing requirements, not calibrated levels of task difficulty.' Rename Opus's subsection and my 'hard set'. Keep the one-action count and the 36% median as descriptions.",
    "fresh arithmetic; the judgment about wording is mine")

add("XR-F52-03", ["fable_5_2"], "error", "major",
    "What the liquidation request contains, and which stated figures are recalled",
    [loc(FD + "fable_5_2/sections/setting.tex", 7, "It gives no price, mortgage value or sale value, and it does not say that selling buildings releases mortgages."),
     loc(FD + "fable_5_2/sections/own.tex", 38, r"Of \fact{x.nc.numbers.checked} stated totals, gaps or remainders, \fact{x.nc.numbers.equal} equal the value computed from the records."),
     loc(FD + "fable_5_2/sections/own.tex", 38, "Since the prompt supplies none of these values, each one is a board fact the system recalled.")],
    "In all 338 stored liquidation requests the action state and the player's own state carry no price, mortgage value or sale value, and neither the system prompt nor the menu note states the release rule. That part holds. But the same request carries a twenty-row public timeline, and 511 of those rows across liquidation requests are mortgages shown with their dollar amount. So 'the prompt gives no mortgage value' is false for the request as a whole. In the sixteen first requests the timeline shows no mortgage of the deeds concerned and one redemption price (G13, Park Place, $193). The '14 of 15' count is one figure per text of mixed kinds (a gap after sales, cash after payment, the two failures' correct partial sums). The count that bears on the claim is narrower: nine successful texts put a dollar value on the unlisted mortgages and eight are right (G2 Sol writes $430 for $400). Opus's '12 of 13 explicit texts with every amount correct' is consistent with this. Source: data/check_request_values.json; hand check of all financing amounts in the sixteen texts.",
    "Replace both sentences with the wording in replacement_prose.tex, 'The stated amounts'. Say the values are not in the request for those deeds. Do not say each figure was recalled.",
    "fresh, from stored requests; amounts hand-checked against the sixteen printed texts")

add("XR-F52-04", ["fable_5_2"], "overreach", "major",
    "A null result on a coarse post hoc measure is stated as a finding about what refusals follow",
    [loc(FD + "fable_5_2/manuscript.tex", 13, "Refusals mention the rival's set under both forms, yet rejection does not rise with the building the rival could then afford."),
     loc(FD + "fable_5_2/manuscript.tex", 13, "Stated concern about rivals matches action and attaches to the event of completion."),
     loc(FD + "fable_5_2/sections/rival.tex", 61, "If refusals in general followed that reasoning, they would be more common when the proposer would keep more building cash. They are not."),
     loc(FD + "fable_5_2/sections/rival.tex", 73, "It does not follow the measured size of what the rival could do next, which level four would require."),
     loc(FD + "fable_5_2/sections/discussion.tex", 7, "It is also what an agent would do if the word ``monopoly'' alone drove the refusal.")],
    "The capacity slices reproduce (swaps 26/33, 42/48, 23/27; cash bids 13/19, 7/20, 20/28; data/check_recipient_conflicts.json, rejected_by_proposer_house_capacity). The cells hold 19 to 48 offers, the measure ignores what the proposer could still mortgage, the bands were chosen after inspection, and the offers in each band differ in everything else. Flat counts in such cells do not show that responses ignore the size of the opportunity. The sentence about the word 'monopoly' has no record behind it.",
    "Keep the slices in the appendix with Opus's wording (opus/sections/bargaining.tex:49, 'these slices give no sign that refusals scale with the rival's building power'). Remove the claim from the abstract, the section close and the conclusion. Delete the 'word monopoly' sentence.",
    "fresh, from stored records")

add("XR-F52-05", ["fable_5_2"], "quotation", "moderate",
    "G13: an editorial ellipsis removes the buyer's second stated motive, and the odds error is misdated",
    [loc(FD + "fable_5_2/sections/quotes.tex", 16, r"potentially completing that color group. \textnormal{[\ldots]} so keeping grok solvent with cash from a \$200 purchase seems favorable overall"),
     loc(FD + "fable_5_2/sections/talk.tex", 13, "Its public odds of 5 in 36 overstate a direct roll of nine, which is 4 in 36. Its own note uses the correct figure"),
     loc(FD + "fable_5_2/sections/talk.tex", 13, "Opus's text repeats the estate concern and does not address the financing claim.")],
    "The stored text returned with Opus's acceptance (G13 d253) reads, between the two quoted parts: 'If grok goes bankrupt to me instead, that could hand me the yellows and build pressure against them at my orange hotels,'. The 'so' that follows refers to that sentence. The ellipsis makes the conclusion appear to rest on denying Sol the estate alone. On the odds: the note sent with the public pitch (d250) says '8 Short Line $200 to p2 (5/36, they inherit yellows)'. The public 5/36 repeats a miscounted distance. The 4/36 figure is in the next decision's note (d252). Opus held $1,926 at d253. Source: data/quote_manifest.json ids g13-d250-note, g13-d253-reason.",
    "Quote the whole span. Say the public figure repeats the note's miscount. Add the buyer's cash. Replacement text: replacement_prose.tex, section 4.",
    "fresh, from stored fields")

add("XR-F52-06", ["opus"], "quotation", "moderate",
    "G13: the quoted sentence is not the estate concern it is said to repeat",
    [loc(FD + "opus/sections/conduct.tex", 30, r"Its returned reasoning repeats the estate concern: \emph{``\InlineQuote{g13-accept-reason-inline}.''}"),
     loc(FD + "opus/sections/quotes_generated.tex", 87, r"\DeclareInlineQuote{g13-accept-reason-inline}{If grok goes bankrupt to me instead, that could hand me the yellows and build pressure against them at my orange hotels, so keeping grok solvent with cash from a \$200 purchase seems favorable overall}")],
    "The quoted sentence states a different prospect: that Grok might later go bankrupt to the buyer, which would hand the buyer the yellows. The concern about Sol inheriting is the preceding sentence of the same stored text ('if player 4 goes bankrupt to player 2, player 2 would inherit the yellows plus Pennsylvania').",
    "Quote both sentences and describe two stated routes. Opus's observation that the buyer's interest in Grok's solvency is recorded at its $130 counter, before the selective claim, is correct and should be kept.",
    "fresh, from stored fields")

add("XR-F52-07", ["astra", "sol"], "omission", "minor",
    "G13: the buyer's returned text is summarized as one motive",
    [loc(FD + "astra/sections/conduct.tex", 29, "Its explanation repeats the concern about Sol inheriting the yellows."),
     loc(FD + "sol/sections/continuations.tex", 18, "Its returned explanation repeats the estate concern after the appeal, rather than establishing an independently recorded prior motive.")],
    "Both sentences are true and incomplete. The same text also weighs the buyer inheriting the yellows itself, and the buyer held $1,926 against a $200 price. Astra and Sol are right that the concern follows the opening pitch. Opus is right that it precedes the selective claim. The three statements are compatible.",
    "Use one account: the concern is recorded after the pitch (d250) and before the selective claim (d252), and the acceptance text gives two routes.",
    "fresh, from stored fields")

add("XR-F52-08", ["astra", "sol", "opus", "fable_5_2"], "population", "moderate",
    "Applied acceptances include calls whose own text refuses",
    [loc(FD + "astra/sections/negotiation.tex", 5, "Each nevertheless accepts between 26 and 30 offers. Those similar settlement totals emerge from different ways of responding to disagreement."),
     loc(FD + "sol/sections/bargaining.tex", 4, "Nevertheless each accepts between 26 and thirty offers."),
     loc(FD + "opus/sections/bargaining.tex", 7, "and each accepts 26 to 30 offers"),
     loc(FD + "fable_5_2/sections/rival.tex", 14, r"An opening swap or cash bid that would complete only the proposer's group was accepted \fact{x.po.accept} times in \fact{x.po.n}.")],
    "All four drafts report Grok's conflicting calls among its openings (64 of 136). None reports them among responses. In 11 of the 920 responses the selected attempt's assistant content names a tool other than the received call. All are Grok's, and 7 of them are among its 28 acceptances (6 name reject_trade, 1 names counter_trade). Of the three accepted opening offers that complete only the proposer's group, two are such calls: G16 d247, where the applied public message itself reads 'No. Park Place is not for sale.', and G18 d83. The third (G3 d194) agrees with its text. The swap gap is unaffected (30.5 with all responses, 31.2 without the conflicted ones). Source: data/check_recipient_conflicts.json.",
    "Add one sentence to the census and one to the opening table (replacement_prose.tex, section 3.1). Do not treat 3 of 186 as three decisions to accept.",
    "fresh, from stored records")

add("XR-F52-09", ["astra", "sol", "opus", "fable_5_2"], "uncertainty", "moderate",
    "Each draft prints a different resampling range for the same contrast, and the narrowest one is drawn as the main bar",
    [loc(FD + "astra/sections/negotiation.tex", 21, r"The whole-block resampling range is 24.2--35.5 points, but removing Grok authors changes it to $-3.8$--31.9."),
     loc(FD + "astra/sections/negotiation.tex", 25, r"gray segments show the central 95\% of all 3,125 whole-block resamples"),
     loc(FD + "sol/sections/bargaining.tex", 28, "Exact block resampling yields central bands of [24.2, 35.5] for swaps, [-18.0, 3.2] for cash bids and [-3.8, 31.9] for swaps without Grok authors."),
     loc(FD + "opus/sections/bargaining.tex", 39, r"The two-stage resampling interval is $+12.3$ to $+48.8$ points for all swaps"),
     loc(FD + "fable_5_2/sections/tables.tex", 69, r"Swap rejection gap, all proposers & 95/116 vs 37/72 & +30.5 & 5/5 & +28.7 to +33.3 & +24.2 to +35.5 & +13.8 to +47.8 \\")],
    "All printed ranges reproduce to within simulation noise (data/check_offers.json, resampling). For all swaps: whole blocks 24.2 to 35.5 (exact, 3,125 resamples), games 14.0 to 47.9, blocks then games 12.5 to 48.8. Without Grok-authored offers: -3.8 to 31.9, -1.9 to 37.9, -10.1 to 40.5. Whole-block resampling is the narrowest for the unfiltered gap because the five block totals differ less than the games inside a block. With five units it understates spread, and Astra's figure draws it as the only bar. No draft is wrong on the arithmetic. They disagree on which number a reader sees first.",
    "Print the five block values, leave-one-block-out and all three resampling units in one table (replacement_prose.tex, Table 5). State the two findings that hold under every unit: the unfiltered swap gap stays positive, and without Grok-authored offers every range includes zero. Call none of them a confidence interval.",
    "fresh resampling of stored observations")

add("XR-F52-10", ["astra", "fable_5_2"], "construct", "moderate",
    "Title and summary words name a cognitive construct the text says it does not measure",
    [loc(FD + "astra/manuscript.tex", 4, r"\title{Planning and Bargaining in a Persistent Economy:\\An Observational Study of LLM Agents}"),
     loc(FD + "astra/manuscript.tex", 14, "supply evidence of local financial planning alongside a complete account of their negotiation behavior"),
     loc(FD + "astra/sections/scientific_introduction.tex", 3, "These episodes pose a concrete question about LLM planning"),
     loc(FD + "fable_5_2/manuscript.tex", 13, "Stated foresight about the agent's own financing is accurate and matches action.")],
    "Astra's own results section says the texts 'remain recorded statements, not a measurement of the computation producing the action' (astra/sections/finance.tex:19). 'Planning' in the title and 'foresight' in my abstract promise more than that.",
    "Use Sol's title, 'Stated opportunities and executed choices'. In summaries write 'stated anticipation followed by consistent action'.",
    "reading")

add("XR-F52-11", ["opus"], "overreach", "moderate",
    "A general lesson is drawn from sixteen debts and eight chosen incidents",
    [loc(FD + "opus/sections/discussion.tex", 23, "Where channels agree, a stated plan is a good guide to the action that follows, so it is worth reading."),
     loc(FD + "opus/sections/discussion.tex", 5, "Second, the failures we can trace lie in the assessment rather than in carrying it out.")],
    "Agreement between a stated assessment and the next action was examined in the sixteen unlisted-collateral debts and in incidents chosen for clarity. In that set it holds 16 of 16 at the first action. No population of statements was sampled. 'The failures we can trace' are three: two omissions and one call that contradicts a correct note.",
    "Scope both sentences to the cases examined, as the same paragraph's first sentence does ('in the debts and incidents we examined').",
    "reading, with the counts confirmed in data/check_debts.json")

add("XR-F52-12", ["opus", "fable_5_2"], "method", "moderate",
    "A one-pass keyword screen is reported as what recipients' stated reasons are",
    [loc(FD + "opus/manuscript.tex", 11, "and recipients give similar reasons under both forms"),
     loc(FD + "opus/sections/bargaining.tex", 44, "The stated reasons are much the same under both forms."),
     loc(FD + "fable_5_2/sections/rival.tex", 40, "The stated reasons do not separate the two forms.")],
    "Both rest on regular expressions over the public message and applied note (terms such as 'set', 'third', 'close', 'house'). Opus answered 162 of its 189 trade responses through recovery and has no note. My refusal-style columns were written after reading examples (fable_5_2/handoff.md:59). The screen shows that completion and building words are common in rejections under both forms. It does not code reasons.",
    "Keep the screen in the appendix under its own name. Take the sentence out of Opus's abstract. Drop my refusal-style table or move it to the appendix as a pattern count.",
    "reading; the counts themselves were not rerun in this review")

add("XR-F52-13", ["sol", "opus"], "population", "moderate",
    "The main offer table folds sale offers into 'other', and one cash comparison does not name its population",
    [loc(FD + "sol/sections/full_offer_rows.tex", 10, r"Other & Recipient only & 93 (12/46/35) & 45 (1/15/29) & 48 (11/31/6) \\"),
     loc(FD + "opus/sections/bargaining.tex", 18, "Holders also reject 29 of 45 offers to sell them the deed that would complete their own group, usually at a high price."),
     loc(FD + "sol/sections/continuations.tex", 3, r"Non-completing requests also receive fewer refusals below \$100, 4/9 versus 92/138.")],
    "The 45 opening 'other, recipient only' offers are 41 sale offers (1 accepted, 14 countered, 26 rejected) and 4 others. Holders rejecting 26 of 41 offers to sell them their own completing deed is a row a reader should see, and Opus's '29 of 45 offers to sell' counts the 4 other offers as sales. The 4/9 and 92/138 counts reproduce only for opening deed requests that complete nobody's group and go to Sol, Gemini or Grok (data/check_recipient_conflicts.json, holder_cash_opening_to_sol_gemini_grok). Over all four recipients they are 4/10 and 94/150.",
    "Use four forms as Astra and I do (astra/sections/opening_complete.tex). Name the population in the cash sentence.",
    "fresh, from stored records")

add("XR-F52-14", ["astra"], "wording", "minor",
    "A causal verb for an association",
    [loc(FD + "astra/sections/conduct.tex", 5, "Cash affects both the willingness to transact and what a transaction enables.")],
    "The paragraph that follows reports counts by holder cash and ends 'There is no uniform threshold'. The counts reproduce (17/69 and 120/175). They are an association with stage and recipient mixed in, as the paragraph says.",
    "Open with Sol's sentence (sol/sections/continuations.tex:3), 'Low cash often accompanies bargaining engagement rather than immediate acceptance.'",
    "fresh for the counts")

add("XR-F52-15", ["astra", "sol", "fable_5_2", "opus"], "fact", "minor",
    "Incident details that the events state more exactly",
    [loc(FD + "astra/sections/conduct.tex", 18, "Sol adds three dark-blue houses within eight turns."),
     loc(FD + "sol/sections/appendix.tex", 24, "Sol adds three dark-blue houses within eight turns."),
     loc(FD + "fable_5_2/sections/appendix.tex", 32, "Sol adds three dark-blue houses within eight turns."),
     loc(FD + "opus/sections/bargaining.tex", 69, "and loses the group to Gemini at its bankruptcy on turn 86"),
     loc(FD + "opus/sections/finance.tex", 28, "Gemini at G4 d270 and G8 d257 names the released mortgages without valuing them.")],
    "G7: Sol builds the three houses at turn 71, three turns after the sale, as Opus writes. It sells one of them at turn 72 in a liquidation and two more at turn 87. Sol's note at the build says it can sell a house if rent requires. G2: the events record Sol's bankruptcy at turn 85. The first request that shows it bankrupt is at turn 86. Sixteen texts: Grok at G18 d313 also names the released mortgages without a value. The $270 of orange rent to Gemini in G7 reproduces.",
    "Write 'three turns later' for G7 and add that one house was sold the next turn. Use turn 85 for G2. List three unvalued texts.",
    "fresh, from stored events")

add("XR-F52-16", ["fable_5_2", "opus"], "omission", "moderate",
    "Two drafts drop the ownership populations that say what a trade becomes",
    [loc(FD + "fable_5_2/findings_and_limits.md", 83, "Asking-price medians, construction receipts and first-estate concentration are not in this manuscript."),
     loc(FD + "opus/evidence_map.md", 58, "| Construction defaults, first-estate counts, exposure summaries | Not used in this draft | n/a |")],
    "Astra and Sol keep them in two paragraphs each. The transfer counts reproduce from stored events (data/check_economy.json): 113 accepted trades move 207 deeds and complete 63 groups; non-final estates move 227 deeds and complete 52 groups; 69 more groups complete only at the final elimination; 38 of 40 non-final eliminations follow rent on the creditor's developed color property; the first estate went to the eventual winner in 18 of 20 games. I did not recompute first-window construction (16/17, 17/18, 7/15, 3/13) or rent receipts ($57,378), which remain inherited.",
    "Restore one subsection from Sol's 'Groups become productive, then change hands' (sol/sections/continuations.tex:23-28) with Astra's sentence that receipts are not incremental returns.",
    "fresh for transfers and eliminations; construction and receipts inherited")

add("XR-F52-17", ["fable_5_2"], "wording", "minor",
    "The appendix leans toward a cause for the provider refusal",
    [loc(FD + "fable_5_2/sections/appendix.tex", 191, "That fits a refusal which follows a request for private reasoning and stops when the request is removed, but the saved responses do not name the category.")],
    "The saved responses carry one message, a content_filter finish reason and no category. The other three drafts state that and stop.",
    "Delete the sentence up to 'but'. Keep 'the saved responses do not name the category'.",
    "reading")

add("XR-F52-18", ["astra", "sol", "opus", "fable_5_2"], "addition", "none",
    "A source-checked sequence none of the drafts has: the same omission made in advance and revised at the debt (G5)",
    [loc(FD + "opus/sections/finance.tex", 28, "Gemini's returned reasoning at G5 d263 first totals only the house sales, then writes that the deeds can be mortgaged after the houses are sold"),
     loc(FD + "fable_5_2/sections/own.tex", 32, "The provider-returned text of the same response shows the sum being revised")],
    "Four turns before the debt (G5 d258) Gemini's applied note justifies spending $200 on a house with 'my total liquidatable cash + houses is $774 < $900', a total that omits the two dark-blue deeds. That note is in the stored request for d263. The text returned at d263 starts from the house sales and then says 'I initially miscalculated!', and the applied note gives the full $1,049 budget. In G17 the same system leaves the same two deeds out and declares. One sequence, not a rate.",
    "Use it as the worked illustration inside the sixteen-case result (replacement_prose.tex, 'The same system both ways'). It is supporting material like the G12 and G17 notes and not a ninth incident.",
    "fresh, from stored fields; presence of the earlier note in the later request asserted in tools/verify_replacement.py")

add("XR-F52-19", ["astra", "sol", "opus"], "addition", "none",
    "G15: the refusal follows another player's public appeal, which is in the refuser's request",
    [loc(FD + "astra/sections/negotiation.tex", 34, r"At G15 turn 63, Sol offers two greens for Ventnor and \$100, completing both groups."),
     loc(FD + "sol/sections/bargaining.tex", 40, r"At G15 turn 63, Sol has \$730 and Grok \$333."),
     loc(FD + "opus/sections/bargaining.tex", 54, r"At G15 turn 63, Sol has \$730 and Grok \$333.")],
    "One turn earlier (G15 d166) Opus ends its turn with the public message 'GPT now owns 2 reds, 2 greens and 2 yellows and has $1000+ in cash. He's the one to watch, so let's not hand him the last piece of any set.' The message is in Grok's stored request at d169. Gemini also rejects a Sol offer on that turn (d171). My draft has this (fable_5_2/sections/rival.tex:52). It is a second public appeal besides G20, and it bears on question 7.",
    "Add one sentence to the G15 card. Do not claim the appeal caused the refusal.",
    "fresh, from stored fields")

add("XR-F52-20", ["astra", "sol", "opus", "fable_5_2"], "strength", "none",
    "Passages to carry into the integrated paper as written",
    [loc(FD + "astra/sections/scientific_introduction.tex", 3, r"A player owes \$1,400 and holds \$49 in cash."),
     loc(FD + "astra/sections/finance.tex", 9, "These categories characterize financing requirements, not calibrated levels of task difficulty."),
     loc(FD + "sol/sections/methods.tex", 38, "Prospective means recorded in the first resolved response before subsequent liquidation feedback, not independent of the state supplied in that request."),
     loc(FD + "sol/sections/finance.tex", 20, "Reporting nineteen as a success denominator would mix a chosen financing route with a required dependency."),
     loc(FD + "opus/sections/bargaining.tex", 51, "One description fits the counts: completing the proposer's group is usually met with refusal in a swap and with a higher price in a cash bid. Why is not identified."),
     loc(FD + "opus/sections/conduct.tex", 57, "Opus's redemptions change what completing the greens would cost, so its later bids do not contradict its explanation."),
     loc(FD + "fable_5_2/sections/own.tex", 53, "Ten actions are not ten steps of lookahead. What Sol fixed in advance was the total, the decision not to concede, and the reliance on")],
    "Each is the clearest statement of its point among the four drafts and each survived the checks in this review. Also adopt Opus's figure of the sixteen debts (opus/assets/necessary_collateral.pdf), Opus's configuration table (opus/sections/design.tex:12-18), Sol's appendix of the sixteen full first texts (sol/sections/necessary_texts.tex) and Sol's replay paragraph (sol/sections/appendix.tex:162-164).",
    "See integration_proposal.md for placement.",
    "reading")


def main():
    problems = []
    for f in F:
        for l in f["locations"]:
            p = REV / l["file"]
            lines = p.read_text().split("\n")
            if l["passage"] not in lines[l["line"] - 1]:
                problems.append((f["id"], l["file"], l["line"]))
    out = {
        "reviewer": "fable_5_2",
        "date": "2026-11-12",
        "scope": "All-four whole-paper cross-review of the frozen 12 November drafts. Line numbers are 1-based lines of the frozen files in four_draft_manifest.json.",
        "severity_scale": {
            "major": "changes a claim in an abstract, introduction or conclusion",
            "moderate": "changes the reading of a paragraph, table or incident",
            "minor": "a precision or wording fix that leaves the reading intact",
            "none": "not a defect: an addition or a passage to adopt",
        },
        "passages_verified_on_stated_lines": not problems,
        "findings": F,
    }
    path = Path(__file__).resolve().parents[1] / "findings.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(len(F), "findings;", "all passages found on stated lines" if not problems else f"NOT FOUND: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
