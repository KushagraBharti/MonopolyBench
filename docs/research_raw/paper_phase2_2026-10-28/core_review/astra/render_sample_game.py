"""Render fixed sample bundles with exact cross-record deduplication.

This reading aid verifies lossless reconstruction, hashes opaque blobs, and does
not mark anything semantically reviewed. Pages split at fixed character offsets.
"""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game", type=int)
    args = parser.parse_args()
    sample = [json.loads(s) for s in (HERE.parent / "public_unflagged_sample.jsonl").read_text().splitlines()]
    sample = [s for s in sample if s["game"] == args.game]
    originals = {}
    for s in sample:
        path = ROOT / s["packet"]
        originals[s["decision_id"]] = {
            "source_unit": s, "packet_sha256": digest(path.read_text()),
            "bundle": json.loads(path.read_text().splitlines()[s["packet_line"] - 1]),
        }
    seen, values = {}, {}

    def transform(value, path, key=None):
        if key in {"signature", "data"} and isinstance(value, str) and len(value) > 100:
            values[path] = value
            return {"$opaque": path, "characters": len(value), "sha256": digest(value)}
        if isinstance(value, str) and len(value) > 120 and value.lstrip().startswith(("{", "[")):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                pass
            else:
                values[path + "/raw"] = value
                return {"$json": transform(parsed, path + "/parsed"), "raw": path + "/raw"}
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if len(encoded) > 80 and encoded in seen:
            return {"$duplicate": seen[encoded]}
        if len(encoded) > 80:
            seen[encoded] = path
            values[path] = value
        if isinstance(value, dict):
            return {k: transform(v, path + "/" + k, k) for k, v in value.items()}
        if isinstance(value, list):
            return [transform(v, path + "/" + str(i)) for i, v in enumerate(value)]
        return value

    def resolve(value):
        if isinstance(value, dict):
            if "$opaque" in value:
                raw = values[value["$opaque"]]
                assert digest(raw) == value["sha256"]
                return raw
            if "$duplicate" in value:
                return values[value["$duplicate"]]
            if "$json" in value:
                raw = values[value["raw"]]
                assert resolve(value["$json"]) == json.loads(raw)
                return raw
            return {k: resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v) for v in value]
        return value

    rendered = transform(originals, "root")
    assert resolve(rendered) == originals
    text = json.dumps(rendered, ensure_ascii=False, separators=(",", ":"))
    out = HERE / "sample_reading"
    out.mkdir(exist_ok=True)
    path = out / f"game{args.game:02d}.json"
    path.write_text(text)
    print(json.dumps({"file": str(path.relative_to(ROOT)), "bundles": len(sample), "characters": len(text),
                      "pages_of_14000_characters": (len(text) + 13999) // 14000,
                      "reconstruction_equals_original": True, "sha256": digest(text),
                      "semantic_review_status": "not implied by generation"}))


if __name__ == "__main__":
    main()
