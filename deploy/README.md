# Railway cloud runner

The cloud runtime uses one API, one supervisor, up to five game processes, one
finalizer, and SQLite WAL on a persistent volume. Local mode is unchanged.

## Before the first paid run

1. Commit a reviewed, clean tree. Run `bash scripts/verify.sh` and
   `cd python/packages/microbench && uv run pytest`.
2. Create a Railway Pro service with exactly one replica and a 50 GB volume at
   `/data`. Configure daily and weekly backups and disable automatic deploys.
3. Set the variables in `.env.example` in Railway. Generate a session secret with
   `python -c 'import secrets; print(secrets.token_hex(32))'`. Use distinct long
   dashboard and export credentials. Keep the OpenRouter key server-side.
4. Enable OpenAI and Anthropic BYOK in OpenRouter, allow same-provider credit
   fallback, and fund credits for the other seats. There is no application spend cap.
5. Generate the domain. Use HTTPS: session cookies are always Secure.
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

`build_info.json` records the source commit and lockfile hashes. Set
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

For an interactive local dashboard, use an HTTPS reverse proxy to the API and
build the frontend with `VITE_MB_MODE=cloud npm run build`. Set `MB_BUILD_INFO` to
your local build manifest and `MB_DATA_DIR` to a disposable directory. Set
`MB_DISK_RESERVE_GB=0` only in disposable test environments.

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
