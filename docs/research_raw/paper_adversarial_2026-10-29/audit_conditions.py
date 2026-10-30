"""Recheck action provenance, actual HTTP records, and chronology conditions.

Definitions are peer-informed. This is a new canonical-record derivation, not
blind replication or semantic interpretation of every explanatory channel.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P2 = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review/sol"
ALIASES = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini",
           "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}
FOCAL = {4: {148, 149, 150, 151, 152}, 6: {19, 20, 21}, 11: {255, 256, 257, 258},
         13: {218, 243, 244, 250, 251, 252, 253, 311},
         18: {83, 335, 360, 419, 431, 441, 442, 460}, 19: {135, 136}, 20: {1, 4}}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def content_name(content):
    try:
        value = json.loads(content or "")
    except ValueError:
        names = set(re.findall(r'"name"\s*:\s*"([a-z_]+)"', content or ""))
        return (names.pop(), "malformed_explicit_name") if len(names) == 1 else (None, "unparsed")
    if not isinstance(value, dict) or not isinstance(value.get("name"), str):
        return None, "no_named_call"
    return value["name"], "json_name"


def main():
    manifest = json.loads((ROOT / "docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json").read_text())
    counts = defaultdict(Counter)
    ends, conflicts, all_attempt_conflicts, conditions = [], [], [], []
    transport, source_hashes = Counter(), {}
    prior_exposure = json.loads((P2 / "trade_timeline_audit.json").read_text())
    exposure = {(r["game"], r["decision_id"]): r for r in prior_exposure["affected_initial_prompts"]}
    prior_bad = defaultdict(list)
    for row in prior_exposure["bad_events"]:
        prior_bad[row["game"]].append(row)
    for game in manifest["games"]:
        g, run = game["game"], ROOT / game["run"]
        source = run / "decisions.jsonl"
        source_hashes[str(source.relative_to(ROOT))] = digest(source.read_bytes())
        starts = {}
        for line_no, line in enumerate(source.open(), 1):
            row = json.loads(line)
            did = row["decision_id"]
            if row["phase"] == "decision_started":
                starts[did] = row
                continue
            if row["phase"] != "decision_resolved":
                continue
            start = starts[did]
            model, applied = ALIASES[row["openrouter_model_id"]], row["final_action"]["action"]
            valid = [(i, a) for i, a in enumerate(row["attempts"]) if a.get("outcome") == "valid"]
            selected = valid[-1] if valid and not row.get("fallback_used") else None
            cname, form = content_name(selected[1].get("assistant_content")) if selected else (None, "none")
            named_conflict = selected is not None and cname is not None and cname != selected[1]["parsed_tool_call"]["name"]
            common = {"game": g, "decision_id": did, "model": model,
                      "source_line": line_no, "source_line_sha256": digest(line.rstrip("\n").encode())}
            if "build_houses_or_hotel" in start["prompt_payload"]["action_state"].get("available_actions", []):
                counts[model]["construction_tool_listed"] += 1
                if applied == "end_turn":
                    category = "engine_default" if row.get("fallback_used") else "received_name_conflict" if named_conflict else "no_detected_name_conflict"
                    counts[model]["applied_end"] += 1
                    counts[model][category] += 1
                    ends.append({**common, "category": category, "selected_content_name": cname,
                                 "content_form": form, "response_condition": selected[1].get("response_condition") if selected else None})
            if model == "Grok":
                for index, attempt in enumerate(row["attempts"]):
                    name, shape = content_name(attempt.get("assistant_content"))
                    tool = attempt.get("parsed_tool_call")
                    if not name or not tool or name == tool.get("name"):
                        continue
                    record = {**common, "attempt_index": index, "content_name": name,
                              "received_tool_name": tool["name"], "form": shape,
                              "outcome": attempt.get("outcome"), "selected": selected is not None and selected[0] == index}
                    path = run.parent / "cloud/calls" / f'{attempt["call_id"]}.response.json'
                    saved = json.loads(path.read_text())
                    raw = json.loads(saved["response_text"])
                    request = json.loads(saved["request_payload_raw"])
                    raw_message = raw["choices"][0]["message"]
                    raw_tool = raw_message["tool_calls"][0]["function"]
                    assert raw_tool["name"] == tool["name"]
                    assert raw_message.get("content") == attempt.get("assistant_content")
                    assert request.get("stream") is not True
                    assert raw["choices"] == saved["response_json"]["choices"]
                    record.update({"http_path": str(path.relative_to(ROOT)), "http_file_sha256": digest(path.read_bytes()),
                                   "nonstreamed_request": True, "raw_body_json": True,
                                   "raw_names_match_decision_record": True})
                    all_attempt_conflicts.append(record)
                    if record["selected"]:
                        conflicts.append(record)
                        transport["selected_conflicts_in_nonstreamed_raw_json"] += 1
            suffix = int(did.rsplit("-", 1)[1])
            if suffix in FOCAL.get(g, set()):
                payload = selected[1].get("prompt_payload") if selected else None
                payload = payload or start["prompt_payload"]
                memory = payload.get("memory", {})
                # Prompt shape may put memory beneath game_state; preserve the
                # actual located object and exact textual rows for evidence.
                if not memory:
                    memory = payload.get("game_state", {}).get("memory", {})
                timeline = memory["public_timeline_last_20"]
                rendered = json.dumps(payload, ensure_ascii=False)
                matches = []
                for bad in prior_bad[g]:
                    expected = bad["expected_delivered_row"]
                    # Restrict full-row equality to the actual timeline, not
                    # structured trade history or repeated text elsewhere.
                    if expected in timeline:
                        matches.append({"seq": bad["seq"], "defect": bad["defect"]})
                conditions.append({**common, "selected_attempt": selected[0] if selected else None,
                                   "response_condition": selected[1].get("response_condition") if selected else None,
                                   "applied_action": applied, "content_name": cname,
                                   "received_name_conflict": named_conflict,
                                   "matched_formatter_rows": matches,
                                   "initial_prompt_prior_audit": exposure.get((g, did), {}).get("defects", []),
                                   "selected_payload_sha256": digest(rendered.encode()),
                                   "located_timeline_length": len(timeline)})
    retained = json.loads((P2 / "received_name_conflict_audit.json").read_text())
    retained_ids = {(r["game"], r["decision_id"], r["attempt_index"]) for r in retained["all_named_conflicts"]}
    new_ids = {(r["game"], r["decision_id"], r["attempt_index"]) for r in conflicts}
    assert retained_ids == new_ids
    output = {"counts": {m: dict(counts[m]) for m in ALIASES.values()}, "end_records": ends,
              "selected_grok_conflicts": conflicts, "all_attempt_conflicts": all_attempt_conflicts,
              "transport": dict(transport), "chronology_conditions": conditions,
              "conflict_scope": dict(Counter(("selected_" if r["selected"] else "unselected_") + r["form"] for r in all_attempt_conflicts)),
              "source_sha256": source_hashes, "script_sha256": digest(Path(__file__).read_bytes()),
              "scope": "Canonical records newly read; exact prior conflict case-set reproduced; raw HTTP body/request checked per case. Exposure target rows are inherited from the previous formatter audit and matched anew in selected prompts. No latent intention, attention, or causal attribution inferred."}
    (HERE / "conditions_audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({key: output[key] for key in ("counts", "transport", "conflict_scope")}, indent=2))


if __name__ == "__main__":
    main()
