# Corrected benchmark treatment and audit disposition

This change defines `audit_corrected_v2`. It is a new executable treatment,
not a correction to the observations in historical saved games. Source fingerprints,
model/provider/reasoning configuration, caps, and prompt text identify new runs.
Do not pool v2 and historical results as a homogeneous experimental cohort.

## Findings 1–8: engine and observations

- Current trade offers carry their author's player ID. Legacy snapshots use the
  party opposite the most recent historical offer author, because history holds
  previous offers. Empty history falls back to the thread initiator.
- Build plans are ordered purchases. Every entry must preserve even development
  and bank inventory; interleave houses across a color group. Future hotel
  conversions cannot finance an earlier shortage of physical houses.
- No property in a developed color group can be traded, including bare siblings.
- Third failed jail rolls create a normal debt, permit financing, and move using
  the already recorded dice after payment. Birthday debts likewise offer the
  owing player financing and resume the original turn owner afterward.
- An unasked last auction bidder receives a decision when there is no high bid.
- Unmortgaged properties retain doubled unimproved monopoly rent when a sibling
  is mortgaged. Bankruptcy transfers held jail cards to the creditor, or returns
  them to their source decks for bank bankruptcy.

The retained ruleset is deliberately **not rules-complete classic Monopoly**:
creditors inherit developed properties intact without mortgage-transfer interest;
bank-returned properties become unowned without immediate auctions; voluntary
bankruptcy is surrender even if financing remains; management is generally the
active player's post-turn phase and remains restricted in jail; scarce buildings
have no competing-purchase auction. These are declared variants, not claims of
standard rules. Changing them requires another treatment version.

## Findings 9–19: policies and measurement

- Baselines do not repeatedly open empty trades. A 1,000-decision per-turn guard
  fails the run visibly instead of manufacturing a winner. Baselines are simple
  comparison policies, not economically optimal opponents.
- Both micro runners validate economic actions through reconstructed public
  engine state and the action schema. This reconstruction supports legality, not unseen decks or
  counterfactual stochastic continuation. The scorer also rejects illegal actions.
- Wording criteria are reported separately from action quality. Cash calculations
  include development, financing, and accepted trades; a proposed trade never
  counts as a realized monopoly. Bids report cash reserved, not a realized purchase.
- Eleven legacy fixtures have illegal reference actions and are quarantined by
  the microbench runner before any provider request. Suite and batch selections
  are screened in full before constructing a client; invalid selections fail
  upfront with their fixture IDs. The originals are retained;
  see `audit_quarantined_fixtures.json`. They require separately reviewed replacement
  scenarios, not retrospective changes designed to make their scores look good.
- Related-fixture comparisons explicitly lack validated causal interpretation.
  Micro campaign reports describe independent fixture aggregation, not continuous
  economic play. Existing counterfactual pairs still need controlled-difference review.
- Bankruptcy-to-bank holdings follow the actual CASH_CHANGED reason contract.
  Complete recorded runs reconcile final property counts with terminal snapshots.
- Rank means terminal net-worth rank with ties, not elimination order. Survival is
  global bankruptcy turn (or censored terminal turn), distinct from own turns played.
  Liquid net worth is cash minus mortgage principal; immediate mortgage capacity
  is separately reported. The legacy composite is labeled descriptive/unvalidated.
- Invalid-output fallback tries mortgage/building sale before bankruptcy.
- Usage v2 preserves unknown cost as null, distinguishes upstream inference cost
  from gateway charges, and adds upstream cost only for explicit BYOK or a zero
  gateway charge. Decision, player, model and run costs remain null when any
  contributing call cost is missing. Campaign statistics exclude unknown costs
  from numeric averages and report unknown counts. A separate known-cost subtotal
  preserves reported spending; monetary budget enforcement stops before the next
  game whenever an executed run has incomplete cost coverage, even below budget
  and when failure continuation is enabled. Remaining budget is then only an upper
  bound. Durable calls without resolved decisions remain
  accounted for, including interrupted/unknown calls.
  Batch leaderboards charge each model once per run even when it occupies multiple
  seats; batch cost summaries and model cards preserve unknown costs.
  Confirmed zero-call runs cost zero, so baseline-only campaigns continue across
  cells. Historical empty totals require explicit zero-attempt/complete-coverage
  evidence before being treated as zero; an absent report is still unknown.
- Campaign leaderboard inference resamples seed means, labels small block counts,
  and provides no singleton interval. Ordinary ungrouped summaries are descriptive.
  Cyclic rotation balances absolute seats, not all relative opponent positions.
  Reused seeds do not imply identical future draws after strategies diverge.
- Campaign cell identity includes resolved actor/model/provider/reasoning settings
  and game limits, while excluding budgets, preflight paths and execution controls.
  Raising a budget does not turn completed cells into new paid games.

## Findings 20–32: integrity and local recovery

- Strict replay parsing rejects malformed/non-object JSONL rows. Decision/action
  identities, order and payloads reconcile independently; extra actions after game
  end fail. State-event and full-event provenance checks remain distinct scopes.
- Completion parses required artifacts, reruns replay, checks summary versus the
  terminal event, requires the final completion marker, and verifies a complete
  inventory with file hashes and sizes. Missing inventory entries or hashes fail
  completion. Inventory includes prompts, calls, commit journals and snapshots.
  The human review queue, labels and label summary are mutable annotations outside
  this execution-integrity check, so post-hoc reviews do not invalidate a game.
- Canonical appends flush/fsync. Snapshot and JSON replacement uses a temporary
  file, fsync and atomic replacement. Quality write errors propagate.
- Each applied action has a durable commit containing the exact action, resolved
  decision and emitted events before those records are appended separately.
  Recovery restores missing committed tails idempotently and rejects contradictory
  or malformed records. It validates all planned repairs before writing, rejects
  interior gaps and unknown action/resolved-decision records, and checks run
  identity/treatment before repair. Exact committed
  turn boundaries resume without advancing ahead of saved events; pending starts
  are not logged twice. It does not guess damaged bytes or missing model decisions.
- Calls record intent, physical call ID and result before optional metadata lookup.
  The production client defaults to no hidden transport retries. Durable responses
  are reused for an identical request. Known pre-submission/auth/rate-limit
  rejections may retry on recovery with a new call ID; each earlier record remains
  intact and accounted for. An interrupted call with unknown outcome fails closed
  pending billing reconciliation. Custom clients that retry internally
  are outside this physical-call accounting guarantee.
- Conflicting prompt/response artifacts are archived by content hash. Completed
  source trajectories can re-enter finalization; a summary file alone does not
  block recovery. `completion.json` is written after required finalization stages.
- Account/transport failures fail without applying a strategic fallback. A failure
  artifact and usage accounting remain. Microbench failures also close their client
  and retain accounting for unresolved calls. Invalid model output retains one corrective
  retry and then the versioned deterministic fallback.
- Completion calls have a 120-second total deadline; generation/catalog enrichment
  in the runner has a 15-second deadline. Launch pricing is separate from final
  pricing. Provider-returned usage remains the cost source.
- Changing a model clears an inherited provider pin unless explicitly overridden.
  Preflight uses automatic tool choice as production does. Returned model/provider
  metadata remains evidence to inspect; this does not certify every external route.
- API run IDs include provider, reasoning and executable treatment. Starting an
  already recorded run is rejected before stopping another active run or appending
  any evidence, with an HTTP 400 recovery instruction; interrupted runs use recovery.
- Replay steps expose event type, sequence, actor and payload to the timeline.
  The UI also reads historical nested event envelopes without rewriting saved
  artifacts, so decision inspection, filters and review selection work for both.

Recovery is conservative, not a general cloud supervisor. Uncommitted or malformed
tails, unknown in-flight calls, concurrent writers and treatment changes require
explicit reconciliation. The tests cover append boundaries and response reuse;
they do not prove recovery from every possible OS/power/network failure.

## Findings 33–44: scope and interpretation

Railway authentication, public deployment, concurrent worker supervision, a job
ledger and multi-user access control are outside this change. The local API still
supports one active game. The UI now distinguishes stopped from engine-ended and
does not show a success badge merely because replay-report files exist.

Observations are constructed public state, not omniscient game state. General
player summaries now include bankruptcy and jail-turn count. Memory remains the
last 20 combined public timeline entries and the acting player's last 10 private
analysis entries, plus active auction/trade histories. No universal rent table or
unbounded transcript is supplied. Judge decisions from the preserved actual prompt.

Reasoning effort is provider-native; it is not equal compute across providers.
The engine seed determines transitions and replay, not provider generations.
Keyword communication flags are candidates, not validated deception/collusion.
False speech, disagreement, generated private analysis and instruction violation
are different constructs. Human calibration, independent coding and adjudication
remain research work; this patch does not claim they have occurred.

The eight heterogeneous historical games remain exploratory/regression evidence.
Their prior reported replay exceptions (R191 provenance and R166/R172 duplicate
starts), missing usage, and incomplete source hashes remain visible. No historical
run, scorecard, manuscript, or archive is rewritten. Replaying old games under v2
can diverge because the engine rules changed; use their original executable when
assessing historical replay. Unexecuted studies, power calculations, release PDFs
and supplement packages are not made complete by software repairs.

Both verification wrappers now include microbench tests and the Windows TUI typing
issue is fixed. See `audit_validation.json` for measured smoke results. New paid
campaigns still need a frozen design, eligibility/stopping/rerun rules, and a stated
unit of inference. No new campaign or Railway deployment is launched here.
