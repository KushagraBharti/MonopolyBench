from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path


SAVED_DIR = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = SAVED_DIR / "analysis"
RUN_DIR = SAVED_DIR / "run"
QUALITY_DIR = SAVED_DIR / "quality_check"
ZIP_PATH = SAVED_DIR / f"{SAVED_DIR.name}-analysis.zip"
REPO_ROOT = SAVED_DIR.parents[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def actual_files(root: Path):
    result = {}
    for path in sorted(
        (item for item in root.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        data = path.read_bytes()
        result[path.relative_to(root).as_posix()] = (len(data), sha256(data))
    return result


def check_source(errors: list[str]) -> None:
    manifest = load(ANALYSIS_DIR / "manifests" / "source_artifact_hashes.json")
    for label, root in (("run", RUN_DIR), ("quality_check", QUALITY_DIR)):
        expected = {
            row["relative_path"]: (row["bytes"], row["sha256"])
            for row in manifest["artifact_sets"][label]["files"]
        }
        actual = actual_files(root)
        if actual != expected:
            errors.append(f"{label} source inventory differs")


def check_parseability(errors: list[str]) -> None:
    for path in ANALYSIS_DIR.rglob("*.json"):
        try:
            load(path)
        except Exception as exc:
            errors.append(f"invalid JSON {path}: {exc}")
    for path in ANALYSIS_DIR.rglob("*.jsonl"):
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if line.strip():
                try:
                    json.loads(line)
                except Exception as exc:
                    errors.append(f"invalid JSONL {path}:{number}: {exc}")
    for path in ANALYSIS_DIR.rglob("*.csv"):
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                list(csv.reader(handle))
        except Exception as exc:
            errors.append(f"invalid CSV {path}: {exc}")


def check_pngs(errors: list[str]) -> None:
    for path in ANALYSIS_DIR.rglob("*.png"):
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            errors.append(f"invalid PNG signature/IHDR: {path}")
            continue
        width, height = struct.unpack(">II", data[16:24])
        if width < 100 or height < 100:
            errors.append(f"implausible PNG dimensions {width}x{height}: {path}")


def check_generated_hashes(errors: list[str]) -> None:
    manifest = load(ANALYSIS_DIR / "manifests" / "generated_output_hashes.json")
    excluded = set(manifest["excluded_self_referential_paths"])
    expected = {
        row["relative_path"]: (row["bytes"], row["sha256"])
        for row in manifest["files"]
    }
    actual = {
        rel: value
        for rel, value in actual_files(ANALYSIS_DIR).items()
        if rel not in excluded
    }
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        mismatched = sorted(
            rel
            for rel in set(expected) & set(actual)
            if expected[rel] != actual[rel]
        )
        errors.append(
            f"generated hashes differ missing={missing} extra={extra} "
            f"mismatched={mismatched}"
        )


def check_zip(errors: list[str]) -> dict:
    expected = {
        f"analysis/{rel}": path.read_bytes()
        for path in ANALYSIS_DIR.rglob("*")
        if path.is_file()
        for rel in [path.relative_to(ANALYSIS_DIR).as_posix()]
    }
    with zipfile.ZipFile(ZIP_PATH) as archive:
        bad = archive.testzip()
        if bad:
            errors.append(f"ZIP CRC failed at {bad}")
        actual_names = set(archive.namelist())
        if actual_names != set(expected):
            errors.append(
                f"ZIP entries differ missing={sorted(set(expected)-actual_names)} "
                f"extra={sorted(actual_names-set(expected))}"
            )
        for name in set(expected) & actual_names:
            if archive.read(name) != expected[name]:
                errors.append(f"ZIP bytes differ for {name}")
    return {
        "path": ZIP_PATH.name,
        "bytes": ZIP_PATH.stat().st_size,
        "sha256": sha256(ZIP_PATH.read_bytes()),
        "entry_count": len(expected),
        "crc": "pass" if not errors else "see_errors",
        "entry_content_parity": "pass" if not errors else "see_errors",
    }


def check_required(errors: list[str]) -> None:
    required = [
        "README.md",
        "manifests/source_artifact_hashes.json",
        "manifests/analysis_manifest.json",
        "manifests/generated_output_hashes.json",
        "quality/artifact_completeness.json",
        "quality/call_reconciliation.json",
        "quality/replay_verification.json",
        "quality/quality_flags.json",
        "reports/integrity_report.md",
        "tables/integrity_summary.csv",
    ]
    for rel in required:
        if not (ANALYSIS_DIR / rel).is_file():
            errors.append(f"missing required artifact {rel}")
    replay = load(ANALYSIS_DIR / "quality" / "replay_verification.json")
    if replay["replay_report"]["status"] != "state_passed_artifact_failed":
        errors.append("aggregate replay status was softened or changed")
    if replay["artifact_replay_report"]["first_mismatch_index"] != 669:
        errors.append("artifact first mismatch is not index 669")


def check_current_replay(errors: list[str]) -> None:
    for relative in (
        "python/packages/engine/src",
        "python/packages/arena/src",
        "python/packages/telemetry/src",
    ):
        path = str(REPO_ROOT / relative)
        if path not in sys.path:
            sys.path.insert(0, path)
    from monopoly_arena.replay_verification import (  # noqa: PLC0415
        build_replay_verification_reports,
    )
    from monopoly_telemetry import build_run_files  # noqa: PLC0415

    run_files = build_run_files(SAVED_DIR, "run", quality_base_dir=SAVED_DIR)
    run_files.run_id = "mock-83265-81ed4937"
    replay = build_replay_verification_reports(run_files)
    aggregate = replay["replay_report"]
    state = replay["state_replay_report"]
    artifact = replay["artifact_replay_report"]
    expected = (
        aggregate["status"] == "state_passed_artifact_failed"
        and state["status"] == "passed"
        and state["first_mismatch_index"] is None
        and artifact["status"] == "failed"
        and artifact["first_mismatch_index"] == 669
        and artifact["missing_actions"] == 0
        and artifact["extra_actions"] == 0
        and artifact["decision_id_mismatch"] is False
    )
    if not expected:
        errors.append("current in-memory replay differs from the documented result")


def main() -> None:
    errors: list[str] = []
    check_required(errors)
    check_source(errors)
    check_parseability(errors)
    check_pngs(errors)
    check_generated_hashes(errors)
    check_current_replay(errors)
    zip_result = check_zip(errors)
    manifest = load(SAVED_DIR / "saved_game_manifest.json")
    if manifest.get("analysis_zip", {}).get("sha256") != zip_result["sha256"]:
        errors.append("saved_game_manifest ZIP SHA-256 differs")
    if manifest.get("analysis_zip", {}).get("entry_count") != zip_result["entry_count"]:
        errors.append("saved_game_manifest ZIP entry count differs")
    result = {
        "status": "pass" if not errors else "fail",
        "source_hashes": "pass" if not errors else "see_errors",
        "required_artifacts": "pass" if not errors else "see_errors",
        "json_csv_png_validation": "pass" if not errors else "see_errors",
        "generated_hashes": "pass" if not errors else "see_errors",
        "current_in_memory_replay": "pass" if not errors else "see_errors",
        "zip": zip_result,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
