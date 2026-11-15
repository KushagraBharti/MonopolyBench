"""Cohort map, source commits, rule-source hashes and corpus counts. Read-only.

Uses saved run summaries and cloud execution manifests, `git show` of the two
run commits (reading blobs only), and counts over events/decisions files.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter

import lib

SOURCES = [
    "python/packages/engine/src/monopoly_engine/engine.py",
    "python/packages/arena/src/monopoly_arena/decision_resolver.py",
    "python/packages/arena/src/monopoly_arena/llm_runner.py",
    "python/packages/arena/src/monopoly_arena/player_config.py",
    "contracts/data/board.json",
]


def git_blob_sha(commit: str, path: str) -> str | None:
    try:
        data = subprocess.run(["git", "-C", str(lib.ROOT), "show", f"{commit}:{path}"],
                              capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    cohort = []
    commits = set()
    events = 0
    decisions_by_model = Counter()
    attempts = 0
    for g in range(1, 21):
        run = lib.ROOT / lib.game_map()[str(g)]
        summ = json.loads((run / "summary.json").read_text())
        manifest = json.loads((run.parent / "cloud/execution_manifest.json").read_text())
        sha = None
        stack = [manifest]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                for k, v in x.items():
                    if k == "git_sha" and isinstance(v, str):
                        sha = v
                    else:
                        stack.append(v)
            elif isinstance(x, list):
                stack.extend(x)
        commits.add(sha)
        win = summ["winner_player_id"]
        seats = {pid: lib.label(p["name"]) for pid, p in summ["players"].items()}
        cohort.append({
            "game": g, "seed": summ["run_config"]["seed"], "block": (g - 1) // 4 + 1,
            "rotation": (g - 1) % 4 + 1, "turns": summ["turn_count"],
            "winner": seats.get(win), "winner_seat": int(win[1:]) if win else None,
            "seats": [seats[f"p{i}"] for i in range(1, 5)],
            "source_commit": sha, "run_dir": lib.game_map()[str(g)],
        })
        with (run / "events.jsonl").open() as fh:
            events += sum(1 for _ in fh)
        for idx, z in lib.decisions(g).items():
            rz = z.get("decision_resolved")
            if rz:
                decisions_by_model[lib.label(rz.get("player_name", ""))] += 1
                attempts += len(rz.get("attempts", []))
    src = {}
    for p in SOURCES:
        here = hashlib.sha256((lib.ROOT / p).read_bytes()).hexdigest()
        src[p] = {"HEAD": here, **{c[:8]: git_blob_sha(c, p) for c in sorted(commits)}}
    head = subprocess.run(["git", "-C", str(lib.ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {
        "cohort": cohort,
        "run_commits": sorted(commits),
        "repository_head_at_build": head,
        "source_sha256": src,
        "events": events,
        "decisions": sum(decisions_by_model.values()),
        "decisions_by_model": dict(decisions_by_model),
        "attempts": attempts,
        "wins_by_model": dict(Counter(c["winner"] for c in cohort)),
        "wins_by_seat": dict(Counter(c["winner_seat"] for c in cohort)),
    }
    lib.write_json("provenance.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "cohort"}, indent=1))


if __name__ == "__main__":
    main()
