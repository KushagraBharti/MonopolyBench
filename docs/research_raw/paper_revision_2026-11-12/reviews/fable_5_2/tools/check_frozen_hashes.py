#!/usr/bin/env python3
"""Read-only check of the frozen four-draft manifest and the baseline manifest.

Usage: python3 -I check_frozen_hashes.py <repo_root> <label> <out_json>
Only hashes files; never writes outside <out_json>.
"""
import hashlib
import json
import sys
from pathlib import Path


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    label = sys.argv[2]
    out = Path(sys.argv[3])
    rev = root / "docs/research_raw/paper_revision_2026-11-12"
    four = json.loads((rev / "four_draft_manifest.json").read_text())
    base = json.loads((rev / "baseline_manifest.json").read_text())
    report = {"label": label, "four_draft": {}, "baseline": {}}
    for name, table, prefix in (
        ("four_draft", four["files"], rev),
        ("baseline", base, root),
    ):
        missing, changed, ok = [], [], 0
        for rel, want in sorted(table.items()):
            p = prefix / rel
            if not p.is_file():
                missing.append(rel)
                continue
            if sha(p) != want:
                changed.append(rel)
            else:
                ok += 1
        report[name] = {
            "entries": len(table),
            "matching": ok,
            "missing": missing,
            "changed": changed,
        }
    report["manifest_sha256"] = {
        "four_draft_manifest.json": sha(rev / "four_draft_manifest.json"),
        "baseline_manifest.json": sha(rev / "baseline_manifest.json"),
        "CHARTER.md": sha(rev / "CHARTER.md"),
        "CROSS_REVIEW.md": sha(rev / "CROSS_REVIEW.md"),
    }
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if all(
        not report[k]["missing"] and not report[k]["changed"]
        for k in ("four_draft", "baseline")
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
