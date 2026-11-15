"""For every debt episode, compare the first liquidation menu's mortgageable deeds with the deeds actually
mortgaged later in the episode. A mortgage of a deed absent from the first menu is an 'unlocked' mortgage
(made available by an earlier building sale). Read-only over canonical decisions.jsonl and the retained
Fable/Astra/Opus-agreeing debt ledger. Run from repo root with python3 -I."""
import collections, glob, hashlib, json, pathlib
ROOT = pathlib.Path.cwd(); REV = ROOT / "docs/research_raw/paper_revision_2026-11-11"
eps = json.loads((REV / "full_drafts/fable_5_2/data/a4_debt_episodes.json").read_text())
need = collections.defaultdict(set)
for e in eps:
    for d in e["decisions"]: need[e["game"]].add(d)
start, res_ = {}, {}
hashes = {}
for g in sorted(need):
    f = glob.glob(str(ROOT / f"saved_games/railway-research-*/game-{g:02d}-*/run/decisions.jsonl"))[0]
    hashes[g] = hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
    for line in open(f):
        r = json.loads(line); k = int(r["decision_id"].rsplit("-", 1)[1])
        if k not in need[g]: continue
        if r["phase"] == "decision_started":
            start[(g, k)] = r["prompt_payload"]["action_state"]["scenario"]["options"]
        else:
            res_[(g, k)] = r["final_action"]
rows = []
for e in eps:
    g = e["game"]; first = start[(g, e["decisions"][0])]
    first_mort = set(first.get("mortgageable_space_keys") or [])
    morts = [res_[(g, d)]["args"].get("space_key") or res_[(g, d)]["args"].get("property") or json.dumps(res_[(g, d)]["args"])
             for d in e["decisions"] if res_[(g, d)]["action"] == "mortgage_property"]
    sold_any = any(res_[(g, d)]["action"] == "sell_houses_or_hotel" for d in e["decisions"])
    unlocked = [m for m in morts if m not in first_mort]
    rows.append({"game": g, "first_decision": e["decisions"][0], "model": e["model"], "outcome": e["outcome"],
                 "sold_buildings": sold_any, "mortgages": len(morts), "unlocked_mortgages": len(unlocked)})
paid = [r for r in rows if r["outcome"] == "paid"]
out = {"decision_file_sha256": hashes,
       "paid_episodes": len(paid),
       "paid_with_sale_and_mortgage": sum(r["sold_buildings"] and r["mortgages"] > 0 for r in paid),
       "paid_with_unlocked_mortgage": sum(r["unlocked_mortgages"] > 0 for r in paid),
       "paid_with_unlocked_mortgage_by_model": dict(collections.Counter(r["model"] for r in paid if r["unlocked_mortgages"] > 0)),
       "unlocked_mortgage_actions_in_paid": sum(r["unlocked_mortgages"] for r in paid),
       "rows": rows}
p = REV / "reviews/opus/data/unlock_check.json"; p.write_text(json.dumps(out, indent=1))
print({k: v for k, v in out.items() if k not in ("rows", "decision_file_sha256")})
