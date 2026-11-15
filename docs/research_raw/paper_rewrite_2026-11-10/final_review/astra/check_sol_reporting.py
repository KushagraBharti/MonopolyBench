"""Retained-ledger checks for Sol's final reporting findings; no evaluations."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
RESEARCH = BASE.parent


def read_json(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


offers_path = BASE / "data/agenda_offers.json"
offers = read_json(offers_path)
threads = defaultdict(list)
for row in offers:
    threads[row["thread_id"]].append(row)
transitions = []
for thread in threads.values():
    thread.sort(key=lambda row: row["offer_seq"])
    for current, following in zip(thread, thread[1:]):
        if current["response"] != "counter_trade":
            continue
        assert following["author"] == current["recipient"]
        assert following["recipient"] == current["author"]
        transitions.append((current, following))
assert len(transitions) == 394
author_only = [pair for pair in transitions if pair[0]["completion_cell"] == "author_only"]
retained_only = [
    pair for pair in author_only
    if pair[1]["recipient_new_groups"] and not pair[1]["author_new_groups"]
]


def cash_summary(pairs):
    changes = [
        -following["net_cash_author_to_recipient"] - current["net_cash_author_to_recipient"]
        for current, following in pairs
    ]
    return {
        "n": len(changes),
        "cash_improvements": sum(value > 0 for value in changes),
        "median_cash_change": median(changes),
    }


all_summary = cash_summary(author_only)
subset_summary = cash_summary(retained_only)
assert all_summary == {"n": 111, "cash_improvements": 89, "median_cash_change": 100}
assert subset_summary == {"n": 88, "cash_improvements": 85, "median_cash_change": 125}

temporal_path = BASE / "data/agenda_temporal_rows.jsonl"
temporal = rows(temporal_path)
sample_path = RESEARCH / "paper_phase2_2026-10-28/core_review/public_unflagged_sample.jsonl"
sample = rows(sample_path)
counts = Counter((row["game"], row["player_id"]) for row in temporal)
tags = Counter(tag for row in temporal for tag in row["semantic_tags"])
missing = [row for row in temporal if not row["fields"]["private_thought"]["present"]]
assert len(temporal) == 240 and len(counts) == 80 and set(counts.values()) == {3}
assert len({row["decision_id"] for row in temporal}) == 240
assert {row["decision_id"] for row in temporal} == {row["decision_id"] for row in sample}
assert all(not row["provider_summary_semantically_coded"] for row in temporal)
assert {tag: tags[tag] for tag in ["P", "O", "R"]} == {"P": 59, "O": 36, "R": 25}
assert len(missing) == 53 and {row["model"] for row in missing} == {"anthropic/claude-opus-5.5"}

pin_path = BASE / "integrated/qa/integrated_file_hashes.json"
pins = read_json(pin_path)["files"]
mismatches = [name for name, digest in pins.items() if sha(BASE / "integrated" / name) != digest]
assert not mismatches, mismatches
sources = [
    offers_path, temporal_path, sample_path,
    RESEARCH / "paper_agenda_revision_2026-10-29/temporal/protocol.md",
    RESEARCH / "paper_phase2_2026-10-28/core_review/build_review_index.py",
]
result = {
    "scope": "Re-tabulation of retained records and source reads, not semantic recoding or engine execution.",
    "counter_transitions": len(transitions),
    "author_only_counters": all_summary,
    "retaining_only_original_author_completion": subset_summary,
    "temporal": {
        "decisions": len(temporal), "player_games": len(counts), "per_player_game": 3,
        "retained_tags": {tag: tags[tag] for tag in ["P", "O", "R"]},
        "missing_private_fields": len(missing), "missing_private_model": "Opus",
        "same_ids_as_original_sample": True, "provider_explanations_excluded": True,
        "pool_definition": "No candidate_ids in the earlier public-pass coverage ledger; full-channel overlap remains possible.",
    },
    "integrated_pin_files": len(pins), "integrated_pin_mismatches": mismatches,
    "source_sha256": {str(path.relative_to(RESEARCH)): sha(path) for path in sources},
    "script_sha256": sha(Path(__file__)),
}
(HERE / "sol_reporting_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if key not in {"source_sha256", "script_sha256"}}, indent=2))
