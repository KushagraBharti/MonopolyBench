"""Render replacement_prose.pdf to page images and extract its text for checks."""
import sys, json
from pathlib import Path
import pymupdf
HERE = Path(__file__).resolve().parent.parent
doc = pymupdf.open(HERE / "replacement_prose.pdf")
out = HERE / "qa"
out.mkdir(exist_ok=True)
text = []
for i, page in enumerate(doc, start=1):
    page.get_pixmap(dpi=80).save(out / f"p{i:02d}.png")
    text.append(page.get_text())
(out / "replacement_prose_text.txt").write_text("\n\f\n".join(text))
print("pages", len(doc))
