"""Extract arXiv abstract-page metadata from locally downloaded abs HTML files.

Usage: python3 -I arxiv_meta.py <abs_dir> <out_json>
Each file in abs_dir is named <arxiv_id>.html (slashes replaced by _).
Reads only; records title, authors, submission history, comments, journal
reference, primary subject and the abstract text for later section checks.
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def main() -> None:
    src = Path(sys.argv[1])
    out = {}
    for f in sorted(src.glob("*.html")):
        t = f.read_text(encoding="utf-8", errors="replace")
        rec = {"file_sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
        m = re.search(r'<meta name="citation_title" content="([^"]*)"', t)
        rec["title"] = html.unescape(m.group(1)) if m else None
        rec["authors"] = [html.unescape(a) for a in re.findall(r'<meta name="citation_author" content="([^"]*)"', t)]
        m = re.search(r'<td class="tablecell comments[^"]*">(.*?)</td>', t, re.S)
        rec["comments"] = clean(m.group(1)) if m else None
        m = re.search(r'<td class="tablecell jref">(.*?)</td>', t, re.S)
        rec["journal_ref"] = clean(m.group(1)) if m else None
        m = re.search(r'<span class="primary-subject">(.*?)</span>', t, re.S)
        rec["primary_subject"] = clean(m.group(1)) if m else None
        m = re.search(r'<div class="submission-history">(.*?)</div>', t, re.S)
        hist = clean(m.group(1)) if m else ""
        rec["versions"] = re.findall(r"\[(v\d+)\]\s*(\w{3}, \d{1,2} \w{3} \d{4})", hist)
        m = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', t, re.S)
        rec["abstract"] = clean(m.group(1)).replace("Abstract:", "", 1).strip() if m else None
        out[f.stem.replace("_", "/")] = rec
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
