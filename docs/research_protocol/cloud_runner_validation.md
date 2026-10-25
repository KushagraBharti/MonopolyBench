# Cloud runner code validation

Local validation on 2026-10-24, extended on 2026-10-25:

The PR adversarial review also covers corrupt committed prefixes with pending
appends, missing journal records, repair attribution after restart, interrupted
atomic-write temporary files, pause/resume ownership, preflight cancellation,
finalizer scheduling, atomic campaign freeze, serialized export revisions, and
decision pagination beyond 300 decisions. Readers expose committed JSONL bytes;
pending response artifacts remain hidden from the decision inspector. The
bounded reader cache tails only newly committed journal/decision records; a
regression verifies that repeated list/bundle requests do not rescan old payloads.

- Full repository verification: contracts, Ruff, mypy, 245 engine/API/arena/
  telemetry tests, frontend lint and frontend build passed.
- All 20 microbench tests, which the repository verification script omits,
  passed (265 Python tests in total).
- A five-process smoke batch passed, including one killed worker and verified
  package round trips.
- A five-process uncapped mock batch ended by bankruptcy at turns 160, 143,
  153, 94 and 138. One worker was killed and recovered; this interruption did
  not require canonical byte repair. Both replay
  verdicts passed for every game. All five exported packages verified.
- The uncapped batch recorded 1,691 physical mock completion calls and
  54,883,635 compressed package bytes. These are fixture measurements, not
  real-model cost or performance predictions.
- Unit/integration coverage includes journal prefixes and contradictions,
  all transition kinds, initial/corrective response reuse, interruption limits,
  persisted outage budgets, five-slot scheduling, live writer locks, exact local
  event/action/prompt/snapshot preservation, account pauses, auth and export scope,
  path rejection, BYOK cost states, and package integrity.

The mock policy deliberately concentrates property ownership and builds houses
to exercise terminal bankruptcy. It is a test fixture, not a research player.

The image builds with the locked Python workspace and a cloud frontend. This
workspace's proxy requires its CA bundle as a BuildKit `build_ca` secret for
dependency downloads; certificate verification stays enabled. Railway's schema
URL returned HTTP 403 here, so live platform configuration validation remains a
deployment check.

Container runtime checks also passed: health 200, unauthenticated jobs 401,
password login 200, authenticated status and export-token reads, and SIGTERM
shutdown with exit code 0. No provider key was supplied to the container.

A separate container with a loopback-only mock gateway passed the complete API
flow: all four preflight routes, preparation, idempotent repeated launch, two
concurrent smoke jobs through supervisor/worker/finalizer, passing replay and
analysis, export-token downloads, and local inventory verification. It used a
dummy mock key and made no paid requests.

The browser pass uses Chromium against the container with a copied mock data
volume. It exercises password login, five completed cards, modal dismissal,
job-scoped decision pagination, board geometry, static image responses, and a
390-pixel mobile viewport. The decision inspector and live feeds have bounded
heights; dashboard styles do not override the existing game panel controls.

The single-service Docker Compose path was also exercised from a build context
with no host `build_info.json`. One healthy container automatically started its
internal mock gateway, passed preflight, completed the built-in smoke game,
passed replay and analysis, and served a verified downloadable package. Removing
and recreating the container preserved its volume, credentials, authenticated
session, completed job, and export token without queuing a second demo game.
Killing the supervisor caused the container to restart and become healthy again.
The committed image's source and lockfile fingerprints matched the host. A second
supervisor crash with five active smoke games recovered all five; every game
completed with passing replay/analysis and a verified export. Final SIGTERM
shutdown exited with code 0.
Normal mode without an API key started a working authenticated dashboard and
failed preflight without creating paid jobs. Chromium verified localhost HTTP
login, the demo banner, board rendering, decision inspection, and session reload
without page errors. Tests cover volume-mode separation, demo campaign blocking,
secret persistence, local-only cookie behavior, and build fingerprints. ASGI
cancellation cleanup now releases the shared game tailer under cancelled scopes.

## Stacked on the `audit_corrected_v2` treatment (2026-10-25)

These checks rerun the evidence after merging PR #2. Cloud games now use the v2
rules, usage accounting v2 and PR #2's strict completion contract.

- Full repository verification: contracts, Ruff, mypy, 425 Python tests
  (engine 65, API 114, arena 176, telemetry 41, microbench 29), frontend lint and
  frontend build passed.
- Each physical call has exactly one durable owner: `CloudClient` journals it, and
  the resolver's local call journal and deadlines step aside. A regression game
  pauses after three failed transport attempts and resumes to the same
  events/actions as an uninterrupted game. Every decision attempt references a
  responded ledger call, and no resolver call files exist.
- Two uncapped five-process mock batches each killed and recovered one worker.
  All ten games ended by bankruptcy at turns 159, 147, 152, 125 and 143 (both
  batches were identical), with 1,588 responded calls per batch and none unknown.
  Both replay verdicts, analysis and every package verification passed. Every
  exported run also satisfies PR #2's strict completion check, with exactly one
  terminal `GAME_OVER` snapshot.
- The Compose demo built from the stacked commit served health with its git SHA,
  local password login, a completed smoke game with passing replay and analysis,
  and a token-authorized export that passed `unpack_verified` and the strict
  completion check. With `MB_LOCAL_HTTP=0`, the image refused to start without a
  private dashboard password. With one it became healthy, rejected `monopoly`,
  and accepted the private password.
- Regressions cover storage-full finalization retry, generation-metadata cost
  backfill into the call ledger (credit, BYOK, BYOK revealed only by generation
  metadata, upstream cost without a BYOK flag, and BYOK evidence without an
  upstream bill, each agreeing with usage v2), the 1,000-decisions-per-turn guard
  in the cloud worker, BYOK upstream cost in exported analysis tables, and
  exported analysis that keeps unknown call costs unknown while reporting known
  subtotals and missing-cost counts.
- Operational regressions cover a full SQLite ledger pausing a game for storage
  like a full disk, a frozen campaign's concurrency bounding simultaneous games, a
  failed replay verdict being saved when finalization raises, a recovered worker
  reading its decision log once instead of before every decision, and a dashboard
  review read leaving a journaled run recoverable.

Not exercised here: Railway deploy/redeploy, backup restoration, real provider
compatibility, BYOK billing, Windows/macOS export execution, and real-model soak
performance. The draft campaign remains unfrozen with no seed draw. Follow the
release acceptance steps in `deploy/README.md` before paper games.
