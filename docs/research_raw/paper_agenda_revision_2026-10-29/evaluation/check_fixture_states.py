"""Follow-up static-state diagnostic; source scenarios are never modified."""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import run_offline as runner


def main() -> None:
    rows = []
    for path in sorted((runner.ROOT / "contracts/micro/scenarios").glob("*.json")):
        scenario = json.loads(path.read_text())
        decision = scenario["decision_point"]
        state = decision["state"]
        groups = defaultdict(list)
        failures = []
        for space in state["board"]:
            if space.get("group"):
                groups[space["group"]].append(space)
        houses = sum(int(s.get("houses") or 0) for s in state["board"])
        hotels = sum(bool(s.get("hotel")) for s in state["board"])
        if state["bank"]["houses_remaining"] != 32 - houses:
            failures.append({"type": "house_stock_conservation", "declared": state["bank"]["houses_remaining"], "board_implied": 32 - houses})
        if state["bank"]["hotels_remaining"] != 12 - hotels:
            failures.append({"type": "hotel_stock_conservation", "declared": state["bank"]["hotels_remaining"], "board_implied": 12 - hotels})
        for group, spaces in groups.items():
            levels = [5 if s.get("hotel") else int(s.get("houses") or 0) for s in spaces]
            if not any(levels):
                continue
            owners = {s.get("owner_id") for s in spaces}
            if len(owners) != 1 or None in owners:
                failures.append({"type": "developed_group_ownership", "group": group, "owners": sorted(owners, key=str)})
            if any(s.get("mortgaged") for s in spaces):
                failures.append({"type": "developed_group_mortgage", "group": group})
            if max(levels) - min(levels) > 1:
                failures.append({"type": "uneven_development", "group": group, "levels": levels})
        if decision.get("liquidation"):
            liq = decision["liquidation"]
            player = next(p for p in state["players"] if p["player_id"] == decision["player_id"])
            implied = max(0, liq["owed_amount"] - player["cash"])
            if liq["shortfall"] != implied:
                failures.append({"type": "liquidation_shortfall", "declared": liq["shortfall"], "cash": player["cash"], "owed": liq["owed_amount"], "implied": implied})
        rows.append({"scenario_id": scenario["scenario_id"], "source_sha256": runner.file_digest(path), "failures": failures})
    summary = {"scenarios": len(rows), "scenarios_with_at_least_one_failure": sum(bool(x["failures"]) for x in rows), "failure_types": dict(Counter(f["type"] for row in rows for f in row["failures"])), "scope": "Specified static invariants only; no proof of full reachability or optimal reference choice", "adaptive_status": "Follow-up after initial legality audit", "protocol_sha256": runner.file_digest(runner.HERE / "fixture_state_checks_protocol.json")}
    runner.save_json(runner.HERE / "results/fixture_state_checks.json", {"summary": summary, "rows": rows})
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
