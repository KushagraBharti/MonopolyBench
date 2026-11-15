"""Render the built PDF to two-page contact sheets and extract its text for inspection."""
from __future__ import annotations

from pathlib import Path

import pymupdf
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
out = HERE / "qa" / "render"
out.mkdir(parents=True, exist_ok=True)
for old in out.glob("sheet_*.png"):
    old.unlink()
doc = pymupdf.open(HERE / "manuscript.pdf")
pages = []
for page in doc:
    pix = page.get_pixmap(dpi=78)
    pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
for k in range(0, len(pages), 2):
    pair = pages[k:k + 2]
    width = sum(im.width for im in pair) + 10 * (len(pair) - 1)
    sheet = Image.new("RGB", (width, max(im.height for im in pair)), "#888888")
    x = 0
    for im in pair:
        sheet.paste(im, (x, 0))
        x += im.width + 10
    sheet.save(out / f"sheet_{k // 2 + 1:02d}.png")
(HERE / "qa" / "manuscript_text.txt").write_text("\n".join(p.get_text() for p in doc))
print("pages", len(pages), "sheets", (len(pages) + 1) // 2)
