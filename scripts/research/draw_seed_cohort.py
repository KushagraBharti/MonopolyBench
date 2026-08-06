from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw an auditable outcome-blind research seed cohort.")
    parser.add_argument("--cohort-id", required=True)
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--entropy-hex")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.count < 1:
        raise SystemExit("--count must be positive")

    repo_root = Path(__file__).resolve().parents[2]
    registry_path = repo_root / "contracts" / "research" / "monopoly_long_v1_seed_registry.json"
    registry = _read_json(registry_path)
    excluded = {
        int(entry["seed"])
        for cohort in _dict(registry.get("cohorts")).values()
        for entry in _list(_dict(cohort).get("seeds"))
        if isinstance(entry, dict) and isinstance(entry.get("seed"), int)
    }
    entropy_hex = args.entropy_hex or secrets.token_hex(32)
    try:
        entropy = bytes.fromhex(entropy_hex)
    except ValueError as error:
        raise SystemExit("--entropy-hex must be valid hexadecimal") from error
    if len(entropy) < 16:
        raise SystemExit("--entropy-hex must contain at least 128 bits")

    seeds: list[dict[str, Any]] = []
    counter = 0
    while len(seeds) < args.count:
        material = (
            b"MonopolyBench/outcome-blind-seed-draw/v1\0"
            + args.cohort_id.encode("utf-8")
            + b"\0"
            + entropy
            + counter.to_bytes(8, "big")
        )
        digest = hashlib.sha256(material).digest()
        seed = int.from_bytes(digest[:4], "big")
        counter += 1
        if seed == 0 or seed in excluded or any(row["seed"] == seed for row in seeds):
            continue
        seeds.append(
            {
                "seed": seed,
                "label": f"{args.cohort_id}-{len(seeds) + 1}",
                "rationale": (
                    "Outcome-blind SHA-256 draw from committed entropy; no trajectory was inspected before inclusion."
                ),
                "draw_counter": counter - 1,
                "draw_digest_sha256": digest.hex(),
            }
        )

    payload = {
        "schema_version": "v1",
        "seed_draw_version": "outcome_blind_seed_draw_v1",
        "cohort_id": args.cohort_id,
        "count": args.count,
        "algorithm": (
            "uint32_be(SHA256(domain_separator || cohort_id || entropy || uint64_be(counter))[0:4]); "
            "reject zero, duplicates, and pre-existing registered seeds"
        ),
        "entropy_hex": entropy_hex,
        "drawn_at_utc": _utc_now(),
        "source_commit": _git_head(repo_root),
        "excluded_registered_seed_count": len(excluded),
        "outcome_information_used": False,
        "seeds": seeds,
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "Seed drawing changes run configuration only and is never injected into prompts.",
        },
    }
    output_path = (repo_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(output_path),
                "cohort_id": args.cohort_id,
                "entropy_hex": entropy_hex,
                "seeds": [row["seed"] for row in seeds],
            },
            sort_keys=True,
        )
    )
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
