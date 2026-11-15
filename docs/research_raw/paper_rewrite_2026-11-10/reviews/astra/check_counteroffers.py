"""Peer-informed re-tabulation of existing offers; no engine or model execution.

Checks the new Opus result using exact group identities and unchanged noncash
bundles, as well as sign reversal and mandatory-interest-adjusted cash.
"""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
SOURCE = BASE / "data/agenda_offers.json"
rows = json.loads(SOURCE.read_text())
threads = defaultdict(list)
for row in rows:
    threads[(row["game"], row["thread_id"])].append(row)

joined = []
for key, chain in sorted(threads.items()):
    chain.sort(key=lambda row: row["exchange_index"])
    assert [r["exchange_index"] for r in chain] == list(range(len(chain)))
    for index, old in enumerate(chain):
        if old["response"] != "counter_trade":
            assert index == len(chain) - 1
            continue
        new = chain[index + 1]
        assert old["recipient"] == new["author"]
        assert old["author"] == new["recipient"]
        assert old["turn"] == new["turn"]
        assert old["recipient_cash_before"] == new["author_cash_before"]
        same_bundle = all(
            sorted(old[a]["properties"]) == sorted(new[b]["properties"])
            and old[a]["get_out_of_jail_cards"] == new[b]["get_out_of_jail_cards"]
            for a, b in [("offer", "request"), ("request", "offer")]
        )
        delta = (
            new["request"]["cash"] - new["offer"]["cash"]
            - old["offer"]["cash"] + old["request"]["cash"]
        )
        assert delta == -new["net_cash_author_to_recipient"] - old["net_cash_author_to_recipient"]
        joined.append({
            "game": key[0], "thread": key[1], "decision": old["decision"],
            "counter_decision": new["decision"],
            "responder": old["recipient_model"],
            "original_cell": old["completion_cell"],
            "original_author_groups": old["author_new_groups"],
            "new_original_author_groups": new["recipient_new_groups"],
            "same_author_completion": bool(old["author_new_groups"])
            and set(old["author_new_groups"]) == set(new["recipient_new_groups"]),
            "counterer_completes": bool(new["author_new_groups"]),
            "same_noncash_bundle": same_bundle,
            "cash_delta": delta,
            "cash_delta_after_interest": new["author_cash_if_accepted"] - old["recipient_cash_if_accepted"],
        })

assert len(joined) == 394
author = [r for r in joined if r["original_cell"] == "author_only"]
kept = [r for r in author if r["same_author_completion"]]
kept_only = [r for r in kept if not r["counterer_completes"]]
cash_only = [r for r in kept_only if r["same_noncash_bundle"]]
assert (len(author), len(kept), len(kept_only), len(cash_only)) == (111, 92, 88, 79)
assert sum(r["cash_delta"] > 0 for r in kept_only) == 85
assert all(r["cash_delta"] > 0 for r in cash_only)
assert all(r["cash_delta"] == r["cash_delta_after_interest"] for r in kept_only)
assert median(r["cash_delta"] for r in kept_only) == 125

legal = [r for r in rows if r["accept_available"]]
styles = {}
for model in ["Sol", "Gemini", "Opus", "Grok"]:
    styles[model] = {}
    for cell in ["author_only", "recipient_only"]:
        selected = [r for r in legal if r["recipient_model"] == model and r["completion_cell"] == cell]
        styles[model][cell] = {"n": len(selected), **Counter(r["response"] for r in selected)}
assert styles["Opus"]["author_only"]["accept_trade"] == 7
assert styles["Opus"]["author_only"]["n"] == 52
assert styles["Opus"]["recipient_only"]["accept_trade"] == 5
assert styles["Opus"]["recipient_only"]["n"] == 42

report = {
    "scope": "Peer-informed independent retained-ledger re-tabulation, not raw-game reconstruction or a new evaluation.",
    "source": str(SOURCE.relative_to(BASE)),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "all_counters": len(joined),
    "author_only_counters": len(author),
    "keep_exact_original_author_groups": len(kept),
    "keep_only_original_author_completion": len(kept_only),
    "increase_cash_within_that_subset": 85,
    "median_cash_increase_all_88": median(r["cash_delta"] for r in kept_only),
    "unchanged_noncash_bundle_subset": len(cash_only),
    "cash_increases_in_unchanged_bundle_subset": len(cash_only),
    "median_increase_unchanged_bundle_subset": median(r["cash_delta"] for r in cash_only),
    "response_styles": styles,
    "rows": joined,
}
(HERE / "counteroffer_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
