# Saved games

The research set is 20 games from the Railway campaigns: five seed blocks, each with all four seat rotations. It is stored in two folders, and each folder's README records its integrity checks and research caveats.

- `railway-research-12-games-2026-10-25/` holds games 1–12 (seed blocks 1–3).
- `railway-research-8-games-2026-10-26/` holds games 13–20 (seed blocks 4–5).
- `frontier-*/` and `archive/` hold earlier exploratory games. Keep them separate from the research set.

## Original ZIPs for the research set

Each research folder's `storage_manifest.json` and `game-index.csv` list its server ZIPs under `archives/`: 14 for the first folder and 9 for the second. They are not in git: some exceed GitHub's 100 MB file limit, and every ZIP duplicates the extracted folders committed here. The owner keeps them outside the repository at `~/MonopolyBench-research/<folder>/archives/`, and the Railway volume still holds the server exports.

## Verifying

Run each folder's `audit/scripts/verify_collection.py` with `python/.venv/bin/python`. On a fresh clone each script checks every committed file against its `storage_manifest.json` and replays its games. Add `--archives <folder>` to also check the ZIPs against the SHA-256 values recorded in `storage_manifest.json` and `audit/download-index.json`.

The second folder's verifier also checks the combined set against the first folder: no shared jobs, runs or seeds, collection numbers 1–20 with no gaps, and five complete seed blocks.
