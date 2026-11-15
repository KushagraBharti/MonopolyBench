"""Retained annotations and original-record checks for final integration."""
import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
ROOT = BASE.parents[2]
DATA = BASE / "data"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


first_path = DATA / "agenda_rejection_reasons.json"
second_path = ROOT / "docs/research_raw/paper_agenda_revision_2026-10-29/reviews/negotiation/own_74_row_ledger.json"
first = read(first_path)["rows_data"]
second = {row["decision_id"]: row for row in read(second_path)}
agreed = [row for row in first if "D" in row["codes"] and "D" in second[row["decision_id"]]["reviewer_codes"]]
assert len(agreed) == 61
by_model = dict(Counter(row["recipient_model"] for row in agreed))
assert by_model == {"Grok": 27, "Sol": 4, "Opus": 1, "Gemini": 29}
by_cell = dict(Counter(row["completion_cell"] for row in agreed))
assert by_cell == {"both": 34, "recipient_only": 27}

# Load only the retained pure content-parser function, not its module imports.
parser_path = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review/sol/audit_received_name_conflicts.py"
tree = ast.parse(parser_path.read_text())
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "extract")
namespace = {"json": json, "re": re}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(parser_path), "exec"), namespace)
extract = namespace["extract"]
forms = Counter()
conflicts = set()
opus = Counter()
focal = {}
sources = {str(path.relative_to(ROOT)): sha(path) for path in [first_path, second_path, parser_path]}
for game_dir in sorted((ROOT / "saved_games").glob("railway-research-*/game-??-*")):
    game = int(game_dir.name.split("-")[1])
    path = game_dir / "run/decisions.jsonl"
    sources[str(path.relative_to(ROOT))] = sha(path)
    for line in path.open():
        row = json.loads(line)
        if row["phase"] != "decision_resolved":
            continue
        model = row["openrouter_model_id"]
        index = int(row["decision_id"].rsplit("-", 1)[-1])
        if model == "x-ai/grok-4.7":
            valid = [attempt for attempt in row["attempts"] if attempt["outcome"] == "valid"]
            if valid and not row.get("fallback_used"):
                attempt = valid[-1]
                content = extract(attempt.get("assistant_content"))
                forms[content["status"] if content else "unavailable"] += 1
                if content and content["name"] != attempt["parsed_tool_call"]["name"]:
                    conflicts.add((game, row["decision_id"]))
        if model == "anthropic/claude-opus-5.5":
            meta = row["sequence_meta"]
            opus["decisions"] += 1
            opus["model_fallback_used"] += bool(meta["model_fallback_used"])
            assert meta["returned_model"] == model
            assert len(row["attempts"]) <= 2
            assert "fallback_without_private_thought" in str(meta["response_policy"])
            assert "anthropic/claude-opus-4.8" in str(meta["response_policy"])
        if (game == 16 and index == 602) or (game == 18 and index in {442, 445, 448, 453, 454, 455, 456, 457, 460, 461}) or (game == 2 and index in {119, 120}):
            focal[f"G{game}d{index}"] = {"turn": row["turn_index"], "action": row["final_action"]}
    if game == 7:
        events_path = game_dir / "run/events.jsonl"
        events = [json.loads(line) for line in events_path.open()]
        focal["G7_followthrough_events"] = [row for row in events if row["turn_index"] in {95, 110, 112} and row["type"] in {"PROPERTY_PURCHASED", "HOUSE_BUILT", "CASH_CHANGED"}]
        sources[str(events_path.relative_to(ROOT))] = sha(events_path)

ledger = read(DATA / "resolution_conditions.json")
retained = {(row["game"], row["decision_id"]) for row in ledger["selected_grok_conflicts"]}
assert conflicts == retained and len(conflicts) == 139
named = sum(value for key, value in forms.items() if key != "unavailable")
assert named == 1068
assert opus == {"decisions": 1696, "model_fallback_used": 0}
recurrence = read(DATA / "agenda_recurrence.json")["episodes"]
no_feedback = [row for row in recurrence if not row["delivered_feedback"] and row["next_decision_id"]]
assert len(no_feedback) == 59 and sum(row["next_any_submission_uneven"] for row in no_feedback) == 54
assert {row["model"] for row in no_feedback} == {"anthropic/claude-opus-5.5"}
result = {
    "scope": "Retained-label join, original-record reads and the unchanged content parser. No new semantic coding, engine execution or evaluation.",
    "agreed_reasons": {"total": 61, "by_model": by_model, "by_cell": by_cell},
    "grok_content": {"named": named, "conflicts": len(conflicts), "forms": dict(forms), "same_conflict_records": True},
    "opus_fallback": dict(opus), "recurrence_without_feedback": {"successors": 59, "repeats": 54, "all_opus": True},
    "focal": focal, "source_sha256": sources, "script_sha256": sha(Path(__file__)),
}
(HERE / "fable_reporting_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if key not in {"focal", "source_sha256", "script_sha256"}}, indent=2))
