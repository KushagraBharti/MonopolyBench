"""Selected G14 accounting, ownership and liquidation checks from originals."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, rows
from monopoly_engine.board import PROPERTY_RENT_TABLES

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 14]
    selected = {93, 94, 139, 140, 161, 162, 217, 222, 223, 225, 234}
    packets = {int(u["decision_id"][-6:]): rows(ROOT / u["packet"])[u["packet_line"] - 1]
               for u in units if int(u["decision_id"][-6:]) in selected}
    run = ROOT / packets[140]["source_run"]
    events = rows(run / "events.jsonl")
    accepted = [e for e in events if e["type"] == "TRADE_ACCEPTED"]
    winner_trades = [e for e in accepted if "p1" in {e["payload"]["initiator_player_id"],
                                                     e["payload"]["counterparty_player_id"]}]
    assert winner_trades == []
    dispositions = [check(14, 209, 346), check(14, 222, 522), check(14, 234, 907)]
    state225 = packets[225]["initial_prompt"]["payload"]["game_state"]
    rail_keys = {"READING_RAILROAD", "PENNSYLVANIA_RAILROAD", "B_O_RAILROAD", "SHORT_LINE"}
    rails = [s for s in state225["you"]["holdings"]["owned"] if s["space_key"] in rail_keys]
    assert len(rails) == 3 and "B_O_RAILROAD" in state225["bank"]["unowned_space_keys"]
    preceding_rail_rents = [e for e in events if e["type"] == "RENT_PAID"
                            and e["seq"] < 1660 and e["payload"]["space_index"] == 15]
    assert preceding_rail_rents[-1]["payload"]["amount"] == 100
    assert sum(s["houses"] for s in state225["you"]["holdings"]["owned"]) == 32
    assert state225["bank"]["houses_remaining"] == 0
    brown_exchange_cash = {}
    for n in [94, 139]:
        by_player = {p: sum(e["payload"]["delta"] for e in packets[n]["canonical_event_segment"]
                           if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "TRADE_CASH"
                           and e["payload"]["player_id"] == p) for p in ["p2", "p3"]}
        brown_exchange_cash[n] = by_player
    assert brown_exchange_cash == {94: {"p2": 200, "p3": -200}, 139: {"p2": -100, "p3": 100}}
    ventnor_events = packets[161]["canonical_event_segment"]
    assert any(e["type"] == "PROPERTY_TRANSFERRED" and e["payload"]["space_index"] == 27
               and e["payload"]["to_player_id"] == "p2" for e in ventnor_events)
    assert packets[162]["applied_action_record"]["action"]["action"] == "unmortgage_property"
    assert PROPERTY_RENT_TABLES[32][3:5] == [900, 1100] or tuple(PROPERTY_RENT_TABLES[32][3:5]) == (900, 1100)
    report = {"scope": "Selected original-source checks and three exact legal liquidation ceilings. Not full semantic review of all game decisions.",
              "winner_completed_trades": len(winner_trades), "game_accepted_trades": len(accepted),
              "brown_exchange_cash": brown_exchange_cash,
              "ventnor_completion_decision": packets[161]["decision_id"],
              "ventnor_redemption_decision": packets[162]["decision_id"],
              "rails_at_d225": rails, "prior_pennsylvania_rail_rent": preceding_rail_rents[-1],
              "houses_owned_at_d225": 32, "liquidation_checks": dispositions,
              "local_final_landing_schedule": {"three_house_rent": 900, "four_house_rent": 1100,
                                                "actual_resource_ceiling": 907,
                                                "qualification": "Local schedule comparison only. No alternative winner or earlier resource trajectory inferred."},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "packet_sha256": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                 for u in units if int(u["decision_id"][-6:]) in selected},
              "source_sha256": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                                for n in ["actions.jsonl", "events.jsonl", "run_config.json"]},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g14_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G14 verified: winner completed zero trades; liquidation ceilings346/522/907; three railroads, not four; brown cash directions; completion161 versus redemption162.")


if __name__ == "__main__":
    main()
