import unittest
from checkpoint_audit import Ledger

BOARD = [{"index": 1, "name": "Test Avenue", "price": 100}]


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger(["p1", "p2"], BOARD)

    def event(self, kind, **payload):
        self.ledger.apply({"type": kind, "payload": payload})

    def buy(self, pid="p1", price=100):
        self.event("PROPERTY_PURCHASED", player_id=pid, space_index=1, price=price)

    def test_cash_only_changes_via_cash_events(self):
        self.buy()
        self.assertEqual(self.ledger.cash["p1"], 1500)
        self.event("CASH_CHANGED", player_id="p1", delta=-100, reason="buy_property")
        self.assertEqual(self.ledger.cash["p1"], 1400)

    def test_creditor_inherits_development_and_mortgage(self):
        for mortgaged, houses in [(False, 2), (True, 0)]:
            with self.subTest(mortgaged=mortgaged, houses=houses):
                self.ledger = Ledger(["p1", "p2"], BOARD)
                self.buy()
                if mortgaged:
                    self.event("PROPERTY_MORTGAGED", space_index=1)
                if houses:
                    self.event("HOUSE_BUILT", space_index=1, count=houses)
                self.buy("p2", 0)
                self.assertEqual(self.ledger.assets[1], {"owner":"p2", "houses":houses, "hotel":False, "mortgaged":mortgaged})
                self.assertEqual(self.ledger.bank_houses, 32 - houses)

    def test_bank_return_clears_buildings_and_mortgage_even_without_cash(self):
        self.buy()
        self.event("PROPERTY_MORTGAGED", space_index=1)
        self.event("PROPERTY_UNMORTGAGED", space_index=1)
        self.event("HOUSE_BUILT", space_index=1, count=4)
        self.event("HOTEL_BUILT", space_index=1, count=1)
        self.event("CASH_CHANGED", player_id="p1", delta=0, reason="BANKRUPTCY_ASSETS_TO_BANK")
        self.assertEqual(self.ledger.assets[1], {"owner":None, "houses":0, "hotel":False, "mortgaged":False})
        self.assertEqual((self.ledger.bank_houses, self.ledger.bank_hotels), (32,12))

    def test_hotel_downgrade_and_house_sale(self):
        self.buy()
        self.event("HOUSE_BUILT", space_index=1, count=4)
        self.event("HOTEL_BUILT", space_index=1, count=1)
        self.assertEqual((self.ledger.bank_houses, self.ledger.bank_hotels), (32,11))
        self.event("HOTEL_SOLD", space_index=1, count=1)
        self.event("HOUSE_SOLD", space_index=1, count=2)
        self.assertEqual(self.ledger.assets[1]["houses"], 2)
        self.assertEqual((self.ledger.bank_houses, self.ledger.bank_hotels), (30,12))

    def test_transfer_retains_mortgage_and_rejects_wrong_owner(self):
        self.buy()
        self.event("PROPERTY_MORTGAGED", space_index=1)
        self.event("PROPERTY_TRANSFERRED", space_index=1, from_player_id="p1", to_player_id="p2", mortgaged=True)
        self.assertTrue(self.ledger.assets[1]["mortgaged"])
        with self.assertRaises(ValueError):
            self.event("PROPERTY_TRANSFERRED", space_index=1, from_player_id="p1", to_player_id="p2", mortgaged=True)

    def test_observation_cash_mismatch_is_detected(self):
        observed = {"you":{"player_id":"p1", "cash":1499, "holdings":{"owned":[],"mortgaged":[]}},
                    "others":[{"player_id":"p2", "cash":1500, "holdings":{"owned":[],"mortgaged":[]}}],
                    "bank":{"houses_remaining":32,"hotels_remaining":12,"unowned_space_keys":["TEST_AVENUE"]}}
        self.assertEqual([x["field"] for x in self.ledger.compare(observed)], ["cash.p1"])
        observed["you"]["cash"] = 1500
        self.assertEqual(self.ledger.compare(observed), [])

    def test_mortgage_list_uses_structured_space_keys(self):
        self.buy()
        self.event("PROPERTY_MORTGAGED", space_index=1)
        observed = {"you":{"player_id":"p1", "cash":1500, "holdings":{
            "owned":[{"space_key":"TEST_AVENUE", "houses":0,"hotel":False,"mortgaged":True}],
            "mortgaged":[{"space_key":"TEST_AVENUE"}]}},
            "others":[{"player_id":"p2","cash":1500,"holdings":{"owned":[],"mortgaged":[]}}],
            "bank":{"houses_remaining":32,"hotels_remaining":12,"unowned_space_keys":[]}}
        self.assertEqual(self.ledger.compare(observed), [])


if __name__ == "__main__":
    unittest.main()
