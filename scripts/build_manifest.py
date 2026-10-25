"""Fingerprint the build inputs without requiring Git, Node, or uv on the host."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

INPUTS = ("python", "frontend", "contracts", "campaigns", "scripts", "deploy", ".dockerignore", "compose.yaml")
EXCLUDE = {".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", ".git"}


def source_digest(root: Path) -> str:
    paths: list[Path] = []
    for name in INPUTS:
        path = root / name
        if path.is_file():
            paths.append(path)
        elif path.is_dir():
            for directory, dirs, files in os.walk(path):
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDE and not d.startswith(".env") and not d.endswith(".egg-info"))
                paths.extend(Path(directory) / f for f in files if not f.startswith(".env") and not f.endswith((".pyc", ".pyo", ".zip", ".mp4")))
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def build_manifest(root: Path, git_sha: str = "") -> dict:
    fingerprint = source_digest(root)
    # The deploy helper may supply commit provenance, but stale/legacy host
    # manifests must never identify a different set of build inputs.
    previous = root / "build_info.json"
    if not git_sha and previous.exists():
        try:
            candidate = json.loads(previous.read_text())
            if candidate.get("source_sha256") == fingerprint:
                git_sha = candidate.get("git_sha", "")
        except (ValueError, AttributeError):
            pass
    if not isinstance(git_sha, str) or git_sha and not re.fullmatch(r"[a-fA-F0-9]{40,64}", git_sha):
        git_sha = ""
    return {"git_sha": git_sha or "source:" + fingerprint,
            "image_digest": "source:" + fingerprint,
            "source_sha256": fingerprint,
            "lockfiles": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                          for name in ("python/uv.lock", "frontend/package-lock.json")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("build_info.json"))
    parser.add_argument("--git-sha", default="")
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_manifest(args.source, args.git_sha), sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
