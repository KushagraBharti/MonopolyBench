"""Generate every displayed quotation from canonical decision records.

Each entry names a game, zero-based decision, channel and either the full
field or contiguous excerpts given by exact start and end marker strings.  The
script reads ``decisions.jsonl``, writes ``sections/quotes.tex`` and
``data/quote_manifest.json`` (path, line, pointer, span, hashes), compares
reused quotations with the definitions in the previous integrated paper, and
records the first later prompt in which a public message reached the named
counterparty.  Quotation text is never typed by hand in the manuscript.

It also writes ``data/b6_readings.json``: the author's reading of the first
stored text in each of the sixteen necessary-collateral episodes.  The reading
is one model-assisted pass by the drafting assistant.  It is not human coding.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from corpus import REPO, load_all, sha256_file

HERE = Path(__file__).resolve().parents[1]
OLD_SECTIONS = REPO / "docs/research_raw/paper_revision_2026-11-11/integrated/sections"

CHANNELS = {
    "public": "public message",
    "note": "applied private note",
    "content": "assistant content, not applied",
    "reasoning": "provider-returned explanation",
}

# id, game, decision, channel, spec, reused_from, deliver_to
Q = [
    # ---- finance: G20 payment ------------------------------------------------
    ("g20-d325-creditor", 20, 325, "note", "full", "g20-d325-creditor-note", None),
    ("g20-d327-plan", 20, 327, "note", "full", "g20-d327-plan", None),
    ("g20-d336-last", 20, 336, "note", "full", "g20-d336-last", None),
    # ---- finance: counted and uncounted collateral ---------------------------
    ("g5-d263-note", 5, 263, "note", [("By selling all 3 houses on Park Place", "survive with $149 cash.")], None, None),
    ("g17-d234-note", 17, 234, "note", "full", None, None),
    ("g12-d190-note", 12, 190, "note", "full", None, None),
    # ---- bargaining: G15 -------------------------------------------------------
    ("g15-d169-note", 15, 169, "note", [("Trade gives p4", "one house each ($600).")], "fx-g15-refusal-note", None),
    ("g15-d174-sweetener", 15, 174, "public", "full", "fx-g15-sweetener", "Grok"),
    ("g15-d175-refusal", 15, 175, "public", "full", "fx-g15-final-refusal", "Sol"),
    # ---- bargaining: G2 --------------------------------------------------------
    ("g2-d124-note", 2, 124, "note", "full", "g2-d124-note", None),
    ("g2-d128-keep", 2, 128, "public", "full", "g2-d128-keep", "Opus"),
    # ---- third party: G13 ------------------------------------------------------
    ("g13-d250-insurance", 13, 250, "public", "full", "g13-opening-insurance", "Opus"),
    ("g13-d252-omission", 13, 252, "reasoning", [("I will frame the $130 offer", "may not calculate the mortgage themselves.")], "g13-omission-explanation", None),
    ("g13-d253-buyer", 13, 253, "reasoning", [("I'm also considering the scenario", "potentially completing that color group."), ("so keeping grok solvent", "the mortgage interest is minor.")], None, None),
    # ---- casebook: G7 ----------------------------------------------------------
    ("g7-d42-final", 7, 42, "public", [("$600, final.", "no set to protect.")], "g7_d42_public", "Sol"),
    ("g7-d42-ceiling", 7, 42, "note", [("If they return at $625", "Do not go above $625.")], "g7_d42_private", None),
    ("g7-d141-bid", 7, 141, "note", [("p4 just acquired", "sell New York Avenue for cash.")], "new-g7-d141-timed-bid", None),
    ("g7-d142-ask", 7, 142, "note", "full", None, None),
    # ---- casebook: G19 ---------------------------------------------------------
    ("g19-d135-public", 19, 135, "public", "full", "g19_d135_false_public", "Sol"),
    ("g19-d135-note", 19, 135, "note", [("Misread the board.", "not orange."), ("Abort this trade. Do not send it.", "Abort this trade. Do not send it.")], "g19-abort", None),
    ("g19-d136-public", 19, 136, "public", "full", "g19_d136_correction_accept", "Grok"),
    # ---- casebook: G20 appeal --------------------------------------------------
    ("g20-d96-appeal", 20, 96, "public", "full", "g20-coordination-appeal", "Grok"),
    ("g20-d97-note", 20, 97, "note", [("p4 is organizing a cash boycott", "don't wait on a sale.")], "g20-recognition-note", None),
    ("g20-d101-refusal", 20, 101, "public", "full", "g20-concrete-refusal", "Grok"),
    # ---- casebook: G18 ---------------------------------------------------------
    ("g18-d431-assurance", 18, 431, "public", "full", "g18-assurance", "Sol"),
    ("g18-d431-content", 18, 431, "content", [("I also didn't raise my Pacific offer", "help p1 last longer.")], None, None),
    ("g18-d441-invocation", 18, 441, "public", "full", "g18-invocation", "Opus"),
    ("g18-d442-withdrawal", 18, 442, "public", "full", "g18-withdrawal", "Sol"),
    ("g18-d442-explanation", 18, 442, "reasoning", "full", "g18-withdrawal-explanation", None),
]

INLINE = [
    ("in-g5-d263-revise", 5, 263, "reasoning", [("I initially miscalculated!", "This is key!")]),
    ("in-g4-d72-rule", 4, 72, "note", [("I will only trade a monopoly-completing property if I receive a completed monopoly in return.",) * 2]),
    ("in-g1-d122-commit", 1, 122, "note", [("Do not counter", "invites the deal.")]),
    ("in-g15-d166-appeal", 15, 166, "public", [("let's not hand him the last piece of any set",) * 2]),
    ("in-g2-d127-final", 2, 127, "public", [("$450, and that's my final offer.",) * 2]),
    ("in-g2-d127-ceiling", 2, 127, "note", [("My ceiling is about $475.",) * 2]),
    ("in-g13-d252-floor", 13, 252, "note", [("4/36 Short Line still fatal even with Ventnor mortgaged",) * 2]),
    ("in-g12-d249-note", 12, 249, "note", [("Declaring bankruptcy would be a mistake because staged even sales raise $350 > $207.",) * 2]),
    ("in-g20-d129-houses", 20, 129, "public", [("That's money you can put into more red houses right now",) * 2]),
    ("in-g19-d136-note", 19, 136, "note", [("No opponent monopoly enabled.",) * 2]),
]

# The sixteen necessary-collateral episodes.  code: explicit / tentative / omits.
# check: (kind, stated value) compared with the records by this script.
READINGS = [
    (1, 476, "note", ("Must sell before yellows can be mortgaged.", "to clear the debt."), "explicit", ("gap_after_sales", 74)),
    (2, 216, "note", ("Clearing buildings unlocks yellow mortgages worth $430", "with two yellows mortgaged."), "explicit", ("unlisted_value", 430)),
    (4, 270, "note", ("I must sell my 4 houses on Yellow", "the remaining $174 shortfall."), "explicit", ("gap_after_sales_ignoring_listed", 174)),
    (4, 308, "reasoning", ("Selling back my 7 houses at half price gets 525", "totaling 910"), "explicit", ("total_with_cash", 910)),
    (5, 263, "note", ("unlock the ability to mortgage Park Place ($175) and Boardwalk ($200)", "survive with $149 cash."), "explicit", ("cash_after", 149)),
    (6, 185, "reasoning", ("plus mortgaging Boardwalk for $200 and those three properties for another $220", "$770 total"), "explicit", ("raise_without_cash", 770)),
    (8, 257, "note", ("which will also unlock Park Place and Boardwalk for mortgaging", "the remaining $217 shortfall."), "explicit", ("gap_after_first_sale", 217)),
    (11, 203, "reasoning", ("Adding the remaining mortgages on St James, Tennessee, and New York", "with $56 left over."), "explicit", ("cash_after", 56)),
    (12, 190, "note", ("With $53 cash, maximum liquidity is $408, below $500 owed.",) * 2, "omits", ("stated_maximum", 408)),
    (13, 195, "note", ("I must sell the house on Boardwalk ($100) and mortgage Park Place ($175)", "non-Dark-Blue properties"), "explicit", ("unlisted_deed_value", 175)),
    (17, 234, "note", ("my total liquidatable value is only $530",) * 2, "omits", ("stated_maximum", 530)),
    (17, 254, "reasoning", ("mortgaging those three properties adds $110+$110+$120=$340", "totaling $843"), "explicit", ("total_with_cash", 843)),
    (18, 309, "note", ("which will allow me to mortgage St. Charles Place ($70) on the next step", "the remaining $38 shortfall"), "explicit", ("gap_after_sales", 38)),
    (18, 313, "note", ("Selling all 5 houses yields only $500", "(~$49 gap)."), "explicit", ("gap_after_sales", 49)),
    (20, 291, "reasoning", ("I'm checking whether mortgaging the pink lots themselves", "could close the gap."), "tentative", None),
    (20, 327, "note", ("Full liquidation should yield $1,414 including cash and all mortgages", "by $14."), "explicit", ("cash_after", 14)),
]

TEX_MAP = {"\\": r"\textbackslash{}", "$": r"\$", "%": r"\%", "&": r"\&", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", '"': r"\char34{}"}
ALLOWED_NON_ASCII = set("—–’‘“”é×→")


def tex_escape(s: str) -> str:
    out = []
    for ch in s:
        if ch in TEX_MAP:
            out.append(TEX_MAP[ch])
        elif ch == "→":
            out.append(r"$\rightarrow$")
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
    spans, pos = [], 0
    for start_marker, end_marker in spec:
        s = text.index(start_marker, pos)
        e = text.index(end_marker, s) + len(end_marker)
        spans.append((s, e))
        pos = e
    return spans, False


def delivered(g, k: int, message: str, to_model: str):
    pid = g.pid_of[to_model]
    for j in range(k + 1, min(g.n_decisions, k + 60)):
        st = g.started[j]
        if st["player_id"] == pid and message in json.dumps(st["prompt_payload"], ensure_ascii=False):
            return j
    return None


def old_definitions() -> dict:
    out = {}
    pat = re.compile(r"\\DeclareTranscriptQuote\{([^}]+)\}\{([^}]*)\}\{(.*)\}\s*$")
    for name in ("transcript_quotes.tex", "opus_quotes.tex", "fable_quotes.tex", "additional_quotes.tex"):
        for line in (OLD_SECTIONS / name).read_text().splitlines():
            m = pat.match(line)
            if m:
                out[m.group(1)] = (m.group(3), name)
    return out


def main() -> None:
    games = load_all()
    old = old_definitions()
    debt = {(e["game"], e["first_decision"]): e for e in json.loads((HERE / "data/b2_debt_episodes.json").read_text())}
    tex = ["% Generated by analysis/build_quotes.py from canonical decisions.jsonl. Do not edit by hand.",
           "% Exact spans, offsets and hashes: data/quote_manifest.json. Bracketed ellipses are editorial."]
    manifest, hashes = [], {}

    def base(qid, gn, k, channel, spec):
        g = games[gn]
        text, pointer, sel = field_of(g, k, channel)
        spans, full = spans_of(text, spec)
        parts = [text[s:e] for s, e in spans]
        body = r" \textnormal{[\ldots]} ".join(tex_escape(p) for p in parts)
        path = g.decisions_path
        hashes.setdefault(str(path), sha256_file(path))
        entry = {"id": qid, "game": gn, "decision": k, "turn": g.resolved[k]["turn_index"],
                 "speaker": g.model[g.resolved[k]["player_id"]], "channel": CHANNELS[channel], "selected_attempt": sel,
                 "response_condition": g.resolved[k]["sequence_meta"].get("response_condition"),
                 "applied_action": g.resolved[k]["final_action"]["action"],
                 "source": str(path.relative_to(REPO)), "source_sha256": hashes[str(path)],
                 "jsonl_line_1based": g.decision_line[k], "json_pointer": pointer,
                 "field_sha256": hashlib.sha256(text.encode()).hexdigest(), "full_field": full,
                 "spans": [{"span": [s, e], "text": text[s:e]} for s, e in spans]}
        return g, text, parts, body, full, sel, entry

    for qid, gn, k, channel, spec, reused, deliver_to in Q:
        g, text, parts, body, full, sel, entry = base(qid, gn, k, channel, spec)
        cond = "" if entry["response_condition"] == "standard" else " · action-only recovery"
        label = f"{entry['speaker']} · {CHANNELS[channel]} · G{gn} d{k}{cond} · {'full field' if full else 'excerpt'}"
        entry["metadata"] = label
        tex.append(f"\\DeclareTranscriptQuote{{{qid}}}{{{label}}}{{{body}}}")
        if reused:
            old_body, old_file = old[reused]
            norm = lambda t: t.replace("\\par", "").strip()
            entry["reused_from"] = {"id": reused, "file": f"paper_revision_2026-11-11/integrated/sections/{old_file}"}
            entry["text_identical_to_reused_definition"] = norm(old_body) == norm(body)
            assert entry["text_identical_to_reused_definition"], (qid, old_body, body)
        if deliver_to:
            probe = text.strip() if full else parts[0]
            entry["delivered_to"] = deliver_to
            entry["first_recipient_prompt_containing_message"] = delivered(g, k, probe, deliver_to)
            assert entry["first_recipient_prompt_containing_message"] is not None, qid
        manifest.append(entry)

    tex.append("% ---- inline quotations ----")
    for qid, gn, k, channel, spec in INLINE:
        g, text, parts, body, full, sel, entry = base(qid, gn, k, channel, spec)
        entry["inline"] = True
        tex.append(f"\\DeclareInlineQuote{{{qid}}}{{{body}}}")
        manifest.append(entry)

    tex.append("% ---- first stored text in the sixteen necessary-collateral episodes ----")
    readings = []
    for gn, k, channel, markers, code, check in READINGS:
        qid = f"nc-g{gn}-d{k}"
        g, text, parts, body, full, sel, entry = base(qid, gn, k, channel, [markers])
        entry["inline"] = True
        tex.append(f"\\DeclareInlineQuote{{{qid}}}{{{body}}}")
        manifest.append(entry)
        e = debt[(gn, k)]
        assert e["tier"] == "unlisted"
        verified = None
        if check:
            kind, val = check
            gap = e["debt"] - e["cash"] - e["listed_mortgage"] - e["salvage"]
            truth = {
                "gap_after_sales": gap,
                "gap_after_sales_ignoring_listed": e["debt"] - e["cash"] - e["salvage"],
                "gap_after_first_sale": None,
                "unlisted_value": e["unlisted_mortgage"],
                "unlisted_deed_value": 175,
                "total_with_cash": e["cash"] + e["listed_mortgage"] + e["salvage"] + e["unlisted_mortgage"],
                "raise_without_cash": e["listed_mortgage"] + e["salvage"] + e["unlisted_mortgage"],
                "cash_after": e.get("cash_after_payment"),
                "stated_maximum": e["cash"] + e["listed_mortgage"] + e["salvage"],
            }[kind]
            if kind == "gap_after_first_sale":
                truth = e["debt"] - e["cash"] - 100  # G8: $625 owed, $308 cash, one $100 house sold first
            verified = {"kind": kind, "stated": val, "from_records": truth, "equal": truth == val}
        readings.append({
            "game": gn, "decision": k, "model": e["model"], "channel": CHANNELS[channel],
            "response_condition": entry["response_condition"], "code": code,
            "quoted_span": parts[0], "quote_id": qid,
            "debt": e["debt"], "cash": e["cash"], "listed_mortgage": e["listed_mortgage"], "salvage": e["salvage"],
            "unlisted_mortgage": e["unlisted_mortgage"],
            "reach_without_unlisted": e["cash"] + e["listed_mortgage"] + e["salvage"],
            "outcome": e["outcome"], "first_action": e["first_action"], "n_actions": e["n_actions"],
            "cash_after_payment": e.get("cash_after_payment"), "stated_number_check": verified,
        })
    codes = {}
    for r in readings:
        codes.setdefault(r["outcome"], {}).setdefault(r["code"], 0)
        codes[r["outcome"]][r["code"]] += 1
    assert codes == {"paid": {"explicit": 13, "tentative": 1}, "eliminated": {"omits": 2}}, codes
    checks = [r["stated_number_check"] for r in readings if r["stated_number_check"]]
    summary = {
        "reader": "Claude Fable 5.2 (drafting assistant), one pass over the first stored text of each episode on 12 November 2026",
        "status": "model-assisted reading; no human annotation; the same texts were read independently by three other assistants in the 11 November assessments",
        "codes_by_outcome": codes,
        "channel_by_outcome": {o: {c: sum(1 for r in readings if r["outcome"] == o and r["channel"] == c) for c in sorted({r["channel"] for r in readings})} for o in ("paid", "eliminated")},
        "stated_numbers_checked": len(checks), "stated_numbers_equal_records": sum(c["equal"] for c in checks),
        "stated_numbers_unequal": [[r["game"], r["decision"], r["stated_number_check"]] for r in readings if r["stated_number_check"] and not r["stated_number_check"]["equal"]],
        "rows": readings,
    }
    (HERE / "sections").mkdir(exist_ok=True)
    (HERE / "sections" / "quotes.tex").write_text("\n".join(tex) + "\n")
    (HERE / "data" / "quote_manifest.json").write_text(json.dumps({"schema": "fable_5_2_quote_manifest_v2", "quotes": manifest}, indent=1, ensure_ascii=False) + "\n")
    (HERE / "data" / "b6_readings.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    print("cards", len(Q), "inline", len(INLINE), "readings", len(READINGS), "reused", sum(1 for q in Q if q[5]))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
    for e in manifest:
        if e.get("delivered_to"):
            print("  delivered", e["id"], "->", e["delivered_to"], "at d", e["first_recipient_prompt_containing_message"])


if __name__ == "__main__":
    main()
