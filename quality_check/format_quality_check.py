from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from format_quality_check_nested import format_quality_payload


DEFAULT_INPUT_DIR = Path("quality_check/mock-25273-a49d65fc")


def _pretty_json(text: str) -> str | None:
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        return None
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)


def _format_file(src: Path, dest: Path) -> None:
    raw = src.read_text(encoding="utf-8")
    pretty = format_quality_payload(raw) or _pretty_json(raw)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if pretty is None:
        dest.write_text(raw, encoding="utf-8")
        return
    dest.write_text(pretty + "\n", encoding="utf-8")


def _resolve_output_dir(input_dir: Path, output_dir: Path | None) -> Path:
    if output_dir is not None:
        return output_dir
    return input_dir.parent / f"{input_dir.name}_formatted"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pretty-print raw OpenRouter prompt/response TXT files.",
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        nargs="?",
        default=None,
        help=(
            "Path to a quality_check run folder (e.g. quality_check/mock-123). "
            f"Defaults to {DEFAULT_INPUT_DIR}."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output folder (defaults to <input>_formatted).",
    )
    args = parser.parse_args(argv)

    input_dir = args.input_dir or DEFAULT_INPUT_DIR
    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input folder not found: {input_dir}")

    output_dir = _resolve_output_dir(input_dir, args.output_dir)

    txt_files = sorted(input_dir.glob("*.txt"))
    if not txt_files:
        raise SystemExit(f"No .txt files found in: {input_dir}")

    for src in txt_files:
        dest = output_dir / src.name
        _format_file(src, dest)

    print(str(output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
