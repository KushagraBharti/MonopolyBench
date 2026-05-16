# Micro-v1 Research Backlog

- source_url: https://arxiv.org/abs/2103.00683
  source_type: strategy/research
  claim: Hybrid Monopoly agents combine learned decisions with fixed policies for less frequent buy/trade decisions.

- source_url: https://en.wikibooks.org/wiki/Monopoly/Strategy
  source_type: strategy/research
  claim: Jail traffic raises orange value; railroads are frequent enough to matter; house shortages and hotel conversion affect development strategy.

- source_url: https://www.wargamer.com/monopoly/how-to-win-monopoly
  source_type: strategy/research
  claim: Early jail slows acquisition; late-game jail can be protective; utilities are often weak.

- source_url: https://ultraboardgames.com/monopoly/strategy.php
  source_type: strategy/research
  claim: Cash reserves should be preserved when developed opponent monopolies exist.

- source_url: https://sanghyun-kim.com/monopoly-analysis
  source_type: strategy/research
  claim: Markov-chain analysis highlights orange traffic and Illinois Avenue as high-probability property decisions.

- source_url: https://instructions.hasbro.com/en-hk/instruction/monopoly-standard-monopoly
  source_type: strategy/research
  claim: Official component limits include 32 houses and 12 hotels; auctions, trading, houses, hotels, mortgages, and jail are rule-governed.

- source_url: https://www.hasbro.com/common/instruct/Monopoly.pdf
  source_type: strategy/research
  claim: Jail can result from cards, Go To Jail, or three doubles; the Bank holds deeds, houses, and hotels before purchase.

- source_url: https://www.monopolyland.com/monopoly-rules/
  source_type: strategy/research
  claim: Declined property goes to auction; jail options are pay, card, or roll; scarce houses/hotels are auctioned.

- source_url: https://www.monopolyland.com/monopoly-auction-rules/
  source_type: strategy/research
  claim: Auction bids can start at any amount, but cash limits and opponent needs should shape bidding strategy.

- source_url: https://www.monopolyland.com/monopoly-statistics-that-will-help-you-win/
  source_type: strategy/research
  claim: Jail is the most landed space; Illinois Avenue and New York Avenue are high-probability properties.

- source_url: https://www.soa.org/news-and-publications/newsletters/compact/2012/april/actuarial-monopoly.aspx
  source_type: strategy/research
  claim: Probability modeling explains why orange and red squares receive elevated traffic from Jail.

- source_url: https://www.normalesup.org/~stephens/MAS275/monopoly.pdf
  source_type: strategy/research
  claim: Jail is highly probable and Illinois Avenue is a high-probability property; orange/red groups are relatively high traffic.

- source_url: https://quatizer.com/strateg.html
  source_type: strategy/research
  claim: Strategic play prioritizes efficient monopolies, development timing, and avoiding cash starvation.

- source_url: https://www.playiro.com/articles/when-to-build-houses-vs-hotels-in-monopoly-the-ultimate-strategy-guide
  source_type: strategy/research
  claim: Hotels can be a trap when holding houses constrains opponent development.

- source_url: https://www.reddit.com/r/monopoly/comments/m41qj2
  source_type: strategy/research
  claim: Experienced players discuss using scarce houses and avoiding hotel conversion to limit opponents.

## buy-or-auction-vermont-light-blue-tempo-01
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-vermont-light-blue-tempo-01
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly/Strategy - Wikibooks, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: easy

## buy-or-auction-connecticut-light-blue-low-buffer-02
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-connecticut-light-blue-low-buffer-02
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly Strategy - Quatizer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: medium

## buy-or-auction-new-york-orange-high-traffic-03
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-new-york-orange-high-traffic-03
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly Statistics That Will Help You Win, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: medium

## buy-or-auction-illinois-red-completion-04
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-illinois-red-completion-04
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly Analysis - SangHyun Kim, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, public, thought
difficulty: medium

## buy-or-auction-electric-company-cash-danger-05
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-electric-company-cash-danger-05
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: start_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## buy-or-auction-water-works-no-utility-synergy-06
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-water-works-no-utility-synergy-06
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: start_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: medium

## buy-or-auction-reading-first-railroad-07
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-reading-first-railroad-07
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: easy

## buy-or-auction-pennsylvania-second-railroad-08
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-pennsylvania-second-railroad-08
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, public, thought
difficulty: easy

## buy-or-auction-bo-railroad-cash-rich-opponent-09
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-bo-railroad-cash-rich-opponent-09
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Auction Rules Explained
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: medium

## buy-or-auction-short-line-third-railroad-low-cash-10
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-short-line-third-railroad-low-cash-10
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: start_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## buy-or-auction-kentucky-blocks-beta-red-11
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-kentucky-blocks-beta-red-11
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly Analysis - SangHyun Kim, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: medium

## buy-or-auction-tennessee-blocks-orange-12
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-tennessee-blocks-orange-12
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, public, thought
difficulty: medium

## buy-or-auction-st-charles-low-cost-open-13
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-st-charles-low-cost-open-13
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: easy

## buy-or-auction-oriental-cheap-builder-14
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-oriental-cheap-builder-14
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: easy

## buy-or-auction-boardwalk-fame-bias-low-cash-15
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-boardwalk-fame-bias-low-cash-15
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: start_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## buy-or-auction-park-place-no-boardwalk-16
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-park-place-no-boardwalk-16
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: start_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, public, thought
difficulty: hard

## buy-or-auction-st-james-orange-deny-leader-17
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-st-james-orange-deny-leader-17
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly Auction Rules Explained
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: medium

## buy-or-auction-virginia-pink-with-trade-path-18
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-virginia-pink-with-trade-path-18
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Monopoly Strategy - Quatizer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: medium

## buy-or-auction-mediterranean-cheap-but-blocking-19
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-mediterranean-cheap-but-blocking-19
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: buy_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, acceptable_branch, cash, thought
difficulty: easy

## buy-or-auction-north-carolina-green-caution-20
category: BUY_OR_AUCTION
scenario_slug: buy-or-auction-north-carolina-green-caution-20
strategic_tension: Purchase timing, monopoly/blocking value, and liquidity.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: buy_property, start_auction
preferred_action: start_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, public, thought
difficulty: hard

## auction-illinois-min-raise-red-completion-01
category: AUCTION
scenario_slug: auction-illinois-min-raise-red-completion-01
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Analysis - SangHyun Kim, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: medium

## auction-new-york-orange-completion-02
category: AUCTION
scenario_slug: auction-new-york-orange-completion-02
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Statistics That Will Help You Win, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: medium

## auction-tennessee-cheap-steal-03
category: AUCTION
scenario_slug: auction-tennessee-cheap-steal-03
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly Auction Rules Explained
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: easy

## auction-st-james-defensive-block-04
category: AUCTION
scenario_slug: auction-st-james-defensive-block-04
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Auction Rules Explained
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: hard

## auction-boardwalk-overbid-drop-05
category: AUCTION
scenario_slug: auction-boardwalk-overbid-drop-05
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## auction-park-place-no-pair-drop-06
category: AUCTION
scenario_slug: auction-park-place-no-pair-drop-06
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## auction-electric-company-utility-overpay-07
category: AUCTION
scenario_slug: auction-electric-company-utility-overpay-07
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly Auction Rules Explained
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: medium

## auction-water-works-second-utility-cap-08
category: AUCTION
scenario_slug: auction-water-works-second-utility-cap-08
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, discipline, thought
difficulty: medium

## auction-reading-railroad-low-price-09
category: AUCTION
scenario_slug: auction-reading-railroad-low-price-09
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Auction Rules Explained
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: easy

## auction-bo-railroad-third-railroad-10
category: AUCTION
scenario_slug: auction-bo-railroad-third-railroad-10
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, public, thought
difficulty: medium

## auction-kentucky-block-red-11
category: AUCTION
scenario_slug: auction-kentucky-block-red-11
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Analysis - SangHyun Kim, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: medium

## auction-indiana-leader-threat-12
category: AUCTION
scenario_slug: auction-indiana-leader-threat-12
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Auction Rules Explained, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, discipline, thought
difficulty: hard

## auction-virginia-pink-midgame-13
category: AUCTION
scenario_slug: auction-virginia-pink-midgame-13
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Strategy - Quatizer, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: medium

## auction-pacific-green-too-expensive-14
category: AUCTION
scenario_slug: auction-pacific-green-too-expensive-14
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## auction-oriental-light-blue-cheap-block-15
category: AUCTION
scenario_slug: auction-oriental-light-blue-cheap-block-15
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, public, thought
difficulty: easy

## auction-mediterranean-brown-ignore-war-16
category: AUCTION
scenario_slug: auction-mediterranean-brown-ignore-war-16
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, discipline, thought
difficulty: medium

## auction-pennsylvania-railroad-force-price-17
category: AUCTION
scenario_slug: auction-pennsylvania-railroad-force-price-17
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Auction Rules Explained, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: medium

## auction-short-line-cash-leader-trap-18
category: AUCTION
scenario_slug: auction-short-line-cash-leader-trap-18
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Monopoly Auction Rules Explained, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## auction-states-avenue-positive-but-not-critical-19
category: AUCTION
scenario_slug: auction-states-avenue-positive-but-not-critical-19
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: bid_auction
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, minimum, cap, thought
difficulty: easy

## auction-marvin-gardens-yellow-overstretch-20
category: AUCTION
scenario_slug: auction-marvin-gardens-yellow-overstretch-20
strategic_tension: Auction value, blocking pressure, and bid discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: bid_auction, drop_out
preferred_action: drop_out
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, discipline, thought
difficulty: hard

## trade-propose-water-works-for-new-york-01
category: TRADE_PROPOSE
scenario_slug: trade-propose-water-works-for-new-york-01
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly Statistics That Will Help You Win, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-reading-for-tennessee-02
category: TRADE_PROPOSE
scenario_slug: trade-propose-reading-for-tennessee-02
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly/Strategy - Wikibooks, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-jail-card-for-st-james-03
category: TRADE_PROPOSE
scenario_slug: trade-propose-jail-card-for-st-james-03
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, card, cash, thought, discipline
difficulty: hard

## trade-propose-red-indiana-for-kentucky-04
category: TRADE_PROPOSE
scenario_slug: trade-propose-red-indiana-for-kentucky-04
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly Analysis - SangHyun Kim, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-red-block-with-railroad-05
category: TRADE_PROPOSE
scenario_slug: trade-propose-red-block-with-railroad-05
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly/Strategy - Wikibooks, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-mutual-orange-vs-yellow-06
category: TRADE_PROPOSE
scenario_slug: trade-propose-mutual-orange-vs-yellow-06
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Actuarial Monopoly - Society of Actuaries, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: hard

## trade-propose-mutual-red-vs-green-07
category: TRADE_PROPOSE
scenario_slug: trade-propose-mutual-red-vs-green-07
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Analysis - SangHyun Kim
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: hard

## trade-propose-no-good-trade-boardwalk-08
category: TRADE_PROPOSE
scenario_slug: trade-propose-no-good-trade-boardwalk-08
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: hard

## trade-propose-cash-poor-beta-orange-09
category: TRADE_PROPOSE
scenario_slug: trade-propose-cash-poor-beta-orange-09
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-cash-poor-gamma-red-10
category: TRADE_PROPOSE
scenario_slug: trade-propose-cash-poor-gamma-red-10
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly Analysis - SangHyun Kim, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-railroad-swap-for-light-blue-11
category: TRADE_PROPOSE
scenario_slug: trade-propose-railroad-swap-for-light-blue-11
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly/Strategy - Wikibooks, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: easy

## trade-propose-jail-card-late-safety-for-red-12
category: TRADE_PROPOSE
scenario_slug: trade-propose-jail-card-late-safety-for-red-12
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly rules and how to win - Wargamer, MONOPOLY Parker Brothers Real Estate Trading Game Rules
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, card, cash, thought, discipline
difficulty: hard

## trade-propose-defensive-deny-green-13
category: TRADE_PROPOSE
scenario_slug: trade-propose-defensive-deny-green-13
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: hard

## trade-propose-utility-package-for-railroad-14
category: TRADE_PROPOSE
scenario_slug: trade-propose-utility-package-for-railroad-14
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-politically-risky-leader-message-15
category: TRADE_PROPOSE
scenario_slug: trade-propose-politically-risky-leader-message-15
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly Auction Rules Explained, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, public, discipline
difficulty: hard

## trade-propose-dark-blue-fame-trap-16
category: TRADE_PROPOSE
scenario_slug: trade-propose-dark-blue-fame-trap-16
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: hard

## trade-propose-yellow-build-race-17
category: TRADE_PROPOSE
scenario_slug: trade-propose-yellow-build-race-17
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: medium

## trade-propose-pink-cheap-development-18
category: TRADE_PROPOSE
scenario_slug: trade-propose-pink-cheap-development-18
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: easy

## trade-propose-brown-fast-build-19
category: TRADE_PROPOSE
scenario_slug: trade-propose-brown-fast-build-19
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Monopoly Strategy - Quatizer, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, thought, discipline
difficulty: easy

## trade-propose-orange-no-reveal-public-20
category: TRADE_PROPOSE
scenario_slug: trade-propose-orange-no-reveal-public-20
strategic_tension: Trade structure, plausibility, and private/public message discipline.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: propose_trade
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: target, request, offer_asset, cash, public, discipline
difficulty: hard

## trade-response-accept-orange-for-utility-01
category: TRADE_RESPONSE
scenario_slug: trade-response-accept-orange-for-utility-01
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Monopoly Statistics That Will Help You Win, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: accept_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, safe_branch, thought, message_ok
difficulty: easy

## trade-response-accept-red-with-cash-02
category: TRADE_RESPONSE
scenario_slug: trade-response-accept-red-with-cash-02
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Monopoly Analysis - SangHyun Kim, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: accept_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, safe_branch, thought, message_ok
difficulty: medium

## trade-response-accept-liquidity-saving-03
category: TRADE_RESPONSE
scenario_slug: trade-response-accept-liquidity-saving-03
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: accept_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, safe_branch, thought, message_ok
difficulty: medium

## trade-response-reject-beta-orange-04
category: TRADE_RESPONSE
scenario_slug: trade-response-reject-beta-orange-04
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Actuarial Monopoly - Society of Actuaries, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: reject_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, reject_branch, thought, no_public_needed
difficulty: hard

## trade-response-reject-leader-red-05
category: TRADE_RESPONSE
scenario_slug: trade-response-reject-leader-red-05
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Monopoly Analysis - SangHyun Kim, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: reject_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, reject_branch, thought, no_public_needed
difficulty: hard

## trade-response-reject-boardwalk-bait-06
category: TRADE_RESPONSE
scenario_slug: trade-response-reject-boardwalk-bait-06
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: reject_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, reject_branch, thought, no_public_needed
difficulty: hard

## trade-response-counter-mutual-monopoly-cash-07
category: TRADE_RESPONSE
scenario_slug: trade-response-counter-mutual-monopoly-cash-07
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: counter_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, counter_request, counter_cash, public
difficulty: hard

## trade-response-counter-jail-card-value-08
category: TRADE_RESPONSE
scenario_slug: trade-response-counter-jail-card-value-08
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Monopoly rules and how to win - Wargamer, MONOPOLY Parker Brothers Real Estate Trading Game Rules
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: counter_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, counter_request, counter_cash, public
difficulty: hard

## trade-response-reject-face-value-positive-09
category: TRADE_RESPONSE
scenario_slug: trade-response-reject-face-value-positive-09
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: reject_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, reject_branch, thought, no_public_needed
difficulty: hard

## trade-response-accept-pink-build-window-10
category: TRADE_RESPONSE
scenario_slug: trade-response-accept-pink-build-window-10
strategic_tension: Trade response under asymmetric monopoly value.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: accept_trade, reject_trade, counter_trade
preferred_action: accept_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, safe_branch, thought, message_ok
difficulty: medium

## build-orange-third-house-st-james-01
category: BUILD_OR_MORTGAGE
scenario_slug: build-orange-third-house-st-james-01
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Actuarial Monopoly - Society of Actuaries, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: medium

## build-orange-third-house-tennessee-02
category: BUILD_OR_MORTGAGE
scenario_slug: build-orange-third-house-tennessee-02
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Statistics That Will Help You Win, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: medium

## build-orange-third-house-new-york-03
category: BUILD_OR_MORTGAGE
scenario_slug: build-orange-third-house-new-york-03
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Statistics That Will Help You Win, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: easy

## build-orange-mortgage-utility-to-build-04
category: BUILD_OR_MORTGAGE
scenario_slug: build-orange-mortgage-utility-to-build-04
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, mortgage, thought
difficulty: hard

## build-red-third-house-kentucky-05
category: BUILD_OR_MORTGAGE
scenario_slug: build-red-third-house-kentucky-05
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Analysis - SangHyun Kim, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: medium

## build-red-third-house-illinois-06
category: BUILD_OR_MORTGAGE
scenario_slug: build-red-third-house-illinois-06
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Analysis - SangHyun Kim, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: medium

## build-red-cash-caution-end-07
category: BUILD_OR_MORTGAGE
scenario_slug: build-red-cash-caution-end-07
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## build-light-blue-cheap-tempo-08
category: BUILD_OR_MORTGAGE
scenario_slug: build-light-blue-cheap-tempo-08
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: easy

## build-light-blue-last-cheap-house-09
category: BUILD_OR_MORTGAGE
scenario_slug: build-light-blue-last-cheap-house-09
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Standard Game Instructions - Hasbro, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: medium

## build-yellow-expensive-caution-10
category: BUILD_OR_MORTGAGE
scenario_slug: build-yellow-expensive-caution-10
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## build-green-expensive-caution-11
category: BUILD_OR_MORTGAGE
scenario_slug: build-green-expensive-caution-11
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## build-house-shortage-hold-four-12
category: BUILD_OR_MORTGAGE
scenario_slug: build-house-shortage-hold-four-12
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: When To Build Houses vs Hotels In Monopoly, Monopoly house shortage strategy discussion
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## build-house-shortage-avoid-hotel-red-13
category: BUILD_OR_MORTGAGE
scenario_slug: build-house-shortage-avoid-hotel-red-13
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Standard Game Instructions - Hasbro, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## build-last-houses-orange-14
category: BUILD_OR_MORTGAGE
scenario_slug: build-last-houses-orange-14
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly Standard Game Instructions - Hasbro, When To Build Houses vs Hotels In Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: hard

## build-mortgage-railroad-for-red-15
category: BUILD_OR_MORTGAGE
scenario_slug: build-mortgage-railroad-for-red-15
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly/Strategy - Wikibooks, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, mortgage, thought
difficulty: medium

## build-mortgage-utility-for-light-blue-16
category: BUILD_OR_MORTGAGE
scenario_slug: build-mortgage-utility-for-light-blue-16
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, mortgage, thought
difficulty: medium

## build-preserve-cash-vs-boardwalk-17
category: BUILD_OR_MORTGAGE
scenario_slug: build-preserve-cash-vs-boardwalk-17
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## build-opponent-position-orange-now-18
category: BUILD_OR_MORTGAGE
scenario_slug: build-opponent-position-orange-now-18
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: medium

## build-pink-cheap-two-houses-19
category: BUILD_OR_MORTGAGE
scenario_slug: build-pink-cheap-two-houses-19
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, group, count, thought
difficulty: easy

## build-dark-blue-hotel-fame-trap-20
category: BUILD_OR_MORTGAGE
scenario_slug: build-dark-blue-hotel-fame-trap-20
strategic_tension: Development timing, cash reserve, and house-supply constraints.
source_claims: When To Build Houses vs Hotels In Monopoly, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: build_houses_or_hotel, mortgage_property, end_turn
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## liquidation-mortgage-electric-before-orange-01
category: LIQUIDATION
scenario_slug: liquidation-mortgage-electric-before-orange-01
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, asset, thought
difficulty: medium

## liquidation-mortgage-reading-before-red-02
category: LIQUIDATION
scenario_slug: liquidation-mortgage-reading-before-red-02
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly/Strategy - Wikibooks, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, asset, safe_branch, thought
difficulty: medium

## liquidation-mortgage-water-works-bank-debt-03
category: LIQUIDATION
scenario_slug: liquidation-mortgage-water-works-bank-debt-03
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly Standard Game Instructions - Hasbro, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, asset, thought
difficulty: easy

## liquidation-sell-one-orange-evenly-04
category: LIQUIDATION
scenario_slug: liquidation-sell-one-orange-evenly-04
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly Standard Game Instructions - Hasbro, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: sell_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, sell_branch, not_bankrupt, thought
difficulty: hard

## liquidation-sell-red-house-not-core-railroad-05
category: LIQUIDATION
scenario_slug: liquidation-sell-red-house-not-core-railroad-05
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: MONOPOLY Parker Brothers Real Estate Trading Game Rules, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: sell_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, sell_branch, not_bankrupt, thought
difficulty: hard

## liquidation-bankruptcy-unavoidable-bank-06
category: LIQUIDATION
scenario_slug: liquidation-bankruptcy-unavoidable-bank-06
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly Standard Game Instructions - Hasbro, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: declare_bankruptcy
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, bankruptcy, thought
difficulty: hard

## liquidation-bankruptcy-unavoidable-player-07
category: LIQUIDATION
scenario_slug: liquidation-bankruptcy-unavoidable-player-07
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: MONOPOLY Parker Brothers Real Estate Trading Game Rules, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: declare_bankruptcy
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, bankruptcy, thought
difficulty: hard

## liquidation-mortgaged-interest-edge-08
category: LIQUIDATION
scenario_slug: liquidation-mortgaged-interest-edge-08
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly Standard Game Instructions - Hasbro, Monopoly/Strategy - Wikibooks
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, asset, safe_branch, thought
difficulty: medium

## liquidation-preserve-monopoly-survival-09
category: LIQUIDATION
scenario_slug: liquidation-preserve-monopoly-survival-09
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, asset, thought
difficulty: medium

## liquidation-sell-hotel-house-shortage-10
category: LIQUIDATION
scenario_slug: liquidation-sell-hotel-house-shortage-10
strategic_tension: Debt payment, legal liquidation order, and asset preservation.
source_claims: Monopoly Standard Game Instructions - Hasbro, When To Build Houses vs Hotels In Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: mortgage_property, sell_houses_or_hotel, declare_bankruptcy
preferred_action: sell_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, sell_branch, not_bankrupt, thought
difficulty: hard

## jail-early-pay-undeveloped-board-01
category: JAIL
scenario_slug: jail-early-pay-undeveloped-board-01
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly rules and how to win - Wargamer, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: pay_jail_fine
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, tempo, thought
difficulty: easy

## jail-early-pay-many-unowned-02
category: JAIL
scenario_slug: jail-early-pay-many-unowned-02
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly rules and how to win - Wargamer, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: pay_jail_fine
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, tempo, thought
difficulty: easy

## jail-early-use-card-tempo-03
category: JAIL
scenario_slug: jail-early-use-card-tempo-03
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: MONOPOLY Parker Brothers Real Estate Trading Game Rules, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, use_get_out_of_jail_card, roll_for_doubles
preferred_action: use_get_out_of_jail_card
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, card, thought
difficulty: medium

## jail-early-pay-own-railroad-race-04
category: JAIL
scenario_slug: jail-early-pay-own-railroad-race-04
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: pay_jail_fine
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, tempo, thought
difficulty: medium

## jail-late-roll-orange-danger-05
category: JAIL
scenario_slug: jail-late-roll-orange-danger-05
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly rules and how to win - Wargamer, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: roll_for_doubles
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, defense, cash, thought
difficulty: hard

## jail-late-roll-red-danger-06
category: JAIL
scenario_slug: jail-late-roll-red-danger-06
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly Analysis - SangHyun Kim, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: roll_for_doubles
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, defense, cash, thought
difficulty: hard

## jail-late-roll-house-shortage-07
category: JAIL
scenario_slug: jail-late-roll-house-shortage-07
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: When To Build Houses vs Hotels In Monopoly, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: roll_for_doubles
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, defense, cash, thought
difficulty: hard

## jail-late-roll-cash-poor-08
category: JAIL
scenario_slug: jail-late-roll-cash-poor-08
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: roll_for_doubles
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, defense, cash, thought
difficulty: hard

## jail-card-third-turn-use-09
category: JAIL
scenario_slug: jail-card-third-turn-use-09
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: MONOPOLY Parker Brothers Real Estate Trading Game Rules, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, use_get_out_of_jail_card, roll_for_doubles
preferred_action: use_get_out_of_jail_card
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, card, thought
difficulty: medium

## jail-card-late-own-orange-income-10
category: JAIL
scenario_slug: jail-card-late-own-orange-income-10
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly rules and how to win - Wargamer, Actuarial Monopoly - Society of Actuaries
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, use_get_out_of_jail_card, roll_for_doubles
preferred_action: use_get_out_of_jail_card
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, card, thought
difficulty: medium

## jail-third-turn-no-card-pay-11
category: JAIL
scenario_slug: jail-third-turn-no-card-pay-11
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: MONOPOLY Parker Brothers Real Estate Trading Game Rules, Monopoly Rules: How to Play Monopoly
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: pay_jail_fine
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, tempo, thought
difficulty: medium

## jail-third-turn-low-cash-roll-12
category: JAIL
scenario_slug: jail-third-turn-low-cash-roll-12
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly Rules: How to Play Monopoly, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: roll_for_doubles
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, defense, cash, thought
difficulty: hard

## jail-own-red-rent-collection-13
category: JAIL
scenario_slug: jail-own-red-rent-collection-13
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Monopoly Analysis - SangHyun Kim, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: pay_jail_fine
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, tempo, thought
difficulty: medium

## jail-own-orange-safe-board-pay-14
category: JAIL
scenario_slug: jail-own-orange-safe-board-pay-14
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: pay_jail_fine
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, tempo, thought
difficulty: medium

## jail-cash-poor-danger-roll-15
category: JAIL
scenario_slug: jail-cash-poor-danger-roll-15
strategic_tension: Jail as tempo early, defense late, or card/third-turn management.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: pay_jail_fine, roll_for_doubles
preferred_action: roll_for_doubles
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, defense, cash, thought
difficulty: hard

## post-turn-end-no-good-mortgage-01
category: POST_TURN_STRATEGY
scenario_slug: post-turn-end-no-good-mortgage-01
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: medium

## post-turn-end-cash-danger-02
category: POST_TURN_STRATEGY
scenario_slug: post-turn-end-cash-danger-02
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard

## post-turn-end-avoid-overaction-03
category: POST_TURN_STRATEGY
scenario_slug: post-turn-end-avoid-overaction-03
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: easy

## post-turn-build-orange-before-beta-04
category: POST_TURN_STRATEGY
scenario_slug: post-turn-build-orange-before-beta-04
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, build, thought
difficulty: medium

## post-turn-build-red-before-gamma-05
category: POST_TURN_STRATEGY
scenario_slug: post-turn-build-red-before-gamma-05
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly Analysis - SangHyun Kim, MAS275 Probability Modelling Example
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, build, thought
difficulty: medium

## post-turn-build-light-blue-cheap-06
category: POST_TURN_STRATEGY
scenario_slug: post-turn-build-light-blue-cheap-06
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach, Monopoly Strategy - Quatizer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: build_houses_or_hotel
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, build, thought
difficulty: easy

## post-turn-unmortgage-reading-safe-07
category: POST_TURN_STRATEGY
scenario_slug: post-turn-unmortgage-reading-safe-07
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly/Strategy - Wikibooks, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: unmortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, space, thought
difficulty: easy

## post-turn-unmortgage-illinois-before-traffic-08
category: POST_TURN_STRATEGY
scenario_slug: post-turn-unmortgage-illinois-before-traffic-08
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly Analysis - SangHyun Kim, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: unmortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, space, thought
difficulty: medium

## post-turn-unmortgage-new-york-safe-09
category: POST_TURN_STRATEGY
scenario_slug: post-turn-unmortgage-new-york-safe-09
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly Statistics That Will Help You Win
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: unmortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, space, thought
difficulty: medium

## post-turn-propose-orange-before-ending-10
category: POST_TURN_STRATEGY
scenario_slug: post-turn-propose-orange-before-ending-10
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Actuarial Monopoly - Society of Actuaries, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, request, thought
difficulty: medium

## post-turn-propose-red-before-build-11
category: POST_TURN_STRATEGY
scenario_slug: post-turn-propose-red-before-build-11
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly Analysis - SangHyun Kim, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, request, thought
difficulty: hard

## post-turn-propose-railroad-swap-12
category: POST_TURN_STRATEGY
scenario_slug: post-turn-propose-railroad-swap-12
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly/Strategy - Wikibooks, Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: propose_trade
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, request, thought
difficulty: medium

## post-turn-mortgage-utility-build-orange-13
category: POST_TURN_STRATEGY
scenario_slug: post-turn-mortgage-utility-build-orange-13
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly rules and how to win - Wargamer, Winning Monopoly Strategies - UltraBoardGames
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, mortgage_property, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, space, thought
difficulty: hard

## post-turn-mortgage-railroad-build-red-14
category: POST_TURN_STRATEGY
scenario_slug: post-turn-mortgage-railroad-build-red-14
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Monopoly/Strategy - Wikibooks, Monopoly Analysis - SangHyun Kim
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, mortgage_property, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: mortgage_property
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, space, thought
difficulty: hard

## post-turn-avoid-unmortgage-cash-poor-15
category: POST_TURN_STRATEGY
scenario_slug: post-turn-avoid-unmortgage-cash-poor-15
strategic_tension: Intentional optional-action sequencing after movement.
source_claims: Winning Monopoly Strategies - UltraBoardGames, Monopoly rules and how to win - Wargamer
board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios
legal_actions_required: end_turn, build_houses_or_hotel, propose_trade, unmortgage_property
preferred_action: end_turn
acceptable_actions: rubric-dependent partial credit
bad_actions: actions missing the primary rubric branch
rubric_criteria: branch, cash, thought
difficulty: hard
