"""Write findings.json and assert that every quoted passage sits at the stated file and line.

Document-only. Usage: python3 -I build_findings.py <integrated_dir> <out_json>
"""
import hashlib
import json
import sys
from pathlib import Path

root, out_path = Path(sys.argv[1]), Path(sys.argv[2])
PIN = "8268234265df2bb9e0cf9a3303a51f79992e96e69a42b1d074c867697313feb5"
assert hashlib.sha256((root / "manuscript.pdf").read_bytes()).hexdigest() == PIN

F = []
MISSES = []


def add(fid, severity, title, file, line, passage, evidence, resolution, check, replacement=None, sources=None):
    text = (root / file).read_text().splitlines()
    if passage not in text[line - 1]:
        key = passage.split()[1] if len(passage.split()) > 1 else passage
        at = text[line - 1].find(key)
        MISSES.append((fid, file, line, passage[:70], text[line - 1][max(0, at - 60):at + 160]))
    F.append({"id": fid, "severity": severity, "title": title, "file": f"integrated/{file}", "line": line,
              "exact_passage": passage, "evidence": evidence, "proposed_resolution": resolution,
              "replacement_block": replacement, "check": check, "sources": sources or []})


CANON = "saved_games/railway-research-*/game-*/run/decisions.jsonl"
EVENTS = "saved_games/railway-research-*/game-*/run/events.jsonl"

# ------------------------------------------------------------------ blocking
add("FF-D01", "blocking", "The no-option category is stated for every group but holds only for the completed group",
    "sections/development.tex", 6,
    "nine with no construction option on any recorded menu",
    "The first management prompts for Grok's G1 orange window (d298) and G1 dark-blue window (d314) both list "
    "build_houses_or_hotel among available actions, with buildable_space_keys = [ATLANTIC_AVENUE]. Both attached "
    "notes discuss and decline the Atlantic house. The retained ledger defines the category per target group. The "
    "same two decisions are also counted among the 663 end_turn actions on menus offering construction, so the "
    "section places them in two populations that the present wording makes mutually exclusive. The same wording "
    "recurs in the Figure 1 bar label and caption (development.tex line 10), methods.tex line 8, and the heading "
    "and text of Appendix B.1 (appendix.tex lines 94 and 97). All nine Table 11 rows and remainders reproduce.",
    "Say 'no recorded menu offers construction on the completed group' in all five places, and state that two G1 "
    "prompts list a buildable house on another group. No count changes.",
    "performed: original decision_started prompts for all nine windows; resolution_conditions.json end_records",
    "FF-D01", [CANON, "data/first_management_windows.json", "data/resolution_conditions.json",
               "checks/windows_prices_conflicts.json"])

add("FF-L01", "blocking", "A liquidation ceiling in G16 is described as an executed liquidation",
    "sections/finance_inheritance.tex", 18,
    "In G16, extensive liquidation instead reaches \\$1,393 against \\$2,000.",
    "At G16 d602 the debt menu opens with cash $288 and owed $2,000. The applied action is declare_bankruptcy with "
    "no prior sale or mortgage. The attached note reads: 'Even selling all Light Blue hotels ($375) and mortgaging "
    "all remaining unmortgaged properties ($730) would only bring total cash to $1,393'. Table 12 prints cash 288 "
    "and bound 1,393 for the same row. The paragraph opens 'Actual staged liquidation can succeed', so the "
    "sentence reads as a second executed liquidation. The G20 d327-336 figures in the same paragraph reproduce "
    "($49 + $700 + $665 = $1,414 against $1,400).",
    "State that Gemini declares at the first debt menu and that its note computes the $1,393 total, which equals "
    "the bound. This is a correct insolvency calculation and can be presented as one.",
    "performed: original G16 d602 and G20 d327-337 records; data/t06_eliminations.json",
    "FF-L01", [CANON, "data/t06_eliminations.json"])

add("FF-Q01", "blocking", "Fifteen displayed cards labelled 'excerpt' quote the complete field",
    "sections/transcript_quotes.tex", 3,
    "Grok · public message · G13 d250 · attempt 0 · excerpt",
    "The integration corrected eight labels in fable_quotes.tex from 'excerpt' to 'full field'. The same condition "
    "remains in transcript_quotes.tex. My field-level match finds that these displayed cards equal the whole "
    "original field: g13-opening-insurance (line 3), g13-seller-counter (4), g13-acceptance (7), g18-assurance (8), "
    "g18-invocation (9), g18-withdrawal (10), g18-withdrawal-explanation (11, modulo trailing whitespace), "
    "g20-coordination-appeal (12), g20-concrete-refusal (15), g7_d43_public (21), g19_d135_false_public (24), "
    "g19_d136_correction_accept (25), g12_d249_public_bankruptcy (28), g20-received-and-applied-public (29) and "
    "g20-recipient-recognition (30). Two declared but unused cards share it: g13-seller-floor (5) and "
    "g20-sale-response (14). All 49 declared cards, including the 35 displayed, match their original field "
    "verbatim, and no card labelled 'full field' is partial. Only the label is wrong.",
    "Apply the same label transformation to the seventeen lines, or drop the excerpt/full-field distinction from "
    "every card. Quotation text needs no change.",
    "performed: all 49 card payloads matched against original decision_resolved records",
    None, [CANON, "checks/quotes.json"])

# ------------------------------------------------------------------ should fix
add("FF-C01", "should_fix", "G18 follow-up offers have no stated author, which hides that Opus bid lower",
    "sections/finance_inheritance.tex", 88,
    "Subsequent \\$150 and \\$225 offers also fail.",
    "Both are Opus's bids at G18 d454 and d455 (turn 194), six turns after the withdrawal. Sol, then holding $249, "
    "counters at $450 and $350 and later asks $300 (d461). Opus's message at d457 says 'My $225 offer stands'. "
    "Opus also unmortgages Pennsylvania at d445 (turn 190) and North Carolina at d448 (turn 192). The returned "
    "explanation quoted in the card says redeeming and building 'would cost far more than it's worth'. The record "
    "therefore shows repricing below the withdrawn figure, and the stated cost reason is not matched by later "
    "conduct. The rest of the card reproduces: $200 opening bid, $250 'final' counter, four 'offer stands' "
    "messages, two $750 payments, cash $69 then $49, and the $450 and $350 package offers.",
    "Name the bidder and the asks, and add the two redemptions. Adjust the reading so the explanation is "
    "attributed and contrasted with the later bids.",
    "performed: original G18 d419-d461 records and offer ledger",
    "FF-C01", [CANON, "data/agenda_offers.json"])

add("FF-R01", "should_fix", "The AgentMonopoly prompt claim is attached to the repository but comes from the paper",
    "sections/related_limits.tex", 7,
    "Its prompt encourages bluffing while prohibiting public messages contradicting the action.",
    "The archived engine source (qa/literature, sha256 f509b017...) contains no prompt text. It does confirm the "
    "three implementation facts: evaluate_trade allows only accept_trade and reject_trade (line 359), bankruptcy "
    "follows balance < 0 with no liquidation step (lines 220-322), and _declare_bankruptcy reassigns owner_id to "
    "the creditor without clearing buildings (lines 536-545). The bluffing rule is in the paper, Section 4 and "
    "Appendix A.2, as is elimination at negative cash. The sentence follows 'These are implementation findings', "
    "carries no citation, and so reads as a repository fact. Separately, the FinBoardBench building-sale rule in "
    "line 9 has no locator although the evidence map credits Appendix C.3.",
    "Cite the paper with section locators for the prompt and the negative-cash rule, keep the repository citation "
    "for the three implementation facts, and add the Appendix C.3 locator.",
    "performed: archived engine source read; arXiv HTML for 2610.29330v2 and 2605.27896v1 read through a fetch "
    "tool that returns extracted passages, not raw pages",
    "FF-R01", ["integrated/qa/literature/agentmonopoly_engine_2434f427.py.txt",
               "https://arxiv.org/html/2610.29330v2", "https://arxiv.org/html/2605.27896v1"])

add("FF-B01", "should_fix", "Recipient-level orderings are pooled over thread position right after the paper shows pooling matters",
    "sections/bargaining.tex", 30,
    "Sol, Gemini and Grok reject author-only offers more often than recipient-only offers and accept them less often. Opus reverses both orderings",
    "The statement is true of Table 8, which pools positions. Within position, for Sol, Gemini and Grok, the "
    "rejection ordering holds in five of six cells and fails for Sol's openings (19/41 against 3/6). The "
    "acceptance ordering holds in three of six, ties for Sol's openings (0/41, 0/6), and reverses for Gemini's "
    "later offers (4/9 against 4/12) and Grok's openings (3/61 against 0/18). 'Reverses' overstates Opus's 7/52 "
    "against 5/42. The preceding paragraph also leaves two of Table 2's four rows unused. The 'neither' row is "
    "the natural reference: 152/238 (63.9%) opening and 27/170 (15.9%) later. 'Much of this pooled contrast "
    "changes' (line 28) can be stated as a halving.",
    "Mark the recipient statement as pooled, give the within-position cells, replace 'reverses' with 'shows "
    "neither ordering', and add the 'neither' and 'both' reference rates.",
    "performed: re-tabulation of data/agenda_offers.json",
    "FF-B01", ["data/agenda_offers.json", "checks/offers.json"])

add("FF-B02", "should_fix", "Counter-content counts have an unstated denominator and an undisclosed composition",
    "sections/bargaining.tex", 56,
    "Eighty-five improve the counterer's net cash, with a median increase of \\$125.",
    "Eighty-five is out of the eighty-eight, not the 111 (where the count is 89) or the ninety-two (87). The "
    "prose predicate 'preserve the same original author's newly complete group' and the Table 4 heading 'All "
    "requested deeds retained' select the identical ninety-two counters, which the text does not say. Sol and "
    "Opus write 92 of the 111 counters and 80 of the 110; Opus writes 37 and 23 under action-only recovery. The "
    "section discloses the analogous concentration for rejection reasons but not for counters. The unchanged-"
    "bundle, more-cash form is the majority for each counterer in both rows (Sol 32/50, 36/47; Gemini 6/9, 3/5; "
    "Opus 32/42, 22/33; Grok 9/10, 20/25). All Table 4 cells reproduce: 111/92/79 and 110/87/81, with 169 "
    "non-completing counters and 59 requesting no deed.",
    "State the denominator, state that the two predicates coincide, and add the composition and per-counterer "
    "counts.",
    "performed: independent join of all 394 counters in data/agenda_offers.json",
    "FF-B02", ["data/agenda_offers.json", "checks/offers.json"])

add("FF-B03", "should_fix", "The agreed sixty-one can be itemized by configuration from retained ledgers",
    "sections/bargaining.tex", 76,
    "the agreed sixty-one are not itemized by configuration",
    "Both row-level codings are retained: data/agenda_rejection_reasons.json and "
    "paper_agenda_revision_2026-10-29/reviews/negotiation/own_74_row_ledger.json. Joining them on game and "
    "decision reproduces 63, 63, 61 common and 65 either. The 61 are Gemini 29 of 31, Grok 27 of 31, Sol 4 of 4 "
    "and Opus 1 of 8. All eight Opus rows lack a private note. By cell they are 34 of 36 both-completing and 27 "
    "of 38 recipient-only. The 74 split 4/31/8/31 and 38/36 as printed, and 34 come from G1 and G15.",
    "Replace the disclaimer with the itemization. It shows that the result describes Gemini and Grok and that "
    "more than half the agreed reasons arise where the author's monopoly is itself on offer.",
    "performed: row join of two retained coding ledgers; the codings themselves are inherited LLM-assisted labels",
    "FF-B03", ["data/agenda_rejection_reasons.json",
               "../paper_agenda_revision_2026-10-29/reviews/negotiation/own_74_row_ledger.json"])

add("FF-D02", "should_fix", "The paper says what a conflict need not mean and omits what the content named",
    "sections/development.tex", 18,
    "In a received conflict, content may request a mortgage or an invalid build rather than an already executable house purchase.",
    "In 22 of the 24 conflicting end_turn records on construction menus the content names build_houses_or_hotel "
    "(the others name propose_trade and mortgage_property). In three of the four first-window conflicts Grok "
    "mortgages deeds in the window and the content of the final decision names a build: G8 d163, one house on "
    "each orange, $300 against $472, after four mortgages raising $310; G13 d151, one house on each of two "
    "yellows, $300 against $357, after two mortgages raising $335; G12 d166, 3/2/2 pink houses, $700 against "
    "$726, after three mortgages raising $350, a plan per-entry validation would reject. G20 d97 names a "
    "mortgage. Attached notes in G8, G12 and G13 record the houses as built. Grok builds at turn 89 in G8, turn "
    "63 in G12, and never in G13. The hedge is accurate for G12 and G20 and understates G8 and G13.",
    "Describe the four windows and give the 22 of 24. Keep the statement that no content plan was executed.",
    "performed: original G8 d159-163, G12 d161-166, G13 d149-151, G20 d97-102 records; conflict ledger; build events",
    "FF-D01 (line 18 paragraph) and FF-D02 (line 20 sentence)", [CANON, EVENTS, "data/resolution_conditions.json"])

add("FF-L02", "should_fix", "The G12 note is described only by its errors although it derives the payment route",
    "sections/finance_inheritance.tex", 29,
    "The note also contains arithmetic errors.",
    "The applied private note at G12 d249 opens 'Full even liquidation cannot cover the $250', then recomputes: "
    "two Virginia houses, one each on St. Charles and States, one more, '+$50 to $293 ... pay $250, survive with "
    "$43'. That is the five-sale route and remainder of the retained witness. It then says five houses would "
    "remain when two would. The menu lists no mortgageable deed and only Virginia as sellable, consistent with "
    "the 2-2-3 holding.",
    "Say that the note reaches the witness route after an initial false statement, and name the miscount.",
    "performed: original G12 d249 record",
    "FF-L02", [CANON])

add("FF-S01", "should_fix", "A configured model-fallback stage is not disclosed, and it never ran",
    "sections/setup.tex", 36,
    "An invalid action-only response receives no further corrective request.",
    "Every Opus decision record carries response_policy claude_refusal_recovery_v1 with stages standard, "
    "same_model_without_private_thought and fallback_without_private_thought, a fallback model "
    "anthropic/claude-opus-4.8, and max_resolver_calls 3. The display name in the public records is "
    "'claude-opus-5.5 with claude-opus-4.8 fallback'. Across all 1,696 Opus decisions model_fallback_used is "
    "false, returned_model is anthropic/claude-opus-5.5, and no decision has more than two attempts. A reader of "
    "the public artifacts will see the fallback name and cannot learn from the paper that it was unused. The "
    "printed counts reproduce: 1,604 first-attempt refusals, 1,605 decisions with a refusal, 215 of 306 and "
    "1,390 of 1,390, one refusal text.",
    "Add two sentences stating the third stage and that it never ran.",
    "performed: all 20 canonical decisions.jsonl files",
    "FF-S01", [CANON, "checks/response_conditions.json"])

add("FF-S02", "should_fix", "The 139 conflicts have no stated denominator",
    "sections/setup.tex", 40,
    "Grok's selected responses contain 139 disagreements between the action named in assistant content and the received tool call.",
    "Reading every Grok decision record, I find a JSON action name in the selected attempt's content in 1,068 of "
    "1,663 decisions, and the name differs from the received call in 139 of those, the same 139 decisions as the "
    "retained ledger with none added or missing. The paper gives the 139 without saying how many records allow "
    "the comparison. My content-name pattern is simple, so the 1,068 should be confirmed with the retained parser.",
    "Give the denominator, for example '139 of the 1,068 selected responses whose content names an action'.",
    "performed: all 20 canonical decisions.jsonl files; the denominator uses a simple pattern",
    "FF-S02", [CANON, "checks/name_conflicts.json"])

add("FF-T01", "should_fix", "The 240-decision sample is undefined, counted in the wrong unit, and concentrated in Grok",
    "sections/temporal_discussion.tex", 4,
    "The fixed 240-decision sample contains fifty-nine forward-looking own-action passages, thirty-six prospective opponent-capacity or outcome passages and twenty-five references to correction or feedback, with overlap.",
    "The retained protocol defines the sample as three hash-ranked decisions per player-game from a pool the "
    "earlier public-message extractor had not flagged, sixty per configuration, and says it is not a prevalence "
    "sample. The paper never states this. The 59, 36 and 25 are sampled decisions carrying a tag, not passages. "
    "Grok supplies 39 of the 59 and 22 of the 36; Opus supplies 5 and 0. Methods line 31 also cites '614 "
    "overlapping catalog entries', a population the paper never defines.",
    "State the sampling rule and per-configuration size, use 'decisions', give Grok's share, and delete or define "
    "the 614.",
    "performed: data/agenda_temporal_rows.jsonl and the retained protocol; the tags are inherited single-reader labels",
    "FF-T01", ["data/agenda_temporal_rows.jsonl", "data/agenda_temporal.json",
               "../paper_agenda_revision_2026-10-29/temporal/protocol.md"])

add("FF-T02", "should_fix", "Feedback and configuration are fully confounded in the recurrence ledger",
    "sections/temporal_discussion.tex", 10,
    "Feedback exposure, states, targets and configurations differ, and some successors occur in the same turn.",
    "The ledger gives 9 repeats in 50 successors after delivered feedback and 54 in 59 without. All 59 successors "
    "without delivered feedback are Opus's. 'Configurations differ' is weaker than the record.",
    "State 54 of 59 and that all are Opus's.",
    "performed: data/agenda_recurrence.json",
    "FF-T02", ["data/agenda_recurrence.json"])

add("FF-W01", "should_fix", "The abstract's lead result cannot be read without the body",
    "manuscript.tex", 13,
    "The systems complete 17, 18, 15 and 13 color groups through trade, but build on 16, 17, 7 and 3 in their first management windows.",
    "The abstract never says which system each number belongs to, and 'One participant receives action-only "
    "refusal recovery' is unnamed. A reader cannot connect the recovery condition to the system that built on 7. "
    "The abstract also uses plurals for single incidents: 'financial-denial appeals' (G20 only), 'changed "
    "assurances' (G18 only) and 'selective disclosure' (G13 only).",
    "Name the four systems in order, name Opus, and use the singular for single incidents.",
    "performed: document read",
    "FF-W01", [])

# ------------------------------------------------------------------ optional
add("FF-C02", "optional", "G2 holds a same-seller, same-deed price contrast and a fuller ledger that the card omits",
    "sections/bargaining.tex", 85,
    "The residual cash calculation is correct; the construction calculation is not.",
    "At G2 d119, one turn before the card begins, Sol counters Grok's $200 bid for Marvin Gardens at $450. Grok "
    "holds no yellow and replies at d120 that '$450 is the price for the player who completes yellow'. Against "
    "Opus, Sol asks $650, then $600, and refuses $450 at d128. This is the most direct evidence in the corpus "
    "for the section's subject. The later ledger is also fuller than printed: both yellows arrive mortgaged; Sol "
    "pays $26 interest and $286 to redeem, mortgages four deeds for $410, and builds two houses for $300; after "
    "Opus's estate passes to Gemini with developed light blues, Sol pays $450 on Connecticut the next turn by "
    "selling both houses; Gemini redeems the yellows and builds six houses the turn after Sol's bankruptcy. "
    "Every figure already in the card reproduces ($845, $520, $195, $435, $17, $1,300, $300, $150, event 1566).",
    "Add one paragraph on the two asks and extend the finding. Keep the caveat that the negotiations differ.",
    "performed: original G2 d117-d129 and d197-198 records; G2 events turns 69-86",
    "FF-C02 (optional)", [CANON, EVENTS])

add("FF-C03", "optional", "G7 has a ledger follow-through that ties it to the paper's sequence",
    "sections/bargaining.tex", 122,
    "The deed transfers for \\$600. Sol's note says it prefers reinvesting to holding out for another \\$25.",
    "Grok completes green at turn 95 through a $171 auction purchase of Pennsylvania, builds nothing on it, and is "
    "the first player eliminated at turn 110 owing Sol $1,400. The estate returns North Carolina to Sol inside "
    "the complete group, and Sol builds a house on each green at turn 112. As printed the card stops at a $25 "
    "gap and has no later consequence, which is why two reviewers preferred it in the appendix.",
    "Add three sentences. With them the card supports the acquisition, development and succession sequence.",
    "performed: G7 events; data/t06_eliminations.json; group_episodes.jsonl",
    "FF-C03 (optional)", [EVENTS, "../paper_phase1_2026-10-28/sol/group_episodes.jsonl"])

add("FF-C04", "optional", "The mortgaged Pennsylvania in G13 comes from the first-window conflict the paper counts elsewhere",
    "sections/finance_inheritance.tex", 67,
    "Grok offers its mortgaged Pennsylvania to Opus for \\$200:",
    "Pennsylvania is mortgaged at G13 turn 63 (event 1082) in Grok's first management window for yellow, is never "
    "redeemed, and transfers mortgaged at turn 107. That window is one of the four received-call conflicts. "
    "Grok has no HOUSE_BUILT event in G13.",
    "Add a cross-reference paragraph. It links the development and inheritance sections through one deed.",
    "performed: G13 events and d149-151 records",
    "FF-C04 (optional)", [CANON, EVENTS])

add("FF-C05", "optional", "G19 does not say that the accepted swap completes nothing",
    "sections/bargaining.tex", 134,
    "\\TranscriptFinding{The swap and \\$150 payment execute.}",
    "The ledger cell is 'neither'. Sol's note at d136 reads 'No opponent monopoly enabled ... strictly favorable "
    "swap'. Saying so explains why acceptance needs no belief in the false premise.",
    "Add the clause and the note's phrase.",
    "performed: original G19 d135-136 records and offer ledger",
    "FF-C05 (optional)", [CANON, "data/agenda_offers.json"])

add("FF-C06", "optional", "Two small precision points in G20 and the G3 control",
    "sections/development.tex", 47,
    "Sol had already stated its own reason not to fund Grok",
    "Sol's reason is in its private note at G20 d95, one decision before the appeal, not in a public message. In "
    "Appendix D.2, Grok's quote says $58 and Gemini's next note says $43; Gemini's cash is $58 at d362 and d363 "
    "and $43 at d364, two turns later.",
    "Write 'had already recorded privately', and add a clause in D.2 that Gemini's cash fell to $43 by its next "
    "decision.",
    "performed: original G20 d95-d97 and G3 d362-364 records",
    None, [CANON])

add("FF-I01", "optional", "Route and creditor counts lack the reference figures that make them readable",
    "sections/finance_inheritance.tex", 36,
    "eighteen of sixty-three trade-completed groups belong to eventual winners",
    "One player in four wins. Trade completions are at 18/63 (29%) and auction completions at 2/9, against 12/16 "
    "for direct purchase and 45/52 for nonterminal estates. Line 55 says the creditor 'often' owns the developed "
    "property while Appendix B holds the number, 57 of 60. My event read finds 57 eliminations in which the "
    "debtor's last move ends on a color-group property and the creditor is a player. Auction-completed groups "
    "collect $3,358, a figure the routes paragraph omits. All printed route, deed and cash totals reproduce from "
    "events: 207, 397, 227, 202, $7,843, $7,148, 54 = 35 + 19, 18 and 16 games.",
    "Add the quarter reference and move the 57 into the main text.",
    "performed: all 20 events.jsonl files and group_episodes.jsonl; 'developed' in the 57 is inherited",
    "FF-I01 (optional)", [EVENTS, "../paper_phase1_2026-10-28/sol/group_episodes.jsonl",
                          "checks/estates_from_events.json"])

add("FF-B04", "optional", "Two exploratory cuts have undisclosed author or recipient composition",
    "sections/bargaining.tex", 112,
    "are accepted in 12/85 cases, against 47/407 for other recipients, and are countered more often",
    "Fifty-nine of the 85 low-cash recipients are Sol (34) or Opus (25), the two configurations that mostly "
    "counter. Within configuration the counter share rises for Sol (27/34 against 63/110) and Grok (7/12 against "
    "27/128) and is flat for Opus and Gemini. In Table 9, Opus authors 166 of the 307 bids. All printed cells "
    "reproduce: 48, $194, 57, $571, 21, 30, the four thresholds, 13, 16, 6, and all sixteen Table 9 medians.",
    "Add one clause on composition to each, or leave as is given the exploratory framing.",
    "performed: data/agenda_offers.json and contracts/data/board.json",
    None, ["data/agenda_offers.json", "contracts/data/board.json"])

add("FF-W02", "optional", "Scope disclaimers are dense and several repeat three or more times",
    "sections/bargaining.tex", 52,
    "Low acceptance does not establish absence of agreement bias.",
    "A pattern count over the abstract and main sections finds about 111 scope-limiting sentences in 537 and 52 "
    "of 97 prose paragraphs ending in one; in the bargaining section, 13 of 19. The count is a regex estimate. "
    "Repeated propositions include: no effect of completion (Table 2 caption, lines 28 and 30, limitations); no "
    "utility reference (line 52, related work, limitations, Table 6); board price (line 74, Table 9 caption, "
    "Appendix A.1 twice); cash and distress (lines 110 and 112 three times, Appendix A); winner conditioning "
    "(finance lines 36 and 55, Table 5 caption, limitations); no-option scope (methods, Figure 1 caption, "
    "development twice, Appendix B.1 three times); no general audit method (introduction, discussion, related "
    "work).",
    "Keep each caveat once in text and once in the limitations. Candidate deletions are listed in review.md.",
    "performed: document-only count (tools/count_hedges.py); judgments of redundancy are mine",
    "FF-W02 (optional compressions)", ["checks/hedges.json"])

add("FF-W03", "optional", "Internal process vocabulary appears in the scientific text",
    "sections/methods.tex", 25,
    "This rewrite re-tabulates their retained results; it does not execute new game continuations.",
    "'This rewrite' or 'the rewrite' appears in methods lines 25 and 33, limitations line 23, and appendix lines "
    "146, 189 and 191. A reader has no referent for it. The statement that no games were added appears four "
    "times (methods, limitations, Appendix B.1, Appendix C).",
    "Write 'this paper' in the body and keep the process account in Appendix E.",
    "performed: document read",
    None, [])

add("FF-W04", "optional", "Two floats interrupt the text they belong to",
    "sections/finance_inheritance.tex", 8,
    "\\begin{figure}[t]",
    "Figure 2 lands on page 14 between Transcript 5's 'What happened' and 'What this shows'. Table 4 lands on "
    "page 7 above the last paragraph of Section 4.1 and before the heading of the subsection that discusses it. "
    "Pages 8, 10 and 16 end with roughly a third blank, and pages 24 and 33 are mostly blank. No text, table or "
    "card is clipped on any of the 33 pages.",
    "Add a float barrier after the G20 source line and before the Section 4.2 heading, or relax the two "
    "placements.",
    "performed: all 33 pages of the pinned PDF rendered and viewed",
    None, ["render/page_07.png", "render/page_14.png"])

add("FF-P01", "optional", "Six exhibit inputs sit outside the 38-file pin",
    "manuscript.tex", 27,
    "\\input{sections/appendix}",
    "integrated/data holds nine JSON files that are not in qa/integrated_file_hashes.json. Three quote manifests "
    "are covered by source_manifest.json. The other six (agenda_offers, first_management_windows, t01_cohort, "
    "t03_trade_groups, t06_eliminations, t09_entry_nonbuild_records) feed build_exhibits.py and the check "
    "scripts. Each is byte-identical to its parent data/ copy today. Their hashes are recorded in "
    "verification.md.",
    "Add the nine data files to the hash manifest.",
    "performed: hashes computed and compared",
    None, ["integrated/qa/integrated_file_hashes.json", "integrated/source_manifest.json"])

add("FF-R02", "optional", "One Arena detail was not confirmed at abstract level, and one FinBoardBench figure is available",
    "sections/related_limits.tex", 5,
    "studies promise follow-through",
    "The arXiv abstract page for 2608.14825v3 confirms 2,583 emails, twenty one-year runs, use of simulator "
    "ground truth and replication with judges from two other model families. It does not mention promise "
    "follow-through, which rests on Sol's earlier section read. FinBoardBench Section 3.2 reports that 33.3% of "
    "negotiation decisions choose counter; here 394 of 920 responses are counters, from 36/242 for Gemini to "
    "141/189 for Opus.",
    "No change required. The 33.3% figure could be set beside this cohort's counter shares in one sentence.",
    "performed at abstract level only for Arena; FinBoardBench and DECE passages as extracted by the fetch tool",
    None, ["https://arxiv.org/abs/2608.14825v3", "https://arxiv.org/html/2605.27896v1",
           "https://arxiv.org/abs/2610.35773v1"])

if MISSES:
    for m in MISSES:
        print("MISS", m)
    raise SystemExit(1)
order = {"blocking": 0, "should_fix": 1, "optional": 2}
F.sort(key=lambda f: order[f["severity"]])
out = {
    "reviewer": "Fable 5.2 xhigh",
    "review": "fresh whole-paper review of the integrated manuscript",
    "pinned_pdf_sha256": PIN,
    "scope": "Existing-file re-tabulation, original source reads, primary literature reads and document-only "
             "builds. No game, engine execution, replay, branch, synthetic test, reference policy or model "
             "evaluation query.",
    "severity_scale": {
        "blocking": "A statement that is false or contradicts another statement as worded. Each has a wording fix "
                    "and changes no count.",
        "should_fix": "Accurate but incomplete or ambiguous in a way that changes what a reader concludes.",
        "optional": "Strengthening, style or process preference."},
    "counts": {s: sum(f["severity"] == s for f in F) for s in order},
    "findings": F,
}
out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps(out["counts"]), len(F))
