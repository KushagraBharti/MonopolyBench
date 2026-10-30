"""Lossless deduplication for reading one original packet, with opaque blobs hashed.

Every distinct readable value remains. Duplicate references resolve exactly.
This creates a reading aid and never marks a decision as reviewed.
"""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game", type=int)
    parser.add_argument("decision", type=int)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    ledger = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"
    unit = next(u for u in map(json.loads, ledger.read_text().splitlines())
                if u["game"] == args.game and int(u["decision_id"][-6:]) == args.decision)
    packet = ROOT / unit["packet"]
    row = json.loads(packet.read_text().splitlines()[unit["packet_line"] - 1])
    seen, originals, opaque = {}, {}, []

    def transform(value, path, key=None):
        if key in {"signature", "data"} and isinstance(value, str) and len(value) > 100:
            opaque.append({"path": path, "characters": len(value), "sha256": sha(value)})
            return {"$opaque_blob": opaque[-1]}
        if isinstance(value, str) and len(value) > 120 and value.lstrip().startswith(("{", "[")):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                pass
            else:
                originals[path + "/$raw_json"] = value
                return {"$json_encoded_string": transform(parsed, path + "/$parsed"),
                        "raw_source": path + "/$raw_json", "raw_sha256": sha(value)}
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if len(encoded) > 120 and encoded in seen:
            return {"$exact_duplicate_of": seen[encoded], "sha256": sha(encoded)}
        if len(encoded) > 120:
            seen[encoded], originals[path] = path, value
        if isinstance(value, dict):
            return {k: transform(v, f"{path}/{k}", k) for k, v in value.items()}
        if isinstance(value, list):
            return [transform(v, f"{path}/{i}") for i, v in enumerate(value)]
        return value

    rendered = transform(row, "root")

    def resolve(value):
        if isinstance(value, dict) and "$json_encoded_string" in value:
            original = originals[value["raw_source"]]
            assert sha(original) == value["raw_sha256"]
            assert resolve(value["$json_encoded_string"]) == json.loads(original)
            return original
        if isinstance(value, dict) and "$exact_duplicate_of" in value:
            original = originals[value["$exact_duplicate_of"]]
            assert sha(json.dumps(original, sort_keys=True, ensure_ascii=False)) == value["sha256"]
            return original
        if isinstance(value, dict) and "$opaque_blob" in value:
            path = value["$opaque_blob"]["path"].split("/")[1:]
            original = row
            for p in path:
                original = original[int(p)] if isinstance(original, list) else original[p]
            assert sha(original) == value["$opaque_blob"]["sha256"]
            return original
        if isinstance(value, dict):
            return {k: resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v) for v in value]
        return value

    assert resolve(rendered) == row
    result = {"source_unit": unit, "packet_sha256": sha(packet.read_text()),
              "scope": "All distinct readable original values; exact duplicates linked; opaque signatures/data hashed. No semantic review status implied.",
              "reconstruction_equals_original": True, "original": rendered}
    print(json.dumps(result, indent=None if args.compact else 2, ensure_ascii=False))


if __name__ == "__main__":
    main()
