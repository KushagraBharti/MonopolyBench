"""Check already-read findings against source packets; never display review labels."""
import hashlib
import json
import sys
from pathlib import Path

out = Path(__file__).resolve().parent
repo = next(p for p in out.parents if (p / "contracts").is_dir())
game = int(sys.argv[1])
manifest = json.loads((out.parent.parent / "full_review" / f"game-{game:02d}" / "manifest.json").read_text())
checks = []
for index in map(int, sys.argv[2:]):
    source = manifest["sources"][index]
    packet_path = repo / source["packet"]
    raw = packet_path.read_bytes().splitlines(keepends=True)[source["packet_line"] - 1]
    packet = json.loads(raw)
    hashes = {hashlib.sha256(raw).hexdigest(), hashlib.sha256(raw.rstrip(b"\r\n")).hexdigest()}
    assert source["source_line_sha256"] in hashes
    assert packet["decision_id"] == source["decision_id"]
    row = {"index": index, "source": source, "hash_verified": True,
           "action": packet["applied_action_record"],
           "events": packet["canonical_event_segment"]}
    checks.append(row)
(out / f"game-{game:02d}" / "source_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps([{"index": c["index"], "source": c["source"], "hash_verified": True} for c in checks]))
