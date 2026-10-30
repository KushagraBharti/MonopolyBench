"""Immediate G17 financing checks after complete fixed-sample reading."""

import hashlib
import json
from pathlib import Path

from monopoly_engine.engine import PROPERTY_RENT_TABLES

from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 17]
    u = next(u for u in units if u["decision_id"].endswith("000236"))
    packet = ROOT / u["packet"]
    b = rows(packet)[u["packet_line"] - 1]
    run = ROOT / b["source_run"]
    group = ["ORIENTAL_AVENUE", "VERMONT_AVENUE", "CONNECTICUT_AVENUE"]
    reports = {}
    for develop in [False, True]:
        engine, decision = restore(run, u["decision_id"])
        steps = []

        def act(name, args):
            nonlocal decision
            assert decision["player_id"] == "p4"
            decision, record = apply(engine, decision, name, args)
            steps.append(record)

        if develop:
            act("mortgage_property", {"space_key": "NORTH_CAROLINA_AVENUE"})
            act("build_houses_or_hotel", {"build_plan": [
                {"space_key": k, "kind": "HOUSE", "count": 1} for k in group]})
        for _ in range(4 if develop else 3):
            for key in group:
                act("sell_houses_or_hotel", {"sell_plan": [
                    {"space_key": key, "kind": "HOUSE", "count": 1}]})
        for key in group + ["STATES_AVENUE", "VENTNOR_AVENUE"] + ([] if develop else ["NORTH_CAROLINA_AVENUE"]):
            act("mortgage_property", {"space_key": key})
        cash = next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == "p4")
        assert cash == (684 if develop else 759)
        reports["after_three_fourth_houses" if develop else "current"] = {"cash": cash, "steps": steps}
    assert [PROPERTY_RENT_TABLES[i][4] for i in [6, 8, 9]] == [400, 400, 450]
    events = rows(run / "events.jsonl")
    assert next(e for e in events if e["type"] == "PLAYER_MOVED" and e["seq"] == 1594)["payload"]["from"] == 36
    report = {"scope": "All twelve common bundles read. Two local management-state liquidation branches; no invented debt or future outcome.",
              "peer_exposure": "Sol nominated the 236 financing error; implementation independent, not blind.",
              "branches": reports, "four_house_rents": [400, 400, 450],
              "current_cash": b["initial_prompt"]["payload"]["game_state"]["you"]["cash"],
              "source_unit": u, "packet_sha256": hashlib.sha256(packet.read_bytes()).hexdigest(),
              "canonical_hashes": {n: hashlib.sha256((run / n).read_bytes()).hexdigest()
                                   for n in ["events.jsonl", "actions.jsonl", "run_config.json"]},
              "engine_sha256": hashlib.sha256((ROOT / "python/packages/engine/src/monopoly_engine/engine.py").read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    assert report["current_cash"] == 24
    (HERE / "g17_sample_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G17 sample checks pass: current financing 759, after three fourth houses 684; rent schedule 400/400/450.")


if __name__ == "__main__":
    main()
