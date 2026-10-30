"""Serialize manually written judgments, never generate semantic annotations.

Input columns are explicitly authored by Sol after reading each source entry:
ID | verdict | linkage | support | unsupported | alternative | counterexample | limits.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    target = HERE / "case_reviews.jsonl"
    records = [json.loads(x) for x in target.read_text().splitlines() if x.strip()]
    existing = {r["catalog_id"] for r in records}
    catalog = {r["catalog_id"]: r for r in map(json.loads, (HERE.parent / "candidate_catalog.jsonl").read_text().splitlines())}
    seen = set()
    for line in (HERE / "authored_judgments.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = [x.strip() for x in line.split("|")]
        assert len(fields) == 8, fields
        identifier, verdict, link, support, unsupported, alternative, counterexample, limits = fields
        assert identifier not in seen
        seen.add(identifier)
        if identifier in existing:
            continue
        source = catalog[identifier]
        records.append({
            "catalog_id": identifier,
            "reading_status": "catalog entry read; completed trajectory summary read",
            "initial_verdict": verdict,
            "episode_linkage": link,
            "supported": support,
            "unsupported": unsupported,
            "alternatives": alternative,
            "counterexamples": counterexample,
            "channel_limits": limits,
            "source_checks": {"original": False, "catalog_source_file": source["source_file"], "catalog_source_line": source["source_start_line"]},
            "disposition": "Initial source-level judgment retained; paper use requires original-artifact audit",
        })
    target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    progress = json.loads((HERE / "progress.json").read_text())
    progress["catalog_reviewed_ids"] = [r["catalog_id"] for r in records]
    progress["remaining_catalog_ids"] = [identifier for identifier in catalog if identifier not in progress["catalog_reviewed_ids"]]
    progress["remaining_catalog"] = len(progress["remaining_catalog_ids"])
    sample_file = HERE / "negative_control_reviews.jsonl"
    reviewed_sample = [json.loads(line)["decision_id"] for line in sample_file.read_text().splitlines() if line.strip()] if sample_file.exists() else []
    progress["sample_reviewed_ids"] = reviewed_sample
    progress["remaining_sample_ids"] = [json.loads(line)["decision_id"] for line in (HERE.parent / "public_unflagged_sample.jsonl").read_text().splitlines() if json.loads(line)["decision_id"] not in reviewed_sample]
    progress["remaining_sample"] = len(progress["remaining_sample_ids"])
    public_ids = [key for key in catalog if key.startswith("public-")]
    reviewed_ids = set(progress["catalog_reviewed_ids"])
    next_public = next((i for i, key in enumerate(public_ids) if key not in reviewed_ids), len(public_ids))
    if next_public == len(public_ids):
        progress["phase"] = "All catalog initial judgments complete; common-sample originals, further audits and synthesis remain active"
        progress["next"] = ("All 614 catalog judgments and all 240 common originals recorded. Remaining representative original audits, aggregate replications, episode linkage, debate and substantial synthesis remain active."
                            if len(reviewed_sample) == 240 else
                            f"All614catalog source judgments recorded; common sample index{len(reviewed_sample)} onward. Original audits, historical note trails, debate and synthesis remain active.")
    else:
        progress["next"] = f"Public helper offset{next_public} onward; common sample index{len(reviewed_sample)} onward. All remaining scope stays active."
    (HERE / "progress.json").write_text(json.dumps(progress, indent=2) + "\n")
    print(f"Serialized {len(records)} actual initial judgments; {progress['remaining_catalog']} remain")


if __name__ == "__main__":
    main()
