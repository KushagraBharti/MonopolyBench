"""Render every PDF page to PNG plus 4x3 contact sheets (Opus review; read-only on the PDF).
Usage: uv run --with pymupdf --with pillow python -I render_pages.py <pdf> <outdir> [zoom]"""
import sys
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw
pdf, out = Path(sys.argv[1]), Path(sys.argv[2]); zoom = float(sys.argv[3]) if len(sys.argv) > 3 else 1.4
out.mkdir(parents=True, exist_ok=True)
tiles = []
for i, pg in enumerate(pymupdf.open(pdf)):
    f = out / f"p{i+1:03}.png"
    pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False).save(f)
    im = Image.open(f).convert("RGB"); im.thumbnail((300, 300))
    t = Image.new("RGB", (310, 330), "#ccc"); t.paste(im, ((310 - im.width) // 2, 24))
    ImageDraw.Draw(t).text((6, 4), f"p{i+1}", fill="black"); tiles.append(t)
for k in range(0, len(tiles), 12):
    sub = tiles[k:k+12]; s = Image.new("RGB", (310*4, 330*((len(sub)+3)//4)), "white")
    for j, t in enumerate(sub): s.paste(t, (310*(j % 4), 330*(j // 4)))
    s.save(out / f"contact_{k+1:03}.png")
print(len(tiles), "pages ->", out)
