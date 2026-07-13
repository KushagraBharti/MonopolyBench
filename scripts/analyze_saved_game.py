from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_SRC = REPO_ROOT / "python" / "packages" / "telemetry" / "src"
if str(TELEMETRY_SRC) not in sys.path:
    sys.path.insert(0, str(TELEMETRY_SRC))

from monopoly_telemetry.expanded_metrics import analyze_saved_game  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate deterministic, expanded metrics for one MonopolyBench saved game."
    )
    parser.add_argument(
        "saved_game",
        type=Path,
        help="Saved-game folder (containing run/) or the run artifact folder itself.",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    result = analyze_saved_game(args.saved_game, args.output_dir)
    print(json.dumps({"run_id": result["run_id"], "counts": result["counts"]}, indent=2))


if __name__ == "__main__":
    main()
