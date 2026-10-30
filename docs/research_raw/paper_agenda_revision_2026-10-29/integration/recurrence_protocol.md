# Construction-error recurrence protocol

Frozen before computing recurrence outcomes, 29 October 2026.

This observational extension asks whether a particular construction encoding error recurs at a later submitted construction decision in the same player-game. It does not test learning, an optimal policy, or the effect of corrective feedback.

The population is every recorded decision in the existing twenty-game corpus. A construction-submission decision contains a parsed tool call named `build_houses_or_hotel`. An uneven-error decision contains the exact validator substring `Uneven intermediate building operation` in an attempt's validation errors. A delivered-feedback case additionally has a later attempt in the same decision whose actual prompt scenario notes contain that exact error. The previous response alone does not count as delivered feedback.

For each uneven-error decision, find the next distinct decision in that player-game containing a parsed construction submission. Record whether its first construction submission repeats the error and whether any submission repeats it, whether the next decision is in the same global turn, the gap in that actor's decisions, the response conditions, and actual applied actions. Record right censoring when no later construction submission occurs. Also report the first delivered-feedback episode per player-game, to avoid presenting all overlapping episode links as independent replications.

The repeated opportunity is a submitted construction decision, not proof of an identical affordable allocation. Changed state, feedback persistence, different target allocations, refusals, and conditional submission selection prevent a causal feedback or durable-learning interpretation. No link crosses a game boundary. Original resolution outcomes stay intact. All totals retain player-game and configured-model strata.

Validation will reconcile corpus size, known uneven-error population and configured-model counts against the retained recovery audit. Synthetic tests will cover a late error, feedback in a later prompt, missing feedback, next-decision rather than same-decision lookup, censoring, and cross-game separation.
