"""Mutation tests for retained-data checks; no game or provider execution."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from pathlib import Path

from verify_agenda import ROOT, verify


def main():
    checks = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        shutil.copytree(ROOT / "data", root / "data")
        verify(root)
        mutations = [
            (
                "offer cash",
                "agenda_offers.json",
                lambda d: d[0].__setitem__(
                    "author_cash_if_accepted", d[0]["author_cash_if_accepted"] + 1
                ),
            ),
            (
                "offer author",
                "agenda_offers.json",
                lambda d: d[0].__setitem__("author", d[0]["recipient"]),
            ),
            (
                "thread endpoint",
                "agenda_threads.json",
                lambda d: d[0]["response_ids"].pop(),
            ),
            (
                "flow amount",
                "agenda_flows.json",
                lambda d: d[0].__setitem__("amount", d[0]["amount"] + 1),
            ),
            (
                "feedback exposure",
                "agenda_recurrence.json",
                lambda d: d["episodes"][0].__setitem__(
                    "delivered_feedback", not d["episodes"][0]["delivered_feedback"]
                ),
            ),
            (
                "next submission",
                "agenda_recurrence.json",
                lambda d: d["episodes"][0].__setitem__("next_decision_id", None),
            ),
            (
                "source field",
                "agenda_sample_fields.json",
                lambda d: d[0]["fields"]["public_message"].__setitem__(
                    "value", "corrupted"
                ),
            ),
            (
                "censored winner",
                "agenda_pilot_games.json",
                lambda d: d[0].__setitem__("winner_player_id", "p1"),
            ),
            (
                "reference failures",
                "agenda_scenarios.json",
                lambda d: d.__setitem__("invalid_reference_preferred", 10),
            ),
        ]
        for label, filename, mutate in mutations:
            path = root / "data" / filename
            original = path.read_text()
            changed = copy.deepcopy(json.loads(original))
            mutate(changed)
            path.write_text(json.dumps(changed))
            detected = False
            try:
                verify(root)
            except (AssertionError, KeyError, StopIteration):
                detected = True
            finally:
                path.write_text(original)
            assert detected, label
            checks.append({"mutation": label, "detected": detected})
        verify(root)
    result = {"status": "pass", "mutations": checks, "count": len(checks)}
    (ROOT / "qa/agenda_verifier_regression.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
