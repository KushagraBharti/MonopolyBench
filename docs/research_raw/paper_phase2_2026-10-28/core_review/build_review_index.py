"""Index source entries and choose a content-blind missed-case audit sample.

This script creates inventories, not semantic judgments or independent labels.
Run from any directory; all recorded paths are relative to the repository root.
"""

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE = HERE.parent
REVIEWERS = PHASE / "reviewers"
SALT = "monopolybench-phase2-core-public-unflagged-v1"
SOURCE_HASHES = {}


def rel(path):
    return str(path.relative_to(ROOT))


def read(path):
    data = path.read_bytes()
    SOURCE_HASHES[rel(path)] = hashlib.sha256(data).hexdigest()
    return data.decode("utf-8")


def rows(path):
    return [json.loads(line) for line in read(path).splitlines() if line.strip()]


def write_rows(path, records):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))


def markdown_entries(path, prefix, game=None):
    lines = read(path).splitlines(keepends=True)
    section = "preamble"
    current = None
    result = []

    def finish(end):
        if current is None:
            return
        start, number, heading = current
        status = "historical" if "historical" in heading.lower() else "final"
        result.append({
            "catalog_id": f"{prefix}-{status}-{number:02d}",
            "source_reviewer": prefix.split("-")[0],
            "entry_status": status,
            "game": game,
            "source_file": rel(path),
            "source_start_line": start + 1,
            "source_end_line": end,
            "source_sha256": SOURCE_HASHES[rel(path)],
            "section": heading,
            "source_number": number,
            "raw_markdown": "".join(lines[start:end]),
        })

    for i, line in enumerate(lines):
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        item = re.match(r"^(\d+)\.\s", line)
        if heading:
            finish(i)
            current = None
            section = heading.group(1)
        elif item:
            finish(i)
            current = (i, int(item.group(1)), section)
    finish(len(lines))
    return result


def main():
    catalog = []
    public_path = REVIEWERS / "sonnet_public/candidates.jsonl"
    public = rows(public_path)
    for i, entry in enumerate(public, 1):
        catalog.append({
            "catalog_id": "public-" + entry["candidate_id"],
            "source_reviewer": "public",
            "entry_status": "final",
            "game": entry["game"],
            "source_file": rel(public_path),
            "source_start_line": i,
            "source_end_line": i,
            "source_sha256": SOURCE_HASHES[rel(public_path)],
            "source_entry": entry,
        })
    catalog += markdown_entries(REVIEWERS / "terra/shortlist_games_1_6.md", "terra")
    for game in range(7, 14):
        catalog += markdown_entries(
            REVIEWERS / f"astra_parallel_b/game-{game:02d}/candidates.md",
            f"b-g{game:02d}", game,
        )
    for game in range(14, 21):
        catalog += markdown_entries(
            REVIEWERS / f"astra_parallel_c/game-{game:02d}/shortlist.md",
            f"c-g{game:02d}", game,
        )
    counts = Counter((x["source_reviewer"], x["entry_status"]) for x in catalog)
    expected = {
        ("public", "final"): 441, ("terra", "final"): 8,
        ("b", "final"): 84, ("b", "historical"): 21, ("c", "final"): 60,
    }
    assert dict(counts) == expected, counts
    assert len({x["catalog_id"] for x in catalog}) == len(catalog)

    ledger_path = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"
    units = {r["decision_id"]: r for r in rows(ledger_path)}
    coverage = rows(REVIEWERS / "sonnet_public/coverage.jsonl")
    assert len(coverage) == len(units) == 6989
    assert {r["decision_id"] for r in coverage} == set(units)
    strata = defaultdict(list)
    for row in coverage:
        if not row["candidate_ids"]:
            strata[(row["game"], row["player_id"])].append(row)
    sample = []
    stratum_counts = []
    for (game, player), pool in sorted(strata.items()):
        ranked = sorted(pool, key=lambda r: hashlib.sha256(
            (SALT + "|" + r["decision_id"]).encode()).hexdigest())
        selected = ranked[:3]
        stratum_counts.append({"game": game, "player_id": player,
                               "eligible": len(pool), "selected": len(selected)})
        for rank, r in enumerate(selected, 1):
            unit = units[r["decision_id"]]
            sample.append({
                "decision_id": r["decision_id"], "game": game, "player_id": player,
                "packet": unit["packet"], "packet_line": unit["packet_line"],
                "public_source_file": r["source_file"],
                "public_source_line": r["source_line"],
                "eligible_in_stratum": len(pool), "selection_rank": rank,
                "selection_sha256": hashlib.sha256(
                    (SALT + "|" + r["decision_id"]).encode()).hexdigest(),
                "eligibility": "No candidate_ids in public-pass coverage ledger",
                "semantic_review": "pending",
            })
    assert len(sample) == len({r["decision_id"] for r in sample})
    assert len(strata) == 80
    write_rows(HERE / "candidate_catalog.jsonl", catalog)
    write_rows(HERE / "public_unflagged_sample.jsonl", sample)
    read(Path(__file__).resolve())
    manifest = {
        "schema_version": 1,
        "purpose": "Lossless source index and content-blind missed-case audit sample; not adjudication",
        "catalog_entries": len(catalog), "final_source_entries": 593,
        "historical_source_entries": 21,
        "counts": [{"reviewer": k[0], "status": k[1], "entries": v}
                   for k, v in sorted(counts.items())],
        "entry_count_warning": "Entries overlap; counts are neither unique episodes nor prevalence",
        "sampling": {
            "salt": SALT, "rule": "Lowest SHA256(salt|decision_id), up to 3 per game/player",
            "eligible_public_unflagged": sum(len(p) for p in strata.values()),
            "selected": len(sample), "strata": stratum_counts,
            "limitations": "Public-unflagged only; may appear in full-channel review. Not a prevalence estimate.",
        },
        "source_sha256": dict(sorted(SOURCE_HASHES.items())),
        "generated_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                             for name in ["candidate_catalog.jsonl", "public_unflagged_sample.jsonl"]},
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"catalog": len(catalog), "final": 593, "historical": 21,
                      "sample": len(sample), "eligible": manifest["sampling"]["eligible_public_unflagged"]}))


if __name__ == "__main__":
    main()
