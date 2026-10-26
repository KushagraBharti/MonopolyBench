# Saved games

- `railway-research-12-games-2026-10-25/` holds the 12 research games from the Railway campaigns: three seed blocks, each with all four seat rotations. Its README records the integrity checks and the research caveats.
- `frontier-*/` and `archive/` hold earlier exploratory games. Keep them separate from the research set.

## Original ZIPs for the research set

The research folder's `storage_manifest.json` and `game-index.csv` list 14 server ZIPs under `archives/`. They are not in git: two exceed GitHub's 100 MB file limit, and every ZIP duplicates the extracted folders committed here. The owner keeps them outside the repository at `~/MonopolyBench-research/railway-research-12-games-2026-10-25/archives/`, and the Railway volume still holds the server exports.

Run `audit/scripts/verify_collection.py` with `python/.venv/bin/python` to check the collection. On a fresh clone it checks every committed file against `storage_manifest.json` and replays all 12 games. Add `--archives <folder>` to also check the ZIPs against the SHA-256 values recorded in `storage_manifest.json` and `audit/download-index.json`.
