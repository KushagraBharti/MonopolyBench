"""Author coding of the sixteen first responses in the necessary-collateral episodes.

This is a model-assisted reading by one LLM author with the full stored fields in hand.
It is not human annotation. Every evidence span below is asserted to occur verbatim in
the named stored channel by 07_tables.py, so a reader can check each label against text.

Tiers (first that applies, over every available channel of the first response)
  explicit   a channel says that selling or clearing buildings enables, unlocks, allows
             or must precede mortgaging deeds of that color group
  ordered    no such statement, but a channel gives a sequence in which a building sale
             comes before a named mortgage of a deed in the same group
  inclusive  neither of the above, but a stated total or itemisation includes the mortgage
             value of deeds in a developed group
  tentative  the released mortgages are raised as a possibility without being counted
  omission   no available channel mentions the mortgage value of developed-group deeds and
             the stated maximum excludes it
"""

TIER_LABEL = {
    "explicit": "Explicit dependency",
    "ordered": "Ordered route",
    "inclusive": "Inclusive budget",
    "tentative": "Tentative resource",
    "omission": "Omission",
}
TIER_ORDER = ["explicit", "ordered", "inclusive", "tentative", "omission"]

# (game, first decision): tier, evidence channel, evidence span, figures, route remark
CODING = {
    (1, 476): dict(
        tier="explicit", channel="note", span="Must sell before yellows can be mortgaged.",
        figures="Values correct ($75, $130, $140). No total stated.",
        other="The provider field gives a garbled reason for the rule (\"requires even distribution of houses\").",
        route="As stated: one house sold, one yellow mortgaged."),
    (2, 216): dict(
        tier="explicit", channel="note", span="Clearing buildings unlocks yellow mortgages worth $430",
        figures="One value wrong: the three yellow mortgages total $400, not $430. Shortfall figures correct.",
        other="The provider field is confused (\"selling two houses yielding $150 each\").",
        route="As stated: both houses sold, Marvin Gardens and one other yellow mortgaged."),
    (4, 270): dict(
        tier="ordered", channel="note", span="sell my 4 houses on Yellow ($300 total) and then mortgage two Yellow properties to cover the remaining $174 shortfall",
        figures="Correct. The provider field values the three yellow mortgages at $400, also correct.",
        other="",
        route="As stated. The listed $30 Mediterranean mortgage was left unused."),
    (4, 308): dict(
        tier="inclusive", channel="provider", span="Selling back my 7 houses at half price gets 525, and mortgaging the three red properties adds 340, totaling 910",
        figures="Total equals the full bound ($910). Stated maximum remainder $110 is correct.",
        other="Says selling \"has to happen incrementally\"; the validator accepts bundles and the second call sold six houses.",
        route="Two of the three red mortgages sufficed; paid with $0 left."),
    (5, 263): dict(
        tier="explicit", channel="note", span="unlock the ability to mortgage Park Place ($175) and Boardwalk ($200)",
        figures="Total equals the full bound ($1,049). Stated remainder $149 met exactly.",
        other="The provider field first counts house sales only, then revises to add the two mortgages.",
        route="As stated."),
    (6, 185): dict(
        tier="inclusive", channel="provider", span="plus mortgaging Boardwalk for $200 and those three properties for another $220, gives me access to $770 total",
        figures="$770 of proceeds and a $208 maximum remainder both equal the full bound.",
        other="States a first step (\"mortgage Boardwalk first, then work through selling houses\").",
        route="First step as stated; one of three pink mortgages sufficed, two deeds left unmortgaged."),
    (8, 257): dict(
        tier="explicit", channel="note", span="which will also unlock Park Place and Boardwalk for mortgaging",
        figures="Shortfalls correct ($317, then $217). Mortgages not valued, no total.",
        other="The provider field stops at the house and the listed Baltic mortgage (\"I need to make a more holistic plan\").",
        route="House sold, Boardwalk and Baltic mortgaged; Park Place left unmortgaged."),
    (11, 203): dict(
        tier="inclusive", channel="provider", span="Adding the remaining mortgages on St James, Tennessee, and New York ($90+$90+$100) brings the total to $556",
        figures="States the listed-only total ($276) and then the full bound ($556). Stated remainder $56 met exactly.",
        other="",
        route="As stated; every resource used."),
    (12, 190): dict(
        tier="omission", channel="note", span="maximum liquidity is $408, below $500 owed. No legal liquidation can save me.",
        figures="Arithmetic correct for what is counted. $408 equals the listed-only total; $340 of red mortgages is absent.",
        other="The provider field repeats the sum and adds that bankruptcy \"might transfer property anyway\".",
        route="Declared at the first menu."),
    (13, 195): dict(
        tier="ordered", channel="note", span="I must sell the house on Boardwalk ($100) and mortgage Park Place ($175) plus $335 in non-Dark-Blue properties, keeping Boardwalk and Kentucky Avenue unmortgaged",
        figures="Correct. The plan implies $28 left, which is what remained.",
        other="The provider field prints \"$44\" where the listed total is $445, then reaches the same plan.",
        route="Exactly as stated, deed for deed."),
    (17, 234): dict(
        tier="omission", channel="note", span="my total liquidatable value is only $530 (5 Dark Blue houses at $100 each plus $30 for mortgaging Baltic Avenue)",
        figures="Arithmetic correct for what is counted. $530 equals the listed-only total; $375 of dark-blue mortgages is absent.",
        other="The provider field counts the $500 and ends \"I will have to start thinking of additional options\".",
        route="Declared at the first menu."),
    (17, 254): dict(
        tier="inclusive", channel="provider", span="mortgaging those three properties adds $110+$110+$120=$340, totaling $843",
        figures="Total equals the full bound ($843).",
        other="Says five houses cannot be sold in one call; a five-house bundle ends even and would pass the validator.",
        route="Two sale calls and one of three red mortgages; $63 left."),
    (18, 309): dict(
        tier="explicit", channel="note", span="which will allow me to mortgage St. Charles Place ($70) on the next step to cover the remaining $38 shortfall",
        figures="Correct ($412 after sales, $38 short, $70 mortgage). Implied remainder $32 met.",
        other="The provider field covers the sale only. The applied bundle sold St. Charles houses that the menu did not list.",
        route="As stated."),
    (18, 313): dict(
        tier="ordered", channel="note", span="Selling all 5 houses yields only $500, so I still need to mortgage PP or BW afterward",
        figures="Correct ($500, about $49 short). The provider field gives the full-liquidation remainder ($326) correctly, among several reversed or wrong figures.",
        other="Request context showed another player's sale and mortgage one turn earlier.",
        route="Three sale calls, then Park Place mortgaged; $126 left."),
    (20, 291): dict(
        tier="tentative", channel="provider", span="I'm checking whether mortgaging the pink lots themselves after clearing the houses could close the gap",
        figures="Accounting confused: \"$725 short even after\" restates the initial shortfall, and $680 of proceeds is compared with the whole $1,000 debt without the $275 held. The true gap after those proceeds is $45.",
        other="",
        route="Nine houses sold, two listed mortgages, one released pink mortgage; $25 left."),
    (20, 327): dict(
        tier="inclusive", channel="note", span="Full liquidation should yield $1,414 including cash and all mortgages, enough for $1,400 rent by $14",
        figures="Total equals the full bound ($1,414). Stated remainder $14 met exactly.",
        other="The provider field itemises the released orange ($280) and brown ($60) mortgages; a second paragraph about a hotel sale is confused.",
        route="Everything liquidated in ten calls. The debt is $14 below the bound, so no other end state pays."),
}

# Author reading of the ten notes carried into each of the sixteen first requests.
# kind: conditional = a resource figure that was correct for the condition under which it
# was written (buildings standing) and excludes what a sale would release.
CARRIED = {
    (1, 476): ("rule", "yellows cannot be mortgaged while it stands", "States the rule; a later note lists \"yellow mortgages ~$400 as reserve\"."),
    (2, 216): ("none", "all spare collateral already mortgaged", "No figure for the yellow deeds."),
    (4, 270): ("none", "which covers the $209 shortfall without needing to mortgage Mediterranean Avenue", "An earlier payment by house sales."),
    (4, 308): ("none", "", "Ten notes from turns 62 to 65 about a purchase, 81 turns old."),
    (5, 263): ("conditional", "my total liquidatable cash + houses is $774 < $900", "A salvage-only comparison at turn 141; the response revises it."),
    (6, 185): ("empty", "", "No carried notes."),
    (8, 257): ("none", "so I must sell 1 house on Park Place for $100", "An earlier payment by a house sale."),
    (11, 203): ("empty", "", "No carried notes."),
    (12, 190): ("conditional", "$53 cash plus $130 mortgage capacity", "\"$130\" emergency or spare mortgage capacity in six notes, turns 57 to 73."),
    (13, 195): ("conditional", "$445 in mortgageable non-Dark-Blue properties", "\"$445\" in three notes at turn 75."),
    (17, 234): ("conditional", "Keeping Baltic Avenue unmortgaged as a $30 emergency reserve", "\"$30 emergency reserve\" once, turn 68."),
    (17, 254): ("empty", "", "No carried notes."),
    (18, 309): ("rule", "p3 must sell all 5 Dark Blue houses and mortgage a Dark Blue property", "Applies the sale-then-mortgage sequence to a rival."),
    (18, 313): ("conditional", "only roll 4 (Virginia $700) is unpaid even after selling all 5 houses ($500)", "A salvage-only maximum at turn 90."),
    (20, 291): ("empty", "", "No carried notes."),
    (20, 327): ("conditional", "$325 idle mortgage capacity", "\"$325 idle mortgage capacity\" in three notes, turns 102 to 104."),
}
