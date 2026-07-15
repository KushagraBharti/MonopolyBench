from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "scripts" / "analyze_negotiation_tactics.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("analyze_negotiation_tactics", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _bundle(*, cash: int = 0, properties: list[str] | None = None) -> dict[str, object]:
    return {
        "cash": cash,
        "properties": properties or [],
        "get_out_of_jail_cards": 0,
    }


def _event(
    seq: int,
    event_type: str,
    actor: str | None,
    offer: dict[str, object],
    request: dict[str, object],
) -> dict[str, object]:
    return {
        "schema_version": "v1",
        "run_id": "run-negotiation",
        "event_id": f"evt-{seq}",
        "seq": seq,
        "turn_index": 7,
        "actor": {"kind": "PLAYER" if actor else "ENGINE", "player_id": actor},
        "type": event_type,
        "payload": {
            "initiator_player_id": "p1",
            "counterparty_player_id": "p2",
            "exchange_index": max(0, seq - 1),
            "offer": offer,
            "request": request,
        },
    }


def _decision(
    decision_id: str,
    event_id: str,
    seq: int,
    player_id: str,
    model_id: str,
    action: str,
    message: str,
) -> dict[str, object]:
    return {
        "run_id": "run-negotiation",
        "decision_id": decision_id,
        "player_id": player_id,
        "openrouter_model_id": model_id,
        "model_display_name": model_id,
        "final_action": {
            "action": action,
            "args": {},
            "public_message": message,
            "private_thought": "not exported",
        },
        "emitted_event_ids": [event_id],
        "emitted_event_seq_start": seq,
        "emitted_event_seq_end": seq,
    }


def test_analyzer_extracts_offers_tactics_and_model_frequencies(tmp_path: Path) -> None:
    module = _load_module()
    run_dir = tmp_path / "saved" / "run"
    output_dir = tmp_path / "output"
    first_offer = _bundle(cash=50)
    first_request = _bundle(properties=["BALTIC_AVENUE"])
    second_offer = _bundle(properties=["BALTIC_AVENUE"])
    second_request = _bundle(cash=100)
    final_offer = _bundle(cash=60)
    final_request = _bundle(properties=["BALTIC_AVENUE"])
    events = [
        _event(1, "TRADE_PROPOSED", "p1", first_offer, first_request),
        _event(2, "TRADE_COUNTERED", "p2", second_offer, second_request),
        _event(3, "TRADE_COUNTERED", "p1", final_offer, final_request),
        _event(4, "TRADE_ACCEPTED", "p2", final_offer, final_request),
    ]
    _write_jsonl(run_dir / "events.jsonl", events)
    decisions = [
        _decision(
            "d1",
            "evt-1",
            1,
            "p1",
            "model-a",
            "propose_trade",
            "This is fair because it completes your monopoly.",
        ),
        _decision(
            "d2",
            "evt-2",
            2,
            "p2",
            "model-b",
            "counter_trade",
            "This is my final offer.",
        ),
        _decision(
            "d3",
            "evt-3",
            3,
            "p1",
            "model-a",
            "counter_trade",
            "I can improve the cash.",
        ),
        _decision("d4", "evt-4", 4, "p2", "model-b", "accept_trade", "Accepted."),
    ]
    _write_jsonl(run_dir / "decisions.jsonl", decisions)
    manifest = module.analyze_sources(
        [run_dir],
        output_dir,
        board_path=ROOT / "contracts" / "data" / "board.json",
    )

    assert manifest["counts"] == {
        "runs": 1,
        "episodes": 1,
        "offers": 3,
        "tactic_uses": 11,
    }
    with (output_dir / "negotiation_offers.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        offers = list(csv.DictReader(handle))
    assert offers[0]["is_initial_offer"] == "1"
    assert offers[-1]["is_final_submitted_offer"] == "1"
    assert offers[-1]["is_accepted_offer"] == "1"
    assert offers[-1]["concession_face_value"] == "10"
    assert "private_thought" not in offers[-1]

    with (output_dir / "negotiation_tactics.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        tactics = list(csv.DictReader(handle))
    tactic_ids = {(row["offer_id"], row["tactic_id"]) for row in tactics}
    assert (offers[0]["offer_id"], "INITIAL_ANCHOR") in tactic_ids
    assert (offers[0]["offer_id"], "FAIRNESS_FRAMING") in tactic_ids
    assert (offers[0]["offer_id"], "VALUE_FRAMING") in tactic_ids
    assert (offers[0]["offer_id"], "RATIONALE_DISCLOSURE") in tactic_ids
    assert (offers[1]["offer_id"], "TAKE_IT_OR_LEAVE_IT") in tactic_ids
    assert (offers[2]["offer_id"], "CONCESSION") in tactic_ids
    with (output_dir / "negotiation_episodes.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        episodes = list(csv.DictReader(handle))
    assert episodes[0]["outcome"] == "TRADE_ACCEPTED"
    assert episodes[0]["offer_count"] == "3"

    with (output_dir / "model_negotiation_summary.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        models = {row["model_id"]: row for row in csv.DictReader(handle)}
    assert models["model-a"]["offer_count"] == "2"
    assert models["model-a"]["accepted_offer_count"] == "1"
    assert models["model-b"]["offer_count"] == "1"


def test_frequency_tables_support_cross_run_model_bias_analysis() -> None:
    module = _load_module()
    offers = [
        {
            "run_id": "run-a",
            "episode_id": "episode-a",
            "offer_id": "offer-a",
            "model_id": "model-a",
            "model_display_name": "Model A",
        },
        {
            "run_id": "run-b",
            "episode_id": "episode-b",
            "offer_id": "offer-b",
            "model_id": "model-a",
            "model_display_name": "Model A",
        },
    ]
    tactics = [
        {**offers[0], "tactic_id": "FAIRNESS_FRAMING", "tactic_family": "language"},
        {**offers[1], "tactic_id": "FAIRNESS_FRAMING", "tactic_family": "language"},
    ]
    aggregate = module.tactic_frequency_rows(offers, tactics, include_run=False)
    by_run = module.tactic_frequency_rows(offers, tactics, include_run=True)
    summary = module.model_summary_rows(offers, tactics)

    assert aggregate[0]["tactic_use_count"] == 2
    assert aggregate[0]["frequency_per_offer"] == 1.0
    assert {row["run_id"] for row in by_run} == {"run-a", "run-b"}
    assert summary[0]["run_count"] == 2
    assert summary[0]["dominant_language_tactic"] == "FAIRNESS_FRAMING"
