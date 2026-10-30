"""Record bounded, read-only source checks for the LaTeX formatting review."""

import collections
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


datasets = {}
for path in sorted((BASE / "astra/exhibits").glob("t*.csv")):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fields = reader.fieldnames
    objects = json.loads(path.with_suffix(".json").read_text())
    assert len(rows) == len(objects), path
    mismatches = []
    for row_no, (row, obj) in enumerate(zip(rows, objects), 1):
        for key in fields:
            value = obj.get(key)
            # DictWriter uses an empty string for None and stringifies lists/bools.
            expected = "" if value is None else str(value)
            if row[key] != expected:
                mismatches.append([row_no, key, row[key], expected])
    datasets[path.stem] = {
        "rows": len(rows),
        "columns": fields,
        "csv_sha256": sha(path),
        "json_sha256": sha(path.with_suffix(".json")),
        "csv_json_mismatches": mismatches,
    }

sources = [BASE / "paper_outline.md", BASE / "figures_and_tables.md",
           BASE / "astra/exhibit_captions.md", BASE / "sol/handoff.md",
           BASE / "literature_review.md", *BASE.rglob("*.bib")]
result = {
    "scope": "Existing source/dataset consistency only; no new scientific claims.",
    "datasets": datasets,
    "total_dataset_rows": sum(d["rows"] for d in datasets.values()),
    "source_sha256": {str(p.relative_to(BASE)): sha(p) for p in sources if p.exists()},
}
out = HERE / "source_baseline.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
