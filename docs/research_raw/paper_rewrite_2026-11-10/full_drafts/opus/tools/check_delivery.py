#!/usr/bin/env python3
"""Check that public messages quoted in the Opus draft reached the recipient's next prompt.

Reads canonical prompt files (read-only) and writes ../data/opus_delivery_checks.json.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DRAFT = HERE.parent
REPO = DRAFT.parents[4]
CAMPAIGN = REPO / "saved_games" / "railway-research-12-games-2026-10-25"
G2 = CAMPAIGN / "game-02-102turns-270aabe8" / "run" / "prompts"
G11 = CAMPAIGN / "game-11-145turns-2b0fe1ce" / "run" / "prompts"

CHECKS = [
    ("G2 d124 Sol public -> Opus d125", G2, 125, "doesn't compensate for handing you that monopoly"),
    ("G2 d127 Opus public -> Sol d128", G2, 128, "that's my final offer"),
    ("G2 d197 Opus public -> Sol d198", G2, 198, "These two finish a monopoly for you"),
    ("G11 d255 Sol false claim -> Grok d256", G11, 256, "completes your pinks"),
    ("G11 d256 Grok reply -> Sol d257", G11, 257, "Pennsylvania completes your greens"),
]


def main():
    results = []
    for label, folder, dec, needle in CHECKS:
        files = sorted(folder.glob(f"decision_*-dec-{dec:06d}_user.json"))
        found = any(needle in f.read_text(encoding="utf-8").replace("\\u2019", "'") for f in files)
        results.append({"check": label, "prompt_files": [str(f.relative_to(REPO)) for f in files],
                        "needle": needle, "found": found})
    out = DRAFT / "data" / "opus_delivery_checks.json"
    out.write_text(json.dumps({"scope": "Substring presence in the recipient's next user prompt; not attention, belief or reliance.",
                               "results": results}, indent=1) + "\n", encoding="utf-8")
    for r in results:
        print(r["found"], r["check"])


if __name__ == "__main__":
    main()
