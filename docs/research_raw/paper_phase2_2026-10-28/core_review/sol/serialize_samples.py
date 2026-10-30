"""Serialize manually authored sample judgments after original bundle reading."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def main():
    samples = [json.loads(line) for line in (HERE.parent / "public_unflagged_sample.jsonl").read_text().splitlines()]
    target = HERE / "negative_control_reviews.jsonl"
    records = [json.loads(line) for line in target.read_text().splitlines() if line.strip()]
    existing = {record["decision_id"] for record in records}
    for line in (HERE / "sample_judgments.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = [field.strip() for field in line.split("|")]
        assert len(fields) == 8, fields
        index, verdict, link, supported, new, unsupported, alternative, limits = fields
        sample = samples[int(index)]
        if sample["decision_id"] in existing:
            continue
        original = (ROOT / sample["packet"]).read_text().splitlines()[sample["packet_line"] - 1]
        unit = json.loads(original)
        records.append({
            "decision_id": sample["decision_id"], "sample_index": int(index), "game": sample["game"], "player_id": sample["player_id"],
            "reading_status": "Original semantic bundle and surrounding applied chronology read; exact repeated fields may reference previously read originals",
            "initial_verdict": verdict, "episode_linkage": link, "supported": supported, "new_candidate_or_counterexample": new,
            "unsupported": unsupported, "alternatives": alternative, "channel_limits": limits,
            "source_checks": {"packet": sample["packet"], "packet_line": sample["packet_line"], "packet_line_sha256": hashlib.sha256(original.encode()).hexdigest(), "event_ids": [event["seq"] for event in unit["canonical_event_segment"]]},
            "sample_limits": f"One of three salted-hash sampled public-unflagged decisions in stratum of {sample['eligible_in_stratum']}; full-channel overlap possible; no population prevalence estimate",
            "disposition": "Initial original-bundle judgment retained",
        })
        existing.add(sample["decision_id"])
    target.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records))
    print(f"Serialized {len(records)} actual sample judgments")


if __name__ == "__main__":
    main()
