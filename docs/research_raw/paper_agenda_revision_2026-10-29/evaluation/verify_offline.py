"""Verify retained pilot data and execute safety/reproducibility checks."""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import socket
import tempfile
from collections import Counter
from pathlib import Path

import run_offline as runner


def read_jsonl(path: Path) -> list[dict]:
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f]


def stream_hash(values: list[dict]) -> str:
    h = hashlib.sha256()
    for value in values:
        h.update(runner.canonical(value) + b"\n")
    return h.hexdigest()


def replay(directory: Path) -> dict:
    config = json.loads((directory / "run_config.json").read_text())
    expected = json.loads((directory / "summary.json").read_text())
    actions = read_jsonl(directory / "actions.jsonl.gz")
    events = read_jsonl(directory / "events.jsonl.gz")
    decisions = read_jsonl(directory / "decisions.jsonl.gz")
    assert stream_hash(actions) == expected["action_stream_sha256"]
    assert stream_hash(events) == expected["event_stream_sha256"]
    assert len(actions) == expected["decisions_applied"]
    assert len(events) == expected["events"]
    engine = runner.Engine(seed=config["seed"], players=config["players"], run_id=config["run_id"], max_turns=None, ts_step_ms=1)
    assert engine.get_snapshot() == json.loads((directory / "initial_snapshot.json").read_text())
    emitted = []
    index = 0
    guard = 0
    while index < len(actions):
        guard += 1
        assert guard <= len(actions) * 10 + 1
        _, new_events, decision, _ = engine.advance_until_decision(max_steps=1)
        emitted.extend(new_events)
        if decision is None:
            continue
        assert decision == decisions[index]["decision"]
        action = actions[index]
        assert action == decisions[index]["generated_action"]
        policy = config["policies"][decision["player_id"]]
        assert runner.choose_baseline_action(decision, policy) == action
        assert not engine.validate_action_for_decision(action, decision)
        _, new_events, _, _ = engine.apply_action(action)
        emitted.extend(new_events)
        index += 1
    if expected["status"] == "terminated" and not engine.is_game_over():
        _, new_events, decision, _ = engine.advance_until_decision(max_steps=1)
        emitted.extend(new_events)
        assert decision is None
    assert emitted == events
    assert engine.get_snapshot() == json.loads((directory / "final_snapshot.json").read_text())
    assert runner.digest(engine.get_snapshot()) == expected["final_snapshot_sha256"]
    assert Counter(a["action"] for a in actions) == expected["action_counts"]
    if expected["status"] != "terminated":
        assert expected["winner_player_id"] is None
        assert expected["winner_policy"] is None
    return {"run_id": config["run_id"], "actions": len(actions), "events": len(events), "exact_replay": True}


def expect_rejection(fn, kind: type[Exception]) -> bool:
    try:
        fn()
    except kind:
        return True
    raise AssertionError("Expected rejection did not occur")


def tests(protocol: dict, out: Path) -> dict:
    checks = {}
    checks["known_protocol_valid"] = runner.load_protocol(runner.HERE / "protocol.json") == protocol
    with tempfile.TemporaryDirectory(prefix="monopoly-offline-guards-") as tmp:
        path = Path(tmp) / "protocol.json"
        for name, edit in [
            ("paid_enabled_rejected", lambda d: d["paid_run_gate"].update(enabled=True)),
            ("network_enabled_rejected", lambda d: d["offline_pilot"].update(network_allowed=True)),
            ("nonzero_spend_rejected", lambda d: d["offline_pilot"].update(spending_cap_usd=1)),
            ("unbounded_limit_rejected", lambda d: d["offline_pilot"].update(decision_limit=0)),
            ("unknown_policy_rejected", lambda d: d["offline_pilot"].update(mixed_roster=["not_a_policy"] * 4)),
            ("engine_turn_limit_rejected", lambda d: d["offline_pilot"].update(engine_max_turns=100)),
        ]:
            changed = copy.deepcopy(protocol)
            edit(changed)
            path.write_text(json.dumps(changed))
            checks[name] = expect_rejection(lambda: runner.load_protocol(path), ValueError)
    players = [{"player_id": f"p{i}", "name": f"p{i}"} for i in range(1, 5)]
    engine = runner.Engine(seed=81, players=players, run_id="guard-only-not-a-research-game", max_turns=None)
    _, _, decision, _ = engine.advance_until_decision(max_steps=1)
    assert decision is not None
    invalid = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "not_an_action", "args": {}}
    checks["invalid_action_rejected"] = bool(engine.validate_action_for_decision(invalid, decision))
    checks["invalid_action_apply_rejected"] = expect_rejection(lambda: engine.apply_action(invalid), ValueError)
    checks["unknown_baseline_rejected"] = expect_rejection(lambda: runner.choose_baseline_action(decision, "not_a_policy"), ValueError)
    # The audit hook raises before the operating system attempts a connection.
    with socket.socket() as sock:
        checks["network_attempt_blocked_before_connect"] = expect_rejection(lambda: sock.connect(("127.0.0.1", 9)), RuntimeError)
    assert runner.NETWORK_ATTEMPTS == ["socket.connect"]
    scenario_path = runner.ROOT / "contracts/micro/scenarios/auction-railroad-first-01.json"
    if not scenario_path.exists():
        scenario_path = next((runner.ROOT / "contracts/micro/scenarios").glob("auction-*.json"))
    scenario = json.loads(scenario_path.read_text())
    decision = scenario["decision_point"]
    overspend = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "bid_auction", "args": {"bid_amount": 10**9}, "public_message": "", "private_thought": "fixture mutation"}
    checks["unaffordable_auction_rejected"] = bool(runner.validate_fixture_action(decision, overspend))
    raw = [{"seq": 1, "type": "test"}]
    corrupted = copy.deepcopy(raw)
    corrupted[0]["seq"] = 2
    checks["event_mutation_changes_digest"] = stream_hash(raw) != stream_hash(corrupted)
    assert all(checks.values())
    result = {"status": "pass", "checks": checks, "count": len(checks), "network_guard_test_attempts": 1, "actual_network_connections": 0, "provider_calls": 0, "test_fixture_scope": "Guard tests and one pending decision are synthetic tests, not additional research games"}
    runner.save_json(out / "guard_tests.json", result)
    return result


def main() -> None:
    out = runner.HERE / "results"
    protocol = runner.load_protocol(runner.HERE / "protocol.json")
    sources = json.loads((out / "sources_before.json").read_text())
    assert runner.source_manifest() == sources
    replays = [replay(p) for p in sorted((out / "games").iterdir()) if p.is_dir()]
    assert len(replays) == protocol["offline_pilot"]["primary_games"]
    fixture_rows = json.loads((out / "baseline_fixture_actions.json").read_text())
    for row in fixture_rows:
        path = runner.ROOT / "contracts/micro/scenarios" / f"{row['scenario_id']}.json"
        decision = json.loads(path.read_text())["decision_point"]
        assert runner.choose_baseline_action(decision, row["policy"]) == row["action"]
        assert runner.validate_fixture_action(decision, row["action"]) == row["economic_legality_errors"]
    reference_rows = json.loads((out / "reference_fixture_actions.json").read_text())
    for row in reference_rows:
        path = runner.ROOT / "contracts/micro/scenarios" / f"{row['scenario_id']}.json"
        decision = json.loads(path.read_text())["decision_point"]
        assert runner.validate_fixture_action(decision, row["action"]) == row["errors"]
    guard = tests(protocol, out)
    result = {"status": "pass", "replayed_games": len(replays), "replayed_actions": sum(x["actions"] for x in replays), "replayed_events": sum(x["events"] for x in replays), "replays": replays, "baseline_fixture_choices_rechecked": len(fixture_rows), "reference_fixture_choices_rechecked": len(reference_rows), "protected_source_hashes_unchanged": runner.source_manifest() == sources, "guard_checks": guard["count"], "scope": "Same-engine replay and exact artifact consistency; not an independent engine implementation or strategic validity proof"}
    runner.save_json(out / "verification.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "replays"}, sort_keys=True))


if __name__ == "__main__":
    main()
