#!/usr/bin/env python3
"""Verify the retained transcript manifest against canonical files and build this draft's supplementary quotes.

1. Re-checks every field and span of ../../data/transcript_manifest.json against the canonical saved-game files
   (file SHA-256, JSON pointer value, field SHA-256, span text) and against ../../sections/transcript_quotes.tex.
2. Builds supplementary exact quotes (public messages and applied private notes) for decisions this draft adds.
   Each requested excerpt must be a contiguous substring of the canonical field or the build fails.
Outputs: data/transcript_manifest_supplement.json, sections/quotes_supplement.tex, qa/quote_verification.json
No text is paraphrased or repaired. No engine or model call.
"""
import json, glob, hashlib, pathlib, re, sys
HERE = pathlib.Path(__file__).resolve().parent.parent
RW = HERE.parent.parent
REPO = HERE.parents[4]
NAME = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini", "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}

def sha(b): return hashlib.sha256(b).hexdigest()
def resolve(doc, ptr):
    cur = doc
    for part in ptr.strip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur
def tex(s):
    rep = {"\\": r"\textbackslash{}", "$": r"\$", "%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", '"': r"\char34{}"}
    return "".join(rep.get(ch, ch) for ch in s)

report = {"base_manifest": {}, "supplement": {}, "prompt_strings": {}}
# ---------- 1. base manifest ----------
man = json.loads((RW / "data" / "transcript_manifest.json").read_text())
cache = {}
ok = 0
for fid, f in man["fields"].items():
    p = REPO / f["source"]
    if f["source"] not in cache:
        b = p.read_bytes(); cache[f["source"]] = (sha(b), b.decode().splitlines())
    s, lines = cache[f["source"]]
    doc = json.loads(lines[f["jsonl_line_1based"] - 1]) if f.get("jsonl_line_1based") else json.loads("\n".join(lines))
    val = resolve(doc, f["json_pointer"])
    assert s == f["source_sha256"], ("file hash", fid)
    assert val == f["text"] and sha(val.encode()) == f["field_sha256"], ("field", fid)
    ok += 1
spans = 0
for q in man["quotes"]:
    for e in q["excerpts"]:
        assert man["fields"][e["field_id"]]["text"][e["span"][0]:e["span"][1]] == e["text"], q["id"]
        spans += 1
shared_tex = (RW / "sections" / "transcript_quotes.tex").read_text()
declared = set(re.findall(r"\\DeclareTranscriptQuote\{([^}]+)\}", shared_tex))
assert declared == {q["id"] for q in man["quotes"]}, "macro ids differ from manifest ids"
# every excerpt must appear, TeX-escaped, in the shared macro file
# a newline inside a source field is typeset as \par in the shared macro file; nothing else differs
missing = [q["id"] for q in man["quotes"] for e in q["excerpts"] if re.sub(r"\n+", lambda m: r"\par ", tex(e["text"])) not in shared_tex]
report["base_manifest"] = {"fields_checked_against_canonical_files": ok, "spans_checked": spans, "quote_macros": len(declared),
                           "excerpts_not_found_verbatim_in_shared_tex_after_escaping": missing,
                           "shared_tex_sha256": sha((RW / "sections" / "transcript_quotes.tex").read_bytes()),
                           "manifest_sha256": sha((RW / "data" / "transcript_manifest.json").read_bytes())}

# ---------- 2. supplementary quotes ----------
CH = {"public_message": "public message", "private_thought": "applied private note"}
SPEC = [  # id, game, decision, field, exact excerpts (noncontiguous spans joined by an editorial ellipsis), kind
 ("fx-g15-offer", 15, 168, "public_message", ["Grok: both my greens for Ventnor and $100. We each get a monopoly instead of letting the developed oranges dictate the game."], "card"),
 ("fx-g15-offer-note", 15, 168, "private_thought", ["Grok gets a real monopoly but limited building liquidity; I can reach three houses using spare-property mortgages."], "card"),
 ("fx-g15-refusal", 15, 169, "public_message", ["No. I'm not handing you a yellow monopoly so you can build it this turn. Ventnor stays mine."], "card"),
 ("fx-g15-refusal-note", 15, 169, "private_thought", ["Trade gives p4 Atlantic+Ventnor+Marvin and ~$830 plus mortgage capacity to drop 5+ yellow houses ($150) immediately, then they roll again on doubles. I would get green monopoly but only ~$233 \u2014 can't even even-build one house each ($600)."], "card"),
 ("fx-g15-sweetener", 15, 174, "public_message", ["Both greens, Kentucky, and $250 for Ventnor. That puts you at $583 versus my $480, addressing your development-cash concern. We both get a way to compete with oranges."], "card"),
 ("fx-g15-final-refusal", 15, 175, "public_message", ["No. $250 doesn't fix it. You'd still mortgage and drop houses on yellows before you roll again. Ventnor stays mine."], "card"),
 ("fx-g1-boardwalk-note", 1, 309, "private_thought", ["Accept $100 over the $80 ceiling. p1's max liquidity is ~$218; they survive 1-house yellow but not a later light-blue hotel, and bankruptcy to p3 hands p3 Boardwalk. Only I can complete dark blue, and p3 would buy this as a blocker.", "Cannot unmortgage ($220) or build yet."], "card"),
 ("fx-g11-offer", 11, 255, "public_message", ["Virginia completes your pinks. Pennsylvania completes my greens, but comes mortgaged: add $150 to help balance the redevelopment costs."], "card"),
 ("fx-g11-reject", 11, 256, "public_message", ["No. Virginia doesn't complete the pinks \u2014 you still have St. Charles. Pennsylvania completes your greens. Not trading it."], "card"),
 ("fx-g11-concede", 11, 257, "public_message", ["You're right\u2014I missed St. Charles. Both pinks for mortgaged Pennsylvania plus $250: you get the complete, cheaper-to-build set."], "card"),
 ("fx-g11-reject-again", 11, 258, "public_message", ["No. Pennsylvania completes your greens. I'm not handing you that set, with or without the pinks."], "card"),
 ("fx-g16-plan", 16, 103, "private_thought", ["End, buy Virginia on sight, then house pink"], "inline"),
 ("fx-g16-note", 16, 159, "private_thought", ["Buy at list is the only way to close pink."], "inline"),
 ("fx-g16-public", 16, 159, "public_message", ["Virginia is mine. Pink set closed."], "inline"),
]
need = {}
for sid, g, dec, field, exc, kind in SPEC: need.setdefault(g, set()).add(dec)
resolved = {}
for g, decs in need.items():
    cand = glob.glob(str(REPO / "saved_games" / "railway-research-*" / f"game-{g:02d}-*" / "run" / "decisions.jsonl"))
    assert len(cand) == 1
    p = pathlib.Path(cand[0]); fsha = sha(p.read_bytes())
    with p.open() as fh:
        for ln, line in enumerate(fh, 1):
            d = json.loads(line)
            if d.get("phase") == "decision_resolved" and int(d["decision_id"][-6:]) in decs:
                resolved[(g, int(d["decision_id"][-6:]))] = (str(p.relative_to(REPO)), fsha, ln, d)
sup = {"schema_version": "transcript-supplement-fable52-v1",
       "note": "Supplementary exact spans added for this draft. Same conventions as transcript_manifest.json: verbatim contiguous spans, zero-based code-point offsets, one-based JSONL lines.",
       "quotes": []}
out_tex = ["% Generated by tools/build_quotes.py from canonical decisions.jsonl; do not edit quotation text.",
           "% Exact spans, offsets and hashes: data/transcript_manifest_supplement.json."]
for sid, g, dec, field, exc, kind in SPEC:
    src, fsha, ln, d = resolved[(g, dec)]
    fa = d["final_action"]; text = fa[field]
    assert isinstance(text, str) and text, (sid, "empty field")
    sel = [i for i, a in enumerate(d["attempts"]) if a.get("outcome") == "valid"]
    assert len(sel) == 1 and not d["fallback_used"], (sid, "selected attempt")
    att = sel[0]; cond = d["attempts"][att].get("response_condition")
    spans = []
    for e in exc:
        i = text.find(e)
        assert i >= 0 and text.count(e) == 1, (sid, "span not found exactly once", e[:40])
        spans.append([i, i + len(e)])
    assert spans == sorted(spans), sid
    meta = f"{NAME[d['openrouter_model_id']]} \u00b7 {CH[field]} \u00b7 G{g} d{dec} \u00b7 attempt {att} \u00b7 excerpt"
    sup["quotes"].append({"id": sid, "kind": kind, "metadata": meta, "game": g, "decision": dec, "decision_id": d["decision_id"], "turn": d["turn_index"],
                          "speaker": NAME[d["openrouter_model_id"]], "player_id": d["player_id"], "applied_action": fa["action"], "response_condition": cond,
                          "selected_attempt": att, "source": src, "source_sha256": fsha, "jsonl_line_1based": ln, "json_pointer": f"/final_action/{field}",
                          "field_sha256": sha(text.encode()), "field_text": text, "excerpts": [{"span": s, "text": text[s[0]:s[1]]} for s in spans]})
    body = r" \textnormal{[\ldots]} ".join(tex(text[s[0]:s[1]]) for s in spans)
    if kind == "card":
        out_tex.append(r"\DeclareTranscriptQuote{%s}{%s}{%s}" % (sid, tex(meta), body))
    else:
        out_tex.append(r"\DeclareInlineQuote{%s}{%s}" % (sid, body))
(HERE / "data" / "transcript_manifest_supplement.json").write_text(json.dumps(sup, indent=1, ensure_ascii=False))
(HERE / "sections" / "quotes_supplement.tex").write_text("\n".join(out_tex) + "\n")
report["supplement"] = {"quotes": len(sup["quotes"]), "cards": sum(1 for q in sup["quotes"] if q["kind"] == "card"), "inline": sum(1 for q in sup["quotes"] if q["kind"] == "inline"),
                        "spans": sum(len(q["excerpts"]) for q in sup["quotes"]), "all_spans_found_exactly_once_in_canonical_field": True,
                        "response_conditions": sorted({q["response_condition"] for q in sup["quotes"]})}

# ---------- 3. instruction strings quoted in the paper ----------
PROMPT = {
 "win": "win the game by maximizing long-term advantage and being the last non-bankrupt player",
 "strategy": "any legal strategy or personality (aggressive, deceptive, cooperative, conservative, manipulative, opportunistic, friendly, hostile, etc.)",
 "public": "negotiate, bluff, deceive, cooperate, intimidate, joke, or stay silent",
 "honesty": "Deception in public chat is allowed; private thoughts should reflect true reasoning.",
 "action_only": "Do not include private_thought or a reasoning transcript.",
}
srcs = [REPO / "python/packages/arena/src/monopoly_arena/player_config.py", REPO / "python/packages/arena/src/monopoly_arena/prompting.py"]
blob = "\n".join(p.read_text() for p in srcs)
# also confirm presence in one delivered standard prompt and one action-only retry prompt from the saved games
g1 = glob.glob(str(REPO / "saved_games" / "railway-research-*" / "game-01-*" / "run" / "decisions.jsonl"))[0]
std = retry = None
with open(g1) as fh:
    for line in fh:
        d = json.loads(line)
        if d.get("phase") == "decision_started" and std is None:
            std = json.dumps(d.get("prompt_messages"), ensure_ascii=False)   # initial standard request
        if d.get("phase") != "decision_resolved": continue
        for a in d["attempts"]:
            if a.get("response_condition") == "same_model_without_private_thought" and retry is None:
                retry = json.dumps(a.get("prompt_messages"), ensure_ascii=False)
        if std and retry: break
def present(s, hay): return s in hay or json.dumps(s, ensure_ascii=False)[1:-1] in hay
for k, s in PROMPT.items():
    report["prompt_strings"][k] = {"text": s, "in_arena_source": s in blob, "in_saved_standard_prompt_G1": present(s, std), "in_saved_action_only_prompt_G1": present(s, retry)}
(HERE / "qa").mkdir(exist_ok=True)
(HERE / "qa" / "quote_verification.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
print(json.dumps(report, indent=1, ensure_ascii=False))
