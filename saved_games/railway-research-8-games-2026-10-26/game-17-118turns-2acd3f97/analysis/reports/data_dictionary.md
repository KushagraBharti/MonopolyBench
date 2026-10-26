# Data Dictionary: package-oi64rfxq

## Tables

- `run_summary.csv`: one-row run summary and artifact counts.
- `players.csv`: player/model configuration plus final summary values.
- `model_usage.csv`: token, cost, retry, fallback, and latency totals by player/model. `cost` is blank when any call cost is unknown; `known_cost_subtotal` and `missing_cost_calls` show coverage. `openrouter_model_id` is the seat's participant model; calls served by a configured fallback model (for example Opus 4.8 after Opus 5.5 refusals) stay in that seat's totals and are broken out in `fallback_model_calls`, `fallback_models`, `fallback_model_cost` and `fallback_model_known_cost_subtotal`. `fallback_rows` counts deterministic game fallback moves, which are unrelated.
- `per_call_usage.csv`: one row per OpenRouter call attempt. `openrouter_model_id` is the model that served the call; `participant_model_id`, `requested_model_id`, `response_condition` and `fallback_model_used` show when a configured fallback model served the seat.
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
