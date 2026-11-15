"""Peer-informed independent re-tabulations and original quote/delivery checks.

No engine execution, hypothetical trajectory, or model call. The population
checks use retained ledgers; quote checks read canonical decisions directly.
"""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[2]
sources = {}


def read(path):
    sources[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())


offers = read(BASE / "data/agenda_offers.json")
legal = [r for r in offers if r["accept_available"]]
threads = read(BASE / "data/agenda_threads.json")
conflicts = read(BASE / "data/resolution_conditions.json")["selected_grok_conflicts"]
flows = read(BASE / "data/agenda_flows.json")
cohort = read(BASE / "data/t01_cohort.json")
winners = {r["game"]: r["winner"] for r in cohort}
assert len({r["decision_id"] for r in conflicts}) == 139
conflict_keys = {(r["game"], int(r["decision_id"].split("-dec-")[1])) for r in conflicts}
opened = [r for r in threads if r["initiator_model"] == "Grok"]
conflict_opened = [r for r in opened if (r["game"], r["start_decision"]) in conflict_keys]
conflict_responses = [r for r in offers if (r["game"], r["decision"]) in conflict_keys]
assert len(opened) == 136 and len(conflict_opened) == 64
assert sum(r["terminal"] == "TRADE_ACCEPTED" for r in conflict_opened) == 17
assert len(conflict_responses) == 11
assert Counter(r["response"] for r in conflict_responses) == {
    "accept_trade": 7, "counter_trade": 1, "reject_trade": 3,
}
accepted_conflicts = [r for r in conflict_responses if r["response"] == "accept_trade"]
opus_completions = [r for r in accepted_conflicts if r["author_model"] == "Opus" and r["author_new_groups"]]
assert len(opus_completions) == 3

one_sided = [r for r in legal if r["completion_cell"] in ("author_only", "recipient_only")]
completer_pays = [r for r in one_sided if
                 (r["completion_cell"] == "author_only" and r["net_cash_author_to_recipient"] > 0)
                 or (r["completion_cell"] == "recipient_only" and r["net_cash_author_to_recipient"] < 0)]
assert (len(one_sided), len(completer_pays)) == (429, 373)
sales = []
for r in legal:
    if r["response"] != "accept_trade" or r["net_cash_author_to_recipient"] == 0:
        continue
    seller_role = "recipient" if r["net_cash_author_to_recipient"] > 0 else "author"
    buyer_role = "author" if seller_role == "recipient" else "recipient"
    sales.append({"game": r["game"], "decision": r["decision"],
                  "seller_cash": r[f"{seller_role}_cash_before"],
                  "seller": r[f"{seller_role}_model"],
                  "buyer_completes": bool(r[f"{buyer_role}_new_groups"]),
                  "any_completion": bool(r["author_new_groups"] or r["recipient_new_groups"])})
completing = [r for r in sales if r["buyer_completes"]]
noncompleting = [r for r in sales if not r["any_completion"]]
assert len(sales) == 107 and len(completing) == 48 and len(noncompleting) == 57
assert median(r["seller_cash"] for r in completing) == 194
assert median(r["seller_cash"] for r in noncompleting) == 571
sensitivity = {}
for threshold in [50, 100, 150, 200]:
    poor = [r for r in sales if r["seller_cash"] < threshold]
    sensitivity[threshold] = {"cash_receiving_sales": len(poor),
                              "payer_completes": sum(r["buyer_completes"] for r in poor)}
assert sensitivity == {50: {"cash_receiving_sales": 20, "payer_completes": 14},
                       100: {"cash_receiving_sales": 30, "payer_completes": 21},
                       150: {"cash_receiving_sales": 36, "payer_completes": 22},
                       200: {"cash_receiving_sales": 40, "payer_completes": 24}}
assert sum(r["seller_cash"] < 100 for r in completing) == 21
assert sum(r["seller_cash"] < 100 for r in noncompleting) == 9

ep_path = BASE.parent / "paper_phase1_2026-10-28/sol/group_episodes.jsonl"
sources[str(ep_path.relative_to(REPO))] = hashlib.sha256(ep_path.read_bytes()).hexdigest()
episodes = [json.loads(line) for line in ep_path.read_text().splitlines()]
assert len(episodes) == 209
assert Counter(r["route"] for r in episodes) == {"trade": 63, "creditor_inheritance": 121, "direct_purchase": 16, "auction": 9}
estates = [r for r in episodes if r["route"] == "creditor_inheritance"]
assert Counter(r["access_status"] for r in estates) == {"observed": 52, "no_access_before_game_end": 69}
assert sum(r["model"] == winners[r["game"]] for r in estates if r["access_status"] == "observed") == 45
rent_by_owner = defaultdict(int)
for r in episodes:
    if r["route"] == "trade":
        rent_by_owner[r["model"]] += r["rent_until_loss_or_end"]
assert dict(rent_by_owner) == {"Sol": 20818, "Gemini": 26070, "Opus": 5930, "Grok": 4560}
estate_recipient = defaultdict(set)
for r in flows:
    if r["kind"].startswith("estate_"):
        estate_recipient[(r["game"], r["elimination_index"])].add(r["to_model"])
assert sum(estate_recipient[(g, 1)] == {winners[g]} for g in winners) == 18
assert sum(all(estate_recipient[(g, i)] == {winners[g]} for i in [1, 2, 3]) for g in winners) == 16

manifest = read(BASE / "full_drafts/fable_5_2/data/transcript_manifest_supplement.json")
cache = {}
quote_checks = []


def strings(value, path=""):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from strings(v, f"{path}/{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from strings(v, f"{path}/{i}")
    elif isinstance(value, str):
        yield path, value


for q in manifest["quotes"]:
    p = REPO / q["source"]
    if p not in cache:
        sources[q["source"]] = hashlib.sha256(p.read_bytes()).hexdigest()
        cache[p] = [json.loads(line) for line in p.read_text().splitlines()]
    assert sources[q["source"]] == q["source_sha256"]
    row = cache[p][q["jsonl_line_1based"] - 1]
    assert row["decision_id"] == q["decision_id"]
    field = row
    for key in q["json_pointer"].strip("/").split("/"):
        field = field[key]
    assert field == q["field_text"]
    assert hashlib.sha256(field.encode()).hexdigest() == q["field_sha256"]
    for span in q["excerpts"]:
        a, b = span["span"]
        assert field[a:b] == span["text"]
    checked = {"id": q["id"], "exact_field_and_spans": True}
    if q["game"] in (11, 15) and q["json_pointer"].endswith("public_message"):
        action = row["final_action"]
        if action["action"] == "propose_trade":
            recipient = action["args"]["to_player_id"]
        else:
            old_offer = next(r for r in offers if r["decision_id"] == q["decision_id"])
            recipient = old_offer["author"]
        request = next(r for r in cache[p][q["jsonl_line_1based"]:] if
                       r["phase"] == "decision_started" and r["player_id"] == recipient)
        paths = [path for path, text in strings(request["prompt_payload"]) if field in text]
        assert paths, q["id"]
        checked.update({"recipient": recipient, "next_request": request["decision_id"],
                        "full_message_delivered": True, "paths": paths})
    quote_checks.append(checked)

assert len(quote_checks) == 14
assert sum("next_request" in r for r in quote_checks) == 8
report = {
    "scope": "Peer-informed independent retained-ledger checks and original-field checks; not fresh engine validation, causal analysis or a new evaluation.",
    "sources": sources, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "conflicts": {"grok_openings": 136, "conflicting_openings": 64, "settled_conflicting_openings": 17,
                  "conflicting_trade_responses": 11, "conflicting_acceptances": 7, "opus_completing_acceptances": 3},
    "cash": {"completer_pays": 373, "one_sided_offers": 429, "payer_completing_sales": 48,
             "seller_under_100_in_payer_completing_sales": 21, "median_seller_cash_completing": 194,
             "median_seller_cash_no_completion": 571, "sensitivity": sensitivity},
    "economy": {"completion_routes": dict(Counter(r["route"] for r in episodes)),
                "nonterminal_estate_completions": 52, "nonterminal_estate_completions_by_winner": 45,
                "trade_completion_rent_by_owner": dict(rent_by_owner), "winner_first_estate_games": 18,
                "same_winner_all_three_estates_games": 16},
    "quote_checks": quote_checks,
    "wording_limits": ["21/48 is not a majority. 21/30 uses a different conditioning set.",
                       "A cash receipt in a bundled trade does not prove a causal price premium for completion.",
                       "64 conflicting received proposals remain actual proposals; origin and intended action remain unresolved.",
                       "Eight prompt-delivery checks establish exposure only, not belief or influence."],
}
(HERE / "fable_addition_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("sources", "quote_checks")}, indent=2))
