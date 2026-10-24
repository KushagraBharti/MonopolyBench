# Cloud runner plan evidence, 2026-10-24

Raw evidence behind `docs/cloud_runner_plan.md`. Files are copied unchanged from the planning session's working directory. `SHA256SUMS` lists their hashes; check them with `shasum -a 256 -c SHA256SUMS`.

| Path | What it is | Source and retrieval time (UTC-5) |
| --- | --- | --- |
| `run_measurements.json` | Per-game file counts, logical bytes, allocated bytes, decisions, attempts, provider token totals, and request spans for the eight saved games. Computed read-only from `saved_games/` at commit `c370c87c`. | Local measurement, 2026-10-24 15:09 |
| `catalog/openrouter-models.json` | Full public OpenRouter model catalog. | `GET https://openrouter.ai/api/v1/models`, 2026-10-24 15:08 |
| `catalog/selected_models.json` | Catalog entries for the four requested models. | Extracted from the catalog above |
| `catalog/*_endpoints.json` | Per-provider endpoints, prices, tiers, and supported parameters for each requested model. | `GET https://openrouter.ai/api/v1/models/<id>/endpoints`, 2026-10-24 15:09 |
| `hosting/hetzner_regular_r2.html`, `hosting/hetzner_cloud_r2.html`, `hosting/hetzner_matrix_r2.css` | Hetzner pricing pages and the stylesheet that hides the CPX "unavailable" tooltip unless a card has the `not-available` class. | `https://www.hetzner.com/cloud/regular-performance/`, `https://www.hetzner.com/cloud/`, 2026-10-24 15:21 |
| `reviews/` | Round 1 notes from Claude and Codex `gpt-6-astra`, and Astra's round 2 response and round 3 review of the plan draft. | Planning session, 2026-10-24 |
| `design_reference/` | The two screenshots supplied as layout references: a fund dashboard card grid and a 3-step create modal. | Supplied by the project owner |

All web requests were public and unauthenticated. No paid or authenticated provider calls were made.
