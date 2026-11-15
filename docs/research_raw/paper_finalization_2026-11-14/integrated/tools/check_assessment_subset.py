"""Verify stored fields for the declared collateral-assessment subset.

The three reading labels are model-assisted judgments made by Fable and the
integrator after reading the 21 additional fields. This script preserves their
definitions, population and source spans; it does not automate semantic validity.
No engine, policy, replay, state search or provider call is used.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in HERE.parents if (p / "contracts/data/board.json").exists())
source = json.loads((HERE / "data/complete_financing_records.json").read_text())
rows = source["rows"]
subset = [r for r in rows if r["U0"] < r["debt"] and r["Mstar"] > r["M0"]]
assert len(subset) == 37
assert sum(r["Mstar"] > r["M0"] for r in rows) == 121
unpayable = [r for r in subset if r["Ustar"] < r["debt"]]
assert len(unpayable) == 21
listed = {(3, 426), (5, 309), (8, 280)}
discussed = {(2, 215), (10, 188)}
cache = {}
annotations = []
for r in unpayable:
    path = ROOT / r["source"]
    if path not in cache:
        blob = path.read_bytes()
        assert hashlib.sha256(blob).hexdigest() == source["sources"][r["source"]]
        cache[path] = {int(x["decision_id"][-6:]): (i, x)
                       for i, line in enumerate(blob.splitlines(), 1)
                       if (x := json.loads(line))["phase"] == "decision_resolved"}
    line, record = cache[path][r["decision"]]
    note = record["final_action"].get("private_thought")
    attempt = record["attempts"][-1]
    explanation = attempt.get("raw_response", {}).get("choices", [{}])[0].get("message", {}).get("reasoning")
    text = note or explanation
    assert text == (r["applied_action"].get("private_thought") or r["provider_reasoning"])
    key = r["game"], r["decision"]
    label = "listed maximum" if key in listed else "resource discussed" if key in discussed else "inclusive amount"
    annotations.append(dict(game=r["game"], decision=r["decision"], model=r["model"],
                            debt=r["debt"], U0=r["U0"], Ustar=r["Ustar"], label=label,
                            selected_channel="authored note" if note else "returned explanation",
                            text=text, field_sha256=hashlib.sha256(text.encode()).hexdigest(),
                            source=r["source"], source_sha256=source["sources"][r["source"]],
                            jsonl_line_1based=line))
assert sum(r["label"] == "inclusive amount" for r in annotations) == 16
assert sum(r["label"] == "resource discussed" for r in annotations) == 2
assert sum(r["label"] == "listed maximum" for r in annotations) == 3
result = dict(population="U0 < debt and Mstar > M0", size=37,
              payable=16, unpayable=21, additional_fields=annotations,
              reading="Fable 5.2 and Astra integrator; retrospective, model-assisted, not human-validated",
              definitions={"inclusive amount": "A full-bound total, proceeds or deficit includes the released principal, sometimes using aggregate wording; not necessarily an explicit dependency or wholly correct response.",
                           "resource discussed": "Released mortgages are stated without a full-bound amount.",
                           "listed maximum": "U0 is described as the maximum, omitting released mortgages."})
(HERE / "data/assessment_subset.json").write_text(json.dumps(result, indent=2) + "\n")
table = [r"\begin{longtable}{@{}lrrrl@{}}",
         r"\caption{The 21 unpayable entries in the collateral-assessment subset. Categories describe one selected field, not whole-response accuracy.}\label{tab:assessment-extension}\\",
         r"\toprule Entry & Debt & $U_0$ & $U_*$ & Selected field's content\\\midrule\endfirsthead",
         r"\toprule Entry & Debt & $U_0$ & $U_*$ & Selected field's content\\\midrule\endhead"]
for r in annotations:
    table.append(f"G{r['game']} d{r['decision']} & {r['debt']:,} & {r['U0']:,} & {r['Ustar']:,} & {r['label']} " + r"\\")
table += [r"\bottomrule\end{longtable}"]
(HERE / "sections/assessment_subset.tex").write_text("\n".join(table) + "\n")
print("Verified all 21 additional fields in the defined 37-entry subset; preserved model-reading labels.")
