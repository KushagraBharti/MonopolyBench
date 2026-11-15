"""Generate every quotation used in the paper from the stored response fields.

Each entry names a game, a zero-based decision, a channel and either the whole field or an
exact excerpt. The script asserts that the excerpt occurs in the stored field, records
file, line, field hash and character offsets, and writes LaTeX macros. Quotation text in
the manuscript is never typed by hand.

Channels
  note      final_action.private_thought   (authored private note, applied tool argument)
  public    final_action.public_message    (authored public message, applied tool argument)
  provider  attempts[-1] message.reasoning (provider-returned reasoning field)
  content   attempts[-1] assistant_content (text returned beside the tool call, not applied)

Writes data/quote_manifest.json and sections/gen_quotes.tex.
"""
from lib import *

LABEL = {"note": "authored note", "public": "public message", "provider": "provider field", "content": "assistant content, not applied"}

# id, game, decision, channel, excerpt (None = whole field)
Q = [
    # --- finance: exact valuation and selective financing
    ("g20-creditor", 20, 325, "note", "p3's total liquidation value is $1,414 ($49 cash + $675 from selling 9 Orange houses and 2 Brown hotels + $690 from mortgaging 8 unmortgaged properties)."),
    ("g20-plan", 20, 327, "note", None),
    ("g20-last", 20, 336, "note", "Final $30 mortgage covers $16 shortfall, leaving $14 after rent."),
    ("g13-select", 13, 195, "note", None),
    ("g13-select-why", 13, 195, "provider", "I'm now leaning towards this approach to maximize my rental income potential."),
    ("g5-revise", 5, 263, "provider", "I initially miscalculated! Selling the houses on Park Place and Boardwalk alone doesn't cover the debt. However, I can mortgage Park Place and Boardwalk after selling the houses!"),
    ("g1-rule", 1, 476, "note", "Must sell before yellows can be mortgaged."),
    ("g18-rule", 18, 309, "note", "which will allow me to mortgage St. Charles Place ($70) on the next step"),
    ("g2-opus-locked", 2, 215, "provider", "mortgaging the light-blue properties themselves for $160 once the houses are gone"),
    ("g15-max", 15, 203, "note", "Max raise is $520 (houses $50 + Ill $120 + Ventnor $130 + Penn $160 + Med $30 + Baltic $30). $241+$520=$761 < $800. Short $39 even at full liquidation."),
    ("g10-sol-locked", 10, 188, "note", "even subsequently mortgaging light blues adds only $160"),
    # --- the two false budgets, both channels
    ("g12-false-note", 12, 190, "note", None),
    ("g12-false-provider", 12, 190, "provider", "It seems like bankruptcy might transfer property anyway, so declaring insolvency could be the best option without needing further actions."),
    ("g17-false-note", 17, 234, "note", None),
    ("g17-false-provider", 17, 234, "provider", "This won't cover my rent in full, so I will have to start thinking of additional options."),
    # --- listed-only totals on unpayable debts
    ("g3-listed", 3, 426, "note", "Selling all twelve houses raises $300 and mortgaging both railroads adds $200: maximum $914, insufficient."),
    ("g5-listed", 5, 309, "provider", "Mortgaging my remaining properties and selling houses only gets me to 639 total"),
    ("g8-listed", 8, 280, "note", "Only liquidation is 6 orange houses at $50 = $300, total $386. No unmortgaged properties."),
    # --- departures from the asset bound
    ("g12-conflict-note2", 12, 249, "note", "The sell_houses call was the correct action. Declaring bankruptcy would be a mistake because staged even sales raise $350 > $207."),
    ("g12-conflict-public", 12, 249, "public", None),
    ("g9-later", 9, 196, "provider", "I have already mortgaged Mediterranean Avenue and Pennsylvania Avenue. I will continue that strategy for consistency"),
    ("g20-declare-note", 20, 273, "note", "Selling first only hands the bank the house at half price before the same bankruptcy. Declare now."),
    ("g19-rules-provider", 19, 224, "provider", "Under standard rules, a bankrupt player must turn over all assets to the creditor, and mortgaged properties transfer with their mortgage. The engine might enforce different rules."),
    ("g18-fee", 18, 344, "note", "mortgaging it before declaring bankruptcy forces p4 to pay the 10% mortgage transfer fee."),
    ("g18-inherit", 18, 313, "note", "Must not go bankrupt — p1 would inherit built dark blues and I am eliminated."),
    # --- bargaining incidents
    ("g15-refusal-note", 15, 169, "note", "Trade gives p4 Atlantic+Ventnor+Marvin and ~$830 plus mortgage capacity to drop 5+ yellow houses ($150) immediately, then they roll again on doubles. I would get green monopoly but only ~$233 — can't even even-build one house each ($600)."),
    ("g15-final", 15, 175, "public", None),
    ("g2-blocker-price", 2, 120, "public", "$450 is the price for the player who completes yellow. I'm not building it."),
    ("g2-price", 2, 124, "public", None),
    ("g2-note", 2, 124, "note", "At $325 p4 retains $520, enough for nine yellow houses immediately."),
    ("g7-public", 7, 42, "public", "$600, final."),
    ("g7-private", 7, 42, "note", "If they return at $625, accept"),
    ("g7-timed", 7, 141, "note", "p4 just acquired the Dark Blue monopoly and spent down to $84 building 3 houses. Since p4 now needs cash to add houses on Park Place and Boardwalk ($200 each), they have strong incentive to sell New York Avenue for cash."),
    ("g13-pitch", 13, 250, "public", None),
    ("g13-floor", 13, 252, "note", "$130 only works if I also mortgage Ventnor and kills the only rent."),
    ("g13-omit", 13, 252, "provider", "I will frame the $130 offer as leaving me $35 short of Short Line, omitting that I could mortgage Ventnor to survive."),
    ("g13-buyer", 13, 253, "provider", "keeping grok solvent with cash from a $200 purchase seems favorable overall — it's affordable, denies player 2 a monopoly, and the mortgage interest is minor."),
    ("g19-false", 19, 135, "public", None),
    ("g19-abort", 19, 135, "note", "Abort this trade. Do not send it."),
    ("g19-correct", 19, 136, "public", None),
    ("g20-appeal", 20, 96, "public", None),
    ("g20-boycott", 20, 97, "note", "p4 is organizing a cash boycott, so don't wait on a sale."),
    ("g20-refuse", 20, 101, "public", None),
    ("g18-assure", 18, 431, "public", None),
    ("g18-reserve", 18, 431, "provider", "Buying Pacific might just prolong p1's survival, so maybe it's smarter to hold onto cash in case p1's orange hotels hit me with heavy rent."),
    ("g18-invoke", 18, 441, "public", None),
    ("g18-withdraw", 18, 442, "public", None),
]


def field(r, channel):
    if channel == "note":
        return r["final_action"].get("private_thought") or ""
    if channel == "public":
        return r["final_action"].get("public_message") or ""
    if channel == "provider":
        return provider_text(r)
    if channel == "content":
        return r["attempts"][-1].get("assistant_content") or ""
    raise KeyError(channel)


def main():
    manifest, macros = [], ["% Generated by tools/06_quotes.py from stored response fields. Do not edit by hand."]
    for qid, g, d, channel, excerpt in Q:
        st, rs, lines = load(g)
        r = rs[d]
        whole = field(r, channel)
        text = whole.strip() if excerpt is None else excerpt
        start = whole.find(text)
        assert text and start >= 0, f"quote {qid} not found in G{g} d{d} {channel}: {whole[:200]!r}"
        manifest.append(dict(
            id=qid, game=g, decision=d, channel=channel, speaker=who(r), turn=r["turn_index"],
            attempt_index=len(r["attempts"]) - 1, response_condition=r["attempts"][-1].get("response_condition"),
            whole_field=excerpt is None, text=text, char_start=start, char_end=start + len(text),
            field_sha256=text_sha256(whole), source_file=str(decisions_path(g).relative_to(ROOT)), source_line=lines[d],
            source_file_sha256=file_sha256(decisions_path(g))))
        body = tex(" ".join(text.split()))
        macros.append(f"\\DeclareQuote{{{qid}}}{{{body}}}")
        macros.append(f"\\DeclareQuoteMeta{{{qid}}}{{{who(r)}, {LABEL[channel]}, G{g} d{d}}}")
    write_json("quote_manifest.json", manifest)
    (SECTIONS / "gen_quotes.tex").write_text("\n".join(macros) + "\n")
    print("quotes", len(manifest), "all found in their stored fields")


if __name__ == "__main__":
    main()
