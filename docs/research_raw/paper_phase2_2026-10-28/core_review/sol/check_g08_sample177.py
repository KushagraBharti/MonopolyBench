"""Common sample85: unapplied content build and received END, exact local check."""

import copy
import hashlib
import json
from pathlib import Path

from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def main():
    engine, decision, packet, provenance = prefix(8, 177)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    assert next(p["cash"] for p in before["players"] if p["player_id"] == actor) == 704
    assert [engine.state.board[i].houses for i in [16, 18, 19]] == [0, 0, 0]
    attempt = packet["attempts"][0]
    content = json.loads(attempt["assistant_content"])
    assert content["name"] == "build_houses_or_hotel"
    assert attempt["parsed_tool_call"]["name"] == "end_turn"
    actual = copy.deepcopy(engine)
    _, actual_events, _, _ = actual.apply_action(packet["applied_action_record"]["action"])
    assert not any(e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"} for e in actual_events)
    actual_cash = next(p["cash"] for p in actual.get_snapshot()["players"] if p["player_id"] == actor)
    assert actual_cash == 704
    proposed = content["arguments"]["build_plan"]
    assert [p["count"] for p in proposed] == [2, 2, 3]
    plan = [{"space_key": key, "kind": "HOUSE", "count": 1}
            for _ in range(2) for key in ["ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE"]]
    plan.append({"space_key": "NEW_YORK_AVENUE", "kind": "HOUSE", "count": 1})
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": "build_houses_or_hotel", "args": {"build_plan": plan}}
    _, events, _, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    assert [engine.state.board[i].houses for i in [16, 18, 19]] == [2, 2, 3]
    assert next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == actor) == 4
    report = {**provenance, "before": before, "received_attempt": attempt,
              "recorded_applied": packet["applied_action_record"], "actual_events": actual_events,
              "actual_cash": actual_cash, "interleaved_alternative": action,
              "alternative_events": events, "alternative_after": engine.get_snapshot(),
              "limits": "Complete sample177original available bundle and adjacent176/178read, with the truncated middle of returned reasoning separately repaired. Content proposes grouped2/2/3build; received toolEND and applied private claim already built/cash4 despite actual704/bareoranges. Affordable final allocation is legally reachable after interleaving, not a claim grouped content order itself was legal. No build was submitted to validator in history, no retry/default, no upstream cause or latent intended action, no future rent/winner. Provider explanation itself notices prior phantom construction then oscillates through plans; it is not a uniformly correct internal-state transcript.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g08_sample177_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "actual_cash": 704,
                      "alternative_cash": 4, "alternative_houses": [2, 2, 3]}))


if __name__ == "__main__":
    main()
