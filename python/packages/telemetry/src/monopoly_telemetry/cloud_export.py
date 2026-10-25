"""Download immutable packages without changing any existing local game."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.request import Request, urlopen
from urllib.parse import urlparse

from .export import unpack_verified
from .inventory import verify_inventory, safe_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--token", default=os.getenv("MB_EXPORT_TOKEN"))
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--campaign")
    parser.add_argument("--include-smoke", action="store_true")
    args = parser.parse_args()
    if urlparse(args.url).scheme != "https" and urlparse(args.url).hostname not in {"localhost", "127.0.0.1"}:
        parser.error("Use HTTPS for export credentials")
    if not args.token:
        parser.error("Provide MB_EXPORT_TOKEN or --token")
    headers = {"Authorization": f"Bearer {args.token}"}
    with urlopen(Request(args.url.rstrip("/")+"/api/exports", headers=headers), timeout=60) as response:
        exports = json.load(response)
    args.dest.mkdir(parents=True, exist_ok=True)
    for entry in exports:
        if args.campaign and entry.get("campaign_id") != args.campaign:
            continue
        if entry.get("job_kind") == "smoke" and not args.include_smoke:
            continue
        safe_path(entry["scope_id"])
        safe_path(entry["export_id"])
        name = entry["scope_id"] + (f"-r{entry['revision']}" if entry["scope"] == "campaign" else "")
        if entry["scope"] == "job" and entry.get("run_id"):
            run_id = safe_path(entry["run_id"])
            if entry.get("campaign_id"):
                name = safe_path(entry["campaign_id"]) + f"/{entry['cell_index']}-{run_id}"
            else:
                name = ("single/" if entry.get("job_kind") == "single" else "smoke/") + run_id
        target = args.dest / name
        if target.exists():
            verify_inventory(target)
            if json.loads((target / "storage_manifest.json").read_text())["tree_sha256"] != entry["manifest_sha256"]:
                raise ValueError(f"Existing local package differs: {target}")
            continue
        partial = args.dest / f".{entry['export_id']}.zip.partial"
        offset = partial.stat().st_size if partial.exists() else 0
        request_headers = {**headers, **({"Range": f"bytes={offset}-"} if offset else {})}
        if offset != entry["bytes"]:
            with urlopen(Request(args.url.rstrip("/")+f"/api/exports/{entry['export_id']}/download", headers=request_headers), timeout=60) as response:
                mode = "ab" if offset and response.status == 206 else "wb"
                with partial.open(mode) as handle:
                    shutil.copyfileobj(response, handle)
        with tempfile.TemporaryDirectory(dir=args.dest) as temporary:
            staging = Path(temporary) / "game"
            staging.mkdir()
            unpack_verified(partial, staging)
            manifest = verify_inventory(staging)
            if manifest["tree_sha256"] != entry["manifest_sha256"]:
                raise ValueError("Downloaded manifest differs from server inventory")
            target.parent.mkdir(parents=True, exist_ok=True)
            os.rename(staging, target)
        partial.unlink()
        print(target)


if __name__ == "__main__":
    main()
