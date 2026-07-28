# Mechanism Case Studies

These cases are selected for mechanism diversity, not prevalence or ranking. Each separates canonical facts, reported reasoning, bounded interpretation, and unresolved counterfactuals.

ID shorthand `dec-NNNNNN` expands to `mock-3676466999-527872e4-dec-NNNNNN`. Event citations are written in full; the exhaustive path join is in `analysis/review/evidence_index.csv`.

## 1. Pink/orange consolidation through a two-counter trade (turn 10)

Facts: GPT proposed States Avenue + $100 for Tennessee at `dec-000024`; Claude countered for $160 at `dec-000025`; GPT split the difference at $130 in `dec-000026`; Claude accepted at `dec-000027`. Canonical transition `evt-000187` records acceptance, followed by cash and property transfers through `evt-000193`. Claude then held two of three pinks while GPT held Tennessee.

Reported reasoning: Claude explicitly described the pink path as cleaner because St. James split the orange group; GPT described orange upside and the risk of giving Claude 2/3 pink. This supports deliberate set-consolidation bargaining, not proof that either side's valuation was objectively correct.

Downstream fact: at turn 26, `dec-000073`–`dec-000076` swapped Virginia for Connecticut + $40, completing Claude's pink and Gemini's light-blue monopolies. Gemini's nine-house build is canonical at `mock-3676466999-527872e4-evt-000521`–`mock-3676466999-527872e4-evt-000524`. Counterfactual surplus remains oracle-gated.

## 2. The sole auction and disciplined exit (turn 35)

Facts: Grok started the Marvin Gardens auction; `evt-000681` opens it. GPT bid $201 (`dec-000102`, `evt-000686`). Claude, Gemini, and Grok dropped via `dec-000103`–`dec-000105`; `evt-000704` awards Marvin to GPT for $201. Every bidder had an explicit bid/drop legal menu.

Interpretation: this is a clean observed participation/dropout sequence. It does not establish general auction skill from one episode. The later sale of Marvin to Gemini for $80 at `dec-000211`–`dec-000212` shows that acquisition value depended on later liquidity and blocking considerations.

## 3. House-supply pressure and portfolio reshaping (turns 70–81)

Facts: GPT sold mortgaged Marvin to Gemini for $80 (`dec-000211`/`dec-000212`), then at turn 77 sold the full red set for $500 (`dec-000223`/`dec-000224`) while reporting survival pressure. At turn 81, GPT traded New York for Boardwalk + Pennsylvania Avenue (`dec-000235`/`dec-000236`), completing Gemini's orange set but leaving GPT with blockers rather than a buildable monopoly.

Interpretation: the sequence evidences a pivot from development to liquidity/blocking. Whether the pivot maximized survival or merely delayed elimination is not proved without branch replay.

## 4. Mortgage churn as a concrete capital-allocation cost (turns 85 and 118)

Facts: GPT mortgages Boardwalk and Pennsylvania at `dec-000257`/`dec-000258`, then immediately unmortgages Boardwalk at `dec-000259`, before any intervening roll. The pattern repeats at `dec-000367`–`dec-000369`. Ownership/blocking is unchanged; the only durable accounting effect is mortgage interest plus a shifted cash buffer.

Interpretation: this is a directly observed inefficiency, unlike counterfactual trade regret. Later reasoning cites near-term landing probability, but no intervening event changed it inside either sequence. The engine legally applied every action.

## 5. Transparent two-step brown consolidation under zero-house supply (turn 144)

Facts: GPT first gives Baltic+$100 for Mediterranean (`dec-000444`/`dec-000445`), then offers $80 to buy Baltic back. Gemini explicitly says this completes GPT's brown set and counters at $150; the parties settle at $120 (`dec-000446`–`dec-000449`). GPT's net cash payment is $220 and the bank has zero houses.

Communication assessment: GPT's first public message says browns are not an immediate threat, while its reported reasoning describes a long-run brown path. That statement is mechanically true under zero house supply, and the completion aim is explicit before final acceptance. This is strategic staging/selective disclosure, not an evidence-backed deception label.

## 6. Rail/dark-blue exchange loop and bankruptcy cascade (turns 122–165)

Facts: GPT bought Grok's four mortgaged railroads for $450 (`dec-000384`/`dec-000385`) and immediately sold Boardwalk to Grok for $500 (`dec-000386`/`dec-000387`), giving Grok dark-blue control. Grok later landed on Claude's States Avenue at turn 134 and declared bankruptcy at `dec-000428`; Claude inherited Park/Boardwalk. Gemini then landed on Claude's Park Place at turn 150 and declared at `dec-000465`. GPT did the same at turn 165 and declared at `dec-000487`, after which `evt-003340` ended the game with Claude as winner.

Interpretation: the asset transfers created a survivor-feedback mechanism: each bankruptcy transferred cash and deeds to Claude, enlarging the next opponent's exposure. This is a causal mechanism in the canonical event sequence, not proof that earlier trades alone caused each bankruptcy.

## 7. Reported numeric reasoning versus canonical rent

Facts: Claude repeatedly reports four-house pink rents as $925/$1,000 (for example `dec-000188`), but `mock-3676466999-527872e4-evt-002025` records $625 on States and `mock-3676466999-527872e4-evt-002349` records $700 on Virginia. After building dark blues, Claude reports four-house Park as $1,100 at `dec-000437`; the terminal prompt and `dec-000487` establish $1,300. These numbers occur in private thought, while the engine charges canonical rent.

Interpretation: private-thought numeric reliability is imperfect even in a winning trajectory. The errors do not mutate state and are not public deception, but they weaken claims that every liquidity judgment was calibrated from exact rent tables.

## 8. Duplicate start-marker reliability defect without duplicate action

Facts: `dec-000030` has two `decision_started` rows at request_start_ms 1784106556435 and 1784107243862. Its one `decision_resolved` row uses 1784107243862; there is one action row, one usage decision chain, and one event request/response/public/private quartet. Across the run there are 489 starts but 488 resolutions/actions. No other decision has a duplicate start.

Interpretation: this is a trace-marker duplication/restart artifact, not two model decisions and not a duplicate trade proposal. Counts in this review use resolved/applied decision denominators.

