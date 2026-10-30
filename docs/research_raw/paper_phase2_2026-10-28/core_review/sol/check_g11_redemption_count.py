"""Read-only rent calculations around actual redemptions; no invented landing."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import HERE, prefix


def active_rents(engine, actor):
    owner = next(p for p in engine.state.players if p.player_id == actor)
    electric = engine.state.board[12]
    reading = engine.state.board[5]
    assert electric.owner_id == reading.owner_id == actor
    assert not electric.mortgaged and not reading.mortgaged
    return {"electric_on_dice10": engine._calculate_rent(electric, owner, 10),
            "reading": engine._calculate_rent(reading, owner, 10)}


def main():
    game = units(11)
    engine, decision, _packet, provenance = prefix(11, 181)
    actor = decision["player_id"]
    before = active_rents(engine, actor)
    assert engine.state.board[28].mortgaged and engine.state.board[15].mortgaged
    steps = []
    for suffix in [181, 182]:
        action = game[suffix][0]["applied_action_record"]["action"]
        assert action["decision_id"] == decision["decision_id"]
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events)
        steps.append({"suffix": suffix, "action": action, "events": events, "active_sibling_rents_after": active_rents(engine, actor)})
    after = active_rents(engine, actor)
    assert before == after == {"electric_on_dice10": 100, "reading": 50}
    report = {**provenance, "original_source": game[181][1], "before_active_rents": before, "steps": steps,
              "after_active_rents": after,
              "claim": "The actual WW and PennRR redemptions activate their own landing spaces; they do not increase the already-active Electric or Reading rents. Both sibling rates already count the mortgaged owned deed.",
              "limits": "Direct read-only engine rent calculation for existing active siblings, with actual redemption actions. No alternate landing, debt, future receipt or optimality claim. No full provider bundle implied.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g11_redemption_count_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "before": before, "after": after, "claim": report["claim"]}))


if __name__ == "__main__":
    main()
