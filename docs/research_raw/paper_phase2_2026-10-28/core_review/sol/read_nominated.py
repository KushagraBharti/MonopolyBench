"""Render one nominated nonsample bundle; output never implies completed review.

--prior names only same-game bundles already manually read in full. Character
slices support complete contiguous reading of unusually long returned texts.
"""

import argparse
import contextlib
import io
import json

from read_samples import HERE, ROOT, compact, load_units, remember, render


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game", type=int)
    parser.add_argument("suffix", type=int)
    parser.add_argument("--prior", nargs="*", type=int, default=[])
    parser.add_argument("--chars", nargs=2, type=int)
    args = parser.parse_args()
    for record in map(json.loads, (HERE / "negative_control_reviews.jsonl").read_text().splitlines()):
        source = record["source_checks"]
        unit = json.loads((ROOT / source["packet"]).read_text().splitlines()[source["packet_line"] - 1])
        remember(compact(unit), f"reviewed {record['decision_id']}")
    units = load_units(args.game)
    for unit, _, _, _ in units:
        if int(unit["decision_id"][-6:]) in args.prior:
            remember(compact(unit), f"explicitly previously read nonsample G{args.game}d{unit['decision_id'][-6:]}")
    unit = next(row[0] for row in units if int(row[0]["decision_id"][-6:]) == args.suffix)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        render(-1, {"game": args.game, "decision_id": unit["decision_id"], "scope": "nominated nonsample original audit"}, units)
    output = buffer.getvalue()
    if args.chars:
        start, stop = args.chars
        print(f"TOTAL CHARACTERS {len(output)}; DISPLAY {start}:{min(stop, len(output))}")
        print(output[start:stop])
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
