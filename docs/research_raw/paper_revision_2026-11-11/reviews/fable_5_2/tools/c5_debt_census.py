"""Check 5. The liquidation census, closed on original events, and reconciled
across the four frozen drafts.

Read-only event reduction over the twenty saved games. No engine import, no
replay, no model call. For every LIQUIDATION_DECISION in decisions.jsonl:
  * group consecutive decisions for one player, turn, owed amount, reason and
    creditor into an episode;
  * close the episode on the events its last decision emitted: a bankruptcy
    cash event for the debtor, or a payment of the owed amount by the debtor;
  * record action names, engine defaults (fallback_used) and, for Grok, whether
    the assistant text of the selected attempt names a different action from
    the applied call.
Then compare game, player, first decision, debt and outcome with the episode
files in full_drafts/{astra,sol,opus,fable_5_2}.
"""
import ast
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPO = ROOT.parents[2]
OUT = HERE.parent / "data/c5_debt_census.json"
COLL = [REPO / "saved_games/railway-research-12-games-2026-10-25",
        REPO / "saved_games/railway-research-8-games-2026-10-26"]
LABEL = {"gpt-6.1-sol": "Sol", "gemini-4-argon": "Gemini", "claude-opus-5.5": "Opus", "grok-4.7": "Grok"}
NAME_RE = re.compile(r'"name"\s*:\s*"([a-z_]+)"')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lit(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            try:
                return ast.literal_eval(x)
            except Exception:
                return x
    return x


games = {}
for c in COLL:
    for g in sorted(c.glob("game-[0-9][0-9]-*")):
        if g.is_dir():
            games[int(g.name.split("-")[1])] = g / "run"
assert sorted(games) == list(range(1, 21))

episodes = []
src = {}
totals = Counter()
for gno in range(1, 21):
    run = games[gno]
    src[f"G{gno}/decisions.jsonl"] = sha(run / "decisions.jsonl")
    src[f"G{gno}/events.jsonl"] = sha(run / "events.jsonl")
    events = {}
    for line in open(run / "events.jsonl"):
        e = json.loads(line)
        events[e["seq"]] = e
    started, order = {}, []
    resolved = {}
    for line in open(run / "decisions.jsonl"):
        d = json.loads(line)
        if d["phase"] == "decision_started":
            started[d["decision_id"]] = d
            order.append(d["decision_id"])
        else:
            resolved[d["decision_id"]] = d
    totals["decisions"] += len(order)
    cur = None
    for idx, did in enumerate(order):
        s, r = started[did], resolved[did]
        if s["decision_type"] != "LIQUIDATION_DECISION":
            # a non-liquidation decision by the same player closes its open episode
            if cur and s["player_id"] == cur["player"]:
                cur = None
            continue
        totals["liquidation_decisions"] += 1
        pp = lit(s.get("prompt_payload_raw") or s["prompt_payload"])
        sc = pp["action_state"]["scenario"]
        sig = (s["player_id"], int(s["turn_index"]), sc["owed_amount"], sc.get("reason"), sc.get("owed_to_player_id"))
        fa = lit(r["final_action"])
        action = fa["action"]
        fb = str(r["fallback_used"]) == "True"
        # Grok text against applied call
        conflict = None
        model = LABEL.get(s["player_name"], s["player_name"])
        if model == "Grok":
            atts = lit(r["attempts"])
            sel = atts[-1] if isinstance(atts, list) and atts else None
            content = None
            if isinstance(sel, dict):
                content = sel.get("assistant_content")
                if content is None:
                    rr = sel.get("raw_response") or {}
                    try:
                        content = rr["choices"][0]["message"].get("content")
                    except Exception:
                        content = None
            if content:
                m = NAME_RE.search(content)
                if m:
                    conflict = (m.group(1) != action)
        s0, s1 = int(r["emitted_event_seq_start"]), int(r["emitted_event_seq_end"])
        if cur is None or cur["sig"] != sig:
            cur = {"game": gno, "sig": sig, "player": s["player_id"], "model": model, "turn": sig[1],
                   "debt": sc["owed_amount"], "reason": sc.get("reason"), "creditor": sc.get("owed_to_player_id"),
                   "cash_first": pp["game_state"]["you"]["cash"], "first_decision": idx,
                   "decisions": [], "actions": [], "fallback": [], "grok_conflict": [], "ranges": []}
            episodes.append(cur)
        cur["decisions"].append(idx)
        cur["actions"].append(action)
        cur["fallback"].append(fb)
        cur["grok_conflict"].append(conflict)
        cur["ranges"].append((s0, s1))
    # close each episode of this game on the events its last decision emitted
    for ep in [e for e in episodes if e["game"] == gno]:
        s0, s1 = ep["ranges"][-1]
        evs = [events[q] for q in range(s0, s1 + 1) if q in events]
        bankrupt = any(e["type"] == "CASH_CHANGED" and e["payload"].get("player_id") == ep["player"]
                       and str(e["payload"].get("reason", "")).startswith("BANKRUPTCY") for e in evs)
        bankrupt = bankrupt or ep["actions"][-1] == "declare_bankruptcy"
        pay_exact = [e["seq"] for e in evs if e["type"] == "CASH_CHANGED" and e["payload"].get("player_id") == ep["player"]
                     and e["payload"].get("delta") == -ep["debt"]
                     and not str(e["payload"].get("reason", "")).startswith(("MORTGAGE", "SELL", "BANKRUPTCY"))]
        rent_exact = [e["seq"] for e in evs if e["type"] == "RENT_PAID" and e["payload"].get("from_player_id") == ep["player"]
                      and e["payload"].get("amount") == ep["debt"]]
        ep["closing_event_types"] = [e["type"] for e in evs]
        ep["payment_event_seqs"] = pay_exact
        ep["rent_paid_event_seqs"] = rent_exact
        if bankrupt:
            ep["outcome"] = "eliminated"
            ep["declared"] = ep["actions"][-1] == "declare_bankruptcy"
        elif pay_exact:
            ep["outcome"] = "paid"
        else:
            ep["outcome"] = "unclosed"

for ep in episodes:
    ep["sig"] = list(ep["sig"])
    ep["n_actions"] = len(ep["actions"])
    ep["sold_buildings"] = "sell_houses_or_hotel" in ep["actions"]

paid = [e for e in episodes if e["outcome"] == "paid"]
elim = [e for e in episodes if e["outcome"] == "eliminated"]
res = {
    "scope": "read-only event reduction; no engine, replay or model call",
    "source_sha256": src,
    "decisions": totals["decisions"], "liquidation_decisions": totals["liquidation_decisions"],
    "episodes": len(episodes), "paid": len(paid), "eliminated": len(elim),
    "unclosed": sum(e["outcome"] == "unclosed" for e in episodes),
    "paid_single_action": sum(e["n_actions"] == 1 for e in paid),
    "paid_multi_action": sum(e["n_actions"] >= 2 for e in paid),
    "paid_action_count_distribution": dict(sorted(Counter(e["n_actions"] for e in paid).items())),
    "paid_with_building_sale": sum(e["sold_buildings"] for e in paid),
    "paid_actions_total": sum(e["n_actions"] for e in paid),
    "paid_mortgage_actions": sum(a == "mortgage_property" for e in paid for a in e["actions"]),
    "paid_sale_actions": sum(a == "sell_houses_or_hotel" for e in paid for a in e["actions"]),
    "paid_actions_other": dict(Counter(a for e in paid for a in e["actions"] if a not in ("mortgage_property", "sell_houses_or_hotel"))),
    "paid_total_debt": sum(e["debt"] for e in paid),
    "paid_episodes_with_engine_default": sum(any(e["fallback"]) for e in paid),
    "paid_actions_with_engine_default": sum(sum(e["fallback"]) for e in paid),
    "paid_episodes_with_rent_reason": sum(e["reason"] == "RENT" for e in paid),
    "paid_rent_episodes_with_matching_RENT_PAID_event": sum(bool(e["rent_paid_event_seqs"]) for e in paid if e["reason"] == "RENT"),
    "grok_paid_episodes": sum(e["model"] == "Grok" for e in paid),
    "grok_paid_actions": sum(e["n_actions"] for e in paid if e["model"] == "Grok"),
    "grok_paid_actions_with_named_text": sum(c is not None for e in paid if e["model"] == "Grok" for c in e["grok_conflict"]),
    "grok_paid_actions_text_names_other_action": sum(c is True for e in paid if e["model"] == "Grok" for c in e["grok_conflict"]),
    "grok_paid_episodes_with_conflict": sum(any(c is True for c in e["grok_conflict"]) for e in paid if e["model"] == "Grok"),
    "grok_conflict_rows_in_paid": [{"game": e["game"], "turn": e["turn"], "debt": e["debt"], "actions": e["actions"], "conflict": e["grok_conflict"]}
                                   for e in paid if e["model"] == "Grok" and any(c is True for c in e["grok_conflict"])],
    "eliminated_after_some_liquidation_action": sum(e["n_actions"] >= 2 for e in elim),
    "eliminated_with_engine_default": sum(any(e["fallback"]) for e in elim),
    "eliminated_declared": sum(e.get("declared", False) for e in elim),
    "grok_elim_text_names_other_action": [{"game": e["game"], "turn": e["turn"], "debt": e["debt"], "actions": e["actions"], "conflict": e["grok_conflict"]}
                                          for e in elim if e["model"] == "Grok" and any(c is True for c in e["grok_conflict"])],
    "by_model": {m: {"episodes": sum(e["model"] == m for e in episodes), "paid": sum(e["model"] == m for e in paid),
                     "eliminated": sum(e["model"] == m for e in elim),
                     "paid_multi_action": sum(e["model"] == m and e["n_actions"] >= 2 for e in paid),
                     "paid_with_building_sale": sum(e["model"] == m and e["sold_buildings"] for e in paid)}
                 for m in ("Sol", "Gemini", "Opus", "Grok")},
    "later_eliminated_same_game": None,
}
elim_players = {(e["game"], e["player"]) for e in elim}
res["paid_episodes_of_players_later_eliminated"] = sum((e["game"], e["player"]) in elim_players for e in paid)

# ---- reconcile with the four frozen drafts ---------------------------------
mine = {(e["game"], e["player"], e["first_decision"]): e for e in episodes}


def dec_index(x):
    if isinstance(x, int):
        return x
    return int(str(x).rsplit("-", 1)[-1])


def load(name):
    if name == "astra":
        d = json.load(open(ROOT / "full_drafts/astra/data/liquidation_episodes.json"))
        return {(r["game"], r["player"], dec_index(r["first_decision"])): (r["debt"], r["outcome"], len(r["actions"]), r["upper_bound"]) for r in d}
    if name == "sol":
        d = json.load(open(ROOT / "full_drafts/sol/data/debt_episodes.json"))
        return {(r["game"], r["player"], dec_index(r["first_decision"])): (r["debt"], r["outcome"], len(r["decisions"]), r["bound"]) for r in d}
    if name == "opus":
        d = json.load(open(ROOT / "full_drafts/opus/data/debt_episodes.json"))["episodes"]
        return {(r["game"], r["player"], dec_index(r["first_decision"])): (r["owed"], r["outcome"], r["n_decisions"], r["nominal_bound"]) for r in d}
    d = json.load(open(ROOT / "full_drafts/fable_5_2/data/a4_debt_episodes.json"))
    return {(r["game"], r["player"], dec_index(r["first_decision"])): (r["debt"], r["outcome"], len(r["decisions"]), r["bound_U"]) for r in d}


def norm(o):
    o = str(o).lower()
    return "paid" if o.startswith("paid") else "eliminated"


recon = {}
bounds = {}
for name in ("astra", "sol", "opus", "fable_5_2"):
    other = load(name)
    bounds[name] = {k: v[3] for k, v in other.items()}
    only_mine = sorted(set(mine) - set(other))
    only_theirs = sorted(set(other) - set(mine))
    diff = []
    for k in set(mine) & set(other):
        m = mine[k]
        if (m["debt"], m["outcome"], m["n_actions"]) != (other[k][0], norm(other[k][1]), other[k][2]):
            diff.append([list(k), [m["debt"], m["outcome"], m["n_actions"]], [other[k][0], norm(other[k][1]), other[k][2]]])
    recon[name] = {"rows": len(other), "keys_only_in_this_check": [list(k) for k in only_mine],
                   "keys_only_in_draft": [list(k) for k in only_theirs], "field_differences": diff}
res["reconciliation_with_drafts"] = recon
# do the four drafts agree on the own-asset bound?
keys = set.intersection(*[set(b) for b in bounds.values()])
bd = [[list(k), {n: bounds[n][k] for n in bounds}] for k in sorted(keys) if len({bounds[n][k] for n in bounds}) > 1]
res["bound_disagreements_across_drafts"] = bd
# elimination classes from the drafts' bounds (bound below debt)
fab = json.load(open(ROOT / "full_drafts/fable_5_2/data/a4_debt_episodes.json"))
res["fable_inherited_class_counts"] = dict(Counter(r["inherited_class"] for r in fab))
res["eliminated_bound_below_debt_fable"] = sum(r["outcome"] != "paid" and r["bound_U"] < r["debt"] for r in fab)
res["paid_bound_below_debt_fable"] = sum(r["outcome"] == "paid" and r["bound_U"] < r["debt"] for r in fab)
res["paid_bound_minus_debt_under_250_fable"] = sum(r["outcome"] == "paid" and 0 <= r["bound_U"] - r["debt"] < 250 for r in fab)
res["episodes_rows"] = episodes
OUT.write_text(json.dumps(res, indent=1))
for k, v in res.items():
    if k in ("source_sha256", "episodes_rows"):
        continue
    print(k, ":", json.dumps(v)[:900])
