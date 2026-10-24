"""Version the executable treatment without including generated run artifacts."""
from functools import lru_cache
import hashlib
from pathlib import Path
from .paths import resolve_repo_root


@lru_cache(maxsize=1)
def treatment_fingerprint() -> str:
    root = resolve_repo_root()
    paths: list[Path] = []
    for package in ("engine", "arena"):
        paths.extend((root / "python" / "packages" / package / "src").rglob("*.py"))
    paths.extend((root / "contracts" / "schemas").glob("*.json"))
    paths.extend((root / "contracts" / "data").glob("*.json"))
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()
