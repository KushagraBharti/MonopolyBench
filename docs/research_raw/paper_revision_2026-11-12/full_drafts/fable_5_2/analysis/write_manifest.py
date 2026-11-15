"""Record hashes of every input read and every file in this draft package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from corpus import BOARD_PATH, COLLECTIONS, REPO, game_dirs

HERE = Path(__file__).resolve().parents[1]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


inputs = {}
for n, run in game_dirs().items():
    for name in ("events.jsonl", "decisions.jsonl", "players.json", "replay_report.json", "artifact_replay_report.json", "state_replay_report.json", "run_config.json"):
        inputs[rel(run / name)] = sha(run / name)
for coll in COLLECTIONS:
    inputs[rel(coll / "game-index.csv")] = sha(coll / "game-index.csv")
inputs[rel(BOARD_PATH)] = sha(BOARD_PATH)
retained = [
    "docs/research_raw/paper_revision_2026-11-11/integrated/data/offers.json",
    "docs/research_raw/paper_revision_2026-11-11/integrated/data/liquidation_episodes.json",
    "docs/research_raw/paper_rewrite_2026-11-10/data/t06_eliminations.json",
    "docs/research_raw/paper_agenda_revision_2026-10-29/negotiation/rejection_reason_coding.json",
    "docs/research_raw/paper_agenda_revision_2026-10-29/reviews/negotiation/reason_comparison.json",
    "docs/research_raw/paper_revision_2026-11-11/integrated/sections/transcript_quotes.tex",
    "docs/research_raw/paper_revision_2026-11-11/integrated/sections/opus_quotes.tex",
    "docs/research_raw/paper_revision_2026-11-11/integrated/sections/fable_quotes.tex",
    "docs/research_raw/paper_revision_2026-11-11/integrated/sections/additional_quotes.tex",
    "docs/research_raw/paper_revision_2026-11-12/baseline_manifest.json",
    "docs/research_raw/paper_revision_2026-11-12/CHARTER.md",
]
retained_h = {p: sha(REPO / p) for p in retained}
n_intents = sum(1 for coll in COLLECTIONS for _ in coll.glob("game-*/cloud/calls/*.intent.json"))
n_tools = sum(1 for n, run in game_dirs().items() for _ in (run / "prompts").glob("*_tools.json"))
outputs = {}
for p in sorted(HERE.rglob("*")):
    if not p.is_file():
        continue
    r = p.relative_to(HERE)
    if r.parts[0] == "build" or r.parts[:2] == ("qa", "render") or "__pycache__" in r.parts or r.name in ("source_manifest.json", ".DS_Store"):
        continue
    outputs[str(r)] = sha(p)
manifest = {
    "note": "Inputs are read-only. Call-intent and tool-schema files are counted, not hashed one by one.",
    "canonical_inputs": inputs,
    "retained_inputs_from_earlier_work": retained_h,
    "call_intent_files_read": n_intents,
    "tool_schema_files_read": n_tools,
    "package_files": outputs,
}
(HERE / "source_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
print("inputs", len(inputs), "retained", len(retained_h), "package files", len(outputs))
