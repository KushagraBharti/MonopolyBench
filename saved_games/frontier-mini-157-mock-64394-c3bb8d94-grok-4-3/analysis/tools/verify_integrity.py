from __future__ import annotations

import hashlib
import json
from pathlib import Path

from monopoly_arena.replay_verification import build_replay_verification_reports
from monopoly_telemetry import build_run_files


SAVED_DIR = Path(__file__).resolve().parents[2]
RUN_DIR = SAVED_DIR / "run"
ANALYSIS_DIR = SAVED_DIR / "analysis"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def verify_source_hashes() -> dict[str, object]:
    manifest = read_json(ANALYSIS_DIR / "manifests" / "source_artifact_hashes.json")
    results: dict[str, object] = {}
    for label, artifact_set in manifest["artifact_sets"].items():
        base = SAVED_DIR / ("run" if label == "run" else "quality_check")
        expected = {
            entry["relative_path"]: (entry["bytes"], entry["sha256"])
            for entry in artifact_set["files"]
        }
        actual = {}
        for path in sorted(item for item in base.rglob("*") if item.is_file()):
            data = path.read_bytes()
            actual[path.relative_to(base).as_posix()] = (
                len(data),
                hashlib.sha256(data).hexdigest(),
            )
        results[label] = {
            "expected_count": len(expected),
            "actual_count": len(actual),
            "missing": sorted(set(expected) - set(actual)),
            "extra": sorted(set(actual) - set(expected)),
            "mismatched": sorted(
                key
                for key in set(expected) & set(actual)
                if expected[key] != actual[key]
            ),
        }
    return results


def main() -> None:
    summary = read_json(RUN_DIR / "summary.json")
    usage = read_json(RUN_DIR / "usage.json")
    attempts = read_jsonl(RUN_DIR / "usage_attempts.jsonl")
    actions = read_jsonl(RUN_DIR / "actions.jsonl")

    run_files = build_run_files(SAVED_DIR, "run", quality_base_dir=SAVED_DIR)
    run_files.run_id = summary["run_id"]
    replay = build_replay_verification_reports(run_files)
    source_hashes = verify_source_hashes()

    attempt_cost = sum(float(row.get("cost") or 0) for row in attempts)
    result = {
        "run_id": summary["run_id"],
        "state_replay_status": replay["state_replay_report"]["status"],
        "artifact_replay_status": replay["artifact_replay_report"]["status"],
        "event_count": replay["state_replay_report"]["original_event_count"],
        "action_count": len(actions),
        "attempt_count": len(attempts),
        "cost_matches": abs(attempt_cost - float(usage["totals"]["cost"])) < 1e-9,
        "source_hashes": source_hashes,
    }
    failed = (
        result["state_replay_status"] != "passed"
        or result["artifact_replay_status"] != "passed"
        or not result["cost_matches"]
        or any(
            item["missing"] or item["extra"] or item["mismatched"]
            for item in source_hashes.values()
        )
    )
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
