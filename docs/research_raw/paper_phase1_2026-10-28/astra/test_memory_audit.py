import unittest

from memory_audit import NoteHistory, attempt_memory


def note(seq, player="p1", text="plan"):
    return {"event_id": f"evt-{seq}", "turn_index": seq,
            "payload": {"decision_id": f"dec-{seq}", "player_id": player, "thought": text}}


class MemoryTests(unittest.TestCase):
    def test_literal_fallback_is_not_provenance(self):
        history = NoteHistory()
        history.append(note(1, text="fallback"), False)
        history.append(note(2, text="fallback"), True)
        self.assertEqual(history.origins("p1"), {"model_response": 1, "deterministic_fallback": 1})

    def test_memory_window_expires_old_notes(self):
        history = NoteHistory(limit=2)
        for i in range(3):
            history.append(note(i), i > 0)
        self.assertEqual(history.origins("p1"), {"deterministic_fallback": 2})
        self.assertTrue(history.compare("p1", [{"turn_index": i, "thought": "plan"} for i in [1, 2]]))

    def test_other_player_notes_are_not_exposed(self):
        history = NoteHistory()
        history.append(note(1, player="p2"), False)
        self.assertTrue(history.compare("p1", []))
        self.assertFalse(history.compare("p2", []))

    def test_missing_memory_is_unknown_not_empty(self):
        self.assertFalse(NoteHistory().compare("p1", None))

    def test_only_first_attempt_can_reference_initial_prompt(self):
        initial = {"your_private_thoughts_last_10": [{"thought": "plan"}]}
        self.assertEqual(attempt_memory({"prompt_payload": None}, 0, initial),
                         (initial, "initial_decision_record"))
        self.assertEqual(attempt_memory({"prompt_payload": None}, 1, initial),
                         ({}, "attempt_record"))


if __name__ == "__main__":
    unittest.main()
