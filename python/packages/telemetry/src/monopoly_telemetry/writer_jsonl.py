from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=True))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    fsync_directory(path.parent)


def fsync_directory(path: Path) -> None:
    if os.name != "nt":
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def atomic_write(path: Path, data: bytes) -> None:
    missing = []
    parent = path.parent
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    path.parent.mkdir(parents=True, exist_ok=True)
    for directory in reversed(missing):
        fsync_directory(directory.parent)
    fd, name = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        fsync_directory(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_jsonl_strict(path: Path, *, allow_partial_tail: bool = False) -> list[dict[str, Any]]:
    """Parse every complete row strictly. Readers that can race an in-progress append
    may ignore an unterminated final fragment; recovery must not."""
    if not path.exists():
        return []
    data = path.read_bytes()
    if allow_partial_tail:
        data = data[:data.rfind(b"\n") + 1]
    if data and not data.endswith(b"\n"):
        raise ValueError(f"{path}: incomplete trailing record ({len(data.rsplit(bytes([10]), 1)[-1])} bytes)")
    rows = []
    for index, line in enumerate(data.splitlines(), 1):
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError(f"{path}:{index}: malformed JSON") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{index}: expected object")
        rows.append(row)
    return rows


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    """Replace a complete file only after its new bytes are durable."""
    atomic_write(path, text.encode(encoding))
