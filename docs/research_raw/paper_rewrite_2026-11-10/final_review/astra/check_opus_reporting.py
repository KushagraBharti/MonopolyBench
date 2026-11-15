"""Read saved records for Opus's final findings. Never import or execute the engine."""

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
ROOT = BASE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def keys(value):
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(key)
            found.update(keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(keys(child))
    return found


paths = sorted((ROOT / "saved_games").glob("railway-research-*/game-??-*"))
assert len(paths) == 20
economic_fields = {"price", "rent", "house_cost", "group", "group_progress", "mortgage_value", "unmortgage_cost", "redemption", "cost"}
census = defaultdict(Counter)
all_keys = defaultdict(set)
memory = Counter()
initials = {}
focal = {}
sources = {}
system_texts = {}
targets = {
    1: {298, 314}, 3: {176}, 7: {339}, 12: {249},
    13: {250, 252}, 16: {234}, 20: {95, 129, 130, 156, 157, 158, 159, 160},
}
for game_dir in paths:
    game = int(game_dir.name.split("-")[1])
    source = game_dir / "run/decisions.jsonl"
    sources[str(source.relative_to(ROOT))] = sha(source)
    for row in rows(source):
        index = int(row["decision_id"].rsplit("-", 1)[-1])
        if row["phase"] == "decision_started":
            initials[(game, index)] = row["prompt_payload"]
            payload = row["prompt_payload"]
            state = dict(payload["game_state"])
            mem = state.pop("memory", {})
            dtype = payload["action_state"]["decision_type"]
            names = keys(state) | keys(payload["action_state"])
            all_keys[dtype].update(names)
            census[dtype]["n"] += 1
            for field in sorted(economic_fields):
                census[dtype][field] += field in names
            if "opus" in row["player_name"]:
                notes = mem.get("your_private_thoughts_last_10", [])
                text = [(note.get("thought") or "").strip() for note in notes]
                if not notes:
                    memory["empty"] += 1
                elif all(not note or note.lower() == "fallback" for note in text):
                    memory["only_fallback"] += 1
                else:
                    memory["has_authored_note"] += 1
            for message in row.get("prompt_messages", []):
                if message["role"] == "system":
                    text = message["content"]
                    digest = hashlib.sha256(text.encode()).hexdigest()
                    system_texts[digest] = text
        elif row["phase"] == "decision_resolved" and index in targets.get(game, set()):
            focal[f"G{game}d{index}"] = {
                "action": row["final_action"],
                "attempts": [
                    {
                        "attempt_index": attempt_index,
                        "outcome": attempt.get("outcome"),
                        "assistant_content": attempt.get("assistant_content"),
                        "provider_reasoning": (attempt.get("raw_response") or {}).get("choices", [{}])[0].get("message", {}).get("reasoning"),
                    }
                    for attempt_index, attempt in enumerate(row.get("attempts", []))
                ],
            }

assert sum(row["n"] for row in census.values()) == 6989
assert census["POST_TURN_ACTION_DECISION"]["n"] == 4081
for dtype in ["POST_TURN_ACTION_DECISION", "TRADE_RESPONSE_DECISION", "LIQUIDATION_DECISION", "JAIL_DECISION"]:
    assert all(census[dtype][key] == 0 for key in economic_fields)
assert dict(memory) == {"empty": 1108, "only_fallback": 286, "has_authored_note": 302}
g7 = initials[(7, 339)]
assert g7["action_state"]["available_actions"] == ["mortgage_property", "declare_bankruptcy"]
assert g7["action_state"]["scenario"]["options"]["sellable_building_space_keys"] == []

eliminations = json.loads((BASE / "data/t06_eliminations.json").read_text())
debt_rows = []
for row in eliminations:
    prompt = initials[(row["game"], int(row["decision"].split("-")[-1]))]
    state = prompt["game_state"]
    action = prompt["action_state"]
    debtor = state["you"]
    position = debtor["position"]
    # This state is delivered before the retained elimination-triggering action.
    # Directly match the creditor's holding to the debtor's board position.
    creditor = action["scenario"].get("owed_to_player_id")
    holding = None
    for other in state["others"]:
        if other["player_id"] == creditor:
            holding = next((h for h in other["holdings"]["owned"] if h["space_key"] == position), None)
    developed = bool(holding and (holding["houses"] or holding["hotel"]))
    debt_rows.append({
        "game": row["game"], "decision": row["decision"], "debtor": row["model"],
        "type": action["decision_type"], "reason": action["scenario"].get("reason"),
        "creditor": creditor, "position": position, "creditor_holding": holding,
        "developed_rent": developed and action["scenario"].get("reason") == "RENT",
    })

last = {game: max(int(row["decision"].split("-")[-1]) for row in debt_rows if row["game"] == game) for game in range(1, 21)}
for row in debt_rows:
    row["terminal"] = int(row["decision"].split("-")[-1]) == last[row["game"]]
debt_totals = {
    "all": sum(row["developed_rent"] for row in debt_rows),
    "nonterminal": sum(row["developed_rent"] and not row["terminal"] for row in debt_rows),
}
assert debt_totals == {"all": 57, "nonterminal": 38}, debt_totals

offers = json.loads((BASE / "data/agenda_offers.json").read_text())
threads = defaultdict(list)
for row in offers:
    threads[row["thread_id"]].append(row)
requested_retained, completion_retained = set(), set()
for thread in threads.values():
    thread.sort(key=lambda row: row["offer_seq"])
    for current, following in zip(thread, thread[1:]):
        if current["response"] != "counter_trade" or current["completion_cell"] != "author_only":
            continue
        assert current["recipient"] == following["author"]
        if set(current["request"]["properties"]) <= set(following["offer"]["properties"]):
            requested_retained.add(current["decision_id"])
        if set(current["author_new_groups"]) <= set(following["recipient_new_groups"]):
            completion_retained.add(current["decision_id"])
assert requested_retained == completion_retained and len(requested_retained) == 92

principals = [30, 50, 60, 70, 75, 80, 90, 100, 110, 120, 130, 140, 150, 160, 175, 200]
rounding = [{"principal": value, "exact_charge": (value * 11 + 9) // 10, "float_charge": math.ceil(value * 1.1)} for value in principals]
assert [row["principal"] for row in rounding if row["exact_charge"] != row["float_charge"]] == [50, 90, 100, 110, 200]
engine_path = ROOT / "python/packages/engine/src/monopoly_engine/engine.py"
sources[str(engine_path.relative_to(ROOT))] = sha(engine_path)
result = {
    "scope": "Original initial-prompt census, recorded debt-state matches, exact arithmetic and source reading. No engine calls or new semantic coding.",
    "census": dict(census), "structured_key_union": {key: sorted(value) for key, value in all_keys.items()},
    "memory": dict(memory), "redemption_arithmetic": rounding,
    "g7_d339": {"action_state": g7["action_state"], "you": g7["game_state"]["you"], "bank": g7["game_state"]["bank"]},
    "developed_rent_debts": debt_totals, "debt_rows": debt_rows,
    "author_only_counter_predicates": {"requested_deed_retention": 92, "completion_retention": 92, "symmetric_difference": 0},
    "focal": focal, "initial_system_prompts": system_texts, "source_sha256": sources,
    "script_sha256": sha(Path(__file__)),
}
(HERE / "opus_reporting_checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"census": dict(census), "memory": dict(memory), "developed_rent_debts": debt_totals, "initial_system_prompt_variants": len(system_texts)}, indent=2))
