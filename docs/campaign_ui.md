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

The Dashboard summarizes all saved games, campaigns, tests and exports, with
recent activity and workspace readiness. Its totals are counted across the
database, independently of list pagination. Games lists standalone runs only;
Tests lists short model checks; campaign games stay in their parent campaign.
The sidebar links to Dashboard, Games, Campaigns, Tests and Exports. List pages
request `/api/campaigns?summary=true` for names without embedded research records.

Exports is the authenticated download library for completed game packages,
diagnostic packages and campaign snapshots. A campaign's visible download controls
prepare a revisioned snapshot and retain links after refresh. Snapshots taken
before every game finishes preserve the current records; they do not imply final
game packages exist. Earlier revisions remain downloadable in Research details.
Preparing or downloading a snapshot never starts a game or calls a provider.

`POST /api/campaigns/prepare` accepts `name`, `seed_blocks`, `concurrency` and an
optional shared `cost_budget` recorded-spend pause threshold.
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
campaigns before changing their status and immediately creates every game entry
and Watch board link. Before a worker saves a move, the API returns a deterministic
engine-produced initial board marked `snapshot_kind=initial_preview`. It is not
a canonical checkpoint. Committed snapshots and WebSocket events replace it as
the game progresses. No engine rules are implemented in the UI.

Campaign Pause requests safe boundary pauses for playing games and holds queued
games. An in-flight model request may finish. Resume restarts campaign-paused games
after their previous writers release their locks; individually paused games stay
paused. Every game card also has its own pause, resume and cancel controls.
`POST /api/campaigns/{id}/cells/{index}/start` starts only that game, with an
explicit individual override. It does not authorize the remaining games. A single
game may explicitly resume while the campaign stays paused. Campaign cancellation
is terminal and prevents unstarted games and technical reruns from launching.

Run one game is a separate `/games/new` flow. `POST /api/games/prepare` accepts
four supported models, low/medium/high effort, an uncapped game or a 1–10000 turn
limit, and an optional recorded-spend threshold. `POST /api/games` starts exactly
one reviewed preparation with an idempotency key. It records `kind=single`, keeps
full research artifacts and does not claim to be a balanced campaign. Model tests
retain `/api/smoke/prepare` and `/api/smoke`, 5–10 turns, 1–20 games, configurable
effort/models and an optional threshold for each game.
Resuming a standalone game or test does not require a fresh campaign connection
check and remains available in demo mode. It still checks code identity, account
and maintenance stops, storage and the recorded-spend threshold.

The billing policy is unchanged: OpenAI BYOK preferred with OpenRouter-credit
fallback, Anthropic BYOK preferred, Google/xAI OpenRouter credits, observational
billing enforcement and existing funding only. No budget is added by default.
One technical rerun per cell retains the original; losses are not rerun. Creating
and saving are free of provider calls. Checking model connections makes provider
compatibility requests, and starting games uses the configured funding.

An optional `cost_budget` pauses before new requests when known recorded spend
reaches the threshold. A campaign threshold is shared across every game and
technical rerun; a standalone or test threshold applies to each game. Missing or
unknown settled costs pause capped runs rather than counting as zero. In-flight
requests can finish and concurrent calls can overshoot, so this is not a guaranteed
hard spending cap or a statement about free quotas or final invoices. The guard
does not estimate charges or alter prompts. A reached immutable threshold cannot
be bypassed by Resume; uncapped runs retain their existing accounting behavior.
The same restriction applies to an unreconciled charge, including an HTTP error
or timed-out request with no reported cost. Resume does not acknowledge or erase
that uncertainty. If the provider never supplies a reconcilable charge, that
capped run cannot continue with its immutable settings. Preserve its artifacts
and create a separate run if needed; there is no charge-waiver control.
