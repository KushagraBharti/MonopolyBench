#!/usr/bin/env python3
"""Approximate main-text prose word counts, excluding tables, figures, quotes,
equations and references. A rough check, not texcount."""
import pathlib
import re

DRAFT = pathlib.Path(__file__).resolve().parent.parent
MAIN = ["abstract", "introduction", "setup", "measurement", "bargaining", "construction", "liquidity",
        "conduct", "temporal", "related", "discussion", "limitations", "conclusion"]
APP = ["app_cohort", "app_conditions", "app_offers", "app_certificates", "app_incidents", "app_temporal",
       "app_pilot", "app_provenance"]


def prose(text):
    text = re.sub(r"(?m)%.*$", "", text)
    for env in ["table", "figure", "equation", "tabular", "tabularx", "longtable"]:
        text = re.sub(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env), " ", text, flags=re.S)
    text = re.sub(r"\\TranscriptQuote\{[^}]*\}", " ", text)
    text = re.sub(r"\\(cite|ref|label|path|includegraphics|input)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = re.sub(r"[{}$~\\]", " ", text)
    return [w for w in text.split() if re.search(r"[A-Za-z0-9]", w)]


def main():
    tot = 0
    for n in MAIN:
        c = len(prose((DRAFT / "sections" / f"{n}.tex").read_text()))
        tot += c if n != "abstract" else 0
        print(f"{n:14s} {c:6d}")
    print(f"{'MAIN (no abstract)':14s} {tot:6d}")
    atot = sum(len(prose((DRAFT / "sections" / f"{n}.tex").read_text())) for n in APP)
    print(f"{'APPENDICES':14s} {atot:6d}")


if __name__ == "__main__":
    main()
