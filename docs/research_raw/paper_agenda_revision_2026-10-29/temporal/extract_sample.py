"""Extract complete scoped fields from the frozen 240-decision sample."""
from pathlib import Path
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((OUT / "sample_manifest.json").read_text())
    packets = {}
    actions = {}
    records = []
    for item in manifest["rows"]:
        path = ROOT / item["packet"]
        if path not in packets:
            raw = path.read_bytes()
            packets[path] = (raw.decode().splitlines(), digest(raw))
        lines, file_hash = packets[path]
        packet = json.loads(lines[item["packet_line"] - 1])
        assert packet["decision_id"] == item["decision_id"]
        run = ROOT / packet["source_run"]
        action_path = run / "actions.jsonl"
        if action_path not in actions:
            raw = action_path.read_bytes()
            actions[action_path] = (raw.decode().splitlines(), digest(raw))
        action_lines, action_hash = actions[action_path]
        line = packet["source_lines"]["action"]
        canonical = json.loads(action_lines[line - 1])
        assert canonical == packet["applied_action_record"]
        action = canonical["action"]
        resolution = packet["resolution"]
        assert action == resolution["final_action"]
        state = packet["initial_prompt"]["payload"]["game_state"]
        available = packet["initial_prompt"]["payload"]["action_state"]
        fields = {}
        for field in ("public_message", "private_thought"):
            value = action.get(field)
            fields[field] = {"value": value, "present": field in action,
                             "sha256": digest(value.encode()) if isinstance(value, str) else None,
                             "json_pointer": "/action/" + field}
        records.append({
            "id": f"G{item['game']:02d}d{int(item['decision_id'].rsplit('-',1)[1]):06d}",
            "game": item["game"], "decision_id": item["decision_id"],
            "decision_index": int(item["decision_id"].rsplit("-", 1)[1]),
            "player_id": packet["player_id"], "model": packet["model"],
            "turn_index": packet["turn_index"], "decision_type": packet["decision_type"],
            "action": action["action"], "args": action["args"], "fields": fields,
            "cash": state["you"]["cash"], "position": state["you"]["position"],
            "holdings": state["you"]["holdings"], "bank": state["bank"],
            "others": state["others"], "menu": available,
            "response_condition": resolution.get("sequence_meta", {}).get("response_condition"),
            "fallback_used": resolution["fallback_used"],
            "attempt_outcomes": [x["outcome"] for x in packet["attempts"]],
            "event_start": packet["source_lines"]["event_segment_start"],
            "event_end": packet["source_lines"]["event_segment_end"],
            "source_run": packet["source_run"],
            "source": {"packet": item["packet"], "packet_line": item["packet_line"],
                       "packet_sha256": file_hash,
                       "actions": str(action_path.relative_to(ROOT)), "action_line": line,
                       "actions_sha256": action_hash},
            "selection_rank": item["selection_rank"],
            "public_unflagged_pool_size": item["eligible_in_stratum"],
        })
    records.sort(key=lambda r: (r["game"], r["decision_index"]))
    assert len(records) == len({x["id"] for x in records}) == 240
    assert set(Counter(x["game"] for x in records).values()) == {12}
    assert set(Counter((x["game"],x["player_id"]) for x in records).values()) == {3}
    (OUT / "sample_fields.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    report = {"rows": len(records), "source_actions_equal": len(records),
              "missing_private": sum(not x["fields"]["private_thought"]["present"] for x in records),
              "characters": sum(len(f["value"] or "") for x in records for f in x["fields"].values()),
              "source_manifest_sha256": digest((OUT / "sample_manifest.json").read_bytes())}
    (OUT / "extraction_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
