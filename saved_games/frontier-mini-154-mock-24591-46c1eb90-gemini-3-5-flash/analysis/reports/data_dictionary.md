# Data Dictionary: frontier-mini-154-mock-24591-46c1eb90-gemini-3-5-flash

## Tables

- `run_summary.csv`: one-row run summary and artifact counts.
- `players.csv`: player/model configuration plus final summary values.
- `model_usage.csv`: token, cost, retry, fallback, and latency totals by player/model.
- `per_call_usage.csv`: one row per OpenRouter call attempt.
- `per_turn_usage_by_player.csv`: token/cost totals by turn and player.
- `per_turn_usage_total.csv`: token/cost totals by turn.
- `decisions.csv`: flattened decision resolution rows.
- `actions.csv`: applied engine actions.
- `events.csv`: canonical event stream flattened for scanning.
- `event_counts.csv`: event type frequency.
- `events_by_turn.csv`: event volume by turn.
- `state_by_turn_player.csv`: player cash, position, asset values, and computed net worth by turn.
- `property_holdings_by_turn.csv`: owned property snapshots by turn.
- `bank_inventory_by_turn.csv`: bank house/hotel inventory by turn.
- `trace_findings.csv`, `failure_findings.csv`, `review_queue.csv`: review and issue traces.
- `cash_flow.csv`, `asset_flow.csv`, `auction_threads.csv`, `negotiation_threads.csv`: domain-specific telemetry streams.
- `top_*_calls.csv`: highest cost, latency, output-token, and reasoning-token call outliers.
- `expanded_metrics/`: deterministic trade, auction, mortgage, cash, rent, and decision episode metrics.

## Coverage

- `coverage/artifact_presence.csv`: expected canonical artifact presence.
- `coverage/file_inventory.csv`: recursive file inventory.
- `coverage/file_inventory_summary.csv`: file counts and size by area.
