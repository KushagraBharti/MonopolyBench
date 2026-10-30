"""Check every byte named by the final manuscript ZIP manifest."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.archive) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), "Duplicate archive entries"
        assert all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts for n in names)
        manifest_name = next(n for n in names if n.endswith("/package_manifest.json"))
        prefix = manifest_name.removesuffix("package_manifest.json")
        manifest = json.loads(archive.read(manifest_name))
        assert set(names) == {prefix + n for n in manifest} | {manifest_name}
        for name, expected in manifest.items():
            assert hashlib.sha256(archive.read(prefix + name)).hexdigest() == expected, name
        for name in ("manuscript.pdf", "protected_sources.json", "README.md",
                     "artifacts/historical-claim-audit.zip", "requirements-manuscript.txt"):
            assert name in manifest, name
    print(json.dumps({"status": "pass", "files": len(names),
                      "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
