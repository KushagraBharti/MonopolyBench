"""Portable storage_manifest_v1 integrity contract."""
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from .writer_jsonl import atomic_write


def safe_path(name: str) -> str:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or any(p in {".", ".."} for p in name.split("/")) or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError(f"Unsafe inventory path: {name}")
    return name


def tree_hash(files: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in sorted(files, key=lambda f: f["path"]):
        digest.update((entry["path"] + "\0" + entry["sha256"] + "\n").encode())
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, Any]:
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed in packages")
        if not path.is_file() or path == root / "storage_manifest.json":
            continue
        name = safe_path(path.relative_to(root).as_posix())
        files.append({"path": name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": name.split("/")[0]})
    return {"schema_version": "v1", "manifest_version": "storage_manifest_v1", "files": files, "tree_sha256": tree_hash(files)}


def write_inventory(root: Path) -> dict[str, Any]:
    manifest = inventory(root)
    atomic_write(root / "storage_manifest.json", json.dumps(manifest, sort_keys=True).encode())
    return manifest


def verify_inventory(root: Path) -> dict[str, Any]:
    manifest = json.loads((root / "storage_manifest.json").read_text())
    if manifest.get("manifest_version") != "storage_manifest_v1":
        raise ValueError("Unsupported storage manifest")
    paths = [safe_path(f["path"]) for f in manifest["files"]]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate inventory paths")
    actual = inventory(root)
    if actual != manifest:
        raise ValueError("Package inventory or tree hash mismatch")
    return manifest
