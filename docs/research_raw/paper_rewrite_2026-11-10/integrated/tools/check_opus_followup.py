"""Independent checks of Opus's new arithmetic and price tabulations.

Reads saved prompts and ledgers. No engine import, state mutation, action
execution, hypothetical trajectory or model call.
"""

import hashlib
import json
import math
import re
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
    return [json.loads(line) for line in raw.splitlines()] if lines else json.loads(raw)


board = read(REPO / "contracts/data/board.json")
spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s
          for s in board["spaces"] if s["price"] is not None}
assert len(spaces) == 28
assert spaces["B_O_RAILROAD"]["index"] == 25
assert spaces["B_O_RAILROAD"]["price"] == 200
assert spaces["BALTIC_AVENUE"]["price"] == 60
offers = read(BASE / "data/agenda_offers.json")
run_paths = {r["game"]: REPO / r["source_run"] for r in offers}
window_rows = read(BASE / "data/first_management_windows.json")["rows"]
access, cache = [], {}
for window in window_rows:
    if window["cause"] != "never_legal_in_window":
        continue
    game = window["game"]
    if game not in cache:
        cache[game] = read(run_paths[game] / "decisions.jsonl", True)
    did = window["first_mgmt_decision"]
    request = next(r for r in cache[game] if r["phase"] == "decision_started"
                   and r["decision_id"].endswith(did))
    resolved = next(r for r in cache[game] if r["phase"] == "decision_resolved"
                    and r["decision_id"] == request["decision_id"])
    payload = request["prompt_payload"]
    player = payload["game_state"]["you"]
    assert player["player_id"] == window["player"]
    scenario = payload["action_state"]["scenario"]
    opts = scenario["options"]
    owned = {r["space_key"]: r for r in player["holdings"]["owned"]}
    group = window["group"]
    target = {k for k, s in spaces.items() if s["group"] == group}
    assert target <= set(owned)
    assert not (target & set(opts.get("buildable_space_keys", [])))
    assert all(owned[k]["houses"] == 0 and not owned[k]["hotel"] for k in target)
    mortgages = {k: spaces[k]["price"] // 2 for k in opts.get("mortgageable_space_keys", [])
                 if k not in target}
    for key in mortgages:
        assert key in owned and not owned[key]["mortgaged"]
        assert not owned[key]["houses"] and not owned[key]["hotel"]
    mortgaged_target = sorted(k for k in target if owned[k]["mortgaged"])
    redemption = {k: math.ceil((spaces[k]["price"] // 2) * 1.1) for k in mortgaged_target}
    cash = player["cash"]
    house_cost = board["house_cost_by_group"][group]
    needed = sum(redemption.values()) + house_cost
    bank = payload["game_state"]["bank"]
    assert bank["houses_remaining"] > 0
    if cash >= needed:
        assert set(mortgaged_target) <= set(opts.get("unmortgageable_space_keys", []))
    access.append({"game": game, "decision": did, "model": window["model"], "group": group,
                   "source": str((run_paths[game] / "decisions.jsonl").relative_to(REPO)),
                   "cash": cash, "redemption_by_deed": redemption, "one_house_cost": house_cost,
                   "cash_only_surplus": cash - needed, "outside_group_menu_mortgages": mortgages,
                   "mortgage_budget_surplus": cash + sum(mortgages.values()) - needed,
                   "bank_houses": bank["houses_remaining"],
                   "available_actions": payload["action_state"]["available_actions"],
                   "applied_action": resolved["final_action"],
                   "scope": "Static cash budget and current menu; not an executed financing witness or exhaustive liquidation bound."})

legal = [r for r in offers if r["accept_available"]]
cells = defaultdict(Counter)
for r in legal:
    cells[(r["completion_cell"], "Opening" if r["exchange_index"] == 0 else "Later")][r["response"]] += 1
position = [{"cell": cell, "position": stage, "offers": sum(c.values()),
             "accept": c["accept_trade"], "counter": c["counter_trade"], "reject": c["reject_trade"]}
            for (cell, stage), c in sorted(cells.items())]

def price_direction(row):
    offer, request = row["offer"], row["request"]
    if offer["get_out_of_jail_cards"] or request["get_out_of_jail_cards"]:
        return None
    if not offer["properties"] and request["properties"] and request["cash"] == 0 and offer["cash"] > 0:
        return "bid", request["properties"], offer["cash"]
    if offer["properties"] and not request["properties"] and offer["cash"] == 0 and request["cash"] > 0:
        return "ask", offer["properties"], request["cash"]
    return None

prices = []
all_pure = []
for r in legal:
    description = price_direction(r)
    if description:
        kind, deeds, amount = description
        all_pure.append({"cell": r["completion_cell"], "kind": kind, "game": r["game"],
                         "decision": r["decision"], "deeds": deeds,
                         "ratio": amount / sum(spaces[k]["price"] for k in deeds),
                         "mortgaged": r["author_interest_if_accepted"] + r["recipient_interest_if_accepted"] > 0,
                         "opening": r["exchange_index"] == 0})
for kind, cell in (("bid", "author_only"), ("bid", "neither"), ("ask", "recipient_only"), ("ask", "neither")):
    for label in ("all", "unmortgaged", "opening", "later"):
        rows = [r for r in all_pure if r["kind"] == kind and r["cell"] == cell
                and (label != "unmortgaged" or not r["mortgaged"])
                and (label != "opening" or r["opening"])
                and (label != "later" or not r["opening"])]
        prices.append({"kind": kind, "cell": cell, "subset": label, "n": len(rows),
                       "median_cash_to_list": median(r["ratio"] for r in rows) if rows else None})

opus_access = read(BASE / "reviews/opus/checks/never_legal_access.json")
differences = []
for ours in access:
    theirs = next(r for r in opus_access if (r["game"], r["group"]) == (ours["game"], ours["group"]))
    value = sum(ours["outside_group_menu_mortgages"].values())
    if value != theirs["other_clear_mortgage_value"]:
        differences.append({"game": ours["game"], "group": ours["group"],
                            "reviewer_value": theirs["other_clear_mortgage_value"], "current_menu_value": value})
conflicts = read(BASE / "data/resolution_conditions.json")["selected_grok_conflicts"]
name_pairs = Counter((r["content_name"], r["received_tool_name"]) for r in conflicts)
poor_sellers = Counter()
for r in legal:
    if r["response"] != "accept_trade" or not r["net_cash_author_to_recipient"]:
        continue
    seller = "recipient" if r["net_cash_author_to_recipient"] > 0 else "author"
    buyer = "author" if seller == "recipient" else "recipient"
    if r[buyer + "_new_groups"] and r[seller + "_cash_before"] < 100:
        poor_sellers[r[seller + "_model"]] += 1
assert poor_sellers == {"Opus": 13, "Sol": 4, "Grok": 3, "Gemini": 1}
flows = read(BASE / "data/agenda_flows.json")
winners = {r["game"]: r["winner"] for r in read(BASE / "data/t01_cohort.json")}
recipients = defaultdict(set)
for r in flows:
    if r["kind"].startswith("estate_"):
        recipients[(r["game"], r["elimination_index"])].add(r["to_model"])
terminal_winner = sum(recipients[(g, 3)] == {w} for g, w in winners.items())
assert terminal_winner == 19 and recipients[(13, 3)] == {"BANK"}
episodes = read(BASE.parent / "paper_phase1_2026-10-28/sol/group_episodes.jsonl", True)
assert sum(r["route"] == "trade" and r["rent_until_loss_or_end"] > 0 for r in episodes) == 51
report = {"scope": "Independent retained-data and original-prompt arithmetic; no engine executions or new evaluations.",
          "access": access, "cash_only_cases": sum(r["cash_only_surplus"] >= 0 for r in access),
          "menu_mortgage_budget_cases": sum(r["mortgage_budget_surplus"] >= 0 for r in access),
          "reviewer_mortgage_differences": differences, "thread_position": position, "list_price": prices,
          "bid_ask_rows": all_pure,
          "bankruptcy_content_to_finance": sum(name_pairs[("declare_bankruptcy", a)] for a in ("mortgage_property", "sell_houses_or_hotel")),
          "sell_content_to_bankruptcy": name_pairs[("sell_houses_or_hotel", "declare_bankruptcy")],
          "low_cash_completing_sellers": dict(poor_sellers),
          "terminal_winner_estates": terminal_winner, "terminal_bank_estate_game": 13,
          "trade_completion_episodes_with_paid_rent": 51,
          "sources": sources, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE / "qa/opus_followup_checks.json").write_text(json.dumps(report, indent=2) + "\n")
access_lines = [r"\newcommand{\AccessRows}{%"]
for r in access:
    access_lines.append(" & ".join(map(str, [r["game"], int(r["decision"].split("-")[-1]), r["model"],
                                            r["group"].replace("_", " ").title(), r["cash"],
                                            sum(r["redemption_by_deed"].values()), r["one_house_cost"],
                                            sum(r["outside_group_menu_mortgages"].values()),
                                            r["mortgage_budget_surplus"]])) + r"\\")
access_lines.append("}")
(HERE / "sections/access_rows.tex").write_text("\n".join(access_lines) + "\n")
price_lines = [r"\newcommand{\PriceRows}{%"]
for subset in ("all", "unmortgaged", "opening", "later"):
    row = [subset.capitalize()]
    for kind, cell in (("bid", "author_only"), ("bid", "neither"), ("ask", "recipient_only"), ("ask", "neither")):
        p = next(p for p in prices if (p["kind"], p["cell"], p["subset"]) == (kind, cell, subset))
        row.append(f'{p["median_cash_to_list"]:.3f} ({p["n"]})')
    price_lines.append(" & ".join(row) + r"\\")
price_lines.append("}")
(HERE / "sections/price_rows.tex").write_text("\n".join(price_lines) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("access", "sources", "bid_ask_rows")}, indent=2))
