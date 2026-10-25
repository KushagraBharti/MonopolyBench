# Cloud execution policy v1

Cloud campaign v2 uses the four Q4 2026 models at provider-native medium effort,
standard provider pins, and uncapped games. A game is valid for paper use only
when it ends by bankruptcy and both state and artifact replay pass. Smoke jobs
are always separate. Games execute the `audit_corrected_v2` treatment from
`docs/benchmark_audit_fixes.md`; the cloud runner adds no prompt or rule changes of
its own, and existing E0/E1 configurations are unchanged.

All requests use OpenRouter. Each physical completion attempt has a durable
intent and response, including corrective attempts. An initial invalid output
still gets one corrective attempt, then the existing deterministic fallback.
Transport errors pause the decision instead of choosing a fallback action.
Calls have a 1,200-second total deadline and metadata a 60-second deadline.
Account errors stop admission globally. Outages retry after 300 seconds, at most
12 scheduled attempts before operator intervention. Interrupted unknown requests
may repeat once per decision and three times per game, at the saved resolver stage.

The journal stores bytes and hashes before canonical writes. Recovery only
completes matching prefixes; contradictory bytes fail visibly. It preserves the
engine run ID, seed, player identities, seats, settings, prompt memory and legal
actions. Saved responses are reused without another paid completion. Repaired and
recovered games carry flags. A technical failure creates at most one rerun of the
same cell, retaining both jobs. A cancellation does not cause a rerun.

Campaign configurations, preflight evidence and execution order are frozen.
Amendments append seed blocks and record reasons. Do not deploy changed code in
the middle of a campaign. New campaigns must choose and record their seed cohort
before freezing; the repository's Q4 draft deliberately contains no drawn seeds.

Costs distinguish provider-account charges, OpenRouter charges, missing usage,
and interrupted requests with unknown charges. A known zero charge is different
from an unknown total. Run usage artifacts follow usage accounting v2; the
execution report remains the source for all physical-call costs, including calls
that never reached a resolved decision.
