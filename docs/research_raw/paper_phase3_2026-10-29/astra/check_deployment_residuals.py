"""Independent check of Opus's peer-nominated eight non-build cases.

Uses the final management decision, not any conflict earlier in that turn.
Channel conflict describes received records; content is not privileged intent.
"""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CORE = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review"
EPISODES = ROOT / "docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl"


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    econ = json.loads((CORE / "astra/development_aggregation_check.json").read_text())
    paths = {
        int(p.split("/game-")[1][:2]): ROOT / p for p in econ["event_source_hashes"]
    }
    eps = [json.loads(line) for line in EPISODES.read_text().splitlines()]
    pop = [e for e in eps if e["route"] == "trade" and e["entry_legal"]]
    residual = [e for e in pop if not e["built_first_management"]]
    assert len(pop) == 42 and len(residual) == 8
    sources = {str(EPISODES.relative_to(ROOT)): digest(EPISODES)}
    results = []
    counts = defaultdict(Counter)
    for ep in residual:
        p = paths[ep["game"]].parent / "decisions.jsonl"
        sources[str(p.relative_to(ROOT))] = digest(p)
        rows = [
            (i + 1, json.loads(s)) for i, s in enumerate(p.read_text().splitlines())
        ]
        ds = [
            (line, d)
            for line, d in rows
            if d.get("phase") == "decision_resolved"
            and d["player_id"] == ep["player_id"]
            and d["turn_index"] == ep["first_management_turn"]
            and d["decision_type"] == "POST_TURN_ACTION_DECISION"
            and d["decision_id"] >= ep["first_management_decision"]
        ]
        line, d = ds[-1]
        assert d["final_action"]["action"] == "end_turn"
        valid = [(i, a) for i, a in enumerate(d["attempts"]) if a["outcome"] == "valid"]
        selected = valid[-1] if valid else None
        content_name = None
        if selected:
            parsed = json.loads(selected[1]["assistant_content"])
            content_name = parsed["name"]
            received_name = selected[1]["parsed_tool_call"]["name"]
            assert received_name == "end_turn"
        if d["fallback_used"]:
            assert not valid
            assert any(
                (a.get("parsed_tool_call") or {}).get("name") == "build_houses_or_hotel"
                for a in d["attempts"]
            )
            category = "engine_default"
        elif content_name != "end_turn":
            assert content_name in {"build_houses_or_hotel", "mortgage_property"}
            category = "received_content_tool_conflict"
        else:
            note = d["final_action"]["private_thought"]
            assert "Do NOT build this turn" in note or "Do not house browns yet" in note
            category = "consistent_end_with_stated_reserve"
        counts[ep["model"]][category] += 1
        results.append(
            {
                "game": ep["game"],
                "model": ep["model"],
                "group": ep["group"],
                "decision_id": d["decision_id"],
                "turn": d["turn_index"],
                "category": category,
                "applied_action": d["final_action"]["action"],
                "selected_content_name": content_name,
                "selected_attempt_index": selected[0] if selected else None,
                "attempt_outcomes": [a["outcome"] for a in d["attempts"]],
                "source": str(p.relative_to(ROOT)),
                "line": line,
                "final_action": d["final_action"],
            }
        )
    assert Counter(r["category"] for r in results) == {
        "engine_default": 3,
        "received_content_tool_conflict": 3,
        "consistent_end_with_stated_reserve": 2,
    }
    result = {
        "peer_provenance": "Opus nominated this residual breakdown before Astra's original-record check; independent implementation, not blind replication.",
        "population": 42,
        "built": 34,
        "residual": 8,
        "rows": results,
        "counts_by_model": counts,
        "source_sha256": sources,
        "script_sha256": digest(Path(__file__)),
        "limits": "Final-decision record classification. No repaired-rate, intent, optimality or winner inference. G12's content plan need not be executable as encoded. G20 selected attempt is 1 after a malformed attempt 0.",
    }
    (HERE / "deployment_residual_check.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result["counts_by_model"], indent=2))


if __name__ == "__main__":
    main()
