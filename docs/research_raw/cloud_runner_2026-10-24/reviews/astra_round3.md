# Astra round 3 review

Review of `docs/cloud_runner_plan.md` at commit `c370c87cbfae36c4947946fdd94c8da9f2452f68`, using its current 471-line draft. Repository paths below are relative to `/Users/kushagra/CS-Projects/MonopolyBench`. I made no repository edits, git changes, paid calls, or authenticated calls. I checked the prior reviews, the measurement JSON, saved-run files, referenced code, and public documentation. This file contains issues only.

## Blocking

### B1. The outage policy does not define the action boundary or the probes

Section: Decisions needed from you; Request deadline and provider errors; Release 1 tests. Lines 21, 32, 239, 394, 397.

Exact text: "For decision 8, the recommended policy pauses a game when one seat has 3 decisions in a row fail on transport after retries. The paused game probes every 5 minutes and resumes when the provider answers."

What is wrong: This leaves several benchmark-changing choices to the implementer. Does the third failed decision apply a fallback before pausing, or remain pending? Does an invalid but successfully transported answer reset the streak? Is a probe a free catalog GET, a new completion prompt, or another attempt at the pending decision? A catalog response does not establish completion availability. Paid probes could become unlimited extra attempts and charges, and a successful completion used only as a health probe could be discarded. There is no probe budget, termination rule, durable counter, or test. The plan also says only decisions 1, 3, and 4 need resolution before paid calls, although decision 8 changes the existing fallback policy. The unchanged-fallback test at line 394 needs an explicit exception for an accepted outage policy.

Proposed replacement:

> Decision 8 changes fallback behavior and requires an accepted, versioned rule before paid games use it. Until that rule is specified and tested, retain the existing transport-failure fallback policy and report those moves. The new rule must state whether the third failed decision remains pending, what resets each seat's failure counter, what a probe sends, whether it can incur cost, its maximum attempts and total spending, and how it resumes the saved resolver stage. Persist the counters across restarts. Apply account and budget stops before outage handling. Never discard a valid paid decision response as a health probe. Test the first, second, and third failures, an intervening transported invalid answer, restart while paused, successful recovery, exhausted probe allowance, and unchanged invalid-output fallback behavior.

If the intended rule is already settled, replace this requirements paragraph with those concrete choices. The current wording is not enough to implement safely.

### B2. Quarantining every byte after the commit offset can erase the action/events failure

Section: Release 1 guarantees; interruption table. Lines 210, 220, 222.

Exact text: "Bytes after the last committed offset are moved to a recovery sidecar with their hash. They are never silently dropped."

Also: "While writing files for a committed action, so files and the commit record disagree".

What is wrong: A complete action can be durable in `actions.jsonl` while its events or SQLite commit are incomplete. Moving that whole suffix out of the canonical files and resuming the older prefix would roll back an applied action and could ask the model again. Keeping a sidecar does not make that rollback acceptable. Round 2 explicitly prohibited removing complete actions or events to recover a prefix. The table's phrase "committed action" also misses the common case: the action was applied and written, but the commit record was never written. The same problem exists after the action's events but before the next pending decision.

Proposed replacement:

> Inspect and preserve the entire tail before changing any canonical file. Release 1 may quarantine an incomplete trailing record outside committed offsets. A complete action, complete engine event, or contradictory resolved-decision record beyond the last verified boundary causes a technical failure with the original files preserved. Release 1 never truncates a complete transition, compares only a common event prefix, or regenerates missing events to make recovery pass. This includes the gap before the next pending decision. Release 2 repairs such cases through its journal.

Replace the table's location with:

> After an action or autonomous advance was applied, while its files or commit record were still being written.

Add a targeted test where a complete action and its complete events exist beyond the SQLite offset. It must fail visibly in Release 1 even if the preceding prefix replays.

### B3. Release 1 needs the new preflight and billing guard, but the implementation list postpones them

Section: Models and routing; Research integrity; Release 1 and Release 2; Rollout. Lines 113, 358, 380, 410, 411, 420.

Exact text: "The billing guard then checks every response's returned model and provider. A route mismatch stops the game before the action is applied."

Also: "The new campaign contract, the new preflight version, and their tests." This is currently a Release 2 bullet.

What is wrong: Rollout step 5 needs the new preflight before the first Release 1 game. The current guard is `_CampaignBillingGuard` in `python/packages/arena/src/monopoly_arena/long_campaign.py:836`; ordinary `LlmRunner` jobs do not acquire it automatically. The Release 1 rows do not require wiring it into exploratory workers. The guard checks required BYOK at lines 880 to 884, but does not reject BYOK when OpenRouter-credit billing is required. A provider pin does not select the billing mode. A new dedicated OpenRouter key alone does not prove that an account-level upstream key cannot be used.

Proposed replacement:

> Release 1 includes the new production-shaped preflight and a shared route and billing validator used by every exploratory worker. The preflight sends the production tool choice and effort, verifies a legal tool response and the requested model/provider, and records credit billing. Every physical completion response is persisted and accounted for before the validator can stop the job. Credit-only jobs reject confirmed BYOK and pause if the required billing identity cannot be established. Tests cover wrong model, wrong provider, BYOK, missing billing evidence, and mismatch on a corrective attempt. The historical E1 preflight and its gates remain unchanged. Release 2 adds the new confirmatory campaign contract and its integration with this already-tested validator.

### B4. The allowance rule double-counts active spending and omits spent money from completed jobs

Section: Spending controls; Decisions; Rollout. Lines 27, 229, 248, 420 to 423.

Exact text: "A game starts only if the allowances of all admitted, queued, and running games fit inside both the batch ceiling and the key's `limit_remaining`."

What is wrong: Full allowances cannot be compared with a remaining-credit figure after some of those allowances have already been spent. Conversely, removing completed jobs from the sum can admit another full batch without counting the first batch's spend. The quoted list omits paused, recovering, and finalizing jobs with live obligations. There is also a default rollout failure: the preflight, smoke test, and first full game spend from a $250 lifetime key, then five $50 allowances no longer fit its remaining limit. Replacements need to retain predecessor charges and unknown exposure. "One replacement per game" can also recurse if every replacement gets a fresh entitlement to one replacement.

Proposed replacement:

> The ledger counts settled spend from every job in the authorized batch, unresolved exposure, and the unspent portion of each active or queued allowance. Admission adds the proposed allowance once and compares the resulting total with the original batch ceiling. It separately compares outstanding obligations with a fresh key balance, without subtracting settled charges twice. Paused and recovering jobs retain their allocations. Completing or cancelling a job releases only unused allowance; known charges and unresolved calls remain charged. A replacement shares its logical game's remaining allowance and consumes the single replacement entitlement of the original job, so replacement chains are impossible.
>
> Before the first paid validation call, allocate a validation budget and a five-game batch budget within the approved lifetime key limit. If the total approved limit stays $250, reduce the five game allowances to account for validation spending, or explicitly approve a separate validation allocation. Do not silently reset or raise the key limit. Test admission after partial spending, completion, pause, cancellation, uncertain charges, validation spending, and replacement.

## Should fix

### S1. The headline recovery guarantees exceed Release 1's stated failure model

Section: Release 1 guarantees; interruption table. Lines 205, 220, 224.

Exact text: "Release 1 promises that committed engine actions are never lost or applied twice. Interrupted games resume when the interruption happened during a model call."

What is wrong: Host loss can erase locally committed actions after the last R2 checkpoint. A model-call interruption can also exceed the repeat allowance, lack a conservative cost bound, or have a saved response that requires technical failure under Release 1. The unconditional table entry "Resume automatically" drops the conditions accepted in round 2.

Proposed replacement:

> On a surviving, intact local volume, Release 1 preserves verified committed transitions and never applies one twice in the continued execution. It automatically resumes an unknown interrupted request only when the old writer is dead, replay and artifact checks pass, the exact resolver stage is recoverable, and repeat and spending allowances remain. A saved response follows the separate saved-response rule. Other cases pause or fail with evidence. After host loss, only the last successful remote checkpoint is guaranteed to remain.

### S2. Account errors, temporary credit admission, and missing worker credentials need distinct handling

Section: Request deadline and provider errors; Spending controls; tests. Lines 237, 249, 255, 397.

Exact text: "HTTP 401, 402, and 403 get their own error types and pause the game with the response body saved. They never reach the fallback path."

Also: "Overshoot is small but not bounded at one call per game."

What is wrong: Round 2 required distinguishing actual exhaustion from temporary in-flight admission rejection. A 402 can be a transient rejection before the provider receives a request, not an unknown paid call. Treating every missing `usage.cost` as an uncertain maximum can consume allowance for known rejected requests. Missing credentials return `no_api_key`, not 401, at `openrouter_client.py:79`; a worker with a missing environment variable can still fall back after a supervisor preflight succeeds. Finally, nothing establishes that overshoot is small. [OpenRouter documents separate credit-limit reasons and transient admission responses](https://openrouter.ai/docs/api_reference/limits).

Proposed replacement:

> Missing worker credentials and HTTP 401 or 403 pause as account/configuration errors before any fallback action. For 402, preserve the body and relevant response headers, classify `error.metadata.limit_source` and `reason`, and distinguish exhausted funds from temporary in-flight admission rejection. The default for temporary admission rejection is a visible operational pause; any automatic retry rule must be bounded and versioned. A confirmed rejection before provider dispatch records that evidence rather than an unknown generation charge. Ambiguous network outcomes retain conservative exposure. Unknown settlements can cause overshoot, whose size is not established by these tests.

Test the account errors on both initial and corrective requests, missing worker credentials, and temporary versus permanent 402 responses. Keep an account-wide stop in the shared ledger so the other four workers do not continue issuing calls under a known broken account configuration.

### S3. The Release 2 host-restore promise is missing the remote request-intent boundary

Section: Release 2; interruption table. Lines 224, 408.

Exact text: "Saved responses reach R2 before the next paid call, and a game pauses if R2 is unreachable past a set tolerance. Host loss then means continuing on a new host."

What is wrong: Saving the previous response does not preserve the next request's existence. If the host disappears during that next call, the remote checkpoint can lack its intent, retry counters, and pending spend. A "set tolerance" can also allow several paid calls after the last recoverable checkpoint. A local `flock` does not fence a partitioned old host when a replacement host starts. The full journal needs a precise remote publication point before the stronger continuation claim holds.

Proposed replacement:

> Before each paid POST, durably upload its immutable request intent, resolver stage, retry counters, and spend obligation. Before the following paid POST, publish the preceding response and a verified remote checkpoint containing its action/event commit, required artifacts, and ledger state. Publish the checkpoint marker only after all referenced objects exist and hashes verify. An R2 outage prevents the next paid POST; upload retries have a bounded timeout and then pause. Restore only the latest verified marker with the original image and run ID, after fencing the old host. Account for any remote request intent without a response as an unknown call. Test host loss on both sides of each remote publication boundary and attempted restart of the old host.

### S4. The export manifest needs an explicit hash scope and cannot hash itself

Section: The exported package. Lines 287, 290.

Exact text: "storage_manifest.json      every file: relative path, bytes, SHA-256, role; plus the tree hash"

Also: "The tree hash uses the format already in `saved_game_manifest.json`."

What is wrong: "Every file" includes `storage_manifest.json`, which contains the tree hash, creating a self-reference. The ZIP must be outside its own inventory too. The legacy format is not unique: R191's `source_freeze.tree_hash_format` uses path + NUL + SHA-256 + LF, but Mini273 uses path + TAB + SHA-256 + TAB + bytes + LF. Most saved-game manifests have no such freeze field. The plan also drops POSIX separators, UTF-8 encoding, lowercase digest encoding, and ordinal case-sensitive ordering from the precise format. These matter for laptop verification across Windows and Linux.

Proposed replacement:

> `storage_manifest_v1` inventories every regular payload file, including the frozen `saved_game_manifest.json` and `cloud/` files, but excludes itself and the containing ZIP. It rejects symlinks and unsafe or duplicate normalized paths. Sort relative POSIX paths by Unicode code-point order. For each file, hash the UTF-8 sequence of its path, NUL, lowercase hexadecimal SHA-256, and LF; hash the concatenated sequence for the tree digest. Hash the completed storage manifest separately and use that digest in the immutable object key. This adopts R191's encoding as a new explicit export contract; it does not reinterpret other historical hash formats. Test the same package on Linux and Windows and verify both legacy schemes with their own declared format.

### S5. The existing standardizer will move the new cloud files into the canonical run

Section: Export; Release 1 finalizer. Lines 290, 296, 298, 383.

Exact text: "The `cloud/` folder is new. `docs/artifact_reference.md` will document it, and tests will confirm the local scripts ignore it."

What is wrong: `scripts/standardize_saved_games.py:82` does not preserve `cloud/` or `storage_manifest.json`. Its normalization loop at lines 238 to 246 moves unfamiliar root entries into `run/`. Running that existing local workflow would move the cloud evidence and invalidate the exported inventory. "Tests will confirm" is insufficient when the current implementation contradicts it. Exported ledger rows also need relative artifact references; the live rows and job data can contain `/data/...` paths that do not resolve on the laptop.

Proposed replacement:

> Update the standardizer's preserved root entries to include `cloud/` and `storage_manifest.json`. Keep cloud evidence outside `run/` when generating or regenerating local analysis. Record package-relative references in the export index while retaining original host paths only as provenance. Treat later local analysis as a new derived version instead of silently replacing files covered by the downloaded manifest. Test the standardizer, replay, both named analysis scripts, and a path-resolution audit on an exported copy.

### S6. Failed-game and campaign exports are not specified by the proposed completed-package workflow

Section: Jobs and states; Export; Research integrity. Lines 184, 211, 214, 295, 353.

Exact text: "`python -m monopoly_telemetry.cloud_export --dest saved_games/ [--campaign <id>] [--since <date>]` lists finished packages and downloads each to a temp file."

Also: "Failed, budget-stopped, cancelled, and replaced runs stay in the ledger and in campaign exports."

What is wrong: A damaged or early-stopped game cannot pass the same required-artifact checks as a complete game. It still needs an export, including when replay itself fails. The CLI description does not say whether "finished" includes failure packages. Filtering member games by campaign also does not export the contract, preflight evidence, planned cells that never started, execution order, or replacement relationships. Round 1 explicitly included that campaign-level evidence.

Proposed replacement:

> Export every terminal execution as either a validated completed-game package or a diagnostic package. A diagnostic package retains all existing raw files, quarantine evidence, missing-artifact and replay findings, and the job's final status; it never fabricates a summary or claims replay success. The CLI includes these packages by default. A campaign export also contains the frozen contract, preflight evidence, complete planned-cell matrix, actual launch order, unstarted cells and their reasons, replacement links, and campaign cost and outcome reports. Test failure before the first response, an action/events mismatch, cancellation, budget exhaustion, and a campaign stopped before all cells start.

### S7. R2 operation and storage estimates describe a different upload scheme

Section: Storage; Pieces we are not using; Release 1 checkpoints. Lines 81, 166, 214.

Exact text: "About 5,000 files per game means 100 games use about half the free monthly write allowance."

What is wrong: That multiplication assumes one PUT per raw file, once. The implementation uploads checkpoint packages and a final ZIP, not necessarily individual files. Retaining full checkpoints every 10 decisions also duplicates earlier evidence repeatedly. With roughly 350 to 600 decisions, there can be roughly 35 to 60 scheduled packages per game, plus time-triggered checkpoints and retries. With approximately linear growth, retaining all of them can consume tens of times one core run's bytes. The 2.5 GB working-space allowance and 5 to 12 GB for 48 games exclude that retention, the new raw call copies, interrupted evidence, and package staging. R2's free operation allowances apply to actual API operations, including multipart operations, not local file counts. [R2 pricing](https://developers.cloudflare.com/r2/pricing/).

Proposed replacement:

> Price R2 from the implemented object layout, checkpoint retention, and multipart operations. Release 1 uploads immutable checkpoint packages and final ZIPs, so local file count is not a PUT count. Keep a verified latest checkpoint and its predecessor while a run is active; retire superseded checkpoint packages only after verifying their replacement, and retain diagnostic checkpoints that contain unique evidence. Preserve the final package and failed-execution evidence. Measure cloud call-record bytes, peak staging space, checkpoint growth, and actual PUT/GET counts in the soak. The 100 to 250 MB planning range describes one final package before this additional overhead, not total host or R2 usage.

The retention choice must be stated explicitly. Keeping all checkpoints is also valid, but then size and cost that policy rather than quoting only final-game totals.

### S8. Generation metadata and finalization GETs can still stall indefinitely

Section: Request deadline; Finalization. Lines 233, 252, 379.

Exact text: "Each physical request gets a 20-minute total deadline, measured with a monotonic clock inside the request loop."

What is wrong: The described request loop is the completion retry loop. `_with_generation_metadata` awaits `get_generation` at `decision_resolver.py:399`, and finalization awaits `get_models` at `llm_runner.py:287`. These use the separate `_get_json` path at `openrouter_client.py:296`, with inactivity timeouts only. Round 2 specifically required bounded metadata lookup time after raw response persistence. Without it, the deadline does not bound a resolver stage or finalization. Line 235's "A slow but healthy call is never killed to meet a schedule" also needs to distinguish the 5-minute alert from the declared 20-minute deadline.

Proposed replacement:

> Apply the 20-minute total deadline inside each physical completion attempt. Give catalog, credit, key-limit, generation-metadata, and storage operations separate bounded total timeouts. Persist the completion response before metadata lookup. A metadata timeout records unavailable metadata and retains any unresolved spending exposure; it never causes another completion request. The 5-minute stall alert does not kill a worker. The declared completion deadline still applies. Test a trickling completion body and a trickling metadata response separately.

### S9. The live stream dropped recovery-generation and bounded-queue requirements from round 2

Section: Game page. Line 337.

Exact text: "The tailer reads `events.jsonl` only up to the committed byte offset and sends the snapshot that the same commit references."

What is wrong: The draft omits the round-2 requirements to track file identity/recovery generation and bound each viewer's queue. An offset or sequence alone can refer to a replaced file after recovery. The existing runner can snapshot engine state ahead of events still being yielded at `llm_runner.py:227`; pointing at a snapshot file is not sufficient unless the commit captures the complete corresponding engine advance. These are necessary details for the claimed consistent live view, not an invitation for the UI to reconstruct state.

Proposed replacement:

> Each live commit publishes a complete engine event batch and the exact engine snapshot after that batch. The envelope includes job ID, original run ID, recovery generation, commit ID, and snapshot event sequence. Tailers track file identity and committed offsets. A generation change or missing cursor causes an explicit reset to a committed snapshot. Each viewer has a bounded queue and send timeout; a slow viewer is disconnected and can reconnect with backfill. Test a snapshot taken during a multi-event advance, file replacement after recovery, duplicate delivery, and a viewer that never reads.

### S10. The mock server does not yet establish zero-cost or deterministic concurrency tests

Section: Release 1 test harness; Rollout. Lines 388, 393, 418, 419.

Exact text: "A local HTTP server that speaks the OpenRouter chat API. It returns scripted valid, invalid, and malformed tool calls, delays, 429, 5xx, 402, and dropped connections, so tests run the real httpx client at zero cost."

What is wrong: `OpenRouterClient` has a `base_url` constructor argument, but workers need to receive it explicitly. An empty dummy key returns `no_api_key` before HTTP, while omitted configuration can fall through to the real key in the environment. The test also exercises `/models`, `/generation`, and admission credit/key/endpoint checks, not just chat completions. A single global response queue will yield different answers when five games interleave. A memory soak with tiny responses understates the cost of real prompt/response artifacts and finalization. The outage policy needs additional scripted cases.

Proposed replacement:

> Test mode injects the local server URL and a nonempty dummy key into every worker and preflight client, clears live provider credentials, and denies outbound access except to the mock server. The mock implements completion, model catalog, endpoint, generation, credit, and key-limit responses used by the cloud flow. It keys scripted scenarios by game, decision, resolver stage, and transport attempt rather than arrival order. Include 401, 403, malformed JSON, trickled bodies, missing and delayed cost, wrong routes, BYOK, outage pauses, and recovery repeats. Use representative saved-run payload sizes for the memory/storage soak. Assert that no request targeted a public provider host.

### S11. The create flow has no coherent batch or random-seed review contract

Section: Jobs and states; Create game. Lines 172, 327 to 329.

Exact text: "`POST /api/jobs` validates the request and resolves the seed once."

Also: "Choose the seat order, a "rotate seats across games" toggle, and the number of games."

Also: "The exact resolved configuration: seats, routes, effort, seed, caps, code version, classification, batch ceiling remaining, key limit remaining, queue position, and the preflight verdict."

What is wrong: The review screen cannot show a resolved random seed if the seed is first resolved when launch is submitted. One POST returns one job ID, but the modal can request several games and a seat rotation. The plan does not define atomic versus partial admission, seed reuse across rotations, idempotent expansion after a partial failure, or which game opens. Queue position and remaining credit are observations that can change while the review modal is open.

Proposed replacement:

> A preparation endpoint stores a launch draft with the proposed batch's seed list, seats, and frozen configuration, then returns a preparation ID for the review screen. It neither starts games nor makes paid requests. The launch POST consumes that preparation ID with one idempotency key, rechecks changing admission conditions, and atomically creates the accepted batch and its ordered job IDs. Repeating it returns the same IDs and seeds; a failed admission creates no partial batch. Exploratory rotation uses four cyclic seat orders and shows the exact seed/order assigned to each game before launch. The result opens the batch view with links to each game. Queue position and available credit are labeled as current estimates until admission.

A simpler design is acceptable, but it must choose these semantics explicitly.

### S12. Browser-origin protections and managed-host bypass tests were dropped

Section: Security; Live and API tests; fallback hosting. Lines 341, 342, 344, 398, 435.

Exact text: "Cloudflare Access protects every path, including WebSockets and exports, with an allowlist of your email."

What is wrong: Access authentication is not a complete policy for browser-origin control requests. The old `/run/stop` and similar endpoints accept bodyless POSTs, so carrying them into a cloud route accidentally would matter. Round 2 required cross-origin control-request tests, but line 398 only tests an unauthorized request. The Compose network and unpublished ports specify the VPS case, not Fly/Railway's default public hostnames. A direct managed-host origin must not bypass the tunnel's Access check.

Proposed replacement:

> Require same-origin browser control requests and validate the WebSocket Origin against the configured dashboard origin. Use a CSRF mechanism where cookie authentication permits a cross-site request; machine-authenticated clients use a separate explicit policy. Cloud mode does not register the old global control endpoints. On Fly or Railway, run the API, supervisor, and workers in the single volume-owning deployment and expose the API only through the authenticated tunnel, or validate Access JWTs in the app on every alternate ingress. Test unauthenticated and cross-origin API, WebSocket, and export requests, IPv4/IPv6 origin reachability, and the platform's default hostname.

### S13. The bulk exporter has no authentication path, and signed downloads bypass Access after issuance

Section: Getting it onto the laptop; Security. Lines 294, 295, 342, 344.

Exact text: "The server returns a short-lived signed R2 URL to the immutable ZIP. Downloads resume."

Also: "An audit log records starts, resumes, cancellations, budget changes, and downloads."

What is wrong: The laptop CLI cannot use an email-login Access page as an API. It needs a defined login/token path or tailnet access. R2 signed URLs are bearer capabilities on the R2 S3 hostname; Access protects their issuance, not each subsequent download. The API can audit URL issuance, but cannot claim to observe every download or Range retry made directly to R2. Resuming after expiry requires obtaining a fresh URL for the same immutable object. [Cloudflare's signed URL documentation](https://developers.cloudflare.com/r2/api/s3/presigned-urls/).

Proposed replacement:

> The exporter authenticates through a documented Cloudflare Access CLI login flow or a separately scoped read-only Access service token; the Tailscale deployment uses tailnet access. It never needs the OpenRouter key or bucket write credentials. Access protects the manifest-list and URL-issuance APIs. The returned R2 URL grants temporary bearer access to one immutable object. Audit URL issuance; record completed downloads only when supported by object-store access logs. If a resumable download outlives its URL, authenticate again and request a new URL for the same object and expected hash. Test expiry and Range resumption.

### S14. Idempotent finalization must freeze pricing observations and published package contents

Section: Release 1 guarantees; On the server; Release 1 finalizer. Lines 213, 274, 285, 290, 383.

Exact text: "Finalization is its own idempotent job that runs from committed logs."

Also: "The existing `pricing_snapshot.json` keeps its current end-of-run meaning."

What is wrong: The start-of-run sidecar preserves the old snapshot's purpose, but rerunning today's `_write_pricing_snapshot_artifact` performs a fresh catalog GET. A finalizer retry can therefore overwrite a previous end-of-run observation and change a package hash. Exported ledger rows also change as upload/export status changes, so a package cannot include a live ledger view and remain immutable. The plan needs to distinguish retryable generation from new observation/version creation.

Proposed replacement:

> Freeze the first end-of-run catalog observation, including its timestamp or recorded retrieval failure, and reuse it on finalizer retries. Preserve the independent start-of-run snapshot in the job folder. Freeze the exported ledger subset at a named export revision before hashing. Upload and download status updates remain outside that immutable revision. A retry with the same committed inputs and frozen observations produces the same package manifest. Later reconciliation or analysis creates a new linked export revision rather than overwriting published evidence. Test a finalizer crash after pricing capture and another after manifest creation.

### S15. R191 did not use the proposed 400-turn cap

Section: Decisions needed from you. Line 34.

Exact text: "400 matches the frontier E0 games."

What is wrong: The saved `run/run_config.json` files show 400 for R115, R163, R166, and R172, but 600 for R191. Mini154 and Mini157 used 500, and Mini273 used 600. The proposed cap is a choice, not an exact reproduction of the whole frontier set.

Proposed replacement:

> Use 400 as the proposed full-game cap. Four of the five frontier E0 games used 400; R191 used 600. All eight saved games ended by bankruptcy between turns 115 and 273. Record the selected cap in the execution contract.

### S16. The latency paragraph mistakes a gap between calls for a stalled call

Section: What the code does today; Measured workload / Time. Lines 54, 85.

Exact text: "R166 and R172 spanned 15.5 and 8.9 hours because of single stalled calls or laptop sleep."

Also: "Median call latency was 9 to 12 seconds. GPT-5.5 had a median of 13 to 38 seconds, and the 95th percentile across all calls was 38 to 81 seconds."

What is wrong: R172's summed recorded request latency is 3.5126 hours, its largest recorded attempt is only 138.151 seconds, and it contains a 19,297,295 ms gap, 5.36 hours, between decisions 241 and 242. Its extra wall time is outside a recorded request. The artifacts do not establish why that gap happened. R166's 44,124,652 ms value is a resolver-attempt interval that can include transport retries and clock/sleep effects, not proof of one active provider generation. The median and p95 ranges describe the five frontier games, not all eight: Mini273's median is 7.808 seconds and mini p95 values are about 27 to 31 seconds.

Proposed replacement:

> In the five frontier games, per-game median resolver-attempt latency was about 9 to 12 seconds, GPT-5.5's median was about 13 to 38 seconds, and per-game p95 was about 38 to 81 seconds. These intervals can include transport retries. Six saved games spanned 1.3 to 4.0 hours. R166 contains a 12.26-hour recorded attempt interval. R172 has an 8.93-hour span but only 3.51 hours of recorded attempt latency. Its wall-time span contains a 5.36-hour gap between requests. Sleep, suspension, interruption, or other delays may explain these observations; the artifacts do not establish the cause. Cloud execution removes laptop sleep from the server's lifetime but does not guarantee a 3 to 4 hour finish.

### S17. The saved-package size range mixes logical bytes and allocated disk space

Section: Storage. Line 81.

Exact text: "With analysis added, a saved package is 58 to 167 MiB."

What is wrong: In `run_measurements.json`, 58.434 to 167.219 MiB comes from `du_kib / 1024`, allocated filesystem space. `logical_bytes / 2**20` gives 52.295 to 153.457 MiB. Those package totals include ancillary files, and R172 includes a 24.20 MiB archive, not only newly added analysis. The earlier core table uses logical file bytes. Mixing these units makes the storage and transfer estimate misleading.

Proposed replacement:

> The current saved directories contain 52.3 to 153.5 MiB of logical file bytes and occupy 58.4 to 167.2 MiB on the measured filesystem. Those totals include analysis and, for some runs, archives and existing ZIPs. Core `run/` plus `quality_check/` bytes average 61.85 MiB. Budget final packages and peak working disk separately, including the new cloud call records and checkpoint policy.

### S18. The 24/48-game wall times omit the final partial wave, and 48-game prices assume one roster

Section: Research integrity; Cost. Lines 93, 94, 365.

Exact text: "With 5 slots and about 3.5 hours per game, a 24-game cohort takes about 17 hours of wall time and a 48-game cohort about 34 hours, plus time for long games and stalls."

What is wrong: `N * 3.5 / 5` gives aggregate-work lower bounds of 16.8 and 33.6 hours. If each game takes 3.5 hours, the scheduler needs `ceil(N/5)` waves: 17.5 and 35 hours. Variable lengths and serialized finalization can add more. Also, the 48-game monetary total applies the requested roster's mean 48 times. The provisional paper design has two rosters; the second roster has not been specified here, so this is not a price estimate for that two-roster design.

Proposed replacement:

> If every game takes 3.5 hours and five run at once, 24 games require five waves, about 17.5 hours, and 48 require ten waves, about 35 hours. Uneven game lengths, stalls, and finalization can extend this. The 24- and 48-game cost columns repeat the requested roster's historical-token scenario; they do not price an unspecified second roster or authorize a campaign.

### S19. Preflight and smoke-test prices are unsupported promises

Section: Rollout. Lines 420, 421.

Exact text: "It costs well under $1."

Also: "Run one short paid exploratory game, declared as a smoke test with a 30-turn cap. Expect about $1 to $3."

What is wrong: The new preflight is not implemented or measured, and these requests have no fixed output-token cap. Thirty turns are not a fixed fraction of total decisions or model tokens. The stated $1 to $3 range does not cover the alternate GPT price scenario on the same naive turn extrapolation, and neither projection is a spending bound. The smoke's earlier engine end is an explicit experimental setting change and must not be counted as a full-game timing sample.

Proposed replacement:

> Run the new four-route preflight within the separately approved validation allowance and record its actual cost. Then run one exploratory smoke game with a declared 30-turn cap and its own soft spending threshold. Label it as a smoke test, exclude it from full-game outcome and duration estimates, and test that it reports its actual termination reason. Treat both validation costs as unmeasured until the responses arrive; neither a short prompt nor a turn cap guarantees a dollar maximum.

### S20. Base-provider validation does not establish the exact standard-price endpoint

Section: Models and routing; Spending controls. Lines 105, 107, 113, 251.

Exact text: "The plan pins each seat with `only: [<standard route>]` and `allow_fallbacks: false`. The billing guard then checks every response's returned model and provider."

What is wrong: The preceding base-slug qualifier is retained, but the implementation still treats the base pin like one endpoint for cost bounds. The saved Grok catalog includes `xai/zdr/us` at $2.20/$6.60 as well as `xai` and `xai/zdr` at $2/$6. Base `xai` can match variants and regions, and returned provider `xAI` alone does not identify the region or tier. The guard cannot detect every endpoint-price mismatch using only model and provider strings. [OpenRouter base-slug matching](https://openrouter.ai/docs/guides/routing/provider-selection#base-slug-matching).

Proposed replacement:

> Treat each base provider pin as an allowed endpoint family, not proof of one immutable region, tier, or price. Save the eligible endpoint set at launch and record returned endpoint/tier metadata whenever OpenRouter exposes it. Validate the identities that the response actually supplies; mark finer endpoint identity as unknown when absent. Use the highest applicable price and output bound among eligible endpoints for unresolved exposure, including context-price overrides. Keep the standard-route cost table as a scenario, and do not claim that a provider-name check proves the quoted endpoint price.

### S21. Budget stopping and recoverability disagree in the status definitions

Section: Jobs and states; Spending controls; interruption table. Lines 181, 186, 221, 250, 317.

Exact text: "`paused` | Stopped at a safe boundary for a named reason: budget, account error, provider outage, storage, or operator."

Also: "A game that crosses its soft cap stops at a decision boundary with status `budget_exhausted`."

What is wrong: The same budget event has two statuses. The plan also saves an invalid response and stops with its decision pending, but does not say whether Resume can continue that known response's corrective stage. Ordinary pause can retain it in memory; restarting a worker with a known response is explicitly a Release 1 technical failure. The UI must not offer a resume action that depends on Release 2 response reuse. Finalization/upload failure also needs to retain the engine outcome rather than changing it to an unfinished game.

Proposed replacement:

> Use `budget_exhausted` for the declared per-game or batch stopping threshold. Use `paused` for recoverable account, transient admission, outage, storage, or operator conditions, with a machine-readable reason and allowed transitions. Resume never raises a budget. A threshold-stopped game needs a recorded budget amendment and a supported saved-stage continuation path; otherwise it remains stopped in Release 1. If a process restart would require unsupported saved-response reuse, report a technical failure. Finalization or upload retry preserves the recorded engine outcome and its separate replay and export statuses. Test every allowed transition and every disabled Resume action.

### S22. The plan treats cloud execution as neutral despite its new execution policies

Section: Research integrity and the campaign. Line 349.

Exact text: "The cloud server is a place to execute games. It is not a new experimental treatment."

What is wrong: Hosting alone need not be a treatment, but this release changes deadlines, interruption repeats, outage/fallback behavior, concurrency, and replacement rules. Those can change the selected actions, surviving sample, or provider behavior. Calling the entire change neutral overstates what prompt-preservation and deterministic replay prove.

Proposed replacement:

> Hosting location is operational metadata. The execution-policy version records changes to deadlines, interruptions, outages, concurrency, and replacements because those policies can affect the observed games. Prompt-preservation and replay tests check specific invariants; they do not establish equivalence between historical E0 runs and runs under the new execution policy. Keep those cohorts distinguishable in analysis.

### S23. A free API deploy is conditional on compatible shared storage contracts

Section: Architecture. Line 142.

Exact text: "A deploy that changes only the API never touches running games."

What is wrong: The API shares SQLite and artifact formats with active workers. An API-only schema migration or incompatible live-envelope/artifact reader can still disrupt active jobs without restarting their processes. The draft promises this property without a compatibility rule. Similarly, a saved image digest is not useful for later restore if the image has been garbage-collected.

Proposed replacement:

> An API-only deploy leaves workers running when its ledger migrations and artifact readers remain compatible with the active worker version. Destructive or incompatible shared-schema changes require a drain. Record schema versions and test the old worker with the new API. Retain every referenced worker image in an independent registry or verified archive for the recovery retention period; a digest alone does not preserve its bytes.

### S24. The plan's measurements and catalog evidence exist only in a temporary directory

Section: Opening provenance. Line 5.

Exact text: "Working notes are in `/tmp/mb-cloud-plan/` (`claude_r1.md`, `astra_r1.md`, `astra_r2.md`, `run_measurements.json`, and the public catalog snapshots)."

What is wrong: The final canonical plan depends on workload calculations and dated price/model evidence that will disappear with temporary-file cleanup. The repository instructions call for durable research artifacts. The two screenshot references also have no stable location for an implementer who did not see the original conversation.

Proposed replacement:

> Archive the measurement JSON, its computation method, dated public catalog/pricing evidence, and review notes under `docs/research_raw/cloud_runner_2026-10-24/` or an explicitly named external archive before publishing this plan. Record source URLs, retrieval times, and hashes. Link the supplied dashboard and modal reference images from a durable design-reference location. Keep the canonical plan concise and link to that evidence.

This is a requested author change, not an action taken by this read-only review.

### S25. Completed cards omit the game outcome, and stopped cards omit the reason

Section: All games page. Lines 313 to 317.

Exact text: "The game name, run ID, a status label with a colored dot, and an Exploratory or Campaign badge."

Also: "The replay verdict and the export status, shown separately."

What is wrong: The proposed card never displays the winner or engine termination reason, although the ledger records game outcome separately. A completed 30-turn smoke test and a bankruptcy win can therefore look equivalent. A generic paused/failed label also does not explain whether the user should fix credentials, increase a budget, or wait for a provider. The round-1 dashboard sketch included the winner.

Proposed replacement:

> Finished cards show the server-reported winner, when present, and termination reason, such as bankruptcy or turn cap. Paused and failed cards show the operational reason and a link to any replacement. Keep those fields separate from replay validity and export readiness. The server supplies the outcome and allowed actions; the card does not infer a winner from cash or property values. Test a bankruptcy win, turn-cap smoke test, budget stop, and technical failure.

### S26. Fsync of new JSONL files also needs durable directory creation

Section: Release 1 guarantees. Line 207.

Exact text: "Every JSONL append is followed by fsync. JSON files are written to a temp file, fsynced, renamed, and then the parent directory is fsynced."

What is wrong: The directory fsync requirement only appears for JSON replacement. When a new JSONL file or an artifact directory is created, fsync of the file alone does not establish durability of its directory entry. SQLite can then durably reference a file that is missing after a power failure. The committed-file guarantee depends on creation as well as append durability.

Proposed replacement:

> Fsync each appended JSONL file before committing its offsets. On first creation of a file or directory, also fsync the directory entries needed to reach it from the existing durable data root. For JSON replacement, fsync the temporary file, rename it, and fsync the parent directory. Publish the SQLite commit only after these operations succeed. Test initial file/directory creation and rename boundaries in the VM reset or storage-fault tests.

## Minor

### M1. Correct the misdirected references and ambiguous filenames

Section: What the code does today; Release 1 guarantees; model-config implementation row. Lines 11, 40, 41, 44, 52, 56, 59, 213, 376.

Exact references and proposed corrections:

- `run_manager.py:73` points at the same-run idempotency return. Use `python/apps/api/src/monopoly_api/run_manager.py:77` for stopping a different active run. Replace "starting a second game stops the first" with "starting a different run stops the active run; repeating the same configuration while it is active returns its existing run ID."
- `llm_runner.py:195` is blank. The no-pending-decision rejection is at `python/packages/arena/src/monopoly_arena/llm_runner.py:189`.
- `apps/api/tests/test_llm_runner.py:41` lacks the repository's `python/` prefix. Use `python/apps/api/tests/test_llm_runner.py:41`.
- `openrouter_client.py:416` is the helper used by GET error handling. The production non-streaming completion path classifies 402 at `python/packages/arena/src/monopoly_arena/openrouter_client.py:110`, with the `http_4xx` assignment at line 119. Cite that path for the fallback claim.
- For the literal `concurrency_effective` assignment, use `python/packages/arena/src/monopoly_arena/long_campaign.py:440`; line 438 is the beginning of the nearby sequential-execution fields.
- `LiveBenchPage.tsx:43` supports the WebSocket effect; cite `frontend/src/pages/LiveBenchPage.tsx:91` for the 2.5-second poll.
- Qualify `llm_runner.py` and `player_config.py` as arena files. The API has same-named compatibility wrappers that do not contain the cited implementation.
- `config/players.json` is not a root path. Use `python/apps/api/src/monopoly_api/config/players.json` in the implementation table. The lockfiles are `python/uv.lock` and `frontend/package-lock.json`.

### M2. The current run-card label is not "replay-verified"

Section: Jobs and states. Line 189.

Exact text: "Today a run card counts as replay-verified when `replay_report.json` exists."

What is wrong: `frontend/src/pages/RunsPage.tsx:77` to line 88 uses report existence to choose `split replay`, `legacy replay`, or `partial`. It uses success styling for the two split reports, but does not label a legacy report's mere presence as verified. The proposed verdict-based improvement is justified; the description of today's UI is inaccurate.

Proposed replacement:

> Today the cards choose `split replay`, `legacy replay`, or `partial` from report-file existence, and use success styling when both split reports exist. They do not read the verdict. New cards read and display the state and artifact replay verdicts from the report contents.

### M3. Transport failure produces a fallback outcome in the resolver; the runner applies it

Section: What the code does today. Line 52.

Exact text: "When a call fails after transport retries, `decision_resolver.py:268` applies a deterministic fallback action."

What is wrong: The resolver constructs and returns a fallback outcome. `LlmRunner` applies its action through the engine at line 335. The distinction matters in a plan that must intercept account errors and route mismatches before state mutation.

Proposed replacement:

> After transport retries fail, `decision_resolver.py:268` returns a deterministic fallback outcome. `LlmRunner` then asks the engine to apply it at `llm_runner.py:335`.

### M4. Clarify exactly what is absent before a response arrives

Section: What the code does today. Line 46.

Exact text: "A crash before the response arrives leaves no prompt files at all, because they are written when the resolver builds its outcome."

What is wrong: Standalone files for the pending resolution can be absent, but `decision_started` already records the initial prompt messages/payload before the POST at `decision_resolver.py:198`. Earlier completed decisions' prompt files also remain. A corrective request can have the initial quality response already written. The new exact wire-intent records are still needed, but the current statement overgeneralizes the lost evidence.

Proposed replacement:

> A crash during the initial request can leave no standalone prompt or quality files for that pending resolution. `decisions.jsonl` can still contain its initial `decision_started` prompt payload. A crash during a corrective request can leave the initial quality files but no complete prompt-artifact set or durable corrective-stage state. Persist exact physical-request intent before each POST.

### M5. Qualify the hosting price examples and distinguish database from file storage

Section: Hosting; Pieces we are not using. Lines 152 to 166.

Exact text: "About $23 a month at 2 GB average RAM, about $43 at 4 GB."

Also: "Supabase's free plan pauses on inactivity and stores 500 MB."

What is wrong: The Railway arithmetic is $20 RAM + $2 CPU + $0.75 disk = $22.75 only with the round-2 assumptions of 0.1 average vCPU and 5 GB of actual volume usage. Those assumptions were dropped. Fly's quoted $28.39/$52.39 values are low-price-region compute-plus-volume estimates, not all-in quotes. Supabase's 500 MB is database storage; its free file-storage allowance is 1 GB. "Downloading everything is free" should say no R2 internet-egress charge, since requests can exceed free allowances. [Railway pricing](https://docs.railway.com/pricing/plans), [Fly pricing](https://docs.fly.io/about/pricing/), [Supabase pricing](https://supabase.com/pricing), [R2 pricing](https://developers.cloudflare.com/r2/pricing/).

Proposed replacements:

> Railway's example assumes 0.1 average vCPU and 5 GB of actual volume storage: about $22.75 at 2 GB average RAM, or $42.75 at 4 GB, before egress. These are usage scenarios, not a measured bill.

> Fly's example uses a lowest-priced region and includes compute plus a 20 GB volume, before snapshot, egress, and other charges.

> Supabase Free includes a 500 MB database and 1 GB of file storage, with project pausing after a week of inactivity.

> R2 does not charge for internet egress. Storage and request charges still apply beyond the free allowances.

### M6. The cost scenarios need their token-accounting assumptions and missing usage disclosed

Section: Cost. Lines 89, 93 to 96.

Exact text: "We kept each lab's historical token totals from the five frontier games and applied the new prices."

What is wrong: The arithmetic uses reported prompt and completion totals at the standard token prices, without applying cache discounts or separately adding reasoning tokens. Readers need the formula to reproduce it. R191 has one attempt without usage, so the inputs are not complete measured billing for every call.

Proposed replacement:

> For each lab, multiply recorded prompt tokens by the proposed input price and recorded completion tokens by the output price, then divide by one million. Do not add reasoning tokens again or apply cache discounts in this scenario. Preserve the providers' original usage fields for later analysis. R191 contains one attempt without usage, so these inputs omit any unreported tokens or charges. The five-game means are $11.410428 and $28.8645496; the GPT seat contributes about 38.2% and 75.6%, respectively.

### M7. The determinism test must hold the original run ID constant

Section: Determinism; tests. Lines 199, 393.

Exact text: "all with the same scripted responses."

What is wrong: The proposed random new run IDs differ across executions. The engine embeds the run ID in decision IDs at `engine.py:1324`, and prompts include the decision ID at `prompting.py:601`. Baseline randomness also uses it. The existing full artifact replay comparison does not erase those differences. The test cannot promise identical canonical actions/events merely from the same responses and seed.

Proposed replacement:

> Run each comparison in an isolated output root with the same engine run ID, seed, identities, settings, and scripted response sequence. Give the jobs different cloud job IDs. Assert identical canonical events/actions and exact initial/corrective payloads. Test collision prevention separately; do not remove run IDs from the production replay comparison to make the test pass.

### M8. Replace the remaining vague or compressed prose

Section: Several sections. Exact excerpts and replacements follow.

- Line 42, "Five games could share one asyncio loop, but should not." This states a judgment before its mechanism. Replace with: "Use separate worker processes because synchronous finalization in a shared asyncio loop would delay the other games."
- Line 49, "Missing wire files are ignored." The code ignores write failures, not an inventory of missing files. Replace with: "The quality-artifact writer catches `OSError` and lets the decision continue."
- Line 156, "We chose the VPS for control over restarts, not because it gives the lowest invoice." Replace with: "The VPS lets an API deploy leave workers running and lets the supervisor drain games before a worker update. Choose the smaller measured-safe size to reduce its monthly cost."
- Line 195, "It pauses games at a safe boundary rather than letting the disk fill." The pronoun and proactive guarantee are unclear, especially for an unexpected ENOSPC. Replace with: "The supervisor checks a configured free-space reserve during play and pauses before the next request when the reserve is low. An unexpected write or fsync failure stops that execution and preserves the available evidence."
- Line 245, "Release 1 stacks five controls." Replace with: "Release 1 checks spending at admission and before each physical request, records uncertain charges, and uses a dedicated provider key limit."
- Line 433, "The chance is low because file writes take milliseconds against calls that take 10 to 60 seconds." There is no measured crash distribution, and disk faults, deployment, or fsync stalls need not occur uniformly in time. Replace with: "We have not measured the probability of these failures. Targeted fault tests verify the declared outcome at each write boundary."
- Line 443, "Release 1 still carries call records, the commit index, writer locks, and strict visible failure." Replace with: "Release 1 records each physical call, commits durable file offsets, excludes concurrent writers, and fails when it cannot verify recovery."
- Line 447, "account errors kept out of the fallback path." Replace with: "the worker pauses on account errors before returning a fallback outcome."

