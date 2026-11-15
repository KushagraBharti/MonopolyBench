"""Build findings.json and check that every quoted passage occurs verbatim in
the frozen draft file it names. Read-only on the drafts."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FD = ROOT / "full_drafts"
OUT = HERE.parent / "findings.json"

A, S, O, F = "astra", "sol", "opus", "fable_5_2"
P = lambda draft, rel, text: {"draft": draft, "file": f"full_drafts/{draft}/{rel}", "text": text}

EVIDENCE_STATUS = {
    "verified_fresh": "Recomputed in this review from saved records or frozen ledgers by a script under reviews/fable_5_2/tools.",
    "verified_reading": "Checked in this review by reading a named source field, file or primary paper.",
    "agreement_across_drafts": "Independent rebuilds in the four drafts agree row by row, confirmed in this review.",
    "inherited": "Rests on earlier engine-executed checks or model-assisted labels that this review did not rerun.",
    "judgment": "A scientific or presentational judgment. No new arithmetic.",
}

findings = [
 {"id": "FBL-01", "severity": "major", "area": "central claim", "drafts": [O, A, S],
  "title": "The opening rejection contrast is carried by swaps and is absent for cash bids",
  "evidence_status": "verified_fresh",
  "passages": [
    P(O, "manuscript.tex", "Opening offers that would complete only the proposer's group are rejected more often than offers that complete nobody (74\\% against 64\\%)"),
    P(O, "sections/bargaining.tex", "The clearest contrast is between opening offers that would complete only the author's group and opening offers that complete no group."),
    P(A, "manuscript.tex", "Offers completing only their author's group are rejected more often than recipient-completing offers within both opening and later negotiations; the conditional gaps are about thirteen percentage points."),
    P(S, "sections/bargaining.tex", "The pooled rejection rate is 55.0\\% when only the author completes and 27.1\\% when only the recipient completes."),
  ],
  "evidence": "Opus's contrast reproduces (138/187 against 152/238, blocks +15.0, +18.9, +5.8, +7.6, +10.8). Its baseline pools three kinds of proposal. Every author-completing opening asks the recipient for a deed. The neither population also holds 62 openings that ask for none, refused 47/62. Split by form: swaps 95/116 (82%) against 37/72 (51%), accepted 1 against 17; cash bids 42/70 (60%) against 67/103 (65%), lower for completing bids in 4 of 5 blocks. The swap gap is positive for each recipient (Sol 12/21 v 1/16, Gemini 45/49 v 25/33, Grok 35/37 v 9/12, Opus 3/9 v 2/11) and each block. 29 of the 72 non-completing swaps and 13 of their 17 acceptances were opened by a conflicting Grok call; without the 64 such threads the shares are 93/112 and 26/43. First occurrence of a bundle: 77/93 and 33/67. Without Grok-authored swaps: 90/108 and 24/36. Later offers show no gap in either form. Astra's and Sol's author-only against recipient-only contrast compares being asked for a deed with being offered one.",
  "check_outputs": ["data/c3_defensive_contrast.json", "data/c3b_offer_type.json", "data/c3c_swap_table.json", "data/c3d_dedup.json", "data/c3e_grok_conflict_openings.json"],
  "resolution": "Lead the bargaining section with the split by offer form (replacement_prose.tex, Table 1 and Section 2.1). Keep Opus's all-offer contrast as the first sentence and the author-only against recipient-only cells in the full census table. State the gap as seventeen to thirty-four points across treatments and say that it belongs to openings."},

 {"id": "FBL-02", "severity": "major", "area": "central claim", "drafts": [O],
  "title": "The flat capacity cut does not support a categorical rule",
  "evidence_status": "verified_fresh",
  "passages": [
    P(O, "manuscript.tex", "Responses also do not change with the proposer's post-trade building cash, the quantity agents cite most."),
    P(O, "sections/discussion.tex", "A coherent reading is that the agents apply a categorical rule, roughly ``do not hand a rival a monopoly cheaply'', and then bargain over price with a generic routine."),
    P(O, "sections/bargaining.tex", "Their response follows the category, a rival completing a group, rather than the amount they cite."),
  ],
  "evidence": "The cut reproduces (100/134, 32/42, 6/11 opening; 13/65, 7/34, 1/3 later). By recipient it is at a ceiling for Gemini (46/50, 15/16, 1/1) and Grok (40/46, 11/12, 3/3) and small for Sol (12/26, 5/10, 2/5). The lowest cell is lower (55%). A proposer who offers more cash keeps less, so price is confounded with the grouping. The notes usually cite cash plus mortgage capacity, which the cut ignores. The same population responds in a graded way to the holder's own cash: quartiles for standard-condition holders are 41%, 64%, 81% and 77% rejection.",
  "check_outputs": ["data/c3_defensive_contrast.json", "data/c9_cash_sensitivity.json"],
  "resolution": "Report the cut as a null on one variable in one short paragraph (replacement_prose.tex, Section 2.4). Remove the categorical-rule mechanism from the abstract, the contributions and the discussion heading."},

 {"id": "FBL-03", "severity": "major", "area": "central claim", "drafts": [F],
  "title": "The title's 'until' and the release claim overstate the liquidity result",
  "evidence_status": "verified_fresh",
  "passages": [
    P(F, "manuscript.tex", "\\title{LLM Agents Withhold a Rival's Monopoly\\\\Until They Need the Cash"),
    P(F, "manuscript.tex", "These deeds move when the holder is short of cash."),
    P(F, "sections/introduction.tex", "\\emph{The deed moves when its holder is short of cash.}"),
  ],
  "evidence": "Of the 43 one-sided completing sales, 20 come from a holder with under $100, 6 from $100 to $299 and 17 from $300 or more. Twelve of the 20 are Opus under action-only recovery. Without Opus as holder the split is 8, 5 and 10. By holder: Opus 12 of 20, Sol 4 of 8, Grok 3 of 10, Gemini 1 of 5. Gemini rejects 10 of 11 requests under $100. Opus rejects 3 of 52 at any level, so it does not withhold.",
  "check_outputs": ["data/c2_refusal_to_sale.json", "data/c6_distress_populations.json", "data/c9_cash_sensitivity.json"],
  "resolution": "Drop the title. Present liquidity as the condition under which the guard weakens, with the system-by-system counts (replacement_prose.tex, Section 3 and the third discussion paragraph)."},

 {"id": "FBL-04", "severity": "major", "area": "denominators", "drafts": [F],
  "title": "The 25% against 69% headline is inflated by Opus as holder and by thread position",
  "evidence_status": "verified_fresh",
  "passages": [
    P(F, "manuscript.tex", "of requests for such a deed, and asking prices rise as the buyer nears a complete group while bids rise little"),
    P(F, "sections/introduction.tex", "The gap appears in each of the five seed blocks."),
  ],
  "evidence": "Pooled 17/69 against 120/175 reproduces. 21 of the 69 low-cash requests go to Opus, which rejects none. 43 of the 69 are later offers against 40 of the 175. For standard-condition holders the contrast is 13/20 against 105/125 at the opening and 4/28 against 12/24 later. By system: Sol 4/26 against 25/45, Grok 3/11 against 46/52, Gemini 10/11 against 46/52. Nineteen of Sol's 26 low-cash requests come from G1, G9 and G18. Thresholds of $50 to $200 and $300 or $500 keep the sign. Mortgage status of the requested deed does not explain it. Low cash also lowers refusal of non-completing requests (4/9 against 92/138 at the opening), and the completion gap is 17 to 21 points in every band, so the prediction in my initial position that the guard vanishes for poor holders is not supported.",
  "check_outputs": ["data/c1_cash_by_cell.json", "data/c9_cash_sensitivity.json"],
  "resolution": "Report the standard-condition counts by thread position and by system. State that the two regularities add at the opening. Do not put a pooled percentage in the abstract."},

 {"id": "FBL-05", "severity": "major", "area": "selection", "drafts": [F],
  "title": "The refusal-to-sale pairs do not separate cash pressure from a better offer",
  "evidence_status": "verified_fresh",
  "passages": [
    P(F, "sections/liquidity.tex", "The sharper evidence follows a pair through time."),
    P(F, "sections/liquidity.tex", "The comparison holds the holder, the buyer and the group fixed."),
  ],
  "evidence": "Cash fell in 13 of 14, as stated. The net cash to the holder was higher at the sale than in the first declined request in 8, equal in 2 and lower in 4. The deeds exchanged differ in 9 of the 14, and five refused swaps later sold for cash alone. Only 8 of the 14 holders had under $100 at the sale. In the 38 multi-turn pairs that never settled, holder cash also fell in 25, and in 18 of the 24 that started at $300 or more. Refusals are selected on high cash and sales on lower cash, so some fall is built into the comparison.",
  "check_outputs": ["data/c2_refusal_to_sale.json"],
  "resolution": "Keep the pair table in an appendix with the declined and accepted terms side by side. Describe the histories as consistent with cash pressure and not as sharper evidence (replacement_prose.tex, 'Histories')."},

 {"id": "FBL-06", "severity": "major", "area": "selection", "drafts": [F],
  "title": "Seller conversion (9 of 14 against 1 of 29) is mostly group ownership and is conditioned on winning",
  "evidence_status": "verified_fresh",
  "passages": [
    P(F, "manuscript.tex", "Sellers who built houses within eight turns of such a sale won in"),
    P(F, "sections/introduction.tex", "\\emph{What the cash becomes separates the trajectories.} Some cash-poor sellers were paying for their own houses, and most of them won."),
  ],
  "evidence": "Twenty of the 29 sales without building were made by sellers who held no complete group and could not build. By player-game: 20 held a group when they sold, of which 12 built within eight turns (8 won) and 8 did not (0 won); 18 held no group (1 won). At the sale level the seller won 10 of 43 and the buyer 11 of 43. The split survives inside group holders but rests on 20 player-games and uses the game's outcome.",
  "check_outputs": ["data/c4_seller_conversion.json"],
  "resolution": "Remove from the abstract and the list of results. Keep one paragraph at the player-game level with the group split and the seller and buyer win counts (replacement_prose.tex, 'What followed')."},

 {"id": "FBL-07", "severity": "moderate", "area": "scope", "drafts": [F],
  "title": "The two-and-two building contrast reads as a ranking under conditions that forbid one",
  "evidence_status": "verified_fresh",
  "passages": [
    P(F, "sections/introduction.tex", "After completing a group by trade, Sol and Gemini almost always built at once, while Opus and Grok often did not."),
    P(F, "sections/discussion.tex", "Turning a position into income is rarer, and it is where their trajectories differ."),
  ],
  "evidence": "First management turn: 16/17, 17/18, 7/15, 3/13 (inherited classification, same in all four drafts). Of the 18 unbuilt windows for Opus and Grok, 9 had no legal build (8 groups with a mortgaged deed), 3 were engine defaults after an uncorrectable action-only plan and 4 were conflicting Grok calls. Three timing definitions circulate: 43 (first management turn), 44 (by the owner's next turn, Opus) and 54 (ever).",
  "check_outputs": ["data/c7_landings_and_misc.json"],
  "resolution": "Report once, by system, with the causes beside the counts, as the open-ended contrast to the liquidation census. Use the first-management-turn definition in the main text and give the other two in a table note."},

 {"id": "FBL-08", "severity": "moderate", "area": "headline", "drafts": [A],
  "title": "The liquidation census shows execution under a menu, and the 'reasoning' wording overreaches",
  "evidence_status": "verified_fresh",
  "passages": [
    P(A, "manuscript.tex", "These provide positive evidence of executed financial reasoning"),
    P(A, "sections/discussion.tex", "A second finding concerns \\emph{executed multi-step reasoning}."),
    P(A, "sections/execution.tex", "Sixty-seven take one action, while sixty-one require two to ten."),
    P(F, "manuscript.tex", "Forced liquidation is the one financial task every system handled reliably"),
  ],
  "evidence": "All counts reproduce from saved events: 188 episodes, 128 paid, 60 eliminated, none unclosed; 67 single-action and 61 multi-action payments; 180 mortgage and 89 sale actions; 68 episodes with building sales; $51,997 paid. The 67 single-action payments have a median shortfall of $35 (35 mortgages, 32 sales). The menu offers only mortgage, building sale and bankruptcy, so paying mostly means not declaring early. 'Require' is unverified: no draft shows that a two-action payment could not have been made in one. What is informative: 128 of 131 payable; mortgage first in 40 of 51 where both options were offered; only 2 of 68 sold buildings when menu mortgages would have covered; two of the three payable declarations omit collateral that selling buildings would unlock. My draft's 'the one financial task' claims uniqueness that nothing measures.",
  "check_outputs": ["data/c5_debt_census.json", "data/c11_prose_facts.json"],
  "resolution": "Keep the census in the abstract as one sentence and give it its own section titled by the task structure (replacement_prose.tex, Section 4). Say 'take' or 'use', not 'require'. Say execution, not reasoning, except where a checked note is quoted."},

 {"id": "FBL-09", "severity": "moderate", "area": "headline", "drafts": [S],
  "title": "'Several distances' is a reading of four incidents and should frame the paper, not head it",
  "evidence_status": "judgment",
  "passages": [
    P(S, "sections/introduction.tex", "Our central finding is that competitive consequences enter bargaining at several distances from the immediate exchange."),
    P(S, "sections/discussion.tex", "The strongest supported discovery is competitive-option attention"),
  ],
  "evidence": "The population support for rival-directed reasons is the inherited 61 of 74 codes. Construction funds, resale through an intermediary and inheritance are each shown by one or two selected incidents (G2, G15, G20, G13, G18). Sol's abstract leads with a negative (no identified premium) and reports no positive behavioral contrast of its own.",
  "check_outputs": [],
  "resolution": "Use Sol's definition of strategic attention and its attention against effectiveness distinction as the frame. Anchor it with the offer-form contrast and the price cells. Present the three distances as what the incidents show."},

 {"id": "FBL-10", "severity": "moderate", "area": "numbers", "drafts": [S, A],
  "title": "The G1 and G15 concentration is 31 of the 61 agreed codes and 34 of the 74 rows",
  "evidence_status": "verified_fresh",
  "passages": [
    P(S, "sections/bargaining.tex", "However, thirty-four common-positive labels come from G1 and G15"),
    P(A, "sections/bargaining.tex", "thirty-four records come from G1 and G15"),
  ],
  "evidence": "The retained row file has 22 rows from G1 and 12 from G15 (34 of 74). The common-positive keys hold 21 from G1 and 10 from G15 (31 of 61). Opus and Fable state both correctly.",
  "check_outputs": ["data/c7_landings_and_misc.json"],
  "resolution": "Write '31 of the 61 agreed codes (34 of the 74 rows) come from G1 and G15'."},

 {"id": "FBL-11", "severity": "moderate", "area": "estimand", "drafts": [A, S, O, F],
  "title": "Same seller, game and deed: 4, 2, 1 and 5, 1, 1 differ by one row and one summary",
  "evidence_status": "verified_fresh",
  "passages": [
    P(A, "sections/bargaining.tex", "four have a higher completing-buyer median, two a lower one and one a tie"),
    P(S, "sections/bargaining.tex", "Four have higher median asks to the completing buyer, two lower, and one equal"),
    P(O, "sections/bargaining.tex", "The first ask to the completing buyer is higher in five, lower in one and equal in one."),
    P(F, "sections/attention.tex", "The tightest comparison is weaker."),
  ],
  "evidence": "Rows: G1 Opus Boardwalk 150, 100 against 350; G2 Sol Marvin Gardens 650, 600 against 450; G4 Opus Boardwalk 450, 250, 175, 100, 150 (mortgaged, turns 152 to 164) against 280 (unmortgaged, turn 74); G15 Opus Baltic 180, 150, 120, 100 against 100; G16 Grok Marvin Gardens 1,200 against 400; G17 Grok Mediterranean 35 against 35; G20 Grok New York 400, 400 against 120. Median: 4 higher, 2 lower, 1 equal. First ask: 5, 1, 1. Last ask: 3, 2, 2. Only G4 moves between median and first ask, and it is the one row whose mortgage status differs. On the six mortgage-matched rows both summaries give 4, 1, 1. Every completing ask exceeds every other ask in 3 of 7.",
  "check_outputs": ["data/c8_spot_checks.json"],
  "resolution": "Print the seven rows. State 4, 1, 1 for the six mortgage-matched rows under either summary and describe G4 separately. This is a reason-based choice and not the more favorable definition."},

 {"id": "FBL-12", "severity": "moderate", "area": "denominators", "drafts": [O, S, F],
  "title": "Three 'distress sale' populations need one primary definition",
  "evidence_status": "verified_fresh",
  "passages": [
    P(O, "manuscript.tex", "Completing deeds change hands mostly when the holder is short of cash (14 of 22 such cash sales)."),
    P(S, "sections/bargaining.tex", "Among forty-eight cash settlements completing the paying side's group, twenty-one sellers have less than \\$100, compared with thirty low-cash cash-receiving settlements overall."),
    P(O, "sections/discussion.tex", "\\subsection{A market that clears under distress}"),
  ],
  "evidence": "All three reproduce from one ledger. Opus: cash for deeds only, completes the payer, 14/22 against 7/31 completing nobody (6/11 against 4/22 without Opus sellers). Sol: any net-cash settlement completing the payer, 21/48; its comparison figure is 30 of 107 net-cash settlements, and the sentence omits the 107. Fable: settlements completing exactly one party, 20/43 against 9/57 cash settlements completing nobody (8/23 against 6/41 without Opus). 'Mostly' is true of 14/22 only. Under the wider definitions it is 20/43 and 21/48. All condition on settlement.",
  "check_outputs": ["data/c6_distress_populations.json"],
  "resolution": "Primary: settlements completing exactly one party (43), with the cash-only subset and the without-Opus counts in the same sentence. Say over-represented, not mostly. Retitle the discussion subsection."},

 {"id": "FBL-13", "severity": "moderate", "area": "scope", "drafts": [O],
  "title": "Buyer and seller generalizations flatten system heterogeneity",
  "evidence_status": "verified_fresh",
  "passages": [
    P(O, "sections/bargaining.tex", "\\subsection{Asking prices rise, bids do not}"),
    P(O, "sections/bargaining.tex", "Holders thus price a rival's completion more consistently than buyers price their own."),
  ],
  "evidence": "Asks to completing buyers are higher in 11 of 12 seller, mortgage and stage cells (Sol's table reproduces) but the pooled ordering reverses in blocks 1 and 5. Bids: Sol higher for own completion, Grok lower, Opus slightly higher. The asymmetry is two systems moving in opposite directions.",
  "check_outputs": ["data/c11_prose_facts.json"],
  "resolution": "Say that asks rise in most cells and that bids move in no common direction, naming the systems (replacement_prose.tex, Section 2.2)."},

 {"id": "FBL-14", "severity": "moderate", "area": "novelty", "drafts": [A, S, O, F],
  "title": "No draft cites prior work on denying trades to a leading rival in multi-player trading games",
  "evidence_status": "verified_reading",
  "passages": [
    P(O, "sections/bargaining.tex", "Defensive bargaining can also be collective."),
    P(S, "sections/discussion.tex", "Our contribution is the bounded behavioral account enabled by complete offer histories, financing opportunities, and estate trajectories"),
    P(A, "sections/discussion.tex", "Thus neither LLM Monopoly play nor contextual bargaining is novel by itself."),
    P(F, "sections/discussion.tex", "Earlier work built scorable multi-party negotiation games with greedy and adversarial players"),
  ],
  "evidence": "Guhe and Lascarides, 'The Effectiveness of Persuasion in The Settlers of Catan', IEEE CIG 2014 (doi 10.1109/CIG.2014.6932861). Read here from the Edinburgh Research Explorer PDF text layer, pages 2, 4 to 6 and 9. Symbolic agents; persuasion aims include 'Fewer Opponent Trades', with the example 'Don't trade with him! He's about to win!'; moves to embargo a player or block a resource ('Don't give him ore, because then he'll build a city and we're all doomed'); the JSettlers baseline already refuses to trade with a player at eight or more victory points; 10,000 simulated games per condition with compliance imposed; an embargo helps most at seven points and is too late at eight. This is the same consideration as G20's funding appeal and Opus's G15 appeal.",
  "check_outputs": ["verification.md, 'Literature'"],
  "resolution": "Add the related-work paragraph in replacement_prose.tex. State the contribution as unprompted appearance in LLM play, the instruments used and the dependence on liquidity."},

 {"id": "FBL-15", "severity": "moderate", "area": "incidents", "drafts": [A, S, O, F],
  "title": "The main incident sets lack a transcript of successful execution",
  "evidence_status": "verified_fresh",
  "passages": [
    P(A, "sections/execution.tex", "In G20 d327--336, Sol starts with \\$49 against \\$1,400 and combines \\$700 building salvage with \\$665 mortgages, paying with \\$14 left."),
    P(S, "sections/economy.tex", "Starting with \\$49, it raises \\$700 in building salvage and \\$665 through mortgages, pays \\$1,400, and retains \\$14."),
    P(F, "sections/default.tex", "In G20 Sol met a"),
  ],
  "evidence": "Three drafts mention the G20 payment in one sentence and none quotes it. The saved notes show Gemini computing Sol's liquidation value as $1,414 before raising the rent to $1,400 (d325), Sol stating the same total and the $14 remainder before its first action (d327), and seven of its ten notes giving the exact remaining shortfall. Events confirm $700 from two sale actions, $665 from eight mortgages, rent event 2245 and $14 in the next prompt. Sol's second note plans to mortgage the browns once their buildings are sold, which is the step the two payable declarations in G12 and G17 omit (they leave out $340 and $375 of unlockable mortgage value).",
  "check_outputs": ["data/new_quote_manifest.json", "data/g20_payment_facts.json", "data/c11_prose_facts.json"],
  "resolution": "Make the G20 payment a main incident beside G12 (replacement_prose.tex, Section 4, four generated cards). The brief asks for competent execution in the eight."},

 {"id": "FBL-16", "severity": "moderate", "area": "incidents", "drafts": [F, O],
  "title": "Incident load and balance: G19 in an appendix, 44 and 31 cards, Grok in seven of eight",
  "evidence_status": "verified_reading",
  "passages": [
    P(F, "sections/appendix.tex", "\\paragraph{A false premise is corrected and the offer accepted (G19).}"),
    P(O, "sections/discussion.tex", "seven involve Grok, whose separate content and call channels make conflicts visible"),
  ],
  "evidence": "Fable moves the one incident of competent correction (G19) to an appendix and prints 44 cards and about 8,200 words of main prose. Opus prints 31 cards, seven for G2. Astra uses 17 cards and Sol 19 for the same eight incidents. All quotation manifests in the four packages pass an independent source check here (28, 10 and 14 inherited entries, 4 new Opus entries and 50 Fable entries; file hash, field hash and span).",
  "check_outputs": ["data/c10_quote_sources.json"],
  "resolution": "Eight main incidents with 20 to 24 cards (integration_proposal.md, incident table). G19 returns to the main text in compact form. G2 keeps three cards including Sol's d119 resale note."},

 {"id": "FBL-17", "severity": "moderate", "area": "pre-estate", "drafts": [O, F, S, A],
  "title": "Pre-estate positions use four proxies and two timings, and one sentence leans causal",
  "evidence_status": "agreement_across_drafts",
  "passages": [
    P(O, "sections/consequences.tex", "Positions just before the transfer favour the second reading"),
    P(F, "sections/default.tex", "In most games, then, the first estate went to the player already ahead."),
    P(S, "sections/economy.tex", "First creditors lead or tie in prior paid rent in fifteen games"),
    P(A, "sections/inheritance.tex", "A new check of the delivered state immediately before the first elimination finds its creditor already strictly ahead in building levels in twelve games, cash in eight and deed count in six."),
  ],
  "evidence": "First creditor wins 18 of 20 in all drafts. It leads in prior rent in 15 (Sol, Opus), in a list-price asset index in 15 (Opus, Fable), in building levels in 12 (Astra, Sol), in cash in 8 and strictly in deeds in 6. The rent and asset counts are both 15 but name different games (rent rank is below first in G4, G7, G9, G17, G20; asset rank in G4, G7, G15, G17, G20). Fable measures at the first liquidation menu and Astra and Sol before the bankruptcy action. Eighteen of twenty is conditioned on the winner.",
  "check_outputs": [],
  "resolution": "One case table with all proxies per game and one timing. Lead with prior rent and buildings, which need no valuation. Write that most first creditors were already ahead on these measures and that this neither shows nor excludes an effect of the estate. Keep the five discordant games visible."},

 {"id": "FBL-18", "severity": "minor", "area": "numbers", "drafts": [O],
  "title": "Median debt at elimination is $912.50; $925 is the upper median",
  "evidence_status": "verified_fresh",
  "passages": [P(O, "sections/consequences.tex", "The paid debts are smaller (median \\$250, against \\$925 at elimination)")],
  "evidence": "The 30th and 31st of the 60 elimination debts are $900 and $925. tools/debts.py takes the element at index n // 2.",
  "check_outputs": ["verification.md, 'Small numeric points'"],
  "resolution": "Print $912.50 or say 'about $900'."},

 {"id": "FBL-19", "severity": "minor", "area": "scope", "drafts": [O],
  "title": "An unscoped probability is added to G13",
  "evidence_status": "verified_reading",
  "passages": [P(O, "sections/consequences.tex", "about 12\\% with doubles")],
  "evidence": "The figure ignores cards, jail and the three-doubles rule. The point of the incident is the omitted mortgage.",
  "check_outputs": [],
  "resolution": "Keep the single-roll statement (4 in 36 against the claimed 5 in 36) and drop the 12%."},

 {"id": "FBL-20", "severity": "minor", "area": "setup", "drafts": [O],
  "title": "The rule table says prices and rents appear in auction prompts",
  "evidence_status": "verified_reading",
  "passages": [P(O, "sections/setup.tex", "Prices and rents appear only in purchase and auction prompts")],
  "evidence": "Opus's own prose, the other three drafts and the saved prompts agree that auction prompts give the group only. A saved liquidation prompt (G20 d329) lists deed keys with no values.",
  "check_outputs": ["data/c11_prose_facts.json"],
  "resolution": "Table row: prices and rents in purchase prompts, group in auction prompts, none elsewhere."},

 {"id": "FBL-21", "severity": "minor", "area": "numbers", "drafts": [S, O, F, A],
  "title": "The 213 landings split 150 and 63 under two different partitions",
  "evidence_status": "verified_fresh",
  "passages": [
    P(S, "sections/economy.tex", "Group landings during ownership & 150 & 63"),
    P(O, "sections/consequences.tex", "Opponents land on these groups 213 times while the completing owner holds them, 150 times after the owner has built"),
  ],
  "evidence": "By first-management-turn class: 150 and 63 landings, rent $53,810 and $3,568. By whether a building stood at the landing: 150 and 63, rent $56,126 and $1,252. The coincidence is real. Cross table: 133 and 17 on first-turn groups, 17 and 46 on the others. Per-group landings and rent agree across the Sol, Opus and Fable rebuilds for all 63 groups.",
  "check_outputs": ["data/c7_landings_and_misc.json"],
  "resolution": "Use one partition in the main text (building present at the landing answers the question a reader asks) and note the other in the table."},

 {"id": "FBL-22", "severity": "minor", "area": "numbers", "drafts": [A],
  "title": "Seven or eight of the nine no-option windows have a mortgage, by two definitions",
  "evidence_status": "verified_fresh",
  "passages": [P(A, "sections/execution.tex", "Seven of the nine receive a mortgaged completing deed")],
  "evidence": "Eight of the nine groups held at least one mortgaged deed at completion (Sol and Fable). Astra counts the completing deed itself.",
  "check_outputs": ["data/c7_landings_and_misc.json"],
  "resolution": "Use 'eight of the nine groups held a mortgaged deed'."},

 {"id": "FBL-23", "severity": "minor", "area": "citations", "drafts": [F],
  "title": "Two economics citations in my draft rest on abstract-level reading",
  "evidence_status": "verified_reading",
  "passages": [P(F, "sections/introduction.tex", "which is the standard setting for a forced sale below value~\\cite{shleifer1992liquidation}")],
  "evidence": "My own literature_inspiration.md records that Shleifer and Vishny (1992, 2011) and Rubinstein (1982) were read at the abstract or record level only. The fire-sale prediction also fits only Opus's prices.",
  "check_outputs": [],
  "resolution": "Cite Jehiel, Moldovanu and Stacchetti (1996) and Jehiel and Moldovanu (1995), which were read. Drop the fire-sale framing from the introduction or have someone read the 1992 paper first."},

 {"id": "FBL-24", "severity": "minor", "area": "census", "drafts": [A, S, O, F],
  "title": "One paid episode contains a Grok action whose text names another action",
  "evidence_status": "verified_fresh",
  "passages": [
    P(A, "sections/execution.tex", "In 128 episodes the agent raises funds and pays"),
    P(S, "sections/economy.tex", "In 128, the final action emits payment of the recorded amount."),
  ],
  "evidence": "No paid or eliminated episode contains an engine default. Among Grok's 30 actions in 20 paid episodes, 11 carry text that names an action and one names a different action from the applied call (G1, turn 210, $550 debt). Six Grok elimination episodes contain such a disagreement, including G12 d249.",
  "check_outputs": ["data/c5_debt_census.json"],
  "resolution": "One clause in the census paragraph. Success is an observed system outcome and not every action can be assigned to a coherent text."},
]

# --- validate passages ---------------------------------------------------------------------
problems = []
for f in findings:
    for p in f["passages"]:
        path = ROOT / p["file"]
        if not path.exists():
            problems.append((f["id"], "missing file", p["file"])); continue
        body = path.read_text(encoding="utf-8")
        if p["text"] not in body:
            problems.append((f["id"], "passage not found", p["file"], p["text"][:70]))
        else:
            p["line"] = body[: body.index(p["text"])].count("\n") + 1
assert not problems, problems

manifest = json.load(open(ROOT / "four_draft_hashes.json"))
for f in findings:
    for p in f["passages"]:
        key = "docs/research_raw/paper_revision_2026-11-11/" + p["file"]
        assert key in manifest, key
        p["file_sha256"] = manifest[key]

out = {
    "schema": "reviews/fable_5_2 findings v1",
    "reviewer": "Fable 5.2 (whole-paper coauthor)",
    "date": "2026-11-11",
    "scope": "Cross-review of the four frozen drafts under full_drafts/. Existing-record arithmetic and reading only. No game, engine run, replay, model call, synthetic test or baseline.",
    "severity_scale": {"major": "Changes the central claim, a headline number or the title.",
                       "moderate": "Changes a section's argument, a denominator or the novelty statement.",
                       "minor": "A number, a definition or a sentence."},
    "evidence_status": EVIDENCE_STATUS,
    "counts": {"findings": len(findings),
               "by_severity": {s: sum(f["severity"] == s for f in findings) for s in ("major", "moderate", "minor")},
               "by_draft": {d: sum(d in f["drafts"] for f in findings) for d in (A, S, O, F)}},
    "findings": findings,
}
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out["counts"]))
