"""Portable consistency checks for the research-agenda extension.

These recalculate aggregates from retained rows. Original-source census and
engine replay are separate, documented checks, not claims made by this script.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    data = root / "data"

    def read(name):
        return json.loads((data / f"agenda_{name}.json").read_text())

    def rows(name):
        return [
            json.loads(line)
            for line in (data / f"agenda_{name}.jsonl").read_text().splitlines()
        ]

    offers, threads, aggregate = read("offers"), read("threads"), read("negotiation")
    assert len(offers) == len({r["decision_id"] for r in offers}) == 920
    assert len(threads) == len({r["thread_id"] for r in threads}) == 526
    assert Counter(r["response"] for r in offers) == {
        "accept_trade": 113,
        "counter_trade": 394,
        "reject_trade": 413,
    }
    cells = defaultdict(Counter)
    for r in offers:
        assert r["author"] != r["recipient"]
        assert r["author_cash_if_accepted"] == (
            r["author_cash_before"]
            - r["offer"]["cash"]
            + r["request"]["cash"]
            - r["author_interest_if_accepted"]
        )
        assert r["recipient_cash_if_accepted"] == (
            r["recipient_cash_before"]
            + r["offer"]["cash"]
            - r["request"]["cash"]
            - r["recipient_interest_if_accepted"]
        )
        assert r["accept_available"] == (
            min(r["author_cash_if_accepted"], r["recipient_cash_if_accepted"]) >= 0
        )
        expected_cell = (
            "both"
            if r["author_new_groups"] and r["recipient_new_groups"]
            else "author_only"
            if r["author_new_groups"]
            else "recipient_only"
            if r["recipient_new_groups"]
            else "neither"
        )
        assert r["completion_cell"] == expected_cell
        if r["accept_available"]:
            cells[expected_cell][r["response"]] += 1
    expected = {
        "neither": (60, 169, 179),
        "author_only": (19, 111, 159),
        "recipient_only": (24, 78, 38),
        "both": (10, 35, 36),
    }
    for cell, counts in expected.items():
        assert (
            tuple(
                cells[cell][a]
                for a in ("accept_trade", "counter_trade", "reject_trade")
            )
            == counts
        )
    for t in threads:
        subset = sorted(
            (r for r in offers if r["thread_id"] == t["thread_id"]),
            key=lambda r: r["response_seq"],
        )
        assert [r["decision_id"] for r in subset] == t["response_ids"]
        assert len(subset) == t["response_count"]
        assert (
            sum(r["response"] == "counter_trade" for r in subset) == t["counter_count"]
        )
        assert t["elapsed_global_turns"] == 0
        assert subset[-1]["response"] in ("accept_trade", "reject_trade")
    assert sum(t["prior_threads_same_pair"] > 0 for t in threads) == 414
    assert not any(r["fallback_used"] for r in offers)
    assert sum(r["retry_used"] for r in offers) == 168
    assert (
        sum(r["accept_available"] for r in offers)
        == aggregate["counts"]["acceptance_available"]
        == 918
    )

    winners = {
        r["game"]: r["winner"]
        for r in json.loads((data / "t01_cohort.json").read_text())
    }
    flows = read("flows")
    for record in aggregate["flow_totals"]:
        selected = [r for r in flows if r["kind"] == record["kind"]]
        assert len(selected) == record["events"]
        assert {r["unit"] for r in selected} == {record["unit"]}
        assert sum(r["amount"] for r in selected) == record["amount"]
        assert (
            sum(r["amount"] for r in selected if r["to_model"] == winners[r["game"]])
            == record["received_by_eventual_winner"]
        )
    for record in aggregate["estate_stage_totals"]:
        selected = [
            r
            for r in flows
            if r["kind"] == record["kind"]
            and r["terminal_estate"] == record["terminal"]
        ]
        assert len(selected) == record["events"]
        assert sum(r["amount"] for r in selected) == record["amount"]
        assert (
            sum(r["amount"] for r in selected if r["to_model"] == winners[r["game"]])
            == record["received_by_eventual_winner"]
        )

    history, recurrence = rows("recurrence_rows"), read("recurrence")
    assert len(history) == len({r["decision_id"] for r in history}) == 6989
    by_actor = defaultdict(list)
    for r in history:
        by_actor[r["game"], r["player_id"]].append(r)
    episodes = {r["decision_id"]: r for r in recurrence["episodes"]}
    for actor_rows in by_actor.values():
        actor_rows.sort(key=lambda r: r["decision_index"])
        first_feedback_seen = False
        for i, row in enumerate(actor_rows):
            if not row["uneven_error"]:
                continue
            e = episodes[row["decision_id"]]
            errors = [a["index"] for a in row["attempts"] if a["uneven"]]
            feedback = any(
                a["feedback_delivered"] and any(j < a["index"] for j in errors)
                for a in row["attempts"]
            )
            assert e["delivered_feedback"] == feedback
            assert e["first_feedback_episode_in_player_game"] == (
                feedback and not first_feedback_seen
            )
            first_feedback_seen |= feedback
            next_row = next(
                (r for r in actor_rows[i + 1 :] if r["construction_submission"]), None
            )
            assert e["next_decision_id"] == (
                next_row["decision_id"] if next_row else None
            )
            if next_row:
                first = next(
                    a
                    for a in next_row["attempts"]
                    if a["name"] == "build_houses_or_hotel"
                )
                assert e["next_first_submission_uneven"] == first["uneven"]
                assert e["next_same_global_turn"] == (
                    next_row["turn_index"] == row["turn_index"]
                )
    selections = {
        "all_uneven": list(episodes.values()),
        "delivered_feedback": [e for e in episodes.values() if e["delivered_feedback"]],
        "first_delivered_per_player_game": [
            e for e in episodes.values() if e["first_feedback_episode_in_player_game"]
        ],
        "feedback_and_applied_build": [
            e
            for e in episodes.values()
            if e["delivered_feedback"] and e["applied_construction_here"]
        ],
        "feedback_without_applied_build": [
            e
            for e in episodes.values()
            if e["delivered_feedback"] and not e["applied_construction_here"]
        ],
    }
    for name, selected in selections.items():
        observed = [e for e in selected if e["next_decision_id"]]
        summary = recurrence["summary"][name]["total"]
        assert (
            len(selected),
            len(observed),
            sum(e["next_first_submission_uneven"] for e in observed),
        ) == (
            summary["episodes"],
            summary["next_submission_observed"],
            summary["next_first_repeats"],
        )

    sample, coded, temporal = (
        read("sample_fields"),
        rows("temporal_rows"),
        read("temporal"),
    )
    assert len(sample) == len(coded) == 240
    assert {r["id"] for r in sample} == {r["id"] for r in coded}
    assert set(Counter(r["model"] for r in sample).values()) == {60}
    tags = Counter(tag for r in coded for tag in r["semantic_tags"])
    assert dict(tags) == temporal["counts"]["codes"]
    assert (tags["P"], tags["O"], tags["R"]) == (59, 36, 25)
    assert sum(not r["fields"]["private_thought"]["present"] for r in sample) == 53
    original = {r["id"]: r for r in sample}
    for r in coded:
        assert r["fields"] == original[r["id"]]["fields"]
        for field in r["fields"].values():
            if field["present"]:
                assert (
                    hashlib.sha256(field["value"].encode()).hexdigest()
                    == field["sha256"]
                )
        assert not r["fallback_used"]
    landings = read("landing_endpoints")
    assert len(landings) == 8
    assert (
        Counter(r["status"] for r in landings)
        == temporal["counts"]["landing_endpoint_counts"]
    )
    for r in landings:
        assert "P" in next(x["semantic_tags"] for x in coded if x["id"] == r["id"])
        if r["status"] == "no_observed_opportunity":
            assert not r["all_matching_opportunities"]
        else:
            opportunity = r["all_matching_opportunities"][0]
            assert "buy_property" in opportunity["menu"]["available_actions"]
            assert (opportunity["action"]["action"] == "buy_property") == (
                r["status"] == "purchase_applied"
            )

    pilot, games, scenarios = read("evaluation"), read("pilot_games"), read("scenarios")
    assert len(games) == 20
    assert Counter(g["status"] for g in games) == {
        "decision_censored": 19,
        "terminated": 1,
    }
    assert (
        sum(g["decisions_applied"] for g in games)
        == pilot["total_applied_primary_decisions"]
        == 19494
    )
    assert sum(g["events"] for g in games) == pilot["total_primary_events"] == 179816
    assert not any(g["provider_calls"] or g["fallbacks"] or g["errors"] for g in games)
    assert sum(g["action_counts"].get("build_houses_or_hotel", 0) for g in games) == 44
    assert sum(g["action_counts"].get("propose_trade", 0) for g in games) == 0
    for g in games:
        if g["status"] == "decision_censored":
            assert g["winner_player_id"] is None and g["decisions_applied"] == 1000
    assert sum(x["invalid"] for x in scenarios["by_policy"].values()) == 75
    assert all(
        x["legal"] + x["invalid"] == 130 for x in scenarios["by_policy"].values()
    )
    assert scenarios["invalid_reference_preferred"] == 11
    assert sum(r["private_keyword_fraction"] > 0 for r in read("scenario_rows")) == 128
    assert read("readiness")["passes_both_limited_checks"] == 68
    return {
        "status": "pass",
        "offer_rows": len(offers),
        "threads": len(threads),
        "typed_flow_rows": len(flows),
        "construction_history_rows": len(history),
        "error_episodes": len(episodes),
        "sampled_fields": len(sample),
        "pilot_games": len(games),
        "limits": "Recalculation and consistency of retained rows; source validity, semantic coding and engine replay are separately reviewed.",
    }


if __name__ == "__main__":
    result = verify()
    (ROOT / "qa/agenda_consistency.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result))
