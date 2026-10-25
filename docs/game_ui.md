# Game table

The cloud game page prioritizes the board, player possessions and one activity
timeline combining public chat with engine actions. Its controls operate the cloud
job; they do not submit Monopoly
moves. The engine remains authoritative for positions, ownership, cash, buildings,
mortgages, jail, bankruptcy and outcomes.

Lab marks identify the model configured for a seat. Seat colors identify players
and property ownership, including games where several seats use the same model.
Campaign rotations therefore change lab marks without changing the seat colors.
An Anthropic mark does not prove the configured fallback model was used. Exact
model and response-condition attribution remains available in decision artifacts.
The static marks are bundled from Lobe Icons; source and license are in
`frontend/public/labs/`.

Timeline ordering follows event sequence numbers, with turn markers providing
context. Public messages, private-thought events and raw provider reasoning are
different records. Private content is disclosed explicitly rather than mixed into
public chat. Provider reasoning comes from saved decision attempts; a successful
request can have no readable reasoning or no private-thought field. Those absences
do not establish a failed decision. The full prompts, retries, validation results
and requested/returned models remain accessible through decision details.

Connection state and game lifecycle are separate. A connected socket can display
a paused, cancelled or completed game. A finished snapshot's active-player field
must not be presented as a model currently thinking. Winners come from the saved
outcome, never a client-side cash ranking.

The per-job cloud cache rejects duplicate commits, older recovery generations and
payloads from another run. Accepted snapshots and event windows are projected
together into the shared presentation store. Reconnecting or revisiting a game
hydrates its cached view; it must not mix names, deeds or messages from another job.
Incremental envelopes without a snapshot preserve the last committed board.

Run frontend regression checks with Node 22.6 or newer:

```sh
cd frontend
npm run test:ui
```

These checks are included in both verification scripts. Browser checks additionally
cover viewport fit, property inspection, panel scrolling, keyboard focus, narrow
screens, duplicate models, full games and terminal states.
