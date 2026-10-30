"""Archive the source-dependent agenda study, excluding the prior draft backup."""

from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "paper_agenda_revision_2026-10-29"
allowed = {".py", ".json", ".jsonl", ".md", ".tex", ".csv", ".gz", ".txt", ".bib"}
excluded = {
    "baseline",
    "build",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    "render",
}
files = sorted(
    p
    for p in SOURCE.rglob("*")
    if p.is_file()
    and p.suffix in allowed
    and not excluded.intersection(p.relative_to(SOURCE).parts)
)
manifest = {
    str(p.relative_to(SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in files
}
target = ROOT / "artifacts/research-agenda-audit.zip"
prefix = "docs/research_raw/paper_agenda_revision_2026-10-29/"
with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        info = zipfile.ZipInfo(
            prefix + str(path.relative_to(SOURCE)), date_time=(2026, 10, 29, 0, 0, 0)
        )
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, path.read_bytes())
    info = zipfile.ZipInfo(
        prefix + "archive_manifest.json", date_time=(2026, 10, 29, 0, 0, 0)
    )
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, json.dumps(manifest, indent=2) + "\n")
with zipfile.ZipFile(target) as archive:
    for name, digest in manifest.items():
        assert hashlib.sha256(archive.read(prefix + name)).hexdigest() == digest
report = {
    "files": len(files),
    "bytes": target.stat().st_size,
    "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    "source_dependent": True,
    "manifest_verified": True,
}
(ROOT / "qa/agenda_source_archive.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
