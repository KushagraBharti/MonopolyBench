# Create, review and start a campaign

The cloud workspace lets the owner create a full campaign without a repository
change or deployment. Choose a name, a game count in groups of four and the number
of simultaneous games. The fixed Q4 participants use medium effort, uncapped
turns and the existing refusal-recovery policy. Each group shares one fresh board
seed across four cyclic seat rotations, so every participant takes every seat.

Review shows the server's prepared settings and models. Saving creates a frozen,
ready campaign. It does not create jobs or start games. Starting is a separate
explicit action. The server rechecks readiness when Start is requested, including
source identity, model-check freshness, maintenance/account stops and disk reserve.
An old campaign remains inspectable when a code update prevents it from starting.
Nothing automatically migrates or re-freezes its records.

The games dashboard requests `/api/campaigns?summary=true` for campaign names,
so its refreshes do not repeatedly download every embedded research record.

`POST /api/campaigns/prepare` accepts `name`, `seed_blocks` and `concurrency`.
It durably reserves outcome-blind seeds and returns the exact review matrix,
configuration, preparation ID and readiness. It never calls a model or creates
jobs. Draws exclude packaged cohorts, the earlier exclusion universe, all saved
job/cell seeds and every previous server preparation. Selection and reservation
share a serialized transaction. Seed entropy, digest/counters, exclusions and
execution ordering are retained. Reviewing again retains the earlier preparation.

`POST /api/campaigns/create` accepts the preparation ID and an idempotency key.
It freezes that exact server-held preparation on the current source after a
passing model check within six hours. Repeat saves return the same campaign;
reusing a save key with another preparation is rejected. The research-freeze
records embed the cohort, matrix and analysis contract with canonical JSON hashes.
The runtime cohort supplements the packaged registry without editing repository
files. These records are not a claim of external preregistration. Campaign exports
remain self-contained and preserve the records of unstarted and failed games.

`POST /api/campaigns/{id}/run` is the explicit start action. It rejects blocked
campaigns before changing their status. The supervisor retains its existing
identity guard, concurrency and execution behavior. Pausing a campaign pauses
new launches; already running games finish their current work under the existing
supervisor policy. Research details, artifact downloads and replay remain available
without occupying the main setup flow.

The billing policy is unchanged: OpenAI BYOK preferred with OpenRouter-credit
fallback, Anthropic BYOK preferred, Google/xAI OpenRouter credits, observational
billing enforcement, existing funding only and no added campaign dollar cap.
One technical rerun per cell retains the original; losses are not rerun. Creating
and saving are free of provider calls. Checking model connections makes provider
compatibility requests, and starting games uses the configured funding.
