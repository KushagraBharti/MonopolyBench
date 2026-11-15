"""Generate every displayed quotation from canonical decision records.

Each entry names a game, zero-based decision, channel and either the full
field or contiguous excerpt(s) given by exact start/end marker strings.  The
script reads ``decisions.jsonl`` directly, writes ``sections/quotes.tex`` and
``data/quote_manifest.json`` (path, line, pointer, span, hashes), checks that
reused quotations equal the previously checked definitions, and records the
first later prompt in which a public message was delivered to the named
counterparty.  Quotation text is never typed by hand in the manuscript.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from corpus import REPO, load_all, sha256_file

HERE = Path(__file__).resolve().parents[1]
OLD_SECTIONS = REPO / "docs/research_raw/paper_rewrite_2026-11-10/integrated/sections"

# channel -> (label, pointer builder)
CHANNELS = {
    "public": "public message",
    "note": "applied private note",
    "content": "assistant content (not applied)",
    "reasoning": "returned provider explanation",
}

# id, game, decision, channel, spec, reused_from (old id or None), deliver_to (model label or None)
# spec: "full" or list of (start_marker, end_marker) pairs; a span runs from the first
# occurrence of start_marker through the end of the first later occurrence of end_marker.
Q = [
    # ---- G2 -----------------------------------------------------------------
    ("g2-d118-liquidity-pitch", 2, 118, "public", "full", None, "Sol"),
    ("g2-d124-price", 2, 124, "public", "full", "g2-d124-price", "Opus"),
    ("g2-d124-note", 2, 124, "note", "full", "g2-d124-note", None),
    ("g2-d128-note", 2, 128, "note", "full", None, None),
    ("g2-d197-reverse", 2, 197, "public", "full", "g2-d197-reverse", "Sol"),
    # ---- G15 ----------------------------------------------------------------
    ("g15-d166-appeal", 15, 166, "public", "full", None, "Grok"),
    ("g15-d169-refusal-note", 15, 169, "note", [("Trade gives p4", "one house each ($600).")], "fx-g15-refusal-note", None),
    ("g15-d174-sweetener", 15, 174, "public", "full", "fx-g15-sweetener", "Grok"),
    ("g15-d175-final-refusal", 15, 175, "public", "full", "fx-g15-final-refusal", "Sol"),
    ("g15-d176-wait-note", 15, 176, "note", [("Seek B&O at auction", "when opponents need cash.")], None, None),
    # ---- G7 -----------------------------------------------------------------
    ("g7-d39-liquid", 7, 39, "public", "full", None, "Grok"),
    ("g7-d42-final", 7, 42, "public", [("$600, final.", "no set to protect.")], "g7_d42_public", "Sol"),
    ("g7-d42-ceiling", 7, 42, "note", [("If they return at $625", "Do not go above $625.")], "g7_d42_private", None),
    ("g7-d141-timed-bid", 7, 141, "note", [("p4 just acquired", "sell New York Avenue for cash.")], None, None),
    ("g7-d142-ask-note", 7, 142, "note", "full", None, None),
    # ---- G1 -----------------------------------------------------------------
    ("g1-d306-offer", 1, 306, "public", "full", None, "Grok"),
    ("g1-d307-counter", 1, 307, "public", "full", None, "Opus"),
    ("g1-d309-accept-note", 1, 309, "note", [("Accept $100 over the $80 ceiling.", "buy this as a blocker."), ("Cannot unmortgage ($220) or build yet.", "Cannot unmortgage ($220) or build yet.")], "fx-g1-boardwalk-note", None),
    # ---- G13 ----------------------------------------------------------------
    ("g13-d250-insurance", 13, 250, "public", "full", "g13-opening-insurance", "Opus"),
    ("g13-d252-floor", 13, 252, "note", "full", "g13-seller-floor", None),
    ("g13-d252-omission", 13, 252, "reasoning", [("I will frame the $130 offer", "may not calculate the mortgage themselves.")], "g13-omission-explanation", None),
    ("g13-d253-accept", 13, 253, "public", "full", "g13-acceptance", "Grok"),
    # ---- G18 ----------------------------------------------------------------
    ("g18-d420-note", 18, 420, "note", "full", None, None),
    ("g18-d431-assurance", 18, 431, "public", "full", "g18-assurance", "Sol"),
    ("g18-d441-invocation", 18, 441, "public", "full", "g18-invocation", "Opus"),
    ("g18-d442-withdrawal", 18, 442, "public", "full", "g18-withdrawal", "Sol"),
    ("g18-d442-explanation", 18, 442, "reasoning", "full", "g18-withdrawal-explanation", None),
    # ---- G20 ----------------------------------------------------------------
    ("g20-d96-appeal", 20, 96, "public", "full", "g20-coordination-appeal", "Grok"),
    ("g20-d97-recognition", 20, 97, "note", [("p4 is organizing a cash boycott", "don't wait on a sale.")], "g20-recognition-note", None),
    ("g20-d100-sale", 20, 100, "public", "full", "g20-sale-response", "Gemini"),
    ("g20-d101-refusal", 20, 101, "public", "full", "g20-concrete-refusal", "Grok"),
    # ---- G12 ----------------------------------------------------------------
    ("g12-d249-content", 12, 249, "content", [('"name": "sell_houses_or_hotel"', '"name": "sell_houses_or_hotel"'), ('"sell_plan": [', '"count": 2}]')], "g12-sale", None),
    ("g12-d249-note", 12, 249, "note", [("The sell_houses call was the correct action.", "Do not call another tool.")], "g12_d249_private_final", None),
    ("g12-d249-public", 12, 249, "public", "full", "g12_d249_public_bankruptcy", "Opus"),
    # ---- G17 (estate section) -------------------------------------------------
    ("g17-d234-public", 17, 234, "public", [("$530 max liquidity", "just $20 short.")], None, None),
    # ---- appendix controls ----------------------------------------------------
    ("g19-d135-public", 19, 135, "public", "full", "g19_d135_false_public", "Sol"),
    ("g19-d135-note", 19, 135, "note", [("Misread the board.", "not orange."), ("Abort this trade. Do not send it.", "Abort this trade. Do not send it.")], "g19-abort", None),
    ("g19-d136-public", 19, 136, "public", "full", "g19_d136_correction_accept", "Grok"),
    ("g11-d256-public", 11, 256, "public", "full", "fx-g11-reject", "Sol"),
    ("g11-d257-public", 11, 257, "public", "full", "fx-g11-concede", "Grok"),
    ("g11-d258-public", 11, 258, "public", "full", "fx-g11-reject-again", "Sol"),
    ("g3-d363-public", 3, 363, "public", [("Houses stay locked.", "unless someone frees buildings.")], "G3-2", "Gemini"),
    ("g3-d363-note", 3, 363, "note", [("Do not hotel/sell:", "to pay.")], "G3-3", None),
    ("g3-d364-note", 3, 364, "note", [("I will conserve my $43 cash", "pass GO next turn.")], "G3-5", None),
]

# short inline quotations used inside running prose
INLINE = [
    ("in-g1-d313-distress", 1, 313, "note", [("seek North Carolina or future distress rather than subsidizing rivals", "seek North Carolina or future distress rather than subsidizing rivals")]),
    ("in-g20-d95-cashstarved", 20, 95, "note", [("P1's red monopoly is cash-starved; buying New York now would fund dangerous development", "P1's red monopoly is cash-starved; buying New York now would fund dangerous development")]),
    ("in-g7-d43-reinvest", 7, 43, "note", [("reinvest in cheaper, stronger sets rather than hold out for another $25", "reinvest in cheaper, stronger sets rather than hold out for another $25")]),
    ("in-g1-d308-weapon", 1, 308, "public", [("A monopoly on dark blue is the only thing on this board that can stand up to p3's $3.6k", "A monopoly on dark blue is the only thing on this board that can stand up to p3's $3.6k")]),
    ("in-g18-d443-rebuild", 18, 443, "note", [("Opponent withdrew Pacific offer and refuses funding our rebuild", "Opponent withdrew Pacific offer and refuses funding our rebuild")]),
    ("in-g20-d129-houses", 20, 129, "public", [("That's money you can put into more red houses right now", "That's money you can put into more red houses right now")]),
]

TEX_MAP = {
    "\\": r"\textbackslash{}",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    '"': r"\char34{}",
}
ALLOWED_NON_ASCII = set("—–’‘“”é×")


def tex_escape(s: str) -> str:
    out = []
    for ch in s:
        if ch in TEX_MAP:
            out.append(TEX_MAP[ch])
        elif ord(ch) < 128 or ch in ALLOWED_NON_ASCII:
            out.append(ch)
        else:
            raise ValueError(f"unsupported character {ch!r} (U+{ord(ch):04X})")
    return "".join(out)


def field_of(g, k: int, channel: str):
    r = g.resolved[k]
    sel = None
    for i, a in enumerate(r["attempts"]):
        if a.get("outcome") == "valid":
            sel = i
    if sel is None:
        sel = len(r["attempts"]) - 1
    if channel == "public":
        return r["final_action"]["public_message"], "/final_action/public_message", sel
    if channel == "note":
        return r["final_action"]["private_thought"], "/final_action/private_thought", sel
    if channel == "content":
        return r["attempts"][sel]["assistant_content"], f"/attempts/{sel}/assistant_content", sel
    if channel == "reasoning":
        return r["attempts"][sel]["raw_response"]["choices"][0]["message"]["reasoning"], f"/attempts/{sel}/raw_response/choices/0/message/reasoning", sel
    raise KeyError(channel)


def spans_of(text: str, spec):
    if spec == "full":
        core = text.strip()
        start = text.index(core)
        return [(start, start + len(core))], True
    spans = []
    pos = 0
    for start_marker, end_marker in spec:
        s = text.index(start_marker, pos)
        e = text.index(end_marker, s) + len(end_marker)
        spans.append((s, e))
        pos = e
    return spans, False


def contains(obj, needle: str) -> bool:
    if isinstance(obj, str):
        return needle in obj
    if isinstance(obj, dict):
        return any(contains(v, needle) for v in obj.values())
    if isinstance(obj, list):
        return any(contains(v, needle) for v in obj)
    return False


def delivered(g, k: int, message: str, to_model: str):
    pid = g.pid_of[to_model]
    for j in range(k + 1, min(g.n_decisions, k + 60)):
        st = g.started[j]
        if st["player_id"] == pid and contains(st["prompt_payload"], message):
            return j
    return None


def old_definitions() -> dict:
    out = {}
    pat = re.compile(r"\\DeclareTranscriptQuote\{([^}]+)\}\{([^}]*)\}\{(.*)\}\s*$")
    for name in ("transcript_quotes.tex", "opus_quotes.tex", "fable_quotes.tex"):
        for line in (OLD_SECTIONS / name).read_text().splitlines():
            m = pat.match(line)
            if m:
                out[m.group(1)] = (m.group(2), m.group(3), name)
    return out


def main() -> None:
    games = load_all()
    old = old_definitions()
    tex = [
        "% Generated by analysis/build_quotes.py from canonical decisions.jsonl. Do not edit by hand.",
        "% Exact spans, offsets and hashes: data/quote_manifest.json. Bracketed ellipses are editorial.",
    ]
    manifest = []
    hashes = {}
    for qid, gn, k, channel, spec, reused, deliver_to in Q:
        g = games[gn]
        text, pointer, sel = field_of(g, k, channel)
        spans, full = spans_of(text, spec)
        parts = [text[s:e] for s, e in spans]
        body = r" \textnormal{[\ldots]} ".join(tex_escape(p) for p in parts)
        speaker = g.model[g.resolved[k]["player_id"]]
        label = f"{speaker} · {CHANNELS[channel]} · G{gn} d{k} · attempt {sel} · {'full field' if full else 'excerpt'}"
        tex.append(f"\\DeclareTranscriptQuote{{{qid}}}{{{label}}}{{{body}}}")
        path = g.decisions_path
        hashes.setdefault(str(path), sha256_file(path))
        entry = {
            "id": qid,
            "metadata": label,
            "game": gn,
            "decision": k,
            "turn": g.resolved[k]["turn_index"],
            "speaker": speaker,
            "channel": CHANNELS[channel],
            "selected_attempt": sel,
            "response_condition": g.resolved[k]["sequence_meta"].get("response_condition"),
            "applied_action": g.resolved[k]["final_action"]["action"],
            "source": str(path.relative_to(REPO)),
            "source_sha256": hashes[str(path)],
            "jsonl_line_1based": g.decision_line[k],
            "json_pointer": pointer,
            "field_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "full_field": full,
            "spans": [{"span": [s, e], "text": text[s:e]} for s, e in spans],
        }
        if reused:
            old_label, old_body, old_file = old[reused]
            entry["reused_from"] = {"id": reused, "file": f"paper_rewrite_2026-11-10/integrated/sections/{old_file}"}
            # the earlier files encode a trailing newline in one field as "\\par "; ignore that markup only
            norm = lambda t: t.replace("\\par", "").strip()
            entry["text_identical_to_reused_definition"] = norm(old_body) == norm(body)
            assert entry["text_identical_to_reused_definition"], (qid, old_body, body)
        if deliver_to:
            # deliver the first displayed span (full message for full fields)
            j = delivered(g, k, parts[0] if not full else text.strip(), deliver_to)
            entry["delivered_to"] = deliver_to
            entry["first_recipient_prompt_containing_message"] = j
            entry["delivery_checked"] = True  # None means the message was not found in the next 60 prompts
        manifest.append(entry)
    tex.append("% ---- inline quotations ----")
    for qid, gn, k, channel, spec in INLINE:
        g = games[gn]
        text, pointer, sel = field_of(g, k, channel)
        spans, full = spans_of(text, spec)
        parts = [text[s:e] for s, e in spans]
        body = r" \textnormal{[\ldots]} ".join(tex_escape(p) for p in parts)
        tex.append(f"\\DeclareInlineQuote{{{qid}}}{{{body}}}")
        path = g.decisions_path
        hashes.setdefault(str(path), sha256_file(path))
        manifest.append(
            {
                "id": qid, "inline": True, "game": gn, "decision": k, "turn": g.resolved[k]["turn_index"],
                "speaker": g.model[g.resolved[k]["player_id"]], "channel": CHANNELS[channel], "selected_attempt": sel,
                "response_condition": g.resolved[k]["sequence_meta"].get("response_condition"),
                "source": str(path.relative_to(REPO)), "source_sha256": hashes[str(path)],
                "jsonl_line_1based": g.decision_line[k], "json_pointer": pointer,
                "field_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "spans": [{"span": [s, e], "text": text[s:e]} for s, e in spans],
            }
        )
    (HERE / "sections").mkdir(exist_ok=True)
    (HERE / "sections" / "quotes.tex").write_text("\n".join(tex) + "\n")
    (HERE / "data" / "quote_manifest.json").write_text(json.dumps({"schema": "fable_5_2_quote_manifest_v1", "quotes": manifest}, indent=1, ensure_ascii=False) + "\n")
    print("quotes", len(Q), "inline", len(INLINE), "reused", sum(1 for q in Q if q[5]))
    for e in manifest:
        if e.get("delivered_to"):
            print("  delivered", e["id"], "->", e["delivered_to"], "at d", e["first_recipient_prompt_containing_message"])


if __name__ == "__main__":
    main()
