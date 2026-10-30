"""Bounded source-packet reader. No annotations, automatic review, or hidden cursor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def page_text(value, offset, size):
    if offset < 0 or not 1 <= size <= 12000:
        raise ValueError("Use nonnegative offset and size 1..12000")
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    end = min(offset + size, len(text))
    return text[offset:end], {"offset": offset, "end": end, "total_characters": len(text),
                              "complete": end == len(text), "next_offset": None if end == len(text) else end}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default="batch_01")
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--part", choices=("behavior", "observation", "raw"), default="behavior")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--size", type=int, default=10000)
    args = parser.parse_args()
    manifest = json.loads((HERE / "batches" / f"{args.batch}.json").read_text())
    unit = manifest["units"][args.index]
    packet = json.loads((ROOT / unit["packet"]).read_text().splitlines()[unit["packet_line"] - 1])
    if args.part == "observation":
        value = {"initial_prompt": packet["initial_prompt"],
                 "attempt_prompts": [{"attempt": a["attempt_index_zero_based"], "prompt": a["prompt"]}
                                     for a in packet["attempts"]]}
    elif args.part == "raw":
        value = packet
    else:
        attempts = []
        for attempt in packet["attempts"]:
            raw = attempt.get("raw_response")
            if isinstance(raw, dict) and "choices" in raw:
                # Preserve ALL choices and each complete provider message, including reasoning.
                response = {"model": raw.get("model"), "provider": raw.get("provider"),
                            "choices": raw["choices"]}
            else:
                response = raw
            attempts.append({k: attempt.get(k) for k in (
                "attempt_index_zero_based", "outcome", "response_condition", "reason",
                "error_type", "error_message", "validation_errors", "requested_model",
                "assistant_content", "parsed_tool_call", "parsed_tool_calls")}
                | {"provider_response": response})
        value = {"applied_action_record": packet["applied_action_record"], "attempts": attempts,
                 "canonical_events": [{k: e[k] for k in ("seq", "turn_index", "actor", "type", "payload")}
                                      for e in packet["canonical_event_segment"]],
                 "resolution": packet["resolution"], "source_lines": packet["source_lines"],
                 "source_run": packet["source_run"], "physical_responses": packet["physical_responses"]}
    body, pagination = page_text(value, args.offset, args.size)
    print(json.dumps({"batch": args.batch, "index": args.index, "decision_id": unit["decision_id"],
                      "game": unit["game"], "source_packet": unit["packet"],
                      "source_packet_line": unit["packet_line"], "part": args.part, **pagination}))
    print(body)
    print("END PAGE. Read remaining offsets and both behavior + observation before marking review complete.")


if __name__ == "__main__":
    main()
