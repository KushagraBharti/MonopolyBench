from pathlib import Path
import os
import zipfile

from .inventory import verify_inventory, safe_path
from .writer_jsonl import fsync_directory


def package_zip(staging: Path, destination: Path) -> None:
    verify_inventory(staging)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".partial")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging).as_posix())
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, destination)
    fsync_directory(destination.parent)


def unpack_verified(archive: Path, staging: Path) -> None:
    with zipfile.ZipFile(archive) as handle:
        names: set[str] = set()
        for member in handle.infolist():
            name = safe_path(member.filename.rstrip("/"))
            if name in names or (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Duplicate path or symlink in archive")
            names.add(name)
            target = staging / name
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with handle.open(member) as source, target.open("xb") as dest:
                    import shutil
                    shutil.copyfileobj(source, dest)
    verify_inventory(staging)
