"""Approximate main-text prose words: section sources minus tables, figures, quotation cards, source lines and commands."""
import re, sys
from pathlib import Path
D = Path(__file__).resolve().parents[1]
total = 0
for name in ["introduction", "design", "finance", "bargaining", "conduct", "discussion"]:
    s = (D / f"sections/{name}.tex").read_text()
    s = re.sub(r"%.*", "", s)
    s = re.sub(r"\\begin\{(table|figure)\}.*?\\end\{\1\}", " ", s, flags=re.S)
    s = re.sub(r"\\TranscriptQuote\{[^}]*\}|\\TranscriptSource\{[^\n]*\}", " ", s)
    s = re.sub(r"\\InlineQuote\{[^}]*\}", " ", s)
    s = re.sub(r"\\(cite|ref|label)\{[^}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^]]*\])?", " ", s)
    s = re.sub(r"[{}$~\\]", " ", s)
    n = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,%/-]*", s))
    total += n
    print(f"{name:14s}{n:6d}")
print(f"{'total':14s}{total:6d}")
