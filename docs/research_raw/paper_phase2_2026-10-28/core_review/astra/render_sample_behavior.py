"""Reading aid retaining all behavioral channels, omitting transport metadata.

No coverage is awarded by generation. Source packets remain authoritative.
Full messages, prompts, attempts, calls, errors, state and event payloads survive;
timestamps, billing, request IDs and duplicate raw-payload encodings are omitted.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {k: ({"opaque_characters": len(v), "sha256": digest(v.encode())}
                    if k in {"signature", "data"} and isinstance(v, str) and len(v) > 100
                    else clean(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
        try:
            return {"decoded_json_string": clean(json.loads(value))}
        except json.JSONDecodeError:
            pass
    return value


def prompt(p):
    return {k: v for k, v in p.items() if k != "raw_payload"}


def project(unit):
    path = ROOT / unit["packet"]
    b = json.loads(path.read_text().splitlines()[unit["packet_line"] - 1])
    attempts = []
    for a in b["attempts"]:
        item = {k: a.get(k) for k in ["attempt_index_zero_based", "requested_model",
                "response_condition", "outcome", "reason", "validation_errors",
                "error_type", "error_message", "assistant_content", "parsed_tool_call",
                "parsed_tool_calls"]}
        item["prompt"] = prompt(a["prompt"])
        raw = a.get("raw_response") or {}
        item["returned_model"] = raw.get("model")
        item["choices"] = raw.get("choices")
        if "error" in raw:
            item["raw_error"] = raw["error"]
        attempts.append(item)
    return clean({"source_unit": unit, "packet_sha256": digest(path.read_bytes()),
                  "model": b["model"], "turn": b["turn_index"],
                  "initial_prompt": prompt(b["initial_prompt"]), "attempts": attempts,
                  "applied": b["applied_action_record"],
                  "resolution": {k: b["resolution"].get(k) for k in ["applied", "fallback_used",
                    "fallback_reason", "retry_used", "sequence_meta", "emitted_event_seq_start",
                    "emitted_event_seq_end", "final_action"]},
                  "events": [{"seq": e["seq"], "turn": e["turn_index"], "actor": e["actor"],
                              "type": e["type"], "payload": e["payload"]}
                             for e in b["canonical_event_segment"]]})


def compact(original):
    counts = Counter()

    def key(v):
        return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def count(v):
        k = key(v)
        if len(k) > 100:
            counts[k] += 1
        if isinstance(v, dict):
            for x in v.values():
                count(x)
        elif isinstance(v, list):
            for x in v:
                count(x)

    count(original)
    anchors = {}

    def pack(v):
        k = key(v)
        repeated = counts[k] > 1
        if repeated and k in anchors:
            return {"ref": anchors[k]}
        n = None
        if repeated:
            n = len(anchors)
            anchors[k] = n
        r = ({a: pack(x) for a, x in v.items()} if isinstance(v, dict)
             else [pack(x) for x in v] if isinstance(v, list) else v)
        return {"define": n, "value": r} if repeated else r

    result = pack(original)
    recovered = {}

    def unpack(v):
        if isinstance(v, dict):
            if set(v) == {"ref"}:
                return recovered[v["ref"]]
            if set(v) == {"define", "value"}:
                recovered[v["define"]] = unpack(v["value"])
                return recovered[v["define"]]
            return {k: unpack(x) for k, x in v.items()}
        return [unpack(x) for x in v] if isinstance(v, list) else v

    assert unpack(result) == original
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("game", type=int)
    args = p.parse_args()
    units = [json.loads(s) for s in (HERE.parent / "public_unflagged_sample.jsonl").read_text().splitlines()]
    units = [u for u in units if u["game"] == args.game]
    assert len(units) == 12
    result = compact([project(u) for u in units])
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    out = HERE / "sample_reading" / f"game{args.game:02d}_behavior.json"
    out.write_text(text)
    print(json.dumps({"file": str(out.relative_to(ROOT)), "characters": len(text),
                      "sha256": digest(text.encode()), "semantic_review": "not implied"}))


if __name__ == "__main__":
    main()
