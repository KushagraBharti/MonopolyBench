"""Exact original-bundle reading aid with short, explicit duplicate anchors.

Every distinct readable value remains. A definition {"#": n, "value": ...}
can be reused by {"@": n}; references only point backward. JSON encoded
strings are parsed for readability with their raw bytes retained for the
reconstruction check. Opaque encrypted values are represented by hashes.
Generation never marks a semantic review complete.
"""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def render(original):
    seen, raw_values = {}, []

    def transform(value, key=None):
        if key in {"signature", "data"} and isinstance(value, str) and len(value) > 100:
            raw_values.append(value)
            return {"$opaque_blob_id": len(raw_values) - 1, "characters": len(value), "sha256": digest(value)}
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if len(encoded) > 50 and encoded in seen:
            return {"@": seen[encoded]}
        anchor = None
        if len(encoded) > 50:
            anchor = len(seen)
            seen[encoded] = anchor
        if isinstance(value, str) and len(value) > 50 and value.lstrip().startswith(("{", "[")):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                result = value
            else:
                raw_values.append(value)
                raw_index = len(raw_values) - 1
                result = {"$encoded_json": transform(parsed), "raw": raw_index, "sha256": digest(value)}
        elif isinstance(value, dict):
            result = {k: transform(v, k) for k, v in value.items()}
        elif isinstance(value, list):
            result = [transform(v) for v in value]
        else:
            result = value
        return {"#": anchor, "value": result} if anchor is not None else result

    rendered = transform(original)
    anchors = {}

    def resolve(value):
        if isinstance(value, dict):
            if "@" in value:
                return anchors[value["@"]]
            if "#" in value:
                result = resolve(value["value"])
                anchors[value["#"]] = result
                return result
            if "$opaque_blob_id" in value:
                raw = raw_values[value["$opaque_blob_id"]]
                assert digest(raw) == value["sha256"]
                return raw
            if "$encoded_json" in value:
                raw = raw_values[value["raw"]]
                assert digest(raw) == value["sha256"]
                assert resolve(value["$encoded_json"]) == json.loads(raw)
                return raw
            return {k: resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v) for v in value]
        return value

    assert resolve(rendered) == original
    return rendered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game", type=int)
    args = parser.parse_args()
    units = [json.loads(s) for s in (HERE.parent / "public_unflagged_sample.jsonl").read_text().splitlines()]
    units = [u for u in units if u["game"] == args.game]
    original = []
    for unit in units:
        path = ROOT / unit["packet"]
        original.append({"source_unit": unit, "packet_sha256": digest(path.read_text()),
                         "bundle": json.loads(path.read_text().splitlines()[unit["packet_line"] - 1])})
    result = render(original)
    out = HERE / "sample_reading" / f"game{args.game:02d}_compact.json"
    out.parent.mkdir(exist_ok=True)
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    out.write_text(text)
    print(json.dumps({"path": str(out.relative_to(ROOT)), "characters": len(text),
                      "sha256": digest(text), "bundles": len(original),
                      "exact_reconstruction": True, "semantic_review": "not implied"}))


if __name__ == "__main__":
    main()
