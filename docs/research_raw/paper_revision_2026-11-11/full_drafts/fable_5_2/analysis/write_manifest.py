"""Record hashes of every input read and every file in this draft package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from corpus import BOARD_PATH, REPO, game_dirs

HERE = Path(__file__).resolve().parents[1]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


inputs = {}
for n, run in game_dirs().items():
    for name in ("events.jsonl", "decisions.jsonl", "players.json"):
        inputs[rel(run / name)] = sha(run / name)
inputs[rel(BOARD_PATH)] = sha(BOARD_PATH)
retained = [
    "docs/research_raw/paper_rewrite_2026-11-10/data/agenda_offers.json",
    "docs/research_raw/paper_rewrite_2026-11-10/data/t06_eliminations.json",
    "docs/research_raw/paper_rewrite_2026-11-10/data/first_management_windows.json",
    "docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/rejection_reason_coding.json",
    "docs/research_raw/paper_agenda_revision_2026-10-29/reviews/negotiation/reason_comparison.json",
    "docs/research_raw/paper_rewrite_2026-11-10/integrated/sections/transcript_quotes.tex",
    "docs/research_raw/paper_rewrite_2026-11-10/integrated/sections/opus_quotes.tex",
    "docs/research_raw/paper_rewrite_2026-11-10/integrated/sections/fable_quotes.tex",
    "docs/research_raw/paper_rewrite_2026-11-10/integrated/preamble.tex",
    "docs/research_raw/paper_revision_2026-11-11/baseline_hashes.json",
]
retained_h = {p: sha(REPO / p) for p in retained}
n_prompt_files = sum(1 for n, run in game_dirs().items() for _ in (run / "prompts").glob("*_tools.json"))
n_intents = sum(1 for n, run in game_dirs().items() for _ in (run.parent / "cloud" / "calls").glob("*.intent.json"))
outputs = {}
for p in sorted(HERE.rglob("*")):
    if not p.is_file():
        continue
    r = p.relative_to(HERE)
    if r.parts[0] in ("build",) or r.parts[:2] == ("qa", "render") or "__pycache__" in r.parts or r.name in ("source_manifest.json", "build_stdout.txt", ".DS_Store"):
        continue
    outputs[str(r)] = sha(p)
manifest = {
    "note": "Inputs are read-only. Per-game prompt tool files and call-intent files are counted, not hashed individually.",
    "canonical_inputs": inputs,
    "retained_inputs_from_earlier_work": retained_h,
    "tool_schema_files_read": n_prompt_files,
    "call_intent_files_read": n_intents,
    "package_files": outputs,
}
(HERE / "source_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
print("inputs", len(inputs), "retained", len(retained_h), "package files", len(outputs))
