import unittest

from prepare_behavior_review import batches, event_segments, prompt_copy, readable_copy


class PacketTests(unittest.TestCase):
    def test_events_partition_without_losing_prelude_or_terminal(self):
        events = [{"type": "GAME_STARTED"},
                  {"type": "LLM_DECISION_REQUESTED", "payload": {"decision_id": "a"}},
                  {"type": "CASH_CHANGED"},
                  {"type": "LLM_DECISION_REQUESTED", "payload": {"decision_id": "b"}},
                  {"type": "GAME_ENDED"}]
        segments = list(event_segments(events))
        self.assertEqual([x for _, _, part in segments for x in part], events)
        self.assertEqual([(did, line) for did, line, _ in segments], [("a", 1), ("b", 4)])

    def test_oversized_decision_is_preserved(self):
        units = [{"text": "a" * 40}, {"text": "b"}, {"text": "c"}]
        result = list(batches(units, 20))
        self.assertEqual([unit for batch in result for unit in batch], units)

    def test_only_encrypted_data_is_opaque(self):
        value = [{"type": "reasoning.encrypted", "data": "cipher"},
                 {"type": "reasoning.text", "text": "available"},
                 {"type": "ordinary", "data": "meaningful"}]
        result = readable_copy(value)
        self.assertTrue(result[0]["data"]["opaque"])
        self.assertEqual(result[1:], value[1:])
        self.assertEqual(value[0]["data"], "cipher")

    def test_prompt_dedup_only_when_semantically_identical_json(self):
        value = {"prompt_payload": {"cash": 5}, "prompt_payload_raw": '{ "cash": 5 }',
                 "prompt_messages": [{"role": "user", "content": '{"cash": 5}'},
                                     {"role": "system", "content": "instruction"},
                                     {"role": "user", "content": "extra instruction"}]}
        result = prompt_copy(value)
        self.assertEqual(result["messages"][0]["content"], {"exact_json_value_ref": "payload"})
        self.assertEqual(result["messages"][1:], value["prompt_messages"][1:])


if __name__ == "__main__":
    unittest.main()
