"""Adversarial checks with altered witnesses and independently invalid actions."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import run_audit as audit


def restore(case_id):
    case = next(row for row in audit.read(audit.HERE / "cases.json") if row["case_id"] == case_id)
    folder = audit.HERE / "inputs" / f'g{case["game"]:02d}'
    engine = audit.Engine(**audit.read(folder / "config.json"))
    digest = hashlib.sha256()
    count = 0
    for line in (folder / "actions.jsonl").read_text().splitlines():
        record = json.loads(line)
        _, events, decision, _ = engine.advance_until_decision(max_steps=100000)
        for event in events:
            digest.update(audit.canonical(event) + b"\n")
            count += 1
        if decision["decision_id"] == case["decision_id"]:
            if digest.hexdigest() != case["prefix"]["canonical_prefix_sha256"] or count != case["prefix"]["event_count"]:
                raise ValueError("Corrupted historical prefix")
            return engine, decision, case
        _, events, _, _ = engine.apply_action(record["action"], decision_meta=record.get("decision_meta"))
        for event in events:
            digest.update(audit.canonical(event) + b"\n")
            count += 1
    raise ValueError("Case not reached")


class Certificates(unittest.TestCase):
    def test_frozen_inputs(self):
        audit.check_inputs()

    def test_tampered_hash_rejected(self):
        original = audit.HERE
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "actions.jsonl").write_text("corrupted\n")
            (root / "inputs_manifest.json").write_text(json.dumps({"files": {
                "actions.jsonl": hashlib.sha256(b"authentic\n").hexdigest()}}))
            try:
                audit.HERE = root
                with self.assertRaisesRegex(ValueError, "Input hash mismatch"):
                    audit.check_inputs()
            finally:
                audit.HERE = original

    def test_historical_action_mutation_changes_event_hash(self):
        folder = audit.HERE / "inputs/g01"
        move = json.loads((folder / "actions.jsonl").read_text().splitlines()[0])
        engine = audit.Engine(**audit.read(folder / "config.json"))
        _, prefix, _, _ = engine.advance_until_decision(max_steps=100000)
        move["action"]["public_message"] = "Deliberately altered replay record"
        _, events, _, _ = engine.apply_action(move["action"], decision_meta=move["decision_meta"])
        expected = audit.read(folder / "event_hashes.json")
        self.assertNotEqual([audit.sha(e) for e in events], expected[len(prefix):len(prefix) + len(events)])

    def test_allocation_change_detected(self):
        engine, decision, case = restore("G02-dec-000075-default")
        plan = next(a["plan"] for a in case["attempts"] if "plan" in a)
        expanded = audit.atomic_plan(engine, plan)
        self.assertEqual(audit.multiset(plan), audit.multiset(expanded))
        corrupted = expanded[:-1]
        self.assertNotEqual(audit.multiset(plan), audit.multiset(corrupted))
        # Reachability alone cannot certify preservation of the requested target.
        self.assertTrue(audit.build_trial(engine, decision, expanded)["legal"])
        self.assertFalse(audit.build_trial(engine, decision, plan)["legal"])

    def test_locked_hotel_sale_rejected(self):
        engine, decision, _ = restore("G07-dec-000339-elimination")
        self.assertEqual(engine.get_snapshot()["bank"]["houses_remaining"], 0)
        with self.assertRaises(ValueError):
            audit.apply_checked(engine, decision, "sell_houses_or_hotel", {"sell_plan": [
                {"space_key": "VIRGINIA_AVENUE", "kind": "HOTEL", "count": 1}]})

    def test_unlocked_mortgage_cannot_be_moved_before_sales(self):
        engine, decision, _ = restore("G12-dec-000190-elimination")
        with self.assertRaises(ValueError):
            audit.apply_checked(engine, decision, "mortgage_property", {"space_key": "ILLINOIS_AVENUE"})

    def test_missing_mortgage_does_not_pay(self):
        engine, decision, case = restore("G12-dec-000190-elimination")
        debt = decision["liquidation"]["owed_amount"]
        witness = audit.greedy_payment(engine, decision, case["actor"], debt)
        self.assertTrue(witness["paid"])
        self.assertEqual(witness["steps"][-1]["action"], "mortgage_property")
        paid = False
        for step in witness["steps"][:-1]:
            decision, actual = audit.apply_checked(engine, decision, step["action"], step["args"])
            paid |= audit.payment_in(actual["events"], case["actor"], debt)
        self.assertFalse(paid)
        self.assertLess(audit.actor(engine, case["actor"]).cash, debt)

    def test_certificate_at_triggering_state_is_complete(self):
        engine, decision, case = restore("G07-dec-000339-elimination")
        choices = audit.liquidation_actions(engine, decision)
        self.assertEqual(choices, [("mortgage_property", {"space_key": "ORIENTAL_AVENUE"})])
        proof = audit.exhaustive_financing(engine, decision, case["actor"], 750)
        self.assertTrue(proof["exhausted"])
        self.assertFalse(proof["paid"])
        self.assertEqual(proof["state_count"], 1)
        self.assertTrue(proof["nodes"][0]["edges"][0]["bankrupt"])

    def test_bundled_sale_blocks_atomic_impossibility_certificate(self):
        # Fresh-review counterexample. Synthetic, inventory-conserving state;
        # this is a verifier regression, not a historical or optimal-play claim.
        config = audit.read(audit.HERE / "inputs/g01/config.json")
        config["run_id"] = "certificate-bundled-sale-regression"
        engine = audit.Engine(**config)
        engine._started = True
        engine.state.phase = "RUNNING"
        debtor = engine.state.players[0]
        debtor.cash = 0
        debtor.position = 24
        for index in (1, 3):
            space = engine.state.board[index]
            space.owner_id, space.houses = debtor.player_id, 1
        for index in (37, 39):
            space = engine.state.board[index]
            space.owner_id, space.hotel = debtor.player_id, True
        for indices in ((6, 8, 9), (16, 18, 19), (21, 23, 24)):
            for index, houses in zip(indices, (4, 3, 3)):
                space = engine.state.board[index]
                space.owner_id, space.houses = engine.state.players[1].player_id, houses
        engine.state.bank.houses_remaining = 0
        engine.state.bank.hotels_remaining = 10
        self.assertEqual(sum(s.houses for s in engine.state.board), 32)
        self.assertEqual(sum(s.hotel for s in engine.state.board), 2)
        events = []
        debt = engine._calculate_rent(engine.state.board[24], engine.state.players[1], 6)
        self.assertEqual(debt, 750)
        payment = {"amount": debt, "reason": "RENT", "kind": "RENT",
                   "to_player_id": "p2", "space_index": 24}
        decision = engine._request_payment(debtor, payment, events,
                                           turn_index=0, rolled_double=False)
        engine._activate_debt_decision(decision, events)
        case = {"case_id": "synthetic", "kind": "elimination", "game": 0,
                "model": "synthetic", "actor": debtor.player_id,
                "decision_id": decision["decision_id"], "classification": "declared"}
        with self.assertRaisesRegex(ValueError, "bundled building sales are not enumerated"):
            audit.check_elimination(engine, decision, case)
        plan = []
        for key in ("PARK_PLACE", "BOARDWALK"):
            plan += [{"space_key": key, "kind": "HOTEL", "count": 1},
                     {"space_key": key, "kind": "HOUSE", "count": 4}]
        _, result = audit.apply_checked(engine, decision, "sell_houses_or_hotel", {"sell_plan": plan})
        self.assertTrue(audit.payment_in(result["events"], debtor.player_id, debt))
        self.assertEqual(audit.actor(engine, debtor.player_id).cash, 250)


if __name__ == "__main__":
    unittest.main(verbosity=2)
