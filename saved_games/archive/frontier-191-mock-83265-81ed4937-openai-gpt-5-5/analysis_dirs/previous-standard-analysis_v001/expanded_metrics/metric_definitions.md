# Expanded metric definitions

All exact metrics are reconstructed from canonical events, resolved decisions, actions, and initial state. Null means the denominator or required observation does not exist; it never means zero.

## Trades

- **Proposal acceptance rate** = accepted episodes initiated / terminal-or-open proposals initiated.
- **Back-and-forth count** = number of `TRADE_COUNTERED` events between proposal and terminal event.
- **Public exchange count** = proposal plus counteroffers. Messages may add richer negotiation context but do not alter this count.
- **Partner HHI** = sum of squared proposal shares by counterparty; higher values indicate concentration.

## Auctions

- **Observed eligible players** are players with a bid or dropout event in the auction. This is deliberately not called rules-engine eligibility when no explicit eligibility snapshot was emitted.
- **Participation** requires at least one bid. **Dropout** requires `AUCTION_PLAYER_DROPPED`. **Win** comes from `AUCTION_ENDED`.
- **Winning-bid/list ratio** = winning bid / board list price.

## Mortgages and cash

- A **mortgage cycle** pairs a mortgage with the next unmortgage for the same player and space.
- **Mortgage churn actions per asset** = (mortgages + matched unmortgages) / unique mortgaged assets.
- **Cash volatility** is reported both for event deltas and reconstructed balances.
- **Maximum drawdown** is the largest peak-to-later-balance decline in the reconstructed cash series.
- A **cash shock** is a single cash delta of -$200 or worse. Recovery reaches the pre-shock cash balance; unrecovered shocks are censored.
- `cash_reason_metrics.csv` separates gross inflow, gross outflow, and net flow for every player/reason pair.
- Maximum underwater duration counts consecutive reconstructed cash observations below the prior running peak.

## Player-episode tables

- `trade_player_episodes.csv` supplies one initiator and one counterparty row per trade for role-correct denominators.
- `auction_player_episodes.csv` supplies one row per observed eligible player/auction with bids, dropout, and win fields.

## Semantic and counterfactual metrics

Promise fulfillment, deception, negotiation quality, and long-horizon agency require evidence-linked judge labels. Optimality and regret require an explicit oracle or counterfactual evaluator. The deterministic analyzer refuses to fabricate either class.
