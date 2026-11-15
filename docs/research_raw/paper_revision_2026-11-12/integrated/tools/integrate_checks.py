"""Recount stored first actions and print all initial texts; no engine execution."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in HERE.parents if (p / "saved_games").is_dir())
read = lambda n: json.loads((HERE / "data" / n).read_text())
eps = read("liquidation_episodes.json")
necessary = read("necessary_collateral.json")["necessary_unlocked_collateral"]
targets = {(e["game"], e["first_decision"]): e for e in eps}
needed = {(r["game"], r["decision"]): r for r in necessary}
games = read("game_map.json")
sources, rows, fields, extra_quotes = {}, [], [], []
selected_spans = {
    (5,263): ("integrated-g5-revision", "Gemini", "I initially miscalculated!", "This is key!"),
    (13,253): ("integrated-g13-buyer", "Opus", "I'm also considering the scenario", "the mortgage interest is minor."),
    (18,431): ("integrated-g18-reservation", "Opus", "Buying Pacific might just prolong p1's survival", "heavy rent.")
}
scenario = ("Choose exactly one liquidation action now. The engine will apply it, "
            "update your cash/assets, and ask you again if you still cannot pay. "
            "Declare bankruptcy only when you cannot or should not raise enough cash.")
scenario_count = 0
acceptance_conflicts = []
grok_acceptances = 0
only_declaration = 0
for game, run in games.items():
    game = int(game)
    p = ROOT / run / "decisions.jsonl"
    blob = p.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    sources[str(p.relative_to(ROOT))] = digest
    for line_number, line in enumerate(blob.splitlines(), 1):
        rec = json.loads(line)
        if rec["phase"] == "decision_started":
            if scenario in json.dumps(rec, ensure_ascii=False):
                scenario_count += 1
            d = int(rec["decision_id"].rsplit("-",1)[1])
            if (game,d) in targets:
                e = targets[(game,d)]
                if e["upper_bound"] < e["debt"]:
                    if rec["prompt_payload"]["action_state"]["available_actions"] == ["declare_bankruptcy"]:
                        only_declaration += 1
            continue
        if rec["phase"] != "decision_resolved":
            continue
        decision = int(rec["decision_id"].rsplit("-", 1)[1])
        key = (game, decision)
        if "grok" in rec["openrouter_model_id"] and rec["final_action"]["action"] == "accept_trade":
            grok_acceptances += 1
            valid = [a for a in rec["attempts"] if a.get("outcome") == "valid"]
            named = re.search(r'"name"\s*:\s*"([a-z_]+)"', (valid[-1].get("assistant_content") or "") if valid else "")
            if named and named[1] != "accept_trade":
                acceptance_conflicts.append(dict(game=game,decision=decision,named_action=named[1]))
        if key in selected_spans:
            qid, speaker, start_text, end_text = selected_spans[key]
            index = len(rec["attempts"]) - 1
            text = rec["attempts"][index]["raw_response"]["choices"][0]["message"]["reasoning"]
            start = text.index(start_text)
            stop = text.index(end_text,start)+len(end_text)
            extra_quotes.append(dict(id=qid,game=game,decision=decision,speaker=speaker,
                metadata=f"{speaker} · provider-returned explanation · G{game} d{decision} · excerpt",
                source=str(p.relative_to(ROOT)),source_sha256=digest,jsonl_line_1based=line_number,
                json_pointer=f"/attempts/{index}/raw_response/choices/0/message/reasoning",
                field_sha256=hashlib.sha256(text.encode()).hexdigest(),
                spans=[dict(span=[start,stop],text=text[start:stop])]))
        if key in targets:
            e = targets[key]
            action = rec["final_action"]["action"]
            assert action == e["actions"][0]
            cls = ("payable" if e["outcome"] == "paid" or key in {(12,190),(12,249),(17,234)}
                   else "above_bound" if e["upper_bound"] < e["debt"] else "menu_restricted")
            rows.append(dict(game=game, decision=decision, category=cls, action=action,
                             fallback=rec["fallback_used"], outcome=e["outcome"]))
        if key in needed:
            r = needed[key]
            note = rec["final_action"].get("private_thought")
            if note:
                text = note
                channel = "Applied private note"
                pointer = "/final_action/private_thought"
            else:
                index = len(rec["attempts"]) - 1
                text = rec["attempts"][index]["raw_response"]["choices"][0]["message"]["reasoning"]
                channel = "Provider-returned explanation"
                pointer = f"/attempts/{index}/raw_response/choices/0/message/reasoning"
            assert text == (r["private_note"] if note else r["provider_reasoning"])
            model = next(m for m,k in [("Sol","sol"),("Gemini","argon"),("Opus","opus"),("Grok","grok")] if k in r["model"].lower())
            fields.append(dict(game=game, decision=decision, model=model, outcome=r["outcome"],
                               channel=channel, text=text, source=str(p.relative_to(ROOT)),
                               source_sha256=digest, jsonl_line_1based=line_number,
                               json_pointer=pointer, field_sha256=hashlib.sha256(text.encode()).hexdigest()))
assert len(rows) == 188 and len(fields) == 16
assert scenario_count == 338  # Initial decision payloads; attempt prompt files are a different count.
summary = {c: dict(Counter(r["action"] for r in rows if r["category"] == c))
           for c in ["payable", "above_bound", "menu_restricted"]}
assert summary["payable"]["declare_bankruptcy"] == 3
assert summary["above_bound"]["declare_bankruptcy"] == 50
assert not any(r["fallback"] for r in rows)
assert grok_acceptances == 28 and len(acceptance_conflicts) == 7
assert only_declaration == 8
def tex(s):
    escapes = {"\\":r"\textbackslash{}", "&":r"\&", "%":r"\%", "$":r"\$", "#":r"\#",
               "_":r"\_", "{":r"\{", "}":r"\}", "~":r"\textasciitilde{}", "^":r"\textasciicircum{}",
               "→":r"\(\rightarrow\)"}
    return "".join(escapes.get(c,c) for c in s).replace("\n", r"\par "+"\n")
blocks = []
for f in sorted(fields, key=lambda r:(r["game"],r["decision"])):
    blocks.append(r"\Needspace{8\baselineskip}\subsection*{"+f'G{f["game"]} d{f["decision"]}, {f["model"]}, {f["outcome"]}'+"}\n"
                  + r"{\small\textit{"+f["channel"]+r". Full field at the first decision.}\par "
                  + tex(f["text"]) + r"\par}"+"\n")
(HERE/"sections/necessary_texts.tex").write_text("\n".join(blocks))
(HERE/"sections/integration_quotes.tex").write_text("\n".join(
    r"\DeclareTranscriptQuote{"+q["id"]+"}{"+tex(q["metadata"])+"}{"+tex(q["spans"][0]["text"])+"}"
    for q in extra_quotes)+"\n")
(HERE/"data/integration_quote_manifest.json").write_text(json.dumps(dict(quotes=extra_quotes),indent=2)+"\n")
(HERE/"data/initial_text_manifest.json").write_text(json.dumps(dict(fields=fields,sources=sources),indent=2)+"\n")
(HERE/"data/first_action_checks.json").write_text(json.dumps(dict(summary=summary,rows=rows,
    scenario_note=scenario,scenario_count=scenario_count,sources=sources,
    grok_acceptances=grok_acceptances,acceptance_conflicts=acceptance_conflicts,
    above_bound_only_declaration=only_declaration),indent=2)+"\n")

plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.spines.top":False,
                     "axes.spines.right":False,"pdf.fonttype":42})
fig,ax = plt.subplots(figsize=(6.8,4.4))
ordered = sorted(necessary,key=lambda r:(r["game"],r["decision"]))
y = np.arange(len(ordered))
initial = np.array([r["cash"]+r["listed_mortgages"]+r["salvage"] for r in ordered])
full = np.array([r["upper_bound"] for r in ordered])
ax.barh(y,initial,color="#567d9b",height=.65,label="Cash + all salvage + initial mortgages")
ax.barh(y,full-initial,left=initial,color="#d6e0e7",height=.65,label="Mortgages released by sales")
for i,r in enumerate(ordered):
    ax.plot([r["debt"]]*2,[i-.39,i+.39],color="#1e1e1e",lw=1.5)
    if r["outcome"] != "paid":
        ax.scatter([r["debt"]],[i],marker="x",s=35,color="#a64817",zorder=4)
ax.plot([],[],color="#1e1e1e",label="Debt")
ax.scatter([],[],marker="x",s=35,color="#a64817",label="Declared bankruptcy")
models=[next(m for m,k in [("Sol","sol"),("Gemini","argon"),("Opus","opus"),("Grok","grok")] if k in r["model"].lower()) for r in ordered]
ax.set(yticks=y,yticklabels=[f'G{r["game"]} d{r["decision"]}  {m}' for r,m in zip(ordered,models)],
       xlabel="Game dollars",xlim=(0,1550))
ax.invert_yaxis()
ax.grid(axis="x",alpha=.12)
ax.legend(loc="upper center",bbox_to_anchor=(.44,1.19),ncol=2,frameon=False,fontsize=7)
fig.tight_layout()
fig.savefig(HERE/"assets/financial_dependencies.pdf")
fig.savefig(HERE/"assets/financial_dependencies.png",dpi=180)
plt.close(fig)
print(json.dumps(dict(episodes=len(rows),initial_fields=len(fields),scenario_prompts=scenario_count,summary=summary),indent=2))
