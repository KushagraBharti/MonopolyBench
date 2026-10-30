"""Independent, read-only readiness checks against the October corpus.

Run from any directory with Python. Derived JSON is written beside this script;
canonical game artifacts are never modified. This is descriptive analysis, not
a counterfactual evaluation or an estimate of population playing strength.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COLLECTIONS = [
    ROOT / "saved_games/railway-research-12-games-2026-10-25",
    ROOT / "saved_games/railway-research-8-games-2026-10-26",
]


def read(path: Path):
    return json.loads(path.read_text())


def main():
    totals = Counter()
    models = defaultdict(Counter)
    games, sources, management_examples = [], [], []
    response_example = None
    for collection in COLLECTIONS:
        for package in sorted(p for p in collection.glob("game-*") if p.is_dir()):
            run = package / "run"
            config, summary = read(run / "run_config.json"), read(run / "summary.json")
            names = {p["player_id"]: p["openrouter_model_id"] for p in config["players"]}
            events = [json.loads(line) for line in (run / "events.jsonl").open()]
            for filename in ["events.jsonl", "run_config.json", "summary.json"]:
                path = run / filename
                sources.append({"path": str(path.relative_to(ROOT)),
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            accepted = [e for e in events if e["type"] == "TRADE_ACCEPTED"]
            proposed = [e for e in events if e["type"] == "TRADE_PROPOSED"]
            builds = [e for e in events if e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}]
            first = builds[0] if builds else None
            winner = summary["winner_player_id"]
            participation = Counter(pid for e in accepted for pid in
                                    [e["payload"]["initiator_player_id"], e["payload"]["counterparty_player_id"]])
            game_number = int(package.name.split("-")[1])
            games.append({
                "game": game_number, "seed": config["seed"], "turns": summary["turn_count"],
                "winner": names[winner],
                "winner_seat_zero_based": next(i for i, p in enumerate(config["players"])
                                               if p["player_id"] == winner),
                "first_builder": names[first["payload"]["player_id"]] if first else None,
                "first_builder_won": bool(first and first["payload"]["player_id"] == winner),
                "first_build_event": first["event_id"] if first else None,
                "winner_completed_trades": participation[winner], "completed_trades": len(accepted),
                "package": str(package.relative_to(ROOT)),
            })
            totals.update(games=1, turns=summary["turn_count"], events=len(events),
                          decisions=sum(e["type"] == "LLM_DECISION_RESPONSE" for e in events),
                          initial_trade_proposals=len(proposed),
                          counteroffers=sum(e["type"] == "TRADE_COUNTERED" for e in events),
                          completed_trades=len(accepted), first_builder_wins=games[-1]["first_builder_won"])
            for pid, model in names.items():
                models[model].update(
                    player_games=1, wins=pid == winner,
                    proposals=sum(e["payload"]["initiator_player_id"] == pid for e in proposed),
                    received_proposals=sum(e["payload"]["counterparty_player_id"] == pid for e in proposed),
                    completed_trade_participations=participation[pid],
                    own_turns=summary["players"][pid]["turns_played"],
                    rent_received=sum(e["payload"]["amount"] for e in events if e["type"] == "RENT_PAID"
                                      and e["payload"]["to_player_id"] == pid))
            if game_number in {6, 8}:
                lower, upper = (74, 85) if game_number == 6 else (77, 87)
                for line in (run / "decisions.jsonl").open():
                    decision = json.loads(line)
                    if (decision["phase"] != "decision_started" or decision["player_id"] != "p4"
                            or not lower <= decision["turn_index"] <= upper):
                        continue
                    payload = decision.get("prompt_payload") or {}
                    state, action = payload.get("game_state", {}), payload.get("action_state", {})
                    management_examples.append({
                        "game": game_number, "decision_id": decision["decision_id"],
                        "turn": decision["turn_index"], "type": decision["decision_type"],
                        "cash": state.get("you", {}).get("cash"),
                        "in_jail": state.get("you", {}).get("in_jail"),
                        "available_actions": action.get("available_actions"),
                        "buildable_space_keys": action.get("scenario", {}).get("options", {}).get("buildable_space_keys"),
                    })
            if game_number == 1:
                path = next((run / "prompts").glob("*000112_response.json"))
                message = read(path)["choices"][0]["message"]
                content = json.loads(message["content"])
                function = message["tool_calls"][0]["function"]
                arguments = json.loads(function["arguments"])
                response_example = {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "content_action": content["name"], "tool_action": function["name"],
                    "arguments_equal": content["parameters"] == arguments,
                    "public_message": arguments["public_message"],
                    "interpretation": "Observable same-response inconsistency; latent intent and upstream cause are unidentified.",
                }
    result = {
        "scope": "Independent descriptive checks; no new games or changes to canonical evidence.",
        "totals": totals, "model_totals": models, "games": games,
        "counterexamples": [g for g in games if not g["first_builder_won"] or g["winner_completed_trades"] == 0],
        "management_access_examples": management_examples, "response_inconsistency_example": response_example,
        "interpretation_limits": [
            "Five seed blocks and one roster; player-game rows and repeated episodes are dependent.",
            "First-builder association does not identify a causal effect.",
            "First offered management window measures conditional responsiveness; jail/access choices and elapsed delay remain outcomes.",
            "Response inconsistency remains observable communication/action disagreement; it does not establish deliberate deception.",
        ],
        "sources": sources,
    }
    (OUT / "astra_independent_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"totals": totals, "models": models,
                      "response_inconsistency_example": response_example}, indent=2))


if __name__ == "__main__":
    main()
