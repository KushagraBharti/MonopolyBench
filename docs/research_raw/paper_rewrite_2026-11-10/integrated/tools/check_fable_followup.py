"""Check cross-review additions using retained records, without engine execution."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
REPO = BASE.parents[2]
sources = {}


def read(path, lines=False):
    raw = path.read_bytes()
    sources[str(path.relative_to(REPO))] = hashlib.sha256(raw).hexdigest()
    return [json.loads(s) for s in raw.splitlines()] if lines else json.loads(raw)


offers = read(BASE / "data/agenda_offers.json")
threads = defaultdict(list)
for row in offers:
    threads[row["thread_id"]].append(row)
pairs = []
for rows in threads.values():
    rows.sort(key=lambda r: r["exchange_index"])
    for offer, counter in zip(rows, rows[1:]):
        assert offer["response"] == "counter_trade"
        assert offer["recipient"] == counter["author"]
        pairs.append((offer, counter))
assert len(pairs) == 394
counter_rows, markup = [], {}
for cell in ("author_only", "neither"):
    rows = [(a, b) for a, b in pairs if a["completion_cell"] == cell and a["request"]["properties"]]
    retained, pure, ratios = 0, 0, []
    for a, b in rows:
        retained += set(a["request"]["properties"]) <= set(b["offer"]["properties"])
        same = all(sorted(a[x]["properties"]) == sorted(b[y]["properties"])
                   and a[x]["get_out_of_jail_cards"] == b[y]["get_out_of_jail_cards"]
                   for x, y in (("offer", "request"), ("request", "offer")))
        before, after = a["net_cash_author_to_recipient"], -b["net_cash_author_to_recipient"]
        pure += same and after > before
        if same and not a["offer"]["properties"] and before > 0:
            ratios.append({"game": a["game"], "decision": a["decision"], "ratio": after / before,
                           "includes_jail_card": bool(a["offer"]["get_out_of_jail_cards"]
                                                      or a["request"]["get_out_of_jail_cards"])})
    counter_rows.append({"cell": cell, "n": len(rows), "all_requested_deeds_retained": retained,
                         "identical_noncash_bundle_cash_increased": pure})
    markup[cell] = {"n": len(ratios), "median": median(r["ratio"] for r in ratios), "rows": ratios}
assert [(r["n"], r["all_requested_deeds_retained"], r["identical_noncash_bundle_cash_increased"])
        for r in counter_rows] == [(111, 92, 79), (110, 87, 81)]
neither = [r for r in offers if r["accept_available"] and r["completion_cell"] == "neither"
           and len(r["request"]["properties"]) != len(r["offer"]["properties"])]
buyer_pays = sum((len(r["request"]["properties"]) > len(r["offer"]["properties"]))
                 == (r["net_cash_author_to_recipient"] > 0)
                 and r["net_cash_author_to_recipient"] != 0 for r in neither)
assert (len(neither), buyer_pays) == (313, 309)
rejections = [r for r in offers if r["accept_available"] and r["response"] == "reject_trade"
              and r["completion_cell"] in {"recipient_only", "both"}]
reason_population = dict(Counter(r["recipient_model"] for r in rejections))
assert reason_population == {"Sol": 4, "Gemini": 31, "Grok": 31, "Opus": 8}

conflicts = read(BASE / "data/resolution_conditions.json")["selected_grok_conflicts"]
conflict_ids = {(r["game"], int(r["decision_id"].rsplit("-", 1)[1])) for r in conflicts}
accepts = [r for r in offers if r["completion_cell"] == "author_only" and r["response"] == "accept_trade"]
assert len(accepts) == 19
accepted_summary = {"n": len(accepts), "later": sum(r["exchange_index"] > 0 for r in accepts),
                    "recipient_below_100": sum(r["recipient_cash_before"] < 100 for r in accepts),
                    "opus": sum(r["recipient_model"] == "Opus" for r in accepts),
                    "conflicts": sum((r["game"], r["decision"]) in conflict_ids for r in accepts)}
assert accepted_summary == {"n": 19, "later": 16, "recipient_below_100": 8, "opus": 7, "conflicts": 3}
assert all(r["response_condition"] == "same_model_without_private_thought"
           for r in accepts if r["recipient_model"] == "Opus")
runs = {r["game"]: REPO / r["source_run"] for r in offers}
cache = {}


def records(game):
    if game not in cache:
        cache[game] = read(runs[game] / "decisions.jsonl", True)
    return cache[game]


def decision(game, index, phase):
    return next(r for r in records(game) if r["phase"] == phase
                and int(r["decision_id"].rsplit("-", 1)[1]) == index)


opening_accepts = []
for r in accepts:
    if r["exchange_index"]:
        continue
    resolved = decision(r["game"], r["decision"], "decision_resolved")
    opening_accepts.append({"game": r["game"], "decision": r["decision"],
                           "recipient": r["recipient_model"], "response_condition": r["response_condition"],
                           "named_conflict": (r["game"], r["decision"]) in conflict_ids,
                           "attempts": resolved["attempts"]})
assert len(opening_accepts) == 3 and sum(r["named_conflict"] for r in opening_accepts) == 2
unconflicted = next(r for r in opening_accepts if not r["named_conflict"])
assert (unconflicted["game"], unconflicted["decision"]) == (3, 194)
attempt = unconflicted["attempts"][0]
assert json.loads(attempt["assistant_content"])["name"] == attempt["parsed_tool_call"]["name"] == "accept_trade"
g2 = decision(2, 197, "decision_started")
assert g2["prompt_payload"]["game_state"]["you"]["cash"] == 17
eps = read(REPO / "docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl", True)
g13_green = [e for e in eps if e["game"] == 13 and e["model"] == "Opus" and e["group"] == "GREEN"]
assert len(g13_green) == 1 and g13_green[0]["acquisition_turn"] == 114 and g13_green[0]["route"] == "auction"
orange = [e for e in eps if 13 <= e["game"] <= 16 and e["player_id"] == "p1" and e["group"] == "ORANGE"]
assert [(e["game"], e["acquisition_turn"], e["route"]) for e in orange] == [
    (13, 47, "direct_purchase"), (14, 47, "direct_purchase"), (15, 47, "direct_purchase"), (16, 116, "trade")]
g2_events = read(runs[2] / "events.jsonl", True)
g13_events = read(runs[13] / "events.jsonl", True)
selected_events = {"G2_t72": [e for e in g2_events if e["turn_index"] == 72 and
                                ("BANKRUPTCY" in e["payload"].get("reason", "")
                                 or e["type"] == "PROPERTY_PURCHASED")],
                   "G13_t114": [e for e in g13_events if e["turn_index"] == 114 and
                                  any(s in e["type"] for s in ("AUCTION", "PURCHASE", "TRANSFER"))]}
assert {25, 35} <= {e["payload"]["space_index"] for e in selected_events["G2_t72"]
                   if e["type"] == "PROPERTY_PURCHASED" and e["payload"]["player_id"] == "p2"}
g2_debt = decision(2, 215, "decision_started")["prompt_payload"]["action_state"]["scenario"]
assert g2_debt["owed_amount"] == 1300
next_move = next(e for e in g13_events if e["turn_index"] > 107 and e["type"] == "PLAYER_MOVED"
                 and e["actor"]["player_id"] == "p4")
assert next_move["turn_index"] == 111 and next_move["payload"]["to"] == 29
selected_events["G13_next_Grok_move"] = next_move
out = {"scope": "Retained-ledger re-tabulation and original record inspection; no engine or model execution.",
       "counters": counter_rows, "markup": markup, "buyer_pays_neither": [buyer_pays, len(neither)],
       "reason_population": reason_population, "author_only_acceptances": accepted_summary,
       "opening_author_only_acceptances": opening_accepts, "G2_d197_cash": 17,
       "G13_green": g13_green, "block4_oranges": orange, "events": selected_events, "source_sha256": sources}
(HERE / "qa/fable_followup_checks.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: out[k] for k in ("counters", "reason_population", "author_only_acceptances")}, indent=2))
print("Opening acceptances:", [(r["game"], r["decision"], r["recipient"], r["named_conflict"]) for r in opening_accepts])
print("Markup:", {k: (v["n"], v["median"], sum(r["includes_jail_card"] for r in v["rows"])) for k, v in markup.items()})
