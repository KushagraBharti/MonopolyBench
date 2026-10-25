# Container and Railway cloud runner

The cloud runtime uses one API, one supervisor, up to five game processes, one
finalizer, and SQLite WAL on a persistent volume. Local mode is unchanged.

## One-command local startup

Install Docker Engine/Desktop with Compose v2, clone this repository, and run
from the repository root:

```sh
docker compose up --build
```

Open **http://localhost:8000** and log in with password **`monopoly`**; no username
is needed. Docker builds the React frontend and installs the locked Python runtime;
the resulting single image runs all processes in one container. No host Python,
Node, uv, Redis, or external database is needed. The health check waits for the API.
Add `-d --wait` to start in the background and wait for a healthy container.

For real-model runs, create a root `.env` file containing
`OPENROUTER_API_KEY=your-key` before starting (or export that variable in your
shell). `.env.example` documents optional settings. Without a key the dashboard
remains usable, but preflight prevents games from starting. Configure OpenRouter
routes, credits, and BYOK before paid games as described below.

For a complete, zero-cost exercise, run:

```sh
MB_DEMO=1 docker compose up --build
```

In PowerShell, use `$env:MB_DEMO="1"; docker compose up --build`. Demo mode starts
a loopback mock gateway in the same container and queues one five-turn smoke
game automatically. Watch it complete, inspect decisions and replay reports, and
download its verified package. The demo overrides any inherited provider key and
route, cannot freeze research campaigns, and is visibly labeled in the dashboard.
The automatic game is queued once per volume, including across container restarts.

### Credentials, storage, and lifecycle

The dashboard password defaults to **`monopoly`**, including when reusing a volume
from an older build that generated a random password. Set `MB_DASHBOARD_PASSWORD`
only if you want a different password. Session and export secrets are generated
automatically and persist in `runtime_secrets.json` with mode `0600` inside the
data volume. The provider key is never written into that file. Retrieve the
current dashboard password or export token at any time:

```sh
docker compose exec monopolybench python -m monopoly_api.bootstrap --show-password
docker compose exec monopolybench python -m monopoly_api.bootstrap --show-export-token
```

Use the same `.env`/shell settings (especially `MB_DEMO` and `MB_PORT`) for later
Compose commands. To avoid repeating the demo prefix, put `MB_DEMO=1` in `.env`.
Set `MB_PORT` to change the local port; the default binds only to `127.0.0.1:8000`.
Compose explicitly allows session cookies over HTTP only for literal localhost
hosts. Remote deployments require HTTPS and use Secure cookies.

The default volume is `monopolybench-data-0` for real games and
`monopolybench-data-1` for demo games (Compose project names change that prefix).
`MB_DATA_VOLUME` can choose an existing named volume; runtime mode markers reject
sharing one volume between demo and real games. Keep ample disk space for raw
artifacts: real mode reserves 5 GB by default and pauses admission when low.

```sh
docker compose logs -f
docker compose restart
docker compose down
```

Stopping allows up to 190 seconds for workers to drain and all data survives
`down`. **Do not add `--volumes`/`-v` unless you intend to delete the saved games
and credentials.** To update, finish active games, update the checkout, then run
`docker compose up --build` again. Interrupted games require the same build
identity for automatic recovery. Back up the data volume and export games regularly.

The same image can run without Compose after `docker build -f deploy/Dockerfile
-t monopolybench:local .`; supply a volume at `/data/monopolybench`, port 8000,
credentials/key as needed, `--init`, and `--stop-timeout 190`. Compose supplies
these runtime settings for the normal one-command path. For localhost HTTP with
plain `docker run`, also set `-e MB_LOCAL_HTTP=1`.

### Networks with a private certificate authority

Normal builds need no certificate configuration. If your HTTPS proxy uses a
private CA, provide a trusted combined CA bundle through the optional build
secret override; TLS verification stays enabled:

```sh
MB_BUILD_CA=/path/to/ca-bundle.pem docker compose \
  -f compose.yaml -f deploy/compose.build-ca.yaml up --build
```

That secret is only mounted during dependency installation and is not baked into
the image. If the running service also uses that proxy, mount its CA read-only
and set `SSL_CERT_FILE` to the mounted bundle in a local Compose override.

## Railway: before the first paid run

1. Commit a reviewed, clean tree. Run `bash scripts/verify.sh` and
   `cd python/packages/microbench && uv run pytest`.
2. Create a Railway Pro service with exactly one replica and a 50 GB volume at
   `/data`. Configure daily and weekly backups and disable automatic deploys.
3. Set the variables in `.env.example` in Railway. Keep `MB_DEMO=0` and
   `MB_LOCAL_HTTP=0`. The default dashboard password is `monopoly`;
   `MB_DASHBOARD_PASSWORD` overrides it. Session and export secrets are generated
   automatically. Keep the OpenRouter key server-side.
4. Enable OpenAI and Anthropic BYOK in OpenRouter, allow same-provider credit
   fallback, and fund credits for the other seats. There is no application spend cap.
5. Generate the domain. Use HTTPS: remote session cookies are Secure.
6. Set `MB_DEPLOY_URL`, then use `scripts/deploy_railway.sh --force-interrupt`
   for the initial deployment. Subsequently also set `MB_DASHBOARD_PASSWORD`, then invoke the
   script without the override. The script refuses a dirty tree and active games.
7. Run the mock soak and redeploy/backup-restore exercises on Railway before
   paid smoke games. Run real 5–10-turn smoke games and inspect routes, costs,
   both replay reports, recovery, and a downloaded package.
8. Choose the first seed block, draw it using `scripts/research/draw_seed_cohort.py`,
   record it in the registry and the v2 campaign's `seeds`, and draw the fixed
   `execution_order_seed`. The checked-in draft intentionally has no seeds and
   cannot be frozen until the study size is chosen. Run a fresh preflight, freeze,
   then start the campaign. Each seed creates four cyclic seat assignments.

The image generates `build_info.json` from its source and lockfiles, including on
a fresh checkout without any generated host files. The deploy helper includes
the Git commit; direct builds can set `--build-arg MB_GIT_SHA=$(git rev-parse HEAD)`
(or `MB_GIT_SHA` for Compose). Without a commit, provenance uses an explicit source
fingerprint. Stale host manifests are ignored. Set
`MB_IMAGE_DIGEST` to the immutable OCI digest when your build pipeline exposes it;
otherwise the build uses an explicitly labeled `source:<sha>` identity. Recovery
requires an exact match. An actual OCI digest is needed for an image-level
provenance claim. Python is pinned to 3.12.14.

## Local zero-cost exercise

From the repository root, use the workspace Python environment:

```sh
python/.venv/bin/python scripts/cloud_soak.py --games 5 --turns 5 --interrupt
```

The harness uses a loopback mock API and dummy credentials, launches independent
worker processes, interrupts one, and verifies the exported packages. Use
`--turns 0` for uncapped games. No real provider calls are allowed in test mode.

For an interactive local dashboard, use the Docker demo above. The separate
harness is useful for fault injection and uncapped multi-game verification.

## Operations

- Account banner: fix the key or credits, then Resume all. No fallback move is
  applied for an account or transport failure.
- Provider outage: three immediate transport attempts, then a durable pause;
  retry every five minutes, up to twelve scheduled retries. Resume resets it.
- Deploy: pause the campaign, let games finish, deploy. SIGTERM stops admission
  and allows in-flight calls to finish for up to 180 seconds. Boot repairs partial
  journal writes before replay. Keep the same code/image for automatic recovery.
- Failed game: inspect the diagnostic export. One rerun uses the same seed and
  seats; the original evidence remains. Cancelled games are never auto-rerun.
- Storage pause: free space or enlarge the volume, then Resume. Never remove
  active run files. Keep backups and export regularly.
- Campaign amendment: `POST /api/campaigns/{id}/amend` with `seeds` and `reason`
  appends seed blocks without changing earlier cells.
- Campaign export: `POST /api/campaigns/{id}/export` creates a new immutable
  revision with cells, amendments, launch order, costs and available job packages.

```sh
cd python
uv run python -m monopoly_telemetry.cloud_export \
  --url https://YOUR-SERVICE.up.railway.app --dest ../saved_games \
  --campaign monopoly-long-v2-frontier-2026q4
```

The command reads `MB_EXPORT_TOKEN`, resumes partial downloads, verifies every
file and the tree hash, and never overwrites an existing game. Add `--include-smoke`
to download smoke packages. Analyze a copy of an exported game to keep the
downloaded inventory valid.

## Release acceptance on infrastructure

Local tests cannot establish Railway drain timing, actual provider compatibility,
BYOK billing, backup restoration, or memory limits. Run the five-game uncapped
mock soak on Railway, interrupt a deployment, restore a backup into a scratch
volume, then run the four-route paid preflight and simultaneous real smoke games.
Record memory, disk, finalization time, package size, and replay verdicts before
freezing paper games. No cloud service or paid request is created by this code change.
