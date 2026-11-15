"""Source checks for bounded final-review changes; stored records only."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import statistics

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in HERE.parents if (p / "saved_games").is_dir())
read = lambda n: json.loads((HERE / "data" / n).read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
games = read("game_map.json")
totals, readable, detail_types = Counter(), Counter(), Counter()
sources, selected = {}, {}
targets = {2: {115, 118, 119, 120, 122, 124}, 5: {263},
           13: {251, 252}, 15: {76, 158, 162, 165},
           18: {421, 423, 425, 427, 431, 438}, 20: {95, 97, 98, 99, 100}}
offers = read("offers.json")
cash_bids = [r for r in offers if r["accept_available"] and r["exchange_index"] == 0
             and r["completion_cell"] in {"author_only", "neither"}
             and r["request"]["properties"] and not r["offer"]["properties"]
             and r["offer"]["cash"] > 0 and r["request"]["cash"] == 0
             and not r["offer"]["get_out_of_jail_cards"]
             and not r["request"]["get_out_of_jail_cards"]]
opus_keys = {(r["game"], r["offer_decision"]) for r in cash_bids if r["author_model"] == "Opus"}
opus_conditions = Counter()
for game, run in games.items():
    game = int(game)
    p = ROOT / run / "decisions.jsonl"
    blob = p.read_bytes()
    sources[str(p.relative_to(ROOT))] = sha(blob)
    for line_number, line in enumerate(blob.splitlines(), 1):
        rec = json.loads(line)
        if rec["phase"] != "decision_resolved":
            continue
        d = int(rec["decision_id"].rsplit("-", 1)[1])
        model = next(m for m, k in [("Sol", "sol"), ("Gemini", "argon"),
                     ("Opus", "opus"), ("Grok", "grok")] if k in rec["openrouter_model_id"])
        totals[model] += 1
        attempt = rec["attempts"][-1]
        msg = ((attempt.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {})
        if msg.get("reasoning"):
            readable[model] += 1
        types = sorted({x.get("type", "") for x in (msg.get("reasoning_details") or [])})
        detail_types[model + "|" + "+".join(types)] += 1
        if (game, d) in opus_keys:
            opus_conditions[attempt["response_condition"]] += 1
        if d in targets.get(game, set()):
            selected[f"G{game} d{d}"] = dict(
                source=str(p.relative_to(ROOT)), source_sha256=sha(blob),
                jsonl_line_1based=line_number, turn=rec["turn_index"],
                private_note=rec["final_action"].get("private_thought"),
                public_message=rec["final_action"].get("public_message"),
                provider_explanation=msg.get("reasoning"))
assert totals == Counter(Sol=1961, Gemini=1669, Opus=1696, Grok=1663)
assert readable == Counter(Sol=287, Gemini=1316, Opus=1560, Grok=1662)
assert len(cash_bids) == 173 and len(opus_keys) == 110
assert opus_conditions == Counter(standard=5, same_model_without_private_thought=105)
assert "Keep Marvin blocking" in selected["G2 d115"]["private_note"]
assert "blocker, not a set" in selected["G2 d118"]["private_note"]
assert "controls access" in selected["G2 d119"]["public_message"]
assert "Don't sell Ventnor" in selected["G15 d76"]["private_note"]
assert "Never trade Ventnor" in selected["G15 d162"]["private_note"]
assert "Buying Pacific might just prolong" in selected["G18 d431"]["provider_explanation"]
assert "would fund dangerous development" in selected["G20 d95"]["private_note"]
eps = read("liquidation_episodes.json")
bound_sufficient = [e for e in eps if e["upper_bound"] >= e["debt"]]
assert len(bound_sufficient) == 132
assert sum(e["actions"][0] == "declare_bankruptcy" for e in bound_sufficient) == 3
prices = read("single_deed_prices.json")
price_cells = []
for seller in ["Sol", "Gemini", "Opus", "Grok"]:
    for mortgaged in [False, True]:
        groups = [[r for r in prices if r["kind"] == "ask" and r["author"] == seller
                   and r["mortgaged"] == mortgaged and r["completes"] == c]
                  for c in [True, False]]
        if all(groups):
            medians = [statistics.median(r["ratio"] for r in group) for group in groups]
            price_cells.append(dict(seller=seller, mortgaged=mortgaged,
                                    n=[len(g) for g in groups], ratio_medians=medians))
assert len(price_cells) == 7 and all(x["ratio_medians"][0] > x["ratio_medians"][1] for x in price_cells)
certificate_path = ROOT / "docs/research_raw/paper_agenda_revision_2026-10-29/baseline/data/certificate_results.json"
certificates = json.loads(certificate_path.read_text())
witnesses = []
for r in certificates["results"]:
    if r.get("certificate") == "legal_payment_witness":
        w = r["witness"]
        witnesses.append(dict(case=r["case_id"], paid=w["paid"],
                              steps=[dict(action=s["action"], args=s["args"]) for s in w["steps"]],
                              final={k:v for k,v in w.items() if k != "steps"}))
assert len(witnesses) == 3
result = dict(source_hashes=sources, response_totals=dict(totals),
              readable_reasoning=dict(readable), reasoning_detail_types=dict(detail_types),
              opus_cash_bid_conditions=dict(opus_conditions), selected_fields=selected,
              price_cells=price_cells, bound_sufficient=132,
              certificate_report=str(certificate_path.relative_to(ROOT)),
              certificate_report_sha256=sha(certificate_path.read_bytes()),
              stored_witnesses=witnesses)
(HERE / "data/final_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(records=sum(totals.values()), selected_fields=len(selected),
                      cash_bids=len(cash_bids), price_cells=len(price_cells), witnesses=len(witnesses))))
