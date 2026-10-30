import unittest

from visibility_inventory import final_note_origin, reasoning_inventory


class VisibilityTests(unittest.TestCase):
    def response(self, **message):
        return {"choices": [{"message": message}]}

    def test_token_counts_are_not_reasoning_text(self):
        self.assertEqual(reasoning_inventory({"usage": {"reasoning_tokens": 900}}), [])

    def test_content_and_private_argument_are_not_provider_reasoning(self):
        response = self.response(content='{"private_thought":"plan"}',
                                 tool_calls=[{"function": {"arguments": '{"private_thought":"plan"}'}}])
        self.assertEqual(reasoning_inventory(response), [])

    def test_plain_provider_reasoning_is_readable(self):
        result = reasoning_inventory(self.response(reasoning="Compare two deals"))
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["readable"])
        self.assertEqual(result[0]["kind"], "reasoning")

    def test_summary_remains_labelled_summary(self):
        result = reasoning_inventory(self.response(reasoning_details=[
            {"type": "reasoning.summary", "summary": "Saved explanation"}]))
        self.assertEqual(result[0]["kind"], "reasoning.summary")
        self.assertTrue(result[0]["readable"])

    def test_encrypted_fields_are_not_readable(self):
        result = reasoning_inventory(self.response(reasoning_details=[
            {"type": "reasoning.encrypted", "data": "opaque", "text": "not plaintext reasoning"}]))
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]["readable"])

    def test_all_choices_and_detail_indices_are_preserved(self):
        result = reasoning_inventory({"choices": [{"message": {}}, {"message": {
            "reasoning_details": [{"type": "reasoning.encrypted", "data": "x"},
                                  {"type": "reasoning.text", "text": "Readable"}]}}]})
        self.assertEqual(len(result), 2)
        self.assertIn("choices[1]", result[1]["location"])
        self.assertIn("[1].text", result[1]["location"])

    def test_empty_and_non_dictionary_responses(self):
        for value in (None, "network failure", {}, {"choices": None}):
            self.assertEqual(reasoning_inventory(value), [])

    def test_note_origin_distinguishes_synthetic_text_and_absence(self):
        self.assertEqual(final_note_origin({"private_thought":"fallback"}, True), "deterministic_fallback")
        self.assertEqual(final_note_origin({"private_thought":"Evaluate rent risk"}, False), "nonfallback_final_action")
        self.assertEqual(final_note_origin({"private_thought":"  "}, False), "no_nonempty_final_note")
        self.assertEqual(final_note_origin({}, True), "no_nonempty_final_note")


if __name__ == "__main__":
    unittest.main()
