from __future__ import annotations

import hashlib
import json
import struct
import zipfile
from pathlib import Path


SAVED = Path(__file__).resolve().parents[2]
ANALYSIS = SAVED / "analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


errors: list[str] = []
layout = json.loads((SAVED / "saved_game_manifest.json").read_text(encoding="utf-8"))
standard = json.loads((ANALYSIS / "manifest.json").read_text(encoding="utf-8"))
research = json.loads(
    (ANALYSIS / "manifests" / "analysis_manifest.json").read_text(encoding="utf-8")
)
source = json.loads(
    (ANALYSIS / "manifests" / "source_artifact_hashes.json").read_text(encoding="utf-8")
)

actual_root_entries = sorted(path.name for path in SAVED.iterdir())
if actual_root_entries != sorted(layout["root_entries"]):
    errors.append("saved-game root entries differ from saved_game_manifest.json")

for area, inventory in source["areas"].items():
    area_root = SAVED / inventory["path"]
    tree_hash = hashlib.sha256()
    for entry in inventory["files"]:
        path = area_root / entry["path"]
        if (
            not path.exists()
            or path.stat().st_size != entry["bytes"]
            or sha256(path) != entry["sha256"]
        ):
            errors.append(f"source hash mismatch: {area}/{entry['path']}")
        tree_hash.update(
            f"{entry['path']}\0{entry['bytes']}\0{entry['sha256']}\n".encode()
        )
    if tree_hash.hexdigest() != inventory["inventory_sha256"]:
        errors.append(f"source inventory hash mismatch: {area}")

for entry in research["generated_file_hashes"]:
    path = SAVED / entry["path"]
    if (
        not path.exists()
        or path.stat().st_size != entry["bytes"]
        or sha256(path) != entry["sha256"]
    ):
        errors.append(f"analysis hash mismatch: {entry['path']}")

for name in standard["tables"]:
    path = ANALYSIS / "tables" / name
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"missing/empty table: {name}")
for name in standard["reports"]:
    path = ANALYSIS / "reports" / name
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"missing/empty report: {name}")
for name in standard["plots"]:
    path = ANALYSIS / "plots" / name
    if not path.exists() or path.stat().st_size < 24:
        errors.append(f"missing/empty plot: {name}")
        continue
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        errors.append(f"invalid PNG signature: {name}")
        continue
    width, height = struct.unpack(">II", data[16:24])
    if width < 100 or height < 100:
        errors.append(f"implausible PNG dimensions: {name} ({width}x{height})")

zip_path = SAVED / layout["layout"]["standard_analysis_zip"]
archive = layout["archive_validation"]
if sha256(zip_path) != archive["zip_sha256"]:
    errors.append("analysis zip SHA-256 differs from saved_game_manifest.json")
analysis_files = {
    path.relative_to(SAVED).as_posix(): path
    for path in ANALYSIS.rglob("*")
    if path.is_file()
}
with zipfile.ZipFile(zip_path) as bundle:
    names = [entry.filename for entry in bundle.infolist() if not entry.is_dir()]
    if bundle.testzip() is not None:
        errors.append("analysis zip CRC test failed")
    if set(names) != set(analysis_files):
        errors.append("analysis zip entry set differs from analysis/ file set")
    for name, path in analysis_files.items():
        if hashlib.sha256(bundle.read(name)).hexdigest() != sha256(path):
            errors.append(f"analysis zip content mismatch: {name}")

result = {
    "status": "pass" if not errors else "fail",
    "errors": errors,
    "source_run_files": source["areas"]["run"]["file_count"],
    "source_quality_check_files": source["areas"]["quality_check"]["file_count"],
    "standard_tables": len(standard["tables"]),
    "standard_plots": len(standard["plots"]),
    "reports": len(standard["reports"]),
    "analysis_files": len(analysis_files),
    "zip_files": len(names),
    "zip_sha256": sha256(zip_path),
}
print(json.dumps(result, indent=2))
if errors:
    raise SystemExit(1)
