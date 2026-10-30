"""Check coverage and references, never infer that an original was read."""

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

from check_additional_economics import ROOT

HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def lines(path):
    return path.read_text().splitlines()


def rows(path):
    return [json.loads(line) for line in lines(path) if line.strip()]


def main():
    manifest = json.loads((HERE.parent / "manifest.json").read_text())
    catalog = rows(HERE.parent / "candidate_catalog.jsonl")
    cases = rows(HERE / "case_reviews.jsonl")
    pool = rows(HERE.parent / "public_unflagged_sample.jsonl")
    reviewed = rows(HERE / "negative_control_reviews.jsonl")
    progress = json.loads((HERE / "progress.json").read_text())
    assert len(catalog) == len(cases) == 614
    assert len(pool) == len(reviewed) == 240
    assert {r["catalog_id"] for r in cases} == {r["catalog_id"] for r in catalog}
    assert {r["decision_id"] for r in reviewed} == {r["decision_id"] for r in pool}
    assert not progress["remaining_catalog"] and not progress["remaining_sample"]
    assert len(progress["narratives_read"]) == 20
    assert all(r["reading_status"] and r["initial_verdict"] and r["episode_linkage"] for r in cases + reviewed)
    for entry in catalog:
        path = ROOT / entry["source_file"]
        assert digest(path) == entry["source_sha256"], path
        assert 1 <= entry["source_start_line"] <= entry["source_end_line"] <= len(lines(path))
    for relative, expected in manifest["source_sha256"].items():
        assert digest(ROOT / relative) == expected, relative
    for name, expected in manifest["generated_sha256"].items():
        assert digest(HERE.parent / name) == expected, name
    selection = {r["decision_id"]: (index, r) for index, r in enumerate(pool)}
    for review in reviewed:
        index, selected = selection[review["decision_id"]]
        assert review.get("sample_index", index) == index
        checks = review["source_checks"]
        assert (checks["packet"], checks["packet_line"]) == (selected["packet"], selected["packet_line"])
        line = lines(ROOT / checks["packet"])[checks["packet_line"] - 1]
        assert hashlib.sha256(line.encode()).hexdigest() == checks["packet_line_sha256"]
        unit = json.loads(line)
        assert unit["decision_id"] == review["decision_id"]
        assert checks["event_ids"] == [e["seq"] for e in unit["canonical_event_segment"]]

    missing_reports = []
    for record in cases + reviewed:
        for update in record.get("verification_updates", []):
            report = update.get("report")
            if report and not (HERE / report).exists() and not (ROOT / report).exists():
                missing_reports.append(report)
    assert not missing_reports, missing_reports
    bad_links = []
    checked_links = 0
    for path in HERE.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("http:", "https:", "t3-thread:", "#", "mailto:")):
                continue
            target = unquote(target.split("#")[0].strip("<>"))
            if not target:
                continue
            checked_links += 1
            if not (path.parent / target).exists():
                bad_links.append([path.name, target])
    assert not bad_links, bad_links
    script_digests = {digest(path): path.name for path in HERE.glob("*.py")}
    stale_reports = []
    hashed_reports = 0
    for path in HERE.glob("*.json"):
        if path.name == "review_integrity_checks.json":
            # This report is regenerated below with the current checker digest.
            continue
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "script_sha256" in data:
            hashed_reports += 1
            if data["script_sha256"] not in script_digests:
                stale_reports.append(path.name)
    assert not stale_reports, stale_reports
    report = {"catalog_entries": len(cases), "complete_common_original_records": len(reviewed),
              "trajectory_conclusions": len(progress["narratives_read"]),
              "catalog_source_hashes_match": True, "shared_manifest_hashes_match": True,
              "all_sample_original_line_hashes_and_event_ids_match": True,
              "verification_report_targets_exist": True, "markdown_local_links_checked": checked_links,
              "current_script_digest_reports_checked": hashed_reports,
              "limits": "Integrity confirms what the manually authored ledgers and files contain. It does not establish semantic reading, correctness of a verdict, independent annotation, unique episode counts or completion of the substantive research contract.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "review_integrity_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
