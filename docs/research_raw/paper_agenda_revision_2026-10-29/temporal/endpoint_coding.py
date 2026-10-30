"""Manual endpoint adjudications, separate from the mechanical linkage.

The eight landing policies form an exhaustive text-defined subset. The additional
chronologies are illustrative, not a random subsample or a success-rate census.
All remaining prospective rows retain explicit unscorable reasons below.
"""

LANDING_POLICIES = {
    'G02d000161': ['VIRGINIA_AVENUE', 'MEDITERRANEAN_AVENUE'],
    'G03d000016': ['PARK_PLACE'],
    'G04d000126': ['VIRGINIA_AVENUE', 'MEDITERRANEAN_AVENUE', 'B_O_RAILROAD', 'NORTH_CAROLINA_AVENUE'],
    'G05d000103': ['ORIENTAL_AVENUE', 'VIRGINIA_AVENUE'],
    'G06d000036': ['ORIENTAL_AVENUE', 'CONNECTICUT_AVENUE', 'ELECTRIC_COMPANY'],
    'G06d000037': ['ORIENTAL_AVENUE', 'CONNECTICUT_AVENUE', 'ELECTRIC_COMPANY'],
    'G09d000119': ['ATLANTIC_AVENUE', 'VENTNOR_AVENUE', 'MARVIN_GARDENS', 'PACIFIC_AVENUE', 'VIRGINIA_AVENUE', 'BALTIC_AVENUE'],
    'G16d000103': ['VIRGINIA_AVENUE'],
}

# source id: (endpoint decisions, status, endpoint interpretation).
TRACES = {
    'G09d000064': ([65,66,67,68,102,103,162,163,164], 'delayed_target_reached',
        'The three-house dark-blue target is reached at d163, turn60, after d64 turn29. d67 adds Boardwalk, d102 adds Park Place, and d163 adds one to each. Financing, rolls and trades intervene; the record establishes a realized target, not an effect of remembered planning.'),
    'G11d000219': ([220,221,222], 'conditional_target_reached',
        'After the jail exit, d220 adds the third Park Place house; d221 also adds a fourth Boardwalk house. The source action is PAY while the named-content audit records ROLL. Later adherence to one plan does not resolve that earlier channel conflict.'),
    'G12d000131': ([132,133], 'stopping_rule_observed',
        'The improved offer is rejected at d132; the speaker ends at d133 and explicitly says to stop bidding against itself. Later different negotiations are not violations of this offer-specific endpoint.'),
    'G13d000163': ([164,165], 'public_plan_realized',
        'The public mortgage-to-houses statement is followed by construction at d164 and END at d165. No quantity or horizon was specified; this is local realized consistency, not evidence that other unbuilt turns were involuntary.'),
    'G14d000145': ([146,147,148,149], 'same_turn_target_reached',
        'Three later single-house-per-street layers complete the stated brown4/4 target at d148, with d149 cash619. The source and follow-ups share turn61. This is eventual target attainment, not preservation of the rejected proposal within d145 or proof of learning.'),
    'G14d000190': ([191,192], 'next_step_debt_paid',
        'The next action mortgages Marvin Gardens as stated. The current debt is paid and d192 cash is20. No later solvency or winner counterfactual is inferred.'),
    'G15d000143': ([144,151,155], 'explicit_policy_revised',
        'The next management action builds one house on each brown despite the source sentence Do not build browns. d144 gives a revised income-and-reserve rationale. The later NC opportunity starts an auction, followed by a150 bid, consistent with contesting rather than promising a list-price purchase.'),
    'G15d000271': ([273], 'conditional_redemption_observed',
        'The later Short Line redemption is applied at d273. Its event charge is111 rather than the110 anticipated by the source. This is an engine fee discrepancy, not failure to perform the named redemption.'),
    'G17d000162': ([166,169,172], 'auction_ceiling_revised',
        'An approximate400 ceiling becomes460 at d166, then530 at d169; actual bids410 and500 exceed the earlier figures. d172 drops because the minimum551 exceeds cash545. Revised rationales invoke opponent resale risk; their truth or optimality is not identified.'),
    'G17d000228': ([229,230,231,232], 'auction_limit_respected',
        'After the speaker bids40, p1 jumps to100, so the next legal minimum101 exceeds the99 cash ceiling. Dropping at d232 therefore does not contradict the instruction not to drop before99. The opponent outbids as forecast; future construction is a separate conditional claim.'),
    'G17d000236': ([237,241,242], 'explicit_plan_revised',
        'Instead of immediately building three fourth houses, d237 ends with a revised reserve argument. At the later changed state d241 builds only Oriental. The source and revision use liquidation calculations that omit unlocked light-blue mortgages; the sequence is not proof that the revision improved play.'),
    'G18d000253': ([254,255,256,257,258,259,260,261], 'counter_then_fallback_sequence',
        'The recipient counters, the speaker rejects, then mortgages Atlantic, Marvin and Pacific and reaches dark-blue2/2 at d259. It adds a further Boardwalk house at d260. A counter rather than a literal rejection triggered the fallback; the sampled record also contains a named content/action conflict.'),
    'G18d000428': ([429,430], 'next_step_debt_paid',
        'After selling three red houses, the next action mortgages Kentucky; the750 debt is paid, and d430 cash is69 with orange hotels retained. This endpoint is current-debt payment, not permanent asset preservation.'),
    'G19d000092': ([93,94,95], 'explicit_offer_plan_revised',
        'Following rejection, d94 ends rather than raising toward300. The applied note explicitly says not to raise before the roll and gives a reserve calculation. This establishes observed revision, not a feedback-caused improvement.'),
    'G19d000234': ([235,236,237], 'same_turn_layers_observed',
        'Two further red layers follow at d235 and d236 in turn115; d237 cash is262. The source commits to later layers but does not itself specify a total of nine purchases.'),
    'G20d000040': ([42,44,46,47], 'within_auction_revision',
        'The initial235 numerical ceiling is not breached: bids230 and232 precede withdrawal at minimum234. However, d42 explicitly tightens the ceiling to230, and d44 acknowledges exceeding that newer ceiling by2. Revision occurs with no auction settlement or intervening income.'),
    'G20d000099': ([100,101,102,103], 'sequence_revised_target_reached',
        'The next action offers Vermont for150 rather than mortgaging it. After rejection, d102 mortgages Vermont and d103 cash is157, reaching the stated financing endpoint in the same turn. Immediate-next-action and eventual financing consistency differ.'),
    'G20d000256': ([257,258], 'condition_failed',
        'The proposed cash-for-New-York acquisition is rejected. The six-house development plan was conditional on acceptance, so subsequent END is not a failed execution of an available accepted-trade plan.'),
    'G20d000324': ([325,326], 'affordance_followed_by_action_not_promise',
        'The source says a fourth house unlocks a hotel next step. d325 converts Pennsylvania to a hotel. The source is an affordance statement, not an unambiguous commitment; it stays in the broad candidate inventory and out of adherence rates.'),
}

UNSCORABLE = {
    'G01d000044': 'Reopening is conditional on a price drop or changed holdings, with no date; neither persistence nor abandonment follows from the next END alone.',
    'G01d000318': 'Building is gated by a liquidation threshold and opponent timing. No unique prescribed quantity or deadline is given; testing optimal restraint would require legal branches.',
    'G01d000426': 'Jail-card use and pink purchase are conditional policies; a windfall and a future jail opportunity are not controlled.',
    'G02d000249': 'Multiple no-buy/no-trade policies and an insolvency forecast have different conditions. No single binary temporal endpoint is specified.',
    'G03d000088': 'Asking terms describe a negotiation target, not an unconditional commitment to obtain agreement or a deadline.',
    'G03d000102': 'Mortgage-first policy is triggered by being short of cash, whose threshold and purpose are unspecified.',
    'G05d000251': 'Building depends on rival approach and reserve assessment; a later build alone cannot establish whether that condition was met earlier.',
    'G07d000168': 'Restoring the third Park Place house requires an unspecified sensible liquidity buffer. Cash availability alone does not define compliance.',
    'G07d000182': 'Pennsylvania acquisition then green construction is a contingent goal without control of the required acquisition or a deadline.',
    'G07d000203': 'Jail retention can terminate through an involuntary doubles roll. A later departure is not by itself a plan violation.',
    'G08d000125': 'Reopening depends on buildable completion or seller pressure. The latter is not defined by an observable threshold.',
    'G08d000177': 'Prospective expansion starts from a false current-development account in an applied END record. The named conflict and actual bare holdings preclude treating the stated cash4 and2/2/3 houses as the plan starting state.',
    'G08d000254': 'A cash/reachable-liquidity rebuilding threshold is conditional on uncertain future receipts and no deadline is supplied.',
    'G09d000032': 'High-value purchase class is unspecified. St James is emphasized but no unconditional next-purchase identity is promised.',
    'G09d000198': 'Public mortgage-to-development goal has no quantity or horizon. Context records the next opportunities; lack of an immediate build is not a failed promise.',
    'G10d000044': 'Acquiring St James before building requires another owner or future bank opportunity; no acceptance, price or deadline is promised.',
    'G10d000057': 'Repeated acquisition-and-building goal remains conditional on acquiring St James and preserving reserves.',
    'G10d000132': 'Revisit talks after a real St James bid is a conditional negotiation policy; meaningful price and deadline are unspecified.',
    'G11d000066': 'Reassess after an orbit is not an observable action commitment. Later reserves also depend on GO and random movement.',
    'G12d000045': 'Virginia acquisition then building is a goal, with no purchase opportunity under the actor control or deadline.',
    'G12d000072': 'Virginia acquisition then building remains conditional; current rival cash claims are adjudicated separately from the own plan.',
    'G12d000096': 'Connecticut then Vermont is a multi-party conditional negotiation, not an executable unilateral sequence at the source decision.',
    'G13d000098': 'Mortgage-to-build policy begins only after a set is acquired, with no fixed deadline or unique mortgage order.',
    'G13d000160': 'Atlantic expansion rests on a phantom completed build and cash57 in an actual END record with cash357. A later action cannot validate that starting account.',
    'G13d000171': 'Price floor and later construction depend on counterterms and clearing railroad risk; no single stable-state endpoint is specified.',
    'G14d000150': 'Denial priorities do not promise an unconditional purchase at a specified price or opportunity.',
    'G14d000164': 'Denial purchases require future cash to clear multiple threats; terms and deadline are not fixed.',
    'G17d000040': 'Delay the Virginia premium until States acquisition is a conditional bargaining preference, not an observable instruction on every future bid.',
    'G17d000240': 'Third Park Place house is a next major investment after income; major and sufficient income are not quantified.',
    'G18d000244': 'Ventnor pressure is conditional on the recipient funding threshold; actual future counterterms matter.',
    'G20d000164': 'Reopen talks after Pacific acquisition is a conditional public invitation, not a fixed action commitment.',
    'G20d000215': 'Approximate130 ceiling is a soft bound; no observed bid above it establishes only local consistency, not a tested willingness to stop at that threshold.',
}

# These are semantic types, not correctness labels. One row may contain more than
# one proposition; the type describes the principal forecast candidate.
FORECAST_TYPE = {
 'G01d000137':'possible_movement','G01d000426':'possible_choice',
 'G02d000161':'auction_capacity_and_result','G02d000266':'rent_exposure',
 'G03d000207':'capacity_and_stock_endpoint','G04d000126':'conditional_financing',
 'G05d000103':'unbounded_terminal_claim','G05d000208':'conditional_liquidation',
 'G05d000251':'movement_reachability','G05d000300':'unbounded_terminal_claim',
 'G06d000190':'unbounded_terminal_claim','G07d000182':'financing_feasibility',
 'G07d000329':'conditional_liquidation','G08d000177':'possible_movement',
 'G09d000082':'hypothetical_trade_financing','G09d000212':'unbounded_terminal_claim',
 'G10d000133':'possible_movement','G11d000219':'unbounded_bankruptcy_candidate',
 'G11d000235':'conditional_liquidation','G12d000072':'financing_feasibility',
 'G13d000098':'financing_feasibility','G13d000171':'hypothetical_trade_financing',
 'G14d000140':'financing_feasibility','G14d000164':'financing_feasibility',
 'G15d000143':'financing_feasibility','G15d000169':'hypothetical_trade_financing',
 'G15d000262':'conditional_liquidation','G16d000322':'hypothetical_trade_financing',
 'G17d000228':'auction_choice_and_conditional_build','G17d000236':'conditional_liquidation',
 'G18d000244':'movement_probability','G18d000284':'movement_reachability',
 'G19d000062':'hypothetical_trade_financing','G19d000092':'financing_feasibility',
 'G19d000220':'unelicited_counterparty_refusal','G20d000319':'conditional_liquidation',
}

FORECAST_TRACES = {
 'G02d000161': ([162,163,164], 'The two cash-constrained rivals drop and p2 receives New York at192. This is a correct event forecast grounded in the public bid limit, not evidence of private-belief inference.'),
 'G03d000207': ([208,209,210,211,212,213], 'The next own management at Short Line has three bank houses, but it follows the speakers doubles continuation before any opponent acts, so it is not a test of opponent behavior. At the later own Boardwalk management after rival decisions, stock is still three. Neither endpoint validates the stated upper bounds on opponents legal financing capacity.'),
 'G17d000228': ([229,230,231,232,238,243,246,252,253,254,255,256,257,261,264,267], 'The rival outbids at100. Its subsequent jail rolls lead to a fine and debt liquidation before first management at d257 with cash63. No subsequent actual menu offers building through elimination at d267. The outbid is realized, but the later absence of building is neither a deliberate nonbuild nor a falsification of the initial conditional financing claim. Alternative financing sequences from later management are not executed in this extension.'),
 'G19d000220': ([221,222,223,224,225], 'No offer is made or received before the speaker is eliminated. The assertion that opponents would not pay therefore has no observed acceptance test; their later receipt of the estate is not evidence of an elicited refusal.'),
}
