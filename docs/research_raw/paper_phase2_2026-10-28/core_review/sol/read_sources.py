"""Lossless text reading aids. No annotation or inferred review status."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent.parent


def catalog(args):
    rows = [json.loads(x) for x in (BASE / "candidate_catalog.jsonl").read_text().splitlines()]
    if args.reviewer:
        rows = [x for x in rows if x["source_reviewer"] == args.reviewer]
    for row in rows[args.start:args.end]:
        print("\n", row["catalog_id"], row["entry_status"], "game", row["game"])
        if "raw_markdown" in row:
            print(row["raw_markdown"])
            continue
        entry = dict(row["source_entry"])
        # Exact source claims retained. Repetitive serialization metadata is replaced
        # by the complete canonical decision IDs; source remains authoritative.
        refs = entry.pop("decision_refs", [])
        print("DECISIONS", [(x["decision_id"].rsplit("-", 1)[-1], x.get("player_id"), x.get("turn_index"), x.get("action"), x.get("event_seq_range")) for x in refs])
        for field in ("display_numbering", "label_policy", "reviewer", "game", "candidate_id"):
            entry.pop(field, None)
        rendered = json.dumps(entry, ensure_ascii=False, indent=1)
        print(re.sub(r"campaign-[a-z0-9-]+-dec-(\d{6})", r"dec-\1", rendered))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("--reviewer")
    catalog(parser.parse_args())
