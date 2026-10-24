# Astra round 2 review

Prepared on 24 October 2026. I read `claude_r1.md` in full, revisited my round-one plan, and checked the relevant code and public documentation. All code paths below are relative to `/Users/kushagra/CS-Projects/MonopolyBench`. This review changes no repository files or git state and makes no authenticated or paid API calls.

## A. Release sequencing and minimum durability

Modify. I accept two releases. Release 1 can safely run exploratory games without the full execution journal if it explicitly fails on inconsistent records instead of promising recovery from every crash. My round-one requirement put too much recoverability ahead of the first exploratory batch. Integrity and recoverability are different requirements.

The action-before-events window is a visible failure under strict recovery. `python/packages/arena/src/monopoly_arena/llm_runner.py:335` applies the action, then writes the action, resolved decision, and individual events in that order. `_restore_interrupted_run` at line 141 regenerates the events from every recorded action and compares the complete canonical lists. An action with missing events fails that comparison. There is another normal failure window after all action events are written but before the next engine advance finishes. Recovery advances to the next pending decision, so its regenerated tail can exceed the saved tail. Fsync does not close either window.

For Release 1, preserve the files and mark these cases `technical_failure`. Do not remove a complete action, truncate complete events, weaken equality to a common prefix, or regenerate missing events without a separately tested repair protocol. A declared replacement run can proceed unattended within its replacement and spending limits. Keep the failed execution linked to that replacement. Release 2 should repair these windows through its journal.

I require these additions to your floor:

1. Persist a small commit record, separate from the full Release 2 journal. At a completed engine boundary, fsync the required files and then commit their byte offsets, last event sequence, action count, decision identity, snapshot path/hash, and artifact references. SQLite should use durable commits. Publish that record only after its files are durable. Include autonomous engine advances and terminal boundaries, not just model actions. This supports your proposed live reader and checkpoint uploader. A stale record after a crash may cause a visible failure in Release 1. It must never cause unverified bytes to become committed progress.
2. Add a durable intent and result record for every physical HTTP completion request, including internal transport retries. Persist the exact request payload or its immutable reference before sending, with a unique call ID, recovery epoch, decision ID, resolver stage, and transport attempt index. Save the raw response before metadata lookups, validation, or another request. These are operational sidecars, not a new engine journal. Without them, a crash can leave no prompt files at all to quarantine.
3. Make required artifact write failures stop the worker. `python/packages/arena/src/monopoly_arena/decision_resolver.py:859` currently catches `OSError` from quality-file writes and returns. Fsync in the lower writer alone will not fix this. A game can otherwise pass engine replay while silently missing wire evidence. Finalization must verify required artifact presence and cross-file references, not merely hash whatever files happen to exist.
4. Preserve retry state and account for abandoned calls. Event equality does not examine the pending decision's resolver stage or provider charges. An invalid attempt followed by an interrupted corrective request must not restart with an ordinary attempt-zero prompt. See C. Reconciliation must include orphan responses and unknown requests. `python/packages/telemetry/src/monopoly_telemetry/usage.py:32` currently counts only attempts inside `decision_resolved` rows, so moving files alone does not preserve spending totals.
5. Use an exclusive per-run writer lock in addition to the job claim. A stale heartbeat is not proof that the worker died. Recovery must verify process identity and lock ownership before replacement. Otherwise a slow or suspended worker can resume alongside its replacement and corrupt both the files and spending account.

Complete the proposed write rules. Atomic JSON replacement needs fsync of the temporary file before rename and fsync of the parent directory afterward on the target filesystem. Preserve the first-write rule for canonical turn snapshots. Quarantine trailing JSONL bytes only outside the committed offsets. Damage within committed bytes, malformed complete records, wrong record types, duplicate action IDs, and event sequence gaps must fail validation. Keep the original bytes and their hashes before any truncation.

Archive orphan files through a resumable recovery record with exact paths and hashes. A raw `decision_<pending>*` glob can match another decision's prefix and miss the compact hashed filename from `run_files.py:376`. Persist the archive plan before moving files, use a unique recovery directory, and finish an interrupted archive operation before any new request. Include both prompt and quality trees and all attempt variants.

Periodic remote checkpoints are sufficient for this release. Freeze a consistent package at a committed boundary, using fixed log offsets and immutable file versions, then upload it asynchronously. Do not zip a directory while it changes. Start with every 10 decisions or the next boundary after five minutes, plus game end and failure. This is an audit backup policy, not a five-minute recovery guarantee. Upload the job's frozen configuration and launch record before its first paid request so host loss does not erase the existence of the game. Preserve the last remote checkpoint as partial evidence after host loss.

Random process kills are useful but cannot replace targeted tests. Include the action/events gap, the gap before the next pending decision, interrupted orphan archival, fsync failures, disk full, and terminal events written before finalization starts. Use scripted LLM responses with invalid-output and transport-retry cases. Baseline-only games do not exercise the resolver. Compare recovery prompts, including corrective prompts, with uninterrupted execution. A process kill leaves the kernel page cache alive, so add a VM restart or equivalent storage fault test before claiming power-loss durability.

The existing restore method also rejects a replay with no pending decision at `llm_runner.py:195`. The new finalizer therefore needs a terminal replay path. It cannot rely on ordinary mid-game recovery or on the presence of `summary.json`.

With these changes, Release 1 can fail visibly without silently inventing a clean research record. Without the attempt records and artifact checks, your proposed floor can still yield correct engine replay with incomplete or misleading research artifacts.

## B. Spend control

Modify. I accept deferred worst-case reservations for ordinary successful requests in Release 1. Describe per-game limits as soft stopping thresholds, with a dedicated provider key as an additional spending control. I reject the unconditional claim that overshoot is limited to one provider call per running game.

`python/packages/arena/src/monopoly_arena/openrouter_client.py:105` can send three physical requests for one resolver attempt. The corrective attempt can invoke another three. Earlier timed-out requests may still run or settle at the provider after the client starts their replacements. The current client returns only the final transport result. Checking costs only after `create_chat_completion` returns misses those earlier requests. Crashes and resumed requests create the same problem.

Release 1 needs a hook before and after each physical POST. Persist actual cost or an explicit conservative pending amount before allowing the next POST. Check the game and shared totals before transport retries, corrective retries, and interruption repeats as well as ordinary decisions. Unknown charges must remain charged against admission until reconciled. Keep actual cost, estimated exposure, and unresolved calls separate. Do not insert estimates into the existing actual-only usage fields or count both an estimate and its later replacement actual.

Serialize game admission in SQLite. Count the proposed game and existing allocations, including jobs admitted but not yet running. Five tabs must not independently pass the same stale credit check. A simple allocation of approved game allowances is sufficient here. Full per-request reservation accounting can wait. Historical per-game estimates are useful planning inputs, but they do not prove that a campaign ceiling will hold. Stop new calls when the shared threshold is reached, even if each game's threshold has remaining room.

Use a dedicated key with no periodic limit reset for the first batch, no automatic replenishment, and an explicitly chosen billing mode. OpenRouter documents key caps and an estimated in-flight budget, but the latter applies only to some accounts and uses a fixed estimation cap when `max_tokens` is absent. It is not a universal provider-maximum reservation mechanism or a documented promise of zero settlement overshoot. [OpenRouter limits](https://openrouter.ai/docs/api_reference/limits)

There is a required code change at the error boundary. HTTP 402 currently becomes `http_4xx` in the client, and `decision_resolver.py:268` turns unsuccessful transport results into deterministic fallback actions. Intercept key/account budget exhaustion before that fallback path. Preserve the response body and distinguish exhausted funds from temporary in-flight admission rejection. The new contract must state whether the latter causes a bounded wait or a visible operational pause. Do not change prompts or silently lower output limits to clear it.

If a valid paid response crosses a soft threshold, the declared policy can apply that already received action and stop before another request. If an invalid response would require another paid corrective attempt, preserve it and stop while the decision is pending. Budget stopping must not fabricate a fallback action or a completed game.

The $9.44 Gemini example is only the output component of a worst-case request estimate. Input charges and route pricing also matter. I would reserve such an upper estimate for an unknown call in Release 1 when the endpoint supplies a usable bound, rather than for every successful call in advance. If the bound is unknown, stop further spending when exposure cannot be justified. A small historical average is not a conservative bound on a lost request.

This is acceptable for exploratory runs with an approved contingency. It does not establish an exact dollar maximum. Release 2 adds the full reservation ledger and reconciliation tests.

## C. Unknown in-flight responses

Modify. I accept automatic repetition under a declared, bounded interruption policy. A human need not approve every recovery. I reject resetting the resolver's retry history or treating every interrupted pending decision as a fresh ordinary attempt.

Distinguish the resolver attempt from a physical request and a recovery epoch. Keep the existing meaning of attempt 0 and corrective attempt 1. Give each replacement request a new call ID and an `after_interruption` record outside the model payload. Reissue the same saved request at the same resolver stage. If attempt 0 was invalid and the corrective request was interrupted, resend that corrective payload with its original error feedback. Do not grant another initial attempt and another corrective retry.

A reasonable proposed limit is one interruption repeat per decision and three per game, in addition to the unchanged ordinary transport policy. Freeze the chosen limits before launch, account for each unknown physical call first, and check remaining funds before repetition. Repeated crashes must eventually become a visible technical failure, not unlimited paid restarts. The supervisor must first establish that the old local writer is dead. It still cannot prove that the provider stopped the old request.

Only classify a response as unknown after examining the durable call record and any saved response. Where a generation ID exists, later authorized billing reconciliation can improve the estimate, but it must not create another completion request. No request ID and no response means unresolved exposure, not a free call.

Full response reuse may remain in Release 2. In Release 1, a recorded response that cannot yet be resumed safely can produce a technical failure and a declared replacement run. Do not discard a known response and label it unknown to invoke this policy. If the corrective stage cannot be reconstructed exactly, fail visibly instead of restarting that decision's prompting sequence.

My round-one pause recommendation was too restrictive for these exploratory games. I replace it with bounded automatic repetition for genuinely unknown requests, exact stage preservation, and explicit execution metadata. This remains a declared change to execution policy and must not silently carry into confirmatory cells.

## D. Total transport deadline

Modify. A 20-minute total deadline per physical completion request is acceptable as a proposed operational parameter. It is also a retry-policy change because it can turn a response that previously succeeded into a timeout, repeat, or fallback. Put it in the versioned execution contract for Release 1 and the new campaign contract before confirmatory work. It need not change any prompt text.

HTTPX distinguishes connection, read, write, and pool timeouts. A read timeout measures the wait for the next chunk, not the full request. Keep the existing inactivity timeouts and add a monotonic total deadline inside each physical request iteration. TCP keepalive packets alone do not constitute response-body progress; trickled HTTP body bytes can avoid a read timeout. [HTTPX timeout documentation](https://www.python-httpx.org/advanced/timeouts/)

Catch the total-deadline exception explicitly. The current catch at `openrouter_client.py:160` handles HTTPX exceptions, not necessarily the exception from an asyncio deadline wrapper. Record the outcome as a distinct total timeout, preserve whatever evidence exists, count uncertain cost, and then use the declared transport-retry path. Do not let a supervisor timeout reset the retry counter.

Three physical requests at 20 minutes can consume about one hour for a resolver stage. A subsequent corrective stage can add another hour. This deadline prevents an unbounded request, not a four-hour game guarantee. Metadata lookups also need bounded total time and must occur after raw response persistence.

At five minutes, send one stall notice based on request age or lack of committed progress, with the worker heartbeat reported separately. Non-streaming requests do not expose useful token progress to the current application. Do not restart a live worker merely because this alert fires.

The 12.3-hour observation supports a deadline, but its cause remains unknown. `_now_ms` in `decision_resolver.py:880` uses wall-clock `time.time`, and one resolver latency includes transport retries. It is not proof that one provider generation actively ran for 12.3 hours.

## E. Hosting choice and fallback order

Modify. Keep a VPS first, Fly second, and Railway third. My firm default is Hetzner CPX32 in an EU location, with 4 vCPU and 8 GB RAM, subject to actual provisioning availability. The current page's embedded price is EUR 35.99 per month before VAT. CPX22 is 2 vCPU and 4 GB at EUR 19.99. These replace my cheap-CX budget assumption. Check the selected network options and backups in the final quote. [Hetzner Regular Performance](https://www.hetzner.com/cloud/regular-performance/)

Your CPX stock conclusion is overstated. I fetched the HTML and its stylesheet. Every CPX card contains the unavailable tooltip, but the stylesheet hides it by default and exposes it on hover only for a `.cloud-matrix-product.not-available` card. The fetched CPX cards have no such class and their Create links are enabled in the markup. This does not prove account-level capacity, but the extracted tooltip text does not prove that all CPX servers are unavailable. The CX card on the main cloud page does have an explicit unavailable badge, so do not wait for CX stock. [Cloud page](https://www.hetzner.com/cloud/), [matrix stylesheet](https://www.hetzner.com/_resources/themes/hetzner/dist/cloudMatrixTableDO.css?m=1792487586)

Keep this fallback order concrete:

1. Provision the CPX32. If a five-worker load test plus one finalizer fits within 4 GB with operating-system headroom, CPX22 is the cheaper approved size for the actual deployment. Do not assume the whole stack fits below 2 GB merely because provider calls are asynchronous.
2. If Hetzner capacity, account setup, or maintenance requirements block deployment, use one Fly Machine. A shared 2-vCPU machine with 4 GB and a 20 GB volume is about $28.39 per 30 days in the lowest-priced regions. With 8 GB it is about $52.39. These are compute-plus-volume estimates before other charges. Use 4 GB only after the same memory test. [Fly pricing](https://docs.fly.io/about/pricing/)
3. Use Railway Pro if its deployment workflow is preferred or Fly is unavailable. It has a $20 monthly minimum including usage, not a $20 fixed bill for arbitrary memory. At 2 GB average RAM, 0.1 average vCPU, and 5 GB actual volume use, the published rates imply about $22.75 before egress. At 4 GB average RAM that is about $42.75. [Railway pricing](https://docs.railway.com/pricing/plans)

The deployment concern strengthens the VPS preference. Separate API and worker Compose services let an API update leave active workers alive. A worker-image update still requires a drain, and a VPS reboot still interrupts games. Fly documents downtime with one Machine and volume. Railway prevents overlapping deployments on the same volume. Disable automatic deployments during active batches and drain before platform deploys on either fallback. They can support an API process restart within the existing machine, but not an ordinary whole-machine deployment without interruption. [Fly volume behavior](https://docs.fly.io/volumes/overview), [Railway volume behavior](https://docs.railway.com/volumes/reference)

I would not claim this order is always the lowest invoice. It prioritizes controlled deployments while Release 1 has deliberately limited recovery. I saved the public Hetzner HTML and CSS evidence beside this review in `/tmp/mb-cloud-plan/hetzner_*_r2.*`.

## F. Authentication

Accept, with a deployment condition. Tunnel plus Access is the primary access control when the API listens only on loopback or a private container network, inbound application ports are closed for IPv4 and IPv6, and every published application path requires Access. Tunnel does not itself add a login policy or close a port that Docker publishes publicly. [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)

Origin JWT validation is then a second check. Keep it cheaply by enabling `cloudflared`'s documented `access.required` option with the correct team and application audience. That avoids writing a second authentication system just for Release 1. Test unauthenticated API, WebSocket, and export requests, along with cross-origin control requests. [Cloudflare origin Access settings](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/origin-parameters/#access)

Tailscale Serve is the no-domain alternative for owner devices on the tailnet. It gives a private HTTPS endpoint, not a publicly accessible site for arbitrary browsers. Use Serve, not Funnel, and restrict tailnet access to the intended owner devices. Closing the laptop does not affect the host's execution. [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)

## G. Live view from committed files

Modify. I prefer your file-tailing approach for this scale. The ledger and files can be the only durable communication path. A separate pub/sub service is unnecessary.

Use one tailer per viewed run, with bounded viewer queues and polling or local file notifications. Read only through the ledger's committed byte offset and sequence. Offsets alone are not a recovery cursor after a file changes, so track file identity and recovery generation. Reconnect clients by run ID and event sequence, then reset or backfill against a consistent committed record.

Change "latest canonical snapshot" to "the engine snapshot referenced by this commit." `run_files.py:71` preserves the first canonical snapshot for each turn and writes later states to variant files. Choosing the highest turn filename can display an old state. `python/packages/engine/src/monopoly_engine/models.py:179` also has no snapshot event-sequence field. Add the snapshot's sequence association to the job/live envelope or sidecar and update the corresponding contracts. The frontend must not reconstruct missing board state from event rules.

There is a further ordering issue at `llm_runner.py:227`. The runner can capture its current engine state while it is still yielding events from a completed engine advance. That snapshot may already reflect events the file reader has not seen. Commit the complete event batch and its corresponding engine snapshot together before exposing either. Publish a latest immutable snapshot at each chosen live commit if the existing snapshot schedule is too sparse.

This needs the small commit record in A, but not the full replay journal. The API can restart and rebuild its tailers while workers continue.

## H. Notifications

Accept. Offer an optional phone notification channel during setup and leave it disabled until the user chooses the destination. ntfy is a useful first option; an existing Discord or Slack webhook can use the same small notification adapter. Send status and an authenticated dashboard link, never prompts, response bodies, credentials, or a signed download URL.

Use a durable notification outbox, bounded retries, and a deduplication key for each status transition or stall episode. A delivery failure must not stall a game or prevent artifact completion. An ordinary ntfy topic is readable by anyone who knows its name, so use an unguessable topic or authenticated topic protection and describe that choice accurately. [ntfy publishing and topics](https://docs.ntfy.sh/publish/)

A notifier on the game host cannot report complete host loss while that host is down. Do not promise that alert without a separately configured external heartbeat monitor. No notification setup or messages are authorized by this review itself.

## I. Effort estimate

Modify. My best estimate is five focused engineering days for Release 1, with a planning range of four to six days, roughly 32 to 48 hours. This assumes one strong engineer with coding agents, existing accounts ready, reuse of the current board and artifact readers, and the visible-failure policy in A. It includes the dashboard, job/process split, attempt records, budget stops, auth, deploy, complete exports, and the targeted verification. Add elapsed time for one cloud soak and the first full game. Those games can run unattended while other review work continues.

The riskiest Release 1 item is preserving resolver stage and physical-call accounting across interruption without changing prompts or allowing two writers. The UI and VM provisioning are less uncertain. If we insist that every interrupted response or partial engine transition must resume successfully, this estimate no longer applies.

Release 2 is another seven focused engineering days, with a planning range of five to eight days, roughly 40 to 64 hours. That covers the full journal and projection repair, response reuse, remote per-decision durability, reservation reconciliation, host restore, and tests at every defined persistence boundary. The riskiest item is proving that journal repair, resolver recovery, and canonical artifact projection agree under every ordering of partial writes. Calling crash tests exhaustive should mean every enumerated protocol boundary, not every possible filesystem or hardware failure.

These are engineering estimates, not deadlines. They exclude completing the paper, a 48-game campaign, account verification delays, and scientific decisions about the second roster. I no longer require the entire combined release before any exploratory game can run.

## J. Other corrections and revisions

Modify. I retain the shared architecture and revise these claims from our first-round plans.

- Your finding 4 says recovery uses plain JSON parsing. The actual API `_read_jsonl` at `python/apps/api/src/monopoly_api/run_manager.py:960` skips malformed lines. A new strict reader must replace that path and cover validation/finalization readers as well. Plainly adding fsync will not change the reader's behavior.
- Your prompt-overwrite finding is correct and more urgent than my first-round filename description suggested. Quality requests are also written only after a response and metadata lookup at `decision_resolver.py:228`. Prompt files are written when the resolver constructs its outcome. A crash during the request can leave no attempt files, and a crash before the corrective response can leave no durable initial parsed attempt. This is why Release 1 needs request intent and immediate response persistence.
- Moving an orphan usage row is not the common current case. Usage files are generated at finalization from resolved decisions. The new execution-cost report must account for requests absent from that projection. Existing actual-only fields must retain their meaning.
- The prompt reconstruction script is useful evidence, not an existing end-to-end recovery test. Its main path at `scripts/research/prove_prompt_reconstruction.py:655` reconstructs selected saved-game prompts. Reuse its comparison helpers, but add interrupted-worker tests for both initial and corrective stages. Do not claim the script alone proves recovery equivalence.
- "Medium-effort floors" overstates the cost projections. Past token counts give scenarios, not lower bounds for different models. Higher requested effort can change strategy, game length, and retries as well as tokens per call. New games can cost less or more. Keep both OpenAI price scenarios until the user resolves the intended route and price discrepancy.
- The provider-slug statement needs one qualifier. The docs say a base slug does not by itself opt into a service tier. They also say eligible tier endpoints already in the routing pool can match a base slug. Save the intended route and observed provider metadata instead of treating every base slug as an exact immutable endpoint. [OpenRouter provider routing](https://openrouter.ai/docs/guides/routing/provider-selection#base-slug-matching)
- I withdraw my cheap CX default and my universal pause-on-unknown-response rule. I also withdraw a separate pub/sub path as a release requirement. For Release 1, remote checkpoints are evidence preservation; host-loss continuation belongs in Release 2.
- Your Railway volume figures need a wording update. The current docs call 5 GB and 50 GB default sizes, and say both paid plans can resize. Do not treat Hobby's 5 GB as a verified absolute cap. Railway also retains removed Pro deployment images for only 120 hours, so keep a reproducible image or independent registry copy for later research recovery. [Volume defaults](https://docs.railway.com/volumes/reference), [image retention](https://docs.railway.com/pricing/plans#image-retention-policy)
- Your R2 figures now have primary-source confirmation: Standard storage is $0.015 per GB-month, with 10 GB-month free, one million Class A operations free, ten million Class B operations free, and no internet egress charge. Class A and B overages are $4.50 and $0.36 per million respectively. [R2 pricing](https://developers.cloudflare.com/r2/pricing/)

Both plans must preserve every failed or replaced execution in the research ledger. A rerun does not turn its failed predecessor into a missing row. The dashboard should distinguish game completion, replay validity, analysis completion, and remote export readiness. Five games reaching some terminal status is not the same claim as five valid completed games within four hours.

## Revised decisions

- Ship Release 1 before the full journal, with strict visible failures for unrecoverable file combinations.
- Include durable physical-call records, a small committed-file index, writer exclusion, and required-artifact checks in Release 1.
- Permit bounded automatic repeats of unknown calls while preserving the resolver stage and uncertain spending.
- Treat Release 1 budget caps as stopping thresholds and handle provider budget errors outside game fallback logic.
- Version the total request deadline and interruption policy before paid launch.
- Use an available EU CPX32 by default, then Fly, then Railway. Downsize only after measuring five workers plus finalization.
- Tail committed files for live updates, use Tunnel plus Access or private Tailscale Serve, and offer opt-in notifications.
- Plan about five engineering days to the exploratory release and another seven for Release 2. Keep confirmatory cells behind the stronger execution contract and verification.
