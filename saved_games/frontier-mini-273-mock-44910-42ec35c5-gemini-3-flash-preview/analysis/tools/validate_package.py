from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1]
SAVED = ANALYSIS.parent
ZIP = SAVED / f"{SAVED.name}-analysis.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    errors: list[str] = []
    source = read_json(ANALYSIS / "manifests" / "source_artifact_hashes.json")
    generated = read_json(ANALYSIS / "manifests" / "analysis_manifest.json")
    saved_manifest = read_json(SAVED / "saved_game_manifest.json")

    source_checked = 0
    source_trees = {}
    for label, artifact_set in source["artifact_sets"].items():
        base = SAVED / artifact_set["path"]
        actual_paths = {
            path.relative_to(base).as_posix()
            for path in base.rglob("*")
            if path.is_file()
        }
        expected_paths = {
            item["relative_path"] for item in artifact_set["files"]
        }
        if actual_paths != expected_paths:
            errors.append(f"{label} source file set mismatch")
        lines = []
        for item in artifact_set["files"]:
            path = base / item["relative_path"]
            if (
                not path.is_file()
                or path.stat().st_size != item["bytes"]
                or sha256(path) != item["sha256"]
            ):
                errors.append(f"source mismatch: {label}/{item['relative_path']}")
            source_checked += 1
            lines.append(
                f"{item['relative_path']}\t{item['sha256']}\t{item['bytes']}\n"
            )
        tree = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
        source_trees[label] = tree
        if tree != artifact_set["tree_sha256"]:
            errors.append(f"{label} source tree hash mismatch")

    excluded = {item["path"] for item in generated["exclusions"]}
    expected_generated = {item["path"] for item in generated["generated_files"]}
    actual_generated = {
        path.relative_to(ANALYSIS).as_posix()
        for path in ANALYSIS.rglob("*")
        if path.is_file() and path.relative_to(ANALYSIS).as_posix() not in excluded
    }
    if actual_generated != expected_generated:
        errors.append("generated analysis file set mismatch")
    generated_lines = []
    for item in generated["generated_files"]:
        path = ANALYSIS / item["path"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256(path) != item["sha256"]
        ):
            errors.append(f"generated hash mismatch: {item['path']}")
        generated_lines.append(
            f"{item['path']}\t{item['sha256']}\t{item['bytes']}\n"
        )
    generated_tree = hashlib.sha256(
        "".join(generated_lines).encode("utf-8")
    ).hexdigest()
    if generated_tree != generated["generated_tree_sha256"]:
        errors.append("generated analysis tree hash mismatch")

    json_count = 0
    jsonl_count = 0
    csv_count = 0
    png_count = 0
    for path in ANALYSIS.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.suffix == ".json":
                read_json(path)
                json_count += 1
            elif path.suffix == ".jsonl":
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        json.loads(line)
                jsonl_count += 1
            elif path.suffix == ".csv":
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    list(csv.reader(handle))
                csv_count += 1
            elif path.suffix == ".png":
                data = path.read_bytes()
                if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
                    errors.append(f"invalid PNG: {path.relative_to(ANALYSIS)}")
                else:
                    width, height = struct.unpack(">II", data[16:24])
                    if width < 100 or height < 100:
                        errors.append(
                            f"implausible PNG dimensions: "
                            f"{path.relative_to(ANALYSIS)} {width}x{height}"
                        )
                png_count += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"parse failure {path.relative_to(ANALYSIS)}: {exc}")

    required = (
        "README.md",
        "manifests/source_artifact_hashes.json",
        "manifests/analysis_manifest.json",
        "quality/artifact_completeness.json",
        "quality/call_reconciliation.json",
        "quality/replay_verification.json",
        "quality/quality_flags.json",
        "reports/integrity_report.md",
        "tables/integrity_summary.csv",
        "expanded_metrics/summary.json",
        "expanded_metrics/expanded_metrics_report.md",
    )
    for rel in required:
        path = ANALYSIS / rel
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing required deterministic artifact: {rel}")

    standard = read_json(ANALYSIS / "manifest.json")
    for name in standard["reports"]:
        if not (ANALYSIS / "reports" / name).is_file():
            errors.append(f"missing standard report: {name}")
    for name in standard["tables"]:
        if not (ANALYSIS / "tables" / name).is_file():
            errors.append(f"missing standard table: {name}")
    for name in standard["plots"]:
        if not (ANALYSIS / "plots" / name).is_file():
            errors.append(f"missing standard plot: {name}")

    actual_root = sorted(path.name for path in SAVED.iterdir())
    if actual_root != sorted(saved_manifest["root_entries"]):
        errors.append("saved_game_manifest root entries mismatch")
    freeze = saved_manifest["source_freeze"]
    if (
        freeze["run_tree_sha256"] != source_trees.get("run")
        or freeze["quality_check_tree_sha256"]
        != source_trees.get("quality_check")
    ):
        errors.append("saved_game_manifest source freeze mismatch")

    analysis_files = {
        path.relative_to(SAVED).as_posix(): path
        for path in ANALYSIS.rglob("*")
        if path.is_file()
    }
    with zipfile.ZipFile(ZIP) as archive:
        bad = archive.testzip()
        if bad is not None:
            errors.append(f"ZIP CRC failure: {bad}")
        zip_name_list = [
            item.filename for item in archive.infolist() if not item.is_dir()
        ]
        zip_names = set(zip_name_list)
        if len(zip_name_list) != len(zip_names):
            errors.append("ZIP contains duplicate file entries")
        if zip_names != set(analysis_files):
            errors.append("ZIP entry set differs from analysis file set")
        for name, path in analysis_files.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != sha256(path):
                errors.append(f"ZIP content mismatch: {name}")
    if sha256(ZIP) != saved_manifest["zip_validation"]["sha256"]:
        errors.append("ZIP SHA-256 differs from saved_game_manifest")
    if (
        ZIP.stat().st_size != saved_manifest["zip_validation"]["bytes"]
        or len(analysis_files) != saved_manifest["zip_validation"]["file_count"]
    ):
        errors.append("ZIP size/file count differs from saved_game_manifest")

    completeness = read_json(ANALYSIS / "quality" / "artifact_completeness.json")
    calls = read_json(ANALYSIS / "quality" / "call_reconciliation.json")
    replay = read_json(ANALYSIS / "quality" / "replay_verification.json")
    flags = read_json(ANALYSIS / "quality" / "quality_flags.json")
    if completeness["status"] != "pass":
        errors.append("artifact completeness does not pass")
    if calls["status"] != "pass":
        errors.append("call reconciliation does not pass")
    if (
        replay["state_replay"]["status"] != "passed"
        or replay["artifact_replay"]["status"] != "passed"
    ):
        errors.append("replay verification does not pass")
    if flags["blocking_flags"]:
        errors.append("quality flags contain blocking entries")

    result = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "source_files_checked": source_checked,
        "source_tree_hashes": source_trees,
        "generated_files_checked": len(expected_generated),
        "generated_tree_sha256": generated_tree,
        "json_files_parsed": json_count,
        "jsonl_files_parsed": jsonl_count,
        "csv_files_parsed": csv_count,
        "png_files_checked": png_count,
        "reports_checked": len(standard["reports"]) + 1,
        "zip_files_checked": len(analysis_files),
        "zip_sha256": sha256(ZIP),
    }
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
