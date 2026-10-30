"""Make reversible reading copies. This prepares evidence, never review labels."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TAG = "$same_as"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pointer_key(value):
    return str(value).replace("~", "~0").replace("/", "~1")


def encode(value, minimum=120):
    """Replace exactly equal earlier subtrees with their JSON pointer."""
    seen = {}

    def visit(item, path):
        if isinstance(item, dict) and TAG in item:
            raise ValueError("Reserved reference key exists in source")
        identity = canonical(item)
        eligible = isinstance(item, (dict, list, str)) and len(identity) >= minimum
        if eligible and identity in seen:
            return {TAG: seen[identity]}
        if eligible:
            seen[identity] = path
        if isinstance(item, dict):
            return {key: visit(child, path + "/" + pointer_key(key))
                    for key, child in item.items()}
        if isinstance(item, list):
            return [visit(child, path + "/" + str(i)) for i, child in enumerate(item)]
        return item

    return visit(value, "")


def decode(value):
    resolved = {}

    def visit(item, path):
        if isinstance(item, dict) and set(item) == {TAG}:
            result = resolved[item[TAG]]
        elif isinstance(item, dict):
            result = {key: visit(child, path + "/" + pointer_key(key))
                      for key, child in item.items()}
        elif isinstance(item, list):
            result = [visit(child, path + "/" + str(i)) for i, child in enumerate(item)]
        else:
            result = item
        resolved[path] = result
        return result

    return visit(value, "")


def prepare(batch, start, count):
    manifest_path = HERE / "batches" / (batch + ".json")
    manifest = json.loads(manifest_path.read_text())
    units = manifest["units"][start:start + count]
    if not units:
        raise ValueError("No assigned decisions")
    cache, packets, sources = {}, [], []
    for unit in units:
        path = ROOT / unit["packet"]
        if path not in cache:
            cache[path] = path.read_text().splitlines()
        line = cache[path][unit["packet_line"] - 1]
        packet = json.loads(line)
        assert packet["decision_id"] == unit["decision_id"]
        packets.append(packet)
        sources.append({"decision_id": unit["decision_id"], "game": unit["game"],
                        "packet": unit["packet"], "packet_line": unit["packet_line"],
                        "source_line_sha256": hashlib.sha256(line.encode()).hexdigest()})
    original = {"sources": sources, "packets": packets}
    encoded = encode(original)
    assert decode(encoded) == original, "Reading copy failed exact JSON round trip"
    target = HERE / "reading_chunks" / batch / f"units_{start:04d}_{start + len(units) - 1:04d}"
    target.parent.mkdir(parents=True, exist_ok=True)
    # Compact keys, but one top-level packet per line for easy bounded reading.
    body = '{"sources":' + json.dumps(encoded["sources"], ensure_ascii=False) + ',\n"packets":[\n'
    body += ',\n'.join(json.dumps(p, ensure_ascii=False, separators=(",", ":")) for p in encoded["packets"])
    body += '\n]}\n'
    target.with_suffix(".json").write_text(body)
    assert decode(json.loads(body)) == original
    report = {"batch": batch, "start_index": start, "count": len(units),
              "decision_ids": [u["decision_id"] for u in units],
              "exact_json_roundtrip": True, "source_compact_characters": len(canonical(original)),
              "reading_characters": len(body), "semantic_review": "not_performed",
              "reading_sha256": hashlib.sha256(body.encode()).hexdigest()}
    target.with_suffix(".manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "decision_ids"}))
    print(target.with_suffix(".json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default="batch_01")
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()
    prepare(args.batch, args.start, args.count)
