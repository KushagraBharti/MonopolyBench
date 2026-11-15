"""Package or hash-check the manuscript release; never execute benchmark code.

Run after the document and source checks. This archives static document inputs,
derived data, provenance and inspection scripts. Original game files remain in
the repository at the paths and hashes recorded in the data manifests.
"""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MANIFEST = HERE / "release_manifest.json"
ARCHIVE = HERE / "release.zip"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_paths():
    roots = {"sections", "data", "tools", "assets"}
    suffixes = {".tex", ".bib", ".pdf", ".md", ".sh"}
    selected = []
    for path in HERE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(HERE)
        if any(part in {"__pycache__", ".DS_Store"} for part in rel.parts):
            continue
        if rel.parts[0] in roots or (
            len(rel.parts) == 1
            and (path.suffix in suffixes or path.name == ".latexmkrc")
        ):
            selected.append(path)
    return sorted(selected)


def verify():
    manifest = json.loads(MANIFEST.read_text())
    failures = [
        rel for rel, expected in manifest["files"].items()
        if not (HERE / rel).is_file() or digest(HERE / rel) != expected
    ]
    if failures:
        raise SystemExit("Release hash mismatch: " + ", ".join(failures))
    print(f"Verified {len(manifest['files'])} packaged files.")


def package():
    if not (HERE / "manuscript.pdf").is_file():
        raise SystemExit("Build manuscript.pdf before packaging.")
    paths = payload_paths()
    files = {p.relative_to(HERE).as_posix(): digest(p) for p in paths}
    manifest = {
        "format": "monopolybench-manuscript-release-v1",
        "scope": "Static manuscript and retained evidence; no new evaluations.",
        "manuscript_sha256": files["manuscript.pdf"],
        "files": files,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths + [MANIFEST]:
            rel = path.relative_to(HERE).as_posix()
            item = zipfile.ZipInfo("monopolybench-paper/" + rel, (2026, 11, 14, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = (0o100755 if path.suffix == ".sh" else 0o100644) << 16
            archive.writestr(item, path.read_bytes())
    archive_hash = digest(ARCHIVE)
    (HERE / "release.sha256").write_text(archive_hash + "  release.zip\n")
    verify()
    print(f"Archive SHA-256: {archive_hash}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Check an existing extracted release.")
    args = parser.parse_args()
    verify() if args.verify else package()
